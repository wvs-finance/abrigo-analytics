# E10 Phase 1 (E10.0) — Code-Quality Review (Stage 2)

Reviewer: code-quality reviewer. Scope: correctness, maintainability, security
of the Phase-1 implementation. Spec-compliance (stage 1) already PASSED.

## Verdict: APPROVED_WITH_NITS

- Critical: 0
- Important: 1 (addressed below — provenance/registry divergence; non-blocking
  because it is a documentation/reproducibility gap, not a defect of the
  shipped code path)
- Minor: 5

The Phase-1 code is well-structured, fully typed, three-tier-clean, and the
firewall checker passes (40 files clean). All 23 Phase-1 tests
(`test_fx_ingest_io.py` 19 + `test_panel_regime_break.py` 4) pass. The single
Important finding is a reproducibility/documentation divergence between the
endpoint registry and the frozen snapshots; it does not corrupt any shipped
result and is acknowledged as non-blocking, hence APPROVED rather than
CHANGES-REQUESTED. (Out-of-scope: `test_nhpp_engine.py`, `test_surface_grid.py`,
`test_verdict_classifier.py` failures belong to later phases.)

## Verified strengths

- **Three-tier discipline holds.** `types/fx.py` imports only `dataclasses` /
  `datetime`. `modules/regime_break.py` imports only `_errors` + `types` — no
  `utils`. `fx_ingest_io.py` is correctly the sole holder of mutable state
  (`requests_issued`, snapshot dir, HTTP session). Clean.
- **functional-python conformance.** `CurrencyDailyFXRow`,
  `MonthlyRealizedVarianceCell`, `FXIngestResult`, `PanelWindowDiagnostics`,
  `ManagedFloatScreenResult` are all `frozen=True, slots=True`.
  `RegimeBreakScreenModule` is a frozen-dc + `__call__` stateless callable. No
  inheritance beyond `Exception` subclasses in `_errors.py`. Full typing.
- **HALT-DV branch is correct.** `fetch_currency` rejects ZAR/KES/GHS via the
  `PANEL_CURRENCIES` membership check *before* any HTTP request;
  `test_fetch_currency_rejects_dropped_currency` asserts
  `requests_issued == 0`. No flat-fill, no placeholder path. Correct.
- **Empty-payload branch is correct.** `_parse_currency_payload` raises
  `DataVisibilityRevokedError` on `if not rows` and on any
  `JSONDecodeError/KeyError/ValueError/TypeError`. The branch logic is sound.
- **Security is clean.** No hardcoded secrets, no `eval`/`pickle`/`exec`.
  Parsers use `json.loads` and manual CSV splitting only. All 5 endpoints are
  the expected central-bank domains. The empty-payload `errors="strict"` decode
  on CSV is the safe choice.
- **CSV parser robustness.** `_parse_csv_fx` keys the ECB parse off
  `header.index("TIME_PERIOD"/"OBS_VALUE")` rather than a fixed column, which
  correctly survives the quoted title column with embedded commas.

## Findings

### Important

**I-1 — `_FX_ENDPOINT` registry does not match the frozen-snapshot endpoints
(`fx_ingest_io.py:87-100` vs provenance sidecars).**
Every provenance sidecar records a *parameterized* endpoint (COP:
`?$limit=...&$where=...&$order=...`; BRL: `?@dataInicial=...&$format=json&$top=5000`;
EUR: `?format=csvdata&startPeriod=...&endPeriod=...`; GBP:
`?csv.x=yes&Datefrom=...&SeriesCodes=XUDLUSS&...`). The `_FX_ENDPOINT` registry
holds only the *bare* base URLs. Consequences:

- `fetch_currency` ignores its `since`/`until` arguments entirely — they are
  written to the provenance sidecar but never appended to the URL. A live
  `fetch_currency("EUR", since, until)` would GET the bare ECB URL with no
  `startPeriod`/`endPeriod`, returning the full series (or, for COP's Socrata
  default `$limit`, a *different* 1000-row default window — exactly the
  divergent pull the COP `dedup_note` says was discarded).
- The frozen Tier-2 snapshots were therefore produced by an out-of-band script,
  not by the shipped `FXSeriesIngest.fetch_currency`. The tests round-trip the
  *parser* against real snapshots (good), but no test exercises the actual URL
  the code would issue, so the divergence is invisible to CI.

Minimal fix (prose): make `_FX_ENDPOINT` values URL templates (or
per-currency builder functions) that consume `since`/`until`, so
`fetch_currency` reconstructs exactly the parameterized endpoint recorded in
the provenance sidecar. Then the snapshot is reproducible from the shipped code
and `since`/`until` stop being dead parameters. Alternatively, if Phase-1
deliberately treats the snapshots as the frozen artifact and `fetch_currency`
is only the future re-pull path, add a docstring note stating the bare URLs are
placeholders and add a test asserting the registry URL matches the sidecar
`endpoint` base — so the gap is documented and CI-guarded rather than silent.

This is filed Important (not Critical) because the shipped Phase-1 *results*
(the parsed panel) come from real, correctly-windowed snapshots and are sound;
the defect is in reproducibility/maintainability of the re-pull path.

### Minor

**M-1 — empty-payload `DataVisibilityRevokedError` branch has no direct test
(`_parse_currency_payload:352-356`).**
Stage-1 noted this; it remains true. The `if not rows` branch is only reached
transitively. Recommend a synthetic test feeding `b"[]"` (NGN/COP/BRL) and
`b"TIME_PERIOD,OBS_VALUE\n"` (EUR) directly to `_parse_currency_payload` and
asserting `DataVisibilityRevokedError`. This is not real-data mocking — it is a
malformed-input edge case the real snapshots cannot exercise, so
`feedback_real_data_over_mocks.md` does not bar it.

**M-2 — `_write_snapshot` filename collision on sub-second re-pull
(`fx_ingest_io.py:195-197`).** The timestamp is second-resolution
(`%Y-%m-%dT%H-%M-%SZ`). Two `fetch_currency` calls for the same currency
within one second silently overwrite the first snapshot and its sidecar. The
writer is deterministic but not idempotency-safe across rapid re-pulls.
Low-likelihood in practice; consider millisecond resolution or an
exists-check.

**M-3 — BRL date parse assumes a fixed 19-char prefix
(`fx_ingest_io.py:325-326`).** `str(r["dataHoraCotacao"])[:19]` works for
`YYYY-MM-DDTHH:MM:SS` but would silently mis-slice a date-only or
fractional-second variant. The NGN parser already uses the safer `[:10]` +
`date.fromisoformat`. Minor; the real BCB payload is consistent today.

**M-4 — `RegimeBreakScreenModule.__call__` adds an `allow_mixed_regime`
keyword absent from the `RegimeBreakScreen` Protocol
(`regime_break.py:213-218` vs `protocols.py`).** Because it is keyword-only
with a default, the class still satisfies the Protocol structurally, so this is
benign — but the Protocol and implementation signatures have drifted.
Recommend either adding the keyword to the Protocol or noting the intentional
extension in the Protocol docstring.

**M-5 — `_REGIME_BREAK_START` retains GHS/KES dead entries
(`regime_break.py:75-76`).** Documented as "historical record," and
`screen_managed_float` will happily return a result for them. They are not in
`PANEL_CURRENCIES`, so they cannot reach the live panel via the ingest, but a
direct `screen_managed_float(currency="GHS")` call succeeds silently. Acceptable
given the explicit docstring, but a one-line guard or a separate
`_HISTORICAL_REGIME_BREAK` dict would prevent accidental reuse.

## Test-quality assessment

The 19 `test_fx_ingest_io.py` tests are genuine, not vacuous: they parse real
frozen snapshots, assert `fx_rate > 0`, window membership, ascending sort, the
NGN `post_regime_break` flag, COP dedup boundaries, provenance-sidecar keys, and
the HALT-DV `ValueError` + `requests_issued == 0`. Coverage of the 5 parsers
and the HALT-DV branch is good. Gaps: the empty-payload branch (M-1) and the
parameterized-URL path (I-1) are untested. `regime_break` has 4 passing tests in
`test_panel_regime_break.py`.

## Bottom line

APPROVED_WITH_NITS. No Critical findings; the single Important finding (I-1) is
a reproducibility/documentation gap with a clear, low-risk fix and is explicitly
non-blocking because shipped Phase-1 results are sound. Recommend addressing
I-1 and M-1 before Phase 2 builds the panel on top of the ingest.
