"""Types tier for dev_ai_cost_v2 — frozen-dataclass value containers.

Tier-import rule: ``types/`` imports neither ``modules/`` nor ``utils/`` from
the dev_ai_cost_v2 sub-package. Polars is a value-tier-admissible dependency
(it is a pure data-container library, not an IO boundary).

Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.4 §3.5
+ §0.3 CORRECTIONS-Y-5a/-Y-5b/-Y-2 + Y-6 + §0.4 CORRECTIONS-Y-7.

Sibling spec ref: ``docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md``
v0.1.3 CORRECTIONS-RR/-TT adds the ``uuid: str`` field on ``MessageRecord``
(per-JSONL-line uuid from the Anthropic Claude Code schema). The field is
required for R6 pool canonicalization (tertiary sort key + same-path
dedupe tiebreaker); an empty uuid would make the sort ambiguous and is
therefore rejected at construction.

v0.2.3 changes (Task 9.5):
  - CORRECTIONS-Y-2: ``cost_usd_notional`` is ``float`` (ccusage parity).
    ``DailyNotionalPanel`` monetary cols are ``pl.Float64``.
  - Y-5b: ``JSONLReadResult`` defined here (types-tier) carrying
    ``records: tuple[MessageRecord, ...]`` and
    ``dropped_non_assistant_count: int``.
  - Y-5a: ``DailyNotionalPanel`` carries the 4 PricingTable counters and
    the 1 JSONLReader counter as audit-visible scalars.
  - Y-6: ``ephemeral_pi_share`` column + scalar attached to the panel.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

import polars as pl


# ─── EXPECTED_PANEL_SCHEMA ────────────────────────────────────────────────────
#
# Pinned schema for ``DailyNotionalPanel.df``. Validated in __post_init__.
# CORRECTIONS-Y-2: monetary columns are ``pl.Float64`` (ccusage parity
# semantics; supersedes v0.2.1 ``pl.Decimal``). Y-6: panel carries
# ``ephemeral_pi_share`` as a scalar broadcast across all rows (single value
# per panel build — the share is a global diagnostic, not per-date).

EXPECTED_PANEL_SCHEMA: dict[str, pl.DataType] = {
    "date_utc": pl.Date,
    "notional_cost_usd": pl.Float64,
    "notional_cost_cop": pl.Float64,
    "trm_cop_per_usd": pl.Float64,
    "input_tok": pl.Int64,
    "output_tok": pl.Int64,
    "cache_create_5m": pl.Int64,
    "cache_create_1h": pl.Int64,
    "cache_read": pl.Int64,
    "n_messages": pl.Int64,
    "ephemeral_pi_share": pl.Float64,
}


# ─── MessageRecord ────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class MessageRecord:
    """A single parsed assistant message from a Claude Code JSONL session log.

    Fields:
        ts: timezone-aware UTC datetime (ms-precision from Anthropic JSONL).
            ``tz-naive`` and non-UTC tz inputs are rejected.
        model: Anthropic model identifier (e.g., ``"claude-sonnet-4-5"``).
        input_tok: standard input token count (``≥ 0``).
        output_tok: standard output token count (``≥ 0``).
        cache_create_5m: ``cache_creation.ephemeral_5m_input_tokens`` from the
            Anthropic JSONL ``usage`` block (``≥ 0``).
        cache_create_1h: ``cache_creation.ephemeral_1h_input_tokens`` from the
            Anthropic JSONL ``usage`` block (``≥ 0``).
        cache_read: ``cache_read_input_tokens`` from the Anthropic JSONL
            ``usage`` block (``≥ 0``).
        cost_usd_notional: rate-card USD cost computed at parse time by
            ``PricingTable`` (``float`` per CORRECTIONS-Y-2; ccusage parity;
            ``≥ 0`` and finite — NaN/inf rejected).
        session_id: Claude Code ``sessionId`` (groups messages within a
            session).
        request_id: Anthropic ``requestId``; ``None`` on legacy Claude Code
            (pre-2.0). ``JSONLReader`` emits a warning when ``None`` is
            observed but does not error.
        is_error: ``True`` if the assistant message was an error response.
        uuid: per-JSONL-line UUID. Either Anthropic-emitted or
            ``"synth-sha256:..."`` per Y-5e (R6 canonicalization gates on
            the prefix). Required non-empty for R6 pool canonicalization
            (CORRECTIONS-RR/-TT).

    Raises:
        ValueError: if ``ts`` is tz-naive or non-UTC; if any token field is
            negative; if ``cost_usd_notional`` is negative, NaN, or infinite;
            if ``uuid`` is empty.
    """

    ts: datetime
    model: str
    input_tok: int
    output_tok: int
    cache_create_5m: int
    cache_create_1h: int
    cache_read: int
    cost_usd_notional: float
    session_id: str
    request_id: str | None
    is_error: bool
    uuid: str  # R6 v0.1.3 CORRECTIONS-RR/-TT

    def __post_init__(self) -> None:
        # tz-awareness + UTC-offset check. ``timezone.utc`` and any
        # ``timezone(timedelta(0))`` both pass (offset == zero).
        if self.ts.tzinfo is None or self.ts.utcoffset() != timezone.utc.utcoffset(self.ts):
            raise ValueError(
                f"MessageRecord.ts must be timezone-aware UTC; got {self.ts!r}"
            )
        for fname in (
            "input_tok",
            "output_tok",
            "cache_create_5m",
            "cache_create_1h",
            "cache_read",
        ):
            v: int = getattr(self, fname)
            if v < 0:
                raise ValueError(f"MessageRecord.{fname} must be >= 0; got {v}")
        if not math.isfinite(self.cost_usd_notional):
            raise ValueError(
                f"MessageRecord.cost_usd_notional must be finite (no NaN/inf); "
                f"got {self.cost_usd_notional}"
            )
        if self.cost_usd_notional < 0:
            raise ValueError(
                f"MessageRecord.cost_usd_notional must be >= 0; got {self.cost_usd_notional}"
            )
        if not self.uuid:
            raise ValueError(
                "MessageRecord.uuid must be non-empty (required by R6 canonicalization)"
            )


# ─── TokensByCategory ─────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TokensByCategory:
    """Token counts per Anthropic billing category; consumed by
    ``PricingTable.__call__``.

    The five categories correspond to LiteLLM pricing keys at
    SHA ``e58a561c`` (the canonical pricing snapshot pinned by the
    dev_ai_cost_v2 sub-package):

    - ``input``           → ``input_cost_per_token`` (200k tier applied
      inside ``PricingTable.__call__`` per CORRECTIONS-Y-2)
    - ``output``          → ``output_cost_per_token``
    - ``cache_create_5m`` → ``cache_creation_input_token_cost`` (5m default)
    - ``cache_create_1h`` → aggregated with ``cache_create_5m`` inside
      ``PricingTable.__call__`` body per CR-Z-3 / Y-5c (the 5m+1h sum is
      multiplied by the single ``cache_creation_input_token_cost`` rate).
    - ``cache_read``      → ``cache_read_input_token_cost``

    **IMMUTABILITY (Y-5c / CR-Z-3)**: ``__init__`` does NOT mutate the
    inputs. The split is preserved intact so diagnostic notebooks can
    consume the ephemeral 5m vs 1h breakdown; cost aggregation happens
    only inside ``PricingTable.__call__``.

    Raises:
        ValueError: if any field is negative.
    """

    input: int
    output: int
    cache_create_5m: int
    cache_create_1h: int
    cache_read: int

    def __post_init__(self) -> None:
        for fname in (
            "input",
            "output",
            "cache_create_5m",
            "cache_create_1h",
            "cache_read",
        ):
            v: int = getattr(self, fname)
            if v < 0:
                raise ValueError(f"TokensByCategory.{fname} must be >= 0; got {v}")


# ─── JSONLReadResult ──────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class JSONLReadResult:
    """Result of one ``JSONLReader.__call__`` invocation (Y-5b / CR-Z-2).

    Lives in the **types tier** (Y-5b): both ``modules`` (panel_builder)
    and ``utils`` (jsonl_io) consume this container; types-tier placement
    keeps the import topology acyclic.

    Fields:
        records: materialized tuple of parsed assistant ``MessageRecord``
            instances (immutable, hashable). Tuple chosen over ``Sequence``
            here to enforce types-tier immutability convention; downstream
            consumers iterate freely without exhausting the container.
        dropped_non_assistant_count: number of JSONL rows skipped because
            ``type != "assistant"`` (Y-5a counter ownership pin —
            JSONLReader-side counter, not PricingTable-side).
        dropped_malformed_line_count: v0.2.4 Y-7 — number of JSONL lines
            silently skipped because ``json.loads`` raised
            ``json.JSONDecodeError`` (filesystem partial-write corruption,
            trailing null-byte blocks, truncated JSON). The skip is
            scope-limited to JSON-syntax failures; Pydantic schema errors
            on valid JSON still raise ``JSONLSchemaError``.
        dropped_duplicate_count: v0.2.5 Y-8 — number of JSONL rows
            collapsed by the OSS-mirror uniqueHash dedup discipline
            (``${message.id}:${requestId}`` → keep-largest-tokenTotal,
            with ``hasSpeed`` tiebreaker on equal totals). Increments on
            EVERY collision of a previously-seen ``_unique_hash``,
            whether the new row supersedes the kept entry (replacement)
            or is discarded. Equivalently:
            ``dropped_duplicate_count == raw_assistant_rows_admitted -
            len(records)``. Rows whose ``message.id`` is None bypass the
            dedup map entirely and do NOT increment this counter (per
            spec §0.5 CR optional-7th / RC FLAG-B).
        dropped_non_anthropic_count: v0.2.10 audit-econ #9 — number of
            assistant JSONL rows skipped because ``message.model`` is
            ``None`` or does not start with ``claude-`` (case-insensitive).
            The operator's ``~/.claude/projects/`` tree contains both
            Claude Code AND OpenAI Codex / other-vendor sessions; admitting
            non-Anthropic rows inflated downstream token aggregates at
            cost=0 (PricingTable's ladder returned 0 for unknown models).
            The filter moves UPSTREAM to JSONLReader so non-Anthropic
            tokens never enter the panel at all. Tokens AND cost are both
            excluded.

    Counter ownership (Y-5a): this container carries ONLY the
    JSONLReader-side counters (``dropped_non_assistant_count``,
    ``dropped_malformed_line_count``, ``dropped_duplicate_count``,
    ``dropped_non_anthropic_count``). The PricingTable-side counters
    (``WARN_missing_keys_count``, ``dropped_unknown_model_count``,
    ``multiple_substring_match_warning``) live on ``PricingTable`` and are
    surfaced into ``DailyNotionalPanel`` by the panel-builder.

    Raises:
        ValueError: if ``dropped_non_assistant_count``,
            ``dropped_malformed_line_count``,
            ``dropped_duplicate_count``, or
            ``dropped_non_anthropic_count`` is negative.
    """

    records: tuple[MessageRecord, ...]
    dropped_non_assistant_count: int
    dropped_malformed_line_count: int
    dropped_duplicate_count: int
    dropped_non_anthropic_count: int

    def __post_init__(self) -> None:
        if self.dropped_non_assistant_count < 0:
            raise ValueError(
                f"JSONLReadResult.dropped_non_assistant_count must be >= 0; "
                f"got {self.dropped_non_assistant_count}"
            )
        if self.dropped_malformed_line_count < 0:
            raise ValueError(
                f"JSONLReadResult.dropped_malformed_line_count must be >= 0; "
                f"got {self.dropped_malformed_line_count}"
            )
        if self.dropped_duplicate_count < 0:
            raise ValueError(
                f"JSONLReadResult.dropped_duplicate_count must be >= 0; "
                f"got {self.dropped_duplicate_count}"
            )
        if self.dropped_non_anthropic_count < 0:
            raise ValueError(
                f"JSONLReadResult.dropped_non_anthropic_count must be >= 0; "
                f"got {self.dropped_non_anthropic_count}"
            )


# ─── DailyNotionalPanel ───────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class DailyNotionalPanel:
    """Frozen-dc wrapper over a polars ``DataFrame`` holding the daily
    notional cost panel (one row per UTC date).

    The wrapper itself is frozen; the inner ``DataFrame`` is *not* (an
    acknowledged threat in spec v0.2.1 §6). Consumers should treat ``df``
    as read-only or call ``.clone()`` before mutation.

    Schema is validated in ``__post_init__`` against
    ``EXPECTED_PANEL_SCHEMA``: missing columns, extra columns, and wrong
    dtypes all raise ``ValueError`` with a descriptive message identifying
    the offending column(s).

    v0.2.10 counter split (audit-econ finding #10 + #1):
      The previous single ``dropped_rows_count`` aggregated three
      different units (message-level + TRM-row-level + day-level) into
      one scalar. It is removed and replaced by three named counters
      that each pin one unit. The day-level counter
      ``dropped_trm_missing_weekday_count`` surfaces Colombian-holiday
      Mondays — weekdays where Claude was active but Banrep published
      no TRM row (audit-econ finding #1). No forward-fill: TRM-missing
      weekday drops are a DESIGN CHOICE (spec §6 forward-fill-forbidden
      invariant). The counter exposes the magnitude.

    v0.2.3 counters per Y-5a + Y-6 + v0.2.10 split:
      - ``dropped_weekend_message_count``: per-MESSAGE count of records
        whose UTC date falls on Sat/Sun (split from old
        ``dropped_rows_count`` — message unit).
      - ``dropped_weekend_trm_row_count``: per-TRM-ROW count of Banrep
        TRM quotes whose date falls on Sat/Sun (split from old
        ``dropped_rows_count`` — TRM-row unit).
      - ``dropped_trm_missing_weekday_count``: per-DAY count of weekday
        UTC dates that had Claude messages but no matching TRM row
        (holiday Mondays etc.; split from old ``dropped_rows_count``
        — day unit; audit-econ finding #1).
      - ``dropped_error_count``: ``is_error=True`` rows excluded from cost
        aggregation (v0.2.1).
      - ``dropped_non_assistant_count``: JSONL rows skipped because
        ``type != "assistant"`` (Y-5a, sourced from ``JSONLReadResult``).
      - ``dropped_malformed_line_count``: v0.2.4 Y-7 — JSONL lines silently
        skipped on ``json.JSONDecodeError`` (sourced from
        ``JSONLReadResult``).
      - ``dropped_duplicate_count``: v0.2.5 Y-8 — JSONL rows collapsed by
        the OSS-mirror uniqueHash dedup discipline (sourced from
        ``JSONLReadResult``).
      - ``warn_missing_keys_count``: LiteLLM rate-key absences (Y-5a,
        sourced from ``PricingTable``).
      - ``dropped_unknown_model_count``: model-lookup-ladder-exhausted
        rows (Y-5a, sourced from ``PricingTable``).
      - ``multiple_substring_match_warning``: substring-tiebreaker-invoked
        rows (Y-5a / Y-5d, sourced from ``PricingTable``).
      - ``dropped_non_anthropic_count``: v0.2.10 audit-econ #9 — assistant
        rows whose ``message.model`` is None or non-``claude-*`` (Codex,
        GPT, etc.); filtered upstream by ``JSONLReader`` so their tokens
        do NOT inflate panel aggregates. Sourced from ``JSONLReadResult``.
      - ``ephemeral_pi_share``: Y-6 diagnostic
        ``Σ cache_create_1h / Σ (cache_create_5m + cache_create_1h)``;
        0.0 if denominator is 0. Bounded ``[0, 1]``.

    Fields:
        df: the underlying polars ``DataFrame``. Schema pinned by
            ``EXPECTED_PANEL_SCHEMA``.
        dropped_weekend_message_count: per-message weekend drops (``≥ 0``).
        dropped_weekend_trm_row_count: per-TRM-row weekend drops (``≥ 0``).
        dropped_trm_missing_weekday_count: per-day inner-join misses where
            the message-side daily aggregate has no matching TRM row
            (``≥ 0``). Surfaces holiday-Monday-style drops (audit-econ #1).
        dropped_error_count: count of assistant-error messages dropped
            during panel construction (``≥ 0``). Operator visibility
            requirement per spec v0.2.1 §3.4.
        dropped_non_assistant_count: JSONLReader-side counter (Y-5a).
        dropped_malformed_line_count: JSONLReader-side counter (v0.2.4 Y-7).
        dropped_duplicate_count: JSONLReader-side counter (v0.2.5 Y-8).
        dropped_non_anthropic_count: JSONLReader-side counter (v0.2.10
            audit-econ #9).
        warn_missing_keys_count: PricingTable-side counter (Y-5a).
        dropped_unknown_model_count: PricingTable-side counter (Y-5a).
        multiple_substring_match_warning: PricingTable-side counter (Y-5d).
        ephemeral_pi_share: Y-6 scalar in ``[0, 1]``.

    Raises:
        ValueError: if ``df.schema`` diverges from ``EXPECTED_PANEL_SCHEMA``
            (missing columns, extra columns, or wrong dtype); if any of
            the counter fields are negative; if ``ephemeral_pi_share`` is
            outside ``[0, 1]`` or non-finite.
    """

    df: pl.DataFrame
    dropped_weekend_message_count: int
    dropped_weekend_trm_row_count: int
    dropped_trm_missing_weekday_count: int
    dropped_error_count: int
    dropped_non_assistant_count: int
    dropped_malformed_line_count: int
    warn_missing_keys_count: int
    dropped_unknown_model_count: int
    multiple_substring_match_warning: int
    ephemeral_pi_share: float
    dropped_duplicate_count: int
    dropped_non_anthropic_count: int

    def __post_init__(self) -> None:
        actual: dict[str, pl.DataType] = dict(self.df.schema)
        missing = set(EXPECTED_PANEL_SCHEMA) - set(actual)
        extra = set(actual) - set(EXPECTED_PANEL_SCHEMA)
        if missing or extra:
            raise ValueError(
                f"DailyNotionalPanel schema drift: missing={sorted(missing)}, "
                f"extra={sorted(extra)}"
            )
        for col, expected in EXPECTED_PANEL_SCHEMA.items():
            if actual[col] != expected:
                raise ValueError(
                    f"DailyNotionalPanel column {col!r}: expected dtype "
                    f"{expected}, got {actual[col]}"
                )
        for fname in (
            "dropped_weekend_message_count",
            "dropped_weekend_trm_row_count",
            "dropped_trm_missing_weekday_count",
            "dropped_error_count",
            "dropped_non_assistant_count",
            "dropped_malformed_line_count",
            "warn_missing_keys_count",
            "dropped_unknown_model_count",
            "multiple_substring_match_warning",
            "dropped_duplicate_count",
            "dropped_non_anthropic_count",
        ):
            v: int = getattr(self, fname)
            if v < 0:
                raise ValueError(
                    f"DailyNotionalPanel.{fname} must be >= 0; got {v}"
                )
        if not math.isfinite(self.ephemeral_pi_share):
            raise ValueError(
                f"DailyNotionalPanel.ephemeral_pi_share must be finite; "
                f"got {self.ephemeral_pi_share}"
            )
        if not (0.0 <= self.ephemeral_pi_share <= 1.0):
            raise ValueError(
                f"DailyNotionalPanel.ephemeral_pi_share must be in [0, 1]; "
                f"got {self.ephemeral_pi_share}"
            )


__all__ = [
    "EXPECTED_PANEL_SCHEMA",
    "MessageRecord",
    "TokensByCategory",
    "JSONLReadResult",
    "DailyNotionalPanel",
]
