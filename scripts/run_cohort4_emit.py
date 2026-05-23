"""Run the SAAS-COHORT-4 Z-cap pin emission pipeline end-to-end.

Driver script per CLOSE plan v0.2 Phase 1.3:

1. Load real C1 v0.4 ``synthetic_tau_t`` posterior-predictive ``q_t_cop``
   draws from the canonical Hive-partitioned parquet tree.
2. Verify the 5 audit-block input files are present (HALT on missing).
3. Build the canonical Pin-M2 5-test-point grid via
   ``make_default_test_point_grid``.
4. Drive the full ``pin_and_emit`` pipeline:
       - Derive π(t) symbolic + lambdified (Pin M1).
       - Compute audit-block sha256 over the 5-file input set (Pin M4).
       - Run ``ZCapRunner`` (per-draw Z evaluator + sign + monotonicity +
         identity gates).
       - Emit ``Z_cap_pinned.json`` + ``Z_cap_pinned.SIGN_VERDICTS.md``.

**Expected HALT route (Phase 1.3).** The C4 v0.3 smoke test established
that real C1 v0.4's CV ≈ 0.84 produces ``stderr/Ẑ ≈ 1.3e-2 >> 1e-3``
ceiling at the C1-emitted N_draws (~16k truncated to MC_DRAWS_FLOOR =
4000 in ``ZCapRunner``). The expected outcome of this Phase-1.3 run is a
clean ``MCErrorBudgetExceededError`` HALT — the runner records this as a
soft failure (exit code 3, sidecar emission with EXCEEDED status). Phase 2
(CLOSE plan v0.2) resolves via N_draws bump to ≈ 7.1e5 (Path α).

**Anti-fishing invariants (NEVER relaxed).**

- The MC stderr/Ẑ ≤ 1e-3 ceiling is NOT widened. HALT is the correct
  route per the spec §8(1) HALT protocol.
- The κ-monotonicity gate (∂|π|/∂κ < 0) v0.2 form is NOT reintroduced;
  the v0.3 honest derivation (κ ∉ free_symbols(π)) is preserved.
- Spec floors (MC_DRAWS_FLOOR = 4000) are NOT relaxed.

Usage::

    uv run python scripts/run_cohort4_emit.py
"""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path
from typing import Final

import numpy as np

from simulations.saas_builder.cohort_4._errors import (
    DiagnosticGateError,
    IdentityToleranceError,
    MCErrorBudgetExceededError,
)
from simulations.saas_builder.cohort_4.io import (
    DEFAULT_AUDIT_INPUT_RELATIVE_PATHS,
    AuditBlockResolver,
    pin_and_emit,
)
from simulations.saas_builder.cohort_4.types import (
    MC_DRAWS_FLOOR,
    MC_STDERR_RATIO_CEILING,
    make_default_test_point_grid,
)
from simulations.utils.parquet_io import SyntheticTauReader

# ─── Repo / output anchors ───────────────────────────────────────────────────

REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent

C1_SYNTH_DIR: Final[Path] = (
    REPO_ROOT / "simulations" / "saas_builder" / "data" / "synthetic_tau_t"
)

EMIT_DIR: Final[Path] = (
    REPO_ROOT / "simulations" / "saas_builder" / "data"
)


def _verify_upstream_artifacts() -> tuple[list[Path], list[Path]]:
    """Verify all 5 Pin-M4 audit-block inputs are present.

    Returns (present, missing). Phase-1.3 soft-fallback: ``PRIMARY_RESULTS.md``
    and ``ROBUSTNESS_RESULTS.md`` are tolerated as missing only if Phase 1.2
    has not yet completed (the audit-block resolver will still HALT — this
    fallback only annotates the runtime banner).
    """
    paths = [(REPO_ROOT / Path(rel)).resolve() for rel in DEFAULT_AUDIT_INPUT_RELATIVE_PATHS]
    present = [p for p in paths if p.exists()]
    missing = [p for p in paths if not p.exists()]
    return present, missing


def _load_q_t_cop_draws() -> np.ndarray:
    """Load posterior-predictive ``q_t_cop`` from the C1 v0.4 panel."""
    if not C1_SYNTH_DIR.is_dir():
        raise FileNotFoundError(
            f"C1 synthetic_tau_t panel missing at {C1_SYNTH_DIR}"
        )
    reader = SyntheticTauReader()
    rows = reader(C1_SYNTH_DIR)
    if len(rows) == 0:
        raise RuntimeError(
            f"C1 synthetic_tau_t panel is empty at {C1_SYNTH_DIR}"
        )
    q = np.asarray([r["q_t_cop"] for r in rows], dtype=np.float64)
    if q.size < MC_DRAWS_FLOOR:
        raise RuntimeError(
            f"C1 panel has {q.size} rows, below MC_DRAWS_FLOOR={MC_DRAWS_FLOOR}"
        )
    return q


def _emit_halt_sidecar(
    audit_block: str,
    halt_reason: str,
    halt_class: str,
    cv_real: float,
    n_draws_used: int,
    expected_stderr_ratio: float,
) -> Path:
    """Write a Z_cap_pinned.SIGN_VERDICTS.md sidecar with EXCEEDED status.

    Phase-1.3 deferred-additive-bump: ``ZCapPinned`` schema lacks a
    ``mc_error_budget_status`` field, so we DO NOT emit a partial JSON
    (would pollute the round-trip equality check). Instead we emit the
    sidecar only, annotating the budget breach for Phase-2 disposition.
    """
    EMIT_DIR.mkdir(parents=True, exist_ok=True)
    sidecar = EMIT_DIR / "Z_cap_pinned.SIGN_VERDICTS.md"
    body = (
        "# Z_cap_pinned — SIGN VERDICTS sidecar (PHASE-1.3 HALT)\n\n"
        "**Status:** `mc_error_budget_status=\"EXCEEDED, deferred to Phase 2\"`\n\n"
        f"**HALT class:** `{halt_class}`\n\n"
        f"**HALT reason:** {halt_reason}\n\n"
        "## MC error-budget metrics (Pin M2-fix)\n\n"
        f"- ``MC_DRAWS_FLOOR`` (spec floor, runner truncation): {MC_DRAWS_FLOOR}\n"
        f"- ``MC_STDERR_RATIO_CEILING``: {MC_STDERR_RATIO_CEILING:.6e}\n"
        f"- C1 q_t_cop draws available: {n_draws_used}\n"
        f"- Empirical CV(q_t_cop): {cv_real:.6f}\n"
        f"- Expected stderr/Ẑ at N={MC_DRAWS_FLOOR}: {expected_stderr_ratio:.6e}\n"
        f"- Budget breach factor: {expected_stderr_ratio / MC_STDERR_RATIO_CEILING:.2f}×\n\n"
        "## Audit block (Pin M4)\n\n"
        f"`{audit_block}`\n\n"
        "## Anti-fishing record\n\n"
        "Per CLOSE plan v0.2 Phase 1.3 / Phase 2 path α, the resolution is\n"
        "to bump N_draws ≈ 7.1e5 (4 chains × 178k) at the C1 emit stage,\n"
        "NOT to widen the MC stderr/Ẑ ceiling. The 1e-3 ceiling is\n"
        "anti-fishing-locked per spec §8(1) + the\n"
        "`feedback_pathological_halt_anti_fishing_checkpoint` rule. No\n"
        "partial `Z_cap_pinned.json` is emitted (the JSON schema lacks a\n"
        "budget-status field; emitting would pollute the round-trip\n"
        "equality check). This sidecar is the canonical Phase-1.3 output.\n\n"
        "## Per-test-point sign verdicts\n\n"
        "Not evaluated — pipeline halted at MC budget gate before sign\n"
        "certification. Re-run after Phase-2 N_draws bump.\n"
    )
    sidecar.write_text(body, encoding="utf-8")
    return sidecar


def main() -> int:
    """Run the COHORT-4 emission pipeline; return process exit code."""
    print("=" * 72)
    print("SAAS-COHORT-4 Z-cap emission — CLOSE plan v0.2 Phase 1.3")
    print(f"  MC_DRAWS_FLOOR             = {MC_DRAWS_FLOOR}")
    print(f"  MC_STDERR_RATIO_CEILING    = {MC_STDERR_RATIO_CEILING:.6e}")
    print(f"  repo_root                  = {REPO_ROOT}")
    print(f"  emit_dir                   = {EMIT_DIR}")
    print("=" * 72)

    # 1. Verify upstream artifacts.
    print("\n[1/5] Verifying Pin-M4 audit-block inputs...")
    present, missing = _verify_upstream_artifacts()
    for p in present:
        print(f"       OK  {p.relative_to(REPO_ROOT)}")
    for p in missing:
        print(f"       MISSING  {p.relative_to(REPO_ROOT)}")
    if missing:
        print(
            "\n       HALT — required audit-block input(s) missing."
            " AuditBlockResolver would raise FileNotFoundError."
        )
        return 4

    # 2. Load C1 q_t_cop draws.
    print("\n[2/5] Loading C1 q_t_cop posterior-predictive draws...")
    t0 = time.time()
    q_t_cop = _load_q_t_cop_draws()
    print(f"       OK — loaded {q_t_cop.size} draws in {time.time()-t0:.1f}s")
    cv_real = float(q_t_cop.std(ddof=1) / q_t_cop.mean())
    expected_ratio = cv_real / float(np.sqrt(MC_DRAWS_FLOOR))
    print(f"       Empirical CV(q_t_cop) = {cv_real:.6f}")
    print(
        f"       Expected stderr/Ẑ at N={MC_DRAWS_FLOOR}: {expected_ratio:.6e}"
        f"  (ceiling = {MC_STDERR_RATIO_CEILING:.6e})"
    )
    if expected_ratio > MC_STDERR_RATIO_CEILING:
        print(
            f"       PRE-FLIGHT WARN — expected MC budget breach by"
            f" {expected_ratio / MC_STDERR_RATIO_CEILING:.2f}×."
            " HALT is the expected Phase-1.3 outcome."
        )

    # 3. Build the canonical 5-TP grid.
    print("\n[3/5] Building Pin-M2 5-test-point grid...")
    grid = make_default_test_point_grid()
    for tp in grid:
        print(
            f"       {tp.label}: κ={tp.kappa:.3e}  X̄/Ȳ={tp.x_over_y_bar:.1f}"
            f"  σ₀={tp.sigma_0:.3e}"
        )

    # 4. Pre-resolve audit block (so we can emit the HALT sidecar with it).
    print("\n[4/5] Pre-resolving audit-block sha256 (Pin M4)...")
    resolver = AuditBlockResolver(repo_root=REPO_ROOT)
    audit_block = resolver()
    print(f"       sha256 = {audit_block}")

    # 5. Drive pin_and_emit with full available draws (Phase 2 path α).
    from simulations.saas_builder.cohort_4.types import MCBudget
    from simulations.saas_builder.cohort_4.z_cap import ZCapRunner
    n_avail = int(q_t_cop.size)
    runner = ZCapRunner(mc_budget=MCBudget(n_draws=n_avail))
    print(
        f"\n[5/5] Driving pin_and_emit (5-TP × {n_avail} draws,"
        f" full C1 v0.4 panel post-Phase-2)..."
    )
    t_start = time.time()
    try:
        json_path, sidecar_path, z_cap, sign_verdicts = pin_and_emit(
            q_t_cop_draws=q_t_cop,
            test_points=grid,
            repo_root=REPO_ROOT,
            emit_dir=EMIT_DIR,
            runner=runner,
        )
    except MCErrorBudgetExceededError as e:
        elapsed = time.time() - t_start
        print(
            f"\n       HALT (expected) — MCErrorBudgetExceededError after"
            f" {elapsed:.1f}s"
        )
        print(f"       reason: {e}")
        sidecar = _emit_halt_sidecar(
            audit_block=audit_block,
            halt_reason=str(e),
            halt_class="MCErrorBudgetExceededError",
            cv_real=cv_real,
            n_draws_used=int(q_t_cop.size),
            expected_stderr_ratio=expected_ratio,
        )
        print("\n" + "=" * 72)
        print("EMISSION SUMMARY — PHASE-1.3 HALT (deferred to Phase 2)")
        print("=" * 72)
        print("  HALT class               : MCErrorBudgetExceededError")
        print(f"  audit_block sha256       : {audit_block}")
        print(f"  empirical CV(q_t_cop)    : {cv_real:.6f}")
        print(f"  expected stderr/Ẑ        : {expected_ratio:.6e}")
        print(f"  ceiling                  : {MC_STDERR_RATIO_CEILING:.6e}")
        print(
            f"  breach factor            :"
            f" {expected_ratio / MC_STDERR_RATIO_CEILING:.2f}×"
        )
        print(f"  sidecar emitted          : {sidecar}")
        print("  Z_cap_pinned.json        : NOT emitted (HALT pre-emission)")
        print("  resolution               : CLOSE plan v0.2 Phase 2 path α —")
        print("                             N_draws bump to ~7.1e5 (4×178k).")
        print("=" * 72)
        return 3
    except (DiagnosticGateError, IdentityToleranceError) as e:
        print(f"\n       HALT — {type(e).__name__}: {e}")
        traceback.print_exc()
        return 2

    elapsed = time.time() - t_start
    print(f"       OK — pin_and_emit completed in {elapsed:.1f}s")

    # ─── PASS-path summary ──────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("EMISSION SUMMARY — PHASE-1.3 PASS")
    print("=" * 72)
    print(f"  Z_cop_per_month          : {z_cap.Z_cop_per_month:.6f}")
    print(f"  ci_95                    : [{z_cap.ci_95_lo:.6f}, {z_cap.ci_95_hi:.6f}]")
    print(f"  audit_block sha256       : {z_cap.audit_block}")
    print(f"  schema_version           : {z_cap.schema_version}")
    print(f"  json_path                : {json_path}")
    print(f"  sidecar_path             : {sidecar_path}")
    print(f"  empirical CV(q_t_cop)    : {cv_real:.6f}")
    print(f"  expected stderr/Ẑ        : {expected_ratio:.6e}")
    print()
    print("  Per-TP sign verdicts:")
    for sv in sign_verdicts:
        marker = "PASS" if sv.passes else "FAIL"
        print(
            f"    {sv.label}  z={sv.z_value:.6e}  ci=[{sv.ci_95_lo:.6e},"
            f" {sv.ci_95_hi:.6e}]  sign={marker}"
            f"  identity_residual={sv.identity_residual:.3e}"
        )
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
