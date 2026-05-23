# `simulations/` — Global FX-vol simulation infrastructure

This package hosts the global (cross-iteration) infrastructure for every
FX-vol simulation iteration in this repo: SaaS-builder Stage-2,
Pair D, dev-AI, and any future cohort.

It is the implementation of plan
`docs/plans/2026-05-07-sim-infra-0.md` (SIM-INFRA-0).

## Three-tier discipline (NON-NEGOTIABLE)

Per `~/.claude/skills/functional-python/SKILL.md`, every `.py` file in this
package belongs to exactly one tier. Misplacement is a Reality Checker BLOCK.

| Tier | Directory | Construct | Imports allowed from |
|------|-----------|-----------|----------------------|
| **Value** | `types/` | `@dataclass(frozen=True)` + `__post_init__` validation only. Accessors are FREE FUNCTIONS, not methods. | stdlib + numpy + typing only |
| **Callable** | `modules/` | `@dataclass(frozen=True)` + `__call__`. Config in fields, logic in `__call__`. Stateless. | `simulations.types` only |
| **IO Boundary** | `utils/` | Class with `__init__`. The ONLY place mutable state lives. Filesystem / network / opaque external APIs. | `simulations.types` (Pydantic allowed transiently for JSON validation) |

`typing.Protocol` is allowed — for cross-tier interfaces it lives in
`types/` and is implemented in `modules/` or `utils/`.

No inheritance other than `Protocol` (and stdlib `Exception` subclasses).

## `__init__.py` policy (per Phase 1 reconciliation §2.9)

Every `__init__.py` declares an explicit `__all__: list[str]`. No star
imports. No transitive re-exports across tier boundaries — cross-tier
consumers fully-qualify imports
(`from simulations.types.distributions import TruncParetoParams`).

This makes the Reality Checker tier-import grep mechanically reliable:
violations show up as direct submodule imports across tiers.

## Extension model — per-iteration peers without inheritance

Per Phase 1 reconciliation §2.7 + §2.8, future iterations may add a peer
folder beside the global ones:

```
simulations/
├── types/           ← global Value types
├── modules/         ← global Callables
├── utils/           ← global IO boundaries
├── pair_d/
│   ├── types/       ← per-iter Values (optional)
│   ├── modules/     ← per-iter Callables
│   └── utils/       ← per-iter IO (rare)
└── saas_builder/    ← (this iteration uses globals only; no per-iter types/)
```

When a per-iteration Callable needs to extend a global Callable, use one of
three patterns (in preference order). **Inheritance is forbidden.**

1. **Wrap (default).** Per-iter Callable holds the global Callable as a
   frozen field and delegates inside `__call__`.
2. **Protocol-based polymorphism.** Per-iter Callable implements the same
   `typing.Protocol` declared in `simulations/types/`.
3. **Higher-order constructor.** A free function returns a configured
   frozen-dataclass.

The SaaS-builder Stage-2 iteration uses globals only (no
`simulations/saas_builder/types/`).

## Phase ordering

This is implemented per the SIM-INFRA-0 plan in four sub-tasks:

- **Task 2.1** — `simulations/types/` (Value tier) — THIS COMMIT.
- **Task 2.2** — `simulations/modules/` (Callable tier) — depends on 2.1.
- **Task 2.3** — `simulations/utils/` (IO Boundary tier) — depends on 2.1.
- **Task 2.4** — `simulations/tests/` (strategies + math-pin tests).

## Math pins (Phase 2 prelude — see plan §"Phase 2 prelude")

- **M1.** TruncPareto α-floor (α ≥ 1.5 for SaaS-builder cohort, spec §8(6))
  binds at the **sampler Callable** in `modules/`, NOT on
  `types/TruncParetoParams` (which accepts any α > 0). See
  `types/distributions.py` docstring contract.
- **M2.** Softplus β-tightness (L¹ deviation < 1e-3·κ on [0, 2κ]) is
  enforced at the **regularizer Callable** in `modules/`. The free
  function `tightness_l1_deviation` in `types/distributions.py` is the
  computational primitive.
- **M3.** Blended `p_t` formula (spec §5.1) lives in `modules/`.
- **M4.** Parquet + JSON column schemas (spec §10) live in `utils/` as
  TypedDict row schemas; the corresponding Value containers
  (`PosteriorDraws`, `MonthlyCDF`, `ZCapPinned`) live in `types/`.
- **M5.** FX path closed form (PRIMITIVES (6) + (8)) lives in `modules/`;
  the parameter Value `FXPathParams` lives in `types/`.

See each tier's `README.md` for detail.

---

## User manual — how to read and interpret the work

This section is the on-ramp for anyone (future contributor, supervisor,
Stage-3 implementer) opening the repo cold. It maps the artifacts to
their reading order and explains how to interpret what comes out of the
pipelines.

### Reading order

1. **`docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`** —
   read first. Canonical Stage-2 deliverable. §1 is the executive
   verdict; §8 is the plain-language product-surface translation;
   §9 is the Stage-3 readiness checklist.
2. **`docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md`** (spec
   v1.2.1) — pre-registration lock. Read §5 (the (Y, M, X) decomposition
   + cost model), §6 (functional-form table including S_t pin), §8
   (gates and HALT triggers), §10 (parquet schemas), and §15
   (CORRECTIONS-α audit-trail blocks v1.0 → v1.2.1).
3. **`notes/PRIMITIVES.md`** — math anchors. §4.2 is the saas-cohort
   instantiation; §6, §7, §8, §10 contain the Δ closed forms, variance
   proxy, and Carr-Madan replication referenced by C2 and C4.
4. **`notes/SaaS_Builders_AI_NativeBuilders.md`** — saas-cohort-specific
   PRIMITIVES extension. Currently imports primitives + cohort
   parameterization.

### Cohort decomposition (where the code lives)

```
SIM-INFRA-0 (this package)            simulations/{types,modules,utils}/
    │                                  226 tests, 99% coverage
    │
    ├── COHORT-1 — T1 cost posterior   simulations/saas_builder/{priors,
    │                                  model, diagnostics, emit}.py
    │
    ├── COHORT-2 — T2 sign cert        simulations/saas_builder/cohort_2/
    │
    ├── COHORT-3 — Υ_t form selection  simulations/saas_builder/cohort_3/
    │
    └── COHORT-4 — π(t) + Z cap pin    simulations/saas_builder/cohort_4/
```

### Interpreting cohort outputs

Each cohort produces a verdict artifact under `simulations/saas_builder/data/`
(gitignored; regenerated by running the corresponding driver script).

- **`Z_cap_pinned.json` (schema v1.1)** — canonical Stage-2 outcome.
  Fields: pinned cap value, 95% CI bounds, 5-element `sign_verdicts`
  array (per-test-point z, ci_lo, ci_hi, sign, identity_residual),
  audit_block sha256 over upstream parquet inputs (deterministic;
  changes if any upstream parquet changes).
- **`gate_verdict.json`** — C2 primary-regime sign certification.
  24-bracket evidence array with `sign_strictly_negative` per bracket
  + aggregate `n_sign_violations`. Verdict alphabet `PASS|WEAK|MARGINAL
  |FAIL|INDISTINGUISHABLE` per spec §10.
- **`PRIMARY_RESULTS.md`, `ROBUSTNESS_RESULTS.md`** — human-readable
  C2 narratives. PRIMARY is the gate verdict; ROBUSTNESS is the
  bank-spread overlay (walled off; informational only).
- **`revenue_form_verdict.json`** — C3 PSIS-LOO-CV outcome. ELPD ± SE
  per form + verdict. Currently INDISTINGUISHABLE (Δelpd/SE = 1.67
  below 2.0 threshold).
- **`_AUDIT.json`** — C1 posterior diagnostic block. All 6 gate metrics
  at emission time + audit_block sha256.

### Verdict semantics

- **24/24 PASS in primary regime** — pre-registered sign expectation
  holds throughout the spec §5.2 parameter family. Strong.
- **24/24 PASS in bank-spread overlay** — sign holds even under
  bank-imposed FX-spread frictions. Stronger.
- **5/5 sign-cert TPs PASS with strictly positive 95% CI lower bound**
  — cohort cap is positive at multiple FX bracket points with
  credible-interval-level confidence under the prior + model.
- **INDISTINGUISHABLE on C3** — data does not statistically distinguish
  the three Υ_t forms; spec-pinned Det+churn is used downstream;
  HALT-on-flip safeguard fired no flip vs the legacy prior.

### Audit trail

31 verdict files across 7 audit cycles in `scratch/2026-05-08-*/` and
`scratch/2026-05-09-*/`. Format per cycle:

- `rc-verdict.md` (Reality Checker) — empirical claims vs committed
  code/artifacts/spec
- `mq-verdict.md` (Model QA Specialist) — methodology integrity
  (math, identification, anti-fishing posture)
- `cr-verdict.md` (Code Reviewer) — code quality

Each verdict defaults to REJECT and lists BLOCKs (must-fix) and FLAGs
(non-blocking). Forward-fix versions (`-v0.3`, `-v0.4`, `-v1.2.1`)
document remediation cycles.

### Reproducing the verdict

```bash
# 1. Setup
uv venv --python 3.13 && source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Run cohorts in dependency order
uv run python scripts/run_cohort1_emit.py    # ~5 min — produces synthetic_tau_t parquets
uv run python scripts/run_cohort2_emit.py    # <1 sec — produces gate_verdict.json
uv run python scripts/run_cohort3_emit.py    # ~30 sec — produces revenue_form_verdict.json
uv run python scripts/run_cohort4_emit.py    # <1 sec — produces Z_cap_pinned.json

# 3. Verify reproducibility
uv run pytest simulations/tests/             # 423/423 passing
```

The audit_block sha256 in `Z_cap_pinned.json` is deterministic across
runs (modulo PyMC's RNG state). If sha256 differs, an upstream parquet
has changed.

### Methodology corrections during the cycle (read §6 of verdict memo for detail)

1. **C1 v0.3 → v0.4 marginalization** — Categorical-Gibbs over 1000
   builders failed §8(8) ESS gate. Marginalized 3 discrete latents
   analytically; pure NUTS now; 78× speedup; ESS scaled 38 → 338,540
   after Phase 2 N_draws bump.
2. **C2 v0.2 → v0.3 bracket re-orientation** — original (ε, ω) sweep
   mis-oriented vs spec §5.2 parameter family. Re-oriented to 24-cell
   parameter grid; deterministic PASS/FAIL test fixtures replaced
   tautological assertions.
3. **C4 v0.2 → v0.3 anti-fishing remediation** — fabricated `1/κ` factor
   in π(t) caught by independent MQ. Re-derived from PRIMITIVES; (X̄/Ȳ)²
   restored; M2 sign expectation amended pre-registered.

### Methodology lessons memorialized

- `memory/feedback_self_grading_vs_independent.md` — independent-audit
  pattern (17+ BLOCKs caught only by independent verifies)
- `memory/feedback_post_hoc_fit_anti_fishing_pattern.md` — C4 1/κ case
  study with detection heuristics (free-symbol audit + derivation-anchor
  citation check)
- `memory/feedback_worktree_agents_no_subdispatch.md` — Claude Code
  harness invariant; orchestration must run from main session for
  multi-phase plans
