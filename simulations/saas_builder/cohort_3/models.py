"""PyMC model builders + fit driver for SAAS-COHORT-3 Υ_t form selection.

Implements spec §5 form (1)/(2)/(3) verbatim — three Callable model
builders + a fit-driver Callable that wraps ``pm.sample`` and
``pm.compute_log_likelihood``.

Tier — Callable (frozen-dc + ``__call__``). Imports allowed: cohort_3
``types``/``priors`` + PyMC + numpy. NOT ``cohort_3.io``.

Pin coverage:

- Pin R1: three forms exactly. ``CandidateSetClosedError`` on any 4th
  registration via the fit-driver registry.
- Pin R4: sampler defaults pin draws ≥ 4000 per chain × 4 chains.
- Pin R4-bis: ``rho_boundary_mass`` computed from posterior for
  AR(1)-log only; non-AR(1) forms emit None.
"""

from __future__ import annotations

import math
import warnings
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

import arviz as az
import numpy as np
import pymc as pm

from simulations.saas_builder.cohort_3._errors import (
    CandidateSetClosedError,
    LfoCvUnavailableError,
)
from simulations.saas_builder.cohort_3.priors import (
    Ar1LogPrior,
    DetChurnPrior,
    MartingalePrior,
)
from simulations.saas_builder.cohort_3.types import (
    REVENUE_FORM_NAMES,
    RHO_BOUNDARY_TAIL_THRESHOLD,
    CvMethod,
    RevenueFormFit,
    RevenueFormName,
    UpsilonPanel,
)

# ─── Pin R4 sim-count constants ────────────────────────────────────────────────

#: Pin R4 — Stage-2 PyMC sim-count floor (per chain post-warmup).
DRAWS_PER_CHAIN_FLOOR: Final[int] = 4000

#: Pin R4 — chain-count floor.
CHAIN_FLOOR: Final[int] = 4

#: Pin R4 — r-hat ceiling.
RHAT_GATE: Final[float] = 1.01

#: Pin R4 — ESS_bulk / ESS_tail floor.
ESS_GATE: Final[float] = 400.0

#: Pin R4 — Pareto-k̂ HIGH threshold.
PARETO_K_HIGH: Final[float] = 0.7

#: Pin R4 — Pareto-k̂ HIGH-frac FAIL ceiling.
PARETO_K_HIGH_FRAC_GATE: Final[float] = 0.05


# ─── First-trajectory helper ──────────────────────────────────────────────────


def _first_trajectory(panel: UpsilonPanel) -> np.ndarray:
    """Extract a single Υ_t trajectory, sorted by month_index.

    The three Stage-2 model builders fit a 1-D time series; this helper
    picks the first (cohort_id, simulation_id) group encountered
    (deterministic given panel input order) and returns its Υ_t values
    sorted ascending by month.

    KNOWN LIMITATION — Stage-2 single-trajectory fit (CORRECTIONS-α v0.3
    §15.8 / CR-S4 / MQ-FLAG-1). When ``UpsilonPanel`` carries N > 1
    posterior trajectories (multiple ``simulation_id`` values), this
    helper SILENTLY DISCARDS the remaining N-1 trajectories. The Stage-2
    spec scope (spec §5 + Pin R5) admits only single-trajectory fits;
    hierarchical pooling across posterior trajectories is DEFERRED to
    Stage-3 and out of scope for this iteration. Consumers that supply a
    multi-sim panel will see LOO-CV computed only on the first
    trajectory's (T-1) increments — ELPD/SE will reflect that
    trajectory's idiosyncrasies, not the full posterior. Document this
    on the verdict-routing artifact when a multi-sim panel is fed.

    Returns:
        1-D float array of length ≥ 2 — the first trajectory only.

    Raises:
        ValueError: if no trajectory has ≥ 2 observations.
    """
    cohort_id = panel.cohort_id
    simulation_id = panel.simulation_id
    months = panel.month_index
    values = panel.upsilon_cop
    if cohort_id and simulation_id:
        first_key = (cohort_id[0], simulation_id[0])
    else:
        raise ValueError("UpsilonPanel must have non-empty trajectory labels")
    # CORRECTIONS-α v0.3 §15.8: surface multi-trajectory truncation loudly.
    # Stage-2 fit is single-trajectory by design; hierarchical pooling
    # deferred to Stage-3.
    unique_keys = set(zip(cohort_id, simulation_id))
    if len(unique_keys) > 1:
        warnings.warn(
            f"_first_trajectory: panel carries {len(unique_keys)}"
            f" (cohort_id, simulation_id) trajectories;"
            f" Stage-2 fit uses ONLY the first ({first_key!r}) and"
            f" discards the remaining {len(unique_keys) - 1}. Hierarchical"
            f" pooling deferred to Stage-3 (spec-pin reference: spec §5"
            f" + Pin R5; CORRECTIONS-α v0.3 §15.8 / CR-S4 / MQ-FLAG-1).",
            stacklevel=2,
        )
    indices = [
        i for i, (c, s) in enumerate(zip(cohort_id, simulation_id))
        if (c, s) == first_key
    ]
    if len(indices) < 2:
        raise ValueError(
            f"_first_trajectory: trajectory {first_key!r} has"
            f" {len(indices)} observations; need ≥ 2"
        )
    sub_months = months[indices]
    sub_values = values[indices]
    order = np.argsort(sub_months, kind="stable")
    return np.asarray(sub_values[order], dtype=np.float64)


# ─── Model builder Callables (Pin R1 — three closed forms) ─────────────────────


@dataclass(frozen=True)
class MartingaleModelBuilder:
    """Spec §5 form (1) — martingale Υ_t = Υ_{t-1} + ε_t.

    Likelihood: y_t = y_{t-1} + ε_t with ε_t ~ Normal(0, σ_ε).
    Prior: σ_ε ~ HalfNormal(scale).

    Pointwise log-likelihood emitted via ``pm.compute_log_likelihood``
    over the (T-1) increment observations after the initial.
    """

    prior: MartingalePrior = field(default_factory=MartingalePrior)

    def __call__(self, panel: UpsilonPanel) -> pm.Model:
        y = _first_trajectory(panel)
        diffs = np.diff(y)
        with pm.Model() as model:
            sigma_epsilon = pm.HalfNormal(
                "sigma_epsilon", sigma=self.prior.sigma_epsilon_scale
            )
            pm.Normal("obs", mu=0.0, sigma=sigma_epsilon, observed=diffs)
        return model


@dataclass(frozen=True)
class Ar1LogModelBuilder:
    """Spec §5 form (2) — AR(1)-log: log Υ_t = ρ log Υ_{t-1} + ε_t.

    Prior: ρ ~ TruncatedNormal(μ_ρ, σ_ρ, lower=-1, upper=1);
    σ_ε ~ HalfNormal(scale).

    Likelihood: log y_t ~ Normal(ρ · log y_{t-1}, σ_ε) for t ≥ 1.
    """

    prior: Ar1LogPrior = field(default_factory=Ar1LogPrior)

    def __call__(self, panel: UpsilonPanel) -> pm.Model:
        y = _first_trajectory(panel)
        log_y = np.log(y)
        log_y_prev = log_y[:-1]
        log_y_curr = log_y[1:]
        with pm.Model() as model:
            rho = pm.TruncatedNormal(
                "rho",
                mu=self.prior.rho_mu,
                sigma=self.prior.rho_sigma,
                lower=-1.0,
                upper=1.0,
            )
            sigma_epsilon = pm.HalfNormal(
                "sigma_epsilon", sigma=self.prior.sigma_epsilon_scale
            )
            pm.Normal(
                "obs",
                mu=rho * log_y_prev,
                sigma=sigma_epsilon,
                observed=log_y_curr,
            )
        return model


@dataclass(frozen=True)
class DetChurnModelBuilder:
    """Spec §5 form (3) — deterministic + churn: Υ_t = Υ_0·(1+g)^t · ∏(1-λ).

    Closed-form: at month t (0-indexed), Υ_t = Υ_0 · ((1+g)·(1-λ))^t.
    The combined effective growth ((1+g)·(1-λ)) is what the data identifies;
    we estimate Υ_0, g, λ separately with informative priors per RESEARCH
    Q4 anchors.

    Likelihood: log y_t ~ Normal(log Υ_0 + t·log((1+g)·(1-λ)), σ_obs).
    σ_obs is a HalfNormal nuisance with the AR(1) σ_ε scale (re-uses
    same magnitude on log scale).
    """

    prior: DetChurnPrior = field(default_factory=DetChurnPrior)
    sigma_obs_scale: float = 0.5

    def __post_init__(self) -> None:
        if not (math.isfinite(self.sigma_obs_scale)
                and self.sigma_obs_scale > 0.0):
            raise ValueError(
                f"DetChurnModelBuilder.sigma_obs_scale ="
                f" {self.sigma_obs_scale} must be a finite float > 0"
            )

    def __call__(self, panel: UpsilonPanel) -> pm.Model:
        y = _first_trajectory(panel)
        # Spec v1.2.1 §15.4 forward-fix (CLOSE Phase 0 Task 0.2b): the
        # likelihood scores t=1..T-1 (length T-1), matching the (T-1)
        # convention documented in :func:`_first_trajectory`. Without this
        # alignment, ``arviz.compare`` raises "number of observations should
        # be the same across all models" because martingale and AR(1)-log
        # both emit T-1 pointwise log-lik values while det+churn previously
        # emitted T. The deterministic process Υ_t = Υ_0·((1+g)·(1-λ))^t
        # at t=0 is exactly Υ_0, so dropping that observation removes a
        # degenerate point that contributed only to identifying Υ_0 (which
        # is now identified through the t≥1 mean curve via prior + data).
        t_arr = np.arange(1, len(y), dtype=np.float64)
        log_y = np.log(y[1:])
        with pm.Model() as model:
            upsilon_0 = pm.LogNormal(
                "upsilon_0",
                mu=self.prior.upsilon0_log_mu,
                sigma=self.prior.upsilon0_log_sigma,
            )
            g = pm.Normal(
                "g", mu=self.prior.g_mu, sigma=self.prior.g_sigma
            )
            lam = pm.Beta(
                "lam",
                alpha=self.prior.lambda_beta_a,
                beta=self.prior.lambda_beta_b,
            )
            sigma_obs = pm.HalfNormal("sigma_obs", sigma=self.sigma_obs_scale)
            # log Υ_t = log Υ_0 + t·log((1+g)·(1-λ))
            log_eff = pm.math.log((1.0 + g) * (1.0 - lam))
            mu_t = pm.math.log(upsilon_0) + t_arr * log_eff
            pm.Normal("obs", mu=mu_t, sigma=sigma_obs, observed=log_y)
        return model


# ─── Diagnostic helpers ────────────────────────────────────────────────────────


def _summary_diagnostics(idata: az.InferenceData) -> tuple[float, float, float]:
    """Return (rhat_max, ess_bulk_min, ess_tail_min) over posterior."""
    summary = az.summary(idata, kind="diagnostics")
    rhat_max = float(np.nanmax(summary["r_hat"].to_numpy()))
    ess_bulk_min = float(np.nanmin(summary["ess_bulk"].to_numpy()))
    ess_tail_min = float(np.nanmin(summary["ess_tail"].to_numpy()))
    return rhat_max, ess_bulk_min, ess_tail_min


def _pareto_k_stats(loo_obj: az.ELPDData) -> tuple[float, float]:
    """Return (pareto_k_max, pareto_k_high_frac) from arviz.loo output.

    ``loo_obj.pareto_k`` is a (n_obs,) DataArray. ``pareto_k_high_frac`` is
    the fraction of observations with k̂ ≥ PARETO_K_HIGH.
    """
    k_arr = np.asarray(loo_obj.pareto_k.values, dtype=np.float64)
    if k_arr.size == 0:
        return 0.0, 0.0
    k_finite = k_arr[np.isfinite(k_arr)]
    if k_finite.size == 0:
        return float("inf"), 1.0
    k_max = float(np.max(k_finite))
    high_frac = float(np.mean(k_finite >= PARETO_K_HIGH))
    return k_max, high_frac


def compute_rho_boundary_mass(idata: az.InferenceData) -> float:
    """Return P(|ρ| > RHO_BOUNDARY_TAIL_THRESHOLD | data) — Pin R4-bis.

    Used only for AR(1)-log fits. Reads ``idata.posterior['rho']`` and
    returns the empirical fraction of draws with |ρ| > 0.95.

    Raises:
        KeyError: if 'rho' is absent from idata.posterior.
    """
    rho_samples = np.asarray(idata["posterior"]["rho"].values).ravel()
    if rho_samples.size == 0:
        return 0.0
    finite = rho_samples[np.isfinite(rho_samples)]
    if finite.size == 0:
        return 1.0
    return float(np.mean(np.abs(finite) > RHO_BOUNDARY_TAIL_THRESHOLD))


def evaluate_gates(
    rhat_max: float,
    ess_bulk_min: float,
    ess_tail_min: float,
    n_chains: int,
    n_draws_per_chain: int,
    pareto_k_high_frac: float,
) -> bool:
    """Return True iff Pin R4 four conditions all pass.

    Pin R4: r̂ ≤ 1.01, ESS_bulk/tail ≥ 400, n_draws ≥ 4000 per chain
    AND chains ≥ 4, Pareto-k̂ HIGH-frac ≤ 0.05.
    """
    if not math.isfinite(rhat_max) or rhat_max > RHAT_GATE:
        return False
    if not math.isfinite(ess_bulk_min) or ess_bulk_min < ESS_GATE:
        return False
    if not math.isfinite(ess_tail_min) or ess_tail_min < ESS_GATE:
        return False
    if n_chains < CHAIN_FLOOR or n_draws_per_chain < DRAWS_PER_CHAIN_FLOOR:
        return False
    if pareto_k_high_frac > PARETO_K_HIGH_FRAC_GATE:
        return False
    return True


# ─── Form registry — Pin R6 closure guard ─────────────────────────────────────


# Module-level frozen registry: mapping form_name → builder class.
# Functions outside this module that try to register a fourth form must
# raise CandidateSetClosedError per Pin R6.
_BUILDER_REGISTRY: Final[Mapping[str, type]] = {
    "martingale": MartingaleModelBuilder,
    "ar1_log": Ar1LogModelBuilder,
    "det_churn": DetChurnModelBuilder,
}


def get_builder_class(form_name: str) -> type:
    """Return the builder class for a known form name.

    Raises:
        CandidateSetClosedError: if ``form_name`` is not in the closed
            Pin R1 set ``REVENUE_FORM_NAMES``.
    """
    if form_name not in _BUILDER_REGISTRY:
        raise CandidateSetClosedError(
            f"get_builder_class: form_name = {form_name!r}"
            f" not in closed candidate set {REVENUE_FORM_NAMES};"
            f" Pin R6 anti-fishing closure forbids 4th form."
        )
    return _BUILDER_REGISTRY[form_name]


def register_form(form_name: str, builder_cls: type) -> None:
    """Closed-set guard — always raises ``CandidateSetClosedError``.

    Pin R6 / spec §8(5): the candidate set is closed at three forms.
    Any attempt to register a fourth form is an anti-fishing violation
    and HALTs at construction time.
    """
    raise CandidateSetClosedError(
        f"register_form: candidate set is CLOSED at {REVENUE_FORM_NAMES}"
        f" per Pin R6; attempted to add {form_name!r} -> {builder_cls!r}"
    )


# ─── Fit driver Callable ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class FitDriver:
    """Run pm.sample on each of the three forms; emit RevenueFormFit per form.

    Pin R4 sim-count floor enforced: draws ≥ 4000, chains ≥ 4. Pointwise
    log-likelihood emitted via ``pm.compute_log_likelihood`` so that
    downstream ``arviz.compare(ic="loo")`` works.

    Pin R6: form registry is the closed module-level mapping; any attempt
    to inject a fourth form via :func:`register_form` raises
    :class:`CandidateSetClosedError`.

    LFO-CV branch (CORRECTIONS-α §15.3): off by default; ``cv_method``
    field on emitted ``RevenueFormFit`` records "loo" unless caller
    explicitly opts into LFO via ``self.cv_method == 'lfo'`` (which then
    delegates to ``arviz.loo`` with ``pointwise=True`` plus a check for
    LFO utilities; raises :class:`LfoCvUnavailableError` if absent).
    """

    draws: int = DRAWS_PER_CHAIN_FLOOR
    chains: int = CHAIN_FLOOR
    tune: int = 1000
    target_accept: float = 0.95
    seed: int = 20260508
    cv_method: CvMethod = "loo"

    def __post_init__(self) -> None:
        if self.draws < DRAWS_PER_CHAIN_FLOOR:
            raise ValueError(
                f"FitDriver.draws = {self.draws}"
                f" must be ≥ DRAWS_PER_CHAIN_FLOOR = {DRAWS_PER_CHAIN_FLOOR}"
                f" (Pin R4 floor)"
            )
        if self.chains < CHAIN_FLOOR:
            raise ValueError(
                f"FitDriver.chains = {self.chains}"
                f" must be ≥ CHAIN_FLOOR = {CHAIN_FLOOR} (Pin R4 floor)"
            )
        if not (0.0 < self.target_accept < 1.0):
            raise ValueError(
                f"FitDriver.target_accept = {self.target_accept}"
                f" must lie in (0, 1)"
            )
        # CR N3 v0.3 sweep: cv_method is now ``CvMethod`` Literal, so the
        # tuple-membership check below is now a defense-in-depth guard for
        # callers that bypass the type system (str injected at runtime).
        if self.cv_method not in ("loo", "lfo"):
            raise ValueError(
                f"FitDriver.cv_method = {self.cv_method!r}"
                f" must be 'loo' or 'lfo'"
            )

    def __call__(
        self,
        form_name: RevenueFormName,
        panel: UpsilonPanel,
        idata_path: str,
    ) -> tuple[az.InferenceData, RevenueFormFit]:
        """Fit one form; return (idata_with_log_lik, RevenueFormFit).

        Pin R6 enforced via :func:`get_builder_class`: unknown form_name
        raises :class:`CandidateSetClosedError` BEFORE any sampling work.
        """
        builder_cls = get_builder_class(form_name)
        builder = builder_cls()
        model = builder(panel)
        with model:
            idata = pm.sample(
                draws=self.draws,
                chains=self.chains,
                tune=self.tune,
                target_accept=self.target_accept,
                random_seed=self.seed,
                progressbar=False,
                idata_kwargs={"log_likelihood": True},
            )
        # CORRECTIONS-α v0.3 §15.7 (CR-S3 = MQ-FLAG-3 = RC-FLAG-3): the
        # previous fall-through branch tagged ``cv_method="lfo"`` while
        # silently emitting PSIS-LOO output — dishonest data provenance.
        # `arviz` lacks first-class forward-step LFO-CV utilities at this
        # release; the only honest behaviour is to HALT unconditionally
        # whenever LFO is requested (per CORRECTIONS-α §15.3 + the
        # `feedback_pathological_halt_anti_fishing_checkpoint` rule).
        if self.cv_method == "lfo":
            raise LfoCvUnavailableError(
                "FitDriver: cv_method='lfo' requested but arviz lacks"
                " first-class LFO-CV utilities; PSIS-LOO must NOT be"
                " silently relabelled as LFO. Foreground HALTs per"
                " CORRECTIONS-α §15.3."
            )
        # arviz.loo for k̂ stats (LOO branch only — LFO branch raised above).
        loo_result = az.loo(idata, pointwise=True)
        rhat_max, ess_bulk_min, ess_tail_min = _summary_diagnostics(idata)
        pareto_k_max, pareto_k_high_frac = _pareto_k_stats(loo_result)
        rho_boundary_mass: float | None = None
        if form_name == "ar1_log":
            rho_boundary_mass = compute_rho_boundary_mass(idata)
        gates_passed = evaluate_gates(
            rhat_max=rhat_max,
            ess_bulk_min=ess_bulk_min,
            ess_tail_min=ess_tail_min,
            n_chains=self.chains,
            n_draws_per_chain=self.draws,
            pareto_k_high_frac=pareto_k_high_frac,
        )
        fit = RevenueFormFit(
            form_name=form_name,
            idata_path=idata_path,
            rhat_max=rhat_max,
            ess_bulk_min=ess_bulk_min,
            ess_tail_min=ess_tail_min,
            n_chains=self.chains,
            n_draws_per_chain=self.draws,
            pareto_k_max=pareto_k_max,
            pareto_k_high_frac=pareto_k_high_frac,
            gates_passed=gates_passed,
            rho_boundary_mass=rho_boundary_mass,
            cv_method="loo",  # LFO branch raises before this point (§15.7)
        )
        return idata, fit


__all__ = [
    "Ar1LogModelBuilder",
    "CHAIN_FLOOR",
    "DRAWS_PER_CHAIN_FLOOR",
    "DetChurnModelBuilder",
    "ESS_GATE",
    "FitDriver",
    "MartingaleModelBuilder",
    "PARETO_K_HIGH",
    "PARETO_K_HIGH_FRAC_GATE",
    "RHAT_GATE",
    "compute_rho_boundary_mass",
    "evaluate_gates",
    "get_builder_class",
    "register_form",
]
