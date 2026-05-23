# E10 Phase 3 Code Review — I-1 Remediation Backlog

**Status:** OPEN (deferred — non-blocking)
**Source:** `scratch/2026-05-20-e10-revision/Phase3_quality_review.md`
**Logged:** 2026-05-21

## Finding

`_MIN_SURVIVING_DAYS = 2` in `simulations/e10_gsps/modules/panel_construction.py:82`
admits a degenerate cell. A cell with exactly 2 surviving positive-Q days yields
exactly 1 daily log-return; `population_variance` of a length-1 series returns
`0.0`. The result is a cell with `material_gap = False` but
`var_total = var_fx = var_q = cov_term = 0.0` and `fx_variance_share = NaN` —
the §4.2 identity check passes vacuously (0 = 0+0+0) and an information-free
cell enters the panel as a real cell.

## Why deferred

- Reviewer verdict: APPROVED_WITH_NITS (non-blocking). All 150 production panel
  cells have far more than 3 surviving days, so no real cell currently hits the
  degenerate condition.
- The fix is **not** a pure code change — spec v0.7 pins the threshold at 2 in
  two places (§4.2 prose and §9 verdict ladder). A unilateral code change to
  threshold = 3 would silently drift the runtime from the spec, violating the
  anti-fishing/spec-vs-code-coherence invariant.
- Correct remediation requires a CORRECTIONS-E10-8 amendment cycle (spec edit
  + 2-way review + code patch + re-review) — appropriate post-Phase 4 once the
  surface is in hand and the threshold's effect on the verdict ladder is fully
  in scope.

## Remediation plan (when scheduled)

1. Draft CORRECTIONS-E10-8 paragraph in `docs/specs/2026-05-20-e10-gsps-v0.7-convex-multicurrency-design.md`:
   raise threshold to 3 (≥2 log-returns ⇒ non-degenerate population variance);
   update §4.2 prose and §9 PARTIAL clause; add ledger entry.
2. RC + Model QA 2-way closure-only re-review of v0.7 + amendment.
3. Code patch in `panel_construction.py:82` (`= 2` → `= 3`) + docstring at
   `panel_construction.py:42` + `types/panel.py:36`.
4. Confirm panel-build re-run is a no-op (all 150 cells unaffected); commit
   under CORRECTIONS-E10-8.

## Related minor findings (deferred together)

- Duplicated `_drop_zero_query_days` helper across two modules with
  inconsistent error typing.
- Dead full-grid `build_fx_variance_cell` computation in the builder.
- Verbatim re-stamp of `identity_residual`.
- `_rel_close` scale floor of 1.0 degrading the 1e-9 check to absolute tolerance.
- Unvalidated `type: ignore` in `panel_io.read`.

These travel with the I-1 amendment.
