# Model-QA Review — E10 GSPS v0.2 Convex Multi-Currency Design

**Reviewed artifact:** `docs/specs/2026-05-20-e10-gsps-v0.2-convex-multicurrency-design.md` (v0.2 DRAFT, 330 lines)
**Reviewer role:** Model QA Specialist — econometric / simulation-design soundness (content-matched second reviewer per `feedback_review_pair_specialist_by_content.md`; Reality Checker owns feasibility in parallel)
**Date:** 2026-05-20
**Posture:** read-only. No spec edits, no code, no simulation runs. Algebra verified by hand (sympy unavailable in env).

---

## Verdict: NEEDS WORK

The v0.2 reframe (directional → convex, single → multi-currency) is structurally the right move and the anti-fishing scaffolding is intact. But the **central object — the FX-variance share — is not the externally-valid quantity the spec claims it is**. Because Q is fully simulated and the share is a monotone function of the simulator's Q-volatility calibration, the PASS/FAIL verdict is determined by a calibration choice the spec has not yet pinned, not by nature. This is a **Critical** defect that the demonstration-grade posture mitigates but does not resolve, because the spec still routes the share through the §9 verdict ladder as if it were an empirical finding. Combined with the unjustified 0.30 threshold and the un-identified `Q_low`, three Critical findings block a v0.3 PASS.

**Critical count: 3.**

---

## Critical findings

### C-1 — The FX-variance share is mechanically determined by the simulator's Q-volatility calibration, not by nature; the §9 verdict ladder treats it as empirical.

**Model claim.** §4.3 / §7 field 2: the FX-variance share `Var(logFX) / Var(log cost)` is "the only object that distinguishes FX risk from query-volume noise," and §9 routes it through a four-rung PASS/PARTIAL/FAIL/NON-RETIREMENT ladder. §4.2 frames "Q is stochastic" as what "makes the question real."

**Defect.** The decomposition is `Var(log cost) = Var(logQ) + Var(logFX) + 2·Cov(logQ,logFX)` (exact — see Algebra note below). The share is therefore

```
share = Var(logFX) / ( Var(logFX) + Var(logQ) + 2·Cov )
```

`Var(logFX)` is real (central-bank data). `Var(logQ)` and `Cov` are **100% simulator outputs** — they are whatever the R6 NHPP intensity dispersion and the Q–FX coupling are calibrated to. `∂share/∂Var(logQ) < 0`: the share falls monotonically as the simulator's Q-volatility rises. Whoever sets the NHPP overdispersion sets the share, and hence the verdict. The §4.2 claim that "Q being stochastic makes the question real" is half-true: Q being stochastic makes the share *non-degenerate* (escaping the §4.1 trivial-β), but it does not make the share *empirically identified* — it relocates the trivial mechanical dependence from "β trivially positive" to "share trivially equal to whatever the Q-calibration implies." The spec has swapped a trivial numerator-on-numerator regression for a share whose denominator is half-fabricated. §11 item 5 (representative-analyst) and item 2 (`Q_low`) both touch this but neither names the core problem: **the decisive object is a function of free simulator parameters.**

**What would fix it.** Two acceptable resolutions, pick one and pre-pin it:
(a) Demote the share from a *verdict object* to a *calibration-sensitivity surface*. Report the share as a function of the Q-volatility calibration (a curve, not a number), pre-pin the calibration anchor exogenously (C-3 / F-2 below), and state the verdict as "for Q calibrated to [observed anchor], the share is X" — never "the share is X" unqualified. The §9 ladder must then be re-pinned against the *anchored* share with the calibration frozen before any run.
(b) Make `Var(logQ)` itself an empirical quantity: calibrate the NHPP to a real, observed multi-analyst query-volume panel (even a small one) so the denominator is not free. The spec currently has no such anchor (see C-3).
Until one is done, the §9 ladder is reporting a property of the simulator as a property of the cohort. The methods-paper §5 hook (§12) inherits this: "validated on a simulated cohort" is only honest if the simulation's variance ratio is anchored, not chosen.

### C-2 — The 0.30 material-share threshold is an unanchored round number and is the single most consequential pre-pinned value.

**Model claim.** §7 field 3 / §11 item 4: FX-variance share ≥ 0.30 is the "pre-pinned material floor"; §9 makes it the PASS/PARTIAL boundary; the spec admits the rationale is "materiality," not a power calculation.

**Defect.** 0.30 is asserted, not derived. The spec's own §11 item 4 flags this and asks the reviewer to rule. My ruling: **0.30 is not defensible as currently stated.** The decision the threshold supports is "is a convex FX hedge the right instrument for this cohort?" That decision has a *natural economic anchor the spec ignores*: a long-gamma straddle (the §13 M-sketch) is worth buying when its expected convex payoff covers its stream-funded premium. The break-even FX-variance share is the share at which the straddle's expected payoff (a function of realized FX variance and the strike geometry) equals the premium cost (≤ 10% of stream notional per v0.1 §6.2). That break-even share is computable from the M-side payoff economics — it is *the* correct floor. 0.30 has no relationship to it; it is a convenient round number that happens to sit between "trivial" and "dominant." Worse, because of C-1, a threshold on a simulator-determined quantity is doubly arbitrary: a number with no economic anchor, applied to an object with no empirical anchor.

**What would fix it.** Derive the floor from the hedge economics, not from "materiality." Concretely: in the Stage-2 M-sketch (§13), compute the FX-variance share at which the straddle's expected payoff covers its premium under the pinned strike/range geometry and the pinned premium fraction. Pre-pin *that* number as field 3. If it lands near 0.30, fine — but it must be derived, and the derivation must be in the spec before the pre-pin locks. The current text ("0.30 ... no post-hoc adjustment") locks an arbitrary number; locking an arbitrary number is not anti-fishing protection, it is anti-fishing theater. Note this is the one number that, once frozen, cannot move — so it must be right before lock, not after.

### C-3 — The simulator has no specified calibration anchor; the R6 NHPP intensity function, `Q_low`, and the Q–FX dependence are all unpinned, making the simulation fantasy-threshold-exposed.

**Model claim.** §6.3 / §7 field 5: the simulator emits Q "calibrated to that currency's market"; the posture is "demonstration-grade ... a fantasy-threshold posture confined to Q alone."

**Defect.** "Calibrated to that currency's market" names no data source. The dev_ai_cost evaluation is explicit (`dev_ai_cost_model_evaluation.md` §1.B, O-2): the only real query-workflow data that ever existed is **one developer's Claude Code JSONL, n=1**, and that iteration PAUSED precisely because n=1 is too sparse. The v0.1 E10-Sim clause (v0.1 §9 note) was honest about this — it explicitly said the consumption profile must be "the *user's own* observed profile, not a fictional cohort scaling," and called that the NON-FANTASY condition. **v0.2 drops that clause entirely.** §6.3 now says "calibrated to that currency's market" with no anchor, across ~12 currencies for which no per-currency query-workflow data exists. Three specific unpinned objects:
- The NHPP intensity λ(t) — §6.2 reuses the R6 "hour-block × day-type seasonality grid" but no λ₀ or seasonality multipliers are given, and crucially **no overdispersion / clustering parameter**, which (per C-1) *is* `Var(logQ)`, the denominator of the verdict object.
- `Q_low` — §11 item 2 admits it is "a behavioral parameter ... the spec does not fix one." It is not under-identified; it is **un-identified**. It enters the band `[Q_low, Q_high]` that defines who carries the risk, so an un-pinned `Q_low` means the cohort itself is undefined.
- The Q–FX covariance term — §4.2 includes `2·Cov(logQ, logFX)` in the decomposition but the spec never says whether the simulator generates Q independently of FX (Cov ≈ 0) or with a behavioral coupling (analysts cut queries in high-FX-vol months — the v0.1 §3.2 "usage-rate response to FX" hypothesis). This is a modeling decision with a sign-relevant effect on the share and it is simply absent.

**What would fix it.** Pre-pin, in the spec, before E10.1: (i) the calibration anchor for λ₀ and the overdispersion parameter — and per the v0.1 NON-FANTASY clause, this anchor must be a real observed profile (the user's own JSONL, scaled per documented assumptions) or it is fantasy; (ii) a concrete `Q_low` with its derivation, or remove the band and replace it with a single anchored Q-distribution; (iii) an explicit pre-pin of the Q–FX dependence structure (independent, or coupled with a stated sign and magnitude). Until the simulator is anchored, §7 field 5's claim "fantasy-threshold posture confined to Q alone" is false — the fantasy is not "confined," it is the entire denominator of the decisive object.

---

## Strong findings

### S-1 — Wild cluster bootstrap with ~12 currency clusters is at the lower edge of validity; the spec should add a fallback and acknowledge the residual size distortion.

§7 inference: "~12 currency clusters, a wild cluster bootstrap by currency (Webb six-point weights)." The Webb-weight choice is correct — six-point weights are the standard small-G fix and dominate Rademacher below G ≈ 12 (Cameron-Gelbach-Miller; Webb 2014). But G = 12 is *borderline*, not safe: even with Webb weights, wild cluster bootstrap can retain meaningful size distortion below G ≈ 15–20, and the distortion is worst for one-sided tests near the null — which is exactly the §9 test geometry ("CI on the share excludes the floor from below"). The spec pre-commits to a single method with no fallback. **Fix:** pre-pin a secondary inference arm (e.g., the CGM subcluster / score-bootstrap, or randomization-inference across currencies) as a *concordance check*, and state explicitly that a v0.3 verdict requires both arms to agree. Also: with only ~12 clusters and currency FE absorbing 12 parameters out of ~360 cells, the effective residual degrees of freedom are thinner than the cell count suggests — the spec's "~360 cells clears N_MIN" framing (§8) is slightly generous; the binding dimension for inference is G = 12, not N = 360.

### S-2 — Currency FE alone is insufficient; common global FX-volatility shocks require month FE (two-way FE).

§7 field 6 specifies currency FE only, with the rationale that it "absorbs level differences in FX-regime volatility across countries." That is correct for the *cross-currency level* of FX vol. But realized FX variance has a strong **common global component** — risk-off episodes, USD-funding stress, global rate shocks move EM FX vol together. With currency FE only, a global vol spike enters both X (FX realized variance) and Y (cost-stream variance, which contains FX) in the same month for every currency, inflating the within-currency vol-on-vol association by a common-shock artifact rather than a cohort-specific channel. **Fix:** add month (time) FE — make it two-way FE (currency × month). This absorbs the common global FX-vol factor and leaves the *idiosyncratic per-currency* vol variation as the identifying variation, which is the economically meaningful object. The spec should pre-pin two-way FE and treat currency-FE-only as a sensitivity arm, not the primary. (Caveat: month FE will absorb a large share of the FX-vol variation; if it absorbs nearly all of it, that itself is a finding — it would mean the cohort's FX risk is a global factor, not a hedgeable per-currency micro-risk, which bears on the §13 instrument choice.)

### S-3 — The single-representative-analyst-per-currency design biases the FX-variance share *upward*.

§6.3 / §11 item 5: one representative analyst per currency. This is not neutral for the decisive object. Collapsing a heterogeneous cohort to one representative analyst **removes cross-sectional dispersion in Q**. Within-currency analyst heterogeneity (different workflows, different query mixes, different volumes within the band) is a real component of `Var(logQ)` in any honest cohort-level cost-variance object. The single-analyst design captures only the *time-series* variance of one Q-process and discards the *cross-analyst* variance. Since the share is `Var(logFX)/(Var(logFX)+Var(logQ)+2Cov)` and the single-analyst design **understates `Var(logQ)`**, it **mechanically overstates the FX-variance share** — biasing the iteration toward PASS. This compounds C-1: not only is the denominator simulator-determined, the chosen simplification systematically shrinks it. **Fix:** for a demonstration-grade verdict the single-analyst design is acceptable *only if* the spec (i) states explicitly that the resulting share is an **upper bound** on the true cohort FX-variance share, and (ii) re-pins the §7 field 3 floor and the §9 ladder to read against an upper-bound share (i.e., the PASS bar should be *higher*, or PASS should be stated as "FX share could be material" not "is material"). Better: simulate a small distribution of analyst types per currency (3–5 archetypes) so `Var(logQ)` carries its cross-sectional component. The spec's §11 item 5 asks the right question; the answer is "it overstates the share — do not ship the single-analyst design without the upper-bound caveat."

### S-4 — The §4.2 "leading order in log-returns" hedge is unnecessary and the spec should drop it; the real exactness gap is elsewhere.

§4.2 / §11 item 3 state the three-way decomposition holds "to leading order, in log-returns" and defer "the exact algebraic form" to E10.2. **This caveat is misplaced.** If Y is defined as the realized variance of **log** cost (i.e., `Var(Δlog cost)`), the decomposition `Var(Δlog cost) = Var(Δlog Q) + Var(Δlog FX) + 2·Cov` is **exact**, not leading-order — because `Δlog cost = Δlog Q + Δlog FX` is an exact identity (the constant `c` drops, `Δlog c = 0`) and the variance of a sum is exactly the sum of variances plus twice the covariance, for *any* random variables, with no approximation. There is no higher-order term and no bias. The "leading-order" language is therefore either (a) harmless but wrong, if Y is `Var(Δlog cost)`, or (b) a genuine problem, if Y is secretly the realized variance of the cost **level** `Var(cost)` — for which there is *no* clean additive decomposition (`Var(Q·c·FX)` involves `E[Q²FX²]` and does not split into FX + Q + cov). §5.2 defines Y as "realized variance of the ... cost stream" without specifying log vs level, and §4 talks about both "Var(cost stream)" and "log-returns" interchangeably. **Fix:** state unambiguously that Y, X, and the decomposition are all in **log-return space** (`Var(Δlog ·)`), delete the "leading order" caveat (the decomposition is exact there), and explicitly ban the level-variance object. If for any reason the level variance is wanted (e.g., for VaR / notional sizing in §13), that is a *separate* object and must not be fed into the §4.3 share. §11 item 3 should be resolved as: "no bias, provided Y is pinned to log space; the leading-order language is a spec error to delete."

---

## Weak findings

### W-1 — R6 NHPP is a defensible architecture for query arrivals but the spec under-specifies it relative to its own decisiveness.
A non-homogeneous Poisson process with hour-block × day-type seasonality is a reasonable model for analyst query arrivals at the *intra-period* level — arrivals are event-like, seasonality is real. The reuse of the R6 design (`dev_ai_cost_model_evaluation.md` §3, "reuse the design; build the code") is sound. **But** a pure NHPP is *equidispersed* (variance = mean within each cell). Real query workloads are bursty and overdispersed at the *monthly aggregate* level. Since the monthly aggregate `Var(logQ)` is the C-1 denominator, an equidispersed NHPP will *understate* monthly Q-variance and (per S-3's mechanism) overstate the FX share. The spec must pin whether the monthly Q-distribution is the raw NHPP aggregate (equidispersed) or carries an additional overdispersion layer (the R6 "session-composition bootstrap" partly does this — but the spec does not say so explicitly). This is Weak only because it is fixable inside C-3's calibration pre-pin; flagged so C-3's fix explicitly covers the dispersion parameter.

### W-2 — `Q_high = 39,000` rests on a behavioral rationality assumption that is asserted, not modeled.
§2.2 derives `Q_high` as `$390 ÷ $0.01` — the point "above which a rational analyst switches to the [Dune] subscription." This assumes analysts are cost-minimizing at the margin and that the Dune subscription and the x402 pay-per-query stream are perfect substitutes. Neither is obviously true (switching costs, feature differences, the very "qualitative limits" §2.2 invokes for `Q_low`). The $390 vs $399 question (§11 item 1) is a second-order quibble next to this: pinning `Q_high` off a *model cap* rather than the *observed price* is defensible precisely because the whole bound is a modeling abstraction, not a measurement — so my ruling on §11 item 1 is **keep $390 as primary, $39,900 as sensitivity, as the spec proposes**; the $9 is immaterial. But the spec should state that `Q_high` is a modeling boundary with a behavioral assumption attached, not a sharp empirical cutoff.

### W-3 — "Demonstration-grade" is the correct posture but the spec slightly overclaims within it.
§7 field 5 is right that confirmatory-grade is impossible here (Q simulated, G = 12). But the spec twice describes the fantasy as "confined to Q alone." Per C-1 and C-3, the fantasy is not confined — it propagates into the *denominator of the verdict object* and therefore into every §9 rung. Demonstration-grade is honest; "fantasy confined to Q alone" is not. **Fix:** restate as "the simulated Q enters the decisive share through the decomposition denominator; the verdict is demonstration-grade and conditional on the pinned Q-calibration." This is a wording fix, but it matters because §12's methods-paper hook leans on the posture being clean.

### W-4 — §6.2 reuse fraction (~25–30%) is plausibly correct (§11 item 6).
The dev_ai_cost evaluation's component-by-component disposition matrix (§3 of that doc) is thorough and its conclusion — R5/R4-S3 estimators cannot express vol-on-vol, the vol-on-vol estimator is a fresh build, R6 is a spec not code — is sound. I confirm the build-fresh list in §6.2 is **complete on the estimator side**: nothing in R5 (n=1 realized variance) or R4-S3 (magnitude-on-magnitude HAC-OLS) can be salvaged into the variance-on-variance estimator. One addition for the build-fresh list: the **two-way-FE panel machinery** (per S-2) and the **secondary inference arm** (per S-1) are also fresh builds not present in dev_ai_cost. §11 item 6 resolves: build-fresh list is complete for what it covers; extend it by those two items.

---

## Observations

- **O-1.** §9's NON-RETIREMENT rung ("Q-variance component dominates") is genuinely good anti-fishing design — it pre-commits that "FX vol is not the cohort's main risk" is an acceptable, non-engineered verdict. Preserve it. But note it is the *flip side* of C-1: if Q-variance dominance is simulator-determined, so is NON-RETIREMENT. The honesty of the rung depends entirely on fixing C-3's calibration anchor.
- **O-2.** §13.3's ideal-scenario caveat (no on-chain FX-pair options venue exists) is correctly firewalled and does not bear on the model-side verdict — the β-validation is deployment-independent, as CLAUDE.md permits. No model-QA objection to the M-sketch.
- **O-3.** The CORRECTIONS-E10-2 block (§0.2) is a clean, visible pivot record and complies with the HALT-checkpoint discipline. The directional → convex reframe is a genuine ex-ante thesis change, not post-data threshold tuning. Approved on process grounds.

---

## §11 open-items disposition

| # | Item | Disposition |
|---|------|-------------|
| 1 | $390 vs $399 Dune price | **Acceptable deferral.** Keep $390 primary, $39,900 sensitivity. Immaterial (W-2). |
| 2 | `Q_low` operationalization | **BLOCKER.** Folded into C-3 — `Q_low` is un-identified; the cohort is undefined without it. |
| 3 | Variance-decomposition exactness | **Spec error, must fix (S-4).** No bias *if* Y is pinned to log space; delete the "leading-order" caveat. Not a deferral — a one-line correction. |
| 4 | 0.30 material-share threshold | **BLOCKER.** Critical C-2 — derive from hedge break-even economics, do not assert. |
| 5 | Representative-analyst calibration | **BLOCKER (model-correctness).** Strong S-3 — single-analyst design biases the share upward; needs the upper-bound caveat or a multi-archetype simulation. |
| 6 | R6 reuse fraction | **Acceptable.** Build-fresh list confirmed complete; extend by two-way-FE machinery + secondary inference arm (W-4). |

Genuine model-correctness BLOCKERs: items **2, 4, 5** (and 3 as a mandatory one-line fix). Acceptable deferrals: items **1, 6**.

---

## Algebra note (verified by hand)

With `cost = Q · c · FX`, `c` constant: `Δlog cost = Δlog Q + Δlog FX` exactly. Hence
`Var(Δlog cost) = Var(Δlog Q) + Var(Δlog FX) + 2·Cov(Δlog Q, Δlog FX)` — **exact for any random variables**, no higher-order terms. The §4.2 "leading order" caveat is therefore wrong *in log space* (S-4). It would be *correct* only for the cost **level** variance `Var(cost)`, which has no clean additive split — confirming the spec must pin Y to log space. The share `Var(ΔlogFX)/Var(Δlog cost)` is then exact and clean, but `Var(ΔlogQ)` and the covariance are pure simulator outputs, and `∂share/∂Var(ΔlogQ) < 0` — the share is monotone in a free simulator parameter (C-1).

---

## Summary for dispatch

- **Verdict: NEEDS WORK.**
- **Critical count: 3** — (C-1) share is simulator-calibration-determined yet routed through the §9 verdict ladder as empirical; (C-2) 0.30 threshold is an unanchored round number; (C-3) simulator has no calibration anchor, `Q_low` un-identified, Q–FX dependence unspecified.
- **0.30 threshold verdict: NOT defensible as stated.** It is asserted on "materiality," not derived. It has a natural economic anchor the spec ignores — the FX-variance share at which the §13 long-gamma straddle's expected convex payoff covers its stream-funded premium. Pre-pin *that* derived break-even share as field 3, not a round number. Doubly arbitrary while C-1 stands: an unanchored number applied to an unanchored object.
- A v0.3 PASS is achievable: resolve C-1 by demoting the share to a calibration-conditional sensitivity surface, C-2 by deriving the floor from hedge break-even economics, C-3 by pinning the simulator to a real observed profile per the v0.1 NON-FANTASY clause. Strong findings S-1 (add a second inference arm), S-2 (two-way FE), S-3 (upper-bound caveat), S-4 (pin Y to log space, delete the leading-order caveat) should all land in v0.3.
