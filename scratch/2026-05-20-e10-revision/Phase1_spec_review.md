# E10 Phase 1 (E10.0) — Spec-Compliance Review (Stage 1 of 2)

**Reviewer:** spec-compliance reviewer (TestingRealityChecker)
**Date:** 2026-05-20
**Scope:** Phase 1 tasks 1.1–1.4 vs plan v0.2 + spec v0.5 (5-currency re-spec)
**Mode:** read-only; pytest run permitted; no code edits.

## Verdict: NOT-COMPLIANT — implementer fixes required

Per-task: 1.1 GAP, 1.2 GAP, 1.3 MET, 1.4 GAP. **MET count: 1 of 4.**
SPEC-COMPLIANT requires all four MET with no GAP/EXTRA. Three GAPs block.

The Phase 1 *functional behavior* (5 series fetched, 3 dropped honestly,
regime screen, x402 re-verify) is substantially delivered and the
regime-break tests pass. But the code still encodes the **stale 8-currency
v0.4 spec** as its frozen contract, in direct violation of the v0.5
5-currency re-spec the review explicitly requires the code to honor. This
is a real spec-compliance failure, not a cosmetic one — `PANEL_CURRENCIES`
is the panel-dimension constant and it is wrong.

## Per-task table

| Task | Verdict | Summary |
|---|---|---|
| 1.1 — FX ingest IO unit | **GAP** | 5 series fetched + frozen; 3 dropped honestly. But unit is hard-coded to the 8-currency v0.4 panel; no test exercises it against the real snapshot. |
| 1.2 — regime-break screen | **GAP** | Module correct, 0.4 RED tests green. But registry/docstrings keyed to 8 currencies incl. ZAR/KES/GHS — stale v0.4 contract. |
| 1.3 — x402 re-verification | **MET** | $0.01 USDC flat `exact` scheme re-verified; HTTP 402 snapshot frozen with full decode. |
| 1.4 — panel window / cell-count | **GAP** | No panel-window-intersection deliverable produced; the only memo on record (completion memo) declares 1.4 a NON-RETIREMENT verdict, not a fixed 5-currency window. |

## Findings

### F1 (GAP, 1.1/1.2) — code encodes the stale 8-currency v0.4 panel, not the v0.5 5-currency re-spec
`simulations/e10_gsps/types/fx.py` defines `PANEL_CURRENCIES` as an
**8-tuple** (COP, BRL, KES, NGN, GHS, ZAR, EUR, GBP) with the comment
"The eight panel currencies per spec v0.4 §3.3 — fixed (the panel is NOT
expanded)." Spec v0.5 §3.3 / CORRECTIONS-E10-5 re-specifies the panel to
**5 currencies (COP, BRL, EUR, GBP, NGN)**; ZAR/KES/GHS are *removed*, not
merely flagged unavailable. The review brief states the code must "honor
the v0.5 5-currency re-spec (not the stale 8-currency v0.4)."
Consequences:
- `fx_ingest_io.py` `_FX_ENDPOINT`, `_FX_SOURCE` carry all 8; `fetch_currency`
  validates against the 8-member `PANEL_CURRENCIES`. ZAR/KES/GHS are still
  first-class panel members handled via `None`-sentinel + `halt_reason`.
- `regime_break.py` `_REGIME_BREAK_START` carries all 8 incl. GHS/KES
  managed-float dates; `screen_managed_float` accepts ZAR/KES/GHS as valid
  panel currencies and returns a result for them.
The plan's CORR-E10P-10 says the *delivered Phase-1 work is VALID under the
re-spec* — but VALID-as-fetch-behavior is not the same as
spec-compliant-as-code. The dropped currencies belong in a documented
HALT-DV record, not baked into the live panel-dimension constant. Under
v0.5, `PANEL_CURRENCIES` must be the 5-tuple and ZAR/KES/GHS must be a
separate `HALT_DV_CURRENCIES`-style constant (the latter already exists in
`fx_ingest_io.py` but the panel constant was never narrowed).

### F2 (GAP, 1.1/1.2) — pervasive stale "spec v0.4" / "8 panel currencies" references
Both reviewed modules cite the superseded spec throughout:
- `fx_ingest_io.py` docstring: "the 8 E10 panel currencies (spec v0.4 §1.2)";
  `fetch_currency` docstring: "One of the 8 panel currency codes"; "spec
  v0.4 §3.3"; "spec v0.4 §1 HALT-DV".
- `regime_break.py` docstring: "spec v0.4 §3.3 / §10 E10.0"; `_REGIME_BREAK_START`
  comment "spec v0.4 §3.3"; `screen_managed_float`/`confine_to_float_regime`
  docstrings: "One of the 8 panel currency codes"; coverage error message
  hard-codes "spec v0.4 §8".
The accepted spec is **v0.5**. Carrying v0.4 citations in main-line code
after a closure re-spec is a spec-traceability defect — a reader cannot
tell the code targets the accepted contract.

### F3 (GAP, 1.1) — no test exercises `fx_ingest_io.py` against the real frozen snapshot
The brief for 1.1 requires "Tests run against a real frozen snapshot, not a
mock (per `feedback_real_data_over_mocks.md`)." `grep` finds **zero** test
files referencing `FXSeriesIngest`, `fx_ingest_io`, `FXIngestResult`, or
`data/raw/e10_gsps`. The ingest unit — `_parse_currency_payload`,
`_parse_csv_fx`, the COP/BRL/EUR/GBP/NGN format branches, the inversion to
local-per-USD, the window filter, the `available=False` HALT-DV branch — is
**entirely untested**. The frozen Tier-2 snapshots exist on disk; a parser
test should round-trip them. Task-0.4's harness covers only `regime_break`.
This is a missing Phase-1 deliverable, not a Phase-2 item.

### F4 (GAP, 1.4) — no 5-currency panel-window deliverable; only a NON-RETIREMENT memo on record
Plan task 1.4 deliverable is "Panel-window diagnostics + cell-count" fixing
the window as "the post-regime-break intersection across the 5 currencies …
~150 cells." The only artifact found is `e10_phase1_completion.md`, which
under the **8-currency** frame declares 1.4 "Cannot be fixed … HALT-DV →
NON-RETIREMENT" and calls a 5-currency panel a "silent re-specification —
BANNED." That memo predates and contradicts the v0.5 re-spec; it is stale.
No code constant, diagnostics artifact, or memo records the fixed
`2023-11-01→2026-04-30` window and the ~150-cell (5×~30) count under v0.5.
The completion memo cannot be relied on as the 1.4 deliverable — its
verdict is the opposite of the accepted re-spec.

### F5 (GAP, 1.1 — minor) — duplicate / inconsistent COP snapshot; one provenance missing `source`
`data/raw/e10_gsps/fx/` contains **two** COP raw snapshots
(`15-19-55Z`, `119894 B` and `15-20-48Z`, `70741 B`) from different
endpoints (bare resource URL vs a `$where`-filtered query). The Tier-2
freeze should be a single deterministic snapshot per currency; two
divergent COP pulls make the frozen panel ambiguous for the Phase-3 Tier-3
round-trip. Separately, the BRL and EUR/GBP provenance sidecars omit the
`source` key the COP/NGN sidecars carry — `_write_snapshot` always writes
`source`, so the BRL/EUR/GBP sidecars on disk were produced by an earlier
code path; provenance is inconsistent across the 5 frozen series.

## Independent verification performed

1. **Test suite** — `pytest simulations/e10_gsps/tests/`: 61 passed, 40
   failed. All 40 failures are Phase 2–6 RED harnesses (NHPP engine,
   decomposition, surface-grid, verdict-classifier, the 5 notebooks) — they
   raise `NotImplementedError(_PHASE2..6)` by design. **No Phase-2+ harness
   was prematurely made green — no over-building.** The 4 task-0.4
   regime-break tests (`test_panel_regime_break.py`) **pass** (4/4 green),
   confirming the 1.2 RED harness is satisfied.
2. **Tier-2 snapshots** — 5 FX series present (COP×2, BRL, EUR, GBP, NGN)
   with provenance sidecars; x402 probe present with full HTTP-402
   `payment-required` decode. **The 3 HALT-DV currencies (ZAR/KES/GHS) are
   NOT fabricated** — no placeholder snapshot exists for them. Honest drop
   confirmed.
3. **Scope check** — Phase 1 built ONLY the FX ingest unit and regime-break
   module. No simulator, no panel decomposition, no surface, no verdict
   logic was implemented (all Phase-2+ modules remain `NotImplementedError`
   stubs). **Scope is clean.**
4. **v0.5 re-spec honored?** — **NO.** See F1/F2. The code's panel-dimension
   constant and all spec citations target the superseded 8-currency v0.4.

## Required fixes before SPEC-COMPLIANT (Stage 2)

1. Narrow `types/fx.py` `PANEL_CURRENCIES` to the v0.5 5-tuple
   (COP, BRL, EUR, GBP, NGN); move ZAR/KES/GHS to a documented
   HALT-DV-dropped constant; update the comment to spec v0.5 §3.3.
2. Update all "spec v0.4" / "8 panel currencies" references in
   `fx_ingest_io.py` and `regime_break.py` to spec v0.5 / 5 currencies;
   prune ZAR/KES/GHS from `_FX_ENDPOINT`/`_FX_SOURCE`/`_REGIME_BREAK_START`
   or relocate them to an explicit dropped-currency record.
3. Add a Phase-1 test exercising `FXSeriesIngest` parsing against the real
   frozen Tier-2 snapshots (per `feedback_real_data_over_mocks.md`).
4. Produce the task-1.4 5-currency panel-window deliverable
   (`2023-11-01→2026-04-30`, ~150 cells) as a code constant or diagnostics
   artifact, and supersede the stale NON-RETIREMENT verdict in
   `e10_phase1_completion.md` with a v0.5-aligned completion record.
5. Resolve the duplicate COP snapshot to a single deterministic Tier-2
   freeze; regenerate the BRL/EUR/GBP provenance sidecars so all 5 carry
   the `source` key consistently.

No EXTRA (out-of-scope) work was found — the implementation under-honors
the re-spec rather than over-building.
