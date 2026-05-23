"""Task 4.2 b1 derivation — analytic moments of the DISCRETE eq.(7) σ_T statistic.

This script is the offline derivation artefact backing
``simulations/stochastic_fx/variance_proxy.py``'s three new free functions
``gbm_discrete_sigma_t_moments`` / ``ou_discrete_sigma_t_moments`` /
``merton_discrete_sigma_t_moments`` per plan v0.4 §16.4 disposition (b1).

NOT imported by the runtime package. Reviewers may re-run it to cross-check
the discrete-statistic analytic forms.

Notation
--------
Path indices j, k ∈ {0, 1, ..., n} with n = ``n_steps``. Number of timepoints
N = n + 1. Time grid t_j = j·dt where dt = T/n. Per-path statistic per spec
v0.3 §6 eq. (7):

    σ_T = (1/T) · Σ_{j=0..n} (X_j − X̄)²,   X̄ = (1/N) Σ_j X_j.

Identity used throughout: Σ_j (X_j − X̄)² = X^T M X with M = I − (1/N) 1·1^T
(centering projection, symmetric idempotent, rank n).

Per family, write μ_j = E[X_j], Σ_jk = Cov(X_j, X_k). Then for Y = X − μ:

    E[X^T M X] = tr(M Σ) + μ^T M μ

    Var(X^T M X) = 2 tr((M Σ)²) + 4 (M μ)^T Σ (M μ)         (*)

(*) is EXACT under joint-Gaussianity of X. For GBM and Merton (X lognormal /
lognormal-mixture, NOT Gaussian) it is a leading-order approximation valid
when σ²T is small (canonical: σ²T ≈ 0.01 for GBM, ≈ 0.0025 + jump-vol ≈
0.0025+0.12 for Merton — both well within the regime where lognormal-vs-
Gaussian-quadratic-form discrepancy is below the 5% Pin Z1.3b tolerance).

Per-family log-step characteristics (X_j = x_0 · ∏_{ℓ≤j} e^{L_ℓ} for the
log-multiplicative families GBM and Merton):

  GBM:    L ~ N(−σ²/2·dt, σ²·dt) ⇒ φ₁ := E[e^L] = 1 (martingale),
                                    φ₂ := E[e^{2L}] = e^{σ²·dt}.
  Merton: L = L_diff + L_jump, independent.
          L_diff ~ N(−σ²/2·dt, σ²·dt) (with μ=0, jump_mean=0 canonical pins).
          L_jump | N_jumps = √N · σ_J · Z' with N_jumps ~ Poisson(λ·dt).
          E[e^{α·L_jump}] = E[exp(α²·N_jumps·σ_J²/2)] (Gaussian MGF inside)
                          = exp(λ·dt·(exp(α²·σ_J²/2) − 1))   (Poisson PGF).
          So φ₁ = E[e^L] = 1 · exp(λ·dt·(exp(σ_J²/2) − 1)) (with μ_J = 0).
             φ₂ = E[e^{2L}] = e^{σ²·dt} · exp(λ·dt·(exp(2σ_J²) − 1)).
  OU:     X is Gaussian, NOT log-multiplicative; treated directly via
          E[X_j] = mu_bar + (x_0 − mu_bar)·e^{−θ·t_j},
          Cov(X_j, X_k) = σ²·e^{−θ·|t_j−t_k|}·(1 − e^{−2θ·min(t_j,t_k)})/(2θ).

For X_j = x_0 · ∏ e^{L_ℓ} (GBM/Merton):
  μ_j = E[X_j] = x_0 · φ₁^j
  E[X_j²] = x_0² · φ₂^j
  E[X_j X_k] = x_0² · φ₂^{min(j,k)} · φ₁^{|k−j|}     (j ≤ k branch + symmetry)
  Cov(X_j, X_k) = x_0² · φ₁^{|k−j|} · (φ₂^{min(j,k)} − φ₁^{2·min(j,k)})

Closed-form quantities used in the moment formulas (M = I − (1/N)·1·1^T):

  tr(M Σ) = Σ_j Σ_jj − (1/N) Σ_{j,k} Σ_jk
  μ^T M μ = Σ_j μ_j² − (1/N) (Σ_j μ_j)²
  tr((M Σ)²) = tr(Σ²) − (2/N) ||Σ·1||² + (1/N²) (1^T·Σ·1)²
  (M μ)^T Σ (M μ): vector quadratic, computed numerically.

For OU, μ^T M μ = 0 at canonical pin (X_0 = mu_bar exactly).
For GBM with μ=0, μ_j ≡ x_0 (martingale), so μ^T M μ = 0.

This script computes both E[σ_T] and Var[σ_T] discrete-analytic numerically
at canonical pins, and compares to Monte Carlo at N_paths = 1000, fixed seed.
The relative errors must be below MOMENT_REL_TOL = 0.05 to satisfy Pin Z1.3b.
"""
from __future__ import annotations

import math

import numpy as np

from simulations.stochastic_fx import (
    CANONICAL_GBM,
    CANONICAL_MERTON,
    CANONICAL_OU,
    GBMPathGenerator,
    JumpDiffusionPathGenerator,
    OUPathGenerator,
)
from simulations.stochastic_fx.types import (
    GBMParameters,
    JumpDiffusionParameters,
    OUParameters,
)


def _build_M_Sigma_quantities(
    mu: np.ndarray, sigma_matrix: np.ndarray
) -> tuple[float, float]:
    """Return ``(E_statistic, Var_statistic)`` for the discrete σ_T·T statistic.

    The statistic is ``Σ_j (X_j − X̄)²`` BEFORE the 1/T normalization. The
    caller divides by T (mean) or T² (variance).

    Uses M = I − (1/N) 1·1^T (centering projection) and the closed-form
    trace identities. Var formula is the Gaussian-quadratic-form leading
    order (exact for OU; valid for GBM/Merton at small σ²T per derivation
    docstring).
    """
    N = sigma_matrix.shape[0]
    diag_sigma = float(np.trace(sigma_matrix))
    sum_sigma = float(np.sum(sigma_matrix))
    row_sums = sigma_matrix.sum(axis=1)
    row_sum_sq = float(np.dot(row_sums, row_sums))
    frob_sq = float(np.sum(sigma_matrix * sigma_matrix))

    tr_M_Sigma = diag_sigma - sum_sigma / N
    tr_MSigma_sq = frob_sq - 2.0 * row_sum_sq / N + sum_sigma * sum_sigma / (N * N)

    # μ^T M μ = ||μ||² − (Σ μ)² / N
    sum_mu = float(mu.sum())
    norm_mu_sq = float(np.dot(mu, mu))
    mu_M_mu = norm_mu_sq - sum_mu * sum_mu / N

    # M μ = μ − (1·μ̄)·1; (Mμ)^T Σ (Mμ)
    m_mu = mu - sum_mu / N
    sigma_m_mu = sigma_matrix @ m_mu
    quad_term = float(np.dot(m_mu, sigma_m_mu))

    e_stat = tr_M_Sigma + mu_M_mu
    var_stat = 2.0 * tr_MSigma_sq + 4.0 * quad_term
    return e_stat, var_stat


def gbm_discrete_moments(params: GBMParameters) -> tuple[float, float]:
    """Discrete σ_T moments for GBM at canonical grid (E, Var)."""
    n_steps = params.n_steps
    N = n_steps + 1
    dt = params.T / n_steps
    sigma2_dt = params.sigma * params.sigma * dt
    # phi_1 = 1 (martingale, mu=0); phi_2 = exp(σ²·dt)
    log_phi2 = sigma2_dt
    # log E[X_j²] = j · log φ₂; E[X_j²] = x_0² · φ₂^j
    # Cov(X_j, X_k) = x_0² · (φ₂^min(j,k) − 1)
    j_idx = np.arange(N)
    # E[X_j] = x_0
    mu = np.full(N, params.x_0, dtype=np.float64)
    # Build covariance matrix Σ_jk = x_0² · (exp(σ²·dt·min(j,k)) − 1)
    min_jk = np.minimum.outer(j_idx, j_idx).astype(np.float64)
    # Use expm1 for numerical stability at small σ²·dt.
    sigma_matrix = (params.x_0 ** 2) * np.expm1(log_phi2 * min_jk)
    e_stat, var_stat = _build_M_Sigma_quantities(mu, sigma_matrix)
    return e_stat / params.T, var_stat / (params.T * params.T)


def ou_discrete_moments(params: OUParameters) -> tuple[float, float]:
    """Discrete σ_T moments for OU at canonical grid (E, Var) — EXACT Gaussian."""
    n_steps = params.n_steps
    N = n_steps + 1
    dt = params.T / n_steps
    theta = params.theta
    sigma = params.sigma
    mu_bar = params.mu_bar
    x_0 = params.x_0

    j_idx = np.arange(N)
    t = j_idx * dt
    # E[X_t] = mu_bar + (x_0 − mu_bar)·e^{−θ·t}
    mu = mu_bar + (x_0 - mu_bar) * np.exp(-theta * t)

    # Var[X_t] = σ²/(2θ) · (1 − e^{−2θ·t})
    var_x = (sigma ** 2 / (2.0 * theta)) * (1.0 - np.exp(-2.0 * theta * t))
    # Cov(X_s, X_t) = σ²·e^{−θ·|t−s|}·(1 − e^{−2θ·min(s,t)})/(2θ)
    min_t = np.minimum.outer(t, t)
    abs_diff_t = np.abs(np.subtract.outer(t, t))
    sigma_matrix = (sigma ** 2 / (2.0 * theta)) * np.exp(-theta * abs_diff_t) * (
        1.0 - np.exp(-2.0 * theta * min_t)
    )
    # Diagonal sanity: Σ_jj should equal var_x. (Difference is 0 by construction.)
    e_stat, var_stat = _build_M_Sigma_quantities(mu, sigma_matrix)
    return e_stat / params.T, var_stat / (params.T * params.T)


def merton_discrete_moments(
    params: JumpDiffusionParameters,
) -> tuple[float, float]:
    """Discrete σ_T moments for Merton at canonical grid (E, Var)."""
    n_steps = params.n_steps
    N = n_steps + 1
    dt = params.T / n_steps
    sigma = params.sigma
    lambda_jump = params.lambda_jump
    mu_J = params.jump_mean
    sigma_J2 = params.jump_std ** 2
    x_0 = params.x_0

    # log φ₁ = (μ - σ²/2)·dt + μ_J·λ·dt·(...) — combine diffusion+jump moment GFs.
    # E[e^L] = E[e^{L_diff}] · E[e^{L_jump}].
    # E[e^{L_diff}] = exp(μ·dt) for our log_diff = (μ − σ²/2)·dt + σ√dt·Z:
    # actually E[e^{(μ−σ²/2)·dt + σ√dt·Z}] = exp((μ−σ²/2)·dt + σ²·dt/2) = exp(μ·dt)
    # E[e^{L_jump}] : with L_jump | N = N·μ_J + √N·σ_J·Z',
    #   E[e^{N·μ_J + √N·σ_J·Z'} | N] = exp(N·μ_J + N·σ_J²/2)
    #   E[exp(N·(μ_J + σ_J²/2))] = exp(λ·dt·(exp(μ_J + σ_J²/2) − 1))     (Poisson PGF)
    # So log φ₁ = μ·dt + λ·dt·(exp(μ_J + σ_J²/2) − 1).
    log_phi1 = params.mu * dt + lambda_jump * dt * (math.exp(mu_J + sigma_J2 / 2.0) - 1.0)
    # E[e^{2L_diff}] = exp(2μ·dt + σ²·dt) (apply MGF at θ=2).
    # E[e^{2L_jump}]: E[e^{2N·μ_J + 2√N·σ_J·Z'} | N] = exp(2N·μ_J + 2N·σ_J²)
    #               = exp(N·(2μ_J + 2σ_J²)); MGF over N gives
    #               exp(λ·dt·(exp(2μ_J + 2σ_J²) − 1)).
    log_phi2 = (
        2.0 * params.mu * dt + sigma ** 2 * dt
        + lambda_jump * dt * (math.exp(2.0 * mu_J + 2.0 * sigma_J2) - 1.0)
    )
    j_idx = np.arange(N)
    # μ_j = x_0 · exp(j · log φ₁)
    mu = x_0 * np.exp(j_idx * log_phi1)
    # E[X_j²] = x_0² · exp(j · log φ₂)
    # E[X_j X_k] = x_0² · exp(min(j,k) · log φ₂ + |k-j| · log φ₁)
    min_jk = np.minimum.outer(j_idx, j_idx).astype(np.float64)
    abs_diff = np.abs(np.subtract.outer(j_idx, j_idx)).astype(np.float64)
    e_xj_xk = (x_0 ** 2) * np.exp(log_phi2 * min_jk + log_phi1 * abs_diff)
    # μ_j · μ_k = x_0² · exp((j+k) · log φ₁)
    sum_jk = np.add.outer(j_idx, j_idx).astype(np.float64)
    mu_outer = (x_0 ** 2) * np.exp(log_phi1 * sum_jk)
    sigma_matrix = e_xj_xk - mu_outer

    e_stat, var_stat = _build_M_Sigma_quantities(mu, sigma_matrix)
    return e_stat / params.T, var_stat / (params.T * params.T)


def _run_one(family: str, gen, canonical, moments_fn) -> None:
    ens = gen(rng_seed=42, n_paths=1000)
    e_an, v_an = moments_fn(canonical)
    e_emp = float(ens.sigma_t.mean())
    v_emp = float(ens.sigma_t.var(ddof=1))
    err_e = abs(e_emp - e_an) / abs(e_an) if e_an != 0.0 else float("nan")
    err_v = abs(v_emp - v_an) / abs(v_an) if v_an != 0.0 else float("nan")
    print(f"=== {family.upper()} ===")
    print(f"  E_an  = {e_an: .6e}   E_emp  = {e_emp: .6e}   rel_err = {err_e:.4%}")
    print(f"  V_an  = {v_an: .6e}   V_emp  = {v_emp: .6e}   rel_err = {err_v:.4%}")


if __name__ == "__main__":
    _run_one("gbm", GBMPathGenerator(params=CANONICAL_GBM), CANONICAL_GBM, gbm_discrete_moments)
    _run_one("ou", OUPathGenerator(params=CANONICAL_OU), CANONICAL_OU, ou_discrete_moments)
    _run_one(
        "merton",
        JumpDiffusionPathGenerator(params=CANONICAL_MERTON),
        CANONICAL_MERTON,
        merton_discrete_moments,
    )
