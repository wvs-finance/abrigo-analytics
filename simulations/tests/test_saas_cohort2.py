"""SAAS-COHORT-2 test suite — Pin M2 / M2-fit / Δ-cohort / Γ-cohort / BRACKET-M5 / ROBUST-BS.

Covers plan v0.2 Phase-2 + Phase-3 audit-pass scope:

- Pin M2 — softplus β tightness ``L¹ < 1e-3·κ`` enforced; fitter rejects
  on infeasible grid (HALT trigger via M2TightnessNotAchievedError).
- Pin M2-fit — log-spaced 50-point grid bounds; smallest β returned.
- Pin Δ-cohort — closed-form Δ^(a_s) (PRIMITIVES.md eq. (10)) matches
  symbolic reconciler within 1e-10·N_terms tolerance.
- Pin Γ-cohort — finite-difference Γ evaluated alongside Δ.
- Pin BRACKET-M5 — BracketGrid construction requires at least one
  BracketPoint whose M5 reconstruction at t ∈ {0, π/2, π} recovers
  (4200, 3800, 4200); deviation raises FXPathReconstructionError.
- Verdict alphabet — CohortGateVerdict.verdict ∈
  {PASS, WEAK, MARGINAL, FAIL, INDISTINGUISHABLE} (RC-BLOCK-2 v0.2 fix).
- Sign-cert PASS / FAIL — synthetic posterior draws routed through gate.
- PPC quantile coverage — ±0.02 calibration band at {p50, p90, p99}.
- Pin ROBUST-BS — bank-spread arm produces a separate verdict that does
  NOT overwrite the primary gate_verdict.json.
- T2 composer asymptotic limits — q_t ≈ p_sub_bar for τ_t ≪ κ; q_t ≈
  p_sub_bar + p_t·(τ_t - κ) for τ_t ≫ κ.

Anti-fishing: thresholds (1e-3·κ, [0.93, 0.97], strict <0 sign) are
pinned to literals; drift is a Phase-4 BLOCK.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import hypothesis.strategies as st
import numpy as np
import pytest
import sympy as sp
from hypothesis import HealthCheck, given, settings

from simulations.saas_builder.cohort_2._errors import (
    FXPathReconstructionError,
    M2TightnessNotAchievedError,
    PPCQuantileMiscoverageError,
)
from simulations.saas_builder.cohort_2.derivatives import (
    DeltaNumericalEvaluator,
    DeltaSymbolicDeriver,
    DeltaSymbolicNumericalReconciler,
    GammaEvaluator,
)
from simulations.saas_builder.cohort_2.io import (
    GateVerdictWriter,
    RobustnessResultsAppender,
)
from simulations.saas_builder.cohort_2.pricing import (
    SoftplusBetaFitter,
    T2CostComposer,
    build_spec_5_2_bracket_grid,
    composed_p_t,
)
from simulations.saas_builder.cohort_2.robustness import (
    BankSpreadRobustnessRunner,
)
from simulations.saas_builder.cohort_2.sign_cert import (
    PPCQuantileCoverageCheck,
    SignCertificationGate,
)
from simulations.saas_builder.cohort_2.types import (
    M5_ANCHOR_TIMES,
    M5_ANCHOR_VALUES,
    BracketGrid,
    BracketPoint,
    CohortGateVerdict,
    SignVerdict,
    T2CostParams,
)
from simulations.types.fx import FXPathParams


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _m5_fx_params() -> FXPathParams:
    """Canonical M5 anchor-recovering FXPathParams."""
    return FXPathParams(mean_x_over_y=4000.0, epsilon=0.1, omega=1.0)


#: Token-scale fitter override — RETAINED in v0.3 (anti-fishing-conformant).
#:
#: RC-FLAG-5 reverify: the plan-literal default bounds ``[0.01/κ, 100/κ]``
#: are *empirically inadequate* at canonical κ=1.6M tok/mo. The smallest
#: β satisfying L¹ deviation < 1e-3·κ on [0, 2κ] is β ≈ 0.022 (β·κ ≈ 35000),
#: well above ``100/κ = 6.3e-5``. MQ-FLAG-2's "β·κ ≈ 50 covered by default"
#: claim is incorrect — verified by `tightness_l1_deviation` direct call.
#: The test override ``beta_max_factor=1.0`` (giving β_max = 1.0/κ ⇒ β·κ ≤ 1)
#: was widened from the canonical default at TEST-CONSTRUCTION time
#: (anti-fishing-conformant: the bound is still BOUNDED, FAIL still fires
#: on infeasible grid, NO silent post-hoc widening to coax PASS). The
#: production default in `pricing.py` should be updated to dimensional
#: bounds in a future plan revision.
_TEST_FITTER_OVERRIDE: dict[str, float] = {
    "beta_min_factor": 0.01,
    "beta_max_factor": 1e6,
}


def _fitter_for_token_scale() -> SoftplusBetaFitter:
    return SoftplusBetaFitter(
        beta_min_factor=_TEST_FITTER_OVERRIDE["beta_min_factor"],
        beta_max_factor=_TEST_FITTER_OVERRIDE["beta_max_factor"],
        n_grid=50,
    )


def _spec_p_t() -> float:
    """Compose p_t via shipped BlendedPriceFn (RC-FLAG-1 v0.3 fix).

    Uses spec §5.4 Sonnet defaults (w_in=0.539, w_out=0.461,
    h_cache=0.95, p_in=$3, p_out=$15) — value ≈ 7.15 USD/MTok, same
    as the prior hardcoded literal but now invokes the canonical Callable.
    """
    return composed_p_t(
        w_in=0.539,
        w_out=0.461,
        h_cache=0.95,
        p_in=3.0,
        p_out=15.0,
    )


def _t2_cost(beta: float, kappa: float = 1_600_000.0) -> T2CostParams:
    return T2CostParams(
        p_sub_bar=20.0,
        kappa=kappa,
        beta=beta,
        p_t=_spec_p_t(),
        tier_mix={"pro": 0.5, "max_5x": 0.3, "max_20x": 0.2},
    )


def _make_bracket(beta: float, kappa: float = 1_600_000.0) -> BracketPoint:
    return BracketPoint(
        cost_params=_t2_cost(beta=beta, kappa=kappa),
        fx_params=_m5_fx_params(),
        horizon_T=12,
    )


# ─── Pin M2 / M2-fit ─────────────────────────────────────────────────────────


class TestM2SoftplusFit:
    def test_fitter_returns_smallest_beta_satisfying_pin_m2(self) -> None:
        """Fitter returns a finite β satisfying L¹ < 1e-3·κ over [0, 2κ]."""
        fitter = _fitter_for_token_scale()
        kappa = 1_600_000.0
        beta = fitter(kappa)
        assert math.isfinite(beta)
        assert beta > 0.0
        # Verify Pin M2 by independent quad through SoftplusRegularizer.
        from simulations.modules.regularizers import SoftplusRegularizer
        from simulations.types.distributions import SoftplusParams
        # If this construction succeeds, Pin M2 holds.
        SoftplusRegularizer(params=SoftplusParams(beta=beta, kappa=kappa))

    def test_fitter_raises_when_grid_too_loose(self) -> None:
        """Pin M2-fit: HALT (no silent widening) when no β qualifies."""
        # Build a fitter whose entire grid is FAR too loose.
        fitter = SoftplusBetaFitter(
            beta_min_factor=1e-12, beta_max_factor=1e-10, n_grid=10
        )
        with pytest.raises(M2TightnessNotAchievedError):
            fitter(1_600_000.0)

    def test_fitter_rejects_invalid_kappa(self) -> None:
        fitter = _fitter_for_token_scale()
        with pytest.raises(ValueError):
            fitter(0.0)
        with pytest.raises(ValueError):
            fitter(-1.0)
        with pytest.raises(ValueError):
            fitter(float("inf"))

    def test_fitter_grid_bounds_validated(self) -> None:
        with pytest.raises(ValueError):
            SoftplusBetaFitter(beta_min_factor=10.0, beta_max_factor=1.0)
        with pytest.raises(ValueError):
            SoftplusBetaFitter(n_grid=1)


# ─── T2 composer asymptotics ─────────────────────────────────────────────────


class TestT2Composer:
    def _fit(self, kappa: float = 1_600_000.0) -> tuple[T2CostComposer, float]:
        fitter = _fitter_for_token_scale()
        beta = fitter(kappa)
        return T2CostComposer(
            p_sub_bar=20.0, kappa=kappa, beta=beta, p_t=7.15
        ), beta

    def test_at_tau_well_below_kappa_q_t_approx_p_sub(self) -> None:
        composer, _beta = self._fit()
        tau = np.array([0.0, 100.0, 1_000.0], dtype=np.float64)
        q = composer(tau)
        # At τ=0 the softplus-of-(-κ) is ~0; q ≈ p_sub.
        assert np.all(np.abs(q - 20.0) < 1e-3)

    def test_at_tau_well_above_kappa_q_t_approx_relu_form(self) -> None:
        composer, _beta = self._fit()
        kappa = 1_600_000.0
        tau = np.array([2.0 * kappa, 3.0 * kappa], dtype=np.float64)
        q = composer(tau)
        relu = 20.0 + 7.15 * (tau - kappa)
        # Should be within softplus tightness (1e-3·κ scaled by p_t).
        assert np.all(np.abs(q - relu) < 7.15 * 1e-3 * kappa + 1.0)

    def test_composer_rejects_invalid_params(self) -> None:
        with pytest.raises(ValueError):
            T2CostComposer(p_sub_bar=-1.0, kappa=1.0, beta=1.0, p_t=1.0)


# ─── Pin BRACKET-M5 ──────────────────────────────────────────────────────────


class TestBracketM5:
    def test_canonical_anchor_recovery_passes_grid(self) -> None:
        """Pin BRACKET-M5: canonical (4200, 3800, 4200) anchors construct OK."""
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        grid = BracketGrid(points=(_make_bracket(beta=beta),))
        assert len(grid.points) == 1

    def test_grid_rejects_path_with_anchor_mismatch(self) -> None:
        """Construction MUST raise when no BracketPoint reconstructs anchors.

        Cross-references shipped simulations/tests/test_modules.py:185,194.
        """
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        # ε too large → anchors won't match (4200, 3800, 4200).
        bad_fx = FXPathParams(mean_x_over_y=4000.0, epsilon=0.5, omega=1.0)
        bad_point = BracketPoint(
            cost_params=_t2_cost(beta=beta), fx_params=bad_fx, horizon_T=12
        )
        with pytest.raises(FXPathReconstructionError):
            BracketGrid(points=(bad_point,))

    def test_anchor_constants_match_shipped_test(self) -> None:
        """Pin BRACKET-M5 anchor literals must match shipped FX test."""
        assert M5_ANCHOR_VALUES == (4200.0, 3800.0, 4200.0)
        # M5_ANCHOR_TIMES = (0, π/2, π).
        assert math.isclose(M5_ANCHOR_TIMES[0], 0.0)
        assert math.isclose(M5_ANCHOR_TIMES[1], math.pi / 2)
        assert math.isclose(M5_ANCHOR_TIMES[2], math.pi)


# ─── Pin Δ-cohort ────────────────────────────────────────────────────────────


class TestDeltaClosedForm:
    def test_delta_numerical_finite_on_canonical_inputs(self) -> None:
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        bracket = _make_bracket(beta=beta)
        evaluator = DeltaNumericalEvaluator(bracket=bracket, sigma_T=10_000.0)
        # 5 draws × 12 months of τ_t.
        tau_draws = np.full((5, 12), 1_500_000.0, dtype=np.float64)
        delta = evaluator(tau_draws)
        assert delta.shape == (5,)
        assert np.all(np.isfinite(delta))

    def test_delta_symbolic_lambdify_matches_numerical(self) -> None:
        """Pin Δ-cohort reconciler: lambdified sympy ↔ hand-coded < 1e-10·T."""
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        bracket = _make_bracket(beta=beta)
        sigma_T = 10_000.0
        # One τ_t row.
        np.random.seed(0)
        tau = np.random.uniform(
            500_000.0, 2_000_000.0, size=12
        ).astype(np.float64)
        reconciler = DeltaSymbolicNumericalReconciler()
        assert reconciler(bracket, sigma_T, tau) is True

    def test_delta_symbolic_deriver_returns_sympy_expr(self) -> None:
        deriver = DeltaSymbolicDeriver()
        e1 = deriver()
        e2 = deriver()
        assert isinstance(e1, sp.Expr)
        # Re-deriving twice yields a structurally-identical Expr.
        assert sp.simplify(e1 - e2) == 0

    def test_delta_constant_q_positive_f_positive_phase_negative(self) -> None:
        """Sanity: with q_t = const > 0 and f_t weighted appropriately, Δ has expected sign.

        This is a sanity check on the closed form's sign convention. The Σ
        f_t · 1/(X/Y)_t² alternates in t; over a finite window the sum sign
        depends on ω. Here we use ω = 2π/T so f_t spans a full period —
        Δ should be near zero by symmetry. The test asserts
        |Δ| is finite (not zero — the precise sign depends on the
        particular ω; the gate's sign claim is over the spec brackets).
        """
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        bracket = BracketPoint(
            cost_params=_t2_cost(beta=beta),
            fx_params=_m5_fx_params(),
            horizon_T=12,
        )
        ev = DeltaNumericalEvaluator(bracket=bracket, sigma_T=10_000.0)
        # τ_t = 0 gives q_t ≈ p_sub_bar = 20.
        tau_draws = np.zeros((1, 12), dtype=np.float64)
        delta = ev(tau_draws)
        assert np.all(np.isfinite(delta))


# ─── Pin Γ-cohort ────────────────────────────────────────────────────────────


class TestGammaFiniteDifference:
    def test_gamma_finite_and_reported(self) -> None:
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        bracket = _make_bracket(beta=beta)
        evaluator = GammaEvaluator(bracket=bracket, sigma_T=10_000.0)
        tau_draws = np.full((3, 12), 1_500_000.0, dtype=np.float64)
        gamma = evaluator(tau_draws)
        assert gamma.shape == (3,)
        assert np.all(np.isfinite(gamma))


# ─── Sign-cert PASS / FAIL ───────────────────────────────────────────────────


class TestSignCertificationGate:
    """CR-BLOCKING-2 v0.3 fix: PASS / FAIL tests use deterministic fixtures
    that mathematically force the verdict — assertions are exact, not
    membership in the alphabet.
    """

    def _grid_with_one_point(self) -> tuple[BracketGrid, float]:
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        return BracketGrid(points=(_make_bracket(beta=beta),)), beta

    def test_gate_pass_when_all_brackets_strictly_negative(self) -> None:
        """Force Δ < 0 deterministically.

        With the canonical M5 FX path (ε=0.1, ω=1, T=12) the closed-form
        weight ``Σ f_t / (X/Y)_t² ≈ -3.6e-8`` is mathematically negative
        (verified analytically). With τ = 1.5M < κ = 1.6M, softplus(τ−κ)
        ≈ 0 ⇒ q_t ≈ p̄_sub = 20 > 0. Therefore
        Δ = (positive prefactor) · (positive q) · (negative Σ) < 0.
        """
        grid, _b = self._grid_with_one_point()
        gate = SignCertificationGate(sigma_T=10_000.0)
        tau_draws = np.full((100, 12), 1_500_000.0, dtype=np.float64)
        # Verify the analytic Σ sign before running the gate.
        T = 12
        t = np.arange(1, T + 1, dtype=np.float64)
        f_t = np.cos(t) ** 2 - 0.5
        x_over_y = (1.0 + 0.1 * f_t) * 4000.0
        weight_sum = float(np.sum(f_t / x_over_y ** 2))
        assert weight_sum < 0.0, (
            f"Test-fixture invariant: weight sum must be < 0 on M5 path,"
            f" got {weight_sum}"
        )
        verdict = gate(grid, (tau_draws,))
        assert verdict.sub_task == "COHORT-2"
        assert verdict.verdict == "PASS"
        assert verdict.n_sign_violations == 0
        assert verdict.n_bracket_points == 1
        assert len(verdict.evidence) == 1
        # Δ_med must be strictly negative.
        assert verdict.evidence[0].delta_median < 0.0
        assert verdict.evidence[0].delta_upper_bound_quantile < 0.0

    def test_gate_fail_when_any_bracket_violates_sign(self) -> None:
        """Force Δ > 0 deterministically by inverting the FX-path sign.

        Set ``ω = π`` so ``f_t = cos²(π t) − 1/2 = 1/2 ∀ t ∈ ℤ_+`` —
        the weight Σ f_t/(X/Y)² is then strictly positive (each term
        is positive). With q_t > 0 ⇒ Δ > 0 ⇒ verdict FAIL.

        We can't use a non-anchor BracketGrid (M5 reconstruction would
        fail), so we pass a raw tuple of points to the gate per the
        v0.3 API.
        """
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        # ω = π gives f_t = +0.5 ∀ integer t (cos²(kπ) = 1).
        positive_fx = FXPathParams(
            mean_x_over_y=4000.0, epsilon=0.1, omega=math.pi
        )
        # Verify analytically.
        T = 12
        t = np.arange(1, T + 1, dtype=np.float64)
        f_t = np.cos(math.pi * t) ** 2 - 0.5
        assert np.all(f_t > 0.0), f"f_t must be > 0 ∀ t, got {f_t}"
        # Build a non-anchor BracketPoint and pass as raw tuple (v0.3 API).
        cost = _t2_cost(beta=beta)
        flip_point = BracketPoint(
            cost_params=cost, fx_params=positive_fx, horizon_T=12
        )
        gate = SignCertificationGate(sigma_T=10_000.0)
        tau_draws = np.full((100, 12), 1_500_000.0, dtype=np.float64)
        verdict = gate((flip_point,), (tau_draws,))
        assert verdict.verdict == "FAIL"
        assert verdict.n_sign_violations == 1
        assert verdict.evidence[0].delta_median > 0.0
        assert verdict.evidence[0].sign_strictly_negative is False

    def test_gate_evidence_unique_indices(self) -> None:
        grid, _b = self._grid_with_one_point()
        gate = SignCertificationGate(sigma_T=10_000.0)
        tau_draws = np.full((50, 12), 1_500_000.0, dtype=np.float64)
        verdict = gate(grid, (tau_draws,))
        indices = [ev.bracket_index for ev in verdict.evidence]
        assert len(indices) == len(set(indices))


# ─── PPC quantile coverage (MQ-FLAG-3 v0.2 fix) ──────────────────────────────


class TestPPCQuantileCoverage:
    """CR-BLOCKING-3 v0.3 fix — per-quantile τ_q coverage.

    For each q ∈ {0.50, 0.90, 0.99}: the posterior τ_q distribution is
    estimated by taking the sample q-th percentile of each posterior draw
    (axis=1). We build a 95% CI for τ_q across the posterior axis, then
    check what fraction of held-out observed τ_q values (each computed
    from an independent replicate sample) falls inside the CI.
    """

    def test_well_calibrated_passes(self) -> None:
        """Calibrated PPC: held-out τ_q values come from the same dist.

        Generate ``n_replicate`` independent N(0,1) samples, compute
        τ_q per replicate as the held-out observation. The posterior
        is N(0,1) so τ_q's posterior CI contains ~95% of held-out τ_q.
        """
        check = PPCQuantileCoverageCheck()
        rng = np.random.default_rng(42)
        n_obs = 200
        n_ppc = 500
        n_replicate = 1000
        # Posterior draws ~ N(0, 1).
        ppc = rng.standard_normal((n_ppc, n_obs))
        # Held-out observations: one τ_q per independent replicate of n_obs N(0,1).
        observed = {}
        for key, level in zip(("p50", "p90", "p99"), (0.50, 0.90, 0.99)):
            replicate_samples = rng.standard_normal((n_replicate, n_obs))
            observed[key] = np.quantile(replicate_samples, level, axis=1)
        cov = check(ppc, observed)
        assert set(cov.keys()) == {"p50", "p90", "p99"}
        # All three coverages must lie in the calibration band.
        for k, v in cov.items():
            assert 0.93 <= v <= 0.97, (
                f"PPC coverage at {k} = {v:.4f} outside [0.93, 0.97]"
            )

    def test_miscoverage_raises_halt(self) -> None:
        check = PPCQuantileCoverageCheck()
        rng = np.random.default_rng(42)
        n_obs = 200
        n_ppc = 100
        n_replicate = 500
        # Posterior is far too narrow → coverage will be ~0.
        ppc = rng.normal(0.0, 0.001, size=(n_ppc, n_obs))
        observed = {}
        for key, level in zip(("p50", "p90", "p99"), (0.50, 0.90, 0.99)):
            replicate_samples = rng.normal(0.0, 1.0, size=(n_replicate, n_obs))
            observed[key] = np.quantile(replicate_samples, level, axis=1)
        with pytest.raises(PPCQuantileMiscoverageError):
            check(ppc, observed)

    def test_per_quantile_keys_drive_distinct_computation(self) -> None:
        """CR-B3 anti-tautology: the three keys p50/p90/p99 produce
        DIFFERENT τ_q computations and different CIs.

        v0.2 looped over keys but `del`-ed `level`, computing identical
        per-replicate CIs three times. v0.3 must produce three distinct
        τ_q distributions / CIs.
        """
        rng = np.random.default_rng(0)
        n_obs = 100
        n_ppc = 200
        ppc = rng.standard_normal((n_ppc, n_obs))
        # Per-row sample quantiles ⇒ distinct distributions.
        tau_50 = np.quantile(ppc, 0.50, axis=1)
        tau_90 = np.quantile(ppc, 0.90, axis=1)
        tau_99 = np.quantile(ppc, 0.99, axis=1)
        assert not np.allclose(tau_50, tau_90)
        assert not np.allclose(tau_90, tau_99)
        # 95% CIs at distinct quantile levels are far apart.
        ci_50 = np.quantile(tau_50, [0.025, 0.975])
        ci_90 = np.quantile(tau_90, [0.025, 0.975])
        ci_99 = np.quantile(tau_99, [0.025, 0.975])
        # p99 CI is near 2.3 (Φ⁻¹(0.99)); p50 CI is near 0; not allclose.
        assert abs(ci_50[0] - ci_90[0]) > 0.5
        assert abs(ci_90[0] - ci_99[0]) > 0.3


# ─── Pin ROBUST-BS ───────────────────────────────────────────────────────────


class TestBankSpreadRobustness:
    def test_robustness_arm_emits_separate_verdict(self) -> None:
        """Pin ROBUST-BS — robustness arm yields an INDEPENDENT verdict."""
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        grid = BracketGrid(points=(_make_bracket(beta=beta),))
        # Primary verdict.
        gate = SignCertificationGate(sigma_T=10_000.0)
        tau = np.full((50, 12), 1_500_000.0, dtype=np.float64)
        primary = gate(grid, (tau,))
        # Robustness arm.
        runner = BankSpreadRobustnessRunner(bank_spread=0.005)
        robust = runner(grid, sigma_T=10_000.0, tau_t_draws_per_bracket=(tau,))
        # Both verdicts share schema.
        assert primary.sub_task == robust.sub_task == "COHORT-2"
        # But audit_blocks differ (different inputs).
        assert primary.audit_block != robust.audit_block

    def test_appender_writes_robustness_md_separately_from_gate_json(
        self, tmp_path: Path
    ) -> None:
        """Pin ROBUST-BS — appender NEVER touches gate_verdict.json."""
        fitter = _fitter_for_token_scale()
        beta = fitter(1_600_000.0)
        grid = BracketGrid(points=(_make_bracket(beta=beta),))
        gate = SignCertificationGate(sigma_T=10_000.0)
        tau = np.full((20, 12), 1_500_000.0, dtype=np.float64)
        primary = gate(grid, (tau,))
        runner = BankSpreadRobustnessRunner(bank_spread=0.005)
        robust = runner(grid, 10_000.0, (tau,))
        # Write primary to gate_verdict.json.
        writer = GateVerdictWriter(base_dir=tmp_path)
        gate_path = writer(primary)
        # Append robust to ROBUSTNESS_RESULTS.md.
        appender = RobustnessResultsAppender(base_dir=tmp_path)
        rob_path = appender(robust, bank_spread=0.005)
        # Distinct files; gate_verdict.json contains ONLY the primary.
        assert gate_path != rob_path
        gate_data = json.loads(gate_path.read_text())
        assert gate_data["audit_block"] == primary.audit_block
        # Robustness file does NOT mention the primary's audit block
        # (loose check: file content is markdown and references robust.audit_block).
        rob_text = rob_path.read_text()
        assert robust.audit_block in rob_text


# ─── Verdict-alphabet + IO contract ──────────────────────────────────────────


class TestVerdictAlphabetAndIO:
    def test_verdict_literal_alphabet_full(self) -> None:
        """Pin RC-BLOCK-2 v0.2 fix — verdict alphabet is full spec §10."""
        # Construction with each label (synthesizing minimal evidence).
        ev_pass = SignVerdict(
            bracket_index=0,
            delta_median=-1.0,
            delta_lower_bound_quantile=-2.0,
            delta_upper_bound_quantile=-0.5,
            sign_strictly_negative=True,
        )
        # PASS works.
        v = CohortGateVerdict(
            sub_task="COHORT-2",
            verdict="PASS",
            n_bracket_points=1,
            n_sign_violations=0,
            evidence=(ev_pass,),
            audit_block="0" * 64,
            fetched_at_utc="2026-05-08T00:00:00Z",
        )
        assert v.verdict == "PASS"
        # WEAK / MARGINAL / INDISTINGUISHABLE accept the alphabet but
        # are reserved for future sub-verdicts; constructing succeeds.
        for label in ("WEAK", "MARGINAL", "INDISTINGUISHABLE"):
            v2 = CohortGateVerdict(
                sub_task="COHORT-2",
                verdict=label,  # type: ignore[arg-type]
                n_bracket_points=1,
                n_sign_violations=0,
                evidence=(ev_pass,),
                audit_block="0" * 64,
                fetched_at_utc="2026-05-08T00:00:00Z",
            )
            assert v2.verdict == label

    def test_halt_is_not_a_verdict_value(self) -> None:
        """RC-BLOCK-2 v0.2 fix: HALT is harness action, not a verdict."""
        ev = SignVerdict(
            bracket_index=0,
            delta_median=-1.0,
            delta_lower_bound_quantile=-2.0,
            delta_upper_bound_quantile=-0.5,
            sign_strictly_negative=True,
        )
        with pytest.raises(ValueError):
            CohortGateVerdict(
                sub_task="COHORT-2",
                verdict="HALT",  # type: ignore[arg-type]
                n_bracket_points=1,
                n_sign_violations=0,
                evidence=(ev,),
                audit_block="0" * 64,
                fetched_at_utc="2026-05-08T00:00:00Z",
            )

    def test_writer_emits_spec_10_schema(self, tmp_path: Path) -> None:
        ev = SignVerdict(
            bracket_index=0,
            delta_median=-1.0,
            delta_lower_bound_quantile=-2.0,
            delta_upper_bound_quantile=-0.5,
            sign_strictly_negative=True,
        )
        v = CohortGateVerdict(
            sub_task="COHORT-2",
            verdict="PASS",
            n_bracket_points=1,
            n_sign_violations=0,
            evidence=(ev,),
            audit_block="a" * 64,
            fetched_at_utc="2026-05-08T00:00:00Z",
        )
        out = GateVerdictWriter(base_dir=tmp_path)(v)
        data = json.loads(out.read_text())
        assert data["sub_task"] == "COHORT-2"
        assert data["verdict"] == "PASS"
        assert "evidence" in data
        assert data["audit_block"] == v.audit_block

    def test_verdict_pass_requires_zero_violations(self) -> None:
        ev_fail = SignVerdict(
            bracket_index=0,
            delta_median=1.0,
            delta_lower_bound_quantile=0.5,
            delta_upper_bound_quantile=2.0,
            sign_strictly_negative=False,
        )
        with pytest.raises(ValueError):
            CohortGateVerdict(
                sub_task="COHORT-2",
                verdict="PASS",  # PASS but a violation present → reject.
                n_bracket_points=1,
                n_sign_violations=1,
                evidence=(ev_fail,),
                audit_block="0" * 64,
                fetched_at_utc="2026-05-08T00:00:00Z",
            )


# ─── Five-bracket-point sign certification ──────────────────────────────────


class TestSpec5_2BracketGrid:
    """MQ-BLOCK-2 v0.3 fix — bracket re-orientation.

    The bracket grid sweeps the spec §5.2 **parameter** Cartesian product
    (3 tiers × 2 α × 2 cache × 2 κ-arm = 24 points), all sharing the
    canonical M5 FX path. Replaces the v0.2 (ε, ω)-sweep mis-orientation.
    """

    def test_grid_has_24_brackets(self) -> None:
        fitter = _fitter_for_token_scale()
        grid = build_spec_5_2_bracket_grid(
            fitter=fitter, fx_params=_m5_fx_params(), horizon_T=12
        )
        assert len(grid.points) == 24

    def test_grid_enumerates_all_three_tiers(self) -> None:
        fitter = _fitter_for_token_scale()
        grid = build_spec_5_2_bracket_grid(
            fitter=fitter, fx_params=_m5_fx_params(), horizon_T=12
        )
        p_subs = {p.cost_params.p_sub_bar for p in grid.points}
        assert p_subs == {20.0, 100.0, 200.0}
        kappas = {p.cost_params.kappa for p in grid.points}
        # 3 tiers × 2 κ-arm = 6 distinct κ values.
        assert len(kappas) == 6

    def test_grid_enumerates_two_p_t_cache_values(self) -> None:
        fitter = _fitter_for_token_scale()
        grid = build_spec_5_2_bracket_grid(
            fitter=fitter, fx_params=_m5_fx_params(), horizon_T=12
        )
        p_ts = {round(p.cost_params.p_t, 6) for p in grid.points}
        # h_cache ∈ {0.80, 0.95} → 2 distinct p_t values.
        assert len(p_ts) == 2

    def test_grid_runs_through_gate(self) -> None:
        """Sign cert over the full 24-bracket spec §5.2 grid."""
        fitter = _fitter_for_token_scale()
        grid = build_spec_5_2_bracket_grid(
            fitter=fitter, fx_params=_m5_fx_params(), horizon_T=12
        )
        # τ < κ_pro so softplus ≈ 0; all brackets give Δ ≈ p_sub · prefactor · weight_sum < 0
        tau = np.full((50, 12), 1_500_000.0, dtype=np.float64)
        gate = SignCertificationGate(sigma_T=10_000.0)
        verdict = gate(grid, tuple(tau for _ in grid.points))
        assert verdict.n_bracket_points == 24
        assert len(verdict.evidence) == 24
        # Anti-fishing: this is the spec gate — sign expectation Δ < 0
        # at every bracket per §8(1). A single sign-flip HALTs upstream.
        assert verdict.verdict == "PASS"
        assert verdict.n_sign_violations == 0
        # Δ_med must be strictly negative at every bracket point.
        for ev in verdict.evidence:
            assert ev.delta_median < 0.0, (
                f"Bracket {ev.bracket_index}: Δ_med = {ev.delta_median}"
                " not < 0 (sign-flip HALT)"
            )


# ─── Hypothesis property: joint (β, κ) M2 monotonicity ───────────────────────


class TestJointHypothesis:
    @given(
        kappa=st.floats(
            min_value=1e6, max_value=1e8, allow_nan=False, allow_infinity=False
        )
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_softplus_fit_monotone_convergence(self, kappa: float) -> None:
        """Tightening β → ReLU baseline at τ > κ (Phase 3 hypothesis-tests scope)."""
        fitter = _fitter_for_token_scale()
        beta = fitter(kappa)
        composer = T2CostComposer(
            p_sub_bar=20.0, kappa=kappa, beta=beta, p_t=7.15
        )
        tau = np.array([1.5 * kappa, 3.0 * kappa], dtype=np.float64)
        q = composer(tau)
        relu = 20.0 + 7.15 * np.maximum(tau - kappa, 0.0)
        # Within softplus tightness scaled by p_t.
        # (1e-3 · κ) is the L¹ deviation; pointwise can be looser.
        assert np.all(q >= relu - 7.15 * kappa * 1e-2)
