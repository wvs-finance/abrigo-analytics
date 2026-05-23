# SAAS-COHORT-1 — Mutation testing report

**Scope:** `simulations/saas_builder/` (4 files: priors.py, model.py, diagnostics.py, emit.py).
**Method:** manual targeted mutations (9 total), one at a time, full
`pytest simulations/tests/test_saas_builder.py` between revert.
**Plan §3.6 thresholds:** ≥80% kill rate; ≤5% equivalent-mutant exemption.

## Summary

| #  | File              | Mutation                                            | Initial result | After hardening |
|----|-------------------|-----------------------------------------------------|----------------|-----------------|
| 1  | priors.py         | `DIRICHLET_ALPHA_VECTOR[2]` 3.0 → 3.5               | KILLED clear   | KILLED          |
| 2  | priors.py         | Flip `not math.isclose(...)` → `math.isclose(...)`  | KILLED clear   | KILLED          |
| 3  | model.py          | `M3_SONNET_BLENDED_PRICE_EXPECTED` 7.1495 → 7.30    | KILLED clear   | KILLED          |
| 4  | model.py          | TruncatedNormal `lower=ap.alpha_lower` → `lower=0.0` | SURVIVED       | KILLED clear    |
| 5  | diagnostics.py    | `rhat_max <= RHAT_GATE` → `rhat_max >= RHAT_GATE`    | KILLED clear   | KILLED          |
| 6  | emit.py           | Month guard `month <= 0` → `month < 0`              | SURVIVED       | KILLED clear    |
| 7  | emit.py           | Drop `negbin_mu_phi_to_r_p`; write `(mu, 0.5)`      | SURVIVED       | KILLED clear    |
| 8  | diagnostics.py    | `SIM_COUNT_DRAW_FLOOR` 4000 → 100                   | KILLED clear   | KILLED          |
| 9  | emit.py           | `q_t_cop=float(qcop_arr[sim_id])` → `q_t_cop=0.0`   | SURVIVED       | KILLED clear    |

**Initial mutation score:** 5/9 = **55.6%** (below 80% threshold).
**Post-hardening mutation score:** 9/9 = **100%**.
**Equivalent-mutant exemptions:** 0 / 9 = **0%** (well under 5% cap).

## Surviving-mutation gap analysis (initial pass)

Four mutations survived the original 50-test cohort suite. Pattern: the surviving
mutations targeted the **emission path's per-cell content** and **boundary
guards** that no test directly asserted. Specifically:

- **#4** — model.py's `lower=ap.alpha_lower` was tested only via the priors-tier
  `__post_init__`. The Bayesian-level α-floor (the actual PyMC distribution
  parameter) had no model.py-side assertion.
- **#6** — `month <= 0` was a single-comparator boundary; no test passed
  `month=0` as the off-by-one boundary case.
- **#7** — emit-path NegBin reparam `(μ, φ) → (r, p)` was unit-tested in
  isolation in `priors.py`, but the *emit-path consumer* in `emit.py` was not
  round-trip-tested at the cell level.
- **#9** — emit-path q_t_cop column was tested for non-zero variance
  (Property #6) but not for value-by-value equality with the posterior-predictive
  group input.

## Hardening — 4 new tests in `TestMutationKillers`

`simulations/tests/test_saas_builder.py::TestMutationKillers` adds 4 tests
that target each surviving mutation:

1. `test_model_alpha_lower_passed_to_pymc` — kills #4 by inspecting the
   `alpha_pareto` PyMC RV's owner.inputs and verifying `1.5` is among the
   symbolic scalar bounds.
2. `test_emit_negbin_reparam_round_trip` — kills #7 by pinning (μ, φ) at
   (80, 60), running emit, and asserting BOTH `r·(1-p)/p == μ` and
   `r·(1-p)/p² == μ + μ²/φ` to disambiguate accidental equality at the mean
   under wrong reparameterization.
3. `test_emit_q_t_cop_propagates_from_pp` — kills #9 by pinning a known
   non-zero pp.q_t_cop array and asserting cell-by-cell equality between
   first-100 emit rows and `pp.q_t_cop.ravel()[:100]`.
4. `test_emit_month_zero_rejected` — kills #6 by passing `month=0` and
   asserting `pytest.raises(ValueError, match="month")`. The mutation flips
   the boundary so month=0 reaches the diagnostic gate, raising
   `DiagnosticGateError` instead — wrong type, test fails, mutation killed.

## Diagnostic quality (kill messages)

All 9 killed mutations produced **clear** diagnostic messages — each test
name immediately points to the spec/pin under test, and the failure message
includes the offending value vs. the expected pin. No cascading or indirect
failures.

## Equivalent-mutant exemption inventory

None claimed. The 9 mutations were chosen to be semantically meaningful;
none of them fall into the equivalent-mutant category (no-op, dead-code,
optimization-equivalent rewrites).

## Recommendations preserved for SIM-INFRA-1

The pre-mortem (PRE-MORTEM.md) "Themes and Recommendations" section flags
two structural patterns (math pins double-encoded + emission column
convention unasserted) that the hardening here partially addresses but
should be lifted to `simulations/utils/parquet_io.py` as a
`SyntheticTauInvariants` Callable in a follow-up. This is documented as
SIM-INFRA-1 follow-up scope, OUT OF SCOPE for COHORT-1.
