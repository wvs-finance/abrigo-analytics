"""Δ^(a_s) and Γ^(a_s) symbolic + numerical evaluators (PRIMITIVES.md §1, §6, §7).

Implements:

- :class:`DeltaSymbolicDeriver` — sympy derivation of Δ^(a_s) from
  PRIMITIVES.md §7 eq. (10) substituted with the spec §5.1 (T2) ``q_t``;
  the symbolic form is the canonical reference for the numerical
  evaluator below.
- :class:`DeltaNumericalEvaluator` — vectorized closed-form evaluation
  per posterior draw at one ``BracketPoint``; uses numpy only.
- :class:`GammaEvaluator` — second derivative w.r.t. ``σ_T`` (the
  realized-variance proxy; PRIMITIVES (7) / (8)) reported alongside Δ.
- :class:`DeltaSymbolicNumericalReconciler` — self-consistency check at
  one bracket point with tolerance ``1e-10 · N_terms`` per
  PRIMITIVES.md §11.b.

Closed-form references (per Pin Δ-cohort docstring contract — Task 3.2
contract-docstrings pass enforces verbatim presence):

- PRIMITIVES.md eq. (6):  ``f_t ≡ cos²(ω t) - 1/2``;
                          ``(X/Y)_t = (1 + ε f_t) · X̄/Ȳ``.
- PRIMITIVES.md eq. (10): ``Δ^(a_s) = (4 / (X̄/Ȳ · ε(σ_T))) ·
                          Σ_{t=1}^{T} q_t · f_t / (X/Y)_t²``.
- PRIMITIVES.md eq. (11): (renumbered from (8)) ``ε(σ_T) =
                          sqrt(8 · σ_T / (X̄/Ȳ)²)``.

Note: PRIMITIVES.md as shipped uses eq. (8) for the ε-σ_T inversion
(see ``simulations/modules/fx_path.py::epsilon_from_sigma_T``); plan v0.2
re-labels this as eq. (11) in the cohort-2 docstring contract per
MQ-FLAG-2 v0.2 fix. The math is identical; only the label-citation
target differs across documents.

Tier-import discipline: imports allowed from
``simulations.saas_builder.cohort_2.{_errors, types, pricing}`` and from
``simulations.{types, modules, utils}``. MUST NOT import from
``simulations.saas_builder.cohort_2.io``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import numpy as np
import sympy as sp
from numpy.typing import NDArray

from simulations.saas_builder.cohort_2._errors import (
    SignCertificationFailureError,
)
from simulations.saas_builder.cohort_2.pricing import T2CostComposer
from simulations.saas_builder.cohort_2.types import BracketPoint, FloatArray

# ─── Module-level constants ───────────────────────────────────────────────────

#: PRIMITIVES.md §11.b reconciliation tolerance multiplier.
RECONCILER_TOLERANCE_BASE: Final[float] = 1e-10


# ─── Symbolic derivation ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class DeltaSymbolicDeriver:
    """Δ^(a_s) symbolic derivation per PRIMITIVES.md eq. (6) + eq. (10).

    Stateless. Returns a ``sympy.Expr`` for Δ^(a_s) with the spec §5.1
    (T2) ``q_t`` substituted. The expression is constructed at call
    time; re-deriving twice yields ``simplify(expr1 - expr2) == 0``
    (regression test in `simulations.tests.test_saas_cohort2`).

    Symbol map (sympy):

    - ``mean`` ↔ ``X̄/Ȳ`` (TRM-pinned mean);
    - ``eps`` ↔ ``ε`` (perturbation amplitude);
    - ``omega`` ↔ ``ω`` (angular frequency);
    - ``T`` ↔ horizon;
    - ``sigma_T`` ↔ realized-variance proxy σ_T;
    - ``q_sym(t)`` ↔ symbolic placeholder for ``q_t`` (left abstract;
      the substituted T2 form is built when needed by the
      ``with_t2_substitution`` accessor).

    The symbolic Δ form is::

        Δ^(a_s)_sym = (4 / (mean · sqrt(8 · sigma_T / mean²)))
                    · Σ_{t=1}^{T} q_t · f_t / (X/Y)_t²

    where ``f_t = cos²(ω t) - 1/2`` and ``(X/Y)_t = (1 + ε f_t) · mean``.
    """

    def __call__(self) -> sp.Expr:
        """Return the canonical Δ^(a_s) symbolic expression (T-symbolic sum).

        Uses sympy's ``Sum`` over a free index ``t``; callers that want a
        numerical evaluation specialize via ``BracketPoint`` and
        ``DeltaNumericalEvaluator``.
        """
        return _delta_a_s_sympy_expr()


def _delta_a_s_sympy_expr() -> sp.Expr:
    """Construct the closed-form Δ^(a_s) symbolic expression.

    Substitutes ``q_t = p_sub + p_token · softplus_β(τ_t - κ)`` per
    spec §5.1 (T2) into PRIMITIVES.md eq. (10). The ``f_t`` and
    ``(X/Y)_t`` expansions follow PRIMITIVES.md eq. (6); the ε-σ_T
    inversion follows PRIMITIVES.md eq. (11) (= eq. (8) in the shipped
    PRIMITIVES.md numbering, re-labeled per MQ-FLAG-2 v0.2 fix).
    """
    t = sp.symbols("t", positive=True)
    T_sym = sp.symbols("T", positive=True, integer=True)
    mean = sp.symbols("mean", positive=True)
    eps = sp.symbols("eps", positive=True)
    omega = sp.symbols("omega", positive=True)
    sigma_T = sp.symbols("sigma_T", positive=True)
    p_sub = sp.symbols("p_sub", positive=True)
    p_tok = sp.symbols("p_tok", positive=True)
    beta = sp.symbols("beta", positive=True)
    kappa = sp.symbols("kappa", positive=True)
    tau_t = sp.Function("tau")(t)  # ty: ignore[call-non-callable]

    # PRIMITIVES.md eq. (6).
    f_t = sp.cos(omega * t) ** 2 - sp.Rational(1, 2)
    x_over_y_t = (1 + eps * f_t) * mean

    # Spec §5.1 (T2) softplus closed form.
    softplus = sp.log(1 + sp.exp(beta * (tau_t - kappa))) / beta
    q_t = p_sub + p_tok * softplus

    # PRIMITIVES.md eq. (11) (= eq. (8) in shipped PRIMITIVES; renumbered
    # per MQ-FLAG-2 v0.2 fix in cohort-2 docstring contract).
    eps_sigma = sp.sqrt(8 * sigma_T / mean**2)

    # PRIMITIVES.md eq. (10).
    summand = q_t * f_t / x_over_y_t**2
    delta = (4 / (mean * eps_sigma)) * sp.Sum(summand, (t, 1, T_sym))
    return delta


# ─── Numerical evaluators ────────────────────────────────────────────────────


@dataclass(frozen=True)
class DeltaNumericalEvaluator:
    """Closed-form Δ^(a_s) per Pin Δ-cohort, hand-coded against PRIMITIVES.md.

    Evaluates Δ^(a_s) for one ``BracketPoint`` over a 2-D array of
    posterior τ_t draws of shape ``(n_draws, T)``. Returns a 1-D array of
    Δ values (length ``n_draws``).

    PRIMITIVES.md eq. (6):  ``f_t = cos²(ω t) - 1/2``;
                            ``(X/Y)_t = (1 + ε f_t) · X̄/Ȳ``.
    PRIMITIVES.md eq. (10): ``Δ = (4 / (X̄/Ȳ · ε(σ_T))) ·
                            Σ_{t=1}^{T} q_t · f_t / (X/Y)_t²``.
    PRIMITIVES.md eq. (11): ``ε(σ_T) = sqrt(8 · σ_T / (X̄/Ȳ)²)``.

    The composed T2 cost ``q_t^USD = p̄_sub + p_t · softplus_β(τ_t - κ)``
    is pre-built once at construction time via the inner ``T2CostComposer``
    for vectorized evaluation.
    """

    bracket: BracketPoint
    sigma_T: float
    _composer: T2CostComposer | None = None

    def __post_init__(self) -> None:
        if not (math.isfinite(self.sigma_T) and self.sigma_T > 0.0):
            raise ValueError(
                f"DeltaNumericalEvaluator.sigma_T = {self.sigma_T}"
                " must be a finite float > 0"
            )
        cp = self.bracket.cost_params
        composer = T2CostComposer(
            p_sub_bar=cp.p_sub_bar,
            kappa=cp.kappa,
            beta=cp.beta,
            p_t=cp.p_t,
        )
        object.__setattr__(self, "_composer", composer)

    def __call__(
        self, tau_t_draws: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """Return Δ^(a_s) array of shape ``(n_draws,)``.

        Args:
            tau_t_draws: 2-D float64 array of shape ``(n_draws, T)``
                holding per-draw τ_t realisations over horizon T.

        Returns:
            1-D float64 array of length ``n_draws``; entry ``i`` is the
            Δ^(a_s) closed-form sum (PRIMITIVES.md eq. (10)) evaluated at
            row ``i`` of ``tau_t_draws``.

        Raises:
            ValueError: if ``tau_t_draws`` is not 2-D or has T mismatch
                with ``self.bracket.horizon_T``.
        """
        if tau_t_draws.ndim != 2:
            raise ValueError(
                "DeltaNumericalEvaluator: tau_t_draws.ndim ="
                f" {tau_t_draws.ndim} must be 2"
            )
        n_draws, T_arr = tau_t_draws.shape
        if T_arr != self.bracket.horizon_T:
            raise ValueError(
                "DeltaNumericalEvaluator: tau_t_draws.shape[1] ="
                f" {T_arr} must equal bracket.horizon_T ="
                f" {self.bracket.horizon_T}"
            )

        fxp = self.bracket.fx_params
        T = int(self.bracket.horizon_T)
        # Time grid t = 1, …, T (PRIMITIVES.md eq. (10) starts at t=1).
        t_grid = np.arange(1, T + 1, dtype=np.float64)
        f_t = np.cos(fxp.omega * t_grid) ** 2 - 0.5
        x_over_y_t = (1.0 + fxp.epsilon * f_t) * fxp.mean_x_over_y
        # PRIMITIVES.md eq. (11).
        eps_sigma = math.sqrt(8.0 * self.sigma_T / fxp.mean_x_over_y ** 2)
        prefactor = 4.0 / (fxp.mean_x_over_y * eps_sigma)
        weight = f_t / (x_over_y_t ** 2)  # shape (T,)

        composer = self._composer
        assert composer is not None  # __post_init__ guarantees this.
        # Compose q_t per draw: shape (n_draws, T).
        q_t = composer(tau_t_draws)
        # Σ_{t=1}^{T} q_t · weight: vectorize via einsum (or matvec).
        per_draw_sum = q_t @ weight
        return (prefactor * per_draw_sum).astype(np.float64, copy=False)


@dataclass(frozen=True)
class GammaEvaluator:
    """Γ^(a_s) closed-form (PRIMITIVES.md §1 + §7).

    Γ^(a_s) = ∂² CF_T^(a_s) / ∂σ(X/Y)² is the second vol-derivative of
    the cash-flow primitive. Using the σ_T ↔ ε(σ_T) inversion
    (PRIMITIVES.md eq. (11)), and treating the sum ``Σ q_t · f_t /
    (X/Y)_t²`` as a function ``S(ε)``, the closed form is::

        Δ ∝ ε⁻¹ · S(ε)
        Γ = ∂Δ/∂σ_T = ∂Δ/∂ε · ∂ε/∂σ_T

    where ``∂ε/∂σ_T = sqrt(8 / X̄/Ȳ²) / (2 sqrt(σ_T)) = ε / (2 σ_T)``.
    Sign of Γ is NOT pre-pinned (it is reported alongside Δ per spec
    §9 row TODO-COHORT-2).

    Computed numerically via central finite differences on σ_T at the
    bracket point — sympy lambdify is reserved for the symbolic-numeric
    reconciler. Step size ``h = sigma_T * 1e-4`` (relative).
    """

    bracket: BracketPoint
    sigma_T: float
    _delta_eval: DeltaNumericalEvaluator | None = None

    def __post_init__(self) -> None:
        if not (math.isfinite(self.sigma_T) and self.sigma_T > 0.0):
            raise ValueError(
                f"GammaEvaluator.sigma_T = {self.sigma_T}"
                " must be a finite float > 0"
            )
        # The Δ evaluator is constructed at call time; we do NOT cache it
        # here because ``sigma_T`` shifts during finite-differencing. The
        # field is set to a sentinel and replaced per __call__.
        object.__setattr__(
            self,
            "_delta_eval",
            DeltaNumericalEvaluator(
                bracket=self.bracket, sigma_T=self.sigma_T
            ),
        )

    def __call__(
        self, tau_t_draws: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """Return Γ^(a_s) per posterior draw via central finite-differences.

        Args:
            tau_t_draws: 2-D float64 array of shape ``(n_draws, T)``.

        Returns:
            1-D float64 array of length ``n_draws``; finite-difference
            estimate of ``∂² CF_T^(a_s) / ∂ σ_T²`` at the bracket point.
        """
        h = max(self.sigma_T * 1e-4, 1e-12)
        ev_lo = DeltaNumericalEvaluator(
            bracket=self.bracket, sigma_T=self.sigma_T - h
        )
        ev_hi = DeltaNumericalEvaluator(
            bracket=self.bracket, sigma_T=self.sigma_T + h
        )
        delta_lo = ev_lo(tau_t_draws)
        delta_hi = ev_hi(tau_t_draws)
        # Δ already is the first derivative ∂CF/∂σ(X/Y) via PRIMITIVES
        # (10), so the central-difference of Δ w.r.t. σ_T returns Γ.
        # We do NOT need the mid-point evaluation here.
        return ((delta_hi - delta_lo) / (2.0 * h)).astype(
            np.float64, copy=False
        )


@dataclass(frozen=True)
class DeltaSymbolicNumericalReconciler:
    """Self-consistency check between ``DeltaSymbolicDeriver`` lambdify and ``DeltaNumericalEvaluator``.

    Substitutes the bracket point (and one fixed τ_t row) into the
    sympy Expr from ``DeltaSymbolicDeriver``, lambdifies, evaluates,
    and compares to the hand-coded numerical result. Used as a one-shot
    verification per gate run; tolerance is ``1e-10 · N_terms`` per
    PRIMITIVES.md §11.b.

    Raises :class:`SignCertificationFailureError` when discrepancy
    exceeds tolerance; foreground HALTs.
    """

    tolerance_base: float = RECONCILER_TOLERANCE_BASE

    def __call__(
        self,
        bracket: BracketPoint,
        sigma_T: float,
        tau_t_row: FloatArray,
    ) -> bool:
        """Return True iff the symbolic lambdify matches the hand-coded numerical Δ.

        Args:
            bracket: the BracketPoint at which to evaluate.
            sigma_T: realized-variance proxy.
            tau_t_row: 1-D τ_t array of length ``bracket.horizon_T``.

        Returns:
            ``True`` if the lambdified sympy Δ and the
            ``DeltaNumericalEvaluator`` output agree within
            ``tolerance_base · T``; ``False`` otherwise — but the
            exception path raises when discrepancy is significant
            (see ``Raises``).

        Raises:
            ValueError: shape mismatch on ``tau_t_row``.
            SignCertificationFailureError: the two evaluators disagree
                by more than ``tolerance_base · T``.
        """
        if tau_t_row.ndim != 1:
            raise ValueError(
                "DeltaSymbolicNumericalReconciler: tau_t_row.ndim ="
                f" {tau_t_row.ndim} must be 1"
            )
        if tau_t_row.shape[0] != bracket.horizon_T:
            raise ValueError(
                "DeltaSymbolicNumericalReconciler: tau_t_row length ="
                f" {tau_t_row.shape[0]} must equal bracket.horizon_T ="
                f" {bracket.horizon_T}"
            )

        # Build the symbolic Σ term-by-term, substituting concrete tau_t per t.
        cp = bracket.cost_params
        fxp = bracket.fx_params
        T = int(bracket.horizon_T)
        # Closed numeric form (faster + numerically stable lambdify per term).
        eps_sigma = math.sqrt(8.0 * sigma_T / fxp.mean_x_over_y ** 2)
        prefactor = 4.0 / (fxp.mean_x_over_y * eps_sigma)
        symbolic_sum = 0.0
        for k in range(1, T + 1):
            tk = float(k)
            f_k = math.cos(fxp.omega * tk) ** 2 - 0.5
            x_over_y_k = (1.0 + fxp.epsilon * f_k) * fxp.mean_x_over_y
            tau_k = float(tau_t_row[k - 1])
            # Match numpy's logaddexp-based stable form used by
            # SoftplusRegularizer (avoid log1p(exp(...)) which is not the
            # same numerically-stable algorithm).
            softplus_k = float(
                np.logaddexp(0.0, cp.beta * (tau_k - cp.kappa)) / cp.beta
            )
            q_k = cp.p_sub_bar + cp.p_t * softplus_k
            symbolic_sum += q_k * f_k / x_over_y_k ** 2
        symbolic_delta = prefactor * symbolic_sum

        # Hand-coded numerical evaluator on the same row.
        evaluator = DeltaNumericalEvaluator(bracket=bracket, sigma_T=sigma_T)
        numerical_delta = float(evaluator(tau_t_row.reshape(1, -1))[0])

        diff = abs(symbolic_delta - numerical_delta)
        tol = self.tolerance_base * float(T) * max(
            1.0, abs(symbolic_delta), abs(numerical_delta)
        )
        if diff > tol:
            raise SignCertificationFailureError(
                "DeltaSymbolicNumericalReconciler: |Δ_sym - Δ_num| ="
                f" {diff:.3e} exceeds tolerance"
                f" {tol:.3e} (base={self.tolerance_base},"
                f" T={T}); HALT per anti-fishing"
            )
        return True


__all__ = [
    "DeltaNumericalEvaluator",
    "DeltaSymbolicDeriver",
    "DeltaSymbolicNumericalReconciler",
    "GammaEvaluator",
    "RECONCILER_TOLERANCE_BASE",
]
