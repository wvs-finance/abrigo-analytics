"""Tests for ``simulations.dev_ai_cost_v2.types`` — frozen-dc value containers.

Spec ref: docs/specs/2026-05-16-ai-cost-factor-model-design.md v0.2.3 §3.5
+ §0.3 CORRECTIONS-Y-5a/-Y-5b/-Y-2 + Y-6.
Sibling spec: docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md
v0.1.3 CORRECTIONS-RR/-TT — adds ``uuid: str`` field on ``MessageRecord`` for
R6 pool canonicalization (tertiary sort key + dedupe disambiguation).
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import polars as pl
import pytest
from hypothesis import given

from simulations.dev_ai_cost_v2.types import (
    EXPECTED_PANEL_SCHEMA,
    DailyNotionalPanel,
    JSONLReadResult,
    MessageRecord,
    TokensByCategory,
)


# ─── MessageRecord ────────────────────────────────────────────────────────────


def _valid_message_kwargs() -> dict:
    return dict(
        ts=datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc),
        model="claude-sonnet-4-5",
        input_tok=100,
        output_tok=50,
        cache_create_5m=0,
        cache_create_1h=0,
        cache_read=0,
        cost_usd_notional=0.0015,  # float per CORRECTIONS-Y-2
        session_id="sess-1",
        request_id=None,
        is_error=False,
        uuid="msg-uuid-abc-123",  # R6 v0.1.3 CORRECTIONS-RR/-TT
    )


def test_message_record_constructs_with_valid_fields() -> None:
    rec = MessageRecord(**_valid_message_kwargs())
    assert rec.model == "claude-sonnet-4-5"
    assert rec.uuid == "msg-uuid-abc-123"
    assert rec.input_tok == 100
    assert rec.cost_usd_notional == 0.0015
    # CORRECTIONS-Y-2: cost_usd_notional is float, not Decimal.
    assert isinstance(rec.cost_usd_notional, float)


def test_message_record_rejects_negative_tokens() -> None:
    kwargs = _valid_message_kwargs() | {"input_tok": -1}
    with pytest.raises(ValueError, match="input_tok"):
        MessageRecord(**kwargs)


def test_message_record_rejects_negative_output_tok() -> None:
    kwargs = _valid_message_kwargs() | {"output_tok": -5}
    with pytest.raises(ValueError, match="output_tok"):
        MessageRecord(**kwargs)


def test_message_record_rejects_negative_cache_create_5m() -> None:
    kwargs = _valid_message_kwargs() | {"cache_create_5m": -1}
    with pytest.raises(ValueError, match="cache_create_5m"):
        MessageRecord(**kwargs)


def test_message_record_rejects_negative_cache_create_1h() -> None:
    kwargs = _valid_message_kwargs() | {"cache_create_1h": -1}
    with pytest.raises(ValueError, match="cache_create_1h"):
        MessageRecord(**kwargs)


def test_message_record_rejects_negative_cache_read() -> None:
    kwargs = _valid_message_kwargs() | {"cache_read": -1}
    with pytest.raises(ValueError, match="cache_read"):
        MessageRecord(**kwargs)


def test_message_record_rejects_negative_cost() -> None:
    kwargs = _valid_message_kwargs() | {"cost_usd_notional": -0.01}
    with pytest.raises(ValueError, match="cost_usd_notional"):
        MessageRecord(**kwargs)


def test_message_record_rejects_nan_cost() -> None:
    """CORRECTIONS-Y-2: float cost must reject NaN/inf."""
    kwargs = _valid_message_kwargs() | {"cost_usd_notional": float("nan")}
    with pytest.raises(ValueError, match="cost_usd_notional"):
        MessageRecord(**kwargs)


def test_message_record_rejects_inf_cost() -> None:
    kwargs = _valid_message_kwargs() | {"cost_usd_notional": float("inf")}
    with pytest.raises(ValueError, match="cost_usd_notional"):
        MessageRecord(**kwargs)


def test_message_record_rejects_neg_inf_cost() -> None:
    kwargs = _valid_message_kwargs() | {"cost_usd_notional": float("-inf")}
    with pytest.raises(ValueError, match="cost_usd_notional"):
        MessageRecord(**kwargs)


def test_message_record_rejects_naive_datetime() -> None:
    kwargs = _valid_message_kwargs() | {"ts": datetime(2026, 5, 1, 12, 0)}  # tz-naive
    with pytest.raises(ValueError, match="timezone-aware UTC"):
        MessageRecord(**kwargs)


def test_message_record_rejects_non_utc_timezone() -> None:
    from datetime import timedelta
    kwargs = _valid_message_kwargs() | {
        "ts": datetime(2026, 5, 1, 12, 0, tzinfo=timezone(timedelta(hours=-5)))
    }
    with pytest.raises(ValueError, match="UTC"):
        MessageRecord(**kwargs)


def test_message_record_rejects_empty_uuid() -> None:
    """R6 canonicalization sorts by uuid; empty string is ambiguous."""
    kwargs = _valid_message_kwargs() | {"uuid": ""}
    with pytest.raises(ValueError, match="uuid"):
        MessageRecord(**kwargs)


def test_message_record_is_frozen() -> None:
    rec = MessageRecord(**_valid_message_kwargs())
    with pytest.raises((AttributeError, Exception)):
        rec.model = "other"  # type: ignore[misc]


def test_message_record_request_id_can_be_none() -> None:
    """Legacy Claude Code pre-2.0 emits request_id=None; JSONLReader warns
    but does not error. Type contract permits None."""
    rec = MessageRecord(**(_valid_message_kwargs() | {"request_id": None}))
    assert rec.request_id is None


# ─── TokensByCategory ─────────────────────────────────────────────────────────


def test_tokens_by_category_constructs() -> None:
    t = TokensByCategory(
        input=100, output=50, cache_create_5m=10, cache_create_1h=5, cache_read=200
    )
    assert t.input == 100
    assert t.cache_read == 200


def test_tokens_by_category_zero_is_valid() -> None:
    t = TokensByCategory(input=0, output=0, cache_create_5m=0, cache_create_1h=0, cache_read=0)
    assert t.input == 0


def test_tokens_by_category_rejects_negative_input() -> None:
    with pytest.raises(ValueError, match="input"):
        TokensByCategory(input=-1, output=0, cache_create_5m=0, cache_create_1h=0, cache_read=0)


def test_tokens_by_category_rejects_negative_cache_read() -> None:
    with pytest.raises(ValueError, match="cache_read"):
        TokensByCategory(input=0, output=0, cache_create_5m=0, cache_create_1h=0, cache_read=-1)


# ─── DailyNotionalPanel ───────────────────────────────────────────────────────


def _valid_panel_df() -> pl.DataFrame:
    """Build a minimal one-row DataFrame matching EXPECTED_PANEL_SCHEMA.

    CORRECTIONS-Y-2 / Y-6: monetary cols are Float64; ``ephemeral_pi_share``
    is a Float64 scalar broadcast across the panel.
    """
    return pl.DataFrame(
        {
            "date_utc": [datetime(2026, 5, 1).date()],
            "notional_cost_usd": [1.50],
            "notional_cost_cop": [6300.00],
            "trm_cop_per_usd": [4200.00],
            "input_tok": [1000],
            "output_tok": [500],
            "cache_create_5m": [0],
            "cache_create_1h": [0],
            "cache_read": [0],
            "n_messages": [5],
            "ephemeral_pi_share": [0.0],
        },
        schema={
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
        },
    )


def _panel_kwargs(**overrides) -> dict:
    """Default kwargs for a DailyNotionalPanel including v0.2.3/2.4/2.5/2.10 counters."""
    base = dict(
        df=_valid_panel_df(),
        dropped_weekend_message_count=0,
        dropped_weekend_trm_row_count=0,
        dropped_trm_missing_weekday_count=0,
        dropped_error_count=0,
        dropped_non_assistant_count=0,
        dropped_malformed_line_count=0,
        warn_missing_keys_count=0,
        dropped_unknown_model_count=0,
        multiple_substring_match_warning=0,
        ephemeral_pi_share=0.0,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=0,
    )
    base.update(overrides)
    return base


def test_daily_notional_panel_constructs() -> None:
    p = DailyNotionalPanel(**_panel_kwargs())
    assert p.df.height == 1
    assert p.dropped_weekend_message_count == 0
    assert p.dropped_weekend_trm_row_count == 0
    assert p.dropped_trm_missing_weekday_count == 0
    assert p.dropped_non_assistant_count == 0
    assert p.dropped_malformed_line_count == 0
    assert p.warn_missing_keys_count == 0
    assert p.dropped_unknown_model_count == 0
    assert p.multiple_substring_match_warning == 0
    assert p.ephemeral_pi_share == 0.0


def test_daily_notional_panel_rejects_missing_column() -> None:
    df = _valid_panel_df().drop("trm_cop_per_usd")
    with pytest.raises(ValueError, match="missing"):
        DailyNotionalPanel(**_panel_kwargs(df=df))


def test_daily_notional_panel_rejects_extra_column() -> None:
    df = _valid_panel_df().with_columns(pl.lit(1).alias("rogue_col"))
    with pytest.raises(ValueError, match="extra"):
        DailyNotionalPanel(**_panel_kwargs(df=df))


def test_daily_notional_panel_rejects_wrong_dtype() -> None:
    df = _valid_panel_df().with_columns(pl.col("input_tok").cast(pl.Float64))
    with pytest.raises(ValueError, match="input_tok"):
        DailyNotionalPanel(**_panel_kwargs(df=df))


def test_daily_notional_panel_rejects_negative_weekend_message_count() -> None:
    """v0.2.10 audit-econ #10: per-message weekend counter must be ≥ 0."""
    with pytest.raises(ValueError, match="dropped_weekend_message_count"):
        DailyNotionalPanel(**_panel_kwargs(dropped_weekend_message_count=-1))


def test_daily_notional_panel_rejects_negative_weekend_trm_row_count() -> None:
    """v0.2.10 audit-econ #10: per-TRM-row weekend counter must be ≥ 0."""
    with pytest.raises(ValueError, match="dropped_weekend_trm_row_count"):
        DailyNotionalPanel(**_panel_kwargs(dropped_weekend_trm_row_count=-1))


def test_daily_notional_panel_rejects_negative_trm_missing_weekday_count() -> None:
    """v0.2.10 audit-econ #1: per-day TRM-missing-weekday counter must be ≥ 0."""
    with pytest.raises(ValueError, match="dropped_trm_missing_weekday_count"):
        DailyNotionalPanel(**_panel_kwargs(dropped_trm_missing_weekday_count=-1))


def test_daily_notional_panel_rejects_negative_non_anthropic_count() -> None:
    """v0.2.10 audit-econ #9: non-Anthropic upstream filter counter ≥ 0."""
    with pytest.raises(ValueError, match="dropped_non_anthropic_count"):
        DailyNotionalPanel(**_panel_kwargs(dropped_non_anthropic_count=-1))


def test_daily_notional_panel_rejects_negative_error_counts() -> None:
    with pytest.raises(ValueError, match="dropped"):
        DailyNotionalPanel(**_panel_kwargs(dropped_error_count=-1))


def test_daily_notional_panel_rejects_negative_non_assistant_count() -> None:
    """Y-5a: counter ownership — dropped_non_assistant_count must be ≥ 0."""
    with pytest.raises(ValueError, match="non_assistant"):
        DailyNotionalPanel(**_panel_kwargs(dropped_non_assistant_count=-1))


def test_daily_notional_panel_rejects_negative_malformed_line_count() -> None:
    """v0.2.4 Y-7: dropped_malformed_line_count must be ≥ 0."""
    with pytest.raises(ValueError, match="dropped_malformed_line"):
        DailyNotionalPanel(**_panel_kwargs(dropped_malformed_line_count=-1))


def test_daily_notional_panel_rejects_negative_duplicate_count() -> None:
    """v0.2.5 Y-8: dropped_duplicate_count must be ≥ 0."""
    with pytest.raises(ValueError, match="dropped_duplicate_count"):
        DailyNotionalPanel(**_panel_kwargs(dropped_duplicate_count=-1))


def test_daily_notional_panel_rejects_negative_warn_missing_keys() -> None:
    with pytest.raises(ValueError, match="warn_missing_keys"):
        DailyNotionalPanel(**_panel_kwargs(warn_missing_keys_count=-1))


def test_daily_notional_panel_rejects_negative_dropped_unknown_model() -> None:
    with pytest.raises(ValueError, match="dropped_unknown_model"):
        DailyNotionalPanel(**_panel_kwargs(dropped_unknown_model_count=-1))


def test_daily_notional_panel_rejects_negative_multiple_substring() -> None:
    with pytest.raises(ValueError, match="multiple_substring"):
        DailyNotionalPanel(**_panel_kwargs(multiple_substring_match_warning=-1))


def test_daily_notional_panel_ephemeral_pi_share_bounds() -> None:
    """Y-6: π̂ is a share in [0, 1]; out-of-range values are rejected."""
    with pytest.raises(ValueError, match="ephemeral_pi_share"):
        DailyNotionalPanel(**_panel_kwargs(ephemeral_pi_share=1.5))
    with pytest.raises(ValueError, match="ephemeral_pi_share"):
        DailyNotionalPanel(**_panel_kwargs(ephemeral_pi_share=-0.1))


def test_expected_panel_schema_has_eleven_columns() -> None:
    """Pin schema width — v0.2.3 adds ``ephemeral_pi_share`` (Y-6)."""
    assert len(EXPECTED_PANEL_SCHEMA) == 11
    assert "ephemeral_pi_share" in EXPECTED_PANEL_SCHEMA


def test_expected_panel_schema_monetary_cols_are_float64() -> None:
    """CORRECTIONS-Y-2: cost cols are Float64, not Decimal."""
    assert EXPECTED_PANEL_SCHEMA["notional_cost_usd"] == pl.Float64
    assert EXPECTED_PANEL_SCHEMA["notional_cost_cop"] == pl.Float64
    assert EXPECTED_PANEL_SCHEMA["trm_cop_per_usd"] == pl.Float64
    assert EXPECTED_PANEL_SCHEMA["ephemeral_pi_share"] == pl.Float64


# ─── JSONLReadResult (Y-5b: types-tier placement) ────────────────────────────


def test_jsonl_read_result_importable_from_types() -> None:
    """CR-Z-2 pin: JSONLReadResult lives in types/, NOT in jsonl_io.

    Tier discipline: jsonl_io is utils-tier; types are imported by both
    modules and utils, so the result container must live in types.
    """
    from simulations.dev_ai_cost_v2 import types as _types
    assert hasattr(_types, "JSONLReadResult")


def test_jsonl_read_result_not_exported_from_jsonl_io() -> None:
    """CR-Z-2 pin: JSONLReadResult must not be defined in jsonl_io module."""
    from simulations.dev_ai_cost_v2 import jsonl_io as _jsonl_io
    # The symbol may be re-exported as a name (re-import is fine) but its
    # canonical __module__ must be the types module.
    assert JSONLReadResult.__module__ == "simulations.dev_ai_cost_v2.types"
    # And it is not in __all__ of jsonl_io
    if hasattr(_jsonl_io, "__all__"):
        assert "JSONLReadResult" not in _jsonl_io.__all__


def test_jsonl_read_result_constructs() -> None:
    rec = MessageRecord(**_valid_message_kwargs())
    r = JSONLReadResult(
        records=(rec,),
        dropped_non_assistant_count=3,
        dropped_malformed_line_count=0,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=0,
    )
    assert len(r.records) == 1
    assert r.dropped_non_assistant_count == 3
    assert r.dropped_malformed_line_count == 0
    assert r.dropped_duplicate_count == 0
    assert r.dropped_non_anthropic_count == 0


def test_jsonl_read_result_records_is_tuple_immutable() -> None:
    """Y-5b: records is a tuple (immutable, hashable)."""
    rec = MessageRecord(**_valid_message_kwargs())
    r = JSONLReadResult(
        records=(rec,),
        dropped_non_assistant_count=0,
        dropped_malformed_line_count=0,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=0,
    )
    assert isinstance(r.records, tuple)


def test_jsonl_read_result_rejects_negative_count() -> None:
    with pytest.raises(ValueError, match="dropped_non_assistant"):
        JSONLReadResult(
            records=(),
            dropped_non_assistant_count=-1,
            dropped_malformed_line_count=0,
            dropped_duplicate_count=0,
            dropped_non_anthropic_count=0,
        )


def test_jsonl_read_result_rejects_negative_malformed_count() -> None:
    """v0.2.4 Y-7: dropped_malformed_line_count must be >= 0."""
    with pytest.raises(ValueError, match="dropped_malformed_line"):
        JSONLReadResult(
            records=(),
            dropped_non_assistant_count=0,
            dropped_malformed_line_count=-1,
            dropped_duplicate_count=0,
            dropped_non_anthropic_count=0,
        )


def test_jsonl_read_result_rejects_negative_duplicate_count() -> None:
    """v0.2.5 Y-8: dropped_duplicate_count must be >= 0."""
    with pytest.raises(ValueError, match="dropped_duplicate_count"):
        JSONLReadResult(
            records=(),
            dropped_non_assistant_count=0,
            dropped_malformed_line_count=0,
            dropped_duplicate_count=-1,
            dropped_non_anthropic_count=0,
        )


def test_jsonl_read_result_rejects_negative_non_anthropic_count() -> None:
    """v0.2.10 audit-econ #9: dropped_non_anthropic_count must be >= 0."""
    with pytest.raises(ValueError, match="dropped_non_anthropic_count"):
        JSONLReadResult(
            records=(),
            dropped_non_assistant_count=0,
            dropped_malformed_line_count=0,
            dropped_duplicate_count=0,
            dropped_non_anthropic_count=-1,
        )


def test_jsonl_read_result_empty_records_valid() -> None:
    r = JSONLReadResult(
        records=(),
        dropped_non_assistant_count=0,
        dropped_malformed_line_count=0,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=0,
    )
    assert r.records == ()
    assert r.dropped_non_assistant_count == 0
    assert r.dropped_malformed_line_count == 0
    assert r.dropped_duplicate_count == 0
    assert r.dropped_non_anthropic_count == 0


# ─── CR-Z-1 counter ownership pin ────────────────────────────────────────────


def test_cr_z_1_pricingtable_owns_warn_missing_keys_count() -> None:
    """CR-Z-1: WARN_missing_keys_count lives on PricingTable, NOT on JSONLReader.

    Tier discipline: counter ownership cannot be shared across tiers.
    """
    from simulations.dev_ai_cost_v2.anthropic_pricing import PricingTable
    from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader

    # PricingTable instance carries the counter as a field.
    fields = {f.name for f in PricingTable.__dataclass_fields__.values()}
    assert "WARN_missing_keys_count" in fields
    assert "dropped_unknown_model_count" in fields
    assert "multiple_substring_match_warning" in fields

    # JSONLReader does NOT carry WARN_missing_keys_count as a public field.
    # (Y-5f: JSONLReader.__init__ now takes pricing= to compute cost at parse
    # time, but it still does NOT own the WARN_missing_keys_count counter
    # — that lives on the injected PricingTable per Y-5a.)
    init_params = set(JSONLReader.__init__.__code__.co_varnames)
    assert "WARN_missing_keys_count" not in init_params


def test_cr_z_1_jsonlreadresult_owns_dropped_non_assistant_count() -> None:
    """CR-Z-1: dropped_non_assistant_count lives on JSONLReadResult, NOT on PricingTable."""
    from simulations.dev_ai_cost_v2.anthropic_pricing import PricingTable

    fields = {f.name for f in JSONLReadResult.__dataclass_fields__.values()}
    assert "dropped_non_assistant_count" in fields

    pt_fields = {f.name for f in PricingTable.__dataclass_fields__.values()}
    assert "dropped_non_assistant_count" not in pt_fields


# ─── Hypothesis property test ─────────────────────────────────────────────────


from simulations.tests.strategies import message_records  # noqa: E402


@given(rec=message_records())
def test_message_record_post_init_invariants(rec: MessageRecord) -> None:
    """Every successfully-constructed MessageRecord must satisfy __post_init__ invariants."""
    assert rec.input_tok >= 0
    assert rec.output_tok >= 0
    assert rec.cache_create_5m >= 0
    assert rec.cache_create_1h >= 0
    assert rec.cache_read >= 0
    assert rec.cost_usd_notional >= 0
    assert math.isfinite(rec.cost_usd_notional)
    assert rec.uuid != ""
    assert rec.ts.tzinfo is not None
    assert rec.ts.utcoffset() == timezone.utc.utcoffset(rec.ts)
