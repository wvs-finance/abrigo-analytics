"""Panel construction — the 5-currency × ~30-month E10 panel (plan task 3.x).

Assembles the per-(currency, month) panel cell: the X-side FX realized
variance (spec v0.6 §3.2), the Y-side cost-stream realized variance
(§5.2), and the exact §4.2 three-way log-variance decomposition (§4.2),
all on the plan-task-3.0 common daily within-month differencing grid.

The common differencing grid (plan task 3.0 / CORR-E10P-3)
----------------------------------------------------------
The exact §4.2 identity ``Var(Δlog cost) = Var(Δlog FX) + Var(Δlog Q) +
2·Cov`` holds cell-by-cell exactly only when X and the Q-component are
differenced on an *identical* sub-monthly index. The grid is the FX
trading days the central bank quotes (one FX rate per day); the NHPP
simulator emits one daily Q count per FX day (the engine aligns the
trajectory to the FX path length).

The daily gapped-grid decomposition (spec v0.7 CORRECTIONS-E10-7)
----------------------------------------------------------------
``cost = Q × $0.01 × FX``; a day with zero priceable queries has zero
cost, and ``Δlog cost`` is undefined there. The calibrated Cox Q-process
(E10.1 §3 — daily VMR ≈ 20, decisively overdispersed) concentrates query
mass into sprint days, so ~51% of background days carry Q = 0. Per spec
v0.7 §3.2 / §4.2 / §5.2 (CORRECTIONS-E10-7) the X realized variance, the
Y realized variance, and the §4.2 three-way decomposition are ALL
computed on the **daily grid restricted to non-zero-Q days** — the
common surviving index. The drop is *forced by the log domain* (Δlog of a
zero is undefined), not a discretionary filter. Per cell the construction
drops the zero-Q days and differences the surviving days. FX and Q are
dropped on the SAME surviving index, so the common gapped grid is
preserved and the exact identity still holds:
``log(cost_b) − log(cost_a) = (log Q_b − log Q_a) + (log FX_b − log FX_a)``
is exact for ANY pair of days on which Q, FX, and cost are all positive.

There is exactly ONE canonical X per (currency, month) cell — the
realized variance of Δlog(FX) on the surviving non-zero-Q-day common
index. ``PanelCell.x_realized_variance`` and ``decomposition.var_fx`` are
the SAME gapped-grid FX object (spec v0.7 reconciliation; the v0.6
two-divergent-FX-objects condition — a full-daily-grid X alongside a
gapped-grid ``var_fx`` — is CLOSED). The full-daily-grid FX realized
variance is no longer carried on the panel cell.

A cell with fewer than two surviving positive-Q days cannot be
log-differenced and carries ``material_gap = True`` (routes to the §9
descriptive ladder; the decomposition still computes for every cell that
has ≥ 2 surviving days — all 150 panel cells do).

Discipline
----------
``modules``-tier: frozen-dataclass stateless containers + free pure
functions; no mutable state, no imports from ``..utils``. The numeric FX
values are 100% real central-bank data (fantasy-firewall enforced); Q is
the only simulated quantity.
"""

from __future__ import annotations

from collections.abc import Sequence

from simulations.e10_gsps._errors import DecompositionIdentityError
from simulations.e10_gsps.modules.decomposition import decompose_cell
from simulations.e10_gsps.modules.differencing_grid import (
    GridAlignmentReport,
    verify_cell_grid,
)
from simulations.e10_gsps.modules.realized_variance import (
    daily_log_returns,
    realized_variance_sum,
)
from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    MonthlyRealizedVarianceCell,
    PanelCell,
    ThreeWayDecompositionCell,
)

# A cell needs at least this many surviving positive-Q days for its daily
# log-returns (one fewer than the day count) to be non-empty.
# Phase-3 review I-1 (2026-05-21): with n=2 the decomposition produces a
# single log-return and population variance is degenerate (=0, share=NaN).
# Spec v0.7 pins this threshold at 2; a future CORRECTIONS-E10-8 amendment
# will raise it to 3 (methodologically correct). No production cell hits
# this: all 150 panel cells have far more than 3 surviving days.
_MIN_SURVIVING_DAYS: int = 2


def _drop_zero_query_days(
    daily_query_counts: Sequence[int],
    daily_fx_rate: Sequence[float],
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    """Drop the zero-Q days from a (Q, FX) daily pair on the common grid.

    A zero-query day has zero cost; ``Δlog cost`` is undefined there.
    Q and FX are filtered on the SAME index so the surviving grid is
    common to both — the exact §4.2 identity is preserved.

    Args:
        daily_query_counts: The daily simulated query counts.
        daily_fx_rate: The matching daily real FX rates — MUST share the
            ``daily_query_counts`` index.

    Returns:
        The surviving (positive-Q) ``(query_counts, fx_rates)`` pair, in
        original order.

    Raises:
        DecompositionIdentityError: the two inputs have unequal length —
            they are not on a common grid (plan task 3.0).
    """
    if len(daily_query_counts) != len(daily_fx_rate):
        raise DecompositionIdentityError(
            f"zero-day drop grid mismatch: {len(daily_query_counts)} Q "
            f"observations vs {len(daily_fx_rate)} FX observations; the "
            f"two must share one daily index (plan task 3.0)."
        )
    surviving = [
        (q, fx)
        for q, fx in zip(daily_query_counts, daily_fx_rate, strict=True)
        if q > 0
    ]
    if not surviving:
        return ((), ())
    q_out, fx_out = zip(*surviving, strict=True)
    return (tuple(q_out), tuple(fx_out))


def build_panel_cell(
    fx_cell: MonthlyRealizedVarianceCell,
    trajectory: CostStreamTrajectory,
) -> PanelCell:
    """Assemble one (currency, month) panel cell — X, Y, and the §4.2 split.

    Per spec v0.7 §3.2 (CORRECTIONS-E10-7) the canonical X is the realized
    variance of Δlog(FX) on the surviving non-zero-Q-day common index —
    NOT the full daily grid. ``PanelCell.x_realized_variance`` is set to
    that gapped-grid quantity; ``fx_cell`` is used only for the cell
    identity, the qualifying flag, and the daily FX trading-day count.

    Args:
        fx_cell: The X-side FX realized-variance cell — supplies the cell
            identity, the qualifying flag, and the daily FX trading-day
            count. ``fx_cell.realized_log_variance`` (the full-daily-grid
            FX variance) is NOT carried onto the panel cell — the panel X
            is the gapped-grid quantity computed here.
        trajectory: The matching simulated cost-stream trajectory — the
            daily Q counts, the real daily FX path, and the daily cost.

    Returns:
        A ``PanelCell`` with X, Y, the exact decomposition (all on the
        surviving non-zero-Q-day common grid), and the FX-variance share.
        ``x_realized_variance`` is the SAME gapped-grid FX object as
        ``decomposition.var_fx`` — up to the sum-vs-population convention,
        both are computed from the identical surviving ``Δlog FX`` series.

    Raises:
        DecompositionIdentityError: the trajectory's Q and FX daily
            indices do not share a common grid (plan task 3.0); OR the
            §4.2 additive identity fails on the surviving grid.
        ValueError: a surviving daily FX rate or cost is non-positive
            (``Δlog`` undefined) — signals upstream data corruption.
    """
    q_surv, fx_surv = _drop_zero_query_days(
        trajectory.daily_query_counts, trajectory.daily_fx_rate
    )
    n_surviving = len(q_surv)
    material_gap = n_surviving < _MIN_SURVIVING_DAYS

    # The canonical X (spec v0.7 §3.2 / CORRECTIONS-E10-7): realized
    # variance of Δlog(FX) on the surviving non-zero-Q-day common index.
    # ``fx_returns`` is empty when fewer than two days survive — then the
    # sum-of-squares is 0.0, matching the zeroed decomposition cell below.
    fx_returns = daily_log_returns(fx_surv)
    x_realized_variance = realized_variance_sum(fx_returns)

    if material_gap:
        # Too few positive-Q days to log-difference — the decomposition is
        # not computable for this cell. Emit a zeroed decomposition cell
        # flagged via ``material_gap``; the cell routes to the §9 ladder.
        empty = ThreeWayDecompositionCell(
            currency=fx_cell.currency,
            year=fx_cell.year,
            month=fx_cell.month,
            var_total=0.0,
            var_fx=0.0,
            var_q=0.0,
            cov_term=0.0,
            grid_index_length=n_surviving,
            identity_residual=0.0,
        )
        return PanelCell(
            currency=fx_cell.currency,
            year=fx_cell.year,
            month=fx_cell.month,
            x_realized_variance=x_realized_variance,
            y_realized_variance=0.0,
            decomposition=empty,
            n_fx_trading_days=fx_cell.n_trading_days,
            n_surviving_days=n_surviving,
            material_gap=True,
            fx_variance_share=float("nan"),
            qualifying=fx_cell.qualifying,
            seed=trajectory.seed,
        )

    q_returns = daily_log_returns(tuple(float(q) for q in q_surv))
    cost_returns = tuple(
        f + q for f, q in zip(fx_returns, q_returns, strict=True)
    )

    decomp = decompose_cell(
        fx_log_returns=fx_returns, q_log_returns=q_returns
    )
    decomposition = ThreeWayDecompositionCell(
        currency=fx_cell.currency,
        year=fx_cell.year,
        month=fx_cell.month,
        var_total=decomp.var_total,
        var_fx=decomp.var_fx,
        var_q=decomp.var_q,
        cov_term=decomp.cov_term,
        grid_index_length=n_surviving,
        identity_residual=decomp.identity_residual,
    )

    share = (
        decomp.var_fx / decomp.var_total
        if decomp.var_total > 0.0
        else float("nan")
    )
    return PanelCell(
        currency=fx_cell.currency,
        year=fx_cell.year,
        month=fx_cell.month,
        x_realized_variance=x_realized_variance,
        y_realized_variance=realized_variance_sum(cost_returns),
        decomposition=decomposition,
        n_fx_trading_days=fx_cell.n_trading_days,
        n_surviving_days=n_surviving,
        material_gap=False,
        fx_variance_share=share,
        qualifying=fx_cell.qualifying,
        seed=trajectory.seed,
    )


def verify_panel_grids(
    cells: Sequence[tuple[MonthlyRealizedVarianceCell, CostStreamTrajectory]],
) -> tuple[GridAlignmentReport, ...]:
    """Emit the index-alignment verification artifact for the panel.

    For each (FX cell, trajectory) pair, asserts the daily FX index and
    the daily Q index share a common length (plan task 3.0). Any mismatch
    raises before the panel is assembled.

    Args:
        cells: The (FX cell, trajectory) pairs to verify.

    Returns:
        One ``GridAlignmentReport`` per cell — the task-3.0 deliverable.

    Raises:
        DecompositionIdentityError: any cell's FX and Q daily indices have
            unequal length.
    """
    return tuple(
        verify_cell_grid(
            currency=fx_cell.currency,
            year=fx_cell.year,
            month=fx_cell.month,
            fx_index_length=len(traj.daily_fx_rate),
            q_index_length=len(traj.daily_query_counts),
        )
        for fx_cell, traj in cells
    )


__all__ = [
    "PanelCell",
    "build_panel_cell",
    "verify_panel_grids",
]
