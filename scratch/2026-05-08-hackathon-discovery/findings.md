# Hackathon Discovery — Findings

**Date:** 2026-05-08
**Window:** 2026-05-15 → 2026-07-15
**Scope:** Crypto/Web3 hackathons + continuous builder programs evaluated for Abrigo fit
**Inputs:** User-named events (Atrium UHI9, Somnia Agentathon, Celo Proof of Ship, Algebra/Panoptic/Mento sponsorships) + parallel research agent sweep

## In-window candidates (sorted by fit)

| # | Name | Organizer | Submission deadline | Prize (USD) | Chain | Tracks/themes | Fit | Source |
|---|---|---|---|---|---|---|---|---|
| 1 | **UHI9 capstone Hookathon** *(user enrolled)* | Atrium Academy / Uniswap Foundation | **June 11, 2026** | ≥$15k cohort prize pool (sponsors per Atrium tier table: $5k/$10k/$15k slots) | Uniswap v4 | Impermanent Loss & Yield Systems — IL-protection hooks, structured-yield AMMs | **5/5** — verbatim match for Abrigo's premium-funded ratchet over a Panoptic-style LP position | https://atrium.academy/uniswap |
| 2 | **Mantle Turing Test 2026 — Phase 2 "AI Awakening"** | Mantle + Bybit + Byreal + BGA + DoraHacks | **June 15, 2026** | $100k | Mantle (EVM L2) | AI Trading & Strategy; Agentic Wallets & Economy; ERC-8004 agent identity | **4/5** — Agentic-wallet track maps to premium-funded ratchet UX; +4 days vs UHI9; reskin from same codebase | https://chainwire.org/2026/04/23/mantle-launches-turing-test-hackathon-2026 |
| 3 | **Celo Proof of Ship** *(user enrolled)* | Celo Foundation / CeloPG | **Continuous** (monthly) | $5,000 cUSD/month | Celo (EVM) | Onchain reputation; AI-evaluated on shipping cadence; Karma GAP + Farcaster submission | **4/5** — continuous channel; rewards public shipping (vs UHI9's one-shot reveal); Mento ecosystem alignment | https://www.celopg.eco/programs/proof-of-ship |
| 4 | **Somnia Agentathon (Encode × Somnia)** | Encode Club / Somnia | TBD — user has URL | TBD | Somnia L1 (EVM-compatible) | Agentic L1, AI-agent infra | **TBD/5** — secondary reskin target; somnia-mcp tools already in env | https://www.encodeclub.com/programmes/agentathon (page exists, JS-rendered, not fetchable) |
| 5 | **UHI10 application** *(reserve)* | Atrium Academy | **May 15, 2026** primary / June 21 late | Tuition covered + ≥$15k cohort prize | Uniswap v4 | "The Fair Flow Frontier" — Sustainable Liquidity & MEV Protection | **3/5 as reserve** — only fires if UHI9 capstone is missed; Hookathon is in September | https://atrium.academy/uniswap |
| 6 | ETHGlobal New York 2026 | ETHGlobal | June 14, 2026 (in-person) | TBA (~$300-500k aggregated) | Ethereum + L2s | Mixed sponsor bounties | **0/5 — ruled out** | Travel from Colombia > entire $800 envelope |
| 7 | ETHGlobal Lisbon 2026 | ETHGlobal | July 26, 2026 (in-person) | TBA | Ethereum | EU-DeFi heavy | **0/5 — ruled out** | Same travel-cost ruling |

## Recommended portfolio

- **Primary**: UHI9 capstone Hookathon (June 11) — already enrolled; theme verbatim matches product framing; multi-prize potential via Algebra/Panoptic/Mento sponsor tracks
- **Secondary**: Mantle Turing Test Phase 2 (June 15) — same codebase reskinned; Agentic Wallets track validates the streaming-premium UX even off-Panoptic; $100k pool
- **Continuous**: Celo Proof of Ship — submit Mento-side / Celo-side infrastructure for monthly reputation building; tension with Hookathon "wow reveal" requires careful what-to-publish-when discipline
- **Tertiary** (pending URL verification): Somnia Agentathon — secondary reskin if dates allow
- **Reserve** (only if June 11 capstone missed): UHI10 application by May 15 → September Hookathon
- **Out**: ETHGlobal NY/Lisbon (travel cost > envelope)

## Strategic tensions surfaced

1. **Public-shipping cadence (Celo Proof of Ship) vs reveal-day polish (UHI9 Hookathon)**. Resolution: ship infrastructure (Mento integration, Celo-side deployment, agent identity primitives) publicly for Proof of Ship reputation; hold the Panoptic settlement / capstone hook narrative for the June 11 Hookathon reveal. Two artifacts, one codebase.

2. **Submission count vs solo+34-day capacity**. Realistic concurrent capacity is 2 submissions sharing a codebase, not 4 independent ones. UHI9 + Mantle reskin is the maximum responsible plan; Somnia pulls in if and only if its deadline is after June 15 (giving 4 free days).

3. **Algebra/Panoptic/Mento sponsor tracks within UHI9** are *intra-channel multipliers*, not separate channels. Optimizing for them means tailoring the *narrative* (not building separate features) — Algebra-flavored reading: concentrated-liquidity hook; Panoptic-flavored reading: perpetual-option backing; Mento-flavored reading: local-currency stablecoin (cCOP, COPm) pair.

## Ruled out (pre-window or wrong fit)

Concluded before 2026-05-15: Hyperliquid London (Jan), Aleph BA (March), HackMoney 2026 (Feb), Solana Frontier (May 11), x402 SF Agentic Commerce (Feb 11–13), Coinbase "Agents in Action" (no 2026 successor), Sonic DeFAI (Feb 2025), Tether Galactica WDK (Mar 22–23), Mento Global Stablecoin (Apr–May 2025), MNEE (Jan 12), Kite AI Global (Apr 26), HashKey Horizon (Apr 23), EasyA Consensus Miami (May 5–7), ETHPrague (May 8–10), Encode "Commit to Change" Comet (Jan 13).

Wrong-chain/scope: StableHacks (Solana), Pump.fun Build in Public (Solana), Casper, ARC Prize, Agents Without Masters NEAR, Hedera Apex.

## Could not verify — needs user input

1. **Somnia Agentathon URL** — page exists at encodeclub.com/programmes/agentathon but JS-rendered; user has source pending share
2. **UHI9 sponsor-track prize pool breakdown** — Algebra/Panoptic/Mento amounts are private to enrolled cohort
3. **Superfluid Wave Pool** — continuous program, not in scope unless user wants continuous-bounty channels added
4. **Panoptic direct sponsorship** — Cantina bug bounty paused; custom partnership only via direct contact

## Implications for budget memo

- **No new line items** required: Farcaster account + Karma GAP project listing for Celo Proof of Ship are free
- **Mantle reskin** uses same Solidity + same Alchemy account; marginal cost ~$0
- **Somnia reskin** uses already-configured somnia-mcp; marginal cost ~$0
- **UHI10 reserve** is a $0 application; only consumes attention if June 11 is missed
- The $800 envelope is unchanged; what changes is the *recovery-channel architecture* (single-event → portfolio)
