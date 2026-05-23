# Phase 6 — Delphi Autofix Verification

**Date:** 2026-05-23
**Scope:** Verification of the 7-fix autofix wave applied per `Phase6_Delphi_propagation_map.md`.

**Headline:**
- All 7 fixes landed sequentially.
- Full unit suite: **152/152 passing** (pre-fix and post-fix baselines identical).
- Descriptive-posture firewall: **PASS** — 66 files scanned clean (54 source + 12 notebook).
- Verdict invariance: **CONFIRMED** — `NON-RETIREMENT` subtype `q_dominance` preserved.
- Notebooks 04 + 05 re-executed end-to-end.

---

## Per-fix verification

### Fix 1 — HIGH-1/2 GBM/JD calibration scale mismatch

**File touched:** `simulations/e10_gsps/modules/sensitivity_arms.py`

**Change:** Recalibrated `_arm_d_gbm_jd_comparator` from a (broken)
"per-month-equivalent vol with `T_month = 1`" framing to the correct
per-step (per-day) convention:
- `dt = 1.0` day; `T_month = n_steps_default * dt` days.
- GBM: `σ = sqrt(target_var_fx)` (was `sqrt(target_var_fx / T_month)`
  with `T_month = 1`, which was the bug's source).
- JD: same per-step diffusion split (`σ_jd² · dt = 0.9 · target_var_fx`);
  `λ_jump = 1/n_steps` (≈1 jump per month); `jump_std` derived to add
  the remaining 10% of per-step variance.
- Updated comment block at lines 459-464 and 506-518.
- Updated notes string at lines 644-651 to drop the false "calibrated
  to panel-mean var_fx" claim and state truthfully: "calibrated per
  currency to per-step (per-day) panel-mean Var(Δlog FX); GBM step
  dt = 1 day; n_steps = monthly day-count (default 21)."

**Numerical verification** (offline standalone check):
- `target_var_fx = 1.5e-4`, `n_steps = 21`, `n_paths = 256`.
- Measured per-step Var(Δlog X) on GBM ensemble: `1.43e-4`.
- Relative error: **0.048** (well below 0.1 tolerance).

**Downstream effect on `E10.4_arms_summary.json` arm-d** (post-notebook-rerun):
- `panel_mean_share`: `9.11e-6` → `1.88e-4` (rose by ~21x as predicted —
  this is the deflation-removal correction).
- `concordance_metric`: `1.44e-4` → `3.41e-5` (now closer to primary).
- `concordance_verdict`: `concordant` (unchanged).
- `q_variance_dominance_flag`: `True` (unchanged).

**Tests:** `simulations/e10_gsps/tests/unit/test_sensitivity_arms.py` —
16 passed.

### Fix 2 — MID-3 surface flat-broadcast disclosure

**Files touched:**
- `simulations/e10_gsps/types/surface.py` (added field + docstring)
- `simulations/e10_gsps/modules/surface_grid.py` (module docstring +
  two `SurfaceGridResult(...)` instantiations)
- `simulations/e10_gsps/modules/currency_spread.py` (one
  `SurfaceGridResult(...)` instantiation)
- `simulations/e10_gsps/tests/strategies/types_strategies.py`
  (Hypothesis strategy update)

**Change:** Added `is_panel_mean_broadcast: bool = True` field on
`SurfaceGridResult` Value-tier container. Documented in module + result
docstrings as Phase-6 Delphi auditor-1 MID-3 disclosure. Wired:
- `evaluate_surface_grid` → `True` (panel-mean broadcast).
- `compute_currency_spread._per_currency_surface` → `True`
  (per-currency mean broadcast).
- `SurfaceGridModule.__call__` (per-cell overload) → `False`
  (per-cell shares, not broadcast).

**Tests:** `test_surface_grid.py` + `test_currency_spread.py` +
`test_types_roundtrip.py` + `test_sensitivity_arms.py` — 56 passed.

### Fix 3 — MID-1 q-dominance flag spec-form sibling

**Files touched:**
- `simulations/e10_gsps/types/surface.py` (added field + docstring)
- `simulations/e10_gsps/modules/surface_grid.py` (helpers
  `_panel_mean_q_share` and `_cell_q_share`; spec-form flag computed
  at both `evaluate_surface_grid` and `SurfaceGridModule.__call__`)
- `simulations/e10_gsps/modules/currency_spread.py` (spec-form flag
  at `_per_currency_surface`; new import)
- `simulations/e10_gsps/tests/strategies/types_strategies.py`
  (Hypothesis strategy update)

**Change:** Added `q_variance_dominance_flag_spec_form: bool = False`
field on `SurfaceGridResult`. Code/share-form flag (`var_fx/var_total
< s_be` panel-wide) preserved as load-bearing for the §9 classifier;
spec-form flag (`var_q/var_total > 1 - s_be` panel-wide) emitted as
audit-transparent sibling. Both forms coincide iff `cov_term = 0`;
documented in docstrings. For the real E10 panel they coincide
because `cov_term` is small (residual ~1e-15).

**Tests:** Full unit suite — 152 passed.

### Fix 4 — MID-4 arm-b wording (algebraic-identity assertion)

**File touched:** `simulations/e10_gsps/modules/sensitivity_arms.py`

**Change:** Tightened module docstring, function docstring, decision-
citation, and notes string to state the canonical phrasing in three
places: "Arm (b) is an ALGEBRAIC-IDENTITY ASSERTION under monthly-
scalar coupling — not a coupled-daily re-simulation. A constant per-
month scalar drops out of daily Δlog Q exactly; concordance_metric = 0
is mathematical, not numerical."

**Tests:** `test_sensitivity_arms.py` — 16 passed. The
`test_arm_b_user_pinned_operationalization_yields_zero_metric` test
continues to assert `concordance_metric == 0.0` exactly (the algebraic
identity).

### Fix 5 — MID-2 vol-on-vol hand-rolled FWL slope (keep-as-is + doc)

**File touched:** `simulations/e10_gsps/modules/vol_on_vol_regression.py`

**Change:** Added docstring block on `_within_slope` explaining the
deliberate choice of hand-rolled FWL over statsmodels OLS: under the
descriptive-only posture only the slope sign and the two-co-primary
gap are reported; the hand-rolled form makes the no-SE contract
syntactically visible (structurally incapable of emitting an SE);
β̂ is mathematically identical to statsmodels OLS on the residualized
regressors (FWL theorem). β̂ values unchanged.

**Tests:** `test_vol_on_vol_regression.py` — 8 passed.

### Fix 6 — MID-5 strip BLR prose from classifier rationale

**File touched:** `simulations/e10_gsps/modules/verdict_classifier.py`

**Change:** `_rationale_q_dominance_full_surface` replaced. Removed:
"The convex FX-volatility hedge is not the right instrument for the
representative Web3 data-analyst profile: the cost-stream variance is
structurally bound to Q (own-output behavior), not to FX (BLR
virtual-economy price volatility). Honest, acceptable verdict — never
engineered away." Replaced with the prescribed mechanistic statement.

The BLR/PK interpretation already lives in `notebooks/e10_gsps/
05_verdict_writeup.ipynb` Trio 6 (lines 471-552) — labelled
"interpretive prose only - no computation". After notebook 05 re-
execution, the rendered `verdict_rationale` cell now carries the clean
mechanistic verdict; PK interpretation is confined to Trio 6.

**Tests:** `test_verdict_classifier.py` — 8 passed. No test asserts on
the stripped BLR substring.

### Fix 7 — End-to-end notebook re-execution

**Files touched (regenerated):**
- `notebooks/e10_gsps/04_sensitivity_arms.ipynb`
- `notebooks/e10_gsps/05_verdict_writeup.ipynb`
- `notebooks/e10_gsps/diagnostics/E10.4_arms_summary.json`
- `notebooks/e10_gsps/diagnostics/E10.5_verdict_summary.json`

**Verification (`E10.5_verdict_summary.json`):**
```
verdict: NON-RETIREMENT
non_retirement_subtype: q_dominance
verdict_rationale: "...Q-variance component dominates the §4.2
  three-way log-variance decomposition across the whole anchored
  Q-volume range... Load-bearing input: q_variance_dominates = True."
  [BLR/own-output/engineered-away clauses REMOVED]
inputs_snapshot.q_variance_dominates: true
phase5_all_concordant: true
no_rescue_clause_held: true
methods_paper_anchor_preserved: true
```

---

## Comprehensive verification

- **Unit suite:** `uv run pytest simulations/e10_gsps/tests/unit/` →
  **152 passed in 3.20s** (identical pass count to pre-fix baseline).
- **Firewall:** `python scripts/e10_firewall_check.py
  simulations/e10_gsps/ notebooks/e10_gsps/` → **PASS — 66 files
  scanned clean**.
- **No `type: ignore` added.** No `# noqa` added. No broad `except`
  introduced. No pre-commit bypass.
- **Verdict invariance confirmed:** §9 verdict `NON-RETIREMENT`
  subtype `q_dominance` preserved end-to-end.

## Arm-d numerical verification (Fix 1)

Pre-fix `E10.4_arms_summary.json` arm[2] (`d_gbm_jd_comparator`):
- `panel_mean_share`: **`9.113036737280616e-06`** (~17x deflated vs
  primary `1.535e-4`).

Post-fix `E10.4_arms_summary.json` arm[2]:
- `panel_mean_share`: **`1.876391998594440e-04`** (relative gap to
  primary panel-mean: `0.22` — close to target; the comparator
  measures a different stochastic process so exact equality is not
  required).
- Single-currency standalone check (COP, `target_var_fx = 1.5e-4`,
  `n_paths = 256`, `n_steps = 21`): measured `var_fx = 1.43e-4`,
  relative error **`0.048`** — well inside the 0.1 tolerance.
- `concordance_metric`: `1.44e-4` → `3.41e-5` (concordance improved).
- `q_variance_dominance_flag`: True (preserved).
- `concordance_verdict`: `concordant` (preserved).

## Deliverable status

- 7 fixes applied; tests green; firewall clean.
- This verification report.
- NO COMMIT (per skill — orchestrator commits after final audit).
