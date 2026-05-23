---
artifact_kind: independent_reality_check_implementation_verdict
auditor: Reality Checker (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-08
target_commit_range: 0a6bec0..17f83b6 (Phase 0–4 of notebooks-trio plan)
default_verdict: REJECT
---

# RC Wave-1 Verdict — Notebooks-Trio Implementation (Phase 0–4)

## Verdict: ACCEPT_WITH_FLAGS

The implementation passes every load-bearing empirical claim made in the design,
plan, and verdict-memo: 458/458 pytest GREEN, 35/35 in the verify-relevant
subset (9 audit-value + 3 audit-reader + 23 verify), all three notebooks
execute headless in 24.4 s wall (well under the 60 s budget), trio audit
sha256 is reproducible, and the committed `Z_cap_pinned.json` matches the
M2 pin (4687.94 ± 1.0 COP/mo, CI lo = 168.17 > 0). Default REJECT is
overridden because every numeric and structural claim was independently
verified by direct command output, not by reading code in isolation.

Two non-blocking flags are recorded against the file-bytes anchor design
choice and one minor tier-import stylistic note. Neither blocks merge.

### Per-phase audit table

| Phase | Claim                                                | Evidence                                                                           | Verdict |
|-------|------------------------------------------------------|------------------------------------------------------------------------------------|---------|
| 0     | `simulations/types/saas_cohort1_audit.py` — frozen   | `Audit` + `AuditVerdict` both `@dataclass(frozen=True)`, full `__post_init__` gates | PASS    |
| 0     | `AuditReader` in `simulations/utils/json_io.py`      | Symbol exists, mirrors `ZCapPinnedReader` pattern, importable                       | PASS    |
| 0     | 9 audit-value tests + 3 audit-reader tests pass      | `pytest test_audit_value.py test_audit_reader.py` → 9 + 3 PASSED                    | PASS    |
| 1     | `RTagVerdict` `audit_sha256` non-Optional `str`      | `simulations/saas_builder/verify/types.py:30` — `audit_sha256: str`                 | PASS    |
| 1     | `CommittedArtifactLoader` audit_block validation     | `__init__` calls `_read_audit_block_field` on each artifact; raises on malformed   | PASS    |
| 1     | trio_audit_sha256 over file bytes (alphabetical)     | `_compute_trio_audit_sha256` orders by `p.name`; reproduced live = `147e01df…`     | PASS    |
| 1     | 8 free pure verifiers in `checks.py`                 | `verify_r1..r8_*` defined; all return `RTagVerdict`                                 | PASS    |
| 1     | 13 exports in `__init__.__all__`                     | 5 (Loader/exceptions/Values) + 8 (verifiers) = 13 — confirmed                       | PASS    |
| 1     | Three-tier discipline                                | types.py: stdlib only; checks.py: imports only Value tiers; io.py: imports utils    | PASS    |
| 2     | 23 verify tests pass                                 | `pytest test_verify.py` → 23 PASSED                                                 | PASS    |
| 2     | R2 negative test calls verifier (commit 910cdd7)     | Lines 86–115 build injected expression, assert κ retained, then call verifier with `pi_t_expression=injected` and assert `not v.passed` | PASS |
| 2     | R4 wrong-factorization (4×2×3×1) is real             | Lines 175–185 build `[(t,a,c,0) for t∈4, a∈2, c∈3]`, assert `len==24` then `not v.passed` | PASS |
| 2     | Audit-block tamper test raises `AuditBlockMismatch`  | Lines 319–337 mutate `audit_block` to `"not-a-hex"`, `pytest.raises(AuditBlockMismatch)` | PASS |
| 3     | `01_math_anchors.ipynb` covers R1–R5                 | Headers §2.1 R1, §2.2 R2, §2.3 R3, §2.4 R4, §2.5 R5 present                         | PASS    |
| 3     | `02_cohort_runs.ipynb` covers R6–R7                  | Headers §3.2 R6, §3.3 R7 present                                                    | PASS    |
| 3     | `03_z_cap_synthesis.ipynb` covers R8 + cross-rollup  | §4 R8 + §5 cross-trio TrioRollup re-runs R1–R8                                      | PASS    |
| 3     | Trio pattern (header / citation / WHY / CODE / INTRP)| Confirmed in nb-03 cells [2..6]: header → citation → boxed-LaTeX → code → interp    | PASS    |
| 3     | All notebooks execute headless < 60 s                | Live wall: 24.378 s (3 nbconvert executions chained, 0 errors)                      | PASS    |
| 4     | 3 PDFs in `…/figures/`                               | `pi_t_curve.pdf`, `s_t_survival.pdf`, `sigma_0_overlay.pdf` present                 | PASS    |
| 4     | `make notebooks` globs `simulations/notebooks/`      | Makefile target finds `notebooks simulations/notebooks` `-name '*.ipynb'`           | PASS    |
| Pin   | R1 σ₀ = 20,000 baseline                              | `test_r1_happy` passes with `(X̄/Ȳ)²·ε²/8 = (2)²·200²/8 = 20,000`                  | PASS    |
| Pin   | R3 perpetual identity residual ≤ 1e-8                | `test_r3_happy` passes; sympy limit = 0 exactly, residual = 0.0                     | PASS    |
| Pin   | R8 Z_cap = 4687.94 ± 1.0                             | Live load: `Z_cop_per_month = 4687.942347178384` — residual ≈ 0.058 COP             | PASS    |
| Pin   | R8 95% CI lo > 0                                     | Live load: `ci_95_lo = 168.172482700353`                                            | PASS    |
| AF    | R2 1/κ regression guard exercises verifier           | Inject `legit/κ`, precondition asserts κ retained post-simplify, then verifier returns `not passed` | PASS |
| AF    | No magnitude promises / pin relaxations introduced   | R8 tol = 1.0 COP unchanged from M2 pin; R1 expected = 20,000 unchanged              | PASS    |
| Live  | Full pytest suite GREEN                              | 458 passed, 4 warnings (cohort3 fork DeprecationWarning, unrelated), 24.66 s        | PASS    |
| Live  | `trio_audit_sha256` reproducible across constructions| Two `CommittedArtifactLoader('…/data')` → identical `147e01df…b480e0c2`             | PASS    |

## BLOCKs (must-fix before merge)

None.

## FLAGs (non-blocking)

1. **`trio_audit_sha256` is a file-bytes anchor, not the upstream-lineage
   anchor implied by per-artifact `audit_block`.** `io.py` lines 1–37 honestly
   document this: the four committed JSONs each carry an `audit_block` that is
   sha256 over UPSTREAM source bytes (`cohort_prior.parquet`,
   `synthetic_tau_t/` partitions), but the trio anchor is computed by
   alphabetically-ordered `sha256(file_bytes)`-of-`sha256(file_bytes)`. This
   is adequate for the trio's tamper-detection contract (and the second
   tamper test confirms it drifts on byte mutation), but it does NOT bind
   upstream provenance. A future hardening pass could wire
   `AuditBlockHasher` to re-derive the per-artifact `audit_block` from
   source files when those are present, with the file-bytes anchor as
   fallback. Documented as design-v0.3 §3a.4.1 deliberate scope cut, not a
   slip.

2. **`verify_r6_softplus_l1_tightness` does an in-function import of
   `simulations.types.distributions`** (`checks.py:276`). This is a Value-tier
   import (no IO) so tier discipline is preserved, but the deferred import is
   a stylistic outlier vs. the other verifiers, which import top-of-file. If
   future refactors add second consumers of `SoftplusParams` /
   `tightness_l1_deviation`, lift the import to module top. Cosmetic only.

3. **`_gate_verdict_from_dict` injects `ci_level=0.95` from the `_95` field
   suffix and `audit_block=""` for evidence entries that lack the field.** The
   docstring (`io.py:104–119`) is explicit about both, and the injection is
   correct given the on-disk pre-rename schema. Recording for audit-trail
   visibility — any future re-emit of `gate_verdict.json` should write the
   current schema (`delta_lower_bound_quantile` + explicit `ci_level`) and
   this shim can then be deleted. Not a defect; technical debt note.

## Evidence summary

```
$ git log --oneline 0a6bec0..17f83b6
17f83b6 build(make): notebooks target globs simulations/notebooks/
f6f8a3b feat(notebooks): figures — π(t) curve, S_t survival, σ₀ overlay
ea6009b feat(notebooks): 03_z_cap_synthesis.ipynb — R8 + cross-trio rollup
53b5ba0 feat(notebooks): 02_cohort_runs.ipynb — R6 + R7 trios
3127faa feat(notebooks): 01_math_anchors.ipynb — R1–R5 trios
a4fa182 feat(notebooks): env.py + references.bib + .gitignore for trio
910cdd7 refactor(verify): R2 verifier accepts optional pi_t_expression for testing
ffbae21 test(verify): 23 cases per design §3a.6 negative-case table
98e7fe0 refactor(verify-checks): tighten verdict semantics + R3 finite-guard
d70da52 feat(verify): checks tier — 8 R-tag verifiers as free pure functions
064a8b5 refactor(verify-io): tighten failure-mode diagnostics
1c9cc6d feat(verify): io tier — CommittedArtifactLoader + trio audit anchor
b72acb4 feat(verify): types tier — RTagVerdict + TrioRollup
126d51c refactor(audit-reader): bring AuditReader into ZCapPinnedReader symmetry
feccff4 feat(utils): add AuditReader for _AUDIT.json → Audit Value
5407284 refactor(audit-value): mirror posterior.py validation pattern + tighten gates
bf9c2f1 feat(types): add Audit Value-tier dataclass for _AUDIT.json schema

$ uv run pytest simulations/tests/
458 passed, 4 warnings in 24.66s

$ uv run pytest test_audit_value.py test_audit_reader.py test_verify.py -v
35 passed in 2.26s   (9 + 3 + 23, distribution per design)

$ time bash -c 'for nb in simulations/notebooks/saas_builder_stage_2/0*.ipynb;
                do uv run jupyter nbconvert --to notebook --execute --inplace "$nb";
                done'
[NbConvertApp] Writing 18883 bytes to .../01_math_anchors.ipynb
[NbConvertApp] Writing 11959 bytes to .../02_cohort_runs.ipynb
[NbConvertApp] Writing 12115 bytes to .../03_z_cap_synthesis.ipynb
real    0m24.378s     ← well under 60 s budget

$ uv run python -c "from simulations.saas_builder.verify import CommittedArtifactLoader;
                    L1 = CommittedArtifactLoader('simulations/saas_builder/data');
                    L2 = CommittedArtifactLoader('simulations/saas_builder/data');
                    print(L1.trio_audit_sha256, L2.trio_audit_sha256,
                          L1.trio_audit_sha256 == L2.trio_audit_sha256)"
trio_sha_1: 147e01dfcbda6a1b776beed403891ce5a1a5fefdd186c6dcf60e95e4b480e0c2
trio_sha_2: 147e01dfcbda6a1b776beed403891ce5a1a5fefdd186c6dcf60e95e4b480e0c2
reproducible: True

$ uv run python -c "...; z = L.load_z_cap_pinned(); print(z.Z_cop_per_month, z.ci_95_lo)"
Z_cop_per_month: 4687.942347178384
ci_95_lo:        168.172482700353
                 ↑ both within M2 pin (4687.94 ± 1.0 COP/mo; CI lo > 0)

$ ls simulations/notebooks/saas_builder_stage_2/figures/
pi_t_curve.pdf
sigma_0_overlay.pdf
s_t_survival.pdf

$ ls simulations/saas_builder/verify/
__init__.py  checks.py  io.py  types.py    (three-tier surface intact)
```

**Recommendation**: ACCEPT_WITH_FLAGS — merge `iter/saas-builder-stage-2`. The
three flags are documentation/refactor candidates, none gate the merge. The
notebooks-trio implementation faithfully realises design v0.3 §3a, the
verdict-memo §1 numeric pins, and the anti-fishing R2 1/κ regression guard
mandated by Stage-2 prereg-lock §6.
