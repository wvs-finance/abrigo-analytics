---
artifact_kind: independent_methodology_audit_verdict_reverify
auditor: Model QA Specialist (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-08
target_artifact: docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md (v1.2.1; 1078 lines)
predecessor_audit: scratch/2026-05-09-spec-v1.2-review/mq-verdict.md (MQ ACCEPT_WITH_FLAGS on v1.2; FLAG-A + FLAG-B)
default_verdict: REJECT
---

# MQ Reverify Verdict — Spec v1.2 → v1.2.1 Patch

**Verdict: ACCEPT** (no residual FLAGs; both v1.2 FLAGs verifiably resolved; no new BLOCKs introduced; audit-trail integrity preserved).

---

## FLAG-A (concentration provenance) — RESOLVED

§6.1 L452–477 adds a 3-pronged "Concentration-provenance defence" paragraph. Each prong checked:

- **(i) Upper exclusion (>10%/mo)** — L455–461: "at concentration 100, prior mass on $\lambda > 0.10$/mo is $\approx 1.5\%$… SURVEY.md citation 5 … tail beyond 10%/mo not observed in any cited prosumer cohort." Numerically verified in v1.2 audit (Pr(λ>0.10)=0.0151). The exclusion is grounded in the cited prosumer-segment empirical range, not retro-fit. **Sound.**
- **(ii) <50 rejection (contractual-billing cohort)** — L461–469: "lower concentrations admit material prior mass on $\lambda > 0.15$/mo … inconsistent with the cohort's wage-funded recurring-purchase model — the cohort has *contractual monthly billing* (SURVEY.md §3.1 distinguishing from BG/NBD non-contractual setting)." The reasoning is methodologically valid: contractual-billing cohorts have per-period unsubscribe-vs-renew bounded churn, and BG/NBD-style heavy-tailed priors are inappropriate. The argument distinguishes Stage-2 synthetic-Bayesian regime (no panel shrinkage) — correctly noting prior dominance risk. **Sound.**
- **(iii) >200 rejection (Stage-3 falsification capacity)** — L469–477: "concentrations $>200$ overconfidently constrain Stage-3 falsification — the Stage-3 Weibull-$k$-vs-exponential test … requires posterior shrinkage capacity from real survival panel data, which a too-tight Stage-2 prior would suppress." This explicitly preserves the §6.1 Stage-3 falsification path (L479–487, k≠1 LR test). The reasoning is correct: a too-tight prior would dominate a finite Stage-3 panel and suppress the falsification signal. **Sound.**

The defence is independent-benchmark-grounded, not posterior-targeted. FLAG-A discharged.

## FLAG-B (Task 0.2b NO-OP) — RESOLVED

Four sub-requirements all met:

1. **Prior delta acknowledged** — §15.4 L890–898: "C3 v0.3 was implemented with $\lambda \sim \mathrm{Beta}(2.0, 38.0)$ … spec v1.2 pins $\lambda \sim \mathrm{Beta}(4.5, 95.5)$ … The priors are **NOT equivalent** — they differ in both location ($0.050$ vs $0.045$) and concentration ($40$ vs $100$, a factor of $2.5\times$ in informativeness)." ✅
2. **NON-NO-OP routing** — §15.4 L900–912 specifies the literal `priors.py` line edit (`DET_CHURN_LAMBDA_BETA_A = 2.0` → `4.5`; `_B = 38.0` → `95.5`), full PSIS-LOO-CV re-run, and re-issued §9 verdict. ✅
3. **HALT-on-flip preserved** — §15.4 L914–919: "The HALT-on-flip safeguard from CLOSE plan v0.2 Phase 0 Task 0.2b **remains in force**." ✅
4. **Anti-fishing posture (lit-grounds-before-code)** — §15.4 L928–936: "The $\mathrm{Beta}(4.5, 95.5)$ prior was selected on independent literature grounds … **before** the v1.2 author inspected `cohort_3/priors.py`." Reinforced in §15.7 L1052–1061. ✅

## §15.3 disclaimer — PRESENT

§15.3 L851–871: explicit "v1.2.1 correction" blockquote distinguishes preserved form-coincidence from falsified prior-hyperparameter coincidence. Original v1.2 framing retained verbatim in surrounding prose; correction layered on top. Audit-trail integrity preserved.

## No relabeling check

Beta(4.5, 95.5) UNCHANGED at L438. Mean 0.045, 95% CI [0.013, 0.094] — same numerics as v1.2. Patch is text-only on the spec; pin invariant. ✅

## Anti-fishing posture (§15.7 strictly-tightening assertion)

§15.7 L1005–1008: "(b) **No pin loosened, no candidate added** — patch is strictly tightening: §6.1 adds independent-benchmark provenance for $\alpha_S + \beta_S = 100$; §15.4 escalates Task 0.2b from NO-OP to NON-NO-OP (more verification, not less)." Verified by inspection: §6.1 candidate-set closure (L489–493) unchanged; §8 invariants preserved per §15.5 item 5; §9 thresholds unchanged per §15.7 item 10 (L1070–1072). ✅

## Audit-trail integrity

§15.3, §15.4 retained verbatim with "v1.2.1 correction" preface blockquotes (L853–863, L883–888). No overwriting of historical text. §15.7 explicitly enumerates the v1.2 → v1.2.1 deltas in two tables (L1022–1024, L1038–1043). ✅

## New-BLOCK spot-check

Scanned §6.1 provenance prose, §15.3/§15.4 corrections, §15.7 sub-block. No new claims requiring fresh adjudication. The Task 0.2b re-fit introduces a real downstream verification dependency but that is the point of the FLAG-B remediation, not a methodological hazard. No new BLOCKs.

---

## Files referenced

- `/home/jmsbpp/apps/abrigo-analytics/docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (v1.2.1; §6.1 L399–493, §15.3 L851–879, §15.4 L881–936, §15.7 L994–1077)
- `/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-09-spec-v1.2-review/mq-verdict.md` (predecessor v1.2 verdict)
- `/home/jmsbpp/apps/abrigo-analytics/simulations/saas_builder/cohort_3/priors.py` L42–43 (Beta(2.0, 38.0) — to be edited under Task 0.2b)

**Verdict: ACCEPT.** Both v1.2 FLAGs verifiably resolved. No new BLOCKs. v1.2.1 cleared for CLOSE plan v0.2 Phase 1 dispatch (subject to Task 0.2b NON-NO-OP execution and HALT-on-flip).

End of MQ reverify on spec v1.2.1.
