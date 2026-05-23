"""Hypothesis input strategies — one per Value type in ``simulations.types``.

These strategies do **not** impose Callable-tier guards (e.g., the SaaS-builder
α ≥ 1.5 floor for ``TruncParetoSampler``). They generate the full Value-tier
admissible region so that the Callable's tier-rejection behavior can itself
be tested. Where helpful, narrowed strategies (e.g., ``saas_truncpareto_params``,
``tight_softplus_params``) are provided as separate composites.

Phase 3.3 ``hypothesis-tests`` skill will extend these with property tests
on the Callable transforms.
"""

from __future__ import annotations

import hypothesis.strategies as st
import numpy as np

from simulations.types.distributions import (
    SAAS_TRUNC_PARETO_ALPHA_CEILING,
    SAAS_TRUNC_PARETO_ALPHA_FLOOR,
    NegBinParams,
    SoftplusParams,
    TruncParetoParams,
)
from simulations.types.fx import BlendedPriceParams, FXPathParams, RealizedVarianceParams
from simulations.types.posterior import MonthlyCDF, PosteriorDraws, ZCapPinned
from simulations.types.tier import (
    SUBSCRIPTION_USD_PER_MONTH,
    TIER_IDS,
    TierID,
    TierPricing,
    TierPrior,
)


# ─── Private helpers ──────────────────────────────────────────────────────────


@st.composite
def _dirichlet_tier_mix(draw: st.DrawFn) -> dict[TierID, float]:
    """Draws a ``dict[TierID, float]`` summing to 1.0 within ``1e-9``.

    Used by :func:`tier_prior` and :func:`zcap_pinned` to satisfy the
    sum-to-one contract on tier-mass mappings. Private (not exported).
    """
    raw = [
        draw(
            st.floats(
                min_value=0.05,
                max_value=0.95,
                allow_nan=False,
                allow_infinity=False,
            )
        )
        for _ in range(len(TIER_IDS))
    ]
    total = sum(raw)
    pi: dict[TierID, float] = {tier: raw[i] / total for i, tier in enumerate(TIER_IDS)}
    # Patch any rounding drift onto the last entry to clear the 1e-9 sum guard.
    drift = 1.0 - sum(pi.values())
    pi[TIER_IDS[-1]] += drift
    return pi


# ─── Distribution-parameter strategies ────────────────────────────────────────


@st.composite
def truncpareto_params(
    draw: st.DrawFn,
    *,
    alpha_min: float = 0.5,
    alpha_max: float = 3.0,
) -> TruncParetoParams:
    """Draw ``TruncParetoParams`` over the **Value-tier** admissible region.

    The default range allows α below the SaaS-builder floor (1.5) so the
    Callable's M1 rejection behavior can be tested.
    """
    alpha = draw(st.floats(min_value=alpha_min, max_value=alpha_max,
                            allow_nan=False, allow_infinity=False, exclude_min=True))
    x_m = draw(st.floats(min_value=1e-3, max_value=1e3,
                         allow_nan=False, allow_infinity=False, exclude_min=True))
    # x_max strictly > x_m
    multiplier = draw(st.floats(min_value=1.001, max_value=100.0,
                                 allow_nan=False, allow_infinity=False))
    return TruncParetoParams(alpha=alpha, x_m=x_m, x_max=x_m * multiplier)


@st.composite
def saas_truncpareto_params(draw: st.DrawFn) -> TruncParetoParams:
    """Draw ``TruncParetoParams`` honoring the SaaS-builder α ≥ 1.5 floor.

    The α-domain is intentionally narrowed to ``α ∈ [1.9, ceiling]`` rather
    than the full sampler-admissible ``α ∈ [1.5, ceiling]``. This reflects
    the 5%-tolerance Monte-Carlo precision floor of
    ``test_truncpareto_sampler_distributional_validity`` (Phase 3.3): with
    ``n=10000`` samples, α near the 1.5 cohort floor produces a heavy enough
    right tail that sample-mean drift can exceed 5% relative tolerance on
    Hypothesis-adversarial seeds (e.g., flakes observed at α=1.515625,
    α=1.701171875, and α=1.75 — Phase 3.4 hotfix). Analytic worst-case
    drift (z=3.29 over n=10000 with x_max/x_m=100) is ≈ 4.6% at α=1.75,
    ≈ 4.1% at α=1.9, and ≈ 3.8% at α=2.0. The 1.9 floor leaves comfortable
    margin under Hypothesis's ``max_examples=50`` × seed-search budget.

    The sampler is correct outside ``[1.9, ceiling]``; the test would need
    ``n >> 10000`` samples for 5% accuracy near α=1.5. Strategy domain is
    therefore narrowed to where the test's tolerance bound is sound,
    analogous to the ``negbin_params`` precedent.

    The α=1.5 sampler-construction refusal (M1) is still tested via the
    Value-tier ``truncpareto_params`` strategy, which permits α < 1.5 to
    drive the rejection-behavior tests.
    """
    # Monte-Carlo precision floor (1.9) is strictly > the M1 floor (1.5),
    # so the assertion below is a guard against constant drift.
    monte_carlo_alpha_min = 1.9
    assert monte_carlo_alpha_min >= SAAS_TRUNC_PARETO_ALPHA_FLOOR
    return draw(
        truncpareto_params(
            alpha_min=monte_carlo_alpha_min,
            alpha_max=SAAS_TRUNC_PARETO_ALPHA_CEILING,
        )
    )


@st.composite
def negbin_params(draw: st.DrawFn) -> NegBinParams:
    """Draw ``NegBinParams`` with ``r ∈ [0.5, 100]`` and ``p ∈ [0.05, 0.95]``.

    This domain restriction reflects the 5%-tolerance Monte-Carlo precision
    floor of ``test_negbin_sampler_distributional_validity`` (Phase 3.3).
    Outside this regime — e.g., ``(r=0.0625, p=0.001)`` — the NegBin
    variance-to-mean ratio ``σ²/μ = 1/p`` blows up faster than ``n=10000``
    samples can validate the sample mean at 5% relative tolerance, causing
    test flakes. The sampler implementation is still correct outside this
    regime; the test would need ``n >> 10000`` samples to assert 5%
    accuracy. Strategy domain is therefore intentionally narrowed to where
    the test's tolerance bound (``max(0.05·μ, 0.5)``) is sound.
    """
    r = draw(st.floats(min_value=0.5, max_value=100.0,
                       allow_nan=False, allow_infinity=False))
    p = draw(st.floats(min_value=0.05, max_value=0.95,
                       allow_nan=False, allow_infinity=False))
    return NegBinParams(r=r, p=p)


@st.composite
def softplus_params(draw: st.DrawFn) -> SoftplusParams:
    """Draw ``SoftplusParams`` over the Value-tier admissible region.

    May produce β values that fail the M2 tightness criterion (so the
    Callable's rejection behavior can be tested).
    """
    beta = draw(st.floats(min_value=1e-2, max_value=1e3,
                          allow_nan=False, allow_infinity=False, exclude_min=True))
    kappa = draw(st.floats(min_value=1e-2, max_value=1e3,
                           allow_nan=False, allow_infinity=False, exclude_min=True))
    return SoftplusParams(beta=beta, kappa=kappa)


@st.composite
def tight_softplus_params(draw: st.DrawFn) -> SoftplusParams:
    """Draw ``SoftplusParams`` whose β passes the M2 tightness criterion.

    Empirically, ``β · κ ≥ 50`` clears the ``deviation < 1e-3 · κ`` bar with
    healthy margin (Pareto floor argument in the regularizers docstring).
    Use a generous floor of ``β ≥ 200/κ`` so the criterion holds across the
    grid-numerical regime.
    """
    kappa = draw(st.floats(min_value=0.1, max_value=10.0,
                           allow_nan=False, allow_infinity=False))
    beta_floor = 200.0 / kappa
    beta = draw(st.floats(min_value=beta_floor, max_value=beta_floor * 10.0,
                          allow_nan=False, allow_infinity=False))
    return SoftplusParams(beta=beta, kappa=kappa)


# ─── Tier strategies ──────────────────────────────────────────────────────────


@st.composite
def tier_prior(draw: st.DrawFn) -> TierPrior:
    """Draw a ``TierPrior`` whose π sums to 1 within ``1e-9``."""
    pi = draw(_dirichlet_tier_mix())
    alpha_0 = draw(st.floats(min_value=1.0, max_value=100.0, allow_nan=False))
    return TierPrior(pi=dict(pi), alpha_0=alpha_0)


@st.composite
def tier_pricing(draw: st.DrawFn) -> TierPricing:
    """Draw ``TierPricing`` near (but not equal to) the spec §5.2 pins."""
    perturbations = draw(
        st.tuples(
            st.floats(min_value=0.5, max_value=2.0, allow_nan=False),
            st.floats(min_value=0.5, max_value=2.0, allow_nan=False),
            st.floats(min_value=0.5, max_value=2.0, allow_nan=False),
        )
    )
    pricing = {
        tier: SUBSCRIPTION_USD_PER_MONTH[tier] * pert
        for tier, pert in zip(TIER_IDS, perturbations)
    }
    return TierPricing(usd_per_month=pricing)


# ─── FX strategies ────────────────────────────────────────────────────────────


@st.composite
def fx_path_params(draw: st.DrawFn) -> FXPathParams:
    """Draw ``FXPathParams`` with ε ∈ (0, 1) per spec §3 / PRIMITIVES (6)."""
    mean_x_over_y = draw(st.floats(min_value=1.0, max_value=1e6,
                                    allow_nan=False, allow_infinity=False,
                                    exclude_min=True))
    epsilon = draw(st.floats(min_value=1e-3, max_value=1.0 - 1e-3,
                              allow_nan=False, allow_infinity=False))
    omega = draw(st.floats(min_value=1e-3, max_value=10.0,
                            allow_nan=False, allow_infinity=False, exclude_min=True))
    return FXPathParams(mean_x_over_y=mean_x_over_y, epsilon=epsilon, omega=omega)


@st.composite
def realized_variance_params(draw: st.DrawFn) -> RealizedVarianceParams:
    """Draw ``RealizedVarianceParams`` with ``horizon_T > 0``."""
    horizon_T = draw(st.integers(min_value=1, max_value=10_000))
    return RealizedVarianceParams(horizon_T=horizon_T)


@st.composite
def blended_price_params(draw: st.DrawFn) -> BlendedPriceParams:
    """Draw ``BlendedPriceParams`` with ``w_in + w_out = 1`` exactly."""
    w_in = draw(st.floats(min_value=0.05, max_value=0.95,
                          allow_nan=False, allow_infinity=False))
    w_out = 1.0 - w_in
    h_cache = draw(st.floats(min_value=0.0, max_value=1.0,
                              allow_nan=False, allow_infinity=False))
    p_in = draw(st.floats(min_value=0.1, max_value=100.0,
                           allow_nan=False, allow_infinity=False))
    p_out = draw(st.floats(min_value=0.1, max_value=200.0,
                            allow_nan=False, allow_infinity=False))
    return BlendedPriceParams(
        w_in=w_in, w_out=w_out, h_cache=h_cache, p_in=p_in, p_out=p_out
    )


# ─── Posterior / emission strategies ──────────────────────────────────────────


@st.composite
def posterior_draws(draw: st.DrawFn) -> PosteriorDraws:
    """Draw a small ``PosteriorDraws`` with shape-consistent metadata."""
    n_params = draw(st.integers(min_value=1, max_value=4))
    n_rows = draw(st.integers(min_value=1, max_value=32))
    seed = draw(st.integers(min_value=0, max_value=2**31 - 1))
    rng = np.random.default_rng(seed)
    arr = rng.normal(size=(n_rows, n_params)).astype(np.float64)
    names = tuple(f"p{i}" for i in range(n_params))
    return PosteriorDraws(draws=arr, param_names=names)


@st.composite
def monthly_cdf(draw: st.DrawFn) -> MonthlyCDF:
    """Draw a four-percentile ``MonthlyCDF`` (p10/p50/p90/p99)."""
    base = draw(st.floats(min_value=10.0, max_value=10_000.0, allow_nan=False))
    # All multipliers ≥ 1 so the resulting CDF values are non-decreasing.
    spreads = draw(
        st.tuples(
            st.floats(min_value=1.0, max_value=2.0, allow_nan=False),
            st.floats(min_value=1.0, max_value=5.0, allow_nan=False),
            st.floats(min_value=1.0, max_value=10.0, allow_nan=False),
        )
    )
    p10 = base
    p50 = base * spreads[0]
    p90 = p50 * spreads[1]
    p99 = p90 * spreads[2]
    return MonthlyCDF(
        percentiles=(10.0, 50.0, 90.0, 99.0),
        values_usd=(p10, p50, p90, p99),
    )


@st.composite
def zcap_pinned(draw: st.DrawFn) -> ZCapPinned:
    """Draw a ``ZCapPinned`` Value with valid sha256 and tier_mix."""
    z = draw(st.floats(min_value=10.0, max_value=1e6, allow_nan=False))
    half_width = draw(st.floats(min_value=0.01 * z, max_value=0.5 * z, allow_nan=False))
    audit_int = draw(st.integers(min_value=0, max_value=2**256 - 1))
    audit_block = f"{audit_int:064x}"
    tier_mix = draw(_dirichlet_tier_mix())
    return ZCapPinned(
        Z_cop_per_month=z,
        ci_95_lo=z - half_width,
        ci_95_hi=z + half_width,
        audit_block=audit_block,
        tier_mix=dict(tier_mix),
    )


# ─── SAAS-COHORT-1 prior strategies ──────────────────────────────────────────
#
# These strategies generate cohort-1 prior hyperparameter Value containers
# for the SAAS-COHORT-1 (T1 subscription-cap regime) PyMC fit. They model
# the spec v1.1.1 §5.1 + §5.2 admissible region — narrowly so cohort
# implementation tests can exercise the M1 / M3 / Dirichlet pins without
# leaking out-of-spec parameters.


@st.composite
def negbin_turns_prior(draw: st.DrawFn):
    """Draw a ``NegBinTurnsPrior`` (cohort-1) consistent with spec §5.2.

    Constraints (read off priors.py:NegBinTurnsPrior.__post_init__):

    - ``mu_loc`` strictly positive; constrained near μ ≈ 80.
    - ``phi_loc`` strictly positive; pinned near φ ≈ 60 (over-disp 2.3×).
    - ``mu_log_sigma`` and ``phi_sigma`` strictly positive.
    """
    from simulations.saas_builder.priors import NegBinTurnsPrior

    mu_loc = draw(st.floats(min_value=20.0, max_value=200.0, allow_nan=False))
    mu_log_sigma = draw(
        st.floats(min_value=0.05, max_value=1.0, allow_nan=False)
    )
    phi_loc = draw(st.floats(min_value=10.0, max_value=200.0, allow_nan=False))
    phi_sigma = draw(
        st.floats(min_value=1.0, max_value=50.0, allow_nan=False)
    )
    return NegBinTurnsPrior(
        mu_loc=mu_loc,
        mu_log_sigma=mu_log_sigma,
        phi_loc=phi_loc,
        phi_sigma=phi_sigma,
    )


@st.composite
def truncpareto_alpha_prior(draw: st.DrawFn):
    """Draw a ``TruncParetoAlphaPrior`` honoring the M1 floor [1.5, 2.5].

    Constraints (read off priors.py:TruncParetoAlphaPrior.__post_init__):

    - ``alpha_lower`` ≥ 1.5 and ``alpha_upper`` ≤ 2.5.
    - ``alpha_lower < alpha_upper``.
    - ``alpha_loc`` ∈ ``(alpha_lower, alpha_upper)``.
    - ``alpha_scale`` strictly positive.
    """
    from simulations.saas_builder.priors import TruncParetoAlphaPrior

    lower = draw(st.floats(min_value=1.5, max_value=1.7, allow_nan=False))
    upper = draw(st.floats(min_value=2.3, max_value=2.5, allow_nan=False))
    loc = draw(
        st.floats(
            min_value=lower + 0.01,
            max_value=upper - 0.01,
            allow_nan=False,
        )
    )
    scale = draw(st.floats(min_value=0.05, max_value=0.5, allow_nan=False))
    return TruncParetoAlphaPrior(
        alpha_loc=loc,
        alpha_scale=scale,
        alpha_lower=lower,
        alpha_upper=upper,
    )


# ─── dev_ai_cost_v2 strategies ───────────────────────────────────────────────
#
# Strategies for ``simulations.dev_ai_cost_v2.types`` value containers.
# Spec ref: docs/specs/2026-05-16-ai-cost-factor-model-design.md v0.2.1 §3.5.
# Sibling spec: docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md
# v0.1.3 CORRECTIONS-RR/-TT — ``MessageRecord.uuid`` required non-empty.


@st.composite
def message_records(draw: st.DrawFn):
    """Draw a ``MessageRecord`` over the Value-tier admissible region.

    All token fields are non-negative (``MessageRecord.__post_init__`` would
    otherwise reject). ``ts`` is timezone-aware UTC. ``uuid`` is non-empty
    per R6 v0.1.3 CORRECTIONS-RR/-TT (used as pool-canonicalization sort
    key tiebreaker).

    CORRECTIONS-Y-2 (v0.2.3): ``cost_usd_notional`` is ``float`` (ccusage
    parity); bounded at 1000.0 for shrinking tractability.
    """
    from datetime import datetime as _dt
    from datetime import timezone as _tz

    from simulations.dev_ai_cost_v2.types import MessageRecord

    naive = draw(
        st.datetimes(
            min_value=_dt(2024, 1, 1),
            max_value=_dt(2027, 1, 1),
        )
    )
    ts = naive.replace(tzinfo=_tz.utc)
    model = draw(
        st.sampled_from(
            ["claude-sonnet-4-5", "claude-haiku-4-5", "claude-opus-4-7"]
        )
    )
    input_tok = draw(st.integers(min_value=0, max_value=10**6))
    output_tok = draw(st.integers(min_value=0, max_value=10**6))
    cache_create_5m = draw(st.integers(min_value=0, max_value=10**6))
    cache_create_1h = draw(st.integers(min_value=0, max_value=10**6))
    cache_read = draw(st.integers(min_value=0, max_value=10**6))
    cost_usd_notional = draw(
        st.floats(
            min_value=0.0,
            max_value=1000.0,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    session_id = draw(st.text(min_size=1, max_size=64))
    request_id = draw(st.one_of(st.none(), st.text(min_size=1, max_size=64)))
    is_error = draw(st.booleans())
    # Y-5e: uuid may emit synth-sha256: prefix or arbitrary string. The
    # MessageRecord contract still rejects empty strings (R6 dedupe), so
    # draw a non-empty string here; synthesis is exercised at jsonl_io's
    # boundary, not at the MessageRecord level.
    uuid = draw(st.text(min_size=1, max_size=64))
    return MessageRecord(
        ts=ts,
        model=model,
        input_tok=input_tok,
        output_tok=output_tok,
        cache_create_5m=cache_create_5m,
        cache_create_1h=cache_create_1h,
        cache_read=cache_read,
        cost_usd_notional=cost_usd_notional,
        session_id=session_id,
        request_id=request_id,
        is_error=is_error,
        uuid=uuid,
    )


__all__ = [
    "truncpareto_params",
    "saas_truncpareto_params",
    "negbin_params",
    "softplus_params",
    "tight_softplus_params",
    "tier_prior",
    "tier_pricing",
    "fx_path_params",
    "realized_variance_params",
    "blended_price_params",
    "posterior_draws",
    "monthly_cdf",
    "zcap_pinned",
    "negbin_turns_prior",
    "truncpareto_alpha_prior",
    "message_records",
]
