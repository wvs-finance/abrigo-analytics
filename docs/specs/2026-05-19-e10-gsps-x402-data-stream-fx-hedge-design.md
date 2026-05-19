# E10 — Generalized Subscription Payment Stream (GSPS): x402-USDC data-consumption FX hedge for Colombian Web3-analyst cohort

**Spec version:** v0.1 DRAFT (G2 candidate; awaiting subgraph-coverage research closure + G3 RC+CR 2-way review)
**Date:** 2026-05-19
**Parent artifacts:**
- Conversational framing transcript: 2026-05-19 session (Bittensor → x402 → GSPS generalization arc)
- Parent iteration referenced for X-substrate: `docs/specs/2026-05-18-e4-narrowed-superfluid-r3-design.md` (Superfluid streamed-liability primitive)
- Pair D PASS verdict reused as X-substrate prior: `memory/project_pair_d_phase2_pass.md` (COP/USD lag β = +0.137, p ≈ 1.5e-08)
- Methods-paper joint outline: `docs/specs/2026-05-19-methods-paper-e3-e8-e9-joint-outline.md` (proposed E10 contribution)

**G0 verdict (proposed, pending DV-gate):** CONDITIONAL CANDIDATE — passes the abstract feasibility test (x402 USDC payments are live on Base via The Graph Gateway and CoinGecko per public 2026 announcements); decisive feasibility verdict depends on the §0 DV-gate audit currently in flight (background agent `superfluid-subgraph-x402-coverage`, dispatched 2026-05-19).

**Anchor memos:**
- `memory/reference_bhaduri_laski_riese_concept_bridge.md` (PK anchor)
- `memory/feedback_dune_last_resort_exhaust_free_resources.md` (DV-gate cost rule; E10 is *defined by* this rule applied to the data-consumption layer)
- `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`
- `memory/feedback_data_visibility_gate_before_modeling.md`
- `memory/project_pair_d_phase2_pass.md` (X-substrate reuse rationale)
- `memory/feedback_no_code_in_specs_or_plans.md`
- `memory/feedback_no_inline_signatures_in_plans.md`

**Methodology anchor:** x402 (HTTP 402 Payment Required revival) under Linux Foundation governance (2026-04-02; founding members include Coinbase, Google, AWS, Microsoft, Stripe, Visa, Mastercard); The Graph Gateway USDC-on-Base x402 endpoint (2026 launch); CoinGecko x402 USDC endpoints at $0.01/req flat. The instrument family generalizes the streamed-liability convex hedge primitive (E4) and the Pair D COP/USD lag β to a third Y-channel: continuous-consumption API payment streams.

**PK theory anchor:** BLR 2006 virtual-vs-real dichotomy applied at the *data-services-import* margin. A Colombian Web3 analyst's productive output (P_i) is observable code / dashboards / analytical models; their consumption of data services (the input the productive function requires) is priced in USDC and paid via continuous streams, while their income is COP-denominated. The COP/USD adverse move during the stream window is the exact micro-risk this iteration tests as a hedgeable β surface.

---

## 0. Data-visibility gate verdict (RESOLVED 2026-05-19: DV-PASS-FREE confirmed; substrate-age caveat introduced — see §0.4 + CORRECTIONS-E10-1)

Per `memory/feedback_data_visibility_gate_before_modeling.md`, the DV gate runs upstream of all iteration-specific G0 checks. For E10 the gate is the critical-path decision: the entire iteration is *defined* by the proposition that paid-Dune is unnecessary because The Graph Gateway covers the on-chain payment-stream surface at near-zero cost.

### 0.1 Decision-citation block — DV gate (RESOLVED)

> **Reference:** `memory/feedback_dune_last_resort_exhaust_free_resources.md`; G3 background research dispatched 2026-05-19 (agent `superfluid-subgraph-x402-coverage`) returned primary-source verification per §0.4 below.
> **Why this gate runs first:** the iteration thesis presumes the substrate is observable on free or near-free infrastructure. The G3 research closed this question definitively.
> **Relevance to E10:** §0.4 findings (a) **confirm DV-PASS-FREE** via the Superfluid V1 Optimism subgraph at Graph free tier ($0/mo, dominates Dune Plus $390/mo at 20× cost headroom on 5k queries/mo); but (b) **introduce a substrate-age caveat** — x402 USDC payments on Base went live only **2026-05-12** (eight days before this spec), forcing the §2 cohort sample window to be reconsidered (see CORRECTIONS-E10-1).
> **Connection to chosen data path:** Superfluid V1 Optimism subgraph (CFA flows, IDA/GDA events, Stream / Token / Account entities) on Graph free tier as primary; x402 USDC pay-per-query on Base as future-substrate layer once protocol matures; Banrep TRM (free, public) for COP/USD reference; CoinGecko free tier (USDC reference). All paths PASS-FREE — no engineering substitute required.

### 0.2 Source ledger (RESOLVED 2026-05-19)

| Component | Source | Endpoint / URL | Tier | Refresh cadence | Verified |
|---|---|---|---|---|---|
| Superfluid CFA flows on Optimism (PRIMARY substrate per CORRECTIONS-E10-1) | The Graph Decentralized Gateway → `superfluid-finance/protocol-v1` Optimism deployment | `https://gateway.thegraph.com/api/[API-KEY]/subgraphs/id/48YRvi7PHbX4RJChq4nF8DpmJGZxcvUgwfdf8QoHBXxT` | free tier 100k queries/mo (sufficient for E10 by 20× headroom) | per-block | 2026-05-19 (G3 closure; ~3.2K GRT signal; Stream/FlowUpdatedEvent/Account/Token/Index/Pool entities all confirmed in `schema.graphql`) |
| x402 USDC payment events on Base (FUTURE substrate; substrate-too-young as of 2026-05-19) | The Graph Gateway x402 endpoint on Base | `gateway.thegraph.com/api/x402/...` (canonical pattern UNCONFIRMED — blog post returned HTTP 500 on G3 fetch) | x402 USDC pay-per-query; price returned dynamically in 402 header (no published flat rate) | Base block cadence (~2s) | x402 gateway live **2026-05-12** per crypto.news; per-query pricing opaque |
| USDC/Base reference price + depeg-event panel | CoinGecko free tier | `api.coingecko.com/api/v3/coins/usd-coin` | free 30 calls/min | hourly | 2026-05-19 |
| COP/USD daily reference rate | Banco de la República (Banrep) | `https://www.banrep.gov.co/sites/default/files/paginas/trm.xls` + REST API | free public | daily | reused from Pair D + E5 |
| Optimism chain raw RPC (verification fallback) | Optimism public RPC | `https://mainnet.optimism.io` | free, rate-limited | per-block | reused from E4 |
| Base chain raw RPC (x402 indexer build path) | Base public RPC | `https://mainnet.base.org` | free, rate-limited | per-block | available |

**Pricing line (RESOLVED):** Graph free tier provides 100k queries/mo against the Superfluid V1 Optimism subgraph. Expected E10 query budget ≤ 5,000/mo. **Headroom: 20× the budget at $0/mo recurring cost.** Compares to **$390/mo Dune Plus** under the legacy subscription model — the substitution is economically dominant by infinite ratio.

**Critical caveat (G3 finding):** x402 USDC payment events on Base do NOT yet exist as a usable cohort substrate. x402 launched 2026-05-12 (eight days before this spec); the cohort sample window for x402 events is necessarily 2026-05-12 → present, which is too short to support empirical β identification. See **CORRECTIONS-E10-1** for the substrate-redefinition consequence.

### 0.3 Free-path audit per `dune-last-resort-exhaust-free-resources` (RESOLVED)

Per the rule's audit checklist:

| Question | Action | Status |
|---|---|---|
| Is the data on-chain? | Superfluid CFA on Optimism is fully on-chain | YES |
| Is there a maintained subgraph? | Superfluid V1 Optimism subgraph `48YRvi7…HBXxT` on Graph Decentralized Network; entity coverage includes Stream/FlowUpdatedEvent/Account/Token/Index/Pool | YES (G3 confirmed) |
| Is the data covered by a public BigQuery dataset? | `bigquery-public-data.crypto_optimism` available as cross-check | YES |
| Is there a provider-specific free API? | CoinGecko free tier (USDC); Banrep TRM (COP/USD) | YES both |
| If all above fail, is paid Dune the only path? | N/A — Graph free tier dominates Dune Plus by 20× headroom at $0/mo | N/A |

**Audit verdict:** DV-PASS-FREE CONFIRMED. No engineering substitute required for the Superfluid Optimism substrate path. The x402-on-Base substrate path is held in abeyance per CORRECTIONS-E10-1 (substrate-too-young).

### 0.4 G3 closure findings (2026-05-19; primary-source verified)

Per background research dispatch `superfluid-subgraph-x402-coverage`:

**Confirmed**:
- Subgraph ID `48YRvi7PHbX4RJChq4nF8DpmJGZxcvUgwfdf8QoHBXxT` (Superfluid V1 Optimism) is live on Graph Decentralized Network
- Maintainer: Superfluid team (`superfluid-finance/protocol-monorepo`, `packages/subgraph/schema.graphql`)
- Entities present: Stream (CFA), FlowUpdatedEvent, Account, Token (SuperToken), Index/IndexSubscription (IDA), Pool/PoolMember (GDA), TokenStatistic, AccountTokenSnapshot
- Graph free tier provides 100k queries/mo; E10 expected budget ≤ 5,000/mo (20× headroom)
- x402 gateway live on Base since 2026-05-12 per `crypto.news`; endpoint pattern `/api/x402/...`

**UNCONFIRMED (would require live probe)**:
- Subgraph sync freshness (explorer panel was "Loading" at fetch; resolve via `_meta { block { number } }` GraphQL probe)
- Indexer count and reliability (3.2K GRT signal is modest)
- x402 per-query USDC price (returned dynamically in 402 header; no published rate)
- Whether the Superfluid V1 Optimism subgraph specifically is routable via the x402 endpoint (crypto.news implies all decentralized-network subgraphs, but not specifically verified)

**Caveats**:
- x402 is brand new (8 days as of spec date); canonical Graph blog post for x402 returned HTTP 500 during G3 fetch — endpoint stability concern
- GRT vs USDC billing: API-key billing via GRT-on-Arbitrum or credit card; USDC only via x402-on-Base. No GRT-on-Base path. For a Colombia-based wallet, holding USDC on Base is operationally simpler than acquiring GRT on Arbitrum.
- Schema-level: GDA Pool entities present; legacy IDA-only patterns also covered. Verify subgraph version matches Optimism deployment block range if analysis touches GDA-specific events.

### 0.5 CORRECTIONS-E10-1 — substrate-too-young; primary substrate switched from x402-on-Base to Superfluid-CFA-on-Optimism

**Trigger:** G3 closure (§0.4) revealed that x402 USDC payments on Base went live only 2026-05-12 — eight days before this spec. The §2 cohort sample window (originally 2025-12 → 2026-05) cannot be populated with x402 events because the substrate did not exist before 2026-05-12. The cohort sample window for x402 events is necessarily 2026-05-12 → present (≤ 8 days), which is structurally below any meaningful N for empirical β identification.

**Anti-fishing-compliant response** (per `feedback_pathological_halt_anti_fishing_checkpoint.md`):

1. **Disposition memo:** The original §2 cohort filter ("≥ 1 USDC payment event on Base directed at a data-services x402 endpoint") is **structurally infeasible** at this date. This is not a threshold-tuning issue; it is a substrate-existence issue. The substrate-too-young verdict mirrors the structural substrate caveat preserved in `memory/project_p1_sn18_spec_parked_for_record.md` §9 ("SUBSTRATE_TOO_YOUNG 4th outcome").
2. **User-enumerated pivot (single option offered ex ante in §1.4 [DEF-3]):** primary substrate switches to **Superfluid CFA flows on Optimism** as the data-consumption-stream observable. This was anticipated in §1.4 [DEF-3] as one of two stream-treatments; the pivot promotes it from secondary to primary. The x402 substrate remains a future-roadmap component (§9 NON-RETIREMENT-PENDING-MATURITY outcome), re-checkable at +6 and +12 months.
3. **CORRECTIONS block (this section):** all downstream sections updated to reflect Superfluid-Optimism as primary substrate. §2 cohort filter, §3 Y construction, and §5 spec all need amendment in v0.2 (deferred to G4 dispatch).
4. **Post-hoc 3-way review (required per the rule):** dispatch RC + CR + reviewer wave at v0.2 prior to any E10.1 cohort enumeration sub-task.

**What this CORRECTIONS preserves**:
- The (Y, M, X) triple's *structure*: COP-cost of a continuous-consumption USDC outflow stream hedged by Panoptic COPm/USDC put, on a substrate that observes the outflow. Switching the substrate from x402 to Superfluid CFA preserves all three.
- The X-substrate (COP/USD lag per Pair D PASS) — unchanged.
- The methods-paper hook (§8 GSPS generalization) — unchanged.
- The anti-fishing invariants (§7) — unchanged.

**What this CORRECTIONS changes**:
- §2 cohort filter: "x402 payment events on Base" → "Superfluid CFA outflows on Optimism to identifiable data-services / consumption-services receivers" (the receiver-identification rule [DEF-2] becomes the critical filter)
- §0.2 PRIMARY substrate moved to Superfluid-Optimism subgraph
- §9 verdict ladder gains explicit **NON-RETIREMENT-PENDING-MATURITY** outcome for the x402 path (re-check trigger: x402 protocol age ≥ 6 months AND ≥ 50 Colombian-attributable payer wallets identifiable)

**What this CORRECTIONS does NOT do (banned moves per anti-fishing rule)**:
- Does NOT relax the §5 sign / magnitude / lag / primary-spec pre-pin. Those remain LOCKED.
- Does NOT extend the sample window beyond the substrate's existence to manufacture cohort size on x402.
- Does NOT silently re-name the iteration or hide the substrate switch. The CORRECTIONS block is the visible record of the pivot per established discipline (analogous to E4 narrowed CR-S3 / RC-F8 fold).

---

## 1. Cohort verification result (PENDING G3 closure)

### 1.1 Decision-citation block — cohort filter

> **Reference:** Pair D PASS verdict (`memory/project_pair_d_phase2_pass.md`, β = +0.137 on COP/USD lag); CLAUDE.md framework (investor classes that are exposed to a hedgeable micro-risk on a productive-investment path).
> **Why this filter:** the operative cohort consists of wallets that (a) make recurring USDC payments to data-services endpoints (The Graph Gateway, CoinGecko x402, QuickNode x402 RPC), (b) exhibit Colombian-country attribution (whether by self-disclosed payment-receipt metadata, geo-IP if available from gateway logs, or by wallet co-occurrence with COP-stablecoin transactions such as COPm via Mento on Celo).
> **Relevance:** the iteration's empirical claim — that COP/USD lag transmits to data-consumption-stream USD-cost — requires a cohort observably *both* paying in USDC *and* exposed to COP/USD. Without the Colombian-attribution filter, the cohort collapses to global x402 payers and the FX-channel identification is lost.
> **Connection to verdict:** N_cohort target ≥ 75 (anti-fishing floor); if Colombian-attribution under any of the three rules above yields N < 75, the iteration downgrades to a **simulated-cohort posture** (E10-Sim, where the cohort is constructed from a representative Colombian-analyst data-consumption profile, and Y is computed as a counterfactual COP-cost path).

### 1.2 N_cohort and distribution (PENDING G3)

PENDING the G3 subgraph-coverage closure. Expected upper bound: low hundreds of wallets globally on Base x402 (the protocol is six months old as of 2026-05); the Colombian-attribution sub-cohort is expected to be tens, not hundreds. The HALT trigger in §5 row 7 binds.

### 1.3 HALT-trigger evaluation (PENDING)

| Pre-pin HALT trigger | Threshold | Observed | Status |
|---|---|---|---|
| N_cohort < 75 → downgrade to E10-Sim posture | 75 | PENDING-G3 | PENDING |
| x402 subgraph absent on The Graph Gateway → DV-FAIL → NON-RETIREMENT or fallback indexer build | live + queryable | PENDING-G3 | PENDING |
| Banrep TRM not retrievable for 2025-06 → 2026-05 window | retrievable | retrievable (reused from Pair D and E5) | NOT triggered |

### 1.4 Deferred-to-ingest items (non-blocking, recorded for transparency)

- **[DEF-1]** Colombian-attribution rule selection: choose between (a) wallet co-occurrence with COPm Mento transactions on Celo + bridge-traceable Base activity; (b) self-disclosed payment-receipt metadata (if x402 spec allows); (c) IP-geo from public gateway logs (privacy-bounded). Decision at G3.
- **[DEF-2]** x402 payment-event ABI: requires confirmation from x402 reference implementation that payment receipts are indexable as event logs (vs in-headers-only). Background agent dispatched.
- **[DEF-3]** Stream-vs-discrete-payment treatment: x402 produces discrete pay-then-retry events; Superfluid CFA produces continuous flow updates. The Y definition (§3) must treat both as instances of the same payment-stream notional aggregated over the month.

---

## 2. Cohort definition (LOCKED candidate; pending §1 closure)

Eligibility expression (locked at v0.1, will move to LOCKED at G3 close):
- Wallet address W with ≥ 1 USDC payment event on Base directed at a data-services x402 endpoint within the sample window (2025-12 → 2026-05; six-month window expected to grow)
- Colombian-attribution rule satisfied per §1.4 [DEF-1] (one of three rules)
- Aggregate monthly USDC consumption-stream notional ≥ $10 USDC equivalent (dust filter; excludes one-shot test transactions)
- Sample window: 2025-12 inclusive → most-recent-completed-month inclusive (rolling tail)

Out of scope (NON-RETROFITTABLE):
- Non-Colombian x402 payers — they don't exhibit COP/USD risk by construction; the FX-channel identification requires the cohort definition.
- One-shot x402 payment events (single requests, no stream) — the iteration is about *continuous-consumption* GSPS, not discrete API calls. Continuous-consumption is operationalized as ≥ 2 distinct payment events in the same month.
- Non-data-services x402 payees — the iteration is narrowly about data-availability consumption (the user's stated pivot from AI inference to data layer). AI-inference x402 (e.g., Anthropic relayer if it materializes) is a sibling iteration E10-B that may follow.
- Counterfactual cohort scaling ("if N Colombian analysts adopted x402...") — banned by `memory/project_abrigo_portfolio_prioritization_with_fallback.md`. The simulated-cohort posture (E10-Sim) is permitted as an explicit downgrade verdict, NOT as a primary fantasy frame.

---

## 3. Y definition (LOCKED candidate)

### 3.1 Primary Y

**Y_{i,t} = realized COP-equivalent monthly cost of wallet i's USDC consumption stream during month t.**

Construction:
- Numerator: sum of all USDC payment events from wallet i to in-scope data-services endpoints during month t, in USDC units
- Multiplier: month-t average COP/USD rate from Banrep TRM (monthly mean)
- Y_{i,t} has units of COP/month and is the operative variable the hedge protects

Normalization: log-difference Δlog(Y_{i,t}) for the regression; cross-wallet level differences absorbed by wallet FE.

### 3.2 Secondary Y (robustness arm)

**Y_USD_{i,t} = realized USD-cost of the same stream, NO COP multiplier.** This separates the *USDC stream-quantity* channel from the *COP/USD multiplier* channel. The β on COP/USD lag should be near-zero on Y_USD (the stream is USDC-denominated; FX should not enter mechanically) — its non-zero deviation identifies any usage-rate response to FX (e.g., the wallet reduces queries in COP/USD adverse periods).

### 3.3 Banned Y constructions

- "Counterfactual COPm-streamed equivalent" as primary Y — that's an M-side construction; using it as Y collapses the firewall between empirical β identification and M-design.
- Per-wallet USDC-equivalent productive output (the analyst's revenue from dashboards / reports) — introduces a separate income-channel β that confounds the consumption-side identification. Productive-output β is a Stage-3 deployment concern, not Stage-1.

---

## 4. X definition (LOCKED candidate; reuses Pair D substrate)

### 4.1 Decision-citation block — X choice

> **Reference:** Pair D PASS verdict (`memory/project_pair_d_phase2_pass.md`); Banrep TRM daily series; the same COP/USD lag construction validated in Pair D Phase-2 at β = +0.137, p ≈ 1.5e-08.
> **Why COP/USD lag as the instrument:** the iteration's mechanical claim — that the COP-denominated cost of a USDC-priced data stream rises when COP weakens against USD — is identical in structure to Pair D's BPO offshoring cost-channel. The PASSing β is the prior; E10 tests whether the *same* X transmits to a *different* Y channel (data consumption vs labor offshoring).
> **Relevance:** the X side is empirically validated; the iteration's contribution is the Y side (new substrate). This compresses the iteration risk to: does the data-consumption channel admit a measurable β on an X that already has a PASSing prior?
> **Connection to chosen lag structure:** k=1 day, k=7 day, k=28 day lags per Pair D Phase-2 spec; primary is contemporaneous monthly aggregation (consistent with §3.1 monthly Y construction).

### 4.2 Auxiliary X (USDC depeg-event channel)

Secondary X: USDC/USD basis vol over the month, sourced from CoinGecko free tier. The hypothesis: even with COP/USD held constant, a USDC depeg event (e.g., the 2023-03 SVB-driven event) would shift Y by the depeg magnitude. Pre-pin: |β_depeg| ≪ |β_COPUSD| over the sample window (no major depeg event in 2025-12 → 2026-05 expected; the depeg β is a robustness arm).

### 4.3 NOT controlled for (deliberately pre-pinned)

- x402 protocol per-request unit-price drift — the protocol is six months old; per-request pricing is set by gateway operators and changes infrequently. Pre-pin: any per-request price change within the sample window is recorded as a finding, not absorbed.
- The Graph indexer-selection latency — the gateway routes per-query to indexers; we observe the USDC payment notional, not the indexer revenue split. The wallet's POV is the payment notional, which is what Y captures.

---

## 5. Pre-pin (seven fields, LOCKED candidate; demonstration-grade posture pending §1)

| # | Field | Value | Rationale / non-negotiable |
|---|---|---|---|
| 1 | **Sign** | β > 0 on contemporaneous Δlog(COP/USD) → Y rises when COP weakens | Direct mechanical channel: USDC-priced stream × COP/USD multiplier; identical sign-prior to Pair D. |
| 2 | **Magnitude floor** | 0.10 SD-units of Δlog(Y) — demonstration-grade posture | Cohort size (PENDING §1) expected at tens not hundreds; demonstration-grade floor honest given event-N constraint. Promote to 0.40 (MDES_SD per CLAUDE.md anti-fishing invariant) if N_cohort ≥ 75. **No post-hoc floor adjustment.** |
| 3 | **Lag** | Contemporaneous monthly primary; k=1, k=7, k=28 day daily-aggregation secondaries | Mirrors Pair D Phase-2 lag structure for cross-iteration comparability |
| 4 | **Primary spec** | Δlog(Y_{i,t}) = α + β · Δlog(COP/USD_t) + γ_i + ε_{i,t}; monthly panel; wallet FE; cluster-robust SE by wallet; HAC L=⌊T^(1/3)⌋ within-wallet | Same family as Pair D Phase-2 spec; cluster-robust because wallet count > 30 expected (if PENDING §1 confirms); HAC handles within-wallet serial correlation |
| 5 | **Inference** | Wild cluster bootstrap (Cameron-Gelbach-Miller; Webb six-point weights; B=999) by wallet if G ≥ 30 wallets; per-wallet jackknife if G < 30 | Inference geometry chosen by cohort size; both options pre-committed; no post-data switching |
| 6 | **Power posture** | **Demonstration-grade** by default; upgrades to confirmatory-grade IFF N_cohort ≥ 75 AND sample-window months ≥ 6 | x402 is six months old; sample window naturally tight. Demonstration-grade is honest; confirmatory upgrade is conditional. |
| 7 | **HALT condition (binding)** | If §1 returns N_cohort < 25 even at the loosest Colombian-attribution rule → automatic downgrade to **E10-Sim** simulated-cohort posture (single Y trajectory under representative consumption profile, no empirical β estimated, methods-paper contribution preserved). If x402 subgraph absent AND custom-indexer fallback fails → NON-RETIREMENT. **Sign / magnitude / lag / spec all FROZEN at pre-pin.** | Anti-fishing invariant carry-forward |

### 5.1 Auxiliary controls (locked into the X_{i,t-k} term)

- USDC reserve composition shift indicator (Circle attestation events) — absorbs USDC depeg-risk channel
- Base chain gas fee level (mean per-month) — absorbs payment-fee component if non-trivial relative to stream notional
- Banrep monetary policy rate change events — absorbs COP-side monetary channel

### 5.2 NOT controlled for (deliberately pre-pinned)

- x402-protocol adoption rate over the sample window — part of the cohort dynamic, not a confounder
- The Graph indexer-network GRT-burn rate — gateway internals; wallet POV abstracts over this

---

## 6. M-sketch (Stage-2 firewall; Panoptic perpetual put on COP/USDC proxy; descriptive only)

### 6.1 Decision-citation block — M anchor

> **Reference:** Pair D PASS Phase-2 M-sketch (precedent for COP/USD-denominated Panoptic positions in the Abrigo portfolio); CLAUDE.md §"Transmission mechanism — premium-funded ratchet on productive investment"; E4 narrowed §12 (streamed-liability convex hedge primitive).
> **Why this M anchor:** the iteration extends a validated M-family to a third instance (E4 streamed-liability + Pair D BPO-channel + E10 data-consumption-channel all share the same Panoptic-perpetual-put structure with stream-funded premium). The M-anchor is *not novel* — that's the point. The contribution is the Y-side substrate, not the M-side mechanism.
> **Relevance:** M is descriptive only at Stage-2; deployment is firewalled to Stage-3 per CLAUDE.md.
> **Connection to empirical β:** Panoptic put on COP/USDC pair (or USDC/ETH proxy if COPm/USDC depth on Mento insufficient on the deployment chain) pays out precisely when Δlog(COP/USD) > 0 — the same shock §5 row 1 identifies empirically.

### 6.2 Ideal-scenario M position (descriptive)

```
Underlying pair:        COPm / USDC on Celo (Mento native pair) — primary
                        USDC / ETH on Base (proxy if COPm/USDC depth insufficient on Panoptic)
Position venue:         Panoptic perpetual put on the Uniswap V3-equivalent pool
Strike:                 80-90% of COP/USDC spot at stream-month start (long-tail OTM)
Position notional:      monthly USDC stream notional × COP/USDC spot at strike
Tenor:                  monthly rolling (perpetual on Panoptic; auto-rolled each cycle)
Premium source:         ≤10% of monthly stream notional, debited as a Superfluid CFA flow
                        out of the wallet's USDC balance (the stream funds the hedge on
                        its own premium — Streamed-Liability Convex Hedge primitive, third
                        instance after E4 + E9-A)
Anti-correlation:       put pays out exactly when monthly Y (COP-denominated stream cost)
                        rises above pre-hedge expectation — convex protection on the
                        productive-investment trajectory of the Web3 analyst cohort
```

### 6.3 Generalized-subscription-payment-stream (GSPS) instrument family — methods-paper hook

E10 is the **section-5 candidate anchor** of the joint methods-paper outline at `docs/specs/2026-05-19-methods-paper-e3-e8-e9-joint-outline.md`. Proposed restructure:

- Section 1: PK theoretical anchor (BLR + Minsky two-price + Kaleckian) — cross-iteration
- Section 2: Maymin CEV-on-AMM bridge (E8 dTAO)
- Section 3: Superfluid-stream stochastic continuous settlement (E4 narrowed) — first streamed-liability instance
- Section 4: Fabi MFG energy-AMM bridge × Colombian AGPE empirical β (E9-A) — second streamed-liability instance
- **Section 5 (NEW): GSPS x402-USDC payment-stream β on COP/USD lag (E10) — third streamed-liability instance; cross-cohort generalization (RetroPGF builders + Colombian PV operators + Colombian Web3 analysts); demonstrates that the streamed-liability convex hedge is a family, not a one-off**
- Section 6: Joint convergence — three permissionless CFMM constructions all operationalize the Minsky P_k / P_i AMM-gap proposition under non-trivial cohort data

E10's contribution to the methods-paper is **independent of the §5 β verdict**. On NON-RETIREMENT (DV-gate fail or N_cohort below downgrade threshold), the GSPS conceptual generalization survives as a methods-paper artifact. On PASS or PARTIAL, the contribution upgrades to "GSPS β validated on a real Colombian-Web3-analyst cohort using a payment substrate (x402) that did not exist when the framework was first proposed."

### 6.4 Premium funding (descriptive; native to the substrate)

Unique to E10 vs prior iterations: **the hedge premium can itself be paid as a Superfluid CFA flow out of the same wallet that runs the consumption stream**. The wallet maintains two flows simultaneously: outflow-A to data-services (the consumption stream); outflow-B to the Panoptic put premium escrow (the hedge stream). Both are denominated in USDC and netted against the same Base-chain wallet balance. Total economic exposure to COP/USD is hedged at the wallet level, end-to-end on-chain, with no off-chain settlement friction.

This is the **cleanest empirical instance of the GSPS primitive in the Abrigo portfolio**: substrate, instrument, and cohort all native to the same on-chain rail.

### 6.5 Stage-correctness (CLAUDE.md)

- Stage 1 (this iteration §1-§5): empirical risk validation on x402 data-consumption substrate
- Stage 2 (this section §6.1-§6.4): ideal M-sketch — Panoptic put structure with Superfluid-streamed premium, descriptive only
- Stage 3 (OUT OF SCOPE): no LP-capital sourcing on Panoptic COPm/USDC, no live x402 hedge-premium flow, no Mento bridge deployment

Stage drift is anti-fishing-banned.

---

## 7. Anti-fishing carry-forward

Per `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`:

- **N_MIN = 75** (carried; binds on confirmatory-grade promotion; demonstration-grade default if N < 75)
- **POWER_MIN = 0.80** (carried at the cohort dimension; sample-window-dimension constraint disclosed via per-wallet jackknife when G < 30)
- **MDES = 0.10 SD-units** of Δlog(Y) (demonstration-grade); 0.40 (confirmatory-grade) iff cohort upgrades — pre-committed, no post-hoc adjustment
- All pre-pin fields declared BEFORE any data is touched: §5 is locked at v0.1; G3 closure only revises §1 cohort verification, not §5 spec content
- **HALT chain** fires on any spec-vs-data contradiction: disposition memo + user-enumerated pivot + CORRECTIONS block + post-hoc 3-way review
- **NO Colombian-attribution rule swap after data pull.** [DEF-1] resolves to ONE rule at G3; the other two become explicit robustness arms (sign-concordance only, not inferential)
- **NO post-hoc sample-window extension** to manufacture cohort size. Sample window is anchored to the rolling tail of x402 protocol existence (six months as of 2026-05).
- **NO post-hoc magnitude floor adjustment.** 0.10 (demo) / 0.40 (confirmatory) is FROZEN; promotion requires structural N-clearance, not magnitude tuning.
- **NO sensitivity-arm rescue of primary FAIL.** Daily-lag arms (k=1, k=7, k=28), Y_USD secondary, USDC-depeg-channel auxiliary are all sensitivity-only.
- **NO importing Pair D's β = +0.137 as a magnitude target for E10.** Pair D is the X-substrate prior; the Y substrate is novel. Magnitude is identified independently on the new Y.

### 7.1 NON-RETIREMENT as a real verdict possibility

E10's §9 verdict ladder explicitly includes NON-RETIREMENT under two distinct triggers: (a) DV-gate failure (no subgraph + no viable indexer build path), (b) cohort failure (N < 25 even at loosest Colombian-attribution rule). The E10-Sim simulated-cohort downgrade preserves the methods-paper hook even if empirical β cannot be estimated.

---

## 8. Methods-paper hook (cross-iteration)

E10 is the third (after E4, E9-A) and conceptually-most-general instance of the streamed-liability convex hedge primitive in the Abrigo portfolio. The methods-paper contribution is:

- E4 instantiates on a Superfluid-streamed-vesting cohort (forced lock, mechanically-illiquid tail)
- E9-A instantiates on a Colombian AGPE energy-AMM cohort (productive-output flow, hydrology-shock-priced)
- **E10 instantiates on a continuous-consumption payment-stream cohort (USDC outflow, FX-priced) — the most general form, where the hedged stream is a *cost* rather than a *receipt*. The asymmetry generalizes the streamed-liability primitive from "hedge a streamed-in receipt" to "hedge a streamed-out cost" — both within the same convex-payoff Panoptic structure.**

The cross-iteration convergence claim: a single Panoptic perpetual put with stream-funded premium hedges *both* receipt-stream cohorts (E4, E9-A) and cost-stream cohorts (E10), distinguished only by the cohort's stream direction. This is the methods-paper contribution worth a Cambridge JE / ROPE / Metroeconomica submission, independent of any single iteration's β verdict.

---

## 9. Verdict ladder (collectively exhaustive; LOCKED ex ante)

| Verdict | Conditions | Action |
|---|---|---|
| **PASS** | β̂ > 0 on contemporaneous Δlog(COP/USD_t); β̂ ≥ MDES (0.10 demo / 0.40 confirmatory per §5 row 2); 90% wild-cluster-bootstrap CI excludes 0 from below; sign consistent across daily-lag sensitivity arms; N_cohort ≥ 75 (confirmatory) or ≥ 25 (demonstration) | Stage-2 M-sketch graduates to formal write-up; methods-paper section 5 anchor upgrades to validated form; cross-iteration convergence claim (§8) gains its third empirical instance |
| **PARTIAL** | β̂ > 0 but EITHER β̂ < MDES OR CI sign-ambiguous OR daily-lag arms flip sign on ≥ 1 lag | Demonstration-grade verdict; methods-paper §5 anchor preserved at descriptive form; cross-iteration convergence claim preserved with PARTIAL footnote |
| **FAIL** | β̂ ≤ 0 with 90% CI excluding 0 from above (wrong sign confirmed) | Sign-failure recorded honestly; HALT + disposition memo; close E10 β-claim; methods-paper §5 anchor still proceeds with the qualitative GSPS-generalization bridge; E10-B (AI-inference x402 sibling) would inherit a chastened prior |
| **NON-RETIREMENT** | (a) DV-gate fail (now resolved — DV-PASS-FREE per §0), OR (b) N_cohort < 25 at loosest Colombian-attribution rule on the Superfluid-Optimism substrate, OR (c) sample-window months < 4 after Colombian-attribution filter on Superfluid-Optimism | Park E10 empirical β-claim; preserve GSPS conceptual contribution to methods-paper §5 in qualitative form |
| **NON-RETIREMENT-PENDING-MATURITY** (NEW; per CORRECTIONS-E10-1) | Triggered specifically for the x402-on-Base substrate path: substrate age < 6 months AND Colombian-attributable payer wallet count < 50 | Park x402-substrate sub-iteration; re-check trigger at x402 age ≥ 6 months (≈ 2026-11) AND ≥ 50 Colombian payers; Superfluid-Optimism substrate path proceeds independently and is not blocked by this verdict |

**Note on the E10-Sim downgrade clause.** If §1 returns N_cohort in [10, 25), the iteration shifts to E10-Sim posture: a representative-Colombian-Web3-analyst consumption profile is constructed (e.g., 5000 The Graph queries/mo + 500 CoinGecko x402/mo + 2000 QuickNode RPC/mo = ~$15-25/mo USDC stream notional), the Y trajectory is computed counterfactually under that profile + Banrep TRM history, and the β is estimated on the single counterfactual time series. This is descriptive-only, demonstration-grade, and explicitly NON-FANTASY because the consumption profile is the *user's own* observed profile, not a fictional cohort scaling.

---

## 10. Sub-task order (locked dispatch sequence)

1. **E10.0** (G3 closure; PRECONDITION; background agent dispatched 2026-05-19): close the subgraph-coverage question per §0.2 PENDING-G3 line. Outcome decides DV-gate verdict.
2. **E10.0.B** (G3 closure; PRECONDITION): close the Colombian-attribution rule selection [DEF-1] per §1.4. Outcome decides §1.1 cohort filter.
3. **E10.1**: cohort enumeration — pull all x402 USDC payment events on Base in sample window; apply Colombian-attribution rule; produce cohort registry with N_cohort + per-wallet monthly notional.
4. **E10.2**: panel construction — per-wallet per-month Y (COP-equivalent stream cost) via Banrep TRM monthly mean; per-day X (Δlog(COP/USD)) panel.
5. **E10.3**: primary β estimation — pre-pin §5 spec; wild cluster bootstrap inference.
6. **E10.4**: sensitivity arms — daily-lag k=1, k=7, k=28 (sign-concordance only); Y_USD secondary (residual-channel identification); USDC-depeg auxiliary (robustness only).
7. **E10.5**: verdict assembly — per §9 ladder; disposition memo if HALT triggers.

E10.0 and E10.0.B are HALT-gating preconditions; if either fails, the iteration NON-RETIREMENTs (or downgrades to E10-Sim) without running E10.1-E10.5.

---

## 11. Open items for reviewer attention (G3 RC + CR dispatch)

1. **DV-gate closure (§0.2 PENDING-G3)**: background agent must return subgraph IDs + x402 endpoint URLs + cost confirmation. If subgraph absent → custom-indexer build estimate (1-2 days vs the assumed default) — confirm engineering ceiling acceptable.
2. **Colombian-attribution rule (§1.4 [DEF-1])**: three candidate rules; which is the primary at G3? Privacy boundary on the IP-geo rule may rule it out unilaterally.
3. **Stream-vs-discrete payment treatment (§1.4 [DEF-3])**: x402 emits discrete events; Superfluid CFA emits continuous flow updates. Confirm §3.1 monthly aggregation handles both uniformly.
4. **Demonstration-grade vs confirmatory-grade default (§5 row 6)**: should the demonstration-grade default be locked even if N_cohort ≥ 75 marginally, to be conservative on the new substrate? Alternative: hardcode demonstration-grade for v0.1, promote to confirmatory only in a hypothetical v0.2 spec revision.
5. **E10-Sim posture (§9 note)**: should E10-Sim be a separate spec, or absorbed as a downgrade within E10? Currently absorbed; reviewer may argue for split.
6. **Methods-paper §5 reservation (§8)**: confirm allocation of methods-paper §5 slot to E10 is consistent with the joint outline; alternative is to add E10 as a §5.4 subsection within an extended §5.

---

## 12. Anti-fishing closure

All §7 invariants carry forward to each sub-task unchanged. Pre-pin locked in this draft; any post-data threshold tuning triggers CORRECTIONS block + 2-way re-review per the established pattern. NON-RETIREMENT and E10-Sim downgrade are valid acceptable outcomes; neither is a goal-post move.

E10 GSPS spec v0.1 DRAFT closes here. Awaiting (a) G3 background-research closure on subgraph coverage, (b) G3 RC + CR 2-way review per workplan progressive-gating chain.
