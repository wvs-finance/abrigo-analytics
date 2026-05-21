"""Realized-variance constructors — X-side and Y-side (plan tasks 3.1 / 3.2).

Two realized-variance objects, both computed on the plan-task-3.0 common
daily within-month differencing grid.

X-side (task 3.1)
-----------------
Per spec v0.6 §3.2, the panel X cell is the **realized variance of
Δlog(FX)** for one (currency, month): the within-month **sum of squared
daily log-returns** (the sum-vs-mean convention is fixed at pre-pin —
sum). NGN is confined to its post-June-2023 float window upstream by the
``regime_break`` screen; this module differences whatever daily FX level
series it is handed.

Y-side (task 3.2)
-----------------
Per spec v0.6 §5.2, the panel Y cell is the realized variance of Δlog of
the local-currency cost stream ``cost = Q × $0.01 × FX``, on the same
common grid. ``build_cost_variance_cell`` differences the trajectory's
daily cost series with the same sum-of-squares convention.

The decomposition operator
--------------------------
The exact §4.2 three-way identity is stated for the **variance operator**
``Var(·)``. Both the sum-of-squared-returns convention and the
population-variance convention satisfy an exact additive identity
(``Σ(a+b)² = Σa² + Σb² + 2Σab`` and ``Var(a+b) = Var a + Var b + 2Cov``).
This module exposes both conventions so the panel X/Y cells carry the
spec-§3.2 sum convention while the decomposition (``decomposition.py``)
uses a single consistent operator internally.

Discipline
----------
``modules``-tier: frozen-dataclass stateless callables + free pure
functions; no mutable state, no imports from ``..utils``. The numeric FX
values are 100% real central-bank data (the fantasy-firewall enforces
this); this module only differences and squares them.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    MonthlyRealizedVarianceCell,
)


def daily_log_returns(level: Sequence[float]) -> tuple[float, ...]:
    """Daily log-returns of a within-month level series.

    Δlog at index t is ``log(level[t]) - log(level[t-1])``. A length-``n``
    level series yields ``n - 1`` log-returns on the common differencing
    grid (plan task 3.0).

    Args:
        level: The within-month daily level series (FX rate or cost),
            strictly positive.

    Returns:
        The ``len(level) - 1`` daily log-returns; an empty tuple for a
        series shorter than 2 observations.

    Raises:
        ValueError: a level observation is non-positive — a log-return
            of a non-positive level is undefined; the constructor never
            silently coerces (an FX rate or cost of 0 signals upstream
            data corruption).
    """
    if len(level) < 2:
        return ()
    for x in level:
        if x <= 0.0:
            raise ValueError(
                f"level series contains a non-positive value ({x}); "
                f"Δlog is undefined — the realized-variance constructor "
                f"never coerces a corrupt level observation."
            )
    logs = [math.log(x) for x in level]
    return tuple(logs[t] - logs[t - 1] for t in range(1, len(logs)))


def realized_variance_sum(log_returns: Sequence[float]) -> float:
    """Realized variance — the spec-§3.2 within-month sum-of-squares.

    ``Σ r_t²`` over the within-month daily log-returns. This is the
    sum-vs-mean convention fixed at pre-pin (spec v0.6 §3.2 — sum). It is
    the value carried in ``MonthlyRealizedVarianceCell.realized_log_variance``.

    Args:
        log_returns: The within-month daily log-returns.

    Returns:
        The non-negative sum of squared log-returns.
    """
    return float(sum(r * r for r in log_returns))


def population_variance(log_returns: Sequence[float]) -> float:
    """Population variance ``Var(r) = mean(r²) - mean(r)²``.

    The variance operator the exact §4.2 decomposition identity is stated
    against. Population (divisor ``n``) rather than sample (divisor
    ``n-1``) so the additive identity ``Var(a+b) = Var a + Var b + 2Cov``
    holds exactly with the matching population covariance.

    Args:
        log_returns: The within-month daily log-returns.

    Returns:
        The non-negative population variance; ``0.0`` for an empty or
        single-element series.
    """
    n = len(log_returns)
    if n == 0:
        return 0.0
    mean = sum(log_returns) / n
    return float(sum((r - mean) ** 2 for r in log_returns) / n)


def build_fx_variance_cell(
    *,
    currency: str,
    year: int,
    month: int,
    daily_fx_level: Sequence[float],
    qualifying: bool,
) -> MonthlyRealizedVarianceCell:
    """Construct one (currency, month) X-side realized-variance cell.

    Per spec v0.6 §3.2 — the within-month sum of squared daily log-returns
    of the FX rate, on the plan-task-3.0 common daily grid.

    Args:
        currency: The panel currency code.
        year: Calendar year of the cell.
        month: Calendar month (1-12) of the cell.
        daily_fx_level: The within-month daily central-bank FX level
            series (local-currency-per-USD), strictly positive.
        qualifying: Whether the cell lies inside the currency's
            post-regime-break qualifying window (spec v0.6 §3.3 — NGN
            confined to its post-June-2023 float).

    Returns:
        A ``MonthlyRealizedVarianceCell`` whose ``realized_log_variance``
        is the sum-of-squares realized variance and whose
        ``n_trading_days`` is the daily FX level count on the common grid.

    Raises:
        ValueError: an FX level observation is non-positive.
    """
    returns = daily_log_returns(daily_fx_level)
    return MonthlyRealizedVarianceCell(
        currency=currency,
        year=year,
        month=month,
        realized_log_variance=realized_variance_sum(returns),
        n_trading_days=len(daily_fx_level),
        qualifying=qualifying,
    )


@dataclass(frozen=True, slots=True)
class CostVarianceCell:
    """One (currency, month) Y-side cost-stream realized-variance cell.

    ``realized_log_variance`` is the spec-§3.2 sum-of-squares realized
    variance of Δlog(cost); ``n_trading_days`` is the daily cost-series
    length on the common grid (plan task 3.0). ``seed`` records the
    simulator seed of the underlying trajectory for Tier-3 reproducibility.
    """

    currency: str
    year: int
    month: int
    realized_log_variance: float
    n_trading_days: int
    seed: int


def build_cost_variance_cell(
    trajectory: CostStreamTrajectory,
) -> CostVarianceCell:
    """Construct one (currency, month) Y-side cost-stream variance cell.

    Per spec v0.6 §5.2 — the realized variance of Δlog of the
    local-currency cost stream ``cost = Q × $0.01 × FX``, on the common
    daily grid (plan task 3.2).

    Args:
        trajectory: The per-(currency, month) simulated cost-stream
            trajectory — daily Q counts, real FX path, and their product.

    Returns:
        A ``CostVarianceCell`` carrying the sum-of-squares realized
        variance of the daily cost log-returns.

    Raises:
        ValueError: a daily cost observation is non-positive — Δlog is
            undefined (a zero-query day yields a zero cost; a panel cell
            with a zero-cost day cannot be log-differenced and signals an
            upstream Q-aggregation gap).
    """
    returns = daily_log_returns(trajectory.daily_cost)
    return CostVarianceCell(
        currency=trajectory.currency,
        year=trajectory.year,
        month=trajectory.month,
        realized_log_variance=realized_variance_sum(returns),
        n_trading_days=len(trajectory.daily_cost),
        seed=trajectory.seed,
    )


__all__ = [
    "CostVarianceCell",
    "build_cost_variance_cell",
    "build_fx_variance_cell",
    "daily_log_returns",
    "population_variance",
    "realized_variance_sum",
]
