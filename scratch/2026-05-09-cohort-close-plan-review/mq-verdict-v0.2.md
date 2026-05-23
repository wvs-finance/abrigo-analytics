# MQ Verdict — SAAS-COHORT-CLOSE plan v0.2 (reverify)

**Plan:** `docs/plans/2026-05-09-saas-cohort-close.md` v0.2
**Reviewer:** Model QA Specialist (independent, reverify)
**Date:** 2026-05-08
**Prior:** v0.1 REJECT — 3 BLOCKs + 5 FLAGs

---

## Verdict: **ACCEPT_WITH_FLAGS**

All 3 v0.1 BLOCKs verifiably resolved. All 5 v0.1 FLAGs folded with line-pinned fixes. No new BLOCKs introduced. Two LOW FLAGs raised against the v0.2 patch surface itself; both non-blocking.

---

## BLOCK resolution audit

### v0.1 BLOCK-1 (Path β → Path α) — RESOLVED

- **Path α adopted, brute N_draws.** Plan l. 145: *"Path α (brute N_draws ≈ 7.1e5) — deterministic, requires NO spec amendment, faithful to spec v1.1.1 §5.4 (which deferred per-tier θ_k differentiation, not authorized it)."* Task 2.2 Step 1 (l. 163) pins the bump in run-config only; l. 149 *"No code changes to … `priors.py` or `model.py` (model parameterization unchanged)."* Verified: no model surgery.
- **Per-tier θ_k explicitly deferred to Stage-3 (labeled, not silent).** Plan header Out-of-scope l. 25: *"Per-tier θ_k differentiation (deferred to Stage-3 unconditionally per v0.2 CORRECTIONS-α — see §15 BLOCK-1 resolution)."* Cross-referenced at l. 158 (Task 2.1 Step 1) and l. 348 (§15). Verified: deferral is explicit and traceable.
- **C1 MQ-FLAG-1 → one-line caveat (NOT re-parameterization).** Task 2.2 Step 4 (l. 166): *"C1 MQ-FLAG-1 … is **NOT** resolved by Path α — it remains a documented spec-property of Stage-2 … FLAG-1 routes to Phase 3 Task 3.1 as a one-line caveat."* Task 3.1 Step 1 (l. 189) executes: *"add one-line caveat in C1 plan v0.4."* Verified: matches C1 MQ-v0.4 prescription exactly.
- **Path β meta-lesson recorded for Phase 6 Task 6.1.** Plan ll. 31–32, l. 269 (Task 6.1 Step 2): *"Foreground writes `feedback_post_hoc_fit_anti_fishing_pattern.md` with both 1/κ and v0.1 Path β case studies."* §15 BLOCK-1 anti-fishing meta-lesson l. 349 explicitly tags Phase 6 Task 6.1 Step 2. Verified.

### v0.1 BLOCK-2 (Phase 0 pre-determination) — RESOLVED

- **Task 0.1 forbids implementation-anchoring.** Plan l. 77: *"The brief explicitly forbids the agent from anchoring on what C3's existing code computes; the recommendation must be defensible from first principles."* Step 2 (l. 78) requires divergence flag if recommendation ≠ C3 code. Verified.
- **Task 0.2 binds to lit-survey, NOT to C3 v0.3.** Plan l. 82: *"`Model QA Specialist` writes additive amendment to spec §5 pinning $S_t$ to **whatever Task 0.1 recommends** — NOT necessarily the deterministic factor."* Verified: ratification language from v0.1 l. 65 fully removed.
- **Task 0.2b HALT-routes C3 re-fit including ELPD-rank inversion.** Plan l. 87 (header), Step 3 (l. 90): *"Compare new ELPD ranking to v0.3 ranking. If ranking changes, HALT + CORRECTIONS-α + user adjudication (form-choice changing the Det+churn-vs-AR(1)-vs-martingale ranking is a Stage-2 verdict shift, not a spec-amendment housekeeping item)."* Step 5 (l. 92) handles no-op branch. Task 0.3 Step 2 (l. 96) MQ wave checks "if C3 was re-fit, does the new ELPD ranking hold up under k̂ sensitivity?" Verified: rank-inversion case correctly elevated to verdict-shift HALT, not silent ratification.

### v0.1 BLOCK-3 (schema mislabel) — RESOLVED

- **Optional fields default None.** Plan l. 214: *"New per-TP fields are `Optional[…]` in `ZCapPinned` with default `None`."* Task 4.1 Step 1 (l. 227) implements. Verified.
- **Validator accepts both schema_versions.** Plan l. 214: *"The transient Pydantic validator in `simulations/utils/json_io.py` accepts both versions."* Task 4.1 Step 1 (l. 227): *"update transient Pydantic validator to accept both versions."* Verified.
- **Backward-compat round-trip test exists.** Task 4.1 Step 4 (l. 230): *"Add backward-compat round-trip test: load v1.0 fixture → v1.1 reader → v1.1 emit → v1.0 reader. All four steps must succeed."* Verification matrix l. 331 pins evidence at `simulations/tests/saas_builder/test_z_cap_pinned_schema_compat.py`. Task 4.2 Step 1 (l. 234) RC wave re-asserts. Verified.

---

## v0.1 FLAG fold-in audit

| v0.1 FLAG | v0.2 fix location | Status |
|---|---|---|
| RC-FLAG-1 (delegation map) | New table ll. 38–48 | RESOLVED |
| RC-FLAG-2 (P4 RC-only → RC+MQ) | Task 4.2 Step 2 l. 235 adds MQ wave | RESOLVED |
| RC-FLAG-3 (verify matrix) | New table ll. 325–334 | RESOLVED |
| RC-FLAG-4 (plan-version rule) | Task 2.1 Step 2 l. 159 deterministic | RESOLVED |
| RC-FLAG-5 (sidecar removal) | Task 7.5 ll. 315–319 | RESOLVED |
| MQ-FLAG-1 (P1 RC light-pass) | Tasks 1.1/1.2/1.3 Step 5 | RESOLVED |
| MQ-FLAG-2 (P1 HALT) | Task 1.3 Step 3 l. 132 | RESOLVED |
| MQ-FLAG-3 (memo caveat) | Task 5.1 Step 1 (e) l. 252 | RESOLVED |
| MQ-FLAG-4 (memo contradiction) | Eliminated by BLOCK-1 fix | RESOLVED |
| MQ-FLAG-5 (commit msg) | Task 2.2 Step 5 l. 167 `chore(...)` | RESOLVED |

---

## New FLAGs against v0.2

### NEW-FLAG-1 (LOW) — Task 2.2 Step 1 (l. 163): N_draws figure not pinned
Quote: *"bump N_draws … to 7.1e5 (or smallest power-of-two-friendly N satisfying stderr/Ẑ < 1e-3 at CV=0.84 per pilot test)."* The "or smallest" disjunction defers the actual N to a pilot test inside the implementation task. Acceptable as deterministic budget remediation — the criterion (stderr/Ẑ < 1e-3) is the methodologically-binding constraint, and Task 2.3 Step 1 verifies it. Suggest documenting the pilot N in the commit message for audit-trail completeness. Non-blocking.

### NEW-FLAG-2 (LOW) — Task 0.2b Step 4 (l. 91): silent re-fit if ELPD ranking unchanged
Quote: *"IF ranking unchanged, commit re-fit and proceed."* If Task 0.1 recommends a non-deterministic form (e.g., exponential survival) and the ELPD ranking happens to be preserved, C3 is re-fit and committed without independent verify on the new posterior diagnostics (R-hat, ESS, divergences under the new $S_t$). Recommend Task 0.3 Wave 2 MQ check explicitly cover the re-fit posterior diagnostics, not only the ELPD ranking. Plan l. 96 mentions "k̂ sensitivity" — extend to full diagnostic suite. Non-blocking; resolvable in v0.3 self-review.

---

## Methodology audit dimensions — v0.2 coverage

| Dim | Status |
|---|---|
| 1. P0 spec amendment scope | PASS (BLOCK-2 resolved; Task 0.1/0.2 decoupled; Task 0.2b HALT-handles rank inversion) |
| 2. P2 Path α methodology | PASS (BLOCK-1 resolved; spec-faithful; per-tier θ_k → Stage-3 explicit) |
| 3. P4 schema additive semantics | PASS (BLOCK-3 resolved; Optional+None default; both-version validator; round-trip test) |
| 4. P5 modeling memo content | PASS (FLAG-3 folded into Task 5.1 (e)) |
| 5. P1 emission ordering | PASS (unchanged; RC light-pass added) |
| 6. P3 nits sweep | PASS (C1 MQ-FLAG-1 caveat correctly routed) |
| 7. P6 memory hygiene | PASS (Path β case study added; consistent with Phase 2 Path α) |
| 8. HALT triggers | PASS (Phase 1 added; Phase 0 Task 0.2b added) |
| 9. No silent fishing | PASS (Path β demoted; Phase 0 ratification removed) |

---

## Promotion recommendation

**Promote to ACCEPT_WITH_FLAGS.** Plan v0.2 is ready for Phase 0 dispatch. The two NEW-FLAGs are LOW, non-blocking, and resolvable in implementation-time CORRECTIONS-α blocks without re-cycling plan-doc verify.

**Word count: 597.**
