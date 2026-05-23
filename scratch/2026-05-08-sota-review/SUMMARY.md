# Abrigo SOTA / Competitive Landscape — Synthesis

**Date:** 2026-05-08
**Inputs:** `track-1-direct-onchain-convex.md`, `track-2-indirect-onchain-em-savings.md`, `track-3-indirect-offchain-fintech.md`, `track-4-hackathon-academic.md`
**Benchmark:** Numo (Robert Leifke) — triple role (peer, scoring axis, format reference)

---

## TL;DR — three signals

1. **The intersection is empty.** No single competitor — across 50+ players surveyed — occupies the cross-product of *convex payoff × EM-FX-native × wage-earner-accessible × premium-funded ratchet × open-source × permissionless*. Numo owns convex+architecture but is now linear-FX-forwards. Mento owns EM-FX denomination but is linear-by-construction. HaloFi/Kotani own wage-earner UX but no convexity. Track 4's literature scan finds the cross-product **also empty in academic and hackathon prior art**.
2. **The Numo wedge survived the benchmark.** Numo pivoted from squared/perpetual options (2022 "permissionless options exchange" thesis) to an EM-FX **forward** AMM (2025–26 "market maker for global payments"). Forwards are linear; Abrigo's convex + premium-funded ratchet wedge survives intact. The Numoen→Numo rebrand is itself a *cautionary signal*: payoff-first protocols without population-targeted (Y, X) discipline drift away from their original thesis. Abrigo's (Y, M, X) framework is structurally the correction.
3. **The competitive moat is split.** *Mechanism* moat is real — no one combines convex, EM-FX, and ratchet. *Distribution* moat is not — closed-source LATAM/Africa fintechs (Nubank, Bitso, Littio, Yellow Card) own the wage-earner UX. Abrigo's correct posture is **partner with the on-ramps; out-design the incumbents on the open-source convex EM-FX-native ratchet axis they structurally cannot match**.

---

## 1. Executive map (2×2)

```
                                  CONVEX PAYOFF
                                       ▲
                                       │
   Track 1 — Direct on-chain convex    │
   (≠ EM-FX, ≠ wage-earner accessible) │
                                       │
   • Panoptic              • Numo's    │
     (V4 pools, gamma)       Archer    │
   • Opyn Squeeth            (BTC      │
   • Premia v3               experiment│  ← Abrigo's
   • Derive / Aevo           — paper)  │     target
   • Stryke / Hegic                    │     quadrant
   • Pendle YT (partial)               │     (EMPTY)
                                       │
                                       │
   ON-CHAIN ◄─────────────────────────┼─────────────────────────► OFF-CHAIN
                                       │
                                       │
   Track 2 — Indirect on-chain         │  Track 3 — Indirect off-chain
   (EM-FX, but linear)                 │  (UX-strong, but linear, custodial)
                                       │
   • Mento cStables (cCOP/cBRL/cKES)  │  • Littio (CO)   • Nubank USDC
   • Aave V3 on Celo                   │  • Bold (CO)     • Bitso+ (LATAM)
   • Ubeswap LP                        │  • Belo (AR)     • Lemon Earn (AR)
   • HaloFi (commitment ratchet)       │  • Buenbit (AR)  • Yellow Card (AF)
   • BRLA / BRZ / BRD                  │  • Risevest (NG) • Cowrywise (NG)
   • Glo Dollar                        │  • Valiu (CO/VE) • Chipper (AF)
   • Kotani Pay (rail)                 │  • OpenTrade (BR/CO/AR T-bill rails)
                                       │
                                       ▼
                                LINEAR PAYOFF
```

**The upper-right quadrant is Abrigo's.** It is empty in May 2026.

---

## 2. 7-axis differentiation table

Cluster-level scores across the four tracks. Y = strong; ~ = partial; N = absent.

| Axis | Track 1 (direct convex) | Track 2 (on-chain EM savings) | Track 3 (off-chain fintech) | Track 4 (hackathon) | **Abrigo (target)** | **Numo (current)** |
|---|---|---|---|---|---|---|
| Permissionless | Y | Y | N | Y | **Y** | Y |
| Convex payoff | Y | N | N | N | **Y** | N (was Y in 2022) |
| EM-FX-native | N | Y | ~ | ~ | **Y** | Y |
| Wage-earner accessible | N | ~ | Y | ~ | **Y** | ~ (SMB) |
| Premium-funded ratchet | N | N (HaloFi partial) | N (Cowrywise/Risevest closest) | N | **Y** | N |
| Open-source | Y | Y | N | Y | **Y** | Y |
| **Numo-rigor (0–5)** | **2–5** (Numo, Panoptic = 5) | **1–4** (Mento 3.5, Aave 4) | **0–2** (ceiling 2) | **0–5** (Numo 5; rest ≤ 2) | **5 (target)** | **5** |

**Read.** Abrigo is the only design specification that hits every axis. Every cluster has at least one structural N. Track 3's Numo-rigor ceiling of 2 is the most diagnostic single number in this entire review: it tells us no off-chain fintech can credibly compete on mechanism transparency.

---

## 3. Abrigo ↔ Numo: overlap, divergence, composition

### Overlap (real)
- **Permissionless on-chain venue.** Both are non-custodial, code-public, KYC-free at the contract layer.
- **EM-FX-native focus.** Numo's current `forex-swap` Uniswap V4 hook is the cleanest non-Mento, non-Panoptic architecture for on-chain EM-FX hedging publicly documented as of May 2026.
- **Wage-earner-adjacent population pull.** Numo's Valora (Celo) mobile-wallet fork is the only Track-1 signal of mobile wage-earner UX experimentation. Abrigo and Numo target structurally similar populations even if Numo's stated audience is "EM SMBs invoicing in USD."
- **Open-source + Angeris-circle CFMM-replication theory.** Both descend from Replicating Market Makers (arXiv:2103.14769) and Replicating Monotonic Payoffs Without Oracles (arXiv:2111.13740).
- **Format / methodology.** Leifke's Medium essays are the stylistic model Abrigo's public materials should aim at — math-first, single-thesis, primary-source citations, no marketing fluff.

### Divergence (defensible)
- **Payoff geometry.** Numo's current product is a **forward** (linear in FX rate, with a discount-curve term structure). A forward locks rate; it does not ratchet wage flow into productive-capital exposure via accumulated convex payoff. Abrigo's convex + Panoptic-settled position is structurally distinct.
- **Ratchet mechanism.** Numo offers FX hedging *as a service*. Abrigo offers a *premium-funded ratchet* — recurring small premium → accumulated convex exposure → wage→capital boundary crossing. Numo has no equivalent narrative or instrument.
- **Settlement venue.** Numo settles on its own AMM (V4 hook). Abrigo settles on Panoptic (perpetual options on Uniswap V3/V4 LP positions). Different settlement primitives with different liquidity surfaces.
- **Population framing.** Numo targets EM SMBs. Abrigo targets EM wage earners and frames the problem in **post-Keynesian distribution** terms — distribution is institutionally determined, the wage→capital boundary is institutional, not equilibrium-given. Numo is silent on inequality framing.

### Composition (under-explored, high-leverage)
- **Numo as linear delta-hedge leg under Abrigo convex overlay.** Consume Numo FX-forward curves to delta-hedge the linear component of an Abrigo Panoptic position; Abrigo retains the gamma/convexity wrapper.
- **Numo as Abrigo M-design reference.** Numo's RMM-on-YieldSpace design is the cleanest existing precedent for parameterising EM-FX positions on-chain. Abrigo's M-design step (the Panoptic-position construction that *would* settle the empirical β if deployed) can borrow Numo's discount-curve approach for any non-Panoptic-eligible legs.
- **Two-way distribution exchange.** Abrigo provides Numo with the EM wage-earner distribution channel its FX-forward AMM lacks; Numo provides Abrigo with the SMB-corridor liquidity its wage-side-only deployment does not bootstrap on its own.

### Net assessment
Numo is a **near-neighbor non-competitor** today and the **highest-probability future competitor** in Track 1 (6–12 month horizon). Mitigation: ship Panoptic-settled M-design for Pair D and the premium-funded ratchet narrative *before* Numo bolts an options layer onto `forex-swap` — they have the squared-options pedigree to do exactly this if their SMB FX-forward thesis stalls.

---

## 4. Top-5 partnership candidates

Ranked by integration leverage × execution feasibility.

1. **Mento Labs — denomination layer.** Mento V3 FPMM + reserve backing for cCOP/cKES/cREAL legs of Panoptic positions. Mento's `mento-core` repo is the most architecturally serious EM-stable infrastructure publicly available; cCOP launched ([Mento blog](https://www.mento.org/blog/announcing-the-launch-of-ccop---celo-colombia-peso-decentralized-stablecoin-on-the-mento-platform)) but yield products on it are absent — Abrigo fills that lane. *Caveat:* Mento is also the highest pivot risk in Track 2; partnership before pivot is the strategic move.
2. **Panoptic — settlement venue.** Native settlement per the Abrigo thesis. Concrete sketch: Abrigo M-design parameterises a Panoptic position on a Mento-stable / USDC pool; Abrigo wraps the Panoptic position in a wage-stream-friendly recurring-premium contract. Panoptic V2 beta + V4 hooks are the integration surface ([Panoptic V4 launch](https://panoptic.xyz/blog/panoptic-launches-on-uniswap-v4)).
3. **Littio + Bitso — LATAM on-ramp.** Both already custody USDC, both already operate PSE/SPEI/PIX rails, both already serve the Colombian/LATAM wage earner. Littio is YC + Circle + Avalanche/OpenTrade-plumbed ([Avalanche blog](https://www.avax.network/blog/colombian-neobank-littio-opentrade-interest-bearing-usd-accounts-avalanche)); Bitso has the broadest LATAM regulatory footprint. Either could white-label "Abrigo convexity unit" as a premium-funded savings tier.
4. **Yellow Card — Africa on-ramp.** First licensed stablecoin operator on the continent; Visa partnership signals appetite for consumer-facing structured products ([Cointelegraph](https://cointelegraph.com/news/visa-yellow-card-stablecoin-payments-africa)). For cKES/cGHS/cNGN-denominated Abrigo deployments, Yellow Card + Kotani Pay are the only credible last-mile pair.
5. **Cowrywise — Africa white-label / population-fit precedent.** Recurring-savings DNA is the closest existing primitive to Abrigo's premium-funding pattern. A white-labeled "Convex Plan" inside Cowrywise would let an Abuja wage earner buy convexity from the most-trusted savings brand they already use. Numo-rigor scoring of 2 means partnership is a structural complement, not a competitive threat.

**Honourable mentions.** OpenTrade (premium-float treasury manager — already plumbed into Littio + Belo), HaloFi (recurring-deposit UX precedent + forfeiture mechanic template for premium-default handling), Aave V3 on Celo (collateral source for idle premium float), IDB Lab / LACChain (policy-cover umbrella for a Colombia pilot — Davivienda has IDB-sandboxed on-chain instrument experience).

---

## 5. Top-3 competitive risks

1. **Numo bolts options onto FX-forward AMM.** The team has the squared-options pedigree (the entire 2022 Numoen thesis), already operates a V4 hook, already has a Valora wallet fork. If Leifke layers a perpetual-options curve on top of `forex-swap` and ships a mobile entry point, the overlap with Abrigo becomes near-total. **Mitigation:** ship Pair-D Panoptic-settled M-design and the premium-funded ratchet narrative on a 3–6 month horizon, before this pivot is plausible. Engage Leifke directly as partnership candidate before he becomes a competitor.
2. **Nubank pivots into long-gamma USDC vs BRL.** 131M users, custodial USDC desk at 4% APY, R$45B Brazil 2026 investment ([BusinessWire](https://www.businesswire.com/news/home/20260427273702/en/Nubank-to-Invest-R$-45-Billion-in-Brazil-in-2026)), banco-múltiplo regulatory footing. A "Nu Hedge" product (long-gamma USDC vs BRL via a partner desk) is the most plausible incumbent pivot. **Mitigation:** open-source mechanism + Mento-native EM-pair coverage Nubank cannot easily reproduce inside a banco-múltiplo wrapper. Brazil is *not* the Colombia-first iteration; let Nubank own BRL while Abrigo locks COP, KES, ARS.
3. **Lemon Cash extends Morpho integration to Panoptic.** Already deploys to Morpho ([Morpho story](https://morpho.org/stories/lemon/)); the leap from Morpho yield to Panoptic premium is small for a team that already thinks in DeFi primitives. Smallest *technical* leap to Abrigo's lane in Track 3. **Mitigation:** partnership conversation before pivot — Lemon as Argentina on-ramp; differentiate by population framing (wage-earner ratchet vs. their crypto-first user base).

**Lower-tier risks.** Bitso (already has the desk + LATAM regulatory footprint — partner before pivot); Mento Labs extending V3 with a derivative overlay (medium-low probability, slow if it happens, governance-conservative); Aave V4 spokes (architecturally feasible "convex EM-FX spoke", low probability — Aave risk DAO is conservative).

---

## 6. Excerptable downstream-use sections

### `[USE:positioning]` — Internal positioning + partnership memo

Abrigo's defensible wedge across the 2026 SOTA is the **intersection** of: convex Panoptic-settled payoff × EM-FX-native denomination × wage-earner-accessible UX × premium-funded ratchet × open-source × permissionless. No competitor in the 50+ players surveyed across direct on-chain convex hedges, indirect on-chain EM savings/FX vaults, indirect off-chain LATAM/Africa dollar fintechs, and hackathon/academic prior art occupies that intersection in May 2026. Numo (the closest peer) is now linear-FX-forwards; Mento is linear-by-construction; Panoptic owns the convex venue but has no EM-FX deployment; closed-source fintechs (Nubank, Littio, Bitso, Yellow Card) own wage-earner UX but cap at delta-1 USD or US-asset baskets. Strategic posture: **partner with the on-ramps, integrate Mento as denomination layer before they consider building a competing overlay, settle on Panoptic as application-not-competitor, and out-design the closed-source fintechs on the one axis they structurally cannot match — open-source convex EM-FX-native ratchet logic inside a SEDPE/sandbox-friendly wrapper.** Top-5 integration candidates: Mento, Panoptic, Littio + Bitso, Yellow Card, Cowrywise. Top-3 competitive risks: Numo bolting options onto `forex-swap`, Nubank entering long-gamma USDC/BRL, Lemon Cash extending Morpho to Panoptic.

### `[USE:grant]` — Accelerator / grant competitive section

The 2026 landscape for permissionless on-chain instruments addressing EM wage-earner capital access splits cleanly into four clusters: (1) direct on-chain convex hedges (Panoptic, Numo, Opyn Squeeth, Premia, Pendle YT) — sophisticated payoff geometries with no EM-FX deployment and no wage-earner UX; (2) indirect on-chain EM savings (Mento cStables, Aave-on-Celo, HaloFi, BRLA/BRZ, Glo Dollar) — EM-FX-native but linear-by-construction, no path from recurring premium to productive-capital exposure; (3) indirect off-chain LATAM/Africa fintechs (Nubank USDC, Littio, Bitso+, Belo, Lemon, Yellow Card, Risevest, Cowrywise) — strong wage-earner UX, closed-source, custodial, delta-1 to USD; (4) hackathon and academic prior art (Celo Proof of Ship 576 projects in 2025, ETHGlobal Buenos Aires Nov 2025, IDB Lab portfolio, post-Keynesian distribution theory, Banerjee-Duflo et al. graduation-program literature) — no shipped or finalist project covers ≥4 of the 7 Abrigo axes. Abrigo is the only design specification that hits every axis: convex, permissionless, EM-FX-native, wage-earner-accessible, premium-funded ratchet, open-source. The Pair-D PASS verdict (β = +0.137, p ≈ 1.5e-08, BPO offshoring × COP/USD lag) provides empirical validation that the underlying microeconomic risk admits a measurable beta on which a Panoptic position would settle cleanly under ideal-scenario liquidity.

### `[USE:academic]` — Related-work section

Abrigo's design intersects four literatures whose joint cross-product has not been previously instantiated. **Post-Keynesian distribution theory** (Lavoie 2014; Hein & Stockhammer 2024; Stockhammer 2022; Kohler, Guschanski & Stockhammer 2018) frames distribution as institutionally determined and identifies financialization as a wage-share-compressing force, motivating Abrigo's reframing of the wage→capital boundary as institutional rather than equilibrium-given. **Household FX-hedging literature in EM** (Dalgıç 2024; Du & Huber 2023; Alfaro et al. HBS 21-096; BIS WP 1303; Chen & Zhou 2025) documents that EM households self-insure via informal dollarization at inferior pricing and that institutional hedging infrastructure is restricted to large investors — supporting the demand-side of Abrigo's thesis. **Microfinance graduation programs** (Banerjee, Duflo et al. 2015 *Science*; Banerjee, Duflo & Sharma 2021 NBER w28074; BRAC PROPEL Toolkit) demonstrate that asset transfers can produce durable capital accumulation for the very poor, but uniformly assume *external grant capital* — Abrigo's premium-funded variant inverts this assumption and is empirically untested in the graduation-program literature. **CFMM-replication and perpetual-options theory** (Angeris, Evans & Chitra arXiv:2103.14769 and 2111.13740; Lambert & Kristensen Panoptic arXiv:2204.14232; Hugonnier, Jermann & Ackerer arXiv:2310.11771; Designing Funding Rates arXiv:2506.08573) provides the technical foundations for the M-design step. The closest existing implementation is Numo (Robert Leifke), which inherits the same Angeris-circle theory but currently delivers linear FX forwards, not convex payoffs, and targets EM SMBs rather than wage earners. Abrigo's contribution is the cross-product of these four literatures: an instrument-financed (premium-funded) ratchet, denominated in EM-FX, settled via convex Panoptic positions, framed in post-Keynesian distributional terms.

---

## 7. Anti-fishing report

Per `CLAUDE.md` carry-forward invariants, this synthesis was checked for silent scope expansion, threshold-tuning of scoring axes after seeing data, and burial of findings that would invalidate Abrigo's positioning. Findings:

- **No scope drift.** The four tracks adhered to their pre-pinned cluster definitions; players that did not fit (Pods, Ribbon-into-Aevo, Mercury B2B-only, generic CEX savings) were dropped, not folded in.
- **Scoring axes pinned before dispatch.** The 7-axis schema (permissionless / convex / EM-FX-native / wage-earner-accessible / premium-funded ratchet / open-source / Numo-rigor) was fixed in `DESIGN.md` before any agent ran. No axis was added, removed, or renamed mid-stream.
- **Refutation candidates surfaced explicitly.** Numo's 2025–26 EM-FX pivot is the most plausible refutation candidate and is reported in §3 (Abrigo↔Numo) and §5 (Risk #1) without softening. Dalgıç 2024's insurance-arrangement result is identified explicitly as the support-side empirical anchor; the only refutation candidate (premium drag dominates spot-stablecoin holding) is empirically struck down by the Pair-D PASS verdict already in `memory/`.
- **No silent re-framing.** If any cluster turned out to deliver Abrigo-equivalent functionality, the SOTA would have HALTed and surfaced a disposition memo. None did. The cross-product remains empty.

---

## 8. Deliverables manifest

- [x] `scratch/2026-05-08-sota-review/DESIGN.md` (committed `5658cb3`)
- [x] `scratch/2026-05-08-sota-review/track-1-direct-onchain-convex.md`
- [x] `scratch/2026-05-08-sota-review/track-2-indirect-onchain-em-savings.md`
- [x] `scratch/2026-05-08-sota-review/track-3-indirect-offchain-fintech.md`
- [x] `scratch/2026-05-08-sota-review/track-4-hackathon-academic.md`
- [x] `scratch/2026-05-08-sota-review/SUMMARY.md` (this file, with three tagged excerptable sections)
