# Reality Checker — Direction 4 (USDC-Saver Colombian Cohort, Stablecoin De-Peg X)

**Reviewer**: TestingRealityChecker (Reality Checker lens)
**Spec under review**: `docs/specs/2026-05-18-four-direction-gating-step-plans.md` Direction 4 (lines 185–233)
**Date**: 2026-05-18
**Default disposition**: NEEDS WORK unless overwhelming evidence supports gating-step feasibility as written

---

## Headline verdict

**NEEDS WORK — gating step has THREE concrete feasibility breaks and ONE conceptual confusion that must be repaired before dispatch.** The direction itself is *substantively* defensible (Abrigo edge is real, on-chain-native cohort is genuine, depeg risk is novel for retail). The breaks are in the gating-step CRITERIA, not the iteration thesis. Specifically: (1) the "≥20 depeg events at ≥0.5%" pass criterion is empirically wrong and would falsely PASS the gate on microstructure noise; (2) the "≥10K Colombian USDC wallets" threshold has no empirical anchor; (3) Bitso/Lemon/Buenbit do not publish Colombia-specific USDC AUM; (4) the spec text conflates **cohort size** (population denominator) with **sample N** (panel observations for β estimation) — these are independent gates and the spec treats them as if one implies the other.

---

## 1. Bitso / Lemon / Buenbit Colombian USDC AUM disclosure — DOES NOT EXIST AS SPECIFIED

**Spec claim** (lines 196–198): "Bitso publishes quarterly transparency reports. May include Colombian USDC AUM aggregate. Lemon Cash transparency disclosures … Colombian USDC holdings may be inferable. Buenbit Colombia disclosures — same path."

**Reality**:

- **Bitso publishes regional/LATAM aggregates, NOT Colombia-specific USDC AUM.** The Bitso "2025 Latin America Cryptocurrency Landscape Report" (released May 2026) discloses *purchase-mix percentages* across Argentina/Brazil/Colombia/Mexico (USDC 23%, BTC 18%, USDT 16% of purchases LATAM-wide) — these are *flow* numbers, not *stock* (AUM) numbers, and not Colombia-disaggregated for USDC specifically. The spec assumes a stock disclosure that does not exist publicly.
- **Lemon Cash publishes Proof-of-Reserves / Proof-of-Liabilities at a global Merkle-tree level**, not jurisdiction-disaggregated. Their PoR shows ~$160M aggregate user assets backed by on-chain reserves; there is **no public Colombia-cut**. Lemon is Argentina-primary and only launched the Colombia pilot in late 2025 (per Colombia Fintech 2025-10-16 article) — the Colombian AUM stock is *operationally too young* (≤6 months at gate time) to yield any longitudinal panel even if disclosed.
- **Buenbit does not publish public AUM transparency reports at the country level.** This claim in the spec appears to be wishful — no evidence found of Buenbit Colombia disclosures.

**Mitigation cited in spec** (line 227): "use total LATAM USDC AUM × Colombia-share-of-LATAM-users (rough but defensible)". Reality check: Bitso's own LATAM "share" reporting does not break out Colombia from the Argentina/Brazil/Mexico aggregate at AUM granularity. Colombia-share-of-LATAM-USERS (from press claims of ~6M LATAM users) is *user count*, not *USDC dollar AUM* — USDC dollar holdings per user are highly skewed (Pareto), so users-share ≠ AUM-share. Defensible only if the spec explicitly flags the multiplication as a Fermi estimate, not a measurement.

**Verdict on §Data inputs 1–3**: spec needs to be rewritten as "attempt to obtain Colombia-specific AUM; **expect to fail**; pre-commit to the Fermi-estimate fallback with explicit error bars". Otherwise Day-1 of the gate produces an immediate disposition memo with no data, which is fine for closing the gate but should be PRE-ENUMERATED in the spec, not discovered.

---

## 2. ≥10K Colombian USDC wallets pass criterion — NO EMPIRICAL ANCHOR

**Spec claim** (line 212): "Estimated distinct Colombian USDC-holder addresses ≥ 10,000."

**Reality**:

- The "10K wallets" number appears in the spec without citation. It's plausibly a round-number floor, but in a gating step the floor must have a defensible source.
- Bitso has ~6M LATAM users total (2023 Series C public claim). Colombian fraction of Bitso users is unpublished. *Order-of-magnitude triangulation*: Colombia ≈ 50M population vs LATAM-key-markets (AR + BR + MX + CO) ≈ 380M; Colombian share by population ≈ 13%. Applying 13% to 6M ≈ 780K Bitso Colombian users total (across all assets, not just USDC). If 23% of *purchase activity* is USDC (LATAM-wide proxy) and active-USDC-holder rate is some fraction of active users, the plausible Colombian USDC-holder count on Bitso alone is 50K–300K. Lemon adds maybe 10K–50K (six-month-old Colombian operation). Buenbit's Colombian footprint is smaller.
- So the 10K floor is **almost certainly cleared**, but for the wrong reason: it's far below the plausible band. The criterion as written is non-binding — it will PASS regardless of what the data actually says, which means the gate doesn't gate. A useful gate would set the floor where the spec genuinely doesn't know if it'll pass (e.g., 100K or 250K).
- Conversely, if the *intent* was to set a "permissionless-hedge demand base" floor (line 217), 10K is plausibly correct, but it should be justified ("smallest cohort at which a Panoptic position has measurable retail demand") not asserted.

**Verdict on §Pass criteria**: the 10K threshold needs to be either (a) raised to a level that genuinely binds, or (b) explicitly justified as a "minimum demand base for permissionless hedge" with a citation to whatever industry / Panoptic-pool data informs the floor. Current spec lacks both.

---

## 3. ≥20 depeg events at ≥0.5% pass criterion — EMPIRICALLY WRONG, CONFLATES NOISE WITH EVENTS

**Spec claim** (lines 213, 218): "Historical USDC depeg events of magnitude ≥ 0.5%: count ≥ 20 (sufficient for EVT tail estimation)" / fail-criterion "count < 5".

**Reality** (verified against public USDC depeg literature):

- **Genuine USDC depeg events** in the 2018-09 → 2026-05 window:
  - **March 2023 SVB**: drop to ~$0.88, magnitude ~12%. This is the canonical event.
  - **Earlier 2023 flash-crash** on Binance to ~$0.74 (cited in some sources as the same SVB event, others as a separate intraday liquidity event).
  - **October 2025 flash-crash** affecting multiple stablecoins ($3.8B off-parity briefly across exchanges).
  - That's **2–3 genuine events** at meaningful magnitude across 7.5 years.
- **At the ≥0.5% threshold**: USDC trades on dozens of venues with non-zero spreads. Intra-day deviations of ≥0.5% occur on *thin venues* nearly continuously without representing actual peg-failure. Using a 0.5% threshold conflates microstructure noise (which is not the X risk the instrument should hedge) with genuine depeg events (which is the X risk).
- The S&P Global / depeg-event-counting literature notes that at low thresholds frequency explodes — one cited report counted "609 instances of depeg events in 2023 alone" *across multiple stablecoins*, mostly noise. Counting these as events for EVT estimation is exactly what EVT statisticians warn against: **the Hill estimator is biased when the threshold is below the tail-onset region**.

**Concrete failure mode**: as written, the spec will "PASS" the gate by counting hundreds of ≥0.5% noise observations on minor venues, generate a meaningless Hill-estimator tail β, and proceed to Stage-2 with a fragile identification driven by venue-specific microstructure. This is anti-Reality.

**Verdict on §Pass criteria**: the threshold must be either (a) ≥5% on the *primary* venue (Coinbase or Curve USDC/USDC.e) — at which the count over 2018-09 → 2026-05 is 1–3, mechanically below the EVT-stable floor; or (b) reframed as "count of *distinct depeg episodes* at the daily-close level with magnitude ≥ X%" where X is justified against the Liu et al. 2023 "Anatomy of a Run" event definition. The current 0.5% threshold is the worst of both worlds: too low for genuine events, too restrictive for noise filtering.

---

## 4. EVT tail estimation with rare events — STRUCTURALLY UNSTABLE

**Spec claim** (line 208): "if depeg events are too rare for a daily-panel β estimate, propose alternative — extreme-value-theory tail β rather than mean-regression β."

**Reality**:

- EVT (Pickands–Balkema–de Haan, peaks-over-threshold) typically requires **30–50 exceedances** above the threshold for a stable shape-parameter estimate. Below 20 exceedances the Hill estimator has standard errors that exceed the point estimate. The literature is consistent on this — Embrechts/Klüppelberg/Mikosch (1997) "Modelling Extremal Events", §6.4.
- If the 0.5% threshold is fixed (rebutting §3 above), Hill is fine but the threshold is wrong.
- If the threshold is correctly set at 1–5% (genuine peg failure), the exceedance count is 1–5 over 7.5 years. **EVT is structurally unidentified at N=1–5**.
- The spec's fallback to EVT is therefore not a fallback — it's the same problem in different clothing. With 1–3 genuine events, no method (EVT, mean-regression, jump-conditional) yields stable estimates.

**Verdict on §Method step 4**: the EVT mention is sleight-of-hand that hides the structural identification problem. The honest framing is: **the depeg-X iteration is fundamentally identification-fragile because the tail event distribution is sparse**. This should be a top-line risk in the spec, possibly an automatic FAIL of the gate, not a method-detail bullet.

**Comparison to Direction 3's anti-fishing tripwire** (lines 175–177): Direction 3 honestly flags that re-using the same data inflates garden-of-forking-paths risk. Direction 4 should similarly honestly flag that the depeg-event count is structurally too sparse for β estimation, *regardless* of cohort size — and pre-enumerate a pivot (e.g., to broader stablecoin-stress X, or to a synthetic depeg-stress factor across stablecoins).

---

## 5. Commercial on-chain analytics descope — DUNE PUBLIC DASHBOARDS INSUFFICIENT

**Spec claim** (line 199): "Dune / Allium queries on USDC transfers from Colombian-exchange-tagged addresses … public Dune dashboards may suffice."

**Reality**:

- **Dune labels exchange-deposit addresses by exchange operator** (Bitso, Lemon, Buenbit are taggable at the *exchange* level) but **does not natively label by user-country**. There is no public Dune dashboard mapping Bitso-deposit-addresses → Colombian users vs Argentinian vs Mexican.
- To attribute country, one would need: (a) Bitso's internal customer-country mapping (private, not on Dune); or (b) inference from CEX→DEX outflow patterns combined with localized DEX usage (highly noisy, unvalidated). The Dune "LATAM Crypto 2025 Report" (dune.com/blog/latam-crypto-2025-report) does country-level analysis but uses *aggregated regional flows*, not wallet-level country tags.
- Commercial tools (Arkham, Chainalysis, Nansen Pro) have better entity tagging but still typically do NOT tag retail customer country reliably — even commercial tags max out at exchange-cluster level for most LATAM exchanges.

**Verdict on §Data inputs 4**: the on-chain analytics path as written is not feasible at Dune-public granularity. The mitigation cited (line 228 — "descope if budget bars it") amounts to descoping the entire on-chain Y-observable for this direction. Spec should pre-acknowledge that the on-chain side will collapse to "aggregate Bitso+Lemon Colombian USDC AUM proxied via Fermi estimate × Bitso's published LATAM regional totals", not direct wallet tagging.

---

## 6. Cohort vs sample distinction — CONFLATED IN SPEC

**Spec claim — gating question** (lines 192–193): "Is the Colombian USDC-holder cohort large enough … **AND** has the historical USDC/USDT depeg event volume been sufficient to estimate β with adequate power on a ≥75-day panel?"

**Reality** — the spec gets the logical structure RIGHT here (uses AND, not implication), but the iteration design downstream treats them as if a large cohort implies usable sample. They are independent:

- **Cohort** = population of Colombian USDC-holders. Determines instrument *demand* and policy relevance.
- **Sample for β** = time-series of (Y_t, X_t) pairs where Y is COP-realized cohort holdings and X is USDC/USDT deviation. The N here is determined by *time-series length and event density*, NOT cohort size. A 1-million-wallet cohort with 2 depeg events yields the same β-identification problem as a 1K-wallet cohort with 2 depeg events.
- The Abrigo N_MIN=75 invariant applies to the **sample**, not the cohort. With ~3 genuine depeg events over 7.5 years, no daily panel of any length crosses N_MIN for the event-conditional β.

**The gating-question phrasing is fine. The pass criteria are not** — line 210–213 lists cohort thresholds and event-count thresholds as if both passing implies iteration go. They don't. Even with 1M wallets and 20 noise-events ≥0.5%, the gate should FAIL because no genuine β is identifiable.

**Verdict on §Gating question**: add an explicit pass-criterion clause: "**Both** sample-identifiability **and** cohort-relevance must independently pass. Sample-identifiability requires ≥10 *genuine* depeg episodes (defined as primary-venue daily-close deviation ≥X%) within the analyzable window; absent that, the iteration is GATE-FAIL regardless of cohort size."

---

## 7. 3-day effort estimate — UNDER-SCOPED FOR HONEST GATE

**Spec claim** (line 220): "3 working days: Day 1 Bitso/Lemon/Buenbit … Day 2 Dune queries … Day 3 USDC/USDT depeg inventory + sensitivity."

**Reality**:

- **Day 1 (public-disclosure pulls)**: realistic at 1 day IF the gate explicitly expects to find no Colombia-specific AUM and accepts the Fermi-estimate fallback. If the analyst spends Day 1 hunting for the Colombia-specific number that doesn't exist, it's a wasted day.
- **Day 2 (Dune queries)**: 1 day is realistic only for *exchange-level* aggregate USDC flows (e.g., "how much USDC sits on Bitso hot wallets" — this is tractable). For country-attributed wallet tagging, no public Dune dashboard exists; building one is a 1–2 week effort minimum, well outside the gate scope. Day 2 must be scoped to the exchange-level aggregate plus the Fermi country-share, NOT wallet-tagged country attribution.
- **Day 3 (depeg inventory)**: 1 day is sufficient ONLY if "inventory" means "list 3 genuine events and 600+ noise events at low thresholds, plot the threshold-vs-event-count curve, and declare EVT-unstable". If it means "estimate the Hill tail β with bootstrapped CIs", that's another 1–2 days minimum.

**Honest re-estimate**: **4–5 working days** if the analyst is explicitly told upfront that the AUM disclosure won't exist and the wallet-tagging won't work; **7+ days** if they discover those facts during the gate (more likely).

**Verdict on §Effort estimate**: the 3-day estimate assumes everything works first try. Add 1–2 days for the expected failure-discovery cost, OR pre-pin the failure modes (no country-specific AUM exists; no Dune country tagging exists; ≥0.5% threshold yields noise; etc.) so the analyst goes in calibrated.

---

## Realistic Quality Certification

**Overall gating-step quality rating**: **C+** (acceptable thesis, broken criteria)

- The direction is substantively interesting and the Abrigo edge is real (depeg insurance for LATAM retail does not exist off-chain).
- Three pass-criteria are misspecified and will produce a falsely-PASS gate.
- One major data assumption (Bitso/Lemon/Buenbit Colombia-specific AUM) is unsupported.
- Effort estimate is optimistic by ~50%.
- Anti-fishing pre-pin discipline is weaker here than in Direction 3 (which honestly enumerates the data-reuse fishing risk).

**Gating-step status**: **NEEDS WORK** — three concrete amendments required before dispatch.

---

## Required amendments before dispatch

1. **Amend §Pass criteria (line 213)**: replace "Historical USDC depeg events of magnitude ≥ 0.5%: count ≥ 20" with "Historical USDC depeg episodes at primary-venue daily-close magnitude ≥ X% (X to be pre-pinned with citation to Liu et al. 2023 or similar): count ≥ Y where Y is the EVT-stable floor for the chosen tail estimator (Hill: 20–30; POT-GPD: similar)". Pre-pin both X and Y BEFORE pulling data.

2. **Amend §Data inputs 1–3 (lines 196–198)**: rewrite as "**Expect** Bitso/Lemon/Buenbit to publish only LATAM-aggregate USDC stock figures, NOT Colombia-specific. Pre-commit to Fermi estimate (Colombia-share-of-LATAM-population × LATAM-AUM) as the primary cohort-size method, with the public AUM scan as a *bonus* refinement, not the primary path."

3. **Amend §Effort estimate (line 220)**: revise to 5 working days with the failure modes pre-enumerated, OR keep 3 days with explicit "by-EOD-Day-1, declare AUM-disclosure FAIL and shift to Fermi" tripwire.

4. **Add §Anti-fishing tripwire** (parallel to Direction 3's lines 175–177): "Depeg-event count is structurally sparse (1–3 genuine events over 7.5 years). EVT estimates at low-threshold settings are biased by microstructure noise. If genuine-event count < 10, gate **FAILs** regardless of cohort size. No threshold-shopping post-hoc."

5. **Add §Cohort vs sample explicit separation**: add a clause to §Gating question (line 192) that explicitly states "cohort-size and sample-identifiability are independent gates; both must pass; cohort-pass does not substitute for sample-pass".

---

## Cross-direction context (informing this verdict)

The dev_ai_cost_v2 PAUSED-PENDING-MORE-DATA verdict (`memory/project_dev_ai_cost_v2_verdict.md`) anchored the four-direction exploration on the recognition that the *cost-side Y for subscription-quoted wage-earners structurally suppresses FX-vol β*. Direction 4 is the only one of the four that genuinely escapes this trap (USDC depeg risk for savers is independent of subscription cost structure). That makes Direction 4 the **most thesis-novel** of the four, which raises the bar on getting the gating step right — a falsely-PASS Direction 4 would consume the "one full iteration at a time" slot (line 252) at the expense of Directions 1–3 which have cleaner identification.

The discipline established in Direction 3 (lines 153–158 pre-pin, lines 175–177 anti-fishing tripwire) is the template Direction 4 currently lacks. Direction 4 needs the same level of pre-pinned specificity *before* dispatch.

---

## Re-assessment

**Required after amendments**: yes. Re-review once §Pass criteria, §Data inputs, §Effort estimate, anti-fishing tripwire, and cohort-vs-sample separation are revised.

**Files referenced**:
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-18-four-direction-gating-step-plans.md` (lines 185–233, Direction 4)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/memory/project_dev_ai_cost_v2_verdict.md` (anchoring verdict)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/CLAUDE.md` (anti-fishing invariants, §Anti-fishing invariants section)

**External evidence**:
- Bitso "2025 Latin America Cryptocurrency Landscape Report" — flow %, not stock AUM, not Colombia-specific
- Lemon Cash Proof-of-Reserves — Merkle-tree aggregate, not country-disaggregated; Colombia operation <6 months old at gate time
- USDC depeg literature (S&P Global Sep-2023, Liu et al. 2023, Federal Reserve papers) — 2–3 genuine events, hundreds of low-threshold noise instances
- Dune Analytics public dashboards — exchange-level tagging exists, country-level retail attribution does not
