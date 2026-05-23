# STAGE-3 A1 — Panoptic strategy re-survey (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `memory/feedback_no_code_in_specs_or_plans.md` (NON-NEGOTIABLE), this plan does NOT contain Python or Solidity code blocks. Each task dispatches a specialized agent who authors code per the functional-python skill + the Honnibal audit-pass chain.
>
> **Foreground orchestrates, never authors.** Per repo memory `memory/feedback_specialized_agents_per_task.md` (NON-NEGOTIABLE).

**Plan version:** v0.4 (in-execution CORRECTIONS-α — gate-2.4 tolerance precision-floor fix per §11.3)
**Master spec:** `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2
**Predecessor:** `simulations/saas_builder/cohort_5_strip/` (commit `3442852`); Stage-2 verdict memo (`docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`)
**Status:** Wave-1 ACCEPT_WITH_FLAGS-DISPOSED — per-task execution authorized
**Estimated wall-time:** 1–2 days of focused work

---

## §0 Goal

**One sentence.** Survey the current Panoptic primitive set, evaluate alternative strategies against the same `CarrMadanEnvelopeVerifier` metric at the canonical TP1 fixture, and produce a KEEP_IRONCONDOR / REPLACE_WITH_X verdict against the pre-pinned 5pp REPLACE margin (master spec Pin P-A1.4).

## §1 Architecture

A1 is a **research + light-code** track. Output is a comparison table, a per-candidate envelope evaluation, and a verdict JSON. No PyMC re-fit; no cohort_5_strip schema change unless the verdict is REPLACE.

The light-code component is a generalized strip-emit harness under `simulations/saas_builder/cohort_5_strip/strategies/` that lets the existing `CarrMadanEnvelopeVerifier` consume non-reverse-IC primitives via a Protocol-typed adapter (see Phase 2). This adapter is the structural prerequisite for Pin P-A1.MQ-FLAG-3 comparability.

## §2 Tech stack

- Python 3.13, functional-python skill (frozen-dc / free fns / IO Boundary).
- Existing `simulations/saas_builder/cohort_5_strip/` package; READ-ONLY consumption + ADDITIVE extension via a new sub-package.
- Markdown for research artifacts; JSON for the verdict.
- Web research via WebFetch / WebSearch on Panoptic docs (current as of 2026-05-11).

---

## §3 Cross-spec references

| Master-spec section | What this plan must satisfy |
|---------------------|-----------------------------|
| §2.1 phase 1 | Discovery (the comparison table) |
| §2.1 phase 2 + MQ-FLAG-3 caveat | Evaluation with cross-primitive comparability demonstrated |
| §2.1 phase 3 | KEEP/REPLACE verdict + citation back to comparison-table row |
| §2.1 HALT-triggers | No-emit primitive → HALT; 5pp threshold pin (P-A1.4) |
| §5 P-A1.1 / P-A1.2 / P-A1.3 / P-A1.4 | Pin coverage per Wave-2 review |
| §6.1 Wave-1 review | This plan dispatches RC + MQ before execution |

---

## §4 File structure

```
docs/plans/2026-05-11-stage-3-a1-panoptic-restrategy.md     ← THIS plan
scratch/2026-05-11-a1-panoptic-survey/
├── STRATEGY_COMPARISON.md           Phase 1 research artifact
├── envelope_evaluation_log.md       Phase 2 raw run log
└── verdict_rationale.md             Phase 3 reasoning trace

simulations/saas_builder/cohort_5_strip/strategies/   ← NEW sub-package
├── __init__.py
├── _errors.py
├── types.py                  Protocol: StrategyAdapter (lifts a non-IC primitive into the strip API)
├── adapters.py               Per-primitive concrete adapters (long_strangle, butterfly, custom)
└── compare.py                EnvelopeComparator: runs N adapters through the verifier and ranks

simulations/saas_builder/data/
└── strategy_verdict.json     Phase 3 emit (NEW schema v1.0)

simulations/tests/
└── test_saas_cohort5_strategies.py   Test coverage for the adapters
```

If verdict is REPLACE, a **follow-up** spec lands at `docs/specs/2026-05-{NN}-cohort-5-strip-delta-spec.md` (out of A1 scope; A1 only emits the JSON verdict).

---

## §5 Phase 1 — Discovery

### Task 1.1 — Research current Panoptic primitive set

**Files:**
- Create: `scratch/2026-05-11-a1-panoptic-survey/STRATEGY_COMPARISON.md`

**Agent dispatch:** `general-purpose` agent with a research brief: read Panoptic's current public documentation (panoptic.xyz docs, GitHub README, recent blog posts) via WebFetch and produce a comparison table of available primitives. (RC-FLAG-1 disposition: `general-purpose` is the right specialist for web-research + markdown-authoring tasks where no domain-specific agent fits; per `memory/feedback_specialized_agents_per_task.md`'s spirit, the "specialist per task" rule maps RESEARCH+MARKDOWN tasks to `general-purpose` because no Panoptic-domain specialist exists in the agent catalog.)

**Acceptance:**
- Table has one row per primitive offered (e.g., long-strangle, short-strangle, long-straddle, butterfly, custom-leg combos, Streamia overlays).
- Columns: `primitive_id` · `leg_count` · `payoff_shape` (analytic, e.g., piecewise-linear), `convexity_class` (long-vol / short-vol / mixed) · `on-chain liquidity status` (live / limited / inactive) · `admits_strip_emit?` (yes/no, with rationale).
- Each row carries an inline citation to the documentation source URL + access timestamp.
- Bottom-of-table summary lists which primitives CANNOT admit a deterministic strike-ladder + weight emit (these are HALT candidates per master spec §2.1 HALT-trigger #1).
- Word budget: 800–1500 words total.

**Anti-fishing constraint.** The agent is briefed NOT to pre-rank primitives; the comparison table is a factual catalogue, not a preference ordering. Ranking happens in Phase 3 after Phase 2's numerical evaluation.

**Commit message:** `research(stage-3-a1): Panoptic primitive comparison table`

---

### Task 1.2 — Filter candidates by deterministic-emit admissibility

**Files:**
- Modify: `scratch/2026-05-11-a1-panoptic-survey/STRATEGY_COMPARISON.md` (add §"Filtered candidate set" section)

**Agent dispatch:** same `general-purpose` agent (continuation of Task 1.1 context).

**Acceptance:**
- Top-of-section list of 2–4 primitives that admit deterministic emit and are candidates for Phase 2 evaluation. Each carries a one-line rationale.
- Existing reverse-IC (the cohort_5_strip baseline) appears in the list as the comparison baseline.
- If fewer than 2 candidates remain (impossibility of cross-comparison), HALT per master spec §2.1 HALT-trigger #1; emit disposition memo `scratch/2026-05-11-a1-panoptic-survey/HALT_NO_CANDIDATES.md`.

**Commit message:** `research(stage-3-a1): filter Panoptic candidates to deterministic-emit set`

---

## §6 Phase 2 — Evaluation

### Task 2.1 — Specify the StrategyAdapter Protocol

**Files:**
- Create: `simulations/saas_builder/cohort_5_strip/strategies/_errors.py`
- Create: `simulations/saas_builder/cohort_5_strip/strategies/types.py`

**Agent dispatch:** `Senior Developer` (per `memory/feedback_specialized_agents_per_task.md` — types-tier work is Senior Developer scope), brief covers:
- Read `simulations/saas_builder/cohort_5_strip/types.py` (IronCondor / IronCondorStrip / ReplicationVerdict) and `simulations/saas_builder/cohort_5_strip/replication.py` (CarrMadanEnvelopeVerifier).
- Author a `StrategyAdapter` Protocol with a single method `build_strip(s_0, sigma_0, k_star) -> IronCondorStrip-equivalent` that any candidate primitive implements.
- Author a `NormalizedEnvelopeScore` frozen-dc that wraps `ReplicationVerdict` with the additional fields `(primitive_id, comparability_proof: Literal["tiled_body", "primitive_variant", "normalized_score"], normalized_score: float)` per master-spec §2.1 phase 2 MQ-FLAG-3 disposition.
- **Normalized score formula (MQ-FLAG-A1.2 disposition).** The `normalized_score` field is defined as `max_relative_error * (1.0 + abs(Π_strip(S_0)) / max(abs(Π_strip(S))))` over the verifier grid — a multiplicative correction that absorbs the non-tiled-body floor offset for non-reverse-IC primitives. Pin: this formula MUST be a frozen module-level constant; ex-post adjustment requires CORRECTIONS-α + a fresh Wave-1 review. Provides primitive-independent comparability when `comparability_proof = "normalized_score"`.
- Author `StrategyAdapterError`, `ComparabilityProofMissingError`, and `ComparabilityProofFalsifiedError` exceptions (per MQ-FLAG-A1.5: catch both ABSENT and FALSE proofs).
- Three-tier discipline (functional-python skill): frozen-dc only at Value tier; Protocol allowed.

**Acceptance:**
- Files exist, type-check clean (`uv run ty`), ruff clean.
- No `IronCondorStrip` subclassing — the Protocol returns the existing frozen-dc type or a typed dispatch.
- `__post_init__` on `NormalizedEnvelopeScore` rejects unknown `comparability_proof` values.

**Commit message:** `feat(cohort_5_strip/strategies): StrategyAdapter Protocol + types`

---

### Task 2.2 — Implement adapters for filtered candidates

**Files:**
- Create: `simulations/saas_builder/cohort_5_strip/strategies/adapters.py`
- Create: `simulations/tests/test_saas_cohort5_strategies.py` (initial test file with one parametrized fixture per adapter)

**Agent dispatch:** `Senior Developer` per Task 2.1 brief.

**Acceptance:**
- One adapter implemented per Phase-1 filtered candidate.
- Each adapter is a frozen-dc with `__call__` returning an `IronCondorStrip`-typed object whose legs match the candidate primitive's natural 4-strike geometry.
- For non-reverse-IC candidates, the adapter MUST surface the `comparability_proof` choice (one of: tiled_body / primitive_variant / normalized_score) as a constructor argument.
- Existing reverse-IC adapter included as the baseline (re-exports the existing `cohort_5_strip.build_strip` behavior).
- One Hypothesis property test per adapter: built strip satisfies `IronCondorStrip.__post_init__` invariants for any valid `(s_0, sigma_0, k_star)` triple.

**Commit message:** `feat(cohort_5_strip/strategies): adapters for filtered Panoptic candidates`

---

### Task 2.3 — Implement the EnvelopeComparator

**Files:**
- Create: `simulations/saas_builder/cohort_5_strip/strategies/compare.py`
- Modify: `simulations/saas_builder/cohort_5_strip/strategies/__init__.py` (public exports)

**Agent dispatch:** `Senior Developer`.

**Acceptance:**
- `EnvelopeComparator` frozen-dc with `__call__(adapters: tuple[StrategyAdapter, ...], fixture: TestPoint) -> tuple[NormalizedEnvelopeScore, ...]`.
- Runs the SHIPPED `CarrMadanEnvelopeVerifier` against each adapter's built strip.
- Returns scores sorted by `max_relative_error` ASCENDING (best replication first). On floating-point tie (`max_relative_error` equal within 1e-12), secondary sort by `primitive_id` lexicographically (MQ-NIT-A1.2 stability pin).
- Raises `ComparabilityProofMissingError` if any adapter is missing its `comparability_proof` field.
- **Comparability-proof verification (MQ-FLAG-A1.5).** For each adapter claiming `comparability_proof = "tiled_body"`, the comparator MUST runtime-verify by calling `cohort_5_strip.assert_long_vol_signature(strip)` on the built strip; if it fails, raise `ComparabilityProofFalsifiedError`. For `comparability_proof = "primitive_variant"`, the comparator MUST receive the primitive-specific verifier as a constructor argument (a `PrimitiveVariantVerifier` Protocol authored in Task 2.1); if absent, raise `ComparabilityProofMissingError`. For `comparability_proof = "normalized_score"`, the comparator uses `normalized_score` instead of raw `max_relative_error` for ranking.

**Commit message:** `feat(cohort_5_strip/strategies): EnvelopeComparator with comparability-proof gate`

---

### Task 2.3b — Author primitive-variant verifiers if needed (MQ-FLAG-A1.1 disposition)

**Files:**
- Conditionally create: `simulations/saas_builder/cohort_5_strip/strategies/variant_verifiers.py`
- Conditionally extend: `simulations/tests/test_saas_cohort5_strategies.py`

**Agent dispatch:** `Senior Developer` (conditional — runs only if at least one Phase-1 filtered candidate uses `comparability_proof = "primitive_variant"`).

**Acceptance:**
- For each `primitive_variant` candidate, author a verifier function that mirrors `CarrMadanEnvelopeVerifier`'s contract (returns a `ReplicationVerdict`) but uses primitive-specific centering / proxy / β-fit. Each variant verifier MUST pass an equivalence test against `CarrMadanEnvelopeVerifier` when applied to a reverse-IC strip (numerical equivalence within 1e-12).
- If no Phase-1 candidate uses `primitive_variant`, this task is SKIPPED with explicit rationale recorded in `scratch/2026-05-11-a1-panoptic-survey/STRATEGY_COMPARISON.md` §"Comparability proof routing".
- This task is the explicit authoring step that v0.1 omitted (MQ-FLAG-A1.1: `primitive_variant` lane was referenced but never authored).

**Commit message:** `feat(cohort_5_strip/strategies): primitive-variant verifiers for non-reverse-IC adapters`

---

### Task 2.4 — Run the comparator on filtered candidates at TP1

**Files:**
- Create: `scratch/2026-05-11-a1-panoptic-survey/envelope_evaluation_log.md`

**Agent dispatch:** `Senior Developer` + `Reality Checker` agent for an inline numerical cross-check (NOT a Wave-2 review — Wave-2 RC+MQ on A1's exit deliverables happens AFTER all phases complete; this RC dispatch is a per-task accuracy gate per RC-FLAG-2 disposition, scoped to verify the reproducibility tolerance only).

**Acceptance:**
- The eval log lists, for each filtered candidate, the `NormalizedEnvelopeScore` tuple including `(primitive_id, max_relative_error, normalized_score, tolerance=0.35, comparability_proof, raw_verdict_passes)`.
- **Reverse-IC numerical baseline pin (MQ-NIT-A1.1; relaxed v0.3 → v0.4 per §11.3):** reverse-IC at TP1 reports `max_relative_error ≈ 0.2813` (matching `simulations/saas_builder/data/IronCondor_strip.STRIKES.md` line 25 = `2.8134e-01`). Eval log entry for reverse-IC MUST match this value within `5e-5` (matches the published baseline's 5-sig-fig emission precision floor; the prior `1e-6` tolerance was tighter than the published baseline's precision and produced a false-FAIL on the bit-exact-correct value `0.2813412838694053`). Drift > 5e-5 indicates upstream cohort_5_strip change.
- TP1 fixture used: `(S_0=4000.0, sigma_0=20000.0, k_star=4687.94)` per master-spec §2.1 phase 2 line.
- **Reproducibility tolerance pin (RC-FLAG-3 disposition):** independent re-runs of the comparator match within `1e-12` on `max_relative_error` (the verifier is deterministic — least-squares fit over a closed-form grid; tighter than the v0.1 `1e-9` which was unsourced). Source: the verifier has no stochastic components; `1e-12` is the floor for float64 arithmetic in the β-fit + grid-evaluation chain.
- All raw outputs reproducible from the cohort_5_strip code at the commit pinned in `consumed_strip_audit_block`.

**Commit message:** `eval(stage-3-a1): TP1 envelope evaluation log for all filtered candidates`

---

## §7 Phase 3 — Verdict

### Task 3.1 — Apply the P-A1.4 5pp threshold and emit verdict

**Files:**
- Create: `scratch/2026-05-11-a1-panoptic-survey/verdict_rationale.md`
- Create: `simulations/saas_builder/data/strategy_verdict.json` (schema v1.0)

**Agent dispatch:** `Senior Developer` for the JSON emit + `Reality Checker` for the verdict-rationale audit.

**Acceptance:**
- Verdict JSON schema:

  ```
  {
    "schema_version": "v1.0",
    "verdict": "KEEP" | "REPLACE",
    "primitive_id": "<id of winning candidate>",
    "rationale_citation": "<row reference in STRATEGY_COMPARISON.md>",
    "envelope_at_tp1": <max_relative_error>,
    "envelope_delta_vs_ironcondor_pp": <signed float, positive = candidate beats IronCondor>,
    "p_a1_4_threshold_pp": 5.0,
    "comparability_proof": "tiled_body" | "primitive_variant" | "normalized_score",
    "audit_block": "<sha256>",
    "consumed_strip_audit_block": "94150326..." (full strip audit at evaluation time)
  }
  ```
- **Sign convention pin (MQ-FLAG-A1.4 disposition).** `envelope_delta_vs_ironcondor_pp = ironcondor.max_relative_error - candidate.max_relative_error`, expressed in percentage points (multiply by 100). Positive delta = candidate has LOWER envelope error = candidate REPLICATES BETTER than IronCondor. Negative delta = candidate is WORSE.
- KEEP verdict iff `max(envelope_delta_vs_ironcondor_pp for all candidates) < 5.0` (strict — no candidate beats by ≥ 5pp).
- REPLACE verdict iff at least one candidate has `envelope_delta_vs_ironcondor_pp >= 5.0` (the master-spec §2.1 pre-pinned threshold; see Pin P-A1.4).
- **Multi-candidate tie-break pin (MQ-FLAG-A1.3 disposition).** If MULTIPLE candidates qualify above 5pp:
  (i) winner = the candidate with the HIGHEST `envelope_delta_vs_ironcondor_pp` (most replication improvement);
  (ii) on float-tie within `1e-12`, secondary sort by `primitive_id` lexicographic ascending;
  (iii) if the float-tie spans more than 2 candidates AND they have different `comparability_proof` types, HALT — disposition memo, user-enumerated tie-break (the comparability-proof type-comparability question is unresolved within the plan).
- `audit_block` covers `(STRATEGY_COMPARISON.md` sha256 + `envelope_evaluation_log.md` sha256 + `consumed_strip_audit_block` + this JSON's other fields)`.
- A round-trip read-back test confirms the emitted JSON matches the in-memory verdict.

**HALT triggers (per master-spec §2.1):**
- Multiple candidates tie within the threshold → HALT, disposition memo, user-enumerated tie-break.
- The winning candidate's `comparability_proof` is `"primitive_variant"` AND the primitive-specific verifier variant was never authored → HALT, route to a Phase-2 amendment.

**Commit message:** `verdict(stage-3-a1): emit strategy_verdict.json + rationale trace`

---

### Task 3.2 — If REPLACE, draft the delta-spec stub

**Files (only if Task 3.1 emitted REPLACE):**
- Create: `docs/specs/2026-05-{NN}-cohort-5-strip-delta-spec.md` (stub, content out of A1 scope)

**Agent dispatch:** `general-purpose` (lightweight scaffolding only).

**Acceptance:**
- Stub spec header includes `parent_strategy_verdict_audit_block` pointing to Task 3.1's JSON.
- Stub lists the cohort_5_strip files that the swap would touch (types.py / geometry.py / replication.py / emit.py + tests).
- Stub explicitly defers full design to a follow-up brainstorming cycle.

If Task 3.1 emitted KEEP, skip Task 3.2 entirely.

**Commit message:** `spec(stage-3-cohort-5-delta): stub for post-A1 REPLACE swap`

---

## §8 Pin coverage (per master spec §5)

| Pin | This plan's coverage |
|-----|-----------------------|
| P-A1.1 (comparison-table completeness) | Task 1.1 + Task 1.2 emit the STRATEGY_COMPARISON.md table; Wave-2 RC review verifies all admissible-emit primitives are covered. |
| P-A1.2 (envelope evaluation reproducible) | Task 2.4 emits envelope_evaluation_log.md; Task 3.1's strategy_verdict.json carries the audit_block. RC cross-check enforces reproducibility. |
| P-A1.3 (verdict citation-backed) | Task 3.1 emits `rationale_citation` field referencing a comparison-table row. |
| P-A1.4 (5pp threshold pre-pinned) | Task 3.1's threshold logic uses the master-spec-pinned 5.0 constant; the JSON emits the constant explicitly so any post-hoc adjustment is detectable in `git diff`. |

## §9 HALT routing

| Trigger | Route |
|---------|-------|
| Task 1.2 yields < 2 candidates | HALT — disposition memo, master-spec scope re-pin via §6.4 escalation. |
| Task 2.x adapter fails Hypothesis property tests | HALT — Senior Developer iterates; do NOT relax property tests. |
| Task 2.4 envelope evaluation log has unreplicable numbers | HALT — investigate non-determinism in `CarrMadanEnvelopeVerifier`; this is a cohort_5_strip drift, route to a strip-level patch. |
| Task 3.1 multiple-candidate tie within 5pp | HALT — user-enumerated tie-break per master-spec §2.1 HALT-trigger #1. |
| Wave-1 or Wave-2 RC+MQ on this plan returns BLOCK | HALT per master-spec §6.1; CORRECTIONS-α landed in this plan's §11. |

## §10 Artifacts emitted

| Artifact | Phase | Schema | Lineage parent |
|----------|-------|--------|-----------------|
| `scratch/2026-05-11-a1-panoptic-survey/STRATEGY_COMPARISON.md` | 1 | markdown | (none — research output) |
| `scratch/2026-05-11-a1-panoptic-survey/envelope_evaluation_log.md` | 2 | markdown | `IronCondor_strip.audit_block` |
| `scratch/2026-05-11-a1-panoptic-survey/verdict_rationale.md` | 3 | markdown | both above |
| `simulations/saas_builder/data/strategy_verdict.json` | 3 | v1.0 (new) | sha over (1) + (2) + strip audit |
| `simulations/saas_builder/cohort_5_strip/strategies/` package | 2 | code | reverse-IC adapter re-uses existing strip emit; new adapters are additive |
| `docs/specs/2026-05-{NN}-cohort-5-strip-delta-spec.md` (if REPLACE) | 3 | spec stub | strategy_verdict.json audit |

## §11 CORRECTIONS-α (patch log)

### §11.1 v0.1 → v0.2 (Wave-1 RC+MQ disposition)

**Wave-1 review verdict:** RC ACCEPT_WITH_FLAGS + MQ ACCEPT_WITH_FLAGS (2026-05-11). 0 BLOCKs. Verdict files:
- `scratch/2026-05-11-stage-3-a1-rc-mq-review/rc-verdict.md`
- `scratch/2026-05-11-stage-3-a1-rc-mq-review/mq-verdict.md`

| Finding | Severity | Disposition | Location |
|---------|----------|-------------|----------|
| MQ-FLAG-A1.1 | Material | New Task 2.3b authors primitive-variant verifiers when needed; equivalence-test against `CarrMadanEnvelopeVerifier` on reverse-IC required. v0.1 omitted this authoring step. | §6 Task 2.3b |
| MQ-FLAG-A1.2 | Material | `normalized_score` formula pinned as a frozen module-level constant in Task 2.1 spec: `max_relative_error × (1 + |Π_strip(S_0)| / max|Π_strip|)`. Ex-post adjustment requires CORRECTIONS-α + fresh Wave-1 review. | §6 Task 2.1 |
| MQ-FLAG-A1.3 | Material | Multi-candidate tie-break pinned: highest envelope-delta wins; float-tie → secondary sort by `primitive_id` ascending; multi-candidate float-tie with different comparability-proof types → HALT. | §7 Task 3.1 |
| MQ-FLAG-A1.4 | Material | Sign convention pinned: `envelope_delta_vs_ironcondor_pp = ironcondor.max_relative_error - candidate.max_relative_error`, multiplied by 100 (percentage points); positive = candidate replicates BETTER. | §7 Task 3.1 |
| MQ-FLAG-A1.5 | Material | New `ComparabilityProofFalsifiedError` exception class; comparator runtime-verifies `tiled_body` claims via `assert_long_vol_signature` and `primitive_variant` claims via the variant-verifier-equivalence test. | §6 Task 2.1 + Task 2.3 |
| RC-FLAG-1 | Material | `general-purpose` dispatch rationale added: research+markdown tasks map to `general-purpose` because no Panoptic-domain specialist exists in the agent catalog (consistent with the spirit of `memory/feedback_specialized_agents_per_task.md`). | Task 1.1 |
| RC-FLAG-2 | Material | Task 2.4 RC dispatch re-labeled explicitly as "per-task accuracy gate, NOT a Wave-2 review" — Wave-2 RC+MQ on A1 exit deliverables runs separately after all phases complete. | §6 Task 2.4 |
| RC-FLAG-3 | Material | Task 2.4 reproducibility tolerance changed from unsourced `1e-9` to `1e-12` with rationale (verifier is deterministic; float64 floor). | §6 Task 2.4 |
| MQ-NIT-A1.1 | Cosmetic | Reverse-IC numerical baseline pin added: `max_relative_error ≈ 0.2813` at TP1, matches `IronCondor_strip.STRIKES.md` line 25. Eval log MUST match within 1e-6. | §6 Task 2.4 |
| MQ-NIT-A1.2 | Cosmetic | Comparator tie-break: secondary sort by `primitive_id` ascending (lexicographic) on float-tie within 1e-12. | §6 Task 2.3 |

### §11.2 v0.2 → v0.3 (in-execution predicate tightening; scoped Wave-1 re-review)

**Trigger.** Task 1.2 implementer applied the v0.2 filter rule `admits_strip_emit AND convexity_class != "short-vol"` strictly and produced 11 candidates + 1 baseline = 12, well above the plan's "2–4 primitives" estimate. The mismatch revealed a drafting slip in v0.2: the rule `!= "short-vol"` admits mixed-vol primitives (call_spread, put_spread, super_bull, super_bear, call_ratio_spread, zebra), which mathematically CANNOT cleanly Carr-Madan-replicate long-variance.

**Math anchor (PRIMITIVES.md §10).** The Carr-Madan strip identity (eq. 18) replicates σ_T as a positive-weighted integral of OTM put + call payoffs. The integrand is non-negative everywhere; the long-vol primitive family is the positive-Borel-measure-weighted closure of `{OTM put payoff, OTM call payoff}`. Mixed-vol combos (call_spread, put_spread, super_bull, super_bear, call_ratio_spread, zebra) carry **negative distributional δ-mass at one or more strikes** (point-concavity in their piecewise-linear payoff) and therefore lie OUTSIDE that cone — they cannot be expressed as a single 2/K²-weighted Carr-Madan combination. (MQ-V03-FLAG-1 wording-precision fix: piecewise-linear payoffs have Γ ≡ 0 almost everywhere, with concavity manifesting at isolated kink-points as negative distributional δ-mass; "negative Γ region" is loose for this class.)

**Effect on the Phase-2 lanes.** The centered-strip / β-fit / log-contract-proxy envelope verifier produces an algebraically well-defined `max_relative_error` even on a mixed-vol candidate, but the resulting number is **operationally uninterpretable** — it does not represent σ_T-replication quality because mixed-vol primitives do not replicate σ_T. The `comparability_proof = "normalized_score"` lane is in the same boat: the `max_rel_err × (1 + |Π(S_0)|/max|Π|)` formula runs and produces a finite number, but the number lacks a σ_T-replication semantic. (MQ-V03-FLAG-2 wording-precision fix: v0.3 prose initially said "broken" — the algebra runs, the interpretation does not.) Excluding mixed-vol via the v0.3 predicate prevents Phase-3 from comparing operationally-uninterpretable scores against operationally-meaningful long-vol scores.

**Predicate tightening (replaces v0.2 rule).** Filter rule v0.3:
```
candidate qualifies iff:
    admits_strip_emit = "yes"
  AND
    convexity_class == "long-vol"    (strict; NOT "!= short-vol")
```
The strict equality excludes mixed-vol primitives and concentrates Phase-2 evaluation on the primitive family for which the envelope metric is mathematically defined.

**This is NOT fishing because.** The predicate change is anchored ex-ante in PRIMITIVES.md §10 (a frozen Stage-2 derivation), not in the observed candidate counts. The motivation is mathematical correctness of the envelope metric, not target-count tuning. The §10 anchor was always available; v0.2's "!= short-vol" was a drafting error that this CORRECTIONS-α surfaces.

**Scoped Wave-1 re-review.** Per master-spec §6.4, the predicate change requires fresh RC+MQ Wave-1 verdicts SCOPED TO THIS CORRECTIONS-α ENTRY ONLY (not a full plan re-review). Verdicts land in `scratch/2026-05-11-stage-3-a1-rc-mq-review/wave-1-v0.3/rc-verdict.md` and `mq-verdict.md`. Master spec is unchanged (the predicate refinement lives at the plan level, not the master-spec level).

**Effect on Tasks 1.2 forward.**
- Task 1.2 implementer re-runs §5 of `STRATEGY_COMPARISON.md` with the v0.3 predicate. Prior v0.2 §5 content is overwritten in-place; old §5 candidates not matching v0.3 are listed in the "filtered-out" sub-list with the new rationale.
- Tasks 2.x and 3.x consume the v0.3 filtered set unchanged.
- Pin coverage in §8 is unchanged.

### §11.3 v0.3 → v0.4 (in-execution gate-2.4 precision-floor fix)

**Trigger.** Task 2.4 execution produced reverse-IC `max_relative_error = 0.2813412838694053` (full float64 precision). The plan v0.3 §6 Task 2.4 acceptance pinned baseline match within `1e-6` against the published `STRIKES.md` value `2.8134e-01`. Drift vs the truncated 5-sig-fig string is `1.28e-6` — just above `1e-6`. Investigation (Wave-1 RC re-review on Task 2.4):

- `consumed_strip_audit_block` matches verbatim → NOT cohort_5_strip drift.
- Bit-exact reproducibility across re-runs (`|Δ| = 0.0`) → NOT non-determinism.
- Independent recompute by RC reviewer = `0.2813412838694053` exactly.

**Root cause.** The plan v0.3 `1e-6` tolerance is tighter than the published baseline's emission precision floor (`2.8134e-01` is a 5-sig-fig markdown emission; precision floor `~5e-5`). Comparing a 17-sig-fig float to a 5-sig-fig string and asserting `1e-6` is mathematically incoherent — the gate is structurally false-FAIL even on the bit-exact-correct value.

**Fix.** Relax the gate-2.4 tolerance from `1e-6` to `5e-5` (matches the published baseline's 5-sig-fig emission precision). Task 2.4 §6 Task 2.4 acceptance updated inline above.

**Anti-fishing posture.** The fix matches the baseline emission's actual precision — it does NOT relax tolerance to "fit observed drift." The relaxation is mathematically justified by the baseline string's precision floor, NOT by the observed `1.28e-6` value. If a future cohort_5_strip change produced drift `> 5e-5`, the gate would still FAIL.

**Scope.** Plan-level only; cohort_5_strip code, master spec, and Task 2.4 eval log are unchanged. Task 2.4 deliverable was SPEC_COMPLIANT at Wave-1 review; this CORRECTIONS-α just updates the plan's tolerance number to a coherent value for any future re-runs.

### §11.4 Wave-2 (post-execution) review reserve

Wave-2 RC+MQ on this plan's exit deliverables lands its own block at §11.5.

## §12 References

- `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2 — master spec.
- `simulations/saas_builder/cohort_5_strip/__init__.py` — Pin S1–S8 framing this plan extends.
- `simulations/saas_builder/cohort_5_strip/replication.py:1-28` — verifier docstring (canonical envelope form).
- `simulations/saas_builder/cohort_5_strip/types.py:57-74` — `REPLICATION_REL_TOL = 0.35` rationale.
- `notes/PRIMITIVES.md` §10 (Carr-Madan), §11 (discrete strip).
- `memory/feedback_no_code_in_specs_or_plans.md` — plan-as-orchestration-only convention.
- `memory/feedback_specialized_agents_per_task.md` — foreground-orchestrates-never-authors.

---

*End of A1 plan v0.1. Wave-1 RC+MQ review dispatch before any task execution.*
