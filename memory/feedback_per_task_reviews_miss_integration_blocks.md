---
name: feedback-per-task-reviews-miss-integration-blocks
description: Tasks 1–8 each passed per-task spec+code review on synthetic fixtures yet the whole pipeline could not parse any real Claude Code JSONL — synthetic fixtures built to match spec claims hide cases where the spec is wrong about reality; integration-test floor on real fixture required before impl-review fires
metadata:
  type: feedback
---

**Observed failure mode** (iter/ai-cost-2026-05, Task 9 impl-review):

Tasks 1–8 of the AI-cost-factor-model plan each passed both **spec-compliance review** and **code-quality review**, working off synthetic JSONL fixtures hand-crafted to match the v0.2.1 spec's schema claims. All eight commits landed clean.

At Task 9 the 3-way impl-review fired (Code Reviewer + Reality Checker + Backend Architect) — Reality Checker ran the pipeline against a real `~/.claude/projects/*.jsonl` and the entire system **failed to parse a single message**. Root cause: every synthetic fixture had been written to validate the spec's contracts (`extra="forbid"`, costUSD field present, single canonical `type` value), and the spec's contracts were wrong about external reality. See [[reference-claude-code-jsonl-schema-permissive]] for the schema gap.

**Why this is structural** (not a one-off oversight):

When the same artifact (the spec) is the source of both (a) the implementation contracts AND (b) the test-fixture shapes, per-task reviews are tautological — they verify the code matches itself. No amount of additional per-task review catches this; only an external-reality probe does. The 8 clean reviews give false confidence that the cumulative system works.

**How to apply** — formalized as **CORRECTIONS-Y-4**:

1. **Any external-data-ingest spec MUST declare an integration-test floor** using a **real fixture** (not synthetic, not hand-crafted to match the spec) BEFORE per-task reviews start. The fixture is checked into the repo or pinned by hash.
2. **The integration test runs at the earliest task that touches the ingest path**, not at impl-review time. If the earliest task can't yet produce output, the integration test asserts only "parses without raising"; richer assertions are added as later tasks land.
3. **Parity oracle, when available, is part of the integration floor**. For AI-cost this is `ccusage` matched within 0.1% per Y-4 — see [[project-substrate-decision-lineage]].
4. **The 3-way impl-review checkpoint stays** but its job becomes "verify the integration floor was honored", not "first contact with reality".
5. **Generalize**: any spec that mentions "external JSONL / API response / on-chain log / CSV from vendor" triggers this rule. Synthetic fixtures are allowed only AFTER a real fixture has been parsed end-to-end.

**Why this note**: the temptation to skip the real-fixture step is high (real data is messy, fixtures are tidy). The 8-clean-reviews-then-everything-broke pattern is the only counter-evidence strong enough to make the rule stick.

**Links**: [[project-ai-cost-v0-2-3-state]] · [[reference-claude-code-jsonl-schema-permissive]] · [[project-substrate-decision-lineage]] · [[feedback-real-data-over-mocks]] · [[feedback-three-way-review]] · [[feedback-implementation-review-agents]]
