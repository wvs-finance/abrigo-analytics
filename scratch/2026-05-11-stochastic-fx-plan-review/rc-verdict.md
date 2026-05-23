# RC verdict — stochastic-fx-variant plan v0.1
**Reviewer:** Reality Checker (RC)
**Plan under review:** docs/plans/2026-05-11-stochastic-fx-variant.md
**Review wave:** Wave-1 plan-time (per spec v0.3 §10)
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

Default posture is NEEDS WORK; lifted to ACCEPT_WITH_FLAGS because every
load-bearing repo-state claim verified true (audit_block hex grep, file
paths, `NUMERICAL_IDENTITY_TOL` line, utils patterns, gitignore line 53).
Residual flags are material but not BLOCKing.

## Findings (BLOCK / FLAG / NIT)

**FLAG-RC-1 (material) — inline-backtick code signatures throughout
Acceptance bullets.** Parent spec v0.3 §11.4 closed FLAG-RC-1-v2 by
prose-ifying §3 `variance_proxy.py` function signatures. The plan now
re-introduces the same pattern in inline backticks at scale:
- L147–149: `GBMParameters(mu: float, sigma: float, x_0: float, T: float, dt: float, n_steps: int)` etc.
- L151–153: `CANONICAL_GBM = GBMParameters(mu=0.0, sigma=0.10/sqrt(12), …)` (an executable assignment expression).
- L171–172: `family_id: Literal["gbm", "ou", "merton"]`, full PathEnsemble + InversionVerdict field-by-field type-annotated declarations.
- L225, L249, L271, L294, L296: `__call__(rng_seed: int, n_paths: int) -> PathEnsemble` and
  `compute_sigma_t_per_path(ensemble: PathEnsemble) -> NDArray`.
- L226: literal recurrence `X_{t+dt} = X_t * exp((mu - sigma^2/2) * dt + sigma * sqrt(dt) * Z_t)` (math notation, admissible).
- L342–343: `PathEnsembleEmitter(emit_dir: Path)` constructor signature.

The brief explicitly narrows the check to fenced Python blocks ("Math
notation, JSON-schema shape illustrations, bash command lines, and ASCII
directory trees are admissible") — so this is not a no-code violation
under the brief's own wording. BUT the parent spec's RC-FLAG-1-v2
disposition framed the convention as applying to inline `(…) → return-type`
signatures too. The plan inherits a stricter reading by reference and
should align. Recommended disposition: keep the type-annotated field
LISTS for value-tier `__post_init__` validation requirements (these
are testable contract statements, not code), but rewrite the executable-
looking `CANONICAL_*` assignments (L151–153) as a prose table mirroring
spec §4.2's per-family pin table (which IS the canonical authority).
Not BLOCKing because the plan's purpose IS to direct an authoring agent;
the brief admits this.

**FLAG-RC-2 (NIT) — checkbox tracking syntax advertised but absent.**
Front-matter line 3: "Steps use checkbox (`- [ ]`) syntax for tracking."
Zero `- [ ]` markers exist in the document (`grep -cE "^- \[ \]"` → 0).
Per `superpowers:subagent-driven-development`, sub-agent flow expects
checkbox state-tracking. Either remove the front-matter promise or add
checkboxes at each task header. NIT only.

**FLAG-RC-3 (material) — Phase B / Phase C tolerance constant
co-location.** Plan L315 declares `MOMENT_REL_TOL = 0.05` and
`KS_PVALUE_FLOOR = 0.01` as `InversionVerifier`-private (Task 4.2
module-level). Plan L343 (Task 5 emitter) and L374–376 (Task 6
acceptance) refer to the same constants by name. Acceptable, but the
plan does NOT pin where these constants LIVE for import. Spec §8
calibrates both; the plan should pin the import path (e.g.,
`simulations.stochastic_fx.variance_proxy::MOMENT_REL_TOL`) explicitly
in Task 4.2 Acceptance so downstream tasks don't shadow-define them.
Recommend: add one bullet "exported from `variance_proxy.py` for
downstream import" to Task 4.2.

## Convention-compliance audit (no-code, agents-per-task)

- Fenced code blocks in plan: 2 total (L61–96 = file-structure ASCII
  tree; admissible). No fenced Python blocks. PASS per brief's literal
  wording.
- Inline-backtick signatures: extensive — flagged FLAG-RC-1 above.
- Agent dispatch field present on EVERY task: 13/13 tasks (Task 0, 1.1,
  1.2, 1.3, 2.1, 3.1, 3.2, 3.3, 4.1, 4.2, 5, 6, 7). PASS.
- Two N/A entries (Task 0 gitignore, Task 7 hex-grep) explicitly cite
  `memory/feedback_specialized_agents_per_task.md` shell-ops exception.
  PASS.
- Specialist-agent vocabulary used (`Senior Developer`, `AI Engineer`,
  `Reality Checker`) consistent with the feedback memory's catalog. PASS.

## Spec-coverage audit

§3 component → task mapping verified in plan §3 cross-reference table
(L40–55):
- `_errors.py` → Task 1.1 ✓
- `types.py` → Tasks 1.2 + 1.3 ✓
- `moments.py` → Task 2.1 ✓
- `generators.py` → Tasks 3.1 + 3.2 + 3.3 ✓
- `variance_proxy.py` → Tasks 4.1 + 4.2 ✓
- `emit.py` → Task 5 ✓
- Pins Z1.1–Z1.6 all mapped in plan §13 coverage table; Z1.5 cross-
  references Task 4.2's "N=1000 floor" rule (L320). PASS.
- §4.2 per-family parameter pin table referenced explicitly by Task 1.2
  ("Module-level canonical-pin constants per spec v0.3 §4.2 table") and
  by Task 4.2 (per-family reference-distribution dispatch). PASS.

## Type-consistency audit

- `family_id: Literal["gbm", "ou", "merton"]` declared at L171.
- Task 3.1 generator (GBM) emits ensembles consumed by Task 4.2 with
  `ensemble.family_id` dispatch on `{gbm, ou, merton}_moments` (L318).
  Closed alphabet matches.
- Task 5 emit filenames use `{family_id}` interpolation
  (`path_ensemble_{family_id}.parquet`, L342;
  `inversion_verdict_{family_id}.json`, L343). PASS.
- §4 file structure (L88–93) and §15 artifact table (L436–437) use
  `{family}` (without `_id` suffix). Cosmetic only — naming convention
  drift; NIT.
- `NUMERICAL_IDENTITY_TOL = 1e-6` import path verified:
  `simulations/saas_builder/cohort_4/types.py:48` = `NUMERICAL_IDENTITY_TOL: Final[float] = 1e-6`. PASS.
- `MOMENT_REL_TOL` / `KS_PVALUE_FLOOR` defined at Task 4.2, referenced
  by Task 5 (L343) and Task 6 (L375–376). Export-path pin missing —
  see FLAG-RC-3.

## File-path existence audit

- `simulations/saas_builder/cohort_4/types.py::NUMERICAL_IDENTITY_TOL`
  → line 48 `NUMERICAL_IDENTITY_TOL: Final[float] = 1e-6` ✓
- `simulations/saas_builder/data/IronCondor_strip.json` → file exists;
  `grep -F '94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329'`
  returns `"audit_block": "94150326…"` line ✓ (matches Pin Z1.6 hex
  exactly).
- `simulations/utils/{parquet_io.py, json_io.py, audit_block.py}` all
  exist ✓.
- `simulations/saas_builder/cohort_5_strip/__init__.py` audit-block
  reference is at the docstring tail (in Pin S8 description, line
  ~50ff); the literal hex lives in the emitted JSON file as verified.
  Plan correctly grep-targets the JSON, not the source module. PASS.
- Parent directories of new directories (`notes/` exists with
  PRIMITIVES.md / STAGE_2_RESULTS.md / SaaS_Builders_*; `simulations/`,
  `scratch/`) all exist. PASS.
- `.gitignore` line 53 region (lines 51–53 viewed) currently contains
  `simulations/saas_builder/data/` only — Task 0's planned addition of
  `simulations/stochastic_fx/data/` is correct and the
  "alphabetically near" claim is honest (alphabetical sort puts
  `stochastic_fx` after `saas_builder/data`). PASS.

## Anti-fishing posture audit

- No outcome pre-pinning: `grep "WILL PASS|will pass|will fail|expected to pass"`
  returned zero matches. PASS.
- The Task 6 commit-message line 383 reads
  `eval(stochastic_fx): end-to-end run at canonical pins — all 3 families PASS`.
  This is a PREDICTED commit message for the PASS branch only; it
  silently assumes the outcome. Recommended: change the planned commit
  message to outcome-neutral (`eval(stochastic_fx): end-to-end run at
  canonical pins — InversionVerdict per family emitted`) and have Task 6
  pick the PASS/FAIL message at run-time based on actual verdicts.
  FLAG-RC-4 (material anti-fishing concern: a pre-committed PASS commit
  message biases the executor to make the commit match the message).
- Pin Z1.5 "N=1000 floor, not parameter to grow" enforcement: present
  at Task 4.2 L320 ("the verifier rejects calls where
  `ensemble.paths.shape[0] != 1000` … Does NOT accept 'increased N'") AND
  in §13 row Z1.5 AND in §14 HALT routing row for Task 6. PASS.
- HALT routing table §14 covers every numbered task family
  (1.x / 2.1 / 3.x / 4.1 / 4.2 / 6 / 7) with explicit trigger → route
  mapping. Task 5 (emit) has no §14 row; failures there are
  ruff/ty/round-trip and routed by Task 1.x's "ruff / ty / Hypothesis-
  test fail" row in §14 by analogy. NIT — add explicit Task 5 row.

## Summary

Plan is implementable as-is for an authoring agent. Material flags
RC-1 (inline-backtick code in Acceptance bullets), RC-3 (constant
export-path pin missing), and RC-4 (pre-committed PASS commit
message) should be disposed in a v0.2 patch BEFORE plan execution
begins. NITs (RC-2 checkbox absence, family-naming drift, Task 5
HALT row) are admissible to dispose alongside or in a v0.2.1.

**Recommend:** ACCEPT_WITH_FLAGS — disposition v0.2 lands FLAG-RC-1
(prose-ify Task 1.2 `CANONICAL_*` to a table), FLAG-RC-3 (one bullet
in Task 4.2), FLAG-RC-4 (outcome-neutral Task 6 commit message). NITs
optional. No need for full Wave-1 re-dispatch; an orchestrator-side
v0.2 patch suffices per master-spec §6.1 ACCEPT_WITH_FLAGS-disposed
path.
