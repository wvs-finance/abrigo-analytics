# Model-QA Re-Review — E10 GSPS v0.5 Convex Multi-Currency Design (post-HALT, G≈5)

**Reviewed artifact:** `docs/specs/2026-05-20-e10-gsps-v0.5-convex-multicurrency-design.md` (v0.5 DRAFT, 452 lines)
**Reviewer role:** Model QA Specialist — closure re-review of the CORRECTIONS-E10-5 panel re-spec (8→5 currencies); modeling-soundness ownership at G≈5. Reality Checker covers honesty/feasibility in parallel.
**Prior reviews (this reviewer):** `ModelQA_review_e10_v0.2.md` (NEEDS WORK, 3 Critical); `ModelQA_rereview_e10_v0.3.md` (PARTIAL, 1 new Critical N-1).
**Date:** 2026-05-20
**Posture:** read-only. No spec edits, no code. DoF arithmetic computed (see Algebra note).

---

## Verdict: PASS

A PASS requires the G≈5 re-spec verified modeling-coherent and **no new Critical**. v0.5 meets
both. The CORRECTIONS-E10-5 narrowing is a genuine panel-dimension re-spec, not a redesign and
not a test tuning: it freshly pre-pins §7 field 6 only, leaves the other six pre-pin fields
frozen, and — critically — does not need a posture demotion because v0.4 already executed that
demotion (CORRECTIONS-E10-4 Fix 1). My v0.3 Critical N-1 was "G≈8 cannot support the §9 PASS
rung." v0.4 retired the PASS rung. **At v0.5 there is no inferential rung left for a thinner G
to break** — N-1 is therefore extinguished by the v0.4 fix, not re-opened by the v0.5 narrowing.

The narrowing genuinely makes the *descriptive* posture *more* defensible, not less: a thinner
identification dimension can only undermine an inferential claim, and there is none. The two
honest concerns the spec itself flags as §11 open items (bands, two-way FE) are real and I rule
on both below — but neither rises to Critical, because neither gates a verdict and the spec
already labels both as descriptive-only / non-gating.

**New Critical count: 0.** New findings: 0 Strong · 2 Weak · 1 Observation.

---

## Modeling-soundness checks at G≈5

### Check 1 — Is the iteration still coherent at G≈5? — YES.

The v0.5 logic in §0.5 / §8 / §9 holds. The chain is: v0.4 demoted E10 to descriptive-only
*because* G≈8 could not support inference; the deliverable became the §4.3 FX-variance-share
sensitivity surface, a *description*. A description does not have a power requirement — it has
a *resolution* requirement. G≈5 reduces the cross-sectional resolution of the surface but does
not make it incoherent, because the surface is a per-(currency,month) cell object (Check 5) and
is *swept across the anchored Q-volume range*, not across currencies. The currency dimension
supplies cross-sectional FX-vol *regime spread*, not the primary axis of the surface. With
COP/BRL/NGN (three distinct EM vol regimes — managed-float COP, free-float BRL, post-float NGN)
plus EUR/GBP (two DM regimes), the 5 currencies still span a non-trivial FX-vol regime range.
The surface is therefore still a "characterization" — qualified, correctly, as a 5-regime
characterization. It does **not** collapse to "5 unconnected currency-specific curves": the
shared Q-process and shared decomposition identity (§4.2) are what bind the five into one
object; the currency count sets how *finely* the regime axis is sampled, not whether the object
exists. v0.5's §0.5 claim ("G≈5 does not change the posture") is verified correct.

### Check 2 — Two-way FE at G≈5. RULING: keep two-way FE as primary; promote currency-FE-only to **co-primary descriptive**.

DoF arithmetic (Algebra note): 150 cells; two-way FE absorbs 34 parameters (1 intercept + 4
currency + 29 month); 1 slope; **115 cell-level residual DoF**. Arithmetically the within
estimator is comfortably *estimable* — it is not rank-deficient and does not collapse to "no
variation." So the spec's §7 field 6 retention of two-way FE is not wrong.

But the *identifying* content is the concern, not estimability. Month FE removes the common
global FX-vol factor; what identifies the slope is the *idiosyncratic per-currency* vol
deviation, and that lives on only 5 currencies. If the global risk-off factor is large for EM
FX vol (it usually is — my v0.3 N-1d caveat), month FE absorbs most of X's variation and the
identifying contrast is thin. v0.5 §7 field 6 states this plainly ("very thin identifying
variation"). For a *descriptive* surface this is acceptable as the primary — the surface is
still computed — but the reader cannot tell, from a two-way-FE-only run, whether thinness
reflects a real result (FX risk is a global factor, not a per-currency micro-risk — itself a
finding bearing on the §13 instrument choice) or merely the narrow panel. The currency-FE-only
arm carries the global factor *inside* the identifying variation and is the natural complement.
v0.5 lists currency-FE-only as a §7 sensitivity arm only. **Ruling: promote currency-FE-only to
a co-primary descriptive specification, reported alongside two-way FE.** Reason: at G≈5 the gap
between the two specifications *is itself descriptive information* (it quantifies how much of
the cost-stream FX-vol exposure is global vs idiosyncratic), and burying it in a sensitivity
arm hides a result the §13 M-sketch needs. This does not require a redesign — both runs are
already specified; it is a reporting-status change. Recorded as Weak W-1 (not Critical: the
surface is still produced and coherent under either specification).

### Check 3 — Descriptive uncertainty bands at G≈5. RULING: DROP both bands from the deliverable; replace with a non-statistical raw 5-currency dispersion display.

At G≈5: wild cluster bootstrap with 5 clusters is far below the ~G≈12 threshold where Webb
six-point weights keep size distortion tolerable — it is not "more illustrative," it is
*broken* as an interval. The permutation arm has support 2^5 = 32 (min one-sided p ≈ 0.031),
and — per my v0.3 N-3, unchanged — the EM/DM exchangeability assumption is violated (COP/BRL/NGN
not exchangeable with EUR/GBP). v0.5's response (§7, §9, §11 item 1) is to *keep both* with a
"hardened illustrative-not-inferential label."

That is the wrong call. A label does not change what a reader does with a plotted band: a
shaded interval on a surface plot *reads* as an uncertainty statement no matter the caption,
and at G≈5 these two bands carry no valid uncertainty content at all — the WCB interval is
size-distorted and the permutation distribution is not a valid randomization distribution.
Keeping them is the residual-inferential-claim risk §11 item 1 itself raises, and at G≈5 that
risk is realized, not hypothetical. **Ruling: drop the wild cluster bootstrap and the
permutation arm from the SURFACE-PRODUCED deliverable.** Replace them with an honest
non-statistical display: the raw per-currency surface curves overplotted (5 curves), or the
min–max / interquartile envelope of the 5 currency-specific surfaces labelled explicitly as
"observed spread across 5 currencies — descriptive range, not an uncertainty interval." That
delivers the genuine descriptive content the bands were *meant* to convey (how much the surface
moves across FX-vol regimes) without dressing 5 points as a statistical interval. This is a
Weak finding (W-2), not Critical: the §4.3 surface — the actual primary deliverable — does not
depend on the bands; §9 already states the bands do not gate any verdict. So dropping them
subtracts a misleading element and loses nothing load-bearing.

### Check 4 — The 6 untouched pre-pin fields. VERIFIED untouched and coherent at 5 currencies.

- **Field 1 (sign, β>0):** a per-cell mechanical sign gate; currency count irrelevant. Coherent.
- **Field 2 (primary object = surface + ex-ante break-even):** the surface is a per-cell object
  swept over Q-volume (Check 5); 5 vs 8 currencies changes its resolution, not its definition.
  Coherent.
- **Field 3 (material threshold = ex-ante break-even):** derived in §13.2 from ex-ante-pinned
  payoff geometry and option-premium economics — carries zero panel content, so the panel
  re-spec cannot touch it. The firewall (my v0.3 C-2 / N-2) is genuinely restored in v0.4 and
  is untouched at v0.5. Coherent. (§11 item 4 correctly carries it forward for confirmation.)
- **Field 4 (lag, contemporaneous monthly):** per-cell; currency-invariant. Coherent.
- **Field 5 (posture, descriptive/illustrative):** the load-bearing one. Verified: the posture
  was non-inferential from v0.4, so a thinner G cannot demote it further. v0.5 §0.5 / §8 / §9
  state this repeatedly and correctly. Coherent.
- **Field 7 (HALT condition):** defined against the surface over the whole anchored range, not
  a point, and against simulator-anchor failure — none of which is currency-count-dependent.
  Coherent.

The exact three-way log-variance decomposition (§4.2) and the HALT conditions are genuinely
untouched and remain coherent. Confirmed.

### Check 5 — The decomposition + surface at 5 currencies. VERIFIED structurally intact.

`Var(Δlog cost) = Var(Δlog FX) + Var(Δlog Q) + 2·Cov(Δlog FX, Δlog Q)` is an exact identity per
(currency,month) cell (verified algebraically in my v0.3 re-review — unchanged). It is a cell
object; it has no currency-count dependence. The FX-variance share is likewise per-cell. The
re-spec does not break either — confirmed.

The sharper question: the surface is swept across the Q-volume range, and the Q-process is
currency-invariant (one representative analyst, §2.2 / §6.6). So the *cross-sectional* spread of
the surface rests entirely on the 5 FX-vol regimes. Is 5 enough spread to call it a
"characterization"? My assessment: **yes, marginally — and honestly labelled.** The 5 currencies
are not 5 draws from one regime: COP (managed float), BRL (free float), NGN (post-float EM),
EUR, GBP (DM) span a genuine range of realized-FX-variance levels. The surface will show a
visibly different FX-variance share across these regimes — that *is* a characterization. It is
a coarse one, and v0.5 must (and does, §9 G-count note) label it as a 5-regime characterization,
not over-claim a continuous cross-sectional surface. The honest framing is already in §9: "a
characterized surface with honestly-labelled descriptive bands" — with my W-2 ruling, "bands"
becomes "observed 5-currency spread." With that substitution the characterization claim holds.

It is *not* the case that G≈5 makes the surface "not worth computing." The surface's primary
axis (Q-volume) is fully intact and is the methods-paper §5 contribution (§12); the currency
axis is a secondary regime-spread axis that is coarse but real. The deliverable survives.

---

## §11 open-items disposition

| # | Item | Ruling |
|---|------|--------|
| 1 | G≈5 descriptive-band labelling | **DROP both bands** (see Check 3 / W-2). At G≈5 the WCB interval is size-broken and the permutation distribution is invalid (32-point support + EM/DM non-exchangeability). A hardened label does not fix a plotted band that reads as an uncertainty statement. Replace with a raw 5-currency min–max/IQR spread display explicitly labelled non-statistical. Bands gate no verdict, so dropping them costs nothing load-bearing. |
| 2 | 5-currency two-way-FE thin variation | **Keep two-way FE as primary; PROMOTE currency-FE-only to co-primary descriptive** (see Check 2 / W-1). Two-way FE is estimable (115 residual DoF) so it stays; but at G≈5 the two-way-vs-currency-only gap is itself descriptive information on global-vs-idiosyncratic FX-vol exposure and must be reported, not buried in a sensitivity arm. Reporting-status change only — both runs already specified. |
| 3 | Surface-grid resolution | Acceptable — grid-at-E10.3 unchanged from v0.4; my v0.3 §11-item-5 grid-sweep point already landed in §9 ("evaluated on a grid, not at endpoints"). Confirmed. |
| 4 | Ex-ante exposure assumption for break-even | Acceptable — this is the v0.4 closure of my v0.3 C-2/N-2; §13.2 pins payoff geometry to a declared ex-ante prior before E10.2, carries no Stage-1 content. Firewall restored. Confirmed; reviewer-attention flag appropriate. |

---

## New findings

- **W-1 (Weak) — Promote currency-FE-only to co-primary descriptive.** See Check 2 / §11 item 2.
  At G≈5 the two-way-FE vs currency-FE-only gap quantifies global-vs-idiosyncratic FX-vol
  exposure — a result the §13 instrument choice depends on. Burying it as a sensitivity arm
  hides descriptive content. Not Critical: the surface is produced and coherent under either.
- **W-2 (Weak) — Drop the WCB and permutation bands at G≈5; replace with a raw 5-currency
  spread display.** See Check 3 / §11 item 1. At G≈5 both bands carry no valid statistical
  content; a label does not neutralize a plotted interval. Not Critical: bands gate no verdict.
- **Obs-1 (Observation) — N-1 (my v0.3 Critical) is extinguished, not carried.** N-1 was "G≈8
  cannot support the §9 PASS rung." v0.4 retired the PASS rung (CORRECTIONS-E10-4 Fix 1). With
  no inferential rung, a thinner G≈5 has no inferential claim to break. v0.5 correctly does not
  re-open N-1 and correctly states (§0.5/§8/§9) the narrowing strengthens, not weakens, the
  descriptive conclusion. Confirmed sound.

No new Critical or Strong findings. My v0.3 N-2 (break-even ex-ante) and N-3 (permutation
exchangeability) are addressed: N-2 by v0.4's §13.2 ex-ante pinning; N-3 is now moot under W-2
(the permutation arm is dropped). N-4 (bracket width) / N-5 (λ-form) carry forward into E10.1
unchanged — both already have pinning rules deferred to the E10.1 calibration note (acceptable).

---

## Algebra note (verified)

G=5, T≈30 ⇒ N=150 cells. Two-way FE absorbs 1 + (G−1) + (T−1) = 1+4+29 = 34 parameters; 1
slope ⇒ **115 cell-level residual DoF** — two-way within estimator is estimable, not
rank-deficient. Cluster-robust inference effective DoF ≈ G−1 = 4 — far below any usable
threshold, which is *why* no inferential claim is made and is consistent with the descriptive
posture. Permutation support 2^G = 32; min one-sided p ≈ 1/32 ≈ 0.031 — too coarse and, with
EM/DM non-exchangeability, not a valid randomization distribution ⇒ W-2 drop ruling.
Decomposition identity `Var(Δlog cost)=Var(ΔlogFX)+Var(ΔlogQ)+2Cov` exact per cell, verified
in the v0.3 re-review, unchanged.

---

## Summary for dispatch

- **Verdict: PASS.** The G≈5 re-spec is modeling-coherent; no new Critical. CORRECTIONS-E10-5 is
  a genuine panel-dimension re-spec, not a redesign or test tuning. My v0.3 Critical N-1 is
  extinguished by v0.4's retirement of the inferential PASS rung — there is no inferential rung
  for a thinner G to break, and the spec correctly does not re-open it.
- **New Critical count: 0.** Findings: 0 Strong, 2 Weak (W-1, W-2), 1 Observation.
- **§11 item 1 (bands) — explicit call: DROP both bands.** At G≈5 the wild cluster bootstrap
  interval is size-broken and the permutation arm (2^5=32 support, EM/DM non-exchangeability) is
  not a valid randomization distribution. A hardened label does not fix a plotted interval that
  reads as an uncertainty statement. Replace with a raw 5-currency min–max/IQR spread display
  explicitly labelled non-statistical. Bands gate no verdict — dropping them loses nothing.
- **§11 item 2 (two-way FE) — explicit call: keep two-way FE as primary, PROMOTE
  currency-FE-only to co-primary descriptive.** Two-way FE is estimable (115 residual DoF) and
  stays; but at G≈5 the two-way-vs-currency-only gap is itself descriptive content on
  global-vs-idiosyncratic FX-vol exposure and must be reported co-primary, not buried in a
  sensitivity arm. Reporting-status change, not a redesign.
- The descriptive surface IS still worth computing at G≈5: its primary axis (Q-volume) is fully
  intact (the methods-paper §5 contribution); the currency axis is a coarse-but-real 5-regime
  spread (managed-float COP, free-float BRL, post-float NGN, EUR, GBP). Label it a 5-regime
  characterization, not a continuous cross-sectional surface — §9 already does.
- Both W-1 and W-2 are reporting/labelling changes the user should adopt before E10.1; neither
  blocks the PASS.
```
