"""Callable-tier package for ``simulations``.

Frozen-dataclass + ``__call__`` stateless transforms. Configuration lives in
fields; logic lives in ``__call__``. Imports allowed from
:mod:`simulations.types` only — no IO, no sibling Callable instances at
construction time (composition happens via passing arrays/values, not
class instances).

See ``simulations/modules/README.md`` for the contract and decomposition.
"""

from simulations.modules.fx_path import (
    FXPathGen,
    RealizedVarianceCalc,
    epsilon_from_sigma_T,
)
from simulations.modules.pricing import BlendedPriceFn
from simulations.modules.regularizers import SoftplusRegularizer
from simulations.modules.samplers import (
    NegBinSampler,
    TierMixCategorical,
    TruncParetoSampler,
)

__all__: list[str] = [
    # fx_path
    "FXPathGen",
    "RealizedVarianceCalc",
    "epsilon_from_sigma_T",
    # samplers
    "TruncParetoSampler",
    "NegBinSampler",
    "TierMixCategorical",
    # regularizers
    "SoftplusRegularizer",
    # pricing
    "BlendedPriceFn",
]
