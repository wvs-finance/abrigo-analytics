"""SAAS-COHORT-3 test suite — Pin R1–R6 verification.

Covers Plan v0.2 Phase-2 + Phase-3 audit-pass scope:

- Pin R1: closed candidate set; ``CandidateSetClosedError`` on 4th form.
- Pin R1: prior validation for each of the three forms.
- Pin R2: ``LooComparator`` invokes ``arviz.compare`` with ``ic="loo"``.
- Pin R3: verdict-router PASS / MARGINAL / INDISTINGUISHABLE / WEAK / FAIL
  thresholds with closed-interval boundary semantics (RC-FLAG-2 fix).
- Pin R4: gate evaluation (r̂, ESS, Pareto-k̂ HIGH-frac, sim-count floor).
- Pin R4-bis: AR(1)-log boundary-mass routing — clean / WEAK / HALT
  (RhoBoundaryHaltError) with three-state coverage.
- Pin R5: IO round-trip — verdict JSON, idata NetCDF, audit-block sha.
- Pin R6: thresholds are Final module-level constants.

Anti-fishing: every threshold is pinned to a literal verbatim from
spec §5–§9 and tested at the boundary value. Drift is a Phase-4 BLOCK.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from unittest.mock import patch

import arviz as az
import hypothesis.strategies as st
import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from xarray import DataArray, Dataset

from simulations.saas_builder.cohort_3._errors import (
    CandidateSetClosedError,
    LfoCvUnavailableError,
    RhoBoundaryHaltError,
    SchemaMismatchError,
)
from simulations.saas_builder.cohort_3.io import (
    InferenceDataPersister,
    VerdictArtifactWriter,
    compute_audit_block,
)
from simulations.saas_builder.cohort_3.loo import (
    INDISTINGUISHABLE_RATIO_MAX,
    PASS_RATIO_MIN,
    LooComparator,
    VerdictRouter,
    _classify_ratio,
)
from simulations.saas_builder.cohort_3.models import (
    CHAIN_FLOOR,
    DRAWS_PER_CHAIN_FLOOR,
    Ar1LogModelBuilder,
    DetChurnModelBuilder,
    FitDriver,
    MartingaleModelBuilder,
    compute_rho_boundary_mass,
    evaluate_gates,
    get_builder_class,
    register_form,
)
from simulations.saas_builder.cohort_3.priors import (
    Ar1LogPrior,
    DetChurnPrior,
    MartingalePrior,
)
from simulations.saas_builder.cohort_3.types import (
    REVENUE_FORM_NAMES,
    UPSILON_PANEL_MIN_MONTHS,
    Ar1LogParams,
    DetChurnParams,
    LooComparisonResult,
    MartingaleParams,
    RevenueFormFit,
    UpsilonPanel,
    VerdictRouting,
    is_known_form,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _make_panel(n_months: int = 36, n_sims: int = 1) -> UpsilonPanel:
    """Construct a synthetic UpsilonPanel of length n_months with n_sims sims."""
    rows = []
    rng = np.random.default_rng(20260508)
    for s_idx in range(n_sims):
        for m in range(n_months):
            value = float(1.0e6 * (1.05 ** m) * rng.uniform(0.95, 1.05))
            rows.append((m, f"sim_{s_idx}", value, "cohort_a"))
    return UpsilonPanel(
        month_index=np.array([r[0] for r in rows], dtype=np.int64),
        simulation_id=tuple(r[1] for r in rows),
        upsilon_cop=np.array([r[2] for r in rows], dtype=np.float64),
        cohort_id=tuple(r[3] for r in rows),
    )


def _synthetic_idata_for_arviz(
    elpd_loo_target: float = 0.0,
    n_obs: int = 30,
    seed: int = 0,
) -> az.InferenceData:
    """Construct an arviz InferenceData with hand-set log_likelihood values.

    The log_likelihood group's values are set so that LOO-CV elpd ≈
    ``elpd_loo_target`` (equal across observations).
    """
    rng = np.random.default_rng(seed)
    n_chains = 4
    n_draws = 1000
    # log_likelihood per observation: equal across draws ⇒ deterministic LOO.
    per_obs_ll = elpd_loo_target / max(n_obs, 1)
    ll = np.full((n_chains, n_draws, n_obs), per_obs_ll, dtype=np.float64) + \
        rng.normal(0, 1e-3, (n_chains, n_draws, n_obs))
    posterior = Dataset(
        {
            "theta": DataArray(
                rng.normal(size=(n_chains, n_draws)),
                dims=("chain", "draw"),
            ),
        }
    )
    log_likelihood = Dataset(
        {
            "obs": DataArray(
                ll,
                dims=("chain", "draw", "obs_dim"),
            ),
        }
    )
    return az.InferenceData(
        posterior=posterior, log_likelihood=log_likelihood
    )


def _zero_audit() -> str:
    return "0" * 64


# ─── R1: closed candidate-set ──────────────────────────────────────────────────


def test_r1_known_forms() -> None:
    assert REVENUE_FORM_NAMES == ("martingale", "ar1_log", "det_churn")
    for name in REVENUE_FORM_NAMES:
        assert is_known_form(name)
    assert not is_known_form("brownian_bridge")


def test_r1_get_builder_class_known() -> None:
    assert get_builder_class("martingale") is MartingaleModelBuilder
    assert get_builder_class("ar1_log") is Ar1LogModelBuilder
    assert get_builder_class("det_churn") is DetChurnModelBuilder


def test_r1_get_builder_class_4th_form_raises() -> None:
    with pytest.raises(CandidateSetClosedError, match="closed candidate set"):
        get_builder_class("brownian_bridge")


def test_r1_register_form_always_raises() -> None:
    """Pin R6: registry is closed; register_form ALWAYS raises."""
    with pytest.raises(CandidateSetClosedError, match="CLOSED"):
        register_form("brownian_bridge", MartingaleModelBuilder)


def test_r1_fit_driver_unknown_form_raises() -> None:
    panel = _make_panel()
    driver = FitDriver()
    with pytest.raises(CandidateSetClosedError):
        driver("not_a_form", panel, "/tmp/x.nc")  # type: ignore[arg-type]


# ─── R1: per-form param validation ────────────────────────────────────────────


def test_r1_martingale_params_validation() -> None:
    MartingaleParams(sigma_epsilon=1.0)
    with pytest.raises(ValueError):
        MartingaleParams(sigma_epsilon=-1.0)
    with pytest.raises(ValueError):
        MartingaleParams(sigma_epsilon=0.0)
    with pytest.raises(ValueError):
        MartingaleParams(sigma_epsilon=float("inf"))


def test_r1_ar1_params_stationarity() -> None:
    Ar1LogParams(rho=0.5, sigma_epsilon=0.1)
    Ar1LogParams(rho=-0.99, sigma_epsilon=0.1)
    with pytest.raises(ValueError, match="stationarity"):
        Ar1LogParams(rho=1.0, sigma_epsilon=0.1)
    with pytest.raises(ValueError, match="stationarity"):
        Ar1LogParams(rho=-1.0, sigma_epsilon=0.1)
    with pytest.raises(ValueError, match="stationarity"):
        Ar1LogParams(rho=1.5, sigma_epsilon=0.1)


def test_r1_det_churn_params_validation() -> None:
    DetChurnParams(upsilon_0=1.0, g=0.05, lam=0.05)
    with pytest.raises(ValueError):
        DetChurnParams(upsilon_0=0.0, g=0.05, lam=0.05)
    with pytest.raises(ValueError):
        DetChurnParams(upsilon_0=1.0, g=-0.6, lam=0.05)
    with pytest.raises(ValueError):
        DetChurnParams(upsilon_0=1.0, g=0.05, lam=0.0)
    with pytest.raises(ValueError):
        DetChurnParams(upsilon_0=1.0, g=0.05, lam=1.0)


def test_r1_priors_validation() -> None:
    MartingalePrior()
    Ar1LogPrior()
    DetChurnPrior()
    with pytest.raises(ValueError):
        MartingalePrior(sigma_epsilon_scale=-1.0)
    with pytest.raises(ValueError):
        Ar1LogPrior(rho_mu=2.0)
    with pytest.raises(ValueError):
        Ar1LogPrior(rho_sigma=0.0)
    with pytest.raises(ValueError):
        DetChurnPrior(lambda_beta_a=0.0)


# ─── R3: verdict-router boundary semantics (closed-interval discipline) ────────


def test_r3_classify_indistinguishable_band() -> None:
    """ratio ∈ [0, 2) → INDISTINGUISHABLE (strict <)."""
    assert _classify_ratio(0.0) == "INDISTINGUISHABLE"
    assert _classify_ratio(1.0) == "INDISTINGUISHABLE"
    assert _classify_ratio(1.999) == "INDISTINGUISHABLE"


def test_r3_classify_marginal_band_inclusive() -> None:
    """ratio ∈ [2, 4] → MARGINAL (closed both ends, RC-FLAG-2 fix)."""
    assert _classify_ratio(2.0) == "MARGINAL"
    assert _classify_ratio(3.0) == "MARGINAL"
    assert _classify_ratio(4.0) == "MARGINAL"


def test_r3_classify_pass_band() -> None:
    """ratio ∈ (4, ∞) → PASS (strict >)."""
    assert _classify_ratio(4.001) == "PASS"
    assert _classify_ratio(5.0) == "PASS"
    assert _classify_ratio(100.0) == "PASS"


def test_r3_classify_negative_raises() -> None:
    with pytest.raises(ValueError):
        _classify_ratio(-0.5)
    with pytest.raises(ValueError):
        _classify_ratio(float("nan"))


def test_r3_thresholds_are_final() -> None:
    """Pin R6: 2·SE / 4·SE thresholds pinned at module level."""
    assert INDISTINGUISHABLE_RATIO_MAX == 2.0
    assert PASS_RATIO_MIN == 4.0


@given(ratio=st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False))
def test_r3_classify_monotonicity(ratio: float) -> None:
    """Property: verdict is non-decreasing in ratio across the three bands."""
    label = _classify_ratio(ratio)
    if ratio < 2.0:
        assert label == "INDISTINGUISHABLE"
    elif ratio <= 4.0:
        assert label == "MARGINAL"
    else:
        assert label == "PASS"


# ─── R3 + R4: VerdictRouter end-to-end ─────────────────────────────────────────


def _fit(
    name: str,
    *,
    gates_passed: bool = True,
    pareto_k_max: float = 0.3,
    rho_boundary_mass: float | None = None,
) -> RevenueFormFit:
    if name == "ar1_log" and rho_boundary_mass is None:
        rho_boundary_mass = 0.0
    if name != "ar1_log":
        rho_boundary_mass = None
    return RevenueFormFit(
        form_name=name,  # type: ignore[arg-type]
        idata_path=f"/tmp/{name}.nc",
        rhat_max=1.005 if gates_passed else 1.50,
        ess_bulk_min=500.0 if gates_passed else 50.0,
        ess_tail_min=500.0 if gates_passed else 50.0,
        n_chains=4,
        n_draws_per_chain=4000,
        pareto_k_max=pareto_k_max,
        pareto_k_high_frac=0.0 if gates_passed else 0.5,
        gates_passed=gates_passed,
        rho_boundary_mass=rho_boundary_mass,
    )


def _comparison(
    forms: tuple[str, ...],
    elpd_loo: dict[str, float],
    dse: dict[str, float],
) -> LooComparisonResult:
    """Build a synthetic LooComparisonResult for verdict-router unit tests."""
    sorted_forms = tuple(sorted(forms, key=lambda f: -elpd_loo[f]))
    top = sorted_forms[0]
    elpd_diff = {top: 0.0}
    for f in sorted_forms[1:]:
        elpd_diff[f] = elpd_loo[top] - elpd_loo[f]
    n = len(sorted_forms)
    weight = {f: 1.0 / n for f in sorted_forms}
    se = {f: 1.0 for f in sorted_forms}
    warning = {f: False for f in sorted_forms}
    return LooComparisonResult(
        ranked_forms=sorted_forms,
        elpd_loo=elpd_loo,
        elpd_diff=elpd_diff,
        dse=dse,
        weight=weight,
        se=se,
        warning=warning,
    )


def test_r3_verdict_pass() -> None:
    """|Δ| = 5·SE → PASS."""
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -5.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    router = VerdictRouter()
    result = router(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "PASS"
    assert result.winning_form == "martingale"


def test_r3_verdict_marginal_at_3se() -> None:
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -3.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "MARGINAL"


def test_r3_verdict_marginal_at_2se_boundary() -> None:
    """RC-FLAG-2: ratio = 2.0 exactly → MARGINAL."""
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -2.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "MARGINAL"


def test_r3_verdict_marginal_at_4se_boundary() -> None:
    """RC-FLAG-2: ratio = 4.0 exactly → MARGINAL."""
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -4.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "MARGINAL"


def test_r3_verdict_indistinguishable_at_1se() -> None:
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -1.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "INDISTINGUISHABLE"
    # CORRECTIONS-α v0.3 §15.10 (CR-S5 / RC-FLAG-1): no winner declared
    # on INDISTINGUISHABLE — winning_form must be "" not the top form.
    assert result.winning_form == ""


def test_r3_verdict_indistinguishable_no_winning_form_marginal_has_one() -> None:
    """CORRECTIONS-α v0.3 §15.10: winning_form discipline by verdict band.

    PASS / WEAK / MARGINAL → winning_form = top.
    INDISTINGUISHABLE / FAIL → winning_form = "".
    """
    forms = ("martingale", "ar1_log", "det_churn")
    # MARGINAL case — winner declared.
    cmp_marg = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -3.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    res_marg = VerdictRouter()(cmp_marg, fits, audit_block=_zero_audit())
    assert res_marg.verdict == "MARGINAL"
    assert res_marg.winning_form == "martingale"
    # INDISTINGUISHABLE case — no winner.
    cmp_ind = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -1.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    res_ind = VerdictRouter()(cmp_ind, fits, audit_block=_zero_audit())
    assert res_ind.verdict == "INDISTINGUISHABLE"
    assert res_ind.winning_form == ""


def test_r3_verdict_fail_top_gates() -> None:
    """Pin R4: top form's gates_passed = False → FAIL."""
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -10.0, "det_churn": -20.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {
        "martingale": _fit("martingale", gates_passed=False),
        "ar1_log": _fit("ar1_log"),
        "det_churn": _fit("det_churn"),
    }
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "FAIL"
    assert result.winning_form == ""


def test_r3_verdict_weak_non_top_gates() -> None:
    """Pin R4: non-top form gate failure → WEAK."""
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -10.0, "det_churn": -20.0},
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    fits = {
        "martingale": _fit("martingale"),
        "ar1_log": _fit("ar1_log", gates_passed=False),
        "det_churn": _fit("det_churn"),
    }
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "WEAK"


# ─── R4-bis: AR(1)-log boundary-mass routing ───────────────────────────────────


def test_r4bis_clean_no_action() -> None:
    """P(|ρ|>0.95) ≤ 0.05 → no action; verdict band-driven."""
    forms = ("ar1_log", "martingale", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"ar1_log": 0.0, "martingale": -5.0, "det_churn": -10.0},
        dse={"ar1_log": 0.0, "martingale": 1.0, "det_churn": 1.0},
    )
    fits = {
        "ar1_log": _fit("ar1_log", rho_boundary_mass=0.02),
        "martingale": _fit("martingale"),
        "det_churn": _fit("det_churn"),
    }
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "PASS"
    assert result.winning_form == "ar1_log"


def test_r4bis_weak_top_ar1() -> None:
    """0.05 < P(|ρ|>0.95) ≤ 0.20 + AR(1) is top → downgrade to WEAK."""
    forms = ("ar1_log", "martingale", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"ar1_log": 0.0, "martingale": -5.0, "det_churn": -10.0},
        dse={"ar1_log": 0.0, "martingale": 1.0, "det_churn": 1.0},
    )
    fits = {
        "ar1_log": _fit("ar1_log", rho_boundary_mass=0.10),
        "martingale": _fit("martingale"),
        "det_churn": _fit("det_churn"),
    }
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "WEAK"


def test_r4bis_halt_on_severe_boundary_mass() -> None:
    """P(|ρ|>0.95) > 0.20 → RhoBoundaryHaltError."""
    forms = ("ar1_log", "martingale", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"ar1_log": 0.0, "martingale": -5.0, "det_churn": -10.0},
        dse={"ar1_log": 0.0, "martingale": 1.0, "det_churn": 1.0},
    )
    fits = {
        "ar1_log": _fit("ar1_log", rho_boundary_mass=0.30),
        "martingale": _fit("martingale"),
        "det_churn": _fit("det_churn"),
    }
    with pytest.raises(RhoBoundaryHaltError, match="exceeds Pin R4-bis"):
        VerdictRouter()(cmp, fits, audit_block=_zero_audit())


# ─── R4: gate evaluation ──────────────────────────────────────────────────────


def test_r4_gates_clean() -> None:
    assert evaluate_gates(
        rhat_max=1.005,
        ess_bulk_min=500.0,
        ess_tail_min=500.0,
        n_chains=4,
        n_draws_per_chain=4000,
        pareto_k_high_frac=0.0,
    )


def test_r4_gates_rhat_breach() -> None:
    assert not evaluate_gates(
        rhat_max=1.05,
        ess_bulk_min=500.0,
        ess_tail_min=500.0,
        n_chains=4,
        n_draws_per_chain=4000,
        pareto_k_high_frac=0.0,
    )


def test_r4_gates_ess_breach() -> None:
    assert not evaluate_gates(
        rhat_max=1.005,
        ess_bulk_min=100.0,
        ess_tail_min=500.0,
        n_chains=4,
        n_draws_per_chain=4000,
        pareto_k_high_frac=0.0,
    )


def test_r4_gates_chain_floor_breach() -> None:
    assert not evaluate_gates(
        rhat_max=1.005,
        ess_bulk_min=500.0,
        ess_tail_min=500.0,
        n_chains=2,
        n_draws_per_chain=4000,
        pareto_k_high_frac=0.0,
    )


def test_r4_gates_draws_floor_breach() -> None:
    assert not evaluate_gates(
        rhat_max=1.005,
        ess_bulk_min=500.0,
        ess_tail_min=500.0,
        n_chains=4,
        n_draws_per_chain=1000,
        pareto_k_high_frac=0.0,
    )


def test_r4_gates_pareto_k_breach() -> None:
    assert not evaluate_gates(
        rhat_max=1.005,
        ess_bulk_min=500.0,
        ess_tail_min=500.0,
        n_chains=4,
        n_draws_per_chain=4000,
        pareto_k_high_frac=0.10,
    )


# ─── R4-bis: compute_rho_boundary_mass ────────────────────────────────────────


def test_r4bis_rho_mass_zero_when_centered() -> None:
    rho_samples = np.zeros((4, 1000))
    posterior = Dataset(
        {"rho": DataArray(rho_samples, dims=("chain", "draw"))}
    )
    idata = az.InferenceData(posterior=posterior)
    assert compute_rho_boundary_mass(idata) == 0.0


def test_r4bis_rho_mass_one_when_extreme() -> None:
    rho_samples = np.full((4, 1000), 0.99)
    posterior = Dataset(
        {"rho": DataArray(rho_samples, dims=("chain", "draw"))}
    )
    idata = az.InferenceData(posterior=posterior)
    assert compute_rho_boundary_mass(idata) == 1.0


def test_r4bis_rho_mass_fraction() -> None:
    rho_samples = np.concatenate([
        np.full(2000, 0.99),
        np.full(2000, 0.10),
    ]).reshape(4, 1000)
    posterior = Dataset(
        {"rho": DataArray(rho_samples, dims=("chain", "draw"))}
    )
    idata = az.InferenceData(posterior=posterior)
    mass = compute_rho_boundary_mass(idata)
    assert math.isclose(mass, 0.5, abs_tol=0.01)


# ─── R5: UpsilonPanel validation ──────────────────────────────────────────────


def test_r5_panel_min_months_floor() -> None:
    """Pin R5: at least one trajectory must have ≥ 24 months."""
    with pytest.raises(ValueError, match="months"):
        _make_panel(n_months=10, n_sims=1)


def test_r5_panel_positive_upsilon() -> None:
    months = np.arange(30, dtype=np.int64)
    upsilon = np.full(30, 1.0e6)
    upsilon[0] = -1.0  # break the positivity invariant
    with pytest.raises(ValueError, match="positive"):
        UpsilonPanel(
            month_index=months,
            simulation_id=tuple([f"sim_{i}" for i in range(30)]),
            upsilon_cop=upsilon,
            cohort_id=tuple(["cohort_a"] * 30),
        )


def test_r5_panel_minimum_24_months_exact() -> None:
    """Boundary: exactly 24 months is admissible."""
    panel = _make_panel(n_months=UPSILON_PANEL_MIN_MONTHS, n_sims=1)
    assert panel.month_index.shape[0] == UPSILON_PANEL_MIN_MONTHS


# ─── R5: IO round-trip ────────────────────────────────────────────────────────


def test_r5_verdict_json_roundtrip(tmp_path: Path) -> None:
    verdict = VerdictRouting(
        verdict="PASS",
        winning_form="martingale",
        delta_elpd_loo=5.0,
        se=1.0,
        pareto_k_max_per_form={"martingale": 0.3, "ar1_log": 0.4, "det_churn": 0.5},
        weights_per_form={"martingale": 0.6, "ar1_log": 0.3, "det_churn": 0.1},
        audit_block=_zero_audit(),
        fetched_at_utc="2026-05-08T00:00:00Z",
    )
    writer = VerdictArtifactWriter(tmp_path)
    path = writer.write(verdict)
    assert path.exists()
    loaded = writer.read()
    assert loaded == verdict


def test_r5_verdict_json_schema_drift_raises(tmp_path: Path) -> None:
    """Pin R5: missing/extra JSON keys raise SchemaMismatchError."""
    bad_path = tmp_path / "cohort_3_verdict.json"
    bad_path.write_text(json.dumps({"verdict": "PASS"}))
    writer = VerdictArtifactWriter(tmp_path)
    with pytest.raises(SchemaMismatchError, match="schema drift"):
        writer.read()


def test_r5_idata_netcdf_roundtrip(tmp_path: Path) -> None:
    idata = _synthetic_idata_for_arviz(elpd_loo_target=10.0, n_obs=10)
    persister = InferenceDataPersister(tmp_path)
    p = persister.write("martingale", idata)
    assert p.exists()
    loaded = persister.read("martingale")
    # Round-trip preserves log_likelihood group.
    assert "log_likelihood" in loaded.groups()


def test_r5_audit_block_deterministic() -> None:
    h1 = compute_audit_block(
        "data/upsilon_panel.parquet",
        "2026-05-08T00:00:00Z",
        {
            "martingale": "estimates/cohort_3_idata_martingale.nc",
            "ar1_log": "estimates/cohort_3_idata_ar1_log.nc",
            "det_churn": "estimates/cohort_3_idata_det_churn.nc",
        },
    )
    h2 = compute_audit_block(
        "data/upsilon_panel.parquet",
        "2026-05-08T00:00:00Z",
        {
            "martingale": "estimates/cohort_3_idata_martingale.nc",
            "ar1_log": "estimates/cohort_3_idata_ar1_log.nc",
            "det_churn": "estimates/cohort_3_idata_det_churn.nc",
        },
    )
    assert h1 == h2
    # Per Pin R5: 64 lowercase hex chars.
    assert len(h1) == 64
    assert all(c in "0123456789abcdef" for c in h1)


def test_r5_audit_block_invariant_under_dict_insertion_order() -> None:
    """CR N6 v0.3 sweep: compute_audit_block sorts idata_paths keys.

    Two ``Mapping`` inputs with the same items but different insertion
    order (Python 3.7+ dict preserves insertion order) must yield the
    same digest. Pins the ``sorted(idata_paths)`` reduction in
    ``cohort_3/io.py:compute_audit_block`` against silent regression to
    iteration-order-dependent hashing.
    """
    paths_order_a = {
        "martingale": "estimates/cohort_3_idata_martingale.nc",
        "ar1_log": "estimates/cohort_3_idata_ar1_log.nc",
        "det_churn": "estimates/cohort_3_idata_det_churn.nc",
    }
    paths_order_b = {
        "det_churn": "estimates/cohort_3_idata_det_churn.nc",
        "martingale": "estimates/cohort_3_idata_martingale.nc",
        "ar1_log": "estimates/cohort_3_idata_ar1_log.nc",
    }
    h_a = compute_audit_block(
        "data/upsilon_panel.parquet",
        "2026-05-08T00:00:00Z",
        paths_order_a,
    )
    h_b = compute_audit_block(
        "data/upsilon_panel.parquet",
        "2026-05-08T00:00:00Z",
        paths_order_b,
    )
    assert h_a == h_b


# ─── R2: arviz.compare integration via LooComparator ───────────────────────────


def test_r2_loo_comparator_invokes_arviz_compare() -> None:
    """Pin R2: LooComparator calls arviz.compare with ic='loo'."""
    idata_a = _synthetic_idata_for_arviz(elpd_loo_target=0.0, n_obs=20, seed=1)
    idata_b = _synthetic_idata_for_arviz(elpd_loo_target=-10.0, n_obs=20, seed=2)
    idata_c = _synthetic_idata_for_arviz(elpd_loo_target=-20.0, n_obs=20, seed=3)
    comparator = LooComparator()

    captured: dict[str, object] = {}
    real_compare = az.compare  # bind BEFORE patching

    def _spy_compare(*args: object, **kwargs: object) -> object:
        captured.update(kwargs)
        return real_compare(*args, **kwargs)

    with patch("simulations.saas_builder.cohort_3.loo.az.compare",
               side_effect=_spy_compare):
        result = comparator({
            "martingale": idata_a,
            "ar1_log": idata_b,
            "det_churn": idata_c,
        })

    assert captured.get("ic") == "loo"
    assert captured.get("method") == "stacking"
    assert isinstance(result, LooComparisonResult)
    assert "martingale" in result.ranked_forms


def test_r2_loo_comparator_reject_unknown_form() -> None:
    idata = _synthetic_idata_for_arviz()
    with pytest.raises(ValueError, match="closed set"):
        LooComparator()({"brownian": idata})


def test_r2_loo_comparator_reject_invalid_method() -> None:
    with pytest.raises(ValueError, match="method"):
        LooComparator(method="not_a_method")


# ─── Misc ──────────────────────────────────────────────────────────────────────


def test_fit_driver_validates_floors() -> None:
    """FitDriver enforces Pin R4 sim-count floors at construction."""
    with pytest.raises(ValueError, match="DRAWS_PER_CHAIN_FLOOR"):
        FitDriver(draws=1000)
    with pytest.raises(ValueError, match="CHAIN_FLOOR"):
        FitDriver(chains=2)
    with pytest.raises(ValueError, match="target_accept"):
        FitDriver(target_accept=1.5)
    # Accept at floor.
    FitDriver(draws=DRAWS_PER_CHAIN_FLOOR, chains=CHAIN_FLOOR)


def test_fit_driver_lfo_method_validation() -> None:
    """FitDriver only accepts 'loo' or 'lfo' for cv_method."""
    FitDriver(cv_method="loo")
    FitDriver(cv_method="lfo")
    with pytest.raises(ValueError, match="cv_method"):
        FitDriver(cv_method="cross_val")


def test_revenue_form_fit_ar1_requires_rho_mass() -> None:
    """Pin R4-bis: AR(1)-log fit MUST carry rho_boundary_mass; non-AR1 must NOT."""
    with pytest.raises(ValueError, match="ar1_log requires"):
        RevenueFormFit(
            form_name="ar1_log",
            idata_path="/tmp/x.nc",
            rhat_max=1.005,
            ess_bulk_min=500.0,
            ess_tail_min=500.0,
            n_chains=4,
            n_draws_per_chain=4000,
            pareto_k_max=0.3,
            pareto_k_high_frac=0.0,
            gates_passed=True,
            rho_boundary_mass=None,  # missing — should raise
        )
    with pytest.raises(ValueError, match="must be None"):
        RevenueFormFit(
            form_name="martingale",
            idata_path="/tmp/x.nc",
            rhat_max=1.005,
            ess_bulk_min=500.0,
            ess_tail_min=500.0,
            n_chains=4,
            n_draws_per_chain=4000,
            pareto_k_max=0.3,
            pareto_k_high_frac=0.0,
            gates_passed=True,
            rho_boundary_mass=0.10,  # set on non-AR1 — should raise
        )


def test_loo_comparison_result_weight_normalization() -> None:
    """LooComparisonResult enforces weight sum ≈ 1."""
    with pytest.raises(ValueError, match="weight sum"):
        LooComparisonResult(
            ranked_forms=("martingale", "ar1_log"),
            elpd_loo={"martingale": 0.0, "ar1_log": -5.0},
            elpd_diff={"martingale": 0.0, "ar1_log": 5.0},
            dse={"martingale": 0.0, "ar1_log": 1.0},
            weight={"martingale": 0.5, "ar1_log": 0.3},  # sum 0.8
            se={"martingale": 1.0, "ar1_log": 1.0},
            warning={"martingale": False, "ar1_log": False},
        )


def test_verdict_routing_audit_block_validation() -> None:
    """Pin R5: audit_block must be 64 lowercase hex chars."""
    with pytest.raises(ValueError, match="64 lowercase hex"):
        VerdictRouting(
            verdict="PASS",
            winning_form="martingale",
            delta_elpd_loo=5.0,
            se=1.0,
            pareto_k_max_per_form={},
            weights_per_form={},
            audit_block="not_a_sha",
            fetched_at_utc="2026-05-08T00:00:00Z",
        )


# ─── Model-builder smoke tests (no pm.sample) ────────────────────────────────


def test_martingale_builder_returns_pymc_model() -> None:
    import pymc as pm
    panel = _make_panel(n_months=30, n_sims=1)
    model = MartingaleModelBuilder()(panel)
    assert isinstance(model, pm.Model)
    var_names = {rv.name for rv in model.unobserved_RVs} | {
        rv.name for rv in model.observed_RVs
    }
    assert "sigma_epsilon" in var_names
    assert "obs" in var_names


def test_ar1_log_builder_returns_pymc_model() -> None:
    import pymc as pm
    panel = _make_panel(n_months=30, n_sims=1)
    model = Ar1LogModelBuilder()(panel)
    assert isinstance(model, pm.Model)
    var_names = {rv.name for rv in model.unobserved_RVs} | {
        rv.name for rv in model.observed_RVs
    }
    assert "rho" in var_names
    assert "sigma_epsilon" in var_names


def test_det_churn_builder_returns_pymc_model() -> None:
    import pymc as pm
    panel = _make_panel(n_months=30, n_sims=1)
    model = DetChurnModelBuilder()(panel)
    assert isinstance(model, pm.Model)
    var_names = {rv.name for rv in model.unobserved_RVs} | {
        rv.name for rv in model.observed_RVs
    }
    assert {"upsilon_0", "g", "lam", "sigma_obs"} <= var_names


def test_det_churn_builder_validates_sigma_obs_scale() -> None:
    with pytest.raises(ValueError, match="sigma_obs_scale"):
        DetChurnModelBuilder(sigma_obs_scale=-1.0)


def test_loo_comparator_full_pipeline() -> None:
    """End-to-end LooComparator → VerdictRouter on synthetic InferenceData.

    Pin R2 + R3 integration: arviz.compare runs without mock; verdict-router
    classifies the resulting elpd_diff/dse ratio.
    """
    idata_a = _synthetic_idata_for_arviz(elpd_loo_target=0.0, n_obs=20, seed=1)
    idata_b = _synthetic_idata_for_arviz(elpd_loo_target=-50.0, n_obs=20, seed=2)
    idata_c = _synthetic_idata_for_arviz(elpd_loo_target=-100.0, n_obs=20, seed=3)
    cmp = LooComparator()({
        "martingale": idata_a,
        "ar1_log": idata_b,
        "det_churn": idata_c,
    })
    fits = {
        "martingale": _fit("martingale"),
        "ar1_log": _fit("ar1_log"),
        "det_churn": _fit("det_churn"),
    }
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    # CR N5 v0.3 sweep: tighten membership to a frozenset literal (Pin R3
    # closed verdict alphabet); avoids the variadic-tuple membership lookup
    # and matches the static type of ``VerdictLabel``.
    assert result.verdict in frozenset(
        {"PASS", "MARGINAL", "INDISTINGUISHABLE", "WEAK", "FAIL"}
    )
    assert cmp.ranked_forms[0] == "martingale"


# ─── Hypothesis property: rank-name covariance ────────────────────────────────


# ─── CORRECTIONS-α v0.3 §15.9 (CR-S1): dse=0 boundary disambiguation ─────────


def test_r3_dse_zero_with_zero_delta_is_indistinguishable() -> None:
    """CR-S1: se == 0 ∧ |Δelpd| == 0 → ratio = 0 → INDISTINGUISHABLE.

    Legitimate ties under stacking should NOT short-circuit to PASS via
    inf-ratio.
    """
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": 0.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 0.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    result = VerdictRouter()(cmp, fits, audit_block=_zero_audit())
    assert result.verdict == "INDISTINGUISHABLE"
    assert result.winning_form == ""
    assert result.delta_elpd_loo == 0.0
    assert result.se == 0.0


def test_r3_dse_zero_with_nonzero_delta_raises() -> None:
    """CR-S1: se == 0 ∧ |Δelpd| != 0 is degenerate; refuse to classify."""
    forms = ("martingale", "ar1_log", "det_churn")
    cmp = _comparison(
        forms,
        elpd_loo={"martingale": 0.0, "ar1_log": -5.0, "det_churn": -10.0},
        dse={"martingale": 0.0, "ar1_log": 0.0, "det_churn": 1.0},
    )
    fits = {n: _fit(n) for n in forms}
    with pytest.raises(ValueError, match="degenerate"):
        VerdictRouter()(cmp, fits, audit_block=_zero_audit())


# ─── CORRECTIONS-α v0.3 §15.7 (CR-S3 / MQ-FLAG-3 / RC-FLAG-3): LFO HALTs ─────


def test_fit_driver_lfo_request_raises_unconditionally() -> None:
    """CR-S3: cv_method='lfo' must raise LfoCvUnavailableError, not relabel.

    The previous fall-through tagged ``cv_method='lfo'`` while emitting
    PSIS-LOO output. CORRECTIONS-α v0.3 §15.7 requires unconditional HALT
    so consumers cannot be misled about cross-validation provenance.
    """
    panel = _make_panel(n_months=30, n_sims=1)
    driver = FitDriver(cv_method="lfo")
    with pytest.raises(LfoCvUnavailableError, match="LFO"):
        driver("martingale", panel, "/tmp/x.nc")


# ─── CORRECTIONS-α v0.3 §15.8 (CR-S4 / MQ-FLAG-1): multi-traj warning ────────


def test_first_trajectory_warns_on_multi_sim_panel() -> None:
    """CR-S4: panels with N>1 (cohort, sim) trajectories trigger a
    UserWarning surfacing the Stage-2 single-trajectory limitation.
    """
    import warnings as _warnings
    from simulations.saas_builder.cohort_3.models import _first_trajectory

    panel = _make_panel(n_months=30, n_sims=3)
    with _warnings.catch_warnings(record=True) as caught:
        _warnings.simplefilter("always")
        out = _first_trajectory(panel)
        relevant = [w for w in caught if "Stage-2" in str(w.message)]
        assert len(relevant) == 1
        assert "discards" in str(relevant[0].message)
    # Returns a 1-D array of the FIRST trajectory only.
    assert out.ndim == 1
    assert out.shape[0] == 30


def test_first_trajectory_no_warn_on_single_sim_panel() -> None:
    """CR-S4: single-trajectory panel (the canonical Stage-2 path) emits
    no Stage-2 limitation warning.
    """
    import warnings as _warnings
    from simulations.saas_builder.cohort_3.models import _first_trajectory

    panel = _make_panel(n_months=30, n_sims=1)
    with _warnings.catch_warnings(record=True) as caught:
        _warnings.simplefilter("always")
        _first_trajectory(panel)
        relevant = [w for w in caught if "Stage-2" in str(w.message)]
        assert len(relevant) == 0


@given(
    elpd_a=st.floats(min_value=-100.0, max_value=0.0, allow_nan=False),
    elpd_b=st.floats(min_value=-100.0, max_value=0.0, allow_nan=False),
    elpd_c=st.floats(min_value=-100.0, max_value=0.0, allow_nan=False),
)
@settings(max_examples=20, deadline=None,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_rank_permutation_invariance(
    elpd_a: float, elpd_b: float, elpd_c: float
) -> None:
    """Property: top form is the one with max elpd_loo regardless of input order.

    This pins LOO-comparator's rank ordering on hand-crafted synthetic
    LooComparisonResult Values without re-running arviz.
    """
    elpds = {"martingale": elpd_a, "ar1_log": elpd_b, "det_churn": elpd_c}
    expected_top = max(elpds, key=lambda k: elpds[k])
    cmp = _comparison(
        forms=("martingale", "ar1_log", "det_churn"),
        elpd_loo=elpds,
        dse={"martingale": 0.0, "ar1_log": 1.0, "det_churn": 1.0},
    )
    assert cmp.ranked_forms[0] == expected_top
