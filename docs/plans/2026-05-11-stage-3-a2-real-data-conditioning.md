# STAGE-3 A2 — Real-data cohort conditioning (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `memory/feedback_no_code_in_specs_or_plans.md` (NON-NEGOTIABLE), this plan does NOT contain Python code blocks. Each task dispatches a specialized agent who authors code per the functional-python skill + the Honnibal audit-pass chain.
>
> **Foreground orchestrates, never authors.** Per repo memory `memory/feedback_specialized_agents_per_task.md` (NON-NEGOTIABLE).

**Plan version:** v0.2 (Wave-1 RC+MQ ACCEPT_WITH_FLAGS — 5 FLAGs + 6 NITs disposed inline per §12.1)
**Master spec:** `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2
**Predecessor:** Stage-2 verdict memo §9 (Stage-3 readiness checklist row #1); the C1 cost-posterior code at top-level `simulations/saas_builder/{emit,model,priors,diagnostics}.py` (NOT a `cohort_1/` sub-package — corrected per RC-A2-FLAG-1, §12.1); cohort_5_strip emit (commit `3442852`)
**Status:** Wave-1 ACCEPT_WITH_FLAGS-DISPOSED — per-task execution authorized once §12.1 corrections land
**Estimated wall-time:** 3–6 weeks (sourcing is the long pole; not parallelizable beyond a small team)

---

## §0 Goal

**One sentence.** Replace the synthetic Pareto-tier cost prior in C1 with empirical $(\bar C^{P10}, \bar C^{P50}, \bar C^{P90})$ percentiles sourced via a pre-pinned DevSurvey instrument from LATAM solo AI-builders, re-fit C1 against the empirical prior, re-pin Z_cap to v1.2, re-emit the cohort_5_strip, and re-verify all strip pins under the post-K⋆-shift geometry — without smuggling any outcome-direction prediction.

## §1 Architecture

A2 is a **field-work + analytics re-fit + re-emit** track. The dominant cost is sourcing (weeks of survey deployment); the analytics-side work is mostly a prior swap (C1's marginalization, R5, stays exact per master-spec §2.2 MQ-NIT-1 disposition) plus a re-run of the existing cohort_5_strip emit driver.

The plan deliberately PRE-PINS the sourcing protocol (Phase 1) BEFORE any data is touched (master-spec Pin P-A2.1), satisfies the $N \ge 75$ floor AT EXIT (Pin P-A2.2), preserves the Stage-2 Υ_t HALT-on-rank-flip safeguard (Pin P-A2.4, scope-tightened per MQ-NIT-2), and explicitly re-verifies cohort_5_strip pins under the new K⋆ (Pin P-A2.5, MQ-FLAG-4 disposition).

## §2 Tech stack

- Python 3.13, PyMC for the C1 re-fit (mirroring `simulations/saas_builder/model.py` top-level C1 conventions).
- Survey instrument: vendor-neutral DevSurvey-style; no external service procurement in scope. Channel deployment via the channels listed in `notes/SaaS_Builders_AI_NativeBuilders.md` §"Identification strategy".
- Existing `simulations/utils/parquet_io.py` for the empirical-distribution emit.
- Existing `simulations/saas_builder/cohort_5_strip/emit.py` re-driver for the post-re-pin strip emit.

---

## §3 Cross-spec references

| Master-spec section | What this plan must satisfy |
|---------------------|-----------------------------|
| §2.2 phase 1 | Sourcing protocol PRE-PINNED before data |
| §2.2 phase 2 | Empirical percentiles, $N \ge 75$, survey-method bias acknowledged |
| §2.2 phase 3 (MQ-NIT-1 disposition) | C1 prior replacement — R5 marginalization stays analytic, only LSE prior-weights re-evaluated |
| §2.2 phase 4 (MQ-FLAG-4 disposition) | Strip-pin re-verification under post-K⋆-shift geometry |
| §5 P-A2.1 / P-A2.2 / P-A2.3 / P-A2.4 / P-A2.5 | Pin coverage per Wave-2 review |
| §6.1 Wave-1 review | This plan dispatches RC + MQ before execution |

---

## §4 File structure

```
docs/plans/2026-05-11-stage-3-a2-real-data-conditioning.md   ← THIS plan
scratch/2026-05-11-a2-devsurvey/
├── SOURCING_PROTOCOL.md                  Phase 1 PRE-PINNED instrument (timestamp < first-data)
├── channel_deployment_log.md             Phase 2 running deployment log
├── sample_audit.md                       Phase 2 sample-bias caveat record
├── prior_swap_rationale.md               Phase 3 R5-marginalization-preserved argument
└── strip_reverify_log.md                 Phase 4 re-emit + re-verification record

simulations/saas_builder/data/
├── cohort_distribution_empirical.parquet   Phase 2 emit (NEW; raw + processed survey responses)
├── cohort_prior.parquet                    Phase 3 OVERWRITE under empirical percentiles (v1.1; v1.0 = synthetic)
├── Z_cap_pinned.json                       Phase 3 OVERWRITE → schema v1.2 (adds parent_audit_block field)
└── IronCondor_strip.json                   Phase 4 OVERWRITE via re-emit (schema v1.0 unchanged)

simulations/saas_builder/{emit,model,priors,diagnostics}.py   ← READ-ONLY; A2 swaps prior, NOT model structure (top-level C1 implementation; NOT a cohort_1/ sub-package — see §12.1 RC-A2-FLAG-1)
simulations/types/posterior.py       ← Modify Z_cap_pinned schema to v1.2 (add parent_audit_block optional field)
simulations/utils/json_io.py         ← Update ZCapPinnedReader/Writer to accept v1.2

simulations/tests/
├── test_saas_cohort1_empirical_prior.py     NEW: prior-swap regression suite
└── test_z_cap_pinned_schema_v1_2.py         NEW: v1.0 / v1.1 / v1.2 reader compat
```

The C1 model (`simulations/saas_builder/model.py`, top-level) is **not modified**; only the cohort prior parquet that feeds it changes.

---

## §5 Phase 1 — Pre-pinned sourcing protocol

### Task 1.1 — Author the DevSurvey-style sourcing protocol

**Files:**
- Create: `scratch/2026-05-11-a2-devsurvey/SOURCING_PROTOCOL.md`

**Agent dispatch:** `general-purpose` agent with a research brief — read `notes/SaaS_Builders_AI_NativeBuilders.md` §"Identification strategy", `notes/PRIMITIVES.md` §4.2 calibration-sources, and Stage-2 verdict memo §7 limitation 3 (DevSurvey convenience-sampling caveat). Produce the survey protocol.

**Acceptance:**
- §1 Target population definition (solo AI-native LATAM builders, post-revenue / pre-scale; criteria for inclusion / exclusion). Pre-pinned with no outcome-direction prediction.
- §2 Channels list: Twitter/X, Discord (CELO Buildathon group, AI-dev groups, no-code communities), Telegram, Platzi ecosystem, indie-hacker LATAM groups. One row per channel with: contact, deployment date target, expected response volume, known sampling bias.
- §3 Survey instrument — questions, response options, JSON-schema for the captured response. The instrument captures at minimum: monthly USD tooling cost ($\bar C$), monthly COP revenue ($\overline\Upsilon$), commitment-stickiness self-report (annual subs vs PAYG split), tier mix (Cursor Pro / Max-5x / Max-20x / Anthropic API), location.
- §4 Anti-fishing pre-pin: $N_{\text{MIN}} = 75$ floor enforced at EXIT (not at pre-registration); rank-flip-on-Υ-LOO HALT semantic carried verbatim from Stage-2 §15.4; no outcome-direction language.
- §5 Acknowledged limitation: convenience sampling, expected over-representation of visible-online subset (mirrors Stage-2 verdict memo §7 limitation 3 wording).
- §6 Channel-deployment schedule with target dates (relative weeks from sign-off, not absolute calendar dates — wall-clock is dependent on review approval timing).
- §7 Stop rule: data collection ends when both (i) $N \ge 75$ across at least 3 channels AND (ii) any single channel does not exceed 60% of the sample.
- §8 Audit-block scope: a sha256 over the FINAL processed parquet locks downstream reproducibility (mirrors Stage-2 audit pattern).
- The file's filesystem mtime MUST be earlier than the first row of `cohort_distribution_empirical.parquet` — Pin P-A2.1 enforces this.

**Commit message:** `protocol(stage-3-a2): pre-pinned DevSurvey sourcing instrument`

---

### Task 1.2 — Pre-pin lock the SOURCING_PROTOCOL.md via two-commit dance (RC-A2-FLAG-2 disposition)

**Files:**
- Append to: `scratch/2026-05-11-a2-devsurvey/SOURCING_PROTOCOL.md` (NEW §0 lock-block referencing Task 1.1's commit sha).
- Apply git tag `a2-sourcing-pinned-2026-05-NN` to THIS task's commit.

**Agent dispatch:** N/A — orchestrator-only operation (the foreground edits the §0 lock-block + applies the tag; no specialist needed; per `memory/feedback_specialized_agents_per_task.md` shell-ops exception).

**Two-commit-dance rationale (RC-A2-FLAG-2).** The chicken-and-egg in v0.1 (the §0 lock-block referencing its own commit sha is self-referential) is resolved by splitting: Task 1.1 commits the protocol BODY (sha = `commit_A`); Task 1.2 commits the §0 lock-block referencing `commit_A` (sha = `commit_B`); the git tag `a2-sourcing-pinned-2026-05-NN` is applied to `commit_B`. The temporal-ordering anchor for Pin P-A2.1 is the GIT-COMMIT-TIMESTAMP on `commit_A` (or `commit_B` — either works; both must precede the first data-row commit), NOT file mtime (which does not survive `git clone`).

**Acceptance:**
- Tag exists in git pointing to `commit_B`.
- `commit_A`'s git-commit-timestamp (`git log -1 --format=%cI commit_A`) PRECEDES every commit timestamp that touches `simulations/saas_builder/data/cohort_distribution_empirical.parquet`. RC Wave-2 verifies via `git log --format=%cI`.
- The §0 lock-block contents in `SOURCING_PROTOCOL.md` reference `commit_A` (the body-commit sha), not `commit_B`.

**Commit message:** `lock(stage-3-a2): anchor sourcing protocol via §0 lock-block + git tag`

---

## §6 Phase 2 — Sourcing deployment + sample fit

### Task 2.1 — Deploy the survey instrument across channels

**Files:**
- Modify: `scratch/2026-05-11-a2-devsurvey/channel_deployment_log.md` (append-only running log)

**Agent dispatch:** N/A for the actual outreach (this is human field work; per `memory/feedback_specialized_agents_per_task.md` shell-ops / coordination exception). The plan's responsibility is to require the log entries; the foreground orchestrator edits the log directly (per shell-ops exception). `Project Shepherd` (in the agent catalog as a project-coordination agent) MAY be dispatched per-weekly-update for a structured log roll-up, but is not required for individual log entries. (RC-A2-FLAG-5 disposition.)

**Acceptance:**
- One log entry per channel deployment with: timestamp, channel, response count to date, sample composition (location / tier / role distribution snapshots).
- Log updates committed weekly (small, frequent commits per CLAUDE.md style).
- No analysis or summary statistics in the log — raw counts only. Analysis happens at Phase 2 Task 2.3.

**Commit message style:** `survey(stage-3-a2): channel deployment log — week NN`

---

### Task 2.2 — Land raw + processed responses to parquet

**Files:**
- Create: `simulations/saas_builder/data/cohort_distribution_empirical.parquet` (Hive-partitioned by channel; `simulations/saas_builder/data/` is gitignored at `.gitignore:53` covering this entire directory and matching the sibling artifacts `cohort_prior.parquet`, `Z_cap_pinned.json`, `IronCondor_strip.json`; the parquet is reproducible-from-raw-responses + audit-block-pinned and NOT committed — RC-A2-FLAG-3 disposition: gitignore decision is COMMIT-NOTHING-EXTEND-NOTHING because the existing rule covers it)
- Create: `simulations/saas_builder/cohort_1_empirical/` (NEW thin sub-package under cohort_1's umbrella) with `io.py` IO Boundary that reads raw CSV / JSON responses into the parquet.

**Agent dispatch:** `Data Engineer` agent — read `simulations/utils/parquet_io.py` conventions; author the IO Boundary class that lands raw responses into a hive-partitioned parquet with a deterministic audit_block.

**Acceptance:**
- New sub-package `simulations/saas_builder/cohort_1_empirical/` has three-tier discipline (Value / Callable / IO Boundary).
- `EmpiricalResponseLoader` IO Boundary class with `__init__` + `__call__(raw_response_paths: tuple[Path, ...]) -> Path` returning the parquet emit path.
- Schema for the parquet: one row per respondent; columns `(respondent_id_hash, channel, c_bar_usd_per_month, upsilon_cop_per_month, stickiness_fraction, tier_mix_self_report, location, response_timestamp)`.
- Personal data redacted: `respondent_id_hash` is a sha256 of the original respondent identifier; raw identifiers are NOT stored in the repo.
- `audit_block` for the parquet computed via the shipped `simulations/utils/audit_block.py::compute_audit_block`.

**Commit message:** `data(stage-3-a2): empirical response loader + parquet schema`

---

### Task 2.3 — Compute empirical percentile prior

**Files:**
- Create: `simulations/saas_builder/cohort_1_empirical/percentile_estimator.py` (Callable tier)
- Modify: `scratch/2026-05-11-a2-devsurvey/sample_audit.md` (add §"Sample size + bias audit" with N counts, channel-mix table, anchor citations)

**Agent dispatch:** `Senior Developer` + `Data Engineer` (paired for the percentile derivation + the sample audit doc).

**Acceptance:**
- `PercentileEstimator` frozen-dc with `__call__(empirical_parquet_path: Path) -> CohortPercentileTriple(c_p10, c_p50, c_p90)`.
- **Pre-pinned CI method (MQ-A2-5 disposition):** BCa (bias-corrected accelerated) bootstrap with 10,000 resamples for the P10 and P90 tail percentiles (where ordinary bootstrap is biased at small $N$); ordinary bootstrap with 10,000 resamples for the P50 median. The choice MUST be pinned in `SOURCING_PROTOCOL.md` §3 BEFORE any data lands (anti-fishing: locking the CI method ex-post would be an anti-fishing pattern). NOT a point estimate alone — mirrors Stage-2's CI-width gate posture.
- `sample_audit.md` reports: total $N$, per-channel $N_c$, max-channel-share fraction (must be $\le 0.60$ per Phase-1 stop rule), location distribution, tier-mix distribution. Survey-method bias caveat carried forward from SOURCING_PROTOCOL.md §5.
- HALT condition: $N < 75$ OR max-channel-share > 0.60 → HALT; route to channel-deployment extension.

**Commit message:** `feat(stage-3-a2): PercentileEstimator + sample audit`

---

## §7 Phase 3 — C1 prior swap + Z_cap re-pin

### Task 3.1 — Land empirical prior into cohort_prior.parquet

**Files:**
- Modify: `simulations/saas_builder/data/cohort_prior.parquet` (OVERWRITE — bump schema version row from v1.0 synthetic to v1.1 empirical)

**Agent dispatch:** `Data Engineer` — read `simulations/saas_builder/emit.py` (where `cohort_prior.parquet` is originally written; top-level C1 location, NOT `cohort_1/emit.py`) and `simulations/saas_builder/priors.py` (prior-hyperparameter conventions). Produce a one-shot script that consumes `cohort_distribution_empirical.parquet` + the `CohortPercentileTriple` and overwrites `cohort_prior.parquet` with the empirical version.

**Acceptance:**
- New `cohort_prior.parquet` carries empirical percentile triple in its prior fields; v1.0 synthetic Pareto fields are zeroed and the schema-version field is bumped to v1.1.
- A `parent_audit_block` field is added at the parquet metadata level pointing to v1.0 synthetic.
- Round-trip test: existing `simulations.saas_builder.priors` Reader loads v1.1 without breakage (the schema bump is additive at the metadata layer, not the row schema).

**Commit message:** `data(stage-3-a2): empirical cohort_prior.parquet schema v1.1 (overwrites synthetic v1.0)`

---

### Task 3.2 — Re-fit C1 against the empirical prior

**Files:**
- Modify: `simulations/saas_builder/` top-level C1 re-fit driver (existing entry point at `simulations/saas_builder/emit.py::CohortEmitter`; NOT `cohort_1/emit.py` — RC-A2-FLAG-1 path correction)
- Create: `scratch/2026-05-11-a2-devsurvey/prior_swap_rationale.md` (MQ-NIT-1 disposition record)

**Agent dispatch:** `AI Engineer` (PyMC-trained agent; cohort-1 model is PyMC) + `Reality Checker` for the diagnostic gate verification.

**Acceptance:**
- The C1 `pm.sample` re-runs against the empirical-prior `cohort_prior.parquet`, emitting a refreshed `simulations/saas_builder/data/synthetic_tau_t/` Hive-partitioned parquet (NOTE: the directory name carries `synthetic_` from Stage-2; A2 does NOT rename it to avoid breaking downstream consumers — the contents are now empirical-prior-conditioned, the name is a legacy artifact tracked in `prior_swap_rationale.md` for Stage-4 cleanup).
- `_AUDIT.json` re-emitted with the new diagnostic snapshot. Pin P-A2.3 thresholds enforced:
  - `rhat_max` < 1.01
  - `ess_bulk_min` ≥ 1000
  - `ess_tail_min` ≥ 1000
  - `divergence_frac` = 0.0
  - `ci_width_ratio_max` ≤ 1.10
- HALT if any threshold fails — route to methodology review (probably an N_draws bump per the Stage-2 §4.1 path-α precedent).
- `prior_swap_rationale.md` explicitly notes (per MQ-NIT-1): "R5 (STAGE_2_RESULTS.md §2.5) marginalization carries through unchanged — the discrete-latent sum-out is analytic; only the LSE prior-weights $P(\text{tier}_i, n_d, n_m)$ are re-evaluated against the empirical $\bar C$ percentiles."

**Commit message:** `feat(stage-3-a2): C1 re-fit posterior under empirical prior + diagnostic re-PASS`

---

### Task 3.3 — Υ_t rank-flip safeguard re-evaluation

**Files:**
- Modify: `simulations/saas_builder/cohort_3/` PSIS-LOO-CV re-run driver
- Modify: `simulations/saas_builder/data/revenue_form_verdict.json` (OVERWRITE with re-evaluated ranking)
- Append to: `scratch/2026-05-11-a2-devsurvey/prior_swap_rationale.md` (§"Pin P-A2.4 — Υ_t rank-flip safeguard outcome")

**Agent dispatch:** `AI Engineer` + `Reality Checker`.

**Acceptance:**
- PSIS-LOO-CV re-run on the post-A2-re-fit C1 posterior + the Stage-2 C3 Υ_t-form candidates (martingale, AR(1)-log, det+churn).
- HALT if `winning_form != "ar1_log"` OR `ranked_forms[1] != "det_churn"` OR the Stage-2 INDISTINGUISHABLE-verdict-band crossing flips (e.g., the post-empirical-prior verdict moves from INDISTINGUISHABLE to {WEAK, MARGINAL, PASS, FAIL} per spec v1.2.1 §9 verdict-band semantic) — disposition memo, route to user-enumerated pivot per Stage-2 §15.4. (MQ-A2-2 disposition: v0.1's HALT was strictly weaker than Stage-2 §15.4 — caught rank flips but missed verdict-band crossings; v0.2 tightens.)
- Per MQ-NIT-2: this safeguard scope is Υ_t-LOO ranking ONLY, NOT cost-prior ranking. The rationale document MUST state this verbatim.

**Commit message:** `verify(stage-3-a2): Υ_t LOO rank-flip safeguard re-PASS under empirical prior`

---

### Task 3.4 — Z_cap v1.2 re-pin + schema bump

**Files:**
- Modify: `simulations/types/posterior.py` — extend `ZCapPinned` with optional `parent_audit_block: str | None` field (schema v1.0 / v1.1 / v1.2 compat).
- Modify: `simulations/utils/json_io.py` — `ZCapPinnedReader` and `ZCapPinnedWriter` accept v1.2 with the new field; v1.1 and v1.0 readers remain backward-compat.
- Modify: `simulations/saas_builder/data/Z_cap_pinned.json` — OVERWRITE via cohort_4 re-emit at new K⋆ derived from refreshed C1.

**Agent dispatch:** `Senior Developer` (types-tier extension) + `AI Engineer` (cohort_4 re-emit driver).

**Acceptance:**
- `ZCapPinned.parent_audit_block` is optional at the dataclass level; v1.0 / v1.1 readers default it to `None`; v1.2 writers populate it with the Stage-2 v1.1 audit `1fb1f7a4…5d31` (master spec §1.3).
- Hypothesis property test: round-trip `ZCapPinnedReader → ZCapPinned → ZCapPinnedWriter → ZCapPinnedReader` preserves all v1.2 fields.
- New `Z_cap_pinned.json` emitted via re-run of `simulations.saas_builder.cohort_4.io.pin_and_emit` against the refreshed C1 posterior; `audit_block` and `parent_audit_block` both populated.
- Existing `simulations/tests/test_saas_cohort4.py` re-runs green; if it fails because of schema-bump conventions, route to a v1.2 reader compatibility test.

**Commit message:** `feat(types/posterior): ZCapPinned schema v1.2 (parent_audit_block) + Z_cap re-pin at empirical K⋆`

---

## §8 Phase 4 — Strip pin re-verification (MQ-FLAG-4 disposition)

### Task 4.1 — Re-emit cohort_5_strip against the new K⋆

**Files:**
- Modify: `simulations/saas_builder/data/IronCondor_strip.json` (OVERWRITE via `cohort_5_strip.StripEmitter()`).
- Modify: `simulations/saas_builder/data/IronCondor_strip.STRIKES.md` (re-emitted sidecar).

**Agent dispatch:** N/A — orchestrator runs `simulations.saas_builder.cohort_5_strip.StripEmitter()` directly (zero-modification re-execution of the shipped emit driver).

**Acceptance:**
- New `IronCondor_strip.json` schema_version remains "v1.0" (unchanged).
- New `audit_block` differs from `94150326…` (the Stage-2-fixture audit) because the K⋆ input shifted; this is the EXPECTED behavior of Pin S8 (audit-block lineage).
- The new audit_block + the parent Z_cap v1.2 audit_block are both surfaced in `strip_reverify_log.md`.

**Commit message:** `data(stage-3-a2): cohort_5_strip re-emit at empirical K⋆`

---

### Task 4.2 — Re-run CarrMadanEnvelopeVerifier on the new strip

**Files:**
- Create: `scratch/2026-05-11-a2-devsurvey/strip_reverify_log.md`

**Agent dispatch:** `Senior Developer` + `Reality Checker`.

**Acceptance:**
- The log records: old audit_block (`94150326…`), new audit_block, old `max_relative_error`, new `max_relative_error`, both `passes` verdicts.
- Pin S6 envelope still PASSES at the cohort_5_strip's pinned 35% tolerance.
- If FAIL, HALT and route to A1 — geometry re-tune is a strategy-level concern, not an A2 re-emit concern.

**Commit message:** `verify(stage-3-a2): CarrMadanEnvelopeVerifier re-PASS on post-K⋆ strip`

---

### Task 4.3 — Re-run assert_long_vol_signature on the new strip

**Files:**
- Modify: `scratch/2026-05-11-a2-devsurvey/strip_reverify_log.md` (append §"Pin S5 re-verification")

**Agent dispatch:** N/A — orchestrator runs `simulations.saas_builder.cohort_5_strip.assert_long_vol_signature(strip)` and records the outcome.

**Acceptance:**
- Pin S5 (long-vol signature) re-PASSES — `Π_strip(S_0) ≡ 0` strict, `Π_strip(S_0·e^{±δ_inner}) > 0`.
- If FAIL, HALT and route to A1 (the tiled-body convention does not survive the new K⋆ — strategy re-tune required).
- The 26 cohort_5_strip tests re-run green against the new artifact.

**Commit message:** `verify(stage-3-a2): assert_long_vol_signature re-PASS on post-K⋆ strip`

---

## §9 Pin coverage (per master spec §5)

| Pin | This plan's coverage |
|-----|-----------------------|
| P-A2.1 (sourcing protocol pre-pinned) | Task 1.1 + Task 1.2 emit + git-tag SOURCING_PROTOCOL.md; RC Wave-2 verifies the commit timestamp predates the first data-row commit. |
| P-A2.2 (N ≥ 75 at exit) | Task 2.3 sample audit reports N; HALT if N < 75. |
| P-A2.3 (C1 diagnostic gates re-PASS) | Task 3.2 enforces the 5 gates; HALT if any fails. |
| P-A2.4 (Υ_t rank-flip safeguard armed) | Task 3.3 re-runs LOO; HALT on flip. Scope tightened to Υ_t only per MQ-NIT-2. |
| P-A2.5 (strip pin re-verification) | Tasks 4.2 + 4.3 re-run envelope + long-vol signature; HALT-and-route-to-A1 on failure. |

## §10 HALT routing

| Trigger | Route |
|---------|-------|
| Task 1.1 protocol contains outcome-direction language | HALT — RC Wave-1 catches this; revise to deliverable-existence only. |
| Task 2.3 N < 75 OR max-channel-share > 0.60 | HALT — extend deployment; re-evaluate at next sample audit. |
| Task 3.2 C1 diagnostics fail Pin P-A2.3 thresholds | HALT — N_draws bump or methodology review. |
| Task 3.3 Υ_t LOO ranking flips against det+churn | HALT — disposition memo, user-enumerated pivot per Stage-2 §15.4. |
| Task 4.2 envelope re-verification FAILS | HALT — route to A1 (geometry / strategy re-tune). |
| Task 4.3 long-vol signature re-verification FAILS | HALT — route to A1 (tiled-body convention broken under new K⋆). |
| Wave-1 or Wave-2 RC+MQ on this plan returns BLOCK | HALT per master-spec §6.1; CORRECTIONS-α landed in this plan's §12. |

## §11 Artifacts emitted

| Artifact | Phase | Schema | Lineage parent |
|----------|-------|--------|-----------------|
| `scratch/2026-05-11-a2-devsurvey/SOURCING_PROTOCOL.md` | 1 | markdown + git-tag anchor | (none — first pre-pin) |
| `scratch/2026-05-11-a2-devsurvey/{channel_deployment_log,sample_audit,prior_swap_rationale,strip_reverify_log}.md` | 2/3/4 | markdown | SOURCING_PROTOCOL.md sha |
| `simulations/saas_builder/data/cohort_distribution_empirical.parquet` | 2 | new (Hive-partitioned by channel) | sha over raw responses |
| `simulations/saas_builder/data/cohort_prior.parquet` | 3 | v1.1 (overwrites v1.0 synthetic) | parent metadata field → v1.0 audit |
| `simulations/saas_builder/data/synthetic_tau_t/` | 3 | (unchanged schema; re-emitted contents) | cohort_prior.parquet v1.1 audit |
| `simulations/saas_builder/data/Z_cap_pinned.json` v1.2 | 3 | v1.2 (adds parent_audit_block) | Stage-2 v1.1 audit (`1fb1f7a4…5d31`) |
| `simulations/saas_builder/data/IronCondor_strip.json` re-emit | 4 | v1.0 (unchanged) | Z_cap v1.2 audit |
| `simulations/types/posterior.py` / `simulations/utils/json_io.py` | 3 | code | (additive schema bump) |

## §12 CORRECTIONS-α (patch log)

### §12.1 v0.1 → v0.2 (Wave-1 RC+MQ disposition)

**Wave-1 review verdict:** RC ACCEPT_WITH_FLAGS + MQ APPROVE-WITH-NITS (2026-05-11). 0 BLOCKs. Verdict files:
- `scratch/2026-05-11-stage-3-a2-rc-mq-review/rc-verdict.md`
- `scratch/2026-05-11-stage-3-a2-rc-mq-review/mq-verdict.md`

| Finding | Severity | Disposition | Location |
|---------|----------|-------------|----------|
| RC-A2-FLAG-1 | Material (BLOCKING-for-execution) | All `simulations/saas_builder/cohort_1/` references corrected to top-level `simulations/saas_builder/{emit,model,priors,diagnostics}.py`. C1 was never namespaced. 12+ occurrences updated. | §4 file structure, Task 3.1, Task 3.2 |
| RC-A2-FLAG-2 | Material (BLOCKING-Task-1.2) | Task 1.2 rewritten as a two-commit dance: Task 1.1 commits the body (`commit_A`); Task 1.2 appends the §0 lock-block referencing `commit_A` and applies the git tag to `commit_B`. Temporal-ordering anchor is git-commit-timestamp, NOT file mtime (which doesn't survive `git clone`). | Task 1.2 |
| RC-A2-FLAG-3 | Material (gitignore decision) | Verified `.gitignore:53` covers `simulations/saas_builder/data/` (full directory), so the empirical parquet inherits gitignore correctly. Plan now cites `.gitignore:53` explicitly. RC's earlier reading was based on `data/*.parquet` rule alone; the full-directory rule resolves the question. Decision: COMMIT-NOTHING-EXTEND-NOTHING. | Task 2.2 |
| RC-A2-FLAG-4 | NIT | Add `_DEPRECATED_NAME.md` sidecar to `simulations/saas_builder/data/synthetic_tau_t/` at Task 3.2 re-emit time (one-line file noting Stage-4 cleanup will rename). | Task 3.2 acceptance |
| RC-A2-FLAG-5 | NIT | `Project Shepherd` confirmed as a cataloged agent (project-coordination role); v0.2 clarifies that for individual log entries the foreground edits directly (shell-ops exception per `memory/feedback_specialized_agents_per_task.md`), and Project Shepherd is reserved for structured weekly roll-ups. | Task 2.1 |
| MQ-A2-1 | Cosmetic-but-load-bearing | `prior_swap_rationale.md` must explicitly state "no per-tier $\theta_k$ in A2; per-tier differentiation deferred to second-wave (STAGE_2_RESULTS.md §5 open item 3)." Prevents silent scope creep at re-fit time. | Task 3.2 acceptance |
| MQ-A2-2 | Material | Task 3.3 HALT condition tightened to also catch verdict-band crossings (INDISTINGUISHABLE → {WEAK, MARGINAL, PASS, FAIL}) per spec v1.2.1 §9 semantic. v0.1 captured only rank-order flips. | Task 3.3 |
| MQ-A2-3 | Cosmetic | `prior_swap_rationale.md` states the spec gates ($r̂ < 1.01$, ESS_bulk ≥ 1000, divergence_frac = 0.0, ci_width_ratio_max ≤ 1.10) are LOAD-BEARING; if `simulations/saas_builder/diagnostics.py` carries looser code-level defaults, the spec gates override. | Task 3.2 acceptance |
| MQ-A2-4 | Cosmetic | Acknowledge cohort_5_strip Pin S6 docstring drift fix (35%, not 5%) per master-spec §9.2 ticket — already landed in commit `78841b1`. No further action in A2. | (informational) |
| MQ-A2-5 | Material if $N \approx 75$ | Bootstrap variant pre-pinned in SOURCING_PROTOCOL.md §3: BCa (10,000 resamples) for P10/P90 tails; ordinary bootstrap (10,000 resamples) for P50. Locks CI method ex-ante per anti-fishing. | Task 1.1 §3 + Task 2.3 acceptance |
| MQ-A2-6 | Workflow | A1↔A2 wall-time interleaving — deferred to operator scheduling discretion; master-spec §3 dependency graph already covers A1↔B1 soft dep, and A2's strip re-verification (Phase 4) would catch any A1-driven strategy swap retroactively. No spec change. | (operational) |

### §12.2 Wave-2 (post-execution) review reserve

Wave-2 RC+MQ on this plan's exit deliverables lands its own block at §12.3.

## §13 References

- `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2 — master spec (§2.2 for this plan).
- `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` — Stage-2 spec; §15.4 Υ_t HALT-on-flip semantic.
- `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md` — §4.1 C1 marginalization detail; §7 limitation 3 sampling caveat.
- `notes/STAGE_2_RESULTS.md` §2.5 — R5 marginalization analytic-form proof (MQ-NIT-1 anchor).
- `notes/SaaS_Builders_AI_NativeBuilders.md` §"Identification strategy" — A2 sourcing channels.
- `notes/PRIMITIVES.md` §4.2 — calibration sources.
- `simulations/saas_builder/{emit,model,priors,diagnostics}.py` (top-level) — read-only consumer of `cohort_prior.parquet`.
- `simulations/saas_builder/cohort_4/io.py::pin_and_emit` — Z_cap re-emit driver.
- `simulations/saas_builder/cohort_5_strip/emit.py::StripEmitter` — strip re-emit driver.
- `memory/feedback_no_code_in_specs_or_plans.md` / `memory/feedback_specialized_agents_per_task.md` — orchestration conventions.

---

*End of A2 plan v0.1. Wave-1 RC+MQ review dispatch before any task execution.*
