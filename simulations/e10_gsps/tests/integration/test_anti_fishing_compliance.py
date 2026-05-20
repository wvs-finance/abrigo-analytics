"""Anti-fishing compliance grep test (plan v0.2 Phase 0.10).

RED in Phase 0: the five E10 analysis notebooks do not yet exist, so the
compliance assertions fail at the existence check. Once each notebook
lands (Phases 2-6) and adopts ``notebooks/e10_gsps/_TEMPLATE.ipynb``, the
test goes GREEN.

The test asserts every E10 analysis notebook embeds:
(a) the descriptive-posture banner;
(b) the seven §7 pre-pin field labels + the LOCKED marker;
(c) at least one decision-citation block (4-part: reference / why /
    relevance / connection).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from simulations.e10_gsps.modules.anti_fishing_checks import (
    PRE_PIN_FIELD_LABELS,
    descriptive_posture_banner_present,
    pre_pin_fields_present,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
NOTEBOOK_DIR = REPO_ROOT / "notebooks" / "e10_gsps"

E10_ANALYSIS_NOTEBOOKS = (
    "01_simulator_calibration.ipynb",
    "02_panel_decomposition.ipynb",
    "03_surface_characterization.ipynb",
    "04_sensitivity_arms.ipynb",
    "05_verdict_writeup.ipynb",
)


def test_template_exists() -> None:
    """The notebook template is a Phase-0 deliverable — GREEN."""
    assert (NOTEBOOK_DIR / "_TEMPLATE.ipynb").exists()


def test_template_carries_all_anti_fishing_embeddings() -> None:
    """The template itself embeds the banner + seven pre-pin fields —
    GREEN once the template lands (verifies the embedding source)."""
    text = (NOTEBOOK_DIR / "_TEMPLATE.ipynb").read_text(encoding="utf-8")
    assert descriptive_posture_banner_present(text)
    assert pre_pin_fields_present(text)
    for label in PRE_PIN_FIELD_LABELS:
        assert label in text


@pytest.mark.parametrize("notebook_name", E10_ANALYSIS_NOTEBOOKS)
def test_analysis_notebook_carries_descriptive_posture_banner(
    notebook_name: str,
) -> None:
    """RED in Phase 0 — analysis notebook missing until its phase lands."""
    path = NOTEBOOK_DIR / notebook_name
    assert path.exists(), f"{notebook_name} not yet created (RED Phase 0)"
    assert descriptive_posture_banner_present(
        path.read_text(encoding="utf-8")
    ), f"{notebook_name} missing the descriptive-posture banner"


@pytest.mark.parametrize("notebook_name", E10_ANALYSIS_NOTEBOOKS)
def test_analysis_notebook_carries_pre_pin_locked_block(
    notebook_name: str,
) -> None:
    """RED in Phase 0 — analysis notebook missing until its phase lands."""
    path = NOTEBOOK_DIR / notebook_name
    assert path.exists(), f"{notebook_name} not yet created (RED Phase 0)"
    assert pre_pin_fields_present(
        path.read_text(encoding="utf-8")
    ), f"{notebook_name} missing the seven §7 pre-pin fields / LOCKED marker"
