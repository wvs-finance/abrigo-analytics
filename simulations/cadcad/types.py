"""Value-tier containers for the cadCAD integration of stochastic-FX.

Parent spec: ``docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex``
§6.2 — six state variables ``(X, S, C, P, W, R)`` and six PSUBs. This module
declares the three frozen-dataclass Value types that pin the simulation
surface: a per-step state record (:class:`CadCADState`), a hyperparameter
container (:class:`CadCADConfig`), and the multi-step trajectory output
(:class:`CadCADTrajectory`).

State variables (paper §6.2)
-----------------------------
- ``X`` — FX rate at step ``j`` (paper §3-§5 SDE families dispatched).
- ``S`` — running σ_T accumulator at step ``j`` (paper eq. 7 form).
- ``C`` — cost trajectory at step ``j`` (cost-factor-spec responsibility;
  Phase 1 carries the initial state forward untouched — PSUB-3 stub).
- ``P`` — replicating-portfolio MTM (Carr-Madan 12-leg IronCondor strip;
  PSUB-4 stub for Phase 1).
- ``W`` — wage-premium balance (PSUB-5 stub for Phase 1).
- ``R`` — ratchet variable; informational accumulator
  ``R_{j+1} = R_j + max(P_{j+1} − P_j, 0)``.

Tier discipline
---------------
Value tier under ``functional-python`` regime. Imports limited to stdlib +
numpy + the cadCAD typed-error hierarchy. MUST NOT import from
``simulations.cadcad.psubs`` or ``simulations.cadcad.driver`` (sibling
Callable / IO-Boundary tiers). MUST NOT import from
``simulations.stochastic_fx`` Callable or IO modules (cross-tier import
discipline); types-of-types imports from ``simulations.stochastic_fx.types``
ARE admitted by the CLAUDE.md tier rules but are not needed here because
the cadCAD layer is FX-family-agnostic at the Value tier.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Final

import numpy as np

from simulations.cadcad._errors import CadCADConfigError, CadCADStateError

#: Closed alphabet of admitted FX-family identifiers for PSUB-1 dispatch.
#: Mirrors the stochastic-fx package alphabet plus the ``"deterministic"``
#: branch (constant-path stub for sanity tests and degenerate runs).
_FAMILY_ALPHABET: Final[frozenset[str]] = frozenset(
    {"gbm", "ou", "merton", "deterministic"}
)

#: 64-char lowercase hex audit_block regex (sha256 hexdigest format) —
#: identical convention to ``simulations.stochastic_fx.types.PathEnsemble``.
_AUDIT_BLOCK_REGEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _require_finite_state(name: str, value: float) -> None:
    """Raise ``CadCADStateError`` if ``value`` is NaN or +/- infinity."""
    if not math.isfinite(value):
        raise CadCADStateError(f"{name} must be finite; got {value!r}")


def _require_finite_config(name: str, value: float) -> None:
    """Raise ``CadCADConfigError`` if ``value`` is NaN or +/- infinity."""
    if not math.isfinite(value):
        raise CadCADConfigError(f"{name} must be finite; got {value!r}")


# ─── CadCADState ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CadCADState:
    """Per-step state record for the cadCAD integration (paper §6.2).

    Six state variables ``(X, S, C, P, W, R)`` plus the discrete step index
    ``j`` carried as ``step``. The six floats correspond to the paper's
    state-variable list at step ``j``.

    Invariants (raise ``CadCADStateError``):

    - ``step`` is a non-negative ``int`` (not a ``bool``);
    - all six floats are finite;
    - ``X > 0`` (FX rate is a positive scalar by construction);
    - ``W >= 0`` (wage-premium balance is non-negative by accounting).

    ``S``, ``C``, ``P``, ``R`` are unrestricted in sign at this tier; the
    PSUBs enforce family-specific monotonicity where applicable (PSUB-6
    ratchet accumulation, for example, only ever adds non-negative
    increments to ``R``).
    """

    step: int
    X: float
    S: float
    C: float
    P: float
    W: float
    R: float

    def __post_init__(self) -> None:
        if isinstance(self.step, bool) or not isinstance(self.step, int):
            raise CadCADStateError(
                f"step must be an int (not bool); got {type(self.step)!r}"
            )
        if self.step < 0:
            raise CadCADStateError(f"step must be >= 0; got {self.step!r}")
        _require_finite_state("X", self.X)
        _require_finite_state("S", self.S)
        _require_finite_state("C", self.C)
        _require_finite_state("P", self.P)
        _require_finite_state("W", self.W)
        _require_finite_state("R", self.R)
        if self.X <= 0.0:
            raise CadCADStateError(f"X must be > 0; got {self.X!r}")
        if self.W < 0.0:
            raise CadCADStateError(f"W must be >= 0; got {self.W!r}")


# ─── CadCADConfig ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CadCADConfig:
    """Simulation hyperparameters for a single cadCAD run (paper §6.2).

    Pins the run-level reproducibility surface: ``n_steps`` discrete steps
    of width ``dt``, dispatched against ``family_id`` in the closed FX
    alphabet, seeded by ``rng_seed`` (Pin Z1.2 determinism — identical
    config yields identical paths).

    Invariants (raise ``CadCADConfigError``):

    - ``n_steps > 0`` (and not a ``bool``);
    - ``dt > 0`` and finite;
    - ``rng_seed >= 0`` (and not a ``bool``);
    - ``family_id`` in closed alphabet
      ``{"gbm", "ou", "merton", "deterministic"}``;
    - ``initial_state`` is a ``CadCADState`` instance with ``step == 0``
      (callers MUST start the simulation at the origin).

    The ``"deterministic"`` family identifier is a Phase 1 sanity-test
    branch (constant FX path equal to ``initial_state.X``); the
    SDE-bearing branches ``{"gbm", "ou", "merton"}`` dispatch to the
    stochastic-fx generators.
    """

    n_steps: int
    dt: float
    rng_seed: int
    family_id: str
    initial_state: CadCADState

    def __post_init__(self) -> None:
        if isinstance(self.n_steps, bool) or not isinstance(self.n_steps, int):
            raise CadCADConfigError(
                f"n_steps must be an int (not bool); got {type(self.n_steps)!r}"
            )
        if self.n_steps <= 0:
            raise CadCADConfigError(f"n_steps must be > 0; got {self.n_steps!r}")
        _require_finite_config("dt", self.dt)
        if self.dt <= 0.0:
            raise CadCADConfigError(f"dt must be > 0; got {self.dt!r}")
        if isinstance(self.rng_seed, bool) or not isinstance(self.rng_seed, int):
            raise CadCADConfigError(
                f"rng_seed must be an int (not bool); got {type(self.rng_seed)!r}"
            )
        if self.rng_seed < 0:
            raise CadCADConfigError(f"rng_seed must be >= 0; got {self.rng_seed!r}")
        if self.family_id not in _FAMILY_ALPHABET:
            raise CadCADConfigError(
                f"family_id must be one of {sorted(_FAMILY_ALPHABET)!r}; "
                f"got {self.family_id!r}"
            )
        if not isinstance(self.initial_state, CadCADState):
            raise CadCADConfigError(
                "initial_state must be a CadCADState instance; "
                f"got {type(self.initial_state)!r}"
            )
        if self.initial_state.step != 0:
            raise CadCADConfigError(
                "initial_state.step must equal 0; "
                f"got {self.initial_state.step!r}"
            )


# ─── CadCADTrajectory ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CadCADTrajectory:
    """Full simulation output — six per-state-variable path arrays + audit.

    Holds the seven 1-D arrays of length ``n_steps + 1`` (the ``+1``
    accounting for the initial state at step 0), the JSON-serialized
    config used to generate the trajectory, and the 64-char lowercase hex
    audit_block (SHA-256 over config-JSON + concatenated path bytes,
    matching the stochastic-fx Pin Z1.2 recipe).

    Invariants (raise ``CadCADStateError``):

    - ``steps`` is a 1-D ``np.ndarray`` of integer dtype;
    - each of ``X_path / S_path / C_path / P_path / W_path / R_path`` is a
      1-D ``np.ndarray`` of floating dtype;
    - all seven arrays share the same length;
    - all numeric entries are finite;
    - ``config_json`` is a non-empty ``str``;
    - ``audit_block`` matches ``^[0-9a-f]{64}$``.

    Equality / hash caveat: ``__eq__`` and ``__hash__`` are the
    auto-generated frozen-dataclass forms and dispatch through
    ``np.ndarray.__eq__`` on the path fields — so direct trajectory
    equality is intentionally out of scope (mirrors
    ``simulations.stochastic_fx.types.PathEnsemble``). Round-trip
    equality is supplied at the IO-Boundary tier when a persistence
    layer is added.
    """

    steps: np.ndarray
    X_path: np.ndarray
    S_path: np.ndarray
    C_path: np.ndarray
    P_path: np.ndarray
    W_path: np.ndarray
    R_path: np.ndarray
    config_json: str
    audit_block: str

    def __post_init__(self) -> None:
        for name, arr in (
            ("steps", self.steps),
            ("X_path", self.X_path),
            ("S_path", self.S_path),
            ("C_path", self.C_path),
            ("P_path", self.P_path),
            ("W_path", self.W_path),
            ("R_path", self.R_path),
        ):
            if not isinstance(arr, np.ndarray):
                raise CadCADStateError(
                    f"{name} must be a numpy.ndarray; got {type(arr)!r}"
                )
            if arr.ndim != 1:
                raise CadCADStateError(
                    f"{name} must be 1-D; got ndim={arr.ndim!r}"
                )
        if not np.issubdtype(self.steps.dtype, np.integer):
            raise CadCADStateError(
                f"steps must have integer dtype; got {self.steps.dtype!r}"
            )
        for name, arr in (
            ("X_path", self.X_path),
            ("S_path", self.S_path),
            ("C_path", self.C_path),
            ("P_path", self.P_path),
            ("W_path", self.W_path),
            ("R_path", self.R_path),
        ):
            if not np.issubdtype(arr.dtype, np.floating):
                raise CadCADStateError(
                    f"{name} must have floating dtype; got {arr.dtype!r}"
                )
            if not np.all(np.isfinite(arr)):
                raise CadCADStateError(f"{name} must contain only finite values")

        n = self.steps.shape[0]
        for name, arr in (
            ("X_path", self.X_path),
            ("S_path", self.S_path),
            ("C_path", self.C_path),
            ("P_path", self.P_path),
            ("W_path", self.W_path),
            ("R_path", self.R_path),
        ):
            if arr.shape[0] != n:
                raise CadCADStateError(
                    f"{name} length must equal steps length {n!r}; "
                    f"got {arr.shape[0]!r}"
                )

        if not isinstance(self.config_json, str):
            raise CadCADStateError(
                f"config_json must be a str; got {type(self.config_json)!r}"
            )
        if len(self.config_json) == 0:
            raise CadCADStateError("config_json must be a non-empty str")
        if not isinstance(self.audit_block, str):
            raise CadCADStateError(
                f"audit_block must be a str; got {type(self.audit_block)!r}"
            )
        if _AUDIT_BLOCK_REGEX.fullmatch(self.audit_block) is None:
            raise CadCADStateError(
                "audit_block must match ^[0-9a-f]{64}$; "
                f"got {self.audit_block!r}"
            )


__all__ = [
    "CadCADConfig",
    "CadCADState",
    "CadCADTrajectory",
]
