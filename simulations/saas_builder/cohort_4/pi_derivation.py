r"""Symbolic π(t) derivation per Pin M1 (plan v0.3 §Phase-2 prelude).

CORRECTIONS-α v0.2 → v0.3 (anti-fishing remediation, MQ-BLOCK 1+2 fix):

The v0.2 implementation injected a spurious ``1/κ`` coupling factor into
π(t) post-hoc to satisfy plan-§M2's ``∂|π|/∂κ < 0`` expectation. This
was an anti-fishing violation per
``feedback_pathological_halt_anti_fishing_checkpoint``: a multiplicative
factor introduced for the purpose of preserving a sign target has no
anchor in PRIMITIVES.md / saas-note §4.1.

The honest derivation chain (PRIMITIVES.md §6 → §8.1 → §10 → §15) does
NOT couple κ to π(t); κ enters Z **only** through the spec §5.1 (T2)
``q_t^USD = p̄_sub + p_t · softplus_β(τ_t − κ)`` channel, which is
already C2-marginalized into the C1 posterior-predictive ``q_t^cop``
draws consumed by ``z_cap.PerDrawZEvaluator``. Re-injecting κ into π
double-counts.

Honest M1 chain (no κ in π):

- **Step 1 — Pitch identity** (saas note §4.1 + spec §4.1).
  Z = inf{z ∈ ℝ₊ : E[q_t^USD / (X/Y)_t + π(t)] ≤ z}. κ enters via
  ``q_t^USD`` only.
- **Step 2 — Perpetual-horizon premium identity**
  (PRIMITIVES.md §15 open item 4 + §9 streamed variant).
  ``π(t) · dt ↔ dΠ/dt · dt``.
- **Step 3 — Closed-form Π** (PRIMITIVES.md §8.1).
  ``Π(σ_T) = K⋆ · √σ_T`` at equilibrium ``K_s = K_l = K⋆``.
- **Step 4 — Carr-Madan linearization** (PRIMITIVES.md (16)–(19)).
  Around pinned ``σ₀``: ``Π(σ_T) ≈ K⋆√σ₀ + K̂·(σ_T − σ₀)``,
  ``K̂ ≡ K⋆/(2√σ₀)``.
- **Step 5 — Variance proxy along deterministic FX path** (PRIMITIVES.md
  §6 + §7). With ``(X/Y)_t = (1 + ε·(cos²(ωt) − 1/2))·X̄/Ȳ``::

      σ_T(t) = (X̄/Ȳ)² · ε² · [1/8 + sin(4ωt)/(32ωt)]

  The ``(X̄/Ȳ)²`` prefactor is RESTORED (was silently dropped in v0.2;
  MQ-FLAG-1).

Closed form::

    π(t; K⋆, σ₀, ε, ω, t, X̄/Ȳ) =
        K⋆ · ε² · (X̄/Ȳ)² · (4ωt cos(4ωt) − sin(4ωt))
        / (64 · ω · √σ₀ · t²)

**Free symbols (canonical 6-tuple):**
``{K_star, sigma_0, epsilon, omega, t, xy_bar}``. Note: κ is NOT a free
symbol of π (it enters Z only through q_t^USD). ``xy_bar`` replaces
the v0.2 ``kappa`` slot in the 6-tuple. Plan v0.3 §M2 monotonicity is
re-pinned to ``∂|π|/∂(X̄/Ȳ) > 0`` (strict; π ∝ (X̄/Ȳ)²).

NO IO. NO mutable state.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import sympy as sp

from simulations.saas_builder.cohort_4.types import (
    PI_T_CANONICAL_SYMBOLS,
    PiTSymbolic,
)

# ─── Free functions: per-step symbolic builders ──────────────────────────────


def _step_5a_variance_proxy_symbolic() -> tuple[
    sp.Expr, sp.Symbol, sp.Symbol, sp.Symbol, sp.Symbol
]:
    r"""Return σ_T(t) closed form per Pin M1 Step 5 (HONEST — with (X̄/Ȳ)²).

    Substitution chain (PRIMITIVES.md §6 + §7):

    - FX path: ``(X/Y)_s = (1 + ε·(cos²(ωs) − 1/2))·X̄/Ȳ``;
    - Squared deviation: ``((X/Y)_s − X̄/Ȳ)² = (X̄/Ȳ)²·ε²·(cos²(ωs) − 1/2)²``;
    - Time-averaged via ``cos²(ωs) − 1/2 = cos(2ωs)/2`` →
      ``(cos² − 1/2)² = (1 + cos(4ωs))/8``;
    - Integrate analytically:
      ``(1/t)·∫₀ᵗ (X̄/Ȳ)²·ε²·(1 + cos(4ωs))/8 ds
        = (X̄/Ȳ)²·ε²·[1/8 + sin(4ωt)/(32ωt)]``.

    The ``(X̄/Ȳ)²`` prefactor is preserved verbatim (CORRECTIONS-α v0.3
    fix for MQ-FLAG-1; v0.2 silently dropped it).

    Returns the symbolic σ_T(t) Expr along with the (t, omega, epsilon,
    xy_bar) Symbols for downstream use.
    """
    t = sp.symbols("t", positive=True)
    omega = sp.symbols("omega", positive=True)
    eps = sp.symbols("epsilon", positive=True)
    xy_bar = sp.symbols("xy_bar", positive=True)
    sigma_T_t = (
        xy_bar**2
        * eps**2
        * (sp.Rational(1, 8) + sp.sin(4 * omega * t) / (32 * omega * t))
    )
    return sigma_T_t, t, omega, eps, xy_bar


def _step_5b_d_sigma_d_t(sigma_T_t: sp.Expr, t: sp.Symbol) -> sp.Expr:
    """Return dσ_T/dt per Pin M1 Step 5 closing.

    Exact symbolic derivative of the closed-form σ_T(t); consumed by
    Step 4 Carr-Madan ``π(t) = K̂ · dσ_T/dt``.
    """
    return sp.diff(sigma_T_t, t)


def _step_4_carr_madan_K_hat() -> tuple[sp.Expr, sp.Symbol, sp.Symbol]:
    r"""Return K̂ = K⋆/(2√σ₀) per Pin M1 Step 4 (Carr-Madan).

    PRIMITIVES.md §10 (16)–(19): linearize Π(σ_T) = K⋆√σ_T around σ₀ to
    obtain ``Π ≈ K⋆√σ₀ + K̂·(σ_T − σ₀)`` with ``K̂ ≡ K⋆/(2√σ₀)``.
    """
    K_star = sp.symbols("K_star", positive=True)
    sigma_0 = sp.symbols("sigma_0", positive=True)
    K_hat = K_star / (2 * sp.sqrt(sigma_0))
    return K_hat, K_star, sigma_0


def derive_pi_t_symbolic() -> PiTSymbolic:
    r"""Build the closed-form π(t) per Pin M1 Steps 1–5 (plan v0.3 honest).

    Returned ``PiTSymbolic`` carries the closed form::

        π(t) = (K⋆ / (2·√σ₀)) · dσ_T/dt
             = K⋆·ε²·(X̄/Ȳ)²·(4ωt·cos(4ωt) − sin(4ωt))
               / (64·ω·√σ₀·t²)

    with σ_T(t) = (X̄/Ȳ)²·ε²·[1/8 + sin(4ωt)/(32ωt)] (PRIMITIVES.md §6).

    **Anti-fishing trace.** Every step of this chain is reproduced
    verbatim from PRIMITIVES.md / saas-note. NO ad-hoc multiplicative
    factor is introduced for sign-cert convenience — the v0.2 ``1/κ``
    coupling has been REMOVED (CORRECTIONS-α v0.3, MQ-BLOCK-1 fix).

    Free symbols: {K_star, sigma_0, epsilon, omega, t, xy_bar}.
    Note κ ∉ free_symbols; κ enters Z only via q_t^USD (spec §5.1 T2).

    Returns:
        Frozen PiTSymbolic carrying the symbolic π(t) Expr and a
        numpy-broadcasting lambdified evaluator with positional
        signature ``(K_star, sigma_0, epsilon, omega, t, xy_bar)``.

    Raises:
        ValueError: propagates from PiTSymbolic.__post_init__ if the
            constructed Expr's free-symbol set drifts from
            PI_T_CANONICAL_SYMBOLS.
    """
    sigma_T_t, t, omega, eps, xy_bar = _step_5a_variance_proxy_symbolic()
    d_sigma_dt = _step_5b_d_sigma_d_t(sigma_T_t, t)
    K_hat, K_star, sigma_0 = _step_4_carr_madan_K_hat()

    # Step 2 — perpetual-horizon premium identity:
    # π(t) = dΠ/dt = K̂ · dσ_T/dt. NO κ-coupling (v0.3 honest).
    pi_t_expr = K_hat * d_sigma_dt
    pi_t_simplified = sp.simplify(pi_t_expr)

    canonical = set(PI_T_CANONICAL_SYMBOLS)
    free_names = frozenset(str(s) for s in pi_t_simplified.free_symbols)
    if not free_names.issubset(canonical):
        raise ValueError(
            f"derive_pi_t_symbolic: free_symbols {sorted(free_names)}"
            f" must be a subset of {sorted(canonical)}"
        )

    # Lambdify with canonical positional signature
    # (K_star, sigma_0, epsilon, omega, t, xy_bar) — κ removed in v0.3.
    syms_in_order = (K_star, sigma_0, eps, omega, t, xy_bar)
    lam = sp.lambdify(syms_in_order, pi_t_simplified, modules="numpy")

    def _lambdified_wrapper(
        K_star_v: float | np.ndarray,
        sigma_0_v: float | np.ndarray,
        epsilon_v: float | np.ndarray,
        omega_v: float | np.ndarray,
        t_v: float | np.ndarray,
        xy_bar_v: float | np.ndarray,
    ) -> np.ndarray:
        out = lam(K_star_v, sigma_0_v, epsilon_v, omega_v, t_v, xy_bar_v)
        return np.asarray(out, dtype=np.float64)

    return PiTSymbolic(
        expr=pi_t_simplified,
        lambdified=_lambdified_wrapper,
        free_symbols=free_names,
        primitives_anchor=(
            "PRIMITIVES.md §6 (FX path) → §8.1 (Π = K⋆√σ_T) →"
            " §10 (16)–(19) Carr-Madan → §7 variance proxy →"
            " §15 open item 4 (perpetual π·dt ↔ dΠ/dt). NO κ-coupling"
            " (v0.3 anti-fishing fix)."
        ),
        saas_note_anchor=(
            "notes/SaaS_Builders_AI_NativeBuilders.md §4.1 pitch formula"
            " (premium-funded ratchet); κ enters Z via q_t^USD softplus,"
            " NOT via π(t)."
        ),
    )


# ─── Identity-tolerance check (Pin M2) ───────────────────────────────────────


@dataclass(frozen=True)
class IdentityResidualEvaluator:
    """Evaluate the perpetual-identity residual π(t) ↔ dΠ/dt.

    Pin M2 inheritance (CORRECTIONS-α v0.3, MQ-BLOCK-2 fix):

    - The v0.2 ``Pi_grid /= κ`` rescaling created a tautological identity
      check (any common multiplier f(κ) on both π and Π passes the
      discrete diff test). Removed.
    - The honest test verifies π(t) = dΠ_lin/dt for the Carr-Madan-
      linearized Π = K⋆√σ₀ + K̂·(σ_T − σ₀), which by construction is
      satisfied symbolically *exactly* — sympy ``simplify(π − dΠ/dt)``
      returns 0 identically. The residual is therefore purely the
      finite-difference / discretization error of the trapezoid rule
      vs the analytic derivative.
    - Symbolic tolerance ≤ ``1e-10 · N_legs`` per PRIMITIVES.md §12 ledger
      (sympy zero check; trivially satisfied).
    - Numerical tolerance ≤ ``1e-6`` per Path A v0 §10.4 reconciliation
      under finite-t discretization. We assert this against an *exact-
      symbolic* gauge: the maximum finite-difference error of the
      trapezoid rule applied to π·dt vs the true ΔΠ_lin (computed from
      the symbolic closed form, not from a re-discretization).
    """

    #: Identity-test discretization grid size.
    #:
    #: CORRECTIONS-α v0.3 (MQ-BLOCK-2 fix): the v0.2 default of 12 (matching
    #: spec §2 monthly grain) violates Nyquist for the σ_T(t) ∝ sin(4ωt)
    #: closed form at ω=1 (Nyquist Δt < π/(4ω) ≈ 0.785). The identity test
    #: is a numerical-approximation gauge of π(t) ≡ dΠ_lin/dt (which holds
    #: SYMBOLICALLY exactly — see ``assert_perpetual_identity_symbolic``).
    #: 5000 points on t ∈ [0.5, 12] gives Δt ≈ 2.3e-3 month, residual ≈
    #: 1e-8 < NUMERICAL_IDENTITY_TOL. The grid size is a free parameter
    #: of the test; not a tolerance widening (anti-fishing-clean).
    n_t_grid: int = 5000

    def __post_init__(self) -> None:
        if self.n_t_grid < 2:
            raise ValueError(
                f"IdentityResidualEvaluator.n_t_grid = {self.n_t_grid}"
                " must be ≥ 2 (need at least 2 time points for finite differences)"
            )

    def __call__(
        self,
        pi_t: PiTSymbolic,
        K_star: float,
        sigma_0: float,
        epsilon: float,
        omega: float,
        xy_bar: float,
        t_lo: float = 0.5,
        t_hi: float = 12.0,
    ) -> float:
        r"""Return the maximum perpetual-identity residual on the grid.

        Evaluates ``|π(t)·Δt − ΔΠ_lin| / |Π_lin|`` over the grid where
        Π_lin = K⋆√σ₀ + K̂·(σ_T − σ₀) is the Carr-Madan-linearized payoff.
        The trapezoid-rule midpoint approximation introduces O(Δt²) error,
        bounded by NUMERICAL_IDENTITY_TOL = 1e-6 at the saas-cohort
        monthly grain.

        Args:
            pi_t: PiTSymbolic Value carrying the lambdified π(t).
            K_star, sigma_0, epsilon, omega, xy_bar: scalar substitutions
                (note κ is NOT a parameter of π in v0.3 honest derivation).
            t_lo, t_hi: time grid endpoints (months).

        Returns:
            Maximum relative identity residual (dimensionless float ≥ 0).

        Raises:
            ValueError: if t_lo ≤ 0 (σ_T(t) has 1/t factor) or
                t_hi ≤ t_lo, or if σ_T(t) ≤ 0 on the grid.
        """
        if not (t_lo > 0.0):
            raise ValueError(
                f"IdentityResidualEvaluator: t_lo = {t_lo} must be > 0"
                " (σ_T(t) closed form has 1/t factor)"
            )
        if not (t_hi > t_lo):
            raise ValueError(
                f"IdentityResidualEvaluator: t_hi ({t_hi}) must exceed"
                f" t_lo ({t_lo})"
            )
        t_grid = np.linspace(t_lo, t_hi, self.n_t_grid, dtype=np.float64)
        # σ_T(t) closed form WITH (X̄/Ȳ)² prefactor (CORRECTIONS-α v0.3).
        sigma_T_grid = (
            xy_bar**2
            * epsilon**2
            * (
                1.0 / 8.0
                + np.sin(4.0 * omega * t_grid) / (32.0 * omega * t_grid)
            )
        )
        if not np.all(sigma_T_grid > 0.0):
            raise ValueError(
                "IdentityResidualEvaluator: σ_T(t) ≤ 0 on the time grid;"
                " (X/Y)-amplitude ε too small or grid spans a zero-crossing"
            )
        # Carr-Madan-linearized Π for identity check (NO /κ rescaling
        # — CORRECTIONS-α v0.3 MQ-BLOCK-2 fix).
        Pi_grid = K_star * np.sqrt(sigma_0) + (
            K_star / (2.0 * np.sqrt(sigma_0))
        ) * (sigma_T_grid - sigma_0)
        pi_grid = pi_t.lambdified(
            K_star, sigma_0, epsilon, omega, t_grid, xy_bar
        )
        d_t = np.diff(t_grid)
        pi_mid = 0.5 * (pi_grid[:-1] + pi_grid[1:])
        d_Pi = np.diff(Pi_grid)
        residuals = np.abs(pi_mid * d_t - d_Pi) / np.maximum(
            np.abs(Pi_grid[:-1]), 1e-300
        )
        return float(np.max(residuals))


def assert_perpetual_identity_symbolic(pi_t: PiTSymbolic) -> None:
    r"""Assert symbolic π(t) − dΠ_lin/dt ≡ 0 (sympy exact zero).

    The non-tautological identity test (CORRECTIONS-α v0.3, MQ-BLOCK-2):
    rebuild Π_lin from the canonical Carr-Madan formula and assert that
    ``simplify(π − dΠ/dt)`` returns sympy.S.Zero. This catches any drift
    in the Step 1–5 chain symbolically, not numerically.

    Raises:
        ValueError: if the residual does not symbolically reduce to 0.
    """
    t = sp.symbols("t", positive=True)
    omega = sp.symbols("omega", positive=True)
    eps = sp.symbols("epsilon", positive=True)
    xy_bar = sp.symbols("xy_bar", positive=True)
    K_star = sp.symbols("K_star", positive=True)
    sigma_0 = sp.symbols("sigma_0", positive=True)
    sigma_T = (
        xy_bar**2
        * eps**2
        * (sp.Rational(1, 8) + sp.sin(4 * omega * t) / (32 * omega * t))
    )
    Pi_lin = K_star * sp.sqrt(sigma_0) + (
        K_star / (2 * sp.sqrt(sigma_0))
    ) * (sigma_T - sigma_0)
    dPi_dt = sp.diff(Pi_lin, t)
    residual = sp.simplify(pi_t.expr - dPi_dt)
    if residual != 0:
        raise ValueError(
            "Perpetual-identity symbolic check failed:"
            f" simplify(π − dΠ_lin/dt) = {residual}, expected 0."
            " (CORRECTIONS-α v0.3 MQ-BLOCK-2 non-tautological gate)"
        )


__all__ = [
    "IdentityResidualEvaluator",
    "assert_perpetual_identity_symbolic",
    "derive_pi_t_symbolic",
]
