# MQ Verdict — SAAS-COHORT-CLOSE plan v0.1 (Wave 2 of 2)

**Plan:** `docs/plans/2026-05-09-saas-cohort-close.md` v0.1
**Reviewer:** Model QA Specialist (independent)
**Date:** 2026-05-08
**Default verdict basis:** REJECT unless full math-contract integrity.

---

## Verdict: **REJECT**

Two compounding spec-amendment defects (P0 scope, P2 anti-fishing posture) and one schema-bump methodology error block promotion. Phases 1, 3, 5, 6, 7 are clean.

---

## BLOCKs

### BLOCK-1 (HIGH) — Plan ll. 116–158 (Phase 2): Path β is **anti-fishing-suspect retro-fit**, not ambiguity adjudication
Quote (l. 118): *"Path β (per-tier θ_k re-parameterization) chosen over Path α (brute N_draws ≈ 7.1e5) because (i) it also resolves C1 MQ-FLAG-1 (`pi` posterior near-prior structurally), (ii) spec §5.4 hints at per-tier θ_k as a methodological richness."*

Three independent residual-evidence findings invalidate this:

(a) **Spec §5.4 does NOT hint at per-tier θ_k.** Verbatim §5.4 (spec ll. 363–375) is *"Realism overrides committed (resolves RC-BLOCK-3, RC-FLAG-2)"* — it covers bracket coverage, cost-revenue endogeneity (ρ=0 primary), bank-spread sensitivity-arm demotion, and cross-border scope. **No per-tier θ_k clause exists.** The C1 MQ-v0.4 verdict (l. 12) reads §5.4 the opposite way: *"per-tier (α, x_m, μ, φ) is shared, **deferred** to COHORT-2/3 per spec §5.4"*. The plan inverts a deferral into a hint. This is the textbook anti-fishing failure mode.

(b) **C1 MQ-FLAG-1 is LOW-severity documentation, not a structural defect.** C1 MQ-v0.4 ll. 51–52: *"FLAG-1 (LOW, D4): π posterior is structurally near-prior in COHORT-1 because tier-conditional θ_k is deferred. **Document this as a spec-property in plan v0.4 (one-line caveat)** so COHORT-2/3 readers don't mistake the v0.4 §8(7) ratio of 1.04 on π for a meaningful posterior update."* The audit prescribes a one-line caveat. The plan retro-fits an entire re-parameterization instead.

(c) **C4 RC v0.3 explicitly endorses Path α.** RC ll. 55–56: *"Real-C1 MC breach (stderr/Ẑ ≈ 1.3e-2 vs 1e-3 ceiling) is a LEGITIMATE HALT, not a defect. … The proper disposition is HALT-WEAK + N-bump, not vectorization. System did the right thing."* RC also flags "raise n_draws to 1e6 (cheap, deterministic)" as the budget remediation. Plan demotes this with no engineering justification (the "~6h re-fit" claim at l. 118 is not in any audit residual).

Path β converts a LOW documentation flag into a v1.3 spec amendment with **3× free parameters** and unaudited identification consequences. This is silent-fishing under the `feedback_post_hoc_fit_anti_fishing_pattern` rule the plan itself proposes to memorialize in Phase 6 — the irony is structural.

**Required remediation:** Replace Phase 2 with Path α (N_draws = 7.1e5; deterministic; no spec amendment). Move Path β to Stage-3 deferred-items list (plan ll. 20–24). C1 MQ-FLAG-1 → Phase 3 nit (one-line caveat in C1 plan v0.4 §"v0.3 → v0.4"). If user truly wants Path β, the plan must (i) cite the spec clause permitting per-tier θ_k explicitly (none exists in v1.1.1) and (ii) pin per-tier prior + identification audit BEFORE re-fit, not after.

### BLOCK-2 (HIGH) — Plan ll. 49–73 (Phase 0): order-of-operations contaminates ambiguity adjudication
Quote (l. 51): *"COHORT-3 v0.3 MQ-FLAG-2: spec §5 Det+churn revenue form does not pin whether $S_t$ is the deterministic factor `(1-λ)^t`, Bernoulli per-step, exponential survival, or Weibull. C3 implementer chose deterministic but the ambiguity persists in the locked spec text."*

Quote (l. 65): *"`Model QA Specialist` writes additive amendment to spec §5 pinning $S_t$ as the deterministic factor `(1-λ)^t` (matches existing C3 implementation; rationale per Task 0.1 memo)."*

The amendment direction is **pre-determined to ratify the existing C3 implementation** before the Task 0.1 literature survey runs. Task 0.1 (l. 60) asks the agent to *"enumerate the 4 candidate $S_t$ forms … and state which form COHORT-3's existing implementation actually computes"* — but Task 0.2 already pins the answer to whatever C3 chose. This is anti-fishing-equivalent to the 1/κ post-hoc fit the plan correctly identifies as a case study (Phase 6).

The C3 v0.3 PSIS-LOO-CV verdict was computed under one $S_t$ form. If the literature survey concludes Bernoulli per-step or exponential survival is the methodologically-correct choice, the C3 ELPD comparison must be redone — not silently ratified. The plan does not address k̂ sensitivity (the user's audit-dimension question) nor whether form-choice changes the Det+churn-vs-AR(1)-vs-martingale ranking.

**Required remediation:** Decouple Task 0.2 from C3 implementation. Task 0.1 selects $S_t$ form on methodology grounds (cohort-specific churn dynamics for solo AI-native LATAM builders — note plan §0 trigger does not articulate the economic semantics). Task 0.2 pins whatever the survey concludes. If the conclusion ≠ deterministic factor, Task 0.3 routes to C3 re-fit + ELPD recompute, not to v1.2 amendment freeze.

### BLOCK-3 (MEDIUM) — Plan ll. 196–217 (Phase 4): "reject with migration hint" silently fails sidecar consumers
Quote (l. 203): *"add backward-compat test (load v1.0 JSON → reject with clear error OR migrate via additive defaults — pick 'reject with migration hint' to avoid silent data drift)."*

Schema bump is declared additive (l. 196 header), but the chosen behaviour is **reject-on-old-version**. Additive bumps must accept v1.0 by definition (additive ⇒ v1.1 reader is a superset of v1.0 reader). Choosing "reject" here is a **breaking** schema change mislabeled as additive. Per the user's audit dimension 3 ("retain sidecar reading capability"), the v1.1 reader must accept v1.0 and treat new per-TP fields as `None | absent`.

**Required remediation:** Switch to "migrate via additive defaults" (the user's intent). Mark new fields `Optional` in `ZCapPinned`; transient Pydantic validator in `simulations/utils/json_io.py` accepts both versions. Round-trip test: v1.0 load → v1.1 emit (with absent fields = `None`) → v1.0 read still succeeds. Sidecar `.md` deprecation marker is fine.

---

## FLAGs

### FLAG-1 (LOW) — Plan l. 350: self-review item 7 understates Phase 1 risk
Quote: *"Phase 1, 3, 6, 7: foreground review sufficient (mechanical work or process)."*

Phase 1 emit scripts produce the artifacts that Phase 5 modeling memo cites and Phase 4 schema migration validates. Mechanical-work classification is correct only if scripts are pure rebuilds; if they re-fit posteriors (Task 1.1 l. 92, Task 1.3 l. 104 *"rebuild C1 posterior"*), seed-pinning + run-determinism merit RC verify. Add RC light-pass on Phase 1 commits.

### FLAG-2 (LOW) — Plan ll. 332–333: HALT trigger inventory missing Phase 1
Quote: *"HALT triggers explicit at Tasks 0.3, 2.4, 2.5, 3.x (via audit-pass chain), 4.2, 5.2."*

Task 1.3 l. 106 verifies *"5-TP sign cert PASS"* but no HALT path is defined for sign-cert FAIL on real-C1 re-build. If C1 posterior shifts under any Phase-3 nit (e.g., `tier_idx` builder slot-0 fix at l. 167), Z_cap signs may flip. Add explicit HALT + CORRECTIONS-α route.

### FLAG-3 (LOW) — Plan l. 233 (Task 5.1): memo limitations omit per-tier θ_k caveat under Path α
If BLOCK-1 is honored and Path α is adopted, the memo must state: *"π posterior remains structurally near-prior because tier-conditional θ_k is deferred to Stage-3 per spec §5.4; this does not invalidate the Z_cap sign cert (π contribution is ~1e-10 of q/(X/Y) per RC v0.3 ll. 58)."* Plan brief at l. 233 currently asserts the opposite (*"per-tier θ_k now-informative"*).

### FLAG-4 (LOW) — Plan ll. 248–251 (Phase 6 memos): lessons correctly framed; one wording risk
The three lessons (self-grading-vs-independent, post-hoc-fit anti-fishing, worktree-no-subdispatch) are methodologically accurate per residuals. **However**, if BLOCK-1 stands and Phase 2 ships Path β, the post-hoc-fit memo would be authored by the same plan that commits a post-hoc fit. Either fix Phase 2 (BLOCK-1 remediation) or note the contradiction.

### FLAG-5 (INFO) — Plan l. 153 (Task 2.4 Step 4): commit-message convention drift
*"`data: re-emit Stage-2 artifacts under spec v1.3 (per-tier theta_k)` — note `data/` is gitignored so this commit is the driver-script invocation log + diagnostics, not the JSON itself."* — the commit subject promises `data:` content but the body says no data committed. Use `chore(saas-cohort-1):` instead.

---

## Methodology audit dimensions — coverage map

| Dim | Covered? | Notes |
|---|---|---|
| 1. P0 spec v1.2 amendment scope | NO — BLOCK-2 | Decoupled from C3 implementation required |
| 2. P2 Path β methodology | NO — BLOCK-1 | Anti-fishing fail; spec §5.4 misread |
| 3. P4 schema bump | NO — BLOCK-3 | Reject-on-old mislabeled as additive |
| 4. P5 modeling memo content | PARTIAL — FLAG-3 | Limitations need per-tier deferral |
| 5. Phase 1 emission ordering | YES | C3 ∥ C2 → C4 correctly sequenced (l. 87, l. 110) |
| 6. Phase 3 nits sweep classification | YES | Methodology-touching item (l. 168 `delta_upper_bound_95`) routed to Task 3.2 with audit-pass chain |
| 7. P6 memory hygiene framing | PARTIAL — FLAG-4 | Lessons correct; contradiction-with-Phase-2 risk |
| 8. HALT triggers | PARTIAL — FLAG-2 | Phase 1 missing |
| 9. No silent fishing in spec amendments | FAIL — BLOCK-1, BLOCK-2 | Both spec amendments retro-fit |

---

## Remediation cycle

Cycle Phase 0 (Task 0.2 decoupling) and Phase 2 (Path α swap) → re-author plan v0.2 → re-run RC + MQ 2-wave verify before Phase 0 dispatch. BLOCK-3 is a one-line edit. FLAGs are resolvable in v0.2 self-review pass.

**Word count: 691.**
