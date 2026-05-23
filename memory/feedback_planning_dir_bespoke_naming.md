---
name: .planning/ uses bespoke filenames per iteration, never GSD/superpowers convention
description: In the abrigo-analytics repo, the .planning/ directory uses iteration-specific bespoke filenames (00-iteration-charter.md etc.) instead of GSD/superpowers names (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md) to avoid conflation across parallel (Y, M, X) iterations
type: feedback
---

**Rule.** When creating or extending `.planning/` for a new (Y, M, X) iteration in `abrigo-analytics`, use **bespoke iteration-specific filenames** (numbered prefix + descriptive name, e.g. `00-iteration-charter.md`, `01-methodology.md`, `02-open-threads.md`). Do **not** use the GSD/`get-shit-done`/`superpowers` convention names: `PROJECT.md`, `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, `config.json`.

**Why:**
- The repo runs multiple parallel (Y, M, X) iterations simultaneously (Pair D Stage-2, dev-AI Stage-1, SaaS-builder Stage-2, plus closed iterations) — see `CLAUDE.md`.
- Each iteration has its own scratch/, notebooks/, docs/specs/, and memory/ artifacts; planning state for any one iteration must not get conflated with the others.
- GSD slash commands (`/gsd:progress`, `/gsd:plan-phase`, etc.) auto-detect `.planning/PROJECT.md` and `.planning/ROADMAP.md` and treat the entire repo as a single GSD project. That's wrong here — the repo is a multi-iteration analytics workspace, not one project.
- Using bespoke filenames keeps `.planning/` discoverable to humans/agents reading the repo, but invisible to GSD's auto-detection.

**How to apply:**
- New iteration kicks off → create `.planning/{iteration_id}/` if multiple iterations need parallel `.planning/` state, OR clear/replace top-level `.planning/` files when only one is active at a time. Confirm with user which mode applies before bulk-rewriting.
- Filenames take the form `NN-purpose.md` where NN is a sort prefix and purpose is short and iteration-relevant.
- Always include a `README.md` at the top of `.planning/` explaining which iteration this scaffolding belongs to and noting the bespoke-naming rationale.
- Substantive artifacts (specs, notebooks, dispositions) still go to `docs/specs/`, `notebooks/`, `scratch/`, `memory/` per the repo's existing convention. `.planning/` is ephemeral scaffolding, not the canonical home of the work.
- If the user invokes a `/gsd:*` slash command, **flag the conflation risk** before letting GSD touch `.planning/`. Suggest a bespoke alternative.
