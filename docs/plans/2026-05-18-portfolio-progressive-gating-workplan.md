# Portfolio-Level Progressive-Gating Work Plan

**Date:** 2026-05-18
**Anchor specs:**
- `docs/specs/2026-05-18-four-direction-investment-productivity-gating.md` v0.3
- `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2 (older joint iteration)
- `memory/project_abrigo_portfolio_prioritization_with_fallback.md`

## Generalizable primitive — Streamed-Liability Convex Hedge

Across multiple surviving directions, the cohort receives a **recurring stream** (subsidies, grants, token emissions, claims) that creates an **unhedged liability** against local-currency obligations. The general M-shape:

```
M = Panoptic perpetual put sized to STREAM-TAIL UN-REALIZED NOTIONAL
    on (stream-denominator-token / USDC) pool
    premium funded by claimed-and-converted stream-head receipts
```

Instances of this primitive across the portfolio:

| Direction | Stream | Stream-tail liability | Hedge M |
|---|---|---|---|
| **E4 narrowed (Superfluid R3+)** | OP RetroPGF R3+ Superfluid 90-day vest stream | Un-vested OP balance mechanically locked | Panoptic put on OP/USDC sized to un-vested notional |
| **E5-revised (RefiColombia)** | 10K-COPm claims every ~9.6h | Forward-expected COPm flow × COP-realized purchasing-power | Panoptic put on COPm/cUSD straddle |
| **E8 (Bittensor dTAO)** | TAO + alpha subnet emissions | Future-revenue alpha/TAO un-converted balance | Maymin-CEV-priced put on alpha/TAO native pool |
| **E7 (Mento minter)** | COPm/EURm/BRLm peg-defense seigniorage stream | Mento reserve composition risk | Cross-Mento basket convex hedge |

The unifying observation: **the stream itself is the premium-funding source for the convex hedge on the stream-tail**. This collapses Abrigo's "premium-funded ratchet" framework into a single repeatable instrument design.

## Progressive Gating Framework (G0 → G4)

Every direction in the portfolio progresses through 5 gates. Blockers surface as early as possible; PASS at each gate unlocks the next. NON-RETIREMENT at any gate is honest exit per `feedback_pathological_halt_anti_fishing_checkpoint.md`.

### G0 — Cohort + Observability Feasibility (≤2 days)
- Cohort exists and is identifiable on EVM (or simulatable per fantasy-threshold rules)?
- Data sources public-default + free-tier?
- N_MIN=75 achievable structurally (counting active-revenue cohort members, not registered)?
- **BLOCK if**: cohort not identifiable / data not public / cohort scale <1/3 of N_MIN

### G1 — Y Construction + Pre-pin Sketch (≤5 days)
- Y empirically constructible from G0 data?
- X identifiable from PK theory (BLR/Minsky/Kaleckian) + observable on chain?
- 7-field pre-pin (sign / magnitude / lag / primary spec / inference / power / HALT) drafted?
- **BLOCK if**: Y has mechanical identity bias / X not pre-pinnable / cohort N achievable but pre-pin requires Y to be reframed

### G2 — Pre-pin Draft Spec + 2-way Review (≤7 days)
- Spec drafted to dev_ai_cost_v2 v0.2.1 / D1.D+D4 v0.2 template
- RC + CR review dispatched in parallel
- All Critical findings autofix-cascaded to v0.2 of direction spec
- Closure-only re-review APPROVED_WITH_NITS or better
- **BLOCK if**: spec v0.2 still has unaddressed Critical findings / permissionless premise breaks

### G3 — Implementation Plan + 2-way Review (≤7 days)
- Plan v0.1 drafted to D1.D+D4 plan v0.2 template
- TDD scaffold (failing tests for every modules-tier component)
- Anti-fishing mechanical enforcement (compliance grep tests; HALT triggers in code)
- RC + CR review → autofix → closure-APPROVED
- **BLOCK if**: plan v0.2 still has unaddressed Critical findings / wall-clock implausible

### G4 — Iteration Execution + Verdict (≤21 days per spec §10)
- Phases 0-7 execution per plan v0.2
- Post-hoc audit-econ Delphi (3 Opus auditors) before write-up
- Verdict: PASS / PARTIAL-PASS / FAIL / NON-RETIREMENT per §7 collectively-exhaustive matrix
- **BLOCK / NON-RETIREMENT if**: empirical data contradicts pre-pin / HALT triggers fire

### G5 — Stage-2 M-Sketch (post-PASS only)
- Ideal-scenario Panoptic-position design
- No deployment work; sketch only per CLAUDE.md staging discipline

### G6 — Stage-3 Deployment (out of scope for this work plan)
- Requires live LP capital + Panoptic-mainnet-tradability verification

## Per-Direction Current G-Level (2026-05-18 snapshot)

| Direction | Status | Current G | Next-gate trigger |
|---|---|---|---|
| **E8 dTAO × Maymin** | ACTIVE PRIMARY | **G2** (Day-1 G0+G1 complete; methods-paper-only verdict; ready for spec draft) | Draft E8 standalone spec v0.1 + 2-way review |
| **E5-revised RefiColombia** | FROZEN READY (PARTIAL Day-1) | **G1 PARTIAL** (effective cohort N=70 <75; lifetime 521d) | Wait ~10 weeks for cohort growth OR reframe Y → Δlog(claim_ops) weekly + activate |
| **E7 Mento minter** | FROZEN READY (pinned) | **G0** (not yet dispatched) | G0 cohort feasibility scoping (~2 days) |
| **E4 narrowed (Superfluid R3+)** | FROZEN READY (E4.0 narrowed) | **G1 PARTIAL** (Option A narrowing locked; re-execute Dune q/3399900 needed) | Re-execute Dune + draft narrowed-E4 spec v0.1 |
| **E3 + E8 joint methods-paper** | PARALLEL TRACK | **G2** (theory + empirical anchors in place) | Methods-paper draft (multi-year track, not gated like β-iterations) |

## Parallel Dispatch Plan (sorted by primary-fallback order)

### Wave 1 (immediate dispatch)
1. **E8 spec v0.1 draft** + 2-way review (G2 → G3)
2. **E8 LATAM-operator simulation pre-pin** (under fantasy-threshold guard) — parallel to spec
3. **E7 G0 cohort feasibility** (Mento minter) — 2-day cheap scoping in parallel
4. **E4 narrowed (Superfluid R3+) Dune re-execute** + spec v0.1 draft

### Wave 2 (post-Wave-1 verdicts)
5. **E8 plan v0.1** + 2-way review (G3 → G4)
6. **E5 reframe spec amendment** — apply Δlog(claim_ops) weekly + freeze for 10-week cohort growth
7. **Methods-paper joint E3+E8 outline** — multi-year parallel track

### Wave 3 (post-Wave-2)
8. **E8 Phase 0 dispatch** (G4 execution) — sub-package scaffold + TDD harness
9. **E7 G1 if Wave-1 G0 PASSes**

### Fall-back triggers (per portfolio memo)
- E8 data infeasible OR simulation crosses fantasy threshold → activate E4-narrowed + E5-revised in parallel
- E4 fails Dune re-execute OR narrowing doesn't preserve N_MIN → escalate to E5 or E7

## Streamed-Liability Convex Hedge — Methodology Generalization

If 2+ directions PASS G4 with streamed-liability M-shape, we have a **portfolio-level methodology paper** beyond the E3+E8 Maymin paper:

> *"Streamed-Liability Convex Hedging on Permissionless CFMM Venues: Empirical Operationalization of the Minsky P_k/P_i Gap Across Heterogeneous Cohorts."*

Empirical instances supporting the methodology: E4 PG builders + E5 RefiColombia + E7 Mento minter + E8 Bittensor operators. Each is a different domain (open-source builders / direct-transfer recipients / stablecoin minters / decentralized AI operators) but the M-shape is identical. This is a stronger external-positioning narrative than any single iteration.

## Anti-fishing carry-forward

All §0 invariants from the four-direction spec carry forward:
- N_MIN=75 / POWER_MIN=0.80 / MDES_SD=0.40
- Pre-pin BEFORE data
- HALT-on-spec-vs-data triggers disposition memo + user-enumerated pivot + CORRECTIONS block
- NON-RETIREMENT is honest outcome at every gate
- Fantasy-threshold check per `project_abrigo_portfolio_prioritization_with_fallback.md`

The progressive-gating framework does NOT relax any invariant — it only ensures blockers surface at the cheapest possible step.

## Recommended next action

Dispatch Wave 1 (4 parallel tasks):
1. E8 standalone spec v0.1 draft (no dependencies)
2. E8 LATAM-operator simulation pre-pin (parallel to #1)
3. E7 G0 Mento minter cohort feasibility scoping (parallel)
4. E4 narrowed Dune q/3399900 re-execute + spec v0.1 draft (parallel)

Each is 1-3 day effort; all can dispatch immediately. Wave 1 outcomes inform Wave 2 prioritization within ~1 week.
