# Abrigo SOTA / Competitive Landscape Review — Design Spec

**Date:** 2026-05-08
**Status:** Approved (brainstorming)
**Owner:** JMSBPP
**Branch:** iter/saas-builder-stage-2
**Output root:** `scratch/2026-05-08-sota-review/`

## 1. Goal

Produce a modular research artifact mapping prior art and competitor landscape around Abrigo's thesis — *permissionless on-chain perpetual convex hedge as a premium-funded ratchet for the wage→productive-capital transition in EM populations* — structured so sections can be excerpted into:

1. **Internal positioning + partnership memo** (primary near-term use).
2. **Grant / accelerator application competitive section** (Celo PG, Mento, Allo/Gitcoin, ETHGlobal, IDB Lab).
3. **Academic-style related-work section** (working paper / thesis chapter).

## 2. Non-goals

- No β-estimation, no notebook execution, no simulation work.
- No Solidity code, no contract integration sketches beyond high-level partnership/composability identification.
- No grant text drafted in this artifact — only the reusable competitive section.
- No silent scope expansion to make the landscape "look thinner." Scope drift is anti-fishing-banned (carry-forward invariant).

## 3. Benchmark — Numo (Robert Leifke)

Numo plays **three roles** in this review:

1. **Direct peer deep-dive** — own dedicated subsection in Track 1, deepest single-player section in the artifact (~30% of Track-1 word budget). Captures: mechanism, payoff space, settlement venue, EM-FX feasibility, on-chain status, team, funding, public artifacts (whitepaper, blog, repos, talks).
2. **Gold-standard scoring axis** — every competitor across all four tracks scored on a **Numo-rigor index**: design-architecture sophistication, payoff expressiveness, hook/composability depth, documentation rigor. Becomes a column in every comparison table and the synthesis differentiation table.
3. **Format/methodology benchmark** — Numo's whitepaper/docs/blog corpus collected as the stylistic reference for Abrigo's eventual public materials. Track-4 agent owns this collection.

The synthesis includes a dedicated **"Abrigo ↔ Numo: overlap, divergence, composition"** section, separate from cluster summaries.

## 4. Scope — four parallel tracks

### Track 1 — Direct on-chain convex hedges
**Players (non-exhaustive seed list):** Numo, Panoptic, Opyn (squeeth, everlasting options), Premia v3, Lyra/Derive, Aevo, Stryke/Dopex, Pendle PT/YT, Hegic, Pods, IPOR, Ribbon/Aevo vaults.
**Map:** payoff shape, settlement venue, retail accessibility, EM-FX coverage, premium-funded-ratchet feasibility, Numo-rigor index.

### Track 2 — Indirect on-chain (EM savings / FX vaults)
**Players (seed):** Mento + cStable family (cUSD, cEUR, cREAL, cCOP, cKES), Glo Dollar, Halofi, Goodghosting, Aave-on-Celo, Moola, Ubeswap LP-as-savings, Re.al, Brla.digital, Transfero stables, Stasis EURS, Ondo USDY for retail.
**Map:** FX-debasement protection mechanism (passive vs active), wallet-share overlap with Abrigo target, partnership/composability surface, Numo-rigor index.

### Track 3 — Indirect off-chain (closed-source EM dollar fintechs)
**Geo weighting:** Colombia-first → LATAM-broad → Africa-secondary.
**Players (seed):** Nubank USD/Cripto, Belo, Lemon Cash, Buenbit, Bitso+, Valiu, Littio, Rappi Pay USD, Bold, Yellowcard, Chipper, Mercury Stablecoin, Wise EM rails.
**Map:** product (USD savings / USD account / crypto-on-ramp), regulatory wrapper, target user, **why a wage earner uses *that* instead of an on-chain hedge** — i.e. the UX moat Abrigo must beat or sidestep, Numo-rigor index (where applicable).

### Track 4 — Hackathon + academic adjacent prior art
**Sources:** Celo Proof of Ship cohorts (last 3–4 quarters), ETHGlobal LATAM/Bogotá/Africa winners, Mento Labs grants, Allo/Gitcoin EM-savings rounds, IDB Lab portfolio, post-Keynesian distribution literature (arxiv MCP + SSRN), informal-worker capital-access papers, structural-transformation finance, Panoptic + Numo academic/whitepaper artifacts.
**Map:** what's been tried, what failed, design-space gaps, partnership/people candidates. Owns the **Numo-corpus collection** for the format/methodology benchmark role.

## 5. Per-track output schema

Each agent writes a self-contained markdown file to `scratch/2026-05-08-sota-review/track-{N}-{name}.md` using this fixed structure:

1. **Players & products** — table of identified players with one-line description.
2. **Mechanism table** — how each player constructs its product (payoff / yield source / FX exposure).
3. **Coverage of Abrigo thesis components** — scored on seven axes:
   - Permissionless (Y/N — anyone can take the position without gatekeeper approval)
   - Convex payoff (Y/N/partial)
   - EM-FX-native (Y/N/partial)
   - Wage-earner accessible (Y/N/partial — UX, KYC, ticket size)
   - Premium-funded ratchet (Y/N — does the product convert wage stream into productive-capital exposure?)
   - Open-source (Y/N — code/contracts publicly inspectable, distinct from permissionless access)
   - **Numo-rigor index (0–5)**
4. **Gaps Abrigo fills** — what each cluster cannot or does not do.
5. **Partnership / integration candidates** — who, why, what concrete integration sketch.
6. **Risk: who could pivot into our lane** — and what would need to change for them to do so.

**Word budget:** ≤ 2.5k words per track. Citation-rich (URLs / arxiv IDs inline).
**Source preference:** arxiv MCP for academic, web for fintech/hackathon/on-chain product docs.

## 6. Dispatch — parallel agents

Four agents launched in a single message (parallel):
- **Track 1:** `Trend Researcher` (Numo deep-dive prioritized).
- **Track 2:** `Trend Researcher`.
- **Track 3:** `Trend Researcher` (LATAM/Colombia weighting explicit).
- **Track 4:** `general-purpose` with arxiv MCP allowance + lit-review-style approach.

Each agent receives:
- Abrigo thesis summary (lifted from `CLAUDE.md` §"Abrigo Operating Framework").
- Numo's triple role (peer / scoring axis / format benchmark).
- The schema in §5.
- Anti-fishing scope guard (no expansion past §4 cluster definitions).
- Output path.

**Estimated wall time:** ~15–25 min parallel + ~10 min synthesis.

## 7. Synthesis

After all four tracks return, write `scratch/2026-05-08-sota-review/SUMMARY.md` containing:

1. **One-page executive map** — 2×2 (on-chain vs off-chain × convex vs linear-savings) with all players placed.
2. **7-axis differentiation table** — Abrigo vs each cluster on: permissionless, convex, EM-FX-native, wage-earner-accessible, premium-funded-ratchet, open-source, **Numo-rigor index**.
3. **Abrigo ↔ Numo: overlap, divergence, composition** — dedicated section.
4. **Top-5 partnership candidates** with concrete integration sketches.
5. **Top-3 competitive risks** with mitigation.
6. **Three excerptable downstream-use sections**, tagged:
   - `[USE:positioning]` — for internal partnership memo.
   - `[USE:grant]` — for accelerator/grant competitive section.
   - `[USE:academic]` — for related-work section.

## 8. Anti-fishing invariants

Carry-forward from `CLAUDE.md`:
- No silent scope expansion. If a player doesn't fit the four tracks, it's out — not folded in to thicken the landscape.
- No threshold tuning of the scoring axes after seeing data. Axes are pinned in §5 before agents dispatch.
- If Numo or any other competitor turns out to invalidate part of Abrigo's positioning, that finding is reported in the synthesis, not buried — HALT + disposition is the response, not silent re-framing.

## 9. Deliverables checklist

- [ ] `scratch/2026-05-08-sota-review/track-1-direct-onchain-convex.md`
- [ ] `scratch/2026-05-08-sota-review/track-2-indirect-onchain-em-savings.md`
- [ ] `scratch/2026-05-08-sota-review/track-3-indirect-offchain-fintech.md`
- [ ] `scratch/2026-05-08-sota-review/track-4-hackathon-academic.md`
- [ ] `scratch/2026-05-08-sota-review/SUMMARY.md` (with three tagged excerptable sections)

## 10. Out of scope (explicit)

- Generic DeFi yield aggregators not targeting EM populations.
- CEX savings products with no EM-specific design.
- Payments-only rails (e.g., Strike, Bitnob without savings layer).
- NFT-based "savings" games.
- Any β-estimation, M-design, or contract work — those belong in the iteration pipeline, not this artifact.
