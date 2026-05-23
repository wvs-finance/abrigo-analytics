# Cohort-3 Plan-Doc MQ Verdict — Wave 2/2

**Plan reviewed:** `docs/plans/2026-05-08-saas-cohort-3-revenue-form-loo.md` (v0.1)
**Reviewer:** Model QA Specialist
**Date:** 2026-05-07
**Default:** REJECT

## Verdict: ACCEPT_WITH_FLAGS

Plan correctly pins three forms, mandates `arviz.compare(ic="loo", method="stacking")` over PyMC posteriors with pointwise log-likelihood, fixes the 4·SE / 2·SE thresholds as `Final` constants, sets the k̂ < 0.7 / >5%-obs FAIL gate, and pre-pins the verdict-routing artifact schema (R5). All nine MQ dimensions hit the bar. Residual issues are FLAG (clarification) not BLOCK (methodology break).

## Dimension-by-dimension

1. **Three forms specified** — PASS. Pin R1 (lines 61–75) reproduces martingale ε_t∼N(0,σ_ε²), AR(1)-log with |ρ|<1, det+churn f(t)=Υ₀(1+g)^t and S_t=∏(1−λ_s) with single Beta-prior λ. Distributions explicit on all three.
2. **PyMC PPC → LOO** — PASS. Line 232 mandates `pm.compute_log_likelihood` (or `idata_kwargs={"log_likelihood": True}` at sample time). Pin R2 (line 77) explicitly REJECTS hand-rolled IC arithmetic. Pointwise log-lik is the LOO input, not MLE point predictions.
3. **`arviz.compare` usage** — PASS. Line 77 pins `ic="loo", method="stacking"` with rationale embedded. Method is named, not silently picked.
4. **ELPD thresholds** — PASS. Pin R3 (lines 83–91) pre-pins PASS at |Δ|>4·SE vs *every* runner-up, INDISTINGUISHABLE at <2·SE, MARGINAL between. Constants are `Final` (line 260) — no runtime override path. Selection rule pre-pinned and immutable.
5. **k̂ < 0.7 PSIS-LOO** — PASS. Pin R4 (line 98) pins k̂<0.7 for ≥95% obs; >5% violation = FAIL on top form. **FLAG-A:** plan does not name LFO-CV as the refit alternative when k̂ violations cluster on time-adjacent obs — Phase-1 Q2 (line 146) flags the LOO-on-dependent-data failure mode but Phase 2 has no LFO-CV branch. Acceptable since Phase-1 reconciliation (1.3) is the gate; surface in CORRECTIONS-α if research returns "LFO required."
6. **No AICc / BIC / DIC / WAIC** — PASS. Line 77 explicitly REJECTS AICc, WAIC-only, DIC. LOO is the canonical choice. Clean.
7. **Verdict-routing artifact** — PASS. Pin R5 (line 102) names `estimates/cohort_3_verdict.json` with full schema: `winning_form`, `verdict`, `delta_elpd_loo`, `se`, `pareto_k_max_per_form`, `weights_per_form`, `audit_block`, `fetched_at_utc`. JSON round-trip in Task 2.5 R5 test.
8. **Anti-fishing on indistinguishability** — PASS. Pin R3 (line 87) and Task 2.3 contract (line 257) require explicit INDISTINGUISHABLE emission, NOT silent default-to-martingale. Pin R6 closure + `CandidateSetClosedError` (line 235) blocks fourth-form smuggling. RC Task 4.1 #14 + MQ Task 4.2 #5 verify no runtime threshold override.
9. **Stationarity / unit-root** — PARTIAL. Line 233 pins ρ∼Normal(0, 0.5) truncated to |ρ|<1 — prior enforces stationarity. **FLAG-B:** plan has NO posterior-side check for ρ posterior mass piling up at the |ρ|=1 boundary (near-unit-root degeneracy). Pre-mortem 3.5 (line 357) lists "AR(1)-log with ρ prior pinned at ±1 boundary" as a sampler fragility but routes it to convergence diagnostics, not to a non-stationarity HALT. Recommend FLAG-B remediation: add a posterior-tail diagnostic (e.g., P(|ρ|>0.95) > threshold) → WEAK or HALT routing in v0.2 CORRECTIONS-α. Not a BLOCK because R4 R̂ + ESS gates will catch most pathologies and the truncated prior is already a hard constraint.

## Cross-cutting strengths

- Pin R6 anti-fishing closure is enforced at TWO layers: (i) `Final` thresholds in modules, (ii) runtime guard `CandidateSetClosedError` on fourth-form registration. Belt + suspenders.
- Diagnostic gates (R4) are in `RevenueFormFit` Value type — gate state is data, not exception, preventing silent retry-until-pass loops.
- Task 4.2 MQ spec-doc reverify (lines 422–433) independently audits Pins R1–R6, including #6 silent-fishing check (default `target_accept` biasing toward one form) — explicit guard against tuning-as-fishing.
- §5.2 prior brackets are referenced as immutable per Pin R6.

## FLAGs (not BLOCKs)

- **FLAG-A** (Pareto-k → LFO-CV): Phase-1 Q2 surfaces the LOO-on-dependent-data concern but Phase 2 has no LFO branch. If Phase 1 returns "LFO required for time-series," v0.2 CORRECTIONS-α must add it. Currently routed via Phase-1 reconciliation gate, acceptable.
- **FLAG-B** (ρ near-unit-root posterior diagnostic): truncated prior enforces stationarity; posterior boundary-mass diagnostic is missing. Add P(|ρ|>0.95) reporting in `RevenueFormFit` and wire to WEAK/HALT in v0.2.

## Disposition

ACCEPT_WITH_FLAGS. Plan is methodologically sound for SAAS-COHORT-3 dispatch. FLAG-A and FLAG-B route through CORRECTIONS-α in v0.2 after Phase 1 reconciliation closes; neither blocks Phase 2 dispatch given Pin R6 closure and R4 gate enforcement.

End of verdict.
