# cadCAD Backend Documentation — Functional-Python Translation Layer

**Status:** v0.1 (drafted 2026-05-16 as the design substrate for `simulations/cadcad/`)
**Authority:** This doc + the working paper at `docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex` §6 (especially §6.2 state-vars + 6 PSUBs) + Appendix C (forward-looking implementation spec).
**Skill chain enforced:** `functional-python`, `contract-docstrings`, `tighten-types`, `hypothesis-tests`, `pre-mortem`.
**Audience:** any agent or human dispatched to read, write, or review `simulations/cadcad/*.py`.

---

## §0 Purpose

cadCAD ([cadCAD-org/cadCAD](https://github.com/cadCAD-org/cadCAD)) is a Python library for complex-adaptive dynamical systems. It defines a stateful simulation loop with state variables, policies, partial state update blocks (PSUBs), and system configurations. The library's idioms are **mutation-heavy and weakly typed by default**: untyped `dict` for states, list-of-dict accumulation for history, policies returning unconstrained signal dicts.

This is incompatible with the Abrigo repo's discipline (per `~/.claude/skills/functional-python/SKILL.md` + `memory/feedback_check_functional_python_skill_first.md`):

- **Frozen dataclasses only** — no mutable state holders.
- **Free pure functions** — no methods carrying state.
- **Full typing strictness** — no `Any`, no untyped `dict` at module surfaces.
- **No inheritance** — except stdlib `Exception` and `typing.Protocol`.
- **Composition over inheritance** — closures + frozen-dc + `Protocol` for polymorphism.

We therefore do not consume cadCAD's runtime directly. We consume its **architectural primitives** (state variables, PSUBs, system configurations) re-expressed under the functional-python regime, and we build the simulation loop ourselves as a thin orchestration of free functions.

This doc is the translation layer between cadCAD's stated primitives and the project's functional-python implementation. Every PSUB committed to `simulations/cadcad/psubs.py` MUST conform to the patterns in this doc.

---

## §1 Translation table — cadCAD primitive ↔ functional-python equivalent

| cadCAD primitive | cadCAD idiom (rejected) | Project equivalent (mandatory) |
|---|---|---|
| **State variable** | Untyped `dict` entry; mutated in place via `state["x"] = ...` | Field on a `@dataclass(frozen=True)` `State` container; replaced via `dataclasses.replace(state, x=...)` |
| **Initial state** | `genesis_states = {"x": 0.0, ...}` (untyped) | `INITIAL_STATE: Final[State] = State(x=0.0, ...)` constructed once, validated via `__post_init__` |
| **System config / params** | `system_params = {"sigma": [0.25, 0.30]}` (untyped, list-of-sweep semantics) | `@dataclass(frozen=True)` `Config` container; sweep ranges are explicit `tuple[Config, ...]` |
| **Policy function** | `def p(params, substep, state_history, prev_state) -> dict[str, Any]: return {"signal": ...}` | `def policy_x(state: State, config: Config) -> SignalX:` — typed input, typed return (`SignalX` = frozen-dc named record), pure |
| **PSUB function** | `def s(params, substep, state_history, prev_state, policy_input) -> tuple[str, Any]: return ("x", new_value)` | `def psub_x_update(state: State, signal: SignalX, config: Config) -> StateDelta:` — returns a `@dataclass(frozen=True)` `StateDelta` carrying only the fields it touches |
| **Partial state update block** (composing policies + PSUBs) | `{"policies": {"p": p}, "variables": {"x": s, "y": s2}}` dict-of-dicts | `PSUB_<n>: Final[tuple[...]]` — a `Protocol`-typed callable taking `(State, Config)` and returning `State` (the post-block state). Composition is via function call; no dict registry. |
| **State history** | Mutable list of state dicts, appended in place | `Trajectory` frozen-dc holding numpy arrays of per-step values (one array per state field) |
| **Simulation execution** | `executor = Executor(exec_context, configs)` → mutable iteration | `def run_simulation(config: Config) -> Trajectory:` — free function, pure (modulo deterministic RNG state per Pin Z1.2) |
| **system_config_dict + run_config** | `{"N": 1, "T": range(100), "M": params}` | A single frozen-dc `Config` argument to `run_simulation` |
| **Logging** | Print-side-effect within PSUBs | Logs emitted to a frozen-dc `RunLog` returned alongside `Trajectory` from the IO Boundary tier |

---

## §2 Forbidden cadCAD idioms and their functional replacements

### Idiom 1 — Mutable state history list

cadCAD pattern:
```python
state_history.append(prev_state.copy())
prev_state["x"] = new_x
```

This violates frozen-dc + composition discipline. Even if `state_history` is treated as append-only, the elements are shallow-copied dicts whose values can drift.

**Functional replacement.** A `Trajectory` frozen-dc holds numpy arrays of per-step values. The simulation loop pre-allocates the arrays (length `n_steps + 1`) and writes to slot `j+1` from PSUB outputs at step `j`. The pre-allocated buffer is functionally indistinguishable from a series of immutable snapshots: each slot is written exactly once, and the `Trajectory` is constructed at the end of the loop via `Trajectory(X_path=..., ...)`.

The simulation loop body looks like:

```python
# Inside run_simulation; loop body is the only "mutable" surface and only for
# pre-allocated numpy arrays that are never reshaped or re-indexed.
for j in range(n_steps):
    state_j = State(step=j, X=X_path[j], S=S_path[j], ...)
    state_j1 = compose_all_psubs(state_j, config, rng)
    X_path[j + 1] = state_j1.X
    S_path[j + 1] = state_j1.S
    # ... one assignment per field; no in-place state mutation
```

The state dataclass is reconstructed per step from indexed array reads; the arrays themselves are append-only writes (each slot exactly once). This is **conceptually pure** even though numpy in-place writes are used for efficiency. Document this in the function docstring.

### Idiom 2 — Untyped policy dicts

cadCAD pattern:
```python
def cost_policy(params, substep, state_history, prev_state):
    return {"cost_delta": prev_state["x"] * params["rate"]}
```

The return type `dict[str, float]` is implicit and unenforced; consumers index by string key with no type discipline.

**Functional replacement.** Each policy returns a `@dataclass(frozen=True)` signal record:

```python
@dataclass(frozen=True)
class CostSignal:
    """Output of the cost-trajectory policy at step j.

    Consumed by psub_3_cost_advance to compute C_{j+1}.
    """
    token_demand: float
    api_rate: float
    fx_rate: float

def cost_policy(state: State, config: Config) -> CostSignal:
    """Pure: state + config → typed signal."""
    return CostSignal(
        token_demand=state.exogenous_demand,
        api_rate=config.api_rate_card_at_step(state.step),
        fx_rate=state.X,
    )
```

The PSUB consumer signature `def psub_3(..., signal: CostSignal, ...) -> StateDelta` is now type-checked end-to-end.

### Idiom 3 — In-place state mutation inside PSUBs

cadCAD pattern:
```python
def update_x(params, substep, state_history, prev_state, policy_input):
    return ("x", prev_state["x"] + policy_input["delta"])
```

The return tuple `("x", new_value)` is in-place semantics: cadCAD's framework overwrites the field on `prev_state`.

**Functional replacement.** Return a `StateDelta` frozen-dc carrying only the touched fields:

```python
@dataclass(frozen=True)
class FXAdvanceDelta:
    """Field delta emitted by psub_1_fx_advance.

    Only X is touched; other state fields are unchanged.
    """
    X_new: float

def psub_1_fx_advance(
    state: State, config: Config, fx_path: NDArray[np.float64]
) -> FXAdvanceDelta:
    """..."""
    return FXAdvanceDelta(X_new=float(fx_path[state.step + 1]))
```

The orchestrator (`run_simulation`) is responsible for applying the deltas:

```python
def _apply_fx_delta(state: State, delta: FXAdvanceDelta) -> State:
    return dataclasses.replace(state, X=delta.X_new)
```

This separation ensures the PSUB is pure (no state-touching outside the explicit delta), and the orchestrator's `_apply_*_delta` helpers are themselves pure free functions.

### Idiom 4 — Policy + PSUB co-located in one dict

cadCAD pattern:
```python
psub_1 = {
    "policies": {"p_fx": fx_policy},
    "variables": {"X": update_X, "Y": update_Y},
}
```

Two policies and two variables share a dict namespace; ordering and composition semantics are implicit.

**Functional replacement.** Each PSUB is a single named free function that internally calls its constituent policies (also free functions) and constructs the post-PSUB `State` either via `dataclasses.replace(state, ...)` or via the `State(...)` constructor directly (both are equivalent — the constructor re-validates `__post_init__` invariants from scratch, which is the stronger of the two; v0.1 Phase 1 driver uses the constructor pattern per Wave-1 MQ-F1 disposition). No dict registry. Composition order is explicit in the function body:

```python
def psub_1_fx_advance(
    state: State, config: Config, fx_path: NDArray[np.float64]
) -> State:
    """FX-path-advance PSUB (§6.2 PSUB-1 of the paper).

    Composes the FX policy and applies its delta to state.X.
    """
    # In Phase 1, the FX policy is trivial: read pre-sampled path
    delta = FXAdvanceDelta(X_new=float(fx_path[state.step + 1]))
    return _apply_fx_delta(state, delta)
```

Composition across all six PSUBs in the simulation loop is then a function call chain:

```python
state_j1 = psub_6_ratchet(
    psub_5_wage_drain(
        psub_4_portfolio_update(
            psub_3_cost_advance(
                psub_2_sigma_t_update(
                    psub_1_fx_advance(state_j, config, fx_path),
                    config,
                    X_window,
                ),
                config,
                exogenous_signal,
            ),
            config,
        ),
        config,
    ),
    config,
)
```

This is verbose intentionally — the composition order is the cadCAD execution semantics, made explicit and audit-traceable. If a future PSUB needs to be inserted or skipped, the change is a single function call edit, not a registry mutation.

### Idiom 5 — `params` as a sweep range

cadCAD pattern:
```python
system_params = {"sigma": [0.25, 0.30, 0.35]}
# cadCAD sweeps over the cartesian product
```

This couples parameter sweeps to the simulation primitive itself, mixing single-run semantics with multi-run.

**Functional replacement.** Sweeps are constructed explicitly at the orchestrator level:

```python
def sweep_simulation(
    base_config: Config,
    sigma_grid: tuple[float, ...],
) -> tuple[Trajectory, ...]:
    """Run the simulation across a sweep of sigma values.

    Each Trajectory is produced by an independent run_simulation call.
    No shared state between runs; each run carries its own audit_block.
    """
    return tuple(
        run_simulation(dataclasses.replace(base_config, sigma=s))
        for s in sigma_grid
    )
```

Single-run semantics (`run_simulation`) remain clean; multi-run is a separate composer.

### Idiom 6 — Implicit RNG state

cadCAD pattern:
```python
import random
random.seed(42)  # global side effect
```

Global RNG state violates Pin Z1.2 determinism (any code path running between seeding and consumption can perturb state).

**Functional replacement.** Pin Z1.2 mandates `numpy.random.default_rng(seed)`. Pass the `Generator` instance into PSUB-1 (the only stochastic PSUB after pre-sampling); other PSUBs are deterministic. For our Phase 1 design, FX path is pre-sampled at simulation initialization, so the RNG is consumed exactly once at `_FxPathPreSampler` construction. The simulation loop is then strictly deterministic.

```python
def run_simulation(config: Config) -> Trajectory:
    """..."""
    rng = np.random.default_rng(config.rng_seed)
    fx_path = _pre_sample_fx_path(config, rng)  # consumes rng once
    # ... loop is deterministic given fx_path
```

---

## §3 Per-PSUB docstring template (`contract-docstrings` skill)

Every PSUB function in `simulations/cadcad/psubs.py` MUST cover the eight content elements below — verbatim subsection headings are preferred but narrative-prose coverage is also acceptable provided every element is locatable (Wave-1 RC-F2 disposition softened the v0.1 "must match this template" to "must cover the content elements in some form"):

```python
def psub_<N>_<role>(
    state: State,
    config: Config,
    <additional_typed_input>: <Type>,
) -> State:
    """<one-line role statement matching paper §6.2 PSUB-<N>>.

    Mathematical contract: <one or two sentences citing the paper eq./pin>.

    Inputs:
        state: <which State fields it reads; cite eq. labels if applicable>.
        config: <which Config fields it reads>.
        <additional>: <typed input contract; cite source>.

    Returns:
        Post-PSUB State. Only the following fields are mutated relative
        to the input state: <list of field names>. All other fields are
        preserved verbatim (via dataclasses.replace).

    Errors raised:
        CadCADStateError: if <input invariant violated>.
        <Other>: <when raised>.

    Errors NOT caught (propagate from callees):
        <list of upstream errors that can propagate without being
        re-wrapped — e.g., SDEParameterError from the stochastic_fx
        layer>.

    Pin: <Pin Zx reference if applicable, e.g., Pin Z1.2 determinism>.

    Implementation pointer: <paper §6.2 sub-bullet that this PSUB
    instantiates>.
    """
    ...
```

This template is enforced by review at Wave-1; deviations are flagged.

---

## §4 Tier-purity rules for `simulations/cadcad/`

Three-tier discipline per `CLAUDE.md` §`simulations/ discipline` and the precedent established by `simulations/stochastic_fx/`:

| File | Tier | Allowed imports |
|---|---|---|
| `simulations/cadcad/types.py` | Value | stdlib (`dataclasses`, `typing`, `math`); `numpy`; `simulations.stochastic_fx.types` (for `PathEnsemble` if needed) |
| `simulations/cadcad/psubs.py` | Callable | stdlib; `numpy`; `simulations.cadcad.types`; `simulations.cadcad._errors`; `simulations.stochastic_fx` (PathGenerators, `variance_proxy.recompute_sigma_t`) |
| `simulations/cadcad/driver.py` | IO Boundary | All of the above + `hashlib` + `json` + `pathlib` |
| `simulations/cadcad/emit.py` (Phase 2+) | IO Boundary | All of the above + `pyarrow` + `scipy.stats` |
| `simulations/cadcad/_errors.py` | Value | stdlib only; subclass `simulations.stochastic_fx._errors.StochasticFXError` for hierarchy continuity |

**Forbidden cross-tier imports**:
- `types.py` ↛ `psubs.py` or `driver.py` (Value tier is leaf)
- `psubs.py` ↛ `driver.py` or `emit.py` (Callable tier doesn't reach IO)
- Anything in `simulations/cadcad/` ↛ `simulations/saas_builder/cohort_*/` (the cohort packages are domain-specific; cadCAD is the dynamic-system layer over the stochastic-fx substrate, NOT over cohort-specific code)

**Allowed cross-package import**: `simulations.cadcad.*` may import `simulations.stochastic_fx.*` at module top (lazy imports inside function bodies are also fine for forward references).

**Runtime-vs-code-level tier purity (Wave-1 RC-F3 disposition).** Tier purity is enforced **at the source-text level** (the imports declared at module top in each `.py` file), NOT at the `sys.modules` level after package import. The package `__init__.py` eagerly re-exports symbols from `types`, `psubs`, and `driver`, so a user who does `import simulations.cadcad` (or even `import simulations.cadcad.types`) will see all three submodules loaded in `sys.modules`. This is benign: each submodule's own AST imports remain tier-pure. Reviewers probing tier purity should run the AST-based check against each `.py` file in isolation rather than scanning `sys.modules` after a package import.

---

## §5 Determinism + audit_block recipe

Per Pin Z1.2 (paper §1.4 + spec v0.5 §5), every simulation run produces a deterministic audit_block. Two recipe variants are admissible; either preserves Pin Z1.2 strong-form determinism. The v0.1 implementer chose Variant B per Wave-1 RC-F1 disposition.

### Variant A — explicit-LE-seed (mirrors `simulations/stochastic_fx/generators.py` convention)

```python
def _compute_audit_block(
    canonical_config_json: str,
    rng_seed: int,
    X_path: NDArray[np.float64],
    S_path: NDArray[np.float64],
    # ... all other path arrays in fixed order ...
) -> str:
    """Deterministic SHA-256 audit_block (Pin Z1.2)."""
    hasher = hashlib.sha256()
    hasher.update(canonical_config_json.encode("utf-8"))
    hasher.update(rng_seed.to_bytes(8, "little"))   # explicit LE-byte seed step
    for path_array in (X_path, S_path, C_path, P_path, W_path, R_path):
        hasher.update(path_array.tobytes())
    return hasher.hexdigest()
```

### Variant B — seed-inside-canonical-JSON (cadCAD convention, v0.1 driver implementation)

```python
def _compute_audit_block(
    canonical_config_json: str,  # rng_seed is already a field inside this JSON
    X_path: NDArray[np.float64],
    S_path: NDArray[np.float64],
    # ... all other path arrays in fixed order ...
) -> str:
    """Deterministic SHA-256 audit_block (Pin Z1.2)."""
    hasher = hashlib.sha256()
    hasher.update(canonical_config_json.encode("utf-8"))
    # rng_seed is part of canonical_config_json via json.dumps(asdict(config), sort_keys=True)
    for path_array in (X_path, S_path, C_path, P_path, W_path, R_path):
        hasher.update(path_array.tobytes())
    return hasher.hexdigest()
```

**Why Variant B is acceptable for cadCAD.** The `Config` frozen-dc carries the seed as a field; `json.dumps(asdict(config), sort_keys=True)` produces a stable byte serialization that includes the seed in a deterministic position. Hashing the seed a second time as 8-byte LE adds no information; omitting it preserves Pin Z1.2 strong-form determinism while reducing recipe duplication.

**Variant A is preserved** for backward-compatibility with `simulations/stochastic_fx/generators.py` where `canonical_params_json` historically did NOT include the seed (the seed was a sibling argument to the hashing function, not a field on the Parameters dataclass).

Validation: at the end of `run_simulation`, the orchestrator runs the recipe AND a re-run cross-check (same config + same rng_seed produces bit-exact identical audit_block). This is the Pin Z1.2 strong-form test (cross-process determinism — see Wave-2 RC R5 + Phase 1 RC-R2 / MQ-MQ4).

---

## §6 Phase plan for `simulations/cadcad/`

### Phase 1 (in flight at dispatch time)
- `types.py` (State, Config, Trajectory frozen-dcs)
- `psubs.py` PSUB-1 (FX advance), PSUB-2 (σ_T accumulator), PSUB-6 (ratchet)
- `psubs.py` PSUB-3, 4, 5 as stubs raising `NotImplementedError`
- `driver.py` `run_simulation` orchestrator
- `_errors.py` `CadCADError` hierarchy
- Tests + audit_block determinism + tier-purity verification

### Phase 2 (after Phase 1 lands + cost-factor spec v0.2.1 clears Wave-2)
- PSUB-3 (cost-trajectory advance) — couples to AI-cost-factor spec
- PSUB-4 (replicating-portfolio update) — couples to cohort_5_strip
- PSUB-5 (wage-premium drain)
- `emit.py` IO Boundary tier (parquet trajectory + JSON config + MD summary)
- Cross-PSUB integration tests

### Phase 3 (after Phase 2 lands)
- Notebook companion via Analytics Reporter (final-simulation notebook per `memory/project_post_stochastic_fx_plan_unlocks.md`)
- Figures + numerical sensitivity sweeps + LaTeX-rendered math
- Paper-update pass: §7 results section gets a "cadCAD simulation results" subsection

### Out of scope (deferred indefinitely)
- Multi-agent cadCAD (multiple cohorts as parallel agents) — current design is single-agent
- Network-stratified state variables — current state is six scalars
- Real-time data feeding (the `X_t` is sampled from the SDE generators, not from live FX feeds) — that's a separate "live-execution" sub-project

---

## §7 Review protocol for `simulations/cadcad/*.py`

Wave-1 RC + MQ Delphi-independent per `memory/feedback_block_protocol_end_to_end_validated.md` and the established stochastic-fx pattern. RC focus areas:

- Tier purity (per §4 above)
- audit_block determinism (cross-process bit-equality)
- §3 docstring template compliance
- §2 forbidden-idiom absence (grep-based audit)

MQ focus areas:

- State transitions are pure (frozen-dc + `dataclasses.replace` only)
- PSUB composition order matches paper §6.2 exactly
- Trajectory arrays' per-slot writes occur exactly once (no double-write, no skip)
- Pin Z1.2 determinism: cross-process re-run bit-exact

Both reviewers MUST cite this backend doc (§<n>) when flagging deviations, so dispositions trace back to the design substrate rather than to ad-hoc preferences.

---

## §8 Related references

**Project-internal:**
- `docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex` §6, App C — primary design spec
- `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.1 — downstream consumer (Phase 2 coupling target)
- `simulations/stochastic_fx/` — the precedent package for functional-python + three-tier discipline
- `memory/project_post_stochastic_fx_plan_unlocks.md` — sequencing context
- `memory/feedback_check_functional_python_skill_first.md` — read the skill from disk before code-touching
- `memory/feedback_specialized_agents_per_task.md` — foreground-orchestrates-never-authors

**External:**
- `~/.claude/skills/functional-python/SKILL.md` — paradigm enforcement
- `~/.claude/skills/contract-docstrings/SKILL.md` — docstring template authority
- `~/.claude/skills/tighten-types/SKILL.md` — type-strictness audit
- `~/.claude/skills/hypothesis-tests/SKILL.md` — property-test generation
- `~/.claude/skills/pre-mortem/SKILL.md` — failure-mode foresight

**Library:**
- cadCAD: https://github.com/cadCAD-org/cadCAD — for primitive concepts ONLY. We do NOT consume the library at runtime; the simulation loop is built from free functions following this doc's translation patterns.

---

## §9 Document maintenance

This doc is **substrate**, not implementation. It changes only when:

1. A new cadCAD primitive becomes relevant (e.g., if Phase 3 introduces multi-agent semantics, §1 gets a new row)
2. The skill chain changes (e.g., a new skill is added that affects PSUB authoring)
3. A forbidden idiom from §2 is observed in a Wave-1 review (the idiom gets added to §2 with the disposition trail)

Edits to this doc require a Wave-1 RC review of the diff (NOT a full Wave-1 — this is doc, not code) because the doc is itself a contract surface that implementation agents read and reference.

Version bumps: this is v0.1. v0.2 will land when Phase 2 PSUBs converge their cost-factor + portfolio coupling details.
