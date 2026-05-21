# E10 Phase 3 (E10.2) — Code-Quality Review (Stage 2)

Reviewer: Code Reviewer agent. Scope: correctness, maintainability, numerical
soundness of the Phase-3 panel + decomposition code. Spec-compliance (stage 1)
already PASSED after CORRECTIONS-E10-7; not re-litigated here.

## Verdict: APPROVED_WITH_NITS

No Critical findings. No unaddressed Important findings (one Important is a
latent-degeneracy concern with a minimal fix; it does not block because all 150
real panel cells are unaffected — see I-1). Counts: 0 Critical, 1 Important,
5 Minor.

The exact §4.2 decomposition numerics are sound. The variance/covariance
estimator convention is consistent across all three terms (same `n`, same
population divisor, same surviving index). The single-canonical-X reconciliation
is correctly implemented. All 22 Phase-3 unit tests pass; tier-import discipline
holds.

## Files reviewed

`modules/decomposition.py`, `modules/panel_construction.py`,
`modules/realized_variance.py`, `types/panel.py`, `types/fx.py`,
`types/decomposition.py`, `utils/panel_io.py`,
`scripts/build_e10_gsps_panel.py`, the three Phase-3 unit test files,
`nhpp_engine.py` `_cell_seed`.

---

## Important

### I-1 — `_MIN_SURVIVING_DAYS = 2` admits a degenerate, unflagged cell

`panel_construction.py:78` / `:160` / `:169`. A cell with exactly 2 surviving
positive-Q days yields exactly 1 daily log-return. `population_variance` of a
length-1 series returns `0.0` (the mean equals the single observation), so the
cell is built with `material_gap = False`, `var_total = var_fx = var_q =
cov_term = 0.0`, `identity_residual = 0.0`, and `fx_variance_share = NaN`. I
reproduced this directly. The identity check passes *vacuously* (0 = 0+0+0) and
the cell enters the panel as a non-gap, real cell carrying no information — a
silent zero that would bias any cross-cell variance-share statistic toward 0
and inject a NaN share.

The Phase-3 memo referenced a ≥4-surviving-day expectation; the code enforces
only ≥2. The docstring at `panel.py:36` claims `material_gap` is True "iff the
cell has fewer than two surviving days" — but the operative defect is at 2, not
below 2, because the *log-return* count (n_surviving − 1) must be ≥ 2 for a
non-degenerate variance, not the day count.

This is downgraded from Critical only because, per the spec-reviewer and the
`test_full_panel_identity_holds_exactly_on_real_data` assertion (`n_cells ==
150`, no material gaps observed), every real panel cell has many surviving
days — so no production cell currently hits this. It remains a latent defect.

Minimal fix: set `_MIN_SURVIVING_DAYS = 3` (⇒ ≥2 log-returns ⇒ non-degenerate
population variance), and correct the `panel.py` docstring to "fewer than three
surviving days". Alternatively, after computing `var_total`, treat a non-gap
cell whose `var_total == 0.0` as a degenerate gap. Prefer the threshold fix —
it is the cleaner invariant and matches the memo.

---

## Minor

### M-1 — Duplicated `_drop_zero_query_days` across two modules
`decomposition.py:173` and `panel_construction.py:81` define near-identical
private helpers; the `panel_construction` copy adds a length guard the
`decomposition` copy omits (the latter relies on `zip(strict=True)` to raise a
`ValueError` instead of the typed `DecompositionIdentityError`). Extract one
shared helper into `realized_variance.py` (or a small `differencing_grid`
helper) and have both call it, so the grid-mismatch path raises the same typed
error everywhere. Not load-bearing today because `ThreeWayDecompositionModule`
length-checks the indices before calling its copy (`decomposition.py:255`).

### M-2 — `build_fx_variance_cell` work is computed then discarded
`build_e10_gsps_panel.py:119` builds an `fx_cell` whose `realized_log_variance`
(full-daily-grid X) is then never used — `build_panel_cell` recomputes X on the
gapped grid and `panel.py` does not carry the field. Correct (this is the v0.7
single-canonical-X reconciliation), but the full-grid log-return pass is dead
computation. Consider a lighter `fx_cell` constructor that supplies only the
identity / `n_trading_days` / `qualifying`, or document the intentional waste.

### M-3 — `identity_residual` is re-stamped, not re-derived, after cell re-stamp
`decomposition.py:277` and `panel_construction.py:207` rebuild the
`ThreeWayDecompositionCell` to attach the cell identity, copying `var_*` and
`identity_residual` verbatim from the inner `decompose_cell` result. Correct,
but the re-stamped cell's `identity_residual` is no longer independently
verifiable against its own `var_*` fields without trusting the copy. A one-line
`assert` (or a single shared constructor that stamps identity inside
`decompose_cell` via optional kwargs) would remove the trust gap. Cosmetic.

### M-4 — `_rel_close` scale floor of 1.0 is generous for tiny variances
`build_e10_gsps_panel.py:138`. Realized log-variances of FX are O(1e-3) or
smaller; with `scale = max(|a|, |b|, 1.0)` the effective absolute tolerance is
`1e-9 · 1.0 = 1e-9`, i.e. the comparison degrades to absolute-1e-9 for all
small cells rather than true relative tolerance. This is *more* lenient than a
pure relative check, so it will not produce false HALTs, but it means a
simulator cell that drifts by 1e-10 *relative* (well above bit-noise for a
deterministic seed) passes silently. Given the seed is fully deterministic,
consider tightening to a pure relative check or dropping the `1.0` floor.

### M-5 — `panel_io.read` `PanelRow(**record)` has a `type: ignore`
`panel_io.py:217`. The `TypedDict` is constructed from an untyped `to_pylist()`
dict with a blanket `type: ignore[typeddict-item]` — no runtime validation that
the row actually has the declared keys/types beyond the column-name check at
`:211`. The column-set check catches missing/extra columns but not a wrong
dtype slipping through Arrow. Low risk because `_arrow_schema()` pins dtypes on
emit; acceptable for an internal Tier-1 artifact. Note for future hardening.

---

## Confirmed sound (checklist items that passed)

- **Decomposition numerics.** `var_fx`, `var_q`, `cov_term`, `var_total` all use
  population divisor `n` over the *same* surviving index; `cost_log_returns` is
  the pointwise sum `fx + q`; the residual `var_total − (var_fx+var_q+cov_term)`
  is checked against `1e-12`. The identity is exact, not leading-order. The
  Hypothesis property test (`test_additive_identity_holds_exactly_on_common_grid`)
  is a genuine exact-identity test over random grids, not a fixed fixture.
- **Zero-Q-day drop.** `_drop_zero_query_days` filters Q and FX on one shared
  comprehension over `zip(strict=True)` — X and Q drop on the identical
  surviving index; no off-by-one. `daily_log_returns` then differences both
  surviving series identically (n_surviving − 1 returns each).
- **Single canonical X.** In `build_panel_cell`, `x_realized_variance` and
  `decomposition.var_fx` both derive from the *same* `fx_returns` object
  (`panel_construction.py:166`). They differ only by sum-of-squares vs
  population-variance convention — intentional and documented at `panel.py:24`
  and `realized_variance.py:23`. Harmless: each consumer uses the convention
  its spec section pins (§3.2 sum for X cells, §4.2 `Var` for the split).
- **Determinism.** `_cell_seed` is a pure function of `(currency, year, month)`;
  `np.random.default_rng(seed)` is threaded explicitly per cell. I checked seed
  collisions across all 5 panel currencies × 2023-2026 — 240 distinct seeds,
  zero collisions (currency `ord`-sum bases 217/224/226/227/236 are distinct
  and the `year*100+month` term maxes at ~202612 < the 1e6 spacing). FX is real
  data so bit-exact; the 1e-9 simulator tolerance split is correctly applied.
- **NaN handling.** `fx_variance_share` is `NaN` when `var_total <= 0` or the
  cell is a material gap; `_rel_close` treats `NaN == NaN` as equal so the
  round-trip does not false-fail on gap cells.
- **Tier discipline.** `modules/` files import only `types/` and sibling
  `modules/`; no `utils/` import. `types/` imports nothing from
  `modules/`/`utils/`. The builder script is the IO boundary and is the only
  caller of `utils.panel_io` / `utils.fx_ingest_io`. `test_tier_import_discipline`
  passes.
- **functional-python.** All containers are `frozen=True, slots=True`
  dataclasses; modules are frozen-dc + `__call__` stateless callables; free
  pure functions elsewhere; full typing throughout.
- **File sizes / security.** Largest reviewed file is `nhpp_engine.py` (822 LoC,
  out of Phase-3 scope but noted); Phase-3 files are 42-293 LoC. No hardcoded
  secrets, no network calls in the builder (100% offline frozen Tier-2).
- **Tests.** 22/22 Phase-3 unit tests pass; assertions are genuine (exact
  identity, mismatched-grid raise, material-gap flag, schema-drift rejection).
  `test_covariance_term_near_zero_under_qfx_independence` was correctly fixed to
  use a genuinely orthogonal Q series with a documented rationale.

## Most important finding

**I-1** — `_MIN_SURVIVING_DAYS = 2` admits a 2-surviving-day cell that produces
an all-zero decomposition (`var_total = 0`, `fx_variance_share = NaN`) yet is
*not* flagged `material_gap`. The identity check passes vacuously and the
degenerate cell enters the panel as a real cell. No real panel cell currently
hits this (all 150 have many surviving days), so it does not block APPROVED —
but raise the threshold to 3 (⇒ ≥2 log-returns) and fix the `panel.py`
docstring.
