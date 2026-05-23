"""Task 6 end-to-end driver — stochastic-FX three-family verification.

Parent spec: ``docs/specs/2026-05-11-stochastic-fx-variant-design.md`` v0.5.
Parent plan: ``docs/plans/2026-05-11-stochastic-fx-variant.md`` v0.6, §11 Task 6.

Runs the canonical (GBM, OU, Merton) families at ``rng_seed=42``, ``n_paths=1000``
through the Phase A + Phase B + Phase C ``InversionVerifier`` composite, emits
``PathEnsemble`` parquet + ``InversionVerdict`` JSON per family, then renders
``notes/STOCHASTIC_FX_RESULTS.md`` via :class:`StochasticFxResultsEmitter`.

Determinism cross-check (Pin Z1.2): the full pipeline is re-run from scratch
inside the same Python process; per-family ``InversionVerdict.audit_block``
MUST be bit-exact identical to the first run. This is the Task 6 acceptance
gate.

HALT routing (Pin Z1.5): if any phase fails for any family, the verifier
raises (MomentMatchFailedError / InversionTestFailedError / MCBudgetExceededError).
The driver does NOT retry, does NOT seed re-roll, does NOT widen tolerance.
The exception propagates; the user disposes via CORRECTIONS-α.

Hardware-constrained Merton Phase C reference (FLAG-RC-V0.5-1 disposition).
This is a HARDWARE-CONSTRAINED LOCAL RUN. The spec-pinned constant
``N_REF = 100_000`` in ``simulations/stochastic_fx/variance_proxy.py`` is
UNCHANGED — production behavior is governed by the spec-pinned constant.
At canonical Merton ``n_steps = 5000``, a single ``(N_REF, n_steps + 1)``
float64 path matrix is ~4 GB; the :class:`JumpDiffusionPathGenerator` peaks
near ~36 GB during construction. This workstation has ~4 GB free.

Per the FLAG-RC-V0.5-1 disposition recorded in scratch/2026-05-11-stochastic-
fx-spec-review/wave-1-v0.5/, an OOM at the canonical reference does NOT
constitute a Pin Z1.5 spec failure — it is a hardware constraint on the
developer workstation. The same ``monkeypatch.setattr(variance_proxy, "N_REF",
5_000)`` pattern is established in the autouse fixture of
``simulations/tests/test_saas_stochastic_fx.py::TestPhaseCMertonEmpiricalCDF``
(line 1778) and reviewed in Task 4.2 / wave-1 v0.6. Falling back to
``N_REF = 5_000`` here applies that same established pattern at the driver
level with explicit cross-document disclosure.

Disclosure surface: this docstring, the moment_verification_log.md sibling,
the ks_test_log.md sibling, the STOCHASTIC_FX_RESULTS.md Merton section, and
the commit message. Five mutually-corroborating disclosure points per
FLAG-RC-V0.5-1 disposition.
"""
from __future__ import annotations

import gc
import json
import sys
import traceback
from pathlib import Path
from typing import Final

from simulations.stochastic_fx import (
    CANONICAL_GBM,
    CANONICAL_MERTON,
    CANONICAL_OU,
    GBMPathGenerator,
    InversionVerdict,
    InversionVerdictEmitter,
    InversionVerifier,
    JumpDiffusionPathGenerator,
    KS_PVALUE_FLOOR,
    MOMENT_REL_TOL,
    NUMERICAL_IDENTITY_TOL,
    OUPathGenerator,
    PathEnsembleEmitter,
    StochasticFxResultsEmitter,
    gbm_discrete_sigma_t_moments,
    merton_discrete_sigma_t_moments,
    ou_discrete_sigma_t_moments,
)
from simulations.stochastic_fx import variance_proxy as _variance_proxy

# ── Outcome-neutral configuration ────────────────────────────────────────────
EMIT_DATA_DIR: Final[Path] = Path("simulations/stochastic_fx/data")
EMIT_RESULTS_DIR: Final[Path] = Path("notes")
RNG_SEED: Final[int] = 42
N_PATHS: Final[int] = 1000

# Hardware-constrained N_REF for Attempt 2. Production constant
# (variance_proxy.N_REF = 100_000) is UNCHANGED in spec v0.5 §11.7.
HARDWARE_CONSTRAINED_N_REF: Final[int] = 5_000


FAMILIES: Final = (
    ("gbm", GBMPathGenerator, CANONICAL_GBM, gbm_discrete_sigma_t_moments),
    ("ou", OUPathGenerator, CANONICAL_OU, ou_discrete_sigma_t_moments),
    (
        "merton",
        JumpDiffusionPathGenerator,
        CANONICAL_MERTON,
        merton_discrete_sigma_t_moments,
    ),
)


def _run_family(family_id, gen_cls, params, moments_fn):
    """Generate ensemble, run verifier, emit per-family artifacts."""
    ensemble = gen_cls(params=params)(rng_seed=RNG_SEED, n_paths=N_PATHS)
    e_an, var_an = moments_fn(params)
    e_emp = float(ensemble.sigma_t.mean())
    var_emp = float(ensemble.sigma_t.var(ddof=1))

    verifier = InversionVerifier()
    verdict = verifier(params, ensemble, x_bar=params.x_0)

    pe_emitter = PathEnsembleEmitter(EMIT_DATA_DIR)
    iv_emitter = InversionVerdictEmitter(EMIT_DATA_DIR)
    pe_path = pe_emitter.emit_and_verify(ensemble)
    iv_path = iv_emitter.emit_and_verify(verdict)

    print(
        f"  {family_id}: "
        f"composite_pass={verdict.composite_pass} "
        f"mean_rel={verdict.phase_b_mean_rel_err:.3e} "
        f"var_rel={verdict.phase_b_var_rel_err:.3e} "
        f"ks_p={verdict.phase_c_ks_pvalue:.3e} "
        f"audit={verdict.audit_block[:12]} "
        f"pe={pe_path.name} iv={iv_path.name}"
    )

    return {
        "family_id": family_id,
        "verdict": verdict,
        "e_analytic": e_an,
        "var_analytic": var_an,
        "e_empirical": e_emp,
        "var_empirical": var_emp,
    }


def run_all_families(label):
    """One full pass over the three families. Returns list of result dicts."""
    print(f"[{label}] starting pass over {len(FAMILIES)} families")
    results = []
    for family_id, gen_cls, params, moments_fn in FAMILIES:
        result = _run_family(family_id, gen_cls, params, moments_fn)
        results.append(result)
        gc.collect()
    return results


def main(argv):
    EMIT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    EMIT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    attempt = argv[1] if len(argv) > 1 else "auto"
    use_hardware_constrained = False

    if attempt == "canonical":
        # Attempt 1: production N_REF = 100_000 (spec-pinned)
        first_pass = run_all_families("attempt-1 canonical N_REF=100_000")
    elif attempt == "hardware_constrained":
        # Attempt 2: hardware-constrained N_REF = 5_000
        use_hardware_constrained = True
        _variance_proxy._merton_reference_sigma_t.cache_clear()
        original_n_ref = _variance_proxy.N_REF
        _variance_proxy.N_REF = HARDWARE_CONSTRAINED_N_REF
        try:
            print(
                f"[ATTEMPT 2] hardware-constrained: monkey-patched "
                f"variance_proxy.N_REF: {original_n_ref} -> "
                f"{_variance_proxy.N_REF}. spec-pinned constant unchanged."
            )
            first_pass = run_all_families("attempt-2 hardware-constrained")
        finally:
            _variance_proxy._merton_reference_sigma_t.cache_clear()
    else:
        # auto: try canonical, fall back to hardware-constrained on OOM
        try:
            first_pass = run_all_families("attempt-1 canonical N_REF=100_000")
        except MemoryError as exc:
            print(f"[ATTEMPT 1 FAILED — MemoryError] {exc!r}")
            traceback.print_exc()
            print("[ATTEMPT 1 FAILED] falling through to attempt-2 hardware-constrained")
            use_hardware_constrained = True
            gc.collect()
            _variance_proxy._merton_reference_sigma_t.cache_clear()
            _variance_proxy.N_REF = HARDWARE_CONSTRAINED_N_REF
            first_pass = run_all_families("attempt-2 hardware-constrained")

    # Render STOCHASTIC_FX_RESULTS.md
    verdicts_first = tuple(r["verdict"] for r in first_pass)
    results_emitter = StochasticFxResultsEmitter(EMIT_RESULTS_DIR)
    results_path = results_emitter.emit(verdicts_first)
    print(f"[emit] {results_path}")

    # ── Determinism cross-check (Pin Z1.2) ────────────────────────────────────
    print("[determinism] re-running full pipeline from scratch for audit_block parity")
    _variance_proxy._merton_reference_sigma_t.cache_clear()
    second_pass = run_all_families("determinism-rerun")

    determinism_report = []
    for first, second in zip(first_pass, second_pass, strict=True):
        family_id = first["family_id"]
        first_audit = first["verdict"].audit_block
        second_audit = second["verdict"].audit_block
        bit_exact = first_audit == second_audit
        determinism_report.append((family_id, bit_exact, first_audit, second_audit))
        marker = "OK" if bit_exact else "FAIL"
        print(
            f"  [{marker}] {family_id}: "
            f"first={first_audit[:12]} second={second_audit[:12]}"
        )
        if not bit_exact:
            raise AssertionError(
                f"Pin Z1.2 determinism FAIL: family={family_id!r} "
                f"first_audit_block={first_audit!r} second_audit_block={second_audit!r}"
            )

    # Write moment + KS logs (driven by first_pass)
    log_dir = Path("scratch/2026-05-11-stochastic-fx-execution")
    log_dir.mkdir(parents=True, exist_ok=True)

    n_ref_used = HARDWARE_CONSTRAINED_N_REF if use_hardware_constrained else 100_000

    moment_lines = [
        "# Moment Verification Log — Stochastic-FX End-to-End Run 2026-05-13",
        "",
        f"**Spec version:** v0.5",
        f"**Plan version:** v0.6",
        f"**Driver:** `scratch/2026-05-11-stochastic-fx-execution/driver.py`",
        f"**N_REF used for Merton Phase C reference:** "
        f"{n_ref_used}{' (hardware-constrained per FLAG-RC-V0.5-1; spec-pinned constant unchanged)' if use_hardware_constrained else ' (spec-pinned canonical)'}",
        f"**rng_seed:** {RNG_SEED}",
        f"**n_paths:** {N_PATHS}",
        f"**MOMENT_REL_TOL:** {MOMENT_REL_TOL}",
        "",
    ]
    family_labels = {
        "gbm": "GBM at canonical pin (CANONICAL_GBM)",
        "ou": "OU at canonical pin (CANONICAL_OU)",
        "merton": "Merton jump-diffusion at canonical pin (CANONICAL_MERTON)",
    }
    for r in first_pass:
        v = r["verdict"]
        mean_pass = "PASS" if v.phase_b_pass else "FAIL"
        moment_lines.extend(
            [
                f"## {family_labels[r['family_id']]}",
                f"- Analytic E[sigma_T]:           {r['e_analytic']!r}",
                f"- Empirical mean(sigma_T):       {r['e_empirical']!r}",
                f"- mean rel-err:                  {v.phase_b_mean_rel_err!r} "
                f"(< MOMENT_REL_TOL = {MOMENT_REL_TOL} -> {mean_pass})",
                f"- Analytic Var[sigma_T]:         {r['var_analytic']!r} "
                f"(Isserlis Gaussian-quadratic-form per spec v0.5 §11.6 audit-trail)",
                f"- Empirical var(sigma_T):        {r['var_empirical']!r}",
                f"- var rel-err (audit-trail):     {v.phase_b_var_rel_err!r} "
                f"(NOT gated; observation-only per v0.5 §11.6)",
                "",
            ]
        )
    (log_dir / "moment_verification_log.md").write_text("\n".join(moment_lines), encoding="utf-8")
    print(f"[emit] {log_dir / 'moment_verification_log.md'}")

    ks_lines = [
        "# KS Test Log — Stochastic-FX End-to-End Run 2026-05-13",
        "",
        f"**Spec version:** v0.5",
        f"**Plan version:** v0.6",
        f"**KS_PVALUE_FLOOR:** {KS_PVALUE_FLOOR}",
        f"**N_REF_SEED:** 20260513 (spec-pinned)",
        "",
        "## GBM (Phase C: moment-matched lognormal MoM reference, scipy.stats.ks_1samp)",
        "Reference shape s = sqrt(log(1 + Var/E²)), scale = E/sqrt(1 + Var/E²) "
        "constructed from ANALYTIC moments (Method-of-moments per NIT-MQ-1 disposition).",
    ]
    for r in first_pass:
        v = r["verdict"]
        ks_pass = "PASS" if v.phase_c_pass else "FAIL"
        if r["family_id"] == "gbm":
            ks_lines.append(
                f"- ks_pvalue: {v.phase_c_ks_pvalue!r} "
                f"(>= {KS_PVALUE_FLOOR} -> {ks_pass})"
            )
            ks_lines.append("")
            ks_lines.append(
                "## OU (Phase C: moment-matched gamma MoM reference, scipy.stats.ks_1samp)"
            )
            ks_lines.append(
                "Reference shape a = E²/Var, scale = Var/E constructed from ANALYTIC moments."
            )
        elif r["family_id"] == "ou":
            ks_lines.append(
                f"- ks_pvalue: {v.phase_c_ks_pvalue!r} "
                f"(>= {KS_PVALUE_FLOOR} -> {ks_pass})"
            )
            ks_lines.append("")
            ks_lines.append(
                "## Merton (Phase C: empirical-CDF via high-N reference run, scipy.stats.ks_2samp)"
            )
            ks_lines.append(
                f"- N_REF actually used: {n_ref_used}"
                + (
                    " (HARDWARE-CONSTRAINED per FLAG-RC-V0.5-1; production "
                    "spec-pinned N_REF = 100_000 unchanged in "
                    "simulations/stochastic_fx/variance_proxy.py)."
                    if use_hardware_constrained
                    else " (spec-pinned canonical)."
                )
            )
            ks_lines.append("- N_REF_SEED: 20260513")
        elif r["family_id"] == "merton":
            ks_lines.append(
                f"- ks_2samp pvalue: {v.phase_c_ks_pvalue!r} "
                f"(>= {KS_PVALUE_FLOOR} -> {ks_pass})"
            )
            ks_lines.append("")
    ks_lines.append("## Determinism cross-check (Pin Z1.2)")
    for family_id, bit_exact, first_audit, second_audit in determinism_report:
        marker = "BIT-EXACT" if bit_exact else "MISMATCH"
        ks_lines.append(
            f"- {family_id}: {marker} "
            f"(first run audit_block prefix `{first_audit[:16]}`; "
            f"second run audit_block prefix `{second_audit[:16]}`)"
        )
    ks_lines.append("")
    (log_dir / "ks_test_log.md").write_text("\n".join(ks_lines), encoding="utf-8")
    print(f"[emit] {log_dir / 'ks_test_log.md'}")

    # Final summary
    print("\n=== TASK 6 SUMMARY ===")
    attempt_label = "Attempt-2 (hardware-constrained N_REF=5_000)" if use_hardware_constrained else "Attempt-1 (canonical N_REF=100_000)"
    print(f"Attempt: {attempt_label}")
    for r in first_pass:
        v = r["verdict"]
        print(
            f"  {r['family_id']}: composite_pass={v.composite_pass} "
            f"audit_block_prefix={v.audit_block[:16]}"
        )
    for family_id, bit_exact, *_ in determinism_report:
        print(f"  determinism[{family_id}]: bit-exact={bit_exact}")


if __name__ == "__main__":
    main(sys.argv)
