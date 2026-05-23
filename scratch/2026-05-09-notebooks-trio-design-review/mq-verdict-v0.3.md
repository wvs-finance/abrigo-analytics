---
artifact_kind: independent_methodology_verdict
auditor: Model QA Specialist (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-08
target_artifact: docs/specs/2026-05-09-simulations-notebooks-saas-builder-stage-2-design.md (v0.3, commit 0aca03a)
predecessor_audit: scratch/2026-05-09-notebooks-trio-design-review/mq-verdict.md (Wave-1, v0.2 ACCEPT_WITH_FLAGS — 6 FLAGs F1–F6)
default_verdict: REJECT
---

# MQ Wave-2 REVERIFY — Notebooks Trio Design v0.3

## Verdict: ACCEPT

All six Wave-1 FLAGs (F1–F6) are resolved in v0.3 without methodology
regression. The patches strictly tighten the verify surface on every
axis the Wave-1 audit identified. No new methodology FLAGs introduced.
One INFO-level observation on the `Audit` Value addition is recorded
below for the implementation plan but does not block acceptance.

---

## Per-FLAG resolution audit

### MQ-F1 (TypedDict reuse claim) — RESOLVED

v0.3 chose **neither** of my Wave-1 options literally — it converged
with the stronger RC-BLOCK-1 framing: instead of inventing TypedDicts
or duplicating them in `verify/io.py`, the loader returns the
**existing frozen Value-tier dataclasses** from `simulations.types`
(`ZCapPinned`, `CohortGateVerdict`, `RevenueFormFit`). This is
methodologically superior to my F1 option-2 (local schema in
verify/io.py) because:

- It honors the Phase-2 utils freeze without invoking an exemption.
- It honors the global-types-first discipline of `simulations/README.md`
  §"Extension model" — verify/ is iteration-scoped, types/ is global.
- It avoids row-schema duplication entirely (rather than displacing it).

§3a.2 explicitly states "All committed-artifact data classes are
reused from existing `simulations.types`, not redefined." §3a.4 table
maps each loader to a concrete existing frozen-dc with file path. The
three-tier discipline is preserved: types/ ↛ modules/utils, modules/ ↛
utils, verify/types.py imports stdlib+numpy only, verify/checks.py
imports verify.types and modules callables, verify/io.py is the only
filesystem reader. Tier import discipline is unviolated.

**Verdict**: F1 resolved. Convergence with RC-BLOCK-1 is the right
outcome.

### MQ-F2 (silent tamper gap on R1–R5) — RESOLVED

§3a.4.1 enumerates a four-step trio-level sha256 mechanism:
(1) loader reads all four committed artifacts at construction;
(2) per-file sha256 is recomputed and asserted equal to embedded
`audit_block` field via `simulations.utils.audit_block.AuditBlockHasher`
(this addresses RC-FLAG-2's "real check, not display" framing);
(3) four per-artifact sha256s concatenated alphabetically and
re-hashed → `trio_audit_sha256`;
(4) every `RTagVerdict.audit_sha256` is bound to this trio anchor.

Confirmed in §3a.2: `audit_sha256: str` (NOT Optional, with explicit
parenthetical "NOT Optional — see §3a.4"). §3a.3 input table shows
every verifier including R1–R4 (sympy-only) accepts `audit_sha256` as
an input. §9 success criteria includes a dedicated bullet: "Every
`RTagVerdict.audit_sha256` (including R1–R4 sympy-only) carries the
trio-level anchor; the field is non-Optional."

The tamper chain is uniform across 8/8 verdicts. R1, R2, R3, R4 — all
sympy-only — receive the trio anchor even though they load nothing,
which closes the silent gap.

**Verdict**: F2 resolved. Stronger than my Wave-1 ask because the
embedded-vs-recomputed assertion (step 2) elevates this from "sha256
threading" to "real tamper detection at loader construction".

### MQ-F3 (R5 tier leak) — RESOLVED

§3a.3 R5 row reads: `verify_r5_marginalization_match(posterior_chain:
np.ndarray, tol, audit_sha256)`. No `posterior_path`. §3a.4 table adds
`load_posterior_chain() -> np.ndarray (shape (N_draws, n_params))`.
§3a.4 method block confirms `def load_posterior_chain(self) ->
np.ndarray`. §3a.3 explanatory text explicitly notes "The v0.2 R5
signature `posterior_path` was a tier leak (Callable performing IO);
v0.3 fixes per Wave-1 MQ-F3 + RC-FLAG-3."

Three-tier discipline restored: the Callable now receives a
pre-materialized array; only the IO Boundary class touches the
filesystem.

**Verdict**: F3 resolved.

### MQ-F4 (R2 simplification guard) — RESOLVED

§3a.6 R2 row pins: "(a) inject `1/κ + π(t)` → fail; **precondition
assertion** that `sympy.simplify(injected).free_symbols` is non-empty
before invoking the verifier (Wave-1 MQ-F4 — guards against `1/κ -
1/κ` cancellation false-pass)."

The precondition assertion is exactly what I asked for and the
rationale is correctly captured (cancellation false-pass vector).

**Verdict**: F4 resolved.

### MQ-F5 (per-R-tag negative cases) — RESOLVED

§3a.6 enumerates negative cases for every R-tag:

- R1: ε perturbed by 10× tol
- R2: 1/κ injection + simplify-precondition (per F4)
- R3: tol tightened 100×
- **R4: length 23 + length 25 + factorization 4×2×3×1** (3 negatives — exactly what F5 asked for: cardinality AND factorization)
- R5: tol tightened 1000× + chain shape mismatch
- **R6: tightness 1e-2·κ (10× M2 pin)** (exactly what F5 asked for)
- **R7: Beta(4, 96) near-miss + (1-λ)^(t-1) off-by-one exponent** (exactly what F5 asked for)
- R8: 1% perturbation + CI lower < 0

Test count: 8 happy + 12 negative = 20, plus 1 cross-cutting audit-block
mismatch test = ≥ 21. F5's ask was 16 → 20; v0.3 hits 21. §9 success
criteria includes the floor explicitly.

**Verdict**: F5 resolved.

### MQ-F6 (R3 naming) — RESOLVED

Spot-checked all references:
- §3a.3 table (L136): `verify_r3_perpetual_identity` ✓
- §3a.3 explanatory note (L150–152): explicit rename rationale ✓
- §4 table (L295): `verify_r3_perpetual_identity` ✓
- CORRECTIONS-α patch 6 (L471–472): rename pinned ✓

No stale `_residual` suffix references survive in the design. `grep`
on the file confirms 4 occurrences of `verify_r3_perpetual_identity`
(in §3a.3 table, §3a.3 narrative, §4 table, CORRECTIONS-α) and zero
of `verify_r3_perpetual_identity_residual`.

**Verdict**: F6 resolved.

---

## Methodology regression scan

### Tier discipline (v0.2 → v0.3)

No tier inversion introduced. The v0.2 tier leak (R5 path-as-input)
is FIXED, not regressed. types/ ↛ modules/utils is preserved
(`verify/types.py` imports stdlib+numpy only per §3a.1). modules/ ↛
utils is preserved (no module imports utils in the verify surface;
the loader composes utils internals from io.py only).

### `Audit` Value addition — global-types-first discipline

§3a.2 explicitly states the new `Audit` Value goes to
`simulations/types/saas_cohort1_audit.py`, NOT to `verify/types.py`.
This matches the global-types-first discipline of `simulations/README.md`
§"Extension model" (no per-iteration types/). The `AuditReader` lives
in `simulations/utils/json_io.py` following the established
`ZCapPinnedReader` pattern (§3a.4 precondition subtask). §9 success
criteria includes a dedicated bullet enforcing this placement.

**INFO (not a FLAG)**: the `Audit` Value addition does touch a
"Phase-2-frozen" tier, but the touch is global-types-tier (which is
the *intended* extension surface per the README) rather than
verify-local. This is the correct architectural choice. No SIM-INFRA-0
exemption is required because adding new frozen-dataclasses to types/
is sanctioned by the extension model. The implementation plan should
note this as a precondition phase (already does — Phase 0 explicit).

### Verify-only constraint (§3a.6 negative cases)

All 12 enumerated negative cases are verify-only: they inject bad
inputs into already-loaded artifacts (perturb a scalar, mutate a
sympy expression, mismatch a chain shape, near-miss a prior token).
None re-invoke `pymc.sample`. None re-fit. The verify-only contract
of §5 is preserved across the expanded test surface.

### CORRECTIONS-α v0.2→v0.3 fidelity

The 8 patches enumerated in CORRECTIONS-α match the diffs in the
v0.3 body. Citations spot-checked against my Wave-1 verdict:

- Patch 1 cites `mq-verdict L163–195` → my F1 entry runs L163–195 ✓
- Patch 2 cites `mq-verdict L79–96, L217–223` → §4 dimension scan L79–96 ✓; F2 FLAG entry L217–223 ✓
- Patch 3 cites `mq-verdict L225–229` → F3 entry L225–229 ✓
- Patch 4 cites `mq-verdict L231–235` → F4 entry L231–235 ✓
- Patch 5 cites `mq-verdict L237–241` → F5 entry L237–241 ✓
- Patch 6 cites `mq-verdict L243–246` → F6 entry L243–246 ✓

Citations are accurate. RC dedup correctly identified F1≡RC-BLOCK-1
and F3≡RC-FLAG-3, yielding 8 distinct fixes.

### Strictly-tightening posture

CORRECTIONS-α v0.3 claim: "Strictly tightening on every axis." Verified:
- Tamper chain: 4/8 → 8/8 (uniform anchor)
- Tier discipline: R5 leak closed
- Naming: R3 consistent with sibling verifiers
- Negative-case floor: 16 → 20+1
- Type reuse: invented dicts → existing frozen Values
- Audit chain: surface display → rehash+assert (real check)

No upstream pin relaxed. R1–R8 set unchanged. σ₀=20,000, residual≤6.31e-9,
24 brackets, 1e-3·κ tightness, Beta(4.5, 95.5), Z_cap=4,687.94 — all
verbatim.

---

## BLOCKs (must-fix)

None.

## FLAGs (non-blocking)

None.

## INFO

**I1.** §3a.4 precondition subtask adds new code to two
"Phase-2-frozen" modules (`simulations/types/saas_cohort1_audit.py`
new file; `simulations/utils/json_io.py` new `AuditReader` class).
The placement is methodologically correct (global-types-first), but
the implementation plan should treat Phase 0 as a discrete commit
that lands `Audit` + `AuditReader` BEFORE the verify sub-package is
authored, so PR review can audit the `_AUDIT.json` schema in
isolation. Not a methodology defect — sequencing guidance only.

---

## Methodology summary

v0.3 is methodologically sound and represents a strict tightening
over v0.2 on every axis the Wave-1 audit identified. All six Wave-1
FLAGs are resolved at or above the bar I set:

- F1 resolved by adopting the stronger RC-BLOCK-1 framing (existing-
  Values reuse beats local TypedDict redefinition).
- F2 resolved by a uniform trio-level anchor with real rehash+assert
  semantics (stronger than the sha256-threading I asked for).
- F3 resolved by signature change + new loader method, fully restoring
  three-tier discipline.
- F4 resolved with the exact `sympy.simplify` precondition I requested.
- F5 resolved with all three R-tag negative cases I enumerated (R4
  factorization, R6 wide tightness, R7 near-miss prior + exponent).
- F6 resolved with no stale references surviving.

No methodology regression detected. The new `Audit` Value addition
honors the global-types-first discipline. The verify-only constraint
holds across the expanded negative-case surface (no PyMC re-runs).
CORRECTIONS-α citations are accurate. No new BLOCKs or FLAGs.

Verdict: **ACCEPT**. Proceed to writing-plan; no further design
revisions required from a methodology standpoint.
