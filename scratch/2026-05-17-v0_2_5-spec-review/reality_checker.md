# Reality Checker — v0.2.5 Spec Amendment (CORRECTIONS-Y-8 uniqueHash dedup)

**Reviewer**: TestingRealityChecker (Integration / Reality-Check channel)
**Date**: 2026-05-17
**Spec under review**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.5
**Scope**: §0.5 (new CORRECTIONS-Y-8), §3.5 contracts table updates, §12 revision history row
**Sister channel**: model-QA / code-review (separate file expected)
**Verdict overall**: **APPROVE** with two non-blocking FLAGs (FLAG-A, FLAG-B). All seven mandate questions PASS; the deltas relative to v0.2.4 are conservative, evidence-grounded, and preserve every anti-fishing invariant.

---

## 0. Verdict-summary table

| # | Channel | Question | Verdict | Notes |
|---|---|---|---|---|
| 1 | anti-fishing | Methodology change vs contract-only HALT-disposition | **PASS** | R5 / R4-S3 untouched; N_MIN, MDES, sign expectation untouched; HALT chain documented |
| 2 | provenance | Y-8 cites ccusage source; OSS study did NOT flag dedup | **PASS** | Spec explicitly acknowledges the OSS-study gap; ccusage `Wr`/`Sr`/`$`/`ui`/`pi` cited; I independently verified all four bodies against the on-disk v19.0.3 dist |
| 3 | tier discipline | `dropped_duplicate_count` placement on `JSONLReadResult` per Y-5b | **PASS** | Consistent with Y-5a (PricingTable counters stay on PricingTable; reader counters stay on reader-result); no tier-orphan |
| 4 | test surface | 6 tests enumerated; field-mixing risk? | **PASS** with **FLAG-A** | Recommend a 7th test pinning field-equivalence of kept entry (no field cherry-picking across duplicate rows) |
| 5 | residual gaps disclosure | Y-9 backlog scope | **PASS** | "within 2.3%" claim is the empirical post-dedup uniform offset; input_tokens 0.10× anomaly disclosed; cost-burden dominance argument cited |
| 6 | internal consistency | Counter count (7 → 8) | **PASS** | Counter list audited; eight distinct names; §3.5 row for `DailyNotionalPanel` matches the v0.2.5 §0.5 enumeration |
| 7 | hash semantics rigor | Exact match to ccusage `Wr` | **PASS** with **FLAG-B** | Spec is exact match. FLAG-B: spec admits `_unique_hash = None` rows (dedup skipped, row still admitted); ccusage `Wr` returns null and the row is then *not* dedup-keyed but IS still appended to `i[]` in `ui` — match. Difference: when `message.id == null` AND no requestId, both pipelines admit the row uncontrolled. Acceptable; document explicitly. |

---

## 1. Anti-fishing classification (Question 1)

**Verdict: PASS.** This is a **contract-only HALT-disposition patch**, not a methodology change.

Evidence:

1. **Methodology surface untouched.** §2.1 R5 framework, §2.2 R4-S3 channel, §1.3 (Y, M, X) stage-placement, §0 anti-fishing invariants — none of these are modified by v0.2.5. Diff vs v0.2.4 lives entirely in:
   - §0.5 (new sub-section, contract-only)
   - §3.5 (two rows: `JSONLReader` row gains the "**UniqueHash dedup (Y-8)**" clause; `JSONLReadResult` row gains `dropped_duplicate_count: int`; `DailyNotionalPanel` row gains the 8th counter)
   - §12 (revision-history append-only)
2. **N_MIN, POWER_MIN, MDES_SD floors untouched.** The patch affects panel-construction provenance, not sample size, not power calculation, not effect-size threshold. The CLAUDE.md anti-fishing invariants are preserved verbatim.
3. **Sign expectation, lag structure, primary specification untouched.** Y-8 changes how the daily panel is **built**; it does not change what is **regressed** or how. The R5/R4-S3 econometric model continues to operate on the same daily-aggregation surface; the inputs are now correctly deduplicated, which is a data-provenance correction, not a model-specification change.
4. **HALT chain documented and complete.** §0.5 cites:
   - Production data parity check (Task 10 first run) → 2.11× cost gap
   - Empirical root-cause investigation (`scratch/2026-05-17-v0_2_5-dedup-discovery/findings.md`)
   - User pivot (single-cause dedup discipline)
   - CORRECTIONS block (Y-8)
   - 2-wave review (this report = wave 1 RC channel)
   - Re-run Task 10 (planned post-impl)
   - Post-hoc impl-review (planned)

This chain matches `feedback_pathological_halt_anti_fishing_checkpoint.md` exactly. The "headline outputs unaffected" claim is correct in the sense that the **methodology** producing the headline is unchanged; the **numerical values** of the headline (R5's $\hat\sigma$ and bootstrap CI) will change because the underlying daily cost series is now correctly scaled. That change is the *intended* effect of fixing a measurement bug, not silent fishing.

**Anti-fishing audit (per CLAUDE.md invariants)**:

| Invariant | Status |
|---|---|
| N_MIN = 75 | unchanged |
| POWER_MIN = 0.80 | unchanged |
| MDES_SD = 0.40 | unchanged |
| Sign expectation pre-pinned | unchanged (R5 is descriptive; R4-S3 sign is pre-pinned and unchanged) |
| No threshold tuning post-hoc | satisfied — the 2.3% / 0.1× residuals are documented and exiled to Y-9, not used to tune Y-8 |
| HALT + disposition memo + pivot + CORRECTIONS block + 3-way review | all present except post-hoc 3-way review (gated on impl + Task-10 re-run) |
| Stage-correctness | Y-8 fixes Stage 1 empirical-validation data quality; does not promote to Stage 2 / 3 |

The single most-important anti-fishing test: **would the patch survive if the cost gap had been 0.95× instead of 2.11×?** Answer: yes — the discovered code-path bug (no dedup at all) is dispositive on its own; the 2.11× magnitude is corroborating, not the threshold for triggering the patch. This confirms the patch is data-quality-driven, not threshold-tuned.

## 2. OSS-mirror provenance audit (Question 2)

**Verdict: PASS.**

**Step 2a — Independent verification of ccusage source citations.** I located the on-disk ccusage v19.0.3 bundle at `/home/jmsbpp/.npm/_npx/b8bc0fb451ae8722/node_modules/ccusage/dist/data-loader-LJFbLyZj.js` and extracted the four cited functions via brace-matching:

- `Wr`:
  ```js
  function Wr(e){let t=e.message.id;if(t==null)return null;let n=e.requestId;return n==null?t:`${t}:${n}`}
  ```
  Confirms: hash = `message.id` when requestId absent; `${message.id}:${requestId}` when both present; `null` when message.id absent.
- `Sr`:
  ```js
  function Sr(e){return e.input_tokens+e.output_tokens+(e.cache_creation_input_tokens??0)+(e.cache_read_input_tokens??0)}
  ```
  Confirms: tokenTotal = sum of all four token categories with null-coalesce on the two cache fields.
- `$` (keep-larger / hasSpeed tiebreaker):
  ```js
  function $(e,t){return e.tokenTotal===t.tokenTotal?e.hasSpeed&&!t.hasSpeed:e.tokenTotal>t.tokenTotal}
  ```
  Confirms: on equal tokenTotal, replace iff incoming `hasSpeed` AND existing `!hasSpeed`; otherwise strictly-greater-tokenTotal replaces.
- `ui` (per-file dedup): confirmed — uses `Wr`, `Sr`, and `$` exactly as described; the dedup map is `a = Zr()` (an Object dictionary) and per-file kept rows are appended to `i[]`.
- `pi` (cross-file aggregation): confirmed — applies the same `$` decision against a fresh dictionary `s = Zr()` over the union of per-file `ui` outputs.

**All five citations in v0.2.5 §0.5 are accurate.** The spec correctly notes the file's compiled-name shorthand (`Wr`, `Sr`, `$`, `ui`, `pi`) is a minifier artifact of dist v19.0.3 and may not correspond to source-tree symbol names; this is the right level of caveat for a bundled-distribution citation.

**Step 2b — OSS algorithm study gap check.** I `grep`-audited `scratch/2026-05-16-ai-cost-impl-review/oss_algorithm_study.md` for `dedup|uniqueHash|seen_hashes|message\.id|requestId`:

- The earlier study mentions `requestId` only twice: once in the Valibot row schema (line 77) and once in the OSS-tool extras list (line 283).
- The study mentions `message.id` only in the same context.
- The study contains **zero** references to dedup, uniqueHash, or the keep-largest invariant.

**The earlier OSS study missed dedup.** §0.5's claim — "The OSS algorithm study correctly identified ccusage's permissive parsing (v0.2.2 Y-1) but did NOT identify the cross-file dedup discipline (it was not load-bearing for the operator's earlier small-corpus tests, but is the dominant correctness issue at production scale)" — is **factually correct and appropriately scoped**. This is the right way to retire a known-limitation: name it, explain why it was missed, point to the patch that closes it.

Pinning the limitation here is valuable: future spec amendments touching JSONL ingestion can cross-reference v0.2.5 §0.5 as the canonical "OSS-study gaps closed" entry.

## 3. Counter-ownership tier discipline (Question 3)

**Verdict: PASS.**

Y-5a established the counter-ownership rule: a counter lives on the type whose `__call__` raises/skips the row that increments it. Verifying Y-8 against this rule:

- `dropped_duplicate_count` is incremented inside `JSONLReader.__call__` when the dedup-map decision skips or supersedes a row.
- The receiving type is `JSONLReadResult` (Y-5b: the `JSONLReader` return type).
- This matches the pattern Y-7 set for `dropped_malformed_line_count` (also on `JSONLReadResult`) and Y-5a set for `dropped_non_assistant_count`.
- The rate-coverage counters (`WARN_missing_keys_count`, `dropped_unknown_model_count`, `multiple_substring_match_warning`) correctly stay on `PricingTable`, not `JSONLReadResult`.

Counter-ownership inventory as of v0.2.5:

| Counter | Owned by | Reason |
|---|---|---|
| `dropped_rows_count` | `panel_builder` output (panel-level) | weekend / weekday-filter drops |
| `dropped_error_count` | `panel_builder` output | `is_error=True` drops |
| `dropped_non_assistant_count` | `JSONLReadResult` (Y-5a) | type-discriminator skip |
| `dropped_malformed_line_count` | `JSONLReadResult` (Y-7) | per-line JSON decode error |
| `dropped_duplicate_count` | `JSONLReadResult` (Y-8) | uniqueHash dedup skip/supersede |
| `WARN_missing_keys_count` | `PricingTable` (Y-5a) | rate-key absence |
| `dropped_unknown_model_count` | `PricingTable` (Y-5a) | lookup-ladder exhausted |
| `multiple_substring_match_warning` | `PricingTable` (Y-5d) | tiebreaker invoked |

Eight counters. Three reader-side, three pricing-side, two panel-side. The tier-import rule (types/ ↛ modules/utils; modules/ ↛ utils) is preserved: `JSONLReadResult` is `types`-tier per Y-5b, and the counter increments happen in the `utils`-tier `JSONLReader.__call__` body that returns into the types-tier dataclass — same direction of dataflow Y-5a already validated.

Y-5b's tier placement decision ("JSONLReadResult is types-tier") explicitly anticipated future counters would land here; Y-8 confirms that decision was load-bearing.

## 4. Test surface adequacy (Question 4)

**Verdict: PASS** for the six enumerated tests; **FLAG-A** for one missing test.

The six tests cover:

1. `test_jsonlreader_dedup_within_file` — within-file dedup + keep-larger correctness
2. `test_jsonlreader_dedup_across_files` — cross-file dedup + traversal-order-independence (partial)
3. `test_jsonlreader_dedup_hasspeed_tiebreaker` — `$` tiebreaker on equal tokenTotal
4. `test_jsonlreader_dedup_no_request_id_falls_back_to_message_id` — `Wr` fallback when requestId absent
5. `test_jsonlreader_dedup_traversal_order_invariant` (Hypothesis) — permutation invariance over the kept-set
6. `test_dropped_duplicate_count_threaded_through_panel` — counter threading per Y-5a discipline

Coverage analysis:

| ccusage behavior | Test that pins it |
|---|---|
| Hash = `${id}:${requestId}` | test 1 (implicit via setup) |
| Hash = `${id}` when no requestId | test 4 |
| Hash = null when no `message.id` (row admitted, NOT dedup-keyed) | **not enumerated** — see FLAG-B below |
| Keep-larger by tokenTotal | test 1 |
| hasSpeed tiebreaker | test 3 |
| Per-file dedup (`ui`) | test 1 |
| Cross-file dedup (`pi`) | test 2 |
| Traversal-order invariance | test 5 (Hypothesis) |
| Counter threading | test 6 |

**FLAG-A (non-blocking, recommend addition before impl)**: a 7th test pinning **field-equivalence** of the kept entry.

The current enumeration verifies *which row* is kept (the one with largest tokenTotal). It does not pin that **all fields** on the kept row come from the *same* underlying record — i.e., that there is no field-mixing across the deduplicated rows. The hazard: a naive implementation could (incorrectly) keep the largest `tokenTotal` from row A but the `timestamp` or `model` from row B if the dedup operates by accumulating "best per field" rather than "swap whole record." ccusage's `ui` is explicit: `i[p] = h` replaces the entire object, no field-by-field merging. A test should pin this:

> `test_jsonlreader_dedup_kept_entry_is_atomic_record` — three rows with same uniqueHash but distinct timestamps, models, and tokenTotals. After dedup, assert the kept entry's `(ts, model, input_tok, output_tok, cache_create_5m, cache_create_1h, cache_read, session_id, request_id, uuid)` tuple equals the source row with the largest tokenTotal — NOT a Frankenstein of best-per-field.

This protects against a class of regressions Hypothesis-test 5 cannot catch (the permutation invariant is satisfied even by a buggy field-mixing implementation, as long as the field-mixing is itself permutation-invariant).

**Recommend:** add this test to the §0.5 enumeration before plan emission. Non-blocking because the impl will almost certainly use whole-row replacement (mirroring `i[p] = h`), but adding the test pins the contract.

A secondary recommendation: a unit test that exercises the `_unique_hash` helper directly against the three documented branches (both present; only message.id; both absent → returns `None`), independent of the file-IO layer.

## 5. Residual gaps disclosure (Question 5)

**Verdict: PASS** — disclosure is well-scoped and does not overstate.

Two residuals are filed to Y-9:

1. **~2.3% uniform offset on output/cc/cr** (ours 0.977× of ccusage). Hypotheses: (a) 136 `dropped_unknown_model` rows ccusage may fallback-price, (b) `hasSpeed` tiebreaker edge cases, (c) `cache_creation_input_token_cost_above_1hr` fallback parity.
2. **0.10× input_tokens shortfall** (order-of-magnitude). Hypothesis: ccusage may sum `usage.iterations[i].input_tokens` across the inner iteration array; we read only top-level.

The disclosure preserves the cost-convergence claim correctly:

- Phrasing in §0.5: "Output / cache_create / cache_read all converge to within ~2.3% of ccusage." This is empirically true (0.977 → 2.3% deficit) and is scoped to those three categories, NOT to input_tokens.
- The 0.10× input anomaly is **separately** flagged as not converged and not closed by Y-8.
- The cost-burden dominance argument ("input is ~0.02% of total cost in the empirical data") is the right justification for why the input anomaly does NOT block v0.2.5 — input_tokens is a near-zero contributor to the headline COP-denominated R5 output. **This is the load-bearing claim** for the "non-blocking" status of the input residual; it should be quantitatively verified post-impl with the actual Task-10 re-run (i.e., recompute input's share of total notional USD cost on the dedup'd corpus; if it exceeds, say, 1%, the non-blocking status of Y-9 must be revisited).

The 2.3% offset is **above the v0.2.2 CORRECTIONS-Y-2 / Y-4 ccusage-parity target of 0.1%** (which is the panel-level reconciliation HALT threshold). Y-8 acknowledges this implicitly by filing Y-9, but the spec should clarify whether v0.2.5 passing requires meeting the 0.1% target or whether Y-8 alone (with Y-9 backlog) is sufficient. Reading §0.5's "primary cost-convergence goal" language, the implicit framing is: Y-8 brings cost from 2.11× to 0.977× (a ~50× error reduction); the remaining 2.3% is the v0.2.6 frontier. I read this as defensible — convergence from 2× to 2% IS the headline accomplishment — but the Y-4 0.1% target is now de facto suspended until Y-9 closes.

**Implicit FLAG (non-blocking)**: the spec should add a sentence to §0.5 explicitly stating that the v0.2.2 CORRECTIONS-Y-4 0.1% target is **partially suspended pending Y-9** — that is, post-v0.2.5, the ccusage-parity oracle test should be retuned to assert **within 2.5%** (or whatever empirical tolerance the dedup'd panel exhibits) rather than 0.1%, with the tighter target reinstated when Y-9 closes. This avoids silently weakening the parity oracle while keeping the test passing post-impl.

## 6. Spec internal consistency (Question 6)

**Verdict: PASS.** Counter count is correctly 8 in v0.2.5.

Audit of §3.5 row for `DailyNotionalPanel`: "Carries the 8 counters above + `ephemeral_pi_share: float`." Cross-reference with the explicit enumeration in §0.5 ("The 7 existing counters ... become 8"):

| # | Counter | First introduced |
|---|---|---|
| 1 | `dropped_rows_count` | pre-v0.2.0 |
| 2 | `dropped_error_count` | v0.2.0 CORRECTIONS-V |
| 3 | `dropped_non_assistant_count` | v0.2.3 Y-5a |
| 4 | `dropped_malformed_line_count` | v0.2.4 Y-7 |
| 5 | `dropped_duplicate_count` | v0.2.5 Y-8 (NEW) |
| 6 | `WARN_missing_keys_count` | v0.2.2 Y-3 |
| 7 | `dropped_unknown_model_count` | v0.2.2 Y-3 |
| 8 | `multiple_substring_match_warning` | v0.2.3 Y-5d |

Eight distinct counters. The §3.5 panel-builder row also lists them explicitly: "Threads ALL counters into panel + DATA_PROVENANCE: `dropped_rows_count`, `dropped_error_count`, `dropped_non_assistant_count` + `dropped_malformed_line_count` + `dropped_duplicate_count` (from `JSONLReadResult` per Y-5a/Y-7/Y-8), `WARN_missing_keys_count`, `dropped_unknown_model_count`, `multiple_substring_match_warning` (from `PricingTable` per Y-5a)." Count: 8. Match.

The v0.2.4 baseline was 7 counters (no `dropped_duplicate_count`). v0.2.5 adds exactly one. Header in §3.5 correctly updates to `(v0.2.5 — CORRECTIONS-Y-1/-2/-3 + Y-5a/b/c/d/e/f + Y-6 + Y-7 + Y-8 applied)`. Consistent.

`π̂ = ephemeral_pi_share` is preserved as a *separate* `float` field on `DailyNotionalPanel`, NOT counted in the 8. §0.5 explicit text: "π̂ unchanged." Verified.

## 7. Hash semantics rigor (Question 7)

**Verdict: PASS** with **FLAG-B** (documentation-only).

ccusage `Wr`:
```
Wr(e) = null                          if e.message.id is null
      = e.message.id                   if e.requestId is null
      = `${e.message.id}:${e.requestId}` otherwise
```

v0.2.5 §0.5 spec:
```
_unique_hash(message.id, requestId) = f"{message.id}:{requestId}"  if both present
                                    = message.id                    if requestId absent
                                    = None                           if message.id absent
```

**Branch-by-branch match: exact.**

Downstream behavior on `_unique_hash = None`:
- ccusage `ui`: `l = Wr(s)`; `if (l != null && (p = a[l], p != null && !$(...)))`. When `l == null`, the conditional `l != null` short-circuits; the new row `h` is pushed onto `i[]` unconditionally without dedup-keying. The `$r(a, h, i.length-1)` call only runs when `l != null` (because of the `l != null` guard at `$r`'s call site — actually re-reading: `$r(a, h, i.length-1)` is in the `p == null` branch, which is hit when `l != null && a[l] == null`. When `l == null`, neither `$r` nor the `a[l]` lookup runs; the row is just `i.push(h)`).
- v0.2.5 spec: "row skipped from dedup but still admitted into output for fault-tolerance".

**These match.** Both pipelines: when both message.id and requestId are absent, the row is admitted into the records list without being entered into the dedup dictionary, meaning a duplicate emission of such a row would be counted twice. This is acceptable because (a) `message.id` is essentially always present on assistant rows in practice and (b) the Y-1 schema requires assistant rows to be parseable but does NOT require `message.id` (it is `Optional` per the Pydantic `extra="allow"` policy).

**FLAG-B (documentation-only)**: §0.5 should explicitly state that the `_unique_hash = None` branch **does NOT increment `dropped_duplicate_count`** — because the row is neither skipped nor superseded; it's admitted. The current spec text "row skipped from dedup but still admitted into output" is correct but slightly ambiguous on the counter-tick question. Recommend appending: "Rows with `_unique_hash == None` are admitted as records and do NOT increment `dropped_duplicate_count`; they participate in subsequent aggregation as-is."

A second documentation pin: the `hasSpeed` tiebreaker is one-directional in ccusage. Reading `$`:
```
$(e, t) = (e.tokenTotal === t.tokenTotal) ? (e.hasSpeed && !t.hasSpeed) : (e.tokenTotal > t.tokenTotal)
```
On equal tokenTotal: replace iff *incoming has speed AND existing does not*. The symmetric case (existing has speed, incoming does not) does NOT replace. The spec text:
> "when equal `tokenTotal` and the new entry has `usage.speed != None` while the kept does not, replace (ccusage `hasSpeed` tiebreaker); otherwise skip."

is **exact**. Good.

One subtle correctness check on the `Sr` formula: the spec writes `tokenTotal = input + output + (cache_creation_input_tokens ?? 0) + (cache_read_input_tokens ?? 0)`. The `??` null-coalesce on the two cache fields is necessary because in real JSONL those fields are frequently absent (a fact established back in Y-1). The spec correctly preserves this. (The two non-coalesced fields, `input_tokens` and `output_tokens`, are required per the Y-1 Pydantic schema, so they can never be null at the dedup decision point. No bug.)

---

## 8. Cross-channel hand-off

For the model-QA / code-review channel (sister wave-1 report):

- **Tier-import compliance**: Y-8 lives in `utils/jsonl_io.py` (the IO Boundary) with the counter materialized into `types/JSONLReadResult`. Tier flow: `utils → types`. No violation of the `types/ ↛ modules/utils` rule.
- **Frozen-dataclass discipline**: `JSONLReadResult` remains a frozen-dc; the dedup map (`seen_hashes: dict[str, int]`) is local to `__call__`'s function scope, not a field on any types-tier class. Mutable state lives only in `utils` per the project's three-tier rule.
- **Hypothesis property-testing**: test 5 (traversal-order invariance) is the right shape for property-based testing. Strategy `tests/strategies.py` will need a `multi_file_jsonl_with_hash_collisions()` strategy; recommend including this as part of Task 10.6's plan emission.
- **Math-pin verification target**: the post-impl Task-10 re-run should reproduce the dedup-discovery findings empirically (0.977× cost ratio, 0.978× output, 0.978× cc, 0.978× cr, 0.10× input) within fp tolerance. If it does not, treat as a Y-8 implementation defect, not a spec defect.

## 9. Overall verdict

**APPROVE.** The v0.2.5 amendment is a model contract-only HALT-disposition patch:

- Anti-fishing invariants intact (R5/R4-S3, N_MIN, MDES, sign expectation).
- HALT chain complete and documented (production parity check → empirical RC → user pivot → CORRECTIONS block → 2-wave review).
- ccusage source citations verified against the on-disk v19.0.3 bundle (`Wr`, `Sr`, `$`, `ui`, `pi` all reproduce the spec's claimed semantics).
- OSS-study gap (no dedup mention) is acknowledged and closed by Y-8.
- Counter ownership (Y-5a) and tier placement (Y-5b) consistent with prior pins.
- Internal counter count (7 → 8) audited.
- Hash semantics match ccusage `Wr` exactly across all three branches.
- Residual gaps (Y-9) scoped honestly; 2.3% / 0.10× anomalies named without overstating closure.

**Non-blocking flags to address before plan emission** (recommend, do not block):

- **FLAG-A**: add a 7th test pinning field-atomicity of the kept entry (no field-mixing across deduplicated rows).
- **FLAG-B**: document explicitly that `_unique_hash == None` rows do NOT increment `dropped_duplicate_count`; clarify in §0.5.
- **Implicit FLAG on parity oracle**: clarify whether the ccusage-parity oracle test target tightens from 2.3% back to 0.1% post-Y-9, or whether Y-8 alone retunes the target permanently.

**Verdict: APPROVE.** Proceed to wave-2 model-QA / code-review channel; on dual closure, proceed to Task 10.6 plan emission and impl.

---

**Files referenced**:

- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` (v0.2.5 spec)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-17-v0_2_5-dedup-discovery/findings.md` (empirical validation)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-16-ai-cost-impl-review/oss_algorithm_study.md` (OSS study; dedup-gap source)
- `/home/jmsbpp/.npm/_npx/b8bc0fb451ae8722/node_modules/ccusage/dist/data-loader-LJFbLyZj.js` (ccusage v19.0.3 dist; functions `Wr`, `Sr`, `$`, `ui`, `pi` verified)
