# Code Reviewer — v0.2.4 contract-only spec review (CORRECTIONS-Y-7)

- **Channel**: Code Reviewer (Wave 2; parallel Reality Checker channel runs separately)
- **Spec**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` @ v0.2.4 DRAFT
- **Scope reviewed**: §0.4 (Y-7 block), §3.5 rows for `JSONLReader`,
  `JSONLReadResult`, `build_daily_panel`, `DailyNotionalPanel`; revision-history
  entry; status frontmatter.
- **Mandate**: contract-only — no implementation diff exists yet.
- **Verdict**: **APPROVE_WITH_NITS**

---

## Findings table

| ID | Severity | Locus | Finding |
|---|---|---|---|
| CR-7-N1 | NIT | §0.4 final bullet | "The 5 existing counters become 6." Pre-Y-7 panel_builder threads **6** counters (`dropped_rows_count`, `dropped_error_count`, `dropped_non_assistant_count`, `WARN_missing_keys_count`, `dropped_unknown_model_count`, `multiple_substring_match_warning`); Y-7 adds the 7th. §3.5 `DailyNotionalPanel` row correctly states "the 7 counters above". The §0.4 phrasing is the only place the count is off-by-one. Trivial textual fix; non-blocking. |
| CR-7-N2 | NIT | §0.4 "Test surface added" | Tests proposed are state-of-system fixtures only. Suggest one additional adversarial property test: `dropped_malformed_line_count + len(records) + dropped_non_assistant_count + dropped_blank_lines == total_input_lines` (Hypothesis-generated mix of valid assistant / valid non-assistant / blank / null-byte / truncated lines). This is the line-conservation invariant; without it, a future regression that double-counts or silently swallows a line in the wrong bucket is undetected. Goes in Phase-3 hypothesis-tests pass anyway, but worth pinning in the spec. |
| CR-7-N3 | NIT | §0.4 / Task 10.5 | Impl plan (separate doc) must explicitly enumerate the `JSONLReadResult` field-addition migration: every constructor call site (currently only `JSONLReader.__call__`) and every `JSONLReadResult(...)` instantiation in tests must be updated in the same patch to avoid `TypeError: missing 1 required positional argument`. Frozen-dc with positional kwargs at construction means the addition is source-incompatible. The spec text says "minor migration" — acceptable in `iter/` pre-merge — but the impl-plan companion document must list the migration step (per mandate question 3). Flag the gap so it doesn't get lost between contract and impl. |
| CR-7-P1 | PRAISE | §0.4 paragraph 1 | Explicit OSS-mirror provenance ("ccusage `try { JSON.parse(line) } catch { continue }`") gives a stable external referent for the relaxation. This is exactly the kind of citation that makes a silent-skip defensible under the anti-fishing invariants. |
| CR-7-P2 | PRAISE | §0.4 "Risk and observability" | Names the failure mode the silent-skip can mask (producer-side schema regression in a future Claude Code release) AND names the compensating control (counter trend + Y-4 canonical-fixture test). This is the Honnibal try/except discipline at spec level — narrow exception, observable side-channel, ablation argument for why the skip is safe. |
| CR-7-P3 | PRAISE | §3.5 JSONLReader row | The two-sentence Y-7 amendment ("per-line `json.loads` wrapped in `try/except json.JSONDecodeError` → silently skip + increment ... `JSONLSchemaError` still raised on missing required field") is unambiguous about exception-class narrowness and the JSONDecodeError-vs-SchemaError split. Implementer cannot accidentally widen to `except Exception`. |

No BLOCKs.

---

## Per-question notes

1. **Tier discipline preserved (types ↛ modules/utils).** PASS. Counter lives
   on `JSONLReadResult` (types-tier per Y-5b). `JSONLReader` (utils) writes
   it; `build_daily_panel` (modules) reads it and threads to
   `DailyNotionalPanel` (types). No import inversion.

2. **Contract precision — narrow exception.** PASS. Spec text says
   `try/except json.JSONDecodeError` in two places (§0.4 paragraph 1, §3.5
   JSONLReader row). Neither permits widening. Honnibal try-except pin
   satisfied at contract level; implementer obligation is to literally write
   `except json.JSONDecodeError:` and nothing broader.

3. **API surface — `JSONLReadResult` field addition.** Source-incompatible
   change to a public types-tier dataclass. Acceptable in `iter/` pre-merge
   (no external consumer). **CR-7-N3** flags the impl-plan must list the
   migration step. Not a BLOCK because: (a) only one internal constructor
   exists today; (b) we are explicitly in the v0.2.x contract-churn window.

4. **Counter naming consistency.** PASS. `dropped_malformed_line_count` is
   exact-form match with the established
   `dropped_{non_assistant,unknown_model,rows,error}_count` family. Verified
   against §3.5 enumeration.

5. **No try/except masking real bugs.** PASS. The §0.4 explicit clause
   "Schema errors on _valid_ JSON (missing required fields, wrong types)
   still raise `JSONLSchemaError` — the relaxation is scoped to lines that
   aren't even parseable as JSON" is the load-bearing distinction. Pydantic
   schema failures on parseable JSON remain fatal, which preserves the
   producer-side regression alarm path.

6. **Test surface adequacy.** PARTIAL. The 3 proposed tests cover the
   happy-path (null-byte tail), the partial-write (truncated mid-JSON), and
   the counter-threading. Coverage is acceptable for a migration patch.
   CR-7-N2 suggests adding the line-conservation property test, which is the
   one invariant the example-based tests cannot establish.

7. **Documentation hygiene.** PASS. Status frontmatter bumped to 0.2.4 DRAFT
   with concise scope sentence. §3.5 header version-tagged to v0.2.4. §12
   revision-history entry is one paragraph, includes ccusage-mirror
   rationale, disposition path, and explicit closure scope ("line-level half
   of OSS-mirror permissive parsing that v0.2.3 Y-1 only addressed at the
   Pydantic-schema level"). Off-by-one in §0.4 (CR-7-N1) is the only doc
   defect.

---

## Honnibal audit-pass coverage

- **tighten-types**: New field `dropped_malformed_line_count: int` explicit;
  no `Any` / `Optional` smuggled. `JSONLReadResult` remains frozen-dc.
- **contract-docstrings**: §3.5 row functions as the contract-docstring.
  Raises/silenced exceptions both enumerated (`JSONLSchemaError` raised,
  `json.JSONDecodeError` silenced + counted).
- **try-except**: Narrow exception class pinned at spec level. §0.4
  observability paragraph names what the catch hides + the compensating
  control. This is the audit-pass discipline applied pre-implementation,
  which is the right time.
- **pre-mortem**: §0.4 "Risk and observability" *is* a one-paragraph
  pre-mortem (producer-side schema regression masked by silent skip; counter
  trend as detection signal; Y-4 canonical-fixture test as second alarm).
- **hypothesis-tests**: 3 example-based tests pinned; the property-test
  recommendation (CR-7-N2) is the one outstanding gap.
- **mutation-testing**: Not addressed at this contract layer; appropriate to
  defer to the impl patch (kill-rate target on the counter-increment and the
  exception-class match).

---

## Overall verdict

**APPROVE_WITH_NITS.** v0.2.4 is a tight contract-only amendment that
correctly scopes the silent-skip to `json.JSONDecodeError`, preserves the
fatal-`JSONLSchemaError` semantic for producer-side regressions, names the
counter on the right tier (types-tier `JSONLReadResult`, set by utils-tier
`JSONLReader`, read by modules-tier `build_daily_panel`), and documents the
risk + compensating control. Three NITs (off-by-one counter wording in §0.4;
add a line-conservation property test; enumerate the field-addition
migration in the companion impl plan) are non-blocking and can be cleaned up
in the impl patch.

No BLOCKs. Spec is ready to drive the implementation patch once the parallel
Reality Checker channel returns.
