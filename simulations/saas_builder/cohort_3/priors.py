"""Prior hyperparameter Value containers for SAAS-COHORT-3 Υ_t fits.

Pure Value tier — no PyMC import; PyMC distributions are instantiated
downstream in ``models.py``.

Pin coverage:

- Pin R1: martingale σ_ε ~ HalfNormal(s_ε); AR(1)-log ρ ~ Normal(0, 0.5)
  truncated to |ρ|<1, σ_ε ~ HalfNormal(s_ε); det+churn Υ_0 ~ LogNormal,
  g ~ Normal(μ_g, σ_g), λ ~ Beta(a, b).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

# ─── Module-level constants — Pin R1 prior pins ───────────────────────────────

#: Martingale σ_ε prior scale — HalfNormal scale parameter.
#: Anchored at order-of-magnitude of monthly Υ_t variation in COP.
MARTINGALE_SIGMA_EPSILON_SCALE: Final[float] = 1.0e6

#: AR(1)-log ρ prior — Normal(0, AR1_RHO_PRIOR_SIGMA) truncated to (-1, 1).
AR1_RHO_PRIOR_MU: Final[float] = 0.0
AR1_RHO_PRIOR_SIGMA: Final[float] = 0.5

#: AR(1)-log σ_ε prior scale — HalfNormal on log-scale residuals.
AR1_LOG_SIGMA_EPSILON_SCALE: Final[float] = 0.5

#: Det+churn Υ_0 prior — LogNormal(μ, σ) on initial revenue level (COP).
DET_CHURN_UPSILON0_LOG_MU: Final[float] = 14.0  # log(~1.2M COP)
DET_CHURN_UPSILON0_LOG_SIGMA: Final[float] = 1.0

#: Det+churn growth g prior — Normal(μ_g, σ_g).
DET_CHURN_G_PRIOR_MU: Final[float] = 0.05
DET_CHURN_G_PRIOR_SIGMA: Final[float] = 0.10

#: Det+churn churn λ prior — Beta(a, b). Spec v1.2.1 §6.1 pin:
#: λ ~ Beta(4.5, 95.5), mean = 0.045, concentration α+β = 100, anchored
#: on SURVEY.md citation-5 (4.5% midpoint prosumer monthly churn).
#: Spec v1.2.1 §15.4 routes Task 0.2b NON-NO-OP re-fit at this prior;
#: previous v0.3 setting Beta(2.0, 38.0) (mean 0.05, conc. 40) is
#: NOT equivalent — see §15.7 FLAG-A/B.
DET_CHURN_LAMBDA_BETA_A: Final[float] = 4.5
DET_CHURN_LAMBDA_BETA_B: Final[float] = 95.5


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MartingalePrior:
    """Prior pins for the martingale Υ_t form.

    Validation contract:

    - ``sigma_epsilon_scale > 0``.
    """

    sigma_epsilon_scale: float = MARTINGALE_SIGMA_EPSILON_SCALE

    def __post_init__(self) -> None:
        if not (math.isfinite(self.sigma_epsilon_scale)
                and self.sigma_epsilon_scale > 0.0):
            raise ValueError(
                f"MartingalePrior.sigma_epsilon_scale ="
                f" {self.sigma_epsilon_scale} must be a finite float > 0"
            )


@dataclass(frozen=True)
class Ar1LogPrior:
    """Prior pins for the AR(1)-log Υ_t form.

    ``rho ~ TruncatedNormal(rho_mu, rho_sigma, lower=-1, upper=1)``.
    ``sigma_epsilon ~ HalfNormal(sigma_epsilon_scale)``.

    Validation contract:

    - ``rho_sigma > 0`` and ``-1 < rho_mu < 1``.
    - ``sigma_epsilon_scale > 0``.
    """

    rho_mu: float = AR1_RHO_PRIOR_MU
    rho_sigma: float = AR1_RHO_PRIOR_SIGMA
    sigma_epsilon_scale: float = AR1_LOG_SIGMA_EPSILON_SCALE

    def __post_init__(self) -> None:
        if not math.isfinite(self.rho_mu):
            raise ValueError(f"Ar1LogPrior.rho_mu = {self.rho_mu} must be finite")
        if not (-1.0 < self.rho_mu < 1.0):
            raise ValueError(
                f"Ar1LogPrior.rho_mu = {self.rho_mu} must lie in (-1, 1)"
            )
        if not (math.isfinite(self.rho_sigma) and self.rho_sigma > 0.0):
            raise ValueError(
                f"Ar1LogPrior.rho_sigma = {self.rho_sigma}"
                f" must be a finite float > 0"
            )
        if not (math.isfinite(self.sigma_epsilon_scale)
                and self.sigma_epsilon_scale > 0.0):
            raise ValueError(
                f"Ar1LogPrior.sigma_epsilon_scale = {self.sigma_epsilon_scale}"
                f" must be a finite float > 0"
            )


@dataclass(frozen=True)
class DetChurnPrior:
    """Prior pins for the deterministic + churn Υ_t form.

    ``Υ_0 ~ LogNormal(log_mu, log_sigma)``.
    ``g ~ Normal(g_mu, g_sigma)``.
    ``λ ~ Beta(beta_a, beta_b)``.

    Validation contract:

    - ``log_sigma > 0``, ``g_sigma > 0``.
    - ``beta_a > 0``, ``beta_b > 0``.
    """

    upsilon0_log_mu: float = DET_CHURN_UPSILON0_LOG_MU
    upsilon0_log_sigma: float = DET_CHURN_UPSILON0_LOG_SIGMA
    g_mu: float = DET_CHURN_G_PRIOR_MU
    g_sigma: float = DET_CHURN_G_PRIOR_SIGMA
    lambda_beta_a: float = DET_CHURN_LAMBDA_BETA_A
    lambda_beta_b: float = DET_CHURN_LAMBDA_BETA_B

    def __post_init__(self) -> None:
        for name, value in (
            ("upsilon0_log_mu", self.upsilon0_log_mu),
            ("g_mu", self.g_mu),
        ):
            if not math.isfinite(value):
                raise ValueError(
                    f"DetChurnPrior.{name} = {value} must be finite"
                )
        for name, value in (
            ("upsilon0_log_sigma", self.upsilon0_log_sigma),
            ("g_sigma", self.g_sigma),
            ("lambda_beta_a", self.lambda_beta_a),
            ("lambda_beta_b", self.lambda_beta_b),
        ):
            if not (math.isfinite(value) and value > 0.0):
                raise ValueError(
                    f"DetChurnPrior.{name} = {value} must be a finite float > 0"
                )


__all__ = [
    "AR1_LOG_SIGMA_EPSILON_SCALE",
    "AR1_RHO_PRIOR_MU",
    "AR1_RHO_PRIOR_SIGMA",
    "DET_CHURN_G_PRIOR_MU",
    "DET_CHURN_G_PRIOR_SIGMA",
    "DET_CHURN_LAMBDA_BETA_A",
    "DET_CHURN_LAMBDA_BETA_B",
    "DET_CHURN_UPSILON0_LOG_MU",
    "DET_CHURN_UPSILON0_LOG_SIGMA",
    "MARTINGALE_SIGMA_EPSILON_SCALE",
    "Ar1LogPrior",
    "DetChurnPrior",
    "MartingalePrior",
]
