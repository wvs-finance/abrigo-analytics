# E10 Phase 4 — Spec-Compliance Review

**Reviewer:** Code Reviewer (spec-compliance scope; code-quality runs separately)
**Date:** 2026-05-23
**Scope:** Phase 4 modules + types + unit tests just-landed (not yet committed).
**Authoritative anchors:** spec v0.7 §4 / §7 / §9 / §11 / §13; plan v0.2 lines 323–357; CORR-E10P-9/10/11; pre-Phase-4 Model QA + RC reviews; Phase-2.5 break-even record; user-locked decisions of 2026-05-21.

---

## Top-line verdict — **SPEC-COMPLIANT**

Phase 4 (tasks 4.1, 4.2, 4.2a, 4.3) implements **exactly** what spec v0.7 + plan v0.2 + the two user-locked decisions specify. All required outputs, fields, decision-citations, and firewalls are in place; the verdict-ladder I/O is consumable by the §9 classifier in Phase 6; the anti-fishing carry-forward holds (no spec edits, no s_be tuning, honest q-dominance verdict).

37/37 Phase-4 unit tests GREEN; firewall PASS (51 files); CORRECTIONS-E10 ledger ends at -7 (Phase-3 era, no Phase-4-era amendment).

Two NITS surfaced (both non-blocking, documented below).

---

## Task 4.1 — vol-on-vol regression (PASS)

| Check | Verdict | Evidence |
|---|---|---|
| Two co-primary FE specs both run | **PASS** | `vol_on_vol_regression.py:212-224` — `beta_two_way` via `_two_way_demean`; `beta_currency_only` via `_currency_demean`; both fed to `_within_slope`. |
| Two-way-vs-currency-only gap reported as descriptive content | **PASS** | `vol_on_vol_regression.py:226` `gap = beta_two_way - beta_currency_only`; `VolOnVolResult.gap` field at `types/vol_on_vol.py:71`. Real-panel value +13.44 (memo §5). |
| G=5 caveat carried; clustered SE not reported standalone | **PASS** | `vol_on_vol_regression.py:64-68` `_G_CAVEAT_LABEL`; carried via `g_caveat_label`. Module emits NO SE — clustered SE absent entirely, which is *stronger* compliance than "context only". |
| No inferential terminology in any returned string | **PASS** | Firewall scanner clean (51/51); test `test_result_string_fields_carry_no_inferential_terminology` at `test_vol_on_vol_regression.py:194-204` enforces. |
| n_cells = 150, residual DoF (two-way) = 115 | **PASS** | `test_panel_dimensions_recorded` at `test_vol_on_vol_regression.py:116-128` pins both. Arithmetic matches CORR-E10P-9/10/11 (5 + 30 − 1 = 34 absorbed; 150 − 34 − 1 = 115). |
| §4.1 necessary-not-sufficient framing preserved | **PASS** | `types/vol_on_vol.py:1-33` module docstring; `vol_on_vol_regression.py:1-53` module docstring; both explicitly call this "descriptive sign only", "necessary-not-sufficient", "no inferential claim". |

---

## Task 4.2 — surface-grid evaluator (PASS)

| Check | Verdict | Evidence |
|---|---|---|
| Surface = Var(Δlog FX) / Var(Δlog cost) | **PASS** | `surface_grid.py:7-9` docstring; computed via `_panel_mean_share` reading `cell.fx_variance_share` (`PanelCell` field set in Phase-3 panel-construction). |
| Grid log-spaced 50 base + adaptive doubling to 100 within ±0.5 dex of s_be | **PASS** | Constants at `surface_grid.py:106-114`: `DEFAULT_BASE_N=50`, `DEFAULT_REFINED_N=100`, `_REFINEMENT_HALF_WIDTH_DEX=0.5`. Doubling logic at `surface_grid.py:523-534`. Tests `test_evaluate_surface_grid_base_grid_size_default_50` (line 238) + `test_evaluate_surface_grid_adaptive_doubling_triggers_near_s_be` (line 277) + `test_evaluate_surface_grid_no_adaptive_doubling_far_from_s_be` (line 287). |
| Decision-citation stamped (4-part: ref / why / relevance / connection) | **PASS** | `_GRID_DECISION_CITATION` at `surface_grid.py:117-132` carries `Reference: ... Why: ... Relevance: ... Connection: ...` + `user lock 2026-05-21` + literal "log-spaced 50 points" / "adaptive doubling to 100" / "±0.5 dex of s_be = 0.25". Stamped on every result via `grid_resolution_decision_citation` field (`types/surface.py:91`). Module docstring also carries it verbatim (`surface_grid.py:17-38`). |
| Q-range from genuine empirical source (not fabricated) | **PASS** | Q-range `(28.0, 130.0)` passed by caller from Phase-2 anchor (memo §4 cites `notebooks/e10_gsps/diagnostics/E10.1_calibration_note.md` §2 and `scratch/.../e10_q_anchor_buckets.json`). Module accepts `q_range` as a parameter — does NOT hardcode a fabricated value (`surface_grid.py:461-468`). |
| `q_variance_dominance_flag` field present + definition TRUE iff share < s_be at every grid point | **PASS** | `surface_grid.py:546-550`: `q_dom_flag = all((math.isfinite(s) and s < s_be) for s in shares)`. Tests `test_evaluate_surface_grid_q_variance_dominance_flag_true_for_low_share` (line 259) + `_false_when_share_above_s_be` (line 268). Note: definition is `share < s_be`, which is the contrapositive of `var_q/var_total > 1 − s_be` only when `cov_term = 0` (which is the spec §6.4 primary-arm pinned condition). On the primary panel this matches. |
| Required fields on `SurfaceGridResult` | **PASS** | `types/surface.py:81-91`: `points`, `break_even_share`, `grid_resolution`, `interior_crossing`, `crossing_q_volumes`, `anchored_range_low`, `anchored_range_high`, `q_variance_dominance_flag`, `refined`, `effective_n_grid`, `grid_resolution_decision_citation`. All present. |
| §11 open item 1 (surface-grid resolution) closed | **PASS** | User-lock of 2026-05-21 stamped in code + decision-citation; resolution pinned at 50/100. |

---

## Task 4.2a — interior-crossing detection (PASS)

| Check | Verdict | Evidence |
|---|---|---|
| ≥3 contiguous strictly-interior cells below s_be | **PASS** | `detect_interior_crossing` at `surface_grid.py:225-309`; production default `min_run_length=3` at line 230. Test `test_detect_interior_crossing_three_contiguous_strictly_interior_flags` (line 186); `_single_cell_does_not_flag` (line 162); `_two_contiguous_cells_do_not_flag` (line 175). |
| Endpoints excluded from interior count | **PASS** | Loop `for i in range(1, n - 1)` at `surface_grid.py:277` strictly excludes indices 0 and N-1. Endpoint dips routed to `endpoint_below_low` / `endpoint_below_high` (lines 270-271). Test `test_detect_interior_crossing_endpoint_dip_reported_separately` (line 203). |
| "Entirely-below = q-dominance, NOT interior-crossing" semantic guard | **PASS** | `surface_grid.py:295-301`: `at_least_one_endpoint_clears = not (endpoint_below_low and endpoint_below_high)`; `interior_crossing = len(qualifying_runs) > 0 and at_least_one_endpoint_clears`. This is the load-bearing guard that prevents an entirely-below surface from flipping the §9 classification away from NON-RETIREMENT. Real-panel result confirms (memo §7): both endpoints below, interior_crossing=False, q_variance_dominance_flag=True. |
| Returns flag + crossing_locations + endpoint_below tuple | **PASS** | `InteriorCrossingResult` at `types/surface.py:95-122`: `interior_crossing`, `crossing_q_volumes`, `interior_runs`, `endpoint_below_low`, `endpoint_below_high`. |
| Flag wired so §9 classifier in Phase 6 can consume it | **PASS** | `SurfaceGridResult.interior_crossing` (`types/surface.py:84`) matches the `interior_crossing` parameter of `DescriptiveVerdictClassifierModule.__call__` at `modules/verdict_classifier.py:36`. Same name, same type (bool), same semantic. |

---

## Task 4.3 — 5-currency non-statistical spread display (PASS)

| Check | Verdict | Evidence |
|---|---|---|
| 5 per-currency surface curves on shared grid | **PASS** | `currency_spread.py:246-256` groups by currency, evaluates per-currency surface via `_per_currency_surface`. Test `test_compute_currency_spread_emits_5_per_currency_grids` (line 87). |
| Envelope: min / max / Q1 / Q3 / median, pointwise across 5 surfaces | **PASS** | `currency_spread.py:258-272` — `np.nanmin / nanmax / nanquantile(0.25) / nanquantile(0.75) / nanmedian` over axis=0 (currencies). Tests at `test_currency_spread.py:103-148`. |
| `is_em_or_dm` tag map: COP/BRL/NGN=EM, EUR/GBP=DM | **PASS** | `DEFAULT_EM_OR_DM` at `currency_spread.py:76-82`. Test `test_em_dm_tag_map_matches_default_assignment` (line 151). |
| `non_statistical_label` with NOT-confidence-interval / NOT-inferential-band / NOT-hypothesis-test negations | **PASS** | `NON_STATISTICAL_LABEL` at `currency_spread.py:87-90` literally carries all three negations. Test `test_non_statistical_label_present_and_carries_negation` (line 164) enforces. |
| Bootstrap / permutation arms NOT computed | **PASS** | No bootstrap / permutation code in `currency_spread.py`. Comments at lines 7-10 + 56 confirm v0.6 W-2 / CORR-E10P-11 deletion. `SurfaceGridPoint.band_low/band_high` carry NaN per `types/surface.py:14-17`. |
| Spread is descriptive, gates no verdict | **PASS** | Result carries no flag consumed by Phase-6 classifier; only the envelope arrays + tag map + label. Module docstring (`currency_spread.py:1-46`) is explicit. |

---

## Spec §7 seven pre-pin fields — carry-forward (PASS)

Phase-4 code does not silently change any of the seven pre-pinned fields:

- **Field 1 (sign):** descriptive sign of β reported; no inferential test introduced. PASS.
- **Field 2 (primary object):** surface + ex-ante break-even — both implemented in `evaluate_surface_grid` + `s_be=0.25` default. PASS.
- **Field 3 (material threshold):** `DEFAULT_S_BE = 0.25` at `surface_grid.py:103`, sourced from Phase-2.5 record (frozen, not redefined). PASS.
- **Field 4 (lag):** contemporaneous monthly — panel construction is Phase-3 frozen; Phase 4 consumes the same `PanelCell` records, does not re-lag. PASS.
- **Field 5 (posture):** descriptive only — firewall passes; no inferential terminology in any Phase-4 string field. PASS.
- **Field 6 (panel & FE):** 5 currencies × ~30 months ≈ 150 cells; G≈5; two co-primary FE specs — all match Phase-4 implementation (n_cells=150, n_currency_clusters=5 asserted in tests). PASS.
- **Field 7 (HALT conditions):** Phase 4 emits the `q_variance_dominance_flag` that maps to HALT condition (b) (Q-dominance → NON-RETIREMENT) per spec v0.7 §7 / plan §3. PASS.

---

## Spec §9 verdict-ladder I/O compatibility (PASS)

Phase-6 §9 classifier (`modules/verdict_classifier.py:32-37`) consumes six flags:
`surface_computed`, `material_gap`, `simulator_anchored`, `q_variance_dominates`, `interior_crossing`, `dv_gate_passed`.

The four flags Phase 4 is responsible for emitting:

| Phase-6 input | Phase-4 source | Type match | Status |
|---|---|---|---|
| `surface_computed` | Phase 4 *producing* a `SurfaceGridResult` is the flag's positive case; the consuming notebook / Phase-6 plumbing sets it from `len(result.points) > 0` (or equivalent). Implicit but unambiguous. | bool | **PASS** (semantic) |
| `material_gap` | Per-cell `PanelCell.material_gap` (Phase-3 field); aggregated by Phase-6 callsite. Not Phase-4's emission, but Phase 4 does not corrupt it. | bool | **PASS** |
| `q_variance_dominates` | `SurfaceGridResult.q_variance_dominance_flag` (`types/surface.py:88`) | bool / bool | **PASS** |
| `interior_crossing` | `SurfaceGridResult.interior_crossing` (`types/surface.py:84`) | bool / bool | **PASS** |

The Phase-6 classifier is still a RED stub (`modules/verdict_classifier.py:39 raise NotImplementedError`) — fine, Phase 6 has not landed yet; the I/O shape compatibility is what matters at Phase 4 closure and it matches.

---

## Anti-fishing carry-forward (PASS)

- **`s_be = 0.25` sourced from Phase-2.5 frozen record, not redefined.** `surface_grid.py:103` `DEFAULT_S_BE: float = 0.25` with the module-level comment "the spec v0.7 §4.4 ex-ante-pinned value, frozen at the Phase-2.5 break-even record. Carries no Stage-1 estimation content (firewall restored per CORRECTIONS-E10-4 Fix 2)." PASS.
- **Q-dominance verdict from honest computation, not threshold tuning.** Panel-mean share ~1.5e-4 vs s_be=0.25 → ~3 dex below; verdict produced by the `q_variance_dominance_flag = all(s < s_be ...)` computation in `surface_grid.py:548-550`, not by any threshold adjustment. PASS.
- **No Phase-4-era CORRECTIONS amendment.** Spec v0.7 CORRECTIONS ledger ends at -7 (Phase-3 era). `git log` on the spec shows the last touch was the Phase-3 commit. PASS.

---

## NITS (non-blocking)

### NIT-1 — semantic-guard documentation depth

The "entirely-below = q-dominance, NOT interior-crossing" guard (`surface_grid.py:295-301`) is **beyond the literal user-locked rule** ("≥3 contiguous strictly-interior cells below s_be"). The completion memo (§3 Decision 2) explicitly acknowledges this as an extra guard. The user prompt also explicitly verifies it is implemented correctly, so this is *required*, not extra — but the spec text itself does not name it. Recommend a brief one-line addition to spec v0.7 §4.2a in the next minor revision noting the guard, so a future re-reader does not flag it as scope-creep. Non-blocking for Phase 4 closure.

### NIT-2 — `scan_interior_crossing` legacy variant default

`scan_interior_crossing` (`surface_grid.py:312-367`) keeps `min_run_length=1` as default for Phase-0 RED-harness compatibility, while production callers go through `evaluate_surface_grid` which passes `min_run_length=3` (line 543). This is correctly documented in the docstring (lines 320-330) and the test surface (the per-cell-overload `SurfaceGridModule.__call__` at line 425 uses `min_run_length=1` to preserve the original RED-harness semantics). The risk is a future caller importing `scan_interior_crossing` directly and silently using the wrong rule. Recommend either renaming to `_scan_interior_crossing` (private) or adding a runtime `DeprecationWarning` if `min_run_length` is not explicitly passed. Non-blocking for Phase 4 closure; the production path (`evaluate_surface_grid` / `compute_currency_spread`) correctly passes `min_run_length=3`.

---

## Evidence ledger (cross-doc match)

- Real-panel verdict from memo §6–7: `β_two_way=+68.15`, `β_currency_only=+54.71`, `gap=+13.44`, `q_variance_dominance_flag=True`, `interior_crossing=False`, share ~3 dex below s_be everywhere. **Matches** the user prompt's stated result.
- Test count from memo §9: 37/37 Phase-4 GREEN (8 vol_on_vol + 9 currency_spread + 20 surface_grid = 37). **Verified** via `uv run pytest`.
- Firewall: 51 files clean. **Verified** via `python scripts/e10_firewall_check.py simulations/e10_gsps/`.

---

## Conclusion

Phase 4 (tasks 4.1 / 4.2 / 4.2a / 4.3) **SPEC-COMPLIANT**. Both user-locked decisions (2026-05-21) are stamped in code (constant + decision-citation field + module docstring); the descriptive-posture firewall holds; the §9 verdict-ladder I/O matches what the Phase-6 classifier will consume; the anti-fishing carry-forward is intact (no spec edits, no s_be tuning, honest q-dominance verdict from pure computation).

Phase 4 closure (tasks 4.1 / 4.2 / 4.2a / 4.3) is APPROVED from the spec-compliance side. The two nits above can be addressed in-place at Phase-4 closure or deferred to Phase 5 housekeeping.

Task 4.4 (notebook `03_surface_characterization.ipynb`) is outside this review's scope per plan §1 Phase 4 — the Phase-4 exit gate of plan §2 is still gated on 4.4 + closure 2-way review.

---

*Phase 4 spec-compliance review — closes here.*
