# E10 Phase 3 (E10.2) — Stage-1 Spec-Compliance Review

**Reviewer role:** spec-compliance reviewer, Stage 1 of 2 (code-quality is Stage 2).
**Scope:** Phase 3 tasks 3.0–3.5 vs spec v0.6 §3/§4.2/§5/§3.3 and plan tasks 3.0–3.5.
**Date:** 2026-05-20. **Posture:** default-to-finding-gaps; read-only; pytest run.

---

## Verdict

**NOT-COMPLIANT** (one GAP — task 3.3 zero-Q-day construction is an undisclosed
spec-unpinned modeling choice that silently changes the grid the headline share
is computed on). All other tasks MET. The Q-variance-dominance headline is
**honestly spec-computed in its arithmetic** but **rests on an unpinned
construction the spec never sanctioned** — see the honest-computation verdict.

## Per-task table

| Task | Status | Note |
|---|---|---|
| 3.0 — common X/Q differencing grid | **MET** | `differencing_grid.py` pins the daily-FX-trading-day index; `verify_cell_grid` / `verify_panel_grids` raise on mismatch; `E10.2_grid_alignment.json` emitted (150 cells, all aligned). |
| 3.1 — X-side realized-variance constructor | **MET** | `realized_variance_sum` is the within-month sum of squared daily log-returns (spec §3 sum convention); NGN confined upstream by `regime_break`. |
| 3.2 — simulator-run Y | **MET** | `build_cost_variance_cell` differences `cost = Q × $0.01 × FX` on the real FX path; Y is the sum-of-squares realized variance of Δlog(cost). |
| 3.3 — exact §4.2 decomposition | **GAP** | Arithmetic is exact (residual 1.3e-15). But the decomposition runs on a **zero-Q-day-dropped, gapped index** that the spec never pins — see §1 below. |
| 3.4 — Tier-1 emit + Tier-3 builder | **MET** | `panel_io.py` + `build_e10_gsps_panel.py`; round-trip PASS per CORR-E10P-7 (FX bit-exact, sim cells 1e-9). DATA_PROVENANCE.md committed with Tier-2 hashes. |
| 3.5 — notebook 02 | **MET** | Trio checkpoints, decision-citation blocks, descriptive-posture banner, D1 block present; executes headless. |

**MET count: 5 / 6. GAP: 1 (task 3.3). EXTRA: 0.**

---

## 1. The GAP — task 3.3 zero-Q-day drop (the load-bearing finding)

Spec §3.2 pins X as the within-month sum of squared **daily** log-returns; §5.2
pins Y the same on the same **daily** grid; §4.2 states the identity for `Var(·)`
on that grid. The plan task 3.3 is tagged `[mechanical-execution]` — "no
modeling-assumption choice is open here (the sum-vs-mean convention and the
differencing grid are fixed, not chosen)."

The calibrated Cox Q-process produces zero queries on ~51% of days. `Δlog cost`
is undefined on a zero-Q day. The implementer's resolution (`panel_construction.py`
`_drop_zero_query_days`) drops zero-Q days from X **and** Q on the same surviving
index, then differences the survivors. The completion memo §8 describes this in
two sentences and the notebook mentions it once.

Why this is a GAP, not an EXTRA or a MET:

1. **The spec never pinned a zero-Q handling.** The plan asserted the grid was
   "fixed, not chosen" — yet the implementer *did* make a consequential
   construction choice. A spec-unpinned modeling decision that materially shapes
   the headline result is, per the anti-fishing discipline, a HALT-and-disposition
   item, not a silent `[mechanical-execution]` step.
2. **The decomposition is computed on a gapped, irregular index** — not the daily
   grid §3.2/§5.2/§4.2 pin. A surviving pair can span a multi-day gap (sprint day
   → next sprint day). `Δlog FX` over a 4-day gap is not the daily `Δlog FX` the
   spec defines; `Var(Δlog FX)` on the gapped index is a different object.
3. **Divergence inside `PanelCell`.** `x_realized_variance` is the spec-§3.2 X
   (full daily grid, sum-of-squares). The headline `fx_variance_share` uses
   `decomposition.var_fx` (population variance on the gapped surviving grid).
   These are two different FX objects; the panel carries both without the
   notebook/memo reconciling them or flagging that the headline share's numerator
   is NOT the §3.2 X cell.

This must be dispositioned: either (a) a CORRECTIONS block pinning the zero-Q
handling into the spec with explicit reviewer sign-off, or (b) a documented
construction-decision note with the bias analysis below, surfaced to the user.
It cannot stand as an unannounced `[mechanical-execution]` detail.

---

## 2. Honest-computation verdict — is Q-variance dominance honest?

**Verdict: YES, the Q-variance-dominance result is the honest output of the
pinned construction — it is NOT engineered to shrink the FX share — BUT the
specific magnitude (≈0.02%) is conditional on the unpinned zero-Q drop and that
conditionality is under-disclosed.**

Reasoning:

- **Direction of the drop bias is AGAINST, not for, a small FX share.** Dropping
  zero-Q days removes the lowest-Q observations and keeps the large sprint-to-
  sprint jumps, *inflating* `Var(Δlog Q)`. But it also forces `Δlog FX` onto the
  same gapped index, *inflating* `Var(Δlog FX)` (multi-day FX moves). The drop
  does not selectively suppress the FX numerator. Nothing in the construction
  pushes the FX share *down* beyond what the honest data yield. The implementer
  did not tweak anything to make the FX share look smaller.
- **The dominance is structurally sourced and disclosed.** Memo §3 attributes it
  to the Cox process daily VMR ≈ 20 (1 → 27 query swings) — `Var(Δlog Q)` ≈ 2.0–2.5
  vs `Var(Δlog FX)` ≈ 3e-5–1.3e-3. That is an E10.1 calibration consequence, an
  upstream pre-pinned `[brainstorm-judgment]` choice (overdispersion mechanism),
  not a Phase-3 manipulation.
- **Q-variance dominance is an explicitly sanctioned outcome** (spec §7 field 7b,
  §8 anti-fishing carry-forward, §9 NON-RETIREMENT rung). It was not engineered
  away — it is reported plainly. The cross-currency ordering (NGN highest, EUR/GBP
  lowest) is the expected EM-vs-DM pattern, a sanity check the result passes.
- **The identity remains exact after the drop** (max residual 1.3e-15) because
  X and Q are dropped on the *same* surviving index — verified independently:
  the 4 task-0.6 harness tests and the 14 panel tests pass, including the
  real-data 150-cell end-to-end identity check.

So the *sign and order-of-magnitude* of the headline are honest. The residual
concern is **only** that the precise share number is computed on a grid the spec
did not pin, and the memo does not frame the 0.02% as conditional on that choice.

---

## 3. Other honesty checks

- **Sum-vs-mean convention.** X uses `realized_variance_sum` (sum of squares,
  spec §3). The decomposition internally uses `population_variance` — spec §4.2
  is explicitly stated for `Var(·)`, and the module docstring discloses both
  conventions and why. This is spec-consistent, not a divergence: §3.2 X and the
  §4.2 `var_fx` are deliberately different objects per the spec text. MET.
- **Task-0.6 fixture correction is LEGITIMATE, not a weakening.** The original
  `test_covariance_term_near_zero_under_qfx_independence` fixtures were
  near-perfectly anti-correlated (`[0.01,-0.01,...]` vs a sign pattern with a
  large negative centred dot-product) while the docstring claimed independence —
  a genuine fixture bug. The new fixtures
  `fx_lr=[0.01,-0.01,...]`, `q_lr=[0.02,0.02,-0.02,-0.02,...]` have a centred
  inner product of exactly zero (verified: Cov = 0), so the independence property
  it claims to test is now actually exercised. The test was also *strengthened* —
  it now additionally asserts the universal Cauchy-Schwarz bound. The old
  `|cov| <= var_total` assertion was genuinely not a universal property. The
  correction is sound.
- **`test_firewalls.py::test_clean_main_line_passes` failure — CONFIRMED
  pre-existing, not a Phase-3 regression.** All 26 hits are in
  `notebooks/e10_gsps/diagnostics/E10.2.5_break_even_threshold.md` (Phase-2.5
  break-even doc) — `fitted-payoff`, `Panoptic`, `LP`, `strike/range` tokens that
  legitimately belong to the §13 M-sketch. The file is a Phase-2.5 artifact
  (untracked, predates Phase 3). All 11 Phase-3 deliverable files are
  firewall-clean. Disposition (allowlist markers or `_is_scannable_file`
  exclusion of the diagnostics dir) is a Phase-2.5 follow-up — correctly out of
  Phase-3 scope.
- **Test counts verified independently.** `pytest simulations/e10_gsps/tests/`
  → 149 passed, 25 failed. The 25 are all Phase-4/5/6 RED harnesses
  (`test_surface_grid`, `test_verdict_classifier`, 03/04/05 notebook
  execution/compliance) plus the one pre-existing firewall failure. Phase-3
  scope (`test_decomposition`, `test_panel_construction`, `test_panel_io`) is
  22/22 GREEN. Matches the memo.

---

## 4. Required action before SPEC-COMPLIANT

One item blocks compliance:

1. **Disposition the zero-Q-day drop (task 3.3 GAP).** Either fold a
   CORRECTIONS block into the spec pinning the zero-Q handling and the gapped-
   grid decomposition with reviewer sign-off, OR produce a construction-decision
   note that (i) states the drop is a spec-unpinned Phase-3 choice, (ii) carries
   the bias analysis (§2 above — the drop does not bias the FX share downward),
   (iii) reconciles `PanelCell.x_realized_variance` (§3.2 X) vs
   `decomposition.var_fx` (gapped-grid §4.2 term) and discloses which the
   headline share uses, (iv) is surfaced to the user. Until dispositioned the
   `[mechanical-execution]` tag on task 3.3 is incorrect — this was a judgment.

No other gaps. Once the disposition lands, Phase 3 is spec-compliant and may
proceed to Stage-2 code-quality review. The headline Q-variance-dominance result
is honestly computed in substance; the disclosure of its grid-conditionality is
the outstanding deficiency.
