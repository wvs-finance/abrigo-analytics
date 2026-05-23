# `simulations/utils/` — IO Boundary tier

Per the functional-python three-tier hierarchy
(`~/.claude/skills/functional-python/SKILL.md`):

> **IO Boundary**: Class with `__init__`. The ONLY place mutable state lives.
> Network clients, file handles, parquet writers, JSON readers.

## What lives here

| File | Class(es) / function(s) | Purpose | Math pin |
|------|------------------------|---------|----------|
| `errors.py` | `SchemaMismatchError` | Typed exception for M4 schema-drift on read | M4 |
| `parquet_io.py` | `CohortPriorReader/Writer`, `SyntheticTauReader/Writer`, `CohortPriorRow`/`SyntheticTauRow` (TypedDicts) | M4 parquet schemas verbatim; Hive-partitioned on `tier_id` + `month` per Phase 1 reconciliation §2.5 | M4 |
| `json_io.py` | `ZCapPinnedReader/Writer`, private `_ZCapPinnedJsonModel` | M4 `Z_cap_pinned.json` schema verbatim; transient Pydantic validator per §2.2 | M4 |
| `audit_block.py` | `compute_audit_block`, `AuditBlockHasher` | Deterministic sha256 over file contents (path-sorted); 64-hex output consumed by `ZCapPinned.audit_block` | — |
| `pricing_fetcher.py` | `StaticPricingFetcher` | Re-emits spec §5.2 frozen pricing pins as `CohortPriorRow` records (no live HTTP) | — |

## Tier rules (NON-NEGOTIABLE)

1. **Plain `class Foo:` with `__init__`** is the only construct admitted for
   IO classes. Do **not** use `@dataclass(frozen=True)` here.
2. **Pydantic** is allowed **only** in `json_io.py` as a transient validator
   (Phase 1 reconciliation §2.2). Pydantic models are `_`-prefixed (private)
   and never exported in `__all__`. They are constructed by
   `model_validate_json`, immediately converted to a frozen-dc Value from
   `simulations.types`, then discarded.
3. **TypedDict row schemas** (`CohortPriorRow`, `SyntheticTauRow`) live in
   `parquet_io.py` (Phase 1 reconciliation §2.1), not in `simulations.types`.
   They are consumed at the IO boundary for column-level validation before
   conversion to typed Value containers.
4. **Imports**: stdlib + numpy + pandas + pyarrow + pydantic + `simulations.types`.
   **No imports from `simulations.modules`** — the import graph is
   `types/ ← {modules/, utils/}`. `modules/` consumes `utils/` only via the
   Protocols declared in `simulations.types.protocols`.

## M4 schema summary (verbatim per spec §10 + reconciliation §2.4)

`cohort_prior.parquet` (unpartitioned):

```
param: str, percentile: str, value: float, source: str,
fetched_at_utc: str, schema_version: str
```

`synthetic_tau_t.parquet` (Hive-partitioned on `tier_id` + `month`):

```
month: int, simulation_id: int, tier_id: str,
r: float, p: float, alpha: float, x_m: float,
tau_t: float, q_t_usd: float, q_t_cop: float,
schema_version: str
```

`Z_cap_pinned.json`:

```json
{
  "Z_cop_per_month": <float>,
  "ci_95_lo": <float>,
  "ci_95_hi": <float>,
  "audit_block": "<64-hex sha256>",
  "tier_mix": {"pro": <float>, "max_5x": <float>, "max_20x": <float>},
  "schema_version": "v1.0"
}
```

Default emission paths (relative to repo root):

- `simulations/saas_builder/data/cohort_prior.parquet`
- `simulations/saas_builder/data/synthetic_tau_t/tier_id=*/month=*/*.parquet`
- `simulations/saas_builder/estimates/cohort_4/Z_cap_pinned.json`

## Schema-drift behavior

Readers raise `SchemaMismatchError` (subclass of `ValueError`) when the
on-disk artifact's column / field set does not match the M4 declaration.
The exception names exactly which columns are missing and which are extra
so a Phase-4 reality-checker grep can mechanically locate the boundary.
