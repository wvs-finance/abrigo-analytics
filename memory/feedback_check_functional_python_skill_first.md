---
name: Re-read functional-python skill from disk before code-touching
description: User has a project-modified version of the functional-python skill at ~/.claude/skills/functional-python/SKILL.md; re-read from disk via Read tool before any code-touching task because the file changes
type: feedback
---

**Rule.** Before any Python code-touching work in this repo (writing, refactoring, reviewing, or planning code), re-read `~/.claude/skills/functional-python/SKILL.md` directly via the Read tool. Do not rely on memory of an earlier load.

**Why.** The user maintains a *modified* version of the functional-python skill on disk that differs from the upstream/general distribution. They have explicitly updated it during conversations and may continue to do so (mid-fix as of 2026-05-07). Working from a stale loaded copy in conversation context risks committing code or plans that violate the *current* discipline.

The current discipline (as of 2026-05-07) is: three-tier type hierarchy (Value = `@dataclass(frozen=True)`; Callable = `@dataclass(frozen=True)` + `__call__`; IO Boundary = class with `__init__`); no inheritance except `Protocol`; comprehensions over append loops; lazy when natural; full typing strictness (no bare `Any`, `TypeAlias` for domain types, `Final` for constants, `Generic[T]`, `Literal` over string enums). But the *concrete rules* may evolve.

**How to apply.**
- At the start of any task that involves writing or reviewing Python code, run the Read tool on `/home/jmsbpp/.claude/skills/functional-python/SKILL.md` to confirm current state.
- When writing implementation plans (TODO-COHORT-N specs, sub-task plans, etc.), include "re-read functional-python SKILL.md" as the first step under any code-touching task.
- If user says the skill has been "modified" or "updated" or "is being fixed," do NOT proceed with code-touching work that depends on it. Pause and either wait for user signal or ask if the current on-disk version is canonical.
- Confirm via on-disk file mtime + content if uncertain about whether a recent load reflects current state.

**Cross-reference.** The Skill tool (`Skill: functional-python`) loads the skill content into context, but the disk file is the source of truth. Direct Read is preferred when re-checking after a modification claim.
