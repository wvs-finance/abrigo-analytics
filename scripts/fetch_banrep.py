"""Tier 2 fetcher: pull Banco de la República TRM (COP/USD) panels.

The TRM series is the X variable used by Pair D, dev-AI Stage-1, and the
``dev_ai_cost_v2`` factor model (spec
``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` §3.4 +
§0.1 CORRECTIONS-E). Two emit paths are supported:

1. **Monthly path** (legacy, preserved): the canonical end-of-month spot panel
   used by Pair D + the prior dev-AI iteration lives at
   ``scratch/simple-beta-pair-d/data/scripts/`` and is re-derived in
   ``notebooks/dev_ai_cost/scripts/build_cop_usd_panel.py`` from a DuckDB cache
   pre-populated by the closed FX-vol-CPI Phase-A.0 pipeline. ``main()`` here
   prints the pointer so cloners can reproduce it; this path is unchanged.

2. **Daily path** (new): ``fetch_daily_trm`` hits the Datos Abiertos Socrata
   open-data endpoint directly (no auth, no rate limit) and writes a tidy
   parquet panel ``(date: Date, trm_cop_per_usd: Decimal)`` plus a sidecar
   JSON capturing endpoint URL, fetch timestamp, response sha256, and the
   requested ``[since, until]`` window. Exact-Decimal arithmetic per spec
   §3.5 (notional-cost reconciliation requires Decimal for the downstream
   daily COP cost join).

The daily endpoint is the same dataset used by the prior dev-AI iteration's
DuckDB cache (see ``notebooks/dev_ai_cost/scripts/build_cop_usd_panel.py``
docstring) and by ``docs/plans/2026-04-16-structural-econ-data-pipeline.md``
Task 11.M.5 — dataset id ``32sa-8pi3`` on ``datos.gov.co``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Final

import polars as pl
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Daily TRM Socrata endpoint ──────────────────────────────────────────────
#
# Dataset id ``32sa-8pi3`` (Tasa de Cambio Representativa del Mercado) on
# ``datos.gov.co``. Anonymous Socrata access; default page size is 1000 rows,
# which is why ``$limit`` is set to a value larger than the full series length
# (~8,250 daily observations from 1991-12 to present). See plan
# ``docs/plans/2026-04-16-structural-econ-data-pipeline.md`` L518.
_TRM_DAILY_ENDPOINT: Final[str] = "https://www.datos.gov.co/resource/32sa-8pi3.json"
_TRM_DAILY_DEFAULT_LIMIT: Final[int] = 50_000
_TRM_DAILY_HTTP_TIMEOUT_S: Final[float] = 60.0


def _http_get_trm_json(url: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """Issue the Socrata GET and return the decoded JSON payload.

    Indirection point for ``monkeypatch`` in the test suite. The ``try`` is
    intentionally narrow: it covers only the HTTP call + JSON decode (where
    failures are external-state failures — network, Socrata downtime, schema
    surprise at the transport layer). All downstream parsing is handled by
    callers in their own narrowly-scoped ``try`` blocks.
    """
    try:
        resp = requests.get(url, params=params, timeout=_TRM_DAILY_HTTP_TIMEOUT_S)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        # ValueError covers ``resp.json()`` decode failure (Socrata returning
        # HTML on outage). Re-raise as a single typed exception so the caller
        # contract is "RuntimeError on transport failure".
        raise RuntimeError(
            f"Banrep TRM Socrata fetch failed for {url} (params={params}): {exc}"
        ) from exc


def _normalize_row(raw: dict[str, Any]) -> tuple[date, Decimal]:
    """Parse one Socrata row into ``(date, Decimal)``.

    Invariants:

    * ``raw`` must contain both ``valor`` (string-encoded numeric) and
      ``vigenciadesde`` (ISO-8601 date with optional ``T00:00:00.000`` suffix).
    * ``valor`` must parse to a finite positive ``Decimal``.
    * ``vigenciadesde`` must parse to a ``datetime.date`` after stripping
      Socrata's ``.000`` millisecond suffix.

    Raises:
        ValueError: any of the invariants above are violated. The caller is
            expected to either propagate (strict fetcher mode) or count and
            log (lenient mode); ``fetch_daily_trm`` propagates.
    """
    valor_str = raw.get("valor")
    fecha_str = raw.get("vigenciadesde")
    if not isinstance(valor_str, str) or not valor_str:
        raise ValueError(f"row missing or empty 'valor': {raw!r}")
    if not isinstance(fecha_str, str) or not fecha_str:
        raise ValueError(f"row missing or empty 'vigenciadesde': {raw!r}")

    # Parse the date (narrow try — only the parse can fail here).
    try:
        parsed_date = datetime.fromisoformat(fecha_str.replace(".000", "")).date()
    except ValueError as exc:
        raise ValueError(f"row 'vigenciadesde' not ISO-8601: {fecha_str!r}") from exc

    # Parse the value (narrow try — only Decimal construction can fail).
    try:
        parsed_value = Decimal(valor_str)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"row 'valor' not numeric: {valor_str!r}") from exc

    if not parsed_value.is_finite() or parsed_value <= 0:
        raise ValueError(f"row 'valor' must be finite and positive: {parsed_value}")

    return parsed_date, parsed_value


def _validate_window(since: str, until: str) -> tuple[date, date]:
    """Parse and validate the ``[since, until]`` window.

    Raises:
        ValueError: ``since`` or ``until`` is not ISO-8601 ``YYYY-MM-DD``, or
            ``since > until``.
    """
    try:
        since_d = date.fromisoformat(since)
        until_d = date.fromisoformat(until)
    except ValueError as exc:
        raise ValueError(
            f"since/until must be ISO-8601 YYYY-MM-DD; got since={since!r}, until={until!r}"
        ) from exc
    if since_d > until_d:
        raise ValueError(f"since ({since}) must be <= until ({until})")
    return since_d, until_d


def fetch_daily_trm(out_path: Path, since: str, until: str) -> None:
    """Fetch daily Banrep TRM in ``[since, until]`` and emit a parquet panel.

    Output:
        ``out_path`` — parquet with schema ``(date: Date, trm_cop_per_usd:
        Decimal)``, sorted ascending by ``date``, deduplicated on ``date``.

        ``out_path.with_suffix(out_path.suffix + ".provenance.json")`` —
        sidecar capturing endpoint URL, ISO-8601 UTC fetch timestamp, sha256
        of the raw JSON payload, and the requested window.

    Args:
        out_path: Destination path for the parquet panel. Parent directory
            is created if absent.
        since: ISO-8601 ``YYYY-MM-DD`` start date (inclusive).
        until: ISO-8601 ``YYYY-MM-DD`` end date (inclusive).

    Invariants enforced on input:
        ``since`` and ``until`` are ISO-8601 ``YYYY-MM-DD``; ``since <= until``.

    Raises:
        ValueError: ``since``/``until`` violate the input invariant; OR the
            Socrata payload contains a malformed row (propagated from
            ``_normalize_row``).
        RuntimeError: the HTTP call or JSON decode failed (network outage,
            Socrata 5xx, schema surprise at transport layer).

    Errors silenced:
        None. The Socrata Pydantic-ish schema drift (e.g., new fields on the
        response) is tolerated at the dict level — extra keys are ignored —
        but missing required fields raise ``ValueError`` from
        ``_normalize_row``. Schema drift on the *required* fields is therefore
        loud, not silent.

    Notes on external state:
        The Socrata endpoint is rate-limit-free for anonymous access but is
        subject to upstream downtime (datos.gov.co). The narrow ``try`` in
        ``_http_get_trm_json`` re-raises any transport / decode failure as a
        ``RuntimeError``; callers in CI may want to wrap this in a retry
        decorator.
    """
    since_d, until_d = _validate_window(since, until)

    # Socrata filter: ``$where vigenciadesde between '...' and '...'``.
    # Inclusive window endpoints match the contract above. Sort ascending so
    # the downstream parquet is naturally ordered.
    params = {
        "$limit": _TRM_DAILY_DEFAULT_LIMIT,
        "$where": (
            f"vigenciadesde >= '{since_d.isoformat()}T00:00:00.000' "
            f"AND vigenciadesde <= '{until_d.isoformat()}T23:59:59.999'"
        ),
        "$order": "vigenciadesde ASC",
    }

    raw_payload = _http_get_trm_json(_TRM_DAILY_ENDPOINT, params)
    if not isinstance(raw_payload, list):
        raise RuntimeError(
            f"Banrep TRM Socrata returned non-list payload: {type(raw_payload).__name__}"
        )

    # Normalize rows. Each ``_normalize_row`` call has its own narrow ``try``
    # blocks internally; we do not wrap the whole loop in a single broad
    # ``try`` (per try-except skill: narrow each ``try`` to the single
    # operation that can fail).
    rows: list[tuple[date, Decimal]] = [_normalize_row(r) for r in raw_payload]

    # Deduplicate on date — Socrata occasionally emits adjacent
    # ``vigenciadesde``/``vigenciahasta`` ranges that overlap by one day at
    # holiday boundaries. Keep the first occurrence (sorted ascending so
    # earliest publication wins).
    seen: dict[date, Decimal] = {}
    for d, v in rows:
        if d not in seen:
            seen[d] = v

    dates_sorted = sorted(seen)
    values_sorted = [seen[d] for d in dates_sorted]

    df = pl.DataFrame(
        {
            "date": dates_sorted,
            "trm_cop_per_usd": values_sorted,
        },
        schema={
            "date": pl.Date,
            "trm_cop_per_usd": pl.Decimal(precision=18, scale=6),
        },
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out_path)

    # Provenance sidecar. sha256 is computed over the canonical-JSON
    # representation of the raw payload so reruns against an identical
    # Socrata snapshot are byte-stable.
    canonical = json.dumps(raw_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sidecar = out_path.with_suffix(out_path.suffix + ".provenance.json")
    sidecar.write_text(
        json.dumps(
            {
                "endpoint": _TRM_DAILY_ENDPOINT,
                "params": params,
                "since": since,
                "until": until,
                "fetched_at_utc": datetime.now(tz=timezone.utc)
                .replace(microsecond=0)
                .isoformat()
                .replace("+00:00", "Z"),
                "payload_sha256": hashlib.sha256(canonical).hexdigest(),
                "row_count_raw": len(raw_payload),
                "row_count_emitted": df.height,
                "parquet_sha256": hashlib.sha256(out_path.read_bytes()).hexdigest(),
            },
            indent=2,
            sort_keys=True,
        )
    )


def main() -> int:
    print("[Tier 2 / Banrep] COP/USD TRM panel fetcher")
    print()
    print("The canonical Banrep TRM ingest logic is preserved in the Pair D")
    print("scratch artifact. Reuse it from this repo's venv:")
    print()
    print(f"  {REPO_ROOT}/scratch/simple-beta-pair-d/data/scripts/")
    print()
    print("If you only need the processed panel, prefer `make data` (Tier 1) — it")
    print("pulls cop_usd_panel.parquet from HuggingFace in one round trip.")
    print()
    print("Daily TRM panel (new, dev_ai_cost_v2 prerequisite) — invoke from Python:")
    print("  from scripts.fetch_banrep import fetch_daily_trm")
    print("  fetch_daily_trm(Path('data/raw/banrep_trm_daily.parquet'),")
    print("                  since='2024-01-01', until='2026-03-31')")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
