# MQ verdict — Stage-3 Track A2 plan v0.1 (real-data conditioning)

**Reviewer:** Math Quality (MQ), 2-way Delphi-independent.
**Plan under review:** `docs/plans/2026-05-11-stage-3-a2-real-data-conditioning.md` v0.1.
**Master spec:** `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2.
**Stage anchor:** STAGE_2_RESULTS.md §2.5 (R5 marginalization), §3.3 (R7 Υ_t INDISTINGUISHABLE), Stage-2 verdict memo §4.1, §4.3, §7 lim. 3, prereg-lock §15.4.

**Verdict: APPROVE-WITH-NITS.**

The math claims under Pins P-A2.1 – P-A2.5 are sound. The plan correctly preserves the R5 analytic-marginalization argument under prior swap, correctly scopes the Υ_t rank-flip safeguard, and correctly identifies the two strip checks required under post-K⋆-shift geometry. Five nits — none are math-blocking, but two should be tightened before execution.

---

## Per-pin math review

### Pin P-A2.3 — R5 marginalization preservation under prior swap (Task 3.2)

**Claim.** Plan §7 Task 3.2 acceptance bullet 4 + `prior_swap_rationale.md` will state: "R5 (STAGE_2_RESULTS.md §2.5) marginalization carries through unchanged — the discrete-latent sum-out is analytic; only the LSE prior-weights $P(\text{tier}_i, n_d, n_m)$ are re-evaluated against the empirical $\bar C$ percentiles."

**Math check.** R5 (STAGE_2_RESULTS.md §2.5) states:
$$
\sum_{\text{tier}_i,\, n_d,\, n_m} P(\bar C \mid \text{tier}_i, n_d, n_m)\,P(\text{tier}_i, n_d, n_m) = P(\bar C)
$$
The analytic sum-out is exact iff the discrete latents do not condition the $\tau_t$ likelihood at the resolution in play. STAGE_2_RESULTS.md §2.5 explicitly anchors this on the fact that "at Stage-2 resolution the three discrete latents do not condition the $\tau_t$ likelihood (per-tier $\theta_k$ differentiation deferred to Stage-3 per spec §5.4 hint)." STAGE_2_RESULTS.md §5 Stage-3 open items list (item 3) reinforces this: "Per-tier $\theta_k$ differentiation per spec §5.4 hint — resolves the structural near-prior $\pi$ posterior observed at Stage-2 resolution and **converts R5's exact analytic sum-out into a genuine information-bearing marginalization**."

The A2 prior swap replaces $P(\text{tier}_i, n_d, n_m)$ (the joint over discrete latents and tier) with empirical-percentile-derived weights; it does NOT introduce per-tier $\theta_k$ conditioning of the $\tau_t$ likelihood. Therefore the factorization preserved, and R5 still sums out analytically. ✓ APPROVE.

**NIT MQ-A2-1 (cosmetic but load-bearing).** Plan §7 Task 3.2's `prior_swap_rationale.md` must state — verbatim — that A2 does **NOT** introduce per-tier $\theta_k$ differentiation. The current acceptance bullet 4 only paraphrases the sum-out preservation. The danger is silent scope creep: if a later worker reads the empirical prior as "now we differentiate per-tier," R5 is silently broken. Add explicit language: "A2 swaps only the discrete-latent joint prior $P(\text{tier}_i, n_d, n_m)$; A2 does NOT add per-tier $\theta_k$ conditioning to the $\tau_t$ likelihood. Per-tier $\theta_k$ differentiation remains deferred to Stage-4 per STAGE_2_RESULTS.md §5 item 3."

---

### Pin P-A2.4 — Υ_t rank-flip scope (Task 3.3)

**Claim.** Plan §7 Task 3.3: HALT condition `winning_form != "ar1_log"` OR `ranked_forms[1] != "det_churn"`; scope = Υ_t LOO only, NOT cost-prior.

**Math check vs Stage-2 §15.4.** Stage-2 prereg-lock §15.4 specifies the HALT-on-flip semantic as:

> "If the re-fit ELPD ranking flips relative to C3 v0.3 (i.e., a different $\Upsilon_t$ form wins, **or any verdict band crosses the 4·SE / 2·SE thresholds**), the close-out HALTs..."

The plan's HALT condition captures only `winning_form` and `ranked_forms[1]` — i.e., the ordering. It does NOT explicitly capture the **band-crossing** sub-clause from §15.4. STAGE_2_RESULTS.md §3.3 reported $\Delta\mathrm{elpd}/\mathrm{SE} = 1.67$ (INDISTINGUISHABLE band, below the 2·SE PASS threshold). Under the empirical prior, the SE could:

- **(a)** stay $\le 2$ but flip order → captured by plan's HALT ✓
- **(b)** rise above $2$ (verdict band crossing from INDISTINGUISHABLE to WEAK/MARGINAL) WITHOUT flipping order → **NOT captured** by plan's HALT ✗

**NIT MQ-A2-2 (Material).** The plan's HALT condition is **strictly weaker** than Stage-2 §15.4's HALT semantic. Add a third HALT clause: any verdict-band crossing in either direction (INDISTINGUISHABLE ↔ {PASS, WEAK, MARGINAL, FAIL}) triggers HALT. The cohort_3 verdict-band logic already lives in `simulations/saas_builder/cohort_3/loo.py` §verdict-router (PASS/WEAK/MARGINAL/INDISTINGUISHABLE/FAIL bands per the 4·SE / 2·SE thresholds); the plan should read the `verdict` field of the re-emitted `revenue_form_verdict.json` and HALT if it differs from the Stage-2 freeze value (INDISTINGUISHABLE).

The MQ-NIT-2 scoping (Υ_t LOO only, NOT cost-prior) IS preserved correctly — the plan's Task 3.3 runs LOO on the three Υ_t candidates only. ✓ on scope.

---

### Pin P-A2.3 — diagnostic-gate thresholds (Task 3.2)

**Claim.** $\hat r < 1.01$, ESS_bulk ≥ 1000, ESS_tail ≥ 1000, divergence_frac = 0.0, ci_width_ratio_max ≤ 1.10.

**Math check vs anchors.**
- Spec / verdict-memo §4.1: ESS_bulk ≥ 1,000 (observed 338,540), ESS_tail ≥ 1,000 (observed 213,752), divergence_frac = 0.0 (observed 0.0), ci_width_ratio_max ≤ 1.10 (observed 1.0039), $\hat r < 1.01$ (observed 1.0000265). Plan's gates **MATCH the spec / verdict-memo gates exactly.** ✓
- `simulations/saas_builder/diagnostics.py:289-294` `passed` logic uses LOOSER bounds: ESS_bulk ≥ 400, divergence_frac ≤ 0.005, ci_width_ratio_max ≤ 2.0. These are the **code-resident** gates; the SPEC gates (P-A2.3) are tighter.

**NIT MQ-A2-3 (Cosmetic).** There is a spec ↔ code drift in `diagnostics.py` — the docstring `passed` logic permits looser thresholds than the spec / verdict-memo declare. This is NOT an A2 problem (it predates Stage-3), but A2 Task 3.2 must clarify which gate is load-bearing for P-A2.3. The plan should explicitly state that the **spec gates** (the tighter ones) are the Pin P-A2.3 gates, NOT `diagnostics.py::DiagnosticVerdict.passed`. Otherwise an executor could read `passed = True` from the existing code path and declare Pin P-A2.3 satisfied at the wider tolerance. Add to Task 3.2 acceptance: "Pin P-A2.3 passes iff the spec gates are met, NOT iff `DiagnosticVerdict.passed` returns True. If a discrepancy is observed, HALT."

---

### Pin P-A2.5 — Strip pin re-verification (Tasks 4.2 + 4.3)

**Claim.** Re-run `CarrMadanEnvelopeVerifier` (envelope, Pin S6) AND `assert_long_vol_signature` (Pin S5) on the post-K⋆-shift strip.

**Math check.** Master spec §2.2 phase 4 explicitly justifies the two-check choice: "Pin S3 (`x_left < 0 < x_right`) and Pin S2 (`Σw_j = 1`) are K⋆-scale-invariant, but the tiled-body geometry depends on `delta_inner` choice, and a sufficiently extreme K⋆ shift could break the long-vol signature."

This is correct:
- **Pin S2** ($\Sigma w_j = 1$): scale-invariant under multiplicative K⋆ shift. ✓ no re-check needed.
- **Pin S3** ($x_\text{left} < 0 < x_\text{right}$ in log-strikes centred at K⋆): K⋆-scale-invariant by construction (centering is the operation). ✓ no re-check needed.
- **Pin S5** (long-vol signature: $\Pi_\text{strip}(S_0) = 0$ strict, $\Pi_\text{strip}(S_0 e^{\pm\delta_\text{inner}}) > 0$): depends on $\delta_\text{inner}$ geometry vs the K⋆-shifted body. CAN break. ✓ re-check required.
- **Pin S6** (envelope vs log-contract proxy): depends on the strip weights' alignment with $-2/K^2$ Carr-Madan density. CAN break. ✓ re-check required.

The two-check selection is mathematically complete given the K⋆-invariance argument. ✓ APPROVE.

**NIT MQ-A2-4 (Cosmetic).** Plan Task 4.2 references the "cohort_5_strip's pinned 35% tolerance" (Pin S6). Per master-spec §9.2 / RC-FLAG-4 disposition (lines 555–558), there is a known cohort_5_strip docstring drift between `__init__.py:21` (says ≤ 5%) and `types.py:74` (`REPLICATION_REL_TOL = 0.35`). The plan correctly uses the 35% number (the code-level pinned tolerance), but should add a one-line acknowledgement that the docstring fix is upstream (cohort_5_strip patch, not A2's responsibility) so that an executor reading `__init__.py` does not falsely HALT at 5%.

---

### Sample-size + bootstrap methodology (Task 2.3)

**Claim.** "Bootstrap or order-statistic confidence intervals on each percentile reported."

**Math check.** At $N \ge 75$ for tail percentiles ($P_{10}, P_{90}$):
- Order-statistic CI for $P_{10}$ on $N = 75$ has 7.5 expected observations in the $[0, P_{10}]$ tail — viable but coverage near binomial limits.
- Bootstrap CI: basic / percentile / BCa each have different bias-correction properties. **BCa is recommended for tail percentiles** under finite samples (Efron 1987), because basic and percentile bootstrap miss the bias correction that matters most in the tails.

**NIT MQ-A2-5 (Material if N is close to floor).** The plan is silent on which bootstrap variant. Flag: Task 2.3 should specify **BCa bootstrap** (or order-statistic Hutson 1999 if $N < 100$) for tail percentiles. If the executor uses naïve percentile bootstrap on $N = 75$ for $P_{10}$, the tail CI will be over-confident. Add to Task 2.3 acceptance: "Bootstrap variant pre-pinned at protocol time (SOURCING_PROTOCOL.md §3 or §4): BCa (default) or order-statistic; choice locked before any data row is touched per anti-fishing."

---

## Cross-track dependency (A1 ↔ A2)

Plan §3 enumerates dependencies but does not address the A1↔A2 case. If A1 completes during A2's wall-time and recommends REPLACE, the cohort_5_strip emit driver itself changes; A2's Phase 4 re-emit then targets a moving driver.

**NIT MQ-A2-6 (Defer to RC).** This is a workflow-orchestration concern, not a math concern. Routed to RC. Math invariant: if A1 lands REPLACE before A2 Phase 4, A2 Phase 4 must re-run the re-verification against whichever driver is current (a new K⋆ AND a new strip topology). The math (Pins S5, S6) holds either way.

---

## Anti-fishing posture (Task 1.1, §4)

**Claim.** "$N_\text{MIN} = 75$ floor enforced at EXIT (not at pre-registration)."

**Math check vs CLAUDE.md.** CLAUDE.md anti-fishing invariants pin $N_\text{MIN} = 75$ as a hard floor. Stage-2 prereg-lock §15.5 preserves this verbatim. The plan's wording "at EXIT (not at pre-registration)" is correct: pre-registration commits to the FLOOR (a binding lower bound), not to an EXPECTED $N$. No expected-$N$ language appears in Task 1.1 §4. ✓ APPROVE.

The plan's stop rule (Phase 1 §7: "data collection ends when both (i) $N \ge 75$ across at least 3 channels AND (ii) any single channel does not exceed 60% of the sample") is also anti-fishing-clean: a floor + a diversity constraint, no over-collection inducement, no early-stopping trigger.

---

## Schema-v1.2 backward compat (Task 3.4)

**Claim.** `parent_audit_block: str | None` is optional; v1.0 / v1.1 readers default to `None`.

**Math check.** Trivially correct under Python optional-field semantics. The Hypothesis property test specified in Task 3.4 acceptance is the right verification. ✓ APPROVE.

---

## Summary table

| Nit | Severity | Anchor | Action |
|---|---|---|---|
| MQ-A2-1 | Cosmetic but load-bearing | STAGE_2_RESULTS.md §2.5 + §5 item 3 | Tighten Task 3.2 rationale: explicit "no per-tier $\theta_k$ in A2" |
| MQ-A2-2 | Material | Stage-2 §15.4 (band-crossing clause) | Add band-crossing HALT to Task 3.3 |
| MQ-A2-3 | Cosmetic | `diagnostics.py:289-294` vs verdict-memo §4.1 | State spec gates (tighter) are load-bearing, not code-level `passed` |
| MQ-A2-4 | Cosmetic | RC-FLAG-4 disposition / cohort_5_strip drift | Acknowledge 35% (not 5%) is the pinned tolerance |
| MQ-A2-5 | Material if $N \approx 75$ | bootstrap-CI theory | Pre-pin BCa (or order-statistic) at protocol time |
| MQ-A2-6 | Workflow, defer to RC | (none — orchestration) | RC to address A1↔A2 wall-time interleaving |

---

**Verdict: APPROVE-WITH-NITS.** The plan's math is sound. Address MQ-A2-2 (band-crossing) and MQ-A2-5 (bootstrap variant pre-pin) in v0.2 before execution dispatch; MQ-A2-1, -3, -4 are CORRECTIONS-α-class cosmetic tightenings that should land in v0.2 §12.1.

*— MQ, 2026-05-11.*
