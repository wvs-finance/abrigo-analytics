# SIM-INFRA-0 Pre-Implementation Research

**Date:** 2026-05-08
**Plan:** `docs/plans/2026-05-07-sim-infra-0.md` v1.1
**Spec:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1
**Word target:** ≤1500 words

---

## TL;DR (≤200 words)

**Q1 Parquet schema.** Use Hive-style partitioning on `tier_id` (small fixed cardinality, 3 values) + optional `month` (time partition) for `synthetic_tau_t.parquet`; **do not** partition on `simulation_id` (high cardinality → small-files anti-pattern). Schema evolution is *additive-only*: append nullable columns at the end, never mutate existing column types. PyArrow's `ParquetDataset(use_legacy_dataset=False).schema` validation is the canonical mismatch-detection point — wrap it in our `SchemaMismatchError` per Pin M4. snake_case is universal; `Literal["pro","max5x","max20x"]` Value-tier types map to plain `string` in parquet (TypedDict at the row level).

**Q2 Three-tier separation.** `returns` library and Pydantic-v2 internals confirm: container types and their transforms co-located by *effect type*, with `Protocol` for cross-tier interfaces. Plan v1.1 already enforces this; no changes recommended.

**Q3 Pydantic-vs-frozen-dc.** TypedDict for parquet rows (~2.5× faster than nested BaseModel; row-shaped no invariants). Frozen-dc for `simulations/types/` (validated once at construction, no hot-path cost). Pydantic only at `simulations/utils/` IO read boundary (one-shot validation of external parquet/JSON).

**Q4 PyMC TruncPareto.** **Not native.** Canonical pattern: `pm.Truncated("name", pm.Pareto.dist(alpha=a, m=xm), lower=xm, upper=kappa)`. PyMC's `Pareto` has `logcdf`; `pm.Truncated` uses inverse-CDF sampling automatically. **No extra fields needed on `TruncParetoParams`** — just `(alpha, x_m, x_max)`.

---

## Q1. Parquet schema patterns for synthetic-Bayesian outputs

### Column naming
Universal convention is `snake_case`. PyArrow round-trips column names verbatim; pandas reserves the `__index_level_*__` prefix. Spec §10's columns (`month`, `simulation_id`, `tier_id`, `r`, `p`, `alpha`, `x_m`, `tau_t`, `q_t_usd`, `q_t_cop`) already conform.

For `Literal`-typed columns like `tier_id ∈ {"pro","max5x","max20x"}`: store as `string` (or pyarrow `dictionary<int32,string>` for compression — recommended at our cardinality of 3). Validate the literal *only at the IO boundary* (utils/), not in the parquet schema itself; parquet has no enum primitive.

### Partitioning strategy for `synthetic_tau_t.parquet`
The artifact's three-axis structure is `month × simulation_id × tier_id`. Apache Arrow guidance [arrow-docs] is **partition on real filters, not on every column**. Per [datacamp-parquet] and [designandexecute]:

| Axis | Cardinality | Partition? | Reason |
|---|---|---|---|
| `tier_id` | 3 | **Yes** (top-level) | Small, query-aligned (cohort 1/2/3/4 will filter by tier) |
| `month` | ≤ 12 (rolling window per spec §2) | **Yes** (second level) | Time-series filters frequent; small-files risk negligible |
| `simulation_id` | ≥ 4000 (spec §8(8) sim-count floor) | **No** | High cardinality → small-files anti-pattern; keep as a row column |

Hive-style on-disk layout: `synthetic_tau_t.parquet/tier_id=max5x/month=2026-05/data.parquet`. Use `pyarrow.parquet.write_to_dataset(table, root_path, partition_cols=["tier_id","month"])` [arrow-write].

### Schema evolution
**Rule: additive-only, append-at-end, nullable.** When SAAS-COHORT-N adds a column (e.g., a future `q_t_commit` for §6 ratchet row), it appends to the existing schema; old readers ignore unknown columns; new readers tolerate `null` for old rows [parquet-evolution, designandexecute]. **Never** mutate types in place; create a new column and deprecate.

For `cohort_prior.parquet` and `Z_cap_pinned.json`: spec §10 fixes the schema; sub-task plans extending it must follow the additive rule and bump a `schema_version` field (recommended addition to Pin M4 — flag, not block).

PyArrow read-time validation: `ParquetDataset(path).schema.equals(expected_schema)` returns bool; raise `SchemaMismatchError` per Pin M4. Use `pyarrow.unify_schemas([old, new])` for cross-version reads.

**Sources:** [arrow-docs], [arrow-write], [datacamp-parquet], [designandexecute], [parquet-evolution].

---

## Q2. Module-boundary patterns for functional-python three-tier

### Real-world precedent
**`returns` library** (dry-python) [returns-gh] organizes by *container/effect type* rather than tier — `returns.maybe`, `returns.result`, `returns.io`, `returns.future`. Each module bundles the Value (`Some`, `Nothing`), the Callable (`.bind`, `.map` operations), and the Protocol (`KindN`, `Container1`) co-located. `returns.pointfree` and `returns.pipeline` provide higher-order standalone Callables (`bind`, `flow`).

This validates a **horizontal-slice option** for our `simulations/`: each .py file inside `types/` could own one mathematical object end-to-end (e.g., `truncpareto.py` containing `TruncParetoParams` Value type + accessors). Plan v1.1 leaves .py decomposition to task-time; this evidence supports per-object slicing inside each tier folder.

### Where Callables live
`returns` co-locates Callables with their Value containers. For our codebase, plan v1.1's *vertical* split (separate `types/` vs `modules/`) is stricter — and matches `pydantic-core` Rust internals where validators (Callable equivalent) are physically separated from schema (Value equivalent) [pydantic-perf]. **Recommendation: keep plan v1.1's vertical split.** It enforces the "no Callable imports in Value tier" invariant by directory boundary, which `returns`-style co-location cannot.

### Protocol for cross-tier interfaces
`returns` uses `Protocol` for `Container1`, `KindN`. Pydantic-v2 uses `Protocol` for `SchemaValidator`, `SchemaSerializer`. Both confirm: `Protocol` is the right tool for our IO-boundary handshakes (e.g., `class ParquetReader(Protocol): def read(...) -> Table`). Do **not** import concrete IO classes into `modules/`; depend on Protocols.

**Sources:** [returns-gh], [pydantic-perf], functional-python skill (read 2026-05-08).

---

## Q3. Pydantic-vs-frozen-dc decision matrix

The `tighten-types` skill (`~/.claude/skills/tighten-types/SKILL.md`, 2026-05-08 read) §3 prescribes:

> **Choosing between Pydantic and TypedDict:** Prefer `BaseModel` when the dict crosses a system boundary (API request/response, config files, serialisation) or would benefit from validation. Prefer `TypedDict` when the value is an internal data structure that is never validated or serialised.

Combined with [hrekov-perf, pydantic-perf]:

| Construct | Use when | Cost | Our location |
|---|---|---|---|
| **`@dataclass(frozen=True)`** | Internal Value type, validated once at construction, used in hot paths (sampler loops, sympy rewrites) | ~10× faster than Pydantic for repeated access | `simulations/types/` — **all of it** |
| **`TypedDict`** | Dict-shaped row from external source (parquet row, JSON dict), no invariants beyond key presence | ~2.5× faster than nested BaseModel; static-checker only | parquet row schemas inside `simulations/utils/` for read-buffering |
| **`pydantic.BaseModel`** | External-system boundary, runtime validation needed (untrusted input), JSON deserialization | Validation cost; ~10–100× slower per construction than dc | `simulations/utils/` IO boundary **only** when reading external-fetched JSON (e.g., `Z_cap_pinned.json` from a future SAAS-COHORT-4 emission verified before downstream consumption) |

### Per-tier rule for `simulations/types/`
**Frozen-dataclass exclusively.** Validation in `__post_init__` is one-shot (M1: `if alpha <= 0: raise ValueError` is a `__post_init__` line; the M1 *floor* of 1.5 is not a Value-tier invariant per Pin M1 §15.13 — it binds at the sampler Callable). No Pydantic in `types/`; no TypedDict in `types/`.

### Per-tier rule for `simulations/utils/`
**Pydantic at parquet/JSON read boundary; TypedDict for in-memory row shapes during streaming.** `Z_cap_pinned.json` reading: a one-shot `BaseModel.model_validate_json(path.read_text())` then immediate conversion to a frozen-dc `ZCapPinned` Value type before returning to caller. This isolates Pydantic's runtime cost to the boundary; downstream code sees only the frozen-dc.

**Sources:** `tighten-types` SKILL.md, [hrekov-perf], [pydantic-perf], [hevalhazal-medium].

---

## Q4. PyMC `TruncPareto` availability — native or custom?

### Verdict: NOT native; canonical pattern is `pm.Truncated(pm.Pareto.dist(...))`

PyMC v5's continuous-distributions registry [pymc-continuous] does not include a `TruncatedPareto` class. There is `Pareto`, and there is the general-purpose `pm.Truncated` wrapper [pymc-truncated, pymc-truncated-v5.10].

### Canonical pattern
```
# from pymc.io.discourse + pymc-truncated:
pareto_dist = pm.Pareto.dist(alpha=alpha, m=x_m)
trunc_pareto = pm.Truncated("trunc_pareto", pareto_dist, lower=x_m, upper=kappa)
```

`pm.Truncated` requirements [pymc-truncated]:
- wrapped distribution must be a pure `RandomVariable` (Pareto qualifies);
- must implement `logcdf` for MCMC inverse-CDF sampling. **PyMC's `Pareto` has `logcdf`** (visible in v5 source, `pymc/distributions/continuous.py`); the long-standing gap was `logcdf` *of the Truncated wrapper itself*, tracked in [pymc-issue-6686] (closed by PR #7884, ≈2025).

Fallback if `logcdf` were absent: rejection sampling (`max_n_steps=10000` default) — slower but correct. Not needed for Pareto.

### Custom logp alternatives (deferred — not needed)
- `pm.DensityDist(name, alpha, x_m, kappa, logp=custom_logp)` — used when even rejection sampling can't construct the distribution. Not our case.
- `pm.Potential(name, custom_logp_term)` — adds a term to the joint log-prob; used for soft constraints, not full distributions. Not appropriate here.

### Implication for `simulations/types/TruncParetoParams`
**No extra fields needed.** The Value type is just `(alpha: float, x_m: float, x_max: float)` (matching PyMC's `(alpha, m, upper)`). The Callable sampler in `simulations/modules/` constructs `pm.Pareto.dist(...)` + `pm.Truncated(...)` at sampler-construction time and enforces Pin M1's α ≥ 1.5 floor before that construction. SAAS-COHORT-1 will consume `TruncParetoParams` directly with no schema migration.

**Sources:** [pymc-continuous], [pymc-truncated], [pymc-truncated-v5.10], [pymc-issue-6686], [pymc-pareto-v5.7].

---

## References

- **[arrow-docs]** Apache Arrow PyArrow v24 — Reading and Writing Parquet. https://arrow.apache.org/docs/python/parquet.html
- **[arrow-write]** PyArrow `write_to_dataset`. https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_to_dataset.html
- **[datacamp-parquet]** Apache Parquet Explained (DataCamp 2025). https://www.datacamp.com/tutorial/apache-parquet
- **[designandexecute]** Best Approaches to Manage Schema Evolution for Parquet (2025). https://www.designandexecute.com/designs/best-approaches-to-manage-schema-evolution-for-parquet-files/
- **[parquet-evolution]** Parquet schema evolution rules — additive append-at-end (cited by designandexecute and arrow-docs cross-ref).
- **[returns-gh]** dry-python/returns. https://github.com/dry-python/returns
- **[pydantic-perf]** Pydantic Performance docs. https://pydantic.dev/docs/validation/latest/concepts/performance/
- **[hrekov-perf]** Pydantic vs. Dataclasses speed comparison. https://hrekov.com/blog/pydantic-vs-dataclasses-speed-comparison
- **[hevalhazal-medium]** Dataclasses vs Pydantic vs TypedDict vs NamedTuple. https://hevalhazalkurt.medium.com/dataclasses-vs-pydantic-vs-typeddict-vs-namedtuple-in-python-85b8c03402ad
- **[pymc-continuous]** PyMC Continuous Distributions. https://www.pymc.io/projects/docs/en/stable/api/distributions/continuous.html
- **[pymc-truncated]** PyMC Truncated wrapper (stable). https://www.pymc.io/projects/docs/en/stable/api/distributions/truncated.html
- **[pymc-truncated-v5.10]** PyMC v5.10.2 Truncated. https://www.pymc.io/projects/docs/en/v5.10.2/api/distributions/truncated.html
- **[pymc-pareto-v5.7]** pymc.Pareto v5.7.1. https://www.pymc.io/projects/docs/en/v5.7.1/api/distributions/generated/pymc.Pareto.html
- **[pymc-issue-6686]** Implement logcdf for Truncated and Censored — pymc-devs/pymc#6686 (closed via #7884). https://github.com/pymc-devs/pymc/issues/6686
- **`tighten-types` SKILL.md** — `~/.claude/skills/tighten-types/SKILL.md` (read 2026-05-08).
- **functional-python SKILL.md** — `~/.claude/skills/functional-python/SKILL.md` (read 2026-05-08).
