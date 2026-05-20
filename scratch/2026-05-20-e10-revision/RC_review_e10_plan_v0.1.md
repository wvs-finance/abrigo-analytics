# Reality-Checker Review — E10 GSPS v0.4 Implementation Plan (v0.1 DRAFT)

**Reviewer:** TestingRealityChecker (independent RC) — plan-quality + 3-user-mandated-checks review
**Date:** 2026-05-20
**Artifact under review:** `docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md` (552L, v0.1 DRAFT)
**Cross-referenced:** E10 spec v0.4 (419L); `RC_rereview_e10_v0.3.md`; `ModelQA_rereview_e10_v0.3.md`
**Memory anchors:** `feedback_plan_flags_brainstorm_tasks_nonbypassable_data_gates.md`, `feedback_no_code_in_specs_or_plans.md`, `feedback_pathological_halt_anti_fishing_checkpoint.md`, `feedback_data_visibility_gate_before_modeling.md`
**Posture:** read-only. No plan edits. Default NEEDS WORK.

---

## VERDICT: NEEDS WORK

The plan is structurally strong: spec §10 sub-tasks E10.0–E10.5 each map 1:1
onto a phase with binary entry/exit gates; the descriptive-posture discipline
is carried into every phase and mechanically firewalled (Phase 0.13); the
ex-ante break-even pinning (Phase 2.5) is correctly gated before the §4
decomposition; the closure re-reviews' BLOCK findings (G≈8 demotion, ex-ante
threshold, NGN window) are all reflected. The data-fetch HALT discipline is
genuinely present and is the plan's strongest section.

It is **NEEDS WORK, not PASS**, on one BLOCK: **user-mandated check 1
(brainstorm-task flagging) is not satisfied**. The plan never uses the memory's
required tagging convention. Per `feedback_plan_flags_brainstorm_tasks_nonbypassable_data_gates.md`
("How to apply"): every task must be tagged **[brainstorm-judgment]** or
**[mechanical-execution]**. The plan tags zero tasks. The five load-bearing
modeling-assumption choices the brief enumerates — the five λ(t) functional
forms, the ex-ante exposure assumption, the surface-grid resolution, `Q_low`
pinning — are buried inside ordinary task rows that read identically to
mechanical build tasks. A dispatched specialist reading the plan as a contract
cannot tell which tasks demand deliberation + decision-citation surfacing and
which are mechanical. That is the exact failure mode the memory exists to
prevent. It is a single, fixable defect — but it is a BLOCK per the brief.

**1 BLOCK, 2 STRONG, 3 WEAK, 2 OBSERVATION.**

---

## User-mandated checks (the focus — explicit verdict on each)

### Check 1 — Brainstorm-task flagging — **FAIL (BLOCK-1)**

The memory's "How to apply" is explicit: *"Tag each task: [brainstorm-judgment]
or [mechanical-execution] (or note it carries both a judgment sub-step and a
mechanical sub-step)."* The plan does **not tag a single task**. Every §1 phase
table row and the Phase 2.5 table use the same uniform format (# / Task /
Specialized agent / Deliverable) with no judgment-vs-mechanical marker.

The brief enumerates four+ tasks that are genuine brainstorm-judgment:

| Task | Plan location | Judgment content | Flagged? |
|---|---|---|---|
| Five λ(t) NHPP modulation functional forms | 2.1, 2.3 ("lock the five λ(t) modulation functional forms") | overdispersion mechanism (neg-binomial mix vs Cox process), event-spike intensity law, drift parametrization — Model QA N-5 explicitly calls these *shape* choices | **No** |
| Ex-ante exposure assumption | 2.5.1 ("Declare the ex-ante exposure assumption — a stated, frozen prior") | a declared prior that *pins the break-even* — spec §11 open item 2 flags it for user review as "itself a declared prior" | **No** |
| Surface-grid resolution | 4.2 ("the grid resolution pinned in this task per spec §11 open item 1") | non-monotone-surface coverage; spec §11 item 1 explicitly leaves this for reviewer to confirm whether it should be spec-pinned | **No** |
| `Q_low` pinning | 2.3 ("Pin `Q_low` per the §2.4 qualitative-limit rule") | a behavioral-parameter judgment corroborated by proxy research | **No** |

Each of these is written in mechanical-imperative voice ("lock", "pin",
"declare") indistinguishable from genuinely mechanical rows (3.1 "implement the
X-side realized-variance constructor", 1.1 "implement the FX-series ingest
unit"). The plan *does* say, in §1 Phase-2 prose and §7, that 2.1/2.3 forms are
"locked in the E10.1 calibration note" and route through a 2-way review — but
that is a review checkpoint, not the per-task brainstorm tag the memory
mandates, and it does not instruct the *dispatched specialist* to deliberate +
surface load-bearing choices via decision-citation before the review.

Two mitigating facts (they reduce blast radius but do not discharge the BLOCK):
notebook tasks 2.4/3.5/4.4/5.2/6.2 all carry "decision-citation block at every
choice", and §7's pre-Phase-2 review names the λ(t) forms and `Q_low` as
Model QA verification items. But decision-citation in the *notebook* fires
after the choice is made; the memory wants the *plan task itself* flagged so
the choice is deliberated, not mechanically picked, in the first place.

**Verdict: FAIL. BLOCK-1. The plan must tag every task [brainstorm-judgment] /
[mechanical-execution], and for the four+ judgment tasks above explicitly
instruct the specialist to deliberate and surface load-bearing choices for user
input via decision-citation before locking.**

### Check 2 — Non-bypassable data-fetch gates with explicit HALT — **PASS**

Every data-fetch task in the plan carries an explicit, honest, no-fabrication
HALT branch. Verified task by task:

- **Phase 1 / E10.0 — 8 central-bank FX series.** Task 1.1 ingest + 1.4 panel
  window: "HALT and route to NON-RETIREMENT if any currency's qualifying window
  falls below the panel target." §3 HALT table row HALT-DV covers any series
  going "dark / paywalled / auth-gated" → disposition memo, re-classify DV,
  "No silent migration." Phase 1 NON-RETIREMENT trigger block restates all
  three. **Explicit, no escape hatch.**
- **Phase 1 / x402 price re-verify.** Task 1.3 + Phase 1 NON-RETIREMENT trigger:
  "the x402 price probe no longer returns a free `payment-required` offer
  (HALT-DV)." **Explicit.**
- **Phase 2 / E10.1 — the user's own observed query logs (the NON-FANTASY
  anchor).** Task 2.2: "**HALT here if the observed query trace is thin or
  non-representative** (spec §7 field 7a / RC OBS-1) — route to NON-RETIREMENT."
  Reinforced by §3 HALT-SIM-ANCHOR and the Phase 2 NON-RETIREMENT trigger
  block. **Explicit — this is the central anti-fantasy gate and the plan holds
  it.**
- **Proxy research** (The Graph stats / RPC patterns / analyst telemetry).
  Task 2.2 brackets the range with proxies; if the bracket cannot be cleanly
  formed, §3 HALT-SURFACE-UNCOMPUTABLE / spec §9 PARTIAL covers it. Adequately
  routed (see WEAK-2 — could be sharper).

`§0` HALT-DV explicitly bans silent provider migration and bars escalation to
paid Dune. No data-fetch task offers a fabricate / flat-fill / placeholder
path. **Verdict: PASS.**

### Check 3 — No flat-data fabrication anywhere — **PASS**

A full sweep of the plan finds **no task or fallback that would, under data
scarcity, produce arbitrary / flat / placeholder data instead of HALTing.**

- The simulator-calibration path (Phase 2) — the brief's specific scrutiny
  target — enforces spec §7 field 7a's HALT. Task 2.2 routes a thin/
  non-representative observed trace straight to NON-RETIREMENT with **no
  "use default priors" escape hatch**. There is no fallback prior anywhere in
  Phase 2.
- Phase 0.12 installs a dedicated **fantasy-firewall** CI hook that "rejects
  any commit where the FX series or the $0.01 multiplier is sourced from a
  fitted prior, a synthetic generator, or a placeholder constant instead of the
  real central-bank pull or the verified x402 price." This is a *mechanical*
  enforcement of no-flat-data on the real-input side — stronger than the memory
  requires.
- The only generated quantity is Q, and Q is anchored to the observed trace or
  the iteration HALTs. §5 restates "no panel-window extension to manufacture
  cells; no panel-currency expansion."
- Phase 1.4 routes a sub-target panel window to NON-RETIREMENT rather than
  back-filling cells.

**Verdict: PASS.** (One residual: WEAK-1 — Tier-3 round-trip "within tolerance"
is undefined, a soft spot, but it is a reproducibility check on real data, not
a fabrication path.)

**User-mandated check summary: Check 1 FAIL (BLOCK), Check 2 PASS, Check 3
PASS.** PASS of the plan is therefore precluded until BLOCK-1 is closed.

---

## Standard plan-quality findings

### STRONG-1 — Spec §10 coverage is complete, but Phase 2.5 vs spec §10 ordering should be made explicit.

Every spec §10 sub-task maps to a phase: E10.0→P1, E10.1→P2, E10.2→P3,
E10.3→P4, E10.4→P5, E10.5→P6; Phase 0 = pre-data scaffold; Phase 2.5 = ex-ante
break-even. Spec §10 step 3 (E10.2) says "the §4.4 break-even threshold is
pinned ex ante (in §13) **before** this step" — the plan correctly inserts
Phase 2.5 between P2 and P3 to honor that. **But** the plan's §1 says Phase 2.5
maps to "§13.2 / §4.4" while spec §10 has *no E10.x number* for the break-even
pinning — it lives only in §13. A reader checking "every §10 sub-task mapped"
will find Phase 2.5 has no §10 anchor. This is correct behavior (the spec
genuinely places it in §13, before E10.2), but the plan should state plainly
that Phase 2.5 implements a §13-resident step the spec §10 sequence *assumes
already done* at E10.2, not a §10 sub-task. Minor traceability gap. STRONG
because spec-coverage completeness is a core plan-quality axis.

### STRONG-2 — Phase 2.5 dependency on Phase 2 is asserted but its inputs are not clean.

Phase 2.5 entry = Phase 2 exit PASS. But the ex-ante break-even must be pinned
*independently of any Stage-1 estimation content* (the whole point of
CORRECTIONS-E10-4 Fix 2 / spec §4.4). Phase 2.5 task 2.5.1 says the exposure
assumption is "informed by the panel currencies' historical FX-vol regimes and
the §6.2 anchored Q-volume range" — the anchored Q-volume range is a **Phase 2
output**. So Phase 2.5 *does* consume a Phase 2 product. That is acceptable
only if the Q-volume *range* (a calibration input) carries no §4 *decomposition*
content — which it does not (the decomposition runs in Phase 3). The plan
should state explicitly that Phase 2.5 may consume the Phase-2 anchored
Q-volume range but must NOT consume any Phase-3 decomposition output, and that
the firewall (Phase 0.11) is what enforces this. As written, "Phase N needs
only Phase N−1" is technically satisfied but the firewall-critical distinction
(range OK, decomposition NOT OK) is left implicit. The reviewers' C4-2 / N-2
finding is precisely about this leak path; the plan should not leave it to
inference.

### WEAK-1 — "Within tolerance" undefined for Tier-3 round-trip.

Phase 3 exit and task 3.4 require "`make verify` re-derives Tier 1 from Tier 2
... within tolerance" — tolerance is never numerically pinned. A future agent
picks it arbitrarily. Pin it (bit-exact for the FX panel, a small relative
tolerance for simulator-derived cells with a fixed seed) or flag 3.4 as
carrying a judgment sub-step.

### WEAK-2 — Proxy-research data-fetch lacks an as-explicit HALT as the other fetches.

Task 2.2 brackets the Q-range with "researched proxies (The Graph public
query-volume stats; RPC-provider usage patterns; analyst-tooling telemetry)."
Unlike the FX series and the observed-log anchor, the *proxy* fetch has no
dedicated HALT line — it is covered only transitively by HALT-SURFACE-
UNCOMPUTABLE. Per check 2's standard, every data-fetch task should state its
own no-fabrication HALT. If the proxies are unreachable, the bracket cannot be
formed and the surface degrades to a point — the plan should say so explicitly
at task 2.2 (likely → PARTIAL). Not a BLOCK because the anchor *centre* (the
observed trace) carries the binding HALT, but it should be sharpened.

### WEAK-3 — Engineer-day estimate for Phase 2 may be optimistic.

Phase 2 is budgeted 4.0 engineer-days (~32h) for a *from-scratch* build of a
19-task NHPP simulation engine that "has never been stress-tested by contact
with code" (the plan's own §6 words), including five λ(t) modulations with
locked functional forms, NHPP calibration against an observed trace, and full
TDD against the 0.5 harnesses. The R6 spec alone is 19 tasks. 4.0 days for a
load-bearing simulation core with TDD is plausible only if the λ(t) functional
forms are simple closed-forms; if overdispersion needs a Cox-process or
neg-binomial-mixing layer (Model QA N-5 raises exactly this), 4.0 days is
light. The other phase estimates are realistic. Flag Phase 2 as the schedule
risk and consider a range (4–6 days).

### OBSERVATION-1 — Code-agnostic discipline is genuinely satisfied.

A full sweep finds NO inline code, NO function signatures, NO Python. Type and
module names appear only as artifact identifiers (e.g. "the NHPP intensity-
parameter container", "`scripts/e10_firewall_check.py`"). Tasks are described
as *what to achieve* and *how verified*. The §4.2 additive identity appears as
a math expression, not code — consistent with spec §4.2 and the
`feedback_pathological_halt_anti_fishing_checkpoint.md` exception (pinned math
is allowed). `feedback_no_code_in_specs_or_plans.md` is satisfied.

### OBSERVATION-2 — Descriptive-posture discipline is carried into every phase and mechanically enforced.

No phase produces or implies an inferential β verdict. Phase 0.13 installs a
descriptive-posture CI firewall banning `PASS`, `confirmatory`, and inferential-
β language; every notebook task carries a "descriptive-posture banner"; the
verdict classifier (0.8 / 6.1) asserts "no inferential-β verdict can be
emitted"; §5 names G≈8 as the reason. The closure re-reviews' central BLOCK
(NEW-BLOCK-1 / N-1) is fully absorbed. Strong.

---

## Summary table

| Finding | Severity | One-line |
|---|---|---|
| BLOCK-1 / Check 1 | BLOCK | No task is tagged [brainstorm-judgment]/[mechanical-execution]; the 4+ modeling-assumption tasks (λ(t) forms, ex-ante exposure assumption, surface-grid, `Q_low`) read as mechanical |
| Check 2 | PASS | Every data-fetch task carries an explicit no-fabrication HALT branch |
| Check 3 | PASS | No flat/placeholder fallback anywhere; Phase 2 enforces §7-field-7a HALT with no default-priors escape; Phase 0.12 fantasy-firewall enforces mechanically |
| STRONG-1 | STRONG | Phase 2.5 has no spec §10 anchor (correctly — it is §13-resident); plan should say so for traceability |
| STRONG-2 | STRONG | Phase 2.5 consumes the Phase-2 Q-range; plan should state explicitly it must NOT consume any Phase-3 decomposition output (the C4-2 firewall) |
| WEAK-1 | WEAK | Tier-3 round-trip "within tolerance" undefined |
| WEAK-2 | WEAK | Proxy-research fetch lacks an as-explicit HALT as the FX/anchor fetches |
| WEAK-3 | WEAK | Phase 2 (4.0 ed) optimistic for a from-scratch 19-task NHPP engine with TDD |
| OBS-1 | OBSERVATION | Code-agnostic discipline genuinely satisfied |
| OBS-2 | OBSERVATION | Descriptive posture carried + mechanically firewalled in every phase |

---

## Path to PASS

1. **Close BLOCK-1:** tag every task in every §1 phase table and the Phase 2.5
   table as **[brainstorm-judgment]** or **[mechanical-execution]**. For tasks
   2.1/2.3 (λ(t) forms), 2.3 (`Q_low`), 2.5.1 (ex-ante exposure assumption),
   and 4.2 (surface-grid resolution), add an explicit instruction that the
   dispatched specialist must deliberate and surface load-bearing choices for
   user input via decision-citation *before* locking — not mechanically pick.
2. Address STRONG-1 and STRONG-2 (both are traceability/firewall-clarity
   wording fixes, not redesigns).
3. WEAK-1/2/3 should land but do not gate PASS.

This is a **wording/structuring revision, not a redesign** — the plan's
architecture, phase gating, HALT discipline, and posture firewalls are all
sound. One revision cycle closes it. Until BLOCK-1 is resolved the verdict is
**NEEDS WORK**.

---

**RC review of E10 v0.4 implementation plan v0.1 — closes here.**
