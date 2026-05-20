# E10 GSPS v0.4 — Data-Visibility Record (§0 freeze)

**Status:** PHASE-0 FROZEN
**Date frozen:** 2026-05-20
**DV verdict:** **DV-PASS-FREE** <!-- CHECK_ALLOWLIST: DV-PASS-FREE is the canonical data-visibility verdict token, not an inferential verdict -->
**Plan reference:** `docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md`
§0 (DV-PASS-FREE freeze) + Phase 0 task 0.0 <!-- CHECK_ALLOWLIST: DV-PASS-FREE canonical DV token -->
**Spec reference:** `docs/specs/2026-05-20-e10-gsps-v0.4-convex-multicurrency-design.md`
§1 (Data-visibility gate verdict)

This file freezes the §0 data-visibility gate clearance at Phase-0 entry,
BEFORE any external pull fires (plan §0: "§0 closure is mandatory before
Phase 0 task 0.1 fires"). Every empirical input is real and free — no
paid Dune, no paid anything. The $399 Dune Plus figure enters E10 ONLY
as the upper-bound cap of the cost model (`Q_high = 39,900 = $399 / $0.01`);
it is never a tool purchased (plan §0 / spec §1.2; `memory/feedback_dune_
last_resort_exhaust_free_resources.md`).

## Summary

| Field | Value |
|---|---|
| DV verdict | **DV-PASS-FREE** | <!-- CHECK_ALLOWLIST: DV-PASS-FREE canonical DV verdict token -->
| Source 1 — X (FX series) | Eight central banks' published daily FX series (free public) |
| Source 2 — cost multiplier | x402 per-query USDC price — The Graph Gateway `payment-required` decode ($0.01 USDC flat, `exact` scheme) |
| Source 3 — optional cross-check | The Graph free tier, 100k queries/month (on-chain cross-check only; not panel-input) |
| Simulated quantity | Q (monthly data-query volume) — the ONLY generated quantity |
| NOT purchased | Dune Plus ($399/month) — model cap only (`Q_high`), never a tool |
| Tier-2 snapshot discipline | Frozen snapshots committed for all 8 FX series + the x402 price probe; request manifest + materialized snapshot pinned at Phase 0.0 |

## 1. The eight central-bank FX-endpoint manifest (X — Source 1)

All eight currencies have verified free 30-month daily central-bank FX
history (spec §1.2; re-verified per-currency at E10.0 / Phase 1). The
panel month axis is central-bank FX history, NOT Mento token age
(RC BLOCK-1). NGN is confined to its post-June-2023 float regime
(spec §3.3) — the panel window is the intersection of post-structural-
break qualifying series.

| # | Currency | Pair | Central bank | Series | Market segment |
|---|---|---|---|---|---|
| 1 | COP | COP/USD | Banco de la República (Banrep) | TRM daily reference rate | EM — reused from Pair D + E5 |
| 2 | BRL | BRL/USD | Banco Central do Brasil (BCB) | PTAX / published daily series | EM |
| 3 | KES | KES/USD | Central Bank of Kenya (CBK) | published daily indicative rate | EM — managed-float screen at E10.0 |
| 4 | NGN | NGN/USD | Central Bank of Nigeria (CBN) | NFEM / willing-buyer-willing-seller daily | EM — confined post-June-2023 float |
| 5 | GHS | GHS/USD | Bank of Ghana (BoG) | published daily interbank rate | EM — managed-float screen at E10.0 |
| 6 | ZAR | ZAR/USD | South African Reserve Bank (SARB) | published daily rate | EM |
| 7 | EUR | EUR/USD | European Central Bank (ECB) | euro foreign-exchange reference rate | DM — control |
| 8 | GBP | GBP/USD | Bank of England (BoE) | published daily spot rate | DM — control |

**Endpoint freeze note.** Per the plan, the concrete URL / API
endpoints, the materialized Tier-2 frozen snapshots, and the per-currency
qualifying-window start dates are produced and pinned at Phase 1
(task 1.1, the FX-series ingest IO-boundary unit, with the Tier-2
frozen-snapshot writer). This §0 record freezes the *manifest* — the
eight sources, all confirmed free and public — at Phase-0 entry. No
external pull fires before Phase 1.

**HALT-DV (mid-execution regression).** If at any phase any of the 8
central-bank FX series moves behind authentication or paywall → HALT;
disposition memo; re-classify DV to DV-PASS-QUOTED (user approval <!-- CHECK_ALLOWLIST: DV-PASS-QUOTED canonical DV re-classification token -->
required) or DV-BLOCK (park iteration). No silent migration to
alternative providers (plan §0 / §3 HALT-DV).

## 2. The x402 price-probe manifest + decoded `payment-required` snapshot (Source 2)

| Field | Value |
|---|---|
| Probe target | The Graph Gateway x402 endpoint |
| Probe method | HTTP request → decode the `payment-required` (HTTP 402) response header |
| Scheme | `exact` |
| Price | **$0.01 USDC per query, flat** |
| Verified live | 2026-05-20 (spec methodology anchor; spec §1.2) |
| Re-verification | Re-verified at E10.0 / Phase 1 task 1.3 (Reality Checker) |
| Governance | x402 — HTTP 402 revival; Linux Foundation governance |

**Decoded `payment-required` snapshot (verified 2026-05-20).** The
Graph Gateway x402 endpoint returns a fixed `exact`-scheme offer of
$0.01 USDC per query, flat. This is the verified cost multiplier `c`
used in the cost stream `cost = Q x $0.01 x FX` (spec §4.1 / §5.2).
Because `c` is a scale-invariant multiplier, it does not bias the
§4.3 FX-variance share. The materialized probe snapshot (request
manifest + decoded header payload) is written as a Tier-2 frozen
snapshot at Phase 1 task 1.3.

**HALT-DV (x402).** If the probe no longer returns a free
`payment-required` offer → HALT-DV; do NOT assume the $0.01 figure
(plan §1 task 1.3 non-bypassable data-fetch gate).

## 3. The R6 simulation-design blueprint hash

The load-bearing build (Phase 2 — the R6 NHPP query-workflow simulation
engine) is resurrected from a 19-task design spec that was never coded.
The blueprint is pinned by SHA-256 at Phase-0 entry so any drift in the
design document is detectable.

| Artifact | SHA-256 |
|---|---|
| `docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` (R6 blueprint, v0.1.3 APPROVED) | `f6f0c7c63e176225bd2bac76300e87ef3d2872fe1e558a658935978277409127` |
| `docs/specs/2026-05-20-e10-gsps-v0.4-convex-multicurrency-design.md` (E10 spec v0.4 DRAFT) | `20525c2d3448e68288d764149fef41d0ef6f19a6708a57975a37a77511f75553` |

## 4. Frozen at Phase-0 entry

The eight FX-endpoint manifest, the x402 price-probe manifest, the
decoded `payment-required` snapshot, the simulated-quantity declaration
(Q only — X and the FX multiplier are 100% real), and the R6 blueprint
hash are all FROZEN at this Phase-0 commit. Any drift triggers HALT-DV
per plan §3. The fantasy-firewall (plan Phase 0.12) mechanically
enforces that the FX series and the $0.01 multiplier are never sourced
from a fitted prior, a synthetic generator, or a placeholder constant.
