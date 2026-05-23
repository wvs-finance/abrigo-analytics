**import [](./SaaS_Builders_AI_NativeBuilders.md)**

# STAGE_2_RESULTS — SaaS-Builder Stage-2 results anchor

Stage-2 frozen-state math anchor for the SaaS-builder cohort. Continuation of
the predecessor lineage `PRIMITIVES.md` → `SaaS_Builders_AI_NativeBuilders.md`.
All math objects are specializations of numbered primitives in PRIMITIVES.md
(tags `(1)`–`(20)`) or S-tagged equations in SaaS_Builders notes (`(S1)`–`(S4)`).
Equations introduced here carry R-prefix tags (R1, R2, …, R8). Per
PRIMITIVES.md §1, §6: cohort assignment $X = $ USD, $Y = $ COP; FX paths
$(X/Y)_t$, variance $\sigma_T$, and inversion $\varepsilon(\sigma_T)$ inherit
$(6)$–$(8)$ verbatim.

---

## §0 Cohort scope

Per SaaS_Builders (S1)–(S4): solo AI-native LATAM builders with COP-denominated
revenue $\Upsilon_t$ and USD-denominated obligation schedule $q_t$. Stage-2
delivered the synthetic-Bayesian closure of the four cohort-calibration TODOs
under the spec §5.2 24-bracket parameter family. Frozen state at HEAD
`9fd92e5`. No real-data calibration was performed at Stage-2; cohort-level
distributions remain synthetic priors. No magnitude claims are made; sign
certifications and form pins are the deliverables.

## §1 Empirical sign verdict

The PRIMITIVES.md (10) sign claim $\Delta^{(a_s)} < 0$ — inherited as the
universal SaaS_Builders structural-short property — is empirically confirmed
across the entire spec §5.2 24-bracket parameter family via synthetic
sign-certification testing under both the primary regime and the bank-spread
overlay (24/24 PASS each):

$$
\boxed{\;\Delta^{(a_s)} \;<\; 0 \quad \forall\, b \in \mathcal{B}_{24}\;}
$$

The universal-cohort sign claim from PRIMITIVES §2 / §4.2 thus holds
non-trivially over the empirically admissible parameter region for the
AI-native builder cohort.

## §2 Closed forms emerging from / corrected during Stage-2

### §2.1 σ₀ anchor (R1)

Inverting PRIMITIVES (8) $\varepsilon(\sigma_T) = \sqrt{8\sigma_T/\overline{(X/Y)}^2}$
yields the closed-form $\sigma_0$ anchor used by the Carr-Madan linearization
in PRIMITIVES (16):

$$
\boxed{\;\sigma_0 \;=\; \frac{\overline{(X/Y)}^{\,2} \cdot \varepsilon^{\,2}}{8}\;}
\tag{R1}
$$

At the canonical cohort fixtures $\overline{X/Y} = 4000$, $\varepsilon = 0.1$,
this gives $\sigma_0 = 20{,}000$. R1 is the constant against which the
linearized constant $\hat K = K^\star/(2\sqrt{\sigma_0})$ from PRIMITIVES (17)
is computed and against which the perpetual streamed-premium identity (R3) is
validated.

### §2.2 π(t) closed form (R2)

The streamed-premium variant promised in PRIMITIVES §15 open item 4 (and
labelled TODO-COHORT-4 in SaaS_Builders) is closed at Stage-2. The derivation
chain is: PRIMITIVES (6) deterministic FX path → (8) variance proxy inversion
→ (10) $\Delta^{(a_s)}$ closed form → §10 Carr-Madan linearization
$\Pi \approx \hat K \sigma_T$ from (17) → §15 perpetual identity
$\pi(t)\,dt \leftrightarrow d\Pi_{\text{lin}}/dt$. The result:

$$
\boxed{\;
\pi(t) \;=\; \frac{K^\star \cdot \varepsilon^{\,2} \cdot \overline{(X/Y)}^{\,2} \cdot \big(4\omega t \cos(4\omega t) - \sin(4\omega t)\big)}{64 \cdot \omega \cdot \sqrt{\sigma_0} \cdot t^{\,2}}
\;}
\tag{R2}
$$

with free symbols $\{K^\star,\, \sigma_0,\, \varepsilon,\, \omega,\, t,\, \overline{X/Y}\}$.
Crucially, $\kappa \notin \mathrm{free\_symbols}(\pi)$.

*Aside on the v0.2 → v0.3 derivation correction.* An earlier draft included a
spurious $1/\kappa$ factor and dropped the $\overline{(X/Y)}^{\,2}$ prefactor;
both errors were corrected during the cycle. The post-correction form has
$\kappa \notin \mathrm{free\_symbols}(\pi)$ — accordingly, the M2 monotonicity
expectation was re-pinned from $\partial|\pi|/\partial\kappa < 0$ to
$\partial|\pi|/\partial(\overline{X/Y}) > 0$ per the PRIMITIVES.md §6 anchor.
The case-study pathology+detection+fix narrative is recorded in
`feedback_post_hoc_fit_anti_fishing_pattern.md`; the math is the record here.

### §2.3 Perpetual identity (R3)

The Carr-Madan-linearized payoff from PRIMITIVES (16) yields, under
differentiation w.r.t. $t$ along the deterministic path (6),
$\mathrm{simplify}\big(\pi(t) - d\Pi_{\text{lin}}/dt\big) = 0$ symbolically:

$$
\pi(t)\,dt \;=\; \frac{d\Pi_{\text{lin}}}{dt}\,dt
\tag{R3}
$$

Numerical residual on a 5000-point uniform grid over $t \in (0, T]$ is
$\le 6.31 \times 10^{-9}$. R3 is the perpetual-horizon analogue of the
$T$-integrated equilibrium identity $K_l = K_s$ from PRIMITIVES (14):
the streamed premium is the time-derivative of the linearized payoff.

### §2.4 spec §5.2 24-bracket parameter family (R4)

The empirical sign-cert grid is the Cartesian product

$$
\mathcal{B}_{24} \;=\; \{\text{Pro},\, \text{Max5x},\, \text{Max20x}\} \times \{1.5,\, 2.0\} \times \{\text{low},\, \text{high}\} \times \{\text{nominal},\, \text{doubled}\}
\tag{R4}
$$

with index sets (tier, $\alpha_{\text{arm}}$, $h_{\text{cache}}$,
$\kappa_{\text{arm}}$) per spec §5.2 lines 383–388, $|\mathcal{B}_{24}| = 24$.
Empirically: $\Delta^{(a_s)} < 0$ across all 24 brackets under both the
primary regime and the bank-spread overlay (24/24 PASS each).

### §2.5 C1 marginalization equivalence (R5)

At fixed $(\pi, \mu, \varphi, \alpha, x_m)$, the marginalized log-likelihood
over the three discrete latents $(\text{tier\_idx},\, n_{\text{per\_day}},\, n_{\text{month}})$
equals the explicit-Categorical log-likelihood (LSE over tiers):

$$
\sum_{\text{tier}_i,\, n_d,\, n_m} P(\bar C \mid \text{tier}_i, n_d, n_m)\, P(\text{tier}_i, n_d, n_m) \;=\; P(\bar C)
\tag{R5}
$$

The sum-out is exact, not approximate: at Stage-2 resolution the three
discrete latents do not condition the $\tau_t$ likelihood (per-tier $\theta_k$
differentiation deferred to Stage-3 per spec §5.4 hint), so the joint
factorizes and the marginalization is analytic.

## §3 TODO-COHORT-N closures

The four TODO-COHORT-N labels left open in `notes/SaaS_Builders_AI_NativeBuilders.md`
are resolved as follows:

| Tag | Outcome | R-tag |
|---|---|---|
| TODO-COHORT-1 | DEFERRED — synthetic only; no DevSurvey real data at Stage-2 | (Stage-3 §5) |
| TODO-COHORT-2 | CLOSED via softplus regularizer + M2 tightness | R6 |
| TODO-COHORT-3 | INDISTINGUISHABLE per spec §9; tractability-pinned to det+churn | R7 |
| TODO-COHORT-4 | CLOSED at §2.2 (streamed-premium derivation under perpetual horizon) | R2 |

### §3.1 TODO-COHORT-1 — $\bar C$ distribution (DEFERRED)

The cohort distribution $(\bar C^{P10}, \bar C^{P50}, \bar C^{P90})$ over LATAM
solo AI-builders requires DevSurvey-style sourcing per PRIMITIVES.md §4.2
calibration sources. No real-data instrument was deployed at Stage-2; the
synthetic prior $\bar C \approx 100$ USD/month carried forward unchanged from
SaaS_Builders. Closure is a Stage-3 hand-off (§5).

### §3.2 TODO-COHORT-2 — sticky-cost form (CLOSED, R6)

Replacing the SaaS_Builders (S3) one-sided ratchet primary with a smooth
softplus regularizer that admits gradient-based posterior inference:

$$
q_t^{\text{sticky}} \;=\; \beta^{-1} \log\!\big(1 + e^{\beta\,\bar c (X/Y)_t}\big),
\qquad \big\|\,\mathrm{softplus}_\beta - \mathrm{ReLU}\,\big\|_{L^1[0,\,2\kappa]} \;<\; 10^{-3}\,\kappa
\tag{R6}
$$

with $\beta$ chosen as the smallest value satisfying the M2 tightness bound.
Sensitivity arms (linear pass-through, commitment-decay) deferred to Stage-3
per PRIMITIVES.md §15 open item 3.

### §3.3 TODO-COHORT-3 — $\Upsilon_t$ form (INDISTINGUISHABLE, R7)

The three closed-set candidates (martingale (S4), AR(1)-log, det+churn) were
compared via PSIS-LOO-CV across the spec §5.2 grid. The pairwise verdict
$\Delta\mathrm{elpd}/\mathrm{SE} = 1.67 < 2.0$ (Pin R3 threshold) →
**INDISTINGUISHABLE** per spec §9. For tractability, spec v1.2.1 §6.1 pins the
det+churn form:

$$
S_t \;=\; (1 - \lambda)^{t}, \qquad \lambda \;\sim\; \mathrm{Beta}(4.5,\, 95.5)
\tag{R7}
$$

The HALT-on-flip semantic is preserved verbatim from spec v1.2.1: any
Stage-3 evidence flipping the LOO ranking against det+churn triggers HALT, not
a soft form re-selection. No flip was detected against the legacy
$\mathrm{Beta}(2.0,\, 38.0)$ prior at Stage-2 freeze.

### §3.4 TODO-COHORT-4 — $\pi(t)$ under perpetual horizon (CLOSED, R2)

Closed at §2.2; cross-reference (R2). The streamed-premium $\pi(t)$ derivation
under perpetual horizon resolves the SaaS_Builders streamed-premium claim and
PRIMITIVES.md §15 open item 4 simultaneously.

## §4 Z_cap pinned

The streamed-premium cap from the SaaS_Builders pitch (S5) — *"your Claude
Code bill in COP never exceeds $Z$ COP/month"* — formalizes via the
PRIMITIVES (15) streamed-premium variant of the buyer/seller split:

$$
\boxed{\;
\mathbb{E}\!\left[\frac{q_t^{\,\text{det}}}{(X/Y)_t} + \pi(t)\right] \;\le\; Z_{\text{cap}}
\;}
\tag{R8}
$$

Stage-2 pin (synthetic, sign-cert grade, NOT a magnitude prediction):
$Z_{\text{cap}} = 4{,}687.94$ COP/month with 95% CI $[168.17,\, 14{,}606.14]$ at
test-point TP1. Per-test-point CIs vary monotonically with the FX bracket per
Pin M2. All 5/5 sign-certification test points PASS.

## §5 Stage-3 open items

Math-form hand-off; no engineering checklist; no magnitude promises.

1. Real-data conditioning of the cohort $\Upsilon_t$ and $q_t$ distributions —
   closes TODO-COHORT-1 with empirical $(\bar C^{P10},\, \bar C^{P50},\, \bar C^{P90})$
   per PRIMITIVES.md §4.2 calibration sources.
2. Stochastic-FX variant per PRIMITIVES.md §15 open item 2 — replace the
   deterministic generator (6) with GBM, OU, jump-diffusion, or
   empirical-calibrated SDEs while preserving (8)'s
   $\varepsilon \leftrightarrow \sigma_T$ inversion in distribution.
3. Per-tier $\theta_k$ differentiation per spec §5.4 hint — resolves the
   structural near-prior $\pi$ posterior observed at Stage-2 resolution and
   converts R5's exact analytic sum-out into a genuine information-bearing
   marginalization.
4. Hierarchical pooling for C3 across multiple synthetic trajectories —
   resolves the single-trajectory limitation under which the
   $\Upsilon_t$-form selection (R7) returned INDISTINGUISHABLE.
5. Weibull $k \neq 1$ falsification of $S_t = (1-\lambda)^t$ as the nested
   null per spec v1.2.1 §6.1 Stage-3 falsification path.
6. On-chain Panoptic discrete-strip deployment per PRIMITIVES.md §11 — the
   12-leg IronCondor implementation $\Pi_T \approx \sum_j w_j \mathrm{Condor}_j(S_T)$
   from (20), with the $a_l$ vault simultaneously deployed by the protocol per
   PRIMITIVES.md §4.1.

## §6 Reproducibility

Stage-2 freeze pin: HEAD `9fd92e5` ("deliverable(saas-cohort): Stage-2
modeling memo + Phase-4 schema-bump audit"). Anchor sha256 hashes (full sha
for the two main artifacts; tails for the supplementary):

- `Z_cap_pinned.json::audit_block` = `1fb1f7a42131268f3448da8d61b685ce27fe1facf356122e557ac10d329b5d31`
- `gate_verdict.json::audit_block` = `4da660b55e7ad33071711dc313f12a4d06283717e7a332a7f7ddcd8a19672173`
- `revenue_form_verdict.json::audit_block` = `588a491b…8adb`
- `_AUDIT.json::audit_block` = `ded06012…162a`

Verification:

```
python3 -c "import json;print(json.load(open('simulations/saas_builder/data/Z_cap_pinned.json'))['audit_block'])"
```

## §7 References

- `notes/PRIMITIVES.md` — anchors used: §1 cash-flow primitive, §6 variance proxy, §7 $\Delta$ closed forms, §8 CPO neutralizing payoff, §10 Carr-Madan, §11 discrete strip, §15 open items.
- `notes/SaaS_Builders_AI_NativeBuilders.md` — cohort instantiation; (S1)–(S4); pitch form (S5).
- `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` — spec v1.2.1.
- `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md` — Stage-2 verdict memo.
