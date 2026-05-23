"""Round-trip / immutability tests for the E10 GSPS types tier (plan task 0.3).

These tests go GREEN in Phase 0 (the types-tier containers are real
deliverables, not stubs). Every container is frozen per the
``functional-python`` discipline; every field round-trips.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest
from hypothesis import given

from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    CurrencyDailyFXRow,
    DescriptiveVerdictResult,
    LambdaModulationSpec,
    MonthlyRealizedVarianceCell,
    NHPPIntensityParameters,
    SurfaceGridResult,
    ThreeWayDecompositionCell,
)
from simulations.e10_gsps.tests.strategies.types_strategies import (
    cost_stream_trajectories,
    currency_daily_fx_rows,
    descriptive_verdict_results,
    lambda_modulation_specs,
    monthly_realized_variance_cells,
    nhpp_intensity_parameters,
    surface_grid_results,
    three_way_decomposition_cells,
)


@given(currency_daily_fx_rows())
def test_currency_daily_fx_row_is_frozen(row: CurrencyDailyFXRow) -> None:
    with pytest.raises(FrozenInstanceError):
        row.fx_rate = 0.0  # type: ignore[misc]


@given(currency_daily_fx_rows())
def test_currency_daily_fx_row_round_trips(row: CurrencyDailyFXRow) -> None:
    assert replace(row) == row


@given(monthly_realized_variance_cells())
def test_monthly_variance_cell_is_frozen(
    cell: MonthlyRealizedVarianceCell,
) -> None:
    with pytest.raises(FrozenInstanceError):
        cell.realized_log_variance = -1.0  # type: ignore[misc]


@given(lambda_modulation_specs())
def test_lambda_modulation_spec_is_frozen(spec: LambdaModulationSpec) -> None:
    with pytest.raises(FrozenInstanceError):
        spec.locked = True  # type: ignore[misc]


@given(nhpp_intensity_parameters())
def test_nhpp_intensity_parameters_is_frozen(
    params: NHPPIntensityParameters,
) -> None:
    with pytest.raises(FrozenInstanceError):
        params.lambda_0 = 0.0  # type: ignore[misc]


@given(nhpp_intensity_parameters())
def test_nhpp_carries_five_lambda_modulation_slots(
    params: NHPPIntensityParameters,
) -> None:
    """The NHPP container must carry exactly the five §6.3 lambda(t)
    modulation slots — Phase 0 holds the slots, not the chosen forms."""
    assert len(params.modulations) == 5


@given(cost_stream_trajectories())
def test_cost_stream_trajectory_is_frozen(
    traj: CostStreamTrajectory,
) -> None:
    with pytest.raises(FrozenInstanceError):
        traj.seed = 0  # type: ignore[misc]


@given(three_way_decomposition_cells())
def test_decomposition_cell_is_frozen(
    cell: ThreeWayDecompositionCell,
) -> None:
    with pytest.raises(FrozenInstanceError):
        cell.var_total = 0.0  # type: ignore[misc]


@given(three_way_decomposition_cells())
def test_decomposition_strategy_satisfies_exact_identity(
    cell: ThreeWayDecompositionCell,
) -> None:
    """The strategy constructs exact-identity cells: var_total equals the
    sum of the three parts (residual exactly zero). This is a sanity
    check on the strategy, not on the Phase-3 decomposition module."""
    parts = cell.var_fx + cell.var_q + cell.cov_term
    assert abs(cell.var_total - parts) < 1e-12


@given(surface_grid_results())
def test_surface_grid_result_is_frozen(result: SurfaceGridResult) -> None:
    with pytest.raises(FrozenInstanceError):
        result.break_even_share = 0.0  # type: ignore[misc]


@given(descriptive_verdict_results())
def test_descriptive_verdict_result_is_frozen(
    result: DescriptiveVerdictResult,
) -> None:
    with pytest.raises(FrozenInstanceError):
        result.verdict = None  # type: ignore[misc,assignment]
