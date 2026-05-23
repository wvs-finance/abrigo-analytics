# Reality Checker — Wave-1 plan-doc verdict on SAAS-COHORT-1 (T1) plan

**Plan reviewed:** `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md` v0.1
**Spec anchor:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1
**Date:** 2026-05-07
**Default verdict posture:** REJECT unless every dimension holds.

## Verdict: REJECT

Two BLOCK-grade contract-mismatch findings against shipped `simulations/modules/pricing.py`. Plan cannot dispatch Task 2.2 as written — the named import does not exist in the codebase, and the asserted API surface (`.price_per_mtok`, tier-string constructor) is not what was shipped. Other dimensions (agent dispatchability, file-path concreteness, anti-fishing posture, audit-pass ordering, wave structure, out-of-scope discipline) all hold.

## BLOCKs

### BLOCK-1 — Misnamed shipped contract: `BlendedPriceCalc` does not exist
**Location:** plan §"Phase 2 prelude — Math pins" Pin M3 (line 60); plan §"File structure" / Architecture (line 15); Task 2.2 inputs (line 210); Task 2.2 behavior contract (line 217); plan §"Notes for plan-doc reverifiers" (line 464); plan §"Verification matrix" (line 432).
**Verbatim quote:** *"the blended-price constant from `BlendedPriceCalc` at default cache hit"* (Pin M3, line 60); *"`BlendedPriceCalc(tier=\"sonnet\").price_per_mtok = 7.1495`"* (line 464).
**Reality:** `simulations/modules/pricing.py` ships **`BlendedPriceFn`** (frozen-dc with field `params: BlendedPriceParams`, callable via `__call__() -> float`). There is no `BlendedPriceCalc` symbol. `__all__ = ["BlendedPriceFn"]` (pricing.py:58).
**Why BLOCK:** the AI-Engineer dispatch brief in Task 2.2 instructs the agent to import a non-existent symbol. Either Task 2.2 is impossible as written, or the agent will silently extend `simulations/modules/` (which the plan itself forbids in §"Out of scope": "any extension to `simulations/{types,modules,utils}/` infrastructure — SIM-INFRA-0 follow-ups").
**Fix:** rename throughout to `BlendedPriceFn`; update API expectations per BLOCK-2.

### BLOCK-2 — Wrong API surface for the blended-price callable
**Location:** Pin M3 (line 60); Task 2.2 behavior contract (line 217); §"Notes for plan-doc reverifiers" (line 464).
**Verbatim quote:** *"`cost_usd = tokens * BlendedPriceCalc(tier).price_per_mtok / 1e6`"* (line 217); *"`BlendedPriceCalc(tier=\"sonnet\").price_per_mtok = 7.1495`"* (line 464); *"asserts the Sonnet tier returns $7.1495 ± 0.0005/MTok at construction"* (line 60).
**Reality:** `BlendedPriceFn(params=BlendedPriceParams(...))` — no `tier=` string keyword, no `.price_per_mtok` attribute. The blended price is obtained by *calling* the instance: `BlendedPriceFn(params)()` returns float $/MTok. Tier selection is implicit in the `(p_in, p_out, w_in, w_out, h_cache)` fields of `BlendedPriceParams`, not a tier-string keyword. The construction-time assertion the plan promises (Sonnet ≈ 7.1495) is structurally impossible: `BlendedPriceFn.__post_init__` validates params, not a tier-conditioned numeric output.
**Why BLOCK:** the model-factory `__post_init__` assertion required by Pin M3 (and again by the docstring requirement in Task 3.2) cannot be coded against the shipped API. The plan's defense-in-depth guarantee for M3 fails at the source.
**Fix:** rewrite Pin M3 + Task 2.2 contract to either (a) call `BlendedPriceFn(BlendedPriceParams.sonnet_default())()` (if such a factory exists or is added under SIM-INFRA-0) and assert ≈ 7.15, or (b) construct the params struct inline and assert call-time output. The 7.1495 ± 0.0005 tolerance must also be reconciled with FLAG-1.

## FLAGs (non-blocking; address in v0.2 alongside BLOCK fixes)

### FLAG-1 — "$7.1495 verbatim from spec §5.1" overstates what spec says
**Location:** plan Pin M3 (line 60: *"Blended Sonnet $/MTok = $7.1495 (spec §5.1; ...)"*); Task 2.2 inputs; §"Notes" (line 464).
**Reality:** spec §5.1 line 254 reads *"≈ 7.15/MTok blended"*; spec §5.4 footnote in shipped pricing.py docstring also rounds to ≈ 7.15. The exact figure 7.1495 is a *recomputation* (0.539·3·0.145 + 0.461·15 = 0.234 + 6.915 = 7.149), not a verbatim spec figure. Plan asserts a 0.0005 tolerance against a number the spec does not pin to four decimals.
**Recommendation:** either (a) reword to "spec §5.1 closed form evaluates to 7.1495; assertion tolerance 0.0005", or (b) widen tolerance to ±0.01 to match the spec's "≈ 7.15" precision.

### FLAG-2 — `synthetic_tau_t.parquet` schema column list omits `schema_version`
**Location:** plan Pin M4 (line 62: lists *"month, simulation_id, tier_id, r, p, alpha, x_m, tau_t, q_t_usd, q_t_cop"*).
**Reality:** `simulations/utils/parquet_io.py` line 8-9 ships the column set *with* a trailing `schema_version` column. Plan's verbatim list under-specifies M4 by one column. If Task 2.4 emits exactly the plan-listed columns, the writer will reject (or silently coerce), depending on how parquet_io enforces.
**Recommendation:** add `schema_version` to the M4 column list verbatim; or cite parquet_io.py module-level constants by name and defer the exact column tuple to the writer.

### FLAG-3 — Phase 0.2 references `memory/project_sim_infra_0_complete.md` which may not exist
**Location:** Task 0.2 step 1.
**Reality:** recent commit log shows `memory: refresh saas-builder Stage-2 state (v1.1.1 REVERIFY-PASSED)` but no SIM-INFRA-0 completion memory file is referenced in the visible commit graph. Task 0.2 says "or equivalent" which is escape-hatch language inviting silent skip.
**Recommendation:** name the exact memory file (e.g., the Stage-2 active memory) or convert step 1 to a sha-pin against the SIM-INFRA-0 PR-merge commit.

## Dimensions confirmed clean

1. **Agent dispatchability** — `engineering-ai-engineer.md`, `engineering-code-reviewer.md`, `engineering-backend-architect.md`, `specialized-model-qa.md` all present in active registry; none under `_archived/`. `gsd-phase-researcher.md` present at agents root. PASS.
2. **File-path concreteness** — every Phase-2 task names exact `simulations/saas_builder/{priors,model,diagnostics,emit}.py` paths; no TBD. PASS.
3. **Math pins M1 / M4 partial reproduction** — M1 (α ≥ 1.5) accurately matches spec §8(6) and shipped `TruncParetoSampler` construction-time check (samplers.py:66). M4 column set matches modulo FLAG-2. PASS with FLAG-2.
4. **Anti-fishing posture** — N_MIN=75, POWER_MIN=0.80, MDES_SD=0.40 cited (line 32). HALT triggers reference `feedback_pathological_halt_anti_fishing_checkpoint` at lines 359, 381, 389. Sign / lag / primary-spec pre-pin asserted (lines 33-34). PASS.
5. **Out-of-scope discipline** — T2, Υ_t, Z-cap, infra extensions, deployment, spec edits all listed under §"Out of scope (explicit, NON-NEGOTIABLE)" lines 24-29. PASS.
6. **Audit-pass chain ordering** — Phase 3 ordering tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing matches Honnibal canonical order and SIM-INFRA-0 precedent (line 287). PASS.
7. **Verifier wave structure** — Phase 4 dispatches Reality Checker (4.1) then Model QA Specialist (4.2) BEFORE Code Reviewer (Phase 5 / Task 5.1). PASS.

## Required actions before promotion to ACCEPT

Author v0.2 with a CORRECTIONS-α block addressing BLOCK-1, BLOCK-2; reconcile FLAG-1 tolerance; add `schema_version` to M4 column listing; pin the SIM-INFRA-0 completion reference. Re-run Wave-1 RC + Wave-2 MQ on v0.2.

**Verdict file:** `/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-08-cohort-plans-review/cohort-1-rc-verdict.md`
