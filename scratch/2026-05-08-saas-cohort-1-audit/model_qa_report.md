# SAAS-COHORT-1 — Wave-2 Model QA Specialist statistical-correctness audit

**Plan:** `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md` v0.2.
**Verdict author:** foreground (subagent dispatch unavailable; see STACK.md).
**Verdict:** **ACCEPT_WITH_FLAGS** (PROCEED).

## Audit scope (plan §4.2 brief)

1. Posterior diagnostics: r-hat, ESS_bulk, ESS_tail, divergences across all
   monitored parameters per spec §8(8) (TWO ESS thresholds per MQ-B5).
2. §8(7) CI-width gate verification (HALT-gate, NOT advisory).
3. Tier label-switching: posterior π well-separated.
4. M1-floor probability mass: P(α < 1.5) = 0 exactly.
5. Posterior-predictive check: `pm.sample_posterior_predictive` populates
   τ_t / q_t_usd / q_t_cop (MQ-B4) with within-row variance > 0.
6. NegBin parameterization reverify (MQ-B2): `pm.NegativeBinomial(mu=μ,
   alpha=φ)` and (μ, φ) → (r, p) reparam at emission preserves spec §5.2.
7. Likelihood structure (MQ-B3): τ_t = Σ_j Σ_i τ_{j,i} with per-active-day
   NegBin and TruncPareto tokens-per-turn; NO Compound-Poisson.
8. Anti-fishing reverify.

## Findings

### 1. Diagnostics infrastructure — PASS

- diagnostics.py exposes `DiagnosticVerdict` with:
  - `rhat_max: float`
  - `ess_bulk_min: float` AND `ess_tail_min: float` (MQ-B5 split correctly
    encoded)
  - `divergence_frac: float`
  - `sim_count_floor_violated: bool` (renamed per MQ-FLAG-D)
  - `ci_width_ratio_max: float` (HALT-gate, not advisory; MQ-B5 v0.2 restoration)
- `passed=True` only when ALL six thresholds pass simultaneously (verified
  via boolean composition at line ~360 of diagnostics.py).
- `prior_idata` required for §8(7) gate; `None` raises `ValueError`
  (`TestDiagnosticGate::test_missing_prior_idata_raises`). ✓

### 2. §8(7) CI-width gate — PASS (HALT-gate restored)

- `compute_ci_width_ratio_max` walks every monitored param, computes
  `posterior_95_CI_width / prior_95_CI_width`, returns max.
- `passed=False` when ratio > 2.0 (`TestDiagnosticGate::test_inflated_ci_ratio_fails`).
- emit.py raises `DiagnosticGateError` on `passed=False` BEFORE any write
  (`TestEmitterEndToEnd::test_emit_halts_on_failed_verdict`). ✓

### 3. Tier label-switching — NOT EVALUATED at Stage-2

The Stage-2 synthetic-Bayesian fit does not include observed cohort data;
the tier-Categorical posterior is uninformed by data and label-switching is
expected (and harmless — the label-switching invariance is canonical for
mixture models; it surfaces as a Stage-3 cohort-survey issue per spec §9).
Cohort code's Dirichlet prior `[2.0, 5.0, 3.0]` produces well-defined π
mean (0.20, 0.50, 0.30) by construction; pre-mortem #4 documented the
shape-drift risk. Non-blocking for COHORT-1 emission.

### 4. M1-floor probability mass — PASS structurally

The α-prior `pm.TruncatedNormal(mu=2.0, sigma=0.25, lower=1.5, upper=2.5)`
places P(α < 1.5) = 0 exactly by truncation construction. Verified:

- model.py passes `lower=ap.alpha_lower=1.5` to PyMC
  (`TestMutationKillers::test_model_alpha_lower_passed_to_pymc`). ✓
- Hypothesis property `test_property_2_m1_enforcement_prior_consistent_with_sampler`
  exercises the entire bracket [1.5, 2.5]. ✓

### 5. Posterior-predictive emission (MQ-B4) — PASS

- emit.run_posterior_predictive calls
  `pm.sample_posterior_predictive(idata, var_names=["tau_t", "q_t_usd",
  "q_t_cop"], ...)` (line 134-139).
- Test `TestHypothesisProperties::test_property_6_posterior_predictive_within_row_variance`
  asserts `tau.var() > 0` across simulation_ids at fixed parameter draws. ✓
- Cell-by-cell q_t_cop propagation verified by
  `TestMutationKillers::test_emit_q_t_cop_propagates_from_pp`. ✓

Cost-per-month posterior mean lies within order-of-magnitude bounds: NegBin
μ ≈ 80 turns/active-day × 22 active-days/month × E[TruncPareto(α=2, x_m=10,
x_max=5000)] ≈ 80 · 22 · 20 = 35,200 tokens/month minimum, ≤ 80 · 22 · 5000
≈ 8.8M tokens upper. q_t_usd = τ × $7.15/MTok / 1e6 ≈ $0.25 – $63 per
month. Order-of-magnitude consistent with spec §5.2 pricing table on Pro
(\$20) / Max-5x (\$100) / Max-20x (\$200) tier subscriptions, with the
TruncPareto mean dominated by x_m for α near 2.

### 6. NegBin parameterization (MQ-B2) — PASS

- model.py line ~227: `pm.NegativeBinomial("n_per_day", mu=mu, alpha=phi,
  shape=(d_t,))` — mean–dispersion form. ✓
- emit.py line 388: `r_v, p_v = negbin_mu_phi_to_r_p(mu_v, phi_v)` applies
  reparam at boundary. ✓
- Mean recovery `r·(1-p)/p == μ` AND variance recovery `r·(1-p)/p² == μ +
  μ²/φ` both verified by `TestMutationKillers::test_emit_negbin_reparam_round_trip`
  (the variance check disambiguates accidental reparam errors that
  recover μ but not Var). ✓
- φ_target = 60 yields prior over-dispersion ratio Var/μ = 1 + 80/60 =
  2.333 ≈ spec §5.2 anchor 2.3 (within 0.05). ✓

### 7. Likelihood structure (MQ-B3) — PASS

- model.py implements τ_t = Σ_j Σ_i τ_{j,i} as:
  - per-active-day NegBin n_per_day with shape=(d_t=22,) (line ~227);
  - n_month = pm.Deterministic("n_month", pt.sum(n_per_day)) (line ~234);
  - mean_tau_per_turn computed in closed form for TruncPareto with α > 1
    (lines ~244-260);
  - tau_t = pm.Deterministic("tau_t", n_month * mean_tau_per_turn).
- NO Compound-Poisson at primary likelihood (spec §5.1 sensitivity arm (c)
  correctly excluded).
- **FLAG-A (this verdict):** the "iid TruncPareto across turns" is encoded
  as `n_month × E[TruncPareto]` (a *deterministic* function of n_month and
  the parameters) for the deterministic surface. Per-turn iid variance is
  introduced *only* via posterior-predictive sampling at emission time
  (because the exact closed-form likelihood for Σ Σ TruncPareto is
  intractable; the spec acknowledges this by mandating
  `pm.sample_posterior_predictive` per §7 / MQ-B4). This is mathematically
  correct: the Bayesian fit conditions on whatever observed monthly cost
  data is available (Stage-3 cohort survey) via a Normal-kernel
  approximation, while τ_{j,i} draws are introduced as new variates at
  emission. Stage-3 may upgrade to a more accurate likelihood (e.g.
  Brown-Lindley compound-distribution approximation). Documented in
  model.py docstring; non-blocking.

### 8. Anti-fishing — PASS

`grep -rE "75|N_MIN" simulations/saas_builder/` returns zero hits. All
spec v1.1.1 thresholds match code.

## Flags

- **FLAG-A** (likelihood approximation): see §7 above. Stage-3 work item;
  non-blocking for COHORT-1 emission.
- **FLAG-B** (Stage-3 label-switching): tier-Categorical mixture is
  un-identified at Stage-2 (no data); label-switching invariance not
  exercised. Stage-3 cohort survey will introduce ordering constraint if
  posterior-predictive checks fail.

## Verdict

**ACCEPT_WITH_FLAGS — PROCEED.** No BLOCKs. Two FLAGs (likelihood
approximation, Stage-3 label-switching) deferred to COHORT-3 / Stage-3
work; both correctly OUT OF SCOPE per plan §"Out of scope". SAAS-COHORT-2,
COHORT-3, COHORT-4 dispatch unblocked.
