"""Path constants + reproducibility seed for the SaaS-Builder Stage-2 trio.

Mirrors the notebooks/dev_ai_cost/env.py pattern. parents[0] =
saas_builder_stage_2/, parents[1] = notebooks/, parents[2] = simulations/,
parents[3] = repo root.

Used by the math-anchor trio (01_math_anchors, 02_cohort_runs,
03_z_cap_synthesis) to:

- locate the committed Stage-2 artifacts under
  ``simulations/saas_builder/data/`` (DATA_ROOT)
- emit per-notebook tamper-check diffs to ``estimates/`` (gitignored)
- write reference figures to ``figures/`` (committed PDFs)
- ensure repo root is on sys.path so notebook kernels can import
  ``simulations.saas_builder.verify.*`` regardless of where they were
  launched from
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import numpy as np

_THIS_FILE: Final[Path] = Path(__file__).resolve()

_NOTEBOOK_DIR: Final[Path] = _THIS_FILE.parents[0]   # saas_builder_stage_2/
_NOTEBOOKS_DIR: Final[Path] = _THIS_FILE.parents[1]  # notebooks/
_SIMULATIONS_DIR: Final[Path] = _THIS_FILE.parents[2]  # simulations/
REPO_ROOT: Final[Path] = _THIS_FILE.parents[3]         # repo root

DATA_ROOT: Final[Path] = REPO_ROOT / "simulations" / "saas_builder" / "data"
ESTIMATES_ROOT: Final[Path] = _NOTEBOOK_DIR / "estimates"
FIGURES_ROOT: Final[Path] = _NOTEBOOK_DIR / "figures"

# Ensure the repo root is on sys.path so `from simulations.saas_builder.verify
# import ...` works from a notebook kernel started anywhere.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def reproducibility_seed() -> int:
    """Set numpy's legacy global seed and return the canonical value."""
    np.random.seed(0)
    return 0
