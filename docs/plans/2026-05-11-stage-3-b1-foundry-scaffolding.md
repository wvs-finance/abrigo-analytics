# STAGE-3 B1 — Foundry scaffolding against forked Panoptic (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `memory/feedback_no_code_in_specs_or_plans.md` (NON-NEGOTIABLE), this plan does NOT contain Python or Solidity code blocks. Each task dispatches a specialized agent who authors code per the functional-python skill (analytics-side) + type-driven-development / evm-tdd skills (Solidity-side, in the cross-repo).
>
> **Foreground orchestrates, never authors.** Per repo memory `memory/feedback_specialized_agents_per_task.md` (NON-NEGOTIABLE).
>
> **Cross-repo plan.** B1 spans two repos: `abrigo-analytics` (this repo) provides the JSON-artifact contract + a stable handoff doc; `thetaSwap-core-dev` (separate repo) houses the Solidity / Foundry implementation. This plan canonicalizes the handoff and the analytics-side guarantees; the Foundry implementation is scoped via the linked plan in `thetaSwap-core-dev` and is dispatched per its OWN review cycle. The Wave-2 RC+MQ review on B1 in THIS repo verifies the handoff contract; the cross-repo plan has its own RC+MQ.

**Plan version:** v0.2 (Wave-1 RC+MQ ACCEPT_WITH_FLAGS — 5 FLAGs + 3 NITs disposed inline per §11.1)
**Master spec:** `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2
**Predecessor:** `simulations/saas_builder/cohort_5_strip/` (commit `3442852`); `IronCondor_strip.json` v1.0 (audit `94150326…`)
**Cross-repo target:** `thetaSwap-core-dev` (Solidity + Foundry harness; out of this plan's commit scope)
**Status:** Wave-1 ACCEPT_WITH_FLAGS-DISPOSED — per-task execution authorized
**Estimated wall-time:** 3–5 days analytics-side; cross-repo Foundry work tracked separately

---

## §0 Goal

**One sentence.** Define the analytics-side contract that the contract-side Foundry test harness consumes (JSON schema, audit-block validation, FX-path generator interface, envelope-assertion formula), and produce a cross-repo handoff document that pins everything `thetaSwap-core-dev` needs to write a `forge test` suite asserting net LP P&L tracks the cohort_5_strip's centered-strip envelope within the Pin-S6 35% tolerance.

## §1 Architecture

B1's analytics-side contribution is a **handoff doc + a deterministic FX-path generator** exposed via a tiny CLI so the contract-side Foundry test harness can shell out to it (or alternatively, the FX paths are pre-computed into a JSON fixture that the Foundry test reads). The analytics side does NOT author Solidity.

The cross-repo handoff doc names the exact `thetaSwap-core-dev` commit sha that B1's Wave-2 review checks against. The expectation is that the contract-side team produces (i) a JSON-loader fixture, (ii) the 12-leg position provisioner, (iii) the 24-bracket envelope assertion, and emits a forge-test verdict that this plan's Wave-2 review consumes.

## §2 Tech stack

**Analytics side (in scope of this commit):**
- Python 3.13, functional-python skill.
- Existing `simulations/saas_builder/cohort_5_strip/` package (READ-ONLY consumption).
- New thin CLI module: `simulations/saas_builder/cohort_5_strip/fx_path_emit.py` (additive).

**Contract side (cross-repo, OUT of this commit's scope):**
- Solidity (Foundry / forge), forked-Panoptic fixture.
- evm-tdd skill (`evm-tdd:phases:01-specify`, `02-implement`, `03-verify`).

---

## §3 Cross-spec references

| Master-spec section | What this plan must satisfy |
|---------------------|-----------------------------|
| §2.3 phase 1 (schema-binding) | JSON loader asserts `schema_version == "v1.0"` and `audit_block` matches |
| §2.3 phase 2 (position provisioning) | Document the leg-to-Panoptic-primitive routing convention |
| §2.3 phase 3 (FX-path simulation) | FX generator implements PRIMITIVES.md §6 eq. (6) over the 24-bracket parameter family (Stage-2 spec §5.2) |
| §2.3 phase 4 (envelope assertion) | Centered-strip / β-fit / peak-normalized form per MQ-FLAG-1 disposition |
| §5 P-B1.1 / P-B1.2 | Pin coverage per Wave-2 review |
| §6.1 Wave-1 review | This plan dispatches RC + MQ before execution |
| §8.1 limitation acknowledgement | Cross-repo coordination is light; analytics side does NOT author Solidity |

---

## §4 File structure

```
docs/plans/2026-05-11-stage-3-b1-foundry-scaffolding.md     ← THIS plan
scratch/2026-05-11-b1-foundry-handoff/
├── HANDOFF.md                  Cross-repo coordination doc (canonical handoff contract)
├── FX_PATH_GENERATOR.md        Math + CLI usage doc for the generator
└── ENVELOPE_ASSERTION_PROOF.md MQ-FLAG-1 disposition trace — the canonical formula + numerical example

simulations/saas_builder/cohort_5_strip/
└── fx_path_emit.py             NEW Callable tier: 24-bracket FX-path JSON emitter

simulations/saas_builder/data/
└── fx_paths_24_brackets.json   NEW fixture: pre-computed FX paths per bracket × time grid
```

The `thetaSwap-core-dev` files (`test/integration/StripReplication.t.sol`, etc.) are tracked OUT-OF-REPO; their sha is recorded in HANDOFF.md and verified at B1's Wave-2 review.

---

## §5 Phase 1 — Handoff contract authoring

### Task 1.1 — Draft the cross-repo handoff document

**Files:**
- Create: `scratch/2026-05-11-b1-foundry-handoff/HANDOFF.md`

**Agent dispatch:** `general-purpose` agent (orchestration / coordination authoring; no code).

**Acceptance:**
- §1 Consumed analytics artifacts: full path to `simulations/saas_builder/data/IronCondor_strip.json` + the current audit_block (`94150326…`); pinned commit sha (`3442852`).
- §2 Required Foundry behavior: enumerated as a numbered list — JSON-load + schema_version check, audit_block re-hash, position-provision against forked Panoptic, run all 24 FX-bracket scenarios, assert envelope per Phase-4 formula.
- §3 Envelope assertion formula: the EXACT centered-strip / β-fit / peak-normalized form from master-spec §2.3 phase 4 + `simulations/saas_builder/cohort_5_strip/replication.py:1-28`. NOT the v0.1-spec relative-error form (which had denominator collapse — MQ-FLAG-1).
- §4 FX-path generator: pointer to `fx_path_emit.py` CLI (authored in Task 2.1) + `fx_paths_24_brackets.json` fixture path.
- §5 Cross-repo sha pinning: a `thetaSwap_core_dev_commit_sha` field reserved (populated at B1 Wave-2 review time after the contract-side team merges).
- §6 Out-of-scope clarifier: Streamia premium plumbing (B2 in the master spec deferred list) is NOT part of B1; B1 tests replication mechanics only.
- §7 Anti-pattern callouts: the Foundry test must NOT (i) re-derive the 35% tolerance from PRIMITIVES.md §12 row 1's 5%, (ii) silently relax the tolerance, (iii) reduce the 24-bracket family to a subset without master-spec amendment.

**Commit message:** `handoff(stage-3-b1): cross-repo coordination doc + envelope-assertion formula pin`

---

### Task 1.2 — Author the envelope-assertion proof trace

**Files:**
- Create: `scratch/2026-05-11-b1-foundry-handoff/ENVELOPE_ASSERTION_PROOF.md`

**Agent dispatch:** `general-purpose` (mathematical writeup; no code).

**Acceptance:**
- Walks through the centered-strip / β-fit / peak-normalized form step by step using the canonical TP1 fixture; produces the same `max_relative_error ≈ 0.28` number that `CarrMadanEnvelopeVerifier` reports on the current emitted strip (the run output recorded in `simulations/saas_builder/cohort_5_strip/IronCondor_strip.STRIKES.md` is the reference).
- Includes a §"Why not |Π−K̂σ|/|K̂σ|" section explaining the denominator-collapse failure mode (MQ-FLAG-1 historical record); references the spec v0.1 → v0.2 CORRECTIONS-α v9.1 entry.
- Includes a §"σ_T computation contract" (MQ-FLAG-B1.1 disposition) that pins:
  - **The Foundry test computes σ_T from PRIMITIVES.md §6 eq. (7) DISCRETELY on the emitted FX samples**, NOT from the Stage-2 closed-form path integral $(\overline{X/Y})^2 \varepsilon^2 [1/8 + \sin(4\omega t)/(32\omega t)]$ (STAGE_2_RESULTS.md §2.2). Rationale: the Foundry test ingests the JSON-emitted FX samples; computing σ_T from the same samples (rather than the closed form) keeps the Foundry-side computation black-box-equivalent to the analytics-side pre-compute. Drift between discrete and closed-form is caught at the envelope-assertion stage if material.
  - **Time-grid n_points pinned at 5000** (MQ-FLAG-B1.2 disposition; mirrors cohort_4's `n_t_grid = 5000` convention from `simulations/saas_builder/cohort_4/pi_derivation.py` which satisfies Nyquist for the $\sin(4\omega t)$ kernel at $\omega = 1$). The JSON `time_grid.n_points` field MUST be exactly 5000 at emit time. Foundry test uses the FX samples as-is, NOT a different grid.

**Commit message:** `proof(stage-3-b1): canonical envelope-assertion formula + numerical example`

---

## §6 Phase 2 — FX-path generator (analytics side)

### Task 2.1 — Author the FX-path emitter

**Files:**
- Create: `simulations/saas_builder/cohort_5_strip/fx_path_emit.py`
- Create: `simulations/tests/test_saas_cohort5_fx_path_emit.py`
- Create: `scratch/2026-05-11-b1-foundry-handoff/FX_PATH_GENERATOR.md` (usage doc)

**Agent dispatch:** `Senior Developer` (frozen-dc Callable tier authoring per functional-python skill).

**Acceptance:**
- `FXPathEmitter` frozen-dc with `__call__(brackets: tuple[ParameterBracket, ...], time_grid: TimeGrid) -> Mapping[BracketId, FloatArray]`.
- **All Value types authored in this task (RC-FLAG-2 disposition).** v0.1 referenced `TimeGrid` and `BracketId` without defining them; v0.2 pins:
  - `ParameterBracket` frozen-dc: `(tier: TierID, alpha_arm: Literal[0, 1], cache_regime: Literal["low", "high"], kappa_arm: Literal[0, 1], epsilon: float, omega: float, xy_bar: float)`. Lives in `simulations/saas_builder/cohort_5_strip/fx_path_emit.py` (NEW Value type, NOT re-import from cohort_2 — see RC-FLAG-1 below).
  - `TimeGrid` frozen-dc: `(t_start_months: float, t_end_months: float, n_points: int)` with `__post_init__` validating `t_end > t_start > 0` and `n_points >= 2`.
  - `BracketId` TypeAlias for `str` (the canonical `"<tier>_<alpha_arm>_<cache_regime>_<kappa_arm>"` string).
- **cohort_2 type relationship (RC-FLAG-1 disposition).** v0.1 said "MUST re-import from `simulations.saas_builder.cohort_2.types` if it exists." Investigation: `cohort_2.types` exports `BracketPoint`/`BracketGrid` with a DIFFERENT shape `(T2CostParams, FXPathParams, horizon_T)`. v0.2 resolves: cohort_5_strip authors a NEW `ParameterBracket` type tailored to the FX-path emit; the (tier, α-arm, cache, κ-arm) factorization constants are imported as named constants from `simulations.saas_builder.cohort_2` (e.g., `TIER_IDS`, `ALPHA_ARMS`, `CACHE_REGIMES`, `KAPPA_ARMS` if they exist there; if not, declared as module-level constants in `fx_path_emit.py` with citation back to Stage-2 spec v1.2.1 §5.2 lines 383–388 verbatim).
- The FX-path generator implements PRIMITIVES.md §5 eq. (6) verbatim (MQ-NIT correction: eq. (6) lives in §5 "Deterministic FX path generator", NOT §6): $(X/Y)_t(\varepsilon, \omega) = (1 + \varepsilon\,(\cos^2(\omega t) - 1/2))\,\overline{X/Y}$.
- One Hypothesis property test: for any valid `(ε, ω, t)` triple with `0 < ε < 1` (PRIMITIVES.md §5 constraint), the emitted FX value lies in `[(1 - ε/2), (1 + ε/2)] · X̄/Ȳ` (eq. 6 amplitude bound).
- One regression test: emit at the canonical TP1 bracket and compare against a hard-coded fixture array (pin-fixture pattern — locks the FX-path values bit-reproducibly).
- A `simulations/saas_builder/cohort_5_strip/__init__.py` re-export of `FXPathEmitter` + `ParameterBracket`.

**Commit message:** `feat(cohort_5_strip): 24-bracket FX-path emitter for B1 Foundry handoff`

---

### Task 2.2 — Pre-compute and emit fx_paths_24_brackets.json

**Files:**
- Create: `simulations/saas_builder/data/fx_paths_24_brackets.json` (gitignored; reproducible-from-source)
- Create: a one-shot script entry-point on the `FXPathEmitter` IO Boundary (Task 2.1 frozen-dc is Callable; the IO Boundary wrapper that writes JSON lives in a new `fx_path_io.py` file).
- Modify: `simulations/saas_builder/cohort_5_strip/__init__.py` to export the IO Boundary class.

**Agent dispatch:** `Senior Developer`.

**Acceptance:**
- `FXPathJSONEmitter` IO Boundary class with `__init__(emit_dir, ...)` + `__call__()` that runs `FXPathEmitter` over the 24 brackets and emits a deterministic JSON fixture.
- JSON schema:
  ```
  {
    "schema_version": "v1.0",
    "primitives_anchor": "PRIMITIVES.md §5 eq. (6) (FX-path generator); §6 eq. (7) (realized variance)",
    "n_brackets": 24,
    "time_grid": {"t_start_months": <float>, "t_end_months": <float>, "n_points": 5000},
    "brackets": [
      {"bracket_id": "<str>", "tier": "<str>", "alpha_arm": <int>, "cache_regime": "<str>", "kappa_arm": <int>,
       "epsilon": <float>, "omega": <float>, "x_over_y_bar": 4000.0,
       "fx_path": [<float>, <float>, ...]}, ...
    ],
    "audit_block": "<sha256>",
    "strip_audit_block_parent": "<sha256 of the IronCondor_strip.json this fixture is paired with>"
  }
  ```
  (MQ-NIT disposition: `strip_audit_block_parent` field added for cross-fixture drift defense. If A2 re-emits the strip, the FX-paths file's parent_audit_block field will visibly point to the OLD strip — the Foundry test loads both and asserts they match before running.)
- `audit_block` hashes the serialized payload sans the audit_block field (mirrors cohort_5_strip's `_compute_strip_audit_block` convention).
- Round-trip read-back equality enforced.
- 24 brackets emitted; one Hypothesis property test confirms `len(brackets) == 24` and the (tier × α × cache × κ) factorization is `3 × 2 × 2 × 2`.

**Commit message:** `data(cohort_5_strip): fx_paths_24_brackets.json fixture for B1 Foundry handoff`

---

## §7 Phase 3 — Cross-repo dispatch + handoff sha pin

### Task 3.1 — Open the cross-repo plan in `thetaSwap-core-dev`

**Files (cross-repo, OUT of this commit's scope):**
- `thetaSwap-core-dev/docs/plans/2026-05-{NN}-stage-3-b1-strip-replication-foundry.md`

**Agent dispatch:** N/A — this is a coordination step. The plan in `thetaSwap-core-dev` is authored via its own brainstorming → writing-plans cycle under the evm-tdd skill chain (`evm-tdd:evm-tdd` → `evm-tdd:phases:01-specify`). The HANDOFF.md from Task 1.1 is the canonical input.

**Acceptance:**
- The cross-repo plan exists and cites HANDOFF.md's commit sha as its master spec.
- The cross-repo plan's first phase reads `IronCondor_strip.json` + `fx_paths_24_brackets.json` and asserts audit_block matches.
- The cross-repo plan's exit deliverables match master-spec §2.3 exit-deliverables list: forge test 24/24 PASS at 35% envelope tolerance.

This task is a coordination handoff; this repo's Wave-2 review verifies via `HANDOFF.md::thetaSwap_core_dev_commit_sha` that the cross-repo plan was authored.

**Commit message:** N/A — this is a cross-repo action; HANDOFF.md is updated with the cross-repo plan sha when known.

---

### Task 3.2 — Wait for cross-repo Wave-2 verdict; record outcome

**Files:**
- Modify: `scratch/2026-05-11-b1-foundry-handoff/HANDOFF.md` (append §"Cross-repo Wave-2 verdict")

**Agent dispatch:** N/A — orchestrator records the cross-repo verdict (PASS / FAIL).

**Acceptance:**
- HANDOFF.md §"Cross-repo Wave-2 verdict" lists: cross-repo commit sha, forge test outcome (24/24 PASS or N/24 FAIL), envelope max-rel-error per bracket if FAIL.
- If FAIL on ≥ 1 bracket, route per master-spec §2.3 to A1 (geometry / strategy fix). MQ-FLAG-B1.3 disposition aligns with master-spec exit of 24/24 strict.
- If PASS, B1 closes; both Wave-2 RC+MQ on THIS plan dispatch.

**Wait-timeout escape valve (RC-FLAG-3 disposition).** Task 3.2 explicit wait-cap: **30 calendar days** after Task 1.1's HANDOFF.md commit lands. If no cross-repo merge has occurred within 30 days, the orchestrator emits `scratch/2026-05-11-b1-foundry-handoff/STALLED.md` documenting the wait condition, marks B1 as STALLED in the master-spec milestone status, and surfaces to the user for one of: (a) extend the wait, (b) close B1 as DEFERRED and re-open after A1 completes, (c) escalate the cross-repo dependency. NO indefinite wait.

**Commit message:** `coord(stage-3-b1): record cross-repo Wave-2 verdict in HANDOFF.md`

---

## §8 Pin coverage (per master spec §5)

| Pin | This plan's coverage |
|-----|-----------------------|
| P-B1.1 (JSON schema + audit_block validation in Foundry) | Task 1.1 HANDOFF.md §2 enumerates the Foundry-side schema check requirements; Task 3.2 records the cross-repo verdict. |
| P-B1.2 (envelope assertion at 35% on the canonical metric) | Task 1.2 ENVELOPE_ASSERTION_PROOF.md pins the canonical metric form; cross-repo Foundry test must cite this proof; Task 3.2 records the per-bracket envelope verdicts. |

## §9 HALT routing

| Trigger | Route |
|---------|-------|
| Task 1.1 HANDOFF.md cites a non-canonical envelope formula (e.g., the v0.1-spec relative-error form) | HALT — RC Wave-1 catches this. |
| Task 2.1 FX-path generator fails its Hypothesis property test | HALT — Senior Developer iterates; do NOT relax. |
| Task 2.2 fx_paths_24_brackets.json round-trip fails or bracket count ≠ 24 | HALT — generator drift; route to cohort_2 spec §5.2 reconciliation. |
| Task 3.2 cross-repo forge test FAILS on ≥ 1 bracket at 35% tolerance | HALT — route to A1 (strategy / geometry fix, not a B1-level fix). MQ-FLAG-B1.3 disposition: master-spec §2.3 exit is 24/24 PASS strict, so ANY single-bracket FAIL is a HALT, not the "≥ 2/24" looser v0.1 condition. |
| Cross-repo Foundry deployment can NOT provision any leg of the 12-leg strip on forked Panoptic | HALT — route to A1 (Panoptic strategy is unsupported; strategy swap required). |
| Wave-1 or Wave-2 RC+MQ on this plan returns BLOCK | HALT per master-spec §6.1; CORRECTIONS-α landed in this plan's §11. |

## §10 Artifacts emitted

| Artifact | Phase | Schema | Lineage parent |
|----------|-------|--------|-----------------|
| `scratch/2026-05-11-b1-foundry-handoff/HANDOFF.md` | 1/3 | markdown + commit-sha pin fields | `IronCondor_strip.audit_block` |
| `scratch/2026-05-11-b1-foundry-handoff/ENVELOPE_ASSERTION_PROOF.md` | 1 | markdown | `cohort_5_strip/replication.py` lines |
| `scratch/2026-05-11-b1-foundry-handoff/FX_PATH_GENERATOR.md` | 2 | markdown | `fx_path_emit.py` |
| `simulations/saas_builder/cohort_5_strip/fx_path_emit.py` | 2 | code (Callable tier) | (additive, no parent) |
| `simulations/saas_builder/cohort_5_strip/fx_path_io.py` | 2 | code (IO Boundary tier) | (additive) |
| `simulations/saas_builder/data/fx_paths_24_brackets.json` | 2 | v1.0 (new) | sha over emitter inputs |
| Cross-repo: `thetaSwap-core-dev/test/integration/StripReplication.t.sol` | 3 (cross-repo) | Solidity / Foundry | HANDOFF.md sha |

## §11 CORRECTIONS-α (patch log)

### §11.1 v0.1 → v0.2 (Wave-1 RC+MQ disposition)

**Wave-1 review verdict:** RC ACCEPT_WITH_FLAGS + MQ ACCEPT_WITH_FLAGS (2026-05-11). 0 BLOCKs. Verdict files:
- `scratch/2026-05-11-stage-3-b1-rc-mq-review/rc-verdict.md`
- `scratch/2026-05-11-stage-3-b1-rc-mq-review/mq-verdict.md`

**Convergent finding (both reviewers).** RC-FLAG-1 + RC-FLAG-2 + MQ-FLAG-B1.2 converge on under-specified types/contracts in §6 Task 2.1/2.2. v0.2 pins all Value types (`ParameterBracket`, `TimeGrid`, `BracketId`) inline + pins `time_grid.n_points = 5000`.

| Finding | Severity | Disposition | Location |
|---------|----------|-------------|----------|
| RC-FLAG-1 | Material | `ParameterBracket` is a NEW Value type in cohort_5_strip (NOT a re-import from cohort_2 — cohort_2 has `BracketPoint`/`BracketGrid` with a different shape). Factorization constants (`TIER_IDS`, `ALPHA_ARMS`, etc.) imported from cohort_2 if available; otherwise declared as module-level constants citing Stage-2 spec v1.2.1 §5.2 lines 383–388. | §6 Task 2.1 |
| RC-FLAG-2 | Material | All three undefined types (`TimeGrid`, `BracketId`, `ParameterBracket`) pinned with full Value-tier specs. `TimeGrid` validates `t_end > t_start > 0`, `n_points >= 2`. `BracketId` is a `TypeAlias` for the canonical `"<tier>_<alpha>_<cache>_<kappa>"` string. | §6 Task 2.1 |
| RC-FLAG-3 | Minor | Task 3.2 wait-timeout escape valve added: 30 calendar days; on stall, emit `STALLED.md` and surface to user for extend/defer/escalate. NO indefinite wait. | §7 Task 3.2 |
| MQ-FLAG-B1.1 | Material | §"σ_T computation contract" in HANDOFF.md (Task 1.2) pinned: Foundry computes σ_T from PRIMITIVES.md §6 eq. (7) DISCRETELY on emitted FX samples, NOT from the Stage-2 closed-form path integral. | Task 1.2 acceptance |
| MQ-FLAG-B1.2 | Material | `time_grid.n_points = 5000` pinned (mirrors cohort_4 `n_t_grid = 5000` Nyquist-compliant convention for $\sin(4\omega t)$ kernel at $\omega = 1$). JSON schema field constrained to exactly 5000 at emit time. | §6 Task 2.2 JSON schema |
| MQ-FLAG-B1.3 | Material | HALT trigger tightened from "≥ 2/24 FAIL" to "≥ 1/24 FAIL" — aligns with master-spec §2.3 exit of 24/24 strict. Any single-bracket FAIL routes to A1. | §9 HALT routing + Task 3.2 |
| PRIMITIVES.md §-cite off-by-one (MQ-NIT) | Cosmetic | All FX-path references corrected from "§6 eq. (6)" to "§5 eq. (6)" (eq. (6) is in §5 "Deterministic FX path generator"). Realized-variance references stay "§6 eq. (7)" (correct). | §6 Task 2.1 + JSON `primitives_anchor` field + §12 references |
| `strip_audit_block_parent` field (MQ-NIT) | Cosmetic | Added to `fx_paths_24_brackets.json` schema for cross-fixture drift defense — if A2 re-emits the strip, the FX-paths file points to the OLD strip via this field, and the Foundry test asserts match before run. | §6 Task 2.2 JSON schema |

### §11.2 Wave-2 (post-execution) review reserve

Wave-2 RC+MQ on this plan's exit deliverables lands its own block at §11.3.

## §12 References

- `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2 — master spec (§2.3 for this plan; §9.1 MQ-FLAG-1 disposition rationale; §8.1 cross-repo coordination acknowledgement).
- `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` §5.2 — 24-bracket parameter family (input to Task 2.x).
- `notes/PRIMITIVES.md` §5 eq. (6) — FX-path generator (Phase 2 mathematical anchor); §6 eq. (7) — realized variance (Foundry-side anchor); §11 — discrete strip; §12 — tolerance ledger.
- `simulations/saas_builder/cohort_5_strip/replication.py:1-28` — canonical envelope-verifier docstring; the formula the Foundry test must implement.
- `simulations/saas_builder/cohort_5_strip/types.py:57-74` — `REPLICATION_REL_TOL = 0.35` rationale.
- `simulations/saas_builder/cohort_5_strip/__init__.py` — Pin S1–S8 framing that B1 verifies in-the-large.
- `memory/feedback_no_code_in_specs_or_plans.md` — plan-as-orchestration-only.
- `memory/feedback_specialized_agents_per_task.md` — foreground-orchestrates-never-authors.
- `evm-tdd:evm-tdd` skill — cross-repo Solidity / Foundry methodology anchor (consumed by `thetaSwap-core-dev`, NOT by this plan).

---

*End of B1 plan v0.1. Wave-1 RC+MQ review dispatch before any task execution.*
