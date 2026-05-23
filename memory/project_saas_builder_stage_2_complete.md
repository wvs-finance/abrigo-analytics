---
name: SaaS-builder Stage-2 — COMPLETE (verdict memo committed)
description: 2026-05-09 Stage-2 cohort instantiation closed. 24/24 Δ < 0 PASS primary + bank-spread; Z_cap pinned at 4,687.94 COP/mo (~$1.17 USD/mo) with strictly positive 95% CI; 5/5 sign-cert TPs PASS. Architecturally consistent under synthetic-Bayesian regime. Verdict memo at docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md. Commit 9fd92e5 on iter/saas-builder-stage-2.
type: project
---

**Iteration ID.** `saas_builder_stage_2`
**Status.** COMPLETE (Stage-2 verdict memo committed; PR #3 ready for finalize).
**Kickoff.** 2026-05-07.
**Closure.** 2026-05-09.

## Empirical verdict

- Δ^(a_s) < 0 strictly across **all 24 spec §5.2 brackets** (3 tiers × 2 α × 2 cache × 2 κ-arm), primary regime + bank-spread overlay (24/24 PASS each).
- Z_cap pinned at **4,687.94 COP/mo (~$1.17 USD/mo at TRM=4000)** with 95% CI [168.17, 14606.14] (TP1; per-TP CIs vary monotonically with FX bracket per Pin M2).
- 5/5 test-point sign certifications PASS at Z = 4,453–4,922 COP/mo across {κ, 0.5κ, 1.5κ, FX=4200, FX=3800}.
- Perpetual identity: sympy exact zero + numerical residual 6.31e-9 over n=5000 grid.
- π(t) is the **dominant scale factor** in Z_cap (|π|_TP1 = 4687.73 vs Z_cap_TP1 = 4687.94 → ~99.99%); small absolute magnitude reflects (X̄/Ȳ)² coupling at calibrated σ₀=20,000, NOT a small-π-vs-baseline split.

**Verdict statement:** the SaaS-Builder cohort hedge is **structurally well-formed / architecturally consistent under the synthetic-Bayesian regime**. Magnitudes are small but architecturally sound. Stage-3 (real-data conditioning) will determine whether real-data magnitudes scale up to be commercially material — that is not a Stage-2 question.

## Branch + PR

- Branch: `iter/saas-builder-stage-2` (origin: JMSBPP/abrigo-analytics)
- Draft PR: https://github.com/wvs-finance/abrigo-analytics/pull/3 (PR #7 finalize via SAAS-COHORT-CLOSE Phase 7)
- HEAD: `9fd92e5` (Stage-2 verdict memo + Phase 4 schema-bump audit)

## Final spec + plan state

- Spec: v1.2.1 (`docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md`)
  - v1.0 → v1.1 → v1.1.1 → v1.2 → v1.2.1
  - v1.2 amendment: pinned C3 Det+churn $S_t = (1-\lambda)^t$, $\lambda \sim \text{Beta}(4.5, 95.5)$ per lit-survey adjudication
  - v1.2.1 patch: concentration provenance (FLAG-A) + prior-mismatch acknowledgment + Task 0.2b NON-NO-OP routing (FLAG-B)
- Cohort plans (all v0.3 / v0.4 with CORRECTIONS-α blocks):
  - C1 v0.4 (post-marginalization): `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md`
  - C2 v0.3 (post-bracket-re-orient): `docs/plans/2026-05-08-saas-cohort-2-t2-pricing-sign.md`
  - C3 v0.3 (post-LFO-fix + winning_form + dse=0 + multi-sim): `docs/plans/2026-05-08-saas-cohort-3-revenue-form-loo.md`
  - C4 v0.3 (post-anti-fishing remediation): `docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md`
- CLOSE plan v0.2: `docs/plans/2026-05-09-saas-cohort-close.md` (Phases 0-7; through Phase 6 complete)
- Verdict memo: `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md` v1.1

## Three significant methodology corrections during the cycle

1. **C1 v0.3 → v0.4 marginalization** — original `pm.Categorical(tier_idx, shape=(1000,))` + CompoundStep + CategoricalGibbsMetropolis hit r̂=1.115, ESS=38 in real emit (failed §8(8)). Marginalized 3 discrete latents (tier_idx, n_per_day, n_month) out of inference graph; pure NUTS now; sampling 78× faster (607s → 7.8s). Phase 2 N_draws bump (4000 → 178,000 per chain → 712k total) further increased ESS to 338,540.
2. **C2 v0.2 → v0.3 bracket re-orientation** — original (ε, ω) sweep mis-oriented; spec §5.2 lines 383-388 require parameter brackets. Re-oriented to 24-cell parameter family. `object.__new__` frozen-dc bypass replaced with `tuple[BracketPoint, ...]` gate API. Tautological PASS/FAIL tests replaced with deterministic forcing fixtures.
3. **C4 v0.2 → v0.3 anti-fishing remediation** — original π(t) had spurious `1/κ` factor invented to satisfy plan v0.2 M2 (∂|π|/∂κ < 0). Independent MQ flagged as anti-fishing violation. Forward-fix re-derived π(t) from PRIMITIVES (no κ multiplier — κ structurally not a free symbol); restored (X̄/Ȳ)² factor; fixed σ₀ anchor (= xy²·ε²/8 per PRIMITIVES §6 eq. 8 inversion); pre-registered new sign expectation `∂|π|/∂(X̄/Ȳ) > 0` in plan v0.3.

## Independent audit trail

31 verdict files across 7 audit cycles in `scratch/2026-05-08-saas-cohort-{1,2,3,4}-independent-audit/` + `scratch/2026-05-09-spec-v1.2-review/` + `scratch/2026-05-09-cohort-close-plan-review/` + `scratch/2026-05-09-phase-4-schema-bump-review/` + `scratch/2026-05-09-stage-2-memo-review/` + `scratch/2026-05-08-cohort-plans-review/`. 17+ BLOCKs caught only by independent audit; self-grading caught zero.

## End-to-end test suite

- 423 tests passing at HEAD (vs 415 pre-Phase 3 nits, 411 mid-CLOSE-Phase-1, 226 baseline post-SIM-INFRA-0)
- 99% coverage on `simulations/{types,modules,utils}/`; 86-90% on `simulations/saas_builder/{cohort_2,cohort_3,cohort_4}/`
- ruff + ty clean

## Open / out-of-scope (Stage-3 readiness checklist)

- Real-data conditioning of C1 (per spec §5.4 hint)
- Per-tier θ_k differentiation (resolves C1 MQ-FLAG-1: π posterior structurally near-prior under shared θ_k)
- Hierarchical pooling for C3 (resolves `_first_trajectory` single-trajectory limitation)
- Weibull k≠1 falsification of $S_t$ (nested null pinned in spec v1.2.1 §6.1)
- On-chain Panoptic 12-leg IronCondor strip per PRIMITIVES.md §20 (deployment-stage)
- LP capital + execution test

## Pipeline next (CLOSE plan Phase 7)

- Phase 7: PR #3 finalize — convert WIP→ready; final review; merge or close per `feedback_no_merge_without_approval`. Delete `iter/saas-builder-stage-2` branch post-merge.

## Methodology lessons memorialized

- `feedback_self_grading_vs_independent.md` — 17+ BLOCKs caught only by independent RC + MQ + CR
- `feedback_post_hoc_fit_anti_fishing_pattern.md` — C4 v0.2 1/κ case study
- `feedback_worktree_agents_no_subdispatch.md` — Claude Code harness invariant; orchestration pattern
