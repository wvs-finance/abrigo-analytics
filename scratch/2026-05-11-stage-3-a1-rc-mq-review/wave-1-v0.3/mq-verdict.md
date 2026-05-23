# MQ verdict — A1 plan v0.2 → v0.3 predicate-change CORRECTIONS-α (scoped re-review)

**Reviewer:** Math Quality (MQ)
**Scope:** §11.2 v0.2 → v0.3 entry ONLY
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

The predicate tightening itself (`!= "short-vol"` → `== "long-vol"`) is mathematically correct and well-motivated. Two ancillary claims in the §11.2 prose are imprecise and should be tightened in a follow-up wording patch; neither invalidates the predicate change.

## Findings (severity-graded)

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| MQ-V03-FLAG-1 | Cosmetic-Material | "Negative Γ region" phrasing is loose for piecewise-linear mixed-vol primitives (call_spread, put_spread, super_bull, super_bear, zebra are piecewise-linear → Γ = 0 a.e. with delta singularities at strikes, with NEGATIVE delta-mass at the inner strike for spread/ratio configs). The precise criterion is "payoff is not globally convex in S over the verifier span" — equivalently, the distributional second derivative is not a non-negative measure. Recommend wording: "primitives that are not globally convex in S (Γ has negative distributional mass at some strike)". | Wording-only patch to §11.2 paragraph 2; predicate unchanged. |
| MQ-V03-FLAG-2 | Material | The claim that the `comparability_proof = "normalized_score"` lane is "broken for mixed-vol" because "the multiplicative correction is derived under the assumption of monotone-convex payoff" is **not algebraically supported**. The formula `max_relative_error × (1 + |Π(S_0)| / max|Π(S)|)` (replication.py:184, types.py:57-74 floor rationale) is a purely arithmetic normalization. It does not require monotone-convex inputs; it only requires `max|Π(S)| > 0` over the grid (already enforced by `peak <= 0.0` guard at replication.py:179-183). The lane is **not broken**, it is **uninterpretable**: the score is a finite real number but it no longer measures envelope-fit to a log-contract proxy, because the underlying object (σ_T Carr-Madan replication) does not exist for non-convex payoffs. Recommend reframing §11.2 sentence as: "the resulting score, while finite, would not measure σ_T-replication fidelity — it would measure linear-fit residual to a quadratic proxy on an object that is not σ_T-shaped." | §11.2 paragraph 2 sentence revision; predicate unchanged. |
| MQ-V03-NIT-1 | Cosmetic | §11.2 says "positive Γ everywhere" for long-vol primitives. The strip (reverse-IC, 4-leg) is piecewise-linear → Γ = 0 in the interior of each piece with positive delta-mass concentrated at the four strikes (sum of which is positive over the convex hull). Same imprecision as FLAG-1. Recommend "globally convex with positive Γ-measure" or "non-negative distributional Γ everywhere with strictly positive total mass". | Optional wording. |

## Math anchor verification

**PRIMITIVES.md §10 eq. (18).** `σ_T ∼ ∫₀^{S_0} P(K)/K² dK + ∫_{S_0}^∞ C(K)/K² dK`. Verified:

- OTM put payoff `P(K) = max(K − S_T, 0) ≥ 0` for all S_T.
- OTM call payoff `C(K) = max(S_T − K, 0) ≥ 0` for all S_T.
- Weight `1/K² > 0` strictly for K > 0.
- Therefore the integrand is non-negative everywhere; integral is well-defined and non-negative for any S_T ≥ 0.

This identity holds for the **continuous-strike measure** of OTM puts and calls. A primitive whose payoff can be written as a positive-Borel-measure-weighted combination of (OTM put, OTM call) payoffs inherits both (a) non-negative payoff everywhere and (b) global convexity in S (since each OTM put and call is convex and convexity is preserved under positive linear combinations and limits).

**Long-vol claim (verified).** A reverse-IC strip with K1<K2<K3<K4 and signs (long put @K1, short put @K2, short call @K3, long call @K4) has payoff = `max(K1−S,0) − max(K2−S,0) − max(K3−S,0) + max(K4−S,0)` up to additive constants — this is **globally convex** in S (V-shape with flat ATM body). Long_call_spread_strip and long_straddle are likewise globally convex. assert_long_vol_signature (replication.py:197-238) checks the empirical signature (Π(S_0)=0 floor + positive on both sides of inner body); a sufficient witness of convexity over the verifier span.

**Mixed-vol exclusion (verified, with wording caveat).** Consider call_spread: payoff = `max(S−K1,0) − max(S−K2,0)` with K1<K2.
- For S ≤ K1: payoff = 0 (flat).
- For K1 < S < K2: payoff = S − K1 (increasing linear).
- For S ≥ K2: payoff = K2 − K1 (flat).

Second derivative (distributional): `δ(S−K1) − δ(S−K2)`. The δ-mass at K2 is **negative**. So the payoff is **not globally convex** — it is concave at K2. This is the substantive content of the §11.2 claim. The phrasing "regions of negative Γ" is loose (the negative mass is a point mass, not a region) but the conclusion is correct: call_spread is not a positive linear combination of OTM puts and calls and therefore is not σ_T-replicable via eq. (18).

Same analysis applies to put_spread, super_bull/super_bear (multi-strike spread variants), call_ratio_spread (concavity from the short leg ratio), and zebra (zero-cost call-ratio-spread variant with the same concave-at-mid signature). Predicate correctly excludes all six.

**normalized_score path (FLAG-2 elaboration).** The formula `max_rel_error × (1 + |Π(S_0)|/max|Π|)` is a comparability lift that absorbs a non-zero ATM floor offset by penalizing it multiplicatively. For a call_spread with K1<S_0<K2, Π(S_0) = S_0−K1 > 0, so the multiplier is finite and > 1. The formula will run, produce a finite number, and rank the candidate. But the underlying envelope fit (centered strip vs β·log-contract-proxy) at replication.py:162-191 is a least-squares fit of a non-convex payoff to a CONVEX quadratic; the residual no longer measures σ_T-replication fidelity. The lane is operationally uninterpretable, not algebraically broken. The right framing in §11.2 is "no σ_T-replication interpretation exists" rather than "the multiplicative correction assumes monotone-convex payoff."

**Effect on conclusion.** The predicate v0.3 (`convexity_class == "long-vol"`) is the correct restriction. Both the envelope-fit path and the normalized-score path return numbers for mixed-vol candidates, but neither number bears the meaning the comparator needs (Phase-2 envelope-delta-vs-ironcondor in σ_T-replication units). Excluding mixed-vol upstream is mathematically necessary; the v0.2 `!= "short-vol"` rule was indeed a drafting slip.

**Anti-fishing check.** PRIMITIVES.md §10 is dated Stage-2 (frozen). The §11.2 anchor is ex-ante. The predicate change is motivated by mathematical correctness (Carr-Madan integrand sign), not by candidate-count tuning. No fishing concern.

## Verdict justification

ACCEPT_WITH_FLAGS. The predicate change is correct. FLAG-1 and FLAG-2 are wording-precision issues in the §11.2 prose that do not affect the executable rule; recommend a follow-up cosmetic edit but do not require a fresh Wave-1 review for the wording patch (it is strictly tightening, not loosening).

---

*MQ verdict end — 2026-05-11.*
