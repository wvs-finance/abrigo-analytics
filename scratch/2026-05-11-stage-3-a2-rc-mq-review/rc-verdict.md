# RC verdict — Stage-3 A2 plan (Real-data cohort conditioning)

**Reviewer:** Reality Checker (RC, Wave-1, Delphi-independent per master-spec §6.1)
**Plan under review:** `docs/plans/2026-05-11-stage-3-a2-real-data-conditioning.md` v0.1
**Master spec:** `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2
**Verdict date:** 2026-05-11
**Verdict:** **ACCEPT_WITH_FLAGS** — 1 BLOCK-candidate downgraded to MATERIAL once file-path naming is fixed (it is pervasive but mechanically correctable), plus 3 MATERIAL FLAGs and 2 NITs. Default posture would have been NEEDS WORK; downgraded because the math/spec scaffolding is correct and the issues are file-path / convention drift, not scientific drift.

---

## §1 Reality-check commands executed

- `ls simulations/saas_builder/{cohort_1,cohort_4,cohort_5_strip,data}` — confirms cohort_4 / cohort_5_strip / data exist; **`cohort_1/` does NOT exist** (see FLAG-1).
- `grep -n ZCapPinned ... posterior.py` — confirmed dataclass has `schema_version` + optional `sign_verdicts` field; additive v1.2 with optional `parent_audit_block` is forward-compatible.
- `grep -n schema_version ... json_io.py` — confirmed `ZCapPinnedReader` / `ZCapPinnedWriter` accept v1.0 (no `sign_verdicts`) AND v1.1 (with `sign_verdicts`), additive pattern.
- `cat .gitignore` — confirms `data/*.parquet` is gitignored; `simulations/saas_builder/data/cohort_distribution_empirical.parquet` would inherit that ONLY IF the rule covers nested `data/` dirs (see FLAG-3).
- `ls scratch/2026-05-11-stage-3-a2-rc-mq-review/` — review directory exists, ready to receive verdict.
- `grep -rn synthetic_tau_t simulations/saas_builder/cohort_{3,4,5_strip}/` — confirms cohort_4 `io.py:58` consumes `simulations/saas_builder/data/synthetic_tau_t`; legacy-name retention claim is plausible.
- `grep -n StripEmitter / assert_long_vol_signature cohort_5_strip/` — confirmed both APIs are public (`__init__.py` exports both); orchestrator-only re-emit is technically feasible.
- `grep -rn ar1_log\|det_churn cohort_3/` — confirmed `loo.py` ships PSIS-LOO-CV via `arviz.compare(..., ic="loo", method="stacking")`; Task 3.3 re-run target is real.

---

## §2 FLAGs (severity-graded)

### FLAG-1 — MATERIAL (pervasive file-path drift)

**Issue.** The plan refers to `simulations/saas_builder/cohort_1/` (12+ occurrences: §4 file structure, Task 3.1 agent brief citing `cohort_1/emit.py`, Task 3.2 modifying `cohort_1/emit.py::CohortEmitter`, §4 file-structure box `simulations/saas_builder/cohort_1/   ← READ-ONLY`, §13 references). **No such directory exists.** The C1 implementation lives at the SAAS-builder top level — `simulations/saas_builder/{emit.py, model.py, priors.py, diagnostics.py}`. The `cohort_1/` namespace was a Stage-2 plan convention that was never instantiated; cohorts 2 / 3 / 4 / 5_strip have their own sub-packages, but C1 is the un-namespaced top level.

**Evidence:**
```
$ ls simulations/saas_builder/
cohort_2  cohort_3  cohort_4  cohort_5_strip  data  diagnostics.py
emit.py  _errors.py  __init__.py  model.py  priors.py  verify
```

**Impact.** Every Task 3.x file-path is wrong (Task 3.1, 3.2, 3.4). Task 3.2's agent brief cites a non-existent file (`cohort_1/emit.py`). The NEW `simulations/saas_builder/cohort_1_empirical/` sub-package (Task 2.2) is fine structurally but its naming becomes misleading next to a non-existent `cohort_1/` parent.

**Required fix.** Either (a) rename Task references throughout from `cohort_1/...` to `saas_builder/...` for the top-level files (read-only references) and `cohort_1_empirical/` for the new sub-package; OR (b) introduce a `cohort_1/` sub-package as a Stage-2 cleanup task PRECEDING A2 (separate plan/PR). Path (a) is far less invasive. The plan must NOT execute Task 3.x until §4 file-structure box reflects actual repo paths.

### FLAG-2 — MATERIAL (Task 1.2 git-tag temporal-ordering — chicken-and-egg)

**Issue.** Task 1.2 says: tag the commit landing Task 1.1 with `a2-sourcing-pinned-2026-05-NN` AND record the commit sha at the top of `SOURCING_PROTOCOL.md` in a §0 lock-block. The commit message text in Task 1.2 explicitly forbids amending. But to record the commit-sha INSIDE the file, the file must be modified AFTER the commit lands; that modification then needs its own commit. Pin P-A2.1 says the protocol mtime MUST precede the first data-row commit. Two issues:

1. **Self-reference loop:** the protocol file at commit-N records sha-of-commit-N, but sha-of-commit-N depends on the file contents. The only ways out are: (i) amend (forbidden by Task 1.2), (ii) two-commit dance where the lock-block is a SEPARATE commit with its own sha referencing the parent commit, (iii) git-tag-only with the lock-block referencing the tag name only (no sha inside the file).
2. **mtime semantics ambiguous:** the plan says `SOURCING_PROTOCOL.md` mtime must be < the first data-row commit. File mtime on disk is NOT preserved through `git clone`; the only durable temporal-ordering check is git-commit-timestamp or git-tag-timestamp.

**Required fix.** Resolve to two-commit dance (Task 1.1 lands the protocol body; Task 1.2 lands the §0 lock-block referencing Task 1.1's commit sha + applies the git tag at Task 1.2's commit). Replace "mtime" language with "git-commit timestamp" or "git-tag exists and points to commit < first-data-commit." Wave-2 RC verifies via `git log --format=%cI` on the tagged commit vs the first data-row commit.

### FLAG-3 — MATERIAL (gitignore rule for empirical parquet)

**Issue.** Task 2.2 claims `simulations/saas_builder/data/cohort_distribution_empirical.parquet` is gitignored per repo convention (artifact NOT committed). The current `.gitignore` covers `data/*.parquet` under the repo-root `data/` directory only:

```
data/raw/
...
data/*.parquet
```

These globs are anchored at repo root (`data/...`). They do NOT match `simulations/saas_builder/data/*.parquet`. Evidence: `cohort_prior.parquet`, `IronCondor_strip.json`, `Z_cap_pinned.json` all exist IN-REPO under `simulations/saas_builder/data/` — they are tracked artifacts.

**Required fix.** EITHER (a) commit the empirical parquet to the repo (consistent with cohort_prior.parquet sibling) and treat the audit_block + sha lineage as the reproducibility anchor; OR (b) extend `.gitignore` with `simulations/saas_builder/data/cohort_distribution_empirical.parquet` explicitly and document the personal-data-redaction rationale (raw responses MAY include enough PII signal to warrant not committing). Both paths are defensible; the plan must pick one and not assume the gitignore convention covers it silently.

### FLAG-4 — NIT (Task 3.2 directory naming retains `synthetic_tau_t`)

**Issue.** Task 3.2 acknowledges `simulations/saas_builder/data/synthetic_tau_t/` retains its name post-empirical-prior-swap to avoid breaking downstream consumers. Verified:
- `cohort_4/io.py:58` consumes the path directly.
- `cohort_4/z_cap.py:11,106` references the C1 `synthetic_tau_t` panel.

So the downstream-breaking concern is real. The name-retention rationale stands. However, the plan's note says the directory will be "tracked in `prior_swap_rationale.md` for Stage-4 cleanup" — Stage-4 has no spec yet. Suggest adding a TODO marker file or `_DEPRECATED_NAME.md` sidecar inside the directory at re-emit time so future readers do not assume the name is still semantically "synthetic".

### FLAG-5 — NIT (Task 2.1 agent dispatch `Project Shepherd`)

**Issue.** Task 2.1 says "N/A for the actual outreach (this is human field work). The plan's responsibility is to require the log entries; an orchestrator agent (`Project Shepherd`) coordinates the log updates." `Project Shepherd` is not enumerated in `memory/feedback_specialized_agents_per_task.md` task-to-agent mapping (which is Abrigo-brand-side). If `Project Shepherd` does not exist in the agent catalog, this is a fictional agent dispatch.

**Required fix.** Either confirm `Project Shepherd` exists in the agent catalog, OR replace with a real cataloged agent (`Technical Writer` for log updates is the closest match), OR mark this fully N/A with explicit foreground-orchestrator rationale (foreground edits the log directly per the "shell-ops tasks" exception in `feedback_specialized_agents_per_task.md`).

---

## §3 Verified-OK claims

1. **`ZCapPinned` schema bump to v1.2 with optional `parent_audit_block`** — verified additive-compatible. The dataclass already has `sign_verdicts: tuple[...] | None = None` as the v1.1 additive field with the same pattern. v1.0 readers default `parent_audit_block` to `None`; v1.2 writers populate it. Compatible with `ZCapPinnedReader`'s pattern (json_io.py lines 79-92 show the Pydantic transient model already accepts `schema_version` as a defaulted field).
2. **`ZCapPinnedReader`/`Writer` v1.0+v1.1 support** — verified: `json_io.py:79-83` docstring explicitly says "accepts BOTH schema v1.0 (no `sign_verdicts`) AND v1.1." Extension to v1.2 is mechanical.
3. **`cohort_5_strip.StripEmitter` orchestrator-only re-run (Task 4.1)** — verified API public: `__init__.py:77,147` exports `StripEmitter`; `emit.py:197` defines the class; `assert_long_vol_signature` exported at `__init__.py:95,152`. Zero-modification re-execution is feasible.
4. **`cohort_4.io.pin_and_emit` re-emit driver (Task 3.4)** — verified: `cohort_4/io.py:250,445` defines and exports `pin_and_emit`.
5. **PSIS-LOO-CV infrastructure for Task 3.3** — verified: `cohort_3/loo.py:85,202` ships `arviz.compare(..., ic="loo", method="stacking")` and reads `ar1_log` fits; `cohort_3/_errors.py:10` closes the form-set to `{martingale, ar1_log, det_churn}`.
6. **HALT routing in §10** — verified each of the 7 triggers has a target route (revise, extend, methodology review, user-pivot, route-to-A1, CORRECTIONS-α). No orphan HALT.
7. **Pin coverage in §9 vs master-spec §5** — verified: P-A2.1 through P-A2.5 each map to a Task with HALT semantics.
8. **Anti-fishing — Task 1.1 acceptance criteria** — verified the §1–§8 listing contains no outcome-direction language (target population, channels, instrument, anti-fishing pre-pin, limitation, schedule, stop rule, audit-block-scope). No "we expect $\bar C$ to be in [X, Y]" smuggled in.
9. **Re-emission round-trip property for Task 3.4** — Hypothesis test posture is consistent with existing `simulations/tests/` discipline.

---

## §4 Verdict and disposition

**Verdict: ACCEPT_WITH_FLAGS.**

Plan author MUST land a v0.2 with the following before execution begins:

- **FLAG-1 fix (BLOCKING for execution):** §4 file-structure box + Task 3.1 / 3.2 / 3.4 path references corrected from `cohort_1/...` to actual top-level `saas_builder/...` (or a precursor Stage-2-cleanup PR that materializes `cohort_1/`).
- **FLAG-2 fix (BLOCKING for Task 1.2):** rewrite Task 1.2 as two-commit dance with git-commit-timestamp ordering, not file-mtime ordering.
- **FLAG-3 fix (BLOCKING for Task 2.2):** decide commit-the-parquet vs. extend-gitignore; record decision in the plan.
- **FLAG-4 (non-blocking):** add `_DEPRECATED_NAME.md` sidecar at re-emit time.
- **FLAG-5 (non-blocking):** confirm or replace `Project Shepherd` agent reference.

Wave-1 RC posture is satisfied that the underlying scientific scaffolding (prior swap, R5 marginalization preservation, Υ_t rank-flip safeguard scope per MQ-NIT-2, strip re-verification per MQ-FLAG-4) is correctly framed. The blockers are file-path traceability and git-workflow plumbing, not science.

This verdict is INDEPENDENT of MQ's parallel verdict per master-spec §6.1 Delphi safeguard. Convergent BLOCKs (if any) escalate to master spec per §6.4; pure file-path FLAGs land in the A2 plan's §12 CORRECTIONS-α as v0.1 → v0.2.

---

**Reviewer:** RC (Reality Checker)
**Verdict file:** `scratch/2026-05-11-stage-3-a2-rc-mq-review/rc-verdict.md`
**Word count:** ~1380.
