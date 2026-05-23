# Wave 2 — Code Reviewer Report on v0.2.5 (CORRECTIONS-Y-8 uniqueHash Dedup)

**Reviewer**: Code Reviewer (Wave 2; parallel to Reality Checker)
**Date**: 2026-05-17
**Spec**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.5 (DRAFT)
**Scope**: §0.5 CORRECTIONS-Y-8, §3.5 contracts table row updates, §12 revision history
**Verdict**: **APPROVE_WITH_NITS**

---

## Summary

The v0.2.5 contract-only amendment is well-scoped, surgically minimal, and
correctly mirrors ccusage's source-truth dedup discipline. The empirical
justification (2.11× → 0.977× cost convergence) is direct, the failure mode
(per-message duplication on `${message.id}:${requestId}`) is mechanistically
explained, and the residual gaps are honestly filed to Y-9 rather than
absorbed into Y-8 to make convergence look tighter. Tier discipline is
preserved, the new counter follows the established `dropped_X_count` naming
pattern, and the test surface is honest about the non-obvious behaviors
(hasSpeed tiebreaker, traversal-order invariant).

Two nits and one suggested clarification — none blocking. The amendment is
ready to drive an implementation patch.

---

## Findings

### PRAISE

- **Empirical-first amendment discipline.** §0.5 leads with the
  measured-from-real-data 2.11× overcount and only then proposes the spec
  change. Per `feedback_pathological_halt_anti_fishing_checkpoint`, this is
  the correct HALT → root-cause-investigation → CORRECTIONS-block path. No
  threshold tuning, no silent re-run; the gap exceeded the 0.1% ccusage-
  parity target (Y-2/Y-4) by ~3 orders of magnitude, which is exactly the
  kind of spec-vs-data contradiction that should trigger an amendment cycle.

- **ccusage source-citation precision.** §0.5 names the exact compiled-JS
  symbols (`Wr` for uniqueHash, `Sr` for tokenTotal, `$` for keep-larger,
  `ui` for per-file dedup, `pi` for cross-file dedup) at a pinned version
  (19.0.3) of `node_modules/ccusage/dist/data-loader-LJFbLyZj.js`. This is
  the level of provenance needed for a "we are deliberately mirroring an
  OSS reference" claim to be auditable later. The Y-8 closure of the OSS
  algorithm study's earlier gap (it caught Y-1 parsing but missed dedup
  because the gap was scale-dependent) is honestly acknowledged.

- **Honesty about residual gaps.** The 0.10× input_tokens anomaly is
  explicitly NOT claimed as closed by Y-8 and is filed as Y-9. The 2.3%
  residual on output/cc/cr is also acknowledged as not-yet-explained with
  three concrete working hypotheses. This is the opposite of the
  anti-fishing "footnote and move on" anti-pattern.

- **Tier discipline correctly traced.** The amendment recapitulates the
  Y-5a/-5b lessons from v0.2.3: the counter lives on `JSONLReadResult`
  (types tier) per Y-5b precedent, the dedup map is local to `__call__`
  (utils tier, no instance state), and threading goes
  `JSONLReadResult → build_daily_panel → DailyNotionalPanel → CLI` exactly
  as the previous 7 counters do.

### BLOCK

(none)

### NIT-1 (suggested clarification to §0.5 — non-blocking)

The spec text says "in-memory dedup map keyed on `_unique_hash(message.id,
requestId)` → index of currently-kept entry" but does not state explicitly
that **the dedup map is local to a single `__call__` invocation, not
instance state**. Mandate question (3) is the right one to surface this.

A `JSONLReader` is currently a `utils` (IO Boundary) tier class with
`__init__` — by the functional-python tier rules, mutable state is
*permitted* on this tier. But promoting the dedup map to instance state
would create cross-invocation leakage (a second `__call__` with a
narrower `since`/`until` window would see entries from the first call
"already-kept" and skip valid rows). The contract-correct design is:

> The dedup map is constructed fresh inside each `__call__` invocation
> and discarded on return. It is **NOT** an instance attribute. The
> mutability of the per-call accumulator inside `__call__` is consistent
> with the IO-Boundary tier discipline; the frozen-dc invariant applies
> only to `JSONLReadResult` (the return value).

**Suggested edit**: add one sentence to the third bullet of §0.5's "Spec
change (contract-only)" block stating "the dedup map is local to a single
`__call__` invocation; it is not an instance attribute." Or fold this
into the §3.5 `JSONLReader` row's UniqueHash dedup clause.

### NIT-2 (collision-safety on the `:` delimiter — non-blocking)

Mandate question (2). Anthropic's documented ID format is `msg_<base62>`
for message IDs and `req_<base62>` for request IDs (alphanumeric only;
underscore prefix terminator, no colons). The format
`f"{message.id}:{requestId}"` is safe under current Anthropic field
constraints.

**However**, this safety is contingent on Anthropic's public ID schema not
drifting. A more defensive design — and one that costs nothing — would be
to use a tuple-key `(message.id, requestId)` directly in the dict, which
eliminates the delimiter dependency entirely. ccusage chose string-concat
because TypeScript object keys are strings; Python dicts support tuple
keys natively. This is a strictly-stronger design with no behavioral
change.

**Suggested edit (optional)**: change the spec from
`_unique_hash = f"{message.id}:{requestId}"` to
`_unique_hash = (message.id, requestId)` (tuple, with `None`
falling-through for the requestId-missing case as `(message.id, None)`).
The helper signature in the §3.5 contracts table row would then be
`_unique_hash(msg_id: str, request_id: str | None) -> tuple[str, str | None]`.

If the spec author prefers the string-concat form for ccusage-parity
debuggability (i.e., easier to print/log/diff against ccusage's own
hashes), that's also defensible — but then please add a sentence
asserting "no Anthropic-emitted message.id or requestId contains the
`:` character at the pinned LiteLLM SHA / ccusage 19.0.3 surface" and
file a Y-9 sentinel if either field ever ships with a colon. Not
blocking either way.

### NIT-3 (counter-increment semantics — clarification)

§0.5 says "the counter increments every time a duplicate hash is
encountered and SKIPPED (replacements also tick the counter, since they
represent a duplicate that was seen but superseded)."

This is unambiguous *as code*: every time `_unique_hash` collides with an
already-seen entry, increment by 1, regardless of whether the new row
replaces or is discarded. Cross-check: the 5 test cases enumerate
`dropped_duplicate_count == 2` for a 3-row collision (correct under this
rule: 2 collisions, regardless of which row survives) and
`dropped_duplicate_count == 1` for the across-files 2-row collision
(correct).

**Minor improvement**: consider renaming the field to
`duplicate_collision_count` since "dropped" is semantically misleading
when the counter ticks on replacements (the prior kept-entry is dropped,
not the incoming row — but from a "rows seen but not retained" view,
both interpretations work). On reflection: established naming pattern
(`dropped_X_count`) and Y-5a discipline strongly favor keeping
`dropped_duplicate_count` for consistency. **Recommend NO change** —
just flagging for the spec author's awareness. The docstring on the
`JSONLReadResult` field should state the increment rule explicitly.

---

## Per-question notes

### (1) Tier discipline preserved

**PASS.** The counter is added to `JSONLReadResult` per Y-5b precedent
(types tier). The `_unique_hash` helper is correctly placed in
`jsonl_io.py` (utils tier) where it belongs — it is an IO-Boundary
implementation detail, not a value-tier type. The §3.5 `JSONLReadResult`
row in v0.2.5 lists `dropped_duplicate_count: int` alongside the existing
two counters from Y-5a/Y-7, preserving the established types-tier
container shape.

No tier crossing introduced. types/ still imports neither modules/ nor
utils/; modules/ still imports types/ but not utils/. The `_unique_hash`
helper does not need to be exported from any module — it lives entirely
inside `jsonl_io.py` as a private helper.

### (2) Hash collision safety

**PASS with NIT-2.** See NIT-2 above. Under Anthropic's current public ID
schema, `:` is excluded from message.id and requestId, so
`f"{message.id}:{requestId}"` is safe. The tuple-key alternative is
strictly stronger but optional.

### (3) Mutability discipline (dedup map local to `__call__`)

**PASS with NIT-1.** The intent is clearly correct (local to invocation,
not instance state), but the spec text doesn't make this explicit. See
NIT-1 above. Suggested one-sentence clarification.

### (4) API surface change (`JSONLReadResult.dropped_duplicate_count`)

**PASS.** Adding a field to a frozen `@dataclass(slots=True)` is
source-incompatible — every `JSONLReadResult(...)` constructor call must
be migrated. Confirmed call sites that will need updates:

- `simulations/dev_ai_cost_v2/jsonl_io.py:332` (the producer)
- `simulations/tests/test_dev_ai_cost_v2_types.py` (5 construction sites
  at lines 344, 357, 367, 377, 385)
- `simulations/tests/test_dev_ai_cost_v2_panel_builder.py` (3 sites at
  lines 111, 299, 381)
- `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` (1 site at line
  548)

That's ~10 call sites. Per the v0.2.4 Y-7 precedent (which migrated
`dropped_malformed_line_count` similarly), this is acceptable inside
`iter/ai-cost-2026-05` pre-merge.

**Action for the implementation patch (not the spec)**: enumerate these
migration sites in the implementation plan's task breakdown, the way Y-5f
and Y-7 did. The spec itself does not need to enumerate them; that is
plan-emission's job. **No spec-text change required for this mandate
question.**

### (5) Naming consistency

**PASS.** `dropped_duplicate_count` fits the established pattern. The 7
prior counters all follow `dropped_X_count` or `WARN_X_count` or
`<noun>_warning`. The new counter is the 4th `dropped_X_count` peer:

- `dropped_rows_count` (weekend filter)
- `dropped_error_count` (is_error=True filter)
- `dropped_non_assistant_count` (Y-5a type-discriminator filter)
- `dropped_malformed_line_count` (Y-7 line-level skip)
- `dropped_duplicate_count` (Y-8 uniqueHash dedup) ← new
- `dropped_unknown_model_count` (PricingTable lookup failure)

Pattern-fit: clean.

### (6) Test honesty

**PASS.** The 6 enumerated tests cover the algorithmic decision-space:

| Test | Property under test | Strength |
|---|---|---|
| `test_jsonlreader_dedup_within_file` | basic keep-larger rule | example-based, correct |
| `test_jsonlreader_dedup_across_files` | cross-file dedup (ccusage `pi`) | example-based, correct |
| `test_jsonlreader_dedup_hasspeed_tiebreaker` | tiebreaker on equal tokenTotal | non-obvious behavior — explicit test is the right call |
| `test_jsonlreader_dedup_no_request_id_falls_back_to_message_id` | fallback when requestId absent | edge case, covered |
| `test_jsonlreader_dedup_traversal_order_invariant` (Hypothesis) | "result is invariant under permutation of file-traversal order" | property-based — the strongest invariant statement, exactly right |
| `test_dropped_duplicate_count_threaded_through_panel` | counter surfaces on `DailyNotionalPanel` | threading-discipline check, matches Y-5a/Y-7 pattern |

The Hypothesis traversal-order test is well-scoped: the property "the set
of kept entries is the same regardless of file iteration order" is
precisely what ccusage's `pi` cross-file dedup guarantees, and is
non-trivial to verify by example because the failure mode (e.g., a "first
seen wins" bug) would only manifest on specific orderings. Strong
choice.

The within-file vs across-files split mirrors ccusage's `ui` (per-file)
and `pi` (cross-file) discipline. Both are necessary because the keep-
larger rule must apply uniformly across the entire corpus, not just
within each file.

**One missing test** (not blocking, recommend adding): a
`test_jsonlreader_dedup_missing_message_id_admitted_without_dedup` test —
the spec says "else `None` (row skipped from dedup but still admitted
into output for fault-tolerance — a missing message.id is rare in real
data and our v0.2.3 Y-1 already requires assistant rows to be
parseable)." This branch should be exercised by a unit test, because
"admitted without dedup" is a non-obvious behavior — a future refactor
could easily change this to "dropped" or "errored" without flagging it.

**Recommendation**: add a 7th test
`test_jsonlreader_dedup_missing_message_id_admitted_without_dedup` to
the §0.5 enumeration. Non-blocking; can land in the implementation
patch.

### (7) Pre-mortem on residual gaps

**PASS.** §0.5 honestly defers two residual gaps to Y-9 backlog:

1. The **0.10× input_tokens anomaly** (order-of-magnitude shortfall on a
   single category). This is the right gap to flag loudly. The §0.5
   text is explicit: "Y-8 does NOT close" this. The mitigation argument
   (input is ~0.02% of total cost, so the headline cost-convergence
   stands) is quantitatively defensible — but the spec should not
   over-state confidence in this. Read of the relevant passage:

   > "input is ~0.02% of total cost in the empirical data, so this
   > residual does NOT block the v0.2.5 cost-reliability convergence.
   > Surfaced for follow-up."

   That's honest. It does not claim "input_tokens shortfall doesn't
   matter"; it claims "input_tokens shortfall does not block the
   *primary* convergence goal of v0.2.5" with the magnitude
   justification. Accurate.

2. The **2.3% residual** on output/cc/cr. Three working hypotheses
   listed: (a) iterations-array aggregation, (b) `dropped_unknown_model`
   fallback divergence, (c) hasSpeed tiebreaker edge cases. None
   claimed-as-fixed; all filed to Y-9. Honest.

**Sub-question raised in mandate**: "Is the deferral honest — i.e., does
it not under-state the residual gap?"

My read: the deferral is honest. The 0.977 vs 1.000 cost ratio is a
genuine convergence (within the 2.3% residual which is also flagged),
and the categorical breakdown is reported transparently. The spec does
NOT claim "ccusage-parity within 0.1%" is achieved by Y-8 alone — that
target (Y-2/Y-4) remains a separate measurement, not asserted as
satisfied by v0.2.5. v0.2.5 closes the dominant root cause; Y-9 must
close the rest before the §2.1 verdict-table "ccusage-parity within
0.1%" criterion can be claimed as met.

**Recommendation (non-blocking)**: §0.5's "Anti-fishing invariant carried"
paragraph would benefit from one explicit sentence acknowledging that
the §2.1 / §6 ccusage-parity-0.1% criterion is **still not satisfied**
by v0.2.5 (we go from 211% over to 2.3% over, which is much closer but
still 23× over the 0.1% target). The Y-9 backlog must close this before
R5 can produce M-design-usable output per the §2.1 verdict-logic table.
Right now §0.5 leaves the parity-target status implicit; making it
explicit prevents a future reader from assuming v0.2.5 satisfies the
parity criterion when it does not.

### (8) Documentation hygiene

**PASS.** Spot-checks:

- **§3.5 contracts table row updates (lines 1127–1128)**: the
  `JSONLReader` row in §3.5 now includes a full UniqueHash dedup clause
  citing Y-8, the dedup map keying rule, the keep-larger + hasSpeed
  tiebreaker discipline, and the duplicate-counter increment semantics.
  Accurate against §0.5 text. The `JSONLReadResult` row lists
  `dropped_duplicate_count: int` as one of three counters carried by
  the types-tier dataclass, matching Y-5b precedent.
- **§3.5 row 1132 (`build_daily_panel`)**: counter list updated to
  include `dropped_duplicate_count` in the "Threads ALL counters"
  enumeration. Accurate.
- **§3.5 row 1133 (`DailyNotionalPanel`)**: "the 8 counters above"
  language matches the new count (was 7 + 1 = 8). Accurate.
- **Status frontmatter (line 5)**: bumped to `0.2.5` with appropriate
  DRAFT marker and a one-sentence summary of the convergence
  (2.11×→0.977×). Concise + informative.
- **§12 revision history entry (line 1389)**: 0.2.5 row added; concise,
  cites the empirical findings file, names the residual gaps as Y-9.
  Stylistically consistent with prior entries.
- **§0.5 section header**: "v0.2.4 → v0.2.5 CORRECTIONS (reliability-
  convergence patch)" matches the established pattern of v0.2.3 / v0.2.4
  CORRECTIONS section headings.

One minor doc-hygiene NIT:

### NIT-4 (numbering off-by-one in counter-count language)

§0.5 says: "The 7 existing counters [...] become 8." Cross-checking the
existing v0.2.4 spec: `dropped_rows_count`, `dropped_error_count`,
`dropped_non_assistant_count`, `dropped_malformed_line_count`,
`WARN_missing_keys_count`, `dropped_unknown_model_count`,
`multiple_substring_match_warning` = **7 prior counters**, +1 new =
**8 total**. Confirmed accurate. No change.

(Initial flag retracted on re-counting; leaving here for audit
visibility.)

---

## Honnibal audit-pass coverage

The amendment was reviewed for code-quality concerns that would emerge in
the implementation patch (anticipatory review per the Honnibal chain):

| Audit pass | Coverage in v0.2.5 | Findings |
|---|---|---|
| **tighten-types** | NEW field type is explicitly `dropped_duplicate_count: int` (matches existing peer fields); helper signature implicit but well-determined | None — the type story is clean. The tuple-key alternative (NIT-2) would tighten further but is optional. |
| **contract-docstrings** | Not directly in scope for spec; but the implementation patch should add a docstring on `JSONLReader.__call__` documenting "in-memory dedup keyed on `(message.id, requestId)`; keep-larger-tokenTotal with hasSpeed tiebreaker; missing message.id admitted without dedup." | Flag for impl patch: §0.5 should require the implementation to update `JSONLReader.__call__`'s docstring with the dedup contract, the `_unique_hash` helper's docstring with its return-`None` semantics, and the `JSONLReadResult.dropped_duplicate_count` field docstring with the "increments on every collision including replacements" rule per NIT-3. |
| **try-except** | No new exception paths introduced. Dedup is pure dict-lookup arithmetic. `_unique_hash` returning `None` is handled by a conditional skip, not by raising. Clean. | None. |
| **pre-mortem** | §0.5 includes a "Backlog (Y-9)" paragraph with three working hypotheses for the residual gap. This *is* a pre-mortem-style audit of "what could still be wrong." | Recommend §0.5 also surface the *failure modes* of the dedup map itself: (a) extreme memory if the corpus is millions of messages (current scale is ~87k rows, 3-tuple of int-equivalent per entry = OK; flag if scale grows 100×); (b) the `None`-keyed fallback could mask a class of malformed rows if message.id loss is systematic, not random. Optional addition to §0.5 pre-mortem paragraph. |
| **mutation-testing** | Not in scope for the spec amendment, but the test surface (6 tests) is well-shaped for mutation coverage: each test pins a specific decision (keep-larger, hasSpeed-tie, traversal-invariance, threading) that would catch the corresponding code mutation. | Adequate. The traversal-order Hypothesis test alone covers a large mutation space. |

The amendment is implementation-ready: the contract is complete, the
behaviors are unambiguously specified, and the test enumeration covers
the algorithmic decision-space tightly enough that a Honnibal audit-pass
chain on the implementation patch should be a small follow-on rather
than a re-design.

---

## Overall verdict

**APPROVE_WITH_NITS**

The v0.2.5 contract-only amendment is sound. The empirical justification
is direct, the spec change is surgically minimal, tier discipline is
preserved, the counter follows the established naming pattern, the test
surface is honest about non-obvious behaviors, and the residual gaps are
honestly filed forward rather than glossed over.

Four nits, none blocking:

1. **NIT-1**: Add one sentence to §0.5 making explicit that the dedup
   map is local to `__call__` and not instance state.
2. **NIT-2** (optional): Consider tuple-keying the dedup map for
   delimiter-independence, or add an explicit assertion that Anthropic
   IDs do not contain `:`.
3. **NIT-3**: Have the implementation patch (not the spec) document
   the counter-increment rule explicitly on the field docstring.
4. (Sub-note inside question 7): Explicitly acknowledge in §0.5 that
   the ccusage-parity-0.1% criterion (§2.1 / §6) is **still NOT
   satisfied** by v0.2.5 — Y-9 must close the residual 2.3% before that
   criterion graduates.

Additional optional enhancement: add
`test_jsonlreader_dedup_missing_message_id_admitted_without_dedup` as a
7th enumerated test to cover the `None`-key fallback branch.

The spec is ready to drive the implementation patch in parallel with /
after the Reality Checker's verdict on the same amendment. No
re-emission cycle required after these nits land.

---

## File pointers

- Reviewed spec: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` (v0.2.5)
- Empirical justification: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-17-v0_2_5-dedup-discovery/findings.md`
- Existing types-tier dataclass (will gain the new field):
  `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/dev_ai_cost_v2/types.py` (lines 192–245)
- `JSONLReadResult` constructor call sites that the implementation patch must migrate:
  - `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/dev_ai_cost_v2/jsonl_io.py:332`
  - `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/tests/test_dev_ai_cost_v2_types.py:344,357,367,377,385`
  - `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/tests/test_dev_ai_cost_v2_panel_builder.py:111,299,381`
  - `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/tests/test_dev_ai_cost_v2_jsonl_io.py:548`
