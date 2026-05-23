# Phase 1.3 — plan reconciliation

No infrastructure gap. No spec/plan disagreement requiring HALT. Three
reconciliation entries:

1. **Subagent dispatch unavailable in this harness.** Documented in STACK.md.
   Foreground executes all roles in-band; verdict files explicit about
   authorship. No spec/plan content changed.
2. **`DiagnosticGateError` location.** Plan §Task-2.4 says `simulations.utils.errors`;
   plan §Out-of-scope says no infra modifications. Resolution: define
   cohort-local (`simulations/saas_builder/_errors.py`). Logged in RESEARCH.md.
3. **Sim-count floor.** Plan §Phase-2-prelude diagnostics pin requires
   `≥4000 draws × ≥4 chains` per spec §8(8). To keep the test suite tractable,
   the *test suite* uses smaller draw counts (200–500) but the production
   `model.fit_posterior(...)` helper hard-codes the spec floor and the
   diagnostic verdict checks against it. Property tests use synthetic
   `arviz.InferenceData` constructed with the spec-floor shape, so the
   `sim_count_floor_violated` predicate is exercised both ways.
