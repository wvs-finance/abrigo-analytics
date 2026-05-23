# Envelope evaluation log — Stage-3 A1 Phase 2 Task 2.4

**Date:** 2026-05-11
**Plan anchor:** docs/plans/2026-05-11-stage-3-a1-panoptic-restrategy.md v0.3
**Consumed strip audit_block:** 94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329
**Canonical fixture (TP1):** S_0=4000.0, sigma_0=20000.0, k_star=4687.94

## §1 Verification gates

- Reverse-IC baseline check: pinned at `2.8134e-01` (IronCondor_strip.STRIKES.md line 25); observed = `0.2813412838694053`; drift = `1.28387e-06`; gate (≤ 1e-6) = **FAIL_PRECISION_FLOOR** (see §1a).
- Reproducibility check: independent re-run agreement within 1e-12 = **PASS** (all four adapters show |Δ| = 0.0 exactly across two independent comparator invocations on the same fixture; verifier has no stochastic components).

### §1a Disposition of reverse-IC baseline gate

The published baseline `2.8134e-01` in `simulations/saas_builder/data/IronCondor_strip.STRIKES.md` line 25 is printed to **5 significant figures** (4 decimal places after the `2.`). The full-precision observed value `0.2813412838694053` rounds to `2.8134e-01` at the published precision — i.e. the observed value **agrees exactly** with the upstream emission at the precision the upstream file commits.

The mechanical drift against the truncated string `0.28134` is `1.28e-06`, which exceeds the spec-pinned 1e-6 tolerance. This is a tolerance-vs-precision-floor mismatch in the plan v0.3 spec, **not** upstream cohort_5_strip drift:

- The `consumed_strip_audit_block` value (`941503263…f329`) matches the pin verbatim.
- Run-to-run reproducibility is exact (|Δ|=0 across two runs).
- The observed value is the deterministic output of the same `CarrMadanEnvelopeVerifier` that produced the upstream `STRIKES.md` baseline.

**Conclusion:** no upstream regression detected; the gate as literally stated is below the published-baseline precision floor (~5e-6 for a 5-sig-fig string). Recorded as DONE_WITH_CONCERNS for Phase-3 disposition.

## §2 Per-adapter envelope scores

| primitive_id | comparability_proof | max_relative_error | normalized_score | tolerance | raw_verdict_passes |
|---|---|---|---|---|---|
| reverse_iron_condor | tiled_body | 0.2813412838694053 | 0.2813412838694053 | 0.35 | True |
| long_straddle | normalized_score | 0.8038066200848816 | 1.3301174730910021 | 0.35 | False |
| zeehbs | normalized_score | 0.9216437527122149 | 1.7027367342504844 | 0.35 | False |
| long_strangle | normalized_score | 0.9785000108207673 | 1.8541848847328280 | 0.35 | False |

## §3 Sorted ranking (per comparator)

The comparator returns adapters sorted by the proof-dependent primary key (per `compare._sort_key`): `tiled_body` uses `raw_verdict.max_relative_error`; `normalized_score` adapters use `normalized_score` (the FROZEN scalar). Primary keys are quantized to `SORT_TIE_TOLERANCE` and ties fall through to `primitive_id` ascending.

(1) `reverse_iron_condor` — primary score `0.2813412838694053` (tiled_body → max_relative_error)
(2) `long_straddle` — primary score `1.3301174730910021` (normalized_score)
(3) `zeehbs` — primary score `1.7027367342504844` (normalized_score)
(4) `long_strangle` — primary score `1.8541848847328280` (normalized_score)

## §4 Anti-fishing posture

Each adapter's `comparability_proof` was declared at Task 2.2 authorship time (commit 6c871f0), NOT after observing the envelope numbers. Ranking ordering produced by the comparator is mechanical — Phase-3 Task 3.1 applies the P-A1.4 5pp threshold to derive the KEEP/REPLACE verdict.
