"""FX-variance-share sensitivity-surface Value-tier container (spec v0.7 §4.3).

The FX-variance share is ``Var(d log FX) / Var(d log cost)``. It is NOT
a single number — it is a calibration-conditional sensitivity SURFACE,
the share reported as a function across the anchored Q-volume range. The
surface is the primary deliverable of E10 v0.7 (spec §9 SURFACE-PRODUCED
rung — quoted from the spec ladder for descriptive reference only).

It is evaluated on a grid across the WHOLE range, not at endpoints (plan
task 4.2 / 4.2a — interior-crossing detection).

CORR-E10P-11 / spec v0.6 W-2: bootstrap and permutation bands are DROPPED
at G~=5 (size-broken, EM/DM exchangeability violated). The legacy
``band_low`` / ``band_high`` slots on ``SurfaceGridPoint`` are retained as
NaN-valued placeholders so existing consumers compile; cross-currency
spread is reported instead by ``currency_spread.CurrencySpreadResult``
(non-statistical 5-currency min-max / IQR display).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SurfaceGridPoint:
    """One grid point on the FX-variance-share sensitivity surface.

    ``q_volume`` is the monthly query-volume coordinate in the anchored
    range. ``fx_variance_share`` is ``Var(d log FX) / Var(d log cost)``
    evaluated at that volume. ``band_low`` / ``band_high`` are legacy
    descriptive-band placeholders carried as NaN per CORR-E10P-11 — the
    bootstrap / permutation bands have been DROPPED at G~=5; the
    cross-currency spread is reported by ``CurrencySpreadResult``.
    ``below_break_even`` flags whether this point dips below the
    ex-ante-pinned break-even threshold (plan task 4.2a).
    """

    q_volume: float
    fx_variance_share: float
    band_low: float
    band_high: float
    below_break_even: bool


@dataclass(frozen=True, slots=True)
class SurfaceGridResult:
    """The full FX-variance-share sensitivity surface across the anchored
    Q-volume range.

    ``points`` is the grid (ordered by ``q_volume``). ``break_even_share``
    is the ex-ante-pinned fitted-hedge break-even threshold (spec v0.7
    §4.4 — pinned BEFORE the surface is computed; carries no Stage-1
    estimation content). ``grid_resolution`` is the log-spaced step size
    used (plan task 4.2 ``[brainstorm-judgment]``). ``interior_crossing``
    is True when a non-monotone surface dips below the break-even per the
    user-locked rule (>=3 contiguous strictly-interior cells; plan
    CORR-E10P-4 / task 4.2a). ``crossing_q_volumes`` lists the volumes at
    which any below-break-even cell occurs (full list including
    endpoints; the interior-crossing rule is applied separately).
    ``anchored_range_low`` / ``anchored_range_high`` are the §6.2
    defended-range bounds.

    ``q_variance_dominance_flag`` (code/share-form): True iff the
    FX-variance share is strictly below ``break_even_share`` at every
    grid point — i.e. ``var_fx / var_total < break_even_share`` panel-
    wide. This is the load-bearing input to the §9 classifier (plan
    task 6.1) — added per pre-Phase-4 Model QA review item 6.

    ``q_variance_dominance_flag_spec_form``: True iff
    ``var_q / var_total > 1 - break_even_share`` at every grid point.
    This is the spec-narrative form (spec v0.7 §7 field 7b). The two
    flags are algebraically equivalent IFF ``cov_term = 0`` in the §4.2
    three-way decomposition ``var_total = var_fx + var_q + cov_term``;
    they differ in general by the sign of ``cov_term``. Both are
    emitted for audit transparency. For the E10 panel ``cov_term`` is
    small (decomposition residual ~1e-15 across non-material-gap cells)
    and the two flags coincide. Added per Phase-6 Delphi auditor-1
    MID-1 disclosure requirement (2026-05-23).

    ``refined`` records whether the adaptive doubling fired (user-locked
    rule: refine to 100 log-spaced points if any cell on the base 50-pt
    pass sits within +/-0.5 dex of ``break_even_share``).
    ``effective_n_grid`` is the actual grid length (50 or 100).
    ``grid_resolution_decision_citation`` carries the 4-part
    decision-citation for the user-locked grid choice (reference / why /
    relevance / connection).

    ``is_panel_mean_broadcast`` discloses the construction of the surface
    values across the Q-grid. When True (default) the surface is a
    horizontal line at the panel-mean (or per-currency mean) share —
    every ``SurfaceGridPoint.fx_variance_share`` carries the same scalar
    by construction. This is the honest semantics of the E10 v0.7
    evaluator: the calibrated Cox Q-process produces a panel whose share
    is approximately invariant in Q-volume across the anchored range, so
    the evaluator broadcasts the panel-mean share across the grid (see
    ``modules/surface_grid.py`` and ``modules/currency_spread.py``).
    When False the surface is per-cell (the Phase-0
    ``SurfaceGridModule.__call__`` overload emits one grid point per
    decomposition cell with the cell's own share). Downstream LaTeX
    (§5 methods-paper export) and audit consumers MUST read this flag
    when characterizing the surface — a flat broadcast is descriptively
    honest for E10 v0.7 but MUST NOT be claimed as a Q-dependent
    function. Added per Phase-6 Delphi auditor-1 MID-3 disclosure
    requirement (2026-05-23).
    """

    points: tuple[SurfaceGridPoint, ...]
    break_even_share: float
    grid_resolution: float
    interior_crossing: bool
    crossing_q_volumes: tuple[float, ...]
    anchored_range_low: float
    anchored_range_high: float
    q_variance_dominance_flag: bool
    refined: bool
    effective_n_grid: int
    grid_resolution_decision_citation: str
    is_panel_mean_broadcast: bool = True
    q_variance_dominance_flag_spec_form: bool = False


@dataclass(frozen=True, slots=True)
class InteriorCrossingResult:
    """Result of the interior-crossing scan (plan task 4.2a;
    user-locked rule 2026-05-21).

    User-locked rule: an interior crossing flags iff >=3 contiguous
    strictly-interior grid cells have ``share < break_even_share``.
    Single-cell and 2-cell dips do NOT flag. Endpoints (first and last
    grid cells) are excluded from the interior count — they are reported
    separately on ``endpoint_below_low`` / ``endpoint_below_high``.

    ``interior_crossing`` is True iff the user-locked rule fires.
    ``crossing_q_volumes`` lists every q-volume whose share dipped below
    ``break_even_share`` (the full set, including endpoints — kept for
    backward-compat with the Phase-0 RED harness which checks membership
    of an interior dip volume). ``interior_runs`` lists each contiguous
    run of strictly-interior below-threshold cells as
    ``(start_idx, end_idx)`` pairs (inclusive indices into the parent
    grid); only runs of length >=3 contribute to the flag.
    ``endpoint_below_low`` / ``endpoint_below_high`` carry the
    low-Q / high-Q endpoint dip status (reported separately —
    endpoint-violation, NOT interior-crossing).
    """

    interior_crossing: bool
    crossing_q_volumes: tuple[float, ...]
    interior_runs: tuple[tuple[int, int], ...]
    endpoint_below_low: bool
    endpoint_below_high: bool
