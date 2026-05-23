# Reality Checker — v0.2.4 Y-7 impl-review

**Scope**: post-hoc impl-review of `134cbcb` (source) + `07f907f` (tests) against
spec v0.2.4 §0.4 CORRECTIONS-Y-7 + §3.5 contract table + Task-10 disposition.
**Reviewer**: TestingRealityChecker (skeptic; default = NEEDS WORK).
**Date**: 2026-05-17.

## Verdict summary
**APPROVE.** Six enumerated tests are all present and exercise the claimed
contract; the source patch is minimal, narrowly scoped, threaded correctly
through the modules tier into `DailyNotionalPanel`; production-run counter
audit values are operationally plausible and match the disposition memo. No
test softening, no `pytest.skip` bypasses, no regression to v0.2.3 CR-Z pins.
Anti-fishing chain holds: the patch closes the HALT without backsliding on
prior architectural commitments.

## Per-check

### 1. Y-7 contract honored — narrow `except json.JSONDecodeError`
**PASS.** `simulations/dev_ai_cost_v2/jsonl_io.py:294-298` wraps **only** the
`json.loads(stripped)` call in `try/except json.JSONDecodeError`. The
Pydantic `ValidationError` catch at line 308-313 remains in place and still
raises `JSONLSchemaError` with `{path}:{line_no}` context. Catch is not
widened to `Exception` and not widened to `ValueError`. Module-level docstring
(lines 21-26 + 260-268) names the narrow scope explicitly and asserts
"Pydantic schema errors on valid JSON still raise JSONLSchemaError" —
behavior-test FLAG-4b at `test_dev_ai_cost_v2_jsonl_io.py:589-612` proves it.

### 2. Counter ownership preserved — `JSONLReadResult`, not `PricingTable`
**PASS.** `dropped_malformed_line_count: int` is declared on
`types.JSONLReadResult` (`types.py:230-232`), validated `≥ 0` in
`__post_init__` (lines 240-244), and surfaced on `DailyNotionalPanel`
(types.py:311; validated lines 332-345). `panel_builder.build_daily_panel`
reads `read_result.dropped_malformed_line_count` (panel_builder.py:219) and
threads it into `DailyNotionalPanel(...)`. The counter is **never** touched
by `PricingTable` — CR-Z-1 ownership pin (`test_dev_ai_cost_v2_types.py:398`,
`:420`) still holds and is exercised.

### 3. Six enumerated tests present
**PASS.** All six required tests exist in
`simulations/tests/test_dev_ai_cost_v2_jsonl_io.py`:

| Required test | Line | Asserts |
|---|---|---|
| `test_jsonlreader_skips_trailing_null_bytes` | 459 | 3 records parsed; `dropped_malformed_line_count == 1`; 3000-byte trailing `\x00` block |
| `test_jsonlreader_skips_truncated_json` | 495 | mid-line partial-write → 1 record + counter==1 |
| `test_dropped_malformed_line_count_threaded_through_panel` | 520 | `DailyNotionalPanel.dropped_malformed_line_count == 7` (modules-tier thread-through) |
| `test_jsonlreader_blank_lines_do_not_increment_malformed_counter` (FLAG-4a) | 562 | blank/whitespace-only/tab-only lines → counter==0 |
| `test_jsonlreader_valid_json_invalid_schema_still_raises` (FLAG-4b) | 589 | valid JSON, missing `input_tokens` → `JSONLSchemaError` |
| `test_jsonlreader_line_conservation_property` (CR-7-N2 Hypothesis) | 623 | `@given` random bytes → `malformed + records + non_assistant + blank_inferred == total_lines` |

### 4. Anti-fishing audit
**PASS.** No `pytest.skip`/`xfail`/`skipif` markers anywhere in the v2 test
suite (`grep -nE "pytest\.skip|@pytest\.mark\.skip|@pytest\.mark\.xfail|skipif"`
returned empty). Test count deltas in review range:

- `test_dev_ai_cost_v2_jsonl_io.py`: 21 → **27** (+6, all Y-7).
- `test_dev_ai_cost_v2_types.py`: 41 → **43** (+2: `_rejects_negative_malformed_count` ×2 for both containers).
- `test_dev_ai_cost_v2_panel_builder.py`: 15 → **15** (no net add, but `_result` helper updated + 2 existing tests pass the new field as 0 — back-compat, not softening).
- `test_dev_ai_cost_v2_migration.py`: assertion strengthened from
  `fields == {records, dropped_non_assistant_count}` to require the new
  malformed field — this is a tightening, not a softening.

**Net suite delta: +8 tests, zero deletions, zero relaxations.** Existing
tests were updated to thread the new constructor kwarg (default `=0`); no
existing assertion was weakened or removed.

### 5. Production-run faithfulness
**PASS.** DATA_PROVENANCE.md counter audit table enumerates exactly **7
counters + π̂**, source tiers correctly labeled (3 PricingTable-side, 2
JSONLReader-side, 2 panel_builder-side, 1 scalar). Values:

- `dropped_malformed_line_count = 1` matches the single Task-10 trailing-null
  byte block in the disposition memo. **Plausible.**
- `dropped_unknown_model_count = 136` against `dropped_non_assistant_count
  = 134,102` is roughly 0.1% of assistant rows — operationally consistent
  with stray sentinel `model: "claude-3"` shorthand and test-session rows
  that don't survive the exact → `anthropic/` → longest-substring ladder.
  **Plausible.**
- `substr_tiebreaker = 0`: LiteLLM's `claude-*` keys disambiguate uniquely
  for the corpus's actual model names (`claude-sonnet-4-5`,
  `claude-sonnet-4-6`, `claude-haiku-4`), so the alphabetical tiebreaker is
  never invoked. **Plausible** and matches CR-Z-4 design intent (tiebreaker
  exists for defensive correctness, not as a typical-path mechanism).
- `ephemeral_pi_share = 0.418827` ∈ [0, 1], finite. **Plausible.**

### 6. No regression in v0.2.3 CR-Z pins
**PASS.** Spot-checked each:

- **CR-Z-1 counter ownership**: `test_cr_z_1_pricingtable_owns_warn_missing_keys_count`
  + `test_cr_z_1_jsonlreadresult_owns_dropped_non_assistant_count` present.
- **CR-Z-2 tier placement**: `test_jsonl_read_result_importable_from_types`
  + `test_jsonl_read_result_not_exported_from_jsonl_io` present.
- **CR-Z-3 aggregation locus (5m+1h sum at PricingTable)**: untouched in
  this diff; pricing module not modified.
- **CR-Z-4 tiebreaker**: pricing module unmodified; tests in
  `test_dev_ai_cost_v2_pricing.py` untouched.
- **CR-Z-5 uuid synthesis (basename-bound)**: `_synth_uuid` unchanged
  (`jsonl_io.py:115-130`); `test_cr_z_5_synth_uuid_path_independent_basename_bound`
  intact.

## Overall verdict
**APPROVE.** The HALT is closed. The patch is narrowly scoped, contractually
documented, end-to-end threaded, and proven by 6 dedicated tests + 1
Hypothesis conservation property. Anti-fishing chain holds. Counter audit
in DATA_PROVENANCE.md matches the production-run emit line and is
operationally plausible across all 7 fields. No deferred technical debt
beyond what spec §0.4 already enumerates as "v0.2.5 deferred work" (hard-fail
threshold on `dropped_malformed_line_count / total_lines`, DATA_PROVENANCE
schema pin, ccusage-parity oracle).

Cleared to proceed to Task 11 (β̂ estimation on N=29, expected power-HALT
already disposition-staged at `notebooks/dev_ai_cost_v2/dispositions/power_halt_template.md`).
