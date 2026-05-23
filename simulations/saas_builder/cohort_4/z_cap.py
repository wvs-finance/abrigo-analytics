r"""Posterior-predictive Z-cap evaluator + 5-test-point sign certification.

Plan v0.2 §Phase-2 Task 2.2 / 2.4 / Pin M2 (5-TP sign cert) / Pin M2-fix
(MC error budget). NO IO at this tier — emission is delegated to
``cohort_4.io``.

Z definition (spec §4.1 cap operationalization):

    Z = E[q_t^USD / (X/Y)_t + π(t)]

with ``q_t^USD`` drawn from the C1 ``synthetic_tau_t`` panel and ``π(t)``
the closed-form streamed premium derived in ``pi_derivation.py``.

Per-test-point: each TP fixes ``(κ, X̄/Ȳ, σ₀)``; the per-draw posterior-
predictive realisation is::

    Z_d = (q_t_cop)_d / (X̄/Ȳ)_TP
        + π(t_anchor; K⋆_d, σ₀_TP, ε, ω, t_anchor, X̄/Ȳ_TP)

with ``K⋆_d = (q_t_cop)_d`` (per-draw equilibrium strike).

**K⋆ identification (CORRECTIONS-α v0.3, MQ-BLOCK-3 disambiguation).**
Plan v0.3 fixes the v0.2 silent identification ``K⋆ ≡ q_t^cop``:

- Per PRIMITIVES.md §8.1, K⋆ is the equilibrium strike of the CPO
  payoff Π(σ_T) = K⋆√σ_T. Dimensionally, since Π is denominated in COP
  and σ_T has units COP², K⋆ is dimensionally COP/√(COP²) — i.e., a
  strike-level scalar with units √(COP²)/COP = dimensionless when
  Π is normalized.
- Per saas-note §4.1, the streamed premium π(t) (which scales with K⋆)
  is set so that the user's CPO position notionally tracks their
  posterior-predictive monthly USD obligation translated to COP.
- Setting K⋆_d = (q_t_cop)_d ties the per-draw convex-hedge notional
  to the C1 posterior's per-draw overage realisation. Under the
  ideal-scenario clause (CLAUDE.md §"ideal-scenario modeling permitted"
  — Stage-2 deployment liquidity is structurally thin and the cohort_4
  artifact is a Stage-2 ideal-scenario M-sketch), this is a free
  parameter of the M-design step, not a measured quantity. The
  dimensional reading is a "hedge notional in COP per √variance unit"
  which is consistent with the §4.1 pitch identity.
- Plan v0.3 makes this identification EXPLICIT and surfaces it as a
  M-design parameter rather than a derived quantity. Alternative
  identifications (K⋆ = κ converted via FX, K⋆ = constant per-tier
  notional) are admissible Stage-2 M-design variants and are scoped
  to a separate plan amendment.
- κ is ABSENT from π(t) (CORRECTIONS-α v0.3 anti-fishing fix); κ enters
  Z only via the q_t^USD softplus channel, already C2-marginalized
  into the q_t_cop draws this evaluator consumes.

The MC stderr/Ẑ ≤ 1e-3 budget is enforced at runtime; breaches raise
``MCErrorBudgetExceededError``. Sign violations (any per-TP ``ci_95_lo
≤ 0``) raise ``DiagnosticGateError`` per the HALT protocol.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simulations.saas_builder.cohort_4._errors import (
    DiagnosticGateError,
    IdentityToleranceError,
    MCErrorBudgetExceededError,
)
from simulations.saas_builder.cohort_4.pi_derivation import (
    IdentityResidualEvaluator,
)
from simulations.saas_builder.cohort_4.types import (
    MCBudget,
    MC_DRAWS_FLOOR,
    NUMERICAL_IDENTITY_TOL,
    PiTSymbolic,
    SignVerdict,
    TestPoint,
    ZEvaluationResult,
    stderr_ratio,
)

# ─── Defaults (plan v0.2 §M2 + spec §6 functional-form pins) ─────────────────

#: Spec §6 / PRIMITIVES.md §6 — ε ∈ (0, 1) FX-path amplitude (default mid-bracket).
DEFAULT_FX_EPSILON: float = 0.1

#: Spec §6 — ω > 0 FX-path frequency (default; M5-anchor compatible).
DEFAULT_FX_OMEGA: float = 1.0

#: Spec §2 — monthly time grain; t_anchor = T/2 = 6.0 months for stable σ_T.
DEFAULT_T_ANCHOR: float = 6.0


# ─── Z evaluator (Callable tier) ─────────────────────────────────────────────


@dataclass(frozen=True)
class PerDrawZEvaluator:
    """Compute the per-draw Z realisation array for one TestPoint.

    Inputs at ``__call__``:

    - ``pi_t``: PiTSymbolic carrying the lambdified π(t).
    - ``test_point``: one TestPoint (κ, X̄/Ȳ, σ₀, label).
    - ``q_t_cop_draws``: 1-D float64 array of posterior-predictive
      ``q_t^cop`` realisations from the C1 synthetic_tau_t panel.

    Returns: ZEvaluationResult carrying the per-draw Z array + summary
    statistics + the identity residual at this test point.

    Pin M2-fix (MC error budget) is enforced upstream by ``ZCapRunner``;
    this Callable computes the budget metric but does not raise on breach.
    """

    fx_epsilon: float = DEFAULT_FX_EPSILON
    fx_omega: float = DEFAULT_FX_OMEGA
    t_anchor: float = DEFAULT_T_ANCHOR
    identity_evaluator: IdentityResidualEvaluator = IdentityResidualEvaluator()

    def __post_init__(self) -> None:
        if not (0.0 < self.fx_epsilon < 1.0):
            raise ValueError(
                f"PerDrawZEvaluator.fx_epsilon = {self.fx_epsilon}"
                " must lie in (0, 1) per spec §6"
            )
        if not (self.fx_omega > 0.0):
            raise ValueError(
                f"PerDrawZEvaluator.fx_omega = {self.fx_omega} must be > 0"
            )
        if not (self.t_anchor > 0.0):
            raise ValueError(
                f"PerDrawZEvaluator.t_anchor = {self.t_anchor}"
                " must be > 0 (σ_T(t) has 1/t factor)"
            )

    def __call__(
        self,
        pi_t: PiTSymbolic,
        test_point: TestPoint,
        q_t_cop_draws: NDArray[np.float64],
    ) -> ZEvaluationResult:
        """Return the per-draw posterior-predictive Z result."""
        if q_t_cop_draws.ndim != 1:
            raise ValueError(
                "PerDrawZEvaluator: q_t_cop_draws.ndim ="
                f" {q_t_cop_draws.ndim} must be 1"
            )
        if q_t_cop_draws.size < MC_DRAWS_FLOOR:
            raise ValueError(
                f"PerDrawZEvaluator: q_t_cop_draws.size = {q_t_cop_draws.size}"
                f" must be ≥ {MC_DRAWS_FLOOR} (Pin M2-fix)"
            )
        if not np.all(np.isfinite(q_t_cop_draws)):
            raise ValueError(
                "PerDrawZEvaluator: q_t_cop_draws contains non-finite values"
            )
        if not np.all(q_t_cop_draws >= 0.0):
            raise ValueError(
                "PerDrawZEvaluator: q_t_cop_draws contains negative values;"
                " q_t^cop is a cost (must be ≥ 0)"
            )

        # K⋆_d = (q_t_cop)_d (per-draw equilibrium strike — saas-note §4.1
        # pitch identity ties hedge notional to expected COP overage).
        # Add a small floor to keep K⋆ > 0 (PiTSymbolic positivity assumption).
        K_star_per_draw = np.maximum(q_t_cop_draws, 1e-12).astype(np.float64)

        # π(t_anchor; K⋆_d, σ₀_TP, ε, ω, t_anchor, X̄/Ȳ_TP) per draw.
        # CORRECTIONS-α v0.3: 6th positional arg is xy_bar (was kappa);
        # κ is absent from π(t) under the honest derivation.
        pi_per_draw = pi_t.lambdified(
            K_star_per_draw,
            test_point.sigma_0,
            self.fx_epsilon,
            self.fx_omega,
            self.t_anchor,
            test_point.x_over_y_bar,
        )
        pi_per_draw = np.asarray(pi_per_draw, dtype=np.float64)

        # q_t_cop / (X̄/Ȳ) per draw.
        q_over_xy = q_t_cop_draws / test_point.x_over_y_bar

        # Z_d = q/(X/Y) + π(t).
        z_per_draw = (q_over_xy + pi_per_draw).astype(np.float64, copy=False)
        if not np.all(np.isfinite(z_per_draw)):
            raise ValueError(
                "PerDrawZEvaluator: per-draw Z contains non-finite values"
            )

        z_mean = float(np.mean(z_per_draw))
        z_var = float(np.var(z_per_draw, ddof=1))
        z_stderr = float(np.sqrt(z_var / z_per_draw.size))
        ci_95_lo = float(np.percentile(z_per_draw, 2.5))
        ci_95_hi = float(np.percentile(z_per_draw, 97.5))

        # Numerical identity residual at this TP (uses K⋆ = posterior-mean).
        K_star_mean = float(np.mean(K_star_per_draw))
        identity_residual = self.identity_evaluator(
            pi_t,
            K_star=K_star_mean,
            sigma_0=test_point.sigma_0,
            epsilon=self.fx_epsilon,
            omega=self.fx_omega,
            xy_bar=test_point.x_over_y_bar,
        )

        return ZEvaluationResult(
            label=test_point.label,
            z_per_draw=z_per_draw,
            z_mean=z_mean,
            z_stderr=z_stderr,
            ci_95_lo=ci_95_lo,
            ci_95_hi=ci_95_hi,
            identity_residual=identity_residual,
        )


# ─── 5-test-point sign certification (Callable tier) ─────────────────────────


@dataclass(frozen=True)
class SignCertifier:
    """Convert a tuple of ``ZEvaluationResult`` into per-TP ``SignVerdict``.

    Plan v0.3 §M2 sign expectation (immutable per anti-fishing): every TP
    must have ``ci_95_lo > 0``. Identity residual must be ≤
    ``NUMERICAL_IDENTITY_TOL = 1e-6`` (Path A v0 §10.4 inheritance).

    Monotonicity check (called separately by the runner):
    ``|π|_TP4 > |π|_TP1 > |π|_TP5`` (∂|π|/∂(X̄/Ȳ) > 0 strict, plan v0.3
    M2-fix; replaces v0.2's ∂|π|/∂κ which was structurally
    unsatisfiable since κ ∉ free_symbols(π) — anti-fishing remediation
    per CORRECTIONS-α v0.3).
    """

    def __call__(
        self, results: Sequence[ZEvaluationResult]
    ) -> tuple[SignVerdict, ...]:
        """Return one SignVerdict per ZEvaluationResult."""
        return tuple(
            SignVerdict(
                label=r.label,
                z_value=r.z_mean,
                ci_95_lo=r.ci_95_lo,
                ci_95_hi=r.ci_95_hi,
                passes=r.ci_95_lo > 0.0,
                identity_residual=r.identity_residual,
                identity_passes=r.identity_residual <= NUMERICAL_IDENTITY_TOL,
            )
            for r in results
        )


def assert_pin_m2_monotonicity(
    pi_t: PiTSymbolic,
    test_points: Sequence[TestPoint],
    fx_epsilon: float = DEFAULT_FX_EPSILON,
    fx_omega: float = DEFAULT_FX_OMEGA,
    t_anchor: float = DEFAULT_T_ANCHOR,
    K_star_anchor: float = 1.0e6,
) -> tuple[float, float, float]:
    r"""Return ``(|π|_TP4, |π|_TP1, |π|_TP5)`` and assert strict monotonicity.

    CORRECTIONS-α v0.3 (MQ-BLOCK-1 anti-fishing fix): the v0.2 chain
    ``|π|_TP2 > |π|_TP1 > |π|_TP3`` (corresponding to ``∂|π|/∂κ < 0``)
    was satisfiable only via a spurious ``1/κ`` factor in π. With κ
    correctly removed from π under the honest derivation, |π| is
    identical at TP1=TP2=TP3 and the κ-monotonicity gate is structurally
    unsatisfiable.

    Plan v0.3 §M2-fix replaces it with the legitimate (X̄/Ȳ)-monotonicity
    ``∂|π|/∂(X̄/Ȳ) > 0`` strict, anchored in PRIMITIVES.md §6 closed
    form (π ∝ (X̄/Ȳ)²). Equivalent strict chain
    ``|π|_TP4 > |π|_TP1 > |π|_TP5`` (X̄/Ȳ = 4200, 4000, 3800 COP/USD).

    Args:
        pi_t: symbolic π(t) anchor.
        test_points: must include TP1, TP4, TP5 in canonical positions.
        fx_epsilon, fx_omega, t_anchor: shared FX path constants.
        K_star_anchor: shared K⋆ for the (X̄/Ȳ)-direction property test.

    Returns:
        Tuple ``(|π|_TP4, |π|_TP1, |π|_TP5)`` for downstream sidecar
        emission.

    Raises:
        DiagnosticGateError: on monotonicity violation (anti-fishing
            HALT per ``feedback_pathological_halt_anti_fishing_checkpoint``).
    """
    by_label = {tp.label: tp for tp in test_points}
    missing = {"TP1", "TP4", "TP5"} - by_label.keys()
    if missing:
        raise DiagnosticGateError(
            f"assert_pin_m2_monotonicity: missing test-points {sorted(missing)};"
            " plan v0.3 §M2 grid requires TP1, TP4, TP5"
            " ((X̄/Ȳ)-monotonicity branch)"
        )
    pi_vals: dict[str, float] = {}
    for label in ("TP4", "TP1", "TP5"):
        tp = by_label[label]
        pi_v = pi_t.lambdified(
            K_star_anchor,
            tp.sigma_0,
            fx_epsilon,
            fx_omega,
            t_anchor,
            tp.x_over_y_bar,
        )
        pi_vals[label] = float(np.abs(np.asarray(pi_v).item()))
    if not (pi_vals["TP4"] > pi_vals["TP1"] > pi_vals["TP5"]):
        raise DiagnosticGateError(
            "Pin M2 monotonicity violation:"
            f" |π|_TP4={pi_vals['TP4']:.6e},"
            f" |π|_TP1={pi_vals['TP1']:.6e},"
            f" |π|_TP5={pi_vals['TP5']:.6e};"
            " required strict chain |π|_TP4 > |π|_TP1 > |π|_TP5"
            " (plan v0.3 §M2-fix ∂|π|/∂(X̄/Ȳ) > 0)"
        )
    return (pi_vals["TP4"], pi_vals["TP1"], pi_vals["TP5"])


# ─── Top-level cohort runner (Callable tier) ─────────────────────────────────


@dataclass(frozen=True)
class ZCapRunner:
    """Orchestrate the 5-test-point Z-cap evaluation + pin emission.

    Outputs a tuple ``(per_tp_results, sign_verdicts, monotonicity_triple)``
    consumed by ``cohort_4.io.pin_and_emit``. No IO at this tier.

    Pin M2-fix MC budget enforcement: every TP's ``ZEvaluationResult`` is
    checked against ``mc_budget.stderr_ratio_ceiling`` immediately after
    evaluation; on breach, ``MCErrorBudgetExceededError`` is raised
    (HALT routing per ``feedback_pathological_halt_anti_fishing_checkpoint``).

    Sign / identity gates: any TP failing ``passes`` or ``identity_passes``
    raises ``DiagnosticGateError`` / ``IdentityToleranceError`` respectively.
    """

    per_draw_evaluator: PerDrawZEvaluator = PerDrawZEvaluator()
    sign_certifier: SignCertifier = SignCertifier()
    mc_budget: MCBudget = MCBudget(n_draws=MC_DRAWS_FLOOR)

    def __call__(
        self,
        pi_t: PiTSymbolic,
        test_points: Sequence[TestPoint],
        q_t_cop_draws: NDArray[np.float64],
    ) -> tuple[
        tuple[ZEvaluationResult, ...],
        tuple[SignVerdict, ...],
        tuple[float, float, float],
    ]:
        """Evaluate all 5 test points + sign-certify + monotonicity-check."""
        if len(test_points) != 5:
            raise ValueError(
                f"ZCapRunner: test_points must have length 5;"
                f" got {len(test_points)}"
            )
        # Need ≥ mc_budget.n_draws posterior draws.
        if q_t_cop_draws.size < self.mc_budget.n_draws:
            raise ValueError(
                f"ZCapRunner: q_t_cop_draws.size = {q_t_cop_draws.size}"
                f" must be ≥ mc_budget.n_draws = {self.mc_budget.n_draws}"
            )
        # Truncate to exactly n_draws if the C1 panel is larger
        # (deterministic — first n rows; C1 emits a sorted panel).
        draws = q_t_cop_draws[: self.mc_budget.n_draws].astype(
            np.float64, copy=False
        )

        results = tuple(
            self.per_draw_evaluator(pi_t, tp, draws) for tp in test_points
        )

        # MC budget enforcement (Pin M2-fix).
        for r in results:
            ratio = stderr_ratio(r)
            if ratio > self.mc_budget.stderr_ratio_ceiling:
                raise MCErrorBudgetExceededError(
                    f"MC budget breach at {r.label}:"
                    f" stderr/Ẑ = {ratio:.6e} > "
                    f"ceiling {self.mc_budget.stderr_ratio_ceiling:.6e};"
                    f" N_draws = {draws.size};"
                    " HALT per feedback_pathological_halt_anti_fishing_checkpoint"
                )

        # Identity-tolerance gate (Pin M2 numerical inheritance).
        for r in results:
            if r.identity_residual > NUMERICAL_IDENTITY_TOL:
                raise IdentityToleranceError(
                    f"Identity residual breach at {r.label}:"
                    f" residual = {r.identity_residual:.6e}"
                    f" > tol {NUMERICAL_IDENTITY_TOL:.6e};"
                    " HALT per feedback_pathological_halt_anti_fishing_checkpoint"
                )

        sign_verdicts = self.sign_certifier(results)

        # Sign gate (Pin M2 — Z_cap > 0 ∀ TP).
        violations = [v for v in sign_verdicts if not v.passes]
        if violations:
            raise DiagnosticGateError(
                "Sign verdict failure at"
                f" {[v.label for v in violations]}:"
                " ci_95_lo ≤ 0 — HALT per spec §8(1) +"
                " feedback_pathological_halt_anti_fishing_checkpoint"
            )

        # Monotonicity assertion (uses K⋆ = posterior-mean for stability).
        K_star_mean = float(np.mean(np.maximum(draws, 1e-12)))
        monotonicity_triple = assert_pin_m2_monotonicity(
            pi_t,
            test_points,
            fx_epsilon=self.per_draw_evaluator.fx_epsilon,
            fx_omega=self.per_draw_evaluator.fx_omega,
            t_anchor=self.per_draw_evaluator.t_anchor,
            K_star_anchor=K_star_mean,
        )

        return results, sign_verdicts, monotonicity_triple


__all__ = [
    "DEFAULT_FX_EPSILON",
    "DEFAULT_FX_OMEGA",
    "DEFAULT_T_ANCHOR",
    "PerDrawZEvaluator",
    "SignCertifier",
    "ZCapRunner",
    "assert_pin_m2_monotonicity",
]
