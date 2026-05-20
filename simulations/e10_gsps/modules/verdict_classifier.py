"""Descriptive-verdict classifier — Phase-0 RED stub.

Plan v0.2 task 0.8 declares the failing-test harness; the real §9
descriptive-ladder classifier lands in Phase 6 (plan task 6.1). This
module is a deliberate stub: it defines every symbol the
``test_verdict_classifier`` harness imports so collection succeeds, and
every callable raises ``NotImplementedError`` so the harness goes RED.

E10 v0.4 is descriptive-only — the classifier maps the six §9 flags to
exactly one of SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT and can NEVER
emit an inferential beta verdict (spec v0.4 §9 / CORRECTIONS-E10-4
Fix 1). Mirrors the E8 RED-stub pattern.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulations.e10_gsps.types import DescriptiveVerdictResult

_PHASE6 = "descriptive-verdict classifier lands in Phase 6 (plan task 6.1)"


@dataclass(frozen=True, slots=True)
class DescriptiveVerdictClassifierModule:
    """Stateless callable — maps the six §9 flags to exactly one
    descriptive-ladder rung (RED stub until Phase 6)."""

    def __call__(
        self,
        *,
        surface_computed: bool,
        material_gap: bool,
        simulator_anchored: bool,
        q_variance_dominates: bool,
        interior_crossing: bool,
        dv_gate_passed: bool,
    ) -> DescriptiveVerdictResult:
        raise NotImplementedError(_PHASE6)

    def emit_inferential_verdict(self, label: str) -> None:
        """An inferential verdict is structurally BANNED — E10 v0.4 makes
        no inferential beta claim. Even the Phase-0 stub refuses it (the
        refusal is the contract, not an unfinished feature)."""
        raise NotImplementedError(_PHASE6)
