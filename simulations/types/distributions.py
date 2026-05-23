"""Distribution-parameter Value types.

Covers spec §6 functional-form rows:

- ``tau_{j,i} ~ TruncPareto(alpha, x_m, kappa)`` — tokens-per-turn;
- ``N_j ~ NegBin(r, p)`` — daily turn count;
- softplus regularizer ``softplus_β(x) = β⁻¹ log(1 + e^{β x})`` with cap κ
  (spec §5.1 (T2)) — Value-tier *parameters only*; the regularizer Callable
  lives in ``simulations.modules``.

Math pin enforcement boundary (per Phase 1 reconciliation §2.3 and SIM-INFRA-0
plan Phase 2 prelude M1/M2):

- ``TruncParetoParams`` accepts ANY α > 0 here. The α ≥ 1.5 floor for the
  SaaS-builder cohort (spec §8(6)) binds at the **sampler Callable** in
  ``simulations.modules``, NOT at this Value tier. Future iterations
  defining their own samplers MUST honor or override the floor explicitly
  per their cohort spec.

- ``SoftplusParams`` exposes (β, κ) and the free function
  ``tightness_l1_deviation`` returning the L¹ deviation of softplus_β from
  ReLU on [0, 2κ]. The criterion ``deviation < 1e-3 · κ`` is enforced by
  the regularizer Callable in ``simulations.modules``, not here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import NDArray

# ─── Module-level constants ───────────────────────────────────────────────────

#: Spec §8(6) saas-builder α floor; lives here as a documented constant for
#: cross-reference. **It is not enforced at this Value tier** — the sampler
#: Callable in ``simulations.modules`` raises on α < SAAS_TRUNC_PARETO_ALPHA_FLOOR.
SAAS_TRUNC_PARETO_ALPHA_FLOOR: Final[float] = 1.5

#: Spec §5.1 saas-builder α upper bracket end (informational; not enforced here).
SAAS_TRUNC_PARETO_ALPHA_CEILING: Final[float] = 2.5

#: Spec §5.1 (T2) softplus tightness criterion as a multiplier on κ.
#: Deviation must be strictly less than ``SOFTPLUS_TIGHTNESS_EPS * kappa``
#: (enforced at the regularizer Callable, not at this Value tier).
SOFTPLUS_TIGHTNESS_EPS: Final[float] = 1e-3

#: Default integration grid resolution for ``tightness_l1_deviation``.
SOFTPLUS_TIGHTNESS_GRID_N: Final[int] = 4096


# ─── Private validators ───────────────────────────────────────────────────────


def _is_finite_positive(x: float) -> bool:
    """Return True iff x is a finite (non-inf, non-NaN) strictly-positive float."""
    return math.isfinite(x) and x > 0.0


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TruncParetoParams:
    """Truncated-Pareto parameters (spec §5.1 (T1) — tokens-per-turn).

    Density is proportional to ``α x_m^α / x^{α+1}`` for ``x ∈ [x_m, x_max]``,
    with normalizer such that the total mass on the truncated support is 1.

    Validation contract (this Value tier ONLY):

    - ``alpha > 0``,
    - ``x_m > 0``,
    - ``x_max > x_m``.

    α-floor contract (Phase 1 reconciliation §2.3, SIM-INFRA-0 plan §15.13):

        This Value tier accepts any α > 0. The α-floor for the SaaS-builder
        cohort (α ≥ 1.5 per spec §8(6)) binds at the sampler Callable in
        simulations/modules/. Future iterations defining their own samplers
        MUST honor or override the floor explicitly per their cohort spec.

    Symbol map (PRIMITIVES §13 + spec §5.1):

    - ``alpha`` ↔ Pareto tail index α;
    - ``x_m`` ↔ scale (lower-support) parameter;
    - ``x_max`` ↔ truncation cap κ (spec §5.1 — anything past κ enters the
      (T2) metered regime).
    """

    alpha: float
    x_m: float
    x_max: float

    def __post_init__(self) -> None:
        if not _is_finite_positive(self.alpha):
            raise ValueError(
                f"TruncParetoParams.alpha = {self.alpha} must be a finite float > 0"
            )
        if not _is_finite_positive(self.x_m):
            raise ValueError(
                f"TruncParetoParams.x_m = {self.x_m} must be a finite float > 0"
            )
        # x_max must be finite-positive AND strictly greater than x_m.
        if not (_is_finite_positive(self.x_max) and self.x_max > self.x_m):
            raise ValueError(
                f"TruncParetoParams.x_max = {self.x_max} must be a finite float"
                f" > x_m = {self.x_m}"
            )


@dataclass(frozen=True)
class NegBinParams:
    """Negative-binomial parameters (spec §5.1 — daily turn count N_j).

    Convention: ``r`` is the dispersion / number-of-failures parameter; ``p``
    is the success probability. Variance > mean iff ``p < 1``, which is
    required for the spec §5.1 over-dispersion claim (Anthropic costs-doc
    p90/mean ≈ 2.3×).

    Validation contract:

    - ``r > 0`` (relaxed from integer-only per spec §5.1; the Callable
      sampler may quantize),
    - ``0 < p < 1`` (open on both sides; ``p = 0`` and ``p = 1`` are
      degenerate).
    """

    r: float
    p: float

    def __post_init__(self) -> None:
        if not _is_finite_positive(self.r):
            raise ValueError(
                f"NegBinParams.r = {self.r} must be a finite float > 0"
            )
        # Bounded-interval check (NaN and ±inf both fail the comparison; rejected as intended).
        if not (0.0 < self.p < 1.0):
            raise ValueError(
                f"NegBinParams.p = {self.p} must lie in the open interval (0, 1)"
            )


@dataclass(frozen=True)
class SoftplusParams:
    """Softplus-regularizer parameters (spec §5.1 (T2)).

    Defines ``softplus_β(x) = β⁻¹ log(1 + e^{β x})`` with cap κ. The β → ∞
    limit recovers ReLU ``(x)^+``. Spec §5.1 (T2) requires the L¹ deviation
    of softplus_β from ReLU on the support [0, 2κ] to be strictly less than
    ``SOFTPLUS_TIGHTNESS_EPS · κ``.

    The criterion is enforced at the regularizer Callable in
    ``simulations.modules`` — see the free function ``tightness_l1_deviation``
    below for the computational primitive.

    Validation contract (Value tier ONLY):

    - ``beta > 0``,
    - ``kappa > 0``.
    """

    beta: float
    kappa: float

    def __post_init__(self) -> None:
        if not _is_finite_positive(self.beta):
            raise ValueError(
                f"SoftplusParams.beta = {self.beta} must be a finite float > 0"
            )
        if not _is_finite_positive(self.kappa):
            raise ValueError(
                f"SoftplusParams.kappa = {self.kappa} must be a finite float > 0"
            )


# ─── Free-function accessors ──────────────────────────────────────────────────


def trunc_pareto_admits_saas_floor(params: TruncParetoParams) -> bool:
    """Return ``True`` iff the SaaS-builder α ≥ 1.5 floor (spec §8(6)) holds.

    PURE accessor — does NOT raise. The α-floor is enforced at the sampler
    Callable in ``simulations.modules``; this helper exists for cross-tier
    consumers (e.g., diagnostic notebooks) that want to inspect the floor
    without constructing a sampler.
    """
    return params.alpha >= SAAS_TRUNC_PARETO_ALPHA_FLOOR


def neg_bin_mean(params: NegBinParams) -> float:
    """Return the mean of NegBin(r, p): ``r (1 - p) / p``."""
    return params.r * (1.0 - params.p) / params.p


def neg_bin_variance(params: NegBinParams) -> float:
    """Return the variance of NegBin(r, p): ``r (1 - p) / p²``."""
    return params.r * (1.0 - params.p) / (params.p * params.p)


def _softplus_scalar(x: float, beta: float) -> float:
    """Numerically-stable scalar softplus_β(x) = β⁻¹ log(1 + exp(β x))."""
    z = beta * x
    # log1p(exp(z)) stable form: max(z, 0) + log1p(exp(-|z|))
    return (max(z, 0.0) + math.log1p(math.exp(-abs(z)))) / beta


def tightness_l1_deviation(
    params: SoftplusParams, *, n_grid: int = SOFTPLUS_TIGHTNESS_GRID_N
) -> float:
    """Return the L¹ deviation of softplus_β from ReLU on [0, 2 κ].

    Computes ``∫₀^{2κ} |softplus_β(x - κ) - (x - κ)^+| dx`` via composite
    trapezoid rule on ``n_grid`` evenly-spaced nodes. Spec §5.1 (T2) requires
    this value to be strictly less than ``SOFTPLUS_TIGHTNESS_EPS · κ`` for
    a valid SaaS-builder regularizer; that criterion is enforced at the
    regularizer Callable in ``simulations.modules`` — this function is the
    pure computational primitive.

    Note this is the L¹ deviation as a function of the **shifted** argument
    ``x - κ``, matching the (T2) usage ``softplus_β(τ_t - κ)``.

    Note: numerical accuracy of the trapezoid integral degrades for
    ``β · κ > 30`` (cusp half-width drops below the grid spacing). The spec
    criterion ``deviation < 1e-3 · κ`` is met by ``β ≈ 50/κ``, well within
    the accurate regime, so production use does not enter the noisy band.

    Args:
        params: ``SoftplusParams(beta, kappa)``.
        n_grid: number of trapezoid nodes (default ``SOFTPLUS_TIGHTNESS_GRID_N``).

    Returns:
        The L¹ deviation as a non-negative float.

    Raises:
        ValueError: if ``n_grid < 2``.
    """
    if n_grid < 2:
        raise ValueError(f"n_grid = {n_grid} must be ≥ 2")
    kappa = params.kappa
    beta = params.beta
    xs: NDArray[np.float64] = np.linspace(0.0, 2.0 * kappa, n_grid, dtype=np.float64)
    shifted = xs - kappa
    # Stable softplus_β(shifted)
    z = beta * shifted
    softplus_vals = (np.maximum(z, 0.0) + np.log1p(np.exp(-np.abs(z)))) / beta
    relu_vals = np.maximum(shifted, 0.0)
    abs_diff = np.abs(softplus_vals - relu_vals)
    # Composite trapezoid rule
    integral: float = float(np.trapezoid(abs_diff, xs))
    return integral


__all__ = [
    "SAAS_TRUNC_PARETO_ALPHA_FLOOR",
    "SAAS_TRUNC_PARETO_ALPHA_CEILING",
    "SOFTPLUS_TIGHTNESS_EPS",
    "SOFTPLUS_TIGHTNESS_GRID_N",
    "TruncParetoParams",
    "NegBinParams",
    "SoftplusParams",
    "trunc_pareto_admits_saas_floor",
    "neg_bin_mean",
    "neg_bin_variance",
    "tightness_l1_deviation",
]
