# Direction 2 — Colombian Import Micro-Vendors — Gate Decision

**Status:** COMPLETE — 2026-05-18
**Spec anchor:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 2 (v0.2)
**Effort:** 4 parallel sub-investigations + empirical DANE-zip download test

## Composite verdict

**CONDITIONAL PASS** — direction graduates to full-iteration spec v0.1 drafting, with three pre-registered scope conditions:

1. **Cohort = legal-entity micro-importers only** (natural-person importers are recategorized to NIT=0 by DIAN under Ley 1581/2012). Quantify exclusion magnitude as a counter in the data-build CLI.
2. **Aggregate panel (HS-chapter × origin × month) is the primary Y; firm-level join is conditional escalation only if aggregate β PASSes.** This honors the CLAUDE.md stage-drift discipline (don't balloon M-design / data-acquisition before β-existence is confirmed).
3. **Tariff/VAT step-function controls (γ·Δτ_t, δ·ΔVAT_t in the pre-pinned spec) MUST be implemented before any β regression.** The Decreto 414/2021 → Decreto 2598/2022 apparel step (15% → 40% NMF) and the 2026 postal de minimis collapse (USD 200 → USD 50) are dominant confounders that would absorb the FX β signal if uncontrolled. This is the D2-CR Blocker 2 closure.

## Sub-task results

| ID | Investigation | Verdict | Headline finding |
|---|---|---|---|
| D2.1 | DIAN / DANE customs data | **CONDITIONAL PASS** | Aggregate panel (HS-10 × origin × month) instant-free for N≈100 months 2008-2026. Firm-level NIT field empirically confirmed absent from public DANE microdata (41 fields actual vs 44 documented). Firm-level workaround via DIAN datos.gov.co Form 500 weekly (slug `fan6-7ztf`; Banrep Eslava et al. precedent) |
| D2.2 | RUES Confecámaras NIT join | **CONDITIONAL PASS** | NIT join feasible for legal entities via DIAN Form 500 → RUES `c82u-588k` Socrata; size column in RUES advanced-consulta CSV documented but unverified. Decreto 957/2019 thresholds confirmed by sector. Natural-person truncation permanent |
| D2.3 | ERPT literature priors | **PASS** | 7 Colombia + 10 EM point estimates; modal β=0.30-0.50 (1m import-price); asymmetry depreciation > appreciation 1.5-2×; Amiti-Itskhoki-Konings predicts small-importer β ≥0.70. Recommended primary prior `Normal(0.50, 0.20)` truncated [0,1] |
| D2.4 | Tariff + VAT step-function panel | **PASS** | 432-row panel (9yr × 4 chapters × 12m) constructible from public *decretos*/*leyes*; every step grounded in legal source. Dominant confounders: apparel τ 15%→40% (2021-22), postal de minimis USD 200→USD 50 (2026) |

## Pass criteria check (vs spec §Direction 2 v0.2)

| Criterion | Spec target | Actual | Status |
|---|---|---|---|
| Public-data monthly panel N ≥ 75 | ≥75 obs | ~100 months 2018-01→2026-04 | ✅ PASS |
| RUES size-classification join feasible | Yes | Conditional on advanced-consulta export `tamaño` column (1-day live test) | 🟡 CONDITIONAL |
| Importer count in micro brackets ≥ 5,000 | ≥5,000 | TBD on RUES pull; macro Tejido Empresarial reports suggest ~10-50K legal-entity micro-importers nationally | 🟡 To verify |
| ERPT priors ≥ 3 informative papers | ≥3 | 7 Colombia + 10 cross-country | ✅ PASS |
| Tariff/VAT control panel constructible | Yes | 432-row panel from public legal sources | ✅ PASS |

## Pre-pin (CARRIED FORWARD UNCHANGED from spec §0.2 — anti-fishing-locked)

| Field | Value |
|---|---|
| Sign | β_FX→cost > 0 (depreciation → higher COP-equivalent cost) [v0.1 spec had β<0 due to inverted sign convention; corrected here to match ERPT-literature convention] |
| Magnitude floor | \|β\| ≥ 0.10 SD-units (lower bound, raised from spec 0.05 given Amiti-Itskhoki-Konings micro-importer upshift) |
| Lag | Contemporaneous primary; k=1 month secondary; k>3 BANNED |
| Primary specification | `Δlog(Y_cost)_t = α + β·Δlog(TRM)_t + γ·Δτ_{c,t} + δ·ΔVAT_{c,t} + chapter FE + ε_t` (panel: month × chapter; HS chapters 85, 61, 62, 94 primary basket) |
| Inference | HAC with L = ⌊T^(1/3)⌋; cluster-robust by chapter |
| Power floor | 0.80 |
| HALT chain | Spec-vs-data contradiction → disposition memo + user-enumerated pivot |
| Bayesian prior (if Bayesian spec adopted) | β ~ Normal(0.50, 0.20) truncated [0,1] |

**Note on sign-flip from v0.2 spec:** spec §Direction 2 pre-pin had β<0 ("higher COP/USD → lower margin"). The ERPT literature convention is β>0 for `Y_cost = USD_imports × spot × (1+τ+VAT)` (higher spot → higher cost). The economic content is identical (cost rises when COP weakens); only the sign convention differs. Locking β>0 here to match literature priors. Spec v0.3 amendment to follow for canonical alignment.

## Recommendations for full iteration (Direction 2, spec v0.1)

1. **HS scope:** primary basket HS 85, 61, 62, 94. Secondary sensitivity: 42, 64, 95, 71, 39, 90.
2. **Time window:** 2018-01 → 2024-12 for stable τ regime (avoid the 2025-2026 postal de minimis confounder unless interaction term added).
3. **Y construction:** `Y_cost_{c,t} = Σ_subhdg (CIF_USD × TRM × (1 + τ_{subhdg,t} + IVA_{c,t}))` aggregated to chapter-month. Use VACID field from DANE microdata (CIF USD).
4. **Data pipeline:** 
   - Stage 1 (this gate): aggregate β-existence test on chapter × month
   - Stage 2 (if Stage 1 PASS): firm-level via DIAN Form 500 + RUES join
5. **M-sketch (cohort-wallet perspective per §0.1):** one-sided long-call on USDCOP, sized to next-quarter expected USD COGS commitment. Premium funded via working-capital financing spread (financialization-channel link to the user's `FINANCILATION.md` framework: micro-vendors typically access COP-denominated working-capital loans; the FX-protection premium can be funded from the margin between loan COP cost and USD-denominated COGS pass-through).
6. **Anti-fishing tripwires carried forward:**
   - Decreto 414/2021 and Decreto 2598/2022 apparel-τ step MUST be included as covariate before β estimation. Omitting them post-hoc to recover a desired β = silent-fishing.
   - 2026 postal de minimis sample-end period treated as caveat regime; β estimated 2018-2024 primary.
   - Sign-flip from spec v0.2 pre-pin (β<0 → β>0) is a convention change, NOT a methodology change; locked here before any data is touched.

## Open issues escalated to user

1. **Cohort labeling**: "legal-entity micro-importers" (excluding natural persons) — accept as cohort scope, or descope direction in favor of one that includes natural-person micro-importers (would require different data path entirely)?
2. **Sign-flip from spec v0.2** (β<0 → β>0): accept as convention-only amendment to spec v0.3, or trigger full 2-way re-review of v0.3?
3. **Sequencing of next gates**: D2 PASS clears the queue. Confirm dispatch of D1-G1 + D4 in parallel per §0.6, or hold for D2 full-iteration spec drafting first?
4. **Stage-correction**: Stage-1 aggregate-only first per CLAUDE.md stage-drift discipline (recommended), or attempt firm-level direct?

## Files

- `01_dian_pull/findings.md` — DIAN/DANE data availability + empirical NIT-suppression test
- `02_rues_join/findings.md` — RUES Confecámaras join feasibility + Decreto 957/2019 thresholds
- `03_erpt_priors/findings.md` — ERPT priors with literature anchors
- `04_tariff_vat_panel/findings.md` — Tariff + VAT step-function panel 2018-2026 + 432-row schema
- `gate_decision.md` — this file
