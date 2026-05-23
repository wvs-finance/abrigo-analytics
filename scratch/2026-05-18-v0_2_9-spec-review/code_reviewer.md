# Code Reviewer — v0.2.9 Contract-Only Spec Amendment Review

**Spec:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md`
**Patch:** CORRECTIONS-Z3 — power-recipe lag pin (§0.9, NEW)
**Wave:** 2 of 2 (parallel to Reality Checker anti-fishing review)
**Branch state:** `master` w/ uncommitted modification to spec file (diff: +106 / -2)
**Reviewer focus:** spec rigor, implementation surface, verdict-label hygiene,
diagnostic-transparency, cross-references, documentation hygiene, §0.8 precedent
preservation.

---

## Summary (overall impression)

The patch is a clean **contract-only** clarification: it pins one of two
defensible readings of CORRECTIONS-J's power-recipe text, defends the pin on
first-principles (not on which answer it gives), documents the divergent
recipe transparently in the same notebook cell, and updates the revision
history. The diff is exactly the surface promised — frontmatter + §0.9 + §12
revision row, no contract changes to §3.5, no code changes outside the Task
14 notebook.

The patch is largely **APPROVE_WITH_NITS**. The strongest concern is hygiene-
shaped, not correctness-shaped: §2.2.B's power-calc paragraph (the section §0.9
references as "preserved verbatim") gives no forward-pointer to §0.9, even
though the §0.8 patch established exactly that forward-pointer pattern. A
reader landing on §2.2.B will re-encounter the same ambiguity that triggered
the Task 14 HALT. PARTIAL-* verdict labels are also defined only in §0.9 prose,
not in §2.2.B's verdict-logic bullet list.

---

## Findings

### BLOCK
None.

### NIT

**NIT-1: Missing forward-pointer §2.2.B → §0.9 (pattern-break vs §0.8).**

§2.2.B lines 1479-1481 read verbatim:

> **Power calculation (CORRECTIONS-J + CORRECTIONS-U)**: power Monte-Carlo'd
> on **residual SD** of $|\Delta\ln\text{NotionalCost}^{USD}|$ after
> partialling out $|\Delta\ln\text{Tokens}|$.

The §0.8 patch precedent (line 1443-1449) added an inline forward-pointer to
§0.8 in §2.2.A so future readers landing on the canonical section get routed
to the premise-conditional patch:

> **v0.2.8 amendment (CR NIT-3 forward-pointer):** the HALT-on-FAIL rule
> above is **premise-conditional**. §0.8 CORRECTIONS-Z2 reclassifies …
> Readers landing on this section should consult §0.8 before applying the
> HALT rule.

§0.9 says "§2.2.B's power-floor language is preserved verbatim" — accurate
but insufficient. The whole point of §0.9 is that "partialling out
$|\Delta\ln\text{Tokens}|$" without a lag-pin is ambiguous (that is the
finding that produced the HALT). A reader landing on §2.2.B today will
re-derive the same ambiguity. Recommend adding a §0.9 forward-pointer
adjacent to the "partialling out" sentence, mirroring §0.8's pattern:

> **v0.2.9 amendment (forward-pointer):** "partialling out
> $|\Delta\ln\text{Tokens}|$" was silent on lag structure. §0.9
> CORRECTIONS-Z3 pins the canonical recipe to **contemporaneous**
> $|\Delta\ln\text{Tokens}|_t$ (no lag); the lagged-tokens alternative
> is computed and reported in the notebook but does NOT gate the test.

This is the same hygiene rule the §0.8 patch self-applied. Without it,
v0.2.9's discipline is asymmetric with v0.2.8's. (Low-cost fix; ~3 lines.)

**Affected line:** ~1481 in current file (between "partialling out
$|\Delta\ln\text{Tokens}|$." and the "Power-HALT checkpoint…" sentence).

**NIT-2: §4 power-HALT checkpoint paragraph also lacks lag pin / forward-pointer.**

§4 line 1714-1716 reads:

>   - **Power-measurement HALT-checkpoint** (CORRECTIONS-J + CORRECTIONS-U):
>     compute residual SD of $|\Delta\ln\text{NotionalCost}^{USD}|$ after
>     partialling out $|\Delta\ln\text{Tokens}|$; Monte-Carlo measured power
>     at MDES = 0.40 residual-SD with current $T$. If power < 0.50, route to

Same ambiguity ("partialling out $|\Delta\ln\text{Tokens}|$" with no lag).
Also notable: §4 attaches this checkpoint to `01_data_eda.ipynb` (Task 11),
whereas §0.9 says the test-surface change is in `04_r4s3_usd_behavioral.ipynb`
(Task 14). The implication is that nb 01 already used contemporaneous (Task
11 EDA's 0.7115) and only nb 04 needs the dual-recipe diagnostic. That
allocation is defensible, but the spec doesn't say so explicitly. Two cheap
fixes (either is sufficient):

- Add forward-pointer at §4 line 1716 mirroring NIT-1.
- Or note in §0.9's "Test surface added" block that nb 01 (Task 11) used
  contemporaneous originally and does NOT require an update because it
  matches the canonical pin.

The second option closes the asymmetry-of-coverage question that a future
reviewer will otherwise raise.

**NIT-3: PARTIAL-* verdict labels defined only in §0.9 prose, not in §2.2.B
verdict-logic bullet list.**

§2.2.B's "Verdict logic (R4-S3-USD)" block (lines 1488-1498) enumerates:
- REJECT_NULL
- FAIL_TO_REJECT
- HALT

§0.9 introduces and uses **PARTIAL-FAIL_TO_REJECT** in the Task 14 verdict
re-evaluation (line 1264, "Under all three gates → **PARTIAL-FAIL_TO_REJECT**"),
defining it by example (gates A+B passed, gate C "N partial"). The status
frontmatter also refers loosely to "FAIL_TO_REJECT" without the PARTIAL-
prefix, while the revision-history row uses **PARTIAL-FAIL_TO_REJECT**.

Three concrete issues:

1. **No definition table.** A future implementer / reviewer cannot derive
   the PARTIAL-* taxonomy from §2.2.B alone. They have to know §0.9 exists.

2. **PARTIAL-REJECT is mentioned in the original review mandate (Q3) but
   does not appear anywhere in the spec.** Either the mandate is wrong
   about its current usage (true — `grep -n PARTIAL-REJECT` returns zero
   hits) and only PARTIAL-FAIL_TO_REJECT is defined; or PARTIAL-REJECT is
   the symmetric label intended for the REJECT_NULL side and the spec is
   incomplete. Either way: the verdict-logic table in §2.2.B should
   either (a) explicitly enumerate the PARTIAL-* variants and the gate-
   combinations that produce them, or (b) state that PARTIAL- is a
   prefix applied per §0.9 when the N gate is the only failing gate.

3. **Asymmetry across status fields.** The status frontmatter (line 5)
   reads "Task 14 verdict re-evaluation under pinned recipe becomes
   FAIL_TO_REJECT" while §0.9 body (line 1264) and the revision row
   (line 1931) say **PARTIAL-FAIL_TO_REJECT**. The frontmatter is
   weaker; readers comparing the two will note the inconsistency.
   Recommend tightening frontmatter to say "PARTIAL-FAIL_TO_REJECT
   (verdict partial pending N≥38)".

Suggested concrete fix: append one row to §2.2.B's verdict-logic table:

> - **PARTIAL-{REJECT_NULL,FAIL_TO_REJECT}** = all gates above except $N
>   \geq 38$ are met; verdict is the corresponding REJECT_NULL or
>   FAIL_TO_REJECT prefixed with PARTIAL- and remains partial until $N
>   \geq 38$ on a later refresh. The headline number is reported with
>   the partial tag; the verdict does not graduate to full until the N
>   gate clears.

**NIT-4: "MUST compute both" language is implicit, not explicit.**

§0.9 line 1245-1250 reads "Trio 4 power cell is amended to compute BOTH
recipes" — present-tense declarative is reasonably strong, and the verdict-
cell language ("evaluates the gate on the contemporaneous recipe ONLY")
implicitly mandates both being available. However, the anti-fishing case
benefits from one explicit MUST. Recommend tightening to:

> Trio 4 power cell **MUST** compute and report both recipes (contemporaneous
> and lagged) in adjacent cells; the verdict cell evaluates the gate on the
> contemporaneous recipe ONLY but the lagged number is required to be
> printed for diagnostic transparency.

This closes the wiggle-room a future maintainer might exploit ("I dropped
the lagged calc because it's noise") and aligns with §0.8's "REGIME-
CONDITIONAL with two required preconditions" mandatory-diagnostic pattern.

**NIT-5: §0.9 "Cross-references" bullet referring to its own outcome.**

Line 1284: "R4-S3-USD (PARTIAL-FAIL_TO_REJECT per §0.9)" inside §0.9's
own Cross-references bullet is technically self-referential. Reads as a
forward-reference to a section the reader is already inside. Cosmetic but
worth tightening to "(PARTIAL-FAIL_TO_REJECT per the verdict re-evaluation
above)" or simply dropping the "per §0.9" suffix.

**NIT-6: Status frontmatter spec_version-aware bump confirms hygiene.**

Frontmatter bump from `0.2.8` → `0.2.9` is correct. v0.2.8 explicitly
called out a catch-up frontmatter sync from v0.2.7 (where the bump was
missed). v0.2.9 does not repeat that lapse. **PRAISE for the discipline.**

### PRAISE

1. **Pre-emptive anti-fishing disclosure** (§0.9 lines 1232-1241). The
   "looks-like-result-chasing" paragraph names the threat by name, then
   defends with three orthogonal arguments (chronological precedent,
   first-principles, surfaced divergence). This is exactly the
   meta-honesty discipline that protects future-reviewer trust. Pair the
   transparency with NIT-4's explicit MUST and the chain is airtight.

2. **Variance-ratio precedent preserved** (Q7). §0.8 established the
   discipline of computing a diagnostic ratio
   (`var_ratio = var(abs_dln_trm) / var(abs_dln_cop_usd)`); §0.9 adds a
   second analogous diagnostic (power computed under both recipes).
   These are **additive disciplines** — both require a single notebook
   cell that prints a transparency-supporting number that is NOT
   verdict-graduating. No conflict. The pattern is converging into a
   reusable "diagnostic-only mandatory readout" idiom across the spec,
   which is excellent meta-design.

3. **Convergent-evidence framing** (lines 1281-1287). Four independent
   measurements (R5, Z-arms, R4-S3-COP, R4-S3-USD) are explicitly
   itemized as converging on the same conclusion. This is correct
   anti-fishing reasoning: weak evidence × multiple-independent-paths =
   stronger inference. The framing fends off the "you cherry-picked the
   reading that gave you the framework prior" criticism by anchoring on
   convergence, not on the one-arm result.

4. **Contract-only scope honored.** Diff is +106 / -2 in one file. No
   touches to §3.5, simulations/, scripts/, or jsonl_io. Implementation
   surface is genuinely "Task 14-bis = one notebook cell amendment".

5. **Numbers reconcile.** Spot-checked: residual SD 0.787 → power 0.7115;
   residual SD 1.156 → power 0.1745. The 0.40/SD ratio difference
   (0.508 vs 0.346) explains the power gap qualitatively. Headline
   α̂₁^USD = −18.12, p = 0.652 is preserved unchanged across patch.

---

## Per-question notes

### Q1 — Spec rigor (is "CONTEMPORANEOUS |Δln tokens|" unambiguous?)

**Mostly yes, but tightenable.** §0.9 lines 1198-1203 introduce the
contemporaneous-vs-lagged distinction with explicit index notation:
`|Δln tokens|_t` (contemporaneous) vs `|Δln tokens|_{t-LAG_PRIMARY}`
(lagged). The index `t` aligns with the index on `|Δln cost^USD|_t`
implicit in the R4-S3-USD specification (line 1454-1456). So "contemporaneous
of what" resolves cleanly: same-date `t` as the cost return being
partialled.

What's NOT pinned: whether `t` is the date of cost (`notional_cost_usd`
bucket date), date of tokens (token-count bucket date), or date of usage
event. In practice these are all the same by construction of the panel-
builder — both `notional_cost_usd` and `total_tokens` are bucketed on the
same weekday-UTC date in `simulations/dev_ai_cost_v2/panel.py`. So the
spec's `t` index inherits the panel's date-key by reference. This is not
a defect; it's a non-issue. But a future implementer who is unfamiliar
with the panel schema could conceivably misread.

**Recommendation (optional).** One sentence in §0.9 — e.g., "the contemporaneous
date `t` is the panel's weekday-UTC date-key shared by `notional_cost_usd`
and `total_tokens` columns" — would close this loophole. NIT-level, not
BLOCK.

### Q2 — Implementation surface (genuinely small?)

**Yes.** Confirmed by `git diff --stat`: 1 file, +106/-2 lines. The diff is:
- frontmatter `spec_version: 0.2.8 → 0.2.9`
- frontmatter `status:` rewrite
- new §0.9 section (lines 1188-1290 in current file)
- new §12 revision-history row

**Zero changes** to:
- `simulations/dev_ai_cost_v2/jsonl_io.py` — verified by diff scope
- `simulations/dev_ai_cost_v2/panel.py` — verified
- §3.5 component contracts — verified (no diff in that line range)
- §2.2.B Specification or Verdict logic blocks — verified (preserved verbatim
  per §0.9's own claim)

The "Task 14-bis" implementation surface is exactly one notebook
(`notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb`) gaining a Trio
4 power-cell modification + a markdown disclaimer cell. Per §0.9 line
1245-1256 this is the only test-surface change required.

Implementation-side caveat (out of contract-only scope but worth flagging):
the notebook update is **not yet implemented** (the spec patch is
uncommitted; the implementation work is separate). When the notebook PR
lands, a Code Reviewer pass on the implementation will verify (a) both
recipes are actually computed, (b) the verdict cell only uses
contemporaneous, (c) the markdown disclaimer is present per §0.9 line
1252-1256.

### Q3 — PARTIAL-* verdict labels (well-documented in §2.2.B?)

**Not well-documented in §2.2.B; only described by example in §0.9.** See
NIT-3 above for full discussion. Summary:

- Only `PARTIAL-FAIL_TO_REJECT` is actually used in the current spec
  (`grep -n PARTIAL-` finds 4 hits, all post-v0.2.9 and all
  `PARTIAL-FAIL_TO_REJECT`).
- `PARTIAL-REJECT` referenced in the review mandate does NOT appear in
  the spec text.
- §2.2.B verdict-logic block enumerates REJECT_NULL, FAIL_TO_REJECT, HALT
  but not the PARTIAL- variants.
- Status frontmatter says "FAIL_TO_REJECT"; §0.9 body and §12 row say
  "PARTIAL-FAIL_TO_REJECT". This inconsistency is not severe but
  reviewer-confusable.

**Recommendation:** add a verdict-table extension in §2.2.B per NIT-3 fix
snippet, and tighten frontmatter status to use PARTIAL-FAIL_TO_REJECT.

### Q4 — Diagnostic transparency requirement (MUST compute both?)

**Effectively yes, but the language is declarative-imperative rather than
MUST-imperative.** §0.9 line 1245-1250: "Trio 4 power cell **is amended to
compute BOTH recipes**" — present-passive imperative. The verdict cell's
"evaluates the gate on the contemporaneous recipe ONLY" implies both must
be visible.

This is enforceable in practice (a reviewer of the notebook PR can verify
both cells exist), but the spec language could be tighter. See NIT-4 for
the suggested MUST upgrade.

Anti-fishing-wise, the divergent number 0.17 IS surfaced in the spec
itself (line 1250 "expected power ≈ 0.17") AND in the §12 revision row
("under lagged-tokens partialling … 0.1745 < 0.50"). So the headline
disclosure exists at the spec layer regardless of notebook implementation.
A future reader cannot miss that the lagged-recipe reading exists and
disagrees with the canonical reading. **This satisfies the
anti-fishing-disclosure intent.**

### Q5 — Cross-references (correct?)

All verified by grep:

| Cross-ref | Location in §0.9 | Resolved? |
|---|---|---|
| CORRECTIONS-J | lines 1194, 1207, 1280 | YES — appears at §2.2.B line 1479, §4 line 1714, anti-fishing §7 line 1802/1819 |
| CORRECTIONS-S | lines 1266, 1273 | YES — §0.0 line 196, §2.2.B line 1453, §2.2.A line 1429, §4 line 1730 |
| CORRECTIONS-U | line 1227 | YES — §0.0 line 221, §2.2.B line 1479/1483, §4 line 1714, §7 line 1802 |
| CORRECTIONS-K | line 1273 | YES — §0.6 line 795, §2.4 line 1518, §7 line 1827 |
| §2.2.B | lines 1242, 1288 | YES — section header at line 1451 |
| §0.6 (Z-arms) | line 1282 | YES — §0.6 starts line 783 |
| §0.8 chain (R4-S3-COP regime-conditional) | line 1283-1284 | YES — §0.8 starts line 1084 |

**One observation (not a defect):** §0.9 does NOT cross-reference §2.2.B's
verdict-logic block when introducing PARTIAL-FAIL_TO_REJECT. This is the
gap NIT-3 flags. The label is invented in §0.9 prose without anchoring to
the existing §2.2.B taxonomy.

### Q6 — Documentation hygiene

- **§12 revision history entry (line 1931):** present, dated 2026-05-18,
  references §0.9, summarizes Task 14 outcome + the pin rationale + the
  PARTIAL- verdict re-evaluation. Length comparable to v0.2.6/v0.2.7/v0.2.8
  rows. PRAISE.

- **Frontmatter `spec_version` bump:** 0.2.8 → 0.2.9. Correct (NIT-6 above).

- **Status sentence length:** ~600 characters, single paragraph. Comparable
  to v0.2.7/v0.2.8 status sentences. Long but not unreasonable; reads like
  abstract+method+verdict in one shot. **APPROVE.**

- **One inconsistency** in frontmatter: says "FAIL_TO_REJECT" while body
  says "PARTIAL-FAIL_TO_REJECT". See NIT-3 issue 3.

- **No date drift in cross-refs**: 2026-05-18 used for the new revision
  row and §0.9 disposition trigger, matches today's date.

### Q7 — `var_ratio` precedent preservation (additive or conflicting?)

**Strictly additive.** Both §0.8 and §0.9 establish the same idiom:

- §0.8: compute `var_ratio = var(abs_dln_trm) / var(abs_dln_cop_usd)`
  in the notebook; if < 0.01 (plus additive-identity check) → reclassify
  CONSISTENCY-FAIL as REGIME-CONDITIONAL. The diagnostic ratio IS the
  reclassification gate.

- §0.9: compute power under both recipes (contemporaneous AND lagged); the
  verdict cell gates on contemporaneous ONLY but the lagged number is
  reported for transparency. The diagnostic ratio (well, the diagnostic
  pair) is NOT a gate — it's a transparency requirement.

These are different roles for the diagnostic: §0.8 uses it AS the gate
(when the headline test is unreliable), §0.9 uses it ALONGSIDE the gate
(to expose the spec-text ambiguity that produced the HALT). No conflict
— they are complementary tools in the same anti-fishing toolkit.

**Pattern emerging:** "mandatory diagnostic readout in the notebook"
appears now in §0.8 (var_ratio + additive identity) and §0.9 (both power
recipes). The spec is converging on this idiom and §0.9 honors §0.8's
precedent cleanly. PRAISE.

---

## Overall verdict

**APPROVE_WITH_NITS.**

The patch is sound on the four substantive axes (anti-fishing discipline,
implementation-surface containment, internal consistency, cross-ref
correctness). The defense-of-pin argument structure (chronological
precedent, first-principles, divergent-disclosure) is exactly what an
anti-fishing reviewer wants to see, and the variance-ratio precedent from
§0.8 is preserved as an additive (not conflicting) discipline.

Six NITs, all hygiene-level, none BLOCK:

- **NIT-1 (high impact, easy fix):** add §0.9 forward-pointer at §2.2.B
  line 1481 mirroring the §0.8 → §2.2.A precedent. Without it, future
  readers landing on §2.2.B re-derive the ambiguity that produced this
  patch.
- **NIT-2 (mid impact, easy fix):** same forward-pointer treatment at §4
  line 1716, or clarify in §0.9 why nb 01 doesn't need an update.
- **NIT-3 (mid impact, mid effort):** define PARTIAL-* verdict labels in
  the §2.2.B verdict-logic block; clarify PARTIAL-REJECT existence;
  reconcile frontmatter "FAIL_TO_REJECT" with body "PARTIAL-FAIL_TO_REJECT".
- **NIT-4 (low impact, trivial fix):** upgrade "is amended to compute BOTH"
  to explicit MUST language.
- **NIT-5 (cosmetic):** drop the self-reference "per §0.9" inside §0.9's
  own cross-refs.
- **NIT-6 (no fix needed):** PRAISE for frontmatter discipline.

**Recommendation:** land NIT-1 + NIT-3 (issue 3, frontmatter consistency)
before commit; NIT-2 + NIT-3 (issue 1+2) + NIT-4 + NIT-5 can land in a
small followup commit or with v0.2.10 if any. None block the v0.2.9
patch from being committed and the Task 14-bis notebook update from
being implemented.

---

## Files referenced

- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` (spec under review; §0.9 at lines 1188-1290, §2.2.B at 1451-1498, §0.8 at 1084-1186, §12 row at 1931)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb` (Task 14 impl target — not yet updated; outside contract-only scope)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/01_data_eda.ipynb` (Task 11 EDA, source of canonical contemporaneous-tokens power 0.7115)
