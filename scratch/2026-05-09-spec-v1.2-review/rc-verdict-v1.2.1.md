# RC Reverify Verdict — Spec v1.2 → v1.2.1 patch

**Auditor**: TestingRealityChecker (independent reverify)
**Spec**: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (v1.2.1, 1078 lines)
**Date**: 2026-05-08
**Default**: REJECT unless full FLAG resolution + no regressions.

## Verdict: ACCEPT

All 8 verification points pass with overwhelming evidence. No regressions detected.

## Verification matrix

| # | Item | Location | Status |
|---|---|---|---|
| 1 | §6.1 3-pronged provenance (>10%/mo tail; <50 reject; >200 reject) with citations | L452–477 | PASS — explicit paragraph "Concentration-provenance defence", all 3 prongs labelled (i)/(ii)/(iii); SURVEY.md citation 5 + §3.1 cited |
| 2 | §15.3 "v1.2.1 correction" blockquote disclaiming prior coincidence | L853–863 | PASS — leading blockquote explicitly states "the priors do NOT match"; cites C3 `priors.py:42-43` Beta(2.0, 38.0) vs v1.2 Beta(4.5, 95.5) |
| 3 | §15.4 NON-NO-OP routing + priors.py:42-43 line edit + HALT-on-flip preserved | L881–926 | PASS — "rescinds the NO-OP authorization"; explicit `DET_CHURN_LAMBDA_BETA_A = 2.0` → 4.5 / `DET_CHURN_LAMBDA_BETA_B = 38.0` → 95.5 amendment; "HALT-on-ELPD-rank-flip … remains in force" (L914–919) |
| 4 | §15.7 NEW sub-block documents both FLAGs with verdict-line citations | L994–1076 | PASS — FLAG-A and FLAG-B tables present (L1020, L1036); MQ verdict cited (L1074–1076 + L1000–1004); RC verdict cited (L1003); 5-point feedback_pathological_halt invariant check (a)–(e) all present |
| 5 | Beta(4.5, 95.5) UNCHANGED (no covert relabel) | L438, L860, L870, L877, L888, L893, L901, L922, L1042, L1046, L1053 | PASS — value appears 11× consistently; Beta(2.0, 38.0) appears only as the C3 v0.3 OLD value being replaced |
| 6 | Version header v1.2 → v1.2.1, emit_timestamp 2026-05-08, corrections_block extended | L3, L4, L11 | PASS — `spec_version: v1.2.1`; `emit_timestamp_utc: 2026-05-08`; corrections_block lists §14, §15, AND §15.7 v1.2 → v1.2.1 |
| 7 | No other pins loosened (M1–M5, anti-fishing, Υ_t closed set, PSIS-LOO threshold) | §8, §9, §15.5(1–7), §15.7(8–10) | PASS — §15.5 items 1–7 preserved verbatim; §15.7 items 8–10 add explicit no-loosening on candidate closure / HALT-on-flip / 4·SE-2·SE thresholds; N_MIN=75, POWER_MIN=0.80, MDES_SD=0.40 cited verbatim L942–945 |
| 8 | Audit-trail integrity: v1.2 §15.3/§15.4 history not overwritten | L851 ff., L881 ff. | PASS — both sections begin with "(revised v1.2.1)" header + explicit `> v1.2.1 correction.` blockquote prefacing the original claim being corrected; mistake disclosed not suppressed |

## Anti-fishing posture verification

- **Strictly tightening**: §15.7(b) — concentration provenance ADDED; Task 0.2b escalated NO-OP → NON-NO-OP (more verification, not less). Confirmed by inspection.
- **No threshold relaxed**: 4·SE PASS / 2·SE INDISTINGUISHABLE preserved (L955–956, L1070–1072).
- **Candidate-set closure §8(5) reaffirmed**: L489–493 + L1066–1067.
- **External-signal trigger**: MQ verdict ACCEPT_WITH_FLAGS at `scratch/2026-05-09-spec-v1.2-review/mq-verdict.md` cited explicitly (L1000, L1075).
- **Authority chain documented**: lit → SURVEY → spec → conformance → mismatch detected → NON-NO-OP re-fit (L979–981); the inverse (code → spec ratification) explicitly rejected (L983–985).

## Regressions checked, none found

- §0 reconciliation, §4.1 pitch cap, §5 cost specification, §6 primary forms, §7 PyMC + arviz, §8 invariants (10 items), §9 gates, §11 dependency graph, §13 dispatch precondition — all sections downstream of the patch boundary inspected; no edits outside §6.1, §15.3, §15.4, §15.7 + frontmatter.
- Beta(2.0, 38.0) confined to historical/contrast usage (C3 v0.3's OLD prior); Beta(4.5, 95.5) is the sole live pin.
- HALT-on-ELPD-rank-flip not weakened; in fact load-bearing-elevated (L1068–1069 item 9).

## Residual

None blocking. Two MQ FLAGs (G/H/I/J non-blocking carry-forwards from v1.2) remain untouched — out of scope for this patch.

## Recommendation

PROCEED to v1.2.1 promotion. Sub-task dispatch authorization in §13(5–6) survives; CLOSE plan v0.2 Phase 0 Task 0.2b NON-NO-OP execution unblocked. Independent MQ reverify on v1.2.1 should confirm before Phase 1 dispatch (already queued per §15.7(e)).

**Verdict**: ACCEPT.
