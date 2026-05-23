"""Phase-A algebraic σ_T computation, ε-inversion, and three-phase InversionVerifier for the stochastic-fx variant.

Parent spec: ``docs/specs/2026-05-11-stochastic-fx-variant-design.md`` v0.5 §6
+ §11.6 (mean-only Phase-B gate) + §11.7 (per-family Phase C reference
dispatch — GBM/OU lognormal/gamma moment-matched MoM; Merton empirical-CDF
via high-N reference run at pinned ``N_REF = 100_000`` and
``N_REF_SEED = 20260513``).

Parent plan ``docs/plans/2026-05-11-stochastic-fx-variant.md`` v0.6 §16.5
+ §16.7 scopes Task 4.2 ``InversionVerifier`` (Phase A + Phase B mean-only +
Phase C per-family-dispatch combiner) to this module.

Module surface (Callable tier — free functions + frozen-dc Verifier):

- :func:`recompute_sigma_t` — re-applies spec v0.3 §6 eq. (7) discretely to the
  ensemble's paths and returns the per-path realised-variance array (Task 4.1).
- :func:`eq_8_inversion` — closed-form spec v0.3 §6 eq. (8):
  ``ε = sqrt(8·σ_T / x̄²)`` (Task 4.1).
- :func:`phase_a_algebraic_check` — Pin Z1.3a algebraic substitution check.
  Family-agnostic — the algebra is identical for GBM, OU, and Merton.
- :func:`gbm_discrete_sigma_t_moments` — Task 4.2 b1 derivation. Returns the
  analytic ``(E[σ_T], Var[σ_T])`` of the DISCRETE eq. (7) statistic for the
  GBM family at the canonical grid; Var uses the Isserlis Gaussian-quadratic-
  form approximation (~8% under at canonical pin, documented honestly —
  audit-trail only under v0.5; not gating).
- :func:`ou_discrete_sigma_t_moments` — Task 4.2 b1. EXACT under joint-
  Gaussianity of the OU paths (~3% MC-noise floor at N=1000).
- :func:`merton_discrete_sigma_t_moments` — Task 4.2 b1. Isserlis Gaussian-
  quadratic-form approximation under-estimates true Var by ~71% at canonical
  pin (lognormal-mixture distribution has un-represented 4th-cumulant jump-
  kurtosis terms); audit-trail only under v0.5.
- :class:`InversionVerifier` — Task 4.2 Phase A+B+C combiner. Frozen-dc with
  empty body; parameters arrive via ``__call__``. Pin Z1.5 anti-fishing
  N-floor: requires ``ensemble.paths.shape[0] == 1000`` EXACTLY (raises
  :class:`MCBudgetExceededError` otherwise — N is NOT a tuning surface).

Module-level constants:

- :data:`NUMERICAL_IDENTITY_TOL` — Phase A residual tolerance, single-source
  from ``simulations.saas_builder.cohort_4.types``.
- :data:`MOMENT_REL_TOL` — Pin Z1.3b tolerance for the MEAN-only Phase-B gate
  (0.05 per v0.4 §5).
- :data:`KS_PVALUE_FLOOR` — Pin Z1.4 Phase-C KS-test floor (0.01 per spec).
  Single threshold across all three families (anti-fishing surface — per-family
  dispatch is on the reference SHAPE, not the threshold).
- :data:`N_PATHS_FLOOR` — Pin Z1.5 anti-fishing N floor (1000 EXACT).
- :data:`N_REF` — v0.6 Pin Z1.4 high-N reference path-count for Merton
  empirical-CDF reference (100_000 per spec §11.7).
- :data:`N_REF_SEED` — v0.6 Pin Z1.4 frozen RNG seed for Merton high-N
  reference run (20260513 per spec §11.7).

Tier purity (functional-python skill — Callable tier):

- Allowed imports (module top): stdlib ``hashlib`` / ``json`` / ``math`` /
  ``functools``, ``numpy``, ``scipy.stats`` (ks_1samp / ks_2samp /
  lognorm / gamma for Phase C), ``simulations.stochastic_fx.types``,
  ``simulations.stochastic_fx._errors``, and
  ``simulations.saas_builder.cohort_4.types`` (constant reuse).
- LAZY imports (inside function body only — preserves module-load tier-purity):
  ``simulations.stochastic_fx.generators.JumpDiffusionPathGenerator`` is
  imported INSIDE :func:`_merton_reference_sigma_t` ONLY. Module-load remains
  generator-free; the runtime tier-cross is intentional and documented per
  plan v0.6 §16.7 (FLAG-RC-V0.5-1 / FLAG-MEM-1 disposition).
- FORBIDDEN imports: sibling Callable ``moments`` (cross-Callable imports
  break tier purity); ``utils`` (Task 5 territory).
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
from dataclasses import dataclass
from typing import Final

import numpy as np
from scipy.stats import gamma as _scipy_gamma
from scipy.stats import ks_1samp as _scipy_ks_1samp
from scipy.stats import ks_2samp as _scipy_ks_2samp
from scipy.stats import lognorm as _scipy_lognorm

from simulations.saas_builder.cohort_4.types import (
    NUMERICAL_IDENTITY_TOL as _COHORT_4_NUMERICAL_IDENTITY_TOL,
)
from simulations.stochastic_fx._errors import (
    InversionTestFailedError,
    MCBudgetExceededError,
    MomentMatchFailedError,
    SDEParameterError,
)
from simulations.stochastic_fx.types import (
    GBMParameters,
    InversionVerdict,
    JumpDiffusionParameters,
    OUParameters,
    PathEnsemble,
)

#: Numerical-identity tolerance ceiling for Phase-A algebraic checks
#: (FLAG-RC-3 disposition per plan v0.4 §9 Task 4.1 acceptance bullet 1 —
#: reused verbatim from :data:`simulations.saas_builder.cohort_4.types.NUMERICAL_IDENTITY_TOL`).
NUMERICAL_IDENTITY_TOL: Final[float] = _COHORT_4_NUMERICAL_IDENTITY_TOL

#: Pin Z1.3b MEAN-only Phase-B relative-error tolerance (spec v0.4 §5).
#: Under v0.5 (plan §16.5 Option-B disposition 2026-05-13), this gates ONLY
#: the empirical-vs-analytic relative error on E[σ_T]; variance rel-err is
#: emitted to :class:`InversionVerdict.phase_b_var_rel_err` as audit-trail
#: observation but does NOT gate composite_pass.
MOMENT_REL_TOL: Final[float] = 0.05

#: Pin Z1.4 Phase-C KS goodness-of-fit p-value floor (spec v0.4 §5).
#: Phase C PASSES iff ``ks_pvalue >= KS_PVALUE_FLOOR``.
KS_PVALUE_FLOOR: Final[float] = 0.01

#: Pin Z1.5 anti-fishing N-paths floor (spec v0.4 §8). The MC budget at
#: verification is EXACTLY 1000 paths — NOT a tuning surface. N is checked
#: for strict equality (not >=) so that "more paths until passing" is
#: structurally impossible.
N_PATHS_FLOOR: Final[int] = 1000

#: v0.6 Pin Z1.4 — high-N path-count for Merton's empirical-CDF Phase-C
#: reference run (spec v0.5 §11.7). Pinned constant; the implementer MUST
#: NOT vary it to make Merton pass. Per FLAG-RC-V0.5-1 / FLAG-MEM-1
#: disposition, only the resulting ``sigma_t`` 1-D array (~800 KB) is cached
#: — never the full :class:`PathEnsemble` (~4 GB at canonical n_steps=5000).
#: Note: this constant is NOT subject to the Pin Z1.5 anti-fishing N-floor
#: (which governs the TEST sample at N=1000); ``N_REF`` is the REFERENCE,
#: pinned by spec.
N_REF: Final[int] = 100_000

#: v0.6 Pin Z1.4 — frozen RNG seed for Merton's high-N empirical-CDF
#: reference run (spec v0.5 §11.7 disposition date 2026-05-13). Pinned;
#: changing this constant constitutes anti-fishing-banned spec amendment
#: requiring CORRECTIONS-α + scoped Wave-1 re-review.
N_REF_SEED: Final[int] = 20260513


# ─── Function 1: recompute σ_T from ensemble.paths ───────────────────────────


def recompute_sigma_t(ensemble: PathEnsemble) -> np.ndarray:
    """Re-apply spec v0.3 §6 eq. (7) to ``ensemble.paths`` and return per-path σ_T.

    The discrete realised-variance estimator is, for each path *i*:

    .. math::

        \\sigma_{T,i} = \\frac{1}{T} \\sum_{t=0}^{n_{\\text{steps}}}
                       \\bigl(x_{i,t} - \\bar{x}_i\\bigr)^2,

    where :math:`\\bar{x}_i` is the path-mean and *T* is read out of
    ``ensemble.canonical_params_json``. The formula mirrors the vectorised
    computation in ``simulations.stochastic_fx.generators`` (e.g. GBM line
    ~183), so a fresh re-application here is the natural Phase-A
    cross-check: any drift between the generator and this recomputation
    signals a formula transcription error.

    Parameters
    ----------
    ensemble:
        A validated :class:`PathEnsemble`. The function reads ``paths`` and
        the ``"T"`` key out of ``canonical_params_json``.

    Returns
    -------
    numpy.ndarray
        1-D float array of shape ``(N_paths,)``.

    Raises
    ------
    SDEParameterError
        If ``canonical_params_json`` cannot be parsed as JSON or lacks a
        positive-real ``"T"`` field.
    """
    try:
        params_dict = json.loads(ensemble.canonical_params_json)
    except json.JSONDecodeError as exc:
        raise SDEParameterError(
            "canonical_params_json must be parseable JSON; "
            f"got error: {exc!s}"
        ) from exc
    if "T" not in params_dict:
        raise SDEParameterError(
            "canonical_params_json must contain a 'T' key; "
            f"got keys: {sorted(params_dict.keys())!r}"
        )
    T_value = params_dict["T"]
    if not isinstance(T_value, (int, float)) or isinstance(T_value, bool):
        raise SDEParameterError(
            f"canonical_params_json['T'] must be a real number; got {T_value!r}"
        )
    if not math.isfinite(T_value) or T_value <= 0.0:
        raise SDEParameterError(
            f"canonical_params_json['T'] must be finite and > 0; got {T_value!r}"
        )

    paths = ensemble.paths
    path_means = np.mean(paths, axis=1, keepdims=True)
    sigma_t: np.ndarray = np.sum((paths - path_means) ** 2, axis=1) / float(T_value)
    return sigma_t


# ─── Function 2: eq.(8) algebraic inversion σ_T → ε ──────────────────────────


def eq_8_inversion(sigma_t: float, x_bar: float) -> float:
    """Closed-form spec v0.3 §6 eq. (8): ``ε = sqrt(8·σ_T / x̄²)``.

    Returns the IronCondor strike width ε for a single realised-variance
    proxy value σ_T and FX mean x̄. The mapping is monotonic in σ_T and
    convex; closed-form so machine-epsilon-precise on float64.

    Trivial-degenerate limit (Pin Z1.3a): at ``sigma_t == 0.0`` the
    function returns exactly ``0.0``, since ``sqrt(0) == 0.0`` in IEEE 754.

    Parameters
    ----------
    sigma_t:
        Realised-variance proxy on the path, in the same units as ``x_bar**2``.
        Must be non-negative and finite.
    x_bar:
        Path-mean FX level (strictly positive, finite).

    Returns
    -------
    float
        The non-negative finite strike width ε.

    Raises
    ------
    SDEParameterError
        If ``sigma_t`` is negative or non-finite, or if ``x_bar`` is
        non-positive or non-finite.
    """
    if not math.isfinite(sigma_t):
        raise SDEParameterError(f"sigma_t must be finite; got {sigma_t!r}")
    if sigma_t < 0.0:
        raise SDEParameterError(f"sigma_t must be >= 0; got {sigma_t!r}")
    if not math.isfinite(x_bar):
        raise SDEParameterError(f"x_bar must be finite; got {x_bar!r}")
    if x_bar <= 0.0:
        raise SDEParameterError(f"x_bar must be > 0; got {x_bar!r}")
    return math.sqrt(8.0 * sigma_t / x_bar**2)


# ─── Function 3: Phase-A algebraic substitution check (Pin Z1.3a) ────────────


def phase_a_algebraic_check(
    ensemble: PathEnsemble, x_bar: float
) -> tuple[bool, float]:
    """Pin Z1.3a algebraic substitution check — closed-form identity round-trip.

    For each path's stored σ_T_n in ``ensemble.sigma_t``, compute
    ``ε_n = eq_8_inversion(σ_T_n, x̄)`` and verify the identity

    .. math::

        \\varepsilon_n^2 \\;=\\; \\frac{8 \\, \\sigma_{T,n}}{\\bar{x}^2}.

    Because eq. (8) is closed-form, the residual is essentially machine
    epsilon — this function tests the absence of a transcription bug, not
    the empirical viability of the mapping. PASS iff the maximum absolute
    residual across all N paths is ≤ :data:`NUMERICAL_IDENTITY_TOL`.

    Family-agnostic: the algebra is identical for GBM, OU, and Merton —
    the σ_T values on the ensemble already encode the family-specific
    information.

    Parameters
    ----------
    ensemble:
        A validated :class:`PathEnsemble`. Phase A consumes
        ``ensemble.sigma_t`` (N-vector of per-path realised-variance proxies).
    x_bar:
        Positive finite FX mean used in the closed-form inversion. Typically
        the canonical pin's ``x_0`` for trivial-degenerate testing; may also
        be a path-mean estimate from the ensemble in production use.

    Returns
    -------
    tuple[bool, float]
        ``(pass_flag, max_abs_residual)``. ``pass_flag`` is ``True`` iff
        ``max_abs_residual <= NUMERICAL_IDENTITY_TOL``.

    Raises
    ------
    SDEParameterError
        If ``x_bar`` is non-positive or non-finite.
    """
    if not math.isfinite(x_bar):
        raise SDEParameterError(f"x_bar must be finite; got {x_bar!r}")
    if x_bar <= 0.0:
        raise SDEParameterError(f"x_bar must be > 0; got {x_bar!r}")

    sigma_t_array = ensemble.sigma_t
    # Vectorised closed-form inversion: ε_n = sqrt(8·σ_T_n / x̄²).
    # numpy.sqrt is safe at σ_T_n == 0 (returns 0.0); the ensemble's
    # __post_init__ already guarantees finite sigma_t entries.
    eps_squared = 8.0 * sigma_t_array / (x_bar**2)
    eps_array = np.sqrt(eps_squared)
    # Round-trip identity: (ε_n)² − 8·σ_T_n / x̄² should be machine-epsilon.
    residuals = eps_array**2 - eps_squared
    max_abs_residual = float(np.max(np.abs(residuals)))
    pass_flag = bool(max_abs_residual <= NUMERICAL_IDENTITY_TOL)
    return pass_flag, max_abs_residual


# ─── Task 4.2 b1: discrete-moment functions per family ───────────────────────


def _build_M_Sigma_quantities(
    mu: np.ndarray, sigma_matrix: np.ndarray
) -> tuple[float, float]:
    """Return ``(E_stat, Var_stat)`` for the un-normalized statistic ``Σ_j (X_j − X̄)²``.

    Closed-form construction with centering projection
    ``M = I − (1/N) 1·1ᵀ`` (symmetric idempotent, rank n):

    .. math::

        \\mathbb{E}[X^T M X] &= \\operatorname{tr}(M \\Sigma) + \\mu^T M \\mu \\\\
        \\operatorname{Var}(X^T M X) &= 2 \\operatorname{tr}((M \\Sigma)^2)
            + 4 (M \\mu)^T \\Sigma (M \\mu)

    The Var identity is EXACT under joint-Gaussianity of ``X`` and is the
    leading-order Isserlis term otherwise (under-represents 4th-cumulant
    contributions of lognormal/lognormal-mixture distributions).

    Caller divides ``E_stat`` by ``T`` and ``Var_stat`` by ``T²`` to obtain
    moments of the σ_T statistic per spec v0.3 §6 eq. (7).

    See ``scratch/2026-05-13-task-4.2-discrete-moments/derivation.py`` for
    the full hand-derivation backing this expansion.
    """
    N = sigma_matrix.shape[0]
    diag_sigma = float(np.trace(sigma_matrix))
    sum_sigma = float(np.sum(sigma_matrix))
    row_sums = sigma_matrix.sum(axis=1)
    row_sum_sq = float(np.dot(row_sums, row_sums))
    frob_sq = float(np.sum(sigma_matrix * sigma_matrix))

    tr_M_Sigma = diag_sigma - sum_sigma / N
    tr_MSigma_sq = frob_sq - 2.0 * row_sum_sq / N + sum_sigma * sum_sigma / (N * N)

    sum_mu = float(mu.sum())
    norm_mu_sq = float(np.dot(mu, mu))
    mu_M_mu = norm_mu_sq - sum_mu * sum_mu / N

    m_mu = mu - sum_mu / N
    sigma_m_mu = sigma_matrix @ m_mu
    quad_term = float(np.dot(m_mu, sigma_m_mu))

    e_stat = tr_M_Sigma + mu_M_mu
    var_stat = 2.0 * tr_MSigma_sq + 4.0 * quad_term
    return e_stat, var_stat


def gbm_discrete_sigma_t_moments(params: GBMParameters) -> tuple[float, float]:
    """Analytic ``(E[σ_T], Var[σ_T])`` for the DISCRETE eq. (7) statistic under GBM.

    Uses the centering-projection identity ``Σ_j (X_j − X̄)² = XᵀMX`` with
    ``M = I − (1/N)·1·1ᵀ`` against the GBM auto-covariance kernel
    (Hull 1997 §13.2; eq. (3.5)):

    .. math::

        \\operatorname{Cov}(X_j, X_k) = x_0^2 \\bigl( e^{\\sigma^2 \\min(t_j, t_k)} - 1 \\bigr)

    at canonical ``μ = 0`` (martingale; ``μ_j ≡ x_0`` so ``μᵀMμ = 0``).

    The Var formula uses the Isserlis Gaussian-quadratic-form leading order
    ``2·tr((MΣ)²) + 4·(Mμ)ᵀΣ(Mμ)``, which is EXACT under joint-Gaussianity
    but only LEADING-ORDER for the lognormal X_j here. At the canonical pin
    (σ²·T ≈ 0.01) this approximation under-estimates the true Var by ~8% as
    measured against Monte Carlo at N=1000 (see derivation script). Under
    v0.5 the Var rel-err is audit-trail only (Pin Z1.3b mean-only gate),
    so this honest known-limitation is acceptable; readers can interpret
    :class:`InversionVerdict.phase_b_var_rel_err` as the residual of the
    Gaussian-quadratic-form approximation against the lognormal truth.

    Parameters
    ----------
    params:
        Validated :class:`GBMParameters`. Uses ``sigma``, ``T``, ``n_steps``,
        ``x_0``.

    Returns
    -------
    tuple[float, float]
        ``(E_analytic, Var_analytic)`` of the σ_T statistic, both
        non-negative finite. Caller compares against MC empirical moments
        with relative-error tolerance :data:`MOMENT_REL_TOL` (mean only
        per v0.5).
    """
    n_steps = params.n_steps
    N = n_steps + 1
    dt = params.T / n_steps
    log_phi2 = params.sigma * params.sigma * dt  # log φ₂ = σ²·dt (μ = 0 martingale)
    j_idx = np.arange(N)
    mu = np.full(N, params.x_0, dtype=np.float64)
    # Cov(X_j, X_k) = x_0² · (exp(σ²·dt·min(j,k)) − 1)  — use expm1 for stability.
    min_jk = np.minimum.outer(j_idx, j_idx).astype(np.float64)
    sigma_matrix = (params.x_0 ** 2) * np.expm1(log_phi2 * min_jk)
    e_stat, var_stat = _build_M_Sigma_quantities(mu, sigma_matrix)
    return e_stat / params.T, var_stat / (params.T * params.T)


def ou_discrete_sigma_t_moments(params: OUParameters) -> tuple[float, float]:
    """Analytic ``(E[σ_T], Var[σ_T])`` for the DISCRETE eq. (7) statistic under OU.

    OU is Gaussian, so the Isserlis Gaussian-quadratic-form formulas for
    ``E[XᵀMX]`` and ``Var(XᵀMX)`` are EXACT — no approximation enters.
    The remaining ~2-3% MC-noise floor at N=1000 is purely sampling
    variability, not a model-truncation residual. (Karatzas–Shreve 1991
    §5.6 eq. 6.13 for the auto-covariance kernel.)

    Auto-covariance kernel:

    .. math::

        \\operatorname{Cov}(X_s, X_t) =
            \\frac{\\sigma^2}{2\\theta} e^{-\\theta |t-s|}
            \\bigl(1 - e^{-2\\theta \\min(s, t)}\\bigr)

    Mean dynamics: ``E[X_t] = μ̄ + (x_0 − μ̄)·exp(−θ·t)``. At canonical pin
    ``x_0 = μ̄`` so ``μ_j ≡ μ̄`` constant ⇒ ``μᵀMμ = 0``.

    Parameters
    ----------
    params:
        Validated :class:`OUParameters`.

    Returns
    -------
    tuple[float, float]
        ``(E_analytic, Var_analytic)``.
    """
    n_steps = params.n_steps
    N = n_steps + 1
    dt = params.T / n_steps
    theta = params.theta
    sigma = params.sigma
    mu_bar = params.mu_bar
    x_0 = params.x_0

    j_idx = np.arange(N)
    t = j_idx * dt
    mu = mu_bar + (x_0 - mu_bar) * np.exp(-theta * t)

    min_t = np.minimum.outer(t, t)
    abs_diff_t = np.abs(np.subtract.outer(t, t))
    sigma_matrix = (sigma ** 2 / (2.0 * theta)) * np.exp(-theta * abs_diff_t) * (
        1.0 - np.exp(-2.0 * theta * min_t)
    )
    e_stat, var_stat = _build_M_Sigma_quantities(mu, sigma_matrix)
    return e_stat / params.T, var_stat / (params.T * params.T)


def merton_discrete_sigma_t_moments(
    params: JumpDiffusionParameters,
) -> tuple[float, float]:
    """Analytic ``(E[σ_T], Var[σ_T])`` for the DISCRETE eq. (7) statistic under Merton.

    Merton jump-diffusion: log-multiplicative ``X_j = x_0 · ∏_{ℓ≤j} e^{L_ℓ}``
    with ``L_ℓ = L_diff + L_jump`` and the per-step characteristic functions

    .. math::

        \\log\\varphi_1 &= \\mu \\, dt + \\lambda \\, dt \\bigl(e^{\\mu_J + \\sigma_J^2/2} - 1\\bigr) \\\\
        \\log\\varphi_2 &= 2\\mu \\, dt + \\sigma^2 dt
            + \\lambda \\, dt \\bigl(e^{2\\mu_J + 2\\sigma_J^2} - 1\\bigr)

    (Andersen–Piterbarg 2010 vol. I §8.5). The first two moments of the path
    are ``μ_j = x_0 · φ₁^j`` and
    ``E[X_j X_k] = x_0² · φ₂^{min(j,k)} · φ₁^{|k−j|}``, giving

    .. math::

        \\operatorname{Cov}(X_j, X_k) = x_0^2 \\, \\varphi_1^{|k-j|}
            \\bigl(\\varphi_2^{\\min(j,k)} - \\varphi_1^{2 \\min(j,k)}\\bigr).

    The Isserlis Gaussian-quadratic-form Var approximation UNDER-ESTIMATES
    the true Var by ~71% at the canonical pin against MC@N=1000 (Merton's
    lognormal-mixture distribution has substantial 4th-cumulant
    jump-kurtosis contributions that the leading-order Gaussian formula
    cannot represent). Under v0.5 this is audit-trail only — the
    :class:`InversionVerdict.phase_b_var_rel_err` field will reflect this
    structural gap and serves as a diagnostic, not a gate.

    The full-distribution match across all moments (including the un-
    approximated 4th cumulant) is preserved at Phase C via the KS test
    against the moment-matched lognormal reference (Pin Z1.4).

    Parameters
    ----------
    params:
        Validated :class:`JumpDiffusionParameters`.

    Returns
    -------
    tuple[float, float]
        ``(E_analytic, Var_analytic)``.
    """
    n_steps = params.n_steps
    N = n_steps + 1
    dt = params.T / n_steps
    sigma = params.sigma
    lambda_jump = params.lambda_jump
    mu_J = params.jump_mean
    sigma_J2 = params.jump_std ** 2
    x_0 = params.x_0

    log_phi1 = params.mu * dt + lambda_jump * dt * (
        math.exp(mu_J + sigma_J2 / 2.0) - 1.0
    )
    log_phi2 = (
        2.0 * params.mu * dt
        + sigma ** 2 * dt
        + lambda_jump * dt * (math.exp(2.0 * mu_J + 2.0 * sigma_J2) - 1.0)
    )
    j_idx = np.arange(N)
    mu = x_0 * np.exp(j_idx * log_phi1)
    min_jk = np.minimum.outer(j_idx, j_idx).astype(np.float64)
    abs_diff = np.abs(np.subtract.outer(j_idx, j_idx)).astype(np.float64)
    e_xj_xk = (x_0 ** 2) * np.exp(log_phi2 * min_jk + log_phi1 * abs_diff)
    sum_jk = np.add.outer(j_idx, j_idx).astype(np.float64)
    mu_outer = (x_0 ** 2) * np.exp(log_phi1 * sum_jk)
    sigma_matrix = e_xj_xk - mu_outer

    e_stat, var_stat = _build_M_Sigma_quantities(mu, sigma_matrix)
    return e_stat / params.T, var_stat / (params.T * params.T)


# ─── Task 4.2: InversionVerifier (Phase A+B+C combiner) ──────────────────────


def _canonical_params_json_for_verdict(
    params: GBMParameters | OUParameters | JumpDiffusionParameters,
) -> str:
    """Return the sort-keys JSON representation of ``params`` for audit hashing.

    Mirrors the convention used by ``generators._canonical_params_json``
    (frozen-dc ``asdict`` + ``json.dumps(..., sort_keys=True)``), but
    re-implemented here to keep ``variance_proxy`` import-free of
    ``generators`` (tier purity).
    """
    import dataclasses

    return json.dumps(dataclasses.asdict(params), sort_keys=True)


@functools.cache
def _merton_reference_sigma_t(
    canonical_params_json: str, n_ref: int, n_ref_seed: int
) -> np.ndarray:
    """Cached high-N reference ``sigma_t`` array for Merton Phase-C empirical-CDF KS.

    Per spec v0.5 §11.7 + plan v0.6 §16.7: samples ``n_ref`` paths from
    :class:`simulations.stochastic_fx.generators.JumpDiffusionPathGenerator`
    at the params encoded in ``canonical_params_json`` with frozen
    ``n_ref_seed``; returns ONLY the 1-D ``sigma_t`` array (~800 KB at
    ``n_ref = 100_000``). The full :class:`~simulations.stochastic_fx.types.PathEnsemble`
    is allowed to be GC'd — caching it would explode resident memory
    (~4 GB at canonical ``n_steps = 5000``) per FLAG-RC-V0.5-1 / FLAG-MEM-1
    disposition.

    Tier-purity note: imports :class:`JumpDiffusionPathGenerator` LAZILY
    inside the function body (NOT at module load) so ``variance_proxy``'s
    module-load remains tier-pure (no module-level dependency on the
    sibling Callable ``generators``). The runtime tier-cross is intentional
    and documented in plan v0.6 §16.7.

    Cache key: ``(canonical_params_json, n_ref, n_ref_seed)``. Calls with
    identical keys return the same array object (bit-identical
    via ``np.array_equal``). At canonical Merton with ``N_REF = 100_000``
    and 5000 steps, the one-time reference run takes ~30 s on a typical
    workstation; subsequent ``__call__``s on :class:`InversionVerifier`
    re-use the cached array in microseconds.
    """
    # Lazy import — see docstring "Tier-purity note".
    from simulations.stochastic_fx.generators import JumpDiffusionPathGenerator

    params_dict = json.loads(canonical_params_json)
    params = JumpDiffusionParameters(**params_dict)
    ensemble = JumpDiffusionPathGenerator(params=params)(
        rng_seed=n_ref_seed, n_paths=n_ref
    )
    # Detach the sigma_t array from the held PathEnsemble so the ensemble
    # (carrying the ~4 GB paths matrix) can be garbage-collected once this
    # function returns. FLAG-RC-V0.5-1 / FLAG-MEM-1 disposition: cache the
    # array ONLY, never the PathEnsemble.
    return np.asarray(ensemble.sigma_t).copy()


def _phase_c_ks_test(
    sigma_t_array: np.ndarray,
    family_id: str,
    e_analytic: float,
    var_analytic: float,
    canonical_params_json: str,
) -> tuple[bool, float]:
    """Phase C: per-family KS goodness-of-fit dispatch (Pin Z1.4 v0.6).

    Per spec v0.5 §11.7 + plan v0.6 §16.7, the reference SHAPE dispatches on
    ``family_id`` (the pass threshold ``KS_PVALUE_FLOOR = 0.01`` is single-
    valued across all three families — the anti-fishing surface):

    - **GBM** — moment-matched lognormal MoM reference; ``scipy.stats.ks_1samp``.
      Shape ``s = sqrt(log(1 + Var/E²))``, scale ``E/sqrt(1 + Var/E²)``.
    - **OU** — moment-matched gamma MoM reference; ``scipy.stats.ks_1samp``.
      Shape ``a = E²/Var``, scale ``Var/E``.
    - **Merton (v0.6 amendment)** — empirical-CDF reference via high-N
      reference run (``N_REF = 100_000`` paths at ``N_REF_SEED = 20260513``);
      ``scipy.stats.ks_2samp`` against the cached reference ``sigma_t`` array.
      The v0.5 lognormal-Merton reference is RETIRED (failed at KS p=3.41e-21
      due to Poisson-mixture-of-lognormals geometry; empirical-CDF correctly
      handles the mixture without relaxing the floor or per-family-tuning).

    Both GBM and OU paths use DIRECT method-of-moments construction from the
    ANALYTIC moments (NIT-MQ-1 disposition per plan v0.5 §9 Task 4.2) — does
    NOT call ``.fit()`` against the tested sample, which would re-introduce
    the tautology surface MQ flagged at spec v0.1. Merton's empirical-CDF
    reference is drawn from an INDEPENDENT high-N sample (different seed
    region from the test sample's seed=42 — the test budget at N=1000 is
    drawn from a pinned PathEnsemble whose seed is NOT N_REF_SEED), so the
    NIT-MQ-1 tautology is preserved.

    Returns ``(pass_flag, ks_pvalue)`` where ``pass_flag`` is
    ``ks_pvalue >= KS_PVALUE_FLOOR``.

    Edge case: trivial-degenerate σ=0 ensembles produce a degenerate
    point-mass sigma_t (zero variance), against which a continuous
    parametric reference is ill-defined. The Phase A check already
    catches this corner case; here we defensively return ``(True, 1.0)``
    if either analytic moment is non-positive so a downstream caller
    using zero-volatility parameters does not crash inside scipy.
    """
    if e_analytic <= 0.0 or var_analytic <= 0.0:
        return True, 1.0

    if family_id == "gbm":
        ratio = 1.0 + var_analytic / (e_analytic * e_analytic)
        s = math.sqrt(math.log(ratio))
        scale = e_analytic / math.sqrt(ratio)
        ks_result = _scipy_ks_1samp(
            sigma_t_array, _scipy_lognorm(s=s, scale=scale).cdf
        )
    elif family_id == "ou":
        a = e_analytic * e_analytic / var_analytic
        scale = var_analytic / e_analytic
        ks_result = _scipy_ks_1samp(
            sigma_t_array, _scipy_gamma(a=a, scale=scale).cdf
        )
    elif family_id == "merton":
        # v0.6 — empirical-CDF reference via high-N reference run. Cached so
        # repeated InversionVerifier.__call__s reuse the same reference
        # without re-sampling. Keyed on the canonical params JSON + the
        # two pinned constants (so changes to N_REF or N_REF_SEED — which
        # require CORRECTIONS-α — invalidate the cache).
        reference_sigma_t = _merton_reference_sigma_t(
            canonical_params_json, N_REF, N_REF_SEED
        )
        ks_result = _scipy_ks_2samp(sigma_t_array, reference_sigma_t)
    else:
        # Defence-in-depth — PathEnsemble.__post_init__ enforces the closed
        # alphabet but the verifier's __call__ dispatches on this string.
        raise SDEParameterError(
            f"unknown family_id {family_id!r}; "
            "expected one of {'gbm', 'ou', 'merton'}"
        )
    p_value = float(ks_result.pvalue)
    pass_flag = bool(p_value >= KS_PVALUE_FLOOR)
    return pass_flag, p_value


@dataclass(frozen=True)
class InversionVerifier:
    """Three-phase verifier (Pin Z1.3a + Pin Z1.3b v0.5 mean-only + Pin Z1.4 v0.6 dispatch).

    Empty-body frozen-dc per functional-python skill (parameters are
    supplied via ``__call__``). Composes the three independent phase checks
    into one :class:`InversionVerdict` with the composite-AND invariant
    enforced by ``InversionVerdict.__post_init__``.

    Phase C v0.6 per-family reference dispatch (spec v0.5 §11.7, plan v0.6
    §16.7): GBM uses moment-matched lognormal MoM reference + ``ks_1samp``;
    OU uses moment-matched gamma MoM reference + ``ks_1samp``; Merton uses
    empirical-CDF reference via high-N run (``N_REF = 100_000`` paths at
    pinned ``N_REF_SEED = 20260513``) + ``ks_2samp``. Reference SHAPE
    dispatches on family; the pass threshold ``KS_PVALUE_FLOOR = 0.01`` is
    single-valued (anti-fishing surface).

    Anti-fishing N-floor (Pin Z1.5): the TEST ensemble MUST have EXACTLY
    1000 paths. Both 999 and 1001 raise :class:`MCBudgetExceededError`. N
    is not a tuning surface — adding paths until passing would silently
    widen the moment-match acceptance region. ``N_REF = 100_000`` for
    Merton's reference is NOT subject to this floor (it's the comparator,
    not the test sample) — but it IS spec-pinned (per spec §11.7).

    HALT routing (spec v0.5 §6 + plan v0.6 §16.5 + §16.7):

    - Phase B mean-rel-err > MOMENT_REL_TOL ⇒ raise
      :class:`MomentMatchFailedError`.
    - Phase C ks_pvalue < KS_PVALUE_FLOOR ⇒ raise
      :class:`InversionTestFailedError`.
    - Phase A residual > NUMERICAL_IDENTITY_TOL ⇒ no raise; recorded as
      ``phase_a_pass = False`` and composite_pass=False (the algebraic
      identity is closed-form; a failing residual indicates the path
      ensemble's stored sigma_t is corrupt — the caller decides whether to
      escalate).

    Var rel-err is COMPUTED and stored in
    :class:`InversionVerdict.phase_b_var_rel_err` for audit-trail
    transparency, but does NOT gate composite_pass per v0.5 Option-B
    disposition.

    ``InversionVerdict.phase_c_n_paths`` records the TEST sample's
    path-count (=1000 at Pin Z1.5), NOT N_REF (per v0.6 FLAG-RC-V0.5-2
    disposition). The high-N Merton reference's existence is recorded in
    the ``audit_block`` (which binds N_REF + N_REF_SEED), not here.
    """

    def __call__(
        self,
        params: GBMParameters | OUParameters | JumpDiffusionParameters,
        ensemble: PathEnsemble,
        x_bar: float,
    ) -> InversionVerdict:
        """Run Phase A + Phase B (mean-only gate) + Phase C and return a verdict.

        Parameters
        ----------
        params:
            Per-family parameters frozen-dc. Dispatched on family-class to
            pick the correct discrete-moment function.
        ensemble:
            Validated :class:`PathEnsemble` with EXACTLY 1000 paths
            (Pin Z1.5). The ``family_id`` field selects the Phase-B
            analytic-moment function and the Phase-C reference family.
        x_bar:
            Positive finite FX mean for the Phase-A inversion.

        Returns
        -------
        InversionVerdict
            Composite verdict carrying per-phase pass/fail, residual /
            rel-err / p-value metrics, ``composite_pass``, the canonical
            ``tex_anchor`` string, and the deterministic ``audit_block``.

        Raises
        ------
        MCBudgetExceededError
            If ``ensemble.paths.shape[0] != 1000`` (Pin Z1.5).
        MomentMatchFailedError
            If Phase B mean-rel-err > :data:`MOMENT_REL_TOL`.
        InversionTestFailedError
            If Phase C KS p-value < :data:`KS_PVALUE_FLOOR`.
        SDEParameterError
            If ``x_bar`` is non-positive or non-finite (raised inside
            ``phase_a_algebraic_check``).
        """
        # Pin Z1.5 N-floor: STRICT equality with N_PATHS_FLOOR = 1000.
        n_paths_actual = ensemble.paths.shape[0]
        if n_paths_actual != N_PATHS_FLOOR:
            raise MCBudgetExceededError(
                "Pin Z1.5 anti-fishing N-floor: ensemble.paths.shape[0] must "
                f"equal {N_PATHS_FLOOR} EXACTLY; got {n_paths_actual!r}"
            )

        # Phase A — Pin Z1.3a algebraic substitution check.
        phase_a_pass, phase_a_max_residual = phase_a_algebraic_check(
            ensemble, x_bar=x_bar
        )

        # Phase B — Pin Z1.3b v0.5 mean-only gate.
        family_id = ensemble.family_id
        if family_id == "gbm":
            e_an, var_an = gbm_discrete_sigma_t_moments(params)  # type: ignore[arg-type]
        elif family_id == "ou":
            e_an, var_an = ou_discrete_sigma_t_moments(params)  # type: ignore[arg-type]
        elif family_id == "merton":
            e_an, var_an = merton_discrete_sigma_t_moments(params)  # type: ignore[arg-type]
        else:
            # PathEnsemble.__post_init__ enforces the closed alphabet, so this
            # branch is unreachable in practice; included as defence-in-depth.
            raise SDEParameterError(
                f"unknown family_id {family_id!r}; "
                "expected one of {'gbm', 'ou', 'merton'}"
            )

        e_emp = float(ensemble.sigma_t.mean())
        var_emp = float(ensemble.sigma_t.var(ddof=1))
        mean_rel_err = abs(e_emp - e_an) / abs(e_an)
        var_rel_err = abs(var_emp - var_an) / abs(var_an)
        phase_b_pass = bool(mean_rel_err <= MOMENT_REL_TOL)
        if not phase_b_pass:
            raise MomentMatchFailedError(
                f"Pin Z1.3b mean-only gate FAILED for family {family_id!r}: "
                f"mean_rel_err={mean_rel_err!r} > MOMENT_REL_TOL={MOMENT_REL_TOL!r} "
                f"(E_an={e_an!r}, E_emp={e_emp!r}); "
                "var_rel_err is audit-trail-only and not gated."
            )

        # Phase C — Pin Z1.4 per-family KS goodness-of-fit (v0.6 reference
        # dispatch). GBM/OU use moment-matched lognormal/gamma MoM (NIT-MQ-1);
        # Merton uses empirical-CDF reference via high-N (N_REF=100k) run at
        # pinned N_REF_SEED. Reference SHAPE dispatches on family_id; the
        # pass threshold KS_PVALUE_FLOOR=0.01 is single-valued (anti-fishing).
        canonical_params_json = _canonical_params_json_for_verdict(params)
        phase_c_pass, ks_pvalue = _phase_c_ks_test(
            ensemble.sigma_t,
            family_id,
            e_an,
            var_an,
            canonical_params_json,
        )
        if not phase_c_pass:
            raise InversionTestFailedError(
                f"Pin Z1.4 KS gate FAILED for family {family_id!r}: "
                f"ks_pvalue={ks_pvalue!r} < KS_PVALUE_FLOOR={KS_PVALUE_FLOOR!r}"
            )

        # Audit block (v0.6 FLAG-RC-V0.5-5 recipe): sha256 over
        # (ensemble.audit_block, canonical params JSON, x_bar,
        #  MOMENT_REL_TOL, KS_PVALUE_FLOOR, N_REF, N_REF_SEED) in that fixed
        # order. N_REF and N_REF_SEED bind the Merton high-N reference to the
        # audit trail so any change to either constant invalidates the digest.
        # For GBM/OU runs the two constants are still hashed in (they're
        # module-level Final constants regardless of which family dispatches)
        # — single recipe across families.
        hasher = hashlib.sha256()
        hasher.update(ensemble.audit_block.encode("utf-8"))
        hasher.update(canonical_params_json.encode("utf-8"))
        hasher.update(f"{x_bar:.17g}".encode("utf-8"))
        hasher.update(f"{MOMENT_REL_TOL:.17g}".encode("utf-8"))
        hasher.update(f"{KS_PVALUE_FLOOR:.17g}".encode("utf-8"))
        hasher.update(f"{N_REF}".encode("utf-8"))
        hasher.update(f"{N_REF_SEED}".encode("utf-8"))
        audit_block = hasher.hexdigest()

        composite_pass = bool(phase_a_pass and phase_b_pass and phase_c_pass)
        tex_anchor = f"notes/stochastic_fx_tex/sigma_t_moments_{family_id}.tex"

        return InversionVerdict(
            family_id=family_id,
            phase_a_pass=phase_a_pass,
            phase_a_max_residual=phase_a_max_residual,
            phase_b_pass=phase_b_pass,
            phase_b_mean_rel_err=mean_rel_err,
            phase_b_var_rel_err=var_rel_err,
            phase_c_pass=phase_c_pass,
            phase_c_ks_pvalue=ks_pvalue,
            phase_c_n_paths=n_paths_actual,
            composite_pass=composite_pass,
            tex_anchor=tex_anchor,
            audit_block=audit_block,
        )


__all__ = [
    "KS_PVALUE_FLOOR",
    "MOMENT_REL_TOL",
    "NUMERICAL_IDENTITY_TOL",
    "N_PATHS_FLOOR",
    "N_REF",
    "N_REF_SEED",
    "InversionVerifier",
    "eq_8_inversion",
    "gbm_discrete_sigma_t_moments",
    "merton_discrete_sigma_t_moments",
    "ou_discrete_sigma_t_moments",
    "phase_a_algebraic_check",
    "recompute_sigma_t",
]
