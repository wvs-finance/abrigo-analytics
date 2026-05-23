---
name: dev-AI cost factor model v0.2.10 — Wave-5 closure verdict
description: Demonstration-grade pilot iteration; FX-vol contribution to AI-cost variance empirically ~0% for this user x this window; R4-S3-USD behavioral test POWER-HALTED; iteration PAUSED-PENDING-MORE-DATA; framework pivot recommended.
type: project
---

## Headline

Demonstration-grade pilot iteration (N_MIN=38, POWER_MIN=0.50 — below project defaults 75 / 0.80); FX-vol contribution to AI-cost variance empirically approximately 0% for this user x this window (2026-01-06 to 2026-05-14, N=28 weekday rows post-first-diff); behavioral subscription-inelasticity test (R4-S3-USD) POWER-HALTED under canonical lagged-tokens recipe (power 0.1745 < 0.50); verdict-grade conclusions deferred pending N >= 75 panel.

## 1. Iteration scope (per §2.3.1)

- **Grade**: demonstration-grade. Spec §2.3.1 Amendment #5 (v0.2.10 §0.10 CORRECTIONS-W3) pins this iteration's verdict-eligibility surface at the LOWER grade:
  - N_MIN = 38 weekday days (vs project default 75)
  - POWER_MIN = 0.50 at MDES = 0.40 residual-SD (vs project default 0.80)
  - MDES_SD = 0.40 (unchanged)
- **Observed N**: 28 weekday rows after first-diff — **BELOW demonstration-grade N_MIN floor**.
- **Window**: 2026-01-06 to 2026-05-14 (Claude Code JSONL, single user / pilot subject).
- **Pilot framing**: subscription-user notional cost (rate card x token usage) as a *fair proxy* for what a non-subscribed LATAM developer would have paid for the equivalent usage pattern (spec §1.2). Strong assumption — equal demand under both billing regimes — documented as a §6 threat.
- **Verdict-grade graduation requires**: future panel with N >= 75 weekday rows AND power >= 0.80 at the same MDES. At current cadence (~28 rows in ~18 weeks), reaching N >= 75 takes an estimated additional 12–18 months.

## 2. Pre-pinned outcome surface (§2.2.B, §2.1, §2.4)

| Arm | Pre-pinned outcome label | Realized outcome (v0.2.10) |
|---|---|---|
| **R5 PRIMARY descriptive** (§2.1) | (no verdict — descriptive ratio with bootstrap CI; M-design usability gate only) | FX share (excl cov) = **0.0000277** (90% stationary-bootstrap CI [-0.0000034, +0.0000411]); CI half-width = 0.000022 << 0.15 M-design threshold; 2*Cov diagnostic = -0.002924 (negative; weak natural-hedge effect within developer's behavior, 90% CI [-0.008650, +0.002815] crosses zero). |
| **R4-S3-COP** consistency check (§2.2.A) | CONSISTENCY-PASS / CONSISTENCY-FAIL | **REGIME-CONDITIONAL FAIL** per §0.8 CORRECTIONS-Z2 (additive identity holds at 1.78e-15 absolute error; FX beta shrinks toward zero in the deflated regression). Per §0.10 Amendments #6/#7, this verdict is **UNINFORMATIVE for the framework** and is **REMOVED from the R5 corroboration list**. |
| **R4-S3-USD** behavioral test (§2.2.B) | REJECT_NULL / FAIL_TO_REJECT / HALT / POWER-HALT | **POWER-HALT** under canonical lagged-tokens recipe (power 0.1745 < 0.50 demonstration-grade floor). Coefficient for record only: alpha1_USD(k=1) = -18.116337, HAC SE = 40.221, t = -0.450, p_two_sided = 0.6524, HAC L = floor(28^(1/3)) = 3. PARTIAL-* labels SCOPED to demonstration-grade are NOT applicable here because the power gate fires FIRST. |
| **Z-1, Z-2-main, Z-2-W diagnostic arms** (§2.4) | (no verdict — diagnostic-only per CORRECTIONS-K) | Z-1a weekly FX share = 0.000073; Z-1b monthly FX share = 0.000099 (TAGGED uninformative T=4); Z-2-main median FX share close to daily baseline 0.0000277. **Z-3 verdict: NOT_ESCALATE**. Per §0.10 Amendment #4, Z-arms are **SAME-RATIO corroborations of R5** (different time horizons / TRM windows / bootstrap regimes applied to the same algebraic ratio), **NOT independent measurements**. Inflating the count via same-ratio corroborations is fishing-by-redundancy. |

## 3. Substantive interpretation (Role A per CORRECTIONS-R)

Under R5's pinned Role A (individual-sizing), the substantive reading is:

- For this user x this 2026-Q1-Q2 window, individual cost-burden volatility is **dominated by token-burst usage variance**, NOT by FX moves (USDCOP). Usage share = 1.001078 (90% CI [0.998897, 1.003730]); FX share = 0.0000277 (90% CI [-3.4e-6, +4.1e-5]); covariance term diagnostic = -0.002924 (small, negative, CI crosses zero).
- The behavioral subscription-inelasticity null (R4-S3-USD: does USD-side cost vol respond to FX vol despite zero marginal cost?) **cannot be adjudicated** at current N + power. The POWER-HALT routes the test to "no inference attempted" — neither REJECT_NULL nor FAIL_TO_REJECT applies.
- **M-design implication under Role A**: individual hedge sizing should be dominated by token-volume risk; the FX-vol contribution to individual cost-burden vol is **empirically small for this user-and-window** (regime-conditional reading, not a general statement). Verdict-grade confirmation requires the N >= 75 panel.

**NO population-level transmission claim is made.** The R4-S3-USD POWER-HALT precludes any framework-graduation claim about LATAM young-worker AI-cost burden risk. The FX-share-approximately-zero reading is a **regime-conditional descriptive finding on the n=1 proxy subject**, not a framework-disconfirming result.

## 4. Audit-econ closure note (§0.10 reference)

The v0.2.9 verdict (PARTIAL-FAIL_TO_REJECT under contemporaneous Z3 power-recipe pin, commit `90f099e` 2026-05-17) was **WITHDRAWN** per the audit-econ Delphi (`scratch/2026-05-18-ai-cost-delphi/`) findings:

- **Amendment #4** (Critical): convergent-evidence framing rewritten "FOUR independent measurements" -> "ONE descriptive ratio (R5) + ONE POWER-HALTed behavioral test (R4-S3-USD)". Z-arms relabeled as SAME-RATIO corroborations.
- **Amendment #5** (Critical): demonstration-grade vs verdict-grade split formalized. Mandatory headline disclosure of "below project defaults" phrase enforced in this memo + LaTeX write-up.
- **Amendment #6 / #7** (High): R4-S3-COP's REGIME-CONDITIONAL FAIL is UNINFORMATIVE and REMOVED from corroboration accounting.
- **Amendment #8** (High): Z3 power-recipe REVERTED from contemporaneous (v0.2.9 selection) to LAGGED tokens partialling (matches R4-S3-USD's own k=1 lag structure). Under the lagged canonical recipe, power = 0.1745 < 0.50 → POWER-HALT (anticipated per CORRECTIONS-U).
- LiteLLM dual-pin (commit SHA + file SHA-256) enforcement, Codex commingling upstream filtering, and holiday-Monday surfacing are v0.2.10 audit-closure operations committed in Waves 1-3 (commits `96c51e1` -> `7ebef73`).

## 5. Iteration disposition (FRAMEWORK NEXT STEP)

**Status: PAUSED-PENDING-MORE-DATA at demonstration-grade.**

Not closed-PASS; not closed-FAIL; explicitly demonstration-grade with sub-floor N (28 < 38). The R5 descriptive finding (FX share approximately 0%) is regime-conditional and informs M-design priors under Role A; the R4-S3-USD behavioral test cannot be adjudicated.

### Pre-enumerated pivot options for the (Y, M, X) framework owners

- **Option 1 — Continue accumulating**: keep logging Claude Code JSONL on the pilot subject; resume the iteration when `max(weekday days observed) >= 75`. Re-run from Task 10 (panel build) at the new window. Expected timeline ~12-18 months at observed cadence (~1.5 weekday rows / week). Anti-fishing risk: regime change over an 18-month horizon may invalidate the proxy assumption (§1.2).

- **Option 2 — Pivot within Y to a different X**: keep the same Y (LATAM young-worker AI-cost burden risk) but pivot to a different X candidate. The R6 sibling iteration (continuous-stream simulation; spec `docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` v0.1.3) is the natural next X candidate within the framework. R6 is parked at v0.1.3 and ready for dispatch.

- **Option 3 — Pivot to a different Y**: switch target population to one where the FX-channel hypothesis is empirically stronger ex-ante (e.g., non-subscribed pay-per-API LATAM cohort with direct FX exposure on each invoice). This iteration's small-FX finding is **regime-conditional on the subscription pilot subject**, not framework-disconfirming for the broader LATAM target population.

The choice between Options 1 / 2 / 3 is the framework owner's, not this verdict memo's.

### Anti-fishing pins carried forward

- NO claim that R4-S3-USD "fails to reject" the null — the POWER-HALT means the test cannot be adjudicated.
- NO citation of R4-S3-COP or Z-arms as "corroborating" evidence per §0.10 Amendments #4/#6/#7.
- NO use of "FAIL_TO_REJECT" or "PARTIAL-FAIL_TO_REJECT" labels — withdrawn in v0.2.10.
- The headline finding is "FX share approximately 0% descriptive in this regime" — NOT "FX channel does not exist".

## 6. References

- **Spec**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.10 (§0.10 CORRECTIONS-W3 Amendments #1–#8; §1 framework placement; §2.1 R5 PRIMARY; §2.2.A R4-S3-COP; §2.2.B R4-S3-USD; §2.3.1 demonstration-grade subsection)
- **DATA_PROVENANCE**: `notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md` (Wave-4 rewrite under v0.2.10; window 2026-01-06 to 2026-05-14, N=28 post-first-diff, dual-pin LiteLLM rate table, Codex commingling filter, holiday-Monday surfacing)
- **Disposition**: `notebooks/dev_ai_cost_v2/dispositions/2026-05-18-task14-power-halt.md` (R4-S3-USD POWER-HALT trigger + pre-enumerated user pivots A / B / C)
- **Audit reports**: `scratch/2026-05-18-ai-cost-delphi/agent1_math_model.md`, `agent2_data_replication.md`, `agent3_code_econ.md`, `dependency_propagation_map.md` (audit-econ Delphi closure 2026-05-18)
- **Notebooks**: `notebooks/dev_ai_cost_v2/01_data_eda.ipynb` (EDA + power HALT-checkpoint), `02_r5_descriptive.ipynb` (R5 PRIMARY), `03_r4s3_cop_consistency.ipynb` (R4-S3-COP REGIME-CONDITIONAL FAIL), `04_r4s3_usd_behavioral.ipynb` (R4-S3-USD POWER-HALT), `05_sensitivity.ipynb` (R4-S3 sensitivity arms), `06_z_sensitivity.ipynb` (Z-1 / Z-2 / Z-3 — NOT_ESCALATE)
- **LaTeX write-up**: `docs/writeups/2026-05-18-ai-cost-factor-model-v0.2.10.tex`
- **R6 sibling spec (pivot target)**: `docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` v0.1.3
- **Plan**: `docs/plans/2026-05-16-ai-cost-factor-model-plan.md` Task 17 (lines 1820–1847)
- **Precedent style**: `memory/project_pair_d_phase2_pass.md`
