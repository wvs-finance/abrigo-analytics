---
name: reference-claude-code-jsonl-schema-permissive
description: Empirical schema notes on real Claude Code v2.1.x JSONL — 9 type values (only assistant carries usage), costUSD absent from 100% of real assistant rows, 6 extra fields in message.usage, LiteLLM cache-rate gaps for sonnet-4-5/4-6
metadata:
  type: reference
---

**Observed against 5 real `~/.claude/projects/*.jsonl` sessions** (v2.1.x, 355 assistant rows surveyed):

**1. `type` field has 9 distinct values**:
`assistant`, `user`, `summary`, `system`, plus 5 others. **Only `assistant` rows carry token usage.** All other types must type-discriminate to a no-op for the cost pipeline — they are not errors, they are legitimate JSONL content.

**2. `costUSD` field is ABSENT from 0/355 real assistant rows.**
v0.2.1's design assumed this field would be present and authoritative. It is not present at all. **Cost MUST be computed at parse time** as `Σ_cat tokens_cat × rate_cat`. See [[project-substrate-decision-lineage]] for the v0.2.2 amendment that codified this.

**3. `message.usage` has 6 unmodeled fields** beyond what v0.2.1's `extra="forbid"` schema allowed:
- `cache_creation_input_tokens` (flat field, distinct from the nested cache_creation breakdown)
- `inference_geo`
- `iterations`
- `server_tool_use`
- `service_tier`
- `speed`

v0.2.2 patch: **`extra="allow"`** on Pydantic models. `extra="forbid"` is unusable against this surface.

**4. LiteLLM rate-table gaps** (at pinned SHA `e58a561caa21169fb02174148444c08509ce7028`):
**6 of 21 claude-* models** lack a published `cache_creation_input_token_cost_above_1hr` rate, including `claude-sonnet-4-5` and `claude-sonnet-4-6` — **the two most-used production models**. Per-model × per-cache-category rate gating with `Optional[float]` is the only viable contract; missing-rate cells must surface as `WARN_missing_keys_count` (owned by `PricingTable` per v0.2.3) rather than parse failures.

**5. Cross-tool corroboration**: all four OSS Claude Code cost tools surveyed (`ccusage`, `cc-lens`, `agentsview`, `claude-parser`) implement permissive parsing + per-model rate gating. **No tool in the OSS ecosystem uses strict schema validation against Claude Code JSONL.** This is structural to the format, not an implementation choice.

**Why this note**: every "but the spec says costUSD should be there" or "why don't we use extra=forbid for safety" debate dies here. The numbers (0/355, 6/21, 9 types) are the substrate; future contract changes must reconcile with them.

**Links**: [[project-substrate-decision-lineage]] · [[project-ai-cost-v0-2-3-state]] · [[feedback-per-task-reviews-miss-integration-blocks]] · [[reference-r6-sibling-amendments-to-v0-2-1]]
