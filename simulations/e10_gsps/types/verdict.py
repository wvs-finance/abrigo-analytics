"""Descriptive-verdict Value-tier container (spec v0.4 §9).

E10 v0.4 is a descriptive / illustrative iteration. The §9 ladder is
collectively exhaustive and contains exactly three rungs —
SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT. There is NO ``PASS`` rung
and NO ``FAIL``-on-beta rung: E10 v0.4 makes no inferential beta claim
(spec v0.4 CORRECTIONS-E10-4 Fix 1). The descriptive-posture firewall
(plan Phase 0.13) enforces this mechanically.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DescriptiveVerdict(Enum):
    """The three collectively-exhaustive §9 descriptive-ladder rungs.

    - SURFACE_PRODUCED — the FX-variance-share sensitivity surface is
      computed and characterized across the anchored Q-volume range with
      descriptive bands attached, compared against the ex-ante-pinned
      break-even (the success state).
    - PARTIAL — the surface is computed but with material gaps (a panel
      currency drops below its qualifying window; the anchored range
      cannot be cleanly bracketed; the surface covers only part of the
      intended range).
    - NON_RETIREMENT — the DV gate fails, OR the simulator cannot be
      anchored to the §6.2 NON-FANTASY profile, OR the Q-variance
      component dominates the decomposition across the WHOLE anchored
      range. A valid, acceptable verdict — never engineered away.
    """

    SURFACE_PRODUCED = "SURFACE-PRODUCED"
    PARTIAL = "PARTIAL"
    NON_RETIREMENT = "NON-RETIREMENT"


@dataclass(frozen=True, slots=True)
class DescriptiveVerdictResult:
    """The consolidated descriptive verdict per the §9 ladder.

    ``verdict`` is exactly one of the three ``DescriptiveVerdict`` rungs.
    The six flags below are the §9 classifier inputs (plan task 0.8 /
    6.1): ``surface_computed`` (the surface was produced across the
    anchored range), ``material_gap`` (a panel currency dropped or the
    range could not be bracketed), ``simulator_anchored`` (the §6.2
    NON-FANTASY anchor held), ``q_variance_dominates`` (the Q-variance
    component dominates across the WHOLE range), ``interior_crossing``
    (a non-monotone interior dip below break-even — plan task 4.2a;
    surfaced explicitly, never averaged away), and ``dv_gate_passed``
    (the data-visibility gate held through execution). ``rationale``
    carries the §9-ladder reasoning string.
    """

    verdict: DescriptiveVerdict
    surface_computed: bool
    material_gap: bool
    simulator_anchored: bool
    q_variance_dominates: bool
    interior_crossing: bool
    dv_gate_passed: bool
    rationale: str
