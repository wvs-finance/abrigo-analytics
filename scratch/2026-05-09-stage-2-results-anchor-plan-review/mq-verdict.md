# MQ Verdict — Stage-2 Results Anchor Plan Review

**Plan:** `docs/plans/2026-05-09-stage-2-results-anchor.md` v0.1
**Auditor:** Model QA Specialist
**Date:** 2026-05-08

## Verdict: **ACCEPT_WITH_FLAGS**

The plan faithfully scopes STAGE_2_RESULTS.md as a math↔code provenance anchor over the frozen HEAD `9fd92e5`, enforces the 4-part citation contract, preserves HALT-on-flip semantics, and bans magnitude promises. The 10 methodology dimensions are largely satisfied with three FLAGs and one near-BLOCK on count arithmetic.

---

## Dimension-by-dimension findings

### D1 — Document role faithful: **PASS**
L12, L113, L311–313, L22 explicitly cap the doc as anchor-only, freeze-pinned, no auto-update, no new claims. Out-of-scope clause at L22 ("introducing any new claim... magnitude promises... Stage-3 implementation work") is methodologically correct.

### D2 — 29 §2 entry count: **FLAG-1 (arithmetic-correct, but mislabeled in subtotal)**
Task 1.2 enumerates: §2.A (8 entries: A.1–A.8), §2.B (5 entries: B.1–B.5), §2.C (8 entries: C.1–C.8), §2.D (8 entries: D.1–D.8). Sum = 8+5+8+8 = **29**. Self-review checklist L324 confirms "8 primitives + 5 pins + 8 forward-fix claims + 8 artifacts = 29." ✓

**However**: §2.A contains heterogeneous entries — A.1–A.5 are Eq. (6)/(7)/(8)/(10)/(11) closed forms; A.6–A.8 are §6/§10/§11 references. The user brief decomposition was "8 primitives (eqs. 6-11, §6, §10)" — A.8 ("§11") is included but the brief only listed §6 and §10 explicitly. Recommend TW brief either (a) drop A.8 to align with brief's "§6, §10" or (b) flag the extension. **FLAG-1**: L138 includes `§2.A.8 — §11 — C2 reference` not enumerated in user brief's primitive list. Either prune or document as scope extension.

### D3 — Citation format rigor: **PASS**
Task 1.3 (L170–177) locks the 4-part format: claim verbatim, post-cycle form, code pointer (`file:line` + pytest name — both required, either missing → MQ BLOCK), artifact pointer (full sha256). The "either missing → MQ BLOCK in Phase 3" enforcement clause (L176) is methodologically correct — no degradation path to a weaker citation.

### D4 — §4 anti-fishing case-study framing: **FLAG-2**
L117–120 lists §4.1/§4.2/§4.3 as worked examples for Stage-3 implementers. Task 1.4 (L181–187) defines the case-study format with five required components ending in "lesson for Stage-3 implementers — one sentence, no magnitude promises." Framing is **not** "bug fixes" — good. **However**, the format requires "pre-fix claim" and "fix applied" but does not explicitly require the **detection heuristic** (i.e., what early signal would have caught the pathology). User-brief dimension D4 specifies "detection heuristics retained." **FLAG-2**: Task 1.4 missing explicit "detection heuristic" bullet between (b) pathology and (c) fix applied. Recommend inserting a 6th required component.

### D5 — §6 anti-fishing posture (no magnitude promises): **PASS (strong)**
Task 1.5 (L191–198) enumerates the six Stage-3 hand-off bullets explicitly. L197 — "Stage-2 Z = 4453–4922 COP/mo magnitudes are synthetic and certify only sign; Stage-3 must NOT inherit these as magnitude predictions" — is exactly the required posture. L200 reinforces: "must NOT promise that 'real data will scale up,' 'magnitudes will increase,' or any equivalent." Anti-fishing §4 (L314) repeats the constraint. Triple-locked.

### D6 — HALT-on-flip preservation: **PASS**
L154 (§2.C.5) "C3 ELPD ranking + INDISTINGUISHABLE verdict + HALT-on-flip preservation" is enumerated as a frozen claim. L198 §6 invariant: "Stage-2 INDISTINGUISHABLE revenue-form verdict (C3) is a HALT-on-flip preservation; Stage-3 must re-run on real data and respect the HALT semantic." Anti-fishing §5 (L315): "C3 INDISTINGUISHABLE / HALT-on-flip semantic must be preserved as a HALT instruction for Stage-3, not softened to a recommendation." Not retroactively softened.

### D7 — Reproducibility certificate (§5): **PASS**
Task 0.3 (L92–96) pins the two sha256 anchors (`Z_cap_pinned.json::audit_block` → `1fb1f7a4...`; `gate_verdict.json::audit_block` → `4da660b5...`) from authoritative emit artifacts. Verification protocol via `python -c "import json; ..."` and HALT-on-divergence is correct. L316: full sha256 in §5, truncation only in §2 with consistent tail.

### D8 — 8-row verification matrix: **PASS with FLAG-3**
Task 1.6 (L206–215) provides the matrix covering Phase 1 / Phase 2 / Phase 3 across 8 claim-classes. Coverage maps to §2.A.1–.5, §2.A.6–.8, §2.B.1, §2.B.2, §2.B.3–.5, §2.C.1–.8, §2.D.1–.8, and §5 anchors. **FLAG-3**: Row 6 ("C1/C2/C3/C4 forward-fix claims") collapses 8 §2.C entries into one row — MQ Phase-3 verification per claim risks under-granularity. Recommend RC/MQ briefs (L269–270) explicitly enumerate per-§2.C subclaim verdicts to avoid roll-up masking.

### D9 — No spec drift: **PASS**
L22 out-of-scope; L311 "STAGE_2_RESULTS.md is a results anchor; it CANNOT introduce any claim not already in spec / PRIMITIVES.md / SaaS note / code at HEAD `9fd92e5`." STAGE_2_RESULTS is read-only with respect to upstream. CLAUDE.md update at L298 is gated as "Optional; foreground decides" with separate commit — no covert spec amendment vector.

### D10 — 3-wave HALT semantics: **PASS**
Task 3.3 Step 2 (L282): "If Wave-2 still has BLOCKs, dispatch one more CORRECTIONS pass; if Wave-3 still has BLOCKs, HALT and surface to user." Cap at Wave-3 with explicit HALT — correct.

---

## Summary table

| # | Dimension | Verdict |
|---|---|---|
| 1 | Document role faithful | PASS |
| 2 | 29 §2 entry enumeration | FLAG-1 (A.8 scope extension) |
| 3 | Citation format rigor | PASS |
| 4 | §4 case-study framing | FLAG-2 (missing detection heuristic) |
| 5 | §6 no magnitude promises | PASS |
| 6 | HALT-on-flip preserved | PASS |
| 7 | §5 reproducibility cert | PASS |
| 8 | 8-row verification matrix | FLAG-3 (row-6 granularity) |
| 9 | No spec drift | PASS |
| 10 | 3-wave HALT semantics | PASS |

## Recommended remediations (non-blocking)

- **FLAG-1**: At Task 1.2 §2.A, either prune §2.A.8 (§11) or add a one-line note that §11 is included as a C2-adjacent reference beyond the user-brief enumeration.
- **FLAG-2**: Insert in Task 1.4 a required bullet: "Detection heuristic — what early signal (test, sanity check, dimensional analysis) would have caught the pathology pre-merge."
- **FLAG-3**: In Task 3.1 Step 2, require MQ Wave-1 brief to emit per-§2.C.{1..8} verdicts, not a single aggregate verdict.

**Final verdict: ACCEPT_WITH_FLAGS.** The three FLAGs are documentation-quality refinements; none invalidate the structure pin or the anti-fishing posture. Plan is methodologically sound to dispatch.
