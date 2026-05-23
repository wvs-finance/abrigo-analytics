---
name: dune-last-resort-exhaust-free-resources
description: User directive 2026-05-19 — Dune paid tier ($390/mo Plus) is LAST RESORT. Exhaust all free resources (Etherscan, native chain RPCs, The Graph subgraph free tier, Allium free tier, Covalent free tier, BigQuery public crypto datasets, custom indexer on free RPC) before considering paid Dune. Paid-Dune is only approved if ALL or near-ALL active iterations converge to require it for explanatory power that no free combination can replicate.
metadata:
  type: feedback
---

## Rule

For every active or candidate Abrigo iteration, **Dune paid tier ($390/mo Dune Plus
or higher) is treated as the LAST RESORT data path**. Before any iteration commits
to paid Dune:

1. **Exhaust free-tier alternatives** first. Candidate free paths to check (per
   iteration's domain):
   - **Etherscan / Optimism Etherscan / Arbiscan / Basescan / Celoscan APIs**
     (free tier; rate-limited but generous)
   - **Native chain RPCs** (Optimism public RPC, Celo Forno, Ethereum public RPC,
     Subtensor EVM RPC, Polygon public RPC, etc.) — direct on-chain reads
   - **The Graph subgraph queries on free tier** — when a maintained subgraph
     covers the contract surface
   - **Allium free tier**, **Covalent free tier**, **Goldsky free tier** — newer
     analytics platforms with no-cost entry tiers
   - **Google BigQuery public crypto datasets** (`bigquery-public-data.crypto_*`,
     `cryptocompare_*`) — free query budget per month
   - **Custom indexer** on free RPC + local Parquet store (~1-3 days engineering
     cost, zero recurring cost)
   - **Provider-specific free APIs** (Taostats free, XM-API free, NOAA free,
     Banrep datos.gov.co free, etc.)

2. **Document the audit**: every iteration's data-visibility check (per
   [[data-visibility-gate-before-modeling]]) must explicitly enumerate which free
   paths were tried, which worked, and which failed. The DV verdict moves from
   PASS-FREE to PASS-QUOTED only when no free combination can replicate the
   needed data scope.

3. **Convergence test for paid-Dune approval**: paid Dune is approved ONLY if:
   - All or near-all (≥3 of currently-active) iterations converge to require
     Dune for explanatory power, AND
   - No free combination can replicate the cross-iteration data scope at any
     reasonable engineering cost, AND
   - User explicitly approves the subscription decision

   Single-iteration requirements for paid Dune do NOT trigger approval — the
   iteration is parked or reframed to use free paths instead.

## Why

Per user (2026-05-19, post-Wave-2-DV-audit revealing E4 routine-refresh quoted
at Dune Plus ~$390/mo):

> "For the Dune path here, that's the last resort. If any of the specifications
> or works we're pursuing required, all converge to require a Dune for
> explanatory power, then we can consider it. Exhaust all free resources."

The rule prevents the failure mode of locking the portfolio into a $390+/mo
recurring cost on the basis of a single iteration's preferred data path, when
free alternatives (or a one-time indexer build) typically cover the same scope
at the cost of ~1-3 engineering days. Recurring subscription cost compounds
fast across iterations; engineering effort to use free paths is one-time.

## How to apply

**Immediate effect**: E4 narrowed Superfluid R3+ iteration cannot proceed to
routine-refresh Dune queries until free-path audit completes. Wave-1.4
one-shot panel (already in hand, no further Dune cost) remains usable for
historical-panel analysis. Sub-task E4.0.B (7-day swap-age histogram) must be
attempted via free paths before any further Dune credit burn.

**Per-iteration audit checklist before any Dune query**:

| Question | Action |
|---|---|
| Is the data on-chain? | Try chain RPC + Etherscan API first |
| Is there a maintained subgraph? | Try The Graph free tier |
| Is the cohort small enough to backfill via custom indexer? | Build indexer (1-3 days, zero recurring cost) |
| Is the data covered by a public BigQuery dataset? | Try `bigquery-public-data.crypto_*` |
| Is there a provider-specific free API? | Use it (Taostats, XM-API, Banrep, NOAA, etc.) |
| If all above fail, is paid Dune the only path? | Park iteration; check for convergence with other active iterations |

**Convergence-tracking**: maintain a running list of iterations whose only
remaining data path is paid Dune. The list lives in
`scratch/portfolio_dune_convergence_tracker.md` (to be created on first
convergence-candidate). Subscription decision triggers when the list reaches
≥3 iterations AND all have failed free-path audits.

## What this rule does NOT prohibit

- **Free Dune credit usage** (the ~25-credit/month free tier; one-shot queries
  burning ≤100 credits one-time). The Wave-1.4 one-shot panel for E4 was OK
  under this rule.
- **Paid Dune for explicitly time-bounded, one-time research** if user
  pre-approves on a per-task basis (not portfolio-wide subscription).
- **Engineering-time investment** to build free-path alternatives — that's the
  intended path under this rule.

## Anti-fishing carry-forward

Free-path-first does NOT relax anti-fishing invariants. Pre-pin discipline,
HALT-on-spec-vs-data, transparency-continuation disclosure all preserved
unchanged. The rule is a cost-allocation rule, not a methodology relaxation.

## Currently-known free-path audits needed (post-Wave-2)

| Iteration | Quoted Dune use | Free-path audit status |
|---|---|---|
| E4 narrowed Superfluid R3+ | Wave-1.4 one-shot panel + Sub-task E4.0.B + routine refresh | Wave-3 audit dispatched: try Optimism RPC + Etherscan + The Graph Superfluid subgraph + custom indexer |
| E7-A Mento Reserve | None (Celo RPC direct, free) | Already PASS-FREE; ~1-2 day indexer build is the free path |
| E8 dTAO × Maymin | None (Taostats free + Subtensor EVM RPC free) | Already PASS-FREE |
| E5 RefiColombia | None (subsidios REST + Celo RPC + Banrep TRM all free) | Already PASS-FREE |
| E9-A AGPE Energy-AMM | None (XM-API free + NOAA ONI free) | Already PASS-FREE |

## Links

[[data-visibility-gate-before-modeling]] — the gate this rule modifies
[[abrigo-portfolio-prioritization-with-fallback]] — cost-management consistent with risk-managed portfolio
[[no-merge-without-approval]] — analogous discipline on irreversible commitments
[[e5-floor-relaxation-current-data-availability]] — paired methodology shift from same conversation
