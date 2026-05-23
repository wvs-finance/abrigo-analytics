# MQ verdict — Stage-3 first-wave master design spec v0.1

**Reviewer:** Math Quality (MQ)
**Spec under review:** docs/specs/2026-05-11-stage-3-first-wave-design.md
**Review wave:** Wave-1 plan-time (per spec §6.1)
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

## Executive summary

The master spec is mathematically sound at the scope-and-gate level: pin
identifications are largely traceable to PRIMITIVES.md, STAGE_2_RESULTS.md, and
the cohort_5_strip code; cross-track dependencies are correctly typed; and the
anti-fishing carry-forward (§1.1) preserves Stage-2 invariants. Two material
flags concern (i) a **metric mismatch** between the spec's §2.3 B1 envelope
assertion `|Π_realized − K̂·σ_T| / |K̂·σ_T| ≤ 0.35` and what `CarrMadanEnvelopeVerifier`
actually computes (a centered-strip vs log-contract-proxy max relative residual
after best-fit β), and (ii) the A1 5pp KEEP/REPLACE margin (§2.1) is **not
covered by any pin** in §5 and could be smuggled later. Neither rises to BLOCK
because both are dispatchable in the per-track plans; both must land as
explicit FLAGs that the A1 and B1 plan reviews resolve.

## Findings (severity-graded)

### BLOCK
(none)

### FLAG (material, non-blocking)

- **MQ-FLAG-1: B1 envelope-assertion form does not match the shipped
  verifier.** §2.3 phase 4 specifies
  `|Π_realized − K̂·σ_T| / |K̂·σ_T| ≤ 0.35`. The shipped
  `CarrMadanEnvelopeVerifier` (`simulations/saas_builder/cohort_5_strip/replication.py:162-191`)
  instead (a) **centers** the strip by subtracting `Π_strip(S_0)`,
  (b) compares the centered residual to the log-contract proxy
  `Q(S_T) = −2·log(S_T/S_0) + 2·(S_T−S_0)/S_0` after (c) a least-squares
  best-fit scale `β`, and (d) reports `max|strip_centered − β·Q| / peak(|strip_centered|)`.
  The 35% tolerance was *derived for this metric* (types.py:57-74,
  rationale `1 − 3·(1/3)² = 2/3` for the 3-piece linear fit floor).
  Applied to the spec's stated form, the metric (i) has a **denominator
  collapse** as σ_T → 0 (relative error blows up when the deterministic
  path of PRIMITIVES.md §5 lands near σ_0), and (ii) drops the centering
  step that the verifier uses to absorb the constant LP collateral floor.
  Mathematical reasoning: the Carr-Madan strip identity PRIMITIVES.md (19)
  is up to a constant + linear-in-S_T offset; the relevant approximation
  error is on the convex EXCESS, not on raw `K̂·σ_T`.
  Suggested fix: B1 plan must pin the assertion as **either** (option A)
  the centered-strip-vs-proxy form actually verified, **or** (option B)
  a different formula `(Π_realized − Π_strip(S_0)) − β·K̂·σ_T` with an
  explicit β-fit step. Pin S6 (cohort_5_strip `__init__`) is the
  canonical reference; B1's plan must cite it.

- **MQ-FLAG-2: A1 5pp REPLACE margin is unpinned.** §2.1 HALT-triggers
  bullet 2 introduces a 5-percentage-point envelope-comparison threshold
  ("candidate X must beat the existing IronCondor by ≥ 5 percentage points
  on the TP1 envelope metric"). This is a **decision threshold** in the
  anti-fishing sense (§1.1 protected class) yet does not appear in §5's
  pin table. Without a pin it could be silently tuned to 3pp or 7pp later
  to flip the verdict, exactly the C4 1/κ pattern Stage-2 caught
  (verdict memo §4.4). Mathematical reasoning: 5pp on a metric whose
  theoretical floor is ~33% (types.py:66-69, `2/3` linear-approx error)
  and empirical achievement is ~30% (types.py:67) corresponds to roughly
  a 15-17% **relative** improvement — large enough to be material, but
  the absolute-vs-relative-error framing is unspecified.
  Suggested fix: add **P-A1.4** to §5 — *"the 5pp REPLACE margin is
  pre-pinned in this master spec v0.1 §2.1 BEFORE the comparison table
  is built; any post-comparison adjustment requires CORRECTIONS-α and
  a fresh RC+MQ Wave-1 review."* Also specify whether 5pp is on the
  raw `max_relative_error` metric or on a derived score.

- **MQ-FLAG-3: A1 cross-strategy envelope comparison may be
  ill-typed.** §2.1 phase 2 reuses `CarrMadanEnvelopeVerifier` for
  *non-IronCondor* primitives ("strangle, butterfly, condor, custom-leg
  combos"). The verifier's geometry is reverse-IC-specific: the
  `assert_long_vol_signature` check (replication.py:197-238) hardcodes
  the **tiled-body** convention where `Π_strip(S_0) ≈ 0` so the
  centered-strip metric equals the raw strip metric. A butterfly or
  strangle does NOT generically have a zero floor at S_0; the centering
  step still works but the comparison-table row meanings shift.
  Suggested fix: the A1 plan must demonstrate that
  `CarrMadanEnvelopeVerifier` applied to a non-reverse-IC primitive
  produces a numerically-comparable score, OR introduce a
  primitive-specific verifier protocol. Reuse of "the same verifier"
  is not by itself a sufficient comparability argument.

- **MQ-FLAG-4: A2 → cohort_5_strip re-emit invariants (S1–S8)
  preservation is asserted but not pinned.** §3 says the re-emit is
  "a re-run of the existing emit driver, not a strategy change"; §4's
  artifact ledger lists `IronCondor_strip.json` re-emit at schema v1.0
  unchanged. However, the K⋆ shift propagates through R8 (Z_cap) and
  thereby through the strike ladder geometry (§S3 in types.py); whether
  S1–S8 all survive a K⋆ shift is an empirical claim, not a tautology.
  Mathematical reasoning: Pin S3 (`x_left < 0 < x_right` strictly) and
  Pin S2 (`Σw_j = 1` under WEIGHT_SUM_TOL) are scale-invariant under
  K⋆ multiplication, but the **tiled-body** geometry (replication.py:200-204)
  depends on `delta_inner` and the choice of log-offset triple — if A2
  emits a K⋆ such that the existing geometry no longer tiles, the
  long-vol signature check (assert_long_vol_signature) will fail.
  Suggested fix: A2 plan adds an explicit re-verification step:
  *"after Z_cap v1.2 re-pin, re-run `CarrMadanEnvelopeVerifier` and
  `assert_long_vol_signature` on the new strip; if either fails, HALT
  and route to A1 (geometry re-tune)."* This is implicit in §2.3 phase 4
  for B1 but should be made explicit pre-B1 for A2.

### NIT (cosmetic)

- **MQ-NIT-1: §2.2 phase 3 phrasing on C1 re-fit.** "C1 cost posterior
  re-fits against the empirical prior" is ambiguous. R5 (STAGE_2_RESULTS.md
  §2.5) marginalized over `(tier_idx, n_per_day, n_month)` exactly. Replacing
  the synthetic Pareto with empirical percentiles changes the **prior**
  `P(tier_i, n_d, n_m)` (or equivalently the prior over `C̄`), not the
  likelihood factor. The marginalization R5 stays analytic; only the prior
  weights change. Recommend rephrasing to: "C1 cost prior is replaced by
  the empirical $(\bar C^{P10},\bar C^{P50},\bar C^{P90})$ percentile
  family; R5's analytic marginalization carries through unchanged, only
  the LSE prior-weights are re-evaluated."

- **MQ-NIT-2: §2.2 P-A2.4 conflation risk.** The pin says "rank-flip
  safeguard armed" by reference to Stage-2 §15.4. Stage-2's HALT-on-flip
  was defined for **Υ_t form selection** (R7 INDISTINGUISHABLE under
  PSIS-LOO-CV). It is NOT defined for cost-prior changes. The §2.2 HALT
  trigger correctly preserves the Υ_t semantic ("if the empirical prior
  triggers a Υ_t LOO ranking flip against det+churn"), but the wording
  in P-A2.4 ("rank-flip safeguard armed") is loose enough to be misread
  as a cost-prior rank flip. Recommend tightening to: "P-A2.4: Υ_t
  PSIS-LOO ranking against det+churn (R7) is re-evaluated under the
  empirical prior; any flip triggers HALT per Stage-2 §15.4 semantic."

- **MQ-NIT-3: §1.3 audit-block lineage sha256 scope.** The chain
  Stage-2 v1.1 → cohort_5_strip strip emit → A2 v1.2 is mathematically
  sound as a content-addressed pin **provided** the sha256 covers all
  inputs that drive the strip geometry — i.e., the canonical fixture
  `(S_0, σ_0, K⋆)`, the log-offset triple, the weight vector, and the
  schema version. STAGE_2_RESULTS.md §6 lists `Z_cap_pinned.json::audit_block`
  but does not enumerate what bytes are hashed. Recommend §1.3 footnote:
  *"the audit_block sha256 covers all fields of the emitted JSON
  artifact; silent drift in non-hashed fields (e.g., compiler version,
  numpy version) is out of scope and tracked by the parent_audit_block
  chain in §4."*

## Method-choice soundness audit

**A1 — Panoptic strategy re-survey.** Method choice is *partly* sound.
The decision to reuse `CarrMadanEnvelopeVerifier` at a single canonical
TP1 fixture is the right starting point — it is the same metric Stage-2
gated on, so cross-strategy comparability is at least *defined*.
Limitations: (i) single-fixture evaluation (§8 limitation 2 acknowledges
this honestly) means a candidate primitive could win at TP1 and lose
across the 24-bracket family, deferred to second wave; (ii) FLAG-3
above — the verifier is reverse-IC-tuned and may not produce
type-comparable scores for other primitive families without adaptation.
The KEEP/REPLACE decision-theoretic structure is correct in principle
but its threshold is unpinned (FLAG-2).

**A2 — Real-data cohort conditioning.** Method choice is sound. R5's
exact analytic marginalization (STAGE_2_RESULTS.md §2.5) means the
synthetic-Pareto → empirical-percentiles substitution is mathematically
clean: the posterior re-fit is a prior re-weighting, not a structural
model change. The N_MIN=75 floor, $r̂<1.01$, ESS_bulk≥1000 are
appropriate carryovers. The HALT-on-rank-flip safeguard (§2.2) is
correctly scoped to the Υ_t LOO ranking, not the cost prior (NIT-2
clarifies). DevSurvey convenience sampling is acknowledged (§8
limitation 3) as a magnitude caveat rather than a sign-cert blocker —
this is the right call given Stage-2's sign-cert posture.

**B1 — Foundry scaffolding.** Method choice is *largely* sound but
the envelope-assertion form (FLAG-1) is a material specification error.
The schema-binding phase (P-B1.1) is correct defense-in-depth; the
24-bracket PRIMITIVES.md §6 generator is the right deterministic test
oracle; the cross-repo handoff via JSON artifact is correctly typed.
The envelope-assertion formula must be re-cited from the shipped
verifier docstring (replication.py:1-28) rather than re-derived
informally.

## Pin coverage audit

| Pin | Mathematical claim | Verifiable as | Pass/Fail |
|-----|--------------------|----------------|-----------|
| P-A1.1 | Comparison-table coverage (existence) | Table exists, primitives enumerated | PASS (existence pin, no math content) |
| P-A1.2 | Envelope evaluation reproducible | audit_block on strategy_verdict.json | PASS (content-addressed) |
| P-A1.3 | KEEP/REPLACE verdict citation-backed | Row reference in verdict JSON | PASS (procedural) |
| **(missing)** | **5pp REPLACE margin pre-pinned** | (no pin) | **FAIL — see FLAG-2** |
| P-A2.1 | Sourcing protocol pre-pinned | SOURCING_PROTOCOL.md timestamp < first-data | PASS |
| P-A2.2 | N ≥ 75 at exit | Sample-size assertion | PASS |
| P-A2.3 | C1 diagnostic gates re-PASS | $r̂<1.01$, ESS_bulk≥1000 | PASS (numerical) |
| P-A2.4 | Rank-flip safeguard armed (Υ_t) | LOO comparison re-run | PASS (with NIT-2 wording fix) |
| P-B1.1 | JSON schema/audit_block validation | Foundry assert | PASS |
| P-B1.2 | Envelope tolerance pinned at 35% | REPLICATION_REL_TOL import | PASS on tolerance value; **FAIL on metric form — see FLAG-1** |
| P-X.1 | RC+MQ Wave-1 review before exec | This review process | PASS (in progress) |
| P-X.2 | RC+MQ Wave-2 post-exec | Future | PASS (procedural) |

Pin gap: the spec is missing a pin for the 5pp A1 margin (FLAG-2 →
P-A1.4 suggested). P-B1.2 passes on tolerance value but fails on
metric-form specification (FLAG-1).

## Dimensional / replication-metric consistency

**§2.1 phase 2 (A1 cross-strategy).** The shipped verifier returns a
dimensionless ratio `max|strip_centered − β·Q| / peak(|strip_centered|)`.
This is the right shape for cross-primitive comparison — primitive-
independent, scale-invariant, and bounded in [0, ∞). However, FLAG-3
notes that the *fit step* (β least-squares against Q) presumes the
candidate primitive admits a single best-fit scale to a log-contract
proxy; this is true for any twice-continuously-differentiable convex
payoff, so structurally fine, but the *interpretation* of β shifts
between primitive families (it absorbs strike-ladder normalization
differently for a butterfly vs reverse-IC). The 5pp comparison threshold
(FLAG-2) needs to specify whether it is on the `max_relative_error`
field or on a normalized score.

**§2.3 phase 4 (B1 envelope assertion).** The stated form
`|Π_realized − K̂·σ_T| / |K̂·σ_T| ≤ 0.35` is dimensionally a relative
error of realized strip P&L against the linearized target. It is
**not** what the shipped verifier computes (see FLAG-1). The shipped
form is preferable on two grounds: (i) denominator stability (peak of
centered strip is monotone non-zero by construction once the strip
is non-degenerate), and (ii) constant-offset invariance (the LP
collateral floor at S_0 is absorbed). Recommend B1 plan adopt the
verifier's exact form. As σ_T → 0 the spec's form has a denominator
collapse; the verifier's form does not (peak of centered strip remains
strictly positive in the convex span).

## Anti-fishing rigor on the 5pp margin (§2.1 HALT trigger)

The 5pp margin is the only quantitative decision threshold in the
master spec that drives a verdict (KEEP vs REPLACE). It appears in
§2.1 HALT-triggers bullet 2 but does NOT appear in §5 pin coverage.
This is structurally identical to the κ-removal anti-fishing pattern
caught in Stage-2 (verdict memo §4.4 / `feedback_post_hoc_fit_anti_fishing_pattern.md`
case study): a numeric threshold introduced mid-spec, not pre-pinned,
adjustable post-hoc to flip a verdict.

Two defenses:

1. The §2.1 prose says "Pre-pinned BEFORE the comparison table is
   built (anti-fishing per §1.1)." This is the *right intent* but
   intent without pin enforcement is exactly what the feedback file
   warns against.
2. The 5pp value itself is mathematically defensible: against a
   metric whose theoretical floor is ~33% and empirical achievement
   is ~30% (types.py:66-69), 5pp absolute (= 15-17% relative) is
   neither trivial nor obviously gameable.

Required fix: add P-A1.4 to §5 pin table making the 5pp threshold
content-addressed in this master spec v0.1; any post-hoc adjustment
requires CORRECTIONS-α and a fresh RC+MQ Wave-1 review on the master
spec, which would trigger §6.4 BLOCK-routing escalation.

Without P-A1.4 the spec passes scope-and-gate review but leaves an
anti-fishing hole that a future plan author could walk through. With
P-A1.4 the spec is fully locked.

---

*End of MQ verdict. Wave-1 plan-time, master-spec scope. Dispatched
independently of RC per §6.1 Delphi independence safeguard.*
