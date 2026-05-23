---
artifact_kind: disposition_memo
parent_spec: docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md v1.0
emit_timestamp_utc: 2026-05-07
trigger: 2-wave doc verify returned REJECT/REJECT (Wave-1 RC: 3 BLOCKs + 5 FLAGs; Wave-2 MQ: 7 BLOCKs + 6 FLAGs)
authority: feedback_pathological_halt_anti_fishing_checkpoint (HALT + disposition + user adjudication + CORRECTIONS-block + post-hoc verify)
precedent: corrections_eta_decomposition.md (sibling 8-BLOCK case, user picked γ)
---

# Disposition memo — SaaS-builder Stage-2 pre-reg v1.0 → v1.1 pivot

## §1 Why this memo fires

Both audit waves returned REJECT. Combined: 10 load-bearing BLOCKs + 11
FLAGs. Per `feedback_pathological_halt_anti_fishing_checkpoint`, this
requires HALT → disposition memo with ≥3 pivot options → user
adjudication → CORRECTIONS-block in v1.1 → post-hoc 2-wave verify on
v1.1 result. This memo executes step 2 of that protocol.

## §2 Combined BLOCK summary

**Wave-1 RC (reality / scope / source discipline):**
- RC-BLOCK-1 — dev-AI Stage-1 FAIL (β=−0.146, 2026-05-06) silently
  ignored; potential stage-drift per CLAUDE.md.
- RC-BLOCK-2 — N_MIN=75 / POWER_MIN=0.80 / MDES_SD=0.40 mis-imported
  into synthetic-Bayesian regime where they don't apply.
- RC-BLOCK-3 — bank-spread $s_t$ overlay declared in §5.4(c) but absent
  from §3 FX-path lock; silent primary-spec mutation.

**Wave-2 MQ (methodological correctness):**
- MQ-BLOCK-1 — **Pareto $\tau_{j,i}$ has undefined mean** under cited
  prior (implied α ≈ 1.24); $\mathbb E[a_s]$ ill-posed; bootstrap CI
  inconsistent.
- MQ-BLOCK-2 — LogNormal $N_j$ continuous-not-integer; cited 30×
  variance is τ-variance not N-variance; use NegBin.
- MQ-BLOCK-3 — $x_m(i)$ position-dependence unpinned; primary form's
  iid assumption contradicts cited Ouyang super-linearity.
- MQ-BLOCK-4 — (T2) kink produces Dirac mass in $\Gamma^{(a_s)}$;
  bootstrap CI undefined; "3 test points" insufficient certification.
- MQ-BLOCK-5 — primary-tier-pin (§6) vs tier-mix-posterior (§9)
  inconsistency; CORRECTIONS-ι requires per-user heterogeneity.
- MQ-BLOCK-6 — AICc wrong for PyMC pipeline; use PSIS-LOO-CV.
- MQ-BLOCK-7 — stationary-bootstrap mis-applied to non-time-series
  posteriors.

The asymmetry: **MQ-BLOCK-1 is the only BLOCK that makes the spec
ill-posed-by-construction.** The other nine are spec-text fixes (form
choices, threshold inheritance, contradictions, criterion replacements)
that don't require structural redesign.

## §3 Pivot options

### Option α — full v1.1 patch in one revision

Apply all 10 BLOCK fixes simultaneously. Recommended by both auditors
("patch to v1.1 addressing all BLOCKs").

**Specific fixes by BLOCK:**

| BLOCK | Fix |
|---|---|
| RC-1 | Add §0.1 reconciling dev-AI Stage-1 FAIL: explain why this cohort ≠ Section J narrow-ICT employment-share; invoke CLAUDE.md "ideal-scenario clause" independent of empirical β. |
| RC-2 | Replace §8 verbatim invariants with: (a) genuinely-applicable Stage-2 invariants (sign pre-pin, bracket immutability, HALT-on-conflict); (b) declaration that N_MIN/POWER/MDES bind Stage-3 cohort survey only; (c) Stage-2-specific: posterior CI-width thresholds, sim-count floor, prior-sensitivity sweep. |
| RC-3 | Demote $s_t$ to sensitivity arm only; remove from "primary spec" wording in §5.4(c); §3 unchanged. |
| MQ-1 | Replace Pareto with TruncPareto($\alpha, x_m, x_{\max}=\kappa$); pin $\alpha \in [1.5, 2.5]$ bracket; refuse posteriors with $\alpha < 1.5$. |
| MQ-2 | Replace LogNormal $N_j$ with NegBin($r, p$) (over-dispersion 2.3× from costs-doc p90/mean = 30/13). |
| MQ-3 | Pin primary as iid with constant $x_m$; demote position-dependence to sensitivity arm with explicit form $x_m(i) = x_m^0 (1 + i/i_0)$, $i_0$ bracketed. |
| MQ-4 | Replace bootstrap-CI-of-point-Γ with softplus-regularized Γ; require TODO-COHORT-4 certification at 5 test points including $\kappa \pm 0.5\kappa$. |
| MQ-5 | Replace primary-tier-pin with tier-prior (e.g., Pro 20% / Max-5x 50% / Max-20x 30%); §6 emits `tier_id` as discrete latent. |
| MQ-6 | Replace AICc routing with PSIS-LOO-CV via `arviz.compare`: PASS if $\Delta\mathrm{elpd}_{\mathrm{loo}} > 4 \cdot \mathrm{SE}$; INDISTINGUISHABLE if $< 2 \cdot \mathrm{SE}$. |
| MQ-7 | Strip stationary-bootstrap from §7; replace with `pm.sample_posterior_predictive` + percentiles. |

**Pros:** single CORRECTIONS-block, single re-verify cycle, clean
audit trail.
**Cons:** 10 simultaneous changes; v1.1 may itself need a third wave;
cognitive overhead.
**Effort:** 1–2 sessions to author + 1 verify cycle.

### Option β — decompose v1.1 (RC fixes) + v1.2 (MQ fixes)

Mirror the CORRECTIONS-η decomposition pattern. v1.1 lands the 3 RC
BLOCKs (scope, anti-fishing-applicability, FX-path-lock cleanup); v1.2
lands the 7 MQ BLOCKs (math/stats methodology).

**Pros:** lower-risk per cycle; matches established repo pattern
(CORRECTIONS-η was decomposition over a smaller BLOCK count); easier to
review each wave independently.
**Cons:** two verify cycles instead of one; longer wall-clock; v1.1
itself doesn't unblock sub-task dispatch (must wait for v1.2).
**Effort:** 2 sessions + 2 verify cycles.

### Option γ — substantive scope pivot: lock-less pre-reg

Recognize that 7 of 10 BLOCKs are functional-form choices being made
*before* data is available. The right pre-reg in a Bayesian regime
locks **scope, gates, and discipline** — not point-estimates of
distribution shapes.

**Concretely, v1.1-γ pre-reg locks:**
- Cohort scope (§1, §2, §3 FX-path class — unchanged from v1.0).
- Anti-fishing discipline applicable to synthetic-Bayesian: bracket
  immutability, prior-elicitation discipline (≥3 independent
  first-party sources per parameter), candidate-set closure (no
  post-hoc additions), model-selection criterion (LOO-CV with
  pinned thresholds).
- Verification gates §9 with kink-aware Γ, model-comparison criterion,
  test-point structure.
- Output artifact contract §10.

**v1.1-γ pre-reg does NOT lock:**
- Specific $\tau$ distribution family (TruncPareto vs. mixture vs.
  TruncWeibull) — pinned by TODO-COHORT-1 LOO-CV competition over a
  closed candidate set.
- Specific $N$ distribution (NegBin vs. ZINB vs. Hurdle) — same.
- Position-dependence form $x_m(i)$ — same.
- Tier-mix prior — pinned by TODO-COHORT-1 from cohort-sourcing
  metadata.

**TODO-COHORT-1 becomes a prior-elicitation + posterior-comparison
task** that pins functional forms via competition within the closed
candidate set, with LOO-CV as the criterion and the §9 routing
(PASS / WEAK / MARGINAL / FAIL / INDISTINGUISHABLE) as the verdict.

**Pros:** methodologically cleaner — lets data drive functional form
within a closed admissible set; addresses MQ-BLOCK-1, -2, -3, -5
structurally (they become moot — no point-pin to be wrong about);
still answers RC-BLOCK-1, -2, -3.
**Cons:** real rewrite (~1–2 sessions); requires explicit
candidate-set closure to avoid fishing; reviewer must trust the
candidate-set is comprehensive.
**Mitigation:** sha-pin the candidate set in v1.1-γ §6; refuse
post-hoc additions per anti-fishing.
**Effort:** 1–2 sessions to author + 1 verify cycle.

### Option δ — HALT + park spec; reopen Stage-1 FAIL question first

RC-BLOCK-1 is the most thesis-level concern. Per CLAUDE.md, "Stage-1
empirical β confirmation FIRST. Stage drift (M-design ballooning back
into apparatus) is anti-fishing-banned."

The dev-AI Stage-1 FAIL closed 2026-05-06 with sign-flip
(β=−0.146 on Section J ICT). `memory/project_saas_builder_stage_2_active.md`
notes the FAIL "raises required Stage-1 sign-prior strength but does
not invalidate this iteration's hypothesis" — but that is *asserted*,
not *adjudicated*.

**Option δ:** before authoring v1.1, write a separate
`docs/specs/2026-05-07-saas-builder-stage-1-fail-reconciliation.md`
that adjudicates whether the SaaS-builder cohort survives the dev-AI
FAIL. Possible outcomes: (i) cohort survives, with explicit new
sign-prior justification → proceed to v1.1 in flavor α/β/γ; (ii)
cohort does not survive → spec is parked indefinitely, scope pivots
to a different cohort.

**Pros:** strictest anti-fishing reading; resolves the highest-stakes
RC-BLOCK at the thesis level rather than the spec-text level.
**Cons:** may pause Stage-2 work indefinitely; reconciliation memo
itself requires careful argument; if cohort survives, eventually
need to land v1.1 anyway.
**Effort:** 1 reconciliation-memo session, then re-evaluate.

## §4 Comparison matrix

| Pivot | Wall-clock | Sessions | Risk | Methodological cleanliness | Resolves RC-BLOCK-1 | Resolves MQ-BLOCK-1 |
|---|---|---|---|---|---|---|
| α | shortest | 1–2 + 1 verify | medium (10 simultaneous changes) | medium (point-pins with brackets) | yes (§0.1 patch) | yes (TruncPareto bracket) |
| β | longest | 2 + 2 verify | lowest per cycle | medium | yes | yes |
| γ | medium | 1–2 + 1 verify | low (data-driven pin) | highest | yes | structural (no point-pin to be wrong about) |
| δ | undefined | 1 reconcile + ? | thesis-level pause | n/a | yes (thesis-level) | n/a until cohort survives |

## §5 Recommendation

**Option α with γ-flavored brackets.** Concretely:
- Do the v1.1 patch in one revision per Option α (single CORRECTIONS
  block, single re-verify).
- For MQ-BLOCK-1, -2, -3, -5: prefer **brackets and tier-prior** (γ
  flavor) over **point-pins** (pure α flavor). I.e., TruncPareto
  $\alpha \in [1.5, 2.5]$ not a single $\alpha$; NegBin
  $(r, p)$ with prior 95% CI not a point; tier-prior over $\{Pro,
  Max-5x, Max-20x\}$ with bracket on the mix.
- Address RC-BLOCK-1 with §0.1 reconciliation memo *inline* in v1.1,
  not as a separate Option-δ pause — the reconciliation argument is
  short ("post-revenue solo SaaS builder ≠ Section J narrow-ICT
  employment-share population, hence Section J FAIL is non-binding;
  ideal-scenario clause permits Stage-2 independent of empirical β").
  If this argument feels weak on user review, escalate to Option δ.

This route lands v1.1 in one revision, addresses all 10 BLOCKs, gives
the data-driven cleanliness of γ where it matters most (the heavy-tail
parameter $\alpha$), and preserves the established repo pattern of
single CORRECTIONS-block per disposition.

**Alternative if user prefers stricter discipline:** Option δ first, to
get the dev-AI-FAIL question explicitly adjudicated, then proceed to
α/γ.

## §6 What user adjudication unblocks

Once user picks pivot:
1. Author v1.1 spec per pivot.
2. CORRECTIONS-block embedded in v1.1 header (recording v1.0 → v1.1
   delta with full carry-forward / defer matrix and preserved-guarantees
   argument).
3. Re-run 2-wave verify on v1.1.
4. On ACCEPT or ACCEPT_WITH_FLAGS, dispatch TODO-COHORT-1..4 sub-task
   plans via `superpowers:writing-plans`.

End of disposition memo.
