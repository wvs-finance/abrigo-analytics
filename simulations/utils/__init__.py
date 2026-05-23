"""IO Boundary tier package for ``simulations``.

Per the functional-python skill, this is the **only** tier where
``class Foo: def __init__(...)`` (mutable-state-admitting) constructs
live. Everything here either:

- reads / writes parquet files honouring the M4 column schemas;
- reads / writes JSON files honouring the M4 ``Z_cap_pinned.json``
  field set;
- computes deterministic sha256 audit-block digests over file contents;
- emits the spec §5.2 frozen pricing table.

Cross-tier consumers SHOULD prefer fully-qualified imports
(``from simulations.utils.parquet_io import SyntheticTauWriter``) over
the curated re-exports below.
"""

from simulations.utils.audit_block import (
    AuditBlockHasher,
    compute_audit_block,
)
from simulations.utils.errors import SchemaMismatchError
from simulations.utils.json_io import (
    Z_CAP_PINNED_FIELDS,
    AuditReader,
    ZCapPinnedReader,
    ZCapPinnedWriter,
)
from simulations.utils.parquet_io import (
    COHORT_PRIOR_COLUMNS,
    SYNTHETIC_TAU_COLUMNS,
    SYNTHETIC_TAU_PARTITION_COLS,
    CohortPriorReader,
    CohortPriorRow,
    CohortPriorWriter,
    SyntheticTauReader,
    SyntheticTauRow,
    SyntheticTauWriter,
    cohort_prior_row,
    synthetic_tau_row,
)
from simulations.utils.pricing_fetcher import StaticPricingFetcher

__all__: list[str] = [
    # errors
    "SchemaMismatchError",
    # audit-block
    "AuditBlockHasher",
    "compute_audit_block",
    # parquet IO
    "COHORT_PRIOR_COLUMNS",
    "SYNTHETIC_TAU_COLUMNS",
    "SYNTHETIC_TAU_PARTITION_COLS",
    "CohortPriorRow",
    "SyntheticTauRow",
    "CohortPriorReader",
    "CohortPriorWriter",
    "SyntheticTauReader",
    "SyntheticTauWriter",
    "cohort_prior_row",
    "synthetic_tau_row",
    # JSON IO
    "Z_CAP_PINNED_FIELDS",
    "AuditReader",
    "ZCapPinnedReader",
    "ZCapPinnedWriter",
    # pricing
    "StaticPricingFetcher",
]
