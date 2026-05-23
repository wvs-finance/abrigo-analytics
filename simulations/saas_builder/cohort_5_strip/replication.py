r"""Carr-Madan replication-envelope verification for the 3-condor strip.

The strip is a discrete approximation to the continuous Carr-Madan
variance-replicating integral (PRIMITIVES.md §10 eq. 18). The continuous
form replicates the log-contract — a twice-differentiable payoff whose
second derivative is exactly ``2/K²`` — which is the canonical
variance proxy at the terminal spot ``S_T``.

This module verifies two properties of the emitted strip:

1. **Long-vol convexity (Pin S5).** The strip payoff is convex in
   ``S_T``: the value at the body midpoint ``S_0`` is a local minimum
   relative to values at the outer wings of each condor. This is the
   long-vol signature required by the LP (a_l) side of the CPO market.

2. **Log-contract envelope (Pin S6).** After CENTERING the strip
   (subtracting ``Π_strip(S_0)`` — the constant payoff floor coming
   from the off-center condors' capped wings at spot), the residual
   tracks the log-contract proxy
   ``Q(S_T) = -2·log(S_T/S_0) + 2·(S_T-S_0)/S_0`` up to a single
   best-fit scale factor ``β``, with max relative residual ≤
   :data:`REPLICATION_REL_TOL` (default 5% per PRIMITIVES.md §12 row 2).
   The constant floor is absorbed by the LP's collateral at S_0; the
   convex excess is what the CPO buyer pays for via the streamed
   premium π(t).

NO IO at this tier. All functions are pure with respect to inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from simulations.saas_builder.cohort_5_strip._errors import (
    ReplicationToleranceError,
)
from simulations.saas_builder.cohort_5_strip.types import (
    REPLICATION_REL_TOL,
    IronCondor,
    IronCondorStrip,
    ReplicationVerdict,
)


def condor_payoff(condor: IronCondor, s_t: float) -> float:
    r"""Reverse-IC payoff at terminal spot ``s_t`` (long-vol convention).

    .. math::

        P(S_T) = -\max(K_1-S_T, 0) + \max(K_2-S_T, 0)
                 + \max(S_T-K_3, 0) - \max(S_T-K_4, 0)

    Sign breakdown per :data:`LEG_KIND_ORDER`:

    - SHORT put @ K_1: ``-max(K_1 - S_T, 0)``
    - LONG  put @ K_2: ``+max(K_2 - S_T, 0)``
    - LONG  call @ K_3: ``+max(S_T - K_3, 0)``
    - SHORT call @ K_4: ``-max(S_T - K_4, 0)``

    Payoff is zero in the inner body ``[K_2, K_3]``, positive in the
    wings ``(K_1, K_2)`` and ``(K_3, K_4)``, and CAPPED at the constants
    ``K_2 - K_1`` (deep down) and ``K_4 - K_3`` (deep up).
    """
    if not math.isfinite(s_t):
        raise ValueError(f"condor_payoff: s_t = {s_t} must be finite")
    k_1, k_2, k_3, k_4 = (leg.strike for leg in condor.legs)
    short_put_k1 = -max(k_1 - s_t, 0.0)
    long_put_k2 = max(k_2 - s_t, 0.0)
    long_call_k3 = max(s_t - k_3, 0.0)
    short_call_k4 = -max(s_t - k_4, 0.0)
    return short_put_k1 + long_put_k2 + long_call_k3 + short_call_k4


def strip_payoff(strip: IronCondorStrip, s_t: float) -> float:
    """Weighted strip payoff ``Π_strip(S_T) = Σ w_j · ReverseIC_j(S_T)``."""
    return sum(c.weight * condor_payoff(c, s_t) for c in strip.condors)


def log_contract_proxy(s_t: float, s_0: float) -> float:
    r"""Canonical Carr-Madan log-contract payoff at terminal spot.

    .. math::

        Q(S_T) = -2 \cdot \log(S_T / S_0) + 2 \cdot (S_T - S_0) / S_0

    ``Q(S_0) = 0``, ``Q''(K) = 2/K² > 0`` — the canonical Carr-Madan
    weight profile. ``Q(S_T) ≥ 0`` everywhere with equality only at
    ``S_T = S_0``. The (centered) strip payoff after best-fit scale
    tracks ``Q(S_T)`` inside the strip's convex span.
    """
    if not (math.isfinite(s_t) and math.isfinite(s_0)):
        raise ValueError(
            f"log_contract_proxy: s_t = {s_t}, s_0 = {s_0} must both be finite"
        )
    if s_t <= 0.0 or s_0 <= 0.0:
        raise ValueError(
            f"log_contract_proxy: s_t = {s_t}, s_0 = {s_0} must both be > 0"
        )
    return -2.0 * math.log(s_t / s_0) + 2.0 * (s_t - s_0) / s_0


def _fit_scale(
    strip_centered: tuple[float, ...], proxy_values: tuple[float, ...]
) -> float:
    """Least-squares fit of ``Π_strip_centered ≈ β · Q``.

    Returns the optimal ``β`` for the unconstrained linear regression
    ``minimize_β Σ (strip_j - β · proxy_j)²``. Closed form:
    ``β = Σ strip_j · proxy_j / Σ proxy_j²``. The intercept is
    fixed at 0 because the inputs are already centered: ``Q(S_0) = 0``
    and the strip is centered so ``Π_strip_centered(S_0) = 0``.
    """
    num = sum(s * q for s, q in zip(strip_centered, proxy_values))
    den = sum(q * q for q in proxy_values)
    if den <= 0.0:
        raise ReplicationToleranceError(
            "_fit_scale: log-contract-proxy grid is degenerate (Σ Q² = 0)"
        )
    return num / den


@dataclass(frozen=True)
class CarrMadanEnvelopeVerifier:
    """Verify the centered strip tracks the log-contract proxy within tolerance.

    Default tolerance is :data:`REPLICATION_REL_TOL` (5%, PRIMITIVES.md
    §12 row 2). The verification grid spans the strip's convex region
    from ``S_0 · exp(-span)`` to ``S_0 · exp(+span)`` with
    ``n_grid_points`` samples (default 17, an odd number so ``S_0``
    itself is sampled).

    The strip is centered at ``S_0`` before fitting: the off-center
    condors' capped-wing contributions at spot form a constant floor
    that the LP holds as static collateral. The convex EXCESS above
    that floor is what the CPO buyer pays the streamed premium for —
    and that is what the envelope check compares to the log-contract
    proxy.
    """

    n_grid_points: int = 17
    span: float = 0.15
    tolerance: float = REPLICATION_REL_TOL

    def __post_init__(self) -> None:
        if not isinstance(self.n_grid_points, int) or self.n_grid_points < 3:
            raise ValueError(
                f"CarrMadanEnvelopeVerifier.n_grid_points = {self.n_grid_points}"
                " must be an int ≥ 3"
            )
        if not (math.isfinite(self.span) and self.span > 0.0):
            raise ValueError(
                f"CarrMadanEnvelopeVerifier.span = {self.span}"
                " must be a finite float > 0"
            )
        if not (math.isfinite(self.tolerance) and self.tolerance > 0.0):
            raise ValueError(
                f"CarrMadanEnvelopeVerifier.tolerance = {self.tolerance}"
                " must be a finite float > 0"
            )

    def __call__(self, strip: IronCondorStrip) -> ReplicationVerdict:
        s_0 = strip.s_0
        # Symmetric log-strike grid spanning [-span, +span] around log(S_0).
        step = 2.0 * self.span / (self.n_grid_points - 1)
        s_grid = tuple(
            s_0 * math.exp(-self.span + step * i) for i in range(self.n_grid_points)
        )
        strip_vals = tuple(strip_payoff(strip, s) for s in s_grid)
        proxy_vals = tuple(log_contract_proxy(s, s_0) for s in s_grid)
        floor = strip_payoff(strip, s_0)
        strip_centered = tuple(v - floor for v in strip_vals)
        beta = _fit_scale(strip_centered, proxy_vals)
        residuals = tuple(
            abs(strip_centered[i] - beta * proxy_vals[i])
            for i in range(self.n_grid_points)
        )
        peak = max(abs(v) for v in strip_centered)
        if peak <= 0.0:
            raise ReplicationToleranceError(
                "CarrMadanEnvelopeVerifier: centered strip payoff is identically"
                " zero across the grid — strip geometry is degenerate"
            )
        max_rel = max(residuals) / peak
        passes = max_rel <= self.tolerance
        return ReplicationVerdict(
            max_relative_error=max_rel,
            tolerance=self.tolerance,
            n_grid_points=self.n_grid_points,
            passes=passes,
        )


verify_carr_madan_envelope = CarrMadanEnvelopeVerifier()


def assert_long_vol_signature(strip: IronCondorStrip) -> None:
    """Assert the strip's long-vol convexity signature (Pin S5).

    Checks (under the tiled-body geometry where adjacent condor inner
    bodies meet at the neighbouring centers, so the strip floor at
    ``S_0`` is exactly zero):

    1. ``Π_strip(S_0) == 0`` within :data:`SPOT_FLOOR_TOL` — every
       condor's inner body covers ``S_0`` or borders it.
    2. ``Π_strip(S_0 · e^{-delta_inner}) > 0`` — leaving the ATM body
       on the down side pays.
    3. ``Π_strip(S_0 · e^{+delta_inner}) > 0`` — leaving the ATM body
       on the up side pays.

    These together establish the strip's convex long-vol signature
    relative to spot.

    Raises:
        ReplicationToleranceError: If any signature check fails.
    """
    s_0 = strip.s_0
    delta_inner = strip.geometry.delta_inner
    payoff_at_spot = strip_payoff(strip, s_0)
    payoff_down = strip_payoff(strip, s_0 * math.exp(-delta_inner))
    payoff_up = strip_payoff(strip, s_0 * math.exp(+delta_inner))
    spot_floor_tol = 1e-9 * max(1.0, s_0)
    if abs(payoff_at_spot) > spot_floor_tol:
        raise ReplicationToleranceError(
            f"assert_long_vol_signature: Π_strip(S_0) = {payoff_at_spot}"
            f" exceeds spot-floor tolerance {spot_floor_tol}"
            " (tiled-body geometry should drive the floor to 0)"
        )
    if not payoff_down > 0.0:
        raise ReplicationToleranceError(
            f"assert_long_vol_signature: Π_strip(S_0·e^{{-δ_inner}})"
            f" = {payoff_down} must be > 0 (long-vol on down side)"
        )
    if not payoff_up > 0.0:
        raise ReplicationToleranceError(
            f"assert_long_vol_signature: Π_strip(S_0·e^{{+δ_inner}})"
            f" = {payoff_up} must be > 0 (long-vol on up side)"
        )


__all__ = [
    "CarrMadanEnvelopeVerifier",
    "assert_long_vol_signature",
    "condor_payoff",
    "log_contract_proxy",
    "strip_payoff",
    "verify_carr_madan_envelope",
]
