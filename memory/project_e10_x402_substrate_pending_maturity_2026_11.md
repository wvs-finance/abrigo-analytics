---
name: e10-x402-substrate-pending-maturity-2026-11
description: E10 GSPS iteration's x402-on-Base substrate path is NON-RETIREMENT-PENDING-MATURITY per CORRECTIONS-E10-1 (2026-05-19); re-check trigger 2026-11 when x402 protocol is ≥6 months old. Primary substrate pivoted to Superfluid CFA on Optimism.
metadata:
  type: project
---

E10 (Generalized Subscription Payment Stream — x402-USDC data-consumption FX hedge) spec v0.1 DRAFT 2026-05-19 originally targeted x402 USDC payment events on Base as primary cohort substrate. G3 background research (`superfluid-subgraph-x402-coverage` dispatch, 2026-05-19) closed the substrate-feasibility question and found:

- **x402 USDC gateway on Base went live 2026-05-12** (8 days before spec date)
- **Original cohort sample window (2025-12 → 2026-05) is structurally infeasible** — substrate did not exist before 2026-05-12; cohort cannot be observed at meaningful N
- CORRECTIONS-E10-1 recorded the substrate-too-young finding per `feedback_pathological_halt_anti_fishing_checkpoint.md`
- Primary substrate pivoted to **Superfluid CFA flows on Optimism** (subgraph `48YRvi7PHbX4RJChq4nF8DpmJGZxcvUgwfdf8QoHBXxT` on Graph Decentralized Network free tier; 100k queries/mo, 20× headroom on E10 budget; PASS-FREE, dominates Dune Plus $390/mo at $0/mo)
- x402-on-Base path preserved as **NON-RETIREMENT-PENDING-MATURITY** sub-iteration in §9 verdict ladder

**Re-check trigger (2026-11)**: revisit the x402 sub-iteration when BOTH conditions hold:
1. x402 protocol age ≥ 6 months from 2026-05-12 launch (earliest: 2026-11-12)
2. ≥ 50 Colombian-attributable payer wallets identifiable on Base x402 endpoints (any of the three [DEF-1] attribution rules)

Until both conditions hold, do NOT propose x402-on-Base as the primary substrate for any new Abrigo iteration. Superfluid CFA on Optimism is the validated substrate alternative.

**Why this memory exists, not just the spec annotation**: the spec is an iteration artifact that may be archived or revised; the re-check date is a portfolio-level commitment that must survive spec churn. Analogous to `[[p1-sn18-spec-finalized-sha256-pinned-parked-2026-04-27]]` preserving the parked-iteration substrate state.

**How to apply**:
- When the user proposes an x402-payment-based iteration before 2026-11, surface this memory and confirm whether the re-check conditions are satisfied
- When 2026-11 arrives, re-dispatch the substrate-coverage research to verify both conditions; if confirmed, unblock E10-x402 sub-iteration v0.2 dispatch
- Do NOT recommend acquiring GRT-on-Arbitrum for E10 work; USDC-on-Base via x402 is the only crypto-pay path on The Graph, and the Superfluid-Optimism path uses Graph free tier directly with no payment

**G3 research caveats preserved for re-check** (from agent `superfluid-subgraph-x402-coverage` 2026-05-19):
- x402 per-query USDC price is opaque (returned dynamically in 402 header; no published flat rate)
- Whether Superfluid V1 Optimism subgraph specifically is routable via the `/api/x402/...` endpoint is UNCONFIRMED — would require live curl probe at re-check
- Subgraph sync freshness UNCONFIRMED (explorer panel didn't render at fetch); resolve via `_meta { block { number } }` GraphQL probe before any E10 production query
- The Graph canonical x402 announcement blog returned HTTP 500 during G3 fetch — endpoint stability concern as of 2026-05

## Links

[[p1-sn18-spec-finalized-sha256-pinned-parked-2026-04-27]] — analogous substrate-pending state for SN18 Cortex.t
[[dune-last-resort-exhaust-free-resources]] — the cost-allocation rule whose application drove E10's existence
[[pair-d-phase2-pass]] — X-substrate (COP/USD lag β = +0.137) reused by E10
[[pathological-halt-anti-fishing-checkpoint]] — the rule that mandated CORRECTIONS-E10-1 instead of silent substrate switch
