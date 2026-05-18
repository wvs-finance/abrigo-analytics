# Code Reviewer — Direction 1 (USD-earning Colombian Remote Workers, ADP bridge)

**Reviewer:** Code Reviewer (methodology / identification / pre-pin sufficiency)
**Target:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 1 (lines 13–65)
**Scope:** gating-step coherence — does the proposed Y, X, M, and gate produce a defensible *full iteration* if PASS? Methodology bugs that would silently sink the full spec if not caught at the gate.
**Reference patterns:** dev_ai_cost_v2 v0.2.10 (pre-pin discipline, HALT chain, anti-fishing carry-forward), `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`.

## Verdict

**CONDITIONAL_APPROVE.**

The direction is conceptually the strongest of the four (FX exposure is structural, not residual; cohort is policy-relevant; M-design has a clean Panoptic mapping). But as written, the spec ships **three identification-level defects** that would compromise the full iteration if not fixed at the gate: (1) Y is undefined as a level vs. log-difference vs. CPI-deflated quantity — three substantively different objects; (2) the level/vol distinction in X is *named* but not *operationalized*, leaving the door open to a mechanical β=1 result mislabeled as "structural"; (3) no pre-pinned sign/lag/magnitude exists for Direction 1 (Direction 3 has one — this is an inconsistency, not an oversight that can be deferred to the full iteration). These three must close at the gate (not at full-iteration spec v0.1) because they reshape the data-request memo to ADP.

Also: survival bias is unaddressed and is non-trivial for a cohort defined by *currently holding* a USD-paying job.

Approve to proceed with the gate **conditional** on a CORRECTIONS-style amendment to §Direction 1 closing the items below before the ADP memo is drafted.

---

## Critical issues (MUST fix before gate runs)

### C1. Y is three different objects — pick one and pre-pin it

The spec says `Y = usd_wage × spot_COP_USD`, "measured at cohort-aggregate level". This is a **nominal COP level**. Three candidates collapse into one symbol:

- `Y_nominal = USD_wage × spot_COP_USD` — nominal COP wage. Non-stationary, drifts with both COP depreciation and USD wage growth. Regressing this on FX vol gets contaminated by trend and inflation.
- `Y_real = (USD_wage × spot_COP_USD) / CPI_COP` — purchasing-power-equivalent COP wage. This is what the post-Keynesian wage→capital framework *actually cares about*: real wage purchasing power, not nominal headline.
- `Δlog Y = Δlog(USD_wage) + Δlog(spot_COP_USD)` — log-differenced first moment. Stationary, decomposable, the only one that admits a standard OLS-on-stationary-regressors β interpretation.

Each gives a different β with a different sign expectation and a different M-design implication. Pre-pin to **one** before the ADP memo goes out — because the ADP request fields depend on it (do we need a USD wage *deflator* series? a CPI series? both?).

**Recommendation:** primary Y = `Δlog(USD_wage × spot_COP_USD)` (log-differenced nominal COP wage), with `Δlog((USD_wage × spot_COP_USD)/CPI_COP)` as the deflated secondary. Pre-pin in the gate write-up.

### C2. The level-vs-vol distinction is named but not operationalized

The X bullet says "COP/USD spot level *and* realized volatility (both channels matter — level for one-shot conversion timing, vol for path uncertainty)." This is correct in spirit but **mechanically loaded**:

- For a worker paid USD on the 15th and converted the same day, `COP_wage_t = USD_wage_t × spot_t` — the β on contemporaneous spot is **identity (=1)**, not behavior. This β is not informative about FX exposure; it's just the conversion formula.
- The structural β lives in the **vol component** *or* in the **lagged-conversion behavior**: when do workers convert vs. hold USDC? do they smooth conversion across the month? do they accumulate during low vol and spend during high vol?

If the full iteration regresses `Y_nominal` on `spot_t` and reports β ≈ 1 as "FX transmission confirmed", that is a tautology, not a finding. The R5 dev_ai_cost_v2 lesson is exactly this: a mechanical-identity β is not the same as a behavioral β.

**Recommendation:** at the gate, pre-commit to the **primary** β being on either (a) realized FX volatility, (b) FX *jump* component (per Direction 3 bipower machinery — reusable), or (c) a *behavioral* conversion-timing model (e.g., `Δlog Y_real` on lagged FX vol). Spot level as primary is anti-fishing-banned because it produces a tautological β.

### C3. No pre-pinned sign / magnitude / lag — must close at the gate, not later

Direction 3 of the same document explicitly pre-pins (§ "Pre-pin (anti-fishing)") before any regression runs. Direction 1 does not. This is structurally inconsistent and violates the anti-fishing carry-forward stated in the cross-direction §Anti-fishing carry-forward block.

The gating step itself does not run β regressions, so a gate-level pre-pin is not *technically* required by the anti-fishing protocol. **But** the gate produces the data-request memo to ADP, and the fields requested in that memo encode an implicit specification choice (e.g., requesting percentile distribution p10–p90 commits to heterogeneity-sensitive estimation; requesting only the mean commits to cohort-aggregate). Defer pre-pin to the full iteration and the data-request memo will be under-specified or over-specified.

**Recommendation:** the gate write-up MUST include a pre-pin checklist (see end of this review) before the ADP memo leaves the building. Treat the pre-pin as a load-bearing artifact, not a deferred concern.

### C4. Survival bias — the cohort definition selects on outcome

"Colombian workers currently paid USD by foreign employer" is a *survivor* cohort. Workers who lost their USD-paying job exit the cohort; the cohort's measured wage volatility is the volatility of those who kept the job, not the volatility of the population that *entered* the USD-paid labor pool.

Implications:
- Cohort-aggregate wage volatility is biased *downward* (job-loss-induced volatility is censored).
- The transmission channel of FX vol → wage may operate via *exit* (worker fired when COP appreciation makes them too expensive in USD-equivalent) rather than via wage adjustment. The β-on-survivors misses this.
- The policy story ("FX vol hurts USD-paid workers") may be empirically supported even when the within-cohort β is small, because the cost shows up in exit rates not wage moves.

**Recommendation:** the ADP data request must include **monthly cohort headcount churn** (entries + exits), not just stock. The full iteration must either (a) model entries/exits as a secondary Y, (b) condition on a balanced sub-cohort with > N months continuous USD pay, or (c) explicitly scope the β as "within-survivor" and acknowledge the bias in the verdict. Pre-commit at the gate.

---

## Strong recommendations (SHOULD fix)

### S1. M-direction check: long-USDC / short-COPm protects against COP *strengthening*

The M sketch (line 18) says "Hedge protects against COP appreciation eroding COP-converted wage." Let's verify the sign.

- Cohort earns USD; converts to COP for spending.
- COP **appreciation** (lower COP/USD, fewer COP per USD) → COP wage **falls** → bad for cohort.
- Long-USDC / short-COPm position: gains when USDC appreciates vs COPm, i.e., when COP weakens vs USD. **This is the wrong direction for the stated risk.**

The cohort's structural risk is COP **strengthening** (each USD buys fewer COP). The hedge that pays out on COP strengthening is the opposite leg: **long-COPm / short-USDC** (gain when COP gains).

Either:
- The M sketch sign is wrong (most likely — re-check)
- Or the cohort's risk was misstated (the spec says "appreciation eroding wage" which is correct directionally)

**Recommendation:** fix the M direction. Long-COPm / short-USDC, or equivalently a long-COPm-call / long-USDC-put structure on the USDC/COPm Panoptic pool. Verify against a worked numerical example in the gate write-up before it propagates to the full spec.

### S2. Cohort-aggregate vs individual heterogeneity — aggregate β may not be enough for M-design

The spec measures Y "at cohort-aggregate level, not individual level" (line 16). This is appropriate for the empirical-β feasibility test (more degrees of freedom, less measurement noise). But the M-design step downstream consumes the β as a **per-capita hedge size**:

> "the M-design hedge must absorb $Y$ COP of cost-burden variance per month"

If the aggregate β = 0.10 but individual β has bimodal distribution (a tail of workers with β = 0.5 and a mode at β ≈ 0), the aggregate hedge is **mis-sized for both groups**. The premium-funded ratchet only works if the hedge is matched to the individual's actual exposure.

The ADP percentile fields (p10/p25/p50/p75/p90 of monthly USD pay) are listed in the data-input ask, but the spec doesn't explain how they feed back into β heterogeneity estimation. They give pay-size heterogeneity, not β heterogeneity directly, but they're the entry point for a quantile-regression β.

**Recommendation:** add to the gate write-up: "If the full iteration is dispatched, the primary β is cohort-aggregate; a secondary specification estimates β at p25/p50/p75 of pay-size strata (proxy for individual β heterogeneity)." This commits the data-request to include enough granularity to support the secondary spec.

### S3. Banrep BoP backstop has aggregation level mismatch

The Banrep BoP services-exports `servicios informáticos y de información` line is proposed as a public fallback (line 33). This series captures **total USD inflow at the macroeconomy level** — exporters' billing, not workers' wages. It includes:
- Software-company export revenue (employer side, not worker side)
- Consulting fees paid to Colombian *firms* by foreign clients
- Some pass-through to worker wages (the relevant component)

The pass-through rate from this aggregate to actual worker wages is unknown and possibly time-varying. Using this as a Y proxy without an explicit pass-through model would conflate three different processes: foreign demand, firm margins, and wage share.

**Recommendation:** if Banrep BoP becomes the primary Y source (ADP and DANE both fail), the full iteration must explicitly model the BoP-to-wage pass-through. The gate write-up should flag this as a critical assumption to validate before dispatching the full iteration. Currently the spec treats Banrep BoP as a clean backstop; it is not.

### S4. DANE GEIH 2018–2022 coverage gap acknowledged but not mitigated

Line 62 correctly notes that DANE GEIH likely lacks a foreign-employer identifier pre-2022 → series may only start ~2022 → N borderline for monthly ≥ 75. This is a known limitation but the spec doesn't propose what happens if the panel arrives at N=48 (4 years of monthly data, 2022→2026):

- N=48 < N_MIN=75 (Abrigo invariant) → would force a demonstration-grade vs verdict-grade scope decision (per dev_ai_cost_v2 §2.3 framing).
- Could go demonstration-grade with explicit power disclosure.
- Or extend to weekly granularity to lift N (≈ 200 weeks) at the cost of higher noise.

**Recommendation:** pre-commit in the gate to the action under N=48: either (a) demonstration-grade with disclosure, (b) weekly upsample, or (c) close direction. The decision shouldn't be made after seeing the data.

### S5. Conversion-timing decision is the actual interesting object — model it explicitly

Once C2 is fixed (level β is identity, vol β is the structural object), the question becomes: *why* would FX vol affect COP-realized wage at all? The mechanism is the worker's **conversion-timing decision**:

- If worker converts USD → COP on payday (mechanical, no discretion), then `cov(Y, vol) = 0` modulo noise.
- If worker holds USDC and converts opportunistically, then `cov(Y, vol)` reflects timing skill (or lack thereof).
- If worker is forced to convert by liquidity needs (e.g., COP rent), then `cov(Y, vol)` reflects the constraint, not skill.

These are three different stories with three different M-design implications:
- Story 1: hedge is unnecessary (no exposure to vol).
- Story 2: hedge competes with worker's own timing alpha — premium must beat the skill.
- Story 3: hedge substitutes for the missing optionality — premium-funded ratchet narrative is strongest here.

**Recommendation:** the ADP data-request should include **conversion-frequency proxy** (does ADP show currency of payment on the worker side? does the cohort have a tracked currency-of-conversion?). If not in ADP, propose surveying via a Bumeran / Mercer add-on. Without this, the β interpretation will be ambiguous between the three stories.

---

## Nits (MAY fix)

### N1. "USD wage × spot COP/USD" — clarify the spot timing convention

Spot at payment date? Spot at month-end? Average over month? Worker's actual conversion-date spot (likely not observable)? Each choice gives a slightly different β. Pre-pin the spot convention in the gate write-up (most natural: spot at payment date if ADP records payment date; month-end TRM otherwise — match Banrep's published convention for cross-source comparability).

### N2. SOC top-3 industry banding — confirm ADP exposes SOC

ADP US uses SOC for payroll classification, but ADP Colombia (if it's a separate product) may use Colombian SCIAN-equivalent codes. Verify the banding system before drafting the memo. Mismatched code systems waste a memo cycle.

### N3. "Payment frequency mix" feeds M roll cadence — make the dependency explicit

The spec mentions biweekly/monthly mix affects M roll cadence (line 29). It would help downstream if the gate write-up included a one-line spec of "if biweekly share > X%, M is 2-week-roll Panoptic position; otherwise monthly-roll." This is M-design territory but the data ask anticipates it.

### N4. Cohort growth ≥ 5% YoY policy-relevance criterion (line 47) is unanchored

Where does 5% come from? Is this a published Abrigo threshold or an ad-hoc bar? If ad-hoc, document the reasoning briefly. If borrowed (e.g., DANE's "emerging sector" definition), cite. Otherwise looks like a tunable threshold and the next reviewer will flag it.

### N5. The "ideal-scenario M sketch" caveat is honored, but the Panoptic pool existence is asserted

Line 18 says "long-USDC / short-COPm position on the Mento USDC/COPm Panoptic pool". Per CLAUDE.md, ideal-scenario modeling is permitted, but the gate write-up should briefly flag: does the USDC/COPm Panoptic pool exist *today*, or is its existence part of the ideal scenario? If it doesn't exist, the M sketch is doubly-ideal (the pool *and* the liquidity), which is fine for empirical-β work but should be transparent.

---

## Pre-pin checklist for the full iteration spec

The following MUST be written down and committed (in `scratch/2026-05-XX-direction-1-gating/gate_decision.md` or an attached pre-pin appendix) **before any β regression runs** in the full iteration. Concrete values, not placeholders.

### Y (outcome)
- [ ] **Primary Y**: `Δlog(USD_wage_t × TRM_t)` — log-differenced nominal COP wage, monthly frequency.
- [ ] **Secondary Y**: `Δlog((USD_wage_t × TRM_t) / CPI_COP_t)` — real (deflated) COP wage.
- [ ] **Spot convention**: monthly-average TRM (Banrep published series), payment-date if ADP exposes it. Pre-pin to one — no post-hoc choice.

### X (regressor)
- [ ] **Primary X**: realized monthly FX volatility, `σ_t = √(Σ_{d ∈ month_t} r_d²)` where `r_d = Δlog TRM_d`.
- [ ] **Secondary X**: FX jump component via Barndorff-Nielsen bipower (reuse Direction 3 machinery — no Lee-Mykland alternative). Pre-pinned to BN bipower.
- [ ] **Banned as primary**: spot **level**. Primary regression on level produces tautological β ≈ 1 (mechanical identity). Level is permitted only as a control or in the deflated secondary.

### Sign expectation
- [ ] **Primary β** (Y on vol): **negative** (`β_vol < 0`). Reasoning: FX vol creates conversion-timing uncertainty; the survivor cohort cannot perfectly time; expected utility-equivalent realized wage falls in high-vol months even if mean is preserved. (This is the structural channel; if β ≈ 0 we close the direction or pivot to the conversion-timing-behavior story.)
- [ ] **Secondary β** (Y on FX jump, asymmetric): **negative on COP-appreciation jumps**, **positive on COP-depreciation jumps**, asymmetric magnitudes (loss-aversion / cash-flow-constrained convertibility).

### Magnitude expectation
- [ ] **Primary β magnitude floor**: `|β_vol| ≥ 0.10 SD-units of Y per SD-unit of σ`. Below this, declare "FX vol channel structurally weak for this cohort" and close.
- [ ] **MDES**: 0.40 SD-units (Abrigo invariant — non-negotiable).

### Lag
- [ ] **Primary lag**: contemporaneous (`vol_t → Y_t`).
- [ ] **Secondary lag**: `k = 1` month (`vol_{t-1} → Y_t`) for delayed-conversion behavior.
- [ ] **Banned**: k > 3 (anti-fishing — long-lag specifications are post-hoc-prone).

### Panel structure
- [ ] **N target**: ≥ 75 monthly observations (Abrigo invariant). If only N=48 available (DANE 2022→2026 case), declare **demonstration-grade** explicitly per dev_ai_cost_v2 §2.3 — POWER_MIN drops to 0.50, verdicts labeled PARTIAL-* until panel extends.
- [ ] **Demonstration-grade threshold**: documented in spec, not chosen post-hoc.

### Survival-bias controls
- [ ] **Cohort definition**: pre-commit to one of:
  - (a) "All workers with ≥ 1 USD pay in month t" (open cohort, includes entries/exits)
  - (b) "Balanced sub-cohort: workers with ≥ 24 consecutive months of USD pay" (closed cohort, survivor bias acknowledged)
- [ ] **Entry/exit Y**: include monthly cohort headcount churn as a secondary Y. Regress entries and exits on FX vol/jumps separately. If primary β on wage is small but entry/exit β is large, the structural story holds via the labor-market channel, not the wage-channel.

### Heterogeneity
- [ ] **Primary**: cohort-aggregate β.
- [ ] **Secondary**: pay-size-stratum β (p25, p50, p75 of monthly USD pay) — quantile-style β for M-position sizing heterogeneity.

### M-direction
- [ ] **Pre-committed M leg**: long-COPm / short-USDC on USDC/COPm Panoptic pool (hedges against COP **strengthening**, the cohort's structural risk).
- [ ] Fix the spec text on line 18 — currently states the wrong direction.

### HALT triggers (anti-fishing carry-forward)
- [ ] Spec-vs-data contradiction (e.g., primary β sign flips, or panel N falls below floor) → HALT + disposition memo + ≥3 user pivot options + CORRECTIONS block + 3-way review. No silent threshold tuning. Per `feedback_pathological_halt_anti_fishing_checkpoint.md`.
- [ ] Threshold tuning post-hoc: anti-fishing-banned. Any change to pre-pinned values above requires a CORRECTIONS block citing (old, new, preserved-guarantees-argument, commit anchor).

---

## Summary one-liner

**Direction 1 is the most promising of the four (structural FX channel, policy-relevant cohort, clean M-mapping), but it ships with three identification defects (Y ambiguity, level-vs-vol tautology risk, missing pre-pin) and one design defect (M-direction sign) that must close at the gate, not at the full-iteration spec. Survival bias and conversion-timing behavior are real structural concerns that the data-request memo must anticipate.** CONDITIONAL_APPROVE pending closure of items C1–C4 and S1 in the gate write-up.
