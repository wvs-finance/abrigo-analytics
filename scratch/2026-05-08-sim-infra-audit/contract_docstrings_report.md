# Contract-Docstrings Audit — `simulations/`

**Scope**: Every public function/method/Callable in `simulations/{types,modules,utils}/`.
**Skill**: `contract-docstrings` (input invariants, errors raised on violation,
errors from external state, silenced errors from callees).
**Branch**: `iter/saas-builder-stage-2`. **Baseline HEAD**: `2e73300` (Phase 3.1
tighten-types pass).

## Summary

| Metric | Count |
|---|---|
| Public functions / Callables audited | **41** |
| Already compliant (no edit) | **31** |
| Docstrings extended with Contract section | **10** |
| Docstrings rewritten (substance changed) | **0** |
| Load-bearing docstrings preserved verbatim | **3** (M1 / M3 / M5) |

**Final state**:
- `ruff check simulations/` → **All checks passed**
- `pytest simulations/tests/ -v` → **177 passed**

No code logic changed. No exceptions added or silenced. Docstrings only.

## Per-file findings

### `types/distributions.py` — already compliant
All 10 public symbols had Contract-equivalent prose. The α-floor contract on
`TruncParetoParams` (preserved verbatim) is the load-bearing M1 documentation;
the L¹-deviation contract on `tightness_l1_deviation` already lists Args /
Returns / Raises. No edits.

### `types/fx.py` — already compliant
`FXPathParams`, `RealizedVarianceParams`, `BlendedPriceParams` carry full
validation contracts. The M3 BlendedPriceParams formula docstring is
load-bearing — preserved verbatim. `fx_amplitude_envelope` is a trivial pure
accessor (no Contract section warranted per skill rules). No edits.

### `types/posterior.py` — 2 accessors extended
- `parameter_index()` — Contract section added: documents that the underlying
  `tuple.index` raises `ValueError` and that the function re-raises with a
  descriptive message via `from exc`.
- `cdf_percentile_value()` — Contract section added: documents the **exact
  float-equality** lookup semantics (no tolerance) — surprising behaviour worth
  flagging.
- `n_total_draws()`, `ci_95_width()` left as one-liners (trivial accessors).
- All three Value classes (`PosteriorDraws`, `MonthlyCDF`, `ZCapPinned`) already
  carry full validation-contract sections; not modified.

### `types/tier.py` — 2 accessors extended
- `categorical_mass()` — Contract added: implicit `KeyError` from dict lookup
  if `tier` is mis-typed at runtime (Literal type-checker enforces statically).
- `subscription_price_usd()` — same.
- `TierPrior` and `TierPricing` already had full validation contracts. No edits.

### `types/protocols.py` — already compliant
All five `Protocol` declarations carry one-line summaries; Protocols cannot
"raise" so no Contract section applies. No edits.

### `modules/samplers.py` — already compliant
Three Callables (`TruncParetoSampler`, `NegBinSampler`, `TierMixCategorical`)
all carry full Args/Returns/Raises blocks plus M1 documentation on
`TruncParetoSampler.__post_init__`. M1 α-floor contract preserved verbatim. No edits.

### `modules/regularizers.py` — already compliant
`SoftplusRegularizer` carries the M2 tightness contract on the class
docstring; `__post_init__` raises explicitly with a clear message; `__call__`
has Args / Returns. No edits.

### `modules/pricing.py` — already compliant
`BlendedPriceFn` is a total function — no preconditions beyond the
`BlendedPriceParams` invariants (enforced upstream). M3 formula citation
preserved verbatim. No edits.

### `modules/fx_path.py` — 2 Callables extended
- `FXPathGen.__call__` — Contract added: documents that `np.nan` / `np.inf`
  in `t` propagate **silently** to NaN outputs (preserves numpy total-function
  semantics; flagged as the silent-wrong-result case).
- `RealizedVarianceCalc.__call__` — Contract added: documents the
  **silent-wrong-result** case where `len(path) ≠ horizon_T + 1` is not
  cross-checked. The Callable trusts caller-supplied `path` length; mismatch
  silently changes the σ_T denominator.
- `epsilon_from_sigma_T` already had a full Args/Returns/Raises block. No edit.
- M5 PRIMITIVES.md (6) / (7) / (8) citations preserved verbatim.

### `utils/parquet_io.py` — 4 IO `__call__` methods extended
- `CohortPriorWriter.__call__` — Contract added: empty-rows raises
  `ValueError`; `astype` cast-failure surfaces as pandas `ValueError` (this
  IS the M4 dtype-mismatch detector); column-set drift via
  `SchemaMismatchError`; OS errors propagate.
- `CohortPriorReader.__call__` — Contract added: missing file
  `FileNotFoundError`, column drift `SchemaMismatchError`, pandas read
  errors propagate.
- `SyntheticTauWriter.__call__` — Contract added: documents the
  **`month=4/` vs `month=4.0/` Hive-directory hazard** that
  `SYNTHETIC_TAU_DTYPES` defends against. pyarrow conversion errors
  propagate.
- `SyntheticTauReader.__call__` — Contract added: missing-directory
  vs no-parquet-files distinction; partition-column reattachment
  semantics (Categorical → str coercion).

### `utils/json_io.py` — 2 IO `__call__` methods extended
- `ZCapPinnedReader.__call__` — Contract added: enumerates the **five
  validation layers** (file exists → JSON parse → top-level type →
  field-set → Pydantic per-field → `ZCapPinned.__post_init__`). Notes
  that `json.JSONDecodeError` and `pydantic.ValidationError` are NOT
  silenced.
- `ZCapPinnedWriter.__call__` — Contract added: notes the writer relies
  on upstream `ZCapPinned` invariants (no re-validation); only OS errors
  can surface.
- `_coerce_tier_mix` already had a clear docstring. No edit.

### `utils/audit_block.py` — 1 Callable extended
- `AuditBlockHasher.__call__` — Contract added: delegates to
  `compute_audit_block`; documents the inherited preconditions
  (non-empty paths, regular files) and the propagating `OSError` on
  read failure. `compute_audit_block` itself was already fully
  contract-documented.

### `utils/pricing_fetcher.py` — 1 Callable extended
- `StaticPricingFetcher.__call__` — Contract added: documents that the
  function is **total** (no preconditions, no raises) because it reads
  `Final` module constants only. Flagged as a placeholder for a future
  live-HTTP fetcher whose contract would need rewriting.

### `utils/errors.py` — already compliant
`SchemaMismatchError` carries a clear semantic-cause docstring. No edit.

## Findings of note

1. **Silent wrong-result in `RealizedVarianceCalc.__call__`**: the Callable
   does not cross-check `len(path) == params.horizon_T + 1`. A caller passing
   a shorter or longer path silently changes the σ_T denominator. Now
   documented; remediation (if desired) belongs to a hypothesis-test in
   Phase 3.3, not this docstring pass.

2. **Silent NaN propagation in `FXPathGen.__call__`**: numpy's total-function
   semantics let non-finite `t` produce NaN paths without warning. Documented
   as expected behaviour preserving the M5 closed form.

3. **Hive-directory hazard mitigation in `SyntheticTauWriter`**: the
   `astype(SYNTHETIC_TAU_DTYPES)` call on line ~253 is **load-bearing** for
   producing `month=4/` directories rather than `month=4.0/` when callers
   pass `int`-shaped data through the unchecked `TypedDict`. Docstring now
   makes this explicit.

4. **Pydantic-vs-Schema error layering** in `ZCapPinnedReader`: the field-set
   pre-check is intentional — without it, callers would get a
   `pydantic.ValidationError` (which doesn't subclass `ValueError`) instead
   of `SchemaMismatchError` for the most common drift mode. Now documented.

No bugs identified. No refactor recommendations made (per skill rules — this
is a documentation pass).

## Load-bearing docstrings preserved verbatim

- **M1**: `TruncParetoParams` α-floor contract per spec §15.13 / §8(6) —
  the Value-tier-vs-sampler-tier split.
- **M3**: `BlendedPriceParams` formula per spec §5.1, with the Sonnet 4.6
  arithmetic verification (≈ 7.15 USD/MTok).
- **M5**: `FXPathGen` PRIMITIVES.md (6) closed form; `RealizedVarianceCalc`
  PRIMITIVES.md (7); `epsilon_from_sigma_T` PRIMITIVES.md (8).

These remain unchanged in substance; Contract sections were appended only.
