---
name: reference-r6-sibling-amendments-to-v0-2-1
description: Concrete contract patches landed in AI-cost Tasks 2 + 4 — DevAICostError sub-package root (Task 2 aef0f5d), MessageRecord.uuid:str + v0.2.3 synth-sha256 prefix (Task 4 a70ed58)
metadata:
  type: reference
---

**Two contract patches** that R6 (continuous-stream-simulation sibling spec) and AI-cost spec converged on during v0.2.1 plan execution. Both are committed and ride forward into v0.2.3.

**Patch 1 — `DevAICostError(Exception)` as sub-package root** (Task 2, commit `aef0f5d`):

- Module: `_errors.py` at the sub-package root
- Pattern: single root exception type that all sub-package errors inherit from
- Multi-inheritance case: `JSONLSchemaError(DevAICostError, SchemaMismatchError)` — preserves the sub-package root hierarchy AND the existing project-wide `SchemaMismatchError` taxonomy
- Why: lets callers catch `except DevAICostError` to scope-handle anything from this sub-package without coupling to specific error subclasses; the multi-inheritance preserves cross-cutting taxonomies (schema, IO, validation) that exist project-wide

**Patch 2 — `MessageRecord.uuid: str`** (Task 4, commit `a70ed58`):

- v0.2.1 origin: CORRECTIONS-RR / -TT added the field as required string
- **v0.2.3 amendment**: support `synth-sha256:` prefix synthesis when JSONL `uuid` field is absent
  - Synthesis rule: `synth-sha256:` + `sha256(file_basename + ":" + line_no_zfill_8).hexdigest()`
  - Deterministic (same file + line always produces same uuid)
  - Self-identifying via prefix (downstream consumers can distinguish JSONL-native uuids from synthesized ones)
- Why: real Claude Code JSONL is permissive about `uuid` presence (see [[reference-claude-code-jsonl-schema-permissive]]); strict-required without synthesis fallback would force parse failures on real data; synthesis with a verifiable prefix preserves the per-message identity invariant downstream simulation code depends on

**Why this note**: the two patches are the only places in v0.2.1 plan execution where R6 and AI-cost specs share a concrete contract surface. When Task 9.5 migration (8 files) lands, both patches must be carried through identically to maintain sibling-spec parity. Future R6 work that touches errors/identity must reference these commits.

**Links**: [[project-ai-cost-v0-2-3-state]] · [[project-substrate-decision-lineage]] · [[reference-claude-code-jsonl-schema-permissive]]
