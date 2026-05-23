# Code Reviewer Closure Re-Review — D1.D + D4 Joint Spec v0.2

**Reviewer:** Code Reviewer (methodology-rigor lens, closure-only)
**Spec:** `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2
**Prior verdict:** v0.1 CONDITIONAL_APPROVE with 4 MUST-fix + 6 Strong recs
**Date:** 2026-05-18
**Scope:** verify CORRECTIONS-B closure of MUST 1-4 and Strong recs ONLY. CORRECTIONS-A not re-litigated.

---

## Closure verdict

**APPROVED_WITH_NITS** — all four MUST-fixes are closed in the right direction. Strong recs 1-6 are addressed inline. Pre-pin sufficiency is restored across §4.1, §4.2, §4.3. Two minor v0.2-introduced items remain (duplicated §14 heading; one residual NIT-5 lag-k=2 gap carried forward) but neither warrants blocking. Implementation may proceed under v0.2.

The autofix direction is correct on every count. The spec is now identifiable where v0.1 was not: Δ-spec dodges spurious regression, ratio-of-means dodges Jensen+denominator-blowup, aggregate-with-bias-disclosure honestly handles the wallet non-overlap rather than pretending it away, and the single-primary commitment in §3.1 plugs the FWER hole. None of the fixes is wrong-direction and none introduces a new bug worse than what it replaced.

---

## MUST 1-4 closure check

### MUST-1 (spurious regression / spline) — CLOSED

§4.1 now declares Δlog primary with COP/USD spot promoted to PRIMARY X (no interpolation; daily public data). Banrep services-credit is demoted to *quarterly validation only* via sign-concordance — not entering any inferential test in interpolated form. The spline interpolation is explicitly removed (§13 CORRECTIONS-B). Stationarity gate (ADF + KPSS, both must agree, p<0.05 / p>0.05 respectively) is declared as pre-data gate; cointegration fallback explicit. The Granger-Newbold risk that drove v0.1's block is structurally eliminated because (a) Δ-form is unit-root-safe, (b) the X that previously needed interpolation is no longer the primary X. Closure is clean.

Minor note: the ADF/KPSS AND-conjunction posture is conservative but defensible (open item §14.8 self-flags this). Reviewer agrees with AND as the prudent default; reject only if both reject.

### MUST-2 (joint identity wallet non-overlap) — CLOSED

§1 and §4.3 reframe ρ̂ as a *population-aggregate transmission proxy*, NOT a wallet-level identity. The 30-60% overlap is acknowledged in-line. Path (B) aggregate-with-bias-disclosure is adopted explicitly with named bias direction: "Phase 1 ρ̂ likely **understates** true wage→capital rate due to (a) non-overlap external inflows boost CF without flowing through E_T, and (b) speculator round-trips inflate E_T without producing capital formation." This is exactly the honest-minimum path the v0.1 review proposed as option (b). Composite-vs-wage attribution (v0.1 review focus #7) is also closed by the same bias-direction disclosure now appearing in §1 *and* §4.3 *and* every §7 verdict row's population-scope clause. Reviewer accepts.

### MUST-3 (ratio-estimator instability) — CLOSED

§4.3 names `ρ̂_window = (Σ ΔCF_t) / (Σ E_t)` ratio-of-means as PRIMARY aggregation. Mean-of-ratios (`ρ_t` monthly) is demoted to "secondary visualization only — NOT an inferential object," explicitly citing Jensen-bias and denominator-blowup as reasons. Two HALT triggers are added: `|ρ̂_window| > 1.5` (identity-breakdown) and `Σ E_t < $10M` (denominator floor) — both required in v0.1 review. Mean-of-ratios visualizations carry a denominator-floor (`E_t > 0.05·max(E_t)`) to suppress blowups. All three of the v0.1 MUST-3 amendments are in place. Closure is clean.

### MUST-4 (multiple-testing protection) — CLOSED

New §3.1 explicitly commits single-primary-per-estimand: one D1.D spec, one D4.1 GPD POT fit (USDC-only at u=$0.99), one joint aggregation (ratio-of-means full-window). Sensitivity arms are labeled sign-concordance only with the explicit statement "secondary cannot rescue a primary FAIL" — the Bonferroni-equivalent posture the v0.1 review prescribed. Banned-moves list is comprehensive: post-hoc favorable-arm selection, regime cherry-picking, sub-window re-run are all named. §4.2 inherits the §3.1 rule (pooled and USDT-only arms are sensitivity-only; USDC-only posterior is the inferential headline). §4.3 inherits via "regime conditionals are *exploratory only* and labeled as such." Closure is clean.

---

## Strong recs closure check

| Rec | v0.1 ask | v0.2 status |
|---|---|---|
| SHOULD-1 (γ≠0 vs γ=0 dual mechanism) | Pre-pin two arms | CLOSED — §4.1 "Auxiliary spec" row pins γ≠0 and γ=0 as two arms |
| SHOULD-2 (pooled vs USDT-only) | Pre-pin both as competing arms | CLOSED — §4.2 declares Primary GPD (USDC-only) + Sensitivity arm A (pooled) + Sensitivity arm B (USDT-only); 10× ξ̂ divergence acknowledged |
| SHOULD-3 (off-ramp decomposition has implicit residual) | Make residual explicit | CLOSED — §4.3 decomposition row now reads `ρ̂ = 1 − off_ramp − consumption + external_inflow + residual` with note "partition is NOT a clean identity" |
| SHOULD-4 (coverage-scalar asymmetric role in ρ̂) | Pre-pin symmetric vs asymmetric | CLOSED — §4.3 "Coverage-scalar asymmetry" row commits to 5-arm sensitivity (10/10, 20/20, 35/35, 20/35, 35/20); notes ratio-of-means is scalar-invariant under symmetric application |
| SHOULD-5 (Dune query state can change) | Pre-pin frozen snapshot | CLOSED — §13 CORRECTIONS-B Tier-2 frozen-snapshot requirement explicitly committed to `data/raw/onchain/snapshots/YYYY-MM-DD_<query>.{sql,parquet}` |
| NIT-2 / SHOULD-derived (ρ sign expectation consistency) | Reconcile ρ ≥ 0 with ρ̄ < 0 HALT | CLOSED — §4.3 sign row now reads "ρ̂ ≥ 0 (population aggregate; cohort cannot collectively decumulate while receiving)" and FAIL row in §7 catches both ρ̂ ≤ 0 and ρ̂ > 1.5 |
| NIT-3 (verdict notebook 06 input-vs-output) | Pre-pin Notebook 06 consumes only parquet | NOT FORMALLY CLOSED — §6 still lists Notebook 06 as "verdict consolidation" without pinning input-output separation. Acceptable nit; safer to add. |
| NIT-5 (lag k=2 gap) | Either primary/secondary/banned | NOT CLOSED — §4.1 still reads "k=0-1 secondary; k>3 BANNED"; k=2 status remains ambiguous. Minor. |
| NIT-6 (M-sketch wording: same chain ≠ same venue) | Tone down "measurement = deployment channel" | PARTIAL — §8 adds STAGE-2 FIREWALL paragraph (helpful), §8.3 still reads "measurement channel = deployment channel — unique structural alignment." The v0.1 nit specifically asked to soften this. Carried forward as nit. |

Six strong recs CLOSED; three nits partial/open (NIT-3, NIT-5, NIT-6). None of the open nits is a blocker.

---

## Pre-pin sufficiency audit v0.2 (field counts vs v0.1)

### §4.1 D1.D side

| Field count v0.1 | Field count v0.2 | Net change |
|---|---|---|
| 7 fields | **11 fields** | +4: Stationarity gate, Auxiliary spec (γ≠0 / γ=0), Banrep quarterly cross-check, X-PRIMARY vs X-SECONDARY split |

All v0.1 PARTIAL/NO ratings now flip to YES except NIT-5 (k=2 lag-gap, minor). Primary specification row is unambiguous and is one row — single-primary commitment honored. HALT trigger row explicitly references §3.1. Sufficient.

### §4.2 D4.1 side

| Field count v0.1 | Field count v0.2 | Net change |
|---|---|---|
| 9 fields | **11 fields** | +2: explicit Primary GPD fit row + Sensitivity arms A/B rows + Multiple-testing protection row |

v0.1 SHOULD-2 (pooled vs USDT-only as competing arms) now structurally pinned. NIT-1 (magnitude floor trivially satisfied via SVB) remains technically open but is not load-bearing for the verdict given the posterior is the headline. Sufficient.

### §4.3 Joint ρ̂ — the heaviest rewrite

| Field count v0.1 | Field count v0.2 | Net change |
|---|---|---|
| 5 fields | **10 fields** | +5: Primary estimand (ratio-of-means), Numerator definition, Denominator definition, Aggregation HALT, Denominator floor, Secondary visualization (with floor), Regime conditional (with pre-committed thresholds), Bias direction disclosure, Coverage-scalar asymmetry |

This is the section that drove the v0.1 CONDITIONAL. All five v0.1 PARTIAL/NO ratings now flip to YES. Regime definition (v0.1 audit "missing — explicit regime definition") is now pre-committed as (calm = COP/USD 30d vol < median; stress = ≥ p75; depeg = months containing ≥1 USDC depeg ≥0.5%). Magnitude floor is REMOVED (RC C4 finding — undertheorized), replaced with sign + significance + sign-concordance — a defensible weakening that is *more* honest than the v0.1 floor. Sufficient.

### §4 cross-cutting

| Dimension | v0.1 | v0.2 |
|---|---|---|
| Single primary spec per side | NO | **YES** (§3.1 explicit) |
| FWER protection | NO | **YES** (§3.1 sign-concordance + Bonferroni-equivalent posture) |
| Aggregation level for ρ̄ | NO | **YES** (ratio-of-means primary) |
| Layer C deferral with bias direction | partial | **YES** (§1, §4.3, §7 all carry the disclosure) |

Pre-pin sufficiency: PASS across §4.1, §4.2, §4.3.

---

## NEW issues introduced by v0.2 amendments (critical check)

I checked specifically for whether v0.2 introduced any new bugs while fixing MUSTs.

1. **Duplicated `§14` heading**: there are TWO `## 14.` sections — `## 14. Open items for closure re-review` and `## 14. Anti-fishing closure`. This is a numbering bug (the second should be `§15`). Cosmetic; does not affect content. Flag for cleanup but not blocking.

2. **§14 open item #7** asks whether 5 coverage-scalar sensitivity arms are enough or whether a 6th independent-prior arm is needed. This is correctly framed as a reviewer flag, not a covert spec change. Reviewer position: 5 arms is sufficient for Phase-1 demonstration-grade; the 6th arm is a Phase-2 elaboration. No action needed in v0.2.

3. **§14 open item #8** asks whether ADF/KPSS AND-conjunction is too restrictive vs OR. Reviewer position: AND is the correct conservative default (a single test failing is enough to suspect non-stationarity). Keep AND. No action.

4. **Ratio-of-means scalar-invariance claim (§4.3)** — the new row reads "ratio-of-means estimator is INVARIANT to the scalar at population aggregate level. Caveat: if D1.D and D4.1 cohorts have different Colombia-share rates, ratio depends on scalar-ratio." This is mathematically correct (scalar cancels under symmetric application; doesn't cancel under asymmetric). The 5 sensitivity arms (including the asymmetric 20/35 and 35/20) properly test this. No bug.

5. **NIT-1 / §4.2 magnitude floor** "Tail-distance ≥ 1.0% on at least one historical episode" remains trivially satisfied by SVB-2023 — this was a v0.1 NIT not closed in v0.2. Not a new bug, but a known carry-forward.

6. **§6 transparency block requirement** is new and good — adds "what data was used / what gaps remain / what this notebook does NOT claim" to every notebook. This is positive scope addition, not new risk.

7. **§7 verdict matrix** — collective exhaustiveness check. I verified the four-row matrix against the (β-sign × ρ̂-sign × GPD-ξ × data-availability) state space. All states map. Edge-case precedence (PARTIAL on one estimand + PASS on another → PARTIAL-PASS) is explicit. No gap.

No new bugs introduced. The cosmetic §14 duplication is the only mechanical issue.

---

## Pass/fail on autofix completeness

| Item | Required closure | Delivered |
|---|---|---|
| MUST-1 spurious regression | Δ-spec primary + ADF/KPSS gate + spline removal + COP/USD primary X | YES |
| MUST-2 wallet non-overlap | Aggregate-with-bias-disclosure; ρ̂ as population-aggregate proxy | YES |
| MUST-3 ratio-estimator | Ratio-of-means primary + 1.5 HALT + denominator floor + mean-of-ratios demoted | YES |
| MUST-4 multiple-testing | §3.1 single-primary + sign-concordance + Bonferroni-equivalent posture | YES |
| SHOULD-1 γ-control dual mechanism | γ≠0 and γ=0 arms | YES |
| SHOULD-2 pooled vs USDT GPD | 3-arm structure with primary + 2 sensitivity | YES |
| SHOULD-3 decomposition residual | Explicit residual term + "not a clean identity" disclosure | YES |
| SHOULD-4 scalar asymmetric role | 5-arm sensitivity incl. asymmetric scalars | YES |
| SHOULD-5 Dune snapshot | Frozen-snapshot requirement in §13 + §5.4 | YES |
| RC C2 composite-vs-wage bias | Phase-1 ρ̂ "composite indicator" + bias direction in §1, §4.3, §7 | YES |
| RC C4 verdict exhaustiveness | 4-row matrix + ρ̄ ≥ 0.05 floor removed + population scope clause | YES |
| Pre-pin sufficiency §4.1 | All v0.1 PARTIAL/NO → YES except NIT-5 (minor) | YES |
| Pre-pin sufficiency §4.2 | All v0.1 PARTIAL/NO → YES except NIT-1 (minor) | YES |
| Pre-pin sufficiency §4.3 | All v0.1 PARTIAL/NO → YES (5 → 10 fields) | YES |

**Autofix completeness: PASS.** All 4 MUSTs and 6 Strong recs are addressed in the correct direction.

---

## Recommended cleanups (non-blocking; can be deferred to v0.3 or done at execution start)

1. Renumber the second `## 14.` to `## 15. Anti-fishing closure`.
2. Resolve lag k=2 in §4.1 (NIT-5): pin to "secondary" or "banned."
3. Soften §8.3 "measurement channel = deployment channel" to "measurement and deployment share the same chain stack" (NIT-6).
4. Add a one-line pin to §6 Notebook 06: "consumes only parquet outputs of 02-05; no recomputation" (NIT-3).
5. Replace §4.2 magnitude floor "tail ≥ 1.0% on at least one historical episode" with a forward-looking floor or remove the row (NIT-1).

None of these blocks implementation. Implementation under v0.2 is approved.

---

**Reviewer recommendation:** APPROVED_WITH_NITS. Week-1 Dune query execution and Tier-2 frozen snapshot work may begin. The 5 nits above can be folded into a v0.2.1 cleanup pass or carried into the v0.3 post-Phase-1 revision — both are acceptable.

Files referenced:
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md`
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-18-d1d-d4-joint-spec-review/cr.md`
