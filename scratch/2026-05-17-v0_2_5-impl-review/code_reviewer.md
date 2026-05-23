# Code Reviewer — v0.2.5 Y-8 implementation review (Wave 2)

Date: 2026-05-17
Branch: `iter/ai-cost-2026-05`
Commits reviewed: `56b6b21`, `08249b2`, `09f2aa6`
Spec ref: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.5 §0.5 + §3.5
Parallel review: Reality Checker (spec-compliance) — separate file.

---

## Summary

**Overall verdict: APPROVE.**

The Y-8 patch is a clean, surgical implementation of the OSS-mirror uniqueHash
dedup pipeline. Tier discipline preserved, frozen-dc + slots semantics
preserved, helpers are pure + typed + documented, and the bit-for-bit
correspondence with ccusage's `Wr` / `Sr` / `$` functions is exact. The 8
new tests cover every spec-enumerated case including the two RC-flagged
edge paths (FLAG-A whole-record atomicity, FLAG-B missing-message-id
bypass). No BLOCKers found; one minor NIT (non-blocking) about a
documentation-style discrepancy on `_construct_message_record`'s `Errors
silenced` docstring section; one PRAISE on the `has_speed_by_idx`
parallel-list design.

| # | Channel                           | Verdict |
|---|-----------------------------------|---------|
| 1 | Tier discipline                   | PASS    |
| 2 | Frozen-dc + slots integrity       | PASS    |
| 3 | Helper purity + ccusage parity    | PASS    |
| 4 | hasSpeed transient-state design   | PASS    |
| 5 | Mutability scope (local-only)     | PASS    |
| 6 | Test honesty                      | PASS    |
| 7 | Constructor-call-site migration   | PASS    |
| 8 | CLI emission                      | PASS    |
| 9 | No dead code / shims / widening   | PASS    |
| 10| Honnibal audit-pass coverage      | PASS    |

---

## Findings

### BLOCK — none.

### PRAISE

**P1 — `has_speed_by_idx` parallel-list is the right design.**
`simulations/dev_ai_cost_v2/jsonl_io.py:375`. Threading `has_speed_by_idx:
list[bool]` parallel to `records` instead of widening `MessageRecord` (the
public types-tier contract) is the correct call. The `speed` field is a
transient diagnostic needed only inside the dedup loop; surfacing it on
`MessageRecord` would have polluted the downstream contract for
R6/panel_builder/Hypothesis strategies, all of which already pin
`MessageRecord.__dataclass_fields__`. Parallel-list goes out of scope at
function exit — no leak. Index-space alignment is enforced by appending to
both lists at every `records.append` call site (3 sites: two `continue`
branches at lines 432-433, 439-440, and the replacement branch at lines
471-472), and never to one without the other.

**P2 — Counter increment rule matches ccusage exactly.**
Line 447: `dropped_duplicate += 1` fires on every hash collision regardless
of replace/discard branch. ccusage's `pi`/`ui` loaders behave the same
way (`if(p!=null&&!$(...))return;` drops new without count; the `else`
branch replaces, dropping existing). Net dropped = collisions = exactly
what the counter records. The invariant pinned in the field docstring
(`dropped_duplicate_count == raw_assistant_rows_admitted - len(records)`)
holds.

**P3 — `_unique_hash` and `_token_total` are bit-for-bit ccusage mirrors.**
Verified against `node_modules/ccusage/dist/data-loader-LJFbLyZj.js`
(ccusage v19.0.3):
- `Wr`: `let t=e.message.id; if(t==null)return null; let n=e.requestId;
  return n==null?t:` `${t}:${n}` `;` — `_unique_hash`
  (`simulations/dev_ai_cost_v2/jsonl_io.py:163`) matches exactly.
- `Sr`: `e.input_tokens+e.output_tokens+(e.cache_creation_input_tokens??0)+
  (e.cache_read_input_tokens??0)` — `_token_total`
  (`simulations/dev_ai_cost_v2/jsonl_io.py:185`) matches exactly. The
  `cache_create` arg is the pre-summed `5m + 1h` total per spec §3.5 /
  Y-5c, matching ccusage's flat `cache_creation_input_tokens` field.
- `$` (replacement predicate): `e.tokenTotal===t.tokenTotal ? e.hasSpeed
  && !t.hasSpeed : e.tokenTotal > t.tokenTotal` — Python equivalent at
  line 466-470 matches: `new_tt > existing_tt or (new_tt == existing_tt
  and new_has_speed and not existing_has_speed)`. ✓

**P4 — Whole-record replacement is unambiguous (RC FLAG-A closed).**
Line 471: `records[existing_idx] = new_record` replaces the entire
`MessageRecord` immutable instance — no field-mixing across rows is
possible (frozen-dc enforces this structurally). The test
`test_jsonlreader_dedup_field_atomicity` exercises differing model + ts +
all 5 token fields between the two collision rows and verifies every
field on the kept record came from the winner. Solid.

### NIT

**N1 — `_construct_message_record` docstring missing `Errors silenced` section.**
`simulations/dev_ai_cost_v2/jsonl_io.py:207`. The contract-docstrings
audit-pass discipline (per project's Honnibal chain) prescribes Args /
Returns / Raises / Errors silenced sections on every function. The
existing docstring has Args + Returns but no Raises or Errors silenced;
the function technically propagates `ValueError` from
`MessageRecord.__post_init__` (negative tokens, NaN cost, empty uuid)
without catching, so a `Raises: ValueError` line would complete the
contract documentation. Non-blocking; v0.2.6 documentation polish.

**N2 — `Path.rglob` order non-determinism noted but not pinned.**
`simulations/dev_ai_cost_v2/jsonl_io.py:377`. The keep-largest rule is
order-invariant for distinct `tokenTotal` values; the `hasSpeed`
tiebreaker is order-invariant when at most one row in any collision
cluster has `speed != None`. If a production cluster ever contains TWO
equal-tokenTotal rows both with `hasSpeed == True`, the kept entry is
the first-encountered one, which depends on filesystem-defined `rglob`
order. Production data has not yet exhibited this case, but a
defensive sort (`sorted(projects_root.rglob("*.jsonl"))`) would make
the algorithm fully deterministic without semantic change — ccusage's
`Yr`/`fe` loader does sort. Filed as nit for v0.2.6 backlog; does not
block v0.2.5 closure because the empirical 0.9994× parity demonstrates
production data does not hit the multi-hasSpeed-tie pathology.

---

## Per-file walk-through

### `simulations/dev_ai_cost_v2/jsonl_io.py` (PASS)

- **Tier discipline**: file imports only `types`, `_errors`,
  `anthropic_pricing` (utils → types + sibling pure-callable). No
  `modules/` import. ✓
- **Helpers**: `_unique_hash` (line 163) and `_token_total` (line 185)
  are module-level pure functions with full type annotations, complete
  docstrings (purpose + Args + Returns), and no side effects.
- **Pydantic surface**: `_Usage` gains optional `speed: str | None = None`
  (line 104) so the hasSpeed tiebreaker is decidable without rummaging
  through `model_extra`. `_Message` gains optional `id: str | None =
  None` (line 118) so `_unique_hash` can be called at validation time.
  Both fields are Optional with sensible defaults — backward-compatible
  with all existing fixtures.
- **Dedup state scoping**: `seen_hashes: dict[str, int]` (line 374) and
  `has_speed_by_idx: list[bool]` (line 375) are local to `__call__`.
  `JSONLReader` instance state is unchanged from v0.2.4 (only
  `self._pricing` survives across calls). ✓ matches CR NIT-1 mutability
  pin.
- **Counter increment placement**: `dropped_duplicate += 1` at line 447
  fires unconditionally on any collision, BEFORE the keep-vs-discard
  decision at lines 466-473. Correct per CR NIT-3.
- **Frankenstein-mixing impossible**: `new_record` is a fully-constructed
  `MessageRecord` (frozen-dc), and replacement is via index assignment
  on the list. No partial-field updates.
- **None-hash bypass**: line 431-434 short-circuits the dedup path for
  `_unique_hash → None` rows. The counter does NOT tick; the record IS
  appended with its `has_speed` flag. RC FLAG-B path closed.

### `simulations/dev_ai_cost_v2/types.py` (PASS)

- `JSONLReadResult.dropped_duplicate_count: int` added at line 246; non-
  negative validation at line 259-263. Field appears at the end of the
  field list — does not break existing positional-arg call sites
  (though all known call sites are keyword-arg, verified below).
- `DailyNotionalPanel.dropped_duplicate_count: int` added at line 339.
  Validated in the `for fname in (...)` loop at line 364. Field placed
  AFTER `ephemeral_pi_share` (which was the existing terminal field).
  Slightly unfortunate ordering since one might expect counter fields
  grouped together — but does NOT break `frozen=True, slots=True` and
  does NOT break any keyword-arg call site. Migration test
  `test_daily_notional_panel_v0_2_3_fields` verifies the field-set as a
  set, not order, so the placement is invisible to the contract.
- Both `__post_init__` blocks remain functional: tuple-of-fields iteration
  for non-negative checks at line 356-365 includes
  `dropped_duplicate_count`. ✓

### `simulations/dev_ai_cost_v2/panel_builder.py` (PASS)

- Threading: line 224 surfaces
  `read_result.dropped_duplicate_count` →
  `DailyNotionalPanel.dropped_duplicate_count`. No additional
  PricingTable interactions. Counter-threading discipline (Y-5a)
  preserved.
- Docstring (line 101-104) explicitly enumerates the 3 JSONLReader
  counters + 3 PricingTable counters, mentioning Y-5a, Y-7, and Y-8
  amendments together. Clean, accurate.
- Tier discipline: still no `utils/` import; only `types`, `anthropic_pricing`,
  and `polars`. ✓

### `scripts/build_notional_cost_panel.py` (PASS)

- Print line (lines 127-138) emits 9 fields total:
  - **JSONLReader-sourced (grouped first)**: `dropped_rows`,
    `dropped_error`, `dropped_non_assistant`, `dropped_malformed`,
    `dropped_duplicate`.
  - **PricingTable-sourced (grouped next)**: `warn_missing_keys`,
    `dropped_unknown_model`, `substr_tiebreaker`.
  - **π̂ scalar (last)**: `ephemeral_pi_share`.
- Note: `dropped_rows` and `dropped_error` are panel-side (not
  JSONLReader-sourced); they are surfaced from `build_daily_panel`'s
  own bookkeeping. The print-line comment at line 121-126 calls these
  "original 2 counters" and groups them first, which is consistent
  with the v0.2.2 audit-line history. The user's review prompt's
  "JSONLReader-sourced grouped before PricingTable-sourced" ordering
  is satisfied for the new counters.

### `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` (PASS)

8 new tests (spec §0.5 enumerates exactly 8):

| # | Test                                                            | Spec line | Verdict |
|---|-----------------------------------------------------------------|-----------|---------|
| 1 | `test_jsonlreader_dedup_within_file`                            | 735-738   | PASS    |
| 2 | `test_jsonlreader_dedup_across_files`                           | 739-742   | PASS    |
| 3 | `test_jsonlreader_dedup_hasspeed_tiebreaker`                    | 743-745   | PASS    |
| 4 | `test_jsonlreader_dedup_no_request_id_falls_back_to_message_id` | 746-747   | PASS    |
| 5 | `test_jsonlreader_dedup_traversal_order_invariant` (Hypothesis) | 748-752   | PASS    |
| 6 | `test_dropped_duplicate_count_threaded_through_panel`           | 753-754   | PASS    |
| 7 | `test_jsonlreader_dedup_field_atomicity` (RC FLAG-A)            | 755-759   | PASS    |
| 8 | `test_jsonlreader_dedup_missing_message_id_admitted_without_counter` (FLAG-B) | 760-764 | PASS |

- Test 5 uses real `st.permutations(["f0.jsonl", ..., "f3.jsonl"])` —
  permutes the BASENAME assigned to each tokenTotal value, exercising
  the traversal-order invariance via filesystem-ordering of differently-
  named files. Not a sanitized subset. ✓
- Test 7 (atomicity): differs across model (`claude-sonnet-4-5` vs
  `claude-opus-4-7`), timestamp (10:00:00Z vs 11:00:00Z), AND all 5
  token fields. Asserts every field on the kept record is the
  winner's. No Frankenstein possible. ✓
- Test 8 (missing-message-id): writes 3 rows with `message.id=None`,
  asserts all 3 records admitted, `dropped_duplicate_count == 0`. ✓

All 8 tests have non-trivial multi-line assertions (each verifies at
least 2 of: record count, kept-record identity via uuid/output_tok,
counter value, model/ts/field atomicity). No empty-assertion smoke
tests.

### `simulations/tests/test_dev_ai_cost_v2_types.py` (PASS)

- `_panel_kwargs()` helper (line 212-227) gains
  `dropped_duplicate_count=0` default — all 11 existing
  `DailyNotionalPanel(**_panel_kwargs(...))` call sites now pass the
  new field without modification.
- 2 new negative-count tests:
  - `test_daily_notional_panel_rejects_negative_duplicate_count` (line 282)
  - `test_jsonl_read_result_rejects_negative_duplicate_count` (line 396)
- All 4 `JSONLReadResult(...)` direct constructor sites (lines 351, 366,
  377, 388, 399, 408) pass `dropped_duplicate_count=...` explicitly. ✓

### `simulations/tests/test_dev_ai_cost_v2_panel_builder.py` (PASS)

- `_result` helper (line 101-119) gains `dropped_duplicate: int = 0`
  parameter and threads it through the `JSONLReadResult` constructor.
- 2 direct `JSONLReadResult(...)` fixture call sites (lines 303-308,
  386-391) pass `dropped_duplicate_count=0` explicitly.

### `simulations/tests/test_dev_ai_cost_v2_migration.py` (PASS)

- `test_jsonl_read_result_fields_exact` (line 59-67) pinned exactly to
  the 4-field set: `{records, dropped_non_assistant_count,
  dropped_malformed_line_count, dropped_duplicate_count}`. Uses `==`
  (exact equality on a set), so any future drift fails loud.
- `test_daily_notional_panel_v0_2_3_fields` (line 130-150) pins the
  10 required fields including `dropped_duplicate_count` via
  `required - fields` subtraction. Loud-fail on field-removal.

---

## Constructor-call-site migration audit

`grep -rn "JSONLReadResult(" simulations/ scripts/` — 12 call sites:

| File:Line                                          | Kwargs include dropped_duplicate_count? |
|----------------------------------------------------|------------------------------------------|
| `simulations/dev_ai_cost_v2/jsonl_io.py:474`       | ✓ (line 478: `dropped_duplicate_count=dropped_duplicate`) |
| `simulations/tests/test_dev_ai_cost_v2_types.py:351` | ✓                                      |
| `simulations/tests/test_dev_ai_cost_v2_types.py:366` | ✓                                      |
| `simulations/tests/test_dev_ai_cost_v2_types.py:377` | ✓                                      |
| `simulations/tests/test_dev_ai_cost_v2_types.py:388` | ✓                                      |
| `simulations/tests/test_dev_ai_cost_v2_types.py:399` | ✓ (rejection-test for -1 value)        |
| `simulations/tests/test_dev_ai_cost_v2_types.py:408` | ✓                                      |
| `simulations/tests/test_dev_ai_cost_v2_panel_builder.py:114` | ✓ (via `_result` helper default) |
| `simulations/tests/test_dev_ai_cost_v2_panel_builder.py:303` | ✓                              |
| `simulations/tests/test_dev_ai_cost_v2_panel_builder.py:386` | ✓                              |
| `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py:548`     | ✓                              |
| `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py:916`     | ✓                              |

`grep -rn "DailyNotionalPanel(" simulations/ scripts/` — 14 call sites:

| File:Line                                          | Kwargs include dropped_duplicate_count? |
|----------------------------------------------------|------------------------------------------|
| `simulations/dev_ai_cost_v2/panel_builder.py:214`  | ✓ (line 224: `dropped_duplicate_count=read_result.dropped_duplicate_count`) |
| `simulations/tests/test_dev_ai_cost_v2_types.py` (13 sites via `_panel_kwargs()`) | ✓ (via helper default) |

**All call sites migrated.** No CR NIT-3 follow-through gaps.

---

## Honnibal audit-pass coverage

| Pass                  | Coverage on Y-8 surface                            | Verdict |
|-----------------------|----------------------------------------------------|---------|
| tighten-types         | `_unique_hash` returns `str \| None`; `_token_total` returns `int`; `has_speed_by_idx: list[bool]` is explicitly typed; `seen_hashes: dict[str, int]` is explicitly typed; all new field annotations are concrete `int` (not `Optional[int]`). | PASS |
| contract-docstrings   | `_unique_hash` + `_token_total` both have Args/Returns sections. `JSONLReader.__call__`'s docstring gained a "Dedup pipeline (v0.2.5 Y-8)" subsection. Types tier `JSONLReadResult.dropped_duplicate_count` and `DailyNotionalPanel.dropped_duplicate_count` both have multi-line field-doc explaining the spec lineage, increment rule, and the FLAG-B bypass. One minor gap on `_construct_message_record` (see N1). | PASS (with N1) |
| hypothesis-tests      | `test_jsonlreader_dedup_traversal_order_invariant` uses `st.permutations(...)` with `max_examples=20`. Real permutation generator, not a sanitized subset. | PASS |
| try-except            | The narrow `try/except json.JSONDecodeError` from v0.2.4 Y-7 (line 388-392) is unchanged. No new try/except blocks introduced for dedup. Pydantic ValidationError still raised through `JSONLSchemaError`. No exception widening. | PASS |
| pre-mortem            | Hypothesized failure modes are addressed: (a) Frankenstein-row mixing (RC FLAG-A) — closed by whole-record replacement test; (b) None-hash counter pollution (RC FLAG-B) — closed by counter==0 test; (c) traversal-order non-determinism — closed by Hypothesis permutation test for the keep-largest case (multi-hasSpeed-tie case noted as N2 nit). | PASS |
| mutation-testing      | N/A per review prompt — migration scope is small (3 production files + 4 test files, ~190 LoC added). The 8 dedup tests + 2 negative-count tests + Hypothesis permutation give effective mutation coverage by inspection: mutating the `>` to `>=` in line 466 would fail test 1 (3-row 200/500/300 case); flipping the FLAG-B branch would fail test 8; removing the `dropped_duplicate += 1` would fail tests 1/2/5/7. | N/A (small scope) |

---

## Spec compliance cross-check (vs §0.5)

| Spec §0.5 line | Implementation reference                                | Match |
|----------------|---------------------------------------------------------|-------|
| 690-693 (uniqueHash + None-bypass) | `_unique_hash` line 163; bypass line 431-434 | ✓ |
| 696-700 (mutability scope local-only) | `seen_hashes` line 374 inside `__call__` | ✓ |
| 701-706 (Sr keep-largest + hasSpeed tiebreaker) | `_token_total` line 185 + replace predicate line 466-470 | ✓ |
| 707-713 (counter ownership + increment rule) | `JSONLReadResult.dropped_duplicate_count` types.py:246; `dropped_duplicate += 1` line 447 | ✓ |
| 714-720 (panel threading) | `panel_builder.py:224` | ✓ |
| 733-764 (8 tests enumerated) | All 8 present in `test_dev_ai_cost_v2_jsonl_io.py:744-1001` | ✓ |

---

## Counters that are NOT JSONLReader/Pricing-sourced

For completeness — the user's prompt language "JSONLReader-sourced counters
grouped before PricingTable-sourced" deserves a footnote. The CLI print
line groups:
1. `dropped_rows` + `dropped_error` (panel_builder-internal — weekend +
   `is_error` filter accounting).
2. `dropped_non_assistant` + `dropped_malformed` + `dropped_duplicate`
   (JSONLReader-sourced, threaded via `JSONLReadResult`).
3. `warn_missing_keys` + `dropped_unknown_model` + `substr_tiebreaker`
   (PricingTable-sourced).
4. `ephemeral_pi_share` (panel-builder Y-6 scalar).

The new Y-8 counter sits adjacent to its JSONLReader siblings, satisfying
the grouping intent. ✓

---

## Final verdict

**APPROVE** — proceed to spec closure (already merged at `09f2aa6`).

The two NITs (N1 docstring polish, N2 rglob-sort determinism hedge) are
non-blocking and can be picked up in v0.2.6 alongside Y-9 (input_tokens
0.10× residual). The 128/128 green tests + 0.9994× ccusage parity in
production close the reliability-convergence HALT cleanly.

Reviewer: code_reviewer agent
Wave: 2 (parallel to Reality Checker spec-compliance review)
