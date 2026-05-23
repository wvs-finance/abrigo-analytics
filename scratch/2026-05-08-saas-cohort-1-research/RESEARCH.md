# Phase 1 — research (skipped by foreground decision)

**Decision:** SKIPPED — settled by SIM-INFRA-0 §1.1 research deliverable
(`scratch/2026-05-08-sim-infra-research/`). All four research questions
(Dirichlet hyperparameter elicitation, NUTS reparameterization for compound
likelihoods, arviz diagnostic conventions, PyMC `TruncatedPareto` availability)
were answered by the SIM-INFRA-0 Phase-1 work.

## Resolution carried forward

1. **Dirichlet `α₀ = 10·[0.20, 0.50, 0.30]`** — adopted verbatim per spec
   §5.2; concentration 10 is "mildly informative" in the standard
   weak-prior literature (Gelman BDA3 §3.5; Stan-User-Guide §11). No deviation.

2. **Compound NegBin × TruncPareto NUTS reparameterization** — known divergence
   risk near α-floor; mitigated via lower-bounded `pm.TruncatedNormal(2.0, 0.25, lower=1.5, upper=2.5)`
   per Phase-2 prelude FLAG-A. NegBin uses `pm.NegativeBinomial(mu=μ, alpha=φ)`
   per MQ-B2 pin.

3. **arviz r-hat / ESS conventions** — `az.summary` with `var_names=`
   restriction; `az.rhat` / `az.ess` for direct scalar extraction. Convention
   pinned in diagnostics.py docstring.

4. **PyMC `TruncatedPareto`** — PyMC 5.28 ships `pm.Truncated(pm.Pareto(...), lower, upper)`
   wrapper. Used directly; no custom logp.

## Module-boundary review (Phase 1.2 — foreground)

`simulations/saas_builder/` placement reviewed against three-tier discipline:

- `priors.py` — Value tier (frozen-dc parameter containers; `__post_init__`
  enforces M1 floor at prior level).
- `model.py` — Callable tier (frozen-dc `__call__(observed) -> pm.Model`);
  imports PyMC; this is the layer where PyMC enters the codebase.
- `diagnostics.py` — Callable tier (frozen-dc `__call__(idata) -> DiagnosticVerdict`);
  imports arviz; no PyMC.
- `emit.py` — Callable tier (orchestrator); imports `simulations.utils.parquet_io`
  (IO Boundary tier); only place with non-trivial try/except.

No infrastructure gap surfaced. Generalizes cleanly to future cohort packages
(`simulations/pair_d/`, `simulations/dev_ai/`).

**Deviation from plan §"emit.py behavior contract":** the plan calls for
`DiagnosticGateError` to live in `simulations.utils.errors`. Per the plan's
own §"Out of scope (NON-NEGOTIABLE)" rule that infrastructure extensions are
SIM-INFRA-0 follow-ups, the foreground defines `DiagnosticGateError` cohort-local
(`simulations/saas_builder/_errors.py`) instead. This honors the no-modify-utils
discipline strictly. Logged for post-hoc review.
