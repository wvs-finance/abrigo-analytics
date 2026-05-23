# E10 Phase 4 — Code-Quality Review

**Scope:** the three Phase-4 modules (`vol_on_vol_regression`, `surface_grid`,
`currency_spread`), their three companion type modules, the 37 new unit
tests, and the executed `03_surface_characterization.ipynb` notebook +
side-effect JSON. Spec-compliance and posture/fishing are out of scope (covered
in parallel reviews).

**Top-line verdict: APPROVED_WITH_NITS.**

The implementation is solid, defensively-written, well-documented, and respects
the three-tier discipline cleanly. Every Phase-4 test passes (37/37 green
locally). I found **zero Critical** items, **two Important** items (one
implementation/docstring drift; one test-coverage gap), and a small number of
**Minor** items. None block the commit; addressing Important-1 is a one-line
fix worth doing before the next time the panel acquires material-gap cells.

---

## What's good (briefly)

- **Tier discipline is exemplary.** `types/` imports nothing from `modules/`
  or `utils/`; `modules/` imports only from `types/` and `_errors`;
  no `BaseModel` / `TypedDict` / inheritance creep. The repo-wide grep for
  cross-tier imports returns nothing actionable.
  (`simulations/e10_gsps/modules/{vol_on_vol_regression.py:55-61,
  surface_grid.py:82-97, currency_spread.py:48-70}`).
- **Frozen-dataclass discipline holds.** Every returned object is
  `@dataclass(frozen=True, slots=True)`; no class-with-state, no `__init__`
  mutation in `modules/` or `types/`.
- **No firewalled patterns.** Zero `type: ignore`, zero `# noqa`, zero
  `except Exception` / `BaseException`, zero bare `except`. The only `raise`
  sites are narrow `ValueError` / `SurfaceGridError` at well-defined input
  gates.
- **Docstring contracts are largely complete** — every public function
  documents inputs, returns, and the specific exception(s) raised on input
  violation. The "Raises" sections are *specific* (e.g. `SurfaceGridError:
  Q-range invalid, panel empty, or no panel cell carries a finite share` —
  the three failure modes are enumerated, not collapsed to "input invalid").
- **Numerical edge cases are handled defensively.**
  `_within_slope` guards the degenerate `denom == 0.0` case (collinear-with-
  FE) by returning `0.0` rather than blowing up
  (`vol_on_vol_regression.py:144-160`); a unit test exercises this
  (`test_betas_zero_on_degenerate_single_month_panel`).
- **The interior-crossing semantic guard is the right call.** A surface
  entirely below `s_be` (which IS what the Phase-3 panel produces — `share ~
  3 dex below s_be`) would naively flag as "interior crossing" because all
  interior cells are below. The semantic guard at
  `surface_grid.py:296-301` ("a crossing requires at least one endpoint to
  clear") correctly routes the panel-wide-dominance case to
  `q_variance_dominance_flag` and the interior-crossing flag to False —
  exactly the §9-classifier behaviour the verdict ladder requires. The
  notebook's executed `interior_crossing_flag = False` +
  `q_variance_dominance_flag = True` confirms this.
- **The user-locked decisions are wired correctly:** the ≥3-contiguous rule
  is `min_run_length=3` in `evaluate_surface_grid` and
  `_per_currency_surface`; the legacy `min_run_length=1` is preserved only
  in the Phase-0 RED-harness overload `SurfaceGridModule.__call__` with an
  explicit docstring justification (`surface_grid.py:319-329`). The ±0.5
  dex band is implemented as `10**0.5 ≈ 3.16` symmetric multiplicative on
  the log scale (`_is_within_half_dex` at `surface_grid.py:149-160`,
  duplicated inline at `currency_spread.py:229-236`).
- **Endpoint pinning to user-supplied bounds.** `evaluate_surface_grid`
  rewrites the first and last grid points to the exact `q_low` / `q_high`
  values (not `numpy.logspace`'s ~1-ulp drift), so downstream consumers
  comparing against the anchored range see exact equality
  (`surface_grid.py:572-591`). Nice touch, tested at
  `test_evaluate_surface_grid_anchored_range_recorded`.
- **Notebook is reproducible.** No mutable globals, no monkey-patching, no
  star-imports, no across-cell state outside the standard `cells_panel /
  vov / sg / cs / ic` graph; the JSON artifact is written via
  `pathlib.Path.write_text` with `default=float` so numpy scalars
  serialize cleanly. A fresh kernel will reproduce.

---

## Important findings (should fix; one-line each)

### Important-1 — `_panel_mean_share` docstring says "non-material-gap cells" but the implementation does not filter on `material_gap`

`simulations/e10_gsps/modules/surface_grid.py:198-222`

```python
def _panel_mean_share(panel: Sequence[PanelCell]) -> float:
    """Panel-mean FX-variance share across non-material-gap cells.   # <-- claim
    ...
    """
    finite_shares = [
        cell.fx_variance_share
        for cell in panel
        if math.isfinite(cell.fx_variance_share)                      # <-- only isfinite
    ]
```

The filter is `math.isfinite(cell.fx_variance_share)` only — `cell.material_gap`
is never read. Two ways forward:

1. **Implementation fix (preferred):** add `and not cell.material_gap` to
   the comprehension, matching the docstring.
2. **Docstring fix:** drop "non-material-gap cells" from the docstring and
   document the policy as "across cells where the share is finite (material-
   gap cells with finite shares are included; the Phase-3 panel emits NaN
   shares on material-gap cells, so the isfinite filter happens to be
   equivalent in practice)."

**Why it matters today:** the executed notebook reports
`material_gap_flag: false` and `panel_cells: 150`, so the panel currently
carries no material-gap cells and the bug is inert. **Why it matters
tomorrow:** if any future regime-break re-screen yields a material-gap cell
with a finite share (e.g. a partial-month with reduced surviving days but
non-NaN var totals), the surface evaluator will silently include it,
contradicting the docstring's contract and Phase-3's defended "material-gap
cells excluded" invariant. Either fix is acceptable; the one-line
implementation fix is cheaper.

`currency_spread.py:229-236` carries an inlined duplicate of
`_is_within_half_dex`'s logic for currency-mean shares — same `isfinite`
omission, same lack of `material_gap` filter (via the shared
`_panel_mean_share` call upstream). Fixing `_panel_mean_share` corrects both
sites.

### Important-2 — No property-based (Hypothesis) test coverage on the three new modules

The repo elsewhere uses Hypothesis (`tests/strategies/types_strategies.py`,
`test_decomposition.py`, `test_types_roundtrip.py`); the three Phase-4 test
modules use only example-based tests. The high-value property tests that
are missing — each is a 5-10 line Hypothesis-`@given` addition, none
critical for commit but each catches a class of bug example-based tests
cannot:

- **`run_vol_on_vol` linearity property:** for any balanced panel and any
  `k > 0`, `run_vol_on_vol(scale_y_by_k(panel)).beta_two_way == k *
  run_vol_on_vol(panel).beta_two_way`. Catches future regressions that
  silently scale the FE projection (e.g. accidental double-demeaning).
- **`detect_interior_crossing` monotonicity property:** for any share grid,
  if you uniformly add `delta > 0` to every share, the `interior_crossing`
  flag transitions monotonically (True → True or True → False; never
  False → True under uniform lift). Catches sign / threshold inversions.
- **`compute_currency_spread` envelope-containment property:** at every
  grid point, `envelope_min <= envelope_q1 <= envelope_median <=
  envelope_q3 <= envelope_max`. The example tests cover the equal-share-
  per-currency case where these are all equal; a Hypothesis test over
  random per-currency shares would catch a future bug that inverts
  `np.nanquantile`'s axis argument.

This is a **suggestion**, not a blocker — the example-based coverage at 37
tests is solid for a Phase-4 commit. Capture as a follow-up.

---

## Minor findings (nits)

### Minor-1 — `_two_way_demean` per-currency / per-month mean loop is O(G·n + T·n); fine at G=5, T=30 but quadratic in panel scale

`vol_on_vol_regression.py:103-118`. The current loop builds an integer
boolean mask per currency and per month:

```python
for c in range(n_currencies):
    mask = currency_idx == c
    if mask.any():
        currency_means[c] = float(values[mask].mean())
```

At `n=150, G=5, T=30` this is irrelevant. If the panel ever scales to, say,
all 8 § 3.3 candidate currencies x 60 months = 480 cells across more groups,
`np.bincount(currency_idx, weights=values) / np.bincount(currency_idx)` is
a single-pass vectorized equivalent. Captured as scaling-debt only — do
not refactor now.

### Minor-2 — One-step FWL identity is exact only for balanced panels; the docstring is honest but the test suite never exercises the unbalanced case

`vol_on_vol_regression.py:88-91` correctly notes:

> for an unbalanced panel this is a first-order approximation, but the E10
> panel is balanced at 5 x 30 = 150.

Every Phase-4 vol-on-vol test calls `_build_synthetic_panel(n_currencies=5,
n_months=30)` — balanced. There is no test that asserts what
`beta_two_way` does on a deliberately-unbalanced panel (e.g. drop 3 cells
from one currency) — i.e. nothing pins the documented approximation error.
At the Phase-3-panel-is-balanced-by-construction invariant this is fine
(`material_gap` excludes a cell from regression input upstream, but only
via panel-builder filtering; the within-transformation itself never sees
the gap). If E10 ever lifts the balance invariant, add a regression test.

### Minor-3 — `_log_spaced` returns a tuple of `float`, but `evaluate_surface_grid` later passes that tuple into `scan_interior_crossing` which expects `Sequence[float]` — works fine, but the type annotation `tuple[float, ...]` would be tighter than re-binding via `q_grid = _log_spaced(...)` and `shares = [...]` (list)

Cosmetic only. The current `Sequence[float]` annotation accepts both.

### Minor-4 — `compute_currency_spread` does not validate that every panel currency appears in `is_em_or_dm` (or its override)

`currency_spread.py:274-276`:

```python
is_em_or_dm = dict(em_or_dm) if em_or_dm is not None else dict(
    DEFAULT_EM_OR_DM
)
```

If a future panel includes a currency the override map omits, the
downstream notebook overplot crashes at `cs.is_em_or_dm[cur]` with a
`KeyError`, far from this site. A two-line check —

```python
missing = set(by_currency) - set(is_em_or_dm)
if missing:
    raise SurfaceGridError(f"EM/DM tag missing for: {sorted(missing)}")
```

— would surface the failure at the source. Not blocking; the current
G=5 panel is fully covered by `DEFAULT_EM_OR_DM`.

### Minor-5 — `SurfaceGridModule.__call__` carries a `grid_resolution: float` parameter that is recorded on the result but never consumed by the per-cell evaluator

`surface_grid.py:384-458`. The per-cell evaluator (Phase-0 RED-harness
compatibility overload) accepts `grid_resolution` purely so the call site
can pass it through to `SurfaceGridResult.grid_resolution`. The docstring
correctly notes "the per-cell-as-grid evaluator does not refine in this
overload" but the parameter is otherwise inert. Either:

- pass it through (current behaviour, documented), or
- drop it and have the call site set `grid_resolution=float("nan")` /
  similar.

The current state is acceptable; just flag for the reader that the
parameter is a vestige.

### Minor-6 — Two `enumerate(...)` patterns rebuilt as `for i in range(len(...))`

`surface_grid.py:436` and `surface_grid.py:562` both use
`for i in range(len(...))` where `enumerate(decomposition_cells)` /
`enumerate(q_grid)` would be one symbol shorter and avoid an indexed
lookup. Style only.

### Minor-7 — The notebook's adaptive `REPO` discovery loop is fine but could be replaced with a single `REPO = Path(__file__).resolve().parents[N]` if notebooks ever get a portable launcher

`notebooks/e10_gsps/03_surface_characterization.ipynb` cell 1:

```python
REPO = Path.cwd()
while not (REPO / 'simulations').is_dir() and REPO != REPO.parent:
    REPO = REPO.parent
```

Works on a fresh kernel; cosmetic only.

### Minor-8 — `test_detect_interior_crossing_three_contiguous_strictly_interior_flags` carries a redundant assertion

`test_surface_grid.py:200`:

```python
assert end <= len(result.crossing_q_volumes) - 2 or end <= 5
```

`result.crossing_q_volumes` is `()` for `detect_interior_crossing` (it's
populated by `scan_interior_crossing`), so `len(result.crossing_q_volumes)
- 2 == -2` and the assertion reduces to `end <= 5`. The intent is to
assert "the run sits in strictly-interior indices, not at the endpoints".
The cleaner form would be `assert 1 <= start and end <= n - 2` where
`n = len(shares)` is passed through from the caller. Not wrong, just
opaque.

---

## Test-quality assessment

37/37 tests pass. The assertions are concrete (real expected values, not
loose `pytest.approx` everywhere — e.g. `residual_dof_two_way == 115`,
`n_cells == 150`, exact slope `pytest.approx(0.5, rel=1e-10)`). No
trivial / tautological asserts. The user-locked decisions are exercised:

- `min_run_length=3` rule: 4 dedicated tests
  (`test_detect_interior_crossing_single_cell_does_not_flag`,
  `test_detect_interior_crossing_two_contiguous_cells_do_not_flag`,
  `test_detect_interior_crossing_three_contiguous_strictly_interior_flags`,
  `test_no_interior_crossing_with_clean_surface_under_user_locked_rule`);
- ±0.5 dex adaptive doubling: 2 dedicated tests
  (`test_evaluate_surface_grid_adaptive_doubling_triggers_near_s_be`,
  `test_evaluate_surface_grid_no_adaptive_doubling_far_from_s_be`);
- EM/DM tagging: 1 dedicated test
  (`test_em_dm_tag_map_matches_default_assignment`).

A nit on the adaptive-doubling test: it triggers refinement with
`share = 0.25` exactly, which is `0.0 dex` from `s_be`. A complementary
boundary test at `share = s_be / 10**0.5` (the exact edge of the trigger
band) would pin the inclusive-boundary semantics in
`_is_within_half_dex`. Not blocking.

---

## Notebook lightweight check

- Headless `matplotlib.use('Agg')` set before any `pyplot` import.
- No `from simulations... import *`.
- No mutable globals; the cell graph is linear (`cells_panel → vov → sg →
  ic → cs → summary → JSON`).
- The side-effect `E10.3_surface_summary.json` matches the executed
  results: `panel_cells: 150`, `q_variance_dominance_flag: true`,
  `interior_crossing_flag: false`, `refined: false`, `sign_two_way: 1`,
  `sign_currency_only: 1`. Consistent with the descriptive-posture
  expectation.
- Cross-cell reproducibility on a fresh kernel: the `cells_panel = …` →
  `summary` chain has no hidden dependencies (no `sg`/`ic`/`vov` mutated
  in place).

---

## Closing

Code is ready to commit. The single Important item worth a one-line fix
before merge is the `_panel_mean_share` material-gap drift (Important-1);
the rest is suggestions and follow-up technical debt the user can carry
into Phase 5 / Phase 6 without rework. Verdict: **APPROVED_WITH_NITS**.

**File paths of substantive findings:**
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/e10_gsps/modules/surface_grid.py:198-222`
  (Important-1: docstring/implementation drift on material-gap filter)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/e10_gsps/modules/currency_spread.py:274-276`
  (Minor-4: missing EM/DM-tag completeness validation)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/e10_gsps/modules/vol_on_vol_regression.py:88-91`
  (Minor-2: unbalanced-panel approximation not tested)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/simulations/e10_gsps/tests/unit/test_surface_grid.py:200`
  (Minor-8: opaque interior-index assertion)
