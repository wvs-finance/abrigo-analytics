# Model-QA Review — E10 GSPS v0.4 Implementation Plan v0.1 DRAFT

**Reviewer:** Model QA Specialist (independent; content-matched second reviewer per
`feedback_review_pair_specialist_by_content.md`). Reality Checker covers
feasibility/data-gates in parallel.
**Artifact:** `docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md` (552L)
**Anchors read:** E10 v0.4 spec; R6 blueprint v0.1.3 (lines 1-734); dev_ai_cost
evaluation; `feedback_plan_flags_brainstorm_tasks_nonbypassable_data_gates.md`.
**Scope:** modeling/simulation soundness of the phased build. Read-only.
**Date:** 2026-05-20

---

## VERDICT: NEEDS WORK

The plan is structurally sound — the phase sequencing, the Stage-1/Stage-2 firewall
restoration, the exact-decomposition gate, and the descriptive-posture firewall are all
correct. But it **fails the user-mandated 2026-05-20 brainstorm-task-flagging check**:
no task in the plan carries an explicit `[brainstorm-judgment]` / `[mechanical-execution]`
tag, and at least six load-bearing modeling-assumption choices are written as if they
were mechanical build steps. Per the directive, a modeling-assumption choice treated as
mechanical is a **Critical** finding. There is one Critical (the missing flagging),
which on its own bars PASS. No Critical on modeling correctness itself.

**Critical count: 1.**

---

## Findings

### CRITICAL

**C-1 — No task is tagged [brainstorm-judgment] vs [mechanical-execution]; six
modeling-assumption choices are written as mechanical steps.**
The 2026-05-20 directive (`feedback_plan_flags_brainstorm_tasks_nonbypassable_data_gates.md`
§1) is explicit: every plan must tag each task so the dispatched specialist knows
whether to deliberate (with decision-citation) or execute mechanically. This plan has
**zero such tags**. The §1 phase tables carry only (`#`, Task, Specialized agent,
Deliverable) columns. The consequence is exactly the failure mode the directive names:
a dispatched agent treats a functional-form choice as a build step and picks the first
option un-deliberated, un-cited. Six tasks are demonstrably judgment tasks dressed as
mechanical (see the dedicated brainstorm-flagging section below for the per-task
breakdown). Resolution: add an explicit tag column or per-task tag to every §1 / §4 /
§2.5 task, and for each judgment task require a decision-citation block + (where
load-bearing) user surfacing. This is the sole bar to PASS.

### STRONG

**S-1 — The overdispersion mechanism (burstiness, λ(t) modulation 2) is left vague —
no pinned mechanism.** Plan task 2.1 lists "burstiness/overdispersion" as one of the
five λ(t) modulations; task 2.3 says "lock the five λ(t) modulation functional forms
(overdispersion mechanism, event-spike intensity law, drift parametrization)." But a
pure NHPP — which is what the R6 blueprint §2.1 specifies, λ(t)=λ₀·f·g — produces
arrivals that are *equidispersed conditional on λ(t)* (Poisson within each cell). An
NHPP cannot by itself generate the monthly-aggregate overdispersion the spec §6.3
item 2 demands ("the monthly-aggregate Q-distribution is overdispersed"). Overdispersion
requires an explicit mechanism *beyond* λ(t) deterministic modulation: a doubly-stochastic
(Cox) process, a mixed-Poisson (negative-binomial) marginal, a Hawkes self-exciting
kernel, or a stochastic λ₀ drawn per session. The plan never names which. This is the
single most consequential modeling gap because overdispersion directly inflates
Var(Δlog Q) — the denominator term that competes with Var(Δlog FX) in the §4.3 share.
Get the overdispersion mechanism wrong and the entire FX-variance-share surface shifts.
The plan must pin the mechanism as a flagged brainstorm task, not bury it inside a
"lock the functional forms" mechanical clause. (This is also the most important item
the pre-Phase-2 Model QA review must verify — but it should be specified in the plan,
not discovered at review.)

**S-2 — The realized-variance-per-month construction is not explicitly matched between
X and Y in the plan.** Spec §3.2 and §5.2 both pin realized variance as "the within-month
sum of squared daily log-returns (sum-vs-mean convention fixed at pre-pin)." For the
§4.2 identity to hold *cell-by-cell*, X (Var Δlog FX) and Y-component (Var Δlog Q) must
be computed with the *same estimator at the same frequency on the same within-month
index*. Plan task 3.1 builds X as "within-month sum of squared daily log-returns." Plan
task 3.2 builds Y from `cost_τ = Q_τ × $0.01 × FX_τ` "over the sub-monthly index τ" —
but the sub-monthly index for Q (NHPP arrivals, potentially intra-day) is finer than
the *daily* FX index. If Q is aggregated to daily before differencing while FX is
already daily, the match holds; if Q's Δlog is taken at arrival granularity, the
identity `Δlog cost = Δlog Q + Δlog FX` breaks at the cell level because FX is constant
within a day. Task 3.3 asserts the additive identity is "verified to hold exactly" —
but the plan never states the X/Y frequency-alignment rule that *makes* it hold. The
identity is exact algebraically only if both Δlog series are sampled on an identical
time grid. The plan must pin the common differencing grid (recommend: both daily,
within-month) as an explicit task, and the 0.6 property test must exercise the
*alignment*, not just the arithmetic on already-aligned synthetic inputs.

**S-3 — Non-monotone surface risk is acknowledged but the plan provides no detection
rule.** Spec §11 open item 1 names the risk precisely (Model QA item 5: a surface can
dip below break-even in the interior while clearing both endpoints). Plan task 4.2 says
"the grid resolution pinned in this task per spec §11 open item 1" and task 0.7's
harness asserts "the surface is evaluated on a grid across the whole range, not at
endpoints." Good — but evaluating on a grid is necessary, not sufficient. The plan
never says what happens when an *interior grid point* dips below break-even: is that a
SURFACE-PRODUCED with a flagged interior crossing, or a different verdict? The §9
verdict ladder has no rung for "surface non-monotone / crosses break-even in the
interior." The plan should add an explicit interior-crossing detection + reporting step
to task 4.2/4.4 and state how the §9 classifier (task 6.1) treats a non-monotone
surface. As written, an interior dip could be silently averaged away.

### WEAK

**W-1 — Phase 2.5 sequencing is correct but the firewall test is weaker than the
firewall claim.** Phase 2.5 is genuinely sequenced after Phase 2 and strictly before
Phase 3 — §1 ("fires after Phase 2 and strictly before Phase 3"), the Phase 3 entry
criterion ("Phase 2 exit PASS **and Phase 2.5 break-even threshold frozen**"), §4, and
the §3 HALT table all agree. The ex-ante-pinning logic is sound: the break-even is
derived from option-premium economics against an ex-ante exposure assumption, carrying
no Stage-1 content. Correct. But the *mechanical* enforcement (Phase 0.11 Stage-2
firewall) only greps for "payoff-fitting language" — it cannot detect the subtler
breach the directive cares about: a Phase 2.5 agent who pins the ex-ante exposure
assumption by *peeking* at the Phase 1 FX snapshots' realized variance. The plan says
the assumption is "informed by the panel currencies' historical FX-vol regimes" (task
2.5.1) — historical FX-vol is Phase-1 ingested data. There is a thin line between
"informed by historical regimes" (legitimate ex-ante prior) and "calibrated to the
panel's realized variance" (firewall breach). The plan should state the bright line
explicitly: the ex-ante exposure assumption may use *published long-run FX-vol regime
characterizations* but may NOT use the realized within-window variance of the E10 panel
itself. Without that line, Phase 2.5 task 2.5.1 is a judgment task with a latent
firewall hazard.

**W-2 — G≈8 is carried honestly into the descriptive posture but the FE estimation
phase (task 4.1) does not restate the limitation at point of use.** §5 and the spec §8
name G≈8 as the structural reason for the descriptive demotion. Good. But task 4.1
("vol-on-vol two-way-FE regression — currency FE + month FE; report the descriptive
sign of β") runs a two-way FE panel on 8 currency clusters × ~30 months. With currency
FE *and* month FE on G≈8, the within-transformation burns one degree of freedom per
currency and per month — the residual identifying variation is thin, and any clustered
SE is for context only. The plan correctly routes inference to descriptive bands
(task 4.3, "neither gates a verdict") and the descriptive-posture firewall (0.13) bans
inferential language — so there is no PASS-rung leakage; this is consistent. The weak
point is only that task 4.1 itself does not restate "G≈8, descriptive sign only" at the
point the regression is implemented — it relies on the firewall to catch leakage rather
than instructing the agent up front. Minor: add the G≈8 caveat to the 4.1 task text.

**W-3 — Descriptive-bands posture is correct; no PASS-rung leakage found.** Task 4.3
keeps the wild cluster bootstrap and permutation arm "ONLY as descriptive bands... 
explicitly labelled illustrative-not-inferential at G≈8... Neither gates a verdict."
This matches spec §7 and CORRECTIONS-E10-4 Fix 1. Task 0.13's descriptive-posture
firewall bans "PASS", "confirmatory", and inferential-β phrasing mechanically. The §9
ladder (SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT) has no PASS rung. Sensitivity arms
(Phase 5) are "descriptive concordance only" and "cannot rescue a primary HALT." This
is all consistent — no finding, recorded as a clean pass of check 5.

### OBSERVATION

**O-1 — The five λ(t) modulations are sequenced correctly across spec→build→calibrate→
test, except for the overdispersion gap (S-1).** Specification lives in spec §6.3
(pre-committed) and plan task 2.3 (functional forms locked). Build is task 2.1. Calibration
is task 2.2 (to the §6.2 NON-FANTASY anchor). Testing is task 0.5 (failing harness
"exercising the five λ(t) modulations"). The order is sound: forms locked before any
run (Model QA N-5 carried), harness red before build. The only defect is that
modulation 2 (overdispersion) cannot be a deterministic λ(t) form (S-1).

**O-2 — The exact-decomposition gate is correctly placed.** The §4.2 identity
`Var(Δlog cost) = Var(Δlog FX) + Var(Δlog Q) + 2·Cov` is a genuine exact algebraic
identity (verified numerically: variance of a sum, residual ≈ 1e-15). Task 0.6 demands
a property test asserting it holds "exactly... (no leading-order tolerance)" and task
3.3 verifies "no leading-order term." This is correct and matches the spec's deletion
of the v0.2 "leading-order" caveat. The only caveat is the X/Y frequency-alignment
precondition (S-2) — the identity is exact only on a common differencing grid.

**O-3 — R6 reuse framing is honest.** The plan states ~70% fresh / ~10-15% reuse,
consistent with the dev_ai_cost evaluation (which says ~25-30% reuse counting
engineering scaffolding, ~70% fresh estimation core). The plan correctly treats the R6
*design* as reused and the R6 *code* as non-existent ("the R6 code does not exist and
is built fresh"). The discard of cap-wait/session-cap logic (task 2.1) is correct —
x402 has no session cap.

---

## Brainstorm-task-flagging check (USER-MANDATED, 2026-05-20)

**Result: FAIL.** This is the finding that drives the NEEDS WORK verdict.

The plan carries **no `[brainstorm-judgment]` / `[mechanical-execution]` tags on any
task**. Per the directive, this is a Critical-class deficiency (C-1). From a modeling
vantage, the following six tasks are judgment tasks the plan currently treats as
mechanical:

| Brainstorm task | Plan location | How the plan treats it | Should be |
|---|---|---|---|
| **The five λ(t) functional forms** | 2.1, 2.3 | "lock the five λ(t) modulation functional forms" — phrased as a mechanical lock-in | `[brainstorm-judgment]` — choosing a diurnal form, an event-spike intensity law, a drift parametrization are functional-form choices. Decision-citation required. |
| **The overdispersion mechanism** | 2.1, 2.3 | listed inside "lock the functional forms"; mechanism never named (S-1) | `[brainstorm-judgment]` — Cox vs mixed-Poisson vs Hawkes is a structural modeling choice; load-bearing for the §4.3 share; must surface for deliberation. |
| **The ex-ante exposure-assumption prior (Phase 2.5)** | 2.5.1 | "Declare the ex-ante exposure assumption" — phrased as a declaration step | `[brainstorm-judgment]` — it is a declared prior on FX-vol exposure structure; spec §11 open item 2 itself flags it for review. Decision-citation + user surfacing required. |
| **The surface-grid resolution** | 4.2 | "the grid resolution pinned in this task" — phrased as a within-task pin | `[brainstorm-judgment]` — resolution must be fine enough to catch a non-monotone interior crossing (S-3); spec §11 open item 1 flags it. Judgment + citation. |
| **The Q_low pinning rule** | 2.3 | "Pin `Q_low` per the §2.4 qualitative-limit rule" — phrased as rule-application | Carries both: the *rule* is spec-given (mechanical application), but identifying "the volume at which observed logs first exhibit a qualitative pattern the free tier cannot serve" is a judgment call on real data. Tag as **mixed** — flag the judgment sub-step. |
| **The Q-FX dependence structure** | 2.1 (primary: independence), 5.1 (coupling arm) | primary independence is spec-pinned (§6.4); the coupling arm's "pre-stated sign and magnitude" is in task 5.1 as a mechanical re-run | `[brainstorm-judgment]` for the coupling arm's sign+magnitude — those are not yet pinned in the plan or spec and require an economic-behavioral judgment. |

The plan's §9 dispatch note assigns Model QA Specialist to "the estimation/decomposition
core" and "simulator-calibration discipline" — but assigning an agent is not the same
as flagging a task as judgment-bearing. A specialist dispatched against an
un-flagged task still reads (Task, Deliverable) and may execute mechanically.

**Required fix for PASS:** add an explicit tag to every task in §1, §2.5 (§4), and the
phase tables; for each `[brainstorm-judgment]` task, require a decision-citation block
(4-part: reference / why / relevance / connection) and, for the load-bearing ones (the
overdispersion mechanism, the ex-ante exposure prior), explicit user surfacing before
the dispatched agent commits the choice.

**Note on the data-gate half of the directive:** the plan satisfies §2 of the directive
well — every data-fetch task has an explicit non-bypassable HALT branch (HALT-DV in §3
and §0; Phase 1 NON-RETIREMENT triggers; "no silent migration to alternative
providers"; the fantasy-firewall 0.12 mechanically bans synthetic-FX substitution).
The data-gate half is a clean pass; only the brainstorm-flagging half fails.

---

## Summary of checks

| # | Check | Result |
|---|---|---|
| 1 | R6 NHPP phased build; five λ(t) modulations sequenced | PARTIAL — sequencing sound; overdispersion mechanism vague (S-1) |
| 2 | Exact three-way log-variance decomposition; X/Y RV match | PARTIAL — identity exact; X/Y frequency-alignment not pinned (S-2) |
| 3 | Ex-ante break-even pinned before Phase 3 decomposition | PASS — correctly gated; minor firewall-line hazard (W-1) |
| 4 | FX-variance-share surface grid; non-monotone-surface risk | PARTIAL — grid required; no interior-crossing detection rule (S-3) |
| 5 | Descriptive bands kept descriptive; no PASS-rung leakage | PASS (W-3) |
| 6 | G≈8 carried honestly into estimation phase | PASS — not re-inflated; restate at task 4.1 (W-2) |
| — | **Brainstorm-task-flagging (user-mandated)** | **FAIL — C-1** |

---

## Path to PASS

1. **C-1 (mandatory):** tag every task `[brainstorm-judgment]` / `[mechanical-execution]`
   / mixed; require decision-citation + user surfacing on the six judgment tasks.
2. **S-1:** name the overdispersion mechanism explicitly as a flagged brainstorm task
   (Cox / mixed-Poisson / Hawkes / stochastic-λ₀) — it is not a deterministic λ(t) form.
3. **S-2:** pin the common X/Y differencing grid (recommend daily, within-month) as an
   explicit task; the 0.6 property test must exercise alignment, not pre-aligned inputs.
4. **S-3:** add an interior-crossing detection + reporting step to task 4.2/4.4 and
   state how the §9 classifier treats a non-monotone surface.
5. **W-1/W-2:** state the ex-ante-prior bright line (published regime characterizations
   only, not E10-panel realized variance); restate G≈8 in task 4.1.

PASS is blocked solely by C-1 (and the directive's PASS condition). The modeling core
itself has no Critical — S-1/S-2/S-3 are Strong and fixable in a v0.2 amendment. Once
the tags are added and S-1/S-2/S-3 resolved, this plan is sound for execution.

---

*Model-QA review of E10 GSPS v0.4 implementation plan v0.1 — closes here.*
*Roll up to plan v0.2 with the parallel Reality Checker review per block-protocol.*
