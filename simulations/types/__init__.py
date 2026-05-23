"""Value-tier package for ``simulations``.

Frozen-dataclass parameter containers, Protocols, TypeAliases, and Final
constants. See ``simulations/types/README.md`` for the contract.

Cross-tier consumers SHOULD prefer fully-qualified imports
(``from simulations.types.distributions import TruncParetoParams``) over
the curated re-exports below; the explicit ``__all__`` exists primarily for
discoverability and for the reality-checker tier-import grep.
"""

from simulations.types.distributions import (
    SAAS_TRUNC_PARETO_ALPHA_CEILING,
    SAAS_TRUNC_PARETO_ALPHA_FLOOR,
    SOFTPLUS_TIGHTNESS_EPS,
    SOFTPLUS_TIGHTNESS_GRID_N,
    NegBinParams,
    SoftplusParams,
    TruncParetoParams,
    neg_bin_mean,
    neg_bin_variance,
    tightness_l1_deviation,
    trunc_pareto_admits_saas_floor,
)
from simulations.types.fx import (
    CACHED_INPUT_DISCOUNT,
    DEFAULT_H_CACHE,
    DEFAULT_W_IN,
    DEFAULT_W_OUT,
    HAIKU_PRICE_IN_USD_PER_MTOK,
    HAIKU_PRICE_OUT_USD_PER_MTOK,
    OPUS_PRICE_IN_USD_PER_MTOK,
    OPUS_PRICE_OUT_USD_PER_MTOK,
    SONNET_PRICE_IN_USD_PER_MTOK,
    SONNET_PRICE_OUT_USD_PER_MTOK,
    BlendedPriceParams,
    FXPathParams,
    RealizedVarianceParams,
    fx_amplitude_envelope,
)
from simulations.types.posterior import (
    DEFAULT_CDF_PERCENTILES,
    DEFAULT_SCHEMA_VERSION,
    MonthlyCDF,
    PosteriorDraws,
    ZCapPinned,
    cdf_percentile_value,
    ci_95_width,
    n_total_draws,
    parameter_index,
)
from simulations.types.protocols import (
    AuditBlockHasher,
    PosteriorDrawsReader,
    PosteriorDrawsWriter,
    ZCapPinnedReader,
    ZCapPinnedWriter,
)
from simulations.types.tier import (
    DEFAULT_TIER_DIRICHLET_ALPHA,
    DEFAULT_TIER_PI,
    SUBSCRIPTION_USD_PER_MONTH,
    TIER_IDS,
    TierID,
    TierMap,
    TierPricing,
    TierPrior,
    categorical_mass,
    subscription_price_usd,
)

__all__: list[str] = [
    # tier
    "TIER_IDS",
    "TierID",
    "TierMap",
    "TierPrior",
    "TierPricing",
    "DEFAULT_TIER_PI",
    "DEFAULT_TIER_DIRICHLET_ALPHA",
    "SUBSCRIPTION_USD_PER_MONTH",
    "categorical_mass",
    "subscription_price_usd",
    # distributions
    "TruncParetoParams",
    "NegBinParams",
    "SoftplusParams",
    "SAAS_TRUNC_PARETO_ALPHA_FLOOR",
    "SAAS_TRUNC_PARETO_ALPHA_CEILING",
    "SOFTPLUS_TIGHTNESS_EPS",
    "SOFTPLUS_TIGHTNESS_GRID_N",
    "trunc_pareto_admits_saas_floor",
    "neg_bin_mean",
    "neg_bin_variance",
    "tightness_l1_deviation",
    # fx
    "FXPathParams",
    "RealizedVarianceParams",
    "BlendedPriceParams",
    "DEFAULT_W_IN",
    "DEFAULT_W_OUT",
    "DEFAULT_H_CACHE",
    "CACHED_INPUT_DISCOUNT",
    "SONNET_PRICE_IN_USD_PER_MTOK",
    "SONNET_PRICE_OUT_USD_PER_MTOK",
    "OPUS_PRICE_IN_USD_PER_MTOK",
    "OPUS_PRICE_OUT_USD_PER_MTOK",
    "HAIKU_PRICE_IN_USD_PER_MTOK",
    "HAIKU_PRICE_OUT_USD_PER_MTOK",
    "fx_amplitude_envelope",
    # posterior
    "PosteriorDraws",
    "MonthlyCDF",
    "ZCapPinned",
    "DEFAULT_SCHEMA_VERSION",
    "DEFAULT_CDF_PERCENTILES",
    "n_total_draws",
    "parameter_index",
    "cdf_percentile_value",
    "ci_95_width",
    # protocols
    "PosteriorDrawsReader",
    "PosteriorDrawsWriter",
    "ZCapPinnedReader",
    "ZCapPinnedWriter",
    "AuditBlockHasher",
]
