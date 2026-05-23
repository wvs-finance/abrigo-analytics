# Model QA Specialist — Plan-doc Verify Verdict
## Plan: `2026-05-08-saas-cohort-2-t2-pricing-sign.md` v0.1

**Verdict: ACCEPT_WITH_FLAGS**

Default REJECT overcome: the plan satisfies the methodological core (M2-tightness criterion explicit and quantified, Δ/Γ closed forms specialized from PRIMITIVES rather than re-derived, sign certification gate strictly < 0 at every bracket × (ε, ω) cell, bank-spread arm structurally walled off, posterior-predictive CI mandated NOT bootstrap, α-floor not mutated). Three FLAGs and two BLOCK-adjacent items remain; none reach REJECT individually.

---

### BLOCK candidates promoted to FLAG (close before Phase 2 dispatch)

**FLAG-1 — Anchor mis-citation (lines 19–20, 244, 357, 497).**
Plan header cites "PRIMITIVES.md §10 (Carr-Madan)" as the closed-form anchor for Δ. Δ^(a_s) closed form is at PRIMITIVES.md **§7 eq. (10)** (verified at PRIMITIVES.md:230); §10 is Carr-Madan replication. The Phase-2 prelude (line 80) and verification matrix (line 497) cite §7 correctly, but the header (line 20) and Task 1.2 brief (line 153 reads §1/§4.2/§6/§7/§8 — correct) are inconsistent with the title-line "PRIMITIVES.md §10". MQ dimension #2 (closed-form specialization) is satisfied by content, but the user-facing anchor list misleads. Fix: update line 20 to `§4.2 (cohort instantiation), §6 (FX path), §7 (Δ closed forms), §8 (CPO sign argument)`.

**FLAG-2 — Δ-cohort eq. number drift (line 80).**
Plan pin Δ-cohort references "PRIMITIVES.md (7'), eq. 7'". PRIMITIVES.md §7 numbers the Δ^(a_s) form as **eq. (10)** (verified PRIMITIVES.md:232). The "(7')" notation is non-existent in the source. Task 3.2 contract-docstrings pass requires the Δ-evaluator docstring to cite "PRIMITIVES.md (6), (7'), (8) verbatim" (line 356) — this will fail RC because (7') is not a real label. Fix: replace all "(7')" with "(10)" and "(8)" with "(11)" or whatever matches §8.1; have Task 1.2 reconciliation memo confirm exact eq. numbers BEFORE Phase 2 dispatch.

**FLAG-3 — PPC quantile checks under-specified (MQ dimension #6).**
Plan mandates posterior-predictive 95% CI on Δ and Γ (line 272, 331, 437) but does NOT pin **which user-relevant quantiles** of token-consumption τ_t the PPC must cover. Spec §9 row TODO-COHORT-2 demands posterior-predictive credible interval; MQ standard requires PPC at minimum {50th, 90th, 99th} of τ_t to detect fat-tail miscoverage that would silently widen the Δ CI and absorb a near-zero sign violation (this is exactly the pre-mortem item line 373: "Sign-flip at one bracket point being absorbed by overly wide credible interval"). Pre-mortem flags it but no test pins it. Fix: add to Task 2.5 a PPC-coverage test asserting empirical coverage at {50, 90, 99}-pct of τ_t draws falls within [0.93, 0.97] for nominal 95%; HALT otherwise.

---

### Methodology dimensions — pass/fail

| # | Dimension | Verdict | Evidence |
|---|---|---|---|
| 1 | Softplus L¹-tightness criterion + grid + κ + smallest-β rule | PASS | M2 / M2-fit at lines 72–78; SOFTPLUS_TIGHTNESS_EPS shipped (distributions.py:48); β not free — fitter returns smallest grid-β satisfying M2 |
| 2 | Δ specialized, not re-derived | PASS (with FLAG-1, FLAG-2) | Task 1.2 hand-derives by **substitution** (line 158); Task 2.3 sympy verifies, numpy hand-codes against closed form (line 248) — correct order |
| 3 | Γ specialized; sign NOT pre-pinned | PASS | Line 86 explicit "Γ^(a_s) sign is NOT pre-pinned (it is an output)"; spec §9 alignment (line 502 of spec) |
| 4 | 5-point bracket sign cert at [4200, 3800, 4200] | PASS | BRACKET-M5 pin (line 88–92); strict `<0` at every bracket × (ε, ω) cell; HALT per spec §8(1) |
| 5 | Bank-spread overlay re-runs gate; ROBUSTNESS_RESULTS table | PASS | ROBUST-BS pin (line 94); demoted-to-sensitivity correctly per spec line 599, 610; primary verdict walled off (line 273) |
| 6 | PPC quantile checks | PARTIAL | See FLAG-3 |
| 7 | No silent α-floor tuning | PASS | α-floor 1.5 not touched; sampler-tier enforcement (distributions.py:40) inherited; plan does not re-sample posterior (line 17 "No PyMC") |
| 8 | C1 composition via shipped parquet IO | PASS | PosteriorReader wraps `simulations/utils/parquet_io.py` (line 225); Task 0.4 schema gate (line 120) |
| 9 | Sympy/numerical fallback with MC error budget | PASS | DeltaSymbolicNumericalReconciler at tolerance `1e-10·N_terms` (line 249); reconciler is gate-blocking |

---

### Strengths

- Task 2.3 split (symbolic derive → verify → hand-code numerical) is the correct MQ pattern; sympy is not in the hot path.
- Pre-mortem (Task 3.5) explicitly enumerates the CI-absorption failure mode (line 373) — only the test coverage (FLAG-3) is missing.
- Anti-fishing audit at Task 4.1 step 10 (line 417) explicitly checks for silent grid widening between v0.1 and gate-verdict commits.
- Task 4.2 MQ reverify hand-derives Δ at one random bracket point from PRIMITIVES alone (line 435) — independent reproducibility.

---

**Disposition.** Address FLAG-1, FLAG-2, FLAG-3 in v0.2 CORRECTIONS block; ACCEPT for commit with FLAG record. Re-verify not required.

**Word count:** ~580.
