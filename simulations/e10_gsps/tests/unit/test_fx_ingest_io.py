"""Phase-1 tests for the FX-series ingest IO unit (plan task 1.1 — E10.0).

Exercises ``FXSeriesIngest`` / ``FXIngestResult`` and the per-currency
payload parser against the **real frozen Tier-2 snapshots** under
``data/raw/e10_gsps/fx/`` — not a mock — per
``memory/feedback_real_data_over_mocks.md``. The snapshots are the
deterministic central-bank pulls frozen at E10.0; the parser is
round-tripped against them so the parse path is covered using only the
real frozen central-bank payloads.

Also covers the HALT-DV branch: a currency dropped at E10.0
(ZAR / KES / GHS — CORRECTIONS-E10-5) is rejected honestly by
``fetch_currency`` — it is not a v0.5 panel currency and surfaces a
``ValueError`` rather than a flat-filled or placeholder series.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote

import pytest

from simulations.e10_gsps._errors import DataVisibilityRevokedError
from simulations.e10_gsps.types import PANEL_CURRENCIES, CurrencyDailyFXRow
from simulations.e10_gsps.utils.fx_ingest_io import (
    HALT_DV_CURRENCIES,
    FXIngestResult,
    FXSeriesIngest,
    _FX_URL_BUILDER,
    _parse_currency_payload,
)

# ── Real frozen Tier-2 snapshot directory (NOT a mock) ───────────────────
_REPO_ROOT = Path(__file__).resolve().parents[4]
_FX_SNAPSHOT_DIR = _REPO_ROOT / "data" / "raw" / "e10_gsps" / "fx"

# The pinned v0.5 panel window (spec v0.5 §3.3 — 2023-11-01 → 2026-04-30).
_PANEL_SINCE = "2023-11-01"
_PANEL_UNTIL = "2026-04-30"


def _frozen_snapshot(currency: str) -> Path:
    """Return the single frozen Tier-2 ``.raw`` snapshot for ``currency``.

    Fails the test if zero or more than one snapshot exists — the Tier-2
    freeze must be exactly one deterministic snapshot per currency
    (F5 / CORRECTIONS-E10-5 dedup).
    """
    hits = sorted(_FX_SNAPSHOT_DIR.glob(f"fx_{currency}.*.raw"))
    assert len(hits) == 1, (
        f"{currency}: expected exactly one frozen Tier-2 snapshot, "
        f"found {len(hits)}: {[p.name for p in hits]}"
    )
    return hits[0]


# ── Real-snapshot parser round-trip (per feedback_real_data_over_mocks) ──


@pytest.mark.parametrize("currency", PANEL_CURRENCIES)
def test_real_snapshot_present_for_every_panel_currency(currency: str) -> None:
    """Each of the 5 v0.5 panel currencies has exactly one frozen Tier-2
    snapshot with a provenance sidecar carrying the ``source`` key."""
    snap = _frozen_snapshot(currency)
    sidecar = snap.with_suffix(".provenance.json")
    assert sidecar.exists(), f"{currency}: provenance sidecar missing"
    meta = json.loads(sidecar.read_text())
    assert meta["currency"] == currency
    assert meta["source"], f"{currency}: provenance 'source' key missing"
    assert meta["payload_sha256"], f"{currency}: payload sha256 missing"


@pytest.mark.parametrize("currency", PANEL_CURRENCIES)
def test_parser_round_trips_real_frozen_snapshot(currency: str) -> None:
    """``_parse_currency_payload`` parses each currency's real frozen
    Tier-2 payload into ``CurrencyDailyFXRow`` records inside the pinned
    panel window — only the real frozen central-bank payload is read."""
    body = _frozen_snapshot(currency).read_bytes()
    rows = _parse_currency_payload(currency, body, _PANEL_SINCE, _PANEL_UNTIL)

    assert rows, f"{currency}: parser produced no rows from real snapshot"
    assert all(isinstance(r, CurrencyDailyFXRow) for r in rows)
    assert all(r.currency == currency for r in rows)
    # Every parsed row is a positive local-per-USD rate inside the window.
    assert all(r.fx_rate > 0.0 for r in rows)
    assert all(
        _PANEL_SINCE <= r.observation_date.isoformat() <= _PANEL_UNTIL
        for r in rows
    )
    # Rows are returned sorted ascending by observation date.
    dates = [r.observation_date for r in rows]
    assert dates == sorted(dates)


def test_cop_snapshot_is_the_deduped_windowed_pull() -> None:
    """The single COP snapshot is the deterministic windowed pull
    (F5 dedup) — the divergent bare-URL pull was removed; the canonical
    snapshot covers exactly the panel window."""
    rows = _parse_currency_payload(
        "COP", _frozen_snapshot("COP").read_bytes(), _PANEL_SINCE, _PANEL_UNTIL
    )
    assert rows[0].observation_date.isoformat() == _PANEL_SINCE
    assert rows[-1].observation_date.isoformat() == _PANEL_UNTIL


def test_ngn_post_regime_break_flag_set_from_real_snapshot() -> None:
    """NGN rows parsed from the real snapshot inside the panel window all
    carry ``post_regime_break=True`` — the candidate window is entirely
    inside the post-June-2023 float regime (spec v0.5 §3.3)."""
    rows = _parse_currency_payload(
        "NGN", _frozen_snapshot("NGN").read_bytes(), _PANEL_SINCE, _PANEL_UNTIL
    )
    assert all(r.post_regime_break for r in rows)


# ── HALT-DV branch — dropped currencies are rejected honestly ────────────


@pytest.mark.parametrize("currency", HALT_DV_CURRENCIES)
def test_dropped_currency_is_not_a_panel_member(currency: str) -> None:
    """ZAR / KES / GHS are NOT v0.5 panel currencies (CORRECTIONS-E10-5)
    and have no frozen snapshot — the honest E10.0 drop, no flat-fill."""
    assert currency not in PANEL_CURRENCIES
    assert not list(_FX_SNAPSHOT_DIR.glob(f"fx_{currency}.*.raw"))


@pytest.mark.parametrize("currency", HALT_DV_CURRENCIES)
def test_fetch_currency_rejects_dropped_currency(
    currency: str, tmp_path: Path
) -> None:
    """``fetch_currency`` on a HALT-DV-dropped currency raises
    ``ValueError`` — it surfaces the drop honestly and issues no HTTP
    request, never substituting a placeholder series."""
    ingest = FXSeriesIngest(snapshot_dir=tmp_path)
    with pytest.raises(ValueError, match="not an E10 v0.5 panel currency"):
        ingest.fetch_currency(currency, _PANEL_SINCE, _PANEL_UNTIL)
    assert ingest.requests_issued == 0


def test_fxingestresult_shape() -> None:
    """``FXIngestResult`` is the frozen per-currency outcome container —
    a completed panel-currency fetch carries ``available=True`` and the
    daily rows; the HALT-DV fields exist for the gate's use."""
    result = FXIngestResult(
        currency="COP",
        available=True,
        rows=(),
        snapshot_path=None,
        halt_reason=None,
    )
    assert result.currency == "COP"
    assert result.available is True
    with pytest.raises(AttributeError):
        result.currency = "BRL"  # type: ignore[misc]  # frozen


# ── M-1: empty-payload DataVisibilityRevokedError branch ─────────────────


@pytest.mark.parametrize(
    ("currency", "empty_body"),
    [
        ("NGN", b"[]"),
        ("COP", b"[]"),
        ("BRL", b'{"value": []}'),
        ("EUR", b"TIME_PERIOD,OBS_VALUE\n"),
        ("GBP", b"DATE,XUDLUSS\n"),
    ],
)
def test_empty_payload_raises_data_visibility_revoked(
    currency: str, empty_body: bytes
) -> None:
    """A syntactically-valid but row-empty payload trips the
    ``if not rows`` HALT-DV branch of ``_parse_currency_payload``.

    The real frozen snapshots are all non-empty, so this malformed-input
    edge case is exercised with synthetic empty bytes — not real-data
    mocking (``feedback_real_data_over_mocks.md`` does not bar it). The
    ingest raises rather than returning a flat-filled or placeholder
    series."""
    with pytest.raises(DataVisibilityRevokedError, match="no rows|no parser"):
        _parse_currency_payload(
            currency, empty_body, _PANEL_SINCE, _PANEL_UNTIL
        )


# ── I-1: re-pull URL templates reproduce the frozen-sidecar endpoint ─────


def _frozen_sidecar_endpoint(currency: str) -> str:
    """Return the ``endpoint`` URL recorded in ``currency``'s frozen
    Tier-2 provenance sidecar."""
    sidecar = _frozen_snapshot(currency).with_suffix(".provenance.json")
    return str(json.loads(sidecar.read_text())["endpoint"])


@pytest.mark.parametrize("currency", PANEL_CURRENCIES)
def test_url_builder_reproduces_frozen_sidecar_endpoint(
    currency: str,
) -> None:
    """``_FX_URL_BUILDER[currency](since, until)`` reconstructs exactly the
    parameterized endpoint recorded in the frozen Tier-2 sidecar (I-1).

    A live re-pull therefore hits the same windowed URL the shipped
    snapshot was produced from — ``since``/``until`` are no longer dead
    parameters. Comparison is percent-decoded on both sides so a Socrata
    ``$where`` clause written human-readably in the sidecar still matches
    the encoded URL the builder issues. NGN is the documented gap: its
    CBN endpoint has no window parameter, so the builder reproduces the
    bare base URL the sidecar also records."""
    built = _FX_URL_BUILDER[currency](_PANEL_SINCE, _PANEL_UNTIL)
    recorded = _frozen_sidecar_endpoint(currency)
    assert unquote(built) == unquote(recorded), (
        f"{currency}: re-pull URL diverges from frozen sidecar endpoint\n"
        f"  built:    {unquote(built)}\n"
        f"  recorded: {unquote(recorded)}"
    )


def test_ngn_url_builder_is_documented_gap() -> None:
    """The NGN builder ignores ``since``/``until`` by design — the CBN
    GetAllExchangeRates endpoint has no window parameter (documented gap,
    I-1). The same bare URL is produced regardless of the window."""
    a = _FX_URL_BUILDER["NGN"]("2023-11-01", "2026-04-30")
    b = _FX_URL_BUILDER["NGN"]("2020-01-01", "2021-01-01")
    assert a == b
    assert a == "https://www.cbn.gov.ng/api/GetAllExchangeRates"


def test_windowed_url_builders_consume_since_until() -> None:
    """The four windowed builders (COP/BRL/EUR/GBP) produce a *different*
    URL for a different window — confirming ``since``/``until`` are live
    parameters, not ignored (I-1, contrast with the NGN gap)."""
    for currency in ("COP", "BRL", "EUR", "GBP"):
        panel = _FX_URL_BUILDER[currency](_PANEL_SINCE, _PANEL_UNTIL)
        other = _FX_URL_BUILDER[currency]("2020-01-01", "2021-01-01")
        assert panel != other, f"{currency}: builder ignores the window"
