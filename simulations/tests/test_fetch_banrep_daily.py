"""Tests for the daily Banrep TRM endpoint added to ``scripts/fetch_banrep.py``.

Plan ref: ``docs/plans/2026-05-16-ai-cost-factor-model-plan.md`` Task 1.
Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` §3.4 + §0.1
CORRECTIONS-E (prerequisite for ``dev_ai_cost_v2`` daily-COP cost work).

Coverage:

* **Schema regression** — the emitted parquet has the contractual schema
  ``(date: Date, trm_cop_per_usd: Decimal)`` and at least 15 weekday rows in a
  half-month window.
* **Provenance metadata** — a sidecar JSON next to the parquet captures
  endpoint URL, fetch timestamp, response sha256, and the requested window.
* **Monthly endpoint regression** — the existing ``main()`` printout for the
  monthly Pair D path is preserved (no daily endpoint should break the
  pre-existing CLI surface).
* **Hypothesis property** — the row-normalizer (``_normalize_row``) accepts
  well-formed Socrata rows and rejects malformed rows with ``ValueError``.

Both the schema regression and provenance tests stub the HTTP layer with
``monkeypatch`` to keep the suite offline; the malformed-row test exercises
the pure normalizer with no network involvement.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import polars as pl
import pytest
from hypothesis import given, strategies as st


# ── Hypothesis strategies for the Socrata row normalizer ─────────────────────
#
# Socrata's ``32sa-8pi3`` dataset returns each row as a dict with at minimum
# the fields ``valor`` (string-encoded TRM in COP per USD) and
# ``vigenciadesde`` (ISO-8601 date with ``T00:00:00.000`` suffix). The
# normalizer must accept these and emit ``(date, Decimal)``; everything else
# is malformed and must raise ``ValueError``.

_VALOR_RE_OK = st.decimals(
    min_value=Decimal("100.00"),
    max_value=Decimal("10000.0000"),
    allow_nan=False,
    allow_infinity=False,
    places=4,
).map(lambda d: format(d, "f"))

_DATE_RE_OK = st.dates(
    min_value=date(1991, 12, 1),
    max_value=date(2030, 12, 31),
).map(lambda d: f"{d.isoformat()}T00:00:00.000")


@st.composite
def _well_formed_row(draw: st.DrawFn) -> dict[str, str]:
    return {
        "valor": draw(_VALOR_RE_OK),
        "vigenciadesde": draw(_DATE_RE_OK),
        "vigenciahasta": draw(_DATE_RE_OK),
    }


@st.composite
def _malformed_row(draw: st.DrawFn) -> dict[str, str]:
    """Generate a row missing one of the required fields, or with bad types."""
    kind = draw(st.sampled_from(["missing_valor", "missing_fecha", "bad_valor"]))
    row: dict[str, str] = {
        "valor": draw(_VALOR_RE_OK),
        "vigenciadesde": draw(_DATE_RE_OK),
    }
    if kind == "missing_valor":
        row.pop("valor")
    elif kind == "missing_fecha":
        row.pop("vigenciadesde")
    elif kind == "bad_valor":
        row["valor"] = draw(
            st.text(alphabet=st.characters(blacklist_categories=("Nd",)), min_size=1, max_size=8)
        )
    return row


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_socrata_payload() -> list[dict[str, str]]:
    """Synthetic Socrata response covering 2024-01-01 .. 2024-01-31 weekdays.

    ``vigenciadesde`` ranges are 1-day in the real Banrep feed for weekdays
    and longer over weekends/holidays (the TRM publication carries forward
    over non-trading days). For test purposes we emit 1 row per calendar day
    so that the half-month-of-weekdays floor is comfortably met.
    """
    payload: list[dict[str, str]] = []
    for day in range(1, 32):
        iso = f"2024-01-{day:02d}T00:00:00.000"
        payload.append(
            {
                "valor": f"{3900.0 + day:.4f}",
                "vigenciadesde": iso,
                "vigenciahasta": iso,
            }
        )
    return payload


# ── Daily endpoint: schema + provenance ─────────────────────────────────────


def test_daily_trm_emits_parquet_with_expected_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_socrata_payload: list[dict[str, str]],
) -> None:
    """``fetch_daily_trm`` writes ``(date, trm_cop_per_usd)`` parquet."""
    from scripts import fetch_banrep

    monkeypatch.setattr(
        fetch_banrep, "_http_get_trm_json", lambda _url, _params: fake_socrata_payload
    )

    out = tmp_path / "banrep_trm_daily.parquet"
    fetch_banrep.fetch_daily_trm(out_path=out, since="2024-01-01", until="2024-01-31")

    df = pl.read_parquet(out)
    assert df.columns == ["date", "trm_cop_per_usd"], df.columns
    assert df.schema["date"] == pl.Date
    # trm_cop_per_usd is exact Decimal (CORRECTIONS-V). Polars Decimal carries
    # (precision, scale); we assert it is a Decimal dtype regardless of scale.
    assert df.schema["trm_cop_per_usd"].is_decimal()
    assert df.height >= 15


def test_daily_trm_writes_provenance_sidecar(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_socrata_payload: list[dict[str, str]],
) -> None:
    """A ``.provenance.json`` sidecar records endpoint, fetch ts, sha256."""
    from scripts import fetch_banrep

    monkeypatch.setattr(
        fetch_banrep, "_http_get_trm_json", lambda _url, _params: fake_socrata_payload
    )

    out = tmp_path / "banrep_trm_daily.parquet"
    fetch_banrep.fetch_daily_trm(out_path=out, since="2024-01-01", until="2024-01-31")

    sidecar = out.with_suffix(out.suffix + ".provenance.json")
    assert sidecar.exists(), f"missing provenance sidecar: {sidecar}"
    meta = json.loads(sidecar.read_text())
    assert meta["endpoint"] == fetch_banrep._TRM_DAILY_ENDPOINT
    assert meta["since"] == "2024-01-01"
    assert meta["until"] == "2024-01-31"
    assert isinstance(meta["fetched_at_utc"], str) and meta["fetched_at_utc"].endswith("Z")
    assert isinstance(meta["payload_sha256"], str) and len(meta["payload_sha256"]) == 64


def test_daily_trm_rejects_inverted_window(tmp_path: Path) -> None:
    """``since > until`` violates the documented invariant — must raise."""
    from scripts import fetch_banrep

    out = tmp_path / "banrep_trm_daily.parquet"
    with pytest.raises(ValueError, match="since.*until"):
        fetch_banrep.fetch_daily_trm(out_path=out, since="2024-02-01", until="2024-01-01")


def test_daily_trm_rejects_non_iso_dates(tmp_path: Path) -> None:
    """Non-ISO date inputs violate the documented invariant — must raise."""
    from scripts import fetch_banrep

    out = tmp_path / "banrep_trm_daily.parquet"
    with pytest.raises(ValueError):
        fetch_banrep.fetch_daily_trm(out_path=out, since="01-01-2024", until="2024-01-31")


# ── Monthly endpoint: regression on existing main() ─────────────────────────


def test_monthly_main_preserved(capsys: pytest.CaptureFixture[str]) -> None:
    """The pre-existing ``main()`` printout for the Pair D monthly path is preserved."""
    from scripts import fetch_banrep

    rc = fetch_banrep.main()
    captured = capsys.readouterr().out
    assert rc == 0
    assert "Banrep" in captured
    assert "TRM" in captured
    # The pointer to the Pair D scratch fetcher must remain — downstream
    # notebooks reference it for monthly EOM aggregation provenance.
    assert "scratch/simple-beta-pair-d" in captured


# ── Hypothesis property tests on the row normalizer ─────────────────────────


@given(row=_well_formed_row())
def test_normalize_well_formed_row_returns_tuple(row: dict[str, str]) -> None:
    from scripts.fetch_banrep import _normalize_row

    parsed_date, parsed_value = _normalize_row(row)
    assert isinstance(parsed_date, date)
    assert isinstance(parsed_value, Decimal)
    assert parsed_value > 0


@given(row=_malformed_row())
def test_normalize_malformed_row_raises_value_error(row: dict[str, str]) -> None:
    from scripts.fetch_banrep import _normalize_row

    with pytest.raises(ValueError):
        _normalize_row(row)
