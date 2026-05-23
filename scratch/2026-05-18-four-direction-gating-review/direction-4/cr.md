# Code Reviewer — Direction 4 (USDC-Saver Colombian Cohort)

**Reviewer lens:** methodology / econometrics / identification
**Target:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` § Direction 4
**Verdict:** **CONDITIONAL PASS** — gate is *operationally* runnable in 3 days, but the methodology section has **3 blockers** and **4 suggestions** that must be resolved BEFORE the gate is executed, otherwise the gate output will not be sufficient to spawn a full iteration with the Abrigo anti-fishing invariants intact.

---

## Summary

The Direction 4 gate asks the right *feasibility* questions (cohort size, AUM, depeg event count) but the **methodology underwriting the eventual β-estimate is under-specified to a degree that the gate could pass on data-availability grounds while the full iteration would HALT on identification grounds within Phase 1.** Specifically: the Y conflates two distinct risk channels (depeg + FX), the EVT method has 3+ pre-pin DOF unaddressed, the M-design verb ("short-tail") is directionally ambiguous, and the event-N (not cohort-N) is the binding identification constraint and is not surfaced in the pass/fail criteria. Direction 4 also has **zero pre-pin** of sign / magnitude / lag, while Direction 3 in the same spec has a full pre-pin block — this is an inconsistency the spec should resolve.

What is good: data-source triangulation (Bitso / Lemon / Buenbit / Dune) is sensible; the cohort-AUM × event-count product gate is the right shape; the descope of paid analytics (Arkham) preserves reproducibility-tier discipline; the 3-day effort budget is realistic for the data-pull portion.

---

## Blockers (must fix before gate runs)

### B1. 🔴 Compound-Y conflates two risk channels — β is not identified on the novel X

**Where:** Line 188 — `Y = usdc_balance × usdc_usd_price × spot_COP_USD`.

**Why this is a blocker:** Direction 4's novel risk channel — and the entire reason to dispatch this iteration separately from Direction 1 (which is already the COP/USD channel) — is **USDC depeg** (`usdc_usd_price ≠ 1`). But the Y as written multiplies through by `spot_COP_USD`, which means a β estimated on depeg-X will be **contaminated by FX moves on depeg days**. This is not hypothetical: the canonical USDC depeg event (2023-03-10/11, SVB) coincided with broad USD strength and a COP/USD spike — the two regressors are mechanically correlated on the very days where identification is supposed to come from.

If the gate passes and a full iteration is spawned with this Y, Phase 1 of that iteration will need to either (a) drop one channel (and then the iteration is no longer about depeg) or (b) run a two-factor regression with N≈3-10 depeg events — instantly violating N_MIN=75 power floor on the depeg coefficient.

**Suggestion:**
- **Decompose Y into the depeg-isolated channel:** `Y_depeg = (usdc_usd_price - 1) × usdc_balance × spot_COP_USD`. The `spot_COP_USD` factor remains as a *units* conversion to COP (so the wage-earner relevance is preserved) but the *variation* in Y_depeg is now driven only by USDC's deviation from peg, not by FX. The β on depeg-X is then identified on the channel of interest.
- Add a secondary specification `Y_FX_baseline = 1 × usdc_balance × (spot_COP_USD - spot_COP_USD.mean())` to confirm Direction 1's FX channel is being captured separately, not double-counted here.
- The spec should state explicitly that **Direction 4's β is on depeg-only**; FX channel belongs to Directions 1/3.

---

### B2. 🔴 EVT method choice has 3+ unspecified DOF — pre-pin block is missing

**Where:** Line 207 — "if depeg events are too rare for a daily-panel β estimate, propose alternative — extreme-value-theory tail β rather than mean-regression β."

**Why this is a blocker:** EVT is not a single method. The line above silently grants the gate-runner three or more researcher degrees of freedom that, if exercised post-hoc, are textbook silent-fishing per `feedback_pathological_halt_anti_fishing_checkpoint.md`:

1. **Estimator family:** GPD (peaks-over-threshold) vs. Hill vs. Pickands vs. block-maxima GEV. Each gives different tail-index estimates on the same data.
2. **Threshold choice u:** for POT, the threshold above which observations are "tail." Standard practice is mean-excess plot + Hill plot to pick u; both have visual-judgment DOF. Choices of u = 0.5%, 1%, 2%, 5% deviation from peg will give materially different β estimates.
3. **Tail-index inference:** asymptotic SE vs. bootstrap vs. profile-likelihood CI. Direction 3's pre-pin already commits to stationary-bootstrap for the threshold-regression; Direction 4 has no equivalent commitment.
4. (Optional 4th) **Stationarity assumption:** standard EVT requires stationary tail behavior — see B3 below.

Direction 3 has a complete pre-pin block (line 154-159: sign / magnitude / lag / decomposition method). Direction 4 has **none**. This is an internal inconsistency in the spec and a direct anti-fishing-invariant violation if carried into the full iteration.

**Suggestion:**
- Add a pre-pin block to Direction 4 modeled on Direction 3's:
  - **Estimator:** pre-commit to GPD-POT (most common, asymptotically grounded under regularity).
  - **Threshold u:** pre-commit to u = 0.5% deviation from peg (i.e., |usdc_usd_price - 1| ≥ 0.005), or pre-commit to a *rule* like "u chosen at the 90th percentile of absolute deviation in the calm regime 2020-01 → 2023-02."
  - **Inference:** stationary bootstrap with B=10,000 resamples, identical to R5 infrastructure.
  - **Sign expectation:** tail-β of cohort-aggregate Y_depeg with respect to depeg-X is positive (depeg destroys USDC value 1:1; the β should be at least the cohort's USDC-share of balance).
  - **Magnitude expectation:** ≥ 0.5 in dollar-elasticity terms (tight prior from accounting identity).

---

### B3. 🔴 M-design verb is directionally ambiguous — "short-tail Panoptic position" is the wrong direction for the cohort

**Where:** Line 190 — `M = short-tail Panoptic position on the USDC/USDT pool. Pays out on USDC depeg events.`

**Why this is a blocker:** "Short-tail" in derivatives language conventionally means *short the tail* — i.e., **sell** tail-protection premium, **collect** carry in calm regimes, and **lose** money on depeg events. That is exactly the wrong direction for the cohort. A Colombian USDC-saver is **already structurally short the tail** by virtue of holding USDC; the *hedge* that converts them from short-tail to neutral is a **long-tail** position (buy depeg protection, pay premium in calm, get paid on depeg).

The next sentence ("Pays out on USDC depeg events") confirms the *intended* direction is long-tail. So the language is inconsistent with itself.

For Panoptic specifically: on a USDC/USDT pool, the depeg-protection structure would be a **long out-of-the-money put on USDC** (or equivalently a long call on USDT) — i.e., a Panoptic option that pays when the pool price moves away from 1. Calling this "short-tail" because the cohort is short-tail is a category error: M describes the *hedge*, not the *underlying exposure*.

**Suggestion:**
- Rewrite line 190 to:
  > **M (ideal-scenario sketch):** *long-tail* Panoptic position on the USDC/USDT pool — a long OTM put on USDC (or equivalent long-gamma structure) struck at e.g. $0.99 or $0.98 USDC/USDT. Pays out on USDC depeg events; premium is funded by cohort-side USDC yield (Aave/Compound/Moonwell USDC supply rate, currently ~3-5%).
- Make the premium-funded-ratchet mechanism explicit (the original spec does not say where the premium comes from, even though the cohort earns 3-5% USDC yield natively — this is the natural premium source and should be specified).

---

## Suggestions (should fix before gate runs)

### S1. 🟡 Stationarity assumption pre- vs post-March-2023 needs explicit treatment

USDC depeg behavior pre-March-2023 and post-March-2023 is plausibly non-stationary. Pre-SVB, the market priced USDC as effectively pegged; post-SVB, depeg risk is a named, traded, monitored phenomenon (USDC/USDT basis is now watched continuously). Tail behavior, depeg frequency, and the speed of repeg are all plausibly different across this break.

Standard EVT assumes **stationary tail behavior**. If the regime shifted on 2023-03-10, then fitting one GPD to the full 2018-09 → 2026-05 series is mis-specified.

**Suggestion:** Pre-commit (in the pre-pin block from B2) to either (a) fit two regimes separately and report both, with a Chow-style structural-break test as the primary diagnostic, or (b) restrict the sample to post-2023-03-15 (loses the March-2023 event itself, but ensures stationary tail behavior in the estimation window — at cost of event-N).

### S2. 🟡 Event-N vs cohort-N — the binding constraint is not the gate's PASS criterion

The pass criterion at line 213 ("Historical USDC depeg events of magnitude ≥ 0.5%: count ≥ 20") correctly identifies event-N as the relevant N, but the *Risk* section at line 229 admits "The β estimate may be effectively driven by a single event — fragile identification."

The spec needs to surface this contradiction. Specifically: in the historical record, depeg events of ≥ 0.5% magnitude are dominated by 2023-03-10/11 (the actual ≥ 1% breach) plus a handful of intra-day wobbles. "Count ≥ 20" is plausibly achievable only by counting **intra-day** ≥ 0.5% wobbles on a sub-daily price series — which then drags in microstructure-noise issues that EVT at sub-daily frequency is sensitive to (Barndorff-Nielsen 2004 §5).

**Suggestion:**
- Disambiguate: is the depeg-event count measured at daily closing price, daily-low (intraday extremum), or per-trade?
- Pre-commit (before the gate runs) to one of those frequencies.
- If the daily-close count is < 5, the gate should FAIL even if intraday-extremum count is ≥ 20 — because the M-payoff settles on Panoptic at the pool's continuous price, which after fee adjustments and gas friction is closer to daily-close than to intraday-tick.

### S3. 🟡 Cohort-N is statistically irrelevant to β; the spec should say so

The PASS criterion mixes cohort-AUM ≥ $5M, distinct-addresses ≥ 10K, and event-N ≥ 20 — but only the third is an input to the β-estimate. The first two are *policy-relevance* criteria (does this cohort matter for Abrigo's inequality-reduction thesis?), not *identification* criteria.

This is fine in principle (Abrigo gates on both relevance and feasibility), but the spec should label each criterion as policy-relevance vs identification, so the gate-runner can't conflate "we have 10K wallets so N is fine" — they're orthogonal. Without this labeling, a reviewer downstream could mis-read the gate output as N=10,000 when in fact N is the count of depeg events, plausibly N ≤ 5.

**Suggestion:** Re-label the PASS-criteria bullets:
- (policy-relevance) Cohort AUM ≥ $5M
- (policy-relevance) Distinct addresses ≥ 10,000
- (identification) Depeg-event count ≥ 20 daily-close observations ≥ 0.5% deviation

### S4. 🟡 Premium-funded-ratchet mechanism for USDC-savers is uniquely clean — call it out

Unlike Directions 1, 2, 3 — where the premium-funding source requires construction (a wage-conversion overlay, or a tariff-margin overlay, or a cost-side covered yield) — the USDC-saver cohort has a **native, observable, continuous premium source**: the USDC supply yield on Aave/Compound/Moonwell/etc., currently ~3-5% APY and historically observable since 2020. This is structurally the cleanest premium-funded-ratchet of the four directions and the spec under-sells it.

**Suggestion:** Add to the M-design section: "Premium-funded ratchet: Aave/Compound USDC supply yield is observable on-chain since 2020-12; historical mean ≈ 3.2% APY, sufficient to fund a continuously-rolled OTM-put position on USDC/USDT at typical CFMM IV without out-of-pocket cohort outlay. The ratchet *self-finances* — the cohort's existing yield converts depeg-protection cost into a yield-haircut rather than a wage-deduction."

---

## Nits

### N1. 💭 Liu et al. 2023 citation (line 201) — verify the citekey

"The Anatomy of a Run" is the title of multiple papers (there's a 2023 paper by Liu, Makarov, Schoar on stablecoin runs; there's also an older Diamond-Dybvig-tradition paper). Pin the citekey and check it's the stablecoin one.

### N2. 💭 USDC vs USDT-as-numeraire choice

The X is specified as `USDC/USDT spot price deviation from 1.0000`. But March 2023 was a *USDC* depeg event, not a USDT one — USDT held its peg while USDC fell. So the ratio moved because of USDC's numerator. If a future depeg is on the USDT side (USDT has its own historical wobbles, e.g. 2018-10), the same ratio would move in the opposite direction and the cohort's exposure is unaffected (they hold USDC, not USDT). Consider specifying the X as `usdc_usd_price` (from CoinGecko's USD-denominated USDC quote) rather than the ratio, so the cohort-relevant direction is preserved.

### N3. 💭 Direction 4 gate-output filename uses placeholder `2026-05-XX`

Line 232 has `scratch/2026-05-XX-direction-4-gating/`. The current scratch directory at `scratch/2026-05-18-four-direction-gating-review/direction-4/` is for the review, not the gate execution. The gate-execution directory should be created at gate-run time with the actual date; the spec's placeholder is fine.

---

## Pre-pin checklist (must be populated BEFORE gate runs)

Direction 4 has zero pre-pin in the current spec. Direction 3 has a full pre-pin block. To bring Direction 4 to parity:

- [ ] **Y specification:** `Y_depeg = (usdc_usd_price - 1) × usdc_balance × spot_COP_USD` (per B1). Pre-commit at gate-spec revision, not at gate-execution.
- [ ] **X specification:** `X = usdc_usd_price` (CoinGecko USD-denominated, daily close). NOT the USDC/USDT ratio (per N2).
- [ ] **Sign expectation:** β > 0 on Y_depeg ~ (X − 1). (When USDC depegs downward, cohort COP-realized savings fall — direct accounting identity, so this is a tight prior, not a discovery.)
- [ ] **Magnitude expectation:** β ∈ [0.5, 1.0] in dollar-elasticity terms (accounting identity floor: 1.0 minus any partial-redemption hedge already in the cohort's holdings).
- [ ] **Lag specification:** contemporaneous primary; 1-day lag as secondary (depeg moves are intra-day-fast; lagged response would indicate redemption-queue friction, which is a secondary story).
- [ ] **Estimator:** GPD peaks-over-threshold (per B2). Not Hill, not Pickands, not block-maxima GEV.
- [ ] **Threshold u:** 0.5% absolute deviation from peg, OR 90th percentile of `|usdc_usd_price - 1|` in the calm-regime training window 2020-01 → 2023-02 — pre-pinned, not chosen by mean-excess-plot inspection at run time.
- [ ] **Inference:** stationary bootstrap, B=10,000, identical to R5 infrastructure (re-use, do not re-invent).
- [ ] **Stationarity handling:** pre-pin whether to (a) fit pre-2023-03-15 and post separately and report both, or (b) restrict to post-2023-03-15 only (per S1). Recommend (a) with Chow-style break diagnostic.
- [ ] **Event-count frequency:** daily close (per S2). Intraday tick counts do not qualify.
- [ ] **M-direction:** long-tail (long OTM put on USDC) — *not* short-tail (per B3).
- [ ] **Premium source:** Aave/Compound USDC supply rate, contemporaneous-rolling 30d mean (per S4).
- [ ] **PASS-criterion labeling:** policy-relevance vs identification (per S3).

When the pre-pin checklist is populated and committed in a spec-revision with a CORRECTIONS block (per `feedback_pathological_halt_anti_fishing_checkpoint.md`), Direction 4 is ready to run its gate.

---

## Files referenced

- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-18-four-direction-gating-step-plans.md` (lines 185-232, Direction 4 section; lines 154-159 Direction 3 pre-pin block for comparison)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/memory/feedback_pathological_halt_anti_fishing_checkpoint.md` (anti-fishing invariants binding on the full iteration)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/CLAUDE.md` (N_MIN=75, POWER_MIN=0.80, MDES_SD=0.40 invariants)

## Recommended next step

**CONDITIONAL PASS** — the spec is structurally sound but methodologically under-specified. Block gate execution until the Pre-pin checklist above is populated and committed in a revision of `docs/specs/2026-05-18-four-direction-gating-step-plans.md` § Direction 4. Estimated revision effort: 0.5 working day. The 3-day gate budget then proceeds unchanged.
