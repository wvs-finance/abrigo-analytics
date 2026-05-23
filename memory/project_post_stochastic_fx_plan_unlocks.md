---
name: post-stochastic-fx-plan-unlocks
description: Two deliverables unlocked by completion of the stochastic-FX plan (Tasks 0-7); final-simulation notebook is written by Analytics Reporter; LaTeX paper references it
metadata:
  type: project
---

Completion of `docs/plans/2026-05-11-stochastic-fx-variant.md` (Tasks 0-7
+ Wave-2 §16.8 review) unlocks **two parallel deliverables**, plus a
shared notebook artefact, per user reminder 2026-05-13:

1. **cadCAD integration** of the dynamic system across BOTH the
   deterministic models (cohort_5_strip + earlier Stage-2 cohorts) AND
   the stochastic-fx three-SDE-family work. Per the earlier
   user-disposition (2026-05-13 via AskUserQuestion): **doc-first
   sequencing** — build the LaTeX-econ design spec FIRST, then
   implement the cadCAD code. Mirrors the design → spec → plan →
   implement convention used for stochastic-fx.

2. **LaTeX-econ-model working paper draft** — math-paper writeup of
   the ENTIRE body of work to date (deterministic + stochastic-fx +
   cadCAD integration). Invoked via the `/latex-econ-model` skill at
   `~/.claude/skills/latex-econ-model/SKILL.md`. Audience: working
   paper / academic; per the earlier disposition. Lives at
   `docs/papers/` or similar (NOT `docs/supervisor-review/` per the
   user's earlier choice between three audience options).

**Shared artefact — the final-simulation notebook.** The numerical
results, graphs, and math-formula rendering that anchor the LaTeX
paper live in a **Jupyter notebook written by the Analytics Reporter
agent**. The notebook holds:
- Reproducible computation (re-runs the canonical-pin verifier per
  family; emits the parquet/JSON/MD artefacts).
- Publication-quality figures (using `econ-visualization` and/or
  `graph` skills; sample paths per family, σ_T cross-section,
  KS-reference overlays, Phase B/C diagnostic plots).
- LaTeX-renderable math expressions (the σ_T eq.(7) form, the
  per-family E[σ_T] hand-derived closed forms from spec §11.6, the
  eq.(8) inversion, the empirical-CDF-vs-parametric Phase C
  comparison plots).

The LaTeX paper REFERENCES the notebook (via `\input{}` of generated
tex fragments OR `\includegraphics{}` of PNG/PDF outputs); the paper
itself stays prose+math without embedded computation. This mirrors the
Stage-2 pattern (`STAGE_2_RESULTS.md` + Stage-2 notebooks in
`simulations/notebooks/saas_builder_stage_2/`).

**Why:** the user maintains separation of concerns between
(a) computation that must be reproducible-on-demand and
(b) writeup that must compile cleanly in LaTeX without re-running
expensive simulations. The notebook handles (a); the paper handles
(b); the paper cites the notebook's emitted artefacts.

**How to apply when the stochastic-fx plan completes:**
1. Confirm Tasks 0-7 + Wave-2 §16.8 are all DONE.
2. Dispatch the LaTeX-econ paper spec design first (per `/latex-econ-model`
   skill; matches doc-first sequencing chosen earlier).
3. In parallel, dispatch Analytics Reporter to scaffold the final-
   simulation notebook structure (cells: setup → per-family run →
   diagnostic plots → cross-family summary → figure-export to
   `notes/stochastic_fx_figures/` or similar).
4. Once the notebook lands, the paper draft references its emitted
   tex/PNG artefacts.
5. cadCAD implementation begins AFTER the LaTeX-econ design spec
   converges (doc-first sequencing).

**Related memories:**
- `[[reference_installed_skills_2026_05]]` for the Analytics Reporter
  + Economist Analyst + Visual Storyteller + Whimsy Injector skill
  matrix.
- `[[feedback_notebook_trio_checkpoint]]` for the notebook-trio
  discipline (why-markdown / code / interpretation-markdown).
- `[[feedback_notebook_citation_block]]` for the 4-part
  decision-citation block convention preceding every test or spec
  choice in the notebook.
- `[[feedback_specialized_agents_per_task]]` —
  foreground-orchestrates-never-authors. The notebook IS authored by
  Analytics Reporter; the orchestrator dispatches with a clear brief.
