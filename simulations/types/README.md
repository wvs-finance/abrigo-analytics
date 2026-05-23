# `simulations/types/` — Value tier

Frozen-dataclass parameter containers, structural Protocols, TypeAliases,
and Final constants for every Value-tier row in spec
`docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1 §6.

## Hard rules (per functional-python skill + Phase 1 reconciliation)

1. Every dataclass is `@dataclass(frozen=True)`. No exceptions.
2. `__post_init__` is **validation-only**. It raises `ValueError` on bad
   input. No state mutation, no side effects.
3. **No methods other than `__post_init__`.** Accessors are FREE FUNCTIONS
   in the same file (e.g., `def percentile_50(p: CohortPrior) -> float`).
4. Inheritance is forbidden except `typing.Protocol` (used for cross-tier
   structural interfaces consumed by `modules/` or `utils/`).
5. Imports allowed: stdlib + `numpy` + `typing` / `typing_extensions` only.
6. **NO Pydantic.** Pydantic appears transiently in `utils/` only.
7. **NO TypedDict.** Parquet row schemas (TypedDict) live in `utils/`.
8. **NO Hypothesis strategies.** Strategies live in `tests/strategies.py`.
9. No imports from `simulations.modules` or `simulations.utils`. This is
   the upstream-most tier.
10. All module-level constants annotated `Final`.
11. All repeated compound types (≥2 occurrences) get a `TypeAlias`.
12. `Literal[...]` over string enums (e.g. `Literal["pro", "max_5x", ...]`).
13. No bare `Any` in signatures. Use `TypeVar` or a concrete Protocol.
14. Use `X | None` (Python 3.13), never `Optional[X]`.

## File decomposition

| File | Theme | Spec §6 rows covered |
|------|-------|----------------------|
| `tier.py` | Tier identity + Categorical/Dirichlet prior + tier pricing | `tier_id`, `bar_p_sub` |
| `distributions.py` | TruncPareto, NegBin, Softplus parameter Values | `tau_{j,i}`, `N_j`, `q_t^{sticky}` (params) |
| `fx.py` | FX path + variance proxy parameters | `(X/Y)_t`, `sigma_T`, blended `p_t` parameters |
| `posterior.py` | Posterior draw containers + monthly CDF + Z-cap pin | PyMC outputs, §10 emission Values |
| `protocols.py` | Cross-tier structural Protocols (parquet reader / writer interfaces) | n/a — declared here, implemented in `utils/` |

## What does NOT live here

- Hypothesis strategies → `tests/strategies.py`.
- TypedDict parquet row schemas → `utils/` (one per parquet artifact).
- Pydantic models → `utils/` (transient JSON validation only).
- Sampler logic → `modules/`.
- The α ≥ 1.5 floor enforcement → `modules/` (sampler Callable). The Value
  type accepts any α > 0; see the `TruncParetoParams` docstring contract
  per Phase 1 reconciliation §2.3.
- The softplus β-tightness criterion enforcement → `modules/`. The free
  function `tightness_l1_deviation(SoftplusParams) -> float` is the
  computational primitive offered here.

## Public API

The `__init__.py` re-exports a curated set in `__all__`. Cross-tier
consumers should import directly from submodules
(`from simulations.types.distributions import TruncParetoParams`).
