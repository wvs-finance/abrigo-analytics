# E10 GSPS — Phase 2 (E10.1) Completion Memo

**Phase:** 2 — E10.1, the load-bearing R6 NHPP query-workflow simulation
engine build.
**Date:** 2026-05-20.
**Scope executed:** plan v0.4 §1 Phase 2 tasks 2.1, 2.2, 2.3 / 2.3a /
2.3b, 2.4. STOPPED at Phase 2 exit (no Phase 2.5 / Phase 3+).
**Status:** DONE_WITH_CONCERNS — Phase-2 exit criterion met; one
spec-anticipated PARTIAL fired on the two OPEN calibration items.

---

## 1. Files created / modified

**Created:**
- `simulations/e10_gsps/tests/unit/test_nhpp_engine_phase2.py` — 15
  behaviour-focused Phase-2 tests (STRICT TDD for the task-2.1
  implementation choices beyond the task-0.5 RED contract).
- `notebooks/e10_gsps/01_simulator_calibration.ipynb` — the task-2.4
  calibration notebook (21 cells, trio HALT-checkpoints, decision-
  citation blocks, descriptive-posture banner, pre-pin LOCKED block).
- `notebooks/e10_gsps/dispositions/E10.1_proxy_research_PARTIAL.md` —
  the task-2.2 proxy-research-gate disposition memo.

**Modified:**
- `simulations/e10_gsps/modules/nhpp_engine.py` — the RED stub replaced
  by the real R6 NHPP engine (the load-bearing build).
- `notebooks/e10_gsps/diagnostics/E10.1_calibration_note.md` — new §0
  Phase-2 build addendum folding in the pre-Phase-2 review's five
  forward-carried recommendations (A1-A5).
- `notebooks/e10_gsps/diagnostics/E10.0_panel_window.json` — RC O-1:
  stale v0.5 spec citation refreshed to v0.6.

## 2. The NHPP engine design

**Mechanism — Cox / doubly-stochastic NHPP (calibration note §3.3,
RATIFIED by the pre-Phase-2 Model QA review).** The arrival process is a
deterministic intensity envelope λ_det(t) carrying the five §6.3
modulations, multiplied by a *random* per-day sprint-intensity Λ_d. The
day-count is `Poisson(λ_det(d) × Λ_d)`. The doubly-stochastic Λ_d layer
is what produces the trace's daily VMR ≈ 20 — a pure NHPP is Poisson-
equidispersed conditional on λ(t) and cannot.

**Gamma primary / log-normal sensitivity arm (Model QA Strong-1).** The
mechanism *class* is trace-anchored; the *Gamma* mixing law within it is
a conjugacy default, not discriminable from log-normal at n≈12-28 daily
counts. The engine carries both:
- `overdispersion_mechanism="cox"` — Gamma-mixed sprint-intensity
  background (PRIMARY); Gamma-mixed Poisson ⇒ NB marginal, so the §3.4
  fallback nests.
- `overdispersion_mechanism="cox_lognormal"` — log-normal-mixing
  background (the §4.3 SENSITIVITY arm).
- `overdispersion_mechanism="negative_binomial"` — the §3.4 NB-marginal
  fallback (shares the Gamma marginal).
An empty / unrecognised mechanism raises `NHPPCalibrationError` at
construction — no default-priors escape hatch.

**Modulations 2 + 3 unified.** Per calibration note §4.2/§4.3, burstiness
(modulation 2) and event spikes (modulation 3) are two readouts of ONE
mechanism. Λ_d is a two-component mixture — a moderate-variance
*background* on most days, a heavy-tailed *spike* on a sparse Bernoulli
fraction — and the whole mixture is the single overdispersion mechanism
(not two independent multipliers). The mixture is affine-rescaled to
mean 1 and to the variance that pins the day-count VMR to a swept
`vmr_target` (VMR ≈ 20 is the swept-range *centre*, Model QA Strong A2,
exposed as a constructor parameter — not a hard target).

**The other three modulations:** modulation 1 = weekday/weekend weight ×
a locked two-peak diurnal envelope (`diurnal_hourly_envelope()`);
modulation 5 = a log-linear secular-drift weight; modulation 4 = an
end-of-month bump whose *shape* is wired and whose *magnitude* defaults
to 0.0 (the OPEN item).

**Q ⊥ FX (spec §6.4):** the engine accepts the real FX path but the Cox
arrival process never conditions on it; the seed is derived from
`(currency, year, month)`. Two runs against different FX paths at the
same cell produce identical Q. `cost = Q × $0.01 × FX` is the only place
FX enters. Cap-wait / session-cap R6 logic discarded (x402 has no cap).

**`calibrated_intensity_parameters()`** — the canonical trace-anchored
parameter factory (calibrated `lambda_0` reproducing the ~60-130/mo
centre; `q_high = 39,900`; `q_low = NaN` unpinned marker).

Discipline: `modules`-tier frozen-dataclass stateless callable + free
pure functions; no mutable state; no `..utils` import (tier-import
discipline test green). Ruff clean.

## 3. Calibration result

- **Q-volume centre** — the calibrated Cox process reproduces the
  anchored ~60-130 priceable-queries/month band (calibration note §2);
  the §4.3 surface sweeps the whole envelope (Model QA Strong A3).
- **Overdispersion** — the calibrated engine produces a monthly-aggregate
  Fano factor well above the equidispersed-Poisson value of 1 under all
  three locked mechanisms (verified in the notebook).
- **Four λ(t) modulations LOCKED and own-trace-anchored** (diurnal/
  weekday, burstiness, event spikes, secular drift); modulation 4's
  magnitude OPEN.
- **`Q_high` = 39,900/mo** — pinned off the $399 Dune-Plus price, not the
  trace.

## 4. Proxy-research outcome (task 2.2 / 2.3b non-bypassable gate)

The proxy-research data-fetch gate was evaluated. Proxies (The Graph
Studio/billing docs; RPC-provider free-tier characterizations; Dune
usage docs; the project's own `x402_subgraph_design_space.md`) are
**partially reachable** but **pin no numeric value** for either OPEN
item:

- **`Q_low`** — UNPINNED. The free tier's qualitative limit is a
  *capability* threshold (`trace_*`/archive/large-`eth_getLogs`/cross-
  protocol-curation need), NOT a query-volume threshold; The Graph
  publishes no per-second rate limit; the metadata-only trace cannot
  observe capability need. `Q_low` cannot be expressed as a scalar.
  Engine carries it as `NaN`.
- **Month-end seasonality magnitude (modulation 4)** — UNPINNED. No
  public statistic discloses a month-end reporting-cadence magnitude.
  Engine default `month_end_bump_magnitude = 0.0` (documented no-op).

Per CORR-E10P-8 / RC WEAK-2 / spec §9 this routed the two items to
**PARTIAL** — the §4.3 surface degrades from a band to a centre-only
characterization on those two dimensions. **No flat-fill, no fabricated
bracket.** Both items were flagged non-HALT and spec-anticipated by the
calibration note and both pre-Phase-2 reviews. Disposition:
`notebooks/e10_gsps/dispositions/E10.1_proxy_research_PARTIAL.md`.

**No HALT/PARTIAL on anchor grounds** — the observed trace is genuine
and non-trivial; HALT-SIM-ANCHOR did not fire.

## 5. Test counts

Baseline (Phase-2 entry): **40 failed, 92 passed.**
Phase-2 exit: **32 failed, 115 passed** (+23 passing, −8 failed).

The +23: the 4 task-0.5 RED NHPP tests now green; 15 new Phase-2 NHPP
behaviour tests green; 2 notebook-01 tests (exists + headless execute)
green; 2 anti-fishing-compliance tests for notebook 01 (banner + pre-pin
LOCKED block) green.

The remaining 32 failures are ALL out-of-Phase-2 scope: `test_decomposition`
(4, Phase 3), `test_surface_grid` (4, Phase 4), `test_verdict_classifier`
(8, Phase 6), and 16 notebook-execution + anti-fishing parametrizations
for notebooks 02-05 (Phases 3-6). None is a Phase-2 regression. The
task-0.5 NHPP harness — the Phase-2 RED contract — is fully green.

## 6. Firewall status

`python scripts/e10_firewall_check.py` → **PASS — 44 files scanned
clean.** All three firewalls (Stage-2 / fantasy / descriptive-posture)
clean. The descriptive-posture firewall passes — no inferential-β
language in the engine or the calibration notebook.

## 7. Concerns (the DONE_WITH_CONCERNS qualifier)

1. **PARTIAL on the two OPEN items.** Spec-anticipated and non-HALT, but
   it is carried forward: the §4.3 surface will be a centre-only
   characterization on the `Q_low` / month-end dimensions unless the
   user sources non-public telemetry (pivot option 2 in the disposition
   memo).
2. **VMR-target calibration at high λ_0.** The day-count VMR pins
   cleanly to the swept target at the trace-anchored arrival rate
   (~5/day → VMR ≈ 25, within the swept range around 20). At a much
   higher synthetic λ_0 the pooled daily VMR overshoots because the
   weekday/weekend bimodality (locked modulation 1) adds genuine
   between-day variance on top of the Cox layer. This is correct
   behaviour — modulation 1 *should* inflate the daily VMR — and VMR ≈ 20
   is explicitly a swept-range centre, not a hard target (Model QA
   Strong A2). The calibration runs at the trace-anchored rate.
