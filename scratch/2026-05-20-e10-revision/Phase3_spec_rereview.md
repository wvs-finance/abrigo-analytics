# E10 Phase 3 (E10.2) — Stage-1 Spec-Compliance RE-REVIEW (closure)

**Reviewer role:** spec-compliance reviewer, Stage 1 of 2 (code-quality is Stage 2).
**Scope:** confirm CORRECTIONS-E10-7 closed the single GAP from the first Phase-3
review (task 3.3, spec-unpinned zero-Q-day handling). Spec v0.7.
**Date:** 2026-05-20. **Posture:** default-to-finding-gaps; read-only; pytest + firewall run.
**First review:** `scratch/2026-05-20-e10-revision/Phase3_spec_review.md` — verdict NOT-COMPLIANT, 1 GAP.

---

## Verdict

**SPEC-COMPLIANT.** The single GAP (task 3.3) is **CLOSED**. The two divergent FX
objects are reconciled to ONE canonical X. No new GAP introduced. CORRECTIONS-E10-7
is a contradiction-forced construction-grid pin, not a result-shop — the headline
Q-variance-dominance result is confirmed unchanged. Phase 3 proceeds to Stage-2
code-quality review.

**GAP closure: task 3.3 → CLOSED.**

## Per-task table

| Task | Status | Note |
|---|---|---|
| 3.0 — common X/Q differencing grid | **MET** | Unchanged; `decompose_cell` still rejects mismatched lengths with `DecompositionIdentityError`. |
| 3.1 — X-side realized-variance constructor | **MET** | `realized_variance_sum` of Δlog(FX); now computed on the surviving non-zero-Q-day index per the v0.7 pin. |
| 3.2 — simulator-run Y | **MET** | Y = `realized_variance_sum(cost_returns)` on the surviving index; spec §5.2 now pins this grid. |
| 3.3 — exact §4.2 decomposition + zero-Q handling | **MET** *(was GAP)* | Closed by CORRECTIONS-E10-7 — see §1. Zero-Q drop spec-pinned; FX objects reconciled; identity exact (residual 1.33e-15). |
| 3.4 — Tier-1 emit + Tier-3 builder | **MET** | Unchanged from first review. |
| 3.5 — notebook 02 | **MET** | Unchanged from first review. |

**MET count: 6 / 6. GAP: 0. EXTRA: 0.**

---

## 1. GAP closure — task 3.3 (the load-bearing finding)

**Check 1 — spec v0.7 pins the gapped grid.** CONFIRMED. Spec v0.7 §3.2, §5.2, and
§4.2 each carry an explicit CORRECTIONS-E10-7 amendment block pinning X, Y, and the
three-way decomposition to "the **daily grid restricted to non-zero-Q days** — the
common surviving index." All three sections state the drop is "**forced by the log
domain** (Δlog of a zero is undefined), not a discretionary filter." The ~51%
zero-Q-day prevalence is stated in §0.7, §3.2, and §6.3 (attributed to the upstream
`[brainstorm-judgment]` Cox-process daily-VMR≈20 calibration). The plan task 3.3 text
now carries the same pin plus a retroactive note that the `[mechanical-execution]`
tag, as executed, had carried an unflagged modeling decision — honest disclosure.

**Check 2 — the two FX objects reconciled to ONE canonical X.** CONFIRMED. In
`panel_construction.build_panel_cell`: `_drop_zero_query_days` filters Q and FX on
the SAME index (line 156); `fx_returns = daily_log_returns(fx_surv)` (line 166);
`x_realized_variance = realized_variance_sum(fx_returns)` (line 167) — the X cell is
recomputed on the surviving grid, NOT carried over from the full-daily-grid
`fx_cell`. `decompose_cell` is handed the same `fx_returns` (line 205), so
`decomposition.var_fx = population_variance(fx_returns)` is computed from the
identical surviving Δlog FX series. `PanelCell.x_realized_variance` and
`decomposition.var_fx` differ only by the documented sum-vs-population convention —
NOT by grid. `types/fx.py` (lines 60-64) and `types/panel.py` (lines 22-31)
docstrings both state the v0.6 two-divergent-FX-objects condition is CLOSED and that
`MonthlyRealizedVarianceCell` is no longer carried onto the panel cell as X. No
divergent full-daily-grid FX object remains in the panel path.

**Check 7 — exact §4.2 identity holds on the reconciled panel.** CONFIRMED.
`data/panels/e10_gsps_panel.parquet` (150 cells): max `|identity_residual|` =
**1.33e-15** (floating-point zero). `decompose_cell` enforces `_IDENTITY_TOL = 1e-12`
and raises on violation — never silently computes an inexact identity. The identity
holds exactly because X and Q are dropped on the SAME surviving index.

The GAP is fully dispositioned per option (a) of the first review's required action
— a CORRECTIONS block folded into the spec with reviewer-driven sign-off.

---

## 2. Anti-fishing — CORRECTIONS-E10-7 is contradiction-forced, result unchanged

**Check 3.** CONFIRMED. Spec v0.7 §0.7's "What CORRECTIONS-E10-7 does NOT do" block
states plainly the gapped-grid pin is "the **contradiction-forced resolution** — the
daily-grid decomposition is *infeasible* on ~51% of cells because `Δlog(0)` is
undefined, full stop. It is **NOT** a post-hoc grid-swap chosen to chase a different
FX share." It explicitly affirms the §9 verdict ladder is untouched, the §7 pre-pin
seven fields are FROZEN, and the N_MIN/POWER_MIN/MDES anti-fishing invariants are
unrelaxed. This is consistent with the first review's §2 honest-computation finding
(the drop biases neither direction of the FX share).

**Headline result IS unchanged — verified independently on the reconciled panel:**
mean `var_q` ≈ **2.297**, mean `var_fx` ≈ **3.16e-4**, implied FX share ≈ **0.014%**.
This matches the first review's reported var_q ≈ 2.30, var_fx ≈ 3.16e-4, FX share
≈ 0.015% (rounding). Q-variance dominance stands — the CORRECTIONS pinned the
construction without altering the result, exactly as §0.7 claims.

---

## 3. Plan annotation and firewall-test fix

**Check 4 — task 3.3 plan annotation.** CONFIRMED. CORR-E10P-12 is recorded as a
full CORRECTIONS row in the plan (line 28) citing the Phase-3 review, the
HALT-SPEC-DATA-CONTRADICTION trigger, and the user-enumerated pivot. Plan task 3.3
(line 315) is amended in place with the spec-pinned zero-Q handling and an explicit
retroactive note.

**Check 5 — firewall-test fix.** CONFIRMED CORRECT. The fix is **per-line
`<!-- CHECK_ALLOWLIST: ... -->` markers** on the legitimate §13 M-sketch lines of
`notebooks/e10_gsps/diagnostics/E10.2.5_break_even_threshold.md` — 25 markers, each
annotated "legitimate spec-§13 M-sketch payoff-geometry quote (Phase-2.5 break-even
record)." This is NOT a firewall broadening and NOT a directory exclusion: the
firewall pattern set is unchanged and the diagnostics directory remains scanned. The
allowlist marks only the specific legitimate lines, leaving the firewall live for
any genuine Stage-2 leakage elsewhere.

**Check 6 — independent verification.**
- `pytest simulations/e10_gsps/tests/` → **150 passed, 24 failed**. The 24 failures
  are all out-of-scope Phase 4-6 RED harnesses: `test_surface_grid` (Phase 4),
  `test_verdict_classifier` (Phase 5), and the 03/04/05 notebook
  `exists`/`executes_headless`/`descriptive-poster-banner`/`pre-pin-locked-block`
  integration tests (Phase 4-6). No Phase-3 test fails. The 27 firewall tests
  (including `test_clean_main_line_passes`) all PASS — the pre-existing firewall
  failure from the first review is now closed. No over-building observed: the 24
  RED harnesses are pre-committed failing-test scaffolds, not premature
  implementations.
- `python scripts/e10_firewall_check.py` → **"E10 firewall PASS — 54 files scanned
  clean."**

---

## 4. Conclusion

All seven closure checks pass. The single GAP from the first Phase-3 review is
CLOSED via CORRECTIONS-E10-7, properly recorded as a visible spec block, a plan
CORRECTIONS row, and reconciled code. The two FX objects are now ONE canonical
gapped-grid X. The headline Q-variance-dominance result is independently confirmed
unchanged. No new GAP. The firewall-test fix is a correct per-line allowlist, not a
weakening.

**Phase 3 (E10.2) is SPEC-COMPLIANT** and may proceed to the Stage-2 code-quality
review.
