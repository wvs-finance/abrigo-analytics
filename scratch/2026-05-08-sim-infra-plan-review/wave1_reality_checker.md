# Wave-1 Reality Checker — `docs/plans/2026-05-07-sim-infra-0.md`

**Reviewer**: TestingRealityChecker (Wave-1 of 2-wave doc verify per `feedback_two_wave_doc_verification`)
**Default**: REJECT (per discipline + plan-document gating).
**Verdict**: **ACCEPT_WITH_FLAGS** — substantive content reality-grounds against spec v1.1.1, repo memory rules, and the file system; two BLOCK-class agent-registry mismatches plus several FLAGs require fix or explicit user adjudication before commit. Default-to-REJECT discipline tempered: every BLOCK has a one-line fix and none invalidates the plan's structure or scope.

---

## BLOCKs (must fix before commit)

### BLOCK-1 — `Data Engineer` agent is _archived_, not active

**Evidence.** `ls /home/jmsbpp/.claude/agents/engineering/` returns no `data-engineer.md`; the file lives at `_archived/engineering/engineering-data-engineer.md`. Plan line 148 names the Phase-2 author as `Data Engineer`. Spec v1.1.1 §11/§13 routes Phase-2 implementation through this agent. Memory `feedback_specialized_agents_per_task` is NON-NEGOTIABLE about specialist-per-task and explicitly forbids foreground authoring.

**Quoted text (plan L148):** "**Agent.** `Data Engineer` (per `feedback_specialized_agents_per_task`)."

**Why BLOCK.** Phase 2 is the *only* code-authoring task in the plan. If the named author does not exist in the active registry, Phase 2 cannot dispatch as written → silent foreground-authoring fallback is the predictable failure mode, which is exactly what the NON-NEGOTIABLE memory bans.

**Fix.** Either (a) un-archive `engineering-data-engineer.md` (user decision); (b) substitute `engineering-senior-developer.md` (active) and document the swap in a CORRECTIONS-α block; or (c) split Phase 2 across `engineering-backend-architect` (architecture) + `engineering-senior-developer` (code).

### BLOCK-2 — `Model QA Specialist` referenced for Wave-2 plan-doc verify; agent is _archived_

**Evidence.** Plan L346 (Phase-4 footnote) cites `feedback_two_wave_doc_verification` and asserts "this plan document was 2-wave verified (Reality Checker + Model QA)". `feedback_two_wave_doc_verification` defaults Wave-2 to **Model QA Specialist** for econometric specs and to a domain match for plans. `_archived/specialized/specialized-model-qa.md` is the only file matching that name. The spec under which this plan operates is econometric/structural; Wave-2 specialist must be picked.

**Quoted text (plan L346):** "this plan document was 2-wave verified (Reality Checker + Model QA) by foreground orchestration **before commit**".

**Why BLOCK.** The plan asserts a verify it cannot complete with active-registry agents. Either the assertion is fantasy (RC's primary failure pattern) or it requires a substitute. Foreground self-stating "verified" without a live specialist agent fails the rule.

**Fix.** Confirm Wave-2 specialist for THIS doc-verify cycle is `engineering-software-architect` or `specialized-workflow-architect` (both active) — both fit "implementation plan / process governance" Wave-2 mapping in the memory. Update the footnote at L346 accordingly. (Foreground may run this on the user's authority, but the agent name must match registry.)

---

## FLAGs (lower-severity follow-ups; do not block commit)

### FLAG-A — HALT-trigger discipline: explicit `feedback_pathological_halt_anti_fishing_checkpoint` ritual under-specified at gates 4.1 / 4.2

**Evidence.** Plan L332 ("On REJECT, surface to user with disposition memo per `feedback_pathological_halt_anti_fishing_checkpoint`") names the rule but does not enumerate the **5-step ritual** (HALT exception type + disposition memo + ≥3 pivot options + CORRECTIONS block + 2-wave post-hoc verify). Gate 4.2 (static analysis) L344 says "On any failure, HALT" with no ritual reference at all. The mutation-testing kill-rate sub-80% case (L282) lets the agent "iterate until ... met OR all surviving mutants documented as semantic-equivalent" — no HALT cascade if iteration plateau occurs.

**Fix.** Add one line to each gate: "On HALT, follow the 5-step ritual in `feedback_pathological_halt_anti_fishing_checkpoint` — typed exception, disposition memo, ≥3 user-enumerated pivots, CORRECTIONS block, 2-wave post-hoc verify."

### FLAG-B — `Data Engineer` is also named in spec v1.1.1 ecosystem; cross-doc consistency risk

**Evidence.** Memory `project_saas_builder_stage_2_active` ("REVERIFY-PASSED") records the iteration as currently expecting `engineering-data-engineer.md`. If BLOCK-1 is resolved by archiving-swap, the same swap propagates to all four future SAAS-COHORT plans. Plan does not pre-emptively flag this downstream impact.

**Fix.** Add a one-line note to plan L17 sub-task position section: "If `Data Engineer` is unavailable, downstream COHORT-1..4 plans must inherit the same substitution."

### FLAG-C — Phase 2 dispatched as a single agent for ~all of `simulations/{types,modules,utils,tests}`

**Evidence.** Plan L136 ("Single agent dispatch covering Phase 2"). This is large surface for one agent — Value tier + Callable tier + IO Boundary tier + tests + Hypothesis strategies + `pyproject.toml` edits. Contradicts the *spirit* of `feedback_specialized_agents_per_task` (per-task specialization) even though it satisfies the letter ("dispatches a specialist").

**Fix.** Optional — split Phase 2 into 2.1 (Value tier + types/), 2.2 (Callable tier + modules/), 2.3 (IO + utils/), 2.4 (tests/strategies.py). User adjudication.

### FLAG-D — `gsd-phase-researcher` (L84) is dispatched in a non-GSD-managed plan

**Evidence.** `feedback_planning_dir_bespoke_naming` flags GSD auto-detection as a conflation hazard in this multi-iteration repo. Plan correctly avoids `.planning/` GSD names but uses `gsd-phase-researcher` agent; this agent looks up `.planning/` files for context. If absent, behavior is undefined.

**Fix.** Specify in the brief that the agent must operate doc-driven (spec + plan paths supplied) and *not* read `.planning/`. Or substitute `gsd-project-researcher` after verifying its `.planning/`-independence.

### FLAG-E — Verification matrix (L394) is missing `Z_cap_pinned.json` schema-completeness check

**Evidence.** Spec §10 row "estimates/Z_cap_pinned.json" requires `audit_block: str` + `tier_mix: {...}`. Verification matrix L406 lists the artifact location only (`simulations/utils/`) but the Phase-4 Reality Checker brief at L319-329 does not enumerate JSON-schema audit. Reality Checker would not catch a missing field.

**Fix.** Add bullet 9 to L319-329 brief: "JSON IO writer-side: confirm `Z_cap_pinned.json` schema matches spec §10 row exactly."

### FLAG-F — Mutation kill-rate threshold pinned at 80% with no source citation

**Evidence.** Plan L279 pins "≥ 80%" and parenthetically references "§8(7) of spec for posterior CI-width threshold analog". §8(7) is **CI-width threshold for posteriors**, not mutation kill rate — they are not analogs. The 80% number is a soft industry default, not a spec-anchored figure.

**Fix.** Either (a) drop the false analogy to §8(7) and document 80% as plan-author judgment (acceptable); or (b) cite the actual `mutation-testing` skill default. One-line edit at L279.

### FLAG-G — Phase 5 Task 5.3 (PR refresh, L387) hardcodes PR number `3` and remote `wvs-finance/abrigo-analytics`

**Evidence.** Plan L387: "`gh pr edit 3 --repo wvs-finance/abrigo-analytics ...`". Memory `feedback_push_origin_not_upstream` is NON-NEGOTIABLE: push must go to `origin` (JMSBPP), never `upstream` (wvs-finance). The PR draft is at wvs-finance#3 by user choice (per `project_saas_builder_stage_2_active`), but the `git push` line at L386 says `git push origin iter/saas-builder-stage-2` correctly. The `gh pr edit` line is on the PR remote, which is consistent — but the conjunction is brittle.

**Fix.** Add a one-line precondition: "Confirm PR #3 still exists on wvs-finance/abrigo-analytics; if remote PR has migrated, update --repo arg." No memory rule violated.

---

## Spec-coverage cross-check (positive findings — no BLOCK)

Every spec v1.1.1 §6 row that is infrastructure (FX path (X/Y)_t, σ_T, ε(σ_T), TruncPareto/NegBin params, softplus, tier-prior, blender, parquet/JSON IO, audit-block sha) maps cleanly to a `simulations/` location in the verification matrix L394-407. **No coverage gap detected.**

Every NON-NEGOTIABLE memory rule the plan cites is honored at the structural level: code-agnostic (✓ — zero code blocks except shell git/uv invocations, which are operations not authored Python); 2-wave plan verify (✓ — Phase-4 footnote L346 + this artifact); functional-python re-read (✓ — Task 0.1 L54-60); bespoke `.planning/` naming (✓ — N/A, plan does not touch `.planning/`).

Out-of-scope discipline (PyMC, sympy, saas-builder-specific transforms): correctly enumerated L19; Phase 1 research Q4 (L89) on PyMC `TruncPareto` is forward-looking only and does not pull PyMC into Phase 2 implementation. **Honored.**

Sub-task graph correctness: plan correctly positions itself as **prereq** for SAAS-COHORT-1..4 (L17), not as one of the cohort plans. Verified against spec §11 dependency graph. **Honored.**

File-structure realism: folder-level only, with explicit "specific `.py` files inside each folder are decided by implementing agents at task-time" (L44). Consistent with user direction that .py decomposition is task-time discovery. **Honored.**

Honnibal sequence (Phase 3): tighten-types → contract-docstrings → hypothesis-tests → try-except → mutation-testing → pre-mortem (L193-306). Each pass committed separately (L208-211, 228-230, 247-249, 267-269, 286-288, 304-306). **Ordering correct.**

Phase 4 verification gates: ruff + ty + pytest with coverage ≥90% pinned (L341-343); mutation kill-rate 80% pinned (L279); functional-python compliance criteria enumerated 1-8 in 4.1 brief (L320-328). **Concrete and evaluatable.**

---

## Recommended path

ACCEPT_WITH_FLAGS PROCEED conditional on:
1. BLOCK-1 + BLOCK-2 resolved by user adjudication on agent substitutes (one-line CORRECTIONS-α addendum to plan).
2. FLAG-A applied (HALT ritual one-liners at 4.1 and 4.2).
3. FLAGs B–G optional; user discretion.

Plan is structurally sound; rejecting it for substitutable-agent naming would be process-theater.

---

**Word count**: ~1140
