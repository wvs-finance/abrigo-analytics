"""Per-family closed-form analytic moments E[σ_T] and Var[σ_T].

Parent spec: ``docs/specs/2026-05-11-stochastic-fx-variant-design.md`` v0.3 §4.2
(canonical pins) and §6 (eq. 7 σ_T proxy + eq. 8 inversion).
Parent plan: ``docs/plans/2026-05-11-stochastic-fx-variant.md`` §7 Task 2.1
pins the literal Python forms transcribed here.

Three free functions, one per SDE family. Each takes the family's
``Parameters`` frozen-dataclass and returns a ``tuple[float, float]`` of
``(E[σ_T], Var[σ_T])``. Pure scalar arithmetic via :pymod:`math`; no IO,
no global state, no sympy at runtime.

Substitution convention (FLAG-MQ-2 disposition)
------------------------------------------------
The symbolic envelope-scale ratio ``(X̄/Ȳ)²`` is conceptually the squared
ratio of the FX numerator and denominator long-run means. At every
canonical-pin fixture in spec v0.3 §4.2 we pin ``x_0 = X̄/Ȳ = 4000.0`` so
the Python implementation may use ``params.x_0**2`` interchangeably with
``(X̄/Ȳ)²``. The SYMBOLIC form ``(X̄/Ȳ)²`` is retained in the LaTeX
fragments under ``notes/stochastic_fx_tex/`` — that is the conceptually
correct notation; the Python substitution is a pin-time convenience only.

NEW-BLOCK-MQ-4 lesson
---------------------
The GBM closed form carries a trailing ``− 1`` inside the brackets:
``(exp(σ²T) − 1) / (σ²T) − 1``. Without it the expression does NOT
vanish at σ → 0 and produces a ~200× error at the canonical pin. The
formula here is the corrected v0.3 form; see
``memory/reference_gbm_sigma_t_closed_form.md`` for the lesson.

Per-family references
---------------------
- GBM: Hull §15 (Options, Futures, and Other Derivatives) — lognormal
  integrated-variance moment generating expansion; mean-zero log-drift
  assumed throughout.
- OU: Standard Ornstein-Uhlenbeck stationary moments (e.g.
  Karatzas-Shreve §5.6, Lord-Pelsser); chi-squared approximation used
  for the leading-order ``Var[σ_T]``.
- Merton jump-diffusion: Andersen & Piterbarg, *Interest Rate Modeling*
  Vol I §2.7 (mean) and §2.7.3 (compound-Poisson moment-of-moment for
  the variance). The variance contribution from the compound-Poisson
  component uses
  ``Var(Σ_i Y_i) = λ T · E[Y²]`` for i.i.d. ``Y_i = x_0² (e^{J_i} − 1)²``
  with ``J_i ~ N(μ_J, σ_J²)``; we expand
  ``E[(e^J − 1)⁴] = e^{4μ_J + 8σ_J²} − 4 e^{3μ_J + 9σ_J²/2}
                    + 6 e^{2μ_J + 2σ_J²} − 4 e^{μ_J + σ_J²/2} + 1``
  using the Gaussian moment-generating identity
  ``E[e^{k J}] = exp(k μ_J + k² σ_J² / 2)``.

Tier discipline
---------------
Callable tier under the ``functional-python`` regime. Imports from
``simulations.stochastic_fx.types`` and ``simulations.stochastic_fx._errors``
only. Must NOT import from ``simulations.stochastic_fx.utils`` (which does
not yet exist — Task 5 territory). All functions are stateless pure
transforms returning plain Python floats.
"""

from __future__ import annotations

import math

from simulations.stochastic_fx.types import (
    GBMParameters,
    JumpDiffusionParameters,
    OUParameters,
)


def gbm_sigma_t_moments(params: GBMParameters) -> tuple[float, float]:
    """Analytic ``(E[σ_T], Var[σ_T])`` for the GBM family.

    Closed forms (spec v0.3 §4.2; plan §7 Task 2.1 table):

    - ``E[σ_T] = (X̄/Ȳ)² · ((exp(σ² T) − 1) / (σ² T) − 1)``
    - ``Var[σ_T] = 2 (X̄/Ȳ)⁴ · (exp(σ² T) − 1)² / (σ⁴ T²)``

    At canonical pin we substitute ``(X̄/Ȳ)² → params.x_0**2``
    (FLAG-MQ-2 disposition). The trailing ``− 1`` in ``E[σ_T]`` is the
    NEW-BLOCK-MQ-4 fix — without it the expression fails the σ → 0
    vanishing requirement.

    Mean-zero log-drift assumed (Hull §15 leading order). All inputs
    are validated by :class:`~simulations.stochastic_fx.types.GBMParameters`
    via ``__post_init__``; this function performs no further validation
    and returns plain Python floats.
    """
    sigma2_T = params.sigma**2 * params.T
    # ((exp(x) - 1)/x) - 1  ==  (exp(x) - 1 - x)/x  ==  (expm1(x) - x)/x.
    # The (expm1(x) - x)/x form is algebraically identical to the plan-§7
    # acceptance-table form but is numerically stable at σ → 0; the naive
    # ``(math.exp(σ²T) - 1) / (σ²T) - 1`` loses all precision once σ²T
    # drops below ~1e-15 (NEW-BLOCK-MQ-4 σ → 0 sanity test).
    expectation = params.x_0**2 * (math.expm1(sigma2_T) - sigma2_T) / sigma2_T
    variance = (
        2.0
        * params.x_0**4
        * math.expm1(sigma2_T) ** 2
        / (params.sigma**4 * params.T**2)
    )
    return (float(expectation), float(variance))


def ou_sigma_t_moments(params: OUParameters) -> tuple[float, float]:
    """Analytic ``(E[σ_T], Var[σ_T])`` for the OU (stationary) family.

    Closed forms (spec v0.3 §4.2; plan §7 Task 2.1 table):

    - ``E[σ_T] = σ² / (2 θ)`` (exact stationary moment)
    - ``Var[σ_T] = 2 σ⁴ / ((2 θ)² T)`` (leading order under
      chi-squared approximation)

    Reference: standard Ornstein-Uhlenbeck stationary moments (see e.g.
    Karatzas-Shreve §5.6). All inputs validated upstream by
    :class:`~simulations.stochastic_fx.types.OUParameters`.
    """
    expectation = params.sigma**2 / (2.0 * params.theta)
    variance = 2.0 * params.sigma**4 / ((2.0 * params.theta) ** 2 * params.T)
    return (float(expectation), float(variance))


def merton_sigma_t_moments(
    params: JumpDiffusionParameters,
) -> tuple[float, float]:
    """Analytic ``(E[σ_T], Var[σ_T])`` for the Merton jump-diffusion family.

    Closed forms (spec v0.3 §4.2; plan §7 Task 2.1 table; Andersen-Piterbarg
    Vol I §2.7 mean, §2.7.3 variance):

    - ``E[σ_T] = x_0² σ² T``
      ``+ λ x_0² · (e^{2(μ_J + σ_J²)} − 2 e^{μ_J + σ_J²/2} + 1) · T``

      where the jump factor is
      ``E[(e^J − 1)²] = E[e^{2J}] − 2 E[e^J] + 1``
      for ``J ~ N(μ_J, σ_J²)``.

    - ``Var[σ_T] = 2 σ⁴ x_0⁴ T + λ x_0⁴ · M₄ · T``

      where ``M₄ = E[(e^J − 1)⁴]`` is the compound-Poisson
      moment-of-moment per Andersen-Piterbarg §2.7.3:

      ``M₄ = e^{4μ_J + 8σ_J²} − 4 e^{3μ_J + 9σ_J²/2}``
      ``    + 6 e^{2μ_J + 2σ_J²} − 4 e^{μ_J + σ_J²/2} + 1``

      derived by binomial expansion of ``(e^J − 1)⁴`` and the Gaussian
      moment-generating identity ``E[e^{k J}] = exp(k μ_J + k² σ_J² / 2)``.
      The variance of a compound-Poisson sum ``Σ_{i=1..N_T} Y_i`` with
      ``N_T ~ Poisson(λ T)`` and i.i.d.
      ``Y_i = x_0² (e^{J_i} − 1)²`` is
      ``Var(Σ_i Y_i) = λ T · E[Y_i²] = λ T x_0⁴ M₄``.

    Mean-zero log-drift assumed. All inputs validated upstream by
    :class:`~simulations.stochastic_fx.types.JumpDiffusionParameters`.
    """
    mu_j = params.jump_mean
    s_j = params.jump_std
    s_j2 = s_j * s_j

    # E[(e^J - 1)^2] = E[e^{2J}] - 2 E[e^J] + 1
    e_g_minus_1_sq = (
        math.exp(2.0 * (mu_j + s_j2))
        - 2.0 * math.exp(mu_j + s_j2 / 2.0)
        + 1.0
    )

    expectation = (
        params.x_0**2 * params.sigma**2 * params.T
        + params.lambda_jump * params.x_0**2 * e_g_minus_1_sq * params.T
    )

    # M_4 = E[(e^J - 1)^4]
    #     = E[e^{4J}] - 4 E[e^{3J}] + 6 E[e^{2J}] - 4 E[e^J] + 1
    # with E[e^{kJ}] = exp(k * mu_J + k^2 * sigma_J^2 / 2)
    m4 = (
        math.exp(4.0 * mu_j + 8.0 * s_j2)
        - 4.0 * math.exp(3.0 * mu_j + 4.5 * s_j2)
        + 6.0 * math.exp(2.0 * mu_j + 2.0 * s_j2)
        - 4.0 * math.exp(mu_j + s_j2 / 2.0)
        + 1.0
    )

    variance = (
        2.0 * params.sigma**4 * params.x_0**4 * params.T
        + params.lambda_jump * params.x_0**4 * m4 * params.T
    )

    return (float(expectation), float(variance))


__all__ = [
    "gbm_sigma_t_moments",
    "merton_sigma_t_moments",
    "ou_sigma_t_moments",
]
