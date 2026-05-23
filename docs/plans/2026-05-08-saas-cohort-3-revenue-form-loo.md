# SAAS-COHORT-3 — Υ_t (cohort revenue process) form selection via PSIS-LOO-CV (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `feedback_no_code_in_specs_or_plans` (NON-NEGOTIABLE), this plan does NOT contain code blocks. Each task dispatches a specialized agent who authors code per the functional-python skill.
>
> **Foreground orchestrates, never authors.** Per repo memory `feedback_specialized_agents_per_task` (NON-NEGOTIABLE).

**Plan version:** v0.2 (2026-05-08 emit; CORRECTIONS-α folds 5 ACCEPT_WITH_FLAGS findings from RC + MQ Wave-1/2 verdicts; commit-eligible without reverify)
**Predecessor version:** v0.1 (2026-05-08 initial; ACCEPT_WITH_FLAGS at both waves; verdict files in `scratch/2026-05-08-cohort-plans-review/cohort-3-{rc,mq}-verdict.md`)
**Predecessor plans:** SIM-INFRA-0 v1.1 (REVERIFY-PASSED 2026-05-07) — Value/Callable/IO infrastructure consumed here.
**Spec anchor:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1 — §5 (Υ_t spec), §6 (functional-form table row Υ_t), §7 (PSIS-LOO-CV tooling commitment), §9 (TODO-COHORT-3 verification gate row), §10 (output artifact contract).
**Status:** LOCKED-PENDING-REVERIFY (post-hoc plan-doc 2-wave required before commit).

**Goal:** Select the cohort revenue process form Υ_t that best fits the post-revenue solo AI-native-builder cohort prior, choosing among three pre-pinned candidates (martingale, AR(1)-log-MRR, deterministic + churn) by PSIS-LOO-CV ELPD comparison via `arviz.compare`. Emit a verdict-routing artifact with ELPD-diff, SE, weight ranking, and PASS/MARGINAL/INDISTINGUISHABLE/WEAK/FAIL routing per spec §9.

**Architecture:** Three independent PyMC posterior fits over a shared synthetic Υ_t panel sourced from cohort-prior parquet (RESEARCH.md §6 + spec §5.2 brackets); each fit emits an InferenceData with pointwise log-likelihood; `arviz.compare(..., ic="loo")` computes ELPD diffs and SE; verdict-router maps the diff/SE pair to the spec §9 routing table. Posterior containers reuse `simulations/types/posterior.PosteriorDraws` (SIM-INFRA-0 contract); a Phase-1 research deliverable flags whether a Υ_t-specific extension is required (out-of-scope SIM-INFRA-0 patch — surfaced, not authored, here).

**Tech stack:** Python 3.13 + uv + PyMC + arviz + numpy + pandas + pyarrow. Functional-python three-tier discipline preserved. No sympy (closed-form not required); no Lean / Aristotle (per spec §7 Option 1).

**Sub-task position:** Independent of COHORT-1 and COHORT-2 at execution time (revenue dynamics do not consume cost posteriors). Blocks COHORT-4 jointly with COHORT-2.

**Out of scope (NOT covered by this plan):**
- Cost-side T1/T2 work (TODO-COHORT-1 monthly $/mo CDF; TODO-COHORT-2 softplus sticky fit). Distinct cohort plans.
- Z-cap pin (TODO-COHORT-4). Distinct cohort plan.
- Cohort survey ingest (Stage-3 Option γ n=30–75). Out of Stage 2 entirely.
- SIM-INFRA-0 contract patches. If `PosteriorDraws` lacks fields needed for a Υ_t time-series posterior, this plan flags it (Phase 1 research deliverable) but does NOT author the patch — that is a SIM-INFRA-0 v1.2 amendment.
- Notebook-trio authoring of empirical Υ_t (notebook lands in `notebooks/saas_builder_stage_2/cohort_3_upsilon_loo/`; the plan covers code authoring + headless execution, not interactive trio narration).

---

## File structure (folder-level only; .py decomposition is task-time discovery)

```
simulations/
├── saas_builder/
│   ├── __init__.py
│   ├── README.md
│   ├── cohort_3/
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── types/         # Value tier — Υ_t-specific containers (UpsilonPanel, RevenueFormFit, LooComparisonResult, VerdictRouting)
│   │   ├── modules/       # Callable tier — three model builders (martingale / ar1_log / det_churn), LOO comparator, verdict router
│   │   └── tests/         # property tests + math-pin tests + arviz-stub regression
│   └── (peer cohorts at sibling paths — out of scope here)
notebooks/saas_builder_stage_2/cohort_3_upsilon_loo/
└── (notebook trios — author in Phase 5; plan covers headless invocation only)
docs/plans/2026-05-08-saas-cohort-3-revenue-form-loo.md   # this file
scratch/2026-05-08-cohort-3-research/                     # Phase-1 research artifacts
scratch/2026-05-08-cohort-3-audit/                        # Phase-4 / Phase-5 audit reports
scratch/2026-05-08-cohort-3-plan-review/                  # 2-wave plan-doc verify (pre-commit)
```

Specific `.py` decomposition is decided by implementing agents at task-time per functional-python skill three-tier discipline. Tier-import discipline (types/ ↛ modules; modules/ ↛ utils) is enforced at Reality Checker verification (Phase 4).

---

## Phase 0 prelude — Math pins (REPRODUCED VERBATIM FROM SPEC §5–§9)

> Resolves anti-fishing invariant §8(5) (candidate-set closure). These pins are **inputs to every Phase-2 / Phase-3 task agent dispatch**. The implementing agent reads these contracts before authoring code; foreground enforces by including the relevant pin in each Task brief.

**Pin R1 — Three candidate Υ_t functional forms (spec §5 / §6 row Υ_t).** The candidate set is CLOSED at three forms. Adding a fourth form is an anti-fishing violation per spec §8(5) and fires HALT per `feedback_pathological_halt_anti_fishing_checkpoint`. Forms verbatim:

1. **Martingale (primary):**

$$\Upsilon_t \;=\; \Upsilon_{t-1} + \epsilon_t,\qquad \epsilon_t \sim \mathcal{N}(0,\sigma_\epsilon^2),\qquad \mathbb{E}[\Upsilon_{t+1}\mid\mathcal F_t] = \Upsilon_t.$$

2. **AR(1)-log (sensitivity arm a):**

$$\log \Upsilon_t \;=\; \rho \log \Upsilon_{t-1} + \epsilon_t,\qquad \epsilon_t \sim \mathcal{N}(0,\sigma_\epsilon^2),\qquad |\rho| < 1.$$

3. **Deterministic + churn (sensitivity arm b):**

$$\Upsilon_t \;=\; f(t) \cdot S_t,\qquad S_t \;=\; \prod_{s=1}^{t}(1 - \lambda_s),$$

where $f(t)$ is a deterministic growth/level path (parameterized as $f(t) = \Upsilon_0 \cdot (1+g)^t$ for primary fit; $g$ free) and $S_t$ is cohort survival under hazard $\lambda_s$ (parameterized as a single Beta-prior monthly churn $\lambda$ for primary fit; arm-internal sensitivity to time-varying $\lambda_s$ is OUT of scope here).

**Pin R2 — PSIS-LOO-CV via `arviz.compare` (spec §7, §9; resolves MQ-BLOCK-6).** Model selection MUST use `arviz.compare(model_dict, ic="loo", method="stacking")` over PyMC posteriors with pointwise log-likelihood emitted via `pm.compute_log_likelihood` (or equivalent `idata_kwargs={"log_likelihood": True}` at sample time). AICc, WAIC-only, DIC, and information-criterion arithmetic by hand are REJECTED. The expected log pointwise predictive density is:

$$\widehat{\mathrm{elpd}}_{\mathrm{loo}} \;=\; \sum_{i=1}^{n} \log p(y_i \mid y_{-i}),\qquad p(y_i \mid y_{-i}) \;\approx\; \frac{1}{S}\sum_{s=1}^{S} w_i^{(s)}\, p(y_i \mid \theta^{(s)}),$$

with importance weights $w_i^{(s)}$ smoothed by Pareto-smoothed importance sampling (PSIS); `arviz` reports the difference $\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}}$ and its standard error $\mathrm{SE}(\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}})$.

**Pin R3 — Verdict routing thresholds (spec §9 TODO-COHORT-3 row).** The verdict router maps $(\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}}, \mathrm{SE})$ between the top-ranked form and each runner-up to one of five buckets:

- **PASS** — top form is the winner: $|\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}}| > 4 \cdot \mathrm{SE}$ versus *every* runner-up.
- **MARGINAL** — top form leads but with $2 \cdot \mathrm{SE} \le |\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}}| \le 4 \cdot \mathrm{SE}$ versus the second-place form.
- **INDISTINGUISHABLE** — $|\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}}| < 2 \cdot \mathrm{SE}$ versus the second-place form. Verdict-router emits explicit INDISTINGUISHABLE label, NOT a silent winner pick.
- **WEAK** — diagnostic gates fail on at least one fit (see Pin R4) but ranking is computable; downstream consumer must treat as exploratory.
- **FAIL** — diagnostic gates fail on the top fit OR `arviz.compare` raises, OR Pareto-k diagnostic ($\hat k$) exceeds 0.7 for >5% of observations on the top fit. HALT per spec §8(10).

The thresholds (4·SE PASS / 2·SE INDISTINGUISHABLE) are PRE-PINNED and immutable; no post-hoc relaxation.

**Pin R4 — Diagnostic gates (spec §8(8) sim-count floor; arviz convention).** Each of the three PyMC fits MUST satisfy ALL of:

- ≥ 4,000 posterior draws across ≥ 4 chains.
- $\hat R \le 1.01$ for every parameter.
- ESS_bulk $\ge 400$ AND ESS_tail $\ge 400$ for every parameter.
- Pareto $\hat k < 0.7$ for $\ge 95\%$ of observations on the LOO computation; the verdict-router treats $\hat k \ge 0.7$ on >5% of observations as a FAIL on that form.

Any breach: WEAK if non-top form, FAIL if top form, HALT per `feedback_pathological_halt_anti_fishing_checkpoint`.

**Pin R4-bis — AR(1)-log posterior boundary-mass diagnostic (v0.2 MQ-FLAG-B fix; near-unit-root degeneracy).** In addition to the four diagnostic conditions above, the AR(1)-log fit MUST emit a posterior tail-mass diagnostic on the auto-regressive coefficient: $\Pr(|\rho| > 0.95 \mid \text{data})$ computed from the truncated-Normal posterior. Routing:
- $\Pr(|\rho| > 0.95) \le 0.05$ — clean; no action.
- $0.05 < \Pr(|\rho| > 0.95) \le 0.20$ — WEAK on the AR(1)-log form (non-stationarity warning); verdict-router downgrades AR(1)-log to WEAK if it would otherwise rank top.
- $\Pr(|\rho| > 0.95) > 0.20$ — HALT per `feedback_pathological_halt_anti_fishing_checkpoint`: posterior mass piling at the stationarity boundary indicates the AR(1)-log specification is mis-fitting the data; foreground emits disposition memo with ≥3 pivot options (e.g., switch primary to martingale, allow random-walk-with-drift sensitivity arm via SIM-INFRA-0 amendment, or close iteration with FAIL).
The diagnostic is recorded as `RevenueFormFit.rho_boundary_mass: float | None` (None for non-AR(1) forms; Task 2.1 adds the additive field). Truncated prior `Normal(0, 0.5)` truncated to $|\rho|<1$ is unchanged — the diagnostic catches posteriors that the truncation cannot detect.

**Pin R5 — Cohort prior input contract (spec §10).** The Υ_t panel input MUST be loaded from `notebooks/saas_builder_stage_2/data/cohort_prior.parquet` with the SIM-INFRA-0 Pin M4 schema (`param`, `percentile`, `value`, `source`, `fetched_at_utc`); a derived synthetic Υ_t panel (`upsilon_panel.parquet`) is emitted with columns `month`, `simulation_id`, `upsilon_cop`, `cohort_id`. The InferenceData artifacts emit to `estimates/cohort_3_idata_{martingale,ar1_log,det_churn}.nc` (NetCDF). The verdict artifact emits to `estimates/cohort_3_verdict.json` with fields `winning_form`, `verdict` (PASS/MARGINAL/INDISTINGUISHABLE/WEAK/FAIL), `delta_elpd_loo`, `se`, `pareto_k_max_per_form` (object), `weights_per_form` (object), `audit_block`, `fetched_at_utc`.

**Pin R6 — Anti-fishing closure.** Per spec §8(5), the candidate set {martingale, AR(1)-log, det+churn} is CLOSED. Per spec §8(3), §5.2 brackets are immutable. Per spec §8(10), any threshold breach (R3 FAIL or R4 FAIL) fires HALT cascade discipline: `superpowers:requesting-code-review` + disposition memo + user-enumerated pivot + CORRECTIONS-block + post-hoc 2-wave verify on the result.

---

## Phase 0 — Pre-flight

### Task 0.1 — Re-read functional-python skill from disk
Per `feedback_check_functional_python_skill_first.md` (NON-NEGOTIABLE).

- [ ] **Step 1** — Read `~/.claude/skills/functional-python/SKILL.md` via Read tool.
- [ ] **Step 2** — Confirm sha256 + line count match the reference recorded in `feedback_check_functional_python_skill_first.md`. If divergent, surface to user before proceeding.
- [ ] **Step 3** — Read-only; no commit.

### Task 0.2 — Confirm Python venv + dev deps
- [ ] **Step 1** — `uv venv --python 3.13` (idempotent).
- [ ] **Step 2** — `source .venv/bin/activate` and confirm `python --version` returns 3.13.x.
- [ ] **Step 3** — `uv pip install -r requirements.txt`.
- [ ] **Step 4** — Confirm PyMC ≥ 5.x and arviz ≥ 0.18 importable; `python -c "import pymc, arviz; print(pymc.__version__, arviz.__version__)"`. If absent, add to `pyproject.toml` and pin in CORRECTIONS-block of v0.2.

### Task 0.3 — Confirm SIM-INFRA-0 ACCEPT and contract availability
- [ ] **Step 1** — Confirm `simulations/types/posterior.py` exposes `PosteriorDraws` and that import succeeds: `python -c "from simulations.types.posterior import PosteriorDraws"`.
- [ ] **Step 2** — Confirm `simulations/utils/` parquet IO Boundary class is importable and round-trips a `cohort_prior.parquet` toy fixture per SIM-INFRA-0 Pin M4 schema.
- [ ] **Step 3** — Confirm `simulations/types/distributions.py` exposes the prior-parameter containers for any prior reused (NegBinParams, etc.). Read-only; no commit.

### Task 0.4 — Confirm working tree clean and on `iter/saas-builder-stage-2`
- [ ] **Step 1** — `git status --short`. Expect no modified files (untracked allowed).
- [ ] **Step 2** — `git branch --show-current`. Expect `iter/saas-builder-stage-2`.

### Task 0.5 — Confirm agent registry state
- [ ] **Step 1** — `find ~/.claude/agents -name 'engineering-ai-engineer*' -o -name 'specialized-reality-checker*' -o -name 'specialized-model-qa*' -o -name 'engineering-code-reviewer*' -o -name 'research-gsd-phase-researcher*'` returns active (non-archived) paths for all five. If any in `_archived/`, HALT per `feedback_pathological_halt_anti_fishing_checkpoint`.

---

## Phase 1 — Research and contract review

### Task 1.1 — Research (`gsd-phase-researcher`, background)

**Files:** Create `scratch/2026-05-08-cohort-3-research/RESEARCH.md`. Writes to `scratch/`, NOT `.planning/`, per `feedback_planning_dir_bespoke_naming.md`.

**Brief.** Pin PSIS-LOO-CV usage against SaaS revenue-trajectory econometrics literature. Specifically:

1. Does the SaaS-MRR / cohort-revenue literature use PSIS-LOO-CV for time-series-form selection between martingale, AR(1)-log, and det+churn classes? Cite ≥ 3 sources (Vehtari/Gelman/Yao papers + at least 1 SaaS-domain reference).
2. Within PyMC, what is the canonical pattern for emitting pointwise log-likelihood on a panel-of-iid-trajectories model versus a true time-series likelihood? Identify the failure mode of LOO when observations are dependent (single-trajectory log-lik) and the recommended LFO-CV alternative; pin which regime applies to our Υ_t use-case.
3. Does `simulations/types/posterior.PosteriorDraws` (SIM-INFRA-0 v1.1 shipped contract) support the fields needed for a time-series InferenceData round-trip (chains, draws, observed_data, log_likelihood, sample_stats)? If NO, flag as a Phase-1 research deliverable: "SIM-INFRA-0 v1.2 amendment requested" — but DO NOT author the patch in this plan.
4. For the det+churn form, what literature justifies a Beta-prior on monthly churn $\lambda$ for solo AI-native builders? Cite ≥ 2 sources for the prior parameterization; note the gap if literature is thin.
5. Pareto-$\hat k$ rule of thumb (>0.7 = problematic) — confirm the 5%-of-observations threshold versus the spec §9 routing as anti-fishing-safe.

Output: ≤ 1500 words; per-question section; references with URLs/citekeys; explicit "open question" marker on any item where literature is thin.

- [ ] **Step 1** — Foreground dispatches `research-gsd-phase-researcher` (canonical registry ID per Task 0.5) in background.
- [ ] **Step 2** — Continue Task 1.2 in parallel; 1.3 blocks on 1.1.

### Task 1.2 — Contract review (`AI Engineer`, parallel, read-only)

**Files:** Create `scratch/2026-05-08-cohort-3-research/CONTRACT_REVIEW.md`.

**Brief.** Read-only review:
1. Enumerate which `simulations/types/` Value containers are reused as-is (likely: `PosteriorDraws`, possibly tier-prior types).
2. Enumerate which Υ_t-specific containers are NEW to this cohort (candidates: `UpsilonPanel`, `RevenueFormFit`, `LooComparisonResult`, `VerdictRouting`). For each: justify why it cannot be expressed by an existing SIM-INFRA-0 type.
3. Identify the canonical PyMC + arviz idiom for `arviz.compare` returning a DataFrame indexed by model name, with columns `rank`, `elpd_loo`, `p_loo`, `elpd_diff`, `dse`, `weight`, `se`, `warning`. The verdict-router contract MUST be a free function on this DataFrame — not on raw InferenceData.
4. Identify any required edits to SIM-INFRA-0 `simulations/utils/` IO Boundary class to support InferenceData NetCDF persistence (likely: arviz `to_netcdf` / `from_netcdf` wrappers as a NEW IO Boundary class in this cohort's `cohort_3/` sub-folder, NOT a SIM-INFRA-0 patch). Output: ≤ 1000 words.

- [ ] **Step 1** — Foreground dispatches `engineering-ai-engineer` (canonical registry ID) in background.
- [ ] **Step 2** — Read-only; produces only the markdown.

### Task 1.3 — Plan reconciliation memo (foreground)

**Files:** Create `scratch/2026-05-08-cohort-3-research/PLAN_RECONCILIATION.md`.

- [ ] **Step 1** — Read 1.1 + 1.2 outputs.
- [ ] **Step 2** — Reconcile any disagreement between research literature pin and contract review (e.g., literature says "use LFO-CV for time-series" but contract review locks LOO; resolve by pinning to spec §7 commitment with documented dissent).
- [ ] **Step 3** — If 1.1 surfaces a needed SIM-INFRA-0 patch, file the request as a separate scratch artifact `scratch/2026-05-08-cohort-3-research/SIM_INFRA_0_V1_2_AMENDMENT_REQUEST.md` and HALT this plan pending user adjudication. Do not silently extend the SIM-INFRA-0 contract.
- [ ] **Step 4** — Commit research artifacts.

```bash
git add scratch/2026-05-08-cohort-3-research/
git commit -m "research(cohort-3): PSIS-LOO-CV literature pin + contract review + reconciliation"
```

---

## Phase 2 — Implementation

> **Sub-task split.** Phase 2 is split into four per-tier dispatches, each a separate `AI Engineer` dispatch with a scoped surface. Implementing agent decides .py decomposition within each surface. The pin prelude (R1–R6) is included in EVERY dispatch brief.

### Task 2.1 — Implement `simulations/saas_builder/cohort_3/types/`

**Files:** Create `simulations/saas_builder/__init__.py`, `simulations/saas_builder/README.md`, `simulations/saas_builder/cohort_3/{__init__.py, README.md}`, `simulations/saas_builder/cohort_3/types/{__init__.py, README.md, *.py}`.

**Agent.** `engineering-ai-engineer` (canonical registry ID per Task 0.5; v0.2 normalization).

**Inputs (passed in dispatch brief):**
- This plan's Phase 0 prelude (Pins R1–R6).
- Spec v1.1.1 §5, §6 (Υ_t row), §9 (TODO-COHORT-3 row), §10 (output schema).
- `notes/PRIMITIVES.md` §4.2 (AI-native builder cohort reinterpretation; streaming COP MRR).
- Phase 1 outputs (RESEARCH.md, CONTRACT_REVIEW.md, PLAN_RECONCILIATION.md).
- `simulations/types/posterior.py` shipped contract.
- functional-python skill (re-read in 0.1).

**Behavior contract:**
- Every `.py` file is Value-tier: `@dataclass(frozen=True)` + `__post_init__` validation only; no methods.
- Free-function accessors in same file.
- TypeAliases for repeated compound types; `Final` for module-level constants.
- No imports from `cohort_3/modules/` or any `simulations/utils/` path beyond Phase 1-pinned reuses.
- Must include encodings for: `UpsilonPanel` (panel of (month, simulation_id, upsilon_cop, cohort_id) with at least one cohort and ≥ 24 months); `MartingaleParams` ($\sigma_\epsilon > 0$); `Ar1LogParams` ($|\rho| < 1$, $\sigma_\epsilon > 0$); `DetChurnParams` ($\Upsilon_0 > 0$, $g \in [-0.5, 5.0]$ as a sanity bracket, $\lambda \in (0, 1)$); `RevenueFormFit` (form-name enum {`martingale`, `ar1_log`, `det_churn`} + InferenceData path + diagnostic-gate-pass flags per Pin R4); `LooComparisonResult` (the `arviz.compare` DataFrame columns as typed fields); `VerdictRouting` (verdict ∈ {PASS, MARGINAL, INDISTINGUISHABLE, WEAK, FAIL}, winning_form, delta_elpd_loo, se, pareto_k_max_per_form mapping, weights_per_form mapping, audit_block sha, fetched_at_utc).

- [ ] **Step 1** — Foreground dispatches `engineering-ai-engineer` (canonical registry ID) in background with the brief.
- [ ] **Step 2** — On agent completion, run `pytest simulations/saas_builder/cohort_3/tests/ -v` (initial sanity if any tests exist) and `ty check simulations/saas_builder/cohort_3/types/`. Both clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(cohort-3/types): Value-tier containers per spec §6 Υ_t row + Pin R5"
```

### Task 2.2 — Implement `simulations/saas_builder/cohort_3/modules/` — three model builders

**Files:** Create `simulations/saas_builder/cohort_3/modules/{__init__.py, README.md, *.py}`. Three Callables for the three model builders + a fourth for the fit driver.

**Agent.** `engineering-ai-engineer` (canonical registry ID per Task 0.5; v0.2 normalization).

**Inputs (passed in dispatch brief):**
- Phase 0 prelude (R1 verbatim — three forms; R4 sim-count + diagnostic gates; R5 IO contract).
- Task 2.1 output (imports allowed from `cohort_3/types/` and `simulations/types/`).
- Spec §5 (forms) + §7 (PyMC) + §8(8) (sim-count floor).

**Behavior contract:**
- Every `.py` file is Callable-tier: `@dataclass(frozen=True)` + `__call__`.
- May import from `cohort_3/types/` and `simulations/types/`; MUST NOT import from `simulations/utils/` or `cohort_3/utils/` (read/write happens in 2.4).
- Three model-builder Callables (`MartingaleModelBuilder`, `Ar1LogModelBuilder`, `DetChurnModelBuilder`), each returning a `pm.Model` instance for a given `UpsilonPanel`. The model MUST emit pointwise log-likelihood (`pm.compute_log_likelihood` invocation flag at sample time, OR explicit `Deterministic` node, per Phase 1 reconciliation Pin).
- Pre-pinned priors: martingale $\sigma_\epsilon \sim \text{HalfNormal}(s_\epsilon)$ where $s_\epsilon$ is anchored to RESEARCH.md §6; AR(1)-log $\rho \sim \text{Normal}(0, 0.5)$ truncated to $|\rho|<1$, $\sigma_\epsilon \sim \text{HalfNormal}(s_\epsilon)$; det+churn $\Upsilon_0 \sim \text{LogNormal}$ anchored to cohort prior, $g \sim \text{Normal}(\mu_g, \sigma_g)$, $\lambda \sim \text{Beta}(a,b)$ anchored per Phase 1 Q4.
- A `FitDriver` Callable runs `pm.sample(draws=4000, chains=4, ...)` per Pin R4 floor and returns the InferenceData (or a `RevenueFormFit` Value object). Diagnostic-gate-failure sets `RevenueFormFit.gates_passed = False`; the Callable does NOT raise on gate failure — it records and returns.
- The candidate set is closed: a runtime guard raises a typed `CandidateSetClosedError` if anyone tries to register a fourth form via the fit driver.
- **LFO-CV refit branch (v0.2 RC-FLAG-3 + MQ-FLAG-A fix; addresses LFO-CV-vs-LOO under trajectory-dependence).** When Phase-1 reconciliation (Task 1.3) returns "LFO required for time-series" — i.e., RESEARCH.md Q2 verdict identifies LOO-on-dependent-data as a load-bearing failure mode for the AR(1)-log and det+churn forms — the `FitDriver` Callable MUST expose an LFO-CV refit branch that invokes `arviz.loo` in `pointwise=True` + manual leave-future-out folds (Bürkner-Gabry-Vehtari 2020 LFO-CV pattern) instead of (or alongside) the canonical PSIS-LOO. Branch trigger: foreground inspects `PLAN_RECONCILIATION.md` and, **independently**, the runtime Pareto-$\hat k$ statistic — if any one fitted form returns $\hat k \ge 0.7$ on $> 5\%$ of observations (Pin R4 FAIL gate) AND the violations are concentrated on time-adjacent observations (auto-correlation of $\hat k$-flag indicator > 0.3), then LFO-CV refit is invoked. The LFO-CV branch reuses the same posterior draws and re-weights via approximate-LFO (PSIS over forward-step predictive density) — no resampling. The verdict-router treats LFO-CV ELPD identically to LOO ELPD (R3 thresholds 4·SE / 2·SE unchanged). LFO-CV branch records `cv_method: "lfo" | "loo"` in `RevenueFormFit` Value (additive field; Task 2.1 adds it as part of the Value-tier container). If the `arviz` version in `pyproject.toml` lacks LFO-CV utilities, the branch raises a typed `LfoCvUnavailableError` and the foreground HALTs per `feedback_pathological_halt_anti_fishing_checkpoint`. Default branch (when Phase-1 returns LOO-OK and runtime $\hat k$ is clean) is canonical PSIS-LOO unchanged.

- [ ] **Step 1** — Foreground dispatches `engineering-ai-engineer` (canonical registry ID) in background.
- [ ] **Step 2** — Run `pytest simulations/saas_builder/cohort_3/tests/ -v` (sanity) and `ty check simulations/saas_builder/cohort_3/modules/`. Both clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(cohort-3/modules): three model builders + fit driver per Pin R1, R4"
```

### Task 2.3 — Implement `simulations/saas_builder/cohort_3/modules/` — LOO comparator and verdict router

**Files:** Add `.py` files to `simulations/saas_builder/cohort_3/modules/` for `LooComparator` and `VerdictRouter`.

**Agent.** `engineering-ai-engineer` (canonical registry ID per Task 0.5; v0.2 normalization).

**Inputs:**
- Phase 0 prelude (R2 PSIS-LOO-CV formula; R3 verdict thresholds; R4 Pareto-$\hat k$ gate).
- Task 2.1 + 2.2 outputs.

**Behavior contract:**
- `LooComparator` Callable: takes a mapping `{form_name: RevenueFormFit}`, calls `arviz.compare(idata_dict, ic="loo", method="stacking")`, returns a `LooComparisonResult` Value.
- `VerdictRouter` Callable: takes a `LooComparisonResult` + the per-form gate-passed flags + per-form Pareto-$\hat k$ statistics, returns a `VerdictRouting` Value with verdict per Pin R3 thresholds. The router MUST emit INDISTINGUISHABLE explicitly when $|\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}}| < 2 \cdot \mathrm{SE}$; it MUST NOT silently pick a winner.
- Both Callables import from `cohort_3/types/` and `simulations/types/` only.
- `arviz.compare` warning column is propagated into `VerdictRouting.audit_block` for traceability.
- Verdict thresholds (4·SE, 2·SE) are `Final` module-level constants; no parameter override permitted (anti-fishing R6).

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — `pytest` + `ty check`. Clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(cohort-3/modules): LOO comparator + verdict router per Pin R2, R3"
```

### Task 2.4 — Implement `simulations/saas_builder/cohort_3/utils/` — IO boundary

**Files:** Create `simulations/saas_builder/cohort_3/utils/{__init__.py, README.md, *.py}`.

**Agent.** `engineering-ai-engineer` (canonical registry ID per Task 0.5; v0.2 normalization).

**Inputs:**
- Phase 0 prelude (R5 IO contract).
- Task 2.1 + 2.3 outputs.
- SIM-INFRA-0 `simulations/utils/` parquet IO Boundary precedent (read-only reuse).

**Behavior contract:**
- Every `.py` file is IO-Boundary-tier: `class Foo: def __init__(...)` allowed (mutable state lives ONLY here); not frozen-dc.
- May import from `cohort_3/types/`, `simulations/types/`, `simulations/utils/` only.
- `UpsilonPanelLoader`: reads `cohort_prior.parquet` per SIM-INFRA-0 M4 schema, derives `UpsilonPanel` per Pin R5, writes to `data/upsilon_panel.parquet`. Schema mismatch raises typed `SchemaMismatchError` (reuse SIM-INFRA-0 type if exposed; else local subclass of it).
- `InferenceDataPersister`: writes/reads InferenceData via `arviz.to_netcdf` / `from_netcdf` to `estimates/cohort_3_idata_{form}.nc`. Round-trip property tested in Phase 3.
- `VerdictArtifactWriter`: writes `VerdictRouting` to `estimates/cohort_3_verdict.json` per Pin R5 schema. JSON keys validated on round-trip.
- Audit-block sha helper: SHA-256 over the input parquet path + the cohort prior fetched_at_utc + the three idata.nc paths; pinned in `VerdictRouting.audit_block`.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — `pytest` + `ty check`. Clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(cohort-3/utils): IO boundary — panel loader + idata persister + verdict writer per Pin R5"
```

### Task 2.5 — Tests scaffold and strategies

**Files:** Create `simulations/saas_builder/cohort_3/tests/{__init__.py, README.md, strategies.py, test_*.py}`.

**Agent.** `engineering-ai-engineer` (canonical registry ID per Task 0.5; v0.2 normalization).

**Inputs:** Tasks 2.1–2.4; Phase 0 prelude (R1–R5 — every pin gets at least one regression test).

**Behavior contract:**
- `strategies.py`: one Hypothesis strategy per Value type from Task 2.1.
- Initial regression tests assert:
  - **R1 closure:** registering a fourth form raises `CandidateSetClosedError`.
  - **R1 form math:** synthetic-from-prior martingale data gives a `RevenueFormFit` for the martingale builder whose posterior $\sigma_\epsilon$ recovers the seed within prior CI-width.
  - **R2 LOO arithmetic:** on a tiny-data toy `arviz.compare` mock, `LooComparator` returns the expected `elpd_diff` and `dse` (numeric assert ±1e-6).
  - **R3 verdict thresholds:** verdict-router emits PASS at $|\Delta|=5\cdot\mathrm{SE}$, MARGINAL at $|\Delta|=3\cdot\mathrm{SE}$, INDISTINGUISHABLE at $|\Delta|=1\cdot\mathrm{SE}$, FAIL when gate flag is False on top form, WEAK when gate flag is False on a non-top form. **Boundary cases (v0.2 RC-FLAG-2 fix):** at $|\Delta|=2\cdot\mathrm{SE}$ AND $|\Delta|=4\cdot\mathrm{SE}$ exactly, verdict MUST be MARGINAL (closed-interval semantics on the MARGINAL band per Pin R3).
  - **R4 diagnostic gates:** synthetic InferenceData with $\hat R = 1.05$ marks `gates_passed = False`; with all gates clean marks True.
  - **R4-bis ρ boundary-mass (v0.2 MQ-FLAG-B fix):** synthetic AR(1)-log posterior with $\Pr(|\rho|>0.95) = 0.10$ → WEAK routing on AR(1)-log; with $\Pr(|\rho|>0.95) = 0.30$ → HALT triggered (test asserts the HALT-disposition path is invoked); with $\Pr(|\rho|>0.95) = 0.02$ → no action.
  - **R5 IO round-trip:** parquet panel write+read preserves columns and types; idata NetCDF round-trip preserves observed_data and log_likelihood; verdict JSON round-trip preserves all fields.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — `pytest simulations/saas_builder/cohort_3/tests/ -v`. All pass.
- [ ] **Step 3** — Commit.

```bash
git commit -am "test(cohort-3): initial strategies + math-pin tests for R1–R5"
```

---

## Phase 3 — Audit-pass chain (Honnibal sequence)

> Six sequential skill invocations. Order: tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing. Pre-mortem identifies fragilities first; mutation-testing then verifies tests cover them. Same order as SIM-INFRA-0 v1.1 §15.5.

### Task 3.1 — `tighten-types`
**Skill scope:** `simulations/saas_builder/cohort_3/`. Apply recommendations; re-test + re-typecheck; commit.
- [ ] **Step 1** — Invoke `superpowers:tighten-types` skill scoped to the cohort.
- [ ] **Step 2** — Apply agent recommendations (Pydantic where the skill recommends; preserve frozen-dc tier discipline).
- [ ] **Step 3** — `pytest simulations/saas_builder/cohort_3/tests/ -v && ty check simulations/saas_builder/cohort_3/`. Clean.
- [ ] **Step 4** — `git commit -am "audit(cohort-3): tighten-types pass"`.

### Task 3.2 — `contract-docstrings`
**Skill scope:** `simulations/saas_builder/cohort_3/`. Apply; re-test; commit. The three model-builder Callables MUST cite "spec §5 form (1)/(2)/(3)" verbatim in their docstrings; the verdict router MUST cite "spec §9 TODO-COHORT-3 row" verbatim; the LOO comparator MUST cite "spec §7 PSIS-LOO-CV via `arviz.compare`" verbatim.
- [ ] **Step 1–4** — Invoke / apply / verify / `git commit -am "audit(cohort-3): contract-docstrings pass — spec §5/§7/§9 citations pinned"`.

### Task 3.3 — `hypothesis-tests`
**Skill scope:** `simulations/saas_builder/cohort_3/modules/` + `simulations/saas_builder/cohort_3/tests/`.
**Additional property scope:**
- For the verdict router: a property test sweeping $\Delta\widehat{\mathrm{elpd}}_{\mathrm{loo}} / \mathrm{SE}$ ratio over $[0, 10]$ asserts the verdict is monotone in the ratio. **Boundary discipline (v0.2 RC-FLAG-2 fix; canonical interpretation of Pin R3):** INDISTINGUISHABLE iff ratio $\in [0, 2)$ (strict `<`); MARGINAL iff ratio $\in [2, 4]$ (closed both ends — at exactly $2 \cdot \mathrm{SE}$ AND at exactly $4 \cdot \mathrm{SE}$, verdict is MARGINAL); PASS iff ratio $\in (4, \infty)$ (strict `>`). Property-test cases include the two exact boundary values $\mathrm{ratio} = 2.0$ and $\mathrm{ratio} = 4.0$ → both MARGINAL. The `Final` constants in modules use `>` for PASS and `<` for INDISTINGUISHABLE; equality lands in MARGINAL by complement. Foreground REQUIRES the boundary test cases at 2.0 and 4.0 to assert MARGINAL exactly.
- For the LOO comparator: a property test on synthetic InferenceData triples asserts that swapping any two forms' names permutes the comparator's output rank column accordingly (rank-name covariance).
- For the model builders: a property test asserts that a martingale builder's posterior $\sigma_\epsilon$ scales linearly with the input panel's standard-deviation, holding seed fixed.
- [ ] **Step 1–4** — Invoke / apply / verify / `git commit -am "audit(cohort-3): hypothesis-tests pass — verdict-monotonicity, rank-name covariance, σ-scaling properties"`.

### Task 3.4 — `try-except`
**Skill scope:** `simulations/saas_builder/cohort_3/`. Tier reminder: only `cohort_3/utils/` should have non-trivial `try/except`. Modules should let typed errors propagate.
- [ ] **Step 1–4** — Invoke / apply / verify / `git commit -am "audit(cohort-3): try-except pass"`.

### Task 3.5 — `pre-mortem`
**Skill scope:** `simulations/saas_builder/cohort_3/modules/` AND `simulations/saas_builder/cohort_3/utils/`.

For each surfaced fragility: (a) regression test, (b) refactor, or (c) document in module README. Specific fragilities to enumerate (non-exhaustive — agent expands):

- PyMC sampler non-convergence on a degenerate prior (e.g., AR(1)-log with $\rho$ prior pinned at ±1 boundary). **v0.2 MQ-FLAG-B fix:** routed to Pin R4-bis posterior boundary-mass diagnostic, NOT to convergence diagnostics alone — $\Pr(|\rho|>0.95) > 0.20$ fires HALT independent of $\hat R$/ESS gate state.
- `arviz.compare` raising on log_likelihood absent (verify `pm.compute_log_likelihood` was invoked).
- Pareto-$\hat k$ exceeding 0.7 on >5% of obs for the top form (FAIL routing).
- InferenceData NetCDF round-trip silently dropping `log_likelihood` group on older arviz versions.
- Verdict-router floating-point edge cases at exactly $|\Delta| = 2 \cdot \mathrm{SE}$ or $4 \cdot \mathrm{SE}$ (closed-interval discipline per Pin R3 + v0.2 RC-FLAG-2 fix: both endpoints belong to MARGINAL band; INDISTINGUISHABLE uses strict `<` and PASS uses strict `>`).
- Cohort-prior parquet schema drift between SIM-INFRA-0 v1.1 and a future v1.2.

Pre-mortem produces the inventory; the next pass (mutation-testing 3.6) verifies tests cover them.

- [ ] **Step 1–4** — Invoke / apply / verify / `git commit -am "audit(cohort-3): pre-mortem pass — modules + utils fragilities enumerated"`.

### Task 3.6 — `mutation-testing`
**Skill scope:** `simulations/saas_builder/cohort_3/{types, modules, utils}/`.

**Kill-rate threshold: ≥ 80%** (industry-standard benchmark; not an analog of spec §8(7) posterior CI-width gate).

**Equivalent-mutant exemption cap: ≤ 5%** of total mutants. Each exemption requires a one-line justification in the report. If > 5% claimed equivalent, `Code Reviewer` audits the exemption list before this audit pass closes.

- [ ] **Step 1** — Invoke skill.
- [ ] **Step 2** — Iterate adding tests until kill rate ≥ 80% AND exemption rate ≤ 5%. Prefer adding tests over claiming exemption.
- [ ] **Step 3** — Re-test; commit.

```bash
git commit -am "audit(cohort-3): mutation-testing pass — kill rate $METRIC% (≥80%; equiv-exempt ≤5%)"
```

---

## Phase 4 — Verification gate

### Task 4.1 — Reality Checker compliance audit

**Files:** Create `scratch/2026-05-08-cohort-3-audit/reality_checker_compliance.md`.

**Agent.** `specialized-reality-checker` (canonical registry ID per Task 0.5; v0.2 normalization).

**Brief.** Audit `simulations/saas_builder/cohort_3/` against functional-python skill rules + Phase 0 math pins (R1–R6) + IO schema audit:

1. Every `@dataclass` in types/ has `frozen=True` (grep verified).
2. Inheritance only via `Protocol` or `Exception` subclassing.
3. Every public function has a return-type annotation.
4. No bare `Any` outside IO-boundary opaque returns; each instance documented.
5. Every module-level constant is `Final` (specifically the verdict thresholds 2·SE, 4·SE).
6. Every repeated compound type has a `TypeAlias`.
7. Tier-import discipline: types/ ↛ modules/utils; modules/ ↛ utils.
8. Audit artifacts (3.1–3.6) all present + commits visible in `git log`.
9. **Pin R1 closure:** Reality Checker MUST verify by direct test execution that registering a fourth form raises `CandidateSetClosedError`.
10. **Pin R2:** verify `arviz.compare(..., ic="loo")` is the function actually called (grep + import-trace).
11. **Pin R3 thresholds:** verify the `Final` constants `=== 2.0` and `=== 4.0` and that no parameter override path exists.
12. **Pin R4 diagnostic gates:** verify the `RevenueFormFit.gates_passed` flag is set per all four sub-conditions ($\hat R$, ESS_bulk, ESS_tail, Pareto-$\hat k$).
13. **Pin R5 schema audit:** read a synthetic-emit `cohort_3_verdict.json`, verify field presence + types per the prelude verbatim.
14. **Anti-fishing R6:** verify there is no path by which a non-pre-pinned threshold can be passed at runtime.

Default to REJECT. Each finding: file:line evidence. ≤ 1500 words.

**HALT trigger.** On REJECT verdict, foreground executes `feedback_pathological_halt_anti_fishing_checkpoint` protocol: (a) HALT, (b) disposition memo with ≥ 3 pivot options, (c) user adjudication, (d) CORRECTIONS-block in v0.2 of this plan, (e) post-hoc reverify.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Verdict ACCEPT or ACCEPT_WITH_FLAGS → advance. REJECT → HALT per above.
- [ ] **Step 3** — Commit verdict artifact.

### Task 4.2 — Model QA Specialist spec-doc reverify

**Files:** Create `scratch/2026-05-08-cohort-3-audit/model_qa_compliance.md`.

**Agent.** `specialized-model-qa` (canonical registry ID per Task 0.5; v0.2 normalization).

**Brief.** Independent statistical / spec-doc audit:

1. Spec-trace: each of Pins R1–R6 has a code path that implements it verbatim. The three forms in Pin R1 MUST be implemented with the priors and parameter spaces pinned; deviation is a BLOCK.
2. PSIS-LOO-CV usage critique: confirm `arviz.compare` is invoked with `ic="loo"`; confirm pointwise log-likelihood is emitted; confirm the data is iid-across-cohort-trajectories at the LOO leave-out unit (else flag for LFO-CV per Phase 1 reconciliation).
3. Verdict-routing thresholds (2·SE, 4·SE) match spec §9 verbatim.
4. Diagnostic-gate thresholds match spec §8(8) verbatim ($\hat R \le 1.01$, ESS ≥ 400, draws ≥ 4000 / chains ≥ 4) and arviz convention ($\hat k < 0.7$).
5. Anti-fishing closure: confirm the candidate set cannot be extended at runtime.
6. Identify any silent statistical fishing (e.g., default tuning that effectively narrows the prior post-hoc; default `target_accept` that biases toward one form).

Default to REJECT. ≤ 1500 words.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Verdict handling per Task 4.1 HALT discipline.
- [ ] **Step 3** — Commit verdict artifact.

### Task 4.3 — Static analysis sweep

**HALT trigger:** any failure → `feedback_pathological_halt_anti_fishing_checkpoint`.

- [ ] **Step 1** — `ruff check simulations/saas_builder/cohort_3/`. Zero warnings.
- [ ] **Step 2** — `ty check simulations/saas_builder/cohort_3/` (or `mypy --strict` equivalent). Zero errors.
- [ ] **Step 3** — `pytest simulations/saas_builder/cohort_3/tests/ -v --cov=simulations/saas_builder/cohort_3`. All pass; coverage ≥ 90%.
- [ ] **Step 4** — On any failure: HALT.

> **Note on plan-document verify.** Per `feedback_two_wave_doc_verification` (NON-NEGOTIABLE), this plan MUST be 2-wave verified (Reality Checker + Model QA Specialist) by foreground orchestration **before commit**, separate from the in-plan implementation gates above. Verdicts at `scratch/2026-05-08-cohort-3-plan-review/`. Plan executors do not re-run that pre-commit verify.

---

## Phase 5 — Code review, headless run, PR-readiness

### Task 5.1 — Code Reviewer audit

**Files:** Create `scratch/2026-05-08-cohort-3-audit/code_reviewer_report.md`.

**Agent.** `engineering-code-reviewer` (canonical registry ID per Task 0.5; v0.2 normalization). Per `feedback_implementation_review_agents`.

**Brief.** Independent code review: correctness, maintainability, performance. NOT functional-python compliance (covered by 4.1) and NOT statistical compliance (covered by 4.2). Specifically:
- PyMC model code idiomaticness (centered vs. non-centered parameterizations where applicable; `pm.Data` containers for swappable observed data).
- arviz API usage (correct `ic` argument, correct `method`, log_likelihood emission pattern).
- Test fixtures: synthetic data generators are deterministic (seeded); no hidden non-determinism.
- Performance: `pm.sample` invoked once per form per fit driver call; no redundant resampling.

- [ ] **Step 1** — Dispatch.
- [ ] **Step 2** — Apply non-blocking suggestions; HALT on blocking findings per `feedback_pathological_halt_anti_fishing_checkpoint`.
- [ ] **Step 3** — `git commit -am "review(cohort-3): Code Reviewer pass"`.

### Task 5.2 — Headless end-to-end run on toy panel

- [ ] **Step 1** — Stage a toy `cohort_prior.parquet` fixture under `simulations/saas_builder/cohort_3/tests/fixtures/` (small enough that `pm.sample(draws=4000, chains=4)` completes in < 5 minutes on a CPU).
- [ ] **Step 2** — Invoke the fit-driver + LOO comparator + verdict-router as a single pipeline; emit `cohort_3_idata_{martingale,ar1_log,det_churn}.nc` and `cohort_3_verdict.json`.
- [ ] **Step 3** — Manually inspect `cohort_3_verdict.json`: confirm verdict ∈ {PASS, MARGINAL, INDISTINGUISHABLE, WEAK, FAIL}; confirm all R5 fields present.
- [ ] **Step 4** — `git commit -am "test(cohort-3): headless toy-panel end-to-end run committed verdict artifact"`.

### Task 5.3 — CLAUDE.md update (if SIM-INFRA-0 path-listing changes)

- [ ] **Step 1** — Inspect whether `simulations/saas_builder/cohort_3/` warrants a CLAUDE.md repo-structure mention. If yes, add one line under repo structure noting "saas-builder Stage-2 cohort sub-packages (`simulations/saas_builder/cohort_N/`)".
- [ ] **Step 2** — `git commit -am "docs(cohort-3): CLAUDE.md repo-structure note"` (skip if no change).

### Task 5.4 — PR refresh

- [ ] **Step 1** — `git push origin iter/saas-builder-stage-2`.
- [ ] **Step 2** — Resolve PR number dynamically:

```bash
PR_NUM=$(gh pr list --repo wvs-finance/abrigo-analytics --search "head:iter/saas-builder-stage-2" --json number -q '.[0].number')
gh pr edit "$PR_NUM" --repo wvs-finance/abrigo-analytics --body "$(cat <<'EOF'
... [body update covering SAAS-COHORT-3 completion, verdict artifact path, and remaining Stage-2 sub-task status: COHORT-1 / COHORT-2 / COHORT-4] ...
EOF
)"
```

- [ ] **Step 3** — Confirm PR shows new commits.

---

## Verification matrix (cross-reference)

| Spec anchor | Pin | `cohort_3/` location | Verified by |
|---|---|---|---|
| §5 / §6 row Υ_t — three forms | R1 | `modules/` (three model builders) + `types/` (three params containers) | Tasks 2.1, 2.2, 3.3, 4.1 #9, 4.2 #1 |
| §7 — PSIS-LOO-CV via `arviz.compare` | R2 | `modules/` (LOO comparator) | Tasks 2.3, 4.1 #10, 4.2 #2 |
| §9 TODO-COHORT-3 — verdict thresholds | R3 | `modules/` (verdict router) + `types/VerdictRouting` | Tasks 2.3, 3.3, 4.1 #11, 4.2 #3 |
| §8(8) — sim-count + diagnostic floor | R4 | `modules/` (FitDriver) + `types/RevenueFormFit` | Tasks 2.2, 3.5, 4.1 #12, 4.2 #4 |
| §10 — output schema | R5 | `utils/` (panel loader, idata persister, verdict writer) | Tasks 2.4, 4.1 #13 |
| §8(5) — candidate-set closure | R6 | `modules/` (FitDriver runtime guard) + `Final` thresholds | Tasks 2.2, 2.3, 4.1 #14, 4.2 #5 |
| §9 — Pareto-$\hat k$ FAIL routing | R3+R4 | `modules/` (verdict router) | Tasks 2.3, 3.5, 4.1 #11, 4.2 #2 |

---

## Strategic delegation map

| Phase / Task | Agent / Skill | Surface |
|---|---|---|
| 1.1 Research | `research-gsd-phase-researcher` | PSIS-LOO-CV literature pin |
| 1.2 Contract review | `engineering-ai-engineer` | Read-only review of SIM-INFRA-0 contracts |
| 2.1 types/ | `engineering-ai-engineer` | Value tier |
| 2.2 modules/ — model builders | `engineering-ai-engineer` | Callable tier (PyMC) |
| 2.3 modules/ — LOO + verdict | `engineering-ai-engineer` | Callable tier (arviz) |
| 2.4 utils/ | `engineering-ai-engineer` | IO Boundary tier |
| 2.5 tests/ | `engineering-ai-engineer` | Test scaffold |
| 3.1 tighten-types | `superpowers:tighten-types` | All tiers |
| 3.2 contract-docstrings | `superpowers:contract-docstrings` | All tiers |
| 3.3 hypothesis-tests | `superpowers:hypothesis-tests` | modules/ + tests/ |
| 3.4 try-except | `superpowers:try-except` | utils/ primarily |
| 3.5 pre-mortem | `superpowers:pre-mortem` | modules/ + utils/ |
| 3.6 mutation-testing | `superpowers:mutation-testing` | All tiers |
| 4.1 RC compliance | `specialized-reality-checker` | Functional-python + Pin R1–R6 |
| 4.2 MQ spec-doc reverify | `specialized-model-qa` | Statistical / spec-trace |
| 4.3 Static sweep | foreground (ruff / ty / pytest) | All tiers |
| 5.1 Code review | `engineering-code-reviewer` | Correctness / maintainability |
| 5.2 Headless run | foreground | End-to-end |
| 5.4 PR refresh | foreground (gh) | Remote |

---

## Self-review checklist

- [x] Spec coverage complete (§5 forms, §6 Υ_t row, §7 tooling, §9 TODO-COHORT-3 row, §10 schema all mapped to tasks).
- [x] No code blocks (only bash + invocation snippets and HEREDOC PR body sketch).
- [x] Every task names agent / skill.
- [x] Every audit-pass commits separately.
- [x] Phase 0 includes functional-python skill re-read.
- [x] HALT triggers reference `feedback_pathological_halt_anti_fishing_checkpoint`.
- [x] Out-of-scope enumerated (T1/T2 cost, Z-cap, SIM-INFRA-0 patches, notebook authoring).
- [x] Math pins R1–R5 + anti-fishing R6 in Phase 0 prelude verbatim from spec.
- [x] Audit-pass order mirrors SIM-INFRA-0 v1.1 §15.5 (pre-mortem before mutation-testing).
- [x] Pre-mortem scope includes `utils/`.
- [x] Mutation 80% threshold disambiguated from spec §8(7).
- [x] Equivalent-mutant cap pinned at ≤ 5%.
- [x] PR number resolved dynamically.
- [x] Two-wave plan-doc reverify queued (`scratch/2026-05-08-cohort-3-plan-review/`).
- [x] Independence from COHORT-1 / COHORT-2 documented in header.
- [x] Phase-1 SIM-INFRA-0 v1.2 amendment-request escape hatch (1.3 Step 3) prevents silent contract drift.

---

## §"CORRECTIONS-α v0.1 → v0.2" — delta record

**emit_timestamp_utc:** 2026-05-08
**Trigger.** Wave-1 RC verdict ACCEPT_WITH_FLAGS (3 FLAGs) + Wave-2 MQ verdict ACCEPT_WITH_FLAGS (2 FLAGs); both at `scratch/2026-05-08-cohort-plans-review/cohort-3-{rc,mq}-verdict.md`. No BLOCKs at either wave. Per `feedback_pathological_halt_anti_fishing_checkpoint`, FLAGs are absorbable in CORRECTIONS-α without re-running 2-wave verify; this v0.2 is commit-eligible. Format precedent: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` §14.

### §15.1 — RC-FLAG-1 (dispatch-map informality) → canonical agent IDs

**Source:** RC verdict line 42 ("strategic delegation map names agents informally as 'AI Engineer' ... not the canonical registry IDs").
**Fix location:** Strategic delegation map (rows 1.1–5.1) + Task 1.1 Step 1 + every per-task `**Agent.**` brief (Tasks 1.2, 2.1–2.5, 4.1, 4.2, 5.1).
**Resolution.** All informal labels normalized to canonical registry IDs: `engineering-ai-engineer`, `specialized-reality-checker`, `specialized-model-qa`, `engineering-code-reviewer`, `research-gsd-phase-researcher`. Task 0.5 active-registry probe is unchanged (already canonical). Each replaced label carries the v0.2 normalization annotation in-line.

### §15.2 — RC-FLAG-2 (monotonicity boundary at `=4·SE`) → closed-interval disambiguation

**Source:** RC verdict line 44 ("the actual interval status at `=4·SE` (MARGINAL vs PASS) is ambiguous").
**Fix location:** Task 3.3 hypothesis-test scope (verdict-router monotonicity property) + Task 2.5 R3 thresholds test + Task 3.5 pre-mortem floating-point edge-case entry.
**Resolution.** Pin R3's MARGINAL band $[2 \cdot \mathrm{SE}, 4 \cdot \mathrm{SE}]$ is canonically closed at both endpoints. Property test ranges in Task 3.3 explicitly state INDISTINGUISHABLE iff ratio $\in [0, 2)$ (strict `<`); MARGINAL iff ratio $\in [2, 4]$ (closed both ends); PASS iff ratio $\in (4, \infty)$ (strict `>`). Task 2.5 boundary-case tests add explicit assertions at exactly $|\Delta| = 2 \cdot \mathrm{SE}$ AND $4 \cdot \mathrm{SE}$ → both MARGINAL. Task 3.5 pre-mortem entry now records the closed-interval semantics explicitly.

### §15.3 — RC-FLAG-3 + MQ-FLAG-A (LFO-CV vs LOO under trajectory-dependence) → LFO-CV refit branch in Phase 2

**Source:** RC verdict line 46 ("flagging for MQ Wave-2"); MQ verdict line 33 ("Phase-1 Q2 surfaces the LOO-on-dependent-data concern but Phase 2 has no LFO branch").
**Fix location:** Task 2.2 `FitDriver` behaviour contract (new bullet authorizing LFO-CV refit branch).
**Resolution.** `FitDriver` Callable now exposes an LFO-CV refit branch with two trigger conditions: (i) Phase-1 reconciliation memo verdict "LFO required for time-series" OR (ii) runtime Pareto-$\hat k$ FAIL gate WITH time-adjacent-violation pattern (auto-correlation of $\hat k$-flag indicator > 0.3). Branch reuses posterior draws + approximate-LFO via PSIS over forward-step predictive density (Bürkner-Gabry-Vehtari 2020 LFO-CV); verdict-router thresholds (R3) unchanged. `RevenueFormFit` Value gains additive field `cv_method: "lfo" | "loo"`. Default branch (LOO-OK + clean $\hat k$) is canonical PSIS-LOO unchanged. Phase-1 reconciliation gate (Task 1.3) remains the primary routing — runtime branch is belt-and-suspenders.

### §15.4 — MQ-FLAG-B (AR(1)-log near-unit-root posterior diagnostic) → Pin R4-bis

**Source:** MQ verdict line 34 ("Add P(|ρ|>0.95) reporting in `RevenueFormFit` and wire to WEAK/HALT in v0.2").
**Fix location:** New Pin R4-bis (Phase 0 prelude, immediately after Pin R4) + Task 2.5 boundary-mass test addition + Task 3.5 pre-mortem ρ-boundary entry annotation.
**Resolution.** Pin R4-bis adds a posterior tail-mass diagnostic on $\rho$: $\Pr(|\rho| > 0.95 \mid \text{data})$ computed from the truncated-Normal posterior; routing $\le 0.05$ clean / $(0.05, 0.20]$ WEAK / $> 0.20$ HALT. `RevenueFormFit.rho_boundary_mass: float | None` is an additive Value-tier field (None for non-AR(1) forms). Truncated prior $\rho \sim \text{Normal}(0, 0.5) \cap |\rho|<1$ unchanged — diagnostic catches posteriors the truncation alone cannot detect (mass piles up at the stationarity boundary even with truncation). Task 2.5 regression test covers three boundary-mass states (clean / WEAK / HALT). Task 3.5 pre-mortem entry now routes the ρ-boundary fragility to R4-bis explicitly, not to convergence diagnostics alone.

### §15.5 — Preserved guarantees

This patch preserves:

1. **Anti-fishing closure (Pin R6).** Candidate set {martingale, AR(1)-log, det+churn} unchanged; `CandidateSetClosedError` runtime guard unchanged; `Final` thresholds 2·SE / 4·SE unchanged. Pin R4-bis is a *new* diagnostic constraint (HALT-eligible), not a relaxation.
2. **Verdict-router thresholds (Pin R3).** 2·SE INDISTINGUISHABLE / 4·SE PASS pre-pinning is unchanged. RC-FLAG-2 fix only disambiguates the *boundary* semantics — strict `<` on INDISTINGUISHABLE, closed at endpoints for MARGINAL, strict `>` on PASS — which is the interpretation already implied by Pin R3's `≤` / `>` operators.
3. **PSIS-LOO-CV via `arviz.compare` (Pin R2).** Default cross-validation method is unchanged. LFO-CV branch (RC-FLAG-3 + MQ-FLAG-A fix) is conditional fallback only — triggered by Phase-1 verdict OR runtime $\hat k$-pattern; LOO remains primary.
4. **SIM-INFRA-0 contract (Pin R5).** No SIM-INFRA-0 v1.2 amendment is required by this patch. The new fields `cv_method` and `rho_boundary_mass` live on the cohort-3-local `RevenueFormFit` Value (Task 2.1 surface), not on `simulations/types/posterior.PosteriorDraws`.
5. **Phase-1 escape hatch (Task 1.3 Step 3).** SIM-INFRA-0 v1.2 amendment-request HALT path remains the only mechanism for upstream contract drift. v0.2 changes do not bypass it.
6. **2-wave verifier discipline.** v0.1 passed RC + MQ at ACCEPT_WITH_FLAGS; v0.2 absorbs the 5 FLAGs without invalidating the verdicts. Per RC verdict line 50 + MQ verdict line 38, no reverify is required.

### §15.6 — Anti-fishing posture

NO threshold relaxed. Three new constraints added (Pin R4-bis posterior boundary-mass HALT; LFO-CV trigger conditions; closed-interval boundary semantics). Each strictly *increases* the failure surface — i.e., increases the set of posterior states that route to WEAK or HALT — and therefore reduces the silent-fishing surface. Per `feedback_pathological_halt_anti_fishing_checkpoint`: trigger ✅ external 2-wave verify FLAGs; disposition memo ✅ this CORRECTIONS-α block enumerates per-FLAG resolution; user adjudication ✅ patch authored under explicit user instruction; old + new + preserved-guarantees argument ✅ §15.1–§15.5; post-hoc verify ⏳ NOT required (FLAGs are non-blocking; both verdicts state "no re-RC required" / "FLAG-A and FLAG-B route through CORRECTIONS-α in v0.2 ... neither blocks Phase 2 dispatch").

End of plan v0.2.

---

## §"CORRECTIONS-α v0.2 → v0.3" — delta record

**emit_timestamp_utc:** 2026-05-08
**Trigger.** Three independent post-implementation audits on commit `f86ce58`
(RC verdict ACCEPT_WITH_FLAGS at `scratch/2026-05-08-saas-cohort-3-independent-audit/rc-verdict.md`,
MQ verdict ACCEPT_WITH_FLAGS at `…/mq-verdict.md`, CR ACCEPT-grade with 3
SUGGESTIONS + 6 NITs) returned four convergent issues. None are BLOCKs;
all four are forward-fixable in CORRECTIONS-α before downstream propagation.
Per `feedback_pathological_halt_anti_fishing_checkpoint`, FLAGs are absorbable
without re-running 2-wave verify.

### §15.7 — LFO-CV mislabel (CR-S3 = MQ-FLAG-3 = RC-FLAG-3) → unconditional HALT

**Source.** RC verdict line 116 ("`models.py:416-425` LFO branch re-uses
`loo_result` and only flips `cv_method` label; no genuine forward-step PSIS
reweighting"); MQ verdict line 63-79 ("the `cv_method='lfo'` branch …
**falls through** without doing LFO; only the output label `cv_method='lfo'`
differs"); CR-S3 (same observation, dishonest data provenance).
**Fix location.** `simulations/saas_builder/cohort_3/models.py:415-425`
(`FitDriver.__call__` LFO branch); test addition at
`simulations/tests/test_saas_cohort3.py::test_fit_driver_lfo_request_raises_unconditionally`.
**Resolution.** The LFO branch now raises `LfoCvUnavailableError`
unconditionally whenever `cv_method == "lfo"` is requested, BEFORE any
`az.loo` call. Consumers cannot receive PSIS-LOO output under an LFO label;
foreground HALTs cleanly per CORRECTIONS-α §15.3 +
`feedback_pathological_halt_anti_fishing_checkpoint`. The `cv_method` field
on emitted `RevenueFormFit` is now hard-pinned to `"loo"` (dead branch
removed). The `Literal["loo", "lfo"]` admits "lfo" only as a request token —
never as an emitted label.

### §15.8 — `_first_trajectory` multi-trajectory truncation (CR-S4 = MQ-FLAG-1) → loud documentation + runtime warning

**Source.** MQ verdict line 26-43 ("the fit driver picks the first
`(cohort_id, simulation_id)` group and discards remaining trajectories. …
spec §5 does not authorize this restriction"); CR-S4 (same).
**Fix location.** `simulations/saas_builder/cohort_3/models.py:71-105`
(`_first_trajectory` docstring + runtime `warnings.warn`); test additions
at `…::test_first_trajectory_warns_on_multi_sim_panel` +
`…::test_first_trajectory_no_warn_on_single_sim_panel`.
**Resolution (option α — documentation-only).** Stage-2 single-trajectory
fit is preserved; hierarchical pooling across posterior trajectories is
DEFERRED to Stage-3 and out of scope for this iteration. The truncation is
now surfaced explicitly via (i) a "KNOWN LIMITATION" docstring section
referencing this §15.8 + spec §5 + Pin R5, and (ii) a runtime
`UserWarning` emitted when the panel carries N > 1 unique
`(cohort_id, simulation_id)` keys, listing how many trajectories are
discarded. Single-trajectory panels (the canonical Stage-2 input) emit no
warning. Option β (hierarchical refactor) was rejected as out-of-scope per
the user's autonomous-mode directive.

### §15.9 — `dse=0` → `+inf` ratio → PASS misclassification (CR-S1) → explicit branch

**Source.** CR-S1 ("`simulations/saas_builder/cohort_3/loo.py:218`. When
`se == 0.0` the code currently returns `inf` → PASS, but
`delta_elpd == 0` ∧ `se == 0` should classify as INDISTINGUISHABLE").
**Fix location.** `simulations/saas_builder/cohort_3/loo.py:218`
(`VerdictRouter.__call__` ratio computation); test additions at
`…::test_r3_dse_zero_with_zero_delta_is_indistinguishable` +
`…::test_r3_dse_zero_with_nonzero_delta_raises`.
**Resolution.** Replaced the silent `float("inf")` fallback with an
explicit two-branch disambiguation:

- `se == 0.0 ∧ delta_elpd == 0.0` → `ratio = 0.0` (legitimate ties under
  stacking; routes to INDISTINGUISHABLE band).
- `se == 0.0 ∧ delta_elpd != 0.0` → raise `ValueError` (degenerate input
  from `arviz.compare`; ratio is ill-defined; refusing to classify rather
  than silently passing).
- `se > 0.0` → `ratio = delta_elpd / se` (canonical path, unchanged).

Anti-fishing posture: the previous behaviour silently mapped a degenerate
input to PASS (a *strictly more permissive* classification). The new
behaviour either ties (INDISTINGUISHABLE — non-permissive) or raises
(non-permissive). Neither path increases the PASS surface.

### §15.10 — `winning_form = top` on INDISTINGUISHABLE (CR-S5 = RC-FLAG-1) → empty winner on INDISTINGUISHABLE/FAIL

**Source.** RC verdict line 101-106 ("`loo.py:257-259` sets
`winning_form = top` even when verdict is INDISTINGUISHABLE. Plan line 88
forbids 'silent winner pick'; … the field semantics could be tightened to
`winning_form = ""` on INDISTINGUISHABLE"); CR-S5 (same).
**Fix location.** `simulations/saas_builder/cohort_3/loo.py:257-259`
(verdict-router `winning_form` assignment) + `…/types.py` `VerdictRouting`
docstring + validation contract; test additions at
`…::test_r3_verdict_indistinguishable_no_winning_form_marginal_has_one`,
plus assertion added to existing
`…::test_r3_verdict_indistinguishable_at_1se`.
**Resolution.** `winning_form` is now declared iff `verdict ∈
{PASS, WEAK, MARGINAL}`; `verdict ∈ {INDISTINGUISHABLE, FAIL}` emits
`winning_form = ""` (no winner declared) per Pin R3's
explicit-non-winner semantics. Consumers wanting the
numerically-best form on INDISTINGUISHABLE can still inspect
`comparison.ranked_forms[0]`; verdict-router does NOT advertise it.
`VerdictRouting` Value-tier docstring + `__post_init__` invariants
updated to reflect the new contract.

### §15.11 — Preserved guarantees

This patch preserves:

1. **Anti-fishing closure (Pin R6).** `Final` thresholds 2·SE / 4·SE
   unchanged. Candidate set unchanged. `register_form` unconditional raise
   unchanged. New constraints (LFO unconditional HALT, dse=0 explicit
   refusal, INDISTINGUISHABLE no-winner) all *strictly increase* the
   failure surface — they reduce the set of posterior states that route
   to PASS or that silently advertise a winner. No threshold relaxed.
2. **Verdict-router thresholds (Pin R3).** Closed-interval boundary
   semantics from v0.2 §15.2 unchanged. The `winning_form` discipline in
   §15.10 is a *tightening* of Pin R3's "no winner declared on
   INDISTINGUISHABLE" semantics — already implied; now enforced.
3. **PSIS-LOO-CV via `arviz.compare` (Pin R2).** Default LOO branch
   unchanged. §15.7 only removes a dishonest LFO-fall-through path; LOO
   remains canonical and is the only emitted CV method.
4. **SIM-INFRA-0 contract (Pin R5).** No SIM-INFRA-0 amendment required.
   All edits live in `simulations/saas_builder/cohort_3/`.
5. **Stage-2 / Stage-3 boundary.** §15.8 makes the Stage-2
   single-trajectory restriction explicit and documented; hierarchical
   pooling remains a Stage-3 concern. The Stage boundary is not crossed.
6. **2-wave verifier discipline.** v0.2 passed RC + MQ + CR at
   ACCEPT-grade; v0.3 absorbs the 4 convergent FLAGs without invalidating
   any verdict. Per the three audit verdicts, no reverify is required.

### §15.12 — Out-of-scope (deferred to v0.4 or escalated)

- **MQ-FLAG-2 (Det+churn S_t Bernoulli vs deterministic).** Not addressed
  here; surfaces as a spec-amendment request to user — the `(1-λ)^t`
  collapse is a non-trivial methodological choice that should be pinned
  in spec §5 explicitly (Bernoulli/exponential survival vs. deterministic
  factor with Beta-prior λ shared across months).
- **CR NITs (×6).** Deferred to v0.4 cosmetic pass.
- **Phase 5 e2e real-sample (`pm.sample(draws=4000, chains=4)`).** Runner
  script authored separately; not a code-change concern of v0.3.

### §15.13 — Anti-fishing posture

NO threshold relaxed. Four new constraints added (LFO unconditional HALT;
dse=0 explicit ValueError on degenerate input; `winning_form = ""` on
INDISTINGUISHABLE/FAIL; multi-trajectory `UserWarning`). Each strictly
*increases* the failure or surface-of-attention — i.e., increases the set
of posterior states that route to HALT, refuse classification, or emit no
winner — and therefore reduces the silent-fishing surface. Per
`feedback_pathological_halt_anti_fishing_checkpoint`: trigger ✅ three
external audit verdicts (RC + MQ + CR); disposition memo ✅ this block;
user adjudication ✅ explicit user instruction in autonomous mode;
old + new + preserved-guarantees argument ✅ §15.7–§15.11; post-hoc verify
⏳ NOT required (FLAGs are non-blocking; all three verdicts ACCEPT-grade).

End of plan v0.3.
