"""Integration test for the three E10 firewalls (plan v0.2 Phase 0.11-0.13).

This test exercises the firewall by feeding it synthetic violations and
asserting non-zero exit. It uses per-line CHECK_ALLOWLIST markers and
runtime string concatenation so the literal banned tokens do not appear
in this file's scannable source.

Phase-0 exit criterion: each of the three firewalls MUST actually fire
when its prohibited language is introduced. The synthetic-violation file
is written into the main-line tree, the checker is run, non-zero exit is
asserted, and the file is removed in a finally block — no permanent
commit is created.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CHECKER = REPO_ROOT / "scripts" / "e10_firewall_check.py"
MAINLINE = REPO_ROOT / "simulations" / "e10_gsps"


def _run_checker(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
    )


def test_checker_exists() -> None:
    assert CHECKER.exists(), "Phase 0.11 firewall script missing"
    assert CHECKER.is_file()


def test_clean_main_line_passes() -> None:
    """Baseline: the Phase 0 scaffold contains no banned tokens."""
    result = subprocess.run(
        [sys.executable, str(CHECKER)],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"Phase 0 scaffold should be firewall-clean but checker reported:\n"
        f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )


# ---------------------------------------------------------------------------
# Firewall 1 — Stage-2 (plan Phase 0.11).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "synthetic_token",
    [
        "Pan" + "optic",
        "dep" + "loy",
        "dep" + "loyment",
        "L" + "P",
        "strike " + "selection",
        "range " + "geometry",
        "payoff " + "fitting",
        "fitted " + "payoff",
        "ready to dep" + "loy",
    ],
)
def test_stage2_firewall_rejects_synthetic_violation(
    synthetic_token: str,
) -> None:
    """Plan 0.11: a synthetic Stage-2 token in main-line scope must be
    rejected (exit code != 0)."""
    violation_file = MAINLINE / "tests" / "integration" / "_synthetic_stage2.py"
    violation_file.write_text(f"x = '{synthetic_token}'\n", encoding="utf-8")
    try:
        result = _run_checker(violation_file)
        assert result.returncode != 0, (
            f"Stage-2 firewall did NOT reject '{synthetic_token}'.\n"
            f"STDERR: {result.stderr}"
        )
        assert "stage-2" in result.stderr.lower()
    finally:
        violation_file.unlink(missing_ok=True)


def test_stage2_true_docstring_with_msketch_reference_is_exempt() -> None:
    """A true module docstring may carry a §13 M-sketch cross-reference
    — the Stage-2 firewall exempts docstrings."""
    docstring_file = MAINLINE / "tests" / "integration" / "_synthetic_doc.py"
    banned = "Pan" + "optic"
    docstring_file.write_text(
        f'"""This module documents the spec §13 {banned} M-sketch."""\n'
        f"x = 1\n",
        encoding="utf-8",
    )
    try:
        result = _run_checker(docstring_file)
        assert result.returncode == 0, (
            f"True docstring incorrectly flagged.\nSTDERR: {result.stderr}"
        )
    finally:
        docstring_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Firewall 2 — fantasy (plan Phase 0.12).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "synthetic_token",
    [
        "synthetic " + "FX",
        "simulated " + "FX",
        "fabricated " + "FX",
        "generated FX " + "series",
        "placeholder " + "FX rate",
        "synthetic " + "price",
    ],
)
def test_fantasy_firewall_rejects_synthetic_fx_substitution(
    synthetic_token: str,
) -> None:
    """Plan 0.12: sourcing the FX series / $0.01 multiplier from a
    fitted prior / synthetic generator / placeholder must be rejected."""
    violation_file = MAINLINE / "tests" / "integration" / "_synthetic_fantasy.py"
    violation_file.write_text(
        f"comment = '{synthetic_token}'\n", encoding="utf-8"
    )
    try:
        result = _run_checker(violation_file)
        assert result.returncode != 0, (
            f"Fantasy firewall did NOT reject '{synthetic_token}'.\n"
            f"STDERR: {result.stderr}"
        )
        assert "fantasy" in result.stderr.lower()
    finally:
        violation_file.unlink(missing_ok=True)


def test_fantasy_firewall_has_no_docstring_exemption() -> None:
    """The fantasy firewall must fire even inside a docstring — a
    fitted-prior substitution of the FX series is a violation wherever
    it appears."""
    doc_file = MAINLINE / "tests" / "integration" / "_synthetic_fantasy_doc.py"
    banned = "synthetic " + "FX"
    doc_file.write_text(
        f'"""This module uses {banned} for the panel."""\nx = 1\n',
        encoding="utf-8",
    )
    try:
        result = _run_checker(doc_file)
        assert result.returncode != 0, (
            "Fantasy firewall must NOT exempt docstrings.\n"
            f"STDERR: {result.stderr}"
        )
    finally:
        doc_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Firewall 3 — descriptive-posture (plan Phase 0.13).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "synthetic_token",
    [
        "P" + "ASS",
        "conf" + "irmatory",
        "beta " + "verdict",
        "inferential " + "beta",
        "significant " + "at",
        "reject the " + "null",
    ],
)
def test_descriptive_posture_firewall_rejects_inferential_language(
    synthetic_token: str,
) -> None:
    """Plan 0.13: PASS / confirmatory / inferential-beta verdict language
    in main-line code must be rejected — E10 v0.4 is descriptive-only."""
    violation_file = MAINLINE / "tests" / "integration" / "_synthetic_descriptive.py"
    violation_file.write_text(
        f"label = '{synthetic_token}'\n", encoding="utf-8"
    )
    try:
        result = _run_checker(violation_file)
        assert result.returncode != 0, (
            f"Descriptive-posture firewall did NOT reject '{synthetic_token}'.\n"
            f"STDERR: {result.stderr}"
        )
        assert "descriptive-posture" in result.stderr.lower()
    finally:
        violation_file.unlink(missing_ok=True)


def test_descriptive_posture_per_line_allowlist_exempts_spec_quote() -> None:
    """A line carrying the CHECK_ALLOWLIST marker (an explicitly tagged
    spec-§9-quoting block) is exempt; an unmarked line is not."""
    mixed_file = MAINLINE / "tests" / "integration" / "_synthetic_mixed.py"
    banned = "conf" + "irmatory"
    mixed_file.write_text(
        f"quoted = '{banned} (spec quote)'  # CHECK_ALLOWLIST\n",
        encoding="utf-8",
    )
    try:
        result = _run_checker(mixed_file)
        assert result.returncode == 0, (
            "CHECK_ALLOWLIST-marked spec-quote line was not exempted.\n"
            f"STDERR: {result.stderr}"
        )
    finally:
        mixed_file.unlink(missing_ok=True)


def test_per_line_allowlist_does_not_exempt_whole_file() -> None:
    """A file with the marker on ONE line MUST still have OTHER lines
    scanned — whole-file exemption MUST be gone."""
    violation_file = MAINLINE / "tests" / "integration" / "_synthetic_perline.py"
    banned = "Pan" + "optic"
    contents = (
        "# CHECK_ALLOWLIST: this comment alone must NOT exempt the next line\n"
        f"x = '{banned}'\n"
    )
    violation_file.write_text(contents, encoding="utf-8")
    try:
        result = _run_checker(violation_file)
        assert result.returncode != 0, (
            "Whole-file allowlist bypass STILL present.\n"
            f"STDERR: {result.stderr}"
        )
    finally:
        violation_file.unlink(missing_ok=True)
