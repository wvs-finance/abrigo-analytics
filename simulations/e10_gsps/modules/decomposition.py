"""Exact three-way log-variance decomposition (spec v0.6 §4.2; plan task 3.3).

The decisive empirical object of E10. Because the per-query price ``c =
$0.01`` is constant, ``cost = Q × c × FX`` makes

    Δlog cost = Δlog Q + Δlog FX

an EXACT pointwise identity. The variance of a sum is exactly the sum of
variances plus twice the covariance, so

    Var(Δlog cost) = Var(Δlog FX) + Var(Δlog Q) + 2·Cov(Δlog FX, Δlog Q)

is EXACT — no higher-order term, no leading-order approximation (spec
v0.6 §4.2).

The common-grid precondition (plan CORR-E10P-3 / task 3.0)
----------------------------------------------------------
The identity holds cell-by-cell exactly only when X (``Δlog FX``) and the
Q-component (``Δlog Q``) are differenced on an *identical* sub-monthly
index. ``decompose_cell`` is handed two log-return sequences and rejects
mismatched lengths with ``DecompositionIdentityError`` — it never
silently computes an inexact identity against misaligned pairs.
``ThreeWayDecompositionModule`` enforces the precondition upstream by
deriving both Δlog series from the SAME daily grid: the FX cell's daily
index and the simulator trajectory's daily Q index, which the NHPP engine
already aligns to one shared daily length.

The variance operator
---------------------
The decomposition uses the **population variance** ``Var(z) = mean(z²) -
mean(z)²`` and the matching **population covariance**, for which the
additive identity ``Var(a+b) = Var a + Var b + 2Cov(a,b)`` holds exactly.
This is the literal ``Var`` of spec §4.2. (The panel X/Y cells separately
carry the spec-§3.2 sum-of-squares realized variance — see
``realized_variance.py``.)

Discipline
----------
``modules``-tier: frozen-dataclass stateless callable + free pure
functions; no mutable state, no imports from ``..utils``.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from simulations.e10_gsps._errors import DecompositionIdentityError
from simulations.e10_gsps.modules.realized_variance import (
    daily_log_returns,
    population_variance,
)
from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    MonthlyRealizedVarianceCell,
    ThreeWayDecompositionCell,
)

# The exact identity is verified to floating-point tolerance; a residual
# above this signals a real (non-rounding) decomposition error.
_IDENTITY_TOL: float = 1e-12


def _population_covariance(
    a: Sequence[float], b: Sequence[float]
) -> float:
    """Population covariance ``Cov(a, b) = mean(a·b) - mean(a)·mean(b)``.

    Args:
        a: First daily log-return series.
        b: Second daily log-return series — MUST share ``a``'s index.

    Returns:
        The population covariance; ``0.0`` for empty inputs.

    Raises:
        DecompositionIdentityError: ``a`` and ``b`` have unequal length —
            the covariance of two mismatched-grid series is meaningless
            (plan CORR-E10P-3).
    """
    if len(a) != len(b):
        raise DecompositionIdentityError(
            f"covariance grid mismatch: series of length {len(a)} and "
            f"{len(b)}; X and Q must be differenced on a common grid."
        )
    n = len(a)
    if n == 0:
        return 0.0
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    return float(
        sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b, strict=True))
        / n
    )


def decompose_cell(
    *,
    fx_log_returns: Sequence[float],
    q_log_returns: Sequence[float],
) -> ThreeWayDecompositionCell:
    """Decompose one (currency, month) cell's cost-stream log-variance.

    Computes the exact §4.2 three-way additive identity on the common
    differencing grid the two log-return series share.

    Args:
        fx_log_returns: The within-month daily log-returns of FX
            (``Δlog FX``) on the common grid.
        q_log_returns: The within-month daily log-returns of the Q index
            (``Δlog Q``) on the SAME common grid — MUST have the same
            length as ``fx_log_returns``.

    Returns:
        A ``ThreeWayDecompositionCell`` with ``var_fx``, ``var_q``,
        ``cov_term`` (= ``2·Cov``), ``var_total`` (= the sum of the three,
        which equals ``Var(Δlog cost)`` exactly because ``Δlog cost =
        Δlog FX + Δlog Q``), ``grid_index_length`` (the common log-return
        index length), and ``identity_residual`` (≈ 0 on the common grid).
        ``currency`` / ``year`` / ``month`` are left blank — this primitive
        operates on raw log-returns; ``ThreeWayDecompositionModule`` is the
        cell-identified entry point.

    Raises:
        DecompositionIdentityError: ``fx_log_returns`` and
            ``q_log_returns`` have unequal length (mismatched differencing
            grids — plan CORR-E10P-3 / task 3.0); OR the additive identity
            fails to hold within ``_IDENTITY_TOL`` (a genuine numerical
            decomposition error, not a grid mismatch).
    """
    if len(fx_log_returns) != len(q_log_returns):
        raise DecompositionIdentityError(
            f"X has {len(fx_log_returns)} daily log-returns but Q has "
            f"{len(q_log_returns)}; the exact §4.2 identity holds "
            f"cell-by-cell only on a common sub-monthly differencing grid "
            f"(plan task 3.0 / CORR-E10P-3). The decomposition never "
            f"silently computes an inexact identity."
        )
    n = len(fx_log_returns)
    cost_log_returns = tuple(
        fx + q for fx, q in zip(fx_log_returns, q_log_returns, strict=True)
    )

    var_fx = population_variance(fx_log_returns)
    var_q = population_variance(q_log_returns)
    cov_term = 2.0 * _population_covariance(fx_log_returns, q_log_returns)
    var_total = population_variance(cost_log_returns)

    residual = var_total - (var_fx + var_q + cov_term)
    if not math.isfinite(residual) or abs(residual) > _IDENTITY_TOL:
        raise DecompositionIdentityError(
            f"exact §4.2 identity violated: Var(Δlog cost)={var_total!r} "
            f"vs Var(Δlog FX)+Var(Δlog Q)+2·Cov="
            f"{var_fx + var_q + cov_term!r}; residual {residual!r} exceeds "
            f"tolerance {_IDENTITY_TOL}. On a common grid this residual is "
            f"floating-point zero — a larger residual is a real error."
        )

    return ThreeWayDecompositionCell(
        currency="",
        year=0,
        month=0,
        var_total=var_total,
        var_fx=var_fx,
        var_q=var_q,
        cov_term=cov_term,
        grid_index_length=n,
        identity_residual=residual,
    )


def _drop_zero_query_days(
    daily_query_counts: Sequence[int],
    daily_fx_rate: Sequence[float],
) -> tuple[tuple[int, ...], tuple[float, ...]]:
    """Drop the zero-Q days from a (Q, FX) daily pair on the common grid.

    The canonical daily gapped-grid restriction (spec v0.7 §3.2 / §4.2,
    CORRECTIONS-E10-7): a zero-query day has zero cost and an undefined
    ``Δlog cost``; the drop is forced by the log domain. Q and FX are
    filtered on the SAME index so the surviving grid is common to both —
    the exact §4.2 identity is preserved on the gapped grid.

    Args:
        daily_query_counts: The daily simulated query counts.
        daily_fx_rate: The matching daily real FX rates — MUST share the
            ``daily_query_counts`` index.

    Returns:
        The surviving (positive-Q) ``(query_counts, fx_rates)`` pair, in
        original order.
    """
    surviving = [
        (q, fx)
        for q, fx in zip(daily_query_counts, daily_fx_rate, strict=True)
        if q > 0
    ]
    if not surviving:
        return ((), ())
    q_out, fx_out = zip(*surviving, strict=True)
    return (tuple(q_out), tuple(fx_out))


@dataclass(frozen=True, slots=True)
class ThreeWayDecompositionModule:
    """Stateless callable — the exact §4.2 three-way log-variance
    decomposition for one identified (currency, month) panel cell.

    Satisfies the ``types.ThreeWayDecomposition`` Protocol. The module is
    the cell-identified entry point: it derives ``Δlog FX`` and ``Δlog Q``
    from the simulator trajectory's daily Q index and the real daily FX
    path — both on the SAME daily grid (plan task 3.0), restricted to the
    surviving non-zero-Q-day common index (spec v0.7 §3.2 / §4.2,
    CORRECTIONS-E10-7) — and delegates the arithmetic to ``decompose_cell``.
    """

    def __call__(
        self,
        fx_cell: MonthlyRealizedVarianceCell,
        trajectory: CostStreamTrajectory,
    ) -> ThreeWayDecompositionCell:
        """Decompose one identified (currency, month) cell.

        The trajectory's ``daily_query_counts`` is the NHPP simulator's
        intra-day arrivals already aggregated to the daily grid (the
        engine aligns the trajectory to the FX path length). The FX daily
        level series is the trajectory's ``daily_fx_rate`` — the real
        central-bank path — which by construction shares the trajectory's
        daily index. Per spec v0.7 CORRECTIONS-E10-7 the zero-Q days are
        dropped from FX and Q on the SAME surviving index before
        differencing — the canonical daily gapped grid. ``grid_index_length``
        is reported as the surviving non-zero-Q-day count; the differenced
        series carries one fewer observation.

        Args:
            fx_cell: The (currency, month) X-side realized-variance cell —
                supplies the cell identity. (Its ``n_trading_days`` is the
                full-daily-grid count and is NOT the gapped-grid index.)
            trajectory: The matching simulated cost-stream trajectory —
                supplies the daily Q counts and the real daily FX path.

        Returns:
            A ``ThreeWayDecompositionCell`` carrying the cell identity and
            the exact §4.2 split on the surviving non-zero-Q-day common
            grid, with ``grid_index_length`` set to that surviving count.

        Raises:
            DecompositionIdentityError: the FX and Q daily indices do not
                share a common grid; OR the additive identity fails.
            ValueError: a surviving daily FX rate yields a non-positive
                level (``Δlog`` undefined — signals upstream FX data
                corruption).
        """
        if len(trajectory.daily_fx_rate) != len(
            trajectory.daily_query_counts
        ):
            raise DecompositionIdentityError(
                f"{fx_cell.currency} {fx_cell.year}-{fx_cell.month:02d}: "
                f"trajectory FX daily index has "
                f"{len(trajectory.daily_fx_rate)} observations but the Q "
                f"daily index has {len(trajectory.daily_query_counts)}; "
                f"X and Q must share a common daily grid (plan task 3.0)."
            )
        q_surv, fx_surv = _drop_zero_query_days(
            trajectory.daily_query_counts, trajectory.daily_fx_rate
        )
        fx_returns = daily_log_returns(fx_surv)
        q_returns = daily_log_returns(
            tuple(float(q) for q in q_surv)
        )
        cell = decompose_cell(
            fx_log_returns=fx_returns, q_log_returns=q_returns
        )
        # Re-stamp with the cell identity and the surviving gapped-grid
        # index length (the canonical non-zero-Q-day count).
        return ThreeWayDecompositionCell(
            currency=fx_cell.currency,
            year=fx_cell.year,
            month=fx_cell.month,
            var_total=cell.var_total,
            var_fx=cell.var_fx,
            var_q=cell.var_q,
            cov_term=cell.cov_term,
            grid_index_length=cell.grid_index_length,
            identity_residual=cell.identity_residual,
        )


__all__ = [
    "ThreeWayDecompositionModule",
    "decompose_cell",
]
