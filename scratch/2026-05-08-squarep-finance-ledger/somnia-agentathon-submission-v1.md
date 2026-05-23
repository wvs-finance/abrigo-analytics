# Somnia Agentathon — Application Drafts

**URL:** https://www.encodeclub.com/programmes/agentathon
**Pulled forward from Day 27 (June 3) plan task** — user filled application 2026-05-08

## Field: "What do you want to build?" — long version (~270 words)

**Abrigo** — a permissionless on-chain hedging instrument that converts a wage earner's recurring micro-premium into productive-capital exposure over time, settled by an autonomous reactive contract on Somnia.

**The problem.** In emerging markets, wage earners can't accumulate productive capital from a pure-savings start because the macro risks along the path — FX devaluation, inflation regime breaks, sectoral demand shocks — wipe out savings before they compound. We've empirically validated the structural gap on Colombian data: a Colombian-services hedge correlates with COP/USD lag at β = +0.137, p ≈ 1.5e-08 (Pair D). The hedge is real; the on-chain instrument isn't built yet.

**What we're building.** A **premium-funded ratchet**: the holder streams a small recurring premium from wage income (cCOP via Superfluid); an autonomous on-chain agent maintains a long-gamma convex position whose payoff and roll yield accumulate into capital exposure across time. The hedge's *existence* is what creates the capital position — without it, the wage earner never crosses the boundary.

**Why Somnia.** The ratchet is fundamentally reactive: it must respond to oracle price moves, time intervals, and balance thresholds without external keepers, with low-latency settlement legacy L1s can't deliver economically. Somnia's reactive primitive collapses what would otherwise be a multi-component keeper architecture into a single autonomous on-chain agent — which is the real product.

**Demo.** Somnia testnet: wallet streams cCOP premium via Superfluid; reactive agent rebalances the long-gamma position on each oracle tick; minimal frontend visualizes the ratchet building capital exposure across simulated time.

## Field: "What do you want to build?" — tight version (~120 words)

**Abrigo** — a permissionless on-chain hedge that converts a wage earner's recurring micro-premium into productive-capital exposure, settled by an autonomous reactive agent on Somnia.

Wage earners in emerging markets can't accumulate productive capital from savings because FX, inflation, and sectoral risks wipe out compounding. We empirically validated this on Colombian data: β = +0.137, p ≈ 1.5e-08.

Holders stream cCOP premium via Superfluid; a Somnia reactive contract maintains a long-gamma position; payoff and roll yield ratchet into capital exposure across time.

Somnia's reactive primitive collapses what would be a multi-component keeper architecture into a single autonomous on-chain agent — which *is* the product. Demo: testnet wallet → reactive agent rebalancing → frontend visualizing the ratchet building capital across simulated time.

## Positioning notes (for follow-up fields if asked)

- **Brand name:** Abrigo (Spanish: shelter/coat). Parent lab: D2P Finance (@D2pFinance on X).
- **Empirical foundation:** Pair D PASS verdict 2026-04-28 — β = +0.137, p ≈ 1.5e-08 on BPO offshoring × COP/USD lag. See `memory/project_pair_d_phase2_pass.md`. If judges ask for methodology, we have the notebook trio + 3-way reviewer sign-off.
- **Panoptic naming policy:** do NOT name Panoptic in pitch copy per `memory/project_ran_product_framing.md`. Use "long-gamma convex position" or "perpetual options primitive" instead.
- **Crypto abstraction:** mainstream wage-earner positioning hides crypto from end-user copy; tech-disclosure fields can be explicit. Two-tier rule per `memory/project_abrigo_two_tier_field_rule.md`.
- **Implementation partners named:** Superfluid (premium streaming), Mento (cCOP). Reactive Network NOT named in this Somnia-side copy (saved for UHI9-side application where Reactive Network is sponsor).
- **What's NOT named here:** Panoptic, ThetaSwap (former internal name), Angstrom, Uniswap v4 / UHI9 (the Hookathon submission is a parallel separate channel, not relevant to Somnia judges).

## Likely follow-up fields and quick drafts

If the application asks any of these, drafts are ready:

- **Team size:** 1 (solo founder; agent-assisted)
- **Track:** Real-world use cases on Somnia's Agentic L1 (financial inclusion / DeFi / structured products)
- **Status:** Empirical foundation validated (Pair D PASS); reactive contract architecture in design; targeting Somnia testnet demo for Agentathon
- **What we need from Somnia:** access to Agentic L1 testnet RPC, oracle integration documentation, reference reactive-contract patterns
- **Why we'd ship:** existing 34-day execution sprint already running for parallel UHI9 capstone (June 11); Somnia reskin is low marginal engineering cost given architectural overlap
