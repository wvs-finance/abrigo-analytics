---
name: e10-gsps-state
description: E10 GSPS (convex multi-currency data-consumption FX-volatility hedge) iteration state as of 2026-05-20 — spec v0.5 accepted after a HALT-DV re-spec to 5 currencies; Phase 0 + Phase 1 (E10.0) complete; Phase 2 (E10.1) is HALT-gated on the user's own observed query-workflow data.
metadata:
  type: project
---

## What E10 is

E10 — Generalized Subscription Payment Stream (GSPS): a **convex (volatility), not
directional** FX hedge for a Web3 data analyst who pays continuously for data access.
The analyst's cost stream is `Q × $0.01 × FX` (Q = monthly query volume, $0.01 = verified
flat x402 per-query price). The hedged risk is the *volatility* of the local-currency
cost. Test: the FX-variance share of `Var(Δlog cost)`, reported as a calibration-
conditional **sensitivity surface** — explicitly **descriptive, not inferential**
(makes no β verdict). E10 is the methods-paper §5 anchor (convex/cost-side
generalization of the streamed-liability primitive; survives any verdict).

## Spec / plan lineage (all in docs/specs, docs/plans)

- Spec: v0.1 (directional, Colombia-only) → v0.2 (convex reframe) → v0.3 (review-driven)
  → v0.4 (demoted to descriptive after G≈8 underpower) → **v0.5 ACCEPTED**
  (`2026-05-20-e10-gsps-v0.5-convex-multicurrency-design.md`) — 5-currency re-spec.
  Five CORRECTIONS blocks (E10-1..E10-5), every pivot a visible record.
- Plan: `docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md` v0.2 (CORR-E10P-1..10).
  Code-agnostic; 7 phases; every task tagged `[brainstorm-judgment]`/`[mechanical-execution]`.

## Accepted spec: v0.6

`docs/specs/2026-05-20-e10-gsps-v0.6-convex-multicurrency-design.md` supersedes v0.5.
CORRECTIONS-E10-6 folded the two converged post-HALT reviewer recommendations:
W-2 dropped the size-broken wild-bootstrap + permutation bands at G≈5, replaced with a
raw 5-currency min–max/IQR spread display (non-statistical); W-1 promoted currency-FE-only
to co-primary descriptive alongside two-way FE (kept primary, estimable: 150 cells,
115 residual DoF). §11 open items 1-2 RESOLVED; 3-4 (surface-grid resolution, ex-ante
exposure assumption) carry forward.

## Execution state as of 2026-05-20

- **Phase 0 — COMPLETE + fully reviewed.** `simulations/e10_gsps/` three-tier scaffold;
  3 firewalls (Stage-2 / fantasy / descriptive-posture) installed + adversarially
  verified; §0 DV record frozen; 6 RED test harnesses. Two-stage review PASSED
  (spec-compliance SPEC-COMPLIANT 14/14; code-quality APPROVED_WITH_NITS, nits fixed).
  Repo-wide note: a stale `core.hooksPath` had disabled ALL pre-commit hooks
  (E4/E7-A/E8/E10) — fixed; the pre-commit hook now chains all four checkers.
- **Phase 1 (E10.0) — COMPLETE + fully reviewed for the 5-currency panel.** HALT-DV
  fired: 3 of 8 original currencies (ZAR/KES/GHS) have NO free machine-readable daily
  ~30-month central-bank FX series (SARB legacy server down; CBK machine-readable ends
  2024-01; BoG behind a bot wall). User-enumerated pivot 2026-05-20: re-spec to the
  **5 available currencies — COP, BRL, EUR, GBP, NGN** (window 2023-11-01→2026-04-30,
  150 cells, **G ≈ 5 clusters**). CORRECTIONS-E10-5 → v0.5; post-HALT 2-way re-review
  (RC + Model QA) both PASS. Delivered code: `utils/fx_ingest_io.py` (5-currency
  ingest, URL-template builders for reproducible re-pull), `modules/regime_break.py`,
  `types/fx.py` (`PANEL_CURRENCIES` 5-tuple, `PANEL_WINDOW`); Tier-2 frozen FX
  snapshots under `data/raw/e10_gsps/`; panel-window artifact
  `notebooks/e10_gsps/diagnostics/E10.0_panel_window.json`. Phase-1 two-stage review
  PASSED (spec-compliance SPEC-COMPLIANT 4/4 after a v0.4→v0.5 re-spec code fix;
  code-quality APPROVED_WITH_NITS, nits fixed). Test suite: 92 passed / 40 RED
  (the 40 are genuine Phase-2-6 NotImplementedError harnesses — no over-building).
- **Phase 2 (E10.1) — NOT STARTED. HALT-gated.** It needs the **user's own observed
  data-query-workflow logs** (the NON-FANTASY simulator-calibration anchor) AND a
  mandatory pre-Phase-2 RC + Model QA review. Phases 3-6 follow Phase 2.

## To resume — what Phase 2 (E10.1) needs

Three things gate Phase 2:
1. **The user's own observed data-query-workflow logs** — volume, protocol mix,
   cadence — the NON-FANTASY anchor that centres the simulator's Q-volume range.
   Without a genuine observed trace, Phase 2 HALTs (HALT-SIM-ANCHOR → NON-RETIREMENT).
2. **The mandatory pre-Phase-2 2-way review** (RC + Model QA) per plan §7.
3. The pre-Phase-2 review also verifies the Phase-1 panel + the v0.6 spec drift-free.

W-1/W-2 are already folded (CORRECTIONS-E10-6 → v0.6) — no longer pending.

## Honest posture

E10 is descriptive-only; G≈5 does not demote it further (v0.4 already abandoned
inferential β claims — there is no inferential rung left for thin G to break). NON-
RETIREMENT remains a valid verdict (Q-variance dominance across the anchored range).
The methods-paper §5 contribution survives any §9 verdict.

## Links

[[review-pair-specialist-by-content]] — the RC+Model QA 2-way review discipline E10 used
[[plan-flags-brainstorm-tasks-nonbypassable-data-gates]] — the data-fetch-gate rule that drove the honest HALT-DV
[[data-visibility-gate-before-modeling]] — the DV gate
[[dune-last-resort-exhaust-free-resources]] — the cost rule E10 is built around
[[pathological-halt-anti-fishing-checkpoint]] — the HALT chain E10.0 ran (disposition → pivot → CORRECTIONS → re-review)
[[bhaduri-laski-riese-concept-bridge]] — PK anchor; E10 = methods-paper §5
