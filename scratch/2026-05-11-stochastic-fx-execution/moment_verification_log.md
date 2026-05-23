# Moment Verification Log — Stochastic-FX End-to-End Run 2026-05-13

**Spec version:** v0.5
**Plan version:** v0.6
**Driver:** `scratch/2026-05-11-stochastic-fx-execution/driver.py`
**N_REF used for Merton Phase C reference:** 5000 (hardware-constrained per FLAG-RC-V0.5-1; spec-pinned constant unchanged)
**rng_seed:** 42
**n_paths:** 1000
**MOMENT_REL_TOL:** 0.05

## GBM at canonical pin (CANONICAL_GBM)
- Analytic E[sigma_T]:           11171300.44901763
- Empirical mean(sigma_T):       11296507.25212178
- mean rel-err:                  0.01120789863951421 (< MOMENT_REL_TOL = 0.05 -> PASS)
- Analytic Var[sigma_T]:         99838416612391.44 (Isserlis Gaussian-quadratic-form per spec v0.5 §11.6 audit-trail)
- Empirical var(sigma_T):        121069197946322.05
- var rel-err (audit-trail):     0.21265142271192183 (NOT gated; observation-only per v0.5 §11.6)

## OU at canonical pin (CANONICAL_OU)
- Analytic E[sigma_T]:           13543536.284575583
- Empirical mean(sigma_T):       13566307.513933085
- mean rel-err:                  0.0016813355743311377 (< MOMENT_REL_TOL = 0.05 -> PASS)
- Analytic Var[sigma_T]:         28537632531882.883 (Isserlis Gaussian-quadratic-form per spec v0.5 §11.6 audit-trail)
- Empirical var(sigma_T):        27763863281593.207
- var rel-err (audit-trail):     0.02711399585880866 (NOT gated; observation-only per v0.5 §11.6)

## Merton jump-diffusion at canonical pin (CANONICAL_MERTON)
- Analytic E[sigma_T]:           163700594.73530617
- Empirical mean(sigma_T):       164849022.40084106
- mean rel-err:                  0.007015415352594295 (< MOMENT_REL_TOL = 0.05 -> PASS)
- Analytic Var[sigma_T]:         2.234990225100107e+16 (Isserlis Gaussian-quadratic-form per spec v0.5 §11.6 audit-trail)
- Empirical var(sigma_T):        8.330686810915725e+16
- var rel-err (audit-trail):     2.7273929511448247 (NOT gated; observation-only per v0.5 §11.6)
