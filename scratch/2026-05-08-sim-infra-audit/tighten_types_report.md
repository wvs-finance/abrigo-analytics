# tighten-types audit — `simulations/`

**Date:** 2026-05-08
**Scope:** `simulations/{types,modules,utils,tests}/` (all `.py`)
**Branch:** `iter/saas-builder-stage-2` (HEAD `1f3726b` → patched in this pass)
**Phase:** SIM-INFRA-0 Phase 3 Task 3.1

## Summary

| Metric                        | Count |
| ----------------------------- | ----- |
| Files audited                 | 19    |
| Issues identified             | 5     |
| Fixes applied                 | 5     |
| Recommendations deferred      | 0     |
| Recommendations rejected (rule violations) | 0 |

Baseline already strong from Phase 2 reviews (I1–I5 + N1). The audit surfaced
ZERO weak-typing pathologies on the seven dimensions enumerated by the
`tighten-types` skill except for one consistent pattern: **IO-Boundary
classes initialized attribute types in the `__init__` body rather than at the
class scope.** This was lifted to class-body annotations for all five
stateful IO classes.

## Audit checklist results

### 1. Bare `Any` in signatures

**Result:** ZERO occurrences across `types/`, `modules/`, `utils/`. Verified.
The only `Any` usages are in `simulations/tests/test_types.py` and
`simulations/tests/test_utils.py` inside `cast(Any, ...)` calls used to
deliberately bypass type-checker for negative-path test coverage (verifying
runtime `TypeError` from `__post_init__`); these are correct test idiom and
left in place.

### 2. Loose `dict[str, X]` that should be Pydantic / TypedDict / frozen-dc

**Result:** ZERO weak dicts. Inventory:

- `simulations/utils/parquet_io.py` already uses `CohortPriorRow` and
  `SyntheticTauRow` `TypedDict`s per reconciliation §2.1 (constraint
  honored — TypedDict scoped to `parquet_io.py` only).
- `simulations/utils/json_io.py:117` `payload: dict[str, object]` — transient
  serialization payload immediately fed to `json.dumps`. Per skill guidance
  ("TypedDict when never validated/serialized") this *is* serialized, but
  it's a one-shot writer-side construction with no consumer ever destructuring
  it; converting to a TypedDict adds zero typecheck strength. **No change.**
- `simulations/types/posterior.py` `tier_mix: Mapping[TierID, float]` already
  uses the Literal `TierID` for keys — strongest possible.

**Project rule honored:** No Pydantic introduction in `types/` or `modules/`.

### 3. Missing `@overload` for narrowable unions

**Result:** ZERO candidates. Reviewed:

- `CohortPriorReader.__call__(path: str | Path | None = None) -> list[...]`
  — return type does not vary with input; no overload value.
- `compute_audit_block(file_paths: Sequence[str | Path]) -> str` — return
  is always `str`.
- `epsilon_from_sigma_T(sigma_T: float, mean_x_over_y: float) -> float` —
  monomorphic.
- All `__call__` methods on Callable-tier frozen-dcs have stable signatures.

### 4. Redundant in-body type annotations

**Result:** Reviewed, none qualify for removal under the skill's rule
("Do not remove annotations on initial declarations"). Conventional
local-variable initializations like `coerced: list[Path] = [...]` and
`payload: dict[str, object] = {...}` are kept.

### 5. Missing return annotations

**Result:** ZERO. Every function and method carries an explicit return
annotation, including `-> None` on `__init__` / `__post_init__`.

### 6. Generic `T` without `bound=`

**Result:** No user-defined `TypeVar`s in scope. Not applicable.

### 7. Class attribute annotations missing at class scope

**Result:** 5 occurrences — **fixed**. See per-file findings below.

## Per-file findings

### `simulations/types/distributions.py`
Clean. No changes.

### `simulations/types/fx.py`
Clean. No changes.

### `simulations/types/posterior.py`
Clean. `Mapping` import from `typing` retained (annotation use) alongside
`MappingABC` (isinstance use) — intentional disambiguation.

### `simulations/types/protocols.py`
Clean. All four Protocols correctly use `runtime_checkable`.

### `simulations/types/tier.py`
Clean.

### `simulations/types/__init__.py`
Clean.

### `simulations/modules/fx_path.py`
Clean. `FXPathGen.params: FXPathParams` etc. live in the frozen-dc body —
canonical form.

### `simulations/modules/pricing.py`
Clean.

### `simulations/modules/regularizers.py`
Clean.

### `simulations/modules/samplers.py`
Clean. `TierMixCategorical` correctly typed `NDArray[np.str_]`.

### `simulations/modules/__init__.py`
Clean.

### `simulations/utils/audit_block.py`
- **Line 74–77** `AuditBlockHasher.__init__` — stateless (no fields). No
  class-body annotation needed. Clean.

### `simulations/utils/errors.py`
Clean (typed `Exception` subclass).

### `simulations/utils/json_io.py`
- **Line 72–73, 111–112** `ZCapPinnedReader/Writer.__init__` — stateless.
  Clean.
- **Line 117** `payload: dict[str, object]` — initial local declaration;
  per skill rule kept as-is.

### `simulations/utils/parquet_io.py`
- **Line 167 (was)** `CohortPriorWriter.__init__`: in-body
  `self._base_dir: Path = ...` → **lifted** to class-scope `_base_dir: Path`
  declaration. Fix applied.
- **Line 189 (was)** `CohortPriorReader.__init__`: same pattern. **Fixed.**
- **Line 235 (was)** `SyntheticTauWriter.__init__`: same pattern. **Fixed.**
- **Line 267 (was)** `SyntheticTauReader.__init__`: same pattern. **Fixed.**
- TypedDicts `CohortPriorRow` / `SyntheticTauRow` already canonical.

### `simulations/utils/pricing_fetcher.py`
- **Line 45–50 (was)** `StaticPricingFetcher.__init__`: in-body
  `self._fetched_at_utc: str = ...` → **lifted** to class-scope
  `_fetched_at_utc: str`. Fix applied.

### `simulations/utils/__init__.py`
Clean.

### `simulations/tests/strategies.py`
Clean. All composites typed and return `dict[TierID, float]` with the
Literal narrowing.

### `simulations/tests/test_modules.py`, `test_types.py`, `test_utils.py`
Clean. `Any` only inside `cast(Any, ...)` for negative-path tests
(deliberate type-checker bypass to verify runtime guards).

## Fixes applied (5 total)

All five fixes follow the same pattern: lift `self._foo: T = ...` from
`__init__` body to class-scope `_foo: T` declaration, dropping the redundant
in-body annotation.

| File                                | Class                  |
| ----------------------------------- | ---------------------- |
| `simulations/utils/parquet_io.py`   | `CohortPriorWriter`    |
| `simulations/utils/parquet_io.py`   | `CohortPriorReader`    |
| `simulations/utils/parquet_io.py`   | `SyntheticTauWriter`   |
| `simulations/utils/parquet_io.py`   | `SyntheticTauReader`   |
| `simulations/utils/pricing_fetcher.py` | `StaticPricingFetcher` |

## Project-specific constraints honored

- ✅ **No Pydantic added to `types/` or `modules/`** (reconciliation §2.2).
  Pydantic remains scoped to `simulations/utils/json_io.py` as the transient
  `_ZCapPinnedJsonModel` validator.
- ✅ **No inheritance added** apart from existing `Protocol` (`protocols.py`)
  and `Exception` (`errors.py:SchemaMismatchError`).
- ✅ **`TypedDict` only in `simulations/utils/parquet_io.py`** (reconciliation
  §2.1). `CohortPriorRow` and `SyntheticTauRow` unchanged.
- ✅ **`Final` for module-level constants** preserved.
- ✅ **`numpy.typing.NDArray` for array signatures** verified consistent.

## Verification

```
$ ruff check simulations/
All checks passed!

$ ty check simulations/
All checks passed!

$ pytest simulations/tests/
177 passed in 1.52s
```

No regressions. Type tightening complete.
