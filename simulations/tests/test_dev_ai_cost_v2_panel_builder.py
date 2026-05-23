"""Tests for ``simulations.dev_ai_cost_v2.panel_builder.build_daily_panel``.

Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.3
§3.3 (daily aggregation), §3.5 (panel contract), §0.1 CORRECTIONS-V
(``is_error`` dropped, UTC half-open), CORRECTIONS-M (forward-fill
forbidden), §0.3 CORRECTIONS-Y-2/-Y-5a/-Y-5b/-Y-6.

Sibling spec ref: ``docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md``
v0.1.3 CORRECTIONS-RR/-TT — ``MessageRecord.uuid`` required.

Test inventory (v0.2.3):
1. Reconciliation under Float64: sum of per-message ``cost_usd_notional``
   over non-error rows equals panel ``notional_cost_usd`` within float
   tolerance (Y-2 ccusage parity).
2. is_error rows dropped from cost, counted via ``dropped_error_count``.
3. Forward-fill forbidden (records-side gaps).
4. Weekends dropped on both sides.
5. Double-iteration equivalence over tuple-records (Y-5b).
6. Polars vs. Python weekday calendar pin.
7. Hypothesis property: no records-only days in output.
8. Empty records → empty panel.
9. TRM-only days not in output.
10. Y-5a counter threading: JSONLReader-side counter + PricingTable
    counters surface on the panel.
11. Y-6 π̂ computation and broadcast.
12. JSONLReadResult is the input type (not Sequence[MessageRecord]).
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
    _REQUIRED_KEYS,
)
from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel
from simulations.dev_ai_cost_v2.types import (
    DailyNotionalPanel,
    JSONLReadResult,
    MessageRecord,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _toy_pricing(tmp_path: Path) -> PricingTable:
    fake = {"claude-sonnet-4-5": {k: 1e-06 for k in _REQUIRED_KEYS}}
    p = tmp_path / "lite.json"
    p.write_text(json.dumps(fake))
    return PricingTable.from_litellm_sha(
        LITELLM_SHA_PINNED, p, skip_sha_check=True
    )


def _toy_trm() -> pl.DataFrame:
    """5 weekdays 2026-05-04..2026-05-08 (Mon-Fri). Float64 trm column (Y-2)."""
    return pl.DataFrame(
        {
            "date": [date(2026, 5, d) for d in (4, 5, 6, 7, 8)],
            "trm_cop_per_usd": [4100.0, 4105.0, 4090.0, 4110.0, 4120.0],
        },
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )


def _rec(
    day: int,
    hour: int = 12,
    *,
    is_error: bool = False,
    uuid_suffix: str = "",
    cache_create_5m: int = 0,
    cache_create_1h: int = 0,
) -> MessageRecord:
    """Build a ``MessageRecord`` fixture with a unique non-empty uuid (Y-2 float cost)."""
    return MessageRecord(
        ts=datetime(2026, 5, day, hour, tzinfo=timezone.utc),
        model="claude-sonnet-4-5",
        input_tok=1000,
        output_tok=500,
        cache_create_5m=cache_create_5m,
        cache_create_1h=cache_create_1h,
        cache_read=0,
        cost_usd_notional=0.0015,  # float per Y-2
        session_id="s",
        request_id="r",
        is_error=is_error,
        uuid=f"u-{day}-{hour}-{uuid_suffix}",
    )


def _result(
    records: list[MessageRecord],
    dropped_non_assistant: int = 0,
    dropped_malformed: int = 0,
    dropped_duplicate: int = 0,
    dropped_non_anthropic: int = 0,
) -> JSONLReadResult:
    """Wrap records in JSONLReadResult (Y-5b — panel_builder now consumes this).

    v0.2.4 Y-7: ``dropped_malformed`` defaults to 0 for back-compatible test
    fixtures; explicit value used by Y-7 counter-threading test.
    v0.2.5 Y-8: ``dropped_duplicate`` defaults to 0 for back-compatible
    fixtures; explicit value used by Y-8 counter-threading test.
    v0.2.10 audit-econ #9: ``dropped_non_anthropic`` defaults to 0 for
    back-compatible fixtures; explicit value used by #9 counter-threading test.
    """
    return JSONLReadResult(
        records=tuple(records),
        dropped_non_assistant_count=dropped_non_assistant,
        dropped_malformed_line_count=dropped_malformed,
        dropped_duplicate_count=dropped_duplicate,
        dropped_non_anthropic_count=dropped_non_anthropic,
    )


# ─── Test 1: reconciliation under Float64 (Y-2 ccusage parity) ──────────────


def test_reconciliation_float_ccusage_parity(tmp_path: Path) -> None:
    pricing = _toy_pricing(tmp_path)
    records = [
        _rec(4, uuid_suffix="a"),
        _rec(5, uuid_suffix="a"),
        _rec(5, uuid_suffix="b"),
    ]
    panel = build_daily_panel(_result(records), pricing, _toy_trm())
    raw_total = sum(r.cost_usd_notional for r in records if not r.is_error)
    panel_total = panel.df["notional_cost_usd"].sum()
    # Float-arithmetic ccusage parity within 0.1% (relative).
    assert abs(panel_total - raw_total) / raw_total < 1e-3
    # And the dtype is Float64.
    assert panel.df.schema["notional_cost_usd"] == pl.Float64


# ─── Test 2: is_error dropped from cost, counted separately ──────────────────


def test_is_error_rows_dropped_from_cost_counted_separately(
    tmp_path: Path,
) -> None:
    pricing = _toy_pricing(tmp_path)
    records = [
        _rec(4, uuid_suffix="ok"),
        _rec(4, is_error=True, uuid_suffix="err"),
        _rec(5, uuid_suffix="ok"),
    ]
    panel = build_daily_panel(_result(records), pricing, _toy_trm())
    assert panel.dropped_error_count == 1
    may4 = panel.df.filter(pl.col("date_utc") == date(2026, 5, 4))
    assert may4["n_messages"].item() == 1
    # Float comparison (ccusage parity).
    assert may4["notional_cost_usd"].item() == pytest.approx(0.0015, rel=1e-9)


# ─── Test 3: forward-fill forbidden (records-side gaps) ─────────────────────


def test_forward_fill_forbidden_property(tmp_path: Path) -> None:
    pricing = _toy_pricing(tmp_path)
    records = [_rec(5, uuid_suffix="solo")]
    panel = build_daily_panel(_result(records), pricing, _toy_trm())
    out_dates = set(panel.df["date_utc"].to_list())
    assert out_dates == {date(2026, 5, 5)}


# ─── Test 4: weekends dropped on both sides ──────────────────────────────────


def test_weekends_dropped(tmp_path: Path) -> None:
    pricing = _toy_pricing(tmp_path)
    records = [
        _rec(2, uuid_suffix="sat"),
        _rec(3, uuid_suffix="sun"),
        _rec(4, uuid_suffix="mon"),
    ]
    trm = pl.DataFrame(
        {
            "date": [date(2026, 5, d) for d in (2, 3, 4)],
            "trm_cop_per_usd": [4100.0, 4100.0, 4100.0],
        },
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )
    panel = build_daily_panel(_result(records), pricing, trm)
    assert set(panel.df["date_utc"].to_list()) == {date(2026, 5, 4)}
    # v0.2.10 audit-econ #10: split counters — 2 weekend messages
    # (Sat=2 + Sun=3) + 2 weekend TRM rows (Sat=2 + Sun=3).
    assert panel.dropped_weekend_message_count == 2
    assert panel.dropped_weekend_trm_row_count == 2
    assert panel.dropped_trm_missing_weekday_count == 0


# ─── Test 5: double-iteration equivalence over tuple records ────────────────


def test_double_iteration_equivalence(tmp_path: Path) -> None:
    pricing = _toy_pricing(tmp_path)
    records: list[MessageRecord] = [
        _rec(4, uuid_suffix="a"),
        _rec(5, uuid_suffix="b"),
    ]
    p1 = build_daily_panel(_result(records), pricing, _toy_trm())
    p2 = build_daily_panel(_result(records), pricing, _toy_trm())
    assert p1.df.equals(p2.df)
    # v0.2.10 audit-econ #10: three named counters
    assert p1.dropped_weekend_message_count == p2.dropped_weekend_message_count
    assert p1.dropped_weekend_trm_row_count == p2.dropped_weekend_trm_row_count
    assert (
        p1.dropped_trm_missing_weekday_count
        == p2.dropped_trm_missing_weekday_count
    )
    assert p1.dropped_error_count == p2.dropped_error_count
    assert p1.ephemeral_pi_share == p2.ephemeral_pi_share


# ─── Test 6: weekday calendar pins ──────────────────────────────────────────


def test_polars_weekday_calendar_pin() -> None:
    s = pl.Series(
        [date(2026, 5, 4), date(2026, 5, 8), date(2026, 5, 2), date(2026, 5, 3)]
    )
    assert s.dt.weekday().to_list() == [1, 5, 6, 7]


def test_python_weekday_calendar_pin() -> None:
    assert datetime(2026, 5, 4).weekday() == 0  # Mon
    assert datetime(2026, 5, 8).weekday() == 4  # Fri
    assert datetime(2026, 5, 2).weekday() == 5  # Sat
    assert datetime(2026, 5, 3).weekday() == 6  # Sun


# ─── Test 7: Hypothesis property — no records-only days ─────────────────────


@given(
    record_days=st.lists(
        st.sampled_from([4, 5, 6, 7, 8]),
        min_size=1,
        max_size=10,
    ),
    trm_days=st.lists(
        st.sampled_from([4, 5, 6, 7, 8]),
        min_size=1,
        max_size=5,
        unique=True,
    ),
)
@settings(max_examples=40, deadline=None)
def test_no_records_only_days_in_output(
    record_days: list[int],
    trm_days: list[int],
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    tmp_path = tmp_path_factory.mktemp("toy_pricing")
    pricing = _toy_pricing(tmp_path)
    records = [
        _rec(d, uuid_suffix=f"i{i}") for i, d in enumerate(record_days)
    ]
    trm = pl.DataFrame(
        {
            "date": [date(2026, 5, d) for d in sorted(set(trm_days))],
            "trm_cop_per_usd": [4100.0 for _ in range(len(set(trm_days)))],
        },
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )
    panel = build_daily_panel(_result(records), pricing, trm)
    out_dates = set(panel.df["date_utc"].to_list())
    record_date_set = {date(2026, 5, d) for d in record_days}
    trm_date_set = {date(2026, 5, d) for d in trm_days}
    assert out_dates <= (record_date_set & trm_date_set)
    assert out_dates == (record_date_set & trm_date_set)


# ─── Test 8: empty records edge case ─────────────────────────────────────────


def test_empty_records_yields_empty_panel(tmp_path: Path) -> None:
    pricing = _toy_pricing(tmp_path)
    panel = build_daily_panel(_result([]), pricing, _toy_trm())
    assert panel.df.height == 0
    assert panel.dropped_error_count == 0
    # v0.2.10 audit-econ #10: three named counters all 0 when no records.
    assert panel.dropped_weekend_message_count == 0
    assert panel.dropped_weekend_trm_row_count == 0
    assert panel.dropped_trm_missing_weekday_count == 0
    # Y-6: zero records → π̂ = 0.0.
    assert panel.ephemeral_pi_share == 0.0


# ─── Test 9: TRM-only days not in output ────────────────────────────────────


def test_trm_only_days_not_in_output(tmp_path: Path) -> None:
    pricing = _toy_pricing(tmp_path)
    records = [_rec(4, uuid_suffix="only")]
    panel = build_daily_panel(_result(records), pricing, _toy_trm())
    out_dates = set(panel.df["date_utc"].to_list())
    assert out_dates == {date(2026, 5, 4)}


# ─── Test 10: Y-5a counter threading ────────────────────────────────────────


def test_counter_threading_jsonlreader_side(tmp_path: Path) -> None:
    """Y-5a: dropped_non_assistant_count from JSONLReadResult must surface
    on DailyNotionalPanel.
    """
    pricing = _toy_pricing(tmp_path)
    records = [_rec(4, uuid_suffix="a")]
    rr = JSONLReadResult(
        records=tuple(records),
        dropped_non_assistant_count=7,
        dropped_malformed_line_count=0,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=0,
    )
    panel = build_daily_panel(rr, pricing, _toy_trm())
    assert panel.dropped_non_assistant_count == 7


def test_counter_threading_pricingtable_side(tmp_path: Path) -> None:
    """Y-5a: WARN_missing_keys_count + dropped_unknown_model_count +
    multiple_substring_match_warning from PricingTable must surface on
    DailyNotionalPanel.
    """
    # Use a pricing table with a missing required key to bump
    # WARN_missing_keys_count.
    fake = {
        "claude-sonnet-4-5": {
            "input_cost_per_token": 1e-06,
            "output_cost_per_token": 1e-06,
            "cache_creation_input_token_cost": 1e-06,
            # MISSING: cache_creation_input_token_cost_above_1hr
            "cache_read_input_token_cost": 1e-06,
        }
    }
    p = tmp_path / "lite.json"
    p.write_text(json.dumps(fake))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        pricing = PricingTable.from_litellm_sha(
            LITELLM_SHA_PINNED, p, skip_sha_check=True
        )
    assert pricing.WARN_missing_keys_count == 1

    records = [_rec(4, uuid_suffix="a")]
    panel = build_daily_panel(_result(records), pricing, _toy_trm())
    assert panel.warn_missing_keys_count == 1
    assert panel.dropped_unknown_model_count == 0
    assert panel.multiple_substring_match_warning == 0


# ─── Test 11: Y-6 ephemeral π̂ ──────────────────────────────────────────────


def test_y6_ephemeral_pi_share_computed(tmp_path: Path) -> None:
    """Y-6: π̂ = Σ cache_create_1h / Σ (5m + 1h) across all records."""
    pricing = _toy_pricing(tmp_path)
    # Across all 3 records: Σ 1h = 30, Σ 5m = 70 → denom = 100, π̂ = 0.3.
    records = [
        _rec(4, uuid_suffix="a", cache_create_5m=30, cache_create_1h=10),
        _rec(5, uuid_suffix="b", cache_create_5m=20, cache_create_1h=10),
        _rec(6, uuid_suffix="c", cache_create_5m=20, cache_create_1h=10),
    ]
    panel = build_daily_panel(_result(records), pricing, _toy_trm())
    assert panel.ephemeral_pi_share == pytest.approx(0.3, rel=1e-12)
    # And the column is broadcast as a constant scalar across all rows.
    pi_col = panel.df["ephemeral_pi_share"].to_list()
    assert all(v == pytest.approx(0.3, rel=1e-12) for v in pi_col)


def test_y6_ephemeral_pi_share_zero_denominator(tmp_path: Path) -> None:
    """Y-6: when Σ (5m + 1h) == 0, π̂ defaults to 0.0."""
    pricing = _toy_pricing(tmp_path)
    records = [
        _rec(4, uuid_suffix="a", cache_create_5m=0, cache_create_1h=0),
    ]
    panel = build_daily_panel(_result(records), pricing, _toy_trm())
    assert panel.ephemeral_pi_share == 0.0


# ─── Test 12: input type contract (JSONLReadResult, not Sequence) ───────────


def test_build_daily_panel_consumes_jsonl_read_result(tmp_path: Path) -> None:
    """Y-5b/CR-Z-2: signature first arg is JSONLReadResult.

    Smoke test: passing a plain ``list[MessageRecord]`` is a type error;
    here we verify the JSONLReadResult container is what flows.
    """
    pricing = _toy_pricing(tmp_path)
    records = [_rec(4, uuid_suffix="a")]
    rr = JSONLReadResult(
        records=tuple(records),
        dropped_non_assistant_count=0,
        dropped_malformed_line_count=0,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=0,
    )
    # Must work cleanly.
    panel = build_daily_panel(rr, pricing, _toy_trm())
    assert isinstance(panel, DailyNotionalPanel)
    assert panel.df.height == 1


# ─── v0.2.10 audit-econ #10: unit-mixed counter split ───────────────────────


def test_panel_builder_counters_unit_split(tmp_path: Path) -> None:
    """Audit-econ #10: the OLD ``dropped_rows_count`` mixed three units
    (per-message + per-TRM-row + per-day) into one scalar. The new design
    pins three named counters, each to ONE unit.

    Fixture KNOWN counts:
        - 3 weekend messages (Sat 2026-05-02 + Sat + Sun 2026-05-03).
        - 2 weekend TRM rows (Sat 2026-05-02 + Sun 2026-05-03).
        - 1 weekday TRM-missing day (Tue 2026-05-05 has Claude messages
          but no TRM row → dropped by the inner join).

    The sum of the three new counters equals the old aggregate, preserving
    the existing total for regression-safety. Each counter is also
    independently asserted.
    """
    pricing = _toy_pricing(tmp_path)
    # Messages: 2 weekend rows (Sat=2 x1, Sun=3 x2), 1 Tue=5 (TRM-missing),
    # 1 Wed=6 (TRM present), 1 Thu=7 (TRM present).
    records = [
        _rec(2, uuid_suffix="sat"),
        _rec(3, uuid_suffix="sun-a"),
        _rec(3, uuid_suffix="sun-b"),
        _rec(5, uuid_suffix="tue-no-trm"),
        _rec(6, uuid_suffix="wed-ok"),
        _rec(7, uuid_suffix="thu-ok"),
    ]
    # TRM: omit Tue=5 (the holiday-Monday-equivalent day), include Sat=2 +
    # Sun=3 weekend rows (2 weekend TRM rows), plus weekday rows
    # 4, 6, 7, 8.
    trm = pl.DataFrame(
        {
            "date": [date(2026, 5, d) for d in (2, 3, 4, 6, 7, 8)],
            "trm_cop_per_usd": [4100.0, 4100.0, 4100.0, 4100.0, 4100.0, 4100.0],
        },
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )
    panel = build_daily_panel(_result(records), pricing, trm)

    # Assert each named counter independently.
    assert panel.dropped_weekend_message_count == 3, (
        "expected 3 weekend messages (Sat + 2 Sun)"
    )
    assert panel.dropped_weekend_trm_row_count == 2, (
        "expected 2 weekend TRM rows (Sat + Sun)"
    )
    assert panel.dropped_trm_missing_weekday_count == 1, (
        "expected 1 TRM-missing weekday (Tue=5)"
    )

    # Regression-safety: sum equals what the OLD scalar would have been.
    old_total = (
        panel.dropped_weekend_message_count
        + panel.dropped_weekend_trm_row_count
        + panel.dropped_trm_missing_weekday_count
    )
    assert old_total == 3 + 2 + 1 == 6

    # And the surviving panel rows: Wed=6, Thu=7 (Mon=4 has no records).
    out_dates = set(panel.df["date_utc"].to_list())
    assert out_dates == {date(2026, 5, 6), date(2026, 5, 7)}


def test_panel_builder_trm_missing_weekday_count_surfaces_holidays(
    tmp_path: Path,
) -> None:
    """Audit-econ #1: a weekday (e.g. Mon) with Claude messages but no
    Banrep TRM row must surface in
    ``dropped_trm_missing_weekday_count`` (not silently masked, not
    forward-filled).

    Fixture: Mon 2026-05-04 has Claude messages; the TRM panel
    deliberately omits that day (simulating a Colombian holiday). The
    new day-level counter reports exactly 1.
    """
    pricing = _toy_pricing(tmp_path)
    records = [_rec(4, uuid_suffix="mon-holiday-claude-active")]
    # TRM panel omits Mon=4 → models a Colombian holiday.
    trm = pl.DataFrame(
        {
            "date": [date(2026, 5, d) for d in (5, 6, 7, 8)],
            "trm_cop_per_usd": [4100.0, 4100.0, 4100.0, 4100.0],
        },
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )
    panel = build_daily_panel(_result(records), pricing, trm)
    # Mon=4 is the only Claude-active weekday and it has no TRM row.
    assert panel.dropped_trm_missing_weekday_count == 1
    # No forward-fill: panel is empty.
    assert panel.df.height == 0
    # The other two counters are 0 (no weekend activity in this fixture).
    assert panel.dropped_weekend_message_count == 0
    assert panel.dropped_weekend_trm_row_count == 0
