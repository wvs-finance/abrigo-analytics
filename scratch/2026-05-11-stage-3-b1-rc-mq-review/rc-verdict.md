# RC Wave-1 verdict — B1 Foundry scaffolding plan v0.1

**Plan under review:** `docs/plans/2026-05-11-stage-3-b1-foundry-scaffolding.md` (v0.1, 2026-05-11)
**Master spec:** `docs/specs/2026-05-11-stage-3-first-wave-design.md` v0.2
**Reviewer:** Reality Checker (Delphi-independent of MQ)
**Verdict:** **ACCEPT_WITH_FLAGS** — 2 MATERIAL flags, 1 MINOR flag, 0 BLOCKs

---

## §1 Summary

B1 v0.1 is well-architected against the master spec §2.3 phase shape and correctly carries the MQ-FLAG-1 disposition (canonical centered-strip / β-fit / peak-normalized envelope formula) verbatim from §2.3 phase 4. The plan-as-orchestration discipline is honored — no Solidity, no Python (only one JSON-schema illustration in §6 Task 2.2 and one path-tree in §4, both admissible). Agent-dispatch convention is consistent across tasks. The cross-repo light-coordination posture matches master-spec §8.1.

Two MATERIAL flags concern reified type-system claims that do not exist in the codebase yet (RC-FLAG-1: `ParameterBracket` and the `(tier, alpha_arm, cache_regime, kappa_arm)` 4-tuple shape; RC-FLAG-2: `TimeGrid` / `BracketId` aliases) and the implicit ordering hazard for the cross-repo sha-pinning workflow (RC-FLAG-3). All three are fixable in v0.2 without re-running Wave-1 dispatch logic.

---

## §2 RC checks — pass / flag summary

| Check | Verdict | Note |
|---|---|---|
| Cross-repo target existence (analytics-only commit scope) | PASS | Plan §1, §2, §4, §7 consistently treat `thetaSwap-core-dev` as separate; no in-repo Solidity authoring implied. Repo not on local filesystem (only `abrigo-analytics` + `abrigo-marketing` siblings); plan does NOT claim local reachability. |
| Cross-repo sha pin workflow | FLAG (RC-FLAG-3, minor) | See §3.3. |
| JSON schema self-consistency + 24-bracket factorization | PASS | §6 Task 2.2 schema covers `schema_version`, `audit_block`, `n_brackets=24`, `time_grid`, `brackets[]` array; the `3 × 2 × 2 × 2` factorization is asserted in the Hypothesis test bullet. Matches Stage-2 §5.2: 3 tiers (Pro/Max-5x/Max-20x) × 2 α arms ({1.5, 2.5}) × 2 cache regimes (h={0.80, 0.95}) × 2 κ multipliers ({1.0, 2.0}) = 24. |
| Bracket-types reuse from cohort_2 | FLAG (RC-FLAG-1, material) | See §3.1. |
| Anti-pattern callouts (Task 1.1 §7) | PASS | All three are unambiguous and reflect genuine anti-fishing concerns: (i) re-deriving 35% from PRIMITIVES.md §12 row 1's 5% is the exact MQ-FLAG-4 / RC-FLAG-3 convergent disposition pattern recorded in master-spec §9.1 → P-A1.4; (ii) silent tolerance relaxation is the canonical post-hoc-fishing anti-pattern; (iii) bracket subsetting reduces statistical power below §5.2's pinned design. |
| Plan-as-orchestration (no in-plan code) | PASS | `grep -nE 'pragma\|contract \|assertEq\|forge test\|```solidity\|```sol'` returns only prose mentions, no fenced Solidity blocks. Only 2 fenced blocks total: a JSON schema illustration (§6 Task 2.2) and a path-tree (§4). Both admissible. Zero Python code. |
| Agent-dispatch convention | PASS | Task 1.1 (general-purpose, markdown), Task 1.2 (general-purpose, markdown), Task 2.1 (Senior Developer, frozen-dc Callable), Task 2.2 (Senior Developer, IO Boundary), Task 3.1 (N/A coordination), Task 3.2 (N/A orchestrator records). Consistent with `feedback_specialized_agents_per_task.md`. |
| Phase-3 deferral / evm-tdd routing | PASS | Task 3.1 correctly punts the cross-repo plan authoring into the `evm-tdd:phases:01-specify` chain on the `thetaSwap-core-dev` side; HANDOFF.md is the canonical input. No evm-tdd skill invocation is made FROM this repo's plan execution, which is correct. |
| File paths and tier discipline | FLAG (RC-FLAG-2, material) | See §3.2. |
| Envelope-assertion formula fidelity | PASS | §5 Task 1.1 §3 and §5 Task 1.2 anchor on `replication.py:1-28` + master-spec §2.3 phase 4. The "Why not `\|Π−K̂σ\|/\|K̂σ\|`" subsection is required (denominator collapse) and is required in Task 1.2 — verbatim with MQ-FLAG-1 disposition. |
| Tolerance authority (35%) | PASS | §5 Task 1.1 §3 + anti-pattern (i) at §5 Task 1.1 §7 + §8 P-B1.2 row all point at `cohort_5_strip/types.py:74` (`REPLICATION_REL_TOL = 0.35`) and explicitly bar re-derivation from PRIMITIVES.md §12 row 1's 5%. |
| HALT routing (§9) | PASS | Five trigger rows; each routes correctly. Critically, the "cross-repo forge test FAILS on ≥ 2 brackets" row routes to A1 per master-spec §2.3 HALT-trigger #2, not to a B1-level patch — anti-fishing-aligned. |

---

## §3 Material flags

### §3.1 RC-FLAG-1 (material) — `ParameterBracket` is NOT in `cohort_2/types.py`; the (tier, α-arm, cache, κ-arm) 4-tuple shape does not exist as a Value type

**Where:** §6 Task 2.1 bullet 2 says ``ParameterBracket` Value type with `(tier, alpha_arm, cache_regime, kappa_arm)` matching Stage-2 spec §5.2 24-bracket parameter family.` Bullet 4 says `the generator MUST re-import the mapping from `simulations.saas_builder.cohort_2.types` if it exists, NOT re-derive it.`

**Reality check.** Inspection of `simulations/saas_builder/cohort_2/types.py` (533 lines, exports listed in `__all__`):
- Exists: `BracketPoint`, `BracketGrid`, `T2CostParams`, `SignVerdict`, `CohortGateVerdict`, plus the `SPEC_ALPHA_BRACKET`, `SPEC_H_CACHE_BRACKET`, `SPEC_KAPPA_MULTIPLIERS`, `SPEC_TIER_KAPPA`, `SPEC_TIER_P_SUB_BAR` constants.
- DOES NOT exist: a `ParameterBracket` Value type; a `(tier, alpha_arm, cache_regime, kappa_arm)` 4-tuple frozen-dc.

The 24-bracket factorization (3×2×2×2) is empirically present as constants but is NOT reified as a single Value type. `BracketPoint` carries `(T2CostParams, FXPathParams, horizon_T)` — a related but distinct shape pinned to the M5 reconstruction anchors at `t ∈ {0, π/2, π}`.

**Why this matters.** Task 2.1's `if it exists, NOT re-derive` clause is undefined in the current repo state. The Senior Developer agent dispatched at Task 2.1 will land in one of three states, all unspecified by the plan:

1. Re-derive `ParameterBracket` as a NEW frozen-dc in `cohort_5_strip/fx_path_emit.py` (most likely) — creates a parallel type to `BracketPoint`, drift risk.
2. Re-export `BracketPoint` from cohort_2 and adapt the FX emitter to its (T2CostParams, FXPathParams, horizon_T) shape — semantically different from the 4-tuple the plan describes.
3. Add `ParameterBracket` to cohort_2/types.py as a sibling — touches a Stage-2 artifact mid-Stage-3, scope creep.

**Fix request (v0.2 CORRECTIONS-α §11.1):** Task 2.1 bullet 2 + bullet 4 should be rewritten to either (a) name the new Value type explicitly (e.g., `FXBracketSpec`) and acknowledge it is NEW in cohort_5_strip, scoped to FX-path emission only, with a documented bridge to cohort_2's `SPEC_ALPHA_BRACKET` / `SPEC_H_CACHE_BRACKET` / `SPEC_KAPPA_MULTIPLIERS` / `SPEC_TIER_*` constants; or (b) commit to importing and adapting `BracketPoint` / `BracketGrid` and re-shape the FX emitter signature accordingly. Either path is acceptable to RC; the current "if it exists" hedge is not.

### §3.2 RC-FLAG-2 (material) — `TimeGrid` and `BracketId` types are not defined and their tier placement is unspecified

**Where:** §6 Task 2.1 bullet 1: `__call__(brackets: tuple[ParameterBracket, ...], time_grid: TimeGrid) -> Mapping[BracketId, FloatArray]`.

**Reality check.** Neither `TimeGrid` nor `BracketId` appears anywhere in `simulations/`. `FloatArray` exists in `cohort_2/types.py:80` as `NDArray[np.float64]`. The plan does NOT specify which tier these new aliases land in (Value tier — `types/` — or co-located in `cohort_5_strip/`).

**Why this matters.** Three-tier discipline (per CLAUDE.md and SIM-INFRA-0) requires Value-tier types to live in `simulations/types/` or in a cohort-scoped `types.py`; ad-hoc aliases in a Callable-tier module (`fx_path_emit.py`) would violate the import-direction invariant (`types/ ↛ modules/utils`). The plan as written gives the Senior Developer no guidance.

**Fix request (v0.2):** Add a bullet to Task 2.1 specifying that `TimeGrid` (likely a frozen-dc with `t_start`, `t_end`, `n_points` + `__post_init__` monotone-validation) and `BracketId` (likely `TypeAlias = str` with a sha-pinned regex) belong in `cohort_5_strip/types.py` (the cohort-scoped Value tier, mirroring how cohort_2 organizes its types), NOT in `fx_path_emit.py`.

### §3.3 RC-FLAG-3 (minor) — cross-repo Wave-2 review ordering not buildable as stated

**Where:** §5 Task 1.1 acceptance §5: `Cross-repo sha pinning: a `thetaSwap_core_dev_commit_sha` field reserved (populated at B1 Wave-2 review time after the contract-side team merges).` §7 Task 3.2: `Wait for cross-repo Wave-2 verdict; record outcome.`

**Reality check.** B1's Wave-2 review on THIS plan dispatches AFTER all phases close. Task 3.2 is gated on the cross-repo team having (i) merged their `2026-05-{NN}-stage-3-b1-strip-replication-foundry.md` plan, (ii) run `forge test` 24/24, (iii) reported the verdict back. The plan does not name a coordination mechanism (PR cross-link? scratch memo? email?), nor does it bound the wait. If the cross-repo team is also Delphi-independent, the analytics-side Wave-2 review could be blocked indefinitely.

**Why this matters.** A plan whose terminal task is "wait for an external team" without a timeout or escape valve is fragile. Master-spec §3 "No hard ordering" promises A1/A2/B1 dispatch in parallel; B1 closure as a function of an external team's velocity introduces a hidden serial dependency.

**Fix request (v0.2, light):** Add to §9 HALT routing a sixth row: `Task 3.2 cross-repo verdict not received within [N=14] days of Task 2.2 commit → HALT, escalate to founder; this repo's Wave-2 dispatches against partial evidence (Phase-1 + Phase-2 deliverables only) with explicit cross-repo-verdict deferred to a follow-up B1.1.` This preserves analytics-side throughput and makes the dependency observable.

---

## §4 Pin coverage assessment

| Pin | Plan section | RC verdict |
|---|---|---|
| P-B1.1 (JSON schema + audit_block validation in Foundry) | §5 Task 1.1 §2 enumerates loader requirements; §8 row | COVERED |
| P-B1.2 (envelope assertion at 35% on canonical metric) | §5 Task 1.2 + §8 row | COVERED (formula correct, tolerance authority correct, anti-derivation guard present) |

Both Pin-coverage rows pass. The envelope formula in §5 Task 1.1 acceptance §3 is the master-spec §2.3 phase 4 formula verbatim by reference (`the EXACT centered-strip / β-fit / peak-normalized form from master-spec §2.3 phase 4 + replication.py:1-28`).

---

## §5 Final verdict

**ACCEPT_WITH_FLAGS.**

Land v0.2 with §11.1 CORRECTIONS-α dispositions for RC-FLAG-1 (name the new Value type explicitly + bridge to cohort_2 constants), RC-FLAG-2 (place `TimeGrid` / `BracketId` in `cohort_5_strip/types.py`), RC-FLAG-3 (add HALT row for cross-repo wait timeout). None require re-running Wave-1 dispatch logic; all three are tractable text edits to §5 Task 1.1, §6 Task 2.1, and §9.

Cross-reference MQ verdict before disposition lands.

---

**Reviewer:** RC
**Date:** 2026-05-11
**Word count (excl. tables / front-matter):** ~1380
