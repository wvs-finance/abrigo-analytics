"""Descriptive-verdict Value-tier container (spec v0.7 §9).

E10 v0.7 is a descriptive / illustrative iteration. The §9 ladder is
collectively exhaustive and contains exactly three rungs —
SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT. There is NO ``PASS`` rung
and NO inferential-on-beta rung: E10 v0.7 makes no inferential beta
claim (spec v0.7 CORRECTIONS-E10-4 Fix 1). The descriptive-posture
firewall (plan Phase 0.13) enforces this mechanically.

The Phase-6 classifier (plan task 6.1) emits a ``DescriptiveVerdictResult``
that records, in addition to the §9 rung itself, (a) the six §9 input
flags as a frozen audit snapshot, (b) a multi-sentence rationale that
cites which §9 rung fired and why, (c) an explicit interior-crossing
disclosure (the spec §9 / plan task 4.2a rule: a flagged interior
crossing is surfaced explicitly in the verdict, never silently averaged
away), and (d) a NON-RETIREMENT subtype tag (``dv_fail`` /
``simulator_unanchored`` / ``q_dominance`` / ``n/a``) that identifies
which §9 ladder route fired when the verdict is NON-RETIREMENT.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping


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


class NonRetirementSubtype(Enum):
    """Sub-classification of a NON-RETIREMENT verdict (spec v0.7 §9).

    The §9 ladder routes three distinct conditions to NON-RETIREMENT:
    DV-gate fail (the data-visibility gate did not hold through
    execution), simulator-unanchored (the §6.2 NON-FANTASY observed-trace
    anchor failed), and Q-variance dominance (the Q component dominates
    the decomposition across the whole anchored range). The audit
    requires recording WHICH route fired — they reflect different
    underlying failure modes. ``N_A`` records "no applicable subtype"
    when the verdict is SURFACE-PRODUCED or PARTIAL.
    """

    DV_FAIL = "dv_fail"
    SIMULATOR_UNANCHORED = "simulator_unanchored"
    Q_DOMINANCE = "q_dominance"
    N_A = "n/a"


def _empty_snapshot() -> Mapping[str, bool]:
    """Default empty immutable mapping for the inputs snapshot."""
    return MappingProxyType({})


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

    Phase-6 audit fields (defaults preserve Phase-0 strategy + roundtrip
    compatibility):

    - ``non_retirement_subtype`` identifies which §9 ladder route fired
      when the verdict is NON-RETIREMENT (DV fail, simulator unanchored,
      Q-dominance); ``N_A`` for SURFACE-PRODUCED / PARTIAL.
    - ``interior_crossing_disclosure`` surfaces a flagged interior
      crossing explicitly in the verdict, even on a SURFACE-PRODUCED
      rung (spec §9 / plan task 4.2a — never silently averaged away).
    - ``inputs_snapshot`` records the six §9 input flags as a frozen
      mapping for downstream audit.
    """

    verdict: DescriptiveVerdict
    surface_computed: bool
    material_gap: bool
    simulator_anchored: bool
    q_variance_dominates: bool
    interior_crossing: bool
    dv_gate_passed: bool
    rationale: str
    non_retirement_subtype: NonRetirementSubtype = NonRetirementSubtype.N_A
    interior_crossing_disclosure: str = ""
    inputs_snapshot: Mapping[str, bool] = field(default_factory=_empty_snapshot)
