"""Soft regularizer Callables (spec §5.1 (T2) — softplus_β cap).

Implements:

- :class:`SoftplusRegularizer` — pin M2 enforcer + numerically-stable
  ``softplus_β(x) = β⁻¹ log(1 + exp(β x))``.

Pin M2 (spec §5.1 (T2), Phase 1 reconciliation §2.3): the regularizer
β must be tight enough that the L¹ deviation from ReLU on ``[0, 2 κ]``
is strictly less than ``1e-3 · κ``. Enforced at construction time via
:func:`simulations.types.distributions.tightness_l1_deviation`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simulations.types.distributions import (
    SOFTPLUS_TIGHTNESS_EPS,
    SoftplusParams,
    tightness_l1_deviation,
)


@dataclass(frozen=True)
class SoftplusRegularizer:
    """Numerically-stable softplus_β regularizer with M2 tightness floor.

    Implements::

        softplus_β(x) = (1/β) · log(1 + exp(β · x)),

    in the stable form ``np.logaddexp(0, β · x) / β``.

    Pin M2 (spec §5.1 (T2)): refuses construction unless the L¹ deviation
    of ``softplus_β`` from ReLU on the support ``[0, 2 κ]`` is strictly
    less than ``SOFTPLUS_TIGHTNESS_EPS · κ`` (i.e. ``< 1e-3 · κ``).

    NOTE (pre-mortem #7, scratch/2026-05-08-sim-infra-audit/): the
    relative tightness check ties to ``κ``; spec §5.1 (T2) implicitly
    assumes ``κ ~ O(1)`` USD per the cohort cost cap. At ``κ → 0`` the
    threshold ``1e-3 · κ`` drops below the quadrature noise of
    ``tightness_l1_deviation`` and the check no longer reliably
    distinguishes admissible β. Unit-conversion changes that scale κ
    must revisit this assumption.
    """

    params: SoftplusParams

    def __post_init__(self) -> None:
        dev = tightness_l1_deviation(self.params)
        threshold = SOFTPLUS_TIGHTNESS_EPS * self.params.kappa
        if dev >= threshold:
            raise ValueError(
                "SoftplusRegularizer requires β tight enough that L¹"
                " deviation < 1e-3·κ over [0, 2κ];"
                f" got deviation={dev:.4e}, threshold={threshold:.4e}"
            )

    def __call__(self, x: NDArray[np.float64]) -> NDArray[np.float64]:
        """Return ``softplus_β(x)`` evaluated elementwise.

        Args:
            x: input array.

        Returns:
            ``(1/β) · log(1 + exp(β x))`` in numerically-stable form
            (``np.logaddexp(0, β x) / β``); same shape as ``x``.
        """
        beta = self.params.beta
        return (np.logaddexp(0.0, beta * x) / beta).astype(
            np.float64, copy=False
        )


__all__ = [
    "SoftplusRegularizer",
]
