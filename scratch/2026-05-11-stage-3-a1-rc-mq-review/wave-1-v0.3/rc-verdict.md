# RC verdict — A1 plan v0.2 → v0.3 predicate-change CORRECTIONS-α (scoped re-review)

**Reviewer:** Reality Checker (RC)
**Scope:** §11.2 v0.2 → v0.3 entry ONLY (NOT full plan re-review)
**Date:** 2026-05-11
**Commit reviewed:** `8d2edc7` (confirmed via `git log --oneline -3`)
**Verdict:** ACCEPT

## Findings (severity-graded)

### BLOCK
None.

### FLAG (material)
None. The four scoped questions all resolve in favor of ACCEPT:

1. **Math justification per PRIMITIVES.md §10.** Verified. §10 eq. (18) writes σ_T as ∫ P(K)/K² dK + ∫ C(K)/K² dK with a strictly positive 2/K² kernel on OTM puts and calls. The Carr-Madan strip is built from long-vol building blocks (positive Γ everywhere on the OTM rays). Mixed-vol primitives (call_spread, put_spread, super_bull, super_bear, call_ratio_spread, zebra) have sign-changing Γ and therefore cannot be expressed as a single positive-weight combination of the §10 kernel. §11.2's claim that mixed-vol "mathematically CANNOT cleanly Carr-Madan-replicate long-variance" is correct as written and the citation to eq. (18) is the right anchor.

2. **Ex-ante anchoring, not count-driven.** §11.2 explicitly states "anchored ex-ante in PRIMITIVES.md §10 (a frozen Stage-2 derivation), not in the observed candidate counts." PRIMITIVES.md is Stage-2-frozen; §10 predates v0.1 of this plan. The §10 anchor was available at v0.1 and v0.2 — the v0.2 predicate `!= short-vol` is recognizable as a drafting slip (negation of one class admits TWO classes: long-vol AND mixed-vol). The new predicate `== long-vol` is the predicate that v0.2 SHOULD have written had the §10 reading been tight. The fact that the count mismatch (11+1=12 vs. "2–4") was the *trigger* for re-reading §10 is not itself fishing — fishing would be moving the predicate to land a target count without a math anchor. Here the predicate is moved to the predicate the math always required; the count outcome is a downstream consequence and is not used to calibrate the rule.

3. **Form is CORRECTIONS-α (not silent).** Verified. §11.2 is a versioned plan-level entry (v0.2 → v0.3), the plan header line 9 was bumped to v0.3, the commit `8d2edc7` is titled "plan(stage-3-a1): v0.2→v0.3 CORRECTIONS-α — predicate tightening to long-vol pure", and the entry triggers a scoped Wave-1 re-review (this very file). No silent edit. The `normalized_score` precedent in §11.1 MQ-FLAG-A1.2 explicitly required CORRECTIONS-α + fresh Wave-1 for predicate-class adjustments; that protocol is honored here.

4. **"NOT fishing" defense soundness.** §11.2's defense paragraph correctly identifies the three conditions that distinguish a math-anchored predicate correction from post-hoc count-tuning: (i) cite a frozen prior derivation, (ii) motivation is mathematical correctness of the downstream metric, (iii) the anchor predates the trigger. All three are explicit. This is the *inverse-direction* analogue of the κ-removal precedent in `feedback_post_hoc_fit_anti_fishing_pattern.md` — there a fabricated factor was REMOVED because it lacked a PRIMITIVES.md anchor; here a permissive admission (mixed-vol) is REMOVED because it lacks the §10 anchor. The structural principle (rule must be anchored in the frozen math) is the same.

### NIT (cosmetic)
- §11.2 paragraph 2 says the normalized_score lane is "broken for mixed-vol" with the parenthetical that the multiplicative correction is "derived under the assumption of monotone-convex payoff." A one-line citation to the MQ-FLAG-A1.2 disposition (line 126 / line 316) would tighten the cross-reference. Non-blocking.

## Anti-fishing posture audit

§11.2 does not smuggle in count-driven motivation. The text is careful to label the count mismatch as the *trigger* ("revealed a drafting slip") rather than the *justification*. The justification is the §10 kernel-positivity argument, which holds independent of how many candidates the v0.2 rule happened to admit. The §6.4 master-spec carveout reading is correct: §6.4 escalates only CONVERGENT structural BLOCKs to master spec; a plan-internal predicate refinement that does not contradict any master-spec pin stays at plan level. Master spec P-A1.4 (5pp REPLACE margin) and §2.1 HALT triggers are untouched. Honnibal audit-pass chain does not apply (no code in CORRECTIONS-α). Pin coverage §8 unchanged per §11.2 last bullet — verified, no pin invalidated.

The κ-removal precedent comparison is apt and protective: the same checklist (frozen anchor + ex-ante motivation + visible patch) is satisfied here as was required there.

**Verdict: ACCEPT.** Task 1.2 implementer may proceed with the v0.3 predicate; §5 of STRATEGY_COMPARISON.md is to be overwritten in-place with the filtered-out sub-list as §11.2 specifies.
