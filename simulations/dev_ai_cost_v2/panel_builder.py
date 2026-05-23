"""modules-tier pure function: ``JSONLReadResult`` → ``DailyNotionalPanel``.

Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.3
§3.3 (daily aggregation), §3.5 (panel contract), §0.1 CORRECTIONS-V
(``is_error`` dropped, UTC half-open), CORRECTIONS-M (forward-fill forbidden),
§0.3 CORRECTIONS-Y-2/-Y-5a/-Y-5b/-Y-6.

Tier rule: ``modules/`` may import ``types/`` (and the sibling pure-callable
``anthropic_pricing``) but NOT ``utils/`` nor ``_errors``. This function is
pure: no IO, no mutation of inputs, no module-level state.

Weekday-filter semantics
------------------------
``polars`` 1.40 returns ``dt.weekday()`` as Mon=1..Sun=7 (ISO-8601 ordinal),
whereas the stdlib ``datetime.weekday()`` returns Mon=0..Sun=6. These two
conventions are NOT interchangeable; the filter constants below are different
on each side of the join on purpose:

    * python record side: ``< 5`` excludes Sat=5, Sun=6 (correct: keep Mon-Fri).
    * polars TRM side:    ``<= 5`` excludes Sat=6, Sun=7 (correct: keep Mon-Fri).

A unit test fixes both conventions against known calendar dates to prevent
silent regression on a polars version bump.

Float arithmetic (CORRECTIONS-Y-2 / v0.2.3)
-------------------------------------------
All monetary arithmetic is ``float`` (ccusage parity within 0.1%); v0.2.1
``Decimal`` exactness has been retired. The per-message ``cost_usd`` column
is constructed from ``MessageRecord.cost_usd_notional`` (float, computed
upstream by ``PricingTable.__call__``); polars preserves ``Float64`` dtype
through ``group_by`` sums and ``with_columns`` multiplications.

Y-6 ephemeral π̂ diagnostic
---------------------------
``ephemeral_pi_share = Σ cache_create_1h / Σ (cache_create_5m + cache_create_1h)``
across the WHOLE panel (single scalar, broadcast as a constant column).
If the denominator is zero, the share is 0.0. Bounded ``[0, 1]``.
"""
from __future__ import annotations

import polars as pl

from simulations.dev_ai_cost_v2.anthropic_pricing import PricingTable
from simulations.dev_ai_cost_v2.types import (
    EXPECTED_PANEL_SCHEMA,
    DailyNotionalPanel,
    JSONLReadResult,
    MessageRecord,
)


# ─── Per-message empty-frame schema ──────────────────────────────────────────
#
# Schema for the per-message DataFrame when ``records`` is empty (or after
# ``is_error`` filtering leaves no rows). Keeping this constant ensures the
# downstream ``group_by``/``join`` pipeline is dtype-stable regardless of
# input cardinality. v0.2.3: ``cost_usd`` is Float64 (Y-2 ccusage parity).

_MSG_FRAME_SCHEMA: dict[str, pl.DataType] = {
    "date_utc": pl.Date,
    "weekday": pl.Int8,
    "cost_usd": pl.Float64,
    "input_tok": pl.Int64,
    "output_tok": pl.Int64,
    "cache_create_5m": pl.Int64,
    "cache_create_1h": pl.Int64,
    "cache_read": pl.Int64,
}


def _compute_ephemeral_pi_share(records: tuple[MessageRecord, ...]) -> float:
    """Y-6: ``Σ cache_create_1h / Σ (cache_create_5m + cache_create_1h)``.

    If denominator == 0, returns 0.0. Single scalar across the panel.
    """
    sum_1h: int = sum(r.cache_create_1h for r in records)
    sum_5m: int = sum(r.cache_create_5m for r in records)
    denom: int = sum_5m + sum_1h
    if denom == 0:
        return 0.0
    return sum_1h / denom


def build_daily_panel(
    read_result: JSONLReadResult,
    pricing: PricingTable,
    trm_panel: pl.DataFrame,
) -> DailyNotionalPanel:
    """Aggregate ``JSONLReadResult`` records to a daily UTC panel joined with TRM.

    Contract:
        * ``is_error=True`` rows are DROPPED from cost aggregation; their
          count is surfaced as ``DailyNotionalPanel.dropped_error_count``
          (spec CORRECTIONS-V).
        * Weekends (Sat/Sun) are dropped on BOTH sides before the inner
          join; per-message weekend drops are counted in
          ``dropped_weekend_message_count`` (message unit) and per-TRM-row
          weekend drops are counted in ``dropped_weekend_trm_row_count``
          (row unit) (spec §3.5; v0.2.10 audit-econ #10 split).
        * TRM-missing weekday days (Claude active, no Banrep TRM quote —
          e.g. Colombian holiday Mondays) are dropped by the inner join.
          The day-level count is surfaced as
          ``dropped_trm_missing_weekday_count`` (v0.2.10 audit-econ #1).
          This is a DESIGN CHOICE: forward-fill is FORBIDDEN per spec §6
          (forward-filling would smuggle FX volatility into idle days).
          The counter exposes the magnitude rather than papering over it.
        * Forward-fill is FORBIDDEN: a UTC date that lacks a source row on
          EITHER side does NOT appear in the output.
        * All arithmetic is ``float`` (ccusage parity per Y-2).
        * Y-5a + v0.2.4 Y-7 + v0.2.5 Y-8 counter threading: 3 PricingTable
          counters + 3 JSONLReader counters (``dropped_non_assistant_count``,
          ``dropped_malformed_line_count``, ``dropped_duplicate_count``)
          are surfaced into the panel for DATA_PROVENANCE.
        * Y-6 ``ephemeral_pi_share`` computed across all records (single
          scalar, broadcast as a constant Float64 column).

    Args:
        read_result: ``JSONLReadResult`` produced by ``JSONLReader``.
            Carries the JSONLReader-side ``dropped_non_assistant_count``
            counter per Y-5a.
        pricing: ``PricingTable`` — provides the 3 modules-tier counters
            (``WARN_missing_keys_count``, ``dropped_unknown_model_count``,
            ``multiple_substring_match_warning``) per Y-5a. Cost is already
            pre-computed on each ``MessageRecord.cost_usd_notional`` at
            parse time; the table is threaded through here for counter
            access and signature parity with the CLI orchestrator.
        trm_panel: daily Banrep TRM panel with columns ``date`` (``pl.Date``)
            and ``trm_cop_per_usd`` (``pl.Float64``). Both weekday and
            weekend rows are accepted; weekends are filtered internally.

    Returns:
        ``DailyNotionalPanel`` with ``df`` matching ``EXPECTED_PANEL_SCHEMA``
        and all 6 counters + ``ephemeral_pi_share`` populated.

    Raises:
        ValueError: propagated from ``DailyNotionalPanel.__post_init__`` if
            the final DataFrame schema diverges from
            ``EXPECTED_PANEL_SCHEMA``.

    Errors silenced:
        None. Dropped rows (weekends, ``is_error``, inner-join misses,
        non-assistant rows) are all accounted for explicitly via the
        panel-level counters.
    """
    records: tuple[MessageRecord, ...] = read_result.records

    # ── Phase 1: split errors from kept rows ──────────────────────────────
    dropped_error: int = sum(1 for r in records if r.is_error)
    kept: list[MessageRecord] = [r for r in records if not r.is_error]

    # ── Phase 2: build per-message frame (dtype-stable on empty) ─────────
    if kept:
        rows = [
            {
                "date_utc": r.ts.date(),
                "weekday": r.ts.weekday(),
                "cost_usd": float(r.cost_usd_notional),
                "input_tok": r.input_tok,
                "output_tok": r.output_tok,
                "cache_create_5m": r.cache_create_5m,
                "cache_create_1h": r.cache_create_1h,
                "cache_read": r.cache_read,
            }
            for r in kept
        ]
        msg_df = pl.DataFrame(rows, schema=_MSG_FRAME_SCHEMA)
    else:
        msg_df = pl.DataFrame(schema=_MSG_FRAME_SCHEMA)

    # ── Phase 3: count and drop weekend records ───────────────────────────
    weekend_records: int = msg_df.filter(pl.col("weekday") >= 5).height
    weekday_msg = msg_df.filter(pl.col("weekday") < 5)

    # ── Phase 4: group-by-date aggregation (Float64) ─────────────────────
    daily = weekday_msg.group_by("date_utc").agg(
        [
            pl.col("cost_usd").sum().alias("notional_cost_usd"),
            pl.col("input_tok").sum(),
            pl.col("output_tok").sum(),
            pl.col("cache_create_5m").sum(),
            pl.col("cache_create_1h").sum(),
            pl.col("cache_read").sum(),
            pl.len().cast(pl.Int64).alias("n_messages"),
        ]
    )

    # ── Phase 5: weekend filter on TRM side ──────────────────────────────
    trm_weekday = trm_panel.filter(pl.col("date").dt.weekday() <= 5).rename(
        {"date": "date_utc"}
    )
    # Ensure trm_cop_per_usd is Float64 (Y-2): cast if it arrives as Decimal
    # or another numeric dtype from upstream.
    if trm_weekday.schema.get("trm_cop_per_usd") != pl.Float64:
        trm_weekday = trm_weekday.with_columns(
            pl.col("trm_cop_per_usd").cast(pl.Float64)
        )
    weekend_trm: int = trm_panel.height - trm_weekday.height

    # ── Phase 6: inner join (forward-fill forbidden) ─────────────────────
    pre_join_daily_height: int = daily.height
    joined = daily.join(trm_weekday, on="date_utc", how="inner")

    # USD → COP conversion under Float64.
    joined = joined.with_columns(
        (pl.col("notional_cost_usd") * pl.col("trm_cop_per_usd")).alias(
            "notional_cost_cop"
        )
    )

    # Y-6 π̂ broadcast as constant column.
    pi_share: float = _compute_ephemeral_pi_share(records)
    joined = joined.with_columns(
        pl.lit(pi_share, dtype=pl.Float64).alias("ephemeral_pi_share")
    )

    # Final column ordering/selection to match ``EXPECTED_PANEL_SCHEMA`` exactly.
    joined = joined.select(list(EXPECTED_PANEL_SCHEMA.keys()))

    # ── Phase 7: dropped-rows accounting (v0.2.10 audit-econ #10 split) ──
    # Three named counters — each pins ONE unit. The day-level counter
    # surfaces holiday-Monday-style drops (audit-econ finding #1).
    trm_missing_weekday: int = pre_join_daily_height - joined.height

    return DailyNotionalPanel(
        df=joined,
        dropped_weekend_message_count=int(weekend_records),
        dropped_weekend_trm_row_count=int(weekend_trm),
        dropped_trm_missing_weekday_count=int(trm_missing_weekday),
        dropped_error_count=int(dropped_error),
        dropped_non_assistant_count=read_result.dropped_non_assistant_count,
        dropped_malformed_line_count=read_result.dropped_malformed_line_count,
        warn_missing_keys_count=pricing.WARN_missing_keys_count,
        dropped_unknown_model_count=pricing.dropped_unknown_model_count,
        multiple_substring_match_warning=pricing.multiple_substring_match_warning,
        ephemeral_pi_share=pi_share,
        dropped_duplicate_count=read_result.dropped_duplicate_count,
        dropped_non_anthropic_count=read_result.dropped_non_anthropic_count,
    )


__all__ = ["build_daily_panel"]
