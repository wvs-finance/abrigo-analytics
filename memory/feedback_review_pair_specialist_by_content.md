---
name: review-pair-specialist-by-content
description: User directive 2026-05-20 — every spec/plan draft gets a 2-way review for feasibility AND truthfulness of its claims. Reality Checker is always one reviewer; the second is the specialist agent matched to the spec's content (Model QA Specialist for econometric/simulation specs, Code Reviewer for code-bearing work, etc.) — not a fixed reviewer pair.
metadata:
  type: feedback
---

## Rule

When drafting a spec, or putting a spec on top of an existing plan, dispatch a
**2-way review** before the spec advances. The review must test BOTH:
1. **Feasibility** — can the claimed thing actually be built / observed / estimated
2. **Truthfulness** — are the spec's factual claims (data prices, endpoint behavior,
   protocol availability, cohort existence, magnitude priors) actually true

**Reviewer 1 is always the Reality Checker** — feasibility + truthfulness is its
core competency; default-to-NEEDS-WORK posture.

**Reviewer 2 is selected by the spec's content**, not fixed:
- Econometric / statistical / simulation spec → **Model QA Specialist**
- Code-bearing implementation work → **Code Reviewer**
- Documentation-heavy spec → **Technical Writer**
- Solidity / smart-contract spec → **Blockchain Security Auditor** or
  **Solidity Smart Contract Engineer**
- Pick the agent from the available roster whose competency matches the
  spec's dominant additions.

## Why

Per user (2026-05-20, during E10 v0.2 brainstorm):

> "We need to test each of the feasibility and truthfulness of the claims we're
> doing. And that's why if we are drafting specs or putting a spec on top of an
> existing plan, we need to do the two-way review by a reality checker. And also
> I noticed specialized agents from the AI agency [roster]... that is appropriate
> based on the additions on the plan that we are putting."

This refines the earlier review-discipline memories: the reviewer pair is not a
fixed set — the second reviewer is chosen to match what the spec actually contains.
A spec dominated by econometric design should not be reviewed by a Code Reviewer
who has no code to review; it should be reviewed by Model QA.

## How to apply

1. After a spec draft lands, do the inline self-review (placeholders / consistency
   / scope / ambiguity).
2. Identify the spec's dominant content type.
3. Dispatch Reality Checker + the matched specialist in parallel.
4. Integrate the union of findings (CORRECTIONS block) before the user-review gate.
5. This runs IN ADDITION TO the brainstorming skill's user-review gate, not instead.

## Links

[[three-way-review]] — prior review-discipline memory (CR+RC+TW for specs/plans)
[[implementation-review-agents]] — prior memory (CR+RC+SD for implementation reviews)
[[self-grading-vs-independent]] — why independent review is non-negotiable
[[pathological-halt-anti-fishing-checkpoint]] — review feeds the HALT/CORRECTIONS discipline
