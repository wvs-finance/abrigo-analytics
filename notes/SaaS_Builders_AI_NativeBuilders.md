**import [](./PRIMITIVES.md)**

# SaaS Builders / AI-Native Builders — cohort instantiation of $a_s$

Cohort instantiation of `notes/PRIMITIVES.md` §4.2 for solo AI-native LATAM
builders. All math objects below are specializations of numbered primitives
in PRIMITIVES.md; freestanding equations have been removed. Open questions
are now labeled cohort-calibration TODOs, not free `?` symbols.

**Notation.** Per PRIMITIVES.md §1, §6. Cohort assignment: $X = $ USD,
$Y = $ COP. FX paths $(X/Y)_t$, variance $\sigma_T$, and inversion
$\varepsilon(\sigma_T)$ inherit (6)–(8) verbatim.

---

# Cohort scope

- **Population.** Solo AI-native builders, post-revenue / pre-scale, MRR
  in COP, USD-denominated tooling and infra spend.
- **Location.** Colombia primary; broader LATAM secondary.
- **Cash-flow denomination.** Revenue COP; cost USD (recurring obligations).

# Profit — specialization of (5')

Per PRIMITIVES.md (5') the per-user balance sheet is

$$
a_s \;=\; \Upsilon \;-\; \sum_t \frac{q_t}{(X/Y)_t}.
$$

For this cohort, the rolling-horizon form is

$$
a_s^{(T)} \;=\; \sum_{t=0}^{T} \Upsilon_t \;-\; \sum_{t=0}^{T} \frac{q_t}{(X/Y)_t},
\tag{S1}
$$

with $\Upsilon_t$ the COP MRR stream and $q_t$ the USD-denominated
obligation schedule. The freestanding symbol $\Pi_i^{(T)}$ from the prior
draft is identified with $a_s^{(T)}$ — we carry the PRIMITIVES.md name.

**FX-vol sensitivity (resolves the prior open `?`).** From (10):

$$
\frac{\partial a_s^{(T)}}{\partial \sigma_T} \;=\; \Delta^{(a_s)} \;<\; 0.
$$

Sign inherited from §2 / §4.2 (builder is structurally short
$\sigma(X/Y)$). Magnitude scales with $\sum_t q_t f_t / (X/Y)_t^2$ —
*concentration of large $q_t$ in COP-weak regimes amplifies the loss*.

**Thin-margin condition.** Operationally, the design targets the cohort
parameter region where $|\Delta^{(a_s)}|$ is large — high $q_t/\Upsilon_t$
ratio and high stickiness. This replaces the prior freestanding
"thin margin" sketch.

# Cost — specialization of §4.2

Per §4.2, decompose the USD obligation:

$$
q_t \;=\; q_t^{\text{det}} \;+\; q_t^{\text{sticky}}.
\tag{S2}
$$

COP-denominated period cost is $q_t / (X/Y)_t$.

**$q_t^{\text{det}}$ — deterministic recurring USD floor.** Starting pin:

- $\bar C \;\approx\; 100$ USD/month (Claude Code Pro + baseline AWS
  reservations).
- $q_t^{\text{det}} = \bar C$ for all $t$.

Cohort distribution $(\bar C^{P10}, \bar C^{P50}, \bar C^{P90})$ across
LATAM solo AI-builders is **TODO-COHORT-1** — DevSurvey-style sourcing per
§4.2 calibration sources.

**$q_t^{\text{sticky}}$ — usage / commitment component. Primary form: one-sided ratchet.**

$$
q_t^{\text{sticky}} \;=\; \max\!\big(q_{t-1}^{\text{sticky}},\; \bar c \cdot (X/Y)_t\big),
\tag{S3}
$$

$\bar c$ a cohort-specific commitment density. Rationale: SaaS-style
commitments (AWS reserved instances, annual subscriptions, OpenRouter
prepaid credits) do not refund or scale down within-period when
$(X/Y)_t$ falls; they ratchet up when it rises.

Sensitivity arms (PRIMITIVES.md §15): linear pass-through
$q_t^{\text{sticky}} = \bar c (X/Y)_t$; commitment-decay
$q_t^{\text{sticky}} = q_{t-1}^{\text{sticky}} \cdot e^{-\delta} + \bar c (X/Y)_t$.
Choice affects $\Gamma^{(a_s)}$ (second-order), not just $\Delta^{(a_s)}$.

**Sticky-form selection** is **TODO-COHORT-2**.

# Revenue — cohort specification of $\Upsilon_t$

$\Upsilon_t$ in (S1) is the per-user COP revenue stream. Primary form:

$$
\mathbb{E}\!\left[\Upsilon_{t+1} \mid \mathcal{F}_t\right] \;=\; \Upsilon_t,
\tag{S4}
$$

i.e. martingale on the level. Independence assumption:
$\operatorname{cov}(\Upsilon_t, (X/Y)_t) \approx 0$ — solo SaaS prices
locally in COP and FX pass-through to MRR is slow / small at this scale.

Sensitivity arms: AR(1) on $\log \Upsilon_t$ with churn parameter; pure
deterministic recurring with stochastic churn shocks. Both alter
forecastability of $\Upsilon$ but not the sign of $\Delta^{(a_s)}$.

**$\Upsilon$-form selection** is **TODO-COHORT-3**.

# Identification strategy

Sourcing channels for the cohort (no math; feeds §4.2 calibration):

- Twitter/X — AI-native builders.
- Discords / Telegram — CELO Buildathon group, AI-dev groups, no-code
  communities.
- LATAM-local — Platzi ecosystem, indie-hacker LATAM groups.
- DevSurvey-style — Stack Overflow, JetBrains, GitHub Octoverse LATAM
  cohort priors for $(\bar C, \overline\Upsilon, \text{stickiness})$.

**Ideal stage:** post-revenue, pre-scale, monthly recurring revenue.
Critical filter: per-user $a_s^{(T)} > 0$ today (the builder is solvent
absent the hedge); the CPO converts vol-induced runway compression into
a priced exposure rather than rescuing an already-insolvent agent.

# Pitch — math-grounded form

*"Your Claude Code bill in COP never exceeds $Z$ COP/month."*

Math interpretation per §9 (streamed-premium variant): $Z$ is the cap
such that

$$
\mathbb{E}\!\left[\frac{q_t^{\text{det}}}{(X/Y)_t} + \pi(t)\right] \;\le\; Z,
$$

where $\pi(t)$ is the streamed CPO premium paid to the $a_l$-side LP.
The cap is achievable iff the streamed premium is small relative to the
deterministic floor cost.

# Payoff — canonical CPO from §8

The builder buys the $a_s$-side leg of the CPO. Per (13):

$$
\Pi^{(s)}(\sigma_T) \;=\; K_s \,\sqrt{\sigma_T},
$$

with equilibrium $K_s = K_l$ (PRIMITIVES.md (14)) and the discrete 12-leg
IronCondor implementation per §11. Convexity is the $\sqrt{\cdot}$ shape;
perpetual / streamed-premium variant per §9 and §15 open item 4.

**Premium form.** Streamed: $\pi(t)$ in COP/month, paid continuously out
of $\Upsilon_t$. The perpetual-horizon $\pi(t) \leftrightarrow d\Pi/dt$
consistency derivation is **TODO-COHORT-4** (= PRIMITIVES.md §15 open
item 4).

# Today's non-CPO responses (baseline comparator)

The cohort's current responses to $\Delta^{(a_s)} < 0$ — none of these is
a $\Pi$ satisfying (11); they trade exposure *quantity*, not the price
of vol:

| Response | Effectiveness | Failure mode |
|---|---|---|
| Pass-through pricing (raise COP prices) | Low | Lag + competition from non-AI-native builders |
| Buffering (hold extra margin) | Low | Capital inefficient |
| Reduce usage (downgrade tier, cut features) | Medium | Kills growth |
| Dollarization (charge in USD) | Rare | Only feasible for exporters |

**Thesis claim.** The CPO is the first $\Delta^{(a_s)}$-neutralizing
instrument available to this cohort. They hedge quantity, not price; all
responses are reactive, none anticipatory.

**Operational evidence that $\Delta^{(a_s)} < 0$ binds.** When FX moves
adversely, builders report: reduce API calls, delay scaling, defer
features. This is empirical support for the §4.2 sign claim and the §15
"verification of $\Delta^{(a_s)} < 0$" open item — at the cohort
behavioral level the inequality already binds.

# Demand gate (out of scope for the (5') parametrization)

Adoption inequality (Stage-2/3 GTM, separate from the math model):

$$
\text{Pain} \times \text{Frequency} \times \text{Clarity} \;>\; \text{Adoption Friction}.
$$

Operationalization of each factor is a Stage-2 sourcing artifact, not
part of the $a_s$ parametrization. Tracked separately.

---

# Open cohort calibration TODOs (consolidated)

| Tag | Choice | PRIMITIVES.md anchor |
|---|---|---|
| TODO-COHORT-1 | $(\bar C^{P10}, \bar C^{P50}, \bar C^{P90})$ from DevSurvey-style sources | §4.2 calibration sources |
| TODO-COHORT-2 | Sticky-cost functional form (primary: ratchet (S3); arms: linear, decay) | §15 open item 3 |
| TODO-COHORT-3 | $\Upsilon_t$ functional form (primary: martingale (S4); arms: AR(1)-log-MRR, det+churn) | §4.2 mapping table |
| TODO-COHORT-4 | $\pi(t)$ streamed-premium derivation under perpetual horizon | §15 open item 4 |

These four are the genuine Stage-2 cohort-calibration deltas. The math
itself (sign, convexity, replication, equilibrium $K_l = K_s$) is
inherited from PRIMITIVES.md and is not re-derived here.
