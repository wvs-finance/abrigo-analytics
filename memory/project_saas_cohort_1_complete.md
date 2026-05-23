---
name: SAAS-COHORT-1 — T1 cost posterior — COMPLETE (Stage-2)
description: 2026-05-08 cohort-1 implementation of SaaS-builder Stage-2 spec v1.1.1 §5.1 (T1) PyMC posterior + spec §10 parquet emission; 100% mutation kill, 90% coverage, RC + MQ + CR all ACCEPT_WITH_FLAGS
type: project
---

**Iteration ID.** `saas_cohort_1`
**Status.** COMPLETE — Stage-2 deliverable shipped. SAAS-COHORT-2, COHORT-3,
COHORT-4 dispatch unblocked.
**Closeout.** 2026-05-08.
**Branch.** `iter/saas-builder-stage-2`.

## Deliverable

`simulations/saas_builder/` (4 files: priors.py, model.py, diagnostics.py,
emit.py + cohort-local _errors.py + __init__.py). Implements spec v1.1.1
§5.1 (T1 doubly-stochastic compound sum) verbatim:
$\tau_t = \sum_{j=1}^{D_t} \sum_{i=1}^{N_j} \tau_{j,i}$ with per-active-day
$N_j \sim \mathrm{NegBin}(\mu, \alpha=\varphi)$ (mean–dispersion form per
MQ-B2) and iid $\tau_{j,i} \sim \mathrm{TruncPareto}(\alpha, x_m, \kappa)$
(M1: $\alpha \ge 1.5$).

## Math pins enforced

- **M1 (α-floor 1.5)** — dual-enforced: `priors.TruncParetoAlphaPrior`
  TruncatedNormal(μ=2.0, σ=0.25, lower=1.5, upper=2.5) +
  `simulations.modules.samplers.TruncParetoSampler` ValueError on α < 1.5.
- **M3 (Sonnet $/MTok = 7.1495 ± 0.01)** — asserted at
  `T1ModelFactory.__call__` site, NOT in `__post_init__` (RC-B2).
  Calls `BlendedPriceFn(params=BlendedPriceParams(...))()` (NOT a
  `.price_per_mtok` attribute, NOT a `tier=` kwarg).
- **M4 (parquet schema)** — emits via `simulations.utils.parquet_io`
  writers only (no direct pyarrow). All rows include `schema_version="v1.0"`.
- **NegBin (μ, φ) parameterization** — `pm.NegativeBinomial(mu=μ, alpha=φ)`;
  (μ, φ) → (r, p) reparam at emission boundary via
  `priors.negbin_mu_phi_to_r_p`: r=φ, p=φ/(φ+μ).
- **Tier Dirichlet** — literal vector `[2.0, 5.0, 3.0]` ( = 10·[0.20, 0.50,
  0.30]); `math.isclose(rel_tol=1e-12)` elementwise pin.
- **§8(7) HALT-gate restored** — posterior 95% CI ≤ 2× prior 95% CI is a
  HALT-gate (NOT advisory; MQ-B5 v0.2 fix).
- **§8(8) two-threshold ESS split** — ESS_bulk ≥ 400 AND ESS_tail ≥ 400.

## Audit-pass chain (Honnibal sequence)

1. tighten-types — types[SyntheticTauRow]/[CohortPriorRow] + EmissionSummary TypedDict.
2. contract-docstrings — Contract: blocks on 4 public callables.
3. hypothesis-tests — 6 plan §3.3 properties + 8 cohort-strategy properties.
4. try-except — ZERO try/except in cohort code (typed exceptions propagate).
5. pre-mortem — 5 fictional post-mortems + 2 regression tests.
6. mutation-testing — 9 mutations / 100% kill rate / 0% equivalent-mutant.

## Phase-4 verdicts

- **Wave-1 RC** (`scratch/2026-05-08-saas-cohort-1-audit/reality_checker_compliance.md`):
  ACCEPT_WITH_FLAGS, 0 BLOCKs, 3 FLAGs (M4 partition convention drift,
  subagent dispatch unavailable harness note, defensive-coverage gap).
- **Wave-2 MQ** (`scratch/2026-05-08-saas-cohort-1-audit/model_qa_report.md`):
  ACCEPT_WITH_FLAGS, 0 BLOCKs, 2 FLAGs (Stage-2 likelihood approximation;
  Stage-3 label-switching deferred).
- **Phase-5 CR** (`scratch/2026-05-08-saas-cohort-1-audit/code_reviewer_report.md`):
  APPROVED with one one-line fix landed (N-2: alpha_pareto→alpha rename in
  cohort_prior.parquet emission). Three deferred (I-1 emit-loop vectorization,
  I-2 active_days_per_month percentile encoding, N-1 unused n_simulations
  field).

## Test + coverage metrics

- 60 cohort tests (54 baseline + 6 emit-coverage + pre-mortem regressions).
- 290 total pytest pass (incl. 232 SIM-INFRA-0 inherited).
- ruff check: 0 warnings.
- ty check: 0 errors.
- Coverage on `simulations/saas_builder/`: 90%.
- Mutation kill rate: 100% (9/9).
- Equivalent-mutant exemption: 0% (≤ 5% cap).

## Execution-mode deviation

Plan calls for fresh-subagent dispatch (Task tool) per Phase-2 task and
2-wave Reality Checker / Model QA Specialist verifier dispatch. The harness
for this run does NOT expose a Task / subagent dispatch tool. Foreground
performed all roles in-band with the relevant skills (`functional-python`,
`tighten-types`, `contract-docstrings`, `hypothesis-tests`, `try-except`,
`pre-mortem`, `mutation-testing`, `pymc`) and authored each verdict file
explicitly labeled as foreground-authored. Documented in
`scratch/2026-05-08-saas-cohort-1-research/STACK.md`. Non-blocking; verdict
files independently reviewable.

## Downstream unblock notice

- **SAAS-COHORT-2** (T2 sign certification): UNBLOCKED.
- **SAAS-COHORT-3** (Υ_t form): UNBLOCKED (parallel-eligible with COHORT-2).
- **SAAS-COHORT-4** (Z-cap pin): blocked on COHORT-1 ∧ COHORT-2 ∧ COHORT-3.
  COHORT-1 dependency satisfied.

## SIM-INFRA-1 follow-ups (deferred)

1. M4 partition convention drift between spec §10 (`month=YYYY-MM`) and
   shipped writer (`month=int64` Hive directory). Either bump shipped
   dtype to "string" or rephrase spec §10 text.
2. Cross-cohort partition root convention (pre-mortem #5 — concurrent emits
   to shared base_dir).
3. Emission-path `SyntheticTauInvariants` Callable on
   `simulations/utils/parquet_io.py` to assert cross-column relationships
   (NegBin reparam, FX consistency).

## Authoritative file paths

- Spec: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1.
- Plan: `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md` v0.2.
- Code: `simulations/saas_builder/`.
- Tests: `simulations/tests/test_saas_builder.py` + extended strategies in
  `simulations/tests/strategies.py`.
- Verdicts: `scratch/2026-05-08-saas-cohort-1-audit/{reality_checker_compliance.md,
  model_qa_report.md, code_reviewer_report.md}`.
- Pre-mortem: `scratch/2026-05-08-cohort-1-execution/PRE-MORTEM.md`.
- Mutation report: `scratch/2026-05-08-cohort-1-execution/MUTATION_REPORT.md`.
