# MQ verdict — stochastic-fx-variant-design v0.1
**Reviewer:** Math Quality (MQ)
**Date:** 2026-05-11
**Verdict:** BLOCK

The spec has structural-architecture merit (three-tier mirror of cohort_5_strip,
Pin Z1.6 strip preservation, anti-fishing posture), but its core mathematical
claim — distributional verification of PRIMITIVES eq. (8) under three SDE
families with reduction to the deterministic limit — contains at least three
math errors of kind that make Pin Z1.3 unprovable as written and Pin Z1.4
either tautological or under-specified. These must be resolved BEFORE plan
authorship.

---

## Findings

### BLOCK-MQ-1 — "Deterministic limit" of any SDE family does NOT recover eq. (6)

Pin Z1.3 (§5) claims each family's analytic ε(σ_T) form "reduces to PRIMITIVES
eq. (8) under the deterministic limit (σ → 0 for GBM; θ → ∞ for OU; λ_jump → 0
for jump-diffusion)." This is mathematically ill-posed:

- **GBM σ → 0** gives $dX_t = \mu X_t dt$ ⟹ $X_t = X_0 e^{\mu t}$ (exponential
  drift, NOT periodic). With $\mu = 0$ added you get $X_t \equiv X_0$, a
  constant, hence $\sigma_T \equiv 0$ and $\varepsilon \equiv 0$ — the
  TRIVIAL degenerate case. Eq. (6) is $(X/Y)_t = (1 + \varepsilon f_t)
  \overline{X/Y}$ with $f_t = \cos^2(\omega t) - 1/2$, a periodic
  deterministic path indexed by $(\varepsilon, \omega)$. There is no $\omega$
  in GBM, so no parameter limit can produce eq. (6).

- **OU θ → ∞** gives $X_t \to \bar\mu$ pointwise (instantaneous mean
  reversion). Again trivial degeneracy: $\sigma_T \to 0$, $\varepsilon \to 0$.
  Not eq. (6).

- **Merton λ_jump → 0** reduces to GBM, not to eq. (6) — the spec author
  flags this themselves in the prompt as a concern. Correct flag: a
  single-parameter limit of Merton cannot reach eq. (6) because Merton has
  no periodic drift kernel.

The CORRECT framing is: eq. (8) is a **pointwise algebraic identity**
$\varepsilon = g(\sigma_T) \equiv \sqrt{8\sigma_T/\overline{(X/Y)}^2}$. It does
not depend on the path-generation mechanism. Under eq. (6) plus the
canonical-$\omega$ time-average $\frac{1}{T}\sum f_t^2 \to 1/8$, you recover
the *specific value* $\sigma_0 = \varepsilon^2 \overline{(X/Y)}^2 / 8$ (cohort_4
R1 anchor, verified in STAGE_2_RESULTS.md §2.1). Under any SDE family $\sigma_T$
is a path-dependent r.v. and (8) becomes a pushforward of its law.

**What the spec should claim instead:** for each SDE family with appropriately
chosen drift such that $E_\infty[(X/Y)_t] = \overline{X/Y}$, the random
variable $g(\sigma_T)$ has a well-defined distribution; under the
zero-volatility-and-zero-jump degenerate sub-family limit the distribution
collapses to a point mass at $\varepsilon = 0$. That's a triviality, not a
verification of (8).

**Action required.** Re-specify Pin Z1.3. Either (i) drop the "reduces to
eq. (6)" claim and replace with "reduces to the cohort_4 R1 σ_0 value when
the SDE is overlaid on a periodic drift kernel matching eq. (6)" — which
requires augmenting each SDE with a periodic drift term, OR (ii) reframe
the verification as a check that the pointwise inversion (8) commutes with
the SDE expectation: $E[\varepsilon(\sigma_T)]$ as a function of family
parameters, with the trivial-degenerate limit yielding $\varepsilon \to 0$.

Severity: **High**. This Pin as written cannot be discharged at residual ≤
1e-6 because the target form (eq. 8 at deterministic eq. (6) path) is not the
limit of any of the three SDE families along the parameter axis chosen.

---

### BLOCK-MQ-2 — KS-test phase is operationally undefined; risks tautology

§4 step 3 MC phase: "compute empirical $\hat\varepsilon_n = \sqrt{8\sigma_{T,n}/\bar x^2}$
for each of the N paths. KS-test the empirical distribution against the
analytic ε distribution sampled at the same N."

The "analytic ε distribution" is never defined. Two readings:

- **(a) Pushforward.** Analytic distribution of $\varepsilon$ = pushforward
  of the analytic distribution of $\sigma_T$ under $g$. But this analytic
  distribution of $\sigma_T$ is exactly what the spec needs to derive (and
  what the symbolic phase claims to derive). Under GBM, $\sigma_T =
  \frac{1}{T}\sum (X_t - \bar X)^2$ where $X_t$ is lognormal and the sum is
  over correlated lognormals — there is no known closed-form distribution.
  Under OU, only the stationary case has a clean form
  (chi-squared-like times $\sigma^2/(2\theta)$); transient is harder. Under
  Merton, the compound-Poisson contribution prevents a closed form. Sympy
  cannot derive these — they require Itô calculus and Wiener-chaos
  expansion, neither of which sympy.simplify executes.

- **(b) Tautological.** "Analytic ε" computed by applying $g$ to the
  SAME $\sigma_{T,n}$ samples ⟹ KS p-value = 1 always (identical empirical
  distributions). No information content.

If reading (a) is intended, the symbolic phase (Pin Z1.3) must produce the
analytic distribution of $\sigma_T$ (not just the algebraic inversion form)
per family — which is infeasible in closed form for GBM/Merton. If reading
(b) is intended, the gate is meaningless.

A **third defensible reading (c)**, which the spec should adopt: use the
SDE's analytic moment expressions for $\sigma_T$ ($E[\sigma_T]$ and
$\text{Var}[\sigma_T]$ — both closed-form for GBM and stationary OU) to
construct a parametric reference distribution (e.g., gamma fit to those
two moments), then KS-test the empirical $\sigma_T$ samples against that.
Eq. (8)'s inversion is then verified pointwise (trivially) and the
non-trivial content is the SDE's $\sigma_T$ moment match.

**Action required.** Disambiguate §4 step 3. State whether the analytic ε
comes from (a) closed-form distribution of $\sigma_T$, (b) re-application of
$g$ to the same MC samples (tautological, drop), or (c) moment-matched
parametric reference. MQ recommends (c).

Severity: **High**. As written this is either a tautology (no diagnostic
power) or asks for analytic distributions that don't exist in closed form.

---

### BLOCK-MQ-3 — Sympy cannot derive the analytic ε distribution per family

§3 declares `sympy_inversion_check_gbm`, `..._ou`, `..._jump` as Callable-tier
functions returning `(analytic_eps_expr, deterministic_limit_residual)`. The
analytic ε expression is well-defined only as $g(\sigma_T)$ — pure algebraic
substitution, which sympy handles trivially in O(1ms). The hard work — the
distribution of $\sigma_T$ under the family — is **not symbolic algebra**.
It requires:

- For GBM: Itô-calculus computation of $E[(X_t - \bar X)^2]$ over correlated
  lognormals. Sympy does not implement Itô calculus. Manual derivation exists
  in literature (Hull, Andersen-Piterbarg) but is hand-derivation, not
  symbolic-simplify.
- For OU: closed form for stationary $\text{Var}[X_t] = \sigma^2/(2\theta)$ is
  textbook (sympy can simplify the ODE solution). Transient variance
  $\text{Var}[X_t | X_0] = (\sigma^2/(2\theta))(1 - e^{-2\theta t})$ also sympy-
  tractable. But the realized-variance estimator $\frac{1}{T}\sum(X_t - \bar X)^2$
  involves $\bar X$ as a random sample mean — joint expectations across time
  indices are not single-line sympy simplifies.
- For Merton: jump component adds Poisson-compound terms; closed forms exist
  for moments but not via `sympy.simplify`.

The spec should split the symbolic work into (i) the trivial algebraic
inversion check (sympy-tractable, residual genuinely ≤ 1e-6) and (ii) the
moment derivation (hand-derived per family, sympy used only for
simplification of the final closed forms). Pin Z1.3 conflates these.

**Action required.** Either (a) restrict the symbolic phase to the inversion
algebra (which is *family-independent* and only verifies that $g$ commutes
with substitution — a near-trivial check), and move moment derivations to
hand-derived `.tex` fragments emitted via `sympy.latex(...)`; or (b) extend
the symbolic phase to perform moment derivations using a Wiener-chaos or
moment-generating-function package that sympy alone does not provide.

Severity: **High** for plan-execution-readiness; **Medium** for spec validity
(the spec can stand if it commits to (a)).

---

### FLAG-MQ-1 — KS gate p ≥ 0.01 with N ≥ 1000 is permissive in unusual ways

Pin Z1.4. The 0.01 threshold (vs. conventional 0.05) is *more lenient* — it
accepts more often. Combined with N ≥ 1000 (which gives high power to detect
small differences), the gate's calibration is:

- Type-I error rate: 1% (rejects 1% of truly-matching cases).
- Type-II error rate: shrinks rapidly with N; at N=1000 the KS test detects
  Kolmogorov distance differences of order $1/\sqrt{1000} \approx 0.032$.

This is a **stringent** test for small distributional differences but a
**lenient** PASS gate — defensible IF the comparison is between two
computations of the same population quantity allowing for MC noise (your
case if reading (c) above is adopted). For comparison against an externally
derived analytic distribution, the conventional 0.05 is more honest.

Recommend: state explicitly that 0.01 is chosen because the test compares
two MC-noise-bearing estimates of the same population quantity, hence
tolerating slightly larger discrepancies. Document this in §8 anti-fishing
posture alongside an explicit prohibition on increasing N until passing.

Severity: **Medium**. Doesn't block but needs justification block.

---

### FLAG-MQ-2 — Variance proxy under GBM is NOT family-parameter-independent

Under GBM with drift $\mu$ and vol $\sigma$, after long-$T$ stationarization
of $X/Y$ around $\overline{X/Y}$ (which itself requires a drift adjustment —
plain GBM is not stationary), $E[\sigma_T] \to \sigma^2 \overline{(X/Y)}^2$
(approximately, to leading order). Hence

$E[\varepsilon(\sigma_T)] = E[\sqrt{8\sigma_T}/\overline{X/Y}]
\approx \sqrt{8} \cdot \sigma$ (modulo Jensen's-inequality corrections).

The "ε ↔ σ_T inversion" therefore reads, under GBM, as
$\varepsilon \leftrightarrow \sqrt{8}\sigma_{GBM}$ in expectation. The
mapping is family-parameter dependent. The user's prompt flags this; MQ
confirms: the spec should state, per family, the explicit map from
SDE parameters to the *expected* $\varepsilon$ and verify that the MC
empirical $\hat\varepsilon_n$ has mean within tolerance of this analytic
expected $\varepsilon$ — that's the testable content.

Severity: **Medium**. Affects the framing of the verifier, not its
correctness.

---

### NIT-MQ-1 — `n_steps` vs `T` definition consistency

`types.py` PathEnsemble has `n_steps+1` columns and uses `dt`. PRIMITIVES eq.
(7) sums $t = 0, ..., T$ — $T+1$ terms. Verify that the spec's $T$ in eq. (7)
aligns with the `n_steps` field, not `n_steps × dt`. The B1 disposition
already pinned discrete summation; cross-reference it explicitly.

Severity: Low.

---

## Math anchor verification (eq. 6, 7, 8 consistency per SDE family)

- **Eq. (6)** is a deterministic periodic generator with parameters
  $(\varepsilon, \omega)$. No SDE family in §4 has a periodic drift kernel,
  so no SDE family contains (6) as a sub-case along any parameter axis.
- **Eq. (7)** is the discrete realized-variance estimator. It is
  family-agnostic — takes any path and produces $\sigma_T \geq 0$. PASSES
  trivially under all three families.
- **Eq. (8)** is the algebraic inversion $\varepsilon = g(\sigma_T)$.
  Family-agnostic. Trivially verifiable per path; non-trivial content lies
  in the **distribution** of $g(\sigma_T)$ under the family — see
  BLOCK-MQ-2.

The spec conflates two reductions: (a) "$\varepsilon \to 0$ under
zero-volatility limit" (trivial degeneracy, holds for all three families)
and (b) "recovers eq. (6) deterministic identity" (impossible without
periodic drift overlay). Pin Z1.3 must split these.

---

## Sympy feasibility audit per family

| Family | Algebraic inversion (eq. 8 substitution) | $E[\sigma_T]$ closed form | Full $\sigma_T$ distribution closed form |
|---|---|---|---|
| GBM | sympy-trivial | hand-derivable, sympy-simplifiable | NO (Wiener chaos) |
| OU (stationary) | sympy-trivial | sympy-tractable: $\sigma^2/(2\theta)$ | partial (chi-squared-like under Gaussian stationary) |
| OU (transient) | sympy-trivial | sympy-tractable | NO closed form |
| Merton | sympy-trivial | hand-derivable | NO (compound Poisson + Wiener chaos) |

Sympy delivers item 1 (algebraic inversion) per family, but that's the
family-agnostic trivial substitution. Items 2 and 3 require hand derivation
followed by sympy simplification of the final form. Pin Z1.3 should be split
into Z1.3a (algebraic inversion ≤ 1e-6 — trivial) and Z1.3b (moment match ≤
1e-6 — hand-derived per family).

---

## KS-test methodology audit

- Comparing $\hat\varepsilon_n$ to a self-defined pushforward via the same
  $\sigma_T$ samples is tautological. The spec must specify the external
  reference distribution.
- MQ recommends moment-matched gamma (or lognormal) reference using the
  family's analytic $E[\sigma_T]$ and $\text{Var}[\sigma_T]$. Then KS-test
  $\sigma_T$ samples against that reference — and verify pointwise that
  $g(\sigma_{T,n})$ matches $\hat\varepsilon_n$ algebraically (which is
  trivial by construction).
- KS p ≥ 0.01 at N=1000 is defensible under MC-noise-matched reference;
  weakly defensible against externally-derived analytic. State the
  rationale in §8.
- $N \geq 1000$ adequate for moderate-effect detection
  ($D \sim 0.03$); for very tight distributional agreement claims raise
  to $N = 10^4$.

---

## Inversion identity vs distribution audit (the critical question)

**MQ's read:** PRIMITIVES (8) is a pointwise algebraic identity. The spec's
distributional extension does NOT add information beyond the pointwise
identity IF the analytic ε distribution is defined as the pushforward of
the analytic $\sigma_T$ distribution under $g$ — because $g$ is a
deterministic bijection on $\mathbb{R}_{\geq 0}$, and the pushforward and the
empirical-applied-$g$ are equal in law by construction. KS would always pass.

**The non-trivial testable content is one of:**

1. Does the **family's analytic $\sigma_T$ distribution** match the empirical?
   (Verifies the SDE's variance dynamics, not eq. (8).)
2. Does $g$ applied to MC $\sigma_T$ recover the family's analytic
   expected $\varepsilon$ within tolerance? (Verifies eq. (8)'s consistency
   under the family's stationary measure.)

The spec must commit to one. As written, the KS test as described risks
being tautological — see BLOCK-MQ-2.

---

## Pin coverage audit

- **Z1.1** (parameter pre-pinning): adequate. Recommend §4 include a
  concrete numerical pin table per family (mu, sigma, theta, lambda, etc.)
  rather than deferring to "per-family parameter docstrings."
- **Z1.2** (RNG determinism): solid. Hypothesis property test on
  `(rng_seed, n_paths) → (ensemble, audit_block)` is well-formed.
- **Z1.3** (sympy reduction): **BLOCKED — see BLOCK-MQ-1 + BLOCK-MQ-3**.
  Split into Z1.3a (algebraic, trivial) and Z1.3b (moment match,
  hand-derived).
- **Z1.4** (KS gate): **BLOCKED — see BLOCK-MQ-2**. Disambiguate reference
  distribution.
- **Z1.5** (anti-fishing routing): solid.
- **Z1.6** (strip preservation): VERIFIED. Audit hash
  `94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329` matches
  `simulations/saas_builder/data/IronCondor_strip.json` and is cross-cited
  in `strategy_verdict.json`. The hash is stable across `StripEmitter`
  re-runs at fixed cohort_4 audit input (per `_compute_strip_audit_block`
  in `cohort_5_strip/emit.py:113`).

---

## Required actions before plan authorship (CORRECTIONS-α v0.1 → v0.2)

1. Split Pin Z1.3 into Z1.3a (algebraic inversion, family-agnostic, trivial)
   and Z1.3b (per-family moment match against hand-derived $E[\sigma_T]$).
   Drop the "reduces to eq. (6)" claim; replace with "reduces to the trivial
   $\varepsilon \to 0$ point mass under zero-volatility-and-zero-jump."
2. Disambiguate Pin Z1.4: state explicitly what the "analytic ε distribution"
   is. MQ recommends moment-matched parametric reference (gamma /
   lognormal) on $\sigma_T$, with the eq. (8) inversion verified pointwise
   (trivially).
3. Add per-family numerical parameter pin table to §4.
4. Add §4.x "Variance dynamics per family" with the hand-derived
   $E[\sigma_T]$ and $\text{Var}[\sigma_T]$ expressions — these will live as
   `.tex` fragments and are the non-trivial mathematical content.
5. Revise §8 to document the KS gate calibration rationale (0.01 vs 0.05).

With these corrections the spec becomes mathematically sound. Without them
the implementation will either be tautological (KS always passes) or
unprovable (Pin Z1.3 residual cannot be computed because the target form is
ill-posed).

---

**MQ Verdict:** BLOCK pending CORRECTIONS-α v0.2 addressing BLOCK-MQ-1,
BLOCK-MQ-2, BLOCK-MQ-3. Strip preservation (Z1.6) and three-tier
architecture verified sound. Re-review on v0.2.
