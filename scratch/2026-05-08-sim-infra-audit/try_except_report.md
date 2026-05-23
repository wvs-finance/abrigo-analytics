# try-except Audit Report — `simulations/`

**Phase**: SIM-INFRA-0 Phase 3 Task 3.4
**Branch**: `iter/saas-builder-stage-2`
**HEAD before audit**: `bc3825e`
**Skill applied**: `try-except` (audit overly broad scope, by-catch risk,
catches of built-in exceptions that should be conditional checks)
**Date**: 2026-05-08

---

## Scope

Audited every `try:` block under `simulations/` (excluding `__pycache__`).
Tier discipline reminder enforced:

- `simulations/utils/` — IO Boundary tier; non-trivial `try/except` permitted
  here.
- `simulations/types/` — frozen-dataclass + free-function tier; only
  `__post_init__` validation `raise` permitted (no `try/except` wrapping
  validators).
- `simulations/modules/` — pure-function tier; no `try/except`.

## Inventory

`grep -rn "try:" simulations/ --include="*.py"` (excluding caches) returns
**2 blocks total**, both in `simulations/types/posterior.py`:

| # | File                              | Line  | Function                  |
|---|-----------------------------------|-------|---------------------------|
| 1 | `simulations/types/posterior.py`  | 275   | `parameter_index`         |
| 2 | `simulations/types/posterior.py`  | 297   | `cdf_percentile_value`    |

`simulations/utils/`, `simulations/modules/`, and `simulations/tests/` contain
**zero** `try/except` blocks. The IO-boundary tier (`utils/`) currently
implements all error handling via **validate-then-raise** (typed
`SchemaMismatchError`, `FileNotFoundError`, `ValueError`) with no need for
exception capture — the schema validators are pre-condition checks against
local state, so conditional checks are correctly preferred over `try/except`.

## Per-block analysis

### Block 1 — `parameter_index` (posterior.py:275-281)

```python
try:
    return draws.param_names.index(name)
except ValueError as exc:
    raise ValueError(
        f"PosteriorDraws has no parameter named {name!r};"
        f" available: {draws.param_names}"
    ) from exc
```

**Skill checklist:**

1. **Right mechanism?** YES. `tuple.index(name)` raises `ValueError` as part
   of its **documented API** when `name` is absent — this is the
   "validation as parsing" pattern (analogous to `int(s)`, `json.loads`,
   `datetime.strptime`). There is no cheaper precondition check than the
   lookup itself; `name in draws.param_names` would be O(n) and then
   `.index()` is O(n) again — and in the cold path the precondition check
   would still need to raise the same translated error.
2. **Minimally scoped?** YES. The `try` body contains a single expression
   (`return draws.param_names.index(name)`). Zero by-catch surface area.
3. **Except clause too broad?** NO. Catches the exact specific `ValueError`
   that `tuple.index` is documented to raise. Not `Exception`, not
   bare `except`.
4. **Handler masks failure?** NO. Re-raises a more informative `ValueError`
   with `from exc` chaining, preserving the original traceback.
5. **Nested?** NO.

**Constraint check (from task brief):** This is NOT a `__post_init__`
validator wrapping — it is a free-function accessor that **translates** an
opaque stdlib error into a contextful one at the type-API boundary. The
constraint forbids wrapping `__post_init__` validators in `try/except`; that
prohibition does not apply here. The `__post_init__` block in
`PosteriorDraws` (lines around 200-251) raises typed `ValueError` /
`TypeError` directly with **no** `try/except` — compliant.

**Action:** **KEEP AS-IS.** No narrowing, no replacement, no removal.

---

### Block 2 — `cdf_percentile_value` (posterior.py:297-303)

```python
try:
    idx = cdf.percentiles.index(percentile)
except ValueError as exc:
    raise ValueError(
        f"MonthlyCDF has no pinned percentile {percentile!r};"
        f" available: {cdf.percentiles}"
    ) from exc
return cdf.values_usd[idx]
```

**Skill checklist:**

1. **Right mechanism?** YES. Same `tuple.index` translate-and-rethrow
   pattern.
2. **Minimally scoped?** YES. `try` body is a single assignment from one
   expression. The post-block `return cdf.values_usd[idx]` correctly lives
   **outside** the `try` (using `idx` only after successful lookup). Could
   alternatively be expressed as an `else:` clause, but the current shape
   is equally tight and idiomatic — no by-catch reachable from the trailing
   return because `IndexError` from `values_usd[idx]` is a different type
   that is not caught.
3. **Except clause too broad?** NO. Specific `ValueError` only.
4. **Handler masks failure?** NO. Re-raises with chained context.
5. **Nested?** NO.

**Action:** **KEEP AS-IS.**

---

## Hidden-bug risk

Neither block is hiding upstream bugs:

- The `try` body in each is a single `tuple.index()` call against a frozen
  `tuple[str, ...]` / `tuple[float, ...]` field. There is no callee depth
  where an unrelated `ValueError` could surface — `tuple.index` never calls
  user code.
- The handlers re-raise (do not swallow), so any future drift would surface,
  not silently default.

## Tier-discipline verdict

| Tier                        | try/except count | Compliant?       |
|-----------------------------|------------------|------------------|
| `simulations/utils/`        | 0                | YES (validate-then-raise pattern) |
| `simulations/types/`        | 2                | YES (translate-and-rethrow at API boundary; no validator-wrapping) |
| `simulations/modules/`      | 0                | YES              |
| `simulations/tests/`        | 0                | YES              |

The CLAUDE-style constraint ("`__post_init__` validators raise typed
`ValueError`/`TypeError` — these should NOT live inside `try/except`") was
already satisfied at HEAD `bc3825e`. The skill produced no recommendations
that would violate it; nothing to reject.

## Counts

| Action      | Count |
|-------------|-------|
| Audited     | 2     |
| Narrowed    | 0     |
| Replaced (specific exception) | 0 |
| Removed (by-catch / unneeded) | 0 |
| Deferred    | 0     |

All 2 blocks pass the skill checklist on every criterion. No code edits made.

## Verification

```
$ ruff check simulations/
All checks passed!

$ python -m pytest simulations/tests/ -q
1 failed, 185 passed in 1.82s
```

The 1 failure is `TestNegBinSamplerProperty::test_negbin_sampler_distributional_validity`
— a Hypothesis-driven distributional tolerance flake on extreme NegBin
parameters `(r=0.0625, p=0.001)` introduced in Phase 3.3
(`bc3825e audit(sim-infra-0): hypothesis-tests pass`). It is **pre-existing
on HEAD prior to this audit** and entirely unrelated to exception handling.
Out of scope for Task 3.4. The `try-except` audit produced **zero
regressions** because it produced **zero edits**.

## Conclusion

`simulations/` is already disciplined on `try/except`:
- 2 blocks total, both legitimate translate-and-rethrow at the type-layer
  free-function API.
- No `except Exception:` anywhere, no bare `except:`, no by-catch, no
  KeyError/AttributeError/IndexError/TypeError suppression.
- Tier separation holds: utils handles errors via explicit validators;
  modules and tests have none.

No code changes warranted by this audit.
