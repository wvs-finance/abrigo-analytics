---
spec_id: r6-continuous-stream-simulation
spec_version: 0.1.3
created: 2026-05-16
status: APPROVED for plan emission — v0.1.3 polishes NITs from v0.1.2 closure-only review; all three review channels approve
v0_1_0_status: NEEDS_WORK (Wave 1 RC 6 BLOCKs by empirical verification; Wave 2 Model QA 3 BLOCKs pinning; Wave 2 Code Reviewer 3 BLOCKs interface); reports in scratch/2026-05-16-r6-spec-review/
v0_1_1_status: PARTIAL_CLOSE (Wave 1 RC 2 NEW_BLOCKs — weekly-cap unpinnable from Anthropic source; pool sort-key non-unique on real data). Wave 2 Model QA CLOSE_ALL. Wave 2 Code Reviewer PARTIAL_CLOSE (1 editorial NIT-A). Reports at scratch/2026-05-16-r6-spec-review/*_v0_1_1.md
sibling_spec: docs/specs/2026-05-16-ai-cost-factor-model-design.md (R5 + R4-S3, v0.2.1 CLOSE_ALL by all three reviewers)
sibling_corrections_v0_2_1_plan:
  - errors-hierarchy rename — JSONLSchemaError(SchemaMismatchError) → JSONLSchemaError(DevAICostError) with DevAICostError(Exception) as new sub-package root; implementation-time-only, documented in §0.1 CORRECTIONS-AA below; reflected in the v0.2.1 plan at plan-execution time
  - MessageRecord uuid field — add `uuid: str` to MessageRecord frozen-dc; ensure JSONLReader captures Anthropic's per-line uuid field during parsing; required by R6's CORRECTIONS-RR canonicalization (uuid tertiary sort key + tiebreaker per CORRECTIONS-TT below); implementation-time-only; documented in §0.2 CORRECTIONS-RR and verified by Wave 1 RC v0.1.2 closure (v0.2.1 spec §3.5 line 621 does not currently list uuid)
parent_iteration_pin: dev-AI-cost iteration (parent CLAUDE.md "Abrigo Operating Framework")
iteration_directory: notebooks/dev_ai_cost_v2_r6/
relationship_to_v0_2_1: complementary — R5 quantifies cost-risk reduction; R6 quantifies capacity unblocking (dual hedge value)
review_protocol: feedback_two_wave_doc_verification (Wave 1 = Reality Checker; Wave 2 = Model QA Specialist + Code Reviewer in parallel)
verifier_v0_1_0_wave1: NEEDS_WORK — 6 BLOCKs (scratch/2026-05-16-r6-spec-review/wave1_reality_checker.md). Empirical verification on 63,478 messages / 33 distinct days. Triggered feedback_pathological_halt_anti_fishing_checkpoint.
verifier_v0_1_0_wave2_model_qa: NEEDS_WORK — 3 BLOCKs (scratch/2026-05-16-r6-spec-review/wave2_model_qa.md). "Core stack is sound; BLOCKs are amendments to pinning discipline, not model structure."
verifier_v0_1_0_wave2_code_reviewer: NEEDS_WORK — 3 BLOCKs (scratch/2026-05-16-r6-spec-review/wave2_code_reviewer.md). Signature/envelope pins, not architectural defects.
verifier_v0_1_1_wave1: PARTIAL_CLOSE — 5 of 6 v0.1.0 BLOCKs closed; 2 NEW_BLOCKs (4a unpinnable weekly-cap value; 8a sort-key non-unique). scratch/2026-05-16-r6-spec-review/wave1_reality_checker_v0_1_1.md
verifier_v0_1_1_wave2_model_qa: CLOSE_ALL — all 3 BLOCKs + 5 FLAGs closed; plan-emission approved on Model QA channel. scratch/2026-05-16-r6-spec-review/wave2_model_qa_v0_1_1.md
verifier_v0_1_1_wave2_code_reviewer: PARTIAL_CLOSE — all 3 BLOCKs + FLAGs closed; 1 editorial NIT-A (CORRECTIONS-EE "verbatim" overstatement). Plan-emission approved on Code Reviewer channel. scratch/2026-05-16-r6-spec-review/wave2_code_reviewer_v0_1_1.md
verifier_v0_1_2_wave1: CLOSE_ALL — both v0.1.1 NEW_BLOCKs (4a + 8a) closed; plan-emission approved on RC channel; 1 non-blocking NIT-B (stale doc, now fixed in v0.1.3). scratch/2026-05-16-r6-spec-review/wave1_reality_checker_v0_1_2.md
verifier_v0_1_2_wave2_model_qa: not required (CLOSE_ALL at v0.1.1; v0.1.2 changes do not touch Model QA's findings)
verifier_v0_1_2_wave2_code_reviewer: PARTIAL_CLOSE — all v0.1.1 BLOCKs closed; plan-emission approved; 2 non-blocking NITs (NIT-B stale doc; NIT-C canonicalization edge cases — both now fixed in v0.1.3). scratch/2026-05-16-r6-spec-review/wave2_code_reviewer_v0_1_2.md
v0_1_3_review_status: no review required — v0.1.3 changes are documentation-only NIT cleanup explicitly classified non-blocking by reviewers in v0.1.2 reports
plan_emission_blocked_until: not blocked — APPROVED on all three channels
related_skills:
  - structural-econometrics
  - structural-estimation
  - functional-python
  - hypothesis-tests
  - latex-econ-model
  - audit-econ
reuses_from_v0_2_1:
  - JSONLReader (utils tier; reads ~/.claude/projects/**/*.jsonl) — NOTE: v0.1.1 removes the v0.1.0 is_cap_reset extension (Pivot 2 makes it unnecessary)
  - MessageRecord, TokensByCategory, DailyNotionalPanel (types) — UNCHANGED
  - PricingTable (modules; LiteLLM commit SHA e58a561caa21169fb02174148444c08509ce7028) — UNCHANGED
  - JSONLSchemaError (simulations/dev_ai_cost_v2/_errors.py) — reparented to DevAICostError per CORRECTIONS-AA
  - Banrep daily TRM panel (from extended fetch_banrep.py) — UNCHANGED
---

# R6 — Continuous-Stream Simulation for Dual Hedge-Value Quantification

## 0. v0.1.0 → v0.1.1 CORRECTIONS

The v0.1.0 spec was reviewed by all three reviewers and returned NEEDS_WORK
with 12 total BLOCKs. Reality Checker's six BLOCKs emerged from direct
empirical verification against the maintainer's `~/.claude/projects/` JSONL
data (63,478 messages, 33 distinct calendar days), invoking
`feedback_pathological_halt_anti_fishing_checkpoint` — *"spec was finalized
without running the heuristic against the data."* v0.1.1 integrates every
finding via the CORRECTIONS itemized below.

### 0.1 CORRECTIONS itemized

**CORRECTIONS-AA (Errors hierarchy — Code Reviewer BLOCK F8; depends on
v0.2.1 implementation-time amendment).** v0.1.0 referenced
`_errors.DevAICostError` as the parent of `NHPPCalibrationError` and
`SparseHourFallbackError`, but v0.2.1 §3.5 only declares
`JSONLSchemaError(SchemaMismatchError)` with no sub-package root.
v0.1.1 introduces **`DevAICostError(Exception)`** as the sub-package root
in `simulations/dev_ai_cost_v2/_errors.py`; reparents
`JSONLSchemaError` to inherit from `DevAICostError` rather than
`SchemaMismatchError`; declares the new R6 errors as direct subclasses.
This change is implementation-time-only (v0.2.1's design CLOSE_ALL stands;
the rename is a plan-execution detail) and is logged in the v0.2.1 plan as
the very first amendment task.

**CORRECTIONS-BB (NHPP grid coarsening — RC BLOCK 1; Model QA BLOCK 2).**
v0.1.0's 24-hour × 7-day-of-week (168-cell) grid was not identified at
$T = 33$ days: RC's empirical count found 37 empty bins (22%) plus 15
sparse bins (<20 obs). v0.1.1 coarsens to a **4 hour-blocks × 2 day-types
= 8-cell grid**:

- Hour-blocks: morning [06:00, 12:00), afternoon [12:00, 18:00),
  evening [18:00, 22:00), night [22:00, 06:00)
- Day-types: weekday {Mon, Tue, Wed, Thu, Fri}, weekend {Sat, Sun}

At $T = 33$ days × 24 hours ÷ 4 hour-blocks ≈ 200 hour-block observations
per day-type, each cell receives several hundred to several thousand
arrivals — well above the Model QA $N_{\min} = 5$ threshold. The
`NHPPSparseBinError` from v0.1.0 §3.5 is removed (no longer reachable
under the coarsened grid; HALT for any cell with $< 50$ observations
remains as a safety net).

**CORRECTIONS-CC (Cap-reset detection abandoned; session_id used directly
— RC BLOCKs 2 & 3; Code Reviewer BLOCK 2).** v0.1.0's cap-reset heuristic
(gap > 3h AND prior 30min ≥ 5 calls) flagged 61 events on real data, only
13% in the 4–7h plausible cap-reset window; 41% were overnight/weekend
false positives (longest = 77h). RC also verified no JSONL-level cap-hit
signals exist (zero `rate_limit` / `usage_limit_exceeded` strings across
1,680 JSONL files; supersession rule was inert).

v0.1.1 **drops the cap-reset heuristic entirely** and uses
**`MessageRecord.session_id`** (already in v0.2.1 §3.5 schema) for
calibration. NHPP is fit on **within-session inter-arrival times only**;
inter-session gaps are treated as exogenous breaks not modeled by the
arrival process. Sessions encode whatever combination of cap, sleep,
lunch, etc. caused the break — these are out of scope for the arrival
process itself.

For simulation, R6 generates **within-session arrival streams** via NHPP,
then composes them using bootstrap-sampled session-start-times and
session-length distributions from observed data.

The `is_cap_reset` field on `MessageRecord` from v0.1.0 §3.4 is
**removed**; the `extra="forbid"` Pydantic schema conflict (Code Reviewer
BLOCK 2 / RC BLOCK 7) becomes moot.

**CORRECTIONS-DD (Anthropic cap policy corrected — RC BLOCK 4).** v0.1.0
asserted a "rolling 5-hour window" cap rule. Per Anthropic docs
(<https://support.claude.com/en/articles/8325606>, accessed 2026-05-16),
the cap is **session-based, resetting every 5 hours from session start**,
NOT rolling. AND there is a **separate weekly cap** v0.1.0 entirely
omitted. The weekly cap is the dominant binding constraint at extrapolation
rates $k \in \{2, 3, 5\}$.

v0.1.1 cap-wait counter (§3.3) implements **both** caps:

- **Session cap**: session length truncated at 5h from session start;
  excess time counts as cap-wait
- **Weekly cap**: weekly aggregate session-time cap, pre-pinned at the
  Anthropic Pro plan published value with source URL + access date in
  provenance (§5.4); excess time counts as cap-wait

Implementation detail: pre-pinned weekly-cap-hours value is treated as a
declarative constant in `simulations/dev_ai_cost_v2/_anthropic_caps.py`
with a comment block citing the Anthropic source URL + access date. If
Anthropic changes the published value, this constitutes a schema-drift
event requiring spec update.

**CORRECTIONS-EE (NHPPArrivalGenerator signature realigned with
`stochastic_fx` precedent — Code Reviewer BLOCK 1).** v0.1.0's
`NHPPArrivalGenerator.__call__(k, horizon_days, rng_seed, n_paths)` broke
the canonical `simulations/stochastic_fx/generators.GBMPathGenerator`
pattern, which uses `__call__(rng_seed, n_paths)` with all bit-exactness
parameters on the frozen-dc `params`. v0.1.1 moves `k` and `horizon_days`
onto a new frozen-dc `NHPPSimulationConfig` that wraps `NHPPParameters` —
mirroring `GBMPathGenerator` verbatim. The `__call__` signature becomes
`__call__(rng_seed, n_paths) -> ArrivalEnsemble`, and the `audit_block`
recipe captures every bit-exactness parameter (including `k` and
`horizon_days`) through the standard `_compute_audit_block` envelope from
`stochastic_fx`.

**CORRECTIONS-FF (`audit_block` envelope completion — RC BLOCK 8; Code
Reviewer BLOCK 3).** v0.1.0 §5.3 identified the message pool by
`record_count + date_window`. Both reviewers flagged this as insufficient:
two `Sequence[MessageRecord]` instances can share count and window but
differ in content. v0.1.1 adds:

- `message_pool_content_sha256`: SHA-256 over canonical-sorted message
  pool. Canonicalization: sort by `(ts, request_id, session_id)`;
  serialize each `MessageRecord` via `dataclasses.asdict` then
  `canonical_json`; concatenate; hash.
- `parser_version_sha`: own-parser module git SHA at simulation time.

**CORRECTIONS-GG (Hour-block × day-type indexing for whole-message
bootstrap — Model QA FLAG 4).** v0.1.0 §2.4 indexed the bootstrap pool by
hour-of-day only, losing day-type structure that affects token-size
distribution (e.g., weekend ≠ weekday task mix). v0.1.1 indexes by
**(hour-block, day-type) = (4 × 2) = 8 cells**, matching the NHPP grid
(CORRECTIONS-BB). Sparse-cell fallback rule pre-pinned: if $|\mathcal{P}|
< 50$, expand to the cell's day-type marginal pool; if still $< 50$, raise
`SparsePoolError`. The cap-wait simulation HALT threshold is updated
accordingly (§2.7).

**CORRECTIONS-HH (Reconciliation HALT threshold derivation — Model QA
BLOCK 10).** v0.1.0's 5% reconciliation-drift threshold was unrationalized.
Model QA estimated expected drift under correct calibration as < 1% given
$N_{\text{pool}} \sim 1500$ and $M = 10{,}000$. v0.1.1 **tightens to 1%**
with a derivation cell in `01_nhpp_eda.ipynb` that runs the simulation at
$k = 1$ on the calibration data and reports the empirical drift before
running the production sizing curve.

**CORRECTIONS-II (Output-quality flags — Model QA FLAG 9).** v0.1.0 had
no PASS/FAIL verdict but lacked explicit output-quality gates for the
M-design step. v0.1.1 adds **`R6Output.quality_flags: frozenset[str]`**
populated at simulation time:

- `"sparse_cell_fallback_rate_high"` — set if > 10% of arrivals trigger
  sparse-cell fallback (CORRECTIONS-GG)
- `"reconciliation_drift_high"` — set if drift on $k = 1$ mean exceeds 1%
  (CORRECTIONS-HH)
- `"nhpp_convergence_marginal"` — set if MLE converged with
  $|\Delta \log L| / |\log L| > 10^{-4}$ at final iteration
- `"weekly_cap_dominates"` — set if weekly cap is the binding constraint
  for $> 50\%$ of simulated paths at this $k$

M-design step is contractually bound to inspect `quality_flags` before
consuming R6 outputs; downstream documentation cites which flags are
disqualifying.

**CORRECTIONS-JJ (Per-module `audit_block` recipes — Code Reviewer FLAG 4).**
v0.1.0 only specified a top-level `audit_block` envelope. v0.1.1 adds
per-module `audit_block` emissions on `NHPPArrivalGenerator`,
`FXBlockBootstrapGenerator`, and `simulate_cost_trajectories`, each
capturing that module's own parameter contribution. The top-level
envelope (§5.3) chains the per-module hashes.

**CORRECTIONS-KK (`cop_costs` precision boundary — Code Reviewer FLAG 6).**
v0.1.0's `CostTrajectoryEnsemble.cop_costs: NDArray[float64]` regressed
from v0.2.1's Decimal contract. v0.1.1 documents this as the
**ensemble-vs-headline precision boundary**: `cop_costs` is `float64`
within the Monte Carlo ensemble (10k × 22 trajectories make Decimal
prohibitive in memory), but the headline outputs in `R6Output` (VaR,
CVaR, percentiles, etc.) are converted to `Decimal` at the aggregation
step. This is appropriate for statistical (not reconciliation-grade)
output. The precision boundary is explicit in §3.3 and tested by a
Hypothesis property that round-trips a synthetic Decimal-exact cost path
through the ensemble and verifies the aggregated Decimal headlines match
the inputs to within `float64`-tolerance bounds.

**CORRECTIONS-LL (Sparse-cell fallback log schema — Code Reviewer FLAG 7).**
v0.1.0 logged only an integer count of fallback events. v0.1.1 emits a
structured `fallback_log: Sequence[FallbackEvent]` on
`CostTrajectoryEnsemble`, where `FallbackEvent` is a frozen-dc with
`(simulated_ts, hour_block, day_type, fallback_level, observed_pool_size)`.
Hypothesis property tests fallback-rate computation.

**CORRECTIONS-MM (Cap-window parameter pinned — Code Reviewer FLAG 2d).**
v0.1.0's `count_cap_wait_hours(arrivals, cap_window_hours=5.0)` used a
default arg that created a silent-fishing surface. v0.1.1 moves
`cap_window_hours` and `weekly_cap_hours` onto a `CapWaitConfig`
frozen-dc; values pre-pinned with Anthropic source URL + access date; the
config is part of the top-level `audit_block` envelope.

**CORRECTIONS-NN (Token-size invariance across $k$ explicitly
documented — Model QA FLAG 4c).** v0.1.0 §2.3 implicitly assumed the
token-size distribution does not change with extrapolation rate $k$.
v0.1.1 §6 threats explicitly acknowledges this modeling choice with
direction-of-bias analysis: under-states cost variance at high $k$ if
unconstrained users issue shorter calls. R6 v2 (v0.3.0 milestone) is
scoped to relax this if data-driven evidence emerges from cohort step.

**CORRECTIONS-OO (Bootstrap loses within-day autocorrelation — Model QA
FLAG 7).** v0.1.0's i.i.d.-within-pool bootstrap loses within-day
message-size autocorrelation, mechanically over-attributing variance to
the FX channel. v0.1.1 adds a **reconciliation-ratio reporting** cell in
`03_variance_decomp.ipynb` that compares the simulated
$\text{Var}(\Delta\ln\text{Cost}^{USD})$ to the v0.2.1 observed
$\text{Var}(\Delta\ln\text{Cost}^{USD})$; a ratio outside $[0.8, 1.2]$
triggers the `"reconciliation_drift_high"` quality flag (CORRECTIONS-II).

**CORRECTIONS-PP (RNG-call-order documentation — Code Reviewer NIT
3-style).** v0.1.1 docstrings on `NHPPArrivalGenerator` and
`FXBlockBootstrapGenerator` explicitly pin RNG-call order, mirroring
`simulations/stochastic_fx/generators.JumpDiffusionPathGenerator`'s "RNG-
call order is load-bearing for Pin Z1.2" convention.

## 0.2 v0.1.1 → v0.1.2 CORRECTIONS

v0.1.1 review returned PARTIAL_CLOSE from Wave 1 RC with two NEW_BLOCKs
from empirical verification on widened data (51 days / 86,300 messages,
up from v0.1.0's 33 days). Both are line-edits per RC's own
classification ("Both new blocks are line-edits, not methodology
surgery"). Plus one editorial NIT from Wave 2 Code Reviewer.

**CORRECTIONS-QQ (Weekly-cap scope-out — RC NEW_BLOCK 4a).** v0.1.1
CORRECTIONS-DD committed to pinning a `WEEKLY_CAP_HOURS` constant against
"Anthropic published value." Empirical check by Wave 1 RC found the
Anthropic source URL does not publish a numeric weekly-cap value — only
narrative descriptions of "approximate" limits. Pinning is therefore
unsatisfiable; the §2.7 weekly-cap drift HALT cannot fire because no
baseline exists to compare against.

v0.1.2 **scopes out weekly-cap modeling for R6 v1** (option (c) of RC's
four resolution paths):

- `CapWaitConfig` collapses to a single field `session_cap_hours: float`
  (was: both session and weekly fields).
- `WEEKLY_CAP_HOURS` constant in `_anthropic_caps.py` is removed.
- `R6Output.quality_flags` drops `weekly_cap_dominates`.
- `CapWaitCounter.__call__` returns per-path session-cap-wait hours only.
- §2.6 output (3) "Cap-wait friction" reduces to session-cap measure
  only: $H^{\text{obs}}_{\text{session-cap}}$ and
  $H^{\text{sim}}_{\text{session-cap}}(k)$.
- §2.7 removes the weekly-cap parameter drift HALT.
- §6 threats adds new row: "Weekly cap omitted from R6 v1; cap-wait
  friction at high $k$ may be understated by an amount bounded by the
  unmeasured weekly-cap quota." Direction-of-bias: understatement.
- §9 out of scope adds: "Weekly cap modeling — R6 v2 candidate,
  contingent on either Anthropic publishing a numeric value or
  cohort-data empirical calibration." Empirical-calibration option is
  documented (count weekly active-session hours in observed JSONL; flag
  whether the user ever experienced a weekly-cap exhaustion event)
  but deferred to R6 v2 because it would require its own
  pre-registration discipline (cap-detection heuristic, threshold
  pinning, validation).

The session 5h cap (well-documented) remains the load-bearing cap-wait
mechanism for R6 v1 and is sufficient for the M-design step's first
sizing-curve consumption. Weekly cap enters the M-design picture only at
high $k$ where the unsubscribed-population's continuous-stream usage
plausibly bumps against the weekly limit; that question is answered at
R6 v2 + M-design step jointly.

**CORRECTIONS-RR (Pool canonicalization dedupe + uuid tiebreaker — RC
NEW_BLOCK 8a).** v0.1.1 CORRECTIONS-FF asserted the sort key
`(ts, request_id, session_id)` was unique by Claude Code's `request_id`
allocation. Wave 1 RC empirically falsified this claim: 1,955 / 84,237
tuples (~2.3%) appear more than once on the maintainer's actual JSONL,
because the same `requestId` is logged in BOTH the main session file AND
a sub-agent file (when sub-agents are dispatched). A stable sort on a
non-unique key leaks filesystem-walk order into the resulting hash → not
bit-exact across machines or re-runs.

v0.1.2 fix:

- **Dedupe step (new, ahead of canonical sort):** for each `request_id`,
  keep exactly one record. Tiebreaker is **lexicographically smallest
  source-file path** (deterministic across filesystems given a stable
  glob; documented in the canonicalization rule).
- **Tertiary sort key (new):** add the JSONL line's `uuid` field as the
  fourth sort key. Anthropic's Claude Code JSONL schema includes a per-
  line `uuid` field per assistant message — RC's earlier review verified
  this. Sort key becomes `(ts, request_id, session_id, uuid)` after
  dedupe.
- **Updated canonicalization rule (§5.3):**
  1. Glob `~/.claude/projects/**/*.jsonl` in lexicographic order.
  2. For each file, parse to `MessageRecord` sequence.
  3. Across all files, group by `request_id`. For each group with
     $\geq 2$ records, keep the one whose source-file path is
     lexicographically smallest.
  4. Sort the deduplicated set by `(ts, request_id, session_id, uuid)`.
  5. Serialize each row via `dataclasses.asdict` then `canonical_json`.
  6. Concatenate; SHA-256 hash → `message_pool_content_sha256`.
- The "impossible by request_id allocation" claim in CORRECTIONS-FF is
  **dropped** (falsified by RC empirical check).
- Hypothesis property test: shuffle the input file order, re-run the
  canonicalization, verify the resulting hash is identical.
- The `MessageRecord` type does NOT change — `uuid` was already in the
  Anthropic JSONL schema and is captured by the own-parser per v0.2.1
  §3.5. v0.1.2 surfaces it as a sort key, not as a new field. (Note: if
  v0.2.1's `MessageRecord` frozen-dc didn't include `uuid` as a field,
  that's a v0.2.1 plan-execution amendment task — flagged here for
  awareness; the v0.2.1 spec's parser implementation must capture `uuid`
  to support R6's canonicalization.)

**CORRECTIONS-SS (CORRECTIONS-EE wording — Code Reviewer NIT-A).**
v0.1.1 CORRECTIONS-EE described the realigned `NHPPArrivalGenerator`
signature as *"mirroring `GBMPathGenerator` verbatim"*. Code Reviewer's
v0.1.1 closure verified this is overstated: R6 puts `n_paths` on
`NHPPSimulationConfig` whereas the canonical pattern keeps `n_paths` on
`__call__(rng_seed, n_paths)`. R6 is a **strict generalization** —
audit-coverage is stronger because every bit-exactness parameter is
hashed via the standard envelope. v0.1.2 corrects the wording from
"verbatim" to "strict generalization with strictly-stronger audit
coverage"; the actual signature is unchanged from v0.1.1 (Code Reviewer
approved the signature itself).

**CORRECTIONS-TT (Canonicalization edge cases — Code Reviewer NIT-C
from v0.1.2 closure-only; folded into v0.1.3 polish).** CORRECTIONS-RR
left two edge cases unpinned in the dedupe rule:

(a) **Missing `request_id`**: legacy Claude Code versions (pre-2.0) may
emit records with `request_id = None`. v0.1.3 pins: records with
`request_id = None` are **excluded** from the deduplicated message pool
entirely (logged as `dropped_legacy_request_id_count` in
DATA_PROVENANCE per §5.4). Rationale: dedupe semantics require a stable
group key; `None` cannot serve as a group key. Legacy records are out
of scope for R6 simulation provenance (they were already flagged for
warning emission in CORRECTIONS-V).

(b) **Tiebreaker collapse when multiple records share lex-smallest
source-file path**: this can occur if the parser emits multiple records
from the same JSONL file with the same `request_id` (e.g., a request
retried within a single session). v0.1.3 extends step 3 of the
canonicalization rule: **if multiple records share the lex-smallest
source-file path, keep the one with the lex-smallest `uuid`** (using
the per-JSONL-line uuid field). Hypothesis property test for this edge
case added to the shuffle-invariance pin.

The updated 6-step canonicalization rule in §5.3 is amended to reflect
both clarifications. The sibling v0.2.1 plan-execution amendment
documented in the frontmatter `sibling_corrections_v0_2_1_plan` block
covers the `uuid: str` field addition to `MessageRecord` that this
canonicalization depends on.

## 1. Purpose and framework placement

### 1.1 Goal

Quantify the COP cost-burden distribution that a non-subscribed LATAM
developer would face for a continuous-usage API stream calibrated to the
pilot subject's pattern, after removing the session-based 5h
subscription-cap constraint (CORRECTIONS-DD as amended by CORRECTIONS-QQ
scopes out the weekly cap for R6 v1). R6's output is consumed by the
downstream M-design step as the **cost-distribution input** the
Panoptic-eligible hedge position must absorb.

### 1.2 Why R6 complements R5

R5 (v0.2.1) quantifies one dimension of M-design value: cost-risk
reduction (variance decomposition of observed cost burden). R6 quantifies
the second dimension: **capacity unblocking** — the wage-earner-LATAM-dev
target population, currently constrained by Anthropic's session 5h cap
AND weekly cap (or priced out of the API entirely), would face a
different cost-burden distribution under unconstrained continuous-stream
usage.

The dual hedge-value argument requires both:

- **R5 output**: realized FX-vol share of cost-burden variance (observed
  pattern).
- **R6 output**: simulated cost-burden distribution + cap-wait hours under
  the session 5h Anthropic cap (weekly cap scoped out of R6 v1 per
  CORRECTIONS-QQ; a function of extrapolation rate $k$) + output-quality
  flags binding the M-design step.

### 1.3 Stage in the (Y, M, X) framework

Candidate-X enrichment step. R6 produces a cost-distribution + cap-wait
profile + quality flags that the M-design step (subsequent sub-iteration)
consumes directly. R6 itself produces no PASS/FAIL verdict on the (Y, X)
pair.

### 1.4 Relationship to v0.2.1

R6 reuses (UNCHANGED unless noted):

- The own-parser data feeder (`JSONLReader`) for `MessageRecord` source.
  **CORRECTIONS-CC removed v0.1.0's planned `is_cap_reset` extension;
  `JSONLReader` is fully unchanged from v0.2.1.**
- `PricingTable` at the same LiteLLM commit SHA pin
  (`e58a561caa21169fb02174148444c08509ce7028`).
- Banrep daily TRM panel from extended `scripts/fetch_banrep.py`.
- Sub-package errors convention. **CORRECTIONS-AA introduces
  `DevAICostError(Exception)` as new root**; `JSONLSchemaError` is
  reparented to inherit from `DevAICostError`. v0.2.1 plan-execution
  picks this up as the very first amendment task.
- Stationary-bootstrap convention (block length $\lceil T^{1/3} \rceil$).
- Conservative-covariance variance-decomposition rule.
- Sensitivity-arm DIAGNOSTIC-only classification.
- Deterministic-RNG `audit_block` convention from
  `simulations/stochastic_fx/`.

R6 adds:

- NHPP arrival-process calibration on within-session inter-arrival times
  with hour-block × day-type grid (CORRECTIONS-BB)
- Within-session arrival generator + session-composition simulator
- FX block-bootstrap path generator
- Cost-trajectory ensemble simulation with hour-block × day-type indexed
  empirical bootstrap (CORRECTIONS-GG)
- Cap-wait hour counter implementing the session 5h Anthropic cap
  (CORRECTIONS-DD as amended by CORRECTIONS-QQ; weekly cap scoped out of
  R6 v1)
- Output-quality flags for M-design contract binding (CORRECTIONS-II)
- Simulation provenance + new audit_block over R6-specific parameter
  envelope with `message_pool_content_sha256` (CORRECTIONS-FF)

## 2. Methodology stack

### 2.1 Arrival process — Non-Homogeneous Poisson with hour-block × day-type seasonality

**Intensity specification** (CORRECTIONS-BB):

$$\lambda(t) = \lambda_0 \cdot f(\text{hour-block}(t)) \cdot
g(\text{day-type}(t))$$

where:

- $\lambda_0 > 0$ is the baseline rate (calls/hour at the reference
  hour-block × day-type cell)
- $f: \{\text{morning}, \text{afternoon}, \text{evening}, \text{night}\}
  \to \mathbb{R}_+$ is the hour-block multiplier, $f(\text{morning})
  \equiv 1$ as identification constraint
- $g: \{\text{weekday}, \text{weekend}\} \to \mathbb{R}_+$ is the
  day-type multiplier, $g(\text{weekday}) \equiv 1$ as identification
  constraint
- **Hour-block boundaries**: morning [06:00, 12:00), afternoon [12:00,
  18:00), evening [18:00, 22:00), night [22:00, 06:00) — pinned ex-ante
- **Day-type partition**: weekday {Mon..Fri}, weekend {Sat, Sun} —
  pinned ex-ante

**Calibration sample**: within-session inter-arrival times from
`MessageRecord` instances grouped by `session_id` (CORRECTIONS-CC). Each
session contributes its sequence of inter-arrival gaps; cross-session
gaps are excluded. No cap-reset detection heuristic.

**MLE pinning (CORRECTIONS-BB + Model QA BLOCK 2 closure)**:

- Convergence threshold: $|\Delta \log L| < 10^{-6}$ between iterations
- Maximum iterations: 1000
- Per-cell minimum observation count: $N_{\min} = 50$ — well above Model
  QA's $N_{\min} = 5$ floor; HALT if any cell has fewer (expected to be
  unreachable under the 8-cell grid given 33+ active days, but pinned as
  safety net)
- `nhpp_convergence_marginal` quality flag set if final $|\Delta \log L| /
  |\log L| > 10^{-4}$ (CORRECTIONS-II)

### 2.2 Cap-reset detection — REMOVED (CORRECTIONS-CC)

No cap-reset detection. NHPP is fit on within-session inter-arrival times
only; inter-session gaps are exogenous and out of scope for the arrival
process. Sessions are identified by `MessageRecord.session_id`. This
section name retained for v0.1.0 → v0.1.1 traceability.

### 2.3 Extrapolation — sizing curve (unchanged from v0.1.0)

$$\lambda^{R6}(t; k) = k \cdot \hat\lambda^{\text{observed}}(t)$$

Pre-pinned sizing curve: $k \in \{0.5, 1.0, 2.0, 3.0, 5.0\}$.

Token-size invariance across $k$ pre-registered as modeling choice with
explicit direction-of-bias analysis (CORRECTIONS-NN; §6 threats).

### 2.4 Token and model assignment — hour-block × day-type indexed bootstrap (CORRECTIONS-GG)

For each within-session simulated arrival at time $t$:

1. Compute $(h, d) = (\text{hour-block}(t), \text{day-type}(t))$
2. Define pool $\mathcal{P}_{h,d} = \{r \in R^{\text{obs}} : (\text{hour-
   block}(r.ts), \text{day-type}(r.ts)) = (h, d)\}$
3. Sparse-cell fallback: if $|\mathcal{P}_{h,d}| < 50$, expand to the
   day-type marginal $\mathcal{P}_{\cdot, d}$; if still $< 50$, raise
   `SparsePoolError` (HALT)
4. Sample $r^* \sim \text{Uniform}(\mathcal{P}_{h,d})$
5. Use $r^*$'s `(model, input_tok, output_tok, cache_5m, cache_1h,
   cache_read)` for cost computation via `PricingTable`

Sparse-cell fallback events recorded in structured `fallback_log` per
CORRECTIONS-LL. Fallback rate $> 10\%$ triggers
`sparse_cell_fallback_rate_high` quality flag.

### 2.5 Hedge representation — none (unchanged from v0.1.0)

R6 produces unhedged counterfactual cost distribution; M-design step
downstream computes hedge value separately.

### 2.6 Output metrics

For each $k \in \{0.5, 1.0, 2.0, 3.0, 5.0\}$ and $M = 10{,}000$
Monte-Carlo paths over a 1-month horizon (CORRECTIONS-II adds
`R6Output.quality_flags`):

**(1) Cost-burden distribution** (90% stationary-bootstrap CIs):
- Monthly $\hat{\text{VaR}}_{0.05}^{COP}(k)$, $\hat{\text{CVaR}}_{0.05}^{COP}(k)$
- Monthly $\hat{\text{VaR}}_{0.01}^{COP}(k)$, $\hat{\text{CVaR}}_{0.01}^{COP}(k)$
- Percentiles {10, 25, 50, 75, 90, 95, 99}
- Mean and SD of monthly cost
- All headline outputs in `Decimal` per CORRECTIONS-KK precision boundary

**(2) Variance decomposition** with conservative covariance attribution
(unchanged from v0.1.0); reconciliation-ratio reporting against v0.2.1
observed variance per CORRECTIONS-OO.

**(3) Cap-wait friction** under the session 5h cap (CORRECTIONS-DD as
amended by CORRECTIONS-QQ; weekly cap scoped out of R6 v1):
- $H^{\text{obs}}_{\text{session-cap}}$: session-cap wait hours observed
- $H^{\text{sim}}_{\text{session-cap}}(k)$: session-cap wait hours
  simulated under counterfactual continuous-stream

**(4) Output-quality flags** (CORRECTIONS-II as amended by
CORRECTIONS-QQ; `weekly_cap_dominates` flag removed): see §0.1 list +
§0.2 amendments.

**Headline output for M-design step**:

> "For continuous-usage stream at extrapolation rate $k$, the monthly COP
> cost burden has 5%-VaR = $X(k)$ COP (90% bootstrap CI $[a, b]$). FX
> volatility contributes $Y(k)\%$ of the variance under conservative
> attribution. The continuous-stream pattern would experience
> $Z_{\text{session}}(k)$ hours of session-cap-wait per month under
> subscription regime — eliminated by the M-design hedge. (Weekly cap
> scoped out of R6 v1 per CORRECTIONS-QQ; cap-wait friction may be
> understated at high $k$.) Quality flags: $\{Q\}$ (M-design consumes
> only if disqualifying flags are absent)."

### 2.7 HALT events (no PASS/FAIL; pre-enumerated dispositions)

- **NHPP min-bin HALT**: any cell with $< N_{\min} = 50$ observations →
  pre-enumerated pivot: re-coarsen grid or expand window
- **NHPP convergence HALT**: MLE doesn't converge in 1000 iterations
- **Sparse-cell fallback HALT**: $|\mathcal{P}_{\cdot, d}| < 50$ on the
  day-type marginal (sparse cell beyond fallback)
- **Reconciliation drift HALT**: simulated mean cost at $k = 1$ differs
  from observed mean cost by $> 1\%$ (CORRECTIONS-HH)
- **Reconciliation-ratio HALT**: $\text{Var}(\Delta\ln\text{Cost}^{USD})$
  ratio outside $[0.8, 1.2]$ (CORRECTIONS-OO)
All HALTs route to `notebooks/dev_ai_cost_v2_r6/dispositions/`. (The
v0.1.1 "weekly-cap parameter drift HALT" is removed in v0.1.2 per
CORRECTIONS-QQ — Anthropic does not publish a numeric weekly-cap value
to compare against, so the HALT was unfireable.)

## 3. Data architecture

### 3.1 FX path generation — block bootstrap (unchanged from v0.1.0)

Stationary bootstrap (Politis-Romano 1994) on observed daily
$\Delta\ln\text{USDCOP}$ returns, block length
$\lceil T_{\text{hist}}^{1/3} \rceil$, trailing 5-year history.

### 3.2 Arrival ⊥ FX independence (pre-registered for v1; unchanged from v0.1.0)

### 3.3 Component decomposition

All new modules live in `simulations/dev_ai_cost_v2/` (same sub-package
as v0.2.1). Tier discipline per CLAUDE.md.

| Unit | Tier | Signature / Role |
|---|---|---|
| `nhpp_calibration.fit_nhpp(records: Sequence[MessageRecord]) -> NHPPParameters` | modules | groups records by `session_id`; extracts within-session inter-arrival times; binned MLE for $\lambda_0$, $f$, $g$ on the 8-cell hour-block × day-type grid (CORRECTIONS-BB); raises `NHPPSparseBinError` on $N_{\min} < 50$ |
| `types.NHPPParameters` | types | frozen-dc: `lambda_0: float, f_hour_block: tuple[float, float, float, float]` (length 4, $f(\text{morning})=1$), `g_day_type: tuple[float, float]` (length 2, $g(\text{weekday})=1$), `log_likelihood: float, convergence_iters: int, per_cell_counts: tuple[tuple[int, int, int, int], tuple[int, int, int, int]]` |
| `types.NHPPSimulationConfig` | types | frozen-dc wrapping `params: NHPPParameters` + `k: float` + `horizon_days: int` + `n_paths: int` — all bit-exactness parameters in one envelope per CORRECTIONS-EE |
| `arrival_generators.NHPPArrivalGenerator` | modules | frozen-dc with `config: NHPPSimulationConfig` + `__call__(rng_seed: int) -> ArrivalEnsemble` (CORRECTIONS-EE realignment with `stochastic_fx` precedent). Emits per-module `audit_block` per CORRECTIONS-JJ. Docstring pins RNG-call order per CORRECTIONS-PP. |
| `types.ArrivalEnsemble` | types | frozen-dc: `arrival_times: NDArray[float64]` (shape `(n_paths, n_arrivals_max)`, NaN-padded), `session_assignments: NDArray[int32]` (which session each arrival belongs to), `audit_block: AuditBlock` |
| `fx_block_bootstrap.FXBlockBootstrapGenerator` | modules | frozen-dc with `history_returns_sha: str, expected_block_length: int, horizon_days: int, n_paths: int` + `__call__(rng_seed: int) -> FXPathEnsemble`. Docstring pins RNG-call order. Emits per-module `audit_block`. |
| `types.FXPathEnsemble` | types | frozen-dc: `log_returns: NDArray[float64]` (shape `(n_paths, horizon_days)`), `usdcop_paths: NDArray[float64]`, `audit_block: AuditBlock` |
| `cost_simulation.CostSimulator` | modules | frozen-dc with `pricing: PricingTable` + `message_pool: Sequence[MessageRecord]` + `pool_content_sha: str` (precomputed at construction; CORRECTIONS-FF) + `__call__(arrivals: ArrivalEnsemble, fx: FXPathEnsemble, rng_seed: int) -> CostTrajectoryEnsemble`. Performs hour-block × day-type indexed whole-message bootstrap (CORRECTIONS-GG); cost computation via `PricingTable`; FX multiplication; emits structured `fallback_log` per CORRECTIONS-LL. |
| `types.CostTrajectoryEnsemble` | types | frozen-dc: `cop_costs: NDArray[float64]` (float64 ensemble per CORRECTIONS-KK precision boundary; Decimal-headlined in `R6Output`), `fallback_log: tuple[FallbackEvent, ...]`, `audit_block: AuditBlock` |
| `types.FallbackEvent` | types | frozen-dc: `simulated_ts: float, hour_block: str, day_type: str, fallback_level: Literal["cell", "day-type-marginal"], observed_pool_size: int` (CORRECTIONS-LL) |
| `_anthropic_caps.SESSION_CAP_HOURS` | module-level constant | pre-pinned at 5.0 per Anthropic source URL + access date (CORRECTIONS-DD as amended by CORRECTIONS-QQ; weekly cap removed); change requires spec update |
| `types.CapWaitConfig` | types | frozen-dc: `session_cap_hours: float` (CORRECTIONS-MM as amended by CORRECTIONS-QQ — single-field; weekly removed) |
| `cap_wait_counter.CapWaitCounter` | modules | frozen-dc with `config: CapWaitConfig` + `__call__(arrivals: ArrivalEnsemble) -> CapWaitOutput`. Returns per-path session-cap-wait hours. |
| `types.R6Output` | types | frozen-dc: per-$k$ VaR/CVaR (`Decimal`), percentiles (`dict[int, Decimal]`), variance_decomp, cap_wait (session-cap only per CORRECTIONS-QQ; weekly cap scoped out of R6 v1), bootstrap_ci, **`quality_flags: frozenset[str]`** per CORRECTIONS-II as amended by CORRECTIONS-QQ |

### 3.4 Reused from v0.2.1 (UNCHANGED in v0.1.1)

- `jsonl_io.JSONLReader` — fully unchanged from v0.2.1. The v0.1.0
  `is_cap_reset` extension is REMOVED per CORRECTIONS-CC.
- `anthropic_pricing.PricingTable` — unchanged.
- `panel_builder.build_daily_panel` — unchanged (R6 doesn't use it).
- `_errors.py` — receives the CORRECTIONS-AA amendment at v0.2.1 plan-
  execution time (introduce `DevAICostError(Exception)`; reparent
  `JSONLSchemaError`).

### 3.5 New errors

- `DevAICostError(Exception)` — sub-package root, introduced via
  CORRECTIONS-AA in v0.2.1 plan-execution (formally part of v0.2.1's
  errors hierarchy; documented here because R6 depends on it)
- `NHPPCalibrationError(DevAICostError)` — MLE convergence failure
- `NHPPSparseBinError(NHPPCalibrationError)` — any cell with $< N_{\min}
  = 50$ observations
- `SparsePoolError(DevAICostError)` — sparse-cell fallback beyond day-
  type marginal (HALT trigger)

## 4. Notebook structure

`notebooks/dev_ai_cost_v2_r6/`:

- `01_nhpp_eda.ipynb` — calibration EDA per trio-checkpoint convention.
  Required cells:
  - **Within-session inter-arrival distribution plot** by hour-block ×
    day-type cell; verify $N_{\min} = 50$ is met everywhere
  - **NHPP fit diagnostics**: $\hat f$ × $\hat g$ heatmap; residual plot
    of observed vs fitted inter-arrival distributions per cell
  - **Reconciliation-drift cell** (CORRECTIONS-HH): run simulation at
    $k = 1$ on calibration sample; compute drift on mean cost; HALT if
    > 1%
  - **Session-boundary inspection cell**: distribution of inter-session
    gaps (descriptive only; not used in calibration)
- `02_simulation.ipynb` — generate ensembles for sizing curve.
- `03_variance_decomp.ipynb` — conservative-covariance decomposition;
  reconciliation-ratio cell per CORRECTIONS-OO.
- `04_cap_wait.ipynb` — cap-wait hours under the session 5h cap only (per CORRECTIONS-QQ; weekly cap scoped out of R6 v1)
  (session 5h + weekly) per CORRECTIONS-DD; flag dominant constraint.
- `05_sensitivity.ipynb` — diagnostic arms (DIAGNOSTIC-only, no verdict
  authority): horizon $\{3, 12\}$ mo, FX block-length sensitivity.

Cap-reset visual-validation cell from v0.1.0 §4 is REMOVED
(CORRECTIONS-CC: no cap-reset detection in v0.1.1).

## 5. Reproducibility pins

### 5.1 LiteLLM commit SHA pin (shared with v0.2.1)

`e58a561caa21169fb02174148444c08509ce7028`

### 5.2 Banrep daily TRM panel pin

Trailing-5-year file SHA-256 pinned in simulation provenance.

### 5.3 R6 `audit_block` (CORRECTIONS-FF + CORRECTIONS-JJ)

Top-level envelope chains per-module hashes:

```
audit_block = sha256(canonical_json({
  "nhpp_module_hash": <NHPPArrivalGenerator audit_block>,
  "fx_module_hash":   <FXBlockBootstrapGenerator audit_block>,
  "cost_module_hash": <CostSimulator audit_block>,
  "cap_wait_config_hash": sha256(canonical_json(CapWaitConfig)),
  "message_pool_content_sha256": <sha256 of canonical-sorted MessageRecord pool>,
  "parser_version_sha": <own-parser git SHA at simulation time>,
  "litellm_sha": "e58a561c...",
  "banrep_trm_daily_sha": <Banrep TRM parquet SHA>,
  "sizing_curve_k": [0.5, 1.0, 2.0, 3.0, 5.0],
  "rng_seed": int,
  "n_paths": 10000,
  "horizon_days": 22,
}))
```

**Message-pool canonicalization (v0.1.2 amended per CORRECTIONS-RR — RC
NEW_BLOCK 8a closure):**

1. Glob `~/.claude/projects/**/*.jsonl` in lexicographic source-path order.
2. For each file, parse to `MessageRecord` sequence (own-parser).
3. **Drop records with `request_id = None`** (legacy Claude Code pre-2.0;
   logged as `dropped_legacy_request_id_count` in DATA_PROVENANCE per
   CORRECTIONS-TT (a)).
4. Across all remaining files, **dedupe by `request_id`**: for each
   group with $\geq 2$ records (occurs when the same request is logged
   in both the main session file and a sub-agent file — empirically
   ~2.3% of tuples on the maintainer's data), keep the one whose
   **source-file path is lexicographically smallest**. If multiple
   records share the lex-smallest path (same request retried within one
   file), keep the one with the lex-smallest `uuid` (CORRECTIONS-TT (b)).
5. Sort the deduplicated set by `(ts, request_id, session_id, uuid)`.
   The `uuid` quaternary key is per-JSONL-line and resolves any remaining
   ties (e.g. simultaneous timestamps).
6. Serialize each row via `dataclasses.asdict` then `canonical_json`.
7. Concatenate; SHA-256 hash → `message_pool_content_sha256`.

Hypothesis property test: shuffle the input file glob order, re-run the
canonicalization, verify the resulting hash is identical.

The v0.1.1 claim that the original sort key was unique "by Claude Code's
`request_id` allocation" is **dropped** — empirically falsified by Wave 1
RC.

### 5.4 Data-provenance file

`notebooks/dev_ai_cost_v2_r6/data/DATA_PROVENANCE.md` records:

- LiteLLM commit SHA
- Banrep daily TRM parquet SHA-256
- NHPP calibration log-likelihood, convergence iterations, per-cell
  observation counts
- Sizing-curve $k$ values
- RNG seed per Monte Carlo run
- `audit_block` per run
- Sparse-cell fallback event count + structured log
- Cap rule source URL: <https://support.claude.com/en/articles/8325606>
  + access date 2026-05-16
- Pinned `SESSION_CAP_HOURS` value (5.0; weekly cap scoped out per
  CORRECTIONS-QQ)
- `dropped_legacy_request_id_count` — count of records with
  `request_id = None` dropped during canonicalization (CORRECTIONS-TT)
- Own-parser git commit SHA at simulation-build time
- `R6Output.quality_flags` for each $k$

## 6. Threats, identification, mitigations

| Threat | Mitigation |
|---|---|
| Subscription-as-proxy assumption | Inherited from v0.2.1 §6 row 1; bias direction (level overstates, share understates) preserved |
| NHPP identification at $T = 33$ days | 8-cell grid (CORRECTIONS-BB); $N_{\min} = 50$ per cell with HALT (§2.7); empirically validated by RC against actual data |
| Cap-reset detection unreliable on real data | RESOLVED by CORRECTIONS-CC: no cap-reset detection; calibration uses within-session inter-arrival times only via `session_id` |
| JSONL-level cap-hit signals do not exist | RESOLVED by CORRECTIONS-CC: not needed under session_id-based calibration |
| Cap-reset masking selection bias | RESOLVED by CORRECTIONS-CC: no masking; sessions are exogenous |
| Anthropic policy mis-stated (rolling vs session) | CORRECTIONS-DD: session-based 5h cap modeled (was: "rolling"); source URL + access date pinned in provenance |
| Weekly cap omitted from R6 v1 (CORRECTIONS-QQ) | Cap-wait friction at high $k$ may be understated by an amount bounded by the unmeasured weekly-cap quota. Direction-of-bias: understatement. Anthropic does not publish a numeric weekly-cap value to pin against; resolution deferred to R6 v2 (cohort empirical calibration or Anthropic policy change) |
| Hour-block × day-type bootstrap loses fine intra-hour structure | Acknowledged modeling choice; v2 can refine if sufficient cohort data |
| Token-size invariance across $k$ | Acknowledged; bias direction under-states cost variance at high $k$ if real users issue shorter calls when unconstrained (CORRECTIONS-NN) |
| i.i.d.-within-pool bootstrap loses within-day autocorrelation | Reconciliation-ratio reporting + `reconciliation_drift_high` quality flag (CORRECTIONS-OO) |
| Sparse-cell fallback beyond day-type marginal | `SparsePoolError` HALT (§2.7) |
| Independence between arrival and FX | Pre-registered for v1; R6 v2 contingent on R4-S3-USD verdict |
| Block-bootstrap block length mis-sized | $\lceil T_{\text{hist}}^{1/3} \rceil$ pinned; FX block-length sensitivity arm in 05 (DIAGNOSTIC only) |
| Extrapolation rate $k$ as free parameter | Pre-pinned set $\{0.5, 1, 2, 3, 5\}$; no post-hoc additions; M-design selects |
| 5-hour session cap implementation correctness | Cap source URL pinned with access date; implementation in `_anthropic_caps.py` is a declarative constant (`SESSION_CAP_HOURS = 5.0`) |
| Pool sort-key non-unique on real data (RC NEW_BLOCK 8a) | CORRECTIONS-RR: dedupe by `request_id` keeping lexicographically smallest source-file path + `uuid` tertiary sort key; Hypothesis-property-tested for shuffle-invariance |
| `audit_block` envelope insufficient for bit-exactness | CORRECTIONS-FF + CORRECTIONS-JJ: `message_pool_content_sha256` + parser-version SHA + per-module audit_block chain |
| `cop_costs` float64 vs Decimal precision regression | CORRECTIONS-KK: documented as ensemble-vs-headline precision boundary; Hypothesis-property-tested |
| Sensitivity arms acquiring verdict authority | DIAGNOSTIC only (CORRECTIONS-K v0.2.1 convention preserved) |

## 7. Anti-fishing invariants

- NHPP grid: 4 hour-blocks × 2 day-types, **pinned ex-ante** (CORRECTIONS-
  BB)
- Hour-block boundaries pinned: morning [06:00, 12:00), afternoon [12:00,
  18:00), evening [18:00, 22:00), night [22:00, 06:00)
- Day-type partition pinned: weekday {Mon..Fri}, weekend {Sat, Sun}
- Identification constraints pinned: $f(\text{morning}) = 1$,
  $g(\text{weekday}) = 1$
- MLE convergence threshold pinned: $|\Delta \log L| < 10^{-6}$
- Per-cell minimum observation count pinned: $N_{\min} = 50$
- Sizing curve $k \in \{0.5, 1.0, 2.0, 3.0, 5.0\}$ pinned; no post-hoc
  additions
- Sparse-cell fallback threshold pinned ($|\mathcal{P}| < 50$); HALT if
  day-type marginal also sparse
- Block-bootstrap block length pinned: $\lceil T_{\text{hist}}^{1/3}
  \rceil$
- $M = 10{,}000$ Monte Carlo paths pinned
- Anthropic session 5h cap pinned with source URL + access date (weekly
  cap scoped out per CORRECTIONS-QQ; not pre-pinned)
- Arrival ⊥ FX independence pre-registered (v1)
- Reconciliation HALT threshold pinned: 1% drift on $k = 1$ mean (CORRECTIONS-HH)
- Reconciliation-ratio HALT pinned: variance ratio outside $[0.8, 1.2]$
- Sensitivity arms DIAGNOSTIC only
- No PASS/FAIL verdict; quality flags bind M-design consumption
- Token-size invariance across $k$ pre-registered (CORRECTIONS-NN)

## 8. Workflow / agent assignment (unchanged from v0.1.0)

(Same table as v0.1.0 §8; the cap-reset disposition row from v0.1.0
becomes the **reconciliation-drift disposition** row given CORRECTIONS-CC
+ CORRECTIONS-HH.)

## 9. Out of scope (R6 v1.2)

- Joint arrival × FX dependence (R6 v2, contingent on R4-S3-USD verdict)
- **Weekly-cap modeling** (CORRECTIONS-QQ) — R6 v2 candidate, contingent
  on either Anthropic publishing a numeric weekly-cap value or
  cohort-data empirical calibration with its own pre-registration
  discipline (cap-detection heuristic, threshold pinning, validation)
- Hedge model / Panoptic position parameters (M-design step)
- Cohort-level calibration
- Hawkes self-exciting arrival process (R6 v2 candidate)
- Monetization of cap-wait hours (M-design)
- Token-size scaling with $k$ (R6 v2 candidate if data emerges)
- Within-hour-block intra-bin structure
- HTTP-API exposure

## 10. Open questions for v0.1.1 closure-only reviewers

1. **(For Wave 1 RC)** Verify CORRECTIONS-BB (8-cell grid) gives per-cell
   $N \geq 50$ on the actual JSONL data (you previously found 22% empty
   bins on the 168-cell grid; the 8-cell aggregation should resolve).
2. **(For Wave 1 RC)** Verify CORRECTIONS-DD weekly-cap pinned value
   matches current Anthropic documentation at <https://support.claude.com/
   en/articles/8325606> at access date 2026-05-16.
3. **(For Wave 2 Model QA)** Verify CORRECTIONS-CC session_id-based
   calibration is statistically sound — does excluding inter-session gaps
   bias $\hat\lambda$ in any direction? My read: it doesn't, because we
   model only within-session intensity and sessions are exogenous events,
   but reviewer confirmation needed.
4. **(For Wave 2 Model QA)** Verify CORRECTIONS-HH 1% reconciliation
   threshold derivation. Run-in-head: under correct calibration with
   $N_{\text{pool}} \sim 1500$, $M = 10{,}000$, what's the expected drift?
5. **(For Wave 2 Code Reviewer)** Verify CORRECTIONS-EE
   `NHPPSimulationConfig` + `__call__(rng_seed)` signature matches
   `simulations/stochastic_fx/generators.GBMPathGenerator` byte-for-byte.
6. **(For Wave 2 Code Reviewer)** Verify CORRECTIONS-FF message-pool
   canonicalization (sort by `(ts, request_id, session_id)`) is
   sufficient for bit-exactness. Edge case: two records with identical
   `(ts, request_id, session_id)` triples — impossible given Claude
   Code's request_id allocation, but document the assumption.

## 11. Cited files (updated v0.1.1)

| File / directory | Status | Role |
|---|---|---|
| `memory/feedback_two_wave_doc_verification.md` | EXISTS | governing review protocol |
| `memory/feedback_implementation_review_agents.md` | EXISTS | implementation panel composition |
| `memory/feedback_notebook_trio_checkpoint.md` | EXISTS | notebook HALT discipline |
| `memory/feedback_notebook_citation_block.md` | EXISTS | decision-citation block convention |
| `memory/feedback_pathological_halt_anti_fishing_checkpoint.md` | EXISTS | anti-fishing HALT protocol |
| `docs/specs/2026-05-16-ai-cost-factor-model-design.md` | EXISTS at v0.2.1 | sibling spec; R6 reuses data feeder and conventions |
| `docs/specs/2026-05-11-stochastic-fx-variant-design.md` | EXISTS | parent spec for `simulations/stochastic_fx/`; R6 mirrors generator pattern |
| `simulations/stochastic_fx/generators.py` | EXISTS | template for arrival/FX generators |
| `https://support.claude.com/en/articles/8325606` | external; ACCESSED 2026-05-16 | Anthropic Pro plan cap rules source (CORRECTIONS-DD) |
| `simulations/dev_ai_cost_v2/` | TO CREATE in v0.2.1 plan execution | R6 adds modules to this sub-package |
| `simulations/dev_ai_cost_v2/_errors.py` | TO CREATE in v0.2.1 plan execution; CORRECTIONS-AA amends | introduces `DevAICostError(Exception)`; reparents `JSONLSchemaError` |
| `simulations/dev_ai_cost_v2/_anthropic_caps.py` | TO CREATE in R6 plan | declarative constant `SESSION_CAP_HOURS = 5.0` (per CORRECTIONS-QQ, weekly cap scoped out of R6 v1) |
| `notebooks/dev_ai_cost_v2_r6/` | TO CREATE | R6 iteration directory |
| `notebooks/dev_ai_cost_v2_r6/dispositions/` | TO CREATE | pre-enumerated dispositions for §2.7 HALT events |
| `data/panels/banrep_trm_daily.parquet` | TO CREATE in v0.2.1 plan execution | R6 reads by SHA |

## 12. Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-05-16 | Initial draft; cap-reset heuristic; 24×7 NHPP grid; rolling 5h cap |
| 0.1.0 review | 2026-05-16 | NEEDS_WORK from all three reviewers. Wave 1 RC 6 BLOCKs by empirical verification (NHPP not identified at $T=33$; cap-reset heuristic flags 41% off-hours false positives; no JSONL cap signals; Anthropic policy mis-stated). Wave 2 Model QA 3 BLOCKs (pinning). Wave 2 Code Reviewer 3 BLOCKs (signatures/envelope). Reports at `scratch/2026-05-16-r6-spec-review/wave*.md`. |
| 0.1.1 | 2026-05-16 | Integration patch: CORRECTIONS-AA through -PP in §0.1. NHPP grid coarsened to 4 hour-blocks × 2 day-types. Cap-reset detection abandoned in favor of session_id-based within-session calibration. Anthropic policy corrected: session 5h + weekly cap both modeled. NHPP signature realigned with `stochastic_fx` precedent. `audit_block` envelope completed with `message_pool_content_sha256`. `R6Output.quality_flags` bind M-design step. Reconciliation HALT tightened to 1%. |
| 0.1.1 closure-only review | 2026-05-16 | Wave 2 Model QA CLOSE_ALL; Wave 2 Code Reviewer PARTIAL_CLOSE (1 editorial NIT-A); Wave 1 RC PARTIAL_CLOSE with 2 NEW_BLOCKs (4a: Anthropic doesn't publish weekly-cap numeric value; 8a: sort-key non-unique on real data, ~2.3% duplicate tuples). Both NEW_BLOCKs classified as "line-edits not methodology surgery" by RC. Reports at `scratch/2026-05-16-r6-spec-review/wave*_v0_1_1.md`. |
| 0.1.2 | 2026-05-16 | Integration patch: CORRECTIONS-QQ (weekly cap scoped out of R6 v1; `CapWaitConfig` single-field; `weekly_cap_dominates` quality flag removed; documented understatement-direction bias in §6 threats; R6 v2 candidate); CORRECTIONS-RR (pool canonicalization dedupes by `request_id` keeping lexicographically smallest source-file path; `uuid` added as tertiary sort key; "impossible by request_id allocation" claim dropped; Hypothesis-property-tested for shuffle-invariance); CORRECTIONS-SS (CORRECTIONS-EE wording softened from "verbatim" to "strict generalization with strictly-stronger audit coverage"). |
| 0.1.2 closure-only review | 2026-05-16 | Wave 1 RC CLOSE_ALL (1 non-blocking NIT-B). Wave 2 Code Reviewer PARTIAL_CLOSE (1 NIT-B + 1 NIT-C, non-blocking, plan-emission approved). Wave 2 Model QA not re-reviewed (CLOSE_ALL at v0.1.1). All three channels approve plan emission. Reports at `scratch/2026-05-16-r6-spec-review/wave*_v0_1_2.md`. |
| 0.1.3 | 2026-05-16 | Documentation polish only (no methodology changes; no re-review required per reviewer non-blocking classification): NIT-B operative-residue cleanup (§1.2, §1.4, §3.3 R6Output row, §4 04_cap_wait.ipynb description); CORRECTIONS-TT integrates Code Reviewer NIT-C — pins missing-`request_id` behavior (drop legacy records) and tiebreaker collapse handling (lex-smallest `uuid` within same source-file path); §5.3 canonicalization rule expanded to 7 steps; sibling v0.2.1 plan-execution amendments list (`DevAICostError` parent + `MessageRecord.uuid` field) consolidated in frontmatter. **APPROVED for plan emission.** |
