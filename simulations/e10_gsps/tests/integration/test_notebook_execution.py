"""Notebook-execution integration-test harness (plan v0.2 Phase 0.9).

RED in Phase 0: the five E10 notebooks
(``notebooks/e10_gsps/01_simulator_calibration.ipynb`` ...
``05_verdict_writeup.ipynb``) do not yet exist, so the existence
assertion fails. They land across Phases 2-6.

This harness guards against silent-test-pass: it executes each notebook
headless (nbconvert) and asserts a clean run. In Phase 0 it fails at the
existence check; once the notebooks land it executes them.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
NOTEBOOK_DIR = REPO_ROOT / "notebooks" / "e10_gsps"

E10_NOTEBOOKS = (
    "01_simulator_calibration.ipynb",
    "02_panel_decomposition.ipynb",
    "03_surface_characterization.ipynb",
    "04_sensitivity_arms.ipynb",
    "05_verdict_writeup.ipynb",
)


@pytest.mark.parametrize("notebook_name", E10_NOTEBOOKS)
def test_notebook_exists(notebook_name: str) -> None:
    """RED in Phase 0 — the notebooks land in Phases 2-6."""
    path = NOTEBOOK_DIR / notebook_name
    assert path.exists(), (
        f"{notebook_name} not yet created — RED until its phase lands"
    )


@pytest.mark.parametrize("notebook_name", E10_NOTEBOOKS)
def test_notebook_executes_headless(notebook_name: str) -> None:
    """Headless execution guard against silent-test-pass. RED in Phase 0
    (notebook missing); GREEN once the notebook lands and executes."""
    path = NOTEBOOK_DIR / notebook_name
    if not path.exists():
        pytest.fail(f"{notebook_name} missing — cannot execute (RED Phase 0)")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--stdout",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"{notebook_name} failed headless execution:\n{result.stderr}"
    )
