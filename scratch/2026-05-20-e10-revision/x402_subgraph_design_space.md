# E10 — x402 / Subgraph Data Design-Space Research

**Date:** 2026-05-20
**Purpose:** DV-gate / feasibility research input for an E10 (GSPS) spec revision.
**Scope:** Read-only. No code, no spec edits, no iteration dispatch.
**Method tag legend:** [VERIFIED] = confirmed by a live probe in this session.
[DOCS] = current vendor docs via WebFetch. [INFERRED] = reasoned from verified
inputs. [UNVERIFIABLE] = could not pin down; listed in the Open Questions section.

---

## Headline finding (decisive correction to the E10 spec)

The E10 spec (§0.2, §0.4) and the parked-substrate memory both record the x402
per-query USDC price as **"opaque / dynamic / no published flat rate."** This is
now **falsified by a live probe.** A `curl` against The Graph Gateway's x402
endpoint for the exact Superfluid V1 Optimism subgraph in the spec returns:

```
HTTP/2 402
payment-required: <base64 JSON>
```

Decoded `payment-required` header (2026-05-20 12:21 UTC) [VERIFIED]:

```json
{
  "x402Version": 2,
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",          // Base mainnet
    "amount": "10000",                  // USDC 6-decimal base units
    "payTo": "0x79DC34E41B2b591078d3dE222C43EcaaBD52FcCB",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  // USDC on Base
    "extra": {"assetTransferMethod": "eip3009", "name": "USD Coin"}
  }]
}
```

`amount: "10000"` ÷ 10^6 (USDC decimals) = **$0.01 USDC per query, flat.** The
price is a fixed `exact`-scheme amount in the header, not a dynamic quote. It is
the same $0.01 flat rate the spec attributes to CoinGecko x402. The E10 spec's
"opaque pricing" caveat should be retired in v0.2.

---

## Q1 — What data is queryable, and how

### Q1.1 The Graph decentralized network — entity coverage

A subgraph exposes a **protocol-specific GraphQL entity layer** derived from a
chain's raw event logs by an indexed mapping. [DOCS] A typical protocol subgraph
covers:

- **Event-derived entities** — one entity per significant emitted event (e.g.
  `FlowUpdatedEvent`, `Swap`, `Transfer`), each carrying decoded params, tx hash,
  block number, timestamp.
- **Stateful aggregate entities** — running rollups maintained by the mapping
  (e.g. Superfluid `Stream`, `Account`, `TokenStatistic`,
  `AccountTokenSnapshot`; a DEX subgraph's `Pair`, `Token`, `PairDayData`).
- **Relational links** — entities reference one another (a `Stream` references
  its `Token` and `Account`), enabling joins the raw chain cannot do cheaply.
- **`_meta`** — sync head block, for freshness checks.

Coverage is bounded by what the subgraph author chose to index. There is no
cross-protocol normalization: each subgraph is its own schema. Anything the
mapping did not handler-index is simply absent.

### Q1.2 x402-paid subgraph queries — payment mechanics [VERIFIED]

- **Endpoint pattern:** `https://gateway.thegraph.com/api/x402/subgraphs/id/<ID>`
  (confirmed live; `/api/x402/` prefix replaces the API-key path segment).
- **Mechanic:** unauthenticated POST → `HTTP 402` + `payment-required` header
  carrying a base64 JSON x402 v2 offer. Client signs an EIP-3009
  `transferWithAuthorization` for USDC on Base, retries with a
  `Payment-Signature` header, receives the GraphQL result.
- **Price:** **flat $0.01 USDC / query** [VERIFIED via header decode]. Scheme is
  `exact` — a fixed amount, not a dynamic auction. No subscription, no API key,
  no account.
- **Settlement asset:** USDC on Base (`0x8335…2913`), `maxTimeoutSeconds: 300`.
- **Comparison anchor:** the API-key (non-x402) path is **$2 per 100,000
  queries = $0.00002/query** [DOCS, studio-pricing]. So x402 carries a **~500×
  per-query premium** over the API-key path — it buys keylessness/agent-native
  payment, not cheapness. For a human analyst with a wallet, the API-key path is
  far cheaper; x402 matters only for keyless/agentic consumption.

### Q1.3 Public RPC — what is free, what is not [VERIFIED]

Live probes 2026-05-20:

| Probe | Optimism `mainnet.optimism.io` | Base `mainnet.base.org` |
|---|---|---|
| `eth_blockNumber` | OK (`0x90ce6a8`) | OK (`0x2c1a513`) |
| `eth_getLogs` full range | error `-32062` "Block range is too large" | error `-32614` "limited to a 10,000 range" |
| `trace_block` (archive) | — | error `-32601` "rpc method is unsupported" |
| 10k-range `eth_getLogs` | — | transient `-32011` "no backend currently healthy" |

**Freely queryable on public RPC:** current state (`eth_call`, `eth_getBalance`,
`eth_getStorageAt`), individual blocks/txs/receipts, and event logs **in ≤10,000
-block windows** (Base) or bounded windows (Optimism). A full-history event scan
is possible only by paginating thousands of small windows.

**NOT available on free public RPC:** `trace_*` / `debug_*` archive methods
(internal-call tracing, state diffs); large-range log queries; any indexed/
joined/aggregated view; reliable SLA (the transient `-32011` confirms
best-effort backends with no uptime guarantee). Anything requiring decoded ABI
output, cross-block aggregation, or archive state requires a paid indexed
service (a subgraph, an archive-node provider, or Dune).

---

## Q2 — Dune vs The Graph + RPC: the curation gap

### Q2.1 What Dune Plus provides [DOCS, partially]

[DOCS] Dune curated tables use a hierarchical namespace —
`dex.trades`, `dex_solana.trades`, `nft.trades`, `tokens.transfers`,
`<protocol>.<event>` decoded tables — described by Dune as "pre-built, validated
datasets that normalize data from hundreds of protocols across dozens of chains
into consistent schemas," with "automated quality checks at every pipeline
stage." Dune docs cite **~15+ major curated categories** (DEX, NFT, lending,
bridges, staking, token transfers, prices, infrastructure). The spec's
"~8 clusters of curated tables per protocol" claim is **directionally correct
but imprecise** — Dune's organizing unit is the *cross-protocol category*
(~15+), under which each integrated protocol contributes decoded `protocol.*`
tables. "Per protocol" is the wrong axis; "per category, spanning all
protocols" is the actual model. v0.2 should restate this. [VERIFIED] the Free
tier includes 2,500 credits/mo, 10 private queries, API access.

### Q2.2 Replicating Dune via The Graph + RPC — the ETL gap

The Graph gives **raw protocol-specific entities, one schema per subgraph**;
Dune gives **decoded, cross-protocol-normalized tables in one SQL warehouse.**
To replicate Dune's analyst-ready layer from The Graph + RPC you must:

1. Discover/verify a maintained subgraph per protocol (coverage is uneven — many
   long-tail or new protocols have no maintained subgraph; some have only
   hosted-service legacy subgraphs not on the decentralized network).
2. Normalize each subgraph's idiosyncratic schema into a common one.
3. For protocols with no subgraph, build a custom indexer off raw RPC logs
   (the `dune-last-resort` rule's "~1-3 engineering days" path).
4. Maintain decode mappings as ABIs change.

This is the exact ETL labor Dune sells. It is **feasible but not free in
engineering time** — Dune Plus is, precisely, the option to *not* do this work.
"Query any data this way" is true only for protocols with a live maintained
subgraph; it is false in general (no universal subgraph coverage; archive-trace
data has no subgraph at all).

### Q2.3 Design-space partition

| Tier | Workload | Cost |
|---|---|---|
| (a) Free public RPC | Current state, single tx/block lookups, ≤10k-block log scans, contract-state reads | $0 |
| (b) Free-tier subgraph | Decoded protocol entities + aggregates where a maintained subgraph exists, ≤100k queries/mo | $0 |
| (c) x402-paid subgraph | Same subgraph data, keyless/agentic access, or burst above free quota | $0.01/query |
| (d) Dune Plus only | Cross-protocol normalized analytics, archive-trace data, internal-call tracing, ad-hoc SQL over hundreds of protocols, protocols with no maintained subgraph | $399/mo |

**(d) is genuinely Dune-only** for: full cross-protocol SQL joins without
bespoke ETL; `trace_*`-derived internal-transfer/MEV analysis; and any protocol
lacking a subgraph. For a single-protocol, well-subgraphed workload (E10's
Superfluid-CFA-on-Optimism case), tiers (a)/(b) fully suffice — the E10 §0
DV-PASS-FREE verdict holds.

---

## Q3 — Cost bounds

### Q3.1 Upper bound — Dune Plus

- **Price:** $399/mo [DOCS — multiple consistent 2026 third-party sources;
  the dune.com/pricing page itself did not render pricing to the fetcher].
  The E10 spec's "$390/mo" is within rounding of the current $399; v0.2 should
  update to $399 or flag "≈$390-399, vendor page unverified by probe."
- **Buys:** the curated cross-protocol warehouse, a credit budget far above the
  Free tier's 2,500/mo, private queries, API access, team seats. Exact Plus
  credit allocation could not be pinned (see Open Questions).

### Q3.2 Lower bound — minimal pay-as-you-go

A representative analyst doing a **daily dashboard refresh touching 3-5
protocols**:

- **Pure free RPC path:** state reads + bounded log scans → **$0/mo** (rate
  limits and the 10k-block window are the only friction; no monetary cost).
- **Free-tier subgraph path:** 100,000 queries/mo free. A daily refresh of
  3-5 protocols at, say, 20-50 GraphQL queries/day = ~600-1,500 queries/mo —
  **~1.5% of the free quota → $0/mo.**
- **API-key paid overflow:** even a heavy 500,000 queries/mo = (500k-100k) ÷
  100k × $2 = **$8/mo.**
- **x402 keyless equivalent:** the same 1,500 queries/mo at $0.01 flat =
  **$15/mo**; 5,000 queries/mo (E10's stated budget) = **$50/mo.**

So the realistic lower bound for an analyst with a wallet using the API-key path
is effectively **$0/mo** (free quota dominates); the realistic *x402-substrate*
cost for E10's own 5,000-query budget is **~$50/mo**.

### Q3.3 Cost spectrum

```
$0/mo ───────────────────────────── $8/mo ──── $15-50/mo ───────────── $399/mo
 │                                    │            │                       │
 free public RPC +              API-key paid   x402 keyless         Dune Plus
 free-tier subgraph             overflow       pay-per-query        (UPPER CAP)
 (≤100k subgraph q/mo,          (heavy 500k    (E10's own 5k/mo
  bounded RPC log scans)         q/mo case)     budget at $0.01)

 <--- where realistic single-/few-protocol analyst workloads land --->
                                                          <-- only multi-protocol,
                                                              archive-trace, or
                                                              no-subgraph work -->
```

**Where realistic workloads land:** a Web3 analyst doing routine
single-to-few-protocol dashboard work lands at the **$0-15/mo** end. They are
pushed toward the $399 cap only by *cross-protocol curated SQL*, *archive-trace
analytics*, or *protocols with no maintained subgraph* — i.e. the breadth and
decode-labor Dune sells, not raw query volume. The E10 hedgeable band ($0 lower
bound → $399 upper cap) is real, but for most realistic workloads the cost sits
near the floor; the upper cap binds only for breadth-driven workloads.

---

## Q4 — x402 substrate maturity re-check (informational only)

[DOCS / WebSearch, 2026-05-20]:

- The Graph Gateway x402 endpoint launched **2026-05-12** → **8 days old** as of
  today. The E10 memory's parked re-check date (2026-11, ≥6 months) is unchanged
  by this report.
- x402 endpoint is **live and responsive** — the probe returned a well-formed
  HTTP 402 with a valid v2 offer (the spec's "blog returned HTTP 500" concern is
  resolved at the *gateway* level; the *announcement blog* may still be flaky,
  but the endpoint itself works).
- **x402 protocol-wide (not Graph-specific) volume:** ~165M cumulative
  transactions, ~$50M cumulative volume, ~69k active agents, ~95% of volume on
  Base, USDC ~99.8% of payment asset share (Coinbase/third-party figures, late
  April 2026). Daily volume figures cited around ~$28k/day in some coverage.
- **Graph-x402-specific transaction history:** no usable history yet — 8 days
  old, no published Graph-x402 volume metrics. Insufficient for any empirical
  β identification on the x402 substrate.

**Informational verdict (NOT a recommendation):** the x402 substrate remains
too young for E10 empirical work, consistent with the parked
NON-RETIREMENT-PENDING-MATURITY state. The one correction to carry forward: the
per-query price is **not** opaque — it is a verified flat $0.01. Re-check stays
at 2026-11. Do **not** un-park.

---

## Design-space + cost-bounds summary

| Dimension | Finding | Source |
|---|---|---|
| x402 per-query price | **$0.01 USDC flat** (`amount:"10000"`, exact scheme) | [VERIFIED] live 402 header |
| x402 endpoint pattern | `gateway.thegraph.com/api/x402/subgraphs/id/<ID>` | [VERIFIED] |
| x402 settlement | USDC on Base, EIP-3009, 300s timeout | [VERIFIED] |
| Graph free tier | 100,000 queries/mo free | [DOCS] |
| Graph API-key paid | $2 / 100,000 queries ($0.00002/q) | [DOCS] |
| Public RPC log scan limit | 10,000-block window (Base); bounded (Optimism) | [VERIFIED] |
| Public RPC archive methods | `trace_*` unsupported; no SLA | [VERIFIED] |
| Dune Plus price | $399/mo (spec's $390 ≈ correct, slightly stale) | [DOCS] |
| Dune Free tier | 2,500 credits/mo, 10 private queries | [DOCS] |
| Cost LOWER bound (analyst) | ~$0/mo (free RPC + free subgraph quota) | [INFERRED] |
| Cost x402 path (E10 5k q/mo) | ~$50/mo | [INFERRED] |
| Cost UPPER cap | $399/mo Dune Plus | [DOCS] |
| Realistic workload landing | $0-15/mo for single-/few-protocol routine work | [INFERRED] |

---

## Open questions / unverifiable items

1. **Dune Plus exact base price & credit allocation.** dune.com/pricing and the
   docs pricing pages did not render structured pricing to the fetcher. $399/mo
   rests on consistent 2026 third-party sources, not Dune's own page. The Plus
   monthly credit count and seat count are unconfirmed. Spec's "$390" should be
   updated to "≈$399 (third-party-sourced)".
2. **Whether x402's $0.01 is uniform across all subgraphs.** The probe covered
   only the Superfluid V1 Optimism subgraph (`48YRvi7…HBXxT`). Price *could*
   vary by subgraph — though the `exact` scheme and the CoinGecko $0.01 parallel
   suggest a gateway-wide flat rate. Probe 2-3 other subgraph IDs to confirm.
3. **x402 query-result delivery semantics.** Confirmed the 402 challenge; did
   not complete a signed retry (would require a funded Base wallet). Whether one
   payment buys one query or a short-lived session is unverified.
4. **Subgraph coverage breadth.** No enumeration of which protocols lack a
   maintained decentralized-network subgraph was attempted — this is the crux of
   the Q2.2 "feasible but not universal" claim and would need a per-iteration
   audit.
5. **Optimism RPC exact log-window size.** Optimism returned a generic "Block
   range is too large" without a numeric limit (Base gave the explicit 10,000).
   Optimism's precise cap is unconfirmed.
6. **Graph free-tier rate limits (per-second/per-minute).** Only the 100k/mo
   volume cap is documented; any burst-rate throttle is unverified.
