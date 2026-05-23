# Reality-Checker Verdict — SAAS-COHORT-4 plan-doc (Wave 1 of 2)

**Plan:** `docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md` (v0.1)
**Default posture:** REJECT unless overwhelming evidence supports otherwise.
**Reviewer:** TestingRealityChecker (Wave 1 — Reality Check; Wave 2 = Model QA pending).

## Verdict: ACCEPT_WITH_FLAGS

Evidence across 11 reality-check dimensions: 8 PASS, 3 FLAG, 0 BLOCK. The
plan satisfies the dispatchability, prerequisite-gate, M2 grid pre-pinning,
ZCapPinned schema-match, audit-block helper usage, sidecar-emit discipline,
out-of-scope discipline, and Honnibal canonical ordering requirements with
file-path concreteness. Three FLAGs are non-blocking but should be addressed
in v0.2.

## PASS findings (evidence cited)

- **D1 Agent dispatchability** — Task 0.5 (lines 171–173) runs `find` over
  `~/.claude/agents` for the five named agents (`engineering-ai-engineer`,
  `specialized-reality-checker`, `specialized-model-qa`,
  `engineering-code-reviewer`, `specialized-gsd-phase-researcher`) and HALTs
  on archived state. Active-registry gate present.
- **D2 C1/C2/C3 prerequisite gate** — Task 0.4 (lines 165–168) HALTs if
  `synthetic_tau_t.parquet` (C1), `cohort_prior.parquet` (C1),
  `ROBUSTNESS_RESULTS.md` (C2), `PRIMARY_RESULTS.md` (C3) absent. Phase 0
  gate matches the demand exactly.
- **D3 5-test-point grid pre-pinned** — Pin M2 table (lines 72–78) lists
  TP1–TP5 verbatim: {κ₀, 0.5κ₀, 1.5κ₀, FX=4200, FX=3800}. Each row carries
  an explicit pre-evaluation sign expectation (`π(t) > 0` ∀ t) plus
  monotonicity constraints (TP3 < TP1 < TP2 in |π|). Line 80: "No test
  point may be added, removed, or perturbed post-hoc."
- **D4 ZCapPinned schema match** — Pin M3 (lines 86–91) reproduces the
  shipped `simulations/types/posterior.py` field list verbatim:
  `Z_cop_per_month`, `ci_95_lo`, `ci_95_hi`, `audit_block`, `tier_mix`,
  `schema_version`. Cross-checked against posterior.py lines 202–209 and
  json_io.py `Z_CAP_PINNED_FIELDS` lines 24–31 — identical 6-field set.
- **D5 audit-block helper used** — Pin M4 (lines 95–100) explicitly calls
  `simulations.utils.audit_block.compute_audit_block` + `AuditBlockHasher`;
  Task 2.3 (line 300) uses `compute_audit_block(...)` not ad-hoc hashing.
  Path canonicalization via `Path.resolve()` mandated (line 110, 299).
- **D6 Transient Pydantic validator** — Plan line 26 cites
  `simulations.utils.json_io._ZCapPinnedJsonModel` as the transient
  validator. Task 2.3 (line 302) routes emission through
  `ZCapPinnedWriter`, which internally uses the private model. Read→
  frozen-dc→JSON path preserved.
- **D7 Sign-verdict sidecar** — Pin M3 (lines 92–93) explicitly states the
  5-TP verdicts are emitted as sidecar `Z_cap_pinned.SIGN_VERDICTS.md`
  rather than schema-extending `ZCapPinned`. Schema-bump deferred to a
  future plan with explicit note. This matches the demand verbatim.
- **D8 File-path concreteness** — All emitted file paths are absolute
  within the repo (no TBD): `simulations/saas_builder/data/Z_cap_pinned.json`,
  `Z_cap_pinned.SIGN_VERDICTS.md`, `simulations/tests/test_saas_cohort_4.py`,
  `scratch/2026-05-08-saas-cohort-4-{research,audit}/...`.
- **D9 Out-of-scope discipline** — Lines 23–28: C1, C2, C3 fits explicitly
  excluded; PyMC sampler authoring excluded; deployment excluded.
- **D10 Honnibal canonical ordering** — Phase 3 (line 349): tighten-types
  → contract-docstrings → hypothesis-tests → try-except → pre-mortem →
  mutation-testing. Matches SIM-INFRA-0 v1.1 §15.5.
- **D11 2-wave verifier structure** — Lines 464–465: "this plan must be
  2-wave verified (Reality Checker + Model QA Specialist) by foreground
  orchestration before commit, separate from Phase 4." Phase 4 itself
  re-runs RC + Model QA on implementation.

## FLAGs (non-blocking; address in v0.2)

- **FLAG-1 (Task 2.1, line 236):** suggests the implementer MAY extend
  `simulations/types/posterior.py` to host a new `PiTDerivation` Value with
  `schema_version` bump to `v1.1`. This is a schema-extension hedge that
  partially contradicts Pin M3's schema-bump-deferred posture. Recommend
  forcing `PiTDerivation` to live in `simulations/saas_builder/pi_t_symbolic.py`
  (Callable-tier Value adjacent to consumer) and removing the alternative.
- **FLAG-2 (Task 2.2, line 268):** identity-tolerance gate carries two
  thresholds (`≤ 10⁻¹⁰ N_legs` symbolic, `≤ 10⁻⁶` numerical). The
  numerical relaxation is justified by finite-t discretization but should
  cite PRIMITIVES.md §12 or Path A v0 §10.4 inline as the inheritance
  source rather than parenthetically. Wave-2 Model QA will likely re-flag.
- **FLAG-3 (Task 2.4, line 335):** Hypothesis property strategy for
  `PiTDerivation` says "sympy-arity-bounded" without pinning the bound.
  Add an explicit arity ceiling (e.g., max 6 free symbols) to keep the
  property strategy bounded and reproducible.

## Re-assessment requirement

After v0.2 addresses the three FLAGs, no re-RC required (FLAGs are
non-load-bearing). Wave-2 Model QA Specialist verdict is the gating
verifier for the math-pin chain; this RC pass does not pre-empt it.

---
**RC verdict:** ACCEPT_WITH_FLAGS
**Word count:** ~590
