"""Descriptive-verdict classifier (spec v0.7 §9; plan task 6.1).

Maps the six §9 input flags to exactly one descriptive-ladder rung —
SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT. E10 v0.7 is descriptive-
only: the classifier can never emit an inferential beta verdict, a
confirmatory rung, or any state outside the three §9 rungs (spec
CORRECTIONS-E10-4 Fix 1). ``emit_inferential_verdict`` exists solely as
the contract that this rejection is structural (test
``test_classifier_cannot_emit_inferential_beta_verdict``).

The classifier is a stateless callable (frozen-dataclass + ``__call__``)
per the SIM-INFRA-0 functional-python tier-discipline; the free-function
convenience wrapper ``classify_verdict`` is exposed for notebook
consumption (plan task 6.2).

§9 ladder (read order — first matching rung fires):

1. DV-gate failed                              → NON-RETIREMENT (dv_fail)
2. Simulator not anchored to §6.2 NON-FANTASY  → NON-RETIREMENT
   (simulator_unanchored)
3. Surface not computed AND material gap       → PARTIAL
4. Surface not computed (no material gap)      → NON-RETIREMENT
   (q_dominance — the spec-anticipated route; q-dominance is the
   structural reason the surface cannot be characterized cleanly)
5. Q-variance dominates the WHOLE range        → NON-RETIREMENT
   (q_dominance)
6. Material gap present (surface partial)      → PARTIAL
7. Otherwise                                   → SURFACE-PRODUCED
   (interior_crossing is surfaced explicitly in the disclosure string;
   spec §9 / plan task 4.2a — never silently averaged away)

The ordering above is collectively exhaustive over the 2^6 = 64 flag
states and pins exactly one rung per state (verified by the Phase-0
RED test ``test_every_flag_state_maps_to_exactly_one_descriptive_verdict``).
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from simulations.e10_gsps._errors import DescriptiveVerdictError
from simulations.e10_gsps.types import (
    DescriptiveVerdict,
    DescriptiveVerdictResult,
    NonRetirementSubtype,
)


def _snapshot(
    *,
    surface_computed: bool,
    material_gap: bool,
    simulator_anchored: bool,
    q_variance_dominates: bool,
    interior_crossing: bool,
    dv_gate_passed: bool,
) -> MappingProxyType[str, bool]:
    """Return the six §9 input flags as a frozen audit mapping."""
    return MappingProxyType(
        {
            "surface_computed": surface_computed,
            "material_gap": material_gap,
            "simulator_anchored": simulator_anchored,
            "q_variance_dominates": q_variance_dominates,
            "interior_crossing": interior_crossing,
            "dv_gate_passed": dv_gate_passed,
        }
    )


def _interior_crossing_disclosure(interior_crossing: bool) -> str:
    """Surface a flagged interior crossing explicitly in the verdict.

    Spec v0.7 §9 / plan task 4.2a: an interior crossing is a non-monotone
    interior dip of the FX-variance share below the ex-ante break-even.
    It is surfaced explicitly in the verdict result even when the primary
    rung is SURFACE-PRODUCED — never silently averaged away.
    """
    if interior_crossing:
        return (
            "Interior crossing flagged: a non-monotone interior dip of the "
            "FX-variance share below the ex-ante break-even was detected "
            "(plan task 4.2a). Surfaced explicitly in the verdict per spec "
            "§9 — never averaged away into the panel-mean share."
        )
    return ""


def _rationale_dv_fail() -> str:
    return (
        "Verdict NON-RETIREMENT (subtype dv_fail). The data-visibility "
        "gate failed during execution: at least one of the 8 central-bank "
        "FX series, the x402 price probe, or The Graph free tier became "
        "dark / paywalled / auth-gated (spec §1 HALT-DV). The descriptive "
        "characterization cannot be produced under a broken DV gate. "
        "Load-bearing input: dv_gate_passed = False."
    )


def _rationale_simulator_unanchored() -> str:
    return (
        "Verdict NON-RETIREMENT (subtype simulator_unanchored). The R6 "
        "NHPP query-workflow simulation engine could not be anchored to "
        "the §6.2 NON-FANTASY observed-trace profile — the user's genuine "
        "observed query trace was thin or non-representative (spec §7 "
        "field 7a / RC OBS-1). There is no default-priors escape hatch. "
        "Load-bearing input: simulator_anchored = False."
    )


def _rationale_partial_material_gap() -> str:
    return (
        "Verdict PARTIAL. The FX-variance-share sensitivity surface was "
        "computed but with material gaps — a panel currency dropped below "
        "its qualifying window, a set of cells carried fewer than two "
        "surviving non-zero-Q days, or the anchored Q-volume range could "
        "not be cleanly bracketed (spec §9 PARTIAL rung). The partial "
        "surface is documented honestly with its gaps named; the methods-"
        "paper §5 anchor is preserved at descriptive form. Load-bearing "
        "input: material_gap = True."
    )


def _rationale_q_dominance_no_surface() -> str:
    return (
        "Verdict NON-RETIREMENT (subtype q_dominance). The FX-variance-"
        "share sensitivity surface could not be characterized cleanly "
        "across the anchored Q-volume range, with no material panel gap "
        "to attribute the failure to — the structural reason is Q-side "
        "dominance of the cost-stream variance (spec §7 field 7b). The "
        "convex FX-volatility hedge does not clear its ex-ante break-"
        "even for the representative Web3 data-analyst profile. Load-"
        "bearing inputs: surface_computed = False, material_gap = False."
    )


def _rationale_q_dominance_full_surface() -> str:
    return (
        "Verdict NON-RETIREMENT (subtype q_dominance). The Q-variance "
        "component dominates the §4.2 three-way log-variance decomposition "
        "across the whole anchored Q-volume range — the FX-variance-share "
        "sensitivity surface sits orders of magnitude below the ex-ante-"
        "pinned break-even s_be = 0.25 at every grid point (spec §7 field "
        "7b; spec §9 NON-RETIREMENT rung). Load-bearing input: "
        "q_variance_dominates = True."
    )


def _rationale_surface_produced(interior_crossing: bool) -> str:
    base = (
        "Verdict SURFACE-PRODUCED (success state). The FX-variance-share "
        "sensitivity surface was computed and characterized across the "
        "anchored Q-volume range under both co-primary FE specifications "
        "and compared against the ex-ante-pinned break-even s_be = 0.25 "
        "(spec §9 SURFACE-PRODUCED rung). The descriptive deliverable is "
        "complete; the methods-paper §5 anchor carries the surface "
        "construction. The descriptive posture is preserved (spec "
        "CORRECTIONS-E10-4 Fix 1)."
    )
    if interior_crossing:
        return base + (
            " Interior crossing surfaced explicitly in the disclosure "
            "string (plan task 4.2a) — the rung remains SURFACE-PRODUCED "
            "but the crossing is named, not averaged away."
        )
    return base


@dataclass(frozen=True, slots=True)
class DescriptiveVerdictClassifierModule:
    """Stateless callable — maps the six §9 flags to exactly one
    descriptive-ladder rung per the spec v0.7 §9 ordering pinned in the
    module docstring."""

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
        snapshot = _snapshot(
            surface_computed=surface_computed,
            material_gap=material_gap,
            simulator_anchored=simulator_anchored,
            q_variance_dominates=q_variance_dominates,
            interior_crossing=interior_crossing,
            dv_gate_passed=dv_gate_passed,
        )
        disclosure = _interior_crossing_disclosure(interior_crossing)

        # Rung 1 — DV-gate failed routes to NON-RETIREMENT (subtype
        # dv_fail) regardless of the other five flags.
        if not dv_gate_passed:
            return DescriptiveVerdictResult(
                verdict=DescriptiveVerdict.NON_RETIREMENT,
                surface_computed=surface_computed,
                material_gap=material_gap,
                simulator_anchored=simulator_anchored,
                q_variance_dominates=q_variance_dominates,
                interior_crossing=interior_crossing,
                dv_gate_passed=dv_gate_passed,
                rationale=_rationale_dv_fail(),
                non_retirement_subtype=NonRetirementSubtype.DV_FAIL,
                interior_crossing_disclosure=disclosure,
                inputs_snapshot=snapshot,
            )

        # Rung 2 — simulator not anchored to §6.2 NON-FANTASY profile.
        if not simulator_anchored:
            return DescriptiveVerdictResult(
                verdict=DescriptiveVerdict.NON_RETIREMENT,
                surface_computed=surface_computed,
                material_gap=material_gap,
                simulator_anchored=simulator_anchored,
                q_variance_dominates=q_variance_dominates,
                interior_crossing=interior_crossing,
                dv_gate_passed=dv_gate_passed,
                rationale=_rationale_simulator_unanchored(),
                non_retirement_subtype=NonRetirementSubtype.SIMULATOR_UNANCHORED,
                interior_crossing_disclosure=disclosure,
                inputs_snapshot=snapshot,
            )

        # Rungs 3 + 4 — surface was not produced cleanly. Material gap
        # routes to PARTIAL; absence of a material gap with the surface
        # still missing routes to NON-RETIREMENT (q_dominance — the
        # structural §7 field 7b reason).
        if not surface_computed:
            if material_gap:
                return DescriptiveVerdictResult(
                    verdict=DescriptiveVerdict.PARTIAL,
                    surface_computed=surface_computed,
                    material_gap=material_gap,
                    simulator_anchored=simulator_anchored,
                    q_variance_dominates=q_variance_dominates,
                    interior_crossing=interior_crossing,
                    dv_gate_passed=dv_gate_passed,
                    rationale=_rationale_partial_material_gap(),
                    non_retirement_subtype=NonRetirementSubtype.N_A,
                    interior_crossing_disclosure=disclosure,
                    inputs_snapshot=snapshot,
                )
            return DescriptiveVerdictResult(
                verdict=DescriptiveVerdict.NON_RETIREMENT,
                surface_computed=surface_computed,
                material_gap=material_gap,
                simulator_anchored=simulator_anchored,
                q_variance_dominates=q_variance_dominates,
                interior_crossing=interior_crossing,
                dv_gate_passed=dv_gate_passed,
                rationale=_rationale_q_dominance_no_surface(),
                non_retirement_subtype=NonRetirementSubtype.Q_DOMINANCE,
                interior_crossing_disclosure=disclosure,
                inputs_snapshot=snapshot,
            )

        # Rung 5 — Q-variance dominates across the WHOLE anchored range.
        # The §9 spec-anticipated route for E10 — the surface is produced
        # but sits orders of magnitude below s_be at every grid point.
        if q_variance_dominates:
            return DescriptiveVerdictResult(
                verdict=DescriptiveVerdict.NON_RETIREMENT,
                surface_computed=surface_computed,
                material_gap=material_gap,
                simulator_anchored=simulator_anchored,
                q_variance_dominates=q_variance_dominates,
                interior_crossing=interior_crossing,
                dv_gate_passed=dv_gate_passed,
                rationale=_rationale_q_dominance_full_surface(),
                non_retirement_subtype=NonRetirementSubtype.Q_DOMINANCE,
                interior_crossing_disclosure=disclosure,
                inputs_snapshot=snapshot,
            )

        # Rung 6 — surface produced with a material gap routes to PARTIAL.
        if material_gap:
            return DescriptiveVerdictResult(
                verdict=DescriptiveVerdict.PARTIAL,
                surface_computed=surface_computed,
                material_gap=material_gap,
                simulator_anchored=simulator_anchored,
                q_variance_dominates=q_variance_dominates,
                interior_crossing=interior_crossing,
                dv_gate_passed=dv_gate_passed,
                rationale=_rationale_partial_material_gap(),
                non_retirement_subtype=NonRetirementSubtype.N_A,
                interior_crossing_disclosure=disclosure,
                inputs_snapshot=snapshot,
            )

        # Rung 7 — SURFACE-PRODUCED (success state). An interior crossing
        # is surfaced explicitly in the disclosure string (plan task 4.2a)
        # but does not flip the rung — the surface was produced cleanly,
        # the crossing is descriptive content reported alongside.
        return DescriptiveVerdictResult(
            verdict=DescriptiveVerdict.SURFACE_PRODUCED,
            surface_computed=surface_computed,
            material_gap=material_gap,
            simulator_anchored=simulator_anchored,
            q_variance_dominates=q_variance_dominates,
            interior_crossing=interior_crossing,
            dv_gate_passed=dv_gate_passed,
            rationale=_rationale_surface_produced(interior_crossing),
            non_retirement_subtype=NonRetirementSubtype.N_A,
            interior_crossing_disclosure=disclosure,
            inputs_snapshot=snapshot,
        )

    def emit_inferential_verdict(self, label: str) -> None:
        """An inferential verdict is structurally BANNED — E10 v0.7 makes
        no inferential beta claim. The classifier rejects every label —
        the refusal is the contract, not an unfinished feature (spec
        CORRECTIONS-E10-4 Fix 1; plan task 0.13 descriptive-posture
        firewall). The argument is consumed in the rejection message
        purely so the test harness can verify the rejection text."""
        raise DescriptiveVerdictError(
            f"E10 v0.7 is descriptive-only; the classifier cannot emit "
            f"inferential verdict label {label!r} (spec §9 / "
            f"CORRECTIONS-E10-4 Fix 1)."
        )


def classify_verdict(
    *,
    surface_computed: bool,
    material_gap: bool,
    simulator_anchored: bool,
    q_variance_dominates: bool,
    interior_crossing: bool,
    dv_gate_passed: bool,
) -> DescriptiveVerdictResult:
    """Free-function convenience wrapper — notebook entry point (plan
    task 6.2 / notebook 05_verdict_writeup). Delegates to the stateless
    callable so the contract lives in one place."""
    return DescriptiveVerdictClassifierModule()(
        surface_computed=surface_computed,
        material_gap=material_gap,
        simulator_anchored=simulator_anchored,
        q_variance_dominates=q_variance_dominates,
        interior_crossing=interior_crossing,
        dv_gate_passed=dv_gate_passed,
    )
