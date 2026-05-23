"""FX-path, variance-proxy, and blended per-token-price Value types.

Covers spec §6 functional-form rows + PRIMITIVES.md §5 / §6:

- FX path ``(X/Y)_t = (1 + ε (cos²(ω t) - ½)) · (X̄/Ȳ)`` (PRIMITIVES (6),
  spec §3) — ``FXPathParams``;
- Realized variance ``σ_T = T⁻¹ Σ_{t=0}^T ((X/Y)_t - X̄/Ȳ)²`` (PRIMITIVES (7))
  — ``RealizedVarianceParams`` (just the horizon ``T``);
- Blended per-token price
  ``p_t = w_in · p_in · (1 - h_cache + h_cache · 0.10) + w_out · p_out``
  (spec §5.1) — ``BlendedPriceParams`` (constraint ``w_in + w_out = 1``).

Math pin enforcement (per Phase 1 reconciliation + plan Phase 2 prelude):

- M5 FX-path closed form is implemented at the Callable in
  ``simulations.modules`` with PRIMITIVES (6) + (8) verbatim in its docstring.
  This Value tier provides only the parameter container and validation
  ``0 < ε < 1``.
- M3 blended-price formula is implemented at the Callable in
  ``simulations.modules``. This Value tier carries the parameter weights /
  cache fraction / per-tier prices, with constraint ``w_in + w_out = 1``.

Module-level constants reproduce the spec §5.2 pricing pins as ``Final`` USD
per million tokens.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final


def _is_finite_positive(x: float) -> bool:
    """Return True iff x is a finite (non-inf, non-NaN) strictly-positive float."""
    return math.isfinite(x) and x > 0.0

# ─── Module-level constants — spec §5.2 pricing pins ──────────────────────────

#: Spec §5.1 input-token weight (arxiv 2601.14470 input dominance 53.9%).
DEFAULT_W_IN: Final[float] = 0.539

#: Spec §5.1 output-token weight (1 - DEFAULT_W_IN).
DEFAULT_W_OUT: Final[float] = 0.461

#: Spec §5.2 default cache-hit fraction.
DEFAULT_H_CACHE: Final[float] = 0.95

#: Cached-input-token discount factor in spec §5.1 blended formula
#: (cached portion priced at 10% of in-list rate).
CACHED_INPUT_DISCOUNT: Final[float] = 0.10

# Per-model in/out per-MTok prices (USD), spec §5.2 — Sonnet 4.6.
SONNET_PRICE_IN_USD_PER_MTOK: Final[float] = 3.0
SONNET_PRICE_OUT_USD_PER_MTOK: Final[float] = 15.0

# Spec §5.2 — Opus 4.6.
OPUS_PRICE_IN_USD_PER_MTOK: Final[float] = 5.0
OPUS_PRICE_OUT_USD_PER_MTOK: Final[float] = 25.0

# Spec §5.2 — Haiku 4.5.
HAIKU_PRICE_IN_USD_PER_MTOK: Final[float] = 1.0
HAIKU_PRICE_OUT_USD_PER_MTOK: Final[float] = 5.0


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FXPathParams:
    """Parameters for the deterministic FX path (PRIMITIVES (6), spec §3).

    Closed form (implemented in ``simulations.modules``):

        (X/Y)_t = (1 + ε (cos²(ω t) - ½)) · (X̄/Ȳ),  0 < ε < 1.

    Symbol map (PRIMITIVES §13):

    - ``mean_x_over_y`` ↔ stationary FX mean ``X̄/Ȳ``;
    - ``epsilon`` ↔ amplitude ε of the cos² perturbation;
    - ``omega`` ↔ angular frequency ω of the perturbation.

    Validation contract:

    - ``mean_x_over_y > 0``;
    - ``0 < epsilon < 1`` (spec §3 / PRIMITIVES (6) admissible region);
    - ``omega > 0``.
    """

    mean_x_over_y: float
    epsilon: float
    omega: float

    def __post_init__(self) -> None:
        if not _is_finite_positive(self.mean_x_over_y):
            raise ValueError(
                f"FXPathParams.mean_x_over_y = {self.mean_x_over_y}"
                f" must be a finite float > 0"
            )
        # Bounded-interval check (NaN and ±inf both fail the comparison; rejected as intended).
        if not (0.0 < self.epsilon < 1.0):
            raise ValueError(
                f"FXPathParams.epsilon = {self.epsilon} must lie in (0, 1)"
            )
        if not _is_finite_positive(self.omega):
            raise ValueError(
                f"FXPathParams.omega = {self.omega} must be a finite float > 0"
            )


@dataclass(frozen=True)
class RealizedVarianceParams:
    """Parameters of the realized-variance proxy σ_T (PRIMITIVES (7)).

    Closed form (implemented in ``simulations.modules``):

        σ_T = T⁻¹ Σ_{t=0}^{T} ((X/Y)_t - X̄/Ȳ)².

    Validation contract:

    - ``horizon_T > 0`` (number of time steps; integer-typed for clarity).
    """

    horizon_T: int

    def __post_init__(self) -> None:
        if not (self.horizon_T > 0):
            raise ValueError(
                f"RealizedVarianceParams.horizon_T = {self.horizon_T} must be > 0"
            )


@dataclass(frozen=True)
class BlendedPriceParams:
    """Per-token blended price parameters (spec §5.1, M3).

    Closed form (implemented in ``simulations.modules``):

        p_t = w_in · p_in · (1 - h_cache + h_cache · 0.10) + w_out · p_out

    For the Sonnet 4.6 default at ``h_cache = 0.95``:

        p_t ≈ 0.539 · 3 · 0.145 + 0.461 · 15 ≈ 7.15  USD/MTok

    (verified in spec v1.1.1 §5.4 footnote).

    Symbol map:

    - ``w_in`` / ``w_out`` ↔ input / output token weights (spec §5.1);
    - ``h_cache`` ↔ cache-hit fraction;
    - ``p_in`` / ``p_out`` ↔ tier-dependent in/out USD per MTok.

    Validation contract:

    - ``0 < w_in < 1`` and ``w_in + w_out == 1`` within ``1e-12``;
    - ``0 ≤ h_cache ≤ 1``;
    - ``p_in > 0`` and ``p_out > 0``.
    """

    w_in: float
    w_out: float
    h_cache: float
    p_in: float
    p_out: float

    def __post_init__(self) -> None:
        if not (0.0 < self.w_in < 1.0):
            raise ValueError(
                f"BlendedPriceParams.w_in = {self.w_in} must lie in (0, 1)"
            )
        if not (0.0 < self.w_out < 1.0):
            raise ValueError(
                f"BlendedPriceParams.w_out = {self.w_out} must lie in (0, 1)"
            )
        if abs(self.w_in + self.w_out - 1.0) > 1e-12:
            raise ValueError(
                f"BlendedPriceParams: w_in + w_out must equal 1 within 1e-12"
                f" (got {self.w_in + self.w_out!r})"
            )
        # Bounded-interval check (NaN and ±inf both fail the comparison; rejected as intended).
        if not (0.0 <= self.h_cache <= 1.0):
            raise ValueError(
                f"BlendedPriceParams.h_cache = {self.h_cache} must lie in [0, 1]"
            )
        if not _is_finite_positive(self.p_in):
            raise ValueError(
                f"BlendedPriceParams.p_in = {self.p_in} must be a finite float > 0"
            )
        if not _is_finite_positive(self.p_out):
            raise ValueError(
                f"BlendedPriceParams.p_out = {self.p_out} must be a finite float > 0"
            )


# ─── Free-function accessors ──────────────────────────────────────────────────


def fx_amplitude_envelope(params: FXPathParams) -> tuple[float, float]:
    """Return the pointwise (min, max) of the FX path over t.

    Since ``cos²(ω t) - ½ ∈ [-½, ½]``, the envelope is

        (X̄/Ȳ) · (1 - ε/2)  ≤  (X/Y)_t  ≤  (X̄/Ȳ) · (1 + ε/2).
    """
    mean = params.mean_x_over_y
    half_eps = 0.5 * params.epsilon
    return (mean * (1.0 - half_eps), mean * (1.0 + half_eps))
