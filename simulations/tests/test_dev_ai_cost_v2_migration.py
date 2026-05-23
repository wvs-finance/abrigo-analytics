"""CR-Z-6 v0.2.3 migration coverage smoke test.

Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.3
§0.3 CORRECTIONS-Y-5f + §3.5 contracts table.

Imports every public symbol from the v0.2.3 §3.5 contracts table and pins
the runtime signature using ``inspect.signature``. A drift in any contract
arity, return type, or counter ownership fails loud here before downstream
panel builds silently regress.
"""
from __future__ import annotations

import inspect
import typing as _typing

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
)
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader
from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel
from simulations.dev_ai_cost_v2.types import (
    EXPECTED_PANEL_SCHEMA,
    DailyNotionalPanel,
    JSONLReadResult,
    MessageRecord,
    TokensByCategory,
)


def test_litellm_sha_pinned_constant() -> None:
    """The pinned SHA is retained per v0.2.3 (Y-5f does NOT delete it)."""
    assert LITELLM_SHA_PINNED == "e58a561caa21169fb02174148444c08509ce7028"


def test_jsonl_reader_init_takes_pricing() -> None:
    """v0.2.3 Y-5f: JSONLReader __init__ injects PricingTable."""
    sig = inspect.signature(JSONLReader.__init__)
    params = list(sig.parameters.keys())
    assert "pricing" in params


def test_jsonl_reader_call_returns_jsonl_read_result() -> None:
    """v0.2.3 Y-5b: __call__ returns JSONLReadResult (not Sequence)."""
    sig = inspect.signature(JSONLReader.__call__)
    # We cannot inspect the runtime return value type without invoking the
    # callable, but we can confirm the annotation in the signature.
    ret = sig.return_annotation
    # Accept either the class or its name (string-form forward ref).
    ret_name = ret.__name__ if isinstance(ret, type) else str(ret)
    assert "JSONLReadResult" in ret_name


def test_jsonl_read_result_canonical_module() -> None:
    """v0.2.3 Y-5b/CR-Z-2: JSONLReadResult lives in types tier."""
    assert JSONLReadResult.__module__ == "simulations.dev_ai_cost_v2.types"


def test_jsonl_read_result_fields_exact() -> None:
    """v0.2.10 audit-econ #9: JSONLReadResult carries records + 4 JSONLReader counters.

    v0.2.5 Y-8 baseline = 3 counters; v0.2.10 adds
    ``dropped_non_anthropic_count`` to surface Codex/GPT upstream filter.
    """
    fields = {f.name for f in JSONLReadResult.__dataclass_fields__.values()}
    assert fields == {
        "records",
        "dropped_non_assistant_count",
        "dropped_malformed_line_count",
        "dropped_duplicate_count",
        "dropped_non_anthropic_count",
    }


def test_message_record_cost_is_float_type() -> None:
    """v0.2.3 Y-2: cost_usd_notional is float, not Decimal."""
    fields = MessageRecord.__dataclass_fields__
    cost_field = fields["cost_usd_notional"]
    # Annotation may be the type object or a string forward ref.
    ann = cost_field.type
    ann_name = ann.__name__ if isinstance(ann, type) else str(ann)
    assert "float" in ann_name


def test_tokens_by_category_preserves_split() -> None:
    """v0.2.3 Y-5c: 5m and 1h fields remain distinct on TokensByCategory."""
    fields = {f.name for f in TokensByCategory.__dataclass_fields__.values()}
    assert "cache_create_5m" in fields
    assert "cache_create_1h" in fields


def test_pricing_table_owns_v0_2_3_counters() -> None:
    """v0.2.3 Y-5a/CR-Z-1: PricingTable owns 3 counters."""
    fields = {f.name for f in PricingTable.__dataclass_fields__.values()}
    assert "WARN_missing_keys_count" in fields
    assert "dropped_unknown_model_count" in fields
    assert "multiple_substring_match_warning" in fields


def test_pricing_table_call_signature_unchanged() -> None:
    """v0.2.3 RC closure note: PricingTable.__call__ signature is unchanged."""
    sig = inspect.signature(PricingTable.__call__)
    params = list(sig.parameters.keys())
    # self + (model, ts, toks)
    assert params == ["self", "model", "ts", "toks"]


def test_pricing_table_from_litellm_sha_signature_unchanged() -> None:
    """v0.2.3 RC closure note: from_litellm_sha signature unchanged.

    Specifically: positional args (cls, sha, cached_json_path) +
    keyword-only ``skip_sha_check``. No positional-arg breakage downstream.
    """
    sig = inspect.signature(PricingTable.from_litellm_sha)
    params = sig.parameters
    assert "sha" in params
    assert "cached_json_path" in params
    assert "skip_sha_check" in params
    # Confirm skip_sha_check is keyword-only.
    assert params["skip_sha_check"].kind == inspect.Parameter.KEYWORD_ONLY


def test_build_daily_panel_first_arg_is_jsonl_read_result() -> None:
    """v0.2.3 Y-5b: first positional arg renamed records → read_result."""
    sig = inspect.signature(build_daily_panel)
    params = list(sig.parameters.keys())
    assert params[0] == "read_result"
    # Inspect the annotation on the first param.
    first = sig.parameters["read_result"]
    ann = first.annotation
    ann_name = ann.__name__ if isinstance(ann, type) else str(ann)
    assert "JSONLReadResult" in ann_name


def test_daily_notional_panel_v0_2_3_fields() -> None:
    """v0.2.10 audit-econ #10: DailyNotionalPanel carries 10 counters + π̂.

    Y-5a baseline = 6 counters; Y-7 adds ``dropped_malformed_line_count``;
    Y-8 adds ``dropped_duplicate_count``. v0.2.10 splits the legacy
    ``dropped_rows_count`` (mixed-unit) into 3 named counters:
    ``dropped_weekend_message_count`` (msg-level),
    ``dropped_weekend_trm_row_count`` (TRM-row-level), and
    ``dropped_trm_missing_weekday_count`` (day-level; surfaces
    audit-econ #1's holiday Mondays).
    """
    fields = {f.name for f in DailyNotionalPanel.__dataclass_fields__.values()}
    required = {
        "df",
        "dropped_weekend_message_count",
        "dropped_weekend_trm_row_count",
        "dropped_trm_missing_weekday_count",
        "dropped_error_count",
        "dropped_non_assistant_count",
        "dropped_malformed_line_count",
        "dropped_duplicate_count",
        "dropped_non_anthropic_count",
        "warn_missing_keys_count",
        "dropped_unknown_model_count",
        "multiple_substring_match_warning",
        "ephemeral_pi_share",
    }
    missing = required - fields
    assert not missing, f"DailyNotionalPanel missing v0.2.10 fields: {missing}"
    # The legacy unit-mixed counter must be GONE (per CLAUDE.md no
    # backwards-compatibility shims).
    assert "dropped_rows_count" not in fields, (
        "v0.2.10 audit-econ #10: legacy dropped_rows_count must be removed"
    )


def test_expected_panel_schema_v0_2_3() -> None:
    """v0.2.3 Y-2 + Y-6: monetary cols Float64; ephemeral_pi_share present."""
    import polars as pl
    assert EXPECTED_PANEL_SCHEMA["notional_cost_usd"] == pl.Float64
    assert EXPECTED_PANEL_SCHEMA["notional_cost_cop"] == pl.Float64
    assert EXPECTED_PANEL_SCHEMA["trm_cop_per_usd"] == pl.Float64
    assert EXPECTED_PANEL_SCHEMA["ephemeral_pi_share"] == pl.Float64
    # 11 columns total: 10 v0.2.1 + 1 v0.2.3 (π̂).
    assert len(EXPECTED_PANEL_SCHEMA) == 11


def test_all_v0_2_3_symbols_importable() -> None:
    """CR-Z-6 closure: every symbol named in §3.5 contracts table imports cleanly."""
    # Class types
    for cls in (
        MessageRecord,
        TokensByCategory,
        JSONLReadResult,
        DailyNotionalPanel,
        PricingTable,
        JSONLReader,
    ):
        assert inspect.isclass(cls), f"{cls!r} should be a class"

    # Callables
    assert callable(build_daily_panel)

    # Constants
    assert isinstance(LITELLM_SHA_PINNED, str)
    assert isinstance(EXPECTED_PANEL_SCHEMA, dict)
