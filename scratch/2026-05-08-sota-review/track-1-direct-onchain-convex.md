# Track 1 — Direct on-chain convex hedges

Scope: protocols that mint/route on-chain payoffs which are non-linear in some
underlying (options, power-perpetuals, gamma-bearing LP positions, yield
tokens with convex secondary pricing). Excludes linear savings vaults and
payment rails (Track 2 lane).

## 1. Numo deep-dive

Numo, led by **Robert Leifke** (NYC, Dahlia Labs alum, completing a math
degree, profile at [robertleifke.com](https://www.robertleifke.com/)), is the
benchmark for this entire SOTA — and the most important finding of Track 1 is
that **Numo's current iteration directly overlaps Abrigo's EM-FX positioning,
though not its convex-payoff positioning.**

**Two-phase history.** Numo (originally "Numoen") began in October 2022 as
"the world's first permissionless options exchange," using a CFMM specialised
to the payoff of a perpetual call to deliver squared / power-perpetual
exposure with no liquidations and no expiries — see Leifke's foundational
posts [The World's First Permissionless Options Exchange](https://medium.com/numoen/the-worlds-first-permissionless-options-exchange-498a8625291a)
and [Perpetual Options for DeFi](https://medium.com/numoen/perpetual-options-for-defi-821351c0a24f).
The architectural device is the **Replicating Market Maker (RMM)**: derive
the trading function so the LP's portfolio tracks a chosen payoff
([An introduction to Replicating Market Makers](https://medium.com/numoen/an-introduction-to-replicating-market-makers-de5c44d3c558)).
Subsequent posts ([Building a Hyperstructure](https://medium.com/numoen/building-a-hyperstructure-2fce6dc97d00),
[Liquid Staking Boost](https://medium.com/numoen/announcing-liquid-staking-boost-405b49bf7772),
[Protocol Bank — The Numo Vision](https://medium.com/numocash/protocol-bank-the-numo-vision-e87d47c5efb7))
trace a pivot from squared-options to a "world's bank" stablecoin / lending
thesis.

**Current product (2025–2026).** Per Leifke's site, Numo is now "an AMM for
efficient exchange and hedging of foreign currencies on blockchains," with
an explicit goal to "make FX hedging universally accessible — laying the
foundation for a future supranational currency." The product is **on-chain
FX forwards**, not options. Mechanism: a YieldSpace-inspired curve where
each currency pool encodes a zero-coupon bond / discount factor; pairing two
currency pools (e.g. USD-stable × KES-stable) yields a live implied forward
rate without oracles or credit lines — see the Asia Stablecoin writeup
[The Rise of Stablecoin FX](https://asiastablecoin.substack.com/p/the-rise-of-stablecoin-fx-rebuilding).
Target users: **EM SMBs invoicing in USD but paying local suppliers** — the
canonical wage-earner-adjacent FX-mismatch population.

**On-chain status / artifacts.** Public GitHub repos under
[robertleifke](https://github.com/robertleifke) include
[`forex-swap`](https://github.com/robertleifke/forex-swap) ("Prop market
maker for FX stablecoins," Solidity, Uniswap v4, MIT), `numoen` (LP-share
lending, Solidity), `archer` ("Convex perpetuals on BTC," TypeScript),
`stableswap` (Uniswap v4 stablecoin exchange), `fusion` (Rust orderbook for
physically-delivered futures, last update April 2026), and a fork of Valora's
Celo-native `mobile` wallet — the Valora fork is significant: Valora is the
canonical Celo / Mento mobile entry point Abrigo is also targeting. No public
mainnet deployment of the FX-forward product is documented in the sources
inspected; status reads as **late-testnet / prop-market-making** with active
2026 commits. No funding round is publicly documented; the project appears
solo-/small-team and bootstrapped, with Dahlia Labs as the historical org
shell.

**EM-FX feasibility.** Numo's RMM-on-YieldSpace design is *structurally*
EM-FX-native — it requires only two stablecoin legs and a discount-curve
parameterisation. It does not require Mento; it does not require Panoptic.
This is the cleanest non-Mento, non-Panoptic architecture for EM-FX
on-chain hedging publicly documented as of May 2026.

**Overlap with Abrigo — explicit assessment.**

- **Where Numo collides with Abrigo:** EM-FX-native focus, permissionless
  on-chain venue, wage-earner-adjacent population (SMBs, with mobile-wallet
  experimentation via the Valora fork), open-source, primary-source
  intellectual rigor.
- **Where Numo does NOT collide with Abrigo:** Numo's current product is a
  **forward** (linear in the FX rate, with a discount-curve term structure) —
  not a convex / gamma-bearing payoff. A forward locks rate; it does not
  ratchet wage flow into productive-capital exposure via accumulated convex
  payoff. Numo also does not settle on Panoptic and has no premium-funded
  ratchet narrative. The closest convex artifact in Numo's repo set is
  `archer` ("Convex perpetuals on BTC"), which is a side experiment, not the
  flagship.
- **Net:** Numo is a near-neighbor competitor for the *FX hedging surface*
  but a *non-competitor* for the convex / ratchet surface. Abrigo's
  defensible wedge — convex payoff + premium-funded wage-to-capital ratchet —
  survives the Numo benchmark intact. The risk is Numo bolting an options
  layer onto its FX-forward AMM (the team has the squared-options pedigree to
  do exactly this); see §7.

**Format-reference notes.** Leifke's Medium series — particularly
[An introduction to Replicating Market Makers](https://medium.com/numoen/an-introduction-to-replicating-market-makers-de5c44d3c558)
and [Perpetual Options for DeFi](https://medium.com/numoen/perpetual-options-for-defi-821351c0a24f)
— is the stylistic model Abrigo's public materials should aim at: math-first,
single-thesis-per-post, primary-source citations to Paradigm / Angeris work,
no marketing fluff. The `forex-swap` README and Hyperstructure post are also
short-form templates worth emulating.

## 2. Players & products

| Player | One-line | URL | Status |
|---|---|---|---|
| **Numo** | EM-FX forward AMM via YieldSpace-style discount curve; ex-perpetual-options | [robertleifke.com](https://www.robertleifke.com/) / [github](https://github.com/robertleifke) | testnet / prop |
| **Panoptic** | Perpetual options on Uniswap v3/v4 LP positions; streaming premium | [panoptic.xyz](https://panoptic.xyz/) | live (V1.1, V4 pools) |
| **Opyn (Squeeth)** | ETH² power-perpetual; pure gamma | [paradigm.xyz Power Perpetuals](https://www.paradigm.xyz/2021/08/power-perpetuals) | live but low-volume; legacy |
| **Premia v3** | Hybrid AMM/orderbook concentrated-liquidity European options | [yellow.com review](https://yellow.com/research/defi-options-trading-in-2025-how-lyra-dopex-and-panoptic-are-reshaping-derivatives) | live (Arbitrum) |
| **Derive (ex-Lyra)** | Full L2 derivatives stack: options, perps, vaults | [derive.xyz](https://www.derive.xyz/) | live (>$100M TVL) |
| **Aevo (ex-Ribbon)** | Off-chain matching, on-chain settle; options + perps + DOVs | [aevo.xyz](https://www.aevo.xyz/) | live; legacy Ribbon vaults exploited Dec-2025 ([The Block](https://www.theblock.co/post/382461/aevos-legacy-ribbon-dov-vaults-exploited-for-2-7-million-following-oracle-upgrade)) |
| **Stryke (ex-Dopex)** | CLAMM options on concentrated liquidity; SSOVs sunset Feb-2024 | [docs.dopex.io](https://docs.dopex.io/single-staking-options-vault-ssov) | live (CLAMM); SSOV deprecated |
| **Pendle** | PT/YT yield tokenisation; YT is convex on yield | [docs.pendle.finance](https://docs.pendle.finance/pendle-v2/ProtocolMechanics/YieldTokenization/YT) | live; sPENDLE in 2026 |
| **Hegic** | Peer-to-pool ETH/wBTC options on Arbitrum | [hegic.co](https://www.hegic.co/) | live, low activity |
| **IPOR** | On-chain interest rate swaps | [docs.ipor.io](https://docs.ipor.io/interest-rate-derivatives/interest-rate-derivative) | live; postmortem-flagged ([SCapital](https://scapital.medium.com/ipor-a-postmortem-for-the-interest-rate-swap-pioneer-5dc8492c2f7c)) |

Dropped from seed list as off-scope: **Pods** (LATAM-team but linear /
structured-product orientation; revisit Track 2). **Ribbon** absorbed into
Aevo per [RGP-33](https://gov.ribbon.finance/t/rgp-33-merge-ribbon-finance-into-aevo/709).

## 3. Mechanism table

| Player | Payoff shape | Yield source | FX exposure | Settlement venue |
|---|---|---|---|---|
| Numo | Linear forward (FX rate) | LP curve fees | Native (any stablecoin pair) | Own AMM (Uniswap v4 hooks) |
| Panoptic | Long/short gamma; constant-gamma between strikes | Streaming premium from Uni v3/v4 LP fees | Any pair tradeable on Uni v3/v4 | Uniswap v3/v4 pool ([docs](https://panoptic.xyz/docs/contracts/smart-contracts-overview)) |
| Opyn Squeeth | x² power perpetual (pure gamma) | Funding rate (mark − payoff) | ETH-only effectively | Own contracts on Ethereum |
| Premia v3 | European calls/puts | Concentrated-liquidity LP fees + premia | Crypto-native | Own AMM/orderbook (Arbitrum) |
| Derive | Calls/puts + perps + structured | Maker spreads, vault premia | Crypto-native | OP-stack L2 |
| Aevo | Calls/puts, perps, DOV covered-call | Sold-option premium | Crypto-native | Off-chain match, on-chain settle |
| Stryke | CLAMM call/put | LP premium yield | Crypto-native | Arbitrum |
| Pendle | YT (decay convex on yield), PT (linear) | Underlying yield strip | Indirect (yield-bearing stables) | Own AMM |
| Hegic | American-style call/put | Pool premia | ETH/wBTC | Arbitrum |
| IPOR | IRS receiver/payer (linear in rate) | Funding-rate basis | None (rate, not FX) | Own AMM |

## 4. Coverage of Abrigo thesis components (7-axis scoring)

| Player | Permissionless | Convex | EM-FX-native | Wage-earner accessible | Premium-funded ratchet | Open-source | Numo-rigor (0–5) |
|---|---|---|---|---|---|---|---|
| **Numo** | Y | N (forward) | Y | partial (SMB-targeted, mobile-wallet fork) | N | Y | **5** |
| **Panoptic** | Y | Y | partial (any Uni pair, but no EM-FX deployment) | partial (small ticket, but UX is pro-trader) | partial (streaming premium ≠ ratchet) | Y ([panoptic-v1-core](https://github.com/panoptic-labs/panoptic-v1-core)) | 5 |
| **Opyn Squeeth** | Y | Y (pure gamma) | N | partial | N | Y | 4 |
| **Premia v3** | Y | Y | N | N (sophisticated traders) | N | Y | 4 |
| **Derive** | partial (KYC paths) | Y | N | N | N | partial | 3 |
| **Aevo** | partial (off-chain match) | Y | N | N | partial (DOV premium) | partial | 3 |
| **Stryke** | Y | Y | N | partial | partial (CLAMM LP premium) | Y | 3 |
| **Pendle** | Y | partial (YT convex on yield) | N | partial | partial (YT decay vs. yield realised) | Y | 4 |
| **Hegic** | Y | Y | N | partial | N | Y | 2 |
| **IPOR** | Y | N | N | N | N | Y | 3 |

Numo-rigor is anchored: Numo = 5 by construction; Panoptic = 5 because of
explicit pricing-model rigor ([How to Price Perpetual Options](https://panoptic.xyz/research/perpetual-option-pricing-model-comparison),
[Block Scholes × Panoptic](https://www.blockscholes.com/research/block-scholes-x-panoptic-perpetual-option),
[Code4rena Next-Core audit](https://code4rena.com/audits/2025-12-panoptic-next-core)).

## 5. Gaps Abrigo fills

- **No player offers a wage-stream → productive-capital ratchet.** All convex
  payoffs in this cluster are speculative or hedging, denominated in
  crypto-native risk (ETH, BTC) or held as covered-call yield. None route a
  recurring small-ticket premium from a wage stream into accumulating convex
  exposure that crosses the wage / capital boundary.
- **No player combines convex payoff WITH EM-FX-native settlement.** Numo
  has EM-FX, no convexity. Panoptic has convexity, no EM-FX deployment.
  Squeeth has convexity, ETH-only.
- **No player targets a Colombia-first / LATAM / Africa-secondary wage
  earner persona.** Stryke / Premia / Derive / Aevo target pro traders;
  Pendle targets yield farmers; Hegic targets retail crypto. Mobile-first
  EM UX is absent across the cluster (Numo's Valora fork is the only signal,
  and it is not productised).
- **Post-Keynesian inequality framing is absent.** This is a positioning
  asset, not a technical one, but it gives Abrigo a distinctive narrative
  axis no competitor in this cluster contests.

## 6. Partnership / integration candidates

- **Panoptic.** Native settlement venue per the Abrigo thesis. Concrete
  sketch: Abrigo's M-design step parameterises a Panoptic position (strike
  range, gamma profile, premium streaming rate) on a Mento-stable / USDC
  pool; Abrigo wraps the Panoptic position in a wage-stream-friendly
  recurring-premium contract. Panoptic V2 beta (per [ETHDenver 2026 recap](https://panoptic.xyz/blog/panoptic-launches-on-uniswap-v4))
  + V4 hook permissions are the integration surface.
- **Numo.** Two-way: (a) consume Numo FX-forward curves as the linear
  delta-hedging leg under an Abrigo convex overlay; (b) provide Numo with
  the EM wage-earner distribution channel its FX-forward AMM lacks.
- **Pendle.** YT on a yield-bearing EM-stable (e.g. yield-bearing cUSD,
  cKES) gives a convex-on-yield leg that composes with Abrigo's convex-on-FX
  leg to construct multi-factor wage-earner ratchets.
- **Mento (Track 4 boundary).** Out of Track 1 scope but the natural
  denomination layer.

## 7. Risk: who could pivot into our lane

- **Numo (highest risk).** Already EM-FX-native, already has the RMM
  toolkit to replicate non-linear payoffs (the entire Numoen pedigree was
  squared-options), and has a Valora fork suggesting wage-earner UX
  experimentation. If Leifke layers a perpetual-options curve on top of the
  FX-forward AMM and ships a mobile entry point, the overlap with Abrigo
  would become near-total. Mitigation: ship Panoptic-settled M-design and
  the premium-funded ratchet narrative before Numo bolts an options layer
  onto `forex-swap`.
- **Panoptic.** Owns the convex venue Abrigo plans to settle on. If
  Panoptic ships first-party EM-FX pool templates + a recurring-premium SDK,
  the gap closes. Mitigation: stay an *application* on Panoptic, not a
  competitor; lock in distribution via the wage-earner UX layer Panoptic is
  unlikely to build.
- **Pendle.** YT is structurally a convex bet. A Pendle market on a
  yield-bearing EM stablecoin would compose with wage-stream entry — but
  Pendle's UX, language, and target audience are yield farmers, not EM wage
  earners. Mitigation low-cost: stay UX/distribution-differentiated.
- **Stryke / Premia / Derive / Aevo.** Low pivot risk — wrong audience,
  wrong denomination, wrong narrative. Would need a complete strategic
  reorientation.

The defensible Abrigo wedge across this cluster is the **intersection** of:
convex payoff (Panoptic-settled) × EM-FX denomination (Mento / USDC
Panoptic-eligible) × wage-stream premium-funded ratchet (recurring small
ticket UX) × post-Keynesian inequality framing. No single competitor in
Track 1 occupies that intersection as of May 2026; Numo is the only one that
could plausibly arrive there within 6–12 months.
