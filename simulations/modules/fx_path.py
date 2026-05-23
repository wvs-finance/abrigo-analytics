"""FX path generator, realized-variance calculator, and ε ↔ σ_T inversion.

Callable-tier transforms for the deterministic FX path
``(X/Y)_t`` and its realized-variance proxy σ_T. Math pin M5 is enforced
via verbatim citation to ``notes/PRIMITIVES.md``:

- :class:`FXPathGen` — PRIMITIVES.md (6).
- :class:`RealizedVarianceCalc` — PRIMITIVES.md (7).
- :func:`epsilon_from_sigma_T` — PRIMITIVES.md (8).

All Callables are frozen-dataclasses with ``__call__``; configuration lives in
fields, logic in ``__call__``. Imports allowed from ``simulations.types`` only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simulations.types.fx import FXPathParams, RealizedVarianceParams


@dataclass(frozen=True)
class FXPathGen:
    """Deterministic FX path generator (PRIMITIVES.md (6)).

    Implements verbatim::

        (X/Y)_t = (1 + ε · (cos²(ω · t) - 1/2)) · mean_X_over_Y,  0 < ε < 1.

    The amplitude bracket is therefore
    ``mean_x_over_y · (1 ± ε/2)``; see also :func:`fx_amplitude_envelope`
    in :mod:`simulations.types.fx` for the envelope accessor.

    See also :func:`epsilon_from_sigma_T` for the variance-inversion
    primitive (PRIMITIVES.md (8)).
    """

    params: FXPathParams

    def __call__(self, t: NDArray[np.float64]) -> NDArray[np.float64]:
        """Return ``(X/Y)_t`` evaluated pointwise on ``t``.

        Args:
            t: array of times (any shape; same dtype-broadcast rules as numpy).

        Returns:
            ``(1 + ε · (cos²(ω t) - 1/2)) · mean_x_over_y`` as float64.

        Contract:
            Preconditions:
                - ``t`` must be a numeric numpy array. Non-numeric dtype
                  raises ``TypeError`` from ``np.cos`` (implicit).
                - ``t`` SHOULD contain finite values; ``np.nan`` or
                  ``np.inf`` entries propagate to ``NaN`` in the output
                  silently (no validation here — preserves numpy's
                  total-function semantics on the math pin M5).

            Silences:
                None; numpy invalid-FP warnings are NOT suppressed (the
                module does not call ``np.errstate``).
        """
        cos_sq = np.cos(self.params.omega * t) ** 2
        return (
            (1.0 + self.params.epsilon * (cos_sq - 0.5))
            * self.params.mean_x_over_y
        ).astype(np.float64, copy=False)


@dataclass(frozen=True)
class RealizedVarianceCalc:
    """Realized-variance proxy σ_T (PRIMITIVES.md (7)).

    Implements PRIMITIVES.md (7) verbatim::

        σ_T ≡ (1/T) · Σ_{t=0}^{T} ((X/Y)_t - mean_X_over_Y)².

    Note the (T+1)/T arithmetic: the sum runs over ``t ∈ {0, 1, …, T}``
    (T+1 terms), but the divisor is ``T`` (NOT ``T+1``). PRIMITIVES (7)
    is honored literally; the divisor is ``params.horizon_T``.

    The Callable consumes a path *array*. The path length is required to
    equal ``params.horizon_T + 1`` exactly — mismatch raises
    ``ValueError`` (cross-check enforced as of CR I-1).
    """

    params: RealizedVarianceParams
    mean_x_over_y: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.mean_x_over_y) and self.mean_x_over_y > 0.0):
            raise ValueError(
                "RealizedVarianceCalc.mean_x_over_y ="
                f" {self.mean_x_over_y} must be a finite float > 0"
            )

    def __call__(self, path: NDArray[np.float64]) -> float:
        """Return σ_T as a non-negative float.

        Args:
            path: 1-D array of FX values ``(X/Y)_t`` for ``t ∈ {0, …, T}``.
                Length MUST equal ``params.horizon_T + 1``.

        Returns:
            ``Σ_{t=0}^{T} ((X/Y)_t - mean_X_over_Y)² / T``
            (PRIMITIVES.md (7) divisor is T, not T+1; honor literally).

        Contract:
            Preconditions:
                - ``len(path) == params.horizon_T + 1`` (enforced;
                  mismatch raises ``ValueError``).
                - ``path`` should contain finite values; ``NaN``/``inf``
                  propagate (implicit).

            Raises:
                ValueError: if ``len(path) != params.horizon_T + 1``.
                TypeError: if ``path`` is not subtractable from a float
                    (implicit, from ``path - self.mean_x_over_y``).
        """
        expected_len = self.params.horizon_T + 1
        if len(path) != expected_len:
            raise ValueError(
                "RealizedVarianceCalc: path length must be horizon_T + 1 ="
                f" {expected_len}; got {len(path)}"
            )
        diffs = path - self.mean_x_over_y
        return float(np.sum(diffs * diffs) / self.params.horizon_T)


def epsilon_from_sigma_T(sigma_T: float, mean_x_over_y: float) -> float:
    """Invert PRIMITIVES.md (8): ``ε(σ_T) = sqrt(8 · σ_T / mean_x_over_y²)``.

    Free function (not a method on :class:`FXPathParams`) because it produces
    a candidate ε value that callers then validate against the (0, 1)
    admissibility window via :class:`FXPathParams.__post_init__`.

    Args:
        sigma_T: realized-variance proxy as defined in PRIMITIVES.md (7);
            must be ≥ 0.
        mean_x_over_y: stationary FX mean ``X̄/Ȳ``; must be > 0.

    Returns:
        The inverted amplitude ``ε ≥ 0``. Caller must verify ``ε < 1``
        before constructing :class:`FXPathParams`.

    Raises:
        ValueError: if ``sigma_T < 0`` or ``mean_x_over_y <= 0``.
    """
    if not math.isfinite(sigma_T) or sigma_T < 0.0:
        raise ValueError(
            f"epsilon_from_sigma_T: sigma_T = {sigma_T} must be finite and ≥ 0"
        )
    if not (math.isfinite(mean_x_over_y) and mean_x_over_y > 0.0):
        raise ValueError(
            "epsilon_from_sigma_T: mean_x_over_y ="
            f" {mean_x_over_y} must be a finite float > 0"
        )
    return math.sqrt(8.0 * sigma_T / (mean_x_over_y * mean_x_over_y))


__all__ = [
    "FXPathGen",
    "RealizedVarianceCalc",
    "epsilon_from_sigma_T",
]
