# RC verdict — A1 plan v0.1

**Reviewer:** Reality Checker (RC)
**Plan under review:** `docs/plans/2026-05-11-stage-3-a1-panoptic-restrategy.md`
**Review wave:** Wave-1 plan-time (per master spec §6.1)
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

## Executive summary

A1 plan v0.1 traces cleanly to repo state: commit `3442542` exists in git
log, parent paths (`simulations/saas_builder/cohort_5_strip/`,
`simulations/saas_builder/data/`) exist, the canonical TP1 fixture
`(S_0=4000, sigma_0=20000, k_star=4687.94)` matches both master-spec
§2.1 phase 2 (line 155) and `Z_cap_pinned.json::Z_cop_per_month =
4687.942347178384` (rounded), and Pin P-A1.4 is present in master-spec
§5 (line 387). No outcome-direction language; the 5pp threshold is
pre-pinned and KEEP/REPLACE are treated symmetrically. The plan ships
NO Python or Solidity code blocks — the only fenced blocks are an ASCII
file-tree (lines 51–70) and a JSON-schema illustration (lines 205–218),
both admissible per `memory/feedback_no_code_in_specs_or_plans.md`.
Three flags worth raising for plan-author disposition: (1) `general-purpose`
agent dispatch for Tasks 1.1/1.2/3.2 lacks an explicit specialist
rationale per `feedback_specialized_agents_per_task.md`; (2) Task 2.4's
"RC cross-check confirms each `max_relative_error` is reproducible …
to ≥ 1e-9" is in tension with the documented strip-level non-IO
discipline — needs sourcing; (3) the §10 artifact ledger lists a code
sub-package as an "artifact," which is fine but not mirrored in
master-spec §4.

## Findings

### BLOCK

(none)

### FLAG (material)

- **RC-FLAG-A1.1 — `general-purpose` dispatch for research tasks.**
  Tasks 1.1, 1.2, and 3.2 dispatch `general-purpose`. The convention
  in `memory/feedback_specialized_agents_per_task.md:21` ("before
  every plan task, identify the specialist. If none fits, flag to the
  founder") admits no-specialist fall-back BUT requires the flag.
  Plan §5 / §7 should either (a) name a specialist (`Web Researcher`
  or `Technical Writer` for Task 1.1's STRATEGY_COMPARISON.md;
  `Technical Writer` for Task 3.2's stub spec), or (b) add an
  inline note that this is the documented "no specialist fits" case.

- **RC-FLAG-A1.2 — RC self-dispatch is procedurally awkward.**
  Task 2.4 (line 180) and Task 3.1 (line 200) dispatch
  `Reality Checker` as an inline cross-check during execution.
  Master-spec §6.2 Wave-2 already pins RC as a post-execution
  reviewer; using RC as a mid-execution sub-task reviewer risks
  blurring Wave-1/Wave-2 boundaries and could violate Delphi-
  independence on the eventual Wave-2 verdict (the same RC will have
  already cross-checked the numbers it later "independently"
  audits). Recommend: rename the in-task role to "audit pass"
  or dispatch `audit-econ` / a fresh specialist seat for the inline
  cross-check, reserving the `Reality Checker` agent identity for
  Wave-2.

- **RC-FLAG-A1.3 — "Reproducible to ≥ 1e-9" is unsourced.**
  Task 2.4 acceptance line 185 pins a `1e-9` numerical re-run
  tolerance, but the cohort_5_strip code pins envelope tolerance at
  `REPLICATION_REL_TOL = 0.35` (`types.py:74`) and weight-sum at
  `WEIGHT_SUM_TOL = 1e-12` (`types.py:52`). Neither is `1e-9`.
  Plan should cite the source of the `1e-9` rerun-equivalence
  pin (floating-point determinism of the verifier under fixed
  seeds + same numpy?) or relax to a defensibly-sourced number.

### NIT (cosmetic)

- **RC-NIT-A1.1 — §10 lists a code sub-package as an artifact.**
  Master-spec §4 artifact ledger (lines 369–370) lists only
  `STRATEGY_COMPARISON.md` and `strategy_verdict.json` as A1
  artifacts. Plan §10 (line 277) additionally lists
  `simulations/saas_builder/cohort_5_strip/strategies/` as an
  artifact row. Not wrong (the package IS a plan output) but
  master-spec mirror would prefer it called out explicitly as a
  CODE deliverable distinct from the data ledger.

- **RC-NIT-A1.2 — Predecessor commit sha in §0 is correct but
  prefix-only.** Plan line 11 cites `(commit 3442852)` which I
  verified resolves to `3442852 feat(saas-cohort-5-strip):
  Carr-Madan 3-condor (12-leg) IronCondor strip emit`. Consider
  expanding to full 7-char sha for forensic stability — `3442852`
  IS full-7-char, so this is already fine; reading as a NIT only
  in case the convention is to pin 10+ chars.

- **RC-NIT-A1.3 — §4 cross-spec reference table omits §1.3.**
  Master-spec §1.3 (audit-block lineage) imposes a
  `consumed_strip_audit_block` requirement on A1's emits, and the
  plan §7 Task 3.1 JSON schema correctly carries that field — but
  §3 cross-spec table doesn't include §1.3. Add a row.

## Citation trace audit (sample checks)

| Plan claim | Plan loc | Cross-check | Status |
|------------|----------|-------------|--------|
| Commit `3442852` exists | §0 line 11 | `git log` row matches: `3442852 feat(saas-cohort-5-strip): …` | PASS |
| Master spec v0.2 exists | §0 line 10 | `git log` row `78841b1 review(stage-3-first-wave): … spec v0.1→v0.2 disposition` | PASS |
| Parent path `cohort_5_strip/` exists | §4 line 58 | `ls simulations/saas_builder/cohort_5_strip/` → emit.py, _errors.py, geometry.py, __init__.py, replication.py, types.py | PASS |
| TP1 fixture S_0=4000, σ_0=20000, k⋆=4687.94 | §6 line 184 | master-spec §2.1 phase 2 line 155 `(S_0=4000, σ_0=20000, K⋆=4687.94)` + `Z_cap_pinned.json::Z_cop_per_month = 4687.942347178384` | PASS |
| Pin P-A1.4 (5pp threshold) | §7 line 220 + §8 line 257 | master-spec §5 line 387 P-A1.4 row + §2.1 HALT-trigger bullet 2 (lines 195–201) | PASS |
| `REPLICATION_REL_TOL = 0.35` cited | §12 ref line 289 | `types.py:74` matches | PASS |
| Verifier docstring lines 1-28 | §12 ref line 288 | `replication.py:1-28` matches and contains the centered-strip + log-contract-proxy form | PASS |
| `IronCondor_strip.audit_block` lineage | §10 line 274 | master-spec §1.3 + §4 line 369 confirm `94150326…` is current | PASS (data file present) |
| Verdict JSON path | §4 line 66, §7 line 198 | master-spec §2.1 exit-deliverable line 185–187 matches | PASS |

## Convention-compliance audit

- **no-code-in-plans:** PASS. Two fenced blocks total
  (line 51: ASCII file-tree; line 205: JSON schema illustration).
  Both are admissible per `memory/feedback_no_code_in_specs_or_plans.md`
  (schema illustrations + commit-message snippets are exceptions).
  ZERO Python or Solidity fences. Confirmed via
  `grep -nE '^```' docs/plans/2026-05-11-stage-3-a1-panoptic-restrategy.md`.

- **specialized-agents-per-task:** PARTIAL — see RC-FLAG-A1.1.
  All 8 tasks carry an `**Agent dispatch:**` field (lines 83, 103,
  122, 144, 163, 180, 200, 237). Senior Developer dispatch for
  Tasks 2.1–3.1 is appropriate per types-tier convention.
  `general-purpose` dispatch for Tasks 1.1/1.2/3.2 is plausible but
  unrationalized — flag, not block.

- **anti-fishing pre-pinning:** PASS. §0 line 19 frames the
  verdict symmetrically (`KEEP_IRONCONDOR / REPLACE_WITH_X`).
  §5 Task 1.1 line 92 explicitly briefs "NOT to pre-rank
  primitives." §7 Task 3.1 lines 219–220 treats KEEP/REPLACE
  symmetrically on the 5pp threshold. The 5pp threshold itself is
  pre-pinned in master-spec §5 P-A1.4 (line 387) — defensibly
  content-addressed, NOT predicted outcome direction. No language
  of the form "we expect X to beat Y" anywhere.

- **HALT routing:** PASS. §9 HALT table (lines 261–267) routes
  each trigger appropriately: < 2 candidates → disposition memo +
  scope re-pin via master-spec §6.4; property-test failure →
  Senior Developer iterates without relaxing tests; numerical
  non-reproducibility → cohort_5_strip drift investigation; tie
  → user-enumerated tie-break; review BLOCK → CORRECTIONS-α in
  §11.

- **memory citations:** PASS. Both invoked memory files
  (`feedback_no_code_in_specs_or_plans.md` line 5, 291;
  `feedback_specialized_agents_per_task.md` line 7, 292) exist
  under `memory/` per `grep` confirmation.

---

*RC verdict authored independently per master-spec §6.1 Delphi-independence
safeguard. MQ verdict not previewed.*
