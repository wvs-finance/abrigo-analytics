# Code Reviewer — D1.D + D4 Joint Implementation Plan v0.1 Review

**Reviewer:** Code Reviewer (methodology + structure rigor lens)
**Plan:** `docs/plans/2026-05-18-d1d-d4-joint-implementation.md` v0.1
**Spec:** `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2
**Date:** 2026-05-18

---

## Verdict

**REQUEST-CHANGES.** Plan v0.1 is structurally coherent and faithfully translates spec v0.2's §9 scaffold into a 7-phase sequence with named agents, but it has **3 Critical methodology defects** that violate non-negotiable feedback rules (strict TDD ordering, real-data-over-mocks, single-specialist-per-task) and **5 Strong defects** that compromise Tier 3 reproducibility, HALT-trigger test coverage, and post-hoc Delphi sequencing. The defects are addressable inline without re-architecting the plan; no CORRECTIONS-C block needed — a v0.2 plan-revision should suffice.

The plan does NOT violate `feedback_no_code_in_specs_or_plans.md` at the task level (no function signatures, no Python syntax, no executable snippets). It does inherit spec §9's pre-committed file-path scaffold, which is a spec-level decision the plan correctly mirrors without elaboration — acceptable.

---

## Critical (MUST fix before plan v0.2 lock)

### C1 — TDD ordering violated for Phase 2 modules (2.1, 2.3, 2.4, 2.5)

`feedback_strict_tdd.md` is NON-NEGOTIABLE: *"never write implementation code for any feature unless the test for that specific feature has been written FIRST and verified to FAIL"*. Plan v0.1 only stages a failing-test task for Phase 2.2 (stationarity gate, via Phase 0.4) and Phase 0.3 (types tier, via Hypothesis strategies). For all other Phase 2 modules, the test-writing step is collapsed into the implementation task itself ("unit tests + Hypothesis strategies pass" is listed as deliverable, not as a separate prior task).

Specifically missing pre-implementation failing-test tasks for:

- **2.1** inflow_aggregator, colombia_scalar, off_ramp_decomp — no Phase 0.x test harness analogous to 0.4
- **2.3** gpd_pot — no failing-test task before implementation (Phase 0 only covers stationarity gate)
- **2.4** rho_compute (HALT triggers especially) — no failing-test task
- **2.5** panel_io parquet round-trip — no failing-test task

**Fix:** Add Phase 0.5-0.8 failing-test harness tasks mirroring 0.4's pattern, each producing red tests that Phase 2.x then turns green. Predecessor plan dev_ai_cost_v2 did this via per-feature red→green cycles; v0.1 here regresses from that pattern.

### C2 — Phase 1.1 "fixture Dune response" is a mock when real cached data is the discipline

`feedback_real_data_over_mocks.md` priority order: (1) real data, (2) recorded snapshots, (3) mocks only for HTTP errors. Plan v0.1 Phase 1.1 says *"tests against fixture Dune response"* — ambiguous. If "fixture" means a hand-authored sample, that violates the rule. If it means a frozen real snapshot from `data/raw/onchain/snapshots/`, that's correct (priority 2).

Compounding: spec §13 (CORRECTIONS-B Tier 2 frozen-snapshot requirement) explicitly mandates committed parquet snapshots — so the snapshot machinery exists. Phase 1.1 must reference it.

**Fix:** Reword 1.1 to *"tests against frozen real Dune snapshot at `data/raw/onchain/snapshots/2026-05-18_*.parquet`; mocks PERMITTED ONLY for HTTP 429 / timeout error paths per `feedback_real_data_over_mocks.md` clause 2"*. Apply same wording discipline to 1.2 (cryptocompare_io), 1.4 (mento_io).

### C3 — Dual-agent dispatch in 0.3, 2.1, 7.2 violates single-specialist-per-task

`feedback_specialized_agents_per_task.md`: *"before every plan task, identify the specialist"* (singular). Plan v0.1 has at least 3 tasks with concatenated agents:

- **0.3**: "Data Engineer + functional-python"
- **2.1**: "Senior Developer + Data Engineer" (compounded with the C1 batching problem)
- **7.2**: "CR + RC parallel"

7.2 parallel review is fine because CR and RC are independent reviewers reviewing the same artifact — that's the established 2-way review pattern. But 0.3 and 2.1 are *authorship* tasks. Dual-authorship creates ambiguity about which agent's domain posture binds, breaks the audit-trail rationale ("specialized agents bring domain posture ... critical distance the foreground session cannot easily self-impose"), and is the exact anti-pattern the feedback file targets.

**Fix:**
- 0.3 → single agent (Data Engineer, with `functional-python` skill *invoked by* that agent — skills are tools, not co-authors)
- 2.1 → split into 2.1a (inflow_aggregator, Data Engineer), 2.1b (colombia_scalar, Senior Developer), 2.1c (off_ramp_decomp, Senior Developer) — solves both C1 batching and C3 dual-dispatch
- 7.2 → keep parallel but rename to "CR review || RC review" to disambiguate from dual-authorship

---

## Strong (SHOULD fix)

### S1 — Phase 7.1 Delphi audit ordering inverted vs predecessor pattern

dev_ai_cost_v2 v0.2.10 ran Delphi audit-econ as **post-hoc** quality control on a closed verdict. Plan v0.1 has 7.1 Delphi *before* 7.2 impl-review and *after* 6.2 verdict consolidation. This is the correct order for *audit-grade* Delphi (verdict → audit → impl-review → merge) and matches the predecessor pattern when read carefully.

However, Phase 6.2 writes the verdict memo + LaTeX scaffold *before* Delphi audit. If Delphi finds Critical defects, the memo + LaTeX must be re-authored — wasted Technical Writer cycles. Predecessor pattern dispatched Delphi *after verdict notebook 06 but BEFORE memo authorship*.

**Fix:** Reorder Phase 6/7:
1. 6.1 verdict notebook 06
2. 7.1 Delphi audit (3 Opus auditors on verdict notebook + panel-builder + locked notebooks)
3. CORRECTIONS-C cascade if Critical findings emerge
4. 6.2 verdict memo + LaTeX (post-Delphi, integrating findings)
5. 7.2 impl-review (CR + RC)
6. 7.3 commit + PR

This avoids re-authoring memo + LaTeX after Delphi.

### S2 — Tier 3 round-trip procedure underspecified in Phase 2.6

CLAUDE.md three-tier discipline: *"Tier 3 panel-builder re-derives Tier 1 from Tier 2"*. Plan 2.6 says *"CLI panel-builder at `scripts/build_d1d_d4_joint_panel.py` — Tier 3 round-trip implementation"* — but no acceptance criterion specifies what "round-trip" means:

- Bit-identical parquet? (impossible — pandas timestamps + parquet metadata drift)
- Schema-identical + value-equal-within-tolerance? (what tolerance?)
- `make verify` target as in Makefile? (referenced in CLAUDE.md but not in this plan)

Without a deterministic re-derivation procedure + acceptance test, Tier 3 is undefined and `make verify` in Phase 6 will have ambiguous semantics.

**Fix:** Add to 2.6 deliverable: *"Tier 3 acceptance criterion: `make verify` passes, where verify = schema-identical + numeric-equal within 1e-9 absolute tolerance + row-count-identical against published Tier 1 parquet. Define `make verify` target in Makefile."* Add Phase 2.6.1 test task (failing test) before 2.6 implementation per C1.

### S3 — HALT-trigger test coverage in Phase 2.4 is structural, not behavioral

Spec §4.3 defines 3 HALT triggers for ρ_compute: |ρ̂|>1.5, denominator floor $10M, residual<−0.10. Plan 2.4 says *"HALT trigger tests (|ρ̂|>1.5 and denom-floor) pass"* — note the residual<−0.10 trigger is OMITTED from the deliverable. Also, "tests pass" doesn't specify whether HALT triggers raise typed exceptions (`StationarityGateError`/`DepegEventInsufficientError` are declared in 0.1, but no `RhoHaltError` is mentioned).

Compounding: HALT triggers must also fire in notebooks (Phase 3-5 trio HALT checkpoints), but plan never specifies whether HALT-trigger enforcement is (a) raise-and-halt in module + caught by notebook, or (b) check-and-warn in module + notebook authors halt. Predecessor dev_ai_cost_v2 §11.X pattern was (a).

**Fix:** Phase 0.1 add `RhoHaltError`, `ResidualSignError` to `_errors.py`. Phase 0.7 (new per C1) add failing-test harness for all 3 HALT triggers including residual<−0.10 with typed-exception assertions. Phase 2.4 deliverable lists all 3 trigger tests green.

### S4 — Notebook trio HALT enforcement mechanism unspecified

Phases 3-6 reference *"Trio human review (mandatory)"* as the review checkpoint, dispatched to Analytics Reporter. But trio discipline per `feedback_notebook_trio_checkpoint.md` is a *human review* gate, not an agent gate — Analytics Reporter authors the trio; a *human* halts at each interpretation-markdown for review. Plan v0.1 conflates these.

Without a programmatic check, "trio HALT" depends on Analytics Reporter remembering to pause. dev_ai_cost_v2 pattern used a notebook-runner script that halts at each trio boundary and waits for user input.

**Fix:** Either (a) add Phase 0.5 task to author trio-checkpoint runner script that pauses at each interpretation cell, OR (b) explicitly add to Phase 3-6 task wording *"Analytics Reporter authors trio; runs `nbconvert --execute` and STOPS at each interpretation block for foreground orchestrator to surface to user per `feedback_notebook_trio_checkpoint.md` clause 3"*. Option (b) is lighter-weight; pick one.

### S5 — Phase 2.1 batches 3 modules into 1 task — violates atomicity + TDD

Phase 2.1 implements `inflow_aggregator`, `colombia_scalar`, AND `off_ramp_decomp` in a single task. Three modules ≠ one ≤1-day task. This batching also violates strict TDD (C1): a single failing-test→passing-test cycle cannot cover 3 independent module behaviors.

**Fix:** Split per C3 fix (2.1a/2.1b/2.1c). Each ≤4 hours including failing-test → minimal implementation → green.

---

## Nits

### N1 — Pre-pin verification harness mentioned in Phase 0 goal, never instantiated

Phase 0 goal says *"pre-pin verification harness BEFORE any external data pull"*. No Phase 0.x task produces this artifact. Either it's implicit in 0.3+0.4 (then say so), or it's a missing task. Predecessor plan dev_ai_cost_v2 had explicit Task 0.x "pre-pin compliance check".

**Fix:** Add Phase 0.5 *"Pre-pin compliance check: scan spec §4 against `notebooks/d1d_d4_joint/PRE_PIN.md` machine-readable extract; fail if any pre-pin field is missing from spec"*. Specialist: Reality Checker.

### N2 — Phase 1.5 cross-check anchor count not justified

Plan asks for *"≥ 3 anchor agreements at order-of-magnitude"*. Why 3? Spec doesn't specify. If the plan introduces a new threshold not in the spec, that's a CORRECTIONS-C trigger. Lower bar: cite the threshold as inherited from a prior iteration's RC pattern, or escalate to user.

### N3 — Phase 2.7 review checkpoint inserts a new gate not in spec §10's 3-week plan

Spec §10 Week 2 ends with "Tier 3 panel-builder implementation"; plan inserts 2.7 *"Pre-pin compliance review of panel-builder output"* as a 2-way (CR+RC) gate before Phase 3 notebooks. This is a good gate — but it's not in the spec. Either amend spec §10 to include it, or acknowledge the plan adds a non-spec gate (which is acceptable — implementation plans routinely add review gates the spec doesn't anticipate).

### N4 — Wall-clock 9 days vs spec §10 3-weeks discrepancy under-explained

Plan §"Estimated wall-clock" claims 9 days against spec §10's 3 weeks (~15 working days) and says *"review iterations consume the buffer"*. That's 6 days of review buffer = 67% of execution time on review. Either the 9-day estimate is too aggressive (likely — Phase 7.1 Delphi typically takes 1-2 days alone), or the buffer rationale is wrong. Recommend re-estimating Phase 7 (Delphi + 2 days) and Phase 3+4 parallel (which assumes notebook authoring parallelism — historically notebooks bottleneck on review, not authoring).

### N5 — Open item #4 (10 sensitivity arms) is a spec-level question, not a plan question

Plan §"Open items for reviewer attention" #4 asks whether 10 sensitivity arms is too many. This is a spec §3.1 / §4.3 question, not a plan question. Drop from plan open items; if reviewer wants to raise it, that's spec-level CORRECTIONS-C, not plan v0.2 amendment.

### N6 — Phase 0.1 import-discipline test is named but never specified

Plan says *"import-discipline test failing → passing"* in 0.1 deliverable. What does that test do? Likely: AST-walk the package and assert no `from simulations.d1d_d4_joint.modules import *` in types/, no `from ...utils import *` in modules/. Specify the assertion.

---

## Plan-completeness audit (per-phase)

### Phase 0 — Pre-data scaffold

**Coverage:** 4 tasks. Scaffold + disposition template + types tier + stationarity-gate test harness.

**Gaps:**
- (C1) Failing-test harnesses missing for gpd_pot, rho_compute (incl 3 HALT triggers), inflow_aggregator, off_ramp_decomp, panel_io
- (N1) Pre-pin verification harness mentioned in goal but no task
- (N6) Import-discipline test under-specified

**Strength:** 0.3 + 0.4 correctly enforce TDD for types tier + stationarity gate.

### Phase 1 — Data ingest

**Coverage:** 5 tasks. dune_io, cryptocompare_io, banrep extension, mento_io, RC verification.

**Gaps:**
- (C2) "fixture Dune response" wording risks mock-violation
- (N2) Phase 1.5 ≥3-anchor threshold unjustified

**Strength:** 1.5 RC sign-off is the right discipline. Reuse of D4.2 cryptocompare scripts in 1.2 is good incremental work.

### Phase 2 — Panel build

**Coverage:** 7 tasks. Modules (3-in-1), stationarity, GPD, rho, panel_io, builder CLI, review checkpoint.

**Gaps:**
- (C1) Tests precede implementation for stationarity gate only (0.4 → 2.2); missing for 2.1, 2.3, 2.4, 2.5
- (S2) Tier 3 round-trip acceptance criterion undefined
- (S3) HALT trigger #3 (residual<−0.10) missing from 2.4 deliverable
- (S5) 2.1 batches 3 modules
- (N3) 2.7 gate not in spec §10 (acceptable but flag)

**Strength:** 2.7 inserts CR+RC review before notebook phase — correct discipline.

### Phase 3 — D1.D side notebook

**Coverage:** 2 tasks. EDA + inflow β.

**Gaps:**
- (S4) Trio HALT enforcement mechanism unspecified (Analytics Reporter dispatch alone insufficient)

**Strength:** 3.2 explicitly includes data-quality disclosure block per D1 transparency condition.

### Phase 4 — D4.1 side notebook

**Coverage:** 1 task. 3-arm GPD POT fit notebook.

**Gaps:**
- Only 1 task — is this large enough to merit a phase? Could merge into Phase 3. (Minor — separation aids parallel dispatch, so keep.)
- (S4) Same trio HALT mechanism gap

**Strength:** Explicit CORRECTIONS-A posterior update — good spec faithfulness.

### Phase 5 — Joint analysis

**Coverage:** 2 tasks. Joint ρ + sensitivity notebook.

**Gaps:**
- (S4) Same trio HALT mechanism gap
- Phase 5.2 says "Layer C composite-vs-wage placebo arm" — but spec §1 explicitly defers Layer C attribution to Phase 2 (downstream iteration). Is the placebo arm here a Layer C *probe* or actual Layer C attribution? If the latter, scope creep.

**Strength:** 5.1 correctly labels regime conditionals "non-inferential" per spec §3.1.

### Phase 6 — Verdict + write-up

**Coverage:** 2 tasks. Verdict notebook + memo + LaTeX scaffold.

**Gaps:**
- (S1) Memo authored BEFORE Delphi audit — if Delphi finds Critical, memo rewrites

**Strength:** Verdict notebook is its own task with trio review — correct.

### Phase 7 — Post-hoc 3-way review

**Coverage:** 3 tasks. Delphi + impl-review + PR.

**Gaps:**
- (S1) Order should be Delphi → memo → impl-review, not memo → Delphi → impl-review
- (C3) 7.2 dual-agent wording ("CR + RC parallel") — fine for review, clarify wording

**Strength:** Delphi-then-impl-review-then-PR is the right pattern at the top level.

---

## Summary of required edits for plan v0.2

1. (C1) Add Phase 0.5-0.8 failing-test harness tasks for inflow_aggregator/colombia_scalar/off_ramp_decomp, gpd_pot, rho_compute (3 HALT triggers), panel_io
2. (C2) Reword Phases 1.1/1.2/1.4 to specify frozen-snapshot fixtures, not mocks
3. (C3) Split Phase 2.1 → 2.1a/2.1b/2.1c (single specialist each); collapse 0.3 dual-agent to single
4. (S1) Reorder Phase 6/7: 6.1 → 7.1 Delphi → 6.2 memo → 7.2 impl-review → 7.3 PR
5. (S2) Define Tier 3 acceptance criterion + add `make verify` to Makefile + Phase 2.6.1 failing test
6. (S3) Add residual<−0.10 HALT trigger test + typed exceptions to Phase 0.1 errors module
7. (S4) Specify trio HALT enforcement mechanism (script or per-task wording)
8. (S5) Resolved by C3 split
9. (N1) Add Phase 0.5 pre-pin compliance check task
10. (N2) Justify or relax Phase 1.5 ≥3-anchor threshold
11. (N3) Acknowledge Phase 2.7 as plan-level gate (not spec-level)
12. (N4) Revise wall-clock or buffer rationale
13. (N5) Move open-item #4 to spec-level CORRECTIONS-C if reviewer wants to raise it
14. (N6) Specify import-discipline test assertion

**No CORRECTIONS-C needed.** All defects are plan-level (not spec-level); plan v0.2 revision is the right vehicle.

---

## What's good (call out)

- Spec §9 sub-package scaffold faithfully mirrored — types/modules/utils/tests/ tier discipline respected
- Phase 2.7 review gate inserted at the right boundary (panel-builder → notebooks)
- Anti-fishing tripwires section is comprehensive and matches spec §3 + §3.1
- D1 transparency block requirement propagated to every notebook task (Phase 3.1)
- Open items section is honest and surfaces real uncertainties, not theater
- Phase 0 correctly does scaffold + TDD foundation BEFORE any data pull
- Predecessor-pattern citation (`docs/plans/2026-05-04-dev-ai-stage-1-simple-beta-implementation.md`) is correct and the pattern is well-followed at the macro level

The plan is close to lock — the 3 Critical defects are mechanical to fix and the Strong defects are clarifications. v0.2 revision should be ≤2 hours of editing.

CR review closes here.
