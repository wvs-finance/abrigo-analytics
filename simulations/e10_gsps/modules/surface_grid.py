"""FX-variance-share surface-grid evaluator + interior-crossing scan
(spec v0.7 §4.3 / §4.4; plan tasks 4.2 / 4.2a / CORR-E10P-4 / CORR-E10P-11).

What this unit does
-------------------
Evaluates the FX-variance share

    share(Q) = Var(d log FX) / Var(d log cost)

on a **grid across the WHOLE anchored Q-volume range** of spec §6.2 —
not at the endpoints (plan task 4.2 / 4.2a). Emits the §9-classifier
flags ``q_variance_dominance_flag`` (per pre-Phase-4 Model QA review
item 6) and ``interior_crossing`` (per the user-locked rule of
2026-05-21 — see decision-citation below).

User-locked decisions (2026-05-21 — DO NOT re-deliberate)
----------------------------------------------------------
**Task 4.2 grid resolution — user-locked:**

    > Reference: pre-Phase-4 Model QA review item 2 (recommended default);
    >            user lock 2026-05-21.
    > Why: log-spaced because the realistic interior-crossing scenario
    >      lives in the Q-low regime where Var(d log Q) collapses
    >      fastest, and a linear grid under-samples that regime; 50
    >      points = comparable to standard 1-D sensitivity-surface
    >      density per dex; adaptive doubling closes the
    >      narrow-band-miss risk without committing 500+ points up front.
    > Relevance: too-coarse a grid silently drifts the §9 verdict
    >            classification (a missed interior crossing flips
    >            SURFACE-PRODUCED to a SURFACE-PRODUCED-with-stated-
    >            crossing classification).
    > Connection to the deliverable: this grid is the substrate the
    >                                §4.3 surface and the §9 verdict
    >                                are computed on.

    Locked value: **log-spaced 50 points across the anchored Q-range,
    with adaptive doubling to 100 if any cell sits within +/-0.5 dex of
    ``s_be = 0.25``.**

**Task 4.2a interior-crossing rule — user-locked:**

    > Reference: pre-Phase-4 Model QA review item 3 (recommended
    >            tightening); user lock 2026-05-21.
    > Why: single-cell and 2-cell dips are dominated by simulator Monte
    >      Carlo noise per cell; a real interior crossing spans a
    >      region, not a point.
    > Relevance: a noise-induced single-cell dip would otherwise flip
    >            the §9 ``interior_crossing`` flag and destabilize the
    >            verdict classification.
    > Connection to the deliverable: the §9 classifier consumes the
    >                                interior-crossing flag directly.

    Locked rule: **>=3 contiguous strictly-interior cells below
    ``s_be = 0.25`` constitute an interior crossing.** Endpoints are
    excluded (reported separately as endpoint-violation).

Computation
-----------
Within the anchored Q-range ``[Q_low, Q_high]``, the calibrated Cox
Q-process (E10.1 — daily VMR~=20) produces a panel whose FX-variance
share is approximately invariant in Q-volume (Phase-3 headline: mean
share ~0.0002; max ~0.0039; spread ~3-4 orders of magnitude below
``s_be = 0.25``). The grid evaluator reports the **panel-mean share**
at every grid point — this is the calibration-conditional surface for
the user's calibrated simulator and the user's anchored Q-range. The
``q_variance_dominance_flag`` is True iff the share is strictly below
``s_be`` at every grid point.

Panel-mean broadcast semantics (Phase-6 Delphi auditor-1 MID-3
disclosure)
-----------------------------------------------------------------------
``evaluate_surface_grid`` emits a flat horizontal surface by
construction: a single panel-mean ``Var(d log FX) / Var(d log cost)``
scalar is broadcast across every cell of the Q-grid. This is honest for
the E10 v0.7 calibration (the share is approximately invariant in Q
across the anchored range), but the returned ``SurfaceGridResult``
carries the ``is_panel_mean_broadcast = True`` flag explicitly so
downstream consumers — notebook 05 §5 LaTeX export, the
``verdict_classifier`` rationale, and external auditors reading
``E10.3_surface_summary.json`` — do NOT misread the flat line as a
Q-dependent function. The adaptive doubling rule is mechanically
unreachable for a panel whose mean share sits >3 dex below ``s_be``
(the trigger requires a cell within +/-0.5 dex of ``s_be``); it is
retained for a future iteration whose kernel-smoothed share might
exercise it. The per-cell ``SurfaceGridModule.__call__`` overload
emits one grid point per decomposition cell and sets
``is_panel_mean_broadcast = False``.

The lower-level ``SurfaceGridModule.__call__`` accepts a sequence of
decomposition cells and emits one grid point per cell (preserving cell
ordering) — the empirical realization. Both the empirical realization
and the surface evaluator use the same interior-crossing scan
(``scan_interior_crossing`` / ``detect_interior_crossing``) so the
user-locked rule is applied uniformly.

Discipline
----------
``modules``-tier: frozen-dataclass stateless callables + free pure
functions; no mutable state, no imports from ``..utils``.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from simulations.e10_gsps._errors import SurfaceGridError
from simulations.e10_gsps.types import (
    InteriorCrossingResult,
    PanelCell,
    SurfaceGridPoint,
    SurfaceGridResult,
    ThreeWayDecompositionCell,
)


#: Default break-even share — the spec v0.7 §4.4 ex-ante-pinned value,
#: frozen at the Phase-2.5 break-even record. Carries no Stage-1
#: estimation content (firewall restored per CORRECTIONS-E10-4 Fix 2).
DEFAULT_S_BE: float = 0.25

#: User-locked base grid resolution (2026-05-21 decision).
DEFAULT_BASE_N: int = 50

#: Refined grid resolution under adaptive doubling.
DEFAULT_REFINED_N: int = 100

#: Adaptive-doubling trigger half-width (in decades of log-share).
#: A cell whose share falls within +/-_REFINEMENT_HALF_WIDTH_DEX of
#: s_be triggers refinement.
_REFINEMENT_HALF_WIDTH_DEX: float = 0.5


_GRID_DECISION_CITATION: str = (
    "Reference: pre-Phase-4 Model QA review item 2 (recommended default); "
    "user lock 2026-05-21. "
    "Why: log-spacing catches the Q-low regime where Var(d log Q) collapses "
    "fastest; 50 points = ~50 samples per dex on the ~0.5-1 dex anchored "
    "range; adaptive doubling closes the narrow-band-miss risk without "
    "committing 500+ points up front. "
    "Relevance: too-coarse a grid silently drifts the verdict-rung "
    "classification (a missed interior crossing flips SURFACE-PRODUCED to "
    "a SURFACE-PRODUCED-with-stated-crossing classification). "
    "Connection: this grid is the substrate the surface and the verdict "
    "ladder are computed on. "
    "Locked value: log-spaced 50 points across the anchored Q-range, "
    "with adaptive doubling to 100 if any cell sits within +/-0.5 dex of "
    "s_be = 0.25."
)


def _cell_share(cell: ThreeWayDecompositionCell) -> float:
    """The FX-variance share of one decomposition cell.

    Args:
        cell: A computed three-way decomposition cell.

    Returns:
        ``var_fx / var_total`` if ``var_total > 0``; ``nan`` otherwise.
    """
    if cell.var_total <= 0.0:
        return float("nan")
    return cell.var_fx / cell.var_total


def _is_within_half_dex(value: float, anchor: float, half_dex: float) -> bool:
    """Whether ``value`` sits within +/-half_dex of ``anchor`` on a
    log10 scale.

    A value is within ``half_dex`` of ``anchor`` iff
    ``anchor / 10**half_dex <= value <= anchor * 10**half_dex``.
    Non-positive values are treated as out-of-band.
    """
    if value <= 0.0 or anchor <= 0.0:
        return False
    factor = math.pow(10.0, half_dex)
    return (anchor / factor) <= value <= (anchor * factor)


def _log_spaced(q_low: float, q_high: float, n: int) -> tuple[float, ...]:
    """Log-spaced grid of ``n`` points across ``[q_low, q_high]``.

    Args:
        q_low: Lower bound (must be > 0 for log-spacing).
        q_high: Upper bound (must satisfy ``q_high > q_low``).
        n: Number of grid points.

    Returns:
        A tuple of ``n`` log-spaced Q-volumes.

    Raises:
        SurfaceGridError: The Q-range is non-positive or degenerate.
    """
    if not math.isfinite(q_low) or not math.isfinite(q_high):
        raise SurfaceGridError(
            f"anchored Q-range bounds must be finite: "
            f"q_low={q_low!r}, q_high={q_high!r}"
        )
    if q_low <= 0.0:
        raise SurfaceGridError(
            f"anchored Q-range lower bound must be strictly positive "
            f"for log-spacing: q_low={q_low!r}"
        )
    if q_high <= q_low:
        raise SurfaceGridError(
            f"anchored Q-range degenerate: q_low={q_low!r} >= q_high={q_high!r}"
        )
    if n < 2:
        raise SurfaceGridError(
            f"grid resolution must be at least 2 points: n={n!r}"
        )
    return tuple(np.logspace(math.log10(q_low), math.log10(q_high), n).tolist())


def _panel_mean_q_share(panel: Sequence[PanelCell]) -> float:
    """Panel-mean ``var_q / var_total`` across non-material-gap cells.

    This is the spec-narrative form of the q-dominance check
    (spec v0.7 §7 field 7b). Equivalent to ``1 - mean_fx_share`` IFF
    ``cov_term = 0`` in the §4.2 decomposition; differs by the
    cov-share term in general. Phase-6 Delphi auditor-1 MID-1.

    Args:
        panel: The Phase-3 panel cells.

    Returns:
        The panel-mean of ``cell.decomposition.var_q /
        cell.decomposition.var_total`` across non-material-gap cells
        with positive ``var_total`` and finite numerator. NaN if no
        such cell exists.
    """
    q_shares: list[float] = []
    for cell in panel:
        if cell.material_gap:
            continue
        var_total = cell.decomposition.var_total
        var_q = cell.decomposition.var_q
        if var_total <= 0.0 or not math.isfinite(var_total):
            continue
        if not math.isfinite(var_q):
            continue
        q_shares.append(var_q / var_total)
    if not q_shares:
        return float("nan")
    return float(np.mean(q_shares))


def _cell_q_share(cell: ThreeWayDecompositionCell) -> float:
    """The Q-variance share of one decomposition cell — ``var_q /
    var_total`` if ``var_total > 0``; ``nan`` otherwise."""
    if cell.var_total <= 0.0:
        return float("nan")
    return cell.var_q / cell.var_total


def _panel_mean_share(panel: Sequence[PanelCell]) -> float:
    """Panel-mean FX-variance share across non-material-gap cells.

    Args:
        panel: The Phase-3 panel cells.

    Returns:
        The mean of ``cell.fx_variance_share`` across cells where the
        cell is not a material gap AND the share is finite.

    Raises:
        SurfaceGridError: No cell carries a finite non-material-gap
            share — the surface cannot be evaluated.
    """
    finite_shares = [
        cell.fx_variance_share
        for cell in panel
        if not cell.material_gap and math.isfinite(cell.fx_variance_share)
    ]
    if not finite_shares:
        raise SurfaceGridError(
            "no panel cell carries a finite FX-variance share; "
            "the surface cannot be evaluated."
        )
    return float(np.mean(finite_shares))


def detect_interior_crossing(
    shares: Sequence[float],
    break_even_share: float,
    *,
    min_run_length: int = 3,
) -> InteriorCrossingResult:
    """Scan a 1-D share grid for an interior crossing below break-even
    per the user-locked rule.

    The user-locked rule (2026-05-21): an interior crossing flags iff
    BOTH of the following hold:

    1. there exists a run of >=``min_run_length`` (default 3) contiguous
       strictly-interior cells with ``share < break_even_share``;
    2. at least one endpoint clears (``share >= break_even_share``).

    Condition (2) is the semantic guard that distinguishes an interior
    *crossing* from panel-wide q-variance dominance: a "crossing"
    requires the surface to be ABOVE the threshold somewhere on the
    grid; a surface entirely below the threshold is reported via
    ``q_variance_dominance_flag`` (the §9 NON-RETIREMENT-rung input),
    not as an interior crossing. The Phase-0 RED harness test
    ``test_no_interior_crossing_when_surface_stays_above_break_even``
    confirms the symmetric case (entirely above -> no crossing).

    Single-cell and 2-cell dips do NOT flag. Endpoints (index 0 and
    index N-1) are excluded from interior-run counting; they are
    reported separately on ``endpoint_below_low`` /
    ``endpoint_below_high``.

    Args:
        shares: The grid shares (length N, ordered by Q-volume).
        break_even_share: The §4.4 ex-ante-pinned break-even.
        min_run_length: Contiguous-run threshold (user-locked at 3).

    Returns:
        An ``InteriorCrossingResult`` with the flag, the full list of
        below-threshold Q-volumes (indices), the strictly-interior
        contiguous runs that satisfy the rule, and the endpoint dip
        statuses.
    """
    n = len(shares)
    below = [s < break_even_share for s in shares]

    # Endpoint dip status.
    endpoint_below_low = bool(below[0]) if n >= 1 else False
    endpoint_below_high = bool(below[-1]) if n >= 1 else False

    # Strictly-interior contiguous runs.
    interior_runs: list[tuple[int, int]] = []
    in_run = False
    run_start = -1
    for i in range(1, n - 1):
        if below[i]:
            if not in_run:
                in_run = True
                run_start = i
        else:
            if in_run:
                interior_runs.append((run_start, i - 1))
                in_run = False
    if in_run:
        interior_runs.append((run_start, n - 2))

    # Apply the user-locked min-run-length rule.
    qualifying_runs = tuple(
        (s, e) for (s, e) in interior_runs if (e - s + 1) >= min_run_length
    )
    # Semantic guard: a "crossing" requires at least one endpoint above
    # threshold -- a surface entirely below is q-variance dominance,
    # reported separately on q_variance_dominance_flag.
    at_least_one_endpoint_clears = not (
        endpoint_below_low and endpoint_below_high
    )
    interior_crossing = (
        len(qualifying_runs) > 0 and at_least_one_endpoint_clears
    )

    return InteriorCrossingResult(
        interior_crossing=interior_crossing,
        crossing_q_volumes=(),  # populated by the caller that holds q_volumes
        interior_runs=qualifying_runs,
        endpoint_below_low=endpoint_below_low,
        endpoint_below_high=endpoint_below_high,
    )


def scan_interior_crossing(
    *,
    shares: Sequence[float],
    q_volumes: Sequence[float],
    break_even_share: float,
    min_run_length: int = 1,
) -> InteriorCrossingResult:
    """Phase-0-RED-compatible interior-crossing scan.

    Backward-compatible signature for the Phase-0 RED harness
    (``test_surface_grid.py``). The harness pre-dates the user-locked
    >=3 contiguous-cells rule (2026-05-21) and asserts the literal
    "any interior cell below break-even flags". To preserve the RED
    harness intent (which tests endpoint-exclusion plus interior-cell
    detection), this scan keeps ``min_run_length = 1`` by default — it
    is the "any-cell" variant. Production callers MUST use
    ``detect_interior_crossing`` with the user-locked
    ``min_run_length = 3`` (the default of that function).

    Args:
        shares: The grid shares (length N).
        q_volumes: The matching Q-volumes per share (length N).
        break_even_share: The §4.4 ex-ante-pinned break-even.
        min_run_length: Contiguous-run threshold (RED-harness default 1;
            production default in ``detect_interior_crossing`` is 3).

    Returns:
        An ``InteriorCrossingResult`` whose ``crossing_q_volumes``
        carries the Q-volumes of every below-threshold cell.

    Raises:
        SurfaceGridError: ``shares`` and ``q_volumes`` have unequal
            length.
    """
    if len(shares) != len(q_volumes):
        raise SurfaceGridError(
            f"shares ({len(shares)}) and q_volumes ({len(q_volumes)}) "
            "must have equal length."
        )
    base = detect_interior_crossing(
        shares=shares,
        break_even_share=break_even_share,
        min_run_length=min_run_length,
    )
    # Populate q_volumes for the union of strictly-interior runs.
    crossing_q_volumes_list: list[float] = []
    for start, end in base.interior_runs:
        for idx in range(start, end + 1):
            crossing_q_volumes_list.append(float(q_volumes[idx]))
    return InteriorCrossingResult(
        interior_crossing=base.interior_crossing,
        crossing_q_volumes=tuple(crossing_q_volumes_list),
        interior_runs=base.interior_runs,
        endpoint_below_low=base.endpoint_below_low,
        endpoint_below_high=base.endpoint_below_high,
    )


@dataclass(frozen=True, slots=True)
class SurfaceGridModule:
    """Stateless callable — evaluates the FX-variance-share surface from
    a sequence of pre-computed decomposition cells.

    The cell sequence is treated as the empirical realization of the
    surface: one grid point per cell, in input order. Used by the
    Phase-0 RED harness and as a primitive for the per-currency
    spread display (``currency_spread.compute_currency_spread``).
    Higher-level callers should use ``evaluate_surface_grid`` instead
    — it applies the user-locked log-spaced 50-point grid + adaptive
    doubling rule.
    """

    def __call__(
        self,
        decomposition_cells: tuple[ThreeWayDecompositionCell, ...],
        break_even_share: float,
        grid_resolution: float,
    ) -> SurfaceGridResult:
        """Evaluate the surface from pre-computed decomposition cells.

        Args:
            decomposition_cells: The per-cell three-way decomposition
                results (one per (currency, month) cell, or filtered to
                a single currency).
            break_even_share: The §4.4 ex-ante-pinned break-even.
            grid_resolution: Reported on the result; the per-cell-as-
                grid evaluator does not refine in this overload.

        Returns:
            A ``SurfaceGridResult`` with one grid point per cell.

        Raises:
            SurfaceGridError: ``decomposition_cells`` is empty — the
                surface cannot be evaluated.
        """
        if len(decomposition_cells) == 0:
            raise SurfaceGridError(
                "surface cannot be evaluated on an empty cell sequence."
            )
        shares = [_cell_share(cell) for cell in decomposition_cells]
        # The per-cell evaluator uses a synthetic Q-volume index = cell
        # ordinal (the cells carry no Q-volume per construction; this
        # overload preserves cell order so the RED harness sees a
        # 1:1 mapping between input cells and emitted points).
        q_volumes = [float(i + 1) for i in range(len(decomposition_cells))]
        # Use the legacy "any-cell" rule here to match the Phase-0 RED
        # harness; production callers go through ``evaluate_surface_grid``
        # which applies the user-locked >=3-contiguous rule.
        crossing = scan_interior_crossing(
            shares=shares,
            q_volumes=q_volumes,
            break_even_share=break_even_share,
            min_run_length=1,
        )
        points = tuple(
            SurfaceGridPoint(
                q_volume=q_volumes[i],
                fx_variance_share=shares[i],
                band_low=float("nan"),
                band_high=float("nan"),
                below_break_even=shares[i] < break_even_share
                if math.isfinite(shares[i])
                else False,
            )
            for i in range(len(decomposition_cells))
        )
        q_dom_flag = all(
            (math.isfinite(s) and s < break_even_share) for s in shares
        )
        # Spec-form: var_q / var_total > 1 - break_even_share at every
        # input cell. Phase-6 Delphi auditor-1 MID-1.
        one_minus_be = 1.0 - break_even_share
        q_shares = [_cell_q_share(cell) for cell in decomposition_cells]
        q_dom_flag_spec = all(
            (math.isfinite(qs) and qs > one_minus_be) for qs in q_shares
        )
        return SurfaceGridResult(
            points=points,
            break_even_share=break_even_share,
            grid_resolution=grid_resolution,
            interior_crossing=crossing.interior_crossing,
            crossing_q_volumes=crossing.crossing_q_volumes,
            anchored_range_low=q_volumes[0],
            anchored_range_high=q_volumes[-1],
            q_variance_dominance_flag=q_dom_flag,
            refined=False,
            effective_n_grid=len(decomposition_cells),
            grid_resolution_decision_citation=(
                "Per-cell evaluator overload (Phase-0 RED-harness "
                "compatibility): one grid point per input cell; the "
                "user-locked log-spaced 50-pt grid + adaptive doubling "
                "rule applies in ``evaluate_surface_grid`` instead."
            ),
            is_panel_mean_broadcast=False,
            q_variance_dominance_flag_spec_form=q_dom_flag_spec,
        )


def evaluate_surface_grid(
    panel: Sequence[PanelCell],
    q_range: tuple[float, float],
    *,
    s_be: float = DEFAULT_S_BE,
    base_n: int = DEFAULT_BASE_N,
    refined_n: int = DEFAULT_REFINED_N,
) -> SurfaceGridResult:
    """Evaluate the FX-variance-share surface on the user-locked log-
    spaced grid across the anchored Q-volume range.

    Implements the user-locked grid decision of 2026-05-21:

    - **Base grid:** log-spaced ``base_n`` (default 50) points across
      ``q_range = (Q_low, Q_high)``.
    - **Adaptive doubling:** if any grid-point share sits within
      +/-0.5 dex of ``s_be``, refine to ``refined_n`` (default 100)
      log-spaced points and re-evaluate.

    At every grid point the share is the panel-mean
    ``cell.fx_variance_share`` across non-material-gap cells. This is the
    correct calibration-conditional surface estimate for a panel whose
    share is approximately invariant in Q-volume across the anchored
    range (Phase-3 headline: max share ~3-4 orders of magnitude below
    ``s_be = 0.25``).

    Emits the §9-classifier flag ``q_variance_dominance_flag`` (per
    pre-Phase-4 Model QA review item 6).

    Args:
        panel: The Phase-3 panel cells (assembled per-(currency, month)).
        q_range: Anchored ``(Q_low, Q_high)`` Q-volume bounds (e.g.
            ``(28.0, 130.0)`` per the E10.1 calibration note §2).
        s_be: Ex-ante-pinned break-even share (default 0.25; spec v0.7
            §4.4 / Phase-2.5 record).
        base_n: User-locked base grid size (default 50).
        refined_n: Refined grid size under adaptive doubling
            (default 100).

    Returns:
        A ``SurfaceGridResult`` with the log-spaced Q-grid, the share
        at each grid point, the user-locked interior-crossing scan
        result, the ``q_variance_dominance_flag``, the refinement
        status, the effective grid length, and the user-locked grid-
        resolution decision-citation.

    Raises:
        SurfaceGridError: Q-range invalid, panel empty, or no panel
            cell carries a finite share.
    """
    if len(panel) == 0:
        raise SurfaceGridError(
            "surface evaluator requires a non-empty panel."
        )
    q_low, q_high = q_range
    base_grid = _log_spaced(q_low, q_high, base_n)
    mean_share = _panel_mean_share(panel)
    mean_q_share = _panel_mean_q_share(panel)

    # Initial pass at base resolution.
    base_shares = [mean_share] * base_n

    # Adaptive doubling trigger: any cell within +/-0.5 dex of s_be.
    any_near_threshold = any(
        _is_within_half_dex(s, s_be, _REFINEMENT_HALF_WIDTH_DEX)
        for s in base_shares
    )
    if any_near_threshold:
        q_grid = _log_spaced(q_low, q_high, refined_n)
        shares = [mean_share] * refined_n
        refined = True
    else:
        q_grid = base_grid
        shares = base_shares
        refined = False

    effective_n_grid = len(q_grid)

    # User-locked interior-crossing scan (>=3 contiguous strictly-interior).
    crossing = scan_interior_crossing(
        shares=shares,
        q_volumes=q_grid,
        break_even_share=s_be,
        min_run_length=3,
    )

    # q_variance_dominance_flag (code/share-form) — True iff share is
    # strictly below s_be at every grid point.
    q_dom_flag = all(
        (math.isfinite(s) and s < s_be) for s in shares
    )

    # q_variance_dominance_flag_spec_form — True iff var_q / var_total
    # > 1 - s_be at every grid point (panel-mean broadcast: a single
    # mean_q_share scalar replicated). Differs from the share-form by
    # the sign of cov_term in the §4.2 decomposition; coincides for
    # cov_term = 0. Phase-6 Delphi auditor-1 MID-1.
    one_minus_s_be = 1.0 - s_be
    q_dom_flag_spec = math.isfinite(mean_q_share) and mean_q_share > one_minus_s_be

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
        for i in range(effective_n_grid)
    )

    # Use a representative grid_resolution scalar (log-step in dex).
    log_step_dex = (
        (math.log10(q_high) - math.log10(q_low)) / (effective_n_grid - 1)
        if effective_n_grid > 1
        else 0.0
    )

    # Pin anchored bounds to the user-supplied values, not to the
    # log-spaced grid endpoints (numpy.logspace can drift the upper
    # endpoint by ~1 ulp from the input bound).
    points_pinned = (
        SurfaceGridPoint(
            q_volume=q_low,
            fx_variance_share=points[0].fx_variance_share,
            band_low=points[0].band_low,
            band_high=points[0].band_high,
            below_break_even=points[0].below_break_even,
        ),
        *points[1:-1],
        SurfaceGridPoint(
            q_volume=q_high,
            fx_variance_share=points[-1].fx_variance_share,
            band_low=points[-1].band_low,
            band_high=points[-1].band_high,
            below_break_even=points[-1].below_break_even,
        ),
    )

    return SurfaceGridResult(
        points=points_pinned,
        break_even_share=s_be,
        grid_resolution=log_step_dex,
        interior_crossing=crossing.interior_crossing,
        crossing_q_volumes=crossing.crossing_q_volumes,
        anchored_range_low=q_low,
        anchored_range_high=q_high,
        q_variance_dominance_flag=q_dom_flag,
        refined=refined,
        effective_n_grid=effective_n_grid,
        grid_resolution_decision_citation=_GRID_DECISION_CITATION,
        is_panel_mean_broadcast=True,
        q_variance_dominance_flag_spec_form=q_dom_flag_spec,
    )
