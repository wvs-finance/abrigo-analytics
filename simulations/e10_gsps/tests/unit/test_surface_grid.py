"""Failing-test harness — FX-variance-share surface-grid evaluator.

Plan v0.2 Phase 0.7. RED in Phase 0: imports the not-yet-existent
``simulations.e10_gsps.modules.surface_grid`` module, so collection
fails. The evaluator lands in Phase 4 (plan tasks 4.2 / 4.2a).

The harness asserts:
- the surface is evaluated on a grid ACROSS the whole anchored range,
  not at endpoints;
- per plan CORR-E10P-4 / task 4.2a, a synthetic non-monotone surface
  with an interior dip below break-even is detected by the
  interior-crossing scan (every cell scanned, not just endpoints).
"""

from __future__ import annotations

import pytest

from simulations.e10_gsps._errors import SurfaceGridError
from simulations.e10_gsps.modules.surface_grid import (  # noqa: F401 — RED import
    SurfaceGridModule,
    scan_interior_crossing,
)
from simulations.e10_gsps.types import ThreeWayDecompositionCell


def _decomposition_cells(shares: list[float]) -> tuple[ThreeWayDecompositionCell, ...]:
    """Build synthetic decomposition cells whose FX-variance share
    (var_fx / var_total) follows the requested sequence."""
    cells: list[ThreeWayDecompositionCell] = []
    for i, share in enumerate(shares):
        var_total = 1.0
        var_fx = share
        var_q = var_total - var_fx
        cells.append(
            ThreeWayDecompositionCell(
                currency="COP",
                year=2025,
                month=1 + i,
                var_total=var_total,
                var_fx=var_fx,
                var_q=var_q,
                cov_term=0.0,
                grid_index_length=20,
                identity_residual=0.0,
            )
        )
    return tuple(cells)


def test_surface_evaluated_across_whole_range_not_endpoints() -> None:
    """The surface must be evaluated on a grid across the whole anchored
    range — more than two points (endpoints alone are insufficient)."""
    module = SurfaceGridModule()
    cells = _decomposition_cells([0.6, 0.62, 0.58, 0.61])
    result = module(cells, break_even_share=0.30, grid_resolution=100.0)
    assert len(result.points) > 2


def test_interior_crossing_detected_on_non_monotone_surface() -> None:
    """Plan task 4.2a: a non-monotone surface that clears BOTH endpoints
    but dips below break-even in the interior must set interior_crossing
    True and record the crossing volume(s)."""
    # Endpoints at 0.40 (above break-even 0.30); interior dip to 0.20.
    crossing = scan_interior_crossing(
        shares=[0.40, 0.35, 0.20, 0.33, 0.41],
        q_volumes=[1000.0, 2000.0, 3000.0, 4000.0, 5000.0],
        break_even_share=0.30,
    )
    assert crossing.interior_crossing is True
    assert 3000.0 in crossing.crossing_q_volumes


def test_no_interior_crossing_when_surface_stays_above_break_even() -> None:
    """A surface entirely above break-even sets interior_crossing False."""
    crossing = scan_interior_crossing(
        shares=[0.40, 0.45, 0.42, 0.41],
        q_volumes=[1000.0, 2000.0, 3000.0, 4000.0],
        break_even_share=0.30,
    )
    assert crossing.interior_crossing is False
    assert crossing.crossing_q_volumes == ()


def test_surface_raises_when_range_cannot_be_covered() -> None:
    """If the surface cannot be evaluated across the anchored range
    (no decomposition cells), SurfaceGridError is raised."""
    module = SurfaceGridModule()
    with pytest.raises(SurfaceGridError):
        module((), break_even_share=0.30, grid_resolution=100.0)
