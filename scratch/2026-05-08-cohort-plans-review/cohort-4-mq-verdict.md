# SAAS-COHORT-4 — Model QA Specialist plan-doc verdict (Wave 2 of 2)

**Plan:** `docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md` v0.1
**Auditor role:** Model QA Specialist (modeling correctness, anti-fishing, posterior-predictive semantics, identity tolerance)
**Default verdict posture:** REJECT.

## Verdict: ACCEPT_WITH_FLAGS

The plan reproduces the 5-step symbolic chain with anchored citations, pins the 5-test-point grid with sign expectations BEFORE evaluation, defines Z as a posterior-predictive expectation (not a residual bootstrap), enforces the audit-block over the C1/C2/C3 + spec input set, sidecars sign-verdicts rather than silently extending `ZCapPinned`, and routes every gate violation through `feedback_pathological_halt_anti_fishing_checkpoint`. Three modeling-layer FLAGs remain — none invalidate the plan, all should be addressed in v0.2 or in dispatch briefs.

## Dimension-by-dimension findings

### D1 — π(t) symbolic chain (Pin M1) — PASS
Lines 40–66 reproduce all 5 steps: (1) pitch identity → (2) perpetual identity π(t)·dt ↔ dΠ/dt → (3) §8.1 closed form Π=K*√σ_T → (4) Carr-Madan linearization §16-19 → (5) variance proxy §6 substitution. Line 66 explicitly bans the Carr-Madan-skipping shortcut and assigns Reality Checker enforcement. Each step cites PRIMITIVES.md anchor verbatim.

### D2 — Z-cap formula (posterior-predictive, no residual bootstrap) — PASS
Line 269 defines Z as `E[q_t^USD/(X/Y)_t + π(t)]` over the C1 `synthetic_tau_t` panel. Line 270 defines the 95% CI as the **(2.5, 97.5) percentile pair of per-draw Z realizations** — i.e., the predictive distribution of the cap, NOT a bootstrap-on-residuals. Task 4.2 step 4 (line 447) makes this an explicit Model QA gate.

### D3 — 5-test-point grid + sign expectations (Pin M2) — PASS-with-FLAG-1
Lines 70–80 pin the exact grid: TP1 (κ₀, mean), TP2 (0.5κ₀), TP3 (1.5κ₀), TP4 (FX=4200), TP5 (FX=3800). Sign expectation π(t)>0 at all 5. Line 80 bans post-hoc point perturbation. **FLAG-1 (line 76):** the monotonicity claim "|π| < TP1 (less overage exposure)" at TP3 with κ=1.5κ₀ flips direction at TP2 ("|π| monotone in κ direction"). The pre-pinned monotonicity sign of ∂|π|/∂κ is recorded twice with non-orthogonal phrasing. Phase 3.3 (line 367) does require the joint-identifiability hypothesis property to enforce a single signed direction per spec §6 partial-derivative table — but the plan should restate the κ-monotonicity sign in one canonical line in M2 to avoid ambiguity at dispatch time. Recommend v0.2 add: "∂|π|/∂κ < 0 at fixed (X/Y, σ₀) — long-gamma cap shrinks as cap-kink rises."

### D4 — Carr-Madan tractability (symbolic only, no IronCondor strip) — PASS
Lines 60–64 instantiate the static-replication strip identity symbolically. No 12-leg numerical instantiation is attempted; deployment-stage scope per CLAUDE.md ideal-scenario framing is respected. Out-of-scope (line 27) excludes live LP capital and on-chain settlement.

### D5 — Audit-block hash inputs (Pin M4) — PASS
Lines 102–110 enumerate the exact 5-file input set: synthetic_tau_t.parquet, cohort_prior.parquet, ROBUSTNESS_RESULTS.md, PRIMARY_RESULTS.md, spec. `Path.resolve()` canonicalization mandated (line 110). Missing-file FileNotFoundError is the desired enforcement.

### D6 — Symbolic-vs-numerical fallback — PASS-with-FLAG-2
Line 268 sets identity tolerance ≤1e-10 symbolic, ≤1e-6 numerical (per Path A v0 §10.4 inheritance). **FLAG-2:** the plan does not articulate an explicit MC error budget for the posterior-predictive Z computation when the predictive expectation cannot close in sympy and falls back to MC over C1 draws. The 1e-6 numerical tolerance applies to the dΠ/dt identity, not to MC-error on E[Z]. Recommend v0.2 add an MC-stderr gate (e.g., `stderr(Z_hat) / Z_hat ≤ 1e-3` with N_draws ≥ 4000, citing C1 panel size).

### D7 — `ZCapPinned` field-list match (Pin M3) — PASS
Lines 86–92 reproduce the shipped schema verbatim (Z_cop_per_month, ci_95_lo, ci_95_hi, audit_block, tier_mix, schema_version). Verified against `simulations/types/posterior.py:173–257`. Sign verdicts correctly sidecared to `Z_cap_pinned.SIGN_VERDICTS.md` (line 93) — NO silent schema extension; future inclusion gated on additive `schema_version` bump.

### D8 — HALT triggers — PASS
Line 80 (sign reversal at any TP fires HALT per spec §8(1)); line 272 (any test-point sign violation OR identity-tolerance breach → full HALT protocol with disposition memo + 3-way review + CORRECTIONS-block). Tasks 4.1 (line 430) and 4.2 (line 451) inherit the HALT trigger on REJECT.

### D9 — Anti-fishing — PASS-with-FLAG-3
Lines 80, 239, 543–545 carry the anti-fishing posture: 5-test-point grid pre-pinned, no threshold relaxed, audit-block as non-bypassable lineage commitment. **FLAG-3:** Task 0.4 step 2 (line 166) requires COHORT-2 sign-certification PASS but does not mandate that the `ROBUSTNESS_RESULTS.md` be hashed at the *exact commit* that produced the PASS — if the file is mutated post-PASS, the audit-block silently drifts without re-running cert. Recommend v0.2 record the COHORT-2 commit-sha alongside the file path in Pin M4.

## Summary
3 FLAGs, 0 BLOCKs. Modeling-layer foundation is sound: posterior-predictive semantics correct, sign-cert grid pre-pinned, identity tolerance inherited, no schema drift. FLAGs are all v0.2-addressable in dispatch briefs and do not block plan-execution authorization.

**Verdict: ACCEPT_WITH_FLAGS.**
