---
name: project-substrate-decision-lineage
description: Cost-data substrate decisions v0.1.0 → v0.2.3 — why ccusage and claude-parser were rejected, why own-parser stays, what v0.2.2/v0.2.3 changed
metadata:
  type: project
---

**Decision chain**:

| Version | Substrate | Verdict | Reason |
|---------|-----------|---------|--------|
| v0.1.0  | Wrap `ccusage` CLI            | **REJECTED** | Session aggregates only; no per-message granularity |
| v0.2.0  | `claude-parser` Python lib    | **REJECTED** | Schema lacks `usage`/cache fields we need |
| v0.2.1  | Own parser (~150 LoC) per CORRECTIONS-N | **IN USE** | Direct JSONL read; contracts patched in v0.2.2/v0.2.3 |

**v0.2.2 spec amendments (OSS algorithm study informed)**:
- **Type-discriminate FIRST** before any field validation (the 9 `type` values in real Claude Code JSONL, see [[reference-claude-code-jsonl-schema-permissive]])
- **`extra="allow"`** on Pydantic models (not `forbid`) — real `message.usage` has 6 unmodeled fields
- **Cost computed at parse time** as `Σ_cat tokens_cat × rate_cat`, NOT read from JSONL `costUSD` field (which is absent from 100% of real assistant rows)
- **Ephemeral 5m/1h cache windows** preserved on `MessageRecord` for diagnostics but aggregated for cost
- **LiteLLM rates Optional** with per-model gating (some model × cache-cat cells have no published rate)

**v0.2.3 architectural pins** (added to clear final RC fence-sitters):
- **Alphabetical-min tiebreaker** when multiple models match a parse (deterministic, reviewable)
- **uuid synthesis rule**: `synth-sha256:` + `sha256(file_basename + ":" + line_no_zfill_8)` when JSONL `uuid` absent
- **WARN_missing_keys_count owned by `PricingTable`** (not parser) — single source of truth for rate-gap telemetry

**Parity oracle**: `ccusage` against a real `.jsonl` fixture; match within **0.1%** per Y-4.

**LiteLLM pin**: SHA `e58a561caa21169fb02174148444c08509ce7028`.

**Why this note**: every future debate about "should we just use ccusage?" or "why does cost come from rates × tokens instead of the JSONL field?" has already happened across three rejected/superseded versions. The lineage prevents redoing the rejection.

**Links**: [[project-ai-cost-v0-2-3-state]] · [[reference-claude-code-jsonl-schema-permissive]] · [[reference-r6-sibling-amendments-to-v0-2-1]]
