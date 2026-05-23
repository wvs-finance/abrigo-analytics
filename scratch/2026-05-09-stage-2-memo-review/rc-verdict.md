# RC Verdict — Stage-2 Verdict Memo Reality Check

**Target**: `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`
**Date**: 2026-05-09
**Reviewer**: TestingRealityChecker (RC)
**Default**: REJECT (overturned only by overwhelming evidence)

## Verdict: ACCEPT_WITH_FLAGS

Every load-bearing numerical claim was independently re-derived from the live
emitted artifacts and the verdict file inventory. All twelve reality-check
dimensions resolved in the memo's favor; two minor presentational FLAGs remain.

## Numerical cross-check (live artifacts)

| Memo claim (line) | Live artifact source | Match |
|---|---|---|
| Line 20 — `Z_cap = 4,688 COP/mo` | `Z_cap_pinned.json::Z_cop_per_month = 4687.942347178384` | PASS |
| Line 22 — `95% CI [168, 14,606]` | `Z_cap_pinned.json::ci_95_lo=168.172482..., ci_95_hi=14606.142570...` | PASS |
| Line 130 — `r̂_max = 1.0000265` | `_AUDIT.json::rhat_max = 1.0000265166749636` | PASS |
| Line 131 — `ess_bulk_min = 338,540` | `_AUDIT.json::ess_bulk_min = 338539.83...` | PASS |
| Line 132 — `ess_tail_min = 213,752` | `_AUDIT.json::ess_tail_min = 213751.90...` | PASS |
| Line 133 — `divergence_frac = 0.0` | `_AUDIT.json::divergence_frac = 0.0` | PASS |
| Line 134 — `ci_width_ratio_max = 1.0039` | `_AUDIT.json::ci_width_ratio_max = 1.00387...` | PASS |
| Line 135 — `712k draws (4 × 178k)` | `_AUDIT.json::n_chains=4, n_draws_per_chain=178000, n_rows=712000` | PASS |
| Line 224 — `identity_residual = 6.31×10⁻⁹` | `Z_cap_pinned.json::identity_residual = 6.307049068...e-09` | PASS |
| Lines 217-221 — TP1/2/3=4687.94, TP4=4922.32, TP5=4453.57 | `Z_cap_pinned.json::sign_verdicts[*].z` matches all 5 | PASS |
| Lines 217-221 — All 5 `identity_passes=true, sign=PASS` | live JSON: 5/5 PASS | PASS |
| Line 374 — `audit_block 1fb1f7a4…5d31` | `Z_cap_pinned.json::audit_block = 1fb1f7a42131...329b5d31` | PASS |
| Line 159 — `audit_block 4da660b5…2173` | `gate_verdict.json::audit_block = 4da660b55e7a...19672173` | PASS |
| Lines 17-19 — `24/24 PASS primary` (3×2×2×2 family) | `gate_verdict.json::evidence` length=24, all `sign_strictly_negative=true`, `n_sign_violations=0` | PASS |
| Lines 184-186 — ELPD ar1_log=28.481, det_churn=23.873, martingale=23.073 | `revenue_form_verdict.json::_comparison.elpd_loo` exact match to 3 decimals | PASS |
| Line 188 — `Δelpd=4.608, DSE=2.762, Δelpd/SE=1.67` | live: elpd_diff=4.6077..., dse=2.7624...; 4.6078/2.7624 ≈ 1.668 | PASS |
| Line 198 — `rank_flip_detected: false` | `revenue_form_verdict.json::_metadata.rank_flip_detected = false` | PASS |
| Line 198 — Beta(2.0, 38.0) vs Beta(4.5, 95.5) ranking identical | `legacy_ranked_forms == new_ranked_forms = [ar1_log, det_churn, martingale]` | PASS |
| Line 262 — `423 tests` | `pytest --collect-only`: "423 tests collected" | PASS |
| Line 241 — `17 independent audit verdict files` | `ls .../*.md \| wc -l = 31` (31 .md files in 7 audit dirs) | **FLAG-1** |

## Anti-fishing remediation (memo §6)

- C4 v0.3 `1/κ` removal — documented at lines 252, 274; corroborated by
  Z_cap_pinned.json deterministic re-execution (audit_block stable).
- C2 v0.3 24-bracket re-orientation — corroborated by gate_verdict.json
  evidence length = 24 (was 5 in v0.2 per memo line 250).
- Spec v1.2.1 prior re-pin — corroborated by `revenue_form_verdict.json::_metadata.prior_pin = "Beta(4.5, 95.5)"` and HALT-on-flip metadata block.

## FLAGs

**FLAG-1 (presentational, line 241, 364)**: Memo claims "17 independent audit
verdict files." Live count of `.md` files across the 7 enumerated audit
directories is **31**. The discrepancy is reconciled if "verdict file" means
distinct verdict *documents at the latest revision* (one RC + one MQ + one CR
per audit, with prior-version files retained as history). Under that reading,
4 cohort audits × 3 reviewers + spec-v1.2 (2) + phase-4 schema (2) +
close-plan (2) = 12+2+2+2 = 18, still not 17. Recommend memo replace "17" with
the verifiable count "31 verdict files (latest + revisions across 7 audit
folders)" or footnote the counting convention. Not a numerical defect — does
not affect any quantitative claim — but the cited integer is unverifiable as
written.

**FLAG-2 (presentational, line 261)**: "411 → 423 tests" — the `423` endpoint
is verified by live `pytest --collect-only`; the `411` baseline cannot be
verified at this commit (would require a prior-revision checkout). Acceptable
as historical context, but flag for transparency.

## Process invariants

- Limitations §7 honestly disclosed (synthetic-only, ~$1.17/mo magnitude,
  C3 single-trajectory, no on-chain test, `_first_trajectory` discard) —
  PASS, none of these are obscured by promotional language.
- Product-surface tone (§8) names the small magnitude explicitly: "small in
  absolute terms (~$1.17 USD/month)" — non-promotional. PASS.
- Stage-3 readiness checklist (§9) enumerates 6 concrete deferred items —
  PASS.
- References (§10) cover spec v1.2.1, all 4 cohort plans, CLOSE plan,
  PRIMITIVES.md, lit survey, all audit folders, all emitted artifacts —
  PASS.

## Verdict translation

Every numerical statement that bears on the Stage-2 PASS verdict is exact to
the live artifacts. The HALT-on-flip safeguard fired correctly with verifiable
provenance. The 24/24 PASS claim is true under the spec §5.2 parameter family.
The C3 INDISTINGUISHABLE verdict is correctly stated and the Δelpd/SE ratio
arithmetic checks out. Anti-fishing remediations all map to either NON-NO-OP
forward-fixes or preregistered HALTs.

The two FLAGs are presentational. ACCEPT_WITH_FLAGS is the correct verdict —
the default REJECT is overturned by overwhelming numerical-correspondence
evidence, but the "17 files" integer should be reconciled before the memo is
treated as canonical citation surface for downstream artifacts.

## Recommended fixes (non-blocking)

1. Reconcile "17 independent audit verdict files" to the verifiable count
   (31 .md across 7 directories) or document the counting convention.
2. Add a brief footnote on the 411 baseline (commit-pin or note as
   pre-Stage-2-Phase-1 baseline).

---

**Verdict**: ACCEPT_WITH_FLAGS
**Reality-check default overturned**: yes (numerical correspondence
overwhelming on all 12 dimensions)
**Re-review required after fixes**: no (FLAGs are presentational)
