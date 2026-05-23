"""Path constants + reproducibility seed for the stochastic-FX notebook trio.

Mirrors the saas_builder_stage_2/env.py pattern. parents[0] =
stochastic_fx/, parents[1] = notebooks/, parents[2] = simulations/,
parents[3] = repo root.

Used by the stochastic-FX final-simulation notebook trio (01_canonical_verdicts,
02_per_family_figures, 03_strip_preservation) — the reproducibility companion
to ``docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex``.

Responsibilities:

- locate the committed stochastic-FX artifacts under
  ``simulations/stochastic_fx/data/`` (DATA_ROOT) — the per-family
  ``inversion_verdict_{family_id}.json`` sidecars (authoritative
  canonical-pin verdicts) and the ``path_ensemble_{family_id}.parquet``
  files (paper §7 reproducibility anchor).
- write publication-quality reference figures to ``figures/`` (committed PDFs).
- pin the canonical RNG seed used by the paper §7 results
  (``CANONICAL_RNG_SEED = 42``) so the notebook is byte-deterministic
  end-to-end.
- ensure repo root is on sys.path so notebook kernels can import
  ``simulations.stochastic_fx.*`` regardless of where they were launched
  from.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import numpy as np

_THIS_FILE: Final[Path] = Path(__file__).resolve()

_NOTEBOOK_DIR: Final[Path] = _THIS_FILE.parents[0]   # stochastic_fx/
_NOTEBOOKS_DIR: Final[Path] = _THIS_FILE.parents[1]  # notebooks/
_SIMULATIONS_DIR: Final[Path] = _THIS_FILE.parents[2]  # simulations/
REPO_ROOT: Final[Path] = _THIS_FILE.parents[3]         # repo root

NOTEBOOK_DIR: Final[Path] = _NOTEBOOK_DIR
DATA_ROOT: Final[Path] = REPO_ROOT / "simulations" / "stochastic_fx" / "data"
FIGURES_DIR: Final[Path] = _NOTEBOOK_DIR / "figures"

#: Canonical RNG seed used by spec v0.5 §4.2 canonical-pin verification and
#: the paper §7 results table. Held fixed across all three trios so the
#: notebook's outputs match the committed JSON / parquet sidecars
#: byte-for-byte at re-execution.
CANONICAL_RNG_SEED: Final[int] = 42

# Ensure the repo root is on sys.path so `from simulations.stochastic_fx
# import ...` works from a notebook kernel started anywhere.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def reproducibility_seed() -> int:
    """Seed numpy's legacy global RNG and return the canonical pin value.

    The numpy seed is set defensively so any incidental ``np.random.*``
    call in the notebook is deterministic. The authoritative reproducibility
    anchor for the paper is the committed per-family parquet + JSON sidecars
    under ``DATA_ROOT``, which were emitted at ``CANONICAL_RNG_SEED = 42``.
    """
    np.random.seed(CANONICAL_RNG_SEED)
    return CANONICAL_RNG_SEED
