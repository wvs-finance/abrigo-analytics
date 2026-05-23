# SAAS-COHORT-1 Plan v0.2 — Model QA Specialist Reverify Verdict

**Plan:** `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md` v0.2 (CORRECTIONS-α)
**Predecessor verdict:** `cohort-1-mq-verdict.md` v0.1 (REJECT; 5 BLOCKs / 4 FLAGs)
**Authoritative inputs:** spec v1.1.1 §5.1/§5.2/§7/§8(7)/§8(8)/§10; `simulations/types/distributions.py`; `simulations/utils/parquet_io.py`
**Auditor:** Model QA Specialist
**Date:** 2026-05-07

---

## Verdict: ACCEPT

All 5 BLOCKs verifiably resolved against spec and shipped contracts. All 4 FLAGs folded. No new methodology regressions detected.

---

## BLOCK reverify

| ID | Resolution evidence (line refs in v0.2) | Status |
|---|---|---|
| MQ-B1 (`schema_version`) | Pin M4 (L65-72) cites `SYNTHETIC_TAU_COLUMNS` parquet_io.py:44-56 + `COHORT_PRIOR_COLUMNS` parquet_io.py:34-41, both including `schema_version`; Task 2.4 (L310) mandates `synthetic_tau_row` / `cohort_prior_row` factories with `DEFAULT_SCHEMA_VERSION`; Task 3.3 prop #4 (L343) round-trip asserts 11-column set; v0.1→v0.2 spec-§10/code drift documented (L71). | RESOLVED |
| MQ-B2 (NegBin param) | New "NegBin parameterization pin" (L76) pins `pm.NegativeBinomial(mu=μ, alpha=φ)`, anchors μ≈80 + p90/mean≈2.3× to spec §5.2 line 318, documents (μ,φ)→(r,p) reparameterization $r=\varphi$, $p=\varphi/(\varphi+\mu)$ matching distributions.py:193-200 `neg_bin_mean` / `neg_bin_variance`; misparameterized `(r,p)` reading explicitly flagged Phase-4 BLOCK. Task 2.2 (L240) + matrix row (L474) consistent. | RESOLVED |
| MQ-B3 (T1 likelihood) | Architecture summary (L17-18) carries spec verbatim $\tau_t=\sum_{j=1}^{D_t}\sum_{i=1}^{N_j}\tau_{j,i}$ with $D_t\approx22$ + per-active-day NegBin; "Compound-Poisson" stricken from primary and correctly relegated to spec §5.1 sensitivity arm (c) OUT OF SCOPE (L18, L80). New "Likelihood structural pin" (L78-80) restates the doubly-stochastic compound sum; Task 2.2 contract (L240) aligns. | RESOLVED |
| MQ-B4 (posterior_predictive) | New "Posterior-predictive emission pin" (L82) pins `pm.sample_posterior_predictive(idata, var_names=["tau_t","q_t_usd","q_t_cop"])`; Task 2.2 (L247) declares the three as `pm.Deterministic` nodes; Task 2.4 (L307) calls posterior_predictive before emission and routes columns from the `posterior_predictive` group, parameter columns `(r,p,α,x_m)` from `posterior` with reparam at boundary; Task 3.3 NEW prop #6 (L345) verifies within-row variance > 0; Phase-4 MQ brief #5 (L416) reverifies. | RESOLVED |
| MQ-B5 (ESS split + CI-width gate) | Diagnostics pin (L84-88) splits `ESS_bulk≥400 ∧ ESS_tail≥400`; §8(7) explicitly restored as **HALT-gate** "NOT advisory" (v0.1 line 376 demotion called out and reversed); Task 2.3 `DiagnosticVerdict` (L274-279) carries `ess_bulk_min`, `ess_tail_min`, `ci_width_ratio_max` with refusal logic at L280; Task 3.3 prop #5 (L344) splits all four degradations into independent properties; Phase-4 MQ brief #2 (L413) re-elevates §8(7) to BLOCK. | RESOLVED |

## FLAG reverify

- MQ-FLAG-A (TruncatedNormal[1.5, 2.5]): pinned at L208 + Task 3.3 prop #2 + Task 3.5 divergence-cluster pre-mortem. FOLDED.
- MQ-FLAG-B (`math.isclose rel_tol=1e-12`): pinned in tier-prior pin L74 + Task 2.1 contract L209. FOLDED.
- MQ-FLAG-C (PSIS-LOO out of scope): recorded at diagnostics pin item 3 (L88). FOLDED.
- MQ-FLAG-D (`sim_count_floor_violated` rename, N_MIN=75 Stage-3-only): Task 2.3 contract (L277, L281) + diagnostics pin item 1 (L86). FOLDED.

## Methodology regression spot-check

- Anti-fishing invariants verbatim (L34-37): NO drift.
- Out-of-scope list (L26-32) unchanged: T2/Υ_t/Z-cap/spec-edits/deployment all preserved.
- HALT routing on REJECT (L398, L423) cites `feedback_pathological_halt_anti_fishing_checkpoint`: preserved.
- Audit-pass chain order (Phase 3) unchanged: tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing.
- Mutation kill-rate ≥80% / equiv-cap ≤5% (L368-370) preserved.

No regressions.

## Residuals (informational, non-blocking)

- L502 self-review checklist still reads "ESS ≥ 400" + "$N_{\min}=75$" (single-threshold legacy phrasing); body of plan is correct (split + Stage-3-scoped). Recommend a v0.2.1 cosmetic refresh of the checklist line, but body authority dominates — non-blocking.

## Authorization

Sub-task dispatch (Phase 2.1+) AUTHORIZED on this v0.2 ACCEPT verdict per the v0.2 reverify exit criteria (L568-572).
