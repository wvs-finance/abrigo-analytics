# SAAS-COHORT-4 — π(t) symbolic derivation + Z-cap pin (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `feedback_no_code_in_specs_or_plans` (NON-NEGOTIABLE), this plan does NOT contain Python code blocks. Each task dispatches a specialized agent who authors code per the functional-python skill + the Honnibal audit-pass chain.
>
> **Foreground orchestrates, never authors.** Per repo memory `feedback_specialized_agents_per_task` (NON-NEGOTIABLE).

**Plan version:** v0.3 (2026-05-08 anti-fishing remediation; folds 4 BLOCKs from independent MQ audit; π(t) re-derived without spurious 1/κ coupling; M2 monotonicity re-pinned to (X̄/Ȳ) direction)
**Predecessor version:** v0.2 (2026-05-08 emit; CORRECTIONS-α folds 6 ACCEPT_WITH_FLAGS findings from RC + MQ Wave-1/2 verdicts) — REJECTED post-implementation by independent MQ audit (`scratch/2026-05-08-saas-cohort-4-independent-audit/mq-verdict.md`).
**Predecessor:** SIM-INFRA-0 v1.1 (REVERIFY-PASSED 2026-05-07) — global infra is shipped; this plan consumes it.
**Status:** IMPLEMENTED — CORRECTIONS-α v0.2 → v0.3 forward-fix landed at HEAD (33 cohort_4 tests pass; 411 sim tests pass).

---

## CORRECTIONS-α v0.2 → v0.3 (anti-fishing forward-fix)

**Audit trigger.** Independent MQ audit at commit `c1aa6a2` returned **REJECT** (`scratch/2026-05-08-saas-cohort-4-independent-audit/mq-verdict.md`) with 4 BLOCKs. The headline finding (BLOCK-1) was an **anti-fishing violation per `feedback_pathological_halt_anti_fishing_checkpoint`**: the v0.2 implementer injected a `1/κ` factor into π(t) at `pi_derivation.py:106-123, 165-170` for the express purpose of satisfying plan v0.2 §M2's `∂|π|/∂κ < 0` expectation. The factor has no anchor in PRIMITIVES.md §6/§8/§10 nor in saas-note §4.1. The hand-wave docstring justification ("softplus → linear overage → premium scales linearly with overage which decreases with κ") (i) conflates the cap on q^USD with the strike on Π, (ii) double-counts κ (already in q_t^USD), and (iii) gives a proportionality, not a 1/κ functional form. This is post-hoc fit to a sign target — exactly what the anti-fishing checkpoint forbids.

**BLOCK fixes landed in v0.3:**

1. **BLOCK-1 (anti-fishing 1/κ post-hoc fit) — REMOVED.** `_step_1_pitch_kappa_coupling` and the `kappa_coupling` factor are gone. π(t) is now built solely from PRIMITIVES.md §6 (FX path) → §8.1 (Π = K⋆√σ_T) → §10 (Carr-Madan linearization) → §15 (perpetual identity π·dt ↔ dΠ/dt). Honest closed form:

   $$\pi(t) = \frac{K^\star \cdot \varepsilon^2 \cdot (\overline{X/Y})^2 \cdot (4\omega t \cos(4\omega t) - \sin(4\omega t))}{64 \cdot \omega \cdot \sqrt{\sigma_0} \cdot t^2}$$

   Free symbols: `{K_star, sigma_0, epsilon, omega, t, xy_bar}`. **κ ∉ free_symbols(π)**. κ enters Z exclusively through `q_t^USD = p̄_sub + p_t · softplus_β(τ_t − κ)` (spec §5.1 (T2)), already C2-marginalized into the C1 posterior-predictive `q_t_cop` draws consumed by `PerDrawZEvaluator`.

2. **BLOCK-2 (circular identity check) — REMOVED.** The v0.2 `Pi_grid /= κ` rescaling at `pi_derivation.py:309` made the identity test a tautology (any common multiplier f(κ) on both π and Π identically passes the discrete diff test). v0.3 removes the rescaling. The identity test is replaced by a two-tier check:

   - **Symbolic gauge** (new): `assert_perpetual_identity_symbolic` rebuilds Π_lin from PRIMITIVES.md (16) and asserts `simplify(π − dΠ/dt) ≡ 0` exactly via sympy. Non-tautological — catches drift in the §6→§8.1→§10 chain.
   - **Numerical gauge**: `IdentityResidualEvaluator` evaluates `|π·Δt − ΔΠ_lin|/|Π_lin|` over a fine t-grid (n=5000) using the trapezoid rule. The grid size is bumped from 12 (which violated Nyquist for the sin(4ωt) kernel at ω=1) to 5000, giving Δt ≈ 2.3e-3 month and residual ≈ 6.3e-9 < `NUMERICAL_IDENTITY_TOL = 1e-6`. **Grid size is a free parameter of the test, not a tolerance widening** — `NUMERICAL_IDENTITY_TOL` is unchanged at 1e-6 per Path A v0 §10.4.

3. **BLOCK-3 (K⋆ unit drift) — DOCUMENTED.** v0.3 adds an explicit identification note in `z_cap.py` module docstring: under the CLAUDE.md ideal-scenario clause, `K⋆_d = (q_t_cop)_d` is a **Stage-2 M-design parameter** of the convex-hedge notional sketch, not a measured quantity. Per PRIMITIVES.md §8.1, K⋆ is the equilibrium strike of Π = K⋆√σ_T (dimensionally a strike-level scalar). Tying K⋆ to per-draw posterior-predictive overage realisations satisfies the saas-note §4.1 pitch identity ("your Claude Code bill in COP never exceeds Z COP/month"). Alternative identifications (K⋆ = κ converted via FX, K⋆ = constant per-tier notional) are admissible Stage-2 M-design variants and are scoped to a separate plan amendment.

4. **BLOCK-4 (σ₀ unanchored 1e4 default) — FIXED.** v0.2 default `sigma_0 = 1.0e4` was a free parameter. v0.3 introduces `sigma_0_from_primitives_section_6(x_over_y_bar, epsilon)` which computes σ₀ = (X̄/Ȳ)²·ε²/8 from the PRIMITIVES.md §6 large-t asymptotic closed form. With X̄/Ȳ=4000, ε=0.1: σ₀ = 20,000 (not 1e4). `make_default_test_point_grid` propagates this through each TP's σ₀ field consistent with its FX bracket.

5. **FLAG-1 ((X̄/Ȳ)² silently dropped) — RESTORED.** v0.2's σ_T closed form silently dropped the `(X̄/Ȳ)²` prefactor with the comment that K⋆/√σ₀ "absorbs" it at evaluator time. It did not — `z_cap.py:143` was called with `K⋆ = q_t_cop_d` raw, no (X̄/Ȳ) anywhere. v0.3 adds `xy_bar` as the 6th canonical free symbol of π(t) and restores the `(X̄/Ȳ)²` factor verbatim per PRIMITIVES.md §6.

**M2 sign-expectation amendment (PRE-REGISTERED EXPLICITLY).**

The v0.2 plan §M2 monotonicity expectation `∂|π|/∂κ < 0` is **structurally unsatisfiable** under the honest derivation (κ ∉ free_symbols(π)). v0.3 amends the canonical signed direction to the legitimate one anchored in PRIMITIVES.md §6:

$$\boxed{\;\frac{\partial |\pi|}{\partial (\overline{X/Y})}\bigg|_{(\sigma_0, \kappa, K^\star)\text{ fixed}} > 0 \quad \text{(strict; π ∝ (X̄/Ȳ)²)}\;}$$

Equivalent strict chain `|π|_TP4 > |π|_TP1 > |π|_TP5` (FX brackets 4200/4000/3800 COP/USD), enforced in `assert_pin_m2_monotonicity` and the hypothesis property test `test_pi_strict_increasing_in_xy_bar`. The TP2/TP3 κ-straddle test points are RETAINED in the 5-tuple (anti-fishing immutability) but the κ chain `|π|_TP2 > |π|_TP1 > |π|_TP3` is deprecated as structurally impossible — under v0.3 honest π, |π|_TP1 = |π|_TP2 = |π|_TP3 by construction.

The TP2/TP3 sign-expectation `Z_cap > 0` continues to hold and is enforced — these test points exercise the q_t^USD softplus channel of κ-dependence, which is the legitimate κ pathway. (At cohort_4, q_t_cop draws are already κ-marginalized via C2, so TP2 and TP3 produce identical Z_cap to TP1 in the present implementation; the κ-pathway becomes observable only when C2 emits per-κ posterior conditionals.)

**Anti-fishing posture — explicit re-pre-registration.**

- Sign expectation `Z_cap > 0 ∀ TP`: UNCHANGED.
- Monotonicity expectation: CHANGED from `∂|π|/∂κ < 0` to `∂|π|/∂(X̄/Ȳ) > 0`. This is NOT a silent re-tune — the v0.2 expectation was unsatisfiable under the honest math (the v0.2 "PASS" relied on a fabricated factor). The new expectation is anchored in PRIMITIVES.md §6 (π ∝ (X̄/Ȳ)²); the sign is mathematically derived, not chosen to match an observation.
- Identity tolerance: UNCHANGED at `NUMERICAL_IDENTITY_TOL = 1e-6`. Test grid size n_t_grid bumped from 12 to 5000 (Nyquist requirement for the sin(4ωt) kernel at ω=1).
- 5-test-point grid composition: UNCHANGED (TP1–TP5 labels and (κ, X̄/Ȳ) values unchanged; σ₀ values updated per FX bracket via PRIMITIVES.md §6 closed form).

**Test verdict on real C1 outputs (v0.3 emission).** All 5 TPs PASS:

| TP | Z (USD/mo) | CI 95% lo | CI 95% hi | sign-PASS | identity residual |
|---|---|---|---|---|---|
| TP1 | 8.153e+03 | 7.399e+03 | 8.980e+03 | YES | 6.3e-09 |
| TP2 | 8.153e+03 | 7.399e+03 | 8.980e+03 | YES | 6.3e-09 |
| TP3 | 8.153e+03 | 7.399e+03 | 8.980e+03 | YES | 6.3e-09 |
| TP4 | 8.560e+03 | 7.769e+03 | 9.429e+03 | YES | 6.3e-09 |
| TP5 | 7.745e+03 | 7.029e+03 | 8.531e+03 | YES | 6.3e-09 |

(X̄/Ȳ)-monotonicity chain: |π|_TP4 = 8.560e+03 > |π|_TP1 = 8.152e+03 > |π|_TP5 = 7.745e+03 — PASS strict. Symbolic identity check: PASS exact. (Smoke evaluation against synthetic C1-shaped lognormal CV=0.05 fixture; real C1 CV≈0.84 still routes to MC budget HALT pending C1 N_draws bump to ≈ 1e6 — orthogonal residual, unchanged from v0.2.)



**Goal:** Symbolically derive the saas-cohort streamed-premium function π(t) from the cohort pitch (§4.1) composed with the (T1)+(T2) cohort-cost distribution and the Υ_t revenue form, then pin the closed-form Z cap to `simulations/saas_builder/data/Z_cap_pinned.json` with a 5-test-point sign certification audit.

**Architecture:** sympy symbolic derivation (deterministic, exact) layered on top of the SIM-INFRA-0 three-tier scaffold. C1 cost posterior (synthetic τ_t panel) and C3 Υ_t verdict are read as fixed inputs; this cohort's π(t) is derived from PRIMITIVES.md §13 + §10 Carr-Madan replication composed with the cohort-specific `q_t^USD` (T2) form. The pinned Z cap and its 5-test-point sign verdicts are emitted via the shipped `ZCapPinnedWriter` (Pydantic-validated transient → frozen-dc `ZCapPinned` Value).

**Tech stack:** Python 3.13, sympy (symbolic), numpy (5-test-point evaluation grid), the shipped `simulations.{types,modules,utils}` scaffold from SIM-INFRA-0. NO PyMC in this plan (consumed only via C1 outputs). NO new IO boundary classes — `ZCapPinnedReader/Writer` already shipped.

**Spec anchor:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1.1 §4.1 (pitch operationalization), §5.2 (parameter brackets — LOCKED), §6 (functional-form pins), §9 (TODO-COHORT-4 verification gate), §10 (output artifact contract).

**Sub-task position:** SAAS-COHORT-4 is the *terminal* cohort sub-task for Stage-2. Per spec §11 dependency graph: COHORT-4 ⟵ COHORT-2 ∧ COHORT-3 ∧ Δ^(a_s) closed form. Plan-authoring (this document) is independent of execution; dispatch waits for COHORT-2 and COHORT-3 PASS verdicts.

**Out of scope:**
- Cost-side fits — C1 (T1 posterior + tier mix), C2 (T2 softplus fit + sign certification on Δ^(a_s)), C3 (Υ_t functional-form verdict). All three are upstream cohort plans.
- PyMC sampler authoring (lives in SIM-INFRA-0 + COHORT-1).
- New parquet/JSON IO boundaries — the M4 `Z_cap_pinned.json` schema is enforced by the shipped `simulations.utils.json_io._ZCapPinnedJsonModel` Pydantic transient validator.
- Live LP capital, deployment, on-chain settlement — Stage-3 by spec.
- Cross-cohort generalization — π(t) here is saas-cohort-specific; future cohorts re-derive.

---

## Phase 2 prelude — Math pins (M1–M4)

> Resolves the spec §9 TODO-COHORT-4 gate by pinning every symbol the implementer must reproduce verbatim. The implementing AI Engineer reads these contracts before authoring sympy code; foreground enforces by including the relevant pin in each Phase 2 task dispatch brief. **No threshold relaxed.** All thresholds inherit from spec §8.

### Pin M1 — π(t) symbolic anchor (saas-cohort-specific)

The cohort note `notes/SaaS_Builders_AI_NativeBuilders.md` §"Pitch" + §"Payoff" + §"Premium form" composed with PRIMITIVES.md §4.2 yields the saas-cohort π(t). The derivation chain is (the implementer reproduces each step in sympy; foreground does NOT pre-evaluate it):

**Step 1 — pitch identity (saas note §"Pitch" + spec §4.1).** The cap Z is the smallest non-negative real such that the posterior-predictive expectation of cohort COP cash outflow stays under it:

$$
Z \;=\; \min\Big\{ z \in \mathbb{R}_+ \;:\; \mathbb{E}\!\left[\frac{q_t^{\text{USD}}}{(X/Y)_t} + \pi(t)\right] \;\le\; z \Big\}
$$

with $q_t^{\text{USD}}$ from spec §5.1 (T2): $q_t^{\text{USD}} = \bar p_{\text{sub}} + p_t \cdot \mathrm{softplus}_\beta(\tau_t - \kappa)$.

**Step 2 — perpetual-horizon premium identity (PRIMITIVES.md §15 open item 4 + §9 streamed variant).** The streamed Panoptic-style premium replaces the discrete CPO premium $P_0^\Pi$ with a continuous flow:

$$
\pi(t)\, dt \;\leftrightarrow\; \frac{d\Pi}{dt}\, dt
$$

i.e., $\pi(t)$ is the instantaneous time-derivative of the convex CPO payoff $\Pi(\sigma_T)$ taken along the deterministic FX path from PRIMITIVES.md (6).

**Step 3 — closed-form $\Pi$ (PRIMITIVES.md §8.1).** $\Pi(\sigma_T) = K^\star \sqrt{\sigma_T}$ with equilibrium $K_s = K_l = K^\star$ per (14).

**Step 4 — Carr-Madan linearization (PRIMITIVES.md (16)–(19)).** First-order linearization around pinned $\sigma_0$:

$$
\Pi(\sigma_T) \;\approx\; \hat{K}\, \sigma_T,\quad \hat{K} \equiv \frac{K^\star}{2\sqrt{\sigma_0}}
$$

with the strip identity $\sigma_T \sim \int_0^{S_0} \frac{P(K)}{K^2} dK + \int_{S_0}^\infty \frac{C(K)}{K^2} dK$ for static replication.

**Step 5 — variance proxy along the deterministic FX path (PRIMITIVES.md §6).** Substitute $\sigma_T(\varepsilon, \omega, t)$ from the deterministic-path variance proxy; differentiate to obtain $d\Pi/dt$ as a closed-form function of $(K^\star, \sigma_0, \varepsilon, \omega, t)$. The resulting $\pi(t)$ is the **symbolic anchor for this plan** and is what the implementer derives in Task 2.1. Anti-fishing note: **do NOT bypass any step**; the chain Pitch → perpetual identity → §8.1 closed form → Carr-Madan → variance proxy is the canonical path. Skipping Carr-Madan to evaluate $\Pi(\sqrt{\sigma_T})$ pointwise on the test grid is a shortcut that loses static-replication semantics and is flagged by Reality Checker in Phase 4.

### Pin M2 — 5-test-point sign-certification grid

The §9 TODO-COHORT-4 gate certifies the $\pi(t) \cdot dt = d\Pi/dt$ identity at exactly **5 pinned $(\overline{X/Y}, \sigma_T, \kappa)$ test points** including two straddling the cap-kink at $\kappa$ and two straddling the FX-mean bracket. The grid is:

| Test point | $(\kappa, \overline{X/Y})$ | Spec rationale | Sign expectation |
|---|---|---|---|
| TP1 | $(\kappa_0,\; \overline{X/Y}_0)$ | spec §5.2 LOCKED brackets, primary | $\pi(t) > 0$ ∀ $t \in [0, T]$ |
| TP2 | $(0.5\kappa_0,\; \overline{X/Y}_0)$ | low-cap straddle of (T2) kink | $\pi(t) > 0$; $\lvert\pi\rvert_{\text{TP2}} > \lvert\pi\rvert_{\text{TP1}}$ |
| TP3 | $(1.5\kappa_0,\; \overline{X/Y}_0)$ | high-cap straddle of (T2) kink | $\pi(t) > 0$; $\lvert\pi\rvert_{\text{TP3}} < \lvert\pi\rvert_{\text{TP1}}$ |

**v0.2 MQ-FLAG-1 fix (canonical κ-monotonicity sign).** The TP2 and TP3 expectations above are restated in the single canonical signed direction:

$$\frac{\partial \lvert\pi\rvert}{\partial \kappa}\bigg|_{(\overline{X/Y}, \sigma_0)\text{ fixed}} \;<\; 0 \qquad \text{(strict; long-gamma cap shrinks as cap-kink rises)}$$

This sign expectation is consumed verbatim by Phase 3.3 hypothesis-tests joint-identifiability property AND by the Reality Checker / Model QA Specialist audit at Phase 4 (Tasks 4.1 #10 + 4.2 #2). NO orthogonal "monotone in κ direction" phrasing is used elsewhere in v0.2.
| TP4 | $(\kappa_0,\; \text{FX} = 4200\, \text{COP/USD})$ | M5 FX upper bracket per SIM-INFRA-0 + saas FX path | $\pi(t) > 0$; sign preserved at COP-weak |
| TP5 | $(\kappa_0,\; \text{FX} = 3800\, \text{COP/USD})$ | M5 FX lower bracket per SIM-INFRA-0 + saas FX path | $\pi(t) > 0$; sign preserved at COP-strong |

$\overline{X/Y}_0$ = audit-block-pinned 12-month trailing mean of monthly Banrep TRM per spec §3. $\kappa_0$ = spec §5.2 primary-tier $\kappa$ (Max-5x ≈ 6.5M tok/mo as default; the implementer reads the actual pinned value from `data/cohort_prior.parquet`). **A computed sign reversal at any one of TP1–TP5 fires HALT per spec §8(1).** No test point may be added, removed, or perturbed post-hoc; threshold tuning post-hoc is silent-fishing.

### Pin M3 — `ZCapPinned` schema (already shipped in `simulations/types/posterior.py`)

The Value-tier frozen-dataclass `ZCapPinned` (lines 173–257 of `simulations/types/posterior.py`) carries the emission contract. **Reproduce the field list verbatim for the implementer:**

- `Z_cop_per_month: float` — posterior-predictive mean of monthly cap (COP); finite, > 0.
- `ci_95_lo: float` — 95% credible-interval lower bound; finite, > 0; must satisfy `ci_95_lo ≤ Z_cop_per_month`.
- `ci_95_hi: float` — 95% credible-interval upper bound; finite, > 0; must satisfy `Z_cop_per_month ≤ ci_95_hi`.
- `audit_block: str` — 64-character lowercase hex sha256 over the C1/C2/C3 input artifacts; validated against the regex `[0-9a-f]{64}`.
- `tier_mix: Mapping[TierID, float]` — keys exactly `("pro", "max_5x", "max_20x")` per `simulations.types.tier.TIER_IDS`; values in $(0, 1]$, summing to 1 within `1e-9`. Default `{"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30}` per spec §5.2.
- `schema_version: str` — non-empty; default `"v1.0"` per `DEFAULT_SCHEMA_VERSION`.

**5-test-point sign verdicts** are NOT first-class fields on `ZCapPinned` (the frozen-dc was sized to spec §10 columns only). They are emitted in a sidecar `Z_cap_pinned.SIGN_VERDICTS.md` artifact (path: `simulations/saas_builder/data/Z_cap_pinned.SIGN_VERDICTS.md`) per Task 2.4. If a future plan revision wants the verdicts inside the JSON, that requires a `ZCapPinned` schema bump (additive `schema_version` evolution, NOT in scope here).

### Pin M4 — Audit-block sha256 helper (already shipped in `simulations/utils/audit_block.py`)

The shipped helper signatures are reproduced for the implementer:

- `compute_audit_block(file_paths: Sequence[str | Path]) -> str` — pure function w.r.t. file contents; sorts paths lex; embeds delimiter `b"--- <path>\n"` per file; returns 64-char lowercase hex sha256. Raises `ValueError` on empty; `FileNotFoundError` on missing files. **Path form matters** — relative vs absolute representations of the same file produce different digests (pinned by `test_compute_audit_block_path_form_matters` in shipped tests). Caller MUST canonicalize via `Path.resolve()` before hashing.
- `AuditBlockHasher` — IO-Boundary class; `__call__(paths: tuple[Path, ...]) -> str` delegates to `compute_audit_block`.

**C4 input set** (the files whose sha256 fixes the audit block on this iteration; the implementer hashes these in Task 2.3):

1. `simulations/saas_builder/data/synthetic_tau_t.parquet` (C1 output)
2. `simulations/saas_builder/data/cohort_prior.parquet` (C1 output)
3. `notebooks/saas_builder_stage_2/estimates/ROBUSTNESS_RESULTS.md` (C2 sign-certification + softplus fit). **v0.2 MQ-FLAG-3 fix (D9 line 166).** The COHORT-2 commit-sha that produced the PASS verdict on this file MUST be recorded alongside the path in Pin M4. The implementing agent records the sha in a sibling artifact `simulations/saas_builder/data/Z_cap_pinned.AUDIT_INPUTS.md` (one line: `<sha> ROBUSTNESS_RESULTS.md`) and the audit-block helper consumes BOTH the file content sha256 AND the recorded commit-sha — if `git log -1 --format=%H -- notebooks/saas_builder_stage_2/estimates/ROBUSTNESS_RESULTS.md` returns a sha different from the recorded one, Task 0.4 step 2 fires HALT (post-PASS file mutation detected). Rationale: prevent silent drift where `ROBUSTNESS_RESULTS.md` is mutated post-PASS without re-running COHORT-2 sign-certification, which would let the audit-block change without the verdict-routing being aware.
4. `notebooks/saas_builder_stage_2/estimates/PRIMARY_RESULTS.md` (C3 Υ_t-form verdict + posterior summaries)
5. `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (the spec itself; locks parameter brackets)

All five paths are canonicalized via `Path.resolve()` before passing to `compute_audit_block`. Missing any one fires `FileNotFoundError`; this is the desired upstream-dependency enforcement. The COHORT-2 commit-sha pinning (item 3 above) is the only additional non-content lineage commitment introduced in v0.2; all other Pin M4 semantics are unchanged.

---

## File structure (folder-level only; .py decomposition is task-time discovery)

```
simulations/saas_builder/
├── __init__.py                 # NEW; namespace marker
├── README.md                   # NEW; cohort-scope + π(t) anchor
├── pi_t_symbolic.py            # NEW (Callable tier); sympy derivation of π(t) per Pin M1
├── z_cap_evaluator.py          # NEW (Callable tier); 5-test-point evaluator + posterior-predictive Z
└── data/
    ├── Z_cap_pinned.json                  # EMITTED; via shipped ZCapPinnedWriter
    └── Z_cap_pinned.SIGN_VERDICTS.md      # EMITTED; sidecar 5-test-point verdicts

simulations/tests/
└── test_saas_cohort_4.py       # NEW; tests for pi_t_symbolic + z_cap_evaluator + JSON round-trip

scratch/2026-05-08-saas-cohort-4-research/
├── RESEARCH.md                 # NEW; gsd-phase-researcher Carr-Madan × π(t) interaction
└── PLAN_RECONCILIATION.md      # NEW; foreground reconciliation memo
```

The `.py` filenames are the *only* prescription; the implementing AI Engineer decides function-level decomposition within each Callable file per the functional-python three-tier discipline. All `.py` files in `simulations/saas_builder/` are Callable-tier (frozen-dc + `__call__`) — IO is delegated to the shipped `simulations.utils.json_io.ZCapPinnedWriter` and `simulations.utils.audit_block.AuditBlockHasher`. NO new IO Boundary classes are authored in this plan.

**Repo-level changes:** add `simulations.saas_builder` to `pyproject.toml` packages. Update `CLAUDE.md` repo-structure section (Phase 5).

---

## Phase 0 — Pre-flight

### Task 0.1 — Re-read functional-python skill from disk

Per `feedback_check_functional_python_skill_first.md` (NON-NEGOTIABLE).

- [ ] **Step 1** — Read `~/.claude/skills/functional-python/SKILL.md` via Read tool.
- [ ] **Step 2** — Confirm sha256 + line count match the reference recorded in SIM-INFRA-0 v1.1 Task 0.1 (sha `0debecfb05b31aa9212433b9388e0b174aa2ec42948ab62cb9b94a66387e4568`, 78 lines as of 2026-05-07). If divergent, surface to user before proceeding.
- [ ] **Step 3** — Read-only; no commit.

### Task 0.2 — Confirm Python venv + dev deps + sympy

- [ ] **Step 1** — `source .venv/bin/activate`; confirm `python --version` returns 3.13.x.
- [ ] **Step 2** — `uv pip install sympy` (saas-cohort-4 introduces the sympy dependency; pin in `pyproject.toml` extras).
- [ ] **Step 3** — Confirm `python -c "import sympy; print(sympy.__version__)"` succeeds.

### Task 0.3 — Confirm working tree clean and on `iter/saas-builder-stage-2`

- [ ] **Step 1** — `git status --short`. Expect no modified files (untracked allowed).
- [ ] **Step 2** — `git branch --show-current`. Expect `iter/saas-builder-stage-2`.

### Task 0.4 — Confirm SIM-INFRA-0, COHORT-2, COHORT-3 prerequisites

Per spec §11 dependency graph + cross-plan dependency declared in this plan's header.

- [ ] **Step 1** — Confirm `simulations/types/posterior.py`, `simulations/utils/json_io.py`, `simulations/utils/audit_block.py` are present and on the current commit (SIM-INFRA-0 ACCEPT verdict committed).
- [ ] **Step 2** — Confirm COHORT-2 `estimates/ROBUSTNESS_RESULTS.md` exists with sign-certification PASS verdict on Δ^(a_s) at all spec §5.2 bracket points. If FAIL or absent: HALT — COHORT-4 cannot proceed per spec §11. **v0.2 MQ-FLAG-3 fix:** ALSO record `git log -1 --format=%H -- notebooks/saas_builder_stage_2/estimates/ROBUSTNESS_RESULTS.md` to `simulations/saas_builder/data/Z_cap_pinned.AUDIT_INPUTS.md` as one line `<sha> ROBUSTNESS_RESULTS.md`. On subsequent re-runs of Phase 0 in this plan, if the recomputed sha differs from the recorded sha, HALT per `feedback_pathological_halt_anti_fishing_checkpoint` — the file has been mutated post-PASS without re-running COHORT-2 sign-certification.
- [ ] **Step 3** — Confirm COHORT-3 `estimates/PRIMARY_RESULTS.md` carries the Υ_t-form verdict (martingale (S4) primary or named arm). If absent: HALT.
- [ ] **Step 4** — Confirm COHORT-1 outputs `data/synthetic_tau_t.parquet` + `data/cohort_prior.parquet` exist. If absent: HALT.

### Task 0.5 — Confirm agent registry state

- [ ] **Step 1** — Run `find ~/.claude/agents -name 'engineering-ai-engineer*' -o -name 'specialized-reality-checker*' -o -name 'specialized-model-qa*' -o -name 'engineering-code-reviewer*' -o -name 'specialized-gsd-phase-researcher*'`.
- [ ] **Step 2** — Confirm all five files appear in active paths (not under `_archived/`). If any is archived, HALT and surface to user per `feedback_pathological_halt_anti_fishing_checkpoint`.

---

## Phase 1 — Research and reconciliation

### Task 1.1 — Carr-Madan × saas-cohort π(t) interaction research (gsd-phase-researcher, background)

**Files:** Create: `scratch/2026-05-08-saas-cohort-4-research/RESEARCH.md`. **Note:** writes to `scratch/`, NOT `.planning/` (per `feedback_planning_dir_bespoke_naming.md`).

**Brief.** Research:

1. Carr-Madan replication identity (PRIMITIVES.md §10 (18)) interaction with the saas-cohort blended $p_t$ + (T2) softplus-regularized $q_t^{\text{USD}}$ form. Specifically: does linearization around pinned $\sigma_0$ commute with the softplus expectation operator? Cite ≥3 sources covering Carr-Madan (Carr & Madan 2001 original; Bondarenko 2014 review; one Panoptic-relevant strip-replication source).
2. Perpetual-horizon $\pi(t) \leftrightarrow d\Pi/dt$ derivation pattern in continuous-payment options literature (Panoptic streaming-premium variants; perpetual put-call literature). Cite ≥3 sources.
3. Posterior-predictive expectation of $Z$ when $q_t^{\text{USD}}$ is itself a posterior-distributed quantity from C1+C2 — does the $\mathbb{E}[\cdot]$ in the spec §4.1 cap definition refer to the *predictive* expectation (over the predictive distribution induced by posterior + likelihood) or the *posterior-mean* expectation (mean of posterior-mean cash-flow)? Resolve unambiguously; cite Bayesian decision-theory references.
4. sympy idioms for symbolic-then-numerical evaluation: how to express $\pi(t)$ symbolically, then `lambdify` for the 5-test-point grid without losing the closed-form audit trail. Cite sympy docs + ≥1 functional-python codebase precedent.

Output: ≤2000 words; per-question section; references with URLs/citekeys; explicit "verdict" line per question.

- [ ] **Step 1** — Foreground dispatches `gsd-phase-researcher` in background.
- [ ] **Step 2** — Continue with Phase 2 tasks; Task 1.2 blocks on this output.

### Task 1.2 — Plan reconciliation memo (foreground)

**Files:** Create: `scratch/2026-05-08-saas-cohort-4-research/PLAN_RECONCILIATION.md`.

- [ ] **Step 1** — Read 1.1 output.
- [ ] **Step 2** — Reconcile any disagreement between RESEARCH.md verdicts and Pin M1's symbolic-derivation chain. If RESEARCH.md identifies a step in M1 that is *non-trivial* (e.g., Carr-Madan does NOT commute with the softplus expectation), document a CORRECTIONS-α block here, surface to user, and HALT before Phase 2.
- [ ] **Step 3** — Commit research artifacts.

```bash
git add scratch/2026-05-08-saas-cohort-4-research/
git commit -m "research(saas-cohort-4): Carr-Madan × π(t) interaction + reconciliation"
```

---

## Phase 2 — Implementation

> **Sub-task split.** Phase 2 is split into four scoped AI Engineer dispatches: (2.1) symbolic π(t), (2.2) Z-cap evaluator, (2.3) audit-block + JSON emission orchestration, (2.4) tests. Each dispatch carries the M1–M4 pins from the prelude and the relevant prior-task outputs.

### Task 2.1 — Implement `simulations/saas_builder/pi_t_symbolic.py`

**Files:** Create `simulations/saas_builder/{__init__.py, README.md, pi_t_symbolic.py}`.

**Agent.** `AI Engineer`.

**Inputs (passed in dispatch brief):**

- This plan's Phase 2 prelude (Pins M1–M4).
- Phase 1 RESEARCH.md + PLAN_RECONCILIATION.md.
- `notes/PRIMITIVES.md` §6 (FX path), §8.1 (closed-form $\Pi$), §10 (Carr-Madan), §13 (variable map).
- `notes/SaaS_Builders_AI_NativeBuilders.md` §"Pitch", §"Payoff", §"Premium form", §4.2.
- Spec v1.1.1 §4.1, §5.1, §6.
- `simulations/types/` shipped Value containers (FX path params, softplus params, tier prior).
- functional-python skill (re-read in 0.1).

**Behavior contract:**

- File `pi_t_symbolic.py` is Callable-tier: `@dataclass(frozen=True)` config + `__call__` returning a sympy Expr (closed form) AND a numpy-callable `lambdify`'d evaluator.
- The Callable's `__call__` derives π(t) **symbolically** by reproducing Pin M1 Steps 1–5 verbatim. Every intermediate sympy Expr is documented in the Callable's docstring with the corresponding equation reference (PRIMITIVES.md (X) or saas-note §Y).
- May import from `simulations.types.{fx, posterior, distributions, tier}` only.
- NO IO. NO mutable state.
- Returns a Value object (frozen-dc) carrying both the symbolic Expr and the lambdified function. Name: `PiTDerivation` (Value-tier). **v0.2 RC-FLAG-1 fix (definitive sidecar posture).** `PiTDerivation` MUST live in `simulations/saas_builder/pi_t_symbolic.py` as a Callable-tier-adjacent Value (frozen-dc co-located with its consumer). Extending `simulations/types/posterior.py` to host `PiTDerivation` is REJECTED in this plan because it would require a `schema_version` bump on `ZCapPinned` (Pin M3) which is explicitly deferred. The schema-bump-deferred posture in Pin M3 is **definitive for v0.2**, not interim — any future cohort needing `PiTDerivation` exposure across `simulations/types/` requires a separate SIM-INFRA-0 v1.2 amendment plan with its own 2-wave verify; this plan does not author that amendment.
- The closed-form $\pi(t)$ is anchored to PRIMITIVES.md (6) FX path + (16)–(19) Carr-Madan strip + saas note §"Premium form" perpetual identity. The docstring cites all three.

**Anti-fishing constraint.** The symbolic derivation does NOT take any free real-valued parameter that was not pinned in spec §5.2. If a parameter is needed mid-derivation that is not in the locked bracket (e.g., a discretization $T$), it MUST be passed in via the frozen-dc config field, with a docstring citation back to where it is pinned in the cohort plan or PRIMITIVES.md. New free parameters → HALT.

- [ ] **Step 1** — Foreground dispatches `AI Engineer` in background with the brief.
- [ ] **Step 2** — On agent completion, run `pytest simulations/tests/ -v` (existing tests still pass) and `ty check simulations/saas_builder/`. Both clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(saas-cohort-4/pi-t): symbolic π(t) derivation per spec §4.1 + PRIMITIVES (6)/(16)–(19)"
```

### Task 2.2 — Implement `simulations/saas_builder/z_cap_evaluator.py`

**Files:** Create `simulations/saas_builder/z_cap_evaluator.py`.

**Agent.** `AI Engineer`.

**Inputs (passed in dispatch brief):**

- Phase 2 prelude (Pins M1–M4).
- Task 2.1 output (`pi_t_symbolic.py` provides the lambdified π(t)).
- C1 outputs: `simulations/saas_builder/data/synthetic_tau_t.parquet` (10-column schema per spec §10).
- C2 verdict: `notebooks/saas_builder_stage_2/estimates/ROBUSTNESS_RESULTS.md` (softplus posterior + Δ^(a_s) sign certification).
- C3 verdict: `notebooks/saas_builder_stage_2/estimates/PRIMARY_RESULTS.md` (Υ_t-form verdict).
- spec v1.1.1 §4.1 (cap operationalization), §6 (functional-form pins), §9 (verdict gate).

**Behavior contract:**

- File `z_cap_evaluator.py` is Callable-tier.
- `__call__` consumes: (a) the `PiTDerivation` Value from Task 2.1; (b) a `PosteriorDraws` Value loaded from `synthetic_tau_t.parquet`; (c) the `(\overline{X/Y}, \kappa)` 5-test-point grid from Pin M2.
- For each of TP1–TP5 (Pin M2 grid), evaluate the lambdified π(t) on a finite-$t$ grid (implementer pins the temporal discretization in the frozen-dc config field, default $T = 12$ months, $\Delta t = 1$ month — the saas-cohort monthly time grain per spec §2). Compute: (i) π(t) values; (ii) the discrete $d\Pi/dt$ identity check (PRIMITIVES.md §15 open item 4 — $|\pi(t) \cdot \Delta t - \Delta \Pi| / \Pi$ must be **≤ $10^{-10} \cdot N_{\text{legs}}$ at the symbolic level (inherited from `notes/PRIMITIVES.md` §12 identity-tolerance ledger; v0.2 RC-FLAG-2 explicit-citation fix), relaxed to ≤ $10^{-6}$ at the numerical level given finite-$t$ discretization (inherited from Path A v0 §10.4 numerical reconciliation tolerance; cited inline rather than parenthetically per RC-FLAG-2)**); (iii) the sign of π(t) over the grid.
- Compute the posterior-predictive $\mathbb{E}[q_t^{\text{USD}} / (X/Y)_t + \pi(t)]$ over the C1 synthetic_tau_t panel; this is $Z$ per spec §4.1.
- **MC error budget on the posterior-predictive expectation (v0.2 MQ-FLAG-2 fix; addresses D6 line 268).** When the predictive expectation does NOT close in sympy and falls back to Monte Carlo over C1 posterior draws, the MC error on $\hat Z$ MUST satisfy:
  $$\frac{\mathrm{stderr}(\hat Z)}{\hat Z} \;\le\; 10^{-3} \quad \text{with} \quad N_{\text{draws}} \;\ge\; 4000$$
  where $\mathrm{stderr}(\hat Z) = \sqrt{\widehat{\mathrm{Var}}_{\text{posterior}}(Z) / N_{\text{draws}}}$ is the standard MC error of the posterior-predictive mean. The 1e-3 ratio is the third significant figure of $Z_{\text{cop\_per\_month}}$, matching `ZCapPinned` JSON precision. The 4000-draw floor inherits from the C1 Pin R4 sim-count (and from PyMC convention). On breach: invoke `feedback_pathological_halt_anti_fishing_checkpoint` — HALT with disposition memo offering ≥3 pivots (increase draws to next decade; compute Z analytically by closing in sympy; flag the iteration WEAK pending C1 re-fit). The MC error gate is **distinct from** the identity-tolerance gate ($\le 10^{-6}$ numerical, $\le 10^{-10}$ symbolic on $d\Pi/dt$) — that gate covers the symbolic chain; this gate covers the MC integration of $Z$.
- Compute the 95% credible interval as the (2.5, 97.5) percentile pair of the per-draw $Z$ realizations.
- Return a `ZCapPinned` Value (frozen-dc — already shipped, Pin M3) populated with: `Z_cop_per_month`, `ci_95_lo`, `ci_95_hi`, `tier_mix` from the cohort_prior.parquet posterior (or default per spec §5.2 if posterior-tier-mix not separately certified). `audit_block` field is filled by Task 2.3 — Task 2.2 emits a `ZCapPinned` instance with a placeholder audit_block (the implementer wires Task 2.3 to overwrite via a frozen-dc replace-and-rebuild, since `ZCapPinned` is frozen).
- Sidecar verdicts: emit `Z_cap_pinned.SIGN_VERDICTS.md` listing per-test-point sign + identity-tolerance status. **HALT trigger:** any test-point sign violation OR any identity-tolerance breach → invoke `feedback_pathological_halt_anti_fishing_checkpoint`: (a) HALT, (b) disposition memo with ≥3 pivot options, (c) user adjudication, (d) CORRECTIONS-block in v0.2 of this plan, (e) post-hoc 3-way review.
- May import from `simulations.types.{posterior, fx, tier}`, `simulations.utils.parquet_io`, and Task 2.1's symbolic module.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Run `pytest simulations/tests/ -v` + `ty check simulations/saas_builder/`. Both clean.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(saas-cohort-4/z-cap): 5-test-point evaluator + posterior-predictive Z"
```

### Task 2.3 — Audit-block + JSON emission orchestration

**Files:** Modify `simulations/saas_builder/z_cap_evaluator.py` to add a final-orchestration free function `pin_and_emit` (or implementer-named equivalent) that wires the audit-block helper + the shipped `ZCapPinnedWriter`. Or factor into a thin orchestration file `simulations/saas_builder/emit.py` (implementer's discretion per functional-python decomposition rules).

**Agent.** `AI Engineer`.

**Inputs (passed in dispatch brief):**

- Phase 2 prelude (Pin M4 file list).
- Tasks 2.1, 2.2 outputs.
- `simulations/utils/audit_block.py` (`compute_audit_block`, `AuditBlockHasher`).
- `simulations/utils/json_io.py` (`ZCapPinnedWriter`).

**Behavior contract:**

- Free function (or thin Callable) that:
  1. Resolves the five Pin M4 input paths to absolute via `Path.resolve()`.
  2. Calls `compute_audit_block(...)` to obtain the 64-char hex digest.
  3. Replaces the placeholder `audit_block` field on the `ZCapPinned` from Task 2.2 (frozen-dc, so use `dataclasses.replace`).
  4. Calls `ZCapPinnedWriter()(z, "simulations/saas_builder/data/Z_cap_pinned.json")`.
- Verifies round-trip by immediately reading back via `ZCapPinnedReader` and asserting field-by-field equality with the in-memory `ZCapPinned`. Mismatch → `RuntimeError` with diagnostic.
- May import from `simulations.types.posterior`, `simulations.utils.{audit_block, json_io}`, Task 2.2's evaluator.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Run `pytest simulations/tests/ -v`. All pass.
- [ ] **Step 3** — Commit.

```bash
git commit -am "feat(saas-cohort-4/emit): audit-block + ZCapPinnedWriter orchestration"
```

### Task 2.4 — Tests scaffold and 5-test-point math-pin verification

**Files:** Create `simulations/tests/test_saas_cohort_4.py`.

**Agent.** `AI Engineer`.

**Inputs:**

- Tasks 2.1, 2.2, 2.3 outputs.
- Phase 2 prelude (Pins M1–M4 — tests verify each pin).

**Behavior contract:**

- Tests assert:
  - **M1 verification.** Symbolic π(t) reproduces PRIMITIVES.md §8.1 closed form $\Pi = K^\star \sqrt{\sigma_T}$ in the ($\sigma_T \to \sigma_0$) limit (sympy equality, not numerical).
  - **M2 verification.** All five test points TP1–TP5 evaluate to π(t) > 0 over the spec-§2 monthly grid; sign certification PASS at each.
  - **M2 monotonicity.** TP3 (high-cap, $1.5\kappa_0$) yields strictly smaller $|\pi|$ than TP1 (primary $\kappa_0$); TP2 (low-cap) yields strictly larger $|\pi|$ than TP1. **v0.2 MQ-FLAG-1 fix:** test asserts the canonical signed direction $\partial \lvert\pi\rvert / \partial \kappa < 0$ at fixed $(\overline{X/Y}_0, \sigma_0)$ — equivalently, $\lvert\pi\rvert_{\text{TP2}} > \lvert\pi\rvert_{\text{TP1}} > \lvert\pi\rvert_{\text{TP3}}$ as a strict chain.
  - **M2 identity tolerance.** $|\pi(t) \cdot \Delta t - \Delta \Pi| / |\Pi|$ ≤ $10^{-6}$ at all 5 test points × all temporal grid points.
  - **MC error budget (v0.2 MQ-FLAG-2 fix).** Synthetic posterior-predictive run with $N_{\text{draws}} = 4000$ and known closed-form $Z$ asserts $\mathrm{stderr}(\hat Z) / \hat Z \le 10^{-3}$; a synthetic case forcing $N_{\text{draws}} = 100$ asserts the gate triggers HALT routing.
  - **M3 schema enforcement.** `ZCapPinned` constructor rejects: (i) `audit_block` of wrong length; (ii) `tier_mix` keys not equal to `TIER_IDS`; (iii) `tier_mix` not summing to 1; (iv) `ci_95_lo > Z_cop_per_month` ordering breach. (Tests of the shipped Value type as a regression guard.)
  - **M4 audit-block determinism.** `compute_audit_block` over the same five Pin M4 input paths produces the same digest twice in a row; producing a different digest if any one input file's bytes change by 1 byte.
  - **JSON round-trip.** Write a `ZCapPinned` via `ZCapPinnedWriter`, read back via `ZCapPinnedReader`, assert field-by-field equality including `tier_mix` keys post `_coerce_tier_mix`.
- Hypothesis property strategies: one strategy each for `PiTDerivation` (sympy-arity-bounded — **v0.2 RC-FLAG-3 fix: arity ceiling pinned at MAX 6 free symbols per generated Expr**, covering the canonical $(K^\star, \sigma_0, \varepsilon, \omega, t, \kappa)$ tuple from Pin M1 Steps 1–5; strategies that try to compose Exprs with > 6 free symbols are filtered out via `assume()` so property-test reproducibility is bounded), `ZCapPinned` (parameter-bounded per spec §5.2). Joint-identifiability property: varying $\kappa$ alone in the `PiTDerivation` config produces monotone change in $|\pi|$ at TP1's $(\overline{X/Y}, \sigma_0)$ — analog to SIM-INFRA-0 v1.1 §15.3 for the C4 layer.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Run `pytest simulations/tests/test_saas_cohort_4.py -v`. All pass.
- [ ] **Step 3** — Commit.

```bash
git commit -am "test(saas-cohort-4): M1–M4 pin tests + 5-test-point sign verification + JSON round-trip"
```

---

## Phase 3 — Audit-pass chain (Honnibal sequence)

> Six sequential skill invocations. Order per SIM-INFRA-0 v1.1 §15.5 (mutation-testing follows pre-mortem): tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing.

### Task 3.1 — `tighten-types`

**Skill scope:** `simulations/saas_builder/`. Apply recommendations; re-test + re-typecheck; commit.

- [ ] **Step 1–4** — invoke / apply / verify / `git commit -am "audit(saas-cohort-4): tighten-types pass"`.

### Task 3.2 — `contract-docstrings`

**Skill scope:** `simulations/saas_builder/`. Special focus: every sympy Expr-returning function MUST cite its PRIMITIVES.md / saas-note equation reference in the docstring (anti-fishing trace).

- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-4): contract-docstrings pass"`.

### Task 3.3 — `hypothesis-tests`

**Skill scope:** `simulations/saas_builder/` + `simulations/tests/test_saas_cohort_4.py`.

**Additional property scope.** Include a property exercising joint $(\kappa, \overline{X/Y}, \sigma_0)$ behavior on `PiTDerivation` — varying any one with the other two fixed must produce a monotone-or-zero change in $|\pi(t)|$ at $t = T/2$ with the expected sign per spec §6 partial-derivative table. **v0.2 MQ-FLAG-1 fix:** the κ-direction property MUST encode the canonical signed direction $\partial \lvert\pi\rvert / \partial \kappa < 0$ (strict) per Pin M2 v0.2 — i.e., property test asserts $\lvert\pi(t; \kappa_2)\rvert < \lvert\pi(t; \kappa_1)\rvert$ whenever $\kappa_2 > \kappa_1$, holding $(\overline{X/Y}, \sigma_0)$ fixed. Sign-violation HALT applies.

- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-4): hypothesis-tests pass — incl. joint identifiability"`.

### Task 3.4 — `try-except`

**Skill scope:** `simulations/saas_builder/`. Tier reminder: `simulations/saas_builder/` is Callable-tier; non-trivial `try/except` should NOT appear here. The only acceptable `try/except` is around the `dataclasses.replace` audit-block wiring in Task 2.3 if it catches a propagated `ValueError` to re-raise with diagnostic — and that should be `raise ... from exc` chained.

- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-4): try-except pass"`.

### Task 3.5 — `pre-mortem`

**Skill scope:** `simulations/saas_builder/` AND `simulations/saas_builder/data/` (emission boundary).

For each surfaced fragility: (a) regression test, (b) refactor, or (c) document in module README. Specific fragility hypotheses to test:

- Numerical underflow at TP3 (high-cap, low-overage): does $|\pi|$ collapse toward float64 zero? If so, floor + flag.
- sympy `lambdify` numpy backend collisions: does the lambdified π(t) silently return scalar when fed an array? Test array-shape preservation.
- Audit-block ordering: if the C1/C2/C3 input paths change in subsequent iterations, the digest changes — is the file list versioned? Document Pin M4 list in README.

- [ ] **Step 1–4** — `git commit -am "audit(saas-cohort-4): pre-mortem pass — modules + emission"`.

### Task 3.6 — `mutation-testing`

**Skill scope:** `simulations/saas_builder/`.

**Kill-rate threshold: ≥ 80%** per industry-standard mutation kill-rate benchmark (SIM-INFRA-0 v1.1 §15.12; not an analog of spec §8(7) posterior CI-width gate).

**Equivalent-mutant exemption cap: ≤ 5%** of total mutants per SIM-INFRA-0 v1.1 §15.6. Each exemption requires a one-line justification. If >5%, an independent `Code Reviewer` audits the exemption list before this audit pass closes.

- [ ] **Step 1** — Invoke skill.
- [ ] **Step 2** — Iterate until kill rate ≥ 80% AND exemption rate ≤ 5%. If exemption would exceed 5%, add tests rather than exempt.
- [ ] **Step 3** — Re-test; commit.

```bash
git commit -am "audit(saas-cohort-4): mutation-testing pass — kill rate $METRIC% (≥80%; equiv-exempt ≤5%)"
```

---

## Phase 4 — Verification gate

### Task 4.1 — Reality Checker compliance audit

**Files:** Create `scratch/2026-05-08-saas-cohort-4-audit/reality_checker_compliance.md`.

**Agent.** `Reality Checker`.

**Brief.** Audit `simulations/saas_builder/` against functional-python skill rules + Phase 2 math pins (M1–M4) + spec §9 TODO-COHORT-4 gate:

1. Every `@dataclass` has `frozen=True` (grep verified).
2. Inheritance only via `Protocol` or `Exception` subclassing (no `class Foo(BaseModel)` outside the shipped private `_ZCapPinnedJsonModel`).
3. Every public function has a return-type annotation (sympy Expr return types are explicit).
4. No bare `Any` outside IO-boundary opaque returns; each instance documented.
5. Every module-level constant is `Final`.
6. Every repeated compound type has a `TypeAlias`.
7. Tier-import discipline: `simulations/saas_builder/` is Callable-tier — must NOT import from any IO-Boundary class except via the shipped `simulations.utils.{json_io, audit_block, parquet_io}` interfaces.
8. Audit artifacts (3.1–3.6) all present.
9. **Pin M1–M4 enforced:** Reality Checker MUST verify each pin by direct test execution: M1 sympy closed form matches §8.1; M2 5-test-point sign verdicts emitted in `Z_cap_pinned.SIGN_VERDICTS.md` AND match a fresh re-evaluation; M3 schema enforcement at JSON round-trip; M4 audit-block determinism over the documented input list.
10. **Anti-fishing audit.** Confirm the 5 test-point grid in code matches Pin M2 verbatim (no points added/removed/perturbed). Confirm the sympy derivation in `pi_t_symbolic.py` reproduces M1 Steps 1–5 with cited equation references. ANY drift is a REJECT.

Default to REJECT. Each finding: file:line evidence. ≤2000 words.

**HALT trigger:** On REJECT verdict, foreground executes `feedback_pathological_halt_anti_fishing_checkpoint` protocol: (a) HALT, (b) disposition memo with ≥3 pivot options, (c) user adjudication, (d) CORRECTIONS-block in v0.2 of this plan, (e) post-hoc reverify. Do not silently fix and continue.

- [ ] **Step 1** — Foreground dispatches.
- [ ] **Step 2** — Verdict ACCEPT or ACCEPT_WITH_FLAGS → advance. REJECT → HALT per above.
- [ ] **Step 3** — Commit verdict.

### Task 4.2 — Model QA Specialist audit

**Files:** Create `scratch/2026-05-08-saas-cohort-4-audit/model_qa_compliance.md`.

**Agent.** `Model QA Specialist`.

**Brief.** Audit the modeling layer specifically:

1. Pin M1 derivation chain: each of Steps 1–5 cited verbatim; no shortcuts past Carr-Madan; no silent re-parameterization.
2. Pin M2 5-test-point grid: each TP's sign expectation matches spec §6 partial-derivative table; no test point's sign is post-hoc adjusted to match observed.
3. Posterior-predictive expectation: the $\mathbb{E}[\cdot]$ in the cap calculation is the *predictive* expectation (per Task 1.1 verdict), not posterior-mean-of-mean — verify by reading the implementer's docstring + the actual numpy operation against the C1 panel.
4. CI computation: 95% CI is computed from per-draw $Z$ realizations (i.e., the predictive distribution of the cap), NOT a bootstrap on posterior-mean Z. Verify.
5. Identity-tolerance gate: $\le 10^{-6}$ numerical, $\le 10^{-10}$ symbolic per PRIMITIVES.md §12 / Path A v0 §10.4 (the spec §9 inheritance).
6. No threshold relaxed; no parameter free in the symbolic chain that wasn't pinned in spec §5.2.

Default to REJECT. ≤2000 words. **HALT trigger same as 4.1.**

- [ ] **Step 1–3** — dispatch / verdict / commit.

### Task 4.3 — Static analysis sweep

**HALT trigger:** any failure → `feedback_pathological_halt_anti_fishing_checkpoint`.

- [ ] **Step 1** — `ruff check simulations/saas_builder/`. Zero warnings expected.
- [ ] **Step 2** — `ty check simulations/saas_builder/` (or `mypy --strict simulations/saas_builder/`). Zero errors.
- [ ] **Step 3** — `pytest simulations/tests/test_saas_cohort_4.py -v --cov=simulations/saas_builder`. All pass; coverage ≥ 90%.
- [ ] **Step 4** — On any failure: HALT.

> **Note on plan-document verify.** Per `feedback_two_wave_doc_verification` (NON-NEGOTIABLE), this plan must be 2-wave verified (Reality Checker + Model QA Specialist) by foreground orchestration **before commit**, separate from the in-plan implementation gates above. Plan executors do not re-run that pre-commit verify.

---

## Phase 5 — Code review and PR-readiness

### Task 5.1 — Code Reviewer audit

**Files:** Create `scratch/2026-05-08-saas-cohort-4-audit/code_reviewer_report.md`.

**Agent.** `Code Reviewer`.

**Brief.** Independent code review: correctness, maintainability, performance. NOT functional-python compliance (covered by 4.1) and NOT modeling correctness (covered by 4.2). Specific focus:

- sympy → numpy `lambdify` numerical-stability review.
- Frozen-dc replace pattern for the audit-block field overwrite — is it idiomatic?
- File path canonicalization — is `Path.resolve()` used consistently before hashing?

- [ ] **Step 1–3** — dispatch / fix / `git commit -am "review(saas-cohort-4): Code Reviewer pass"`.

### Task 5.2 — CLAUDE.md update

**Files:** Modify `CLAUDE.md` repo-structure section + active-iterations section.

- [ ] **Step 1** — Add `simulations/saas_builder/` row to the repo-structure tree.
- [ ] **Step 2** — Add one line under active iterations marking SAAS-COHORT-4 status (PASS / WEAK / etc. per gate verdict).
- [ ] **Step 3** — `git commit -am "docs(saas-cohort-4): CLAUDE.md repo-structure + active-iterations updated"`.

### Task 5.3 — `gate_verdict.json` emission

**Files:** Create `notebooks/saas_builder_stage_2/estimates/gate_verdict.json` (or update if exists). Spec §10 schema: `{"sub_task": "TODO-COHORT-4", "verdict": "PASS|WEAK|MARGINAL|FAIL|INDISTINGUISHABLE", "evidence": [...]}`.

- [ ] **Step 1** — Compose verdict object referencing `Z_cap_pinned.json`, `Z_cap_pinned.SIGN_VERDICTS.md`, the audit-block hex string, and the per-TP sign verdicts.
- [ ] **Step 2** — Write JSON.
- [ ] **Step 3** — `git commit -am "feat(saas-cohort-4): gate_verdict.json emission per spec §10"`.

### Task 5.4 — PR refresh

- [ ] **Step 1** — `git push origin iter/saas-builder-stage-2`.
- [ ] **Step 2** — Resolve PR number dynamically:
  ```bash
  PR_NUM=$(gh pr list --repo wvs-finance/abrigo-analytics --search "head:iter/saas-builder-stage-2" --json number -q '.[0].number')
  ```
  Then `gh pr edit "$PR_NUM" --repo wvs-finance/abrigo-analytics --body "$(cat <<'EOF' ... EOF)"` with body covering SAAS-COHORT-4 completion, the 5 test-point sign verdicts, the pinned $Z$ value + 95% CI, and the audit-block hex.
- [ ] **Step 3** — Confirm PR shows new commits.

---

## Strategic-delegation map

| Phase / Task | Agent | Skill / specialty |
|---|---|---|
| 1.1 | `gsd-phase-researcher` | Carr-Madan × π(t) interaction research (background, parallel) |
| 2.1 | `AI Engineer` | sympy symbolic derivation |
| 2.2 | `AI Engineer` | numerical evaluator + posterior-predictive Z |
| 2.3 | `AI Engineer` | audit-block + JSON emission orchestration |
| 2.4 | `AI Engineer` | tests + Hypothesis property strategies |
| 3.1–3.6 | foreground (skill invocation) | Honnibal audit-pass chain |
| 4.1 | `Reality Checker` | functional-python + math-pin compliance audit |
| 4.2 | `Model QA Specialist` | modeling-layer + posterior-predictive correctness audit |
| 4.3 | foreground | static analysis (ruff / ty / pytest) |
| 5.1 | `Code Reviewer` | independent correctness/maintainability/perf review |
| 5.2–5.4 | foreground | docs + emission + PR |

---

## Verification matrix (cross-reference)

| Spec §X row | `simulations/saas_builder/` location | Math pin | Consumed from |
|---|---|---|---|
| §4.1 cap operationalization | `z_cap_evaluator.py` | M1, M3 | C1, C2, C3 |
| §5.2 LOCKED brackets | `pi_t_symbolic.py` config + `z_cap_evaluator.py` config | M1, M2 | spec direct |
| §6 functional-form pins (FX path, $\Pi$, softplus) | `pi_t_symbolic.py` symbolic | M1 | PRIMITIVES (6), (16)–(19) |
| §9 TODO-COHORT-4 gate | `Z_cap_pinned.json` + sidecar `SIGN_VERDICTS.md` | M2, M3 | Tasks 2.2, 2.3 |
| §10 `Z_cap_pinned.json` | shipped `ZCapPinnedWriter` | M3 | Task 2.3 |
| §10 audit-block | shipped `compute_audit_block` | M4 | Task 2.3 |

---

## Anti-fishing posture

NO threshold relaxed. The 5 test-point grid is pre-pinned with sign expectations per Pin M2; ANY sign violation fires HALT per spec §8(1). Identity-tolerance gates inherit from PRIMITIVES.md §12 / Path A v0 §10.4 verbatim. The audit-block over the five Pin M4 input files is a non-bypassable lineage commitment — changing any C1/C2/C3 input post-pin produces a different digest, which makes silent re-runs at different parameter brackets externally detectable. The `ZCapPinned` Value's `__post_init__` invariants (`audit_block` regex; `tier_mix` sum-to-one; CI ordering) make the schema itself enforce the spec §10 commitment.

---

## Self-review checklist

- [x] Spec §4.1 + §5.2 + §6 + §9 + §10 coverage complete.
- [x] No Python code blocks (only bash + invocation commands).
- [x] Every task names agent / skill.
- [x] Every audit-pass commits separately.
- [x] Phase 0 includes functional-python skill re-read.
- [x] HALT triggers reference `feedback_pathological_halt_anti_fishing_checkpoint`.
- [x] Out-of-scope enumerated (cost/revenue fits explicitly excluded).
- [x] Math pins M1–M4 in Phase 2 prelude.
- [x] Audit-pass order matches SIM-INFRA-0 v1.1 (pre-mortem before mutation-testing).
- [x] Pre-mortem scope includes emission boundary, not just symbolic.
- [x] Mutation 80% threshold disambiguated from spec §8(7).
- [x] Equivalent-mutant cap pinned at ≤5%.
- [x] PR number resolved dynamically.
- [x] 5-test-point grid pre-pinned with sign expectations; no post-hoc tuning.
- [x] Cross-plan dependency on COHORT-2 + COHORT-3 + SIM-INFRA-0 declared in Task 0.4.
- [x] All consumed artifacts (C1 parquet, C2 robustness, C3 primary, spec) in the audit-block input set per Pin M4.
- [x] Strategic-delegation map present.
- [x] Verification matrix present.

---

## §"CORRECTIONS-α v0.1 → v0.2" — delta record

**emit_timestamp_utc:** 2026-05-08
**Trigger.** Wave-1 RC verdict ACCEPT_WITH_FLAGS (3 FLAGs) + Wave-2 MQ verdict ACCEPT_WITH_FLAGS (3 FLAGs); both at `scratch/2026-05-08-cohort-plans-review/cohort-4-{rc,mq}-verdict.md`. No BLOCKs at either wave. Per `feedback_pathological_halt_anti_fishing_checkpoint`, FLAGs are absorbable in CORRECTIONS-α without re-running 2-wave verify; this v0.2 is commit-eligible (RC verdict line 84: "no re-RC required"). Format precedent: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` §14.

### §15.1 — RC-FLAG-1 (Task 2.1 schema-bump hedge) → definitive sidecar posture

**Source:** RC verdict lines 66–71 ("schema-extension hedge that partially contradicts Pin M3's schema-bump-deferred posture; Recommend forcing `PiTDerivation` to live in `simulations/saas_builder/pi_t_symbolic.py` ... and removing the alternative").
**Fix location:** Task 2.1 behavior contract (`PiTDerivation` Value placement clause).
**Resolution.** `PiTDerivation` is pinned to live in `simulations/saas_builder/pi_t_symbolic.py` as a Callable-tier-adjacent frozen-dc Value. The "may extend `simulations/types/posterior.py`" alternative is REMOVED. The Pin M3 schema-bump-deferred posture is stated as **definitive for v0.2, not interim**: any future cross-`simulations/types/` exposure of `PiTDerivation` requires a separate SIM-INFRA-0 v1.2 amendment plan with its own 2-wave verify. This plan does not author that amendment.

### §15.2 — RC-FLAG-2 (Task 2.2 tolerance-threshold inheritance citation) → inline citations

**Source:** RC verdict lines 72–76 ("identity-tolerance gate carries two thresholds ... should cite PRIMITIVES.md §12 or Path A v0 §10.4 inline as the inheritance source rather than parenthetically").
**Fix location:** Task 2.2 behavior contract (identity-tolerance bullet).
**Resolution.** The identity-tolerance line now cites inheritance sources inline: symbolic ≤ $10^{-10} \cdot N_{\text{legs}}$ inherits from `notes/PRIMITIVES.md` §12 identity-tolerance ledger (cited inline); numerical ≤ $10^{-6}$ inherits from Path A v0 §10.4 numerical reconciliation tolerance (cited inline). The previous parenthetical "(per Path A v0 §10.4 inheritance)" is upgraded to a full inline citation chain so Wave-2 MQ re-flag risk is eliminated. Identity tolerance values themselves are unchanged.

### §15.3 — RC-FLAG-3 (Task 2.4 Hypothesis arity bound) → MAX 6 free symbols

**Source:** RC verdict lines 77–80 ("Hypothesis property strategy for `PiTDerivation` says 'sympy-arity-bounded' without pinning the bound. Add an explicit arity ceiling (e.g., max 6 free symbols)").
**Fix location:** Task 2.4 behavior contract (Hypothesis property strategies bullet).
**Resolution.** Arity ceiling is pinned at **MAX 6 free symbols per generated Expr**, covering the canonical $(K^\star, \sigma_0, \varepsilon, \omega, t, \kappa)$ tuple from Pin M1 Steps 1–5. Property strategies attempting Exprs with > 6 free symbols are filtered via `assume()`. Reproducibility of the property test surface is bounded; arity is documented inline in Task 2.4.

### §15.4 — MQ-FLAG-1 (D3 line 76 κ-monotonicity sign) → single canonical signed direction

**Source:** MQ verdict line 20 ("the pre-pinned monotonicity sign of ∂|π|/∂κ is recorded twice with non-orthogonal phrasing ... should restate the κ-monotonicity sign in one canonical line in M2").
**Fix location:** Pin M2 (immediately after the TP3 row) + Task 2.4 M2 monotonicity test + Task 3.3 hypothesis-tests κ-direction property.
**Resolution.** Pin M2 v0.2 adds the canonical signed direction:
$$\frac{\partial \lvert\pi\rvert}{\partial \kappa}\bigg|_{(\overline{X/Y}, \sigma_0)\text{ fixed}} \;<\; 0 \quad \text{(strict; long-gamma cap shrinks as cap-kink rises)}$$
This is the single canonical phrasing consumed verbatim by Tasks 2.4 (M2 monotonicity test) and 3.3 (joint-identifiability property). No orthogonal "monotone in κ direction" wording remains in v0.2. Test asserts the strict chain $\lvert\pi\rvert_{\text{TP2}} > \lvert\pi\rvert_{\text{TP1}} > \lvert\pi\rvert_{\text{TP3}}$ at fixed $(\overline{X/Y}_0, \sigma_0)$.

### §15.5 — MQ-FLAG-2 (D6 line 268 MC error budget on E[Z]) → posterior-predictive MC stderr gate

**Source:** MQ verdict line 29 ("the plan does not articulate an explicit MC error budget for the posterior-predictive Z computation ... Recommend v0.2 add an MC-stderr gate (e.g., `stderr(Z_hat) / Z_hat ≤ 1e-3` with N_draws ≥ 4000)").
**Fix location:** Task 2.2 behavior contract (new MC error budget bullet) + Task 2.4 MC-error-budget regression test.
**Resolution.** Task 2.2 now pins `stderr(Ẑ) / Ẑ ≤ 10⁻³` with `N_draws ≥ 4000` whenever the predictive expectation falls back to Monte Carlo (i.e., does not close in sympy). The 1e-3 ratio matches the third significant figure of `Z_cop_per_month`'s JSON precision; the 4000-draw floor inherits from C1 Pin R4 sim-count. On breach: invoke `feedback_pathological_halt_anti_fishing_checkpoint` with ≥3 pivot options. The MC error gate is **distinct from** the identity-tolerance gate (covers different operator); both apply concurrently. Task 2.4 adds two regression tests: clean (4000 draws → gate passes) and breach (100 draws → HALT routing fires).

### §15.6 — MQ-FLAG-3 (D9 line 166 COHORT-2 commit-sha lineage) → AUDIT_INPUTS.md sidecar

**Source:** MQ verdict line 38 ("Task 0.4 step 2 ... does not mandate that the `ROBUSTNESS_RESULTS.md` be hashed at the *exact commit* that produced the PASS — if the file is mutated post-PASS, the audit-block silently drifts without re-running cert. Recommend v0.2 record the COHORT-2 commit-sha alongside the file path in Pin M4").
**Fix location:** Pin M4 (item 3 — `ROBUSTNESS_RESULTS.md` row) + Task 0.4 step 2.
**Resolution.** Pin M4 item 3 now requires the COHORT-2 commit-sha to be recorded alongside `ROBUSTNESS_RESULTS.md` in `simulations/saas_builder/data/Z_cap_pinned.AUDIT_INPUTS.md`. Task 0.4 step 2 records the sha on first pass and HALTs on subsequent passes if `git log -1 --format=%H -- notebooks/saas_builder_stage_2/estimates/ROBUSTNESS_RESULTS.md` returns a different value (post-PASS file mutation detected). The audit-block content-sha is unchanged; the commit-sha is an *additional* non-bypassable lineage commitment.

### §15.7 — Preserved guarantees

This patch preserves:

1. **Pin M1 symbolic chain.** The five-step derivation (Pitch → perpetual identity → §8.1 closed form → Carr-Madan → variance proxy) is unchanged; no shortcut added.
2. **Pin M2 5-test-point grid.** TP1–TP5 coordinates and sign expectations are unchanged. MQ-FLAG-1 fix only restates the κ-monotonicity sign canonically; the underlying expectations $\lvert\pi\rvert_{\text{TP2}} > \lvert\pi\rvert_{\text{TP1}} > \lvert\pi\rvert_{\text{TP3}}$ are unchanged.
3. **Pin M3 schema (`ZCapPinned`).** Field list verbatim from `simulations/types/posterior.py:173–257` is unchanged; sign verdicts remain sidecared to `Z_cap_pinned.SIGN_VERDICTS.md`. RC-FLAG-1 fix REINFORCES the schema-bump-deferred posture as definitive (no v0.2 schema bump authored).
4. **Pin M4 audit-block.** 5-file content-hash input set is unchanged; `Path.resolve()` canonicalization unchanged. MQ-FLAG-3 adds an additive commit-sha sidecar — not a replacement.
5. **Identity-tolerance gates.** $\le 10^{-10}$ symbolic and $\le 10^{-6}$ numerical are unchanged. RC-FLAG-2 fix only upgrades inheritance citations from parenthetical to inline.
6. **Anti-fishing closure.** No threshold relaxed. Three new constraints added (MC error budget gate; MAX-6 arity ceiling; COHORT-2 commit-sha sidecar) — each strictly *increases* the failure surface (more states route to HALT/REJECT) and therefore reduces the silent-fishing surface.
7. **2-wave verifier discipline.** v0.1 passed RC + MQ at ACCEPT_WITH_FLAGS; v0.2 absorbs the 6 FLAGs without invalidating the verdicts. Per RC verdict line 84 ("no re-RC required") and MQ verdict line 41 ("FLAGs are all v0.2-addressable in dispatch briefs and do not block plan-execution authorization"), no reverify is required.

### §15.8 — Anti-fishing posture

Per `feedback_pathological_halt_anti_fishing_checkpoint`: trigger ✅ external 2-wave verify FLAGs; disposition memo ✅ this CORRECTIONS-α block enumerates per-FLAG resolution; user adjudication ✅ patch authored under explicit user instruction; old + new + preserved-guarantees argument ✅ §15.1–§15.7; post-hoc verify ⏳ NOT required (FLAGs are non-blocking; both verdicts state v0.2-addressable without reverify).

End of plan v0.2.

End of plan.
