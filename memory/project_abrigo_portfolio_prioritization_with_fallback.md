---
name: abrigo-portfolio-prioritization-with-fallback
description: User clarification 2026-05-18 — Abrigo iteration portfolio is risk-managed: tech-only path (E8 dTAO×Maymin) is PRIMARY but not exclusive; if tech path becomes data-infeasible OR simulation drifts into fantasy territory, fall back to alternative paths (E5 RefiColombia, E7 Mento minter, future redux of E2/E6) where convex macro hedge instruments are still buildable.
metadata:
  type: project
---

## Clarification (user 2026-05-18, post-CLAUDE.md-broadening + post-day-1)

> "We're not dropping entirely. We are doing a prioritization because if the technology path is not feasible in terms of data in terms of simulation being too like fantasy we need to rely on those other things where we can build convex macro hedge instruments."

## The principle

**Tech-only is the priority, NOT the only path.** Abrigo runs a risk-managed iteration portfolio:

1. **Primary track**: technological-domain iterations where the Kaleckian "investment drives real output" channel is empirically tractable AND the cohort has hedgeable micro-risk. Current primary = **E8 (Bittensor dTAO × Maymin) — decentralized substitute for centralized Claude Code (Anthropic API)**.

2. **Activatable fallback tracks**: non-tech iterations where Abrigo can still build convex macro hedge instruments. Kept in spec form but not actively dispatched while primary track is alive. Current fallback set = **E5 RefiColombia COPm subsidies, E7 Mento minter, future redux of E2/E6 if conditions change**.

3. **Fall-back triggers** (when to activate fallback tracks):
   - Primary-track data feasibility fails — e.g., Bittensor public data insufficient for CEV refit at the extended window, or Taostats API access constrained
   - Primary-track simulation drifts into **fantasy territory** — see threshold definition below
   - Primary-track methods-paper rejected at venue (rare; multi-month timeline)

## "Fantasy" threshold for simulation work

Per CLAUDE.md anti-fishing carry-forward, simulation is permitted ONLY when empirically anchored. Threshold for "too fantasy":

| Element | Acceptable | Fantasy |
|---|---|---|
| Input data | Real public Bittensor public data (Taostats API) + real Colombian electricity-cost / FX / import-tariff data | Generated from priors; values picked to match desired headline |
| Counterfactual scope | "What would a Colombian operator's economics look like under observed global Bittensor dynamics?" | "What would Colombia look like if it had a thriving Bittensor scene?" — projecting non-existent cohort behavior |
| Pre-pin discipline | Simulation assumptions DECLARED before running; sensitivity arms on cost-of-electricity / GPU depreciation / FX-bands | Iterating on assumptions until headline β is positive |
| Output framing | "Hypothetical Colombian operator under observed-global-dynamics" with explicit caveat | "We measured that Colombian operators..." (asserting a cohort that doesn't exist) |

If simulation crosses into fantasy on any of the 4 dimensions → HALT simulation track; activate fallback paths.

## Standing portfolio composition (2026-05-18)

**Active primary**:
- E8 dTAO × Maymin methods-paper (CONDITIONAL PASS per E8.0; methods-paper-only path)
- E8 LATAM-operator simulation (Path A from today's response) — bounded by fantasy-threshold check

**Frozen ready (activatable on primary-track failure)**:
- E5 RefiColombia COPm sub-cohort (PARTIAL per Day-1; wait ~10 weeks for cohort growth, reframe Y to Δlog(claim_ops) weekly)
- E7 Mento minter / monetary-sovereignty cohort (pinned for follow-up gating round)
- E4 narrowed to Superfluid-streamed R3+ PG builders (technological cohort; survives reframe)

**Closed**:
- E1 DePIN (EVM-incompatible)
- E2 RWA original (permissionless + P_k inversion)
- E3 as β-iteration (folded into E8 joint methods-paper)
- E6 LATAM-RWA (NON-RETIREMENT — Brazilian-CVM permissionless thin)

## Anti-fishing carry-forward

The portfolio-prioritization-with-fallback framework does NOT relax anti-fishing invariants:
- HALT-on-spec-vs-data carries forward to each track
- Pre-pin discipline applies to simulation as much as empirical work
- NON-RETIREMENT is honest on primary track; activating fallback is NOT a license to manufacture a clean verdict on the failed primary

The fallback set exists so that **iteration-level NON-RETIREMENT does not mean framework-level dead-end**. There are always macro micro-risks the Abrigo framework can address; the question is which cohort has the data + tradability + framework-alignment to make a β-iteration tractable.

## Links

[[abrigo-framing-clarification-investment-productivity]] — broadened goal from wage→capital to investment-productivity (2026-05-18 prior clarification)
[[bhaduri-laski-riese-concept-bridge]] — theoretical anchor; tech-domain iterations naturally fit BLR/Minsky/Kaleckian
[[d1-transparency-continuation]] — disclosure rule applies to fallback activation too
[[pathological-halt-anti-fishing-checkpoint]] — HALT discipline preserved across portfolio
