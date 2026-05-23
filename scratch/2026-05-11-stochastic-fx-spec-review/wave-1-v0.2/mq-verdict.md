# MQ verdict — stochastic-fx-variant-design v0.2 (Wave-1 RE-REVIEW)

**Reviewer:** Math Quality (MQ)
**Date:** 2026-05-12
**Commit under review:** `6b1a466`
**Prior v0.1 verdict:** BLOCK (3 high-severity findings + 2 medium + 1 NIT)
**Verdict on v0.2:** **BLOCK** (1 NEW high-severity finding on hand-derived GBM
moment; prior BLOCK-MQ-1/2/3 disposed satisfactorily otherwise)

---

## Disposition of v0.1 findings

### BLOCK-MQ-1 (Pin Z1.3 split + drop "reduces to eq. (6)" claim) — **DISPOSED**

- §4.2 explicitly retracts the v0.1 "reduces to eq. (6)" claim and replaces it
  with the honest **trivial-degenerate-limit** framing: σ → 0 (and λ → 0 for
  Merton) collapses each family to a point mass at x_0, with σ_T ≡ 0 and ε ≡ 0.
- The text on lines 281-283 of the spec is exactly the framing MQ requested:
  "This is a trivial degeneracy, not a reduction to eq. (6) (which is not the
  limit of any of these families along their parameter axes — eq. (6) requires
  a periodic drift kernel none of these families has)." Confirmed consistent
  with PRIMITIVES.md §5 eq. (6) structure (periodic drift `cos²(ωt) − 1/2`
  parameterized by ε, ω).
- Pin Z1.3a (§5) is family-agnostic, purely algebraic substitution
  `apply_inversion(σ_T_n, x_bar) == √(8·σ_T_n/x_bar²)` at NUMERICAL_IDENTITY_TOL
  = 1e-6 (reuses cohort_4 convention — confirmed at cohort_4/types.py:48).
- Pin Z1.3b (§5) references the §4.2 hand-derived moment tables, NOT
  sympy-derived. §8 anti-fishing posture explicitly retracts the "deterministic
  limit reduces to eq. (6)" claim.

**DISPOSED.** No remaining BLOCK-MQ-1 content.

### BLOCK-MQ-2 (Pin Z1.4 reframing) — **DISPOSED**

- §4.1 Phase C and §5 Pin Z1.4 now describe the MQ-recommended reading (c):
  fit a parametric reference (gamma OR lognormal per §4.2) to the family's
  hand-derived `E[σ_T]` and `Var[σ_T]`, then KS-test empirical σ_T_n samples
  against this reference.
- The §4.2 reference-distribution-per-family table is internally consistent
  with the families' stationary-shape physics:
  - **Lognormal for GBM** ✓ — σ_T under GBM is right-skewed positive, dominated
    by lognormal-squared-deviation behavior; lognormal as a moment-matched
    reference is standard practice (Hull §27).
  - **Gamma for OU** ✓ — stationary OU is Gaussian, hence (X_t − μ̄)² is
    chi-squared-shaped, which is a gamma family with shape parameter 1/2;
    fitting gamma via moment-matching to OU's hand-derived moments is
    well-posed.
  - **Lognormal for Merton** ✓ — moderate λ jump-diffusion is approximately
    lognormal in the diffusion regime; defensible at λ=1/yr.
- v0.1's tautological "pushforward via same σ_T samples" framing is removed.

**DISPOSED.**

### BLOCK-MQ-3 (sympy scope + new moments.py) — **DISPOSED in scope; FAILED in content (see NEW-BLOCK-MQ-4)**

- §3 file-tree adds `moments.py` as a NEW Callable-tier module (lines 116, 152-156).
- §3 prose makes clear sympy is used ONLY for (a) algebraic simplification of
  closed forms and (b) `sympy.latex(...)` rendering — NOT Itô calculus.
  variance_proxy.py prose (lines 147-149) explicitly states "NO Itô calculus
  (sympy cannot perform stochastic calculus)."
- §4.2 hand-derived moment table cites literature anchors (Hull §15 for GBM
  variance estimator; standard OU for OU; Andersen-Piterbarg Vol I §2.7 for
  Merton).

**The scope and architectural disposition is correct.** However, the specific
hand-derived GBM moment formula in §4.2 is wrong — see **NEW-BLOCK-MQ-4** below.

### FLAG-MQ-1 (KS-gate calibration) — **DISPOSED**

§8 documents the 0.01-vs-0.05 rationale in extended form: the threshold is
permissive because the test compares two MC-noise-bearing estimates of the same
population quantity (empirical σ_T_n vs a parametric reference fit to
discretization-implied moments). The explicit "never increase N until passing"
rule is present at §8 (lines 405-412), routed to Pin Z1.5. **DISPOSED.**

### FLAG-MQ-2 (variance-proxy family-dependence framing) — **DISPOSED**

§4.2 makes the family-parameter dependence of E[ε(σ_T)] explicit via the
hand-derived moments. The pointwise algebraic identity (Z1.3a) is split from
the distributional moment match (Z1.3b). **DISPOSED.**

### NIT-MQ-1 (n_steps / T discrete contract) — **DISPOSED**

§4.1 step 3 explicitly cites the B1 plan's σ_T discrete contract per
MQ-FLAG-B1.1 disposition. **DISPOSED.**

---

## NEW-BLOCK-MQ-4 — Hand-derived GBM `E[σ_T]` moment is incorrect (HIGH)

§4.2's GBM moment row states:

> **GBM (mean-zero drift):** E[σ_T] = (X̄/Ȳ)²·(e^{σ²T} − 1)/(σ²T) (leading order in σT)

This is **mathematically incorrect** by an additive `(X̄/Ȳ)²` term. The correct
hand-derivation under Hull's Itô framework:

For mean-zero GBM `dX = σX dW`, X_t = x_0·exp(σW_t − σ²t/2), giving
`Var(X_t) = x_0²·(e^{σ²t} − 1)`. PRIMITIVES eq. (7) σ_T is the time-averaged
quadratic deviation about x̄. Under the spec's stationary anchor x̄ = x_0
= 4000:

```
E[σ_T] = (1/T)·∫₀^T E[(X_s − x_0)²] ds
       = (1/T)·∫₀^T x_0²·(e^{σ²s} − 1) ds
       = x_0² · [ (e^{σ²T} − 1)/(σ²T)  −  1 ]
```

Leading-order in σ²T:
- **Correct:** `E[σ_T] ≈ x_0² · σ²T / 2` (vanishes as σT → 0, as required by
  the trivial-degenerate limit §4.2 itself asserts).
- **Spec (wrong):** `E[σ_T] ≈ x_0² · (1 + σ²T/2)` (approaches x_0² as σT → 0,
  contradicting the spec's own Pin Z1.3a trivial-degenerate-limit claim that
  σ → 0 ⟹ σ_T ≡ 0).

The spec's formula is missing the trailing `− 1`. This is a direct
internal contradiction with §4.2's own trivial-degenerate-limit section:
if E[σ_T] → (X̄/Ȳ)² as σ → 0 instead of 0, the family does NOT reduce to a
point mass at x_0.

### Quantitative impact at canonical pin

GBM pin: σ = 0.10/√12 ≈ 0.02887, T = 12, x_0 = 4000.
- σ²T = 0.01.
- Correct E[σ_T] ≈ 16,000,000 · 0.005 = **80,000**.
- Spec E[σ_T] ≈ 16,000,000 · (1 + 0.005) = **16,080,000**.

The two differ by a factor of ~200. At MOMENT_REL_TOL = 0.05 (Pin Z1.3b), the
Pin Z1.3b moment-match gate will catastrophically FAIL for GBM at the pinned
parameters — and per Pin Z1.5 anti-fishing routing, this would trigger
CORRECTIONS-α + Wave-1 re-review BEFORE implementation can proceed, because
"hand-derived analytic moments in §4.2 are wrong" is exactly the HALT branch
documented at §6 (line 321a).

### Action required

Re-derive the GBM `E[σ_T]` row in §4.2 to either:
- **Exact form:** `E[σ_T] = (X̄/Ȳ)² · [(e^{σ²T} − 1)/(σ²T) − 1]`, OR
- **Leading-order form:** `E[σ_T] ≈ (X̄/Ȳ)² · σ²·T / 2 + O((σ²T)²)`.

Both are sympy-renderable as `.tex` fragments. The Hull §15 anchor still
applies — the citation is fine; the algebra is wrong. The same correction
likely propagates to `Var[σ_T]` (not displayed in the spec table but referenced
in the `.tex` fragments).

### Severity rationale

**High.** The math error is large (~200× at pinned σT), internally contradicts
§4.2's own trivial-degenerate-limit claim, and will make Pin Z1.3b
mechanically unprovable at the pinned parameters. This must be fixed BEFORE
plan authorship — otherwise plan execution would (correctly per Pin Z1.5)
HALT at first GBM moment-match test, demanding CORRECTIONS-α anyway, but at
implementation cost rather than spec-fix cost.

---

## Other math soundness checks

### OU `E[σ_T] = σ²/(2θ)` — **CORRECT**

Standard OU stationary variance. Under spec's pin σ = 0.10·4000/√(2·1.0)
≈ 282.84, θ = 1.0: E[σ_T] = 282.84²/2 ≈ 40,000. Gamma reference is well-posed
(chi-squared-shape). **OK.**

### Merton `E[σ_T] = (X̄/Ȳ)²·σ²·T + λ·(X̄/Ȳ)²·(e^{2(μ_J+σ_J²)} − 2e^{μ_J+σ_J²/2} + 1)·T` — **CORRECT in form**

Diffusion contribution `σ²·T·x_0²` matches the GBM-leading-order term (this
is the form the GBM row SHOULD have used). Jump contribution
`λ·E[(e^J − 1)²]·T·x_0²` with J ~ N(μ_J, σ_J²) expands via the lognormal
MGF to exactly the bracketed expression. Andersen-Piterbarg Vol I §2.7
anchor confirmed. **OK.**

Aside: this exposes the GBM error more starkly — the Merton row's diffusion
term `(X̄/Ȳ)²·σ²·T` is the correct leading-order GBM realized-variance form,
and it should appear in the GBM row too (instead of the offending closed
form).

### Per-family parameter pin table

- Canonical fixture (x̄ = 4000, ε = 0.10, T = 12) ✓ consistent with the
  cohort_5_strip canonical fixture.
- σ pinned in absolute terms per family ✓ — anti-fishing.
- Note: OU's σ pin is parameterized as `0.10·4000/√(2·1.0)`, which couples
  to the ε=0.10 fixture by design (so that ε(E[σ_T]) ≈ 0.10·√2 ≈ 0.14).
  This is documented in §4.2 line 257 and is defensibly intentional under
  Pin Z1.1 pre-pinning; flagged here as **INFO**, not material.

### Anti-fishing posture (§8) — **VERIFIED**

- Explicit retraction of "deterministic limit reduces to eq. (6)" claim
  (§8 lines 419-425). ✓
- N=1000 floor as anti-fishing invariant, NOT a parameter to grow
  (§8 lines 405-412). ✓
- KS-gate calibration rationale at 0.01 vs 0.05 documented. ✓
- Strip preservation Pin Z1.6 invariant unchanged. ✓ (cohort_5_strip
  not imported, not modified, audit_block hex grep specified for
  pre/post verification).
- REPLICATION_REL_TOL (0.35 floor) NOT imported or overridden by this
  spec. ✓ Confirmed at cohort_5_strip/types.py:74.

### Three-tier discipline

`moments.py` is correctly placed at the Callable tier (§2 line 91-93,
§3 line 152) with hand-derived analytic moment expressions emitted as
LaTeX fragments. No inheritance, no mutable state — consistent with the
functional-python skill. ✓

---

## Final verdict

**BLOCK** on v0.2.

The architectural and framing dispositions of BLOCK-MQ-1, BLOCK-MQ-2, and
BLOCK-MQ-3 are CORRECT and complete. The new `moments.py` module, the
trivial-degenerate-limit framing, the Pin Z1.3a/Z1.3b split, and the
moment-matched parametric KS reference are all sound. The KS calibration
rationale and N-floor anti-fishing rule are properly documented.

However, the §4.2 GBM hand-derived `E[σ_T]` formula is wrong by an additive
`(X̄/Ȳ)²` term — internally contradicting the spec's own trivial-degenerate
limit and rendering Pin Z1.3b mechanically unprovable at the pinned GBM
parameters. This is exactly the error class BLOCK-MQ-3's hand-derived-not-
sympy-derived requirement was meant to surface for review, and it has
surfaced as expected.

### Required action (CORRECTIONS-α v0.2 → v0.3)

1. Fix §4.2 GBM `E[σ_T]` row to `(X̄/Ȳ)² · [(e^{σ²T}−1)/(σ²T) − 1]` (exact)
   or leading-order `(X̄/Ȳ)² · σ²·T / 2`.
2. Confirm the `Var[σ_T]` GBM hand-derivation (referenced but not displayed
   in §4.2) is similarly corrected and emitted as the `.tex` fragment.
3. No other corrections required; OU and Merton rows are correct; all v0.1
   BLOCK dispositions are sound.

With this single correction, v0.3 should clear MQ. OU and Merton math is
publication-ready; the architectural reframing of Pins Z1.3a/Z1.3b/Z1.4 is
materially better than v0.1.

---

**MQ Verdict on v0.2:** BLOCK pending CORRECTIONS-α v0.3 addressing
NEW-BLOCK-MQ-4 (GBM hand-derived E[σ_T] correction). All prior BLOCK-MQ-1/2/3
findings DISPOSED. Re-review on v0.3 will be narrow-scope (single moment row).
