# Direction 3 — Jump-Conditional Re-Test — CLOSURE-FAIL

**Date:** 2026-05-18
**Status:** CLOSED — FAIL by mechanical exhaustion of feasibility
**Anchor:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §0.4
**Trigger:** 8-agent gate-step review (Reality Checker + Code Reviewer) returned NEEDS_WORK / CONDITIONAL with overlapping blockers around panel size, jump count, and methodology validity at daily frequency

## What happened

Direction 3 of the four-direction parallel-exploration plan proposed a jump-conditional re-test of the closed dev_ai_cost_v2 panel using Barndorff-Nielsen / Shephard bipower decomposition + threshold regression at p90 FX-vol. The hypothesis: the R5 integrated-variance β ≈ 0 might mask a positive *jump-component* β.

The v0.1 spec assumed the panel had N≈150 trading days. **The actual panel `data/panels/notional_cost_panel.parquet` has N=29 rows (N=28 post-first-diff)**; the 150 figure was the count of TRM trading days available in the data-collection window, not regression observations.

The D3 Reality Checker ran an empirical jump census on the 137-day TRM window:

| Jump threshold | Days exceeding | Intersected with N=29 cost rows |
|---|---|---|
| \|2σ\| | 6 | ~2-4 stress observations |
| \|2.5σ\| | 2 | <1 stress observations |
| \|3σ\| | **0** | 0 |

The spec's own FAIL criterion (`jump count < 5` ⇒ "mechanically uninformative") fires before any analysis runs.

## Why this fails before implementation

1. **N misstatement.** Every downstream calculation in the spec (threshold split, jump-count expectation, bootstrap block length) was computed against the wrong N. Correcting to N=29 collapses the test's feasibility.
2. **Mechanically inadequate jump count.** Asymmetric down-jump arm has literally zero observations at 2.5σ. Threshold-split at p90 yields 2-3 stress obs, not the spec's "~15" estimate.
3. **Bipower variation theoretically misapplied at daily frequency.** Barndorff-Nielsen & Shephard (2004) derives asymptotics for intraday Δ→0; at daily-N=28 the (π/2) bipower estimator is high-variance and lacks the jump-robustness property the strategy depends on. Lee-Mykland (2008) is the daily-applicable alternative, but it doesn't repair the N=29 panel constraint.
4. **Silent POWER_MIN relaxation 0.80 → 0.50** in spec v0.1 without a CORRECTIONS block — exact anti-fishing pattern banned by `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`. Reverted in spec v0.2 §0.2.

## Anti-fishing posture

This closure is the *correct* anti-fishing response. The closed dev_ai_cost_v2 iteration (PR #5, merge `d81d60a`) returned PAUSED-PENDING-MORE-DATA at demonstration-grade. Running a second test on the same data — especially one whose spec parameters were tunable (decomposition method, threshold percentile, lag specification, asymmetry direction) — is garden-of-forking-paths inflation in the standard sense. Pre-pinning *every* DOF would have required Bonferroni correction; the post-correction power floor would have been unreachable on N=29 anyway.

The honest action is: **acknowledge the underlying data is too small for jump-conditional inference, accept demonstration-grade as the final iteration verdict, and redirect resources to directions that can acquire adequate-N panels (D1-G1, D2, D4).**

## Reviewer references

- `scratch/2026-05-18-four-direction-gating-review/direction-3/rc.md` (Reality Checker — empirical census + N misstatement detection)
- `scratch/2026-05-18-four-direction-gating-review/direction-3/cr.md` (Code Reviewer — bipower validity + DOF + Bonferroni)
- `scratch/2026-05-18-four-direction-gating-review/CONSOLIDATION.md` (8-agent roll-up)

## Action items closed

- [x] D3 closure-as-FAIL confirmed by user (2026-05-18)
- [x] Direction 3 section in spec v0.2 banner-flagged with §0.4 pointer
- [x] Notebook `07_jump_conditional.ipynb` **NOT created** (per closure)
- [x] No further effort on D3
- [x] Resources redirected per spec §0.6 sequencing: D2 serial, then D1-G1 + D4 parallel

## What this closure preserves for future use

If a later iteration accumulates ≥75 daily cost-row observations on the same operator (≥12 months of continuous Claude Code data collection), the jump-conditional methodology in v0.1 can be revisited with adequate N. The Lee-Mykland 2008 daily-applicable alternative + Bonferroni-corrected pre-pin should be the starting point at that time. Pinning here for the record: this direction is not invalidated; it is data-blocked at this moment.
