"""Callable-tier unit tests — math pins M1, M2, M3, M5.

- M1: ``TruncParetoSampler`` refuses ``alpha < 1.5`` at construction time.
- M2: ``SoftplusRegularizer`` refuses non-tight ``beta`` (deviation ≥ 1e-3·κ).
- M3: ``BlendedPriceFn(Sonnet defaults)`` returns ≈ 7.149 USD/MTok plus
       cache-corner closed-form expectations (h=0 → no cache, h=1 → full cache).
- M5: ``FXPathGen`` evaluated at ``t ∈ {0, π/2, π}`` matches the closed-form
       triple ``(4200, 3800, 4200)``; ``epsilon_from_sigma_T`` round-trips
       within a documented numerical tolerance.

Phase 3.3 ``hypothesis-tests`` will EXTEND this file with property tests over
the Callable transforms (joint identifiability per CORRECTIONS-α §15.3).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from simulations.modules.fx_path import (
    FXPathGen,
    RealizedVarianceCalc,
    epsilon_from_sigma_T,
)
from simulations.modules.pricing import BlendedPriceFn
from simulations.modules.regularizers import SoftplusRegularizer
from simulations.modules.samplers import (
    NegBinSampler,
    TierMixCategorical,
    TruncParetoSampler,
)
from simulations.types.distributions import (
    NegBinParams,
    SoftplusParams,
    TruncParetoParams,
)
from simulations.types.fx import (
    BlendedPriceParams,
    FXPathParams,
    RealizedVarianceParams,
)
from simulations.types.tier import TIER_IDS, TierPrior


# ─── Pin M1 — TruncPareto α-floor ─────────────────────────────────────────────


class TestM1TruncParetoAlphaFloor:
    """Math pin M1 (spec §8(6))."""

    @pytest.mark.parametrize("alpha", [1.0, 1.4999, 1.0001, 0.5])
    def test_truncpareto_sampler_refuses_alpha_below_floor(self, alpha: float) -> None:
        """Sampler refuses α < 1.5 with a typed ValueError citing the spec."""
        params = TruncParetoParams(alpha=alpha, x_m=1.0, x_max=100.0)
        with pytest.raises(ValueError, match=r"§8\(6\)|alpha"):
            TruncParetoSampler(params=params)

    @pytest.mark.parametrize("alpha", [1.5, 2.0, 2.5])
    def test_truncpareto_sampler_accepts_alpha_at_or_above_floor(
        self, alpha: float
    ) -> None:
        """Sampler accepts α ≥ 1.5 (the spec §8(6) floor)."""
        params = TruncParetoParams(alpha=alpha, x_m=1.0, x_max=100.0)
        sampler = TruncParetoSampler(params=params)
        rng = np.random.default_rng(seed=42)
        samples = sampler(size=128, rng=rng)
        assert samples.shape == (128,)
        assert np.all(samples >= 1.0) and np.all(samples <= 100.0)

    def test_truncpareto_sampler_size_zero(self) -> None:
        """size=0 yields an empty array."""
        sampler = TruncParetoSampler(
            params=TruncParetoParams(alpha=2.0, x_m=1.0, x_max=10.0)
        )
        out = sampler(size=0, rng=np.random.default_rng(0))
        assert out.shape == (0,)

    def test_truncpareto_sampler_negative_size_raises(self) -> None:
        """size < 0 is rejected."""
        sampler = TruncParetoSampler(
            params=TruncParetoParams(alpha=2.0, x_m=1.0, x_max=10.0)
        )
        with pytest.raises(ValueError, match="size"):
            sampler(size=-1, rng=np.random.default_rng(0))


# ─── Pin M2 — Softplus β-tightness ────────────────────────────────────────────


class TestM2SoftplusTightness:
    """Math pin M2 (spec §5.1 (T2))."""

    def test_softplus_regularizer_refuses_loose_beta(self) -> None:
        """β=0.1, κ=1.0 fails the tightness floor by orders of magnitude."""
        with pytest.raises(ValueError, match="L¹|deviation"):
            SoftplusRegularizer(params=SoftplusParams(beta=0.1, kappa=1.0))

    def test_softplus_regularizer_accepts_tight_beta(self) -> None:
        """β=200, κ=1.0 clears the tightness floor."""
        reg = SoftplusRegularizer(params=SoftplusParams(beta=200.0, kappa=1.0))
        x = np.linspace(-2.0, 2.0, 16, dtype=np.float64)
        y = reg(x)
        # Softplus must be ≥ ReLU pointwise.
        relu = np.maximum(x, 0.0)
        assert np.all(y + 1e-9 >= relu)

    def test_softplus_call_shape_preservation(self) -> None:
        """Output shape equals input shape."""
        reg = SoftplusRegularizer(params=SoftplusParams(beta=200.0, kappa=1.0))
        x = np.zeros((3, 4), dtype=np.float64)
        assert reg(x).shape == (3, 4)

    @pytest.mark.parametrize("beta_kappa", [100.0, 150.0, 200.0])
    def test_softplus_boundary_regime(self, beta_kappa: float) -> None:
        """β·κ in [100, 200] — thinnest part of M2 admissible region per CR I4.

        50/κ is the documented edge per the regularizer docstring (deviation
        ≈ 1e-3·κ). We probe at and above 100 to document that the admissible
        region is robust at the boundary; β·κ=50 is intentionally excluded
        because it sits exactly at the deviation threshold and may flip
        depending on grid choice — see :func:`tight_softplus_params` for the
        100/κ headroom rationale.
        """
        params = SoftplusParams(beta=beta_kappa, kappa=1.0)
        SoftplusRegularizer(params=params)  # should not raise


# ─── Pin M3 — Blended per-token price ─────────────────────────────────────────


class TestM3BlendedPrice:
    """Math pin M3 (spec §5.1)."""

    def test_blended_price_sonnet_default(self) -> None:
        """Sonnet defaults yield ≈ 7.149 USD/MTok within 1e-3."""
        params = BlendedPriceParams(
            w_in=0.539, w_out=0.461, h_cache=0.95, p_in=3.0, p_out=15.0
        )
        result = BlendedPriceFn(params=params)()
        # 0.539·3·0.145 + 0.461·15 = 0.234465 + 6.915 = 7.149465
        assert math.isclose(result, 7.149465, abs_tol=1e-3)

    def test_blended_price_no_cache_corner(self) -> None:
        """h_cache=0 collapses cache_factor to 1: p_t = w_in·p_in + w_out·p_out."""
        params = BlendedPriceParams(
            w_in=0.539, w_out=0.461, h_cache=0.0, p_in=3.0, p_out=15.0
        )
        expected = 0.539 * 3.0 + 0.461 * 15.0
        result = BlendedPriceFn(params=params)()
        assert math.isclose(result, expected, abs_tol=1e-12)

    def test_blended_price_full_cache_corner(self) -> None:
        """h_cache=1 collapses cache_factor to 0.10 (cached_input_discount)."""
        params = BlendedPriceParams(
            w_in=0.539, w_out=0.461, h_cache=1.0, p_in=3.0, p_out=15.0
        )
        expected = 0.539 * 3.0 * 0.10 + 0.461 * 15.0
        result = BlendedPriceFn(params=params)()
        assert math.isclose(result, expected, abs_tol=1e-12)

    @pytest.mark.parametrize(
        ("p_in", "p_out", "label"),
        [(5.0, 25.0, "opus"), (1.0, 5.0, "haiku")],
    )
    def test_blended_price_other_tiers_positive(
        self, p_in: float, p_out: float, label: str
    ) -> None:
        """Opus and Haiku also evaluate to a positive blended price."""
        params = BlendedPriceParams(
            w_in=0.539, w_out=0.461, h_cache=0.95, p_in=p_in, p_out=p_out
        )
        result = BlendedPriceFn(params=params)()
        assert result > 0.0, f"tier={label} produced non-positive p_t"


# ─── Pin M5 — FX path closed form ─────────────────────────────────────────────


class TestM5FXPath:
    """Math pin M5 (PRIMITIVES.md (6) + (8))."""

    def test_fx_path_at_anchor_points(self) -> None:
        """t ∈ {0, π/2, π} yield (4200, 3800, 4200) within 1e-9.

        Closed form: cos²(0)=1 → 1.05·4000=4200; cos²(π/2)=0 → 0.95·4000=3800;
        cos²(π)=1 → 4200.
        """
        params = FXPathParams(mean_x_over_y=4000.0, epsilon=0.1, omega=1.0)
        gen = FXPathGen(params=params)
        ts = np.array([0.0, math.pi / 2.0, math.pi], dtype=np.float64)
        out = gen(ts)
        np.testing.assert_allclose(out, [4200.0, 3800.0, 4200.0], atol=1e-9)

    def test_fx_path_envelope_bounds(self) -> None:
        """Generated path stays inside mean·(1±ε/2)."""
        params = FXPathParams(mean_x_over_y=4000.0, epsilon=0.2, omega=2.5)
        gen = FXPathGen(params=params)
        ts = np.linspace(0.0, 10.0, 1024, dtype=np.float64)
        out = gen(ts)
        assert np.all(out >= 4000.0 * (1.0 - 0.1) - 1e-9)
        assert np.all(out <= 4000.0 * (1.0 + 0.1) + 1e-9)

    def test_realized_variance_proxy(self) -> None:
        """σ_T over a flat path equal to the mean is exactly zero."""
        rv = RealizedVarianceCalc(
            params=RealizedVarianceParams(horizon_T=100),
            mean_x_over_y=4000.0,
        )
        # PRIMITIVES (7) horizon contract: path length = horizon_T + 1 = 101.
        flat_path = np.full(101, 4000.0, dtype=np.float64)
        assert rv(flat_path) == 0.0

    def test_realized_variance_divisor_is_T_not_T_plus_one(self) -> None:
        """PRIMITIVES.md (7) divisor is T (NOT T+1). Pin (CR I-1).

        Sum of T+1 squared deviations divided by T — not by len(path).
        """
        # T = 4, path length = 5.
        path = np.array([4200.0, 3800.0, 4200.0, 3800.0, 4200.0], dtype=np.float64)
        mean = 4000.0
        rv = RealizedVarianceCalc(
            params=RealizedVarianceParams(horizon_T=4),
            mean_x_over_y=mean,
        )
        diffs = path - mean
        expected = float(np.sum(diffs * diffs) / 4)  # divide by T=4, not 5
        # Sanity: divide-by-5 (the bug) would give a different number.
        wrong = float(np.sum(diffs * diffs) / 5)
        assert rv(path) == expected
        assert expected != wrong

    def test_epsilon_from_sigma_T_inverts_within_tolerance(self) -> None:
        """Round-trip: given ε, compute σ_T over a long path, invert; recover ε.

        Note (per Task 2.4 brief): the round trip is approximate because σ_T
        from a finite path samples the cos² envelope rather than its true
        mean-square deviation. The closed form gives
        ``σ_T(true) = ε² · mean² / 8`` (cos² has variance 1/8 about its mean
        of 1/2). With a long t-grid spanning many periods the empirical σ_T
        converges to this. Tolerance 1e-3 (abs) holds for this regime.
        """
        mean = 4000.0
        true_eps = 0.1
        # Closed-form σ_T from PRIMITIVES (8) inverted: σ_T = ε² mean² / 8
        sigma_T_closed = (true_eps ** 2) * (mean ** 2) / 8.0
        recovered = epsilon_from_sigma_T(sigma_T_closed, mean)
        assert math.isclose(recovered, true_eps, abs_tol=1e-9)

    def test_epsilon_from_sigma_T_path_round_trip_loose(self) -> None:
        """Path-derived round trip clears 1e-2 tolerance over many cycles.

        Document why: σ_T is mean-of-squared-deviation over a discrete path
        of length T+1, so it carries grid-induced bias of order 1/T. We use
        ω=1, T=4096 spanning ~650 cycles to wash that out; tolerance 1e-2
        is generous and holds reliably.
        """
        mean = 4000.0
        true_eps = 0.1
        params = FXPathParams(mean_x_over_y=mean, epsilon=true_eps, omega=1.0)
        gen = FXPathGen(params=params)
        ts = np.linspace(0.0, 4096.0, 4096, dtype=np.float64)
        path = gen(ts)
        # PRIMITIVES (7) horizon contract: T = len(path) - 1.
        sigma_T = RealizedVarianceCalc(
            params=RealizedVarianceParams(horizon_T=ts.size - 1),
            mean_x_over_y=mean,
        )(path)
        recovered = epsilon_from_sigma_T(sigma_T, mean)
        assert math.isclose(recovered, true_eps, abs_tol=1e-2)

    def test_epsilon_from_sigma_T_rejects_negative_sigma(self) -> None:
        """sigma_T must be ≥ 0."""
        with pytest.raises(ValueError, match="sigma_T"):
            epsilon_from_sigma_T(-1.0, 4000.0)

    def test_epsilon_from_sigma_T_rejects_bad_mean(self) -> None:
        """mean_x_over_y must be > 0."""
        with pytest.raises(ValueError, match="mean_x_over_y"):
            epsilon_from_sigma_T(1.0, 0.0)


# ─── Other Callable tier sanity ───────────────────────────────────────────────


class TestNegBinSampler:
    def test_negbin_sampler_returns_int64(self) -> None:
        """NegBinSampler returns int64 non-negative array."""
        sampler = NegBinSampler(params=NegBinParams(r=4.0, p=0.5))
        out = sampler(size=64, rng=np.random.default_rng(0))
        assert out.dtype == np.int64
        assert np.all(out >= 0)

    def test_negbin_sampler_negative_size_raises(self) -> None:
        """size < 0 rejected."""
        sampler = NegBinSampler(params=NegBinParams(r=4.0, p=0.5))
        with pytest.raises(ValueError, match="size"):
            sampler(size=-1, rng=np.random.default_rng(0))


class TestTierMixCategorical:
    def test_tier_mix_returns_admissible_ids(self) -> None:
        """TierMixCategorical returns only members of TIER_IDS."""
        sampler = TierMixCategorical(prior=TierPrior())
        out = sampler(size=128, rng=np.random.default_rng(0))
        assert set(out.tolist()).issubset(set(TIER_IDS))

    def test_tier_mix_negative_size_raises(self) -> None:
        """size < 0 rejected."""
        sampler = TierMixCategorical(prior=TierPrior())
        with pytest.raises(ValueError, match="size"):
            sampler(size=-1, rng=np.random.default_rng(0))


# ─── Phase 3.3 — Hypothesis property tests over Callable transforms ───────────
#
# Skill: hypothesis-tests. Strategies are imported from tests/strategies.py
# (built in Task 2.4). Each test below states ONE property; the docstring
# documents the expected behavior. If a counter-example shrinks to a tight
# example that violates the property, that's a real finding, not a flake.

from hypothesis import HealthCheck, given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from simulations.tests.strategies import (  # noqa: E402
    blended_price_params,
    fx_path_params,
    negbin_params,
    saas_truncpareto_params,
    tight_softplus_params,
)


def _truncpareto_analytic_mean(alpha: float, x_m: float, x_max: float) -> float:
    """Closed-form mean of the truncated Pareto on ``[x_m, x_max]`` (α ≠ 1).

    E[X] = α · x_m^α · (x_m^{1-α} - x_max^{1-α}) / ((α-1) · (1 - (x_m/x_max)^α)).
    """
    tail = (x_m / x_max) ** alpha
    num = alpha * (x_m ** alpha) * (x_m ** (1.0 - alpha) - x_max ** (1.0 - alpha))
    den = (alpha - 1.0) * (1.0 - tail)
    return float(num / den)


class TestTruncParetoSamplerProperty:
    """Property tests for :class:`TruncParetoSampler`."""

    @given(params=saas_truncpareto_params(), seed=st.integers(min_value=0, max_value=2**31 - 1))
    @settings(max_examples=50, deadline=None,
              suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
    def test_truncpareto_sampler_distributional_validity(
        self, params: TruncParetoParams, seed: int
    ) -> None:
        """Sample mean of n=10_000 draws is within 5% of the analytic mean.

        Property: for any α ≥ 1.5, x_m > 0, x_max > x_m, drawing 10_000 i.i.d.
        TruncPareto variates yields a sample mean within 5% relative tolerance
        of the closed-form ``E[X]``. Also confirms support: every sample lies
        in ``[x_m, x_max]``.
        """
        sampler = TruncParetoSampler(params=params)
        rng = np.random.default_rng(seed)
        samples = sampler(size=10_000, rng=rng)
        # Support property
        assert np.all(samples >= params.x_m)
        assert np.all(samples <= params.x_max)
        # Distributional property: mean within 5% of analytic
        analytic = _truncpareto_analytic_mean(
            params.alpha, params.x_m, params.x_max
        )
        emp = float(samples.mean())
        rel_err = abs(emp - analytic) / analytic
        assert rel_err < 0.05, (
            f"sample mean {emp} differs from analytic {analytic}"
            f" by {rel_err:.3%} > 5% (α={params.alpha},"
            f" x_m={params.x_m}, x_max={params.x_max})"
        )

    @given(
        alpha_lo=st.floats(min_value=1.5, max_value=2.0,
                            allow_nan=False, allow_infinity=False),
        alpha_hi_offset=st.floats(min_value=0.3, max_value=1.0,
                                   allow_nan=False, allow_infinity=False),
        x_m=st.floats(min_value=0.5, max_value=5.0,
                       allow_nan=False, allow_infinity=False),
        seed=st.integers(min_value=0, max_value=2**31 - 1),
    )
    @settings(max_examples=30, deadline=None,
              suppress_health_check=[HealthCheck.too_slow])
    def test_truncpareto_joint_identifiability(
        self, alpha_lo: float, alpha_hi_offset: float, x_m: float, seed: int
    ) -> None:
        """Joint identifiability of (α, x_m, x_max) — CORRECTIONS-α §15.3 / MQ-FLAG-J.

        Holding two parameters fixed, varying the third must produce a MONOTONE
        change in the sample mean of 10_000 i.i.d. draws (rng-seed-fixed):

        - α↑ ⇒ E[X]↓ (heavier left mass).
        - x_m↑ ⇒ E[X]↑ (lower-tail anchor lifted).
        - x_max↑ ⇒ E[X]↑ (upper-tail extended).

        If any monotonicity fails on a counterexample, that's either a sampler
        bug or a strategy bug — surface it immediately.
        """
        x_max = 10.0 * x_m
        alpha_hi = alpha_lo + alpha_hi_offset

        # rng-seed-fixed: identical u-stream for both α
        def _mean(alpha: float, xm: float, xM: float) -> float:
            rng = np.random.default_rng(seed)
            sampler = TruncParetoSampler(
                params=TruncParetoParams(alpha=alpha, x_m=xm, x_max=xM)
            )
            return float(sampler(size=10_000, rng=rng).mean())

        # (1) α↑ ⇒ E[X]↓
        m_lo_alpha = _mean(alpha_lo, x_m, x_max)
        m_hi_alpha = _mean(alpha_hi, x_m, x_max)
        assert m_hi_alpha < m_lo_alpha, (
            f"α-monotonicity FAILED: α={alpha_lo} → mean={m_lo_alpha},"
            f" α={alpha_hi} → mean={m_hi_alpha}"
        )

        # (2) x_m↑ ⇒ E[X]↑
        m_xm_lo = _mean(alpha_lo, x_m, x_max)
        m_xm_hi = _mean(alpha_lo, 2.0 * x_m, 10.0 * (2.0 * x_m))
        # Note: scaling x_m and x_max together is exactly a scale change ×2;
        # we want to vary x_m holding x_max fixed instead:
        m_xm_only_hi = _mean(alpha_lo, 1.5 * x_m, x_max)
        assert m_xm_only_hi > m_xm_lo - 1e-9, (
            f"x_m-monotonicity FAILED: x_m={x_m} → mean={m_xm_lo},"
            f" x_m={1.5*x_m} → mean={m_xm_only_hi}"
        )
        # And the "scale-equivariant" sanity check stays as a documented
        # observation but is not asserted strictly:
        _ = m_xm_hi  # noqa: F841 — kept for clarity / debugging

        # (3) x_max↑ ⇒ E[X]↑ (upper tail extended)
        m_xM_lo = _mean(alpha_lo, x_m, x_max)
        m_xM_hi = _mean(alpha_lo, x_m, 2.0 * x_max)
        assert m_xM_hi > m_xM_lo - 1e-9, (
            f"x_max-monotonicity FAILED: x_max={x_max} → mean={m_xM_lo},"
            f" x_max={2*x_max} → mean={m_xM_hi}"
        )


class TestNegBinSamplerProperty:
    """Property tests for :class:`NegBinSampler`."""

    @given(params=negbin_params(),
           seed=st.integers(min_value=0, max_value=2**31 - 1))
    @settings(max_examples=50, deadline=None,
              suppress_health_check=[HealthCheck.too_slow])
    def test_negbin_sampler_distributional_validity(
        self, params: NegBinParams, seed: int
    ) -> None:
        """Sample mean of 10_000 draws ≈ ``r·(1-p)/p`` within 5% (or 0.5 abs).

        Property: NegBin(r, p) under the (n=r, p) numpy convention has mean
        ``r·(1-p)/p``. Use both relative (5%) and absolute (0.5) tolerance
        because, when the analytic mean is small (e.g. r=0.001, p=0.999 → ≈0),
        relative error blows up while the integer sample mean is still tight.
        """
        sampler = NegBinSampler(params=params)
        rng = np.random.default_rng(seed)
        samples = sampler(size=10_000, rng=rng)
        assert np.all(samples >= 0)
        analytic = params.r * (1.0 - params.p) / params.p
        emp = float(samples.mean())
        # Tolerance: max(5% relative, 0.5 absolute) — the latter dominates for
        # tiny analytic means where Monte Carlo SE is the limiting factor.
        tol = max(0.05 * analytic, 0.5)
        assert abs(emp - analytic) < tol, (
            f"NegBin mean {emp} vs analytic {analytic} differs by"
            f" {abs(emp - analytic)} > tol={tol} (r={params.r}, p={params.p})"
        )


class TestSoftplusRegularizerProperty:
    """Property tests for :class:`SoftplusRegularizer`."""

    @given(params=tight_softplus_params())
    @settings(max_examples=50, deadline=None)
    def test_softplus_regularizer_monotonic(self, params: SoftplusParams) -> None:
        """softplus_β is monotonically non-decreasing on the real line.

        Property: for x_1 < x_2 < … < x_n, softplus(x_i) ≤ softplus(x_{i+1}).
        Evaluated on a deterministic grid of 256 points in [-100, 100].
        """
        reg = SoftplusRegularizer(params=params)
        x = np.linspace(-100.0, 100.0, 256, dtype=np.float64)
        y = reg(x)
        diffs = np.diff(y)
        # Allow tiny negative drift from float64 rounding near saturation.
        assert np.all(diffs >= -1e-9), (
            f"softplus not monotone: min diff = {diffs.min():.3e}"
        )

    @given(
        params=tight_softplus_params(),
        x=st.floats(min_value=-100.0, max_value=100.0,
                    allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100, deadline=None)
    def test_softplus_dominates_relu(
        self, params: SoftplusParams, x: float
    ) -> None:
        """softplus_β(x) ≥ max(x, 0) − 1e-9 (numerical slack) for any real x.

        Property (analytic): softplus(x) = β⁻¹·log(1+e^{βx}) ≥ max(x, 0)
        because log(1+e^{βx}) ≥ max(βx, 0). Holds for any β > 0.
        """
        reg = SoftplusRegularizer(params=params)
        x_arr = np.array([x], dtype=np.float64)
        y = float(reg(x_arr)[0])
        relu = max(x, 0.0)
        assert y + 1e-9 >= relu, (
            f"softplus({x})={y} < ReLU({x})={relu} (β={params.beta},"
            f" κ={params.kappa})"
        )


class TestFXPathGenProperty:
    """Property tests for :class:`FXPathGen`."""

    @given(
        params=fx_path_params(),
        ts=st.lists(
            st.floats(min_value=-1e3, max_value=1e3,
                      allow_nan=False, allow_infinity=False),
            min_size=1, max_size=64,
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_fx_path_envelope(
        self, params: FXPathParams, ts: list[float]
    ) -> None:
        """FX path stays in ``mean·[1 - ε/2, 1 + ε/2]`` for any t.

        Closed form: ``(X/Y)_t = (1 + ε·(cos²(ωt) - 1/2)) · mean``. Since
        ``cos²(ωt) ∈ [0, 1]`` ⇒ ``cos² - 1/2 ∈ [-1/2, 1/2]`` ⇒ multiplier
        ``∈ [1 - ε/2, 1 + ε/2]``.
        """
        gen = FXPathGen(params=params)
        out = gen(np.asarray(ts, dtype=np.float64))
        lo = params.mean_x_over_y * (1.0 - params.epsilon / 2.0)
        hi = params.mean_x_over_y * (1.0 + params.epsilon / 2.0)
        # Numerical slack: relative 1e-12 of envelope half-width.
        slack = 1e-12 * params.mean_x_over_y
        assert np.all(out >= lo - slack)
        assert np.all(out <= hi + slack)


class TestBlendedPriceFnProperty:
    """Property tests for :class:`BlendedPriceFn`."""

    @given(
        params=blended_price_params(),
        bump=st.floats(min_value=0.01, max_value=10.0,
                        allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100, deadline=None)
    def test_blended_price_monotone_in_p_in(
        self, params: BlendedPriceParams, bump: float
    ) -> None:
        """Holding (w_in, w_out, h_cache, p_out) fixed, p_in↑ ⇒ p_t↑.

        Closed form: ``p_t = w_in · p_in · (1 - h + 0.1h) + w_out · p_out``
        is linear in p_in with positive slope ``w_in · (1 - 0.9h_cache)``,
        which is strictly positive for ``w_in > 0`` and ``h_cache ≤ 1``.
        """
        base = BlendedPriceFn(params=params)()
        bumped_params = BlendedPriceParams(
            w_in=params.w_in,
            w_out=params.w_out,
            h_cache=params.h_cache,
            p_in=params.p_in + bump,
            p_out=params.p_out,
        )
        bumped = BlendedPriceFn(params=bumped_params)()
        assert bumped > base, (
            f"BlendedPrice not monotone in p_in: base={base},"
            f" bumped={bumped}, params={params}, bump={bump}"
        )


class TestEpsilonSigmaTRoundTripProperty:
    """Property tests for ``epsilon_from_sigma_T`` ↔ closed/path forms."""

    @given(params=fx_path_params())
    @settings(max_examples=100, deadline=None)
    def test_eps_sigma_T_round_trip_closed_form(
        self, params: FXPathParams
    ) -> None:
        """Closed-form round trip: ``ε(σ_T_closed(ε)) ≈ ε`` within 1e-9.

        From PRIMITIVES (8): ``σ_T_closed = ε² · mean² / 8``. Inverting yields
        ``ε = sqrt(8 σ_T / mean²)``. Round trip is exact up to float64 ulp.
        """
        eps = params.epsilon
        mean = params.mean_x_over_y
        sigma_T_closed = (eps ** 2) * (mean ** 2) / 8.0
        recovered = epsilon_from_sigma_T(sigma_T_closed, mean)
        assert math.isclose(recovered, eps, abs_tol=1e-9, rel_tol=1e-9)

    @given(params=fx_path_params())
    @settings(max_examples=20, deadline=None,
              suppress_health_check=[HealthCheck.too_slow])
    def test_eps_sigma_T_round_trip_path_derived(
        self, params: FXPathParams
    ) -> None:
        """Path-derived round trip: ε ≈ recovered ε within 1e-2.

        Empirical σ_T over a length-4096 path spanning many periods
        (rescaled by ω) converges to the closed-form ε² mean² / 8 with
        bias O(1/T). Tolerance 1e-2 absolute holds for ε ≥ 1e-2; for
        very small ε the absolute tolerance is the limiting factor.
        """
        # Span ~ many cycles regardless of ω: t-grid in units of period.
        period = 2.0 * math.pi / params.omega
        ts = np.linspace(0.0, 256.0 * period, 4096, dtype=np.float64)
        gen = FXPathGen(params=params)
        path = gen(ts)
        # PRIMITIVES (7) horizon contract: T = len(path) - 1.
        sigma_T = RealizedVarianceCalc(
            params=RealizedVarianceParams(horizon_T=ts.size - 1),
            mean_x_over_y=params.mean_x_over_y,
        )(path)
        recovered = epsilon_from_sigma_T(sigma_T, params.mean_x_over_y)
        assert math.isclose(recovered, params.epsilon, abs_tol=1e-2)


# ─── Phase 3.5 — Pre-mortem regression tests ──────────────────────────────────
#
# Skill: pre-mortem. Each test pins a CURRENTLY-INTENTIONAL behavior that is
# documented in the production docstring as silent / documentary / boundary,
# so that a future "defensive guard" PR cannot land without explicitly
# revisiting the contract. See scratch/2026-05-08-sim-infra-audit/
# pre_mortem_report.md for the failure narratives.


class TestPreMortem:
    """Pre-mortem regression tests pinning documented silent behaviors."""

    def test_realized_variance_enforces_length_guard(self) -> None:
        """RealizedVarianceCalc enforces ``len(path) == horizon_T + 1`` (CR I-1).

        Replaces the prior pre-mortem #1 (which DOCUMENTED the missing
        cross-check). PRIMITIVES.md (7) defines σ_T over t ∈ {0,…,T} —
        i.e. T+1 samples. A length mismatch is now a hard ValueError.
        """
        rv = RealizedVarianceCalc(
            params=RealizedVarianceParams(horizon_T=100),
            mean_x_over_y=4000.0,
        )
        # Length 50 (instead of 101) — must raise.
        short_path = np.full(50, 4000.0, dtype=np.float64)
        with pytest.raises(ValueError, match="path length must be horizon_T \\+ 1"):
            rv(short_path)
        # Length 102 (T+2) — must also raise.
        long_path = np.full(102, 4000.0, dtype=np.float64)
        with pytest.raises(ValueError, match="path length must be horizon_T \\+ 1"):
            rv(long_path)
        # Length 101 (= T+1) — passes.
        ok_path = np.full(101, 4000.0, dtype=np.float64)
        assert rv(ok_path) == 0.0

    def test_fx_path_gen_propagates_nan_silently(self) -> None:
        """FXPathGen.__call__ propagates NaN in t to NaN in output.

        Pre-mortem #2 (fx_path.py docstring lines 56–60). A future
        defensive ``np.isnan(t).any()`` guard that raises would
        deliberately fail this test. Pins the numpy total-function
        semantics as the contract.
        """
        gen = FXPathGen(
            params=FXPathParams(mean_x_over_y=4000.0, epsilon=0.1, omega=1.0)
        )
        ts = np.array([0.0, np.nan, math.pi], dtype=np.float64)
        out = gen(ts)
        # Index 0 and 2 finite; index 1 is NaN — NOT raised.
        assert math.isfinite(out[0])
        assert np.isnan(out[1])
        assert math.isfinite(out[2])

    def test_truncpareto_alpha_floor_inclusive(self) -> None:
        """α = 1.5 exactly is admitted (inclusive floor).

        Pre-mortem #8. Spec §8(6) is read as ``α >= 1.5``. A future
        change to a strict ``> 1.5`` floor would surface here.
        """
        sampler = TruncParetoSampler(
            params=TruncParetoParams(alpha=1.5, x_m=1.0, x_max=10.0)
        )
        # Construction succeeded; draw to confirm functional sampler.
        out = sampler(size=16, rng=np.random.default_rng(0))
        assert out.shape == (16,)
