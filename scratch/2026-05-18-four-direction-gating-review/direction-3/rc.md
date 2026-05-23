# Reality Checker Review — Direction 3 (Jump-Conditional Re-Test)

**Date**: 2026-05-18
**Reviewer**: TestingRealityChecker (Reality Checker lens)
**Target**: `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 3
**Verdict**: **NEEDS WORK — DO NOT DISPATCH AS WRITTEN**
**Severity**: 2 critical fishing-risk findings + 1 critical N-misrepresentation; the gate as written cannot answer its own gating question with the data on hand.

---

## TL;DR

The gating step is built on a misstatement about sample size. The spec says "the existing dev_ai_cost_v2 daily panel (N≈150 trading days)" — that is FALSE. The actual cost panel is **N=29 daily observations** (`data/panels/notional_cost_panel.parquet`, verified). The N=150 figure appears to come from confusing *TRM trading days available in a 7-month window* with *cost-panel rows*; only the latter is what a regression actually runs on. Every power and jump-count argument in §Direction 3 needs to be redone from this corrected denominator.

Compounding that, on the empirical TRM in the panel window, **only 6 days exceed |2σ|**, only **2 days exceed |2.5σ|**, and **zero days exceed |3σ|**. Even if the panel were N=150 cost rows, jump-conditional inference would be running on a single-digit event count — and the panel is in fact N=29, so any jump-conditioned regression of cost on jumps is *mechanically uninformative* before any pre-pin discipline matters.

The 2-day effort estimate is plausible *only if* the gate is honestly returning FAIL on insufficient jump count — which is what the empirical evidence here forces. If the team intends to actually estimate β_jump under threshold-regression on this panel, the effort estimate is fictional.

---

## Section A — Critical findings

### A1. [CRITICAL] N=150 is not the panel — N=29 is

The spec asserts "existing dev_ai_cost_v2 daily panel (N≈150 trading days)" (§Direction 3 lines 127, 132, 140) and again "~150-day panel" (line 177). I loaded `data/panels/notional_cost_panel.parquet` directly:

```
Panel shape: (29, 11)
Date range: 2026-01-06 to 2026-05-14
```

The verdict memo `project_dev_ai_cost_v2_verdict.md` lines 17–18 confirms: **"Observed N: 28 weekday rows after first-diff — BELOW demonstration-grade N_MIN floor"** and "Window: 2026-01-06 to 2026-05-14". The 150-day figure must be either:

- a confusion with TRM days available (I count 137 trading days in 2025-10-15 → 2026-05-14, or 563 in the full TRM file 2024-01 → 2026-05), or
- a confusion with calendar days in the panel window (2026-01-06 to 2026-05-14 is ~129 calendar days).

Neither of those is the regression-N. The cost-panel is N=29 because the pilot subject only generated cost on 29 weekdays.

**Consequence**: every power and jump-count argument in §Direction 3 has to be redone against N=29 (or N=28 post-first-diff). Pre-pin discipline cannot rescue an N=28 jump-conditional regression — the design is dead-on-arrival from a mechanical-validity standpoint.

**Required fix**: rewrite the gating-question paragraph (line 132) and pass criteria (lines 161–168) against the actual N. The honest gate question becomes: "On the existing N=28 panel, is there *any* threshold-regression specification that gives ≥10 jump-days *intersecting* cost-panel days?" — and the answer, as A2 shows, is no.

---

### A2. [CRITICAL] Jump count on the actual TRM window is mechanically below the fail threshold the spec itself sets

I ran the empirical jump count on the TRM for 2025-10-15 → 2026-05-14 (137 trading days, the widest plausibly-relevant window). Results:

| Threshold | Count | Up | Down |
|---|---|---|---|
| \|r\| ≥ 2.0σ | 6 | 4 | 2 |
| \|r\| ≥ 2.5σ | 2 | 2 | 0 |
| \|r\| ≥ 3.0σ | 0 | 0 | 0 |

Bipower diagnostics over the same window:
- Days with JV > 0: 42
- Days with JV/RV > 0.5 ("bipower jump days"): 19
- Days in p90-stress regime (rolling 30d vol ≥ p90): **11**
- Days in calm regime: 53

The spec's own fail criterion (line 166): "Jump count < 5 (mechanically uninformative)." Pass criterion (line 163): "Jump count in panel ≥ 10".

**Critical math**: even on the wider 137-TRM-day window, the bipower-based "stress" regime has only 11 days. Once you *intersect* those 11 stress days with the 29 cost-panel days, you typically get **2-4 stress days inside the regression sample** (rough estimate: 11/137 × 29 ≈ 2.3). That fires the spec's own FAIL criterion at line 166.

Asymmetric up/down split is even worse: 2 up-jumps and 0 down-jumps at the 2.5σ threshold across the whole window. The asymmetric jump-β arm has *literally zero* down-jump observations available. The arm is non-estimable.

**Consequence**: the gate's answer is "FAIL — jump count below the mechanical floor" regardless of any pre-pin specification choice. The 2-day implementation effort is wasted unless the goal is to formally document the FAIL.

**Required fix**: either (a) reframe the gate as a *jump-count census* with a 1-day effort (not 2-day), and skip the bipower decomposition + threshold regression entirely; or (b) abandon the same-panel re-test and require a wider TRM-aligned panel (the 137-day TRM window has 2 down-jumps and 4 up-jumps at 2.5σ — still inadequate, but at least bipower IV/JV decomposition has the dynamic range to be meaningful).

---

### A3. [CRITICAL] POWER_MIN relaxation 0.80 → 0.50 is exactly the pattern the anti-fishing rule bans

The spec (line 161) relaxes the power floor: *"Jump β estimable with power ≥ 0.50 at the existing N (relaxed from 0.80 because the integrated-variance test already showed 0; this is a follow-up test, not the primary)."*

Cross-reference `feedback_pathological_halt_anti_fishing_checkpoint.md` step 3:
> "option (c) 'loosen scope mid-stream' is anti-fishing-banned and must be flagged as such in the memo."

And step 4: a CORRECTIONS block must cite (a) old value, (b) new value, (c) preserved-guarantees argument, (d) commit anchors.

The Direction 3 spec does none of this. It silently relaxes POWER_MIN from project-default 0.80 to 0.50 *in a gating step targeting a re-analysis of data that already returned null*. That is the exact silent-relaxation-to-pass pattern the framework bans.

The CLAUDE.md anti-fishing invariants explicitly say `POWER_MIN = 0.80` is NON-NEGOTIABLE, and `feedback_pathological_halt_anti_fishing_checkpoint` lists "Rev-5.3.1 N_MIN relaxation" as the canonical example of how a relaxation MUST be processed.

**Counter-argument the spec could make**: the dev_ai_cost_v2 iteration *itself* was demonstration-grade with `POWER_MIN=0.50` (verdict memo line 14). One could argue Direction 3 inherits that grade. But that's still a relaxation requiring CORRECTIONS-block discipline, not silent application. And critically: the dev_ai_cost_v2 demonstration-grade designation was negotiated *via* a documented Amendment #5 in the spec; Direction 3 has no equivalent paper trail.

**Required fix**: either (a) bind Direction 3 to demonstration-grade explicitly with a CORRECTIONS-style block citing v0.2.10 Amendment #5 as the anchor and preserving the "exploratory" exit-grade pin, or (b) hold the line at POWER_MIN=0.80 and accept the gate will return FAIL on power grounds alone (which it will at N=28).

---

## Section B — High-severity findings

### B1. [HIGH] Hidden DOF: threshold percentile is not pre-pinned

The pre-pin block (lines 154–158) pre-pins:
- Sign (β_stress > β_calm > 0)
- Magnitude (β_stress ≥ 0.05 SD)
- Lag (contemporaneous primary, 1-day secondary)
- Decomposition method (Barndorff-Nielsen, not Lee-Mykland)

But the threshold percentile defining "stress" is mentioned twice with different values: **p90** in the method body (line 148: "rolling_30d_FX_vol ≥ p90"), and the risks block (line 177) treats p90 as if it were pre-pinned. The pre-pin block itself does NOT include "threshold = p90" as an explicit pin.

This is a 4+ DOF gap: p75, p80, p85, p90, p95 are all defensible choices, and the analyst can shop them post-hoc. The user's prompt flags this as exactly the worry: "additional DOF (e.g., threshold = p90 vs p95 vs p80)".

Also missing from the pre-pin:
- Rolling-window length (the method picks 30d; why not 20d, 60d?)
- Jump-detection threshold (the pass-criteria says "Jump count ≥ 10" but never says jumps at what σ-multiple — is it the bipower-JV>0 criterion, or |r|>2σ, or Lee-Mykland critical value?)
- Whether the asymmetric up/down split is *always* run or only conditional on the symmetric test passing
- Whether sign expectations apply per-direction (β_up_jump vs β_down_jump separately, or only on |jump|)

**Required fix**: pre-pin block must enumerate ALL of: threshold percentile (single value, not "p90 or similar"), rolling-window length, jump-detection σ-multiple, asymmetric-arm gating rule.

---

### B2. [HIGH] "Demonstration-grade exit" framing creates a one-way confirmation-bias door

The spec says (line 178): *"treat as exploratory/demonstration-grade regardless of outcome unless replicated on a fresh dataset."*

This sounds disciplined but is asymmetric in practice:

- If the test returns null → "we already said it was exploratory, no claim made" → FAIL is absorbed with no cost.
- If the test returns positive → "exploratory finding, suggestive evidence for jump-channel β > 0, motivates a fresh-dataset replication iteration" → the positive result still gets cited as a directional signal and drives M-design pivots.

That's a one-way valve. Combined with the same-data re-analysis context (garden-of-forking-paths), this creates an evidence asymmetry exactly the kind anti-fishing discipline is supposed to prevent.

**Cross-reference**: the dev_ai_cost_v2 verdict memo lines 67-72 carefully spell out what NO claims may be made from the demonstration-grade iteration. Direction 3 inherits none of those guardrails in writing.

**Required fix**: pre-pin a positive-result discipline block analogous to verdict memo §6's "Anti-fishing pins carried forward":

- NO citation of Direction 3 jump-β as evidence for the framework absent fresh-dataset replication.
- NO use of "directional" / "suggestive" / "consistent with" framing in any downstream artifact.
- If positive, the *only* downstream action permitted is dispatching a fresh-data replication iteration; no M-design priors may shift on the basis of Direction 3 alone.

---

### B3. [HIGH] Bipower variation at daily frequency — methodological validity is borderline, not robust

The spec (line 176) asserts: *"At daily frequency (our data) the method is robust per the Barndorff-Nielsen 2004 paper."* This claim is misleading.

The Barndorff-Nielsen & Shephard 2004 paper develops bipower variation as an *intraday* (high-frequency) estimator. The estimator's asymptotic properties are derived as Δ → 0 (sampling frequency increases). At daily frequency, BV reduces to `(π/2) × |r_t| × |r_{t-1}|` — a single-product estimator with extremely high variance and known small-sample bias.

Daily bipower works in the literature where it works because (a) the sample is in thousands of days and the noise averages out, or (b) it's used as a low-resolution screen, not as a regression input. In our case:

- N=28 cost rows, with bipower computed pairwise → effective bipower-pair count is ~27.
- Mean BV in my computation (0.00005640) is *larger* than mean RV (0.00005349). That's a sample-size artifact, not a meaningful decomposition; it indicates the bipower estimator is unstable at this N.
- Days with JV/RV > 0.5 = 19 out of 137 = 14% — that's a noisy classification, not a clean jump identification.

The spec's risks paragraph (line 176) flags microstructure noise as the concern; the real concern at daily frequency is *small-sample variance of the bipower estimator itself*. The spec misidentifies the validity threat.

**Required fix**: methodology section must either (a) cite a daily-frequency bipower-variation application paper with comparable N (not Barndorff-Nielsen 2004), or (b) substitute a method actually designed for daily-frequency jump detection (Lee-Mykland 2008 with the daily-frequency adjustment, or Aït-Sahalia-Jacod 2009 threshold method). The current cite is a fig leaf.

---

## Section C — Medium-severity findings

### C1. [MEDIUM] Effort estimate of 2 days is optimistic even for a clean FAIL

The 2-day estimate (lines 170–173) allocates:
- Day 1: bipower decomposition + threshold-regression implementation + new notebook
- Day 2: 2-way review + verdict memo

Realistic budget for a v0.2.10-quality notebook honoring the trio + decision-citation discipline (per `CLAUDE.md` "Notebooks" section: every why-markdown / code-cell / interpretation-markdown trio is a HALT checkpoint):

- Trio discipline alone for ~6 analytical steps (data load, log-returns, bipower decomp, JV/RV classification, threshold split, asymmetric split, regression, post-hoc) = ~24 markdown checkpoints = 1 day of human-in-the-loop review at observed cadence.
- Decision-citation blocks (4-part: reference / why / relevance / connection) before every test choice = 5+ citation blocks = ~0.5 day to research and write properly.
- 2-way review on a fishing-flagged re-analysis is NOT a 1-day operation — expect 2 days of reviewer back-and-forth given the A3 power-relaxation issue and the B1 hidden-DOF issue.

Realistic effort: **3.5–4.5 working days**, not 2. The 2-day estimate would only hold if the gate returns FAIL on jump count within Day-1 morning and the rest is verdict-memo writing — which, given A2 evidence, is actually the realistic case. But that means the *effort estimate is honest only under FAIL*; the PASS-path branch is mis-budgeted by 2x.

**Required fix**: budget two paths separately. FAIL-on-jump-count path: 1 day (data pull + census + verdict). PASS-on-jump-count path (which won't happen given A2): 4 days for full bipower + threshold + asymmetric arms + 2-way review.

---

### C2. [MEDIUM] Pass criterion line 163 has an internal inconsistency

Line 163: *"|β_jump - β_calm| confidence interval excludes zero at α=0.10 (two-sided)."*

But the threshold-regression spec (line 147) defines `β_calm` and `β_stress`, not `β_calm` and `β_jump`. The jump-conditional regression in the method (line 142) operates on the IV/JV decomposition, yielding `β_IV` and `β_JV`. There is no `β_jump - β_calm` quantity defined anywhere in the method block.

This is either a sloppy pass-criterion or a smoking gun for *which* test is the primary — and the spec has not made that decision.

**Required fix**: pick one — either the test is bipower-decomposition (β_IV vs β_JV, joint estimation), or it's threshold-regression (β_calm vs β_stress, regime-conditional). Not both as the "primary" with criterion-text borrowing from both.

---

### C3. [MEDIUM] No explicit handling of the holiday-Monday / NA-row interactions

The dev_ai_cost_v2 v0.2.10 panel went through Codex commingling filters and holiday-Monday surfacing (verdict memo §4, Wave-3 commits). Direction 3 inherits the panel post-cleanup but does not address what happens when:

- A jump day falls on a holiday (no cost row → unobservable)
- A stress-regime day has 0 messages (notional cost is 0 or near-0)
- A pre-pinned 1-day-lag jump straddles a weekend gap

These interactions could systematically bias the conditional samples (e.g., COP/USD often jumps on Mondays after weekend news; if Mondays disproportionately have cost rows or disproportionately lack them, the conditional sample is non-random).

**Required fix**: pre-pin handling rules for holiday days, zero-cost days, and weekend-spanning lags BEFORE running. Cite the v0.2.10 holiday-Monday surfacing rules as inherited.

---

## Section D — Cross-direction reality check

Comparing Direction 3 against Directions 1, 2, 4 sequencing (lines 239–242: "All four gating steps run in parallel"):

Direction 3 is the *only* one of the four that re-uses already-analyzed data. Directions 1, 2, 4 all have data-acquisition gates. The asymmetry matters: Direction 3 has zero data-cost and can be cheaply attempted, *which is exactly why* the anti-fishing discipline needs to be strictest for it. The current spec inverts this — Direction 3 has the loosest discipline (POWER_MIN relaxation, incomplete pre-pin, optimistic effort estimate).

**Reality-check inference**: the cheap availability of the data is what makes Direction 3 attractive *and* what makes it the highest fishing-risk of the four. The spec hasn't priced that in.

---

## Section E — Reality-check pass/fail summary against user's review questions

| # | Question | Verdict | Evidence |
|---|---|---|---|
| 1 | Garden-of-forking-paths: pre-pin sufficient or hidden DOF? | **HIDDEN DOF** | B1: threshold pct, rolling window, jump-σ multiple, asymmetric gating all unpinned. |
| 2 | N for jumps on actual TRM history? | **MECHANICALLY INFORMATIVE FAILS** | A2: 6 |r|≥2σ, 2 |r|≥2.5σ, 0 |r|≥3σ in 137-day window; intersected with N=29 panel ≈ 2-4 stress days. |
| 3 | Bipower at daily frequency valid? | **BORDERLINE, MIS-CITED** | B3: BN&S 2004 derives asymptotics for intraday; daily-N=28 bipower is high-variance. Spec misidentifies the threat. |
| 4 | POWER_MIN 0.80 → 0.50 defensible? | **NO, fishing-banned silent relaxation** | A3: no CORRECTIONS block, no Amendment-#5-equivalent paper trail; exactly the pattern `feedback_pathological_halt_anti_fishing_checkpoint` bans. |
| 5 | Pre-pin sufficient? | **NO** | B1: 4+ DOF unpinned. |
| 6 | 2-day effort estimate realistic? | **OPTIMISTIC under PASS path; honest under FAIL** | C1: trio + citation discipline alone ≈ 1.5 days; 2-way review on a fishing-flagged re-analysis ≈ 2 days. Real budget 3.5-4.5 days unless FAIL is declared early. |
| 7 | Demonstration-grade exit creates confirmation-bias door? | **YES** | B2: asymmetric absorption of FAIL vs PASS results; no positive-result discipline block. |

---

## Section F — Recommended actions

**Status**: NEEDS WORK. Do not dispatch the implementation notebook (`07_jump_conditional.ipynb`) until the following are addressed.

**Required-before-dispatch fixes** (in priority order):

1. **Correct the N misstatement** (A1). Replace "N≈150 trading days" with "N=28 weekday cost-panel rows post-first-diff (TRM available on 137 trading days in the window)" everywhere. Redo all power and jump-count statements against N=28.

2. **Run the jump-count census FIRST as a separate sub-gate** (A2). Before any bipower-decomposition implementation, document the empirical jump count *inside the cost-panel intersection*. If it's < 5 (which my analysis says it will be), the gate returns FAIL and no notebook is written. This converts Direction 3 from a 2-day notebook task into a 4-hour census task.

3. **Process the POWER_MIN relaxation through the CORRECTIONS-block discipline** (A3). Cite v0.2.10 Amendment #5 as the inheritance anchor; spell out the preserved-guarantees argument; treat the relaxation as a `feedback_pathological_halt_anti_fishing_checkpoint`-style event with the user explicitly choosing the relaxation path.

4. **Pre-pin the missing DOF** (B1). Single threshold percentile (not "p90 or similar"). Single rolling-window length. Single jump-detection σ-multiple. Explicit asymmetric-arm gating rule.

5. **Add positive-result discipline block** (B2). Symmetrize the absorption of PASS vs FAIL outcomes.

6. **Replace BN&S 2004 cite or substitute a daily-frequency-validated jump-detection method** (B3).

7. **Resolve the β_calm vs β_jump pass-criterion inconsistency** (C2).

8. **Pre-pin holiday/zero-cost/weekend-lag handling** (C3).

9. **Re-budget the effort estimate with separate PASS-path and FAIL-path tracks** (C1).

**Strong recommendation**: re-scope Direction 3 to a **1-day census-only gate** that returns FAIL on jump count *without* implementing the bipower-decomposition notebook. The empirical evidence (A2) is clear that the notebook would not produce inferentially-meaningful output on this panel. Resources freed up should be redirected to Directions 1, 2, 4 — all of which have the chance to acquire data with adequate N.

**If the framework owner insists on running the full notebook despite A2**: the gate is then explicitly a *methodology-pilot* exercise (does the bipower pipeline run? does the threshold-regression code work?), NOT a β-estimation exercise. The pass criteria must be rewritten to reflect that — no β claim, just code-validation — and the verdict memo must explicitly state that no inferential conclusion may propagate forward.

---

## Section G — What WOULD make this gate viable

For completeness, the jump-conditional hypothesis is theoretically interesting and worth eventually testing. What would it take to make Direction 3 a legitimate iteration rather than a fishing-risk re-analysis?

- Panel N ≥ 150 *cost rows* (not TRM days) — requires ~3 years of pilot data at observed cadence, OR a pivot to a higher-cadence cohort.
- ≥ 30 jump-days inside the cost-panel intersection (Lee-Mykland or 2.5σ definition).
- Pre-pin done BEFORE any look at the new data — i.e., the bipower spec must be locked while the wider panel is still being collected.
- Power calculation at POWER_MIN=0.80 (not 0.50) under the jump-conditional regression's effective N.

The 2026-05-18 same-panel re-analysis as currently scoped meets none of these. It should either be deferred until the panel grows, or executed as an explicit methodology pilot with no β claims.

---

## File-paths cited

- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-18-four-direction-gating-step-plans.md` (target spec, §Direction 3 lines 124–181)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/memory/project_dev_ai_cost_v2_verdict.md` (N=28 verdict memo, Amendment #5 demonstration-grade anchor)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/memory/feedback_pathological_halt_anti_fishing_checkpoint.md` (anti-fishing relaxation protocol)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` (closed iteration spec v0.2.10, the data this re-analyzes)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/data/panels/notional_cost_panel.parquet` (cost panel, N=29 rows verified)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/data/raw/banrep_trm_daily.parquet` (TRM source, 137 trading days in 2025-10-15→2026-05-14 window)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/CLAUDE.md` (N_MIN=75 / POWER_MIN=0.80 anti-fishing invariants)
