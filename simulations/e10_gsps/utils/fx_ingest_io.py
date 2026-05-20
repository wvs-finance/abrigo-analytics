"""FX-series ingest IO-boundary unit (plan task 1.1 — E10.0).

IO Boundary tier — a class with ``__init__``; mutable state (the HTTP
session, the request counter, the snapshot directory) lives ONLY here,
per the CLAUDE.md three-tier discipline.

What this unit does
-------------------
Per-currency daily central-bank FX pull for the 5 E10 panel currencies
(spec v0.5 §1.2 source ledger), with a Tier-2 frozen-snapshot writer.
Each currency has a *verified* free public endpoint; the per-currency
fetch method records the raw payload as a frozen Tier-2 snapshot
(``data/raw/e10_gsps/fx/``) with a provenance sidecar (endpoint URL, UTC
fetch timestamp, payload sha256, requested window).

Non-bypassable data-fetch gate (plan task 1.1)
----------------------------------------------
If a central-bank series is unavailable / paywalled / auth-gated / not
machine-readable for the pinned ~30-month window, the fetch raises
``DataVisibilityRevokedError`` — it does NOT substitute, flat-fill, or
proceed on a placeholder. "The data is not there" is a real outcome that
routes to the HALT chain (spec v0.5 §1 HALT-DV; plan §3). The fantasy-
firewall (plan Phase 0.12) independently enforces that no FX value is
ever sourced from a synthetic generator or placeholder constant.

E10.0 per-currency availability verdict (verified 2026-05-20)
-------------------------------------------------------------
Panel — 5 currencies, all REACHABLE (spec v0.5 §3.3):

- COP — Banrep TRM via datos.gov.co Socrata (dataset 32sa-8pi3) — FREE,
  daily, full window. REACHABLE.
- BRL — BCB Olinda OData PTAX CotacaoDolarPeriodo — FREE, daily, full
  window. REACHABLE.
- EUR — ECB Data Portal SDW (EXR/D.USD.EUR.SP00.A, csvdata) — FREE,
  daily, full window. REACHABLE.
- GBP — BoE IADB (series XUDLUSS, CSV) — FREE, daily, full window.
  REACHABLE.
- NGN — CBN Gateway JSON API (/api/GetAllExchangeRates) — FREE, daily,
  629 USD rows in the ~30-month window. REACHABLE.

Historically-dropped set — HALT-DV at E10.0 (CORRECTIONS-E10-5):

The v0.4 8-currency panel was narrowed to the 5 above. ZAR, KES, GHS
lacked a free machine-readable daily ~30-month central-bank series and
were dropped — not substituted (``HALT_DV_CURRENCIES`` below). They are
NOT panel currencies under spec v0.5; ``fetch_currency`` rejects them
with a ``ValueError``. The per-currency unavailability evidence (kept as
the historical HALT-DV record):

- ZAR — SARB: the legacy daily-timeseries server wwwrs.resbank.co.za
  (ExchangeRateDetail.aspx) is UNREACHABLE ("no route to host"); the new
  SarbWebApi serves current snapshots only — NO free machine-readable
  daily history.
- KES — CBK: the tabular forex series (forex-exchange-rates wpDataTable
  id=32 / historical_data.csv) ends 2024-01-04; current daily indicative
  rates are published ONLY as ~2,164 per-day PDF files — NO free
  machine-readable daily series for the panel window.
- GHS — BoG: the entire bog.gov.gh site (incl. economic-data and
  daily-interbank-fx-rates) is behind a Radware bot-management wall
  (validate.perfdrive.com) — NOT free-to-probe.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from simulations.e10_gsps._errors import DataVisibilityRevokedError
from simulations.e10_gsps.types import PANEL_CURRENCIES, CurrencyDailyFXRow

_USER_AGENT: Final[str] = "abrigo-analytics-e10-gsps-e10.0/0.1"
_HTTP_TIMEOUT_S: Final[float] = 60.0

# ── Per-currency verified free public FX endpoints (spec v0.5 §1.2) ──────
#
# The 5 panel currencies, each with a verified free, machine-readable
# daily series for the ~30-month window. ZAR / KES / GHS were dropped at
# E10.0 (CORRECTIONS-E10-5) — they are not panel currencies and carry no
# endpoint; ``fetch_currency`` rejects them via the PANEL_CURRENCIES
# membership check. See the module docstring + HALT_DV_CURRENCIES.
#
# I-1 reproducibility fix (Stage-2 quality review). Four of the five
# endpoints are central-bank APIs that accept an explicit ``[since,
# until]`` window as query parameters; their entry below is a *builder*
# that consumes ``since``/``until`` and reconstructs exactly the
# parameterized URL recorded in the frozen Tier-2 provenance sidecar — so
# a live re-pull is reproducible and matches the shipped snapshot window.
# The COP Socrata default ``$limit`` (1000 rows, no window filter) is
# explicitly overridden by the ``$where``/``$order``/``$limit`` template;
# the divergent bare-resource pull the COP ``dedup_note`` discarded can no
# longer be produced by this code path.
#
# DOCUMENTED GAP — NGN. The CBN Gateway endpoint
# ``/api/GetAllExchangeRates`` has NO window parameter: it returns the
# full multi-currency rate dump unconditionally (the ~8 MB snapshot), and
# ``_parse_currency_payload`` does the ``[since, until]`` windowing in
# code. The NGN builder therefore ignores ``since``/``until`` by design;
# a re-pull is reproducible only up to whatever rows CBN currently
# serves. ``test_registry_url_matches_sidecar_endpoint`` guards that the
# NGN registry URL still equals the sidecar's recorded base.

_COP_RESOURCE: Final[str] = "https://www.datos.gov.co/resource/32sa-8pi3.json"
_BRL_BASE: Final[str] = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarPeriodo(dataInicial=@dataInicial,"
    "dataFinalCotacao=@dataFinalCotacao)"
)
_EUR_BASE: Final[str] = (
    "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A"
)
_GBP_BASE: Final[str] = (
    "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp"
)
_NGN_BASE: Final[str] = "https://www.cbn.gov.ng/api/GetAllExchangeRates"

# Month-number → BoE three-letter month abbreviation (``DD/Mon/YYYY``).
_BOE_MONTHS: Final[tuple[str, ...]] = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


def _build_cop_url(since: str, until: str) -> str:
    """Socrata SoQL URL — ``$where``-windowed, ``$order``-ed, ``$limit``ed.

    Overrides the Socrata 1000-row default ``$limit`` (the divergent bare
    pull the COP ``dedup_note`` discarded) with the explicit panel window.
    """
    where = (
        f"vigenciadesde >= '{since}T00:00:00.000' "
        f"AND vigenciadesde <= '{until}T23:59:59.999'"
    )
    return (
        f"{_COP_RESOURCE}?$limit=50000"
        f"&$where={quote(where)}"
        f"&$order={quote('vigenciadesde ASC')}"
    )


def _build_brl_url(since: str, until: str) -> str:
    """BCB Olinda OData URL — PTAX accepts ``MM-DD-YYYY`` date literals."""

    def _mdy(iso: str) -> str:
        d = date.fromisoformat(iso)
        return f"{d.month:02d}-{d.day:02d}-{d.year:04d}"

    return (
        f"{_BRL_BASE}?@dataInicial='{_mdy(since)}'"
        f"&@dataFinalCotacao='{_mdy(until)}'"
        f"&$format=json&$top=5000"
    )


def _build_eur_url(since: str, until: str) -> str:
    """ECB Data Portal SDW URL — ``startPeriod``/``endPeriod`` ISO dates."""
    return f"{_EUR_BASE}?format=csvdata&startPeriod={since}&endPeriod={until}"


def _build_gbp_url(since: str, until: str) -> str:
    """BoE IADB URL — ``Datefrom``/``Dateto`` in ``DD/Mon/YYYY`` form."""

    def _dmy(iso: str) -> str:
        d = date.fromisoformat(iso)
        return f"{d.day:02d}/{_BOE_MONTHS[d.month - 1]}/{d.year:04d}"

    return (
        f"{_GBP_BASE}?csv.x=yes"
        f"&Datefrom={_dmy(since)}&Dateto={_dmy(until)}"
        f"&SeriesCodes=XUDLUSS&UsingCodes=Y&CSVF=TN&VPD=Y"
    )


def _build_ngn_url(since: str, until: str) -> str:
    """CBN Gateway URL — DOCUMENTED GAP: no window parameter exists.

    The endpoint returns the full multi-currency dump unconditionally;
    ``since``/``until`` are accepted for a uniform builder signature but
    ignored. Windowing happens in ``_parse_currency_payload``.
    """
    del since, until  # CBN GetAllExchangeRates has no window parameter.
    return _NGN_BASE


# Per-currency URL builders — each reconstructs the parameterized endpoint
# recorded in the frozen Tier-2 provenance sidecar from ``since``/``until``.
_FX_URL_BUILDER: dict[str, Callable[[str, str], str]] = {
    "COP": _build_cop_url,
    "BRL": _build_brl_url,
    "EUR": _build_eur_url,
    "GBP": _build_gbp_url,
    "NGN": _build_ngn_url,
}

# Currencies whose free machine-readable daily series was confirmed
# unavailable at E10.0 — the non-bypassable gate fired. The v0.4
# 8-currency panel was narrowed to the 5-currency v0.5 panel by dropping
# these three (CORRECTIONS-E10-5); they are NOT panel members — kept here
# only as the historically-dropped HALT-DV record.
HALT_DV_CURRENCIES: Final[tuple[str, ...]] = ("ZAR", "KES", "GHS")

# Per-currency central-bank source label (spec v0.5 §1.2 — 5 currencies).
_FX_SOURCE: dict[str, str] = {
    "COP": "Banrep",
    "BRL": "BCB",
    "EUR": "ECB",
    "GBP": "BoE",
    "NGN": "CBN",
}


@dataclass(frozen=True, slots=True)
class FXIngestResult:
    """One currency's ingest outcome (one of the 5 v0.5 panel currencies).

    ``rows`` is the daily FX series. ``available`` is True for a
    completed fetch of a panel currency. ``snapshot_path`` points at the
    materialized Tier-2 frozen snapshot. ``halt_reason`` carries
    non-bypassable-gate evidence when ``available`` is False — retained
    for the HALT chain, though under spec v0.5 every panel currency has a
    verified-free endpoint and a mid-fetch regression raises instead.
    """

    currency: str
    available: bool
    rows: tuple[CurrencyDailyFXRow, ...]
    snapshot_path: Path | None
    halt_reason: str | None


class FXSeriesIngest:
    """Per-currency daily central-bank FX-series ingest with a Tier-2
    frozen-snapshot writer (plan task 1.1).

    Mutable state — the snapshot directory and the request counter — is
    confined to this IO-boundary class. The callable/value tiers never
    hold IO state.
    """

    def __init__(self, snapshot_dir: Path) -> None:
        """Initialise the ingest unit.

        Args:
            snapshot_dir: Directory for Tier-2 frozen FX snapshots. Created
                if absent.
        """
        self._snapshot_dir: Path = Path(snapshot_dir)
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.requests_issued: int = 0

    def _http_get(self, url: str) -> bytes:
        """Issue a GET and return the raw body.

        Raises:
            DataVisibilityRevokedError: the endpoint is unreachable,
                returns a non-2xx status, or times out — the
                non-bypassable data-fetch gate (plan task 1.1). The unit
                never substitutes a placeholder series.
        """
        req = Request(
            url,
            headers={"Accept": "*/*", "User-Agent": _USER_AGENT},
        )
        try:
            with urlopen(req, timeout=_HTTP_TIMEOUT_S) as resp:
                body: bytes = resp.read()
        except (HTTPError, URLError, OSError) as exc:
            raise DataVisibilityRevokedError(
                f"FX endpoint unreachable: {url} ({exc!r}). Non-bypassable "
                f"data-fetch gate — HALT-DV; no placeholder substitution."
            ) from exc
        self.requests_issued += 1
        return body

    def _write_snapshot(
        self,
        currency: str,
        endpoint: str,
        body: bytes,
        since: str,
        until: str,
    ) -> Path:
        """Write a Tier-2 frozen snapshot + provenance sidecar.

        Returns:
            The path of the materialized snapshot file.
        """
        # M-2: millisecond resolution + an exists-guard so two sub-second
        # re-pulls for the same currency cannot silently overwrite each
        # other's snapshot + sidecar.
        now = datetime.now(tz=timezone.utc)
        ts = now.strftime("%Y-%m-%dT%H-%M-%S-") + f"{now.microsecond // 1000:03d}Z"
        snap = self._snapshot_dir / f"fx_{currency}.{ts}.raw"
        if snap.exists():
            raise DataVisibilityRevokedError(
                f"snapshot {snap.name} already exists — a sub-millisecond "
                f"re-pull would overwrite a frozen Tier-2 artifact; HALT-DV."
            )
        snap.write_bytes(body)
        sidecar = snap.with_suffix(".provenance.json")
        sidecar.write_text(
            json.dumps(
                {
                    "currency": currency,
                    "source": _FX_SOURCE[currency],
                    "endpoint": endpoint,
                    "since": since,
                    "until": until,
                    "fetched_at_utc": ts,
                    "payload_sha256": hashlib.sha256(body).hexdigest(),
                    "payload_bytes": len(body),
                    "tier": "Tier 2 — frozen raw central-bank pull",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return snap

    def fetch_currency(
        self, currency: str, since: str, until: str
    ) -> FXIngestResult:
        """Fetch one currency's daily FX series in ``[since, until]``.

        Args:
            currency: One of the 5 v0.5 panel currency codes
                (COP, BRL, EUR, GBP, NGN).
            since: ISO-8601 ``YYYY-MM-DD`` window start (inclusive).
            until: ISO-8601 ``YYYY-MM-DD`` window end (inclusive).

        Returns:
            An ``FXIngestResult`` carrying the parsed daily series and the
            materialized Tier-2 snapshot path.

        Raises:
            DataVisibilityRevokedError: the currency's verified-free
                endpoint regresses mid-fetch (unreachable / paywalled /
                non-2xx) — HALT-DV. The unit never flat-fills.
            ValueError: ``currency`` is not a v0.5 panel currency. The 3
                E10.0 HALT-DV-dropped currencies (ZAR / KES / GHS;
                CORRECTIONS-E10-5) are rejected here — they are not panel
                members and have no endpoint.
        """
        if currency not in PANEL_CURRENCIES:
            raise ValueError(
                f"{currency!r} is not an E10 v0.5 panel currency "
                f"(panel: {', '.join(PANEL_CURRENCIES)}). The v0.4 panel "
                f"was narrowed to 5 at E10.0 — ZAR/KES/GHS dropped "
                f"HALT-DV (CORRECTIONS-E10-5); they have no endpoint."
            )

        # I-1: the endpoint is reconstructed per-currency from
        # ``since``/``until`` so a live re-pull reproduces exactly the
        # parameterized URL recorded in the frozen Tier-2 sidecar (NGN is
        # the documented-gap exception — see _build_ngn_url).
        endpoint = _FX_URL_BUILDER[currency](since, until)
        # Verified-free endpoint — a fetch failure here is a mid-execution
        # regression and DOES raise (HALT-DV).
        body = self._http_get(endpoint)
        snap = self._write_snapshot(currency, endpoint, body, since, until)
        rows = _parse_currency_payload(currency, body, since, until)
        return FXIngestResult(
            currency=currency,
            available=True,
            rows=rows,
            snapshot_path=snap,
            halt_reason=None,
        )


def _parse_currency_payload(
    currency: str, body: bytes, since: str, until: str
) -> tuple[CurrencyDailyFXRow, ...]:
    """Parse a raw central-bank payload into ``CurrencyDailyFXRow`` rows.

    Each of the 5 v0.5 panel currencies has a distinct payload format.
    ``post_regime_break`` is set per spec v0.5 §3.3 (NGN: True iff date
    >= 2023-06-01; the free-floating currencies COP/BRL/EUR/GBP: True
    throughout — they have no within-window break).

    Raises:
        DataVisibilityRevokedError: the payload is empty or unparseable
            — treated as a fetch regression (HALT-DV), never silently
            dropped.
    """
    since_d, until_d = date.fromisoformat(since), date.fromisoformat(until)
    ngn_float_start = date(2023, 6, 1)

    def _in_window(d: date) -> bool:
        return since_d <= d <= until_d

    rows: list[CurrencyDailyFXRow] = []
    try:
        if currency == "NGN":
            payload = json.loads(body)
            for r in payload:
                if "DOLLAR" not in str(r.get("currency", "")).upper():
                    continue
                d = date.fromisoformat(str(r["ratedate"])[:10])
                if not _in_window(d):
                    continue
                rows.append(
                    CurrencyDailyFXRow(
                        currency="NGN",
                        observation_date=d,
                        fx_rate=float(r["centralrate"]),
                        source="CBN",
                        post_regime_break=d >= ngn_float_start,
                    )
                )
        elif currency == "COP":
            payload = json.loads(body)
            for r in payload:
                d = datetime.fromisoformat(
                    str(r["vigenciadesde"]).replace(".000", "")
                ).date()
                if not _in_window(d):
                    continue
                rows.append(
                    CurrencyDailyFXRow(
                        currency="COP",
                        observation_date=d,
                        fx_rate=float(r["valor"]),
                        source="Banrep",
                        post_regime_break=True,
                    )
                )
        elif currency == "BRL":
            payload = json.loads(body)
            for r in payload.get("value", []):
                # M-3: parse the full ISO timestamp and take its date,
                # rather than slicing a fixed 19-char prefix — survives a
                # date-only or fractional-second BCB variant.
                d = datetime.fromisoformat(
                    str(r["dataHoraCotacao"])
                ).date()
                if not _in_window(d):
                    continue
                rows.append(
                    CurrencyDailyFXRow(
                        currency="BRL",
                        observation_date=d,
                        fx_rate=float(r["cotacaoVenda"]),
                        source="BCB",
                        post_regime_break=True,
                    )
                )
        elif currency in ("EUR", "GBP"):
            text = body.decode("utf-8", errors="strict")
            rows.extend(_parse_csv_fx(currency, text, since_d, until_d))
        else:  # pragma: no cover — non-panel currency never reaches here
            raise DataVisibilityRevokedError(
                f"{currency} has no parser — not a v0.5 panel currency"
            )
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
        raise DataVisibilityRevokedError(
            f"{currency} payload unparseable ({exc!r}); HALT-DV — the "
            f"ingest never silently drops a malformed series."
        ) from exc

    if not rows:
        raise DataVisibilityRevokedError(
            f"{currency} payload contained no rows in [{since}, {until}]; "
            f"HALT-DV — no flat-fill, no placeholder."
        )
    return tuple(sorted(rows, key=lambda r: r.observation_date))


def _parse_csv_fx(
    currency: str, text: str, since_d: date, until_d: date
) -> list[CurrencyDailyFXRow]:
    """Parse the ECB (EUR) / BoE (GBP) CSV daily-rate payloads.

    ECB ``csvdata`` rows are a fixed-schema CSV whose header names
    ``TIME_PERIOD`` and ``OBS_VALUE``; the title column is quoted and
    contains embedded commas, so the parse is keyed off the header index,
    not a naive split. The BoE IADB CSV is a 2-column ``DATE,rate`` file
    with ``DD Mon YYYY`` dates. Both quote USD-per-unit-of-currency, which
    is inverted here to the local-currency-per-USD convention (spec §3.2).
    """
    out: list[CurrencyDailyFXRow] = []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return out
    header = [h.strip().strip('"') for h in lines[0].split(",")]

    if currency == "EUR":
        # Header-keyed parse — TIME_PERIOD / OBS_VALUE are columns 6 / 7.
        try:
            i_date = header.index("TIME_PERIOD")
            i_rate = header.index("OBS_VALUE")
        except ValueError:
            return out
        for ln in lines[1:]:
            cells = ln.split(",")
            if len(cells) <= max(i_date, i_rate):
                continue
            try:
                d = date.fromisoformat(cells[i_date].strip())
                rate = float(cells[i_rate].strip())
            except ValueError:
                continue
            if rate <= 0.0 or not (since_d <= d <= until_d):
                continue
            out.append(
                CurrencyDailyFXRow(
                    currency="EUR",
                    observation_date=d,
                    fx_rate=1.0 / rate,
                    source="ECB",
                    post_regime_break=True,
                )
            )
        return out

    # BoE GBP — 2-column "DD Mon YYYY",rate.
    for ln in lines[1:]:
        parts = [p.strip().strip('"') for p in ln.split(",")]
        if len(parts) < 2:
            continue
        try:
            d = datetime.strptime(parts[0], "%d %b %Y").date()
            rate = float(parts[1])
        except ValueError:
            continue
        if rate <= 0.0 or not (since_d <= d <= until_d):
            continue
        out.append(
            CurrencyDailyFXRow(
                currency="GBP",
                observation_date=d,
                fx_rate=1.0 / rate,
                source="BoE",
                post_regime_break=True,
            )
        )
    return out


__all__ = [
    "FXIngestResult",
    "FXSeriesIngest",
    "HALT_DV_CURRENCIES",
]
