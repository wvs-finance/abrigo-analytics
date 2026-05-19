# Portfolio-Level Progressive-Gating Work Plan

**Date:** 2026-05-18
**Anchor specs:**
- `docs/specs/2026-05-18-four-direction-investment-productivity-gating.md` v0.3
- `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2 (older joint iteration)
- `memory/project_abrigo_portfolio_prioritization_with_fallback.md`

## Generalizable primitive — Streamed-Liability Convex Hedge

Across multiple surviving directions, the cohort receives a **recurring stream** (subsidies, grants, token emissions, claims) that creates an **unhedged liability** against local-currency obligations. The general M-shape:

```
M = Panoptic perpetual put sized to STREAM-TAIL UN-REALIZED NOTIONAL
    on (stream-denominator-token / USDC) pool
    premium funded by claimed-and-converted stream-head receipts
```

Instances of this primitive across the portfolio:

| Direction | Stream | Stream-tail liability | Hedge M |
|---|---|---|---|
| **E4 narrowed (Superfluid R3+)** | OP RetroPGF R3+ Superfluid 90-day vest stream | Un-vested OP balance mechanically locked | Panoptic put on OP/USDC sized to un-vested notional |
| **E5-revised (RefiColombia)** | 10K-COPm claims every ~9.6h | Forward-expected COPm flow × COP-realized purchasing-power | Panoptic put on COPm/cUSD straddle |
| **E8 (Bittensor dTAO)** | TAO + alpha subnet emissions | Future-revenue alpha/TAO un-converted balance | Maymin-CEV-priced put on alpha/TAO native pool |
| **E7 (Mento minter)** | COPm/EURm/BRLm peg-defense seigniorage stream | Mento reserve composition risk | Cross-Mento basket convex hedge |
| **E10 (GSPS data-consumption)** | Colombian Web3-analyst USDC outflow stream paying for blockchain-data services (Superfluid CFA on Optimism primary; x402-on-Base future) | COP-denominated cost of monthly USDC stream notional under COP/USD adverse move | Panoptic put on COPm/USDC sized to monthly stream notional; premium itself paid as a parallel Superfluid CFA — first cost-side instance of the family |

The unifying observation: **the stream itself is the premium-funding source for the convex hedge on the stream-tail**. This collapses Abrigo's "premium-funded ratchet" framework into a single repeatable instrument design. With E10, the family closes under stream direction: receipt-side streams (E4, E5, E7, E8) and cost-side streams (E10) share the same M-shape with the cohort's exposure-direction as the only sign-flip.

## Progressive Gating Framework (G0 → G4)

Every direction in the portfolio progresses through 5 gates. Blockers surface as early as possible; PASS at each gate unlocks the next. NON-RETIREMENT at any gate is honest exit per `feedback_pathological_halt_anti_fishing_checkpoint.md`.

### G0 — Cohort + Observability Feasibility (≤2 days)
- Cohort exists and is identifiable on EVM (or simulatable per fantasy-threshold rules)?
- Data sources public-default + free-tier?
- N_MIN=75 achievable structurally (counting active-revenue cohort members, not registered)?
- **BLOCK if**: cohort not identifiable / data not public / cohort scale <1/3 of N_MIN

### G1 — Y Construction + Pre-pin Sketch (≤5 days)
- Y empirically constructible from G0 data?
- X identifiable from PK theory (BLR/Minsky/Kaleckian) + observable on chain?
- 7-field pre-pin (sign / magnitude / lag / primary spec / inference / power / HALT) drafted?
- **BLOCK if**: Y has mechanical identity bias / X not pre-pinnable / cohort N achievable but pre-pin requires Y to be reframed

### G2 — Pre-pin Draft Spec + 2-way Review (≤7 days)
- Spec drafted to dev_ai_cost_v2 v0.2.1 / D1.D+D4 v0.2 template
- RC + CR review dispatched in parallel
- All Critical findings autofix-cascaded to v0.2 of direction spec
- Closure-only re-review APPROVED_WITH_NITS or better
- **BLOCK if**: spec v0.2 still has unaddressed Critical findings / permissionless premise breaks

### G3 — Implementation Plan + 2-way Review (≤7 days)
- Plan v0.1 drafted to D1.D+D4 plan v0.2 template
- TDD scaffold (failing tests for every modules-tier component)
- Anti-fishing mechanical enforcement (compliance grep tests; HALT triggers in code)
- RC + CR review → autofix → closure-APPROVED
- **BLOCK if**: plan v0.2 still has unaddressed Critical findings / wall-clock implausible

### G4 — Iteration Execution + Verdict (≤21 days per spec §10)
- Phases 0-7 execution per plan v0.2
- Post-hoc audit-econ Delphi (3 Opus auditors) before write-up
- Verdict: PASS / PARTIAL-PASS / FAIL / NON-RETIREMENT per §7 collectively-exhaustive matrix
- **BLOCK / NON-RETIREMENT if**: empirical data contradicts pre-pin / HALT triggers fire

### G5 — Stage-2 M-Sketch (post-PASS only)
- Ideal-scenario Panoptic-position design
- No deployment work; sketch only per CLAUDE.md staging discipline

### G6 — Stage-3 Deployment (out of scope for this work plan)
- Requires live LP capital + Panoptic-mainnet-tradability verification

## Per-Direction Current G-Level (2026-05-18 snapshot)

| Direction | Status | Current G | Next-gate trigger |
|---|---|---|---|
| **E8 dTAO × Maymin** | ACTIVE PRIMARY | **G2** (Day-1 G0+G1 complete; methods-paper-only verdict; ready for spec draft) | Draft E8 standalone spec v0.1 + 2-way review |
| **E5-revised RefiColombia** | FROZEN READY (PARTIAL Day-1) | **G1 PARTIAL** (effective cohort N=70 <75; lifetime 521d) | Wait ~10 weeks for cohort growth OR reframe Y → Δlog(claim_ops) weekly + activate |
| **E7 Mento minter** | FROZEN READY (pinned) | **G0** (not yet dispatched) | G0 cohort feasibility scoping (~2 days) |
| **E4 narrowed (Superfluid R3+)** | FROZEN READY (E4.0 narrowed) | **G1 PARTIAL** (Option A narrowing locked; re-execute Dune q/3399900 needed) | Re-execute Dune + draft narrowed-E4 spec v0.1 |
| **E9 NEW Energy-AMM convex hedge** | NEW 2026-05-18 (user-added via Fabi et al. 2025-12) | **G0 dispatch pending** | G0 feasibility scoping: Colombian prosumer cohorts + EVM energy-flow observability |
| **E10 GSPS x402-data-stream FX hedge** | NEW 2026-05-19 (cost-side streamed-liability extension) | **G2 DRAFTED** (spec v0.1 at `docs/specs/2026-05-19-e10-gsps-x402-data-stream-fx-hedge-design.md`; G0 PASS-FREE confirmed via Superfluid Optimism subgraph; G1 PASS — Y/X/pre-pin in spec §3-§5; CORRECTIONS-E10-1 substrate pivot recorded) | v0.2 spec amendment propagating substrate pivot to §2-§5 + RC+CR 2-way review → G3 plan |
| **E3 + E8 + E9 + E10 joint methods-paper** | PARALLEL TRACK | **G2** (theory + empirical anchors in place; E9 extends to energy-numéraire; E10 extends to cost-side streamed-liability on continuous-consumption payment streams) | Methods-paper draft (multi-year track) |

## Direction E9 — Energy-AMM Convex Hedge (NEW 2026-05-18)

### Theoretical anchor
**Fabi, Nadkarni, Leone, Ferreira (2025-12)** "Automated Market Making for Energy Sharing" arXiv:2512.24432. Mean-Field Game equilibrium for prosumer-community AMMs. Numerical experiments on Paris administrative region. Result: prosumer community achieves up to **40% gains-from-trade vs grid-only**. Theoretical only — no live blockchain implementation in 2026.

### The conceptual move
Price the M-layer in **kWh-equivalent** rather than COP/USD. Energy is the cleanest P_i numéraire possible per BLR/Minsky lens — it directly represents real-economy productive consumption rather than financialized derivative-of-money. Connects to Soddy (1926) energy-money / real-wealth distinction, Daly steady-state economics, Hodgson institutional money theory.

### Cohort candidate (Colombia-specific per user §0.8.2)
- **Rural solar prosumers** under Resolución CREG 174/2017 (PV self-generation framework)
- **IPSE** (Instituto de Planificación y Promoción de Soluciones Energéticas) rural electrification beneficiaries
- **UPME Subasta de Energía Firme** participants (small-scale generators)
- Aggregator cohorts via **EPM** (Empresas Públicas de Medellín), **Codensa**, **Celsia**

### Pre-pin sketch (G1 — locked after G0 PASS)
- **Y**: cohort-aggregate prosumer realized kWh-output ÷ expected baseline (productivity ratio); or kWh × spot energy price = real economic output
- **X**: energy-shock micro-risks per PK theory — XM operator dispatch costs; CREG resolution regime shifts; El Niño / La Niña hydropower volatility (Colombia ~70% hydro); tokenized REC price shocks
- **M**: Panoptic-equivalent perpetual put on tokenized-kWh-credit / USDC pool, sized to prosumer expected production stream-tail; premium funded by kWh-credit head receipts — **same streamed-liability M-shape as E4/E5/E7/E8**
- **PK anchor**: literal energy-money / real-resource hedging — direct empirical operationalization of BLR/Minsky "real economy" P_i side

### G0 feasibility checks (1-3 days, dispatched alongside Wave 1)
1. **EVM-side energy-tokenization observability** in 2026 — Powerledger / GridSingularity / Energy Web Chain / WePower / SunContract — which are live EVM, what TVL, what volume
2. **Colombian XM operator public data** — dispatch costs, prosumer registries, daily/monthly time-series
3. **CREG-174 prosumer cohort scale** — UPME public registry; could clear N_MIN=75?
4. **Tokenized-REC precedent on EVM** — any LATAM RECs on Toucan / Solid World / KlimaDAO adjacent infrastructure?
5. **Permissionless premise**: can Colombian prosumer hold tokenized kWh on EVM without KYC?

### Fantasy-threshold lock (per portfolio memo)
Energy-AMM is theoretical-only in 2026; simulation IS the path to G1 → G2 unless live infrastructure surfaces. Pre-pin BEFORE simulation:
- Real Colombian XM dispatch data (public-default ✓)
- Real CREG-174 prosumer registry (UPME public ✓)
- Real Colombian electricity prices (XM ✓)
- Synthetic AMM-equivalent dynamics priced via Fabi et al. 2025 Mean-Field Game framework
- DO NOT generate counterfactual "10K Colombian energy-prosumer-AMMs" — that crosses fantasy threshold per `project_abrigo_portfolio_prioritization_with_fallback.md`

## Direction E10 — GSPS x402-Data-Stream FX Hedge (NEW 2026-05-19)

### Theoretical anchor
**x402 protocol** (HTTP 402 Payment Required revival; Linux Foundation governance 2026-04-02; founding members include Coinbase, Google, AWS, Microsoft, Stripe, Visa, Mastercard) + **Superfluid CFA** (constant-flow agreement, continuous on-chain token streaming). The Graph Decentralized Gateway launched USDC-on-Base x402 pay-per-query endpoints 2026-05-12. The conjunction makes per-call and streamed payments to data-services API endpoints natively on-chain — for the first time, a continuous-consumption API service is a fully-observable on-chain payment stream.

### The conceptual move
**Generalize the streamed-liability primitive from receipt-side to cost-side.** All prior instances (E4 RetroPGF receipts, E5 Refi claims, E7 Mento seigniorage, E8 Bittensor emissions, E9 AGPE excedentes) hedge a stream that the cohort *receives*. E10 hedges a stream the cohort *pays*. The Panoptic-perpetual-put M-shape is identical; the only sign-flip is exposure direction. This closes the streamed-liability family under stream direction — a methodological contribution independent of E10's empirical β verdict. Connects to BLR/Minsky on the *data-services-import* margin: a Colombian Web3 analyst's productive output (P_i) is observable code/dashboards/models; the API-consumption input is USDC-priced, while income is COP-denominated, and the COP/USD adverse move during the stream window is the hedgeable micro-risk.

### Cohort candidate (Colombia-specific per user §0.8.2)
- **Colombian Web3-analyst cohort** paying recurring USDC streams to data-services endpoints (The Graph Gateway via x402-on-Base or API-key; CoinGecko x402 endpoints; QuickNode x402 RPC) — observable as on-chain payment events
- Colombian-attribution via one of three rules (per E10 spec §1.4 [DEF-1]): (a) wallet co-occurrence with COPm Mento transactions on Celo + bridge-traceable Base/Optimism activity; (b) self-disclosed payment-receipt metadata if x402 spec permits; (c) IP-geo from public gateway logs (privacy-bounded)
- Dust filter: aggregate monthly USDC consumption-stream notional ≥ $10 USDC equivalent

### Pre-pin sketch (G1 — locked in spec v0.1 §5; awaiting v0.2 amendment per CORRECTIONS-E10-1)
- **Y**: realized COP-equivalent monthly cost of wallet i's USDC consumption stream during month t (USDC notional × Banrep TRM monthly mean)
- **X**: Δlog(COP/USD_t) per Pair D PASS substrate (β = +0.137, p ≈ 1.5e-08); contemporaneous monthly primary; k=1, k=7, k=28 day daily-aggregation secondaries
- **M**: Panoptic perpetual put on COPm/USDC (Mento native on Celo) sized to monthly stream notional; premium funded as a parallel Superfluid CFA outflow from the same wallet — **same streamed-liability M-shape as E4/E5/E7/E8/E9, sign-flipped on exposure direction**
- **Sign**: β > 0 (mechanical; USDC-priced stream × COP/USD multiplier)
- **Magnitude floor**: 0.10 SD-units demonstration-grade by default; 0.40 SD-units confirmatory-grade iff N_cohort ≥ 75
- **PK anchor**: BLR cost-side instantiation on data-services-import margin; Minsky P_k/P_i operationalized via the gap between USDC-priced API service (P_k-equivalent virtual-economy input price) and COP-denominated productive output (P_i analog)

### G0 feasibility checks (RESOLVED 2026-05-19)
1. **Subgraph coverage**: Superfluid V1 Optimism subgraph `48YRvi7PHbX4RJChq4nF8DpmJGZxcvUgwfdf8QoHBXxT` confirmed on Graph Decentralized Network with Stream/FlowUpdatedEvent/Account/Token/Index/Pool entities — PASS
2. **Cost path**: Graph free tier 100k queries/mo dominates Dune Plus $390/mo at 20× headroom on E10 budget — PASS-FREE
3. **x402-on-Base substrate maturity**: protocol launched 2026-05-12 (8 days before spec); cohort sample window for x402 events is structurally too short — **substrate-too-young; CORRECTIONS-E10-1 pivoted primary substrate to Superfluid-Optimism** (memory pin: `project_e10_x402_substrate_pending_maturity_2026_11`)
4. **X-substrate prior**: Pair D PASS verdict reused as Δlog(COP/USD) prior — substrate confirmed
5. **Colombian-attribution rule**: three candidate rules in [DEF-1]; resolution at G3 dispatch

### Substrate-pivot lock per CORRECTIONS-E10-1 (per anti-fishing rule)
- **Primary substrate**: Superfluid CFA flows on Optimism (subgraph confirmed free-tier)
- **Future substrate (NON-RETIREMENT-PENDING-MATURITY)**: x402 USDC payments on Base; re-check trigger 2026-11 (x402 age ≥ 6 months AND ≥ 50 Colombian-attributable payer wallets)
- **DO NOT** propose x402-on-Base as primary substrate for any iteration before 2026-11 re-check confirms both conditions

### G-progression for E10 (per portfolio framework G0→G6)
| Gate | Status (2026-05-19) | Next-gate trigger |
|---|---|---|
| **G0** Cohort + observability feasibility | PASS-FREE (resolved 2026-05-19; G3 background research closure) | — |
| **G1** Y construction + pre-pin sketch | PASS (spec v0.1 §3-§5 locked; 7-field pre-pin per CLAUDE.md anti-fishing invariants) | — |
| **G2** Pre-pin draft spec + 2-way review | **DRAFTED** (v0.1 at `docs/specs/2026-05-19-e10-gsps-x402-data-stream-fx-hedge-design.md`); v0.2 amendment pending to propagate CORRECTIONS-E10-1 substrate pivot through §2 cohort filter / §3 Y construction / §5 spec amendments | v0.2 amendment + RC+CR 2-way review dispatch |
| **G3** Implementation plan + 2-way review | PENDING — blocked on G2 v0.2 close | After G2 close: draft plan v0.1 per `docs/plans/...-e10-implementation-plan-v0.1.md` template |
| **G4** Iteration execution + verdict | PENDING — blocked on G3 | Per spec §10 sub-task sequence (E10.0 → E10.5); 21-day budget |
| **G5** Stage-2 M-sketch (post-PASS only) | PENDING — blocked on G4 PASS verdict | Stage-2 Panoptic-position descriptive write-up per spec §6 |
| **G6** Stage-3 deployment | OUT OF SCOPE for this workplan | Requires live LP capital + Panoptic-mainnet-tradability verification on COPm/USDC pool |

## Parallel Dispatch Plan (sorted by primary-fallback order)

### Wave 1 (immediate dispatch)
1. **E8 spec v0.1 draft** + 2-way review (G2 → G3)
2. **E8 LATAM-operator simulation pre-pin** (under fantasy-threshold guard) — parallel to spec
3. **E7 G0 cohort feasibility** (Mento minter) — 2-day cheap scoping in parallel
4. **E4 narrowed (Superfluid R3+) Dune re-execute** + spec v0.1 draft
5. **E9 G0 feasibility scoping** — Colombian prosumer + EVM energy-tokenization observability (NEW 2026-05-18 per user Fabi et al. paper)

### Wave 2 (post-Wave-1 verdicts)
5. **E8 plan v0.1** + 2-way review (G3 → G4)
6. **E5 reframe spec amendment** — apply Δlog(claim_ops) weekly + freeze for 10-week cohort growth
7. **Methods-paper joint E3+E8 outline** — multi-year parallel track

### Wave 3 (post-Wave-2)
8. **E8 Phase 0 dispatch** (G4 execution) — sub-package scaffold + TDD harness
9. **E7 G1 if Wave-1 G0 PASSes**

### Fall-back triggers (per portfolio memo)
- E8 data infeasible OR simulation crosses fantasy threshold → activate E4-narrowed + E5-revised in parallel
- E4 fails Dune re-execute OR narrowing doesn't preserve N_MIN → escalate to E5 or E7

## Streamed-Liability Convex Hedge — Methodology Generalization

If 2+ directions PASS G4 with streamed-liability M-shape, we have a **portfolio-level methodology paper** beyond the E3+E8 Maymin paper:

> *"Streamed-Liability Convex Hedging on Permissionless CFMM Venues: Empirical Operationalization of the Minsky P_k/P_i Gap Across Heterogeneous Cohorts."*

Empirical instances supporting the methodology: E4 PG builders + E5 RefiColombia + E7 Mento minter + E8 Bittensor operators. Each is a different domain (open-source builders / direct-transfer recipients / stablecoin minters / decentralized AI operators) but the M-shape is identical. This is a stronger external-positioning narrative than any single iteration.

## Anti-fishing carry-forward

All §0 invariants from the four-direction spec carry forward:
- N_MIN=75 / POWER_MIN=0.80 / MDES_SD=0.40
- Pre-pin BEFORE data
- HALT-on-spec-vs-data triggers disposition memo + user-enumerated pivot + CORRECTIONS block
- NON-RETIREMENT is honest outcome at every gate
- Fantasy-threshold check per `project_abrigo_portfolio_prioritization_with_fallback.md`

The progressive-gating framework does NOT relax any invariant — it only ensures blockers surface at the cheapest possible step.

## Recommended next action

Dispatch Wave 1 (4 parallel tasks):
1. E8 standalone spec v0.1 draft (no dependencies)
2. E8 LATAM-operator simulation pre-pin (parallel to #1)
3. E7 G0 Mento minter cohort feasibility scoping (parallel)
4. E4 narrowed Dune q/3399900 re-execute + spec v0.1 draft (parallel)

Each is 1-3 day effort; all can dispatch immediately. Wave 1 outcomes inform Wave 2 prioritization within ~1 week.
