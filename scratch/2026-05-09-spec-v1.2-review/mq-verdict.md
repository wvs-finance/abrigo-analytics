---
artifact_kind: independent_methodology_audit_verdict
auditor: Model QA Specialist (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-08
target_artifact: docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md (v1.2; 908 lines)
predecessor_audit: scratch/2026-05-09-spec-v1.2-review/rc-verdict.md (RC ACCEPT)
default_verdict: REJECT
---

# MQ Verdict — Spec v1.1.1 → v1.2 Amendment

**Verdict: ACCEPT_WITH_FLAGS**

The v1.2 amendment passes the methodology audit. Functional form, nesting claim, authority chain, and anti-fishing posture are sound. Two non-blocking flags on prior concentration provenance and the §15.4 self-referential prior clause.

---

## Audit dimensions

**1. $(1-\lambda)^t$ functional form — PASS.** Spec §6.1 line 410 correctly identifies it as "deterministic factor / discrete-time constant-hazard exponential survival." For monthly cohort billing observation cadence (SURVEY.md §5(i)), this is the canonical form. Verified.

**2. Beta(4.5, 95.5) quantiles — NUMERICALLY VERIFIED.** Computed via `scipy.stats.beta`:
- Mean = 0.04500 ✓ (spec line 442: "0.045")
- SD = 0.02063 ✓ (matches reasoning ~0.021)
- 95% CI = [0.01379, 0.09319] ✓ (spec line 446: "$\approx [0.013, 0.094]$")
- Pr(λ>0.10) = 0.0151; Pr(λ<0.01) = 0.0078 — tail-mass language at lines 447–449 is faithful.

**3. Weibull k=1 nesting — PASS.** Line 452: "$S_t = (1-\lambda)^t$ is the $k=1$ nested null inside Weibull $S(t) = e^{-(\lambda t)^k}$." Mathematically correct for small λ via $(1-\lambda)^t = e^{t\ln(1-\lambda)} \approx e^{-\lambda t}$, which equals Weibull at k=1 with hazard rate λ. SURVEY.md §3.4 citation 2 (Han, Hou & Chen 2018) is the right anchor.

**4. No silent fishing — PASS.** §15.2 (lines 792–822) and §15.6 (lines 894–906) explicit on the authority chain: lit + cohort economics → SURVEY.md → spec → C3 conformance check. SURVEY.md line 3–4: "Author has NOT read C3 v0.3 implementation code... prior to producing this survey." Decoupling discipline holds.

**5. Task 0.2b NO-OP — PASS with flag.** Logic at §15.4 lines 840–846 is sound for the *functional form* (model unchanged ⇒ ELPD trivially preserved). HALT-on-flip safety net (line 854) is appropriate.

**6. Methodology consequence on ELPD / k̂ — PASS.** SURVEY.md line 219+ ("expected effect on ELPD ranking" — no-op with prob ≳0.8). Hazard form is deterministic in λ-conditional posterior; doesn't change the rest of Det+churn computation. Confirmed.

**7. Stage-3 falsification path — PASS.** Lines 452–460 keep Weibull k≠1 as Stage-3-only LR / posterior-CI test. Scope boundary, not fishing escape.

**8. Identifiability / convergence — LOW RISK.** Beta(4.5, 95.5) concentration=100 with synthetic AR(1)-log-MRR likelihood (C3 models.py L228–246) on first-trajectory observations: the prior dominates only if T is small. With monthly panels of T≥24, the likelihood will shrink the posterior; ESS impact bounded. C3 v0.3 ESS gates (R4 floor) catch any pathology.

**9. Authority chain documented — PASS.** §15.2 explicit.

---

## FLAGs

**MQ-FLAG-v1.2-A (Medium): Beta(4.5, 95.5) concentration=100 not directly cited from SURVEY.md.** SURVEY.md line 176–178 specifies only "median ≈ 0.04–0.05 monthly per Recurly/Paddle/Indie Hackers prosumer-segment benchmarks" — it pins the *median*, not the *concentration*. Spec line 444 asserts concentration=100 is "moderate" but provides no independent benchmark for tail-mass calibration. The 95% CI [0.013, 0.094] is *consistent with* SURVEY.md citation 5 (4–5% prosumer range) but the choice of α+β=100 vs. e.g. α+β=20 or α+β=500 is unilateral.

**Remediation:** add one-line provenance — either "concentration set to maximally cover SURVEY.md 4–5% benchmark while excluding λ>10%/mo with 98.5% prior mass" (which is what the math supports) or cite a specific source.

**MQ-FLAG-v1.2-B (Medium): §15.4 lines 848–850 prior-retroactive-definition clause is methodologically uncomfortable.** Quote: *"The $\lambda \sim \mathrm{Beta}(4.5, 95.5)$ prior pinned v1.2 is the prior under which the C3 v0.3 fit is *defined to have been conducted* for purposes of v1.2 close-out."* C3 v0.3 actually uses **Beta(2.0, 38.0)** per `priors.py` L42–43 (`DET_CHURN_LAMBDA_BETA_A=2.0`, `DET_CHURN_LAMBDA_BETA_B=38.0`). Beta(2.0, 38.0) has mean=0.05, concentration=40 — *different* from Beta(4.5, 95.5). The "defined to have been conducted" language is fictive. The escape hatch at lines 850–855 ("If C3 v0.3 source code uses a different λ prior... Task 0.2b becomes a NON-NO-OP") is correctly worded but it **is in fact triggered**: the priors differ.

**Remediation (BLOCKING for Task 0.2b execution, non-blocking for v1.2 spec acceptance):** Phase 0 Task 0.2b must execute as a real re-fit under Beta(4.5, 95.5), not NO-OP. HALT-on-flip applies. Recommend amending §15.4 to acknowledge the prior delta and route Task 0.2b to NON-NO-OP.

---

## Files referenced

- `/home/jmsbpp/apps/abrigo-analytics/docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (v1.2, §6.1 L399–466, §15 L752–907)
- `/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-09-st-literature-survey/SURVEY.md` (§5 L174–189)
- `/home/jmsbpp/apps/abrigo-analytics/simulations/saas_builder/cohort_3/models.py` L237–246
- `/home/jmsbpp/apps/abrigo-analytics/simulations/saas_builder/cohort_3/priors.py` L42–43

**Verdict: ACCEPT_WITH_FLAGS** (FLAG-A: prior concentration provenance; FLAG-B: §15.4 prior-equivalence clause is contradicted by C3 v0.3 source — Task 0.2b is NON-NO-OP).

End of MQ verdict on spec v1.2.
