# Code Reviewer Verdict — D1.D + D4 Joint Spec v0.1

**Reviewer:** Code Reviewer (methodology-rigor lens)
**Spec:** `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.1
**Date:** 2026-05-18
**Scope:** econometric coherence, identification, pre-pin sufficiency, joint-identity validity, anti-fishing posture.

---

## Verdict

**CONDITIONAL_APPROVE** — proceed to v0.2 only after the **four MUST-fix issues** below are explicitly addressed in §4 pre-pin and §7 verdict criteria. The intent is sound, the transparency-condition compliance is good, and the demonstration-grade framing is honest. However, the **primary specification has a textbook spurious-regression risk**, the **joint identity is invalid on non-overlapping wallet sets**, and the **ρ-ratio estimator is unstable in its current form**. These are not nits — they affect whether the headline quantity is identifiable at all.

The block-vs-conditional decision turns on the fact that all four MUST-fixes are pre-implementation pre-pin amendments — no code is wasted by holding. If any one of these were a post-implementation finding it would be BLOCK.

---

## Critical issues (MUST fix before v0.2 implementation)

### MUST-1. Spurious-regression risk in D1.D primary spec — §4.1

The primary spec is:

```
log(Y_t) = α + β·log(X_t) + γ·log(spot_COP_USD_t) + ε_t,  HAC L=⌊T^(1/3)⌋
```

Both `Y_t = log(Bitso USDC inflow × scalar)` and `X_t = log(Banrep services-credit USD)` are **trending in levels** over 2020-01 → 2026-04 (LATAM stablecoin growth + post-COVID services-export expansion). HAC at L≈4 corrects standard errors for residual autocorrelation, but **HAC does not fix spurious regression of two unit-root processes**. The Granger-Newbold 1974 result is that R² and t-statistics inflate even when the true cointegration coefficient is zero.

Additionally, the **spline interpolation of quarterly Banrep services-credit to monthly** introduces a known autocorrelated error structure in X — the interpolated values at non-quarter-end months are deterministic functions of adjacent quarterly observations, which induces serial correlation in `ε_t` at frequencies HAC cannot fully scrub at L=⌊76^(1/3)⌋ ≈ 4.

**Required amendments to §4.1 pre-pin:**

1. **Pre-test for unit roots** in `log(Y_t)` and `log(X_t)` (ADF + KPSS, pre-pinned 5% size). Decision rule must be declared NOW:
   - If both I(1): pre-pin Engle-Granger or Johansen cointegration test as gatekeeper. Only if cointegration is established does the level regression in §4.1 yield consistent β.
   - If non-cointegrated: pre-pinned fall-back to first-difference spec `Δlog(Y_t) = α + β·Δlog(X_t) + γ·Δlog(spot_t) + ε_t`. This is a **different β** (short-run elasticity, not long-run) and the magnitude floor MDES_SD = 0.40 must be re-evaluated against the smaller variance of Δlog vs log.
2. **Acknowledge the spline-induced AR structure** in ε explicitly. Either Newey-West with L large enough to span the interpolation window (L ≥ 3 — a full quarter), or pre-pin month-end-only observations (drops 2/3 of N — fails N_MIN=75; not viable). HAC L=4 is acceptable only if L is pre-pinned as the larger of ⌊T^(1/3)⌋ AND the spline support.

Without this amendment, a "PASS" β in §7 cannot be distinguished from spurious correlation, and the anti-fishing posture is undermined — the HALT trigger β CI contains zero won't fire on a spurious +β that mechanically appears.

### MUST-2. Joint identity `CF = E − L` does not hold on non-overlapping wallet sets — §4.3, §13.3

The spec acknowledges this in §13.3 as an "open item" but the §4.3 pre-pin treats `ρ_t = ΔCF_t / E_t` as if the identity holds. **It does not.**

- D1.D measures Bitso/Lemon CEX hot-wallet inflows. Set A.
- D4.1 measures USDC-holder wallet balance trajectories. Set B.
- Overlap is estimated 30-60% per Salvage Path 4 findings.
- The identity `CF_T = E_T - L_T` is exact only on Set A ∩ Set B. On the union, you have:
  - Inflow to A but not B (CEX users who never hold USDC long, i.e., immediate off-rampers): contribute to E_T but never to ΔCF_t
  - Holding in B but not A (self-custody savers who got USDC from somewhere other than tagged CO CEX): contribute to ΔCF_t with no corresponding E_t

This means ρ_t = ΔCF_t / E_t **mixes apples and oranges** — the numerator's source population is not the denominator's, and there is no reason the ratio is interpretable as a "transmission rate."

**Required amendment:**

Pre-pin one of three resolutions to §4.3 BEFORE data work begins:

(a) **Intersection-only estimand**: define `ρ_t^∩ = ΔCF_t^∩ / E_t^∩` where ^∩ restricts both numerator and denominator to wallets that appear in both panels in the same month. Requires wallet-graph tracing in the Tier-3 panel builder. This is the **rigorous** option.

(b) **Aggregate-bias acknowledgment**: keep ρ_t as defined but pre-commit to reporting it as `ρ_t^aggregate` with an explicit bias-direction statement: "ρ_t^aggregate biases ρ_t^true downward if non-overlap E > non-overlap CF (likely — off-ramps don't show in CF), upward if non-overlap CF > non-overlap E (unlikely)." This is the **honest minimum**.

(c) **Reframe as bound**: pre-commit `ρ_t^aggregate` as an empirical lower bound on the true intersection ρ, and PASS criterion in §7 changes to "lower-bound ρ̄ ≥ 0.05" not "ρ̄ ≥ 0.05."

The current §4.3 is silent on which interpretation applies. Pick one.

### MUST-3. Ratio-estimator instability in ρ_t — §4.3

`ρ_t = ΔCF_t / E_t` with `E_t` in the denominator is a **classic ratio estimator** with known instability when E_t is small (low-activity months) or volatile. Two failure modes:

1. **Near-zero denominators**: a single low-inflow month (e.g., a holiday slowdown, or a Dune query gap) drives ρ_t toward ±∞, dominates any sample average ρ̄, and is not handled by the §4.3 HALT trigger (`ρ̄ < 0`).
2. **Bias in E[ρ_t]**: even when CF and E are jointly stationary, E[ΔCF/E] ≠ E[ΔCF]/E[E] (Jensen's inequality on the ratio function). The sample-mean ρ̄ is a biased estimator of the population ratio.

The current HALT trigger only catches ρ̄ < 0; it does **not** catch ρ̄ blown up by a single small-denominator month or the systematic Jensen bias.

**Required amendments to §4.3:**

1. **Pre-pin a denominator floor**: drop months with `E_t < q_5(E_t)` (bottom 5% of inflow months) from ρ̄ computation, OR Winsorize ρ_t at pre-committed (1%, 99%) quantiles. Choice must be made BEFORE data is touched.
2. **Pre-pin the primary aggregation level**: ratio-of-means `ρ̄ = ΣΔCF_t / ΣE_t` is consistent and not blown up by single small-E months. Mean-of-ratios `(1/T)Σ(ΔCF_t/E_t)` is what the current spec implies and is the unstable one. Pick **ratio-of-means** as primary; mean-of-ratios as exploratory secondary.
3. **Add a second HALT trigger**: `|ρ̄| > 1.5` or any individual `|ρ_t| > 5` triggers HALT with disposition memo (measurement-error or definitional-mismatch is dominating). The current spec lets ρ̄ = 8.3 silently slide because only `ρ̄ < 0` HALTs.

### MUST-4. Multiple-testing protection is absent — implicit in §6, §7

Six notebooks × ~3 specifications each (primary + 2 sensitivity arms for D1.D; primary + 2 priors for D4.1; ρ at three aggregation levels) ≈ 18 effective hypothesis tests, all rolling up to the §7 PASS/FAIL gate at α=0.05. Family-wise α is uncontrolled. A single false-positive in the sensitivity arms could anchor a PARTIAL-PASS that should have been FAIL.

The spec §14 anti-fishing closure does say "post-hoc selection of the favorable arm is BANNED" but does **not** pre-pin how concordance across arms is judged.

**Required amendment to §4 + §7:**

Pre-pin ONE primary specification with α=0.05 single-test inference. ALL other specifications (sensitivity arms, secondary lags, alternative priors) labeled as "exploratory robustness — not contributing to the headline verdict." §7 PASS criterion uses the primary spec only; sensitivity arms inform PARTIAL-PASS vs PASS only via the **sign-concordance** rule (already in §7), which is the appropriate weak-FWER protection. Bonferroni is overkill given the structure; the single-primary commitment is the right tool.

Make this commitment explicit in §4: "The primary specification for D1.D is the one row of §4.1 marked 'Primary specification'. Sensitivity arms in §4.1 (10%/35% scalars) and secondary lags (k=0-1) contribute to the verdict ONLY via sign-concordance with the primary. They are NOT independently inferential."

---

## Strong recommendations (SHOULD fix in v0.2)

### SHOULD-1. COP/USD spot as covariate γ — §4.1 — is it controlling the right thing?

Including `log(spot_COP_USD_t)` as a covariate is theoretically motivated (controlling for the exchange-rate level at which USD-denominated services credit is converted to COP). But it has a dual mechanism:

- It absorbs valuation effects (a stronger USD mechanically raises COP-denominated Banrep services-credit even if real flow is constant).
- It also absorbs **the wage-receipt FX motive itself** — the very channel by which a worker decides to keep USDC vs convert to COP is driven by spot. Including spot may absorb the variation we want to attribute to "USD-flow growth driving USDC receipt."

Recommend: pre-pin TWO primary specifications — one with γ ≠ 0 (the "valuation-controlled" β) and one with γ = 0 (the "uncontrolled" β). The sign and significance of the GAP between the two is itself interpretable. Currently spec hardcodes γ in — this is a soft-fishing risk.

### SHOULD-2. Pooled-stablecoin GPD assumption — §4.2

CORRECTIONS-A is user-signed and the reviewer is instructed not to re-litigate. Accepted. However, the D4.2 findings report **pooled ξ̂ = 0.18 vs USDT-only ξ̂ = 0.018** — an order-of-magnitude divergence. This is a flag, not a block: the pooling assumption that USDC, USDT, DAI share tail shape is empirically suspect.

Recommend: pre-pin a sensitivity arm in §4.2 — "USDT-only prior" vs "pooled prior" as two arms. If the verdict diverges across arms, that itself is the iteration's contribution to knowledge (pooling assumption is the binding constraint). This is consistent with CORRECTIONS-A which permits pooling, not requires it.

### SHOULD-3. Off-ramp decomposition formula is not operationally testable as stated — §4.3

```
ρ_t = (1 − off_ramp_ratio_t) + flow_in_t / E_t
```

This is presented as an identity. It is not — it assumes a clean partition (off-ramp + retained + external inflow) on wallet flows. Reality has chain hops, bridges, intra-CEX transfers, swaps to other tokens that aren't tracked. The leftover residual is silent.

Recommend: rewrite §4.3 decomposition as:

```
ρ_t = 1 − off_ramp_ratio_t + flow_in_ratio_t − unaccounted_residual_t
```

And pre-pin a sanity check: `|unaccounted_residual_t|` median < 10% of E_t. If larger, the partition is not operational and the decomposition is interpretive only, not identity. Notebook 04 should produce this diagnostic explicitly.

### SHOULD-4. Coverage scalar's symmetric role in E_T vs CF_T — §13.1

Open item #1 is correct that the scalar does not bias β (it's a multiplicative constant in log-log regression). But for ρ̄:

```
ρ̄ = ΔCF_T / E_T = ΔCF_T / (raw_inflow × scalar)
```

The scalar appears in the denominator of ρ̄ but NOT the numerator (since CF_T from D4.1 is USDC-holder balance trajectories, measured directly without the same Colombia-scalar — D4.1 cohort is a Fermi'd wallet set with its own coverage assumptions).

This means **scalar choice has asymmetric impact on ρ̄**: a smaller scalar → larger ρ̄. The 10%/20%/35% sensitivity arms therefore yield ρ̄ values that differ by ~3.5× (35/10 ratio). This is large.

Recommend: pre-pin in §4.3 whether (a) the same scalar is applied to both sides for consistency (defensible if we believe Bitso CEX cohort ⊂ D4.1 USDC-holder cohort), (b) different scalars for the two sides with documented justification, or (c) report ρ̄ as a function `ρ̄(scalar)` rather than a point estimate. Currently §13.1 brushes this off as "doesn't bias β" but ρ̄ IS the headline quantity, not β.

### SHOULD-5. Reproducibility tier — Dune query state can change — §5.4

Tier 3 panel-builder is supposed to re-derive Tier 1 from Tier 2. But Tier 2 raw is "Dune SQL outputs" — and the SQL is the Tier-3 input. If Dune's underlying `tokens.transfers` table is updated (re-indexed, schema-changed, retroactive corrections), the same SQL run today vs in 6 months can return different rows. This breaks the Tier 1 ⟶ Tier 3 verification claim in CLAUDE.md.

Recommend: pre-pin that Tier 2 includes a **frozen snapshot of Dune query results** (saved as parquet/jsonl in `data/raw/onchain/`) — not just the SQL. The panel-builder reads the snapshot, not Dune live. Document the snapshot date + the SQL that produced it. Reproducibility flows snapshot ⟶ Tier 1; the SQL itself is a sub-Tier-2 artifact.

---

## Nits (MAY fix)

### NIT-1. §4.2 magnitude floor "Tail-distance ≥ 1.0% on at least one historical episode" trivially satisfies via March-2023 12.6%

The magnitude floor is not actually a binding constraint — it's already satisfied by the fixed historical fact of SVB. This is not a true pre-pin; it's a declarative statement. Recommend: remove from §4.2 magnitude floor row or replace with a forward-looking floor (e.g., "posterior median of 1-year ahead 99%-conditional tail ≥ 2%").

### NIT-2. §4.3 ρ ∈ [0, 1] sign expectation

ρ < 0 is possible if cohort dis-saves (CF_t shrinks while E_t > 0). Spec acknowledges this in the HALT trigger but the sign-expectation row says `ρ ≥ 0`. Inconsistent — relax to "ρ_t real-valued; ρ̄ ≥ 0 expected; ρ̄ < 0 triggers HALT." (Also covers MUST-3 second HALT.)

### NIT-3. §6 trio-discipline notebook 06 (verdict consolidation) has no clear input-vs-output separation

Notebook 06 "PASS/PARTIAL/FAIL/NON-RETIREMENT verdict consolidation" risks becoming a re-run of earlier notebooks under different parameterizations — a fishing surface. Recommend: pre-pin that Notebook 06 consumes only the parquet outputs of Notebooks 02-05 (no recomputation) and produces verdict via a deterministic decision function over those outputs. The decision function logic should be in §7 verdict criteria, fully pre-specified, no notebook-level fiddling.

### NIT-4. §11 cross-references mention `simulations/dev_ai_cost_v2/jsonl_io.py` patterns

Good pattern reuse. Make this explicit in the new `simulations/d1d_d4_joint/utils/` plan: reference the existing module path and indicate which patterns are being borrowed (transient Pydantic validator? row-schema TypedDicts?). Saves a Phase-1 audit cycle.

### NIT-5. §4.1 lag "k=0-1 secondary; k>3 BANNED"

Why is k=2 in the gap? Either it's primary, secondary, or banned. State this precisely.

### NIT-6. §8 M-sketch belongs to Stage 2 per CLAUDE.md staging discipline

§8.1 long-COPm / short-USDC on Mento — Mento broker volume is $41K/day per Salvage Path 4. The M-sketch is correctly labeled "ideal-scenario" per CLAUDE.md but the §8.3 claim "measurement channel = deployment channel" overstates: measurement is on Bitso/Lemon hot wallets, deployment would be on Mento broker. Different on-chain venues. Tone down to "measurement and deployment share the same chain stack" or similar.

---

## Pre-pin sufficiency audit (per-field check of §4.1 / §4.2 / §4.3)

### §4.1 D1.D side — 7 fields declared

| Field | Sufficient? | Issue |
|---|---|---|
| Y | YES | concrete + operational |
| X | **PARTIAL** | spline interpolation residual structure not addressed in the X declaration itself — see MUST-1 |
| Sign | YES | β > 0 explicit |
| Magnitude floor | YES | β ≥ 0.10 |
| Lag | **PARTIAL** | k=2 unspecified — see NIT-5 |
| Primary specification | **NO** | unit-root / cointegration testing not pre-pinned — see MUST-1; γ-control dual mechanism — see SHOULD-1 |
| Colombia-share scalar | YES | 20% central + sensitivity 10/35 |
| HALT trigger | YES | β CI + sensitivity-arm sign-concordance |

**§4.1 missing**: cointegration / unit-root pre-test gate (MUST-1); choice between level-spec and Δ-spec conditional on cointegration result (MUST-1); single-primary commitment for FWER (MUST-4).

### §4.2 D4.1 side — 8 fields declared

| Field | Sufficient? | Issue |
|---|---|---|
| Y | YES | compound-Y decomposition per D4-CR Blocker 1 closure |
| X | YES | u=$0.99 explicit |
| Sign | YES | β > 0 |
| Magnitude floor | NIT-1 | trivially satisfied by SVB |
| Lag | YES | k=0 only |
| Primary specification | **PARTIAL** | pooled vs USDT-only as competing arms not pre-pinned (SHOULD-2) |
| Pooled prior | YES | ξ ~ Normal(0.03, 0.10²) truncated; σ ~ LogNormal |
| Inference | YES | GPD MLE + profile-likelihood CI + jackknife |
| Power floor | YES | demonstration-grade per CORRECTIONS-A |
| HALT trigger | YES | Fermi cohort failure OR genuine event count <2 |

**§4.2 missing**: USDT-only-prior sensitivity arm (SHOULD-2); forward-looking magnitude floor (NIT-1).

### §4.3 Joint ρ — 5 fields declared

| Field | Sufficient? | Issue |
|---|---|---|
| ρ_t definition | **NO** | wallet-set non-overlap unresolved (MUST-2); ratio-estimator instability untreated (MUST-3); scalar asymmetric role (SHOULD-4) |
| Sign | NIT-2 | ρ ≥ 0 inconsistent with HALT trigger which catches ρ̄ < 0 |
| Magnitude floor | YES | ρ̄ ≥ 0.05 |
| Decomposition | **NO** | partition assumed; not testable as stated (SHOULD-3) |
| HALT trigger | **PARTIAL** | only catches ρ̄ < 0; missing ρ̄ > 1.5 or |ρ_t| outlier (MUST-3) |

**§4.3 missing**: most fields. This is the weakest pre-pin block in the spec. Regime threshold (mentioned in review focus #6) is not pre-pinned — what defines a "regime" for the "regime-conditional ρ" mentioned in §6 Notebook 04? Calm vs depeg-event months? Pre-pin the regime definition before any conditioning is done.

**§4.3 missing — explicit regime definition**:

Pre-pin in §4.3:

> **Regime definition (pre-committed)**: month t is in regime `depeg-stress` if any day in month t has `usdc_price < 0.99` for ≥1 day persistence (per D4.2 GENUINE classification rule). Otherwise `calm`. Regime-conditional ρ̄ reported by regime. Conditioning on any OTHER variable post-hoc is BANNED.

Without this, "regime-conditional ρ" in §6.04 is a fishing surface.

### §4 cross-cutting

| Sufficiency dimension | Status |
|---|---|
| All 3 pre-pin tables explicit before data | YES (declarative) |
| Single primary specification per side | **NO** for §4.1 (level vs Δ ambiguous), **NO** for §4.2 (pooled vs USDT-only) |
| FWER protection | **NO** (MUST-4) |
| Aggregation level for ρ̄ | **NO** (monthly mean-of-ratios vs ratio-of-means not pre-pinned — MUST-3) |
| Layer C deferral acknowledgment | YES (§13.4) but **see Composite-vs-wage attribution note below** |

### Composite-vs-wage attribution (review focus #7)

Spec §13.4 acknowledges this as an open item but does not pre-commit a bias direction. The review focus correctly identifies the ambiguity:

- If speculator round-trips dominate composite inflow → E_T overstates wage flow → ρ̄ underestimates true wage→capital rate.
- If wage flows dominate → composite ≈ wage → ρ̄ accurate.

For demonstration-grade Stage-1, this is acceptable **only if pre-committed as a one-sided interpretation**: "ρ̄ reported is a LOWER BOUND on the true wage→capital transmission rate, contingent on composite-inflow being weakly more speculator-weighted than wage-weighted. The reverse (composite more wage-weighted than speculator) would push ρ̄ down, but is implausible given Bitso/Lemon CEX inflows are dominated by retail flows of which speculative trading volume is substantial."

Recommend: add this as a §4.3 pre-pin row "Bias direction (Layer C deferred)" so it's a commitment, not a §13 footnote.

---

## Summary of required v0.2 amendments

To clear CONDITIONAL_APPROVE to APPROVE_WITH_NITS:

1. **MUST-1**: §4.1 pre-pin unit-root / cointegration gate + spline-aware HAC bandwidth.
2. **MUST-2**: §4.3 pre-pin intersection vs aggregate-bias vs lower-bound interpretation of ρ.
3. **MUST-3**: §4.3 pre-pin denominator floor + ratio-of-means as primary aggregation + second HALT on |ρ̄| > 1.5.
4. **MUST-4**: §4 + §7 single-primary commitment + sign-concordance as the only multi-arm rule.

SHOULD-1 through SHOULD-5 should be addressed in v0.2 but can be deferred to v0.3 if user prioritizes velocity. NITs are optional.

The spec's intent is correct: directly measure the wage→capital transmission rate on the rail that would also be the deployment rail. The framing as demonstration-grade Stage-1 is honest. The transparency-condition §0.8 compliance is strong. The anti-fishing posture in §3 + §14 is real. **What's missing is the econometric machinery to ensure the headline quantity ρ̄ is actually identifiable, not just defined.** The MUST-fixes above plug that gap pre-implementation, which is exactly when they're cheap.

---

**Reviewer recommendation:** the user should sign a CORRECTIONS-B block addressing MUST-1 through MUST-4 before any Week-1 Dune query execution. Code execution under v0.1 would burn implementation effort on a spec whose primary regression is not identified.

**Pair this CR review with the Reality Checker review per §12. The two are complementary, not redundant: RC validates data feasibility; CR validates that the math works conditional on data feasibility being already established.**
