"""Value-tier unit tests for ``simulations.types``.

Asserts the validation invariants documented in each Value type's
``__post_init__``: finite-positive enforcement, bounded-interval guards,
``Mapping`` shape requirements, and the ``ZCapPinned.audit_block`` regex.

Hypothesis property tests for downstream Callables live in
``test_modules.py`` and will be extended in Phase 3.3.
"""

from __future__ import annotations

import math
from typing import Any, cast

import numpy as np
import pytest
from hypothesis import given

from simulations.tests import strategies as S
from simulations.types.distributions import (
    NegBinParams,
    SoftplusParams,
    TruncParetoParams,
    neg_bin_mean,
    neg_bin_variance,
    tightness_l1_deviation,
    trunc_pareto_admits_saas_floor,
)
from simulations.types.fx import (
    BlendedPriceParams,
    FXPathParams,
    RealizedVarianceParams,
    fx_amplitude_envelope,
)
from simulations.types.posterior import (
    MonthlyCDF,
    PosteriorDraws,
    ZCapPinned,
    cdf_percentile_value,
    ci_95_width,
    n_total_draws,
    parameter_index,
)
from simulations.types.tier import (
    SUBSCRIPTION_USD_PER_MONTH,
    TIER_IDS,
    TierPricing,
    TierPrior,
    categorical_mass,
)


# ─── TruncParetoParams ────────────────────────────────────────────────────────


class TestTruncParetoParams:
    @pytest.mark.parametrize("alpha", [0.0, -1.0, math.inf, -math.inf, math.nan])
    def test_rejects_non_finite_positive_alpha(self, alpha: float) -> None:
        """alpha must be finite and strictly positive."""
        with pytest.raises(ValueError, match="alpha"):
            TruncParetoParams(alpha=alpha, x_m=1.0, x_max=10.0)

    @pytest.mark.parametrize("x_m", [0.0, -0.5, math.inf, math.nan])
    def test_rejects_bad_x_m(self, x_m: float) -> None:
        """x_m must be finite and strictly positive."""
        with pytest.raises(ValueError, match="x_m"):
            TruncParetoParams(alpha=2.0, x_m=x_m, x_max=10.0)

    @pytest.mark.parametrize("x_max", [0.5, 1.0, math.inf, math.nan, -3.0])
    def test_rejects_bad_x_max(self, x_max: float) -> None:
        """x_max must be finite-positive AND strictly greater than x_m=1.0."""
        with pytest.raises(ValueError, match="x_max"):
            TruncParetoParams(alpha=2.0, x_m=1.0, x_max=x_max)

    def test_accepts_valid_below_saas_floor(self) -> None:
        """Value tier accepts α=1.0 < SaaS floor (1.5); sampler enforces floor."""
        p = TruncParetoParams(alpha=1.0, x_m=1.0, x_max=10.0)
        assert p.alpha == 1.0
        assert trunc_pareto_admits_saas_floor(p) is False

    def test_admits_saas_floor_helper(self) -> None:
        """trunc_pareto_admits_saas_floor returns True for α ≥ 1.5."""
        p = TruncParetoParams(alpha=1.5, x_m=1.0, x_max=10.0)
        assert trunc_pareto_admits_saas_floor(p) is True


# ─── NegBinParams ─────────────────────────────────────────────────────────────


class TestNegBinParams:
    @pytest.mark.parametrize("r", [0.0, -1.0, math.inf, math.nan])
    def test_rejects_bad_r(self, r: float) -> None:
        """r must be finite and strictly positive."""
        with pytest.raises(ValueError, match="r"):
            NegBinParams(r=r, p=0.5)

    @pytest.mark.parametrize("p", [0.0, 1.0, -0.1, 1.1, math.inf, math.nan])
    def test_rejects_p_outside_open_unit(self, p: float) -> None:
        """p must lie strictly inside (0, 1); endpoints rejected."""
        with pytest.raises(ValueError, match=r"\(0, 1\)"):
            NegBinParams(r=2.0, p=p)

    def test_mean_and_variance_accessors(self) -> None:
        """neg_bin_mean / variance return r(1-p)/p and r(1-p)/p²."""
        params = NegBinParams(r=4.0, p=0.5)
        assert math.isclose(neg_bin_mean(params), 4.0)
        assert math.isclose(neg_bin_variance(params), 8.0)


# ─── SoftplusParams ───────────────────────────────────────────────────────────


class TestSoftplusParams:
    @pytest.mark.parametrize("beta", [0.0, -1.0, math.inf, math.nan])
    def test_rejects_bad_beta(self, beta: float) -> None:
        """beta must be finite and strictly positive at the Value tier."""
        with pytest.raises(ValueError, match="beta"):
            SoftplusParams(beta=beta, kappa=1.0)

    @pytest.mark.parametrize("kappa", [0.0, -2.0, math.inf, math.nan])
    def test_rejects_bad_kappa(self, kappa: float) -> None:
        """kappa must be finite and strictly positive."""
        with pytest.raises(ValueError, match="kappa"):
            SoftplusParams(beta=1.0, kappa=kappa)

    def test_tightness_deviation_decreases_with_beta(self) -> None:
        """L¹ deviation from ReLU monotonically tightens as β grows."""
        loose = SoftplusParams(beta=1.0, kappa=1.0)
        tight = SoftplusParams(beta=100.0, kappa=1.0)
        assert tightness_l1_deviation(loose) > tightness_l1_deviation(tight)

    def test_tightness_l1_grid_floor(self) -> None:
        """tightness_l1_deviation refuses n_grid < 2."""
        with pytest.raises(ValueError, match="n_grid"):
            tightness_l1_deviation(SoftplusParams(beta=10.0, kappa=1.0), n_grid=1)

    def test_tightness_l1_grid_floor_accepts_two(self) -> None:
        """``n_grid == 2`` is the boundary case — must be accepted, not rejected."""
        # Boundary: predicate is ``n_grid < 2``; n_grid=2 must pass.
        result = tightness_l1_deviation(SoftplusParams(beta=10.0, kappa=1.0), n_grid=2)
        assert math.isfinite(result)
        assert result >= 0.0

    def test_tightness_l1_known_value(self) -> None:
        """Pinned numerical value at β=10, κ=1, n_grid=257.

        Catches mutations to the integration grid bounds (``np.linspace``
        endpoints), the shift offset (``xs - κ`` vs ``xs + κ``), the
        softplus formula sign, and the ``2*κ`` upper bound. The trapezoid
        integral over [0, 2κ]=[0,2] with β=10 is ≈ 0.01645 (verified against
        unmutated implementation; pinned with ±5% tolerance).
        """
        result = tightness_l1_deviation(
            SoftplusParams(beta=10.0, kappa=1.0), n_grid=257
        )
        assert 0.0156 < result < 0.0173, f"deviation {result} outside expected band"

    def test_tightness_l1_deviation_default_n_grid_high_precision(self) -> None:
        """tightness_l1_deviation default n_grid (4096) yields high-precision result.

        Kills mutmut L1_13: dropping the ``n_grid`` argument from
        ``np.linspace(0.0, 2.0 * kappa, n_grid)`` defaults the linspace
        ``num`` to 50, producing ~6.9e-5 absolute drift versus the
        4096-node grid at β=10, κ=1.

        The expected value is pinned against an INDEPENDENT high-precision
        reference (computed externally with n=8192: 0.016448430195608172).
        We do NOT call ``tightness_l1_deviation`` with ``n_grid=8192`` to
        derive the reference, because under the L1_13 mutation that call
        also collapses to n=50 — masking the drift. The pinned literal
        is the load-bearing kill condition.

        Tolerance ±2e-5 is tight enough to surface the n=50 drift
        (~6.9e-5) while remaining stable across numpy/BLAS variation.
        """
        params = SoftplusParams(beta=10.0, kappa=1.0)
        result = tightness_l1_deviation(params)  # uses default n_grid (4096)
        # Independent reference (computed offline at n=8192). Do NOT replace
        # with a function call — the mutation we kill makes the function
        # ignore n_grid, which would equate result and any "reference" call.
        expected_8192 = 0.016448430195608172
        assert abs(result - expected_8192) < 2e-5, (
            f"default n_grid (4096) drifted from pinned 8192-node reference:"
            f" {result=} vs {expected_8192=}; |Δ|={abs(result - expected_8192)}"
            f" — likely L1_13 mutation (n_grid dropped, defaulting linspace"
            f" to 50 nodes)."
        )

    def test_tightness_l1_nonnegative(self) -> None:
        """L¹ deviation is non-negative — catches sign-flip mutations on softplus."""
        for beta in (1.0, 5.0, 50.0):
            d = tightness_l1_deviation(SoftplusParams(beta=beta, kappa=1.0))
            assert d >= 0.0, f"negative deviation {d} at β={beta}"

    def test_tightness_l1_scales_linearly_with_kappa_at_fixed_beta(self) -> None:
        """L¹ deviation scales linearly with κ when β is fixed.

        Substituting u = x - κ in ∫₀^{2κ}|softplus_β(x−κ) − (x−κ)^+|dx gives
        ∫_{-κ}^{κ}|softplus_β(u) − u^+|du. For β·κ ≫ 1 the integrand is
        concentrated near u=0 and the integral saturates, but for moderate
        β·κ the integral roughly doubles when κ doubles at fixed β. Catches
        mutations that drop κ from the integration bounds (e.g.
        ``np.linspace(0.0, 2.0, n)`` vs ``np.linspace(0.0, 2.0*κ, n)``) by
        checking the LARGER-κ deviation strictly exceeds the smaller.
        """
        # Use β=1 (loose regime) where integrand spans the full [-κ, κ] window.
        d1 = tightness_l1_deviation(SoftplusParams(beta=1.0, kappa=1.0))
        d2 = tightness_l1_deviation(SoftplusParams(beta=1.0, kappa=2.0))
        # Doubling κ widens the integration window — d2 strictly exceeds d1.
        assert d2 > d1, f"d2 ({d2}) should exceed d1 ({d1}) when κ doubles"
        # Substantial growth: catches mutations that drop κ from the bounds.
        assert d2 > 1.3 * d1, f"d2/d1 = {d2/d1} is suspiciously low; κ scaling broken?"

    def test_tightness_l1_decreases_to_zero_at_high_beta(self) -> None:
        """As β → ∞ the L¹ deviation → 0 (softplus_β → ReLU).

        At β=50/κ the deviation must be well below 1e-3·κ (the spec
        criterion). Catches mutations that prevent convergence (wrong
        shift sign, wrong upper bound).
        """
        d = tightness_l1_deviation(SoftplusParams(beta=50.0, kappa=1.0))
        # Spec criterion: deviation < SOFTPLUS_TIGHTNESS_EPS·κ = 1e-3·1.0
        assert d < 1e-3, f"β=50, κ=1: deviation {d} should be < 1e-3"


# ─── FX types ─────────────────────────────────────────────────────────────────


class TestFXPathParams:
    @pytest.mark.parametrize("epsilon", [0.0, 1.0, -0.1, 1.5, math.inf, math.nan])
    def test_rejects_epsilon_outside_open_unit(self, epsilon: float) -> None:
        """epsilon must lie strictly inside (0, 1); endpoints rejected."""
        with pytest.raises(ValueError, match=r"\(0, 1\)"):
            FXPathParams(mean_x_over_y=4000.0, epsilon=epsilon, omega=1.0)

    @pytest.mark.parametrize("mean", [0.0, -1.0, math.inf, math.nan])
    def test_rejects_bad_mean(self, mean: float) -> None:
        """mean_x_over_y must be finite and strictly positive."""
        with pytest.raises(ValueError, match="mean_x_over_y"):
            FXPathParams(mean_x_over_y=mean, epsilon=0.1, omega=1.0)

    def test_amplitude_envelope_accessor(self) -> None:
        """fx_amplitude_envelope returns mean·(1±ε/2) bounds."""
        p = FXPathParams(mean_x_over_y=4000.0, epsilon=0.1, omega=1.0)
        lo, hi = fx_amplitude_envelope(p)
        assert math.isclose(lo, 4000.0 * 0.95)
        assert math.isclose(hi, 4000.0 * 1.05)


class TestRealizedVarianceParams:
    @pytest.mark.parametrize("T", [0, -1, -100])
    def test_rejects_non_positive_horizon(self, T: int) -> None:
        """horizon_T must be strictly positive."""
        with pytest.raises(ValueError, match="horizon_T"):
            RealizedVarianceParams(horizon_T=T)


class TestBlendedPriceParams:
    def test_weights_must_sum_to_one(self) -> None:
        """w_in + w_out must equal 1 within 1e-12."""
        with pytest.raises(ValueError, match="must equal 1"):
            BlendedPriceParams(w_in=0.5, w_out=0.4, h_cache=0.5, p_in=3.0, p_out=15.0)

    @pytest.mark.parametrize("w_in", [0.0, 1.0, -0.1, 1.1])
    def test_rejects_w_in_endpoints(self, w_in: float) -> None:
        """w_in must lie strictly inside (0, 1)."""
        with pytest.raises(ValueError, match=r"\(0, 1\)|w_in"):
            BlendedPriceParams(
                w_in=w_in, w_out=1.0 - w_in, h_cache=0.5, p_in=3.0, p_out=15.0
            )

    @pytest.mark.parametrize("h", [-0.1, 1.1, math.inf, math.nan])
    def test_rejects_h_cache_outside_unit(self, h: float) -> None:
        """h_cache must lie in [0, 1]."""
        with pytest.raises(ValueError, match="h_cache"):
            BlendedPriceParams(w_in=0.5, w_out=0.5, h_cache=h, p_in=3.0, p_out=15.0)

    def test_h_cache_endpoints_accepted(self) -> None:
        """h_cache=0 and h_cache=1 are admissible (closed interval)."""
        BlendedPriceParams(w_in=0.5, w_out=0.5, h_cache=0.0, p_in=3.0, p_out=15.0)
        BlendedPriceParams(w_in=0.5, w_out=0.5, h_cache=1.0, p_in=3.0, p_out=15.0)


# ─── Tier types ───────────────────────────────────────────────────────────────


class TestTierPrior:
    def test_pi_must_be_mapping(self) -> None:
        """A list-of-pairs is rejected with TypeError (not AttributeError)."""
        pairs: list[tuple[str, float]] = [
            ("pro", 0.2),
            ("max_5x", 0.5),
            ("max_20x", 0.3),
        ]
        with pytest.raises(TypeError, match="Mapping"):
            TierPrior(pi=cast(Any, pairs))

    def test_keys_must_match_tier_ids(self) -> None:
        """Missing or extra keys are rejected."""
        with pytest.raises(ValueError, match="exactly"):
            TierPrior(pi=cast(Any, {"pro": 0.5, "max_5x": 0.5}))

    def test_pi_must_sum_to_one(self) -> None:
        """π values must sum to 1 within 1e-9."""
        with pytest.raises(ValueError, match="sum to 1"):
            TierPrior(pi={"pro": 0.1, "max_5x": 0.1, "max_20x": 0.1})

    @pytest.mark.parametrize("v", [0.0, -0.1, 1.5])
    def test_pi_values_must_lie_in_open_unit(self, v: float) -> None:
        """π values must lie in (0, 1]; 0 and >1 rejected."""
        with pytest.raises(ValueError, match=r"\(0, 1\]"):
            TierPrior(pi={"pro": v, "max_5x": 0.5, "max_20x": 1.0 - 0.5 - v})

    def test_alpha_0_must_be_positive(self) -> None:
        """alpha_0 must be finite and strictly positive."""
        with pytest.raises(ValueError, match="alpha_0"):
            TierPrior(alpha_0=0.0)

    def test_categorical_mass_accessor(self) -> None:
        """categorical_mass returns π[tier] from the prior."""
        prior = TierPrior()
        assert categorical_mass(prior, "max_5x") == 0.5


class TestTierPricing:
    def test_must_be_mapping(self) -> None:
        """A list-of-pairs is rejected with TypeError."""
        pairs: list[tuple[str, float]] = [
            ("pro", 20.0),
            ("max_5x", 100.0),
            ("max_20x", 200.0),
        ]
        with pytest.raises(TypeError, match="Mapping"):
            TierPricing(usd_per_month=cast(Any, pairs))

    def test_default_matches_spec(self) -> None:
        """Default TierPricing matches spec §5.2 pins."""
        pricing = TierPricing()
        for tier in TIER_IDS:
            assert pricing.usd_per_month[tier] == SUBSCRIPTION_USD_PER_MONTH[tier]

    def test_rejects_non_positive_price(self) -> None:
        """Per-tier USD/mo must be finite and strictly positive."""
        with pytest.raises(ValueError, match="usd_per_month"):
            TierPricing(usd_per_month={"pro": 0.0, "max_5x": 100.0, "max_20x": 200.0})


# ─── Posterior types ─────────────────────────────────────────────────────────


class TestPosteriorDraws:
    def test_rejects_one_dimensional(self) -> None:
        """draws.ndim must equal 2."""
        with pytest.raises(ValueError, match="ndim"):
            PosteriorDraws(
                draws=np.zeros(8, dtype=np.float64),
                param_names=("p0",),
            )

    def test_rejects_shape_param_mismatch(self) -> None:
        """draws.shape[1] must equal len(param_names)."""
        with pytest.raises(ValueError, match="param_names"):
            PosteriorDraws(
                draws=np.zeros((4, 2), dtype=np.float64),
                param_names=("p0",),
            )

    def test_rejects_duplicate_param_names(self) -> None:
        """param_names must be unique."""
        with pytest.raises(ValueError, match="duplicate"):
            PosteriorDraws(
                draws=np.zeros((4, 2), dtype=np.float64),
                param_names=("p0", "p0"),
            )

    def test_n_total_draws_and_index(self) -> None:
        """n_total_draws and parameter_index helpers behave."""
        d = PosteriorDraws(
            draws=np.arange(12, dtype=np.float64).reshape(4, 3),
            param_names=("a", "b", "c"),
        )
        assert n_total_draws(d) == 4
        assert parameter_index(d, "b") == 1
        with pytest.raises(ValueError, match="no parameter"):
            parameter_index(d, "z")


class TestMonthlyCDF:
    def test_rejects_length_mismatch(self) -> None:
        """percentiles and values_usd must have equal length."""
        with pytest.raises(ValueError, match="equal length"):
            MonthlyCDF(percentiles=(10.0, 50.0), values_usd=(1.0,))

    @pytest.mark.parametrize("q", [0.0, 100.0, -10.0, 110.0])
    def test_rejects_percentile_endpoints(self, q: float) -> None:
        """percentiles must lie strictly inside (0, 100)."""
        with pytest.raises(ValueError, match=r"\(0, 100\)"):
            MonthlyCDF(percentiles=(q,), values_usd=(1.0,))

    def test_rejects_non_increasing_percentiles(self) -> None:
        """percentiles must be strictly increasing."""
        with pytest.raises(ValueError, match="strictly increasing"):
            MonthlyCDF(percentiles=(50.0, 10.0), values_usd=(1.0, 2.0))

    def test_rejects_decreasing_values(self) -> None:
        """values_usd must be non-decreasing."""
        with pytest.raises(ValueError, match="non-decreasing"):
            MonthlyCDF(percentiles=(10.0, 50.0), values_usd=(5.0, 1.0))

    def test_rejects_negative_values_usd(self) -> None:
        """MonthlyCDF rejects any negative entry in values_usd (posterior.py:158)."""
        with pytest.raises(ValueError, match="≥ 0"):
            MonthlyCDF(percentiles=(50.0,), values_usd=(-1.0,))

    @pytest.mark.parametrize("c", ["EUR", "usd", "", "BTC"])
    def test_rejects_unknown_currency(self, c: str) -> None:
        """MonthlyCDF rejects currencies not in the whitelist (posterior.py:167)."""
        with pytest.raises(ValueError, match="currency"):
            MonthlyCDF(percentiles=(50.0,), values_usd=(1.0,), currency=c)

    def test_rejects_empty_percentiles(self) -> None:
        """MonthlyCDF rejects empty percentiles tuple (posterior.py:145)."""
        with pytest.raises(ValueError, match="non-empty"):
            MonthlyCDF(percentiles=(), values_usd=())

    def test_cdf_percentile_value_lookup_and_miss(self) -> None:
        """cdf_percentile_value returns pinned percentile or raises ValueError."""
        cdf = MonthlyCDF(percentiles=(10.0, 50.0), values_usd=(1.0, 5.0))
        assert cdf_percentile_value(cdf, 50.0) == 5.0
        with pytest.raises(ValueError, match="no pinned percentile"):
            cdf_percentile_value(cdf, 90.0)


@pytest.fixture
def valid_zcap_kwargs() -> dict[str, Any]:
    """Known-valid kwargs for ZCapPinned; tests mutate one field at a time."""
    return {
        "Z_cop_per_month": 100.0,
        "ci_95_lo": 90.0,
        "ci_95_hi": 110.0,
        "audit_block": "0" * 64,
        "tier_mix": {"pro": 0.2, "max_5x": 0.5, "max_20x": 0.3},
    }


class TestZCapPinned:
    def _valid_block(self) -> str:
        return "0" * 64

    def test_accepts_small_positive_values(self) -> None:
        """Values in (0, 1] are valid — predicate is ``> 0``, not ``> 1``.

        Catches mutations that change ``x > 0.0`` to ``x > 1.0`` in the
        ``_is_finite_positive`` predicate.
        """
        # All three Z fields strictly between 0 and 1 — must construct cleanly.
        z = ZCapPinned(
            Z_cop_per_month=0.5,
            ci_95_lo=0.4,
            ci_95_hi=0.6,
            audit_block="0" * 64,
        )
        assert z.Z_cop_per_month == 0.5
        assert z.ci_95_lo == 0.4
        assert z.ci_95_hi == 0.6

    def test_rejects_audit_block_wrong_length(self) -> None:
        """audit_block must be exactly 64 chars."""
        with pytest.raises(ValueError, match="64 lowercase hex"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=90.0,
                ci_95_hi=110.0,
                audit_block="abc",
            )

    def test_rejects_audit_block_uppercase_hex(self) -> None:
        """audit_block must be lowercase hex."""
        with pytest.raises(ValueError, match="64 lowercase hex"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=90.0,
                ci_95_hi=110.0,
                audit_block="A" * 64,
            )

    def test_rejects_audit_block_non_hex(self) -> None:
        """audit_block must contain only [0-9a-f]."""
        with pytest.raises(ValueError, match="64 lowercase hex"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=90.0,
                ci_95_hi=110.0,
                audit_block="g" * 64,
            )

    def test_rejects_audit_block_with_whitespace(self) -> None:
        """audit_block must not contain leading/trailing whitespace."""
        with pytest.raises(ValueError, match="64 lowercase hex"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=90.0,
                ci_95_hi=110.0,
                audit_block=" " + "0" * 63,
            )

    def test_rejects_ci_inversion(self) -> None:
        """ci_95_lo ≤ Z_cop_per_month ≤ ci_95_hi must hold."""
        with pytest.raises(ValueError, match="ci_95_lo"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=120.0,
                ci_95_hi=130.0,
                audit_block=self._valid_block(),
            )

    def test_tier_mix_must_be_mapping(self) -> None:
        """A list-of-pairs as tier_mix triggers TypeError, not AttributeError."""
        pairs: list[tuple[str, float]] = [
            ("pro", 0.2),
            ("max_5x", 0.5),
            ("max_20x", 0.3),
        ]
        with pytest.raises(TypeError, match="Mapping"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=90.0,
                ci_95_hi=110.0,
                audit_block=self._valid_block(),
                tier_mix=cast(Any, pairs),
            )

    def test_ci_95_width_accessor(self) -> None:
        """ci_95_width returns hi - lo."""
        z = ZCapPinned(
            Z_cop_per_month=100.0,
            ci_95_lo=90.0,
            ci_95_hi=110.0,
            audit_block=self._valid_block(),
        )
        assert math.isclose(ci_95_width(z), 20.0)

    @pytest.mark.parametrize(
        ("field", "bad"),
        [
            ("Z_cop_per_month", math.nan),
            ("Z_cop_per_month", math.inf),
            ("Z_cop_per_month", 0.0),
            ("Z_cop_per_month", -1.0),
            ("ci_95_lo", math.nan),
            ("ci_95_lo", math.inf),
            ("ci_95_lo", 0.0),
            ("ci_95_lo", -1.0),
            ("ci_95_hi", math.nan),
            ("ci_95_hi", math.inf),
            ("ci_95_hi", 0.0),
            ("ci_95_hi", -1.0),
        ],
    )
    def test_rejects_non_finite_or_non_positive_numeric_field(
        self, field: str, bad: float, valid_zcap_kwargs: dict[str, Any]
    ) -> None:
        """ZCapPinned rejects non-finite/non-positive values per field independently.

        The positivity / finiteness guard fires before the ci-inversion guard
        for every (field, bad) combination listed, so a bare ``ValueError``
        match suffices.
        """
        kwargs = dict(valid_zcap_kwargs)
        kwargs[field] = bad
        with pytest.raises(ValueError):
            ZCapPinned(**kwargs)

    def test_rejects_empty_schema_version(
        self, valid_zcap_kwargs: dict[str, Any]
    ) -> None:
        """ZCapPinned rejects empty schema_version string (posterior.py:250)."""
        kwargs = dict(valid_zcap_kwargs)
        kwargs["schema_version"] = ""
        with pytest.raises(ValueError, match="schema_version"):
            ZCapPinned(**kwargs)


# ─── Hypothesis sanity over strategies ────────────────────────────────────────


class TestStrategiesSanity:
    """Smoke tests that each strategy yields constructible Values."""

    @given(S.truncpareto_params())
    def test_truncpareto_strategy_constructs(self, p: TruncParetoParams) -> None:
        """truncpareto_params yields valid Value-tier params."""
        assert p.x_max > p.x_m > 0
        assert p.alpha > 0

    @given(S.saas_truncpareto_params())
    def test_saas_truncpareto_respects_floor(self, p: TruncParetoParams) -> None:
        """saas_truncpareto_params draws α ≥ 1.5 (SaaS floor)."""
        assert p.alpha >= 1.5

    @given(S.negbin_params())
    def test_negbin_strategy(self, p: NegBinParams) -> None:
        """negbin_params yields valid Value-tier params."""
        assert p.r > 0 and 0 < p.p < 1

    @given(S.softplus_params())
    def test_softplus_strategy(self, p: SoftplusParams) -> None:
        """softplus_params yields valid Value-tier params."""
        assert p.beta > 0 and p.kappa > 0

    @given(S.fx_path_params())
    def test_fx_path_strategy(self, p: FXPathParams) -> None:
        """fx_path_params yields ε in (0, 1)."""
        assert 0 < p.epsilon < 1

    @given(S.blended_price_params())
    def test_blended_strategy_sums_to_one(self, p: BlendedPriceParams) -> None:
        """blended_price_params yields w_in + w_out = 1 within 1e-12."""
        assert abs(p.w_in + p.w_out - 1.0) <= 1e-12

    @given(S.tier_prior())
    def test_tier_prior_sums_to_one(self, prior: TierPrior) -> None:
        """tier_prior yields π summing to 1 within 1e-9."""
        assert abs(sum(prior.pi.values()) - 1.0) <= 1e-9

    @given(S.tier_pricing())
    def test_tier_pricing_strategy(self, pricing: TierPricing) -> None:
        """tier_pricing yields strictly-positive USD/mo per tier."""
        for v in pricing.usd_per_month.values():
            assert v > 0

    @given(S.posterior_draws())
    def test_posterior_draws_strategy(self, d: PosteriorDraws) -> None:
        """posterior_draws yields shape-consistent containers."""
        assert d.draws.shape[1] == len(d.param_names)

    @given(S.monthly_cdf())
    def test_monthly_cdf_strategy(self, cdf: MonthlyCDF) -> None:
        """monthly_cdf yields strictly-increasing percentiles + non-decreasing values."""
        assert all(
            cdf.percentiles[i] < cdf.percentiles[i + 1]
            for i in range(len(cdf.percentiles) - 1)
        )

    @given(S.zcap_pinned())
    def test_zcap_pinned_strategy(self, z: ZCapPinned) -> None:
        """zcap_pinned yields a 64-char lowercase hex audit_block."""
        assert len(z.audit_block) == 64
        assert all(c in "0123456789abcdef" for c in z.audit_block)


