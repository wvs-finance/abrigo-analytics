# Model-QA Re-Review — E10 GSPS v0.3 Convex Multi-Currency Design

**Reviewed artifact:** `docs/specs/2026-05-20-e10-gsps-v0.3-convex-multicurrency-design.md` (v0.3 DRAFT, 391 lines)
**Reviewer role:** Model QA Specialist — closure-focused re-review of the 3 v0.2 Model QA Criticals + stress-test of the new G≈8 design
**Prior reviews:** `ModelQA_review_e10_v0.2.md` (this reviewer, NEEDS WORK, 3 Critical); `RC_review_e10_v0.2.md`
**Date:** 2026-05-20
**Posture:** read-only. No spec edits, no code, no simulation. Decomposition algebra verified (sympy unavailable; identity confirmed from the definition of variance — see Algebra note).

---

## Verdict: PARTIAL — NOT a PASS

A PASS requires all 3 prior Criticals CLOSED and no new Critical. v0.3 closes **two** of three
cleanly, leaves **C-2 PARTIALLY-CLOSED** on a genuine firewall question, and the new G≈8-cluster
identification design raises **one new Critical (N-1)**. The v0.3 revision is a substantial, honest
improvement — the NON-FANTASY restoration, the surface reframe, two-way FE, and the dual inference
arm are all real fixes — but the spec as written cannot deliver a confirmatory or even cleanly
demonstration-grade vol-on-vol verdict with 8 currency clusters, and §11 open item 1 flags a real
firewall breach the spec resolves only by assertion.

**New Critical count: 1 (N-1).** Prior-Critical closure: C-1 CLOSED · C-2 PARTIALLY-CLOSED · C-3 CLOSED.

---

## Prior-Critical closure verification

### C-1 (FX-variance share circular) — **CLOSED**

v0.2 routed `share = Var(ΔlogFX)/Var(Δlog cost)` through the §9 ladder as an empirical number,
though its denominator is a simulator output and `∂share/∂Var(ΔlogQ) < 0`. v0.3 §4.3 + §7 field 2
demote the share from a verdict number to a **calibration-conditional sensitivity surface** over the
anchored Q-volume range, and §7 field 7 / §9 define every verdict against the *whole surface*, not a
point. This is resolution (a) from my v0.2 C-1 prescription, adopted faithfully.

**Does the surface genuinely de-circularize, or does circularity move into the anchored range?**
This was the deepest finding and deserves a rigorous answer. The honest assessment: the surface
**materially de-circularizes but does not fully eliminate** the dependence — and v0.3 is honest
about exactly this. The circularity does *partly* relocate into how the anchored range is set
(§6.2: user's own logs as centre, researched proxies as bracket). But this is a *real* escape, not
a softer restatement, for three structural reasons:

1. **The verdict object changes type.** A point share can be moved to either side of a threshold by
   a single calibration choice. A *surface over a range* cannot — §7 field 7 HALT conditions fire on
   "across the WHOLE anchored range," so no point-calibration manufactures a PASS. The degree of
   freedom that survives is the *range itself*, which is lower-dimensional and externally anchored.
2. **The range centre is anchored to observed data**, not chosen. §6.2's user-own-logs anchor is the
   v0.1 NON-FANTASY clause restored. The modeler no longer picks `Var(ΔlogQ)`; they inherit it from
   a real trace. The residual freedom is the *bracket width* (proxy-set choice), which is narrower
   than v0.2's unbounded freedom.
3. **The verdict language is range-explicit** ("FX vol is the dominant risk *for Q-volume in [the
   anchored range]*", §4.3) — the verdict is no longer falsely unconditional.

Residual concern (downgraded to Weak W-1 below, not Critical): the *bracket width* is still a
modeler choice and a wide bracket can make the surface straddle the break-even (→ PARTIAL), a
narrow one can keep it one side. The §6.2 proxy set is named but its width is not pinned. This is a
softer version of the same problem — but it is **bounded, named, and anti-fishing-visible**, where
v0.2's was unbounded and hidden. C-1's core defect ("decisive object is a function of *free*
simulator parameters") is genuinely fixed: the parameters are no longer free. **CLOSED.**

### C-2 (0.30 threshold unanchored) — **PARTIALLY-CLOSED**

v0.3 retires the unanchored 0.30 and replaces it with the **fitted-hedge break-even share** (§4.4,
§8 field 3, §13.2) — the FX-variance share at which the fitted convex payoff's expected return
covers its stream-funded premium. This is exactly the economic anchor I prescribed in v0.2 C-2: the
threshold is now *derived from hedge economics*, not asserted. The derivation logic (expected
convex payoff as a function of realized FX variance and strike/range geometry, set against the
pinned premium fraction) is sound in principle.

**Why only PARTIALLY-CLOSED — the firewall question (§11 open item 1).** The break-even is computed
in §13, the **Stage-2 M-sketch**, and imported into the §8 **Stage-1 pre-pin** before lock (§5.4
states this explicitly: "a pinned Stage-2-derived input to the Stage-1 verdict ladder"). This is a
genuine Stage-1/Stage-2 firewall tension, and §11 item 1 flags it honestly. My assessment:

- It is **not a fatal breach**, because the break-even is a *parameter* (a number derived from
  payoff geometry and a premium fraction), not an *estimation result* — it carries no information
  from the Stage-1 data into the Stage-1 verdict. The firewall exists to stop Stage-2 *findings*
  contaminating Stage-1 *identification*; a pinned geometric constant does not do that.
- But it is **not cleanly closed either**, for two reasons. (i) The break-even depends on the
  *fitted* payoff, and §13.2 says the payoff is "fitted to the exposure structure the §4
  decomposition reveals" — i.e. the threshold depends on a Stage-1 output (the decomposition). That
  is circular: §8 field 3 (threshold) ← §13 (fitted payoff) ← §4 decomposition (Stage-1 estimate).
  The spec must pin the payoff geometry to an *ex-ante* exposure assumption, not the realized
  decomposition, or the threshold is post-data. §5.4 / §13.2 do not currently rule this out.
  (ii) §13.4 states the M-sketch "cannot be deployed" and the premium fraction is an ideal-scenario
  quantity — so the break-even is derived against an *ideal-scenario* premium, never a market one.
  That is acceptable for a demonstration-grade verdict but should be stated as a threshold caveat.

**To fully close C-2:** pin the fitted-payoff geometry (strike/range, premium fraction) to an
ex-ante exposure assumption declared in §13 *before* E10.2 runs the decomposition, and state
explicitly that the break-even uses an ideal-scenario premium. As written, the threshold risks
being a function of the very Stage-1 estimate it gates. **PARTIALLY-CLOSED.**

### C-3 (simulator uncalibrated) — **CLOSED**

v0.2's simulator had no calibration anchor; λ(t), `Q_low`, and the Q–FX dependence were all
unpinned. v0.3 resolves all three:

- **NON-FANTASY anchor restored (§6.2).** Q-volume range *centre* = user's own observed query
  logs; *bracket* = researched proxies. This is the v0.1 clause v0.2 dropped, restored as the
  simulator's calibration anchor. Direct fix of the C-3 defect.
- **Five λ(t) modulations pre-committed (§6.3):** diurnal/weekday cycle, burstiness/overdispersion,
  event spikes, month-end seasonality, secular drift. These are specified concretely enough to be
  non-fishable *as a list* — each is a named, recognized stochastic feature, and the spec correctly
  pre-commits that the *magnitude* (not the presence) is what the §4.3 surface sweeps. Modulation 2
  (overdispersion) explicitly answers my v0.2 W-1: a pure NHPP is equidispersed and understates
  `Var(ΔlogQ)`; v0.3 requires an overdispersion layer. Good.
- **`Q_low` pinning rule (§2.4)** and **Q–FX dependence pre-pinned (§6.4):** independence in the
  primary (Cov ≈ 0 by construction), coupling as a declared sensitivity arm. Both were absent in
  v0.2; both now have a stated, frozen rule.

One residual: §6.3 lists *which* modulations but not their *functional forms* — the magnitude sweep
is anchored, but the *shape* (e.g. is overdispersion a negative-binomial mixing layer or a
Cox-process intensity?) is deferred to E10.1. This is acceptable because the sweep is over
magnitude and the §6.2 anchor pins the centre, but E10.1's calibration note must lock the
functional forms before any run (flagged as W-2). The C-3 *defect* — no anchor, fantasy-exposed —
is genuinely fixed. **CLOSED.**

---

## NEW FINDINGS

### N-1 (Critical) — G≈8 currency clusters cannot support a credible vol-on-vol verdict; the dual-arm gate does not rescue it.

This is the central new concern and it survives stress-testing as a **Critical**. v0.3's panel is
8 currencies × ~30 months ≈ 240 cells, with identification resting on **G ≈ 8 currency clusters**
(§8 explicitly: "the binding inference dimension is G ≈ 8, not the cell count"). Three independent
problems compound:

**(a) Wild cluster bootstrap with 8 clusters is below the danger threshold, not at its edge.**
My v0.2 S-1 flagged G = 12 as borderline. v0.3 *reduced* the panel to 8 currencies (resolving RC
BLOCK-1's panel-axis problem) — which moved the cluster count from borderline into the danger zone.
The literature (Cameron-Gelbach-Miller; Webb 2014; MacKinnon-Webb) is consistent: WCB size
distortion is tolerable down to roughly G ≈ 12 with Webb six-point weights, degrades materially
below that, and is *worst for one-sided tests near the null* — which is exactly the §9 geometry
("CI on the share excludes the break-even from below"). §7 inference concedes this honestly ("Eight
clusters is below the borderline-safe range"). Webb weights help but do not close an 8-cluster gap;
they were designed to extend validity *toward* G ≈ 12, not *to* G ≈ 8. The honest reading: the
primary inference arm is **known to be size-distorted in the exact direction the verdict needs**.

**(b) The permutation arm has thin support — 8 units do not yield enough distinct permutations.**
§11 item 2 asks whether 8 currencies give adequate permutation support. They do not, for the
relevant statistic class. A sign/assignment statistic over 8 units yields **2^8 = 256** distinct
sign assignments; a randomization over orderings yields 8! = 40,320 but a *vol-on-vol slope* sign
statistic is effectively a sign-flip statistic, so the relevant support is ~256. The smallest
attainable one-sided p-value is then ≈ 1/256 ≈ 0.0039 — *coarse but not fatal on its own*. The
deeper problem: with two-way FE already absorbing 8 currency + ~30 month parameters, the
permutation null is over a residualized statistic with very few effective degrees of freedom, and
permutation inference assumes exchangeability of currencies under the null — 8 heterogeneous
currencies (6 EM + EUR/GBP) are **not exchangeable**: EUR/GBP have structurally different FX-vol
regimes, so the permutation distribution mixes non-exchangeable units and the resulting p-value is
not interpretable as a clean randomization test. The arm is *weaker* than §7 presents it.

**(c) "Both arms agree" is the wrong PASS gate.** §11 item 2 asks exactly this. Requiring two arms
to *agree* sounds conservative but is not: if both arms share the same small-G weakness (and they
do — both are small-G inference on the same 8 clusters), agreement is *correlated*, not
*independent confirmation*. Two correlated, individually-unreliable tests agreeing does not yield a
reliable verdict — it yields two unreliable verdicts that happen to point the same way. The correct
posture is the opposite: treat *disagreement* as informative (→ PARTIAL, which §9 does) but do
**not** treat *agreement* as a PASS-grade signal. A genuinely conservative rule would require the
*more conservative* arm's CI to clear the threshold, not both.

**(d) Two-way FE is estimable but DoF-thin.** 8 currency FE + ~30 month FE = ~37 absorbed
parameters from ~240 cells leaves ~200 residual DoF at the *cell* level — fine arithmetically. But
month FE absorbs the common global FX-vol factor (the intended S-2 fix), and what remains is
*idiosyncratic per-currency* vol variation across only 8 currencies. If the global factor is large
(it usually is for EM FX vol — risk-off co-movement), month FE absorbs most of X's variation and
the identifying variation collapses toward the 8-cluster between-currency contrast. My v0.2 S-2
caveat applies in force here: if month FE absorbs nearly all FX-vol variation, *that is itself the
finding* — the cohort's FX risk is a global factor, not a hedgeable per-currency micro-risk — and
it bears directly on the §13 instrument choice. v0.3 does not address this caveat.

**Bottom line on G≈8.** E10 v0.3 as specified is **structurally underpowered for a confirmatory or
clean demonstration-grade vol-on-vol verdict.** The honest options, in order of preference:

1. **Demote the §9 PASS rung to a descriptive/illustrative posture.** Rename PASS → "ILLUSTRATIVE-
   SUPPORTIVE" and state that with G ≈ 8 no rung asserts statistical confirmation — the surface and
   break-even comparison are *descriptive*. This is consistent with §7 field 5's already-honest
   "demonstration-grade" posture; v0.3 just needs to stop the §9 PASS language ("FX volatility
   confirmed as the dominant cost-stream risk") from over-claiming what 8 clusters can deliver.
2. **NON-RETIREMENT-on-power.** If a confirmatory verdict is the goal, 8 clusters cannot reach it;
   honestly park the empirical β-claim on power grounds, exactly as the dev_ai_cost iteration
   PAUSED on N (`dev_ai_cost_model_evaluation.md` O-2). The methods-paper §5 hook (§12) survives
   either way — §12 already says so.
3. *Not recommended:* expand the panel. RC BLOCK-1 already showed currency expansion is constrained
   by free 30-month FX availability; manufacturing clusters is anti-fishing-banned (§7).

This is Critical because §9's PASS rung, as written, promises a verdict the design cannot produce,
and the methods-paper §5 upgrade language ("upgrades to a validated convex... instance", §12) would
inherit an over-claim. The fix is a wording/posture demotion, not a redesign — but it must happen.

### N-2 (Strong) — The break-even payoff geometry must be pinned ex-ante, or C-2's threshold is post-data.

See C-2 above, point (i). §13.2 fits the payoff "to the exposure structure the §4 decomposition
reveals" — making the §8 field 3 threshold depend on a Stage-1 estimate. Pin the strike/range
geometry and premium fraction to an ex-ante exposure assumption declared before E10.2. Without
this, the "no post-hoc threshold adjustment" guarantee (§7 field 3) is not actually delivered: the
threshold moves with the decomposition. This is the unclosed half of C-2.

### N-3 (Strong) — The permutation arm's exchangeability assumption is violated by mixing EM and DM currencies.

See N-1(b). EUR/GBP are developed-market controls with structurally different FX-vol regimes from
the 6 EM currencies. A permutation/randomization test across all 8 assumes currencies are
exchangeable under the null; they are not. Either (i) run permutation inference within the EM block
only (6 units — even thinner, 2^6 = 64), or (ii) state that the permutation arm is a *concordance
diagnostic* with a known exchangeability caveat, not a co-equal inference arm. As written, §7
presents two co-equal arms; one of them rests on a violated assumption.

### N-4 (Weak) — The §6.2 bracket width is unpinned; a residual fishing surface on the surface's span.

See C-1 residual. The Q-volume range *centre* is anchored (user logs) but the *bracket width* (how
far the researched proxies spread the range) is a modeler choice, and bracket width determines
whether the §4.3 surface straddles the break-even (→ PARTIAL) or sits one side (→ PASS/NON-RET).
§6.2 names the proxy set but not a width rule. Pin a bracket rule (e.g. proxy min/max, or a fixed
multiple of the observed centre's dispersion) before E10.1. Weak, not Critical, because the surface
+ whole-range HALT design already bounds the damage — but it should be closed for completeness.

### N-5 (Weak) — λ(t) modulation functional forms deferred to E10.1.

See C-3 residual. §6.3 pre-commits the five modulations as a list but not their functional forms
(overdispersion mechanism, event-spike intensity law, drift parametrization). The magnitude sweep
is anchored; the *shape* is not. E10.1's calibration note must lock the functional forms before any
simulation run, or a shape choice at E10.1 reintroduces a (small) C-3-style freedom.

### N-6 (Observation) — The exact log-space decomposition is now correctly stated.

§4.2 states `Var(Δlog cost) = Var(Δlog FX) + Var(Δlog Q) + 2·Cov(Δlog FX, Δlog Q)` and explicitly
deletes the v0.2 "leading-order" caveat as a spec error. **Confirmed correct.** Since `c` is
constant, `Δlog cost = Δlog Q + Δlog FX` is an exact identity, and `Var(a+b) = Var(a)+Var(b)+2Cov`
is exact for *any* random variables by the definition of variance (verified: `E[(a+b)^2]−E[a+b]^2`
expands term-by-term to `Var(a)+Var(b)+2Cov` with no residual — see Algebra note). §4.2's
statement, the §5.3 ban on the level-variance object `Var(cost)` (which has no clean additive
split), and the §4.2 "no higher-order term" claim are all now correct. This closes my v0.2 S-4.

---

## §11 open-items disposition

| # | Item | Disposition |
|---|------|-------------|
| 1 | Break-even derivation timing / firewall | **Genuine — see C-2 + N-2.** Importing a *parameter* across the firewall is acceptable; importing a number that depends on the §4 decomposition is not. Pin the payoff geometry ex-ante. PARTIALLY closed. |
| 2 | Eight clusters + dual inference | **Genuine BLOCKER — see N-1.** Permutation support is thin (~256), exchangeability is violated, and "both arms agree" is the wrong gate. The honest answer is posture demotion. |
| 3 | `Q_low` pinning rule | **Acceptable.** The rule (user-log anchor + proxy bracket, value pinned at E10.1 before any run) is defensible ex ante and preserves anti-fishing discipline — pinning a *value* at E10.1 from a *rule* declared in the spec is exactly the right sequencing. |
| 4 | Q–FX independence in the primary | **Acceptable as primary.** Independence (Cov ≈ 0) is the right *primary* choice — it is the conservative null (no behavioral hedging), and coupling has a sign-relevant effect that belongs in a declared sensitivity arm (§6.4), not the primary. Confirmed. |
| 5 | Surface-based verdict operationalization | **Needs one fix.** "Across the whole range" is operationally crisp *only if* the full sweep is inspected, not just endpoints — a non-monotone surface can dip below the break-even in the interior while clearing both endpoints. §9 should state the sweep is evaluated on a grid, not at endpoints. PARTIAL vs PASS is otherwise unambiguous. |
| 6 | NGN / dropped currencies | **Genuine — see N-1.** 8 currencies is *not* comfortably adequate for the two-way-FE panel (N-1d). Dropping below 8 at E10.0 should itself trigger a HALT — confirm and add to §7 field 7. |

---

## Algebra note (verified)

`cost = Q·c·FX`, `c` constant ⇒ `Δlog cost = Δlog Q + Δlog FX` exactly (`Δlog c = 0`).
`Var(a+b) = E[(a+b)^2] − (E[a+b])^2 = (E[a^2]+2E[ab]+E[b^2]) − (E[a]+E[b])^2
= (E[a^2]−E[a]^2) + (E[b^2]−E[b]^2) + 2(E[ab]−E[a]E[b]) = Var(a)+Var(b)+2Cov(a,b)` —
**exact for any random variables, no higher-order term.** v0.3 §4.2 is correct; the deleted
"leading-order" caveat was indeed a v0.2 spec error. The level object `Var(cost)` has no such
additive split (`Var(Q·c·FX)` involves `E[Q^2 FX^2]`); §5.3's ban on it is correct.
Permutation support for 8 units: 2^8 = 256 sign assignments (min one-sided p ≈ 0.0039).

---

## Summary for dispatch

- **Verdict: PARTIAL — not a PASS.** A PASS requires all 3 Criticals CLOSED and zero new Critical;
  v0.3 has C-2 PARTIALLY-CLOSED and one new Critical (N-1).
- **Prior-Critical closure:** C-1 **CLOSED** (surface reframe genuinely de-circularizes — residual
  bracket-width freedom is bounded and visible, downgraded to Weak N-4); C-2 **PARTIALLY-CLOSED**
  (break-even is the right economic anchor, but its payoff geometry currently depends on the §4
  decomposition — a post-data threshold path — N-2); C-3 **CLOSED** (NON-FANTASY anchor restored,
  five λ(t) modulations pre-committed, `Q_low` rule + Q–FX dependence pinned).
- **New Critical count: 1** — N-1: G ≈ 8 currency clusters cannot support the §9 PASS rung; WCB is
  size-distorted below ~12, the permutation arm has thin (~256) and non-exchangeable support, and
  "both arms agree" is the wrong gate (correlated, not independent, confirmation).
- **G≈8 verdict:** **Not workable for a confirmatory or clean demonstration-grade vol-on-vol
  verdict.** E10 v0.3 should honestly demote the §9 PASS rung to an ILLUSTRATIVE/descriptive
  posture, or close on NON-RETIREMENT-on-power. The methods-paper §5 hook survives either way (§12
  already commits to this). This is a posture/wording fix, not a redesign.
- **To reach PASS:** (1) fully close C-2 by pinning the break-even payoff geometry ex-ante (N-2);
  (2) resolve N-1 by demoting the PASS rung's claim language to match what 8 clusters deliver;
  (3) fix N-3 (permutation exchangeability) and the §11-item-5 grid-sweep operationalization.
  Weak N-4/N-5 should also land. The v0.3 revision is honest and substantially improved — the
  remaining gap is the cluster-count reality, which the spec half-acknowledges but does not yet act
  on in the verdict ladder.
