# E10 GSPS v0.4 — Phase 0 Spec-Compliance Review (Stage 1 of 2)

**Reviewer:** spec-compliance reviewer (TestingRealityChecker)
**Date:** 2026-05-20
**Plan reviewed against:** `docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md` §0 + §1 Phase 0 (tasks 0.0–0.13)
**Stage:** 1 of 2 — spec-compliance only. Code-quality is a separate Stage-2 review.

## Verdict

**SPEC-COMPLIANT** — proceed to Stage-2 code-quality review.

All 14 Phase 0 tasks MET. No GAP, no EXTRA. The implementer's completion memo
was verified independently; its claims hold. Default-skeptical posture applied
throughout — all firewalls re-run adversarially, test suite re-run, stubs
inspected line-by-line, scope confirmed Phase-0-only.

## Per-task compliance table

| Task | Deliverable | Status |
|---|---|---|
| 0.0 | §0 DV record frozen at `_DV_RECORD.md`; 8-FX manifest + x402 probe + R6 blueprint hash; DV-PASS-FREE | MET |
| 0.1 | three-tier scaffold; 8 named-error classes; tier-import-discipline test passes | MET |
| 0.2 | disposition template (SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT) | MET |
| 0.3 | types tier — 7 frozen-dataclass containers + 5 Protocols; Hypothesis strategies; round-trip tests pass | MET |
| 0.4 | regime-break failing-test harness — RED | MET |
| 0.5 | NHPP engine failing-test harness — RED | MET |
| 0.6 | decomposition failing-test harness (incl. grid-alignment) — RED | MET |
| 0.7 | surface-grid failing-test harness (incl. interior-crossing) — RED | MET |
| 0.8 | verdict-classifier failing-test harness — RED | MET |
| 0.9 | notebook-execution integration harness — RED | MET |
| 0.10 | anti-fishing module + notebook template; compliance grep test | MET |
| 0.11 | Stage-2 firewall — rejects Panoptic/LP/strike/range/payoff | MET |
| 0.12 | fantasy-firewall — rejects fitted-prior/synthetic FX substitution | MET |
| 0.13 | descriptive-posture firewall — rejects PASS/confirmatory/inferential-β | MET |

**MET count: 14 / 14.**

## Independent verification evidence

### 1. Test suite — claimed 56-pass / 44-RED confirmed

`pytest simulations/e10_gsps/tests/` → **56 passed, 44 failed**, 100 tests.
Matches the memo exactly. `pytest --co` produces **zero collection errors** —
the memo's claim that it fixed a collection-error problem with RED stub modules
holds. The 44 RED failures are genuine:

- All NHPP-engine RED failures terminate in `NotImplementedError: NHPP
  simulation engine lands in Phase 2 (plan task 2.1)` raised from `__post_init__`
  / `__call__` / module functions — not import or collection errors.
- All verdict-classifier RED failures terminate in `NotImplementedError:
  descriptive-verdict classifier lands in Phase 6 (plan task 6.1)`.
- Decomposition / surface-grid / regime-break harnesses likewise RED via
  `NotImplementedError` from genuine stub bodies.
- Notebook-execution harness RED because the 5 analysis notebooks
  (01–05) do not yet exist (Phases 2–6) — honest RED.

The 5 RED stub modules (`regime_break.py`, `nhpp_engine.py`,
`decomposition.py`, `surface_grid.py`, `verdict_classifier.py`) were inspected
line-by-line: **every callable raises `NotImplementedError` and carries zero
logic.** `grep` for value-returning `return` statements found none. The E8
RED-stub pattern is faithfully reproduced. `nhpp_engine` raises even in
`__post_init__`, keeping the construction test RED. No over-building.

### 2. Three firewalls — re-run adversarially, all reject

Baseline `python scripts/e10_firewall_check.py` → exit 0 (`PASS — 37 files
scanned clean`). Each violation injected into a main-line file under
`simulations/e10_gsps/modules/`, checker re-run, then reverted:

| Firewall | Injected violation | Checker exit | Result |
|---|---|---|---|
| Stage-2 (0.11) | `Panoptic LP strike selection range geometry payoff fitting` | 1 | REJECTED |
| Fantasy (0.12) | `FX series from a synthetic generator fitted prior` | 1 | REJECTED |
| Descriptive-posture (0.13) | `PASS confirmatory beta verdict significant at 0.05` | 1 | REJECTED |

Post-revert baseline → exit 0. All injected files removed; working tree clean.
The checker scopes `simulations/e10_gsps/` and `notebooks/e10_gsps/`; `docs/`
is out of scope by construction (spec/plan files exempt — matches plan 0.11
"outside the §13 M-sketch docstrings and explicit spec §13 cross-references").
CI workflow `e10-stage2-firewall.yml` runs the same checker on PR/push to the
E10 scope.

### 3. §0 DV record — honest, matches plan §0 table

`_DV_RECORD.md` is consistent with plan §0:
- DV verdict **DV-PASS-FREE**; status PHASE-0 FROZEN.
- 8-currency central-bank FX manifest: COP/Banrep, BRL/BCB, KES/CBK, NGN/CBN,
  GHS/BoG, ZAR/SARB, EUR/ECB, GBP/BoE — all free public; NGN confined
  post-June-2023 float.
- x402: The Graph Gateway, `exact` scheme, **$0.01 USDC/query flat**, verified
  live 2026-05-20.
- Dune Plus $399/mo recorded as model cap only (`Q_high = 39,900 = $399/$0.01`),
  explicitly NOT a purchase — matches the free-resources rule.
- R6 blueprint SHA-256 + E10 v0.4 spec SHA-256 pinned.
- Simulated quantity declared as Q only; X and the FX multiplier 100% real.
- Honest scoping note: the record freezes the *manifest* at Phase-0 entry; no
  external pull fires until Phase 1. This is correct — Phase 0 acquires no data.

### 4. Scope check — Phase 0 only, no over-building

Confirmed ABSENT (correct — they belong to Phases 1–6):
- `data/panels/e10_gsps_panel.parquet` — absent.
- `scripts/build_e10_gsps_panel.py` — absent.
- `notebooks/e10_gsps/0[1-5]_*.ipynb` analysis notebooks — absent (only
  `_TEMPLATE.ipynb`, `_DV_RECORD.md`, `_TEMPLATE.md` present).
- `simulations/e10_gsps/utils/` — only `__init__.py`, no IO-boundary
  implementation (IO units land Phase 1+).

No FX data acquired, no simulator implemented, no decomposition/surface/verdict
logic written. The `modules/` directory holds exactly 6 files: 5 RED stubs +
`anti_fishing_checks.py` (a Phase-0 deliverable per task 0.10). No EXTRA.

### 5. Git-config concern — fix holds, does not break E4/E7-A/E8

- `git config --get core.hooksPath` → unset (exit 1). The stale path is gone.
- `git rev-parse --git-path hooks` → `.git/hooks` (the default resolves
  correctly).
- `.git/hooks/pre-commit` exists, is executable, and chains **all four**
  firewall checkers: `e4_firewall_check.py`, `e7a_firewall_check.py`,
  `e8_firewall_check.py`, `e10_firewall_check.py`. Unsetting the stale
  `core.hooksPath` restores hook firing for all four iterations simultaneously
  — it does not break E4/E7-A/E8; it *re-enables* them. The adversarial
  firewall injections in §2 above were caught by `e10_firewall_check.py` run
  directly; the pre-commit hook is the same checker, now reachable. Fix
  verified correct.

### Types tier (0.3) detail

7 frozen-dataclass containers exported: `CurrencyDailyFXRow`,
`MonthlyRealizedVarianceCell`, `NHPPIntensityParameters`, `CostStreamTrajectory`,
`ThreeWayDecompositionCell`, `SurfaceGridResult`, `DescriptiveVerdictResult`
(plus support types `LambdaModulationSpec`, `SurfaceGridPoint`,
`DescriptiveVerdict` enum). The `LambdaModulationForm` enum carries exactly the
**five** λ(t) modulation slots (diurnal/weekday, burstiness/overdispersion,
event-spikes, month-end, secular drift) and correctly pins **no form** —
form choice is deferred to Phase 2 tasks 2.3/2.3a as the plan requires.
5 Protocols defined. Hypothesis strategies present at `tests/strategies/`;
`test_types_roundtrip.py` GREEN.

### 8 named-error classes (0.1)

`_errors.py` defines all 7 plan-listed concerns plus a DV-revoked class:
`PanelCurrencyCoverageError`, `RegimeBreakScreenError`, `NHPPCalibrationError`,
`SimulatorAnchorError`, `DecompositionIdentityError`, `SurfaceGridError`,
`DescriptiveVerdictError`, `DataVisibilityRevokedError`. The 8th
(`DataVisibilityRevokedError`) supports the HALT-DV mechanism and is not
over-building — it is required infrastructure, not premature implementation.

## GAP / EXTRA findings

None. No missing deliverable, no over-building.

## Notes for Stage-2 (code-quality) review — not compliance blockers

- `test_anti_fishing_compliance.py` per-notebook checks (10 of 12) are RED
  pending the Phase 2–6 analysis notebooks adopting the template. This is the
  intended Phase-0 RED state per task 0.10 ("Compliance test failing until
  template adopted") — compliant, flagged only so Stage-2 does not mistake it
  for a defect.
- `_DV_RECORD.md` and `_TEMPLATE.md` rely on `<!-- CHECK_ALLOWLIST -->` markers
  to pass the descriptive-posture firewall on legitimate spec-quoting tokens
  (DV-PASS-FREE, the named-and-forbidden retired rungs). The mechanism works;
  Stage-2 may wish to confirm the allowlist comments are minimal and not a
  blanket escape hatch.

---

**Stage-1 verdict: SPEC-COMPLIANT.** All 14 tasks MET. Proceed to Stage-2.
