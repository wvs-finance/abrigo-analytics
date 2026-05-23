---
name: feedback-peer-agent-branch-interference
description: A claude-peers instance on another iteration can flip branches and reset HEAD on a long-running plan-execution worktree; check list_peers at start and isolate via worktree if any peer is active
metadata:
  type: feedback
---

**Observed incident** (iter/ai-cost-2026-05, Task 1 execution):

A second Claude Code instance — running on stochastic_fx work in the same repo — flipped branches mid-Task-1 on this worktree and executed `git reset` moving HEAD to `d1cba73`. The Task 1 commit `cba9c67` was orphaned. Recovery succeeded only because `git reflog` still held the dangling object; cherry-pick produced the recovered commit `e3a766e`.

**Why this is invisible by default**: subagent-driven-development workflows assume the worktree is single-tenant. The claude-peers MCP server makes the assumption false — any peer running in the same repo can issue arbitrary git commands. Long plan-execution sessions with sequential commits are the highest-risk surface because each task commit becomes a candidate for accidental reset by a peer working on a sibling iteration.

**How to apply**:

1. **At plan-execution start**, call `mcp__claude-peers__list_peers --scope repo` (or `--scope machine`). Document the peer landscape in the dispatch brief (peer ids, their `set_summary` strings, their `cwd`).
2. **If any peer is active in the same repo**: either (a) HALT and coordinate via `send_message` before dispatching plan tasks, or (b) move work to an isolated `git worktree add` directory whose path no peer is touching.
3. **Call `set_summary` proactively** at session start so other peers can see your branch and current task; this is the symmetric obligation that makes (1) work.
4. **If interference is detected post-hoc**: `git reflog` is the only recovery surface — dangling objects expire after gc, so investigate immediately. Cherry-pick the orphan onto the intended branch; document the new commit hash in the project state note.
5. **Pattern observed in**: orphan `cba9c67` → recovered as `e3a766e`; see [[project-ai-cost-v0-2-3-state]] for the execution-ledger correction.

**Related**: companion to [[project-concurrent-agent-filesystem-interleaving]] but distinct — that note covers in-session parallel subagents writing to overlapping files; this note covers **cross-instance peer agents** issuing git commands that mutate refs.

**Links**: [[project-ai-cost-v0-2-3-state]] · [[project-concurrent-agent-filesystem-interleaving]] · [[feedback-no-parallel-agents-same-dir]]
