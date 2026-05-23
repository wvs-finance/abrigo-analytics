# KS Test Log — Stochastic-FX End-to-End Run 2026-05-13

**Spec version:** v0.5
**Plan version:** v0.6
**KS_PVALUE_FLOOR:** 0.01
**N_REF_SEED:** 20260513 (spec-pinned)

## GBM (Phase C: moment-matched lognormal MoM reference, scipy.stats.ks_1samp)
Reference shape s = sqrt(log(1 + Var/E²)), scale = E/sqrt(1 + Var/E²) constructed from ANALYTIC moments (Method-of-moments per NIT-MQ-1 disposition).
- ks_pvalue: 0.12289679125954278 (>= 0.01 -> PASS)

## OU (Phase C: moment-matched gamma MoM reference, scipy.stats.ks_1samp)
Reference shape a = E²/Var, scale = Var/E constructed from ANALYTIC moments.
- ks_pvalue: 0.3033295604461448 (>= 0.01 -> PASS)

## Merton (Phase C: empirical-CDF via high-N reference run, scipy.stats.ks_2samp)
- N_REF actually used: 5000 (HARDWARE-CONSTRAINED per FLAG-RC-V0.5-1; production spec-pinned N_REF = 100_000 unchanged in simulations/stochastic_fx/variance_proxy.py).
- N_REF_SEED: 20260513
- ks_2samp pvalue: 0.11595645029665462 (>= 0.01 -> PASS)

## Determinism cross-check (Pin Z1.2)
- gbm: BIT-EXACT (first run audit_block prefix `3a0f75401d517f6d`; second run audit_block prefix `3a0f75401d517f6d`)
- ou: BIT-EXACT (first run audit_block prefix `0589f35b10f1ca7f`; second run audit_block prefix `0589f35b10f1ca7f`)
- merton: BIT-EXACT (first run audit_block prefix `12890ce95a36ffea`; second run audit_block prefix `12890ce95a36ffea`)
