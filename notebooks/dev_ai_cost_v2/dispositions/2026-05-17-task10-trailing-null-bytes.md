# Task 10 HALT Disposition — Trailing-Null-Byte JSONL Corruption

**Date:** 2026-05-17
**Trigger:** First production run of `scripts/build_notional_cost_panel.py --since 2024-01-01 --until 2026-05-17` raised `JSONLSchemaError` on real `~/.claude/projects/` data.

## What happened

```
JSONLSchemaError: /home/jmsbpp/.claude/projects/-home-jmsbpp-apps-d2p-frontend/9253ad77-30cb-4f6d-b061-a0b1505d8a14/subagents/agent-af5e1160f7be358ba.jsonl:586 invalid JSON: Expecting value: line 1 column 1 (char 0)
```

File inspection:
- 585 valid JSONL lines (last valid line ends with `}` + newline + EOF marker as expected).
- Bytes after the final newline of line 585 are ~3 KB of literal `\0` (null bytes).
- Hypothesis: partial-write filesystem corruption (block allocated, written with valid JSON for the prefix, then a crash/SIGKILL left the suffix zero-filled).
- This is **not** a malformed JSON line in the application sense; it is filesystem-level garbage that the parser sees as a single "line" `"\0\0\0..."` because `\n` is absent in the null fill.

## Why our parser raises here

`simulations/dev_ai_cost_v2/jsonl_io.py` lines 274–283:

```python
for line_no, line in enumerate(f, start=1):
    stripped = line.strip()
    if not stripped:
        continue
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError as e:
        raise JSONLSchemaError(...) from e
```

`str.strip()` removes ASCII whitespace (`\t\n\r\v\f\ `) but **not** `\x00`. So a `"\0\0\0..."` line passes the blank-line check, fails `json.loads`, and raises.

## Why spec v0.2.3 doesn't already cover this

- CORRECTIONS-Y-1 (§0.3) describes "permissive parse" *only* in terms of Pydantic `extra="allow"` on **valid** JSON.
- The OSS algorithm study (`scratch/2026-05-16-ai-cost-impl-review/oss_algorithm_study.md`) found that ccusage handles malformed lines via `try { JSON.parse(line) } catch { continue }`. Our spec amendment inherited the schema-permissive half of this discipline but not the **line-level malformed-skip** half.
- Result: a v0.2.3 spec gap that the synthetic fixture in `simulations/tests/fixtures/real_claude_jsonl/synthetic_sample.jsonl` did not exercise (all 9 synthetic lines are well-formed JSON).

## Anti-fishing classification

This is a **spec-vs-data contradiction**, not a methodology shift. Per `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`:

> HALT + disposition memo + user-enumerated pivot + CORRECTIONS block + post-hoc 3-way review whenever spec contradicts data.

No iteration parameters change (R5 / R4-S3 framework intact, N_MIN floor intact, MDES intact). Only the IO Boundary contract for `JSONLReader` needs the additional line-level robustness rule.

## Pre-enumerated user pivots

### Option A: Strict mirror of ccusage (silent skip + counter)
**Patch surface:** v0.2.4 contract-only spec patch + `jsonl_io.py` 5-line change.

Add to `JSONLReader.__call__`:
```python
except json.JSONDecodeError:
    dropped_malformed_line += 1
    continue
```

Add to `JSONLReadResult`:
```python
dropped_malformed_line_count: int
```

Thread through panel builder + CLI emission like the existing 5 counters.

**Why:** matches ccusage exactly per OSS algorithm study. Permissive parsing is the documented OSS norm. Filesystem corruption is genuinely outside the producer's contract (Claude Code itself didn't emit those null bytes — the kernel did) so silently skipping is operationally correct.

**Cost:** small v0.2.4 patch + 2-wave review (Reality Checker + Code Reviewer) + 3 new tests (skip-on-null-block, skip-on-truncated-json, counter-increments).

**Risk:** masks genuine producer-side schema regressions. Mitigated by the counter surfacing the count so the operator sees it.

### Option B: Strict-skip with byte-class discrimination
**Patch surface:** larger — discriminate by line content (null-only / whitespace-only / has-printables-but-malformed).

```python
if not stripped or stripped.strip("\x00") == "":
    continue                              # silently skip null/blank blocks
try:
    raw = json.loads(stripped)
except json.JSONDecodeError:
    raise JSONLSchemaError(...) from e    # still raise on truly malformed
```

**Why:** distinguishes filesystem corruption (silent) from producer-side JSON bugs (HALT).

**Cost:** larger patch + more test surface + spec amendment is more substantive than Option A.

**Risk:** the heuristic (null-block == filesystem corruption) may not generalize (could there be partial JSON writes that look like `{"foo`?). Empirically Option A is what ccusage uses and ccusage handles 1000s of users' logs in production.

### Option C: Preprocess + strict parse unchanged
**Patch surface:** new helper `scripts/repair_jsonl.py` that runs over the projects-root pre-build and rewrites files with trailing-null-byte truncation removed; parser stays strict.

**Why:** keeps the parser invariant tight; quarantines repair logic in a separate script.

**Cost:** new script + concerns about modifying source-of-truth `~/.claude/projects/` files (operator may not want this).

**Risk:** mutates external user data; reversibility concerns.

## Recommendation (implementer view, awaiting user)

**Option A**, because:
1. It is the empirically-validated OSS norm (ccusage runs at much larger scale and handles this exact case identically).
2. The OSS algorithm study already established that we should mirror ccusage; this is closing a gap in our v0.2.3 mirror, not a methodology change.
3. The added counter (`dropped_malformed_line_count`) preserves observability — if it spikes, the operator sees a signal and can investigate.
4. It does not mutate the operator's source-of-truth `~/.claude/projects/` files.
5. Smallest patch + cleanest contract.

## HALT routing chain (per `feedback_pathological_halt_anti_fishing_checkpoint.md`)

1. [x] HALT fired + this disposition memo drafted (2026-05-17)
2. [ ] User pivot selected: ____
3. [ ] CORRECTIONS-Y-7 (or v0.2.4 §0.4) block added to spec
4. [ ] 2-wave review on the amendment (Reality Checker + Code Reviewer)
5. [ ] Implementation + new tests
6. [ ] Re-run Task 10 from Step 10.2
7. [ ] Post-hoc 3-way impl-review (per established v0.2.2/v0.2.3 protocol)

## Status

- [x] HALT fired (date: 2026-05-17)
- [x] User pivot selected: **Option A — ccusage-mirror (silent skip + counter)**
- [x] Disposition committed
- [x] Spec amendment landed (v0.2.4 CORRECTIONS-Y-7; commit `b8a1982`)
- [x] 2-wave amendment review: CR APPROVE_WITH_NITS + RC CONDITIONAL_APPROVE → all MUST/SHOULD fixes folded inline
- [x] Implementation landed (commits `134cbcb` + `07f907f`); 855/855 tests green
- [x] Post-hoc impl-review: CR APPROVE_WITH_NITS + RC APPROVE — HALT chain closed
- [x] Re-run Task 10 — production CLI cleared; 29-row panel emitted; DATA_PROVENANCE committed
