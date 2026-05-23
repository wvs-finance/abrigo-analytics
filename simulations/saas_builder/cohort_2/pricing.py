"""Callable-tier T2 (metered-overage) pricing for SAAS-COHORT-2.

Implements:

- :class:`SoftplusBetaFitter` — Pin M2-fit β search (50 log-spaced points
  on ``β ∈ [0.01/κ, 100/κ]``); returns the smallest β satisfying Pin M2
  ``L¹ deviation < 1e-3 · κ`` over ``[0, 2 κ]``. Raises
  :class:`M2TightnessNotAchievedError` if no grid point qualifies (HALT
  trigger; no silent grid widening).
- :class:`T2CostComposer` — vectorized
  ``q_t^USD = p̄_sub + p_t · softplus_β(τ_t - κ)`` per spec §5.1 (T2).
  Wraps the shipped ``simulations.modules.regularizers.SoftplusRegularizer``
  whose ``__post_init__`` re-checks Pin M2 (double-validation is
  intentional — fitter may use a tolerance, regularizer enforces strict).

Tier-import discipline: imports allowed from
``simulations.saas_builder.cohort_2.{_errors, types}`` and from the
shipped ``simulations.{types, modules, utils}`` packages. MUST NOT import
from ``simulations.saas_builder.cohort_2.io`` or ``...data``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Mapping

import numpy as np
from numpy.typing import NDArray

from simulations.modules.pricing import BlendedPriceFn
from simulations.modules.regularizers import SoftplusRegularizer
from simulations.saas_builder.cohort_2._errors import (
    M2TightnessNotAchievedError,
)
from simulations.saas_builder.cohort_2.types import (
    SAAS_TIER_IDS,
    SPEC_ALPHA_BRACKET,
    SPEC_H_CACHE_BRACKET,
    SPEC_KAPPA_MULTIPLIERS,
    SPEC_SONNET_P_IN,
    SPEC_SONNET_P_OUT,
    SPEC_TIER_KAPPA,
    SPEC_TIER_P_SUB_BAR,
    SPEC_W_IN,
    SPEC_W_OUT,
    BracketGrid,
    BracketPoint,
    T2CostParams,
)
from simulations.types.distributions import (
    SOFTPLUS_TIGHTNESS_EPS,
    SoftplusParams,
    tightness_l1_deviation,
)
from simulations.types.fx import BlendedPriceParams, FXPathParams

# ─── Module-level constants — Pin M2-fit ──────────────────────────────────────

#: Pin M2-fit (plan v0.2 Phase 2 prelude) — log-spaced grid lower bound (× 1/κ).
DEFAULT_BETA_MIN_FACTOR: Final[float] = 0.01

#: Pin M2-fit — log-spaced grid upper bound (× 1/κ).
DEFAULT_BETA_MAX_FACTOR: Final[float] = 100.0

#: Pin M2-fit — number of log-spaced grid points.
DEFAULT_BETA_GRID_SIZE: Final[int] = 50


# ─── Callables ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SoftplusBetaFitter:
    """Pin M2-fit search Callable (plan v0.2 Phase 2 prelude).

    Search ``β ∈ [β_min_factor / κ, β_max_factor / κ]`` on a log-spaced
    grid of ``n_grid`` points. Returns the *smallest* β that satisfies
    Pin M2 (``L¹ deviation < 1e-3 · κ`` on ``[0, 2 κ]``); raises
    :class:`M2TightnessNotAchievedError` if no grid point qualifies.

    Anti-fishing posture (NON-NEGOTIABLE): the grid is BOUNDED at
    construction; the Callable does NOT silently widen on infeasibility.
    HALT per ``feedback_pathological_halt_anti_fishing_checkpoint``.

    The returned β is the input to ``SoftplusParams(beta=β, kappa=κ)``
    which is then handed to the shipped ``SoftplusRegularizer`` (whose
    ``__post_init__`` re-checks Pin M2 strictly — double-validation).
    """

    beta_min_factor: float = DEFAULT_BETA_MIN_FACTOR
    beta_max_factor: float = DEFAULT_BETA_MAX_FACTOR
    n_grid: int = DEFAULT_BETA_GRID_SIZE

    def __post_init__(self) -> None:
        if not (0.0 < self.beta_min_factor < self.beta_max_factor):
            raise ValueError(
                "SoftplusBetaFitter: beta_min_factor must satisfy"
                f" 0 < beta_min_factor < beta_max_factor;"
                f" got ({self.beta_min_factor}, {self.beta_max_factor})"
            )
        if self.n_grid < 2:
            raise ValueError(
                f"SoftplusBetaFitter.n_grid = {self.n_grid} must be ≥ 2"
            )

    def __call__(self, kappa: float) -> float:
        """Return the smallest β on the grid satisfying Pin M2.

        Args:
            kappa: subscription cap κ in tokens (must be finite > 0).

        Returns:
            The smallest β on the log-spaced grid for which the L¹
            deviation of ``softplus_β`` from ReLU on ``[0, 2 κ]`` is
            strictly less than ``1e-3 · κ``.

        Raises:
            ValueError: if ``kappa`` ≤ 0 or non-finite.
            M2TightnessNotAchievedError: if NO grid point satisfies M2.
        """
        if not np.isfinite(kappa) or kappa <= 0.0:
            raise ValueError(
                f"SoftplusBetaFitter.__call__: kappa = {kappa}"
                " must be a finite float > 0"
            )
        beta_lo = self.beta_min_factor / kappa
        beta_hi = self.beta_max_factor / kappa
        grid = np.logspace(
            np.log10(beta_lo), np.log10(beta_hi), self.n_grid
        )
        threshold = SOFTPLUS_TIGHTNESS_EPS * kappa
        # Search ascending β: tighter softplus → smaller deviation.
        # Use the shipped ``tightness_l1_deviation`` so the fitter's
        # acceptance is identical to the SoftplusRegularizer's
        # __post_init__ check (avoids quad-precision divergence between
        # the two integrators).
        for beta in grid:
            params = SoftplusParams(beta=float(beta), kappa=float(kappa))
            dev = tightness_l1_deviation(params)
            if dev < threshold:
                return float(beta)
        # No grid point satisfied M2: HALT trigger.
        raise M2TightnessNotAchievedError(
            "SoftplusBetaFitter: no β on grid"
            f" [{beta_lo:.4e}, {beta_hi:.4e}] with {self.n_grid} log-spaced"
            f" points satisfied L¹ deviation < {threshold:.4e} on [0, 2κ]"
            f" with κ={kappa}; do NOT silently widen the grid"
            " (anti-fishing per feedback_pathological_halt_anti_fishing_checkpoint)"
        )


@dataclass(frozen=True)
class T2CostComposer:
    """Spec §5.1 (T2) cost composer Callable.

    Closed form (verbatim spec §5.1)::

        q_t^USD = p̄_sub + p_t · softplus_β(τ_t - κ)

    where ``softplus_β(x) = β⁻¹ log(1 + exp(β x))`` (Pin M2;
    numerically stable form ``logaddexp(0, β x) / β`` shipped via
    ``simulations.modules.regularizers.SoftplusRegularizer``).

    Construction wires the shipped ``SoftplusRegularizer`` whose
    ``__post_init__`` re-runs Pin M2 (``tightness_l1_deviation``) on the
    supplied (β, κ). MQ-FLAG-1 v0.3 fix: the previous "double-validation"
    framing was misleading (both calls used the same primitive); the
    rationale is now strict-construction defense — any caller that bypasses
    ``SoftplusBetaFitter`` and supplies a hand-set β still has Pin M2
    enforced at composer-construction time.
    """

    p_sub_bar: float
    kappa: float
    beta: float
    p_t: float
    # Wired at __post_init__ time; declared Optional so the default-None
    # field-default and the post-init assignment both type-check. Treat
    # as non-None after construction (post_init guarantees this).
    _regularizer: SoftplusRegularizer | None = None

    def __post_init__(self) -> None:
        for name, val in (
            ("p_sub_bar", self.p_sub_bar),
            ("kappa", self.kappa),
            ("beta", self.beta),
            ("p_t", self.p_t),
        ):
            if not np.isfinite(val) or val <= 0.0:
                raise ValueError(
                    f"T2CostComposer.{name} = {val} must be a finite float > 0"
                )
        # Build the softplus regularizer; its __post_init__ enforces Pin M2.
        params = SoftplusParams(beta=self.beta, kappa=self.kappa)
        regularizer = SoftplusRegularizer(params=params)
        # Frozen-dc workaround: object.__setattr__ for the wired field.
        object.__setattr__(self, "_regularizer", regularizer)

    def __call__(
        self, tau_t: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """Evaluate T2 cost ``q_t^USD`` elementwise.

        Args:
            tau_t: tokens-per-turn realisations (any shape; finite values
                expected — NaN/inf propagate via numpy).

        Returns:
            ``q_t^USD = p̄_sub + p_t · softplus_β(τ_t - κ)`` as float64
            (USD per month equivalent; same shape as ``tau_t``).
        """
        regularizer = self._regularizer
        assert regularizer is not None  # __post_init__ guarantees this.
        overage = regularizer(tau_t - self.kappa)
        return (self.p_sub_bar + self.p_t * overage).astype(
            np.float64, copy=False
        )


# ─── Helper: blended p_t via shipped BlendedPriceFn (RC-FLAG-1 v0.3 fix) ────


def composed_p_t(
    w_in: float,
    w_out: float,
    h_cache: float,
    p_in: float,
    p_out: float,
) -> float:
    """Return blended ``p_t`` (USD/MTok) by invoking shipped ``BlendedPriceFn``.

    RC-FLAG-1 v0.3 fix: cohort_2 now invokes the shipped
    ``simulations.modules.pricing.BlendedPriceFn`` instead of hardcoding
    the Sonnet-default ``7.15``. Callers (tests / notebooks / sign-cert
    bracket builder) construct ``BlendedPriceParams`` and pass through
    here; the shipped Callable's verbatim spec §5.1 formula is the
    single source of truth.
    """
    return BlendedPriceFn(
        params=BlendedPriceParams(
            w_in=w_in,
            w_out=w_out,
            h_cache=h_cache,
            p_in=p_in,
            p_out=p_out,
        )
    )()


# ─── Spec §5.2 bracket-grid builder (MQ-BLOCK-2 v0.3 fix) ────────────────────


def build_spec_5_2_bracket_grid(
    fitter: SoftplusBetaFitter,
    fx_params: FXPathParams,
    horizon_T: int = 12,
    tier_mix: Mapping[str, float] | None = None,
) -> BracketGrid:
    """Build the spec §5.2 parameter Cartesian-product bracket grid.

    MQ-BLOCK-2 v0.3 fix — the canonical sweep is over the **parameter**
    family, not over (ε, ω) FX-path cells. The FX path is a fixed M5
    anchor (passed in via ``fx_params``); the brackets sweep:

      - tier_id ∈ {pro, max_5x, max_20x};
      - p̄_sub per tier ∈ {20, 100, 200} USD/mo (inherited from tier);
      - κ-doubling-arm multiplier ∈ {1.0, 2.0};
      - α ∈ {1.5, 2.5} (TruncPareto bracket endpoints; α is recorded as
        a metadata bracket dimension — does NOT affect q_t closed form
        directly, but parameterizes the τ_t draws supplied per-bracket
        by the caller);
      - h_cache ∈ {0.80, 0.95} → blended p_t via shipped
        ``BlendedPriceFn``.

    Yields ``3 × 2 × 2 × 2 = 24`` BracketPoints, each on the same M5 FX
    path. The grid construction asserts M5 anchor recovery on the
    shared ``fx_params`` (one check, not 24).

    Note: α does not enter ``T2CostParams`` (the closed-form q_t depends
    on κ, β, p̄_sub, p_t — not α directly). Bracket-points with the same
    cost params but different α are *identical* in the q_t evaluator;
    the α dimension exists in the spec to enumerate the τ_t draw
    distribution that callers supply per-bracket. v0.3 still emits a
    distinct BracketPoint per α value so the caller can pair each with
    α-specific τ_t draws (e.g. drawn from a TruncPareto with that α).

    Args:
        fitter: a SoftplusBetaFitter (used to fit β per κ value).
        fx_params: the canonical M5 FX path (anchor-recovering).
        horizon_T: realized-variance horizon (default 12).
        tier_mix: tier weights (default uniform across SAAS_TIER_IDS).

    Returns:
        BracketGrid with 24 points enumerating spec §5.2 brackets.
    """
    if tier_mix is None:
        tier_mix = {
            SAAS_TIER_IDS[0]: 1.0 / 3.0,
            SAAS_TIER_IDS[1]: 1.0 / 3.0,
            SAAS_TIER_IDS[2]: 1.0 - 2.0 / 3.0,
        }
    points: list[BracketPoint] = []
    for tier in SAAS_TIER_IDS:
        p_sub_bar = SPEC_TIER_P_SUB_BAR[tier]
        kappa_base = SPEC_TIER_KAPPA[tier]
        for kappa_mult in SPEC_KAPPA_MULTIPLIERS:
            kappa = kappa_base * kappa_mult
            beta = fitter(kappa)
            for h_cache in SPEC_H_CACHE_BRACKET:
                p_t = composed_p_t(
                    w_in=SPEC_W_IN,
                    w_out=SPEC_W_OUT,
                    h_cache=h_cache,
                    p_in=SPEC_SONNET_P_IN,
                    p_out=SPEC_SONNET_P_OUT,
                )
                for _alpha in SPEC_ALPHA_BRACKET:
                    cost = T2CostParams(
                        p_sub_bar=p_sub_bar,
                        kappa=kappa,
                        beta=beta,
                        p_t=p_t,
                        tier_mix=tier_mix,
                    )
                    points.append(
                        BracketPoint(
                            cost_params=cost,
                            fx_params=fx_params,
                            horizon_T=horizon_T,
                        )
                    )
    return BracketGrid(points=tuple(points))


__all__ = [
    "DEFAULT_BETA_GRID_SIZE",
    "DEFAULT_BETA_MAX_FACTOR",
    "DEFAULT_BETA_MIN_FACTOR",
    "SoftplusBetaFitter",
    "T2CostComposer",
    "build_spec_5_2_bracket_grid",
    "composed_p_t",
]
