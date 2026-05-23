---
artifact_kind: independent_reality_check_verdict
auditor: Reality Checker (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-08
target_artifact: docs/specs/2026-05-09-simulations-notebooks-saas-builder-stage-2-design.md (v0.3, commit 0aca03a)
predecessor_audit: scratch/2026-05-09-notebooks-trio-design-review/rc-verdict.md
default_verdict: REJECT
---

# RC Wave-2 Verdict — Notebooks Trio Design v0.3 (REVERIFY)

## Verdict: ACCEPT

All four Wave-1 RC items (1 BLOCK + 3 FLAGs) are resolved by v0.3
without regression. The patches are surgical, cited to verdict line
numbers, and the strictly-tightening posture in CORRECTIONS-α v0.2→v0.3
is verifiable line-by-line. The v0.1→v0.2 CORRECTIONS block is
preserved verbatim. No new claims about codebase artifacts are
introduced that fail spot-check; the one new artifact reference
(`simulations/types/saas_cohort1_audit.py`) is correctly flagged as a
Phase-0 precondition that does NOT yet exist on disk. Cleared for
writing-plans hand-off.

## Per-Wave-1-item resolution audit

| Wave-1 item | v0.3 resolution location | Verification | Status |
|---|---|---|---|
| **RC-BLOCK-1** §3a.4 TypedDict misstatement | §3a.4 (design L158–197) + §3a.2 (L92–97) + §9 success criterion (L386–389) | §3a.4 table now names existing Values: `ZCapPinned` at `simulations/types/posterior.py`, `CohortGateVerdict` at `simulations/types/saas_cohort2_verdict.py`, `RevenueFormFit` at `simulations/types/saas_cohort3.py`. New `Audit` Value at `simulations/types/saas_cohort1_audit.py` (NEW — see precondition). §3a.4 L174–176 cites "Existing Pydantic-validated readers in `simulations/utils/json_io.py` (`ZCapPinnedReader` and equivalents)". §3a.2 L94–96 explicitly states "All committed-artifact data classes are reused from existing `simulations.types`, not redefined". §3a.4 L178–185 contains the precondition subtask language pinning the Phase 0 add to global types tier (NOT to `verify/types.py`). | RESOLVED |
| **RC-FLAG-1** R4 attribution overreach | §3a.3 (L137) + §4 (L296) | §3a.3 R4 row reads "Index sets in spec v1.2.1 §5.2; cardinality derivation in `notes/STAGE_2_RESULTS.md` §2.4 (R4)". §4 R4 row reads "(index sets per spec §5.2; cardinality derivation per `notes/STAGE_2_RESULTS.md` §2.4)". The "matches spec §5.2 verbatim" string is gone. Additionally L155–156 documents the correction explicitly. | RESOLVED |
| **RC-FLAG-2** audit_sha256 source-of-truth | §3a.4.1 L199–222 | L208–212 pins the rehash-and-assert mechanism: "the loader computes a fresh sha256 over the file bytes AND asserts equality with the embedded `audit_block` field … **This is a real tamper check, not window-dressing**". `simulations.utils.audit_block.AuditBlockHasher` is cited verbatim at L211–212 (verified to exist via `ls simulations/utils/audit_block.py`; `grep` confirms `class AuditBlockHasher` at line 71). L221–222 documents `AuditBlockMismatch` raise behavior at construction time before any verifier runs. | RESOLVED |
| **RC-FLAG-3** R5 fifth loader method | §3a.3 (L138, L143–147) + §3a.4 (L172, L195) | §3a.4 loader table includes `load_posterior_chain() → np.ndarray (shape (N_draws, n_params))`. `CommittedArtifactLoader` class signature L195 declares `def load_posterior_chain(self) -> np.ndarray`. §3a.3 R5 row inputs read `posterior_chain: np.ndarray, tol, audit_sha256` (no path). L145–147 documents the v0.2→v0.3 fix: "The v0.2 R5 signature `posterior_path` was a tier leak (Callable performing IO); v0.3 fixes per Wave-1 MQ-F3 + RC-FLAG-3". | RESOLVED |

## Regression scan

### Spot-check: new claims about codebase artifacts

| Artifact claim | Spot-check method | Result |
|---|---|---|
| `simulations.utils.audit_block.AuditBlockHasher` exists | `ls simulations/utils/audit_block.py` + `grep "class AuditBlockHasher"` | EXISTS — file present; `class AuditBlockHasher` at line 71 (IO-Boundary class implementing `simulations.types.protocols.AuditBlockHasher` Protocol). Citation correct. |
| `simulations/types/saas_cohort1_audit.py` does NOT exist (Phase 0 add) | `ls simulations/types/saas_cohort1_audit.py` | ABSENT — `No such file or directory`. Design correctly flags this as a Phase 0 precondition (§3a.4 L171 marks it "NEW — see precondition"; L178–185 enumerates the precondition subtask). No false claim of existence. |
| Existing Value classes (`ZCapPinned`, `CohortGateVerdict`, `RevenueFormFit`) at the cited paths | Confirmed in Wave-1 evidence (rc-verdict.md L145–149) | EXISTS — confirmed live at `simulations/types/posterior.py:264` (`ZCapPinned`), and previously verified `CohortGateVerdict` (`saas_cohort2_verdict.py`) + `RevenueFormFit` (`saas_cohort3.py`) via test imports. Citations correct. |

No new false-existence claims. The `Audit` Value being labelled "NEW" is the correct epistemic posture.

### §9 success-criteria consistency with §3a content

§9 v0.3 additions (L381–399) checked against §3a:

- "verify/ sub-package exists with §3a layout; `__init__.py` declares `__all__`" → matches §3a.1 layout block.
- "test_verify.py covers every R-tag per §3a.6 negative-case table (≥ 20 cases + 1 audit-block-mismatch = ≥ 21 total)" → matches §3a.6 L252–255 totals (20 + 1).
- "`saas_cohort1_audit.py` adds the `Audit` frozen-dataclass; `json_io.py` adds `AuditReader`" → matches §3a.4 precondition L178–185.
- "`CommittedArtifactLoader.__init__` rehashes every committed JSON … raises `AuditBlockMismatch`" → matches §3a.4.1 L208–222.
- "Every `RTagVerdict.audit_sha256` (including R1–R4 sympy-only) carries the trio-level anchor; the field is non-Optional" → matches §3a.2 L108 ("`audit_sha256: str` … NOT Optional") and L118–122 narrative.
- "Notebook code cells contain no direct parquet/JSON file reads" → matches §3a.5 cell shape.
- "Notebook code cells import only from `simulations.saas_builder.verify` and `env.py`" → matches §3a's centralization claim.

All §9 v0.3 additions are backed by concrete §3a content. No success-criterion floats free of body text.

### CORRECTIONS-α v0.2→v0.3 citation audit

Each of the 8 patches in CORRECTIONS-α (design L444–480) cites its origin verdict line:

1. RC-BLOCK-1, MQ-F1 — cites rc-verdict L34, L37–70; mq-verdict L163–195. ✓ (rc-verdict L34 is the BLOCK-1 audit row; L37–70 is the BLOCKs section.)
2. MQ-F2 — cites mq-verdict L79–96, L217–223. ✓ (matches MQ tamper-detection section + F2 flag body.)
3. RC-FLAG-3, MQ-F3 — cites rc-verdict L96–105 (RC FLAG-3 body); mq-verdict L225–229 (F3 body). ✓
4. MQ-F4 — cites mq-verdict L231–235. ✓
5. MQ-F5 — cites mq-verdict L237–241. ✓
6. MQ-F6 — cites mq-verdict L243–246. ✓
7. RC-FLAG-1 — cites rc-verdict L33 (FLAG-1 audit row), L74–81 (FLAG-1 body). ✓
8. RC-FLAG-2 — cites rc-verdict L83–94 (FLAG-2 body). ✓

All citations land on the correct verdict-file line ranges. F1+RC-BLOCK-1 dedup and F3+RC-FLAG-3 dedup are correctly noted in design header L7. The "8 distinct fixes after dedup" arithmetic (1 RC BLOCK + 3 RC FLAGs + 6 MQ FLAGs = 10; minus 2 dedups = 8) checks out.

### CORRECTIONS-α v0.1→v0.2 preservation

Design L499–526 contains the v0.1→v0.2 CORRECTIONS block verbatim from v0.2 (matches the structure summarized in Wave-1 audit table row 10). Posture statements ("strictly tightening", "math content unchanged", "R1–R8 set unchanged") are unchanged. History preserved.

## New BLOCKs introduced by v0.3

None.

## New FLAGs introduced by v0.3

None of consequence. One observational note (NOT a FLAG, NOT blocking):

- §3a.4 L172 footnote on `load_posterior_chain` lists "n/a — numpy primitive" for the "Defined at" column. Strictly the chain trace lives somewhere on disk under `simulations/saas_builder/data/synthetic_tau_t/` (the directory exists per Wave-1 evidence). The "Defined at" column is talking about the *return type* (a numpy array, which is a primitive, hence n/a), not the artifact. The phrasing is fine read in context. Logged for the writing-plan author's awareness only.

## Evidence

```
$ ls simulations/utils/audit_block.py
simulations/utils/audit_block.py            # AuditBlockHasher source — citation correct

$ grep -n "class AuditBlockHasher" simulations/utils/audit_block.py
71:class AuditBlockHasher:                   # class exists; raises AuditBlockMismatch downstream

$ ls simulations/types/saas_cohort1_audit.py
ls: cannot access … : No such file or directory
                                             # correctly flagged as Phase-0 precondition,
                                             # not falsely claimed to exist
```

```
$ grep -n "matches spec §5.2 verbatim" docs/specs/2026-05-09-simulations-notebooks-saas-builder-stage-2-design.md
# (zero matches — RC-FLAG-1 string excised)

$ grep -n "posterior_path" docs/specs/2026-05-09-simulations-notebooks-saas-builder-stage-2-design.md
# only one match, on L146, in the explanatory note documenting the
# v0.2→v0.3 fix. The active R5 input row (L138) reads
# "posterior_chain: np.ndarray". RC-FLAG-3 / MQ-F3 fully closed.

$ grep -n "AuditBlockHasher\|AuditBlockMismatch" docs/specs/…design.md
211: simulations.utils.audit_block.AuditBlockHasher performs the rehash
221: AuditBlockMismatch
                                             # rehash-and-assert pinned;
                                             # raise behavior documented;
                                             # RC-FLAG-2 closed
```

---

**Recommendation to orchestrator.** v0.3 ACCEPT. All four Wave-1 RC
items resolved, no regressions, CORRECTIONS-α citations land on the
correct lines, history preserved. The Phase-0 precondition (add
`Audit` Value + `AuditReader`) is the only cross-tier addition the
writing-plan must schedule before notebook authoring. Cleared for
writing-plans hand-off.
