"""Stateless Callable samplers for cohort synthetic-data tests.

Implements:

- :class:`TruncParetoSampler` — inverse-CDF truncated Pareto sampler. Pin M1
  (spec §8(6)): refuses ``alpha < 1.5`` at construction time.
- :class:`NegBinSampler` — negative-binomial sampler over ``np.random.Generator``.
- :class:`TierMixCategorical` — Categorical(π) sampler over ``TIER_IDS``.

All Callables are frozen-dataclasses with ``__call__``; ``np.random.Generator``
is passed in at call time (modern API; never instantiated inside ``__call__``).

These samplers exist for synthetic-data testing in ``simulations/tests/``.
The PyMC forward pattern used by SAAS-COHORT-1 (per Phase 1 reconciliation
§2.6) is independent of this module — it constructs ``pm.Truncated(...)``
distributions directly and shares only the underlying parameter Value types.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simulations.types.distributions import (
    SAAS_TRUNC_PARETO_ALPHA_FLOOR,
    NegBinParams,
    TruncParetoParams,
)
from simulations.types.tier import TIER_IDS, TierID, TierPrior


@dataclass(frozen=True)
class TruncParetoSampler:
    """Inverse-CDF Truncated Pareto sampler on ``[x_m, x_max]``.

    Density on ``[x_m, x_max]``::

        f(x) = α · x_m^α / x^{α+1} / (1 - (x_m / x_max)^α).

    CDF::

        F(x) = (1 - (x_m / x)^α) / (1 - (x_m / x_max)^α).

    Inverse-CDF sampling (with ``u ∈ [0, 1)``)::

        x = x_m / (1 - u · (1 - (x_m / x_max)^α))^{1/α}.

    Edge cases:

    - ``u = 0`` ⇒ ``x = x_m``;
    - ``u → 1`` ⇒ ``x → x_max`` (numerically clipped via ``np.clip``).

    Pin M1 (spec §8(6), Phase 1 reconciliation §2.3): the SaaS-builder
    cohort requires ``α ≥ 1.5``. The :class:`TruncParetoParams` Value type
    accepts any ``α > 0``; this sampler enforces the floor at construction
    time to keep the cohort boundary explicit.
    """

    params: TruncParetoParams

    def __post_init__(self) -> None:
        if self.params.alpha < SAAS_TRUNC_PARETO_ALPHA_FLOOR:
            raise ValueError(
                "TruncParetoSampler requires alpha >="
                f" {SAAS_TRUNC_PARETO_ALPHA_FLOOR} per spec §8(6);"
                f" got alpha={self.params.alpha}"
            )

    def __call__(
        self, *, size: int, rng: np.random.Generator
    ) -> NDArray[np.float64]:
        """Draw ``size`` independent TruncPareto variates on ``[x_m, x_max]``.

        Args:
            size: number of samples (must be ≥ 0).
            rng: a modern ``numpy.random.Generator`` (pass in; never
                construct here).

        Returns:
            ``np.float64`` array of shape ``(size,)`` with values in
            ``[x_m, x_max]``.

        Raises:
            ValueError: if ``size < 0``.
        """
        if size < 0:
            raise ValueError(f"TruncParetoSampler size={size} must be ≥ 0")
        x_m = self.params.x_m
        x_max = self.params.x_max
        alpha = self.params.alpha
        # Tail mass at x_max relative to x_m: (x_m / x_max)^α
        tail = (x_m / x_max) ** alpha
        u = rng.random(size=size)
        # Inverse-CDF: x = x_m / (1 - u (1 - tail))^{1/α}
        x = x_m / np.power(1.0 - u * (1.0 - tail), 1.0 / alpha)
        # Numerical safety: clip to support endpoints.
        return np.clip(x, x_m, x_max).astype(np.float64, copy=False)


@dataclass(frozen=True)
class NegBinSampler:
    """Negative-binomial sampler (spec §5.1 — daily turn count N_j).

    Convention matches :class:`NegBinParams`: ``r`` is the dispersion /
    number-of-failures parameter, ``p`` is the success probability. Variance
    exceeds the mean for ``p < 1``.

    Uses ``np.random.Generator.negative_binomial`` directly. No floor
    constraint (spec §5.1 has no over-dispersion lower bound).
    """

    params: NegBinParams

    def __call__(
        self, *, size: int, rng: np.random.Generator
    ) -> NDArray[np.int64]:
        """Draw ``size`` independent NegBin(r, p) variates.

        Args:
            size: number of samples (must be ≥ 0).
            rng: modern ``numpy.random.Generator``.

        Returns:
            ``np.int64`` array of non-negative integer turn counts.

        Raises:
            ValueError: if ``size < 0``.
        """
        if size < 0:
            raise ValueError(f"NegBinSampler size={size} must be ≥ 0")
        # numpy uses (n, p) where n = r (dispersion); both real-valued
        # in newer numpy, but we cast to float to be explicit.
        draws = rng.negative_binomial(
            n=float(self.params.r), p=float(self.params.p), size=size
        )
        return draws.astype(np.int64, copy=False)


@dataclass(frozen=True)
class TierMixCategorical:
    """Categorical(π) sampler over the closed tier set ``TIER_IDS``.

    Reads ``TierPrior.pi`` and converts it to an ordered probability
    array indexed by ``TIER_IDS`` (the ordering ``("pro", "max_5x",
    "max_20x")`` is fixed by :data:`simulations.types.tier.TIER_IDS`).
    Uses ``np.random.Generator.choice`` for selection; the result is
    a string-typed array of ``TierID`` values.
    """

    prior: TierPrior

    def __call__(
        self, *, size: int, rng: np.random.Generator
    ) -> NDArray[np.str_]:
        """Draw ``size`` independent Categorical tier ids.

        Args:
            size: number of samples (must be ≥ 0).
            rng: modern ``numpy.random.Generator``.

        Returns:
            ``np.str_`` array of shape ``(size,)`` whose entries are members
            of ``TIER_IDS``.

        Raises:
            ValueError: if ``size < 0``.
        """
        if size < 0:
            raise ValueError(f"TierMixCategorical size={size} must be ≥ 0")
        # Ordered probability vector indexed by TIER_IDS (deterministic).
        probs = np.array(
            [self.prior.pi[t] for t in TIER_IDS], dtype=np.float64
        )
        # numpy choice over a Python tuple of literal strings.
        choices: tuple[TierID, ...] = TIER_IDS
        return rng.choice(np.array(choices), size=size, p=probs)


__all__ = [
    "TruncParetoSampler",
    "NegBinSampler",
    "TierMixCategorical",
]
