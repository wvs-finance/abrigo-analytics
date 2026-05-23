# E10 Pre-Phase-4 Model QA Review

**Reviewer:** Model QA Specialist (independent; did not author E10).
**Scope:** plan §7 item 2 — econometric/modeling design of Phase 4 (E10.3) tasks 4.1, 4.2, 4.2a, 4.3 + Phase-2.5 break-even pin + §9 verdict-ladder I/O contract.
**Counterpart:** Reality Checker (data provenance / posture firewall — out of my scope).
**Inputs read:** spec v0.7 §§3–9, §11 (`docs/specs/2026-05-20-e10-gsps-v0.7-convex-multicurrency-design.md`); plan v0.2 Phase 4 lines 323–362, §4 lines 446–483, §7 lines 565–597 (`docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md`); Phase-2.5 break-even (`notebooks/e10_gsps/diagnostics/E10.2.5_break_even_threshold.md`); Phase-3 completion (`scratch/2026-05-20-e10-revision/e10_phase3_completion.md`).
**Top-line verdict:** **CONDITIONAL** — Phase 4 may fire after the surface-grid resolution (task 4.2) and the interior-crossing detection rule (task 4.2a) receive explicit pre-task guidance per items 2 and 3 below.

---

## Per-item findings

### Item 1 — Task 4.1: two-way FE + currency-FE-only co-primary regression — **PASS**

**Estimability at G=5, n=150, T=30.** The two-way FE absorbs 5 currency dummies + 30 month dummies − 1 (collinearity) = 34 absorbed parameters against n = 150, leaving 115 residual DoF for the single slope of interest (Phase-3 panel report confirms exactly this count, completion §2). The within-transformation is mathematically estimable — there is no rank deficiency. The plan correctly flags (line 353) that with G ≈ 5 currency clusters *and* month FE on, the **identifying variation** is "very thin" — the residualized FX-variance series has both currency means and month means projected out, leaving only the (currency, month) idiosyncratic component of FX variance to drive β. This is a legitimate descriptive concern, not an identification failure.

**Co-primary choice — currency-FE-only vs month-FE-only.** Currency-FE-only is the right co-primary, not month-FE-only. Rationale:

1. The cross-sectional dispersion of FX-variance across the 5 currencies (NGN highest at mean `Var(Δlog FX) ≈ 1.31e-3`; EUR/GBP lowest at ≈ 3e-5 — Phase-3 §3) is ~40× — this is the *between*-currency variation the M-sketch's hedge-sizing depends on (it determines how different the EM and DM regimes are for the §13.2 ATM straddle). Currency-FE-only **preserves** the cross-currency level information while controlling for permanent month-level macro shocks via the panel structure → it answers a different descriptive question than two-way FE (global+idiosyncratic vs idiosyncratic-only).
2. Month-FE-only would discard cross-currency level information entirely (since all 5 currencies sit on the same monthly clock) — this is the *less* informative pairing for an FX-vol hedge whose denomination choice is currency-specific.

The plan's pairing is correct.

**Gap-as-descriptive-content framing.** The two-way-vs-currency-only β gap is a Frisch-Waugh-Lovell decomposition: it quantifies how much of the β signal lives in *global* (month-FE-absorbed) FX-vol co-movement vs *idiosyncratic* (within-month, cross-currency) FX-vol dispersion. Reporting this gap as a descriptive number is defensible **iff** the report carries no p-value, no CI, and no language asserting "more / less significant" — only "the two-way β is X, the currency-only β is Y, the gap quantifies the global-vs-idiosyncratic share." The plan line 353 explicitly says "no inferential claim, no confirmatory language" — the firewall is in place. PASS.

**G≈5 clustered-SE caveat.** Correctly demoted to context-only (lines 353, 380 of plan; spec §8). At G=5 the cluster-robust variance estimator is severely size-distorted (the 2/(G−1) Bessel-style correction is meaningless); any reported SE must carry the explicit "context-only, NOT inferential" label. **Recommendation:** the specialist agent should literally not print a p-value or t-statistic — only the point estimate and the cluster count, with a one-line "G=5 — clustered SE is not estimable as inference" footnote. This is an enforcement note, not a design block.

### Item 2 — Task 4.2: FX-variance-share surface grid resolution — **FLAG** (escalate to user; brainstorm-judgment)

**What the spec gives.** Spec §11 open item 1 (line 345) explicitly defers grid resolution to E10.3 (Phase 4). Plan task 4.2 (line 354) tags it `[brainstorm-judgment]` and *requires* the specialist to surface the chosen resolution with a 4-part decision-citation before locking. **There is no spec-pinned default.**

**Lower bound on grid density (driven by 4.2a interior-crossing).** With the Phase-3 panel showing FX-variance share at mean 0.0002 and max 0.0039 (Phase-3 §3) — all sitting **three orders of magnitude below `s_be = 0.25`** — the realistic interior-crossing scenario is not "surface dips below 0.25 in the middle" but "surface dips above 0.25 in some narrow Q-window we didn't grid-sample." For the share `s(Q) = Var(Δlog FX) / (Var(Δlog FX) + Var(Δlog Q) + 2·Cov)` to cross `s_be = 0.25`, the Q-variance term would need to fall by ~3 orders of magnitude (since FX-variance is bounded by the real central-bank data and roughly constant in Q). A non-monotonic crossing therefore lives in the Q-low regime where `Var(Δlog Q)` is small — i.e. near the lower endpoint of the anchored Q-range. **The grid must be log-spaced (or denser at low-Q), not linear.**

**Defensible default — my recommendation.** Adopt **log-spaced 50 points** across the anchored Q-range `[Q_low, Q_high]` as the prior; allow density doubling (to 100) if a 50-point pass shows any cell within ±0.5 dex of `s_be`. This gives:
- log-spacing — catches the low-Q regime where `Var(Δlog Q)` collapses fastest;
- 50 points — comparable to standard sensitivity-surface practice (Niederreiter density on a 1-D smooth surface);
- adaptive refinement — closes the "non-monotone in a narrow band" risk without committing to 500+ points up front.

**Should resolution scale with Q-range width?** Yes — the anchored range is ~60–130 priceable queries/month at the centre with a bracketed envelope (Phase-2.5 §1.1). On a log scale this is ~0.5–1 dex; 50 log-spaced points = ~50 samples per dex, ample. A wider envelope (e.g. anchored bracket pushes Q_low << 10) would mechanically demand more points to keep per-dex density constant.

**Escalation required.** This is a `[brainstorm-judgment]` choice that gates verdict-rung classification (a too-coarse grid misses an interior crossing → silent verdict drift). **The specialist must surface the chosen resolution to the user with a 4-part decision-citation BEFORE running task 4.2.** My recommended default — log-spaced 50 points + adaptive doubling — is the prior the agent should propose. FLAG.

### Item 3 — Task 4.2a: interior-crossing detection rule — **CONDITIONAL** (rule needs hardening)

**Is endpoint-only insufficient?** Yes, definitively. The decomposition shape `s(Q) = V_fx / (V_fx + V_q(Q) + 2·Cov(Q))` is **not monotone in Q** in general: `V_q` scales with the volatility of `Δlog Q`, which itself depends on the intensity λ(t) of the Cox process — at very low λ the process is dominated by zero-day clustering (high VMR), at high λ the process approaches the equidispersed limit (VMR → 1). The Phase-3 calibration sits in the high-overdispersion regime (VMR ≈ 20), but a sweep across the anchored Q-range traverses regions where this regime can soften. **An interior dip below `s_be` is genuinely possible and endpoint-only checking would miss it.** The plan's "scan every grid cell" rule is correct in principle.

**"Any single cell below `s_be` flags interior-crossing" — too aggressive.** As written (plan line 355), one noisy cell triggers the flag. Two failure modes:
1. **False positives at grid boundaries** — a single cell at the very edge of the Q-range can flip the flag without representing a *substantive* interior crossing.
2. **Simulator-noise-induced false positives** — each cell's `Var(Δlog Q)` carries Monte Carlo variance from the NHPP run; a single noisy cell could dip purely from simulation noise even if the population surface is monotone.

**Recommendation — contiguous-cells sub-rule.** Tighten the detection to: emit `interior-crossing` flag iff **≥ 3 contiguous grid cells** sit below `s_be`, AND those cells are **strictly interior** to the grid (not at the two endpoints). This:
- removes single-cell-noise false positives;
- preserves real interior crossings (which by definition span a region, not a single point);
- keeps the rule mechanical (no judgment on what counts as "material" — it's a fixed integer).

The 3-cell threshold is conservative; at 50 grid points it represents ~6% of the range. The plan should be amended to pin this sub-rule before task 4.2a runs — otherwise the specialist will implement the literal "any single cell" rule of line 355 and the §9 classifier will be unstable to simulator noise.

**§9 wire-up.** The plan correctly routes the flag into the verdict classifier (task 6.1, line 401 — "interior-crossing flag" is in the classifier's input vector). PASS on the wiring; CONDITIONAL on the rule definition.

### Item 4 — Task 4.3: non-statistical 5-currency min–max / IQR spread display — **PASS**

**Right descriptive object?** Yes. With G = 5 and EM/DM mixing (COP, BRL, NGN vs EUR, GBP), the wild-cluster bootstrap is size-broken (G < 12 distortion threshold) and the permutation arm has 2⁵ = 32-point support with EM/DM exchangeability violation — both correctly dropped (plan line 356; spec CORRECTIONS-E10-6). The replacement — overplotting 5 per-currency surface curves + min–max + IQR envelope — is the **honest descriptive object** at G = 5: it shows the raw cross-currency spread *as a spread*, not as an inferential band.

**Within-bucket-then-across-buckets rule?** Worth considering but not required. At G = 5 with 3 EM + 2 DM, the two natural buckets are sufficient to read off the EM/DM split visually if the 5 curves are colour-coded by bucket (EM in one hue family, DM in another). An explicit "EM envelope" and "DM envelope" sub-display would carry only 3-currency and 2-currency observations respectively — too thin to add information beyond the colour coding. **Recommendation:** colour-code by EM/DM bucket in the overplot (cosmetic, not statistical) — the reader will infer the bucket split from the layout. No additional within-bucket envelope is necessary or defensible at this n.

**Firewall against inferential mis-reading.** The explicit "non-statistical, not a CI, not an inferential band, not a hypothesis test" label (plan line 356, repeated four ways) is sufficient *if and only if* the visual rendering also carries the label in-figure (as a subtitle or caption), not just in surrounding prose. **Recommendation:** the figure title or subtitle must literally read "Non-statistical cross-currency spread (5 currencies; min–max + IQR; NOT a confidence interval)." A figure that escapes from the notebook into a slide deck without its surrounding prose must still self-firewall. This is an enforcement note for task 4.4 (notebook author), not a design block. PASS.

### Item 5 — Phase-2.5 break-even `s_be = 0.25` frozen — **PASS**

Confirmed against `notebooks/e10_gsps/diagnostics/E10.2.5_break_even_threshold.md`:
- §5 declares `s_be = 0.25` FROZEN as the imported §7 field-3 material threshold (line 335);
- §3 derivation is mechanical from the task-2.5.1 ex-ante prior `s_exp = 0.25` + task-2.5.2 ideal-scenario fair premium `φ = 0.25` + payoff-capture efficiency `c_payoff = 1` (ideal scenario) → `s_be = φ / c_payoff = 0.25`;
- §0.1 firewall bright line documents: no Phase-3 §4 decomposition output and no E10-panel realized variance consumed — confirmed by reading the derivation (which references only published vol regimes and the Phase-2 Q-volume range);
- §4 ideal-scenario caveat is correctly stated — `c_payoff = 1` is the lower bound on `s_be`; a real (loaded) venue would lift `s_be` above 0.25.
- The "consistency" between `s_exp = 0.25` and `s_be = 0.25` is correctly addressed in §3.4 (not circular — it is the fair-pricing property of a hedge sized to an expected exposure).

Phase 4 task 4.4 must compare the surface against this **fixed** `s_be = 0.25` value, not re-derive it. PASS.

### Item 6 — §9 verdict-ladder I/O contract — **PASS**

The §9 ladder (spec §9, three rungs: SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT) consumes six flags via the Phase-6 classifier (plan task 6.1, line 401):
1. `surface-computed` — Phase 4 task 4.2 emits this on successful grid evaluation.
2. `material-gap` — Phase 3 task 3.3 already emits this per cell (Phase-3 completion §2 confirms 0 material-gap cells; the panel-wide aggregate is available).
3. `simulator-anchored` — Phase 2 (E10.1) calibration deliverable; consumed unchanged.
4. `Q-variance-dominance` — Phase 4 task 4.2 must emit this (the share is far below `s_be` across the whole anchored range — current panel headline of mean share ≈ 0.0002 strongly indicates this rung will fire).
5. `interior-crossing` — Phase 4 task 4.2a emits this (subject to item 3's hardening).
6. `DV-flag` — Phase 1 (E10.0) deliverable; PASS-FREE confirmed.

Phase 4 produces flags 1, 4, and 5. Flag 4 (Q-variance dominance) needs an **explicit emit step in task 4.2**: the surface evaluator must compute the share at every grid point and emit a boolean `q_variance_dominates = (s(Q) < s_be) at every grid point`. The plan does not explicitly call this out in task 4.2's deliverable line (line 354), but it is implied by the §9 NON-RETIREMENT rung's "across the whole anchored range" condition. **Recommendation:** the specialist must add `q_variance_dominance_flag` to task 4.2's emitted artifacts alongside the grid surface and the interior-crossing flag. This is a small spec-traceability tightening, not a redesign. PASS with note.

---

## Top-line verdict — CONDITIONAL

Phase 4 may fire after the specialist agent receives explicit pre-task guidance on:

1. **Task 4.2 surface-grid resolution** (item 2) — adopt **log-spaced 50 points across the anchored Q-range with adaptive doubling to 100 if any cell sits within ±0.5 dex of `s_be = 0.25`** as the prior; surface this choice to the user with a 4-part decision-citation BEFORE running the evaluator. This is the only `[brainstorm-judgment]` task in Phase 4 and is the load-bearing escalation.

2. **Task 4.2a interior-crossing detection rule** (item 3) — tighten "any single cell below `s_be`" to **≥ 3 contiguous strictly-interior grid cells below `s_be`** to remove single-cell-noise false positives. This is a rule-hardening, not a redesign; if the user prefers the literal "any cell" rule for maximum conservatism, that is also defensible — surface the choice.

3. **Task 4.2 emit `q_variance_dominance_flag`** explicitly (item 6) — add to the task's emitted artifacts so the Phase-6 §9 classifier (task 6.1) has the input it requires for the NON-RETIREMENT rung.

4. **Task 4.4 figure-caption firewall** (item 4) — the non-statistical spread display must carry the "NOT a confidence interval" label *in-figure*, not just in surrounding prose. Enforcement note for the notebook author.

No spec amendment (CORRECTIONS-E10-X) is required. The four items above are *task-level* pre-task guidance; the spec is sound, the Phase-3 panel is sound, the Phase-2.5 break-even is frozen, the descriptive posture is intact, and the §9 verdict ladder accepts the inputs Phase 4 will produce.

**Anticipated verdict trajectory.** With Phase-3 panel showing FX-variance share at mean 0.0002 / max 0.0039 (~3 orders of magnitude below `s_be = 0.25`), the surface-grid evaluator will almost certainly find `q_variance_dominance` across the whole anchored range, triggering the **HALT-Q-DOMINANCE → NON-RETIREMENT** rung. This is the spec-anticipated honest outcome (spec §7 field 7b, §9 NON-RETIREMENT row) and the methods-paper §5 hook survives at descriptive form (spec §12). The Phase 4 design is correctly built to produce this verdict cleanly, without engineering it away.

---
*Pre-Phase-4 Model QA review — CONDITIONAL — closes here.*
