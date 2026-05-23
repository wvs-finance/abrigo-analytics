# PRIMITIVES — $a_s$ / $a_l$ / CPO mathematical primitives

Self-contained math reference for the (a_s, a_l) framework and the Convex Payoff
Option (CPO). Faithful to the canonical sources; per-user sharpening and
on-chain identities incorporated inline.

**Provenance**
- Primary derivation: `~/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/notes/2026-04-29-macro-markets-draft-import.md`
- Per-user $a_s$ sharpening: `scratch/path-b-stage-2/phase-1/corrections_iota_a_s_framing.md` (CORRECTIONS-ι, 2026-05-04)
- Substrate scope claim: `scratch/path-b-stage-2/phase-1/corrections_theta_substrate_scope_clarification.md` (CORRECTIONS-θ)
- Discrete strip + verification: `docs/specs/2026-04-30-pair-d-stage-2-A-fork-simulate-spec.md` (Path A)
- LVR identity + a_s synthetic generation: `docs/specs/2026-04-30-pair-d-stage-2-B-on-chain-data-spec.md` v1.4 (Path B)

---

## §1. Cash-flow primitive

For an economic agent (App) $a$ exposed to FX volatility $\sigma(X/Y)$:

$$
CF_T^{(a)} \;=\; \overbrace{I_T^{(a)}\!\left(\sigma(X/Y)\right)}^{\text{inflow}} \;-\; \overbrace{O_T^{(a)}\!\left(\sigma(X/Y)\right)}^{\text{outflow}}
$$

First- and second-order vol-sensitivities:

$$
\Delta^{(a)} \;=\; \frac{\partial}{\partial \sigma(X/Y)}\, CF_T^{(a)} \qquad
\Gamma^{(a)} \;=\; \frac{\partial^2}{\partial \sigma(X/Y)^2}\, CF_T^{(a)}
\tag{1}
$$

## §2. Sign requirements — $(a_s, a_l)$ pair

For a CPO market to clear, two counterparty types are needed:

$$
\underbrace{\Delta^{(a_s)} < 0}_{\text{economically short } \sigma(X/Y)} \qquad
\underbrace{\Delta^{(a_l)} > 0}_{\text{economically long } \sigma(X/Y)}
$$

- $a_s$ — *short-vol* agent, hurt by FX dispersion. The CPO **buyer**.
- $a_l$ — *long-vol* agent, paid by FX dispersion. The CPO **seller** /
  liquidity provider.

## §3. $a_l$ — yield-vault instantiation

USD-denominated vault that earns LP fees proportional to realized FX
movement (the path-roughness fee model):

$$
CF_T^{(a_l)} \;=\; \sum_{t=0}^{T} r_{(a_l)}\, \big|\, (X/Y)_t - (X/Y)_{t-1}\, \big|
\tag{2}
$$

**On-chain identity (LVR / Milionis-Moallemi-Roughgarden):** for the LP NET
position, $\mathrm{LVR} \propto \sigma^2$ (instantaneous). This is the
canonical *short-variance* form that materializes in real Mento V3 / Uniswap
V3 LP P&L. Path B v1.4 reconstructs $CF^{(a_l)}$ as **LP gross fees** (the
form in (2)), which is what the CPO seller earns *before* IL — distinct from
LP NET. Both forms are long-realized-roughness; the CPO uses the gross-fee
form.

## §4. $a_s$ — payment-rail instantiation (one cohort; **not** universal)

> **Cohort note.** The derivation in §4 is the *payment-app* instantiation —
> a user holds a deposit in $Y$ and owes a fixed obligation $B_T$ in $X$
> (e.g. a remittance recipient, a recurring-bill payer). It is **one
> example** of an $a_s$ population, not a definition of $a_s$. Other
> cohorts (e.g. AI-native solo builders, §4.2) share the universal balance
> sheet (5') but have **different $\Upsilon$ and $q_t$ semantics**, no
> fixed $B_T$, and may be perpetual rather than $T$-horizoned.

Payment app guaranteeing fixed obligations $B_T$ in $X$ for users who deposit
$Y$. Allocation of user deposit $D_0^{(Y)}$:

$$
\theta\, D_0^{(Y)} \text{ : yield-vault portion} \qquad
(1-\theta)\, D_0^{(Y)} \text{ : liquid buffer},\quad \theta \in [0,1]
$$

Yield dynamics:

$$
\Upsilon_T(r,\, \theta D_0^{(Y)},\, T) \;=\; \theta D_0^{(Y)} \cdot (1 + rT)
\tag{3}
$$

Sourcing problem — minimize $X$-cost of the obligation under FX path
$(X/Y)_t$:

$$
\min_{\{q_t\}_{t=1}^T}\; \sum_{t=1}^{T} \frac{q_t}{(X/Y)_t}
\quad\text{s.t.}\quad \sum_{t=1}^{T} q_t\, (X/Y)_t = B_T,\;\; q_t > 0\;\forall t
\tag{4}
$$

Resulting $a_s$ cash flow (gross of payoff $\Pi$):

$$
CF_T^{(a_s)} \;=\; \Upsilon_T(r,\, \theta D_0^{(Y)},\, T) \;-\; \sum_{t=1}^{T} \frac{q_t}{(X/Y)_t}
\tag{5}
$$

### §4.1 Per-user $a_s$ sharpening (CORRECTIONS-ι)

Compact balance-sheet form preserved through the Abrigo Operating Framework:

$$
\boxed{\; a_s \;=\; \Upsilon \;-\; \sum_t \frac{q_t}{(X/Y)} \;}
\tag{5'}
$$

**Critical reading.** $a_s$ is **per-user instrument-level**, *not* a
country-aggregate macro variable. Each individual has their own $\Upsilon$
(savings/wage) and own $q_t$ schedule (subscription/obligation pattern).
Stage-2 calibration is a *distribution* over $(\Upsilon, q_t)$ across a
target cohort — not a single time series. (CORRECTIONS-ι §2.) Aggregate
notional at deployment is computed by `cohort_count × P50_per_user_a_s`,
*not* by measuring an aggregate macro proxy.

**No on-chain $a_s$ entity exists** in any LATAM corridor researched
(SYNTHESIS.md §8.1, CORRECTIONS-ε). Abrigo is an **$a_s$-instantiating**
product, not an $a_s$-hedging product — the $a_s$ side must be deployed by
the protocol, simultaneously with the CPO. Synthetic $\Delta^{(a_s)}$ is
generated under pre-pinned $q_t$ schedule families.

### §4.2 AI-native builder reinterpretation (current target cohort)

**Population.** Solo AI-native builders earning revenue in $Y$ (COP MRR)
and incurring recurring USD-denominated tooling/infra costs (Claude Code,
AWS, Cursor, OpenRouter, …). Source: `notes/SaaS_Builders_AI_NativeBuilders.md`.

The payment-app derivation in §4 does **not** apply directly. The
universal balance sheet (5') $a_s = \Upsilon - \sum q_t/(X/Y)$ does. The
mapping changes as follows:

| Symbol | Payment-app cohort (§4) | AI-native builder cohort (§4.2) |
|---|---|---|
| $\Upsilon$ | Lump-sum deposit $D_0^{(Y)}$ + yield $(1+rT)$ at $t_0$ | **Streaming COP revenue** $\Upsilon_t$ (MRR-style, perpetual, possibly stochastic / autocorrelated; cf. `notes/SaaS_Builders_AI_NativeBuilders.md` $\mathbb{E}[\Upsilon_{t+1}\mid\mathcal F_t]$ form) |
| $q_t$ | Sourcing schedule chosen to satisfy $\sum q_t(X/Y)_t = B_T$ | **Exogenous recurring USD obligation schedule** (Claude Code $\bar C \approx 100$ USD/mo deterministic; AWS variable; not a control variable for the user) |
| Constraint | $\sum q_t (X/Y)_t = B_T$, $q_t > 0$ | None (perpetual; no fixed-quantity delivery) |
| Horizon $T$ | User-defined / bill-defined | **Perpetual** ($T \to \infty$) |
| $\theta$ split | Yield-vault vs liquid-buffer choice | Not a primitive; runway management is a separate concern |
| Profit object | $CF_T^{(a_s)}$ over fixed $T$ | $\Pi_i^{(T)} = \sum_t \Upsilon_t - \sum_t C_t$ over rolling $T$; $C_t$ has deterministic + sticky USD components |

**Cost structure.** Decompose $C_t = C_t^{\text{det}} + C_t^{\text{sticky}}$:

- $C_t^{\text{det}}$ — deterministic recurring USD obligations (Claude Code
  fixed plan, baseline AWS reservations). Translates to $Y$ at spot:
  $C_t^{\text{det}} = \bar C \cdot (X/Y)_t$.
- $C_t^{\text{sticky}}$ — usage-based / committed obligations that don't
  scale down within-period when $(X/Y)$ rises (one-sided ratchet).
  Functional form to be pinned in Stage-2 cohort calibration.

**Sign of $\Delta^{(a_s)}$ unchanged.** Builder is structurally short
$\sigma(X/Y)$ — costs translate up when COP devalues, revenue does not.
Hence $\Delta^{(a_s)} < 0$ continues to hold; the CPO sign convention from
§2 is preserved.

**Implications for CPO design.**
1. Premium structure must be **streamed**, not lump-sum — Panoptic streamia
   premium (continuous flow $\pi(t)$ in COP/month) rather than discrete
   $P_0^{\Pi}$.
2. Equilibrium identity (14) $K_l = K_s$ holds at the rate level rather
   than $T$-integrated level.
3. Pitch form (per the source note): the streamed premium $\pi(t)$ is set
   so that the user's expected USD cost obligation in COP terms is bounded
   — *"your Claude Code bill in COP never exceeds $Z$ COP/month."*
4. Per-user instrument scaling (CORRECTIONS-ι): each builder has their own
   $(\bar C, \overline\Upsilon, \text{stickiness})$ tuple; cohort
   calibration produces a *distribution* over these, not a single triple.

**Calibration sources.**
- $\bar C$: AI-vendor public pricing pages (Anthropic API tiers, Cursor,
  AWS reserved instance baselines).
- $\overline\Upsilon$: LATAM solo-SaaS MRR distribution (DevSurvey-style,
  Stack Overflow, JetBrains, GitHub Octoverse LATAM).
- $\text{stickiness}$: usage-based vs commitment-based AWS taxonomy +
  cohort behavioral priors.

## §5. Deterministic FX path generator

Around stationary mean $\overline{X/Y}$, a closed-form perturbation path
parameterized by amplitude $\varepsilon$ and frequency $\omega$:

$$
(X/Y)_t(\varepsilon, \omega)
\;=\; \Big(1 + \varepsilon\,\big(\cos^2(\omega t) - \tfrac{1}{2}\big)\Big)\, \overline{X/Y},
\qquad 0 < \varepsilon < 1
\tag{6}
$$

Define the perturbation kernel:

$$
f_t \;\equiv\; \cos^2(\omega t) - \tfrac{1}{2}
$$

so $(X/Y)_t = (1 + \varepsilon f_t)\, \overline{X/Y}$.

## §6. Variance proxy and $\varepsilon \leftrightarrow \sigma_T$ inversion

Realized variance over horizon $T$:

$$
\sigma_T \;\equiv\; \frac{1}{T}\sum_{t=0}^{T} \big((X/Y)_t - \overline{X/Y}\big)^2
\tag{7}
$$

Inversion (closed form):

$$
\boxed{\;\varepsilon(\sigma_T) \;=\; \sqrt{\frac{8\,\sigma_T}{\overline{(X/Y)}^2}}\;}
\tag{8}
$$

Allowing every quantity to be re-expressed as a function of $\sigma_T$.

## §7. $\Delta^{(a)}$ closed forms

Substituting (6) and (8) into (1):

$$
\Delta^{(a_l)} \;=\; \frac{4\, r_{(a_l)}}{\overline{X/Y}\, \varepsilon(\sigma_T)}\, \sum_{t=1}^{T}\, |f_t - f_{t-1}|
\;>\; 0
\tag{9}
$$

$$
\Delta^{(a_s)} \;=\; \frac{4}{\overline{X/Y}\, \varepsilon(\sigma_T)}\, \sum_{t=1}^{T}\, q_t\, \frac{f_t}{(X/Y)_t^2}
\;<\; 0
\tag{10}
$$

> The sign $\Delta^{(a_s)} < 0$ is **non-trivial** to verify symbolically; it
> is part of Path A v0 exit criterion (b) over admissible $0<\varepsilon<1$.

## §8. CPO — the neutralizing payoff

Introduce a payoff $\Pi(\sigma_T)$ that makes both sides delta-neutral:

$$
\Delta^{a_l + \Pi} \;=\; \Delta^{(a_l)} + \frac{\partial \Pi}{\partial \sigma_T} \;=\; 0
\qquad
\Delta^{a_s - \Pi} \;=\; \Delta^{(a_s)} - \frac{\partial \Pi}{\partial \sigma_T} \;=\; 0
\tag{11}
$$

Either condition yields:

$$
\frac{\partial \Pi}{\partial \sigma_T} \;=\; -\Delta^{(a)}
\;\;\Longrightarrow\;\;
\Pi(\sigma_T) \;=\; -\int_0^{\sigma_T} \Delta^{(a)}(u)\, du
\tag{12}
$$

### §8.1 Closed form $\Pi \propto \sqrt{\sigma_T}$

Using $\Delta^{(a_l)} \propto 1/\sqrt{\sigma_T}$ from (9) (since
$\varepsilon \propto \sqrt{\sigma_T}$):

$$
\Pi^{(l)}(\sigma_T) \;=\; K_l\, \sqrt{\sigma_T}
\qquad
\Pi^{(s)}(\sigma_T) \;=\; K_s\, \sqrt{\sigma_T}
\tag{13}
$$

**Equilibrium identity:**

$$
\boxed{\; K_l \;=\; K_s \;}
\tag{14}
$$

A CPO market clears iff (14) holds. This is the Path A v0 exit criterion (c)
and the core gauge of Path A v2 numerical drift (§11.a of Path A spec).

## §9. Pricing — buyer / seller positions

With premium $P_0^{\Pi}$ and strike-equivalent $K^\star$:

$$
\hat{\Pi}^{(s)} \;=\; P_0^{\Pi} \;-\; \Pi(K^\star;\, \sigma_T)
\qquad
\hat{\Pi}^{(l)} \;=\; \Pi(K^\star;\, \sigma_T) \;-\; P_0^{\Pi}
\tag{15}
$$

$a_s$ pays premium up-front, receives convex payoff. $a_l$ collects premium,
pays convex payoff. Streamed-premium variants (Panoptic-style) replace
discrete $P_0^{\Pi}$ with a continuous flow $\pi(t)$.

## §10. Carr-Madan replication

$\sqrt{\sigma_T}$ is not directly statically replicable. Linearize around
$\sigma_0$:

$$
\sqrt{\sigma_T}
\;\approx\;
\underbrace{\sqrt{\sigma_0} + \frac{1}{2\sqrt{\sigma_0}}(\sigma_T - \sigma_0)}_{\text{linearization}}
$$

Apply $\Pi$ (constant terms collected into $K^\star\sqrt{\sigma_0}$):

$$
\Pi(\sqrt{\sigma_T}) \;\approx\; K^\star\sqrt{\sigma_0} \;+\; \frac{K^\star}{2\sqrt{\sigma_0}}\,\sigma_T
\tag{16}
$$

Define the linearized constant:

$$
\boxed{\; \hat{K} \;\equiv\; \frac{K^\star}{2\sqrt{\sigma_0}} \;}
\tag{17}
$$

so $\Pi \approx \hat K \cdot \sigma_T$ to first order in $(\sigma_T - \sigma_0)$.

**Carr-Madan strip identity.** Variance is statically replicable from a
continuum of OTM puts and calls:

$$
\boxed{\;
\sigma_T
\;\sim\;
\int_0^{S_0} \frac{P(K)}{K^2}\, dK
\;+\;
\int_{S_0}^{\infty} \frac{C(K)}{K^2}\, dK
\;}
\tag{18}
$$

Therefore:

$$
\Pi(\sigma_T) \;\approx\; \hat{K}\,\Big(\int_0^{S_0} \frac{P(K)}{K^2}\, dK + \int_{S_0}^{\infty} \frac{C(K)}{K^2}\, dK\Big)
\tag{19}
$$

## §11. Discrete strip — Panoptic IronCondor implementation

Replace the continuous integral by a weighted sum of IronCondor positions:

$$
\Pi_T \;\approx\; \sum_{j=1}^{N} w_j\, \mathrm{Condor}_j(S_T)
\tag{20}
$$

Per-condor parameters with strikes $K_1 < K_2 < K_3 < K_4$:

- Center: $K_j \approx S_0 \cdot e^{x_j}$
- Width: $\Delta K_j$
- Carr-Madan weight: $w_j \propto 1/K_j^2$

**Default geometry (Path A v2).** $N=3$ condors covering left tail, ATM,
right tail = **12 legs total** (4 legs per Panoptic position, three
positions). Position-by-position leg assignment is pinned per FLAG-F3 of
Path A spec.

## §12. Tolerances and verification gates (Path A)

| Identity | Tolerance | Source |
|---|---|---|
| Symbolic $\Pi$ vs numeric (v0 reconciliation, three $(\varepsilon,\omega)$ test points) | self-consistency $\le 10^{-10} \cdot N_{\text{legs}}$; strip-vs-analytic per §11.b closed form | Path A spec §10.4 |
| $CF^{(a_l)}$ realized vs $\Delta^{(a_l)}$ analytic (forked Mento V3 / Uniswap V3) | $\pm 5\%$ relative error per $(\varepsilon,\omega)$ grid point; sign of slope strictly positive | Path A spec §2 v1 |
| $K_l = K_s$ numerical drift (Path A v2) | per §11.a | Path A spec §11 |
| $\Pi_{\text{realized}}$ vs $\hat K \sigma_T$ envelope | per §11.b | Path A spec §11 |

## §13. Variable map (anti-conflation, CORRECTIONS-ι §5)

| Symbol | Layer | Granularity | Data source |
|---|---|---|---|
| $Y$ (or $Y_p$) | empirical regression outcome | population / macro | Off-chain (DANE GEIH, DevSurvey, etc.); Stage-1 only |
| $X$ | regressor | population / macro | Banrep TRM lag (or local CB FX series) |
| $a_s$ | **per-user instrument balance sheet** | individual | AI-vendor pricing + DevSurvey cohort distribution; Stage-2 only |
| $a_l$ | LP-side accumulation function | on-chain venue | Substrate panel (Mento V3 LP, Uniswap V3 LP, etc.); Stage-2/3 |
| $q_t$ | per-user obligation schedule | individual | Subscription / cost data per cohort; pre-pinned schedule families |
| $\Upsilon$ | per-user fund (deposit + yield) | individual | Wage / savings input |
| Premium leg | wage flow → vault | individual flow | Stage-3 plumbing (Superfluid CFA or discrete) |
| Payout leg | vault → cost wallet | individual flow | Stage-3 plumbing (Superfluid CFA or Panoptic exercise + X402) |

**Critical anti-conflations.**
- Country-aggregate BoP "computer services imports" is **NOT** $a_s$.
- On-chain Mento corridor flow is **NOT** $a_s$ observability — it's
  LP/settlement-rail capacity (CORRECTIONS-θ §2).
- $Y$ is macro/population-level for Stage-1 β regression; $a_s$ is per-user
  for Stage-2 instrument design. Different objects, different stages.

## §14. Stage gates

Per CLAUDE.md "ideal-scenario clause":

1. **Stage-1** — empirical β confirmation on $Y \times X$ at the cohort's
   *macro* transmission. Exit: positive-β at conventional significance.
   $a_s$ and $a_l$ are NOT inputs.
2. **Stage-2** — ideal-scenario M-sketch. Specify the per-user $a_s$
   functional form (5'), pin $q_t$ schedule families, derive
   $\Delta^{(a_s)}$ for the cohort, design CPO position via §10–§11. Exit:
   Panoptic position that *would* settle the empirical β.
3. **Stage-3** — deployment. Sourcing of LP capital, $a_s$-side
   instantiation (the protocol deploys $a_s$, not just the CPO).

## §15. Open / non-trivial items

- Verification of $\Delta^{(a_s)} < 0$ over admissible $0<\varepsilon<1$:
  not closed-form trivial; numerical certification per Path A v0 exit (b).
- Stochastic-FX variant of the path generator (Path A v3): GBM, OU,
  jump-diffusion, empirical-calibrated. (6) is the *deterministic*
  generator; v3 swaps it for stochastic SDEs while preserving (8)'s
  $\varepsilon \leftrightarrow \sigma_T$ inversion in distribution.
- Cohort-specific calibration of $\Upsilon$, $q_t$ for AI-native solo
  builders is the open Stage-2 deliverable for the SaaS-builder iteration
  (per `notes/SaaS_Builders_AI_NativeBuilders.md`). The §4.2
  reinterpretation pins the *form* of the inputs; the *distribution* over
  $(\bar C, \overline\Upsilon, \text{stickiness})$ is the open empirical /
  survey work.
- Sticky-cost functional form for AI-native builders (open `?` in source
  note): one-sided ratchet $C_t^{\text{sticky}} = \max(C_{t-1}^{\text{sticky}}, \bar c \cdot (X/Y)_t)$
  vs. linear pass-through $C_t^{\text{sticky}} = \bar c \cdot (X/Y)_t$ vs.
  commitment-decay (AWS reserved-instance term structure). Choice affects
  the sign and magnitude of $\Gamma^{(a_s)}$, not just $\Delta^{(a_s)}$.
- Streamed-premium $\pi(t)$ derivation under perpetual horizon — Path A v2
  spec assumes finite $T$ for the $\hat K \sigma_T$ linearization; the
  AI-builder reinterpretation needs $\pi(t) \cdot dt$ ↔ $d\Pi/dt$
  consistency under a perpetual rolling-window $\sigma_T$.
