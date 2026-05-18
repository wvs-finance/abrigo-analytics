---
name: bhaduri-laski-riese-concept-bridge
description: Post-Keynesian literature review anchor (Bhaduri-Laski-Riese 2006 "Virtual vs Real Economy") + concept-bridge map linking PK financialization theory to on-chain Abrigo instrument design
metadata:
  type: reference
---

User-provided 2026-05-18 conceptual bridging review (not a novelty audit; concept map for terminology + prior-art seeding).

## Anchor paper

**Bhaduri, A., Laski, K., & Riese, M. (2006).** "A model of interaction between the virtual and the real economy." *Metroeconomica*, 57(3), 412–427. Originally WIIW WP.

Core argument (Kaleckian-Keynesian):
- Stock-market boom → households expand consumption mostly through **debt** (not current income) → demand + output expand
- Rising debt-service burden + falling creditworthiness flip the system → contraction
- Headline: stock-market wealth and real-economy growth can move in opposite directions; virtual prosperity can coexist with real stagnation

**Why this anchors Abrigo**: BLR formalize the exact pathology Abrigo's (Y, M, X) framework is designed to invert. Default financialization = wealth-effect → consumption debt → MORE leverage, not closer to productive-capital ownership. Abrigo's premium-funded ratchet = wage income → convex payoff → productive-capital exposure (the bridge that BLR implicitly says capitalism does not build for wage earners).

## Genealogy (read order)

**Tier 1 — Foundational**
- Keynes GT (1936) Ch. 12 (casino vs enterprise convention-valuation); Ch. 17 (two-price logic origin)
- Kalecki (1971) Selected Essays — effective demand + distribution-driven investment
- Minsky (1975 + 1986) — Financial Instability Hypothesis; two-price theory (P_k asset/demand vs P_i output/supply); casino capitalism

**Tier 2 — Modern PK financialization**
- Stockhammer "Financialization and the slowdown of accumulation" (Cambridge JE 2004); wage-share line with Kohler & Guschanski
- Hein & van Treeck — Handbook of Alternative Theories; ifso WP 32 (2024) — best survey of PK financialization-in-growth-models; direct methodological cousin to BLR
- Bhaduri (2011) "Financial fragility and crisis" (Cambridge JE / Levy WP 593 / WIIW WP 65) — BLR follow-up
- Bhaduri & Marglin (1990) — wage-led vs profit-led growth dichotomy (underwrites Abrigo's CLAUDE.md "distribution is institutionally determined")
- Kregel — Minskian banking/monetary
- Tymoigne (2010) "Minsky's Two-Price Theory of Investment" (Levy) — cleanest formal restatement

**Tier 3 — Recent empirical Minsky / nonlinear**
- delli Gatti, Gusella, Ricchiuti (2025) — arXiv:2511.04348 — regime-switching across USA/FR/DE/CA/AU/UK extending Stockhammer et al. 2019
- Solomon & Golo (2014) — arXiv:1402.0176 — network/percolation Minsky (relevant for on-chain contagion)

## Blockchain-aware bridge literature

### On-chain analog of two-price / virtual-vs-real
- Catalini & Gans (2016/2020) NBER WP 22952 — token economics; utility vs speculative (P_i vs P_k mirror)
- AMM theory: Bartoletti et al. arXiv:2102.11350; Xu et al. SoK arXiv:2103.12732; Jensen et al. arXiv:2105.02782 — AMM pool price vs external = structural two-price gap; impermanent loss = on-chain virtual-vs-real decoupling
- **Lambert, Lyons, Jiao (2022)** Panoptic arXiv:2204.14232 — **Abrigo's M-layer**. A Panoptic position embeds the two-price gap (LP fees from output flow vs option-value appreciation from price-process geometry) into a single tradable primitive
- Maymin (2026) arXiv:2603.29763 — CEV process for AMM tokens, closed-form option pricing

### On-chain analog of premium-funded ratchet / wage→capital
- Impact tokens (IISD 2019) — closest non-academic prior art to Abrigo's mission framing
- ReFi (Regenerative Finance) — industry literature, weak research base
- RWA tokenization: Xia et al. (2025) arXiv:2503.01111
- **Decentralized/parametric insurance: arXiv:2412.05321** — wage-earner pays premium → convex payoff on real risk; CLOSEST extant academic analog of Abrigo's premium-funded ratchet (stops at "indemnify" not "accumulate productive capital")

### On-chain analog of monetary sovereignty / local currency
- **Mento Protocol** — cUSD/cEUR/cREAL/cKES/COPm. On-chain instantiation of Kaldorian/late-Kaleckian/modern PK insistence that monetary sovereignty matters for distribution. Industry-only, no peer-reviewed write-up — **positioning opportunity**

## Concept-bridge map (terminology spine)

| PK concept | BLR/Minsky term | On-chain analog | Cite |
|---|---|---|---|
| Decoupling finance/production | Virtual vs real; two-price | AMM vs spot/oracle; impermanent loss; MEV extraction | BLR 2006; Tymoigne 2010; Bartoletti 2021 |
| Speculative gain at expense of accumulation | Casino capitalism | Extractive DeFi yield-farming; ponzinomics | Minsky 1986; ReFi positioning |
| Stock-wealth → consumption debt not ownership | Virtual wealth effect | Crypto-collateralized borrowing for consumption; circular-leverage stablecoin loops | BLR 2006; von Wachter et al. 2021 arXiv:2102.04227 |
| Convention-driven asset valuation | Keynes Ch.12 beauty contest | Memecoin / narrative-driven token pricing | Keynes 1936 |
| Distribution institutionally determined | Wage-led vs profit-led | Token-distribution governance; fair launch | Bhaduri & Marglin 1990 |
| Premium-funded ratchet (Abrigo) | **Gap to position into**; closest: Steindl forced-saving + Minsky hedge-finance | Parametric insurance + tokenized savings + LBM | arXiv:2412.05321; IISD |
| Wage earner → productive-capital owner | Structural transformation (Kaldor/Lewis/late Kalecki) | RWA tokenization + impact tokens + on-chain equity | Xia 2025; IISD 2019 |
| Two-price gap as locus of arbitrage | Minsky P_k − P_i | Funding rate; perpetual-option premium; convexity premium | Tymoigne 2010; Lambert (Panoptic) 2022 |
| Monetary sovereignty | Kaldor-Robinson-PK monetary | Mento local-currency stables; CBDCs | Mento (no academic anchor yet) |
| Financial fragility / Minsky moment | Bhaduri 2011 FIH | DeFi protocol cascades; liquidation spirals; oracle-failure contagion | delli Gatti 2025; Solomon & Golo 2014 |

## Search-term seeds

**PK-side** (Scholar + RePEc): "virtual wealth"; "two-price theory"; "financialisation of households"; "debt-financed consumption" Kaleckian; "wage-led growth" "financial fragility"; "endogenous money" investment

**Blockchain-side** (arXiv q-fin / econ.GN; Scholar): "impact tokens"; "regenerative finance"; "parametric insurance" smart contract; "real world assets" tokenization productive; "perpetual options" AMM; "liquidity bootstrapping mechanism" "fair launch"; "premium-funded" OR "premium-financed" tokenized

**Bridge terms (almost no one has connected — positioning opportunity)**: "Minsky" "DeFi"; "financialization" blockchain wage; "post-Keynesian" tokenization; "two-price theory" AMM; "casino capitalism" cryptocurrency

## Three papers worth reading in full (priority)

1. **BLR (2006)** — anchor, ~16 pages, Academia.edu PDF
2. **Hein & van Treeck (2024 ifso WP 32)** — situates BLR within PK financialization-in-growth-models program (skim §2-4)
3. **Lambert et al. Panoptic (arXiv:2204.14232)** — re-read with BLR/Minsky lens. The two-price gap is built into the Panoptic primitive — non-trivial conceptual finding for Abrigo spec narrative

## Cleanest unfilled gap (publishable in heterodox journals)

No peer-reviewed paper formally connects Minsky's two-price theory to AMM micro-structure (Maymin 2026 closest piece but doesn't invoke Minsky). Methods-paper framing: **"the Minsky P_k/P_i gap is endogenously instantiated by every concentrated-liquidity AMM, and Panoptic-style perpetual options price that gap directly"** — publishable in Cambridge JE / ROPE / Metroeconomica.

## Terminology choice (outward-facing)

Prefer **"productive-capital ratchet"** or **"wage-to-capital bridge instrument"** over **"self-LBM"** when talking to PK economists or impact-finance funders. The first two are recognized; the third reads as crypto jargon.

## Watch list

Monitor **delli Gatti, Gusella, Ricchiuti** for follow-ups — Stockhammer-school empirics on real-financial cycles is the most active strand, intersects directly with Abrigo's empirical-β workstream.

## Links to other memory

[[financialization-framework]] (`~/learning/post-keynesian/notes/FINANCILATION.md` — CF_T = E_T − L_T operationalization carried into spec v0.3 §0.9)
[[endogenous-money-notes]] (`~/learning/post-keynesian/notes/ENDOGENEOUS_MONEY.md` — opened repeatedly during 2026-05-18 session)
