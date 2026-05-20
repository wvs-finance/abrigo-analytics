"""Three-way log-variance decomposition Value-tier container (spec v0.4 §4.2).

The exact additive identity, in log-return space:

    Var(d log cost) = Var(d log FX) + Var(d log Q) + 2 * Cov(d log FX, d log Q)

This is EXACT (no higher-order term) because ``cost = Q * c * FX`` with
``c`` constant makes ``d log cost = d log Q + d log FX`` an exact
identity (spec v0.4 §4.2). The identity holds cell-by-cell only on a
common X/Q differencing grid (plan CORR-E10P-3 / task 3.0).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThreeWayDecompositionCell:
    """One (currency, month) cell of the exact three-way log-variance
    decomposition.

    ``var_total`` is ``Var(d log cost)``; ``var_fx`` is ``Var(d log
    FX)`` (REAL); ``var_q`` is ``Var(d log Q)`` (simulator output);
    ``cov_term`` is ``2 * Cov(d log FX, d log Q)`` (simulator output,
    ~= 0 in the primary spec per §6.4). ``grid_index_length`` records the
    shared sub-monthly observation-index length on which X and Q were
    differenced — the additive identity holds exactly only when X and Q
    share this index (plan task 3.0). ``identity_residual`` is
    ``var_total - (var_fx + var_q + cov_term)`` and MUST be exactly zero
    (to floating-point tolerance) on the common grid.
    """

    currency: str
    year: int
    month: int
    var_total: float
    var_fx: float
    var_q: float
    cov_term: float
    grid_index_length: int
    identity_residual: float
