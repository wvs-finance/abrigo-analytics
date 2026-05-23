# Methodology QA Verdict — Phase 4 Schema v1.0 → v1.1 Additive Bump

**Commit**: `7c539d9` on `iter/saas-builder-stage-2`
**Auditor**: Model QA Specialist
**Date**: 2026-05-09
**Default verdict**: REJECT
**Rendered verdict**: **ACCEPT_WITH_FLAGS** (3 FLAGs, 0 BLOCKs)

---

## Dimension-by-dimension

### D1 — SignVerdictEntry semantic correctness — PASS

`posterior.py:218-224` carries `{label, z, ci_95_lo, ci_95_hi, sign, identity_residual, identity_passes}`. The `label` ∈ TP1..TP5 alphabet is sufficient as a coordinate handle: the (κ, X̄/Ȳ, σ₀) triple is a function of the TP index pinned in the cohort_4 spec/test-grid — encoding it on the JSON entry would duplicate state and create a drift surface (label vs. coordinates). Sidecar Markdown remains the human-readable coordinate cross-reference per `io.py:138-170`.

### D2 — identity_passes vs identity_residual redundancy — FLAG-1 (Low)

`posterior.py:224` carries both fields but `__post_init__` (`posterior.py:226-260`) does **NOT** enforce `identity_passes == (identity_residual ≤ NUMERICAL_IDENTITY_TOL)`. The docstring claims (`posterior.py:215`) "`identity_passes` is the boolean form of the pass/fail flag" yet no validator binds the two. A v1.1 writer can emit `identity_residual=0.0, identity_passes=False` and the schema accepts it. **Recommendation**: add post-init coupling check, or drop `identity_passes` and have consumers derive it from `identity_residual` against the spec-pinned tolerance.

### D3 — 5-tuple invariant — PASS

`posterior.py:368-372`: `if len(self.sign_verdicts) != 5: raise ValueError("ZCapPinned.sign_verdicts must have exactly 5 entries...")`. Test pin at `test_utils.py:737-757` (`test_v11_rejects_wrong_count`).

### D4 — No-duplicate-labels invariant — PASS (with redundancy)

`posterior.py:373-382` enforces both `set(labels) != {TP1..TP5}` (line 374) AND `len(set(labels)) != len(labels)` (line 379). The first check already implies no duplicates given count==5; the second is unreachable. Harmless, but defensive. Test pin at `test_utils.py:759-785`.

### D5 — Backward-compat correctness — PASS

`test_utils.py:661-681` (`test_v10_file_read_by_post_bump_reader`) hand-crafts a 6-field v1.0 payload, asserts `recovered.sign_verdicts is None` and `recovered.schema_version == "v1.0"`. Reader path `json_io.py:177-178` confirms the None branch. Writer additive semantics verified at `test_utils.py:605-623` (`test_v10_default_roundtrip_omits_sign_verdicts`): `assert "sign_verdicts" not in on_disk`.

### D6 — Forward-compat (v1.0 reader on v1.1 file) — FLAG-2 (Medium)

There is **no test** exercising a *pre-bump* v1.0 reader against a v1.1 file. The post-bump reader uses Pydantic `extra="forbid"` (`json_io.py:84`) BUT explicitly authorizes `sign_verdicts` via `Z_CAP_PINNED_OPTIONAL_FIELDS` at `json_io.py:48,167`. A *pre-bump* deployed reader (a stale clone, an old downstream consumer pinned to a previous commit) lacks both that allowlist and the Pydantic field — it would raise `SchemaMismatchError("extra=['sign_verdicts']")` followed by `pydantic.ValidationError`. The commit message states "v1.0 readers continue to work unchanged" which is **false for the literal pre-bump reader**; only the post-bump reader handles both schemas. **Recommendation**: clarify the commit message / Phase 4 docstring at `posterior.py:46-53` to specify "post-bump readers handle both v1.0 and v1.1 payloads"; treat true forward-compat (pre-bump reader on v1.1) as out-of-scope.

### D7 — Spec §10 schema strict superset — PASS

Required-field set (`Z_CAP_PINNED_FIELDS`, `json_io.py:33-40`) is unchanged from v1.0; `sign_verdicts` is in `Z_CAP_PINNED_OPTIONAL_FIELDS` (`json_io.py:48`). v1.1 ⊃ v1.0 strictly.

### D8 — No silent fishing — PASS

`io.py:176-193` (`_to_sign_verdict_entry`) is a pure projection from `cohort_4.types.SignVerdict` to `SignVerdictEntry`: `sign = "PASS" if sv.passes else "FAIL"` is content-preserving. The sidecar Markdown is still emitted (`io.py:325-329`); content is duplicated, not changed. The Phase 4 brief confines itself to lifting the sidecar payload onto the JSON — methodologically equivalent.

### D9 — audit_block sha256 stability — PASS

`AuditBlockResolver` (`io.py:79-132`) hashes the canonical 5-file PARQUET/MD/spec input list per `DEFAULT_AUDIT_INPUT_RELATIVE_PATHS` (`io.py:57-63`); the emitted JSON is **not** in the audit-block input set. Adding `sign_verdicts` to the JSON does not feed back into the digest. Verified by inspection — no test directly pins this stability against the schema bump (FLAG-3 below).

### D10 — Test coverage of v1.1 invariants — FLAG-3 (Low)

Coverage as observed in `test_utils.py`:

- 5-tuple count: covered (`test_v11_rejects_wrong_count`, line 737).
- Label uniqueness / set: covered (`test_v11_rejects_duplicate_labels`, line 759).
- `identity_passes` consistency with `identity_residual`: **NOT covered** (see FLAG-1).
- Per-TP `ci_95_lo > 0` ↔ `sign == "PASS"` consistency: **NOT directly covered**, but `SignVerdictEntry.__post_init__` (`posterior.py:250-254`) enforces it and it is exercised through round-trip tests.
- audit_block invariance under v1.0 → v1.1 bump: not pinned by an explicit test.

---

## Summary

| ID     | Severity | Issue                                                                           |
|--------|----------|---------------------------------------------------------------------------------|
| FLAG-1 | Low      | `identity_passes` ↔ `identity_residual` consistency not enforced in __post_init__ |
| FLAG-2 | Medium   | Commit-message overclaim: "v1.0 readers continue to work" applies to post-bump readers only |
| FLAG-3 | Low      | Missing explicit test pinning audit_block stability across v1.0 → v1.1 emission |

No BLOCKs. The additive bump is methodologically sound: superset relation preserved, additive emission verified byte-equivalent for v1.0 payloads (`test_utils.py:616-619`), 5-tuple + label invariants enforced and pinned. FLAGs are remediation-track.

**Verdict: ACCEPT_WITH_FLAGS.**
