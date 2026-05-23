---
artifact_kind: plan_reconciliation_memo
parent_plan: docs/plans/2026-05-07-sim-infra-0.md v1.1
inputs:
  - scratch/2026-05-08-sim-infra-research/RESEARCH.md (gsd-phase-researcher; Q1-Q4)
  - scratch/2026-05-08-sim-infra-research/MODULE_BOUNDARY_REVIEW.md (Backend Architect; D1-D4)
emit_timestamp_utc: 2026-05-08
purpose: Reconcile Phase 1 research outputs into authoritative input for Phase 2 Data Engineer dispatches
---

# Plan reconciliation — SIM-INFRA-0 Phase 1 → Phase 2 handoff

## §1 Agreement (no reconciliation needed)

Both research outputs converge on:

1. **M1 α-floor binds at sampler Callable, not Value type.** Plan §15.13 stands. `simulations/types/TruncParetoParams` accepts any $\alpha > 0$; `simulations/modules/TruncParetoSampler` raises typed `ValueError` on $\alpha < 1.5$ in `__post_init__`. Same pattern for M2 softplus β tightness.
2. **Three-tier directory split is correct as written.** Vertical split (`types/` / `modules/` / `utils/`) enforces tier-import discipline by directory boundary; stricter than horizontal co-location patterns. Plan §"File structure" stands.
3. **`Protocol` lives in `types/`** (Q2 + D1 agree). Cross-tier interfaces (e.g., `ParquetReader` consumed by `modules/`, implemented in `utils/`) declared as `Protocol` in `types/`.
4. **Hypothesis strategies live in `tests/strategies.py`**, not in `types/` — keeps `types/` framework-free (D1).
5. **Frozen-dataclass exclusively in `types/`** (Q3 + D1 + functional-python skill).
6. **Pre-mortem-flagged audit pattern**: edge-case rulings from D1 (parquet-row containers as Values; `tightness_l1_deviation` as free function; sha256 helper in `utils/`) are correct and consistent with M1–M5 plan pins.

## §2 Reconciliations (one rule chosen per disagreement)

### §2.1 Parquet row schemas — TypedDict location

- **Q3 says:** `simulations/types/`: frozen-dc exclusively, **no Pydantic, no TypedDict**. TypedDict for parquet row shapes lives at the IO boundary (`simulations/utils/`).
- **D1 says:** Parquet-row containers (`PosteriorDraws`, `CohortPriorRow`, `ZCapPinned`) are Values in `types/`.

**No actual disagreement** once disambiguated:
- **Value-tier *frozen-dc containers* live in `types/`.** Examples: `PosteriorDraws` (holds posterior arrays + parameter metadata), `ZCapPinned` (the emitted Value with CI bounds).
- **TypedDict *row schemas* for parquet column-level reads live in `utils/`.** Examples: `PosteriorDrawsRow: TypedDict` mirrors `synthetic_tau_t.parquet` columns; consumed by parquet reader at IO boundary; converted to `PosteriorDraws` Value before exiting the IO boundary.

Phase-2 instruction: `simulations/types/` contains frozen-dc Values; `simulations/utils/` contains TypedDict row schemas (one per parquet artifact) used by the reader to validate before converting to Values.

### §2.2 Pydantic placement

- **Q3 says:** Pydantic ONLY at JSON/parquet read boundary in `simulations/utils/`; one-shot `model_validate_json` then convert to frozen-dc.
- **D1 says:** [silent on Pydantic placement]
- **functional-python skill says:** [silent on Pydantic; allows it where `tighten-types` recommends]

**Decision (one rule):** Pydantic appears **only** in `simulations/utils/` JSON IO boundary helpers — used for `model_validate_json` then immediately converted to a frozen-dc Value before the IO boundary returns. Pydantic models are *transient* validation containers, never returned to consumers. Phase-2 Task 2.3 implementer follows this rule.

### §2.3 Hidden-coupling risk on TruncPareto (RC reverify FLAG)

RC v1.1 reverify flagged a latent risk: future iteration imports `simulations/types/TruncParetoParams` and constructs a non-canonical sampler bypassing the M1 floor. Combined with Q4 (PyMC `Truncated` pattern):

**Decision:** `simulations/types/TruncParetoParams` carries a docstring contract: *"This Value tier accepts any α > 0. The α-floor for the SaaS-builder cohort (α ≥ 1.5 per spec §8(6)) binds at the sampler Callable in `simulations/modules/`. Future iterations defining their own samplers MUST honor or override the floor explicitly per their cohort spec."* Phase-2 Task 2.1 implementer adds this docstring; Phase 4.1 Reality Checker verifies its presence.

### §2.4 Schema-version field on parquet artifacts (Q1 FLAG, not block)

Q1 recommends adding a `schema_version` field to Pin M4 schemas to support additive-only / append-at-end / nullable schema evolution.

**Decision:** Add `schema_version: str` (e.g., `"v1.0"`) as the **last column** of `cohort_prior.parquet` and `synthetic_tau_t.parquet`; add `schema_version` field to `Z_cap_pinned.json`. This is a Phase-2 Task 2.3 instruction (utils/ parquet writer). It does NOT modify spec §10 (which is the source of truth); the field is *additive*. If user wants spec §10 patched to v1.1.2, surface as separate decision. For SIM-INFRA-0 Phase 2, the writer emits the column / field; consumers ignore unknown values per the additive-only rule.

### §2.5 Parquet partitioning strategy

- **Q1 says:** Hive-partition on `tier_id` (cardinality 3) + `month` (cardinality ≈12-60). Do NOT partition on `simulation_id` (≥4000 → small-files anti-pattern).

**Decision:** Phase-2 Task 2.3 implementer's parquet writer in `simulations/utils/` writes to a Hive-partitioned tree at `simulations/saas_builder/data/synthetic_tau_t/tier_id=*/month=*/*.parquet`. `cohort_prior.parquet` is small enough to remain unpartitioned at `simulations/saas_builder/data/cohort_prior.parquet`.

### §2.6 PyMC TruncPareto pattern (Q4)

`TruncParetoParams` in `simulations/types/` needs only `(alpha, x_m, x_max)`. The PyMC consumption pattern (`pm.Truncated("name", pm.Pareto.dist(alpha=a, m=xm), lower=xm, upper=kappa)`) is downstream — SIM-INFRA-0 doesn't import PyMC; SAAS-COHORT-1 does. **No change to plan.** This pre-resolves a SAAS-COHORT-1 design question and is recorded here for forward-look.

### §2.7 Forward-look: `simulations/<iter>/types/` admitted now

D4 recommends admitting per-iteration `simulations/<iter>/types/` immediately, even though SaaS-builder has no per-iter types yet. Pair D iteration will use it.

**Decision:** SIM-INFRA-0 does NOT create `simulations/saas_builder/types/` (out of scope; SaaS-builder uses globals only). The pattern is documented in the global `simulations/README.md` (Phase 2 Task 2.1 instruction) so future iterations have a precedent without re-inventing it.

### §2.8 Extension without inheritance

D4 recommends three patterns for per-iteration extension of global Callables:
- **Wrap** (preferred): per-iter Callable holds the global Callable as a field.
- **Protocol-based polymorphism**: per-iter implements the same Protocol.
- **Higher-order constructors**: function returning a frozen-dc.

**Decision:** Document all three in `simulations/README.md` "Extension model" section (Phase 2 Task 2.1 instruction). Wrap is the default; the others are for cases where wrap doesn't fit. Phase 4.1 Reality Checker verifies no inheritance violations.

### §2.9 `__init__.py` re-export policy

- **D4 says:** Explicit `__all__ = [...]` per package; no star imports; no transitive re-exports.
- **functional-python skill says:** [silent on `__init__.py` policy]

**Decision (one rule):** Every `__init__.py` in `simulations/` declares an explicit `__all__: list[str]`. Cross-tier consumers fully-qualify imports (`from simulations.types.distributions import TruncParetoParams`). This makes Phase 4.1 Reality Checker's tier-import grep mechanically reliable — tier violations show up as direct submodule imports across tier boundaries, not hidden by star-import re-exports.

## §3 Disposition: dev_ai_cost precedent

D3 ruling stands as authoritative for SaaS-builder iteration design (consumed by SAAS-COHORT-1..4 plan authoring, not SIM-INFRA-0):

**Preserve from `notebooks/dev_ai_cost/`:**
- Notebook trio numbering (`01_data_eda.ipynb`, `02_estimation.ipynb`, `03_tests_and_sensitivity.ipynb`)
- `dispositions/` directory for HALT memos
- `references.bib` for citation provenance
- README gate-table-at-top format

**Discard:**
- `env.py` (pre-uv era; replaced by `.venv` activation)
- Ad-hoc `scripts/build_*.py` mixing transform+IO (replaced by clean `simulations/utils/` IO boundaries + per-iter `modules/` transforms)
- Unvalidated `estimates/` emission (replaced by typed Value containers + IO-boundary schema enforcement)

**Adapt:**
- ETL scripts factor into `simulations/utils/` (IO boundaries) + `simulations/<iter>/modules/` (transforms).
- Audit-block sha pinning helper (already in plan §"File structure") replaces ad-hoc README sha lines.

## §4 Net Phase-2 instructions to Data Engineer

The Phase 2 prelude (M1–M5 math pins) plus this reconciliation form the **authoritative input** for each Phase-2 task dispatch. Specifically, the Data Engineer reads this memo before authoring code, treating §2 decisions as binding.

The plan's Phase 2 task briefs (2.1, 2.2, 2.3, 2.4) are unchanged in scope; the implementer agent receives this memo as additional context per task.

End of reconciliation memo.
