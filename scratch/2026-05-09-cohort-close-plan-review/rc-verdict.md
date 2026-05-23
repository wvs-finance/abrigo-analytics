# RC Verdict — SAAS-COHORT-CLOSE plan-doc verify (Wave 1 of 2)

**Plan reviewed:** `docs/plans/2026-05-09-saas-cohort-close.md` v0.1
**Reviewer:** Reality Checker (TestingRealityChecker)
**Default posture:** REJECT unless overwhelming evidence.

## Verdict: **ACCEPT_WITH_FLAGS**

Reality-check on all 10 dimensions returned no BLOCK-grade defects. Five non-blocking FLAGs documented. The 9 leftover items map cleanly to phases; agent registry is verified-clean; dependency graph is acyclic and correct; anti-fishing invariants carry forward verbatim; out-of-scope discipline holds; audit-pass chain is invoked on every code-touching task; 2-wave verify is scheduled where the plan brief requires it.

## Dimension-by-dimension findings

**D1 — 9-item coverage.** PASS. Self-review checklist (lines 307–316) maps each item to its phase; spot-check confirms Phase 0 = item 1, Phase 2 = item 2, Phase 4 = item 3, Task 3.1 = item 4 (11 sub-items per line 167), Tasks 3.2–3.4 = item 5 (~14 nits cross-referenced to audit FLAGs verbatim), Phase 1 = item 6, Phase 5 = item 7, Phase 6 = item 8, Phase 7 = item 9.

**D2 — Agent dispatchability.** PASS. All 5 named agents found in active registry (none in `_archived/`):
- `~/.claude/agents/testing/testing-reality-checker.md`
- `~/.claude/agents/specialized/specialized-model-qa.md`
- `~/.claude/agents/engineering/engineering-technical-writer.md`
- `~/.claude/agents/engineering/engineering-ai-engineer.md`
- `~/.claude/agents/engineering/engineering-code-reviewer.md`

**D3 — Phase-dependency graph.** PASS. Graph (lines 36–45) is acyclic; declared edges P1⟵P0, P2⟵P0, P3 free, P4⟵P1∧P2, P5⟵P1∧P2∧P3∧P4, P6⟵P5, P7⟵P6 are sensible: spec-v1.2 (P0) precedes driver scripts (P1) so revenue_form_verdict.json reflects the locked S_t form; P2 (re-parameterization) needs spec baseline; P4 (schema bump) needs both driver scripts and re-parameterized model; P5 (memo) needs all artifact-producing phases.

**D4 — File-path concreteness.** PASS. Every task names exact paths (e.g., `scripts/run_cohort{2,3,4}_emit.py`, `simulations/saas_builder/types/`, `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`). The single placeholder `<MERGE_SHA_PHASE_7>` (Task 6.2 line 264) is closed-loop-back-filled by Task 7.4 — explicitly disclosed and acceptable.

**D5 — Anti-fishing invariants.** PASS. Lines 26–30 pin N_MIN=75, POWER_MIN=0.80, MDES_SD=0.40 verbatim from CLAUDE.md; HALT triggers explicit at Tasks 0.3, 2.4 ("do NOT silently raise N_draws — that converts Path β into Path β+α and must be user-adjudicated"), 4.2, 5.2; 1/κ post-hoc fit captured as Phase 6 case study (line 250).

**D6 — Out-of-scope discipline.** PASS. Lines 20–24 enumerate Stage-3 deferrals: real-data conditioning, hierarchical pooling for C3, on-chain Panoptic, per-tier θ_k differentiation IF Path α chosen.

**D7 — Audit-pass chain.** PASS. Honnibal order invoked verbatim at every code-touching task (1.1 §Step 2, 1.2 §Step 2, 1.3 §Step 2, 2.3 §Step 2, 3.1 §Step 1, 3.2–3.4, 4.1 §Step 2).

**D8 — 2-wave verify coverage.** PASS. RC+MQ scheduled at Phase 0 (Task 0.3), Phase 2 (Task 2.5), Phase 5 (Task 5.2). Phase 4 has RC-only (Task 4.2) — see FLAG-2.

**D9 — Path β rationale.** PASS. Lines 117–118 defend Path β over Path α on three methodological grounds: (i) also resolves C1 MQ-FLAG-1 (`pi` near-prior structurally), (ii) spec §5.4 hints at per-tier θ_k as methodological richness, (iii) sub-linear compute scaling. This is methodologically defensible — Path α would silently mask the structural identification weakness flagged by MQ.

**D10 — Format precedent compliance (vs. SIM-INFRA-0 v1.1).** PARTIAL — see FLAG-1, FLAG-3.

## FLAGs (non-blocking)

**FLAG-1 (LOW, format).** Plan lacks an explicit "Strategic delegation map" section. SIM-INFRA-0 uses one to centralize the agent-by-task table; this plan distributes "Agent assignment" lines per-phase instead. Equally readable but fragments the dispatch picture. Recommend a 7-row summary table near the top before Phase 0 dispatch.

**FLAG-2 (LOW, verify-coverage asymmetry).** Phase 4 (schema bump v1.0→v1.1) gets RC-only verify (Task 4.2), no MQ wave. The brief's expectations enumerate "schema bump (P4)" as a 2-wave item. Either elevate to RC+MQ or document why backward-compat reading is purely RC-scope.

**FLAG-3 (LOW, format).** No "Verification matrix" cross-reference table (SIM-INFRA-0 line 378 has one). The Self-review checklist (line 305) partially substitutes but does not cross-reference verify-waves to evidence locations.

**FLAG-4 (LOW, plan-version semantics).** Task 2.1 §Step 2 conditional version-bump rule ("v0.1 → v0.2 IF the verify-cycle has not yet shipped, else v0.2 → v0.3") is ambiguous. Pin a single deterministic rule.

**FLAG-5 (LOW, sidecar lifecycle).** Phase 4 marks `Z_cap_pinned.SIGN_VERDICTS.md` deprecated but keeps emitting it "through Phase 5 for downstream-consumer grace period" (line 202). Define the removal commit explicitly (Phase 7 or Stage-3-opening) so deprecation does not become permanent.

## Recommendation

**ACCEPT_WITH_FLAGS → PROCEED to MQ Wave 2.** All FLAGs are LOW; address in CORRECTIONS-α §15 before Phase 0 dispatch or as part of plan v0.2.

**Files referenced:**
- `/home/jmsbpp/apps/abrigo-analytics/docs/plans/2026-05-09-saas-cohort-close.md`
- `/home/jmsbpp/apps/abrigo-analytics/docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md`
- `/home/jmsbpp/apps/abrigo-analytics/docs/plans/2026-05-07-sim-infra-0.md`
- `/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-08-saas-cohort-{1,2,3,4}-independent-audit/`
