"""SAAS-COHORT-1 — T1 (subscription-cap) per-user latent-cost posterior.

Implements spec v1.1.1 §5.1 (T1 row) + §5.2 (tier prior + pricing) + §10
(emission schemas) for the Colombian solo AI-native SaaS-builder cohort.

Three-tier package layout (functional-python skill):

- ``priors.py`` — Value tier (frozen-dc prior hyperparameter containers
  with M1 α-floor enforced).
- ``model.py`` — Callable tier (PyMC model factory implementing the
  spec §5.1 (T1) doubly-stochastic compound sum
  ``τ_t = Σ_j Σ_i τ_{j,i}`` with per-active-day NegBin(μ, φ) and
  iid TruncPareto(α, x_m, κ); M3 blended-price assertion at call site).
- ``diagnostics.py`` — Callable tier (arviz r-hat / ESS_bulk / ESS_tail /
  divergence / sim-count / posterior-vs-prior CI-width gate).
- ``emit.py`` — Callable tier (orchestrator — calls
  ``pm.sample_posterior_predictive`` for τ_t / q_t_usd / q_t_cop columns,
  then emits Hive-partitioned parquet via
  ``simulations.utils.parquet_io``).

Tier-import discipline (NON-NEGOTIABLE — plan §3 rule "Any modification
request triggers HALT and a SIM-INFRA follow-up plan"):

- May import: ``simulations.types``, ``simulations.modules``,
  ``simulations.utils``.
- May NOT modify any of the above.
- Cohort-local exceptions (e.g. :class:`DiagnosticGateError`) live in
  ``_errors.py`` to avoid SIM-INFRA-0 surface modification.
"""

from __future__ import annotations

from simulations.saas_builder._errors import DiagnosticGateError
from simulations.saas_builder.diagnostics import (
    CI_WIDTH_RATIO_GATE,
    DEFAULT_MONITORED_PARAMS,
    DIVERGENCE_FRAC_GATE,
    ESS_BULK_GATE,
    ESS_TAIL_GATE,
    RHAT_GATE,
    SIM_COUNT_CHAIN_FLOOR,
    SIM_COUNT_DRAW_FLOOR,
    DiagnosticVerdict,
    PosteriorDiagnostic,
    compute_ci_width_ratio_max,
    compute_ci_width_ratio_per_param,
)
from simulations.saas_builder.emit import (
    COHORT_PRIOR_PERCENTILES,
    CohortEmitter,
    EmissionSummary,
    run_posterior_predictive,
)
from simulations.saas_builder.model import (
    DEFAULT_FX_COP_PER_USD,
    DEFAULT_N_BUILDERS,
    M3_BLENDED_PRICE_ABS_TOL,
    M3_SONNET_BLENDED_PRICE_EXPECTED,
    SIGMA_OBS_FIXED,
    T1ModelFactory,
)
from simulations.saas_builder.priors import (
    CohortPriors,
    negbin_mu_phi_to_r_p,
    tier_id_at_index,
)

__all__ = [
    "CI_WIDTH_RATIO_GATE",
    "COHORT_PRIOR_PERCENTILES",
    "DEFAULT_FX_COP_PER_USD",
    "DEFAULT_MONITORED_PARAMS",
    "DEFAULT_N_BUILDERS",
    "DIVERGENCE_FRAC_GATE",
    "ESS_BULK_GATE",
    "ESS_TAIL_GATE",
    "M3_BLENDED_PRICE_ABS_TOL",
    "M3_SONNET_BLENDED_PRICE_EXPECTED",
    "RHAT_GATE",
    "SIGMA_OBS_FIXED",
    "SIM_COUNT_CHAIN_FLOOR",
    "SIM_COUNT_DRAW_FLOOR",
    "CohortEmitter",
    "CohortPriors",
    "DiagnosticGateError",
    "DiagnosticVerdict",
    "EmissionSummary",
    "PosteriorDiagnostic",
    "T1ModelFactory",
    "compute_ci_width_ratio_max",
    "compute_ci_width_ratio_per_param",
    "negbin_mu_phi_to_r_p",
    "run_posterior_predictive",
    "tier_id_at_index",
]
