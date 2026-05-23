# MQ Verdict — Stage-3 B1 Foundry scaffolding (Plan v0.1)

**Reviewer role:** Math Quality (MQ)
**Plan under review:** `docs/plans/2026-05-11-stage-3-b1-foundry-scaffolding.md` v0.1
**Counterpart:** RC (Delphi-independent)
**Date:** 2026-05-11

**Bottom-line verdict:** **ACCEPT_WITH_FLAGS** — 0 BLOCK, 3 Material FLAG, 2 Cosmetic NIT. The envelope-formula pin, the 24-bracket factorization, the FX-path math anchor and the property-test bounds are mathematically sound. The plan is silent on three load-bearing degrees of freedom (time-grid pinning, σ_T mathematical-object disambiguation, forge-test verdict semantic at N/24 with N<2) that affect whether the Foundry test deterministically reproduces the envelope. These must land in v0.2 before Wave-2.

---

## §1 PASS findings (no action)

**(P1) Envelope-formula correctness (Task 1.2 + master §2.3 phase 4 + §9.1 MQ-FLAG-1).** The centered-strip / β-fit / peak-normalized form is the form actually shipped in `simulations/saas_builder/cohort_5_strip/replication.py:124–191` (`CarrMadanEnvelopeVerifier`). Reading the code line-by-line: floor = `strip_payoff(strip, s_0)` (line 171); centered = `v - floor` (line 172); β by closed-form least squares with intercept fixed at 0 (`_fit_scale`, lines 103–120, because Q(S_0)=0 and Π_centered(S_0)=0); residual = `|Π_centered − β·Q|`, peak-normalized by `max|Π_centered|` (lines 174–184). The known TP1 number `max_relative_error ≈ 0.2813` is exactly what `data/IronCondor_strip.STRIKES.md` line 25 reports (`2.8134e-01`). Task 1.2 asks the writer to walk through this; the formula is correctly named and the reference fixture matches. ✓

**(P2) FX-path generator math anchor (Task 2.1).** The plan reproduces PRIMITIVES eq. (6) verbatim: `(X/Y)_t = (1 + ε·(cos²(ωt) − 1/2))·X̄/Ȳ`. The Hypothesis property bound is correct under the standard real-cosine envelope: `cos²(ωt) ∈ [0,1]` so `cos²(ωt) − 1/2 ∈ [−1/2, +1/2]`, and `1 + ε·[−1/2, +1/2] = [1 − ε/2, 1 + ε/2]` for any real ε. The PRIMITIVES.md §5 constraint `0 < ε < 1` is preserved by the bracket family (ε is derived from σ_T via eq. (8), and the 24 brackets all live within the admissible band). ✓

**(P3) 24-bracket factorization (Task 2.2).** The plan asserts `len(brackets) == 24` and the factorization `3 × 2 × 2 × 2`. Cross-checked against Stage-2 spec `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` §5.2 lines 383–388 and STAGE_2_RESULTS.md §2.4 eq. (R4): `B₂₄ = {Pro, Max5x, Max20x} × {1.5, 2.0} × {low, high} × {nominal, doubled}` → |B₂₄| = 3·2·2·2 = 24. Identification of arms: tier=3, α_arm (TruncPareto α ∈ {1.5, 2.0}) =2, cache_regime (h_cache) =2, κ_arm (κ doubling) =2. ✓

**(P4) Anti-pattern callout (i).** "Re-derive the 35% tolerance from PRIMITIVES §12 row 1's 5%" is correctly flagged as forbidden. PRIMITIVES.md §12 row 1's 5% bound is the LP-fee envelope vs Δ^{(a_l)} (calibrated Mento/Uniswap V3 LP P&L), not the 3-condor finite strip envelope. The 35% floor is the theoretical max of a 3-piece piecewise-linear approximation of `x²` (`1 − 3·(1/3)² = 2/3 ≈ 33%`, padded to 35%) per `types.py:57–74`. The two objects have orthogonal anchors; the plan's anti-pattern guard is correct. ✓

**(P5) Anti-pattern callouts (ii), (iii).** "Silently relax the tolerance" and "reduce the 24-bracket family without master-spec amendment" are textbook anti-fishing guards. ✓

---

## §2 Material FLAGs (must land in v0.2)

**(MQ-FLAG-B1.1) σ_T contract conflates two distinct mathematical objects.** Plan Task 1.2 §"σ_T computation contract" says σ_T uses PRIMITIVES.md eq. (7): $\sigma_T = (1/T)\sum_{t=0}^{T}((X/Y)_t − \overline{X/Y})^2$. This is the **discrete realized-variance proxy** over a sampled FX path. But there is a SECOND σ_T expression living in Stage-2 R2/R3 derivation chain — the **closed-form path integral** $\sigma_T(t) = (\overline{X/Y})^2 ε^2 [1/8 + \sin(4ωt)/(32ωt)]$ which arises from substituting eq. (6) into eq. (7) and taking the continuous-time integral (this is the form that produces the R2 closed-form π(t) in STAGE_2_RESULTS.md §2.2). For the Foundry test, the realized P&L the contract computes is the strip's **discrete payoff at terminal $S_T$** vs the **σ_T evaluated at terminal T** — and these need a clear convention: does the Foundry test (a) sample (X/Y)_t on the time-grid and compute eq. (7) discretely, or (b) read σ_T from a closed-form path-integral cache? Per Stage-2 derivation purity, (a) is the one PRIMITIVES.md §6 eq. (7) actually defines; (b) is a Stage-2-internal closed form. Plan should explicitly state "Foundry test computes σ_T via eq. (7) discretely from the FX-path samples emitted in `fx_paths_24_brackets.json` — NOT from the Stage-2 closed-form path-integral expression." Without this, a Foundry implementer could plausibly choose (b) and silently drift.

**(MQ-FLAG-B1.2) Time-grid `n_points` under-specified at the contract boundary.** Plan §6 Task 2.2 JSON schema declares `time_grid: {t_start_months, t_end_months, n_points}` but pins no values. The σ_T discrete sum (eq. 7) is sensitive to n_points: at n=17 (replication.py default for the S_T strike grid — a DIFFERENT object) σ_T discretization error is meaningful; at n=5000 (cohort_4/pi_derivation.py:241 standard) discretization residual is ≤6.31e-9 per STAGE_2_RESULTS.md §2.3. The plan leaves this to the Foundry test, which means two implementations could legitimately disagree on σ_T to several percent — well within the 35% envelope, so the test would still pass, but the bracket-level numbers become non-reproducible. Plan should EITHER pin `n_points = 5000` in HANDOFF.md §3 (matching cohort_4 convention; eq. (7) is the same object), OR explicitly delegate "n_points is a forge-test choice; analytics-side fixture emits at n_points=5000 and Foundry MUST resample-or-consume identically" with a property test enforcing the round-trip. Either is fine; silence is not.

**(MQ-FLAG-B1.3) Forge-test verdict semantic is incomplete at 1/24 FAIL.** Master spec §2.3 exit-deliverable is "24/24 PASS at 35% envelope tolerance" (plan §7 Task 3.1 acceptance). Plan §9 HALT-routing says "FAIL on ≥ 2/24 brackets → HALT route to A1". This leaves **1/24 FAIL** as an undefined state: it is neither an exit (not 24/24) nor a HALT (not ≥ 2). Three possible semantics: (a) 1/24 FAIL is also HALT (exit is strict 24/24); (b) 1/24 FAIL triggers a SINGLE-bracket re-emit and re-test before HALT; (c) 1/24 FAIL is acceptable and exit is "≥ 23/24". Master spec wording (24/24) implies (a). Plan should make this explicit and align §9 HALT-routing with §7 Task 3.1 exit by lowering the HALT threshold to "≥ 1/24 FAIL". The current asymmetry is silent-fishing-shaped: a Foundry implementer who hits 1/24 FAIL has no documented route and may legitimately interpret "not HALT" as "proceed".

---

## §3 Cosmetic NITs (v0.2 nice-to-have)

**(MQ-NIT-B1.1) PRIMITIVES.md section number off-by-one in plan citations.** Plan §3, §5 Task 1.2, §6 Task 2.1 all cite "PRIMITIVES.md §6 eq. (6)" for the FX-path generator. PRIMITIVES.md §6 is "Variance proxy and ε↔σ_T inversion" (containing eq. 7); §5 is "Deterministic FX path generator" (containing eq. 6). The equation numbers are correct; the section numbers are off-by-one. Same off-by-one is present in the master spec (§2.3 phase 3, line 264) and likely propagated. Either the master spec is canonical and PRIMITIVES.md headings are stale, or PRIMITIVES.md is canonical and citations are wrong. Recommend either fixing the citations to "PRIMITIVES.md §5 eq. (6)" / "PRIMITIVES.md §6 eq. (7)" in HANDOFF.md, or filing a CORRECTIONS-α to renumber PRIMITIVES.md sections. Either way, do not let the off-by-one propagate into HANDOFF.md unchallenged.

**(MQ-NIT-B1.2) Cross-fixture audit-block drift.** Plan Task 2.2 emits `fx_paths_24_brackets.json` with its own audit_block, independent of `IronCondor_strip.json`'s audit_block. Mathematically the two fixtures are independent inputs to the Foundry test, so independent audit_blocks are correct. However, if A2 re-emits the strip (e.g., new K⋆-shift per MQ-FLAG-4 in master spec §9.1), the Foundry test must validate that the FX-paths fixture was generated against a strip whose audit_block matches the one Foundry is about to consume. Recommend HANDOFF.md §3 add a "strip_audit_block_parent" field inside the fx_paths JSON pointing at the IronCondor_strip.json audit_block at fixture-emit time, validated by the Foundry test as a cross-check. This is defense-in-depth, not strictly required by the math (the two are mathematically orthogonal), but the plan's anti-pattern §7 "silently relax the tolerance" guard would benefit from a parallel "silently drift the strip" guard.

---

## §4 Cross-repo contract sufficiency assessment

HANDOFF.md §2 enumeration (JSON-load + schema_version check, audit_block re-hash, position-provision, run 24 FX-bracket scenarios, assert envelope) is **mathematically complete** modulo MQ-FLAG-B1.1 and B1.2. Once σ_T is disambiguated (B1.1) and the time-grid is either pinned or its emit-side authority is named (B1.2), every degree of freedom that affects the envelope outcome is fixed by either the analytics-side fixtures (strip JSON + FX paths JSON) or by HANDOFF.md §3 formula pinning. The 12-leg position-provisioning convention is appropriately deferred to the cross-repo Foundry plan — that's a Panoptic-API question, not an analytics math contract.

---

## §5 Disposition recommendation for plan author

Land v0.1 → v0.2 with:

1. **Task 1.2 acceptance bullet**: add explicit statement "σ_T is computed via PRIMITIVES eq. (7) DISCRETELY from the FX-path samples emitted in `fx_paths_24_brackets.json`; the Stage-2 closed-form expression $(\overline{X/Y})^2 ε^2 [1/8 + \sin(4ωt)/(32ωt)]$ is NOT consumed by the Foundry test." (MQ-FLAG-B1.1)
2. **HANDOFF.md §3 (Task 1.1 acceptance)**: pin `time_grid.n_points = 5000` (matching cohort_4/pi_derivation.py:241), or add explicit emit-side authority. (MQ-FLAG-B1.2)
3. **Plan §9 HALT-routing**: change "FAIL on ≥ 2/24 brackets → HALT" to "FAIL on ≥ 1/24 brackets → HALT". Exit is 24/24 strict per master §2.3. (MQ-FLAG-B1.3)
4. **§12 references**: fix `§6 eq. (6)` → `§5 eq. (6)` and `eq. (7)` → `§6 eq. (7)`. (MQ-NIT-B1.1)
5. **Task 2.2 schema**: add `strip_audit_block_parent` field to fx_paths JSON. (MQ-NIT-B1.2)

CORRECTIONS-α §11.1 should record these five dispositions verbatim.

---

## §6 Verdict

**ACCEPT_WITH_FLAGS.** No BLOCK. Three Material FLAGs must land in v0.2 before Wave-2 dispatch. The math is correct; the plan is under-specified at three boundary conditions. The envelope formula pin (Task 1.2) is the load-bearing fix from master-spec MQ-FLAG-1 and is correctly inherited. With v0.2 dispositions landed, B1 is mathematically execution-ready.

---

**MQ reviewer:** Model QA Specialist (independent)
**File:** `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-11-stage-3-b1-rc-mq-review/mq-verdict.md`
**Word count:** ~1380
