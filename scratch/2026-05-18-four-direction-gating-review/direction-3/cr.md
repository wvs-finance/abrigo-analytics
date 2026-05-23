# Code Reviewer — Direction 3 (Jump-Conditional Re-Test) — Methodology Rigor

**File reviewed:** `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 3 (lines 124-181)
**Reviewer lens:** methodology rigor (econometric correctness, identification, anti-fishing carry-forward)
**Verdict:** **CONDITIONAL — multiple blockers must be resolved BEFORE notebook execution**

## Summary

Direction 3 proposes re-analyzing the `dev_ai_cost_v2` panel with Barndorff-Nielsen / Shephard (BNS, 2004) bipower decomposition, threshold regression, and asymmetric jump-β to recover an FX-on-cost signal after R5's integrated-variance β ≈ 0. The instinct is reasonable — distinguishing jump from continuous risk is legitimate in FX econometrics — but the spec as written has **one BLOCKER that invalidates the whole gate** (panel-size misstatement: N=28 actual vs. N≈150 claimed), one **method-validity BLOCKER** (BPV theory requires Δ→0; daily-only data does not support BPV as written), and several **suggestion-grade specification gaps** (threshold-regime mid-zone, ambiguous lag units, missing power-method pre-pin, inadequate Bonferroni discussion). The "anti-fishing tripwire" caveat at line 178 is correctly flagged by the author but is then **undermined** by the spec proposing ≥3 specifications on the same closed-FAIL dataset.

The good news: the author's pre-pin instinct (line 153-158) is the right discipline. It is just incomplete — several DOF remain un-pinned. Below is a concrete pre-pin checklist the author can adopt verbatim.

---

## Findings (priority-sorted)

### 🔴 BLOCKER-1 — Panel size misstatement: N=150 claimed, N=28 actual

Direction 3 (line 127, 132, 177) repeatedly states "N≈150 trading days" / "N≈150" / "~15 stress-regime observations on a 150-day panel". This is **not** what the panel contains.

Per `notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md` (lines 29, 83, 121):
- Raw weekday rows joining TRM = **29**
- Post-first-diff usable N = **28**
- The v0.2.10 audit-econ verdict was POWER-HALT at the demonstration-grade floor `N_MIN = 38`; the panel did not even clear the *demonstration* floor.

**Why this is a blocker:**
1. Every downstream calculation in §Method (threshold split, jump-count expectation, bootstrap block length, power estimate) depends on N. The author wrote those calculations for N=150 and they are all wrong.
2. At N=28, a threshold-regression split into a "stress" regime at p90 yields **2-3 observations** in stress, not "~15". OLS on 3 observations with one slope coefficient has zero degrees of freedom for residual variance estimation. The regression is mechanically undefined or rank-deficient.
3. Jump count: at daily frequency on N=28 trading days, expected jump count under standard BNS detection (z-stat > 3) is plausibly **0–2** — far below the spec's own line-163 "Jump count ≥ 10" pass criterion. The gate **mechanically cannot pass** as written.
4. Bootstrap block length ⌈T^(1/3)⌉ at T=28 = 4, not the R5 value at T=150 = 6. The "re-use R5 infrastructure" claim (line 177) is therefore wrong on its face.

**Suggestion:** Either (a) close this direction with a one-line "panel too small for jump-conditional analysis; revisit when N≥75 panel is built", or (b) re-scope to a *power-only* exercise: "given N=28 and an assumed jump-arrival rate λ, what panel size N* would be required for jump-conditional β to reach power=0.50 at MDES=0.40?" Option (b) is a feasibility memo, not a re-analysis. Pick one and commit before any notebook work.

### 🔴 BLOCKER-2 — Bipower variation at daily frequency is theoretically misapplied

The BNS (2004) bipower variation estimator is:

```
BV_t = μ₁⁻² × Σᵢ₌₂…M |r_{t,i}| × |r_{t,i-1}|
```

where `μ₁ = E|Z| = √(2/π)` for Z ~ N(0,1) so `μ₁⁻² = π/2`. **Crucially, the sum runs over M intraday returns within day t**, and consistency for IV requires M → ∞ (sampling-interval Δ → 0). At daily frequency with M=1 intraday return per "day", the formula degenerates to a single product of consecutive daily returns, which is **not** an estimator of integrated variance — it is a noisy cross-product with no jump-robustness interpretation.

The spec formula (line 144) `IV_t = (π/2) × Σ |r_t| × |r_{t-1}|` is ambiguous between two readings:
1. **Intraday reading**: Σ is over intraday increments within day t. CORRECT formula but **not implementable on this panel** — only daily TRM is available.
2. **Daily-rolling reading**: Σ is over a rolling window of daily returns t=1…T. This is **not** the BNS estimator and has **no published consistency result** in the BNS framework. It is essentially a Hodrick-rolling moving-product, which the literature calls a "realized covariance"-style smoother but does not enjoy the jump-robustness property the spec relies on.

**Why this matters:** the entire identification strategy of Direction 3 rests on separating `IV` (continuous) from `JV = max(0, RV − IV)` (jump). If `IV` is not consistently estimated, `JV` is contaminated by both continuous-variance noise and the cross-product residual. The decomposition is then operating on a quantity the author cannot defend in review.

**Suggestion:**
- **Pre-pin a specific intraday data source** OR **acknowledge daily BPV is heuristic-only**. Two acceptable resolutions:
  1. Acquire intraday TRM (or any continuous COP/USD reference price — e.g., on-chain Mento broker quotes per minute) and run BNS on intraday Δ. This is a **new data ingest** and pushes effort well beyond the 2-day budget.
  2. Drop BPV; use the Lee-Mykland (2008) daily-applicable jump test (their statistic is defined on daily returns and tests each day individually for a jump). This is what the literature recommends when only daily data is available.
- The spec's claim at line 176 ("At daily frequency (our data) the method is robust per the Barndorff-Nielsen 2004 paper") is **incorrect as a paraphrase of BNS 2004**. BNS 2004 derives robustness in the Δ → 0 limit, not at daily Δ. Cite the paper carefully or remove the claim.

### 🔴 BLOCKER-3 — Anti-fishing carry-forward conflicts with the gate design

Line 178 (correctly) flags: "this re-test is on the *same data* as the closed v0.2.10 iteration. To avoid garden-of-forking-paths inflation, we must (a) pre-pin specification before running, (b) treat as exploratory/demonstration-grade regardless of outcome unless replicated on a fresh dataset."

But the spec then proposes (§Method) **at least 3 distinct specifications** (BPV decomposition, threshold regression, asymmetric up/down), each with multiple lag arms (k=1, 2, 3), all evaluated on the same N=28 panel. That is ≥ 9 statistical tests on a panel that already failed its primary spec. By the `feedback_pathological_halt_anti_fishing_checkpoint.md` discipline, this is the textbook fishing pattern — sub-spec proliferation post-FAIL.

**Suggestion:**
- Pre-pin **one primary specification** before running anything (recommend: asymmetric up-jump β with contemporaneous-lag, Lee-Mykland detection — see pre-pin checklist below).
- All others become secondary/exploratory and **must not be quoted as evidence** even if they reach nominal significance. The disposition memo template in `memory/feedback_pathological_halt_anti_fishing_checkpoint.md` should be filed *before* notebook execution, listing the primary + secondaries explicitly.
- Add a Bonferroni-correction line: if K secondary specs are tested, the family-wise α for declaring any one "significant" must be α/K. With K=8 and target α=0.10, individual specs need p < 0.0125. State this explicitly in the spec.

### 🟡 SUGGESTION-1 — Threshold regression leaves an unanalyzed mid-regime

Line 148-149: `β_calm | rolling_30d_vol < median` and `β_stress | rolling_30d_vol ≥ p90`. The interval [median, p90) — **40% of the sample** — is unspecified. If it is silently dropped, the test is non-representative and confounds regime selection with sample selection.

**Suggestion:** Replace the two-cut threshold with one of:
1. **Hansen (1999) continuous threshold regression** with a single break-point estimated from the data + confidence interval for the threshold. Robust to mid-regime arbitrariness and provides a likelihood-based inference for the break itself.
2. **Smooth-transition (Teräsvirta 1994) regression** with a logistic transition function on rolling vol; gives a continuous β(vol) that integrates over the mid-zone.
3. **Strict tertile split** (low/mid/high) with the mid as the reference category in a single regression. Avoids the gap but at the cost of slope-difference power.

Pre-pin which one before running. The author's preferred (presumably Hansen 1999) should be stated explicitly. Note at N=28 even Hansen 1999 is under-powered — this is another argument for re-scoping.

### 🟡 SUGGESTION-2 — Lag specification: trading-day vs. month is ambiguous

Line 150: "N+k lags (k=1, 2, 3 months)". The panel is daily; "months" on a 28-row daily panel is meaningless (it would consume 21 of 28 rows as lag burn-in per arm). Two readings:
1. **Trading-day lags** k ∈ {1, 2, 3}: cost responds to FX with a 1–3 day delay (consistent with "dev defers FX conversion" intuition at line 150). Plausible at this frequency.
2. **Monthly-effect lags** k ∈ {21, 42, 63} trading days: cost-of-subscription monthly billing cycle. Not estimable on N=28.

Treat these as **separate identification claims**. Pre-pin: k ∈ {0, 1, 2, 3} trading days is the only feasible set on this panel. The "month" reading is reserved for the N≥75 fresh panel.

### 🟡 SUGGESTION-3 — Asymmetric β handling is under-specified

Line 149: "Separate up-jumps (COP depreciation) from down-jumps (COP appreciation)." Correct intuition: for a USD-cost in COP, asymmetric exposure is the *whole point* of a long-strangle hedge versus a long-call/short-put. But the spec does not specify:

1. **Definition of "jump"**: is it any FX move > k×σ, or BNS-statistic-significant jump days, or sign-of-return-conditional? Pre-pin.
2. **Conflation risk**: a simple `|FX_return|` regressor conflates magnitude and direction. The correct asymmetric spec is:
   ```
   Δcost = α + β_up · max(Δfx, 0) + β_down · min(Δfx, 0) + ε
   ```
   with the hypothesis `H₀: β_up = -β_down` (symmetric) vs. `H₁: β_up > -β_down` (asymmetric, structural). Pre-pin this specification, not the vague "separate" language at line 149.
3. **Sign expectation**: per the Y formula, `cost_COP = USD_cost × spot_COP_USD`, so `Δcost ≈ USD_cost × Δspot` for fixed USD prices. A COP depreciation (Δfx > 0, COP weakens) raises cost. Both `β_up > 0` and `β_down > 0` are predicted under proportional pass-through; asymmetry would manifest as `|β_up| > |β_down|` if conversion is delayed during appreciation episodes. State this prediction explicitly in the pre-pin.

### 🟡 SUGGESTION-4 — Power calculation method not pre-pinned

Line 151: "Power calculation under jump-conditional specification. N reduces sharply when conditioning on jumps; quantify the power penalty." This sentence is a TODO, not a method. Three concrete choices:

1. **Analytic two-sample power** (Cohen's d framework): `n_per_arm = 2(z_{α/2} + z_β)² / δ²`. Cheap and pre-committable.
2. **Monte Carlo under a pre-specified jump-arrival rate λ and effect size MDES**: simulate N=28 panels, count rejections, report power. Pre-pin RNG seed + iteration count (recommend B=10,000).
3. **Bootstrap-resampled subset power**: subset existing jumps with replacement; report empirical rejection rate. Fragile at N=28; not recommended.

Pre-pin (2) with explicit λ-assumption (e.g., λ = 0.05 jumps/day → ~1.4 jumps in 28 days, mechanically below the gate's own pass criterion of ≥10 jumps).

### 🟡 SUGGESTION-5 — Stationary bootstrap invalid on jump-subset

Line 177: "stationary-bootstrap (re-use R5 infrastructure)". R5's Politis-Romano stationary bootstrap with block length ⌈T^(1/3)⌉ was designed for T=150 (per spec's claim) — but the *actual* T=28. More importantly, applying it to the jump-subset (N_jump ≈ 1–3 expected) is statistically invalid: the bootstrap requires the resampled series to be approximately stationary and the block-length to scale with the dependence horizon, neither of which holds on a handful of jump days drawn from a non-stationary cluster.

**Suggestion:**
- Pre-pin: stationary bootstrap is **valid only for the full-sample regression** (not the jump-conditional sub-regression).
- For the jump-conditional arm, use **exact permutation inference** (permute the jump-indicator across days, B=10,000) or **conservative wild-bootstrap** with Rademacher weights. Both are defensible at small N.
- Block length should be **re-computed from the actual T**, not inherited from R5.

### 💭 NIT-1 — Pass-criterion mismatch with stated power floor

Line 162: "Jump β estimable with power ≥ 0.50 at the existing N". But Pre-pin §line 153 inherits "anti-fishing carry-forward" (project default `POWER_MIN = 0.80`). The dev_ai_cost_v2 demonstration floor is `POWER_MIN = 0.50`. State explicitly: "Direction 3 inherits the dev_ai_cost_v2 demonstration-grade floors (`N_MIN = 38`, `POWER_MIN = 0.50`), NOT the project defaults." Currently this is implicit and a reader would assume project defaults apply.

### 💭 NIT-2 — Reference paper citation incomplete

Line 145: "Barndorff-Nielsen & Shephard (2004), 'Power and Bipower Variation with Stochastic Volatility and Jumps'". Add the journal (Journal of Financial Econometrics 2(1):1–37) and DOI to the spec's decision-citation block per `feedback_notebook_citation_block.md`. Same for any Lee-Mykland or Hansen replacement: full citation + page-of-formula.

### 💭 NIT-3 — Effort estimate (2 days) is unrealistic if BLOCKER-2 resolution requires intraday data

If the author chooses "acquire intraday TRM" as the BPV-validity fix, the effort balloons from 2 days to ≥5 (data ingest + provenance audit + new SHA pin + notebook re-execute). State this conditional in the effort line.

---

## What's good

- **Pre-pin instinct is correct** (line 153-158). The author is voluntarily front-loading the sign / magnitude / lag / method commitment — exactly the discipline the anti-fishing rules require. The skeleton just needs filling in.
- **Anti-fishing self-flag at line 178** is honest and accurate. Most reviews never see authors flag their own forking-paths risk; this one does.
- **Fail criteria are tight** (line 165-168): "Jump count < 5 (mechanically uninformative)" is the right kind of pre-committed exit. The author understands the failure mode.
- **No new data ingest** is appropriately scoped *if* daily BPV were valid — the re-analysis instinct is correct as a cheap experiment. The blocker is method-validity, not scope-creep.

---

## Pre-pin checklist (concrete DOF values for the gate notebook)

Before any cell of `07_jump_conditional.ipynb` is executed, the following 14 values MUST be written in the notebook header (markdown cell #1) AND in `scratch/2026-05-18-direction-3-gating/pre_pin.md`. No value may be amended post-execution without a CORRECTIONS block per `feedback_pathological_halt_anti_fishing_checkpoint.md`.

| # | DOF | Pre-pinned value | Rationale |
|---|---|---|---|
| 1 | **Panel N** | N=28 (post-first-diff), not 150 | Per `DATA_PROVENANCE.md` line 29, 83 |
| 2 | **Demonstration-grade floors** | `N_MIN = 38`, `POWER_MIN = 0.50`, `MDES_SD = 0.40` | Inherited from dev_ai_cost_v2 v0.2.10 §2.3.1 |
| 3 | **Jump-detection method** | Lee-Mykland (2008) daily-applicable z-statistic, NOT BNS bipower | Daily Δ does not satisfy BNS Δ→0 (BLOCKER-2) |
| 4 | **Jump-detection threshold** | z > 3 (two-sided; per L-M default) | Pre-specified, not data-driven |
| 5 | **Primary specification** | Asymmetric β regression: `Δcost = α + β_up · max(Δfx, 0) + β_down · min(Δfx, 0) + ε` | Per SUGGESTION-3 |
| 6 | **Primary lag** | Contemporaneous (k=0); secondary k=1 | Per SUGGESTION-2; "month" lags out of scope |
| 7 | **Primary hypothesis** | H₀: β_up = -β_down (symmetric); H₁: β_up > -β_down (asymmetric depreciation channel) | Sign-of-test pre-committed |
| 8 | **Magnitude expectation** | β_up ∈ [0.05, 0.20] SD-units per SD of FX | Pre-pinned per spec line 156 |
| 9 | **Secondary specs (Bonferroni)** | 4 secondaries: (a) full-sample IV-only, (b) threshold-Hansen-1999, (c) k=1 lag, (d) up-only restriction. Family-wise α = 0.10 → per-spec α = 0.025 | Per BLOCKER-3 |
| 10 | **Inference method (full sample)** | Stationary bootstrap, block length ⌈28^(1/3)⌉ = 4, B = 10,000, seed = 0xABR1G0 | Per SUGGESTION-5; corrected block length |
| 11 | **Inference method (jump subset)** | Exact permutation of jump-indicator, B = 10,000, seed = 0xABR1G0 | Per SUGGESTION-5; bootstrap invalid on subset |
| 12 | **Power method** | Monte Carlo simulation under λ = 0.05 jumps/day, σ_jump = 0.015, B = 10,000, seed = 0xABR1G0 | Per SUGGESTION-4 |
| 13 | **Pass threshold** | (a) Power ≥ 0.50 at MDES=0.40, AND (b) primary p < 0.025 (Bonferroni-adjusted), AND (c) jump count ≥ 5 | Aligns with demonstration-grade floors |
| 14 | **Fail-fast exit** | If jump count < 5 OR pass-criterion (a) fails → file disposition memo + CORRECTIONS block; do NOT proceed to secondary specs | Per `feedback_pathological_halt_anti_fishing_checkpoint.md` |

### Additional pre-pin commitments (textual)

15. **No threshold tuning post-hoc.** If z > 3 yields <5 jumps, the gate FAILS. Do not lower to z > 2.5 to "rescue" the sample; that is silent fishing.
16. **No spec swapping post-hoc.** If primary asymmetric β returns insignificant, do not promote a secondary to primary. File disposition memo enumerating ≥3 pivot options (close direction / acquire intraday data / re-scope to N=75 fresh panel) and surface to user.
17. **No "directional read" rescue.** If point estimate is the predicted sign but CI contains zero, verdict is FAIL with directional informativeness footnote — NOT a soft PASS. Per `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`.
18. **Verdict-grade prohibition.** Regardless of outcome, this gate produces a **demonstration-grade** verdict only. Any "PASS" enters the queue for replication on the N≥75 fresh panel before any Stage-2 M-design work proceeds. This is required by line 178 of the spec and must be restated in the gate decision memo.

---

## Recommended next step

1. **Author resolves BLOCKER-1** by either closing Direction 3 outright (recommended given N=28) OR re-scoping to a power-feasibility-only memo (no β estimation).
2. **If re-scoping survives BLOCKER-1**, author resolves BLOCKER-2 by adopting Lee-Mykland on daily data + dropping BPV language entirely.
3. **Author commits the pre-pin checklist** (table above + textual commitments) to `scratch/2026-05-18-direction-3-gating/pre_pin.md` before any notebook cell executes.
4. **Re-review** (Code Reviewer + Reality Checker) on the revised gate spec + pre-pin file. The current spec as written is not ready for execution.

---

## Files referenced

- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-18-four-direction-gating-step-plans.md` (lines 124-181 — Direction 3 section)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md` (lines 20-44 demonstration-grade floors; line 29 N=28; lines 121-124 ccusage parity table)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/memory/feedback_pathological_halt_anti_fishing_checkpoint.md` (HALT + disposition discipline)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.10 §2.3.1 (demonstration-grade floors source-of-truth)

## External references for pre-pin (citations the notebook decision-block must carry)

- Barndorff-Nielsen, O. E., & Shephard, N. (2004). "Power and Bipower Variation with Stochastic Volatility and Jumps." *Journal of Financial Econometrics*, 2(1), 1–37. — **Cited only to acknowledge the daily-Δ limitation, NOT as the chosen method.**
- Lee, S. S., & Mykland, P. A. (2008). "Jumps in Financial Markets: A New Nonparametric Test and Jump Dynamics." *Review of Financial Studies*, 21(6), 2535–2563. — **Primary jump-detection method.**
- Hansen, B. E. (1999). "Threshold effects in non-dynamic panels: Estimation, testing, and inference." *Journal of Econometrics*, 93(2), 345–368. — **Secondary threshold-regression method.**
- Politis, D. N., & Romano, J. P. (1994). "The Stationary Bootstrap." *Journal of the American Statistical Association*, 89(428), 1303–1313. — **Full-sample inference only.**
