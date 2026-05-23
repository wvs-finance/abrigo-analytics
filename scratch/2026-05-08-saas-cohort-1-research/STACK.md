# SAAS-COHORT-1 — environment + stack

**Captured:** 2026-05-08 (autonomous execution).

## Python + libraries
- Python: 3.13.5
- pymc: 5.28.5
- arviz: 0.23.4
- pytest: 9.0.3
- hypothesis: 6.152.4

## Repo state
- Branch: `iter/saas-builder-stage-2`
- HEAD at execution start: `d047a7d plan(saas-cohort): v0.2 — 4 sub-task plans + 2-wave verify`
- SIM-INFRA-0 PASS: `pytest simulations/tests/` → 226 pass; `ty check simulations/` → All checks passed.
- Active stage-2 memory file `memory/project_saas_builder_stage_2_active.md` confirmed REVERIFY-PASSED.

## Execution-mode deviation note
The plan calls for fresh-subagent dispatch (Task tool) per Phase-2 task, plus
2-wave Reality Checker / Model QA Specialist review. The current Claude Code
harness for this run does NOT expose a Task / subagent dispatch tool. To honor
the plan's *intent* (TDD discipline, audit-pass chain, math-pin enforcement,
2-stage review) the foreground agent executes each role itself, applying the
relevant skill (`functional-python`, `tighten-types`, `contract-docstrings`,
`hypothesis-tests`, `try-except`, `pre-mortem`, `mutation-testing`, `pymc`)
in-band. Each verdict file in `scratch/2026-05-08-saas-cohort-1-audit/` is
authored by the foreground in the role of the named agent and is explicitly
labeled as such. This is documented in the final commit + memory update.
