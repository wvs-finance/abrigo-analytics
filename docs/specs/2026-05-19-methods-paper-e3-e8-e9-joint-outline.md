# Joint Methods-Paper Outline — E3 + E8 + E9

**Status:** OUTLINE (not draft prose). Section structure, target arguments,
citation skeleton, and contribution-positioning paragraph only.
**Date:** 2026-05-19
**Author scope:** Abrigo analytics half (this repo); contract half referenced
as external given.
**Anchor framings:** `memory/reference_bhaduri_laski_riese_concept_bridge.md`
(§"Cleanest unfilled gap"); `memory/project_abrigo_framing_clarification_investment_productivity.md`
(generalized framing); CLAUDE.md theoretical-anchor section.
**Component specs:** `docs/specs/2026-05-18-e8-dtao-maymin-methods-paper-design.md`
(E8); `scratch/2026-05-18-wave1/E9A_prepin/prepin.md` (E9-A); E3 demoted to
methods-paper-only per Day-1 verdict (Panoptic mainnet 2024-07 postdates named events).

---

## §0 Working title + target venues

**Candidate titles** (rank-ordered, all framed around the bridge, not any single empirical β):

1. *"Minsky's Two-Price Theory on the Automated Market Maker: Concentrated-Liquidity AMMs as Empirical Locus of the P_k/P_i Gap, Priced by Perpetual Options"*
2. *"From Virtual Prosperity to On-Chain Convexity: A Post-Keynesian Framework for Pricing the AMM Two-Price Gap with Perpetual Options"*
3. *"Pricing the Minsky Gap on Permissionless AMMs: A CEV-Closed-Form Operationalization with Bittensor and Prosumer-Energy Evidence"*

**Venue ranking:**

- **Primary:** *Cambridge Journal of Economics* — PK-canonical; methods-paper-receptive; Stockhammer/Hein lineage of financialization-in-growth-models papers actively published; the BLR (2006) anchor is in this lineage's bibliography.
- **Secondary:** *Review of Political Economy (ROPE)* — heterodox-friendly; faster turnaround; receptive to formal-model-plus-empirical-illustration structure; less rigid on quantitative-finance content than CJE.
- **Tertiary:** *Metroeconomica* — published the BLR (2006) original; explicit precedent for "virtual-vs-real" formal models; smaller readership.
- **Quaternary:** *Journal of Post Keynesian Economics* — receptive but less likely to value the AMM/CEV machinery; backup if the formal-finance content is the rejection cause at CJE/ROPE/Metroeconomica.
- **Off-PK option (do not lead with):** quantitative-finance venues (*Journal of Finance*, *Review of Financial Studies*) would value the CEV-on-AMM result but would discount the PK theoretical contribution. Keep as fallback if all PK venues reject and the paper is rewritten with the bridge demoted.

**Working choice:** target *Cambridge JE* first; ROPE as fallback; pre-write the methods section so it can be cut and resubmitted without restructuring.

---

## §1 Contribution positioning (one paragraph — the elevator)

Post-Keynesian theory has long held that asset and output markets price the
same productive capital under structurally different mechanisms, generating
Minsky's two-price gap between P_k (asset-market valuation) and P_i
(output-market replacement cost), and Bhaduri-Laski-Riese's "virtual versus
real" co-existence of stock-wealth booms with stagnant productive accumulation.
Until now this gap has been a theoretical object, identified ex post in
macro-econometric cycles. We show that permissionless concentrated-liquidity
automated market makers (AMMs) instantiate the Minsky gap endogenously and
continuously: every AMM pool exhibits an LP-position-implied marginal price
(the P_k analog) that systematically diverges from the underlying spot or
fundamental-output reference (the P_i analog), with the divergence priced
directly by Panoptic-style perpetual options on AMM positions (Lambert,
Lyons, Jiao 2022) via the CEV-process closed-form of Maymin (2026). We
formalize this bridge — BLR virtual/real → Minsky P_k/P_i → CEV-on-AMM →
perpetual-option pricing — as the paper's central methodological contribution.
Four independent empirical anchors illustrate the bridge: (E8) Bittensor
dTAO subnets, where Maymin's CEV elasticity β−1 is significantly negative
across the subnet population with a halving natural-experiment;
(E9) Colombian AGPE prosumer-energy markets, where Fabi et al. (2025)
closed-form prosumer-AMM pricing meets a strong ENSO instrument on the
realized productivity of permitted operators; (E3) a Panoptic-deployment
formal-results sketch on Uniswap V3 LP-IL hedges; and (E10) a Colombian
Web3-analyst data-consumption cohort on Superfluid-Optimism, where the
streamed-liability primitive generalizes from receipt-side to cost-side
under x402-USDC-protocol-priced continuous-consumption flows — the first
empirical anchor in which the cohort's hedgeable stream is an outflow
rather than a receipt, closing the family under stream direction. The
paper's publishability does not depend on any single empirical β verdict
— the theoretical bridge is the contribution; the empirical anchors are
illustrations.

---

## §2 Theoretical core (E3-derived) — the formal Minsky ↔ AMM bridge

This is the paper's central methodological contribution and the basis for
publication independent of any single empirical β verdict. Roughly 30-40% of
final paper length.

### 2.1 BLR virtual/real dichotomy → AMM-mediated vs spot-mediated price discovery

- Restate BLR (2006) virtual/real model in compact form: stock-market wealth → debt-financed consumption → demand → output; debt-service burden flips the system; virtual prosperity coexists with real stagnation.
- Map onto on-chain analog: AMM-pool-implied price (LP-position-mediated; reflects accumulated liquidity-provision behavior and impermanent-loss accounting) versus spot/oracle reference price (reflects external-market fundamentals).
- Argument: the AMM pool is structurally a *virtual* price-discovery layer; its divergence from spot is the on-chain instantiation of BLR's virtual-vs-real decoupling. Impermanent loss = on-chain virtual-vs-real settlement cost.
- Cite: Bartoletti et al. (2021) for AMM theory; Xu et al. (2021) SoK; Jensen et al. (2021).

### 2.2 Minsky P_k/P_i → LP-position-implied marginal price vs underlying spot

- Restate Minsky's two-price model per Tymoigne (2010): P_k is the asset-market valuation of capital, P_i its output-market replacement cost. Investment proceeds when P_k > P_i.
- Bridge: the concentrated-liquidity AMM LP position has an implied marginal price determined by the tick range, the liquidity distribution, and the realized fee accumulation — this is the P_k analog. The reference spot (or external oracle) is the P_i analog.
- Key formal claim: the gap (P_k - P_i) on the AMM is *not* an arbitrage opportunity in the textbook frictionless sense, because the LP position is path-dependent (impermanent loss locks in the gap into LP NPV). The gap is structural, continuous, and observable.
- Cite: Minsky (1986); Tymoigne (2010); Lambert et al. (2022) Panoptic for the option-on-LP-position primitive.

### 2.3 Kaleckian investment-driven output → premium-funded ratchet on productive investment

- Restate Kalecki: investment drives output; distribution is institutionally determined; effective demand is the binding constraint.
- Bridge: the perpetual-option-on-AMM-position pays a premium stream that the investor *receives* (LP side) or *pays* (option-buyer side). For an investor exposed to the underlying production risk, *buying* the perpetual hedge converts a stream of small premium outflows into convex protection of the productive-investment path — the premium-funded ratchet.
- Operational primitive: the streamed-liability convex hedge (see §6). Each iteration in the Abrigo portfolio (E4 Superfluid R3+; E5 RefiColombia; E7 Mento Reserve; E8 Bittensor; E9 AGPE) instantiates the same M-shape with cohort-specific (Y, X).
- Cite: Kalecki (1971); Bhaduri & Marglin (1990) for the wage-led vs profit-led growth distinction underwriting "distribution is institutionally determined"; arXiv:2412.05321 (decentralized parametric insurance) as the closest extant academic analog stopping short of "accumulate productive capital".

### 2.4 Why Panoptic-style perpetual options on AMM positions are the pricing layer

- Continuous payoff, no expiry, LP-collateral: the three structural properties that make a perpetual option on an AMM position the *natural* pricing layer for a continuous, path-dependent two-price gap.
- Existing closed-form: Maymin (2026) provides the CEV-process closed-form pricing for tokens trading on AMMs; the CEV elasticity β−1 is the structural parameter measuring the departure from GBM (i.e., from a pure spot-market-equivalent price process).
- Argument: under GBM (β−1 = 0), the AMM price and the underlying spot are not separable — no two-price gap. Under CEV with β−1 < 0, the AMM price re-rates faster than fundamentals during stress, exactly the Minsky-consistent pattern. The sign and magnitude of β−1 is therefore a *direct empirical measurement* of the Minsky P_k/P_i gap.
- Cite: Lambert, Lyons, Jiao (2022) Panoptic arXiv:2204.14232; Maymin (2026) arXiv:2603.29763.

---

## §3 Empirical anchor 1 — E8 (Maymin 2026 replication + extension)

Roughly 15-20% of final paper length.

- Brief restatement of CEV-on-AMM operationalization (§2.4) as the empirical lens.
- Bittensor dTAO subnet alpha/TAO bonding-curve pools as the cleanest publicly observable instance of a permissionless CFMM where (a) the productive-investment side (subnet emissions = compute output) and (b) the speculative-asset side (alpha-token re-rating) are priced under a single AMM mechanism.
- Population: ≥75 subnets (Maymin Mar-2026 companion paper uses 128 through 2026-02; our window 2025-08-01 → 2026-05-31 retains structural majority).
- Primary estimand: pooled CEV elasticity β−1 on daily log-price increments; profile-likelihood CI; subnet-clustered SE; pre-pinned MDES = 0.10.
- Natural experiment: Dec-2025 halving (emission-rate cut). Pre-locked pre/post windows 2025-10-15 → 2025-12-14 and 2025-12-16 → 2026-02-14. Estimand Δ(β−1); sign expectation (β−1)_post more negative than (β−1)_pre.
- Sensitivity arms (sign-concordance only): TAO reference quoted in USDC / pooled / USDT.
- Anti-fishing posture: LATAM-operator cohort retrofit is BANNED (closed at G0 HARD-FAIL); halving windows pre-locked; single-primary commitment per estimand.
- **Our contribution beyond Maymin:** Maymin (2026 + Mar-2026 companion arXiv:2603.29751) reports β−1 ≈ −0.86 across 128 subnets; 94% individually negative at p<0.001. We are NOT claiming the replication itself as novel. Our contribution is (i) the PK/Minsky/Kaleckian framing wrapped around the empirical result, (ii) the pre-locked halving natural-experiment as a stress test of the Minsky two-price interpretation (a falsifying test Maymin does not run), (iii) the explicit anti-fishing posture and three-tier reproducibility.
- Cross-link to §2: a negative, significant β−1 is interpreted as direct empirical evidence for the Minsky P_k/P_i AMM-gap proposition (§2.2 + §2.4).

---

## §4 Empirical anchor 2 — E9 (Fabi 2025 prosumer-AMM extension)

Roughly 15-20% of final paper length.

- Brief restatement of Fabi, Nadkarni, Leone, Ferreira (2025) arXiv:2512.24432 Definition 1 + Proposition 1: market mechanism (x, P(x)); anonymity ⇔ AMM existence; linear-pricing closed-form P_n = s_n·r(s,d) − d_n·c(s,d) under coalition-proofness; batch-execution + concentrated-liquidity construction satisfying quasi-concavity / monotonicity / homotheticity.
- Why this extension matters for the bridge: Fabi's result demonstrates the AMM-as-pricing-layer property is *not* a token-denominated artifact. The same axiomatic structure that supports Maymin's CEV-on-AMM result on Bittensor-style token pools supports a prosumer-AMM on a real productive-output denomination (kWh). The Minsky P_k/P_i bridge generalizes.
- Empirical anchor: Colombian AGPE cohort (CREG-174/2021 registered, ≥100 kW ≤ 1 MW solar PV operators) on the XM bolsa-de-energía spot price, with ENSO event-study as exogenous instrument (NOAA ONI declared events 2018-2026). Strong-instrument expectation: El Niño onset → hydro deficit → bolsa spike → AGPE productivity ratio rises (PV marginal cost ≈ 0).
- Counterfactual-M scope per E9-A pre-pin: AMM settlement layer is counterfactual (priced under Fabi 2025 MFG closed-form); cohort is real and permit-registered. Cohort N gated on UPME registry pull (currently DV-BLOCK; deferred to Wave 2 audit per `feedback_data_visibility_gate_before_modeling.md`).
- Anti-fishing posture: seven-field pre-pin LOCKED 2026-05-19; NOAA event windows mechanically derived; primary spec = event-study OLS with HAC + AGPE clustering; per-event jackknife inference given small event count; HALT condition if N_AGPE < 75 → downgrade to E9-B methods-paper-only.
- **Our contribution beyond Fabi:** Fabi et al. provide the closed-form axiomatic prosumer-AMM design with a Paris numerical experiment. We do NOT claim novelty on the closed-form. Our contribution is (i) the first empirical application on a non-Paris dataset, (ii) ENSO as exogenous instrument generating a credibly identified productivity-side shock, (iii) integration into the broader BLR/Minsky bridge — Fabi's prosumer-AMM is a *productive-output-denominated* AMM, the cleanest counterexample to the objection that AMM two-price logic only applies to speculative tokens.
- Cross-link to §2: extending the bridge from token-denominated AMM (§3) to energy-denominated AMM (§4) demonstrates that the Minsky two-price logic is a property of the AMM micro-structure, not of the underlying asset class.

---

## §5 Empirical anchor 3 — E3 (Panoptic-deployment formal results)

Roughly 10-15% of final paper length. This anchor is the most fragile of the
three because E3 was demoted from β-iteration to methods-paper-only on Day 1
(Panoptic mainnet 2024-07 postdates the named macro events E3 was originally
designed to hedge).

- What E3 was originally: Uniswap V3 stablecoin-volatile LP impermanent-loss hedge via Panoptic perpetual options; pre-pin attempted on event windows that turned out to predate Panoptic mainnet.
- Why E3 is methods-paper-only material: the empirical β-iteration is infeasible (no Panoptic settlement venue exists during the named macro-event windows). The *formal pricing result* — that an LP-IL position can be replicated as a short straddle on the underlying pair, and that Panoptic prices this directly via the perpetual-option-on-AMM-position primitive — is independently publishable.
- What E3 contributes to the joint paper:
  - **§5.1 Formal LP-IL ↔ short-straddle replication.** Standard result from Uniswap V3 literature; we restate it under the BLR/Minsky lens: the LP-IL is the *settlement cost* of the AMM-mediated virtual price-discovery layer when the spot reference moves.
  - **§5.2 Panoptic-perpetual-option-on-LP-position pricing.** Reproduce Lambert et al. (2022) pricing identity; show that the Maymin (2026) CEV-on-AMM closed-form composes cleanly with the Panoptic streamed-premium primitive.
  - **§5.3 Stage-correctness disclosure.** Explicit acknowledgement that no live Panoptic LP-IL deployment exists in the named windows; the paper claims pricing-theoretic correctness only, not deployment evidence.
- Cross-link to §2: E3 closes the bridge from theory (§2) to instrument design (§5) by exhibiting the explicit perpetual-option pricing on a concrete LP position. Together with §3 (CEV elasticity) and §4 (prosumer-AMM closed-form), the three anchors triangulate the bridge.

---

## §5.5 Empirical anchor 4 — E10 (GSPS cost-side streamed-liability extension)

Roughly 10-15% of final paper length. This anchor extends the streamed-liability
primitive from receipt-side cohorts (E4 / E5 / E7 / E8 / E9) to a cost-side
cohort and is the family-closure contribution of the paper.

- **Substrate**: continuous-consumption payment streams to data-services API endpoints, instantiated on (a) Superfluid CFA flows on Optimism (PRIMARY; subgraph confirmed live on The Graph Decentralized Network free tier 2026-05-19) and (b) x402 USDC pay-per-query on Base (FUTURE; substrate launched 2026-05-12, parked NON-RETIREMENT-PENDING-MATURITY until 2026-11 re-check).
- **The conceptual move**: the streamed-liability convex hedge has been documented across five receipt-side instances (E4 RetroPGF receipts, E5 Refi claims, E7 Mento seigniorage, E8 Bittensor emissions, E9 AGPE excedentes). E10 is the first cost-side instance — the cohort pays a continuous USDC stream and is exposed to the COP/USD adverse move that raises the COP-denominated cost of the same stream. The Panoptic-perpetual-put M-shape is structurally identical to the receipt-side instances; the only sign-flip is exposure direction. This *closes the family under stream direction*, completing the M-shape generalization claim of §6.
- **Cohort**: Colombian Web3-analyst data-consumption cohort, identified by one of three Colombian-attribution rules (wallet co-occurrence with COPm Mento transactions on Celo; self-disclosed payment-receipt metadata; IP-geo from public gateway logs).
- **Primary estimand**: contemporaneous β on Δlog(COP/USD_t) → Δlog(monthly COP-cost of USDC consumption stream); single-primary commitment per estimand; wild cluster bootstrap by wallet (or per-wallet jackknife if G < 30); pre-pinned MDES = 0.10 SD-units demonstration-grade (or 0.40 confirmatory-grade if N_cohort ≥ 75).
- **X-substrate reuse**: the Δlog(COP/USD) X-substrate is the *same* surface that PASSed in Pair D (β = +0.137, p ≈ 1.5e-08); E10's contribution is to test whether the same X transmits to a different Y channel (data-services-consumption cost vs BPO-offshoring labor cost). The X-side prior is empirically established; the iteration's empirical risk is concentrated on the Y side.
- **Substrate-pivot disclosure (CORRECTIONS-E10-1)**: the original spec targeted x402-on-Base as primary substrate; G3 background research (`superfluid-subgraph-x402-coverage` dispatch, 2026-05-19) revealed x402 substrate-too-young (protocol 8 days old at spec date). Anti-fishing-compliant pivot to Superfluid-Optimism as primary substrate recorded in spec v0.1 §0.5; x402 sub-iteration preserved as NON-RETIREMENT-PENDING-MATURITY with 2026-11 re-check trigger (memory pin: `project_e10_x402_substrate_pending_maturity_2026_11`).
- **Anti-fishing posture**: pre-pin locked in spec v0.1 §5 before any data is touched on Superfluid-Optimism; demonstration-grade vs confirmatory-grade promotion is structurally gated on N_cohort, not magnitude-tunable; sample-window extension to manufacture cohort size is banned; NON-RETIREMENT (cohort < 25) is a valid acceptable outcome.
- **Our contribution beyond prior streamed-liability instances**: the four prior instances (E4 / E5 / E7 / E8 / E9) all hedge receipts. E10 demonstrates that the *same* Panoptic-perpetual-put-with-streamed-premium architecture hedges costs as well, with the cohort's exposure direction as the only sign-flip. This is the structural-completeness claim that the streamed-liability primitive is closed under stream direction — a methodological contribution publishable independent of E10's own empirical β verdict.
- **Cross-link to §2**: a non-zero β on Δlog(COP/USD) → Δlog(monthly stream cost) demonstrates that the Minsky P_k/P_i AMM-gap proposition (§2.2) holds on the *consumption* side as well as the production side. The USDC-priced API service is the P_k-equivalent virtual-economy input price; the COP-denominated productive output is the P_i analog; the gap on the COP/USD pair is the on-chain instantiation of BLR's virtual-vs-real decoupling on the data-services-import margin.

---

## §6 Synthesis — the streamed-liability convex hedge primitive

Roughly 5-10% of final paper length. This is the M-shape contribution and
the bridge to applied work.

- Unified M-shape across E4 (Superfluid R3+ Giveth/q-acc grantee), E5 (RefiColombia donation flow), E7 (Mento Reserve), E8 (Bittensor subnet operator), E9 (Colombian AGPE operator), **E10 (Colombian Web3-analyst data-consumption cohort)**:
  - Investor pays a small recurring premium from a cash-flow stream (in E10, the premium is itself a Superfluid CFA outflow from the same wallet that runs the consumption stream — both flows denominated in USDC, both visible on-chain, hedge end-to-end on a single rail)
  - Premium funds a perpetual-option-on-AMM-position long the convex tail of the cohort-specific X risk
  - Payoff accumulates over time into real-economy exposure (productive inventory, capital equipment, equity in real builders, hedged forward purchases) — exact form depends on cohort
  - The hedge's existence is what *protects* the productive-investment path from the X risk that would otherwise destroy it
- **Family closure under stream direction (E10 contribution)**: E4 / E5 / E7 / E8 / E9 all hedge cohort streams that are *received* (grants / claims / seigniorage / emissions / excedentes). E10 is the first instance hedging a stream that is *paid* (data-services consumption outflow). The Panoptic-perpetual-put-with-streamed-premium M-shape is structurally identical across both directions; the cohort's exposure direction determines only the sign-convention of the option-leg, not the architecture. With E10 added, the streamed-liability primitive is closed under stream direction — a methodological-completeness claim that the M-shape generalizes across the full sign-space of cohort cash flows.
- Distinguished from competing M-shapes:
  - Up-front capital protection (vault-style): does not capture the streamed-liability character of cohort cash flow
  - Speculative leverage (perp-DEX style): inverts the convex-payoff direction; investor pays for downside not upside protection
  - Indemnification (parametric insurance, arXiv:2412.05321): stops at "pay out the loss", does not accumulate productive capital
- The streamed-liability primitive is the *operational* form the BLR/Minsky bridge takes when instantiated as an investment-productivity instrument. §2.3 (Kaleckian premium-funded ratchet) is the theoretical justification; §6 is the operational specification.
- Cite: arXiv:2412.05321 (parametric-insurance closest analog); Superfluid documentation (streamed-payment primitive); Panoptic streamed-premium primitive (Lambert 2022).

---

## §7 Anti-fishing posture

Roughly 5% of final paper length. Reviewer-defensive section.

- **The methods-paper is publishable on the theoretical bridge alone.** §2 stands without any single §3/§4/§5 β-verdict. The empirical anchors are illustrations, not proofs.
- **Carry-forward of HALT discipline.** Each empirical-anchor pre-pin (E8 §3-§4, E9-A §4) is locked before data is touched; NON-RETIREMENT is an honest exit; threshold tuning is banned.
- **No cherry-picking across anchors.** If E9-A FAILS its β-iteration (sign reversal or CI containing zero), the methods paper still proceeds — the bridge (§2) + E8 (§3) + E3 (§5) carry the contribution. If E8 FAILS (Maymin's β−1 ≈ −0.86 result fails to replicate on the extended window), we report the FAIL honestly and lean on E9 + E3 + the theoretical bridge.
- **NON-RETIREMENT on E9-A leaves the paper intact.** The E9-A pre-pin's HALT condition (`N_AGPE < 75` → downgrade to E9-B methods-paper-only) is a feature, not a bug — the methods-paper contribution survives degraded empirical anchoring because §2 is the contribution.
- **Cross-anchor robustness as substitute for single-anchor power.** Three independent empirical illustrations on three different X domains (compute output / energy output / LP-IL settlement) substitute for the deeper-but-narrower power any single iteration could deliver.
- **Anti-fishing for the bridge itself.** §2 is pre-stated and not re-tuned across empirical-anchor results. The bridge is the conceptual hypothesis; the anchors test whether the bridge has empirical purchase, not whether the bridge is true.

---

## §8 Citation skeleton

### Tier 1 — PK theoretical anchors (required)
- Bhaduri, Laski, Riese (2006). "A model of interaction between the virtual and the real economy." *Metroeconomica* 57(3): 412-427.
- Minsky, H. P. (1986). *Stabilizing an Unstable Economy.* Yale UP.
- Minsky, H. P. (1975). *John Maynard Keynes.* Columbia UP.
- Kalecki, M. (1971). *Selected Essays on the Dynamics of the Capitalist Economy.* Cambridge UP.
- Keynes, J. M. (1936). *General Theory*, Ch. 12 + Ch. 17.
- Bhaduri, A. & Marglin, S. (1990). "Unemployment and the real wage: the economic basis for contesting political ideologies." *Cambridge JE* 14(4).
- Bhaduri, A. (2011). "Financial fragility and crisis." (Cambridge JE / Levy WP 593 / WIIW WP 65.)
- Soddy, F. (1926). *Wealth, Virtual Wealth and Debt.* (historical anchor for the "virtual wealth" terminology BLR inherit.)
- Tymoigne, E. (2010). "Minsky's Two-Price Theory of Investment." Levy Economics Institute WP.

### Tier 2 — Modern PK financialization
- Stockhammer, E. (2004). "Financialization and the slowdown of accumulation." *Cambridge JE* 28(5).
- Hein, E. & van Treeck, T. (2024). "PK financialization-in-growth-models." ifso WP 32.
- delli Gatti, Gusella, Ricchiuti (2025). arXiv:2511.04348 — regime-switching Minskian empirics across USA/FR/DE/CA/AU/UK.
- Solomon, S. & Golo, N. (2014). arXiv:1402.0176 — network/percolation Minsky.

### Tier 3 — AMM theory + Panoptic + Maymin + Fabi (load-bearing)
- **Lambert, Lyons, Jiao (2022). Panoptic. arXiv:2204.14232** — Abrigo's M-layer; perpetual options on AMM positions.
- **Maymin, P. (2026). "Option Pricing on Automated Market Maker Tokens." arXiv:2603.29763** — CEV-on-AMM closed-form pricing.
- **Maymin Mar-2026 companion. arXiv:2603.29751** — 128-subnet empirical fit; β−1 ≈ −0.86; halving as natural experiment.
- **Fabi, Nadkarni, Leone, Ferreira (2025). "Automated Market Making for Energy Sharing." arXiv:2512.24432** — MFG-AMM closed-form; Paris numerical experiment.
- Bartoletti et al. (2021). AMM theory. arXiv:2102.11350.
- Xu et al. (2021). AMM SoK. arXiv:2103.12732.
- Jensen et al. (2021). arXiv:2105.02782.
- Adams, Zinsmeister, Salem, Keefer, Robinson (2021). *Uniswap v3 Core* whitepaper.
- Adams et al. (2024). *Uniswap v4* whitepaper.

### Tier 4 — On-chain bridge analogs + tokenization
- Catalini, C. & Gans, J. (2016/2020). NBER WP 22952.
- Xia et al. (2025). RWA tokenization. arXiv:2503.01111.
- arXiv:2412.05321 — decentralized/parametric insurance (closest extant academic analog of the premium-funded ratchet).
- von Wachter et al. (2021). arXiv:2102.04227.

### Tier 5 — Bittensor / dTAO
- Bittensor / Yuma Consensus / dTAO whitepaper (citation per Maymin 2026 reference list).

### Tier 6 — Mento / Celo / local-currency on-chain (positioning, may be footnote-only)
- Mento Protocol docs (industry-only, no peer-reviewed write-up — explicit "positioning opportunity" footnote).

### Reserved-for-bibliographic-search
- arxiv MCP search (`mcp__arxiv__*`) reserved for Wave-2 verification: confirm Maymin 2603.29763 / 2603.29751 abstracts and Fabi 2512.24432 abstract; surface any 2026 Q1-Q2 follow-ups citing either. NOT run within this outline session per task scope.

---

## §9 Multi-year timeline

Realistic publication timeline; sequencing of E3 / E8 / E9 empirical work into
the joint paper; first-submission target.

| Quarter | Workstream | Milestone |
|---|---|---|
| 2026-Q2 (now) | E8 spec → implementation; E9-A DV gate; E10 spec v0.1 drafted + v0.2 substrate-pivot amendment; this outline | E8 v0.2 post-review; E9-A registry-pull retry; E10 v0.2 post-CORRECTIONS-E10-1 + RC+CR 2-way review; outline LOCKED |
| 2026-Q3 | E8 Notebook 02-03 (CEV fit + halving); E9-A data ingest (gated on DV); E3 formal pricing write-up; E10 G3 plan + cohort enumeration on Superfluid-Optimism subgraph | E8 verdict (§7 of E8 spec); E9-A verdict OR NON-RETIREMENT; E3 §5 draft ready; E10 G4 dispatch |
| 2026-Q4 | E8 Notebook 04-05 (sensitivity + verdict); E9-A robustness arms; E10 panel construction + β estimation; joint paper §2 draft | E8 methods-paper notebook frozen; E10 verdict OR NON-RETIREMENT; §2 theoretical core LaTeX draft v0.1 |
| **2026-11 (parallel marker)** | **E10 x402-on-Base substrate re-check trigger** per CORRECTIONS-E10-1 memory pin — verify (a) x402 protocol age ≥ 6 months from 2026-05-12 launch, (b) ≥ 50 Colombian-attributable payer wallets identifiable on Base x402 endpoints | If both conditions hold: unblock E10-x402 sub-iteration v0.2 dispatch; otherwise extend NON-RETIREMENT-PENDING-MATURITY by 6 months |
| 2027-Q1 | Joint paper §1 + §5.5 + §6 + §7 + §8 drafting; first-pass internal review (audit-econ Delphi 3-Opus) | Joint paper v0.5 internal-review-cleared |
| 2027-Q2 | Revisions; arxiv-MCP literature-completeness pass; pre-submission solicitation (Stockhammer / Hein / Bhaduri contact) | Joint paper v0.9 pre-submission |
| 2027-Q3 | First submission to Cambridge JE | Submitted |
| 2027-Q4 → 2028-Q2 | Cambridge JE review cycle (CJE typical 6-9 months); ROPE/Metroeconomica fallback if rejected | R&R or rejection |
| 2028-Q3 | Revisions or resubmission to next venue | Accepted (target) |

**Sequencing constraints:**

- §2 theoretical core can be drafted in parallel with E8 / E9 / E10 empirical work; it does not block on any β verdict.
- E8 verdict (expected 2026-Q3) is the lowest-risk anchor (Maymin replication on extended window; high prior on PASS given Maymin Mar-2026 β−1 ≈ −0.86 across 128 subnets).
- E9-A verdict is highest-risk (DV gate not yet cleared; cohort N gated on UPME registry; small event count → demonstration-grade verdict at best).
- E3 §5 write-up is medium-risk (pricing-theoretic content is standard; the contribution is the BLR/Minsky framing wrapper).
- **E10 verdict is medium-risk on the Y side** (data-consumption cohort N on Superfluid-Optimism with Colombian-attribution filter is the main risk; X-side prior is established from Pair D PASS); the §5.5 *methodological-completeness claim* (family closure under stream direction) is independent of E10's empirical β verdict and survives NON-RETIREMENT.

---

## §10 Outstanding questions / known weaknesses

Reviewer-defensive section. Surfaces what makes the paper fragile.

1. **Maymin already published the headline E8 result.** Our contribution on §3 must be the *bridge* (PK framing, halving natural-experiment as Minsky falsification test, anti-fishing posture, three-tier reproducibility) not the *replication*. Reviewer may discount the empirical anchor as "we redid what Maymin did." **Mitigation:** lead §3 with the halving natural-experiment (which Maymin does not run) and the BLR/Minsky framing; subordinate the pooled CEV fit as a sanity-check sub-result.

2. **Fabi's prosumer-AMM may not yet have independent confirmation.** E9 is the first non-Paris empirical application; reviewers may demand more numerical validation of the Fabi closed-form before accepting our application. **Mitigation:** report the Fabi linear-pricing identity P_n = s_n·r(s,d) − d_n·c(s,d) explicitly and demonstrate that our event-study event-window estimates satisfy the identity's sign and monotonicity properties under ENSO shocks; supplement with the Fabi Paris numerical-experiment results as comparison.

3. **Venue conservatism toward crypto-AMM work.** Cambridge JE / ROPE editors may regard the AMM machinery as outside the journal's traditional remit. **Mitigation:** open §1 with BLR and Minsky; the formal-finance content enters only in §2.4 and the empirical sections; framing is heterodox-economics-first, fintech-second.

4. **CEV-vs-GBM identification on cross-subnet pooled data (E8 §3).** Profile-likelihood CI on β−1 is well-behaved at N ≥ 75 subnets, but the cross-subnet correlation structure is not fully resolvable. **Mitigation:** report subnet-clustered SE for the auxiliary mean-effects table; per-subnet individual β−1 distribution as robustness; permutation-placebo for the §4.2 halving natural-experiment.

5. **E9-A DV-BLOCK risk.** If UPME registry pull continues to fail and the XM-API-side registered-generators query also fails, E9-A NON-RETIREMENT is the honest outcome. **Mitigation:** the paper survives via §2 + §3 (E8) + §5 (E3); §4 (E9) becomes a "design-only" section referencing the Fabi closed-form and noting the empirical application is pending data access.

6. **Stage-2 firewall in §5 (E3).** A reviewer may charge that the E3 contribution is "just an unsettleable instrument design." **Mitigation:** §5 explicitly frames as pricing-theoretic correctness, not deployment evidence; cites Maymin (2026) as the precedent that closed-form pricing results are publishable independent of live settlement.

7. **PK-framing vs quant-finance-framing tradeoff.** The contribution sits at the intersection of two readerships. Picking the wrong opening tone alienates one. **Mitigation:** §1 elevator is PK-first (lead with BLR, Minsky, Kalecki); §2.4 + §3 + §5 are quant-finance-readable but never become the framing. If Cambridge JE rejects on "too much DeFi machinery", rewrite §2.4 + §3.1 with the AMM/CEV content pushed to an appendix and resubmit to ROPE.

8. **Cross-anchor coherence.** Three anchors on three different X domains may read as "kitchen sink" to a skeptical reviewer. **Mitigation:** §6 (synthesis) explicitly unifies the M-shape across all five Abrigo iterations (E4 / E5 / E7 / E8 / E9); the three illustrated anchors are not arbitrary but were each independently selected at G0 gates, and §7 anti-fishing posture explains why three weaker independent anchors substitute for one deeper anchor.

9. **The bridge claim itself may be over-strong.** "AMMs *endogenously* instantiate the Minsky gap" is a structural claim. A reviewer may respond that AMMs are *one* venue exhibiting two-price behavior, not a privileged one. **Mitigation:** §2 hedges the strong form: the claim is that *concentrated-liquidity* AMMs instantiate the gap in a path-dependent, LP-NPV-locked-in form, not that AMMs are the unique venue. The privileged property is the pricing layer (Panoptic perpetual options on AMM positions) being computationally explicit, not the gap itself.

10. **No live Panoptic LP-IL deployment evidence anywhere in the paper.** Even §5 is pricing-theoretic, not deployment-empirical. A reviewer may regard this as fatal. **Mitigation:** Maymin (2026) and Fabi et al. (2025) are themselves pricing-theoretic / numerical-experiment papers without live deployment, and they are published. The methods-paper category is well-established and does not require live settlement.

11. **E10 substrate-too-young caveat (CORRECTIONS-E10-1).** The original E10 spec targeted x402-USDC-on-Base as the primary substrate, but x402 launched only 2026-05-12 — the protocol is too young (8 days at spec date; ≤ 6 months at first-paper-draft date) to populate a Colombian-cohort sample window. The anti-fishing-compliant pivot was to switch the E10 primary substrate to Superfluid CFA flows on Optimism, which has years of history and a confirmed Graph free-tier subgraph (`48YRvi7…HBXxT`). **Mitigation:** the §5.5 anchor proceeds on the Superfluid-Optimism substrate; the x402-on-Base sub-iteration is preserved as NON-RETIREMENT-PENDING-MATURITY with explicit 2026-11 re-check trigger (memory pin `project_e10_x402_substrate_pending_maturity_2026_11`). The methodological-completeness claim of §5.5 (family closure under stream direction) does not depend on which payment-protocol substrate hosts the empirical instance — it depends only on the existence of an observable cost-side payment stream, which Superfluid CFA on Optimism provides at scale. A reviewer asking "why not x402 since the paper repeatedly references it?" gets the explicit substrate-maturity disclosure plus the 2026-11 re-check path as part of the paper's future-work section.

---

## §11 Sources verified

- `memory/reference_bhaduri_laski_riese_concept_bridge.md` — PK literature review + concept-bridge map; "Cleanest unfilled gap" section identifies the exact bridge this paper proposes; read 2026-05-19.
- `docs/specs/2026-05-18-e8-dtao-maymin-methods-paper-design.md` v0.1 DRAFT — E8 standalone spec; CEV β−1 pre-pin; halving natural-experiment; §4.3 BLR/Minsky concept-bridge claim; read 2026-05-19.
- `scratch/2026-05-18-wave1/E9A_prepin/prepin.md` LOCKED 2026-05-19 — E9-A seven-field pre-pin; Fabi 2025 Definition 1 + Proposition 1 + linear pricing identity; NOAA ONI event windows; read 2026-05-19.
- `memory/project_abrigo_framing_clarification_investment_productivity.md` — generalized framing (investment productivity, not wage→capital); §2.3 streamed-liability primitive grounding; read 2026-05-19.
- `memory/feedback_data_visibility_gate_before_modeling.md` — DV gate ordering; E9-A DV-BLOCK status; read 2026-05-19.
- `CLAUDE.md` Abrigo Operating Framework section — theoretical-anchor pointers; ideal-scenario modeling caveat for §5 (E3) stage discipline; read 2026-05-19.
- `docs/specs/2026-05-19-e10-gsps-x402-data-stream-fx-hedge-design.md` v0.1 DRAFT — E10 spec; cost-side streamed-liability extension; CORRECTIONS-E10-1 substrate-pivot block; Superfluid-Optimism primary substrate; x402-on-Base future substrate parked NON-RETIREMENT-PENDING-MATURITY 2026-11 re-check; read 2026-05-19.
- `memory/project_e10_x402_substrate_pending_maturity_2026_11.md` — portfolio-level commitment to re-check x402 substrate at 2026-11; preserves substrate-pending state across spec churn; read 2026-05-19.
- `memory/feedback_dune_last_resort_exhaust_free_resources.md` — cost-allocation rule whose application drove E10's existence; Graph free tier dominates Dune Plus $390/mo for E10 by 20× headroom; read 2026-05-19.

**Arxiv MCP not invoked this session** — Maymin (arXiv:2603.29763 + arXiv:2603.29751) and Fabi (arXiv:2512.24432) arxiv IDs verified via the E8 spec and E9-A pre-pin which cite them directly. Per task scope ("Don't run extensive literature searches — the outline cites known anchors"), arxiv MCP queries are reserved for Wave-2 verification when the paper enters drafting.
