# E10 GSPS — Phase 3 (E10.2) Completion Memo

**Iteration:** E10 GSPS — convex multi-currency data-consumption FX-vol hedge.
**Phase:** 3 (E10.2) — panel construction + exact §4.2 three-way log-variance decomposition.
**Plan:** `docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md` §1 Phase 3, tasks 3.0–3.5.
**Spec:** `docs/specs/2026-05-20-e10-gsps-v0.6-convex-multicurrency-design.md` v0.6.
**Date:** 2026-05-20.
**Status:** DONE_WITH_CONCERNS (one pre-existing Phase-2.5 firewall hit; see §7).

---

## 1. Files created

Phase-3 deliverables (all new):

| File | Task | Role |
|---|---|---|
| `simulations/e10_gsps/modules/differencing_grid.py` | 3.0 | Common X/Q daily differencing-grid pin + verification (`verify_cell_grid`, `assert_common_grid`, `GridAlignmentReport`). |
| `simulations/e10_gsps/modules/realized_variance.py` | 3.1 / 3.2 | X-side FX realized-variance constructor (spec §3.2 sum-of-squares) + Y-side cost-stream realized-variance constructor; population-variance operator for the §4.2 decomposition. |
| `simulations/e10_gsps/modules/decomposition.py` | 3.3 | Exact §4.2 three-way log-variance decomposition (`decompose_cell`, `ThreeWayDecompositionModule`) — RED stub replaced with the real implementation. |
| `simulations/e10_gsps/modules/panel_construction.py` | 3.0–3.3 | Per-cell panel assembly: X, Y, exact decomposition; zero-Q-day drop on the common grid; panel-grid verification. |
| `simulations/e10_gsps/types/panel.py` | 3.x | `PanelCell` Value-tier container (moved here so the IO-boundary `panel_io` unit does not cross a tier boundary). |
| `simulations/e10_gsps/utils/panel_io.py` | 3.4 | Tier-1 panel emit/read IO boundary (`PanelParquetIO`, fixed parquet schema, schema-drift detection). |
| `scripts/build_e10_gsps_panel.py` | 3.4 | Tier-3 CLI builder — re-derives Tier-1 from frozen Tier-2 FX; `--verify-against-tier1` round-trip check. |
| `simulations/e10_gsps/DATA_PROVENANCE.md` | 3.4 | Committed provenance record (Tier-2 FX hashes, x402 price, Tier-3 contract). |
| `notebooks/e10_gsps/02_panel_decomposition.ipynb` | 3.5 | Panel-decomposition notebook — trio HALT-checkpoints, decision-citation blocks, descriptive-posture banner, pre-pin cell, D1 transparency disclosure. |
| `simulations/e10_gsps/tests/unit/test_panel_construction.py` | TDD | 14 Phase-3 unit tests (grid, realized variance, panel-cell assembly, real-data end-to-end identity). |
| `simulations/e10_gsps/tests/unit/test_panel_io.py` | TDD | 4 Tier-1 emit/read round-trip + schema-drift tests. |
| `notebooks/e10_gsps/diagnostics/E10.2_grid_alignment.json` | 3.0 | Index-alignment verification artifact (150 cells, all aligned). |
| `notebooks/e10_gsps/diagnostics/E10.2_decomposition_summary.json` | 3.3 | Decomposition headline numbers. |

Files modified:

- `simulations/e10_gsps/types/__init__.py` — export `PanelCell`.
- `simulations/e10_gsps/tests/unit/test_decomposition.py` — task-0.6 harness: corrected the
  `test_covariance_term_near_zero_under_qfx_independence` fixtures. The original fixture
  pair was near-perfectly *anti*-correlated despite the docstring claiming "drawn
  independently"; the assertion `|cov_term| <= var_total` is not a universal property
  (Cauchy-Schwarz permits `|2Cov| > var_total` under strong negative correlation). The
  fixtures are now genuinely orthogonal (centred inner product exactly zero), so the
  stated independence property holds; the universal Cauchy-Schwarz bound is asserted too.
  Output artifact only — `data/panels/e10_gsps_panel.parquet` (gitignored).

## 2. Panel dimensions

- **5 currencies** (COP, BRL, EUR, GBP, NGN) × **30 months** (2023-11-01 → 2026-04-30)
  = **150 (currency, month) cells**.
- **0 material-gap cells** — every cell has ≥ 4 positive-Q days surviving the zero-Q-day
  drop (median 10), so the exact decomposition computes for the whole panel.
- NGN confined to its post-June-2023 float window (spec §3.3); all in-window NGN rows
  are post-float, so confinement does not shorten the panel.
- Re-derived from the 5 frozen Tier-2 central-bank FX snapshots, 100% offline.

## 3. The exact §4.2 three-way decomposition — headline result

`Var(Δlog cost) = Var(Δlog FX) + Var(Δlog Q) + 2·Cov(Δlog FX, Δlog Q)`, computed per cell
with the population-variance operator on the common daily differencing grid (zero-Q days
dropped from X and Q on the same surviving index, preserving the common grid).

**FX-variance share `Var(Δlog FX) / Var(Δlog cost)`:**

| | min | median | mean | max |
|---|---|---|---|---|
| panel | 0.00000 | 0.00001 | **0.0002** | 0.0039 |

**Per-currency mean decomposition terms:**

| Currency | FX-variance share | mean Var(Δlog FX) | mean Var(Δlog Q) | mean 2·Cov |
|---|---|---|---|---|
| COP | 0.0001 | 1.18e-04 | 2.52e+00 | +2.88e-03 |
| BRL | 0.0001 | 8.13e-05 | 2.21e+00 | −1.18e-03 |
| EUR | 0.0000 | 3.47e-05 | 1.95e+00 | −3.33e-04 |
| GBP | 0.0000 | 3.21e-05 | 2.30e+00 | +7.79e-04 |
| NGN | 0.0006 | 1.31e-03 | 2.51e+00 | −1.04e-02 |

**Headline:** `Var(Δlog Q)` (≈ 2.0–2.5) dominates `Var(Δlog FX)` (≈ 3e-5 to 1.3e-3) by
**three-to-four orders of magnitude**. The FX-variance share is ≈ 0.02% on average across
the panel; the cross-currency ordering is the expected developed-vs-EM one (NGN highest
FX share, EUR/GBP lowest). This is the **Q-variance-dominance** pattern spec §7 field 7(b)
anticipates — a valid, acceptable, honest outcome (spec §8 anti-fishing carry-forward).
Its cause is the decisively overdispersed calibrated Cox Q-process (E10.1 §3, daily
VMR ≈ 20): a query workflow swinging 1 → 27 queries day-to-day produces a large `Δlog Q`
variance against which the FX log-return variance is small. All 150 cells sit far below
the ex-ante-pinned break-even `s_be = 0.25`.

## 4. Additive-identity verification

The exact additive identity holds **EXACTLY per cell** — max `|identity_residual|`
across all 150 cells is **1.3e-15** (floating-point zero; tolerance 1e-12 in
`decompose_cell`, 1e-9 in the panel test). No leading-order term. The identity is exact
because `cost = Q × $0.01 × FX` with a constant price makes `Δlog cost = Δlog Q + Δlog FX`
an exact pointwise identity; the variance of a sum is exactly the sum of variances plus
twice the covariance. Verified on the common differencing grid (task 3.0 / CORR-E10P-3) —
the harness exercises both aligned and deliberately-mismatched grids, and `decompose_cell`
raises `DecompositionIdentityError` on a grid mismatch rather than silently computing an
inexact identity.

## 5. Tier-3 round-trip

`python scripts/build_e10_gsps_panel.py --verify-against-tier1` → **PASS** for all 150
cells. Tolerances per CORR-E10P-7: `x_realized_variance` (the real FX panel cell) bit-exact;
the fixed-seed simulator-derived cells (`y_realized_variance`, the decomposition terms)
within 1e-9 relative tolerance. The NHPP engine is referentially transparent in
`(currency, year, month)` via its deterministic per-cell seed.

## 6. Test counts

`pytest simulations/e10_gsps/tests/` → **149 passed, 25 failed**.

- **Task-0.6 decomposition harness: 4/4 GREEN** (was RED). Includes the exact-identity
  property on the common grid and the mismatched-grid rejection.
- New Phase-3 tests: `test_panel_construction.py` 14/14 GREEN, `test_panel_io.py` 4/4 GREEN.
- The 25 failures are **all Phase-4/5/6 RED harnesses** out of Phase-3 scope:
  `test_surface_grid.py` (4 — Phase 4), `test_verdict_classifier.py` (8 — Phase 6),
  `test_notebook_execution.py` + `test_anti_fishing_compliance.py` for the 03/04/05
  notebooks (12 — Phases 4–6, notebooks not yet authored), and
  `test_firewalls.py::test_clean_main_line_passes` (1 — see §7).

## 7. Firewall status

All **11 Phase-3 deliverable files are firewall-clean** (Stage-2, fantasy, descriptive-
posture all PASS). The descriptive-posture firewall — the one the Phase-3 task brief
specifically required to keep passing — is fully clean.

**One pre-existing concern (not introduced by Phase 3):** the full firewall scan reports
26 Stage-2 hits in `notebooks/e10_gsps/diagnostics/E10.2.5_break_even_threshold.md` — the
Phase-2.5 ex-ante break-even record. That document legitimately discusses fitted-payoff /
straddle / Panoptic geometry as a spec-§13-resident M-sketch step, but it is a `.md` file
under `notebooks/e10_gsps/` and the firewall scans it. This makes
`test_firewalls.py::test_clean_main_line_passes` fail. **This failure pre-dates Phase 3**
(present in the Phase-3 starting baseline) and is a Phase-2.5 artifact — Phase 3 neither
caused it nor is scoped to fix it. Recommended disposition: the Phase-2.5 break-even
record should carry per-line `CHECK_ALLOWLIST` markers on its §13 M-sketch lines, or the
firewall's `_is_scannable_file` should exclude `notebooks/e10_gsps/diagnostics/` (a
diagnostics-doc directory), as a Phase-2.5 follow-up. Flagged here for the orchestrator.

## 8. HALT awareness

No HALT fired. HALT-SURFACE-UNCOMPUTABLE was assessed: the calibrated Cox Q-process
produces frequent zero-query days (≈ 51% of raw daily observations), which would make a
naive daily-grid `Δlog cost` undefined. The Phase-3 resolution — drop the zero-Q days from
X and Q on the *same* surviving index — preserves the common grid and keeps the exact
identity intact for every surviving consecutive pair. Every one of the 150 cells retains
≥ 4 surviving positive-Q days, so the decomposition computes panel-wide; 0 cells are
material-gap. The decomposition itself is not the PARTIAL dimension — the OPEN E10.1
calibration items (`Q_low` NaN, month-end magnitude 0.0) carry forward to the Phase-4
surface-characterization bracket, unchanged.

## 9. Exit criterion

Met. The 5-currency × 30-month panel (150 cells) is assembled; per-(currency, month) X, Y,
and the exact three-way decomposition computed; the additive identity verified exact per
cell (max residual 1.3e-15); Tier-1 parquet emitted; Tier-3 round-trip passes within
tolerance; notebook 02 authored and executes headless. Phase 3 (E10.2) closes here. Phase
4 (surface characterization) is NOT started.
