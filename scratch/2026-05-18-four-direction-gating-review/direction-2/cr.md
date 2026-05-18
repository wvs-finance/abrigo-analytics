# Code Reviewer — Direction 2 (Colombian Import Micro-Vendors)

**Reviewer**: Code Reviewer
**Date**: 2026-05-18
**Spec under review**: `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 2 (lines 69–121)
**Verdict (gate-stage)**: CONDITIONAL — gating step is feasibility-only and may proceed, but the spec carries six unresolved methodology defects that MUST be closed before a full β-iteration is dispatched. Three are blockers (must-fix); two are suggestions; one is a nit. The most consequential blocker is the Y construction (1), which as written cannot identify the FX channel.

## Summary

Direction 2 proposes a (Y, M, X) triple where Y is unit margin of import-resale micro-vendors, X is COP/USD spot/vol, and M is a long-gamma Panoptic straddle on USDC/COPm sized to next-quarter USD COGS commitments. The gating question — "can DIAN customs data be disaggregated to a micro-importer cohort for ≥75 months?" — is well-posed and feasible at the gate-stage. Cohort sizing, factor-prior construction sketch, and microdata-request fallback are all in the right ballpark.

However, the *iteration-stage* methodology has gaps that would invalidate the β estimate if the gate passes and the iteration is dispatched without revision. Most importantly, the proposed Y is contaminated by demand-side variation; the spec ignores tariff/VAT regime changes as confounders; the Centrifuge factor-prior story conflates credit-spread and FX-pass-through loadings; the M-design direction is wrong-way for a COP-revenue / USD-COGS vendor; and the spec lacks an anti-fishing pre-pin. These are the same class of defects that closed FX-vol-on-CPI-surprise and dev_ai_cost_v2 — surfacing them at the gate is the cheap moment.

What's good: cohort-relevance thresholds are concrete (≥5,000 importers in target RUT brackets, ≥75 obs), the parallel public/proxy track (DIAN public quarterly → microdata request → Mercado Libre as third tier) is well-sequenced, the Centrifuge factor-prior idea is creative and the right direction for small-N Bayesian shrinkage, and the gate carries a real FAIL branch.

---

## Findings

### 🔴 1. Blocker — Y definition does not isolate the FX channel

**Spec, line 72**:
```
margin = COP_sale_price - (USD_unit_cost × spot_COP_USD × (1+import_tariff+VAT))
```

**Why this fails identification**: `COP_sale_price` is endogenous to the same macro shocks that drive `spot_COP_USD`. On the demand side, COP-denominated retail prices vary with (a) Colombian consumer demand cycles, (b) competing-vendor entry/exit, (c) Mercado Libre platform-fee changes, (d) seasonality (Black Friday, Día sin IVA, end-of-year), (e) consumer-electronics global price decay (HS-code level, ~−15-25% YoY for SKUs that age). On the cost side, `USD_unit_cost` is also endogenous — Aliexpress / Alibaba list prices respond to CNY/USD and to global chip cycles. The "margin" is then a composite of FX shock + demand shock + global cost shock + tariff/VAT regime + platform-fee shock + SKU-age decay. β on `spot_COP_USD` recovers the FX-channel only under the heroic assumption that all five other channels are orthogonal to spot — which they are not (Colombian demand cycles correlate with the terms-of-trade that drive COP/USD).

**Suggestion**: redefine Y at iteration-stage as one of:

- **(preferred) cost-side residual**. Drop the sale price entirely. Y_cost = `USD_unit_cost × spot × (1 + tariff + VAT)` measured in COP per imported unit. This isolates the cost-channel transmission of FX cleanly; the test becomes "does Y_cost track spot at the unit-level / cohort-aggregate scale we expect under full pass-through". Margin is then a downstream object you can comment on but not the regression target.
- **(if margin is load-bearing for the policy story)** margin *residual* after partialling-out category-level demand: `Y = margin - E[margin | category × month-of-year × platform-fee × global-CN-price-index]`. Requires the right-hand controls actually be measured — none of them are listed in the Data inputs section.
- **(weakest)** keep margin, but pre-pin that the test is on the *covariance* of margin with FX after a Cochrane-Orcutt-style demand filter, and document the residual confounding explicitly.

This is a Y-design issue, not an estimator issue. It cannot be patched by HAC errors or by adding controls late.

---

### 🔴 2. Blocker — Tariff/VAT regime changes as confounders are not addressed

**Spec, line 72**: the formula treats `import_tariff` and `VAT` as constants inside the Y formula. The gating-step data plan (lines 79–88) does not mention tariff-regime tracking.

**Why this matters**: Colombian import tariffs on consumer electronics, apparel, and household goods have changed non-trivially over 2018–2026:

- The 2018 anti-dumping investigation on Chinese textiles and the resulting Resolución duties (variable 2018-2021).
- The 2020 COVID-era temporary tariff suspensions on medical and ICT goods.
- The 2022 Resolución MinComercio tariff increases on textiles/apparel to protect domestic producers (~40% Arancel external + 19% IVA stack on some HS chapters).
- IVA-15% / IVA-19% bracket reshuffles under the Petro tax reforms (Ley 2277 of 2022).
- The 2024-2025 Mercado Libre / Aliexpress de minimis-threshold tightening (USD 200 → USD 200 with stricter enforcement, plus 19% IVA on cross-border parcels under the "tributación a importaciones de menor valor" decree).

Each of these is a step-change in the tariff/VAT term inside the Y formula. If un-modeled, they show up as level shifts in Y that correlate with the macro-policy cycle and therefore with COP/USD — biasing β.

**Suggestion**: at iteration-stage, before estimating β, the spec must:
- Compile an HS-code-level monthly tariff+VAT panel from MinComercio Resoluciones + DIAN aranceles consolidados. (DIAN publishes this; it's manual but small — ~10 chapters × 96 months = ~1000 cells.)
- Treat tariff/VAT regimes as known step functions, NOT as free parameters. Either enter them in the Y formula explicitly (so Y is "FX-cost-component-only") or include regime-dummies in the regression with pre-pinned breakpoints.
- Pre-pin which HS chapters are in-scope BEFORE looking at the data. Chapter selection post-hoc that maximizes β is silent fishing.

Add this to the gating-step data-input list now (`Day 1.5` between DIAN public-data pull and Centrifuge query); otherwise the iteration-stage tariff audit becomes a 2-week surprise.

---

### 🔴 3. Blocker — DIAN aggregate confounds micro and large-firm exposures unless the RUT-size filter is strict and disclosed

**Spec, lines 81–82**: "Importer RUT size bracket (DIAN classifies importers; the smallest brackets approximate the micro-cohort)". **Spec, line 116**: "the DIAN HS-code + RUT-size cross-tab may not be available simultaneously (joint disaggregation is more restrictive than either margin alone)".

**Why this matters**: aggregate USD imports from a given HS code reflect *all* importers — Falabella, Éxito, Mercado Libre's own first-party, Alibaba B2B brokers, and individual micro-vendors. The β you get from regressing aggregate `USD_imports × spot` on FX has no micro-vendor interpretation. The RUT-size filter is what carries the entire population-relevance claim of Direction 2. If joint disaggregation (HS × RUT-size × month) is not available, the iteration cannot proceed under the proposed Y.

Worse, the spec line 116 acknowledges this as a risk but does not make joint-disaggregation availability a HARD gate criterion. As written, the gate could PASS on "≥75 obs of DIAN data" even if those obs are only HS-only or RUT-only marginals.

**Suggestion**: add to Pass criteria explicitly:

> "DIAN data yields ≥75 obs of monthly OR ≥32 obs of quarterly imports at the JOINT HS-code × RUT-size × origin-country granularity. Marginal-only availability is FAIL."

If joint cross-tab is unavailable from public data, the spec should pre-commit to: (a) filing the microdata request as the only path, accepting the 4-6 week wall-clock, or (b) closing the direction. The current "DIAN public data yields ≥75 monthly or quarterly observations" criterion (line 97) is too loose — quarterly N=32 with marginal-only disaggregation is *not* an estimable micro-cohort panel.

Also: even with joint disaggregation, "smallest RUT bracket" is a DIAN-defined heuristic (likely "Pequeño Importador" by import-value threshold). Verify what the threshold is — if it admits importers with USD 500K-1M/yr, that is not the micro-vendor cohort the policy story requires. Pre-pin the bracket boundary in the spec.

---

### 🟡 4. Suggestion — Centrifuge factor priors confuse credit-spread loadings with FX-pass-through loadings

**Spec, lines 86, 92–93, 99**: proposes Centrifuge BRL / NGN / IDR / MXN / ZAR tokenized-credit pools as factor-loading anchors for "EM trade-finance" priors.

**Why this is wrong-target**: a Centrifuge BRL pool token's NAV / yield reflects (i) BRL-denominated credit default risk on a specific pool of invoices, (ii) the EM credit spread term structure, (iii) the BRL funding-rate term structure, (iv) idiosyncratic origination-quality of that pool's underwriter. None of these is `BRL_pass_through_coefficient_of_USD_costs_into_BRL_revenue_margins`. The cross-EM transferable factor for Direction 2 is the FX pass-through coefficient β_FX→margin, NOT the credit spread coefficient β_credit→pool_NAV.

Concretely: a high Centrifuge NGN pool yield in 2024 tells you about Nigerian default risk and the naira funding stress, not about how a Lagos micro-importer's margin compressed when USD/NGN moved. Using the pool NAV as a Bayesian prior loading on the Colombian micro-vendor β_FX is a category error.

**Suggestion**: either:
- Repurpose Centrifuge data as a *demand-side* anchor (does EM trade-finance pool activity contract during local-FX-stress periods? → activity proxy, not factor loading), and use it as a covariate or sample-selection signal, not as a prior on β_FX→margin.
- Drop the Centrifuge prior entirely and source FX-pass-through priors from published exchange-rate-pass-through literature for EM consumer-import margins (Burstein-Eichenbaum-Rebelo 2005; Goldberg-Campa 2010; or recent BIS WP on EM ERPT). This literature has β_FX→retail-price coefficients in the right family.
- Use Centrifuge only for the M-side (does Centrifuge LP yield correlate with COPm/USDC pool yield enough to act as an off-Panoptic liquidity sleeve?) — that *is* a credit-spread question and Centrifuge data is right-target for it.

This finding doesn't block the gate (Centrifuge factor-pool inventory is still a useful Day-2 task) but the spec must clarify what *role* the Centrifuge data plays before it becomes a prior in the iteration's Bayesian setup. The current wording (line 86 "factor-loading anchors", line 99 "Bayesian prior construction") asserts a use that the data cannot support.

---

### 🟡 5. Suggestion — Tokenization-as-Y-observability breaks the permissionless premise

**Spec, line 74**: "Alternatively, a *tokenized invoice basket* on Centrifuge whose pool token / COPm spread provides the on-chain Y observable."

**Why this is a tension with Abrigo framing**: per `CLAUDE.md`, the instrument family is "permissionless on-chain perpetual convex instruments, settled on Panoptic". Tokenizing real-world Colombian micro-vendor invoices requires:
- An off-chain custodian to hold the legal-claim invoice documents.
- A legal wrapper (SPV, fideicomiso, or similar) under Colombian securities law to issue the pool token.
- KYC on the originating vendors.
- An off-chain servicer to chase invoice payments.
- Probably a Colombian Superfinanciera registration or qualified-investor exemption.

None of these is permissionless. The Y becomes "on-chain observable" only in the trivial sense that a token price is on-chain — but the underlying cash-flow attestation is fully off-chain trust-laden. This duplicates Goldfinch / Centrifuge's existing tradeoff and inherits its KYC + jurisdictional friction.

**Suggestion**: at iteration-stage, drop the tokenization-as-Y path and treat Y as off-chain-measured (DIAN-derived cohort-aggregate `USD_imports × spot`). The on-chain settlement of M (Panoptic USDC/COPm) is independent of how Y is measured — there is no need to force Y on-chain for the Abrigo framework to function. Method step 5 (line 94: "Decide whether the on-chain Y observable requires the tokenization step ... or can be approximated by `DIAN_USD_imports × spot_COP_USD` directly") already half-acknowledges this; lock in the second option.

Keep the Centrifuge angle alive but reframe it as M-side liquidity infrastructure, not as a Y-observation mechanism.

---

### 🔴 6. Blocker — M-design direction is wrong-way; straddle vs put choice not justified

**Spec, line 74**: "long-gamma straddle on USDC/COPm Panoptic pool, sized to next-quarter USD COGS commitment".

**Why this is direction-wrong**: a COP-revenue / USD-COGS micro-vendor is exposed to *one-sided* FX risk — COP depreciation (USDCOP up) raises their COP cost of next-quarter USD inventory, compressing margin. COP appreciation (USDCOP down) reduces COGS in COP and *expands* margin, which is favorable for the vendor; they do not need a hedge payoff on the favorable side. A straddle pays out on both tails, which means the vendor is paying premium for protection on a direction they do not need protection against.

The right M is a one-sided long-USDC / short-COPm position, i.e. a long call on USDCOP or equivalently a long put on COPm/USDC, sized to next-quarter USD COGS. (This is structurally identical to Direction 1's M but with the COGS commitment as notional instead of wage receivable.) The premium funding via covered-yield overlay still applies.

The "long-gamma straddle" terminology may be inherited from Direction 3's stress-event framing where both tails matter (jump on either side disrupts the cost panel). For a micro-vendor's premium-funded hedge, the asymmetric exposure dominates and straddle is structurally over-priced for the protection delivered.

**Suggestion**: at iteration-stage M-sketch, replace "long-gamma straddle" with "long-call on USDCOP (equivalently long-put on COPm/USDC) struck near current spot, expiring next-quarter, sized to USD COGS commitment". If you want optionality on the appreciation side (margin-expansion capture for the premium-funded ratchet), structure that explicitly as a covered short on the favorable side, not as a symmetric straddle.

Cross-check this against `memory/project_corrections_alpha_predicate_long_vol.md` if it covers the long-vol M-class (the title suggests there's prior guidance on long-vol M choices).

---

### 🔴 7. Blocker — No anti-fishing pre-pin

**Spec, Direction 2 section (lines 69–121)**: there is no pre-pinned sign expectation, lag structure, magnitude floor, or primary specification for the iteration-stage β.

**Why this matters**: per `feedback_pathological_halt_anti_fishing_checkpoint.md` and the CLAUDE.md anti-fishing invariants, sign / magnitude / lag / primary-spec pre-pin must be in place BEFORE data is touched. Direction 3 has this (lines 153–159 — sign β_stress > β_calm > 0, magnitude β_stress ≥ 0.05 SD-units, contemporaneous primary 1-day-lag secondary, decomposition method pinned to Barndorff-Nielsen). Direction 2 has none of it.

The gate-step itself is exempt from N_MIN (per line 9), but the iteration that follows is not exempt from pre-pin. The spec is the right place to pre-pin, not the iteration's notebook.

**Suggestion**: add to Direction 2 spec, before pass criteria:

```
### Pre-pin (iteration-stage; gate-step exempt)
- Sign: β_{spot → cohort-aggregate-USD-cost-in-COP} > 0 (COP depreciation raises COP-cost
  of fixed USD imports; full pass-through implies β ≈ 1.0).
- Magnitude floor: β ≥ 0.40 (incomplete pass-through expected per Burstein-Eichenbaum-Rebelo
  / Goldberg-Campa EM literature; below 0.40 means the channel is mostly absorbed by
  upstream supplier margin or downstream demand-elasticity, neither of which the
  micro-vendor M can hedge).
- Lag: contemporaneous primary; 1-month and 3-month lag as secondary (covering the
  in-transit + customs-clearance + inventory-turnover window).
- Primary spec: cohort-aggregate Y_cost on contemporaneous Δlog(spot), with HS-chapter
  fixed effects and tariff-regime-dummy controls. HAC errors at 3-month lag.
- HS-chapter scope pinned: chapters {84 ICT, 85 electronics, 61-62 apparel, 64 footwear,
  94 furniture} OR whichever subset DIAN joint-disaggregation actually supports — pin
  the subset before estimation, not after.
```

Without this, Direction 2's β-iteration is born exposed to the same garden-of-forking-paths inflation that closed FX-vol-on-CPI-surprise.

---

### 💭 8. Nit — Day-3 task is mis-scoped

**Spec, line 110**: "Day 3: Mercado Libre API capability assessment (do we even need the seller-side Y, or is import-side X enough for a one-sided test?)".

The phrasing "import-side X" is a slip — DIAN imports are the *Y-input* (cost-side), not the X. X is COP/USD spot. The question being asked is real and useful (do we need ML seller-side data at all, or can we run the iteration on cost-side Y alone), but the framing is muddled.

**Suggestion**: rephrase as "Day 3: assess whether DIAN-derived cost-side Y is sufficient for the β-test, or whether Mercado Libre seller-side revenue is required to close the margin formula. If cost-side-only is sufficient (per Finding 1 above), descope ML access from the gating step entirely."

This nit interacts with Finding 1 — if Y is redefined as cost-side residual, ML access stops being a dependency and the gate simplifies.

---

## Cross-references to existing project state

- `memory/project_fx_vol_cpi_notebook_complete.md`: closed-FAIL precedent for a Y-on-FX iteration where the channel was suppressed by confounders. Direction 2's Finding 1 (Y contamination) is the same failure mode.
- `memory/project_pair_d_phase2_pass.md`: the canonical PASS comparison. Pair D's Y is clean (offshoring service flows, denominated in USD, observed at firm-level) and the FX channel transmits without demand-side intermediation. Direction 2 must aim for that level of Y-cleanness or it will re-trace the FX-vol-CPI failure.
- `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`: the discipline that Finding 7 invokes.

## Recommendation

**Gate**: PROCEED with the 5-day feasibility step as written, modified to add (a) Finding 3's stricter joint-disaggregation pass criterion, (b) Finding 2's Day-1.5 tariff/VAT regime panel compile, (c) Finding 8's Day-3 rescope.

**Pre-iteration block**: do NOT dispatch a full β-iteration until Findings 1, 6, and 7 are closed via a spec revision. The remaining blocker (Finding 3) is a gate-step output — if joint disaggregation is unavailable, direction closes regardless.

**Suggested order**: spec revision (1 day) → gate-step execution (5 days) → if PASS, iteration spec v0.1 with the pre-pin block (Finding 7) → R6-style 2-way review → dispatch.

Files touched in this review: this CR only. No code changes.
