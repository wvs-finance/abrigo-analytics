---
name: agents-clean-pytest-artifacts
description: Subagents (especially long-running implementer/reviewer agents) must periodically clean pytest output artifacts that can otherwise accumulate and exhaust disk/memory
metadata:
  type: feedback
---

Subagents running long implementation+test cycles must periodically clean
pytest output artifacts to prevent disk/memory accumulation. This is a
standing instruction the orchestrator MUST embed in every dispatched
agent's brief that touches code or runs tests.

**Why:** Hypothesis property tests, mutation testing, and repeated
pytest runs accumulate large artifact trees that compound across
dispatches. After 5-10 agent cycles in a long session, the
working-directory artifact footprint can reach multi-GB and slow
disk operations, file watchers, and `git status`. The user has
observed this concretely: pytest run-trees + Hypothesis databases +
ruff/mypy/ty caches + mutation-testing artifacts grow monotonically
across agent invocations on the same project.

**How to apply:** Each dispatched-agent brief that runs pytest, ruff,
ty, mypy, mutmut, or Hypothesis tests MUST include a cleanup step at
the END of the agent's task (post-commit, before the report-back).
Cleanup targets (all already in `.gitignore` per the repo convention):

- `.pytest_cache/`
- `.hypothesis/`
- `.ruff_cache/`
- `.mypy_cache/`
- `.coverage`
- `__pycache__/` (recursive — `find . -type d -name __pycache__ -exec rm -rf {} +` 2>/dev/null)
- `.mutmut-cache/` + `mutants/` (if mutation testing was run)
- `.ipynb_checkpoints/` (if any notebook was touched)
- Test-generated emission outputs under `simulations/*/data/`
  (gitignored, but can grow per run — clean only if the test
  generated them transiently, not if Task 5 emit.py produced them
  as expected exit artefacts)

The cleanup is NEVER `rm -rf .`-style; it's targeted to the listed
patterns. The cleanup must NOT touch git-tracked files or
`scratch/` content (which is research artefact, intentionally kept).

Cleanup pattern (drop into agent briefs):

```
After tests pass and the commit lands, clean transient pytest
artifacts to prevent multi-GB accumulation across the session:
  find . -type d \( -name __pycache__ -o -name .pytest_cache \
                    -o -name .hypothesis -o -name .ruff_cache \
                    -o -name .mypy_cache -o -name .ipynb_checkpoints \) \
       -not -path './.venv/*' -exec rm -rf {} + 2>/dev/null || true
  rm -f .coverage
Report disk-freed via `du -sh .` before/after if cleanup was substantive.
```

The orchestrator should also run this cleanup at the END of each major
review cycle (after both Wave-1 reviewers + dispositions) to keep the
working tree lean for the next dispatch.

Related: [[feedback_three_way_review]] for review-cycle structure;
[[project_compact_survival_2026_04_28]] for context-window-management
patterns that interact with disk-state size.
