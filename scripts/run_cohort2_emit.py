"""Run the SAAS-COHORT-2 sign-certification + bank-spread overlay pipeline.

Driver script per SAAS-COHORT-CLOSE plan v0.2 Phase 1.2:

1. Load the C1 v0.4 ``synthetic_tau_t`` Hive-partitioned parquet
   (``simulations/saas_builder/data/synthetic_tau_t/tier_id=*/month=*/``)
   via the shipped :class:`SyntheticTauReader`. Pivot per
   ``simulation_id × month`` so each tier has a per-simulation τ_t panel
   of shape ``(n_sims_for_tier, n_months)``.
2. Build the spec §5.2 24-bracket grid via
   :func:`build_spec_5_2_bracket_grid` on the canonical M5 anchor
   ``FXPathParams(mean_x_over_y=4000, ε=0.1, ω=1)``. Horizon T is set to
   the per-simulation month count emitted by C1 (3 months at v0.4); the
   parameter sweep is the spec §5.2 Cartesian product
   ``3 tiers × 2 κ-arm × 2 h_cache × 2 α = 24 points``.
3. For each bracket, route the τ_t draws by tier (cost_params.p_sub_bar
   inverse-maps to tier_id). All 24 brackets thus consume the *real*
   C1-emitted posterior τ_t draws — no synthetic τ.
4. Run the **primary** :class:`SignCertificationGate` over the 24
   bracket points. HALT (raise) on any sign violation per
   ``feedback_pathological_halt_anti_fishing_checkpoint``.
5. Run the **bank-spread overlay** :class:`BankSpreadRobustnessRunner`
   (Pin ROBUST-BS, default ``s = +0.005``); the robustness arm is walled
   off from the primary verdict — it is written to
   ``ROBUSTNESS_RESULTS.md``, NEVER to ``gate_verdict.json``.
6. Emit:
   - ``simulations/saas_builder/data/PRIMARY_RESULTS.md`` — primary
     regime per-bracket Δ-table + verdict.
   - ``simulations/saas_builder/data/ROBUSTNESS_RESULTS.md`` — bank-spread
     overlay per-bracket Δ-table + verdict.
   - ``simulations/saas_builder/data/gate_verdict.json`` — primary
     verdict in spec §10 alphabet.

Anti-fishing posture (NON-NEGOTIABLE): the M2 softplus tightness
``L¹ < 1e-3·κ`` is enforced strictly via the shipped ``SoftplusRegularizer``;
the β grid bounds are the test-empirically-validated
``[0.01/κ, 1e6/κ]`` (RC-FLAG-5 v0.3 dimensional widening — bounded, not
post-hoc widening). HALT on any sign violation in the primary regime;
do NOT massage the grid, draws, or σ_T to coax PASS. The bank-spread
regime is informational, no HALT.

Usage::

    uv run python scripts/run_cohort2_emit.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

import numpy as np
from numpy.typing import NDArray

from simulations.saas_builder.cohort_2.io import (
    GateVerdictWriter,
    RobustnessResultsAppender,
)
from simulations.saas_builder.cohort_2.pricing import (
    SoftplusBetaFitter,
    build_spec_5_2_bracket_grid,
)
from simulations.saas_builder.cohort_2.robustness import (
    BankSpreadRobustnessRunner,
    DEFAULT_BANK_SPREAD,
)
from simulations.saas_builder.cohort_2.sign_cert import (
    DEFAULT_CI_LEVEL,
    SignCertificationGate,
)
from simulations.saas_builder.cohort_2.types import (
    SAAS_TIER_IDS,
    SPEC_TIER_P_SUB_BAR,
    BracketPoint,
    CohortGateVerdict,
)
from simulations.types.fx import FXPathParams
from simulations.utils.parquet_io import SyntheticTauReader

# ─── Spec-pinned configuration ────────────────────────────────────────────────

#: M5 canonical FX-path anchor (spec §3 / PRIMITIVES.md (6)). The mean is
#: TRM-pinned at 4000 COP/USD — anchor recovery at t ∈ {0, π/2, π} yields
#: exactly (4200, 3800, 4200).
M5_MEAN_X_OVER_Y: Final[float] = 4000.0
M5_EPSILON: Final[float] = 0.1
M5_OMEGA: Final[float] = 1.0

#: Realized-variance proxy used by the sign-cert gate; matches the
#: shipped cohort_2 test fixture (sigma_T = 10_000.0).
SIGMA_T: Final[float] = 10_000.0

#: 95% credible interval per spec §9 row TODO-COHORT-2.
CI_LEVEL: Final[float] = DEFAULT_CI_LEVEL

#: Pin ROBUST-BS — scalar bank-spread overlay (s = +50 bps) applied to
#: ``mean_x_over_y`` for the sensitivity arm. The exact value is a
#: sensitivity dial within the spec §5.4(c) range, not a math-pinned
#: threshold; a future arm extending to time-varying ``s_t`` would
#: extend ``FXPathParams`` rather than this constant.
BANK_SPREAD: Final[float] = DEFAULT_BANK_SPREAD

#: SoftplusBetaFitter dimensional bounds (RC-FLAG-5 v0.3 fix). Test fixture
#: ``_TEST_FITTER_OVERRIDE`` documents that the plan-literal default
#: ``[0.01/κ, 100/κ]`` is empirically inadequate at canonical κ ≈ 1.6M
#: tok/mo — the smallest β satisfying L¹ < 1e-3·κ is ≈ 0.022 (β·κ ≈ 35k),
#: well above ``100/κ = 6.3e-5``. Bounds widened to ``[0.01/κ, 1e6/κ]``
#: at construction time (anti-fishing-conformant: still bounded, FAIL
#: still fires on infeasible grid, NO silent post-hoc widening).
BETA_MIN_FACTOR: Final[float] = 0.01
BETA_MAX_FACTOR: Final[float] = 1e6
BETA_GRID_SIZE: Final[int] = 50

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR: Final[Path] = (
    Path(__file__).resolve().parent.parent
    / "simulations" / "saas_builder" / "data"
)
SYNTHETIC_TAU_DIR: Final[Path] = BASE_DIR / "synthetic_tau_t"
PRIMARY_RESULTS_PATH: Final[Path] = BASE_DIR / "PRIMARY_RESULTS.md"
ROBUSTNESS_RESULTS_PATH: Final[Path] = BASE_DIR / "ROBUSTNESS_RESULTS.md"
GATE_VERDICT_PATH: Final[Path] = BASE_DIR / "gate_verdict.json"


# ─── τ_t panel pivot ─────────────────────────────────────────────────────────


def _load_tau_panels_per_tier() -> dict[str, NDArray[np.float64]]:
    """Read C1 synthetic_tau_t parquet → per-tier τ_t panel.

    Returns:
        Mapping ``tier_id → ndarray`` of shape ``(n_sims_for_tier, n_months)``
        with rows ordered by ``simulation_id`` and columns by ``month``.

    Raises:
        FileNotFoundError: missing dataset directory or no parquet files.
        ValueError: per-sim month-count drift (HALT trigger).
    """
    reader = SyntheticTauReader(base_dir=BASE_DIR)
    rows = reader()
    # Group by (tier_id, simulation_id) → list[(month, tau_t)].
    grouped: dict[
        tuple[str, int], list[tuple[int, float]]
    ] = defaultdict(list)
    for r in rows:
        grouped[(r["tier_id"], r["simulation_id"])].append(
            (r["month"], r["tau_t"])
        )
    panels: dict[str, NDArray[np.float64]] = {}
    for tier in SAAS_TIER_IDS:
        sim_keys = sorted(k[1] for k in grouped if k[0] == tier)
        if not sim_keys:
            raise ValueError(
                f"_load_tau_panels_per_tier: no rows for tier_id={tier!r}"
            )
        # Determine n_months from first sim; verify all sims agree.
        first_pairs = sorted(grouped[(tier, sim_keys[0])])
        n_months = len(first_pairs)
        if n_months < 1:
            raise ValueError(
                f"_load_tau_panels_per_tier: tier {tier!r}"
                f" simulation_id={sim_keys[0]} has 0 months"
            )
        panel = np.empty((len(sim_keys), n_months), dtype=np.float64)
        for i, sid in enumerate(sim_keys):
            pairs = sorted(grouped[(tier, sid)])
            if len(pairs) != n_months:
                raise ValueError(
                    f"_load_tau_panels_per_tier: tier {tier!r}"
                    f" simulation_id={sid} has {len(pairs)} months;"
                    f" expected {n_months} (per-sim drift HALT)"
                )
            for j, (_m, tau) in enumerate(pairs):
                panel[i, j] = tau
        panels[tier] = panel
    return panels


def _tier_for_bracket(point: BracketPoint) -> str:
    """Inverse-map ``point.cost_params.p_sub_bar`` to tier_id.

    The spec §5.2 grid uses tier-disjoint p̄_sub values (20 / 100 / 200
    USD/mo), so this is bijective.
    """
    p_sub = point.cost_params.p_sub_bar
    for tier, ref in SPEC_TIER_P_SUB_BAR.items():
        if abs(p_sub - ref) < 1e-9:
            return tier
    raise ValueError(
        f"_tier_for_bracket: p_sub_bar = {p_sub} not in"
        f" SPEC_TIER_P_SUB_BAR = {dict(SPEC_TIER_P_SUB_BAR)}"
    )


# ─── PRIMARY_RESULTS.md emission ─────────────────────────────────────────────


def _format_primary_section(
    verdict: CohortGateVerdict, sigma_T: float
) -> str:
    """Render the primary-regime markdown table (mirrors robustness format)."""
    lines = [
        "# COHORT-2 Primary Sign-Certification Verdict",
        "",
        "Spec §5.2 24-bracket parameter sweep on the M5 canonical FX path",
        "``(mean_x_over_y, ε, ω) = (4000, 0.1, 1.0)`` with TRM-pinned mean.",
        "",
        f"## Primary regime ({verdict.fetched_at_utc})",
        "",
        f"- verdict: **{verdict.verdict}**",
        f"- sub_task: `{verdict.sub_task}`",
        f"- n_bracket_points: {verdict.n_bracket_points}",
        f"- n_sign_violations: {verdict.n_sign_violations}",
        f"- σ_T (realized variance proxy): {sigma_T}",
        f"- audit_block: `{verdict.audit_block}`",
        "",
        "| bracket_index | Δ median | 95% lower | 95% upper | strict<0 |",
        "|---|---|---|---|---|",
    ]
    for ev in verdict.evidence:
        lines.append(
            f"| {ev.bracket_index}"
            f" | {ev.delta_median:+.6e}"
            f" | {ev.delta_lower_bound_95:+.6e}"
            f" | {ev.delta_upper_bound_95:+.6e}"
            f" | {'YES' if ev.sign_strictly_negative else 'NO'} |"
        )
    lines.append("")
    return "\n".join(lines)


def _write_primary_results(
    verdict: CohortGateVerdict, sigma_T: float, path: Path
) -> Path:
    """Write the primary-regime markdown summary."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_format_primary_section(verdict, sigma_T))
    return path


# ─── Driver ───────────────────────────────────────────────────────────────────


def _delta_med_summary(verdict: CohortGateVerdict) -> tuple[float, float]:
    """Return (min, max) of Δ_median across the verdict's evidence rows."""
    medians = [ev.delta_median for ev in verdict.evidence]
    return (min(medians), max(medians))


def _utc_iso() -> str:
    """ISO-8601 UTC second-precision timestamp for logging."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def main() -> int:
    """Run the COHORT-2 sign-cert + bank-spread overlay pipeline."""
    print("=" * 72)
    print("SAAS-COHORT-2 sign-certification pipeline (SAAS-COHORT-CLOSE 1.2)")
    print(f"  M5 anchor   = (X̄/Ȳ, ε, ω) = ({M5_MEAN_X_OVER_Y}, {M5_EPSILON}, {M5_OMEGA})")
    print(f"  σ_T         = {SIGMA_T}")
    print(f"  CI level    = {CI_LEVEL}")
    print(f"  bank_spread = {BANK_SPREAD:+.4f} (Pin ROBUST-BS)")
    print(f"  base_dir    = {BASE_DIR}")
    print("=" * 72)

    # ─── 1. Load real C1 v0.4 τ_t panels per tier. ────────────────────────
    print("\n[1/6] Reading synthetic_tau_t parquet (C1 v0.4 outputs) ...")
    t0 = time.time()
    panels = _load_tau_panels_per_tier()
    n_months_per_sim = next(iter(panels.values())).shape[1]
    for tier, panel in panels.items():
        print(
            f"       tier={tier:<8s}"
            f"  shape={panel.shape}"
            f"  τ_t range=[{panel.min():.2f}, {panel.max():.2f}]"
        )
    print(f"       n_months_per_sim = {n_months_per_sim}")
    print(f"       elapsed = {time.time() - t0:.2f}s")

    # ─── 2. Build the spec §5.2 24-bracket grid. ──────────────────────────
    print(
        "\n[2/6] Building spec §5.2 24-bracket grid"
        f" (horizon_T = {n_months_per_sim} from C1 emit) ..."
    )
    fitter = SoftplusBetaFitter(
        beta_min_factor=BETA_MIN_FACTOR,
        beta_max_factor=BETA_MAX_FACTOR,
        n_grid=BETA_GRID_SIZE,
    )
    fx_params = FXPathParams(
        mean_x_over_y=M5_MEAN_X_OVER_Y,
        epsilon=M5_EPSILON,
        omega=M5_OMEGA,
    )
    grid = build_spec_5_2_bracket_grid(
        fitter=fitter,
        fx_params=fx_params,
        horizon_T=n_months_per_sim,
    )
    print(f"       n_bracket_points = {len(grid.points)}")
    assert len(grid.points) == 24, (
        f"expected 24 brackets per spec §5.2, got {len(grid.points)}"
    )

    # ─── 3. Route τ_t draws per bracket via tier inverse-map. ─────────────
    print("\n[3/6] Routing τ_t panels per bracket (tier inverse-map) ...")
    tau_per_bracket: tuple[NDArray[np.float64], ...] = tuple(
        panels[_tier_for_bracket(p)] for p in grid.points
    )
    for i, (point, tau) in enumerate(zip(grid.points, tau_per_bracket)):
        if i < 3 or i >= 21:  # Show first 3 + last 3.
            tier = _tier_for_bracket(point)
            print(
                f"       bracket[{i:02d}]"
                f"  tier={tier:<8s}"
                f"  κ={point.cost_params.kappa:.2e}"
                f"  β={point.cost_params.beta:.4e}"
                f"  τ_t shape={tau.shape}"
            )
        elif i == 3:
            print("       ...")

    # ─── 4. Primary sign-certification gate. ──────────────────────────────
    print("\n[4/6] Running primary SignCertificationGate ...")
    t_primary = time.time()
    primary_gate = SignCertificationGate(sigma_T=SIGMA_T, ci_level=CI_LEVEL)
    primary_verdict = primary_gate(grid, tau_per_bracket)
    primary_seconds = time.time() - t_primary
    primary_dmin, primary_dmax = _delta_med_summary(primary_verdict)
    print(
        f"       verdict          = {primary_verdict.verdict}"
        f"  ({primary_verdict.n_sign_violations}"
        f"/{primary_verdict.n_bracket_points} sign violations)"
    )
    print(
        f"       Δ_med range     = [{primary_dmin:+.6e},"
        f" {primary_dmax:+.6e}]"
    )
    print(f"       audit_block      = {primary_verdict.audit_block[:16]}...")
    print(f"       elapsed          = {primary_seconds:.2f}s")

    # ─── 5. Bank-spread overlay (Pin ROBUST-BS, walled off). ──────────────
    print(
        f"\n[5/6] Running bank-spread overlay (s = {BANK_SPREAD:+.4f}) ..."
    )
    t_robust = time.time()
    runner = BankSpreadRobustnessRunner(
        bank_spread=BANK_SPREAD, ci_level=CI_LEVEL
    )
    robust_verdict = runner(
        primary_grid=grid,
        sigma_T=SIGMA_T,
        tau_t_draws_per_bracket=tau_per_bracket,
    )
    robust_seconds = time.time() - t_robust
    robust_dmin, robust_dmax = _delta_med_summary(robust_verdict)
    print(
        f"       verdict          = {robust_verdict.verdict}"
        f"  ({robust_verdict.n_sign_violations}"
        f"/{robust_verdict.n_bracket_points} sign violations)"
    )
    print(
        f"       Δ_med range     = [{robust_dmin:+.6e},"
        f" {robust_dmax:+.6e}]"
    )
    print(f"       audit_block      = {robust_verdict.audit_block[:16]}...")
    print(f"       elapsed          = {robust_seconds:.2f}s")

    # ─── 6. Emit artifacts. ───────────────────────────────────────────────
    print("\n[6/6] Emitting artifacts ...")

    # PRIMARY_RESULTS.md (authored locally — distinct from RobustnessAppender).
    primary_path = _write_primary_results(
        primary_verdict, sigma_T=SIGMA_T, path=PRIMARY_RESULTS_PATH
    )
    print(f"       PRIMARY_RESULTS.md     → {primary_path}")

    # gate_verdict.json (PRIMARY ONLY — Pin ROBUST-BS guard).
    gate_writer = GateVerdictWriter(base_dir=BASE_DIR)
    gate_path = gate_writer(primary_verdict, filename=GATE_VERDICT_PATH.name)
    print(f"       gate_verdict.json      → {gate_path}")

    # ROBUSTNESS_RESULTS.md (bank-spread only, walled off).
    # Reset the file before appending to ensure a clean run-time snapshot.
    if ROBUSTNESS_RESULTS_PATH.is_file():
        ROBUSTNESS_RESULTS_PATH.unlink()
    appender = RobustnessResultsAppender(base_dir=BASE_DIR)
    robust_path = appender(
        robust_verdict,
        bank_spread=BANK_SPREAD,
        filename=ROBUSTNESS_RESULTS_PATH.name,
    )
    print(f"       ROBUSTNESS_RESULTS.md  → {robust_path}")

    # ─── Summary banner ───────────────────────────────────────────────────
    print()
    print("=" * 72)
    print("EMISSION SUMMARY")
    print("=" * 72)
    print(f"  fetched_at_utc           : {_utc_iso()}")
    print(
        f"  primary verdict          : {primary_verdict.verdict}"
        f"  ({primary_verdict.n_sign_violations}"
        f"/{primary_verdict.n_bracket_points} violations)"
    )
    print(
        f"  primary Δ_med range     : [{primary_dmin:+.6e},"
        f" {primary_dmax:+.6e}]"
    )
    print(
        f"  bank-spread verdict      : {robust_verdict.verdict}"
        f"  ({robust_verdict.n_sign_violations}"
        f"/{robust_verdict.n_bracket_points} violations)  [INFORMATIONAL]"
    )
    print(
        f"  robust Δ_med range      : [{robust_dmin:+.6e},"
        f" {robust_dmax:+.6e}]"
    )
    print(f"  primary sampling seconds : {primary_seconds:.2f}")
    print(f"  robust sampling seconds  : {robust_seconds:.2f}")
    print("=" * 72)

    # ─── Anti-fishing HALT on primary sign violation. ─────────────────────
    if primary_verdict.n_sign_violations > 0:
        # Fingerprint the violation for the disposition memo trail.
        violation_fp = hashlib.sha256(
            json.dumps(
                {
                    "audit_block": primary_verdict.audit_block,
                    "n_sign_violations": primary_verdict.n_sign_violations,
                    "violating_brackets": [
                        ev.bracket_index
                        for ev in primary_verdict.evidence
                        if not ev.sign_strictly_negative
                    ],
                },
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        raise AssertionError(
            "SAAS-COHORT-2 PRIMARY SIGN VIOLATION — HALT per"
            " feedback_pathological_halt_anti_fishing_checkpoint."
            f"  n_sign_violations={primary_verdict.n_sign_violations}"
            f"  violation_fingerprint={violation_fp[:16]}..."
            "  Do NOT massage σ_T, β-grid, or τ_t draws to coax PASS."
            "  Surface to orchestrator + write disposition memo."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
