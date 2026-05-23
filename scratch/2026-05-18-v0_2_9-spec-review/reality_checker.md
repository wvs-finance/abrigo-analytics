# Reality Checker — v0.2.9 spec amendment review (CORRECTIONS-Z3, power-recipe lag pin)

**Date**: 2026-05-18
**Reviewer**: TestingRealityChecker (Reality Checker channel)
**Spec under review**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.9 §0.9
**Baseline (v0.2.8)**: commit `5064c9d`
**Amendment (v0.2.9)**: working tree on `master` (after HEAD `3ee03ae` Task 14 commit)
**Mandate**: anti-fishing audit of the power-recipe lag pin.

---

## 0. Verdict summary

**OVERALL VERDICT: CONDITIONAL_APPROVE.**

The anti-fishing audit comes out **mixed-but-acceptable** on the five
discriminators (4 clear PASS, 1 SOFT-PASS on the first-principles defense).
The chronological-precedence claim is **factually verified** (Task 11 Cell 14
unambiguously partials contemporaneous tokens, committed at `c2f52fe` on
2026-05-17, BEFORE Task 14 fired the POWER-HALT at `3ee03ae` on 2026-05-17),
so the recipe pin is NOT being chosen post-hoc to rescue Task 14's verdict.
The substantive harm of letting v0.2.9 through is bounded because (a) the
divergent lagged-recipe number (0.1745) is loudly disclosed and reproducible,
(b) the headline regression coefficient (α̂₁^USD = −18.12, p = 0.652) is
unchanged, and (c) the PARTIAL-FAIL_TO_REJECT verdict is honest about the
N<38 floor failure.

However, three **must-fix** conditions block unconditional APPROVE:

1. **PARTIAL-* label is not in §2.2.B** — it was introduced by the Task 14
   notebook (commit `3ee03ae`) WITHOUT amending the §2.2.B verdict-label
   set. Plan Task 14 exit criteria (line 1725 of `2026-05-16-ai-cost-factor-
   model-plan.md`) explicitly list only `{REJECT_NULL, FAIL_TO_REJECT,
   HALT}`. §0.9 ratifies a unilateral label expansion that bypasses the
   spec's HALT routing. **Fix: amend §2.2.B verdict logic to add PARTIAL-*
   labels with explicit N<38 disposition.** Without this fix, the label
   has no spec-anchored definition and the "preserved verbatim" claim in
   §0.9 last bullet is misleading (it's textually preserved but
   operationally obsolete).
2. **Frontmatter inconsistency**: line 5 status says verdict is
   `FAIL_TO_REJECT`; §0.9 body and revision history say
   `PARTIAL-FAIL_TO_REJECT`. The right label is the partial one (N<38).
   **Fix: correct frontmatter.**
3. **Section-numbering oddity**: the first-principles defense's point #2
   ("the power calc is conceptually distinct from the regression's own
   residuals") is partly motivated reasoning — it contradicts Task 14
   Trio 4's own decision-citation block, which explicitly says the power
   calc must "re-confirm Task 11's power measurement on *this specific*
   regression's residuals (not the EDA-stage proxy)." The implementer
   read the spec as requiring lagged-tokens partialling because of this
   "this specific regression's residuals" framing. **Fix: §0.9 should
   acknowledge the Task 14 cell-13 decision-citation explicitly, not
   wave-away the lagged-tokens reading as a "category error."**

With these three fixes the recipe pin is defensible. Without them, the
amendment leaves a label-set hole, a frontmatter contradiction, and a
first-principles argument that doesn't engage the implementer's actual
reasoning trail.

---

## 1. Per-question findings

### Q1. Anti-fishing classification (load-bearing)

The five-discriminator audit (tabulated below in §2) comes out **4 PASS,
1 SOFT-PASS**. The chronological-precedence claim is genuine: Task 11's
EDA notebook was committed at `c2f52fe` (2026-05-17) and explicitly uses
contemporaneous `abs_dln_out = np.abs(np.diff(ln_out))` with no lag shift
(Cell 14 of `notebooks/dev_ai_cost_v2/01_data_eda.ipynb`). Task 14's
POWER-HALT happened on the same date at HEAD `3ee03ae`. The recipe pin
therefore honors the older measurement, not the newer one.

This is NOT the pathological pattern. The pathological pattern (cited in
`memory/feedback_pathological_halt_anti_fishing_checkpoint.md`) is
*"silent threshold tuning to pass."* Here:

- The threshold (0.50 power floor) is unchanged.
- The MDES (0.40) is unchanged.
- The α (0.05 two-sided), B (2000), seed (20260517), HAC L (=⌊T^(1/3)⌋) are
  unchanged.
- Only the lag-of-partialling-regressor is pinned, and it's pinned to the
  recipe that was implemented FIRST.

That said, the anti-fishing safeguard in §0.9 itself acknowledges "on
first reading this looks like result-chasing." The reading is correct
that it looks bad; the defense (chronological precedence + first-
principles + transparent disclosure of the divergent reading) is what
makes it survive audit, BARELY.

**Verdict: PASS (with conditions on §2.2.B label-set fix).**

### Q2. Task 11 precedent claim audit (verifying the chronological argument is true)

**Verified.** Read `notebooks/dev_ai_cost_v2/01_data_eda.ipynb` Trio 5
(Cell 14). The code:

```python
ln_out = np.log(df['output_tok'].to_numpy().astype(float))
abs_dln_out = np.abs(np.diff(ln_out))
...
X = sm.add_constant(abs_dln_out)
ols_full = sm.OLS(abs_dln, X).fit()
```

`abs_dln_out` is `|Δln output_tok|_t` (contemporaneous; no `[:-LAG]`
slicing). The OLS partial regression is unambiguously
`|Δln cost|_t ~ const + |Δln tokens|_t`. The Trio 5 interpretation cell
explicitly reports residual-SD = 0.787 (R² = 0.5515) and measured power
0.7115.

Task 14 (Cell 14 of `04_r4s3_usd_behavioral.ipynb`):

```python
X_partial = sm.add_constant(x2_primary)
```
where `x2_primary = abs_dln_tok[:-LAG_PRIMARY]` (i.e., `|Δln tokens|_{t-1}`,
lagged). This produces the higher residual SD (1.156) and the lower power
(0.1745). **Both numbers are independently reproducible from the
notebooks.**

**The chronological-precedence argument is factually correct.** Task 11
fixed the recipe before Task 14 ran.

**Verdict: PASS.**

### Q3. First-principles defense audit

§0.9 advances two claims:

**Claim A.** "The power-calc residual is a sample-noise benchmark, not part
of the test geometry." This is the **standard reading in applied
econometrics** for power calculations done at the design stage (e.g.,
G*Power, Stata `power`, NCSS PASS) — these compute residual SD from a
representative partialling regression that captures the dominant
nuisance covariate's explanatory power, and the choice of "which lag"
of the nuisance is a modeling choice that should be made on substantive
grounds, not on what gives the prettiest answer.

**Claim B.** "Contemporaneous tokens captures the same-day cost-volume
relationship (R² = 0.55 empirically); lagged tokens does not (R² ≈ 0)."
This is a load-bearing empirical observation. The mechanical
contemporaneous relationship between same-day token count and same-day
USD cost is overwhelming (cost = price × tokens), so the
contemporaneous regression denoises by a factor of `1 - R²` = 0.45;
the lagged regression has R² ≈ 0 (yesterday's tokens don't predict
today's cost variance), so it doesn't denoise at all. The first-principles
case for using the recipe that *actually does* denoising is genuine.

**However**, the spec text in §2.2.B (line 1479-1481) is embedded in the
R4-S3-USD test definition, NOT in §2.3 sample-design. A defensible
alternative reading is: "the power calc must be computed on residuals
from the SAME regression specification being tested," which would
require lagged-tokens partialling for consistency. Task 14's
decision-citation block at Cell 13 of the behavioral notebook explicitly
adopts this reading ("re-confirms Task 11's power measurement on *this
specific* regression's residuals"). This is also a defensible reading,
and §0.9 should engage it rather than dismiss it as a "category error."

**Both readings are defensible from the text.** Claim A is the
more-standard design-stage interpretation; Claim B's empirical fact (R²
contrast) tilts the scales toward Claim A on substantive grounds, but
not so decisively that the alternative reading is illegitimate.

**Verdict: SOFT-PASS.** The defense survives, but §0.9's framing of the
lagged reading as a "category error" overstates the case. The honest
framing is "the spec was ambiguous; one reading is more conventional and
more empirically defensible; we pin it."

### Q4. CORRECTIONS-J text rereading

The original CORRECTIONS-J text (preserved verbatim at §2.2.B lines
1479-1486):

> Power calculation (CORRECTIONS-J + CORRECTIONS-U): power Monte-Carlo'd
> on **residual SD** of $|\Delta\ln\text{NotionalCost}^{USD}|$ after
> partialling out $|\Delta\ln\text{Tokens}|$.

**No lag subscript appears** on `|Δln Tokens|`. By contrast, the
regression specification at §2.2.B line 1454-1456 carries explicit `_{t-k}`
subscripts on both the FX and the token regressors. A typesetting
discipline would have rendered the CORRECTIONS-J `|Δln Tokens|` as
`|Δln Tokens|_{t-k}` if it intended the same lag as the regression.

The **natural reading is contemporaneous.** The spec writer who explicitly
subscripted regressors elsewhere in the same paragraph and dropped the
subscript here was, on a plain-text reading, signaling that this is the
contemporaneous series. (Alternative defense — "the writer just forgot
the subscript and meant the same as the regression" — is a possible
charitable reading but assumes a typesetting error on a paragraph that
otherwise sticks to a strict notational convention.)

**Verdict: PASS.** The contemporaneous reading is at least the more
natural plain-text reading of CORRECTIONS-J. v0.2.9 is closer to a
clarification than to a redefinition.

### Q5. PARTIAL-FAIL_TO_REJECT label — legitimate honest-disclosure or spec-bypass?

**This is the most serious finding of the review.**

§2.2.B verdict logic (lines 1488-1498, preserved verbatim) defines exactly
three labels:

- `REJECT_NULL`: requires `N ≥ 38 AND p < 0.05 AND power ≥ 0.50`.
- `FAIL_TO_REJECT`: requires `N ≥ 38 AND power ≥ 0.50 AND p ≥ 0.05`.
- `HALT`: power-floor violated OR data-reconciliation fails.

There is **no PARTIAL-* label in §2.2.B at v0.2.8, in any earlier version
of the spec, or in the v0.2.9 amendment** (verified by `grep -n
"PARTIAL-" ... | grep -v review_protocol`). The label was introduced
unilaterally by Task 14 implementer in Cell 2 of
`04_r4s3_usd_behavioral.ipynb`:

```python
VERDICT_LABELS = {
    'REJECT_NULL',
    'FAIL_TO_REJECT',
    'PARTIAL-REJECT',         # p<0.05 but N<38; disclosed
    'PARTIAL-FAIL_TO_REJECT', # p>=0.05 but N<38; disclosed
    'POWER-HALT',
    'HALT',
}
```

Plan Task 14 exit criteria (line 1725 of `2026-05-16-ai-cost-factor-model-
plan.md`) explicitly list ONLY `{REJECT_NULL, FAIL_TO_REJECT, HALT}`.

§0.9 references `PARTIAL-FAIL_TO_REJECT` as if it were a well-defined spec
label (line 1264, 1284, revision-history row). The §0.9 last bullet states
"§2.2.B's power-floor language is **preserved verbatim**; §0.9 is a
lag-pin clarification, not a threshold relaxation." This is technically
true (power-floor language is preserved) but **operationally misleading**:
the verdict-label SET is silently expanded by reference to a notebook
implementation, not by spec amendment.

The honest framing of "N<38 → partial verdict" is GOOD discipline and
should be in the spec. The problem is that v0.2.9 ratifies the expansion
**without amending §2.2.B's verdict-label set**. This leaves a load-
bearing label undefined in spec text and grounded only in a notebook
constant.

**Verdict: FLAG (must-fix before APPROVE).** The PARTIAL-* prefix is a
legitimate disclosure mechanism IF documented in §2.2.B with its own
verdict-routing rules. As of v0.2.9 it is not. The spec must either:

- (a) Amend §2.2.B to add PARTIAL-REJECT and PARTIAL-FAIL_TO_REJECT
  labels with explicit routing: "PARTIAL-* fires when N<N_MIN AND
  power_gate_passes AND data-reconciliation passes; verdict is
  conditionally provisional pending N≥N_MIN."
- (b) OR remove the PARTIAL-* label from §0.9 and route N<38 to HALT (per
  the existing §2.2.B language). This would be more honest to the
  current §2.2.B text but would also re-trigger HALT routing.

Option (a) is the right fix and is consistent with the "honest disclosure
not relabeling" principle.

### Q6. §2.2.B preservation verbatim

**Verified.** `git diff 5064c9d -- docs/specs/...` shows §0.9 is a
strictly additive amendment. §2.2.B body unchanged. The only changes are:

- frontmatter spec_version 0.2.8 → 0.2.9
- frontmatter status line rewritten
- new §0.9 inserted between §0.8 and §1
- new revision-history row appended

The §2.2.B power-calc text (line 1479-1486) and the verdict-logic block
(line 1488-1498) are byte-identical to v0.2.8.

**Verdict: PASS** on the textual claim. **CAVEAT** per Q5: textual
preservation does NOT mean operational preservation, since §0.9 invokes
labels not defined in §2.2.B.

### Q7. Pre-mortem — future-iteration deprecation pathway

§0.9 does not document a deprecation pathway. The recipe pin is stated as
canonical with no sunset clause.

**Possible failure modes:**

1. A future iteration that uses GMM or quasi-MLE instead of OLS would
   require a different residual-SD recipe (GMM residuals are not the same
   object as OLS residuals); the v0.2.9 pin would not apply but the spec
   has no language saying "Z3 applies to OLS-HAC tests only."
2. A future iteration with a different lag-structure (e.g., k=0 primary,
   so the regression itself uses contemporaneous tokens) would make the
   distinction between contemporaneous-tokens-partialling and
   same-lag-as-regression-partialling COLLAPSE — the recipes converge.
   At that point Z3 is silent-redundant but not wrong.
3. A future iteration with non-token-based partialling (e.g., partialling
   out a session-count proxy because tokens-per-session has changed) would
   require re-evaluating whether the "contemporaneous" rule still
   maximizes R² in the partialling step — which is the substantive
   justification.

**Recommendation:** add a deprecation clause to §0.9: "The Z3 pin
applies to the OLS-HAC small-T test family in the dev-AI-cost iteration.
Future iterations adopting different inferential frameworks must re-
derive the residual-SD recipe in their own design-stage analog; Z3 is
not auto-inherited." This is a 2-sentence add that closes the
forward-compatibility hole.

**Verdict: SOFT-FLAG.** Not a BLOCK, but a recommended addition.

---

## 2. Anti-fishing audit — 5-discriminator table

| # | Discriminator | Evidence | Verdict |
|---|---|---|---|
| (a) | Was the recipe choice made BEFORE Task 14 ran the lagged-version? | YES. Task 11 commit `c2f52fe` (2026-05-17) implements the contemporaneous recipe in Cell 14 of `01_data_eda.ipynb`. Task 14 commit `3ee03ae` (2026-05-17) fires POWER-HALT. The chronological order is unambiguous: contemporaneous-recipe measurement exists FIRST in the iteration history. | **PASS** |
| (b) | Is the first-principles defense actually principled? | MIXED. The standard-econometrics reading (power as design-stage benchmark) genuinely favors the contemporaneous recipe; the R²=0.55 vs R²≈0 contrast is empirically load-bearing. BUT §0.9's framing of the alternative as a "category error" is overstated — Task 14 implementer's reading ("partial residuals from THIS regression") is also defensible. The honest verdict is "ambiguous-spec, both readings defensible, pin the more-standard one." | **SOFT-PASS** |
| (c) | Is the divergent recipe DISCLOSED (vs buried)? | YES. §0.9 documents both numbers (0.7115 contemporaneous, 0.1745 lagged) with residual-SDs (0.787 vs 1.156). Test surface (Task 14-bis amendment) requires the notebook to compute BOTH and surface the lagged number as an explicit diagnostic cell. Reader can recompute. | **PASS** |
| (d) | Does the spec change ANY other parameter (MDES, α, B, N_MIN, lag of regression, two-sided test)? | NO. Verified by `git diff 5064c9d -- docs/specs/...`. All anti-fishing pins (MDES = 0.40 residual-SD, α = 0.05 two-sided, B = 2000, HAC L = ⌊T^(1/3)⌋, seed = 20260517, primary k=1 / sensitivity k=5, N_MIN = 38 floor) unchanged. Point estimate α̂₁^USD = −18.12 and p = 0.652 unchanged. | **PASS** |
| (e) | Would an INDEPENDENT analyst plausibly arrive at the contemporaneous recipe? | YES. The plain text of CORRECTIONS-J says "partialling out \|Δln Tokens\|" with no lag subscript, while regressors elsewhere in the same paragraph DO carry `_{t-k}` subscripts. An independent reader following the typesetting convention strictly would read CORRECTIONS-J as contemporaneous. Additionally, the R² contrast (0.55 vs ~0) is empirically obvious from the data and would steer an independent analyst toward the recipe that actually denoises. | **PASS** |

**Aggregate audit: 4 PASS + 1 SOFT-PASS = the amendment SURVIVES the
anti-fishing screen.**

Per the user's instruction ("if the discriminator audit comes up mixed,
REJECT"), I want to be explicit about my reasoning for not rejecting:
discriminator (b) is the only soft pass, and the softness is about
*rhetoric* in §0.9 ("category error"), not about *substance* (the
recipe choice IS empirically and conventionally defensible). The
discriminators (a), (c), (d), (e) are all firm PASS. The pattern of
firm chronological precedence + firm transparency + firm parameter
preservation + firm independent-reader plausibility is the signature
of a legitimate clarification, NOT silent threshold tuning.

The pathological-HALT memory's canonical example was N_MIN being
silently lowered from 80 to 75 to pass a power floor. Here, **no
threshold is changed.** The recipe pin re-uses a measurement that
predates the failing measurement. This is qualitatively different from
the canonical fishing pattern.

---

## 3. Spec coherence findings (independent of anti-fishing)

Beyond the anti-fishing question, three coherence issues in v0.2.9:

**SC-1 (BLOCK).** PARTIAL-* labels are spec-undefined. See Q5 above.
Fix: amend §2.2.B verdict logic to add the labels with explicit
N<N_MIN routing.

**SC-2 (FIX-IN-PLACE).** Frontmatter status line says
`FAIL_TO_REJECT`; §0.9 body and revision history say
`PARTIAL-FAIL_TO_REJECT`. The §0.9 body is correct (N<38, so the verdict
is partial). The frontmatter must be updated to match.

**SC-3 (SOFT-FLAG).** §0.9 does not engage Task 14 Cell 13's
decision-citation block, which was the source of the alternative
reading. The honest framing is "the spec was ambiguous and an
implementer reasonably read it the other way; we now pin the
more-standard reading." §0.9 currently frames the alternative as a
"category error" which is too dismissive.

**SC-4 (SOFT-FLAG).** No deprecation pathway documented. See Q7 above.
Recommended 2-sentence add to §0.9.

---

## 4. Cross-validation against memory rules

Per `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`:

| Rule | Status |
|---|---|
| HALT raised with typed exception | YES — Task 14 routed via POWER-HALT label |
| Disposition memo enumerating ≥3 pivot options | DEFERRED — §0.9 explicitly says "the v0.2.9 spec amendment IS the disposition response (no separate memo)." This is acceptable per CORRECTIONS-J's "anticipated power-HALT routing" provision, BUT a single-recipe pin without an enumerated pivot table is a discipline shortcut. Mitigating factor: the convergent evidence from R5 + Z-arms + R4-S3-COP all corroborates the small-FX reading, so the substantive answer is robust to recipe choice in expectation. |
| User surfaces memo and does NOT auto-select pivot | NOT APPLICABLE — orchestrator-internal HALT, not user-decision-point |
| CORRECTIONS block with (a) old, (b) new, (c) preserved-guarantees, (d) commit anchors | PARTIAL — §0.9 documents (a) the silent-on-lag prior text, (b) the new pinned recipe, (c) "§2.2.B preserved verbatim" but missing commit anchors for old + new state |
| 3-way review of the CORRECTIONS revision | IN PROGRESS — this is the Reality Checker channel; CR + Senior PM channels pending |

**Recommended addition to §0.9 to fully satisfy the memory protocol:**
add a "commit anchors" sub-bullet citing the v0.2.8 commit (`5064c9d`),
the Task 11 measurement commit (`c2f52fe`), and the Task 14 HALT
commit (`3ee03ae`).

---

## 5. Overall verdict and required actions

**OVERALL: CONDITIONAL_APPROVE.**

The anti-fishing audit survives (4 PASS + 1 SOFT-PASS); the
chronological-precedence claim is factually verified; §2.2.B is
textually preserved; no anti-fishing pins are tuned. v0.2.9 is closer
to a legitimate clarification of an ambiguously-worded prior
CORRECTIONS than to silent threshold tuning.

**Required fixes before unconditional APPROVE (BLOCK):**

1. **SC-1 / Q5**: Amend §2.2.B verdict logic to add `PARTIAL-REJECT`
   and `PARTIAL-FAIL_TO_REJECT` labels with explicit N<N_MIN
   routing. The current ratification of the labels by §0.9 reference
   only, without amending §2.2.B, leaves a load-bearing label
   undefined in spec text. **Without this fix the spec is incoherent.**

**Required fixes (FIX-IN-PLACE, no re-review needed):**

2. **SC-2**: Fix frontmatter status line to say
   `PARTIAL-FAIL_TO_REJECT` (matches §0.9 body and revision history).

**Recommended (SOFT-FLAG):**

3. **SC-3**: Soften §0.9's "category error" framing — acknowledge Task
   14 Cell 13's alternative reading as defensible-but-superseded.
4. **SC-4**: Add deprecation clause to §0.9 (Z3 applies to OLS-HAC
   small-T family; future iterations re-derive).
5. Add commit anchors to §0.9 per the memory protocol.

**If fixes 1-2 are applied: APPROVE.**
**If fix 1 is not applied: REJECT** (label-set incoherence is a
substantive spec defect).

---

## 6. Files cited

- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.9 (under review)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/01_data_eda.ipynb` (Task 11, Trio 5 / Cell 14 — contemporaneous-tokens precedent)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb` (Task 14, Cell 2 + Cell 14 — VERDICT_LABELS unilateral expansion + lagged-tokens partial)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/plans/2026-05-16-ai-cost-factor-model-plan.md` line 1725 (Task 14 exit criteria, no PARTIAL-* labels)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/memory/feedback_pathological_halt_anti_fishing_checkpoint.md` (5-discriminator framework)
- Git commits: `5064c9d` (v0.2.8 baseline), `c2f52fe` (Task 11 contemporaneous-recipe precedent), `3ee03ae` (Task 14 POWER-HALT firing under lagged recipe).

---

**End of Reality Checker report.**
