"""IO-Boundary-tier orchestrator for the cadCAD integration.

Parent spec: ``docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex``
§6.2 — runs the six PSUBs in deterministic order across ``n_steps``
discrete steps and emits a fully-validated :class:`CadCADTrajectory`.

Phase 1 scope:

- PSUBs 1, 2, 6 are LIVE (FX advance, σ_T accumulator, ratchet
  accumulation).
- PSUBs 3, 4, 5 are stubbed — the driver routes around them by carrying
  ``state.C``, ``state.P``, ``state.W`` forward unchanged.

Audit-block recipe (mirrors Pin Z1.2 from
``simulations.stochastic_fx.generators``):

    audit_block = sha256(
        config_json.encode("utf-8")
        + concatenation of (
            X_path.tobytes(),
            S_path.tobytes(),
            C_path.tobytes(),
            P_path.tobytes(),
            W_path.tobytes(),
            R_path.tobytes(),
        )
    ).hexdigest()

Identical config + same rng_seed → bit-exact trajectory + bit-exact
audit_block. This is the Pin Z1.2 reproducibility contract.

Tier discipline
---------------
IO-Boundary tier under the ``functional-python`` regime. Imports stdlib +
numpy + ``simulations.cadcad.types`` + ``simulations.cadcad.psubs``. This
tier is the ONLY place where mutable scratch arrays are allowed — the
``run_simulation`` driver allocates seven 1-D ``np.ndarray`` buffers,
fills them in a tight Python loop, then hands them to the frozen
:class:`CadCADTrajectory` constructor for invariant-checked freezing.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json

import numpy as np

from simulations.cadcad.psubs import (
    pre_sample_fx_path,
    psub_1_fx_advance,
    psub_2_sigma_t_accumulator_with_dt,
    psub_6_ratchet,
)
from simulations.cadcad.types import CadCADConfig, CadCADState, CadCADTrajectory


def _config_to_json(config: CadCADConfig) -> str:
    """Serialize a ``CadCADConfig`` to a stable canonical JSON string.

    Flattens the nested ``initial_state`` frozen-dc into the same dict
    layer so ``json.dumps(..., sort_keys=True)`` produces a deterministic
    byte ordering. Mirrors the stochastic-fx
    ``_canonical_params_json`` convention.
    """
    initial = dataclasses.asdict(config.initial_state)
    payload = {
        "n_steps": config.n_steps,
        "dt": config.dt,
        "rng_seed": config.rng_seed,
        "family_id": config.family_id,
        "initial_state": initial,
    }
    return json.dumps(payload, sort_keys=True)


def _compute_audit_block(
    config_json: str,
    X_path: np.ndarray,
    S_path: np.ndarray,
    C_path: np.ndarray,
    P_path: np.ndarray,
    W_path: np.ndarray,
    R_path: np.ndarray,
) -> str:
    """Compute the deterministic SHA-256 audit_block for a trajectory (Pin Z1.2).

    Hashes inputs in fixed order: config_json bytes, then each of the six
    float64 path arrays' bytes in the canonical state-variable order
    ``(X, S, C, P, W, R)``. Returns a 64-char lowercase hex digest
    matching the ``CadCADTrajectory.audit_block`` regex.

    The order is LOAD-BEARING: changing it would change every audit_block
    in the package. Mirrors the
    ``simulations.stochastic_fx.generators._compute_audit_block``
    convention.
    """
    hasher = hashlib.sha256()
    hasher.update(config_json.encode("utf-8"))
    for arr in (X_path, S_path, C_path, P_path, W_path, R_path):
        hasher.update(arr.tobytes())
    return hasher.hexdigest()


def run_simulation(config: CadCADConfig) -> CadCADTrajectory:
    """Run the cadCAD simulation under ``config`` and return the trajectory.

    Phase 1 driver: applies PSUBs 1, 2, 6 in order at each step; PSUBs 3,
    4, 5 are stubbed (their state variables ``C``, ``P``, ``W`` carry
    through from ``config.initial_state`` unchanged).

    Per-step PSUB sequencing (paper §6.2):

    1. PSUB-1 — ``X_{j+1} = fx_path[j + 1]`` (pre-sampled at init).
    2. PSUB-2 — ``S_{j+1} = (1/T_{j+1}) * sum(X[:j+2] − mean(X[:j+2]))**2``.
    3. PSUB-3 — STUB: ``C_{j+1} = C_j``.
    4. PSUB-4 — STUB: ``P_{j+1} = P_j``.
    5. PSUB-5 — STUB: ``W_{j+1} = W_j``.
    6. PSUB-6 — ``R_{j+1} = R_j + max(P_{j+1} − P_j, 0)``.

    Note that with PSUB-4 stubbed (``P_{j+1} == P_j``), PSUB-6
    necessarily emits ``R_{j+1} == R_j`` — the ratchet is wired but
    quiescent until Phase 2.

    Parameters
    ----------
    config
        ``CadCADConfig`` — its ``__post_init__`` has already validated
        every invariant on the run-level hyperparameters.

    Returns
    -------
    CadCADTrajectory
        Validated by :meth:`CadCADTrajectory.__post_init__`.

    Raises
    ------
    SDEParameterError
        (from ``pre_sample_fx_path``) if the SDE Parameters' invariants
        reject the cadCAD config's grid (``n_steps`` < 2, etc.).
    CadCADStateError
        (from ``CadCADTrajectory.__post_init__``) if any path goes
        non-finite (would indicate an FX-family blow-up, e.g. extreme
        OU mean-reversion configurations — unreachable for Phase 1's
        canonical defaults).
    """
    n = config.n_steps
    initial = config.initial_state

    # Pre-sample the FX path once at init (paper §6.2 PSUB-1 backing).
    # Pin Z1.2: same (family_id, rng_seed, n, dt, x_0) → same path.
    fx_path = pre_sample_fx_path(
        family_id=config.family_id,
        rng_seed=config.rng_seed,
        n_steps=n,
        dt=config.dt,
        x_0=initial.X,
    )

    # Allocate per-state-variable path buffers; length (n + 1) covers
    # the initial state at step 0 plus n updates.
    steps = np.arange(n + 1, dtype=np.int64)
    X_path = np.empty(n + 1, dtype=np.float64)
    S_path = np.empty(n + 1, dtype=np.float64)
    C_path = np.empty(n + 1, dtype=np.float64)
    P_path = np.empty(n + 1, dtype=np.float64)
    W_path = np.empty(n + 1, dtype=np.float64)
    R_path = np.empty(n + 1, dtype=np.float64)

    # Seed step 0 with the initial state — all six fields verbatim.
    X_path[0] = initial.X
    S_path[0] = initial.S
    C_path[0] = initial.C
    P_path[0] = initial.P
    W_path[0] = initial.W
    R_path[0] = initial.R

    state = initial
    for _ in range(n):
        # PSUB-1: FX advance (pre-sampled).
        X_new = psub_1_fx_advance(state=state, fx_path=fx_path)
        # PSUB-2: σ_T accumulator update — pass the FRESHLY-EXTENDED fx_path
        # so the window at step (j + 1) sees the new X value (which equals
        # fx_path[state.step + 1] by PSUB-1).
        S_new = psub_2_sigma_t_accumulator_with_dt(
            state=state, fx_path=fx_path, dt=config.dt
        )
        # PSUB-3, 4, 5: STUBS for Phase 1 — carry state forward.
        C_new = state.C
        P_new = state.P
        W_new = state.W
        # PSUB-6: ratchet — wired, quiescent under the PSUB-4 stub.
        R_new = psub_6_ratchet(state=state, P_new=P_new)

        next_step = state.step + 1
        X_path[next_step] = X_new
        S_path[next_step] = S_new
        C_path[next_step] = C_new
        P_path[next_step] = P_new
        W_path[next_step] = W_new
        R_path[next_step] = R_new

        # Advance the state for the next iteration. The frozen-dc
        # ``__post_init__`` invariants are re-checked at every step,
        # which catches FX blow-ups (X <= 0 or non-finite) at the
        # earliest possible moment.
        state = CadCADState(
            step=next_step,
            X=X_new,
            S=S_new,
            C=C_new,
            P=P_new,
            W=W_new,
            R=R_new,
        )

    config_json = _config_to_json(config)
    audit_block = _compute_audit_block(
        config_json, X_path, S_path, C_path, P_path, W_path, R_path
    )

    return CadCADTrajectory(
        steps=steps,
        X_path=X_path,
        S_path=S_path,
        C_path=C_path,
        P_path=P_path,
        W_path=W_path,
        R_path=R_path,
        config_json=config_json,
        audit_block=audit_block,
    )


__all__ = [
    "run_simulation",
]
