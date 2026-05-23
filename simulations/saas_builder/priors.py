"""Prior hyperparameter Value containers for SAAS-COHORT-1 T1 fit.

Pure Value tier (frozen-dataclass + ``__post_init__`` validators); no PyMC
import — PyMC distributions are instantiated downstream in ``model.py``.

Pin coverage (plan v0.2 Phase-2 prelude):

- **M1 α-floor (spec §8(6)).** :class:`TruncParetoAlphaPrior` carries the
  bracket ``[1.5, 2.5]`` (verbatim spec §5.2) and a TruncatedNormal
  (μ=2.0, σ=0.25) shape, lower-bounded at 1.5. ``__post_init__`` rejects
  any prior whose lower bound dips below 1.5 (FLAG-A: prior MUST place
  100% mass on ``[1.5, ∞)``).
- **NegBin (μ, φ) parameterization (MQ-B2).** :class:`NegBinTurnsPrior`
  carries (μ_loc, μ_scale, phi_loc, phi_scale) for the *PyMC* layer's
  ``pm.NegativeBinomial(mu=μ, alpha=φ)`` mean–dispersion form. The
  hyperparameter pin is μ ≈ 80 (turns/active-day median; spec §5.2
  line 318) with φ targeted to deliver over-dispersion ratio
  ``Var/μ = 1 + μ/φ ≈ 2.3`` — i.e. ``φ ≈ 80 / 1.3 ≈ 61.5`` — pinned
  here at the prior-mean scalar :data:`PHI_TARGET_MEAN`.

  **Reparameterization to shipped Value-tier ``NegBinParams(r, p)``.**
  When a (μ, φ) draw is consumed downstream by
  :class:`simulations.modules.samplers.NegBinSampler` (which reads
  ``NegBinParams(r, p)``), the canonical map is::

      r = φ
      p = φ / (φ + μ)

  Reverse map: ``μ = r·(1-p)/p``, ``Var = r·(1-p)/p²`` (matches
  :func:`simulations.types.distributions.neg_bin_mean` /
  :func:`~simulations.types.distributions.neg_bin_variance` exactly).
- **Dirichlet tier prior (spec §5.2).** :class:`TierDirichletPrior`
  carries the literal vector ``[2.0, 5.0, 3.0]`` ( = 10·[0.20, 0.50, 0.30]).
  ``__post_init__`` asserts elementwise via ``math.isclose(rel_tol=1e-12)``
  per MQ-FLAG-B (floating-point literal vs. computed-product equality).
- **TruncPareto x_m prior.** :class:`TruncParetoXmPrior` carries the
  (loc, scale) of the half-normal-style positive prior on ``x_m`` (tokens),
  with tight informative bounds since spec §5.2 anchors x_m at "tens of
  tokens" floor.

Composition pattern: :class:`CohortPriors` wires all four sub-priors into
one frozen-dc container that ``model.py`` consumes in a single call.

Spec anchors:
    Spec v1.1.1 §5.1 (T1 doubly-stochastic compound sum); §5.2 (tier
    prior α₀ = 10·[0.20, 0.50, 0.30] + over-dispersion p90/mean ≈ 2.3×);
    §8(6) (α-floor 1.5).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final

from simulations.types.distributions import (
    SAAS_TRUNC_PARETO_ALPHA_CEILING,
    SAAS_TRUNC_PARETO_ALPHA_FLOOR,
)
from simulations.types.tier import (
    DEFAULT_TIER_DIRICHLET_ALPHA,
    DEFAULT_TIER_PI,
    TIER_IDS,
    TierID,
)

# ─── Module-level constants ───────────────────────────────────────────────────

#: Spec §5.2 line 194 — turns / active-day median target μ (NegBin mean).
NEGBIN_MU_PRIOR_LOC: Final[float] = 80.0

#: Half-width of the lognormal-shape μ prior, expressed as a sigma on log(μ).
#: Tight enough to keep posterior mean within order-of-magnitude of 80,
#: loose enough that the posterior may shrink toward data.
NEGBIN_MU_PRIOR_LOG_SIGMA: Final[float] = 0.25

#: Spec §5.2 line 318 — over-dispersion p90/mean ≈ 2.3× anchor. With
#: NegBin Var = μ + μ²/φ, the dispersion ratio Var/μ = 1 + μ/φ. Solving
#: 1 + 80/φ = 2.3 gives φ ≈ 61.5; pinned at 60.0 for a round prior mean.
PHI_TARGET_MEAN: Final[float] = 60.0

#: Spec §5.2 over-dispersion ratio anchor (Var/μ = 1 + μ/φ).
NEGBIN_OVERDISPERSION_RATIO_TARGET: Final[float] = 2.3

#: Half-width of the half-normal-shape φ prior.
NEGBIN_PHI_PRIOR_SIGMA: Final[float] = 20.0

#: Spec §5.1 (T1) per-month active-day count anchor (D_t ≈ 22).
ACTIVE_DAYS_PER_MONTH: Final[int] = 22

#: Spec §5.2 TruncPareto α prior — TruncatedNormal(μ=2.0, σ=0.25,
#: lower=1.5, upper=2.5) per FLAG-A. The bracket [1.5, 2.5] is verbatim
#: spec §5.2; the (2.0, 0.25) location/scale centers the mass squarely
#: in-bracket and keeps cusp behavior away from the lower boundary.
TRUNCPARETO_ALPHA_PRIOR_MU: Final[float] = 2.0
TRUNCPARETO_ALPHA_PRIOR_SIGMA: Final[float] = 0.25

#: TruncPareto x_m prior — half-normal(σ=10) in tokens. Spec §5.2 anchors
#: x_m at "tens of tokens"; the half-normal places ~99% mass in (0, 30).
TRUNCPARETO_XM_PRIOR_SIGMA: Final[float] = 10.0

#: TruncPareto x_max (truncation κ in spec §5.1 (T1)) — pinned at the
#: subscription-tier-cap regime entry token-count proxy. Spec §5.2 anchors
#: this at the "Pro 5h auto-compact" threshold ≈ 200_000 input tokens;
#: per-turn x_max well below that (this is per-turn, not per-month).
TRUNCPARETO_XMAX_FIXED: Final[float] = 5000.0

#: Dirichlet concentration α₀ vector — literal numeric form
#: ``10 · [0.20, 0.50, 0.30] = [2.0, 5.0, 3.0]`` per spec §5.2.
DIRICHLET_ALPHA_VECTOR: Final[tuple[float, float, float]] = (2.0, 5.0, 3.0)


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class NegBinTurnsPrior:
    """(μ, φ) prior pin for ``pm.NegativeBinomial(mu=μ, alpha=φ)``.

    Consumed by :func:`simulations.saas_builder.model.build_t1_model` to
    construct the per-active-day turn-count latent. The mean–dispersion
    parameterization (μ, φ) is required by MQ-B2; ``r``-``p`` form is
    derived at the boundary with downstream ``NegBinParams`` consumers
    via ``r = φ``, ``p = φ / (φ + μ)``.

    Spec §5.2 anchors:
    - μ ≈ 80 (turns/active-day median; line 318).
    - p90/mean ≈ 2.3× ⇒ φ ≈ μ / 1.3 ≈ 61.5; pinned mean PHI_TARGET_MEAN.

    Validation contract:

    - ``mu_loc > 0``, ``mu_log_sigma > 0`` (lognormal-shape prior on μ).
    - ``phi_loc > 0``, ``phi_sigma > 0`` (half-normal-shape prior on φ).
    """

    mu_loc: float = NEGBIN_MU_PRIOR_LOC
    mu_log_sigma: float = NEGBIN_MU_PRIOR_LOG_SIGMA
    phi_loc: float = PHI_TARGET_MEAN
    phi_sigma: float = NEGBIN_PHI_PRIOR_SIGMA

    def __post_init__(self) -> None:
        if not (math.isfinite(self.mu_loc) and self.mu_loc > 0.0):
            raise ValueError(
                f"NegBinTurnsPrior.mu_loc = {self.mu_loc} must be a finite float > 0"
            )
        if not (math.isfinite(self.mu_log_sigma) and self.mu_log_sigma > 0.0):
            raise ValueError(
                f"NegBinTurnsPrior.mu_log_sigma = {self.mu_log_sigma}"
                f" must be a finite float > 0"
            )
        if not (math.isfinite(self.phi_loc) and self.phi_loc > 0.0):
            raise ValueError(
                f"NegBinTurnsPrior.phi_loc = {self.phi_loc} must be a finite float > 0"
            )
        if not (math.isfinite(self.phi_sigma) and self.phi_sigma > 0.0):
            raise ValueError(
                f"NegBinTurnsPrior.phi_sigma = {self.phi_sigma}"
                f" must be a finite float > 0"
            )


@dataclass(frozen=True)
class TruncParetoAlphaPrior:
    """Lower-bounded TruncatedNormal prior on TruncPareto α (M1 floor).

    Implements the FLAG-A pin: ``pm.TruncatedNormal(mu=2.0, sigma=0.25,
    lower=1.5, upper=2.5)``. The lower bound ``alpha_lower`` is constrained
    at construction time to be ``>= SAAS_TRUNC_PARETO_ALPHA_FLOOR`` (= 1.5);
    the upper bound is constrained to be ``<= SAAS_TRUNC_PARETO_ALPHA_CEILING``
    (= 2.5).

    Spec §8(6) requires α ≥ 1.5 dual-enforced: this Bayesian level
    (priors.py) AND the sampler-construction level
    (:class:`simulations.modules.samplers.TruncParetoSampler` raises on
    α < 1.5). Both must hold; either alone is insufficient defense-in-depth.

    Validation contract:

    - ``alpha_lower >= SAAS_TRUNC_PARETO_ALPHA_FLOOR`` (= 1.5).
    - ``alpha_upper <= SAAS_TRUNC_PARETO_ALPHA_CEILING`` (= 2.5).
    - ``alpha_lower < alpha_upper``.
    - ``alpha_loc`` ∈ ``(alpha_lower, alpha_upper)``.
    - ``alpha_scale > 0``.
    """

    alpha_loc: float = TRUNCPARETO_ALPHA_PRIOR_MU
    alpha_scale: float = TRUNCPARETO_ALPHA_PRIOR_SIGMA
    alpha_lower: float = SAAS_TRUNC_PARETO_ALPHA_FLOOR
    alpha_upper: float = SAAS_TRUNC_PARETO_ALPHA_CEILING

    def __post_init__(self) -> None:
        if not (math.isfinite(self.alpha_lower)):
            raise ValueError(
                f"TruncParetoAlphaPrior.alpha_lower = {self.alpha_lower}"
                f" must be finite"
            )
        if self.alpha_lower < SAAS_TRUNC_PARETO_ALPHA_FLOOR:
            raise ValueError(
                f"TruncParetoAlphaPrior.alpha_lower = {self.alpha_lower}"
                f" must be ≥ SAAS_TRUNC_PARETO_ALPHA_FLOOR ="
                f" {SAAS_TRUNC_PARETO_ALPHA_FLOOR} per spec §8(6)"
            )
        if not math.isfinite(self.alpha_upper):
            raise ValueError(
                f"TruncParetoAlphaPrior.alpha_upper = {self.alpha_upper}"
                f" must be finite"
            )
        if self.alpha_upper > SAAS_TRUNC_PARETO_ALPHA_CEILING:
            raise ValueError(
                f"TruncParetoAlphaPrior.alpha_upper = {self.alpha_upper}"
                f" must be ≤ SAAS_TRUNC_PARETO_ALPHA_CEILING ="
                f" {SAAS_TRUNC_PARETO_ALPHA_CEILING} per spec §5.2 bracket"
            )
        if not (self.alpha_lower < self.alpha_upper):
            raise ValueError(
                f"TruncParetoAlphaPrior: alpha_lower ({self.alpha_lower})"
                f" must be < alpha_upper ({self.alpha_upper})"
            )
        if not (math.isfinite(self.alpha_loc) and
                self.alpha_lower < self.alpha_loc < self.alpha_upper):
            raise ValueError(
                f"TruncParetoAlphaPrior.alpha_loc = {self.alpha_loc}"
                f" must lie in ({self.alpha_lower}, {self.alpha_upper})"
            )
        if not (math.isfinite(self.alpha_scale) and self.alpha_scale > 0.0):
            raise ValueError(
                f"TruncParetoAlphaPrior.alpha_scale = {self.alpha_scale}"
                f" must be a finite float > 0"
            )


@dataclass(frozen=True)
class TruncParetoXmPrior:
    """Half-normal-shape prior on TruncPareto ``x_m`` (tokens-per-turn floor).

    Validation contract:

    - ``xm_sigma > 0`` (half-normal scale).
    - ``x_max_fixed > 0`` (truncation cap κ per spec §5.1 (T1)).
    """

    xm_sigma: float = TRUNCPARETO_XM_PRIOR_SIGMA
    x_max_fixed: float = TRUNCPARETO_XMAX_FIXED

    def __post_init__(self) -> None:
        if not (math.isfinite(self.xm_sigma) and self.xm_sigma > 0.0):
            raise ValueError(
                f"TruncParetoXmPrior.xm_sigma = {self.xm_sigma}"
                f" must be a finite float > 0"
            )
        if not (math.isfinite(self.x_max_fixed) and self.x_max_fixed > 0.0):
            raise ValueError(
                f"TruncParetoXmPrior.x_max_fixed = {self.x_max_fixed}"
                f" must be a finite float > 0"
            )


@dataclass(frozen=True)
class TierDirichletPrior:
    """Dirichlet prior on tier mixture π (spec §5.2).

    Carries ``α₀_vector = [2.0, 5.0, 3.0]`` ( = 10·[0.20, 0.50, 0.30],
    indexed by ``TIER_IDS = ("pro", "max_5x", "max_20x")``). ``__post_init__``
    asserts elementwise via ``math.isclose(rel_tol=1e-12)`` (MQ-FLAG-B fix
    — floating-point literal vs. computed-product equality).

    The hyperparameter is fixed; no hierarchical hyperprior in COHORT-1
    (deferred to a future iteration if posterior-predictive checks fail).

    Validation contract:

    - ``alpha_vector`` length matches ``len(TIER_IDS)`` (= 3).
    - Each ``alpha_vector[i]`` ``isclose`` to the literal numeric vector
      ``DIRICHLET_ALPHA_VECTOR[i]`` within ``rel_tol=1e-12``.
    - ``concentration`` (= ``sum(alpha_vector)``) ``isclose`` to 10.0
      within ``rel_tol=1e-12``.
    - Implied mean π = ``alpha_vector / concentration`` matches
      ``DEFAULT_TIER_PI`` mass-by-mass within ``rel_tol=1e-12``.
    """

    alpha_vector: tuple[float, float, float] = DIRICHLET_ALPHA_VECTOR
    concentration: float = DEFAULT_TIER_DIRICHLET_ALPHA

    def __post_init__(self) -> None:
        if len(self.alpha_vector) != len(TIER_IDS):
            raise ValueError(
                f"TierDirichletPrior.alpha_vector length"
                f" {len(self.alpha_vector)} must equal len(TIER_IDS) ="
                f" {len(TIER_IDS)}"
            )
        # Elementwise isclose vs. literal pin (MQ-FLAG-B).
        for i, a in enumerate(self.alpha_vector):
            if not math.isfinite(a) or a <= 0.0:
                raise ValueError(
                    f"TierDirichletPrior.alpha_vector[{i}] = {a}"
                    f" must be a finite float > 0"
                )
            target = DIRICHLET_ALPHA_VECTOR[i]
            if not math.isclose(a, target, rel_tol=1e-12, abs_tol=0.0):
                raise ValueError(
                    f"TierDirichletPrior.alpha_vector[{i}] = {a}"
                    f" not isclose to spec §5.2 literal {target}"
                    f" (rel_tol=1e-12)"
                )
        # Concentration sum must be 10.0 within rel_tol=1e-12.
        total = sum(self.alpha_vector)
        if not math.isclose(total, 10.0, rel_tol=1e-12, abs_tol=0.0):
            raise ValueError(
                f"TierDirichletPrior: sum(alpha_vector) = {total}"
                f" not isclose to spec §5.2 concentration 10.0"
                f" (rel_tol=1e-12)"
            )
        if not math.isclose(self.concentration, total,
                            rel_tol=1e-12, abs_tol=0.0):
            raise ValueError(
                f"TierDirichletPrior.concentration = {self.concentration}"
                f" must isclose to sum(alpha_vector) = {total}"
            )
        # Implied mean π must match DEFAULT_TIER_PI for each tier.
        for tier_id, a in zip(TIER_IDS, self.alpha_vector):
            implied = a / total
            target_pi = DEFAULT_TIER_PI[tier_id]
            if not math.isclose(implied, target_pi,
                                rel_tol=1e-12, abs_tol=0.0):
                raise ValueError(
                    f"TierDirichletPrior implied π[{tier_id!r}] = {implied}"
                    f" not isclose to DEFAULT_TIER_PI[{tier_id!r}] ="
                    f" {target_pi} (rel_tol=1e-12)"
                )


@dataclass(frozen=True)
class CohortPriors:
    """Bundled prior pins for the SAAS-COHORT-1 T1 fit.

    One frozen-dc container for the four sub-priors consumed by
    :func:`simulations.saas_builder.model.build_t1_model`.

    Spec anchors: §5.1, §5.2, §8(6) — see individual sub-prior docstrings.
    """

    negbin: NegBinTurnsPrior = field(default_factory=NegBinTurnsPrior)
    alpha: TruncParetoAlphaPrior = field(default_factory=TruncParetoAlphaPrior)
    x_m: TruncParetoXmPrior = field(default_factory=TruncParetoXmPrior)
    tier: TierDirichletPrior = field(default_factory=TierDirichletPrior)
    active_days_per_month: int = ACTIVE_DAYS_PER_MONTH

    def __post_init__(self) -> None:
        if self.active_days_per_month <= 0:
            raise ValueError(
                f"CohortPriors.active_days_per_month ="
                f" {self.active_days_per_month} must be > 0"
            )


# ─── Free-function accessors ──────────────────────────────────────────────────


def negbin_mu_phi_to_r_p(mu: float, phi: float) -> tuple[float, float]:
    """Reparameterize PyMC ``NegativeBinomial(mu, alpha=φ)`` to ``NegBinParams(r, p)``.

    Canonical map per Phase-2 prelude MQ-B2:

        r = φ
        p = φ / (φ + μ)

    Reverse-checks: ``r·(1-p)/p = μ`` and ``r·(1-p)/p² = μ + μ²/φ``,
    matching :func:`simulations.types.distributions.neg_bin_mean` and
    :func:`~simulations.types.distributions.neg_bin_variance` exactly.

    Args:
        mu: mean of the per-active-day turn-count distribution (> 0).
        phi: dispersion (PyMC ``alpha=`` argument; > 0). Smaller φ ⇒ heavier
            over-dispersion.

    Returns:
        ``(r, p)`` pair satisfying the shipped ``NegBinParams`` validation
        contract (``r > 0`` and ``0 < p < 1``).

    Raises:
        ValueError: if ``mu <= 0`` or ``phi <= 0``.
    """
    if not (math.isfinite(mu) and mu > 0.0):
        raise ValueError(f"negbin_mu_phi_to_r_p: mu = {mu} must be > 0")
    if not (math.isfinite(phi) and phi > 0.0):
        raise ValueError(f"negbin_mu_phi_to_r_p: phi = {phi} must be > 0")
    r = phi
    p = phi / (phi + mu)
    return r, p


def tier_id_at_index(idx: int) -> TierID:
    """Return the ``TierID`` at position ``idx`` of ``TIER_IDS``.

    Helper for converting Categorical posterior column indices back to
    spec-pinned tier names. ``idx`` must be ``0``, ``1``, or ``2``.

    Raises:
        IndexError: if ``idx`` is out of range (chained from tuple
            indexing).
    """
    return TIER_IDS[idx]


__all__ = [
    "ACTIVE_DAYS_PER_MONTH",
    "DIRICHLET_ALPHA_VECTOR",
    "NEGBIN_MU_PRIOR_LOC",
    "NEGBIN_MU_PRIOR_LOG_SIGMA",
    "NEGBIN_OVERDISPERSION_RATIO_TARGET",
    "NEGBIN_PHI_PRIOR_SIGMA",
    "PHI_TARGET_MEAN",
    "TRUNCPARETO_ALPHA_PRIOR_MU",
    "TRUNCPARETO_ALPHA_PRIOR_SIGMA",
    "TRUNCPARETO_XMAX_FIXED",
    "TRUNCPARETO_XM_PRIOR_SIGMA",
    "CohortPriors",
    "NegBinTurnsPrior",
    "TierDirichletPrior",
    "TruncParetoAlphaPrior",
    "TruncParetoXmPrior",
    "negbin_mu_phi_to_r_p",
    "tier_id_at_index",
]
