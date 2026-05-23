# Cohort-3 Plan-Doc Reality-Checker Verdict — Wave 1 of 2

**Plan reviewed:** `docs/plans/2026-05-08-saas-cohort-3-revenue-form-loo.md` v0.1
**Spec anchor:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1
**Reviewer:** TestingRealityChecker (RC, Wave 1)
**Date:** 2026-05-07

---

## Verdict: ACCEPT_WITH_FLAGS

Default REJECT posture overcome: the ten reality-check dimensions all clear at BLOCK level. Three non-blocking FLAGs follow.

---

## Dimension-by-dimension findings

1. **Agent dispatchability** — PASS. Task 0.5 (lines 132–133) explicitly probes `engineering-ai-engineer`, `testing-reality-checker`, `specialized-model-qa`, `engineering-code-reviewer`, `gsd-phase-researcher` via filesystem find against the active (non-`_archived/`) registry; HALT trigger if any in `_archived/`. Filesystem confirms all five present at `~/.claude/agents/{engineering,testing,specialized}/...md` and `~/.claude/agents/gsd-phase-researcher.md`. **FLAG-1** below covers a downstream docs-consistency issue.

2. **Three Υ_t candidate forms exhaustively pinned with closure guard** — PASS. Pin R1 (lines 61–75) reproduces all three forms verbatim from spec §5/§6: martingale, AR(1)-log, det+churn. Pin R6 (line 104) declares closure. Task 2.2 line 235 mandates `CandidateSetClosedError` runtime guard in `FitDriver`; Task 2.5 line 308 makes its raise behaviour a regression test; RC audit Task 4.1 #9 (line 403) verifies by direct test execution. Closed set, no post-hoc 4th, runtime-enforced.

3. **PSIS-LOO-CV via `arviz.compare`** — PASS. Pin R2 (lines 77–81) explicitly calls `arviz.compare(model_dict, ic="loo", method="stacking")` and REJECTS AICc/WAIC-only/DIC/by-hand IC. Threshold pins R3 (lines 85–87): `|ΔELPD| > 4·SE` PASS, `2·SE ≤ |ΔELPD| ≤ 4·SE` MARGINAL, `< 2·SE` INDISTINGUISHABLE — verbatim match to required spec. Verdict-router test (line 311) covers all three boundaries.

4. **k̂ < 0.7 PSIS-LOO diagnostic gate** — PASS. Pin R4 line 98 pins `Pareto k̂ < 0.7 for ≥ 95%`; R3 line 89 routes `k̂ ≥ 0.7 on >5%` to FAIL. Pre-mortem Task 3.5 enumerates `k̂` excursion as a fragility (line 360); RC audit Task 4.1 #12 (line 406) checks the gate flag.

5. **File-path concreteness, no TBD** — PASS. File-structure block (lines 33–51) names every directory at folder-level granularity (with explicit deferral of `.py` decomposition to task-time per functional-python tier discovery — consistent with SIM-INFRA-0 precedent). Output paths in Pin R5 (line 102) are concrete: `cohort_3_idata_{martingale,ar1_log,det_churn}.nc`, `cohort_3_verdict.json`. No TBDs in plan body.

6. **Independence from C1/C2** — PASS. Header line 20: "Independent of COHORT-1 and COHORT-2 at execution time (revenue dynamics do not consume cost posteriors)". Out-of-scope block lines 23–24 explicitly excludes T1/T2 (C1/C2) work. No data-dependency edges from C1/C2 posteriors into C3 anywhere in plan.

7. **Out-of-scope discipline** — PASS. Lines 22–27: explicit exclusion of T1/T2 (C1/C2 cost work), Z-cap (C4), Stage-3 cohort survey, SIM-INFRA-0 patches, notebook-trio authoring. Discipline preserved in §15 self-review (line 547).

8. **Audit-pass chain Honnibal ordering** — PASS. Phase 3 (lines 325–381) executes tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing in that order, each with separate commit. Mirrors SIM-INFRA-0 v1.1 §15.5 explicitly (line 327). Pre-mortem precedes mutation-testing.

9. **2-wave verifier structure (RC + MQ before CR)** — PASS. Phase 4 line 386: Task 4.1 RC compliance (line 387), Task 4.2 MQ spec-doc reverify (line 418), Task 4.3 static sweep — all before Phase 5 Task 5.1 Code Reviewer (line 454). Note line 448 also pins **plan-document** 2-wave verify pre-commit at `scratch/2026-05-08-cohort-3-plan-review/` — i.e., this very verdict file's sibling.

10. **SIM-INFRA-0 contract-extension escape-hatch** — PASS. Line 16 + Phase 1 Task 1.1 Q3 (line 147) + Task 1.3 Step 3 (line 175) explicitly require: if `PosteriorDraws` insufficient, file `SIM_INFRA_0_V1_2_AMENDMENT_REQUEST.md` and **HALT this plan pending user adjudication. Do not silently extend the SIM-INFRA-0 contract.** Out-of-scope block reaffirms (line 26). Self-review checklist line 556 cross-confirms.

---

## Non-blocking FLAGs

**FLAG-1 (line 530–532, dispatch-map informality).** Strategic delegation map names agents informally as "AI Engineer", "Reality Checker", "Model QA Specialist", "Code Reviewer" — not the canonical registry IDs `engineering-ai-engineer`, `testing-reality-checker`, `specialized-model-qa`, `engineering-code-reviewer`. Task 0.5 uses canonical paths so dispatch is unambiguous in practice, but downstream task briefs (lines 156, 166, 193, 222, 251, 274, 302, 392, 422, 462) repeat the informal labels. *Recommendation v0.2:* normalize to canonical IDs throughout.

**FLAG-2 (line 343, monotonicity property scope).** The verdict-router monotonicity property test is described as INDISTINGUISHABLE for `[0,2)`, MARGINAL for `[2,4]`, PASS for `(4,∞)`. Pin R3 (line 86) defines MARGINAL as `2·SE ≤ |Δ| ≤ 4·SE` (closed both ends); Task 3.5 line 361 separately notes "closed/open interval discipline pinned per Pin R3" but the actual interval status at `=4·SE` (MARGINAL vs PASS) is ambiguous. *Recommendation v0.2:* state the boundary rule explicitly and align line 343 ranges accordingly.

**FLAG-3 (Phase 1 LFO-CV deferral).** Task 1.1 Q2 (line 146) correctly identifies that LOO under dependent observations is a known failure mode and asks for the LFO-CV alternative. Task 1.3 line 174 pre-resolves any disagreement by "pinning to spec §7 commitment with documented dissent". This honours the spec but encodes a possible statistical fragility (single-trajectory log-lik) that MQ Wave-2 should adjudicate explicitly. Not a plan-doc BLOCK — flagging for MQ Wave-2.

---

**Verdict:** ACCEPT_WITH_FLAGS — proceed to Wave-2 MQ. No BLOCKs; three FLAGs absorbable in v0.2 CORRECTIONS-α.

End of Wave-1 RC verdict.
