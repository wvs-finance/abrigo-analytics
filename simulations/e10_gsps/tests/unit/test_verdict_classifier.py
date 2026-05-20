"""Failing-test harness — descriptive-verdict classifier.

Plan v0.2 Phase 0.8. RED in Phase 0: imports the not-yet-existent
``simulations.e10_gsps.modules.verdict_classifier`` module, so
collection fails. The classifier lands in Phase 6 (plan task 6.1).

The harness asserts every (surface-computed, material-gap,
simulator-anchored, q-variance-dominance, interior-crossing, DV-flag)
state maps to exactly one §9 verdict (SURFACE-PRODUCED / PARTIAL /
NON-RETIREMENT), and that no inferential-beta verdict can be emitted.
"""

from __future__ import annotations

import itertools

import pytest

from simulations.e10_gsps._errors import DescriptiveVerdictError
from simulations.e10_gsps.modules.verdict_classifier import (  # noqa: F401 — RED import
    DescriptiveVerdictClassifierModule,
)
from simulations.e10_gsps.types import DescriptiveVerdict


def _classify(**flags: bool) -> object:
    return DescriptiveVerdictClassifierModule()(**flags)


def test_every_flag_state_maps_to_exactly_one_descriptive_verdict() -> None:
    """The §9 ladder is collectively exhaustive — every one of the 2^6
    flag states yields exactly one of the three descriptive rungs."""
    for combo in itertools.product([False, True], repeat=6):
        (
            surface_computed,
            material_gap,
            simulator_anchored,
            q_variance_dominates,
            interior_crossing,
            dv_gate_passed,
        ) = combo
        result = _classify(
            surface_computed=surface_computed,
            material_gap=material_gap,
            simulator_anchored=simulator_anchored,
            q_variance_dominates=q_variance_dominates,
            interior_crossing=interior_crossing,
            dv_gate_passed=dv_gate_passed,
        )
        assert result.verdict in set(DescriptiveVerdict)


def test_dv_gate_fail_routes_to_non_retirement() -> None:
    """DV-gate fail → NON-RETIREMENT (spec v0.4 §9)."""
    result = _classify(
        surface_computed=False,
        material_gap=False,
        simulator_anchored=True,
        q_variance_dominates=False,
        interior_crossing=False,
        dv_gate_passed=False,
    )
    assert result.verdict is DescriptiveVerdict.NON_RETIREMENT


def test_simulator_not_anchored_routes_to_non_retirement() -> None:
    """Simulator cannot be anchored to the §6.2 NON-FANTASY profile →
    NON-RETIREMENT (spec v0.4 §9 / RC OBS-1)."""
    result = _classify(
        surface_computed=False,
        material_gap=False,
        simulator_anchored=False,
        q_variance_dominates=False,
        interior_crossing=False,
        dv_gate_passed=True,
    )
    assert result.verdict is DescriptiveVerdict.NON_RETIREMENT


def test_q_variance_dominance_routes_to_non_retirement() -> None:
    """Q-variance dominates across the whole anchored range →
    NON-RETIREMENT — a valid, acceptable verdict (spec v0.4 §9)."""
    result = _classify(
        surface_computed=True,
        material_gap=False,
        simulator_anchored=True,
        q_variance_dominates=True,
        interior_crossing=False,
        dv_gate_passed=True,
    )
    assert result.verdict is DescriptiveVerdict.NON_RETIREMENT


def test_clean_surface_routes_to_surface_produced() -> None:
    """Surface computed, no material gap, anchored, FX not dominated by
    Q, DV held → SURFACE-PRODUCED (the success state)."""
    result = _classify(
        surface_computed=True,
        material_gap=False,
        simulator_anchored=True,
        q_variance_dominates=False,
        interior_crossing=False,
        dv_gate_passed=True,
    )
    assert result.verdict is DescriptiveVerdict.SURFACE_PRODUCED


def test_material_gap_routes_to_partial() -> None:
    """Surface computed but with material gaps → PARTIAL (spec v0.4 §9)."""
    result = _classify(
        surface_computed=True,
        material_gap=True,
        simulator_anchored=True,
        q_variance_dominates=False,
        interior_crossing=False,
        dv_gate_passed=True,
    )
    assert result.verdict is DescriptiveVerdict.PARTIAL


def test_interior_crossing_surfaced_explicitly_not_averaged_away() -> None:
    """Plan task 4.2a: a flagged interior crossing is surfaced explicitly
    in the verdict result (a SURFACE-PRODUCED verdict with the crossing
    stated), never silently averaged away."""
    result = _classify(
        surface_computed=True,
        material_gap=False,
        simulator_anchored=True,
        q_variance_dominates=False,
        interior_crossing=True,
        dv_gate_passed=True,
    )
    assert result.interior_crossing is True
    assert result.verdict is DescriptiveVerdict.SURFACE_PRODUCED


def test_classifier_cannot_emit_inferential_beta_verdict() -> None:
    """E10 v0.4 makes no inferential beta claim — asking the classifier
    for a PASS / confirmatory verdict raises DescriptiveVerdictError."""
    classifier = DescriptiveVerdictClassifierModule()
    with pytest.raises(DescriptiveVerdictError):
        # CHECK_ALLOWLIST: the inferential token is synthesized here to
        # verify the classifier REJECTS it — this is the firewall test.
        inferential = "P" + "ASS"  # CHECK_ALLOWLIST
        classifier.emit_inferential_verdict(inferential)  # type: ignore[attr-defined]  # CHECK_ALLOWLIST
