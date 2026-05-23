# SAAS-COHORT-1 — Wave-1 Reality Checker compliance audit

**Plan:** `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md` v0.2.
**Verdict author:** foreground (subagent dispatch unavailable in this harness;
see `scratch/2026-05-08-saas-cohort-1-research/STACK.md` "Execution-mode
deviation note"). Audit performed by re-reading every cohort source file and
running every assertion against the spec verbatim.
**Verdict:** **ACCEPT_WITH_FLAGS** (PROCEED).

## Audit scope

Cohort code under `simulations/saas_builder/{__init__.py, _errors.py, priors.py,
model.py, diagnostics.py, emit.py}` against:

1. functional-python three-tier discipline (every `.py` exactly one tier;
   tier-import discipline preserved).
2. Math pins enforced by direct test execution: M1 prior lower-bound +
   sampler refusal at α<1.5; M3 Sonnet `BlendedPriceFn(...)()` call-site
   assertion at 7.1495 ± 0.01; M4 schema round-trip exact column set
   including `schema_version`.
3. Diagnostic gate (r-hat ≤ 1.01 / ESS_bulk ≥ 400 AND ESS_tail ≥ 400 /
   divergence ≤ 0.5% / sim-count ≥ 4000×4 / CI-width ratio ≤ 2.0 per
   spec §8(7)) executes on every emission path; no bypass. N_MIN=75 OUT
   OF SCOPE for Stage-2.
4. Anti-fishing: no threshold tuning between spec v1.1.1 and code.
5. Audit artifacts (3.1–3.6) all present.

## Findings

### Tier discipline — PASS

- `priors.py` is Value tier: frozen-dc + `__post_init__` only. No PyMC import.
  ✓
- `model.py` is Callable tier: `T1ModelFactory` is `@dataclass(frozen=True)`
  with `__call__` returning `pm.Model`; PyMC import contained here. ✓
- `diagnostics.py` is Callable tier: arviz only; no PyMC import. ✓
- `emit.py` is Callable tier: orchestrator; writes through
  `simulations.utils.parquet_io` only; no direct pandas/pyarrow calls. ✓
- `_errors.py` carries cohort-local exception class. ✓
- All four files import only from `simulations.{types,modules,utils}` and
  from each other. NO modifications to SIM-INFRA-0 surface (verified by
  `git diff master..HEAD -- simulations/types simulations/modules
  simulations/utils` showing zero changes outside cohort scope).

### M1 (α-floor 1.5) — PASS, dual-enforced

- priors.py:TruncParetoAlphaPrior `alpha_lower >= 1.5` enforced at construction
  (line ~199 raises ValueError). Default `alpha_lower = 1.5`. ✓
- model.py: `pm.TruncatedNormal("alpha_pareto", lower=ap.alpha_lower, ...)`
  passes priors.alpha.alpha_lower into the PyMC dist (verified by
  `TestMutationKillers.test_model_alpha_lower_passed_to_pymc`). ✓
- samplers.py:TruncParetoSampler refuses α < 1.5 (SIM-INFRA-0; not modified;
  verified via `TruncParetoSampler(TruncParetoParams(alpha=1.49, ...))`
  raising `ValueError`). ✓

### M3 (Sonnet $/MTok) — PASS

- `BlendedPriceFn` symbol verified at `simulations/modules/pricing.py:24`
  with `__all__ = ["BlendedPriceFn"]` (NOT `BlendedPriceCalc`; RC-B1 fix). ✓
- model.py:_build_sonnet_blended_price calls
  `BlendedPriceFn(params=BlendedPriceParams(...))()` (no `.price_per_mtok`
  attribute, no `tier=` keyword; RC-B2 fix). ✓
- Asserted-equality at the model-factory `__call__` site (NOT in
  `__post_init__`; RC-B2 fix). ✓
- Tolerance `abs_tol=0.01` matches spec §5.1 "≈ 7.15" precision (RC-FLAG-1
  resolved). ✓

### M4 (parquet schema) — PASS

- emit.py imports `SyntheticTauWriter`, `CohortPriorWriter`, `synthetic_tau_row`,
  `cohort_prior_row` from `simulations.utils.parquet_io` (verified file:lines
  44-56 + 34-41 in shipped parquet_io.py). ✓
- All emitted rows include `schema_version` via
  `simulations.types.posterior.DEFAULT_SCHEMA_VERSION` (default `"v1.0"`;
  factory functions preserved per spec §10). ✓
- Round-trip property test
  `TestHypothesisProperties::test_property_4_synthetic_tau_round_trip_includes_schema_version`
  exercises both writer + reader and verifies the 11-column set including
  `schema_version`. ✓
- Hive partition `tier_id={pro,max5x,max20x}/month=YYYY-MM/` enforced by the
  shipped `SYNTHETIC_TAU_PARTITION_COLS`. NOTE: cohort emits raw integer
  `month` (e.g. `month=4`), NOT `YYYY-MM` string format. The shipped
  `SYNTHETIC_TAU_DTYPES["month"] = "int64"`, which matches the cohort
  emission. The `YYYY-MM` form in the plan and spec §10 description appears
  to be illustrative; the shipped writer expects `int64`. **FLAG-1**: spec
  §10 vs. shipped writer convention should be reconciled in a future plan.

### Diagnostic gate (§8(7) + §8(8)) — PASS

- diagnostics.py thresholds verified against spec verbatim:
  `RHAT_GATE = 1.01`, `ESS_BULK_GATE = 400.0`, `ESS_TAIL_GATE = 400.0`,
  `DIVERGENCE_FRAC_GATE = 0.005`, `SIM_COUNT_DRAW_FLOOR = 4000`,
  `SIM_COUNT_CHAIN_FLOOR = 4`, `CI_WIDTH_RATIO_GATE = 2.0`. ✓
- Gate refuses passed=True if ANY threshold fails (test
  `TestDiagnosticGate::test_clean_idata_passes` + four degraded cases). ✓
- §8(7) CI-width restored to HALT-gate (NOT advisory; MQ-B5 v0.1→v0.2 fix). ✓
- emit.py raises `DiagnosticGateError` BEFORE any parquet/sidecar write;
  no partial emission. ✓
- N_MIN=75 NOT in cohort code (correctly Stage-3-only per MQ-FLAG-D). ✓
  `sim_count_floor_violated` field renamed from v0.1 `n_min_violated`. ✓

### Anti-fishing — PASS

`grep -rE "75|N_MIN" simulations/saas_builder/` returns zero hits. All
diagnostic thresholds in code match spec v1.1.1 §8 verbatim.

### Audit artifacts — PASS

All six audit-pass commits present in `git log`:
- `audit(saas-cohort-1): tighten-types pass` ✓
- `audit(saas-cohort-1): contract-docstrings pass` ✓
- `audit(saas-cohort-1): hypothesis-tests pass — extended properties` ✓
- `audit(saas-cohort-1): try-except pass — no try/except blocks` ✓
- `audit(saas-cohort-1): pre-mortem pass — model + emit` ✓
- `audit(saas-cohort-1): mutation-testing pass — kill rate 100%` ✓

## Flags

- **FLAG-1** (M4 partition convention drift): spec §10 documents Hive partition
  format `month=YYYY-MM/` whereas shipped `SYNTHETIC_TAU_DTYPES["month"]` is
  `int64` (so on-disk produces `month=4/`). Cohort code conforms to shipped
  writer (correct per plan rule "writer is authority"). Future spec v1.2
  should reconcile by either bumping shipped dtype to `string` (M4 schema bump
  — SIM-INFRA-1 follow-up) or rephrasing spec §10 text. Non-blocking.
- **FLAG-2** (subagent dispatch unavailable): plan §Phase-2 calls for AI
  Engineer subagent dispatch and 2-wave RC + MQ verifier dispatch. The harness
  for this run does NOT expose a Task tool. Foreground performed all roles
  in-band with explicit verdict files. Non-blocking (acknowledged in
  scratch/2026-05-08-saas-cohort-1-research/STACK.md).
- **FLAG-3** (defensive coverage gap): emit.py:179
  `if not isinstance(self.base_dir, Path)` branch is unreachable if
  `field(default_factory=...)` always produces a Path (untested). Non-blocking;
  defensive code appropriate for the boundary.

## Verdict

**ACCEPT_WITH_FLAGS — PROCEED to Wave 2.** No BLOCKs. Three FLAGs documented;
none impede COHORT-2 / COHORT-3 / COHORT-4 dispatch. SIM-INFRA-1 follow-up
plan should pick up FLAG-1 + FLAG-3.
