"""Per-token blended price Callable (spec §5.1, pin M3).

Implements:

- :class:`BlendedPriceFn` — verbatim spec §5.1 formula::

      p_t = w_in · p_in · (1 - h_cache + h_cache · CACHED_INPUT_DISCOUNT)
            + w_out · p_out

  Returns USD per million tokens ($/MTok).

  ``CACHED_INPUT_DISCOUNT = 0.10`` is fixed in
  :mod:`simulations.types.fx` as a ``Final`` constant.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulations.types.fx import CACHED_INPUT_DISCOUNT, BlendedPriceParams


@dataclass(frozen=True)
class BlendedPriceFn:
    """Spec §5.1 blended per-token price (pin M3) — units $/MTok.

    Closed form (verbatim)::

        p_t = w_in · p_in · (1 - h_cache + h_cache · 0.10)
              + w_out · p_out

    where the cache-discount factor ``0.10`` is the module-level constant
    :data:`simulations.types.fx.CACHED_INPUT_DISCOUNT`.

    Sonnet-default verification (spec v1.1.1 §5.4 footnote)::

        0.539 · 3 · (1 - 0.95 + 0.95 · 0.10) + 0.461 · 15
          = 0.539 · 3 · 0.145 + 0.461 · 15
          = 0.234 + 6.915
          ≈ 7.15  USD / MTok.
    """

    params: BlendedPriceParams

    def __call__(self) -> float:
        """Return the blended per-token price in USD per million tokens.

        Returns:
            Scalar float, the spec §5.1 weighted average ``p_t``.
        """
        p = self.params
        cache_factor = (
            1.0 - p.h_cache + p.h_cache * CACHED_INPUT_DISCOUNT
        )
        return float(p.w_in * p.p_in * cache_factor + p.w_out * p.p_out)


__all__ = [
    "BlendedPriceFn",
]
