---
spec_version: 1.0
date: 2026-05-06
topic: Supervisor-review LaTeX document — empirical record + request for guidelines
output_artifact: docs/supervisor-review/2026-05-06-empirical-record-letter.tex (+ compiled PDF)
authoring_strategy: three-agent parallel dispatch + main-thread composition
verification: two-wave (Reality Checker + Model QA Specialist) per `feedback_two_wave_doc_verification`
---

# Design Spec — Supervisor-Review Document

## §0. Purpose of this spec

This spec governs the design of a single formal LaTeX document addressed to
the analytics supervisor (a neoclassical econometrician without on-chain /
programming background). The document is an **empirical-methodology record
and request for guidelines** — not a brand pitch, not a product memorandum.

The document records the (Y, M, X) iteration history under the Abrigo
Operating Framework, presents the methodology that produced each verdict,
introduces the on-chain settlement substrate at a level the supervisor can
evaluate, and asks four prioritised methodological questions.

The Abrigo brand and operating context appear as the *frame* that explains
why these specific iterations exist and why on-chain settlement is the
target deployment venue. They are not the *subject* of the document.

## §1. Audience and posture

- **Reader:** the analytics supervisor. Senior econometrician, neoclassical /
  neoliberal training, comfortable with HAC, OLS, GARCH, IV, panel methods.
  No programming background; no prior exposure to on-chain derivatives,
  Panoptic, Mento stablecoins, or Uniswap V3/V4.
- **Posture:** formal academic memorandum, first-person plural ("we"),
  past-tense for closed iterations, present-tense for the framework,
  future-tense only inside §7.
- **Out of register:** marketing copy, brand positioning, product framing,
  speculative claims about Stage-2 / Stage-3 deployment, code, walkthrough
  of any data fetcher, walkthrough of any Solidity primitive.

## §2. Genre and length

- **Genre:** formal LaTeX academic memorandum.
- **Class:** `article`, single-column, 11pt, ~1.5 line spacing.
- **Length target:** 32–37 pages including appendices (per the §3 table, the
  sum of section budgets after the §7.5 expansion and the Appendix D
  addition is ~36 pages; sub-agents have a soft ±10% latitude).
- **Language:** English (per user pick B in brainstorming dialogue 2026-05-06).
- **Tone discipline:** every empirical claim grounded in either (i) a verdict
  artifact under `memory/` or `docs/specs/`, (ii) a published paper in App B,
  or (iii) declared as conjecture / hypothesis where appropriate.

## §3. Section structure

| § | Title | Author agent | Length |
|---|---|---|---|
| 1 | Introduction & Economic Motivation | Econ-Writer | ~3 pp |
| 2 | Operating Framework — The (Y, M, X) Triple | Econ-Writer | ~3 pp |
| 3 | The Abrigo Lemma — Inequality Differential as Hedge Target | Econ-Writer | ~2 pp |
| 4 | On-Chain Settlement Substrate — Primer for the Non-Specialist Reader | On-Chain Explainer | ~4 pp |
| 5 | Empirical Methodology | Data-Methodology | ~6 pp |
| 6 | The Abrigo Log — Record of Closed and Active Iterations | Data-Methodology | ~7 pp |
| 7 | Open Methodological Questions for Supervisor Review | Econ-Writer | ~5 pp |
| 8 | Request for Guidelines | Econ-Writer | ~1 p |
| App A | Glossary (Econometric / On-chain) | Econ-Writer + On-Chain Explainer | ~2 pp |
| App B | Cited literature (deduplicated by main thread) | All three | ~1 p |
| App C | Sample artifact — Pair D verdict header (sha256-pinned) | Data-Methodology | ~1 p |
| App D | Power-calculation transparency table | Data-Methodology | ~1 p |

### §3.1 Introduction & Economic Motivation

Frames inequality as an **institutionally-determined, empirically-measurable
wealth-distribution gap**. The post-Keynesian framing is acknowledged as the
project's intellectual origin but is not litigated against the supervisor's
neoclassical lens — the document presents inequality as a measurable
distributional outcome that any econometrician can study, regardless of
intellectual commitment about its causes. The wage→capital boundary is
introduced as a persistent friction documented in the development-economics
literature (Mendieta-Muñoz 2017; the Rodrik premature-deindustrialization
canon). Project goal: identify macro risks `X` that block this transition
for specific populations and validate them empirically.

**Refined target-population framing (REVISION-A, 2026-05-06).** The economic
motivation is sharpened from the post-Keynesian abstraction of
inequality-as-aggregate to a **concrete financial-intermediation gap** for an
identifiable underserved population — LATAM digital workers paying
USD-denominated AI / API costs (the same population the dev-AI Stage-1
iteration validates against, per §3.6, sub-section §6.2). These workers face
FX-pass-through cost shocks on their monthly USD spend that cannot be hedged
through any existing Colombian bank product; conventional FX-derivative
venues require minimum notionals and counterparty-credit standing they
cannot meet. The Abrigo framework's contribution is to identify the macro
risks `X` that produce these shocks, validate them empirically, and design
**parametric cost-insurance products** that close the intermediation gap.
Inequality is, under this reading, the *consequence* of the missing
intermediation rather than the framing primitive — which lets the
supervisor evaluate the methodology against insurance-underwriting
standards (parametric-index insurance literature: Carter et al. 2017 *World
Development*; Mahul & Stutley 2010 *World Bank*) rather than a polemic
about distribution.

### §3.2 Operating Framework — The (Y, M, X) Triple

Definitions:
- `Y` = welfare-relevant outcome on the wage→capital boundary, operationalised
  per population (e.g. Section J young-worker employment share, household
  consumption-basket realised volatility, asset-vs-consumption return
  differential).
- `X` = macro risk hypothesised to block the wage→capital transition for
  the target population.
- `M` = settlement geometry on Panoptic — *introduced for completeness,
  declared out of scope for empirical validation, deferred to Stage 2 of
  each iteration*.

Stage discipline:
1. Empirical risk validation FIRST.
2. Ideal-scenario M sketch SECOND.
3. Live deployment LAST.

Iteration order: target-population dominant. Section reproduces the relevant
prose from `CLAUDE.md` "Abrigo Operating Framework" with the on-chain /
liquidity-sourcing operational details elided (those belong in §4 or are
out-of-scope altogether).

### §3.3 The Abrigo Lemma — Inequality Differential as Hedge Target

Formal proposition box:

> **Lemma (Inequality-Differential Hedge Target).** Let `R_a(t)` denote the
> return process of an asset basket representative of capital-holding
> households' wealth, and `R_c(t)` denote the return process of a consumption
> basket representative of working-class households' purchasing power. The
> instrument that settles on the differential
>
> `Y_inequality(t) = R_a(t) − R_c(t)`
>
> is welfare-relevant for working-class wealth in a way that no instrument
> settling on `R_a(t)` alone or `R_c(t)` alone is, because the differential
> directly indexes the relative-wealth gap that determines the working-class
> household's purchasing-power decline relative to capital-holders.

**Status of the lemma — load-bearing disclaimer.** The lemma is stated as a
**proposition motivating the iteration design**, not as a proven theorem.
Its existence as a settlement-feasible Panoptic instrument that materialises
the differential `Y_inequality` is Stage-2 / Stage-3 future work and is
explicitly NOT proven by this lemma. Section text immediately after the
proposition box must repeat this disclaimer in prose; the document is
internally consistent with §5 anti-overclaim invariant on lemma-vs-theorem
status.

Discussion: why a single-aggregate hedge (CPI alone, TRM alone) is
insufficient (rich households often hold CPI-indexed assets); two-sided
market existence (working-class LONG; capital-holders naturally SHORT
through their existing positions, requiring no new counter-party); the
continuous-time differential as a stochastic process whose calibration is
deferred to §7.3 as an open question for supervisor input.

**Insurance-framing sharpening (REVISION-A, 2026-05-06).** The lemma's
mathematical content is unchanged; the economic interpretation is
sharpened from "hedge target" to **parametric-cost-insurance underwriting
target**. Under this reading, the differential `Y_inequality(t)` is the
welfare-relevant index variable that an insurance product should settle
on, with the working-class household as the policy-holder and the
capital-holder as the natural counterparty (already-existing exposure to
`R_a(t)` requires no new opt-in counterparty position). The two-sided
market existence argument therefore reduces to the standard parametric-
insurance counterparty matching of Carter et al. 2017; the implementation
venue (Panoptic perpetual options) is settlement infrastructure, not the
economic primitive.

### §3.4 On-Chain Settlement Substrate — Primer for the Non-Specialist Reader

Anchored to traditional-finance analogues throughout. Topics and required
analogues:

- **What "on-chain" means** — programmable settlement on a public ledger,
  analogue: clearinghouse with public, verifiable, programmable rule-set.
- **Panoptic protocol** — perpetual options on Uniswap V3/V4 LP positions.
  Analogue: a perpetual-future-on-options instrument where the option strike
  is encoded as the price range of a market-making position. Section
  describes payoff geometry without describing implementation.
- **Mento purchasing-parity stablecoins** (COPm, BRLm, KESm, EURm, USDm).
  Analogue: digital country-currency-pegged claim, with the peg maintained
  by an on-chain reserve mechanism. The crucial point for the empirical
  argument is that **a hedge denominated in COPm settles in the user's
  consumption currency** rather than USD — the hedge is purchasing-parity
  preserving by construction.
- **Political-receptivity context** — the Trump-Petro tariff standoff of
  January 2025 produced a documented +100% Littio USDC user-account-growth
  spike within 48 hours (per the project's `OFFCHAIN_COP_BEHAVIOR.md`
  reference document; the same event is used as a structural-break
  event-dummy across `docs/specs/2026-04-20-remittance-surprise-trm-rv-design.md`
  §7 and `memory/project_colombia_yx_matrix.md`). This is a **user-side**
  responsiveness signal — Colombian retail moved into a USD-stablecoin rail
  during a political dollar-access shock — NOT a presidential transaction.
  Anecdotal frame, NOT load-bearing for any empirical or methodological
  claim. Earlier draft language asserting "the Colombian president has
  publicly transacted on-chain" is removed; that specific claim was
  unsourced in the project repository under Wave-1 Reality-Checker review.
- **Critical disclaimer (load-bearing).** The β-validation work is
  *independent* of on-chain deployment. DANE, Banrep, GEIH off-chain data
  drive the estimation. On-chain provides the settlement venue once an
  iteration passes Stage 1. The supervisor's review concerns the
  econometrics; on-chain content in this document is contextual, not
  evidentiary.

What the supervisor needs to retain after §4: (i) on-chain options exist
and are tradable today (Panoptic); (ii) purchasing-parity stablecoin
denominations exist (Mento); (iii) the empirical work he is reviewing is
off-chain econometrics; (iv) the rest of the document does not require
on-chain familiarity.

### §3.5 Empirical Methodology

Following the structural-econometrics discipline. Subsections:

- §5.1 **Pre-registration discipline.** Sign expectation, lag structure,
  primary specification, robustness arms, and verdict thresholds pinned
  in spec text BEFORE any data is touched. Spec sha256 pinned at commit
  time and not adjusted post-data.
- §5.2 **Anti-fishing invariants.** `N_MIN = 75` observations after sample-
  window compliance; `POWER_MIN = 0.80` at the pre-registered MDES;
  `MDES_SD = 0.40` SD-units of `Y`. **Forward-reference to §7.4 (supervisor
  ask):** these three numbers are inherited from Phase-A.0 Rev-5.3.1 and
  have NOT been re-derived per iteration's actual `N` / autocorrelation
  structure. The §5 anti-overclaim invariants bind sub-agents to flag this
  inheritance explicitly; the document is asking the supervisor to
  validate (or revise) the thresholds, not asserting them as proven.
- §5.3 **Functional form and primary inference.** `log(FX_{t-k})` for
  `k ∈ {6, 9, 12}` months; composite `β_composite = β_6 + β_9 + β_12` as
  the primary test statistic; logit-OLS for share-Y, raw-OLS for level-Y.
  **Primary inference is OLS-homoskedastic standard errors** by spec text
  (Pair D §5.3, dev-AI Stage-1 §5.3). HAC (Newey-West) is a pre-committed
  R4 robustness row, not the primary inference. The §6 iteration-block
  headlines report the **less-favorable** of OLS-SE and HAC-SE wherever
  the verdict is invariant under both — Pair D's PASS verdict survived
  HAC SE substitution at one-sided p ≈ 1.46e-08 unchanged, so the HAC SE
  appears in the headline because R4 produced a marginally lower p-value
  than the OLS primary; reporting the more conservative SE convention is
  anti-fishing-cleaner. The verdict label (PASS / FAIL / ESCALATE) is
  invariant across the two SE conventions in every iteration that has
  closed to date.
- §5.4 **Robustness inference (HAC).** HAC (Newey-West) standard errors
  with **fixed lag truncation `L` chosen at spec-authoring time per
  iteration**, NOT a data-driven automatic rule. Project-actual values:
  `L = 12` for monthly Pair D and dev-AI Stage-1 (lag-truncation matches
  the longest right-hand-side lag in the spec — the 12-month
  contracting-cycle horizon); `L = 4` for weekly FX-vol-CPI primary
  (autocorrelation-bandwidth diagnostic in Phase-A.0; A12 HAC(12) is a
  pre-registered fat-tail sensitivity, not the primary). Automatic
  selection rules (Newey-West 1994; Andrews 1991) are intentionally NOT
  used — automatic-selection bandwidth choice introduces a post-data
  degree of freedom that the project's anti-fishing discipline rules out.
- §5.5 **Robustness arms** (per-iteration; pre-pinned at spec-authoring
  time; single-row alternatives that vary exactly one design choice from
  the primary). Typical universe across closed monthly iterations
  (Pair D, dev-AI Stage-1):
    - R1 — regime-dummy methodology-break alternative (e.g., 2021 GEIH
      `empalme` regime dummy).
    - R2 — sector-/sample-cut narrowing (e.g., Section J+M+N narrow Y;
      Section M-only).
    - R3 — functional-form alternative (raw-share vs logit).
    - R4 — HAC-Newey-West inference (per §5.4) substituted for OLS SE.
  FX-vol-CPI uses a wider 13-row sensitivity universe with its own
  pre-registered hash (`nb1_panel_fingerprint.json`
  `sensitivity_preregistration_hash`); A1 monthly cadence and A4
  release-day-excluded are two of the rows. Lag-set immutability is
  anti-fishing-banned (Pair D §9.4); the universe does NOT include "free
  lag tuning". `SUBSTRATE_TOO_NOISY` trigger: ≥3 of 4 R-rows produce
  sign-flipped composite β relative to primary.
- §5.6 **Verdict mapping.** `PASS`, `FAIL`, `ESCALATE` (Clause A:
  positive β, p ∈ (0.05, 0.20]; Clause B: near-zero β with high tail
  asymmetry — operationalised as `|β/SE| < 0.5` AND (`|skew(residuals)| >
  1.0` OR `excess kurtosis(residuals) > 3.0`), all numerics pinned at
  spec-authoring time per iteration), `SUBSTRATE_TOO_NOISY`. Pair D's
  Clause B did NOT fire (`|β/SE| ≈ 5.5` is well outside Clause B
  triggering range); dev-AI Stage-1 Clause B status is post-estimation.
  The numerical thresholds are `MUST NOT BE ADJUSTED POST-DATA` per
  Pair D §9.1 threshold-immutability invariant, inherited verbatim.
- §5.7 **HALT-disposition-pivot.** When spec contradicts data, halt the
  iteration, write a disposition memo, enumerate ≥3 pivot options, request
  user adjudication. Threshold tuning post-hoc is silent fishing and is
  banned (`feedback_pathological_halt_anti_fishing_checkpoint`).

### §3.6 The Abrigo Log — Record of Closed and Active Iterations

Each iteration formatted as a uniform block with **nine** fields:

1. Target population.
2. (Y, X) pair with operational definition.
3. Sign expectation + literature anchor.
4. Primary specification (lag structure, functional form, inference).
5. Sample (`N`, window).
6. Verdict (`PASS` / `FAIL` / `EXIT_*` / `PARKED` / `IN_PROGRESS`).
7. Headline numbers (β, t, p, CI as applicable).
8. Key caveats from independent review (Reality Checker / Model QA / Code
   Reviewer findings inherited into the framework decision log).
9. **Pre-registration sha256 chain.** Per-iteration revision history with
   sha256 hash and date for every spec-text version that governed estimation
   (e.g., Pair D v1.1 → v1.2 → v1.2.1 → v1.3 → v1.3.1; dev-AI Stage-1 v1.0
   → v1.0.1 → v1.0.2). This field is the audit-trail-discipline artifact
   demonstrated in detail in Appendix C; the §6 blocks reproduce the chain
   in compact form for evidentiary completeness.

Iterations covered:

- **§6.1 Pair D — BPO offshoring × COP/USD lag.** PASS verdict 2026-04-28;
  β_composite = +0.13670985, HAC SE 0.02465, t = +5.5456, one-sided
  p = 1.46e-08; sample N=134, 2015-01 to 2026-02. Pre-registration chain:
  v1.1 → v1.2 → v1.2.1 → v1.3 → v1.3.1 (`964c62cca0…ef659`). Four
  Reality-Checker FLAGs preserved as load-bearing inheritances:
    (i) hedge the *correlation*, not the BPO causal channel (RC FLAG #1);
    (ii) lag effect concentrated at lag-6 (≈80% of composite); narrative
    is "concentrated at 6-month horizon, within the 6–12mo contracting
    window," NOT "spread uniformly across 6–12mo" (RC FLAG #3);
    (iii) data-driven window-narrowing → regime-mix concern (post-2014
    oil collapse + COVID + Fed-tightening over-represented; RC FLAG #6);
    (iv) **verdict-sensitivity-to-design-decision** (RC FLAG #5): the
    verdict was sensitivity-tested against an off-spec orchestrator-brief
    variant including `marco2018_dummy` in the primary; the off-spec
    variant produced β = +0.0815 / one-sided p = 0.080 → ESCALATE
    Clause A. Spec-verbatim ran as authoritative per the spec sha256
    pinned 9.5h before Phase-2 dispatch; the off-spec variant is preserved
    in `primary_ols.json:off_spec_sensitivity_orchestrator_brief` for
    audit. Reference: `memory/project_pair_d_phase2_pass.md`,
  `docs/specs/2026-04-27-simple-beta-pair-d-design.md`.

- **§6.2 dev-AI Stage-1 — Section J ICT × COP/USD lag.** IN PROGRESS
  (Phase 1 dispatched 2026-05-05). Pre-registration chain: v1.0 → v1.0.1
  → v1.0.2 (`7c72292516…751f5a`). Section J is a strict subset of Pair D's
  Section G–T cut; compositional-accounting risk explicitly flagged in spec
  v1.0.2 §1 and §9.16. **CORRECTIONS-κ realized-vs-anticipated gap (two
  numbers, not one):**
    (i) `cell_count` realized `[94, 267]` (median 145) vs Y feasibility
    memo §1.1 ex-ante baseline `[700, 1200]` — factor 5–7× below baseline;
    1 month at `cell_count = 94` (2024-10-31, borderline rare-event
    regime under 100); 74/134 months below 150.
    (ii) `raw_share` realized `[0.014, 0.031]` vs spec-anticipated
    `[0.04, 0.10]` — factor 1.3–3× below baseline; logit derivative
    `1/[Y(1−Y)]` consequently maps to `[33, 73]`, a factor 3–7× larger
    amplification than the v1.0.1-anticipated 2.34× across-support
    baseline.
  Disclosed via CORRECTIONS-κ inline (spec v1.0.2 decision_hash
  `7c72292516…751f5a`). The spec's pre-pinned R1 (regime dummy) and R3
  (raw-OLS) hedges become MANDATORY-ESCALATE under realized κ-amplification
  per §6 v1.0.2 escalation-tightening sub-paragraph. Reference:
  `docs/specs/2026-05-04-dev-ai-stage-1-simple-beta-design.md`.

- **§6.3 FX-vol-CPI-surprise — Colombian CPI × TRM realised vol.** CLOSED
  FAIL on the pre-registered weekly primary. Two pre-registered
  sensitivities (A1 monthly cadence, A4 release-day-excluded) showed CIs
  excluding zero at 90% in the positive direction; pivot paths are
  preserved as research record but the primary FAIL is canonical. T1
  exogeneity rejected (F=15.12, p=1.3e-9) — β̂ describe how past
  information predicts current RV, not how exogenous surprises cause
  future RV; the project does not claim structural identification on
  FX-vol. (This corresponds to the Granger-predictive vs structural-
  causal distinction familiar to the supervisor; the document does not
  use β̂ as an impulse-response.) Reference:
  `memory/project_fx_vol_econ_gate_verdict_and_product_read.md`,
  `memory/project_fx_vol_cpi_notebook_complete.md`.

- **§6.4 Phase-A.0 Remittance — Colombian remittance corridor × FX.**
  CLOSED EXIT_NON_REMITTANCE 2026-04-24. The Phase-A.0 specification
  defined a remittance-corridor hedge target (`Y` indexed against
  Colombian remittance flow + FX-pass-through); empirical kill criteria
  k1 (X-driver fingerprint absent in remittance event-window data) and
  partial k2 (cCOP / COPm aggregate user activity is not Colombian
  household remittance, but third-party-DEX volume) fired. Phase-A.0
  exits the (Y, X) pair as falsified-on-mechanism rather than failed-on-
  power, and the workstream pivots to the inequality-differential thesis
  for Mento-native target populations (`memory/project_abrigo_inequality_hedge_thesis.md`).
  **Note on subsequent on-chain attribution.** A 2026-04-24 thesis
  proposed Carbon-DeFi basket-rebalancing volume as a candidate `X_d`
  for the inequality-differential follow-on; that attribution was
  retracted on 2026-04-27 (`memory/project_no_mento_carbon_protocol_integration.md`,
  Rev-5.3.7) after Mento V3 manifest verification confirmed zero
  protocol-level integration between Mento and Carbon — Carbon
  `tokenstraded` events on Celo are pure third-party-DEX activity, not
  Mento Reserve user demand. The β-track Rev-3 X_d candidate has
  re-pivoted to **Mento Broker V2 native swap events** (`mento_celo.broker_evt_swap`
  on Broker `0x777A8255…`); 383,303 distinct traders vs 147 on Carbon —
  factor 2,604× more user-side signal. The supervisor-review document
  presents Phase-A.0 as EXIT on the original (Y, X) and notes the
  on-chain X_d candidate is under re-design at Stage 2; it does NOT
  present Carbon-DeFi as the canonical Phase-A.0 finding. Reference:
  `memory/project_phase_a0_exit_verdict.md`,
  `memory/project_no_mento_carbon_protocol_integration.md`.

- **§6.5 P1 Bittensor SN18 — event-study apparatus.** PARKED for record
  (apparatus complete; no graduating empirical claim). Reference:
  `memory/project_p1_sn18_spec_parked_for_record.md`.

### §3.7 Open Methodological Questions for Supervisor Review

The supervisor-asks, in priority order. Asks §7.1–§7.4 are the four picked
in the brainstorming dialogue 2026-05-06 (user pick E); §7.5 was added on
Wave-2 Model-QA-Specialist FLAG-F6 closure (cross-iteration FWER /
iteration-selection bias is the meta-multiple-comparison concern the
supervisor will form independently — pre-empting it as an explicit ask is
methodologically cleaner than letting the supervisor introduce it):

- **§7.1 Identification strategy.** Current OLS+HAC is correlation-
  identified. T1 exogeneity rejection on FX-vol confirms predictive-
  regression posture. Should we move to IV (and on what instruments —
  policy-rate decisions? oil shocks? US-side AI-API price changes for
  dev-AI?) / event-study / structural VAR? What identification standard
  does the supervisor require before declaring a Stage-1 PASS sufficient
  for Stage-2 dispatch?
- **§7.2 Convex-payoff sufficiency.** Mean-β identification is necessary
  but not sufficient for pricing convex (option-like) instruments
  (`memory/project_abrigo_convex_instruments_inequality.md`). What
  distributional / GARCH-X / EVT extensions does the supervisor recommend
  before declaring an iteration ready for Stage-2 M-design? Specifically:
  is variance-amplification evidence at the X-shock dates sufficient, or
  is full quantile-regression / EVT tail-index estimation required?
  **Insurance-framing sharpening (REVISION-A, 2026-05-06).** The
  question is operationalised as: *what empirical evidence does the
  supervisor require before this β-validation is sufficient to underwrite
  a parametric cost-insurance product?* The convex-payoff sufficiency
  standard is grounded in the parametric-index-insurance pricing
  literature (Carter et al. 2017; Mahul & Stutley 2010 *World Bank*;
  Clarke 2016 *AEJ: Microeconomics* on basis risk), not generic
  option-pricing literature. This reframing is methodologically
  conservative: insurance-pricing literature requires *more* tail-risk
  evidence than option-pricing literature (basis risk, adverse selection,
  catastrophic-loss probability) and the supervisor is invited to apply
  the stricter standard.
- **§7.3 Multi-Y differential calibration.** The Abrigo Lemma's
  `Y_inequality = R_a − R_c` requires constructing each leg as a panel of
  observable variables. How to calibrate joint-leg correlation structure,
  weight components within each leg, handle regime-switching in the
  differential, and apply FWER (or SDR) corrections across the multi-Y
  panel? Specifically: is the standard Bonferroni/Holm conservative
  given the high pairwise correlation expected within each leg?
- **§7.4 Anti-fishing protocol defensibility.** Are `N_MIN=75`,
  `POWER_MIN=0.80`, `MDES_SD=0.40` SD defensible from the supervisor's
  neoclassical-econometrics standpoint? What additional pre-registration
  discipline does he require? (Specifically: pre-analysis plan
  registration in a public registry? `pap` package compliance? AEA RCT
  registry analogue for observational pre-registration per
  Olken 2015 *J Econ Perspectives* and Christensen-Miguel 2018 *J Econ Lit*?)
  These three thresholds are inherited from Phase-A.0 Rev-5.3.1 and have
  not been re-derived per iteration's actual `N` / autocorrelation
  structure (see §5.2 forward-reference). Appendix D presents whatever
  power-derivation transparency is feasible at writing time so the
  supervisor's review is on the actually-defensible numbers, not the
  inherited ones.

- **§7.5 Cross-iteration FWER and iteration-selection bias.** The
  project has run **five** iterations to date (Pair D PASS,
  dev-AI Stage-1 IN PROGRESS, FX-vol-CPI-surprise FAIL-primary-with-
  sensitivity-positives, Phase-A.0 EXIT, P1 PARKED). Each iteration
  was pre-registered, but the **iteration-selection decisions** —
  which (Y, X) pairs to spec-pin in the first place, which pairs to
  drop after EXIT, which pairs to deepen — constitute a meta-multiple-
  comparison structure. Pair D's `p = 1.46e-08` is overwhelmingly
  significant against any reasonable Bonferroni correction over 5
  iteration-level tests. FX-vol-CPI's pre-registered sensitivities
  (A1 monthly 90% CI `[+0.0057, +0.0246]`; A4 release-day-excluded
  90% CI `[+0.0005, +0.0062]`) are far less robust to such a
  correction; A4's lower bound at `0.0005` is at the edge of
  significance even uncorrected. **Question for supervisor:** what
  FWER / SDR / Knowledge-Gradient correction regime should be applied
  across the iteration history, and how should sensitivity-positive
  findings (FX-vol A1 / A4) be weighed under such a correction?
  Sub-question: is iteration-selection itself a multiple-testing
  concern that the existing pre-registration discipline does not
  address, and if so, what mitigations does the supervisor recommend
  (e.g., pre-registered iteration-budget caps, iteration-level
  α-spending function, etc.)?

### §3.8 Request for Guidelines

Short closing. Explicit request for the supervisor's recommended priority
ordering across §7.1–§7.5 and (where applicable) thresholds. Framed so the
response is actionable as the next iteration's design constraints (e.g. "we
will adopt `N_MIN = X` based on the supervisor's recommendation; the
identification strategy for the next iteration will be revised to
`Y` per §7.1 guidance; the cross-iteration α-spending function will be
parameterised per §7.5 guidance"). No implicit promises.

**Insurance-framing closing (REVISION-A, 2026-05-06).** One sentence
records the framing pin: the implementation venue is on-chain (Panoptic
perpetual options; see §4), but the **economic primitive is parametric
cost insurance, not a derivative product**. The supervisor's review
applies insurance-econometrics standards to the empirical work; the
on-chain settlement layer is implementation infrastructure, not pitch.

### §3.9 Appendices

- **Appendix A — Glossary.** Two-column split: econometric terms (HAC,
  composite-β, MDES, FWER, structural VAR, Newey-West, etc.) with terse
  one-line definitions; on-chain terms (Panoptic, Mento, Uniswap LP,
  perpetual option, on-chain settlement, etc.) with one-line definitions
  and traditional-finance analogues.
- **Appendix B — Cited literature.** Baumol-Bowen 1966; Baumol 2006 NBER
  WP 12218; Estache et al. 2021 (Baumol-cluster reference); Mendieta-Muñoz
  2017 *J Econ Struct* "Trade liberalization and premature
  deindustrialization in Colombia"; Rodrik 2016 (premature-deindustrialization
  canon); McMillan-Rodrik 2011 NBER WP 17143 (structural change and
  productivity); Beerepoot-Hendriks 2013 *Service Industries J*
  "Employability of offshore service-sector workers in the Philippines";
  Errighi-Khatiwada-Bodwell ILO 2017 (BPO-comparable framework);
  Olken 2015 *J Econ Perspectives* (pre-analysis plans in development
  economics); Christensen-Miguel 2018 *J Econ Lit* (transparency,
  reproducibility, replication in economics); Hansen 2022 §6/§12 (HAC and
  IV references for §7.1); Kilian-Lütkepohl 2017 (structural VAR
  reference); Engle 2002 *JBES* (DCC-MGARCH for §7.3 calibration); Carter
  et al. 2017 *World Development* (parametric-insurance counterparty
  matching for §3.3 two-sided market). **MACRO_RISKS reference corpus**
  (cited as a project research corpus, NOT a published paper):
  `/home/jmsbpp/apps/liq-soldk-dev/notes/MACRO_RISKS/` — a collection of
  framework-internal notes (`MACRO_RISKS.md`, `INCOME_SETTLEMENT.md`,
  `MACRO_DERIVATIVES.md`, `SIGNAL_TO_INDEX.md`, `PRICE_SETTLEMENT.md`,
  `ECONOMETRICS_NOTES.md`, `MACRO_RISKS_CHECKPOINT.md`) supporting the
  inequality-differential thesis. The supervisor may request specific
  files from the corpus; the citation is included so he is aware that
  the framework's painkiller claims are anchored to an in-house research
  base and not floating in the document.
- **Appendix C — Sample artifact.** Full Pair D verdict header with
  sha256-pinned artifact chain, included so the supervisor can verify the
  audit-trail discipline of the framework.
- **Appendix D — Power-calculation transparency.** Per-iteration
  back-of-the-envelope power derivation showing, for each closed/active
  iteration: pre-committed `N`, observed first-order autocorrelation of
  `Y` residuals, implied detection power at `MDES_SD = 0.40` SD-units of
  `Y` under one-sided `α = 0.05`, with HAC-corrected effective-sample-size
  adjustment per Hansen 2022 §6.18. Method: standard one-sided power
  formula for OLS coefficient under autocorrelated residuals
  (Goh-Knight 1985; Andrews 1991). Where derivation is infeasible at
  writing time, the cell is flagged "inherited from Phase-A.0 Rev-5.3.1,
  not re-derived" and added to §7.4's supervisor ask. The appendix is
  the most direct response to the §7.4 invitation; it converts the
  "is `N_MIN = 75` defensible?" question from rhetorical to data-supported.

### §3.10 Entry-Point Letter — REVISION-C corrections (2026-05-06)

This sub-section records four user-given corrections that apply to the
8-page entry-point letter (`docs/supervisor-review/letter.tex` →
`2026-05-06-supervisor-letter.pdf`), NOT to the 37-page technical
companion. The companion remains unchanged and continues to host the
full Lemma derivation, the on-chain primer, the methodology section,
and all four appendices. The entry-point letter is what the supervisor
reads first; the companion is referenced.

**Correction C-1 (§2 Five Iterations — equation-block format).** The
letter's §2 currently uses a `booktabs` table. Replace with a sequence
of paragraph-blocks, one per iteration, each containing: (1) heading
line (iteration name + verdict); (2) centered model equation in
display math, with sub-/super-script discipline
(`\hat{\beta}_{\mathrm{composite}}`, `\mathrm{logit}`); (3) data
reference (repo path + sha256 + sample); (4) compact test result;
(5) one-sentence interpretation; (6) why-it-fails (FAIL / EXIT) /
caveats-on-PASS / why-parked. Target ~½ page per iteration → ~2.5 pp.

**Correction C-2 (§3 Hedge-target Lemma — REMOVE for v1.2).** The
letter's current §3 presents the abstract Abrigo Lemma in a `lemma`
environment. Remove this section from the entry-point letter. Replace
with a short framing paragraph (≤ ½ pp) stating the concrete risk
target: FX-volatility exposure for LATAM digital workers paid in COP
but carrying recurring USD-denominated professional-input obligations.
The intermediation product target is a contract that compensates for
the FX-pass-through cost shock, denominated in COP or a COP-pegged
purchasing-parity stablecoin. The Lemma's abstract
`Y_inequality(t) = R_a(t) − R_c(t)` framing is preserved in the
37-page companion §3 for supervisor reference; the entry-point letter
does not invoke it.

**Correction C-3 (§1 — bulleted Motivation/Problem/Suggested-solution/
Challenges/Bridge).** The letter's current §1 is prose (~1.5 pp).
Replace with a 5-item `description` list in the order Motivation →
Problem → Suggested solution → Challenges → Bridge to §2. The
wage→capital citations (`mendieta_munoz_2017`, `rodrik_2016`,
`mcmillan_rodrik_2011`) compress into the Motivation bullet.
Challenges bullet is a sub-list of forward pointers to §4 sub-asks.
NO ideology mentions. Target ~0.75–1 pp.

**Correction C-4 (§4 — supervisor-asks reframe to four concrete
asks).** The letter's current §4 ("Five methodological questions") is
replaced with FOUR concrete asks: §4.1 Suggested specifications, §4.2
Risks (which absorbs the prior five methodological questions as
risks-the-project-has-flagged + adds Stambaugh-bias and empalme
residual bias as further flagged risks), §4.3 Bibliography, §4.4
Connections of interested people. Target ~½ pp per ask, ~2 pp total.
The 37-page companion §7 retains the full methodological-question
content unchanged for supervisor reference.

**Out of scope for REVISION-C.** No changes to the §Purpose preamble
or the Closing of `letter.tex`. No changes to the 37-page companion.
No new bib entries. No changes to the spec's §5 anti-overclaim
invariants — the concrete-risk-target framing (C-2), the bulleted §1
restructure (C-3), and the four-ask reframe (C-4) strengthen rather
than weaken the "no marketing register / no Abrigo as product"
invariant by replacing abstract claims with plain-language exposure
descriptions and concrete actionable asks.

### §3.11 Entry-Point Letter — REVISION-D corrections (2026-05-06)

This sub-section records five user-given corrections that apply to the
6-page entry-point letter v1.3 (`docs/supervisor-review/letter.tex` →
`2026-05-06-supervisor-letter.pdf`, committed `05b436d`), NOT to the
37-page technical companion. The companion remains unchanged.

**Correction D-1 (§1 Motivation citation swap to Colombian context).**
The v1.3 §1 Motivation bullet cites three generic FX-as-primary-transmission
references (Calvo & Reinhart 2002 *QJE*; Rey 2015 NBER WP 21162;
Bruno & Shin 2015 *RES*). Replace (or augment) with Colombian-context
references — Banrep "borradores de economía" working papers on inflation
pass-through and TES yield-rate dynamics following FX — sourced via a
background-agent scan of `/home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/{notes,research,docs,design,security-reviews}/`.
Generic references may stay as supporting literature if the
Colombian-specific references are insufficient on their own; Colombian
references take primacy.

**Correction D-2 (§1 Suggested-solution YouTube transcript integration).**
The v1.3 cites `depreciation_insurance_talk` with placeholder bib
metadata. Resolve metadata via background-agent transcript extraction of
`https://www.youtube.com/watch?v=-nPTjKRMSK8` around timestamp 20:50
(= 1250s); fill in speaker, title, channel, upload date, and verbatim
quote about underserved-country demand for depreciation insurance as a
call option on FX rate. Optionally inline-quote the verbatim phrase in
the §1 prose if the supervisor would benefit from seeing the source
language.

**Correction D-3 (§2 data references — repo HTTP URLs).**
The v1.3 §2 iteration blocks reference data via relative paths
(`\texttt{notebooks/bpo\_offshoring\_fx\_lag/}`). Replace with clickable
HTTP URLs via `\href{...}{...}` (hyperref already in preamble); origin is
`https://github.com/JMSBPP/abrigo-analytics`. Required for email delivery
where the supervisor cannot navigate the local repo.

**Correction D-4 (§2 expanded data attribute blocks).**
The v1.3 §2 iteration blocks describe data in a single line. Expand each
to a per-iteration data attribute block surfacing supervisor-relevant
metadata (source, frequency, window, sample size, key transformations,
repo link, spec sha). ~5–7 lines per iteration. Net page-count effect:
+~0.5 pp; ceiling 8 pp per the user's earlier guidance.

**Correction D-5 (§2 Interpretation lines — even shorter).**
The v1.3 Interpretation lines are 10–15 words each. Tighten further to
"verdict + short why," ≤ 10 words each. The verdict label is already in
the iteration heading; the Interpretation line should add a
minimum-information *why* signal, not paraphrase the heading. The
"Why it fails" line that follows handles the long-form post-mortem.

**Out of scope for REVISION-D.** No changes to §3 Risk-target framing,
§4 Asks structure (the four asks remain unchanged), the title block, or
the bibliography section heading. No changes to the 37-page companion.
The §5 anti-overclaim invariants are unchanged; REVISION-D corrections
are mechanical (citation accuracy, link clickability, attribute
disclosure, length cuts) and do not introduce new claims.

### §3.12 Spanish Translation of the Entry-Point Letter (2026-05-06)

This sub-section records the Spanish translation of the 7-page entry-point
letter v1.4 (committed `cf6b7a4`). The Spanish translation is a NEW
deliverable, NOT a modification of the English source; both versions are
preserved.

**Source.** `docs/supervisor-review/letter.tex` → `2026-05-06-supervisor-letter.pdf`.
Compile state: 7 pp, all citations resolved, REVISION-D corrections
integrated.

**Target.** `docs/supervisor-review/letter-es.tex` → `2026-05-06-supervisor-letter-es.pdf`.
Latin-American academic Spanish (Colombian standard); `usted`-form
throughout; verdict labels (`PASS` / `FAIL` / `EXIT_NON_REMITTANCE` /
`PARKED`) preserved in English under `\texttt{...}`; Leifke verbatim
quote preserved in English with a Spanish footnote gloss.

**Pipeline.** Two-agent sequential pipeline:
- Translator (`general-purpose` subagent): produces `letter-es.tex` from
  the English source; consumes a translator-brief that pins the
  terminology table (~30 entries) and the babel-spanish preamble swap.
- Reviewer (`Cultural Intelligence Strategist` subagent, independent
  fresh invocation): verifies translation accuracy + Latin-American
  Spanish register + LaTeX integrity + anglicism/calque flag list.
  Findings integrated by main thread before final commit.

The 37-pp technical companion is NOT translated in this sub-plan; the
Spanish letter references it via the existing English file paths
(`docs/supervisor-review/2026-05-06-empirical-record-letter.pdf`) so the
supervisor can drill into either language at his discretion.

**Background research.** Spanish-academic-AI-writing agent reconnaissance
at `/tmp/spanish-academic-agent-research.md` (2026-05-06) confirmed no
local Spanish-specialist agent exists; the external `deusyu/translate-book`
template (multi-agent translation, language-agnostic, NOT LaTeX-native)
is deferred to user-decision and is not adopted in this run.

**Out of scope for this translation pass.** No changes to the English
letter; no changes to the 37-pp companion; no changes to `refs.bib`
(international refs untranslated; BanRep refs already Spanish-titled);
no changes to the project's spec / plan / sub-plans beyond this §3.12
record. Future iterations may translate the companion or add other
language versions; both are explicitly deferred.

## §4. Multi-agent authorship plan

Three sub-agents dispatched in parallel from the main thread, each with a
section-spec brief stating: scope, length target, source materials, and
explicit anti-overclaim instructions. The main thread composes the final
LaTeX file from their outputs.

| Agent role | Subagent type | Sections | Source materials |
|---|---|---|---|
| **Data-Methodology** | `Model QA Specialist` | §5, §6, App C, App D | `docs/specs/`, `memory/project_*`, structural-econometrics skill |
| **On-Chain Explainer** | `Technical Writer` | §4, App A on-chain half | Panoptic docs, Mento V3 manifest (https://docs.mento.org/mento-v3/build/deployments/addresses.md), `liq-soldk-dev/notes/MACRO_RISKS/` |
| **Econometric Writer** | `Book Co-Author` | §1, §2, §3, §7, §8, App A econ half | `CLAUDE.md`, inequality-hedge-thesis memory, convex-instruments memory |
| **Main thread (orchestrator)** | n/a | App B (assembly only) | each section-author agent emits its own citations as a sub-list; main thread merges, deduplicates, and writes the final `refs.bib` |

**Composition rules.**
- Each agent emits LaTeX source for its sections only, with a file-header
  comment listing the sources it cited.
- The main thread stitches the sections, deduplicates Appendix B citations
  across agents, and assembles the final `.tex` file.
- Cross-references between sections use a documented label scheme: `sec:1`,
  `sec:2`, ..., `sec:8`, `app:A`, `app:B`, `app:C`, `app:D`.
- Bibliography in `bibtex` format under `docs/supervisor-review/refs.bib`.

## §5. Anti-overclaim invariants (apply to all three agents)

- No empirical claim without a citation to either (i) a verdict artifact in
  `memory/` or `docs/specs/`, (ii) a published paper in App B, or (iii)
  declared as conjecture / hypothesis with that label.
- No "Abrigo as product" framing. No marketing register. No promises about
  Stage-2 / Stage-3 deployment timelines.
- No code, no Python, no Solidity, no on-chain data fetcher walkthroughs.
- Pair D is a PASS verdict not a confirmed-causally-identified mechanism;
  per `memory/project_pair_d_phase2_pass.md` Reality-Checker FLAG #1, the
  document hedges the *correlation* and explicitly NOT the BPO causal
  channel. dev-AI Stage-1 inherits this hedging language given the
  compositional-accounting risk.
- FX-vol-CPI-surprise is FAIL on the pre-registered primary; the document
  does NOT call A1 monthly the "main finding" (anti-fishing rule per
  `memory/project_fx_vol_econ_gate_verdict_and_product_read.md`).
- The Abrigo Lemma is presented as a *proposition that motivates the
  iteration design*, not as a proven theorem. The lemma's settlement
  feasibility depends on Stage-2 / Stage-3 work that is out of scope.
- **Cross-iteration FWER posture.** Sub-agents (Econ-Writer §1;
  Data-Methodology §6) MUST acknowledge that the project has run 5
  iterations and that cross-iteration FWER / SDR correction is an open
  methodological question (cross-referenced to §7.5). The §6 iteration
  log MUST NOT present the 5 verdicts as if pre-iteration-selection
  independence held; the document MUST flag iteration-selection as a
  meta-multiple-comparison structure under supervisor review. Specifically,
  no aggregate language like "across 5 iterations the project has
  established X" without a parenthetical acknowledging the FWER /
  iteration-selection caveat.
- **Power-calculation transparency.** The `MDES_SD = 0.40` SD-units /
  `POWER_MIN = 0.80` invariants are inherited from Phase-A.0 Rev-5.3.1
  and have not been re-derived under each iteration's actual `N` /
  autocorrelation structure. Sub-agents writing §3.5 §5.2 / §6 iteration
  blocks MUST flag this as an inherited-not-re-derived parameter pair,
  cross-referenced to §7.4 supervisor-ask and Appendix D power-derivation
  table. No language asserting that the thresholds have been validated
  per iteration; the document is *asking* the supervisor whether they
  are defensible.
- **No "Carbon-DeFi as Mento-native demand" language.** Carbon DeFi has
  no protocol-level integration with Mento per
  `memory/project_no_mento_carbon_protocol_integration.md` (Rev-5.3.7).
  Carbon `tokenstraded` events on Celo are third-party-DEX activity, not
  Mento Reserve user demand. §6.4 framing must reflect the retraction;
  any candidate `X_d` discussion that mentions Mento-Broker-native
  signal as the re-pivot is acceptable, any framing of Carbon volume as
  Mento-protocol demand is banned.

## §6. Output paths

- This design spec: `docs/specs/2026-05-06-supervisor-review-document-design.md`
- Implementation deliverable (out of brainstorming scope, governed by the
  writing-plans plan that follows this spec):
  - LaTeX source: `docs/supervisor-review/2026-05-06-empirical-record-letter.tex`
  - Bibliography: `docs/supervisor-review/refs.bib`
  - Compiled PDF: `docs/supervisor-review/2026-05-06-empirical-record-letter.pdf`

## §7. Verification

This spec is verified per `feedback_two_wave_doc_verification`:
- **Wave 1:** Reality Checker on this draft.
- **Wave 2:** Model QA Specialist on this draft (purpose-matched: econometric
  / structural-econ spec).

Both waves run in parallel. Findings are integrated inline before commit;
no silent override.

## §8. Out of scope for this spec

- The implementation plan that turns this spec into the actual LaTeX file
  (governed by the writing-plans skill, which follows after spec approval).
- The contents of the section-author-agent briefs (drafted at plan time,
  not at design time).
- The supervisor's response. The document is one-shot at v1.0; revision
  cycles based on supervisor feedback are future work.
