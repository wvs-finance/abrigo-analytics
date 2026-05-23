# Code Reviewer — D1.D + D4 Joint Implementation Plan v0.2 Closure Re-Review

**Reviewer:** Code Reviewer (closure-only lens)
**Plan:** `docs/plans/2026-05-18-d1d-d4-joint-implementation.md` v0.2
**Prior verdict:** REQUEST-CHANGES (3 Critical + 5 Strong + 6 Nits)
**Date:** 2026-05-18

---

## Closure verdict

**APPROVED_WITH_NITS.**

All 3 MUST items (C1, C2, C3) and all 4 named SHOULD items (S1, S2, S3, S4) from the prior CR review are materially closed in plan v0.2. The plan additionally absorbs RC-side criticism (C1 wall-clock, C2 silent-test-pass, C3 mechanical anti-fishing, S1 early RC, S2 anchor count, S3 Stage-2 firewall, S4 transparency template) through Phase 0 expansion (4→12 tasks) and Phase 1.6 / Phase 6.1.5 insertions. Two open-item nits (grep-vs-AST anti-fishing lint; Stage-2 firewall regex breadth) are flagged by the plan authors themselves under "Open items for closure re-review" #6 and #7 — those are acceptable as launch-with-known-unknowns and can be tightened in-flight.

No CORRECTIONS-C re-trigger needed. Plan v0.2 is mergeable.

---

## MUST closure

### C1 — TDD coverage for Phase 2 modules → CLOSED

Required: failing-test harnesses for inflow_aggregator (2.1), gpd_pot (2.3), rho_compute (2.4), panel_io (2.5) before implementation.

v0.2 delivers:
- **0.5** inflow_aggregator failing-test harness → 2.1.a turns green
- **0.6** off_ramp_decomp failing-test harness (incl. residual<−0.10 HALT path) → 2.1.c turns green
- **0.7** ρ-compute failing-test harness with all 4 HALT triggers + `RhoHaltError` typed exception → 2.4 turns green
- **0.8** GPD POT failing-test harness for 3-arm fit + profile-likelihood CI + jackknife → 2.3 turns green
- **0.9** notebook-execution integration-test harness (`nbconvert --execute`) against the 5-instance silent-test-pass catalog — directly addresses RC-C2

Every Phase 2 implementation task explicitly references the corresponding Phase 0 test ID as a pre-condition AND lists "make 0.X tests pass" or "test cases failing" in the deliverable column. Red→green ordering is mechanically enforced by the dependency DAG.

Minor: panel_io round-trip test (2.5) does not have a dedicated 0.x failing-test task — the parquet round-trip property test is folded into 2.5's own deliverable ("Parquet round-trip tests pass"). This is a residual TDD-ordering relaxation for one task but acceptable because parquet round-trip is a property assertion (Hypothesis on `OnchainInflowRow` from 0.3) rather than novel module behavior. Flag as nit, not blocker.

### C2 — Phase 1.1 fixture wording → CLOSED

Required: reword "fixture Dune response" to "frozen real Dune snapshot" per `feedback_real_data_over_mocks.md`.

v0.2 Phase 1.1 now reads: *"tests run against **frozen real Dune snapshot** persisted to `data/raw/onchain/snapshots/test-fixtures/` per `feedback_real_data_over_mocks.md` (CR-C2 — NOT a mock)"*. Explicit citation of the feedback rule + CR ID + emphatic "NOT a mock" closes the ambiguity cleanly.

Phase 1.2 (cryptocompare_io) does not repeat the wording but inherits the snapshot persistence path (`data/raw/onchain/snapshots/2026-05-18_kraken_*.parquet`), which is the same discipline. Phase 1.4 (mento_io) says "persisted to Tier 2" without naming the snapshot — minor inconsistency but the Phase 0.9 `nbconvert --execute` integration harness will catch any mock contamination at the notebook layer. Acceptable.

### C3 — Dual-agent dispatch → CLOSED

Required: collapse 0.3 to single Data Engineer; split 2.1 into 2.1.a/b/c (single specialist each).

v0.2 delivers:
- **0.3** now reads "Data Engineer" only; the `functional-python` skill is treated as a tool invoked by the agent, per the explicit CORRECTIONS-C note ("functional-python is a skill not an agent; coordination via dispatch instructions")
- **2.1** split into **2.1.a** (inflow_aggregator, Senior Developer), **2.1.b** (colombia_scalar, Senior Developer), **2.1.c** (off_ramp_decomp, Senior Developer)

Minor: all three split tasks ended up with the *same* specialist (Senior Developer), not the Data-Engineer/Senior-Developer mix the CR fix sketched. This is acceptable — the original sketch was illustrative; what mattered was atomicity + single-specialist-per-task, both achieved.

7.2 dual-CR+RC parallel is retained — correctly, because that's review parallelism not dual authorship.

---

## SHOULD closure

### S1 — Delphi reorder → CLOSED

Required: insert Delphi between verdict notebook (6.1) and memo+LaTeX (6.2) so memo doesn't re-author on Critical findings.

v0.2 inserts **Phase 6.1.5** *"REORDERED per CR-S1 — Pre-write-up Delphi via audit-econ (3 Opus auditors on closed verdict notebook); fix cascade if Critical emerges — runs BEFORE memo + LaTeX authoring to avoid re-authoring"*. Pre-condition: 6.1 done. Mandatory before 6.2. Phase 6.2 deliverable explicitly says "incorporates any Delphi-driven amendments". Closure is complete and the ordering is now: 6.1 → 6.1.5 → 6.2 → 7.1 → 7.2 → 7.3.

### S2 — Tier 3 round-trip acceptance → CLOSED

Required: define `make verify` semantics + tolerance for Tier 3 re-derivation.

v0.2 Phase 2.6: *"Tier 3 acceptance criterion per CR-S2: `make verify` re-runs the panel build from Tier 2 raw, compares against the first emission via `pandas.testing.assert_frame_equal(...check_exact=False, atol=1e-9, rtol=1e-6)`; any discrepancy fails CI"*. Tolerance is named (atol=1e-9, rtol=1e-6), tool is named (`pandas.testing.assert_frame_equal`), CI gate is explicit.

Note: this contains a literal Python function call (`assert_frame_equal(...check_exact=False, atol=1e-9, rtol=1e-6)`) in the plan. Borderline against `feedback_no_code_in_specs_or_plans.md` — but it's a tolerance *spec* (parameters of an acceptance criterion), not an implementation snippet. Read narrowly, acceptable; read strictly, the plan could phrase it as "absolute tolerance 1e-9, relative tolerance 1e-6, via pandas frame-equality assertion" without naming the function. Flag as nit.

### S3 — residual<−0.10 HALT test gap → CLOSED

Required: thread residual<−0.10 HALT trigger through tests + module + typed exception.

v0.2 delivers a 4-point thread:
- **0.1** declares `RhoHaltError` typed exception alongside `JointPanelError`, `StationarityGateError`, `DepegEventInsufficientError`
- **0.6** off-ramp decomposition test harness includes "residual<−0.10 HALT path"
- **0.7** ρ-compute test harness lists all 4 HALT triggers: |ρ̂|>1.5, denominator floor $10M, residual<−0.10, `RhoHaltError` typed exception
- **2.1.c** + **2.4** deliverables explicitly state HALT-trigger tests must be green including the residual<−0.10 path

All 3 spec §4.3 HALT triggers + 1 typed-exception trigger are now mechanically enforced before notebook authoring. Closure complete. (Note: the prior CR review mentioned a `ResidualSignError` — v0.2 collapsed this into `RhoHaltError`, which is fine since both fire on the same condition.)

### S4 — Trio HALT enforcement → CLOSED (via mechanical template)

Required: specify trio HALT enforcement mechanism (script or per-task wording).

v0.2 takes Option (a) — mechanical template — and goes further than the CR fix sketch:
- **0.10** authors `simulations/d1d_d4_joint/anti_fishing_checks.py` + `_TEMPLATE.ipynb` embedding primary-spec-first ordering + sign-concordance integer-count display + p-values-banned in sensitivity outputs; compliance grep test fails on stub notebooks until they adopt the template
- **0.11** authors `_TRANSPARENCY_BLOCK.md` + structural grep test checking each notebook contains all 4 D1-transparency disclosure fields
- Phase 3-6 task wording references trio HALT-checkpoint review for each notebook task

The grep-based compliance test is weaker than an AST-level lint (the plan flags this self-honestly under Open items #6) but is sufficient for v0.2 lock — grep catches the named forbidden patterns, and AST tightening is a v0.3 enhancement.

### S5 — Phase 2.1 batching → CLOSED via C3 split

Already covered under C3. 2.1.a/b/c split resolves both C1 batching and C3 dual-dispatch in one move.

---

## Plan-completeness audit v0.2 (per-phase task count)

| Phase | v0.1 tasks | v0.2 tasks | Delta | Notes |
|---|---|---|---|---|
| Phase 0 | 4 | **12** | +8 | 0.5/0.6/0.7/0.8 (TDD harnesses), 0.9 (nbconvert), 0.10 (anti-fishing template), 0.11 (transparency template), 0.12 (Stage-2 firewall) |
| Phase 1 | 5 | 6 | +1 | 1.6 early RC checkpoint (S1-RC) |
| Phase 2 | 7 | 9 | +2 | 2.1 split into 2.1.a/b/c (net +2) |
| Phase 3 | 2 | 2 | 0 | unchanged |
| Phase 4 | 1 | 1 | 0 | unchanged |
| Phase 5 | 2 | 2 | 0 | unchanged |
| Phase 6 | 2 | 3 | +1 | 6.1.5 Delphi-before-memo (S1-CR) |
| Phase 7 | 3 | 3 | 0 | unchanged |
| **Total** | **26** | **38** | **+12** | All inflations are TDD harnesses, mechanical compliance gates, or review-ordering fixes — zero scope creep |

Wall-clock revised 9 days → 12-14 days, now matches spec §10's 3-week budget and predecessor dev_ai_cost_v2 12-day actual. Realism gap from v0.1 (RC-C1) is closed.

Dependency DAG (Phase 0 → 1 → 2 → 3∥4 → 5 → 6 → 7) preserved and tightened: every Phase 2 module now has a Phase 0.x test pre-condition, and Phase 6.1.5 Delphi sits as a hard gate before Phase 6.2 memo authoring.

---

## NEW issues introduced

### N1-NEW (nit) — `pandas.testing.assert_frame_equal(...)` function call in Phase 2.6

Borderline against `feedback_no_code_in_specs_or_plans.md`. Read as a tolerance spec it's fine; read strictly it's executable Python in a plan. Suggest rephrasing as prose ("absolute tolerance 1e-9, relative tolerance 1e-6, asserted via pandas frame-equality"). Non-blocking.

### N2-NEW (nit, plan-self-flagged) — Open item #6: grep vs AST anti-fishing lint

Plan v0.2 authors flag this themselves. Grep is sufficient for v0.2 lock; tighten to AST if false negatives surface during Phase 3-6 execution. Non-blocking.

### N3-NEW (nit, plan-self-flagged) — Open item #7: Stage-2 firewall regex breadth

Plan v0.2 authors flag the `(Panoptic|deploy|LP|liquidity)` regex as potentially over-broad. The docstring/spec-reference exception is the safety valve. Concrete test: when commit attempts touch `simulations/d1d_d4_joint/` referencing "liquidity" inside a docstring or `docs/specs/` citation, does the hook pass? Phase 0.12 deliverable says "test commit confirms rejection" of a positive case but doesn't require a negative-case test (docstring exception works). Recommend adding "+ test commit confirming docstring/spec-reference exception passes" to 0.12 deliverable. Non-blocking nit.

### N4-NEW (nit) — Phase 2.5 panel_io still lacks a dedicated 0.x failing-test task

The parquet round-trip test is collapsed into 2.5's own deliverable. Strict TDD reading wants the test written first as a Phase 0.x task. Defensible because the property test inherits from 0.3 Hypothesis strategies on `OnchainInflowRow` — so the test infrastructure is pre-staged even if no dedicated 0.x line item exists. Non-blocking nit.

### N5-NEW (informational) — Wall-clock now realistic but tight

12-14 days for 38 tasks plus Delphi cascade plus 2-way post-hoc review is achievable but leaves no buffer for a Delphi-driven CORRECTIONS-C cascade. If 6.1.5 surfaces Critical findings, expect 14 → 16-17 days. Acknowledge in execution kickoff, not a plan-level blocker.

---

## Prior nits status (v0.1 N1-N6)

| Nit | Status in v0.2 |
|---|---|
| N1 pre-pin compliance task | Partially absorbed — 0.10 anti-fishing template includes primary-spec-first ordering, which is the pre-pin enforcement vehicle; no dedicated "pre-pin compliance" task. Acceptable. |
| N2 ≥3-anchor threshold justification | Phase 1.5 expanded to ≥4 anchors with target "≥3 of 4 agree" (RC-S2). Threshold count now justified by anchor expansion, not arbitrary. CLOSED. |
| N3 Phase 2.7 gate not in spec | Open in v0.2; the plan adds 2.7 (now also 1.6) without spec amendment. Acceptable as plan-level gate per N3 fix guidance. |
| N4 wall-clock | Revised 9 → 12-14 days. CLOSED. |
| N5 10 sensitivity arms | Closed in v0.2 open items as spec-level (sign-concordance only). CLOSED. |
| N6 import-discipline test | Still under-specified — 0.1 says "import-discipline test failing → passing" without naming the assertion. Defensible because 0.1 is a Data Engineer task and the agent will instantiate the AST-walk; acceptable but worth a follow-up nit. Open. |

---

## Pass-fail

| Item | Status |
|---|---|
| MUST C1 (TDD coverage) | PASS |
| MUST C2 (frozen real snapshot wording) | PASS |
| MUST C3 (single-specialist-per-task) | PASS |
| SHOULD S1 (Delphi reorder) | PASS |
| SHOULD S2 (Tier 3 acceptance) | PASS |
| SHOULD S3 (residual<−0.10 HALT thread) | PASS |
| SHOULD S4 (trio HALT enforcement) | PASS (mechanical template route) |
| SHOULD S5 (2.1 batching) | PASS (via C3 split) |
| NEW issues | 5 nits, all non-blocking |
| Plan completeness | 26→38 tasks, zero scope creep, all inflation accounted for |
| Wall-clock realism | 9→12-14 days, matches spec §10 + predecessor pattern |

**Closure verdict: APPROVED_WITH_NITS.** Plan v0.2 is mergeable. The 5 new nits (N1-NEW through N5-NEW) and 1 carried-forward nit (N6 import-discipline) are documentation-tightening items that can be addressed during Phase 0 execution without blocking the lock.

Recommended pre-execution housekeeping (optional, not blocking):
1. Rephrase Phase 2.6 `assert_frame_equal(...)` call as prose tolerance spec
2. Add negative-case test commit to Phase 0.12 (docstring/spec-reference exception)
3. Name the AST-walk assertion for Phase 0.1 import-discipline test

CR closure review closes here.
