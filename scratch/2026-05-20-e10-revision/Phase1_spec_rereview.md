# E10 Phase 1 (E10.0) — Spec-Compliance RE-REVIEW (Stage 1 of 2, closure check)

**Reviewer:** spec-compliance reviewer (TestingRealityChecker)
**Date:** 2026-05-20
**Scope:** closure verification of the 5 GAPs from `Phase1_spec_review.md`,
re-checked against accepted spec v0.6 (5-currency panel, unchanged from v0.5)
+ plan Phase 1 tasks 1.1–1.4.
**Mode:** read-only; pytest run permitted; no code edits.

## Verdict: SPEC-COMPLIANT — proceed to Stage 2 (code-quality)

All 5 GAPs CLOSED. Tasks 1.1–1.4 all MET under the 5-currency v0.6 spec.
No EXTRA / over-building found.

## Per-GAP closure status

| GAP | Status | Evidence |
|---|---|---|
| F1 | **CLOSED** | `types/fx.py` `PANEL_CURRENCIES` is the 5-tuple `(COP, BRL, EUR, GBP, NGN)` — confirmed by direct import. ZAR/KES/GHS are not panel members anywhere in live code; they sit in the documented `HALT_DV_CURRENCIES` constant (`fx_ingest_io.py`) and as commented historical entries in `_REGIME_BREAK_START`. `fetch_currency` rejects them with `ValueError` via the membership check. |
| F2 | **CLOSED** | Every remaining "v0.4" reference is explanatory/historical ("the v0.4 8-currency panel was narrowed to 5") — none is a stale contract citation. All live-contract citations now read "spec v0.5 §3.3" (5 currencies). Docstrings, error messages, and registry comments updated throughout `fx_ingest_io.py` + `regime_break.py`. `_FX_ENDPOINT`/`_FX_SOURCE`/`_REGIME_BREAK_START` all carry the 5 panel currencies as live members. |
| F3 | **CLOSED** | `tests/unit/test_fx_ingest_io.py` exists — 19 tests, all pass. Genuine, not vacuous: `_parse_currency_payload` is round-tripped against the **real frozen Tier-2 `.raw` snapshots** under `data/raw/e10_gsps/fx/` (no mocks; `_frozen_snapshot` resolves the on-disk file). Real assertions: positive `fx_rate`, in-window dates, ascending sort, COP first/last obs pinned to the window bounds, NGN `post_regime_break=True` on all rows. The HALT-DV branch (`test_dropped_currency_is_not_a_panel_member`, `test_fetch_currency_rejects_dropped_currency`) confirms ZAR/KES/GHS have no snapshot on disk and `fetch_currency` raises `ValueError` issuing zero HTTP requests — no flat-fill, no fabricated series. The empty-payload `DataVisibilityRevokedError` branch in the parser is exercised indirectly (real snapshots are non-empty). |
| F4 | **CLOSED** | `notebooks/e10_gsps/diagnostics/E10.0_panel_window.json` exists — 5 currencies, window `2023-11-01 → 2026-04-30`, `n_cells = 150` (5 × 30), per-currency breakdown with snapshot filenames. Also encoded as the `PANEL_WINDOW` constant in `types/fx.py`. `e10_phase1_completion.md` is corrected: a CORRECTIONS-E10-5 note supersedes the stale 8-currency NON-RETIREMENT/"BANNED" framing; task 1.4 declared DONE. The disposition memo `notebooks/e10_gsps/dispositions/E10.0_HALT-DV.md` is preserved and annotated `RESOLVED (CORRECTIONS-E10-5)` at the head, with the original NON-RETIREMENT verdict retained as the historical record. |
| F5 | **CLOSED** | Exactly one COP snapshot on disk (`fx_COP.2026-05-20T15-20-48Z.raw`) — the duplicate bare-URL pull was removed; the surviving snapshot is the `$limit`-bounded windowed pull (provenance endpoint confirms). All 5 provenance sidecars (COP, BRL, EUR, GBP, NGN) carry the `source` key (Banrep / BCB / ECB / BoE / CBN). `test_real_snapshot_present_for_every_panel_currency` asserts exactly-one-snapshot and the `source` key, locking the dedup. |

## Per-task table (5-currency v0.6 spec)

| Task | Verdict | Summary |
|---|---|---|
| 1.1 — FX ingest IO unit | **MET** | `FXSeriesIngest` / `FXIngestResult` / parser built; 5 series fetched + frozen with consistent provenance; 3 dropped honestly; unit hard-coded to the 5-currency v0.6 panel; 19 real-snapshot tests pass. |
| 1.2 — regime-break screen | **MET** | `regime_break.py` correct; registry + docstrings keyed to 5 v0.6 currencies; GHS/KES retained only as commented historical record; 4 task-0.4 RED harness tests green. |
| 1.3 — x402 re-verification | **MET** | $0.01 USDC flat `exact` scheme re-verified; HTTP-402 snapshot frozen with full decode (unchanged since first review — was MET). |
| 1.4 — panel window / cell-count | **MET** | `E10.0_panel_window.json` (150 cells) + `PANEL_WINDOW` constant delivered; completion memo corrected; HALT-DV disposition memo preserved + annotated RESOLVED. |

**MET count: 4 of 4.**

## Independent verification performed

1. **Test suite** — `pytest simulations/e10_gsps/tests/`: **80 passed / 40
   failed** (matches the expected count). All 40 failures are genuine
   Phase-2–6 RED harnesses: `test_nhpp_engine` / `test_decomposition` /
   `test_surface_grid` / `test_verdict_classifier` raise
   `NotImplementedError(_PHASE2..6)` by design; the 10 `test_notebook_*`
   failures assert the Phase-5 notebooks are "not yet created (RED Phase 0)".
   No Phase-2+ module was prematurely made green — **no over-building**.
2. **`test_fx_ingest_io.py`** — 19 tests, all pass. Genuine: real frozen
   Tier-2 snapshots read off disk, real assertions, HALT-DV branch confirms
   no flat-fill / no fabricated series and zero HTTP requests on a dropped
   currency. Not vacuous.
3. **`PANEL_CURRENCIES`** — direct import confirms `('COP','BRL','EUR','GBP','NGN')`.
4. **Panel-window artifact** — `E10.0_panel_window.json` carries
   `n_cells = 150`, `n_currencies = 5`, `months_per_currency = 30`, window
   `2023-11-01 → 2026-04-30`; per-currency breakdown sums to 150.
5. **Tier-2 snapshots** — single COP snapshot (dedup confirmed); all 5
   provenance sidecars carry `source`; ZAR/KES/GHS have no snapshot
   (honest drop).

## Notes (non-blocking, for Stage 2 awareness)

- The parser's empty-payload `DataVisibilityRevokedError` branch is not
  directly unit-tested (real snapshots are non-empty by construction). Not
  a spec-compliance gap; a code-quality reviewer may consider a synthetic
  empty-bytes input for that branch.
- `_REGIME_BREAK_START` still maps GHS/KES to dates. This is explicitly
  documented as the historical pinned record and they are unreachable in
  the live 5-currency panel — acceptable, not a stale contract.

No EXTRA (out-of-scope) work found. The implementation now honors the
5-currency v0.6 spec as its frozen contract.
