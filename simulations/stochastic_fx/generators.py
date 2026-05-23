"""Callable-tier SDE path generators for the stochastic-fx variant.

Parent spec: ``docs/specs/2026-05-11-stochastic-fx-variant-design.md`` v0.3
§5 eq. (6) (Itô log-update) and §6 eq. (7) (discrete σ_T proxy).
Parent plan: ``docs/plans/2026-05-11-stochastic-fx-variant.md`` §8 Task 3.1
pins the Euler-Maruyama-on-log-scale discretization plus the deterministic
``audit_block`` recipe transcribed here.

This module hosts one frozen-dataclass per SDE family whose ``__call__``
surface accepts a deterministic RNG seed and an ensemble size and returns
the family's :class:`~simulations.stochastic_fx.types.PathEnsemble`. RNG
handling pins determinism (Pin Z1.2): identical
``(params, rng_seed, n_paths)`` triples yield bit-exact ensembles AND
bit-exact ``audit_block``\\ s.

Task 3.1 shipped ``GBMPathGenerator``; Task 3.2 appended ``OUPathGenerator``;
Task 3.3 (this commit) appends ``JumpDiffusionPathGenerator`` (Merton
jump-diffusion).

Discretization scheme (Plan §8.3.1, GBM family)
------------------------------------------------
Euler-Maruyama on the log-scale, exact for GBM modulo float arithmetic:

    log_step = (mu - sigma**2 / 2) * dt + sigma * sqrt(dt) * Z

where ``Z ~ N(0, 1)`` and the trailing ``- sigma**2 / 2`` is the Itô
correction. Omitting it produces a biased mean of the terminal log-price
of magnitude ``sigma**2 / 2 * T``; the math-anchor test in
``simulations/tests/test_saas_stochastic_fx.py`` catches this directly.

σ_T per path (Plan §8.3.1 step 3 / Spec v0.3 §6 eq. 7)
-------------------------------------------------------
Discrete realised-variance proxy, normalised by ``T`` (NOT by ``n+1``):

    sigma_t[i] = (1 / T) * sum_{j=0..n_steps} (paths[i, j] - mean(paths[i, :]))**2

Matches the B1 plan's σ_T contract per MQ-FLAG-B1.1 disposition.

Audit-block recipe (Pin Z1.2)
-----------------------------
SHA-256 over three inputs in fixed order:

1. ``canonical_params_json`` bytes (``json.dumps(asdict(params),
   sort_keys=True)`` — stable byte serialization);
2. ``rng_seed`` packed as 8 little-endian bytes;
3. ``paths.tobytes()`` — the C-contiguous float64 path matrix bytes.

Result is a 64-char lowercase hex string consumed by
``PathEnsemble.__post_init__`` audit-block regex validation.

Tier discipline
---------------
Callable tier under the ``functional-python`` regime. Imports limited to
``dataclasses``, ``hashlib``, ``json``, ``math``, ``numpy``, and
``simulations.stochastic_fx.types``. Validation is delegated to
``PathEnsemble.__post_init__``, so ``simulations.stochastic_fx._errors``
is NOT imported directly here. MUST NOT import
``simulations.stochastic_fx.moments`` (sibling Callable — cross-Callable
imports break tier purity) or ``simulations.stochastic_fx.utils`` (does
not yet exist; Task 5 territory).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from dataclasses import dataclass

import numpy as np

from simulations.stochastic_fx.types import (
    GBMParameters,
    JumpDiffusionParameters,
    OUParameters,
    PathEnsemble,
)


def _canonical_params_json(
    params: GBMParameters | OUParameters | JumpDiffusionParameters,
) -> str:
    """Serialize a Parameters frozen-dc to a stable canonical JSON string.

    ``dataclasses.asdict`` flattens the frozen-dc to a plain ``dict`` of
    plain Python scalars; ``json.dumps(..., sort_keys=True)`` enforces a
    stable byte ordering so the resulting string is reproducible across
    Python sessions. This canonical form is hashed into ``audit_block``
    AND stored on the returned ``PathEnsemble``. Single source of truth
    shared across all family generators (``GBMPathGenerator``,
    ``OUPathGenerator``, ``JumpDiffusionPathGenerator``).

    Helper signature accepts the closed-alphabet three-way union
    ``GBMParameters | OUParameters | JumpDiffusionParameters`` rather
    than a ``Protocol`` — the three Parameters families are a closed set
    per the alphabet ``{"gbm", "ou", "merton"}`` (spec v0.3 §4.2), so a
    Protocol would introduce a new type-name without value. Mirrors the
    Task 3.2 widening precedent.
    """
    return json.dumps(dataclasses.asdict(params), sort_keys=True)


def _compute_audit_block(
    canonical_params_json: str, rng_seed: int, paths: np.ndarray
) -> str:
    """Compute the deterministic SHA-256 audit_block for a path ensemble (Pin Z1.2).

    Inputs are hashed in fixed order: params JSON bytes, then ``rng_seed``
    packed as 8 little-endian bytes, then ``paths.tobytes()`` (the
    C-contiguous float64 path-matrix bytes). Returns a 64-char lowercase
    hex digest matching the ``PathEnsemble.audit_block`` regex.
    """
    hasher = hashlib.sha256()
    hasher.update(canonical_params_json.encode("utf-8"))
    hasher.update(rng_seed.to_bytes(8, "little"))
    hasher.update(paths.tobytes())
    return hasher.hexdigest()


@dataclass(frozen=True)
class GBMPathGenerator:
    """Deterministic GBM path-ensemble generator (Callable tier, Pin Z1.2).

    Holds a :class:`~simulations.stochastic_fx.types.GBMParameters` frozen-dc
    and exposes a ``__call__(rng_seed, n_paths)`` surface that returns a
    :class:`~simulations.stochastic_fx.types.PathEnsemble`. The discretization
    is Euler-Maruyama on the log-scale (exact for GBM modulo float
    arithmetic); the multiplicative log-step embeds the Itô correction
    ``-sigma**2 / 2``. σ_T per path follows spec v0.3 §6 eq. (7) discretely.

    Pin Z1.2 reproducibility: identical ``(params, rng_seed, n_paths)``
    triples yield bit-exact ``paths``, ``sigma_t``, and ``audit_block``.
    """

    params: GBMParameters

    def __call__(self, rng_seed: int, n_paths: int) -> PathEnsemble:
        """Sample ``n_paths`` GBM trajectories under the held parameters.

        Inputs (callee-validated; ``__post_init__`` on the returned
        ``PathEnsemble`` cross-validates the output invariants):

        - ``rng_seed`` — non-negative ``int`` seed for
          ``numpy.random.default_rng``; Pin Z1.2 reproducibility surface.
        - ``n_paths`` — positive ``int`` ensemble size; ``paths`` will have
          shape ``(n_paths, n_steps + 1)``.

        Returns
        -------
        PathEnsemble
            Family ``"gbm"``, validated by
            :meth:`PathEnsemble.__post_init__`.
        """
        params = self.params
        n_steps = params.n_steps
        dt = params.T / n_steps

        rng = np.random.default_rng(rng_seed)
        # Standard-normal Brownian increments; shape (n_paths, n_steps).
        z = rng.standard_normal((n_paths, n_steps))

        # Log-step per Euler-Maruyama on log-scale (Plan §8.3.1 step 2):
        # the trailing -sigma**2/2 is the Itô correction (MQ check anchor).
        log_step = (params.mu - params.sigma**2 / 2.0) * dt + params.sigma * math.sqrt(dt) * z

        # Cumulative log path with a leading zero column so column 0 maps to
        # log(x_0) after exponentiation; resulting shape (n_paths, n_steps+1).
        log_paths = np.concatenate(
            [np.zeros((n_paths, 1), dtype=log_step.dtype), np.cumsum(log_step, axis=1)],
            axis=1,
        )
        paths = params.x_0 * np.exp(log_paths)
        # Column 0 must equal x_0 EXACTLY (bit-exact); enforce via direct
        # assignment to avoid 1 * x_0 * exp(0) float-roundoff drift.
        paths[:, 0] = params.x_0

        # σ_T per path — spec v0.3 §6 eq. (7) DISCRETELY: sum of squared
        # deviations from the path mean, normalised by T (NOT by n+1).
        # Plan §8.3.1 step 3 pins this convention against B1 plan
        # MQ-FLAG-B1.1 disposition.
        path_means = np.mean(paths, axis=1, keepdims=True)
        sigma_t = np.sum((paths - path_means) ** 2, axis=1) / params.T

        canonical_params_json = _canonical_params_json(params)
        audit_block = _compute_audit_block(canonical_params_json, rng_seed, paths)

        return PathEnsemble(
            family_id="gbm",
            paths=paths,
            sigma_t=sigma_t,
            canonical_params_json=canonical_params_json,
            rng_seed=rng_seed,
            audit_block=audit_block,
        )


@dataclass(frozen=True)
class OUPathGenerator:
    """Deterministic OU path-ensemble generator (Callable tier, Pin Z1.2).

    Holds an :class:`~simulations.stochastic_fx.types.OUParameters` frozen-dc
    and exposes a ``__call__(rng_seed, n_paths)`` surface that returns a
    :class:`~simulations.stochastic_fx.types.PathEnsemble` with
    ``family_id == "ou"``.

    Discretization (Plan §8 Task 3.2)
    ----------------------------------
    EXACT conditional-Gaussian transition for the Ornstein-Uhlenbeck SDE
    ``dX_t = theta * (mu_bar − X_t) * dt + sigma * dW_t`` (Vasicek
    dynamics — see e.g. Glasserman, *Monte Carlo Methods in Financial
    Engineering*, §3.3). Per step from ``X_t`` to ``X_{t+dt}``:

        X_{t+dt} = mu_bar
                 + (X_t − mu_bar) * exp(−theta * dt)
                 + sigma * sqrt((1 − exp(−2·theta·dt)) / (2·theta)) * Z

    where ``Z ~ N(0, 1)``. This is EXACT (no Euler discretization error)
    because the OU SDE admits a closed-form Gaussian transition density.
    The decay factor ``exp(−theta · dt)`` and noise scale
    ``sigma · sqrt((1 − exp(−2·theta·dt)) / (2·theta))`` are scalars
    precomputed once outside the per-step loop.

    σ_T per path (Spec v0.3 §6 eq. 7)
    ----------------------------------
    Identical convention to ``GBMPathGenerator``: discrete realised-variance
    sum-of-squared-deviations from the path mean, normalised by ``T`` (not
    by ``n+1``). The convention is family-agnostic.

    Pin Z1.2 reproducibility: identical ``(params, rng_seed, n_paths)``
    triples yield bit-exact ``paths``, ``sigma_t``, and ``audit_block``.
    """

    params: OUParameters

    def __call__(self, rng_seed: int, n_paths: int) -> PathEnsemble:
        """Sample ``n_paths`` OU trajectories under the held parameters.

        Inputs (callee-validated; ``__post_init__`` on the returned
        ``PathEnsemble`` cross-validates the output invariants):

        - ``rng_seed`` — non-negative ``int`` seed for
          ``numpy.random.default_rng``; Pin Z1.2 reproducibility surface.
        - ``n_paths`` — positive ``int`` ensemble size; ``paths`` will have
          shape ``(n_paths, n_steps + 1)``.

        Returns
        -------
        PathEnsemble
            Family ``"ou"``, validated by
            :meth:`PathEnsemble.__post_init__`.
        """
        params = self.params
        n_steps = params.n_steps
        dt = params.T / n_steps
        theta = params.theta
        mu_bar = params.mu_bar
        sigma = params.sigma

        # Exact-transition scalar pre-factors (Glasserman §3.3): the OU
        # SDE's conditional Gaussian transition has deterministic mean-
        # decay ``decay`` and conditional stdev ``noise_scale``.
        decay = math.exp(-theta * dt)
        noise_scale = sigma * math.sqrt((1.0 - math.exp(-2.0 * theta * dt)) / (2.0 * theta))

        rng = np.random.default_rng(rng_seed)
        # Standard-normal innovations; shape (n_paths, n_steps).
        z = rng.standard_normal((n_paths, n_steps))

        # Allocate the path matrix and seed column 0 with the initial
        # condition x_0 (bit-exact, no float drift). Shape (n_paths, n_steps+1).
        paths = np.empty((n_paths, n_steps + 1), dtype=np.float64)
        paths[:, 0] = params.x_0

        # Iterate the OU EXACT-transition kernel per step. The body of
        # this loop is the canonical Vasicek closed-form update; the
        # ``+ noise_scale * z[:, t]`` term is the family's stochastic
        # increment whose stationary variance is sigma**2 / (2*theta).
        for t in range(n_steps):
            paths[:, t + 1] = mu_bar + (paths[:, t] - mu_bar) * decay + noise_scale * z[:, t]

        # σ_T per path — spec v0.3 §6 eq. (7) DISCRETELY: sum of squared
        # deviations from the path mean, normalised by T (NOT by n+1).
        # Family-agnostic; identical convention to GBMPathGenerator.
        path_means = np.mean(paths, axis=1, keepdims=True)
        sigma_t = np.sum((paths - path_means) ** 2, axis=1) / params.T

        canonical_params_json = _canonical_params_json(params)
        audit_block = _compute_audit_block(canonical_params_json, rng_seed, paths)

        return PathEnsemble(
            family_id="ou",
            paths=paths,
            sigma_t=sigma_t,
            canonical_params_json=canonical_params_json,
            rng_seed=rng_seed,
            audit_block=audit_block,
        )


@dataclass(frozen=True)
class JumpDiffusionPathGenerator:
    """Deterministic Merton jump-diffusion path-ensemble generator (Callable tier, Pin Z1.2).

    Holds a :class:`~simulations.stochastic_fx.types.JumpDiffusionParameters`
    frozen-dc and exposes a ``__call__(rng_seed, n_paths)`` surface that
    returns a :class:`~simulations.stochastic_fx.types.PathEnsemble` with
    ``family_id == "merton"``.

    Discretization (Plan §8 Task 3.3)
    ----------------------------------
    Euler-Maruyama on log-scale for the continuous (GBM) component
    augmented by a compound-Poisson jump component. Per step from
    ``X_t`` to ``X_{t+dt}``:

        log_diff_step    = (mu - sigma**2 / 2) * dt + sigma * sqrt(dt) * Z
        N_jumps[i, t]    ~ Poisson(lambda_jump * dt)                   # int count
        aggregated_log_jump[i, t]
                         = N_jumps * jump_mean
                           + sqrt(N_jumps) * jump_std * Z'
        log_step         = log_diff_step + aggregated_log_jump
        X_{t+dt}         = X_t * exp(log_step)

    where ``Z, Z' ~ N(0, 1)`` are independent standard normals. The
    aggregated-log-jump expression is the EXACT distributional
    equivalent of summing ``N_jumps`` iid ``Normal(jump_mean,
    jump_std**2)`` log-multipliers, conditioned on the count ``N_jumps``:
    a Poisson-sum of normals with mean ``μ_J`` and variance ``σ_J²``,
    conditional on count ``N``, is distributed as
    ``Normal(N·μ_J, N·σ_J²)``. This yields O(n_paths · n_steps) work
    instead of the naive O(total_jumps).

    RNG-call order (Pin Z1.2 reproducibility surface)
    --------------------------------------------------
    A SINGLE ``numpy.random.default_rng(rng_seed)`` instance is consumed
    in a FIXED order per call:

    1. ``rng.standard_normal((n_paths, n_steps))`` — diffusion ``Z``;
    2. ``rng.poisson(lambda_dt, (n_paths, n_steps))`` — jump counts;
    3. ``rng.standard_normal((n_paths, n_steps))`` — conditional-jump
       ``Z'``.

    The order is load-bearing for bit-exact reproducibility — changing
    it would change every audit_block in the package. Pin Z1.2.

    σ_T per path (Spec v0.3 §6 eq. 7)
    ----------------------------------
    Identical convention to ``GBMPathGenerator`` / ``OUPathGenerator``:
    discrete realised-variance sum-of-squared-deviations from the path
    mean, normalised by ``T`` (not by ``n+1``). Family-agnostic.

    Pin Z1.2 reproducibility: identical ``(params, rng_seed, n_paths)``
    triples yield bit-exact ``paths``, ``sigma_t``, and ``audit_block``.
    """

    params: JumpDiffusionParameters

    def __call__(self, rng_seed: int, n_paths: int) -> PathEnsemble:
        """Sample ``n_paths`` Merton jump-diffusion trajectories.

        Inputs (callee-validated; ``__post_init__`` on the returned
        ``PathEnsemble`` cross-validates the output invariants):

        - ``rng_seed`` — non-negative ``int`` seed for
          ``numpy.random.default_rng``; Pin Z1.2 reproducibility surface.
        - ``n_paths`` — positive ``int`` ensemble size; ``paths`` will have
          shape ``(n_paths, n_steps + 1)``.

        Returns
        -------
        PathEnsemble
            Family ``"merton"``, validated by
            :meth:`PathEnsemble.__post_init__`.
        """
        params = self.params
        n_steps = params.n_steps
        # Precomputed scalars (OU-style pattern): dt once, lambda_dt once.
        dt = params.T / n_steps
        lambda_dt = params.lambda_jump * dt

        rng = np.random.default_rng(rng_seed)
        # RNG-call order is LOAD-BEARING for Pin Z1.2 — see class
        # docstring. Three streams sampled in fixed order:
        # (a) diffusion Z, (b) Poisson counts, (c) conditional-jump Z'.
        z_diff = rng.standard_normal((n_paths, n_steps))
        n_jumps = rng.poisson(lambda_dt, (n_paths, n_steps))
        z_jump = rng.standard_normal((n_paths, n_steps))

        # (a) Diffusion log-step — identical to GBM (Plan §8.3.1 step 2):
        # the trailing -sigma**2/2 is the Itô correction.
        log_diff_step = (
            params.mu - params.sigma**2 / 2.0
        ) * dt + params.sigma * math.sqrt(dt) * z_diff

        # (c) Aggregated log-jump per (i, t): Poisson-sum-of-normals
        # conditional on count N is Normal(N·μ_J, N·σ_J²). Vectorized as
        # N·μ_J + sqrt(N)·σ_J·Z'. When N_jumps[i, t] == 0 the contribution
        # is exactly 0 (sqrt(0) * Z' = 0); when lambda_jump == 0 every N
        # is 0 so the entire jump aggregate vanishes, collapsing the
        # family to pure GBM (modulo extra RNG draws).
        n_jumps_f = n_jumps.astype(np.float64)
        aggregated_log_jump = (
            n_jumps_f * params.jump_mean
            + np.sqrt(n_jumps_f) * params.jump_std * z_jump
        )

        # Combined log-step.
        log_step = log_diff_step + aggregated_log_jump

        # Cumulative log path with a leading zero column so column 0 maps
        # to log(x_0) after exponentiation; shape (n_paths, n_steps+1).
        # Mirrors GBMPathGenerator path-construction discipline.
        log_paths = np.concatenate(
            [np.zeros((n_paths, 1), dtype=log_step.dtype), np.cumsum(log_step, axis=1)],
            axis=1,
        )
        paths = params.x_0 * np.exp(log_paths)
        # Column 0 must equal x_0 EXACTLY (bit-exact); enforce via direct
        # assignment to avoid 1 * x_0 * exp(0) float-roundoff drift.
        paths[:, 0] = params.x_0

        # σ_T per path — spec v0.3 §6 eq. (7) DISCRETELY (family-agnostic).
        path_means = np.mean(paths, axis=1, keepdims=True)
        sigma_t = np.sum((paths - path_means) ** 2, axis=1) / params.T

        canonical_params_json = _canonical_params_json(params)
        audit_block = _compute_audit_block(canonical_params_json, rng_seed, paths)

        return PathEnsemble(
            family_id="merton",
            paths=paths,
            sigma_t=sigma_t,
            canonical_params_json=canonical_params_json,
            rng_seed=rng_seed,
            audit_block=audit_block,
        )


__all__ = [
    "GBMPathGenerator",
    "JumpDiffusionPathGenerator",
    "OUPathGenerator",
]
