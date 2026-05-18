# Four-Direction Gating-Step Plan — 8-Agent Review Consolidation

**Date:** 2026-05-18
**Spec under review:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` (v0.1)
**Reviews:** 4 × Reality Checker + 4 × Code Reviewer = 8 independent passes
**Output of consolidation:** spec amendments (→ v0.2) + revised decision matrix + Direction 3 re-scope recommendation

---

## Per-direction verdict roll-up

| Direction | RC verdict | CR verdict | Net status |
|---|---|---|---|
| 1 — USD-paid remote workers (ADP) | NEEDS_WORK | CONDITIONAL_APPROVE | **AMEND-BEFORE-DISPATCH** |
| 2 — Import micro-vendors (DIAN+Centrifuge) | CONDITIONAL PASS | CONDITIONAL | **AMEND-BEFORE-DISPATCH** |
| 3 — Jump-conditional re-test | NEEDS WORK | CONDITIONAL | **RE-SCOPE — dead on arrival at N=29** |
| 4 — USDC-saver cohort | NEEDS_WORK | CONDITIONAL PASS | **AMEND-BEFORE-DISPATCH** |

No direction passed clean. Three of four are amend-and-dispatch; one (Direction 3) is recommended for hard re-scope or close.

---

## Cross-direction pattern findings

### Pattern A — M-hedge direction sign errors (4 of 4 M-design reviews)
Every direction with an M-sketch had at least one reviewer flag a wrong-way hedge:
- **D1**: spec said long-USDC / short-COPm — should be **long-COPm / short-USDC** (cohort already naturally long-USD; spec doubled the exposure)
- **D2**: spec said long-gamma straddle — should be **one-sided long-call on USDCOP** (vendor exposure is one-sided to COP depreciation; straddle wastes premium on appreciation tail)
- **D4**: spec said "short-tail Panoptic position" — should be **long-tail (long OTM put on USDC)** (cohort is structurally short-tail by holding USDC; needs to *buy* tail protection)

**Root cause:** the spec author (me) conflated "the protocol-side position that absorbs the cohort's risk" with "the cohort's hedge position." These are inverses.

### Pattern B — Missing or weak anti-fishing pre-pin (universal)
D3 had a pre-pin block but with hidden DOF (threshold percentile, rolling window, jump-σ multiple, asymmetry sign all unpinned). D1, D2, D4 had no pre-pin at all. Direction 3's silent POWER_MIN relaxation 0.80 → 0.50 without a CORRECTIONS block is the exact pattern banned by `feedback_pathological_halt_anti_fishing_checkpoint.md`.

### Pattern C — Factual errors in data-source claims
- **D1**: DANE GEIH "foreign employer" identifier almost certainly does not exist — GEIH Migration Module covers immigrants *into* CO, not Colombians working *for* foreign employers. Banrep BoP "computer services" is firm-invoice revenue, not worker wages. ADP CPO pathway is 4-12 weeks, not 5 days.
- **D2**: DIAN monthly imports data is **public default** since 2001 (not gated). DIAN classifies importers by **legal form, not size** — micro/small classification requires Decreto 957/2019 RUES join via Confecámaras. **No active Centrifuge EM-currency trade-finance pools exist in 2026** (active pools are US-Treasury/carbon: Anemoy, JTRSY, JAAA, Flowcarbon). Goldfinch V1 borrower pools are mostly closed.
- **D3**: Spec claimed N≈150 trading days; actual `notional_cost_panel.parquet` is N=29 rows (N=28 post-first-diff). 150 was TRM trading-days available, not regression observations. Empirical jump census (D3-RC ran it): **0 days exceed |3σ|, 2 days exceed |2.5σ|, 6 days exceed |2σ|** on the 137-day TRM window → intersected with N=29 cost rows gives ~2-4 stress observations. Spec's own FAIL criterion (jump count < 5) fires before any analysis.
- **D4**: Bitso/Lemon/Buenbit do **not** publish Colombia-specific USDC AUM (Bitso has LATAM-aggregate flows; Lemon Colombia operation <6 months old; Buenbit no public CO disclosures). Only **2-3 genuine USDC depeg events** exist (Mar-2023 SVB; possibly Oct-2025 flash-crash); the ≥20 events ≥ 0.5% criterion conflates noise with events (S&P cited 609 stablecoin instances in 2023 alone). Dune public dashboards cannot tag wallets by country.

### Pattern D — Confounding / identification gaps
- **D1**: Mechanical identity risk (β = 1 on contemporaneous spot is tautology, not behavior); Y triple-collapse (nominal vs real vs Δlog); survival bias (currently-USD-paid is selection on outcome)
- **D2**: Tariff/VAT regime changes 2018-2026 are unmodeled step-functions correlated with macro policy and therefore with COP/USD; margin Y contaminates FX channel with demand variation
- **D3**: Bipower variation at daily frequency is theoretically misapplied (BNS 2004 requires intraday Δ→0); Lee-Mykland 2008 is the daily-applicable alternative
- **D4**: Compound-Y conflates depeg + FX channels; March-2023 SVB event coincided with USD strength → confounded by construction

---

## Decision matrix for user gate decision

| Direction | Mandatory amendments before dispatch | Wall-clock to amend | Wall-clock to execute gate | Recommendation |
|---|---|---|---|---|
| **1 — ADP** | (1) Pre-pin sign/mag/lag block; (2) flip M-direction to long-COPm; (3) cohort definition with open-vs-balanced choice; (4) split into G1 (5-day public-data) + G2 (4-12 week ADP) phases; (5) verify GEIH foreign-employer variable on Day 0 before commit; (6) replace Banrep BoP wage-line claim with services-exports-as-firm-revenue proxy | 1 day | G1 5 days; G2 4-12 weeks wall-clock | **AMEND + DISPATCH G1 only**; G2 conditional on G1 result |
| **2 — Micro-vendors** | (1) Pre-pin sign/mag/lag; (2) flip M to one-sided long-call USDCOP; (3) replace Centrifuge factor-prior claim with published ERPT literature (Burstein-Eichenbaum-Rebelo / Goldberg-Campa / BIS); (4) add RUES Decreto 957/2019 importer-size join as a *separate* data step; (5) reformulate Y as cost-side `USD_imports × spot × (1+tariff+VAT)` with explicit tariff/VAT panel; (6) drop tokenization-as-Y-observability (breaks permissionless premise) | 1 day | 5 days (DIAN monthly is public default, faster than spec assumed) | **AMEND + DISPATCH** |
| **3 — Jump re-test** | Recommendation: **RE-SCOPE to 1-day census-only gate** that returns FAIL on jump count, no notebook | 0.5 day | 1 day | **RE-SCOPE, write up as closed FAIL** |
| **4 — USDC-saver** | (1) Pre-pin EVT DOF (estimator family, threshold u, inference method); (2) flip M-direction to long-tail OTM put on USDC; (3) decompose Y to isolate depeg channel from FX channel; (4) downgrade cohort estimation to Fermi-bound only (Bitso/Lemon don't publish Colombia-cut); (5) revise event-count criterion to ≥2 genuine episodes + tail-distance-from-peg quantile criterion (not ≥20 noise events); (6) extend effort from 3 to 5 days | 0.5 day | 5 days | **AMEND + DISPATCH** |

---

## Critical realization — M-design taxonomy correction needed system-wide

The 4-of-4 M-direction error pattern means the entire framework's M-design step needs an explicit *cohort-side-vs-protocol-side* taxonomy. Adding to the consolidation amendments: a §0 "M-direction conventions" block stating that all M-sketches are written from the **cohort's wallet** perspective (the wage earner / vendor / saver), not the protocol-side counterparty perspective. This avoids the entire class of sign errors going forward.

---

## Anti-fishing carry-forward — strict reading

The 4-of-4 missing-pre-pin pattern means the spec v0.2 must enforce **a uniform pre-pin block** in every direction subsection, with the same 7 required fields:
1. Sign expectation (β > 0, β < 0, asymmetric)
2. Magnitude floor (SD-units of Y)
3. Lag (contemporaneous / k=1 / longer; banned beyond k=3 unless theory-justified)
4. Primary specification (one and only one)
5. Inference method (HAC bandwidth, bootstrap method, EVT estimator)
6. Power floor (default 0.80; demonstration-grade exception requires explicit user approval)
7. HALT chain on spec-vs-data contradiction

D3's pre-pin had 4 of these but missed (1) asymmetry sign, (5) bootstrap validity on jump subset (recommended permutation instead), (6) power-floor relaxation without CORRECTIONS block.

---

## Recommended sequence

1. **Amend spec to v0.2** integrating the cross-direction patterns + per-direction MUST fixes (Pattern A M-sign block, Pattern B uniform pre-pin block, Pattern C fact corrections).
2. **Close Direction 3** as RE-SCOPED-FAIL with a brief disposition memo (the empirical jump census already done by D3-RC is the headline evidence).
3. **User gate decision**: which of D1/D2/D4 to dispatch first? My recommendation: **D2** because (a) DIAN data is genuinely public-default and the gate can run cleanly in 5 days; (b) the Numo-NGN analog has the strongest a-priori theoretical support; (c) D1 is wall-clock-bound on ADP CPO; D4 needs Fermi-grade cohort estimation which is borderline.
4. **Optional: dispatch D1-G1 (public-data-only) in parallel** since it shares no data dependencies with D2.
5. **D4** queued for week-2 after D1-G1 and D2 results inform priors.

---

## Open issues escalated to user

1. **Direction 3 disposition**: confirm RE-SCOPED-FAIL closure, or override and dispatch as census-only?
2. **D1 G1+G2 split**: confirm dispatching G1 (public-data) now without waiting for ADP CPO clearance, or wait until ADP yes/no before any work?
3. **D4 cohort estimation downgrade**: accept Fermi-grade cohort sizing as sufficient for gate decision, or hold for commercial on-chain analytics scoping (Arkham/Chainalysis)?
4. **Sequencing**: dispatch D2 + D1-G1 in parallel (recommended), or strict serial D2 → D1-G1 → D4?
