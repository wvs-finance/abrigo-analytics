# MQ verdict v2 — STAGE_2_RESULTS.md (rewritten)

**Auditor:** Model QA Specialist (independent)
**Doc audited:** `notes/STAGE_2_RESULTS.md` (259 lines, rewritten v2)
**Plan:** `docs/plans/2026-05-09-stage-2-results-anchor.md` v0.3 Phase 3 MQ
**Default:** REJECT.

## Verdict: **ACCEPT_WITH_FLAGS**

The rewrite cleanly inherits the PRIMITIVES → SaaS_Builders pattern, eliminates
the v1.1 citation-registry framing, and discharges every R1–R8 / TODO-COHORT-N
checkpoint with traceable provenance. Math content is correct on all
verifiable items. Two minor FLAGs only — neither blocks acceptance.

## Checkpoint pass/fail (13 items)

| # | Checkpoint | Status | Evidence |
|---|---|---|---|
| 1 | R1 σ₀ closed form + canonical numeric | **PASS** | L46–56 boxed; verified `4000² · 0.01 / 8 = 20000` (sympy/python exact). |
| 2 | R2 π(t) closed form + chain + free_symbols | **PASS** | L70–78 boxed; chain (6)→(8)→(10)→§10→§15 cited L66–68; explicit `κ ∉ free_symbols(π)` L78. |
| 3 | R2 anti-fishing aside (one paragraph, not 6-part) | **PASS** | L80–87 single paragraph; records 1/κ removal + (X̄/Ȳ)² restoration + M2 re-pin from `∂\|π\|/∂κ < 0` to `∂\|π\|/∂(X̄/Ȳ) > 0`. |
| 4 | R3 perpetual identity sympy + numerical residual | **PASS** | L93 `simplify(π − dΠ_lin/dt) = 0`; L100–101 `≤ 6.31e-9` on 5000-pt grid. |
| 5 | R4 24-bracket Cartesian product, \|B\|=24, sign empirics | **PASS** | L109–112 boxed; spec §5.2 lines 383–388 verified; "24/24 PASS each" L116–117. |
| 6 | R5 marginalization equivalence | **PASS** | L125–127 LSE form; L130–133 explicit "sum-out is exact, not approximate" with §5.4 cross-ref justifying the factorization. |
| 7 | TODO-COHORT-N closures with classifications | **PASS** | Table L140–145 + §3.1–§3.4: COHORT-1 DEFERRED, COHORT-2 CLOSED(R6), COHORT-3 INDISTINGUISHABLE+pin(R7), COHORT-4 CLOSED(R2). All four labels match the brief. |
| 8 | R6 softplus + M2 tightness, β-minimal | **PASS** | L160–164 boxed; tightness `< 10⁻³·κ` matches spec; "smallest β satisfying" L166. |
| 9 | R7 Υ_t three candidates, Δelpd/SE = 1.67, det+churn pin, HALT-on-flip | **PASS** | L173–186; verdict memo cross-check confirms `Δelpd/SE = 1.67`, `Beta(4.5, 95.5)`. HALT-on-flip preserved verbatim L183–184. |
| 10 | R8 Z_cap closed form + pinned value + per-TP CI note | **PASS** | L200–204 boxed; `Z_cap = 4,687.94 COP/mo, CI [168.17, 14606.14]` matches verdict memo L387, L416 ("TP1–TP3 share [168.17, 14606.14]"); monotonic-with-FX-bracket caveat correctly stated L208–209. |
| 11 | §5 Stage-3 open items (math only, no eng checklist) | **PASS** | L216–235: real-data conditioning, stochastic FX (PRIMITIVES §15 #2), per-tier θ_k (§5.4), hierarchical C3 pooling, Weibull falsification, on-chain Panoptic strip (PRIMITIVES §11). All math forms; zero engineering tasks. |
| 12 | Anti-fishing posture preserved | **PASS** | Freeze-pin `9fd92e5` recorded L21, L239; HALT-on-flip preserved L183–184; "no magnitude claims" L23–24, L207, L214. |
| 13 | No silent re-derivations / full provenance | **PASS** | Every R-tag traces (R1→(8); R2→(6),(8),(10),§10,§15; R3→(16),(14); R4→spec §5.2; R5→§5.4; R6→PRIMITIVES §15 item 3; R7→spec §9, v1.2.1 §6.1; R8→PRIMITIVES (15), pitch S5). |

## FLAGs (non-blocking)

**FLAG-1 (Minor, §3.4 cross-ref pointer wording).** L189: "Closed at §2.2;
cross-reference (R2)." Cross-reference is fine, but the reference table at L145
labels TODO-COHORT-4 R-tag as "R2", while §2.2's tag-line at L74 is `\tag{R2}`.
Consistent — no fix required, but note the table relies on readers parsing
"R-tag" column as "the R-tag where closure is recorded" rather than "a
TODO-specific R-tag". Cosmetic.

**FLAG-2 (Minor, §6 sha tail abbreviation).** L245–246: two `audit_block`
hashes given as full sha (R8 and gate_verdict), two as `prefix…suffix` tails
(`revenue_form_verdict.json`, `_AUDIT.json`). Mixed presentation. For a
reproducibility section, full shas for all four would be tighter; tails are
adequate for a supplementary anchor but slightly weaken the verification
claim. Recommend full shas in next pass; not blocking.

## Numerical / cross-doc verifications performed

- R1 canonical: `4000² · (0.1)² / 8 = 20000.0000…` ✓ (python).
- Spec §5.2 brackets: 3 tiers × 2 α × 2 h_cache × 2 κ = 24 ✓ (lines 383–388).
- Z_cap = 4,687.94 COP/mo, CI [168.17, 14606.14] ✓ (verdict memo L387, L416).
- Δelpd/SE = 1.67 < 2.0 ✓ (verdict memo L189).
- Beta(4.5, 95.5) re-pin ✓ (verdict memo L196, L282).
- Freeze-pin `9fd92e5` ✓ (matches plan v0.3).
- π magnitude correction (~99.99% of Z_cap, not "~5%") consistent with
  verdict memo MQ-FLAG-1 fix L415 — properly absent from the new doc (which
  makes no magnitude claim).

## Recommendation

**ACCEPT_WITH_FLAGS.** Wave-1 MQ pass cleared. Both flags are cosmetic /
presentational; neither warrants a Wave-1 rerun. Address FLAG-2 (sha
fullness) opportunistically in any follow-up commit; FLAG-1 needs no action.

The rewrite is the math-content record the plan v0.3 Phase 3 MQ brief
specified. Anti-fishing invariants intact, provenance dense, no
re-derivations, no checklist content.

---
**MQ Specialist** • 2026-05-09 • doc HEAD `9fd92e5`
