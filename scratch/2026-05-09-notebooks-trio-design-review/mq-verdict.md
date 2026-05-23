---
artifact_kind: independent_methodology_verdict
auditor: Model QA Specialist (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-08
target_artifact: docs/specs/2026-05-09-simulations-notebooks-saas-builder-stage-2-design.md (v0.2)
default_verdict: REJECT
---

# MQ Wave-1 Verdict — Notebooks Trio Design v0.2

## Verdict: ACCEPT_WITH_FLAGS

Two BLOCK-adjacent issues are downgraded to FLAG because they are
documentation/contract precision defects, not methodology breakage:
the math content, anti-fishing posture, three-tier discipline, and
verify-only contract are all sound. The two flagged defects are
(F1) the TypedDict reuse claim in §3a.4 referencing schemas that do
not actually exist in `simulations.utils.{parquet_io,json_io}`, and
(F2) a soft tamper-detection contract where `audit_sha256` is `None`
for several R-tags (R1–R5) and the spec does not say so. These must
be resolved in the writing-plan, but they do not invalidate the
design's methodology core.

---

## Methodology dimension scoring

### 1. R-tag scope completeness — PASS

All eight R-tags from `notes/STAGE_2_RESULTS.md` are present and
assigned exactly once. Confirmed by cross-walk:

- §2.1 R1 (σ₀)             → 01_math_anchors §R1
- §2.2 R2 (π(t))            → 01 §R2
- §2.3 R3 (perpetual id)    → 01 §R3
- §2.4 R4 (24-bracket)      → 01 §R4
- §2.5 R5 (marginalization) → 01 §R5
- §3.2 R6 (softplus)        → 02_cohort_runs §R6
- §3.3 R7 (S_t pin)         → 02 §R7
- §4   R8 (Z_cap)           → 03_z_cap_synthesis §R8

No double-counting. Clustering rationale (01 = sympy/numpy primitives,
02 = C2+C3 verdict JSONs, 03 = C4 emit) is defensible because each
notebook's IO surface is distinct. R5 placement in 01 is borderline
(it loads a posterior chain — see dimension 5) but acceptable since
the comparator is the analytic marginal, not a re-fit.

### 2. Verify-API soundness — PASS

Tier classification is correct:
- `RTagVerdict` / `TrioRollup` → frozen Value tier ✓
- 8 `verify_r{k}_*` free pure functions → Callable tier; §3a.3
  table inputs are scalars, frozen primitives, paths-as-strings, or
  pre-loaded dicts — no hidden filesystem or network side effects ✓
- `CommittedArtifactLoader` is the only class with `__init__` and is
  the only filesystem reader → IO Boundary tier ✓

R5's input `posterior_path` is a Path used internally — strictly
speaking this is a leak: a Callable receiving a path is doing IO. A
clean three-tier split would have `CommittedArtifactLoader` load the
chain trace into a numpy array first, then pass the array to
`verify_r5_marginalization_match`. Flagged below as F3.

### 3. Anti-fishing posture — PASS

The `κ ∉ free_symbols(π(t))` audit is genuinely capable of catching
a 1/κ re-introduction: sympy's `free_symbols` is structural, not
numerical, so any expression containing `1/κ` (or `κ`-bearing
sub-term) would surface κ in the symbol set. The §3a.6 regression
guard ("deliberate 1/κ re-introduction must fail") is NOT tautological
because it pins the *test for the test*: the pytest case must inject
a non-cancelling 1/κ into a candidate π(t) expression and assert the
verifier returns `passed=False`. This is a meaningful behavioural test.

The §3a.6 phrasing should clarify that the injected expression must
not algebraically simplify to a κ-free form (e.g. `1/κ - 1/κ + π(t)`
would simplify and falsely pass). Logged as F4 (precision, not block).

### 4. Tamper-detection contract — FLAG

§5 promises tamper-detection via `audit_block` sha256 threading. §3a.4
states "audit_sha256 is computed once at load time and threaded through
every `RTagVerdict.audit_sha256`." But §3a.3's input table shows that
R1, R2, R3, R4 receive **no JSON/parquet input** (they are
sympy/closed-form verifiers). For these four R-tags, no committed
artifact is loaded, so no `audit_sha256` exists to thread. The
`RTagVerdict.audit_sha256: str | None` field admits this explicitly
but the spec does not warn that 4/8 verdicts will have
`audit_sha256 = None` and therefore the tamper-check is silently
absent for half the trio.

Recommended fix: §3a.4 should pin a *trio-level* audit anchor (sha256
over the full `_AUDIT.json` + `Z_cap_pinned.json` + verdict JSONs)
and thread that into every `RTagVerdict.audit_sha256` so the tamper
chain is uniform across all 8 verdicts, not just the IO-bearing ones.
Flagged as F2.

### 5. Verify-only constraint preservation — PASS

R5 (`verify_r5_marginalization_match`) loads a saved posterior chain
trace (Phase 2 N_draws ≥ 712k) and compares empirical posterior means
to the analytic marginal. This is pure load + numerical compare; no
PyMC sampler invocation. Confirmed against §4 row R5 wording:
"empirical posterior mean from saved chain trace matches analytic
marginal at the same nodes." No re-fit. The §9 success bullet "No
PyMC import anywhere in the notebook directory" is consistent.

Caveat: if the saved chain is stored as an `arviz.InferenceData`
NetCDF, reading it pulls `arviz` (and transitively `pymc`'s schema
package) into the import graph. The success-bullet phrasing should
clarify "no `pymc.sample` invocation" rather than literal "no PyMC
import". Soft note, not flagged.

### 6. Magnitude-promise / pin-relaxation scan — PASS

Scanned v0.2 vs. STAGE_2_RESULTS.md / verdict memo / spec v1.2.1:

- σ₀ = 20,000 — pinned in verdict memo §1, repeated verbatim in §4
- residual ≤ 6.31e-9 — verdict memo §1, repeated in §4
- 24 brackets (3×2×2×2) — spec v1.2.1 §5.2, repeated in §4
- L¹ deviation < 1e-3·κ — M2 pin, repeated in §4
- λ ~ Beta(4.5, 95.5), S_t = (1-λ)^t — spec v1.2.1 §6.1, verbatim in §4
- Z_cap = 4,687.94 COP/mo, 95% CI [168.17, 14,606.14] — verdict memo §1

No new claim, no new magnitude, no relaxed pin. CORRECTIONS-α's
"strictly tightening" claim holds.

### 7. pytest coverage adequacy — FLAG

"≥ 2 cases per verifier (happy + injected drift)" is a floor, not a
ceiling — adequate as a minimum bar but several R-tags want >2:

- **R4 injected-drift**: 24 → 23 makes sense (drop one bracket); also
  test 25 (extra bracket) and 24-but-wrong-product (e.g. 4×2×3×1) to
  catch a verifier that only checks cardinality and not the
  3×2×2×2 factorization. The §3a.6 floor allows this but doesn't
  require it.
- **R6 negative case**: agreed with the prompt — a deliberately wide
  tightness (e.g. inject `tightness_l1_deviation = 1e-2·κ`, 10×
  the M2 pin) should fail. Currently §3a.6 only mandates a negative
  case for R2.
- **R7 HALT-on-flip**: a deliberate `Beta(4, 96)` (close but wrong)
  should fail — string-equality on the prior token is currently the
  only check; near-miss numerics deserve a guard.

Flagged as F5: §3a.6 should enumerate per-R-tag negative cases, not
leave them to plan-author discretion.

### 8. R-tag → verifier function naming consistency — FLAG

`verify_r3_perpetual_identity_residual` is misnamed for its return
type. Per §3a.2, every verifier returns `RTagVerdict` (with `residual:
float | None` as one field). The suffix `_residual` reads as "returns
a residual scalar" — confusing. The other seven verifiers do not have
type-suggesting suffixes (`_anchor`, `_eliminated_in_pi_t`,
`_cardinality`, `_match`, `_l1_tightness`, `_pin`, `_closed_form`).

Recommendation: rename to `verify_r3_perpetual_identity` (the residual
lives in `RTagVerdict.residual`). Pure naming nit but pytest IDs and
import-path readability matter for a verify surface that contributors
will grep. Flagged as F6.

### 9. TypedDict schema reuse claim — FLAG (largest defect)

§3a.4 claims: *"The TypedDict row schemas are reused from
`simulations.utils.parquet_io` / `simulations.utils.json_io` per
Phase 2 M4 pin — no schema duplication."*

Inspection of the actual modules shows:

- `simulations/utils/parquet_io.py` exports two TypedDicts:
  `CohortPriorRow` and `SyntheticTauRow`. Neither matches a verify
  loader return type.
- `simulations/utils/json_io.py` defines two **private Pydantic
  `BaseModel`** validators (`_SignVerdictEntryJsonModel`,
  `_ZCapPinnedJsonModel`) and exposes `ZCapPinnedReader` /
  `ZCapPinnedWriter` classes — there is **no public TypedDict**
  named `ZCapPinnedDict`, `GateVerdictDict`, `RevenueFormVerdictDict`,
  or `AuditDict` in either module.

The four TypedDicts named in §3a.4's `CommittedArtifactLoader`
signatures therefore do not exist in `utils`. Two valid resolutions:

1. **Add them to utils** (preserves the §3a.4 reuse claim, requires
   touching Phase-2-frozen modules — will need a SIM-INFRA-0
   mini-amendment because utils tier is supposed to be Phase-2-stable).
2. **Define them in `verify/io.py`** (cleaner: keeps the verify
   surface decoupled from utils internals, lets utils stay frozen,
   and matches the principle that a sub-package owns its own row
   schemas). This contradicts §3a.4's "no schema duplication"
   claim and the Phase 2 M4 pin would need a written exemption.

Either resolution is fine, but **the spec as written promises
something that does not exist on disk**. This is the most substantive
defect found. Flagged as F1.

---

## BLOCKs (must-fix)

None. All defects found are precision/contract issues that the
implementation plan can resolve before notebook authoring without
disturbing the math content or three-tier discipline.

## FLAGs (non-blocking)

**F1 (largest).** §3a.4's TypedDict reuse claim references schemas
(`ZCapPinnedDict`, `GateVerdictDict`, `RevenueFormVerdictDict`,
`AuditDict`) that do not exist in `simulations.utils.parquet_io` or
`simulations.utils.json_io`. Resolve in Phase 0 of the writing plan
by either adding the four TypedDicts to `utils/json_io.py` (with a
SIM-INFRA-0 mini-amendment recording the Phase-2-frozen-module touch)
or by defining them locally in `verify/io.py` (and rewriting §3a.4 to
say "verify-local TypedDicts; no coupling to utils internals"). The
second option is cleaner and is recommended.

**F2.** Tamper-detection contract is silently weaker for R1–R5
(sympy/closed-form verifiers receive no IO, so `audit_sha256 = None`).
Strengthen by computing one trio-level audit sha256 at loader
construction time (over the union of all loaded artifact JSONs) and
threading that into *every* `RTagVerdict.audit_sha256`, including the
sympy-only ones. Then the tamper chain is uniform across 8/8 verdicts,
matching §5's promise.

**F3.** R5's verifier signature `verify_r5_marginalization_match(
posterior_path, tol)` accepts a path and reads it internally — a Tier
violation (Callable doing IO). Move the chain load into
`CommittedArtifactLoader.load_posterior_chain() -> np.ndarray` and
pass the array to the verifier. Restores clean three-tier discipline.

**F4.** §3a.6's R2 regression guard should pin: the injected `1/κ`
expression must not algebraically simplify to a κ-free form (e.g.
`1/κ - 1/κ + π(t)` would falsely pass). Add an explicit
`sympy.simplify(injected).free_symbols` precondition assertion in
the test setup.

**F5.** §3a.6 mandates ≥2 cases per verifier but only enumerates a
negative case for R2. Extend to enumerate per-R-tag negative cases:
R4 (cardinality 23 *and* wrong-factorization 4×2×3×1), R6 (deliberate
wide tightness 1e-2·κ), R7 (near-miss prior Beta(4, 96) must fail).
Bumps test count from ≥16 to ≥20 — trivial cost, materially stronger.

**F6.** Rename `verify_r3_perpetual_identity_residual` →
`verify_r3_perpetual_identity` for naming-pattern consistency with
the other seven verifiers. The residual scalar lives in
`RTagVerdict.residual`, not in the function name.

---

## Methodology summary

The v0.2 design is methodologically sound on the high-stakes
dimensions: R-tag scope is complete and non-double-counted; the
verify-only constraint genuinely holds (no PyMC re-fit); the
anti-fishing 1/κ free-symbol audit is a real test (not a tautology)
and the §3a.6 regression guard backs it with CI; no magnitude promises
or pin relaxations were silently introduced; the three-tier
Value/Callable/IO split is correctly executed in §3a.1–§3a.4 modulo
one minor Tier leak in R5's signature. The CORRECTIONS-α
"strictly tightening" claim survives audit. The most substantive
defect is F1 — §3a.4 names four TypedDicts that do not exist in
`simulations.utils`, and resolution forces a choice between an
exemption against the Phase-2 utils freeze and a local-schema
definition in `verify/io.py`. The remaining flags (F2–F6) are
precision improvements that make the verify surface uniformly
strong rather than mostly-strong. Verdict: ACCEPT_WITH_FLAGS;
proceed to writing-plan with the six flags resolved in Phase 0.
