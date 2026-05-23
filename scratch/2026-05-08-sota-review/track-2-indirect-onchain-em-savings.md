# Track 2 — Indirect on-chain EM savings / FX vaults

Scope: indirect on-chain competitors that solve "protect my wage from local-FX
debasement" via *linear* mechanisms — passive stable holding, yield-bearing
stables, lending vaults, LP-as-savings, gamified hodl pools. They compete for
EM wage-earner wallet share with Abrigo but do not provide convex payoffs and
do not operate a premium-funded ratchet. Direct convex/options protocols
(Numo, Panoptic, Stryke, etc.) are deliberately excluded — they belong in
Track 1. Off-chain fintechs (Wise, Nubank, Bitso fiat side, etc.) belong in
Track 3.

## 1. Players & products

| Player | One-line | URL | Status | EM corridors covered |
|---|---|---|---|---|
| Mento Protocol | Decentralized multi-currency stable family on Celo (cUSD, cEUR, cREAL, cCOP, cKES, cNGN, cGHS, cZAR, cGBP, cCHF, cAUD, cCAD, cJPY, PUSO, eXOF) over-collateralized 110% by USDC/DAI/BTC/ETH/CELO reserve | [mento.org](https://www.mento.org) / [docs](https://docs.mento.org/mento-v3/build/repository-overview) | Live; ~$20B annualized volume; 7M+ users | COP, BRL, KES, NGN, GHS, ZAR, EUR, USD, XOF, PHP |
| Glo Dollar (USDGLO) | Brale-issued, fiat-backed USD stablecoin that donates 100% of reserve yield to GiveDirectly basic-income recipients | [glodollar.org](https://www.glodollar.org) / [CoinGecko](https://www.coingecko.com/en/coins/glo-dollar) | Live on Celo, Ethereum, Polygon, Optimism, Base | USD-denominated public goods; modest Celo Uniswap V3 liquidity |
| HaloFi (ex-GoodGhosting) | Gamified gas-pool savings: deposit cUSD weekly, miss a deposit → forfeit principal share to consistent savers; yield from underlying Aave/Moola | [halofi.me](https://halofi.me) / [docs](https://docs.halofi.me) / [GitHub](https://github.com/Good-Ghosting/goodghosting-protocol-v2) | Live on Celo + Polygon; cUSD pools recurring | USD-stable on Celo |
| Aave V3 on Celo | Money-market lending; supply USDC/USDT/cUSD/CELO and earn variable yield, or borrow against collateral | [aave.com](https://aave.com) / [DefiLlama](https://defillama.com/protocol/aave-v3) | Live on Celo since L2 migration (Mar 2025) | USD-stable supply/borrow; no native EM-FX market |
| Moola Market | Aave-fork lending on Celo supporting CELO, cUSD, cEUR | [moola.market](https://moola.market) / [DefiLlama](https://defillama.com/protocol/moola-market) | Live but TVL ~$1.2M, declining | USD- and EUR-stable on Celo |
| Ubeswap | Uniswap-v2/v3 fork on Celo; LP positions in cUSD/USDC, cEUR/cUSD, cREAL/cUSD function as de-facto savings via fees | [ubeswap.org](https://ubeswap.org) / [docs](https://docs.ubeswap.org) | Live; Stablecoin-Summer V3 farms | cUSD, cEUR, cREAL, USDC pairs |
| BRLA Digital (BRLA) | Audited BRL-pegged stablecoin issued by Avenia; on/off-ramp via Brazilian PIX | [brla.digital](https://brla.digital/brlatoken) / [Avenia](https://avenia.io/brla) | Live; growing rapidly post-BCB Resolutions 519/520/521 (Feb 2026) | BRL — Brazil retail/business |
| Transfero BRZ | Largest non-USD stablecoin; ~$185M mcap; multi-chain (incl. Celo) | [transfero.com/stablecoins/brz](https://transfero.com/stablecoins/brz/) / [RWA.xyz](https://app.rwa.xyz/assets/BRZ) | Live; BCB-approved as standard BRL stable | BRL — Brazil dominant |
| BBRL / BRD / BRL1 | Newer BRL-pegged variants (BBRL ~$51M; BRD yield-bearing tied to Brazil sovereign debt; BRL1 backed by Mercado Bitcoin + Bitso consortium) | [coindesk BRD](https://www.coindesk.com/business/2026/01/07/former-brazil-central-bank-official-unveils-real-pegged-stablecoin-with-yield-sharing) | BRD launched Jan 2026; BRL1 LATAM-exchange backed | BRL |
| Stasis EURS | Fiat-backed EUR stablecoin since 2018; ~$150M mcap pre-March-2026 | [stasis.net/eurs-info](https://stasis.net/eurs-info) | Live but **depegged repeatedly Mar–Apr 2026** (–32% to $0.82, +47% to $1.21) | EUR (degraded reliability) |
| Ondo USDY | Yield-bearing tokenized note backed by short-duration US Treasuries; ~4.65% APY; non-US holders only | [ondo.finance/usdy](https://ondo.finance/usdy) / [RWA.xyz](https://app.rwa.xyz/assets/USDY) | Live; ~$740M supply across ETH/SOL/Mantle/Sui/Aptos | USD-yield to non-US retail; no LATAM or Africa rails |
| re.al | EVM L2 specialized for tokenized real-world assets (real estate, T-bills) with a USD-stable settlement | [re.al](https://re.al) | Live; small TVL; not Celo-aligned | USD/EUR RWA exposure |
| Kotani Pay | Africa on/off-ramp connecting Web3 to local currencies; cKES microcredit pilot | [kotanipay.com](https://kotanipay.com) | Live; 1M+ cKES distributed to 150 microentrepreneurs | KES, UGX, GHS, NGN, ZAR — wage rails |

Cut from list: re.al receives only a stub line — it is a chain-as-product, not
an EM-savings instrument; included for completeness because the seed list
named it.

## 2. Mechanism table

| Player | Mechanism | Yield source |
|---|---|---|
| Mento cStables | Mint/redeem against over-collateralized reserve; FPMM pools rebalance vs USDC/CELO/BTC/ETH; users hold cCOP/cKES/cREAL passively to track local fiat | None at the stable-coin layer (yield must come from external lending or LP) |
| Glo Dollar | Passive 1:1 USD stable; yield captured by issuer and donated, NOT paid to holder | None to holder (charity yield) |
| HaloFi | Active commitment: weekly cUSD deposit; principal earns Aave/Moola yield; forfeitures redistributed to compliant savers | Aave/Moola lending APY + redistributed forfeitures |
| Aave V3 / Moola | Passive supply yield from variable-rate borrowing pool | Borrower interest (USD-stable APY 2–6%) |
| Ubeswap LP | Active LP in stable pairs; earn 0.05–0.30% swap fees + UBE incentives | Trading fees + token rewards |
| BRLA / BRZ / BBRL / BRL1 | Passive 1:1 BRL stable; on/off-ramp via PIX; pure FX-tracking | None at coin layer; BRD is yield-bearing via Brazil sovereign debt |
| Stasis EURS | Passive 1:1 EUR stable | None |
| Ondo USDY | Yield-bearing T-bill note; price accretes from ~4.65% APY | Short-duration US Treasuries + bank deposits |
| re.al | Tokenized RWA exposure | RWA cash flows |
| Kotani Pay | Off/on-ramp + microcredit; not a savings vault per se | N/A (rail) |

All of these are *linear* in the underlying. None deliver gamma. None convert
recurring premium into ratcheting capital exposure.

## 3. Coverage of Abrigo thesis components (7-axis scoring)

Permissionless = anyone can mint/use without KYC at the smart-contract layer.
Convex = nonlinear (gamma-positive) payoff. EM-FX-native = denominated in or
referencing EM currency. Wage-earner accessible = mobile UX + low minimums +
local on/off-ramp. Premium-funded ratchet = small recurring premium converts
to larger capital exposure over time. Open-source = code public + permissive.
Numo-rigor (0–5) = design-architecture/payoff-expressiveness/composability/docs
quality benchmarked against [Numo](https://github.com/numoen) (Robert Leifke's
work on Replicating Market Makers and uniform LP geometry).

| Player | Permissionless | Convex | EM-FX-native | Wage-accessible | Premium ratchet | Open-source | Numo-rigor |
|---|---|---|---|---|---|---|---|
| Mento (cCOP/cKES/cREAL/eXOF) | Yes | No | **Yes** (15 currencies) | Yes (mobile rails) | No | Yes ([mento-core](https://github.com/mento-protocol/mento-core)) | **3.5** — strong V3 FPMM + BreakerBox + reserve docs, but linear by design |
| Glo Dollar | Partial (Brale-issued) | No | No (USD only) | Partial | No | Partial | 1 |
| HaloFi | Yes | No (commitment device, not gamma) | No (cUSD-denom) | Yes (mobile) | **Partial** — gamification *is* a recurring-deposit ratchet but linear in payoff | Yes ([GG-v2](https://github.com/Good-Ghosting/goodghosting-protocol-v2)) | 2.5 |
| Aave V3 on Celo | Yes | No | No | Partial | No | Yes | 4 (general DeFi rigor; not EM-tailored) |
| Moola | Yes | No | No | Partial | No | Yes | 2 |
| Ubeswap | Yes | No (LP is concave, not convex) | Partial (cREAL/cCOP/cKES pools exist) | Partial | No | Yes | 2 |
| BRLA | No (regulated issuer) | No | **Yes** (BRL) | Yes (PIX) | No | No | 1.5 |
| Transfero BRZ | No | No | **Yes** (BRL) | Yes | No | No | 1.5 |
| BRD (yield-bearing real) | No | No | **Yes** | Partial | No (yield, not ratchet) | No | 2 |
| Stasis EURS | No | No | EUR (off-thesis) | No | No | No | 1 |
| Ondo USDY | No (KYC, non-US only) | No | No | No (institutional/HNW) | No | No | 3 |
| re.al | Yes | No | No | No | No | Partial | 2 |
| Kotani Pay | No (custodial rail) | No | **Yes** (KES/UGX/GHS) | **Yes** (top wage-earner UX) | No | No | 1.5 |

No player approaches Numo's level (≥4.5) on payoff-expressiveness because none
of them attempt gamma. Mento ranks highest on infrastructure rigor — its V3
FPMM (Functional Pool Market Maker) repository, BreakerBox circuit breakers,
TradingLimitsV2, and the [reserve site](https://github.com/mento-protocol/reserve-site)
publishing live collateralization data are the most architecturally serious
artifacts in this cluster ([repository overview](https://docs.mento.org/mento-v3/build/repository-overview)).

## 4. Wallet-share overlap with Abrigo target

**Colombia (priority).** A Colombian wage earner trying to hedge COP debasement
today has an extremely thin on-chain menu. cCOP launched on Mento ([launch
post](https://www.mento.org/blog/announcing-the-launch-of-ccop---celo-colombia-peso-decentralized-stablecoin-on-the-mento-platform))
but circulating supply and DEX depth remain small relative to USDC dominance
on Colombian exchanges. The dominant pattern is: convert wage COP → buy USDT
or USDC on Bitso/Binance/Buenbit → hold passively. cCOP's primary use is
remittance and merchant payment, not savings accumulation. There is **no
Colombian-specific yield product on-chain** — Aave-on-Celo, Moola, and Ubeswap
all default to USD-stable supply or USDC/cUSD LP. This is a wide-open lane
for Abrigo's premium-funded COP/USD convex hedge.

**Brazil.** The richest field. BRZ ([Transfero](https://transfero.com/stablecoins/brz/),
~$185M mcap), BRLA (Avenia/[BCB-resolution-aligned](https://www.mexc.com/news/1055469)),
BBRL (~$51M), BRL1 (Mercado Bitcoin + Bitso consortium), and the new
yield-bearing BRD ([CoinDesk](https://www.coindesk.com/business/2026/01/07/former-brazil-central-bank-official-unveils-real-pegged-stablecoin-with-yield-sharing))
plus cREAL on Mento. PIX integration is deep. Brazil retail's stablecoin
wallet share is overwhelmingly USD-stable: BCB reports 98% of $6.9B Q1-2026
overseas crypto purchases were stablecoins, with USD-stables dominant even
inside Brazil. So BRL stables are an **off-ramp** more than a savings store;
holders exit BRL into USDC/USDT for the FX-debasement hedge function. Abrigo
overlaps the same impulse but offers convexity instead of linear USD parity.

**Africa (Kenya-anchor).** [cKES](https://www.mento.org) on Mento + Kotani Pay
microcredit pilot ([Chaintum profile](https://chaintum.io/2024/10/23/heres-how-kotani-pay-is-shaking-up-cross-border-payments-in-africa-with-a-splash-of-stablecoins/))
is the most wage-earner-shaped infrastructure in the cluster. cKES distribution
to 150 microentrepreneurs is small but *actually serves the target persona*.
Africa wage earners use mobile-money-on-ramped USD-stables (USDC/USDT) on Tron
and Celo overwhelmingly; cNGN / cGHS / cZAR exist but are thin.

**On/off-ramp realities.** Colombia: Bitso, Binance P2P, Buenbit, El Dorado
(Lightning). No frictionless cCOP fiat ramp at retail scale. Brazil: PIX → BRLA
or BRZ is ~30-second, regulated. Kenya: M-Pesa → cKES via Kotani Pay or
Yellowcard. The Colombia ramp gap is the single largest practical constraint
on Abrigo's target population.

## 5. Gaps Abrigo fills

This entire cluster is **linear by construction**:

1. **No convex payoff.** Holding cCOP, BRZ, USDY, or supplying to Aave gives
   1:1 (or 1:1 + APY) exposure. There is no path by which a small recurring
   premium *expands* into a leveraged stake on macro-risk realization.
2. **No premium-funded ratchet.** HaloFi gamifies recurring deposits but the
   payoff is the principal back plus stable yield — there is no productive-
   capital crossing. The wage earner ends with the same risk class they
   started with.
3. **No EM-macro-risk underlying.** cCOP tracks COP. It does *not* monetize
   COP/USD vol, BPO offshoring exposure, or the Section-J labor-share gap.
   Abrigo's β = +0.137 result on Pair D (BPO offshoring × COP/USD lag) is
   un-replicable inside Mento's stable family.
4. **No wage→productive-capital boundary crossing.** All cluster products keep
   the holder inside the wage/savings stratum. Abrigo's thesis is precisely
   that pure-savings cannot cross the boundary; only convex premium-funded
   exposure can.
5. **Linear yield is depeg-fragile.** Stasis EURS's repeated 25–32% Mar–Apr
   2026 deviations ([blockchainmagazine](https://blockchainmagazine.com/breaking-news/breaking-eurs-plunges-2026-04-02/))
   illustrate that a "safe" linear stable can deliver wage-destroying drawdowns
   without any upside compensation. A convex hedge would have monetized exactly
   this volatility.

## 6. Partnership / integration candidates

**Mento as denomination layer (highest priority).** Mento V3's FPMM and
oracle adapters ([mento-core](https://github.com/mento-protocol/mento-core))
expose cCOP/cKES/cREAL as natively settleable units. Abrigo Panoptic positions
denominated in cCOP/USDC, cKES/USDC, or cREAL/USDC would inherit Mento reserve
backing for the EM-FX leg. Concrete sketch: Panoptic perpetual put on a
cCOP/USDC Uniswap-v4 pool deployed on Celo, premium streamed in cCOP from the
holder's wage wallet.

**Glo Dollar as USD reference + ESG narrative.** USDGLO yield-to-charity story
aligns with Abrigo's inequality-minimization thesis. Use as the USD leg in
USDGLO/cCOP Panoptic pools when public-goods alignment is a marketing axis.

**Aave V3 on Celo as collateral source.** Premium reserves from Abrigo
holders idle between roll dates; supply to Aave-on-Celo in cUSD/USDC for base
APY; ensures the *unused* premium float does not sit dead. Composable with
Mento mint/redeem for in-kind premium settlement.

**HaloFi as recurring-deposit UX precedent.** Their cUSD weekly-deposit gas-
pool UX is the closest existing primitive to Abrigo's premium-funding pattern.
Worth studying their forfeiture mechanic ([GG-v2 contracts](https://github.com/Good-Ghosting/goodghosting-protocol-v2))
as a template for premium-default handling — what happens when a wage earner
misses a premium roll.

**Kotani Pay as Africa on/off-ramp.** For cKES-denominated Abrigo deployments,
Kotani's M-Pesa rail is the only credible last-mile. Partnership sketch: Kotani
handles KES → cKES conversion + premium streaming; Abrigo contracts handle the
Panoptic position.

**BRLA / BRZ as Brazil ramp.** When Abrigo extends to a BRL/USD convex
instrument, BRLA's PIX ramp is the path. Co-marketing with the BCB-clarified
regulatory frame ([Resolutions 519–521](https://www.mexc.com/news/1055469)).

**Ubeswap as Celo-native DEX for premium swaps.** When Panoptic itself is not
on Celo, Ubeswap V3 stable pools provide the rebalancing layer between cCOP
and USDC for premium-routing.

## 7. Risk: who could pivot into our lane

**Mento Labs.** Highest pivot risk. They already operate FPMM pools, oracle
adapters, BreakerBox circuit breakers, and a TradingLimitsV2 system — half
the apparatus needed for derivative settlement. If Mento extended its V3
architecture with an options-like overlay (writing covered calls against
reserve assets, or issuing convex receipts on cStable demand surges), they
could enter Abrigo's lane. Constraints: governance conservatism, reserve
mandate is "back stables" not "underwrite gamma." Probability medium-low; if
it happens it will be slow.

**HaloFi.** Conceptually closest in UX (recurring deposits → outcome). Could
conceivably layer a convex bet on missed-deposit forfeitures. But their team
shape (consumer-savings-app) and the absence of options-pricing rigor in their
docs make this unlikely without a complete repositioning.

**BRD (yield-bearing real).** Already innovating on the BRL stable yield axis
with sovereign-debt linkage. Path to convex would require an options or rates-
derivative wrapper on Brazilian sovereign yield — possible but requires a
different regulatory posture.

**Ondo Finance.** Has the financial-engineering depth and tokenized-treasury
distribution. Could in principle launch tokenized convex products. But their
regulatory posture (non-US, KYC, accredited) is incompatible with Abrigo's
permissionless wage-earner persona. Low pivot risk *into Abrigo's lane*; high
risk of *capturing the institutional adjacent lane*.

**Aave V4 Spokes.** Aave V4's hub-and-spoke architecture (mainnet 30 March
2026, [CoinDesk](https://www.coindesk.com/tech/2026/04/19/aave-records-usd6-billion-tvl-drop-as-kelp-hack-exposes-structural-risk-at-defi-lender))
explicitly supports modular collateral types. A "convex EM-FX spoke" is
architecturally feasible. Probability low (Aave's risk DAO is conservative)
but the rails would support it.

**Net assessment.** No Track-2 incumbent currently has both (a) the options-
pricing rigor and (b) the EM-wage-earner UX to credibly compete on the
premium-funded ratchet. Mento is the only one that could supply infrastructure
plumbing fast enough to matter; the strategic move is to integrate Mento as
denomination layer *before* they consider building a competing overlay
themselves.

## Notes on Numo-rigor scoring

[Numo](https://github.com/numoen) (Robert Leifke et al.) sets the SOTA on
payoff-expressiveness with replicating market-maker work, uniform-LP geometry,
and rigorous Foundry-tested invariants. Against that bar, Track 2 caps at ~4
(Aave V3, on general DeFi rigor) and 3.5 (Mento V3, on EM-stable infrastructure
rigor). Linear-savings products *should* score low here — the index is
measuring depth of payoff design, which is precisely what Abrigo brings and
this cluster does not.

Sources cited inline above.
