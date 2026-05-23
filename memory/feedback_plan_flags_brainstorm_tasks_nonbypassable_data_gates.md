---
name: plan-flags-brainstorm-tasks-nonbypassable-data-gates
description: User directive 2026-05-20 — implementation plans must (1) distinguish brainstorm-judgment tasks (modeling assumptions, equation/spec structure choices) from mechanical-execution tasks so the dispatched specialist knows which is which, and (2) mark data-fetching steps as NON-BYPASSABLE gates — if required data is genuinely unavailable, the task HALTs honestly; it never fabricates, flat-fills, or arbitrarily substitutes data.
metadata:
  type: feedback
---

## Rule

An Abrigo implementation plan specifies HOW specialized agents execute tasks.
Two things every plan must make explicit:

### 1. Flag brainstorm-judgment tasks distinctly from mechanical-execution tasks

Some plan tasks are not mechanical — they require genuine judgment / brainstorming:
- choosing modeling assumptions
- choosing equation or specification structure
- choosing functional forms (e.g. an intensity-function family, a payoff geometry)
- choosing an ex-ante prior or calibration target

These must be **explicitly flagged in the plan as brainstorm-tasks**, so the
dispatched specialist agent knows to deliberate (and, where the choice is
load-bearing, surface it for user input via the decision-citation discipline)
rather than mechanically pick the first option. Mechanical-execution tasks
(build the indexer, run the pull, write the schema test) are flagged as such.
A plan that treats a modeling-assumption choice as if it were a mechanical
step invites an un-deliberated, un-cited decision.

### 2. Data-fetching steps are NON-BYPASSABLE gates — no flat-data fabrication

> User (2026-05-20): "some gating things must not be bypassed, especially for
> data fetching. If we find that we need some data, unfortunately ... we cannot
> bypass it and come up with arbitrary solutions about flat data."

Every plan task that fetches data is a **non-bypassable gate**. If the required
data is genuinely unavailable / unreachable / out of window:
- the task **HALTs honestly** (disposition memo + the iteration's HALT chain)
- it does **NOT** fabricate data, flat-fill a series, substitute an arbitrary
  constant, or proceed on a placeholder
- "the data is not there" is a real verdict (PARTIAL / NON-RETIREMENT), never
  a problem to engineer around

This is the anti-fishing invariant applied to the data layer: a missing input
is surfaced, not silently filled. Plans must state the HALT explicitly at each
data-fetch task, not leave it implicit.

## Why

A plan is the contract a dispatched specialist agent executes against. If the
plan does not flag a modeling-assumption task, the agent treats it as
mechanical and picks arbitrarily. If the plan does not mark a data-fetch as a
non-bypassable gate, an agent under pressure to "complete the task" may
flat-fill or fabricate to keep moving. Both failure modes are prevented at the
plan-writing stage by making the distinction explicit.

## How to apply

When writing or reviewing an Abrigo implementation plan:
- Tag each task: **[brainstorm-judgment]** or **[mechanical-execution]** (or note
  it carries both a judgment sub-step and a mechanical sub-step).
- For every data-fetch task, state the non-bypassable gate + the explicit HALT
  branch ("if series X is unavailable for the pinned window → HALT, disposition
  memo, do NOT substitute").
- Plan reviews (per [[review-pair-specialist-by-content]]) must verify both:
  brainstorm-tasks flagged, data-fetch HALTs explicit.

## Links

[[review-pair-specialist-by-content]] — the 2-way plan/spec review that enforces this
[[data-visibility-gate-before-modeling]] — the upstream DV gate; this rule covers the per-task data-fetch step
[[pathological-halt-anti-fishing-checkpoint]] — the HALT discipline a missing-data gate routes into
[[no-code-in-specs-or-plans]] — plans are code-agnostic; this rule governs how tasks are described
