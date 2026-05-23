# $S_t$ Functional-Form Literature Survey — SAAS-COHORT-CLOSE Phase 0 Task 0.1

**Status.** Methodology-led recommendation. Author has NOT read C3 v0.3 implementation
code (`simulations/saas_builder/cohort_3/models.py`) prior to producing this survey,
per CLOSE plan v0.2 BLOCK-2 anti-fishing constraint. This document adjudicates spec
v1.1.1 §5 Det+churn ambiguity in $S_t$ on the basis of literature evidence and
cohort-specific economic semantics for solo AI-native LATAM builders, not on the
basis of what the existing implementation computes.

## §1. Question

Spec v1.1.1 §5 (Det+churn sensitivity arm for $\Upsilon_t$) introduces a per-builder
cohort-survival process $S_t = \Pr[\text{builder still active at }t \mid \text{active at }t-1]$
but does **not** pin a functional form. Candidates:

1. **Deterministic factor** — $S_t = (1-\lambda)^t$, single hazard $\lambda$, equivalent
   to constant-hazard exponential survival in discrete time. **1 free parameter.**
2. **Bernoulli per-step** — $S_t = \prod_{s=1}^{t}(1-\lambda_s)$ with per-step hazards
   that may be time-varying or stochastic. **$t$ or 2–3 parameters in covariate form.**
3. **Continuous-time exponential** — $S(t) = e^{-\lambda t}$. **1 parameter.**
4. **Weibull** — $S(t) = e^{-(\lambda t)^k}$, shape $k$. Decreasing ($k<1$),
   constant ($k=1$, reduces to exponential), or increasing ($k>1$) hazard.
   **2 parameters.**
5. **Gompertz** — $S(t) = e^{-(b/\eta)(e^{\eta t}-1)}$. Hazard rises geometrically.
   Common in actuarial / mature-SaaS literature. **2 parameters.**
6. **Other** — Pareto-tailed mixtures (BG/NBD heterogeneity); discrete-time
   complementary log-log hazard; Beta-Geometric.

## §2. Method

- arxiv MCP search across `stat.AP`, `stat.ML`, `cs.LG` for SaaS-churn / survival
  treatments (priority per CLAUDE.md global instructions).
- WebSearch for industry benchmarks (Recurly, Paddle, Indie Hackers community)
  to pin order-of-magnitude monthly churn for the prosumer / solopreneur segment.
- WebSearch for organizational-ecology liability-of-newness evidence on hazard
  shape for nascent ventures (Stinchcombe and successors).
- Read `notes/PRIMITIVES.md` and `notes/SaaS_Builders_AI_NativeBuilders.md`
  to anchor the cohort-specific semantics; read spec §5/§6/§8 for what
  Det+churn must compose with.
- Did NOT open `simulations/saas_builder/cohort_3/`.

## §3. Findings per option

### 3.1 Deterministic factor / constant-hazard exponential ($S_t = (1-\lambda)^t$)

**Literature.** This is the workhorse retention specification in B2B/B2C SaaS
practice. Reichheld's classic retention-math identity ($CLV \approx ARPU /
(1 - r) = ARPU/\lambda$ for monthly churn $\lambda$) implicitly assumes a
constant hazard, i.e. exponential survival. Industry benchmark surveys
(Recurly, Paddle, Indie Hackers community guides) report the prosumer /
solo-targeting segment as roughly **4–5% monthly churn** with a *single*
headline rate, not a hazard curve — operationally an exponential-survival
assumption.

**Cohort fit (solo AI-native LATAM builders).** The cohort is post-revenue,
pre-scale, paying ~$100–200 USD/month in tooling against COP MRR. There is
**no calendar event** that would make hazard concentrate at a known horizon;
churn is event-driven (FX shock, side-project abandonment, full-time-job
absorption) and approximately memoryless conditional on the macro state.
Memorylessness is the defining property of constant hazard.

**Strengths.** Maximally parsimonious (1 parameter). Closed-form; differentiates
analytically; trivial to simulate; no identification risk under the synthetic-
Bayesian regime.

**Weaknesses.** Cannot represent honeymoon effects (low early hazard rising
later) or liability-of-newness effects (high early hazard falling later).

### 3.2 Bernoulli per-step with time-varying $\lambda_s$

**Literature.** Equihua et al. (2023) and Buginga & de Souza e Silva (2024)
extend BG/NBD to deep-survival models with per-period covariate-driven
hazards; Gao et al. (2024) propose tensorized latent-factor block-hazard
models. All require N >> per-step parameter count to identify.

**Cohort fit.** Stage-2 is **synthetic-Bayesian** — there is *no* real-cohort
panel of monthly active/inactive observations. A per-step $\lambda_s$ schedule
is unidentified absent priors that effectively collapse it back to a
parametric form. The cohort sample size for Stage-3 (n=30–75 per
RESEARCH.md §6) is below the threshold at which a freely-time-varying
hazard would be cleanly recoverable.

**Strengths.** Most flexible.

**Weaknesses.** Severely violates parsimony in a no-data regime.
Anti-fishing-suspect: free per-step parameters could absorb
$\Upsilon_t$ form mis-specification and contaminate the spec §6 PSIS-LOO-CV
ranking across the four $\Upsilon_t$ candidates.

### 3.3 Continuous-time exponential $S(t) = e^{-\lambda t}$

**Literature.** Identical in shape to (3.1) when $(1-\lambda) = e^{-\lambda'}$;
choice between the two is a discretization convention.

**Cohort fit.** The cohort is observed at **monthly granularity** (MRR cycles,
Anthropic Pro billing, AWS billing). Discrete-time form (3.1) matches the
observation cadence. Continuous-time form forces an avoidable
exp/log conversion at each gate evaluation.

### 3.4 Weibull $S(t) = e^{-(\lambda t)^k}$

**Literature.** Han et al. (2018, arxiv:1808.03831) show Weibull-based sample
size formulas are most robust across the exponential / Weibull / Gompertz
trio in time-to-event trials — Weibull *nests* exponential at $k=1$.
Stinchcombe's liability-of-newness construct (Wharton 2016 restatement;
Aalto IJMR review 2020) predicts $k < 1$ (decreasing hazard) for new
organizational forms — most failures happen early; survivors stabilize.
Indie Hackers / SaaS practitioner literature occasionally invokes
"honeymoon" effects ($k > 1$, rising hazard once free trials end), but
the empirical evidence is mixed and segment-specific.

**Cohort fit (solo AI-native LATAM builders).** A liability-of-newness
argument *would* apply to the **business** (the SaaS company itself)
but the survival object here is **the builder remaining a paying user
of the AI tooling cohort**, not the survival of their company. These two
are correlated but distinct. For the tooling-cohort survival object,
there is no clear theoretical prior for $k \ne 1$:
- Anthropic Pro / Max billing has no honeymoon discount → no $k>1$ kink.
- The AI-native builder population is *self-selected for tool affinity* by
  the time they are paying $\geq\$100$/month → no $k<1$ infant-mortality
  spike either.

**Strengths.** Nests exponential (testable null $k=1$).

**Weaknesses.** 2 parameters, no theoretical anchor for $k$, no real data to
estimate $k$ at Stage-2.

### 3.5 Gompertz $S(t) = e^{-(b/\eta)(e^{\eta t}-1)}$

**Literature.** Standard in actuarial mortality and sometimes in
mature-customer-base churn modeling. EL-Damcese et al. (2014) and the
generalized Gompertz-Weibull-power-series family (Tahmasebi & Jafari,
2015) catalog the algebraic properties.

**Cohort fit.** Gompertz hazard $h(t) = b\,e^{\eta t}$ rises geometrically
with $t$. This is appropriate for biological aging or long-tenure customer
attrition where increasing wear-out is documented. There is no economic
mechanism by which a solo AI-native builder's exit hazard would rise
geometrically with tenure inside the cohort. Importing Gompertz here
would be a biological-metaphor smuggle, not a substantive choice.

### 3.6 Other (BG/NBD, cloglog, Pareto/NBD)

**Literature.** Fader & Hardie's BG/NBD models customer-base purchase frequency
as Poisson + Beta-mixed dropout — a **non-contractual** setting where churn
is unobserved between purchases (Zammit & Zerafa, 2025, arxiv:2502.12912).
The AI-builder cohort here is **contractual** (monthly subscription billing
makes churn directly observable each month), so BG/NBD's headline complexity
is unwarranted. Discrete-time complementary-log-log models (Tsubota & Beppu,
2025, arxiv:2506.00889; Alam & Linero, 2025, arxiv:2502.00606) are the
principled choice if covariate-conditional discrete-time hazards are
needed — but again, Stage-2 has no covariates and no panel data.

## §4. Parsimony argument under synthetic-Bayesian regime

Stage-2 has **no real cohort survival panel**. The Det+churn arm exists *as
a sensitivity arm against the martingale primary* under PSIS-LOO-CV (spec §9
verdict thresholds). Adding shape-flexibility ($k$ in Weibull, $\eta$ in
Gompertz, $\lambda_s$ trajectory in Bernoulli) without data will:

- Inflate posterior uncertainty without informative-likelihood pull.
- Make the Det+churn arm artificially "look worse" (or "look better,"
  depending on prior tightness) in PSIS-LOO-CV vs. martingale and AR(1).
  Either direction *contaminates* the spec §6 $\Upsilon_t$ form-selection
  verdict — exactly the contamination that prereg-locking tries to prevent.
- Enlarge the prior-predictive variance of $a_s^{(T)}$ enough that the
  spec §8(1) sign-pre-pin (HALT on $\Delta^{(a_s)}$ sign reversal at any
  bracket point) becomes *easier to spuriously trip* on Monte-Carlo noise.

Parsimony favors **option (3.1) deterministic factor / constant hazard**.

## §5. Recommendation

**Top recommendation: $S_t = (1-\lambda)^t$ (deterministic factor;
constant-hazard discrete-time exponential), with a single $\lambda$ pinned
by industry-benchmark prior $\lambda \sim \text{Beta}(\alpha_0, \beta_0)$
calibrated to median $\approx 0.04$–$0.05$ monthly per Recurly/Paddle/Indie
Hackers prosumer-segment benchmarks.**

Rationale: (i) matches monthly observation cadence of the AI-tooling
subscription billing cycle; (ii) memoryless hazard is the appropriate
default given event-driven, FX-shock-correlated builder exit, with no
calendar-tied honeymoon or wear-out mechanism; (iii) Reichheld retention
math implicitly assumes this form across all SaaS practitioner literature;
(iv) maximally parsimonious — one parameter, identifiable under cohort
prior alone, leaves the spec §6 $\Upsilon_t$ form-selection LOO-CV
ranking uncontaminated; (v) nested null inside Weibull, allowing a
Stage-3 robustness check at $k\ne 1$ once a real cohort panel exists.

**Runner-up 1: Weibull with $k$-prior centered tightly at $1$**
(e.g., $k \sim \text{LogNormal}(0, 0.2)$). Adds one parameter; allows
Stage-3 falsification of memorylessness without committing to a specific
deviation direction. Reject as primary because the second parameter is
unjustified at Stage-2 with no data.

**Runner-up 2: BG/NBD-style Beta-Geometric mixture
($\lambda \sim \text{Beta}$ over the cohort)**. Aligns with
heterogeneity in builder type (solo vs. team-of-one, COP-MRR vs. mixed
USD-revenue). Reject as primary because heterogeneity is already
captured by the per-builder distribution structure of the cohort posterior;
adding a second-level mixture is double-counting.

## §6. Methodology consequence — will this change C3 v0.3 ELPD ranking?

Reasoning from first principles, without reading C3 code:

The Det+churn arm of $\Upsilon_t$ is one of four candidates competing in
the spec §6 PSIS-LOO-CV ranking against martingale (primary), AR(1)-log-MRR,
and pure deterministic-no-churn. Under the recommended $S_t = (1-\lambda)^t$
the Det+churn form has a single extra parameter ($\lambda$) over pure-det,
and ELPD already discounts that via the LOO penalty term.

If the C3 v0.3 implementation already uses $S_t = (1-\lambda)^t$ (which
the plan brief reports as the implementer's choice), then this recommendation
**produces a no-op confirmation under Task 0.2b** — the spec amendment
ratifies the existing implementation, and the ELPD ranking is unchanged.

If, hypothetically, C3 v0.3 used a Weibull or Gompertz form, the
recommendation would force a re-fit. The expected effect on ELPD ranking:
the Det+churn arm's elpd would *rise* (fewer effective parameters under
LOO penalty), *making it more competitive* against martingale rather than
less. Because the Stage-2 sample size is small and posterior predictive
variance is dominated by the heavy-tail Pareto-cost component (spec §5.1
TruncPareto $\alpha \in [1.5,2.5]$), I expect the SE of the elpd
difference to be large enough that the **PASS / WEAK / MARGINAL / FAIL /
INDISTINGUISHABLE routing** in spec §9 would be **stable to this
re-parameterization** with high probability — i.e., if the v0.3 ranking
returned INDISTINGUISHABLE or MARGINAL, the post-amendment ranking is
expected to also fall into the same band.

Pareto-$\hat k$ sensitivity: deterministic-factor $S_t$ produces
*lower* per-observation contribution to log-likelihood variability than
a parameter-richer survival form; $\hat k$ diagnostics should remain at or
below the v0.3 baseline. Risk of new bad-$\hat k$ observations is **low**.

**Bottom line.** With probability $\gtrsim 0.8$ (subjective), this
recommendation is a no-op against C3 v0.3; with probability $\lesssim 0.2$
it triggers a re-fit whose ELPD ranking band is preserved. Either way,
the spec §6 $\Upsilon_t$ verdict should not flip. Plan Task 0.2b's
HALT-on-flip mechanic remains the appropriate safeguard.

## §7. Citations

1. Zammit, D. & Zerafa, C. (2025). *A Simplified and Numerically Stable
   Approach to the BG/NBD Churn Prediction Model.* arxiv:2502.12912 —
   canonical BG/NBD reference; documents non-contractual setting where
   BG/NBD is applicable, contrasting with this cohort's contractual
   billing.

2. Han, D., Hou, Y., & Chen, Z. (2018). *Sample size determination in
   superiority or non-inferiority clinical trials with time-to-event data
   under exponential, Weibull and Gompertz distributions.* arxiv:1808.03831
   — direct comparison of exponential vs. Weibull vs. Gompertz showing
   Weibull as the most robust nesting form, exponential as the most
   parsimonious special case.

3. Equihua, J. P., Nordmark, H., Ali, M., & Lausen, B. (2023). *Modelling
   customer churn for the retail industry in a deep learning based
   sequential framework.* arxiv:2304.00575 — contemporary deep-survival
   framework illustrating the data demands of free time-varying hazards;
   substantiates the parsimony argument under no-data Stage-2 regime.

4. Tsubota, Y. & Beppu, K. (2025). *Improved Risk Ratio Approximation by
   Complementary Log-Log Models.* arxiv:2506.00889 — discrete-time hazard
   alternative to logistic; cited as principled covariate-extension form
   if Stage-3 data warrants.

5. Reichheld, F. & SaaS practitioner benchmarks — Recurly Customer Churn
   Benchmarks (https://recurly.com/research/churn-rate-benchmarks/);
   Paddle "SaaS churn rate"
   (https://www.paddle.com/blog/saas-churn-rate); Indie Hackers /
   ChurnFree B2B SaaS Churn Rate Benchmarks. Industry pin: prosumer /
   solo-targeted SaaS monthly churn ≈ 4–5%, a single-rate benchmark
   that operationally assumes constant-hazard / exponential survival.

6. Stinchcombe, A. (1965, restated in *Social Science Research* 2017,
   doi:10.1016/j.ssresearch.2016.10.011; Soto-Simeone, Siren, Antretter
   *International Journal of Management Reviews* 2020). *Liability of
   newness.* — Canonical organizational-ecology evidence for $k<1$
   Weibull hazards in **firm survival**, distinct from the **cohort-
   tooling-subscription-survival** object modeled here; cited to
   justify why the LoN-implied Weibull-with-$k<1$ is *not* applicable
   to $S_t$ in this spec.

7. Buginga, G. & de Souza e Silva, E. (2024). *Clustering Survival Data
   using a Mixture of Non-parametric Experts.* arxiv:2405.15934 —
   contemporary nonparametric churn-survival technique cited as the
   over-parameterized end of the parsimony spectrum.
