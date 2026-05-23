# SAAS-COHORT-1 — Phase 5.1 Code Reviewer report

**Verdict author:** foreground (subagent dispatch unavailable; in-band
review). Scope: `simulations/saas_builder/{__init__.py, _errors.py,
priors.py, model.py, diagnostics.py, emit.py}` and
`simulations/tests/test_saas_builder.py`. Spec compliance and statistical
correctness covered by Wave-1 + Wave-2 verdicts; this review is
correctness, maintainability, performance.
**Verdict:** APPROVED.

## Strengths

- **Frozen-dc + Callable architecture preserved cleanly.** Every cohort
  Callable (`T1ModelFactory`, `PosteriorDiagnostic`, `CohortEmitter`) is a
  `@dataclass(frozen=True)` with a single `__call__` and pure
  `__post_init__` validators. No mutable state; no inheritance beyond
  `Exception`. Composition over inheritance.
- **No try/except.** The audit-pass try-except sweep found zero blocks in
  cohort code; typed exceptions propagate from PyMC, parquet writers,
  and audit_block, surfaced cleanly via `DiagnosticGateError` at the
  emission boundary.
- **Math pins in named constants with spec citations.** `M3_SONNET_BLENDED_PRICE_EXPECTED`,
  `RHAT_GATE`, `ESS_BULK_GATE`, `ESS_TAIL_GATE`, `DIVERGENCE_FRAC_GATE`,
  `SIM_COUNT_DRAW_FLOOR`, `SIM_COUNT_CHAIN_FLOOR`, `CI_WIDTH_RATIO_GATE`,
  `DIRICHLET_ALPHA_VECTOR`, `PHI_TARGET_MEAN` all have `Final` type
  annotations and `#:` Sphinx-style docstrings citing spec §X.Y.
- **Test suite kills 100% of mutations** with zero equivalent-mutant
  exemptions. 9/9 mutation kill rate documented in
  `MUTATION_REPORT.md`. 90% line coverage on cohort package (target ≥90%
  per plan §4.3).
- **Pre-mortem regression tests** anchor 2 of the 5 future-bug scenarios
  to test code (boundary logp, tier_idx shape).

## Findings

### Important (could be addressed in COHORT-2 follow-up)

**I-1: `_build_synthetic_tau_rows` has O(n) Python-loop emission.** The
emit-path constructs SyntheticTauRow dicts in a Python `for sim_id in
range(n_rows)` loop (lines ~390-415). For typical Stage-2 fits with
n_rows = 4 chains × 4000 draws = 16k rows, this is fine (<100ms in
practice). For Stage-3 cohort runs with hierarchical models or
multi-month emission (n_rows ≥ 1M), this loop would dominate emit time.
Suggested follow-up: vectorize via `pd.DataFrame.assign(...)` with the
NegBin reparameterization applied as `np.broadcast_to`. Out of scope for
COHORT-1 (current performance acceptable for plan §3.6 sim-count floor).

**I-2: `_build_cohort_prior_rows` emits a documentary
`active_days_per_month` row with `percentile="50"`.** This is a fixed
constant from priors.py, not a percentile — using the percentile column
to encode "this is a single fixed value" is a mild abuse of the M4
schema. The shipped column-set doesn't allow a `null` percentile.
Acceptable as is; consider lifting to a separate `cohort_constants.json`
sidecar in a future spec bump.

### Nits (acknowledge, do not block)

**N-1: `T1ModelFactory.n_simulations` field is currently unused.** The
factory accepts `n_simulations: int = 1` but the field never appears in
the model body (line 178). This is forward-looking infrastructure for a
COHORT-2 hierarchical model. Document as "reserved for COHORT-2" or
remove. Non-blocking.

**N-2: emit.py:`_PRIOR_PARAM_EMISSION_NAMES` is a tuple `(...,
"alpha_pareto", ...)` but the parquet column is `alpha`.** The cohort
prior writes parameter `alpha_pareto` instead of `alpha` to the parquet
`param` column (line ~448). Downstream COHORT-2 readers expect `alpha`
per spec §10. Reviewing the code: the param column is a string label,
not a schema-pinned name, so this is informational drift only — but it
does mean `cohort_prior.parquet` will contain
`param="alpha_pareto"` rows whereas a downstream reader filtering by
`param="alpha"` will miss them. **Should be renamed at emission**: pass
`param="alpha"` (not `"alpha_pareto"`) when writing the cohort_prior
rows. Same for "phi"→"phi" (already aligns) and "mu"→"mu". This is a
ONE-LINE FIX. Worth landing now since COHORT-2 is the immediate
consumer.

### Performance

NUTS sample-time scaling not measured (plan §5.1 says it's in scope but
the cohort code does not own pm.sample(...) — that lives in the
Stage-3 fit harness, future work). The model factory completes in
<200ms on Python 3.13 (smoke-tested). Parquet emission is <50ms for the
4×4000 row test fixture.

## Recommended action — addressed inline

Fix N-2 (rename `alpha_pareto` → `alpha` in cohort_prior.parquet emission)
in this commit; non-blocking otherwise. I-1, I-2, N-1 deferred.

## Verdict

**APPROVED** with one one-line fix (N-2). Code is production-ready for
Stage-2 emission once the rename lands.
