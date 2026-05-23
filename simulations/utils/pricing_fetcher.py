"""Static Anthropic-pricing-table fetcher (placeholder IO boundary).

This module exists to keep the **liveness** of pricing data pinned at an
IO boundary even when the source-of-truth is the spec §5.2 frozen table.
Live HTTP fetching of `https://www.anthropic.com/pricing` is intentionally
*not* implemented in SIM-INFRA-0 (untestable in CI; brittle to rendering
changes). Instead, the spec §5.2 pins live in
``simulations.types.fx`` as ``Final`` constants and this class merely
re-emits them as ``CohortPriorRow`` records suitable for parquet-IO
consumption.

If a future iteration needs live fetching, the contract is: replace this
class with one that returns the same ``CohortPriorRow`` shape; downstream
code does not change.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Final

from simulations.types.fx import (
    HAIKU_PRICE_IN_USD_PER_MTOK,
    HAIKU_PRICE_OUT_USD_PER_MTOK,
    OPUS_PRICE_IN_USD_PER_MTOK,
    OPUS_PRICE_OUT_USD_PER_MTOK,
    SONNET_PRICE_IN_USD_PER_MTOK,
    SONNET_PRICE_OUT_USD_PER_MTOK,
)
from simulations.types.posterior import DEFAULT_SCHEMA_VERSION
from simulations.utils.parquet_io import CohortPriorRow, cohort_prior_row

#: Static citation for the pricing snapshot.
_PRICING_SOURCE: Final[str] = "spec_v1.1.1_§5.2"


class StaticPricingFetcher:
    """Emit the spec §5.2 frozen pricing table as ``CohortPriorRow`` records.

    Constructed without arguments. ``__call__`` returns a deterministic
    six-row list (in/out × {Sonnet, Opus, Haiku}) pinned at the
    construction-time UTC timestamp.
    """

    _fetched_at_utc: str

    def __init__(self, fetched_at_utc: str | None = None) -> None:
        self._fetched_at_utc = (
            fetched_at_utc
            if fetched_at_utc is not None
            else datetime.now(timezone.utc).isoformat(timespec="seconds")
        )

    def __call__(self) -> list[CohortPriorRow]:
        """Return six ``CohortPriorRow`` records — spec §5.2 frozen pricing.

        Pure with respect to the construction-time ``fetched_at_utc``
        timestamp; no IO performed. The "fetcher" name is aspirational —
        a future iteration may replace this class with a live HTTP fetcher
        that returns the same ``CohortPriorRow`` shape.

        Contract:
            Preconditions:
                - None. The function is total: spec §5.2 ``Final``
                  constants are imported at module load and cannot drift.

            Raises:
                None — the function does not validate (constants are
                pinned at module-import time; row construction is a
                straightforward dict literal).
        """
        ts = self._fetched_at_utc
        prices: list[tuple[str, float]] = [
            ("sonnet_price_in_usd_per_mtok", SONNET_PRICE_IN_USD_PER_MTOK),
            ("sonnet_price_out_usd_per_mtok", SONNET_PRICE_OUT_USD_PER_MTOK),
            ("opus_price_in_usd_per_mtok", OPUS_PRICE_IN_USD_PER_MTOK),
            ("opus_price_out_usd_per_mtok", OPUS_PRICE_OUT_USD_PER_MTOK),
            ("haiku_price_in_usd_per_mtok", HAIKU_PRICE_IN_USD_PER_MTOK),
            ("haiku_price_out_usd_per_mtok", HAIKU_PRICE_OUT_USD_PER_MTOK),
        ]
        return [
            cohort_prior_row(
                param=name,
                percentile="P50",
                value=float(value),
                source=_PRICING_SOURCE,
                fetched_at_utc=ts,
                schema_version=DEFAULT_SCHEMA_VERSION,
            )
            for (name, value) in prices
        ]
