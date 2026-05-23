# Model QA Specialist — Wave 2 verdict on `2026-05-08-saas-cohort-1-t1-cost-posterior.md`

**Plan:** `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md` v0.1
**Spec authority:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1
**Wave:** 2 of 2 (statistical-correctness audit)
**Default verdict:** REJECT.

## Verdict: REJECT

5 BLOCKs + 4 FLAGs identified. Plan must be revised to v0.2 with a CORRECTIONS-block before sub-task dispatch.

---

## BLOCKs (math-contract integrity failures)

### BLOCK-1 — `synthetic_tau_t.parquet` schema mismatch with shipped writer (M4 violation)

**Plan line 62 (verbatim):** *"columns: `month`, `simulation_id`, `tier_id`, `r`, `p`, `alpha`, `x_m`, `tau_t`, `q_t_usd`, `q_t_cop`."*

**Shipped writer** `simulations/utils/parquet_io.py:44-56` declares 11 columns including `schema_version` (also required for `cohort_prior.parquet` at lines 34-41). The writer's `_check_columns` (line 311) will raise on emission. Spec §10 line 517 also omits `schema_version`, so the spec-vs-code drift is real, but the plan claims M4 is "already encoded" (line 62) and asserts column-by-column conformance — it does not. **Both M4 lists in the plan are wrong by one column.** Phase-4 will fail under Reality Checker's M4 round-trip property (Task 3.3 property #4) because the plan's column set will not round-trip through the writer. Either (a) plan adds `schema_version` to both Pin M4 lists, or (b) a SIM-INFRA follow-up strips `schema_version` from the writer — the plan must pick one and HALT-route the other per its own §3 rule "Any modification request triggers HALT and a SIM-INFRA follow-up plan" (line 86).

### BLOCK-2 — NegBin parameterization unspecified

Plan line 15, 184-185, 208 reference `NegBin(r, p)` only. PyMC `pm.NegativeBinomial` natively accepts both `(alpha, mu)` (mean-dispersion) AND `(n, p)` (Pascal/count-success) parameterizations; sklearn/scipy use yet another `(n, p)`. Spec §5.2 line 318 anchors over-dispersion to "p90/mean = 30/13 ≈ 2.3×" — a **mean/dispersion** ratio, which only makes contractual sense under the `(mu, alpha)` parameterization. The plan never disambiguates. Implementing AI Engineer (Task 2.2) cannot author an unambiguous prior without this; a `(r, p)` reading with `r` as the success-count and `p` as Bernoulli probability would silently misparameterize the over-dispersion anchor. **Required fix:** plan must pin `pm.NegativeBinomial(mu=μ, alpha=φ)` with `Var = μ + μ²/φ`, and the prior must target `μ ≈ 80` (per §5.2 turns/active-day median) and `φ` calibrated to deliver the 2.3× over-dispersion ratio.

### BLOCK-3 — Compound-Poisson × TruncPareto cluster process arithmetic-vs-distributional conflation

Spec §5.1 (T1) defines `τ_t = Σ_{j=1}^{D_t} Σ_{i=1}^{N_j} τ_{j,i}` — a **doubly-stochastic compound sum** over days × turns. Plan line 15 collapses this to *"per-user monthly turn-count Nj ~ NegBin(r,p) × per-turn token consumption following the Compound-Poisson × TruncPareto cluster process"* — which is **not** the spec's structure. The spec has NegBin per **active day**, not per **month**. Plan line 184 says "Daily turn count Nj" but line 15 (the architectural pin the AI Engineer reads first) says "monthly turn-count" — internal contradiction. The Compound-Poisson reference in line 15 has no spec anchor; spec §5.1 (T1) is a NegBin × TruncPareto compound sum, NOT a Poisson cluster process. The Compound-Poisson form only appears as one *sensitivity arm* candidate (spec §5.1 (c) Markovian session-state). **Implementer will translate the wrong primary likelihood.** Required fix: plan line 15 must read "per-user **per-active-day** turn-count `N_j ~ NegBin(...)`, summed over `D_t≈22` days × `N_j` turns of TruncPareto-distributed tokens" with no mention of "Compound-Poisson" at the primary level.

### BLOCK-4 — Stationary-bootstrap rejection enforced but posterior-predictive draws not pinned for tau_t emission

Spec §7 (line 414-418) replaces stationary bootstrap with `pm.sample_posterior_predictive` (MQ-BLOCK-7 fix, v1.0→v1.1). Plan does not mention "posterior_predictive" anywhere — it only refers to "posterior draws" (lines 13, 15, 264, 273) and "smoke-emit a 100-draw test fixture" (line 276). The `synthetic_tau_t.parquet` columns (`tau_t`, `q_t_usd`, `q_t_cop`) are **functions of latent parameters AND new τ_{j,i} draws** — these REQUIRE posterior-predictive sampling, not posterior parameter draws. Ambiguity here will produce parameter-only draws (`r`, `p`, `alpha`, `x_m`) without τ_t realizations, breaking spec §10 schema. Required fix: Task 2.4 brief must explicitly require `pm.sample_posterior_predictive` for the τ_t/q_t_usd/q_t_cop columns; Task 3.3 hypothesis property must verify τ_t draws have within-row variance >0 across simulation_ids at fixed (r,p,α,x_m) parameter draws.

### BLOCK-5 — Diagnostic gates miss two spec §8 invariants

Plan line 66 pins `r̂ ≤ 1.01`, ESS ≥ 400, divergences ≤ 0.5%. Spec §8(8) requires **ESS_bulk ≥ 400 AND ESS_tail ≥ 400** (two thresholds, not one). Plan collapses to a single `ess_min` field (line 242). Tail-ESS failure on heavy-tailed TruncPareto α posterior is the *most likely* diagnostic violation given §8(6) α-floor proximity — and the plan would silently pass it. Additionally, spec §8(7) posterior CI-width threshold (posterior 95% CI ≤ 2× prior 95% CI) is **not** a Phase-4 gate in the plan — it appears only in the Wave-2 audit brief (line 376) as "shrinkage" non-blocking surfacing. Spec §8(7) is a NON-NEGOTIABLE anti-fishing invariant; the plan demotes it to advisory. Plan also omits PSIS-LOO `k̂ < 0.7` — but COHORT-1 is not running model selection (deferred to COHORT-3), so this is correctly out-of-scope (no BLOCK on k̂; FLAG-D below).

---

## FLAGs (non-blocking but must surface)

### FLAG-A — TruncPareto α-floor: dual enforcement satisfied; one rough edge

Plan line 58 + line 465 correctly dual-enforce: priors.py lower-bound (Bayesian) AND samplers.py refusal (Callable). Task 2.1 line 186 mandates `__post_init__` checks `alpha_lower: Final = 1.5`. Task 3.3 hypothesis property #2 verifies sampler-prior consistency. **However**, the plan does not pin the *form* of the lower-bounded prior — it suggests "`α ~ 1.5 + Gamma(·)` or a TruncatedNormal lower-bounded at 1.5" (line 58). The two have very different tail behavior. Spec §5.2 brackets `α ∈ [1.5, 2.5]` so the natural form is `pm.Bound`-shifted or `pm.TruncatedNormal(lower=1.5, upper=2.5)`. Pre-mortem (Task 3.5) is supposed to catch divergence-cluster-near-1.5 boundary; FLAG it explicitly as a Task 2.1 dispatch input.

### FLAG-B — Tier Categorical + Dirichlet hyperprior encoded faithfully but α₀=10 vector ambiguity

Plan line 64, 187 correctly encode `α₀ = 10 · [0.20, 0.50, 0.30] = [2.0, 5.0, 3.0]`. The vector sums to 10 (concentration=10). `pm.Dirichlet(a=[2.0, 5.0, 3.0])` is unambiguous. Plan is correct. **However**, line 187 says `__post_init__` "asserts elementwise" — assert what tolerance? Floating-point exact equality on [2.0, 5.0, 3.0] is fine for Python literals but fragile if computed as `10 * [0.20, 0.50, 0.30]` (0.20 is not float-exact). Specify `math.isclose(rel_tol=1e-12)` in Task 2.1 brief.

### FLAG-C — AICc correctly absent; model-selection scope correctly deferred

Plan does NOT use AICc anywhere (verified via document inspection). Spec §7 (line 420) replaces AICc with PSIS-LOO-CV. Plan correctly defers model-selection to COHORT-3 (line 25, 504 of spec). PASS on dimension #7.

### FLAG-D — Sample-size guard `N_min=75` semantically misapplied

Plan line 244 imports CLAUDE.md `N_MIN=75` as a "monitored-parameter × posterior-draw count yields effective N < 75 post-thinning" check. Spec §8 declaration (line 432-439) explicitly states `N_MIN=75` binds **Stage-3 cohort survey**, NOT Stage-2 synthetic-Bayesian calibration. The plan re-imports it as a posterior-thinning guard, which has **no spec anchor**. This is harmless (overconservative) but conceptually wrong; the spec §8(8) sim-count floor is `≥4000 draws × ≥4 chains`, NOT `N=75`. Strip the `n_min_violated` field from `DiagnosticVerdict` or rename it to `sim_count_floor_violated` and pin it to spec §8(8).

---

## Methodology-audit dimension matrix

| # | Dimension | Status |
|---|---|---|
| 1 | TruncPareto α-floor dual-enforcement | PASS w/ FLAG-A |
| 2 | NegBin (r,p) vs (μ,φ) parameterization | **BLOCK-2** |
| 3 | Compound-Poisson × TruncPareto turn-process translation | **BLOCK-3** |
| 4 | Tier-Categorical + Dir(α₀=10·[.20,.50,.30]) encoded | PASS w/ FLAG-B |
| 5 | r̂≤1.01 / ESS≥400 / div≤0.5% / k̂<0.7 HALT-gated | **BLOCK-5** (ESS_bulk vs ESS_tail; CI-width §8(7) demoted) |
| 6 | Output schema match column-by-column | **BLOCK-1** (`schema_version` missing) |
| 7 | AICc absent | PASS (FLAG-C) |
| 8 | Stationary bootstrap absent; posterior-predictive used | **BLOCK-4** (posterior-predictive not pinned for τ_t emission) |

---

## Required actions

1. Plan v0.2 with CORRECTIONS-block addressing BLOCK-1..5 verbatim per spec authority.
2. Re-dispatch Wave-2 reverify on v0.2 before sub-task dispatch authorization.
3. FLAG-A..D addressable inline in v0.2 or deferred to Task-2 dispatch briefs with explicit citation.

**Verdict: REJECT.** Sub-task dispatch NOT authorized.

---

**MQ Analyst:** Model QA Specialist (Wave 2)
**Audit date:** 2026-05-07
**Spec authority sha:** v1.1.1
