"""Callable-tier PSUBs (Partial State Update Blocks) for the cadCAD integration.

Parent spec: ``docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex``
§6.2 — six PSUBs in deterministic order:

1. PSUB-1 — FX-path-advance (family-dispatched: GBM / OU / Merton /
   deterministic).
2. PSUB-2 — σ_T-accumulator update (paper eq. 7 form, identical to
   ``simulations.stochastic_fx.generators``).
3. PSUB-3 — Cost-trajectory advance (cost-factor-spec responsibility;
   **deferred to Phase 2** — stub raises ``NotImplementedError``).
4. PSUB-4 — Replicating-portfolio update (Carr-Madan 12-leg IronCondor
   strip; **deferred to Phase 2** — stub raises ``NotImplementedError``).
5. PSUB-5 — Wage-premium drain (**deferred to Phase 2** — stub raises
   ``NotImplementedError``).
6. PSUB-6 — Ratchet accumulation (informational, NOT feedback):
   ``R_{j+1} = R_j + max(P_{j+1} − P_j, 0)``.

Phase 1 ships PSUBs 1, 2, 6 — the FX-side, σ_T-side, and ratchet-side
that depend ONLY on the already-verified stochastic-fx machinery. PSUBs
3, 4, 5 are scaffolded as stubs to keep the call sites stable while
their owning specs (cost-factor + replicating-portfolio) converge.

FX-path pre-sampling rationale (PSUB-1)
----------------------------------------
The stochastic-fx generators are batch-oriented: they sample an entire
``(N_paths, n_steps + 1)`` matrix in one call. A per-step single-path
advance would require re-implementing the SDE kernels inside this module,
which would (a) duplicate the EXACT-transition kernels for GBM /
OU / Merton and (b) break Pin Z1.2 reproducibility because the audit_block
recipe in ``simulations.stochastic_fx.generators`` is computed over the
WHOLE path matrix.

Resolution: at simulation initialization, draw ONE complete path via
:func:`pre_sample_fx_path` (which wraps ``GBMPathGenerator``,
``OUPathGenerator``, or ``JumpDiffusionPathGenerator`` with
``n_paths = 1``). PSUB-1 then reads from this pre-sampled array, indexed
by step. Pin Z1.2 determinism is preserved: same
``(family_id, rng_seed, dt, n_steps, x_0)`` quintuple → same path → same
trajectory ``audit_block``. The SDE kernels remain the single source of
truth for FX dynamics.

Tier discipline
---------------
Callable tier under the ``functional-python`` regime. Imports limited to
stdlib + numpy + ``simulations.cadcad.types`` + ``simulations.cadcad._errors``
+ ``simulations.stochastic_fx`` (generators + types). MUST NOT import the
IO-Boundary ``simulations.cadcad.driver``.
"""

from __future__ import annotations

import math
from typing import Final

import numpy as np

from simulations.cadcad._errors import CadCADConfigError
from simulations.cadcad.types import CadCADState
from simulations.stochastic_fx import (
    GBMParameters,
    GBMPathGenerator,
    JumpDiffusionParameters,
    JumpDiffusionPathGenerator,
    OUParameters,
    OUPathGenerator,
)

#: Default annualized FX volatility used to populate the family
#: Parameters frozen-dc when pre-sampling. Chosen to match the canonical
#: pin in ``simulations.stochastic_fx.types.CANONICAL_GBM`` (10% / sqrt(12)).
#: Phase 1 keeps the FX dynamics' free hyperparameters at single canonical
#: defaults — bespoke parameterizations are a Phase 2 surface (cost-factor
#: spec convergence).
_DEFAULT_SIGMA: Final[float] = 0.10 / math.sqrt(12.0)

#: Default drift (zero — neutral; canonical GBM pin choice).
_DEFAULT_MU: Final[float] = 0.0

#: Default OU mean-reversion speed.
_DEFAULT_THETA: Final[float] = 1.0

#: Default Merton jump-arrival intensity (one jump per unit time).
_DEFAULT_LAMBDA_JUMP: Final[float] = 1.0

#: Default Merton jump-size distribution (zero-mean, 10% std).
_DEFAULT_JUMP_MEAN: Final[float] = 0.0
_DEFAULT_JUMP_STD: Final[float] = 0.10


def pre_sample_fx_path(
    family_id: str,
    rng_seed: int,
    n_steps: int,
    dt: float,
    x_0: float,
) -> np.ndarray:
    """Pre-sample one FX path for the entire simulation horizon (PSUB-1 backing).

    Dispatches on ``family_id`` ∈ ``{"gbm", "ou", "merton", "deterministic"}``
    and returns a length-``(n_steps + 1)`` ``float64`` array. The
    ``"deterministic"`` branch returns a constant path equal to ``x_0`` and
    is the Phase 1 sanity-test surface; the three SDE branches dispatch to
    the verified stochastic-fx generators with ``n_paths = 1`` and slice
    out the single row.

    Rationale for pre-sampling is documented at module-docstring level —
    in short, the stochastic-fx kernels' Pin Z1.2 reproducibility recipe
    is matrix-level, so we must consume an entire matrix here even though
    cadCAD logically only consumes one path.

    Parameters
    ----------
    family_id
        Member of the closed alphabet
        ``{"gbm", "ou", "merton", "deterministic"}``.
    rng_seed
        Non-negative ``int`` seed forwarded to the underlying generator
        (Pin Z1.2 surface). Ignored for the ``"deterministic"`` branch.
    n_steps
        Positive ``int`` step count. The underlying SDE generators require
        ``n_steps >= 2`` — callers MUST pre-check this when wiring up the
        cadCAD driver.
    dt
        Positive ``float`` step width. The horizon ``T = n_steps * dt`` is
        passed through to the SDE Parameters frozen-dc and is subject to
        its grid-consistency invariant.
    x_0
        Strictly-positive ``float`` initial FX rate.

    Returns
    -------
    np.ndarray
        Shape ``(n_steps + 1,)``, dtype ``float64``. Entry ``[j]`` is the
        FX rate at simulation step ``j``.

    Raises
    ------
    CadCADConfigError
        If ``family_id`` is not in the closed alphabet.
    SDEParameterError
        (from the underlying generator) if ``(n_steps, dt, x_0)`` violates
        the family Parameters' invariants.
    """
    T = n_steps * dt

    if family_id == "deterministic":
        # Constant-path stub — useful for end-to-end driver sanity tests
        # and as the degenerate-case reference for the σ_T accumulator
        # (σ_T == 0 on a constant path by paper eq. 7).
        return np.full(n_steps + 1, x_0, dtype=np.float64)

    if family_id == "gbm":
        params = GBMParameters(
            mu=_DEFAULT_MU,
            sigma=_DEFAULT_SIGMA,
            x_0=x_0,
            T=T,
            dt=dt,
            n_steps=n_steps,
        )
        ensemble = GBMPathGenerator(params=params)(rng_seed=rng_seed, n_paths=1)
        return ensemble.paths[0].copy()

    if family_id == "ou":
        params = OUParameters(
            theta=_DEFAULT_THETA,
            mu_bar=x_0,
            sigma=_DEFAULT_SIGMA * x_0,
            x_0=x_0,
            T=T,
            dt=dt,
            n_steps=n_steps,
        )
        ensemble = OUPathGenerator(params=params)(rng_seed=rng_seed, n_paths=1)
        return ensemble.paths[0].copy()

    if family_id == "merton":
        params = JumpDiffusionParameters(
            mu=_DEFAULT_MU,
            sigma=_DEFAULT_SIGMA,
            lambda_jump=_DEFAULT_LAMBDA_JUMP,
            jump_mean=_DEFAULT_JUMP_MEAN,
            jump_std=_DEFAULT_JUMP_STD,
            x_0=x_0,
            T=T,
            dt=dt,
            n_steps=n_steps,
        )
        ensemble = JumpDiffusionPathGenerator(params=params)(
            rng_seed=rng_seed, n_paths=1
        )
        return ensemble.paths[0].copy()

    raise CadCADConfigError(
        "family_id must be one of "
        "{'gbm', 'ou', 'merton', 'deterministic'}; "
        f"got {family_id!r}"
    )


def psub_1_fx_advance(state: CadCADState, fx_path: np.ndarray) -> float:
    """PSUB-1 — FX-path advance (paper §6.2 PSUB-1).

    Returns ``X_{j+1}`` by indexing into the pre-sampled FX path. The
    underlying SDE kernels (GBM / OU / Merton) are the single source of
    truth for FX dynamics — see module docstring for the pre-sampling
    rationale and ``pre_sample_fx_path`` for the dispatch.

    Parameters
    ----------
    state
        The current ``CadCADState`` at step ``j``. Only ``state.step`` is
        consumed by this PSUB.
    fx_path
        The full pre-sampled FX path of shape ``(n_steps + 1,)`` produced
        by :func:`pre_sample_fx_path`.

    Returns
    -------
    float
        ``fx_path[state.step + 1]``.
    """
    return float(fx_path[state.step + 1])


def psub_2_sigma_t_accumulator(state: CadCADState, fx_path: np.ndarray) -> float:
    """PSUB-2 helper — GRID-NORMALIZED sum-of-squared-deviations (NOT eq.(7)).

    This is a building-block primitive that returns the running
    sum-of-squared-deviations divided by ``(state.step + 1)`` GRID UNITS,
    NOT by the realised horizon ``T_{j+1} = (state.step + 1) * dt``.

        return = sum_{k=0..j+1} (X_k − mean(X[:j+2]))**2 / (state.step + 1)

    To obtain the eq.(7) σ_T proxy (paper Definition 1.1, normalised by
    ``T_{j+1}``), use :func:`psub_2_sigma_t_accumulator_with_dt` instead.
    The driver uses ``_with_dt`` exclusively; this dt-free variant is
    retained as a unit-test anchor against the deviation-sum component
    of the formula (Wave-1 MQ-F2 disposition: prior docstring misleadingly
    claimed dt was "recovered indirectly"; in fact dt does not appear in
    this function at all).

    Parameters
    ----------
    state
        The current ``CadCADState`` at step ``j``. Only ``state.step`` is
        consumed.
    fx_path
        The full pre-sampled FX path of shape ``(n_steps + 1,)``.

    Returns
    -------
    float
        Sum-of-squared-deviations from the path-mean over the window
        ``fx_path[: state.step + 2]``, divided by ``(state.step + 1)``.
        This is NOT σ_T in the eq.(7) sense — see ``_with_dt`` variant.
    """
    # Slice path[0..j+1] inclusive — the running window at step j+1.
    window = fx_path[: state.step + 2]
    mean = window.mean()
    sum_sq_dev = float(np.sum((window - mean) ** 2))
    grid_intervals = float(state.step + 1)
    return sum_sq_dev / grid_intervals


def psub_2_sigma_t_accumulator_with_dt(
    state: CadCADState, fx_path: np.ndarray, dt: float
) -> float:
    """PSUB-2 — σ_T-accumulator update normalised by the realised horizon.

    Identical to :func:`psub_2_sigma_t_accumulator` except the normalising
    horizon is the dt-scaled realised horizon ``T_{j+1} = (state.step + 1) * dt``
    — exactly matching the stochastic-fx per-path σ_T convention (sum of
    squared deviations divided by the dt-scaled horizon, NOT by the
    sample count).

    This is the form invoked by :func:`run_simulation` in the driver.

    Parameters
    ----------
    state
        The current ``CadCADState`` at step ``j``.
    fx_path
        Full pre-sampled FX path.
    dt
        Positive simulation step width.

    Returns
    -------
    float
        ``S_{j+1} = (1 / T_{j+1}) * sum_{k=0..j+1} (X_k − mean(X[:j+2]))**2``.
    """
    window = fx_path[: state.step + 2]
    mean = window.mean()
    sum_sq_dev = float(np.sum((window - mean) ** 2))
    realised_horizon = (state.step + 1) * dt
    return sum_sq_dev / realised_horizon


def psub_3_cost_advance(state: CadCADState) -> float:
    """PSUB-3 — Cost-trajectory advance (paper §6.2; **DEFERRED**).

    Phase 1 stub. Owning spec — the AI-cost-factor model design in
    ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` — has not
    yet converged on the closed-form cost-update kernel. Raising
    ``NotImplementedError`` keeps callers honest: the driver routes
    around this stub by carrying ``state.C`` forward unchanged during
    Phase 1.

    Raises
    ------
    NotImplementedError
        Always. Deferred to cadCAD Phase 2 per paper §6 charge.
    """
    raise NotImplementedError(
        "PSUB-3 cost-trajectory advance is deferred to cadCAD Phase 2 "
        "per paper §6 charge (cost-factor spec convergence pending)."
    )


def psub_4_replicating_portfolio_update(state: CadCADState) -> float:
    """PSUB-4 — Replicating-portfolio update (paper §6.2; **DEFERRED**).

    Phase 1 stub. The 12-leg Carr-Madan IronCondor strip's per-step MTM
    valuation requires the verified ``cohort_5_strip`` machinery wired up
    to the live FX state — a Phase 2 integration whose design has not yet
    been written.

    Raises
    ------
    NotImplementedError
        Always. Deferred to cadCAD Phase 2 per paper §6 charge.
    """
    raise NotImplementedError(
        "PSUB-4 replicating-portfolio update is deferred to cadCAD "
        "Phase 2 per paper §6 charge (cohort_5_strip wiring pending)."
    )


def psub_5_wage_premium_drain(state: CadCADState) -> float:
    """PSUB-5 — Wage-premium drain (paper §6.2; **DEFERRED**).

    Phase 1 stub. The premium-funded ratchet's drain kinetics depend on
    the cost trajectory (PSUB-3) and the replicating-portfolio MTM
    (PSUB-4); both of those are themselves Phase 2 surfaces, so the drain
    cannot land standalone in Phase 1.

    Raises
    ------
    NotImplementedError
        Always. Deferred to cadCAD Phase 2 per paper §6 charge.
    """
    raise NotImplementedError(
        "PSUB-5 wage-premium drain is deferred to cadCAD Phase 2 per "
        "paper §6 charge (PSUBs 3 + 4 dependency)."
    )


def psub_6_ratchet(state: CadCADState, P_new: float) -> float:
    """PSUB-6 — Ratchet accumulation (paper §6.2 PSUB-6).

    Informational accumulator (NOT a feedback variable):

        R_{j+1} = R_j + max(P_{j+1} − P_j, 0)

    The ratchet tracks the cumulative *positive* MTM increments of the
    replicating portfolio — the realised convexity payoff that converts
    into productive-capital exposure per the Abrigo premium-funded
    ratchet design (paper §1, transmission channel). Because PSUB-4 is
    deferred in Phase 1 (``P_{j+1} == P_j == state.P``), this PSUB
    returns ``state.R`` unchanged in the Phase 1 driver; the wiring
    nonetheless lives here so PSUB-4 + PSUB-6 graduate together in
    Phase 2.

    Parameters
    ----------
    state
        The current ``CadCADState`` at step ``j``. ``state.P`` and
        ``state.R`` are consumed.
    P_new
        The replicating-portfolio MTM at step ``j + 1`` (output of
        PSUB-4; in Phase 1 this is ``state.P`` carried through).

    Returns
    -------
    float
        ``state.R + max(P_new − state.P, 0.0)``.
    """
    return state.R + max(P_new - state.P, 0.0)


__all__ = [
    "pre_sample_fx_path",
    "psub_1_fx_advance",
    "psub_2_sigma_t_accumulator",
    "psub_2_sigma_t_accumulator_with_dt",
    "psub_3_cost_advance",
    "psub_4_replicating_portfolio_update",
    "psub_5_wage_premium_drain",
    "psub_6_ratchet",
]
