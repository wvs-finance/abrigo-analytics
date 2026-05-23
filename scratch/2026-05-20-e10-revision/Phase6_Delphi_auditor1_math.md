# Phase 6 — Delphi Auditor #1 (Math & Econometrics) — E10 GSPS pre-write-up

**Auditor scope:** §4.2 identity; surface-grid; vol-on-vol arithmetic; s_be derivation; sensitivity arms; verdict ladder.
**Posture:** Independent of auditors #2 / #3. Evidence-driven, file:line citations.
**Date:** 2026-05-23.

---

## CRITICAL findings

None. The §4.2 identity holds at floating-point zero on the gapped grid, the FE arithmetic is correct, the verdict ladder is collectively exhaustive, and the s_be derivation is self-consistent (Phase-2.5 firewall held).

---

## HIGH findings

### FINDING H-1 — Arm (d) GBM/JD calibration scale mismatch
- **Severity:** High
- **Location:** `simulations/e10_gsps/modules/sensitivity_arms.py:507-540` (and the JD branch :549-577)
- **Problem:** The calibration treats `target_var_fx` (the panel-mean of `decomposition.var_fx`) as a monthly-aggregate variance, but `decompose_cell` defines `var_fx = population_variance(fx_log_returns)` — a per-step mean variance ≈ σ²·dt, not Var(Σ Δlog) ≈ σ²·T.
- **Proposed fix:** Either (a) set `sigma_per_month = sqrt(target_var_fx · n_steps / T_month)` so the simulated per-step var matches `target_var_fx`; or (b) target Var(sum) explicitly by computing `Σ r_t²` per path against `target_var_fx·n_steps`. Update notes string to match.
- **Evidence:**
  - `decomposition.py:145-146`: `var_fx = population_variance(fx_log_returns)` — mean-per-step variance.
  - `sensitivity_arms.py:514-515`: `T_month = 1.0; sigma_per_month = math.sqrt(target_var_fx / T_month)` — therefore σ² = target_var_fx.
  - GBM generator (`stochastic_fx/generators.py:165`): `log_step = (μ − σ²/2)·dt + σ·√dt · Z` so per-step Var(log_step) = σ²·dt = target_var_fx·dt = target_var_fx/n_steps_default ≈ target_var_fx/21.
  - `sensitivity_arms.py:538-540`: re-measures `gbm_var_fx` as per-step population variance, returns ~target/21 (not target).
  - **Impact direction:** the deflation of `sub_var_fx` *strengthens* q-dominance (smaller numerator → smaller share). It does NOT flip the NON_RETIREMENT verdict; arm (d) `q_variance_dominance_flag` stays True. But the documented "comparator calibrated to panel-mean var_fx" claim is empirically false by ~21x.
  - Verdict impact: **does not flip the result**, but the methods-paper §5 should not cite "GBM/JD calibrated to the panel-mean FX-variance" without correcting either the calibration or the comparator-moment description.

### FINDING H-2 — Arm (d) JD diffusion/jump variance budget self-inconsistent under the H-1 scale
- **Severity:** High (dependent on H-1)
- **Location:** `simulations/e10_gsps/modules/sensitivity_arms.py:543-577`
- **Problem:** Same scale mismatch as H-1: `sigma_jd = sqrt(target_var_fx · 0.9 / T_month)` and `jump_var = target_var_fx · 0.1 / (λ·T_month)` are sized against monthly-aggregate budget but the comparator is per-step. The per-step Merton variance is `σ_jd²·dt + λ·dt·(μ_J² + σ_J²)` = `(0.9·target/T)·dt + (0.1·target/T)·dt` = `target·dt/T = target/n_steps`. So the 90/10 budget itself is honored (it splits the same /21 deflation), but it's a /21 deflation of the *intended* total — same H-1 root cause.
- **Proposed fix:** Fix H-1; H-2 resolves mechanically.
- **Evidence:** Same as H-1; the JD branch reuses the buggy `T_month=1` convention. The diffusion/jump split is *internally* consistent at 90/10 regardless of scale, but the absolute level is wrong by the same n_steps factor.

---

## MID findings

### FINDING M-1 — q_variance_dominance_flag is defined on FX-share, not Q-share
- **Severity:** Mid
- **Location:** `simulations/e10_gsps/modules/surface_grid.py:548-550` and `:438-440`
- **Problem:** Audit-spec interpretation: `q_variance_dominance_flag` ↔ `var_q/var_total > 1 − s_be = 0.75` at every grid point. Code implements: `var_fx/var_total < s_be` at every grid point. These are equivalent ONLY when `cov_term = 0`. Generally `var_fx/var_total + var_q/var_total = 1 − cov_term/var_total`, so the complement relation breaks under non-zero Cov(ΔlogFX, ΔlogQ).
- **Proposed fix:** Either (a) re-state the spec/code as a single share-based test (`s(Q) < s_be everywhere`) — drop the var_q-side description; or (b) add the actual var_q-share test to the surface and flag both.
- **Evidence:**
  - `surface_grid.py:546-550`: `q_dom_flag = all((isfinite(s) and s < s_be) for s in shares)` where `s = var_fx/var_total`.
  - The decomposition is three-way: `var_total = var_fx + var_q + cov_term` (`decomposition.py:147-148`), with `cov_term = 2·Cov`.
  - On the real panel cov_term is small enough that both conditions fire (share ≈ 1.5e-4, q-share ≈ 0.9998); verdict is unaffected for this run. But the spec's textual "Q-variance component dominates" is not the same as "FX-variance share below s_be" under nonzero Cov.
  - **Impact:** Cosmetic for the current PASS-through-q_dominance result; matters if a future iteration sees large positive cov_term (an FX-Q co-movement regime) where var_fx-share could be < s_be while var_q-share is also < 0.75. The current run is safe; the naming is misleading.

### FINDING M-2 — The "surface across the Q-volume range" is a flat broadcast
- **Severity:** Mid
- **Location:** `simulations/e10_gsps/modules/surface_grid.py:517-535`
- **Problem:** `evaluate_surface_grid` computes a single `mean_share = _panel_mean_share(panel)` and broadcasts it to every grid point (`shares = [mean_share] * base_n`). The "surface" is therefore a horizontal line at the panel-mean by construction — not an empirical Q-dependence. The dex math (`_is_within_half_dex` refinement trigger) is moot: a constant function cannot satisfy refinement on some points but not others. The header docstring ("calibration-conditional surface estimate for a panel whose share is approximately invariant in Q-volume") admits this only weakly.
- **Proposed fix:** Either (a) name this `panel_mean_share_envelope` rather than "surface across the Q-volume range" in §5 prose; or (b) implement a real Q-dependence (e.g., a kernel-smoothed regression of share on Q across cells) — the latter is out of scope for E10 v0.7.
- **Evidence:**
  - `surface_grid.py:517` `mean_share = _panel_mean_share(panel)` (single scalar).
  - `surface_grid.py:520` `base_shares = [mean_share] * base_n` (broadcast).
  - `surface_grid.py:528-529` refined-grid path also broadcasts the same scalar.
  - Adaptive doubling is unreachable for the current panel: mean_share ≈ 1.5e-4, s_be = 0.25, ratio ≈ 1.6e-3, log10 ≈ −2.8 — far beyond ±0.5 dex. `refined: false` confirmed in `E10.3_surface_summary.json`. The mechanism is correct *logic* but is structurally a no-op for any panel whose mean share is more than 0.5 dex from s_be in either direction.

### FINDING M-3 — Arm (b) doesn't actually execute coupled-trajectory pipeline
- **Severity:** Mid
- **Location:** `simulations/e10_gsps/modules/sensitivity_arms.py:288-290`
- **Problem:** Arm (b) computes per-currency z_m envelopes for transparency, then **re-evaluates the surface on the unchanged panel**: `evaluate_surface_grid(panel, q_range, s_be=s_be)`. It does NOT rebuild trajectories with `Q_coupled = Q · s_m`. The arm relies entirely on the algebraic-identity argument (monthly scalar drops out of within-month Δlog Q). Algebra verified correct (audit numerical check confirmed exact dropout for multiplicative monthly scalar). But the arm's name + spec position imply a coupled-panel sensitivity test was *executed*, when in fact only the per-currency z-summary was executed.
- **Proposed fix:** Either (a) rename the arm "Arm (b) — algebraic identity test (Q-FX monthly scalar coupling)" and update notes; or (b) actually rebuild the panel with coupled Q and verify shares numerically (would still yield concordance ~0, providing a sanity sample).
- **Evidence:** Numerical verification of dropout (audit Bash check): for Q=[100, 0, 90, 110, 0, 95, 85] and s_m = 0.7, max |Δlog Q_orig − Δlog Q_coupled| on surviving days = 0.0 exactly.

### FINDING M-4 — `decompose_cell` `_MIN_SURVIVING_DAYS = 2` is methodologically degenerate
- **Severity:** Mid (acknowledged in code as a future amendment; preserving here for §5)
- **Location:** `simulations/e10_gsps/modules/panel_construction.py:83`
- **Problem:** At n=2 surviving days, only one daily log-return exists; population variance of a 1-element series is 0 (correctly returns 0.0 in `realized_variance.population_variance:118`), giving NaN share (`var_total = 0`). Code comment acknowledges Phase-3 review I-1: spec should pin threshold at 3 (one degree of freedom for variance). All 150 production cells have ≫ 3 surviving days, so this is benign for the current run. A future CORRECTIONS-E10-8 is anticipated.
- **Proposed fix:** Raise the threshold to 3 in spec v0.8; defer for now — flag in §5 as a known methodological footnote.
- **Evidence:** `panel_construction.py:79-83` (the comment explicitly acknowledges this).

---

## LOW findings

### FINDING L-1 — Header docstring overstates "calibration-conditional surface" claim
- **Severity:** Low
- **Location:** `simulations/e10_gsps/modules/surface_grid.py:478-485` (docstring), tied to M-2.
- **Problem:** Phrase "the correct calibration-conditional surface estimate" implies a non-trivial Q→share mapping was estimated; what is computed is the panel-mean scalar. Re-phrase per M-2.

### FINDING L-2 — `_within_slope` returns 0.0 silently on degenerate denominator
- **Severity:** Low
- **Location:** `simulations/e10_gsps/modules/vol_on_vol_regression.py:144-160`
- **Problem:** A no-within-variation regressor (e.g., a one-currency panel after a FE-on-currency wipe) yields `denom == 0.0` and the function silently returns slope = 0.0. The descriptive sign label then reads "0" which is honest (`_sign:72-77`), but a caller cannot distinguish "true zero slope" from "degenerate / not identified". Spec posture is descriptive-only so this rarely matters, but the panel of n=150, G=5 should be checked for this case.
- **Proposed fix:** Return NaN with a `sign = 0` so the consuming notebook can disambiguate, or surface a `degenerate_dof_flag` on `VolOnVolResult`. For the current run β_two_way = 68.15, β_cur_only = 54.71 — non-degenerate, finding is preventive only.
- **Evidence:** `vol_on_vol_regression.py:157-159` returns 0.0 unconditionally on denom == 0.

### FINDING L-3 — Population vs sample variance convention is consistent (informational confirmation)
- **Severity:** Low (no issue — flagging for §5 transparency)
- **Location:** `realized_variance.py:102-121` (population), `decomposition.py:65-95` (population covariance), `vol_on_vol_regression.py` (within-FE OLS — no n-vs-n-1 issue, the slope is sum(x̃·ỹ)/sum(x̃²) which is scale-invariant in the convention)
- **Problem:** None. The exact additive identity `Var(a+b) = Var a + Var b + 2 Cov` holds for population (divisor n) but NOT for sample (divisor n−1) unless paired. Both `population_variance` and `_population_covariance` use the matching divisor-n convention. The §5 docstring (`realized_variance.py:23-30`) is explicit about this. Empirical max |residual| = 1.3322676e-15 in `E10.2_decomposition_summary.json:13` confirms the identity holds at machine precision across all 150 cells.

### FINDING L-4 — `gap = beta_two_way − beta_currency_only` direction confirmed
- **Severity:** Low (informational confirmation)
- **Location:** `vol_on_vol_regression.py:226`
- **Evidence:** Code: `gap = beta_two_way - beta_currency_only`. Diagnostic JSON: 68.15124620607666 − 54.714823014552536 = 13.436423191524128. Audit-spec expected gap = +13.44 matches.

---

## Verdict ladder (Section 6 of audit scope)

The 7-rung ordering in `verdict_classifier.py:200-316` is collectively exhaustive over 2^6 = 64 flag states. Verified by walking each rung:
1. !dv_gate_passed → NON_RETIREMENT(dv_fail).
2. !simulator_anchored → NON_RETIREMENT(simulator_unanchored).
3. !surface_computed ∧ material_gap → PARTIAL.
4. !surface_computed ∧ !material_gap → NON_RETIREMENT(q_dominance).
5. surface_computed ∧ q_variance_dominates → NON_RETIREMENT(q_dominance).
6. surface_computed ∧ !q_variance_dominates ∧ material_gap → PARTIAL.
7. otherwise → SURFACE_PRODUCED.

Real-panel flags: `dv_gate_passed=True, simulator_anchored=True, surface_computed=True, material_gap=False, q_variance_dominates=True` → rung 5 fires → `NON_RETIREMENT subtype q_dominance`. Correct.

Inferential-verdict ban: `emit_inferential_verdict` unconditionally raises `DescriptiveVerdictError` (line 318-329) — structural firewall confirmed.

---

## s_be derivation (Section 4 of audit scope)

The `E10.2.5_break_even_threshold.md` derivation traces s_be = 0.25 to first principles:
- s_exp = 0.25 (ex-ante exposure prior, FROZEN §1.3).
- ATM-straddle payoff: Π(s) = c_payoff · s (variance-replication property, §3.2).
- Ideal-scenario fair pricing: c_payoff = 1.
- Break-even: c_payoff · s_be = φ → s_be = φ/c_payoff = 0.25/1 = 0.25.

The s_exp = s_be coincidence is correctly explained as a property of a fair-priced hedge sized to its declared prior (§3.4), not as circular construction. The threshold caveat (§4) honestly flags the no-venue / c_payoff-may-be-lower-in-reality risk. Phase 4 / Phase 5 consume the constant `DEFAULT_S_BE = 0.25` in `surface_grid.py:103` and `sensitivity_arms.py:78` without redefinition. **No issue.**

---

## TOP LINE

**STRONG FOUND — DISCUSSION NEEDED.**

The verdict does not flip — NON_RETIREMENT (q_dominance) is mathematically robust. But two HIGH findings (H-1, H-2) document an arithmetic mismatch in arm (d) GBM/JD calibration that the §5 methods-paper write-up must not gloss over. Two MID findings (M-1 surface-flag complement-vs-Q-share; M-2 surface-as-flat-broadcast) require either rewording or a small structural fix before §5 prose can claim a "Q-dependent surface" or a "Q-variance-dominance" test stricter than the implemented "FX-share-below-s_be" test. Recommendation: triangulate with auditors #2 / #3, then apply (a) wording fix or arithmetic fix on H-1/H-2; (b) wording fix on M-1/M-2/M-3 before §5 authoring. The §4.2 identity, the FE arithmetic, the s_be derivation, and the verdict ladder are clean.
