"""Unit tests — FX-variance-share surface-grid evaluator (spec v0.7
§4.3 / §4.4; plan tasks 4.2 / 4.2a / CORR-E10P-11).

Phase-0 RED harness lines 51-90 (the four original failing tests) are
preserved verbatim and now go GREEN against the Phase-4 implementation.

Phase-4 additions verify:
- the user-locked >=3-contiguous strictly-interior rule for
  ``detect_interior_crossing`` (the production rule of 2026-05-21);
- the user-locked log-spaced 50-point grid + adaptive doubling rule
  in ``evaluate_surface_grid``;
- the ``q_variance_dominance_flag`` emit per pre-Phase-4 Model QA
  review item 6;
- the grid-resolution decision-citation presence on the result;
- endpoint-violation vs interior-crossing distinction.
"""

from __future__ import annotations

import math

import pytest

from simulations.e10_gsps._errors import SurfaceGridError
from simulations.e10_gsps.modules.surface_grid import (
    DEFAULT_BASE_N,
    DEFAULT_REFINED_N,
    SurfaceGridModule,
    detect_interior_crossing,
    evaluate_surface_grid,
    scan_interior_crossing,
)
from simulations.e10_gsps.types import (
    PanelCell,
    ThreeWayDecompositionCell,
)


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


# ── Phase-4 additions ──────────────────────────────────────────────────


def _make_panel_cell(
    *,
    currency: str,
    year: int,
    month: int,
    fx_share: float,
) -> PanelCell:
    """Synthetic ``PanelCell`` carrying only the share-relevant fields
    for the surface evaluator."""
    decomp = ThreeWayDecompositionCell(
        currency=currency,
        year=year,
        month=month,
        var_total=1.0,
        var_fx=fx_share,
        var_q=1.0 - fx_share,
        cov_term=0.0,
        grid_index_length=20,
        identity_residual=0.0,
    )
    return PanelCell(
        currency=currency,
        year=year,
        month=month,
        x_realized_variance=fx_share,
        y_realized_variance=1.0,
        decomposition=decomp,
        n_fx_trading_days=20,
        n_surviving_days=10,
        material_gap=False,
        fx_variance_share=fx_share,
        qualifying=True,
        seed=42,
    )


def _panel_at_share(share: float, n: int = 30) -> tuple[PanelCell, ...]:
    """Build a single-currency panel of n cells all carrying the same
    FX-variance share — used to test the q_variance_dominance_flag and
    the user-locked grid behaviour."""
    return tuple(
        _make_panel_cell(
            currency="COP",
            year=2024 + (i // 12),
            month=1 + (i % 12),
            fx_share=share,
        )
        for i in range(n)
    )


# Task 4.2a — user-locked >=3-contiguous strictly-interior rule.


def test_detect_interior_crossing_single_cell_does_not_flag() -> None:
    """Per the user-locked rule (2026-05-21), a single interior cell
    below break-even MUST NOT flag (1-cell dip is dominated by simulator
    noise)."""
    # Endpoints clear; interior has one isolated dip at index 2.
    result = detect_interior_crossing(
        shares=[0.40, 0.35, 0.20, 0.33, 0.41],
        break_even_share=0.30,
    )
    assert result.interior_crossing is False
    assert result.interior_runs == ()


def test_detect_interior_crossing_two_contiguous_cells_do_not_flag() -> None:
    """Per the user-locked rule, a 2-cell contiguous interior dip MUST
    NOT flag — only >=3 contiguous strictly-interior cells qualify."""
    # Endpoints clear; interior has a 2-cell dip at indices 2 and 3.
    result = detect_interior_crossing(
        shares=[0.40, 0.35, 0.20, 0.22, 0.41, 0.45],
        break_even_share=0.30,
    )
    assert result.interior_crossing is False


def test_detect_interior_crossing_three_contiguous_strictly_interior_flags() -> None:
    """Per the user-locked rule, a 3-cell contiguous strictly-interior
    dip DOES flag."""
    # Endpoints clear; interior has a 3-cell dip at indices 2, 3, 4.
    result = detect_interior_crossing(
        shares=[0.40, 0.35, 0.20, 0.22, 0.18, 0.41, 0.45],
        break_even_share=0.30,
    )
    assert result.interior_crossing is True
    assert len(result.interior_runs) == 1
    start, end = result.interior_runs[0]
    assert end - start + 1 >= 3
    # Strictly interior — first and last grid indices excluded.
    assert start >= 1
    assert end <= len(result.crossing_q_volumes) - 2 or end <= 5


def test_detect_interior_crossing_endpoint_dip_reported_separately() -> None:
    """An endpoint dip is reported via endpoint_below_low /
    endpoint_below_high, NOT via interior_crossing."""
    # Low endpoint dips; interior clear.
    result = detect_interior_crossing(
        shares=[0.10, 0.35, 0.40, 0.45],
        break_even_share=0.30,
    )
    assert result.interior_crossing is False
    assert result.endpoint_below_low is True
    assert result.endpoint_below_high is False

    # High endpoint dips; interior clear.
    result = detect_interior_crossing(
        shares=[0.40, 0.35, 0.40, 0.10],
        break_even_share=0.30,
    )
    assert result.interior_crossing is False
    assert result.endpoint_below_low is False
    assert result.endpoint_below_high is True


def test_no_interior_crossing_with_clean_surface_under_user_locked_rule() -> None:
    """A surface entirely above break-even sets interior_crossing
    False under the user-locked rule (regression check)."""
    result = detect_interior_crossing(
        shares=[0.40, 0.45, 0.42, 0.41, 0.50, 0.48, 0.43],
        break_even_share=0.30,
    )
    assert result.interior_crossing is False


# Task 4.2 — user-locked log-spaced 50-pt grid + adaptive doubling.


def test_evaluate_surface_grid_base_grid_size_default_50() -> None:
    """Per the user-locked decision (2026-05-21), the base grid is
    log-spaced 50 points when no adaptive doubling triggers."""
    # Share well below s_be -> no adaptive doubling.
    panel = _panel_at_share(0.0002)
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    assert result.effective_n_grid == DEFAULT_BASE_N
    assert result.refined is False
    assert len(result.points) == DEFAULT_BASE_N


def test_evaluate_surface_grid_log_spacing_geometric_in_q() -> None:
    """Log-spacing: consecutive q_volume ratios are constant."""
    panel = _panel_at_share(0.0002)
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    qs = [pt.q_volume for pt in result.points]
    first_ratio = qs[1] / qs[0]
    last_ratio = qs[-1] / qs[-2]
    assert math.isclose(first_ratio, last_ratio, rel_tol=1e-9)


def test_evaluate_surface_grid_q_variance_dominance_flag_true_for_low_share() -> None:
    """When the panel share is far below s_be (Phase-3 empirical case),
    q_variance_dominance_flag is True (the §9 NON-RETIREMENT rung input
    fires)."""
    panel = _panel_at_share(0.0002)  # Phase-3 panel-mean.
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    assert result.q_variance_dominance_flag is True


def test_evaluate_surface_grid_q_variance_dominance_flag_false_when_share_above_s_be() -> None:
    """When the panel share exceeds s_be at every grid point,
    q_variance_dominance_flag is False (FX vol dominates — the
    surface-produced rung input fires)."""
    panel = _panel_at_share(0.40)  # Above s_be=0.25.
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    assert result.q_variance_dominance_flag is False


def test_evaluate_surface_grid_adaptive_doubling_triggers_near_s_be() -> None:
    """Per the user-locked rule, if any cell sits within +/-0.5 dex of
    s_be the grid refines to 100 log-spaced points."""
    # Share exactly equal to s_be -- well within +/-0.5 dex.
    panel = _panel_at_share(0.25)
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    assert result.refined is True
    assert result.effective_n_grid == DEFAULT_REFINED_N


def test_evaluate_surface_grid_no_adaptive_doubling_far_from_s_be() -> None:
    """A share many orders of magnitude below s_be does NOT trigger
    adaptive doubling -- it sits well outside the +/-0.5 dex band."""
    # 0.0002 sits ~3 dex below s_be=0.25, far outside +/-0.5 dex.
    panel = _panel_at_share(0.0002)
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    assert result.refined is False


def test_evaluate_surface_grid_carries_decision_citation() -> None:
    """The user-locked grid decision-citation MUST be present on the
    result (4-part: reference / why / relevance / connection)."""
    panel = _panel_at_share(0.0002)
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    citation = result.grid_resolution_decision_citation
    assert "Reference:" in citation
    assert "Why:" in citation
    assert "Relevance:" in citation
    assert "Connection:" in citation
    assert "user lock 2026-05-21" in citation
    assert "log-spaced 50 points" in citation


def test_evaluate_surface_grid_raises_on_invalid_q_range() -> None:
    """A degenerate or non-positive Q-range raises SurfaceGridError --
    the data-fetch gate is non-bypassable."""
    panel = _panel_at_share(0.0002)
    # Lower bound non-positive.
    with pytest.raises(SurfaceGridError):
        evaluate_surface_grid(panel, q_range=(0.0, 130.0))
    # Lower bound >= upper bound.
    with pytest.raises(SurfaceGridError):
        evaluate_surface_grid(panel, q_range=(130.0, 28.0))


def test_evaluate_surface_grid_raises_on_empty_panel() -> None:
    """An empty panel cannot be evaluated."""
    with pytest.raises(SurfaceGridError):
        evaluate_surface_grid((), q_range=(28.0, 130.0))


def test_evaluate_surface_grid_anchored_range_recorded() -> None:
    """The anchored Q-range bounds are recorded on the result."""
    panel = _panel_at_share(0.0002)
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    assert result.anchored_range_low == 28.0
    assert result.anchored_range_high == 130.0
    # The first and last grid points sit at the anchored bounds.
    assert math.isclose(result.points[0].q_volume, 28.0, rel_tol=1e-9)
    assert math.isclose(result.points[-1].q_volume, 130.0, rel_tol=1e-9)


def test_evaluate_surface_grid_break_even_default_is_phase_2_5_pinned() -> None:
    """The default ``s_be`` is the Phase-2.5 ex-ante-pinned 0.25."""
    panel = _panel_at_share(0.0002)
    result = evaluate_surface_grid(panel, q_range=(28.0, 130.0))
    assert result.break_even_share == 0.25
