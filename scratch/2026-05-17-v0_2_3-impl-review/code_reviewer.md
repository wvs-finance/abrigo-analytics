# Code-Quality Review — Task 9.5 v0.2.3 Migration
Date: 2026-05-17
Reviewer: Code Reviewer (Wave 2 — code-quality channel)
Branch: iter/ai-cost-2026-05
Commits reviewed: 31a4d5d..d6da500 (6 commits)
LoC changed: +2001 / -579 across 13 files

## Executive summary

The v0.2.3 migration is well-engineered. Tier discipline, immutability,
frozen-dc + slots, contract-docstrings, typed error hierarchy, and counter
ownership are all clean. The `try/except` discipline is tight (each block
covers exactly one fallible op and raises a typed wrapping error). The
Hypothesis composite was updated for the float cost migration. The CR-Z-4
alphabetical-tiebreaker test correctly exercises determinism across two
opposite dict insertion orders.

The few issues found are NITs — no BLOCKers.

## Findings (ordered by severity)

### BLOCK
None.

### NIT (suggested, non-blocking)

1. **`Path("~/.claude/projects").expanduser()` as default-arg** —
   `simulations/dev_ai_cost_v2/jsonl_io.py:203` and
   `scripts/build_notional_cost_panel.py:64` both compute the expanded
   path **once at module-import time** via Python's default-argument
   evaluation. This is locked in for the lifetime of the process even
   if `HOME` changes (e.g., test sandboxing, CI matrix). Today it is
   harmless because every test passes `projects_root=tmp_path/...`
   explicitly, and the CLI re-parses at runtime — but the read-once
   semantic is surprising. Consider `projects_root: Path | None = None`
   and resolving inside the function body, or computing the default in
   `_parse_args` only.

2. **Private cross-module import in tests** — five test files import
   `_REQUIRED_KEYS` from `anthropic_pricing` and one imports `_synth_uuid`
   from `jsonl_io`. This is pragmatic (the constant is the canonical
   list, DRY), but it ties tests to an explicitly-private symbol. Either
   promote `REQUIRED_KEYS` (drop the underscore) or expose a `Helpers`
   surface for tests. As-is, a future rename silently breaks 5 tests.

3. **Unused `_typing` import** — `simulations/tests/test_dev_ai_cost_v2_migration.py:14`
   imports `typing as _typing` but never references it. Pure noise; remove.

4. **`_lookup_model_key` reverse-containment uses constant score** —
   `anthropic_pricing.py:237-238` scores all reverse-contained candidates
   as `len(model)`, so among multiple keys that reverse-contain the
   query, the score is identical and they all tie. This is currently
   resolved deterministically via the alphabetical tiebreaker (correct
   behavior per Y-5d), but is non-obvious. Adding one sentence in the
   docstring of `_lookup_model_key` clarifying "reverse-containment
   yields equal scores; rank-1 tiebreaker selects alphabetically" would
   prevent a future refactor from reasoning about it incorrectly.

5. **`_REQUIRED_KEYS` excludes `_INPUT_TIER_KEY`** — the load loop
   surfaces the 200k tier key as `None` if absent (no WARN, no counter
   bump), per the Y-2 fallback semantics. The class docstring at
   `anthropic_pricing.py:90-91` says: "Every key in
   `_REQUIRED_KEYS + (_INPUT_TIER_KEY,)` is present in each inner
   mapping; absent rates surface as `None`." That is *true* in practice
   but `_INPUT_TIER_KEY` is logically optional (tier rate) and the
   docstring conflates "always-present-as-key" with "may-be-None-valued"
   — slightly confusing.

6. **`object.__setattr__` on frozen dataclass** — `PricingTable` has
   three mutable counters that are bumped via `object.__setattr__` on a
   `frozen=True, slots=True` instance. This pattern is documented in the
   class docstring (lines 105-113) as the "documented exception for
   modules-tier-owned counters", but it does subtly weaken the
   "modules-tier dc is immutable" invariant. Given the v0.2.3 design
   pinning this on `PricingTable` (CR-Z-1), the pattern is acceptable,
   but it would be cleaner to expose counters via a tiny
   `IncrementOnly` Protocol-typed sidecar object (utils-tier-style),
   leaving `PricingTable` itself a pure frozen value. Treat as a
   future-refactor note; not a blocker for this migration.

7. **`PricingTable.from_litellm_sha` non-claude filter location** — the
   load loop checks `model.startswith("claude-")` BEFORE checking
   `isinstance(rates, dict)`. The test
   `test_pricing_table_skips_non_claude_models` proves this is
   intentional: the non-claude entry's incomplete schema does *not*
   trigger the WARN. Fine, but the test docstring at lines 234-235
   should explicitly call out the order (currently buried in a
   "NOTE:" comment) so a future contributor doesn't reorder the checks.

8. **`del ts` sentinel** — `anthropic_pricing.py:311` uses `del ts` to
   suppress the unused-argument warning for the multi-step-dispatch
   sentinel. This is correct, but a `# noqa: ARG002` plus a one-line
   comment is more discoverable than `del`. Minor style.

9. **`shutil.copy` in integration test** — `test_real_jsonl_integration.py`
   uses `shutil.copy` (not `copy2`); attribute metadata is dropped.
   Doesn't matter here, but use `copy2` if the fixture ever gains
   timestamp-bound semantics.

### PRAISE

1. **CR-Z-4 alphabetical-tiebreaker test is non-trivial** — the
   `test_cr_z_4_alphabetical_tiebreaker` test (lines 307-393 of
   `test_dev_ai_cost_v2_pricing.py`) does NOT just call once. It
   constructs four fixtures with deliberately *different* dict insertion
   orders (`table_a` / `table_b`, then `table_c` / `table_d`) and pins
   that BOTH return identical results AND that the counter was
   incremented on both. The earlier substring-match block (`table_a` /
   `table_b`) is even self-correcting: the implementer recognized that
   forward-substring on a unique-length query does not trigger a tie,
   then refactored to use reverse-containment (`fooX`) where all three
   keys legitimately tie by length. This is exactly the kind of test
   that catches dict-iteration regressions on Python upgrades. Honest,
   defensive testing.

2. **Tier-tier import discipline is clean and proven by direct grep**
   — `types.py` imports only `math`, `dataclasses`, `datetime`, and
   `polars` (no `modules/`, no `utils/`, no `_errors`). `anthropic_pricing.py`
   (modules tier) imports `simulations.dev_ai_cost_v2.types` and no
   `utils/`. `panel_builder.py` (modules tier) imports types + the
   sibling pure-callable `anthropic_pricing` and no `utils/`. `jsonl_io.py`
   (utils tier) imports types + modules. Acyclic and topology-correct.

3. **`__post_init__` invariants are exhaustive** — `MessageRecord`
   validates: tz-naive rejection (line 114), tz-not-UTC rejection (same
   check via `utcoffset` equality), per-field negativity (118-127),
   `cost_usd_notional` finiteness AND non-negativity AS SEPARATE checks
   (128-136 — better error messages than a combined predicate), and
   non-empty uuid (137-140). The NaN check uses `math.isfinite` rather
   than `!= self` (correct).

4. **Schema-pin via Float64 dtype is exact** — `EXPECTED_PANEL_SCHEMA`
   uses the polars dtype singletons directly (`pl.Float64`, `pl.Int64`,
   `pl.Date`). The post-init check compares with `!=`, which is the
   correct equality semantic for `pl.DataType` instances. The empty-DF
   path (line 157 of `panel_builder.py`) constructs the per-message
   frame with the schema explicitly so downstream `group_by` / `join`
   / `with_columns` are dtype-stable on 0-row input. The TRM-side
   `cast(Float64)` defensive coerce (lines 182-185) handles upstream
   Decimal-typed TRM panels cleanly.

5. **Immutability via `MappingProxyType` at both levels** — the
   `rates` field uses `MappingProxyType` wrapping a `dict[str,
   MappingProxyType[str, float | None]]`. Both levels are read-only;
   `rates["claude-x"]["foo"] = ...` would raise `TypeError`.

6. **The synthetic-fixture SKIP guard is the right call** — the
   `_is_synthetic` predicate inspects the `_comment` field on line 1
   and short-circuits `pytest.skip` *before* running the ccusage CLI.
   This prevents false-positive ccusage parity claims on synthetic
   data. The xfail-vs-skip distinction is correctly applied: missing
   ccusage = xfail (environmental); synthetic fixture = skip
   (logically inappropriate); fixture missing = skip (cannot run).

7. **CLI counter emission is operator-friendly** — the print line in
   `scripts/build_notional_cost_panel.py:124-133` surfaces all 7
   audit fields (2 pre-existing + 4 v0.2.3 counters + Y-6 π̂) in a
   single readable string with `%.6f` precision on the share. Trivial
   to parse for an alerting hook.

8. **`_errors.py` MRO** — `JSONLSchemaError(DevAICostError,
   SchemaMismatchError)` keeps three legacy catch patterns
   (`DevAICostError`, `SchemaMismatchError`, `ValueError`) all alive
   simultaneously. Backwards-compatible AND forward-extensible.

9. **`AwareDatetime` regression-guard test is intact** —
   `test_jsonlreader_raises_on_naive_timestamp` (lines 350-363 of
   `test_dev_ai_cost_v2_jsonl_io.py`) pins the v0.2.1 fix 283673d.
   Same with the polars vs python weekday convention pin (lines
   201-212 of `test_dev_ai_cost_v2_panel_builder.py`).

10. **No `_content_digest_unused` orphan** — grepped for
    `_content_digest_unused`, `_legacy_`, `__deprecated_` across all
    13 changed files. Zero hits. Task 6 I-1 dead-code removal is
    confirmed.

## Per-file walk-through

### `simulations/dev_ai_cost_v2/types.py` (+166 lines)
Adds `EXPECTED_PANEL_SCHEMA` (now 11 cols with `ephemeral_pi_share`),
`JSONLReadResult` (Y-5b, types-tier placement), `MessageRecord.uuid`
field, `cost_usd_notional: float` (Y-2), and the 4 new counter fields
plus `ephemeral_pi_share` on `DailyNotionalPanel`. `__post_init__` on
all four dcs is rigorous. Float-bounds check (`isfinite` + non-negative)
correctly handles `±inf` and `nan` separately from the magnitude check.
The `[0, 1]` bounds on `ephemeral_pi_share` are inclusive on both ends
(correct for a share that can saturate). No issues.

### `simulations/dev_ai_cost_v2/anthropic_pricing.py` (+321 / -... lines)
ccusage-parity float arithmetic, Y-3 permissive load, Y-5d ladder. The
two helper statics `_tiered` and `_flat` are clean (per-category gates
on `None` rates). `_lookup_model_key` is correct but worth the NIT-4
docstring upgrade. `LITELLM_SHA_PINNED` retained — v0.2.1 invariant
intact. `from_litellm_sha` raises `ValueError` (correct broad type) and
documents `FileNotFoundError` / `JSONDecodeError` from external state
in the docstring (Honnibal contract-docstrings: pass).

### `simulations/dev_ai_cost_v2/jsonl_io.py` (+277 lines)
The `_Row` Pydantic model is correctly private (`_` prefix) and is the
admitted private-BaseModel exception per CLAUDE.md. `extra="allow"` on
every nested model (Y-5f permissive) is consistent. `_synth_uuid` is
basename-bound + line-bound + truncated-sha256 (16 hex chars =
64 bits — adequate for a per-line dedupe key within a session).
`_construct_message_record` is a small pure helper (correct factoring
to keep the call-site readable). The two `try/except` blocks (lines
278-283 and 293-298) are *narrowly scoped* — each wraps only the one
fallible operation and raises a wrapping typed error with `from e`.
Excellent try/except discipline.

One subtle observation: line 289 short-circuits non-assistant rows via
`not isinstance(raw, dict) or raw.get("type") != "assistant"`. If a
JSONL line decodes to a `list` or scalar (unusual but possible), it
counts as `dropped_non_assistant_count`. That's the right behavior —
malformed-but-valid-JSON is structurally a non-assistant row.

### `simulations/dev_ai_cost_v2/panel_builder.py` (+153 lines)
Pure function — no IO, no module-level state, deterministic. The
weekday-convention dual constants (Python `< 5`, polars `<= 5`) are
the right answer and the docstring (lines 13-23) explains the why
clearly. The TRM-side defensive Float64 cast (lines 182-185) is a
guard against the legacy Decimal TRM panel. The Y-6 π̂ is a single
scalar broadcast as a constant column — sensible. The empty-records
branch (line 157) is dtype-stable. The `pre_join_daily_height -
joined.height` accounting for inner-join loss is correct: it counts
weekday-records-side dates that have no matching TRM row. No issues.

### `scripts/build_notional_cost_panel.py` (+51 / -... lines)
Argparse contract is correct; required `--since`/`--until` with
`date.fromisoformat` type converter (argparse auto-exits 2 on
malformed). `args.out.parent.mkdir(parents=True, exist_ok=True)` is
the right CORRECTIONS-W fix. Counter-print line emits all 7 audit
fields in one line. The `raise SystemExit(main())` idiom propagates
the exit code cleanly. No issues.

### `simulations/tests/strategies.py` (+19 lines)
Hypothesis composite `message_records` updated to draw
`cost_usd_notional` as `float` in `[0, 1000]` with `allow_nan=False,
allow_infinity=False` — correctly aligned with the Y-2 migration.
`uuid` drawn with `min_size=1` — correctly aligned with the R6 v0.1.3
non-empty requirement. No issues.

### `simulations/tests/test_dev_ai_cost_v2_types.py` (+218 lines)
Comprehensive: 12+ MessageRecord rejections, 4 TokensByCategory tests,
schema-drift / wrong-dtype panel tests, 6 negative-counter rejections,
π̂-bounds tests, JSONLReadResult tier-placement assertions, CR-Z-1
counter-ownership pins. Hypothesis property test
`test_message_record_post_init_invariants` reduces back to the public
invariants. No `assert True`. No `pytest.skip` placeholders. Clean.

### `simulations/tests/test_dev_ai_cost_v2_pricing.py` (+329 lines)
12 tests covering Y-3 load-warn, Y-5c aggregation locus, Y-5d
alphabetical tiebreaker (with explicit dict-order shuffling), Y-2
200k tier, fallback, None-rate gate, SHA mismatch guard, unknown-model
counting, non-claude filter. The CR-Z-4 test is especially good (see
PRAISE-1). One Hypothesis property
(`test_pricing_monotone_in_input_tokens`) — appropriate scope for a
modules-tier pure callable.

### `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` (+331 lines)
Covers Y-1 type-discriminator, Y-5b return-type, Y-5e uuid synthesis
(with CR-Z-5 rename-stability), Y-5f permissive `extra=allow`, all
required-field rejections, tz-naive rejection (regression guard for
283673d), blank-line skipping, subproject recursion, half-open UTC
window, and a Hypothesis property for double-iteration equivalence.
The cost-via-injected-PricingTable test
(`test_jsonlreader_costUSD_field_removed`) is a nice pin: it asserts
the *legacy* wire `costUSD=0.99` is ignored AND the computed-from-rates
value `1.5e-4` is used instead. Strong regression guard.

### `simulations/tests/test_dev_ai_cost_v2_panel_builder.py` (+320 lines)
Float reconciliation, is_error counting, forward-fill ban, weekend
double-drop, empty-records edge, TRM-only days excluded, Y-5a counter
threading (both JSONLReader-side AND PricingTable-side, separately),
Y-6 π̂ computed + broadcast, zero-denom π̂, input-type contract pin.
The polars-vs-python weekday calendar pin (lines 201-212) is the
exact regression guard demanded by commit 3d2d62d. Comprehensive.

### `simulations/tests/test_dev_ai_cost_v2_migration.py` (+171 lines NEW)
The CR-Z-6 migration smoke test. 12 tests pinning the v0.2.3 contracts
table signatures via `inspect.signature`. Catches arity or return-type
drift at import time. The unused `_typing` import (NIT-3) is the only
nit. Otherwise excellent: it pins
- `JSONLReader.__init__` accepts `pricing`,
- `JSONLReader.__call__` returns `JSONLReadResult`,
- `JSONLReadResult.__module__ == "...types"` (CR-Z-2 enforces tier),
- `MessageRecord.cost_usd_notional` annotation contains `"float"`,
- `PricingTable` owns 3 counters,
- `from_litellm_sha` keyword-only `skip_sha_check`,
- `build_daily_panel` first arg is `read_result: JSONLReadResult`,
- panel schema has 11 columns and monetary cols are Float64,
- `LITELLM_SHA_PINNED` retained.

### `simulations/tests/test_real_jsonl_integration.py` (+215 lines NEW)
Two tests: the parse-smoke (always runs if fixture present) and the
ccusage-parity oracle (3-level skip/xfail logic). The
`_is_synthetic` predicate prevents a false-positive parity assert on
the placeholder fixture. The xfail cascade is sound:
- `FileNotFoundError` on `npx` → xfail (env);
- `ccusage` returncode != 0 → xfail (env);
- `JSONDecodeError` on ccusage stdout → xfail (schema-drift);
- `(TypeError, KeyError, AttributeError)` on schema parse → xfail
  (ccusage version drift);
- `ccusage_total <= 0` → xfail (no data);
- production litellm cache absent → xfail (env).

The only hard assertion is the `rel_err < 1e-3` ccusage-parity
threshold — exactly the spec §3.5 Y-2 contract. The
`(TypeError, KeyError, AttributeError)` catch is *broad* but each is
genuinely a ccusage-version-drift signal, not a bug-hider — it lands
in xfail, not silent pass.

### `simulations/tests/fixtures/real_claude_jsonl/synthetic_sample.jsonl` (+9 lines)
9 lines: 1 `_comment` (no type field → counted non-assistant) + 5
assistant rows (1 is_error=true) + 1 user + 1 summary + 1 system.
Matches the smoke-test arithmetic. The `<REDACTED>` placeholders +
`SYNTHETIC` marker are appropriate.

## Honnibal audit-pass coverage
- **tighten-types**: PASS. Zero `Any`, zero loose `dict`/`list`, no
  `typing.Optional` (uses `X | None`), `Mapping`/`tuple[T, ...]` used
  where appropriate. Single `_typing` unused import in migration test
  (NIT-3).
- **contract-docstrings**: PASS. Every public `__call__`, classmethod,
  and free function has a docstring with Args/Returns/Raises (and
  "Errors from external state" / "Errors silenced" subsections where
  relevant — exemplary for the IO-boundary `JSONLReader.__call__`).
- **hypothesis-tests**: PASS. `strategies.py:message_records` updated
  for float-cost migration; three test files use `@given` for
  property-based coverage (monotone-in-input-tokens, tuple-records
  re-iteration, post-init-invariants). Bounded `max_examples` /
  `deadline=None` is sane for the slow-path tests.
- **try-except**: PASS. Two narrow blocks in `jsonl_io.py`, each
  wrapping exactly one fallible call (`json.loads`,
  `_Row.model_validate`) and re-raising a typed `JSONLSchemaError`
  with `from e`. No broad `except Exception`. No silent swallowing.
  The xfail integration test has a broad-tuple catch
  `(TypeError, KeyError, AttributeError)` — defensible, lands in
  xfail not pass.
- **pre-mortem**: PASS. Schema-drift on the polars side (`!=` dtype
  check, missing/extra column sets), tz-naive rejection (Pydantic
  `AwareDatetime` + dc `__post_init__`), NaN/inf rejection, empty-DF
  dtype stability, dict-iteration-order independence (CR-Z-4 test),
  rename-stability of synth uuid (CR-Z-5 test). Three layers of
  ladder fallback for unknown models. The `del ts` sentinel pins the
  future multi-step-dispatch contract.
- **mutation-testing**: N/A — not required for migration patch. The
  migration test suite (`test_dev_ai_cost_v2_migration.py`) is itself
  the contract-stability oracle.

## Overall verdict

**APPROVE_WITH_NITS**

The migration is clean, well-tested, and tier-disciplined. None of the
nine NITs blocks merge or v0.2.3 closure. Recommend filing NIT-1 (default
`expanduser()`) and NIT-3 (unused `_typing` import) as immediate
one-line fixes; the rest can land in a follow-up polish PR or be
deferred to the next iteration.
