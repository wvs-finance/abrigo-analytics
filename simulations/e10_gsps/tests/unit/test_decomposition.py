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


def test_module_decomposes_on_surviving_gapped_grid() -> None:
    """Plan task 3.0 + spec v0.7 CORRECTIONS-E10-7: the module aggregates
    the NHPP intra-day arrivals to a daily Q index, drops the zero-Q days
    on the common index, and decomposes on the surviving gapped grid. The
    decomposed cell's grid_index_length is the surviving non-zero-Q-day
    log-return count."""
    fx_cell = MonthlyRealizedVarianceCell(
        currency="COP",
        year=2025,
        month=3,
        realized_log_variance=0.0009,
        n_trading_days=20,
        qualifying=True,
    )
    # 20 daily FX days; days 4 and 11 (0-indexed) carry zero queries —
    # they are dropped on the common index, leaving 18 surviving days.
    counts = tuple(
        0 if i in (4, 11) else 100 + i for i in range(20)
    )
    traj = CostStreamTrajectory(
        currency="COP",
        year=2025,
        month=3,
        daily_query_counts=counts,
        daily_fx_rate=tuple(4000.0 + i for i in range(20)),
        daily_cost=tuple(
            counts[i] * 0.01 * (4000.0 + i) for i in range(20)
        ),
        seed=7,
    )
    module = ThreeWayDecompositionModule()
    cell = module(fx_cell, traj)
    # 18 surviving days ⇒ 17 daily log-returns on the gapped grid.
    assert cell.grid_index_length == 17
    # The exact §4.2 identity still holds on the surviving gapped grid.
    residual = cell.var_total - (cell.var_fx + cell.var_q + cell.cov_term)
    assert abs(residual) < _IDENTITY_TOL


def test_covariance_term_near_zero_under_qfx_independence() -> None:
    """Spec v0.4 §6.4: under primary-spec Q-perp-FX independence the
    covariance term is approximately zero.

    The fixtures are two mean-zero log-return series constructed to be
    EXACTLY uncorrelated — ``q_lr`` is orthogonal to ``fx_lr`` (their
    centred inner product is zero). Under that genuine independence the
    §4.2 covariance term ``2·Cov(Δlog FX, Δlog Q)`` is exactly zero, and
    the exact additive identity collapses to ``var_total = var_fx +
    var_q``. (The earlier fixture pair was near-perfectly *anti*-correlated
    despite the docstring — it did not model independence; Cauchy-Schwarz
    permits ``|2·Cov| > var_total`` whenever Δlog FX and Δlog Q are
    strongly negatively correlated, so the old ``|cov| <= var_total``
    bound was not a universal property.)"""
    # fx_lr: mean-zero, symmetric. q_lr: mean-zero and orthogonal to fx_lr
    # — a sign pattern whose centred dot-product with fx_lr is zero, so
    # Cov(fx_lr, q_lr) == 0 exactly.
    fx_lr = [0.01, -0.01, 0.01, -0.01, 0.01, -0.01, 0.01, -0.01]
    q_lr = [0.02, 0.02, -0.02, -0.02, 0.02, 0.02, -0.02, -0.02]
    cell = decompose_cell(fx_log_returns=fx_lr, q_log_returns=q_lr)
    # Genuine independence ⇒ the covariance term is exactly zero.
    assert abs(cell.cov_term) < _IDENTITY_TOL
    # ⇒ the exact identity collapses to var_total == var_fx + var_q.
    assert abs(cell.var_total - (cell.var_fx + cell.var_q)) < _IDENTITY_TOL
    # And the universal Cauchy-Schwarz bound on the covariance holds.
    assert abs(cell.cov_term) <= 2.0 * (cell.var_fx * cell.var_q) ** 0.5 + _IDENTITY_TOL
