# Reality Checker Verdict — D1.D + D4 Joint Implementation Plan v0.1

**Plan reviewed**: `docs/plans/2026-05-18-d1d-d4-joint-implementation.md` v0.1
**Spec anchor**: `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2 (APPROVED_WITH_NITS)
**Predecessor anchor**: `docs/plans/2026-05-04-dev-ai-stage-1-simple-beta-implementation.md` (491 lines, 11-13 specialist-day floor)
**Reviewer**: Reality Checker (hard lens)
**Date**: 2026-05-18

---

## Verdict

**NEEDS WORK** (do not approve for execution as-is).

The plan faithfully tracks spec v0.2 §3.1, §4.1-§4.3, §6, §7, §13. Specialized-agent assignments are mostly defensible; TDD posture is gestured-at; transparency disclosure is referenced. **But the plan is materially under-specified vs the predecessor pattern, and several anti-fishing tripwires it claims to enforce are aspirational rather than mechanical.** The 9-day estimate is implausible against a precedent of 11-13 specialist-days for a *single-sided* iteration (dev-ai Stage-1 was D1.D only, no joint, no GPD, no D4 side). Phase 0 TDD is sketched at 4 tasks where the dev_ai_cost_v2 precedent had per-task per-step red→green discipline; the plan does NOT install integration-test guards against the 5-instance silent-test-pass catalog. Three Critical issues must be fixed before execution; four Strong should be fixed; nits below.

---

## Critical (MUST fix before dispatch)

### C1 — Wall-clock estimate is unrealistic; 9 days vs 3-week budget hides scope

The plan estimates **9 working days / 66 hours**. The predecessor (`2026-05-04-dev-ai-stage-1-simple-beta-implementation.md` v1.1) carries an **11-13 specialist-day unconditional floor** for a *narrower* iteration:
- Predecessor = D1.D side only (Section J vs COP/USD lag), single OLS regression, three notebooks (`01_data_eda`, `02_estimation`, `03_tests_and_sensitivity`), one panel.
- This plan = D1.D side + D4.1 GPD POT + joint ρ̂ + off-ramp decomposition, **six notebooks**, **three independent data sources** (Dune, CryptoCompare, Mento subgraph, Banrep), four anti-fishing HALT gates (|ρ̂|>1.5, denom-floor, residual<−0.10, stationarity-gate fail), 5-arm Colombia-scalar sensitivity, 3-arm GPD fit, regime-conditional analysis labeled exploratory, and a CORRECTIONS-A pooled-prior Bayesian posterior update.

Predecessor actually consumed **~12 calendar days** for the smaller scope (per `memory/project_dev_ai_cost_v2_verdict.md` chronology + CORRECTIONS-κ HALTs). This joint plan is at least 1.7× the scope. Realistic floor: **15-20 specialist-days**, matching the spec §10 3-week target with **no margin** for the HALT cycles that anti-fishing-locked specs structurally invite (|ρ̂|>1.5 HALT, denom-floor HALT, stationarity-gate fail HALT, residual<−0.10 HALT — four pre-pinned tripwires, each one a CORRECTIONS-block + 3-way review per `feedback_pathological_halt_anti_fishing_checkpoint`).

Plan §"Open items for reviewer attention" item 5 admits "implementation plan is faster than spec budget by design (review iterations consume the buffer)". This is **backwards**: review iterations and HALT cycles do NOT live in unspecified buffer; they are predictable scope. The predecessor explicitly carved out "+2-3 days if cell-pathology fires" and "+1.5 days if ESCALATE-trigger fires". This plan carves out zero contingency.

**Required fix**: rewrite §"Estimated wall-clock" to include explicit HALT-contingency lines (4 pre-pinned tripwires × ~1 day each = +4 days). Raise unconditional floor to 14-16 days. Acknowledge that the spec §10 3-week target only holds if zero HALTs fire.

### C2 — Phase 0 TDD scaffold is too thin; silent-test-pass guard absent

Plan Phase 0 lists 4 tasks (0.1 scaffold, 0.2 disposition template, 0.3 types tier + Hypothesis, 0.4 stationarity-gate harness). That's it. Per `feedback_strict_tdd.md` (NON-NEGOTIABLE) every implementation task in Phases 1-2 needs a failing test FIRST. Phase 1 has 5 ingest tasks (Dune IO, CryptoCompare IO, Banrep extend, Mento IO, cross-check); Phase 2 has 7 module/utility tasks. **Only 1 of those 12 implementation tasks (Phase 2.2 stationarity gate) has a corresponding pre-written test in Phase 0**.

The plan's Phase 1 tasks include language like "tests against fixture Dune response" (1.1) but does not lay out the failing-test-first cycle. Phase 2.1 says "unit tests + Hypothesis strategies pass" — past tense, as if the tests already exist. The plan does NOT install:
- A red→green discipline per implementation task (i.e., a test scaffold in Phase 0 that fails for every utils/modules file the plan will write later).
- The three integration tests against `nbconvert --execute` per notebook that `project_fx_vol_econ_reviewer_and_silent_test_pass_lessons.md` identifies as the load-bearing backstop against the 5-instance silent-test-pass catalog (Tasks 22 E1, 25 cell 10, 27 §1, 24 cell 116, 31 R2).

The plan mentions in its cross-cutting requirements section: "Integration tests run `nbconvert --execute` on every notebook (guard against `feedback_silent_test_pass` 5-instance catalog)" — but this is buried at the bottom and is NOT scheduled as a Phase 0 task. There is no `tests/integration/test_*_end_to_end_execution.py` file laid out in the deliverables.

**Required fix**:
1. Expand Phase 0 with a Task 0.5 "lay all unit-test files for every Phase 1 + Phase 2 module/util with `@pytest.mark.xfail(reason='not implemented yet')` markers" so the red→green chain is enforceable by CI.
2. Add Phase 0 Task 0.6: lay out `tests/integration/test_nb{01..06}_end_to_end_execution.py` skeletons with `nbconvert --execute` calls. These must exist BEFORE any notebook is authored, per the silent-test-pass catalog lesson.
3. Add a Phase 6.X or Phase 7.0 task: run the integration tests as the last gate before verdict commit. The cross-cutting bullet is not enforceable; a scheduled task is.

### C3 — Anti-fishing tripwires are aspirational, not mechanical

The plan's "Cross-cutting requirements > Anti-fishing tripwires" section lists 4 enforcement rules (primary spec first; sensitivity arms as sign-concordance only; regime-conditional ρ̂ labeled exploratory; HALT triggers in every notebook's data-QC cell). **None of these are enforceable in code or CI as written.** They read as guidelines an Analytics Reporter is expected to follow.

Compare to spec §3.1 single-primary commitment, which the spec locks at the level of estimand definition. The plan must translate spec §3.1 into mechanical checks:

- "Primary spec reported first, sensitivity below" → there is no test that asserts the order of cells in a notebook, no linter rule, no notebook-template-with-required-order. An Analytics Reporter under HALT-cycle pressure could easily report sensitivity arms before primary; nothing in the plan catches that.
- "HALT triggers (|ρ̂|>1.5, denominator floor, residual<−0.10, stationarity-gate fail) check in every notebook's data-QC cell" → there is no shared QC-cell helper to import, no test that asserts every notebook calls the HALT-trigger function, no notebook template enforcing the cell.
- "Sensitivity-arm sign-concordance reported as a single integer count" → no schema enforcement on the output table; nothing prevents a frustrated AR from sneaking a p-value back in.

**Required fix**: Phase 0 must include a Task 0.X laying out `simulations/d1d_d4_joint/modules/anti_fishing_checks.py` with concrete callables (`assert_primary_before_sensitivity(nb_path)`, `compute_sign_concordance_count(arms) -> int`, `halt_if_rho_excursion(rho_hat)`, `halt_if_denom_floor(E_T)`) AND `tests/integration/test_notebook_anti_fishing_compliance.py` that runs every notebook and asserts each rule fires. Without this, the tripwires are theater.

---

## Strong (SHOULD fix)

### S1 — Phase 2.7 review checkpoint fires too late

Phase 2.7 (panel-builder 2-way review) is the FIRST review checkpoint in the plan after Phase 0.1 (CR compliance check on scaffold). Between Phase 0.1 and Phase 2.7 there are **11 implementation tasks** (0.3, 0.4, 1.1-1.4, 2.1-2.6) authored by Data Engineer + Senior Developer with NO review checkpoint. The silent-test-pass catalog (`project_fx_vol_econ_reviewer_and_silent_test_pass_lessons.md`) explicitly warns that drift accumulates without inter-phase RC review.

Specifically: the 5 silent-test-pass instances were all caught by RC review at task-level granularity, not phase-level. By Phase 2.7, the panel-builder consumes outputs from Dune IO + CryptoCompare IO + Mento IO + Banrep IO + 4 modules + 2 utils. If any of those silently-pass their unit tests but produce wrong rows, RC at Phase 2.7 will be tracing back through 11 tasks of accumulated state.

**Recommended fix**: insert an RC checkpoint at end of Phase 1 (post-1.5 cross-check) and an RC checkpoint at end of 2.4 (post-rho_compute, the most identification-critical module). The plan currently has only CR sign-offs at 0.1 / 0.3 / 1.1 / 2.1 / 2.5 — those are tier-discipline checks, not anti-fishing identification checks. RC and CR have orthogonal signals per the dev_ai_cost_v2 lessons memo.

### S2 — Phase 1.5 cross-check anchor count is insufficient

Plan Phase 1.5 (Reality Checker cross-check) names two anchors: Chainalysis LATAM crypto adoption report 2025 + Bitso $10.4B Jan-Jul 2025 totals. The deliverable target is "≥ 3 anchor agreements at order-of-magnitude" — but the task lists only 2 anchors. The plan's own deliverable target is unmet by the task description.

Additional anchors readily available at zero marginal cost:
- **DefiLlama** Bitso flows + stablecoin TVL per chain (free API; cross-checks Dune Bitso inflow at chain granularity)
- **Etherscan label dataset** (Bitso 1 `0x58b7...` hot-wallet historical balance; verifies Dune Bitso 1 anchor identity at row level)
- **Mento broker public dashboards** (cross-checks Mento USDC↔COPm swap volumes independently of subgraph)
- **Lemon's published Argentine totals** as proxy for LATAM CEX share (Lemon is the Argentine counterpart; cross-validates Lemon hot wallet attribution)

**Recommended fix**: expand Phase 1.5 to list 4 anchors (Chainalysis, Bitso public, DefiLlama, Etherscan label). 2 anchors agreeing at order-of-magnitude is a weak anti-fishing guard given the 20% Colombia-share scalar carries 10-35% sensitivity (already a 3.5× swing per spec §4.3).

### S3 — Stage-2 firewall has no mechanical enforcement

Spec §8 forbids M-sketch deployment work in this iteration (RC S4 in spec review). The plan inherits this prohibition (Anti-fishing closure paragraph) but provides **no mechanism** for catching accidental Stage-2 work. Risk: an Analytics Reporter authoring notebook 04 (joint ρ̂) could naturally drift into "let's compute the size of the implied Mento USDC/COPm long position" and accidentally cross the firewall.

**Recommended fix**: Phase 0 should add either (a) a pre-commit hook in `.git/hooks/pre-commit` that rejects commits to `notebooks/d1d_d4_joint/` containing strings matching `r"(panoptic|mento.*broker.*position|long-copm|short-usdc|notional|strike|delta|gamma)"` (with exceptions list for descriptive references), OR (b) a CI check `tests/integration/test_stage2_firewall.py` that scans notebook outputs for Stage-2-vocabulary leakage. Spec-level prohibition without mechanical enforcement violates the same pattern as `feedback_pathological_halt_anti_fishing_checkpoint` — pre-pinned constraint without enforcement = silent fishing risk.

### S4 — D1 transparency disclosure block enforcement is verbal, not structural

The plan cites the 4-required-disclosure block (data used / gaps / non-claims / possible outcomes incl. non-retirement) in Phase 3.1 ("**mandatory data-quality disclosure block** per spec §6 + D1 transparency condition") and in the cross-cutting requirements. But there is no:
- Notebook template with a pre-stamped "Data-Quality Disclosure" cell.
- Linter / nbformat check that asserts every notebook contains a cell tagged `data-quality-disclosure` with all 4 sub-sections.
- Test in Phase 7.2 that grep-asserts every notebook contains "Possible outcomes including non-retirement".

`feedback_d1_transparency_continuation.md` explicitly states "This is NOT a license to drag out the iteration indefinitely; it is a license to honestly close it at FAIL or PARTIAL-PASS without escalation pressure to manufacture a clean verdict." Without structural enforcement of the disclosure block, the AR could submit notebooks with token nods to the requirement that satisfy "framing" but not substance.

**Recommended fix**: Phase 0.2 disposition template should be paired with Phase 0.X "notebook template at `notebooks/d1d_d4_joint/_TEMPLATE.ipynb` with pre-stamped cells for citation block, data-quality disclosure (4 sub-cells: data / gaps / non-claims / possible outcomes), HALT-trigger QC cell". Phase 7.2 should include a grep test for the 4 disclosure sub-sections in every notebook.

---

## Nits (MAY fix)

### N1 — Specialized-agent mismatches

Most assignments are defensible (Analytics Reporter for notebooks per predecessor; Data Engineer for IO; Senior Developer for modules). Minor questions:
- Phase 6.2 LaTeX scaffold dispatched to **Technical Writer**. Predecessor used the Analytics Reporter for memo + Technical Writer only for reader-facing PDF / README artifacts (`project_fx_vol_econ_reviewer_and_silent_test_pass_lessons.md` decision-rule table). LaTeX scaffold for a verdict memo is on the borderline. Acceptable but consider Analytics Reporter for verdict-memo authoring + Technical Writer for PDF-export polish only.
- Phase 2.2 stationarity gate dispatched to Senior Developer. Given the econometric subtlety (ADF + KPSS conjunction, cointegration fallback), Model QA Specialist co-dispatch would be safer. The dev_ai_cost_v2 lessons memo's "When to dispatch" rule says any inference-procedure code adds Model QA.
- Phase 2.3 GPD POT dispatched to Senior Developer + Data Engineer. Same Model QA argument — GPD MLE + profile-likelihood CI + jackknife is inference territory.

### N2 — Phase 7.1 Delphi auditor count

3 Opus auditors per dev_ai_cost_v2 v0.2.10 pattern. The joint iteration has two estimands (D1.D β, D4.1 GPD ξ) + one composite (ρ̂) = 3 distinct identification surfaces. 3 auditors is at-floor; adding a 4th specialized on the joint-aggregation econometrics (ρ̂ ratio-of-means bias + wallet non-overlap) would mirror the spec-review pattern where CR + RC + Model QA all caught distinct issues. Acceptable as-is per precedent, but flag for user adjudication.

### N3 — Phase 1.2 "re-uses D4.2 gating scripts at scratch/.../fetch_prices_v2.py as starting point"

The plan inherits an existing CryptoCompare fetcher from D4.2 gating scratch. This is fine, but the inheritance should explicitly state "verify the inherited script's free-tier compliance per `feedback_d1_transparency_continuation` carry-forward + spec §9.14 inherited from predecessor" — predecessor v1.1 closed D11 + RC FLAG-4 on free-tier compliance. The plan does not mention the free-tier discipline at all. Add a one-line free-tier compliance pin.

### N4 — Phase 5.1 regime conditionals labeled "exploratory only"

Plan lists this as a deliverable. Spec §4.3 + §3.1 binds it. Make it more concrete: every regime-conditional ρ̂ figure caption must contain the exact string "EXPLORATORY — NOT INFERENTIAL" in title case (or similar machine-grep-able token) so Phase 7.2 RC can grep-assert compliance.

### N5 — Phase 6.1 verdict notebook does not mention pre-pinning a verdict rubric

Spec §7 lays out 4 collectively-exhaustive verdict rows (PASS / PARTIAL / FAIL / NON-RETIREMENT). Phase 6.1 should consume this rubric mechanically (a `simulations/d1d_d4_joint/modules/verdict_rubric.py` callable that takes (β, β_p, ξ, ρ̂, sensitivity_concordance, data_quality_flag) → verdict_label). Currently Phase 6.1 deliverable is "Notebook + verdict" with no module assignment, opening room for hand-coded verdict logic per-notebook.

### N6 — DAG diagram says Phase 3 ⟷ Phase 4 parallel but Phase 4 pre-condition is "2.7, 3.1 done"

Phase 4.1 lists `2.7, 3.1 done` as pre-conditions. So Phase 4 actually waits on Phase 3.1 (data EDA) before starting, making "Phase 3 ⟷ Phase 4 parallel" misleading. Either drop the 3.1 dependency from 4.1 (D4.1 GPD POT does not actually need the D1.D inflow EDA — they consume different data sources) or correct the DAG diagram. Recommended: drop the dependency; D4.1 GPD POT operates on CryptoCompare USDC/USDT/DAI daily, which is independent of Dune Bitso inflow.

---

## Open questions

1. **Per spec §13 CORRECTIONS-B is "user-approved implicit per autofix-all directive"** — has the user explicitly re-signed on CORRECTIONS-B or is the implicit approval load-bearing? The plan inherits this as fait accompli but the spec's own closure-only re-review is "pending" per the v0.2 header.

2. **Plan §"Estimated wall-clock" claims "Matches spec §10 '3-week execution plan' wall-clock target with margin for review iterations"** — but 9 days < 15 days = 3 weeks. The plan is either claiming to beat the spec budget by ~40% (overconfident) or implicitly defining "review iterations" outside the 9-day count (in which case the 9 days is execution-only). Which is it? Verdict re-issue cycles after Phase 7.2 are not in the 9 days.

3. **Phase 2.6 panel-builder Tier 3 round-trip** — does this verify against a pre-committed Tier 1 reference? The CLAUDE.md three-tier discipline says `make verify` is Tier 3 vs published Tier 1. But this iteration is producing the FIRST version of the joint panel; there is no published Tier 1 to round-trip against. The plan should clarify that Phase 2.6 Tier 3 deliverable IS the round-trip definition and Phase 2.7 review approves it.

4. **`memory/feedback_no_inline_signatures_in_plans.md`** (untracked per git status) — what does this say about the plan's frontmatter? Plan v0.1 has no frontmatter sha pins (unlike predecessor v1.1.1 which pins `spec_sha256` + `plan_verifier_v1_*` + `corrections_kappa_disposition_pin`). Should plan v0.1 carry a similar frontmatter or does the recent feedback forbid it?

5. **5 + 10 sensitivity-arm proliferation** — plan open-items item 4 asks if 10 sensitivity arms (5 Colombia × 2 regime × 1 placebo) is too many. Under spec §3.1 single-primary commitment + Bonferroni-equivalent posture, the answer is structurally: doesn't matter for inference because none of the arms rescue the primary. But for *interpretation*, 10 arms is a lot of sign-concordance bookkeeping. Recommend capping at 5 arms total for sign-concordance reporting (the 5 Colombia-scalar arms) and demoting the 2 regime breakouts + 1 placebo to "additional exploratory diagnostics, not in concordance count".

---

## Recommended path forward

1. Address C1 (wall-clock realism) + C2 (Phase 0 TDD scaffold) + C3 (mechanical anti-fishing enforcement) as v0.2 amendments. These are blockers.
2. Address S1-S4 as v0.2 amendments. These are quality-of-execution issues that will surface as Phase 5+ remediation if left unfixed.
3. Address N1-N6 inline or defer to v0.3 polish. Not blocking.
4. Re-issue v0.2 for 1-cycle RC closure review. CR closure review may be parallel.

**Estimated remediation effort**: 0.5 day for amendments + 0.5 day for re-review = 1 day total to clear to v0.2-APPROVED.

---

**Reality Checker**, 2026-05-18
Evidence base: spec v0.2 (343 lines read in full), plan v0.1 (159 lines read in full), predecessor plan lines 1-250 + grep scan, 4 anchor memos (specialized-agents / strict-TDD / D1-transparency / silent-test-pass).
File location: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-18-d1d-d4-joint-plan-review/rc.md`
