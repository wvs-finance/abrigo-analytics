"""Exact three-way log-variance decomposition — Phase-0 RED stub.

Plan v0.2 task 0.6 declares the failing-test harness; the real exact
decomposition (spec v0.4 §4.2) lands in Phase 3 (plan task 3.3), on the
common X/Q differencing grid pinned by task 3.0 (CORR-E10P-3). This
module is a deliberate stub: it defines every symbol the
``test_decomposition`` harness imports so collection succeeds, and every
callable raises ``NotImplementedError`` so the harness goes RED.

Mirrors the E8 ``simulations/e8_dtao_maymin/modules`` RED-stub pattern.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    MonthlyRealizedVarianceCell,
    ThreeWayDecompositionCell,
)

_PHASE3 = "three-way decomposition lands in Phase 3 (plan task 3.3)"


@dataclass(frozen=True, slots=True)
class ThreeWayDecompositionModule:
    """Stateless callable — computes the exact §4.2 additive identity
    on the common differencing grid (RED stub until Phase 3)."""

    def __call__(
        self,
        fx_cell: MonthlyRealizedVarianceCell,
        trajectory: CostStreamTrajectory,
    ) -> ThreeWayDecompositionCell:
        raise NotImplementedError(_PHASE3)


def decompose_cell(
    *,
    fx_log_returns: Sequence[float],
    q_log_returns: Sequence[float],
) -> ThreeWayDecompositionCell:
    """Decompose one (currency, month) cell's cost-stream log-variance
    into the three §4.2 terms (RED stub until Phase 3)."""
    raise NotImplementedError(_PHASE3)
