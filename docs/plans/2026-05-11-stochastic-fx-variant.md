# STOCHASTIC-FX VARIANT — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. **Tracking unit is the TASK (one task per commit), not per-step** — matches the repo's cohort-N convention (see `docs/plans/2026-05-08-saas-cohort-*` precedents). Per-step `- [ ]` checkboxes are intentionally NOT used; subagent-driven-development's TaskCreate/TaskUpdate is the tracking surface. (FLAG-RC-2 disposition; §16.1.)
>
> **Code-agnostic plan.** Per repo memory `memory/feedback_no_code_in_specs_or_plans.md` (NON-NEGOTIABLE), this plan does NOT contain Python code blocks. Each task dispatches a specialized agent who authors code per the functional-python skill + the Honnibal audit-pass chain.
>
> **Foreground orchestrates, never authors.** Per repo memory `memory/feedback_specialized_agents_per_task.md` (NON-NEGOTIABLE).

**Plan version:** v0.6 (Wave-1 v0.2 ACCEPT_WITH_FLAGS-DISPOSED; v0.3 §16.3 Task 3.1 grid-density; v0.4 §16.4 Task 3.3 σ_T statistic mismatch; v0.5 §16.5 Task 4.2 Pin Z1.3b mean-only; v0.6 adds §16.7 — Task 4.2 mid-execution Pin Z1.4 per-family Phase C reference dispatch (Merton → empirical-CDF via high-N) per user disposition 2026-05-13. Parent spec v0.4 → v0.5 in parallel.)
**Parent spec:** `docs/specs/2026-05-11-stochastic-fx-variant-design.md` v0.3 (Wave-1 ACCEPT_WITH_FLAGS-DISPOSED)
**Predecessor:** `simulations/saas_builder/cohort_5_strip/` (commit `3442852`, audit `94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329` — PRESERVED unchanged per Pin Z1.6)
**Status:** Wave-1 ACCEPT_WITH_FLAGS-DISPOSED — per-task execution authorized once §16.1 corrections land
**Estimated wall-time:** 5–7 days of focused work

---

## §0 Goal

**One sentence.** Build the `simulations/stochastic_fx/` package per the spec v0.3 architecture: three SDE families (GBM, OU, Merton jump-diffusion) with the three-phase per-family verification pipeline (Phase A algebraic inversion / Phase B moment match against hand-derived analytic moments / Phase C KS goodness-of-fit against moment-matched parametric reference), preserving the cohort_5_strip strip-emit invariant.

## §1 Architecture

Three-tier discipline mirroring cohort_5_strip. Package is INDEPENDENT of all first-wave Stage-3 tracks; READ-ONLY consumer of `notes/PRIMITIVES.md` and reuse of `simulations.saas_builder.cohort_4.types::NUMERICAL_IDENTITY_TOL`. Strip preservation invariant (Pin Z1.6) means no cohort_5_strip file is touched.

Hand-derived analytic moments per family (Hull §15 for GBM; standard OU; Andersen-Piterbarg Vol I §2.7 for Merton) live as both Python expressions in `moments.py` AND `.tex` fragments rendered via `sympy.latex(...)` under `notes/stochastic_fx_tex/`. The `.tex` fragments are the integration hook for the future LaTeX-econ-paper consolidator (spec §7.2).

## §2 Tech stack

- Python 3.13, functional-python skill (frozen-dc / free fns / IO Boundary tier).
- NumPy for path generation (`numpy.random.default_rng` for deterministic RNG).
- SciPy for the KS test (`scipy.stats.ks_1samp`) and reference-distribution fits (`scipy.stats.lognorm.fit`, `scipy.stats.gamma.fit`).
- Sympy for algebraic simplification + LaTeX rendering (NOT Itô calculus).
- Hypothesis for property tests on path-distribution invariants and RNG determinism.
- Existing `simulations/utils/{parquet_io.py, json_io.py, audit_block.py}` patterns for emit.

---

## §3 Cross-spec references

| Spec section | This plan's coverage |
|---|---|
| §3 Components — `_errors.py` | Task 1.1 |
| §3 Components — `types.py` | Tasks 1.2 (Parameters frozen-dc per family), 1.3 (PathEnsemble + InversionVerdict) |
| §3 Components — `moments.py` | Task 2.1 (GBM + OU + Merton hand-derived moments + LaTeX rendering) |
| §3 Components — `generators.py` | Tasks 3.1 (GBM), 3.2 (OU), 3.3 (Merton) |
| §3 Components — `variance_proxy.py` | Task 4.1 |
| §3 Components — InversionVerifier (combines Phase A/B/C) | Task 4.2 |
| §3 Components — `emit.py` | Task 5 |
| §3 tests/ | Each task has its own test sub-step; Task 6 runs end-to-end gates |
| §4.1 Phase A (Pin Z1.3a algebraic) | Task 4.1 |
| §4.1 Phase B (Pin Z1.3b moment match) | Task 4.2 |
| §4.1 Phase C (Pin Z1.4 KS test) | Task 4.2 |
| §4.2 Per-family parameter pin table | Task 1.2 (constants); Task 6 (verification) |
| §5 Pin Z1.6 (strip preservation) | Task 7 |
| §11.2 outstanding repo work | Task 0 (gitignore line) |

---

## §4 File structure

```
docs/plans/2026-05-11-stochastic-fx-variant.md          ← THIS plan
scratch/2026-05-11-stochastic-fx-execution/
├── moment_verification_log.md         Task 6 record of per-family Phase B verdicts
├── ks_test_log.md                     Task 6 record of per-family Phase C verdicts
└── pin_z16_strip_preservation_log.md  Task 7 record of audit_block hex grep verdict

.gitignore                              MODIFY (Task 0)

simulations/stochastic_fx/              NEW package
├── __init__.py                         Public API re-exports (Task 1.1 final)
├── _errors.py                          Task 1.1
├── types.py                            Task 1.2 + 1.3
├── moments.py                          Task 2.1
├── generators.py                       Tasks 3.1 + 3.2 + 3.3
├── variance_proxy.py                   Task 4.1 + 4.2
└── emit.py                             Task 5

notes/stochastic_fx_tex/                NEW directory (Task 5)
├── eps_inversion.tex                   Single fragment — eq. (8) algebraic form (family-agnostic)
├── sigma_t_moments_gbm.tex             GBM moments (Hull §15 anchor)
├── sigma_t_moments_ou.tex              OU stationary moments
└── sigma_t_moments_merton.tex          Merton jump-diffusion moments (Andersen-Piterbarg Vol I §2.7)

notes/STOCHASTIC_FX_RESULTS.md          NEW (Task 6) — parallel to STAGE_2_RESULTS.md

simulations/stochastic_fx/data/         NEW gitignored directory (per Task 0)
├── path_ensemble_gbm.parquet           emitted; gitignored
├── path_ensemble_ou.parquet            emitted; gitignored
├── path_ensemble_merton.parquet        emitted; gitignored
├── inversion_verdict_gbm.json          emitted; gitignored
├── inversion_verdict_ou.json           emitted; gitignored
└── inversion_verdict_merton.json       emitted; gitignored

simulations/tests/test_saas_stochastic_fx.py   NEW (tests under each task; final integration in Task 6)
```

---

## §5 Phase 0 — Repo infrastructure

### Task 0 — Add gitignore line for new emit directory

**Files:**
- Modify: `.gitignore` (add `simulations/stochastic_fx/data/` per spec v0.3 §11.2 outstanding repo work)

**Agent dispatch:** N/A — orchestrator-only operation (single-line gitignore edit per `memory/feedback_specialized_agents_per_task.md` shell-ops exception).

**Acceptance:**
- `.gitignore` now contains a line `simulations/stochastic_fx/data/` (alphabetically near existing line 53's `simulations/saas_builder/data/`).
- `git check-ignore simulations/stochastic_fx/data/anything.parquet` returns the path (gitignored).

**Commit message:** `chore(gitignore): add simulations/stochastic_fx/data/ per stochastic-fx-variant spec v0.3 §11.2`

---

## §6 Phase 1 — Value tier (types + errors)

### Task 1.1 — Author `_errors.py` + initial `__init__.py`

**Files:**
- Create: `simulations/stochastic_fx/__init__.py`
- Create: `simulations/stochastic_fx/_errors.py`

**Agent dispatch:** `Senior Developer` (Value-tier exception authoring per `memory/feedback_specialized_agents_per_task.md`).

**Acceptance:**
- `_errors.py` exports `StochasticFXError(Exception)` base + `SDEParameterError(StochasticFXError)` + `InversionTestFailedError(StochasticFXError)` + `MomentMatchFailedError(StochasticFXError)` + `MCBudgetExceededError(StochasticFXError)`. Mirrors `simulations/saas_builder/cohort_4/_errors.py` style.
- `__init__.py` is a minimal stub re-exporting the four exceptions. Full public API re-exports get appended as tasks land.
- One unit test in `simulations/tests/test_saas_stochastic_fx.py` confirms exception inheritance chain via `issubclass`.

**Commit message:** `feat(stochastic_fx): _errors.py + __init__.py stub`

---

### Task 1.2 — Author per-family Parameters Value types

**Files:**
- Create: `simulations/stochastic_fx/types.py` (initial — Parameters types only; PathEnsemble + InversionVerdict added in Task 1.3)
- Modify: `simulations/stochastic_fx/__init__.py` (re-export Parameters types)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add Parameters tests)

**Agent dispatch:** `Senior Developer`.

**Acceptance:**
- Three frozen-dataclass Parameters Value types, one per SDE family. Each has the fields and `__post_init__` invariants documented in the table below (FLAG-RC-1 disposition: function/class signatures replaced with prose tables).

  **Per-family Parameters fields + invariants:**

  | Family | Required fields | `__post_init__` invariants |
  |---|---|---|
  | GBM | drift, volatility, spot, horizon, step size, number of steps | volatility > 0; spot > 0; horizon > 0; step size > 0; number of steps ≥ 2; number of steps × step size equals horizon within float tolerance |
  | OU | mean-reversion rate, long-run mean, volatility, spot, horizon, step size, number of steps | mean-reversion rate > 0; volatility > 0; long-run mean > 0; spot > 0; horizon > 0; step size > 0; number of steps ≥ 2 |
  | Merton jump-diffusion | drift, diffusion volatility, jump intensity, jump-size mean, jump-size std, spot, horizon, step size, number of steps | diffusion volatility > 0; jump intensity ≥ 0; jump-size std > 0; spot > 0; horizon > 0; step size > 0; number of steps ≥ 2 |

- Module-level canonical-pin constants per spec v0.3 §4.2 table, one per family. Numerical values per spec v0.3 §4.2 row entries verbatim. Pin values frozen at this commit; ex-post tuning requires CORRECTIONS-α + scoped Wave-1 re-review per Pin Z1.5.
- One Hypothesis property test per family checking `__post_init__` rejects invalid parameter combinations (zero or negative volatility; number of steps < 2; etc.) AND accepts the canonical pins from spec v0.3 §4.2.
- ruff + ty clean on `simulations/stochastic_fx/`.

**Commit message:** `feat(stochastic_fx/types): per-family Parameters + canonical pins`

---

### Task 1.3 — Author `PathEnsemble` + `InversionVerdict` Value types

**Files:**
- Modify: `simulations/stochastic_fx/types.py` (append the two new Value types)
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add validation tests)

**Agent dispatch:** `Senior Developer`.

**Acceptance:**
- `PathEnsemble` frozen-dataclass holding: a family identifier from the closed alphabet `{gbm, ou, merton}`; a 2-D path matrix (N paths × n_steps+1 timesteps); a 1-D realised-variance array of length N (one σ_T value per path); the canonical parameters JSON-serialized as a string; the deterministic RNG seed used to sample the ensemble; and a 64-char lowercase hex audit_block. `__post_init__` validates: path matrix is 2-D; σ_T array shape matches path-count; audit_block matches the 64-char lowercase hex regex; family identifier is in the closed alphabet.
- `InversionVerdict` frozen-dataclass holding: family identifier; Phase-A pass flag + max algebraic-inversion residual (Pin Z1.3a); Phase-B pass flag + mean and var relative errors (Pin Z1.3b); Phase-C pass flag + KS p-value + path-count used (Pin Z1.4); composite pass flag (logical AND of the three phase flags); a tex_anchor string pointing to the family's LaTeX fragment file; and a 64-char audit_block. `__post_init__` validates: bool fields are bool; composite pass equals the AND of the three phase flags; tolerances numerically reasonable; audit_block matches hex regex; family identifier in closed alphabet.
- One Hypothesis property test per type confirming `__post_init__` rejects invalid combinations.
- ruff + ty clean.

**Commit message:** `feat(stochastic_fx/types): PathEnsemble + InversionVerdict`

---

## §7 Phase 2 — Hand-derived analytic moments + LaTeX fragments

### Task 2.1 — Author `moments.py` with per-family E[σ_T] and Var[σ_T]

**Files:**
- Create: `simulations/stochastic_fx/moments.py`
- Create: `notes/stochastic_fx_tex/sigma_t_moments_gbm.tex`
- Create: `notes/stochastic_fx_tex/sigma_t_moments_ou.tex`
- Create: `notes/stochastic_fx_tex/sigma_t_moments_merton.tex`
- Create: `notes/stochastic_fx_tex/eps_inversion.tex`
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add per-family moment tests)

**Agent dispatch:** `AI Engineer` (math-heavy; coordinates with sympy) + inline `Reality Checker` cross-check that the implemented Python expressions match the hand-derived formulas in spec v0.3 §4.2 verbatim.

**Acceptance:**
- Three free functions in `moments.py`, one per family. Each takes the family's Parameters frozen-dataclass and returns a tuple of two floats: the analytic E[σ_T] and the analytic Var[σ_T]. Per-family math content pinned in the table below (FLAG-MQ-1 + FLAG-MQ-3 disposition: Merton and Var forms now literalised; FLAG-RC-1 disposition: function signatures replaced with prose table).

  **Per-family hand-derived analytic moments** (substitution `(X̄/Ȳ)² → params.x_0**2` at the canonical pin per FLAG-MQ-2; symbolic form retained in `.tex`):

  | Family | Analytic E[σ_T] (Python form) | Analytic Var[σ_T] (Python form) |
  |---|---|---|
  | GBM | `params.x_0**2 * ((exp(params.sigma**2 * params.T) - 1) / (params.sigma**2 * params.T) - 1)` (exact; vanishes at σ→0 per NEW-BLOCK-MQ-4 fix) | `2 * (params.x_0**4) * (exp(params.sigma**2 * params.T) - 1)**2 / (params.sigma**4 * params.T**2)` (Hull §15 leading order; assumes mean-zero log-drift) |
  | OU (stationary) | `params.sigma**2 / (2 * params.theta)` (exact) | `2 * params.sigma**4 / ((2 * params.theta)**2 * params.T)` (leading order under chi-squared approximation; standard OU stationary moment) |
  | Merton jump-diffusion | `params.x_0**2 * params.sigma**2 * params.T + params.lambda_jump * params.x_0**2 * (exp(2*(params.jump_mean + params.jump_std**2)) - 2*exp(params.jump_mean + params.jump_std**2/2) + 1) * params.T` (Andersen-Piterbarg Vol I §2.7; leading order; mean-zero log-drift) | `2 * params.sigma**4 * params.x_0**4 * params.T + params.lambda_jump * params.x_0**4 * (variance contribution from compound-Poisson moment-of-moment; Andersen-Piterbarg §2.7.3 formula expanded literally — implementer transcribes the textbook expression into Python at authoring time, NOT spec-time) |

- **`moments.py` module docstring** (FLAG-MQ-2 disposition) MUST explicitly document the `(X̄/Ȳ)² → params.x_0**2` substitution: the canonical-pin convention pins `x_0 = X̄/Ȳ = 4000.0` so the two are interchangeable at evaluation time, but the SYMBOLIC form `(X̄/Ȳ)²` is the conceptually-correct one and is what the `.tex` fragments retain.

- Numerical sanity test per family: at canonical pins (Task 1.2 spec v0.3 §4.2 table values), the Python-form expressions evaluate to numbers within `1e-12` of hand-computed analytic numbers logged in the test.

- LaTeX-fragment emission via `sympy.latex(...)` for each family's moment expressions; saved to `notes/stochastic_fx_tex/sigma_t_moments_{family_id}.tex` where `{family_id}` ∈ `{gbm, ou, merton}` (NIT family naming drift disposition: use `{family_id}` consistently with the PathEnsemble closed alphabet). Each fragment contains:
  - The exact-form LaTeX retaining symbolic `(X̄/Ȳ)²` notation per FLAG-MQ-2 (NOT the Python substituted form).
  - Literature citation as a LaTeX `\cite{}` (or inline `% ref: ...` comment if a bib file is not present).
  - A numerical-pin example at the canonical fixture, computed via the Python form.

- Also write the family-agnostic eq. (8) algebraic inversion LaTeX to `notes/stochastic_fx_tex/eps_inversion.tex` (single one-line fragment).
- Hypothesis property tests: monotonicity of E[σ_T] in volatility per family; bounds checks (E ≥ 0, Var ≥ 0).
- ruff + ty clean.

**Commit message:** `feat(stochastic_fx/moments): per-family E[σ_T] + Var[σ_T] + LaTeX fragments`

---

## §8 Phase 3 — SDE path generators

### Task 3.1 — Author `GBMPathGenerator`

**Files:**
- Create: `simulations/stochastic_fx/generators.py` (initial — GBM only; OU + Merton added in 3.2 + 3.3)
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add GBM generator tests)

**Agent dispatch:** `Senior Developer` + `AI Engineer` (paired — Senior Developer for the three-tier scaffolding; AI Engineer for the SDE discretization scheme).

**Acceptance:**
- `GBMPathGenerator` frozen-dataclass holding the family's Parameters. Its callable surface accepts a deterministic RNG seed and the number of paths, and returns a PathEnsemble. Uses `numpy.random.default_rng(seed)` for reproducibility per Pin Z1.2. (FLAG-RC-1 disposition: signature prose-ified.)
- Discretization scheme: Euler-Maruyama on log-scale. Per step, the path multiplicatively updates by `exp((drift − volatility²/2)·dt + volatility·√dt · Z)` where `Z ~ N(0, 1)`. The `−volatility²/2` term is the Itô correction (MQ check).
- σ_T computed per path via PRIMITIVES.md §6 eq. (7) discretely: `sigma_t = (1/T) * sum_{i=0..n_steps} (path[i] - mean(path))**2`. Matches B1 plan's σ_T contract per MQ-FLAG-B1.1 disposition.
- audit_block deterministic from `(params canonical JSON, rng_seed, paths bytes)`.
- Hypothesis property tests:
  - Determinism (Pin Z1.2): same `(rng_seed, n_paths)` → bit-exact `audit_block`.
  - Lognormality: at large `n_steps` and `T=1`, `log(path[..., -1] / x_0)` is approximately normal with mean `(mu - sigma^2/2) * T` and variance `sigma^2 * T`. Use Hypothesis with a Normality goodness-of-fit check (Anderson-Darling) at N=1000.
  - Trivial-degenerate limit: at `params.sigma == 1e-8` (effectively 0), all paths collapse near `x_0` and `sigma_t_per_path` mean is `< 1e-6`. Tested on a coarser grid (`n_steps = 100`, `T = 1.0`) rather than the canonical pin (`n_steps = 5000`, `T = 12`) because eq. (7) sum-of-squared-deviations divided by `T` accumulates float64 rounding noise monotonically in grid density — at canonical density the empirical floor lands at ≈ `1.49e-6` (>1e-6) even when the analytic prediction `x_0² · σ²` is `1.6e-9`. See §16.3 (v0.2→v0.3 CORRECTIONS-α) for the disposition rationale and the per-grid measured floor.
- ruff + ty clean.

**Commit message:** `feat(stochastic_fx/generators): GBMPathGenerator`

---

### Task 3.2 — Author `OUPathGenerator`

**Files:**
- Modify: `simulations/stochastic_fx/generators.py` (append)
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add OU tests)

**Agent dispatch:** `Senior Developer` + `AI Engineer`.

**Acceptance:**
- `OUPathGenerator` frozen-dataclass holding the family's Parameters; callable surface mirrors `GBMPathGenerator` (deterministic RNG seed + n_paths in, PathEnsemble out).
- Discretization: EXACT transition (not Euler — OU admits a closed-form Gaussian transition). Per step, the new value equals `long-run-mean + (X_t − long-run-mean)·exp(−rate·dt) + volatility·√((1 − exp(−2·rate·dt))/(2·rate)) · Z`. This is the standard OU exact-conditional-Gaussian update.
- Hypothesis property tests:
  - Mean reversion: at long T and large theta, `mean(path[..., -1])` is close to `mu_bar`.
  - Determinism (Pin Z1.2).
  - Trivial-degenerate limit at `params.theta = 1e8` (effectively instant mean reversion): paths collapse near `mu_bar` and `sigma_t_per_path` mean is `< 1e-3`.
  - Trivial-degenerate limit at `params.sigma = 1e-8`: `sigma_t_per_path` mean `< 1e-6`.

**Commit message:** `feat(stochastic_fx/generators): OUPathGenerator`

---

### Task 3.3 — Author `JumpDiffusionPathGenerator`

**Files:**
- Modify: `simulations/stochastic_fx/generators.py` (append)
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add Merton tests)

**Agent dispatch:** `Senior Developer` + `AI Engineer`.

**Acceptance:**
- `JumpDiffusionPathGenerator` frozen-dataclass holding the family's Parameters; callable surface mirrors the other generators.
- Discretization: Euler-Maruyama on log-scale (per Task 3.1) augmented by compound-Poisson jumps. Per step: (i) sample the number of jumps from a Poisson distribution with mean `jump_intensity·dt`; (ii) sample that many jump sizes from a lognormal distribution with parameters `(jump_mean, jump_std)`; (iii) aggregate jumps multiplicatively into the diffusion step, so the new value equals the GBM diffusion update times the product of jump multipliers.
- Hypothesis property tests:
  - Determinism (Pin Z1.2).
  - Trivial-degenerate limit at `params.sigma = 1e-8 AND params.lambda_jump = 0`: paths collapse near `x_0`; `sigma_t_per_path` mean `< 1e-6`.
  - At `lambda_jump = 0`, JumpDiffusionPathGenerator output statistically matches GBMPathGenerator output (Kolmogorov-Smirnov agreement on terminal-spot distributions at the same N, same rng_seed).

**Commit message:** `feat(stochastic_fx/generators): JumpDiffusionPathGenerator`

---

## §9 Phase 4 — Variance proxy + Inversion verifier

### Task 4.1 — Author `variance_proxy.py` (Phase A algebraic inversion)

**Files:**
- Create: `simulations/stochastic_fx/variance_proxy.py`
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add variance-proxy tests)

**Agent dispatch:** `Senior Developer`.

**Acceptance:**
- A free function that re-applies PRIMITIVES.md §6 eq. (7) to the ensemble's paths and returns the per-path realised variance array. Verifies the σ_T values stored on the ensemble match the freshly-computed values within `NUMERICAL_IDENTITY_TOL = 1e-6` (reused from `simulations.saas_builder.cohort_4.types::NUMERICAL_IDENTITY_TOL`).
- A free function that implements PRIMITIVES.md §6 eq. (8) algebraically: given a realised variance σ_T and the FX mean x_bar, returns `sqrt(8 * σ_T / x_bar**2)`.
- A free function implementing Pin Z1.3a: for each path's σ_T_n, verifies `(eps_n)² == 8·σ_T_n / x_bar²` to float64 precision (algebraic substitution, family-agnostic). Returns the composite pass flag plus the maximum absolute residual across the N paths. PASS iff max residual ≤ `NUMERICAL_IDENTITY_TOL`.
- Unit test: at the canonical fixture (x_bar = 4000.0, σ_T = 20000.0), the inversion function returns exactly 0.1.
- Property test (Hypothesis): for any valid (σ_T > 0, x_bar > 0), the inversion result is finite and non-negative; at σ_T = 0, the result is exactly 0 (trivial-degenerate-limit per Pin Z1.3a).
- ruff + ty clean.

**Commit message:** `feat(stochastic_fx/variance_proxy): σ_T computation + Phase-A algebraic inversion`

---

### Task 4.2 — Author `InversionVerifier` combining Phase A/B/C

**Files:**
- Modify: `simulations/stochastic_fx/variance_proxy.py` (append `InversionVerifier`)
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add verifier tests)

**Agent dispatch:** `Senior Developer` + `AI Engineer` (paired for the moment-match and KS-test math).

**Acceptance:**
- `InversionVerifier` frozen-dataclass with two module-level `Final` constants pinned in `simulations/stochastic_fx/variance_proxy.py`: `MOMENT_REL_TOL = 0.05` (Pin Z1.3b tolerance) and `KS_PVALUE_FLOOR = 0.01` (Pin Z1.4 calibration per spec v0.3 §8). Downstream consumers (Tasks 5, 6) import via `from simulations.stochastic_fx.variance_proxy import MOMENT_REL_TOL, KS_PVALUE_FLOOR` — single source of truth (FLAG-RC-3 disposition). The callable surface accepts the Parameters, a PathEnsemble, and the FX mean x_bar; returns an InversionVerdict.
- Per-family dispatch on the ensemble's family identifier to select the right moment function from `moments.py` and the right reference distribution shape per spec v0.3 §4.2 (lognormal for GBM/Merton; gamma for OU).
- Phase A check: calls the Task 4.1 Phase-A free function to populate `phase_a_passes` and `phase_a_max_residual`.
- Phase B check (Pin Z1.3b, v0.5 mean-only gate per §16.5 disposition): compute empirical mean from `ensemble.sigma_t`; compute analytic `E[σ_T]` of the DISCRETE eq.(7) statistic at canonical grid via the per-family `*_discrete_sigma_t_moments` functions appended to `variance_proxy.py` (per plan §16.4 disposition b1); compute the relative error on the MEAN; PASS iff mean rel-err ≤ `MOMENT_REL_TOL`. **Variance rel-err is still COMPUTED and POPULATED on `InversionVerdict.phase_b_var_rel_err` for audit-trail observation but does NOT gate `phase_b_pass`.** Raises `MomentMatchFailedError` if MEAN rel-err exceeds the tolerance (HALT routing per Pin Z1.5). Full-distribution match (which jointly constrains variance, skew, kurtosis via empirical CDF) is preserved at Phase C below. v0.5 amendment rationale: at the Pin Z1.5 anti-fishing floor N=1000, the sample-variance estimator's intrinsic MC-noise SE is 8-30% per family — incompatible with `MOMENT_REL_TOL=0.05` regardless of analytic-Var correctness. See §16.5 + parent spec §11.6 for the full disposition record.
- Phase C check (Pin Z1.4, v0.6 per-family reference dispatch per §16.7):
  - **GBM, OU** (moment-matched parametric reference, NIT-MQ-1 method-of-moments construction — do NOT call `.fit()` against empirical data):
    - **GBM (lognormal):** given analytic `(E_an, Var_an)` from `gbm_discrete_sigma_t_moments(params)`, compute `s = sqrt(log(1 + Var_an/E_an**2))` and `scale = E_an / sqrt(1 + Var_an/E_an**2)`; construct `scipy.stats.lognorm(s=s, scale=scale)`. KS test: `scipy.stats.ks_1samp(ensemble.sigma_t, reference.cdf)`.
    - **OU (gamma):** given analytic `(E_an, Var_an)` from `ou_discrete_sigma_t_moments(params)`, compute `a = E_an**2 / Var_an` and `scale = Var_an / E_an`; construct `scipy.stats.gamma(a=a, scale=scale)`. KS test: `scipy.stats.ks_1samp(ensemble.sigma_t, reference.cdf)`.
  - **Merton (v0.6 amendment, empirical-CDF reference via high-N reference run):** sample a high-resolution reference ensemble via `JumpDiffusionPathGenerator(params=CANONICAL_MERTON)(rng_seed=N_REF_SEED, n_paths=N_REF)` where `N_REF: Final[int] = 100_000` and `N_REF_SEED: Final[int] = 20260513` are FROZEN module-level constants in `variance_proxy.py`. **Cache ONLY the `sigma_t` 1-D array** (`reference_sigma_t: np.ndarray` of shape `(N_REF,)` ≈ 800 KB), NOT the full `PathEnsemble` (which holds the `paths` 2-D matrix at `N_REF × (n_steps+1) × 8 bytes` ≈ 4 GB at canonical n_steps=5000 — would explode resident memory — per FLAG-RC-V0.5-1 disposition). The implementation pattern is a module-level `functools.cache`-decorated helper that returns only the `sigma_t` array, keyed on `(canonical_params_json_str, N_REF, N_REF_SEED)`. KS test: `scipy.stats.ks_2samp(ensemble.sigma_t, reference_sigma_t)`.
  - Populate `phase_c_ks_pvalue`. PASS iff `ks_pvalue ≥ KS_PVALUE_FLOOR = 0.01` (SINGLE-VALUED across all three families; no per-family relaxation). Raises `InversionTestFailedError` if p < `KS_PVALUE_FLOOR`.
  - **Anti-fishing invariants on Merton's high-N reference:** `N_REF` and `N_REF_SEED` are spec-pinned constants. The implementer MUST NOT vary them to make Merton pass. Changing either constitutes spec amendment via CORRECTIONS-α + scoped Wave-1 re-review.
- **Anti-fishing rule (Pin Z1.5 enforcement at construction time):** the InversionVerifier rejects calls where `ensemble.paths.shape[0] != 1000` (the N=1000 floor per spec v0.3 §8). The check happens INSIDE `__call__` BEFORE any phase runs; raises `MCBudgetExceededError` if violated. N=1000 is a frozen module-level constant, NOT a parameter to grow.
- `tex_anchor` populated with the relative path `notes/stochastic_fx_tex/sigma_t_moments_{family_id}.tex`.
- `audit_block` is sha256 of (ensemble.audit_block + canonical-parameters JSON + x_bar + MOMENT_REL_TOL + KS_PVALUE_FLOOR + N_REF + N_REF_SEED), deterministic across re-runs. (v0.6 FLAG-RC-V0.5-5 disposition: binds the Merton high-N reference-run constants to the audit trail so changing either invalidates the digest.) For GBM and OU runs N_REF/N_REF_SEED are still hashed in (they're module-level constants regardless of which family dispatches) — preserves single-recipe audit_block across families.

  `InversionVerdict.phase_c_n_paths` carries the TESTED ensemble's path count (N=1000 at the Pin Z1.5 floor), NOT N_REF (v0.6 FLAG-RC-V0.5-2 disposition). Rationale: the field's Task 1.3 docstring is "path-count used for the test sample"; N_REF is the reference, not the test. For Merton runs, the high-N reference's existence is recorded via the audit_block binding (above), not via `phase_c_n_paths`.
- Round-trip read-back test: same inputs → same InversionVerdict audit_block.
- Per-family unit tests at canonical pins: verify all three Phases PASS for GBM, OU, Merton.

**Commit message:** `feat(stochastic_fx/variance_proxy): InversionVerifier — Phase A+B+C combiner`

---

## §10 Phase 5 — IO Boundary tier (emit)

### Task 5 — Author `emit.py` with parquet + JSON + LaTeX + MD emitters

**Files:**
- Create: `simulations/stochastic_fx/emit.py`
- Modify: `simulations/stochastic_fx/__init__.py` (re-export)
- Modify: `simulations/tests/test_saas_stochastic_fx.py` (add emit round-trip tests)

**Agent dispatch:** `Senior Developer`.

**Acceptance:**
- Four IO-Boundary-tier classes, each with an `__init__(emit_dir)` and a callable surface (FLAG-RC-1 disposition: class signatures replaced with prose):
  - **PathEnsembleEmitter**: writes a parquet file at `simulations/stochastic_fx/data/path_ensemble_{family_id}.parquet` where `{family_id}` ∈ `{gbm, ou, merton}` (NIT family naming drift disposition: use `{family_id}` consistently, NOT `{family}`). Schema: one row per (path_index, step_index, x_t) triple; metadata holds the canonical parameters JSON + audit_block + rng_seed.
  - **InversionVerdictEmitter**: writes a JSON v1.0 schema file at `simulations/stochastic_fx/data/inversion_verdict_{family_id}.json`. Schema includes all InversionVerdict fields plus three tolerance constants imported from `simulations/stochastic_fx/variance_proxy.py` per FLAG-RC-3: `phase_a_tolerance = NUMERICAL_IDENTITY_TOL`, `phase_b_tolerance = MOMENT_REL_TOL`, `phase_c_tolerance = KS_PVALUE_FLOOR`. Round-trip read-back equality enforced (write → read → in-memory equality).
  - **TexFragmentEmitter**: writes under `notes/stochastic_fx_tex/` (NOT under data/; .tex fragments are committed). No-op if the fragment already exists — these are Task 2.1 artifacts; this class is for re-emit only.
  - **StochasticFxResultsEmitter**: writes `notes/STOCHASTIC_FX_RESULTS.md` (parallel to STAGE_2_RESULTS.md) given a tuple of InversionVerdicts. R-tagged sections per family + cross-family summary table. Format mirrors STAGE_2_RESULTS.md exactly.
- Unit tests:
  - Round-trip on each emitter (write + read + field-equality).
  - File-existence assertions per emit.
  - `simulations/stochastic_fx/data/` files are NOT git-tracked (Task 0 verification — `git check-ignore` returns the path).

**Commit message:** `feat(stochastic_fx/emit): IO Boundary tier — parquet + JSON + tex + MD emitters`

---

## §11 Phase 6 — End-to-end verification

### Task 6 — Run end-to-end per family + emit `STOCHASTIC_FX_RESULTS.md`

**Files:**
- Create: `scratch/2026-05-11-stochastic-fx-execution/moment_verification_log.md`
- Create: `scratch/2026-05-11-stochastic-fx-execution/ks_test_log.md`
- Create: `notes/STOCHASTIC_FX_RESULTS.md` (via Task 5's emitter)

**Agent dispatch:** `Senior Developer` + `Reality Checker` (inline numerical cross-check per cohort_4 pattern).

**Acceptance:**
- A small ad-hoc driver script (NOT committed; run via `.venv/bin/python -c "..."` or a tempfile) for each family:
  1. Construct the canonical Parameters frozen-dc (Task 1.2 CANONICAL_*).
  2. Instantiate the family's PathGenerator (Task 3.x).
  3. Sample `n_paths = 1000` with a fixed `rng_seed = 42`.
  4. Run the `InversionVerifier` against the ensemble at `x_bar = parameters.x_0` (= 4000).
  5. Emit parquet, JSON, MD via the Phase-5 emitters.
- Per family the `InversionVerdict.passes == True`:
  - Phase A residual ≤ NUMERICAL_IDENTITY_TOL (1e-6).
  - Phase B mean relative error ≤ MOMENT_REL_TOL (0.05). [v0.5 §16.5 mean-only gate per user disposition Option B 2026-05-13 — variance rel-err is still emitted to `InversionVerdict.phase_b_var_rel_err` for audit-trail observation but does NOT gate `phase_b_pass`. Full-distribution match preserved at Phase C below.]
  - Phase C KS p-value ≥ KS_PVALUE_FLOOR (0.01).
- `notes/STOCHASTIC_FX_RESULTS.md` emitted with R-tagged sections per family + cross-family summary table.
- `moment_verification_log.md` records each family's analytic-vs-empirical moments + relative errors.
- `ks_test_log.md` records each family's reference-fit parameters + KS p-value.
- HALT routing: if any Phase fails for any family, do NOT silent-retune. Report the failure, route per Pin Z1.5 (CORRECTIONS-α + scoped Wave-1 re-review on the plan, NOT silent fix).
- Reality-Checker cross-check: re-run the same driver from scratch with `rng_seed = 42`; confirm bit-exact identical `InversionVerdict.audit_block` per family (Pin Z1.2 determinism).

**Commit message:** outcome-neutral, decided at run-time per FLAG-RC-4 disposition. If all three families PASS: `eval(stochastic_fx): end-to-end run at canonical pins — emit verdicts (3 families)`. If any family FAILS: `eval(stochastic_fx): end-to-end run at canonical pins — HALT per Pin Z1.5 (family X failed phase Y)`. NEVER pre-pin "all PASS" in the commit message — that would be the anti-fishing pattern of asserting the outcome before the run.

---

## §12 Phase 7 — Pin Z1.6 strip preservation verification

### Task 7 — Verify cohort_5_strip audit_block unchanged

**Files:**
- Create: `scratch/2026-05-11-stochastic-fx-execution/pin_z16_strip_preservation_log.md`

**Agent dispatch:** N/A — orchestrator-only operation (single hex-grep shell command + log entry per `memory/feedback_specialized_agents_per_task.md` shell-ops exception).

**Acceptance:**
- Bash command: `grep -F '94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329' simulations/saas_builder/data/IronCondor_strip.json` returns the audit_block line. Same command run before Task 1.1 (at the plan's start commit) AND after Task 6 (at the plan's last commit). Both runs MUST return the same line.
- `pin_z16_strip_preservation_log.md` records both grep results + the two commit shas.
- HALT routing: if the audit_block has changed during plan execution, HALT and route to cohort_5_strip review (the strip emit is anti-fishing-coupled to this plan's correctness; any drift is a master-spec-level concern).

**Commit message:** `verify(stochastic_fx): Pin Z1.6 cohort_5_strip audit_block preservation`

---

## §13 Pin coverage (per spec v0.3 §5)

| Pin | This plan's coverage |
|---|---|
| Z1.1 — SDE parameters pre-pinned ex-ante | Task 1.2 canonical pins frozen at this commit; Pin enforced by anti-fishing routing in Task 6. |
| Z1.2 — Path-ensemble determinism | Tasks 3.1 / 3.2 / 3.3 each have a Hypothesis test pinning bit-exact audit_block for the same `(rng_seed, n_paths)`. |
| Z1.3a — Algebraic inversion (family-agnostic) | Task 4.1 free function + property test. |
| Z1.3b — Moment match per family | Task 4.2 InversionVerifier Phase B + Task 6 end-to-end. |
| Z1.4 — KS goodness-of-fit per family | Task 4.2 InversionVerifier Phase C + Task 6 end-to-end. |
| Z1.5 — Anti-fishing routing | HALT triggers per task; explicit "N=1000 floor, not parameter to grow" enforcement in Task 4.2 InversionVerifier. |
| Z1.6 — Strip preservation | Task 7. |

## §14 HALT routing

| Trigger | Route |
|---|---|
| Task 1.x ruff / ty / Hypothesis-test fail | HALT — Senior Developer iterates; no relaxation of property tests. |
| Task 2.1 hand-derived moment numerical sanity fails | HALT — re-verify the spec v0.3 §4.2 formulas against literature; CORRECTIONS-α to the spec if the formula was wrong. |
| Task 3.x SDE generator's trivial-degenerate-limit test fails | HALT — discretization defect; investigate (e.g., dt too coarse). NEVER raise sigma to pass. |
| Task 4.1 algebraic-inversion property test fails | HALT — float64 numerical defect; investigate `apply_inversion`. |
| Task 4.2 InversionVerifier raises for canonical fixture | HALT — CORRECTIONS-α + scoped Wave-1 re-review per spec v0.3 Pin Z1.5. |
| Task 5 emit round-trip read-back equality fails on ANY emitter | HALT — IO Boundary tier defect; investigate parquet/JSON schema or LaTeX-fragment encoding. NIT-RC-Task5 disposition. |
| Task 6 any family's Phase B / Phase C fails | HALT per Pin Z1.5. NEVER increase N. NEVER retune SDE parameters silently. |
| Task 7 strip audit_block changed | HALT — route to cohort_5_strip review (master-spec-level coupling concern). |
| Wave-1 or Wave-2 RC+MQ on this plan returns BLOCK | HALT per master-spec §6.1; CORRECTIONS-α in §16. |

## §15 Artifacts emitted

| Artifact | Phase | Schema | Lineage parent |
|---|---|---|---|
| `simulations/stochastic_fx/{__init__,_errors,types,moments,generators,variance_proxy,emit}.py` | 1–5 | code | (new package) |
| `notes/stochastic_fx_tex/{eps_inversion,sigma_t_moments_{family}}.tex` | 2 | LaTeX fragments | sympy.latex() rendering of hand-derived moments |
| `simulations/stochastic_fx/data/path_ensemble_{family}.parquet` | 6 | new v1.0 | sha over (params, rng_seed, paths bytes); gitignored |
| `simulations/stochastic_fx/data/inversion_verdict_{family}.json` | 6 | new v1.0 | sha over (ensemble audit, params, tolerances); gitignored |
| `notes/STOCHASTIC_FX_RESULTS.md` | 6 | parallel to STAGE_2_RESULTS.md | composed of per-family verdicts |
| `scratch/2026-05-11-stochastic-fx-execution/{moment_verification,ks_test,pin_z16_strip_preservation}_log.md` | 6–7 | markdown | run logs |

## §16 CORRECTIONS-α (patch log)

### §16.1 v0.1 → v0.2 (Wave-1 RC+MQ disposition)

**Wave-1 review verdicts:**
- RC: ACCEPT_WITH_FLAGS (4 material flags + 1 NIT + minor naming consistency drift).
- MQ: ACCEPT_WITH_FLAGS (4 flags — math content faithful to spec v0.3; flags are surface-level surface-area improvements).

Verdict files:
- `scratch/2026-05-11-stochastic-fx-plan-review/rc-verdict.md`
- `scratch/2026-05-11-stochastic-fx-plan-review/mq-verdict.md`

Both reviewers explicitly stated no full Wave-1 re-dispatch required; orchestrator-side v0.2 patch suffices.

| Finding | Severity | Disposition | Location |
|---|---|---|---|
| **FLAG-RC-1** | Material | Inline-backtick code signatures pervaded acceptance bullets (`__call__(...) -> ...`, `Name(field: type, ...)`, etc.) — violated `memory/feedback_no_code_in_specs_or_plans.md` per the parent spec's RC-FLAG-1-v2 disposition. v0.2 prose-ifies signatures and replaces constant-construction lines with per-family Parameters tables (Tasks 1.2, 1.3, 2.1, 3.1, 3.2, 3.3, 4.1, 4.2, 5). Math notation and JSON-schema illustrations remain admissible. | Tasks 1.2 / 1.3 / 2.1 / 3.1 / 3.2 / 3.3 / 4.1 / 4.2 / 5 |
| **FLAG-RC-3** | Material | `MOMENT_REL_TOL` and `KS_PVALUE_FLOOR` import path pinned: defined as module-level `Final` in `simulations/stochastic_fx/variance_proxy.py`; downstream consumers import via `from simulations.stochastic_fx.variance_proxy import ...` (single source of truth). | Task 4.2 acceptance + Task 5 emit |
| **FLAG-RC-4** | Material (anti-fishing) | Task 6 commit message reframed as outcome-neutral. Two run-time-decided variants: (i) PASS case emits `eval(stochastic_fx): emit verdicts (3 families)`; (ii) FAIL case emits `eval(stochastic_fx): HALT per Pin Z1.5 (family X failed phase Y)`. Pre-pinning "all PASS" in the commit message was the anti-fishing pattern. | Task 6 |
| **FLAG-RC-2** | NIT | Header text clarifies that the cohort-N convention tracks the TASK (one task per commit), NOT per-step `- [ ]` checkboxes. Subagent-driven-development's TaskCreate/TaskUpdate is the canonical tracking surface. Matches A1/A2/B1 plan precedents. | Header |
| **NIT — `{family_id}` vs `{family}` drift** | Cosmetic | All filename templates and dispatch references now use `{family_id}` consistently with the PathEnsemble Value type's closed alphabet `{gbm, ou, merton}`. | Tasks 2.1 / 5 |
| **NIT — Task 5 missing HALT row** | Cosmetic | §14 HALT routing now has a Task 5 row: "Task 5 emit round-trip read-back equality fails → HALT IO Boundary tier defect". | §14 |
| **FLAG-MQ-1** | Medium | Merton `E[σ_T]` Python form now literalised in Task 2.1 acceptance table — full expression with all terms, mirroring GBM/OU rows (prevents the most-error-prone family from being implementer-discretion). | Task 2.1 per-family moment table |
| **FLAG-MQ-2** | Medium | `moments.py` module docstring requirement explicit: documents the `(X̄/Ȳ)² → params.x_0**2` substitution at canonical pin (x_0 = X̄/Ȳ = 4000); `.tex` fragments retain symbolic `(X̄/Ȳ)²` form. Task 2.1 acceptance now states this requirement separately. | Task 2.1 acceptance |
| **FLAG-MQ-3** | Low | `Var[σ_T]` Python forms for GBM and Merton added to Task 2.1 per-family moment table (alongside the previously-present OU form). Removes the silent-fishing surface. | Task 2.1 per-family moment table |
| **NIT-MQ-1** | Low | Task 4.2 Phase C construction changed from `scipy.stats.lognorm.fit(...)` / `gamma.fit(...)` (which would re-introduce the empirical-fit tautology MQ caught at spec v0.1) to DIRECT method-of-moments construction: `lognorm(s=…, scale=…)` from analytic E and Var; `gamma(a=…, scale=…)` similarly. Construction formulas spelled out in Task 4.2 acceptance. | Task 4.2 Phase C |

### §16.2 Wave-2 (post-execution) review reserve

Wave-2 RC+MQ on this plan's exit deliverables (each family's parquet + JSON + STOCHASTIC_FX_RESULTS.md emit) lands at §16.8 once execution completes (renumbered from §16.6 in v0.5 to make room for §16.7 v0.5 → v0.6 Phase C dispatch disposition).

### §16.3 v0.2 → v0.3 (Task 3.1 mid-execution CORRECTIONS-α — grid-density precision floor)

**Trigger:** Task 3.1 Wave-1 RC ACCEPT_WITH_FLAGS (RC-FLAG-1 Medium / procedural). Task 3.1 implementer disposed the "paths collapse" trivial-degenerate test (`sigma=1e-8`, threshold `< 1e-6`) by reducing test-side `n_steps` from canonical 5000 to 100 — silent param adjustment of the test rather than a documented threshold/grid relaxation. MQ independently confirmed (i) the underlying math is correct (Itô anchor 0.152·SE; eq. (7) literal `Σ(X−mean)²/T`; bit-exact determinism); (ii) the grid-density issue is REAL not fabricated (monotone `mean(sigma_t)`: 2.7e-8 @ n=100, 2.96e-7 @ n=1000, 1.49e-6 @ n=5000). The analytic prediction at `sigma=1e-8` is `x_0² · σ²` ≈ 1.6e-9; the canonical-grid empirical floor of 1.49e-6 is dominated by float64 cumulative-sum rounding noise, not by the SDE physics.

**Precedent:** the A1 plan v0.3→v0.4 precision-floor disposition (commit `74c333c` / scratch `2026-05-11-a1-panoptic-survey/`) that relaxed `1e-6` to `5e-5` for the published 5-sig-fig precision floor in the strategy-verdict baseline. Memory `memory/project_precision_floor_5e5_lesson.md` codifies the disposition pattern: when a test threshold is tighter than the precision the test-bed can deliver, relax to match the floor and document the analytic vs measured gap; do NOT silently adjust auxiliary parameters.

**Disposition:** explicit. The trivial-degenerate test exercises the GEOMETRIC fact "paths collapse to x_0 at zero vol", NOT the production-grid behaviour of σ_T. Either of two anchorings is mathematically valid (and both are inferior-test-of-nothing iff the SDE drift is correctly Itô-corrected, which is independently anchored by `test_ito_correction_anchor`):
- **(a) coarse-grid + tight threshold** (implementer's choice; n_steps=100, threshold <1e-6) — exposes the geometry cleanly without float-accumulation noise; faster test.
- **(b) canonical-grid + relaxed threshold** (would be `n_steps=5000`, threshold ≤ 2e-6) — matches production grid; mirrors A1 disposition more literally but adds wall-time to the test and weakens the threshold by ≈2x.

v0.3 ratifies option (a) as the project-canonical choice for this test class — the test docstring at `simulations/tests/test_saas_stochastic_fx.py::TestGBMPathGenerator::test_trivial_degenerate_limit_sigma_to_zero` documents the n_steps choice, and Task 3.1 acceptance bullet 3 (above) now cites this §16.3. §14 HALT routing's existing "NEVER raise sigma to pass" rule is preserved verbatim; the n_steps-adjustment route is explicitly admissible only with a docstring rationale + a §16-tracked correction (this entry).

**Forward implication for Tasks 3.2 / 3.3.** Both OUPathGenerator and JumpDiffusionPathGenerator inherit the trivial-degenerate test class shape. Their analogous tests SHOULD adopt option (a) verbatim (coarse-grid + tight threshold) for parallelism and to avoid re-litigating the disposition per family.

**RC-FLAG-2 (Low) disposition.** `generators.py` module docstring previously claimed `simulations.stochastic_fx._errors` was imported by this module. It is not (validation is delegated to `PathEnsemble.__post_init__`). Docstring corrected.

**RC-NIT-1 (Trivial) disposition.** The defensive `paths[:, 0] = params.x_0` reassignment is correctness-redundant under IEEE 754 (`exp(0) == 1.0` exactly) but readability-positive. Kept as-is.

**MQ-FLAG-2 (Low) disposition.** Slice-equivalence convention (`gen(seed=42, n_paths=1000).paths[:500]` is NOT equal to `gen(seed=42, n_paths=500).paths` because the RNG state advances differently) deferred to a Task 5 emit.py docstring; not load-bearing for Task 3.1.

### §16.4 v0.3 → v0.4 (Task 3.3 mid-execution CORRECTIONS-α — analytic-vs-empirical σ_T statistic mismatch)

**Trigger:** Task 3.3 implementer self-flagged BLOCK-PROBE-1 during the inline math probe for `JumpDiffusionPathGenerator`. The probe compared `merton_sigma_t_moments(CANONICAL_MERTON)[0]` (analytic E[σ_T] = 1.99e+06) to `mean(JumpDiffusionPathGenerator(CANONICAL_MERTON)(rng_seed=7, n_paths=5000).sigma_t)` (empirical = 1.58e+08) and found a ~137× rel_err. Implementer correctly identified that the SAME ~137× gap exists at the GBM canonical pin (8.03e+04 analytic vs 1.10e+07 empirical) — confirming the discrepancy is a STRUCTURAL mismatch between two valid-but-different σ_T statistics, NOT a JD-aggregation defect.

**Root cause analysis.** The two quantities measure different objects:

1. **Task 2.1 `moments.py` analytic E[σ_T]** is the LEADING-ORDER continuous-time integrated-variance form (per Hull §15 / Andersen-Piterbarg §2.7): `E[(1/T)·∫_0^T (X_t − E[X̄])² dt]` ≈ `x_0² · ((exp(σ²T) − 1)/(σ²T) − 1)` for GBM, with sample-mean-centering neglected. Units: `[X]²`.

2. **Task 3.x generator emit `sigma_t`** is the DISCRETE spec v0.3 §6 eq. (7) statistic: `(1/T) · Σ_{j=0}^{n_steps} (X_j − X̄_path)²`, a Riemann sum that scales as `O(n_steps)` relative to the continuous integral. At canonical `n_steps = 5000, T = 12` the discrete-to-continuous scale factor is `n_steps/T ≈ 417`; combined with the `Var[X̄_path]` centering correction and float64 cumulative-sum noise, the observed ~137× ratio is consistent with this purely-definitional gap.

Both are valid σ_T proxies for the wage-volatility hedge analytic but they do NOT share population moments. The original spec v0.3 §8 Pin Z1.3b (moment match) implicitly assumed they would; the implementer's probe surfaced the assumption defect at the first cross-tier test.

**User disposition (Option 1, 2026-05-13):** Ratify the implementer's omission of the cross-tier moments cross-check in Task 3.3's test class. Route moment-matching to Task 4.2's `InversionVerifier` Phase B, which is the canonical home for analytic-vs-empirical moment reconciliation in this plan.

**Implementer disposition recorded.** `TestJumpDiffusionPathGenerator` class docstring documents the omission rationale; the probe-stated 10% rel-err target in the Task 3.3 implementer brief is RETIRED (had been a stretch goal; conflicts with the statistic-definitional gap). The plan §8 Task 3.3 acceptance block (lines 283-289) did NOT list a moment cross-check — only determinism + λ=0 KS collapse + trivial-degenerate — so the implementer's omission is fully spec-conformant.

**Forward implication for Task 4.2 Phase B (InversionVerifier — moment-match).** Phase B must either:
- **(b1)** Derive the analytic E[σ_T] / Var[σ_T] of the DISCRETE eq. (7) statistic at the canonical grid (depends on `n_steps`, `T`) and compare to empirical moments. Closed-form expressions exist via the auto-covariance structure of the SDE family (e.g., for GBM the discrete-grid integrated variance is `x_0² · Σ_j (exp(σ²·t_j) − 1) / T − x_0² · n_steps · Var[X̄_path] / T`). Implementer choice on whether to derive symbolically (sympy) or numerically (Monte Carlo at high-N reference).
- **(b2)** Convert the discrete empirical to a continuous-form estimator by multiplying by the known scale factor `T / n_steps` (i.e., emit `empirical_continuous = sigma_t · T / (n_steps + 1)`) and compare against the existing moments.py analytic. Simpler but introduces a non-trivial bias for small T (mean-centering correction).
- **(b3)** Sidestep moment-matching entirely and route Phase B to a KS-test (a la Phase C) on the cross-section of `sigma_t` at the canonical grid against a Monte Carlo reference distribution at much higher N.

v0.4 RECOMMENDS option (b1) — derive the analytic of the discrete statistic — as the cleanest match to spec Pin Z1.3b. Pin Z1.3b's tolerance (`MOMENT_REL_TOL = 0.05`, per Task 4.2 acceptance) is retained but applies to the discrete-form comparison, NOT to the continuous-form moments.py output. Task 4.2 acceptance is updated to require an explicit discrete-statistic derivation OR a documented bias-correction step; pinning b1 vs b2 is left to the Task 4.2 implementer's analysis report.

**Tasks 2.1 outputs (moments.py + `.tex` fragments + STOCHASTIC_FX_RESULTS.md template) are UNCHANGED.** They remain the canonical continuous-time analytic forms cited in `notes/stochastic_fx_tex/`. The discrete-statistic analytic is a Task 4.2 derivation, not a moments.py revision. This preserves the Task 2.1 audit_blocks and avoids Wave-2 re-review on Task 2.1.

**Pin coverage update:** Pin Z1.3b's scope is clarified to "moment match between analytic-of-discrete-statistic and empirical-of-emitted-sigma_t". Task 4.2 acceptance to embed this clarification at execution time.

**No Wave-1 re-dispatch required** for Task 3.3 — implementer made a correct judgment call surfacing the structural mismatch; user disposition routes it to Task 4.2. Tasks 3.1 and 3.2 are unaffected (they ship the same eq. (7) statistic; their moment cross-checks were not in their acceptance blocks). Task 4.2 plan section §9 Task 4.2 is the canonical site for the discrete-analytic derivation; no edit there at v0.4 — the Task 4.2 implementer brief at dispatch time will cite this §16.4 and select (b1/b2/b3) based on analysis.

**Verdict files (Task 3.3 Wave-1 still pending dispatch per user halt — not yet scheduled):**
- `scratch/2026-05-11-stochastic-fx-task-3.3-review/rc-verdict.md` (NOT YET WRITTEN)
- `scratch/2026-05-11-stochastic-fx-task-3.3-review/mq-verdict.md` (NOT YET WRITTEN)

When Wave-1 is resumed, both reviewers must read this §16.4 first; the moments cross-check test omission is RATIFIED, not in-scope.

### §16.5 v0.4 → v0.5 (Task 4.2 mid-execution CORRECTIONS-α — Pin Z1.3b mean-only gate)

**Trigger.** Task 4.2 implementer (AI Engineer) selected disposition (b1) per §16.4 — hand-derive the analytic E[σ_T] and Var[σ_T] of the DISCRETE eq.(7) statistic at canonical grid, compare to empirical at N=1000. The MEAN derivation succeeded across all three families:

| Family | analytic E[σ_T] | empirical mean (N=1000, seed=42) | rel-err |
|---|---|---|---|
| GBM | 1.1171e+07 | 1.1297e+07 | **1.12%** |
| OU | 1.3544e+07 | 1.3566e+07 | **0.17%** |
| Merton | 1.6370e+08 | 1.6485e+08 | **0.70%** |

All three are well within `MOMENT_REL_TOL = 0.05` — the mean-match gate is achievable.

**The variance gate is NOT achievable at N=1000.** The implementer ran a Monte-Carlo-noise budget probe (100 independent seeds per family, ensemble variance distribution):

| Family | median rel-err on Var | p90 | max | fraction within ±5% |
|---|---|---|---|---|
| GBM | 11.0% | 22.1% | 51.3% | **28%** |
| OU | 5.2% | 11.2% | 18.3% | **46%** |
| Merton | 18.4% | 53.5% | 95.5% | **12%** |

Even with a HYPOTHETICALLY PERFECT analytic Var, only 12-46% of seeds at N=1000 would pass `MOMENT_REL_TOL=0.05`. The variance estimator's standard error at N is intrinsically `√((κ_eff − 1)/(N−1))` where `κ_eff` is the 4th-cumulant factor (≈ 4-15 per family) — always > 5% at N=1000. **Pin Z1.3b's 5%-on-Var-at-N=1000 was mathematically incompatible with the Pin Z1.5 anti-fishing N-floor.**

The implementer correctly HALTED before committing any code — exactly the §16-anticipated BLOCK scenario. No code modifications were made under the v0.4 acceptance criteria.

**User disposition (Option B, 2026-05-13):** drop variance from the Pin Z1.3b gate. Phase B becomes MEAN-ONLY. Phase C's KS test against the moment-matched reference distribution (constructed from analytic E AND analytic Var via the NIT-MQ-1 method-of-moments construction) preserves the full-distribution constraint that variance-match would have separately provided.

**Why B over A (per-family Var tolerance calibrated to MC budget):**
1. KS at Phase C jointly constrains mean + var + skew + kurtosis via the empirical CDF — a separate variance gate is structurally redundant.
2. Single tolerance `MOMENT_REL_TOL = 0.05` preserved across families — no per-family tuning surface (would look like fishing even when calibrated).
3. Smaller spec diff (one-line removal of "and var" vs three new calibrated thresholds).

**Why NOT D (Phase B = second KS test):** retaining mean-match anchors Phase B to literature-derived analytic moments (Hull / Karatzas-Shreve / Andersen-Piterbarg) rather than dissolving it into a Phase-C duplicate. The b1 hand-derived E[σ_T] formulas are mathematically nontrivial (especially Merton with `μ_j = x_0 · φ₁^j` jump-induced drift) and provide an independent SDE-discretization fidelity check.

**Implementer artefacts preserved.** Hand-derived discrete-moment formulas + MC-noise probe at `scratch/2026-05-13-task-4.2-discrete-moments/derivation.py` (NEW, uncommitted at the time of this disposition — implementer will commit alongside Task 4.2 implementation under the amended acceptance). Three per-family E[σ_T] derivations cited in parent spec §11.6.

**Forward implication for Task 4.2 acceptance** (this plan §9 Task 4.2 bullet, edited in-line):
- Phase B uses MEAN ONLY against the per-family discrete-statistic analytic E[σ_T].
- `phase_b_var_rel_err` is STILL computed and emitted to `InversionVerdict.phase_b_var_rel_err` as audit-trail observation — does NOT gate `phase_b_pass`.
- The implementer's b1 analytic Var derivation is NOT shipped in v0.5 (would have been the Phase B Var comparator under the v0.4 gate; under v0.5 it's superseded by Phase C's full-shape KS).

**Wave-1 re-review:** per master-spec §6.4, BOTH RC and MQ re-dispatch on the spec v0.4 + plan v0.5 amendment. NARROW scope — only Pin Z1.3b row + §4.1 Phase B bullet + §11.6/§16.5 (this section). Verdicts land at `scratch/2026-05-11-stochastic-fx-spec-review/wave-1-v0.4/`.

When Task 4.2 implementation resumes under the amended acceptance, the implementer brief MUST cite §16.5 first; the v0.4 variance gate is RETIRED, mean-only Phase B is the v0.5 contract.

### §16.6 v0.5 Wave-1 re-review (landed 2026-05-13)

Per master-spec §6.4, BOTH RC and MQ re-dispatched on the v0.4 → v0.5 amendment. Both ACCEPT_WITH_FLAGS — all flags disposed orchestrator-side at commit `fabffcf` (RC-FLAG-A1 §11.3→§11.6 cross-refs, RC-FLAG-A2 Task 6 var-gate residual) and `fc0d21e` (FLAG-MQ-V0.4-3 κ_eff range widen to 4-35). Both reviewers independently re-derived the b1 analytic E[σ_T] formulas + re-ran the MC-noise probe — both bit-exact to §11.6. Twice-ratified.

Verdict files:
- `scratch/2026-05-11-stochastic-fx-spec-review/wave-1-v0.4/rc-verdict.md` (ACCEPT_WITH_FLAGS — 2 flags disposed)
- `scratch/2026-05-11-stochastic-fx-spec-review/wave-1-v0.4/mq-verdict.md` (ACCEPT_WITH_FLAGS — 3 flags disposed)

### §16.7 v0.5 → v0.6 (Task 4.2 mid-execution CORRECTIONS-α — Pin Z1.4 per-family Phase C reference dispatch)

**Trigger.** Task 4.2 implementer resumed under the v0.5 amended Phase B mean-only acceptance. Mean-only Phase B WORKED CORRECTLY for all three families (mean rel-err 1.12% GBM / 0.17% OU / 0.70% Merton, all below `MOMENT_REL_TOL = 0.05`; matches §16.5 expected). Phase A passed at machine epsilon. **Phase C catastrophically rejected Merton** with KS p = 3.41e-21 against the v0.5 moment-matched lognormal reference (vs 0.01 floor). 20-seed pass rate per family at canonical pin:

| Family | KS p at seed=42 | 20-seed pass rate |
|---|---|---|
| GBM | 0.1229 | 12/20 |
| OU | 0.3033 | 18/20 |
| Merton | 3.41e-21 | **0/20** |

The implementer correctly HALTED before committing — per §6 HALT routing for Pin Z1.4 failures.

**Root cause.** The v0.4/v0.5 amendment rationale ("Phase C's KS test against the moment-matched reference distribution preserves the full-distribution constraint that variance-match would have separately provided") was correct for GBM/OU (log-multiplicative ↔ lognormal; Gaussian-quadratic ↔ gamma — both decent fits) but **wrong for Merton**, whose σ_T distribution is a Poisson-mixture-of-lognormals with empirical skew=10.4, excess kurtosis=174 at canonical pin (λ=1, σ_J=0.10). A 2-parameter lognormal cannot match heavy-tail mixture geometry by shape, only by location+scale. The shape mismatch is **structural, not a moment-matching deficiency** (even substituting empirical Var still yields KS p=6.9e-9; only `.fit()`-to-sample, the NIT-MQ-1 forbidden tautology, reaches p=0.42).

**User disposition (empirical-CDF reference via high-N, 2026-05-13):** per-family dispatch on Phase C reference SHAPE (NOT on threshold):
- **GBM**: retain moment-matched lognormal reference (NIT-MQ-1 method-of-moments). KS-1-samp. Empirically PASSES.
- **OU**: retain moment-matched gamma reference (NIT-MQ-1 method-of-moments). KS-1-samp. Empirically PASSES.
- **Merton**: empirical-CDF reference via high-N reference run. Pinned constants `N_REF: Final[int] = 100_000` and `N_REF_SEED: Final[int] = 20260513` in `variance_proxy.py`. KS-2-samp against high-N sample's `σ_T`.

Single `KS_PVALUE_FLOOR = 0.01` across all three families — no per-family threshold relaxation.

**Anti-fishing rigor preserved.** See spec §11.7 for the 5-point checklist. Key points: (1) single threshold, (2) `N_REF_SEED` pinned constant not implementer-tunable, (3) `N_REF` pinned constant, (4) no `.fit()` against tested sample, (5) interpretation unchanged (KS p < 0.01 still means "tested sample is statistically distinguishable from reference").

**Forward implication for Task 4.2 (this plan §9 Task 4.2 Phase C bullet, edited in-line at v0.6):**
- Reference distribution selection dispatches on `ensemble.family_id`.
- For Merton, sample the high-N reference via the same `JumpDiffusionPathGenerator` (NOT a different SDE) — anchors Phase C to the SDE itself.
- Cache the high-N reference via `functools.cache` keyed on `(params canonical_json, N_REF, N_REF_SEED)` to avoid re-sampling on every `__call__`.
- Both `KS_PVALUE_FLOOR` and the `N_REF`/`N_REF_SEED` constants are module-level `Final` (single source of truth per FLAG-RC-3 precedent).

**Wave-1 re-review.** Per master-spec §6.4, BOTH RC and MQ re-dispatch on this v0.5 → v0.6 amendment. NARROW scope — Pin Z1.4 row + §4.1 Phase C bullet + §11.7 + §16.7 (this section). Verdicts land at `scratch/2026-05-11-stochastic-fx-spec-review/wave-1-v0.5/`.

When Task 4.2 implementation resumes under v0.6, the implementer brief MUST cite §16.7 first; the v0.5 lognormal-Merton reference is RETIRED.

**Wave-1 re-review verdicts:** to land at `scratch/2026-05-11-stochastic-fx-spec-review/wave-1-v0.5/` (NOT yet written at the time of this commit; re-dispatch IS REQUIRED per master-spec §6.4 BLOCK protocol for this Pin-amendment — orchestrator dispatches both reviewers in parallel before Task 4.2 implementation resumes). FLAG-RC-V0.5-4 disposition: prior copy-paste error (citing Task 3.1 review paths + a "no re-dispatch" sentence imported from §16.3's pattern) corrected; this §16.7 disposition genuinely requires fresh RC+MQ Wave-1 re-review on the Pin Z1.4 row + §4.1 Phase C bullet + §11.7 + §16.7.

## §17 References

- `docs/specs/2026-05-11-stochastic-fx-variant-design.md` v0.3 — parent spec (the §10 protocol for this plan's Wave-1 review).
- `notes/PRIMITIVES.md` §5 eq. (6), §6 eq. (7), (8), §15 open item 2.
- `notes/STAGE_2_RESULTS.md` — parallel structure for `notes/STOCHASTIC_FX_RESULTS.md`.
- `simulations/saas_builder/cohort_5_strip/` — strip artifact preserved per Pin Z1.6.
- `simulations/saas_builder/cohort_4/types.py::NUMERICAL_IDENTITY_TOL` — reused as the float64 floor for Pin Z1.3a.
- `simulations/saas_builder/cohort_4/io.py` — pattern for `pin_and_emit` + round-trip read-back equality, reused for InversionVerdictEmitter.
- `simulations/utils/{parquet_io, json_io, audit_block}.py` — IO Boundary tier patterns.
- `memory/feedback_no_code_in_specs_or_plans.md` — plan-as-orchestration convention.
- `memory/feedback_specialized_agents_per_task.md` — foreground-orchestrates-never-authors.
- `superpowers:writing-plans` — flow that produced this plan.
- `superpowers:subagent-driven-development` — recommended execution flow.

---

*End of stochastic-FX variant plan v0.1. Independent RC + MQ Wave-1 review dispatch by the orchestrator before any task execution.*
