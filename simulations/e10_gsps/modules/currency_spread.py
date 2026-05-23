"""Non-statistical 5-currency min-max / IQR spread display (spec v0.7
§4.3; plan task 4.3 / CORR-E10P-11 / spec v0.6 W-2).

What this unit does
-------------------
Computes the **raw 5-currency min-max / IQR spread display** of the
FX-variance-share surface — the replacement for the v0.5 wild-cluster
bootstrap + permutation arms, which were DROPPED at G~=5 (size-broken;
2^5=32-point permutation support; EM/DM exchangeability violated).

Per-currency surface curves
---------------------------
For each panel currency, evaluate the §4.3 surface on the same anchored
log-spaced Q-grid (the user-locked 50-point grid with adaptive doubling
to 100) — filtered to that currency's panel cells. Five surfaces total
at the G=5 panel.

Envelope across the 5 currencies
--------------------------------
At each grid point, the min, max, Q1, Q3, and median across the 5 per-
currency shares define the **non-statistical envelope**. NOT a
confidence interval. NOT an inferential band. NOT a hypothesis test.
A descriptive spread of 5 observed currency values, FULL STOP.

EM / DM tagging
---------------
Per pre-Phase-4 Model QA review item 4, each panel currency carries an
EM-or-DM tag for cosmetic colour-coding in the notebook overplot:
- EM: COP, BRL, NGN.
- DM: EUR, GBP.

The tag is descriptive metadata only; the spread display itself does
not condition on the EM/DM split.

In-figure firewall label
------------------------
The result object carries a literal ``non_statistical_label`` the
consuming notebook MUST render in the figure (subtitle / caption) so a
figure escaping its surrounding prose still self-firewalls
(per Model QA review item 4 enforcement note).

Discipline
----------
``modules``-tier: frozen-dataclass stateless container + free pure
functions; no mutable state, no imports from ``..utils``.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Literal

import numpy as np

from simulations.e10_gsps._errors import SurfaceGridError
from simulations.e10_gsps.modules.surface_grid import (
    DEFAULT_BASE_N,
    DEFAULT_REFINED_N,
    DEFAULT_S_BE,
    _log_spaced,
    _panel_mean_q_share,
    _panel_mean_share,
    scan_interior_crossing,
)
from simulations.e10_gsps.types import (
    CurrencySpreadResult,
    PanelCell,
    SurfaceGridPoint,
    SurfaceGridResult,
)


#: EM/DM tags per panel currency (per pre-Phase-4 Model QA review item 4).
#: Tags are cosmetic colour-coding metadata for the notebook overplot; the
#: spread display itself does not condition on this split.
DEFAULT_EM_OR_DM: dict[str, Literal["EM", "DM"]] = {
    "COP": "EM",
    "BRL": "EM",
    "NGN": "EM",
    "EUR": "DM",
    "GBP": "DM",
}


#: The literal in-figure firewall label the consuming notebook MUST
#: render alongside the envelope display (per Model QA review item 4).
NON_STATISTICAL_LABEL: str = (
    "5-currency min-max / IQR -- NOT a confidence interval; "
    "NOT an inferential band; NOT a hypothesis test."
)


def _per_currency_surface(
    panel_currency_cells: Sequence[PanelCell],
    q_grid: Sequence[float],
    *,
    s_be: float,
    refined: bool,
    anchored_range_low: float,
    anchored_range_high: float,
) -> SurfaceGridResult:
    """Evaluate the share surface for a single currency on the shared
    Q-grid.

    Args:
        panel_currency_cells: Panel cells filtered to one currency.
        q_grid: The shared log-spaced Q-grid across the anchored range.
        s_be: Ex-ante-pinned break-even share.
        refined: Whether the shared grid was refined to the doubled
            resolution.

    Returns:
        A ``SurfaceGridResult`` with one grid point per Q-grid entry
        for this currency.

    Raises:
        SurfaceGridError: This currency has no finite-share cells.
    """
    mean_share = _panel_mean_share(panel_currency_cells)
    mean_q_share = _panel_mean_q_share(panel_currency_cells)
    n_grid = len(q_grid)
    shares = [mean_share] * n_grid

    crossing = scan_interior_crossing(
        shares=shares,
        q_volumes=q_grid,
        break_even_share=s_be,
        min_run_length=3,
    )
    q_dom_flag = all(
        (math.isfinite(s) and s < s_be) for s in shares
    )
    # Spec-form flag — Phase-6 Delphi auditor-1 MID-1. Broadcast a single
    # mean_q_share scalar; check var_q / var_total > 1 - s_be.
    q_dom_flag_spec = (
        math.isfinite(mean_q_share) and mean_q_share > (1.0 - s_be)
    )

    points = tuple(
        SurfaceGridPoint(
            q_volume=q_grid[i],
            fx_variance_share=shares[i],
            band_low=float("nan"),
            band_high=float("nan"),
            below_break_even=shares[i] < s_be
            if math.isfinite(shares[i])
            else False,
        )
        for i in range(n_grid)
    )

    log_step_dex = (
        (math.log10(q_grid[-1]) - math.log10(q_grid[0])) / (n_grid - 1)
        if n_grid > 1
        else 0.0
    )

    return SurfaceGridResult(
        points=points,
        break_even_share=s_be,
        grid_resolution=log_step_dex,
        interior_crossing=crossing.interior_crossing,
        crossing_q_volumes=crossing.crossing_q_volumes,
        anchored_range_low=anchored_range_low,
        anchored_range_high=anchored_range_high,
        q_variance_dominance_flag=q_dom_flag,
        refined=refined,
        effective_n_grid=n_grid,
        grid_resolution_decision_citation=(
            "Per-currency curve on the shared anchored-range Q-grid "
            "(inherits the user-locked log-spaced 50-point + adaptive-"
            "doubling rule from evaluate_surface_grid)."
        ),
        is_panel_mean_broadcast=True,
        q_variance_dominance_flag_spec_form=q_dom_flag_spec,
    )


def compute_currency_spread(
    panel: Sequence[PanelCell],
    q_range: tuple[float, float],
    *,
    s_be: float = DEFAULT_S_BE,
    base_n: int = DEFAULT_BASE_N,
    refined_n: int = DEFAULT_REFINED_N,
    em_or_dm: dict[str, Literal["EM", "DM"]] | None = None,
) -> CurrencySpreadResult:
    """Compute the non-statistical 5-currency min-max / IQR spread
    display.

    For each panel currency, evaluate the §4.3 surface on the shared
    anchored-range log-spaced Q-grid (user-locked 50 points with
    adaptive doubling to 100), then take the pointwise min / max / Q1 /
    Q3 / median across the 5 per-currency curves.

    Adaptive doubling here is driven by ANY currency's mean share
    falling within +/-0.5 dex of ``s_be``.

    Args:
        panel: The Phase-3 panel cells (5 currencies x ~30 months ~=
            150 cells).
        q_range: Anchored ``(Q_low, Q_high)`` Q-volume bounds.
        s_be: Ex-ante-pinned break-even share.
        base_n: User-locked base grid size (default 50).
        refined_n: Refined grid size under adaptive doubling
            (default 100).
        em_or_dm: Optional override for the EM/DM tag map; defaults to
            ``DEFAULT_EM_OR_DM`` (COP/BRL/NGN=EM, EUR/GBP=DM).

    Returns:
        A ``CurrencySpreadResult`` with the per-currency surfaces, the
        shared Q-grid, the pointwise envelope (min / max / Q1 / Q3 /
        median), the EM/DM tag map, and the literal in-figure
        firewall label.

    Raises:
        SurfaceGridError: Q-range invalid, panel empty, or any
            currency has no finite-share cells.
    """
    if len(panel) == 0:
        raise SurfaceGridError(
            "currency-spread evaluator requires a non-empty panel."
        )
    q_low, q_high = q_range

    # Group cells per currency.
    by_currency: dict[str, list[PanelCell]] = {}
    for cell in panel:
        by_currency.setdefault(cell.currency, []).append(cell)

    # Pre-compute each currency's mean share to decide on adaptive
    # doubling at the panel-aggregate level: if any currency sits
    # within +/-0.5 dex of s_be on the base grid, refine to refined_n.
    currency_mean_shares = {
        cur: _panel_mean_share(cells) for cur, cells in by_currency.items()
    }
    refinement_factor = math.pow(10.0, 0.5)
    any_near_threshold = any(
        (
            ms > 0.0
            and (s_be / refinement_factor) <= ms <= (s_be * refinement_factor)
        )
        for ms in currency_mean_shares.values()
    )

    if any_near_threshold:
        q_grid = _log_spaced(q_low, q_high, refined_n)
        refined = True
    else:
        q_grid = _log_spaced(q_low, q_high, base_n)
        refined = False

    # Per-currency surfaces on the shared grid.
    per_currency_grids: dict[str, SurfaceGridResult] = {
        cur: _per_currency_surface(
            cells,
            q_grid,
            s_be=s_be,
            refined=refined,
            anchored_range_low=q_low,
            anchored_range_high=q_high,
        )
        for cur, cells in by_currency.items()
    }

    # Pointwise envelope across the per-currency curves.
    # Stack: rows = currencies, cols = grid points.
    stacked = np.array(
        [
            [pt.fx_variance_share for pt in per_currency_grids[cur].points]
            for cur in per_currency_grids
        ],
        dtype=float,
    )

    envelope_min = tuple(np.nanmin(stacked, axis=0).tolist())
    envelope_max = tuple(np.nanmax(stacked, axis=0).tolist())
    envelope_q1 = tuple(np.nanquantile(stacked, 0.25, axis=0).tolist())
    envelope_q3 = tuple(np.nanquantile(stacked, 0.75, axis=0).tolist())
    envelope_median = tuple(np.nanmedian(stacked, axis=0).tolist())

    is_em_or_dm = dict(em_or_dm) if em_or_dm is not None else dict(
        DEFAULT_EM_OR_DM
    )

    return CurrencySpreadResult(
        per_currency_grids=per_currency_grids,
        envelope_q_grid=tuple(q_grid),
        envelope_min=envelope_min,
        envelope_max=envelope_max,
        envelope_q1=envelope_q1,
        envelope_q3=envelope_q3,
        envelope_median=envelope_median,
        is_em_or_dm=is_em_or_dm,
        non_statistical_label=NON_STATISTICAL_LABEL,
    )
