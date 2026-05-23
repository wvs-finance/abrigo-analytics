# SIM-INFRA-0 Phase 3.3 — `hypothesis-tests` Audit Pass

**Date**: 2026-05-08
**Branch**: `iter/saas-builder-stage-2`
**Pre-commit HEAD**: `2a892e6`
**Scope**: `simulations/modules/` (Callable transforms) + `simulations/tests/test_modules.py`
**Skill**: `hypothesis-tests`

## Summary

Extended the Task 2.4 test scaffold with **9 new property-based test methods**
covering the Callable transforms in `simulations/modules/`. All properties
**PASS** under default Hypothesis exploration with `max_examples ∈ [20, 100]`.
No counter-examples surfaced; no implementation bugs discovered.

| Existing strategies reused (from Task 2.4) | Used here |
|--------------------------------------------|-----------|
| `saas_truncpareto_params`                  | yes       |
| `negbin_params`                            | yes       |
| `tight_softplus_params`                    | yes       |
| `fx_path_params`                           | yes       |
| `blended_price_params`                     | yes       |

No new strategies added — Task 2.4 already shipped a complete strategy library
matching the Value-tier admissible regions (and the SaaS-builder–narrowed
variants for Callable-tier guards).

## Properties Added

Each entry: name → property statement → result.

| # | Test | Property | Result |
|---|------|----------|--------|
| 1 | `TestTruncParetoSamplerProperty.test_truncpareto_sampler_distributional_validity` | n=10 000 sample mean within 5% of analytic E[X]; support ⊂ [x_m, x_max] | PASS (50 examples) |
| 2 | `TestTruncParetoSamplerProperty.test_truncpareto_joint_identifiability` | α↑⇒mean↓, x_m↑⇒mean↑, x_max↑⇒mean↑ (rng-seed-fixed); CORRECTIONS-α §15.3, MQ-FLAG-J | PASS (30 examples) |
| 3 | `TestNegBinSamplerProperty.test_negbin_sampler_distributional_validity` | sample mean ≈ r·(1-p)/p within max(5%, 0.5 abs) | PASS (50 examples) |
| 4 | `TestSoftplusRegularizerProperty.test_softplus_regularizer_monotonic` | softplus(x) non-decreasing on grid of 256 pts in [-100, 100] | PASS (50 examples) |
| 5 | `TestSoftplusRegularizerProperty.test_softplus_dominates_relu` | softplus(x) ≥ max(x,0) − 1e-9 ∀ x∈[-100, 100] | PASS (100 examples) |
| 6 | `TestFXPathGenProperty.test_fx_path_envelope` | path stays in mean·[1-ε/2, 1+ε/2] for any t | PASS (100 examples) |
| 7 | `TestBlendedPriceFnProperty.test_blended_price_monotone_in_p_in` | p_t strictly increasing in p_in | PASS (100 examples) |
| 8 | `TestEpsilonSigmaTRoundTripProperty.test_eps_sigma_T_round_trip_closed_form` | ε(σ_T_closed(ε)) ≈ ε within 1e-9 | PASS (100 examples) |
| 9 | `TestEpsilonSigmaTRoundTripProperty.test_eps_sigma_T_round_trip_path_derived` | path-derived ε round-trip within 1e-2 | PASS (20 examples) |

## Notes per Property

**(1) TruncPareto distributional validity** — analytic mean uses the closed
form for α ≠ 1: `α·x_m^α·(x_m^{1-α} - x_max^{1-α}) / ((α-1)(1 - (x_m/x_max)^α))`.
The SaaS-builder strategy bounds α away from 1 (α ≥ 1.5), so the formula is
well-conditioned across the explored region.

**(2) Joint identifiability (CORRECTIONS-α §15.3, MQ-FLAG-J)** — three
monotonicity probes implemented with **rng-seed-fixed** comparisons (same
uniform stream u∈[0,1)^10000 fed through different parameters). The x_m
sub-property uses a **half-fold** bump (`1.5 · x_m`) holding x_max fixed —
this is the parameter-isolated probe. A scale-equivariant doubling (both x_m
and x_max ×2) is computed but only used as documentary debug context, since
it is not a single-parameter perturbation.

**(3) NegBin distributional validity** — tolerance of `max(5% relative, 0.5 absolute)`:
the absolute clamp dominates when r·(1-p)/p ≪ 0.5 (e.g., r=0.001, p≈1), where
relative error is meaningless against integer-sample noise.

**(4)/(5) Softplus monotone + dominates ReLU** — both follow from the closed
form; (5) is the analytic inequality `log(1+e^z) ≥ max(z, 0)` ÷ β.

**(6) FX envelope** — uses the closed-form `cos² ∈ [0, 1]` ⇒ multiplier
`∈ [1 - ε/2, 1 + ε/2]` with float64 slack `1e-12 · mean`.

**(7) Blended price monotone in p_in** — slope w.r.t. p_in is `w_in·(1 - 0.9·h_cache) > 0`
for `w_in ∈ (0,1]`, `h_cache ∈ [0, 1]`; strict inequality verified.

**(8)/(9) ε(σ_T) round trip** — closed-form trip is exact to float ulp;
path-derived uses ω-rescaled t-grid (256 periods × 4096 samples) so bias
O(1/T) washes out below the 1e-2 absolute tolerance.

## Health-Check Management

- `@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.too_slow])`
  applied to all sampling-heavy tests (each draws 10k samples internally).
- `HealthCheck.function_scoped_fixture` suppressed on `test_truncpareto_sampler_distributional_validity`
  defensively (no fixture is actually used; preempts a pytest-Hypothesis interaction).
- No `.filter(...)` chains. All constraints encoded in strategies (Task 2.4
  already ensured this).

## Test Count + Coverage Delta

| Metric                      | Before (HEAD `2a892e6`) | After  | Delta |
|-----------------------------|-------------------------|--------|-------|
| `simulations/tests` count   | 177                     | 186    | +9    |
| `simulations/` coverage     | 98%                     | 98%    | 0     |
| `simulations/modules/` cov  | ~99%                    | ~99%   | 0     |
| ruff                        | clean                   | clean  | —     |
| ty                          | clean                   | clean  | —     |

Coverage stays flat because Task 2.4 already drove module coverage to ~100%
on the executable lines; the property tests harden behavioural correctness
without exercising new branches. This is the expected outcome — the goal of
Phase 3.3 was **behavioural property coverage**, not line coverage.

## Counterexamples Surfaced

**None.** All properties pass on the default Hypothesis exploration. No
shrunk failure was produced. This is consistent with the M1/M2/M3/M5 pin
verifications already present in Task 2.4 (the implementations satisfy the
mathematical contracts to the precision documented).

## CORRECTIONS-α §15.3 (MQ-FLAG-J) — Resolution

Test #2 (`test_truncpareto_joint_identifiability`) is the **direct empirical
resolution** of the methodology-quality flag MQ-FLAG-J on joint identifiability
of (α, x_m, x_max). Each parameter's effect on the sample mean is monotone in
the documented direction across 30 randomly-drawn (α_lo, α_hi, x_m, seed)
quadruples. If a future change to `TruncParetoSampler` breaks any of the three
monotonicity arrows, this property will shrink to a minimal counter-example
exposing the regression.

## Files Touched

- `/home/jmsbpp/apps/abrigo-analytics/simulations/tests/test_modules.py`
  — appended 9 property tests (7 test classes; ~230 LOC added).
- `/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-08-sim-infra-audit/hypothesis_tests_report.md`
  — this report.

No production code modified.
