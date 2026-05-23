"""Run the SAAS-COHORT-1 emission pipeline end-to-end.

Driver script that:

1. Constructs the spec §5.1 / §5.2 prior pin bundle (``T1PriorPins`` /
   ``CohortPriors`` defaults).
2. Builds the ``T1ModelFactory`` with ``n_builders=1000`` per spec §5.2
   "Categorical latent per builder" (BLOCK-5 fix).
3. Runs ``pm.sample(draws=178000, chains=4, target_accept=0.95, random_seed=42)``
   per spec §8(8) per-chain ≥ 4000 floor (BLOCK-4 fix). PATH-α RUN: this
   driver bumps DRAWS_PER_CHAIN from the spec floor (4000) to 178,000 to
   satisfy the C4 MC error budget (stderr/Ẑ < 1e-3 at CV=0.84) per CLOSE
   plan v0.2 Phase 2 Path α (`docs/plans/2026-05-09-saas-cohort-close.md`).
   Run-config-only change; NO model surgery, NO spec amendment.
4. Runs ``pm.sample_prior_predictive(draws=4000)`` for the §8(7)
   posterior-vs-prior CI-width gate.
5. For each month ``m`` in the M5 evaluation horizon (default
   ``[4200, 3800, 4200]`` — months 1..3), runs the ``CohortEmitter``
   which:
       - Enforces the §8(7) + §8(8) HALT-gate (raises
         ``DiagnosticGateError`` on any failure — NO partial emission).
       - Runs ``pm.sample_posterior_predictive`` + post-hoc compound-sum
         τ_t reduction via ``run_posterior_predictive`` (BLOCK-1 fix).
       - Writes ``synthetic_tau_t/tier_id=*/month=*/`` Hive-partitioned
         parquet via ``SyntheticTauWriter``.
       - Writes ``cohort_prior.parquet`` via ``CohortPriorWriter``.
       - Writes ``_AUDIT.json`` sidecar with audit-block sha256.

Anti-fishing: draws / chains / target_accept are pinned at the spec floor
and NEVER relaxed. ``DiagnosticGateError`` HALTs cleanly — caller must
adjudicate, not retune.

Usage::

    uv run python scripts/run_cohort1_emit.py
"""

from __future__ import annotations

import time
from pathlib import Path

import pymc as pm

from simulations.saas_builder.diagnostics import PosteriorDiagnostic
from simulations.saas_builder.emit import CohortEmitter
from simulations.saas_builder.model import T1ModelFactory
from simulations.saas_builder.priors import CohortPriors

# ─── Spec-pinned sampling configuration ───────────────────────────────────────

# PATH-α bump (CLOSE plan v0.2 Phase 2): 4000 → 178000 per chain.
# Total N_draws = 4 × 178000 = 712000 ≈ 7.1e5 per plan pin
# (`docs/plans/2026-05-09-saas-cohort-close.md` §"Phase 2 — COHORT-1 MC
# budget on real C1"). Resolves C4 MC error budget breach (stderr/Ẑ ≤ 1e-3
# ceiling at CV=0.84 real-C1 input). Spec §8(8) per-chain ≥ 4000 floor
# satisfied (going UP, not down). NO model surgery, NO spec amendment.
DRAWS_PER_CHAIN: int = 178_000
N_CHAINS: int = 4
TARGET_ACCEPT: float = 0.95
RANDOM_SEED: int = 42
N_BUILDERS: int = 1000

# M5 evaluation horizon — 3-month FX path [4200, 3800, 4200] COP/USD.
FX_PATH_COP_PER_USD: tuple[float, ...] = (4200.0, 3800.0, 4200.0)

# Output base.
BASE_DIR: Path = (
    Path(__file__).resolve().parent.parent
    / "simulations"
    / "saas_builder"
    / "data"
)


def main() -> int:
    """Run the COHORT-1 emission pipeline; return process exit code."""
    print("=" * 72)
    print("SAAS-COHORT-1 emission pipeline")
    print(
        f"  draws/chain = {DRAWS_PER_CHAIN}   chains = {N_CHAINS}"
        f"   target_accept = {TARGET_ACCEPT}   seed = {RANDOM_SEED}"
    )
    print(f"  n_builders  = {N_BUILDERS}")
    print(f"  fx path     = {FX_PATH_COP_PER_USD}")
    print(f"  base_dir    = {BASE_DIR}")
    print("=" * 72)

    # 1. Priors + model.
    priors = CohortPriors()
    factory = T1ModelFactory(priors=priors, n_builders=N_BUILDERS)
    print("\n[1/5] Building PyMC model (M3 Sonnet $/MTok assertion at call site)...")
    model = factory()
    print("       OK — model constructed.")

    # 2. Posterior sample.
    print(
        f"\n[2/5] pm.sample(draws={DRAWS_PER_CHAIN}, chains={N_CHAINS},"
        f" target_accept={TARGET_ACCEPT}) ..."
    )
    t_start = time.time()
    with model:
        posterior_idata = pm.sample(
            draws=DRAWS_PER_CHAIN,
            chains=N_CHAINS,
            target_accept=TARGET_ACCEPT,
            random_seed=RANDOM_SEED,
            progressbar=True,
            return_inferencedata=True,
        )
    sampling_seconds = time.time() - t_start
    print(f"       OK — sampling time = {sampling_seconds:.1f} s")

    # 3. Prior-predictive (required by §8(7) gate).
    print(f"\n[3/5] pm.sample_prior_predictive(draws={DRAWS_PER_CHAIN}) ...")
    with model:
        prior_idata = pm.sample_prior_predictive(
            draws=DRAWS_PER_CHAIN, random_seed=RANDOM_SEED
        )
    print("       OK — prior idata constructed.")

    # 4. Pre-emission diagnostic gate report (informational; emitter
    #    enforces it again before each emission).
    print("\n[4/5] Pre-flight diagnostic report (gate is enforced per-emission):")
    diag = PosteriorDiagnostic()
    verdict = diag(posterior_idata, prior_idata)
    print(f"       rhat_max         = {verdict.rhat_max:.6f}  (≤ 1.01)")
    print(f"       ess_bulk_min     = {verdict.ess_bulk_min:.1f}     (≥ 400)")
    print(f"       ess_tail_min     = {verdict.ess_tail_min:.1f}     (≥ 400)")
    print(
        f"       divergence_frac  = {verdict.divergence_frac:.6f} (≤ 0.005)"
    )
    print(
        f"       sim-floor ok     = {not verdict.sim_count_floor_violated}"
        f"   (chains={verdict.n_chains}, draws/chain={verdict.n_draws_per_chain})"
    )
    print(
        f"       ci_width_ratio   = {verdict.ci_width_ratio_max:.6f} (≤ 2.0)"
    )
    print(f"       passed           = {verdict.passed}")
    if not verdict.passed:
        print(
            "\n       HALT — gate would fail. NOT proceeding to emission."
            " See verdict above; surface to orchestrator."
        )
        return 2

    # 5. Per-month emission loop.
    print(
        f"\n[5/5] Emitting {len(FX_PATH_COP_PER_USD)} months under M5 fx_path"
        f" = {FX_PATH_COP_PER_USD} ..."
    )
    summaries: list[dict[str, object]] = []
    for i, fx_rate in enumerate(FX_PATH_COP_PER_USD, start=1):
        print(
            f"\n   --- month = {i}    fx_cop_per_usd = {fx_rate} ---"
        )
        emitter = CohortEmitter(base_dir=BASE_DIR, fx_cop_per_usd=fx_rate)
        result = emitter(
            priors=priors,
            model=model,
            posterior_idata=posterior_idata,
            prior_idata=prior_idata,
            month=i,
            random_seed=RANDOM_SEED,
        )
        print(
            f"       OK — n_rows = {result['n_rows_synthetic']}    "
            f"sha256 = {result['audit_block'][:16]}..."
        )
        summaries.append(
            {
                "month": i,
                "fx": fx_rate,
                "n_rows": result["n_rows_synthetic"],
                "tau_path": result["synthetic_tau_path"],
                "prior_path": result["cohort_prior_path"],
                "audit_path": result["audit_path"],
            }
        )

    # ─── Summary ────────────────────────────────────────────────────
    total_draws = N_CHAINS * DRAWS_PER_CHAIN
    print("\n" + "=" * 72)
    print("EMISSION SUMMARY")
    print("=" * 72)
    print(f"  sampling_seconds    : {sampling_seconds:.1f}")
    print(f"  total_draws         : {total_draws} (= {N_CHAINS} chains × {DRAWS_PER_CHAIN})")
    print(
        f"  divergences         : {int(verdict.divergence_frac * total_draws)}"
        f"  ({verdict.divergence_frac:.4%})"
    )
    print(f"  rhat_max            : {verdict.rhat_max:.6f}")
    print(f"  ess_bulk_min        : {verdict.ess_bulk_min:.1f}")
    print(f"  ess_tail_min        : {verdict.ess_tail_min:.1f}")
    print(f"  ci_width_ratio_max  : {verdict.ci_width_ratio_max:.6f}")
    print(f"  GATES               : {'PASS' if verdict.passed else 'HALT'}")
    print()
    for s in summaries:
        print(
            f"  month {s['month']}  rows={s['n_rows']}  tau={s['tau_path']}"
        )
        print(f"           prior={s['prior_path']}")
        print(f"           audit={s['audit_path']}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
