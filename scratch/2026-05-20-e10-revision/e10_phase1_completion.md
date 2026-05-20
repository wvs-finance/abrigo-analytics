# E10 GSPS — Phase 1 (E10.0) Completion Memo

**Date:** 2026-05-20 (corrected for the v0.5 5-currency re-spec)
**Phase:** 1 — E10.0 panel-currency verification + regime-break screen + x402 re-verify
**Plan:** `docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md` §1 Phase 1 (tasks 1.1–1.5)
**Spec:** `docs/specs/2026-05-20-e10-gsps-v0.5-convex-multicurrency-design.md` §1.2, §3.3, §7 field 6, §9
**Status:** **COMPLETE — Phase 1 done for the v0.5 5-currency panel.**

> **Correction note (CORRECTIONS-E10-5).** This memo originally framed
> Phase 1 under the superseded 8-currency v0.4 spec — it declared Phase 1
> BLOCKED, task 1.4 a NON-RETIREMENT verdict, and a 5-currency panel
> "BANNED." That framing **predates and is superseded by** the user's
> 2026-05-20 re-spec decision. Under CORRECTIONS-E10-5 the user enumerated
> pivot 2 — re-spec the panel to the 5 reachable currencies (COP, BRL,
> EUR, GBP, NGN) with a fresh §7 field-6 pre-pin — and that re-spec is now
> the accepted spec (v0.5 §3.3). The 5-currency panel is NOT a silent
> re-spec: it is a user-authorised, CORRECTIONS-block-recorded panel-
> dimension re-spec. Task 1.4 produces the 5-currency panel-window
> deliverable; Phase 1 is COMPLETE. This memo is corrected accordingly
> below; the original v0.4 NON-RETIREMENT framing is retained only in the
> HALT-DV disposition memo as the historical record.

---

## Executive summary

Phase 1 (E10.0) executed tasks 1.1–1.4. The non-bypassable FX-data-fetch gate
(task 1.1) re-verified per-currency free daily availability — the per-currency
re-verification the spec §0 DV record explicitly deferred to E10.0. Of the
v0.4 8-currency candidate set, **5 currencies confirm a free, machine-readable
daily ~30-month series** (COP, BRL, EUR, GBP, NGN); **3 do not** (ZAR, KES,
GHS). Per the user's 2026-05-20 non-bypassable-data-gate directive, the 3
missing currencies were NOT flat-filled, substituted, or placeholder-
proceeded — a HALT-DV fired at E10.0. The user-enumerated pivot (2026-05-20)
re-spec'd the panel to the 5 reachable currencies (CORRECTIONS-E10-5; spec
v0.5 §3.3). **Under v0.5, Phase 1 is COMPLETE for the 5-currency panel.**

The x402 price re-verification (task 1.3) PASSED — $0.01 USDC flat, re-verified
exactly. The regime-break screen module (task 1.2) is implemented and its four
task-0.4 RED tests pass.

## Per-currency FX-data availability verdict (task 1.1)

| # | Currency | Source | Verdict | Window confirmed | Rows | Evidence |
|---|---|---|---|---|---|---|
| 1 | COP | Banrep TRM — datos.gov.co Socrata `32sa-8pi3` | **AVAILABLE** | 2023-11-01 → 2026-04-30 | 590 daily | free JSON, no auth |
| 2 | BRL | BCB Olinda OData PTAX `CotacaoDolarPeriodo` | **AVAILABLE** | 2023-11-01 → 2026-04-30 | 627 daily | free OData JSON, no auth |
| 3 | EUR | ECB Data Portal SDW `EXR/D.USD.EUR.SP00.A` | **AVAILABLE** | 2023-11-01 → 2026-04-30 | 635 daily | free csvdata, no auth |
| 4 | GBP | BoE IADB series `XUDLUSS` | **AVAILABLE** | 2023-11-01 → 2026-04-30 | 631 daily | free CSV, no auth |
| 5 | NGN | CBN Gateway API `/api/GetAllExchangeRates` | **AVAILABLE** | 2023-11-01 → 2026-04-30 | 617 daily | free JSON, no auth; 5,984 USD rows total 2001→2026; 731 USD rows post-2023-06 float |
| 6 | ZAR | SARB | **UNAVAILABLE — HALT-DV** | — | — | New `SarbWebApi` = current snapshot only; legacy daily-timeseries server `wwwrs.resbank.co.za` unreachable ("no route to host", 3 retries). No free machine-readable daily ZAR/USD history. |
| 7 | KES | CBK | **UNAVAILABLE — HALT-DV** | — | — | Structured forex series (`historical_data.csv` / wpDataTable id=32 / per-year CSVs) ends 2024-01-04. Current daily indicative rates published ONLY as ~2,164 per-day PDF files. No free machine-readable daily series for the panel window. |
| 8 | GHS | BoG | **UNAVAILABLE — HALT-DV** | — | — | Entire `bog.gov.gh` site behind a Radware bot-management wall (`validate.perfdrive.com`); every economic-data / FX-rate route redirects to a JS bot challenge. Not free-to-probe. |

**Verified-available: 5 / 8. HALT-DV currencies: ZAR, KES, GHS.**

Free options were exhausted before each UNAVAILABLE verdict: SARB new API +
legacy server both probed (3 retries each); CBK datatable AJAX driven with a
session cookie + `wdtNonce` + referer to confirm the 2024-01 cutoff is a real
data cutoff and not a fetch artifact; BoG probed with a browser User-Agent to
confirm the Radware wall is unconditional. No paid source was considered
(`feedback_dune_last_resort_exhaust_free_resources.md`).

## Regime-break screen results (task 1.2)

Implemented `simulations/e10_gsps/modules/regime_break.py` (Callable tier).
The four task-0.4 RED-harness tests now PASS (full suite: 32/32 green).

Spec-pinned per-currency qualifying-window starts (spec §3.3, declared before
data was touched):

| Currency | Qualifying-window start | Regime break |
|---|---|---|
| NGN | **2023-06-01** | Yes — NFEM / willing-buyer-willing-seller float (CORRECTIONS-E10-4 Fix 3) |
| GHS | 2023-01-01 | Yes — post heavily-managed administrative-peg span |
| KES | 2023-03-01 | Yes — post heavily-managed administrative-peg span |
| COP / BRL / ZAR / EUR / GBP | None (no within-window break) | No — free-floating throughout the panel window |

NGN-screen check: the 617 NGN daily rows in the candidate panel window are all
dated 2023-11-01 → 2026-04-30, entirely inside the post-June-2023 float regime
— no peg-regime contamination. (Confinement only bites pre-2023-06 data, which
is outside the candidate window anyway.) GHS / KES screens are pinned but moot
— both currencies are HALT-DV on availability and never reach the screen.

## x402 re-verification result (task 1.3)

**PASSED — re-verifies exactly at $0.01 USDC flat.**

Live probe 2026-05-20 of the The Graph Gateway x402 interface
(`gateway.thegraph.com/api/x402/subgraphs/id/...`) returned **HTTP 402** with a
`payment-required` header decoding to:

| Field | Value |
|---|---|
| x402Version | 2 |
| scheme | `exact` |
| network | `eip155:8453` (Base mainnet) |
| asset | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (USDC on Base) |
| amount (raw) | `10000` |
| price | 10000 / 10⁶ (USDC 6 decimals) = **$0.01 USDC per query, flat** |

Frozen snapshot: `data/raw/e10_gsps/x402/x402_payment_required.json`. The spec
§1.2 / §0 DV-record figure ($0.01 USDC, `exact` scheme) re-verifies exactly —
no drift. The x402 leg is the one DV component that PASSES re-verification.

## Panel-window intersection + cell-count (task 1.4)

**Delivered — 5-currency panel window (CORRECTIONS-E10-5; spec v0.5 §3.3 /
§7 field 6).** Under the accepted v0.5 spec the panel is the 5 reachable
currencies (COP, BRL, EUR, GBP, NGN). The post-regime-break intersection
window the 5 share is **2023-11-01 → 2026-04-30, 30 calendar months**.
Derived at E10.0 from the real frozen Tier-2 snapshots, each currency
contributes exactly 30 (currency, month) cells:

| Currency | Daily rows | Monthly cells | Window |
|---|---|---|---|
| COP | 590 | 30 | 2023-11-01 → 2026-04-30 |
| BRL | 627 | 30 | 2023-11-01 → 2026-04-30 |
| EUR | 635 | 30 | 2023-11-01 → 2026-04-30 |
| GBP | 631 | 30 | 2023-11-01 → 2026-04-30 |
| NGN | 617 | 30 | 2023-11-01 → 2026-04-30 |

**Panel total: 5 currencies × 30 months = 150 (currency, month) cells.**
NGN is confined to its post-June-2023 float regime (CORRECTIONS-E10-4
Fix 3) — every NGN row in the window falls inside the post-float regime, so
confinement does not shorten the panel. COP/BRL/EUR/GBP free-float
throughout the window.

The ~150-cell panel clears N_MIN = 75 at the *cell* dimension; the binding
identification dimension is **G ≈ 5 currency clusters** — structurally
thinner than the v0.4 G ≈ 8, and the spec v0.5 §8 records this plainly. The
descriptive posture is unchanged: E10 was never inferential, so a thinner G
does not demote it further. This is not a silent re-spec — it is the
user-authorised CORRECTIONS-E10-5 panel-dimension re-spec; ZAR/KES/GHS are
dropped, not substituted, and the panel is not extended to recover cells.

**Task-1.4 deliverable:** the panel-window diagnostics record is emitted at
`notebooks/e10_gsps/diagnostics/E10.0_panel_window.json`; the panel-window
constant is `PANEL_WINDOW` (`simulations/e10_gsps/types/fx.py`).

## Currency drops + why

- **ZAR (SARB)** — dropped. SARB publishes no free machine-readable daily
  ZAR/USD timeseries: the modern `SarbWebApi` returns current snapshots only;
  the legacy `wwwrs.resbank.co.za` timeseries server is unreachable.
- **KES (CBK)** — dropped. CBK's machine-readable forex series ends 2024-01-04;
  current daily rates are PDF-only (~2,164 per-day files).
- **GHS (BoG)** — dropped. The entire BoG site is behind a Radware bot wall.

3 of 8 currencies dropped → DV-gate failure → HALT-DV.

## HALT status

- **HALT-DV — FIRED then RESOLVED.** The E10.0 per-currency re-verification
  found 3 of the v0.4 8 candidate currencies (ZAR, KES, GHS) lack a free
  machine-readable daily series; the HALT-DV fired honestly. It was
  **resolved** via the HALT chain: disposition memo → user-enumerated pivot
  (2026-05-20, pivot 2) → CORRECTIONS-E10-5 → spec v0.5 5-currency re-spec.
  The disposition memo (`notebooks/e10_gsps/dispositions/E10.0_HALT-DV.md`)
  is annotated RESOLVED and preserved as the historical record.
- **No NON-RETIREMENT under v0.5.** The v0.4-era NON-RETIREMENT routing
  pertained to the superseded 8-currency design. Under the accepted v0.5
  spec the 5-currency panel IS the design; there is no DV-gate failure for
  the 5 panel currencies — all five re-verified clean.

## Task-by-task status

| Task | Status |
|---|---|
| 1.1 — FX-series ingest IO-boundary unit + Tier-2 snapshots | DONE. Unit built (`utils/fx_ingest_io.py`); 5 reachable currencies fetched + frozen; 3 unavailable currencies recorded as honest HALT-DV (non-bypassable gate fired). |
| 1.2 — Regime-break screen module | DONE. `modules/regime_break.py` built; 4 task-0.4 RED tests pass; full suite 32/32 green. |
| 1.3 — x402 re-verification | DONE. PASSED — $0.01 USDC flat re-verified; snapshot frozen. |
| 1.4 — Panel-window intersection + cell-count | DONE. 5-currency panel window fixed: 2023-11-01 → 2026-04-30, 5 × 30 = 150 (currency, month) cells. Deliverable: `notebooks/e10_gsps/diagnostics/E10.0_panel_window.json` + `PANEL_WINDOW` constant in `types/fx.py`. |
| 1.5 — Early review checkpoint | NOT performed by the implementer. Task 1.5 is the orchestrator's two-stage Reality-Checker review, dispatched after the implementer returns. Flagged for the orchestrator. |

## Phase 1 exit gate

Under the accepted spec v0.5 §3.3 (CORRECTIONS-E10-5), the Phase-1 exit
criterion is read against the **5-currency panel**: all 5 panel currencies
(COP, BRL, EUR, GBP, NGN) confirm a free post-regime-break qualifying
~30-month daily series, the panel window is fixed as their intersection
(2023-11-01 → 2026-04-30, 150 cells), and x402 re-verifies at $0.01 flat.
**Phase 1 exit = MET for the v0.5 5-currency panel — Phase 1 COMPLETE.**
Phase 2 (R6 simulator build) is unblocked, pending the task-1.5 post-HALT
2-way re-review of spec v0.5.

## Artifacts produced

- `simulations/e10_gsps/utils/fx_ingest_io.py` — FX-series ingest IO unit (new)
- `simulations/e10_gsps/modules/regime_break.py` — regime-break screen (RED stub → implemented)
- `data/raw/e10_gsps/fx/fx_{COP,BRL,EUR,GBP,NGN}.*.raw` (+ `.provenance.json`) — Tier-2 frozen FX snapshots
- `data/raw/e10_gsps/x402/x402_payment_required.json` — Tier-2 frozen x402 price-probe snapshot
- `notebooks/e10_gsps/dispositions/E10.0_HALT-DV.md` — disposition memo (annotated RESOLVED via CORRECTIONS-E10-5)
- `notebooks/e10_gsps/diagnostics/E10.0_panel_window.json` — task-1.4 panel-window diagnostics record (5 currencies, 150 cells)
- This completion memo

All work left as uncommitted changes / untracked files per the
commit-only-when-asked constraint.
