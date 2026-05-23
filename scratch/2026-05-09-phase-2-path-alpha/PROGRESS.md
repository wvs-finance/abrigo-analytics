# SAAS-COHORT-CLOSE Phase 2 — Path α — PROGRESS

**Date launched:** 2026-05-08
**Phase:** P2 (MC budget Path α — brute N_draws bump)
**Plan reference:** `docs/plans/2026-05-09-saas-cohort-close.md` §"Phase 2 — COHORT-1 MC budget on real C1 (Path α)"
**Spec posture:** v1.2 unchanged. NO spec amendment shipped (Path α requires none — see CORRECTIONS-α v0.1→v0.2 BLOCK-1 in plan).

## Bump

| Quantity                  | v0.4 baseline | Path-α run         |
| ------------------------- | ------------- | ------------------ |
| `DRAWS_PER_CHAIN`         | 4 000         | **178 000**        |
| `N_CHAINS`                | 4             | 4 (unchanged)      |
| Total N_draws             | 16 000        | **712 000 ≈ 7.1e5** |
| `target_accept`           | 0.95          | 0.95 (unchanged)   |
| `random_seed`             | 42            | 42 (unchanged)     |
| `n_builders`              | 1 000         | 1 000 (unchanged)  |

Plan pin: "≈ 7.1e5 (or smallest power-of-two-friendly N satisfying stderr/Ẑ
< 1e-3 at CV=0.84 per pilot test)" — `docs/plans/2026-05-09-saas-cohort-close.md`
Task 2.2 Step 1, l. 163. 712 000 satisfies the ≈ 7.1e5 plan pin and keeps
4-chain symmetry. Spec §8(8) per-chain ≥ 4000 floor satisfied (going UP,
44.5× above floor).

## Run handle

| Field             | Value                                  |
| ----------------- | -------------------------------------- |
| **PID**           | **228868**                             |
| Working dir       | `/home/jmsbpp/apps/abrigo-analytics`   |
| stdout log        | `/tmp/c1-emit-pathα-stdout.log`        |
| stderr log        | `/tmp/c1-emit-pathα-stderr.log`        |
| Launch verified   | NUTS multiprocess (4 chains in 4 jobs) confirmed in stderr |
| Sampler           | NUTS on `[pi, mu, phi, alpha_pareto, x_m]` |

## Estimated wall-clock

Baseline: 4 000 draws/chain → ~607 s sampling (per v0.4 baseline run).
Linear scaling on draw count → 178 000 / 4 000 = 44.5×.

**Estimated sampling time: ~7.5 hours (≈ 27 000 s).**

Post-sampling: prior-predictive (178 000 draws) + 3-month emission loop
adds modest overhead. **Total wall-clock estimate: ~8 hours.**

## Expected MC stderr/Ẑ post-fit

Per user task spec formula: `1e-3 / sqrt(178000/4000) = ~1.5e-4` per chain
basis. Cross-checked: actual scaling `1.32e-2 / sqrt(712000/16000)
= 1.32e-2 / 6.67 ≈ 1.98e-3`. Discrepancy noted between user formula and
direct MC stderr-scaling formula — **post-fit verify (Task 2.3) will
adjudicate empirically against the 1e-3 ceiling**. If empirical
stderr/Ẑ > 1e-3, HALT + CORRECTIONS-α (Task 2.3 Step 3) — NO budget
relaxation.

## Spec invariants to verify post-fit (Task 2.3)

- r̂ ≤ 1.01
- ESS_bulk + ESS_tail ≥ 400
- divergence_frac ≤ 0.005 (0.5%)
- per-chain sim-floor ≥ 4000 (trivially satisfied at 178 000)
- §8(7) CI-width ratio ≤ 2.0
- §8(8) MC error budget: stderr/Ẑ < 1e-3 (the Path-α target)
- 5-TP sign cert PASS preserved vs. v0.3 baseline (no flips)

## Anti-fishing posture

- Path α is a **run-config-only change**. NO model surgery (priors.py,
  model.py, diagnostics.py untouched).
- Spec v1.2 unchanged. NO amendment to v1.3 (Path β was rejected by
  2-wave verify as anti-fishing-suspect retro-fit).
- DRAWS_PER_CHAIN went UP (4000 → 178 000); spec floor §8(8) preserved.
- MC error budget ceiling 1e-3 preserved (NOT relaxed). If post-fit
  empirical stderr/Ẑ ≥ 1e-3, HALT-route per Task 2.3 Step 3.
- C1 MQ-FLAG-1 (`pi` posterior structurally near-prior) is NOT resolved
  by Path α; routes to Phase 3 Task 3.1 as a one-line caveat in C1 plan
  v0.4 §"v0.3 → v0.4" (per CORRECTIONS-α v0.2 BLOCK-1).

## Files touched

- `scripts/run_cohort1_emit.py` — DRAWS_PER_CHAIN: 4000 → 178_000;
  docstring caveat noting Path-α run.
- `scratch/2026-05-09-phase-2-path-alpha/PROGRESS.md` — this file.

## Next steps (orchestrator)

1. Wait ~8 hours for sampler completion. Check via `ps -p 228868`.
2. On exit-0: dispatch Task 2.3 (RC + MQ 2-wave verify on stderr/Ẑ,
   sign-cert stability, identification, posterior diagnostics).
3. On exit-2 (HALT) or non-zero: inspect logs, surface CORRECTIONS-α.
