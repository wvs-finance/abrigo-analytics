# SaaS-Builder Stage-2 Verdict Memo

**Iteration**: SaaS-Builder (Y, M, X) Stage-2
**Branch**: `iter/saas-builder-stage-2`
**Date**: 2026-05-09
**Stage**: SAAS-COHORT-CLOSE Phase 5 (final canonical deliverable)
**Audience**: future investigators, supervisor/advisor review, Stage-3 implementer
**Status**: PASS (synthetic-Bayesian regime; ideal-scenario clause invoked per `CLAUDE.md` ll. 31-46)

---

## 1. Executive verdict

The SaaS-Builder Stage-2 instantiation of the (Y, M, X) framework **passes its
pre-registered sign-certification gate** under both the primary regime and the
bank-spread robustness overlay. The hedge-side change-of-cap statistic
$\Delta^{(a_s)}$ is strictly negative across all 24 brackets of the spec §5.2
parameter family (3 cohort tiers × 2 churn-mix arms α × 2 cache regimes × 2
softplus-tightness arms κ); 24/24 PASS primary, 24/24 PASS bank-spread. The
cohort-level monthly cap $Z_{\text{cap}}$ is pinned at **4{,}688 COP/month**
(≈ \$1.17 USD-equivalent at TRM = 4{,}000), with a 95% credible interval
[168, 14{,}606] COP whose lower bound is strictly positive. Five-of-five test
points in the spec §8 sign-certification cert PASS, with the perpetual-identity
residual at 6.31×10⁻⁹ (sympy-exact zero corroborated numerically). The verdict
is that the SaaS-Builder cohort hedge is **structurally well-formed** as a
permissionless convex instrument under the synthetic-Bayesian regime
(ideal-scenario clause invoked); magnitudes are small but architecturally
consistent, and the path to Stage-3
(real-data conditioning) is unobstructed by methodological defects.

---

## 2. Background and operating framework

The SaaS-Builder iteration instantiates the Abrigo (Y, M, X) framework
(`CLAUDE.md` §"Operating Framework"; `PRIMITIVES.md` §4.2) for a target
population of AI-native SaaS builders whose subscription costs (Cursor Pro /
Max-5x / Max-20x; Anthropic, OpenAI, Replicate API expenditure) are denominated
in USD but whose wage income is denominated in COP (Colombian peso). **Y** is
the cohort's monthly hedge cap $Z_{\text{cap}}$ — the COP-denominated transfer
that, when financed by a self-LBM premium-funded ratchet, converts wage exposure
into a productive-capital position over the iteration horizon. **M** is the
ideal-scenario Panoptic position family that would settle the convex payoff
(12-leg IronCondor strip per `PRIMITIVES.md` §20; deferred to Stage-3
deployment). **X** is the COP/USD FX risk that compounds USD-denominated tooling
cost shocks against COP wage income — the wage→capital blocker for this cohort.

Stage-2 operates entirely under the **synthetic-Bayesian regime**: priors are
declarative; the cohort-level posterior is constructed under a generative model
without real-data conditioning (`docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md`
§5.2, §15.4). The ideal-scenario clause (`CLAUDE.md` ll. 31-46) is invoked
explicitly: empirical β-validation is independent of actual on-chain Panoptic
liquidity, the M-design step proposes the ideal settlement architecture, and
deployment with live LP capital is the Stage-3 exit. Stage-drift (M-design
ballooning into apparatus) is anti-fishing-banned.

---

## 3. Cohort architecture

The Stage-2 simulation infrastructure rests on the SIM-INFRA-0 three-tier base
(`simulations/types/`, `simulations/modules/`, `simulations/utils/`) per the
`functional-python` skill: frozen-dataclass parameter containers, free-function
stateless transforms, and a single I/O-boundary tier where mutable state is
quarantined. The Stage-2 work decomposes into four cohort sub-plans, each with
an independent audit verdict and its own gate:

```
                      ┌─────────────────────────┐
                      │  spec v1.2.1 (prereg)   │
                      │  PRIMITIVES.md §4.2-§11 │
                      └────────────┬────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │  COHORT-1 (T1)   │ │  COHORT-2 (T2)   │ │  COHORT-3 (Υ_t)  │
    │  cost posterior  │ │  pricing & sign  │ │  revenue form    │
    │  NegBin×Pareto   │ │  softplus / Δ^as │ │  PSIS-LOO-CV     │
    └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
             │                    │                    │
             └─────────┬──────────┴────────────────────┘
                       ▼
             ┌──────────────────────┐
             │  COHORT-4 (Z_cap)    │
             │  π pin + sign cert   │
             │  perpetual identity  │
             └──────────┬───────────┘
                        ▼
                ┌───────────────┐
                │ CLOSE Phase 5 │
                │  this memo    │
                └───────────────┘
```

Cohorts 1–3 produce upstream artifacts (compound posterior draws; per-bracket
$\Delta$ verdicts; Υ_t form selection) that COHORT-4 consumes to pin
$Z_{\text{cap}}$ and discharge the perpetual-identity sign certification. The
CLOSE plan (`docs/plans/2026-05-09-saas-cohort-close.md`) reconciles spec-v1.2
prior corrections, schema-version bumps, and the cross-cohort artifact ledger.

---

## 4. Per-cohort findings

### 4.1 COHORT-1 — T1 cost posterior (NegBin × TruncPareto)

**Plan**: `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md`.

The T1 cost is modeled as a compound negative-binomial × truncated-Pareto
mixture across three pricing tiers (Cursor Pro / Max-5x / Max-20x), with
discrete latents (per-day call counts, monthly aggregation, tier index)
analytically marginalized rather than Gibbs-sampled. The closure properties used
are: (i) sum-of-iid-NegBin = NegBin (parameters scaled by month length), and
(ii) the tier-Categorical is summed out in closed form leaving a 3-component
Pareto mixture per draw.

**Marginalization correction.** The v0.3 implementation had attempted
compound-step CategoricalGibbsMetropolis sampling which produced ESS = 38 (gate
floor 1{,}000) — a 26× shortfall flagged by RC + MQ + CR independent audit.
v0.4 marginalized all three discrete latents into a pure-NUTS chain; ESS rose
to 7{,}537 immediately, then to **338{,}540 (bulk) / 213{,}752 (tail)** after
the Phase-2 N_draws bump (4 chains × 178{,}000 draws = 712k total) required by
the COHORT-4 MC-error budget.

**Diagnostic gates** (`simulations/saas_builder/data/_AUDIT.json`):

| Gate                  | Threshold     | Observed         | Margin           |
|-----------------------|---------------|------------------|------------------|
| `rhat_max`            | < 1.01        | 1.0000265        | 380× headroom    |
| `ess_bulk_min`        | ≥ 1{,}000     | 338{,}540        | 339× headroom    |
| `ess_tail_min`        | ≥ 1{,}000     | 213{,}752        | 214× headroom    |
| `divergence_frac`     | = 0.0         | 0.0              | exact            |
| `ci_width_ratio_max`  | ≤ 1.10        | 1.0039           | 25× headroom     |

712k synthetic τ-draws are emitted to `simulations/saas_builder/data/synthetic_tau_t/`
(month index 0–2; schema v1.0). The cohort prior is stored in
`cohort_prior.parquet`.

### 4.2 COHORT-2 — T2 pricing fit and Δ-sign certification

**Plan**: `docs/plans/2026-05-08-saas-cohort-2-t2-pricing-sign.md`.

T2 pricing is a softplus-smoothed cap function $q_t = \kappa\,\text{softplus}(\beta(c-c^\ast)/\kappa)+q_0$
fit to the published tier ladder via L¹ tightness (verified $L^1 < 10^{-3}\cdot\kappa$
per spec §M2). The hedge-side change-of-cap $\Delta^{(a_s)}$ is computed in
closed form per `PRIMITIVES.md` §7 eq. (10):

$$
\Delta^{(a_s)} = -(1-\alpha)\,a_s\,\frac{\partial q_t}{\partial c} \cdot \cos^2(\theta) \cdot \omega(t)
$$

The 24-bracket sign cert per spec §5.2 enumerates 3 tiers × 2 churn-mix α
∈ {α_low, α_high} × 2 cache regimes × 2 κ-arms.

**Verdict** (`simulations/saas_builder/data/gate_verdict.json`):
- **Primary**: 24/24 strictly negative; $\Delta_\text{med} \in [-2.28\times10^{-8},\, -2.28\times10^{-9}]$.
- **Bank-spread overlay**: 24/24 PASS (`ROBUSTNESS_RESULTS.md`).
- 0 sign violations; `audit_block = 4da660b5…2173`.

**Magnitude reconciliation.** The observed $|\Delta_\text{med}| \approx 10^{-8}$
to $10^{-9}$ is the *analytic prediction*, not a numerical underflow. With
$\beta\cdot\kappa \approx 2.33\times10^4$, the softplus argument saturates and
$q_t$ collapses to the floor $q_0 = \$20$; the $\partial q_t/\partial c$ factor
is therefore exponentially suppressed. Combined with the cos²-near-cancellation
at the calibrated $\theta$, the predicted $|\Delta|$ sits ~13 decades above the
float64 noise floor — well outside any plausible numerical-precision concern.
The sign verdict is robust; the magnitude is a property of the calibrated
softplus regime, documented in `PRIMARY_RESULTS.md`.

### 4.3 COHORT-3 — Υ_t functional-form selection (PSIS-LOO-CV)

**Plan**: `docs/plans/2026-05-08-saas-cohort-3-revenue-form-loo.md`.

Three closed-set candidate forms for the Υ_t revenue trajectory are compared on
a 36-month synthetic panel via PSIS-LOO-CV: (i) martingale random walk,
(ii) AR(1)-log centered, (iii) deterministic-churn $S_t = (1-\lambda)^t$ with
$\lambda \sim \text{Beta}(4.5, 95.5)$.

**Verdict** (`simulations/saas_builder/data/revenue_form_verdict.json`):
**INDISTINGUISHABLE**.

| Form         | ELPD    | SE     | Δelpd | DSE   | Pareto k_max | Weight |
|--------------|---------|--------|-------|-------|--------------|--------|
| ar1_log      | 28.481  | 3.230  | 0.0   | 0.0   | 0.465        | 0.974  |
| det_churn    | 23.873  | 2.846  | 4.608 | 2.762 | 0.224        | 0.026  |
| martingale   | 23.073  | 4.641  | 5.408 | 3.142 | 0.243        | 0.000  |

ar1_log is numerically best (Δelpd = 4.608, DSE = 2.762, **Δelpd/SE = 1.67**),
which falls below the Pin R3 distinguishability threshold of 2.0 on a 36-month
single trajectory. Spec v1.2.1 §6.1 therefore pins det_churn (the
operationally-tractable form) as the canonical Υ_t. All three forms pass
diagnostic gates (k̂_max ≤ 0.465, r̂ = 1.0, ESS_bulk ≥ 4{,}333).

**HALT-on-flip safeguard.** The CLOSE Phase-0 Task 0.2b NON-NO-OP re-fit under
the corrected concentration prior Beta(4.5, 95.5) (vs the legacy
Beta(2.0, 38.0)) was checked for ranking flips per spec §15.4. **No flip
detected** (`rank_flip_detected: false`); both old and new top forms = ar1_log,
ranked sequence (ar1_log, det_churn, martingale) preserved.

### 4.4 COHORT-4 — Z_cap pin and perpetual-identity sign cert

**Plan**: `docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md`.

The cohort cap statistic is

$$
Z_{\text{cap}}(t) = \pi(t) \cdot \frac{\bar{X}}{\bar{Y}} \cdot q_t
$$

where $\pi(t)$ is symbolically re-derived per `PRIMITIVES.md` §6 eq. (8) as
$\pi \propto (\bar{X}/\bar{Y})^2$ (anti-fishing remediation: see §6 below;
the post-hoc $1/\kappa$ factor present in v0.2 was removed). Five-test-point
sign certification (`Z_cap_pinned.SIGN_VERDICTS.md`):

| Label | z (COP/mo) | 95% CI lo | 95% CI hi | Identity passes | Identity residual | Sign |
|-------|------------|-----------|-----------|-----------------|--------------------|------|
| TP1 (κ baseline, X̄/Ȳ=4000)    | 4{,}687.94 | 168.17 | 14{,}606.14 | true | 6.31×10⁻⁹ | PASS |
| TP2 (0.5κ, X̄/Ȳ=4000)          | 4{,}687.94 | 168.17 | 14{,}606.14 | true | 6.31×10⁻⁹ | PASS |
| TP3 (1.5κ, X̄/Ȳ=4000)          | 4{,}687.94 | 168.17 | 14{,}606.14 | true | 6.31×10⁻⁹ | PASS |
| TP4 (FX = 4{,}200)              | 4{,}922.32 | 176.58 | 15{,}336.38 | true | 6.31×10⁻⁹ | PASS |
| TP5 (FX = 3{,}800)              | 4{,}453.57 | 159.76 | 13{,}875.90 | true | 6.31×10⁻⁹ | PASS |

Note: TP1–TP3 share CI bounds since κ ∉ free_symbols(π) under the honest
PRIMITIVES.md §6→§8.1→§10→§15 derivation (κ-only variation; X̄/Ȳ fixed at 4000);
TP4/TP5 shift monotonically per Pin M2 §6 (∂|π|/∂(X̄/Ȳ) > 0 strict).

Pinned $Z_{\text{cap}} = 4{,}687.94$ COP/month at canonical TP1; primary 95% CI
[168.17, 14{,}606.14] COP.
The CI lower bound is strictly positive; the perpetual identity is sympy-exact
zero with a numerical residual of 6.31×10⁻⁹ (15 decades above zero, attributable
to compound float64 rounding in the analytic discharge path). `audit_block =
1fb1f7a4…5d31` is deterministic across re-runs (witnessed in independent audit
re-execution).

**MC error budget remediation.** At C1 v0.4 with N_draws = 16k, the COHORT-4
MC error was 1.32×10⁻², breaching the 1×10⁻³ ceiling. Path α (Phase-2 N_draws
bump to 712k) brought the error within budget without re-architecting the
estimator — the chosen path was the cheaper of the documented α/β/γ
alternatives.

---

## 5. Independent audit summary

Stage-2 underwent **31 verdict files across 7 audit cycles** (RC + MQ + CR per
cohort, plus spec-v1.2 review, Phase-4 schema-bump review, and cohort-close-plan
review — counting latest revisions plus retained version history). The audit panel consisted of `reality-checker` (RC),
`math-quality` (MQ), and `code-reviewer` (CR) Opus sub-agents dispatched in
parallel under Delphi-consensus aggregation per the `audit-econ` skill.

The independent audits caught **12+ BLOCK-severity findings** that self-grading
had missed, including: (i) the C1 v0.3 ESS = 38 marginalization defect;
(ii) the C2 v0.2 5-cell bracket mis-orientation against spec §5.2's 24-cell
parameter family; (iii) the C3 v0.2 LFO-mislabel + winning_form + dse=0 +
multi-sim caveat cluster; (iv) the **C4 v0.2 anti-fishing violation** —
post-hoc $1/\kappa$ factor inserted into $\pi(t)$ to force a sign that
`PRIMITIVES.md` §6 eq. (8) does not predict; (v) the spec-v1.2
prior-hyperparameter mismatch (Beta(2.0, 38.0) vs Beta(4.5, 95.5)); and
(vi) the CLOSE plan v0.2 BLOCK-3 schema-bump anti-fishing pattern (a breaking
schema change mislabeled "additive").

All BLOCKs were either resolved by NON-NO-OP forward-fixes (C1 marginalization,
C2 24-bracket re-orientation, C3 form-selection rerun, C4 1/κ removal) or by
preregistered HALT-on-flip safeguards (Beta-prior re-fit verified no rank flip).

**Test suite**: 423 tests at HEAD post-Phase 4 schema bump (vs 415 pre-Phase 3
nits sweep, vs 411 mid-CLOSE-Phase-1); 99% line coverage on `simulations/types`,
`simulations/modules`, `simulations/utils`, `simulations/saas_builder`; ruff
+ ty clean.

---

## 6. Methodology corrections logged

| Correction                                  | Trigger                                         | Resolution path                                      |
|---------------------------------------------|-------------------------------------------------|------------------------------------------------------|
| C1 v0.3 → v0.4 marginalization              | Audit BLOCK: ESS = 38 (compound-step Gibbs)     | Pure NUTS via analytic latent sum-out → ESS = 7{,}537 → 338{,}540 (Phase-2 bump) |
| C2 v0.2 → v0.3 bracket re-orientation       | Audit BLOCK: 5-cell (ε, ω) ≠ spec §5.2          | Re-derive against 24-cell parameter family (3×2×2×2) |
| C3 v0.2 → v0.3 LFO-mislabel cluster         | Audit BLOCK: LFO-mislabel, winning_form misuse  | Add `winning_form`, fix dse=0 quirk, multi-sim caveat |
| C4 v0.2 → v0.3 anti-fishing remediation     | Audit BLOCK: post-hoc 1/κ in π(t)               | Symbolic re-derive π ∝ (X̄/Ȳ)², σ₀ anchored, perpetual-identity non-tautological |
| Spec v1.1.1 → v1.2.1                        | Lit survey + concentration provenance gap        | Beta(4.5, 95.5) re-pin, NON-NO-OP routing            |
| CLOSE plan v0.1 → v0.2 (BLOCK-3 fix)        | Audit BLOCK: schema-bump mislabeled "additive"  | Correct breaking-change semver bump                  |

Each correction is traceable to a forward-fix commit (see `git log
iter/saas-builder-stage-2`) and discharges a specific audit FLAG/BLOCK in the
corresponding `scratch/2026-05-08-saas-cohort-{1,2,3,4}-independent-audit/`
verdict files.

---

## 7. Limitations

This memo discloses limitations honestly. The Stage-2 ideal-scenario clause is
narrow and does **not** authorize the following claims:

1. **Synthetic-Bayesian only.** No real-data conditioning of cohort costs,
   churn, or revenue trajectory. The posterior is fully prior-driven and the
   verdict is conditional on the spec-pinned generative model. Real-data
   conditioning is the Stage-3 exit.
2. **Small magnitudes are honest.** The π term is the dominant component of
   $Z_{\text{cap}}$ ($|\pi|_{TP1} = 4687.73$ vs $Z_{\text{cap},TP1} = 4687.94$,
   i.e., π ≈ 99.99% of $Z_{\text{cap}}$ at calibrated $\sigma_0 = 20{,}000$).
   The small absolute magnitude (~\$1.17 USD/mo equivalent) reflects the
   $(\bar{X}/\bar{Y})^2$ coupling at canonical fixtures, **NOT a small π
   relative to baseline**. The earlier C4 v0.3 finding that π was "negligible
   vs baseline" was at the prior fixture-suite (CV=0.05, σ₀ wrong); the
   post-$(\bar{X}/\bar{Y})^2$-restoration form makes π the load-bearing scale
   factor. The cap is fundamentally a π-driven quantity at the calibrated
   fixtures; this is the correct economic interpretation of the
   $(\bar{X}/\bar{Y})^2$ derivation, **not a derivation bug** — Stage-3
   magnitudes under real-data conditioning are an open question.
3. **C3 verdict INDISTINGUISHABLE.** Single 36-month trajectory; multi-cohort
   hierarchical pooling is deferred to Stage-3 (Δelpd/SE = 1.67 < 2.0
   threshold).
4. **Per-tier θ_k differentiation deferred.** The cohort-level π posterior
   collapses near the prior at the per-tier resolution; Stage-3 scope per spec
   §5.4 will re-fit with per-tier anchoring (this resolves C1 MQ-FLAG-1).
5. **No on-chain test.** No live Panoptic LP capital was deployed; the
   ideal-scenario clause is invoked, and Stage-3 deployment with real LP
   capital is the genuine market test.
6. **`_first_trajectory` discards multi-sim panels.** The C3 implementation
   selects the first synthetic trajectory; this is a KNOWN LIMITATION
   documented for Stage-3 hierarchical re-implementation.

---

## 8. Verdict translation for product surface

The instrument's mechanics work as designed. The wage-earner's hedge has the
correct convex sign $\Delta < 0$ across the cohort's full parameter family —
both with and without bank spread — and the premium-funded ratchet pays a
strictly positive monthly cap to the wage earner across the realistic FX
bracket (TRM ∈ [3{,}800, 4{,}200]). The cap is small in absolute terms
(~\$1.17 USD/month at TRM = 4{,}000) but the architecture is sound: the sign
holds, the perpetual identity discharges, the priors are honest, and the
Stage-3 path is unobstructed by methodological defect. The Stage-3 question
is whether real-data magnitudes scale up to be commercially material — that
is not a Stage-2 question and Stage-2 does not pretend to answer it.

---

## 9. Stage-3 readiness checklist

- [ ] Real-data conditioning of C1 cost posterior (per spec §5.4 hint).
- [ ] Per-tier θ_k differentiation (resolves C1 MQ-FLAG-1).
- [ ] Hierarchical pooling for C3 across multiple cohort trajectories
      (resolves `_first_trajectory` limitation).
- [ ] Weibull k ≠ 1 falsification of det_churn $S_t$ (pinned in spec
      v1.2.1 §6.1 as a preregistered Stage-3 test).
- [ ] On-chain Panoptic 12-leg IronCondor strip per `PRIMITIVES.md` §20
      (deployment-stage M-design).
- [ ] LP capital provisioning + execution test (Stage-3 deployment exit).

---

## 10. References

**Specs**:
- `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (spec v1.2.1, current)
- `notes/SaaS_Builders_AI_NativeBuilders.md` (cohort-population SaaS note)

**Plans**:
- `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md`
- `docs/plans/2026-05-08-saas-cohort-2-t2-pricing-sign.md`
- `docs/plans/2026-05-08-saas-cohort-3-revenue-form-loo.md`
- `docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md`
- `docs/plans/2026-05-09-saas-cohort-close.md`

**PRIMITIVES.md**: §4.2 (cohort instantiation), §6 (π derivation, eq. 8),
§7 (Δ closed form, eq. 10), §8 (sign-certification cert), §10 (perpetual
identity), §11 (Z_cap pin), §20 (Stage-3 IronCondor strip).

**Lit survey**: `scratch/2026-05-09-st-literature-survey/SURVEY.md` (drove
$S_t$ adjudication and concentration provenance).

**Independent audit verdicts (31 files across 7 audit cycles)**:
- `scratch/2026-05-08-saas-cohort-1-independent-audit/`
- `scratch/2026-05-08-saas-cohort-2-independent-audit/`
- `scratch/2026-05-08-saas-cohort-3-independent-audit/`
- `scratch/2026-05-08-saas-cohort-4-independent-audit/`
- `scratch/2026-05-09-spec-v1.2-review/`
- `scratch/2026-05-09-phase-4-schema-bump-review/`
- `scratch/2026-05-09-cohort-close-plan-review/`

**Emitted artifacts**:
- `simulations/saas_builder/data/Z_cap_pinned.json` (z = 4{,}687.94 COP/mo,
  audit_block 1fb1f7a4…5d31)
- `simulations/saas_builder/data/gate_verdict.json` (24/24 PASS,
  audit_block 4da660b5…2173)
- `simulations/saas_builder/data/revenue_form_verdict.json` (verdict
  INDISTINGUISHABLE, no rank flip)
- `simulations/saas_builder/data/_AUDIT.json` (r̂ = 1.0000265, ESS_bulk
  = 338{,}540, divergences = 0%)
- `simulations/saas_builder/data/synthetic_tau_t/` (712{,}000 draws × 3
  months)
- `simulations/saas_builder/data/PRIMARY_RESULTS.md`,
  `ROBUSTNESS_RESULTS.md`, `Z_cap_pinned.SIGN_VERDICTS.md`

**Framework**: `CLAUDE.md` (Abrigo Operating Framework, ideal-scenario clause
ll. 31-46; anti-fishing invariants).

---

## 11. v1.0 → v1.1 patch notes

This memo was patched in response to the 2026-05-09 RC + MQ 2-wave verify cycle
(`scratch/2026-05-09-stage-2-memo-review/`). All five FLAGs were resolved as
factual corrections against the live emitted artifacts; no verdict claim was
relaxed (anti-fishing posture preserved per `CLAUDE.md` ll. 31-46 and
`feedback_pathological_halt_anti_fishing_checkpoint`).

| FLAG | Source | Severity | Resolution |
|------|--------|----------|------------|
| MQ-FLAG-1 | mq-verdict.md (π magnitude) | Material | §7 limitation 2 rewritten: π is ~99.99% of Z_cap at canonical fixtures (\|π\|_TP1 = 4687.73 vs Z_cap_TP1 = 4687.94), per `Z_cap_pinned.SIGN_VERDICTS.md` row TP1. Earlier "~5% of nominal" claim was wrong by ~20×. |
| MQ-FLAG-2 | mq-verdict.md (uniform CI table) | Material | §4.4 sign-cert table now reports per-TP CIs: TP1–TP3 share [168.17, 14606.14] (κ-only variation), TP4 = [176.58, 15336.38], TP5 = [159.76, 13875.90], per `Z_cap_pinned.json::sign_verdicts`. |
| MQ-FLAG-3 | mq-verdict.md (verbiage) | Minor | §1 "structurally viable" → "structurally well-formed … architecturally consistent under the synthetic-Bayesian regime". §8 honest framing preserved. |
| RC-FLAG-1 | rc-verdict.md ll. 49-59, 95-96 | Minor | §5 and §10 reconciled: "17 independent audit verdict files" → "31 verdict files across 7 audit cycles" (verified count: `find … -name "*.md" \| wc -l = 31`). |
| RC-FLAG-2 | rc-verdict.md ll. 61-64, 97-98 | Minor | §5 test-suite line replaced unverifiable "411 → 423" with the verifiable HEAD-pinned chain "423 at HEAD post-Phase 4 schema bump (vs 415 pre-Phase 3 nits sweep, vs 411 mid-CLOSE-Phase-1)". |

Citations: `scratch/2026-05-09-stage-2-memo-review/rc-verdict.md`,
`scratch/2026-05-09-stage-2-memo-review/mq-verdict.md`,
`simulations/saas_builder/data/Z_cap_pinned.json` (schema v1.1),
`simulations/saas_builder/data/Z_cap_pinned.SIGN_VERDICTS.md`.

---

*End of Stage-2 verdict memo. Independent RC + MQ re-verify is dispatched by
the orchestrator before commit.*
