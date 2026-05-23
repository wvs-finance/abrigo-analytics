"""Common X/Q sub-monthly differencing grid (plan task 3.0 / CORR-E10P-3).

The exact §4.2 three-way log-variance decomposition

    Var(d log cost) = Var(d log FX) + Var(d log Q) + 2 * Cov(d log FX, d log Q)

holds cell-by-cell EXACTLY only when X (d log FX) and the Q-component
(d log Q) are differenced on an *identical* sub-monthly observation
index. Per Model QA Strong-2 (plan CORR-E10P-3), a decomposition that
differences X and Q on mismatched grids silently violates the additive
identity — the cross-term is then computed against misaligned pairs.

What this module pins
---------------------
The common grid for a (currency, month) cell is the **daily FX trading
index** — one observation per central-bank-quoted FX day. The NHPP
simulator emits intra-day arrivals; ``CostStreamTrajectory`` already
aggregates them to one daily query count per FX day (``nhpp_engine``
aligns the trajectory to the FX path length). This module's job is the
verification: it asserts X and the Q-component share the same daily
index length per cell and emits an index-alignment artifact.

The level series ``FX`` and ``Q`` each have ``n`` daily observations on
the common grid; differencing (``d log``) yields ``n - 1`` log-returns.
Both series are differenced on the SAME ``n``-point index, so both
log-return series have the same ``n - 1`` length — the precondition for
the exact identity.

Discipline
----------
``modules``-tier: frozen-dataclass stateless callable + free pure
functions; no mutable state, no imports from ``..utils``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from simulations.e10_gsps._errors import DecompositionIdentityError


@dataclass(frozen=True, slots=True)
class GridAlignmentReport:
    """Index-alignment verification artifact for one (currency, month)
    cell (plan task 3.0 deliverable).

    ``currency`` / ``year`` / ``month`` identify the cell. ``fx_index_length``
    is the count of daily FX level observations; ``q_index_length`` is the
    count of daily Q level observations (the simulator's intra-day arrivals
    aggregated to the daily grid). ``aligned`` is True iff the two indices
    have equal length — the precondition for the exact §4.2 identity.
    ``log_return_length`` is the common differenced-series length
    (``fx_index_length - 1`` when aligned).
    """

    currency: str
    year: int
    month: int
    fx_index_length: int
    q_index_length: int
    aligned: bool
    log_return_length: int


def verify_cell_grid(
    *,
    currency: str,
    year: int,
    month: int,
    fx_index_length: int,
    q_index_length: int,
) -> GridAlignmentReport:
    """Verify X and the Q-component share a common daily differencing grid.

    Args:
        currency: The panel currency code.
        year: Calendar year of the cell.
        month: Calendar month (1-12) of the cell.
        fx_index_length: Count of daily FX level observations in the cell.
        q_index_length: Count of daily Q level observations in the cell —
            the NHPP simulator's intra-day arrivals aggregated to the
            daily grid (``CostStreamTrajectory.daily_query_counts``).

    Returns:
        A ``GridAlignmentReport`` recording whether the two indices align
        and the resulting common log-return length.

    Raises:
        DecompositionIdentityError: the two indices have unequal length —
            X and Q would be differenced on mismatched grids and the exact
            §4.2 identity would not hold cell-by-cell. The decomposition
            never silently computes an inexact identity (plan CORR-E10P-3).
    """
    aligned = fx_index_length == q_index_length
    if not aligned:
        raise DecompositionIdentityError(
            f"{currency} {year}-{month:02d}: FX daily index has "
            f"{fx_index_length} observations but the Q daily index has "
            f"{q_index_length}; X and Q must be differenced on an identical "
            f"sub-monthly grid for the exact §4.2 identity to hold "
            f"cell-by-cell (plan task 3.0 / CORR-E10P-3)."
        )
    return GridAlignmentReport(
        currency=currency,
        year=year,
        month=month,
        fx_index_length=fx_index_length,
        q_index_length=q_index_length,
        aligned=True,
        log_return_length=max(fx_index_length - 1, 0),
    )


def assert_common_grid(
    fx_level: Sequence[float], q_level: Sequence[float]
) -> int:
    """Assert two daily level series lie on a common differencing grid.

    Args:
        fx_level: Daily FX level observations for one cell.
        q_level: Daily Q level observations for the same cell.

    Returns:
        The common index length ``n`` (== ``len(fx_level)``).

    Raises:
        DecompositionIdentityError: the two series have unequal length —
            they cannot be differenced on a common grid.
    """
    n_fx, n_q = len(fx_level), len(q_level)
    if n_fx != n_q:
        raise DecompositionIdentityError(
            f"common-grid violation: FX level series has {n_fx} daily "
            f"observations, Q level series has {n_q}; the two must share "
            f"one sub-monthly index before differencing (plan task 3.0)."
        )
    return n_fx


__all__ = [
    "GridAlignmentReport",
    "assert_common_grid",
    "verify_cell_grid",
]
