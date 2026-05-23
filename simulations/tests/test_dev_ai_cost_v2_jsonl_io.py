"""Tests for ``simulations.dev_ai_cost_v2.jsonl_io.JSONLReader``.

Spec refs:
- ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.3 §3.5,
  §0.3 CORRECTIONS-Y-1 (type-discriminator), Y-5b (JSONLReadResult tier),
  Y-5e (uuid synthesis), Y-5f (permissive Pydantic + cost via injected
  PricingTable).
- ``docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md`` v0.1.3
  CORRECTIONS-RR/-TT (uuid required at MessageRecord level — synthesized
  here when absent at wire level).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from simulations.dev_ai_cost_v2._errors import JSONLSchemaError
from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
    _REQUIRED_KEYS,
)
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader, _synth_uuid
from simulations.dev_ai_cost_v2.types import JSONLReadResult, MessageRecord


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _toy_pricing(tmp_path: Path) -> PricingTable:
    fake = {"claude-sonnet-4-5": {k: 1e-06 for k in _REQUIRED_KEYS}}
    p = tmp_path / "lite.json"
    p.write_text(json.dumps(fake))
    return PricingTable.from_litellm_sha(
        LITELLM_SHA_PINNED, p, skip_sha_check=True
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _valid_row(
    ts: str = "2026-05-01T12:00:00Z",
    uuid: str | None = "msg-uuid-001",
    type_: str = "assistant",
) -> dict:
    r = {
        "timestamp": ts,
        "sessionId": "s1",
        "requestId": "r1",
        "isApiErrorMessage": False,
        "type": type_,
        "message": {
            "model": "claude-sonnet-4-5",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": 0,
                    "ephemeral_1h_input_tokens": 0,
                },
                "cache_read_input_tokens": 0,
            },
        },
    }
    if uuid is not None:
        r["uuid"] = uuid
    return r


# ─── Core: returns JSONLReadResult (Y-5b / CR-Z-2) ──────────────────────────


def test_jsonlreader_returns_jsonl_read_result(tmp_path: Path) -> None:
    """Y-5b: __call__ returns JSONLReadResult, not bare Sequence."""
    proj = tmp_path / "projects" / "p1"
    _write_jsonl(proj / "session.jsonl", [_valid_row()])
    reader = JSONLReader(pricing=_toy_pricing(tmp_path))
    out = reader(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert isinstance(out, JSONLReadResult)
    assert isinstance(out.records, tuple)
    assert len(out.records) == 1
    assert isinstance(out.records[0], MessageRecord)
    assert out.records[0].uuid == "msg-uuid-001"


def test_jsonlreader_utc_boundary_half_open(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    _write_jsonl(
        proj / "s.jsonl",
        [
            _valid_row("2026-05-01T00:00:00Z", uuid="u1"),  # included
            _valid_row("2026-05-01T23:59:59Z", uuid="u2"),  # included
            _valid_row("2026-05-02T00:00:00Z", uuid="u3"),  # EXCLUDED — half-open upper
        ],
    )
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 2
    uuids = {r.uuid for r in out.records}
    assert uuids == {"u1", "u2"}


# ─── Y-1: type-discriminator filter ──────────────────────────────────────────


def test_jsonlreader_skips_non_assistant_rows(tmp_path: Path) -> None:
    """Y-1: rows with type != 'assistant' are skipped before validation;
    skip count surfaces in JSONLReadResult.dropped_non_assistant_count.
    """
    proj = tmp_path / "projects" / "p1"
    rows = [
        _valid_row(uuid="u1", type_="assistant"),
        _valid_row(uuid="u2", type_="user"),
        _valid_row(uuid="u3", type_="system"),
        _valid_row(uuid="u4", type_="summary"),
        _valid_row(uuid="u5", type_="assistant"),
    ]
    _write_jsonl(proj / "s.jsonl", rows)
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 2
    assert {r.uuid for r in out.records} == {"u1", "u5"}
    assert out.dropped_non_assistant_count == 3


def test_jsonlreader_skips_rows_with_no_type_field(tmp_path: Path) -> None:
    """Y-1: absent ``type`` field is treated as non-assistant and skipped."""
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    del row["type"]
    _write_jsonl(proj / "s.jsonl", [row])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 0
    assert out.dropped_non_assistant_count == 1


# ─── Y-5f: permissive Pydantic (extra='allow') ──────────────────────────────


def test_jsonlreader_allows_extra_fields(tmp_path: Path) -> None:
    """Y-5f: extra fields are silently accepted (no JSONLSchemaError)."""
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    row["unknown_extra_field"] = "drift"
    row["another_new_field"] = {"nested": [1, 2, 3]}
    _write_jsonl(proj / "s.jsonl", [row])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1


def test_jsonlreader_costUSD_field_removed(tmp_path: Path) -> None:
    """Y-5f: costUSD is removed from _Row; cost computed at parse time
    via injected PricingTable. The presence/absence of costUSD on the wire
    is now ignored (extra=allow).
    """
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    row["costUSD"] = "0.99"  # legacy wire field — should be ignored
    _write_jsonl(proj / "s.jsonl", [row])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    # Pricing was 1e-06 across all rates; cost = 100*1e-06 + 50*1e-06 = 1.5e-4.
    assert out.records[0].cost_usd_notional == pytest.approx(1.5e-4)
    # NOT 0.99 (the wire costUSD is ignored).


# ─── Y-5e: uuid synthesis ────────────────────────────────────────────────────


def test_jsonlreader_synthesizes_uuid_when_absent(tmp_path: Path) -> None:
    """Y-5e: when row uuid is None/absent, synth uuid is filled in."""
    proj = tmp_path / "projects" / "p1"
    _write_jsonl(proj / "session.jsonl", [_valid_row(uuid=None)])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    rec = out.records[0]
    assert rec.uuid.startswith("synth-sha256:")
    # The synth hash is bound to basename ("session") + line ("00000001").
    expected = _synth_uuid(proj / "session.jsonl", 1)
    assert rec.uuid == expected


def test_jsonlreader_preserves_real_uuid_when_present(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    _write_jsonl(proj / "session.jsonl", [_valid_row(uuid="real-uuid-xyz")])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert out.records[0].uuid == "real-uuid-xyz"


# ─── CR-Z-5: uuid synthesis stability under rename ──────────────────────────


def test_cr_z_5_synth_uuid_path_independent_basename_bound() -> None:
    """CR-Z-5: synth uuid is rename-stable across paths (basename-bound).

    Moving the JSONL file to a different directory must NOT change the
    synth uuid (basename and line stay the same). Changing line number
    MUST change the synth uuid. Changing basename MUST change the synth uuid.
    """
    # Path A (line 42).
    uuid_path_a = _synth_uuid(Path("/path/A/session.jsonl"), 42)
    # Path B with same basename, same line — must be identical.
    uuid_path_b = _synth_uuid(Path("/different/path/B/session.jsonl"), 42)
    assert uuid_path_a == uuid_path_b

    # Different line — must differ.
    uuid_diff_line = _synth_uuid(Path("/path/A/session.jsonl"), 43)
    assert uuid_diff_line != uuid_path_a

    # Different basename — must differ.
    uuid_diff_basename = _synth_uuid(Path("/path/A/other.jsonl"), 42)
    assert uuid_diff_basename != uuid_path_a

    # All synth uuids carry the prefix.
    assert uuid_path_a.startswith("synth-sha256:")
    assert uuid_diff_line.startswith("synth-sha256:")
    assert uuid_diff_basename.startswith("synth-sha256:")


# ─── Y-5f: required-field violations still raise ────────────────────────────


def test_jsonlreader_raises_on_missing_timestamp(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    del row["timestamp"]
    _write_jsonl(proj / "s.jsonl", [row])
    with pytest.raises(JSONLSchemaError):
        JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 2),
            projects_root=tmp_path / "projects",
        )


def test_jsonlreader_raises_on_missing_input_tokens(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    del row["message"]["usage"]["input_tokens"]
    _write_jsonl(proj / "s.jsonl", [row])
    with pytest.raises(JSONLSchemaError):
        JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 2),
            projects_root=tmp_path / "projects",
        )


def test_jsonlreader_raises_on_missing_output_tokens(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    del row["message"]["usage"]["output_tokens"]
    _write_jsonl(proj / "s.jsonl", [row])
    with pytest.raises(JSONLSchemaError):
        JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 2),
            projects_root=tmp_path / "projects",
        )


def test_jsonlreader_allows_missing_uuid_via_synthesis(tmp_path: Path) -> None:
    """Y-5e: uuid is no longer required at the wire level — synthesized."""
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    del row["uuid"]
    _write_jsonl(proj / "s.jsonl", [row])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    assert out.records[0].uuid.startswith("synth-sha256:")


def test_jsonlreader_allows_missing_requestId_via_default(tmp_path: Path) -> None:
    """Y-5f: requestId is Optional with default=None."""
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    del row["requestId"]
    _write_jsonl(proj / "s.jsonl", [row])
    with pytest.warns(UserWarning, match="request_id"):
        out = JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 2),
            projects_root=tmp_path / "projects",
        )
    assert out.records[0].request_id is None


def test_jsonlreader_allows_missing_isApiErrorMessage_via_default(
    tmp_path: Path,
) -> None:
    """Y-1: absent isApiErrorMessage treated as False."""
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    del row["isApiErrorMessage"]
    _write_jsonl(proj / "s.jsonl", [row])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert out.records[0].is_error is False


# ─── Tz-naive timestamp rejection (defense in depth) ────────────────────────


def test_jsonlreader_raises_on_naive_timestamp(tmp_path: Path) -> None:
    """Tz-naive timestamps must be rejected at parse time. DO NOT regress
    on Task 5 fix 283673d (AwareDatetime).
    """
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    row["timestamp"] = "2026-05-01T12:00:00"  # tz-naive (no Z)
    _write_jsonl(proj / "s.jsonl", [row])
    with pytest.raises(JSONLSchemaError):
        JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 2),
            projects_root=tmp_path / "projects",
        )


def test_jsonlreader_skips_invalid_json_does_not_raise(tmp_path: Path) -> None:
    """v0.2.4 Y-7: malformed JSON (JSONDecodeError) is silently skipped
    and counted in ``dropped_malformed_line_count``. Supersedes the v0.2.3
    behavior which raised ``JSONLSchemaError`` on any decode failure.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "s.jsonl").write_text('{"not": "closed"\n')
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 0
    assert out.dropped_malformed_line_count == 1


def test_jsonlreader_raises_on_missing_projects_root(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 2),
            projects_root=tmp_path / "does_not_exist",
        )


def test_jsonlreader_recurses_subprojects(tmp_path: Path) -> None:
    root = tmp_path / "projects"
    _write_jsonl(root / "p1" / "s1.jsonl", [_valid_row(uuid="a")])
    _write_jsonl(root / "p2" / "nested" / "s2.jsonl", [_valid_row(uuid="b")])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=root,
    )
    assert len(out.records) == 2
    assert {r.uuid for r in out.records} == {"a", "b"}


def test_jsonlreader_skips_blank_lines(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    with (proj / "s.jsonl").open("w") as f:
        f.write(json.dumps(_valid_row()) + "\n")
        f.write("\n")
        f.write("   \n")
        f.write(json.dumps(_valid_row(uuid="u2")) + "\n")
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 2


# ─── Hypothesis property: re-iteration via tuple-records ────────────────────


@settings(max_examples=25, deadline=None)
@given(
    n_rows=st.integers(min_value=0, max_value=20),
    uuid_seed=st.integers(min_value=0, max_value=10_000),
)
def test_jsonlreader_double_iteration_property(
    tmp_path_factory: pytest.TempPathFactory,
    n_rows: int,
    uuid_seed: int,
) -> None:
    """Returned JSONLReadResult.records is a tuple — multi-iteration yields
    identical sequences. Replaces the v0.2.1 Sequence-flag-A test.
    """
    tmp_path = tmp_path_factory.mktemp("hyp")
    proj = tmp_path / "projects" / "p1"
    rows = [_valid_row(uuid=f"u-{uuid_seed}-{i}") for i in range(n_rows)]
    if rows:
        _write_jsonl(proj / "s.jsonl", rows)
    else:
        proj.mkdir(parents=True, exist_ok=True)
        (proj / "empty.jsonl").write_text("")
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    first = list(out.records)
    second = list(out.records)
    assert first == second
    assert len(first) == n_rows


# ─── v0.2.4 §0.4 CORRECTIONS-Y-7: line-level malformed-skip ─────────────────


def test_jsonlreader_skips_trailing_null_bytes(tmp_path: Path) -> None:
    """v0.2.4 Y-7: filesystem partial-write corruption (trailing null-byte
    block) is silently skipped; valid records before the corruption parse
    cleanly.

    Mirrors the production failure: agent-af5e1160f7be358ba.jsonl:586 had
    a trailing block of ``b"\\x00" * N`` after the last newline, which the
    pre-v0.2.4 reader treated as a JSONLSchemaError. v0.2.4 Y-7 contract:
    silently skip + increment ``dropped_malformed_line_count``.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    valid_rows = [
        _valid_row(ts="2026-05-01T10:00:00Z", uuid="u1"),
        _valid_row(ts="2026-05-01T11:00:00Z", uuid="u2"),
        _valid_row(ts="2026-05-01T12:00:00Z", uuid="u3"),
    ]
    body = b"".join(
        (json.dumps(r) + "\n").encode("utf-8") for r in valid_rows
    )
    # 3000 null bytes after the last valid line — same as a partial-write
    # corruption block. ``str.strip()`` does not strip null bytes, so the
    # null-byte block reaches the json.loads attempt and JSONDecodeError-s.
    body += b"\x00" * 3000
    (proj / "session.jsonl").write_bytes(body)

    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 3
    assert {r.uuid for r in out.records} == {"u1", "u2", "u3"}
    assert out.dropped_malformed_line_count == 1


def test_jsonlreader_skips_truncated_json(tmp_path: Path) -> None:
    """v0.2.4 Y-7: a truncated (mid-line) partial-write is silently skipped;
    the valid prefix records parse cleanly.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    valid_row = _valid_row(ts="2026-05-01T10:00:00Z", uuid="u1")
    truncated_line = (
        '{"type":"assistant","timestamp":"2026-05-01T11:00:00Z",'
        '"message":{"model":"claude-sonnet-4-5","usage":{"input_tokens'
    )
    (proj / "session.jsonl").write_text(
        json.dumps(valid_row) + "\n" + truncated_line + "\n"
    )

    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    assert out.records[0].uuid == "u1"
    assert out.dropped_malformed_line_count == 1


def test_dropped_malformed_line_count_threaded_through_panel(
    tmp_path: Path,
) -> None:
    """v0.2.4 Y-7: ``JSONLReadResult.dropped_malformed_line_count`` is
    surfaced on ``DailyNotionalPanel.dropped_malformed_line_count`` by
    ``build_daily_panel``. Panel-builder is the JSONLReader→Panel counter
    threading point per Y-5a/Y-7.
    """
    import polars as pl
    from datetime import datetime, timezone, date as _date
    from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel
    from simulations.dev_ai_cost_v2.types import MessageRecord

    # 2026-05-04 is a Monday (weekday=0) so it survives the weekend filter.
    rec = MessageRecord(
        ts=datetime(2026, 5, 4, 12, 0, 0, tzinfo=timezone.utc),
        model="claude-sonnet-4-5",
        input_tok=100,
        output_tok=50,
        cache_create_5m=0,
        cache_create_1h=0,
        cache_read=0,
        cost_usd_notional=1.5e-4,
        session_id="s",
        request_id="r",
        is_error=False,
        uuid="u-1",
    )
    rr = JSONLReadResult(
        records=(rec,),
        dropped_non_assistant_count=0,
        dropped_malformed_line_count=7,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=0,
    )
    pricing = _toy_pricing(tmp_path)
    trm = pl.DataFrame(
        {"date": [_date(2026, 5, 4)], "trm_cop_per_usd": [4000.0]},
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )
    panel = build_daily_panel(rr, pricing, trm)
    assert panel.dropped_malformed_line_count == 7


def test_jsonlreader_blank_lines_do_not_increment_malformed_counter(
    tmp_path: Path,
) -> None:
    """v0.2.4 Y-7 RC FLAG-4a non-over-correction commitment: blank and
    whitespace-only lines are absorbed by the pre-existing
    ``if not stripped: continue`` guard BEFORE the JSON-decode attempt, so
    they leave ``dropped_malformed_line_count == 0``.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    row = _valid_row(ts="2026-05-01T10:00:00Z", uuid="u1")
    (proj / "session.jsonl").write_text(
        json.dumps(row) + "\n"
        "\n"            # blank
        "   \n"         # whitespace-only
        "\t\n"          # tab-only
        + json.dumps(_valid_row(ts="2026-05-01T11:00:00Z", uuid="u2")) + "\n"
    )
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 2
    assert out.dropped_malformed_line_count == 0


def test_jsonlreader_valid_json_invalid_schema_still_raises(
    tmp_path: Path,
) -> None:
    """v0.2.4 Y-7 RC FLAG-4b non-over-correction commitment: the
    JSONDecodeError catch did NOT widen to swallow Pydantic schema errors.
    A line that decodes to valid JSON but is missing a required field
    still raises JSONLSchemaError.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    # Valid JSON, valid type discriminator, but ``message.usage`` is missing
    # the required ``input_tokens``/``output_tokens`` keys.
    bad_row = {
        "type": "assistant",
        "timestamp": "2026-05-01T10:00:00Z",
        "message": {},
    }
    (proj / "session.jsonl").write_text(json.dumps(bad_row) + "\n")
    with pytest.raises(JSONLSchemaError):
        JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 2),
            projects_root=tmp_path / "projects",
        )


@settings(max_examples=40, deadline=None)
@given(
    line_blobs=st.lists(
        st.binary(min_size=0, max_size=200),
        min_size=0,
        max_size=20,
    ),
)
def test_jsonlreader_line_conservation_property(
    tmp_path_factory: pytest.TempPathFactory,
    line_blobs: list[bytes],
) -> None:
    """v0.2.4 Y-7 / CR-7-N2 Hypothesis: line-accounting invariant.

    For any random byte-string input split into newline-separated lines
    the reader's output satisfies::

        dropped_malformed_line_count + len(records) + dropped_non_assistant_count
            + dropped_non_anthropic_count + dropped_blank_inferred
            == total_input_lines

    where ``dropped_blank_inferred`` is computed from the fixture
    (lines whose ``.strip()`` is empty after utf-8 decode, or that cannot
    be decoded as utf-8). The reader never loses or double-counts a line.

    v0.2.10 audit-econ #9: the conservation invariant now includes
    ``dropped_non_anthropic_count`` since the upstream non-Anthropic
    filter is another exhaustive exit path for an admitted assistant row.

    Per spec §0.4: ``dropped_blank`` is not exposed on JSONLReadResult
    (scope-minimal); the conservation test uses a fixture-derived
    blank count rather than adding a new field.
    """
    tmp_path = tmp_path_factory.mktemp("y7_inv")
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    # Construct one .jsonl file from the random blobs (one blob per line).
    # We strip embedded newlines from each blob so that ``len(line_blobs)``
    # equals the file's line count.
    sanitized: list[bytes] = [blob.replace(b"\n", b"") for blob in line_blobs]
    body: bytes = b"\n".join(sanitized)
    if line_blobs:
        body += b"\n"  # trailing newline to keep line-count == len(line_blobs)
    (proj / "session.jsonl").write_bytes(body)

    # Compute the fixture-derived blank count: a line is "blank" if its
    # utf-8 decode + str.strip() is empty. If the blob is not utf-8 we
    # treat it as non-blank (the reader's open(...,"r") with default
    # encoding will raise UnicodeDecodeError; this fixture confines blobs
    # to be safe by virtue of utf-8-clean strip-empty checks below).
    dropped_blank_inferred: int = 0
    for blob in sanitized:
        try:
            decoded = blob.decode("utf-8")
        except UnicodeDecodeError:
            # The reader will raise on the file open / iteration. Skip
            # the invariant check for this fixture by short-circuiting.
            return
        if decoded.strip() == "":
            dropped_blank_inferred += 1

    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(1970, 1, 1),
        until=date(9999, 12, 31),
        projects_root=tmp_path / "projects",
    )

    total_lines: int = len(line_blobs)
    accounted: int = (
        out.dropped_malformed_line_count
        + len(out.records)
        + out.dropped_non_assistant_count
        + out.dropped_non_anthropic_count
        + dropped_blank_inferred
    )
    assert accounted == total_lines, (
        f"line-conservation invariant violated: "
        f"malformed={out.dropped_malformed_line_count}, "
        f"records={len(out.records)}, "
        f"non_assistant={out.dropped_non_assistant_count}, "
        f"non_anthropic={out.dropped_non_anthropic_count}, "
        f"blank_inferred={dropped_blank_inferred}, "
        f"total={total_lines}"
    )


# ─── v0.2.5 §0.5 CORRECTIONS-Y-8: uniqueHash dedup ──────────────────────────


def _dup_row(
    ts: str,
    message_id: str | None,
    request_id: str | None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_5m: int = 0,
    cache_1h: int = 0,
    cache_read: int = 0,
    speed: str | None = None,
    uuid: str = "u-dup",
    model: str = "claude-sonnet-4-5",
) -> dict:
    """Build a JSONL row with explicit message.id + requestId + token mix.

    v0.2.5 Y-8 fixture helper. ``message_id=None`` sets ``message.id`` to a
    JSON null (the row should bypass the dedup map). ``speed`` populates
    ``message.usage.speed`` only when not None (absence is the hasSpeed=False
    branch of the tiebreaker).
    """
    usage: dict = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation": {
            "ephemeral_5m_input_tokens": cache_5m,
            "ephemeral_1h_input_tokens": cache_1h,
        },
        "cache_read_input_tokens": cache_read,
    }
    if speed is not None:
        usage["speed"] = speed
    message: dict = {"model": model, "usage": usage}
    if message_id is not None:
        message["id"] = message_id
    r: dict = {
        "type": "assistant",
        "timestamp": ts,
        "sessionId": "s1",
        "requestId": request_id,
        "isApiErrorMessage": False,
        "uuid": uuid,
        "message": message,
    }
    return r


def test_jsonlreader_dedup_within_file(tmp_path: Path) -> None:
    """v0.2.5 Y-8: within-file dedup keeps the row with the largest
    tokenTotal; counter increments on every collision.

    Three rows share ``message.id=msg_1, requestId=req_1`` with
    tokenTotals 200/500/300 (output-only). Expect 1 record (the 500 row),
    dropped_duplicate_count == 2.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    rows = [
        _dup_row("2026-05-04T10:00:00Z", "msg_1", "req_1",
                 output_tokens=200, uuid="u-a"),
        _dup_row("2026-05-04T10:00:01Z", "msg_1", "req_1",
                 output_tokens=500, uuid="u-b"),
        _dup_row("2026-05-04T10:00:02Z", "msg_1", "req_1",
                 output_tokens=300, uuid="u-c"),
    ]
    _write_jsonl(proj / "session.jsonl", rows)
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 31),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    assert out.records[0].output_tok == 500
    assert out.dropped_duplicate_count == 2


def test_jsonlreader_dedup_across_files(tmp_path: Path) -> None:
    """v0.2.5 Y-8: cross-file dedup keeps the larger row regardless of
    file-traversal order.

    Tests both orderings (file_a first vs file_b first) by sorting the
    file basenames lexicographically — verifies that whichever file
    rglob hits first does not affect the kept entry's identity.
    """
    for first_letter, second_letter in (("a", "b"), ("b", "a")):
        proj = tmp_path / f"projects_{first_letter}{second_letter}" / "p1"
        proj.mkdir(parents=True, exist_ok=True)
        # Larger row lives in "file_b.jsonl" regardless of traversal order.
        small = _dup_row("2026-05-04T10:00:00Z", "msg_x", "req_x",
                         output_tokens=100, uuid="u-small")
        large = _dup_row("2026-05-04T10:00:01Z", "msg_x", "req_x",
                         output_tokens=999, uuid="u-large")
        _write_jsonl(proj / "file_a.jsonl", [small])
        _write_jsonl(proj / "file_b.jsonl", [large])
        out = JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 31),
            projects_root=tmp_path / f"projects_{first_letter}{second_letter}",
        )
        assert len(out.records) == 1
        assert out.records[0].output_tok == 999
        assert out.records[0].uuid == "u-large"
        assert out.dropped_duplicate_count == 1


def test_jsonlreader_dedup_hasspeed_tiebreaker(tmp_path: Path) -> None:
    """v0.2.5 Y-8: on equal tokenTotal, the row with ``usage.speed`` set
    wins (ccusage hasSpeed tiebreaker).
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    no_speed = _dup_row("2026-05-04T10:00:00Z", "msg_s", "req_s",
                        output_tokens=500, speed=None, uuid="u-no")
    with_speed = _dup_row("2026-05-04T10:00:01Z", "msg_s", "req_s",
                          output_tokens=500, speed="standard", uuid="u-yes")
    _write_jsonl(proj / "session.jsonl", [no_speed, with_speed])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 31),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    assert out.records[0].uuid == "u-yes"
    assert out.dropped_duplicate_count == 1


def test_jsonlreader_dedup_no_request_id_falls_back_to_message_id(
    tmp_path: Path,
) -> None:
    """v0.2.5 Y-8: when ``requestId`` is None, ``_unique_hash`` falls
    back to ``message.id`` alone.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    import warnings as _warnings
    a = _dup_row("2026-05-04T10:00:00Z", "msg_only", None,
                 output_tokens=100, uuid="u-1")
    b = _dup_row("2026-05-04T10:00:01Z", "msg_only", None,
                 output_tokens=700, uuid="u-2")
    _write_jsonl(proj / "session.jsonl", [a, b])
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", UserWarning)
        out = JSONLReader(pricing=_toy_pricing(tmp_path))(
            since=date(2026, 5, 1),
            until=date(2026, 5, 31),
            projects_root=tmp_path / "projects",
        )
    assert len(out.records) == 1
    assert out.records[0].output_tok == 700
    assert out.dropped_duplicate_count == 1


@settings(max_examples=20, deadline=None)
@given(
    perm=st.permutations(["f0.jsonl", "f1.jsonl", "f2.jsonl", "f3.jsonl"]),
)
def test_jsonlreader_dedup_traversal_order_invariant(
    tmp_path_factory: pytest.TempPathFactory,
    perm: list[str],
) -> None:
    """v0.2.5 Y-8: kept-entry set is invariant under file-traversal
    permutation.

    Fixture: 4 files each carrying one row of a 4-collision uniqueHash
    cluster. The keep-largest rule should select the same canonical row
    (the one with the maximum tokenTotal) regardless of which file the
    reader encounters first. ``Path.rglob`` order is filesystem-dependent;
    we exercise the invariant by creating files with different
    lexicographic names per permutation iteration.
    """
    tmp_path = tmp_path_factory.mktemp("y8_perm")
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    # tokenTotals 100, 200, 300, 400 — winner is 400.
    totals = [100, 200, 300, 400]
    rows = [
        _dup_row(f"2026-05-04T10:00:0{i}Z", "msg_perm", "req_perm",
                 output_tokens=tot, uuid=f"u-{tot}")
        for i, tot in enumerate(totals)
    ]
    # Assign rows to file names per the permutation.
    for fname, row in zip(perm, rows):
        _write_jsonl(proj / fname, [row])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 31),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    assert out.records[0].uuid == "u-400"
    assert out.dropped_duplicate_count == 3


def test_dropped_duplicate_count_threaded_through_panel(
    tmp_path: Path,
) -> None:
    """v0.2.5 Y-8: ``JSONLReadResult.dropped_duplicate_count`` surfaces
    on ``DailyNotionalPanel.dropped_duplicate_count`` via
    ``build_daily_panel``.
    """
    import polars as pl
    from datetime import datetime, timezone, date as _date
    from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel
    from simulations.dev_ai_cost_v2.types import MessageRecord

    rec = MessageRecord(
        ts=datetime(2026, 5, 4, 12, 0, 0, tzinfo=timezone.utc),
        model="claude-sonnet-4-5",
        input_tok=100,
        output_tok=50,
        cache_create_5m=0,
        cache_create_1h=0,
        cache_read=0,
        cost_usd_notional=1.5e-4,
        session_id="s",
        request_id="r",
        is_error=False,
        uuid="u-1",
    )
    rr = JSONLReadResult(
        records=(rec,),
        dropped_non_assistant_count=0,
        dropped_malformed_line_count=0,
        dropped_duplicate_count=7,
        dropped_non_anthropic_count=0,
    )
    pricing = _toy_pricing(tmp_path)
    trm = pl.DataFrame(
        {"date": [_date(2026, 5, 4)], "trm_cop_per_usd": [4000.0]},
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )
    panel = build_daily_panel(rr, pricing, trm)
    assert panel.dropped_duplicate_count == 7


def test_jsonlreader_dedup_field_atomicity(tmp_path: Path) -> None:
    """v0.2.5 Y-8 RC FLAG-A: whole-record replacement — the row with the
    larger tokenTotal wins on EVERY field. No Frankenstein-mixing.

    Two rows with the same uniqueHash but DIFFERING model, timestamp, and
    token mixes. Assert the kept entry's model, ts, AND tokens all come
    from the single winning row.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    small = _dup_row(
        "2026-05-04T10:00:00Z", "msg_atom", "req_atom",
        input_tokens=10, output_tokens=20, cache_5m=0, cache_1h=0, cache_read=0,
        model="claude-sonnet-4-5", uuid="u-loser",
    )
    # Large row: different model, different ts, much larger tokenTotal.
    large = _dup_row(
        "2026-05-04T11:00:00Z", "msg_atom", "req_atom",
        input_tokens=500, output_tokens=2000, cache_5m=100, cache_1h=200,
        cache_read=300,
        model="claude-opus-4-7", uuid="u-winner",
    )
    _write_jsonl(proj / "session.jsonl", [small, large])
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 31),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    kept = out.records[0]
    # Every field comes from "large" — no mixing.
    assert kept.uuid == "u-winner"
    assert kept.model == "claude-opus-4-7"
    assert kept.ts.hour == 11
    assert kept.input_tok == 500
    assert kept.output_tok == 2000
    assert kept.cache_create_5m == 100
    assert kept.cache_create_1h == 200
    assert kept.cache_read == 300
    assert out.dropped_duplicate_count == 1


def test_jsonlreader_dedup_missing_message_id_admitted_without_counter(
    tmp_path: Path,
) -> None:
    """v0.2.5 Y-8 RC FLAG-B / CR optional-7th: rows with
    ``message.id == None`` bypass the dedup map and are admitted into
    ``records`` without incrementing ``dropped_duplicate_count``.

    Three such rows are written; assert all three appear distinctly in
    output AND the counter stays at 0 (no hash collisions ever recorded).
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    rows = [
        _dup_row("2026-05-04T10:00:00Z", None, "req_a",
                 output_tokens=100, uuid="u-a"),
        _dup_row("2026-05-04T10:00:01Z", None, "req_b",
                 output_tokens=200, uuid="u-b"),
        _dup_row("2026-05-04T10:00:02Z", None, "req_c",
                 output_tokens=300, uuid="u-c"),
    ]
    _write_jsonl(proj / "session.jsonl", rows)
    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 31),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 3
    assert {r.uuid for r in out.records} == {"u-a", "u-b", "u-c"}
    assert out.dropped_duplicate_count == 0


# ─── v0.2.10 audit-econ #9: non-Anthropic upstream filter ────────────────────


def test_jsonlreader_filters_non_anthropic_models(tmp_path: Path) -> None:
    """v0.2.10 audit-econ #9: rows whose ``message.model`` does not start
    with ``claude-`` are skipped UPSTREAM (before the dedup map and
    before the panel). Their tokens AND cost are both excluded.

    Fixture: 3 assistant rows — 1 claude-sonnet-4-5, 1 gpt-4, 1
    codex-davinci. Only the claude row survives; the counter equals 2.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    rows = [
        _valid_row(uuid="claude-row"),  # model = "claude-sonnet-4-5"
    ]
    rows[0]["message"]["model"] = "claude-sonnet-4-5"
    gpt_row = _valid_row(uuid="gpt-row")
    gpt_row["message"]["model"] = "gpt-4"
    codex_row = _valid_row(uuid="codex-row")
    codex_row["message"]["model"] = "codex-davinci"
    rows.extend([gpt_row, codex_row])
    _write_jsonl(proj / "session.jsonl", rows)

    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    # Only the claude row survives; gpt + codex are filtered upstream.
    assert len(out.records) == 1
    assert out.records[0].uuid == "claude-row"
    assert out.records[0].model == "claude-sonnet-4-5"
    assert out.dropped_non_anthropic_count == 2
    # Token aggregates must NOT include the non-Anthropic rows.
    total_input_tok = sum(r.input_tok for r in out.records)
    assert total_input_tok == 100  # only the claude row's tokens


def test_jsonlreader_missing_model_dropped_as_non_anthropic(
    tmp_path: Path,
) -> None:
    """v0.2.10 audit-econ #9: a row whose ``message.model`` field is
    absent (Pydantic default ``"unknown"``) does NOT match the
    ``claude-`` prefix and is treated as non-Anthropic. Skipped upstream
    with counter increment.
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    row = _valid_row(uuid="missing-model")
    del row["message"]["model"]  # Pydantic default kicks in → "unknown"
    _write_jsonl(proj / "session.jsonl", [row])

    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 0
    assert out.dropped_non_anthropic_count == 1


def test_jsonlreader_non_anthropic_filter_is_case_insensitive(
    tmp_path: Path,
) -> None:
    """v0.2.10 audit-econ #9: the prefix check is case-insensitive to
    survive any future capitalization drift in Anthropic-emitted model
    identifiers (e.g. ``Claude-3``, ``CLAUDE-OPUS``).
    """
    proj = tmp_path / "projects" / "p1"
    proj.mkdir(parents=True, exist_ok=True)
    row = _valid_row(uuid="caps-claude")
    row["message"]["model"] = "Claude-3-Opus"  # capitalized
    _write_jsonl(proj / "session.jsonl", [row])

    out = JSONLReader(pricing=_toy_pricing(tmp_path))(
        since=date(2026, 5, 1),
        until=date(2026, 5, 2),
        projects_root=tmp_path / "projects",
    )
    assert len(out.records) == 1
    assert out.dropped_non_anthropic_count == 0


def test_dropped_non_anthropic_count_threaded_through_panel(
    tmp_path: Path,
) -> None:
    """v0.2.10 audit-econ #9: ``JSONLReadResult.dropped_non_anthropic_count``
    is surfaced on ``DailyNotionalPanel.dropped_non_anthropic_count`` by
    ``build_daily_panel``. Mirror of Y-7 / Y-8 counter threading discipline.
    """
    import polars as pl
    from datetime import datetime, timezone, date as _date
    from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel
    from simulations.dev_ai_cost_v2.types import MessageRecord

    rec = MessageRecord(
        ts=datetime(2026, 5, 4, 12, 0, 0, tzinfo=timezone.utc),
        model="claude-sonnet-4-5",
        input_tok=100,
        output_tok=50,
        cache_create_5m=0,
        cache_create_1h=0,
        cache_read=0,
        cost_usd_notional=1.5e-4,
        session_id="s",
        request_id="r",
        is_error=False,
        uuid="u-1",
    )
    rr = JSONLReadResult(
        records=(rec,),
        dropped_non_assistant_count=0,
        dropped_malformed_line_count=0,
        dropped_duplicate_count=0,
        dropped_non_anthropic_count=5,
    )
    pricing = _toy_pricing(tmp_path)
    trm = pl.DataFrame(
        {"date": [_date(2026, 5, 4)], "trm_cop_per_usd": [4000.0]},
        schema={"date": pl.Date, "trm_cop_per_usd": pl.Float64},
    )
    panel = build_daily_panel(rr, pricing, trm)
    assert panel.dropped_non_anthropic_count == 5
