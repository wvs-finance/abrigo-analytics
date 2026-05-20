"""Mechanical anti-fishing enforcement primitives (plan v0.2 Phase 0.10).

This module carries the strings and structural checks the E10 notebook
template must embed, and a compliance check the grep test exercises:

1. **Decision-citation block** — a 4-part block (reference / why /
   relevance / connection) must precede every test or spec choice
   (CLAUDE.md notebook discipline; spec v0.4 decision-citation pattern).

2. **The seven §7 pre-pin fields** — declared in spec v0.4 §7 BEFORE any
   simulation run. The notebook template embeds them verbatim as a
   LOCKED string so a post-data edit is mechanically visible (plan task
   0.10 item b).

3. **Descriptive-posture banner** — E10 v0.4 is descriptive / illustrative
   and makes no inferential beta claim; every notebook carries the banner
   at its top (spec v0.4 §7 field 5 / §9; plan task 0.10 item c).

This module documents the banned strings and the descriptive-posture
text itself, so several of its lines would otherwise trip the firewall.
The checker has NO filename-level exemption — exemption is purely
per-line: every line that names a banned token (or carries the banner
text) ends with an inline ``CHECK_ALLOWLIST`` marker (see lines 26-27
and 53-58). A maintainer adding a new line that names a banned token
MUST add a per-line ``CHECK_ALLOWLIST`` marker to that line; relying on
a whole-file exemption will not work and the firewall will fire.
"""

from __future__ import annotations

# CHECK_ALLOWLIST: anti_fishing_checks.py — this module documents the
# anti-fishing strings themselves; the firewall excludes it from scope.

# The seven §7 pre-pin field LABELS, declared in spec v0.4 §7 LOCKED.
# The notebook template embeds these verbatim; the compliance grep test
# (tests/integration/test_anti_fishing_compliance.py) asserts all seven
# appear in every E10 analysis notebook.
PRE_PIN_FIELD_LABELS: tuple[str, ...] = (
    "Sign",
    "Primary object",
    "Material threshold",
    "Lag",
    "Posture",
    "Panel & FE",
    "HALT condition",
)

# The marker line a notebook's pre-pin cell must carry verbatim so a
# post-data edit to any of the seven fields is mechanically visible.
PRE_PIN_LOCKED_MARKER: str = (
    "E10 v0.4 PRE-PIN LOCKED (spec v0.4 §7) — seven fields declared "
    "BEFORE any simulation run; no post-data tuning."
)

# The descriptive-posture banner every E10 notebook carries at its top.
# CHECK_ALLOWLIST: this string IS the descriptive-posture banner the
# firewall enforces — its own canonical text is exempt per-line.
DESCRIPTIVE_POSTURE_BANNER: str = (  # CHECK_ALLOWLIST
    "DESCRIPTIVE POSTURE — E10 GSPS v0.4 is a descriptive / illustrative "  # CHECK_ALLOWLIST
    "iteration. It makes NO inferential beta claim. The deliverable is the "  # CHECK_ALLOWLIST
    "FX-variance-share sensitivity surface (a description), not a verdict "  # CHECK_ALLOWLIST
    "point. The §7 sign gate is a necessary-not-sufficient descriptive "  # CHECK_ALLOWLIST
    "gate, not an inferential test (spec v0.4 §7 field 5 / §9)."  # CHECK_ALLOWLIST
)

# The four required parts of a decision-citation block (CLAUDE.md).
DECISION_CITATION_PARTS: tuple[str, ...] = (
    "Reference",
    "Why",
    "Relevance",
    "Connection",
)


def pre_pin_fields_present(notebook_text: str) -> bool:
    """True iff all seven §7 pre-pin field labels AND the LOCKED marker
    appear in the given notebook source text (plan task 0.10 item b)."""
    if PRE_PIN_LOCKED_MARKER not in notebook_text:
        return False
    return all(label in notebook_text for label in PRE_PIN_FIELD_LABELS)


def descriptive_posture_banner_present(notebook_text: str) -> bool:
    """True iff the descriptive-posture banner appears in the notebook
    source text (plan task 0.10 item c)."""
    return DESCRIPTIVE_POSTURE_BANNER in notebook_text


def decision_citation_block_present(cell_text: str) -> bool:
    """True iff the cell text carries all four decision-citation parts
    (reference / why / relevance / connection) — CLAUDE.md notebook
    discipline (plan task 0.10 item a)."""
    return all(part in cell_text for part in DECISION_CITATION_PARTS)


__all__ = [
    "PRE_PIN_FIELD_LABELS",
    "PRE_PIN_LOCKED_MARKER",
    "DESCRIPTIVE_POSTURE_BANNER",
    "DECISION_CITATION_PARTS",
    "pre_pin_fields_present",
    "descriptive_posture_banner_present",
    "decision_citation_block_present",
]
