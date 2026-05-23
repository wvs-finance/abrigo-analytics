# MQ verdict — stochastic-fx-variant plan v0.1
**Reviewer:** Math Quality (MQ)
**Plan under review:** docs/plans/2026-05-11-stochastic-fx-variant.md (v0.1, commit `cfb7677`)
**Parent spec:** docs/specs/2026-05-11-stochastic-fx-variant-design.md v0.3 (Wave-1 cleared at `56cc928`)
**Review wave:** Wave-1 plan-time
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

The plan faithfully implements the spec v0.3 math. The NEW-BLOCK-MQ-4 GBM `−1` correction
is preserved verbatim, the KS gate uses `ks_1samp` against a moment-matched parametric
reference (not the v0.1 tautology MQ caught at spec wave), the N=1000 floor is enforced at
construction time, and Phase A/B/C task ordering is correct. Three FLAGs below are
implementability gaps (not math errors); none rises to BLOCK.

---

## Findings (BLOCK / FLAG / NIT)

### FLAG-MQ-1 (Medium) — Merton Phase B Python expression not literal in acceptance
Task 2.1 (plan line 199) spells GBM and OU `E[σ_T]` as exact Python literals in the
acceptance criteria (good — code-author cannot mis-translate). The Merton row instead
says only *"exact form per spec §4.2 Merton row."* The Merton moment is the most error-prone
of the three (jump-compound term `λ·(X̄/Ȳ)²·(e^{2(μ_J+σ_J²)} − 2 e^{μ_J+σ_J²/2} + 1)·T`
has two distinct exponential signs and is easy to off-by-one). Recommend v0.2 expands
acceptance to include the literal Python form, e.g.:

> `E[σ_T] = params.x_0**2 * params.sigma**2 * params.T + params.lambda_jump * params.x_0**2 * (exp(2*(params.jump_mean + params.jump_std**2)) - 2*exp(params.jump_mean + params.jump_std**2 / 2) + 1) * params.T`

with Reality-Checker numerical cross-check at the canonical pin (μ_J=0, σ_J=0.10, λ=1, T=12)
that yields a hand-computed pinned value within 1e-12.

### FLAG-MQ-2 (Medium) — `(X̄/Ȳ)²` → `params.x_0**2` substitution rationale not stated
Spec §4.2 GBM and Merton rows use `(X̄/Ȳ)²` (rolling-mean ratio per PRIMITIVES.md §6). The
plan Task 2.1 substitutes `params.x_0**2`. This is correct at the canonical pin where
`Ȳ ≡ 1` and `X̄ ≡ x_0` by construction, but the substitution should be documented in
`moments.py` docstring (and the `.tex` fragment should retain `(X̄/Ȳ)²` symbolic form for
the future LaTeX-econ-paper consolidator). Otherwise a downstream reader will not see why
`x_0**2` is dimensionally consistent with the spec's symbolic form.

### FLAG-MQ-3 (Low) — Var[σ_T] hand-derived forms not pinned in plan acceptance
Task 2.1 acceptance gives Var[σ_T] forms for OU only (`2σ⁴/((2θ)²·T)` leading order). GBM
and Merton Var[σ_T] are referenced as *"Var[σ_T] form per Hull §15 (hand-derived leading
order; rendered exactly in the `.tex` fragment)"* and "per spec §4.2 Merton row" without
literal Python. Since Phase B (Z1.3b) tests BOTH `mean_relative_error` and
`var_relative_error` against `MOMENT_REL_TOL = 0.05`, an unstated Var[σ_T] formula is a
silent-fishing surface (an implementer could pick a formula that happens to pass at the
canonical pin). Recommend v0.2 pins the literal Var[σ_T] Python expression per family in
Task 2.1 acceptance.

### NIT-MQ-1 (Low) — Phase C lognormal-fit formula in plan should drop `lognorm.fit`
Task 4.2 acceptance (plan line 319) says *"`lognorm.fit` with parameters derived from
log-mean and log-std"*. But the method-of-moments formulas
`log-mean = log(E²/√(Var+E²))`, `log-std = √(log(1 + Var/E²))` are exact closed-form — no
`scipy.stats.lognorm.fit` call needed (and `.fit` would re-fit against EMPIRICAL data,
which would tautologise Phase C). Recommend wording: *"construct
`scipy.stats.lognorm(s=log_std, scale=exp(log_mean))` directly from the analytic moments;
do NOT call `.fit()` against empirical sigma_t_per_path."* Same concern does NOT apply to
gamma — plan correctly specifies `gamma.fit(... floc=0, fscale=Var/E)` consistent with the
spec, though again a direct construction `scipy.stats.gamma(a=E**2/Var, scale=Var/E)`
would be cleaner and tautology-proof.

---

## Math content verification per task

| Spec formula | Plan task expression | Verdict |
|---|---|---|
| GBM `E[σ_T] = (X̄/Ȳ)²·[(e^{σ²T}−1)/(σ²T) − 1]` (spec §4.2 line 268, NEW-BLOCK-MQ-4 corrected) | Task 2.1 line 197: `params.x_0**2 * ((exp(params.sigma**2 * params.T) - 1) / (params.sigma**2 * params.T) - 1)` | ✓ PASS — operator precedence parses to `[(e^{σ²T}−1)/(σ²T)] − 1`; the trailing `− 1` survives the v0.2→v0.3 NEW-BLOCK-MQ-4 fix. σ→0 limit vanishes as required. |
| OU `E[σ_T] = σ²/(2θ)` (spec §4.2 line 269) | Task 2.1 line 198: `params.sigma**2 / (2 * params.theta)` | ✓ PASS — exact match. |
| Merton `E[σ_T] = (X̄/Ȳ)²·σ²·T + λ·(X̄/Ȳ)²·(e^{2(μ_J+σ_J²)} − 2e^{μ_J+σ_J²/2} + 1)·T` (spec §4.2 line 270) | Task 2.1 line 199: *"exact form per spec §4.2 Merton row"* (no Python literal in acceptance) | ✓ math reference correct; FLAG-MQ-1 — should be literalised in plan acceptance to prevent code-author translation error. |
| GBM canonical pins (spec §4.2 line 259/260: σ = 0.10/√12, T=12, x_0=4000, n_steps=5000) | Task 1.2 line 151: `CANONICAL_GBM = GBMParameters(mu=0.0, sigma=0.10/sqrt(12), x_0=4000.0, T=12.0, dt=12.0/5000, n_steps=5000)` | ✓ PASS |
| OU canonical pins (σ = 0.10·x_0/√(2θ), θ=1) | Task 1.2 line 152: `sigma=0.10 * 4000.0 / sqrt(2.0 * 1.0)` | ✓ PASS — algebraic match to spec's "calibrated so σ²/(2θ) ≈ matches GBM moment scale". |
| Merton canonical pins (σ=0.05/√12, λ=1, μ_J=0, σ_J=0.10) | Task 1.2 line 153 | ✓ PASS |

---

## Pin Z1.3a / Z1.3b / Z1.4 implementability audit

**Z1.3a (algebraic inversion, Task 4.1).** `apply_inversion(sigma_t, x_bar) = sqrt(8 * sigma_t / x_bar**2)` matches PRIMITIVES.md §6 eq. (8). Trivially algebraic; the property test `apply_inversion(0, x_bar) == 0` correctly pins the σ→0 trivial-degenerate limit. Unit-test pin `apply_inversion(20000, 4000) == 0.1` is arithmetic-correct: `sqrt(8·20000 / 4000²) = sqrt(160000/16000000) = sqrt(0.01) = 0.1`. ✓ PASS.

**Z1.3b (moment match, Task 4.2).** Plan line 318: empirical `mean(ensemble.sigma_t_per_path)` and `var(ensemble.sigma_t_per_path)` are extracted from the ensemble (not recomputed — `compute_sigma_t_per_path` in Task 4.1 provides the round-trip check at `NUMERICAL_IDENTITY_TOL = 1e-6`). Analytic moments come from `moments.py` (Task 2.1). Relative-error each moment against `MOMENT_REL_TOL = 0.05`. PASS iff BOTH ≤ tol. Raises `MomentMatchFailedError` on failure (HALT routing). ✓ PASS — Pin Z1.3b correctly implemented.

**Z1.4 (KS gate, Task 4.2).** Plan line 319 specifies `scipy.stats.ks_1samp` against the FITTED PARAMETRIC reference (moment-matched lognormal/gamma derived from the analytic E and Var). This is the spec v0.2 BLOCK-MQ-2 corrected framing — NOT `ks_2samp` against pushforward samples (the spec v0.1 tautology MQ caught). ✓ PASS — Pin Z1.4 correctly implemented. KS_PVALUE_FLOOR = 0.01 matches spec §5 Pin Z1.4.

**N=1000 floor enforcement.** Plan line 320: *"the verifier rejects calls where `ensemble.paths.shape[0] != 1000` … Does NOT accept 'increased N' — explicit constant."* Enforced at InversionVerifier construction time. ✓ PASS — Pin Z1.5 anti-fishing-clean.

---

## SDE discretization scheme audit

**GBM Euler-Maruyama log-scale (Task 3.1 line 226).** `X_{t+dt} = X_t * exp((mu - sigma^2/2) * dt + sigma * sqrt(dt) * Z_t)`. The `-sigma²/2` Itô correction is present. ✓ PASS — exact lognormal increment.

**OU exact transition (Task 3.2 line 250).** `X_{t+dt} = mu_bar + (X_t - mu_bar) * exp(-theta * dt) + sigma * sqrt((1 - exp(-2*theta*dt))/(2*theta)) * Z_t`. Variance term `σ²(1−e^{−2θdt})/(2θ)` is the exact OU transition variance (Vasicek closed form). ✓ PASS — no discretization error.

**Merton (Task 3.3 line 272).** GBM Euler-Maruyama step + compound-Poisson jump aggregation: (i) `N ~ Poisson(λ·dt)`, (ii) `N` jump sizes from `lognormal(jump_mean, jump_std)`, (iii) multiplicative aggregation `X_{t+dt} = X_{t+dt}^{diffusion} * prod(jump_sizes)`. Jump distribution is lognormal multiplicative (matches Andersen-Piterbarg §2.7). ✓ PASS. Minor consideration: at `λ·dt = 12/5000 = 0.0024`, `Poisson(0.0024)` is essentially Bernoulli — fine for MC, but Hypothesis test should verify the `lambda_jump = 0` reduction-to-GBM (line 276) holds bit-exactly, not just statistically (the plan correctly specifies a KS statistical agreement test).

---

## Task ordering soundness

| Dependency | Verdict |
|---|---|
| Task 2.1 (moments) before Task 4.2 (InversionVerifier consumes moments) | ✓ Phase 2 < Phase 4 |
| Task 3.x (generators) before Task 6 (end-to-end run) | ✓ Phase 3 < Phase 6 |
| Task 4.1 (verify_phase_a) before Task 4.2 (InversionVerifier wraps Phase A) | ✓ |
| Task 7 (Pin Z1.6 strip preservation grep) timing | ✓ Plan line 397 specifies grep is run BOTH before Task 1.1 AND after Task 6 — catches any mid-execution mutation of the cohort_5_strip audit_block. Audit_block `94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329` verified live in `simulations/saas_builder/data/IronCondor_strip.json`. |

---

## Anti-fishing posture audit

- ✓ N=1000 floor pinned at InversionVerifier construction (Task 4.2 line 320); not a tunable.
- ✓ MOMENT_REL_TOL = 0.05 and KS_PVALUE_FLOOR = 0.01 are module-level constants, NOT call-site parameters.
- ✓ Plan §14 HALT routing (lines 421–428) is explicit: *"NEVER raise sigma to pass"*, *"NEVER increase N"*, *"NEVER retune SDE parameters silently"*. Routes failures to CORRECTIONS-α + scoped Wave-1 re-review (Pin Z1.5 per spec).
- ✓ Task 1.2 canonical pins frozen at plan commit; post-hoc adjustment requires Pin Z1.1 routing.
- ✓ Strip preservation invariant (Pin Z1.6, Task 7) catches accidental mutation.
- ✓ No silent tolerance-relaxation suggestion in the HALT-routing table.

One minor anti-fishing concern (FLAG-MQ-3): Var[σ_T] forms for GBM and Merton not literalised in Task 2.1 acceptance — an implementer could pick a Var formula that happens to pass MOMENT_REL_TOL at the canonical pin without literature anchor. Recommend v0.2 closes this surface.

---

## Summary

Plan v0.1 is mathematically faithful to spec v0.3. The three high-risk arithmetic surfaces
(GBM `−1` correction, KS 1-sample vs. 2-sample, N=1000 floor) are all correctly handled. The
FLAGs concern *plan acceptance literalness*, not math errors — closing them in v0.2 would
remove translation risk at task-execution time. ACCEPT_WITH_FLAGS.

**Disposition routing:** FLAG-MQ-1, FLAG-MQ-2, FLAG-MQ-3, NIT-MQ-1 to be addressed in
plan v0.2 §16.1 CORRECTIONS-α before Task 1.1 dispatch.
