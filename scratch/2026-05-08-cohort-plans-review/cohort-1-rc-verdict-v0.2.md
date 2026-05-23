# Reality Checker — Wave-1 reverify on SAAS-COHORT-1 (T1) plan v0.2

**Plan reviewed:** `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md` v0.2 (CORRECTIONS-α)
**Predecessor verdict:** `scratch/2026-05-08-cohort-plans-review/cohort-1-rc-verdict.md` (v0.1, REJECT — 2 BLOCK + 3 FLAG)
**Spec anchor:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1
**Date:** 2026-05-07
**Default verdict posture:** REJECT unless every BLOCK is verifiably resolved.

## Verdict: ACCEPT

All v0.1 BLOCKs and FLAGs are resolved against shipped code. No regressions detected on the previously-clean dimensions.

## BLOCK resolutions verified

### RC-BLOCK-1 — Contract name `BlendedPriceFn` — RESOLVED
**Authority:** `simulations/modules/pricing.py:23` (`class BlendedPriceFn`), `:58-60` (`__all__ = ["BlendedPriceFn"]`).
**Plan v0.2 evidence:**
- Pin M3 (line 63): *"Encoded in `simulations.modules.pricing.BlendedPriceFn` (frozen-dc Callable; `__all__ = [\"BlendedPriceFn\"]`)"*.
- Task 2.2 inputs (line 233): *"Symbol verified at pricing.py:23-55 ... The symbol `BlendedPriceCalc` does NOT exist; do not import it (RC-B1 fix)."*
- CORRECTIONS table row RC-B1 (line 532) names every v0.1 site that was rewritten.
- Verification: `grep -n "BlendedPriceCalc"` against the plan returns **0 occurrences**. Symbol fully eliminated.

### RC-BLOCK-2 — API surface (params struct + `__call__`) — RESOLVED
**Authority:** `pricing.py:43` (`params: BlendedPriceParams` field), `:45-55` (`__call__(self) -> float` returning `p.w_in * p.p_in * cache_factor + p.w_out * p.p_out`). No `tier=` kwarg, no `.price_per_mtok` attribute.
**Plan v0.2 evidence:**
- Task 2.2 (lines 243-246): *"Construct `price_fn = BlendedPriceFn(params=params)`. Obtain blended scalar: `price_per_mtok = price_fn()` (CALL the instance — there is no `.price_per_mtok` attribute and no `tier=` keyword; RC-B2 fix)."*
- Line 246: assertion site moved from `__post_init__` (structurally impossible) to model-factory `__call__` site — *"NOT in `__post_init__`, which validates the params struct, not a tier-conditioned numeric output"*.
- Sonnet defaults pinned verbatim (line 510): `BlendedPriceFn(params=BlendedPriceParams(p_in=3.0, p_out=15.0, w_in=0.539, w_out=0.461, h_cache=0.95))()`.

## FLAG resolutions verified

- **RC-FLAG-1** (7.1495 tolerance): widened from ±0.0005 to ±0.01 to match spec §5.1's "≈ 7.15" precision (lines 63, 246, 342, 510). Pin language reworded *"closed-form recomputation evaluates to 7.1495"* (no longer asserted as verbatim spec figure).
- **RC-FLAG-2** (`schema_version` column): added verbatim to both M4 column lists (lines 67-69), with citations of shipped `SYNTHETIC_TAU_COLUMNS` (parquet_io.py:44-56) and `COHORT_PRIOR_COLUMNS` (parquet_io.py:34-41) Final tuples. Round-trip property (Task 3.3 #4) updated to "11 columns including `schema_version`".
- **RC-FLAG-3** (Phase 0.2 escape-hatch): Task 0.2 Step 1 (line 124) now names the exact active memory file via the commit-pinned reference `1a141fe memory: refresh saas-builder Stage-2 state (v1.1.1 REVERIFY-PASSED)`; "or equivalent" removed; HALT-on-miss enforced. Memory file `memory/project_saas_builder_stage_2_active.md` confirmed present.

## Regression spot-check (previously-clean dimensions)

1. **Agent dispatchability** — Phase 4/5 still dispatch Reality Checker → Model QA Specialist → Code Reviewer (lines 49-51, 384, 409, 446). PASS.
2. **File-path concreteness** — `simulations/saas_builder/{priors,model,diagnostics,emit}.py` paths preserved. PASS.
3. **Anti-fishing posture** — N_MIN=75 / POWER_MIN=0.80 / MDES_SD=0.40 + HALT trigger language preserved (lines 32-37, 399). PASS.
4. **Audit-pass chain order** — tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing (line 326, Tasks 3.1–3.6); SIM-INFRA-0 precedent preserved. PASS.
5. **Verifier wave structure** — RC (4.1) before MQ (4.2) before Code Reviewer (5.1). PASS.
6. **Out-of-scope discipline** — preserved; CORRECTIONS-α additions stay within the cohort package boundary; spec §10 column-list drift is HALT-routed not silently fixed (line 71). PASS.

## Required actions

None. v0.2 may proceed to Wave-2 Model QA Specialist reverify. On MQ ACCEPT/ACCEPT_WITH_FLAGS, plan is commit-eligible.

**Verdict file:** `/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-08-cohort-plans-review/cohort-1-rc-verdict-v0.2.md`
