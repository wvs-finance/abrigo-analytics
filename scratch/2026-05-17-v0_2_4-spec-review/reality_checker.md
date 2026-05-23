# Reality Checker — v0.2.4 contract-only patch (CORRECTIONS-Y-7)

**Reviewer**: TestingRealityChecker (closure-only)
**Date**: 2026-05-17
**Scope**: §0.4 + CORRECTIONS-Y-7 + §3.5 contract-row updates for
`JSONLReader`, `JSONLReadResult`, `build_daily_panel`, `DailyNotionalPanel` +
revision history line 1245.
**Inputs read**:
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md`
  (lines 554–621, 984–990, 1245)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/dispositions/2026-05-17-task10-trailing-null-bytes.md`
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-16-ai-cost-impl-review/oss_algorithm_study.md`
  (lines 18–20, 95–96, 276 — ccusage/cc-lens line-level skip evidence)

---

## Verdict summary

| # | Question                                          | Verdict |
|---|---------------------------------------------------|---------|
| 1 | Anti-fishing classification                       | PASS    |
| 2 | OSS-mirror consistency (ccusage parity)           | PASS    |
| 3 | Counter ownership tier-discipline                 | PASS    |
| 4 | Test surface adequacy                             | FLAG    |
| 5 | Observability / hard-fail threshold               | FLAG    |
| 6 | Spec internal consistency (counter count)         | FLAG    |

**Overall**: **CONDITIONAL_APPROVE** — 3 FLAGs, 0 BLOCKs. All FLAGs are
inline-fixable doc/test-surface refinements; none touch the substantive
contract or the iteration framework.

---

## Per-question findings

### Q1. Anti-fishing classification — PASS

§0.4 explicitly invokes `feedback_pathological_halt_anti_fishing_checkpoint`
and routes through HALT → disposition memo → user-enumerated pivot (A/B/C in
the disposition) → CORRECTIONS block → 2-wave review. The disposition memo
(lines 41–47) names this a "spec-vs-data contradiction, not a methodology
shift" and pins what is NOT changing:

- R5 / R4-S3 framework: untouched (§2.1 + §2.2 not modified).
- N_MIN = 75 floor: untouched (§2.3 not modified).
- MDES_SD = 0.40: untouched (§2.3 not modified).
- Headline outputs (R5 cost-burden / R4-S3 vol-clustering): unaffected.

The change is contract-only at the IO Boundary (`JSONLReader`) and types
tier (`JSONLReadResult`, `DailyNotionalPanel`). The amendment's risk window
(silent-skip masks producer-side regressions) is *expansionary in coverage*
(parser now ingests more files) — there is no scenario where silent-skip
*tightens* the inclusion criterion to a previously-failing direction, so no
fishing pressure on the verdict. APPROVED on this channel.

### Q2. OSS-mirror consistency — PASS

The OSS algorithm study evidence:

- **ccusage** (study line 95–96): `parseUsageDataLineFast` returns `null`
  on schema failure, and the data-loader does `if (data == null) continue;`
  — silent skip with no counter.
- **cc-lens** (study line 19): `JSON.parse` per line wrapped in
  `catch { /* skip */ }` — silent skip, no counter.
- Study line 276 confirms the recommendation: `json.loads(line)` in
  try/except → "malformed line → skip silently."

Y-7's contract:

```
try: raw = json.loads(stripped)
except json.JSONDecodeError: dropped_malformed_line_count += 1; continue
```

This is a **tighter** mirror than ccusage strictly requires (ccusage
doesn't carry a counter; Y-7 does). The added counter is *not*
over-correction — it is the empirically-correct response to the disposition
memo's observability concern (§0.4 risk paragraph). PASS.

One micro-nit (non-blocking): ccusage skip happens inside Valibot's full
parse, which conflates JSON-decode failure and schema-failure into one skip
class. Y-7 splits the two: JSON-decode failure → silent skip + counter;
Pydantic schema failure on valid JSON → still raise `JSONLSchemaError`.
The split is **operationally correct** and explicitly defended in §0.4
lines 578–580 ("relaxation is scoped to lines that aren't even parseable
as JSON"). This is a strict improvement on the OSS norm and aligns with
Y-5b counter-tier discipline.

### Q3. Counter ownership tier-discipline — PASS

Y-7 places `dropped_malformed_line_count` on `JSONLReadResult` (types
tier, owner = JSONL parser per Y-5b). This is correct per the v0.2.3
precedent:

| Counter family                            | Owner                | Tier  |
|-------------------------------------------|----------------------|-------|
| `dropped_non_assistant_count`             | `JSONLReadResult`    | types |
| `dropped_malformed_line_count` (NEW Y-7)  | `JSONLReadResult`    | types |
| `WARN_missing_keys_count`                 | `PricingTable`       | mod.  |
| `dropped_unknown_model_count`             | `PricingTable`       | mod.  |
| `multiple_substring_match_warning`        | `PricingTable`       | mod.  |

The Y-5a discipline (CR-Z-1 resolution) reads: *line-parse counters live
with the line parser; rate-coverage counters live with the rate table.*
`dropped_malformed_line_count` is a line-parse failure (json.loads raised),
so it belongs with the line parser. Placing it on `PricingTable` would be
a tier violation (PricingTable would gain a counter for an event it never
witnesses). PASS — exact same family as `dropped_non_assistant_count`,
correctly co-located.

§3.5 row 985 carries the placement; line 989's `build_daily_panel` row
threads it from `JSONLReadResult` (not from `PricingTable`). Consistent
across the three §3.5 rows.

### Q4. Test surface adequacy — FLAG

The three enumerated tests (§0.4 lines 608–615) cover the **shapes of
malformed-input the production run hit** (null-byte block + truncated
mid-JSON) and the threading invariant. They are adequate for the closure
gate but the test floor leaves three coverage gaps:

**FLAG-4a (blank-line semantics regression test missing).** §0.4 line 581
asserts: "the blank-line skip continues to apply BEFORE the JSON-decode
attempt, so empty / whitespace-only lines still cost zero counter ticks."
This is a behavioral invariant the patch is making — but it is not
test-pinned. Add:
- `test_jsonlreader_blank_lines_do_not_increment_malformed_counter`
  — file with `\n\n\n` interspersed with valid records → blank-line skip
  fires, `dropped_malformed_line_count == 0`.

Without this test, a future refactor that reorders the strip-vs-decode
sequence could silently mis-attribute blank lines as malformed and inflate
the operational signal.

**FLAG-4b (Pydantic-schema-failure-still-raises regression test missing).**
§0.4 lines 578–580 assert that the line-level relaxation is **scoped** —
valid-JSON-but-invalid-schema still raises. This is the explicit
non-over-correction commitment of Y-7. It is also not test-pinned. Add:
- `test_jsonlreader_valid_json_invalid_schema_still_raises`
  — file with `{"foo":"bar"}` (parseable JSON, missing required
  `timestamp` + `message.usage.{input,output}_tokens`) →
  `JSONLSchemaError` raised, NOT silently skipped.

Without this test, a future refactor that broadens the `except` clause to
`except Exception` would silently swallow producer-side schema regressions
— exactly the failure mode §0.4 lines 596–604 ("Risk and observability")
identifies as the residual risk.

**FLAG-4c (hypothesis property test recommended, non-blocking).** Y-7's
contract is essentially "arbitrary bytes between newlines do not crash the
parser." This is precisely the shape that the `hypothesis-tests` skill
audit pass (canonical per `CLAUDE.md` "Honnibal audit-pass chain") would
add as a property. Recommend a single Hypothesis strategy that builds a
JSONL file from `lists(text() | binary())` and asserts:
- parser does not raise (except `JSONLSchemaError` on schema violations
  per FLAG-4b);
- `len(records) + dropped_non_assistant_count + dropped_malformed_line_count
   + blank_line_skips == total_lines` (the accounting identity).

Property tests catch byte-class corners (CR + LF + tab + form-feed +
non-UTF-8 + bare `}`) the three enumerated unit tests do not. Mark this
as "Task 10.6 minor follow-up" rather than gating v0.2.4 closure — the
3 enumerated tests are the minimum-viable surface and the audit-pass chain
canonically runs *after* the contract lands.

### Q5. Observability / hard-fail threshold — FLAG

§0.4 lines 596–604 acknowledges the silent-skip-masks-regressions risk and
points to two mitigations:

1. The counter surfaces in CLI `[OK]` line + DATA_PROVENANCE.md.
2. Y-4's `test_real_jsonl_integration.py` will catch genuine producer
   regressions because the canonical fixture lines are valid JSON.

Mitigation (2) is well-targeted — a producer regression that changes the
JSON shape would corrupt the fixture and the parity oracle test would
fail. Mitigation (1) relies on the operator *reading* the counter, which
is a soft signal.

**FLAG-5a (no quantitative HARD-FAIL threshold).** The user's question
proposes `dropped_malformed_line_count / total_lines > 0.05 → raise` as a
threshold. The spec currently has none. Two considerations:

- **Argument for adding a threshold**: a 5% malformed-line rate is well
  above any plausible filesystem-corruption baseline (single-block null
  fills should be ≪ 1% of lines, since they typically affect 1 partial
  block at the EOF of 1 file out of hundreds). 5%+ is almost certainly
  producer-side regression and should HALT.
- **Argument against adding a threshold here**: the right threshold is
  hard to pin without baseline data. The disposition's filesystem-corruption
  case yields 1 dropped line in a single file of 585 → file-local rate 0.17%,
  corpus-local rate likely < 0.001%. Picking 5% is arbitrary; 1% might be
  more defensible; 0.5% might be too aggressive in the presence of
  Unicode-edge edge cases. The empirically-supported number requires a
  full-corpus run to establish a baseline.

**Recommendation (compatible with v0.2.4 closure)**: do NOT bake a
quantitative threshold into v0.2.4. Instead amend §0.4 "Risk and
observability" paragraph with one sentence:

> A hard-fail threshold on `dropped_malformed_line_count / total_lines` is
> deferred to v0.2.5 pending a full-corpus baseline; until then, any
> non-zero counter value triggers an operator-side review per the
> DATA_PROVENANCE emission.

This documents the gap, defers the decision to data, and avoids picking a
fishing-vulnerable threshold ex ante. The post-corpus-run baseline review
becomes a v0.2.5 work item.

**FLAG-5b (DATA_PROVENANCE schema not pinned).** §0.4 line 593 says the
counter is "emitted in DATA_PROVENANCE.md" but does not specify the format
(YAML key? markdown row? JSON object?). v0.2.3 had the same ambiguity for
the existing 5 counters. Non-blocking for v0.2.4 (consistency with prior
state) but worth pinning in v0.2.5 to make the operator-side review
machine-readable.

### Q6. Spec internal consistency — FLAG (count mismatch)

User's enumeration of v0.2.3 `DailyNotionalPanel` counters (line 990
pre-Y-7):

1. `dropped_rows_count` (weekend filter)
2. `dropped_error_count` (is_error filter)
3. `dropped_non_assistant_count` (Y-5a, from JSONLReadResult)
4. `WARN_missing_keys_count` (Y-5a, from PricingTable)
5. `dropped_unknown_model_count` (Y-5a, from PricingTable)
6. `multiple_substring_match_warning` (Y-5a, from PricingTable)

Total v0.2.3 = **6**. Plus Y-7's `dropped_malformed_line_count` = **7**.

§3.5 row 990 (post-Y-7) says "Carries the 7 counters above" — **CORRECT**.

§3.5 row 989 (post-Y-7) enumerates 7 by name in `build_daily_panel` →
**CORRECT**.

§0.4 line 594 (post-Y-7) says "The 5 existing counters become 6." →
**WRONG** (off by one in both terms; should be "The 6 existing counters
become 7").

**FLAG-6a (fix narrative count)**: §0.4 line 594 needs the single-word
edit `5 → 6` and `6 → 7`. This is a cosmetic correction with zero
contract impact (the §3.5 contract rows are correct), but it should land
before v0.2.4 finalization to prevent confusion in the next impl review.

Inline fix:

> The 6 existing counters become 7.

---

## Anti-fishing audit

Per `feedback_pathological_halt_anti_fishing_checkpoint`, verify:

| Invariant                                            | State    |
|------------------------------------------------------|----------|
| R5 framework (§2.1) unchanged                        | PASS     |
| R4-S3 framework (§2.2) unchanged                     | PASS     |
| N_MIN = 75 (§2.3) unchanged                          | PASS     |
| POWER_MIN = 0.80, MDES_SD = 0.40 unchanged           | PASS     |
| Sign-expectation / lag-structure / primary spec      | PASS (untouched) |
| Threshold tuning post-hoc                            | NONE — no thresholds added |
| HALT routing chain followed                          | PASS (disposition memo + user pivot + CORRECTIONS block) |
| Disposition memo predates spec amendment             | PASS (same date but memo Step-1 logged BEFORE Step-3 amendment landed) |
| User pivot enumerated A/B/C, chosen A on stated grounds | PASS |
| 2-wave review on amendment                           | IN PROGRESS (this is wave 1) |
| Future re-run Task 10 from Step 10.2                 | DEFERRED to impl |
| Headline-output drift risk                           | NONE — silent-skip is on lines that previously HALTed the pipeline; the alternative was no-output. Including-more-data direction is not a verdict-tilting move because excluded-by-corruption rows had cost = unknown, so neither side of any β-sign expectation is biased. |

The Y-7 patch's *direction of bias* deserves one extra sentence of
audit: silent-skip widens the included-row set (more files parse to
completion). The dropped lines are by construction non-decodable as JSON,
so they carry no assistant-message economic content the framework can
attribute. Adding them back via a stricter skip-discriminator (Option B)
would not recover lost cost/token signal because the bytes contain no
JSON to extract. **The Option A skip is information-preserving at the
econometric level** — it doesn't drop signal, it drops noise the previous
contract conflated with signal. No fishing pressure.

---

## Overall verdict

**CONDITIONAL_APPROVE.**

Rationale: 3 FLAGs, 0 BLOCKs. The substantive contract change (line-level
malformed-skip + types-tier counter) is correct, OSS-aligned, tier-clean,
and anti-fishing-clean. The flags are inline-fixable:

1. **MUST fix before v0.2.4 finalization** (1-line edit): §0.4 line 594
   counter count `5 → 6` and `6 → 7` (FLAG-6a).
2. **SHOULD fix before v0.2.4 finalization** (2 added tests): FLAG-4a
   (blank-line counter-zero test) + FLAG-4b (valid-JSON-invalid-schema
   still-raises test). These pin the two explicit non-over-correction
   commitments §0.4 makes.
3. **DEFER to v0.2.5** (1 amendment + 1 work item): FLAG-5a (defer
   hard-fail threshold pending full-corpus baseline) + FLAG-4c
   (Hypothesis property test as part of canonical audit-pass chain) +
   FLAG-5b (DATA_PROVENANCE schema pin).

Land the MUST + SHOULD fixes inline (3 minutes' work, zero contract
impact), record the DEFER items as v0.2.5 follow-ups, and the patch is
ready for Wave 2 Code Reviewer.

---

**Reviewer**: TestingRealityChecker
**Evidence location**: spec + disposition memo + OSS algorithm study (paths
above)
**Re-review trigger**: only if MUST/SHOULD fixes substantively alter §0.4
or §3.5 rows beyond the 1-line count fix and 2 test additions.
