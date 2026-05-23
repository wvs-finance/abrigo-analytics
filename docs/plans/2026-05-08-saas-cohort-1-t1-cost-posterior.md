# SAAS-COHORT-1 — T1 (subscription-cap) per-user latent-cost posterior (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `feedback_no_code_in_specs_or_plans` (NON-NEGOTIABLE), this plan does NOT contain code blocks. Each task dispatches a specialized agent who authors code per the functional-python skill.
>
> **Foreground orchestrates, never authors.** Per repo memory `feedback_specialized_agents_per_task` (NON-NEGOTIABLE).

**Plan version:** v0.4 (CORRECTIONS-α; marginalizes per-builder Categorical `tier_idx` latent out of the inference graph after the v0.3 emit run produced r̂_max=1.115, ESS_bulk=38, ESS_tail=58 — failing the §8(8) HALT-gate; supersedes v0.3).
**emit_timestamp:** 2026-05-08 (CORRECTIONS-α third pass).
**Predecessor:** v0.3 (DRAFT — code at commit ec26317 produced a structural-mixing failure at the spec §8(8) gate under the explicit-Categorical inference graph; emit log `/tmp/c1-emit-stdout.log`). v0.2 commit 438a01a remains pinned for traceability. SIM-INFRA-0 v1.1.1 REVERIFY-PASSED remains the upstream gate.
**Status:** DRAFT v0.4 — pending re-audit on this CORRECTIONS-α revision. See §"CORRECTIONS-α v0.3 → v0.4" at end of plan for the verbatim resolution table.

**Goal:** Fit and emit the T1 (subscription-cap-regime) PyMC posterior for the per-user monthly latent compute cost on the SaaS-builder cohort, producing tier-conditioned posterior draws + tier-prior summary as Hive-partitioned parquet artifacts to be consumed downstream by COHORT-2 (sign certification), COHORT-3 (Υ_t form), and COHORT-4 (Z-cap pin).

**Architecture:** A single PyMC compound model implementing spec §5.1 (T1) verbatim:
$$\tau_t = \sum_{j=1}^{D_t} \sum_{i=1}^{N_j} \tau_{j,i}, \quad D_t \approx 22,$$
where (a) **per-active-day** turn count $N_j \sim \mathrm{NegBin}(\mu, \alpha_{\mathrm{NB}})$ in PyMC mean-dispersion parameterization (`pm.NegativeBinomial(mu=μ, alpha=φ)`; see §"NegBin parameterization pin" below — MQ-B2), and (b) per-turn token consumption $\tau_{j,i} \sim \mathrm{TruncPareto}(\alpha, x_m, \kappa)$ with α-floor enforced at 1.5 (M1). The compound sum is summed over $D_t$ days × $N_j$ turns; **NOT** a Compound-Poisson cluster process (that label belongs to spec §5.1 sensitivity arm (c), out of scope for this primary fit). Wrapped under a Tier-Categorical latent over (Pro, Max5x, Max20x) with prior $\pi \sim \mathrm{Dir}(\alpha_0)$ per spec §5.2. The model lives in a new `simulations/saas_builder/` cohort package; it imports Value types from `simulations/types/` (notably `NegBinParams`, `TruncParetoParams`, `BlendedPriceParams`), Callable transforms (TruncPareto sampler with M1 enforcement, the blended-price callable `BlendedPriceFn` with M3 = $7.1495/MTok pin) from `simulations/modules/`, and parquet IO writers from `simulations/utils/`. Posterior + posterior-predictive draws are emitted via `simulations/utils/parquet_io.py` (`SyntheticTauWriter`) Hive-partitioned by `tier_id=*/month=*/`; the τ_t / q_t_usd / q_t_cop columns are explicitly populated from `pm.sample_posterior_predictive` per spec §7 (MQ-B4). Diagnostics (r-hat, ESS_bulk, ESS_tail, divergences, posterior-CI-width) gate artifact emission.

**Tech stack:** Python 3.13 + uv + PyMC + arviz + ruff + ty + pytest + Hypothesis. NumPyro/JAX backend permitted at sampler discretion if it improves divergence count; default backend is PyMC's NUTS.

**Spec anchor:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1 — §5.1 (T1 row), §5.2 (tier prior + pricing), §6 (functional-form table), §8(6) (M1 α-floor commitment), §10 (output artifact schemas).

**Sub-task position:** Direct successor of SIM-INFRA-0 v1.1.1 (PASS). Predecessor of SAAS-COHORT-2 (T2 sign certification). Parallel-eligible with SAAS-COHORT-3 (Υ_t form selection). SAAS-COHORT-4 (Z-cap pin) blocks on COHORT-1 ∧ COHORT-2 ∧ COHORT-3.

**Out of scope (explicit, NON-NEGOTIABLE):**
- T2 (rate-card regime) sign certification — SAAS-COHORT-2.
- Υ_t hedge-payoff functional-form selection — SAAS-COHORT-3.
- Z-cap monthly USD/COP pin — SAAS-COHORT-4.
- Any extension to `simulations/{types,modules,utils}/` infrastructure — SIM-INFRA-0 follow-ups.
- Spec edits — locked at v1.1.1; any spec-vs-data contradiction triggers HALT per `feedback_pathological_halt_anti_fishing_checkpoint`, NOT silent threshold tuning (anti-fishing).
- Live deployment / on-chain settlement — Stage-3 work per CLAUDE.md "Ideal-scenario modeling permitted."

**Anti-fishing invariants (carried verbatim from spec §8):**
- $N_{\min} = 75$, $\mathrm{POWER}_{\min} = 0.80$, $\mathrm{MDES}_{\mathrm{SD}} = 0.40$ SD-units of $Y$.
- Sign expectation, lag structure, primary specification PINNED before any data fit. Threshold tuning post-hoc is silent-fishing.
- Spec contradicts data → HALT + disposition memo + ≥3 user-enumerated pivots + CORRECTIONS block + post-hoc 3-way review.

---

## Agents (strategic delegation map)

| Phase | Task | Agent / skill | Rationale |
|---|---|---|---|
| 1 | Prior-elicitation literature pass (conditional) | `gsd-phase-researcher` | Background research on Dirichlet hyperparameter elicitation in subscription-tier mixtures. |
| 1 | Module-boundary review (cohort vs. shared infra) | `Backend Architect` | Confirms `simulations/saas_builder/` placement and import discipline against three-tier rules. |
| 2 | PyMC model + sampler dispatch + diagnostics + artifact emission | `AI Engineer` | Active registry; PyMC + arviz scope. Sole implementer for Phase 2. |
| 3 | Audit-pass chain (six skills, sequential) | foreground invokes skills (`tighten-types`, `contract-docstrings`, `hypothesis-tests`, `try-except`, `pre-mortem`, `mutation-testing`) | Skills, not agents. Same Honnibal sequence as SIM-INFRA-0 Phase 3. |
| 4 | Plan-doc + code-doc verify wave 1 | `Reality Checker` | Active (un-archived). Functional-python compliance + math-pin enforcement audit. |
| 4 | Plan-doc + code-doc verify wave 2 | `Model QA Specialist` | Active (un-archived). Posterior diagnostics + statistical-correctness audit. |
| 5 | Code review | `Code Reviewer` | Independent code-quality reverify. |

`Data Engineer` is NOT used in this plan; PyMC implementation is `AI Engineer`'s scope per the active registry split.

---

## Phase 2 prelude — Math pins (verbatim from spec §5.1)

> These pins are inputs to every Phase-2 task agent dispatch. The implementing agent reads these contracts before authoring code; foreground enforces by including the relevant pin in the dispatch brief.

**Pin M1 — TruncPareto α-floor (spec §8(6); already enforced upstream).** The TruncPareto sampler in `simulations/modules/samplers.py` accepts $\alpha \ge 1.5$ and refuses $\alpha < 1.5$ at sampler-construction time (typed `ValueError`). COHORT-1 PyMC priors on $\alpha$ MUST place 100% mass on $[1.5, \infty)$ — e.g. $\alpha \sim 1.5 + \mathrm{Gamma}(\cdot)$ or a TruncatedNormal lower-bounded at 1.5. Priors that leak below 1.5 are a Phase-4 BLOCK.

**Pin M3 — Blended Sonnet $/MTok ≈ $7.15 (spec §5.1, "≈ 7.15/MTok blended"; closed-form recomputation evaluates to $7.1495). Encoded in `simulations.modules.pricing.BlendedPriceFn` (frozen-dc Callable; `__all__ = ["BlendedPriceFn"]`).** The cost-per-turn likelihood multiplies token counts by the blended-price scalar produced by *calling* a `BlendedPriceFn(params=BlendedPriceParams(...))` instance (no `tier=` keyword and no `.price_per_mtok` attribute exist on the shipped API; the price is the return value of `BlendedPriceFn.__call__()`). Tier selection is implicit in the `(p_in, p_out, w_in, w_out, h_cache)` fields of `BlendedPriceParams` (located in `simulations.types.fx`). COHORT-1 does NOT redefine the formula; it imports `BlendedPriceFn` + `BlendedPriceParams`, constructs the Sonnet-default `BlendedPriceParams` (or uses an upstream-provided factory if one exists in `simulations.types.fx`), and asserts the call-time output equals the spec §5.4 closed form $0.539 \cdot 3 \cdot 0.145 + 0.461 \cdot 15 = 7.1495$ within tolerance ±0.01 (matching spec's "≈ 7.15" precision; resolves RC-FLAG-1). The assertion is invoked AT THE LIKELIHOOD-FACTORY CALL SITE in `model.py.__call__` (NOT in `__post_init__`, which validates the params struct, not a tier-conditioned numeric output — RC-B2 fix). Drift here is a Phase-4 BLOCK.

**Pin M4 — `synthetic_tau_t.parquet` + `cohort_prior.parquet` schemas (spec §10; authoritatively encoded in `simulations/utils/parquet_io.py` Final dtype maps `SYNTHETIC_TAU_DTYPES` and `COHORT_PRIOR_DTYPES`, and the `Final[tuple[str, ...]]` column tuples `SYNTHETIC_TAU_COLUMNS` (parquet_io.py:44-56) and `COHORT_PRIOR_COLUMNS` (parquet_io.py:34-41)).** Posterior emission MUST go through the existing writer (`SyntheticTauWriter`, `CohortPriorWriter`).

- `synthetic_tau_t.parquet` columns (verbatim from shipped `SYNTHETIC_TAU_COLUMNS`): `month`, `simulation_id`, `tier_id`, `r`, `p`, `alpha`, `x_m`, `tau_t`, `q_t_usd`, `q_t_cop`, **`schema_version`**. Dtypes pinned by `SYNTHETIC_TAU_DTYPES` Final map (notably `month: int64`, `simulation_id: int64`, `tier_id: string`, `schema_version: string`).
- `cohort_prior.parquet` columns (verbatim from shipped `COHORT_PRIOR_COLUMNS`): `param`, `percentile`, `value`, `source`, `fetched_at_utc`, **`schema_version`**. Dtypes pinned by `COHORT_PRIOR_DTYPES` Final map.
- Default `schema_version` value supplied by `simulations.types.posterior.DEFAULT_SCHEMA_VERSION` and the convenience row factories `synthetic_tau_row(...)` / `cohort_prior_row(...)` exported from `parquet_io.py`.
- Hive partitioning: `tier_id={pro,max5x,max20x}/month=YYYY-MM/` per `SYNTHETIC_TAU_PARTITION_COLS`.
- The shipped `_check_columns` helper raises `SchemaMismatchError` on any column-set drift; emitter MUST satisfy the writer contract verbatim. No new columns; no column-drop; no dtype coercion. Spec §10 line 517 lists 10 columns (omits `schema_version`); the shipped writer is the authority and supersedes that omission per the v1.1.1 spec → code drift documented under MQ-B1. Per plan §3 rule "Any modification request triggers HALT and a SIM-INFRA follow-up plan" — COHORT-1 conforms to the writer; spec §10 column-list edit is HALT-routed to a SIM-INFRA follow-up if ever needed (NOT in scope here).
- Schema mismatch is a Phase-4 BLOCK.

**Tier prior pin (spec §5.2 verbatim):** $\pi \sim \mathrm{Dir}(\alpha_0)$ with $\alpha_0 = 10 \cdot [0.20, 0.50, 0.30]$ over (Pro, Max5x, Max20x). The numeric vector is `[2.0, 5.0, 3.0]` (concentration = 10). `__post_init__` MUST assert elementwise via `math.isclose(rel_tol=1e-12)` (resolves MQ-FLAG-B; floating-point literal vs. computed-product equality). Hyperparameter is fixed; no hierarchical hyperprior in COHORT-1 (deferred to a future iteration if posterior-predictive checks fail).

**NegBin parameterization pin (spec §5.2 over-dispersion anchor; MQ-B2 fix).** The PyMC layer (`model.py`) MUST instantiate `pm.NegativeBinomial(mu=μ, alpha=φ)` — the **mean–dispersion (μ, α) parameterization** — with $\mathrm{Var} = \mu + \mu^2/\varphi$. Justification: spec §5.2 line 318 anchors over-dispersion to "p90/mean = 30/13 ≈ 2.3×" (a mean/dispersion ratio), and §5.2 line 318 gives $N_j$ turns/active-day median ≈ 80 (mean target). These are mean-scale anchors; only the (μ, α) form allows the prior to target μ directly and calibrate φ to deliver the 2.3× tail/mean. The shipped Value type `simulations.types.distributions.NegBinParams` carries `(r, p)` (its own internal convention, with `r` = dispersion / number-of-failures and `p` = success probability per its docstring); priors.py MUST therefore expose a (μ, φ)-parameterized prior pin AND, where `NegBinParams` instances are constructed for the Callable sampler, perform the canonical reparameterization $r = \varphi$, $p = \varphi/(\varphi + \mu)$ (with corresponding mean $r(1-p)/p = \mu$ and variance $r(1-p)/p^2 = \mu + \mu^2/\varphi$, matching `neg_bin_mean` / `neg_bin_variance` in distributions.py:193-200). Documenting the reparameterization in priors.py module docstring is REQUIRED. A `(r, p)` reading where `r` is a success-count integer and `p` the Bernoulli probability is silently MISPARAMETERIZED against the spec anchor and is a Phase-4 BLOCK.

**Likelihood structural pin (spec §5.1 (T1) verbatim; MQ-B3 fix).** The T1 monthly latent cost is the doubly-stochastic compound sum
$$\tau_t = \sum_{j=1}^{D_t} \sum_{i=1}^{N_j} \tau_{j,i}$$
with $D_t \approx 22$ active days/month (spec §5.1 line 194), per-active-day $N_j \sim \mathrm{NegBin}(\mu, \varphi)$ (NOT per-month; NOT a Poisson), and per-turn $\tau_{j,i} \sim \mathrm{TruncPareto}(\alpha, x_m, \kappa)$ iid (primary spec). The "Compound-Poisson cluster process" is **excluded** from this primary likelihood; it lives only in spec §5.1 sensitivity arm (c) (Markovian session-state) and is OUT OF SCOPE for COHORT-1. Implementations MUST construct the per-day NegBin draw via `pm.NegativeBinomial` and aggregate over $D_t$ days inside the model factory; the per-turn TruncPareto contribution sums (over `N_j` turns) feed the deterministic `τ_t = Σ_j Σ_i τ_{j,i}` accumulator that becomes the τ_t emission column.

**Posterior-predictive emission pin (spec §7 line 415, MQ-BLOCK-7 v1.0→v1.1 fix; MQ-B4).** The columns `tau_t`, `q_t_usd`, `q_t_cop` in `synthetic_tau_t.parquet` are functions of latent parameters AND new draws of the per-turn $\tau_{j,i}$ random variates; they are NOT functions of the posterior parameter draws alone. Emission MUST therefore call `pm.sample_posterior_predictive(idata, var_names=["tau_t", "q_t_usd", "q_t_cop"])` (or the equivalent named-deterministic surface) to populate these columns, NOT raw `idata.posterior` slicing. Stationary bootstrap is structurally absent (spec §7 strip; v1.0→v1.1). Task 2.4 dispatch brief (`emit.py`) MUST encode this requirement; Task 3.3 hypothesis property (added below) verifies within-row variance > 0 in `tau_t` across `simulation_id`s at fixed `(r, p, α, x_m)` parameter draws.

**Diagnostics pin (spec §8(7) + §8(8); this plan; MQ-B5 fix).** Posterior emission is gated on ALL of the following NON-NEGOTIABLE invariants from spec §8; failure of any one triggers HALT, NOT silent reparam:

1. **§8(8) convergence floor:** $\hat R \le 1.01$ on every monitored parameter; **`ESS_bulk ≥ 400` AND `ESS_tail ≥ 400`** on every monitored parameter (TWO thresholds, NOT one — heavy-tailed TruncPareto α posterior is the most likely tail-ESS violator given §8(6) α-floor proximity); divergences $\le 0.5\%$ of post-warmup draws; sim-count floor $\ge 4000$ post-warmup draws × $\ge 4$ chains.
2. **§8(7) posterior-CI-width invariant (HALT-gate, NOT advisory):** for each (T1) parameter $(r, p, \alpha, x_m, \pi, h_{\text{cache}})$, posterior 95% CI width $\le 2 \times$ prior 95% CI width. If exceeded, the data is not informative for that parameter and the emission HALTs per the spec's anti-fishing invariant. v0.1 demoted this to a Wave-2 advisory shrinkage check (line 376); v0.2 restores it as a Phase-4 gate alongside §8(8) (MQ-B5 second arm).
3. PSIS-LOO `k̂ < 0.7` is correctly OUT OF SCOPE for COHORT-1 (model selection deferred to COHORT-3 per spec §9 / TODO-COHORT-3); see MQ-FLAG-C.

---

## File structure (folder-level; .py decomposition is task-time discovery)

```
simulations/
└── saas_builder/                      # NEW (this cohort)
    ├── __init__.py
    ├── README.md
    ├── model.py                       # PyMC model factory (T1 compound + tier mixture)
    ├── priors.py                      # prior pins (Dir tier prior, α-floor-respecting prior)
    ├── diagnostics.py                 # arviz r-hat / ESS / divergence checks
    ├── emit.py                        # artifact emission via simulations/utils/parquet_io.py
    └── data/                          # OUTPUT directory; gitignored
        ├── synthetic_tau_t.parquet/   # Hive-partitioned: tier_id=*/month=*/
        └── cohort_prior.parquet
```

Specific `.py` decomposition inside `simulations/saas_builder/` is decided by the implementing agent at task-time per the functional-python three-tier discipline; the four files above are the minimum surface (model factory, priors, diagnostics, emission). Tier-import discipline preserved: cohort code may import from `simulations/types/` and `simulations/modules/` and `simulations/utils/`, but MUST NOT modify them. Any modification request triggers HALT and a SIM-INFRA follow-up plan.

**Repo-level changes:** add `simulations/saas_builder/data/` to `.gitignore`; update `CLAUDE.md` repo-structure section with the cohort package location (Phase 5).

---

## Phase 0 — Pre-flight

### Task 0.1 — Re-read functional-python skill from disk
Per `feedback_check_functional_python_skill_first` (NON-NEGOTIABLE).

- [ ] **Step 1** — Read `~/.claude/skills/functional-python/SKILL.md` via Read tool.
- [ ] **Step 2** — Confirm contents match the reference recorded in `feedback_check_functional_python_skill_first.md`. Divergence → surface to user before proceeding.
- [ ] **Step 3** — Read-only; no commit.

### Task 0.2 — Confirm SIM-INFRA-0 PASS state
- [ ] **Step 1** — Read the active Stage-2 memory file referenced by recent commit `1a141fe memory: refresh saas-builder Stage-2 state (v1.1.1 REVERIFY-PASSED)`. Confirm verdict REVERIFY-PASSED. (RC-FLAG-3 fix: name the exact memory file referenced by the most-recent state-refresh commit; do NOT use the v0.1 "or equivalent" escape-hatch, which invited silent skip.) If the named memory file is missing, HALT and surface to user — do NOT proceed on a vague predecessor.
- [ ] **Step 2** — Run `pytest simulations/tests/ -v`. All pass.
- [ ] **Step 3** — Run `ty check simulations/`. Zero errors.
- [ ] **Step 4** — On any failure: HALT; SIM-INFRA-0 is the gate, COHORT-1 cannot proceed on a regressing infra layer.

### Task 0.3 — Confirm Python venv + PyMC stack installed
- [ ] **Step 1** — `source .venv/bin/activate`; `python --version` returns 3.13.x.
- [ ] **Step 2** — `uv pip install pymc arviz` (PyMC ≥ 5.10 recommended; constrain by `requirements.txt` if pinned).
- [ ] **Step 3** — `python -c "import pymc, arviz; print(pymc.__version__, arviz.__version__)"`. Record versions in `scratch/2026-05-08-saas-cohort-1-research/STACK.md` (created in Task 1.1).

### Task 0.4 — Confirm working tree clean and on `iter/saas-builder-stage-2`
- [ ] **Step 1** — `git status --short`. Untracked allowed; no staged/modified.
- [ ] **Step 2** — `git branch --show-current`. Expect `iter/saas-builder-stage-2`.

### Task 0.5 — Confirm agent registry state
- [ ] **Step 1** — `find ~/.claude/agents -name 'engineering-ai-engineer*' -o -name 'specialized-model-qa*' -o -name 'specialized-reality-checker*' -o -name 'engineering-code-reviewer*' -o -name 'engineering-backend-architect*'`.
- [ ] **Step 2** — All five appear in active paths (not under `_archived/`). Any in `_archived/` → HALT and surface to user.

---

## Phase 1 — Research and module-boundary review

### Task 1.1 — Prior-elicitation research (gsd-phase-researcher, background, conditional)

**Files:** Create `scratch/2026-05-08-saas-cohort-1-research/RESEARCH.md` and `scratch/2026-05-08-saas-cohort-1-research/STACK.md`.

**Brief.** Research:
1. Dirichlet hyperparameter elicitation patterns for subscription-tier mixtures (≥3 sources). Validate the spec §5.2 $\alpha_0 = 10 \cdot [0.20, 0.50, 0.30]$ choice as plausible vs literature; do NOT propose changes (anti-fishing).
2. PyMC NUTS reparameterization patterns for compound (NegBin × Compound-Poisson × TruncPareto) likelihoods (≥3 sources). Surface common divergence-source patterns.
3. arviz r-hat / ESS / divergence reporting conventions; convention for posterior-predictive-check artifact placement.
4. PyMC `TruncatedPareto` availability — native distribution, custom logp, or numerical-truncation wrapper. (Forward-look from SIM-INFRA-0 Task 1.1 deferred this; resolve here.)

Output: ≤1500 words; per-question section; references with URLs/citekeys. Run conditionally — skip if foreground judges literature already settled by SIM-INFRA-0 §1.1 research deliverable.

- [ ] **Step 1** — Foreground decides: dispatch `gsd-phase-researcher` (background) OR mark "skipped — settled by SIM-INFRA-0 research" with rationale in `RESEARCH.md`.
- [ ] **Step 2** — Continue Task 1.2 in parallel; 1.3 blocks on 1.1 + 1.2.

### Task 1.2 — Cohort module-boundary review (Backend Architect, parallel)

**Files:** Create `scratch/2026-05-08-saas-cohort-1-research/MODULE_BOUNDARY_REVIEW.md`.

**Brief.** Review the proposed `simulations/saas_builder/` placement against:
- functional-python three-tier discipline (cohort code is mostly Callable-tier: model factory + diagnostics + emit are Callables; priors module is Value-tier).
- Spec §6 functional-form table — every row consumed by COHORT-1 must trace to an existing import from `simulations/{types,modules,utils}/`.
- Cross-cohort precedent: does the proposed structure generalize cleanly to future `simulations/pair_d/`, `simulations/dev_ai/` peer packages?
- Identify any infrastructure gap. If found, HALT — gap-fix is a SIM-INFRA-0 follow-up plan, NOT a COHORT-1 task.

- [ ] **Step 1** — Foreground dispatches `Backend Architect` in background.
- [ ] **Step 2** — 1.3 blocks on this + 1.1.

### Task 1.3 — Plan reconciliation memo (foreground)

**Files:** Create `scratch/2026-05-08-saas-cohort-1-research/PLAN_RECONCILIATION.md`.

- [ ] **Step 1** — Foreground reads 1.1 + 1.2 outputs.
- [ ] **Step 2** — Reconcile any disagreement; per-disagreement adjudication entry.
- [ ] **Step 3** — If 1.2 surfaced an infrastructure gap: HALT, raise SIM-INFRA-0 follow-up plan, do NOT proceed.
- [ ] **Step 4** — Commit research artifacts.

```bash
git add scratch/2026-05-08-saas-cohort-1-research/
git commit -m "research(saas-cohort-1): prior-elicitation + module-boundary review + reconciliation"
```

---

## Phase 2 — Implementation

> **Sub-task split.** Phase 2 is split into four scoped `AI Engineer` dispatches (priors → model → diagnostics → emission). Implementing agent decides .py decomposition within each surface. Each task commits separately.

### Task 2.1 — Implement `simulations/saas_builder/priors.py`

**Files:** Create `simulations/saas_builder/__init__.py`, `simulations/saas_builder/README.md`, `simulations/saas_builder/priors.py`.

**Agent.** `AI Engineer`.

**Inputs (passed in dispatch brief):**
- Phase 2 prelude (M1 floor, M3 blended-price pin, M4 schema, tier-prior pin).
- Spec v1.1.1 §5.1 (T1 row) + §5.2 (tier prior $\alpha_0$ + pricing table).
- Existing Value types: `simulations.types.distributions.{TruncParetoParams, NegBinParams}`, `simulations.types.tier.TierMix`, `simulations.types.posterior.CohortPrior`.
- functional-python skill (re-read in 0.1).

**Behavior contract:**
- `priors.py` is Value-tier: frozen-dataclass containers wrapping the prior hyperparameters (NegBin $(\mu, \varphi)$ priors per the NegBin parameterization pin above — MQ-B2; TruncPareto $\alpha, x_m$ priors; tier Dirichlet $\alpha_0$).
- `__post_init__` enforces M1 floor at the prior level: any prior on $\alpha$ MUST be representable as a lower-bounded distribution with lower bound $\ge 1.5$. A field carrying the lower bound (`alpha_lower: Final = 1.5`) is constructed-checked. The plan recommends — and FLAG-A pins as preferred — `pm.TruncatedNormal(mu=2.0, sigma=0.25, lower=1.5, upper=2.5)` (i.e., a TruncatedNormal explicitly bounded to spec §5.2's $\alpha \in [1.5, 2.5]$ bracket) over a `1.5 + Gamma(·)` shift; the two have very different tail behavior near the floor and the bracketed truncation matches spec §5.2 exactly. Pre-mortem (Task 3.5) explicitly tests divergence-cluster-near-1.5 (MQ-FLAG-A fold-in).
- The Dirichlet $\alpha_0$ is exactly the literal vector `[2.0, 5.0, 3.0]` (= $10 \cdot [0.20, 0.50, 0.30]$, sum 10); `__post_init__` asserts elementwise via `math.isclose(rel_tol=1e-12)` (MQ-FLAG-B fix; floating-point literal vs. computed-product tolerance).
- The NegBin prior pin targets $\mu \approx 80$ (turns/active-day median; spec §5.2 line 318) and calibrates $\varphi$ (PyMC `alpha=`) so that $\sigma/\mu = \sqrt{1/\mu + 1/\varphi}$ delivers the spec §5.2 over-dispersion ratio p90/mean ≈ 2.3× (calibration computed at prior-elicitation time and pinned in priors.py module docstring with a verbatim citation of spec §5.2 line 318). Reparameterization $r = \varphi$, $p = \varphi/(\varphi + \mu)$ is documented inline if `NegBinParams(r, p)` instances are constructed for downstream Callable consumers.
- No imports from `simulations/modules/` or `simulations/utils/`.
- No PyMC import in this file (priors.py is pure Value tier; PyMC distributions instantiated in `model.py`).

- [ ] **Step 1** — Foreground dispatches `AI Engineer` with full brief.
- [ ] **Step 2** — On agent completion: `pytest simulations/saas_builder/ -v` (initial sanity) + `ty check simulations/saas_builder/priors.py`. Both clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(saas-cohort-1/priors): T1 prior pins per spec §5.1 + §5.2"
```

### Task 2.2 — Implement `simulations/saas_builder/model.py`

**Files:** Create `simulations/saas_builder/model.py`.

**Agent.** `AI Engineer`.

**Inputs (passed in dispatch brief):**
- Phase 2 prelude (M1 enforced upstream by `simulations.modules.samplers.TruncParetoSampler`; M3 blended price obtained by *calling* a `BlendedPriceFn` instance from `simulations.modules.pricing` — see Pin M3 verbatim).
- Task 2.1 output (priors.py), including the NegBin (μ, φ) parameterization pin and the M1-bracketed TruncatedNormal recommendation.
- Spec §5.1 (T1) verbatim doubly-stochastic compound sum $\tau_t = \sum_{j=1}^{D_t}\sum_{i=1}^{N_j} \tau_{j,i}$ with $D_t \approx 22$, per-active-day $N_j \sim \mathrm{NegBin}(\mu, \varphi)$, per-turn $\tau_{j,i} \sim \mathrm{TruncPareto}(\alpha, x_m, \kappa)$. Tier-Categorical mixture over $\pi$. **NO Compound-Poisson at the primary level (MQ-B3).**
- Existing Callable: `simulations.modules.samplers.TruncParetoSampler` (refuses $\alpha < 1.5$ at construction with typed `ValueError`).
- Existing Callable: `simulations.modules.pricing.BlendedPriceFn` (frozen-dc; field `params: BlendedPriceParams`; `__call__() -> float` returns USD/MTok). Symbol verified at pricing.py:23-55; `__all__ = ["BlendedPriceFn"]` at pricing.py:58-60. **The symbol `BlendedPriceCalc` does NOT exist; do not import it (RC-B1 fix).**
- Existing Value: `simulations.types.fx.BlendedPriceParams` (carries `p_in, p_out, w_in, w_out, h_cache`); `simulations.types.fx.CACHED_INPUT_DISCOUNT` (Final 0.10).
- functional-python skill.

**Behavior contract:**
- `model.py` exposes a Callable-tier model factory: `@dataclass(frozen=True)` + `__call__(observed)` returns a `pymc.Model` context.
- Tier latent: `pm.Categorical(p=π)` with $\pi \sim \mathrm{Dir}(a=[2.0, 5.0, 3.0])$.
- Per-tier sub-likelihoods: per-active-day NegBin turn count via `pm.NegativeBinomial(mu=μ, alpha=φ)` (mean–dispersion form per MQ-B2), iid TruncPareto tokens-per-turn (`α, x_m, κ` per spec §5.1 (T1)), aggregated across $D_t \approx 22$ days × $N_j$ turns into the deterministic `τ_t = pm.Deterministic("tau_t", τ_t_expr)`. NO Compound-Poisson cluster process at the primary level (that's spec §5.1 sensitivity arm (c), out of scope). α prior is the lower-bounded TruncatedNormal from Task 2.1 (M1 enforced at prior level; sampler refusal is dual defense per FLAG-A).
- Cost-per-turn deterministic uses the shipped API:
  - Construct `params = BlendedPriceParams(p_in=3.0, p_out=15.0, w_in=0.539, w_out=0.461, h_cache=0.95)` (Sonnet defaults from spec §5.4 footnote / pricing.py docstring).
  - Construct `price_fn = BlendedPriceFn(params=params)`.
  - Obtain blended scalar: `price_per_mtok = price_fn()` (CALL the instance — there is no `.price_per_mtok` attribute and no `tier=` keyword; RC-B2 fix).
  - Likelihood deterministic: `cost_usd = tokens * price_per_mtok / 1e6`.
- The Sonnet asserted-equality check ($7.1495 \pm 0.01$ — tolerance widened from $\pm 0.0005$ to match spec §5.1's "≈ 7.15" precision per RC-FLAG-1) lives at the model-factory `__call__` site (NOT in `__post_init__`, which validates the params struct, not a tier-conditioned numeric output — RC-B2 fix). Implementation: assert `math.isclose(price_per_mtok, 7.1495, abs_tol=0.01)` immediately after constructing the price_fn at call time.
- Posterior-predictive surface: `tau_t`, `q_t_usd`, `q_t_cop` are declared as `pm.Deterministic` nodes inside the model context so they are emitted as posterior-predictive variables by `pm.sample_posterior_predictive` in Task 2.4 (MQ-B4 fix).
- No imports from `simulations/utils/`.
- May import PyMC (this is the layer where PyMC enters the codebase).

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Run `pytest simulations/saas_builder/ -v` + `ty check simulations/saas_builder/model.py`. Both clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(saas-cohort-1/model): T1 PyMC compound model + tier mixture per spec §5.1"
```

### Task 2.3 — Implement `simulations/saas_builder/diagnostics.py`

**Files:** Create `simulations/saas_builder/diagnostics.py`.

**Agent.** `AI Engineer`.

**Inputs (passed in dispatch brief):**
- Phase 2 prelude diagnostics pin (post-MQ-B5 fix): $\hat R \le 1.01$ on every monitored parameter; **`ESS_bulk ≥ 400` AND `ESS_tail ≥ 400`** on every monitored parameter (TWO thresholds per spec §8(8)); divergences $\le 0.5\%$ of post-warmup draws; sim-count floor $\ge 4000$ post-warmup draws × $\ge 4$ chains per spec §8(8); posterior 95% CI width $\le 2 \times$ prior 95% CI width per spec §8(7) (HALT-gate, NOT advisory).
- Spec §8 anti-fishing invariants. NOTE: $N_{\min}=75$, $\mathrm{POWER}_{\min}=0.80$, $\mathrm{MDES}_{\mathrm{SD}}=0.40$ bind STAGE-3 cohort-survey design per spec §8 declaration line 432-439, NOT this Stage-2 synthetic-Bayesian calibration. The Stage-2 sim-count floor is `≥4000 draws × ≥4 chains` per §8(8) (MQ-FLAG-D fix).
- functional-python skill.

**Behavior contract:**
- `diagnostics.py` exposes a Callable-tier diagnostic: `@dataclass(frozen=True)` + `__call__(idata: arviz.InferenceData, prior_idata: arviz.InferenceData | None = None) -> DiagnosticVerdict`. The optional `prior_idata` carries prior draws for the §8(7) CI-width comparison; if `None`, the verdict requires the caller to supply prior CI widths via a separate parameter (CI-width gate cannot silently skip).
- `DiagnosticVerdict` is a frozen-dc Value type (defined inline or in priors.py) with fields:
  - `rhat_max: float` (max over monitored params)
  - `ess_bulk_min: float` (min over monitored params; spec §8(8) two-threshold split)
  - `ess_tail_min: float` (min over monitored params; spec §8(8) two-threshold split)
  - `divergence_frac: float`
  - `sim_count_floor_violated: bool` (renamed from v0.1 `n_min_violated` per MQ-FLAG-D; pinned to spec §8(8) `≥4000 × ≥4`, NOT CLAUDE.md `N_MIN=75`)
  - `ci_width_ratio_max: float` (max over monitored params of posterior_95_CI_width / prior_95_CI_width; HALT-gate at 2.0 per spec §8(7) — MQ-B5 fix restoring this from advisory to gate)
  - `passed: bool`
- The diagnostic refuses to mark `passed=True` if ANY of: `rhat_max > 1.01`, `ess_bulk_min < 400`, `ess_tail_min < 400`, `divergence_frac > 0.005`, `sim_count_floor_violated`, or `ci_width_ratio_max > 2.0`. Consumer (Task 2.4) HALTs on `passed=False` per `feedback_pathological_halt_anti_fishing_checkpoint`.
- The `n_min_violated` field from v0.1 is REMOVED; `N_MIN=75` is a Stage-3 cohort-survey invariant and was conceptually misapplied as a Stage-2 thinning guard (MQ-FLAG-D fix).
- No PyMC import (arviz only).

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Run `pytest simulations/saas_builder/ -v` + `ty check simulations/saas_builder/diagnostics.py`. Both clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(saas-cohort-1/diagnostics): r-hat + ESS + divergence + N_min gate"
```

### Task 2.4 — Implement `simulations/saas_builder/emit.py`

**Files:** Create `simulations/saas_builder/emit.py`; add `simulations/saas_builder/data/` to `.gitignore`.

**Agent.** `AI Engineer`.

**Inputs (passed in dispatch brief):**
- Phase 2 prelude M4 (parquet column schema verbatim; Hive partition layout).
- Tasks 2.1, 2.2, 2.3 outputs.
- Existing IO writers in `simulations.utils.parquet_io` (Final dtype maps for `synthetic_tau_t.parquet` and `cohort_prior.parquet`).
- Existing Value types: `simulations.types.posterior.{PosteriorDraws, CohortPrior, MonthlyCDF}`.
- functional-python skill.

**Behavior contract:**
- `emit.py` is Callable-tier: orchestrator that takes (model, priors, diagnostics-verdict, idata, posterior_predictive_idata) and emits both parquet artifacts.
- **Posterior-predictive emission (MQ-B4 fix; spec §7 line 415).** Before any emission, `emit.py` MUST call `pm.sample_posterior_predictive(idata, var_names=["tau_t", "q_t_usd", "q_t_cop"])` (or accept its `idata.posterior_predictive` group as input) to obtain new draws of $\tau_t$, $q_t^{\mathrm{USD}}$, $q_t^{\mathrm{COP}}$. The `synthetic_tau_t.parquet` columns `tau_t`, `q_t_usd`, `q_t_cop` are populated from the `posterior_predictive` group, NOT from `posterior` parameter draws. The columns `r`, `p`, `alpha`, `x_m` are populated from the `posterior` group (parameter draws), with the (μ, φ) → (r, p) reparameterization applied at emission time per the NegBin parameterization pin. Stationary bootstrap is structurally absent (spec §7 strip per v1.0→v1.1).
- HALTs (raises typed `DiagnosticGateError`, defined in `simulations.utils.errors`) on `passed=False` from diagnostics. NO partial emission.
- Posterior-draw emission writes through `simulations.utils.parquet_io` only (`SyntheticTauWriter`, `CohortPriorWriter`); no direct pandas/pyarrow calls. Hive partition layout `tier_id=*/month=*/` is enforced by the writer per `SYNTHETIC_TAU_PARTITION_COLS`.
- Every row written through the writer MUST include the `schema_version` field, supplied via the convenience factories `synthetic_tau_row(...)` / `cohort_prior_row(...)` (parquet_io.py:406-453) which default to `simulations.types.posterior.DEFAULT_SCHEMA_VERSION`. Direct dict construction without `schema_version` will raise `SchemaMismatchError` from `_check_columns` (parquet_io.py:127-147).
- `cohort_prior.parquet` emission writes percentile rows (5/25/50/75/95) for each prior parameter, with `source = "spec-v1.1.1-§5.1-§5.2"`, `fetched_at_utc = datetime.now(UTC).isoformat()`, and `schema_version = DEFAULT_SCHEMA_VERSION`.
- Idempotent: re-running over the same `(tier_id, month)` partition overwrites cleanly. Audit-block sha (from `simulations.utils.audit_block`) is recorded for every emission and written into a sidecar `_AUDIT.json`.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Run `pytest simulations/saas_builder/ -v` + `ty check simulations/saas_builder/emit.py`. Both clean. Smoke-emit a 100-draw test fixture under a `tmp_path` fixture and read it back; column set matches M4 exactly.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(saas-cohort-1/emit): posterior + prior parquet emission per spec §10"
```

---

## Phase 3 — Audit-pass chain (Honnibal sequence)

> Six sequential skill invocations, mirroring SIM-INFRA-0 Phase 3 order: tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing. Pre-mortem identifies fragilities first; mutation-testing then verifies tests cover them.

### Task 3.1 — `tighten-types`
**Skill scope:** `simulations/saas_builder/`. Apply recommendations; re-test + re-typecheck; commit.
- [ ] **Step 1–4** — invoke / apply / verify / `git commit -am "audit(saas-cohort-1): tighten-types pass"`.

### Task 3.2 — `contract-docstrings`
**Skill scope:** `simulations/saas_builder/`. Every public function gets a docstring with args / returns / raises / spec-anchor. The Sonnet $7.1495 pin and the M1 $\alpha \ge 1.5$ pin must be referenced in the model factory docstring.
- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-1): contract-docstrings pass"`.

### Task 3.3 — `hypothesis-tests`
**Skill scope:** `simulations/saas_builder/` + `simulations/tests/`.

**Required properties (this cohort):**
1. Tier-prior simplex: any draw from `Dir(a=[2.0, 5.0, 3.0])` lies on the 3-simplex (sum to 1, all ≥ 0).
2. M1 enforcement: any prior-α-draw fed into a downstream `TruncParetoSampler` succeeds (does NOT raise) — the prior's lower-bound construction (TruncatedNormal lower=1.5) is consistent with the sampler's α-floor; α-draws strictly below 1.5 must NOT occur (probability mass = 0 below the floor; resolves FLAG-A).
3. M3 invariance (RC-B1/B2 fix): for any fixed `BlendedPriceParams` instance, `BlendedPriceFn(params=p)()` returns the same float across repeated construction + call cycles in the same process. For the spec §5.4 Sonnet defaults `(p_in=3.0, p_out=15.0, w_in=0.539, w_out=0.461, h_cache=0.95)`, the call-time output equals 7.1495 ± 0.01 (RC-FLAG-1 tolerance widening). The property is verified by *calling* the instance, not by reading a non-existent `.price_per_mtok` attribute.
4. Schema round-trip: any `SyntheticTauRow` (TypedDict from `simulations.utils.parquet_io`) including `schema_version` written via `SyntheticTauWriter` and re-read via `SyntheticTauReader` produces an equal row (column set matches `SYNTHETIC_TAU_COLUMNS` exactly — 11 columns including `schema_version`; dtypes match `SYNTHETIC_TAU_DTYPES`; partition keys reconstructed). Likewise for `CohortPriorRow` / `COHORT_PRIOR_COLUMNS`.
5. Diagnostic monotonicity: synthetically degraded $\hat R$ (above 1.01) MUST yield `passed=False`; synthetically degraded `ESS_bulk` OR `ESS_tail` (below 400) MUST yield `passed=False` (TWO independent properties per MQ-B5); synthetically degraded divergence-rate (above 0.005) MUST yield `passed=False`; synthetically inflated posterior CI width (ratio > 2.0 vs prior) MUST yield `passed=False` per spec §8(7).
6. Posterior-predictive within-row variance (MQ-B4 fix): at fixed parameter draws `(r, p, α, x_m)`, the posterior-predictive `tau_t` realizations across distinct `simulation_id`s have within-group variance > 0 — i.e., the τ_t column is populated from `pm.sample_posterior_predictive` (new τ_{j,i} draws), not from a deterministic function of parameters alone. A property test that finds zero within-group variance is a BLOCK.

- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-1): hypothesis-tests pass — 5 properties"`.

### Task 3.4 — `try-except`
**Skill scope:** `simulations/saas_builder/`. Tier reminder: only `emit.py` (orchestrator touching IO via utils/) should have non-trivial `try/except`; `model.py`, `priors.py`, `diagnostics.py` should let typed exceptions propagate.
- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-1): try-except pass"`.

### Task 3.5 — `pre-mortem`

**Skill scope:** `simulations/saas_builder/{model.py, emit.py}`.

For each surfaced fragility: (a) regression test, (b) refactor, or (c) document in cohort README. Particular focus areas:
- Divergence cluster on the TruncPareto $\alpha$ near the 1.5 boundary (re-parameterize via $\log(\alpha - 1.5)$ if surfaced).
- Tier-Categorical label-switching (resolve via ordering constraint on $\pi$ if surfaced).
- Parquet partition collision under concurrent emission (rare; document if not regression-tested).

- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-1): pre-mortem pass — model + emit"`.

### Task 3.6 — `mutation-testing`

**Skill scope:** `simulations/saas_builder/`.

**Kill-rate threshold: ≥ 80%.** Industry-standard benchmark (Coles 2016; Petrović & Ivanković 2018), NOT spec §8(7) analog (mechanically distinct).

**Equivalent-mutant exemption cap: ≤ 5%** of total mutants. Each exemption requires a one-line justification. If >5% are claimed equivalent, `Code Reviewer` audits the exemption list before the audit pass closes.

- [ ] **Step 1** — Invoke skill.
- [ ] **Step 2** — Iterate adding tests until kill rate ≥ 80% AND ≤5% exemption-claimed.
- [ ] **Step 3** — Re-test; commit.

```bash
git commit -am "audit(saas-cohort-1): mutation-testing pass — kill rate $METRIC% (≥80%; equiv-exempt ≤5%)"
```

---

## Phase 4 — Verification gate (2-wave)

### Task 4.1 — Wave 1: Reality Checker compliance audit

**Files:** Create `scratch/2026-05-08-saas-cohort-1-audit/reality_checker_compliance.md`.

**Agent.** `Reality Checker`.

**Brief.** Audit `simulations/saas_builder/` against:
1. functional-python three-tier discipline (every `.py` is exactly one tier; tier-import discipline preserved).
2. Math pins enforced by direct test execution: M1 prior lower-bound (TruncatedNormal[lower=1.5, upper=2.5]) + sampler refusal at $\alpha < 1.5$; M3 Sonnet `BlendedPriceFn(params=BlendedPriceParams(...))()` call-site assertion fires at 7.1495 ± 0.01; M4 schema round-trip exact column set including `schema_version`.
3. Diagnostic gate (r-hat ≤ 1.01 / **ESS_bulk ≥ 400 AND ESS_tail ≥ 400** / divergence ≤ 0.5% / sim-count ≥ 4000×4 / **CI-width ratio ≤ 2.0 per spec §8(7)**) executes on every emission path; no bypass. `N_MIN=75` is OUT OF SCOPE for Stage-2 (Stage-3 cohort-survey invariant).
4. Anti-fishing: no threshold tuning between spec v1.1.1 and code; if any threshold appears different from spec, that's a BLOCK.
5. Audit artifacts (3.1–3.6) all present.

Default to REJECT. Each finding: file:line evidence. ≤1500 words.

**HALT trigger:** On REJECT verdict, foreground executes `feedback_pathological_halt_anti_fishing_checkpoint`: (a) HALT, (b) disposition memo with ≥3 pivot options, (c) user adjudication, (d) CORRECTIONS-block in v0.2 of this plan, (e) post-hoc reverify. Do not silently fix and continue.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Verdict ACCEPT or ACCEPT_WITH_FLAGS → advance to 4.2. REJECT → HALT.
- [ ] **Step 3** — Commit verdict.

### Task 4.2 — Wave 2: Model QA Specialist statistical-correctness audit

**Files:** Create `scratch/2026-05-08-saas-cohort-1-audit/model_qa_report.md`.

**Agent.** `Model QA Specialist`.

**Brief.** Audit:
1. Posterior diagnostics: r-hat, ESS_bulk, ESS_tail, divergences across all monitored parameters per spec §8(8) (TWO ESS thresholds per MQ-B5); surface any that drift toward the gate boundary even when passing.
2. Prior-vs-posterior CI-width invariant per spec §8(7): posterior 95% CI for each parameter ≤ 2× prior 95% CI; **if exceeded, BLOCK** (HALT-gate per MQ-B5; v0.1 demoted this to advisory shrinkage, v0.2 restores it).
3. Tier label-switching: posterior π's are well-separated; if any pair shows >5% label-switch frequency, BLOCK.
4. M1-floor probability mass: posterior $P(\alpha < 1.5) = 0$ exactly (lower-bound TruncatedNormal prior should make this structural).
5. Posterior-predictive check: confirm `pm.sample_posterior_predictive` was used to populate τ_t / q_t_usd / q_t_cop columns (MQ-B4); within-row variance across simulation_ids at fixed parameter draws must be > 0; cost-per-month posterior mean lies within order-of-magnitude bounds expected from spec §5.2 pricing table × NegBin($\mu \approx 80$, $\varphi$ calibrated to 2.3× over-disp).
6. NegBin parameterization reverify (MQ-B2): code uses `pm.NegativeBinomial(mu=μ, alpha=φ)` with `Var = μ + μ²/φ`; the (μ, φ) → (r, p) reparameterization at downstream emission preserves spec §5.2 anchors.
7. Likelihood structure reverify (MQ-B3): code implements $\tau_t = \sum_{j=1}^{D_t}\sum_{i=1}^{N_j} \tau_{j,i}$ with per-active-day NegBin; NO Compound-Poisson at primary likelihood level.
8. Anti-fishing reverify: confirm thresholds in code = spec v1.1.1 thresholds exactly.

Default to REJECT. ≤1500 words.

**HALT trigger:** same protocol as 4.1.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Verdict ACCEPT / ACCEPT_WITH_FLAGS → advance. REJECT → HALT.
- [ ] **Step 3** — Commit verdict.

### Task 4.3 — Static analysis sweep

**HALT trigger:** any failure → `feedback_pathological_halt_anti_fishing_checkpoint`.

- [ ] **Step 1** — `ruff check simulations/saas_builder/`. Zero warnings.
- [ ] **Step 2** — `ty check simulations/saas_builder/`. Zero errors.
- [ ] **Step 3** — `pytest simulations/ -v --cov=simulations/saas_builder`. All pass; coverage ≥ 90% on the cohort package.
- [ ] **Step 4** — On any failure: HALT.

> **Note on plan-document verify.** Per `feedback_two_wave_doc_verification` (NON-NEGOTIABLE), this plan MUST be 2-wave verified (Reality Checker + Model QA Specialist) by foreground orchestration **before commit**, separate from the in-plan Phase-4 implementation gates. Verdicts at `scratch/2026-05-08-saas-cohort-1-plan-review/`. Plan executors do not re-run that pre-commit verify.

---

## Phase 5 — Code review and PR-readiness

### Task 5.1 — Code Reviewer audit
**Files:** Create `scratch/2026-05-08-saas-cohort-1-audit/code_reviewer_report.md`.
**Agent.** `Code Reviewer`.
**Brief.** Independent code review: correctness, maintainability, performance (NUTS sample-time scaling, parquet emission speed). NOT functional-python compliance (covered by 4.1) or statistical correctness (covered by 4.2).
- [ ] **Step 1–3** — dispatch / fix / `git commit -am "review(saas-cohort-1): Code Reviewer pass"`.

### Task 5.2 — CLAUDE.md + memory update
**Files:** Modify `CLAUDE.md` repo-structure section to include `simulations/saas_builder/`. Create `memory/project_saas_cohort_1_complete.md` with verdict, posterior-summary headline, and downstream unblock notice.
- [ ] **Step 1** — Update CLAUDE.md tree.
- [ ] **Step 2** — Add memory file.
- [ ] **Step 3** — `git commit -am "docs(saas-cohort-1): CLAUDE.md + memory updated"`.

### Task 5.3 — PR refresh

- [ ] **Step 1** — `git push origin iter/saas-builder-stage-2`.
- [ ] **Step 2** — Resolve PR number dynamically:
  ```bash
  PR_NUM=$(gh pr list --repo wvs-finance/abrigo-analytics --search "head:iter/saas-builder-stage-2" --json number -q '.[0].number')
  ```
  Then `gh pr edit "$PR_NUM" --repo wvs-finance/abrigo-analytics --body "$(cat <<'EOF' ... EOF)"` with updated body covering SAAS-COHORT-1 completion + COHORT-2 / COHORT-3 unblock status.
- [ ] **Step 3** — Confirm PR shows new commits.

---

## Verification matrix (cross-reference)

| Spec anchor | Cohort artifact | Math pin | Consumed by |
|---|---|---|---|
| §5.1 T1 doubly-stochastic compound sum $\tau_t = \sum_j^{D_t} \sum_i^{N_j} \tau_{j,i}$ (per-active-day NegBin × iid TruncPareto; NO Compound-Poisson) | `model.py` | M1 | COHORT-2 |
| §5.2 tier prior $\pi \sim \mathrm{Dir}(a=[2.0, 5.0, 3.0])$ | `priors.py` | — | COHORT-2, COHORT-4 |
| §5.2 NegBin (μ, φ) parameterization; PyMC `pm.NegativeBinomial(mu=μ, alpha=φ)` | `model.py` + `priors.py` | — | COHORT-2 |
| §5.2 pricing (Sonnet $3/$15) | `model.py` (via `BlendedPriceFn(params=BlendedPriceParams(...))()`) | M3 | COHORT-3, COHORT-4 |
| §7 `pm.sample_posterior_predictive` for τ_t / q_t_usd / q_t_cop | `emit.py` | — | COHORT-2, COHORT-3, COHORT-4 |
| §8(7) posterior CI-width ≤ 2× prior CI-width (HALT-gate) | `diagnostics.py` | — | gate for emission |
| §8(8) ESS_bulk ≥ 400 ∧ ESS_tail ≥ 400 (two thresholds) | `diagnostics.py` | — | gate for emission |
| §8(6) α-floor 1.5 | `priors.py` lower-bound + upstream sampler | M1 | COHORT-2 |
| §10 `synthetic_tau_t.parquet` schema | `emit.py` (via `parquet_io`) | M4 | COHORT-2, COHORT-3, COHORT-4 |
| §10 `cohort_prior.parquet` schema | `emit.py` (via `parquet_io`) | M4 | COHORT-2 |
| §8 diagnostics + $N_{\min}$ | `diagnostics.py` | — | gate for emission |

---

## Self-review checklist

- [x] Spec coverage complete (§5.1 T1, §5.2, §6, §8(6), §10 mapped to tasks).
- [x] No code blocks (only bash + invocation commands).
- [x] Every task names agent / skill.
- [x] Every audit pass commits separately.
- [x] Phase 0 includes functional-python skill re-read + SIM-INFRA-0 PASS-state confirmation.
- [x] HALT triggers reference `feedback_pathological_halt_anti_fishing_checkpoint`.
- [x] Out-of-scope enumerated (T2, Υ_t, Z-cap, infra extensions, deployment, spec edits).
- [x] Math pins M1, M3, M4 + tier-prior + diagnostics in Phase 2 prelude.
- [x] Audit-pass order matches SIM-INFRA-0 (pre-mortem before mutation-testing).
- [x] Mutation 80% threshold disambiguated from spec §8(7).
- [x] Equivalent-mutant cap pinned at ≤5%.
- [x] PR number resolved dynamically.
- [x] Plan does NOT cover COHORT-2/3/4 work.
- [x] Anti-fishing thresholds inherited from spec verbatim (no relaxation).
- [x] Diagnostics gate ($\hat R \le 1.01$, ESS $\ge 400$, div $\le 0.5\%$, $N_{\min}=75$) explicit and enforceable.

---

## Notes for plan-doc reverifiers

- Predecessor SIM-INFRA-0 v1.1.1 REVERIFY-PASSED is the gate; Phase 0.2 enforces. If SIM-INFRA-0 regresses, COHORT-1 cannot proceed.
- All PyMC code lives in this cohort package; SIM-INFRA-0 is intentionally PyMC-free.
- The Sonnet-default M3 source-of-truth: call `BlendedPriceFn(params=BlendedPriceParams(p_in=3.0, p_out=15.0, w_in=0.539, w_out=0.461, h_cache=0.95))()` returns ≈ 7.1495 (asserted at the model-factory call site within ±0.01 to match spec §5.1's "≈ 7.15" precision). The shipped symbol is `BlendedPriceFn` (frozen-dc, callable via `__call__()`); there is no `BlendedPriceCalc`, no `tier=` keyword, and no `.price_per_mtok` attribute. Cohort code asserts but does not redefine the formula (RC-B1/B2 fix).
- The TruncPareto α-floor is dual-enforced: priors.py TruncatedNormal lower=1.5 (Bayesian level) AND samplers.py construction-time check (Callable level). Both must hold; either alone is insufficient defense-in-depth.
- The NegBin layer uses PyMC's (μ, α) mean-dispersion form (`pm.NegativeBinomial(mu=μ, alpha=φ)`) per spec §5.2 over-dispersion anchor (μ ≈ 80, p90/mean ≈ 2.3×); the Value-tier `NegBinParams(r, p)` is reparameterized at the boundary with $r = \varphi$, $p = \varphi/(\varphi+\mu)$ (MQ-B2 fix).
- τ_t / q_t_usd / q_t_cop emission columns are populated by `pm.sample_posterior_predictive`, NOT by `idata.posterior` parameter slicing (spec §7; MQ-B4 fix).
- This plan v0.2 is the CORRECTIONS-α revision of v0.1; see §"CORRECTIONS-α v0.1 → v0.2" at end of plan for the verbatim BLOCK/FLAG resolution table. Wave-2 reverify queued on v0.2.

---

## CORRECTIONS-α v0.1 → v0.2

> Format precedent: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` §15 (the spec's own v1.0 → v1.1 CORRECTIONS-α block).
>
> Source verdicts:
> - Wave-1 RC: `scratch/2026-05-08-cohort-plans-review/cohort-1-rc-verdict.md` (verdict REJECT; 2 BLOCKs + 3 FLAGs).
> - Wave-2 MQ: `scratch/2026-05-08-cohort-plans-review/cohort-1-mq-verdict.md` (verdict REJECT; 5 BLOCKs + 4 FLAGs).
>
> All seven BLOCKs and all seven FLAGs are addressed in-line throughout the plan body (architecture summary, math pins, Phase-2 task contracts, Phase-3 hypothesis properties, Phase-4 verifier briefs, Verification matrix, Notes for plan-doc reverifiers). This block records the verdict-line → fix-location cross-reference per the §15 precedent.

### BLOCK resolution table

| ID | Verdict line / quote | Fix location in v0.2 | Resolution summary |
|---|---|---|---|
| RC-B1 | RC line 14-19: "Misnamed shipped contract: `BlendedPriceCalc` does not exist" | Architecture summary (line 15); Pin M3; Task 2.2 inputs + behavior contract; Notes for plan-doc reverifiers; Verification matrix | Renamed all references to `BlendedPriceFn` (verified at pricing.py:23-60; `__all__ = ["BlendedPriceFn"]`). The `BlendedPriceCalc` symbol does not exist. |
| RC-B2 | RC line 21-26: "Wrong API surface — no `tier=` keyword, no `.price_per_mtok` attribute. The blended price is obtained by *calling* the instance" | Pin M3; Task 2.2 behavior contract; Task 3.3 property #3; Notes | Rewrote to `BlendedPriceFn(params=BlendedPriceParams(p_in=3.0, p_out=15.0, w_in=0.539, w_out=0.461, h_cache=0.95))()` returning the float price. Asserted-equality check moved from `__post_init__` (structurally impossible) to model-factory `__call__` site. |
| MQ-B1 | MQ line 16-20: "`schema_version` column missing from M4 lists; writer's `_check_columns` will raise on emission" | Pin M4 (rewritten with verbatim citations of `SYNTHETIC_TAU_COLUMNS` parquet_io.py:44-56 and `COHORT_PRIOR_COLUMNS` parquet_io.py:34-41; both Final tuples include `schema_version`); Task 2.4 behavior contract (uses `synthetic_tau_row` / `cohort_prior_row` factories with `DEFAULT_SCHEMA_VERSION`); Task 3.3 property #4 (round-trip with `schema_version`) | Added `schema_version` to both column lists verbatim; cited shipped `Final[Mapping[str, str]]` dtype maps `SYNTHETIC_TAU_DTYPES` and `COHORT_PRIOR_DTYPES`. |
| MQ-B2 | MQ line 22-24: "NegBin parameterization unspecified; `pm.NegativeBinomial` accepts both `(α, μ)` and `(n, p)`; spec §5.2 anchors mean/dispersion" | NEW "NegBin parameterization pin" in Phase-2 prelude; Task 2.1 behavior contract; Task 2.2 inputs + behavior contract; Verification matrix; Notes | Pinned `pm.NegativeBinomial(mu=μ, alpha=φ)` mean-dispersion form with `Var = μ + μ²/φ`, $\mu \approx 80$, $\varphi$ calibrated to spec §5.2 over-dispersion ratio 2.3×. Documented (μ, φ) → (r, p) reparameterization $r=\varphi$, $p = \varphi/(\varphi+\mu)$ for boundary with shipped Value-tier `NegBinParams(r, p)` (distributions.py:114-143). |
| MQ-B3 | MQ line 26-28: "spec §5.1 (T1) is doubly-stochastic compound sum over days × turns; plan collapses to monthly turn-count + Compound-Poisson cluster process — wrong" | Architecture summary (line 15) rewritten verbatim from spec §5.1 line 177; NEW "Likelihood structural pin" in Phase-2 prelude; Task 2.2 inputs + behavior contract; Verification matrix | Replaced "monthly turn-count" with "per-active-day"; replaced "Compound-Poisson × TruncPareto cluster process" with the spec verbatim $\tau_t = \sum_{j=1}^{D_t}\sum_{i=1}^{N_j}\tau_{j,i}$, $D_t \approx 22$, iid TruncPareto. Compound-Poisson is now correctly labeled spec §5.1 sensitivity arm (c) and OUT OF SCOPE for COHORT-1. |
| MQ-B4 | MQ line 30-32: "spec §7 replaces stationary bootstrap with `pm.sample_posterior_predictive`; plan does not mention `posterior_predictive` anywhere" | NEW "Posterior-predictive emission pin" in Phase-2 prelude; Task 2.2 (posterior-predictive surface declared as `pm.Deterministic` nodes); Task 2.4 behavior contract (calls `pm.sample_posterior_predictive` before emission); Task 3.3 NEW property #6 (within-row variance > 0); Phase-4 MQ brief #5; Verification matrix; Notes | Pinned `pm.sample_posterior_predictive(idata, var_names=["tau_t", "q_t_usd", "q_t_cop"])` for the τ_t / q_t_usd / q_t_cop emission columns. Stationary bootstrap structurally absent (spec §7 v1.0→v1.1 strip). |
| MQ-B5 | MQ line 34-36: "spec §8(8) requires ESS_bulk ≥ 400 AND ESS_tail ≥ 400 (TWO thresholds); §8(7) CI-width is NON-NEGOTIABLE invariant, not advisory" | Diagnostics pin rewritten in Phase-2 prelude; Task 2.3 behavior contract (`DiagnosticVerdict` fields split into `ess_bulk_min` + `ess_tail_min`; new `ci_width_ratio_max` HALT-gate field); Task 3.3 property #5 (degraded ESS_bulk OR ESS_tail OR CI-width all yield `passed=False`); Phase-4 MQ brief items 1-2 (CI-width restored from advisory shrinkage to BLOCK-on-failure); Verification matrix | Split single ESS threshold into ESS_bulk + ESS_tail per spec §8(8). Restored §8(7) posterior 95% CI ≤ 2× prior 95% CI as HALT-gate (was demoted to advisory in v0.1 line 376). |

### FLAG fold-in table

| ID | Verdict line / quote | Fix location in v0.2 | Resolution summary |
|---|---|---|---|
| RC-FLAG-1 | RC line 30-33: "$7.1495 verbatim from spec §5.1 overstates spec; spec says ≈ 7.15; tolerance 0.0005 too tight" | Pin M3; Task 2.2 behavior contract (assertion site); Task 3.3 property #3; Notes | Tolerance widened from ±0.0005 to ±0.01 to match spec §5.1's "≈ 7.15" precision; pin language clarified "closed-form recomputation evaluates to 7.1495". |
| RC-FLAG-2 | RC line 35-38: "M4 column list omits `schema_version`" | Pin M4; Task 2.4 behavior contract; Task 3.3 property #4 | Subsumed by MQ-B1; both M4 lists now include `schema_version` verbatim with citations of shipped Final tuples. |
| RC-FLAG-3 | RC line 40-43: "Phase 0.2 references `memory/project_sim_infra_0_complete.md` which may not exist; 'or equivalent' is escape-hatch" | Task 0.2 Step 1 | Replaced "or equivalent" with the active Stage-2 memory file referenced by recent commit `1a141fe`; on miss, HALT and surface to user (no silent skip). |
| MQ-FLAG-A | MQ line 42-44: "TruncPareto α-floor: prior form not pinned; recommend TruncatedNormal lower=1.5 upper=2.5" | Task 2.1 behavior contract; Task 3.3 property #2; Phase-4 RC + MQ briefs | Pinned `pm.TruncatedNormal(mu=2.0, sigma=0.25, lower=1.5, upper=2.5)` matching spec §5.2 bracket; Task 3.5 pre-mortem flagged for divergence-cluster-near-1.5. |
| MQ-FLAG-B | MQ line 46-48: "Dirichlet α₀=10·[0.20,0.50,0.30] elementwise assertion needs `math.isclose(rel_tol=1e-12)` for floating-point safety" | Tier prior pin (Phase-2 prelude); Task 2.1 behavior contract; Task 3.3 property #1 | Specified `math.isclose(rel_tol=1e-12)` with the literal numeric vector `[2.0, 5.0, 3.0]`. |
| MQ-FLAG-C | MQ line 50-52: "AICc correctly absent; PSIS-LOO `k̂` correctly out-of-scope (deferred to COHORT-3)" | Diagnostics pin (Phase-2 prelude) item 3 | Recorded as PASS; explicit note that PSIS-LOO `k̂ < 0.7` is OUT OF SCOPE for COHORT-1 (deferred to COHORT-3 model selection per spec §9). No code change required. |
| MQ-FLAG-D | MQ line 54-56: "`N_min=75` is Stage-3 cohort-survey invariant, not a Stage-2 thinning guard; rename `n_min_violated` to `sim_count_floor_violated` pinned to spec §8(8)" | Task 2.3 behavior contract; Diagnostics pin | Removed `n_min_violated` field; renamed to `sim_count_floor_violated: bool` pinned to spec §8(8) `≥ 4000 draws × ≥ 4 chains`. CLAUDE.md `N_MIN=75` stripped from Stage-2 diagnostic gate (now correctly Stage-3-only). |

### Net delta vs v0.1

- Plan version: v0.1 → v0.2.
- Two pins added in Phase-2 prelude: "NegBin parameterization pin" (MQ-B2), "Likelihood structural pin" (MQ-B3), "Posterior-predictive emission pin" (MQ-B4).
- Pin M3 rewritten end-to-end (RC-B1, RC-B2, RC-FLAG-1).
- Pin M4 rewritten with verbatim Final-tuple citations (MQ-B1, RC-FLAG-2).
- Diagnostics pin rewritten with §8(7) HALT-gate restoration and ESS_bulk/ESS_tail split (MQ-B5).
- Tier prior pin updated with `math.isclose(rel_tol=1e-12)` (MQ-FLAG-B).
- Task 2.1 / 2.2 / 2.3 / 2.4 behavior contracts rewritten to match shipped contracts and pinned parameterizations.
- Task 3.3 hypothesis properties expanded from 5 → 6 (added posterior-predictive within-row-variance property per MQ-B4); property #3 rewritten (M3); property #4 expanded to include `schema_version` (M4); property #5 split (ESS_bulk + ESS_tail + CI-width).
- Phase-4 MQ brief items 5-7 replaced with posterior-predictive check + NegBin parameterization reverify + likelihood-structure reverify.
- Verification matrix expanded from 7 rows to 9 rows (added §5.2 NegBin (μ, φ); §7 posterior-predictive; §8(7) CI-width gate; §8(8) ESS-split).
- Notes-for-reverifiers rewritten with shipped-API source-of-truth statements.

### Reverify exit criteria

v0.2 dispatches Wave-2 RC + MQ on this revision. ACCEPT requires:
1. All 7 BLOCK fixes above traceable to spec authority + shipped code.
2. All 7 FLAGs folded in (no orphan recommendations).
3. No new BLOCKs introduced by the rewrites.
4. Sub-task dispatch (Phase 2.1+) authorized only on a clean Wave-2 ACCEPT or ACCEPT_WITH_FLAGS verdict.

---

## CORRECTIONS-α v0.2 → v0.3

> Format precedent: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` §15 + the v0.1 → v0.2 block above.
>
> Source verdicts (3-way independent post-implementation audit on commit 438a01a):
> - Reality Checker: `scratch/2026-05-08-saas-cohort-1-independent-audit/rc-verdict.md` (verdict REJECT; 4 BLOCKs + 5 FLAGs).
> - Model QA Specialist: `scratch/2026-05-08-saas-cohort-1-independent-audit/mq-verdict.md` (verdict REJECT; 3 BLOCKs + 2 FLAGs).
> - Code Reviewer: `scratch/2026-05-08-saas-cohort-1-independent-audit/cr-verdict.md` (verdict REQUEST_CHANGES; 2 BLOCKING + 8 IMPORTANT).
>
> The 5 cross-auditor consensus BLOCKs are addressed in this revision. Forward-fix implementation in new commits on branch `iter/saas-builder-stage-2`; no history rewrite. v0.2 commit 438a01a remains pinned for traceability.

### Consensus BLOCK resolution table

| ID | Verdict-line citations | Fix location in v0.3 | Resolution summary |
|---|---|---|---|
| BLOCK-1 (compound-sum likelihood) | RC §BLOCK-1; MQ §BLOCK-MQ-1; CR §B1 | `simulations/saas_builder/emit.py` `run_posterior_predictive`; `simulations/saas_builder/model.py` docstring; this plan §"CORRECTIONS-α v0.2 → v0.3" | The spec §5.1 (T1) compound sum $\tau_t = \sum_{j=1}^{D_t}\sum_{i=1}^{N_j}\tau_{j,i}$ is realized by a hybrid PyMC + post-hoc numpy reduction: `pm.sample_posterior_predictive` populates `n_per_day`, `n_month`, `tier_idx`; for each posterior draw of $(\alpha, x_m, n_{\text{month}})$, the shipped `simulations.modules.samplers.TruncParetoSampler` draws $n_{\text{month}}$ iid TruncPareto variates and reduces to $\tau_t = \sum \tau_{j,i}$ outside the model graph. Within-row per-turn variance at fixed posterior parameters is now nonzero (BLOCK-3 verifies). The previous deterministic `tau_t = n_month × E[τ]` is retained ONLY as the μ of the Stage-2 synthetic-Bayesian Normal-kernel proxy on the *fit* arm, not as the emission. |
| BLOCK-2 (HalfNormal proxy malformed) | RC §BLOCK-4; MQ §FLAG-MQ-A; CR §I5 | `simulations/saas_builder/model.py` (constant `SIGMA_OBS_FIXED`; `pm.Normal("tau_t_observed", ..., sigma=SIGMA_OBS_FIXED)`) | Replaced `pm.HalfNormal("sigma_obs", sigma=tau_t * 0.2 + 1.0)` (which passed a stochastic Deterministic as a HalfNormal scale, producing a non-identifiable nested stochastic prior) with a fixed positive scalar `SIGMA_OBS_FIXED = 1.0`. Pre-registered as a static likelihood-proxy hyperparameter; the §8(7) CI-width gate is the discriminator on parameter shrinkage. |
| BLOCK-3 (Property #6 fabricated PP) | RC §BLOCK-3; MQ §BLOCK-MQ-1; CR §I6 | `simulations/tests/test_saas_builder.py::test_property_6_posterior_predictive_within_row_variance` | Rewrote to fit a small synthetic model end-to-end with `pm.sample(draws=100, chains=2)` then call `run_posterior_predictive`. Asserts `tau_pp.shape == (2, 100)`, `tau_pp.var() > 0` (within-row per-turn variance from real TruncPareto resampling), AND reproducibility under fixed `random_seed`. The hand-fabricated `rng.gamma` array path is removed. |
| BLOCK-4 (sim-count floor per-chain) | RC §BLOCK-2 | `simulations/saas_builder/diagnostics.py` (sim_count_floor_violated condition); new test `test_sim_count_floor_violated_per_chain_not_total` | Changed gate from `total_draws < SIM_COUNT_DRAW_FLOOR or n_chains < SIM_COUNT_CHAIN_FLOOR` to `n_draws_per_chain < SIM_COUNT_DRAW_FLOOR or n_chains < SIM_COUNT_CHAIN_FLOOR`. Spec §8(8) requires per-chain ≥ 4000 (= ≥ 16,000 total at 4 chains). v0.2 enforced total ≥ 4000 only; 4 chains × 1000 draws would have silently passed. New regression test pins the per-chain semantics at the v0.2-pass-but-v0.3-fail boundary. |
| BLOCK-5 (tier_idx semantics) | RC §FLAG-B; MQ §BLOCK-MQ-2(b); CR (implicit via I6) | `simulations/saas_builder/model.py` (`pm.Categorical("tier_idx", p=pi, shape=(self.n_builders,))`); `T1ModelFactory.n_builders: int = DEFAULT_N_BUILDERS = 1000`; `simulations/saas_builder/emit.py` `_build_synthetic_tau_rows` (handles 3-D tier_idx) | tier_idx is now vector-shaped over `n_builders` per spec §5.2 "Categorical latent per builder" — each builder carries one latent tier per the spec text. The `T1ModelFactory` exposes `n_builders` (default 1000); for tests, smaller cohorts can be passed (e.g. `n_builders=4`). Emission flattens (chain, draw) and selects builder slot 0 per row, which preserves the v0.2 row-count layout while honoring the spec semantic. |

### IMPORTANT (CR) and FLAG (RC, MQ) items deferred to v0.4

The following CR-IMPORTANT and RC/MQ-FLAG items are NOT addressed in v0.3 (the consensus BLOCK-fix scope); they are recorded here for the next revision:

- CR I1: `.values.ravel()` → `.stack(sample=("chain", "draw")).values` for arviz-version-stable ordering.
- CR I2: `[:n_rows]` truncation should `assert tau_arr.size == n_rows` first.
- CR I3: `base_dir` default is relative; should be absolute or required.
- CR I4: `compute_ci_width_ratio_max` short-circuits on first degenerate prior.
- CR I7: heavy reliance on synthetic `az.from_dict` idata; add `@pytest.mark.slow` real-sample integration test.
- CR I8: `_AUDIT.json` write is non-atomic.
- RC FLAG-A: `compute_ci_width_ratio_max` on `pi` (3-simplex Dirichlet) is per-component-aggregate, not per-component.
- RC FLAG-C, FLAG-D, FLAG-E: var_names omits n_per_day; prior pipeline never end-to-end tested; `__init__.py` is empty.
- MQ FLAG-MQ-B: Hypothesis property #2 does not test joint identifiability of `(α, x_m, κ)`.
- CR NITs N1-N7: rigid tuple arity, magic floors, percentile=50 sentinel mis-use, narrow exception scope.

These do NOT block v0.3 emission correctness on the cohort-mixture spec §5.1 / §5.2 surfaces; they are quality-of-implementation issues for a v0.4 follow-up.

### Net delta vs v0.2

- Plan version: v0.2 → v0.3.
- Two new module-level constants in `model.py`: `DEFAULT_N_BUILDERS = 1000`, `SIGMA_OBS_FIXED = 1.0`.
- `T1ModelFactory.n_builders: int` field added.
- `tier_idx` shape changed from scalar to `(n_builders,)`.
- `pm.HalfNormal("sigma_obs", sigma=tau_t*0.2+1.0)` removed; replaced with fixed `sigma=SIGMA_OBS_FIXED` on the `tau_t_observed` Normal.
- `simulations/saas_builder/emit.run_posterior_predictive` rewritten: post-hoc TruncPareto compound-sum reduction; signature gains `x_max_fixed`, `blended_price_per_mtok`, `fx_cop_per_usd` keyword-only args.
- `CohortEmitter.fx_cop_per_usd` field added (default 4000.0).
- `diagnostics.PosteriorDiagnostic.__call__` sim-count check changed from total to per-chain.
- New tests: `test_sim_count_floor_violated_per_chain_not_total`; `test_property_6_*` rewritten end-to-end.

### Reverify exit criteria (v0.3)

ACCEPT requires:
1. All 5 consensus BLOCKs above traceable to spec authority + shipped code.
2. Test suite passes (current: 57 tests passing) with ruff + ty clean.
3. Coverage ≥ 80% across saas_builder/* (current: 89%).
4. No new BLOCKs introduced by the rewrites.
5. Anti-fishing invariants honored: no spec-pin relaxation; no test-fixture widening; no verdict-threshold tuning.


## CORRECTIONS-α v0.3 → v0.4

> Format precedent: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` §15 + the v0.1 → v0.2 and v0.2 → v0.3 blocks above.
>
> **Trigger.** v0.3 emit run on commit ec26317 (driver: `scripts/run_cohort1_emit.py`; log: `/tmp/c1-emit-stdout.log`). PyMC sampling completed (607.4 s for 4 chains × 4000 draws + 1000 tune) under `CompoundStep(NUTS + Metropolis(n_per_day) + CategoricalGibbsMetropolis(tier_idx))`. Diagnostic verdict:
>
> | Metric | v0.3 emit value | §8(8) gate | Pass? |
> |---|---|---|---|
> | r̂_max | 1.115095 | ≤ 1.01 | FAIL |
> | ESS_bulk_min | 38.1 | ≥ 400 | FAIL |
> | ESS_tail_min | 58.7 | ≥ 400 | FAIL |
> | divergence_frac | 0.000000 | ≤ 0.005 | PASS |
> | sim-floor (per-chain ≥ 4000, n_chains ≥ 4) | 4 × 4000 | required | PASS |
> | ci_width_ratio_max | 1.041070 | ≤ 2.0 | PASS |
>
> Three of six axes failed simultaneously (r̂, ESS_bulk, ESS_tail) — this is a structural mixing failure, not finite-sample noise. Anti-fishing-replication: NO threshold relaxation; the methodology is what changes.
>
> **Diagnosis.** `pm.Categorical("tier_idx", p=pi, shape=(n_builders=1000,))` with the default `CompoundStep` selects `CategoricalGibbsMetropolis` on the 1000-dimensional discrete latent. Each NUTS step requires a Gibbs sweep over all 1000 latents (one per builder); for any reasonable runtime budget, the chains fail to mix in `pi` (and consequently in `mu`, `phi`, `alpha_pareto`, `x_m`, since the tier_idx posterior carries no information about them but the sampler still wastes proposals). r̂ ≈ 1.115 across monitored continuous params confirms chain-level disagreement.
>
> **Fix — exact marginalization (representation change, not spec amendment).** Spec §5.2 "Categorical latent per builder" remains the data-generating model. We integrate the latent out for inference and draw it back at posterior-predictive time. In the COHORT-1 model surface as currently constructed, `tier_idx` does **NOT enter the likelihood** of `tau_t`: the per-turn TruncPareto and per-day NegBin parameters are tier-independent (tier-conditional `(α_k, x_m,k, μ_k, φ_k)` is a future COHORT-2/3 enhancement; spec §5.4 sensitivity arms). The per-builder mixture marginalization
>
> $$
> p(\tau_t \mid \theta) \;=\; \sum_{k=1}^{3} \pi_k \cdot p(\tau_t \mid \mathrm{tier}=k, \theta_k) \;=\; p(\tau_t \mid \theta) \quad (\text{shared } \theta_k = \theta)
> $$
>
> is therefore **degenerate**: removing `tier_idx` from the inference graph leaves the likelihood and the posterior of `(π, μ, φ, α, x_m)` exactly unchanged (an identity, not an approximation). The per-builder tier draws are recovered at posterior-predictive time by sampling `tier_idx[builder] ~ Categorical(π_posterior_draw)` numpy-side, one draw per (chain, draw, builder) slot, using the shipped `numpy.random.Generator`.
>
> A property test (Property #7) is added that pins the numerical equivalence: the marginalized log-likelihood at fixed `(π, μ, φ, α, x_m)` equals the explicit-Categorical log-likelihood (LSE over tiers) within tolerance, on a synthetic τ_t observation grid.

### Secondary + tertiary marginalization (added during v0.4 implementation)

After applying the primary `tier_idx` marginalization, an end-to-end emit run on the v0.4 prototype produced r̂_max=1.062 / ESS_bulk_min=66.8 / ESS_tail_min=175.2 — better than v0.3 (1.115 / 38 / 58) but still failing the §8(8) gate. PyMC's `CompoundStep` invoked `Metropolis` on `n_per_day` (the 22-dim integer NegBin vector with `shape=(D_t,)`); the random-walk Metropolis on this discrete-vector latent left chain-level autocorrelation.

**Secondary fix.** Sum-of-iid NegBin closed form: `Σ_{j=1}^{D_t} N_j` where `N_j ~ NegBin(μ, φ)` iid is itself `NegBin(D_t·μ, D_t·φ)` in PyMC's mean-dispersion form (variance addition: `Var(ΣN_j) = D_t·μ + D_t·μ²/φ = (D_t·μ) + (D_t·μ)²/(D_t·φ)`, matching `NegBin(μ_total=D_t·μ, α_total=D_t·φ)` exactly). The 22-dim `n_per_day` vector is therefore replaced by a single direct draw `n_month ~ NegBin(D_t·μ, D_t·φ)`. The data-generating model spec §5.1 (T1) is unchanged at the marginal-of-the-sum level.

**Tertiary fix (necessitated by per-param diagnostics).** With `n_per_day` removed but `n_month` still a PyMC integer RV, per-param diagnostics showed:

    n_month       r̂=1.087   ESS_bulk=60.5   (1-dim Metropolis)
    mu            r̂=1.086   ESS_bulk=61.5   (NUTS, coupled to n_month)
    pi, phi, alpha_pareto, x_m   r̂≈1.0    ESS_bulk in the thousands

`n_month` Metropolis poorly mixed AND dragged `mu` (its location parameter under the NegBin) into chain-disagreement.

Since the COHORT-1 likelihood does NOT condition on `n_month` (`observed_tau_t=None` in production; `tau_t` Det only propagates `n_month` forward into emission), `n_month` is integrated out exactly. The v0.4 graph replaces the `n_month` NegBin RV with a Deterministic `mean_n_month = D_t·μ` (used only as the Stage-2 fit-arm proxy mean) and synthesizes the integer `n_month` numpy-side at PP time via `rng.negative_binomial(n=D_t·φ, p=D_t·φ/(D_t·φ+D_t·μ))` per (chain, draw) cell. The inference graph becomes **fully continuous** — pure NUTS over `(pi, mu, phi, alpha_pareto, x_m)`, no `CompoundStep`, no `Metropolis`. Three discrete latents (`tier_idx`, `n_per_day`, `n_month`) are recovered post-hoc; all three are exact (not approximate) marginalizations because the COHORT-1 likelihood is degenerate w.r.t. them.

### Single BLOCK resolution

| ID | Verdict-line citation | Fix location in v0.4 | Resolution summary |
|---|---|---|---|
| BLOCK-α (structural mixing failure) | v0.3 emit run `/tmp/c1-emit-stdout.log`: r̂_max=1.115 / ESS_bulk_min=38 / ESS_tail_min=58 | `simulations/saas_builder/model.py` (`pm.Categorical("tier_idx", ...)` REMOVED from `T1ModelFactory.__call__`); `simulations/saas_builder/emit.py` (`run_posterior_predictive` draws tier_idx numpy-side from posterior `pi`); `simulations/tests/test_saas_builder.py` (Property #7 added; tier_idx-in-RV assertions removed) | Marginalize per-builder Categorical `tier_idx` out of the inference graph. Inference now over continuous `(π, μ, φ, α, x_m)` only; NUTS handles the entire posterior with no Gibbs sweep. Per-builder tier draws recovered at PP time via `rng.choice(3, p=pi_draw, size=n_builders)`. Methodology preserved by Property #7 numerical-equivalence test (marginalized ≡ explicit-Categorical likelihood). |

### Pre-registered new behavior

- `T1ModelFactory.__call__` returns a `pm.Model` with the same `pi`, `mu`, `phi`, `alpha_pareto`, `x_m`, `n_per_day`, `n_month`, `mean_tau_per_turn`, `tau_t`, `q_t_usd`, `q_t_cop` nodes as v0.3, MINUS the `tier_idx` Categorical RV. The `n_builders` field is retained on the factory to seed the post-hoc per-builder tier draws at emit time.
- `simulations.saas_builder.emit.run_posterior_predictive` gains the post-hoc `tier_idx` draw: for each `(chain, draw)` posterior cell, sample `tier_idx ~ Categorical(pi[chain, draw, :])` of shape `(n_builders,)` using the shipped `numpy.random.Generator`. Injects a `tier_idx` array of shape `(chain, draw, n_builders)` into the `posterior_predictive` group so downstream emission paths (`_build_synthetic_tau_rows`) preserve their existing 3-D handling.
- `_PP_PYMC_VAR_NAMES` no longer includes `tier_idx` (removed from the `pm.sample_posterior_predictive` var list — it is no longer a graph variable).
- The `var_names` argument to `pm.sample` defaults remain unchanged. The existing `CompoundStep` is no longer triggered (no discrete RVs), so PyMC will use pure NUTS.

### Test delta

- REMOVED: `test_model_has_required_rvs` assertion on `"tier_idx"` membership of `unobserved_RVs`.
- REMOVED: `_make_synthetic_idata` / `_build_minimal_idata_for_emit` injection of `tier_idx` into the posterior group (replaced with injection into the posterior_predictive group, mirroring the new emit path).
- ADDED: `test_property_7_marginalization_numerical_equivalence` — pins the cohort mixture identity at fixed `(π, μ, φ, α, x_m)` over an observed-τ_t grid.
- ADDED: `test_emit_pp_draws_tier_idx_from_posterior_pi` — verifies the post-hoc tier_idx draw uses posterior `pi`.

### Pin invariants preserved

- M1 (α-floor 1.5 dual-enforced): UNCHANGED. `priors.py:TruncParetoAlphaPrior` lower=1.5, sampler-side `TruncParetoSampler.__post_init__` raises on α<1.5.
- M3 (Sonnet blended price 7.1495 ± 0.01): UNCHANGED. Asserted at `T1ModelFactory.__call__` site.
- M4 (parquet schema: `synthetic_tau_t` 11 columns + `cohort_prior` 6 columns including `schema_version`): UNCHANGED.
- M5 (FX path `[4200, 3800, 4200]` over 3 months): UNCHANGED.
- §8(7) CI-width ≤ 2× gate: UNCHANGED.
- §8(8) sim-floor per-chain ≥ 4000 / chains ≥ 4 / r̂ ≤ 1.01 / ESS ≥ 400 / divergence ≤ 0.5%: UNCHANGED.
- Anti-fishing: NO threshold relaxation; NO `n_builders` reduction (still 1000); NO test-fixture widening.

### Net delta vs v0.3

- `T1ModelFactory.__call__` removes the final `pm.Categorical("tier_idx", ...)` block.
- `_PP_PYMC_VAR_NAMES` in `emit.py` drops `"tier_idx"`.
- `run_posterior_predictive` in `emit.py` adds: numpy-side per-builder tier draw; injects 3-D `tier_idx` into `pp.posterior_predictive` group with shape `(chain, draw, n_builders)`.
- `_build_synthetic_tau_rows` reads `tier_idx` from `pp_idata["posterior_predictive"]` (post-hoc) instead of `posterior_idata["posterior"]`.
- Test fixtures `_make_synthetic_idata` and `_build_minimal_idata_for_emit` move `tier_idx` from posterior to posterior_predictive groups.
- One mutation-killer test (`test_emit_tier_idx_shape_matches_posterior`) renamed and re-pointed at the pp group.
- Plan v0.3 → v0.4. No CR-IMPORTANT / RC-FLAG / MQ-FLAG items from the v0.3 deferred list are addressed in v0.4 (those remain queued for v0.5).

### Reverify exit criteria (v0.4)

ACCEPT requires:
1. The single BLOCK above traceable to spec authority + shipped code + Property #7 numerical-equivalence test.
2. Test suite passes, ruff + ty clean.
3. `scripts/run_cohort1_emit.py` end-to-end run yields `verdict.passed = True` with the six §8(7) + §8(8) gate metrics in compliance:
   - r̂_max ≤ 1.01
   - ESS_bulk_min ≥ 400
   - ESS_tail_min ≥ 400
   - divergence_frac ≤ 0.005
   - sim-floor: chains ≥ 4 AND draws/chain ≥ 4000
   - ci_width_ratio_max ≤ 2.0
4. `synthetic_tau_t/tier_id=*/month=*/` parquet files written for all 3 months in the M5 FX path; `cohort_prior.parquet` written; `_AUDIT.json` sidecar with sha256 audit-block.
5. Anti-fishing invariants honored: no spec-pin relaxation; no test-fixture widening; no verdict-threshold tuning; the v0.3 emit failure is acknowledged in this CORRECTIONS-α block, not silently revised away.
