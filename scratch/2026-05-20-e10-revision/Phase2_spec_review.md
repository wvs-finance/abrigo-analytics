# E10 Phase 2 (E10.1) — Stage-1 Spec-Compliance Review

**Reviewer posture:** spec-compliance only (Stage 1 of 2). Default to finding gaps.
**Date:** 2026-05-20
**Scope:** plan v0.4 Phase 2 tasks 2.1–2.4 vs the E10.1 calibration note (build
contract), spec v0.6 §6, and the 5 forward-carried pre-Phase-2 recommendations.

## Verdict

**SPEC-COMPLIANT** — proceed to Stage-2 code-quality review.

Tasks 2.1–2.4 all MET. No GAP. No EXTRA. The PARTIAL on the two OPEN items
(`Q_low`, month-end magnitude) is spec-anticipated (CORR-E10P-8 / spec §6.2 /
§2.4 / §9) and honestly recorded — it is NOT a GAP.

## Per-task table

| Task | Status | Notes |
|---|---|---|
| 2.1 — build the NHPP engine | **MET** | Cox/doubly-stochastic with Gamma-mixed sprint-intensity; 5 §6.3 slots wired; Q⊥FX in primary; cap-wait/session-cap discarded; 4 task-0.5 RED tests green. |
| 2.2 — calibrate to anchor; proxy gate | **MET** | Centre calibrated (~60-130/mo); proxy gate honoured → PARTIAL honestly routed; disposition memo enumerates pivots; no flat-fill. |
| 2.3 / 2.3a / 2.3b — λ(t) forms + Cox + Q_low | **MET** | 4 locked λ(t) forms + Cox mechanism implemented as the calibration note specifies, not re-decided; Q_low carried NaN under PARTIAL. |
| 2.4 — `01_simulator_calibration.ipynb` | **MET** | NHPP fit diagnostics, calibrated process vs anchor, decision-citation blocks, descriptive-posture banner, pre-pin LOCKED block, trio HALT-checkpoints. |

**MET count: 4 of 4.**

## Independent verification

1. **`pytest simulations/e10_gsps/tests/`** — confirmed **115 passed / 32 failed**.
   The 32 RED are all out-of-Phase-2 scope: `test_decomposition.py` (4, Phase 3),
   `test_surface_grid.py` (4, Phase 4), `test_verdict_classifier.py` (8, Phase 6),
   and 16 notebook-execution + anti-fishing parametrizations for notebooks 02-05
   (Phases 3-6). No Phase-2 file is red. The 19 NHPP-engine tests
   (`test_nhpp_engine.py` 4 RED-contract + `test_nhpp_engine_phase2.py` 15
   behaviour) are all green. No over-building into Phase 3+.
2. **`python scripts/e10_firewall_check.py`** — `PASS — 44 files scanned clean`,
   exit 0. Descriptive-posture firewall passes; no inferential-β language in the
   engine or notebook.
3. **Scope check** — Phase 2 built ONLY the NHPP engine + calibration notebook +
   PARTIAL disposition + calibration-note §0 addendum. No Phase 2.5 break-even
   pinning, no Phase 3 decomposition, no Phase 4 surface code. Completion memo
   states "STOPPED at Phase 2 exit"; verified independently — Phase 3-6 modules
   remain RED stubs.
4. **The PARTIAL** — confirmed spec-anticipated. Calibration note §0-A5 / §4.4 /
   §5 / §7, spec §6.2 (routes bracket magnitudes to proxy research) and §2.4
   (defers `Q_low` to a proxy-corroborated rule), and CORR-E10P-8 all anticipate
   it. `E10.1_proxy_research_PARTIAL.md` records the proxies attempted, the
   honest non-pinning outcome, and enumerates 3 user pivots. `Q_low` carried as
   `float("nan")` (visible unpinned marker); `month_end_bump_magnitude` default
   `0.0` (documented no-op — shape wired, magnitude unset). No flat-fill, no
   fabricated bracket. This is honest spec-routing, not a silent gap.

## Per-check confirmation

**2.1.** `nhpp_engine.py` `_simulate_day_counts` implements `Poisson(λ_det(d) ×
Λ_d)` with `Λ_d` a random per-day mixture — the Cox/doubly-stochastic mechanism.
The Gamma-mixed sprint-intensity is the primary (`_sprint_intensity` mechanism
`"cox"` → Gamma background). All five `LambdaModulationForm` slots
(DIURNAL_WEEKDAY_CYCLE, BURSTINESS_OVERDISPERSION, EVENT_DRIVEN_SPIKES,
MONTH_END_SEASONALITY, SECULAR_WORKLOAD_DRIFT) are present and validated by
`_validate_calibrated`; this matches spec §6.3's five-modulation list 1:1. Q is
generated independently of FX — `daily_fx_rate` enters only the `cost = Q ×
$0.01 × FX` product, never the arrival process; test
`test_q_is_independent_of_fx_in_primary_spec` confirms identical Q across
different FX paths. R6 cap-wait/session-cap logic is absent (docstring + memo
confirm discard; x402 has no session cap). Task-0.5 RED harness green.

**2.2 / 2.3 / 2.3a / 2.3b.** The engine implements the calibration-note-locked
forms — it does not re-decide them. `_CALIBRATED_FORM_NAMES` names each
modulation's locked functional form per calibration note §4. The Cox mechanism
matches the §3.3 LOCK. Modulations 2 and 3 are correctly unified as two readouts
of one sprint-intensity mixture (calibration note §4.2/§4.3). `Q_low` is carried
as `NaN` per §2.4 under PARTIAL; the §2.4 pinning rule's deferral to proxy
research is honoured rather than re-decided in code.

**2.4.** `01_simulator_calibration.ipynb` (21 cells) carries: descriptive-posture
banner (cell 0), pre-pin §7 LOCKED block (cell 1), six decision-citation blocks
(data sources, Cox mechanism, five λ(t) modulations, calibrated-vs-anchor, the
two OPEN items, Q⊥FX), NHPP fit diagnostics and the calibrated process vs the
observed anchor, and why/code/interpretation trio markdown HALT-checkpoints.

## Forward-carried recommendations (5) — all folded

| Recommendation | Status | Evidence |
|---|---|---|
| Log-normal sensitivity arm | FOLDED | `overdispersion_mechanism="cox_lognormal"` arm; `test_lognormal_sensitivity_arm_is_a_valid_mechanism`. |
| VMR-as-swept-range | FOLDED | `vmr_target` is a constructor parameter (default 20.0), not a hard-coded target; calibration note §0-A2. |
| 60-130/mo envelope sweep | FOLDED | Calibration note §0-A3 + §2; `test_calibrated_centre_is_in_the_anchored_q_volume_range`. |
| RC O-1 citation refresh | FOLDED | `E10.0_panel_window.json` v0.5→v0.6 citation refreshed (completion memo §1). |
| RC O-2 variance-convention note | FOLDED | Calibration note §0-A4 records sample-vs-population VMR; notebook cell 7 computes both. |

## Findings

None. No GAP, no EXTRA. SPEC-COMPLIANT.
