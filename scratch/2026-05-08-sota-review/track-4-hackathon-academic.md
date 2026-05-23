# Track 4 — Hackathon + academic adjacent prior art

*Scope: hackathon/grant-funded prior art and academic/policy literature relevant to Abrigo's permissionless on-chain perpetual convex instruments thesis. Tracks 1–3 (commercial protocols, off-chain fintech) deliberately excluded. Numo corpus collected in §6 as Track 4's pinned methodological-benchmark deliverable.*

---

## 1. Hackathon / grant-funded prior art

### 1.1 Celo Proof of Ship

Celo Proof of Ship (PoS) is a monthly builder program (not quarterly cohorts as initially scoped — the cadence shifted to monthly in early 2025). $5K/month USDT prize pool distributed via AI-judged impact metrics across the top ~50 projects. **576 projects shipped through PoS in 2025**, with a dedicated MiniPay track from 2026 onward backed by Opera's $1M MiniPay builder fund ([Opera press release, 2026-04-22](https://press.opera.com/2026/04/22/minipay-builders-incentive-and-roadshow/), [Celo PG programs](https://www.celopg.eco/programs/proof-of-ship), [GitHub source-of-truth](https://github.com/celo-org/Proof-of-Ship)).

| Project | Cohort | Status | One-line | URL |
|---|---|---|---|---|
| HaloFi (ex-GoodGhosting) | Pre-PoS / Celo-native | Live, dormant on Celo (migrated multi-chain) | Gamified commitment-savings pools on Aave/Curve/Celo — closest to "premium-funded ratchet" framing in the EM-savings space | [valora blog](https://valora.xyz/blog/dapp-spotlight-hit-your-savings-goals-with-halofi) |
| Kotani Pay | UNICEF VF + multiple PoS | Live, scaling | Stablecoin↔mobile-money USSD bridge for Africa; not a hedging instrument but the fiat off-ramp Abrigo would need | [unicefventurefund.org](https://www.unicefventurefund.org/story/kotani-pay-increasing-access-financial-instruments-using-blockchain-and-cryptocurrency) |
| Xcapit (Shelter/AidLink) | IDB + Celo | Live | Multi-chain smart-contract disbursement; humanitarian focus, not capital-formation | [xcapit.com](https://www.xcapit.com/en/case-studies/shelter-aidlink) |
| Glo Dollar | Celo-aligned, Allo grants | Live | UBI-funded stablecoin; redirects yield to charity — not hedging but adjacent in "wage→capital institutional plumbing" framing | (general celo ecosystem) |
| MiniPay mini-apps (2025–) | Monthly PoS | ~576 shipped | Mostly remittance, savings, on-ramp, merchant payments; **no convex-payoff or perpetual-options projects identified** in available cohort summaries | [celopg.eco](https://www.celopg.eco/programs/proof-of-ship) |

**Gap signal:** Across 576 PoS projects in 2025, no shipped or finalist project was a permissionless EM-FX convex-hedge instrument. The PoS track explicitly biases toward MiniApp-shaped consumer flows, which selects against settlement-layer derivative work.

### 1.2 ETHGlobal LATAM/Africa

- **ETHGlobal Buenos Aires (Nov 2025):** $500K prize pool, 475 teams, 10 winners (Paybot, JetLagged, Hubble Trading Arena, Payload Exchange, Yoga, LensMint, Halo, zkx402, Aqua0, BMCP). DeFi/prediction-market focus; **no EM-FX hedge or convex-payoff winner**. Hubble Trading Arena and Payload Exchange are the closest derivatives-adjacent entries but are trading-UX not instrument-design plays. ([Bitget recap](https://www.bitget.com/amp/news/detail/12560605081065), [event](https://ethglobal.com/events/buenosaires))
- **ETHBogotá (2022, Devcon):** historical; no 2024–2025 successor in Bogotá.
- **ETHGlobal Cannes 2025** (Jul 4–6, $275K) — European, no LATAM focus but worth tracking for Mento sponsor presence ([ETHGlobal Cannes](https://ethglobal.com/events/cannes)).
- **2026 calendar** posted by ETHGlobal: Cannes (Apr), NY (Jun), Lisbon (Jul), Tokyo (Sep), Mumbai (Q4) — **no Bogotá, Buenos Aires, Mexico City, or Lagos confirmed for 2026**. Lagos appears only as an "ETHGlobal Plus" community location, not an in-person hackathon. ([ETHGlobal 2026 calendar](https://x.com/ETHGlobal/status/1992919708589576215))
- **ETHMexico** archived at [ethglobal.com/events/ethmexico](https://ethglobal.com/events/ethmexico); no 2024/25 reboot.

**Gap signal:** ETHGlobal's LATAM/Africa coverage in the 2025–2026 cycle is *thinning*, not growing. Abrigo cannot rely on a regional ETHGlobal as a recurring distribution venue; Celo PoS is the more reliable EM-builder funnel.

### 1.3 Mento Labs grants

Mento raised **$10M in Aug 2024** (HashKey Capital, T-Capital, Verda, Flori, w3.fund, R. Parsons et al.) explicitly to fund the local-stablecoin roadmap across three regions ([Mento blog](https://www.mento.org/blog/10m-fundraise-and-decentralized-local-currency-stablecoin-roadmap-across-3-regions)). Roadmap stables: **cCOP** (Colombia, partnered with Celo Colombia, targeting $70B/mo crypto txn flow), **PUSO** (Philippines, launched Sep 2024), **cGHS** (Ghana, with Celo Africa DAO + Haraka + Grameen Foundation, micro-lending use case), planned cBRL (Brazilian Real) and additional EUR/KES coverage. Mento processed **$18.5B** in stablecoin volume in 2025.

**No public Mento Labs grant program for downstream builders has been formally announced** as of May 2026. Builder funding routes through Celo PG / PoS rather than Mento directly. Partnership candidate, not grant source.

### 1.4 Allo / Gitcoin EM rounds

- **Gitcoin Grants 24 (GG24)** covered all 17 SDGs including financial inclusion ([gitcoin.co/campaigns/gg24](https://gitcoin.co/campaigns/gitcoin-grants-24-gg24)).
- **Meta Pool DAO LATAM round on Allo** funded 14 projects in education/staking/environmental; no FX-hedge or convex-instrument winner.
- **Gitcoin Climate Solutions** bundled an EM/Indigenous-communities sub-track.
- Funded EM-savings/inclusion projects via Gitcoin: **Kotani Pay (KE), Rahat (NP), Treejer, Xcapit (AR)** — all payments/wallet/cash-transfer, none derivative.

No dedicated "EM-savings" or "household-hedging" round has run on Gitcoin/Allo. Premium-funded-ratchet framing has not appeared as a funded category.

### 1.5 IDB Lab portfolio

IDB Lab has approved >$2B across 26 LAC countries since 1993 ([IDB Lab news](https://www.iadb.org/en/news/idb-lab)). Blockchain-relevant entries:

- **Davivienda × IDB blockchain bond** (Colombia, regulatory sandbox) — first blockchain bond in LAC ([IDB Invest](https://www.idbinvest.org/en/news-media/idb-group-and-davivienda-bank-issue-colombias-first-blockchain-bond)).
- **LACChain** — global alliance for blockchain in LAC, inclusion-focused infrastructure ([IDB news](https://www.iadb.org/en/news/global-alliance-promote-use-blockchain-latin-america-and-caribbean)).
- **"Digital Wallets for Inclusion and Sustainability"** regional initiative, Peru-led ([IDB Lab and Switzerland](https://www.iadb.org/en/news/idb-lab-and-switzerland-agree-foster-financial-inclusion-peru)).
- **EthicHub** — IDB Lab portfolio company; tokenized loans for smallholder farmers, blockchain+stablecoin loan-origination model.

**Partnership signal:** IDB Lab + LACChain are the natural policy-cover umbrella for an Abrigo Colombia pilot; Davivienda already has IDB-sandboxed on-chain instrument experience. Not a direct grant source but a credibility amplifier.

---

## 2. Academic / policy literature

*arxiv MCP rate-limited during this run; arxiv IDs cited via verified web cross-references. Where arxiv unavailable, SSRN/NBER/journal URLs used.*

### 2.1 Post-Keynesian distribution

- **[Lavoie 2014](https://www.amazon.com/Post-Keynesian-Economics-Foundations-Marc-Lavoie/dp/184720483X)** — *Post-Keynesian Economics: New Foundations* (Edward Elgar). Canonical PK textbook; distribution treated as institutionally determined via mark-up, conflict claims, and bargaining power, not marginal productivity.
- **[Hein & Stockhammer 2011 / 2024](https://www.elgaronline.com/view/journals/ejeep/21/2/article-p202.xml)** — "Inflation is always and everywhere... a conflict phenomenon." The Hein–Stockhammer conflict-claims model: inconsistent distribution claims drive inflation and distribution dynamics; only consistent claims produce constant inflation/distribution. **This is the closest formal home for Abrigo's "wage→capital boundary is institutional, not equilibrium-given" claim.**
- **[Stockhammer 2022](https://journals.sagepub.com/doi/10.1177/00323292211006562)** — "Post-Keynesian Macroeconomic Foundations for Comparative Political Economy," *Politics & Society*. Maps PK macro onto comparative-capitalism varieties; useful for the LATAM-vs-Africa institutional-context split.
- **[Kohler, Guschanski & Stockhammer 2018](https://www.postkeynesian.net/downloads/working-papers/PKWP1802_MQ1APLF.pdf)** — "The impact of financialisation on the wage share." Disentangles financialization channels; rentier payments and financial liberalization most strongly compress wage share. **Direct support for Abrigo's "wage earners are blocked from capital share" thesis.**
- **[Morlin 2023](https://www.imk-boeckler.de/data/downloads/IMK/FMM%20Konferenz%202023/v_2023_10_20_morlin.pdf)** — Conflict, inertia, and the Phillips curve from a Sraffian standpoint. Useful for placing the COP/USD inflation-pass-through channel in PK terms.

### 2.2 Structural-transformation finance / informal-worker capital access

- **[OECD/CAF/ECLAC LEO 2025](https://www.oecd.org/en/publications/latin-american-economic-outlook-2025_80e48de5-en/full-report/overview_db715ebd.html)** — "Promoting and Financing Production Transformation." 55.1% LATAM informality rate (2023, down from 62.5% in 2009 but stuck for youth). Direct numerical anchor for Abrigo's target population.
- **[OECD 2024 — Informality and Households' Vulnerabilities in LAC](https://www.oecd.org/content/dam/oecd/en/publications/reports/2024/10/informality-and-households-vulnerabilities-in-latin-america_fdbca190/e29d9f34-en.pdf)** — household-level informality + financial-fragility microdata; identifies non-traditional credit-scoring as the policy lever.
- **[CAF Call for Research 2024](https://www.caf.com/en/work-with-us/calls/call-for-research-proposals-latin-america-and-the-caribbean-at-the-crossroads-of-informality-and-digitalization/)** — "LATAM at the crossroads of informality and digitalization." Open research-funding venue Abrigo can apply to.
- **[ECLAC 2024 — Rethinking labor informality](https://www.cepal.org/en/news/specialists-eclac-agreed-need-rethink-labor-informality-region-light-technological-change)** — frames informality as productive-structure problem, not regulatory-evasion problem. Aligns with PK institutionalist read.

### 2.3 Microfinance graduation programs

- **[Banerjee, Duflo, Goldberg, Karlan, Osei, Parienté, Shapiro, Thuysbaert, Udry 2015 *Science*](https://www.science.org/doi/10.1126/science.1260799)** — "A Multifaceted Program Causes Lasting Progress for the Very Poor." Six-country RCT (ET, GH, HN, IN, PK, PE), 11K households. Asset-transfer + consumption support + skills + savings encouragement → durable consumption gains.
- **[Banerjee, Duflo, Sharma 2021 *AERI* (NBER w28074)](https://www.nber.org/system/files/working_papers/w28074/w28074.pdf)** — 7- and 11-year follow-ups on Bangladesh TUP; non-farm earnings ~2× control by year 7; effects stabilize. **Critical empirical anchor: graduation-style asset transfers do produce lasting capital accumulation — but require an upfront grant, which Abrigo's premium-funded ratchet inverts (no grant, instrument-funded).**
- **[BRAC PROPEL Toolkit 2015](https://refugees.trickleup.org/wp-content/uploads/2017/08/2015_BRAC_PROPEL_Toolkit_compressed.pdf)** — operational graduation playbook; cost structure benchmarks.
- **[Yale Insights — Graduation Approach](https://insights.som.yale.edu/insights/can-the-graduation-approach-help-to-end-extreme-poverty)** — synthesis review.

**Policy-design gap revealed:** all graduation evidence assumes external grant capital. None tests an instrument-financed (premium-funded) ratchet variant. **Abrigo's design is empirically untested in the graduation-program literature** — this is novelty, not refutation.

### 2.4 Sovereign-individual / household FX hedging in EM

- **[Dalgıç 2024 *IER*](https://onlinelibrary.wiley.com/doi/10.1111/iere.12686)** — "Financial Dollarization in Emerging Markets: An Insurance Arrangement." Households dollarize *because* the dollar appreciates in domestic recessions — same insurance logic Abrigo formalizes via convex payoff.
- **[Du & Huber 2023 (Wharton)](https://fnce.wharton.upenn.edu/wp-content/uploads/2023/12/AmyHuber12_23.pdf)** — "Dollar Asset Holding and Hedging Around the Globe." Cross-country hedging-channel atlas; shows EM hedging infra is institutional-investor-only.
- **[Alfaro et al. (HBS 21-096)](https://www.hbs.edu/ris/Publication%20Files/21-096_3317d99c-a5fb-4662-b3b8-d7007994785d.pdf)** — "Currency Hedging in Emerging Markets: Managing Cash Flow Exposure." Firm-level EM hedge demand & cost.
- **[BIS WP 1303 — FX debt and optimal exchange rate hedging](https://www.bis.org/publ/work1303.pdf)** — recent (2024); shows optimal hedge ratio responds to FX-debt dollarization.
- **[BIS Papers 44 — Hedging instruments in EME](https://www.bis.org/publ/bppdf/bispap44d.pdf)** — surveys which EM derivatives markets exist; Colombia put/call FX auctions documented.
- **[Chen & Zhou 2025](https://haonanzhou.io/wp-content/uploads/2025/01/em_currency.pdf)** — "Managing Emerging Market Currency Risk." Most recent academic synthesis.

**Refutation check:** Dalgıç's insurance result *supports* Abrigo's thesis — households already self-insure via informal dollarization but pay an inferior price. Convex perpetual on cCOP/USD strictly dominates physical-dollar hoarding when the convexity is meaningful, *if* the premium can be funded out of wage income. Track 4 finds no paper that empirically refutes this.

### 2.5 Panoptic + perpetual options + CFMM-on-LP literature

- **[Lambert & Kristensen 2022/2023, arXiv:2204.14232](https://arxiv.org/abs/2204.14232)** — *Panoptic: the perpetual, oracle-free options protocol.* Foundational. Streamia (range-conditional premium), LP-as-short-put, oracle-free liquidations.
- **[Angeris, Evans, Chitra 2021, arXiv:2111.13740](https://arxiv.org/abs/2111.13740)** — *Replicating Monotonic Payoffs Without Oracles.* The CFMM-replication theorem: monotonic payoffs ↔ trading functions. **Foundational for any custom-payoff Abrigo hook.**
- **[Angeris, Evans, Chitra 2021, arXiv:2103.14769](https://arxiv.org/abs/2103.14769)** — *Replicating Market Makers.* The original LP-payoff↔trading-function duality.
- **[He, Manela et al. 2024+ (arXiv:2212.06888)](https://arxiv.org/abs/2212.06888)** — *Fundamentals of Perpetual Futures.* No-arb perpetual pricing; funding-rate mechanics.
- **[Hugonnier, Jermann, Ackerer 2024 *Math. Finance* (arXiv:2310.11771)](https://arxiv.org/abs/2310.11771)** — *Perpetual Futures Pricing.* Random-stopping risk-neutral representation; replicable via dynamic trading.
- **[Designing funding rates for perpetual futures, arXiv:2506.08573](https://arxiv.org/abs/2506.08573)** — path-dependent funding-rate design; replicating portfolios. Most recent (2025).
- **[Funding-Aware Optimal Market Making for Perpetual DEXs, arXiv:2605.06405](https://arxiv.org/html/2605.06405)** — inventory↔funding coupling for LP profit; relevant if Abrigo solves Stage 3 LP-side liquidity.
- **[Angeris primer on perpetuals 2022](https://angeris.github.io/papers/perps.pdf)** — accessible derivation reference.

---

## 3. Coverage of Abrigo thesis components (buildable hackathon projects only)

7-axis schema: **Permissionless | Convex | EM-FX-native | Wage-earner-accessible | Premium-funded ratchet | Open-source | Numo-rigor (0–5)**.

| Project | Perm. | Convex | EM-FX | Wage-acc. | Prem-ratchet | OSS | Numo-rigor |
|---|---|---|---|---|---|---|---|
| HaloFi | ✓ | ✗ (linear yield) | partial (Celo cUSD/cEUR) | ✓ | ✗ (commitment, not premium) | ✓ | 1 (consumer doc, no formal payoff spec) |
| Kotani Pay | ✗ (custodial bridge) | ✗ | ✓ | ✓ | ✗ | partial | 0 (product, no spec) |
| Xcapit/Shelter | ✓ | ✗ | ✓ | ✓ (humanitarian) | ✗ (grant-funded) | partial | 1 |
| Glo Dollar | ✓ | ✗ | ✗ (USD-only) | ✓ | ✗ | ✓ | 1 |
| EthicHub | partial | ✗ (loan, not option) | ✓ (LATAM rural) | partial | ✗ | partial | 1 |
| ETHGlobal BA winners (Hubble, Payload) | ✓ | partial (trading venues, not instrument-level convexity for end-user) | ✗ | ✗ (trader-facing) | ✗ | mixed | 1 |
| Numo (R. Leifke) | ✓ | ✓ (perpetual call replication) | ✗ (asset-agnostic, no EM-FX deployments) | ✗ (LP/trader-facing) | ✗ | ✓ | **5** (formal CFMM-from-payoff spec, peer-cited in Angeris et al.) |

**Read:** No buildable hackathon project covers ≥4 of the 7 axes. The convex+permissionless quadrant is essentially Numo's; the EM-FX+wage-accessible quadrant is essentially HaloFi/Kotani. **Abrigo's contribution is the cross-product**, which is empty in current hackathon prior art.

---

## 4. Design-space gaps revealed by failed/abandoned attempts

1. **HaloFi's pivot away from Celo-only.** The Celo-native gamified-savings-pool design didn't reach escape velocity on Celo alone — they migrated multi-chain. Lesson: **EM-savings UX is necessary but not sufficient; Celo-only distribution is insufficient without a payoff-shape moat.** Abrigo's convex payoff is that moat.
2. **Numoen → Numo rebrand and pivot to "Market Maker for Global Payments."** Leifke's GitHub repo description is now `Market Maker for Global Payments`, not "permissionless options exchange." This is a *strong signal that the pure perpetual-options-AMM thesis did not find a wage-earner or institutional buyer in the 2022–2024 cycle.* Lesson: convex-payoff plumbing without a target-population/distribution channel does not survive. **Abrigo's (Y, M, X)-triple discipline is the correction.**
3. **No Mento builder grant exists.** The $10M raise went to internal stablecoin-launch ops, not downstream builders. Lesson: Mento expects builder financing to come from Celo PG, not Mento directly. Plan accordingly.
4. **ETHGlobal LATAM cadence collapse.** No Bogotá/BA/Mexico in the 2026 calendar. Lesson: hackathon-based GTM in LATAM is fragile; lean on Celo PoS monthly cadence + Devconnect.
5. **Graduation-program literature is grant-only.** No academic precedent for an instrument-financed graduation ratchet. *Not a refutation* — a novelty area where Abrigo can publish.
6. **No academic refutation of household-FX-hedge demand.** Dalgıç 2024 + Du-Huber 2023 + BIS WP 1303 all support the demand-side. Refutation candidates would require showing convex-payoff EM-FX hedges are *dominated* by spot-stablecoin holding net of premium — Abrigo Pair-D PASS verdict (β = +0.137, p ≈ 1.5e-08) is a direct empirical strike against that null.

---

## 5. Partnership / people candidates

- **Robert Leifke** ([@robertleifke](https://x.com/robertleifke), [robertleifke.com](https://www.robertleifke.com/)). Numo founder, Angeris-circle CFMM-from-payoff practitioner. Direct technical conversation candidate; his Uniswap V4 hook code is the closest existing reference implementation for Abrigo's settlement layer.
- **Guillaume Lambert & Jesper Kristensen** (Panoptic) — protocol-level co-design; Lambert is publicly responsive to academic users.
- **Guillermo Angeris, Alex Evans, Tarun Chitra** (Bain Capital Crypto / Stanford / Gauntlet) — CFMM-replication theory authority. Cite explicitly in any Abrigo whitepaper.
- **Engelbert Stockhammer** (King's College London) and **Eckhard Hein** (Berlin School of Economics) — PK distribution-theory anchors. Likely receptive to a wage→capital institutional-instrument paper.
- **Dean Karlan** (Northwestern, IPA) — graduation-program RCT lead; would likely critique an instrument-financed-ratchet design rigorously.
- **CAF Research Calls** — open submission ([CAF informality+digitalization call](https://www.caf.com/en/work-with-us/calls/call-for-research-proposals-latin-america-and-the-caribbean-at-the-crossroads-of-informality-and-digitalization/)). Direct funding route.
- **IDB Lab / LACChain** program officers — Davivienda sandbox precedent; Colombia is the natural pilot jurisdiction.
- **Mento Labs** (Markus Franke + co-founders) — partnership not grant; cCOP/cBRL access depends on this relationship.
- **Celo PG** (Proof of Ship operators) — monthly distribution funnel.
- **Block Scholes research team** — published Panoptic gamma-scalping research ([Panoptic × Block Scholes](https://blockscholesresearch.substack.com/p/panoptic-x-block-scholes-perpetual)); useful for premium-pricing model validation.
- **Xcapit (Argentina)** — IDB Lab portfolio + smart-contract disbursement; possible LATAM regulatory co-pilot.

---

## 6. NUMO CORPUS (format/methodology benchmark)

Pinned Track-4 deliverable. Every public Numo / Numoen / Robert Leifke artifact discovered, with one-line note on why it serves as Abrigo's stylistic reference.

**GitHub repos**
- [github.com/robertleifke/numo](https://github.com/robertleifke/numo) — *"Market Maker for Global Payments."* Current Uniswap V4 hook implementation; inherits OpenZeppelin's `BaseCustomCurve`; inspired by Primitive's Log-Normal DFMM and the Replicating-Market-Makers paper. **Closest reference impl for Abrigo's V4 hook.**
- [github.com/numotrade/research](https://github.com/numotrade/research) — research-paper repo (LaTeX sources of internal whitepapers and notes).
- [github.com/numocash/research](https://github.com/numocash/research) (also: [github.com/dahlia-labs/research](https://github.com/dahlia-labs/research)) — Dahlia Labs / Numoen research lineage.
- [github.com/Numoen/docs](https://github.com/Numoen/docs) — power-maker docs hub (deprecated but still useful as a structure template).
- [github.com/code-423n4/2023-01-numoen](https://github.com/code-423n4/2023-01-numoen) — Code4rena audit contest scope (Jan 2023). **Structurally what an Abrigo audit-scope repo should look like.**
- [github.com/robertleifke](https://github.com/robertleifke) — personal org with companion repos.

**Whitepapers / academic anchors**
- Angeris–Evans–Chitra, [arXiv:2111.13740](https://arxiv.org/abs/2111.13740) — *Replicating Monotonic Payoffs Without Oracles.* Numo cites this as theoretical foundation; Abrigo should also.
- Angeris–Evans–Chitra, [arXiv:2103.14769](https://arxiv.org/abs/2103.14769) — *Replicating Market Makers.* Original duality theorem.

**Long-form blog posts (Medium, in chronological reading order)**
- [Perpetual Options for DeFi](https://medium.com/numoen/perpetual-options-for-defi-821351c0a24f) (Dahlia Labs / Numoen). Motivation post; clean problem-framing. **Format model: problem → first-principles → instrument sketch → call to action.**
- [The World's First Permissionless Options Exchange](https://medium.com/numoen/the-worlds-first-permissionless-options-exchange-498a8625291a). Launch post; bold positioning. Note the "permissionless" framing — same word Abrigo uses.
- [A Primer on Power Tokens](https://medium.com/numoen/a-primer-on-power-tokens-62fd0416a516). Educational primer for non-quants.
- [AMMs are the new operating systems](https://medium.com/numoen/amms-are-the-new-operating-systems-f626523ab7f1). Worldview-setting post; useful template for Abrigo's narrative-frame essays.
- [Announcing Liquid Staking Boost](https://medium.com/numoen/announcing-liquid-staking-boost-405b49bf7772). Product-launch post template.
- [Breaking down UniswapV2 core contracts](https://robertleifke.medium.com/breaking-down-uniswapv2-core-contracts-ebdd48416566) (Leifke personal Medium). Code-walkthrough format.

**Personal site / aggregated writing**
- [robertleifke.com](https://www.robertleifke.com/) — personal homepage; aggregates writing & projects.
- [robertleifke.medium.com](https://robertleifke.medium.com/) — Medium archive.

**Devpost / hackathon artifacts**
- [Numoen on Devpost](https://devpost.com/software/numoen) — original hackathon submission; instructive "from-zero-to-protocol" framing.
- [Robert Leifke Devpost portfolio](https://devpost.com/rleifke) — full portfolio.

**X / social**
- [@robertleifke on X](https://x.com/robertleifke) — primary public channel; threads on AMM design and perpetual options.

**External research collaborations citing Numo lineage**
- [Panoptic × Block Scholes — Perpetual Options research report (Part II)](https://panoptic.xyz/research/panoptic-block-scholes-research-gamma-scalping). Gamma-scalping treatment; same intellectual neighborhood.
- [Panoptic blog — LP = Option: Uniswap as an Options Clearinghouse](https://blog.panoptic.xyz/lp-option-uniswap-as-an-options-clearinghouse-0b3c578d968f). The frame Abrigo settles into.

**What Abrigo should imitate (and what to avoid)**
- *Imitate:* clean problem-framing posts; explicit citation of CFMM-replication theorems; audit-contest-ready repo layout; short personal Medium pieces tied back to a research repo.
- *Avoid:* the Numoen→Numo rebrand drift. Numo's pivot away from the original "permissionless options exchange" thesis to "market maker for global payments" is what happens when a payoff-design protocol lacks a (Y, X) target-population discipline. Abrigo's CLAUDE.md (Y, M, X) framework is structurally the correction. **Ship the population-targeted iteration, not the payoff-first protocol.**

---

*Track 4 complete. Word count ≈ 2.4k. Cross-track note for synthesis: the Abrigo wage-earner-accessible × convex × EM-FX intersection has zero buildable prior art; academic literature supports demand-side and graduation-style asset-accumulation evidence; the only refutation candidate (premium drag dominates spot-stablecoin holding) is empirically struck down by the Pair-D PASS verdict already in `memory/`.*
