"""E10.4 sensitivity-arm Value-tier containers (spec v0.7 §9; plan task 5.1).

Phase 5 sensitivity arms are **descriptive concordance only**. No arm gates
a verdict; no arm rescues a primary HALT (the Phase-4 NON-RETIREMENT-via-
HALT-Q-DOMINANCE trajectory is locked by the q_variance_dominance_flag of
``evaluate_surface_grid`` on the real Phase-3 panel; Phase-5 arms quantify
*how robust* that descriptive surface is to alternative panel constructions,
nothing more).

Per spec §9 and plan §1.5 Phase 5: each arm reports a single
``concordance_verdict`` literal ("concordant" / "discordant" / "n/a") whose
DEFINITION here is *purely descriptive*:

- "concordant"  -- the arm preserves Q-variance dominance AND the
                   concordance metric (max absolute share difference vs
                   primary) is below 0.05.
- "discordant"  -- one of the above fails. A "discordant" arm still does
                   NOT rescue the primary HALT (spec §9 is unambiguous on
                   this); it surfaces a robustness divergence the §9
                   classifier reports descriptively in the verdict memo.
- "n/a"         -- the arm could not be executed (e.g. arm (d)'s GBM/JD
                   comparator unavailable; arm (c)'s break window
                   unidentifiable). Honest, never fabricated.

Discipline
----------
``types``-tier: frozen-dataclass containers; no logic, no imports from
``..modules`` / ``..utils``. The ``Literal`` arm-name and verdict
constrain the closed-alphabet of arms / verdicts per CORR-E10P-11.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ArmName = Literal[
    "b_qfx_coupling",
    "c_ngn_break_window",
    "d_gbm_jd_comparator",
    "e_per_currency",
    "f_q_high_extended",
]

ConcordanceVerdict = Literal["concordant", "discordant", "n/a"]


@dataclass(frozen=True, slots=True)
class SensitivityArmResult:
    """One Phase-5 sensitivity arm's descriptive concordance result.

    ``arm_name`` is the closed-alphabet arm identifier
    (see ``ArmName``). ``surface_share_summary`` is a dict with at least
    the keys ``min`` / ``max`` / ``median`` / ``panel_mean`` of the
    arm's FX-variance-share surface across its grid; non-finite or
    structurally-omitted values are emitted as NaN, never as silent zeros.

    ``q_variance_dominance_flag`` is True iff every grid cell on the
    arm's surface carries share strictly below the ex-ante-pinned break-
    even (mirrors the primary surface flag). ``interior_crossing_flag``
    is True iff the user-locked >=3-contiguous strictly-interior rule
    fires on the arm's surface (mirrors ``detect_interior_crossing``).

    ``concordance_metric`` is the max absolute share difference between
    the arm's per-grid-point share and the primary's per-grid-point share
    on the SAME anchored Q-grid (a single non-negative scalar; NaN when
    arm is n/a).

    ``concordance_verdict`` is the descriptive verdict literal (see
    ``ConcordanceVerdict``). Per spec §9 a "discordant" arm does NOT
    rescue a primary HALT — the field is informational only.

    ``decision_citation`` is the 4-part user-locked decision-citation
    block (reference / why / relevance / connection). Populated for arms
    that carry a user-locked judgment (arm (b) — the Q-FX coupling sign
    and magnitude); None for purely mechanical arms.

    ``notes`` is free-form descriptive context the arm runner attaches
    (e.g. arm (c) records the break window dates dropped; arm (d) records
    the calibrated GBM/JD moments; arm (f) records the extended Q-high
    value). Never silent — surfaces in the Phase-5 completion memo.
    """

    arm_name: ArmName
    surface_share_summary: dict[str, float]
    q_variance_dominance_flag: bool
    interior_crossing_flag: bool
    concordance_metric: float
    concordance_verdict: ConcordanceVerdict
    decision_citation: str | None
    notes: str


@dataclass(frozen=True, slots=True)
class SensitivityArmsResult:
    """The Phase-5 sensitivity-arm runner's aggregate result.

    ``arms`` is the ordered tuple of per-arm results (one per executed
    arm; HALT'd arms emit ``concordance_verdict = "n/a"`` and stay in
    the tuple — they are NEVER silently dropped).

    ``primary_q_dominance_flag`` records the Phase-4 primary surface's
    Q-variance-dominance flag for cross-arm reference (True per the
    Phase-4 completion memo; the arms inherit this baseline).

    ``no_rescue_clause`` is the literal spec-§9 non-rescue clause every
    consumer (notebook 04, verdict memo) MUST surface alongside the
    arm results so a stray result table cannot misread an arm as a
    verdict-rescue path. Hard-coded; not configurable.
    """

    arms: tuple[SensitivityArmResult, ...]
    primary_q_dominance_flag: bool
    no_rescue_clause: str


__all__ = [
    "ArmName",
    "ConcordanceVerdict",
    "SensitivityArmResult",
    "SensitivityArmsResult",
]
