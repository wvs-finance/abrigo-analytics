# Reality Checker — D1.D + D4 Joint Iteration Spec v0.1

**Reviewer:** Reality Checker (default-NEEDS_WORK, evidence-based)
**Date:** 2026-05-18
**Target:** `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.1 (254 lines)
**Scope:** Reviewer focus items 1–9 supplied by the orchestrator

---

## Verdict

**NEEDS_WORK** — the spec is structurally sound and inherits good anti-fishing
posture from spec v0.3 §0.8 + the gate verdicts, but contains four critical
issues that would silently bias the headline quantity ρ_t and one binding
transparency-condition violation. None is unfixable; all are pre-implementation
spec-level corrections. Resubmit as v0.2 after addressing the four CRITICAL
items below; SHOULD items can be folded in at v0.2 or v0.3.

The spec is NOT ready to dispatch Notebook 01 in its present form. Joint-identity
non-overlap (§13 open item #3), Layer-C conflation (§13 open item #4), and
spline-induced serial correlation (§13 open item #2) are all admitted in the
spec as open items but are not yet resolved — implementation cannot proceed
until they are. The transparency standing rule (`feedback_d1_transparency_continuation.md`)
is partially implemented but inconsistent across §7 verdict criteria.

---

## Critical issues (MUST fix)

### C1. Joint identity `CF_T = E_T − L_T` is not actually a panel-level identity (Open item #3)

**Evidence.** §1 states the identity holds at the panel level. §13 item #3 admits
"D1.D inflow and D4.1 wallet balance are measured on DIFFERENT wallet sets … 
overlap is 30-60% per D4.1 findings, but the identity is exact only on the
*overlap*." The salvage CONSOLIDATION.md confirms 30-60% overlap. The current
draft does not resolve this — it flags it as an open item for the reviewer.

**Why this is critical.** The headline quantity is `ρ_t = ΔCF_t / E_t`. If E_t
is measured on wallet-set A (Bitso/Lemon CEX inflows, all chains) and CF_t is
measured on wallet-set B (USDC holders broadly, 242K Fermi cohort), then for
any single t:

- The non-overlap portion of B accumulates CF without any E in the numerator-
  denominator pair → ρ̄ biased **upward** (saver-only wallets contribute ΔCF
  with no matching E).
- The non-overlap portion of A pays E that exits the on-chain rail entirely
  (off-ramp to bank, withdrawals, consumption) and never appears in ΔCF →
  ρ̄ biased **downward** for those flows.

These biases do not cancel; they have different magnitudes and likely
different cyclical behavior. The headline ρ̄ ≥ 0.05 PASS threshold (§4.3,
§7) is therefore **a measurement of an aggregation, not of a population
transmission rate**. A PASS at ρ̄=0.05 could be entirely explained by saver-
only wallets that never received wage flow on-chain.

**Required fix.** The spec must either:

1. Restrict CF_t to the overlap set explicitly: define CF^overlap_t =
   sum of balances on wallets that received ≥1 Bitso/Lemon CEX-tagged
   inflow in a 6- or 12-month look-back window. Then ρ_t = ΔCF^overlap_t /
   E_t is identity-coherent. The cost is a 40-70% reduction in cohort size,
   which must be disclosed under §0.8. OR
2. Decompose ρ_t into three additive components — overlap-coherent
   transmission, saver-only inflation, and wage-only off-ramp — and pin
   the PASS threshold on the overlap-coherent component only. The
   saver-only and wage-only components are then reported as boundary
   diagnostics, not as the verdict quantity. OR
3. Drop the headline-ρ framing and report E_t and ΔCF_t as two separate
   β-estimates against their macro anchors, with the joint identity
   downgraded to an interpretive narrative not a quantitative claim.

Without one of these, the verdict-graph in §7 is uninterpretable. The current
spec admits the problem (good) but defers it to the reviewer (not good).

### C2. Layer C conflation has a directional bias the spec does not articulate (Open item #4)

**Evidence.** §1: "E_T … = monthly USDC+USDT inflow to Bitso/Lemon hot wallets
× Colombia-share scalar." §13 item #4: "Phase 1 treats composite stablecoin
inflow as wage+savings indicator. Reviewer should flag whether this conflation
makes ρ_t under- or over-estimate the wage→capital rate." Salvage
CONSOLIDATION.md §"Gap B" admits: "all stablecoin inflow as wage+savings
composite … magnitude bias toward wage flow (savings inflows are smaller and
less time-clustered)."

**Why this is critical.** The composite includes (a) wage receipts (true E),
(b) saver round-trips (USDC bought on the exchange to hold — already inside
the cohort, NOT a new E), and (c) speculator round-trips (USDC bought to
trade, exits the rail same-month). Effect on ρ_t = ΔCF_t / E_t:

- Speculator round-trips inflate E_t (denominator up) without changing CF_t
  net of round-trips → ρ̄ **biased toward zero**, opposite to what §13
  item #4 implies. This is the opposite direction to the C1 saver-only-non-
  overlap bias. The two biases can partially cancel for the wrong reason
  — producing a "moderate" ρ̄ that looks correct but is actually two large
  errors offsetting.
- The CONSOLIDATION.md claim that "magnitude bias toward wage flow" is
  about the *level* of the composite, not the *direction* of the ρ_t
  bias. The spec inherits this language without re-deriving the ρ_t
  sign-of-bias question.

**Required fix.** The spec must include a bias-direction table in §4.3 or
§13 that decomposes the composite into wage / saver-roundtrip / speculator-
roundtrip components, states the sign-of-bias on ρ_t for each, and commits
a Phase-1 disclosure language that does NOT claim ρ_t measures the wage→
capital transmission rate — it measures *a composite ratio whose sign relative
to true transmission is theoretically ambiguous in Phase 1*. The §1 framing
("ρ is the post-Keynesian wage→capital ratchet rate the Abrigo framework was
designed to measure") is too strong for the Phase-1 composite and must be
walked back.

### C3. Quarterly→monthly cubic spline for Banrep services-credit USD introduces
residual serial correlation HAC may not handle correctly (Open item #2)

**Evidence.** §5.2: "Banrep BoP services-credit — Quarterly 2018-Q1 → 2025-Q4,
interpolated to monthly via cubic spline." §4.1: "log(Banrep services-credit
USD) quarterly, interpolated to monthly via spline." §4.1 inference clause:
"HAC L=⌊T^(1/3)⌋." T=76 → L=4.

**Why this is critical.** Cubic-spline interpolation of a quarterly series to
monthly:
- Generates **deterministic** within-quarter month-to-month variation (the
  spline curvature), not stochastic variation. Two of every three monthly
  observations of X are mechanical functions of the third.
- The residual ε_t in `log Y_t = α + β log X_t + γ log spot_t + ε_t` will
  therefore exhibit a 3-month deterministic structure — large at quarter
  boundaries, small mid-quarter — that HAC with L=4 will absorb into the
  bandwidth but in a misleading way: HAC assumes stochastic mixing, not
  deterministic block structure.
- The β SE will be biased — typically downward (over-rejection) when the
  effective sample size is N/3 ≈ 25 quarters rather than N=76 monthly
  observations.

This is not a minor methodological nit; the N_MIN=75 floor is justified by
power calculations that assume independent monthly draws. Spline interpolation
collapses the effective N by roughly a factor of 3.

**Required fix.** Three acceptable alternatives, ranked:

1. **Preferred:** Estimate the primary spec at **quarterly** frequency on
   N=28 quarters (2018-Q1 → 2025-Q4 ≈ 32; trimmed for completeness). This
   misses the N_MIN=75 floor and would require an explicit CORRECTIONS-B
   block analogous to D4's CORRECTIONS-A, with a demonstration-grade power
   acceptance. This is the honest path.
2. **Acceptable:** Keep monthly estimation but use **COP/USD spot** (already
   monthly natively per §5.2 row "Banrep TRM daily") as the **primary** X
   and demote services-credit to a quarterly-frequency robustness check.
   §4.1 currently has spot as a γ control; promote it to primary. This is
   §13 open item #2's own suggested alternative — and it should be adopted.
3. **Conditional:** Keep services-credit as primary but switch interpolation
   from cubic spline to **monthly-constant within-quarter** (step-function),
   which converts the deterministic-block problem into a mechanical 3-fold
   replication that is easier to diagnose and to deflate the effective N for
   in the SE calculation. Add a Newey-West-with-prewhitening or a cluster-by-
   quarter SE.

The current spec is silent on this trade-off; v0.2 must pick one and pin it
pre-data.

### C4. Verdict criteria in §7 do not implement the §0.8 transparency standing rule consistently

**Evidence.** §0.8 (parent spec) standing rule + `feedback_d1_transparency_continuation.md`
require that NON-RETIREMENT be a genuine fourth outcome — "data quality
insufficient to discriminate PASS / PARTIAL / FAIL." §7 lists four verdicts
including NON-RETIREMENT, BUT:

- The PASS row requires (i) β > 0 sig at α=0.05, (ii) GPD posterior excludes
  ξ ≤ −0.1, (iii) ρ̄ ≥ 0.05, (iv) coverage-scalar arms agree on sign.
- The PARTIAL-PASS row triggers if any ONE of three conditions fails.
- The FAIL row triggers if D1.D β CI contains zero OR ρ̄ < 0 OR D4.1 ξ ≤ −0.1.
- The NON-RETIREMENT row triggers only if "coverage gaps prevent discrimination
  … Layer C ambiguity dominates."

**Why this is critical.** The four rows are *not collectively exhaustive*.
Consider the realistic case where (a) D1.D β > 0 significant, (b) D4.1
demonstration-grade posterior is consistent with the prior (no new
information), (c) coverage-scalar arms agree, (d) ρ̄ ∈ [0, 0.05]. This
satisfies PARTIAL-PASS by the §7 reading (ρ̄ positive but < 0.05) — but it
also fits NON-RETIREMENT (the data was insufficient to discriminate whether
the underlying transmission rate is materially nonzero). The current §7
forces PARTIAL-PASS, which contradicts the transparency rule that says we
should be willing to call NON-RETIREMENT.

Additionally, the spec implicitly pushes toward PASS by setting ρ̄ ≥ 0.05 as
the magnitude floor. Reviewer focus item #6 asked whether the spec "pushes
toward PASS implicitly." Answer: it does, via three mechanisms:

1. The ρ̄ ≥ 0.05 floor is asserted without derivation — Why 5%? Not 10%?
   Not 1%? The spec must cite the post-Keynesian wage→capital literature
   or a prior calibration to justify this floor. Otherwise it is a
   threshold-tuning candidate (anti-fishing concern).
2. The decomposition `ρ_t = (1 − off_ramp_ratio_t) + flow_in_t / E_t` in
   §4.3 makes ρ ≥ 0 mechanically if off_ramp_ratio ≤ 1 and flow_in ≥ 0,
   even if the cohort is consumption-only — only the < 0 across-regimes
   case triggers HALT.
3. The CORRECTIONS-A signed D4.1 prior is described as "user-approved" in
   §13 item #6 — reviewer instructed not to re-litigate. This is correct
   per protocol, but the spec should still note that the prior favors the
   exponential-tail (Gumbel) domain (ξ near zero), which essentially
   guarantees that the D4.1 GPD posterior "excludes ξ ≤ −0.1" trivially
   — making criterion (ii) of the PASS row a near-tautology rather than
   a discriminating test.

**Required fix.**
(a) Restructure §7 as a 2x2 (β-sig × ρ̄-floor) matrix with NON-RETIREMENT
as the explicit cell for "Layer C ambiguity dominates OR coverage-scalar
sensitivity reverses sign AND ρ̄ within noise band." Make the four cells
collectively exhaustive and mutually exclusive.
(b) Derive or cite the ρ̄ ≥ 0.05 floor pre-data. If it cannot be derived,
demote it to a reportable quantity (no floor) and let the verdict turn on
β-sig + sensitivity-arm-agreement only.
(c) Add a row to §7 noting the D4.1 GPD pass-criterion is partially
tautological given the signed CORRECTIONS-A prior; downweight it in the
joint verdict aggregation.

---

## Strong recommendations (SHOULD fix)

### S1. Colombia-share scalar — sensitivity sweep is insufficient as currently scoped (Open item #1)

The 20% central scalar with arms at 10% / 35% (Reviewer focus item #2) does
not bias β coefficients (the spec is correct on this) but scales ρ̄ directly.
If the true scalar is 10% rather than 20%, the headline ρ̄ doubles. If it is
35%, ρ̄ halves. The spec correctly requires sensitivity-arm-sign agreement for
PASS (§4.1 HALT trigger) but does NOT require sensitivity-arm-magnitude
agreement for the ρ̄ ≥ 0.05 floor.

Recommended: require that the sensitivity sweep produce ρ̄ within ±50% of the
central estimate across all three arms before claiming a magnitude PASS. If
the 10% arm gives ρ̄ = 0.12 and the 35% arm gives ρ̄ = 0.034, the central
0.06 is not robustly distinguishable from the noise band, and the verdict
should be PARTIAL or NON-RETIREMENT, not PASS.

Additionally: the 20% central is sourced from "Bitso CO ≈ 20% of LATAM flow
per Chainalysis/Bitso public data" (CONSOLIDATION.md Gap A). The spec should
cite the specific Chainalysis report + year + page, or treat this as a Fermi-
grade input with wider 5%-50% sensitivity arms. The current 10%-35% range is
not derived; it is asserted.

### S2. Pre-2020 USDC gap and COVID-epoch dominance (Open item #5, Reviewer #5)

§5.1: panel runs 2020-01 → 2026-04 (N=76). USDC launched 2018-09. The spec
acknowledges the gap (§5.1 row "Kraken native OHLC"; D4 gate notes Binance
USDC-USDT from 2018-12 as partial fill with USDT-numeraire confound) but does
not address the structural concern that **N=76 is dominated by the COVID +
post-COVID epoch** (2020-2026) — an unusual macro regime with extraordinary
monetary expansion, capital-flow surges, and stablecoin growth that may not
generalize.

Recommended:
- Add an explicit regime-break test (Chow or Bai-Perron) at 2022-01 or 2022-06
  (post-COVID monetary normalization start) in Notebook 02 or 05. If β
  differs across regimes, report both rather than the pooled estimate.
- Disclose in §2 that external validity is "post-COVID Colombian on-chain
  rails, 2020-2026" and explicitly NOT a claim about pre-COVID or non-
  Colombian generalizability.
- The N=76 floor just barely clears N_MIN=75. There is no headroom for
  trimming bad observations. Add a pre-pin commitment: if any of the 76
  months must be trimmed (e.g., for exchange outages, tagging gaps), the
  iteration moves to PARTIAL-PASS by structural rule, not by re-fitting on
  N=74 silently.

### S3. Anti-fishing tripwire — multiple-comparison protection is under-specified (Reviewer #7)

The spec runs:
- 3 coverage-scalar arms (10% / 20% / 35%)
- 2 Banrep regimes (services-credit primary; COP/USD spot secondary)
- ≥2 lag specs (k=0 primary; k=1 secondary)
- ≥3 GPD prior arms (USDC-only; USDT cross-prior; pooled — per D4 gate)

That is 3 × 2 × 2 × 3 = 36 distinct fittings if fully crossed. Even on a
single primary, the absence of explicit Bonferroni or a single-primary
commitment is an anti-fishing risk.

Recommended:
- §4 should pin a **single primary specification** explicitly (one scalar,
  one Banrep series, one lag, one prior arm) — call it the verdict-determining
  test. All others are robustness sensitivities. The verdict is decided on
  the primary; sensitivities are reported but do not flip the verdict unless
  they flip the *sign* of the primary's β estimate (the HALT condition).
- Add a §3-line commitment that no Bonferroni adjustment is needed *because*
  the primary is singular; sensitivities are not multiple comparisons, they
  are robustness reports.
- The current §4.1 "Primary specification" is singular (good); the §4.3
  decomposition is not labeled primary vs secondary — make this explicit.

### S4. M-sketch §8 is well-scoped but should add an explicit Stage-1-only banner

CLAUDE.md staging discipline (Stage 1 empirical β → Stage 2 ideal-M → Stage
3 deployment) is satisfied in §8.3 ("NOT implemented in this iteration").
Reviewer focus item #8 confirms M-sketch is adequately scoped. However, §8.1,
§8.2, §8.3 each describe positions ("long-COPm / short-USDC on Mento", "25-
delta OTM put on USDC", "0.01% fee tier", "aUSDC or sUSDS collateral",
"σ > 10% HALT") with operational specificity that risks scope creep in
implementation.

Recommended: add a sentence at the top of §8: "All §8 content is Stage-2
reference material reproduced from the D4 gate amendments. **No code,
notebook, or test in this iteration depends on §8 details.** Stage-2 work is
out of scope for this iteration's verdict." This is a low-cost guardrail
against the "M-design ballooning back into apparatus" failure mode that
CLAUDE.md flags.

### S5. Population-scope honesty not carried through verdict criteria (Reviewer #9)

§2 explicitly discloses 15-35% in-scope, 60-85% out-of-scope. Good. But §7
verdict criteria do not carry this caveat: a PASS verdict reads "D1.D β > 0
sig at α=0.05 …" without qualifying the population claim.

Recommended: every §7 verdict row must end with a population-scope clause.
PASS = "for the crypto-rail-paid sub-cohort (15-35% of the broader USD-paid
remote-worker population)." NON-RETIREMENT = "for the in-scope sub-cohort;
the broader 60-85% remains unmeasured and structurally invisible to this
iteration." The transparency standing rule (`feedback_d1_transparency_continuation.md`)
applies at every step — including the verdict-framing step.

Additionally, the LaTeX write-up scaffold in §6 (Notebook 06) and the §10
3-week plan should both include a "scope-disclosure block" template parallel
to the per-notebook data-quality disclosure block.

### S6. Spec is missing a pre-pin commitment on what happens if D1.D PASS but D4.1 FAIL (or vice versa)

The joint identity ties the two sides together. §7 verdict criteria treat the
two sides as joint inputs to a single verdict, but the spec does not pin the
*aggregation rule* pre-data. If D1.D β is +0.15 (significant) and D4.1 GPD
posterior places ξ < −0.1 with mass 0.6, which verdict fires?

Recommended: §7 should include an explicit aggregation matrix:

| D1.D verdict ↓ \ D4.1 verdict → | PASS | DEMO-PASS | FAIL |
|---|---|---|---|
| PASS | Joint PASS | Joint PARTIAL | Joint PARTIAL |
| PARTIAL | Joint PARTIAL | Joint PARTIAL | Joint FAIL |
| FAIL | Joint FAIL | Joint FAIL | Joint FAIL |
| NON-RETIREMENT | any → NON-RETIREMENT | NON-RETIREMENT | NON-RETIREMENT |

The current §7 leaves this implicit. Pin it pre-data.

---

## Nits (MAY fix)

### N1. §1 line 17: the identity `CF_T = E_T − L_T` is presented as the FINANCILATION
framework's identity. The spec attribution to `FINANCILATION.md` is correct,
but the post-Keynesian reader will recognize this as the Kalecki-Levy national-
income identity at the household level. Add a parenthetical "(Kalecki-Levy
household-flow identity, post-Keynesian closure)" or similar to anchor the
econometric reader.

### N2. §4.1 table row "Magnitude floor | β ≥ 0.10 (elasticity SD-units of Δlog Y)"
— the CLAUDE.md anti-fishing invariant is MDES_SD = 0.40. β ≥ 0.10 in
elasticity SD-units is NOT MDES_SD = 0.40 unless the SD of log Y maps to
0.40 SD-units of the elasticity scale, which is not derived. The relationship
between an elasticity floor and the SD-unit floor needs an explicit derivation
or a CORRECTIONS-C block.

### N3. §5.1 lists Tron in the chain set. Bitso/Lemon hot-wallet tagging on
Tron is materially harder than on EVM chains (different address formats,
different subgraph coverage). The spec should either confirm Tron tagging
is in place (Etherscan-equivalent: tronscan.org) or remove Tron from the
chain set with an N-impact note.

### N4. §6 notebook list does not cite the established Pair-D notebook trio
discipline (`memory/feedback_notebook_trio_checkpoint.md`). The trio
HALT-checkpoints column says "YES" for all 6 notebooks but the structure
of which (why/code/interpretation) trios are HALT-checkpoints vs single
cells is left implicit. Add a per-notebook trio count.

### N5. §9 sub-package scaffold places `gpd_pot.py` under `modules/` (Callable
tier) — but GPD MLE is typically iterative and may carry state across
profile-likelihood evaluations. Confirm this fits the frozen-dataclass +
__call__ stateless transform pattern, or move to `utils/` with a class-with-
__init__.

### N6. §3 anti-fishing invariants line "All pre-pin fields … declared BEFORE
any data is touched (§4)" — but D4.1 data has been touched extensively in
the D4 gate (CryptoCompare pulls, GPD fits in `02_depeg_events/data/`). The
D4.1 pre-pin is therefore "post-pin" on the D4 gate data, "pre-pin" only on
the joint iteration. This is the correct posture per CORRECTIONS-A but the
spec should be explicit that D4.1 pre-pin = "frozen at D4 gate close" not
"declared BEFORE any data."

### N7. §10 week-3 plan compresses "Notebook 01-06 execution + HALT-checkpoint
trio review + PASS/PARTIAL/FAIL/NON-RETIREMENT verdict + LaTeX write-up
scaffold" into a single week. This is aggressive given the spec's complexity
(6 notebooks, 4 verdict paths, 3 sensitivity arms, joint-identity aggregation,
3-way review at close). Realistic estimate: 2-3 weeks for week-3 alone.

---

## Open questions for the spec author

1. **Joint-identity overlap (C1).** Of the three resolution paths (restrict
   to overlap, decompose additively, drop headline ρ), which does the author
   prefer? The cost-benefit differs substantially across them.

2. **Spline alternative (C3).** Will the author accept the §13-item-#2 self-
   suggested alternative (promote COP/USD spot to primary, demote services-
   credit to quarterly robustness)? If not, what motivates retaining the
   spline-on-services-credit as primary?

3. **ρ̄ ≥ 0.05 floor (C4 / S1).** Where does the 5% magnitude floor come from?
   Pre-Keynesian household saving rate (Colombia 5-10% historically)? Crypto-
   rail-conditional retention from prior literature? Or asserted ex novo?
   This needs a citation or a CORRECTIONS-C block.

4. **NON-RETIREMENT cell exhaustiveness (C4 / S6).** Will the author adopt
   the 2x2 verdict matrix structure, or keep the current narrative §7? The
   matrix forces collectively-exhaustive cells and is harder to silently
   threshold-tune.

5. **Stage-2 firewall (S4).** Does the author commit that §8 content will
   not be referenced in any Notebook 01-06 cell or in any §9 sub-package
   module? This is the test for Stage-1 stage discipline.

6. **Multiple-comparison single-primary commitment (S3).** Does the author
   accept that the verdict is decided on the singular primary, with
   sensitivities as reports not as verdict-flippers (except via HALT-sign-
   flip)? Confirm explicitly in v0.2.

7. **Multiple wallet sets — chain coverage (N3).** Is Tron tagging in
   the Dune query bundle confirmed or aspirational? If aspirational,
   what is the contingency if Tron data is unavailable at Week-1 close?

---

## Summary of evidence

- Spec read in full (254 lines, all 14 sections).
- Cross-referenced against parent spec v0.3 §0.5–§0.11 (existence of
  CORRECTIONS-A, transparency standing rule §0.8, joint workstream §0.9).
- Cross-referenced against D1 G1 gate decision (75K Fermi central; 15-35%
  coverage; Path 4 dominance; 30-60% D1.D↔D4.1 overlap).
- Cross-referenced against D4 gate decision (USDC N=1 + USDT N=14 cross-prior;
  3 spec amendments; CORRECTIONS-A signed; ξ pooled-prior near zero).
- Cross-referenced against `feedback_d1_transparency_continuation.md` (data-
  quality disclosure block at every step; NON-RETIREMENT as honest outcome).
- Cross-referenced against CLAUDE.md anti-fishing invariants (N_MIN=75,
  POWER_MIN=0.80, MDES_SD=0.40, pre-pin discipline, HALT chain).
- Cross-referenced against salvage-paths CONSOLIDATION.md (Path 4 dominance
  + Gap A + Gap B specifics).

The four CRITICAL items are not stylistic — each one, left unaddressed, would
produce a verdict in §7 that does not correspond to the underlying
transmission-rate parameter the iteration is named after. The seven STRONG
recommendations tighten the anti-fishing posture and the transparency
discipline. The seven nits are cosmetic / footnote-level.

**Verdict: NEEDS_WORK.** Resubmit as v0.2 with C1–C4 resolved and S1–S6
folded in or explicitly declined with reasoning.
