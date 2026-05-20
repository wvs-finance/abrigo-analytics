"""Failing-test harness — exact §4.2 three-way log-variance decomposition.

Plan v0.2 Phase 0.6. RED in Phase 0: imports the not-yet-existent
``simulations.e10_gsps.modules.decomposition`` module, so collection
fails. The decomposition lands in Phase 3 (plan task 3.3).

The harness asserts the EXACT additive identity:

    Var(d log cost) = Var(d log FX) + Var(d log Q) + 2 * Cov(d log FX, d log Q)

Per plan CORR-E10P-3 / Model QA S-2, the identity holds cell-by-cell
EXACTLY only on a common X/Q sub-monthly differencing grid. The harness
therefore feeds X and Q on the SAME and on deliberately MISMATCHED
differencing grids and asserts the identity holds exactly only on the
common grid — it does not merely test the arithmetic on pre-aligned
synthetic inputs.
"""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from simulations.e10_gsps._errors import DecompositionIdentityError
from simulations.e10_gsps.modules.decomposition import (  # noqa: F401 — RED import
    ThreeWayDecompositionModule,
    decompose_cell,
)
from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    MonthlyRealizedVarianceCell,
)

_IDENTITY_TOL = 1e-12


@given(
    fx_log_returns=st.lists(
        st.floats(min_value=-0.2, max_value=0.2, allow_nan=False),
        min_size=16,
        max_size=22,
    ),
    q_log_returns=st.data(),
)
def test_additive_identity_holds_exactly_on_common_grid(
    fx_log_returns: list[float], q_log_returns: st.DataObject
) -> None:
    """On a common differencing grid the additive identity holds exactly
    (residual within floating-point tolerance)."""
    n = len(fx_log_returns)
    q_lr = q_log_returns.draw(
        st.lists(
            st.floats(min_value=-0.3, max_value=0.3, allow_nan=False),
            min_size=n,
            max_size=n,
        )
    )
    cell = decompose_cell(fx_log_returns=fx_log_returns, q_log_returns=q_lr)
    parts = cell.var_fx + cell.var_q + cell.cov_term
    assert abs(cell.var_total - parts) < _IDENTITY_TOL
    assert abs(cell.identity_residual) < _IDENTITY_TOL
    assert cell.grid_index_length == n


def test_mismatched_grid_raises_identity_error() -> None:
    """X and Q on DELIBERATELY mismatched differencing grids (different
    index lengths) must raise DecompositionIdentityError — the module
    must never silently compute an inexact identity."""
    fx_lr = [0.01, -0.02, 0.015, 0.0, -0.01]
    q_lr_short = [0.02, -0.01, 0.0]  # mismatched length
    with pytest.raises(DecompositionIdentityError):
        decompose_cell(fx_log_returns=fx_lr, q_log_returns=q_lr_short)


def test_module_aggregates_q_to_common_daily_grid() -> None:
    """Plan task 3.0: the module aggregates the NHPP intra-day arrivals
    to a daily Q index BEFORE differencing, matching the daily FX index.
    The decomposed cell's grid_index_length must equal the FX cell's
    n_trading_days."""
    fx_cell = MonthlyRealizedVarianceCell(
        currency="COP",
        year=2025,
        month=3,
        realized_log_variance=0.0009,
        n_trading_days=20,
        qualifying=True,
    )
    traj = CostStreamTrajectory(
        currency="COP",
        year=2025,
        month=3,
        daily_query_counts=tuple(100 + i for i in range(20)),
        daily_fx_rate=tuple(4000.0 + i for i in range(20)),
        daily_cost=tuple((100 + i) * 0.01 * (4000.0 + i) for i in range(20)),
        seed=7,
    )
    module = ThreeWayDecompositionModule()
    cell = module(fx_cell, traj)
    assert cell.grid_index_length == fx_cell.n_trading_days


def test_covariance_term_near_zero_under_qfx_independence() -> None:
    """Spec v0.4 §6.4: under primary-spec Q-perp-FX independence the
    covariance term is approximately zero. With FX returns and Q returns
    drawn independently, |cov_term| must be small relative to var_total."""
    fx_lr = [0.01, -0.012, 0.008, -0.005, 0.011, -0.009, 0.006, -0.007]
    q_lr = [-0.02, 0.018, -0.015, 0.022, -0.019, 0.017, -0.021, 0.016]
    cell = decompose_cell(fx_log_returns=fx_lr, q_log_returns=q_lr)
    assert abs(cell.cov_term) <= cell.var_total + _IDENTITY_TOL
