# A1 verdict rationale — Task 3.1

**Date:** 2026-05-11
**Verdict:** KEEP_IRONCONDOR
**Plan anchor:** docs/plans/2026-05-11-stage-3-a1-panoptic-restrategy.md v0.4

## §1 Threshold application

Per Pin P-A1.4 (master spec §5; v0.2 §9.1 MQ-FLAG-A1.4 disposition):

- Sign convention: `delta_pp = (ironcondor.max_relative_error - candidate.max_relative_error) * 100`
  (positive = candidate replicates BETTER than IronCondor, i.e. lower envelope error).
- **KEEP** iff `max(delta_pp for candidate in non_ironcondor) < 5.0` (strict).
- **REPLACE** iff at least one candidate has `delta_pp >= 5.0`.
- Multi-candidate tie-break (MQ-FLAG-A1.3): highest delta wins; float ties within 1e-12 → `primitive_id` lex asc; cross-`comparability_proof` float ties → HALT.

Source values: `scratch/2026-05-11-a1-panoptic-survey/envelope_evaluation_log.md` §2.

## §2 Per-candidate deltas

| candidate | `max_relative_error` | `delta_pp` vs IronCondor | exceeds 5pp? |
|---|---|---|---|
| reverse_iron_condor (BASELINE) | 0.2813412838694053 | 0.0 | n/a |
| long_straddle | 0.8038066200848816 | -52.24653362154763 | False |
| zeehbs | 0.9216437527122149 | -64.03024688428096 | False |
| long_strangle | 0.9785000108207673 | -69.71587269513620 | False |

`max(deltas) = -52.24653362154763` pp (long_straddle).

Full IEEE-754 double precision shown; `delta_pp = (ironcondor.max_relative_error - candidate.max_relative_error) * 100` computed directly from the `max_relative_error` column to its left. Source values from `envelope_evaluation_log.md` §2.

## §3 Verdict

`max(deltas) = -52.25` pp (long_straddle; rounded to 2 dp for readability — see §2 for full IEEE-754 precision) `< 5.0` → **KEEP**.

No non-IronCondor candidate beats IronCondor by the pre-pinned 5pp margin. Every candidate sits **below** IronCondor on the envelope-error metric (delta_pp is negative for all three), confirming reverse-IC remains the strongest replicator on the canonical TP1 fixture.

## §4 Anti-fishing posture

- Threshold `5.0 pp` pre-pinned at plan v0.2 (Pin P-A1.4 in master spec §5); reaffirmed v0.3, v0.4.
- Sign convention pre-pinned at plan v0.2 §11.1 (MQ-FLAG-A1.4 disposition; reaffirmed at plan v0.4 §6 Task 3.1 acceptance).
- Tie-break predicate pre-pinned at plan v0.3 §7 (MQ-FLAG-A1.3 disposition).
- Each adapter's `comparability_proof` declared at Task 2.2 authorship time (commit 6c871f0), BEFORE envelope numbers were observed (see eval log §4).
- No post-hoc threshold adjustment, no spec-flip, no candidate drop.

## §5 Phase-3 disposition

Task 3.2 (delta-spec stub) is **SKIPPED** per plan v0.4 §7 — verdict is KEEP, not REPLACE; no replacement primitive to specify.

Task 3.3 (commit + close) proceeds with this rationale + `strategy_verdict.json` as the Phase-3 deliverables.

## §6 Audit chain

- `consumed_strip_audit_block`: `94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329` (cohort_5_strip pin)
- `consumed_eval_log_sha` (sha256 of envelope_evaluation_log.md): `c6bdc05c6b8558b637db32df146f3c5905981a5045755a40aa67d048f2526b03`
- `audit_block` (this verdict): `3ce65740abcdddf00f3930a65ec544434073711195923b06c5e4466edcd77dff`
