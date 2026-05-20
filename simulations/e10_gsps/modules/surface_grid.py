"""FX-variance-share surface-grid evaluator — Phase-0 RED stub.

Plan v0.2 task 0.7 declares the failing-test harness; the real
surface-grid evaluator and the interior-crossing scan (spec v0.4 §4.3;
plan tasks 4.2 / 4.2a / CORR-E10P-4) land in Phase 4. This module is a
deliberate stub: it defines every symbol the ``test_surface_grid``
harness imports so collection succeeds, and every callable raises
``NotImplementedError`` so the harness goes RED.

Mirrors the E8 ``simulations/e8_dtao_maymin/modules`` RED-stub pattern.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from simulations.e10_gsps.types import (
    SurfaceGridResult,
    ThreeWayDecompositionCell,
)

_PHASE4 = "surface-grid evaluator lands in Phase 4 (plan tasks 4.2 / 4.2a)"


@dataclass(frozen=True, slots=True)
class SurfaceGridModule:
    """Stateless callable — evaluates the FX-variance-share surface on a
    grid across the whole anchored Q-volume range (RED stub until
    Phase 4)."""

    def __call__(
        self,
        decomposition_cells: tuple[ThreeWayDecompositionCell, ...],
        break_even_share: float,
        grid_resolution: float,
    ) -> SurfaceGridResult:
        raise NotImplementedError(_PHASE4)


def scan_interior_crossing(
    *,
    shares: Sequence[float],
    q_volumes: Sequence[float],
    break_even_share: float,
) -> SurfaceGridResult:
    """Scan every grid cell for a below-break-even interior crossing
    (plan task 4.2a — RED stub until Phase 4)."""
    raise NotImplementedError(_PHASE4)
