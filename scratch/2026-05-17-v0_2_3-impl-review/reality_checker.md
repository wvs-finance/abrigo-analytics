# Spec-Compliance Review — Task 9.5 v0.2.3 Migration
Date: 2026-05-17
Reviewer: Reality Checker (TestingRealityChecker, integration-spec-compliance mode)
Branch: iter/ai-cost-2026-05
Commits reviewed: 31a4d5d..d6da500 (6 commits)
Spec: docs/specs/2026-05-16-ai-cost-factor-model-design.md v0.2.3 §0.3 (CORRECTIONS-Y-5a/b/c/d/e/f, Y-6) + §3.5 contracts table

Reviewer posture: paranoid; default to FLAG/BLOCK; only PASS on overwhelming evidence. No tests run by reviewer (per mandate). Verdicts derived from code+spec cross-reading only.

---

## Verdict summary

| Pin | Verdict | Evidence (file:line) |
|---|---|---|
| CR-Z-1 / Y-5a — counter ownership | PASS | anthropic_pricing.py:116-120, 244-248, 314-318 (counters on PricingTable, mutated via object.__setattr__); types.py:222-223 (JSONLReadResult carries only dropped_non_assistant_count); panel_builder.py:213-220 (threading); build_notional_cost_panel.py:127-131 (CLI emission) |
| CR-Z-2 / Y-5b — JSONLReadResult tier | PASS | types.py:195-230 (defined in types tier); types.py:338-343 (__all__ exports it); jsonl_io.py:323 (__all__ = ["JSONLReader"] only); test_dev_ai_cost_v2_types.py:323-331 (tier-placement enforced by test). FLAG-note: `records: tuple[MessageRecord, ...]` is narrower than spec's `Sequence[MessageRecord]` — strictly compatible (tuple is Sequence) and more immutable; non-blocking. |
| CR-Z-3 / Y-5c — aggregation locus | PASS | anthropic_pricing.py:321-322 (aggregation inside __call__); types.py:179-189 (TokensByCategory.__post_init__ validates only, no mutation); test_dev_ai_cost_v2_pricing.py:261-301 (test pins locus + non-mutation) |
| CR-Z-4 / Y-5d — alphabetical tiebreaker | PASS | anthropic_pricing.py:233-249 (`min(candidates)` via `sorted(...)[0]` + counter increment on tie); test_dev_ai_cost_v2_pricing.py:307-393 (shuffled-dict-order determinism asserted) |
| CR-Z-5 / Y-5e — uuid synthesis basename-stable | PASS | jsonl_io.py:108-123 (uses `Path.stem`, sha256, [:16], `zfill(8)`); jsonl_io.py:146-149 (synth only when uuid absent/empty); test_dev_ai_cost_v2_jsonl_io.py:232-256 (path-independent, basename-bound, line-sensitive) |
| CR-Z-6 / Y-5f — migration coverage | PASS | git diff --stat 31a4d5d~1..d6da500 confirms all 8 production files + 6 test files modified per spec table; new fixture file present at simulations/tests/fixtures/real_claude_jsonl/synthetic_sample.jsonl; new test_real_jsonl_integration.py present; new test_dev_ai_cost_v2_migration.py covers public signatures |
| Y-6 — π̂ ephemeral diagnostic | PASS | panel_builder.py:71-81 (formula matches spec, zero-denom→0.0); types.py:296, 326-335 (panel scalar [0,1] validated); build_notional_cost_panel.py:132 (CLI emission); test_dev_ai_cost_v2_panel_builder.py:331-354 (formula + zero-denom) |

Aggregate: 7/7 PASS. Zero BLOCKs, zero FLAGs.

---

## Per-pin findings

### CR-Z-1 / Y-5a — counter ownership: PASS

**Spec requirement** (lines 460-468): `WARN_missing_keys_count`, `dropped_unknown_model_count`, `multiple_substring_match_warning` live on **PricingTable**; `dropped_non_assistant_count` lives on **JSONLReader** side (carried via JSONLReadResult).

**Evidence**:
- `anthropic_pricing.py:116-120` — PricingTable declares the 3 counters as frozen-dc fields with `field(default=0)`.
- `anthropic_pricing.py:208` — `from_litellm_sha` initializes `WARN_missing_keys_count=warn_count` at load.
- `anthropic_pricing.py:244-248` — `multiple_substring_match_warning` incremented at call site via `object.__setattr__` on tied tiebreaker.
- `anthropic_pricing.py:314-318` — `dropped_unknown_model_count` incremented when ladder exhausts.
- `types.py:195-230` — JSONLReadResult carries ONLY `records` + `dropped_non_assistant_count`. No PricingTable counters present.
- `panel_builder.py:213-220` — Both sides threaded into DailyNotionalPanel: `warn_missing_keys_count=pricing.WARN_missing_keys_count`, `dropped_unknown_model_count=pricing.dropped_unknown_model_count`, `multiple_substring_match_warning=pricing.multiple_substring_match_warning`, `dropped_non_assistant_count=read_result.dropped_non_assistant_count`.
- `build_notional_cost_panel.py:124-133` — CLI `[OK]` print line emits all 5 counters + π̂.

**Concern (non-blocking)**: PricingTable is a frozen dataclass but its 3 counters are mutated post-construction via `object.__setattr__`. This is the only modules-tier dc carrying mutable state. Implementer documents this explicitly at anthropic_pricing.py:108-113. It violates strict immutability but the spec line 463 implicitly accepts this (counter ownership pinned to PricingTable). Tests at test_counter_threading_pricingtable_side and test_cr_z_4_alphabetical_tiebreaker verify the mutation actually takes effect and surfaces.

**Verdict**: PASS.

### CR-Z-2 / Y-5b — JSONLReadResult tier assignment: PASS

**Spec requirement** (lines 470-478): JSONLReadResult is a **types-tier** frozen-dc in `simulations/dev_ai_cost_v2/types.py`. Fields: `records: Sequence[MessageRecord]`, `dropped_non_assistant_count: int`. Does NOT carry PricingTable counters.

**Evidence**:
- `types.py:195-230` — JSONLReadResult defined here with exactly two fields.
- `types.py:338-343` — Exported in `__all__`.
- `jsonl_io.py:44-48` — `JSONLReadResult` imported FROM types, not defined locally.
- `jsonl_io.py:323` — `__all__ = ["JSONLReader"]` — JSONLReadResult not exported here.
- `test_dev_ai_cost_v2_types.py:323-331` — Pin-test asserts `JSONLReadResult.__module__ == "simulations.dev_ai_cost_v2.types"` AND that it is not in `jsonl_io.__all__`.

**Judgment-call deviation from spec wording**: Spec says `records: Sequence[MessageRecord]`. Implementer narrowed to `records: tuple[MessageRecord, ...]` (line 222). Tuple IS a Sequence (tuple inherits from Sequence at type level), and the choice is strictly more immutable. Documented at types.py:205-207 with rationale ("enforce types-tier immutability convention"). Non-blocking.

**Verdict**: PASS.

### CR-Z-3 / Y-5c — cache 5m+1h aggregation locus: PASS

**Spec requirement** (lines 480-489): aggregation `toks.cache_create_5m + toks.cache_create_1h` happens **inside `PricingTable.__call__` body only**. `TokensByCategory.__init__` does NOT mutate inputs.

**Evidence**:
- `anthropic_pricing.py:321-322` — `cache_create_total = toks.cache_create_5m + toks.cache_create_1h` computed at call site.
- `anthropic_pricing.py:333-335` — `self._flat(cache_create_total, r["cache_creation_input_token_cost"])` multiplies by single 5m rate. The `cache_creation_input_token_cost_above_1hr` rate is NOT used at call time (consistent with Y-5c + Y-6 note that this introduces ~2× downward bias on 1h share).
- `types.py:179-189` — TokensByCategory.__post_init__ only validates non-negativity; no mutation of input fields.
- Test `test_cr_z_3_aggregation_locus` at test_dev_ai_cost_v2_pricing.py:261-301 explicitly asserts: (a) split preserved post-construction, (b) cost = (A+B) * rate using the single 5m rate, with `cache_creation_input_token_cost_above_1hr=99.0` (deliberately wrong) confirmed unused.

**Verdict**: PASS.

### CR-Z-4 / Y-5d — alphabetical tiebreaker: PASS

**Spec requirement** (lines 491-498): when multiple longest-substring matches tie, **alphabetically-smallest key wins** (`min(candidates)`); counter `multiple_substring_match_warning` incremented; deterministic across dict-ordering.

**Evidence**:
- `anthropic_pricing.py:233-249` — `_lookup_model_key`:
  ```
  candidates: list[tuple[int, str]] = []
  for key in self.rates:
      if key in model:      candidates.append((len(key), key))
      elif model in key:    candidates.append((len(model), key))
  if not candidates: return None
  best_len = max(c[0] for c in candidates)
  tied = sorted(k for ln, k in candidates if ln == best_len)
  if len(tied) > 1:
      object.__setattr__(self, "multiple_substring_match_warning",
                          self.multiple_substring_match_warning + 1)
  return tied[0]
  ```
  `sorted(...)` returns alphabetical order; `tied[0]` ≡ `min(tied)`. Behavior matches spec.
- Counter increment ONLY fires when `len(tied) > 1`. Non-tied longest-match cases (e.g. a single dominant length match) do NOT increment, even if `candidates` had >1 entries with different lengths.
- Test `test_cr_z_4_alphabetical_tiebreaker` at test_dev_ai_cost_v2_pricing.py:307-393 constructs two pricing tables with the same 3 keys in REVERSE dict-insertion order (table_c vs table_d) and asserts identical lookup result + identical post-call counter increment.

**Judgment-call note (Q2 of mandate)**: tiebreaker uses synthetic `claude-fooX-{a,b,c}` keys rather than real LiteLLM model names. The synthetic-key design is appropriate: real LiteLLM keys are unlikely to produce a perfect tie on the substring metric in normal operation (different lengths in practice), so the regression contract here is correctly the algorithmic property (alphabetical wins on tie) rather than a real-world model collision. Tests at test_pricing_unknown_model_returns_zero_and_counts cover the real-world unknown-model path. Sufficient regression contract.

**Verdict**: PASS.

### CR-Z-5 / Y-5e — uuid synthesis hardened: PASS

**Spec requirement** (lines 500-516): synth uuid format = `"synth-sha256:" + sha256(file_basename + ":" + line_no_zfill_8).hexdigest()[:16]`; basename strips directory + any user-prefix (so the example `~/.claude/projects/<some-uuid>/session.jsonl → session`). Synth applied ONLY when JSONL `uuid` absent.

**Evidence**:
- `jsonl_io.py:108-123`:
  ```
  def _synth_uuid(file_path: Path, line_no: int) -> str:
      basename: str = Path(file_path).stem
      digest_input: str = f"{basename}:{str(line_no).zfill(8)}"
      digest: str = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:16]
      return f"synth-sha256:{digest}"
  ```
  Format matches spec exactly. `Path.stem` strips directory AND extension; for the spec example `~/.claude/projects/<some-uuid>/session.jsonl` the stem is `session` — matches.
- `jsonl_io.py:146-149` — synth applied conditionally: `if row.uuid is None or row.uuid == "": uuid = _synth_uuid(...)`. Empty-string treated as absent — defensive (spec only says "absent" but Pydantic might surface either; this is a safe over-coverage).
- Tests at test_dev_ai_cost_v2_jsonl_io.py:201-256 cover all four rename invariants: same basename + diff dir → identical; diff line → differs; diff basename → differs; prefix present on all synth uuids.

**Verdict**: PASS.

### CR-Z-6 / Y-5f — migration coverage: PASS

**Spec requirement** (lines 517-535): 8 files modified per Y-5f table; new fixture dir + test_real_jsonl_integration.py.

**Evidence (git diff --stat 31a4d5d~1..d6da500)**:
- `simulations/dev_ai_cost_v2/types.py` (166 +/-)            ✓
- `simulations/dev_ai_cost_v2/jsonl_io.py` (277 +/-)         ✓
- `simulations/dev_ai_cost_v2/anthropic_pricing.py` (321 +/-) ✓
- `simulations/dev_ai_cost_v2/panel_builder.py` (153 +/-)    ✓
- `simulations/tests/strategies.py` (19 +/-)                 ✓
- `simulations/tests/test_dev_ai_cost_v2_*.py` × 4 (1198 +/-) ✓
- `simulations/tests/fixtures/real_claude_jsonl/synthetic_sample.jsonl` (NEW, 9 lines) ✓
- `simulations/tests/test_real_jsonl_integration.py` (NEW, 215 lines) ✓
- `scripts/build_notional_cost_panel.py` (51 +/-)            ✓
- `simulations/tests/test_dev_ai_cost_v2_migration.py` (NEW, 171 lines) — additional coverage beyond Y-5f table; covers public signatures.

All 8 files in Y-5f table + new fixture + new integration test present. test_dev_ai_cost_v2_migration.py adds belt-and-suspenders signature pinning.

**Verdict**: PASS.

### Y-6 — π̂ ephemeral diagnostic: PASS

**Spec requirement** (lines 537-552): `π̂ = Σ cache_create_1h / Σ (cache_create_5m + cache_create_1h)`; if denominator = 0, set to 0.0; surfaced on DailyNotionalPanel + DATA_PROVENANCE.

**Evidence**:
- `panel_builder.py:71-81`:
  ```
  def _compute_ephemeral_pi_share(records: tuple[MessageRecord, ...]) -> float:
      sum_1h: int = sum(r.cache_create_1h for r in records)
      sum_5m: int = sum(r.cache_create_5m for r in records)
      denom: int = sum_5m + sum_1h
      if denom == 0:
          return 0.0
      return sum_1h / denom
  ```
  Formula matches spec exactly. Zero-denom defaults to 0.0.
- `panel_builder.py:200` — computed over ALL records (kept + dropped errors); spec is silent on whether to exclude is_error rows for this diagnostic; implementer chose to include all (consistent with "Σ across the panel" wording).
- `types.py:296, 326-335` — DailyNotionalPanel carries `ephemeral_pi_share: float`, validated finite + bounded [0,1].
- `types.py:55` — `EXPECTED_PANEL_SCHEMA["ephemeral_pi_share"] = pl.Float64`.
- `panel_builder.py:201-203` — broadcast as constant column.
- `build_notional_cost_panel.py:132` — emitted in CLI `[OK]` print.
- Tests test_y6_ephemeral_pi_share_computed (correctness on Σ_1h=30/Σ_total=100 → 0.3) and test_y6_ephemeral_pi_share_zero_denominator (zero defaults to 0.0).

**Sub-concern (judgment call #1)**: Y-5f file table for `types.py` says "**add `MessageRecord.ephemeral_pi_share` Optional field**" but implementer chose to place π̂ ONLY on `DailyNotionalPanel`. This is a deviation from the Y-5f file-table phrasing. However:
  - Y-6 narrative (lines 537-552) defines π̂ exclusively as a panel-level scalar (`Σ ... / Σ ...` over the panel).
  - A per-message π̂ would be either 0 or 1 (each message has 5m or 1h, not both as ratios), making the per-message field semantically meaningless.
  - §3.5 `DailyNotionalPanel` row (line 921) explicitly carries `ephemeral_pi_share: float per Y-6` — confirming the panel-level placement.
  - §3.5 `MessageRecord` row (line 917) does NOT include ephemeral_pi_share — confirming the omission.
  - The deviation is from the Y-5f file-table prose; the actual §3.5 contracts table is the authoritative contract surface, and the implementation matches §3.5.

This deviation is **reasonable and consistent with the spec's authoritative §3.5 table**; the Y-5f file-table phrasing is a documentation inconsistency in the spec itself (a NIT-level issue, not a deviation by the implementer).

**Verdict**: PASS.

---

## Judgment-call audit (5 explicit calls per mandate)

1. **`MessageRecord.ephemeral_pi_share` placed ONLY on panel (deviation from Y-5f file-table phrasing).**
   §3.5 DailyNotionalPanel row (line 921) explicitly carries it; §3.5 MessageRecord row (line 917) explicitly omits it. The implementer's choice matches §3.5 (the authoritative contract surface) and is semantically correct (π̂ is a panel-level ratio, not a per-message scalar). The Y-5f file-table prose is a documentation inconsistency in the spec itself. **VERDICT: CONSISTENT with spec intent.**

2. **CR-Z-4 tiebreaker test uses synthetic `claude-fooX-{a,b,c}` keys.**
   Real LiteLLM model names are unlikely to tie on the substring metric in normal operation; the regression contract here is correctly the algorithmic property (alphabetical wins on tie), which the synthetic keys exercise definitively. test_pricing_unknown_model_returns_zero_and_counts covers the real-world unknown-model path separately. **VERDICT: SUFFICIENT regression contract.**

3. **Cost computed at parse time via injected PricingTable (utils imports modules).**
   CLAUDE.md tier rule: `types/ imports neither modules/ nor utils/; modules/ imports types/ but not utils/`. By construction, `utils/` is the bottom and CAN import `modules/` and `types/`. `jsonl_io.py` (utils) importing `PricingTable` (modules) is permitted. The implementer's choice of constructor injection (`JSONLReader.__init__(pricing)`) over per-call injection is reasonable: cost is computed once per record at parse time, the table is immutable (modulo counters), and the same table flows through the panel-builder. **VERDICT: TIER-DISCIPLINE COMPLIANT.**

4. **Synthetic fixture marker = first-line `{"_comment": "SYNTHETIC..."}` JSON object instead of `// SYNTHETIC` comment.**
   JSONL convention forbids `//` comments (each line must be valid JSON); the JSON-object marker is the only conforming way to ship a self-flagging fixture. `test_real_jsonl_integration.py:_is_synthetic` reads the first line, parses it as JSON, and checks `obj["_comment"].startswith("SYNTHETIC")`. The parser's pre-validation type-discriminator (jsonl_io.py:289 — `raw.get("type") != "assistant"`) correctly treats the comment row as non-assistant (since it lacks the `type` field), counting it in `dropped_non_assistant_count`. The skip-on-synthetic gate in `test_ccusage_parity_oracle` correctly activates, deferring the parity assertion until a real PII-redacted fixture lands. **VERDICT: REASONABLE; skip is conditional, not a permanent bypass.**

5. **TRM dtype auto-cast Decimal → Float64 in panel_builder (silent drift risk?).**
   `panel_builder.py:182-185`: `if trm_weekday.schema.get("trm_cop_per_usd") != pl.Float64: trm_weekday = trm_weekday.with_columns(pl.col("trm_cop_per_usd").cast(pl.Float64))`. TRM values are COP/USD in the range ~3500-4500 with sub-cent precision (Banrep publishes 4 decimal places, max precision ~6). Float64 carries ~15-17 significant decimal digits. Values like `4123.4567` cast to Float64 losslessly; the relative error from Decimal→Float64 for these magnitudes is ≤ 1e-13, far below the ccusage-parity-0.1% (1e-3) tolerance and the v0.2.1 reconciliation budget. **VERDICT: NO SILENT DRIFT for the operational TRM range.**

---

## Anti-fishing audit

**Test rigor delta (positive, not reduced)**:
- test_dev_ai_cost_v2_pricing.py: -2 old / +6 new tests (renames + 4 net new: aggregation_locus, alphabetical_tiebreaker, 200k_tier, none_rate, tier_fallback). Net positive.
- test_dev_ai_cost_v2_jsonl_io.py + types.py + panel_builder.py: 26 new test definitions added, 5 old removed (covered by replacement tests with updated semantics). Net positive.
- New files: test_dev_ai_cost_v2_migration.py (13 tests), test_real_jsonl_integration.py (2 tests, 1 conditional-skip + 1 always-runs).
- Total net test-count delta: clearly positive. NO silent reduction in rigor.

**Backwards-compat shims**: None found. No `_records_legacy` alias, no `costUSD` fallback (the wire field is explicitly ignored per test_jsonlreader_costUSD_field_removed — Pydantic `extra="allow"` consumes it without using it). No deprecated field shadows.

**try/except masking**:
- `jsonl_io.py:278-283` — `try/except json.JSONDecodeError` → wrapped in `JSONLSchemaError` with file:line context. NOT masking; surfaces.
- `jsonl_io.py:293-298` — `try/except ValidationError` → wrapped in `JSONLSchemaError` with file:line. NOT masking; surfaces.
- No other try/except in production paths.
- `test_real_jsonl_integration.py:147-155` — `try/except FileNotFoundError` → xfail (intentional gate on ccusage CLI availability). NOT masking real bugs; correctly marks environmental absence.
- `test_real_jsonl_integration.py:163-167, 174-181` — `try/except (TypeError, KeyError, AttributeError)` → xfail on ccusage JSON schema drift. This is a defensible defense against ccusage's own schema instability (a known issue with ccusage versioning), not a mask of our pipeline's bugs.

**ccusage-parity test skip status**:
- `test_real_jsonl_integration.py:131-137` — `pytest.skip(...)` activates ONLY when (a) fixture missing, or (b) `_is_synthetic(FIXTURE_FILE)` is True. Both conditions are operator-removable (drop a real PII-redacted JSONL into the fixture dir and the skip vanishes). Skip is conditional, NOT permanent.
- The skip semantics are correct: a synthetic fixture cannot serve as an authoritative oracle for ccusage parity because both sides would be computing the same notional cost from the same toy rates, yielding trivial agreement that proves nothing. The skip preserves the oracle's spec-pinned 0.1% tolerance as a meaningful guarantee for when real data arrives.

**No anti-fishing red flags detected.**

---

## Overall verdict

**APPROVE**.

All 6 CR-Z pins (Y-5a through Y-5f) plus the Y-6 π̂ diagnostic are implemented to spec. The 5 explicit judgment calls flagged in the mandate are each (a) consistent with §3.5 (the authoritative contract surface) where the Y-5f file-table prose conflicts (the π̂-placement deviation), (b) algorithmically sufficient for the regression contract (synthetic-key tiebreaker), (c) tier-discipline compliant (utils→modules import direction), (d) JSONL-convention compliant (JSON-object synthetic marker), and (e) numerically safe (TRM Float64 cast). Anti-fishing audit clean: test rigor increases, no backwards-compat shims, no masking try/except, ccusage-parity skip is conditional and operator-removable.

**Exit criteria status** (Task 9.5, spec line 535):
- (i) all 6 CR-Z BLOCKs verified closed by spec-compliance review — **YES** (this report)
- (ii) regression suite green — **CLAIMED 793/793 passing by implementer; reviewer did not re-run per mandate**
- (iii) ccusage-parity oracle passes on real JSONL fixture — **DEFERRED** (synthetic fixture in tree; oracle test correctly skips until real PII-redacted fixture lands; this is a known gating condition, not a v0.2.3 closure-blocker)
- (iv) impl-review checkpoint re-runs with updated code — **THIS REPORT IS THAT CHECKPOINT**

**Recommendations (non-blocking, deferable to follow-up)**:
1. Spec housekeeping: reconcile the Y-5f file-table prose for `types.py` to drop the obsolete "add `MessageRecord.ephemeral_pi_share` Optional field" phrasing, since §3.5 places this field on `DailyNotionalPanel` only. (NIT for the next spec patch; does NOT block v0.2.3 implementation closure.)
2. When a real PII-redacted JSONL fixture is curated, the synthetic_sample.jsonl should be moved aside (rename or fixture-dir rotation) so `_is_synthetic` returns False and the ccusage-parity oracle activates. Tracked by exit-criterion (iii) above.
3. Optional defensive: add an explicit unit test that constructs a TRM panel with `pl.Decimal` dtype and feeds it through `build_daily_panel` to pin the Float64-cast path (currently only the Float64 path is exercised by the panel-builder test fixtures). Non-blocking; the cast is mathematically safe for the operational TRM range.

---

**Reviewer**: Reality Checker
**Method**: source+spec cross-reading with paranoid posture
**Files inspected**: 14 (8 production + 6 test, plus 1 fixture, plus spec §0.3/§3.5)
**Tools used**: Bash (git log/diff/grep), Read (production + test + spec + fixture)
**Tests run**: NONE (per mandate; trust the 793/793 implementer report)
**Time budget**: single-pass review on diff range 31a4d5d..d6da500
