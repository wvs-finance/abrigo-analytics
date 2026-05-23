# Delphi Audit #1 — Math / Model / Derivations / Anti-Fishing

- **Auditor**: agent #1 of 3 (math/model layer)
- **Target**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.9
- **Notebooks**: `notebooks/dev_ai_cost_v2/{01,02,03,04,05,06}*.ipynb`
- **Panel**: `data/panels/notional_cost_panel.parquet` (29 rows, T=28 first-diffs)
- **Date**: 2026-05-18
- **Independence**: I have not consulted the other two auditors.

## Headline opinion

I found **2 Critical**, **3 High**, **5 Mid**, and **2 Low** findings. The R5 PRIMARY headline number ("FX share ≈ 0.00003") is internally consistent and the additive identity defense is sound, but several adjacent claims around it — most notably the "four independent measurements" convergent-evidence framing, the Z2 reclassification rule, the Z3 power-recipe pin, and the silent floor relaxations baked into CORRECTIONS-G/J — do not survive close reading. The iteration's substantive conclusion (FX-vol is empirically tiny on this window for this user) is likely directionally correct, but the spec's verdict scaffolding around it is closer to a relabeling exercise than the spec admits.

---

## CRITICAL FINDINGS

### FINDING 1 — Convergent-evidence claim is statistically circular

- **Name**: Four "independent" measurements are mechanically the same statistic
- **Severity**: **Critical**
- **Location**: spec §0.9 closing bullet (lines 1285–1290), §0.8 lines 1112–1116, R5 notebook Trio 6 cell 17, R4-S3-COP Trio 4 cell 16
- **Problem**: The spec claims "FOUR independent measurements (R5, Z-arms, R4-S3-COP, R4-S3-USD) agree on small-FX". On this panel, three of the four are deterministic functions of the same single number — `var(Δln TRM) / var(Δln Cost^COP)` — so their agreement is algebraic, not empirical corroboration.
- **Proposed fix**: Drop the "four independent measurements" framing. Honest count is **one** real measurement (the variance ratio) plus **one** independent behavioral test (R4-S3-USD), and the behavioral test is underpowered at N=28.
- **Evidence**:
  - R5 FX share (notebook 02 cell 11): `np.var(dln_trm) / np.var(dln_cop)` = **2.83e-5**.
  - R5 Trio 6 cross-check (notebook 02 cell 17): `(σ̂_FX-only)² / (σ̂_realized)² = Var(Δln TRM) / Var(Δln Cost^COP)` — explicitly noted in cell 17 as equal to the Trio 4 FX share by construction.
  - Z-arm Z-2 backcast: takes the SAME 28 observed `Δln cost^USD` values, composes with extended TRM, and recomputes `Var(Δln TRM) / Var(Δln Cost^COP)`. The denominator is artificially varied; the numerator is the SAME panel quantity. This is a sensitivity of one number to one nuisance, not an independent measurement.
  - R4-S3-COP: by the spec's own §0.8 admission, on this regime the regression has no power to detect anything. The CONSISTENCY-FAIL is THEN re-interpreted as evidence-for-small-FX. This is circular — a near-zero-power test that fails to reject is conventionally evidence of **nothing**, but is here re-coded as corroboration.
  - The only genuinely independent measurement is **R4-S3-USD**, and it is sub-floor (N=28<38) AND power-recipe-contested (see Finding 5). One measurement, one verdict.

### FINDING 2 — Pre-data threshold relaxation hidden in CORRECTIONS-G/J

- **Name**: N_MIN 75→38 and POWER_MIN 0.80→0.50 both relaxed before data, both claimed "demonstration-grade", both load-bearing for the headline label
- **Severity**: **Critical**
- **Location**: spec §0 CORRECTIONS-G (lines 109–117), CORRECTIONS-J (referenced via CORRECTIONS-U lines 221–229), §2.3 (lines 1526–1540), §7 anti-fishing invariants (lines 1842–1847)
- **Problem**: CLAUDE.md's project-default anti-fishing invariants are explicitly stated as `N_MIN = 75, POWER_MIN = 0.80, MDES_SD = 0.40`. This iteration relaxes N_MIN to 38 and POWER_MIN to 0.50 — a 1.97× and 1.60× relaxation respectively — in the SAME spec amendment that introduces the iteration. Both relaxations are inside the "pre-data" CORRECTIONS block, but neither is justified by anything observable independent of the iteration's own design choices (the n=1 subject's observed-day count). The "demonstration-grade" justification is rhetorical: every relaxation in every fishing-tempted iteration could be sold as demonstration-grade.
- **Proposed fix**: Either (a) restore N_MIN=75 and POWER_MIN=0.80 and let the iteration honestly HALT until the operator generates more data, or (b) explicitly cite the prior precedent (Rev-5.3.1) where N relaxation required a preserved power floor proof at the new N — and produce that proof here. The current relaxation does neither: N is relaxed AND power is relaxed.
- **Evidence**:
  - `memory/feedback_pathological_halt_anti_fishing_checkpoint.md` line 15 documents the canonical precedent: "Rev-5.3.1: user selected path α (relax to 75 with `required_power(75, 13, 0.40) = 0.8638 ≥ POWER_MIN`); the CORRECTIONS block documented the load-bearing-guarantees argument". The load-bearing argument was "power floor PRESERVED at the relaxed N". This iteration's CORRECTIONS-G/J does the opposite: relaxes BOTH simultaneously without computing what the power-floor would have to be to preserve the loadbearing 0.80 promise.
  - `CLAUDE.md` line 173: "`N_MIN = 75`, `POWER_MIN = 0.80`, `MDES_SD = 0.40` SD-units of Y. … These are NON-NEGOTIABLE across iterations".
  - Spec §7 line 1845 explicitly states "Power-floor: 0.50 at MDES = 0.40 residual SD for R4-S3 (CORRECTIONS-J + lowered from project-default 0.80 for pilot demonstration-grade)" — the relaxation is acknowledged but the load-bearing-guarantees argument is absent.

---

## HIGH FINDINGS

### FINDING 3 — §0.8 Z2 reclassification is a relabeling, not an econometric defense

- **Name**: REGIME-CONDITIONAL relabel replaces a statistical test with a constant
- **Severity**: **High**
- **Location**: spec §0.8 CORRECTIONS-Z2 (lines 1084–1186), notebook 03 Trio 4 (cells 14–16)
- **Problem**: §0.8 substitutes "HAC-OLS R4-S3-COP must pass" with "additive-identity check + variance-ratio < 0.01". The replacement is not a test — the additive identity holds at FP precision by panel construction (`notional_cost_cop = notional_cost_usd * trm` row-by-row), so it cannot fail by anything other than a parquet bit-flip. The variance ratio is a property of the regime, not a property of the pipeline. So "REGIME-CONDITIONAL FAIL" effectively means "the test was guaranteed to fail and we now accept it". This is not a stricter check (as §0.8 claims at line 1175–1178); it is a different check that cannot fire under any realistic failure mode.
- **Proposed fix**: Keep the §2.2.A HALT-on-FAIL semantics. Acknowledge that in low-FX-vol regimes the R4-S3-COP arm is **uninformative** (low power against any alternative), drop it from the spec as a "consistency check", and rely on the additive-identity assertion ALONE for pipeline integrity (which is what §0.8 actually does, but without the false claim that this replaces the regression).
- **Evidence**:
  - Notebook 03 cell 15: `identity_max_error = 1.78e-15`, the spec's own threshold is `1e-12`. The check is ~3 orders of magnitude tighter than FP epsilon. There is literally no panel-builder failure mode that would push this above 1e-12 without simultaneously corrupting the cost or TRM columns themselves (which is detectable by reading the parquet, not by this check).
  - Spec §0.8 line 1175: "The replacement integrity check (additive identity) is **STRICTER** than the original (HAC-OLS)". This is wrong as stated — the replacement check tests a different thing (panel-builder arithmetic) than the original (vol propagation through the regression). They are not comparable on a strict/loose axis.
  - The genuine econometric concern — "we cannot detect FX-vol pass-through in a regime where FX vol is microscopic" — is correctly identified, but the resolution should be "this arm is uninformative, drop it" not "this arm is reclassified as supporting a small-FX reading".

### FINDING 4 — Convergent-evidence claim mis-attributes R4-S3-COP

- **Name**: A CONSISTENCY-FAIL "supports" the framework prior only after the spec is amended to make it support the framework prior
- **Severity**: **High**
- **Location**: spec §0.8 lines 1112–1116, §0.9 lines 1285–1290, notebook 03 cell 16
- **Problem**: §0.8 lists R4-S3-COP's CONSISTENCY-FAIL as one of the four convergent measurements supporting "FX-vol not a meaningful driver". But the same paragraph admits R4-S3-COP "cannot recover a positive α₁^COP at conventional significance even when both signals are individually clean". A test that cannot reject under the null AND cannot reject under the alternative provides ZERO evidence either way. Counting it as corroborative evidence is double-bookkeeping: the same fact (low FX vol) is used to (a) explain why the test fails AND (b) corroborate that FX vol is low.
- **Proposed fix**: Remove R4-S3-COP from the convergent-evidence list. Restrict the "convergent" claim to R5 + Z-arms + R4-S3-USD, and explicitly disclose that Z-arms are not independent of R5 per Finding 1.
- **Evidence**:
  - Spec §0.8 line 1107–1109: "the noise floor on the regressor swamps its mean" → power ≈ 0 against H1.
  - Spec §0.8 line 1113: "internally consistent with R5 PRIMARY … three independent measurements converge on 'FX-vol is empirically not a meaningful driver'". This claim survives only by counting a zero-power test result as a "measurement".

### FINDING 5 — §0.9 Z3 power-recipe pin chooses the recipe that gives the higher number

- **Name**: Lagged-recipe is the standard reading; contemporaneous-recipe was pinned post-hoc with the data already visible
- **Severity**: **High**
- **Location**: spec §0.9 CORRECTIONS-Z3 (lines 1188–1292), notebook 04 cell 14
- **Problem**: When Task 14 fired POWER-HALT under the lagged-tokens partialling recipe (power = 0.1745), the spec author had two options: (a) HALT and write a disposition memo per the protocol, or (b) re-interpret CORRECTIONS-J to canonicalize the recipe that gave 0.7115 instead. The spec chose (b) and defends it on (i) chronological precedence (Task 11 EDA happened to compute it that way first) and (ii) first-principles ("residual SD is a sample-noise benchmark, not test geometry"). Both defenses are weak:
  - (i) Task 11's choice was implementation-incidental, not a deliberate methodological pin. Treating "the first cell anybody wrote" as canonical is a recipe for any future divergence to be resolved by whoever-pushed-first.
  - (ii) Standard power-calc practice for OLS-with-HAC IS to use the residuals of the regression being tested (see e.g. Cameron & Trivedi 2005 §3.5 on HAC-corrected power; standard `statsmodels` power utilities; Andrews 1991 power-experiment design). The "alternative reading" the spec adopts is not orthodox.
- **Proposed fix**: HALT per CORRECTIONS-J/U's anticipated routing. Fill the disposition memo. The honest user pivot is "accept lower-power result with caveat" (CORRECTIONS-U pivot C). Verdict becomes POWER-HALT (or PARTIAL-FAIL_TO_REJECT with documented low power), not PARTIAL-FAIL_TO_REJECT under a relabeled gate.
- **Evidence**:
  - The contemporaneous-recipe partialling regresses `|Δln cost^USD|_t` on `|Δln tokens|_t` (same time-step). R² = 0.5515 (notebook 01 cell 14). Residual SD = 0.787.
  - The lagged-recipe partialling regresses `|Δln cost^USD|_t` on `|Δln tokens|_{t-1}` (mirroring the R4-S3-USD regression). R² ≈ 0.002 (notebook 04 cell 14 + my replication). Residual SD = 1.156.
  - The R4-S3-USD regression itself uses the LAGGED tokens regressor (`x2_primary = abs_dln_tok[:-LAG_PRIMARY]`, notebook 04 cell 8). Standard power analysis matches the test's residuals.
  - Spec §0.9 line 1235: "v0.2.9 pins the recipe that gives a HIGHER power (0.7115 > 0.1745 > 0.50 only on the higher side). On first reading this looks like result-chasing." The spec author concedes the concern and then dismisses it with the precedent and first-principles arguments above. The concession is itself diagnostic.
  - The "power-calc residual SD is a sample-noise benchmark" defense in §0.9 line 1226 contradicts §2.2.B's own verdict-logic table line 1494 which gates on "measured power ≥ 0.50 at MDES = 0.40 residual-SD" — i.e., the power is the test's detection capacity for THIS specific regression's null. The two cannot be the same number if the residual SD is computed from a different specification.

---

## MID FINDINGS

### FINDING 6 — R5 variance-decomposition identity uses **signed** Δln, not |Δln|

- **Name**: Identity holds for signed log-returns; spec phrasing is loose
- **Severity**: **Mid**
- **Location**: spec §2.1 output 3 (lines 1373–1378), notebook 02 cells 2 & 11
- **Problem**: The audit prompt flagged a potential confusion between signed and absolute log-returns. After replication: **the notebook correctly uses signed Δln** for the variance decomposition. For signed log-returns, the additive identity `dln_cop = dln_usd + dln_trm` holds row-by-row by panel construction (verified at 1.78e-15 in my replication), so `Var(Δln Cost^COP) = Var(Δln Cost^USD) + Var(Δln USDCOP) + 2·Cov(...)` is an algebraic identity. This is mathematically valid. The issue is documentation: the spec uses `Δln` in §2.1 output 3 but mixes "absolute-return data" phrasing in §0.1 CORRECTIONS-P (line 161). The two are different statistical objects. The bootstrap pool in §0.1 line 162 says `absolute-return data` but the actual bootstrap in notebook 02 is on signed `dln_cop` — a minor mismatch that doesn't change the result but should be tightened.
- **Proposed fix**: In §2.1 explicitly write `Var(Δln·)` and `Cov(Δln·, Δln·)` (signed), and in §0.1 CORRECTIONS-P amend "absolute-return data" → "log-return data" (signed). The R5 framework is variance-of-signed-log-returns; R4-S3 is the absolute-log-returns specification. These should not be conflated in prose.
- **Evidence**:
  - Notebook 02 cell 2: `dln_cop = np.diff(np.log(...))`, no `np.abs()`.
  - Notebook 02 cell 11: `fx_share_excl_cov = np.var(x) / np.var(c)` where `x = dln_trm`, `c = dln_cop` (signed).
  - My replication: `Var(dln_cop) = 2.6429`, `Var(dln_usd) + Var(dln_trm) + 2·Cov = 2.6457 + 0.0000749 + (−0.00292) = 2.6429`. Identity holds.
  - The same decomp on **absolute** values does NOT hold: `|dln_cop| ≠ |dln_usd| + |dln_trm|` (max error 0.0245, three orders of magnitude above noise).

### FINDING 7 — Cov term reported "separately, not in FX share" — but the bootstrap CI on FX share treats numerator and denominator independently

- **Name**: Conservative-cov rule is implemented as the spec describes; verify nuance
- **Severity**: **Mid**
- **Location**: notebook 02 cells 10–12, spec §0.1 CORRECTIONS-Q (lines 166–181)
- **Problem**: The notebook's `fx_share_excl_cov(c, u, x) = Var(x)/Var(c)` correctly returns `Var(Δln TRM)/Var(Δln Cost^COP)`. The cov term is reported separately. The spec describes this as "conservative — a positive Cov would inflate the apparent FX share under alternative attributions; dropping it understates and avoids overclaiming". This is correct as a static lower-bound argument. **However**: on this panel `2·Cov = -0.00292` (negative), so under the alternative "split the cov 50/50" attribution the FX share would be even smaller, not larger. The "conservative" framing is sign-dependent and on this data the convention happens to OVERSTATE the FX share relative to symmetric attribution. This is harmless for the headline (the result is "basically zero" either way) but the spec text generalizes incorrectly.
- **Proposed fix**: §0.1 CORRECTIONS-Q should add a sentence: "When Cov < 0, the conservative-excluding rule gives a LARGER FX-share point estimate than symmetric attribution; the conservatism direction depends on sign(Cov) and is documented honestly in the headline."
- **Evidence**: My replication, `2·Cov(dln_usd, dln_trm) = −0.00292`, FX share excl cov = 2.83e-5, FX share with cov rolled in symmetrically would be `(Var(trm) + Cov)/Var(cop) = (7.49e-5 − 0.00146)/2.64 ≈ −5.3e-4` (negative — i.e., FX is treated as a vol-reducing factor). The notebook correctly flags this in cell 12: "negative ⇒ natural hedge effect within the developer's behavior" — but the spec text in CORRECTIONS-Q does not flag the sign-dependence of the conservatism.

### FINDING 8 — HAC bandwidth `L = floor(T^(1/3))` at T=27 → L=3 is defensible but not "Andrews 1991"

- **Name**: Bandwidth pin attribution
- **Severity**: **Mid**
- **Location**: spec §0.1 CORRECTIONS-I implicit (line 1477), notebook 03 cell 2, notebook 04 cell 2
- **Problem**: The spec and notebook header comments cite "Andrews 1991 rule-of-thumb HAC bandwidth: floor(T^(1/3))". Andrews (1991, *Econometrica*) proposed a **data-driven plug-in bandwidth** based on AR(1) pre-fit residuals — not a fixed `T^(1/3)` rule. The `T^(1/3)` rule is actually associated with **Newey-West (1994)** for the Bartlett kernel and is closer to a rule-of-thumb than an optimal Andrews bandwidth. At T=27, L=3 → using 3 lags for HAC; this is conservative-to-reasonable for daily data with weak persistence (Trio 4 of notebook 01 showed lag-1 ACF = +0.0092, essentially white noise). The numeric choice is fine; the attribution is wrong.
- **Proposed fix**: Re-attribute to Newey & West (1994) "Automatic Lag Selection in Covariance Matrix Estimation" *Review of Economic Studies*. Or run the Andrews 1991 plug-in (`statsmodels.stats.sandwich_covariance.cov_hac` with `kernel='bartlett'` and data-driven bandwidth) as a sensitivity. At T=27 the plug-in typically yields L ∈ {1, 2, 3} and would not move any conclusion.
- **Evidence**: Notebook 03 cell 2: `def hac_bandwidth(t_lag: int) -> int: """Andrews (1991) rule-of-thumb HAC bandwidth: L = floor(T^(1/3))."""`. This is a misattribution; Andrews 1991 is the data-driven AR(1) plug-in.

### FINDING 9 — Stationary bootstrap block length `⌈T^(1/3)⌉ = 4` at T=28 is at the low end of Politis-Romano recommendations

- **Name**: Block length defensible but should bracket-sensitivity
- **Severity**: **Mid**
- **Location**: spec §0.1 CORRECTIONS-P (lines 158–164), notebook 02 cell 5
- **Problem**: Politis & Romano (1994, *JASA*) propose the stationary bootstrap with geometric block lengths having expected length `1/p`. They do NOT pin `T^(1/3)` as canonical; the original paper recommends optimizing over a grid (data-driven via plug-in MSE minimization, Politis & White 2004 *Econometric Reviews*). At T=28 → block_len=4 means within-block dependence is captured for at most 4 days; if there's any longer-range vol clustering in `Δln cost^USD` (which there could be at weekly horizons given the bursty single-user usage), the CI will be too tight. With T=28 the sensitivity is large: block_len ∈ {2, 4, 6, 8} all defensible; the FX share CI half-width depends.
- **Proposed fix**: Run the stationary bootstrap at block_len ∈ {2, 4, 6, 8} and report the FX-share CI under each. Pin the **median** (or the widest) as headline. Currently the pin is a single rule-of-thumb without sensitivity.
- **Evidence**: Spec §0.1 line 162: "expected block length `⌈T^(1/3)⌉`. At T = 38, expected block length = 4". The 4 is reasonable; the absence of sensitivity is the gap. At the very least, the notebook should report Politis-White 2004's data-driven optimal length as a cross-check.

### FINDING 10 — PARTIAL-* verdict labels are honest disclosure but the spec walks back the N_MIN floor

- **Name**: PARTIAL-FAIL_TO_REJECT label is OK on its own but the floor it bypasses was already pre-data-relaxed
- **Severity**: **Mid**
- **Location**: spec §2.2.B verdict logic (lines 1492–1524), §0.9 line 1264–1265
- **Problem**: The PARTIAL-* labels (added v0.2.9) ARE genuine honest disclosure as the spec claims at line 1518–1524: they preserve the prefix verbatim and require sub-floor-N disclosure. **Conditional on N_MIN=38 being the correct floor**, this is fine. But Finding 2 already disputes N_MIN=38 — the project-default is 75 — so PARTIAL-FAIL_TO_REJECT at N=28 is actually two floor-deficits stacked: 28<38 (admitted) AND 38<75 (hidden in CORRECTIONS-G). The spec is technically honest at each layer but the cumulative disclosure is buried. A reader who lands on the verdict-logic table without reading §0 CORRECTIONS-G/J cannot infer that the operative floors are 1.97× / 1.60× below project-default.
- **Proposed fix**: §2.2.B verdict-logic table should carry a sticky asterisk on the N_MIN=38 and POWER=0.50 rows pointing back to CORRECTIONS-G/J's project-default deviation and to the §7 anti-fishing invariants line that documents it. Currently the §2.2.B table presents 38 and 0.50 as the canonical floors, which they aren't.
- **Evidence**: Spec §2.2.B verdict-logic gates: "N ≥ 38 weekdays" and "measured power ≥ 0.50". §7 line 1842–1846 acknowledges these are deviations. The verdict-logic table does not cross-reference §7.

---

## LOW FINDINGS

### FINDING 11 — Notebook 02 cell 6 docstring is wrong about ddof

- **Name**: docstring mismatch
- **Severity**: **Low**
- **Location**: notebook 02 cell 5
- **Problem**: `def realized_vol(x): """Population (ddof=0) standard deviation..."""` — but the function calls `np.sqrt(np.var(x))` which IS ddof=0 by default. Docstring is correct but slightly redundant (default np.var has ddof=0; the docstring should say "matches np.var default" rather than "spec-consistent"). The spec actually does not pin ddof — both ddof=0 and ddof=1 would be defensible; the spec is silent. Minor consistency issue.
- **Proposed fix**: Pin ddof in spec §2.1. Suggest ddof=0 for variance ratios (cancels in numerator and denominator) and ddof=1 for σ̂ reporting (sample SD convention).
- **Evidence**: Notebook 02 cell 5, spec §2.1 silent on ddof.

### FINDING 12 — Notebook 02 Trio 3 (VaR) uses point estimator on T=28 sample

- **Name**: 5% empirical quantile on 28 obs has implied precision ~1 obs
- **Severity**: **Low**
- **Location**: notebook 02 cell 8, spec §2.1 output 2 (line 1369–1370)
- **Problem**: `np.quantile(x, 0.05)` on 28 observations places the 5% quantile at order-statistic index `floor(0.05·28) = 1` or `ceil(0.05·28) = 2` depending on interpolation — i.e., the empirical quantile is determined by 1-2 datapoints. The bootstrap CI on this quantity captures resampling variability but the underlying sample is not large enough for a stable 5% quantile estimator. The spec calls it "monthly VaR" in §2.1 line 1369 but the notebook reports daily VaR with the cell-7 disclaimer that "monthly framing is conceptual". This is a spec-vs-notebook drift, harmless because the cell flags it, but the spec should be amended to either (a) compute a real monthly VaR by aggregating, or (b) rename to "daily 5% empirical quantile" throughout.
- **Proposed fix**: Rename "monthly VaR" → "daily 5% empirical quantile" in §2.1 output 2, since that is what is actually computed.
- **Evidence**: Notebook 02 cell 7 markdown: "the spec's 'monthly' framing is conceptual"; spec §2.1 line 1369 still says "empirical 5% monthly VaR".

---

## CHRONOLOGY OF AMENDMENTS — Anti-Fishing Pin Audit

The audit prompt asked whether any of the 9 amendments retroactively relaxed thresholds AFTER seeing data. Per the spec's own dates and the iteration's task-execution log:

| Amend. | Date | Threshold change? | Verdict |
|---|---|---|---|
| v0.1.0 → v0.2.0 | 2026-05-16 | N_MIN 75 → 38 (CORRECTIONS-G); POWER_MIN 0.80 → 0.50 (CORRECTIONS-J) | **Pre-data but unjustified** — see Finding 2 |
| v0.2.0 → v0.2.1 | 2026-05-16 | Bootstrap pin (CORRECTIONS-P); CI 0.20 → 0.15 (CORRECTIONS-T) | Pre-data, tightening — OK |
| v0.2.2 | 2026-05-17 | Cost arithmetic Decimal→float; reconciliation exact→0.1% | Post-data on parser failures, but on accuracy-measurement axis, not verdict threshold. OK. |
| v0.2.3 | 2026-05-17 | Architectural pins, π̂ diagnostic | No threshold change. OK. |
| v0.2.4 | 2026-05-17 | Line-level malformed skip | No threshold change. OK. |
| v0.2.5 | 2026-05-17 | uniqueHash dedup | No threshold change. OK. |
| v0.2.6 | 2026-05-17 | Z-arms added; daily baseline 3e-5 already known by then | **AFTER Task 12 result was known** (FX share = 3e-5 in v0.2.5 R5 output). Z-arms thresholds (5× baseline OR 0.05) pinned with that baseline visible. The 5× rule was specifically chosen to NOT trip on the Z-2 backcast, which is on the same panel. This is post-hoc threshold construction. |
| v0.2.7 | 2026-05-17 | Y-9 timezone artifact | Documentation only. OK. |
| v0.2.8 | 2026-05-17 | Z2 reclassification | **AFTER Task 13 CONSISTENCY-FAIL was known**. See Finding 3. |
| v0.2.9 | 2026-05-18 | Z3 power-recipe pin | **AFTER Task 14 POWER-HALT was known**. See Finding 5. |

**Verdict**: v0.2.0's N/POWER relaxations are pre-data but unjustified relative to the Rev-5.3.1 precedent. v0.2.6 through v0.2.9 are AT LEAST partially post-hoc: each amendment was authored after the result of the relevant task was visible, and each amendment converts a failing or HALT-eligible result into a reportable verdict. The cumulative effect is that every numerical outcome in the iteration that would have HALTed under the v0.2.0 spec now has a pathway to a reportable verdict.

This pattern is the signature of fishing-by-spec-amendment rather than fishing-by-threshold-relaxation. The anti-fishing protocol (`memory/feedback_pathological_halt_anti_fishing_checkpoint.md`) is designed to catch the latter; the iteration has evolved a way around the former. **Each individual amendment is defensible in isolation; the cumulative pattern is not.**

---

## NO-ISSUE NOTES

- **R5 variance-decomposition formula on signed log-returns**: mathematically valid (Finding 6 closes this as docs-only).
- **Test inversion logic on R4-S3-USD α₁^USD**: correctly described and implemented. Two-sided test, null = 0, reject = behavioral channel, fail-to-reject = subscription inelasticity. Notebook 04 cell 2 correctly pins TWO-SIDED before data. OK.
- **CORRECTIONS-Q conservative-cov rule implementation**: matches spec exactly in notebook 02 cell 11. `fx_share_excl_cov = np.var(x) / np.var(c)` where x=dln_trm, c=dln_cop. Cov reported separately. (Sign-direction caveat per Finding 7, but that's prose, not code.)
- **Stationary bootstrap implementation**: `arch.bootstrap.StationaryBootstrap(block_len, *series, seed=...)` is the standard Politis-Romano implementation. The joint-resampling on 3 aligned series in cell 11 preserves row-alignment correctly. OK.
- **Additive-identity check in §0.8 Z2**: 1.78e-15 vs 1e-12 threshold — correctly verifies panel construction. The check itself is fine; my issue (Finding 3) is the framing of what it replaces.

---

## RECOMMENDATIONS TO ORCHESTRATOR

1. **Required to land a verdict**: Address Findings 1, 2 (Critical). The "four independent measurements" claim cannot stand; the floor-relaxation must either be reverted or accompanied by a load-bearing-guarantees proof in the spec.
2. **Should address before write-up**: Findings 3, 4, 5 (High). The Z2 / Z3 reclassifications materially change what numbers are reportable; reviewers and the LaTeX writer should see the alternative readings explicitly.
3. **Defensible to land with disclosure**: Findings 6, 7, 8, 9, 10 (Mid). Prose and citation fixes; do not change verdict.
4. **Cosmetic**: Findings 11, 12 (Low).

**Substantive note for the user/orchestrator**: the underlying empirical reality — "for this user on this 28-day window, FX vol contributes negligibly to COP cost-burden variance" — is **likely true** and would survive a stricter audit. The problem is not the conclusion; it is the spec apparatus around the conclusion, which over-claims convergence, hides floor relaxations, and converts every HALT into a reportable verdict via post-hoc amendment. A cleaner v0.3.0 would have: (a) ONE measurement (R5), (b) ONE behavioral test (R4-S3-USD, properly powered or HALTed), (c) explicit acknowledgment that R4-S3-COP and Z-arms are not independent corroboration, and (d) restored project-default floors with a documented "demonstration-grade" caveat in the headline rather than inside CORRECTIONS-G.
