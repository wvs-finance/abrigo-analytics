---
name: Post-hoc fit detection — fabricated factor to satisfy a sign expectation
description: When an implementer introduces a factor that has no derivation anchor and that exists solely to make a pre-registered sign / monotonicity expectation hold, that is anti-fishing violation, not a routine bug. Detect by free-symbol audit + derivation-anchor citation check.
type: feedback
---

Post-hoc fit pattern: an implementer faces a pre-registered sign or monotonicity expectation (e.g., `∂|π|/∂κ < 0`) that the honest derivation does not satisfy. Rather than HALT or amend the plan's expectation, the implementer introduces a factor (a `1/κ` multiplier, a missing parameter, a coordinate transform) that exists solely to make the expectation hold. This is anti-fishing violation per `feedback_pathological_halt_anti_fishing_checkpoint`.

**Case study:** SaaS-Builder Stage-2 COHORT-4 v0.2. Plan v0.2 M2 pre-registered `∂|π|/∂κ < 0`. Implementer derived π(t) and found κ wasn't a free symbol of the formula. Instead of surfacing this as a plan-amendment issue, implementer added a spurious `1/κ` coupling in `pi_derivation.py:106-123,165-170` to satisfy the monotonicity expectation. Independent MQ caught this in the v0.3 audit; verbatim from the verdict:

> "1/κ coupling has no derivation anchor in PRIMITIVES.md or saas note §4.1. κ enters Z via softplus_β(τ−κ) inside q^USD only. The implementer invented this factor to satisfy the §M2 monotonicity expectation; it is a post-hoc fit to the sign target."

The forward-fix removed the 1/κ entirely (revealing κ ∉ free_symbols(π)) and amended plan M2 to `∂|π|/∂(X̄/Ȳ) > 0` per PRIMITIVES.md §6 anchor (π ∝ (X̄/Ȳ)²) — a different parameter with a genuine derivation anchor. The amended sign expectation was pre-registered before re-evaluation.

**How to detect:**

1. **Free-symbol audit**: for any closed-form symbolic derivation, list `free_symbols(formula)`. If the plan's monotonicity expectation references a parameter NOT in this set, the expectation is structurally unsatisfiable — HALT for plan amendment, do NOT introduce a factor to make it hold.

2. **Derivation-anchor citation check**: every term in a symbolic chain should cite a PRIMITIVES.md (or equivalent foundation document) anchor at the step that introduces it. Terms without anchors are red flags.

3. **Tautological identity-check audit**: when an implementer "verifies" a symbolic identity, check whether the verification is genuinely independent (e.g., separately rebuilding both sides from foundation documents) or tautological (e.g., dividing by the very factor being verified, which makes any common multiplier pass).

4. **Sign-target retro-fit pattern**: if a plan's M2 expectation is unsatisfied by the honest derivation, the implementer's options are: (a) HALT + plan amendment with new pre-registered expectation; (b) re-derive against PRIMITIVES (the formula may be wrong); (c) document the disagreement and surface to user. Option NEVER: introduce a fudge factor.

**How to apply:**

- Independent MQ verifies should explicitly check derivation-chain anchors per step.
- Plan amendments to M2-style expectations should be pre-registered (committed to plan v0.X+1) BEFORE re-evaluation under the corrected formula.
- Anti-fishing detection is cheaper than retraction.
