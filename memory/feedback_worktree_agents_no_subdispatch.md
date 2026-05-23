---
name: Worktree-isolated agents lack Agent/Task tools
description: Agents dispatched with isolation="worktree" cannot dispatch sub-agents. Long multi-phase plans with strategic-delegation maps must be orchestrated from the main session, not delegated to a worktree agent.
type: feedback
---

When dispatching long multi-phase implementation plans (5+ phases, each with strategic-delegation map naming specialized sub-agents per task), the plan execution **must be orchestrated from the main session**, not delegated to a single agent running in `isolation="worktree"`.

**Why:** Worktree-isolated agents do NOT have access to the `Agent` or `Task*` tools. Per the SaaS-Builder Stage-2 iteration (May 2026), two parallel attempts to dispatch full cohort plans (C1 + C3) via worktree agents resulted in:

- C3 worktree agent: HALTED at "Task 0.5 equivalent" (registry check), correctly reporting that "subagent dispatch infrastructure (Task tool, TodoWrite, agent registry resolver for `engineering-ai-engineer` / `specialized-reality-checker` / etc.) is not exposed by this Claude Code harness." 0 phases executed.
- C1 worktree agent: completed end-to-end **but** disclosed an "execution-mode deviation" — performed all roles (RC + MQ + CR + AI Engineer) in-band as foreground because sub-agent dispatch was unavailable. This produced same-agent-grading-own-work, which independent audit subsequently rejected with 12+ BLOCKs.

**How to apply:**

- For implementation plans whose strategic-delegation map names specialized agents per phase, dispatch each phase from the **main session** as a separate `Agent` call. The main session has Agent + Task tools and can route per-phase to AI Engineer / Reality Checker / Model QA Specialist / etc.
- Reserve `isolation="worktree"` for **single-phase, single-agent** tasks (e.g., a focused refactor that doesn't need sub-dispatches). Even then, prefer running in the main worktree if the change touches files multiple downstream agents may need to read.
- Long-running implementation phases that need sub-agent verifies should: (a) dispatch the implementer as one `Agent` call; (b) on completion, dispatch the independent verifies as separate `Agent` calls; (c) gate downstream work on the verifies' verdicts.
- The pattern that consistently worked for SaaS-Builder Stage-2 was: single AI Engineer per phase (consolidated implementation) + independent RC + MQ + CR per phase (consolidated audit). Subagent-driven-development pattern (one sub-agent per task within a phase) fails on the worktree-no-subdispatch constraint.

This is a Claude Code harness invariant as of 2026-05-08; if the platform changes (e.g., worktrees gain Agent dispatch), this memory may relax.
