# Reality-Check Verdict — Phase 4 Schema v1.0 → v1.1 Additive Bump

**Commit:** `7c539d9` on `iter/saas-builder-stage-2`
**Date:** 2026-05-08
**Default verdict:** REJECT (overridden by overwhelming evidence below)

## Verdict: ACCEPT

The bump is genuinely additive. All 10 dimensions confirmed by reading the four files under audit and executing the test suite + on-disk artifact inspection.

## Evidence

### D1 — v1.0 readers continue to work
`simulations/types/posterior.py:307`:
```
sign_verdicts: tuple[SignVerdictEntry, ...] | None = None
```
Default `None` preserves the v1.0 5-arg constructor signature. Test `test_v10_caller_constructor_signature_unchanged` (line 720) passes — verified `recovered.sign_verdicts is None` (line 734).

### D2 — v1.1 writers add per-TP fields
`json_io.py:250-262`: writer guards emission with `if z.sign_verdicts is not None:` — additive on disk. `test_v11_emission_includes_sign_verdicts_on_disk` (line 638) confirms 5-entry list with all 7 expected keys (line 659). On-disk artifact `simulations/saas_builder/data/Z_cap_pinned.json` shows `schema_version: v1.1` with 5 TP entries.

### D3 — Validator accepts both versions
`json_io.py:91`: `schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, min_length=1)` — no version-pinning rejection. `json_io.py:48` `Z_CAP_PINNED_OPTIONAL_FIELDS = ("sign_verdicts",)` and line 167 `unauthorized_extra = actual - required - optional` cleanly partitions both schemas. Tests `test_v10_file_read_by_post_bump_reader` (661) + `test_v11_file_read_yields_sign_verdicts_tuple` (683) both PASS.

### D4 — 5-tuple invariant on v1.1
`posterior.py:368-382` enforces `len == 5`, exact label set `{TP1..TP5}`, no duplicates. `test_v11_rejects_wrong_count` (737) and `test_v11_rejects_duplicate_labels` (759) both PASS.

### D5 — No v1.0 field removed
`json_io.py:33-40` `Z_CAP_PINNED_FIELDS` retains all 6 originals (`Z_cop_per_month, ci_95_lo, ci_95_hi, audit_block, tier_mix, schema_version`). Confirmed on-disk: `keys: ['Z_cop_per_month', 'audit_block', 'ci_95_hi', 'ci_95_lo', 'schema_version', 'sign_verdicts', 'tier_mix']`.

### D6 — No validation threshold changed
`posterior.py:329` audit-block regex `[0-9a-f]{64}` unchanged; `posterior.py:350` sum-to-one tolerance `1e-9` unchanged; sign-consistency `ci_95_lo > 0` (line 250) is the standard gate; identity tolerance/MC budget live in cohort_4 modules — not touched here.

### D7 — pin_and_emit emits v1.1 by default
`io.py:308`: `_build_z_cap_pinned(..., sign_verdicts=sign_verdicts)`. `io.py:237-246`: when `sign_verdicts is not None`, sets `schema_version = SCHEMA_VERSION_V1_1`. Live runner artifact confirms `schema_version: v1.1`.

### D8 — Sidecar .md still emitted
`io.py:325-329` calls `SignVerdictSidecarWriter` Step 7 unconditionally. Artifact present: `simulations/saas_builder/data/Z_cap_pinned.SIGN_VERDICTS.md`.

### D9 — Runner re-run verdict 5/5 PASS
Live JSON inspection: `all PASS: True`, `all identity_passes: True`, `max identity_residual: 6.31e-09` (well under `1e-6`), `all ci_95_lo > 0: True`.

### D10 — Tier-import discipline preserved
`grep "from simulations.saas_builder" simulations/types/ simulations/utils/` returns empty. `json_io.py` imports only `simulations.types.*` + `simulations.utils.errors`; `posterior.py` imports only `simulations.types.tier`. No reverse coupling.

## Test Suite Status

`pytest simulations/tests/` → all 63 tests PASS (test_utils.py: 17/17 schema-version tests including 8 new). No regressions.

## Flags

None blocking. Minor observation: `_build_z_cap_pinned` v1.0 branch (io.py:227-236) returns without explicit `schema_version` arg — relies on dataclass default `"v1.0"`. Clear, but a future v1.2 bump should pass version explicitly to avoid silent default drift. Not a v1.1 issue.

## Final Verdict: **ACCEPT**

The bump is mechanically additive: optional field + writer-guards + reader-extras-allowance + dataclass default `None` + cohort_4 wiring that opts into v1.1 when `sign_verdicts` is supplied. Backward-compat invariant (v1.0 file byte-identical pre/post bump when `sign_verdicts is None`) is enforced both in code (`json_io.py:250` guard) and in test (`test_v10_default_roundtrip_omits_sign_verdicts` line 605).
