# Code Reviewer — v0.2.8 contract-only spec amendment (CORRECTIONS-Z2)

- Spec: `docs/specs/2026-05-16-ai-cost-factor-model-design.md`
- Frontmatter `spec_version`: 0.2.8
- Patch surface: §0.8 (NEW, ~100 lines), revision-history row appended in §12
- Wave: 2 (parallel to Reality Checker)
- Reviewer scope: contract integrity, cross-reference hygiene, FP threshold precision, scope discipline
- Verdict (this channel): **APPROVE_WITH_NITS**

---

## Summary

§0.8 closes a real premise gap in §2.2.A's HALT-on-FAIL rule via a
strictly-stronger replacement integrity check (additive identity at FP
exactness) gated on a numerical regime predicate (variance ratio < 0.01).
The patch is contract-only, has zero code-surface beyond a markdown-cell
addition to `03_r4s3_cop_consistency.ipynb`, preserves §2.2.A verbatim, and
correctly bumps the frontmatter `spec_version` (catching up the missed
v0.2.7 bump).

The substitution direction is anti-fishing-clean: HAC-OLS (statistical) is
replaced by FP-identity (deterministic, no power dependence). The patch
even acknowledges this in the "Anti-fishing invariant carried" paragraph.

Findings below are all NITs — none block approval.

---

## Findings

### BLOCK

None.

### NIT

**NIT-1 — Variance-ratio series definition is ambiguous in the narrative
text (but unambiguous in the notebook snippet).**

§0.8 narrative (lines 1092, 1104, 1121, 1141) repeatedly writes the
threshold as `var(USDCOP) / var(cost^USD) < 0.01` without annotating
whether these are variances of raw log-returns (`Δln`) or of
absolute-log-returns (`|Δln|`). The downstream R4-S3 spec is a regression
of `|Δln Cost^COP|` on `|Δln USDCOP|`, so the operationally meaningful
ratio is on the abs-series. The Task 13-bis snippet (line 1162) correctly
uses `var_ratio = var(abs_dln_trm) / var(abs_dln_cop_usd)`. The
disposition memo also operates on `|Δln|`. So the *intended* definition is
clear from cross-references but **the spec body itself is
underspecified** — a reader of §0.8 alone cannot tell which series.

Suggestion (one-sentence fix): in §0.8 first paragraph, change
`var(USDCOP) << var(cost^USD)` to `var(|Δln USDCOP|) << var(|Δln cost^USD|)`
once, then continue with the shorthand. Or add a single-line definitional
note: "Throughout §0.8, `var(USDCOP)` and `var(cost^USD)` denote variance
of `|Δln USDCOP|` and `|Δln NotionalCost^USD|` respectively (matching the
§2.2.A regressand/regressor series)."

This matters because (a) the empirical numbers cited in §0.8 (`var ≈
3.8e-5`, `var ≈ 1.6`) are consistent only with the abs-log-return
interpretation — different series would produce different ratios and a
post-hoc reader cannot reverse-engineer this from the narrative alone, and
(b) the 0.01 threshold is series-dependent: `var(Δln)` and `var(|Δln|)`
differ in general (they coincide only when the series has zero mean, which
isn't guaranteed for first-differences over a 28-day window).

Severity: NIT. The notebook snippet is correct; the disposition memo
disambiguates; a Task 13-bis implementer cannot get this wrong. But spec
text should be self-contained.

**NIT-2 — `1e-12` FP tolerance derivation is implicit.**

Spec asserts `max |Δln Cost^COP − Δln Cost^USD − Δln USDCOP| < 1e-12`
without showing the headroom calculation. Measured: 1.78e-15. Threshold:
1e-12. Buffer: ~563× (between 2 and 3 orders of magnitude — the spec
narrative says "three orders of magnitude tighter than FP machine epsilon"
on line 1099, which is also the headroom against ε ≈ 2.22e-16, not against
the 1e-12 threshold).

For double-precision Δln operations chained 3-deep (sub of three log
values), the worst-case relative error scales as ~3·ε on each Δln, and
the subtraction of three quantities of similar magnitude can lose up to
~6·ε ≈ 1.3e-15 of relative accuracy. With Δln magnitudes on the order of
1e-2 (daily abs-log-returns), absolute error floor is ~1.3e-17 — so 1e-12
is conservative by ~5 orders of magnitude vs. theoretical FP floor, ~3
orders vs. measured.

Suggestion: add a parenthetical, "(threshold chosen ~3 orders of magnitude
above measured FP error 1.78e-15; conservative against catastrophic
cancellation under future panel-builder refactors)". Not blocking — the
threshold is sound; the rationale is just opaque to future readers.

**NIT-3 — §0.8 reclassifies Task 13 verdict but doesn't update §2.2.A's
verdict-logic block.**

§2.2.A (lines 1332–1334) reads: "Verdict on R4-S3-COP: CONSISTENCY-PASS if
... CONSISTENCY-FAIL otherwise. A consistency-fail HALTs the pipeline
(suspect data corruption), not the framework." §0.8 explicitly states
"§2.2.A is preserved verbatim; §0.8 is a premise-conditional addendum, not
a replacement" (line 1182). This is a deliberate design choice, defensible
on patch-isolation grounds, but a reader landing on §2.2.A without §0.8
would apply the old HALT rule. The disposition memo and the notebook's
new markdown cell are the only forward-pointers.

Suggestion: insert one sentence at the end of §2.2.A's verdict paragraph:
"See §0.8 (CORRECTIONS-Z2) for the premise-conditional addendum when
`var(|Δln USDCOP|) / var(|Δln cost^USD|) < 0.01`." This preserves §2.2.A
verbatim semantics while making the addendum discoverable from the rule
site. Not blocking.

**NIT-4 — Frontmatter status line is a 5-line run-on sentence.**

Line 5 (frontmatter `status`) is one ~700-character sentence packing five
distinct facts (patch trigger, root cause, fix, pivot, catch-up note).
Hard to parse. Most prior versions have shorter status lines.

Suggestion: break into bullets or short sentences. Cosmetic.

### PRAISE

**P-1 — Substitution direction is correctly anti-fishing.** Replacing a
statistical test (HAC-OLS p-value) with a deterministic identity check
(FP exactness) is *stricter*, not looser. The patch explicitly calls this
out ("The replacement integrity check (additive identity) is STRICTER than
the original (HAC-OLS) because it requires floating-point exactness, not
statistical significance"). This is the right framing and avoids the
trap of "we failed our test so we weakened it."

**P-2 — Preconditions correctly composed as AND, not OR.** Both
conditions (a) identity passes AND (b) variance ratio < 0.01 must hold
for reclassification. §0.8 makes this unambiguous in two places: bullet
list ("Both preconditions must be satisfied") and the explicit failure
path ("If either fails, the original §2.2.A HALT-on-FAIL rule stands").
This is exactly the right contract — neither precondition alone is
sufficient to overrule §2.2.A.

**P-3 — Patch surface is genuinely minimal.** No `jsonl_io.py`,
`panel_builder.py`, `anthropic_pricing.py`, or types-tier changes. The
only implementation diff is two computed values + one markdown cell in
`03_r4s3_cop_consistency.ipynb`. The "no code outside the notebook
changes" assertion (line 1168) holds — these are pure numpy variance
computations on already-built panel columns.

**P-4 — Convergent-evidence framing is sound.** §0.8 cites three
independent measurements (R5 PRIMARY FX share ≈ 0.003%; Z-1 multi-period;
Z-2 backcast) corroborating that the small FX share is real, not a
pipeline artifact. This converts what would otherwise look like
post-hoc rescue into an internally-consistent finding triangulated across
arms. Good defensive scaffolding.

**P-5 — Frontmatter catch-up sync handled correctly.** The note that
v0.2.7 updated §0.7 body but missed the `spec_version` bump is honest,
caught in this revision, and documented in both the status line and the
§12 revision-history row.

---

## Per-question notes

**Q1 — Threshold pinning.** Threshold `< 0.01` is pinned literally in
the spec at three sites (lines 1121, 1141 via cross-reference, 1815
revision-history). The condition is stated symmetrically as "two orders
of magnitude apart or more". PASS for pinning; NIT-1 applies to the
units/series ambiguity.

**Q2 — FP tolerance precision.** `1e-12` is reasonable for
double-precision chained Δln subtraction. Measured 1.78e-15 → 1e-12
gives ~563× buffer (2.75 OoM). Float64 ε ≈ 2.22e-16; worst-case
chained-arithmetic relative error on three log subtractions is bounded
above by ~6ε ≈ 1.33e-15, so 1e-12 sits ~3 OoM above the theoretical
floor, comfortably below the measured value. **PASS.** See NIT-2 for a
docstring-style improvement suggestion.

**Q3 — Cross-reference hygiene.**

- §2.2.A → exists at line 1312, content matches §0.8's quoted "HALT-on-FAIL"
  rule. CORRECT.
- §2.1 R5 → exists at line 1227, "FX share ≈ 0.003%" is consistent with
  §2.1's R5 PRIMARY descriptive output. CORRECT.
- §0.6 Z-arms → exists at line 783, Z-1/Z-2/Z-3 enumerated as cited.
  CORRECT.
- Disposition memo path → `notebooks/dev_ai_cost_v2/dispositions/2026-05-17-task13-consistency-fail.md`
  EXISTS on disk. CORRECT.

All four cross-references resolve.

**Q4 — Implementation surface.** Confirmed minimal:

- No diff in `simulations/` package (types/, modules/, utils/).
- No diff in `scripts/build_notional_cost_panel.py`.
- No diff in `dev_ai_cost_v2/jsonl_io.py`, `anthropic_pricing.py`,
  `panel_builder.py`.
- Only notebook-markdown delta to `03_r4s3_cop_consistency.ipynb` (two
  computed-value cells + one markdown banner).

Patch surface is genuinely contract-only. **PASS.**

**Q5 — Preconditions are AND not OR.** Unambiguous — see PRAISE P-2.
**PASS.**

**Q6 — Failure path is explicit.** Line 1144–1145: "Both preconditions
must be satisfied. If either fails, the original §2.2.A HALT-on-FAIL rule
stands." Followed by the §2.2.A-preservation note on line 1182.
**PASS.**

**Q7 — Documentation hygiene.**

- §3.5 component contracts: NOT touched. Correct — no new contracts or
  signature changes. **PASS.**
- §2.2.A: preserved verbatim (verified via grep — verdict block at lines
  1332–1334 unchanged). **PASS.** (NIT-3 suggests one optional
  forward-pointer.)
- §12 revision history: row 0.2.8 appended at line 1815 with full
  context. **PASS.**
- Frontmatter `spec_version`: 0.2.8 (line 3). Catch-up bump documented.
  **PASS.** (NIT-4 on status-line readability.)

---

## Honnibal audit-pass coverage

- **tighten-types**: N/A — no Python signature changes. The two computed
  values in the notebook (`var_ratio`, `additive_identity_max_error`)
  are plain floats; no annotation surface.
- **contract-docstrings**: N/A — no function additions. The notebook
  markdown cell *is* the contract documentation for the precondition
  check.
- **hypothesis-tests**: N/A for contract patch. If the additive-identity
  check were lifted into `panel_builder.build_daily_panel` as a runtime
  postcondition, a Hypothesis property `additive_identity_holds_at_fp`
  would be appropriate. As scoped (notebook-only), not required.
- **try-except**: N/A — no exception-handling surface.
- **pre-mortem**: The patch itself *is* a pre-mortem outcome — it
  retrofits a failure mode (premise-conditional HALT) that wasn't caught
  ex-ante. The replacement integrity check is more robust than the
  original. No further pre-mortem surface in the patch.
- **mutation-testing**: N/A for spec text. The notebook-level integrity
  check has two mutants worth considering when the implementation lands:
  (i) flip `<` to `<=` on `1e-12` (should still pass given 1.78e-15
  margin); (ii) flip `<` to `<=` on `0.01` (the boundary itself is
  empirically ~4 OoM from observed value, so harmless under current
  data). Both are tolerance-edge mutants that pass.

Overall: audit-pass chain is N/A by construction (contract-only patch with
no Python surface). When the notebook implementation lands (Task 13-bis),
a single Hypothesis property on the additive identity over synthetic
panels would be worth adding — flagging here as a forward-looking item
for the impl review, not a current blocker.

---

## Overall verdict

**APPROVE_WITH_NITS.**

Patch is contract-only, anti-fishing-clean (stricter replacement check),
cross-references resolve, frontmatter is correct, §2.2.A preserved
verbatim, AND-precondition logic unambiguous, failure path explicit,
patch surface verified minimal.

The four NITs are all clarity/discoverability items — none would change
behavior or block implementation. NIT-1 (variance series ambiguity in
narrative) is the most worth addressing inline before Task 13-bis lands,
because the disposition memo and notebook snippet disambiguate but the
spec text alone does not.

Recommend approval with optional inline NIT fixes during the same edit
pass that authors the Task 13-bis notebook markdown cell. No re-review
required.

---

## Cross-channel coordination

Parallel Reality Checker channel should be expected to verify:
- Disposition memo content matches §0.8's cited numerical values
  (1.78e-15, 3.8e-5, 1.6, α̂₁^COP = −17.98, p = 0.670, etc.).
- File-existence of disposition memo and notebook on disk.
- §2.1 / §0.6 cross-references' substantive content (not just existence)
  is consistent with §0.8's claims.

This channel did not duplicate those checks; deferred to Reality Checker
scope per two-wave protocol.
