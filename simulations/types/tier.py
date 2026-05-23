"""Tier identity and tier-prior Value types.

Covers spec §6 rows:

- ``tier_id`` — Categorical(π) over {pro, max_5x, max_20x} (spec §5.1, §5.2).
- ``bar_p_sub`` — discrete RV indexed by tier_id (spec §5.2 pricing pins).

Math pins involved: none directly; this is plain Categorical/Dirichlet
parameter material consumed by the SAAS-COHORT-1 sampler in ``modules/``.
"""

from __future__ import annotations

import math
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, field
from typing import Final, Literal, Mapping, TypeAlias


def _is_finite_positive(x: float) -> bool:
    """Return True iff x is a finite (non-inf, non-NaN) strictly-positive float."""
    return math.isfinite(x) and x > 0.0

# ─── TypeAliases ──────────────────────────────────────────────────────────────

#: Tier identity. Spec §5.2 closes the candidate set; no others are admitted.
TierID: TypeAlias = Literal["pro", "max_5x", "max_20x"]

#: Map from tier identity to a scalar attribute (price, mass, cap, …).
TierMap: TypeAlias = Mapping[TierID, float]

# ─── Module-level constants (spec §5.2) ───────────────────────────────────────

#: Frozen tuple of admissible tier ids (matches the Literal above).
TIER_IDS: Final[tuple[TierID, TierID, TierID]] = ("pro", "max_5x", "max_20x")

#: Spec §5.2 monthly subscription pins, USD per month per tier.
SUBSCRIPTION_USD_PER_MONTH: Final[Mapping[TierID, float]] = {
    "pro": 20.0,
    "max_5x": 100.0,
    "max_20x": 200.0,
}

#: Spec §5.1 default Categorical prior π = (Pro, Max-5x, Max-20x).
DEFAULT_TIER_PI: Final[Mapping[TierID, float]] = {
    "pro": 0.20,
    "max_5x": 0.50,
    "max_20x": 0.30,
}

#: Spec §5.1 Dirichlet concentration default α₀ = 10 ("mild").
DEFAULT_TIER_DIRICHLET_ALPHA: Final[float] = 10.0


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TierPrior:
    """Categorical prior over tiers + Dirichlet concentration (spec §5.1).

    Encodes the tier-mix prior π over ``TIER_IDS`` plus a scalar Dirichlet
    concentration ``alpha_0``. The cohort-survey posterior (Stage-3) shrinks
    this prior; pre-survey synthetic draws apply spec §8(7) CI-width gates
    via the consumer Callable in ``simulations.modules``.

    Validation contract (``__post_init__``):

    - Every key of ``pi`` must be in ``TIER_IDS``; missing keys raise.
    - Every value of ``pi`` must be in ``(0, 1]`` (open at 0, closed at 1).
    - ``sum(pi.values())`` must equal 1.0 within ``1e-9`` absolute tolerance.
    - ``alpha_0`` must be strictly positive.
    """

    pi: Mapping[TierID, float] = field(default_factory=lambda: dict(DEFAULT_TIER_PI))
    alpha_0: float = DEFAULT_TIER_DIRICHLET_ALPHA

    def __post_init__(self) -> None:
        if not isinstance(self.pi, MappingABC):
            raise TypeError(
                f"TierPrior.pi must be a Mapping (got {type(self.pi).__name__})"
            )
        keys = set(self.pi.keys())
        admissible = set(TIER_IDS)
        if keys != admissible:
            raise ValueError(
                f"TierPrior.pi must have exactly keys {admissible}; got {keys}"
            )
        # Bounded-interval check (NaN and ±inf both fail the comparison; rejected as intended).
        for k, v in self.pi.items():
            if not (0.0 < v <= 1.0):
                raise ValueError(
                    f"TierPrior.pi[{k!r}] = {v} must lie in (0, 1]"
                )
        total = sum(self.pi.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"TierPrior.pi must sum to 1.0 (got {total!r}, |Δ| > 1e-9)"
            )
        if not _is_finite_positive(self.alpha_0):
            raise ValueError(
                f"TierPrior.alpha_0 = {self.alpha_0} must be a finite float > 0"
            )


@dataclass(frozen=True)
class TierPricing:
    """Per-tier monthly subscription pricing (spec §5.2).

    USD/mo pin per tier. The default matches the spec §5.2 frozen pin
    {pro: 20, max_5x: 100, max_20x: 200}.

    Validation contract:

    - Every key of ``usd_per_month`` must be in ``TIER_IDS``.
    - Every value must be strictly positive.
    """

    usd_per_month: Mapping[TierID, float] = field(
        default_factory=lambda: dict(SUBSCRIPTION_USD_PER_MONTH)
    )

    def __post_init__(self) -> None:
        if not isinstance(self.usd_per_month, MappingABC):
            raise TypeError(
                f"TierPricing.usd_per_month must be a Mapping"
                f" (got {type(self.usd_per_month).__name__})"
            )
        keys = set(self.usd_per_month.keys())
        admissible = set(TIER_IDS)
        if keys != admissible:
            raise ValueError(
                f"TierPricing.usd_per_month must have exactly keys {admissible};"
                f" got {keys}"
            )
        for k, v in self.usd_per_month.items():
            if not _is_finite_positive(v):
                raise ValueError(
                    f"TierPricing.usd_per_month[{k!r}] = {v}"
                    f" must be a finite float > 0"
                )


# ─── Free-function accessors ──────────────────────────────────────────────────


def categorical_mass(prior: TierPrior, tier: TierID) -> float:
    """Return Categorical mass π[tier] from a ``TierPrior``.

    Contract:
        Preconditions:
            - ``tier`` must be in ``TIER_IDS`` (the ``TierID`` Literal).
              Type-checker enforces this; runtime mis-typed values raise
              ``KeyError`` from the dict lookup (implicit).
    """
    return prior.pi[tier]


def subscription_price_usd(pricing: TierPricing, tier: TierID) -> float:
    """Return the monthly subscription price (USD) for a given tier.

    Contract:
        Preconditions:
            - ``tier`` must be in ``TIER_IDS``. Implicit ``KeyError`` from
              dict lookup if not.
    """
    return pricing.usd_per_month[tier]
