# Pre-Mortem Report — SIM-INFRA-0 Phase 3.5

**Scope:** `simulations/modules/` + `simulations/utils/`
  (CORRECTIONS-α §15.4 — scope expanded from modules/-only)
**Date:** 2026-05-08
**Branch:** `iter/saas-builder-stage-2` (HEAD `71d6338`)
**Skill:** pre-mortem

## Summary

Eight post-mortems written. The codebase is sturdy — frozen-dataclass Callables
with `__post_init__` validation cover most arithmetic invariants, and the IO
boundary classes already throw typed `SchemaMismatchError` on shape drift. The
remaining fragilities are concentrated at three architectural seams:

1. **Numpy total-function semantics** at `__call__` boundaries — silent
   NaN/inf propagation and silent length-mismatch denominators.
2. **Stringly-typed Hive partition columns** — `month=4/` vs `month=4.0/`
   directory-name mismatch is one `astype` step away.
3. **Pre-Pydantic schema-set check ordering** in `ZCapPinnedReader` — error
   type contract (`SchemaMismatchError` vs `pydantic.ValidationError`) is
   only enforced by a single ordered if-block.

Five fragilities resolved with regression TESTs (preferred per plan §15.4
hierarchy), three left as DOCUMENT (existing docstrings already explicit).
No production logic was altered — all changes are tests + docstring nudges.

## Post-Mortems

### 1. RealizedVarianceCalc length-mismatch silent denominator

**Severity:** High
**Component:** `simulations/modules/fx_path.py::RealizedVarianceCalc.__call__`
**Fragility type:** Coincidental correctness / Invisible invariant

#### What happened

A simulation iteration that introduced a daily-resampled FX path
(`len(path) = horizon_T`, off-by-one against the spec §7 contract of
`horizon_T + 1`) silently shifted every reported σ_T by ~1/T. Downstream the
inverted ε from `epsilon_from_sigma_T(σ_T, mean)` came back biased low by
~0.5%, falling under the (0, 1) admissibility window for several cohorts that
should have been clamped at boundary. The bias was first noticed when the
Stage-2 plan reviewer compared against a closed-form ε² mean² / 8 reference
and found a systematic 1/T-magnitude gap.

#### The change that caused it

A future iteration switched the path generator to omit the terminal sample
(`np.linspace(0, T, T)` instead of `np.linspace(0, T, T+1)`) to align with a
conventional "T daily returns over a T-day window". Reasonable change for a
financial-time-series-style refactor.

#### Why it broke

`RealizedVarianceCalc.__call__` uses `np.mean(diffs * diffs)` — the denominator
is `len(path)`, not `params.horizon_T + 1`. The class carries `params.horizon_T`
purely for documentation; nothing cross-checks `len(path) == horizon_T + 1`.
The docstring on lines 110–115 of `fx_path.py` explicitly notes "documentary"
and "silent wrong-result case", but a future maintainer rewriting the path
generator has no programmatic signal.

#### How it was caught

Only by a careful reviewer running the closed-form reference. No test would
catch a uniform 1/T bias because most existing tests check ratios or
proportional invariants, not the absolute denominator.

#### Hardening

Add a regression test asserting **the documented (intentional) behavior**:
`RealizedVarianceCalc` does NOT cross-check `len(path)` against
`params.horizon_T + 1`, so future code adding such a check would deliberately
surface as a test failure (forcing the maintainer to confront the contract
choice).

**Disposition:** TEST
**Test:** `simulations/tests/test_modules.py::TestPreMortem::test_realized_variance_documented_no_horizon_cross_check`

---

### 2. FXPathGen NaN/inf silent propagation

**Severity:** Medium
**Component:** `simulations/modules/fx_path.py::FXPathGen.__call__`
**Fragility type:** Assumptions baked into data transformations

#### What happened

A future calibration loop fed `t = np.arange(0, T, dtype=int)` containing
implicit `NaN` values (from a `pd.to_numeric(..., errors="coerce")` upstream).
The FX path emerged with `NaN`-poisoned regions; downstream
`RealizedVarianceCalc` dutifully returned `NaN`; `epsilon_from_sigma_T(NaN, ...)`
raised `ValueError("sigma_T = nan must be finite ≥ 0")`. The ValueError pointed
at the inversion primitive — the actual bug was at the calibration-loop's t
construction, three call frames upstream.

#### The change that caused it

A pandas-based ingest layer was introduced for empirical t-grids; the
`coerce`-on-error policy looked equivalent to a defensive cast.

#### Why it broke

`FXPathGen.__call__` propagates NaN/inf silently (numpy total-function
semantics, documented on lines 56–60 of `fx_path.py`). No upstream guard, no
NaN-mask check. The `ValueError` surfaces at the wrong layer, masking the root
cause.

#### How it was caught

The error message itself; debugging took ~30 minutes to walk back up the call
chain.

#### Hardening

Pin the **documented** behavior with a regression test: `FXPathGen.__call__`
returns NaN when `t` contains NaN. A future "defensive guard" change that
raises instead would deliberately fail the test, forcing a contract review.

**Disposition:** TEST
**Test:** `simulations/tests/test_modules.py::TestPreMortem::test_fx_path_gen_propagates_nan_silently`

---

### 3. SyntheticTauWriter dtype-cast load-bearing for Hive partition layout

**Severity:** Critical
**Component:** `simulations/utils/parquet_io.py::SyntheticTauWriter.__call__`
**Fragility type:** Load-bearing default / Invisible invariant

#### What happened

A future writer optimization removed the explicit
`df = df.astype(dict(SYNTHETIC_TAU_DTYPES))` step on the rationale that
"pyarrow infers dtypes from pandas anyway". Hive partition directories
landed on disk as `month=4.0/` instead of `month=4/`. The reader still passed
its column-set check but produced subtly different `month` values
(`int(4.0) == 4`, so equality survived; downstream parquet partition-pruning
queries that hard-coded `month=4` returned zero rows because the directory
literally was named `month=4.0`).

#### The change that caused it

A perf-pass removed what looked like a redundant cast, with the diff comment
"pyarrow handles this".

#### Why it broke

`SYNTHETIC_TAU_DTYPES["month"] = "int64"` is the only mechanism enforcing
integer-typed partition columns. The TypedDict `SyntheticTauRow` declares
`month: int` but is unchecked at runtime — callers passing `month=4.0` would
flow through unaltered without the explicit `astype`.

#### How it was caught

`test_synthetic_tau_dtype_enforcement` (Task 2.4 + I2 fix) already covers
the directory-name invariant. Added a complementary **constant-pin** test so
removal of the `int64` declaration itself surfaces as a unit-test failure,
not just an integration failure.

#### Hardening

**Disposition:** TEST (complementary)
**Test:** `simulations/tests/test_utils.py::TestPreMortem::test_synthetic_tau_dtypes_pin_month_int64`
(documents that `SYNTHETIC_TAU_DTYPES["month"]` is load-bearing).

---

### 4. ZCapPinnedReader pre-Pydantic field-set check ordering

**Severity:** Medium
**Component:** `simulations/utils/json_io.py::ZCapPinnedReader.__call__`
**Fragility type:** Implicit ordering dependency

#### What happened

A future refactor moved the field-set check **after** `model_validate_json`
on the rationale that "Pydantic already raises on extra fields with
`extra='forbid'`". A consumer that previously caught `SchemaMismatchError`
(a `ValueError` subclass) silently stopped catching anything because the
reader now raised `pydantic.ValidationError`. The consumer's test suite still
passed — pydantic.ValidationError is also derived from Exception, but the
specific `except SchemaMismatchError` branch became dead code.

#### The change that caused it

Refactor: "Pydantic's `extra='forbid'` makes the manual check redundant."

#### Why it broke

The contract on lines 86–104 of `json_io.py` advertises that field-set drift
surfaces as `SchemaMismatchError`. This is preserved only by the manual
`actual != expected` check on lines 118–125 running BEFORE
`model_validate_json` on line 126. Pydantic raises `ValidationError`, which
is NOT a subclass of `ValueError` — consumers depending on `except ValueError`
would silently lose error coverage.

#### How it was caught

Existing test `test_zcap_pinned_reader_schema_drift_extra_field` already
checks for `SchemaMismatchError`. We add an explicit assertion that the
caught exception is NOT a `pydantic.ValidationError` to pin the ordering.

#### Hardening

**Disposition:** TEST
**Test:** `simulations/tests/test_utils.py::TestPreMortem::test_zcap_pinned_reader_extra_field_is_not_pydantic_validation_error`

---

### 5. compute_audit_block path-sort key is `str(p)`, not absolute path

**Severity:** Medium
**Component:** `simulations/utils/audit_block.py::compute_audit_block`
**Fragility type:** Stringly-typed contract / Invisible invariant

#### What happened

A future caller passed a mix of relative and absolute paths to
`compute_audit_block` for the same files (one upstream call site used
`Path.resolve()`, another used the raw `Path("data/x.txt")`). The two callers
produced **different** sha256 audit blocks for what semantically are the same
files because:
1. The path-sort key is `str(p)` not `str(p.resolve())`.
2. The hashed delimiter line `f"--- {p}\n"` embeds the literal path string.

A `ZCapPinned.audit_block` produced by call site A failed equality with one
produced by call site B; downstream consumers that pinned audit blocks across
runs reported false drift.

#### The change that caused it

A defensive `Path.resolve()` was added at one call site (audit-block helper
in a new harness) and not the other (legacy notebook script).

#### Why it broke

`compute_audit_block` documents path-sort invariance but does NOT document
relative-vs-absolute path equivalence. The delimiter `f"--- {p}\n"` makes the
digest a function of the literal Path string, not the file identity.

#### How it was caught

A reviewer noticed two audit blocks that should have matched did not. Added
a regression test pinning the documented (intentional) behavior: relative
and absolute Path representations of the same file yield DIFFERENT digests,
forcing future callers to commit to one canonicalization policy.

#### Hardening

**Disposition:** TEST + DOCUMENT
**Test:** `simulations/tests/test_utils.py::TestPreMortem::test_compute_audit_block_path_form_matters`
Docstring updated to call out the relative-vs-absolute fragility.

---

### 6. ZCapPinned tier_mix sum-to-one tolerance is hardcoded 1e-9

**Severity:** Low
**Component:** `simulations/types/posterior.py::ZCapPinned.__post_init__`
**Fragility type:** Load-bearing default

#### What happened

A future iteration scaled `tier_mix` values to be very small (e.g.,
percent-mass on a 100-tier expansion). The sum-to-one check
`abs(total - 1.0) > 1e-9` started failing on legitimate posteriors due to
accumulated float64 summation rounding when summing 100+ tiny floats.

#### The change that caused it

Tier-set expansion to a 100-tier posterior decomposition.

#### Why it broke

The 1e-9 tolerance is reasonable for 3 tiers but does not scale linearly with
the number of summands. Out of scope for this codebase (tier set is closed at
3) — flagged for forward awareness only.

#### How it was caught

N/A — this is a future scenario; the current 3-tier set is comfortably under
the tolerance.

#### Hardening

**Disposition:** DOCUMENT (current scope is 3 tiers; flag in posterior.py
docstring that 1e-9 assumes O(3) summands).

---

### 7. SoftplusRegularizer numerical near κ → 0

**Severity:** Low
**Component:** `simulations/modules/regularizers.py::SoftplusRegularizer.__post_init__`
**Fragility type:** Boundary condition

#### What happened

A future caller constructed `SoftplusParams(beta=1000.0, kappa=1e-6)`.
The L¹ tightness check `dev < 1e-3 · kappa` became `dev < 1e-9`, which
`tightness_l1_deviation` numerically integrated by quadrature on `[0, 2κ]`
cannot reliably distinguish from zero. The construction passed despite the
spec intent that κ be on the order of the cohort's per-token cost cap (USD).

#### The change that caused it

A unit-conversion experiment (USD → cents) reduced κ by 100×.

#### Why it broke

The relative tightness check ties to κ; at κ → 0 the threshold drops below
quadrature noise. Spec §5.1 (T2) implicitly assumes κ ~ O(1) USD.

#### How it was caught

N/A — speculative. Documented in the regularizer's docstring as a known
boundary.

#### Hardening

**Disposition:** DOCUMENT (note the implicit κ ~ O(1) assumption in the
SoftplusRegularizer docstring).

---

### 8. TruncParetoSampler α exactly equal to 1.5 floor

**Severity:** Low
**Component:** `simulations/modules/samplers.py::TruncParetoSampler.__post_init__`
**Fragility type:** Boundary condition

#### What happened

A future cohort with `α = 1.5` exactly was admitted by the
`α >= 1.5` floor check. Calibration that compared against a baseline using
strict `α > 1.5` produced a one-sample boundary disagreement.

#### The change that caused it

Spec §8(6) reading: ambiguity between "≥ 1.5" and "> 1.5" floor. Sampler
implements the inclusive ≥ form.

#### Why it broke

The boundary is documented in the docstring; nothing surfaces the choice in
tests at the exact boundary.

#### How it was caught

N/A — speculative. We add a regression test pinning the documented
inclusive-floor behavior.

#### Hardening

**Disposition:** TEST
**Test:** `simulations/tests/test_modules.py::TestPreMortem::test_truncpareto_alpha_floor_inclusive`

---

## Themes and Recommendations

**Theme 1 — Documented "intentional silent behaviors" lack regression
coverage.** Several primitives explicitly document silent wrong-result paths
(NaN propagation, length-mismatch denominator, relative-vs-absolute path
hashing) but no test pins those choices. A well-meaning future "defensive
guard" PR could land without surfacing the contract change. **Recommendation:**
when a docstring says "silent" or "documentary", add a test that pins the
silence.

**Theme 2 — Hive partition column dtypes are the highest-leverage IO
fragility.** The `synthetic_tau_t` schema has one cast that, if removed,
silently corrupts on-disk directory structure. Beyond the existing dtype
test, we add a constant-pin test. **Recommendation:** treat
`SYNTHETIC_TAU_DTYPES` as a frozen Final and add a CI check that its values
do not change without an explicit migration note.

**Theme 3 — Error-type ordering at IO boundaries.** `ZCapPinnedReader`'s
contract that drift surfaces as `SchemaMismatchError` (not Pydantic) is
preserved only by the order of two if-blocks. **Recommendation:** add a
regression test asserting the exception type explicitly (NOT just that
`ValueError` is raised), so the ordering is observable.

No structural refactors were applied. All hardening was via tests and minor
docstring edits — preserving the "no production logic changes" constraint
of Phase 3.5.
