"""FX-variance-share sensitivity-surface Value-tier container (spec v0.4 §4.3).

The FX-variance share is ``Var(d log FX) / Var(d log cost)``. It is NOT
a single number — it is a calibration-conditional sensitivity SURFACE,
the share reported as a function across the anchored Q-volume range. The
surface is the primary deliverable of E10 v0.4 (spec §9 SURFACE-PRODUCED).
It is evaluated on a grid across the WHOLE range, not at endpoints (plan
task 4.2 / 4.2a — interior-crossing detection).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SurfaceGridPoint:
    """One grid point on the FX-variance-share sensitivity surface.

    ``q_volume`` is the monthly query-volume coordinate in the anchored
    range. ``fx_variance_share`` is ``Var(d log FX) / Var(d log cost)``
    evaluated at that volume. ``band_low`` / ``band_high`` carry the
    descriptive uncertainty band (the wild cluster bootstrap / permutation
    spread — illustrative-not-inferential at G~=8 per spec §7).
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
    is the ex-ante-pinned fitted-hedge break-even threshold (spec v0.4
    §4.4 — pinned BEFORE the surface is computed; carries no Stage-1
    estimation content). ``grid_resolution`` is the chosen grid step
    (plan task 4.2 ``[brainstorm-judgment]``). ``interior_crossing`` is
    True when a non-monotone surface dips below the break-even in the
    interior while clearing both endpoints (plan CORR-E10P-4 / task
    4.2a). ``crossing_q_volumes`` lists the volumes at which any
    below-break-even cell occurs. ``anchored_range_low`` /
    ``anchored_range_high`` are the §6.2 defended-range bounds.
    """

    points: tuple[SurfaceGridPoint, ...]
    break_even_share: float
    grid_resolution: float
    interior_crossing: bool
    crossing_q_volumes: tuple[float, ...]
    anchored_range_low: float
    anchored_range_high: float
