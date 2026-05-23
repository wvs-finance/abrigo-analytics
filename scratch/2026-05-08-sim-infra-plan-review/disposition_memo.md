---
artifact_kind: disposition_memo
parent_plan: docs/plans/2026-05-07-sim-infra-0.md (uncommitted, on-disk)
emit_timestamp_utc: 2026-05-08
trigger: 2-wave plan-doc verify returned ACCEPT_WITH_FLAGS / REJECT (Wave-1 RC: 2 BLOCKs + 7 FLAGs; Wave-2 MQ: 4 BLOCKs + 6 FLAGs)
authority: feedback_pathological_halt_anti_fishing_checkpoint
precedent: scratch/2026-05-07-prereg-review/disposition_memo.md (parent spec v1.0 → v1.1 cycle)
---

# Disposition memo — SIM-INFRA-0 plan v0.1 → v1.1

## §1 Combined verdict
6 BLOCKs total (2 RC + 4 MQ); 13 FLAGs (7 RC + 6 MQ). Plan does NOT commit-eligible without patch.

## §2 BLOCKs partition into two classes

### Class A — agent-registry mismatch (2 BLOCKs, RC)
- RC-BLOCK-1: `Data Engineer` filesystem path is `~/.claude/agents/_archived/engineering/engineering-data-engineer.md`. Currently dispatchable in this session (empirical: Wave-2 MQ dispatched successfully against archived path), but a fresh session loading `~/.claude/agents/` excluding `_archived/` would not find it. Plan's Phase-2 single-agent dispatch is session-fragile.
- RC-BLOCK-2: Same for `Model QA Specialist` at `~/.claude/agents/_archived/specialized/specialized-model-qa.md`.

### Class B — math-contract leakage (4 BLOCKs, MQ)
- MQ-BLOCK-1: TruncPareto $\alpha \ge 1.5$ floor (spec §8(6)) absent from Phase-2 behavior contract. Implementing agent could ship a TruncPareto sampler that admits $\alpha < 1.5$ posteriors at runtime.
- MQ-BLOCK-2: Softplus $\beta$ tightness pin ($L^1$ deviation $< 10^{-3}\cdot\kappa$, spec §5.1 (T2)) absent from `SoftplusParams` behavior contract. Agent could ship $\beta = 1$ trivially.
- MQ-BLOCK-3: Blended $p_t$ formula (spec §5.1) referenced by name only, never reproduced in agent-facing contract. Theatrical-fix risk: re-introduces v1.0 RC-FLAG-4 ($0.30/MTok cached-portion-vs-blended) bug.
- MQ-BLOCK-4: Parquet schemas pinned in spec §10 delegated back to implementing agent. IO boundary failure surface.

Class A is governance / dispatchability. Class B is math-correctness. Class B is unambiguously fixed by patching the plan to reproduce the four pinned equations + schemas verbatim in Phase-2 behavior contracts. Class A requires user adjudication.

## §3 Pivot options for Class A (agent registry)

### Option α — un-archive the two agents
Move `_archived/engineering/engineering-data-engineer.md` → `engineering/data-engineer.md` (or wherever the active path is). Same for `specialized/specialized-model-qa.md`. Then plan's existing agent names stand as-written.

**Pros.** Cheapest fix. Preserves the iteration's investment in these agents (Pair D Stage-2, dev-AI Stage-1, all 2-wave verifies on this iteration's spec, this plan's verify — all dispatched against `Model QA Specialist` successfully). Aligns RC's filesystem reality with the empirical session reality.

**Cons.** Why were they archived in the first place? May have been an upstream-package update; un-archiving risks reverting whatever fix that move embodied. User may not want to override an upstream maintainer's archive decision. Also: archive state may recur on next plugin update; this is a treadmill.

**User action.** `mv ~/.claude/agents/_archived/engineering/engineering-data-engineer.md ~/.claude/agents/engineering/data-engineer.md` and similar. Or surface to harness maintainer.

### Option β — substitute with active-registry equivalents
- Phase-2 `Data Engineer` → `AI Engineer` (active; matches Python data-pipeline scope per its description: "data pipelines, and AI-powered applications").
- All 2-wave verifies → `Reality Checker` (active; already used) + `Test Results Analyzer` (active; statistical / quality-metrics fit) instead of `Reality Checker` + `Model QA Specialist`. OR: Reality Checker + invoke `audit-econ` skill (Opus sub-agents + Delphi consensus; heavier but methodologically stronger for statistical models).

**Pros.** Plan's agent names are session-resilient — fresh sessions and future contributors don't depend on `_archived/` being loaded. No user filesystem ops.

**Cons.** Loses the iteration's investment in `Model QA Specialist` — it has been the load-bearing methodology auditor across 4 spec/plan reverify cycles in this iteration alone. `Test Results Analyzer` description ("Expert test analysis specialist focused on comprehensive test result evaluation, quality metrics analysis") is closer to test-output review than statistical-model audit. `audit-econ` skill is heavyweight and Delphi-flavored — different audit shape than `Model QA Specialist`'s direct expert review.

### Option γ — keep as-written + add CORRECTIONS-α addendum + surface filesystem state to user
Plan keeps agent names. Add a §"Pre-flight registry check" task at the start that runs `find ~/.claude -name 'engineering-data-engineer*' -o -name 'specialized-model-qa*'` and HALTs if either is in `_archived/` AND not also active in the current session's dispatchable registry. CORRECTIONS-α records the discrepancy; user picks un-archive vs substitute at execution time.

**Pros.** Defers the registry decision until execution (when the session-level fact pattern is known). Preserves the audit trail of the discrepancy without forcing a fix now.

**Cons.** Punts the decision. RC reads this as theatrical (BLOCK still binds at execution-start instead of plan-commit).

### Option δ — hybrid: substitute Phase-2 implementer; preserve verifiers
Phase-2 dispatcher: `AI Engineer` (active). Verifiers (RC + MQ) stay as-written because RC is active and MQ has been working for this iteration. Plan adds a CORRECTIONS note that MQ's filesystem-archive state should be surfaced to user; if a future session can't dispatch it, switch to `audit-econ` skill.

**Pros.** Minimum-friction fix. Phase-2 implementer is session-resilient; verifiers preserved with a fallback documented.

**Cons.** Asymmetric — implementer fixed, verifiers pending. RC could read this as half-measure.

## §4 Recommendation

**Class B (math BLOCKs): unambiguously patch.** Add a Phase-2 "Behavior contracts — math pins" subsection that reproduces verbatim:
- spec §8(6) Pareto-α floor
- spec §5.1 (T2) softplus $L^1$-deviation regularization criterion
- spec §5.1 blended $p_t$ formula
- spec §10 parquet column schemas

Plus the 6 MQ-FLAGs (FX-path equation source anchor; audit-pass ordering swap mutation-testing ↔ pre-mortem; pre-mortem scope to include `utils/`; joint-identifiability $(\alpha, x_m, \kappa)$ property; equivalent-mutant exemption cap; saas-α-floor leak).

Plus the 7 RC-FLAGs (HALT-ritual at gates 4.1/4.2; downstream cohort-plan propagation; Phase-2 single-agent-large-surface mitigation; gsd-phase-researcher `.planning/` interaction; `Z_cap_pinned.json` schema in 4.1; mutation 80% / spec §8(7) false analogy; PR-number hardcode).

**Class A (agent registry): user picks.** My recommendation: **Option α (un-archive)** — preserves the iteration's audit-trail investment and is the cheapest fix; user filesystem op is single `mv`. Falls back to Option δ if user does not want to override the archive.

## §5 What user adjudication unblocks

1. Class B BLOCKs and FLAGs patched into v1.1 of the plan (single CORRECTIONS-α revision).
2. Plan-doc 2-wave reverify dispatched against v1.1.
3. On reverify ACCEPT, plan committed.
4. On commit, advance to: author SAAS-COHORT-1..4 plans (in parallel; they're independent at plan-authoring time).

End of disposition memo.
