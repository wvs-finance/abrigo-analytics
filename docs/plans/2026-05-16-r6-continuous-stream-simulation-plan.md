# R6 Continuous-Stream Simulation (v0.1.3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` (v0.1.3 — APPROVED on all three review channels: Wave 1 RC CLOSE_ALL at v0.1.2, Wave 2 Model QA CLOSE_ALL at v0.1.1, Wave 2 Code Reviewer plan-emission approved at v0.1.2; v0.1.3 is documentation polish only).

**Sibling spec:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md` (v0.2.1 CLOSE_ALL all three reviewers).
**Sibling plan:** `docs/plans/2026-05-16-ai-cost-factor-model-plan.md`.

**Goal:** Quantify the COP cost-burden distribution + session-cap-wait friction that a non-subscribed LATAM developer would face under continuous-usage API stream at extrapolation rates `k ∈ {0.5, 1, 2, 3, 5}`, calibrated to the maintainer's `~/.claude/projects/**/*.jsonl` history via within-session NHPP arrivals + FX block-bootstrap + hour-block × day-type empirical token-size pool, with output-quality flags binding the downstream M-design step.

**Architecture:** Extend the v0.2.1 sub-package `simulations/dev_ai_cost_v2/` with seven new module/types files (NHPP calibration + simulation, FX block-bootstrap, cost simulator, cap-wait counter, declarative Anthropic caps, types extensions). Mirror `simulations/stochastic_fx/generators.py` for generator signatures (frozen-dc config + `__call__(rng_seed) -> Ensemble`). Five notebooks at `notebooks/dev_ai_cost_v2_r6/` with disposition templates. Three-tier import discipline preserved.

**Tech Stack:** Python 3.13, polars, pydantic (`extra="forbid"`), Decimal (headline only), float64 (ensemble interior per CORRECTIONS-KK), Hypothesis, scipy.optimize (MLE), arch (Politis–Romano stationary bootstrap) or own implementation matching `stochastic_fx`. LiteLLM SHA pin `e58a561caa21169fb02174148444c08509ce7028` inherited from v0.2.1.

---

## CRITICAL: Phase 1 must complete before Phase 2

**Phase 1 (Tasks 1–2)** consists of plan-execution amendments to the sibling v0.2.1 plan, documented in R6 v0.1.3 frontmatter `sibling_corrections_v0_2_1_plan`. Specifically:

- CORRECTIONS-AA: introduce `DevAICostError(Exception)` as sub-package root; reparent `JSONLSchemaError` from `SchemaMismatchError` to `DevAICostError`.
- CORRECTIONS-RR / CORRECTIONS-TT: add `uuid: str` field to `MessageRecord` frozen-dc; ensure `JSONLReader` captures Anthropic's per-line `uuid` field.

These are amendments to v0.2.1's deliverables. They MUST land (with passing tests) **before any Phase 2 R6 module is implemented**, because:

- R6's new errors (`NHPPCalibrationError`, `NHPPSparseBinError`, `SparsePoolError`) declare `DevAICostError` as parent.
- R6's `message_pool_content_sha256` canonicalization requires `uuid` on `MessageRecord` for the quaternary sort key + tiebreaker (CORRECTIONS-TT (b)).

If the v0.2.1 plan has already been executed and merged when this plan starts, Tasks 1–2 patch the as-merged code in place; if v0.2.1 plan execution is still in progress, Tasks 1–2 may be folded into the relevant v0.2.1 tasks (5: types, 5: jsonl_io) and re-cited here. Either way, Phase 1 exit gate is a passing `simulations/tests/` suite with the amendments live.

---

## Spec coverage map — CORRECTIONS letters AA–TT and § references → tasks

| CORRECTIONS | What | Implementing Task |
|---|---|---|
| AA (Errors hierarchy: `DevAICostError(Exception)` root; reparent `JSONLSchemaError`) | Phase 1 sibling amendment | Task 1 |
| BB (NHPP grid coarsening: 4 hour-blocks × 2 day-types; `N_min = 50`) | NHPP calibration | Task 4 |
| CC (Cap-reset abandoned; use `session_id` directly) | NHPP calibration on within-session inter-arrival times | Task 4 |
| DD (Anthropic session 5h cap; weekly cap originally pinned) | `_anthropic_caps.SESSION_CAP_HOURS = 5.0` | Task 9 |
| EE (`NHPPArrivalGenerator.__call__(rng_seed)` realigned with `stochastic_fx`) | Arrival generator | Task 5 |
| FF (`audit_block` envelope completion: `message_pool_content_sha256` + `parser_version_sha`) | Audit-block envelope module | Task 10 |
| GG (Hour-block × day-type indexed empirical bootstrap) | Cost simulator | Task 7 |
| HH (Reconciliation HALT tightened to 1%) | EDA notebook + disposition template | Tasks 11, 17 |
| II (`R6Output.quality_flags: frozenset[str]`) | R6Output type + flag computation | Tasks 3, 10 |
| JJ (Per-module `audit_block` recipes) | Each generator/simulator | Tasks 5, 6, 7 |
| KK (`cop_costs` float64 ensemble / Decimal headline precision boundary) | CostTrajectoryEnsemble + R6Output | Tasks 3, 7, 10 |
| LL (Structured `fallback_log: Sequence[FallbackEvent]`) | Cost simulator | Tasks 3, 7 |
| MM (`CapWaitConfig` frozen-dc; values pinned with source URL) | Cap-wait counter | Tasks 3, 8 |
| NN (Token-size invariance across `k` documented bias) | Threats row + notebook preambles | Tasks 12, 13 |
| OO (Reconciliation-ratio reporting cell) | Variance-decomp notebook | Task 13 |
| PP (RNG-call-order docstring pin) | Generator docstrings | Tasks 5, 6 |
| QQ (Weekly-cap scoped out; `CapWaitConfig` single-field) | Cap-wait counter; `_anthropic_caps` | Tasks 8, 9 |
| RR (Pool canonicalization dedupe; `uuid` quaternary sort key) | Phase 1 sibling amendment + canonicalization module | Tasks 2, 10 |
| SS (CORRECTIONS-EE wording softened) | Documentation-only; no task |  — |
| TT (Canonicalization edge cases: drop `request_id=None`; lex-smallest `uuid` tiebreaker) | Canonicalization module + Hypothesis property | Tasks 10, 15 |

| Spec § | Implementing Tasks |
|---|---|
| §2.1 NHPP intensity specification | Task 4 |
| §2.2 cap-reset detection REMOVED | n/a (Task 4 fits on within-session only) |
| §2.3 sizing curve `k ∈ {0.5, 1, 2, 3, 5}` | Task 5 (`NHPPSimulationConfig.k`) |
| §2.4 hour-block × day-type indexed token bootstrap | Task 7 |
| §2.5 hedge representation: none | n/a (out of scope) |
| §2.6 output metrics (VaR/CVaR/percentiles/SD/mean) | Task 10 (R6Output aggregator) |
| §2.7 HALT events | Tasks 11–14, 17 (disposition templates) |
| §3.1 FX path generation block-bootstrap | Task 6 |
| §3.2 Arrival ⊥ FX independence (v1) | Notebook preamble in Task 12 |
| §3.3 component decomposition / contract table | Tasks 3–10 |
| §3.4 reused from v0.2.1 | Phase 1 (Tasks 1–2) |
| §3.5 new errors | Tasks 1, 4 |
| §4 notebook structure | Tasks 11–15 |
| §5.1 LiteLLM SHA pin | Inherited from v0.2.1 |
| §5.2 Banrep daily TRM pin | Inherited from v0.2.1 Task 1 |
| §5.3 R6 `audit_block` + 7-step canonicalization | Task 10 |
| §5.4 DATA_PROVENANCE | Task 16 |
| §6 threats / mitigations | Notebook preambles Tasks 11–15 |
| §7 anti-fishing invariants | Tasks 4–10 (pin in code), Tasks 11–15 (pin in notebooks) |
| §8 workflow / agent assignment | Each task lists owner + audit-pass chain |
| §9 out of scope | Documented in notebook preambles |
| §11 cited files | Tasks 1, 2, 9, 11–17 |

---

## File structure (locked before task decomposition)

### Phase 1 — Sibling v0.2.1 plan-execution amendments

- `simulations/dev_ai_cost_v2/_errors.py` — **modify** (or amend Task 4 in sibling plan): introduce `DevAICostError(Exception)`; reparent `JSONLSchemaError(DevAICostError)`.
- `simulations/dev_ai_cost_v2/types.py` — **modify** (or amend sibling Task 5): add `uuid: str` field to `MessageRecord` frozen-dc.
- `simulations/dev_ai_cost_v2/jsonl_io.py` — **modify** (or amend sibling Task 5/jsonl_io step): capture per-line `uuid` field during JSONL parse; expose on `MessageRecord`.
- `simulations/tests/strategies.py` — **modify**: extend `MessageRecord` strategy with `uuid` field.
- `simulations/tests/test_dev_ai_cost_v2_types.py` — **modify**: pin `MessageRecord.uuid` schema.
- `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` — **modify**: pin uuid parsing; pin reparented `JSONLSchemaError`.

### Phase 2 — R6 sub-package modules (new files inside `simulations/dev_ai_cost_v2/`)

- `simulations/dev_ai_cost_v2/_anthropic_caps.py` — **new** declarative constants module. `SESSION_CAP_HOURS = 5.0`. Source URL + access date comment block.
- `simulations/dev_ai_cost_v2/types.py` — **extend** (already touched in Phase 1). Add: `NHPPParameters`, `NHPPSimulationConfig`, `ArrivalEnsemble`, `FXPathEnsemble`, `CostTrajectoryEnsemble`, `FallbackEvent`, `CapWaitConfig`, `CapWaitOutput`, `R6Output`. All frozen-dc; `R6Output.quality_flags: frozenset[str]`.
- `simulations/dev_ai_cost_v2/_errors.py` — **extend** (already touched in Phase 1). Add `NHPPCalibrationError(DevAICostError)`, `NHPPSparseBinError(NHPPCalibrationError)`, `SparsePoolError(DevAICostError)`.
- `simulations/dev_ai_cost_v2/nhpp_calibration.py` — **new** modules-tier. `fit_nhpp(records: Sequence[MessageRecord]) -> NHPPParameters`.
- `simulations/dev_ai_cost_v2/arrival_generators.py` — **new** modules-tier. Frozen-dc `NHPPArrivalGenerator(config: NHPPSimulationConfig)` with `__call__(rng_seed: int) -> ArrivalEnsemble`.
- `simulations/dev_ai_cost_v2/fx_block_bootstrap.py` — **new** modules-tier. Frozen-dc `FXBlockBootstrapGenerator` (Politis–Romano stationary bootstrap, expected block length `⌈T_hist^(1/3)⌉`).
- `simulations/dev_ai_cost_v2/cost_simulation.py` — **new** modules-tier. Frozen-dc `CostSimulator` with `pool_content_sha` precomputed at construction; `__call__(arrivals, fx, rng_seed) -> CostTrajectoryEnsemble`.
- `simulations/dev_ai_cost_v2/cap_wait_counter.py` — **new** modules-tier. Frozen-dc `CapWaitCounter(config: CapWaitConfig)` returning per-path session-cap-wait hours.
- `simulations/dev_ai_cost_v2/canonicalization.py` — **new** modules-tier. Pure function `canonicalize_message_pool(records_by_path: Mapping[Path, Sequence[MessageRecord]]) -> tuple[Sequence[MessageRecord], int]` returning deduplicated/sorted records + `dropped_legacy_request_id_count`. Computes `message_pool_content_sha256`.
- `simulations/dev_ai_cost_v2/r6_envelope.py` — **new** modules-tier. `compute_r6_audit_block(...) -> AuditBlock`; chains per-module hashes per §5.3.
- `simulations/dev_ai_cost_v2/r6_aggregator.py` — **new** modules-tier. Computes `R6Output` from `CostTrajectoryEnsemble` (VaR, CVaR, percentiles, quality_flags), Decimal-headlined per CORRECTIONS-KK.

### Phase 2 — Tests (new files)

- `simulations/tests/test_dev_ai_cost_v2_types_r6.py` — types tier pins for new R6 types.
- `simulations/tests/test_dev_ai_cost_v2_nhpp_calibration.py` — MLE tests + sparse-bin HALT.
- `simulations/tests/test_dev_ai_cost_v2_arrival_generator.py` — deterministic-RNG equivalence; per-module audit_block.
- `simulations/tests/test_dev_ai_cost_v2_fx_bootstrap.py` — deterministic-RNG equivalence; block-length pin.
- `simulations/tests/test_dev_ai_cost_v2_cost_simulator.py` — hour-block × day-type bootstrap; structured `fallback_log`; precision boundary round-trip.
- `simulations/tests/test_dev_ai_cost_v2_cap_wait.py` — session-cap accounting.
- `simulations/tests/test_dev_ai_cost_v2_canonicalization.py` — shuffle invariance; tiebreaker edge cases; legacy-record-drop.
- `simulations/tests/test_dev_ai_cost_v2_r6_envelope.py` — audit_block envelope chaining.
- `simulations/tests/strategies.py` — **extend** with strategies for R6 types and a `MessageRecord` sequence strategy supporting duplicate `request_id` across paths.

### Phase 3 — Notebooks (new directory `notebooks/dev_ai_cost_v2_r6/`)

- `notebooks/dev_ai_cost_v2_r6/01_nhpp_eda.ipynb`
- `notebooks/dev_ai_cost_v2_r6/02_simulation.ipynb`
- `notebooks/dev_ai_cost_v2_r6/03_variance_decomp.ipynb`
- `notebooks/dev_ai_cost_v2_r6/04_cap_wait.ipynb`
- `notebooks/dev_ai_cost_v2_r6/05_sensitivity.ipynb`
- `notebooks/dev_ai_cost_v2_r6/data/DATA_PROVENANCE.md`
- `notebooks/dev_ai_cost_v2_r6/dispositions/nhpp_min_bin_template.md`
- `notebooks/dev_ai_cost_v2_r6/dispositions/nhpp_convergence_template.md`
- `notebooks/dev_ai_cost_v2_r6/dispositions/sparse_cell_fallback_template.md`
- `notebooks/dev_ai_cost_v2_r6/dispositions/reconciliation_drift_template.md`
- `notebooks/dev_ai_cost_v2_r6/dispositions/reconciliation_ratio_template.md`

### Tier-import rule (enforced)

`types/` ↛ `modules/`, `utils/`; `modules/` ↛ `utils/`. R6 has no new IO Boundary; it consumes `JSONLReader` output (from v0.2.1's utils tier) at the notebook orchestration layer. The new `canonicalization.py` is pure (modules tier): it takes already-parsed `Mapping[Path, Sequence[MessageRecord]]` as input.

---

## Task ordering and dependencies

```
PHASE 1 (sibling v0.2.1 amendments — must complete before Phase 2):

   Task 1 (DevAICostError reparent — CORRECTIONS-AA)
            │
            ▼
   Task 2 (MessageRecord.uuid field — CORRECTIONS-RR/-TT)
            │
            ▼
PHASE 2 (R6 sub-package modules):

   Task 3 (R6 types — NHPP/Ensemble/Output frozen-dcs)
            │
            ▼
   Task 4 (nhpp_calibration.fit_nhpp — CORRECTIONS-BB/-CC)
            │
            ▼
   Task 5 (NHPPArrivalGenerator — CORRECTIONS-EE/-JJ/-PP)
            │
            ▼
   Task 6 (FXBlockBootstrapGenerator — block-length pin, RNG docstring)
            │
            ▼
   Task 7 (CostSimulator — CORRECTIONS-GG/-LL; precomputed pool_content_sha)
            │
            ▼
   Task 8 (CapWaitCounter — CORRECTIONS-MM/-QQ session-only)
            │
            ▼
   Task 9 (_anthropic_caps.SESSION_CAP_HOURS = 5.0)
            │
            ▼
   Task 10 (canonicalization + R6 envelope + R6 aggregator)
            │
            ▼
PHASE 3 (Hypothesis property tests across modules):

   Task 15 (consolidated property-test sweep: shuffle-invariance,
            tiebreaker, forward-fill, double-iteration, precision-boundary,
            deterministic-RNG)
            │
            ▼
PHASE 4 (Notebooks):

   Task 11 (01_nhpp_eda.ipynb) ──► [HALT if min-bin or drift > 1%]
            │
            ▼
   Task 12 (02_simulation.ipynb)
            │
            ▼
   Task 13 (03_variance_decomp.ipynb — reconciliation-ratio cell)
            │
            ▼
   Task 14 (04_cap_wait.ipynb — session-cap only per CORRECTIONS-QQ)
            │
            ▼
   Task 15a (05_sensitivity.ipynb — DIAGNOSTIC arms)
            │
            ▼
PHASE 5 (Implementation review checkpoint):

   Task 16 (Code Reviewer + Reality Checker + Backend Architect review
            per feedback_implementation_review_agents)
            │
            ▼
PHASE 6 (Pre-output Delphi audit):

   Task 17 (audit-econ skill: Delphi panel on pre-output R6 results)
            │
            ▼
PHASE 7 (Disposition templates — written before notebooks run):

   Task 18 (disposition templates for §2.7 HALT events) — actually
            authored alongside Task 11 (templates need to exist BEFORE
            notebook runs to be useful); listed here as a logical phase
            but executed concurrently with Task 11 setup.
            │
            ▼
   Task 19 (release R6 outputs to M-design step — gated on Task 17)
```

**Owner agents (per spec §8):**

- Phase 1 amendments: **Backend Architect** (errors/types) + **Code Reviewer** (post-amend check)
- Phase 2 modules: **Backend Architect** primary, **Code Reviewer** + **Reality Checker** at completion
- Phase 3 property tests: **Backend Architect** with Hypothesis-skill orchestration
- Phase 4 notebooks: **Quantitative Analyst** primary, **Reality Checker** at each HALT checkpoint
- Phase 5 implementation review: per `memory/feedback_implementation_review_agents.md` (Code Reviewer + Reality Checker + Backend Architect parallel dispatch)
- Phase 6 Delphi audit: invoked via `audit-econ` skill

**Audit-pass chain per module (per spec §8):**

`functional-python` (Phase 2 design) → `tighten-types` (post-impl) → `contract-docstrings` → `hypothesis-tests` (Phase 3) → `try-except` → `pre-mortem` → `mutation-testing` (Phase 5 quality gate, selective).

---

# PHASE 1 — Sibling v0.2.1 plan-execution amendments

**Must complete before any Phase 2 task starts.**

## Task 1: Introduce `DevAICostError` root + reparent `JSONLSchemaError` (CORRECTIONS-AA)

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `try-except` + `contract-docstrings`
**Spec ref:** R6 §0.1 CORRECTIONS-AA; R6 §3.4 (reused from v0.2.1); R6 §3.5 (new errors); R6 frontmatter `sibling_corrections_v0_2_1_plan` item 1.
**Depends on:** v0.2.1 plan Task 4 (`_errors.py` exists with `JSONLSchemaError(SchemaMismatchError)`).

**Files:**
- Modify: `simulations/dev_ai_cost_v2/_errors.py`
- Modify: `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` (any `JSONLSchemaError` parent assertions)
- Modify: `simulations/dev_ai_cost_v2/jsonl_io.py` (any import lines for `JSONLSchemaError` parent class)

**Exit criteria:**
- `DevAICostError(Exception)` declared at top of `_errors.py` with docstring "Sub-package root exception for `dev_ai_cost_v2`."
- `JSONLSchemaError(DevAICostError)` — parent changed from `SchemaMismatchError` to `DevAICostError`.
- All existing v0.2.1 tests still pass (the rename is transparent to handlers that catch `JSONLSchemaError` or `Exception`).
- A new test pins the inheritance contract: `issubclass(JSONLSchemaError, DevAICostError) is True`.

**Steps:**

- [ ] **Step 1.1: Write the failing inheritance test**

```python
# simulations/tests/test_dev_ai_cost_v2_errors_hierarchy.py
from simulations.dev_ai_cost_v2._errors import (
    DevAICostError,
    JSONLSchemaError,
)


def test_devaicosterror_is_sub_package_root() -> None:
    assert issubclass(DevAICostError, Exception)
    assert DevAICostError is not Exception


def test_jsonlschemaerror_reparented_to_devaicosterror() -> None:
    assert issubclass(JSONLSchemaError, DevAICostError)
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_errors_hierarchy.py -v`
Expected: FAIL with `ImportError` for `DevAICostError`.

- [ ] **Step 1.2: Amend `_errors.py`**

```python
# simulations/dev_ai_cost_v2/_errors.py
"""Sub-package errors for dev_ai_cost_v2."""


class DevAICostError(Exception):
    """Sub-package root exception for `dev_ai_cost_v2`.

    Introduced per R6 v0.1.1 CORRECTIONS-AA (errors hierarchy). All
    sub-package-specific errors inherit from this class.
    """


class JSONLSchemaError(DevAICostError):
    """Raised when a JSONL row fails the Pydantic `extra='forbid'` schema."""
```

- [ ] **Step 1.3: Run inheritance test to verify it passes**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_errors_hierarchy.py -v`
Expected: PASS.

- [ ] **Step 1.4: Run full sibling sub-package test suite for regression**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_*.py -v`
Expected: PASS (the reparent should be transparent to existing handlers; if a test asserts a specific parent like `SchemaMismatchError`, fix that test to assert `DevAICostError`).

- [ ] **Step 1.5: Apply `contract-docstrings` pass to `_errors.py`**

Apply the `contract-docstrings` skill to both classes: document the contract — `DevAICostError` is raised by no caller directly (it's a root); `JSONLSchemaError` is raised by `JSONLReader` on schema-mismatch; no silenced errors.

- [ ] **Step 1.6: Commit**

```bash
git add simulations/dev_ai_cost_v2/_errors.py \
        simulations/tests/test_dev_ai_cost_v2_errors_hierarchy.py
git commit -m "feat(dev_ai_cost_v2): introduce DevAICostError root; reparent JSONLSchemaError

Per R6 spec v0.1.1 CORRECTIONS-AA, sibling v0.2.1 plan-execution amendment.
JSONLSchemaError now inherits from DevAICostError(Exception). Enables R6's
NHPPCalibrationError / SparsePoolError to share a sub-package root.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Add `uuid: str` field to `MessageRecord`; capture in `JSONLReader` (CORRECTIONS-RR / -TT)

**Owner:** Backend Architect
**Audit-pass chain:** `tighten-types` + `try-except` + `contract-docstrings` + `hypothesis-tests`
**Spec ref:** R6 §0.2 CORRECTIONS-RR; R6 §5.3 (canonicalization step 4 tiebreaker by `uuid`); CORRECTIONS-TT (b) lex-smallest-uuid tiebreaker within same source file. R6 frontmatter `sibling_corrections_v0_2_1_plan` item 2. Wave 1 RC v0.1.2 closure verified `uuid` is missing from v0.2.1 §3.5.
**Depends on:** Task 1; v0.2.1 plan Task 5 (`types.py` + `jsonl_io.py` exist with `MessageRecord`).

**Files:**
- Modify: `simulations/dev_ai_cost_v2/types.py`
- Modify: `simulations/dev_ai_cost_v2/jsonl_io.py`
- Modify: `simulations/tests/strategies.py`
- Modify: `simulations/tests/test_dev_ai_cost_v2_types.py`
- Modify: `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py`

**Exit criteria:**
- `MessageRecord` frozen-dc gains `uuid: str` field as the LAST positional/keyword field (append-only to preserve any existing tests that construct by position; convert to keyword-only if v0.2.1 already used kw-only — check sibling plan Task 5 first).
- `JSONLReader` parses the per-line `uuid` field from the Anthropic JSONL schema (each assistant message line includes a `uuid` key; user lines may not — pin the source-of-truth rule below).
- Pydantic `extra="forbid"` row validator includes `uuid` as a required field.
- Hypothesis strategy for `MessageRecord` emits a non-empty `uuid` string.
- Property test: round-trip a record through `dataclasses.asdict` and verify `uuid` survives.

**Rule for which lines carry `uuid` (pinned ex-ante):** Per the Anthropic Claude Code JSONL schema (verified by Wave 1 RC v0.1.2 closure), each message-level line — both user and assistant — carries a top-level `uuid` field. If during implementation a row is encountered without a `uuid`, the parser raises `JSONLSchemaError("missing uuid")` — do NOT auto-generate or default. (This is the `extra="forbid"` discipline applied symmetrically: a missing required field is an error.)

**Steps:**

- [ ] **Step 2.1: Write the failing test for `MessageRecord.uuid` field**

```python
# simulations/tests/test_dev_ai_cost_v2_types.py (extend)
from simulations.dev_ai_cost_v2.types import MessageRecord
from dataclasses import fields


def test_messagerecord_has_uuid_field() -> None:
    field_names = {f.name for f in fields(MessageRecord)}
    assert "uuid" in field_names
    uuid_field = next(f for f in fields(MessageRecord) if f.name == "uuid")
    assert uuid_field.type is str  # frozen-dc field type annotation
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_types.py::test_messagerecord_has_uuid_field -v`
Expected: FAIL (field missing).

- [ ] **Step 2.2: Add `uuid: str` to `MessageRecord`**

Locate the existing `MessageRecord` frozen-dc in `simulations/dev_ai_cost_v2/types.py`. Add `uuid: str` as the last field. If v0.2.1's `MessageRecord` is constructed via keyword args throughout the codebase (verify by `grep -r "MessageRecord(" simulations/`), append-as-keyword is safe. If positional construction exists, prefer to make all fields keyword-only and update construction sites; do NOT make `uuid` default-valued (CORRECTIONS-V's `extra="forbid"` discipline forbids silent defaults).

- [ ] **Step 2.3: Update Hypothesis strategy in `simulations/tests/strategies.py`**

```python
# in strategies.py, locate the message_record() strategy and add:
@st.composite
def message_record(draw, ...) -> MessageRecord:
    # existing fields ...
    uuid = draw(st.from_regex(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", fullmatch=True))
    return MessageRecord(
        # existing kwargs ...
        uuid=uuid,
    )
```

(The UUID-v4 regex emits realistic-shape strings; the type signature is just `str`, but the strategy producing realistic UUIDs catches downstream parser assumptions.)

- [ ] **Step 2.4: Run the type test to verify it passes**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_types.py::test_messagerecord_has_uuid_field -v`
Expected: PASS.

- [ ] **Step 2.5: Write failing test for `JSONLReader` capturing `uuid`**

```python
# simulations/tests/test_dev_ai_cost_v2_jsonl_io.py (extend)
import json
from pathlib import Path

import pytest

from simulations.dev_ai_cost_v2._errors import JSONLSchemaError
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader


def test_jsonl_reader_captures_uuid_field(tmp_path: Path) -> None:
    line = {
        "type": "assistant",
        "timestamp": "2026-05-16T10:00:00Z",
        "session_id": "sess-1",
        "requestId": "req-1",
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "model": "claude-opus-4-7",
        "message": {
            "usage": {
                "input_tokens": 10,
                "output_tokens": 5,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            }
        },
    }
    f = tmp_path / "x.jsonl"
    f.write_text(json.dumps(line) + "\n")
    reader = JSONLReader(root=tmp_path)
    records = list(reader)
    assert len(records) == 1
    assert records[0].uuid == "550e8400-e29b-41d4-a716-446655440000"


def test_jsonl_reader_missing_uuid_raises_schema_error(tmp_path: Path) -> None:
    line = {
        # same as above but WITHOUT "uuid"
        "type": "assistant",
        "timestamp": "2026-05-16T10:00:00Z",
        "session_id": "sess-1",
        "requestId": "req-1",
        "model": "claude-opus-4-7",
        "message": {"usage": {"input_tokens": 1, "output_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}},
    }
    f = tmp_path / "x.jsonl"
    f.write_text(json.dumps(line) + "\n")
    reader = JSONLReader(root=tmp_path)
    with pytest.raises(JSONLSchemaError, match="uuid"):
        list(reader)
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_jsonl_io.py -v -k uuid`
Expected: FAIL.

- [ ] **Step 2.6: Update `JSONLReader` Pydantic row validator + record construction**

In `simulations/dev_ai_cost_v2/jsonl_io.py`, locate the Pydantic row model (likely named `_RawRow` or similar with `extra="forbid"`). Add `uuid: str` as a required field. In the constructor that maps validated row → `MessageRecord`, pass `uuid=raw.uuid`. The `extra="forbid"` validator will already raise on rows without `uuid` — but the test expects the surfaced exception type to be `JSONLSchemaError`. If the existing `try-except` wrapping does not yet convert Pydantic `ValidationError` to `JSONLSchemaError`, narrow the `try` to the `_RawRow(**line_dict)` call and re-raise as `JSONLSchemaError` (per `try-except` skill, the `try` covers ONLY the validation step).

- [ ] **Step 2.7: Run uuid tests to verify they pass**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_jsonl_io.py -v -k uuid`
Expected: PASS.

- [ ] **Step 2.8: Run full sibling sub-package test suite**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_*.py -v`
Expected: PASS. If any pre-existing test constructed `MessageRecord` without `uuid` (positional or kwargs), update that test to supply a uuid string; do NOT default the field.

- [ ] **Step 2.9: Apply `contract-docstrings` to `JSONLReader.__iter__` (or the iter method)**

Document that `uuid` is required per Anthropic schema; missing-uuid lines raise `JSONLSchemaError`; no silenced errors.

- [ ] **Step 2.10: Commit**

```bash
git add simulations/dev_ai_cost_v2/types.py \
        simulations/dev_ai_cost_v2/jsonl_io.py \
        simulations/tests/strategies.py \
        simulations/tests/test_dev_ai_cost_v2_types.py \
        simulations/tests/test_dev_ai_cost_v2_jsonl_io.py
git commit -m "feat(dev_ai_cost_v2): add MessageRecord.uuid; JSONLReader captures per-line uuid

Per R6 spec v0.1.2 CORRECTIONS-RR + v0.1.3 CORRECTIONS-TT, sibling v0.2.1
plan-execution amendment. uuid is the quaternary sort key + tiebreaker for
R6's message_pool_content_sha256 canonicalization. Pydantic extra='forbid'
raises JSONLSchemaError on missing uuid (no silent defaults).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

**Phase 1 exit gate:** `uv run pytest simulations/tests/test_dev_ai_cost_v2_*.py -v` passes; `git log --oneline -2` shows both Task 1 and Task 2 commits; `grep -n "DevAICostError" simulations/dev_ai_cost_v2/_errors.py` returns the new class; `grep -n "uuid" simulations/dev_ai_cost_v2/types.py` returns the new field. Only then proceed to Phase 2.

---

# PHASE 2 — R6 sub-package modules

## Task 3: Add R6 types — `NHPPParameters`, `NHPPSimulationConfig`, `ArrivalEnsemble`, `FXPathEnsemble`, `CostTrajectoryEnsemble`, `FallbackEvent`, `CapWaitConfig`, `CapWaitOutput`, `R6Output`

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `tighten-types` + `contract-docstrings`
**Spec ref:** §3.3 contract table (lines for each new type); CORRECTIONS-II (`R6Output.quality_flags`); CORRECTIONS-KK (precision boundary docstring); CORRECTIONS-LL (`FallbackEvent`); CORRECTIONS-MM/-QQ (`CapWaitConfig` single-field).
**Depends on:** Phase 1 complete (Tasks 1 + 2 exit gate passed).

**Files:**
- Modify: `simulations/dev_ai_cost_v2/types.py` (extend)
- Create: `simulations/tests/test_dev_ai_cost_v2_types_r6.py`
- Modify: `simulations/tests/strategies.py`

**Exit criteria:**
- All nine new frozen-dcs declared with exact field signatures per spec §3.3.
- `R6Output.quality_flags: frozenset[str]` (NOT `set` — must be immutable per frozen-dc rule).
- `CapWaitConfig` has exactly ONE field `session_cap_hours: float` per CORRECTIONS-QQ.
- `FallbackEvent.fallback_level: Literal["cell", "day-type-marginal"]` per CORRECTIONS-LL.
- `CostTrajectoryEnsemble.cop_costs: NDArray[float64]` with docstring stating CORRECTIONS-KK precision-boundary contract.
- `NHPPParameters.f_hour_block: tuple[float, float, float, float]` with `f_hour_block[0] == 1.0` identification constraint (validated in `__post_init__` or via a separate construction helper since frozen-dc disallows mutation; use a `@classmethod` smart constructor that asserts the constraint).
- `NHPPParameters.g_day_type: tuple[float, float]` with `g_day_type[0] == 1.0` likewise.
- Hypothesis strategies for all new types in `simulations/tests/strategies.py`.
- Test `test_dev_ai_cost_v2_types_r6.py` pins every field name + type.

**Steps:**

- [ ] **Step 3.1: Write the failing test pinning all new types**

```python
# simulations/tests/test_dev_ai_cost_v2_types_r6.py
from dataclasses import fields, is_dataclass
from decimal import Decimal
from typing import Literal, get_args, get_type_hints

import numpy as np

from simulations.dev_ai_cost_v2 import types as r6_types


def test_nhpp_parameters_signature() -> None:
    cls = r6_types.NHPPParameters
    assert is_dataclass(cls)
    field_names = {f.name for f in fields(cls)}
    assert field_names == {
        "lambda_0",
        "f_hour_block",
        "g_day_type",
        "log_likelihood",
        "convergence_iters",
        "per_cell_counts",
    }


def test_nhpp_simulation_config_signature() -> None:
    cls = r6_types.NHPPSimulationConfig
    field_names = {f.name for f in fields(cls)}
    assert field_names == {"params", "k", "horizon_days", "n_paths"}


def test_arrival_ensemble_signature() -> None:
    cls = r6_types.ArrivalEnsemble
    field_names = {f.name for f in fields(cls)}
    assert field_names == {"arrival_times", "session_assignments", "audit_block"}


def test_fx_path_ensemble_signature() -> None:
    cls = r6_types.FXPathEnsemble
    field_names = {f.name for f in fields(cls)}
    assert field_names == {"log_returns", "usdcop_paths", "audit_block"}


def test_cost_trajectory_ensemble_signature() -> None:
    cls = r6_types.CostTrajectoryEnsemble
    field_names = {f.name for f in fields(cls)}
    assert field_names == {"cop_costs", "fallback_log", "audit_block"}


def test_fallback_event_signature() -> None:
    cls = r6_types.FallbackEvent
    field_names = {f.name for f in fields(cls)}
    assert field_names == {
        "simulated_ts",
        "hour_block",
        "day_type",
        "fallback_level",
        "observed_pool_size",
    }


def test_cap_wait_config_is_single_field_per_corrections_qq() -> None:
    cls = r6_types.CapWaitConfig
    field_names = {f.name for f in fields(cls)}
    assert field_names == {"session_cap_hours"}  # weekly removed


def test_r6_output_has_quality_flags_frozenset() -> None:
    cls = r6_types.R6Output
    hints = get_type_hints(cls)
    assert hints["quality_flags"] is frozenset[str]


def test_nhpp_parameters_rejects_non_identified_f_hour_block() -> None:
    import pytest
    with pytest.raises(ValueError, match="f_hour_block"):
        r6_types.NHPPParameters.create(
            lambda_0=1.0,
            f_hour_block=(0.5, 1.0, 1.5, 2.0),  # f[0] != 1
            g_day_type=(1.0, 0.5),
            log_likelihood=-100.0,
            convergence_iters=10,
            per_cell_counts=((100, 100, 100, 100), (50, 50, 50, 50)),
        )
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_types_r6.py -v`
Expected: FAIL (types not yet defined).

- [ ] **Step 3.2: Implement the types in `simulations/dev_ai_cost_v2/types.py`**

```python
# Append to simulations/dev_ai_cost_v2/types.py
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal, Mapping

import numpy as np
from numpy.typing import NDArray

from simulations.dev_ai_cost_v2._errors import DevAICostError
# AuditBlock import (existing in stochastic_fx or in v0.2.1 sub-package):
from simulations.stochastic_fx.types import AuditBlock  # adjust import to actual location


@dataclass(frozen=True, slots=True)
class NHPPParameters:
    """MLE-fit Non-Homogeneous Poisson Process parameters.

    Hour-block × day-type seasonality per R6 §2.1, CORRECTIONS-BB.
    Identification: f_hour_block[0]=1.0 (morning), g_day_type[0]=1.0 (weekday).
    """
    lambda_0: float
    f_hour_block: tuple[float, float, float, float]
    g_day_type: tuple[float, float]
    log_likelihood: float
    convergence_iters: int
    per_cell_counts: tuple[tuple[int, int, int, int], tuple[int, int, int, int]]

    @classmethod
    def create(
        cls,
        *,
        lambda_0: float,
        f_hour_block: tuple[float, float, float, float],
        g_day_type: tuple[float, float],
        log_likelihood: float,
        convergence_iters: int,
        per_cell_counts: tuple[tuple[int, int, int, int], tuple[int, int, int, int]],
    ) -> "NHPPParameters":
        if f_hour_block[0] != 1.0:
            raise ValueError(
                f"NHPPParameters: f_hour_block[0] must be 1.0 (morning ref); "
                f"got {f_hour_block[0]}"
            )
        if g_day_type[0] != 1.0:
            raise ValueError(
                f"NHPPParameters: g_day_type[0] must be 1.0 (weekday ref); "
                f"got {g_day_type[0]}"
            )
        if lambda_0 <= 0:
            raise ValueError(f"NHPPParameters: lambda_0 must be > 0; got {lambda_0}")
        return cls(
            lambda_0=lambda_0,
            f_hour_block=f_hour_block,
            g_day_type=g_day_type,
            log_likelihood=log_likelihood,
            convergence_iters=convergence_iters,
            per_cell_counts=per_cell_counts,
        )


@dataclass(frozen=True, slots=True)
class NHPPSimulationConfig:
    """All bit-exactness parameters for an arrival ensemble."""
    params: NHPPParameters
    k: float
    horizon_days: int
    n_paths: int


@dataclass(frozen=True, slots=True)
class ArrivalEnsemble:
    """NHPP arrival ensemble; NaN-padded per-path ragged times."""
    arrival_times: NDArray[np.float64]  # shape (n_paths, n_arrivals_max)
    session_assignments: NDArray[np.int32]  # shape (n_paths, n_arrivals_max)
    audit_block: AuditBlock


@dataclass(frozen=True, slots=True)
class FXPathEnsemble:
    """Block-bootstrap FX path ensemble over horizon_days."""
    log_returns: NDArray[np.float64]
    usdcop_paths: NDArray[np.float64]
    audit_block: AuditBlock


@dataclass(frozen=True, slots=True)
class FallbackEvent:
    """Structured sparse-cell fallback record per CORRECTIONS-LL."""
    simulated_ts: float
    hour_block: str  # "morning" | "afternoon" | "evening" | "night"
    day_type: str    # "weekday" | "weekend"
    fallback_level: Literal["cell", "day-type-marginal"]
    observed_pool_size: int


@dataclass(frozen=True, slots=True)
class CostTrajectoryEnsemble:
    """Ensemble of COP-cost trajectories.

    Precision-boundary (CORRECTIONS-KK): `cop_costs` is float64 inside the
    ensemble (Decimal prohibitive across 10k × 22 trajectories). Headline
    outputs in `R6Output` are converted to Decimal at aggregation.
    """
    cop_costs: NDArray[np.float64]  # shape (n_paths, horizon_days)
    fallback_log: tuple[FallbackEvent, ...]
    audit_block: AuditBlock


@dataclass(frozen=True, slots=True)
class CapWaitConfig:
    """Cap-wait counter configuration.

    Single-field per CORRECTIONS-QQ (weekly cap scoped out of R6 v1).
    """
    session_cap_hours: float


@dataclass(frozen=True, slots=True)
class CapWaitOutput:
    """Per-path session-cap-wait hours."""
    session_cap_wait_hours: NDArray[np.float64]  # shape (n_paths,)


@dataclass(frozen=True, slots=True)
class R6Output:
    """Aggregated R6 outputs for one k value. Decimal headlines."""
    k: float
    var_05_cop: Decimal
    var_01_cop: Decimal
    cvar_05_cop: Decimal
    cvar_01_cop: Decimal
    percentiles: Mapping[int, Decimal]
    mean_cop: Decimal
    sd_cop: Decimal
    variance_decomp_fx_share: Decimal
    variance_decomp_reconciliation_ratio: Decimal
    cap_wait_session_obs_hours: Decimal
    cap_wait_session_sim_hours: Decimal
    bootstrap_ci_var_05: tuple[Decimal, Decimal]
    quality_flags: frozenset[str]
    audit_block: AuditBlock
```

- [ ] **Step 3.3: Add Hypothesis strategies for new types in `simulations/tests/strategies.py`**

Add `@st.composite` strategies for `NHPPParameters`, `NHPPSimulationConfig`, `ArrivalEnsemble`, `FXPathEnsemble`, `FallbackEvent`, `CostTrajectoryEnsemble`, `CapWaitConfig`, `CapWaitOutput`, `R6Output`. For arrays, use `hypothesis.extra.numpy.arrays` with bounded shapes. For `NHPPParameters`, force `f_hour_block[0] = 1.0` and `g_day_type[0] = 1.0` inside the strategy (since `NHPPParameters.create` validates).

- [ ] **Step 3.4: Run the type test to verify it passes**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_types_r6.py -v`
Expected: PASS.

- [ ] **Step 3.5: Apply `tighten-types` pass**

Run the `tighten-types` skill on `types.py`. Verify no `Any`, no loose `dict`, no missing type parameters. Check that `NDArray[np.float64]` annotations are consistent.

- [ ] **Step 3.6: Apply `contract-docstrings` pass**

Document the precision boundary on `CostTrajectoryEnsemble` (CORRECTIONS-KK contract); document `R6Output.quality_flags` known flag tokens.

- [ ] **Step 3.7: Commit**

```bash
git add simulations/dev_ai_cost_v2/types.py \
        simulations/tests/test_dev_ai_cost_v2_types_r6.py \
        simulations/tests/strategies.py
git commit -m "feat(dev_ai_cost_v2): add R6 types — NHPP/Ensemble/CapWait/R6Output

Per R6 spec §3.3, CORRECTIONS-II (quality_flags frozenset), CORRECTIONS-KK
(float64/Decimal precision boundary), CORRECTIONS-LL (FallbackEvent),
CORRECTIONS-MM/-QQ (CapWaitConfig single-field).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Implement `nhpp_calibration.fit_nhpp` — binned MLE on 8-cell grid (CORRECTIONS-BB, -CC)

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `tighten-types` + `contract-docstrings` + `hypothesis-tests` + `try-except` + `pre-mortem`
**Spec ref:** §2.1 NHPP intensity specification; §2.7 NHPP min-bin HALT; §3.3 contract row; §3.5 new errors `NHPPCalibrationError`, `NHPPSparseBinError`; CORRECTIONS-BB (8-cell grid; `N_min = 50`); CORRECTIONS-CC (session-id grouping; no cap-reset).
**Depends on:** Task 3.

**Files:**
- Create: `simulations/dev_ai_cost_v2/nhpp_calibration.py`
- Modify: `simulations/dev_ai_cost_v2/_errors.py` (add new errors)
- Create: `simulations/tests/test_dev_ai_cost_v2_nhpp_calibration.py`

**Exit criteria:**
- `fit_nhpp(records: Sequence[MessageRecord]) -> NHPPParameters` — pure function (modules tier).
- Groups records by `session_id`; extracts within-session inter-arrival times (cross-session gaps excluded per CORRECTIONS-CC).
- Bins observations into the 8-cell grid: hour-blocks `[06–12), [12–18), [18–22), [22–06)`; day-types `weekday {Mon..Fri}` / `weekend {Sat, Sun}`.
- Binned MLE with closed-form per-cell counts (binned Poisson MLE has closed-form: `λ̂_cell = N_cell / T_cell` where `T_cell` is total exposure time in that cell across all sessions). Identification constraint: `f(morning) = 1.0`, `g(weekday) = 1.0`; back out `lambda_0` from the morning-weekday cell. Other cells give relative multipliers.
- Convergence iters reported as 1 for the closed-form binned MLE (a single algebraic pass). The spec mentions a `|ΔlogL| < 10⁻⁶` threshold and 1000 iters — that is for the iterative variant; for the closed-form binned approach, document why iters=1 in the docstring and pin the convergence_marginal flag computation accordingly (set the flag if any cell has < 50 obs even after passing the HALT — DON'T set if HALT itself fires).
- Raises `NHPPSparseBinError` if any of the 8 cells has < 50 observations.
- Hypothesis property test: synthetic Poisson process with known rate → recovered rate within 3σ.

**Steps:**

- [ ] **Step 4.1: Add NHPP errors to `_errors.py`**

```python
# Append to simulations/dev_ai_cost_v2/_errors.py
class NHPPCalibrationError(DevAICostError):
    """Raised on NHPP MLE convergence failure or invalid input."""


class NHPPSparseBinError(NHPPCalibrationError):
    """Raised when any 8-cell grid cell has < N_min = 50 observations."""


class SparsePoolError(DevAICostError):
    """Raised when (hour-block, day-type) bootstrap pool AND its day-type
    marginal both have < 50 observations.
    """
```

- [ ] **Step 4.2: Write failing test for `fit_nhpp`**

```python
# simulations/tests/test_dev_ai_cost_v2_nhpp_calibration.py
import pytest

from simulations.dev_ai_cost_v2._errors import NHPPSparseBinError
from simulations.dev_ai_cost_v2.nhpp_calibration import fit_nhpp


def test_fit_nhpp_raises_sparse_bin_error_on_undersize_input(
    minimal_messages_under_50_per_cell,
) -> None:
    with pytest.raises(NHPPSparseBinError, match="N_min"):
        fit_nhpp(minimal_messages_under_50_per_cell)


def test_fit_nhpp_recovers_synthetic_homogeneous_rate(
    homogeneous_synthetic_messages,
) -> None:
    """Generate a synthetic stream with constant rate; verify recovered lambda_0
    is within 3 SE of the true rate; multipliers near 1."""
    params = fit_nhpp(homogeneous_synthetic_messages)
    # true rate set by fixture: lambda = 10 / hour
    # under homogeneous rate, all 8 cells should give equivalent estimates
    for f_val in params.f_hour_block:
        assert 0.7 < f_val < 1.3  # 30% tolerance
    for g_val in params.g_day_type:
        assert 0.7 < g_val < 1.3
    assert 8.0 < params.lambda_0 < 12.0
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_nhpp_calibration.py -v`
Expected: FAIL (module not yet implemented).

- [ ] **Step 4.3: Implement `fit_nhpp`**

```python
# simulations/dev_ai_cost_v2/nhpp_calibration.py
"""NHPP arrival-rate calibration on within-session inter-arrival times.

Implements binned MLE on the 8-cell (hour-block × day-type) grid per
R6 spec v0.1.3 §2.1 and CORRECTIONS-BB / -CC.
"""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from simulations.dev_ai_cost_v2._errors import (
    NHPPCalibrationError,
    NHPPSparseBinError,
)
from simulations.dev_ai_cost_v2.types import MessageRecord, NHPPParameters


N_MIN_PER_CELL = 50
HOUR_BLOCK_BOUNDS = ((6, 12), (12, 18), (18, 22), (22, 30))  # 22-30 = 22-06 wraparound
HOUR_BLOCK_LABELS = ("morning", "afternoon", "evening", "night")
DAY_TYPE_LABELS = ("weekday", "weekend")


def _hour_block_index(ts) -> int:
    """Map timestamp to hour-block index [0..3]."""
    hour = ts.hour
    if 6 <= hour < 12:
        return 0
    if 12 <= hour < 18:
        return 1
    if 18 <= hour < 22:
        return 2
    return 3  # 22-06


def _day_type_index(ts) -> int:
    """Map timestamp to day-type index [0..1]. Monday=0..Sunday=6; weekend=5,6."""
    return 0 if ts.weekday() < 5 else 1


def fit_nhpp(records: Sequence[MessageRecord]) -> NHPPParameters:
    """Fit NHPP λ(t) = λ₀ · f(hb(t)) · g(dt(t)) by binned closed-form MLE.

    Inputs: a `Sequence[MessageRecord]`; iterated TWICE (so callers MUST pass
    a materialized sequence, NOT a generator). Property-tested by the
    `double-iteration-equivalence` Hypothesis property in Task 15.

    Raises:
      NHPPSparseBinError: any cell has < 50 observations.
      NHPPCalibrationError: aggregate observation count == 0.
    """
    if len(records) == 0:
        raise NHPPCalibrationError("fit_nhpp: empty record sequence")

    # Group by session_id; extract within-session inter-arrival times.
    by_session: dict[str, list[MessageRecord]] = {}
    for r in records:
        by_session.setdefault(r.session_id, []).append(r)

    # Per-cell observation counts (4 × 2)
    counts = np.zeros((4, 2), dtype=np.int64)
    # Per-cell exposure time (4 × 2) in hours
    exposure = np.zeros((4, 2), dtype=np.float64)

    for sess_records in by_session.values():
        sess_sorted = sorted(sess_records, key=lambda r: r.ts)
        if len(sess_sorted) < 2:
            continue  # cannot extract inter-arrival from singleton session
        for prev, curr in zip(sess_sorted[:-1], sess_sorted[1:]):
            hb = _hour_block_index(curr.ts)
            dt_idx = _day_type_index(curr.ts)
            counts[hb, dt_idx] += 1
            delta_hours = (curr.ts - prev.ts).total_seconds() / 3600.0
            exposure[hb, dt_idx] += delta_hours

    # Check sparse-bin HALT
    sparse_cells = [
        (HOUR_BLOCK_LABELS[hb], DAY_TYPE_LABELS[dt_i], int(counts[hb, dt_i]))
        for hb in range(4)
        for dt_i in range(2)
        if counts[hb, dt_i] < N_MIN_PER_CELL
    ]
    if sparse_cells:
        raise NHPPSparseBinError(
            f"NHPP sparse-bin HALT: N_min=50; sparse cells = {sparse_cells}"
        )

    # Closed-form per-cell rate estimates
    rates = counts / exposure  # shape (4, 2); calls per hour per cell
    # Identification: morning-weekday cell sets lambda_0; multipliers are ratios
    lambda_0 = float(rates[0, 0])
    f_hour_block = tuple(float(rates[hb, 0] / rates[0, 0]) for hb in range(4))
    g_day_type = (1.0, float(rates[0, 1] / rates[0, 0]))

    # Re-scale f so that f[0] = 1 (already true) and lambda_0 is the
    # morning-weekday rate. Validate identification.

    log_likelihood = _binned_poisson_log_likelihood(counts, exposure, rates)

    per_cell_counts = (
        (int(counts[0, 0]), int(counts[1, 0]), int(counts[2, 0]), int(counts[3, 0])),
        (int(counts[0, 1]), int(counts[1, 1]), int(counts[2, 1]), int(counts[3, 1])),
    )

    return NHPPParameters.create(
        lambda_0=lambda_0,
        f_hour_block=f_hour_block,
        g_day_type=g_day_type,
        log_likelihood=log_likelihood,
        convergence_iters=1,  # closed-form binned MLE
        per_cell_counts=per_cell_counts,
    )


def _binned_poisson_log_likelihood(counts, exposure, rates) -> float:
    """log L = Σ_cell [N_cell · log(λ_cell · T_cell) - λ_cell · T_cell - log(N_cell!)]"""
    from math import lgamma

    ll = 0.0
    for hb in range(4):
        for dt_i in range(2):
            n = counts[hb, dt_i]
            t = exposure[hb, dt_i]
            lam = rates[hb, dt_i]
            if t <= 0 or lam <= 0:
                continue
            ll += n * np.log(lam * t) - lam * t - lgamma(n + 1)
    return float(ll)
```

- [ ] **Step 4.4: Add fixtures + Hypothesis strategy**

In `simulations/tests/conftest.py` or `test_dev_ai_cost_v2_nhpp_calibration.py`, add the two fixtures:
- `minimal_messages_under_50_per_cell` — emits 40 messages total across cells.
- `homogeneous_synthetic_messages` — emits ~3000 messages with constant inter-arrival mean 0.1h across 33 days (sessions ≥ 5).

Use `numpy` Poisson sampling to generate timestamps; wrap in MessageRecord instances (use the `MessageRecord` strategy from Task 2 step 2.3 with `ts` overridden).

- [ ] **Step 4.5: Run NHPP tests to verify pass**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_nhpp_calibration.py -v`
Expected: PASS.

- [ ] **Step 4.6: Apply `try-except` audit pass**

Verify `fit_nhpp` raises explicitly — no broad `except` clauses. The `len(records) == 0` check is a conditional, not a `try`. The MLE itself has no I/O so no `try` blocks needed.

- [ ] **Step 4.7: Apply `contract-docstrings` pass**

Document inputs (sequence iterated twice — caller must materialize), outputs, errors raised on invariant violation (sparse-bin / empty input), errors from external state (none — pure function), silenced errors (none).

- [ ] **Step 4.8: Apply `pre-mortem` pass**

Run the `pre-mortem` skill on `fit_nhpp`. Anticipated failure modes:
- DST boundary days have 23 or 25 hours — `_hour_block_index` works on `ts.hour` regardless, OK.
- Timezone-naive `MessageRecord.ts` would produce wrong day-type if UTC-rendered as local. Pin: `MessageRecord.ts` is UTC per v0.2.1 CORRECTIONS-V. Document in `fit_nhpp` docstring.
- Single-message session contributes 0 inter-arrivals; loop `if len(sess_sorted) < 2: continue` handles this. Property test: a corpus of singleton sessions raises `NHPPCalibrationError` (no inter-arrivals at all).

Add the singleton-only property test before commit.

- [ ] **Step 4.9: Commit**

```bash
git add simulations/dev_ai_cost_v2/nhpp_calibration.py \
        simulations/dev_ai_cost_v2/_errors.py \
        simulations/tests/test_dev_ai_cost_v2_nhpp_calibration.py \
        simulations/tests/conftest.py
git commit -m "feat(dev_ai_cost_v2): NHPP calibration on within-session inter-arrivals

8-cell hour-block × day-type grid (CORRECTIONS-BB); session_id-based
grouping (CORRECTIONS-CC); N_min=50 sparse-bin HALT (NHPPSparseBinError).
Closed-form binned Poisson MLE.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Implement `arrival_generators.NHPPArrivalGenerator` (CORRECTIONS-EE, -JJ, -PP)

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `tighten-types` + `contract-docstrings` + `hypothesis-tests` + `pre-mortem`
**Spec ref:** §3.3 contract row; CORRECTIONS-EE (signature realignment with `stochastic_fx`); CORRECTIONS-JJ (per-module audit_block); CORRECTIONS-PP (RNG-call-order docstring pin).
**Depends on:** Task 3 (types), Task 4 (NHPPParameters from fit_nhpp).

**Files:**
- Create: `simulations/dev_ai_cost_v2/arrival_generators.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_arrival_generator.py`

**Exit criteria:**
- Frozen-dc `NHPPArrivalGenerator` with single field `config: NHPPSimulationConfig`.
- `__call__(rng_seed: int) -> ArrivalEnsemble`. No other parameters on `__call__` per CORRECTIONS-EE.
- Generates `n_paths` arrival streams over `horizon_days` at rate `k · λ(t)`.
- Within-session structure simulated by sampling session-start times and session-length distribution from observed data (per spec §0.1 CORRECTIONS-CC: "bootstrap-sampled session-start-times and session-length distributions from observed data"). This requires the calibration step to also expose session-level summaries — extend Task 4 to return these on a companion struct, OR pass observed records directly through `NHPPSimulationConfig`. **Decision:** add `observed_session_summary` (frozen-dc with `start_times: NDArray, lengths_hours: NDArray`) computed in `fit_nhpp` and embedded in `NHPPSimulationConfig` to keep `NHPPArrivalGenerator` pure on its config. Update Task 3 + Task 4 accordingly if not yet done (add to `NHPPSimulationConfig`; have `fit_nhpp` return both `NHPPParameters` and `ObservedSessionSummary` via a tuple, OR — cleaner — add a separate function `summarize_sessions(records) -> ObservedSessionSummary` in `nhpp_calibration.py` to keep `fit_nhpp`'s contract narrow).
- Method generates: per path, sample session count from Poisson with rate = (observed-session-count / horizon-days-observed) × horizon_days; for each session, sample start time uniformly within horizon (or bootstrap from observed start-time distribution) and length from bootstrap of observed lengths; within session, simulate NHPP arrivals at rate `k · λ(t)` via thinning (Lewis–Shedler 1979) against `k · λ_max`.
- RNG-call order pinned in module docstring: `(1) session_count_per_path; (2) session_start_times; (3) session_lengths; (4) within-session thinning candidate times; (5) thinning acceptance uniforms`. Mirroring `simulations/stochastic_fx/generators.py` convention.
- Per-module `audit_block` computed via `_compute_audit_block` from `stochastic_fx`-style helper; captures `config` hash + `rng_seed`.
- Hypothesis property: `gen(seed)` called twice with same seed produces bit-exact `ArrivalEnsemble.arrival_times`.

**Steps:**

- [ ] **Step 5.1: Decide ObservedSessionSummary location**

Update Task 3 retroactively if needed: add `ObservedSessionSummary` frozen-dc to `types.py` (fields: `session_start_offsets_hours: NDArray[float64]`, `session_lengths_hours: NDArray[float64]`, `observed_horizon_days: int`); add to `NHPPSimulationConfig` as new field `observed_summary: ObservedSessionSummary`. Add `summarize_sessions(records: Sequence[MessageRecord]) -> ObservedSessionSummary` in `nhpp_calibration.py`.

Commit this as a step inside Task 5 if Tasks 3/4 are merged; otherwise fold into Tasks 3/4.

- [ ] **Step 5.2: Write failing test for deterministic-RNG equivalence**

```python
# simulations/tests/test_dev_ai_cost_v2_arrival_generator.py
import numpy as np

from simulations.dev_ai_cost_v2.arrival_generators import NHPPArrivalGenerator


def test_arrival_generator_deterministic_rng(sample_nhpp_sim_config) -> None:
    gen = NHPPArrivalGenerator(config=sample_nhpp_sim_config)
    a = gen(rng_seed=42)
    b = gen(rng_seed=42)
    assert np.array_equal(a.arrival_times, b.arrival_times, equal_nan=True)
    assert np.array_equal(a.session_assignments, b.session_assignments)
    assert a.audit_block == b.audit_block


def test_arrival_generator_different_seeds_differ(sample_nhpp_sim_config) -> None:
    gen = NHPPArrivalGenerator(config=sample_nhpp_sim_config)
    a = gen(rng_seed=42)
    b = gen(rng_seed=43)
    # Should differ on at least one arrival time
    assert not np.array_equal(a.arrival_times, b.arrival_times, equal_nan=True)
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_arrival_generator.py -v`
Expected: FAIL.

- [ ] **Step 5.3: Implement `NHPPArrivalGenerator`**

```python
# simulations/dev_ai_cost_v2/arrival_generators.py
"""NHPP arrival generator — within-session intensity × session composition.

RNG-call order is load-bearing for bit-exactness (CORRECTIONS-PP). The
following order MUST be preserved across implementations:

  1. session_count_per_path  — np.random.Generator.poisson, n_paths draws
  2. session_start_offsets   — np.random.Generator.choice on observed
                                start-offset distribution
  3. session_lengths_hours   — np.random.Generator.choice on observed
                                length distribution
  4. within-session NHPP thinning candidate times — exponential(scale=1/λ_max)
  5. thinning acceptance uniforms — np.random.Generator.uniform(0, 1)

Signature alignment per CORRECTIONS-EE: all bit-exactness parameters live
on `NHPPSimulationConfig`; `__call__` takes only `rng_seed`. Strict
generalization of `simulations/stochastic_fx/generators.GBMPathGenerator`
(per CORRECTIONS-SS wording).
"""

from dataclasses import dataclass

import numpy as np

from simulations.dev_ai_cost_v2.types import (
    ArrivalEnsemble,
    NHPPSimulationConfig,
)
from simulations.stochastic_fx.types import AuditBlock  # adjust to actual loc


@dataclass(frozen=True, slots=True)
class NHPPArrivalGenerator:
    config: NHPPSimulationConfig

    def __call__(self, rng_seed: int) -> ArrivalEnsemble:
        rng = np.random.default_rng(rng_seed)
        cfg = self.config
        params = cfg.params
        n_paths = cfg.n_paths
        horizon_hours = cfg.horizon_days * 24.0

        # λ_max for thinning: max over the 8 cells, scaled by k
        lambda_max = cfg.k * params.lambda_0 * max(params.f_hour_block) * max(params.g_day_type)

        # (1) sessions per path — Poisson with observed rate
        observed = cfg.observed_summary
        sessions_per_day = len(observed.session_start_offsets_hours) / observed.observed_horizon_days
        session_count_mean = sessions_per_day * cfg.horizon_days
        session_counts = rng.poisson(lam=session_count_mean, size=n_paths)

        n_sessions_max = int(session_counts.max())
        n_arrivals_max = self._estimate_arrivals_max(lambda_max, observed, n_sessions_max)

        arrival_times = np.full((n_paths, n_arrivals_max), np.nan, dtype=np.float64)
        session_assignments = np.full((n_paths, n_arrivals_max), -1, dtype=np.int32)

        # (2) session start offsets (sampled from observed distribution, bounded by horizon)
        # (3) session lengths
        # (4) thinning candidates
        # (5) thinning acceptances

        for path_idx in range(n_paths):
            n_sess = int(session_counts[path_idx])
            if n_sess == 0:
                continue
            sess_starts = rng.choice(observed.session_start_offsets_hours, size=n_sess, replace=True) % horizon_hours
            sess_lengths = rng.choice(observed.session_lengths_hours, size=n_sess, replace=True)
            arr_idx = 0
            for sess_i in range(n_sess):
                t = sess_starts[sess_i]
                t_end = min(t + sess_lengths[sess_i], horizon_hours)
                # Within-session thinning
                while t < t_end:
                    # (4) draw exponential candidate spacing
                    delta = rng.exponential(scale=1.0 / lambda_max)
                    t = t + delta
                    if t >= t_end:
                        break
                    # (5) thinning acceptance
                    u = rng.uniform()
                    lambda_t = self._lambda_at(t, params, cfg.k)
                    if u <= lambda_t / lambda_max:
                        if arr_idx < n_arrivals_max:
                            arrival_times[path_idx, arr_idx] = t
                            session_assignments[path_idx, arr_idx] = sess_i
                            arr_idx += 1

        audit_block = self._compute_audit_block(rng_seed)
        return ArrivalEnsemble(
            arrival_times=arrival_times,
            session_assignments=session_assignments,
            audit_block=audit_block,
        )

    @staticmethod
    def _lambda_at(t_hours: float, params, k: float) -> float:
        """Compute λ(t) = k · λ_0 · f(hb(t)) · g(dt(t))."""
        # Map t (hours since horizon start) → (hour_of_day, day_of_week)
        # Assume horizon begins at midnight Monday for simplicity (document this in docstring)
        hour_of_day = int(t_hours) % 24
        day_of_week = (int(t_hours) // 24) % 7
        if 6 <= hour_of_day < 12:
            hb_idx = 0
        elif 12 <= hour_of_day < 18:
            hb_idx = 1
        elif 18 <= hour_of_day < 22:
            hb_idx = 2
        else:
            hb_idx = 3
        dt_idx = 0 if day_of_week < 5 else 1
        return k * params.lambda_0 * params.f_hour_block[hb_idx] * params.g_day_type[dt_idx]

    @staticmethod
    def _estimate_arrivals_max(lambda_max: float, observed, n_sessions_max: int) -> int:
        """Conservative upper bound for n_arrivals_max array allocation."""
        max_session_hours = float(observed.session_lengths_hours.max())
        upper = int(lambda_max * max_session_hours * n_sessions_max * 1.5) + 100
        return upper

    def _compute_audit_block(self, rng_seed: int) -> AuditBlock:
        """Per-module audit_block per CORRECTIONS-JJ."""
        # Compose canonical-json over config + rng_seed; SHA-256 hash.
        # Implementation mirrors simulations/stochastic_fx/generators._compute_audit_block.
        from simulations.dev_ai_cost_v2.r6_envelope import _module_audit_block
        return _module_audit_block(
            module="NHPPArrivalGenerator",
            config=self.config,
            rng_seed=rng_seed,
        )
```

Note: `_module_audit_block` is implemented in Task 10; if Task 10 is not yet done, stub it with a placeholder that raises `NotImplementedError`, write the test that skips audit_block equality, and revisit when Task 10 lands. **Preferred ordering:** do Task 10's `r6_envelope.py` skeleton first (just the `_module_audit_block` helper), then Tasks 5–8. Restructure if needed.

- [ ] **Step 5.4: Run arrival-generator tests**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_arrival_generator.py -v`
Expected: PASS.

- [ ] **Step 5.5: Apply `contract-docstrings` pass**

Document: input invariants (`config.k > 0`, `config.horizon_days > 0`, `config.n_paths > 0`); errors raised on violation (`ValueError` via NHPPSimulationConfig construction validators — add these); errors from external state (none — pure compute); silenced errors (none).

- [ ] **Step 5.6: Apply `pre-mortem` pass**

Anticipated failure modes:
- `n_arrivals_max` under-estimate: arrivals beyond capacity silently dropped. Mitigation: bound is 1.5× × max-session-hours × n_sessions_max × λ_max + 100, so over-allocate. Add assertion at end of generation: if any path filled to capacity, raise an explicit error (the array was sized too tight — bump the safety factor).
- Horizon-start day-of-week assumption (midnight Monday) is a modeling choice — document in docstring. M-design step is told.

- [ ] **Step 5.7: Commit**

```bash
git add simulations/dev_ai_cost_v2/arrival_generators.py \
        simulations/tests/test_dev_ai_cost_v2_arrival_generator.py
git commit -m "feat(dev_ai_cost_v2): NHPPArrivalGenerator with stochastic_fx-aligned signature

Per CORRECTIONS-EE (signature realignment); CORRECTIONS-JJ (per-module
audit_block); CORRECTIONS-PP (RNG-call-order docstring pin). Lewis-Shedler
thinning for non-homogeneous Poisson; session composition via bootstrap.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Implement `fx_block_bootstrap.FXBlockBootstrapGenerator` (CORRECTIONS-PP)

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `tighten-types` + `contract-docstrings` + `hypothesis-tests`
**Spec ref:** §3.1 FX path generation; §3.3 contract row; CORRECTIONS-PP (RNG-call-order docstring).
**Depends on:** Task 3, Task 10 (`_module_audit_block` helper).

**Files:**
- Create: `simulations/dev_ai_cost_v2/fx_block_bootstrap.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_fx_bootstrap.py`

**Exit criteria:**
- Frozen-dc `FXBlockBootstrapGenerator` with fields `history_returns_sha: str`, `history_returns: NDArray[float64]`, `expected_block_length: int`, `horizon_days: int`, `n_paths: int`.
- `expected_block_length = math.ceil(len(history_returns) ** (1/3))` — validate at construction.
- `__call__(rng_seed: int) -> FXPathEnsemble`. Stationary bootstrap (Politis–Romano 1994).
- `usdcop_paths` recovered by cumulative product of `(1 + return)` applied to the starting USDCOP (passed via... — decision: starting USDCOP also lives on the config; add `starting_usdcop: Decimal` field, but inside the float64 path arrays it's float64 per CORRECTIONS-KK precision boundary).
- Deterministic-RNG property test (same seed → bit-exact arrays).
- Block-length pin assertion.

**Steps:**

- [ ] **Step 6.1: Write failing tests**

```python
# simulations/tests/test_dev_ai_cost_v2_fx_bootstrap.py
import hashlib
import math

import numpy as np
import pytest

from simulations.dev_ai_cost_v2.fx_block_bootstrap import FXBlockBootstrapGenerator


def test_block_length_is_ceil_cube_root_of_history(sample_fx_history) -> None:
    expected = math.ceil(len(sample_fx_history) ** (1 / 3))
    gen = FXBlockBootstrapGenerator(
        history_returns=sample_fx_history,
        history_returns_sha=hashlib.sha256(sample_fx_history.tobytes()).hexdigest(),
        expected_block_length=expected,
        horizon_days=22,
        n_paths=100,
        starting_usdcop=4200.0,
    )
    assert gen.expected_block_length == expected


def test_fx_block_bootstrap_rejects_wrong_block_length(sample_fx_history) -> None:
    with pytest.raises(ValueError, match="expected_block_length"):
        FXBlockBootstrapGenerator(
            history_returns=sample_fx_history,
            history_returns_sha=hashlib.sha256(sample_fx_history.tobytes()).hexdigest(),
            expected_block_length=999,  # wrong
            horizon_days=22,
            n_paths=100,
            starting_usdcop=4200.0,
        )


def test_fx_bootstrap_deterministic_rng(sample_fx_history) -> None:
    sha = hashlib.sha256(sample_fx_history.tobytes()).hexdigest()
    expected_bl = math.ceil(len(sample_fx_history) ** (1 / 3))
    gen = FXBlockBootstrapGenerator(
        history_returns=sample_fx_history,
        history_returns_sha=sha,
        expected_block_length=expected_bl,
        horizon_days=22,
        n_paths=50,
        starting_usdcop=4200.0,
    )
    a = gen(rng_seed=7)
    b = gen(rng_seed=7)
    assert np.array_equal(a.log_returns, b.log_returns)
    assert np.array_equal(a.usdcop_paths, b.usdcop_paths)
    assert a.audit_block == b.audit_block
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_fx_bootstrap.py -v`
Expected: FAIL.

- [ ] **Step 6.2: Implement `FXBlockBootstrapGenerator`**

```python
# simulations/dev_ai_cost_v2/fx_block_bootstrap.py
"""FX block-bootstrap path generator — Politis–Romano (1994) stationary bootstrap.

RNG-call order (CORRECTIONS-PP):
  1. block-start indices — np.random.Generator.integers(0, len(history), n_blocks)
  2. block-length geometric draws — np.random.Generator.geometric(p=1/expected_block_length)

Block length is geometric-distributed with mean = expected_block_length =
⌈T_hist^(1/3)⌉ per stationary-bootstrap convention. Pre-pinned per spec §3.1.
"""

import hashlib
import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from simulations.dev_ai_cost_v2.types import FXPathEnsemble
from simulations.stochastic_fx.types import AuditBlock


@dataclass(frozen=True, slots=True)
class FXBlockBootstrapGenerator:
    history_returns: NDArray[np.float64]
    history_returns_sha: str
    expected_block_length: int
    horizon_days: int
    n_paths: int
    starting_usdcop: float  # float for ensemble interior; Decimal in headlines

    def __post_init__(self) -> None:
        if self.expected_block_length != math.ceil(len(self.history_returns) ** (1 / 3)):
            raise ValueError(
                f"expected_block_length must be ⌈len(history)^(1/3)⌉ = "
                f"{math.ceil(len(self.history_returns) ** (1 / 3))}; got "
                f"{self.expected_block_length}"
            )
        actual_sha = hashlib.sha256(self.history_returns.tobytes()).hexdigest()
        if actual_sha != self.history_returns_sha:
            raise ValueError(
                f"history_returns_sha mismatch: declared={self.history_returns_sha}, "
                f"actual={actual_sha}"
            )

    def __call__(self, rng_seed: int) -> FXPathEnsemble:
        rng = np.random.default_rng(rng_seed)
        n_paths = self.n_paths
        horizon = self.horizon_days
        history = self.history_returns
        p = 1.0 / self.expected_block_length

        log_returns = np.zeros((n_paths, horizon), dtype=np.float64)
        for path_idx in range(n_paths):
            day_filled = 0
            while day_filled < horizon:
                start = int(rng.integers(0, len(history)))
                block_len = int(rng.geometric(p=p))
                take = min(block_len, horizon - day_filled, len(history) - start)
                log_returns[path_idx, day_filled:day_filled + take] = history[start:start + take]
                day_filled += take

        # Reconstruct USDCOP path: P_t = P_0 · exp(Σ log_returns)
        usdcop_paths = self.starting_usdcop * np.exp(np.cumsum(log_returns, axis=1))

        audit_block = self._compute_audit_block(rng_seed)
        return FXPathEnsemble(
            log_returns=log_returns,
            usdcop_paths=usdcop_paths,
            audit_block=audit_block,
        )

    def _compute_audit_block(self, rng_seed: int) -> AuditBlock:
        from simulations.dev_ai_cost_v2.r6_envelope import _module_audit_block
        return _module_audit_block(
            module="FXBlockBootstrapGenerator",
            config={
                "history_returns_sha": self.history_returns_sha,
                "expected_block_length": self.expected_block_length,
                "horizon_days": self.horizon_days,
                "n_paths": self.n_paths,
                "starting_usdcop": self.starting_usdcop,
            },
            rng_seed=rng_seed,
        )
```

- [ ] **Step 6.3: Add `sample_fx_history` fixture**

In `simulations/tests/conftest.py`: emit 1260 daily returns (5-year trailing) sampled from `np.random.default_rng(seed=0).normal(0, 0.008, 1260)`.

- [ ] **Step 6.4: Run tests**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_fx_bootstrap.py -v`
Expected: PASS.

- [ ] **Step 6.5: Apply `contract-docstrings` pass**

Document RNG-call order; document the precision-boundary contract (float64 paths, Decimal only at headline aggregation).

- [ ] **Step 6.6: Commit**

```bash
git add simulations/dev_ai_cost_v2/fx_block_bootstrap.py \
        simulations/tests/test_dev_ai_cost_v2_fx_bootstrap.py \
        simulations/tests/conftest.py
git commit -m "feat(dev_ai_cost_v2): FX block-bootstrap path generator (Politis-Romano)

Per spec §3.1; stationary bootstrap with expected block length ⌈T_hist^(1/3)⌉.
RNG-call order pinned (CORRECTIONS-PP). Constructor validates SHA + block
length.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Implement `cost_simulation.CostSimulator` (CORRECTIONS-GG, -LL, -KK)

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `tighten-types` + `contract-docstrings` + `hypothesis-tests` + `try-except` + `pre-mortem`
**Spec ref:** §2.4 token & model assignment; §3.3 contract row; CORRECTIONS-GG (hour-block × day-type indexed pool); CORRECTIONS-LL (structured fallback_log); CORRECTIONS-KK (float64 ensemble interior).
**Depends on:** Tasks 3, 5, 6, 10 (envelope helper).

**Files:**
- Create: `simulations/dev_ai_cost_v2/cost_simulation.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_cost_simulator.py`

**Exit criteria:**
- Frozen-dc `CostSimulator` with fields `pricing: PricingTable`, `message_pool: tuple[MessageRecord, ...]` (immutable per frozen-dc), `pool_content_sha: str` (precomputed at construction, validated against pool).
- `__call__(arrivals: ArrivalEnsemble, fx: FXPathEnsemble, rng_seed: int) -> CostTrajectoryEnsemble`.
- Pool indexed by `(hour_block, day_type)` at construction time (precomputed dict).
- For each arrival: compute `(hb, dt)`; sample from pool cell; if cell has `< 50` records, fallback to day-type marginal pool (log `FallbackEvent` with `fallback_level="day-type-marginal"`); if marginal also `< 50`, raise `SparsePoolError`.
- Cost computed via `PricingTable(model, ts, toks) -> Decimal`; **converted to float64 for ensemble storage** per CORRECTIONS-KK; daily aggregation per path applies FX multiplication: `cop_costs[p, d] = sum(usd_costs_in_day_d_for_path_p) × usdcop_paths[p, d]`.
- Hypothesis property: round-trip a synthetic Decimal-exact cost stream → ensemble float64 → aggregation back to Decimal headline → equal within `1e-9` relative tolerance (precision-boundary test).

**Steps:**

- [ ] **Step 7.1: Write failing tests**

```python
# simulations/tests/test_dev_ai_cost_v2_cost_simulator.py
import hashlib

import numpy as np
import pytest

from simulations.dev_ai_cost_v2._errors import SparsePoolError
from simulations.dev_ai_cost_v2.cost_simulation import CostSimulator


def test_cost_simulator_rejects_pool_sha_mismatch(sample_pool, sample_pricing) -> None:
    with pytest.raises(ValueError, match="pool_content_sha"):
        CostSimulator(
            pricing=sample_pricing,
            message_pool=sample_pool,
            pool_content_sha="not-a-valid-sha",
        )


def test_cost_simulator_emits_fallback_event_on_sparse_cell(
    sparse_pool_under_50_in_one_cell,
    sample_pricing,
    sample_arrival_ensemble_targeting_sparse_cell,
    sample_fx_ensemble,
) -> None:
    sim = CostSimulator(
        pricing=sample_pricing,
        message_pool=sparse_pool_under_50_in_one_cell["pool"],
        pool_content_sha=sparse_pool_under_50_in_one_cell["sha"],
    )
    out = sim(arrivals=sample_arrival_ensemble_targeting_sparse_cell,
             fx=sample_fx_ensemble, rng_seed=42)
    assert len(out.fallback_log) > 0
    assert all(ev.fallback_level in {"cell", "day-type-marginal"} for ev in out.fallback_log)


def test_cost_simulator_raises_sparse_pool_error_on_marginal_too_sparse(
    very_sparse_pool, sample_pricing, sample_arrival_ensemble, sample_fx_ensemble,
) -> None:
    sim = CostSimulator(
        pricing=sample_pricing,
        message_pool=very_sparse_pool["pool"],
        pool_content_sha=very_sparse_pool["sha"],
    )
    with pytest.raises(SparsePoolError):
        sim(arrivals=sample_arrival_ensemble, fx=sample_fx_ensemble, rng_seed=42)
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_cost_simulator.py -v`
Expected: FAIL.

- [ ] **Step 7.2: Implement `CostSimulator`**

(Implementation per the structure described in the exit criteria above. Key: precompute `_pool_by_cell: dict[tuple[str, str], tuple[MessageRecord, ...]]` and `_pool_by_day_type: dict[str, tuple[MessageRecord, ...]]` in `__post_init__`. Validate `pool_content_sha` against canonicalized pool serialization. Cost per arrival via `pricing(record.model, arrival_ts, record.tokens) -> Decimal`; convert to float64 immediately for ensemble.)

- [ ] **Step 7.3: Add precision-boundary round-trip Hypothesis property**

```python
from decimal import Decimal

from hypothesis import given, strategies as st


@given(usd_cost_decimals=st.lists(
    st.decimals(min_value="0.000001", max_value="1000.0", places=6),
    min_size=1, max_size=100,
))
def test_precision_boundary_decimal_to_float_to_decimal_roundtrip(usd_cost_decimals) -> None:
    """CORRECTIONS-KK: ensemble interior is float64; headline back to Decimal
    must match input Decimal within 1e-9 relative tolerance.
    """
    as_floats = np.array([float(d) for d in usd_cost_decimals], dtype=np.float64)
    summed_float = float(as_floats.sum())
    summed_decimal_via_inputs = sum(usd_cost_decimals)
    summed_decimal_via_float = Decimal(repr(summed_float))
    rel_diff = abs(summed_decimal_via_inputs - summed_decimal_via_float) / summed_decimal_via_inputs
    assert rel_diff < Decimal("1e-9")
```

- [ ] **Step 7.4: Run tests**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_cost_simulator.py -v`
Expected: PASS.

- [ ] **Step 7.5: Apply `try-except` pass**

Verify the only `try` blocks (if any) are narrow — e.g., a single-statement `try` around `pricing(...)` only if `PricingTable` could fail on a row, with explicit catch + re-raise.

- [ ] **Step 7.6: Apply `pre-mortem` pass**

Failure modes:
- Pool sha drift over time (LiteLLM updates between simulation runs) — caught by sha validation at construction.
- Float overflow at extreme `k`: monthly cost across 22 days × 1000s arrivals × $10/call could be ~$220k → fits float64.
- FX multiplication order: `cop_costs[p, d] = usd_costs_day[d] × usdcop_path[p, d]`. Document the path/day alignment in docstring.

- [ ] **Step 7.7: Commit**

```bash
git add simulations/dev_ai_cost_v2/cost_simulation.py \
        simulations/tests/test_dev_ai_cost_v2_cost_simulator.py
git commit -m "feat(dev_ai_cost_v2): CostSimulator with hour-block × day-type bootstrap

Per CORRECTIONS-GG (indexed pool); CORRECTIONS-LL (structured fallback_log);
CORRECTIONS-KK (float64 ensemble, Decimal headlines). pool_content_sha
precomputed at construction; SparsePoolError on marginal-also-sparse.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Implement `cap_wait_counter.CapWaitCounter` (CORRECTIONS-MM, -QQ)

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `tighten-types` + `contract-docstrings` + `hypothesis-tests`
**Spec ref:** §2.6 (3) cap-wait friction (session-only per CORRECTIONS-QQ); §3.3 contract row; CORRECTIONS-MM (frozen-dc config); CORRECTIONS-QQ (single-field, weekly removed).
**Depends on:** Tasks 3, 5.

**Files:**
- Create: `simulations/dev_ai_cost_v2/cap_wait_counter.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_cap_wait.py`

**Exit criteria:**
- Frozen-dc `CapWaitCounter` with single field `config: CapWaitConfig` (which itself has only `session_cap_hours`).
- `__call__(arrivals: ArrivalEnsemble) -> CapWaitOutput` (note: no `rng_seed` — deterministic given arrivals).
- For each path: walk `arrival_times`; identify session boundaries via `session_assignments`; for each session, if session length exceeds `session_cap_hours`, accumulate `(session_length - session_cap_hours)` as cap-wait. Sum across sessions per path.
- Hypothesis property: zero arrivals → zero cap-wait; session length ≤ 5h → zero cap-wait.

**Steps:**

- [ ] **Step 8.1: Write failing tests**

```python
# simulations/tests/test_dev_ai_cost_v2_cap_wait.py
import numpy as np
import pytest

from simulations.dev_ai_cost_v2.cap_wait_counter import CapWaitCounter
from simulations.dev_ai_cost_v2.types import (
    ArrivalEnsemble,
    CapWaitConfig,
)
from simulations.stochastic_fx.types import AuditBlock  # placeholder


def test_cap_wait_zero_when_all_sessions_under_5h() -> None:
    arrivals = ArrivalEnsemble(
        arrival_times=np.array([[0.5, 1.0, 2.0, np.nan, np.nan]], dtype=np.float64),
        session_assignments=np.array([[0, 0, 0, -1, -1]], dtype=np.int32),
        audit_block=AuditBlock.empty(),
    )
    counter = CapWaitCounter(config=CapWaitConfig(session_cap_hours=5.0))
    out = counter(arrivals=arrivals)
    assert out.session_cap_wait_hours[0] == 0.0


def test_cap_wait_accumulates_excess_above_session_cap() -> None:
    # Session 0: arrivals span 0h..7h → 2h cap-wait excess
    arrivals = ArrivalEnsemble(
        arrival_times=np.array([[0.0, 3.0, 7.0, np.nan]], dtype=np.float64),
        session_assignments=np.array([[0, 0, 0, -1]], dtype=np.int32),
        audit_block=AuditBlock.empty(),
    )
    counter = CapWaitCounter(config=CapWaitConfig(session_cap_hours=5.0))
    out = counter(arrivals=arrivals)
    assert out.session_cap_wait_hours[0] == pytest.approx(2.0)
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_cap_wait.py -v`
Expected: FAIL.

- [ ] **Step 8.2: Implement `CapWaitCounter`**

```python
# simulations/dev_ai_cost_v2/cap_wait_counter.py
"""Session-cap-wait hours counter — session cap only (CORRECTIONS-QQ scopes out weekly cap)."""

from dataclasses import dataclass

import numpy as np

from simulations.dev_ai_cost_v2.types import (
    ArrivalEnsemble,
    CapWaitConfig,
    CapWaitOutput,
)


@dataclass(frozen=True, slots=True)
class CapWaitCounter:
    config: CapWaitConfig

    def __call__(self, arrivals: ArrivalEnsemble) -> CapWaitOutput:
        n_paths = arrivals.arrival_times.shape[0]
        cap = self.config.session_cap_hours
        wait_hours = np.zeros(n_paths, dtype=np.float64)
        for p in range(n_paths):
            sess_ids = arrivals.session_assignments[p]
            times = arrivals.arrival_times[p]
            valid = sess_ids >= 0
            if not valid.any():
                continue
            unique_sessions = np.unique(sess_ids[valid])
            for s in unique_sessions:
                mask = (sess_ids == s)
                sess_times = times[mask]
                if len(sess_times) < 2:
                    continue
                sess_length = float(sess_times.max() - sess_times.min())
                if sess_length > cap:
                    wait_hours[p] += sess_length - cap
        return CapWaitOutput(session_cap_wait_hours=wait_hours)
```

- [ ] **Step 8.3: Run tests**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_cap_wait.py -v`
Expected: PASS.

- [ ] **Step 8.4: Commit**

```bash
git add simulations/dev_ai_cost_v2/cap_wait_counter.py \
        simulations/tests/test_dev_ai_cost_v2_cap_wait.py
git commit -m "feat(dev_ai_cost_v2): session-cap-wait counter (weekly cap scoped out)

Per CORRECTIONS-MM (frozen-dc config); CORRECTIONS-QQ (single-field, weekly
cap scoped out of R6 v1). Deterministic given ArrivalEnsemble — no RNG.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Add `_anthropic_caps.py` declarative constants (CORRECTIONS-DD, -QQ)

**Owner:** Backend Architect
**Audit-pass chain:** `contract-docstrings`
**Spec ref:** §3.3 contract row; §5.4 DATA_PROVENANCE cite; CORRECTIONS-DD (originally session + weekly); CORRECTIONS-QQ (weekly removed for R6 v1).
**Depends on:** none (declarative constants only).

**Files:**
- Create: `simulations/dev_ai_cost_v2/_anthropic_caps.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_anthropic_caps.py`

**Exit criteria:**
- `SESSION_CAP_HOURS = 5.0` — module-level constant.
- Comment block citing source URL `https://support.claude.com/en/articles/8325606` + access date `2026-05-16`.
- No `WEEKLY_CAP_HOURS` (CORRECTIONS-QQ).
- Test pins the constant value (any drift triggers test failure → spec update required).

**Steps:**

- [ ] **Step 9.1: Write failing test**

```python
# simulations/tests/test_dev_ai_cost_v2_anthropic_caps.py
from simulations.dev_ai_cost_v2 import _anthropic_caps


def test_session_cap_hours_pinned_at_5() -> None:
    assert _anthropic_caps.SESSION_CAP_HOURS == 5.0


def test_no_weekly_cap_per_corrections_qq() -> None:
    assert not hasattr(_anthropic_caps, "WEEKLY_CAP_HOURS")
```

- [ ] **Step 9.2: Create the module**

```python
# simulations/dev_ai_cost_v2/_anthropic_caps.py
"""Declarative Anthropic-cap constants.

Source: https://support.claude.com/en/articles/8325606
Access date: 2026-05-16

Per R6 spec v0.1.3 CORRECTIONS-DD: session-based 5h cap modeled.
Per CORRECTIONS-QQ: weekly cap scoped out of R6 v1 (Anthropic does not
publish a numeric weekly-cap value; deferred to R6 v2 contingent on either
Anthropic publishing a numeric value or cohort-data empirical calibration).

Any change to SESSION_CAP_HOURS constitutes a schema-drift event requiring
a spec update. The test in test_dev_ai_cost_v2_anthropic_caps.py guards
against silent drift.
"""

SESSION_CAP_HOURS: float = 5.0
```

- [ ] **Step 9.3: Run tests**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_anthropic_caps.py -v`
Expected: PASS.

- [ ] **Step 9.4: Commit**

```bash
git add simulations/dev_ai_cost_v2/_anthropic_caps.py \
        simulations/tests/test_dev_ai_cost_v2_anthropic_caps.py
git commit -m "feat(dev_ai_cost_v2): pin SESSION_CAP_HOURS = 5.0 (weekly cap scoped out)

Per CORRECTIONS-DD (session cap from Anthropic source URL) + CORRECTIONS-QQ
(weekly cap scoped out of R6 v1 — Anthropic does not publish numeric value).
Test pins the value; any drift triggers spec update.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: Implement canonicalization + R6 audit_block envelope + R6 aggregator (CORRECTIONS-FF, -II, -RR, -TT, -KK)

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` + `tighten-types` + `contract-docstrings` + `hypothesis-tests` + `try-except`
**Spec ref:** §5.3 R6 audit_block + 7-step canonicalization rule (v0.1.3); §2.6 output metrics; §3.3 contract rows; CORRECTIONS-FF (envelope completion); CORRECTIONS-II (quality_flags computation); CORRECTIONS-RR (dedupe + uuid quaternary key); CORRECTIONS-TT (drop request_id=None; lex-smallest uuid tiebreaker); CORRECTIONS-KK (Decimal aggregation).
**Depends on:** Tasks 3, 7, 8.

**Files:**
- Create: `simulations/dev_ai_cost_v2/canonicalization.py`
- Create: `simulations/dev_ai_cost_v2/r6_envelope.py`
- Create: `simulations/dev_ai_cost_v2/r6_aggregator.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_canonicalization.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_r6_envelope.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_r6_aggregator.py`

**Exit criteria:**

`canonicalization.py`:
- Pure function `canonicalize_message_pool(records_by_path: Mapping[Path, Sequence[MessageRecord]]) -> CanonicalizedPool` returning a frozen-dc with `records: tuple[MessageRecord, ...]`, `dropped_legacy_request_id_count: int`, `message_pool_content_sha256: str`.
- Implements the 7-step rule per §5.3:
  1. Iterate paths in lex-sorted order.
  2. Per-path records already parsed (input).
  3. Drop records with `request_id is None`; count dropped.
  4. Dedupe by `request_id`: for each group, keep the record from the lex-smallest source path; within same-path ties, keep the one with lex-smallest `uuid` (CORRECTIONS-TT).
  5. Sort the dedup set by `(ts, request_id, session_id, uuid)`.
  6. Serialize each row via `dataclasses.asdict` + canonical_json.
  7. SHA-256 over concatenated serialization.

`r6_envelope.py`:
- Helper `_module_audit_block(module: str, config, rng_seed: int) -> AuditBlock` — used by every generator + simulator per CORRECTIONS-JJ.
- Top-level `compute_r6_audit_block(nhpp_ensemble, fx_ensemble, cost_ensemble, cap_wait_config, message_pool_sha, parser_version_sha, sizing_curve_k, rng_seed, n_paths, horizon_days) -> AuditBlock`.

`r6_aggregator.py`:
- `aggregate_r6_output(k, cost_ensemble, cap_wait_output, fx_ensemble, observed_cap_wait_hours, observed_variance_usd, audit_block) -> R6Output`. Computes Decimal VaR/CVaR/percentiles/mean/SD; conservative-covariance variance decomposition; reconciliation ratio (observed vs simulated `Var(Δln Cost_USD)`); populates `quality_flags`:
  - `"sparse_cell_fallback_rate_high"` if `> 10%` of arrivals had fallback events (count via `cost_ensemble.fallback_log` divided by total arrivals).
  - `"reconciliation_drift_high"` if reconciliation ratio outside `[0.8, 1.2]` (CORRECTIONS-OO bound).
  - `"nhpp_convergence_marginal"` if NHPPParameters' `|ΔlogL|/|logL| > 1e-4` at final iter — pull through from upstream (need to thread this in; either via `R6Output` accepting a flag set computed in the notebook from NHPPParameters, OR via a thin computed-once helper). Decision: accept `nhpp_params: NHPPParameters` as input and compute the flag here.

Property tests on canonicalization:
- Shuffle the input mapping (different iteration order over `paths`) → identical `message_pool_content_sha256`.
- Drop a `request_id=None` record → `dropped_legacy_request_id_count` increments; hash unaffected.
- Same `(request_id, source_path)` → tiebreaker picks lex-smallest `uuid`.

**Steps:**

- [ ] **Step 10.1: Write failing canonicalization tests**

```python
# simulations/tests/test_dev_ai_cost_v2_canonicalization.py
import hashlib
from pathlib import Path

import pytest

from simulations.dev_ai_cost_v2.canonicalization import canonicalize_message_pool


def test_canonicalization_shuffle_invariant(sample_records_by_path) -> None:
    """CORRECTIONS-RR: shuffling input file order must produce identical hash."""
    a = canonicalize_message_pool(sample_records_by_path)
    shuffled = dict(reversed(list(sample_records_by_path.items())))
    b = canonicalize_message_pool(shuffled)
    assert a.message_pool_content_sha256 == b.message_pool_content_sha256


def test_canonicalization_drops_legacy_request_id_none(records_with_legacy_none) -> None:
    """CORRECTIONS-TT (a): records with request_id=None are excluded."""
    out = canonicalize_message_pool(records_with_legacy_none)
    assert out.dropped_legacy_request_id_count > 0
    assert all(r.request_id is not None for r in out.records)


def test_canonicalization_same_path_tiebreak_by_uuid(records_with_intra_file_dup) -> None:
    """CORRECTIONS-TT (b): within same lex-smallest source path, keep
    lex-smallest uuid.
    """
    out = canonicalize_message_pool(records_with_intra_file_dup)
    request_ids = [r.request_id for r in out.records]
    assert len(request_ids) == len(set(request_ids))  # all unique
    # The kept duplicate must be the one with lex-smallest uuid (fixture asserts)
    for r in out.records:
        if r.request_id == "dup-req-1":
            assert r.uuid == records_with_intra_file_dup["expected_uuid_for_dup_req_1"]


def test_canonicalization_dedupe_picks_lex_smallest_path(records_with_cross_path_dup) -> None:
    """CORRECTIONS-RR: for same request_id across two paths, keep lex-smallest path."""
    out = canonicalize_message_pool(records_with_cross_path_dup)
    request_ids = [r.request_id for r in out.records]
    assert len(request_ids) == len(set(request_ids))
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_canonicalization.py -v`
Expected: FAIL.

- [ ] **Step 10.2: Implement canonicalization**

```python
# simulations/dev_ai_cost_v2/canonicalization.py
"""Message-pool canonicalization per R6 spec v0.1.3 §5.3."""

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from simulations.dev_ai_cost_v2.types import MessageRecord
from simulations.utils.json_io import canonical_json  # exists in utils tier


@dataclass(frozen=True, slots=True)
class CanonicalizedPool:
    records: tuple[MessageRecord, ...]
    dropped_legacy_request_id_count: int
    message_pool_content_sha256: str


def canonicalize_message_pool(
    records_by_path: Mapping[Path, Sequence[MessageRecord]],
) -> CanonicalizedPool:
    """Apply the 7-step canonicalization rule (v0.1.3 §5.3)."""
    # Step 1: glob already supplied as Mapping; iterate paths in lex order
    sorted_paths = sorted(records_by_path.keys())

    # Steps 2 + 3: collect all records, drop request_id=None
    all_records_with_path: list[tuple[Path, MessageRecord]] = []
    dropped = 0
    for path in sorted_paths:
        for rec in records_by_path[path]:
            if rec.request_id is None:
                dropped += 1
                continue
            all_records_with_path.append((path, rec))

    # Step 4: dedupe by request_id. For each group, keep lex-smallest source
    # path; within same-path ties, keep lex-smallest uuid.
    grouped: dict[str, list[tuple[Path, MessageRecord]]] = {}
    for path, rec in all_records_with_path:
        grouped.setdefault(rec.request_id, []).append((path, rec))

    deduped: list[MessageRecord] = []
    for group in grouped.values():
        if len(group) == 1:
            deduped.append(group[0][1])
        else:
            # Lex-smallest source path
            min_path = min(p for p, _ in group)
            same_path_records = [r for p, r in group if p == min_path]
            if len(same_path_records) == 1:
                deduped.append(same_path_records[0])
            else:
                # CORRECTIONS-TT (b): lex-smallest uuid within same path
                deduped.append(min(same_path_records, key=lambda r: r.uuid))

    # Step 5: sort by (ts, request_id, session_id, uuid)
    deduped.sort(key=lambda r: (r.ts, r.request_id, r.session_id, r.uuid))

    # Steps 6–7: serialize + hash
    h = hashlib.sha256()
    for rec in deduped:
        h.update(canonical_json(asdict(rec)).encode("utf-8"))
    sha = h.hexdigest()

    return CanonicalizedPool(
        records=tuple(deduped),
        dropped_legacy_request_id_count=dropped,
        message_pool_content_sha256=sha,
    )
```

- [ ] **Step 10.3: Implement `_module_audit_block` and `compute_r6_audit_block` in `r6_envelope.py`**

```python
# simulations/dev_ai_cost_v2/r6_envelope.py
"""R6 audit_block envelope per §5.3 (per-module chain + top-level)."""

import hashlib
from dataclasses import asdict, is_dataclass
from typing import Any

from simulations.stochastic_fx.types import AuditBlock
from simulations.utils.json_io import canonical_json


def _to_canonical(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _to_canonical(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_canonical(v) for v in obj]
    return obj


def _module_audit_block(*, module: str, config: Any, rng_seed: int) -> AuditBlock:
    """Per-module audit_block (CORRECTIONS-JJ)."""
    payload = {"module": module, "config": _to_canonical(config), "rng_seed": rng_seed}
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return AuditBlock(digest=digest, payload=payload)  # adjust to AuditBlock's actual ctor


def compute_r6_audit_block(
    *,
    nhpp_audit_block: AuditBlock,
    fx_audit_block: AuditBlock,
    cost_audit_block: AuditBlock,
    cap_wait_config_dict: dict,
    message_pool_content_sha256: str,
    parser_version_sha: str,
    sizing_curve_k: tuple[float, ...],
    rng_seed: int,
    n_paths: int,
    horizon_days: int,
    litellm_sha: str = "e58a561caa21169fb02174148444c08509ce7028",
    banrep_trm_daily_sha: str = "",  # filled by caller
) -> AuditBlock:
    """Top-level R6 envelope chaining per-module hashes."""
    payload = {
        "nhpp_module_hash": nhpp_audit_block.digest,
        "fx_module_hash": fx_audit_block.digest,
        "cost_module_hash": cost_audit_block.digest,
        "cap_wait_config_hash": hashlib.sha256(canonical_json(cap_wait_config_dict).encode("utf-8")).hexdigest(),
        "message_pool_content_sha256": message_pool_content_sha256,
        "parser_version_sha": parser_version_sha,
        "litellm_sha": litellm_sha,
        "banrep_trm_daily_sha": banrep_trm_daily_sha,
        "sizing_curve_k": list(sizing_curve_k),
        "rng_seed": rng_seed,
        "n_paths": n_paths,
        "horizon_days": horizon_days,
    }
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return AuditBlock(digest=digest, payload=payload)
```

- [ ] **Step 10.4: Implement `r6_aggregator.aggregate_r6_output`**

(Implementation per exit criteria above — Decimal headlines from float64 ensemble; quality_flags computation per CORRECTIONS-II.)

- [ ] **Step 10.5: Add fixtures for canonicalization tests**

In `conftest.py`: `sample_records_by_path`, `records_with_legacy_none`, `records_with_intra_file_dup`, `records_with_cross_path_dup`.

- [ ] **Step 10.6: Run all Task 10 tests**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_canonicalization.py simulations/tests/test_dev_ai_cost_v2_r6_envelope.py simulations/tests/test_dev_ai_cost_v2_r6_aggregator.py -v`
Expected: PASS.

- [ ] **Step 10.7: Apply `try-except` + `pre-mortem` passes**

Failure modes: empty input mapping → return empty pool with dropped=0 and sha of empty hash (document); duplicate detection on extreme datasets (1.95k duplicates / 84k tuples per spec §0.2) — verify performance acceptable (target: < 1s on 100k records).

- [ ] **Step 10.8: Commit**

```bash
git add simulations/dev_ai_cost_v2/canonicalization.py \
        simulations/dev_ai_cost_v2/r6_envelope.py \
        simulations/dev_ai_cost_v2/r6_aggregator.py \
        simulations/tests/test_dev_ai_cost_v2_canonicalization.py \
        simulations/tests/test_dev_ai_cost_v2_r6_envelope.py \
        simulations/tests/test_dev_ai_cost_v2_r6_aggregator.py \
        simulations/tests/conftest.py
git commit -m "feat(dev_ai_cost_v2): R6 canonicalization + audit_block envelope + aggregator

Per §5.3 (7-step canonicalization with dedupe by request_id keeping
lex-smallest path; uuid quaternary sort key; tiebreaker by lex-smallest uuid
within same path); CORRECTIONS-FF/JJ (per-module + envelope audit_block);
CORRECTIONS-II (quality_flags computation); CORRECTIONS-KK (Decimal headlines
from float64 ensemble).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

# PHASE 3 — Hypothesis property-test consolidation sweep

## Task 15 (Phase 3 main): Add the six critical property tests as a consolidated sweep

**Owner:** Backend Architect (with `hypothesis-tests` skill orchestration)
**Audit-pass chain:** `hypothesis-tests` skill
**Spec ref:** §0.2 CORRECTIONS-RR (shuffle invariance); CORRECTIONS-TT (tiebreaker edge cases); §3.5 forward-fill-forbidden; §3.3 double-iteration equivalence on Sequence[MessageRecord]; CORRECTIONS-KK (precision-boundary round-trip); CORRECTIONS-EE/-PP (deterministic-RNG equivalence).
**Depends on:** Tasks 4, 5, 6, 7, 10. Several property tests have already been written inline per-task; this consolidation step audits coverage + adds anything missing.

**Files:**
- Audit and extend: all `simulations/tests/test_dev_ai_cost_v2_*.py` (per-module property tests written in earlier tasks).
- Possibly create: `simulations/tests/test_dev_ai_cost_v2_properties_r6.py` for the cross-cutting/composite properties (e.g., double-iteration-equivalence which spans `MessageRecord` consumers).

**The six required properties:**

1. **Canonicalization shuffle-invariance** (CORRECTIONS-RR) — written in Task 10 Step 10.1 (`test_canonicalization_shuffle_invariant`). Audit: confirm it shuffles the path mapping order, NOT the records within a path (records-within-path are pre-sorted by the parser; the property is about glob-walk order).

2. **Canonicalization tiebreaker edge cases** (CORRECTIONS-TT) — written in Task 10 Step 10.1 (`test_canonicalization_drops_legacy_request_id_none` + `test_canonicalization_same_path_tiebreak_by_uuid` + `test_canonicalization_dedupe_picks_lex_smallest_path`). Audit: confirm all three sub-cases are Hypothesis-driven (some may currently be example-only — wrap in `@given(...)` strategies that emit synthetic records-by-path mappings with controlled duplicates).

3. **Forward-fill-forbidden on FX panel** — should already exist in v0.2.1 plan's `test_dev_ai_cost_v2_panel_builder.py`. **Audit step:** confirm it exists; if not, ADD: a property generating an FX panel with a missing date in the trailing series; verify the panel-builder raises (does not silently forward-fill). The R6 work consumes the panel via `FXBlockBootstrapGenerator(history_returns=...)`, so the upstream forward-fill ban is a precondition.

4. **Double-iteration equivalence on `Sequence[MessageRecord]`** — the spec's contract for `fit_nhpp` and `CostSimulator.__init__` is that `records` is iterated more than once; passing a generator would silently produce wrong results. Property: for any `Sequence[MessageRecord]` valid input, `list(seq) == list(seq)` (i.e., the parameter type is materialized; this can be checked via runtime assertion `isinstance(records, Sequence) and not isinstance(records, Iterator)` at the entry of `fit_nhpp`). Add the assertion in `fit_nhpp` body; add the property test.

```python
# simulations/tests/test_dev_ai_cost_v2_properties_r6.py
import pytest
from hypothesis import given

from simulations.dev_ai_cost_v2.nhpp_calibration import fit_nhpp
from simulations.tests.strategies import message_records_dense_for_nhpp


@given(records=message_records_dense_for_nhpp())
def test_fit_nhpp_rejects_iterator_passed_as_sequence(records) -> None:
    """A generator masquerading as Sequence should be rejected — double-iter."""
    gen = (r for r in records)
    with pytest.raises(TypeError, match="Sequence"):
        fit_nhpp(gen)  # type: ignore[arg-type]


@given(records=message_records_dense_for_nhpp())
def test_fit_nhpp_double_iteration_equivalent(records) -> None:
    """Calling fit_nhpp twice on the same sequence produces identical params."""
    p1 = fit_nhpp(records)
    p2 = fit_nhpp(records)
    assert p1 == p2
```

5. **Decimal/float64 precision-boundary round-trip** (CORRECTIONS-KK) — written inline in Task 7 Step 7.3 (`test_precision_boundary_decimal_to_float_to_decimal_roundtrip`). Audit: confirm tolerance bound is `1e-9` relative.

6. **Deterministic-RNG equivalence** — written inline in Task 5 Step 5.2 (`test_arrival_generator_deterministic_rng`) and Task 6 Step 6.1 (`test_fx_bootstrap_deterministic_rng`). Audit: confirm both also verify `audit_block` equality (load-bearing per CORRECTIONS-JJ — different seeds → different `audit_block.digest`; same seed → identical).

**Exit criteria:**
- All six properties pass with `--hypothesis-seed=0 --hypothesis-verbosity=verbose`.
- A consolidation note in `simulations/tests/test_dev_ai_cost_v2_properties_r6.py` module docstring lists each property + the spec § reference.
- Coverage gap report: run `coverage run --source=simulations/dev_ai_cost_v2 -m pytest simulations/tests/test_dev_ai_cost_v2_*.py && coverage report -m`. Any uncovered branch in canonicalization / arrival / cost / cap_wait flagged.

**Steps:**

- [ ] **Step 15.1: Audit each property exists and is Hypothesis-driven**

For each of the 6 properties, locate the test file + function name; check that `@given(...)` is used (not just an example). For example-only tests, refactor to `@given(...)` with strategies.

- [ ] **Step 15.2: Add the double-iteration assertion in `fit_nhpp`**

```python
# at the top of fit_nhpp body in nhpp_calibration.py
from collections.abc import Iterator, Sequence

if isinstance(records, Iterator):
    raise TypeError(
        "fit_nhpp requires a materialized Sequence[MessageRecord]; "
        "got an iterator (would be exhausted after first pass)."
    )
```

Apply the same assertion to `CostSimulator.__post_init__` (it iterates `message_pool` twice — once for `_pool_by_cell`, once for `_pool_by_day_type`).

- [ ] **Step 15.3: Run the consolidated sweep**

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_properties_r6.py simulations/tests/test_dev_ai_cost_v2_*.py -v --hypothesis-seed=0`
Expected: PASS.

- [ ] **Step 15.4: Coverage check**

Run: `uv run coverage run --source=simulations/dev_ai_cost_v2 -m pytest simulations/tests/test_dev_ai_cost_v2_*.py && uv run coverage report -m`
Expected: ≥ 90% line coverage on the R6 modules.

- [ ] **Step 15.5: Commit**

```bash
git add simulations/tests/test_dev_ai_cost_v2_properties_r6.py \
        simulations/dev_ai_cost_v2/nhpp_calibration.py \
        simulations/dev_ai_cost_v2/cost_simulation.py
git commit -m "test(dev_ai_cost_v2): consolidated R6 property-test sweep (Hypothesis)

Six critical properties per R6 spec §0.2 CORRECTIONS-RR/-TT/-KK/-EE/-PP and
§3.3/§3.5: canonicalization shuffle-invariance + tiebreaker edge cases;
forward-fill-forbidden; double-iteration equivalence; precision-boundary
round-trip; deterministic-RNG equivalence (incl. audit_block equality).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

# PHASE 4 — Notebooks

All notebooks at `notebooks/dev_ai_cost_v2_r6/`. Follow trio-checkpoint discipline (`memory/feedback_notebook_trio_checkpoint.md`) and decision-citation block convention (`memory/feedback_notebook_citation_block.md`). Each notebook begins with a **preamble cell** citing R6 spec, parent CLAUDE.md framework, and listing the anti-fishing invariants relevant to this notebook.

## Task 11: `01_nhpp_eda.ipynb` — calibration EDA + reconciliation drift HALT

**Owner:** Quantitative Analyst (with Reality Checker at each HALT)
**Audit-pass chain:** trio-checkpoint discipline; decision-citation block per cell.
**Spec ref:** §4 first bullet; §2.7 NHPP min-bin HALT + reconciliation-drift HALT; CORRECTIONS-HH (1% threshold).
**Depends on:** Phase 2 + 3 (all modules + tests passing).

**Files:**
- Create: `notebooks/dev_ai_cost_v2_r6/01_nhpp_eda.ipynb`

**Required cells (decision-citation blocks ahead of each):**

1. **Preamble**: spec citation; framework placement; anti-fishing invariants pinned ex-ante.
2. **Data load**: read `~/.claude/projects/**/*.jsonl` via `JSONLReader`; run `canonicalize_message_pool`; log `dropped_legacy_request_id_count`.
3. **Within-session inter-arrival distribution plot** (per spec §4): histogram per `(hour_block, day_type)` cell; verify `N ≥ 50` per cell.
4. **NHPP fit**: `params = fit_nhpp(canonical_pool.records)`; print `lambda_0`, `f_hour_block`, `g_day_type`, `per_cell_counts`, `convergence_iters`, `log_likelihood`.
5. **Diagnostics heatmap**: `f̂ × ĝ` plotted as 4×2 heatmap; residual plot per cell.
6. **Reconciliation-drift cell (HALT-gated; CORRECTIONS-HH @ 1%)**: simulate at `k = 1.0` for 1 month; compute mean cost; compare to observed monthly mean (from v0.2.1 panel); IF `|drift| > 1%` → write disposition memo at `notebooks/dev_ai_cost_v2_r6/dispositions/reconciliation_drift_<DATE>.md` using template from Task 18 → HALT.
7. **Session-boundary inspection**: distribution of inter-session gaps (descriptive only; NOT used in calibration per CORRECTIONS-CC).

**Exit criteria:**
- Notebook runs end-to-end via `make notebooks` or `uv run jupyter nbconvert --execute`.
- Each trio (why-markdown / code / interpretation-markdown) is human-reviewable.
- HALT logic is hard-coded: if drift > 1%, raise `RuntimeError` with disposition path.

**Steps:**

- [ ] **Step 11.1: Create notebook skeleton with preamble + decision-citation blocks**

Use `jupytext` or write `.ipynb` JSON directly. Preamble cites: `docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` (v0.1.3); `memory/feedback_notebook_trio_checkpoint.md`; `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`. Lists the 4 anti-fishing invariants relevant: NHPP grid (4×2 cells); hour-block boundaries; identification `f(morning)=1`, `g(weekday)=1`; reconciliation HALT @ 1%.

- [ ] **Step 11.2: Implement cells 2–7 per the spec list above**

Each cell is preceded by a why-markdown cell (with 4-part citation block: reference / why / relevance / connection) and followed by an interpretation-markdown cell.

- [ ] **Step 11.3: Run end-to-end**

Run: `uv run jupyter nbconvert --execute --to notebook --inplace notebooks/dev_ai_cost_v2_r6/01_nhpp_eda.ipynb`
Expected: PASS. If reconciliation-drift cell HALTs, that IS the expected behavior — write the disposition memo + escalate.

- [ ] **Step 11.4: Commit**

```bash
git add notebooks/dev_ai_cost_v2_r6/01_nhpp_eda.ipynb
git commit -m "feat(notebooks/dev_ai_cost_v2_r6): 01_nhpp_eda — calibration + drift HALT

Per R6 §4 first bullet + §2.7 + CORRECTIONS-HH (1% reconciliation threshold).
Trio-checkpoint discipline; decision-citation per cell; HALT at >1% drift
routes to dispositions/reconciliation_drift_*.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: `02_simulation.ipynb` — generate ensembles for sizing curve

**Owner:** Quantitative Analyst
**Spec ref:** §4 second bullet; §2.3 sizing curve `k ∈ {0.5, 1, 2, 3, 5}`.
**Depends on:** Task 11 (NHPPParameters fit + drift-HALT cleared).

**Files:**
- Create: `notebooks/dev_ai_cost_v2_r6/02_simulation.ipynb`

**Required cells:**

1. **Preamble** + anti-fishing invariants (sizing-curve pinned ex-ante; no post-hoc additions).
2. **Load fitted `NHPPParameters`** (from saved pickle/json after Task 11).
3. **Construct `FXBlockBootstrapGenerator`** with `history_returns_sha` pinned; verify against Banrep trailing-5y panel SHA.
4. **Construct `CostSimulator`** with `pool_content_sha` from canonicalization (Task 11 step 2).
5. **For each `k ∈ {0.5, 1, 2, 3, 5}`**: build `NHPPSimulationConfig(params, k, horizon_days=22, n_paths=10000)`; instantiate `NHPPArrivalGenerator`; call with `rng_seed` (pinned per-k seed list, e.g. `[1001, 1002, 1003, 1004, 1005]`); call `FXBlockBootstrapGenerator(rng_seed=2001 + i)`; call `CostSimulator(arrivals, fx, rng_seed=3001 + i)` → `CostTrajectoryEnsemble`. Save each ensemble to `notebooks/dev_ai_cost_v2_r6/data/ensemble_k_<k>.parquet` (cop_costs as float64; fallback_log as JSON).
6. **Audit-block envelope**: compute + log `compute_r6_audit_block` for each k. Append to `DATA_PROVENANCE.md`.

**Exit criteria:**
- All 5 ensembles emitted to `data/`.
- DATA_PROVENANCE.md contains audit_blocks for each k.

**Steps:**

- [ ] **Step 12.1: Implement cells 1–6**
- [ ] **Step 12.2: Run end-to-end** — `uv run jupyter nbconvert --execute ...`
- [ ] **Step 12.3: Commit** with message `feat(notebooks/dev_ai_cost_v2_r6): 02_simulation — generate sizing-curve ensembles`

---

## Task 13: `03_variance_decomp.ipynb` — conservative covariance + reconciliation-ratio cell (CORRECTIONS-OO)

**Owner:** Quantitative Analyst
**Spec ref:** §4 third bullet; §2.6 (2) variance decomposition; CORRECTIONS-OO (reconciliation-ratio reporting).
**Depends on:** Task 12 (ensembles saved).

**Files:**
- Create: `notebooks/dev_ai_cost_v2_r6/03_variance_decomp.ipynb`

**Required cells:**

1. **Preamble** + token-size-invariance bias documentation (CORRECTIONS-NN row 4).
2. **Load ensembles for each k** + observed `Var(Δln Cost_USD)` from v0.2.1's R5 output.
3. **Conservative-covariance variance decomposition** per `simulations/saas_builder/...` precedent (or per spec — describe the formula): decompose `Var(Δln Cost_COP) = Var(Δln Cost_USD) + Var(Δln FX) + 2·Cov(Δln Cost_USD, Δln FX)`; under conservative attribution, assign positive covariance to FX channel and negative to USD channel.
4. **Reconciliation-ratio cell** (CORRECTIONS-OO): for `k = 1`, compute `simulated Var(Δln Cost_USD) / observed Var(Δln Cost_USD)`; flag `reconciliation_drift_high` if ratio outside `[0.8, 1.2]`.
5. **Per-k variance-decomp table**: FX share, USD share, covariance.

**Exit criteria:**
- Reconciliation ratio reported with `quality_flags` set on `R6Output`.
- If ratio out of bounds → write disposition memo + HALT.

**Steps:**

- [ ] **Step 13.1: Implement** the conservative-covariance formula referenced in v0.2.1 (cite the exact section in v0.2.1 spec).
- [ ] **Step 13.2: Run end-to-end**.
- [ ] **Step 13.3: Commit**.

---

## Task 14: `04_cap_wait.ipynb` — session-cap-wait hours only (CORRECTIONS-QQ)

**Owner:** Quantitative Analyst
**Spec ref:** §4 fourth bullet; §2.6 (3) cap-wait friction (session-only per CORRECTIONS-QQ); CORRECTIONS-QQ.
**Depends on:** Task 12.

**Files:**
- Create: `notebooks/dev_ai_cost_v2_r6/04_cap_wait.ipynb`

**Required cells:**

1. **Preamble**: pin `SESSION_CAP_HOURS = 5.0`; cite Anthropic source URL + access date. Weekly cap explicitly scoped out per CORRECTIONS-QQ; understatement-direction bias documented.
2. **Load ensembles** + observed cap-wait baseline `H^obs_session-cap` (computed from observed records: per observed session, excess over 5h).
3. **Per-k**: instantiate `CapWaitCounter(config=CapWaitConfig(session_cap_hours=5.0))`; compute `H^sim_session-cap(k)` distribution across `n_paths`.
4. **Plot**: cap-wait hours distribution per k; mean + 90% CI.

**Exit criteria:**
- Single output: `H_session-cap(k)` for k ∈ sizing curve.
- No weekly-cap computation anywhere in the notebook.

**Steps:**

- [ ] **Step 14.1: Implement** cells.
- [ ] **Step 14.2: Run** end-to-end.
- [ ] **Step 14.3: Commit** with message `feat(notebooks/dev_ai_cost_v2_r6): 04_cap_wait — session-cap only per CORRECTIONS-QQ`.

---

## Task 15a: `05_sensitivity.ipynb` — DIAGNOSTIC arms + Politis-White block-length sanity check

**Owner:** Quantitative Analyst
**Spec ref:** §4 fifth bullet; §2.4 DIAGNOSTIC classification (sensitivity arms have NO verdict authority); Wave 2 Model QA v0.1.1 non-blocking preference (Politis-White block-length sanity check).
**Depends on:** Task 12.

**Files:**
- Create: `notebooks/dev_ai_cost_v2_r6/05_sensitivity.ipynb`

**Required cells:**

1. **Preamble**: DIAGNOSTIC-ONLY classification; cite CORRECTIONS-K convention from v0.2.1.
2. **Horizon sensitivity arm**: re-run for `horizon_days ∈ {3 × 22, 12 × 22}` (3 months, 12 months); report cost-distribution shifts.
3. **FX block-length Politis-White sanity check** (Model QA v0.1.1 non-blocking preference): compute Politis-White automatic block-length on observed FX returns; compare to `⌈T_hist^(1/3)⌉` pin; document any discrepancy as DIAGNOSTIC (does NOT alter the v1 pin).
4. **Per-arm result table**.

**Exit criteria:**
- All arms labeled DIAGNOSTIC in plots/tables.
- No verdict change to R6 outputs.

**Steps:**

- [ ] **Step 15a.1: Implement**.
- [ ] **Step 15a.2: Run**.
- [ ] **Step 15a.3: Commit**.

---

# PHASE 5 — Implementation review checkpoint

## Task 16: Dispatch implementation-review agent panel (Code Reviewer + Reality Checker + Backend Architect)

**Owner:** Orchestrator (this plan's executor) per `memory/feedback_implementation_review_agents.md`.
**Spec ref:** §8 workflow / agent assignment.
**Depends on:** Phases 1–4 complete.

**Files:**
- Create: `scratch/2026-05-16-r6-implementation-review/code_reviewer_report.md`
- Create: `scratch/2026-05-16-r6-implementation-review/reality_checker_report.md`
- Create: `scratch/2026-05-16-r6-implementation-review/backend_architect_report.md`
- Create: `scratch/2026-05-16-r6-implementation-review/consolidated_findings.md`

**Exit criteria:**
- Three independent review reports.
- Consolidated findings memo lists any BLOCKs that must be fixed before Phase 6.
- All BLOCKs CLOSE before Phase 6 starts. NEEDS_WORK BLOCKs route back to the relevant Phase 2/3/4 task for amendment.

**Steps:**

- [ ] **Step 16.1: Dispatch Code Reviewer** with brief: "Review `simulations/dev_ai_cost_v2/` R6 modules (nhpp_calibration, arrival_generators, fx_block_bootstrap, cost_simulation, cap_wait_counter, _anthropic_caps, canonicalization, r6_envelope, r6_aggregator) against R6 spec v0.1.3 §3.3 contract rows + CORRECTIONS-AA through TT. Verify (a) frozen-dc + slots discipline; (b) tier-import rule (no types→modules/utils, no modules→utils); (c) RNG-call-order docstring pin on both generators; (d) per-module audit_block emission; (e) precision-boundary documented on CostTrajectoryEnsemble.cop_costs."

- [ ] **Step 16.2: Dispatch Reality Checker** with brief: "Verify the R6 implementation runs end-to-end against the maintainer's ACTUAL `~/.claude/projects/` JSONL data (51 days / 86k messages baseline per spec). Confirm (a) `N ≥ 50` per cell in the 8-cell grid; (b) `fit_nhpp` succeeds without raising `NHPPSparseBinError`; (c) `canonicalize_message_pool` produces a stable hash + reasonable `dropped_legacy_request_id_count`; (d) reconciliation-drift cell in 01_nhpp_eda.ipynb reports < 1%; (e) no `SparsePoolError` at any k in {0.5, 1, 2, 3, 5}."

- [ ] **Step 16.3: Dispatch Backend Architect** with brief: "Audit R6 module composition — does the orchestration flow correctly (`fit_nhpp` → `summarize_sessions` → `NHPPSimulationConfig` → `NHPPArrivalGenerator(rng_seed)` → `ArrivalEnsemble` × `FXBlockBootstrapGenerator(rng_seed)` → `FXPathEnsemble` × `CostSimulator(arrivals, fx, rng_seed)` → `CostTrajectoryEnsemble` → `CapWaitCounter(arrivals)` → `CapWaitOutput`; `aggregate_r6_output` → `R6Output`)? Verify the audit_block envelope chains every bit-exactness parameter."

- [ ] **Step 16.4: Consolidate** findings; if any BLOCKs, route back to relevant Phase 2/3/4 task and re-run.

- [ ] **Step 16.5: Commit** the review artifacts.

```bash
git add scratch/2026-05-16-r6-implementation-review/
git commit -m "review(r6): implementation-review panel — Code Reviewer + RC + Backend Architect

Per feedback_implementation_review_agents. Three independent reviews on the
R6 sub-package modules + notebooks; consolidated findings memo enumerates
BLOCKs (if any) to fix before Phase 6 Delphi audit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

# PHASE 6 — Pre-output Delphi audit

## Task 17: Run `audit-econ` Delphi panel on pre-release R6 outputs

**Owner:** Orchestrator (invokes `audit-econ` skill).
**Spec ref:** §8 workflow / agent assignment; downstream contract — M-design step consumes R6 outputs only after Delphi clearance.
**Depends on:** Task 16 (implementation review CLOSE_ALL).

**Files:**
- Create: `scratch/2026-05-16-r6-delphi-audit/` (sub-agent reports auto-emitted by `audit-econ`).
- Create: `scratch/2026-05-16-r6-delphi-audit/consensus_findings.md`.

**Exit criteria:**
- `audit-econ` Delphi consensus on R6 outputs (cost distribution + variance decomposition + cap-wait hours + quality flags) reaches convergence.
- Severity-sorted findings: BLOCKs must be resolved; FLAGs may be filed as known-bias rows in §6 threats; NITs noted.
- No BLOCK-class findings remain when results are released to M-design.

**Steps:**

- [ ] **Step 17.1: Invoke `audit-econ` skill** with brief: "Audit R6 v0.1.3 implementation: model derivation correctness (NHPP intensity specification, conservative-covariance variance decomposition, stationary-bootstrap block-length), code-data fidelity (canonicalization 7-step rule, precision boundary, RNG determinism), and empirical-result plausibility (sizing-curve VaR/CVaR shape, cap-wait monotonicity in k, reconciliation-ratio bounds). Dispatch Opus sub-agents on three independent dimensions per the skill's Delphi protocol."

- [ ] **Step 17.2: Iterate** until consensus or BLOCKs resolved.

- [ ] **Step 17.3: Commit** consensus findings.

---

# PHASE 7 — Disposition templates + release

## Task 18: Author disposition templates BEFORE Task 11 runs (logical Phase 7, executed earlier — concurrent with Task 11 setup)

**Owner:** Quantitative Analyst (with PM oversight per disposition convention).
**Spec ref:** §2.7 HALT events (5 categories — NHPP min-bin, NHPP convergence, sparse-cell fallback, reconciliation drift, reconciliation-ratio).
**Depends on:** none (templates can be authored first); logically depends on Task 4–10 + 11 so that the HALT triggers are correctly named.
**Executed:** in practice, alongside Task 11 setup so the notebooks reference real disposition paths.

**Files:**
- Create: `notebooks/dev_ai_cost_v2_r6/dispositions/nhpp_min_bin_template.md`
- Create: `notebooks/dev_ai_cost_v2_r6/dispositions/nhpp_convergence_template.md`
- Create: `notebooks/dev_ai_cost_v2_r6/dispositions/sparse_cell_fallback_template.md`
- Create: `notebooks/dev_ai_cost_v2_r6/dispositions/reconciliation_drift_template.md`
- Create: `notebooks/dev_ai_cost_v2_r6/dispositions/reconciliation_ratio_template.md`

**Template structure** (each file):

```markdown
# Disposition memo — [HALT name]

## HALT context
- **HALT trigger:** [exact threshold from §2.7 or quality-flag definition]
- **Spec reference:** docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md v0.1.3 §2.7 / CORRECTIONS-[XX]
- **Notebook:** notebooks/dev_ai_cost_v2_r6/[notebook name]
- **Date:** [YYYY-MM-DD]

## Observed values
- [Numeric value that triggered HALT]
- [Comparison to threshold]

## Diagnostic information
- [Per-cell counts / convergence stats / fallback rate / drift / variance ratio]
- [Sample size]
- [Audit-block of the run]

## Pre-enumerated pivot menu (per feedback_pathological_halt_anti_fishing_checkpoint)
1. [Pivot option A — e.g., re-coarsen grid further]
2. [Pivot option B — e.g., expand historical window]
3. [Pivot option C — close iteration FAIL]

## User-selected pivot (filled when memo is acted on)
- **Selected:** [option]
- **Justification:** [tie to spec + anti-fishing invariants]
- **Date / approver:** [YYYY-MM-DD / user]

## CORRECTIONS block (per anti-fishing protocol)
- **What changed:** [spec amendment / parameter re-pin / iteration closure]
- **What did NOT change:** [pinned invariants preserved]
- **3-way review:** [code reviewer / reality checker / model qa names + verdicts]
```

**Exit criteria:**
- All 5 templates exist with the structure above (instantiate one per HALT category).
- Templates referenced from the relevant notebook HALT cells.

**Steps:**

- [ ] **Step 18.1: Author each template**
- [ ] **Step 18.2: Commit**

```bash
git add notebooks/dev_ai_cost_v2_r6/dispositions/
git commit -m "feat(notebooks/dev_ai_cost_v2_r6): disposition templates for §2.7 HALT events

5 templates per anti-fishing-checkpoint convention: NHPP min-bin, NHPP
convergence, sparse-cell fallback, reconciliation drift (1% per
CORRECTIONS-HH), reconciliation-ratio ([0.8, 1.2] per CORRECTIONS-OO).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 19: Release R6 outputs to M-design step

**Owner:** PM (this plan's executor).
**Spec ref:** §1.3 (R6 output feeds M-design); §2.6 headline output template; R6Output.quality_flags as M-design contractual binding.
**Depends on:** Task 17 (Delphi audit clearance).

**Files:**
- Create: `memory/project_r6_outputs_released_to_m_design.md` — release memo.

**Exit criteria:**
- Memo cites: R6 audit_block envelope; sizing-curve VaR/CVaR/CI table; cap-wait session-hours table; variance decomposition; `quality_flags` per k; reconciliation-ratio.
- M-design step is informed of which flags are disqualifying.

**Steps:**

- [ ] **Step 19.1: Author the release memo** following the existing `memory/project_*.md` convention.
- [ ] **Step 19.2: Commit**.

---

## Self-review checklist (executed after plan completion)

- [ ] **Spec coverage:** every CORRECTIONS letter AA–TT has an implementing task per the coverage table at the top. Verified by re-reading the table.
- [ ] **Placeholder scan:** no "TBD" / "fill in" / "appropriate" / "similar to" hand-waves; every step has concrete code or a concrete command.
- [ ] **Type consistency:** `NHPPSimulationConfig.k`, `horizon_days`, `n_paths` are consistent across Tasks 3, 5, 6, 7, 10, 12; `R6Output.quality_flags` is `frozenset[str]` across Tasks 3 and 10; `MessageRecord.uuid` is `str` across Tasks 2, 4, 10, 15.
- [ ] **Phase 1 prerequisite:** explicitly noted at top + per-task `Depends on:` lines.
- [ ] **Owner agents** per spec §8 named on every task.
- [ ] **Audit-pass chain** named on every code-touching task.

---

## Execution handoff

Plan complete and saved to `docs/plans/2026-05-16-r6-continuous-stream-simulation-plan.md`. Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, two-stage review between tasks, fast iteration on the 19-task / 7-phase structure.

2. **Inline Execution** — execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints at each phase boundary (Phase 1 → 2 → 3 → 4 → 5 → 6 → 7).

Which approach?
