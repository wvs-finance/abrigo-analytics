# Wave-2 Code Reviewer Report — v0.2.6 CORRECTIONS-Z Spec Amendment

- **Spec**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.6 §0.6
- **Channel**: Code Reviewer (parallel to Reality Checker spec-compliance review)
- **Branch / HEAD**: `master` @ `fa77c8f` (post-Task-12)
- **Reviewer mode**: contract-only diff review; no implementation patch on disk yet
  (proposed: `notebooks/dev_ai_cost_v2/06_z_sensitivity.ipynb`)
- **Date**: 2026-05-17

---

## TL;DR verdict

**APPROVE_WITH_NITS.** The amendment is well-formed, pre-registers all
parameters the implementer needs, threads anti-fishing invariants forward
correctly (Z-arms are diagnostic-only per CORRECTIONS-K; the R5 PRIMARY
verdict stays on daily real data), and pins a numerically explicit Z-3
escalation gate before any backcast is touched. No BLOCKs.

Three NITs are worth folding into v0.2.6 directly (no re-review needed):
- N-1: monthly-stratum N-floor language could be marginally tightened
  ("record but disclose" → "report MUST be flagged 'CI uninformative, do
  not interpret the point estimate'").
- N-2: weekly-bucket edge case (1-observation week) needs an explicit
  one-line rule. The spec leaves it implicit.
- N-3: §2.4 sensitivity-arms table is silent on Z-arms; a one-line forward
  reference to §0.6 would prevent future readers from missing them.

The user-raised concerns about §3.5 / §2.4 stale tables, backcast
re-anchoring, OR-vs-AND threshold semantics, and notebook splitting are
addressed individually below; none rise to BLOCK.

---

## Per-question review

### Q1. Specification rigor — bootstrap parameters pinned?

**Verdict: PASS.** All bootstrap parameters are pinned in the spec text
itself (not deferred to plan or code). Concretely:

- **B (Z-1)**: explicitly `B=10,000` per stratum, three distinct seeds
  (20260516 daily, 20260517 weekly, 20260518 monthly) — table at lines
  806-808.
- **block_len (Z-1)**: pinned as `⌈T^(1/3)⌉` formulaically, with the
  numeric instantiation written out (`4` daily, `2-3` weekly, N/A monthly).
- **method**: "stationary bootstrap" named for Z-2 (line 839); Z-1
  inherits "stationary-bootstrap (Politis-Romano)" from §4
  `02_r5_descriptive.ipynb` (line 1312-1314). The §0.6 patch does NOT
  re-state the method per stratum — minor ambiguity but resolvable from
  context.
- **B_paths (Z-2)**: pinned `B_paths = 1,000` (line 846), seed `20260519`,
  block_len `4` matching daily (line 850).
- **CI level**: 90% across the board (consistent with §2.1 R5 contract).
- **cov-rule**: explicit reference to CORRECTIONS-Q ("conservative cov
  rule" / "cov reported separately"), lines 816, 850.

A truly nitpicky implementer could ask "is the Z-1 method also stationary
bootstrap, or could it be circular block?" — but the inheritance from §2.1
R5 is unambiguous in context. **No BLOCK.** Optional NIT: one inline word
"stationary" in the Z-1 row would remove the round-trip.

### Q2. Aggregation rule pinning — sum(cost) + mean(TRM)

**Verdict: SUFFICIENT, with one NIT.** The user's question is right to
flag this. Three observations:

1. The spec explicitly defers volume-weighting: "volume-weighted in code,
   simple-mean in this v0.2.6 — keep simple per scope" (line 813). That's
   a defensible scope cut and the *defer* is itself documented, which is
   what the audit-pass cares about.
2. The bucket goal here is "representative TRM for the bucket" — but the
   v0.2.6 simple-mean choice is fine *because* the analysis re-takes
   `Δln(bucket_mean_TRM)` and feeds that into the variance decomposition.
   If the bucket has a single FX shock concentrated on a high-cost day,
   simple-mean attenuates it; volume-weighted mean would preserve it.
   That's a *known* attenuation and it pushes the Z-1 result CONSERVATIVE
   relative to volume-weighted (i.e., understates the FX share if a
   regime artifact exists). Conservative direction = anti-fishing safe.
3. NIT: the spec should add one half-sentence acknowledging the
   conservative direction of the simple-mean choice, so a future reader
   doesn't read it as a hidden degree of freedom.

**Recommendation**: add to line 813: "...keep simple per scope; this is
conservative against the FX-share signal (simple-mean attenuates
high-cost-day FX shocks relative to volume-weighting)."

### Q3. Bucket-construction edge cases — 1-observation week

**Verdict: NIT — needs one-line pin.** The user's read is correct. As
written ("ISO week containing ≥1 observation"), the spec does not
disambiguate between:
- (a) the week is INCLUDED as a 1-day aggregate (sum-of-one = the value,
  log-diff against prior week's similarly-shaped sum); or
- (b) the week is DROPPED (T reduced by 1).

For weekly with T~8-12 and block_len 2-3, a 1-day week is a *legitimate*
observation under interpretation (a) and only mildly distorts the
distribution. Under (b) you lose a degree of freedom that you cannot
afford at T~8-12.

The amendment should pin this. **Recommendation**: add to the weekly
row: "weeks with a single observation day are INCLUDED as a 1-day
aggregate (sum-of-one); first-diffed against the prior week's bucket
sum." Same convention for monthly. This is the conservative-against-fishing
choice (no post-hoc deletion of inconvenient weeks).

### Q4. Backcast starting value & drift / re-anchoring

**Verdict: PASS with NIT.** The user is correct that an exponential
random walk from a single anchor can drift far from realistic levels
over 520 days. Three reasons this is OK as currently specified, and one
mitigation worth pinning:

1. The Z-2 metric is the **variance decomposition of Δln series**, not
   the level itself. Drift in the level does not bias the variance
   decomposition because `Var(Δln cost^COP) = Var(Δln cost^USD) +
   Var(Δln TRM) + 2 Cov(...)` is level-invariant under multiplicative
   construction. So the absolute drift of `cost^USD_t` over 520 days is
   not a threat to the headline statistic Z-2 reports.
2. The starting `cost^USD_0 = median observed daily cost` is innocuous
   for the *variance* statistic for the same reason — it sets a level
   but does not affect first differences.
3. Where drift *could* bias things is if cost^COP_t × TRM_t multiplication
   creates regime-dependent variance (e.g., heteroscedasticity that the
   first-differencing doesn't fully tame). But Z-2's whole point is to
   pick up exactly that interaction.
4. **NIT** (defensive): add one explanatory sentence noting that
   re-anchoring is *intentionally not* applied because the headline
   statistic is variance-of-Δln (level-invariant), and re-anchoring would
   introduce a discontinuity in Δln_t at re-anchor boundaries that would
   contaminate the FX-share estimate. Pinning the *non-decision* defuses
   the natural reviewer question.

### Q5. Numeric thresholds in Z-3 — OR vs AND

**Verdict: OR is correct as written; document the rationale.**

The user asks whether "≥ 5× daily baseline OR ≥ 0.05 absolute" should be
AND (stricter). The two thresholds are designed to handle a degenerate
boundary case:

- **5× daily baseline** of 0.00003 = 0.00015. That's still essentially
  zero in any practical sense. If Z-2 returns 0.00015 you have "5x a
  microscopic number" — formally satisfies the relative threshold but is
  noise.
- **0.05 absolute** is the substantively meaningful floor (5% of total
  variance attributable to FX).

OR is the **correct logical connector** because either condition
separately is sufficient to disqualify the lightweight backcast:
- Pure relative trigger (`5×` only) catches "FX moved from noise to
  signal proportionally" even at small absolute levels.
- Pure absolute trigger (`0.05` only) catches "FX share is materially
  large in dollar terms" regardless of the daily baseline.

AND would require BOTH — meaning a regime where FX share jumped from
0.00003 to 0.04 (1,333× increase but still under 0.05 absolute) would
NOT escalate. That would be a false negative for the escalation gate's
purpose.

**No BLOCK.** Optional NIT: add a one-line rationale to §0.6 line 854
explaining why OR (not AND) — pre-empts the same reviewer question on
future cycles. Suggested: "OR (not AND) because either a large relative
jump from the baseline OR a substantively material absolute share is
independently sufficient to invalidate the lightweight backcast's
assumptions."

### Q6. Single notebook vs multi-notebook

**Verdict: SINGLE NOTEBOOK IS DEFENSIBLE; document the trio map.**

The user asks whether 9 trios in one notebook violates trio-discipline
reviewability. Counter-arguments for keeping it as one notebook:

1. **Shared anti-fishing cell**: all pins (seeds, B, block_len,
   thresholds) live in cell 2 per the spec (line 878). Splitting would
   either duplicate that cell (drift risk) or import from a shared module
   (extra coupling).
2. **Single HALT-or-CONTINUE routing decision**: Z-3 escalation gate is
   the terminal cell of the notebook (line 875). Splitting Z-1 and Z-2
   into separate notebooks means the routing decision lives in a third
   notebook or is duplicated.
3. **Trio-discipline does NOT cap trios per notebook**; it requires each
   trio to be a HALT-checkpoint. 9 trios in one notebook is fine if each
   trio has the discipline.

Counter for splitting:
- Review effort scales with notebook length; 9 trios + decision-citation
  blocks each is roughly 30-40 cells. That's at the upper end of
  reviewable in one sitting.

**Recommendation (NIT, not BLOCK)**: keep single notebook BUT pin in §0.6
that the notebook's table of contents (cell 1) MUST list the 9 trios in
the form `Z-1.daily / Z-1.weekly / Z-1.monthly / Z-2.setup /
Z-2.resample / Z-2.decompose / Z-3.gate-check / Z-3.escalation-decision
/ Z-3.disposition`. Explicit TOC makes per-trio review tractable.

### Q7. Memory / runtime risk — Z-2 path × token × ts

**Verdict: PASS with NIT on streaming.** The user's math is right but
the sizing is small in absolute terms.

- 1,000 paths × 520 weekdays × (4 token classes + cost + TRM) = 520
  weekdays × 6 series × 1,000 = 3.12M float64 cells = ~25 MB if
  materialized.
- If kept as 1,000 × 520 = 520k cells per series at float64 = ~4 MB per
  series. Trivial.
- The *variance decomposition per path* (the actual statistic) is 6
  scalars × 1,000 paths = 6,000 floats = 48 KB.

So the full materialization is ~25 MB worst case. **No memory threat.**
Runtime: 1,000 × 520 stationary-bootstrap draws is order-of-seconds in
NumPy on the daily pool of 28 values. **No runtime threat.**

**NIT**: the spec should pin that **only the per-path variance-decomposition
scalars are persisted to disk** (the 6,000-float summary), not the 25 MB
path matrix. This is implicit but worth one line so the implementer
doesn't dump everything to parquet "for completeness".

**Recommendation**: add to line 851: "Persisted output: per-path
(B_paths × 4) summary table `(fx_var, usage_var, cov, fx_share)` —
~32 KB. Full path matrices are computed in-memory and discarded; do not
write the (B_paths × 520 × series) tensor to disk."

### Q8. §3.5 / §2.4 cross-reference hygiene

**Verdict: NIT — one-line forward ref in §2.4 is sufficient.**

The user is right that:
- §3.5 (component contracts) is NOT updated by this amendment, and that
  is **correct** — the Z-arms produce notebook-level outputs only; no
  new typed contracts cross the module boundary into `simulations/`.
  Leaving §3.5 unchanged is the right call.
- §2.4 (sensitivity arms table) IS arguably stale. The four arms listed
  (lag k=5, model-fixed subset, regime split, outlier-trimmed) are the
  R4-S3 sensitivity arms from v0.2.0. The Z-arms are *also* sensitivity
  arms but live in §0.6 instead of §2.4. A new reader scanning the spec
  TOC for sensitivity arms would land on §2.4 and miss Z-1/Z-2/Z-3.

**Recommendation (NIT)**: append to §2.4 (after line 1128 "No arm has
verdict authority. Period."):

> Multi-period aggregation and backcast bootstrap sensitivity arms
> (Z-1, Z-2) are pre-registered separately in §0.6 (v0.2.6 amendment)
> with the same diagnostic-only / no-verdict-authority classification.
> Z-3 escalation gate routes to the R6 sibling iteration on threshold
> crossing.

This is a one-paragraph add; no table mutation needed. Keeps §2.4 as
the canonical entry point for "what sensitivity arms exist."

---

## Findings summary

### BLOCKers
*(none)*

### NITs (recommend folding into v0.2.6 directly; no re-review needed)
- **NIT-1** (Q2): document that simple-mean TRM is conservative against
  the FX-share signal vs volume-weighted (one half-sentence at line 813).
- **NIT-2** (Q3): pin the 1-observation-week edge case — INCLUDE as
  1-day aggregate (one row addition to weekly bucketing rule).
- **NIT-3** (Q4): pin the *non-decision* on re-anchoring with a one-line
  rationale (level-invariance of Δln statistic).
- **NIT-4** (Q5): document OR-vs-AND rationale on the Z-3 gate (one line
  at line 854).
- **NIT-5** (Q6): require explicit 9-trio TOC in cell 1 of the notebook
  (one line in test-surface bullet at line 872).
- **NIT-6** (Q7): pin persistence-scope — only per-path summary table
  written to disk, not the path tensor (one line at line 851).
- **NIT-7** (Q8): add forward-reference paragraph in §2.4 pointing to
  §0.6 Z-arms.
- **NIT-8** (Q1): inline-state "stationary bootstrap" in the Z-1
  bucketing table (one word; removes the §4 inheritance round-trip).

### PRAISE
- **Anti-fishing pin discipline is exemplary**: B, seeds (three distinct
  + one for Z-2), block_len formula AND its numeric value at each T,
  CI level, cov-rule, and Z-3 thresholds are all declared pre-data in
  the spec text — not deferred to plan or code. This is the standard
  set by the `feedback_pathological_halt_anti_fishing_checkpoint` and
  this amendment meets it.
- **CORRECTIONS-K integrity preserved**: the patch explicitly re-states
  "Z-arms are diagnostic-only per CORRECTIONS-K — they do not have
  verdict authority over the R5/R4-S3 framework" (line 795-797). Given
  v0.2.0's prior FAIL on §5.5/§9.6 contradiction over sensitivity-arm
  authority, this re-statement is exactly the right defensive move.
- **R6 escalation routing is concrete, not hand-wavy**: §0.6 names the
  R6 spec, the plan, and the version (`v0.1.3`) — verified extant on
  disk during this review. The escalation path is operationally
  actionable, not aspirational.
- **The user-asked sensitivity question is taken at face value**:
  "is the small FX share a regime artifact or a structural property?"
  is answered with a clean two-arm design that disentangles the two
  hypotheses without giving the result authority to revise the R5
  headline. This is the right epistemic posture after an unexpected
  PRIMARY result.

---

## Honnibal audit-pass coverage (against spec text, not code)

### tighten-types
- **N/A at spec level for new types** (no new contracts cross the
  `simulations/` boundary; the Z-arm outputs are notebook-local). §3.5
  contract table correctly NOT mutated.
- One minor: the spec uses informal "cost^USD_0", "Δln cost^USD" prose.
  When `06_z_sensitivity.ipynb` lands, those should map to typed names
  (suggest `bucket_cost_usd_log_diff`, `backcast_path_cost_usd_t0`) in
  notebook cell 2 — but that's an impl concern, not a spec gap.

### contract-docstrings
- The spec text *is* the contract for the notebook. Each Z-arm pre-pins:
  inputs (observed 28-day Δln series; Banrep TRM file), outputs
  (variance-decomposition with separately-reported cov per Q),
  invariants (B, seed, block_len, threshold). This is the
  spec-equivalent of contract-docstring coverage. PASS.

### try-except
- Z-3 escalation gate is the only branching control flow in the
  amendment. It is specified as a numeric threshold check on a computed
  median, not as exception handling — appropriate. No silent-swallow
  risk.
- One implicit gap: what happens if the Banrep TRM file has missing
  weekdays in the 2024-01-03 to 2025-12-31 horizon? The spec doesn't
  pin a missing-data rule for Z-2. Suggest adding: "weekdays with
  missing TRM are forward-filled at most 1 weekday; gaps >1 weekday
  drop the path." This is a NIT, not a BLOCK — implementer can pick a
  reasonable default and document in the notebook.

### pre-mortem
- **Most likely failure mode**: Z-2 returns a median FX share in the
  noisy "5x baseline = 0.00015" zone — formally triggers Z-3 escalation
  but substantively means nothing. The OR threshold gate handles this
  correctly per Q5 analysis above, but the disposition memo template
  should be ready for a "triggered by relative threshold only, absolute
  share is still negligible — recommend NOT activating R6" verdict path.
  **Recommendation (NIT-9)**: spec should pin that the Z-3 disposition
  cell reports BOTH the relative ratio AND the absolute share so the
  human reviewer can sanity-check borderline triggers.
- **Second failure mode**: weekly bucket has T~8 and block_len 2-3, B
  =10,000 stationary-bootstrap CIs at that T are themselves wide.
  Reading the weekly result as "definitive" would be a misuse. Spec
  already partially guards via the "within ±2× / >5×" interpretation
  rule (line 822-825). PASS.

---

## Cross-channel hand-off note

This review is independent of the Reality Checker channel running in
parallel. Areas where the two reviews should reconcile:
- If RC flags spec-compliance issues (e.g., the Z-1 weekly rule
  ambiguity also surfaces in RC's read), prefer RC's framing — they own
  spec-compliance.
- This Code Reviewer review focuses on operational rigor of the pins
  and audit-pass coverage; if RC's verdict is BLOCK on a CORRECTIONS-Z
  ambiguity that this review marked NIT, RC's BLOCK takes precedence.

---

## Overall verdict

**APPROVE_WITH_NITS.**

The v0.2.6 spec amendment is **landable as-is**; the 9 NITs above are
all single-line or single-paragraph improvements that can be folded
into v0.2.6 directly without re-review. The amendment:

- Pre-registers all parameters before data is touched (anti-fishing
  invariant satisfied).
- Preserves CORRECTIONS-K (Z-arms diagnostic-only, no verdict authority).
- Defines a concrete, file-extant escalation path to the R6 sibling.
- Does not mutate §3.5 contract table (correct — no new typed contracts).
- The single-notebook implementation is reviewable if the 9-trio TOC is
  pinned (NIT-5).
- Memory and runtime envelopes are well within tolerance (NIT-6 pins
  the persistence scope).

Code Reviewer channel: **PASS**. Awaiting Reality Checker verdict for
joint two-wave close.

---

## File references

- Spec under review: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md`
  (§0.6 at lines 783-895; §2.4 at lines 1113-1128; §3.5 at line 1253;
  §4 at lines 1293-1326)
- R6 sibling spec (escalation target): `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md`
- R6 plan (escalation target): `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/plans/2026-05-16-r6-continuous-stream-simulation-plan.md`
- Banrep TRM file (Z-2 dependency, verified extant): `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/data/raw/banrep_trm_daily.parquet`
- This report: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-17-v0_2_6-spec-review/code_reviewer.md`
