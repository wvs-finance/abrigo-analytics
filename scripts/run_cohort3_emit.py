"""Run the SAAS-COHORT-3 Υ_t form-selection pipeline end-to-end.

Driver script per CLOSE plan v0.2 Phase 0 Task 0.2b (NON-NO-OP routing per
spec v1.2.1 §15.4):

1. Generate a synthetic Υ_t panel (single trajectory, 36 months) consistent
   with Pin R5's ``UpsilonPanel`` 24-month floor — ground-truth process is
   AR(1)-log with mild persistence + multiplicative log-Normal noise.
2. Fit all three forms (martingale / AR(1)-log / det+churn) under
   spec v1.2.1's prior pins (in particular λ ~ Beta(4.5, 95.5)).
3. Run ``arviz.compare(ic="loo", method="stacking")``; route via
   :class:`VerdictRouter`.
4. Emit ``simulations/saas_builder/data/revenue_form_verdict.json`` plus
   per-form NetCDF idata sidecars.

HALT-on-flip support: pass ``--also-fit-old-prior`` to additionally fit
det+churn under the v0.3 prior Beta(2.0, 38.0) so that the ELPD ranking
under each prior can be compared directly. The verdict JSON metadata
records the prior-pair comparison.

Usage::

    uv run python scripts/run_cohort3_emit.py
    uv run python scripts/run_cohort3_emit.py --also-fit-old-prior

Anti-fishing: draws / chains / target_accept are pinned at the spec floor
and NEVER relaxed even if the new prior produces marginal samples.
``DiagnosticGateError``-equivalent gate failures flow through the verdict
router (FAIL / WEAK), not through threshold widening.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

from typing import cast

import arviz as az
import numpy as np

from simulations.saas_builder.cohort_3.io import (
    InferenceDataPersister,
    VerdictArtifactWriter,
    compute_audit_block,
)
from simulations.saas_builder.cohort_3.loo import LooComparator, VerdictRouter
from simulations.saas_builder.cohort_3.models import (
    DetChurnModelBuilder,
    FitDriver,
)
from simulations.saas_builder.cohort_3.priors import (
    DET_CHURN_LAMBDA_BETA_A,
    DET_CHURN_LAMBDA_BETA_B,
    DetChurnPrior,
)
from simulations.saas_builder.cohort_3.types import (
    REVENUE_FORM_NAMES,
    RevenueFormFit,
    RevenueFormName,
    UpsilonPanel,
)

# ─── Spec-pinned sampling configuration (Pin R4 floors) ───────────────────────

DRAWS_PER_CHAIN: int = 4000
N_CHAINS: int = 4
TUNE: int = 1000
TARGET_ACCEPT: float = 0.95
RANDOM_SEED: int = 20260508
N_MONTHS: int = 36

# Output base — gitignored (data/ tree).
BASE_DIR: Path = (
    Path(__file__).resolve().parent.parent
    / "simulations" / "saas_builder" / "data"
)
ESTIMATES_ROOT: Path = BASE_DIR / "estimates_cohort_3"
VERDICT_PATH: Path = BASE_DIR / "revenue_form_verdict.json"


def _make_synthetic_panel(seed: int = RANDOM_SEED) -> UpsilonPanel:
    """Generate a single 36-month log-AR(1) Υ_t trajectory in COP.

    Ground-truth process used for the smoke fit:

        log Υ_0 = 0.0    (Υ_0 = 1.0 — unitless smoke value)
        log Υ_t = 0.6 · log Υ_{t-1} + ε_t,  ε_t ~ N(0, 0.10)

    Centered at zero because the spec-pinned AR(1)-log form has no
    intercept; smoke realism is sacrificed for fit cleanliness. The
    relative ELPD ranking across the three forms is what the runner
    exercises — not the absolute magnitudes.

    This intentionally generates a panel that AR(1)-log fits well, with
    martingale and det+churn as competing approximations. The ELPD ranking
    under either λ-prior should pin AR(1)-log on top — IF the ranking
    flips between Beta(4.5,95.5) and Beta(2.0,38.0) we surface a HALT.
    """
    rng = np.random.default_rng(seed)
    log_y = np.empty(N_MONTHS, dtype=np.float64)
    # Centered AR(1)-log DGP: the spec-pinned AR(1)-log model is
    # ``log Υ_t = ρ · log Υ_{t-1} + ε_t`` (no intercept), so a faithful
    # smoke fit requires log-data centered near 0. Use Υ_0 = 1 (log=0)
    # and ρ = 0.6 to keep posterior mass off the |ρ|>0.95 boundary
    # (Pin R4-bis HALT). The Υ_t magnitude here is unitless / smoke-only;
    # det+churn's LogNormal Υ_0 prior (μ=14) makes this DGP a poor fit
    # for det+churn, which is the expected dominance pattern.
    log_y[0] = 0.0
    for t in range(1, N_MONTHS):
        log_y[t] = 0.6 * log_y[t - 1] + rng.normal(0.0, 0.10)
    y = np.exp(log_y)
    return UpsilonPanel(
        month_index=np.arange(N_MONTHS, dtype=np.int64),
        simulation_id=tuple(["sim_0"] * N_MONTHS),
        upsilon_cop=y,
        cohort_id=tuple(["cohort_a"] * N_MONTHS),
    )


def _fit_all_forms(
    panel: UpsilonPanel,
    persister: InferenceDataPersister,
    *,
    det_churn_prior: DetChurnPrior | None = None,
    suffix: str = "",
) -> tuple[dict[str, RevenueFormFit], dict[str, az.InferenceData]]:
    """Fit all three forms; persist idata; return (fits, idata_per_form).

    ``det_churn_prior``: optional override for the det+churn prior. None →
    use spec-default (v1.2.1 Beta(4.5, 95.5)).
    ``suffix``: appended to the on-disk NetCDF filename (e.g. "_oldprior").
    """
    driver = FitDriver(
        draws=DRAWS_PER_CHAIN,
        chains=N_CHAINS,
        tune=TUNE,
        target_accept=TARGET_ACCEPT,
        seed=RANDOM_SEED,
        cv_method="loo",
    )
    fits: dict[str, RevenueFormFit] = {}
    idatas: dict[str, az.InferenceData] = {}

    for form_name in REVENUE_FORM_NAMES:
        form_name_typed = cast(RevenueFormName, form_name)
        nc_name = f"{form_name}{suffix}"
        idata_path = str(persister.path_for(nc_name))
        t_start = time.monotonic()

        # det+churn supports optional prior override; the other two forms
        # do not depend on the λ prior so they are fit once.
        if form_name == "det_churn" and det_churn_prior is not None:
            builder = DetChurnModelBuilder(prior=det_churn_prior)
            # Manually replicate FitDriver but with the override builder.
            # (FitDriver uses _BUILDER_REGISTRY default-constructed builders.)
            idata, fit = _fit_with_custom_builder(
                builder, panel, idata_path, driver
            )
        else:
            idata, fit = driver(form_name_typed, panel, idata_path)

        elapsed = time.monotonic() - t_start
        print(
            f"  fit {form_name}{suffix}: rhat={fit.rhat_max:.4f} "
            f"ess_bulk={fit.ess_bulk_min:.0f} ess_tail={fit.ess_tail_min:.0f} "
            f"k_max={fit.pareto_k_max:.3f} k_high={fit.pareto_k_high_frac:.3f} "
            f"gates={fit.gates_passed} ({elapsed:.1f}s)",
            flush=True,
        )
        persister.write(nc_name, idata)
        fits[form_name] = fit
        idatas[form_name] = idata
    return fits, idatas


def _fit_with_custom_builder(
    builder: DetChurnModelBuilder,
    panel: UpsilonPanel,
    idata_path: str,
    driver: FitDriver,
) -> tuple[az.InferenceData, RevenueFormFit]:
    """Fit a single form with a custom-constructed builder.

    Replicates :meth:`FitDriver.__call__` minus the registry lookup so that
    a non-default builder (e.g. det+churn under the legacy λ prior) can be
    fit while still passing through Pin R4 gate evaluation.
    """
    import pymc as pm  # noqa: PLC0415

    from simulations.saas_builder.cohort_3.models import (
        _pareto_k_stats,
        _summary_diagnostics,
        evaluate_gates,
    )

    model = builder(panel)
    with model:
        idata = pm.sample(
            draws=driver.draws,
            chains=driver.chains,
            tune=driver.tune,
            target_accept=driver.target_accept,
            random_seed=driver.seed,
            progressbar=False,
            idata_kwargs={"log_likelihood": True},
        )
    loo_result = az.loo(idata, pointwise=True)
    rhat_max, ess_bulk_min, ess_tail_min = _summary_diagnostics(idata)
    pareto_k_max, pareto_k_high_frac = _pareto_k_stats(loo_result)
    gates_passed = evaluate_gates(
        rhat_max=rhat_max,
        ess_bulk_min=ess_bulk_min,
        ess_tail_min=ess_tail_min,
        n_chains=driver.chains,
        n_draws_per_chain=driver.draws,
        pareto_k_high_frac=pareto_k_high_frac,
    )
    fit = RevenueFormFit(
        form_name="det_churn",
        idata_path=idata_path,
        rhat_max=rhat_max,
        ess_bulk_min=ess_bulk_min,
        ess_tail_min=ess_tail_min,
        n_chains=driver.chains,
        n_draws_per_chain=driver.draws,
        pareto_k_max=pareto_k_max,
        pareto_k_high_frac=pareto_k_high_frac,
        gates_passed=gates_passed,
        rho_boundary_mass=None,
        cv_method="loo",
    )
    return idata, fit


def _emit_verdict(
    fits: dict[str, RevenueFormFit],
    idatas: dict[str, az.InferenceData],
    persister: InferenceDataPersister,
    *,
    metadata: dict[str, object],
) -> None:
    """Run LooComparator + VerdictRouter; persist to revenue_form_verdict.json."""
    comparator = LooComparator(method="stacking")
    comparison = comparator(idatas)
    router = VerdictRouter()
    fetched_at = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    audit_block = compute_audit_block(
        parquet_path="synthetic-AR1log-36mo",
        cohort_prior_fetched_at_utc=fetched_at,
        idata_paths={k: persister.path_for(k) for k in fits},
    )
    verdict = router(
        comparison=comparison,
        fits=fits,
        audit_block=audit_block,
        fetched_at_utc=fetched_at,
    )
    writer = VerdictArtifactWriter(persister.estimates_root)
    writer.write(verdict)

    # Write the canonical revenue_form_verdict.json with metadata sidecar.
    payload = json.loads((persister.estimates_root / "cohort_3_verdict.json").read_text())
    payload["_metadata"] = metadata
    payload["_comparison"] = {
        "ranked_forms": list(comparison.ranked_forms),
        "elpd_loo": dict(comparison.elpd_loo),
        "elpd_diff": dict(comparison.elpd_diff),
        "dse": dict(comparison.dse),
        "weight": dict(comparison.weight),
        "se": dict(comparison.se),
    }
    payload["_per_form_diagnostics"] = {
        name: {
            "rhat_max": f.rhat_max,
            "ess_bulk_min": f.ess_bulk_min,
            "ess_tail_min": f.ess_tail_min,
            "pareto_k_max": f.pareto_k_max,
            "pareto_k_high_frac": f.pareto_k_high_frac,
            "gates_passed": f.gates_passed,
            "rho_boundary_mass": f.rho_boundary_mass,
        }
        for name, f in fits.items()
    }
    VERDICT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VERDICT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"\nverdict written → {VERDICT_PATH}")
    print(f"  verdict={verdict.verdict}  winning_form={verdict.winning_form!r}")
    print(f"  Δelpd={verdict.delta_elpd_loo:.3f}  se={verdict.se:.3f}")
    print(f"  ranked={comparison.ranked_forms}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--also-fit-old-prior",
        action="store_true",
        help="Also fit det+churn under v0.3 Beta(2.0, 38.0) for HALT-on-flip "
             "comparison.",
    )
    args = parser.parse_args(argv)

    print("=" * 72)
    print("SAAS-COHORT-3 Υ_t form-selection — spec v1.2.1 prior pin")
    print("=" * 72)
    print(f"λ ~ Beta(α={DET_CHURN_LAMBDA_BETA_A}, β={DET_CHURN_LAMBDA_BETA_B})")
    print(f"  → mean = {DET_CHURN_LAMBDA_BETA_A / (DET_CHURN_LAMBDA_BETA_A + DET_CHURN_LAMBDA_BETA_B):.4f}")
    print(f"  → concentration α+β = {DET_CHURN_LAMBDA_BETA_A + DET_CHURN_LAMBDA_BETA_B:.1f}")
    print(f"draws/chain={DRAWS_PER_CHAIN} chains={N_CHAINS} target_accept={TARGET_ACCEPT}")
    print()

    panel = _make_synthetic_panel()
    print(f"synthetic panel: {N_MONTHS} months, log-AR(1) ground truth (ρ=0.6, c=0)")

    ESTIMATES_ROOT.mkdir(parents=True, exist_ok=True)
    persister = InferenceDataPersister(ESTIMATES_ROOT)

    # Fit all three forms under the spec v1.2.1 (new) prior.
    print("\n[1/2] fitting under spec v1.2.1 prior λ ~ Beta(4.5, 95.5) …")
    new_fits, new_idatas = _fit_all_forms(panel, persister)
    new_comparator = LooComparator(method="stacking")
    new_comparison = new_comparator(new_idatas)

    metadata: dict[str, object] = {
        "spec_version": "v1.2.1",
        "prior_pin": "Beta(4.5, 95.5)",
        "prior_mean": 0.045,
        "prior_concentration": 100.0,
        "task": "CLOSE Phase 0 Task 0.2b (NON-NO-OP per §15.4)",
        "synthetic_panel_dgp": "log-AR(1) centered: log Υ_0=0, ρ=0.6, σ=0.10, 36 months",
        "halt_on_flip_comparison": False,
    }

    if args.also_fit_old_prior:
        print("\n[2/2] fitting det+churn under legacy v0.3 prior λ ~ Beta(2.0, 38.0) …")
        legacy_prior = DetChurnPrior(lambda_beta_a=2.0, lambda_beta_b=38.0)
        # Reuse the existing martingale + ar1_log idatas (no λ dependence);
        # only re-fit det+churn under the legacy prior.
        legacy_det_idata, legacy_det_fit = _fit_with_custom_builder(
            DetChurnModelBuilder(prior=legacy_prior),
            panel,
            str(persister.path_for("det_churn_oldprior")),
            FitDriver(
                draws=DRAWS_PER_CHAIN,
                chains=N_CHAINS,
                tune=TUNE,
                target_accept=TARGET_ACCEPT,
                seed=RANDOM_SEED,
                cv_method="loo",
            ),
        )
        persister.write("det_churn_oldprior", legacy_det_idata)
        print(
            f"  fit det_churn_oldprior: rhat={legacy_det_fit.rhat_max:.4f} "
            f"ess_bulk={legacy_det_fit.ess_bulk_min:.0f} "
            f"ess_tail={legacy_det_fit.ess_tail_min:.0f} "
            f"k_max={legacy_det_fit.pareto_k_max:.3f} "
            f"gates={legacy_det_fit.gates_passed}",
            flush=True,
        )
        # Build the legacy-prior comparison: martingale + ar1_log + det_churn(legacy).
        legacy_idatas: dict[str, az.InferenceData] = dict(new_idatas)
        legacy_idatas["det_churn"] = legacy_det_idata
        legacy_comparison = LooComparator(method="stacking")(legacy_idatas)
        # HALT-on-flip check: do the rankings agree?
        new_top = new_comparison.ranked_forms[0]
        legacy_top = legacy_comparison.ranked_forms[0]
        flipped = new_top != legacy_top
        metadata["halt_on_flip_comparison"] = True
        metadata["legacy_prior_pin"] = "Beta(2.0, 38.0)"
        metadata["legacy_prior_mean"] = 0.05
        metadata["legacy_prior_concentration"] = 40.0
        metadata["legacy_ranked_forms"] = list(legacy_comparison.ranked_forms)
        metadata["legacy_elpd_loo"] = dict(legacy_comparison.elpd_loo)
        metadata["new_ranked_forms"] = list(new_comparison.ranked_forms)
        metadata["new_top_form"] = new_top
        metadata["legacy_top_form"] = legacy_top
        metadata["rank_flip_detected"] = flipped
        print()
        print("=" * 72)
        print(f"HALT-on-flip check: new_top={new_top!r}  legacy_top={legacy_top!r}")
        if flipped:
            print(">>> RANK FLIP DETECTED — surfaces to spec/plan amendment per §15.4 <<<")
        else:
            print(">>> no-flip-confirmed — verdict ranking is robust to prior choice <<<")
        print("=" * 72)

    _emit_verdict(new_fits, new_idatas, persister, metadata=metadata)
    return 0


if __name__ == "__main__":
    sys.exit(main())
