# `simulations/modules/` — Callable tier

Stateless **Callable** transforms per the functional-python three-tier
hierarchy (see `~/.claude/skills/functional-python/SKILL.md`):

> `@dataclass(frozen=True)` + `__call__`. Configurable stateless transforms.
> Config in fields, logic in `__call__`. One per pipeline stage.

## What lives here

Transforms enumerated in spec v1.1.1 §6 (functional-form table) and Phase 2
of the SIM-INFRA-0 plan, organized by theme:

| File | Callable(s) | Math pin |
|------|-------------|----------|
| `fx_path.py` | `FXPathGen`, `RealizedVarianceCalc`, free `epsilon_from_sigma_T` | M5 (PRIMITIVES.md (6)/(7)/(8)) |
| `samplers.py` | `TruncParetoSampler`, `NegBinSampler`, `TierMixCategorical` | M1 (spec §8(6) α ≥ 1.5) |
| `regularizers.py` | `SoftplusRegularizer` | M2 (spec §5.1 (T2) tightness) |
| `pricing.py` | `BlendedPriceFn` | M3 (spec §5.1 verbatim) |

## What does NOT live here

- **Value types** (frozen-dc parameter containers, Protocols, TypeAliases,
  `Final` constants, free pure accessors) live in `simulations/types/`.
- **IO boundaries** (filesystem, network, parquet readers/writers) live in
  `simulations/utils/`. Callables here MUST NOT import from `utils`.

## Universal contracts

1. Every public class is `@dataclass(frozen=True)` with a `__call__` method.
2. `__post_init__` is validation-only (raises typed exceptions); no mutation.
3. Imports come from `simulations.types` only. No `simulations.utils` imports.
4. Sibling Callables are not imported at construction time. Composition flows
   through *values* (e.g. `RealizedVarianceCalc(path)` consumes the array
   produced by `FXPathGen(t)`, not an `FXPathGen` instance).
5. `np.random.Generator` is passed in via `__call__` keyword arguments. Never
   construct generators inside transforms.
6. No bare `Any` in signatures. `numpy.typing.NDArray` for array typing.

## Pin enforcement summary

| Pin | Where | Trigger |
|-----|-------|---------|
| M1 | `TruncParetoSampler.__post_init__` | `params.alpha < 1.5` raises `ValueError` |
| M2 | `SoftplusRegularizer.__post_init__` | `tightness_l1_deviation ≥ 1e-3 · κ` raises `ValueError` |
| M3 | `BlendedPriceFn.__call__` formula | Sonnet defaults → ≈ $7.15/MTok |
| M5 | `FXPathGen` docstring + `epsilon_from_sigma_T` | Cite PRIMITIVES.md (6) and (8) verbatim |
