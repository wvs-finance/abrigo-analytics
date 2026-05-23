# Salvage Path 4 — On-Chain Crypto Rails

## Verdict
**CONDITIONAL VIABLE** — adopt as **Direction 1.D salvage** (complementary panel, not primary replacement). Public-default data exists; binding constraint is contractor-vs-speculator attribution within tagged Colombian-CEX inflows.

## Two-edged structural finding

1. **Public-default surface is large**. Colombian-resident CEX deposit addresses (Bitso/Lemon/Binance LATAM) tagged on Etherscan + hildobby. USDC/USDT inflow at monthly resolution back to 2020. Mento broker swap events public on Celo. **Monthly N=76 structurally achievable.**
2. **Wage-attribution layer is binding constraint**. Distinguishing "USDC inflow to Colombian exchange = wage from Deel/Remote/Bitwage" from "USDC inflow = speculator/saver round-trip" requires either labeled payroll-router addresses (exist but not publicly tagged) or statistical attribution by transaction pattern (tractable supervised-learning).

## On-chain payroll protocol inventory

| Protocol | Mechanism | Observability | CO relevance | Coverage |
|---|---|---|---|---|
| **Bitwage** (Paystand-owned 2024-11) | Funder→router→worker wallet; USDC/USDT/DAI on ETH+Polygon | Corporate funder partially observable | $400M+ processed, 90K workers; Colombia targeted | High — but address discovery needs clustering |
| **Deel Pay-with-Crypto** | Per-org unique deposit/payout; USDC/EURC/USDT on Base+Polygon | Per-org addresses NOT public; cluster against Deel master treasury | Deel dominant EOR in CO; stablecoin payouts live | High |
| **Remote** | Contractor stablecoin payouts, opt-in | Same as Deel | CO supported | Medium |
| **Request Finance** | Invoice-driven; worker controls address; smart contracts | **Fully observable via smart contracts** | ~2,000 web3 teams/DAOs | Low for total cohort, high for web3-native |
| **Superfluid** | Streaming Constant Flow Agreements; subgraph indexes every stream | **Fully observable via The Graph subgraph** | Niche, multi-chain (Polygon, Op, Base, Gnosis) | Low magnitude, cleanest observability |

**Key**: Bitwage post-Paystand + Deel + Remote together cover majority of US/EU-incorporated employer flows into Colombia in stablecoin form. **None publishes contract-address registry publicly.**

## Colombian-exchange deposit-address tagging (Etherscan + hildobby)

- **Bitso 1**: `0x58b704065b7aff3ed351052f8560019e05925023` — main hot wallet, 1,287,738 transactions, $39.78M tokens (USDT $32.16M + USDC $7.12M), active since 2021-05, multichain (Polygon, Arbitrum, Optimism, Avalanche, Base)
- **Bitso Deposit Funder**: `0x20beea119e70255a8c36e4009c94aedb1f8b8eea`
- **Lemon Cash**: labeled on Etherscan (specific addresses unverified in this dispatch)
- **Wenia / Bancolombia crypto**: operates through Bitso-as-custodian per public regulatory disclosure (Nvio Pagos Colombia in Banrep sandbox)
- **Binance LATAM**: heavily labeled but NOT country-segmented at address level — country attribution requires KYC-side data (not public)

**Central methodological problem**: operator identifiable; country-of-residence-of-depositor NOT recoverable from on-chain data alone.

## Mento COPm volume — too small for primary regressor

| Metric | Value | Source |
|---|---|---|
| cCOP supply (June 2025 H1 report) | 270M cCOP ≈ $64,804 USD | Celo Colombia H1 |
| Holders | ~11,000 unique addresses | Same |
| Cumulative txns | 83,000+ | Same |
| Reserve share | ~0.25% of Mento total | Same |
| May 2026 market cap | $67,668 | CoinGecko |
| 24h volume | $41K on Uniswap V3 Celo (negligible) | CoinGecko |
| Mento Reserve total (May 2026) | $21.72M across 12 stables | reserve.mento.org |

**Two orders of magnitude too small** for coverage-complete wage-conversion proxy. At ~$65K total supply, even 100% wage-payment attribution covers <0.001% of Colombian remote-worker wage flow estimated from BoP. Use only as:
- Existence-of-channel evidence (yes)
- Binary "channel-active" indicator post-Q1-2024
- NOT as primary regressor

## Stablecoin inflow attribution method (3 layers)

### Layer A: Volume envelope (high confidence)
Count monthly USDC + USDT transfers into tagged Bitso/Lemon hot-wallet set across {Ethereum, Polygon, Tron, Arbitrum, Base}. Upper bound on dollar-stable inflow to Colombian/LATAM CEX accounts. Method: Dune SQL against `tokens.transfers` filtered by destination ∈ labeled CEX set.

### Layer B: Colombian share scalar (medium confidence)
Apply 20% Colombia-share scalar (sensitivity 10-35%) derived from:
- Chainalysis 2025: stablecoins >50% of CEX purchases for COP (2024-07 → 2025-06)
- Bitwage Sept-2025: 99% of COP→crypto on Colombian CEXs goes to stablecoins; 40% of all retail Bitso CO buys = USDC/USDT
- Bitso cumulative LATAM Jan-Jul 2025 = $10.4B → 20% × ≈ $2B/year Colombia ≈ **$170M/month**

### Layer C: Wage-vs-speculator attribution (low confidence — binding gap)
Wage inflow segmentation requires:
- Source: deposits from US-corporate-payroll-treasury (Deel/Bitwage/Remote/Multiplier/Papaya/Rise/Toku) — labels don't exist publicly
- Cadence: regular fixed-magnitude transfers from same source to same destination
- Magnitude: round-dollar amounts ($2,500 = post-tax monthly salary at $40K/yr) clustered around month-end / 15th
- Counterparty graph: workers downstream of payroll routers don't typically trade speculatively on same address

**Tractable supervised-learning problem** given labeled training data. Without seed, degrades to anomaly detection with substantial false-positive risk.

## Coverage estimate

**Crypto-rail share of Colombian USD-paid remote-worker wage flow: 15-35% (central 20-25%).**

## Monthly N feasibility — YES

- Ethereum + Polygon coverage back to 2020
- Bitso 1 hot wallet active since 2021-05; pre-2021 via earlier labeled hot wallets
- Tron USDT flows back to 2019
- Celo Mento broker since 2020-04 for cUSD/cEUR; cCOP/COPm since 2024-Q1 only (N≈28 standalone)

**N=76 monthly observations 2020-01 → 2026-04 structurally achievable.** Anti-fishing N_MIN=75 invariant satisfied. **Volume is not the constraint; attribution quality is.**

## Privacy + aggregation policy

- Reporting threshold: never publish address-level metrics below 1,000 distinct sending addresses, or for addresses with annual flow >20× median
- Bucketing: month × chain × token × destination-exchange is safe; address × month is not
- Cross-reference suppression: never join on-chain address-level with off-chain identity (LinkedIn, Twitter, ENS) in published artifacts
- Pre-publication: re-identification adversary test; collapse cells <1000

## Existing Dune dashboards / subgraphs

| Resource | Coverage |
|---|---|
| Mento Labs Eng — Mento Overview (111599) | Official Mento data including cCOP/COPm |
| Mento Labs Eng — Mento Stables Usage (108201) | Per-stable supply, swap, holders |
| bintuparis — Mento Reserves Dashboard (182669) | Reserve composition |
| mando — BITSO ETH (87032) | Top-level Bitso, not CO-isolated |
| Superfluid Protocol V1 subgraph | Multi-chain (Polygon, xDai, Op, Base, Arb, ETH) |
| Mento Protocol Celo | celoscan.io Mento Labs Broker `0x777a8255ca72412f0d706dc03c9d1987306b4cad` |

**Custom-query requirement**: existing dashboards don't isolate Colombian flows. New Dune query bundle needed: monthly USDC/USDT inflow → {Bitso, Lemon} hot-wallets × {ETH, Polygon, Tron, Arb, Base}, joined with Mento broker swap volume on Celo. **Free Dune tier sufficient.**

## URLs verified

- https://bitwage.com/en-us/blog/state-of-stablecoins-in-colombia---september-2025
- https://www.coingecko.com/en/coins/ccop (cCOP/COPM market data)
- https://forum.celo.org/t/celo-colombia-report-2025-h1/11456 (Celo CO H1 2025: 270M cCOP, 11K holders, 83K tx)
- https://reserve.mento.org/ ($21.72M Mento reserve)
- https://etherscan.io/address/0x58b704065b7aff3ed351052f8560019e05925023 (Bitso 1)
- https://celoscan.io/address/0x777a8255ca72412f0d706dc03c9d1987306b4cad (Mento Broker)
- https://docs.superfluid.org/docs/sdk/money-streaming/subgraph
- https://help.letsdeel.com/hc/en-gb/articles/42333671207697 (Deel stablecoin)
- https://www.chainalysis.com/blog/latin-america-crypto-adoption-2025/ (CO $44.2B; >50% COP CEX = stables)
- https://dune.com/blog/latam-crypto-2025-report (Bitso $10.4B; Lemon $810M)
- https://castleisland.vc/wp-content/uploads/2024/09/stablecoins_the_emerging_market_story_091224.pdf (PDF, not parsed — gap)

## Recommendation: Adopt as Direction 1.D

1. **Position**: triangulation third leg, NOT primary measurement. Pair with DANE-GEIH (cohort sizing) + Banrep BoP services-credit (USD-flow envelope)
2. **Scope**: monthly USDC + USDT inflow to {Bitso, Lemon} hot wallets, 2020-01 → 2026-04, on {ETH, Polygon, Tron, Base, Arbitrum}; Colombia-share scalar 20% with sensitivity 10%/35%
3. **Pre-pin BEFORE data**: monotone-positive sign of Bitso-USDC-inflow on Banrep services-credit-USD; lag 0-1 months; spec = simple OLS of log(Bitso USDC inflow CO-share) on log(Banrep services-credit USD), monthly. Single-pin; no post-hoc tuning
4. **Power**: N=76 with expected correlation 0.4-0.6 → adequate
5. **Anti-fishing**: gate on conventional 0.05 significance + correct sign. If FAIL, informative about coverage (crypto-rail share too small to register against BoP), not re-tunable
6. **Mento COPm**: do NOT use as primary regressor. Binary "channel-active" indicator post-Q1-2024 only
7. **Pattern attribution (Layer C)**: defer to Phase 2; do not block Layer A+B on it

**3-week execution plan**:
- Week 1: Dune query bundle for Bitso/Lemon CEX inflow monthly; verify against published 2024 totals
- Week 2: Banrep services-credit reconciliation; cohort-share scalar derivation; pre-pin spec memo
- Week 3: estimation + HALT-checkpoint trio; gate verdict

## Connection to Direction 4 USDC-saver cohort (KEY STRUCTURAL INSIGHT)

D4.1 (USDC-saver cohort, 242K wallets) and D1.D (crypto-paid wage-earner cohort) have **significant but bounded overlap**:
- Both wallet-based, both Colombian-resident via Bitso/Lemon CEX-deposit proxy
- **Overlap mechanism**: worker receives USDC wage on-chain → routes part to Bitso for COP off-ramp (D1.D) → routes savings tail back to savings wallet (D4.1)
- **Overlap estimate: 30-60%, direction of causality D1.D → D4.1** (wage receipt enables saving, not reverse)

**This is precisely the wage→capital transition Abrigo is designed to measure.**

Joint model: D1.D inflow = treatment, D4.1 wallet-balance change = outcome, CEX off-ramp ratio = channel parameter → directly interpretable "fraction of wage flow that transitions into capital position." **Most valuable byproduct, not anticipated in original D1 gating.**

## Financialization-channel connection (FINANCILATION.md operationalization)

`CF_T = E_T − L_T` directly operationalized:
- **E_T (wage earnings flow)** = Layer A+B USDC inflow to Colombian-resident wallets + Layer C wage-vs-speculator scrubbing
- **L_T (savings/holdings depletion)** = symmetric COP off-ramp flow + savings retention rate
- **CF_T (cumulative financial position)** = D4.1 wallet balance trajectory

**The instrument that "creates the capital position" in the Abrigo framework IS the crypto rail itself.** Without USDC payroll: Colombian remote worker faces 3-7% Wise/Payoneer FX friction + regulated banking layer channeling savings into low-yield COP instruments. With USDC payroll: worker holds USD-stable assets natively, can opt into productive-capital exposure (Panoptic-mediated hedge).

The premium-funded ratchet: wage earner pays small recurring premium *out of the same USDC stream* into a Panoptic position. Settlement (COPm/USDC pair on Celo, or Uniswap V3 synthetic) theoretically supported by the rail this path measures.

**The on-chain rail is not just a measurement channel but the same channel as the deployment channel.** Non-trivial structural alignment between D1 measurement and Stage-2 deployment, unique among D1 salvage paths.

Stage-correctness per CLAUDE.md: empirical β-estimate (Stage 1) independent of Panoptic deployment liquidity. On-chain measurement of E_T does NOT require live LP capital; only deployment does. **This is Stage 1 work.**

## Gaps

1. Castle Island EM Stablecoin Survey (Sept-2024) PDF parse failed — Colombia sub-sample + explicit wage-receipt %. **Single most important next-step fetch**
2. Per-org Deel deposit addresses — no public registry; heuristic clustering needed
3. Bitwage funder/router addresses — direct Paystand/Bitwage outreach would yield order-of-magnitude improvement
4. Lemon Cash hot-wallet address verification — labeled on Etherscan; specific addresses not enumerated here
5. Wenia address discovery — operates as Bitso custodian per regulatory disclosure
6. Tron USDT Colombia attribution — Tron $12.38B cumulative LATAM stablecoin chain; CO usage vs ETH/Polygon unclear
7. Visa-Allium 2025 stablecoin payments report — not fetched
8. Colombian-resident vs LATAM-resident attribution at Bitso/Lemon — binding methodological gap (20% scalar = rough proxy)
9. Bitwage-specific Colombian volume — $400M+ global; CO share not disclosed
10. Wage cadence detection benchmark — no labeled training set; heuristic detection unvalidated
