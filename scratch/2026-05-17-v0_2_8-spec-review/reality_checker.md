# Reality Checker — v0.2.8 Spec Amendment Review

**Spec under review:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.8 §0.8 (CORRECTIONS-Z2 — premise-conditional consistency-rule patch).
**Trigger:** Task 13 R4-S3-COP CONSISTENCY-FAIL (k=1 α̂₁^COP = −17.98, p_1s = 0.670; k=5 α̂₁^COP = −35.89, p_1s = 0.873) on the 28-day v0.2.7 production panel.
**Reviewer:** Reality Checker (Integration / anti-fishing channel).
**Date:** 2026-05-17.
**Branch / HEAD:** `master` at `81dbb2e`; Y-9 closure at `11e238d` (PR#4).
**Evidence base:** spec lines 1084–1182, disposition memo (188 lines), notebook 03 (k=1/k=5 OLS outputs), notebook 06 (Z-arms), notebook 02 (R5 PRIMARY), git history of spec file, recomputed variance numbers from notebook 03 cell-4 summary stats.

---

## Verdict summary

| # | Channel | Verdict | One-line |
|---|---|---|---|
| 1 | Anti-fishing classification (stricter check + threshold grounding) | **PASS** | Additive identity (1e−12) is genuinely stricter than HAC-OLS (statistical); 0.01 threshold sits ~3 OOM ABOVE the empirical ratio (~2e−5) — not tuned to the result. |
| 2 | Pre-registration of the reclassification gate (BOTH preconditions) | **PASS** | Both (identity, var-ratio<0.01) are required; 0.01 is defensible mid-range; 0.001 or 0.10 would not change Task 13 disposition. |
| 3 | Convergent-evidence claim (R5 + Z-arms agree) | **PASS** | Notebook-direct: daily 2.83e-5, Z-1 weekly 7.3e-5, Z-2 backcast median 1.94e-5, spec-cited 2.4e-5. All ~10^−5. Sign-consistent: "FX is small / undetectable in this window". |
| 4 | §2.2.A preservation (HALT-on-FAIL still default) | **PASS** | §2.2.A text at lines 1312–1334 is verbatim; §0.8 is gated by an explicit `if both preconditions hold` clause (lines 1144–1145) with fall-back to §2.2.A. |
| 5 | Task 14 unblocking theory (USDCOP regressor, not LHS multiplier on USD side) | **PASS** | R4-S3-USD spec at lines 1338–1342: LHS is `\|Δln NotionalCost^USD\|`, USDCOP enters ONLY as RHS regressor. No identity-driven swamping; the regression is power-limited but not premise-broken. |
| 6 | CORRECTIONS-K integrity (sensitivity arms remain diagnostic-only) | **PASS** | §0.8 modifies the *consistency check* (which is already diagnostic per CORRECTIONS-S), not a sensitivity arm. CORRECTIONS-K (§2.4 line 1416 "No arm has verdict authority. Period.") is untouched. |
| 7 | Catch-up frontmatter sync | **PASS** | Git diff of commit `9089f43` (v0.2.7) confirms `spec_version` was NOT bumped in frontmatter (no `+spec_version` line). v0.2.8 is honest housekeeping, not process drift. |

**Overall verdict: APPROVE.**

---

## Per-question findings

### Q1 — Anti-fishing classification

**Claim under audit (spec §0.8 line 1170-1174):** "the replacement integrity check (additive identity) is **STRICTER** than the original (HAC-OLS) because it requires floating-point exactness, not statistical significance."

**Verification:**

- Original §2.2.A check: HAC-OLS regression with one-sided α=0.05 on a coefficient. Statistical power-bounded; can fail to reject even when the panel is bit-perfect (which is exactly what happened — see notebook 03 cell 7, where OLS reports R² = 0.007 with α̂₁ = −17.98 ± 40.27 HAC SE).
- Replacement check: `max|Δln Cost^COP − Δln Cost^USD − Δln USDCOP| < 1e-12`. This is a tautological algebraic identity by construction of the panel-builder (multiplicative). Any violation means a floating-point bug or a mis-aligned join. Task 13 verified at 1.78e-15 — three OOM tighter than the stated threshold and ~12 OOM below double-precision epsilon-1 (~2.2e-16) accumulated over a few ops.
- The new check has **zero tolerance for the failure mode it's designed to detect** (panel-builder corruption) and **infinite tolerance for the failure mode HAC-OLS was confusingly conflating** (low-power statistical insignificance). This is the textbook signature of a stricter, more diagnostically-targeted gate. Not a relaxation.

**Variance-ratio threshold grounding (the 0.01 claim):**

Recomputed from notebook 03 cell 4 stats (sd_dln_trm=0.004440, sd_dln_cost_cop=1.152415, sd_dln_tokens=1.689745):

| Quantity | Value |
|---|---|
| var(\|Δln USDCOP\|) | 1.971e-5 |
| var(\|Δln Cost^COP\|) | 1.328 |
| var(\|Δln Tokens\|) | 2.855 |
| **var(USDCOP)/var(Cost^COP)** | **1.48e-5** |
| Spec-cited var(USDCOP)/var(Cost^USD) | 2.4e-5 (3.8e-5 / 1.6) |
| Spec threshold | 0.01 = 1e-2 |
| Empirical ratio / threshold | 0.0024× → **threshold is 420× looser than the actual measurement** |

If the spec author had wanted to "tune the threshold to fit the result", they would have set it to ~1e-4 or 1e-3. 0.01 is a *generous* round-number choice that lets the rule fire long before the regime gets as extreme as Task 13's. **The threshold passes the "would-have-fit-other-results" smell test:** Pair-D (β=+0.137 on FX→BPO, signal-rich, var-ratio ≈ 1) would NOT trigger this rule; that is the correct discriminator behavior.

**Verdict: PASS.** Spec's "stricter, not weaker" claim is empirically defensible. Threshold grounded with margin to spare.

### Q2 — Pre-registration of the reclassification gate

**Claim under audit:** the two preconditions are AND-conjoined and both required.

**Spec text (lines 1140–1145):**
> - The additive-identity check (above) passes.
> - The variance-ratio diagnostic `var(USDCOP) / var(cost^USD)` is computed in the notebook and reported < 0.01.
>
> Both preconditions must be satisfied. If either fails, the original §2.2.A HALT-on-FAIL rule stands.

This is explicit AND-logic with explicit fall-back. No ambiguity.

**Is 0.01 defensible vs 0.001 or 0.10?**

- **0.001 (tighter):** would require var(USDCOP) to be three orders of magnitude smaller than var(cost^USD). Task 13's ratio is ~2e−5, so it would still trigger. But would block normal FX-active regimes (e.g., 2022 COP devaluation periods where var(USDCOP) is much larger). For an arm that exists *specifically* to flag low-FX-content regimes, 0.001 is over-restrictive.
- **0.10 (looser):** would fire even when FX explains 1–10% of cost variance — i.e., the regime where the original §2.2.A *should* have power to detect. This would defeat the purpose of the rule.
- **0.01 (chosen):** sits at the boundary where HAC-OLS power genuinely collapses on T≈28 with HAC L=3. Defensible as the "two-orders-of-magnitude" cutoff that the spec calls out.

A more rigorous version of this rule would tie the threshold to a power calculation (e.g., "trigger when measured power against the pre-pinned alternative falls below 0.20"). That would be a future v0.2.9 refinement. For v0.2.8, 0.01 is acceptable as a coarse but well-bounded heuristic.

**Verdict: PASS.** AND-logic is explicit; threshold is defensible (not arbitrary, not post-hoc-tuned).

### Q3 — Convergent-evidence claim audit

**Claim under audit (spec §0.8 line 1112–1116):** R5 PRIMARY (FX share ≈ 0.003%), Z-1 multi-period, and Z-2 backcast all corroborate "FX-vol not a meaningful driver".

**Cross-check (all from notebook outputs, not spec self-citation):**

| Source | FX-share / variance-ratio | 90% CI / range | Includes zero? |
|---|---|---|---|
| Task 12 R5 PRIMARY (daily, pre-pinned baseline) | 2.77e-5 | n/a (pinned baseline) | n/a |
| Task 12 R5 PRIMARY (daily, measured) | 2.83e-5 | [−3.4e-6, +4.1e-5] (cited disposition) | YES |
| Z-1 weekly | 7.3e-5 | [−2.9e-4, +1.3e-4] | YES |
| Z-1 monthly | 9.9e-5 | [nan, nan] (T=3, excluded per spec) | uninformative |
| Z-2 backcast main (median, 1000 paths) | 1.94e-5 | [1.69e-5, 2.23e-5] (inter-path) | NO (but tiny) |
| Z-2-main / daily baseline | 0.70× | escalation rule 5.0× | well below |
| Task 13 var(USDCOP)/var(Cost^COP) | 1.48e-5 | (point) | n/a |
| Spec §0.8 var(USDCOP)/var(Cost^USD) | 2.4e-5 | (point) | n/a |

All six independent measurements land in the band [1e-5, 1e-4], a single order of magnitude. All confidence intervals that exist are consistent with "essentially zero, possibly tiny positive". Z-2 backcast — which uses an entirely different FX regime (2024-2025 vs. observed 2026-Q1-Q2) — converges with the daily R5 baseline at 0.70× ratio. The convergence is not a coincidence of one measurement; it is robustly redundant.

The framing the spec uses ("three independent measurements converge on FX-vol is empirically not a meaningful driver") is accurate. The CIs do include zero (one-tail), but the magnitudes are all O(10^-5) — five orders below the "meaningful" threshold the original §2.2.A presumed.

**Verdict: PASS.** Convergent-evidence claim is empirically substantiated by three notebook-output sources beyond the spec's self-citation.

### Q4 — §2.2.A preservation

**Claim under audit (spec §0.8 line 1182):** "§2.2.A is preserved verbatim; §0.8 is a premise-conditional addendum, not a replacement."

**Verification:**

- §2.2.A text at lines 1312–1334 reads as in v0.2.7 (no `+/-` diffs in the v0.2.8 patch on those lines per the §0.8 inline statement).
- §0.8 fall-back at lines 1144–1145: *"Both preconditions must be satisfied. If either fails, the original §2.2.A HALT-on-FAIL rule stands."*
- The HALT-on-FAIL default is preserved. §0.8 only fires when (a) panel-builder identity holds AND (b) var-ratio < 0.01. If, e.g., a future iteration has a corrupted panel join (identity violated), §2.2.A HALT-on-FAIL fires unmodified. If a future iteration is in a high-FX-vol regime (var-ratio ≥ 0.01), §2.2.A HALT-on-FAIL fires unmodified.

**Edge case:** could the var-ratio be gamed by post-hoc-removing high-FX observations to push var(USDCOP) down? The notebook computes var(USDCOP) over the full Δln series (28 obs), and the spec doesn't allow trimming. This avenue is closed.

**Verdict: PASS.** §2.2.A discipline survives intact as the default; §0.8 is a strictly narrower carve-out.

### Q5 — Task 14 unblocking justification

**Claim under audit (spec §0.8 line 1152–1156):** R4-S3-USD doesn't depend on R4-S3-COP because USDCOP enters only as a regressor on the USD side.

**Verification of the theoretical structure:**

Cost identity in logs: `ln Cost^COP_t = ln Cost^USD_t + ln USDCOP_t`.
First differences (abs): `|Δln Cost^COP_t|` is *not* a pure sum because of the absolute-value operation (sign info is lost). But the additive identity holds for the *signed* first differences: `Δln Cost^COP_t = Δln Cost^USD_t + Δln USDCOP_t` — verified at 1.78e-15.

R4-S3-COP regression: `|Δln Cost^COP_t| = α₀^COP + α₁^COP·|Δln USDCOP|_{t-k} + α₂^COP·|Δln Tokens|_{t-k}`. LHS *contains* USDCOP additively (in signed-log space); the absolute-value transform doesn't remove the additive USDCOP content. When var(USDCOP) << var(Cost^USD), the USDCOP signal in the LHS is dominated by Cost^USD noise, and the lagged USDCOP regressor (also small) has insufficient signal-to-noise to recover α₁ at HAC-T=27.

R4-S3-USD regression: `|Δln Cost^USD_t| = α₀^USD + α₁^USD·|Δln USDCOP|_{t-k} + α₂^USD·|Δln Tokens|_{t-k}`. LHS is `|Δln Cost^USD|` which **does NOT contain USDCOP** by construction — the COP→USD conversion has already been applied in the panel-builder. USDCOP appears *only* as a regressor (RHS).

Critical implication: the failure mode of R4-S3-COP (low-FX-share regime → LHS dominated by token vol → USDCOP signal swamped in both LHS and RHS) does NOT mechanically propagate to R4-S3-USD. R4-S3-USD's regressor power is still limited by the small var(USDCOP) magnitude — but the test is now genuinely testing a behavioral question (do tokens respond to FX?) rather than chasing an arithmetic-propagation tautology that was supposed to be a pipeline check.

The spec acknowledges this in §2.2.B (line 1349): the null is `α₁^USD = 0` two-sided; FAIL-TO-REJECT is the framework prior under subscription regime. CORRECTIONS-U (line 1364–1371) pre-pinned that the power-HALT is expected to fire at T=38. So Task 14 may HALT for power-floor reasons (legitimate, pre-enumerated), but it will not HALT for the R4-S3-COP-style consistency contradiction. Unblocking on the v0.2.8 patch is theoretically clean.

**Verdict: PASS.** The unblocking justification is structurally correct.

### Q6 — CORRECTIONS-K integrity

**Claim under audit:** sensitivity arms remain diagnostic-only; §0.8 is a premise-rule correction on the consistency check (also diagnostic).

**Verification:**

- §2.2.A is labeled "consistency check (NOT a novel finding)" (spec line 1312). Already diagnostic per CORRECTIONS-S — has "no framework-graduation authority" (line 1329).
- §0.8 modifies how §2.2.A's HALT-vs-CONTINUE routing works. It does NOT grant the consistency check verdict authority over the framework.
- CORRECTIONS-K (§2.4 line 1416): "No arm has verdict authority. Period." — untouched.
- The framework-relevant arms (R5 PRIMARY, R4-S3-USD) retain full verdict authority. §0.8 affects neither.

**Verdict: PASS.** The diagnostic-vs-verdict-authority partition is unchanged.

### Q7 — Catch-up frontmatter sync

**Claim under audit:** v0.2.7 patch updated §0.7 body but missed `spec_version` frontmatter bump; v0.2.8 closes the gap.

**Verification:**

```
$ git show 9089f43 -- docs/specs/2026-05-16-ai-cost-factor-model-design.md \
    | grep -E '^[+-]spec_version:|^[+-]## 0\.'
+## 0.7 v0.2.6 → v0.2.7 CORRECTIONS (parity-comparison-harness patch)
```

The v0.2.7 commit (`9089f43`) added `## 0.7` to the body but produced no `+spec_version` diff line — confirming the frontmatter `spec_version: 0.2.6` was carried forward by accident. v0.2.8 frontmatter now reads `spec_version: 0.2.8` and the revision-history table includes both 0.2.7 and 0.2.8 entries.

This is honest housekeeping. It is also a small process signal: the v0.2.7 patch was applied without verifying frontmatter consistency. A pre-commit hook checking `(latest revision-history row) == (frontmatter spec_version)` would prevent recurrence. Not blocking for v0.2.8 approval, but worth flagging for a future workflow improvement.

**Verdict: PASS** (with minor process note logged).

---

## Anti-fishing audit (cross-channel summary)

**Premise-fix vs. threshold-relaxation discriminators (each a YES is a "premise-fix" signal, each NO is a "fishing" signal):**

| Discriminator | Status |
|---|---|
| Is the replacement check stricter than the original under its own failure mode? | YES — additive identity 1e-12 zero-tolerance vs. HAC-OLS statistical-significance threshold. |
| Was the failure mode triggering the patch unanticipated (rather than chased)? | YES — the disposition memo establishes that Task 12 R5 (FX share 0.003%) had already revealed the regime mismatch before Task 13 ran; the §2.2.A text predated R5 measurement. |
| Does the patch's quantitative threshold sit far from the result that motivated it? | YES — 0.01 vs. empirical 1.5e-5 (420× margin). |
| Is the patch gated by an additional STRICTER check (not just a softer one)? | YES — additive identity check is mandatory regardless of var-ratio. |
| Do convergent independent measurements agree with the patch's premise? | YES — six independent FX-share / variance-ratio measures all land in [1e-5, 1e-4]. |
| Does the patch preserve original discipline as fall-back? | YES — §2.2.A HALT-on-FAIL stands when either precondition fails (line 1145). |
| Were sensitivity arms granted new verdict authority? | NO (good direction) — CORRECTIONS-K unchanged. |
| Were anti-fishing pins (N_MIN, POWER_MIN, MDES_SD) loosened? | NO — pins unchanged (line 1175 "no parameter changes; no threshold tuning"). |
| Was the pre-pinned hypothesis or test geometry changed? | NO — R4-S3-COP coefficients, lags, one-sidedness all unchanged; only the FAIL routing was. |
| Was the disposition memo's user-pivot enumeration followed (Option A or B not silently)? | YES — disposition memo lines 162–170 recommend Option A or B; spec §0.8 corresponds to Option A. |

All ten discriminators point to "premise-fix". No "fishing" signals.

**Independent stress-test (what would a fishing patch have looked like?):**

- It would have **lowered ALPHA_LEVEL** from 0.05 to 0.20 to retroactively pass. v0.2.8 does not.
- It would have **swapped LAG_PRIMARY** from k=1 to k=0 (where contemporaneous corr is +0.103, would test positive). v0.2.8 does not.
- It would have **swapped TOKENS_PROXY** from `output_tok` to `cache_create_5m` to chase a different signal. v0.2.8 does not.
- It would have **switched to two-sided** on R4-S3-COP. v0.2.8 does not.
- It would have **widened POWER_MIN** to rescue under-powered runs. v0.2.8 does not.

The disposition memo (lines 109–121) explicitly lists each of these as "what is NOT done here". The patch is internally consistent with anti-fishing protocol.

---

## Overall verdict: **APPROVE**

v0.2.8 §0.8 is a legitimate spec-premise correction:

1. The original §2.2.A FAIL-handler text was written under an empirically-false premise (that var(USDCOP) is comparable to var(cost^USD)). The premise was already falsified by Task 12 R5 (FX share 2.8e-5) BEFORE Task 13 ran — the FAIL was structurally inevitable.
2. The replacement integrity check (additive identity at 1e-12) is genuinely stricter than HAC-OLS for the failure mode it targets (panel-builder bugs / mis-aligned joins).
3. The 0.01 var-ratio threshold gates the reclassification with a wide safety margin (420× looser than the empirical reading), so it cannot be accused of being fitted to Task 13's specific numbers.
4. §2.2.A is preserved verbatim; §0.8 is a narrow conditional carve-out with the original discipline as fall-back.
5. Task 14 (R4-S3-USD) is theoretically independent of R4-S3-COP — verified at the regression-form level.
6. CORRECTIONS-K (sensitivity-arms-no-verdict-authority) is untouched.
7. The frontmatter sync from v0.2.7 is honest housekeeping confirmed by git diff inspection.

The patch routes Task 13's verdict from `CONSISTENCY-FAIL HALT` to `REGIME-CONDITIONAL FAIL — continue to Task 14`, with the headline regression numbers unchanged and the verdict text amended via a markdown disclaimer (preserving the honest FAIL signal while routing past it).

**No conditions attached.** Recommend merging v0.2.8 and proceeding to Task 14.

### Minor process notes (non-blocking)

1. **Frontmatter consistency hook.** The v0.2.7 patch shipped with `spec_version` un-bumped (caught by v0.2.8 catch-up). A pre-commit hook of the form `assert frontmatter.spec_version == latest_revision_history_row.version` would prevent recurrence.
2. **Var-ratio threshold derivation.** A future v0.2.9 could replace the 0.01 round-number with a measured-power-derived threshold (e.g., "fire when measured power against α₁^COP > 0 at MDES = 0.40 falls below 0.20"). This would tighten the rule's theoretical basis without changing the v0.2.8 verdict on Task 13.
3. **Task 14 power-HALT pre-routing.** CORRECTIONS-U at §2.2.B already pre-enumerates the expected power-HALT for R4-S3-USD at T=38; reviewers should verify that Task 14 implementer follows the pre-pinned disposition template at `notebooks/dev_ai_cost_v2/dispositions/power_halt_template.md`.

---

**Reality Checker sign-off:** APPROVE v0.2.8. Patch survives all seven channel audits and all ten anti-fishing discriminators. Convergent evidence (six independent FX-share measurements) is strong. Replacement check (additive identity) is stricter, not weaker. Threshold (0.01) is grounded with margin. §2.2.A discipline preserved. Task 14 unblocking is theoretically sound.

**Evidence files referenced:**
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` (lines 1084–1182, 1305–1416)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/dispositions/2026-05-17-task13-consistency-fail.md` (188 lines)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb` (cells 2, 4, 7, 10, 13)
- `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/notebooks/dev_ai_cost_v2/06_z_sensitivity.ipynb` (cells 1, 3, 5, 14)
- git commit `9089f43` (v0.2.7 patch — confirms missed spec_version bump)
- git HEAD `81dbb2e` (review baseline)
