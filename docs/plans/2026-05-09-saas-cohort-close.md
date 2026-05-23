# SAAS-COHORT-CLOSE — Stage-2 Iteration Wrap-up (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `feedback_no_code_in_specs_or_plans` (NON-NEGOTIABLE), this plan does NOT contain code blocks. Each task dispatches a specialized agent who authors code per the `functional-python` skill and the audit-pass chain (tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing).
>
> **Foreground orchestrates, never authors.** Per repo memory `feedback_specialized_agents_per_task` (NON-NEGOTIABLE).

**Plan version:** v0.2 (post-2-wave-plan-verify; CORRECTIONS-α applied — see §15)
**Emit timestamp:** 2026-05-08
**Predecessor iteration HEAD:** `e675dc8` on `iter/saas-builder-stage-2` (COHORT-4 v0.3 ACCEPT_WITH_FLAGS)
**Spec anchor:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1 (REVERIFY-PASSED). Phase 0 of THIS plan amends it to v1.2.
**Status:** READY-FOR-REVERIFY — RC + MQ 2-wave on this plan-doc v0.2 REQUIRED before Phase 0 dispatch.

**Goal:** Take the 4-cohort SaaS-builder Stage-2 iteration from current ACCEPT-grade per-cohort state to a publishable Stage-2 verdict memo + closed PR #3, resolving 9 leftover items (spec ambiguity, MC budget, schema bump, residuals, nits, real-artifact emission, modeling memo, memory hygiene, PR finalize) without introducing scope drift.

**Architecture:** Seven sequential phases with strict dependencies (P1 ⟵ P0; P2 ⟵ P0; P3 free; P4 ⟵ P1 ∧ P2; P5 ⟵ P1 ∧ P2 ∧ P3 ∧ P4; P6 ⟵ P5; P7 ⟵ P6). Each code-touching phase runs the full Honnibal audit-pass chain. Phases that emit external artifacts (spec amendment, re-fit C1, schema bump, modeling memo) trigger an independent RC + MQ 2-wave verify before merge to `iter/saas-builder-stage-2`.

**Tech stack:** Python 3.13 + uv + ruff + ty + pytest + Hypothesis + PyMC + ArviZ + mutmut. No new runtime deps.

**Out of scope (Stage-3, NOT this plan):**
- Real-data conditioning (this iteration remains synthetic-Bayesian).
- Hierarchical pooling for COHORT-3 Υ_t form selection.
- On-chain Panoptic deployment / live LP capital tests.
- **Per-tier θ_k differentiation (deferred to Stage-3 unconditionally per v0.2 CORRECTIONS-α — see §15 BLOCK-1 resolution).**

**Anti-fishing posture (carried forward, NON-NEGOTIABLE):**
- N_MIN = 75; POWER_MIN = 0.80; MDES_SD = 0.40 SD-units of Y.
- Sign expectations and primary specifications pinned pre-data per spec v1.1.1 §6 and v1.2 amendments.
- Any phase exposing spec drift (data contradicts pre-pinned sign / threshold / functional form) triggers HALT + disposition memo + user-enumerated pivot + CORRECTIONS-α block + post-hoc 3-way review per `feedback_pathological_halt_anti_fishing_checkpoint`.
- Threshold tuning post-hoc is silent-fishing and BANNED. The 1/κ post-hoc fit caught by COHORT-4 MQ is the canonical case study (captured in Phase 6 memory).
- **v0.1 Path β (per-tier θ_k re-parameterization) is itself a case study of post-hoc retro-fit caught by 2-wave verify; v0.2 demotes it and adopts Path α (brute N_draws). Phase 6 `feedback_post_hoc_fit_anti_fishing_pattern.md` will memorialize both 1/κ and the v0.1→v0.2 Path β rejection.**

---

## Strategic delegation map (per SIM-INFRA-0 v1.1 format precedent)

| Phase | Primary agent | Verify wave(s) | Rationale |
|---|---|---|---|
| P0 — Spec v1.2 | Model QA Specialist (lit survey + amendment) | RC + MQ 2-wave (Task 0.3) | Spec amendment must be methodology-led, not implementation-led (BLOCK-2 resolution). |
| P1 — Driver scripts | AI Engineer × 3 (parallel) | RC light-pass on commits (FLAG-1 resolution) | Posterior-rebuild scripts merit seed/run-determinism check. |
| P2 — MC budget Path α | AI Engineer (re-fit) | RC + MQ 2-wave (Task 2.5) | Brute N_draws bump; deterministic; spec-faithful. |
| P3 — Residuals + nits | AI Engineer × 4 (parallel) | Audit-pass chain per file | Mechanical cleanup. |
| P4 — Schema v1.0 → v1.1 (additive) | AI Engineer | RC + MQ 2-wave (Task 4.2) | Backward-compat correctness + math-contract preservation (FLAG-2 resolution). |
| P5 — Modeling memo | Technical Writer | RC + MQ 2-wave (Task 5.2) | Empirical claim grounding + methodology summary fidelity. |
| P6 — Memory hygiene | Foreground | None (process) | 3 feedback memos + project memory rename. |
| P7 — PR #3 finalize | Foreground | User adjudication | Per `feedback_no_merge_without_approval`. |

---

## Phase dependency graph

```
P0 (spec v1.1.1 → v1.2)
 ├─► P1 (driver scripts)         ─┐
 ├─► P2 (MC budget Path α)       ─┤
                                  ├─► P4 (Z_cap_pinned schema bump, additive)
P3 (residuals + nits sweep) ─────┤
                                  ├─► P5 (modeling memo)
                                  └─► P6 (memory hygiene)
                                       └─► P7 (PR #3 finalize)
```

---

## Phase 0 — Spec v1.1.1 → v1.2 amendment (C3 Det+churn $S_t$ ambiguity)

**Trigger.** COHORT-3 v0.3 MQ-FLAG-2: spec §5 Det+churn revenue form does not pin whether $S_t$ is the deterministic factor `(1-λ)^t`, Bernoulli per-step, exponential survival, or Weibull. The C3 implementer chose deterministic, but the ambiguity persists in the locked spec text. **Per v0.2 BLOCK-2 resolution, the amendment direction is decided by methodology grounds (Task 0.1 lit survey) — NOT to ratify the existing C3 implementation.**

**Files**
- Modify: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (additive amendment block §5.X plus version bump v1.1.1 → v1.2 in header).
- Create: `scratch/2026-05-09-saas-cohort-close/phase0-spec-amendment-rationale.md` (decision memo with literature anchors + cohort-specific churn semantics for solo AI-native LATAM builders).

**Agent assignment.** Drafting: `Model QA Specialist` (spec §5 Det+churn semantics). Decision memo: same agent. Independent verify: 2-wave (`Reality Checker` + a second `Model QA Specialist`) on the amendment + memo.

### Task 0.1 — Survey churn-form precedent (methodology-led, NOT implementation-led)
- [ ] **Step 1** — Foreground dispatches `Model QA Specialist` with brief: enumerate the 4 candidate $S_t$ forms (deterministic factor, Bernoulli per-step, exponential continuous-time survival, Weibull with shape parameter), cite ≥2 SaaS-cohort literature sources per form, articulate the cohort-specific churn semantics for solo AI-native LATAM builders, and **recommend** the methodologically-correct form. The brief explicitly forbids the agent from anchoring on what C3's existing code computes; the recommendation must be defensible from first principles.
- [ ] **Step 2** — Output written to `scratch/2026-05-09-saas-cohort-close/phase0-spec-amendment-rationale.md`. Memo MUST include: (a) the 4-way comparison table; (b) recommended form with citation chain; (c) explicit statement of what C3's current code computes, separate from the recommendation; (d) divergence flag if (b) ≠ (c).
- [ ] **Step 3** — No commit yet (rationale memo informs Task 0.2 decision).

### Task 0.2 — Author v1.2 amendment block (selects per Task 0.1, NOT per C3 code)
- [ ] **Step 1** — `Model QA Specialist` writes additive amendment to spec §5 pinning $S_t$ to **whatever Task 0.1 recommends** — NOT necessarily the deterministic factor. The amendment text quotes the Task 0.1 rationale and cites the literature anchors.
- [ ] **Step 2** — Bump spec header version `v1.1.1` → `v1.2`; append CHANGELOG entry citing this plan + COHORT-3 MQ-FLAG-2 source + Task 0.1 memo.
- [ ] **Step 3** — Verify no other §5 sub-sections need rewriting (read spec end-to-end).
- [ ] **Step 4** — Commit: `docs(spec): amend Stage-2 prereg v1.1.1 → v1.2 — pin Det+churn S_t per Task 0.1 lit survey (resolves C3 MQ-FLAG-2)`.

### Task 0.2b — Conditional C3 re-fit + ELPD recompute (HALT-routed)
- [ ] **Step 1** — IF Task 0.1 recommendation ≠ deterministic factor (i.e., Task 0.2 amendment changes the form C3 computes), foreground HALTs Phase 0 promotion. Disposition memo enumerates the gap.
- [ ] **Step 2** — Dispatch `AI Engineer` to update C3 implementation to the new $S_t$ form; re-run PSIS-LOO-CV across the 4 candidate Υ_t forms under the new $S_t$.
- [ ] **Step 3** — Compare new ELPD ranking to v0.3 ranking. If ranking changes, HALT + CORRECTIONS-α + user adjudication (form-choice changing the Det+churn-vs-AR(1)-vs-martingale ranking is a Stage-2 verdict shift, not a spec-amendment housekeeping item).
- [ ] **Step 4** — IF ranking unchanged, commit re-fit and proceed. IF ranking changed, await user pivot decision.
- [ ] **Step 5** — IF Task 0.1 recommendation = deterministic factor (status quo), Task 0.2b is a no-op; document as "no-op confirmed" in CORRECTIONS-α §15.

### Task 0.3 — Independent 2-wave verify
- [ ] **Step 1** — Foreground dispatches `Reality Checker` (Wave 1): does v1.2 amendment text match the Task 0.1 lit-survey recommendation? Are literature citations grounded? Is Task 0.2b correctly routed (no-op vs. re-fit)?
- [ ] **Step 2** — Foreground dispatches a second `Model QA Specialist` (Wave 2, independent): is the chosen $S_t$ form methodologically defensible vs. the 3 alternatives? Does it preserve identification of cohort-specific λ? If C3 was re-fit, does the new ELPD ranking hold up under k̂ sensitivity?
- [ ] **Step 3** — On any BLOCK: HALT + CORRECTIONS-α; cycle Tasks 0.2 → 0.3 until both waves return ACCEPT or ACCEPT_WITH_FLAGS.

---

## Phase 1 — Real-artifact emission driver scripts (C2, C3, C4)

**Trigger.** Code for each cohort exists; only `scripts/run_cohort1_emit.py` is committed. Cohorts 2/3/4 need parallel driver scripts to emit gitignored artifacts under `simulations/saas_builder/data/`.

**Files**
- Create: `scripts/run_cohort2_emit.py` — produces `simulations/saas_builder/data/{ROBUSTNESS_RESULTS.md, PRIMARY_RESULTS.md, gate_verdict.json}`.
- Create: `scripts/run_cohort3_emit.py` — produces `simulations/saas_builder/data/revenue_form_verdict.json`.
- Create: `scripts/run_cohort4_emit.py` — consumes outputs of {C1, C2, C3} emit scripts; produces `simulations/saas_builder/data/Z_cap_pinned.json` + `Z_cap_pinned.SIGN_VERDICTS.md` (the latter remains until Phase 4 schema bump retires it; removal pinned in Phase 7 — see FLAG-5 resolution).
- Modify: `simulations/saas_builder/__init__.py` IF additional public exports needed for driver-script ergonomics (decided at task-time by implementer).

**Agent assignment.** Three `AI Engineer` dispatches in parallel (one per cohort script — independent file paths, no shared mutable state). Each runs the audit-pass chain on its own commit. **RC light-pass on each commit** verifies seed-pinning + run-determinism (per v0.2 MQ-FLAG-1 resolution).

**Dependency.** Phase 0 must be complete: revenue_form_verdict.json field for $S_t$ form must reflect spec v1.2 wording (and C3 code must reflect Task 0.2b outcome).

### Task 1.1 — Author run_cohort2_emit.py (parallel)
- [ ] **Step 1** — Dispatch `AI Engineer` (C2 brief): mirror `scripts/run_cohort1_emit.py` structure; load C2 fitted posterior from in-memory rebuild (no checkpoint files committed); compute the 24 spec §5.2 robustness brackets; emit `ROBUSTNESS_RESULTS.md`, `PRIMARY_RESULTS.md`, `gate_verdict.json`.
- [ ] **Step 2** — Audit-pass chain on the new script: `tighten-types`, `contract-docstrings`, `hypothesis-tests`, `try-except`, `pre-mortem`, `mutation-testing` on any new module-tier functions extracted.
- [ ] **Step 3** — Run script end-to-end locally; verify all three artifacts written and gate JSON parses.
- [ ] **Step 4** — Commit: `feat(saas-cohort-2): driver script emits robustness + primary + gate artifacts`.
- [ ] **Step 5** — Foreground dispatches `Reality Checker` light-pass: confirm seed-pinning + run-determinism (re-run twice, compare hashes).

### Task 1.2 — Author run_cohort3_emit.py (parallel)
- [ ] **Step 1** — Dispatch `AI Engineer` (C3 brief): rebuild PSIS-LOO-CV across the 4 candidate Υ_t forms under spec v1.2 $S_t$ form; emit `revenue_form_verdict.json` with elpd_loo, se_diff, chosen_form, $S_t$ form string (per spec v1.2), and per-form pareto-k diagnostics.
- [ ] **Step 2** — Same audit-pass chain.
- [ ] **Step 3** — Run end-to-end; verify JSON parses and chosen_form matches spec v1.2 + Task 0.2b outcome.
- [ ] **Step 4** — Commit: `feat(saas-cohort-3): driver script emits revenue_form_verdict.json (Υ_t selection)`.
- [ ] **Step 5** — RC light-pass.

### Task 1.3 — Author run_cohort4_emit.py (sequential after 1.1, 1.2)
- [ ] **Step 1** — Dispatch `AI Engineer` (C4 brief): load `gate_verdict.json` (C2), `revenue_form_verdict.json` (C3), and rebuild C1 posterior; compose Z_cap pinned object + per-TP sign verdicts; emit `Z_cap_pinned.json` (current shipped schema) + `Z_cap_pinned.SIGN_VERDICTS.md` sidecar.
- [ ] **Step 2** — Audit-pass chain.
- [ ] **Step 3** — Run end-to-end; verify both artifacts; cross-check 5-TP sign cert PASS. **HALT trigger:** if 5-TP sign cert FAILs on real-C1 re-build (e.g., due to a Phase-3 nit affecting `tier_idx` builder slot-0), HALT + CORRECTIONS-α + user-adjudicated pivot (per v0.2 MQ-FLAG-2 resolution).
- [ ] **Step 4** — Commit: `feat(saas-cohort-4): driver script emits Z_cap_pinned + sign verdicts sidecar`.
- [ ] **Step 5** — RC light-pass.

### Task 1.4 — `make emit-cohorts` Makefile target
- [ ] **Step 1** — Add target running 1 → 2 → 3 → 4 sequentially; depend on `simulations/saas_builder/` source presence; output dir = `simulations/saas_builder/data/` (gitignored).
- [ ] **Step 2** — Document in `simulations/saas_builder/README.md` (create if absent).
- [ ] **Step 3** — Commit: `chore: make emit-cohorts target for full Stage-2 artifact regeneration`.

---

## Phase 2 — COHORT-1 MC budget on real C1 (Path α: brute N_draws bump, spec-faithful)

**Trigger.** C4 MC error budget: stderr/Ẑ = 1.3e-2 vs 1e-3 ceiling at CV=0.84. HALT-routed via `MCErrorBudgetExceededError`. Decision: **Path α (brute N_draws ≈ 7.1e5)** — deterministic, requires NO spec amendment, faithful to spec v1.1.1 §5.4 (which deferred per-tier θ_k differentiation, not authorized it). Path β (per-tier θ_k re-parameterization) was proposed in plan v0.1 and **rejected** by 2-wave verify as anti-fishing-suspect retro-fit (v0.1 misread spec §5.4 deferral as a hint; converted a LOW documentation flag — C1 MQ-FLAG-1 — into 3× free parameters with unaudited identification consequences). See §15 CORRECTIONS-α v0.1 → v0.2 BLOCK-1 for full rationale.

**Files**
- No spec amendment. Spec stays at v1.2 from Phase 0.
- No code changes to `simulations/saas_builder/priors.py` or `model.py` (model parameterization unchanged).
- Modify (run-config only): driver invocation N_draws upped to ≈ 7.1e5 in `scripts/run_cohort1_emit.py` and downstream C4 emit.
- Re-emit: artifacts that depend on real-C1 posterior via `make emit-cohorts`.

**Agent assignment.** Implementation: `AI Engineer` (run-config bump only; no model surgery). Independent verify: 2-wave (`Reality Checker` + `Model QA Specialist`) on re-fit MC error + sign-cert stability.

**Dependency.** Phase 0 complete (spec v1.2 baseline). Phase 1 complete (driver scripts ready for re-emit cycle).

### Task 2.1 — Plan-level Path α adoption (this CLOSE plan)
- [ ] **Step 1** — `Model QA Specialist` confirms in §15 CORRECTIONS-α that Path α is the spec-faithful resolution; per-tier θ_k differentiation is Stage-3 scope (already enumerated under Out-of-scope in this plan header).
- [ ] **Step 2** — Plan version bump rule (deterministic, per v0.2 RC-FLAG-4 resolution): **plan version is bumped exactly once per RC+MQ 2-wave plan-doc verify cycle that returns BLOCKs.** Current cycle: v0.1 → v0.2 (this revision). Future cycles bump v0.2 → v0.3 → v0.4 in the same fashion. No conditional "IF the verify-cycle has not yet shipped" branch.
- [ ] **Step 3** — No commit needed for §15 (already in this v0.2 plan).

### Task 2.2 — Re-fit C1 with N_draws ≈ 7.1e5 + re-emit artifacts
- [ ] **Step 1** — Dispatch `AI Engineer`: bump N_draws in C1 driver invocation to 7.1e5 (or smallest power-of-two-friendly N satisfying stderr/Ẑ < 1e-3 at CV=0.84 per pilot test); re-fit on existing model (no re-parameterization); run `make emit-cohorts` end-to-end.
- [ ] **Step 2** — Verify C4 MC error budget: stderr/Ẑ < 1e-3 on CV=0.84 real-C1 input.
- [ ] **Step 3** — Verify 5-TP sign cert PASS preserved (no flips vs. v0.3 baseline on signs).
- [ ] **Step 4** — C1 MQ-FLAG-1 (`pi` posterior structurally near-prior) is **NOT** resolved by Path α — it remains a documented spec-property of Stage-2 (per-tier θ_k deferred to Stage-3). FLAG-1 routes to Phase 3 Task 3.1 as a one-line caveat in C1 plan v0.4 §"v0.3 → v0.4" (per v0.2 BLOCK-1 resolution).
- [ ] **Step 5** — Commit: `chore(saas-cohort-1): re-emit Stage-2 artifacts with N_draws=7.1e5 (MC budget Path α)`.

### Task 2.3 — Independent 2-wave verify (Phase 2)
- [ ] **Step 1** — Foreground dispatches `Reality Checker`: does the re-fit hit stderr/Ẑ < 1e-3? Are 5-TP signs unchanged vs. v0.3 baseline? No spec amendment shipped (correct: Path α requires none)?
- [ ] **Step 2** — Foreground dispatches `Model QA Specialist`: is identification preserved? Are posterior diagnostics (R-hat, ESS, divergences) clean? Is the brute N_draws rationale documented as deterministic budget remediation?
- [ ] **Step 3** — On BLOCK: HALT + CORRECTIONS-α; cycle Tasks 2.2 → 2.3.

---

## Phase 3 — Residuals + nits sweep (free of P0/P1/P2 dependencies)

**Trigger.** 6 C1 cosmetic residuals + ~14 cross-cohort nits accumulated across review waves. Single sweep avoids 4 separate small commits going stale.

**Files (per cohort, all in `simulations/saas_builder/`):**
- C1: `_AUDIT.json` writer, `tau_t_observed` branch, Dirichlet `pi` flat-ravel, tier_idx builder slot-0, prior-predictive cohort emission test, `__init__.py` exports, ravel ordering, `[:n_rows]` truncation, relative `base_dir`, short-circuit, atomic `_AUDIT.json` write. **Plus:** one-line caveat in C1 plan v0.4 §"v0.3 → v0.4" documenting that `pi` posterior is structurally near-prior in COHORT-1 because tier-conditional θ_k is deferred to Stage-3 (per v0.2 BLOCK-1 resolution; resolves C1 MQ-FLAG-1).
- C2: `delta_upper_bound_95` field-name fix (rename or parameterize by ci_level).
- C3: Mapping import collapse, SupportsFloat redundancy, cv_method literal collapse, line-length, set-membership tightening, audit-block-ordering test.
- C4: PRE-linearized docstring fix, isort, `__all__` alpha-sort, `_z_cap_pinned_equal` privacy, `RuntimeError` → typed cohort-4 error.

**Agent assignment.** One `AI Engineer` per cohort, four parallel dispatches; consolidated commit per cohort.

### Task 3.1 — C1 residuals sweep + MQ-FLAG-1 caveat
- [ ] **Step 1** — Dispatch `AI Engineer` (C1 brief): enumerate the 11 C1 items above; address each; add one-line caveat in C1 plan v0.4; run audit-pass chain on touched files.
- [ ] **Step 2** — Run full saas_builder test suite; expect green.
- [ ] **Step 3** — Commit: `chore(saas-cohort-1): residuals sweep — 11 items + pi-near-prior caveat (MQ + RC + CR flags)`.

### Task 3.2 — C2 nit sweep
- [ ] **Step 1** — Dispatch `AI Engineer` (C2 brief): rename `delta_upper_bound_95` to a ci_level-parameterized field or fix the field-name lie when ci_level≠0.95.
- [ ] **Step 2** — Audit-pass chain on touched files; full test suite green.
- [ ] **Step 3** — Commit: `chore(saas-cohort-2): nit — delta upper-bound field-name parameterization`.

### Task 3.3 — C3 nit sweep
- [ ] **Step 1** — Dispatch `AI Engineer` (C3 brief): 6 nits.
- [ ] **Step 2** — Audit-pass chain; tests green.
- [ ] **Step 3** — Commit: `chore(saas-cohort-3): nit sweep — 6 items (CR + MQ flags from v0.3)`.

### Task 3.4 — C4 nit sweep
- [ ] **Step 1** — Dispatch `AI Engineer` (C4 brief): 5 nits including `RuntimeError` → typed `Cohort4Error` subclass.
- [ ] **Step 2** — Audit-pass chain; tests green.
- [ ] **Step 3** — Commit: `chore(saas-cohort-4): nit sweep — 5 items (CR flags from v0.3)`.

---

## Phase 4 — `Z_cap_pinned.json` schema bump (v1.0 → v1.1, **truly additive**)

**Trigger.** Sidecar `Z_cap_pinned.SIGN_VERDICTS.md` is the per-TP sign-verdict workaround because shipped schema lacks per-TP fields. Plan v0.2/v0.3 of COHORT-4 deferred. Now that all artifacts re-emit under spec v1.2 + Path α (Phase 2), the schema can absorb the sidecar additively.

**Schema-bump semantics (per v0.2 BLOCK-3 resolution).** Additive means **v1.1 reader is a superset of v1.0 reader**. New per-TP fields are `Optional[…]` in `ZCapPinned` with default `None` (or empty container). v1.0 JSON files load successfully under v1.1 with new fields = `None`. v1.1 JSON files emit with new fields populated. Round-trip test: v1.0 load → v1.1 emit (with absent fields = `None`) → v1.0 read still succeeds. The transient Pydantic validator in `simulations/utils/json_io.py` accepts both versions.

**Files**
- Modify: `simulations/saas_builder/types/` (the `ZCapPinned` frozen-dc; add `Optional` per-TP sign-verdict fields with default `None`; bump `schema_version` Final constant `1.0` → `1.1`).
- Modify: `simulations/utils/json_io.py` transient Pydantic validator to accept both `schema_version` values.
- Modify: `simulations/saas_builder/emit.py` (or wherever C4 emit logic lives — task-time discovery): write new fields when available; mark sidecar `.md` as deprecated (header comment) but keep emitting it through Phase 5 for downstream-consumer grace period. **Sidecar `.md` removal pinned to Task 7.5 (per v0.2 RC-FLAG-5 resolution).**
- Modify: tests pinning the v1.0 shape; add tests for v1.1 fields; add backward-compat round-trip test (v1.0 fixture → v1.1 reader → v1.1 emit → v1.0 reader still succeeds).

**Agent assignment.** Implementation: `AI Engineer`. Backward-compat verify: **2-wave RC + MQ** (per v0.2 RC-FLAG-2 resolution).

**Dependency.** Phase 1 (driver scripts emit the artifacts) and Phase 2 (Path α re-fit so per-TP signs are stable) must be complete.

### Task 4.1 — Schema bump (additive) + emit update
- [ ] **Step 1** — Dispatch `AI Engineer`: add `Optional` per-TP sign-verdict fields to `ZCapPinned` with default `None`; bump `schema_version` `1.0` → `1.1`; update transient Pydantic validator to accept both versions; update emit logic to populate fields from C4 internal state; mark sidecar `.md` deprecated (header comment) with removal target = Task 7.5.
- [ ] **Step 2** — Audit-pass chain on touched files.
- [ ] **Step 3** — Re-emit artifacts via `make emit-cohorts`; verify new fields populate correctly.
- [ ] **Step 4** — Add backward-compat round-trip test: load v1.0 fixture → v1.1 reader → v1.1 emit → v1.0 reader. All four steps must succeed.
- [ ] **Step 5** — Commit: `feat(saas-cohort-4): Z_cap_pinned schema v1.0 → v1.1 (additive, per-TP sign verdicts inline)`.

### Task 4.2 — Backward-compat 2-wave verify
- [ ] **Step 1** — Foreground dispatches `Reality Checker`: load a v1.0 fixture; confirm v1.1 reader accepts (NOT rejects); confirm new fields populate as `None` for v1.0 input; confirm v1.1 emit + v1.0 reader round-trip succeeds; verify sidecar deprecation comment cites Task 7.5 removal.
- [ ] **Step 2** — Foreground dispatches `Model QA Specialist`: confirm math-contract preservation (no per-TP sign value differs between sidecar and inline v1.1 fields for the same artifact); confirm `schema_version` semver convention is honored (additive ⇒ minor bump correct).
- [ ] **Step 3** — On BLOCK: cycle Task 4.1.

---

## Phase 5 — Stage-2 modeling memo (deliverable)

**Trigger.** Stage-2 verdict needs a synthesis document for the supervisor + future Stage-3 readers.

**Files**
- Create: `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md` (date matches plan; `docs/specs/` per repo convention for spec-class memos).

**Agent assignment.** Drafting: `Technical Writer`. Independent verify: 2-wave (`Reality Checker` for empirical claim grounding against shipped artifacts; `Model QA Specialist` for methodology summary fidelity).

**Dependency.** Phases 1, 2, 3, 4 complete. Memo cites concrete artifact field values, so artifacts must be in their Phase-4 final shape.

### Task 5.1 — Author memo
- [ ] **Step 1** — Dispatch `Technical Writer` with brief covering: (a) Stage-2 verdict statement (PASS/FAIL on each cohort + overall); (b) Z_cap real-data magnitude (post-Phase-2 numbers from `Z_cap_pinned.json` v1.1); (c) π(t) closed form + economic interpretation; (d) Chosen Υ_t form from C3 (per spec v1.2) + ELPD diff + SE; (e) **limitations: synthetic-Bayesian only, no LP capital tested, hierarchical pooling deferred to Stage-3, AND `pi` posterior remains structurally near-prior because tier-conditional θ_k is deferred to Stage-3 per spec §5.4 — this does not invalidate the Z_cap sign cert (`pi` contribution is ~1e-10 of q/(X/Y) per RC v0.3)** (per v0.2 MQ-FLAG-3 resolution); (f) cross-cohort dependency map; (g) anti-fishing audit trail (12-BLOCK lesson, 1/κ post-hoc fit case study, **v0.1 Path β rejection case study**).
- [ ] **Step 2** — Memo length target: 1500–3000 words; section headers; cite spec v1.2 + this plan v0.2 + per-cohort plan files.
- [ ] **Step 3** — Commit: `docs(saas-stage-2): Stage-2 modeling memo — verdict + limitations + Stage-3 handoff`.

### Task 5.2 — Independent 2-wave verify (Phase 5)
- [ ] **Step 1** — Foreground dispatches `Reality Checker`: every numeric claim in the memo traces to a concrete artifact field or commit-pinned diagnostic. No hand-wave.
- [ ] **Step 2** — Foreground dispatches `Model QA Specialist`: methodology summary matches spec v1.2 + per-cohort implementations; limitations section is honest about scope (including `pi` near-prior caveat).
- [ ] **Step 3** — On BLOCK: cycle Task 5.1.

---

## Phase 6 — Memory hygiene (foreground, no specialized dispatch)

**Trigger.** Three architectural / methodological lessons from this iteration must be captured before context fades. **v0.2 adds a fourth lesson: the v0.1 Path β rejection itself, which exemplifies the post-hoc-fit pattern the second memo memorializes.**

**Files**
- Create: `memory/feedback_self_grading_vs_independent.md` — 12-BLOCK lesson (self-grading caught 0; independent Reality Checker + Model QA Specialist waves caught all 12 BLOCKs across cohorts). **v0.2 addendum: plan-doc 2-wave verify on v0.1 caught 3 additional BLOCKs (Path β, Phase 0 pre-determination, schema-bump mislabel) — extends the lesson from per-cohort to plan-level.**
- Create: `memory/feedback_post_hoc_fit_anti_fishing_pattern.md` — C4 1/κ post-hoc fit case study + **v0.1 Path β case study** (converting LOW doc flag → 3× free parameters by spec-misreading deferral as hint). Detection heuristic: any methodologically-substantive change introduced "to also resolve" a downstream LOW flag, after data is touched, is silent-fishing. The post-hoc fit memo is now consistent with Phase 2 (which ships Path α, NOT Path β).
- Create: `memory/feedback_worktree_agents_no_subdispatch.md` — architectural finding (worktree agents lack the Agent tool; orchestration must run from main session, not from inside a worktree).
- Modify: rename `memory/project_saas_builder_stage_2_active.md` → `memory/project_saas_builder_stage_2_complete.md`; update body with final verdict + memo path + PR # for record.

**Agent assignment.** Foreground authoring (small, no specialized agents needed per plan brief).

### Task 6.1 — Author 3 feedback memos
- [ ] **Step 1** — Foreground writes `feedback_self_grading_vs_independent.md` with v0.2 addendum.
- [ ] **Step 2** — Foreground writes `feedback_post_hoc_fit_anti_fishing_pattern.md` with both 1/κ and v0.1 Path β case studies.
- [ ] **Step 3** — Foreground writes `feedback_worktree_agents_no_subdispatch.md`.
- [ ] **Step 4** — Commit: `docs(memory): 3 feedback memos from SaaS-builder Stage-2 close`.

### Task 6.2 — Refresh project memory
- [ ] **Step 1** — `git mv memory/project_saas_builder_stage_2_active.md memory/project_saas_builder_stage_2_complete.md`.
- [ ] **Step 2** — Update body: final verdict, memo path, PR #3 link, commit SHA of merge (placeholder `<MERGE_SHA_PHASE_7>` back-filled by Task 7.4 — closed-loop).
- [ ] **Step 3** — Commit: `docs(memory): SaaS-builder Stage-2 → complete`.

---

## Phase 7 — PR #3 finalize

**Trigger.** PR #3 (`iter/saas-builder-stage-2` → `master`) is currently WIP. With Phases 0–6 merged into the iteration branch, the PR is ready for final review.

**Files**
- No new files. PR description update + merge + sidecar removal.

**Agent assignment.** Foreground (per established repo pattern + `feedback_no_merge_without_approval`).

**Dependency.** Phase 6 complete (memos must be on the branch before merge so master sees them in one merge).

### Task 7.1 — Update PR #3 description
- [ ] **Step 1** — `gh pr edit 3 --body "$(...)"` with description summarizing: 4 cohorts shipped, spec v1.2 (NOT v1.3 — Path α requires no spec amendment), modeling memo path, 411+ tests, audit-pass chain green, anti-fishing posture preserved (incl. v0.1 Path β rejection case study), Stage-3 explicitly deferred.
- [ ] **Step 2** — Convert WIP → ready: `gh pr ready 3`.

### Task 7.2 — Final review request
- [ ] **Step 1** — Foreground summarizes the PR diff range to the user; surfaces any remaining open FLAGs explicitly.
- [ ] **Step 2** — User adjudicates: merge / hold / further changes. Per `feedback_no_merge_without_approval`, foreground does NOT merge without explicit user approval.

### Task 7.3 — Merge (only on user approval)
- [ ] **Step 1** — `gh pr merge 3 --merge` (preserve commit history; no squash — audit-trail preservation per repo convention).
- [ ] **Step 2** — Capture merge SHA.

### Task 7.4 — Back-fill `<MERGE_SHA_PHASE_7>` placeholder
- [ ] **Step 1** — Replace placeholder in `project_saas_builder_stage_2_complete.md` with merge SHA from Task 7.3.
- [ ] **Step 2** — Commit on `master`: `docs(memory): back-fill Stage-2 merge SHA`.

### Task 7.5 — Sidecar `Z_cap_pinned.SIGN_VERDICTS.md` removal (per v0.2 RC-FLAG-5)
- [ ] **Step 1** — Remove sidecar emission from `scripts/run_cohort4_emit.py` (and any helper modules); the deprecation grace period ends here.
- [ ] **Step 2** — Verify v1.1 schema reader fully covers downstream consumers.
- [ ] **Step 3** — Commit on `master`: `chore(saas-cohort-4): remove deprecated Z_cap_pinned.SIGN_VERDICTS.md sidecar (superseded by schema v1.1)`.
- [ ] **Step 4** — Delete branch `iter/saas-builder-stage-2` locally and on origin (only after user confirms merge + sidecar removal are good).

---

## Verification matrix (per SIM-INFRA-0 v1.1 format precedent — v0.2 RC-FLAG-3 resolution)

| Phase | Task | Verify wave | Evidence location |
|---|---|---|---|
| P0 | 0.3 | RC + MQ 2-wave | `scratch/2026-05-09-saas-cohort-close/phase0-spec-amendment-rationale.md` + spec v1.2 CHANGELOG |
| P1 | 1.1, 1.2, 1.3 (Step 5) | RC light-pass | commit-message hash-equality + RC review note in PR thread |
| P2 | 2.3 | RC + MQ 2-wave | C4 MC stderr/Ẑ diagnostic + 5-TP sign cert artifact |
| P3 | 3.1–3.4 | Audit-pass chain (per file) | mutmut report + ruff/ty clean |
| P4 | 4.2 | RC + MQ 2-wave | round-trip test in `simulations/tests/saas_builder/test_z_cap_pinned_schema_compat.py` |
| P5 | 5.2 | RC + MQ 2-wave | memo + cited artifact field values |
| P6 | — | Foreground self-review | `memory/feedback_*.md` + project memory rename diff |
| P7 | 7.2 | User adjudication | PR #3 review thread |

---

## §15 CORRECTIONS-α (this plan)

### v0.1 → v0.2 (2026-05-08) — RC + MQ 2-wave plan-doc verify cycle 1

**Verdict cycle.** RC verdict: ACCEPT_WITH_FLAGS (5 LOW FLAGs). MQ verdict: REJECT (3 BLOCKs + 5 FLAGs). Composite: REJECT — must remediate before Phase 0 dispatch.

**Format precedent.** Mirrors spec v1.1.1 §15 + SIM-INFRA-0 plan §"CORRECTIONS-α".

#### MQ BLOCK-1 (HIGH) — Phase 2 anti-fishing-suspect Path β → resolved by Path α swap
- **Verdict citation.** MQ verdict ll. 18–31 (`scratch/2026-05-09-cohort-close-plan-review/mq-verdict.md`). Three independent residual-evidence findings: (a) spec §5.4 (ll. 363–375) is "Realism overrides" (bracket coverage, ρ=0, bank-spread, scope) — NOT a per-tier θ_k hint; C1 MQ-v0.4 reads §5.4 as DEFERRING per-tier (l. 12), and the v0.1 plan inverts deferral into a hint; (b) C1 MQ-FLAG-1 prescribed a one-line caveat (LOW severity), not re-parameterization; (c) C4 RC v0.3 ll. 55–56 explicitly endorsed Path α ("HALT-WEAK + N-bump").
- **Fix location.** Phase 2 fully rewritten (ll. ~Phase-2 header through Task 2.3). Spec amendment v1.2 → v1.3 removed entirely. Path β demoted to Stage-3 unconditionally in plan header Out-of-scope. Task 2.2 now specifies brute N_draws ≈ 7.1e5 re-fit, no model surgery. C1 MQ-FLAG-1 routes to Phase 3 Task 3.1 as a one-line caveat in C1 plan v0.4.
- **Anti-fishing meta-lesson.** v0.1 Path β was itself a post-hoc retro-fit — converting a LOW doc flag into a methodologically-substantive 3×-free-parameter re-parameterization to "also resolve" downstream problems. The plan-author should have HALTed at C1 MQ-FLAG-1's "one-line caveat" wording rather than spec-misread §5.4. This v0.2 correction is a case study for `feedback_post_hoc_fit_anti_fishing_pattern.md` (Phase 6, Task 6.1 Step 2).

#### MQ BLOCK-2 (HIGH) — Phase 0 order-of-operations pre-determination → resolved by Task 0.1/0.2 decoupling + Task 0.2b
- **Verdict citation.** MQ verdict ll. 33–42. v0.1 Task 0.2 pinned $S_t$ = deterministic factor "matches existing C3 implementation" BEFORE Task 0.1 lit survey runs; this ratifies rather than adjudicates. C3 PSIS-LOO-CV verdict was computed under one $S_t$ form; if survey concludes a different form is methodologically correct, ELPD comparison must be redone — not silently ratified.
- **Fix location.** Task 0.1 brief rewritten to forbid implementation-anchoring; recommendation must be defensible from first principles. Task 0.2 amends spec to whatever Task 0.1 recommends, NOT to match C3. New Task 0.2b adds HALT-routed C3 re-fit + ELPD recompute conditional on Task 0.1 ≠ deterministic-factor recommendation. Task 0.3 verify wave updated to check the no-op vs. re-fit branch.

#### MQ BLOCK-3 (MEDIUM) — Phase 4 schema bump mislabel → resolved by truly additive semantics
- **Verdict citation.** MQ verdict ll. 44–49. v0.1 declared additive but chose "reject-on-old-version" behavior; additive ⇒ v1.1 reader is a superset of v1.0 reader (must accept v1.0).
- **Fix location.** Phase 4 header rewritten with explicit additive semantics. New per-TP fields are `Optional[…]` with default `None`; transient Pydantic validator accepts both `schema_version` values; round-trip test (v1.0 fixture → v1.1 reader → v1.1 emit → v1.0 reader) added in Task 4.1 Step 4. Sidecar `.md` removal pinned to Task 7.5 (closes RC-FLAG-5).

#### RC FLAG-1 (LOW, format) — Strategic delegation map missing → added
- **Fix location.** New "Strategic delegation map" 7-row table inserted after plan header, before phase dependency graph. Mirrors SIM-INFRA-0 v1.1.

#### RC FLAG-2 (LOW, verify-coverage) — Phase 4 RC-only → upgraded to RC + MQ
- **Fix location.** Task 4.2 retitled "Backward-compat 2-wave verify"; MQ wave added (Step 2) covering math-contract preservation + semver-additive convention check.

#### RC FLAG-3 (LOW, format) — Verification matrix missing → added
- **Fix location.** New "Verification matrix" table inserted between Phase 7 and §15. Cross-references each verify wave to evidence location.

#### RC FLAG-4 (LOW, plan-version semantics) — Conditional bump rule ambiguous → pinned deterministic
- **Fix location.** Task 2.1 Step 2 rewritten: plan version bumps exactly once per RC+MQ 2-wave plan-doc verify cycle that returns BLOCKs. v0.1 → v0.2 (current). No conditional branch.

#### RC FLAG-5 (LOW, sidecar lifecycle) — Sidecar deprecation has no removal commit → pinned to Task 7.5
- **Fix location.** New Task 7.5 in Phase 7. Sidecar `.md` removal commit on `master` after merge + user confirmation. Phase 4 deprecation comment cites Task 7.5 explicitly.

#### MQ FLAG-1 (LOW, Phase 1 risk) — Self-review item 7 understates → RC light-pass added
- **Fix location.** Strategic delegation map Phase 1 row + Tasks 1.1, 1.2, 1.3 each gain a Step 5 (RC light-pass for seed-pinning + run-determinism). Self-review item 7 below revised.

#### MQ FLAG-2 (LOW, Phase 1 HALT trigger missing) → added to Task 1.3
- **Fix location.** Task 1.3 Step 3 gains explicit HALT trigger: if 5-TP sign cert FAILs on real-C1 re-build (e.g., due to Phase-3 nit affecting `tier_idx` builder slot-0), HALT + CORRECTIONS-α + user-adjudicated pivot.

#### MQ FLAG-3 (LOW, memo limitations) — Per-tier θ_k caveat under Path α → memo brief expanded
- **Fix location.** Task 5.1 Step 1 limitations clause (e) expanded: "`pi` posterior remains structurally near-prior because tier-conditional θ_k is deferred to Stage-3 per spec §5.4; this does not invalidate the Z_cap sign cert (`pi` contribution is ~1e-10 of q/(X/Y) per RC v0.3)."

#### MQ FLAG-4 (LOW, Phase 6 wording risk) — Path β contradiction → eliminated by BLOCK-1 fix
- **Fix location.** Phase 2 ships Path α; the post-hoc-fit memo (Task 6.1 Step 2) is now consistent with the plan's own actions. Memo content expanded to include v0.1 Path β rejection as a case study.

#### MQ FLAG-5 (INFO, Task 2.4 commit-message drift) — `data:` mislabel → corrected
- **Fix location.** Task 2.2 (the new Path α equivalent of v0.1's Task 2.4) commit message: `chore(saas-cohort-1): re-emit Stage-2 artifacts with N_draws=7.1e5 (MC budget Path α)` — `chore(saas-cohort-1)` not `data:`.

---

## Self-review checklist (per `superpowers:writing-plans`)

**1. Spec coverage of the 9 leftover items.**
- Item 1 (spec v1.2 amendment) → Phase 0. ✓
- Item 2 (C4 MC budget) → Phase 2 Path α. ✓
- Item 3 (Z_cap_pinned schema bump, additive) → Phase 4. ✓
- Item 4 (C1 cosmetic residuals + MQ-FLAG-1 caveat) → Task 3.1. ✓
- Item 5 (C2/C3/C4 nit cleanup) → Tasks 3.2, 3.3, 3.4. ✓
- Item 6 (real-artifact emission for C2/C3/C4) → Phase 1. ✓
- Item 7 (Stage-2 modeling memo) → Phase 5. ✓
- Item 8 (memory hygiene) → Phase 6. ✓
- Item 9 (PR #3 finalize + sidecar removal) → Phase 7 (incl. Task 7.5). ✓

**2. Placeholder scan.**
- One intentional placeholder (`<MERGE_SHA_PHASE_7>` in Task 6.2) is closed-loop within Task 7.4. Allowed.
- No "TBD", "TODO", "fill in later" elsewhere. ✓
- No "add appropriate error handling" / "handle edge cases" — all tasks pin specific errors (e.g., `MCErrorBudgetExceededError`, `Cohort4Error`). ✓

**3. Type / name consistency.**
- `ZCapPinned` schema name + `schema_version` Final constant + `Z_cap_pinned.json` file name consistent across Phases 1, 2, 4, 5. ✓
- `revenue_form_verdict.json` consistent across Phases 1, 5. ✓
- `gate_verdict.json` consistent across Phases 1, 5. ✓
- Cohort numbering (C1/C2/C3/C4) consistent throughout. ✓
- Spec version chain v1.1.1 → v1.2 (Phase 0). **No v1.3 amendment under v0.2** (Path α requires none). ✓
- `make emit-cohorts` Makefile target referenced consistently in Phases 1, 2, 4. ✓

**4. Anti-fishing posture.**
- N_MIN / POWER_MIN / MDES_SD pinned in plan header. ✓
- HALT triggers explicit at Tasks 0.3, 0.2b, 1.3 (per MQ-FLAG-2), 2.3, 3.x (via audit-pass chain), 4.2, 5.2. ✓
- 1/κ post-hoc fit + v0.1 Path β rejection captured as Phase 6 case studies. ✓

**5. Out-of-scope guards.**
- Stage-3 items enumerated in plan header (incl. per-tier θ_k unconditionally). ✓
- Path β (per-tier θ_k re-parameterization) explicitly demoted in plan header + §15 BLOCK-1. ✓
- Hierarchical pooling for C3 / on-chain Panoptic / real-data conditioning all deferred. ✓

**6. Audit-pass chain coverage.**
- Every code-touching task (1.1, 1.2, 1.3, 2.2, 3.1, 3.2, 3.3, 3.4, 4.1) explicitly invokes the chain. ✓

**7. Independent verify coverage.**
- Phase 0 (spec v1.2): RC + MQ. ✓
- Phase 1 (driver scripts): RC light-pass per task (per MQ-FLAG-1). ✓
- Phase 2 (Path α re-fit): RC + MQ. ✓
- Phase 4 (schema bump, additive): **RC + MQ** (per RC-FLAG-2 resolution). ✓
- Phase 5 (memo): RC + MQ. ✓
- Phase 3, 6, 7: foreground review sufficient (mechanical work or process). ✓

Plan v0.2 is ready for re-cycle 2-wave doc verify (RC + MQ) before Phase 0 dispatch.
