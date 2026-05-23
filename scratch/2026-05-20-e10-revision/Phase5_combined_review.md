# E10 GSPS — Phase 5 (E10.4) Combined Review (spec-compliance + code-quality)

**Reviewer:** Code Reviewer (combined review per Phase-5 sensitivity-arm posture)
**Date:** 2026-05-23
**Scope:** task 5.1 sensitivity-arm runner + types + tests
**Files reviewed:**

- `simulations/e10_gsps/modules/sensitivity_arms.py` (870 lines)
- `simulations/e10_gsps/types/sensitivity_arms.py` (123 lines)
- `simulations/e10_gsps/tests/unit/test_sensitivity_arms.py` (411 lines)
- Phase-5 completion memo: `scratch/2026-05-20-e10-revision/e10_phase5_completion.md`

**Authoritative anchors consulted:**

- Spec v0.7 (`docs/specs/2026-05-20-e10-gsps-v0.7-convex-multicurrency-design.md`) §§4.4, 8 banned-moves, 9, 11
- Plan v0.4 (`docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md`) Phase 5 / task 5.1, CORR-E10P-11
- `simulations/e10_gsps/modules/regime_break.py` `_REGIME_BREAK_START["NGN"] = date(2023, 6, 1)`
- `simulations/e10_gsps/modules/surface_grid.py` flag semantics
- `simulations/e10_gsps/modules/currency_spread.py` (Phase-4 task 4.3 wrap surface)

**Test execution:** `uv run pytest simulations/e10_gsps/tests/unit/test_sensitivity_arms.py -q` → **16 passed** (no failures, no warnings surfaced in tail).

---

## Top-line verdict: **APPROVED_WITH_NITS**

Phase 5 task 5.1 is commit-ready. The implementation is descriptively honest, the spec-§9 no-rescue posture is structurally enforced (not just documented), the [brainstorm-judgment] decision-citation is stamped verbatim, all five pre-committed arms are present (and the dropped currency-FE-only arm is correctly absent per CORR-E10P-11), and the HALT path on arm (d) is genuinely exercised by a real test using `monkeypatch` on `builtins.__import__`. The five concordant results on the real Tier-1 panel reproduce the headline table.

The trajectory is NON-RETIREMENT-via-HALT-Q-DOMINANCE regardless of arm verdicts, as the spec demands. No Critical finding. Two Important findings (one numeric-convention; one tier-import surface) and a handful of Minor nits — none are commit-blockers, all are clean cleanups for a follow-up commit.

---

## Spec-compliance findings

### Critical — none.

### Important

**I-1. Arm (d) GBM/JD calibration uses `var_fx` with the WRONG dimensional convention; the magnitudes still concord trivially, but the calibration story documented in `notes` is half a step from being misread.**

`sensitivity_arms.py:499-500` sets `T_month = 1.0` and `sigma_daily = math.sqrt(target_var_fx / T_month)`. The variable is named `sigma_daily` but it is in fact `sigma_per_month` (since `T = 1.0` is "one month-equivalent"). The downstream `GBMParameters(sigma=sigma_daily, dt=T_month / n_steps_default)` then uses this monthly-sigma with a sub-monthly dt — which is the correct GBM scaling, because variance of `Δlog FX` summed across `n_steps` days = `σ² · T = σ² · 1.0 = target_var_fx`. The math is right; the variable name is misleading. Also: `target_var_fx` is the panel-mean of `decomposition.var_fx`, which is **the per-cell within-month sum of squared Δlog FX on the surviving daily grid** — i.e. realized monthly variance (correct moment-match for the spec's per-cell decomposition). Worth a one-line comment confirming the moment convention so a future reader doesn't relitigate this; the current docstring at lines 458-461 is close but says "sigma_per_month is sqrt(panel-mean var_fx)" which is exactly what `sigma_daily` numerically equals — rename for clarity.

**Recommended action:** rename `sigma_daily` → `sigma_per_month` in `_arm_d_gbm_jd_comparator` (lines 500-501 and 532). No numerics change; readability only. (Minor in code-quality terms; flagged here as Important because the calibration story is load-bearing for the §9 verdict-memo prose.)

**I-2. Arm (f) concordance metric semantics — the docstring says "max share difference vs. the primary's panel-mean share (a scalar) — this is the descriptively honest comparison because the share is panel-mean-invariant in Q" — confirm with the reader that this is the intended comparison.**

`_arm_f_q_high_extended` at lines 742-755 builds the concordance metric against `primary_panel_mean` (scalar), not pointwise against the primary's anchored grid. The argument is that the share is panel-mean-invariant in Q (each surface point carries the same panel-mean share — Q enters only via the grid coordinate, not the share value). On the real panel this yielded `concordance_metric = 2.71e−20` (floating-point zero) which confirms the invariance empirically.

This is structurally correct **given the surface_grid's panel-mean construction**, but it is a different comparison shape than arms (b)/(c)/(d)/(e) (which use `_concordance_metric_vs_primary` — pointwise on equal-length grids). The headline table treats all five metrics on equal footing in the completion memo. Not a defect — but worth a sentence in the §9 verdict memo making the comparison-shape difference explicit so a reader doesn't infer that arm (f) is "more concordant" than the others (2.71e−20 vs 9.43e−05 looks like a tighter result; it's actually a different distance).

**Recommended action:** add one sentence to arm (f)'s `notes` clarifying "metric is max share difference vs. primary panel-mean (scalar) — comparison-shape differs from arms (b)–(e) which are pointwise on equal grids". Notebook 04 should also surface this.

### Minor

**M-1. The plan task 5.1 description (Phase 5 paragraph) references arm (b) only by name; the spec §11 open-item disposition language ("Q-FX behavioral coupling open item resolved by user-lock 2026-05-21") should appear at the top of the completion memo §1 alongside the existing no-rescue clause quote. (Cosmetic; the completion memo currently puts it at §4.)**

**M-2. The `_CONCORDANCE_THRESHOLD = 0.05` constant is described as "Pinned by the user-locked spec" in the inline comment. I cannot find an explicit user-lock for the 0.05 threshold in the spec v0.7 or plan v0.4 grep. The 0.05 figure is reasonable (it is the conventional descriptive-share concordance threshold), but the comment should soften the attribution to "Pinned per implementer's call against the descriptive-share concordance convention; documented here for traceability" unless the user explicitly locked 0.05. (Honest provenance.)**

**M-3. The arm-(c) buffer language: the spec/plan call it a "robustness pair" — a (with-buffer, without-buffer) pair. The current implementation evaluates ONLY the with-buffer leg; the without-buffer leg is the Phase-4 primary, against which concordance is measured. This is implicitly the pair, but the docstring at lines 326-339 doesn't say so explicitly. One-line clarification recommended.**

---

### Spec-compliance verification — checklist

| Check | Status | Evidence |
|---|---|---|
| All 5 arms (b–f) implemented | **PASS** | `ArmName` Literal in `types/sensitivity_arms.py:37-43`; runner dispatches all 5 at `modules/sensitivity_arms.py:835-858` |
| Currency-FE-only is NOT in this runner (correctly removed per CORR-E10P-11) | **PASS** | No `currency_fe` arm in `ArmName`; not in the runner dispatch list |
| Arm (b) carries the 4-part decision-citation (reference / why / relevance / connection) | **PASS** | `_ARM_B_DECISION_CITATION` at `modules/sensitivity_arms.py:94-114` contains all 4 anchors; test `test_arm_b_decision_citation_stamped` asserts each prefix and the `-0.3` magnitude + `2026-05-21` user-lock date |
| Sign NEGATIVE and magnitude `−0.3` are present | **PASS** | `_QFX_COUPLING_ELASTICITY: Final[float] = -0.3` at module line 90; cited in notes and citation prose |
| Operationalization `Q_t · (1 + (−0.3) · z_t)` is stamped verbatim | **PASS** | Quoted in citation lines 111-113 and `notes` line 292-298 |
| `no_rescue_clause` present on aggregate result with spec §9 language | **PASS** | `_NO_RESCUE_CLAUSE` at lines 130-137 reads "Sensitivity arms cannot rescue a primary HALT (spec v0.7 §9). … The Phase-4 trajectory is NON-RETIREMENT via HALT-Q-DOMINANCE …" — matches spec §8 banned-move "no sensitivity-arm rescue of a primary HALT" and spec §9 verdict-ladder content |
| Descriptive-posture firewall holds — no inferential terminology in returned fields | **PASS** | `test_arm_results_carry_no_banned_inferential_terminology` exercises 10 banned phrases (p-value, reject H0, statistically significant, confidence interval, hypothesis test, etc.) against every arm's `notes`, `decision_citation`, and the aggregate `no_rescue_clause` |
| Phase-4 primary `q_variance_dominance_flag` referenced as input (not re-derived; concordance measured against it) | **PASS** | `run_sensitivity_arms` computes the primary surface ONCE at line 831-833 and threads `primary` as a keyword argument into each arm; the aggregate's `primary_q_dominance_flag` field is set from `primary.q_variance_dominance_flag` (line 862) |
| HALT path for arm (d) when `stochastic_fx` unavailable: emits `"n/a"`, never fabricates | **PASS** | The HALT branch at lines 432-454 returns `concordance_verdict="n/a"` with NaN metric and a disposition memo path on `notes`; the test `test_arm_d_halts_when_stochastic_fx_unavailable` exercises this via `monkeypatch.setattr(builtins, "__import__", _fail_stochastic_fx)` — the path is **genuinely exercised**, not just type-checked |
| Spec §8 banned-moves: no post-hoc threshold tuning; no panel expansion; etc. | **PASS** | `_CONCORDANCE_THRESHOLD` and `_NO_RESCUE_CLAUSE` are `Final` and not parameterized to the caller; the only configurable knobs are `s_be`, `base_n`, `refined_n`, `q_high_extended` — all of which default to spec-pinned values |

### Special attention — arm (b) `concordance_metric = 0` honesty

The Model QA agent's report is correct: the user-pinned monthly-scalar coupling `Q_t · (1 + (−0.3) · z_t)` produces a single per-month multiplicative scalar; a constant scalar drops out of within-month `Δlog Q` exactly, so the within-month decomposition `(var_fx, var_q, cov_term, var_total)` is **algebraically unchanged**, and `fx_variance_share = var_fx / var_total` is identical per cell, and the surface is identical, and the concordance metric is **exactly zero** (not just numerically close — algebraically zero).

The implementation handles this transparency in three places:

1. **Module-level docstring** (lines 28-50): a 23-line block titled "Arm (b) — the user-pinned operationalization" lays out the math explicitly, ending with "The concordance metric is exactly zero by construction." Not buried — it is the SECOND major heading in the module docstring.

2. **Function docstring** for `_arm_b_qfx_coupling` (lines 237-260): restates the math and the resulting `concordance_metric = 0` outcome.

3. **Arm-result `notes` field** (lines 292-299): the runtime `notes` string says "The monthly-scalar multiplier leaves within-month Var(Δlog Q) unchanged; the per-cell FX-variance share is identical under this operationalization" alongside the per-currency z_m envelope summary.

The arm **runs** — it does not silently no-op. `_arm_b_qfx_coupling` still computes per-currency z-scores (lines 264-282; visible/transparent via `notes`), still calls `evaluate_surface_grid(panel, q_range, s_be=s_be)` (line 287), still emits a full `SensitivityArmResult`. The descriptive content surfaces: the per-currency z_m envelopes are useful diagnostics about the magnitude of the (level-only) multiplier. Excellent.

**No alternative coupling operationalization was silently substituted.** The arm reports the descriptively honest outcome of the user-pinned operationalization, exactly as the spec §11 disposition demanded.

### NGN regime-break date provenance (verifying "not magic-numbered")

`_NGN_REGIME_BREAK: Final[date] = date(2023, 6, 1)` at module line 118 carries an inline comment "Spec-pinned NGN regime-break date (per `modules/regime_break.py:_REGIME_BREAK_START`)." Cross-check: `regime_break.py:69` shows `_REGIME_BREAK_START: dict[str, date | None] = { "NGN": date(2023, 6, 1), ... }`. **Match confirmed.** Spec §3.4 / CORRECTIONS-E10-4 Fix 3 anchors the June-2023 float.

Nit: importing the constant from `regime_break.py` would be even cleaner (eliminates the duplication), but `regime_break._REGIME_BREAK_START` is a private dict and reaching into the leading-underscore name from a sibling module is a worse violation than the current re-declare-with-citation pattern. Accept as-is.

---

## Code-quality findings

### Critical — none.

### Important

**I-3. The `_arm_d_gbm_jd_comparator` import of `simulations.stochastic_fx` is correct and the docstring acknowledges it ("which is permitted because they are not the e10_gsps utils tier", lines 60-61), but the import is **inside the function** (lines 432-438). This is the intended pattern (a deferred import lets the function emit the HALT result on `ImportError`), and the test exercises it via `monkeypatch` on `builtins.__import__`. However, the `try/except ImportError as exc:` block at lines 432-454 wraps the import AND the four-name `from … import (GBMParameters, GBMPathGenerator, JumpDiffusionParameters, JumpDiffusionPathGenerator)` block on a single statement, which is fine for `ImportError` (atomic import). One thing to verify: if `simulations.stochastic_fx` exists but is missing one of the four names, the `ImportError` is still raised (because `from … import` raises `ImportError` for any missing name), so the HALT branch covers that too. **Not a defect — confirming the path is genuinely robust.**

### Minor

**M-4. `slots=True` on dataclasses (`SensitivityArmResult`, `SensitivityArmsResult`): present. `frozen=True`: present. Full type annotations: present (no untyped fields, no `Any` leakage).**

**M-5. The `_share_summary` helper at `modules/sensitivity_arms.py:145-172` handles all-NaN / empty input by emitting four NaN keys (never silent zero). Correct honest-failure pattern. The `_concordance_metric_vs_primary` helper at lines 175-202 also emits NaN on length mismatch or all-non-finite shares.**

**M-6. The `hash(cur) % 10_000` seed offset at `modules/sensitivity_arms.py:512` and `:551` is a deterministic-enough seed source for the GBM/JD ensembles, but Python's `hash(str)` is randomized per process (PYTHONHASHSEED). This means arm (d) is **not deterministic across runs** unless `PYTHONHASHSEED` is fixed. For a descriptive sensitivity arm (not a primary verdict), this is fine — the 256-path ensemble mean is very stable across seeds. But for reproducibility-tier discipline (Tier-3 round-trip), this is worth pinning. Replace `hash(cur) % 10_000` with a deterministic mapping: e.g. `{"COP": 0, "BRL": 1, "EUR": 2, "GBP": 3, "NGN": 4}.get(cur, 99)` or `int(hashlib.sha256(cur.encode()).hexdigest()[:4], 16)`. (Suggestion; not commit-blocking. Concordance metric on a fresh process would still likely fall well below 0.05.)**

**M-7. Docstring contracts are present and concise on each arm runner and the public `run_sensitivity_arms`. They state input invariants (e.g. "tuple-immutable input is preferred but any Sequence is accepted"), raised errors (none — the runner returns HALT results in place of raising; documented), and silenced errors (e.g. arm (d) silences `ImportError` from `simulations.stochastic_fx` and converts it to a `"n/a"` arm — documented in the function docstring at lines 426-431).**

**M-8. The arm (e) per-currency q-dominance computation at line 672-674 — `per_cur_q_dom = all(sg.q_variance_dominance_flag for sg in spread.per_currency_grids.values())` — is a strict-AND across the 5 per-currency surfaces. Spec/plan does not explicitly pin "all-or-nothing" vs "majority"; the strict-AND is the conservative reading and matches the descriptive posture. Reasonable choice; documented.**

**M-9. The `_in_buffer` predicate in arm (c) at lines 348-353 compares `(year, month)` tuples lexicographically against the buffer endpoint. This is correct because `(2023, 11) <= (2023, 12)` and `(2024, 1) > (2023, 12)`, and `_NGN_REGIME_BREAK = date(2023, 6, 1)` + 6 months → buffer end = (2023, 12). The arithmetic at lines 341-346 is the standard month-rollover; the formula `((month-1 + n) // 12, ((month-1 + n) % 12) + 1)` is correct. The test `test_arm_c_drops_ngn_buffer_cells_when_present` directly asserts "dropped 6 NGN cell" for the 2023-07 … 2023-12 input. Numerics verified.**

### Test quality — 16 tests broken down

| Test | What it verifies | Quality |
|---|---|---|
| `test_all_5_arms_run_on_synthetic_qdom_panel` | Five arms in documented order, no raise | Structural smoke |
| `test_primary_q_dominance_flag_carried_on_aggregate_result` | The aggregate field carries the primary flag | Structural |
| `test_no_rescue_clause_present_on_aggregate_result` | Clause carries "cannot rescue" + "primary" | Spec-§9 enforcement |
| `test_arm_b_decision_citation_stamped` | All 4 prefixes + `-0.3` + `2026-05-21` | Brainstorm-judgment provenance |
| `test_arm_b_user_pinned_operationalization_yields_zero_metric` | `concordance_metric == 0.0` exact equality | Algebraic honesty (excellent) |
| `test_arm_c_ngn_break_window_runs_on_real_phase_layout` | No NGN cells in buffer when panel starts 2024-01 → concordant | Real-panel match |
| `test_arm_c_drops_ngn_buffer_cells_when_present` | "dropped 6 NGN cell" when 2023-07…2023-12 NGN present | Buffer-drop arithmetic |
| `test_arm_d_runs_when_stochastic_fx_available` | Finite metric; verdict in {concordant, discordant} | Happy path |
| `test_arm_d_halts_when_stochastic_fx_unavailable` | `monkeypatch.setattr(builtins, "__import__", …)` → `"n/a"` + disposition memo path | **HALT path genuinely exercised** — non-tautological |
| `test_arm_e_wraps_compute_currency_spread` | Verdict literal + q-dom on synthetic Q-dom panel | Phase-4 wrap smoke |
| `test_arm_f_extends_q_high_to_dune_cap_equivalent` | q-dom + no interior crossing + "39000" in notes | Extended-grid construction |
| `test_arm_q_dominance_flag_correct_on_panel_below_break_even` | All non-n/a arms preserve q-dom on Q-dominated panel | Cross-arm consistency |
| `test_arm_q_dominance_flag_false_when_panel_above_break_even` | Primary q-dom False + arm-b mirrors (since op is identity on shares) | Negative case (non-tautological) |
| `test_arm_surface_share_summary_keys_complete` | Required 4 keys present (never silent omission) | Schema discipline |
| `test_arm_results_carry_no_banned_inferential_terminology` | 10 banned phrases × every arm-string field | Firewall — comprehensive |
| `test_arms_run_on_real_tier1_panel` | Loads `data/panels/e10_gsps_panel.parquet` if present | Real-panel smoke |

The HALT-path test (`test_arm_d_halts_when_stochastic_fx_unavailable`) is the most important non-tautological test in the suite. It uses `monkeypatch.setattr(builtins, "__import__", _fail_stochastic_fx)` which actually replaces the import machinery — a `from simulations.stochastic_fx import …` inside `_arm_d_gbm_jd_comparator` will hit `_fail_stochastic_fx`, raise `ImportError`, fall into the `except ImportError as exc:` branch, and emit `concordance_verdict = "n/a"`. The test then asserts the disposition memo path string is in `notes` ("Phase5_HALT_d_gbm_jd_comparator.md"). **The path is genuinely exercised, not stubbed.**

The descriptive-posture firewall test constructs banned phrases via string concatenation (e.g. `"p" + "-" + "value"`) so the CI grep firewall at `scripts/e10_firewall_check.py` doesn't false-positive on the test source. Clever and correct.

### Tier-import discipline

| Tier | Permitted imports | Observed |
|---|---|---|
| `types/sensitivity_arms.py` | stdlib + typing (no `..modules` / `..utils`) | **CLEAN** — only `dataclasses`, `typing.Literal` |
| `modules/sensitivity_arms.py` | stdlib + numpy + sibling `..modules` + `..types` + cross-package `simulations.stochastic_fx` | **CLEAN** — no `..utils` import; the cross-package `simulations.stochastic_fx` import is in-function (deferred) and explicitly permitted by the module docstring lines 60-61 |
| `tests/unit/test_sensitivity_arms.py` | unrestricted | **CLEAN** — only imports the public `run_sensitivity_arms` and types; uses `pytest.MonkeyPatch` for HALT-path mocking |

### Functional-python discipline

| Check | Status |
|---|---|
| `@dataclass(frozen=True, slots=True)` on all returned containers | **PASS** — both `SensitivityArmResult` and `SensitivityArmsResult` |
| No inheritance | **PASS** — no class-with-base in either types or modules; HALT branches return dataclasses, not exceptions |
| Full type annotations | **PASS** — every public function and helper has annotated params + return; no `Any` |
| No `# type: ignore` | **PASS** — grep clean |
| No `# noqa` | **PASS** — grep clean |
| No broad `except Exception` / `except BaseException` | **PASS** — grep clean. The only `except` is `except ImportError as exc:` at line 439, which is the narrowest specific catch for a deferred import |
| Free pure functions in modules tier | **PASS** — all helpers `_arm_*` and `run_sensitivity_arms` are free functions; no module-level mutable state |

---

## Summary of recommended cleanups (none commit-blocking)

If a lightweight follow-up commit is desired before merging Phase 5, the ranked priority is:

1. **I-1.** Rename `sigma_daily` → `sigma_per_month` in `_arm_d_gbm_jd_comparator` (lines 500-501, 532) for calibration-story clarity.
2. **I-2.** Add a one-sentence comparison-shape note to arm (f)'s `notes` so the 2.71e−20 vs 9.43e−05 metric values are not misread as "arm (f) is the most concordant".
3. **M-6.** Replace `hash(cur) % 10_000` with a deterministic mapping for reproducibility across processes.
4. **M-2.** Soften the `_CONCORDANCE_THRESHOLD = 0.05` inline-comment provenance ("Pinned per implementer's call" rather than "Pinned by user-locked spec") unless an explicit user lock can be cited.

None of these block the commit. The implementation is descriptively honest, structurally correct, spec-§9-compliant, and the trajectory remains NON-RETIREMENT-via-HALT-Q-DOMINANCE regardless of arm verdicts — exactly as the spec demands.

**Approved with nits. Commit-ready.**
