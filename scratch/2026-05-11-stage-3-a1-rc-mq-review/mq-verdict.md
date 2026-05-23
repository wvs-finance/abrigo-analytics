# MQ verdict — A1 plan v0.1
**Reviewer:** Math Quality (MQ)
**Plan under review:** docs/plans/2026-05-11-stage-3-a1-panoptic-restrategy.md
**Review wave:** Wave-1 plan-time (per master spec §6.1)
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

## Executive summary

The plan is mathematically coherent on the core architecture: the
`StrategyAdapter` Protocol + `NormalizedEnvelopeScore` discriminated by a
`comparability_proof` enum is the correct structural response to master-spec
MQ-FLAG-3 (§2.1 phase 2 caveat). The TP1 fixture is dimensionally consistent
with the R1 anchor (σ₀ = S₀²·ε²/8 = 4000²·0.1²/8 = 20000.0, verified
numerically) and `k_star = 4687.94` matches `Z_cap_pinned.json::Z_cop_per_month
= 4687.942347178384` to 4 sig figs.

Five FLAGs land — none BLOCK, but they expose places where the plan's task
graph does not author what its types claim to support, plus boundary-handling
and verdict-tie semantics that are mathematically ill-defined as written.
Disposition is plan-author inline in v0.2; no BLOCK re-review needed.

## Findings (BLOCK / FLAG / NIT)

### MQ-FLAG-A1.1 — `primitive_variant` proof option is not actually authorable inside A1 scope (Material)

Task 2.1 declares the enum `comparability_proof: Literal["tiled_body",
"primitive_variant", "normalized_score"]`. Task 2.2 says "for non-reverse-IC
candidates, the adapter MUST surface the `comparability_proof` choice ... as a
constructor argument" but NO TASK in Phase 2 authors a primitive-specific
verifier variant. Task 3.1 HALT-trigger ("winning candidate's
`comparability_proof` is `"primitive_variant"` AND the primitive-specific
verifier variant was never authored → HALT") confirms this gap is known but
treats it as a runtime emergency rather than a design hole.

Mathematically: master-spec §2.1 phase 2 option (b) requires "a
primitive-specific verifier variant is introduced AND shown numerically
equivalent on a reverse-IC baseline." Plan does not allocate task scope to
either authoring the variant or proving equivalence. As a result, any
candidate whose only viable proof is `primitive_variant` is forced into
either (a) tiled-body — which the candidate may not admit — or (c)
normalized score — which has its own validity question (MQ-FLAG-A1.2).

**Disposition request:** Either add a Task 2.5 "Author primitive-specific
verifier variant + numerical equivalence test on reverse-IC baseline" with
explicit scope language, OR explicitly scope-out `primitive_variant` from
A1 (declare in §1 that only `tiled_body` and `normalized_score` are
in-scope proofs for A1, and `primitive_variant` candidates HALT at Phase 2
rather than Phase 3).

### MQ-FLAG-A1.2 — `normalized_score` proof option is referenced but never mathematically defined in the plan (Material)

Master-spec §2.1 phase 2 option (c) gives an example formula
`max_relative_error / envelope_at_zero_strip`. The plan's Task 2.1 brief
enumerates `"normalized_score"` as a permitted literal but does NOT pin
which normalization formula adapters using this proof must compute, nor
how `EnvelopeComparator` should compare a `normalized_score`-proof
candidate against a `tiled_body`-proof baseline (the baseline's
`max_relative_error` is on a different scale than a normalized score).

Currently `EnvelopeComparator` "sorts by `max_relative_error` ascending"
(Task 2.3). If candidate A reports `max_relative_error = 0.28` under
`tiled_body` and candidate B reports `0.15` under `normalized_score`, the
comparator ranks B above A — but this is comparing apples to apples only
if the normalized score has the same units as `max_relative_error`. The
plan does not enforce this.

**Disposition request:** Pin the normalized-score formula in Task 2.1
acceptance, and require `EnvelopeComparator` to refuse mixed-proof
rankings (or to apply the normalization to ALL candidates uniformly so
the comparator field is dimensionally consistent across proofs).

### MQ-FLAG-A1.3 — Verdict boundary at exactly 5.0 pp is ambiguous (Material)

Task 3.1 reads:
- "KEEP verdict iff `envelope_delta_vs_ironcondor_pp < 5.0` (strict)."
- "REPLACE verdict iff there exists a candidate with
  `envelope_delta_vs_ironcondor_pp >= 5.0`."

Master spec §2.1 HALT-triggers reads: "candidate X must beat the existing
IronCondor by ≥ 5 percentage points ... Anything inside that margin →
KEEP verdict." Spec uses `≥ 5pp → REPLACE`, `< 5pp → KEEP` (closed-above
boundary). Plan uses `< 5.0 → KEEP`, `≥ 5.0 → REPLACE`. **These agree.**
The boundary at exactly 5.0pp goes to REPLACE under both. ✓

HOWEVER: the plan says KEEP iff `envelope_delta_vs_ironcondor_pp < 5.0`
which presupposes there is a single dominant candidate. If the BEST
candidate has delta = 4.999, KEEP holds; if it has delta = 5.0, REPLACE
holds. Strict / non-strict matches spec at the strict-equality boundary,
so this is internally consistent. **The flag is on a different ambiguity:**
the plan does NOT specify which `envelope_delta_vs_ironcondor_pp` to test
when there are multiple candidates. Is it the BEST candidate's delta (max
delta)? The mean? Any candidate above threshold? Task 3.1 implies "exists
≥ 5pp" → REPLACE, but then Task 3.1 says "Multiple candidates tie within
the threshold → HALT" — this only covers ties WITHIN ≤ 5pp, not the case
where multiple candidates separately CROSS 5pp.

**Disposition request:** Add to Task 3.1 acceptance: "When multiple
candidates have `envelope_delta_vs_ironcondor_pp ≥ 5.0`, the winning
candidate is the one with the LARGEST delta; ties at the largest delta
(within `1e-9` absolute) → HALT with user-enumerated tie-break."

### MQ-FLAG-A1.4 — `envelope_delta_vs_ironcondor_pp` SIGN convention is undocumented (Material)

Task 3.1 JSON spec says: `envelope_delta_vs_ironcondor_pp: <signed float,
positive = candidate beats IronCondor>`. But `max_relative_error` is a
NON-NEGATIVE quantity where LOWER = BETTER. "Beating" means
`candidate.max_relative_error < ironcondor.max_relative_error`, i.e. the
delta `(ironcondor − candidate)` is positive when the candidate wins. The
plan does not say which direction the subtraction goes; the KEEP/REPLACE
logic then mis-reads under reversed sign.

Combined with MQ-FLAG-A1.3: the spec text "candidate must BEAT IronCondor
by ≥ 5pp" only makes sense if `envelope_delta_vs_ironcondor_pp =
(ironcondor_envelope - candidate_envelope) × 100`. Plan needs to pin this
formula explicitly.

**Disposition request:** Add to Task 3.1: `envelope_delta_vs_ironcondor_pp
:= (ironcondor.max_relative_error − candidate.max_relative_error) × 100`,
units = percentage points (NOT percent of IronCondor). Positive = candidate
replicates more tightly than IronCondor.

### MQ-FLAG-A1.5 — `ComparabilityProofMissingError` catches absent proofs but does NOT catch FALSE proofs (Material)

Task 2.3 says the comparator raises `ComparabilityProofMissingError` if
any adapter is missing its `comparability_proof` field. This catches the
LIAR-OF-OMISSION case but not the LIAR-OF-COMMISSION case: an adapter can
declare `comparability_proof = "tiled_body"` while its built strip
violates the tiled-body geometry (Π_strip(S_0) ≠ 0). The shipped
`assert_long_vol_signature` includes a check that Π_strip(S_0) ≈ 0 within
`1e-9 * max(1.0, s_0)`, which is exactly the tiled-body check — but Task
2.3 does NOT call `assert_long_vol_signature` on each adapter's strip
before comparing.

Consequence: a candidate adapter that mis-declares `tiled_body` proof can
produce a numerically smaller `max_relative_error` than the baseline
purely by violating the centering assumption, and `EnvelopeComparator`
will rank it as winning.

**Disposition request:** Add to Task 2.3 acceptance: "For each adapter
declaring `comparability_proof = "tiled_body"`, comparator runs
`assert_long_vol_signature` on the built strip before computing the
envelope; failure of `assert_long_vol_signature` → raise
`ComparabilityProofFalseError` (new) with the failing primitive_id." This
is the post-hoc-fishing guard against silent comparability violations.

### MQ-NIT-A1.1 — Reverse-IC baseline re-export is mathematically the right reference (Info)

Task 2.2: "Existing reverse-IC adapter included as the baseline
(re-exports the existing `cohort_5_strip.build_strip` behavior)." Verified
by reading `geometry.StripBuilder`: the existing builder, when consumed
by the shipped `CarrMadanEnvelopeVerifier` on the TP1 fixture, produces
the ~28–33% envelope figure cited in `types.py:60-72` as the empirical
baseline. Re-exporting `build_strip` IS the right reference. ✓ NIT only:
the plan should pin a specific numerical baseline expectation (e.g.,
"reverse-IC baseline at TP1 produces `max_relative_error ∈ [0.27, 0.33]`")
in Task 2.4 acceptance so that any drift in the baseline number itself
HALTs before downstream comparison.

### MQ-NIT-A1.2 — Comparator sort-stability under floating-point ties (Info)

Task 2.3 says sort by `max_relative_error` ascending. For two candidates
producing identical envelopes (e.g., a numerical coincidence at TP1),
Python's `sorted` is stable on insertion order, but that means the
"winner" depends on adapter-tuple ordering — which is decided by Task
1.2's filtered-set ordering. This is a SILENT determinism dependency.

**Disposition request:** Pin sort key as
`(max_relative_error, primitive_id)` lexicographic, so ties resolve
deterministically by primitive_id (alphabetical) rather than by upstream
filter ordering.

## Method-choice soundness audit

| Method choice | Sound? | Notes |
|---|---|---|
| `StrategyAdapter` Protocol returning `IronCondorStrip` | ✓ | Re-using the existing frozen-dc type forces every candidate through the strip's structural invariants (Pin S1–S4). |
| `comparability_proof` 3-way enum | ✓ exhaustive | These three options ARE exhaustive for cross-primitive comparability against a reverse-IC tiled-body baseline: either the candidate geometry inherently centers at S_0 (tiled), or a new verifier is built (variant), or the metric itself is normalized to a scale-invariant ratio (normalized_score). No 4th category exists in the master-spec disposition. |
| Single TP1 fixture | ✓ (with scope guard) | Task 2.4 pins `(S_0=4000.0, sigma_0=20000.0, k_star=4687.94)` ONLY — no smuggled-in robustness sweeps. Master-spec §8 limitation 2 explicitly defers multi-fixture work; plan honors. |
| `EnvelopeComparator` sort ascending by `max_relative_error` | ✓ direction-correct, ✗ tie-handling | Lower envelope = tighter replication. But see MQ-NIT-A1.2 on stability and MQ-FLAG-A1.2 on cross-proof comparability. |
| Reverse-IC baseline re-export | ✓ | Re-uses `build_strip` exactly; produces the documented ~28-33% reference envelope. |
| TP1 σ₀ anchor consistency | ✓ verified | S_0²·ε²/8 = 4000²·0.01/8 = 20000.0 exactly. R1 asymptotic identity holds. |
| TP1 k_star value | ✓ verified | `Z_cap_pinned.json::Z_cop_per_month = 4687.942347178384`; plan's 4687.94 rounds correctly to 4 sig figs. |

## Pin coverage audit (table)

| Master-spec pin | Plan task | Coverage verdict |
|---|---|---|
| P-A1.1 (comparison-table completeness) | Task 1.1 + 1.2 | ✓ covered; Wave-2 RC enforces. |
| P-A1.2 (envelope evaluation reproducible) | Task 2.4 + audit_block in 3.1 | ✓ covered; cross-checked at ≥1e-9. |
| P-A1.3 (verdict citation-backed) | Task 3.1 `rationale_citation` | ✓ covered. |
| P-A1.4 (5pp threshold pre-pinned) | Task 3.1 KEEP/REPLACE logic | ✓ threshold honored, but boundary semantics need MQ-FLAG-A1.3 fix and sign-convention MQ-FLAG-A1.4 fix. |
| **(missing)** Numerical-baseline expectation for reverse-IC at TP1 | (not pinned) | MQ-NIT-A1.1 — recommend adding. |
| **(missing)** Tiled-body geometry runtime check on declared `tiled_body` proofs | (not pinned) | MQ-FLAG-A1.5 — recommend adding. |
| **(missing)** Comparator sort tie-break deterministic key | (not pinned) | MQ-NIT-A1.2 — recommend adding. |
| **(missing)** `primitive_variant` author-task or scope-out | (not pinned) | MQ-FLAG-A1.1 — recommend adding. |
| **(missing)** `normalized_score` formula + cross-proof comparison rule | (not pinned) | MQ-FLAG-A1.2 — recommend adding. |

## Comparability-proof architecture audit

The `(tiled_body | primitive_variant | normalized_score)` triad maps
1:1 to master-spec §2.1 phase 2 options (a)/(b)/(c). The triad IS
exhaustive in the sense that any non-reverse-IC primitive whose envelope
is to be compared against the reverse-IC baseline must satisfy at least
one of these three conditions, otherwise it would be a bare-reuse comparison
which the master spec bans as a HALT trigger.

What the plan does NOT do is enforce that the declared proof is actually
VALID. The runtime `ComparabilityProofMissingError` catches absent proof;
it does not catch false proof (MQ-FLAG-A1.5). This is the single most
important gap from a soundness standpoint: the comparability architecture
is structurally correct but the runtime gate is permissive.

The `primitive_variant` lane is the most dangerous of the three because
(unlike `tiled_body`, which has a clear runtime check via
`assert_long_vol_signature`, and unlike `normalized_score`, which is a
metric transformation) it requires authoring NEW VERIFIER CODE. The plan
references this lane but does not allocate task scope to it
(MQ-FLAG-A1.1).

## Anti-fishing rigor on the 5pp pin

The 5pp threshold (master spec §5 Pin P-A1.4) is content-addressed in the
JSON via the `p_a1_4_threshold_pp: 5.0` field, which is the right anti-
fishing pattern: any post-comparison adjustment of the threshold becomes
visible in `git diff` against the master-spec-pinned constant. Plan
honors this in Task 3.1 acceptance.

Plan §11 reserves CORRECTIONS-α space and §9 routes Wave-1/Wave-2 BLOCK
back to the master spec rather than silently adjusting in-plan; this
preserves the pre-pinning invariant.

The plan does NOT, however, pre-commit to the SIGN of the
`envelope_delta_vs_ironcondor_pp` field (MQ-FLAG-A1.4), which means the
direction of the inequality could in principle be silently swapped at
emit time. Fixing MQ-FLAG-A1.4 closes this anti-fishing surface.

The single-fixture limitation (master-spec §8 limitation 2) is the
biggest residual anti-fishing risk because a candidate could happen to
beat the baseline at TP1 but not at any other fixture in the 24-bracket
family. This is explicitly out of A1 v1 scope per the master spec, and
the verdict JSON's `envelope_at_tp1` field name makes the limitation
explicit in the artifact itself — good. No FLAG, but worth noting as a
Wave-2 carry-forward when the deferred robustness pass eventually lands.

---

*End MQ verdict — Wave-1 plan-time review, A1 plan v0.1.*
