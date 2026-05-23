# v0.2.5 Dedup Discovery — Empirical Validation

**Date**: 2026-05-17

## Root cause confirmed

Our `JSONLReader` does NOT deduplicate within or across files. **ccusage dedupes by `${message.id}:${requestId}`** (function `Wr` in ccusage `data-loader-LJFbLyZj.js`), keeping the entry with the largest `tokenTotal = input + output + cc + cr` (function `Sr` + `$`).

Claude Code logs the same Anthropic message multiple times (streaming chunks + per-iteration entries). Each chunk has its own `usage.input_tokens` etc. ccusage keeps only ONE per `uniqueHash`. We sum all.

## Test session uniqueHash analysis
`/-home-jmsbpp-apps-d2p-frontend/9253ad77-30cb-4f6d-b061-a0b1505d8a14/`

| Source | Assistant rows | Unique `${message.id}:${requestId}` | Dedup factor |
|---|---|---|---|
| Main session file | 1,079 | 551 | 1.96× |
| 41 subagent files (∪) | 5,387 | 3,085 | 1.75× |
| Main ∩ Subagents | 0 (disjoint) | — | — |
| Total | 6,466 | 3,636 | 1.78× |

## Production-wide convergence (43,083 dedup'd entries vs 87,031 raw assistant rows)

| Metric | Ours (no dedup) | Ours (dedup) | ccusage | Dedup ratio |
|---|---|---|---|---|
| Cost ($) | 5,903.87 (on overlap) | 5,037.52 | 5,155.80 | 0.977 (was 2.11) |
| Output tokens | (overcounted) | 31,948,616 | 32,636,241 | 0.979 |
| cache_create tokens | (overcounted) | 251,742,697 | 257,525,627 | 0.978 |
| cache_read tokens | (overcounted) | 5,784,749,501 | 5,914,273,827 | 0.978 |
| **input_tokens** | (overcounted) | **1,226,928** | **12,086,794** | **0.10** ← anomaly |

## Residual gaps to investigate post-v0.2.5

1. **Input-token 10× shortfall** (Y-8 candidate). Post-dedup output/cc/cr all converge to ~0.978× of ccusage; input is 0.10× — that's not a uniform offset. Hypothesis: ccusage may aggregate `iterations[i].input_tokens` across the `usage.iterations` array, while we read only top-level `usage.input_tokens`. Needs probing of a specific message with multi-iteration.

2. **Residual 2.3% gap on cost/output/cc/cr** (Y-9 candidate). Possibly explained by: (a) `dropped_unknown_model_count=136` rows (we drop, ccusage might fallback-price), (b) the `hasSpeed` tiebreaker we ignore, (c) the 6 missing `cache_creation_input_token_cost_above_1hr` keys (we treat ephemeral 1h as 5m; ccusage matches the same fallback per OSS study so this should not be a divergence — confirm).

3. **The 5,387 subagent vs 1,079 main session rows** structure: confirmed ccusage reads both (no glob filter on `subagents/`). Inclusion is correct; dedup is the discipline.

## Spec amendment needed: v0.2.5 §0.5 CORRECTIONS-Y-8

- Add `_unique_hash(msg_id, request_id) -> str | None` helper in `jsonl_io.py`.
- Add `seen_hashes: dict[str, int]` (hash → index of kept entry) to `JSONLReader.__call__`.
- On parse: compute uniqueHash; if seen and new tokenTotal > existing → replace; else if first-seen → keep; else → skip + increment `dropped_duplicate_count`.
- Add counter `dropped_duplicate_count: int` on `JSONLReadResult`.
- Thread through panel + CLI per existing counter-threading discipline.
- Test surface: same 5 OSS-mirror pins + Hypothesis property "result is invariant under file-traversal-order permutation".

## Status

- [x] Hypothesis formed (2026-05-17)
- [x] Empirically validated (dedup → cost converges from 2.11× to 0.977×)
- [ ] v0.2.5 spec amendment drafted
- [ ] 2-wave review
- [ ] Implementation
- [ ] Re-run Task 10
- [ ] Post-hoc 3-way review
