# MODULE_BOUNDARY_REVIEW — SIM-INFRA-0 v1.1

Reviewer: Backend Architect (dispatched by foreground; Phase 1 Task 1.2)
Spec: `2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1 §6, §10
Plan: `2026-05-07-sim-infra-0.md` v1.1 (Phase 2 prelude + 2.1–2.4)
Skill: `~/.claude/skills/functional-python/SKILL.md`

---

## D1. Per-tier inclusion criteria

The plan's three-tier split (`types/` Value, `modules/` Callable, `utils/` IO Boundary) maps cleanly to the skill's three-tier table. Edge cases require explicit rules.

### Value tier (`simulations/types/`) — inclusion criteria
A `.py` file belongs here iff every public symbol satisfies all of:
1. `@dataclass(frozen=True)` with `__post_init__` for *validation only* (raises on invalid input; does not compute or transform).
2. No `__call__`, no methods other than `__post_init__`. Accessors are free functions in the same module operating on the dataclass.
3. Imports limited to `typing`, `dataclasses`, stdlib, `numpy.typing` (for shape aliases). No imports from `simulations.modules` or `simulations.utils`.
4. `TypeAlias` declarations and `Final` constants live here when they describe *domain shape*, not behavior.
5. Pure `Protocol` definitions live here when they type a contract consumed by `modules/`.

### Callable tier (`simulations/modules/`) — inclusion criteria
1. `@dataclass(frozen=True)` with `__call__` as the single public method. Configuration in fields; logic in `__call__`.
2. May import from `simulations.types` only.
3. Stateless across calls (no field is mutated; RNG seeds are fields, not module globals).
4. Construction-time validation (e.g., M1 α-floor) raises typed errors *in `__post_init__`*, not in `__call__`.

### IO Boundary tier (`simulations/utils/`) — inclusion criteria
1. `class Foo: def __init__` permitted; mutable state confined here.
2. Touches the filesystem, network, RNG-as-process-global, or external libraries with side effects (parquet writers, JSON, sha256 over filepaths).
3. May import from `simulations.types` only — never `simulations.modules`.
4. Read paths must validate against typed Value objects (Pin M4); never returns `dict[str, Any]` to callers.

### Edge cases and resolution

- **`PosteriorDraws` (parquet-row container).** This is a *Value* — frozen dataclass mirroring the `synthetic_tau_t.parquet` row schema (M4). The *parquet writer* is in `utils/`; the row-shaped record is in `types/`. Reject `TypedDict` here: it weakens runtime validation that `__post_init__` provides and the plan's M4 audit relies on.
- **`MonthlyCDF`.** Value (frozen-dc holding sorted support + cumulative weights). The *sampler* that draws from it is a Callable in `modules/`.
- **Audit-block sha256 helper.** Plan §2.3 places it in `utils/` because it touches the filesystem (reads file bytes). Correct: the I/O is what binds the tier, not purity. Document this exception in `utils/README.md`.
- **`SoftplusParams.tightness_l1_deviation()`.** The plan permits "method or free function". Pick **free function** in the same module; the skill rule "free functions over methods" is unambiguous when `self` is read-only. The Callable in `modules/` calls this free function for its M2 refusal predicate.
- **Hypothesis strategies.** Live in `simulations/tests/strategies.py`, not in `types/`. Strategies depend on `hypothesis`; `types/` must stay framework-free so cohort plans can import without a test dep.
- **`Protocol` definitions.** Live in `types/` even though they describe Callable interfaces — they are pure shape, no runtime behavior.

---

## D2. Spec §6 row → tier assignment

| Spec §6 row | `types/` (Value) | `modules/` (Callable) | `utils/` (IO) | Notes |
|---|---|---|---|---|
| $a_s^{(T)}$ universal | `AsConfig` (params) | `AsClosedForm.__call__` | — | Free fn allowed if no config; promote to Callable when params accumulate |
| $\Upsilon_t$ martingale primary | `UpsilonParams` | `MartingaleUpsilon.__call__` | — | AR(1)-log + det+churn arms = sibling Callables, not subclasses |
| `tier_id` Categorical | `TierId = Literal["Pro","Max5x","Max20x"]` + `TierPrior` (π, Dirichlet α₀) | `TierSampler.__call__` | — | `Literal` in `types/`, sampler in `modules/` |
| $\bar p_{\text{sub}}$ discrete RV | `SubPriceTable` (frozen mapping `tier_id → price`) | `SubPriceLookup.__call__` | — | Lookup is Callable for composition |
| $q_t^{\text{sticky}}$ softplus | `SoftplusParams` (β, κ + `tightness_l1_deviation` free fn) | `SoftplusRegularizer.__call__` (M2 refusal in `__post_init__`) | — | Tightness predicate is free function, not method |
| $N_j$ NegBin | `NegBinParams` (r>0, 0<p<1) | `NegBinSampler.__call__` | — | Standard pattern |
| $\tau_{j,i}$ TruncPareto | `TruncParetoParams` (α>0 open per §15.13) | `TruncParetoSampler.__call__` (M1 floor α≥1.5 in `__post_init__`) | — | Floor binds at sampler boundary, not type |
| $p_t$ blended | — | `BlendedPriceFn.__call__` (M3 verbatim formula; dimensional-analysis return type) | — | Pure transform; no params type needed beyond inputs |
| $(X/Y)_t$ deterministic | `FXPathParams` ($\overline{X/Y}$, ε∈(0,1), ω) | `FXPathFn.__call__` (M5 verbatim; cites PRIMITIVES (6),(8)) | — | ε bound enforced in `__post_init__` of params |
| $\sigma_T$ realized variance | — | `RealizedVariance.__call__` | — | Free Callable on series |
| $\pi(t)$ streamed premium | `PremiumScheduleParams` | `PremiumStream.__call__` | — | Streaming = lazy generator inside `__call__` |
| Parquet IO `cohort_prior`, `synthetic_tau_t` | `CohortPriorRow`, `PosteriorDraws` (row Values) | — | `ParquetIO.read/write` (class) | M4 schemas verbatim |
| JSON IO `Z_cap_pinned` | `ZCapPinned` (Value) | — | `JsonIO` (class) | M4 schema verbatim |
| Audit-block sha pinning | — | — | `AuditBlockHasher` (class) | Filesystem touch ⇒ utils/ |

---

## D3. `notebooks/dev_ai_cost/` precedent — preserve / discard / adapt

Layout there: flat per-iteration notebook trio (`01_data_eda`, `02_estimation`, `03_tests_and_sensitivity`) + `data/`, `scripts/build_*.py`, `estimates/`, `figures/`, `dispositions/`, `references.bib`, `README.md`, `env.py`.

**Preserve** (port into `simulations/saas_builder/`):
- Notebook trio numbering convention (`01_*`, `02_*`, `03_*`) — discoverable, audit-friendly.
- `dispositions/` subdir for HALT memos.
- `references.bib` per iteration.
- `README.md` with gate-verdict table at top — anchor for future readers.
- `data/` subdir for iteration-specific parquet panels (separate from global Tier-1/2/3 data fetched by `make data`).
- `_nbconvert_template/` and `pdf/` for headless rendering.

**Discard:**
- Inlined `scripts/build_*.py` mixing transforms with I/O (violates three-tier; this is exactly what `simulations/types|modules|utils` factors out).
- `env.py` module-global state — superseded by `simulations.utils` IO classes.
- Ad-hoc `estimates/` parquet emission without column-schema validation — superseded by Pin M4 enforcement.

**Adapt:**
- `dev_ai_cost` ETL scripts become `simulations/utils/` IO classes + `simulations/saas_builder/modules/` transforms; notebooks reduce to thin orchestration.
- Per-iteration `data/` stays, but parquet schemas validated by `simulations/utils/ParquetIO` on read/write.

The new layout strictly improves reuse: Pair D's TruncPareto sampler, future dev-AI's NegBin, and SaaS-builder's softplus all share `simulations/types/` + `simulations/modules/` rather than each iteration re-implementing.

---

## D4. Forward-look — `simulations/<iteration>/` peer extension

### Global vs per-iteration `types/`

**Rule.** `simulations/types/` holds Values that are *form-specific, not population-specific* — `TruncParetoParams`, `NegBinParams`, `SoftplusParams`, `FXPathParams`, generic row-Values whose schema is fixed across iterations. Per-iteration `simulations/<iter>/types/` (admit it now; SaaS-builder does not need it but Pair D will) holds Values that encode *cohort-specific composites* — e.g., `SaasBuilderCohortMix` (Pro/Max5x/Max20x π weights with Dirichlet α₀ from spec §5), `PairDOffshoringWindow`. The discriminator: if two iterations would write the same fields, it's global; if the field set is a population-specific composite, it's per-iteration.

### Extending Callables without inheritance

functional-python BANS `class Foo(Bar)`. Three composition mechanisms, ranked:

1. **Wrapping (preferred).** `simulations/saas_builder/modules/saas_trunc_pareto.py` defines `SaasTruncParetoSampler` — a frozen-dc holding a `TruncParetoSampler` field plus the saas-specific α-floor (§8(6) commits to ≥1.5; another cohort might commit to ≥1.8). `__call__` validates then delegates. Zero inheritance; explicit dependency.
2. **Protocol-based polymorphism.** `simulations/types/protocols.py` defines `class Sampler(Protocol)` with `__call__` signature. Both global and per-iteration Callables satisfy it structurally. Cohort plans that consume "any sampler" type-annotate against the Protocol.
3. **Higher-order construction.** `simulations/modules/samplers.py::make_trunc_pareto(alpha_floor: float) -> TruncParetoSampler` — closure over the floor. Use sparingly: harder to introspect than wrapping.

Avoid mixin-style "extend by subclass" entirely. Pin M1 §15.13 already separates "type accepts α>0" from "this cohort's sampler refuses α<1.5" — wrapping is the natural fit.

### `__init__.py` re-export policy

**One rule: explicit `__all__ = [...]` per package; no star imports; no transitive re-exports.**

Rationale:
- **Discoverability.** `from simulations.types import TruncParetoParams` resolves via the `__all__` list at `simulations/types/__init__.py`; tooling (`ty`, `ruff`, IDE) sees the public surface explicitly.
- **No surprise.** Star re-exports promote private symbols accidentally; transitive re-exports (e.g., `from simulations import TruncParetoParams`) create ambiguity about which package owns the type — fatal for the audit-pass chain (Reality Checker greps `from simulations.types import` to verify tier discipline; transitive re-exports bypass that grep).
- **Audit anchor.** Plan §4.1 step 7 ("tier-import discipline: types/ ↛ modules/utils") is mechanical only when imports are fully package-qualified.

Rejected alternatives: star-import (loses tier-grep audit), no re-export / fully-qualified-only (verbose; pushes domain Values behind 4-segment paths). `__all__` is the Goldilocks choice.

---

## Summary recommendations to Phase 2 dispatchers

1. Place row-shaped parquet Values (`PosteriorDraws`, `CohortPriorRow`, `ZCapPinned`) in `types/`; readers/writers in `utils/`.
2. `tightness_l1_deviation` is a free function, not a method.
3. Permit `simulations/<iter>/types/` now (currently unused; Pair D will need it).
4. Extension mechanism for cohort-specific Callables: wrap, don't subclass; Protocol for "any sampler" annotations.
5. `__init__.py` policy: explicit `__all__`, no star, no transitive re-export.
6. Preserve dev_ai_cost's notebook trio numbering, `dispositions/`, `references.bib`, gate-table-at-top README; discard `env.py` and unvalidated-schema `estimates/`.

End MODULE_BOUNDARY_REVIEW.
