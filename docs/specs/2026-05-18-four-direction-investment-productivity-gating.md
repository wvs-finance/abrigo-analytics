# Four-Direction Investment-Productivity Parallel Exploration — Gating-Step Plans

**Date:** 2026-05-18
**Version:** v0.3 (post RefiColombia deep-research + user dTAO+Maymin reference 2026-05-18; E5 anchored to RefiColombia COPm sub-cohort; NEW E8 = Bittensor dTAO × Maymin (2026) — reopens dev_ai_cost_v2 "FX × Cost of AI" from operator-revenue side; E3+E8 share Maymin methodology under joint methods-paper)
**Sibling spec:** `2026-05-18-four-direction-gating-step-plans.md` v0.3 (first round: D1/D2/D3/D4)
**Framework anchor:** `CLAUDE.md` post-2026-05-18 broadening + `memory/project_abrigo_framing_clarification_investment_productivity.md`
**Theoretical anchor:** `memory/reference_bhaduri_laski_riese_concept_bridge.md` (BLR/Minsky/Kaleckian)

## §0 Standing rules carried forward

### §0.1 Investment-productivity framing (PRIMARY per CLAUDE.md 2026-05-18 broadening)
Goal = make actual investment productive via on-chain CFMM convex hedges against PK-identified micro-risks. Cohorts are *investor classes* exposed to hedgeable micro-risk on their productive-investment path. Each direction below targets one such class.

### §0.2 M-direction convention (carried from first-round §0.1)
All M-sketches written from **cohort wallet perspective** — the investor who would deploy the hedge — NOT protocol counterparty.

### §0.3 Uniform 7-field pre-pin (carried from first-round §0.2)
Every direction below contains:
1. Sign expectation
2. Magnitude floor in SD-units of Δlog Y
3. Lag (contemporaneous / k=0-1; k>3 BANNED)
4. Primary specification (exactly one)
5. Inference method
6. Power floor (0.80 default; demonstration-grade requires explicit CORRECTIONS block)
7. HALT chain on spec-vs-data contradiction

### §0.4 Anti-fishing invariants (NON-NEGOTIABLE)
N_MIN = 75, POWER_MIN = 0.80, MDES_SD = 0.40. Pre-pin BEFORE data; post-hoc threshold tuning banned; HALT-disposition is honest outcome.

### §0.5 Transparency condition carry-forward
Per `memory/feedback_d1_transparency_continuation.md` — every iteration step discloses data needs / actual quality / non-retirement possibility. NON-RETIREMENT is acceptable interim outcome.

### §0.6 Stage discipline
Per CLAUDE.md: β-existence (Stage 1) → ideal M-sketch (Stage 2) → deployment (Stage 3). Stage drift banned. M-sketch in every direction is descriptive-only within the gating step.

### §0.7 Sequencing (parallel)
All 4 directions gated in parallel after meta-spec passes 2-way review. No serial dependency between E5/E6/E3/E4.

### §0.8 USER CONSTRAINTS (locked 2026-05-18, post-review)

Three binding constraints from user clarification 2026-05-18:

1. **EVM-only / Solidity-only / Ethereum-ecosystem focus**. Non-EVM chains (Solana, Cosmos, NEAR, Bitcoin-native, Polkadot, Aptos, Sui) are OUT OF SCOPE. Bridges to EVM are acceptable; native non-EVM is not.
2. **Underserved-population focus**. Cohorts targeting Colombia or other non-US emerging-market populations are preferred. US-resident institutional cohorts (and the RWAs primarily serving them) are deprioritized.
3. **ReFi + impact tokens + real-world assets** must be explicitly evaluated as candidate iteration spaces.

These constraints superseded the original E1/E2 framing during the v0.2 autofix.

### §0.9 CORRECTIONS-D (autofix-all 2026-05-18 post 8-agent review + §0.8 constraints)

**E1 DePIN — CLOSED-OUT under EVM constraint (§0.8.1)**. Helium/MOBILE migrated to Solana 2023; HNT/AKT (Cosmos)/IO.net (Solana)/Hivemapper (Solana) all non-EVM. EVM-only DePIN subset (Render Polygon, DIMO Polygon, WeatherXM, Filecoin-via-FVM) is too small and heterogeneous to sustain framework. Reviewer findings (RC C2/C4/C5/C6; CR C1-C6) all moot under closure.

**E2 RWA holders — CLOSED-OUT under permissionless + PK-inversion**. Both reviewers converged: all 8 named vehicles require off-chain custodian + KYC/AC/QP (binding kill on permissionless premise per CLAUDE.md); active 2026 pools dominated by tokenized US-Treasury which is P_k-side numéraire per BLR (NOT P_i productive investment). Cohort class (institutional/accredited) misaligned with §0.8.2 underserved-population focus.

**E3 CL LP providers — DEMOTED to methods-paper-only track, OUT of β-gating sequence**. Both reviewers (RC: "REFRAME, DO NOT DISPATCH AS β-ITERATION"; CR: 6 blockers including Panoptic mainnet 2024-07 postdates all named events). E3 preserved as standalone methods-paper deliverable per `reference_bhaduri_laski_riese_concept_bridge.md` Cambridge JE / ROPE / Metroeconomica target. Multi-year timeline; not in this gating round.

**E4 PG builders — RETAINED with amendments per reviews**. 6 CR blockers + 8 RC findings folded inline (see §Direction E4 amendments below).

**E5 NEW — ReFi carbon-credit ecosystem × methodology-revision / price-collapse shock**. Replaces E1 slot. Polygon-native EVM ✓; permissionless ✓; Kaleckian-pure (real carbon-sequestration projects = real-economy investment) ✓; LATAM-heavy underserved-population project exposure ✓.

**E6 NEW — LATAM-specific tokenized SME / impact bonds × cohort-cashflow disruption**. Replaces E2 slot. Narrower than original E2; directly targets §0.8.2 underserved-population focus.

**E7 PINNED — Mento minter / monetary-sovereignty cohort**. Conceptually pure under endogenous-money / monetary-sovereignty lens; smaller cohort; pinned for follow-up round, not gated this round.

### §0.10 v0.3 ANCHOR ADDITIONS (2026-05-18 post-RefiColombia + dTAO research)

**E5 anchored to RefiColombia COPm subsidies sub-cohort**. Deep-research found verified live contract `0x947C6dB1569edc9fd37B017B791cA0F008AB4946` (Solidity 0.8.28 verified Celoscan; Celo Mainnet; 163 days history; 596 tx; live subgraph `102458/refi-medellin-ubi`; 77 active beneficiaries just-passes N_MIN=75; ~17.24M COPm distributed across Comuna 13 Medellín (Platohedro) + Caribbean coast (Rosiris cluster) + Saravena/Arauca (Waira cluster)). Reuses Pair D's confirmed positive-β COP/USD anchor. Pre-pin sketch in §E5-revised below.

**NEW E8 — Bittensor dTAO × Maymin (2026) closed-form AMM option pricing**. User-proposed 2026-05-18 reference pair: dTAO whitepaper (subnet alpha-tokens with bonding-curve price discovery against TAO) + Maymin (2026) arXiv:2603.29763 CEV-process closed-form option pricing on AMM tokens. Reopens dev_ai_cost_v2 "FX × Cost of AI" question from the operator-revenue side: subnet operators earn TAO + alpha, COP/local-currency exposure on conversion. **Critical 1-day feasibility scoping (E8.0)** gates everything — wTAO/Subtensor-EVM liquidity check + LATAM operator cohort identifiability. Pre-pin sketch in §E8 below.

**E3 + E8 share Maymin (2026) as methodology primitive**. Joint methods-paper umbrella: closed-form pricing of CFMM-instantiated two-price gaps with two empirical applications — E3 (Uniswap V3 stablecoin+volatile LP-IL hedge) + E8 (Bittensor TAO/alpha pool subnet-revenue hedge). Stronger Cambridge JE / ROPE / Metroeconomica proposition than E3 alone.

---

## Direction E5-revised — RefiColombia COPm Subsidies Sub-cohort × COP/USD-vol & COPm-peg risk

### Cohort
77 active beneficiaries on `SubsidyProgram` contract `0x947C6dB1569edc9fd37B017B791cA0F008AB4946` on Celo Mainnet. Geographic clusters: Comuna 13 Medellín (Platohedro 19/77), Caribbean coast (Rosiris cluster 19/77), Saravena/Arauca conflict zone (Waira cluster 10/77). 163 days of timestamped claim history; subgraph public + free.

### Pre-pin (anti-fishing locked per §0.3)

| Field | Value |
|---|---|
| Y | Cohort-aggregate COPm-denominated claim flow × COP/USD spot for COP-realized purchasing-power = `Σ claim_ops_t × 10,000 × spot_COP_USD_t`; secondary: per-beneficiary log-claim-rate |
| X | COP/USD daily lag-1 returns (Pair D anchor — confirmed positive β=+0.137, p≈1.5e-08); secondary: COPm peg deviation vs cUSD on Mento broker |
| Sign | β > 0 (FX vol → claim-flow USD-realized vol; preserves Pair D direction) |
| Magnitude floor | β ≥ 0.40 SD-units of Δlog Y (CLAUDE.md MDES_SD invariant) |
| Lag | Contemporaneous primary; k=1 month secondary |
| Primary spec | `Δlog(USD_value_t) = α + β·Δlog(spot_COP_USD_t) + γ·peg_dev_t + ε_t`, daily/weekly/monthly arms |
| Inference | HAC L=⌊T^(1/3)⌋; wild-cluster bootstrap on responsable-clusters |
| Power | Demonstration-grade (N=77 borderline); CORRECTIONS-E required if cohort grows below 75 |
| HALT | If active cohort drops below 50 OR if PII API exposure causes program shutdown, NON-RETIREMENT |

### Pass criteria
- N_MIN: 77 active ≥ 75 ✓ (borderline; widen to ever-registered N=85 with state covariate if needed)
- ≥6 months of subgraph history available ✓ (163 days)
- Pair D anchor reusable ✓
- LATAM/Colombia focus per §0.8.2 ✓ (Comuna 13 + Caribbean coast + Arauca underserved cohorts)

### M-sketch (descriptive-only Stage-2)
- COPm/cUSD Panoptic straddle, premium-funded out of 10,000-COPm claim flow
- Caveat: $2.40/claim too small to fund real Panoptic premium today; ideal-scenario only

### OpSec note (NOT a pre-pin field; flagged to user for separate action)
`api.subsidios.reficolombia.org/api/beneficiaries` exposes unauthenticated PII (name + phone + responsable) for 72 registered users. Should be reported to RefiMedellín team.

### Sub-tasks
- E5.1: Pull SubsidyProgram subgraph history → daily claim panel
- E5.2: COPm peg-deviation panel via Mento broker swap events
- E5.3: COP/USD TRM daily panel (reuse existing `fetch_banrep.py`)
- E5.4: Cohort cluster decomposition (Platohedro / Rosiris / Waira / dev clusters)
- E5.5: Verify owner type (multisig vs EOA) for governance-risk severity

---

## Direction E8 — Bittensor dTAO × Maymin AMM Option Pricing (FX × Cost of AI v2)

### Status
**FEASIBILITY-GATED on E8.0 (1-day precondition)**. If wTAO + bridged alpha tokens are not liquid on EVM OR Subtensor EVM execution layer is not live in production OR LATAM subnet-operator cohort is not identifiable, E8 collapses early. Pre-pin sketch retained below; do not dispatch E8.1+ until E8.0 PASSES.

### Cohort (target)
LATAM (especially Colombian) Bittensor subnet operators + validators with EVM-side TAO/alpha exposure. Cohort identification via:
- TAO bridge contract (Tao Bridge, stTAO, or similar wrappers on Ethereum)
- Subtensor EVM execution layer (if live in production)
- Subnet-operator wallets observable via Bittensor public chain explorer + EVM-bridge transfer logs
- LATAM attribution: Discord / forum / GitHub geolocation heuristics

### Pre-pin (anti-fishing locked per §0.3)

| Field | Value |
|---|---|
| Y | Operator USD-equivalent earnings = `alpha_t × alpha_TAO_price_t × TAO_USD_t × COP/USD_t` (or country-specific FX); per-operator monthly panel |
| X | Composite: (i) subnet emission-rate changes; (ii) alpha/TAO AMM-pool divergence (Maymin's two-price gap); (iii) COP/USD spot vol (Pair D anchor) |
| Sign | β > 0 (any shock reduces operator USD-realized earnings) |
| Magnitude floor | β ≥ 0.40 SD-units of Δlog(operator USD earnings) |
| Lag | Contemporaneous primary; k=1 month secondary for cohort-attrition |
| Primary spec | `Δlog(operator_USD_t) = α + β₁·Δlog(emission_index_t) + β₂·Δlog(alpha_pool_gap_t) + β₃·Δlog(spot_COP_USD_t) + ε_t` |
| Inference | HAC + cluster-robust by subnet |
| Methodology primitive | Maymin (2026) CEV closed-form for alpha/TAO AMM-pool option pricing — **this IS the methods-paper contribution shared with E3** |
| Power | 0.80 if E8.0 confirms EVM-side cohort identifiability + N≥60 monthly observations achievable post-dTAO launch |
| HALT | E8.0 FAIL → NON-RETIREMENT close; if EVM wrappers don't exist or are not liquid, redirect to methods-paper-only path |

### E8.0 feasibility-scoping (CRITICAL PRECONDITION, 1 day)

1. **wTAO EVM liquidity check**: Tao Bridge / stTAO / wTAO live on Ethereum / Base / Arbitrum? Daily volume? Uniswap V3 pool depth?
2. **Subtensor EVM status**: Bittensor's EVM execution layer (Subtensor EVM) live in production 2026? Or still testnet?
3. **Alpha-token EVM availability**: Any subnet alpha tokens bridged to EVM? Which subnets?
4. **LATAM operator cohort identifiability**: Bittensor forum / Discord / GitHub geolocation for LATAM operators. Sample size estimate.
5. **Maymin CEV empirical-fit feasibility**: Public alpha/TAO bonding-curve history sufficient for CEV parameter estimation?

### M-sketch (descriptive-only Stage-2)
- Perpetual put on alpha/TAO (or wTAO/USDC) Panoptic-equivalent pool, priced via Maymin CEV closed-form
- Premium funded by operator's TAO-emission stream
- HALT trigger: alpha/TAO pool depth < threshold or Subtensor EVM downtime

### Sub-tasks (post-E8.0 PASS only)
- E8.1: TAO/alpha price + emission-rate panel from Bittensor chain explorer
- E8.2: EVM-side wTAO / alpha-bridge volume panel
- E8.3: LATAM operator cohort identification + revenue panel
- E8.4: Maymin CEV closed-form empirical fit on alpha/TAO pool
- E8.5: Joint methods-paper draft with E3 (CL LP empirical) + E8 (subnet-revenue empirical)

---

---

## Direction E5 — ReFi Carbon-Credit Ecosystem × Methodology-Revision / Price-Collapse Shock

### Y, M, X candidate

- **Cohort**: Holders of ReFi carbon-credit tokens + on-chain carbon-project developers. Concrete sub-cohorts:
  - **Toucan Protocol** (Polygon): BCT (Base Carbon Tonne) + NCT (Nature Carbon Tonne) pool tokens; retirement contracts; project-bridged TCO2 tokens
  - **Klima DAO** (Polygon): KLIMA token + treasury holdings; ~$15M+ treasury 2024
  - **Solid World DAO** (Polygon): pre-issuance / forward-credit tokenization
  - **MOSS Earth** (Ethereum): MCO2 tokens backed by Amazon Brazil REDD+ projects
  - **JustCarbon** (Ethereum): JCR token
  - **C3 Carbon Credit Coin** (Polygon): C3 token
  - **Senken** (Polygon): retirement marketplace

- **Y**: Cohort-aggregate ReFi-token USD value trajectory + retirement-rate panel. Per-token: `log(token_USD_t × circulating_supply_t)` (Y₁ = market cap); secondary `log(monthly_retirements_t)` (Y₂ = real-economy demand signal).
- **X**: 
  - Carbon-methodology shocks (Verra REDD+ methodology revision Jan-2024; Climate Action Reserve revisions; ICVCM Core Carbon Principles release)
  - Voluntary-carbon-market price collapse 2023-2024 (~80% drawdown per CarbonPulse / Bloomberg)
  - EU CBAM regime activation 2026-Q1
- **M (cohort-wallet, descriptive-only — Stage-2 only)**: long-tail OTM put on BCT/USDC or KLIMA/USDC Polygon Uniswap V3 pool; project developer hedges revenue-receipt token against collapse
- **PK anchor**: pure Kaleckian real-economy investment by construction. Carbon projects deploy capital in real reforestation / renewable energy / soil sequestration → produce verified emission-reduction tonnes (real output). BLR P_i side: physical project investment. P_k side: voluntary-market price speculation. **The 2023-2024 voluntary market collapse is a textbook BLR "virtual collapse while real economy continues" event** — projects continued to produce reductions, but token prices collapsed 80% on methodology-revision news.

### Pre-pin (anti-fishing locked per §0.3)

| Field | Value |
|---|---|
| Sign | β > 0 (methodology-revision indicator → token-price drop; primary spec) |
| Magnitude floor | β ≥ 0.40 SD-units of Δlog(token market cap) per CLAUDE.md MDES_SD=0.40 invariant |
| Lag | Contemporaneous primary (news-event); k=1 month secondary for retirement-rate response |
| Primary spec | `Δlog(market_cap_t) = α + β·methodology_shock_indicator_t + γ·Δlog(broader_carbon_index_t) + ε_t`, monthly, HAC L=⌊T^(1/3)⌋ |
| Inference | HAC + cluster-robust by token; wild-cluster bootstrap if G<6 (per E1 RC S5/S7) |
| Power | 0.80 |
| HALT | Methodology-shock events <3 in panel window → demonstration-grade fallback with explicit CORRECTIONS block; <2 events → NON-RETIREMENT |

### Pass criteria
- ≥4 of 7 named protocols yield N≥36 monthly observations of market cap
- ≥3 methodology-revision / price-collapse events identifiable cleanly (Verra REDD+ Jan-2024; voluntary-market 2023 collapse onset; ICVCM activation; CBAM regime activation)
- β CI excludes zero at α=0.05 in primary spec
- Aggregate cohort token-supply ≥ 1M tCO2e in active circulation
- LATAM-project share of underlying carbon credits ≥ 30% (per §0.8.2 underserved-population focus)

### Fail criteria
- <2 protocols with clean panel
- <2 identifiable shock events
- LATAM-project share <10% (would mean cohort is mostly Global North projects; violates §0.8.2)

### Sub-tasks
- E5.1: ReFi protocol inventory + smart-contract address list (Toucan/Klima/Solid World/MOSS/JustCarbon/C3/Senken)
- E5.2: Methodology-shock event panel (Verra revisions + ICVCM + CBAM dates + voluntary-market collapse onset)
- E5.3: Underlying-project geography panel — LATAM share verification per project (Amazon REDD+ projects, Colombian REDD+, Peruvian conservation)
- E5.4: Token-price + retirement-rate panel construction (CryptoCompare + protocol subgraphs)
- E5.5: Panoptic / Uniswap V3 pool inventory for ReFi tokens (Polygon mainnet)

---

## Direction E6 — LATAM-Specific Tokenized SME / Impact Bonds × Cohort-Cashflow Disruption

### Y, M, X candidate (FEASIBILITY-SCOPING SUB-DIRECTION)

**Status notice**: E6 is structurally a feasibility-scoping direction. 2026 inventory of LATAM-specific tokenized SME debt / impact bonds is likely thin post-Goldfinch-V1-sunset. Gate decision may close-FAIL on cohort-inventory-empty before β-estimation runs. Treat as such; do not over-invest in pre-pin until E6.1 feasibility lands.

- **Cohort**: Holders of LATAM-specific tokenized real-world cashflow positions targeting underserved populations:
  - **Goldfinch V1 historical** (BRL/NGN pools, mostly sunset) — comparator only
  - **DLC.Link** Bitcoin-backed loans for Global South (Stacks/Ethereum bridge)
  - **Mountain Protocol** (USDM, ROC-regulated, LATAM-friendly) — stable side
  - **Re Protocol** (impact-debt on Polygon)
  - **Plume Network**'s LATAM-specific pools if any exist
  - **Allianzia / DefiInvest / Centrifuge LATAM subset** — to verify
  - **Mercado Bitcoin tokenized debt** (Brazil-native) — to verify EVM availability
- **Y**: NAV / retirement-rate per pool; per-pool aggregated
- **X**: Underlying-cashflow disruption events (LATAM SME default cycles; sovereign credit-spread events; FX shocks affecting USD-denominated impact bonds)
- **M (descriptive-only)**: long-tail OTM put on LATAM-RWA-token / USDC; very speculative given current liquidity
- **PK anchor**: directly serves §0.8.2 underserved-population focus; BLR P_i side (tokenized real-economy cashflow specifically from Global South / LATAM)

### Pre-pin (anti-fishing locked per §0.3)

| Field | Value |
|---|---|
| Sign | β < 0 (cashflow disruption → NAV decline) |
| Magnitude floor | β ≥ 0.40 SD-units (carries forward CLAUDE.md MDES_SD invariant; no relaxation without explicit CORRECTIONS) |
| Lag | Contemporaneous primary; k=1-3 month secondary for write-down realization |
| Primary spec | Event-study on disruption-window NAV deviation; pooled across LATAM pools |
| Inference | Per-event jackknife if event count is low; otherwise HAC |
| Power | Demonstration-grade default given expected small N; require explicit CORRECTIONS block to proceed if N<75 monthly per pool |
| HALT | If E6.1 feasibility-scoping finds <3 active LATAM-specific tokenized SME / impact-bond instruments on EVM in 2026, NON-RETIREMENT close with disposition memo |

### Pass criteria
- ≥3 active LATAM-specific tokenized SME / impact-bond instruments on EVM identified in 2026
- Aggregate TVL ≥ $20M
- ≥2 identifiable cashflow-disruption events in panel window
- Permissionless transfer + secondary-market liquidity verified for ≥2 instruments

### Fail criteria
- <3 active LATAM-specific EVM instruments → NON-RETIREMENT
- All identified instruments require off-chain custodian + KYC gating
- Aggregate TVL <$2M

### Sub-tasks
- E6.1: 1-day Fermi feasibility scoping — inventory of LATAM-specific tokenized SME / impact bonds on EVM in 2026. **Run this BEFORE all other sub-tasks** — gates the rest of E6
- E6.2: Permissionless / KYC-gating audit per instrument (if E6.1 finds anything)
- E6.3: Underlying-cashflow disruption-event panel
- E6.4: Panoptic / Uniswap V3 tradability for any qualifying instruments

---

## Direction E3 — DEMOTED to methods-paper-only track

**Status**: removed from β-gating sequence per CORRECTIONS-D §0.9. Both reviewers converged on this in v0.1 review (RC: "REFRAME, DO NOT DISPATCH AS β-ITERATION"; CR: "Panoptic mainnet 2024-07 postdates all named events"). The Direction-E3 content in v0.1 sections is preserved as historical context only; do NOT dispatch E3 sub-tasks under this meta-spec.

**Next step for E3**: separate standalone methods-paper spec on its own multi-year track. Target venues: Cambridge JE / ROPE / Metroeconomica. Pin Path A (Maymin 2026 CEV + V3 IL piecewise closed form, theoretical) + Path B (substitute-venue empirical fit on Hegic / Opyn / Squeeth / Premia for events predating Panoptic).

---

## Direction E4 — Amendments per reviews (CORRECTIONS-D continued)

E4 spec content in v0.1 retained, with the following pre-pin amendments folded:

### E4 amendments (autofix per CR 6 blockers + RC 8 findings)

1. **CR-B1 / RC-F7 — Y decomposition**: Replace `Δlog(builder_runway_t)` with **decomposed primary `Δlog(wallet_balance_t)` + secondary `Δlog(burn_rate_t)`**. Burn-rate = trailing-90-day rolling-sum outflows at end-of-month UTC snapshot. **NEW HALT**: if burn-rate observable for <50% of cohort wallets, demonstration-grade fallback or NON-RETIREMENT.

2. **CR-B2 — Multicollinearity**: orthogonalize `Δlog(program_size_t)` on `Δlog(grant_token_USD_t)`; pre-pin VIF threshold 5.0; report orthogonalized β.

3. **CR-B3 — Wallet aggregation**: pre-commit to individual-wallet panel with program FE + cluster-robust by program; inclusion rule ≥ $5,000 USD-equivalent received during panel window.

4. **CR-B4 / RC-F4 — Cut-event heterogeneity**: pre-classify shocks into 3 types (RetroPGF round revisions / STIP-bridge sunset / Gitcoin Stack wind-down); run per-type β; **ban pooling**; PASS criterion revised to ≥2 events *within the same shock type*.

5. **CR-B5 / RC-F1 — Karma GAP coverage**: 1000-milestone PASS criterion binds only on secondary milestone-rate spec, not primary balance-trajectory spec; primary spec requires only N=24 monthly observations of cohort-wallet aggregates. **Pre-data verification**: GAP attestation time-series must be confirmed empirically before E4.1 dispatch.

6. **CR-B6 — HALT trigger**: "Redirect to single-program case study" REMOVED (anti-fishing-banned). Replace with **NON-RETIREMENT gate-FAIL + disposition memo** if <2 programs yield clean panel.

7. **CR-S2 — Small-cluster SE**: pre-pin wild cluster bootstrap (Cameron-Gelbach-Miller; Webb weights; B=999) as primary inference when G<10.

8. **CR-S3 / RC-F8 — Conversion-rate gating precondition (CRITICAL)**: E4 dispatch is **GATED ON A 1-DAY MEASUREMENT TASK** — what fraction of OP/ARB/ETH grant-token receipts convert to USDC within 7 days? If conversion is immediate for >50% of cohort, there's no exposure to hedge; E4 closes-FAIL. **This precondition runs first; nothing else in E4 dispatches until it lands.**

9. **RC-F6 — Cross-program overlap**: E4.5 (overlap analysis) runs BEFORE E4.1-E4.4. Identification depends on overlap structure.

### E4 sub-task order revised
1. **E4.0 NEW (CRITICAL PRECONDITION)**: conversion-rate measurement (1-day; OP/ARB/ETH grant-receipt → USDC conversion within 7 days)
2. E4.5 cross-program overlap analysis (was last; moved to second)
3. E4.1 Karma GAP attestation pull
4. E4.2 Grant-program cut-event panel (per-shock-type classified)
5. E4.3 Builder wallet identification at individual level (≥$5K inclusion)
6. E4.4 Q/acc cohort comparison only
7. E4.6 NEW: Panoptic OP/USDC + ARB/USDC pool tradability verification

---

## Revised sequencing (post-CORRECTIONS-D)

1. **Meta-spec v0.2 (this draft) → 4-agent 2-way review** (E5 RC+CR + E6 RC+CR only; E3/E4 amendments already user-approved per autofix-all directive)
2. **E5 + E6 gating execution** in parallel after review approval
3. **E4 conversion-rate precondition (E4.0)** runs as Day-1 task in parallel with E5/E6 dispatch
4. **E4 full gating** only proceeds if E4.0 PASSES (≥50% builders hold grant-token >7 days)
5. **E3 methods-paper spec** drafted on separate track, no dependency on this gating round
6. **E7 Mento minter** pinned for follow-up gating round

## Cross-direction structural opportunities (revised)

### E5 + E4 share Kaleckian builder-cohort framing
Both target real-economy producers (carbon-project developers / open-source builders) with on-chain attestation of real output. Y_real / Y_virtual headline at maximum generality.

### E5 is the strongest fit to §0.8 user constraints
EVM-native (Polygon ✓), permissionless ✓, Kaleckian-pure real-economy investment ✓, LATAM-heavy underserved-population project exposure ✓.

### E6 directly serves §0.8.2 underserved-population focus
But conditional on 2026 inventory of LATAM-specific instruments. Day-1 Fermi scoping (E6.1) decides everything.

### E3 methods-paper remains the conceptual headline
The Minsky P_k/P_i ↔ AMM micro-structure gap is the unique academic contribution Abrigo can claim — regardless of any iteration's β verdict.

---

## Direction E1 — DePIN Operators × Emission/Reward-Regime Shock

### Y, M, X candidate

- **Cohort**: Operators of decentralized physical infrastructure networks — capital-deployed hardware producing services. Concrete sub-cohorts:
  - **Helium** hotspot operators (1M+ active hotspots; LoRaWAN/5G coverage; HNT/MOBILE rewards)
  - **Filecoin** storage providers (5K+ active SPs; FIL block rewards + storage-deal payments)
  - **Akash Network** compute providers (AKT rewards + USDC compute revenue)
  - **IO.net** GPU operators (IO rewards)
  - **Hivemapper** drivers (HONEY mapping rewards)
  - **Pollen Mobile** operators
  
- **Y**: Operator USD-equivalent revenue trajectory = `tokens_earned_t × spot_token_USD_t × cohort_size_t` for each DePIN
- **X**: Emission-schedule shock (programmatic cliff per token-economics design) OR token-price collapse OR demand-side substitution by traditional infrastructure
- **M (cohort-wallet, descriptive-only)**: long-tail OTM put on DePIN-token / USDC pool — operator hedges the token they're paid in against price collapse; premium funded from on-going emission stream
- **PK anchor**: literal Kaleckian real-economy investment (physical hardware capital → real service output). BLR P_i side: produces real network capacity. BLR P_k side: token speculation by non-operators.

### Pre-pin (anti-fishing locked)

| Field | Value |
|---|---|
| Sign | β > 0 (emission cuts AND price drops AND demand substitution all reduce operator revenue) |
| Magnitude floor | β ≥ 0.10 SD-units of Δlog(operator USD revenue) |
| Lag | Contemporaneous (token rewards transfer same-block); k=1 month secondary for cohort-attrition response |
| Primary spec | `Δlog(operator_USD_revenue_t) = α + β·Δlog(emission_index_t) + γ·Δlog(token_price_t) + ε_t`, monthly, HAC L=⌊T^(1/3)⌋ |
| Inference | HAC + cluster-robust by DePIN protocol |
| Power | 0.80 (N=76 months 2020-01 → 2026-04 likely achievable — Helium since 2019, Filecoin since 2020-10) |
| HALT | If any sub-DePIN has < 24 monthly observations, drop from primary panel; report separately |

### Pass criteria
- ≥3 of 5 named DePIN protocols yield N≥24 monthly observations of operator USD revenue
- β CI excludes zero at α=0.05 in primary spec on pooled panel
- Cohort size ≥10K operators across the pooled panel
- Panoptic / Uniswap V3 pool exists on ≥2 of 5 DePIN tokens

### Fail criteria
- <2 DePIN protocols clear N=24 cleanly
- Cohort size <1K total across all DePINs
- β CI contains zero across all specifications

### Sub-tasks (parallel, dispatched after meta-spec approval)
- E1.1: DePIN protocol inventory + emission-schedule mechanics (5 protocols)
- E1.2: Operator wallet observability + cohort-size estimation via on-chain analytics
- E1.3: Token price + emission-event panel construction (CryptoCompare + protocol subgraphs)
- E1.4: Panoptic / Uniswap V3 pool inventory for DePIN tokens (tradability check)
- E1.5: Cross-DePIN ERPT-equivalent literature (token-emission elasticity)

---

## Direction E2 — RWA Token Holders × Real-Cashflow Disruption

### Y, M, X candidate

- **Cohort**: Holders of tokenized real-world asset positions backed by off-chain productive cashflow:
  - **Centrifuge** pool tokens (Anemoy JTRSY/JAAA US Treasury; New Silver Series 3 real-estate credit; Flowcarbon carbon credits)
  - **Maple Finance** lending-pool tokens ($2B AUM revival; institutional underwritten credit pools)
  - **Plume Network** native RWA-token ecosystem
  - **Ondo Finance** (USDY/OUSG tokenized treasury — different mechanism, treated as comparison)
  - **Goldfinch** (legacy V1 pools winding down; comparison only)

- **Y**: RWA-token NAV trajectory = `pool_token_USD_value_t` for each pool; aggregate: cohort weighted-average NAV
- **X**: Underlying real-cashflow shock (default rate in pool; regulatory event on tokenized-asset class; secondary-market liquidity collapse)
- **M (descriptive-only)**: long-tail OTM put on RWA-token / USDC pool; payoff on NAV-decline events; premium funded by RWA-token staking yield where available
- **PK anchor**: BLR real-economy by construction — tokenized claim on off-chain productive cashflow. Pure P_i instrument. The protection is against the real-side cashflow disruption that BLR's "virtual prosperity" framing identifies as the ultimate constraint.

### Pre-pin

| Field | Value |
|---|---|
| Sign | β < 0 (real-cashflow disruption reduces NAV) |
| Magnitude floor | β ≥ 0.05 SD-units of Δlog(NAV) — RWA pools target stable NAVs, small β bands are meaningful |
| Lag | Contemporaneous primary; k=1 month secondary (admin lag in pool valuation) |
| Primary spec | `Δlog(NAV_t) = α + β·disruption_indicator_t + γ·Δlog(rate_index_t) + ε_t`, monthly |
| Inference | HAC + cluster-robust by pool |
| Power | 0.80 if N≥48 monthly observations achievable; demonstration-grade fallback for newer pools |
| HALT | If <3 pools achieve N≥24, redirect to single-pool case-study rather than panel |

### Pass criteria
- ≥3 RWA pools yield N≥24 monthly NAV observations
- At least 2 historical disruption events identifiable (Goldfinch V1 default cycle; March 2023 tokenized-treasury volatility; potential 2024-2026 pool-specific events)
- β CI excludes zero in primary spec
- Pool TVL aggregate ≥$500M

### Fail criteria
- <2 RWA pools with N≥24
- Zero identifiable historical disruption events
- Aggregate TVL <$100M (insufficient cohort scale)

### Sub-tasks
- E2.1: RWA pool inventory + NAV-history pull (Centrifuge subgraph + Maple subgraph + Plume + Ondo)
- E2.2: Historical disruption-event inventory (Goldfinch V1 defaults; SVB-era treasury moves; pool-specific incidents)
- E2.3: Underlying-rate-index panel (3-mo T-bill, SOFR, EM credit spreads as comparator)
- E2.4: Panoptic/Uniswap pool tradability for RWA tokens
- E2.5: Permissionless premise audit (Centrifuge issuer model vs Maple borrower model — does Abrigo's "permissionless" requirement hold for either?)

---

## Direction E3 — Concentrated-Liquidity LP Providers × IL Spike / Two-Price Gap Shock ⭐ Methods-paper anchor

### Y, M, X candidate

- **Cohort**: Uniswap V3 / Aerodrome / Velodrome / Maverick concentrated-LP providers on stablecoin + volatile-asset pairs. Pure Minsky hedge-finance instances by construction.
- **Y**: LP position USD value (HODL value − IL + fee yield − gas/rebalance cost) trajectory; per-position panel
- **X**: Realized impermanent-loss shock = `|P_pool(t) − P_oracle(t)| / P_oracle(t)` blowups (stablecoin depeg events, oracle-failure cascades, MEV sandwich events) — the **Minsky P_k − P_i gap mechanically instantiated**
- **M (descriptive-only)**: Panoptic put on LP-token / USDC. **The LP token itself IS the two-price-gap-bearing asset that Panoptic perpetuals were designed to price.** Per `reference_bhaduri_laski_riese_concept_bridge.md`: "the Minsky P_k/P_i gap is endogenously instantiated by every concentrated-liquidity AMM, and Panoptic-style perpetual options price that gap directly".
- **PK anchor**: this is the **cleanest empirical operationalization** of BLR/Minsky two-price theory in any cohort identified to date. Methods-paper headline.

### Pre-pin

| Field | Value |
|---|---|
| Sign | β < 0 (IL spike reduces LP value relative to HODL) |
| Magnitude floor | β ≥ 0.20 SD-units of Δlog(LP value) — IL events are large by construction |
| Lag | Contemporaneous (IL realizes intra-block) |
| Primary spec | `Δlog(LP_value_t) = α + β·IL_realized_t + γ·Δlog(fee_yield_t) + ε_t` per-pool, monthly |
| Inference | HAC + cluster-robust by pool tier (0.01% / 0.05% / 0.30% / 1%) |
| Power | 0.80 with N=76 months across pools achievable structurally |
| HALT | If IL events identified across <3 distinct shock types (depeg, oracle, MEV), narrow to single-shock case study |

### Pass criteria
- ≥5 distinct LP pools yield N≥48 monthly observations
- ≥3 distinct historical IL-shock events (March 2023 USDC depeg, Terra contagion May 2022, 3AC/Celsius June 2022, FTX November 2022, BUSD depeg episodes)
- β CI excludes zero in primary spec
- **Methods-paper acceptance criterion**: empirical pricing of Panoptic perpetual put approximates BLR/Minsky P_k − P_i closed-form within ±20% over ≥3 events

### Fail criteria
- <3 IL-shock events identifiable cleanly
- β CI contains zero across all pool tiers
- Panoptic pricing diverges from theoretical P_k − P_i by >50% (would suggest Panoptic primitive is NOT pricing the Minsky gap, killing the methods-paper headline)

### Sub-tasks
- E3.1: Uniswap V3 pool inventory + LP position panel (subgraph)
- E3.2: Historical IL-shock event taxonomy (depeg / oracle / MEV)
- E3.3: Panoptic perpetual-put pricing data (where Panoptic positions existed historically — limited)
- E3.4: BLR/Minsky P_k/P_i closed-form derivation for stablecoin+volatile LP (math derivation, not data; informs methods-paper)
- E3.5: Empirical IL vs theoretical-two-price-gap comparison across events

---

## Direction E4 — Public-Goods Builders × Grant-Regime Cuts (Karma GAP observability)

### Y, M, X candidate

- **Cohort**: Builders receiving on-chain grant capital with Karma GAP EAS-attested milestones — Kaleckian builder cohort producing real output. Sub-cohorts:
  - **Optimism RetroPGF** recipients (rounds 1-5; OP-denominated grants)
  - **Arbitrum STIP** recipients (ARB-denominated)
  - **Gitcoin Grants** historical (closed Stack but data available)
  - **q/acc** cohort (Polygon zkEVM; tokenized via ABCs)
  - **Octant epoch** recipients (90-day ETH-funded rounds)

- **Y**: Builder runway weeks = `wallet_balance_t / monthly_burn_rate_t`; secondary: real-output rate = Karma GAP milestones attested per month
- **X**: Program-size cuts to grant emissions (OP/ARB allocation reductions; Gitcoin Stack sunset; Octant epoch budget changes); secondary: token-price collapse of grant-denominator (OP/ARB/ETH)
- **M (descriptive-only)**: Panoptic put on OP/USDC or ARB/USDC pool; builder hedges grant-denominator token they're paid in; premium funded by builder's USDC reserve. Alternative: short-vol position on Karma-GAP-attested-milestone-rate index.
- **PK anchor**: Kaleckian builder cohort (real production) under endogenous-grant-money credit-cycle risk. BLR P_i side: builder produces real output (code, products, attested milestones). P_k side: grant-token speculative pricing.

### Pre-pin

| Field | Value |
|---|---|
| Sign | β > 0 (grant cuts reduce builder runway) |
| Magnitude floor | β ≥ 0.10 SD-units of Δlog(runway weeks) |
| Lag | Contemporaneous primary; k=1 month secondary for response in milestone-attestation rate |
| Primary spec | `Δlog(builder_runway_t) = α + β·Δlog(program_size_t) + γ·Δlog(grant_token_USD_t) + ε_t`, monthly per cohort |
| Inference | HAC + cluster-robust by program |
| Power | 0.80 if Karma GAP attestation history N≥36 achievable; demonstration-grade fallback otherwise |
| HALT | If <2 grant programs yield clean panels, redirect to single-program case study |

### Pass criteria
- ≥3 grant programs yield N≥36 monthly observations of builder-cohort wallet balances
- Karma GAP EAS attestations clear panel ≥1000 milestones
- ≥2 identifiable program-size cut events (OP RetroPGF round-budget changes; Arbitrum STIP-bridge sunset 2024; Gitcoin Stack wind-down 2025-05)
- β CI excludes zero in primary spec

### Fail criteria
- <2 grant programs with clean panel
- Karma GAP attestation count <100 milestones (insufficient real-output signal)
- β CI contains zero

### Sub-tasks
- E4.1: Karma GAP EAS attestation pull (Ethereum + Optimism + Arbitrum + Celo); milestone-count panel construction
- E4.2: OP/ARB/ETH grant-program disbursement-event timeline (program-size cuts as X-event panel)
- E4.3: Builder wallet identification via Allo Protocol + RetroPGF recipient registry
- E4.4: Q/acc cohort data (Season-1 + Season-2 if available; Mirror.xyz posts)
- E4.5: Cross-program builder-cohort overlap analysis (same builders receive from multiple programs?)

---

## Cross-direction structural opportunities

### E3 is the methods-paper anchor
Per `reference_bhaduri_laski_riese_concept_bridge.md`, the cleanest unfilled academic gap is "Minsky P_k/P_i formally connected to AMM micro-structure". E3's Panoptic-on-LP empirical work IS this contribution. Independent of E3's gating verdict, E3.4 (theoretical derivation) + E3.5 (empirical fit) are publishable.

### E1 + E4 share Kaleckian real-output measurement
Both target builders producing real-economy output (DePIN operators ≡ physical infrastructure; PG builders ≡ open-source code/products). Combined headline = on-chain productive-output rate vs speculative-trading rate (Y_real / Y_virtual at maximum generality).

### E2 is closest to legacy financial-instrument structure
RWA tokens are tokenized claims on off-chain productive cashflow — the bridge to traditional asset-class hedging. Strongest external-positioning story for traditional finance audiences.

## Sequencing & dispatch

1. **This meta-spec** drafted; dispatch 4 × RC + 4 × CR (8 parallel agents) for 2-way review per direction. Spec graduates to v0.2 after autofix-all per established pattern.
2. **Per-direction gating execution** after meta-spec v0.2 approval: 4 directions in parallel, each with 5 sub-task agents (~20 total). Same pattern as first-round gating execution.
3. **Per-direction consolidation** to gate_decision.md with PASS / PARTIAL / FAIL / NON-RETIREMENT verdicts.
4. **Cross-direction methods-paper draft** in parallel (E3 anchor; E1/E4 supplementary; E2 comparison).
5. **Promotion of surviving directions** to full-iteration spec drafting per the dev_ai_cost_v2 / D1.D+D4 precedent.

## Open items for reviewer attention

1. E1 cohort scale: Helium 1M+ hotspots is real; but how many of those are *active* economically (revenue-producing) vs dormant? Reviewer should flag if cohort-size 10K floor is achievable on active-revenue basis only.
2. E2 permissionless premise: Centrifuge issuer model requires off-chain custodian + legal wrapper. Does this break Abrigo's "permissionless" requirement? E2.5 sub-task flags this; reviewer should weigh.
3. E3 methods-paper vs gating-step bifurcation: E3 is more valuable as methods-paper than as gating verdict (LP IL is well-known to be negative; the contribution is the PRICING via Panoptic). Reviewer should advise on whether E3 should be reframed as a "theoretical case study + empirical demonstration" rather than a β-iteration.
4. E4 builder-runway Y construction: depends on cohort-wallet identification at scale. Karma GAP coverage of OP/ARB/Gitcoin recipients is partial. Reviewer should flag if Y is computable cleanly.
5. Cross-direction overlap: do E1 (DePIN ops) and E4 (PG builders) cohorts overlap (same builders running DePIN hardware AND receiving PG grants)? Could be confounder or productive joint analysis.
6. Sequencing realism: 4-parallel gating execution requires ~20 sub-task agents simultaneously. First-round (D1-D4) successfully did this. Reviewer should advise on whether to throttle for context budget.

## Anti-fishing closure

All §0 invariants carry forward to each direction unchanged. Pre-pin locked in this draft; any post-data threshold tuning triggers CORRECTIONS block + 2-way re-review per established pattern. NON-RETIREMENT is a valid outcome for any direction that data-blocks.

Meta-spec v0.1 closes here. Awaiting 4-direction × 2-way (8-agent) review.
