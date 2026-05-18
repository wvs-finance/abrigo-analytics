---
name: abrigo-framing-clarification-investment-productivity
description: User clarification 2026-05-18 — Abrigo's transmission story is broader than wage→capital. Primary frame is "make actual investment productive via on-chain CFMM convex derivatives following post-Keynesian micro-risk identification". Wage-earners are ONE investor class, not the only one.
metadata:
  type: project
---

## Clarification (user voice-note 2026-05-18, post-D5-brainstorm)

> "Abrigo is not for help explicitly transition from wage to capital, but make actual investment productive by means of on-chain, CFMM, convex derivatives. That follows post-Keynesian investment guidelines for identifying those micro-risks. So it's not strictly for wage things."

## Why the clarification matters

Earlier framing (CLAUDE.md "Abrigo Operating Framework" + `project_abrigo_inequality_hedge_thesis.md`): the headline transmission channel was **wage → productive capital via premium-funded ratchet (self-LBM)**. This was always one *instance* of the framework, not the whole framework. The clarification promotes the generalized framing.

**Generalized frame (PRIMARY going forward)**:
- Abrigo's purpose = **make actual investment productive** by providing on-chain CFMM-based convex hedges against **micro-risks identified via post-Keynesian theory**
- Cohorts are **investor classes**, of which wage-earners-becoming-investors is ONE (D1.D); micro-vendors making USD-COGS commitments is ANOTHER (D2); USDC-savers protecting against depeg is ANOTHER (D4); Giveth/q-acc productive-investment donors is ANOTHER (D5)
- The Kaleckian framing (investment drives output, not the reverse) is now the LITERAL operational frame, not just the theoretical underpinning

## What stays the same

- All gating verdicts (D2 CONDITIONAL PASS; D3 CLOSED FAIL; D1.D CONDITIONAL PASS via Path 4; D4 CONDITIONAL PASS via CORRECTIONS-A)
- All spec/plan locks (joint D1.D+D4 spec v0.2, joint plan v0.2)
- All memory references including BLR concept-bridge + D1 transparency condition + retroactive BLR sharpening
- Anti-fishing invariants (N_MIN, POWER_MIN, MDES_SD, HALT discipline)
- Three-tier reproducibility (Tier 1/2/3)
- Stage-correctness discipline (β-existence → M-design → deployment)
- On-chain CFMM + Panoptic as the canonical M-layer

## What shifts in interpretation (no spec rewrite required)

### D1.D + D4 joint iteration
- **Old interpretation**: ρ̂ = "fraction of wage flow transitioning to capital position"
- **New interpretation**: ρ̂ = "savings-retention rate of on-chain stablecoin recipients under FX/depeg micro-risk"
- Both are valid measurements; the new framing is more honest about what we're observing
- The BLR/Minsky retroactive sharpening memo (`reference_d1d_d4_blr_minsky_sharpening.md`) already articulates this — it stands as the operative interpretation guide
- **No v0.2 spec amendment needed** — CORRECTIONS-A + CORRECTIONS-B locks are preserved
- Notebook 06 verdict + LaTeX write-up should adopt the new framing language

### D2 micro-vendors
- **Old framing**: misclassified as wage→capital adjacent
- **New framing fits more naturally**: vendor invests USD in COGS → produces inventory → produces revenue. **FX hedge protects productive investment**. This is the PUREST instance of the framework's purpose.
- **Priority promotion**: D2 should move up in the queue (was paused at CONDITIONAL PASS gate). Drafting D2 full-iteration spec is now the strongest natural next step.

### Direction 5 (q/acc + MiniPay)
- **Old assessment**: park to 2027-Q3+ because productive-investment volume is 3-4 orders too small for Stage-1 β
- **Revised under new framing**: still scale-blocked at Stage-1 β, BUT the methods-paper opportunity (Y_real / Y_virtual as BLR two-price gap) becomes MORE central — it's the conceptual headline contribution of the entire framework, not an ancillary deliverable
- Priority on Dune address-tagging + Fermi scoping stays
- Methods paper draft promoted to parallel-track 2026-2027 (not deferred to 2027)

## What needs updating

### CLAUDE.md "Abrigo Operating Framework" section
The current text emphasizes "wage→productive capital via premium-funded ratchet (self-LBM)". The new framing generalizes this. Proposed amendment direction (NOT yet executed; awaiting user approval):
- Lead with "make actual investment productive via on-chain CFMM convex derivatives following post-Keynesian micro-risk identification"
- Wage→capital becomes one transmission *instance* among several investor-class cohorts
- "Self-LBM" becomes one M-design pattern among others (long-tail OTM put, one-sided long-call USDCOP, q/acc-style ABC, etc.)

### Iteration priority queue (revised)
1. **D2 (Colombian import micro-vendors)** — purest fit; CONDITIONAL PASS already; ready for full-iteration spec drafting
2. **D5 measurement-feasibility scoping** + **methods-paper draft** — central conceptual contribution; parallel track
3. **D1.D+D4 joint** — locked at v0.2, Phase 0 dispatch on plan-v0.2 timeline
4. (None other promoted under new framing)

### Memory hygiene
- This memo (`project_abrigo_framing_clarification_investment_productivity.md`) supersedes the narrow wage→capital reading in `project_abrigo_inequality_hedge_thesis.md` as the PRIMARY framing
- The inequality-differential thesis remains valid as one *application* of the framework (specifically Y₃)
- Concept-bridge map (`reference_bhaduri_laski_riese_concept_bridge.md`) is unchanged — applies equally to investor classes
- BLR/Minsky sharpening (`reference_d1d_d4_blr_minsky_sharpening.md`) is unchanged

## Links

[[bhaduri-laski-riese-concept-bridge]] — terminology + literature spine (no change)
[[d1d-d4-blr-minsky-sharpening]] — retroactive interpretation lens for v0.2 (no change; just becomes primary not retroactive)
[[abrigo-inequality-hedge-thesis]] — historical record; subordinated to this clarification
[[onchain-native-priority]] — Tier-1 on-chain X reaffirmed under new framing
[[abrigo-painkiller-evidence-base]] — painkiller framing carries forward; broadened from "wage earner pain" to "investor pain under micro-risk"
