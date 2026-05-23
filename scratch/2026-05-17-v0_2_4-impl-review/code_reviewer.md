# Code Reviewer Report — v0.2.4 Y-7 Implementation

**Scope:** commits `134cbcb..07f907f` (jsonl_io malformed-skip + types-tier counter
+ panel-builder threading + CLI emission + 6 tests).
**Spec:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.4 §0.4 + §3.5.
**Verdict:** **APPROVE_WITH_NITS**.

---

## Findings

### BLOCK
None.

### NIT
- **NIT-1 (test_dev_ai_cost_v2_jsonl_io.py:649)** the Hypothesis conservation
  property sanitizes embedded newlines (`blob.replace(b"\n", b"")`) so the
  fixture line-count equals `len(line_blobs)`. This is **honest** (it is
  necessary for the line-count invariant to be meaningful) but the docstring
  could state that the strategy operates on lines-not-blobs more crisply. Not a
  test-honesty defect — the `st.binary` input is genuinely arbitrary within
  each line and exercises both `JSONDecodeError` and `non-assistant-dict`
  branches.
- **NIT-2 (test_dev_ai_cost_v2_jsonl_io.py:667)** the UTF-8 short-circuit
  (`return` from the test on `UnicodeDecodeError`) is *honest* — the reader's
  `open("r")` will itself raise `UnicodeDecodeError` and that error path is
  separately uncovered by any unit test. Consider a dedicated test asserting
  the reader's behaviour on non-UTF-8 bytes in a follow-up; not blocking.
- **NIT-3 (jsonl_io.py:284)** `jsonl_path.open("r")` uses the platform default
  encoding. v0.2.4 Y-7 explicitly handles JSON-decode partial-writes; pinning
  `encoding="utf-8"` (and possibly `errors="strict"`) would prevent the
  invisible locale-dependent UTF-8/CP1252 split that the conservation test
  short-circuits around. Pre-existing — out of scope for this commit pair but
  flagged as a pre-mortem item.
- **NIT-4 (test_dev_ai_cost_v2_jsonl_io.py:528-531)** runtime imports inside
  the `test_dropped_malformed_line_count_threaded_through_panel` body
  (`import polars as pl`, `from datetime import ...`). Stylistically prefer
  top-of-module imports; functionally harmless.

### PRAISE
- The exception narrowness is exemplary: `except json.JSONDecodeError` (not
  `except Exception`, not `except ValueError`). The narrow catch is explicitly
  asserted by `test_jsonlreader_valid_json_invalid_schema_still_raises`
  (line 589) — a Pydantic-schema-error on valid JSON still raises
  `JSONLSchemaError`. The non-over-correction commitment is enforced *by test*.
- The blank-line invariant is preserved: `test_jsonlreader_blank_lines_do_not_increment_malformed_counter`
  (line 562) pins the pre-existing `if not stripped: continue` guard order.
  This catches a regression where someone re-orders the strip check below the
  decode attempt and starts counting blanks as malformed.
- Counter-threading is explicit and 1:1: `JSONLReadResult.dropped_malformed_line_count`
  → `DailyNotionalPanel.dropped_malformed_line_count` with no rename or
  derivation. The contract is greppable.
- Spec-anchored docstrings on every new path (jsonl_io.py:21-26, types.py:211-216,
  panel_builder.py:101-104). The "Errors silenced" section in
  `JSONLReader.__call__` correctly enumerates Y-7 as a *silenced* error
  (jsonl_io.py:259-268).
- `__post_init__` non-negative validators on the new
  `dropped_malformed_line_count` field on **both** `JSONLReadResult` and
  `DailyNotionalPanel` (types.py:240, 339-340). Defense in depth.
- Hypothesis conservation property is the right invariant: total lines =
  records + non_assistant + malformed + blank. Catches future counter
  double-bumps or off-by-ones at scale (40 examples).

---

## Per-file walk-through

| File | Verdict | Notes |
|---|---|---|
| `simulations/dev_ai_cost_v2/types.py` | PASS | `JSONLReadResult` gains `dropped_malformed_line_count: int`; `DailyNotionalPanel` gains same field. Both `frozen=True, slots=True` preserved. `__post_init__` validates `>= 0` on both. No tier-import violations (stdlib + polars only). |
| `simulations/dev_ai_cost_v2/jsonl_io.py` | PASS | Narrow `except json.JSONDecodeError` at line 296, `continue`-with-counter pattern. Pydantic schema errors still raise `JSONLSchemaError` (line 308-313, unchanged). Counter wired into return at line 332-336. |
| `simulations/dev_ai_cost_v2/panel_builder.py` | PASS | Single line added at 219 to thread `read_result.dropped_malformed_line_count` → `DailyNotionalPanel.dropped_malformed_line_count`. Pure 1:1 forward. Tier-import rule preserved (types + sibling Callable only). |
| `scripts/build_notional_cost_panel.py` | PASS | Print line groups JSONLReader-sourced counters first (`dropped_non_assistant`, `dropped_malformed`), then PricingTable-sourced (`warn_missing_keys`, `dropped_unknown_model`, `substr_tiebreaker`), then π̂. 7 counters + π̂ = 8 fields, coherent ordering matches the docstring comment at lines 122-126. |
| `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` | PASS | 5 new tests (`_skips_trailing_null_bytes`, `_skips_truncated_json`, `_threaded_through_panel`, `_blank_lines_do_not_increment_malformed_counter`, `_valid_json_invalid_schema_still_raises`) + 1 Hypothesis property (`_line_conservation_property`). Each has a non-trivial assertion. The trailing-null-byte fixture (line 459) mirrors the production failure (`agent-af5e1160f7be358ba.jsonl:586`). |
| `simulations/tests/test_dev_ai_cost_v2_types.py` | PASS | New `test_jsonl_read_result_rejects_negative_malformed_count` + `test_daily_notional_panel_rejects_negative_malformed_line_count` + field-set updates. All existing call sites migrated. |
| `simulations/tests/test_dev_ai_cost_v2_panel_builder.py` | PASS | `_result(...)` fixture extended with `dropped_malformed: int = 0`; all `JSONLReadResult(...)` call sites pass `dropped_malformed_line_count=` explicitly (lines 299, 381). |
| `simulations/tests/test_dev_ai_cost_v2_migration.py` | PASS | Field-set test updated to include `dropped_malformed_line_count`; v0.2.4 reflected in docstring. |

---

## Call-site migration audit (CR-7-N3)

`grep -rn "JSONLReadResult(" simulations/ scripts/` yields **10 call sites**
(1 in jsonl_io.py production, 9 in tests). All 9 test call sites pass
`dropped_malformed_line_count=` explicitly as a keyword argument. The
production call site (jsonl_io.py:332) passes it as a keyword as well. No
missed positional invocations.

`grep -rn "DailyNotionalPanel(" simulations/ scripts/` yields **14 call sites**
(1 in panel_builder.py production, 13 in tests). All test sites use the
`_panel_kwargs(**overrides)` factory which defaults `dropped_malformed_line_count=0`.
The production site (panel_builder.py:214) sets it from `read_result.dropped_malformed_line_count`.
No missed call sites.

---

## Honnibal audit-pass coverage

| Pass | Status | Evidence |
|---|---|---|
| tighten-types | PASS | All new fields typed `int`/`float`; tuple-of-`MessageRecord` preserved on `JSONLReadResult.records`. No `Any`, no loose dicts. |
| contract-docstrings | PASS | Every new path documents input invariants, what it raises, and what it silences. The "Errors silenced" block in `JSONLReader.__call__` (line 259) correctly catalogs `JSONDecodeError`. |
| hypothesis-tests | PASS | `test_jsonlreader_line_conservation_property` is the right property (line accounting invariant under random binary input). 40 examples × ≤20 lines each. |
| try-except | PASS | `except json.JSONDecodeError` (narrow, exact); `except ValidationError` re-raised as `JSONLSchemaError`. No bare `except`, no `except Exception`. |
| pre-mortem | PASS-with-NIT | The migration anticipates trailing-null-bytes, truncated lines, and blank lines. One residual: non-UTF-8 bytes are not pinned by `encoding=` on the open call (NIT-3). |
| mutation-testing | N/A | Migration is small (single narrow try/except + 1 field on 2 dataclasses + 1 line in panel-builder). Mutation surface is too tight to be informative; the conservation property + the schema-error-still-raises test cover the obvious mutants (widen catch → conservation may still hold but schema-error test fails; remove counter bump → conservation fails). |

---

## Overall verdict

**APPROVE_WITH_NITS.**

The v0.2.4 Y-7 implementation is a textbook narrow-fix: a single exception type
caught at a single call site, with a dedicated counter that propagates through
exactly two type-tier containers and surfaces in the operator-visible CLI
print line. Tier discipline is preserved, exception scope is honest (the test
suite *enforces* non-over-correction by asserting that valid-JSON / invalid-schema
still raises), and the conservation Hypothesis property catches the class of
double-counting / line-loss bugs that this kind of accounting refactor most
often introduces. The nits are stylistic and out-of-scope for the Y-7 boundary.
