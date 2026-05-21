"""Assembled E10 panel-cell Value-tier container (plan task 3.x).

The per-(currency, month) panel cell — the X-side FX realized variance
(spec v0.6 §3.2), the Y-side cost-stream realized variance (§5.2), and
the exact §4.2 three-way log-variance decomposition. A pure frozen
dataclass: no logic, tier-import-discipline-clean (the types tier never
imports ``..modules`` / ``..utils``), so the IO-boundary ``panel_io``
unit can construct it without crossing a tier boundary.
"""

from __future__ import annotations

from dataclasses import dataclass

from .decomposition import ThreeWayDecompositionCell


@dataclass(frozen=True, slots=True)
class PanelCell:
    """One assembled (currency, month) E10 panel cell.

    ``x_realized_variance`` is the canonical X-side FX realized variance
    (spec v0.7 §3.2, CORRECTIONS-E10-7 — sum-of-squares of Δlog FX on the
    surviving non-zero-Q-day common index, NOT the full daily grid). It is
    the SAME gapped-grid FX object as ``decomposition.var_fx`` — both are
    computed from the identical surviving Δlog FX series (up to the
    sum-vs-population convention). The v0.6 two-divergent-FX-objects
    condition (a full-daily-grid X alongside a gapped-grid ``var_fx``) is
    CLOSED — there is exactly one canonical X per cell.
    ``y_realized_variance`` is the Y-side cost-stream realized variance
    (§5.2 sum-of-squares of Δlog cost on the same surviving index).
    ``decomposition`` is the exact §4.2 three-way split (population-
    variance operator). ``n_fx_trading_days`` is the daily FX level count;
    ``n_surviving_days`` is the count of positive-Q days the decomposition
    was differenced on after the zero-Q-day drop. ``material_gap`` is True
    iff the cell has fewer than two surviving days — the decomposition
    cannot be computed and the cell routes to the §9 ladder.
    ``fx_variance_share`` is ``var_fx / var_total`` (NaN when var_total is
    zero or the cell is a material gap). ``qualifying`` carries the
    regime-break qualifying status (spec §3.3). ``seed`` records the
    simulator seed of the underlying trajectory for Tier-3 reproducibility.
    """

    currency: str
    year: int
    month: int
    x_realized_variance: float
    y_realized_variance: float
    decomposition: ThreeWayDecompositionCell
    n_fx_trading_days: int
    n_surviving_days: int
    material_gap: bool
    fx_variance_share: float
    qualifying: bool
    seed: int
