# Four-Direction Parallel Exploration — Gating-Step Plans

**Date:** 2026-05-18
**Version:** v0.2 (post 8-agent review; see `scratch/2026-05-18-four-direction-gating-review/CONSOLIDATION.md`)
**Status:** AMENDED — see §0 corrections block before reading direction sections
**Anchor:** post-dev_ai_cost_v2 PAUSED-PENDING-MORE-DATA verdict (`memory/project_dev_ai_cost_v2_verdict.md`). The R5 descriptive null (FX-vol share ≈ 0.003%) on Colombian single-developer subscription cost is informative: it tells us the *cost-side / subscription-quoted* Y for a salaried wage-earner suppresses FX-vol β structurally. To preserve the Abrigo (Y, M, X) framework, we explore four parallel candidates, each with a defined **gating-step** that resolves a single feasibility question before any full iteration is dispatched.

**Governance:** these are sub-iteration *scoping* documents. No empirical-validation work happens inside a gating step — only the data-availability / methodology / population-size questions that determine whether the full iteration is worth N≥75 effort. Each gating step is bounded to ≤1 week of effort.

**Anti-fishing carry-forward:** the Abrigo invariants (N_MIN=75, POWER_MIN=0.80, MDES_SD=0.40, pre-pinned sign/lag, HALT-on-spec-vs-data) remain in force for any full iteration spawned from these gates. Gating steps themselves are *exempt* from N_MIN because they are feasibility checks, not β-estimates.

---

## §0 CORRECTIONS BLOCK (v0.1 → v0.2, post-review)

### §0.1 M-DIRECTION CONVENTION (cross-cutting)

**All M-sketches in this document are written from the COHORT'S WALLET perspective** — the wage earner / vendor / saver / holder who would actually deploy the hedge — **not** the protocol-side counterparty. The v0.1 draft conflated these in 3 of 3 M-design subsections (D1, D2, D4); v0.2 corrects them inline and adopts this convention going forward.

### §0.2 UNIFORM PRE-PIN BLOCK (carried forward to every direction)

Every direction below now contains a `### Pre-pin (anti-fishing)` subsection with these 7 mandatory fields:
1. **Sign expectation** (β > 0, β < 0, asymmetric — must be explicit, not "TBD")
2. **Magnitude floor** in SD-units of Y
3. **Lag** (contemporaneous / k=1 / longer; banned beyond k=3 unless theory-justified)
4. **Primary specification** (exactly one; secondaries explicitly labeled as such)
5. **Inference method** (HAC bandwidth, bootstrap method, EVT estimator — fully specified)
6. **Power floor** (default 0.80; demonstration-grade exception requires explicit user approval in a CORRECTIONS block)
7. **HALT chain** on spec-vs-data contradiction per `feedback_pathological_halt_anti_fishing_checkpoint.md`

D3's v0.1 pre-pin had hidden DOF and a silent POWER_MIN relaxation 0.80→0.50 without a CORRECTIONS block — both are anti-fishing violations and have been removed in v0.2.

### §0.3 FACT CORRECTIONS

| Claim in v0.1 | Reality (v0.2 correction) | Source |
|---|---|---|
| D1: DANE GEIH has "foreign employer" identifier | GEIH Migration Module covers immigrants *into* CO, not Colombian remote workers; no public employer-country-of-domicile field exists | DANE GEIH 2024 dictionary check |
| D1: Banrep BoP "computer services" captures wage component | BPM6 line is firm-invoice revenue (services account), not "compensation of employees" (primary income); cannot be cleanly disaggregated to wages | Banrep BoP methodology PDF |
| D1: 5-day effort estimate | ADP CPO pathway 4-12 weeks; DANE custom microdata 4-8 weeks. Split into **G1 (5-day public-only) + G2 (4-12 week ADP+DANE)** | D1-RC web check |
| D2: DIAN monthly imports data is gated | DIAN monthly customs is **public default** since 2001 via tablero COMEX + DANE microdatos catalogs 473/856 | datos.gov.co, DANE microdatos |
| D2: DIAN classifies importers by RUT-size brackets | DIAN classifies by **legal form, not size**. Micro/small classification = separate join via Decreto 957/2019 RUES (Confecámaras) | D2-RC web check |
| D2: Centrifuge has BRL/NGN/IDR/MXN/ZAR trade-finance pools | 2026 active Centrifuge pools are US-Treasury/carbon (Anemoy, JTRSY, JAAA, Flowcarbon). No EM-currency trade-finance pools. Goldfinch V1 borrower pools mostly closed | github centrifuge/tinlake-pools-mainnet |
| D3: Existing panel N ≈ 150 trading days | Actual `notional_cost_panel.parquet` is **N=29 rows / N=28 post-first-diff**. The 150 was TRM days available, not regression observations | `notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md` |
| D3: Bipower variation validly applied at daily frequency | BNS 2004 derives asymptotics for intraday Δ→0; at daily-N=28 the (π/2) bipower is high-variance. Lee-Mykland (2008) is the daily-applicable alternative | BNS 2004 §3; Lee-Mykland 2008 |
| D4: Bitso/Lemon/Buenbit publish Colombia-specific USDC AUM | Bitso has LATAM-aggregate flows only; Lemon Colombia <6mo old; Buenbit no public CO disclosures. Fallback: Fermi-bound only | D4-RC web check |
| D4: ≥20 historical depeg events at ≥0.5% | Only **2-3 genuine depeg episodes** (Mar-2023 SVB, possibly Oct-2025). 0.5% threshold conflates microstructure noise (S&P cited 609 stablecoin "instances" in 2023 alone) | S&P Global stablecoin valuation report |
| D4: Dune public dashboards can tag wallets by country | Exchange entity tagging exists; retail country attribution does not | D4-RC verification |

### §0.4 DIRECTION 3 RE-SCOPE

Direction 3 is **re-scoped from re-analysis-with-notebook to 1-day census-only gate returning FAIL on jump count**. The empirical jump census already run by the D3 Reality Checker is the headline evidence: on the 137-day TRM window of the existing panel, 0 days exceed |3σ|, 2 days exceed |2.5σ|, 6 days exceed |2σ|. Intersected with the N=29 cost-row panel, ~2-4 stress observations remain — well below the direction's own FAIL criterion (jump count < 5). The full notebook implementation is canceled; the gate decision is FAIL by mechanical exhaustion of feasibility.

### §0.5 D1 PHASE SPLIT — REVISED (user 2026-05-18)

Direction 1 is **descoped to G1 only**. The ADP-dependent G2 phase is removed from the gating step entirely. Per user direction 2026-05-18, **all four directions prioritize publicly-accessible-only data** during gating; ADP / DANE-custom / commercial-analytics paths are out of scope unless a gate-PASS justifies escalation in the full iteration.

G1 (5 working days, public sources only):
- DANE GEIH 2023+ public microdata dictionary scan (verify on Day 0 whether *any* employer-country-of-domicile or wage-currency variable exists; if not, downgrade GEIH from primary to noted-absent)
- Banrep Balance of Payments services-exports monthly series (used as macro-aggregate context, NOT as a wage proxy — per §0.3 fact correction)
- Bumeran Colombia, Mercer Colombia, Hays Colombia public salary surveys — USD vs COP wage bands for tech roles, annual frequency
- LinkedIn Talent Insights aggregates / Glassdoor scrapes (last-resort proxy)
- ADP Research Institute (ADPRI) public publications — check whether any Colombia / LATAM USD-payroll aggregate is already published without requiring CPO clearance

The contact-side ADP request is still permitted as a **parallel asynchronous track** (user-managed, not in the 5-day gate budget); any data that returns within the gate window is bonus, not gating.

### §0.6 SEQUENCING (user 2026-05-18)

1. **D2 (micro-vendors) runs serially first** — strongest theoretical Numo-analog support; DIAN/RUES data is genuinely public-default and the gate runs cleanly in 5 days without parallel-attention split.
2. **After D2 completes**: D1-G1 + D4 dispatch as a parallel pair (both are public-data-only, both have independent data sources, no cross-dependency).
3. **D3 closed-FAIL** (§0.4); no further work.

---

## Direction 1 — USD-earning Colombian Remote Workers (ADP bridge)

### Y, M, X candidate
- **Y**: COP-realized monthly wage of a Colombian worker paid in USD by a foreign employer = `usd_wage × spot_COP_USD`. Measured at cohort-aggregate level, not individual level.
- **X**: COP/USD spot level *and* realized volatility (both channels matter — level for one-shot conversion timing, vol for path uncertainty during the pay cycle).
- **M (ideal-scenario sketch, COHORT-WALLET perspective per §0.1)**: **long-COPm / short-USDC** position on the Mento `USDC/COPm` Panoptic pool, sized to expected next-period USD wage. The cohort is already naturally long-USD (wage paid in USD); long-COPm offsets that exposure so a *strengthening* COP doesn't erode COP-converted purchasing power. Optional: covered-call overlay paid out of monthly conversion to fund the protection premium (premium-funded ratchet). v0.1 had this sign inverted (D1-RC S3, D1-CR S1).

### Pre-pin (anti-fishing, per §0.2)
1. **Sign**: β_vol(COP-realized wage on FX vol) < 0 (higher FX vol erodes wage-buying-power via either conversion-timing loss or precautionary saving); β on FX *level* is mechanical identity and BANNED as primary X
2. **Magnitude floor**: |β_vol| ≥ 0.10 SD-units of `Δlog(USD_wage × TRM)`
3. **Lag**: contemporaneous primary; k=1 month secondary; k>3 BANNED
4. **Primary specification**: `Δlog(USD_wage × TRM)_t = α + β_vol · RV_t^FX + γ · cohort_churn_t + ε_t` (cohort_churn controls for survival bias per D1-CR C4)
5. **Inference**: HAC with bandwidth L = ⌊T^(1/3)⌋ (matches dev_ai_cost_v2 convention)
6. **Power floor**: 0.80 (no relaxation; demonstration-grade requires explicit user CORRECTIONS block)
7. **HALT chain**: any spec-vs-data contradiction triggers disposition memo + user-enumerated pivot

### Gating question
**Can the ADP bridge yield an aggregate, de-identified monthly time-series of (a) USD payroll volume to Colombian payees, (b) headcount of the Colombian USD-paid cohort, sufficient to compute a cohort-aggregate COP-realized-wage panel of length ≥75 months?**

### Data inputs (ADP confidentiality-compatible)
1. **Monthly aggregate USD payroll volume** to Colombian payees, 2018-01 → 2026-04 if available, monthly granularity. No PII, no employer identification, no individual records.
2. **Monthly headcount** of Colombian USD-paid workers (de-identified). Permits per-capita normalization.
3. **Percentile distribution** of monthly USD payment size (p10/p25/p50/p75/p90), per month. Needed for tail-sensitivity in M-position sizing.
4. **Industry banding** at SOC top-3 level (software, customer ops, design, finance/accounting). No employer attribution.
5. **Payment frequency mix** (biweekly vs monthly share). Affects M roll cadence.
6. **YoY cohort growth rate** for the policy-relevance narrative.

### Public-proxy parallel track (do not single-source on ADP)
- DANE GEIH 2023+ waves: scan for a "trabaja para empleador extranjero" / "remuneración en divisa" tag. If absent in raw, propose a custom microdata request (DANE handles these for academic users).
- Banrep Balance of Payments services-exports line `servicios informáticos y de información`. Captures aggregate USD inflow at macro level — coarse but free and continuous since 2000.
- Public salary surveys: Bumeran, Mercer Colombia, Hays Colombia. USD vs COP wage bands for tech roles — annual frequency, free.
- LinkedIn Talent Insights / Glassdoor scrapes — last-resort proxy; methodology audit-grade only.

### Method
1. Compose 1-page de-identified data-request memo (the 6 ADP fields above). Run past ADP legal before contact escalation.
2. In parallel, pull DANE GEIH 2023-2024 microdata; identify whether the "foreign employer" identifier exists. If yes, this is a public-data backstop and ADP risk drops to zero.
3. Pull Banrep BoP services-exports monthly series 2018-01 → 2026-03. Cross-check with DANE GEIH headcount estimates to triangulate cohort size.
4. Cost the data-acquisition tree across (ADP-yes, ADP-no) × (DANE-yes, DANE-no) — 4 cells, choose dominant path.

### Pass criteria (gate → full iteration)
- At least one of {ADP aggregates, DANE GEIH foreign-employer subset, Banrep BoP series} yields a monthly panel ≥75 observations of cohort-aggregate USD-payroll volume.
- Estimated cohort size ≥ 10,000 workers (population relevance).
- Cohort growth rate ≥ 5% YoY (policy-relevance).

### Fail criteria (gate → close direction)
- All three data sources fail: ADP legal blocks aggregates AND DANE has no foreign-employer identifier AND Banrep BoP "computer services" line cannot be disaggregated to wage component.
- Cohort size < 1,000 workers.

### Effort estimate
**5 working days**:
- Day 1: draft ADP memo + run past your contact
- Day 2-3: pull DANE GEIH microdata, scan for relevant identifier
- Day 4: Banrep BoP pull + cross-triangulation analysis
- Day 5: 4-cell data-acquisition cost analysis + gate decision write-up

### Risks / known unknowns
- ADP legal turnaround is unbounded. Mitigated by the DANE/Banrep parallel track which has no third-party dependency.
- The ADP cohort may be a non-representative subsample (only those whose foreign employers use ADP) — but for iteration *scoping*, representativeness is a secondary concern.
- DANE GEIH 2018-2022 likely does NOT have a foreign-employer identifier (it's a newer phenomenon). The series may only start ~2022 — borderline for N≥75 monthly.

### Output artifact
`scratch/2026-05-XX-direction-1-gating/gate_decision.md` with the 4-cell decision matrix and the recommended go/no-go.

---

## Direction 2 — Colombian Import Micro-Vendors (USD COGS / COP revenue)

### Y, M, X candidate
- **Y**: monthly unit margin of import-resale micro-vendors selling on Mercado Libre / Tienda Nube. `margin = COP_sale_price - (USD_unit_cost × spot_COP_USD × (1+import_tariff+VAT))`.
- **X**: COP/USD spot level and vol; secondary: bunker/shipping cost index for arrival-timing variance.
- **M (ideal-scenario sketch, COHORT-WALLET perspective per §0.1)**: **one-sided long-call on USDCOP** (equivalently, long-put on COPm/USDC) sized to next-quarter USD COGS commitment. The vendor has one-sided exposure to COP *depreciation* (USD COGS gets more expensive when COP weakens); a two-sided straddle wastes premium on the appreciation tail. v0.1 had this as a straddle (D2-CR Blocker 6). Tokenized-invoice-basket path on Centrifuge **dropped from v0.2** because (a) Centrifuge has no active EM-currency trade-finance pools (§0.3), (b) tokenization requires off-chain custodian + legal wrapper, breaking the permissionless premise (D2-CR S5).

### Pre-pin (anti-fishing, per §0.2)
1. **Sign**: β_FX→margin < 0 for cost-side specification (`Y_cost = USD_imports × spot × (1+τ+VAT)`); higher FX level → higher COP cost → lower margin
2. **Magnitude floor**: |β| ≥ 0.05 SD-units (cohort margins are thin; lower floor than D1)
3. **Lag**: contemporaneous primary; k=1 month secondary (invoice-arrival timing lag); k>3 BANNED
4. **Primary specification**: `Δlog(Y_cost)_t = α + β · Δlog(TRM)_t + γ · Δτ_t + δ · ΔVAT_t + ε_t` with **explicit tariff τ and VAT step-function panel** as controls per D2-CR Blocker 2 (regime changes 2018-2026 are confounders correlated with macro policy → COP/USD)
5. **Inference**: HAC L = ⌊T^(1/3)⌋
6. **Power floor**: 0.80
7. **HALT chain**: spec-vs-data contradiction triggers disposition memo

### Gating question
**Is there a public, monthly-granularity Colombian customs-imports panel that can be disaggregated to a micro-importer cohort (importer-RUT size brackets indicating small-business) for ≥75 months, sufficient to estimate cohort-aggregate USD COGS variance?**

### Data inputs
1. **DIAN customs import declarations** — public quarterly aggregates; monthly granularity may require a data request. Filterable by:
   - HS code (target consumer-electronics, apparel, accessories, home goods — e-commerce import categories)
   - Importer RUT size bracket (DIAN classifies importers; the smallest brackets approximate the micro-cohort)
   - Origin country (CN, US for the dominant Aliexpress / Alibaba flow)
2. **Mercado Libre seller-cohort revenue** — requires API access or data partnership. ML Developer Platform exists but cohort-aggregate data is gated.
3. **Tienda Nube / Shopify Colombia** — same gating, lower priority.
4. **Centrifuge existing-pool data** — Goldfinch BRL / NGN pools as factor-loading anchors. Public via Centrifuge subgraph.
5. **COPm/USDC pool price** — Mento Broker quote history. Free on-chain query.

### Method
1. Pull DIAN public quarterly imports 2018-Q1 → 2026-Q1. Confirm HS-code + RUT-size disaggregation is available at acceptable resolution.
2. File a custom DIAN data request for monthly granularity if quarterly is insufficient. (DIAN has a microdata-request process; 4-6 week SLA.)
3. Query Centrifuge subgraph for BRL/NGN tokenized-credit pool monthly NAVs 2022-2026; build the cross-EM RWA factor.
4. Estimate cohort size via DIAN importer count in target RUT-size buckets.
5. Decide whether the on-chain Y observable requires the tokenization step (Centrifuge pool buildout) or can be approximated by `DIAN_USD_imports × spot_COP_USD` directly.

### Pass criteria
- DIAN public data yields ≥75 monthly or quarterly observations (quarterly N=32 since 2018; monthly N=99 since 2018 if monthly request approved).
- Importer count in target RUT-size brackets ≥ 5,000 (cohort relevance).
- At least 3 Centrifuge factor pools (BRL, NGN, IDR, MXN, ZAR) exist for Bayesian prior construction.

### Fail criteria
- DIAN refuses monthly request AND quarterly N < 32.
- Importer count in target brackets < 500.
- No Centrifuge factor pools exist for EM trade-finance (forces us to build priors from scratch, blocking the small-N pivot).

### Effort estimate
**5 working days** (with a 4-6 week wall-clock if DIAN microdata request is filed):
- Day 1: DIAN public-data pull + structure assessment
- Day 2: Centrifuge subgraph query + factor-pool inventory
- Day 3: Mercado Libre API capability assessment (do we even need the seller-side Y, or is import-side X enough for a one-sided test?)
- Day 4: cohort-size estimation + factor-prior construction sketch
- Day 5: gate decision + microdata request draft (if needed)

### Risks
- DIAN monthly request SLA may be 4-6 weeks → wall-clock outpaces gating effort but does not block other directions running in parallel.
- The DIAN HS-code + RUT-size cross-tab may not be available simultaneously (joint disaggregation is more restrictive than either margin alone).
- Mercado Libre seller-cohort access is a partnership ask, not a public-data ask. Gate decision should NOT depend on ML access being granted.

### Output artifact
`scratch/2026-05-XX-direction-2-gating/gate_decision.md` + DIAN microdata request draft.

---

## Direction 3 — Jump-Conditional Re-Test on Existing dev_ai_cost_v2 Panel

**STATUS: RE-SCOPED TO 1-DAY CENSUS-ONLY GATE — see §0.4. Returns FAIL by mechanical exhaustion of feasibility. Notebook implementation canceled. Sections below kept for historical record only.**

**Headline FAIL evidence (D3-RC empirical jump census, 137-day TRM window):**
- 0 days exceed |3σ|
- 2 days exceed |2.5σ|
- 6 days exceed |2σ|
- Intersected with N=29 cost-row panel: ~2-4 stress observations remain
- Spec's own FAIL criterion (jump count < 5) fires before any analysis

### Y, M, X candidate (HISTORICAL — DO NOT IMPLEMENT)
- **Y**: existing dev_ai_cost_v2 panel — **ACTUAL N=29 rows / N=28 post-first-diff** (corrected per §0.3; v0.1 claim of N≈150 was the count of TRM trading days available, not regression observations).
- **X**: COP/USD daily returns, decomposed via Barndorff-Nielsen / Shephard bipower variation into continuous + jump components.
- **M (ideal-scenario sketch)**: asymmetric long-strangle Panoptic position on USDC/COPm. Pays out only on |FX jump| ≥ threshold. Cheap when FX is calm; insurance framing rather than continuous-factor exposure.

### Gating question
**On the existing dev_ai_cost_v2 daily panel (N≈150 trading days), does β on the jump-component of FX returns differ from zero at 80% power for MDES = 0.40 SD-units, when the integrated-variance component shows β ≈ 0?**

This is a *re-analysis* gate — no new data acquisition required. The cost is methodology development + notebook execution, not data ingestion.

### Data inputs
- Existing `data/panels/notional_cost_panel.parquet` (sha `83dc8410...` — already on master post-d81d60a).
- Existing daily COP/USD TRM series (already in panel).
- No external dependencies.

### Method
1. **Barndorff-Nielsen / Shephard bipower decomposition.** Decompose daily realized variance of COP/USD log-returns into:
   - Integrated variance (continuous component): `IV_t = (π/2) × Σ |r_t| × |r_{t-1}|`
   - Jump variance (discontinuous component): `JV_t = max(0, RV_t - IV_t)` where `RV_t = Σ r²`
   - Reference: Barndorff-Nielsen & Shephard (2004), "Power and Bipower Variation with Stochastic Volatility and Jumps".
2. **Threshold regression with vol-regime switching.** Estimate two β coefficients:
   - `β_calm`: cost ~ FX_return | (rolling_30d_FX_vol < median)
   - `β_stress`: cost ~ FX_return | (rolling_30d_FX_vol ≥ p90)
3. **Asymmetric jump β.** Separate up-jumps (COP depreciation) from down-jumps (COP appreciation). For a wage-earner cohort the exposure is structurally one-sided.
4. **Lag specification audit.** Re-run with N+k lags (k=1, 2, 3 months) — jumps may transmit with delay if the dev defers FX conversion until after a jump.
5. **Power calculation under jump-conditional specification.** N reduces sharply when conditioning on jumps; quantify the power penalty.

### Pre-pin (anti-fishing)
**Pre-pin BEFORE running any regression:**
- **Sign expectation**: β_stress > β_calm > 0 (FX stress transmits more strongly to USD-quoted costs)
- **Magnitude expectation**: β_stress ≥ 0.05 SD-units (cost moves ≥5% of 1 SD per 1 SD of FX jump)
- **Lag**: contemporaneous primary; 1-day lag as secondary
- **Decomposition method**: Barndorff-Nielsen bipower (not Lee-Mykland alternative — pre-pinned to avoid method-shopping)

### Pass criteria
- Jump β estimable with power ≥ 0.50 at the existing N (relaxed from 0.80 because the integrated-variance test already showed 0; this is a *follow-up* test, not the primary).
- |β_jump - β_calm| confidence interval excludes zero at α=0.10 (two-sided).
- Jump count in panel ≥ 10 (minimum for asymptotic OLS validity under standard rules).

### Fail criteria
- Jump count < 5 (mechanically uninformative).
- |β_jump - β_calm| confidence interval contains zero with width > 0.40 SD-units (genuinely uninformative).
- All conditioning specifications give β = 0 (closes the FX-on-cost story for this population entirely).

### Effort estimate
**2 working days**:
- Day 1: bipower decomposition + threshold-regression implementation in a new `07_jump_conditional.ipynb` notebook (follows the v0.2.10 trio + decision-citation discipline)
- Day 2: 2-way review on the notebook + verdict memo

### Risks
- The bipower decomposition is sensitive to microstructure noise at sub-daily frequency. At daily frequency (our data) the method is robust per the Barndorff-Nielsen 2004 paper.
- Threshold-regression at p90 leaves ~15 stress-regime observations on a 150-day panel — borderline for asymptotic inference. Mitigated by reporting confidence intervals via stationary-bootstrap (re-use R5 infrastructure).
- **Anti-fishing tripwire**: this re-test is on the *same data* as the closed v0.2.10 iteration. To avoid garden-of-forking-paths inflation, we must (a) pre-pin specification before running, (b) treat as exploratory/demonstration-grade regardless of outcome unless replicated on a fresh dataset.

### Output artifact
`notebooks/dev_ai_cost_v2/07_jump_conditional.ipynb` + `scratch/2026-05-XX-direction-3-gating/gate_decision.md`.

---

## Direction 4 — USDC-Saver Colombian Cohort (Stablecoin De-Peg X)

### Y, M, X candidate
- **Y**: COP-realized value of a USDC-holder's stablecoin savings position = `usdc_balance × usdc_usd_price × spot_COP_USD`. The novel risk channel is `usdc_usd_price ≠ 1` (depeg).
- **X**: USDC/USDT spot price deviation from 1.0000, daily granularity. Secondary X: USDC/DAI deviation, USDC concentration in Circle reserves.
- **M (ideal-scenario sketch, COHORT-WALLET perspective per §0.1)**: **long-tail OTM put on USDC** (e.g., on the USDC/USDT pool, struck at $0.99 or below). The cohort is *structurally short-tail* by holding USDC; the hedge must therefore **buy** tail protection. v0.1 said "short-tail position" — inverted (D4-CR Blocker 3). Premium funded by native USDC supply yield (Aave/Compound; D4-CR S4 noted this is the cleanest premium-funded-ratchet of all four directions).
- **Y (decomposed per D4-CR Blocker 1)**: `Y_depeg = (usdc_usd_price − 1) × balance × spot_COP_USD` isolates the depeg channel from the FX channel; the v0.1 compound-Y conflated them.

### Gating question (REVISED per D4-RC)
**Can a Fermi-bound estimate of the Colombian USDC-holder cohort yield ≥10K wallets, AND have ≥2 genuine depeg episodes occurred with tail-distance-from-peg sufficient to identify a long-tail option payoff?**

v0.1 used "≥20 depeg events at ≥0.5%" which conflates microstructure noise with genuine events (S&P cited 609 stablecoin instances in 2023 alone; only 2-3 are genuine episodes). The revised criterion uses event-count + tail-distance, not threshold-count.

### Pre-pin (anti-fishing, per §0.2)
1. **Sign**: β > 0 for `Y_depeg = (usdc_price − 1) × balance × spot_COP_USD` regressed on depeg indicator; the long-tail put pays out when usdc_price drops
2. **Magnitude floor**: defined as **tail-distance-from-peg** ≥ 1.0% on at least one historical episode (March 2023: usdc_price hit $0.88 → 12% tail satisfies trivially)
3. **Lag**: contemporaneous (depeg is intraday); k=0 only
4. **Primary specification**: peaks-over-threshold GPD with u = $0.99 (1% below peg); secondary: empirical-CDF tail
5. **Inference**: GPD MLE with profile-likelihood confidence intervals; jackknife on event subset
6. **Power floor**: demonstration-grade only (genuine event N ≤ 5 mechanically rules out 0.80 power); requires explicit user CORRECTIONS block to dispatch as demonstration-grade
7. **HALT chain**: if Fermi-bound estimate fails or genuine-event count < 2, return FAIL without further analysis

### Data inputs
1. **Bitso Colombia public statistics** — Bitso publishes quarterly transparency reports. May include Colombian USDC AUM aggregate.
2. **Lemon Cash transparency disclosures** — Lemon publishes regulatory filings; Colombian USDC holdings may be inferable.
3. **Buenbit Colombia disclosures** — same path.
4. **On-chain Celo/Polygon/Optimism analytics** — Dune / Allium queries on USDC transfers from Colombian-exchange-tagged addresses. Tagging via Arkham / Chainalysis would require commercial access; public Dune dashboards may suffice.
5. **USDC/USDT historical price** — CoinGecko / CoinMarketCap free API. Daily frequency since USDC launch (2018-09).
6. **Major depeg events history** — March 2023 (SVB Circle exposure, USDC briefly at $0.88), other minor events. Documented in academic literature (Liu et al. 2023 "The Anatomy of a Run").

### Method
1. Pull Bitso/Lemon/Buenbit public transparency reports for the last 8 quarters. Extract Colombian USDC aggregate AUM.
2. Cross-check with on-chain analytics: count distinct addresses tagged as Colombian-exchange-deposit + holding USDC. Aggregate balance.
3. Pull USDC/USDT daily price history 2018-09 → 2026-05. Count depeg events of magnitude ≥ 0.5%, ≥ 1%, ≥ 5%.
4. Estimate panel N: if depeg events are too rare for a daily-panel β estimate, propose alternative — extreme-value-theory tail β rather than mean-regression β.
5. Compose cohort-size-vs-N sensitivity table.

### Pass criteria
- Combined Bitso + Lemon + Buenbit Colombian USDC AUM ≥ $5M.
- Estimated distinct Colombian USDC-holder addresses ≥ 10,000.
- Historical USDC depeg events of magnitude ≥ 0.5%: count ≥ 20 (sufficient for EVT tail estimation).

### Fail criteria
- Cohort AUM < $1M (immaterial, no policy story).
- Distinct addresses < 1,000 (no permissionless-hedge demand base).
- Depeg events with magnitude ≥ 0.5%: count < 5 (no estimable tail).

### Effort estimate
**3 working days**:
- Day 1: pull Bitso/Lemon/Buenbit public reports + extract Colombian USDC figures
- Day 2: on-chain analytics — Dune queries or commercial-API scope (Arkham access is paid; descope if budget bars it)
- Day 3: USDC/USDT depeg event inventory + cohort-size-vs-N sensitivity write-up

### Risks
- Exchange public reports may not disaggregate USDC AUM by country. Mitigated by using total LATAM USDC AUM × Colombia-share-of-LATAM-users (rough but defensible).
- Commercial on-chain analytics (Arkham, Chainalysis) cost ~$1-10K/month. Gate decision should NOT depend on commercial access; Dune public dashboards must suffice or the on-chain proxy is descoped.
- USDC depeg events are concentrated (March 2023 dominates). The β estimate may be effectively driven by a single event — fragile identification.

### Output artifact
`scratch/2026-05-XX-direction-4-gating/gate_decision.md` + cohort-size-vs-N sensitivity table.

---

## Cross-direction governance

### Sequencing
All four gating steps run **in parallel**. They have no inter-dependencies (different data sources, different methods). Total wall-clock to complete all four: ~5-7 working days assuming no external SLA blockers.

### Decision matrix at gate-completion
After all four gates resolve, populate a 4-row decision table:

| Direction | Gate result | Estimated cohort N | Estimated panel N | Recommended next step |
|---|---|---|---|---|
| 1 — USD-paid remote workers | PASS/FAIL/CONDITIONAL | ___ | ___ | Spec v0.1 / close / retry-with-public-proxy |
| 2 — Import micro-vendors | PASS/FAIL/CONDITIONAL | ___ | ___ | Spec v0.1 / close / file DIAN microdata request |
| 3 — Jump-conditional re-test | PASS/FAIL/CONDITIONAL | (existing) | ~150 days | Implement 07_jump_conditional.ipynb / close |
| 4 — USDC-saver cohort | PASS/FAIL/CONDITIONAL | ___ | ___ | Spec v0.1 / close / scope commercial analytics |

### Resource allocation principle
At most **one full iteration** will be dispatched at a time post-gating. The other three PASS results enter a queue ordered by:
1. Estimated Abrigo-edge score (does Panoptic give us an edge competitors don't have?)
2. Cohort size × YoY growth (policy relevance)
3. Estimated time-to-first-β

### Anti-fishing carry-forward
- Pre-pin sign / lag / magnitude expectations BEFORE running any gate-step regression (Direction 3 in particular).
- Threshold tuning post-hoc is silent-fishing and triggers HALT + disposition memo per `feedback_pathological_halt_anti_fishing_checkpoint.md`.
- Per-direction `gate_decision.md` is the canonical record. Reverting/amending a gate decision requires a CORRECTIONS block, not a silent rewrite.

### Review protocol
Each direction is reviewed independently by:
- **Reality Checker** — gating logic, data feasibility, pass/fail-criteria realism, "is this actually doable in 5 days"
- **Code Reviewer** — methodology coherence, identification of statistical / econometric / on-chain-data risks, pre-pin sufficiency

Reviews land in `scratch/2026-05-18-four-direction-gating-review/{direction-N}/{rc,cr}.md`.
