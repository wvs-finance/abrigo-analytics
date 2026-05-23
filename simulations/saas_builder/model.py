"""PyMC model factory for SAAS-COHORT-1 T1 (subscription-cap regime) fit.

Implements spec v1.1.1 §5.1 (T1) verbatim doubly-stochastic compound sum

    τ_t = Σ_{j=1}^{D_t} Σ_{i=1}^{N_j} τ_{j,i},      D_t ≈ 22

with per-active-day ``N_j ~ NegBin(μ, α=φ)`` (mean–dispersion form, MQ-B2)
and iid ``τ_{j,i} ~ TruncPareto(α, x_m, κ)`` (M1: α ≥ 1.5).

Tier-Categorical mixture over ``π ~ Dir([2.0, 5.0, 3.0])`` per spec §5.2.
**No Compound-Poisson cluster process** at the primary likelihood level —
that label belongs to spec §5.1 sensitivity arm (c) and is OUT OF SCOPE
for COHORT-1 (MQ-B3).

Pin enforcement at this layer:

- **M1 (α-floor 1.5):** prior shape is
  ``pm.TruncatedNormal(mu=2.0, sigma=0.25, lower=1.5, upper=2.5)``;
  upstream ``simulations.modules.samplers.TruncParetoSampler`` raises
  on α < 1.5 in the Callable layer (defense-in-depth).
- **M3 ($/MTok blended price):** the model imports
  :class:`simulations.modules.pricing.BlendedPriceFn` and
  :class:`simulations.types.fx.BlendedPriceParams`, constructs the
  Sonnet defaults ``(p_in=3.0, p_out=15.0, w_in=0.539, w_out=0.461,
  h_cache=0.95)``, *calls* the instance (``BlendedPriceFn`` is callable
  with no args) to obtain the blended scalar, and asserts via
  ``math.isclose(price, 7.1495, abs_tol=0.01)`` AT THE FACTORY CALL
  SITE (RC-B2: not in ``__post_init__``, which only validates the
  params struct). Drift here is a Phase-4 BLOCK.

Posterior-predictive emission surface (MQ-B4 + CORRECTIONS-α v0.2 → v0.3
+ v0.3 → v0.4 marginalization):

    The compound sum τ_t = Σ_j Σ_i τ_{j,i} is **NOT** representable as a
    PyTensor Deterministic over a fixed-shape per-turn TruncPareto tensor
    because per-day turn counts ``N_j`` are themselves random. Two
    posterior-predictive emissions are exposed:

    1. ``mean_tau_per_turn`` — Deterministic, used as the mean μ of the
       Stage-2 synthetic-Bayesian Normal-kernel proxy on the *fit* arm.
    2. ``tau_t_pp`` — produced **outside** the model graph by the emit
       pipeline (``simulations.saas_builder.emit.run_posterior_predictive``)
       which, for each posterior draw of ``(μ, φ, α, x_m, n_per_day)``,
       draws ``n_month = Σ n_per_day`` iid TruncPareto variates and reduces
       to τ_t. This is the spec §5.1 (T1) verbatim compound sum (BLOCK-1
       fix). Within-row per-turn variance is nonzero at fixed parameters.

    **CORRECTIONS-α v0.3 → v0.4 — tier_idx marginalization.** The per-
    builder Categorical latent ``tier_idx`` is REMOVED from the inference
    graph. Spec §5.2 "Categorical latent per builder" remains the data-
    generating model; integrating the latent out is exact (not an
    approximation) because the COHORT-1 likelihood does not condition on
    tier_idx (tier-conditional `(α_k, x_m,k, μ_k, φ_k)` is a future
    COHORT-2/3 enhancement; spec §5.4 sensitivity arms). The per-builder
    tier draws are recovered at posterior-predictive time by sampling
    ``tier_idx ~ Categorical(pi)`` numpy-side in
    :func:`simulations.saas_builder.emit.run_posterior_predictive`. This
    eliminates the v0.3 `CompoundStep + CategoricalGibbsMetropolis` over
    1000 latents that produced r̂_max=1.115, ESS_bulk_min=38, ESS_tail_min=58.

This file is the layer where PyMC enters the codebase. Imports are limited
to PyMC + the read-only Value/Callable upstream of cohort code.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final

import numpy as np
import pymc as pm
import pytensor.tensor as pt

from simulations.modules.pricing import BlendedPriceFn
from simulations.saas_builder.priors import (
    DIRICHLET_ALPHA_VECTOR,
    CohortPriors,
)
from simulations.types.fx import (
    BlendedPriceParams,
    DEFAULT_H_CACHE,
    DEFAULT_W_IN,
    DEFAULT_W_OUT,
    SONNET_PRICE_IN_USD_PER_MTOK,
    SONNET_PRICE_OUT_USD_PER_MTOK,
)

# ─── Math pin constants (spec §5.1, §5.2) ─────────────────────────────────────

#: Spec §5.1 closed-form Sonnet blended price expected value
#: ``0.539·3·(1 - 0.95 + 0.95·0.10) + 0.461·15 = 0.234 + 6.915 = 7.1495``.
M3_SONNET_BLENDED_PRICE_EXPECTED: Final[float] = 7.1495

#: Tolerance for the M3 assertion at the factory call site. Widened from
#: 0.0005 to 0.01 (RC-FLAG-1) to match spec §5.1 "≈ 7.15" precision.
M3_BLENDED_PRICE_ABS_TOL: Final[float] = 0.01

#: Default FX rate (X/Y) — COP/USD. Used for the q_t_cop deterministic.
#: Pinned at the spec §3 stationary mean ``X̄/Ȳ`` for COP/USD ≈ 4000 COP/USD.
DEFAULT_FX_COP_PER_USD: Final[float] = 4000.0

#: Spec §5.2 "Categorical latent per builder". Default cohort size for
#: the latent tier vector when no explicit ``n_builders`` is supplied.
#: Pinned at 1000 to match plan v0.3 CORRECTIONS-α §"BLOCK-5 fix".
DEFAULT_N_BUILDERS: Final[int] = 1000

#: Stage-2 synthetic-Bayesian Normal-kernel proxy noise scale. Pre-registered
#: in plan v0.3 CORRECTIONS-α §"BLOCK-2 fix" as a fixed positive scalar (NOT
#: stochastically tied to ``tau_t``). Documented as a static likelihood-proxy
#: hyperparameter; the §8(7) CI-width gate is the discriminator on parameter
#: shrinkage, not this scale.
SIGMA_OBS_FIXED: Final[float] = 1.0


def _build_sonnet_blended_price() -> float:
    """Construct the Sonnet-defaults BlendedPriceFn and return p_t.

    Side-effect-free; constructs ``BlendedPriceParams`` with spec §5.4
    Sonnet defaults, builds ``BlendedPriceFn``, calls it, asserts the
    return value is within ``M3_BLENDED_PRICE_ABS_TOL`` of the spec
    closed form, and returns the float.

    Asserted at *call site* per RC-B2 — not in ``__post_init__``,
    which validates the params struct, not a tier-conditioned numeric
    output.

    Contract:
        Preconditions:
            - The shipped ``simulations.types.fx`` constants
              ``DEFAULT_W_IN``, ``DEFAULT_W_OUT``, ``DEFAULT_H_CACHE``,
              ``SONNET_PRICE_IN_USD_PER_MTOK``,
              ``SONNET_PRICE_OUT_USD_PER_MTOK`` must be present and
              well-typed (Final floats). If a SIM-INFRA-0 follow-up
              renames or removes any, this raises ``ImportError`` at
              module load (caught by Phase 4 verification).
            - Caller is responsible for ensuring ``BlendedPriceFn`` and
              ``BlendedPriceParams`` are not monkey-patched in
              production paths; tests intentionally do this to verify
              the M3 BLOCK assertion fires.

        Raises:
            AssertionError: explicit, line ~108. Fires iff
                ``|price_per_mtok - 7.1495| > 0.01``. Caller (the
                ``T1ModelFactory.__call__`` site) surfaces this as a
                Phase-4 BLOCK and refuses to build the PyMC model.
            ValueError: from ``BlendedPriceParams.__post_init__`` if
                the constructed Sonnet defaults somehow violate the
                ``w_in + w_out == 1`` constraint (defensive — the
                module-level pinned constants satisfy it by design).
    """
    params = BlendedPriceParams(
        p_in=SONNET_PRICE_IN_USD_PER_MTOK,
        p_out=SONNET_PRICE_OUT_USD_PER_MTOK,
        w_in=DEFAULT_W_IN,
        w_out=DEFAULT_W_OUT,
        h_cache=DEFAULT_H_CACHE,
    )
    price_fn = BlendedPriceFn(params=params)
    price_per_mtok = price_fn()  # CALL the instance — no .price_per_mtok attr
    if not math.isclose(
        price_per_mtok,
        M3_SONNET_BLENDED_PRICE_EXPECTED,
        abs_tol=M3_BLENDED_PRICE_ABS_TOL,
    ):
        raise AssertionError(
            f"M3 BLOCK: BlendedPriceFn(Sonnet defaults)() ="
            f" {price_per_mtok!r} drifts from spec §5.1 closed form"
            f" {M3_SONNET_BLENDED_PRICE_EXPECTED} by"
            f" |Δ| = {abs(price_per_mtok - M3_SONNET_BLENDED_PRICE_EXPECTED)};"
            f" tolerance is abs_tol={M3_BLENDED_PRICE_ABS_TOL}."
        )
    return float(price_per_mtok)


@dataclass(frozen=True)
class T1ModelFactory:
    """Frozen-dc Callable building the spec §5.1 (T1) PyMC model.

    The factory holds the prior pin bundle and the FX rate; ``__call__``
    constructs and returns the ``pm.Model`` ready for ``pm.sample(...)``.
    Posterior-predictive Deterministics ``tau_t``, ``q_t_usd``, ``q_t_cop``
    are declared inside the model context so :mod:`emit` can populate them
    via ``pm.sample_posterior_predictive`` (MQ-B4).

    Attributes:
        priors: bundle of prior-hyperparameter Value containers.
        fx_cop_per_usd: stationary FX rate for ``q_t_cop = q_t_usd · FX``;
            default :data:`DEFAULT_FX_COP_PER_USD`.
        n_builders: cohort size — number of POST-HOC tier draws taken
            numpy-side at PP time per CORRECTIONS-α v0.4 marginalization.
            Spec §5.2 "Categorical latent per builder" remains the data-
            generating model; the latent is integrated out for inference
            and recovered at emission. Default :data:`DEFAULT_N_BUILDERS`.
        n_simulations: deprecated alias for legacy callers; ignored when
            ``n_builders`` is supplied. Retained as a frozen-dc field for
            backwards-compatible construction. Default 1.

    Behavior contract:

    - ``__call__`` returns a ``pm.Model`` context with the following
      named random variables and Deterministics:
        - ``mu`` — Lognormal-shape prior on per-active-day NegBin mean.
        - ``phi`` — HalfNormal prior on NegBin dispersion (PyMC ``alpha=``).
        - ``alpha_pareto`` — TruncatedNormal[1.5, 2.5] (M1).
        - ``x_m`` — HalfNormal prior on TruncPareto floor.
        - ``pi`` — Dirichlet([2.0, 5.0, 3.0]) over TIER_IDS (spec §5.2).
        - ``mean_n_month`` — Deterministic ``D_t · μ`` (E[N_month] under
          the marginalized NegBin); the actual ``n_month`` integer draw
          is produced post-hoc at PP time. CORRECTIONS-α v0.4 tertiary
          marginalization eliminates the discrete RV from the inference
          graph entirely; pure NUTS over (`pi`, `mu`, `phi`,
          `alpha_pareto`, `x_m`) only.
        - ``mean_tau_per_turn`` — Deterministic E[τ | α, x_m] (TruncPareto mean).
        - ``tau_t`` — Deterministic ``n_month × mean_tau_per_turn`` (used as
          the μ of the Stage-2 synthetic-Bayesian Normal-kernel proxy on the
          *fit* arm; **NOT** the spec §5.1 compound sum). The compound sum is
          built post-hoc by ``emit.run_posterior_predictive`` (BLOCK-1 fix).
        - **NO** ``tier_idx`` RV in the inference graph — the per-builder
          Categorical latent is marginalized out per CORRECTIONS-α v0.4
          (exact identity since likelihood does not condition on tier_idx
          in COHORT-1). Per-builder tier draws are produced numpy-side
          at PP time from posterior ``pi`` by
          :func:`simulations.saas_builder.emit.run_posterior_predictive`.
    - The Sonnet $/MTok closed form is asserted at construction
      (M3 BLOCK on drift > 0.01) before any pm.* node is built.
    - No imports from ``simulations.utils``.
    """

    priors: CohortPriors = field(default_factory=CohortPriors)
    fx_cop_per_usd: float = DEFAULT_FX_COP_PER_USD
    n_builders: int = DEFAULT_N_BUILDERS
    n_simulations: int = 1

    def __post_init__(self) -> None:
        # Validate FX rate (positive, finite). The M3 check belongs at
        # __call__ per RC-B2; only struct validation lives here.
        if not (math.isfinite(self.fx_cop_per_usd)
                and self.fx_cop_per_usd > 0.0):
            raise ValueError(
                f"T1ModelFactory.fx_cop_per_usd = {self.fx_cop_per_usd}"
                f" must be a finite float > 0"
            )
        if self.n_simulations <= 0:
            raise ValueError(
                f"T1ModelFactory.n_simulations = {self.n_simulations}"
                f" must be > 0"
            )
        if self.n_builders <= 0:
            raise ValueError(
                f"T1ModelFactory.n_builders = {self.n_builders}"
                f" must be > 0 (spec §5.2 — one latent tier per builder)"
            )

    def __call__(self, *, observed_tau_t: np.ndarray | None = None) -> pm.Model:
        """Build and return the spec §5.1 (T1) PyMC model.

        Args:
            observed_tau_t: optional 1-D array of observed monthly latent
                cost samples. If ``None`` (default), the model is purely
                generative — suitable for posterior-predictive sampling
                from the prior (Phase-2 Stage-2 synthetic-Bayesian fit
                per spec §8(8) sim-count floor). If provided, attached
                as ``observed=`` to the per-month ``tau_t`` Normal-shape
                likelihood (kernel approximation; the exact compound-sum
                likelihood is intractable in closed form — Stage-3 work).

        Returns:
            A ``pm.Model`` instance with random variables and posterior-
            predictive Deterministics declared per the behavior contract.

        Contract:
            Preconditions:
                - ``self.priors`` is a constructed :class:`CohortPriors`
                  (its ``__post_init__`` already enforced sub-prior
                  invariants including the M1 α-floor on
                  ``priors.alpha.alpha_lower``).
                - If ``observed_tau_t`` is supplied, it must be
                  reshape-able to 1-D ``float64``. ``observed_tau_t.ndim
                  != 1`` raises ``ValueError`` (explicit, line ~298).
                - The shipped ``BlendedPriceFn`` produces 7.1495 ± 0.01
                  on Sonnet defaults; M3 drift halts construction
                  before any PyMC node is created (see below).

            Raises:
                AssertionError: from :func:`_build_sonnet_blended_price`
                    if the shipped ``BlendedPriceFn`` Sonnet output drifts
                    beyond ``M3_BLENDED_PRICE_ABS_TOL``. Phase-4 BLOCK.
                ValueError: if ``observed_tau_t`` has ``ndim != 1``
                    (explicit guard).
                pymc.SamplingError / pytensor.* errors: NOT raised here —
                propagate at downstream ``pm.sample(...)`` time, not at
                model construction. Caller is responsible for handling.

            Silences: none. All exceptions propagate.
        """
        # M3 assertion at call site (RC-B2): fail fast before any PyMC
        # node creation if the shipped BlendedPriceFn drifts.
        price_per_mtok = _build_sonnet_blended_price()

        nb = self.priors.negbin
        ap = self.priors.alpha
        xp = self.priors.x_m
        d_t = self.priors.active_days_per_month

        with pm.Model() as model:
            # ─── Tier mixture (spec §5.2) ─────────────────────────────
            pi = pm.Dirichlet(
                "pi",
                a=np.array(DIRICHLET_ALPHA_VECTOR, dtype=np.float64),
            )

            # ─── NegBin (μ, φ) prior pin (MQ-B2) ──────────────────────
            # μ — Lognormal-shape: prior median at nb.mu_loc with log-σ.
            mu = pm.Lognormal(
                "mu",
                mu=math.log(nb.mu_loc),
                sigma=nb.mu_log_sigma,
            )
            # φ — HalfNormal centered near nb.phi_loc; expressed via
            # Truncated to keep φ > 0 with prior mean ≈ phi_loc.
            phi = pm.TruncatedNormal(
                "phi",
                mu=nb.phi_loc,
                sigma=nb.phi_sigma,
                lower=1.0,  # avoid pathological phi → 0
            )

            # ─── TruncPareto α + x_m priors (M1 floor) ────────────────
            alpha_pareto = pm.TruncatedNormal(
                "alpha_pareto",
                mu=ap.alpha_loc,
                sigma=ap.alpha_scale,
                lower=ap.alpha_lower,  # 1.5 — M1 floor
                upper=ap.alpha_upper,  # 2.5 — spec §5.2 bracket
            )
            x_m = pm.HalfNormal("x_m", sigma=xp.xm_sigma)

            # ─── Monthly NegBin turn count — FULLY MARGINALIZED ───────
            # CORRECTIONS-α v0.4 TERTIARY MARGINALIZATION: ``n_month`` is
            # the only remaining discrete latent in COHORT-1's graph
            # (after tier_idx and n_per_day were marginalized).  Direct
            # tests showed ``n_month`` Metropolis r̂=1.087 / ESS=60 at
            # 4000 draws/chain; coupling through ``mu`` (NegBin location)
            # dragged ``mu`` to r̂=1.086 / ESS=61 as well.  Since the
            # COHORT-1 likelihood does NOT condition on ``n_month``
            # (``observed_tau_t=None`` in production; ``tau_t`` Det
            # propagates n_month forward into emission only), the
            # ``n_month`` latent is integrated out exactly.  The post-
            # hoc draw at PP time uses ``rng.negative_binomial`` from
            # posterior ``(μ, φ)`` per the closed-form sum-of-iid
            # NegBin: ``n_month ~ NegBin(D_t·μ, D_t·φ)``.  This leaves
            # the inference graph fully continuous — pure NUTS, no
            # CompoundStep, no Metropolis.
            mean_n_month = pm.Deterministic(
                "mean_n_month", mu * float(d_t),
            )
            # Surface n_month as a Deterministic (E[N_month]) so the
            # downstream tau_t Deterministic compiles. The compound-sum
            # τ_t at emission time uses a fresh NegBin draw, NOT this
            # mean — the mean is the Stage-2 fit-arm proxy only.
            n_month = mean_n_month
            # phi reference (kept explicit since downstream PP-time draw
            # of n_month uses both mu and phi from the posterior).
            _ = phi

            # ─── Tokens-per-turn TruncPareto via PyMC Truncated wrapper ─
            # Spec §5.1 (T1) per-turn iid TruncPareto(α, x_m, κ).
            # Mean of TruncPareto(α, x_m, x_max), α > 1, equals
            #   E[X] = (α / (α-1)) · x_m · (1 - (x_m/x_max)^{α-1}) /
            #           (1 - (x_m/x_max)^α)
            # The deterministic monthly token total is (turns) × (mean per turn);
            # the doubly-stochastic monthly latent cost is therefore captured
            # by tau_t = n_month × E[τ_per_turn | α, x_m] for the mean-based
            # likelihood arm. Posterior-predictive draws will instead sample
            # n_month and per-turn variates explicitly via
            # pm.sample_posterior_predictive (MQ-B4).
            x_max = xp.x_max_fixed
            ratio = x_m / x_max
            ratio_pow_alpha = pt.pow(ratio, alpha_pareto)
            ratio_pow_alpha_minus_one = pt.pow(ratio, alpha_pareto - 1.0)
            mean_tau_per_turn = pm.Deterministic(
                "mean_tau_per_turn",
                (alpha_pareto / (alpha_pareto - 1.0))
                * x_m
                * (1.0 - ratio_pow_alpha_minus_one)
                / (1.0 - ratio_pow_alpha),
            )

            # τ_t monthly token total (Deterministic — populated by
            # pm.sample_posterior_predictive at emission time per MQ-B4).
            tau_t = pm.Deterministic(
                "tau_t",
                pt.cast(n_month, "float64") * mean_tau_per_turn,
            )

            # ─── q_t_usd / q_t_cop deterministic emission columns ─────
            # Cost-per-turn USD: (tokens) × ($/MTok) / 1e6. We use the
            # closed-form blended price (spec §5.1; M3 assertion above).
            q_t_usd = pm.Deterministic(
                "q_t_usd",
                tau_t * price_per_mtok / 1.0e6,
            )
            pm.Deterministic(
                "q_t_cop",
                q_t_usd * self.fx_cop_per_usd,
            )

            # If observed monthly cost is supplied, use a normal-kernel
            # likelihood centered on the deterministic τ_t mean, with
            # scale matched to the doubly-stochastic theoretical variance.
            # This is the Stage-2 synthetic-Bayesian likelihood proxy;
            # exact closed-form for Σ Σ TruncPareto is intractable.
            if observed_tau_t is not None:
                obs_arr = np.asarray(observed_tau_t, dtype=np.float64)
                if obs_arr.ndim != 1:
                    raise ValueError(
                        f"observed_tau_t must be 1-D; got shape {obs_arr.shape}"
                    )
                # BLOCK-2 fix (CORRECTIONS-α v0.3): replace stochastic
                # HalfNormal scale ``sigma=tau_t * 0.2 + 1.0`` (which was
                # malformed — passed a Deterministic random variable as a
                # HalfNormal scale, producing a non-identifiable nested
                # stochastic prior) with a fixed positive scalar pin
                # ``SIGMA_OBS_FIXED``. Pre-registered in plan v0.3
                # CORRECTIONS-α §"BLOCK-2 fix".
                pm.Normal(
                    "tau_t_observed",
                    mu=tau_t,
                    sigma=SIGMA_OBS_FIXED,
                    observed=obs_arr,
                )

            # CORRECTIONS-α v0.4: per-builder ``tier_idx`` Categorical
            # is MARGINALIZED OUT of the inference graph. The COHORT-1
            # likelihood does not condition on tier_idx, so integrating
            # the latent out is exact (not an approximation). Per-builder
            # tier draws are recovered at posterior-predictive time by
            # ``simulations.saas_builder.emit.run_posterior_predictive``
            # using ``rng.choice(3, p=pi_draw, size=n_builders)`` per
            # (chain, draw) cell. The v0.3 ``pm.Categorical`` over
            # ``n_builders=1000`` latents triggered ``CompoundStep +
            # CategoricalGibbsMetropolis`` and produced r̂=1.115 / ESS=38;
            # this branch eliminates the structural mixing failure.
            _ = pi  # pi is consumed at PP time; reference kept explicit.

        return model


__all__ = [
    "DEFAULT_FX_COP_PER_USD",
    "DEFAULT_N_BUILDERS",
    "M3_BLENDED_PRICE_ABS_TOL",
    "M3_SONNET_BLENDED_PRICE_EXPECTED",
    "SIGMA_OBS_FIXED",
    "T1ModelFactory",
]
