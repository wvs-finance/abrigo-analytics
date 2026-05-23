# MQ Methodology Audit — STAGE_2_RESULTS.md

**Auditor:** Model QA Specialist (independent)
**Target:** `notes/STAGE_2_RESULTS.md` (761 lines, frozen at HEAD `9fd92e5`)
**Plan:** `docs/plans/2026-05-09-stage-2-results-anchor.md` v0.2
**Authoritative inputs verified:** `notes/PRIMITIVES.md` (428 lines), spec v1.2.1, cohort plans v0.3/v0.4, audit verdicts.

---

## Verdict: **ACCEPT_WITH_FLAGS**

Default REJECT posture lifted. All ten audit dimensions are substantively satisfied. Three minor FLAGs remain — none rise to BLOCK; none loosen pins, add candidates, relax thresholds, or introduce upstream claims.

---

## Per-dimension findings

### D1. §2.A primitives correctly cited — PASS
Verified verbatim against PRIMITIVES.md:
- §2.A.1 ↔ eq. (6) ll. 186–191 ✓
- §2.A.2 ↔ eq. (7) ll. 204–208 ✓
- §2.A.3 ↔ eq. (8) ll. 212–215 ✓ (post-cycle σ₀ = (X̄/Ȳ)²·ε²/8 is correct algebraic inversion)
- §2.A.4 ↔ eq. (10) ll. 229–233 ✓ (verbatim form `4/((X̄/Ȳ)·ε(σ_T)) · Σ q_t·f_t/(X/Y)_t² < 0`)
- §2.A.5 ↔ eq. (11) ll. 243–247 ✓
- §2.A.7 ↔ eq. (17) `K̂ = K⋆/(2√σ₀)` line 316 ✓
- §2.A.8 ↔ eq. (20) ll. 343–361, N=3 / 12 legs ✓

### D2. §2.B math pins — PASS
- M1 (l. 178–180): floor at sampler-Callable + Value `__post_init__` ✓
- M2 (l. 193–194): L¹ < 10⁻³·κ enforced at `SoftplusRegularizer.__post_init__` ✓
- M3 (l. 209–211): $7.1495 closed form with `math.isclose` tolerance ✓
- M4 (l. 226–228): v1.0 → v1.1 schema bump correctly labeled "breaking-change semver" (NOT additive) ✓
- M5 (l. 240–245): single TRM-pinned (X̄/Ȳ); `[4200, 3800, 4200]` are sinusoidal path **values**, NOT distinct means ✓ (correct orientation per prompt)

### D3. §2.C forward-fix claims — PASS
- C1 marginalization: 3 discrete latents named, Property #7 cited ✓
- C2: 24-cell per spec §5.2 (3 tiers × 2 α × 2 cache × 2 κ), NOT 5-cell (ε, ω) ✓
- C2 Δ_analytic = −1.02e-8 reconciliation: β·κ ≈ 2.33e4 saturation + cos²-cancellation ✓
- C3 S_t = (1−λ)^t with Beta(4.5, 95.5) per spec v1.2.1 §6.1 ✓
- C3 ELPD INDISTINGUISHABLE @ Δelpd/SE = 1.67 + HALT-on-flip preserved ✓
- C4 π(t) closed form: `K⋆·ε²·(X̄/Ȳ)²·(4ωt·cos(4ωt) − sin(4ωt))/(64·ω·√σ₀·t²)` — NO 1/κ, κ ∉ free_symbols ✓
- C4 perpetual identity sympy.S.Zero + numerical residual 6.31e-9 ✓
- C4 5-TP magnitudes Z = 4453–4922 COP/mo ✓

### D4. §4 case-study framing — PASS
Three case studies framed as anti-fishing remediations, each cites a named detection heuristic:
- §4.1: tautological-identity audit + derivation-anchor citation check
- §4.2: free-symbol audit
- §4.3: sign-target retro-fit audit + derivation-anchor citation check

### D5. §5 reproducibility certificate — PASS
sha256 full-strings for `Z_cap_pinned.json` (l. 586) and `gate_verdict.json` (l. 588) carried verbatim from `audit_block` fields, with re-hash live confirmation in §0 (ll. 26–30). Verification protocol (ll. 597–614) describes byte-for-byte equality and freeze-pin via `git merge-base`. Authoritative.

### D6. §6 Stage-3 hand-off — PASS
10 enumerated assumptions with explicit "**No magnitude promises.**" header (l. 622). Item 5 (ll. 641–644) prohibits magnitude inheritance.

### D7. No new claims introduced — PASS
Document is read-only with respect to upstream. No fresh derivations, no new pins.

### D8. HALT-on-flip preserved — PASS
§2.C.5 (l. 343, 355) and §6 item 6 (ll. 645–649) both preserve.

### D9. §2.C internal cross-references — PASS
§2.C entries cross-reference §4 case studies; spec v1.2.1 §6.1 cited at §2.C.4.

### D10. Anti-fishing posture — PASS
No pin loosened, no candidate added, no threshold relaxed. Strictly tightening.

---

## FLAGs (non-blocking)

**FLAG-1 — §2.A.6 "large-t asymptotic" mis-label.** Line 136: claims `σ_T = (X̄/Ȳ)²·ε²/8` is the §6 "large-t asymptotic." PRIMITIVES.md §6 presents this as the algebraic inverse of eq. (8), not as a large-t limit. Mathematically equivalent; nomenclature only. *Recommend:* drop "large-t asymptotic" or replace with "closed-form inversion of eq. (8)."

**FLAG-2 — §2.D.1 schema label inconsistency.** Row §2.D.1 (l. 421) labels `synthetic_tau_t/` as "v1.0 partitioned by tier_id" while §2.B.4 (l. 227) and row §2.D.7 explicitly cite the v1.0 → v1.1 schema bump under CLOSE Phase-4. If only `Z_cap_pinned.json` was bumped to v1.1 and synthetic_tau_t legitimately stays at v1.0, the table is correct — but this should be stated explicitly to avoid reader confusion. *Recommend:* clarify scope of Phase-4 bump in §2.B.4 or §2.D.1.

**FLAG-3 — §4.1 detection-heuristic naming.** "Tautological-identity audit" is defensible (the marginalization-vs-Gibbs equivalence is an identity that the audit surfaced), but the v0.3 pathology was primarily a *sampler-mixing failure* (ESS=38). The detection heuristic that *first* caught it could equally be named "ESS-floor sampler diagnostic." *Recommend:* either keep current label and add a parenthetical clarifier, or add the sampler-diagnostic as a co-heuristic.

---

## Disposition

The document satisfies its plan v0.2 contract. The three FLAGs are stylistic / nomenclature-level and do not affect the substantive math, citations, or anti-fishing posture. **ACCEPT_WITH_FLAGS** — Stage-3 hand-off unblocked; FLAGs may be addressed in a cosmetic patch or carried forward as known editorial notes.
