---
spec_id: saas-builder-stage-2-prereg-lock
spec_version: v1.2.1 (tightening patch — concentration-prior provenance + Task 0.2b NON-NO-OP routing per v1.2 independent-audit MQ FLAGs)
emit_timestamp_utc: 2026-05-08
parent_framework: notes/PRIMITIVES.md (a_s / a_l / CPO primitives)
cohort_note: notes/SaaS_Builders_AI_NativeBuilders.md (cohort instantiation of §4.2)
research_anchor: scratch/2026-05-07-claude-code-cost-research/RESEARCH.md (1500 words, 22 references)
audit_anchor: scratch/2026-05-07-prereg-review/ (Wave-1 RC + Wave-2 MQ verdicts; disposition memo); scratch/2026-05-09-spec-v1.2-review/ (RC ACCEPT + MQ ACCEPT_WITH_FLAGS on v1.2; 2 FLAGs addressed in v1.2.1)
authority: CLAUDE.md anti-fishing invariants (NON-NEGOTIABLE); brainstorming flow; CORRECTIONS-ι per-user a_s framing; feedback_pathological_halt_anti_fishing_checkpoint
predecessor: v1.0 (REJECTED 2-wave; 10 BLOCKs + 11 FLAGs); v1.2 (ACCEPT_WITH_FLAGS — 2 MQ FLAGs)
corrections_block: §14 — CORRECTIONS-α v1.0 → v1.1 (covers RC-BLOCK-1,2,3 + MQ-BLOCK-1..7; MQ-FLAG-A..F); §15 — CORRECTIONS-α v1.1.1 → v1.2 (S_t form pin per SURVEY.md, adjudicates C3 MQ-FLAG-2); §15.7 — CORRECTIONS-α v1.2 → v1.2.1 (concentration provenance + Task 0.2b NON-NO-OP routing)
status: REVERIFY-PASSED — Wave-1 RC ACCEPT_WITH_FLAGS PROCEED + Wave-2 MQ ACCEPT_WITH_FLAGS PROCEED. Sub-task dispatch authorized per §13(5–6) pending user approval. Residual: 2 RC FLAGs (Section M source primary-trace, $p_t$ dimensional one-liner) + 4 MQ FLAGs (G stale α-rationale → fixed in v1.1.1; H Dirichlet "mild" wording; I 4·SE PASS threshold stricter than canonical 2·SE; J $(\alpha, x_m, \kappa)$ joint identifiability — mitigated by §8(7) CI-width gate). All non-blocking; addressable in v1.2 or sub-task plan-time.
---

# Stage-2 pre-registration lock — SaaS-builder $a_s$ instantiation (v1.1)

This spec **locks the cross-cutting invariants** that all Stage-2 sub-tasks
(TODO-COHORT-1..4 + downstream) consume. Per CLAUDE.md anti-fishing
discipline, sub-tasks dispatch in parallel only against a sha-pinned
pre-registration. v1.1 incorporates all v1.0 BLOCKs per §14 CORRECTIONS-α.

The sub-tasks themselves (cohort-specific calibration, sticky-form
verification, $\pi(t)$ derivation, $\Upsilon_t$-form selection) are
written as separate plans against this lock.

## §0 Scope statement

**In scope.** Stage-2 ideal-scenario M-sketch for the AI-native solo-builder
cohort. Specifies per-user $a_s$ functional form, $q_t$ workflow-derived
cost dynamics, $\Upsilon_t$ revenue process, and verification gates. The
CPO math (Carr-Madan replication, 12-leg IronCondor, $K_l = K_s$
equilibrium) is **inherited from PRIMITIVES.md and is not re-derived**.

**Out of scope.** Stage-1 empirical β work (handled by separate iteration;
see §0.1 reconciliation); Stage-3 deployment (LP capital sourcing, on-chain
$a_s$ instantiation plumbing); cross-LATAM aggregate welfare (CGE-class).

## §0.1 Reconciliation with dev-AI Stage-1 FAIL (resolves RC-BLOCK-1)

The dev-AI Stage-1 simple-β iteration closed FAIL on **2026-05-06** with
$\beta = -0.146$ sign-flip on Section J (Colombian young-worker 14-28
employment share in CIIU Rev. 4 Section J narrow ICT × Banrep TRM lag).
See `memory/project_dev_ai_section_j_fail.md` for the full record.

**Why this Stage-2 spec proceeds against a sign-flipped Stage-1.** Three
independent grounds:

1. **Population mismatch.** Section J Stage-1 measured *aggregate
   employment-share transmission* — proportion of young workers (14-28)
   employed in narrow ICT versus the rest of the workforce, as a
   macro-level structural-transformation indicator. The Stage-2 cohort
   here is *post-revenue solo SaaS builders incurring USD-denominated AI
   tooling costs against COP MRR*. These are different objects:
   Section J is a cross-sectional employment-share at population scale;
   the SaaS-builder cohort is a per-user balance-sheet sub-population
   (CORRECTIONS-ι § 2: "$a_s$ is per-user instrument-level, not aggregate
   population-level"). The Section J FAIL is informative about the macro
   transmission to *labor allocation*, not about the per-user solvency
   exposure of an existing post-revenue cohort.

2. **Section M counter-evidence.** Stage-1 R2 sensitivity arm produced
   $\beta = +0.455$, $p = 1.13 \cdot 10^{-6}$ on Section M (professional
   / scientific / technical / admin services CIIU 69-75) — load-bearing
   per `memory/project_dev_ai_section_j_fail.md`. The SaaS-builder
   cohort is closer in occupational composition to Section M (knowledge
   workers, professional services) than to Section J (narrow ICT
   employment). The FAIL is on Section J specifically; Section M
   evidence is consistent with positive transmission for the Stage-2
   cohort.

3. **CLAUDE.md ideal-scenario clause invocation.** CLAUDE.md "Abrigo
   Operating Framework — Ideal-scenario modeling permitted" explicitly
   allows: *"empirical β-estimate work is independent of actual on-chain
   deployment; the M-design step proposes the ideal settlement
   architecture; only the deployment step requires real LP capital."*
   This Stage-2 work is M-design (per-user $a_s$ functional-form +
   $\Delta^{(a_s)}$ closed form + CPO position derivation), not Stage-3
   deployment. CLAUDE.md authorizes the M-sketch *independent of empirical
   β confirmation* under the explicit caveat that deployment requires
   LP capital sourcing — which this spec defers to Stage-3.

**Sign-prior carry-forward.** Per `memory/project_saas_builder_stage_2_active.md`,
the dev-AI FAIL "raises required Stage-1 sign-prior strength but does not
invalidate this iteration's hypothesis." The Stage-2 spec adopts the
strict reading: $\Delta^{(a_s)} < 0$ is the framework-level sign claim
inherited from PRIMITIVES.md §2 (universal across $a_s$ cohorts where
USD costs hit COP-revenue agents); the empirical Section J FAIL does not
falsify this per-user sign claim — it only falsifies a *population-level
employment-share* transmission that is structurally different.

**HALT trigger.** If TODO-COHORT-2 fitting on the synthetic cohort
distribution returns $\Delta^{(a_s)} \ge 0$ at any pinned bracket point,
this reconciliation is invalidated and the spec must be parked per
`feedback_pathological_halt_anti_fishing_checkpoint`. Sign-flip in the
Stage-2 synthetic regime would indicate the per-user framework itself
fails for this cohort — a thesis-level finding, not a methodology tweak.

## §1 Geographic and stage scope

- **Primary geography:** Colombia (CO).
- **Secondary geography:** LATAM (Mexico, Brazil, Argentina, Peru, Chile)
  flagged for Stage-3 cohort-survey expansion; not in primary calibration.
- **Stage filter:** post-revenue, pre-scale solo AI-native builder.
  Critical inclusion: per-user $a_s^{(T)} > 0$ today (solvent absent the
  hedge).
- **Cohort exclusions (out of primary):** cross-border-USD-revenue
  builders (Stripe USD MRR); B2B enterprise customers; teams >1 founder;
  pre-revenue experiments. Different cohorts with different
  $\Delta^{(a_s)}$ signs / magnitudes.

## §2 Time grain

- **Cost cadence:** **monthly** — matches subscription billing (Anthropic
  Claude Pro/Max, AWS billing cycles) and MRR cadence.
- **FX cadence:** **monthly mean of daily TRM** for primary; daily TRM as
  sensitivity arm.
- **Sticky-cost evaluation:** monthly.
- **Reporting horizon $T$:** rolling 12-month windows. Perpetual variant
  per PRIMITIVES.md §15 open item 4 is sensitivity arm.

## §3 FX path class

- **Primary scenario:** deterministic perturbation generator from
  PRIMITIVES.md (6) — $(X/Y)_t = (1 + \varepsilon(\cos^2(\omega t) - 1/2))\,\overline{X/Y}$
  with $\varepsilon(\sigma_T)$ inversion (8) and $0 < \varepsilon < 1$.
  **No bank-spread overlay in the primary path** (resolves RC-BLOCK-3).
- **Sensitivity arms:** Path A v3 stochastic SDEs — GBM, OU on $\log X$,
  jump-diffusion. Empirical-calibrated SDE (BanRep TRM 2010–2026 fit) is a
  Phase-2 hardening arm.
- **Bank-spread sensitivity arm only:** $(X/Y)_t^{\text{eff}} = (1 + s_t)(X/Y)_t$
  with $s_t \in [1\%, 3\%]$. Run as an explicit sensitivity arm in
  TODO-COHORT-2; *not* part of the primary path equation.
- **Mean $\overline{X/Y}$ pin:** 12-month trailing mean of monthly Banrep
  TRM as of audit_block timestamp. Recomputed and sha-pinned per
  audit_block.

## §4 Numeraire convention

- **All cash-flow outputs reported in COP** (cohort's lived unit).
- **Internal computation may use USD** (per PRIMITIVES (5')); conversion
  via $(X/Y)_t$ at the audit_block-pinned spot.
- **Premium $\pi(t)$ reported in COP/month.**

### §4.1 Pitch cap $Z$ — operational definition (resolves RC-FLAG-1)

The cohort-note pitch *"your Claude Code bill in COP never exceeds $Z$
COP/month"* operationalizes per `notes/SaaS_Builders_AI_NativeBuilders.md`
§"Pitch":

$$
Z \;=\; \min\Big\{ z \in \mathbb{R}_+ \;:\; \mathbb{E}\!\left[\frac{q_t^{\text{USD}}}{(X/Y)_t} + \pi(t)\right] \;\le\; z \Big\}
$$

with $q_t^{\text{USD}}$ from (T2) and $\pi(t)$ the streamed CPO premium
from §9 TODO-COHORT-4. The $\mathbb{E}[\cdot]$ is the posterior-predictive
mean over the (T1)+(T2) cohort distribution. $Z$ pins to
`estimates/Z_cap_pinned.json` (schema in §10).

## §5 Empirical-anchor commitment (Option α + workflow-derived)

Stage-2 calibration uses **Option α — public-pricing bracket-bound** for
all cost parameters. Cohort first-party survey (Option γ) is a Stage-3
prerequisite. Public-figure P&L scraping (Option β) is queued as
Phase-2 hardening.

### §5.1 Workflow-derived cost specification (rewritten v1.1)

Class scope per the cohort note: terminal-based agentic AI coding
services (Claude Code as canonical exemplar; Aider, Cursor agent mode,
Codex CLI, Gemini CLI, Cline, Continue, Open Interpreter, Devin in
class).

**Token-consumption process (T1) — primary form (post-research +
post-MQ-BLOCK-1,2,3 update):**

$$
\tau_t \;=\; \sum_{j=1}^{D_t} \sum_{i=1}^{N_j} \tau_{j,i}
$$

with:

- **Daily turn count** $N_j \sim \mathrm{NegBin}(r, p)$ — integer-valued,
  over-dispersion supported (variance > mean). Justified by Anthropic
  costs-doc p90/mean = 30/13 ≈ 2.3× over-dispersion (resolves
  MQ-BLOCK-2; LogNormal $N_j$ rejected as continuous-not-integer).
- **Tokens per turn** $\tau_{j,i} \sim \mathrm{TruncPareto}(\alpha, x_m, x_{\max} = \kappa)$
  — bounded support; bounded mean and variance; cap $\kappa$ as natural
  upper bound (anything past $\kappa$ enters (T2) metered regime, priced
  separately). $\alpha \in [1.5, 2.5]$ bracket (resolves MQ-BLOCK-1;
  posteriors with $\alpha < 1.5$ are refused per §8).
- **Within-session iid** $\tau_{j,i}$ in primary form (constant $x_m$).
  Position-dependence $x_m(i)$ is sensitivity arm only (resolves
  MQ-BLOCK-3 silent fishing risk).
- **Active days** $D_t \approx 22$ for full-time builder.

**Sensitivity arms (closed candidate set; sha-pinned per §8):**

(a) **Position-dependent linear context-resend.** $x_m(i) = x_m^0 \cdot (1 + i/i_0)$
with $i_0 \in [10, 30]$ bracketed. Captures linear context-cost growth.

(b) **Position-dependent exponential context-resend.** $x_m(i) = x_m^0 \cdot \exp(\beta \min(i, i_{\max}))$
with $\beta \in [0.05, 0.15]$, $i_{\max} = 50$. Matches Ouyang
"40th message pays for everything before it" mechanism (RESEARCH.md
§2). Breaks $\tau_{j,i}$ iid — declared explicitly.

(c) **Markovian session-state per arxiv 2603.24582.** State space pinned
as $\{$tool-call, code-edit, plan-step, terminal$\}$ (4 states);
transition matrix calibrated from arxiv 2601.14470's phase decomposition
(53.9% / 24.4% / 21.6% / residual); turn-token distribution conditional
on state. Specifies the previously-hand-waving Markovian arm (resolves
MQ-FLAG-F).

(d) **NegBin variant with zero-inflation (ZINB) for $N_j$** for
intermittent-work cohorts (weekend/vacation gaps).

**Two-regime pricing (T2) — primary form with softplus regularization
(post-MQ-BLOCK-4 update):**

$$
q_t^{\text{USD}} \;=\; \bar p_{\text{sub}} \;+\; p_t \cdot \mathrm{softplus}_\beta(\tau_t - \kappa)
$$

with $\mathrm{softplus}_\beta(x) = \beta^{-1}\log(1 + e^{\beta x})$. The
$\beta \to \infty$ limit recovers $(\tau_t - \kappa)^+$. Finite $\beta$
regularizes the kink so $\Gamma^{(a_s)}$ is well-defined everywhere
(resolves MQ-BLOCK-4 Dirac in $\Gamma$). Pin $\beta$ such that
softplus-vs-ReLU $L^1$ deviation $< \epsilon \cdot \kappa$ for
$\epsilon = 10^{-3}$ (i.e., regularization is conservative). Report
$\beta \to \infty$ asymptotic value alongside the regularized estimate.

**Tier-prior — replaces "primary tier" pin (resolves MQ-BLOCK-5):**

Cohort tier mix as a Categorical latent per builder:

$$
\text{tier}_i \sim \mathrm{Categorical}(\pi_{\text{Pro}}, \pi_{\text{Max-5x}}, \pi_{\text{Max-20x}})
$$

with primary prior $\pi = (0.20, 0.50, 0.30)$ and Dirichlet
concentration $\alpha_0 = 10$ (mild; allows posterior shrinkage from
cohort-survey data when Stage-3 lands). $\bar p_{\text{sub}}$ is then a
discrete random variable indexed by $\text{tier}_i$; ditto $\kappa$.

**Blended per-token price $p_t$ (resolves MQ-FLAG-B):**

$$
p_t \;=\; w_{\text{in}} \cdot p_{\text{in}} \cdot (1 - h_{\text{cache}} + h_{\text{cache}} \cdot 0.10) \;+\; w_{\text{out}} \cdot p_{\text{out}}
$$

with $w_{\text{in}} = 0.539$, $w_{\text{out}} = 1 - w_{\text{in}}$ from
arxiv 2601.14470 (53.9% input dominance); $h_{\text{cache}} = 0.95$
cache-hit rate; $p_{\text{in}}, p_{\text{out}}$ tier-dependent (Sonnet
4.6: $3/$15; Opus 4.6: $5/$25; Haiku 4.5: $1/$5). Computes to
$p_t^{\text{Sonnet}} \approx 0.539 \cdot 3 \cdot 0.145 + 0.461 \cdot 15
\approx 7.15$/MTok blended (replaces the prior $0.30$ figure which was
cached-portion only; resolves RC-FLAG-4).

Model mix prior: $p_t$ further indexed by model choice (Sonnet vs Opus
vs Haiku) with prior $\rho = (0.70, 0.20, 0.10)$ (Sonnet dominant in
2026 builder usage).

### §5.2 Parameter brackets — LOCKED v1.1

Sources: Anthropic published per-developer distribution
[`code.claude.com/docs/en/costs`]; per-token pricing
[`platform.claude.com/docs/en/about-claude/pricing`]; arxiv 2604.22750
(token-consumption variance); arxiv 2603.24582 (Markovian framework);
arxiv 2601.14470 (input/output/reasoning split).

**Tier and pricing (firm, vendor-published May 2026):**

| Parameter | Value | Source |
|---|---|---|
| $\bar p_{\text{sub}}$ tiers | $\{20, 100, 200\}$/mo for $\{$Pro, Max-5x, Max-20x$\}$ | claude.com/pricing |
| $p_{\text{in}}$ Sonnet 4.6 | $3$/MTok | platform.claude.com pricing |
| $p_{\text{out}}$ Sonnet 4.6 | $15$/MTok | same |
| $p_{\text{in}}$ Opus 4.6 | $5$/MTok | same |
| $p_{\text{out}}$ Opus 4.6 | $25$/MTok | same |
| $p_{\text{in}}$ Haiku 4.5 | $1$/MTok | same |
| $p_{\text{out}}$ Haiku 4.5 | $5$/MTok | same |
| Opus 4.7 (released 2026-04-16) | nominal $5/$25; effective +35% via tokenizer | finout-opus47 |
| Prompt cache discount | input −90% on cache hit | finout-pricing |
| Batch discount | −50% all classes (sensitivity arm only) | finout-pricing |
| $w_{\text{in}}, w_{\text{out}}$ | $(0.539, 0.461)$ | arxiv 2601.14470 |
| $h_{\text{cache}}$ | $0.95$ primary; $\{0.80, 0.95\}$ sensitivity bracket | alderson-via-RESEARCH |

**Tier-prior $\pi$:**

| Tier | $\pi$ primary | Dirichlet $\alpha_0$ | Bracket |
|---|---|---|---|
| Pro ($20/mo, $\kappa \approx 1.6$M tok/mo) | 0.20 | 10 | $\pi_{\text{Pro}} \in [0.10, 0.30]$ |
| Max-5x ($100/mo, $\kappa \approx 6.5$M tok/mo) | 0.50 | 10 | $[0.40, 0.60]$ |
| Max-20x ($200/mo, $\kappa \approx 14.5$M tok/mo) | 0.30 | 10 | $[0.20, 0.40]$ |

**Cap structure (firm + post-2026-05-06 footnote):**

- 5-hour rolling session window + weekly hard cap (introduced 2025-08-28).
- Pro / Max-5x: blocked when capped.
- Max-20x: opt-in metered API overflow at standard $p_t$ (the (T2)
  overage regime).
- 2026-05-06: 5-hour limits *doubled*, peak-hour reductions removed
  [9to5google, anthropic-spacex]. **Baseline numbers not officially
  published.** Resolves RC-FLAG-3.
- $\kappa$ token-equivalent estimates (independent third-party):
  Pro ≈ 44k tok/5h; Max-5x ≈ 88k tok/5h; Max-20x ≈ 220k tok/5h
  [tokenmix, verdent]. Annualized at 22 active days × 3 windows/day
  ≈ {2.9M, 5.8M, 14.5M} tok/mo respectively (pre-2026-05-06 figures).
- **Post-doubling $\kappa$ sensitivity arm:** repeat all (T2) fits at
  $2 \cdot \kappa$ per tier; report stability across.
- **$\kappa$ uncertainty bracket:** $\kappa \in [\kappa_0 \cdot 0.5,\, \kappa_0 \cdot 2.0]$
  reflecting both the third-party estimation uncertainty and the
  post-doubling unknown.

**$N_j, \tau_{j,i}$ priors (T1 Bayesian fit anchors):**

| Param | Prior median | p90 | Distribution | Bracket / source |
|---|---|---|---|---|
| $N_j$ (turns/active-day) | ~80 | ~250 | NegBin($r, p$) | over-dispersion ratio 2.3× anchored to costs-doc p90/mean = 30/13 |
| $\tau_{j,i}$ | 2–8k tok | 50–150k; truncated at $\kappa$ | TruncPareto | $\alpha \in [1.5, 2.5]$ bracket (refuse $\alpha < 1.5$ per §8) |
| $h_{\text{cache}}$ | 0.95 | — | scalar | RESEARCH.md / alderson |

**Empirical $\$/$mo distribution (Anthropic first-party, enterprise; preserved verbatim):**

| Statistic | Value | Source |
|---|---|---|
| Mean | $13$/active-day | costs-doc |
| p90 | ≤ $30$/active-day | costs-doc |
| Monthly enterprise | $150$–$250$/dev/month | costs-doc |
| Implied p90/mo (22 active days × $30) | $660$/month | derived |

**Empirical token-consumption process (independent + arxiv) — citation hygiene fixed (resolves RC-FLAG-5):**

| Quantity | Bracket | Source |
|---|---|---|
| Light user $/day API | $2$–$5$/day | tokenmix |
| Active user (3–5 hr) $/day | $6$–$12$/day → ≈ $100$–$200$/mo Sonnet 4.6 | tokenmix, verdent |
| costs-doc p90 (ceiling) | $30$/day | costs-doc |
| Heavy / multi-agent (single anecdote) | $50$/day | b2l-ouyang (single named anecdote, not screenshotted) |
| Same-task token-spread (run-to-run) | 30× | arxiv 2604.22750 |
| Agentic-vs-chat token ratio | 1000× | arxiv 2604.22750 |
| Input / output / reasoning split | 53.9% / 24.4% / 21.6% | arxiv 2601.14470 |
| Code-review-style turn share | ≈ 59% | arxiv 2601.14470 |
| Multi-agent vs single-agent ratio | ≈ 7× | costs-doc |
| Self-prediction correlation | ≤ 0.39 | arxiv 2604.22750 |

**Plausible LATAM-builder $/mo (full-time agentic, no subsidy):**
$150$–$400 modal, $500$–$1{,}500 p90, $> 2{,}000$ p99 — heavy-tailed
with cap-induced kink. The CPO sells the right tail.

### §5.3 Heavy-user regime — substantiation status

Per RESEARCH.md §4: substantiated *qualitatively* (Ouyang $1{,}600/mo
[b2l-ouyang]; alderson HN-cited 150–200M tok/day → $5k/mo retail
[alderson]; GitHub #9424 mass cap-breach reports [gh-9424]) but **not
substantiated with clean screenshotted distributions**. Anthropic's own
p90 × 22 days = $660/mo, so the $> 1{,}000/mo regime is the empirical
right tail (5–15% of full-time agentic users) — consistent, not
contradicted, by first-party data.

Levelsio / Marc Lou / Tony Dinh public bills: **NOT FOUND**. No anchors
on these names.

### §5.4 Realism overrides committed (resolves RC-BLOCK-3, RC-FLAG-2)

Per the prior conversation:
- (a) Bracket subsumes mixed-tier usage including API-heavy builders;
  modal coverage ~$2k/mo, **heavy tail with p99 > $2k preserved per §5.2.**
  No upper-bound truncation.
- (b) Cost-revenue endogeneity $\rho(q_t, \Upsilon_t) = 0$ in primary
  spec; sensitivity arm pins $\rho > 0$ for the production-agent
  cohort sub-population (deferred to a separate iteration).
- (c) Bank-spread $s_t \in [1\%, 3\%]$ overlay is a **§3 sensitivity
  arm only** — *not* in the primary FX path. No silent primary-spec
  mutation.
- (d) Cross-border-USD-revenue builders OUT of cohort scope per §1.

## §6 Primary functional-form pins (post-MQ-BLOCK-5 update)

| Object | Primary form | Source | Sensitivity arms |
|---|---|---|---|
| $a_s^{(T)}$ | (S1): $\sum \Upsilon_t - \sum q_t/(X/Y)_t$ | PRIMITIVES (5'); SaaS note | n/a — universal |
| $\Upsilon_t$ | (S4): martingale $\mathbb{E}[\Upsilon_{t+1}\mid\mathcal F_t] = \Upsilon_t$ | SaaS note §"Revenue" | AR(1)-log-MRR; det+churn with $S_t = (1-\lambda)^t$ per §6.1 |
| $\text{tier}_i$ | Categorical($\pi_{\text{Pro}}, \pi_{\text{Max-5x}}, \pi_{\text{Max-20x}}$) per builder | §5.1, §5.2 | Dirichlet bracket |
| $\bar p_{\text{sub}}$ | Discrete RV indexed by $\text{tier}_i$: $\{20, 100, 200\}$ | §5.2 | post-doubling $\kappa$ arm |
| $q_t^{\text{sticky}}$ | (T2) softplus-regularized overage $p_t \cdot \mathrm{softplus}_\beta(\tau_t - \kappa)$ | §5.1 | $\beta \to \infty$ asymptotic; ReLU baseline |
| $N_j$ (turns/day) | NegBin($r, p$) | §5.1, §5.2 | ZINB; over-disp Poisson |
| $\tau_{j,i}$ | TruncPareto($\alpha, x_m, \kappa$), $\alpha \in [1.5, 2.5]$ | §5.1, §5.2 | position-dep linear/exponential; Markovian session-state |
| $p_t$ | Blended (in/out/cache/model-mix) per §5.1 formula | §5.1 | model-mix prior; cache-hit bracket |
| $(X/Y)_t$ | (6) deterministic perturbation | §3 | GBM, OU, jump, empirical, bank-spread $s_t$ |
| FX vol $\sigma_T$ | (7) realized variance | PRIMITIVES.md | high-frequency RV; GARCH |
| Premium $\pi(t)$ | Streamed COP/month per §9; $T = $ rolling 12-mo | §2; PRIMITIVES §9, §15 op4 | discrete monthly $P_0^{\Pi}$ |
| $q_t^{\text{commit}}$ | $q_t^{\text{commit}} = q_{t-1}^{\text{commit}} + \bar c_{\text{ann}} \cdot \mathbf{1}[t = t_{\text{renew}}]$ — annual ratchet (additive to (T2)) | new (resolves MQ-FLAG-C) | flat $\bar c_{\text{ann}} = 0$ for cohorts without annual commitments |

**Note (resolves MQ-FLAG-D).** (T1) and (T2) are defined in **§5.1 of
this document only**; they are not numbered equations of PRIMITIVES.md
(which ends at (20)). T-numbering is local to this spec. Sub-task plans
must cite as "spec §5.1 (T1)" not "PRIMITIVES.md (T1)".

### §6.1 Det+churn survival form $S_t$ — LOCKED v1.2

The Det+churn sensitivity arm of $\Upsilon_t$ requires a per-builder
cohort-survival process $S_t = \Pr[\text{builder still active at }t \mid
\text{active at }t-1]$. v1.1.1 left the functional form ambiguous
(C3 MQ-FLAG-2). v1.2 pins:

$$
S_t \;=\; (1 - \lambda)^t, \qquad \lambda \sim \mathrm{Beta}(\alpha_S, \beta_S)
$$

i.e. **deterministic factor / discrete-time constant-hazard exponential
survival**, single hazard parameter $\lambda$.

**Authority.** `scratch/2026-05-09-st-literature-survey/SURVEY.md`
(2026-05-09) — methodology-led literature survey produced *decoupled
from C3 v0.3 implementation code* per CLOSE plan v0.2 BLOCK-2
anti-fishing constraint. SURVEY.md §5 TOP RECOMMENDATION; rationale per
SURVEY.md §3.1, §3.2, §3.4, §3.5, §4. Citations 1-5: Zammit & Zerafa
2025 (arxiv:2502.12912); Han, Hou & Chen 2018 (arxiv:1808.03831);
Equihua et al. 2023 (arxiv:2304.00575); Tsubota & Beppu 2025
(arxiv:2506.00889); Reichheld + Recurly / Paddle / Indie Hackers
prosumer-segment monthly-churn benchmarks.

**Rationale (condensed from SURVEY.md §5).**
(i) Matches monthly observation cadence of AI-tooling subscription
billing. (ii) Memoryless hazard is the appropriate default given
event-driven, FX-shock-correlated builder exit, with no calendar-tied
honeymoon or wear-out mechanism for the solo AI-native LATAM cohort.
(iii) Reichheld retention math implicitly assumes this form across all
SaaS practitioner literature. (iv) Maximally parsimonious — one
parameter, identifiable under cohort prior alone, leaves the §6
$\Upsilon_t$ form-selection PSIS-LOO-CV ranking uncontaminated by
free shape parameters. (v) Nested null inside Weibull at $k=1$
(SURVEY.md §3.4, citation 2), enabling Stage-3 falsification.

**$\lambda$ prior — pinned v1.2.**

$$
\lambda \sim \mathrm{Beta}(\alpha_S = 4.5,\; \beta_S = 95.5)
$$

Properties: $\mathbb{E}[\lambda] = \alpha_S / (\alpha_S + \beta_S) =
0.045$ (centered on the 4.5% midpoint of the SURVEY.md citation-5
prosumer-segment 4–5% monthly-churn benchmark); concentration
$\alpha_S + \beta_S = 100$ (moderate — informative about the
4–5%/mo industry pin yet allows posterior shrinkage from any Stage-3
cohort survival panel); 95% prior CI $\approx [0.013, 0.094]$ which
covers the full SURVEY.md-cited prosumer/solopreneur range without
admitting implausibly heavy attrition ($\lambda > 0.10$/mo) or
implausible loyalty ($\lambda < 0.01$/mo) for this cohort. Posterior
CI-width threshold §8(7) applies.

**Concentration-provenance defence ($\alpha_S + \beta_S = 100$).** The
concentration is selected as informative-but-not-overconfident on
independent benchmarks, NOT retro-fit to a target posterior. (i)
**Upper exclusion**: at concentration 100, prior mass on $\lambda >
0.10$/mo is $\approx 1.5\%$, excluding implausible $>10\%$/mo exit
rates that contradict prosumer-segment retention benchmarks
(SURVEY.md citation 5: Reichheld + Recurly / Paddle / Indie Hackers
prosumer-segment monthly churn $\approx 4$–$5\%$ reported as a
single-rate quantity; tail beyond $10\%$/mo not observed in any cited
prosumer cohort). (ii) **Lower-concentration rejection**: lower
concentrations ($\alpha_S + \beta_S < 50$) admit material prior mass
on $\lambda > 0.15$/mo (e.g., at concentration 40 ≈ C3 v0.3 prior,
$\Pr[\lambda > 0.15] \approx 4\%$) inconsistent with the cohort's
wage-funded recurring-purchase model — the cohort has *contractual
monthly billing* (SURVEY.md §3.1 distinguishing from BG/NBD non-
contractual setting), making aggressive churn priors inappropriate
for Stage-2 synthetic-Bayesian regime where no panel data shrinks
the prior. (iii) **Higher-concentration rejection**: concentrations
$>200$ overconfidently constrain Stage-3 falsification — the Stage-3
Weibull-$k$-vs-exponential test (§6.1 Stage-3 falsification path)
requires posterior shrinkage capacity from real survival panel data,
which a too-tight Stage-2 prior would suppress. Concentration 100
sits in the documented mid-band (50–200) where 95% prior CI brackets
the SURVEY.md-cited 4–5% range with margin on each side and prior
predictive checks (§7) admit Stage-3 panel updating without
collapsing onto the prior mean.

**Stage-3 falsification path.** $S_t = (1-\lambda)^t$ is the $k=1$
nested null inside Weibull $S(t) = e^{-(\lambda t)^k}$. Once Stage-3
real-cohort survival panel data exists (per RESEARCH.md §6 cohort
survey, n=30–75), constant-hazard memorylessness may be falsified by
fitting Weibull and testing $k \ne 1$ (LR test or posterior CI on $k$
excluding 1). Stage-2 synthetic-Bayesian regime does **not** admit
$k$ as a free parameter (SURVEY.md §3.4 weakness: no theoretical
anchor for $k$ at Stage-2). Falsification is deferred to Stage-3 by
construction — this is not a fishing surface, it is a scope boundary.

**Candidate-set closure (§8(5)) reaffirmed.** $S_t = (1-\lambda)^t$ is
the **only** admitted survival form for the Det+churn arm at Stage-2.
Bernoulli-time-varying, Gompertz, BG/NBD, and free-Weibull are
explicitly **rejected** at Stage-2 per SURVEY.md §3.2, §3.5, §3.6,
§3.4 respectively. Adding any post-hoc fires HALT per §8(5).

## §7 Tooling commitment (Option 1) — post-MQ-BLOCK-6,7 update

**Stack:** Python 3.13 + uv + sympy + numpy + scipy + pandas + PyMC for
all slices. Functional-python skill (frozen-dataclass three-tier:
Value / Callable / IO; no inheritance; comprehensions over loops; full
typing) for all code-touching work.

- **Symbolic derivation:** sympy notebooks per Path A v0 trio-checkpoint
  discipline (`feedback_notebook_trio_checkpoint`).
- **Sign / equilibrium claims:** numerically certified via Path A v0
  exit criteria (a)–(e); tolerance $\le 10^{-10} \cdot N_{\text{legs}}$
  for self-consistency, $\pm 5\%$ for sympy↔numeric reconciliation per
  Path A spec §10.4.
- **Stochastic FX paths (sensitivity arms):** numpy + scipy.stats SDE
  Euler-Maruyama; no Itô-formal proofs.
- **Cohort calibration:** PyMC for Bayesian posterior over $(r, p, \alpha, x_m, \pi, h_{\text{cache}})$.
- **Posterior CI on time-series quantities:** `pm.sample_posterior_predictive`
  + percentile (resolves MQ-BLOCK-7; stationary-bootstrap stripped — not
  applicable to non-time-series synthetic samples or exchangeable
  posterior draws).
- **Model selection:** **PSIS-LOO-CV via `arviz.compare`** (resolves
  MQ-BLOCK-6). Replaces AICc routing. Verdict thresholds in §9.
- **Notebooks:** all Stage-2 work lands in `notebooks/saas_builder_stage_2/`
  per the existing fx_vol pattern.

**No Lean 4, no Aristotle, no Mathematica, no Julia migration** (per
Option 1 commitment). Slice-B load-bearing claims accept numerical
certification as the verification standard for v1.1. Formal proof is a
flagged Phase-2 hardening track if a referee challenges.

## §8 Anti-fishing invariants (rewritten v1.1; resolves RC-BLOCK-2)

**CLAUDE.md anti-fishing thresholds applicability declaration.** The
$N_{\text{MIN}}=75$, $\text{POWER}_{\text{MIN}}=0.80$,
$\text{MDES}_{\text{SD}}=0.40$ thresholds in CLAUDE.md were framed for
**Stage-1 empirical β regression** on real cohort data. They bind the
**Stage-3 cohort survey (Option γ, n=30–75 per RESEARCH.md §6)** when it
runs. They do *not* bind Stage-2 synthetic-Bayesian calibration, which
has no empirical $Y$, no MDES regression, and no n=75 floor — Stage-2
runs on closed-form public-pricing brackets and synthetic posterior
draws. (Resolves RC-BLOCK-2.)

**Stage-2-applicable anti-fishing invariants (NON-NEGOTIABLE):**

1. **Sign pre-pin.** $\Delta^{(a_s)} < 0$ across the entire admissible
   parameter region $0 < \varepsilon < 1$ AND across all bracket points
   in §5.2. A computed sign reversal at any bracket point fires HALT.
2. **Convexity expectation.** $\Pi^{(s)}$ convex in $\sigma_T$ (the
   $\sqrt{\cdot}$ shape from PRIMITIVES (13)). A linear or
   concave-in-$\sigma_T$ winning $\Pi$ form fires the thesis-fitness
   HALT per CORRECTIONS-η RC-BLOCK-2 precedent.
3. **Bracket immutability.** §5.2 brackets, once sha-pinned, are
   frozen. Tightening / widening post-hoc requires a new
   CORRECTIONS-block.
4. **Tier-cap mechanics immutability.** $\kappa$ pinned per audit_block
   cannot be retuned to fit a desired result.
5. **Candidate-set closure.** TODO-COHORT-1 LOO-CV competition draws
   from the closed candidate set in §5.1 sensitivity arms (a)–(d) +
   §6 functional-form table sensitivity arms. **No post-hoc additions
   admitted.** Adding a candidate fires HALT per
   `feedback_pathological_halt_anti_fishing_checkpoint`.
6. **Pareto-α floor.** Posteriors with $\alpha < 1.5$ are refused. The
   bracketed prior $\alpha \in [1.5, 2.5]$ is the floor. *Rationale
   (corrected per Wave-2 MQ reverify FLAG-G):* under TruncPareto with
   $x_{\max} = \kappa$, all moments are bounded for any $\alpha > 0$ —
   the moment-existence concern from MQ-BLOCK-1 was specific to the
   un-truncated Pareto in v1.0. With truncation, the $\alpha < 1.5$
   floor binds for **tail-shape plausibility** (the empirical
   right-tail in RESEARCH.md §3 is heavy but not pathological;
   $\alpha < 1.5$ would imply a right-tail far heavier than any cited
   evidence) and for **identifiability with $\kappa$** — a posterior
   $\alpha$ near 1 with truncation pushes most mass toward $x_{\max}$
   and renders $(\alpha, x_m, \kappa)$ jointly under-identified. HALT
   on $\alpha < 1.5$ guards against both, not against unbounded
   moments.
7. **Posterior CI-width threshold.** For each (T1) / (T2) parameter,
   the posterior 95% CI width must be $\le 2\times$ the prior CI width
   (i.e., posterior is informed by data, not just regurgitating the
   prior). Posterior-driven priors (from Stage-3 survey input) are
   exempt; pre-survey synthetic draws apply this threshold.
8. **Sim-count floor.** PyMC fits use $\ge 4{,}000$ posterior draws
   across $\ge 4$ chains, with $\hat R \le 1.01$ for all parameters,
   ESS_bulk $\ge 400$, ESS_tail $\ge 400$.
9. **Prior-sensitivity sweep.** Each primary functional form fit under
   $\ge 3$ prior parameterizations spanning the §5.2 bracket; results
   must be qualitatively stable (sign of $\Delta^{(a_s)}$ preserved;
   posterior medians within 1× prior-CI of each other).
10. **HALT cascade discipline.** Any threshold breach fires
    `superpowers:requesting-code-review` halt + disposition memo +
    user-enumerated pivot + CORRECTIONS-block + post-hoc 2-wave verify
    on the result, per `feedback_pathological_halt_anti_fishing_checkpoint`.

**MQ-FLAG-A note.** N=75 in CLAUDE.md is for empirical-cohort
regression sample; for Stage-2 prior-elicitation, the analogous floor
is **≥ 3 independent first-party sources per parameter** (e.g., for
$\alpha$ the sources are: arxiv 2604.22750 token spread, arxiv
2601.14470 phase decomposition, RESEARCH.md indie reports).

## §9 Verification gates per sub-task (post-MQ-BLOCK-4,6,7 update)

| Sub-task | Done when | Tolerance |
|---|---|---|
| TODO-COHORT-1 ($\bar C$ distribution / monthly $/mo CDF) | Posterior over (T1) parameters $(r, p, \alpha, x_m, \pi, h_{\text{cache}})$ + tier mix emitted; resulting $\$/$mo CDF reported at p10/p50/p90/p99 | priors anchored to RESEARCH.md §3; ≥3 independent sources per parameter per §8(MQ-FLAG-A); §8 sim-count floor; §8 CI-width threshold |
| TODO-COHORT-2 (sticky / (T2) softplus fit + sign certification) | Softplus-regularized $\Gamma^{(a_s)}$ posterior emitted with 95% credible interval (from posterior-predictive draws, NOT bootstrap); $\beta \to \infty$ asymptotic value reported alongside; sign of $\Delta^{(a_s)}$ certified $< 0$ at all §5.2 bracket points | sign-flip at any bracket point → HALT per §8(1); $\alpha < 1.5$ → HALT per §8(6) |
| TODO-COHORT-3 ($\Upsilon_t$ form selection) | Three forms (martingale, AR(1)-log, det+churn) fit on cohort prior; **PSIS-LOO-CV winner declared** with PASS / WEAK / MARGINAL / FAIL / INDISTINGUISHABLE routing | PASS if $\Delta\mathrm{elpd}_{\mathrm{loo}} > 4 \cdot \mathrm{SE}$; INDISTINGUISHABLE if $< 2 \cdot \mathrm{SE}$; intermediate as MARGINAL (resolves MQ-BLOCK-6) |
| TODO-COHORT-4 ($\pi(t)$ derivation + $Z$ pin) | Closed-form or numerical $\pi(t) \cdot dt = d\Pi/dt$ identity certified at **5 pinned $(\overline{X/Y}, \sigma_T)$ test points** including two straddling the cap-kink at $\kappa \pm 0.5\kappa$ (resolves MQ-BLOCK-4); **$Z$ pinned to `estimates/Z_cap_pinned.json`** per §4.1 (resolves RC-FLAG-1) | Per Path A v0 §10.4 reconciliation tolerance; $Z$ posterior-predictive mean reported with 95% CI |

All sub-task gates also require: input-data sha pinned, output schema
matched per §10, decision-citation block (4-part: reference / why /
relevance / connection) per `feedback_notebook_citation_block`.

## §10 Output artifact contract

Each sub-task emits to `notebooks/saas_builder_stage_2/`:

| Artifact | Format | Schema |
|---|---|---|
| `data/cohort_prior.parquet` | parquet | columns: `param`, `percentile`, `value`, `source`, `fetched_at_utc` |
| `data/synthetic_tau_t.parquet` | parquet | columns: `month`, `simulation_id`, `tier_id`, `r`, `p`, `alpha`, `x_m`, `tau_t`, `q_t_usd`, `q_t_cop` |
| `estimates/PRIMARY_RESULTS.md` | markdown | per-sub-task primary outcome + numerical evidence + decision-citation block |
| `estimates/ROBUSTNESS_RESULTS.md` | markdown | sensitivity arms results |
| `estimates/gate_verdict.json` | JSON | `{"sub_task": ..., "verdict": "PASS|WEAK|MARGINAL|FAIL|INDISTINGUISHABLE", "evidence": [...]}` |
| `estimates/Z_cap_pinned.json` | JSON | `{"Z_cop_per_month": float, "ci_95_lo": float, "ci_95_hi": float, "audit_block": str, "tier_mix": {...}}` (TODO-COHORT-4 emission) |
| `dispositions/` | markdown | HALT memos if any |
| `MEMO.md` | markdown | overall Stage-2 verdict |

Reproducibility manifest: `notebooks/saas_builder_stage_2/REPRODUCIBILITY.md`
records library version pins, RNG seeds, FX-mean audit_block pin, $p_t$
fetch timestamp, $\kappa$ source timestamp.

## §11 Sub-task dependency graph

```
§5.2 brackets (LOCKED v1.1) + §0.1 reconciliation
        │
        ├──► TODO-COHORT-1 (T1 posterior + tier mix)
        │        │
        │        └──► TODO-COHORT-2 (T2 softplus fit + sign certification)
        │                  │
        │                  └──► Δ^(a_s) closed form per cohort
        │                            │
        │                            └──► TODO-COHORT-4 (π(t) derivation + Z pin)
        │
        └──► TODO-COHORT-3 (Υ_t form via LOO-CV)
                  │
                  └──► joins TODO-COHORT-4 input
```

Parallelism: TODO-COHORT-1 and TODO-COHORT-3 dispatch in parallel.
TODO-COHORT-2 depends on COHORT-1. TODO-COHORT-4 depends on both.

## §12 What this spec does NOT lock (deferred)

| Item | Deferred to |
|---|---|
| Cross-LATAM cohort survey (Option γ; n=30–75; conditional $/mo CDF given Colombian solo builder ≥30h/wk Claude Code) | Stage-3 prerequisite — closes the only real public-data gap per RESEARCH.md §6 |
| Public-figure P&L scraping (Option β) | Phase-2 hardening track |
| Stochastic SDE Itô-formal proofs | Phase-2 hardening (Mathlib SDE coverage gap) |
| Cost-revenue endogeneity sub-population ($\rho > 0$) | Separate iteration |
| Cross-border-USD-revenue builders | Separate cohort iteration |
| Production-agent cost workflow (W_prod) | Separate workflow iteration |
| Cross-vendor (non-Anthropic) class-member cost dispersion | Phase-2 hardening; only required if Stage-2 results show vendor sensitivity |
| Formal $K_l = K_s$ proof in Lean | Phase-2 hardening if referee challenge |

## §13 Pre-condition for sub-task dispatch

1. ✅ PRIMITIVES.md sha-pinned at `notes/PRIMITIVES.md` (HEAD).
2. ✅ Cohort note sha-pinned at `notes/SaaS_Builders_AI_NativeBuilders.md`.
3. ✅ §5.2 empirical brackets landed.
4. ✅ This spec is v1.1.
5. ⏳ **Post-hoc 2-wave reverify on v1.1 result** (per
   `feedback_pathological_halt_anti_fishing_checkpoint` step 5; queued).
6. ⏳ User approval on v1.1 reverify ACCEPT (or ACCEPT_WITH_FLAGS plus
   user adjudication on residual FLAGs).

Steps 5–6 unblock sub-task plan authoring via `superpowers:writing-plans`.

## §14 CORRECTIONS-α — v1.0 → v1.1 delta record

Per `feedback_pathological_halt_anti_fishing_checkpoint`, a
CORRECTIONS-block is valid only when:
- (a) Triggered by external signal — ✅ 2-wave verify REJECT/REJECT
  (Wave-1 RC: 3 BLOCKs + 5 FLAGs; Wave-2 MQ: 7 BLOCKs + 6 FLAGs).
- (b) Disposition memo with ≥3 pivot options — ✅
  `scratch/2026-05-07-prereg-review/disposition_memo.md` enumerated
  α/β/γ/δ.
- (c) User adjudication — ✅ user picked Option α with γ-flavored
  brackets (sub-division proceeds; recommended path).
- (d) Old + new + preserved-guarantees argument — ✅ this section.
- (e) Post-hoc verify on the result — ⏳ §13 step 5 queued.

### §14.1 Carry-forward / defer matrix

| v1.0 element | Disposition | v1.1 location |
|---|---|---|
| §0 scope statement | CARRY | §0 |
| §0 dev-AI Stage-1 disposition (one-line out-of-scope) | EXPAND | §0.1 (RC-BLOCK-1 fix) |
| §1 cohort scope | CARRY VERBATIM | §1 |
| §2 time grain | CARRY VERBATIM | §2 |
| §3 FX path class — primary deterministic (6) | CARRY | §3 |
| §3 — bank-spread $s_t$ in primary spec | DEMOTE to sensitivity arm only (RC-BLOCK-3 fix) | §3 sensitivity arm row + §5.4(c) reworded |
| §4 numeraire | CARRY | §4 |
| Pitch $Z$ definition (cohort note only) | PROMOTE inline (RC-FLAG-1 fix) | §4.1 NEW |
| §5.1 (T1) — Poisson $N_t$ | (already updated v1.0 → LogNormal) → REPLACE LogNormal with NegBin (MQ-BLOCK-2 fix) | §5.1 |
| §5.1 (T1) — Pareto $\tau_{j,i}$ unbounded | REPLACE with TruncPareto, $\alpha \in [1.5, 2.5]$ (MQ-BLOCK-1 fix) | §5.1 |
| §5.1 — $x_m(i)$ position-dep "via $x_m$ scaling" hand-wave | PIN form: iid primary, sensitivity arm (a) linear, (b) exponential, (c) Markovian (MQ-BLOCK-3 fix) | §5.1 |
| §5.1 (T2) — ReLU kink | REPLACE with softplus regularization (MQ-BLOCK-4 fix) | §5.1 |
| §5.2 primary tier $\bar p_{\text{sub}} = 200$ | REPLACE with tier-prior Categorical (MQ-BLOCK-5 fix) | §5.1, §5.2, §6 |
| §5.2 effective input rate $0.30$/MTok | REPLACE with blended $p_t$ formula (MQ-FLAG-B + RC-FLAG-4 fix) | §5.1, §5.2 |
| §5.2 $\kappa = 14.5$M tok/mo (pre-doubling) | ANNOTATE with post-2026-05-06 footnote + 2× sensitivity arm (RC-FLAG-3 fix) | §5.2 |
| §5.4(a) "$2k upper bound" | REWORD to "modal coverage; heavy tail preserved" (RC-FLAG-2 fix) | §5.4 |
| §5.4(c) bank-spread "in primary spec" | REWORD to "sensitivity arm only" (RC-BLOCK-3 fix) | §5.4 |
| §5.2 row "Heavy / multi-agent $30-50/day | costs-doc, b2l-ouyang" | SPLIT citation (RC-FLAG-5 fix) | §5.2 |
| §6 functional-form table | UPDATE rows for new (T1)/(T2) primary forms; add tier_id and $q_t^{\text{commit}}$ rows (MQ-FLAG-C fix) | §6 |
| §6 (T1)/(T2) labeled as PRIMITIVES eqs | ANNOTATE local-numbering (MQ-FLAG-D fix) | §6 |
| §7 stationary bootstrap | STRIP; replace with `pm.sample_posterior_predictive` (MQ-BLOCK-7 fix) | §7 |
| §7 AICc routing | REPLACE with PSIS-LOO-CV via `arviz.compare` (MQ-BLOCK-6 fix) | §7, §9 |
| §8 N_MIN/POWER/MDES verbatim from CLAUDE.md | REWRITE: declare Stage-3-only binding; substitute Stage-2-applicable invariants (RC-BLOCK-2 fix) | §8 |
| §9 TODO-COHORT-2 bootstrap CI on $\Gamma$ | REPLACE with posterior-predictive credible interval over softplus-regularized $\Gamma$ (MQ-BLOCK-4, MQ-BLOCK-7 fix) | §9 |
| §9 TODO-COHORT-4 "3 test points" | EXPAND to 5 test points straddling cap-kink (MQ-BLOCK-4 fix) | §9 |
| §9 TODO-COHORT-4 — $Z$ pinning | ADD as done-when criterion (RC-FLAG-1 fix) | §9 |
| §9 TODO-COHORT-3 AICc | REPLACE with PSIS-LOO-CV thresholds (MQ-BLOCK-6 fix) | §9 |
| §10 schema | ADD `Z_cap_pinned.json` (RC-FLAG-1 fix); ADD `tier_id` column to `synthetic_tau_t` | §10 |
| §11 dependency graph | CARRY (label updated to "LOCKED v1.1") | §11 |
| §12 deferred items | CARRY | §12 |
| §13 pre-conditions | UPDATE: steps 3-4 now ✅; add §13(5) post-hoc reverify | §13 |
| §14 CORRECTIONS block | NEW | §14 (this section) |

### §14.2 Preserved guarantees

This patch preserves:

1. **Anti-fishing discipline** — strengthened, not weakened. Stage-2-applicable
   invariants in §8 are concrete (sign pre-pin, Pareto-α floor, candidate-set
   closure, posterior CI-width, sim-count floor, prior-sensitivity sweep) rather
   than mechanically inherited from a different stage.
2. **Convex-instrument thesis** (`project_abrigo_convex_instruments_inequality`)
   — preserved verbatim. §0.1 reconciliation reaffirms.
3. **Per-user $a_s$ framing** (CORRECTIONS-ι) — sharpened by tier-prior
   replacing primary-tier-pin (MQ-BLOCK-5 fix).
4. **Substrate scope claim** (CORRECTIONS-θ) — unaffected.
5. **CPO math from PRIMITIVES.md** — unchanged; v1.1 only updates the
   cohort-specific $q_t$ form.
6. **Free-tier budget pin** (CORRECTIONS-δ) — unaffected.
7. **Two-wave doc verification on every spec revision** — v1.1 reverify
   queued per §13(5).

### §14.3 Anti-fishing posture

NO threshold was relaxed. The Pareto-α floor at 1.5 is a *new constraint*
(refuses ill-posed posteriors that v1.0 silently admitted). The
candidate-set closure rule is a *new constraint* (refuses post-hoc
functional-form additions). Bracket immutability is preserved. The only
"loosenings" are RC-BLOCK-2 (N_MIN/POWER/MDES declared Stage-3-only,
*not weakened*; their original Stage-1 binding remains) and RC-BLOCK-3
(bank-spread demoted from primary to sensitivity arm — strictly less,
not more, fishing surface).

End of CORRECTIONS-α.

---

## Spec self-review (v1.1)

- [x] Placeholder scan: no TBD / TODO / PENDING residue (TODO-COHORT-N
      tags are sub-task labels, not placeholders).
- [x] Internal consistency: (T2) softplus supersedes ReLU consistently
      across §5.1 / §6 / §9. NegBin $N_j$ supersedes LogNormal
      consistently. Tier-prior supersedes primary-tier-pin in §5.2 / §6
      / §9.
- [x] Scope check: single Stage-2 ideal-scenario M-sketch deliverable;
      §0.1 reconciles with Stage-1 FAIL without scope creep.
- [x] Ambiguity: $\bar p_{\text{sub}}$ is now a discrete RV indexed by
      $\text{tier}_i$, not a primary scalar — pinned in §5.1 / §5.2 / §6.
- [x] Cross-reference: every TODO-COHORT-N tag in §5 / §6 / §9 / §11 / §14
      consistent.
- [x] CORRECTIONS-α records all 10 BLOCKs + 11 FLAGs from
      `scratch/2026-05-07-prereg-review/`; carry-forward / defer matrix
      complete.

End of v1.1.

---

## §15 CORRECTIONS-α — v1.1.1 → v1.2 delta record

Per `feedback_pathological_halt_anti_fishing_checkpoint`, this
CORRECTIONS-block is valid because:
- (a) **Triggered by external signal** — C3 (TODO-COHORT-3 $\Upsilon_t$
  form selection via PSIS-LOO-CV) Wave-2 MQ verify produced
  **MQ-FLAG-2**: spec v1.1.1 §5 / §6 Det+churn arm specified a per-
  builder survival process but did not pin its functional form.
  Implementation chose $S_t = (1-\lambda)^t$ on parsimony grounds; MQ
  flagged this as a spec ambiguity not a code defect, requiring spec
  amendment before close-out. ✅
- (b) **Disposition memo with ≥3 pivot options** — SAAS-COHORT-CLOSE
  plan v0.2 (`docs/plans/2026-05-09-saas-cohort-close.md`) Phase 0
  Task 0.1 enumerated: (α) ratify $(1-\lambda)^t$ via decoupled
  literature survey; (β) Weibull with $k$-prior; (γ) Bernoulli per-
  step time-varying; plus four runner-ups (Gompertz, BG/NBD, cloglog,
  continuous-time exponential). ✅
- (c) **User adjudication via decoupled lit survey** — Task 0.1
  produced `scratch/2026-05-09-st-literature-survey/SURVEY.md`
  (288 lines, 7 citations) by an analyst who did NOT read C3 v0.3
  implementation code prior to writing the survey, per CLOSE plan
  v0.2 BLOCK-2 anti-fishing constraint. SURVEY.md §5 TOP
  recommendation: $(1-\lambda)^t$ deterministic factor / discrete-
  time constant-hazard exponential, with $\lambda \sim \mathrm{Beta}$
  prior centered on 4–5% prosumer-segment monthly churn. ✅
- (d) **Old + new + preserved-guarantees argument** — this section. ✅
- (e) **Post-hoc verify on the result** — independent RC + MQ 2-wave
  reverify queued per SAAS-COHORT-CLOSE plan v0.2 Phase 0 Task 0.3. ⏳

### §15.1 The change

| Element | v1.1.1 | v1.2 |
|---|---|---|
| §6 functional-form table, $\Upsilon_t$ row, sensitivity arm column | "AR(1)-log-MRR; det+churn" (form unspecified) | "AR(1)-log-MRR; det+churn with $S_t = (1-\lambda)^t$ per §6.1" |
| §6.1 Det+churn survival form | (absent) | NEW — pins $S_t = (1-\lambda)^t$, $\lambda \sim \mathrm{Beta}(4.5, 95.5)$, falsification path, candidate-set closure |
| Spec version | v1.1.1 | v1.2 |
| emit_timestamp_utc | 2026-05-07 | 2026-05-08 |

### §15.2 Authority and rationale

**Authority is SURVEY.md, NOT C3 v0.3 implementation.** The amendment
ratifies the literature survey's adjudication of spec §5 ambiguity on
the basis of: (i) Reichheld retention-math identity implicitly
assuming constant hazard across SaaS practitioner literature
(SURVEY.md §3.1 + citation 5); (ii) Recurly / Paddle / Indie Hackers
prosumer-segment industry benchmark of 4–5% monthly churn reported as
a single-rate quantity (SURVEY.md citation 5); (iii) parsimony under
synthetic-Bayesian Stage-2 regime where shape-flexibility would
contaminate the §6 PSIS-LOO-CV form-selection ranking (SURVEY.md §4);
(iv) memorylessness as appropriate default for event-driven (FX-
shock, side-project abandonment, full-time-job absorption) builder
exit absent calendar-tied honeymoon/wear-out mechanisms (SURVEY.md
§3.1, §3.4 cohort-fit); (v) Han, Hou & Chen 2018 (arxiv:1808.03831)
showing Weibull as the most robust nesting form, with exponential as
the most parsimonious special case at $k=1$ (SURVEY.md citation 2),
making the pin testable at Stage-3 without committing Stage-2 to the
extra parameter.

**Citations (per SURVEY.md §7).**
1. Zammit & Zerafa 2025 (arxiv:2502.12912) — BG/NBD canonical
   reference; documents non-contractual setting, contrasting with
   this cohort's contractual monthly billing.
2. Han, Hou & Chen 2018 (arxiv:1808.03831) — exponential vs Weibull
   vs Gompertz comparison; Weibull nests exponential at $k=1$.
3. Equihua et al. 2023 (arxiv:2304.00575) — substantiates parsimony
   under no-data Stage-2 regime via deep-survival data demands.
4. Tsubota & Beppu 2025 (arxiv:2506.00889) — discrete-time cloglog
   alternative if Stage-3 covariate-conditional hazards needed.
5. Reichheld + Recurly / Paddle / Indie Hackers — prosumer / solo-
   targeted SaaS monthly churn ≈ 4–5% benchmark, single-rate
   reporting operationally exponential-survival.

### §15.3 Coincidence with C3 v0.3 — partial form-coincidence, prior-mismatch (revised v1.2.1)

> **v1.2.1 correction.** v1.2 §15.3 originally framed the
> SURVEY-vs-C3-v0.3 alignment as "coincidence" on the *functional
> form* and presumed, without inspecting code, that the priors
> matched. v1.2 independent-audit MQ FLAG-B established that **the
> priors do NOT match**: C3 v0.3 implements $\lambda \sim
> \mathrm{Beta}(2.0, 38.0)$ (mean $= 0.05$, concentration $= 40$) per
> `simulations/saas_builder/cohort_3/priors.py:42-43`, while v1.2
> pins $\lambda \sim \mathrm{Beta}(4.5, 95.5)$ (mean $= 0.045$,
> concentration $= 100$). The §15.3 coincidence claim holds only at
> the *functional-form* level $(1-\lambda)^t$; it does NOT extend to
> the prior hyperparameters.

C3 v0.3 implementer chose $(1-\lambda)^t$ for parsimony reasons; the
SURVEY arrived at the same form independently via literature +
cohort-economic semantics. Form coincidence is preserved. Prior-
hyperparameter coincidence is **explicitly disclaimed in v1.2.1**:
the C3 v0.3 $\mathrm{Beta}(2.0, 38.0)$ prior is *not* the v1.2-pinned
$\mathrm{Beta}(4.5, 95.5)$ prior, and the two priors are NOT
equivalent.

**Authority remains the literature survey, not C3 v0.3 code.** Had
SURVEY.md recommended Weibull-with-prior-near-$k=1$ or BG/NBD, v1.2
would have pinned that form and C3 v0.3 would have been re-fit
accordingly. The same logic applies to the prior: SURVEY.md citation
5 (4–5% midpoint, prosumer-segment) drove $\mathrm{Beta}(4.5, 95.5)$;
C3 v0.3's $\mathrm{Beta}(2.0, 38.0)$ was chosen by the implementer
*before* SURVEY.md existed and is not load-bearing on the v1.2 pin.

### §15.4 C3 re-fit / Task 0.2b status — NON-NO-OP routing (revised v1.2.1)

> **v1.2.1 correction.** v1.2 §15.4 authorized Task 0.2b as a NO-OP
> on the assumption that C3 v0.3's prior matched the v1.2 pin. v1.2
> independent-audit MQ FLAG-B falsified that assumption (see §15.3
> revised). v1.2.1 **rescinds the NO-OP authorization** and routes
> Task 0.2b to **NON-NO-OP execution**: a real re-fit of C3 under
> the v1.2-pinned $\mathrm{Beta}(4.5, 95.5)$ prior is required.

**Prior-mismatch acknowledgement (load-bearing).** C3 v0.3 was
implemented with $\lambda \sim \mathrm{Beta}(2.0, 38.0)$
(mean $= 0.05$, concentration $= 40$); spec v1.2 pins $\lambda \sim
\mathrm{Beta}(4.5, 95.5)$ (mean $= 0.045$, concentration $= 100$).
The priors are **NOT equivalent** — they differ in both location
($0.050$ vs $0.045$) and concentration ($40$ vs $100$, a factor of
$2.5\times$ in informativeness). The v1.2-pinned prior is materially
tighter and centred on a slightly lower mean. A re-fit is required
to obtain a posterior conditioned on the v1.2 prior.

**Routing.** Per CLOSE plan v0.2 Phase 0 Task 0.2b, C3 must be re-
fit under the v1.2-pinned $\lambda \sim \mathrm{Beta}(4.5, 95.5)$
prior. The re-fit:

1. Replaces `DET_CHURN_LAMBDA_BETA_A = 2.0` and
   `DET_CHURN_LAMBDA_BETA_B = 38.0` in
   `simulations/saas_builder/cohort_3/priors.py` with $4.5$ and
   $95.5$ respectively (single-line amendment, frozen-dataclass
   semantics preserved).
2. Re-runs the full PSIS-LOO-CV form-selection comparison
   (martingale, AR(1)-log-MRR, det+churn) under the new prior.
3. Re-issues the C3 PASS / WEAK / MARGINAL / FAIL / INDISTINGUISHABLE
   verdict from the §9 thresholds.

**HALT-on-ELPD-rank-flip.** The HALT-on-flip safeguard from CLOSE
plan v0.2 Phase 0 Task 0.2b **remains in force**. If the re-fit
ELPD ranking flips relative to C3 v0.3 (i.e., a different $\Upsilon_t$
form wins, or any verdict band crosses the $4 \cdot \mathrm{SE}$ /
$2 \cdot \mathrm{SE}$ thresholds), the close-out HALTs and a
disposition memo is required before Phase 1 dispatch.

**Audit-trail integrity.** The prior change ($\mathrm{Beta}(2.0,
38.0) \to \mathrm{Beta}(4.5, 95.5)$) is documented as a **real
Stage-2 methodology change** triggered by SURVEY.md adjudication of
§5 ambiguity. It is **not** cosmetic. The v1.2 spec amendment is
a substantive prior tightening, and Task 0.2b is the substantive
verification that the C3 verdict survives that tightening.

**Anti-fishing posture (load-bearing).** The $\mathrm{Beta}(4.5,
95.5)$ prior was selected on independent literature grounds
(SURVEY.md citation 5 prosumer-segment 4–5% midpoint; concentration-
provenance §6.1) **before** the v1.2 author inspected
`cohort_3/priors.py`. The prior was NOT chosen to match the C3 v0.3
results. The fact that it differs from C3 v0.3's prior is evidence
of independent derivation, not post-hoc selection. The decoupled
literature-survey constraint (CLOSE plan v0.2 BLOCK-2) was honoured
specifically to permit this assertion.

### §15.5 Preserved guarantees

This patch preserves verbatim:

1. **CLAUDE.md anti-fishing invariants** — $N_{\text{MIN}}=75$,
   $\text{POWER}_{\text{MIN}}=0.80$, $\text{MDES}_{\text{SD}}=0.40$,
   sign pre-pin discipline, HALT cascade per
   `feedback_pathological_halt_anti_fishing_checkpoint`.
2. **§5 cost specification** — (T1) NegBin × TruncPareto, (T2)
   softplus regularization, tier-prior Categorical, blended $p_t$
   formula, all §5.2 brackets sha-pinned.
3. **§6 $a_s^{(T)}$, $\Upsilon_t$ primary martingale** — unchanged.
   Det+churn remains a sensitivity arm.
4. **§7 PSIS-LOO-CV via `arviz.compare`** — unchanged.
5. **§8 anti-fishing invariants** — all 10 items preserved verbatim.
   §6.1 candidate-set closure reaffirms §8(5).
6. **§9 verification gates** — TODO-COHORT-3 thresholds (PASS at
   $\Delta\mathrm{elpd}_{\mathrm{loo}} > 4 \cdot \mathrm{SE}$;
   INDISTINGUISHABLE at $< 2 \cdot \mathrm{SE}$) unchanged.
7. **$\Upsilon_t$ closed candidate set** (martingale, AR(1)-log-MRR,
   det+churn, pure deterministic-no-churn per spec §6 + C3 v0.3
   territory) — unchanged. v1.2 narrows the *internal specification*
   of the det+churn arm only.

### §15.6 Anti-fishing posture

**No threshold relaxed. No pin loosened. No candidate added.**

The amendment is *strictly tightening*: spec v1.1.1 left $S_t$ form
unspecified, admitting any survival functional form an implementer
might choose. v1.2 pins the form to a specific 1-parameter family
with a specific Beta prior, with explicit candidate-set closure
reaffirming §8(5) HALT-on-post-hoc-additions. The Stage-3
falsification path (Weibull $k\ne 1$) is documented as a *scope
boundary* (synthetic-Bayesian Stage-2 cannot identify $k$ without
data) not as a *fishing escape hatch*.

The lit survey was conducted decoupled from code per CLOSE plan v0.2
BLOCK-2 anti-fishing constraint specifically to avoid retroactive
ratification of an implementation choice. Authority chain:

  (literature + cohort economics) → SURVEY.md TOP recommendation
  → spec v1.2 §6.1 pin → C3 v0.3 conformance check
  → (v1.2.1) prior-mismatch detected → Task 0.2b NON-NO-OP re-fit

NOT:

  (C3 v0.3 implementation) → spec ratification

This ordering is what permits the v1.2.1 NON-NO-OP routing of Task
0.2b in §15.4 (revised) without violating the anti-fishing
invariants: the prior-mismatch is evidence the spec was NOT retro-
fit to the implementation.

End of CORRECTIONS-α v1.1.1 → v1.2.

### §15.7 CORRECTIONS-α — v1.2 → v1.2.1 (concentration provenance + Task 0.2b NON-NO-OP routing)

Per `feedback_pathological_halt_anti_fishing_checkpoint`, this sub-
block is valid because:

- (a) **Triggered by external signal** — v1.2 independent-audit MQ
  verdict (`scratch/2026-05-09-spec-v1.2-review/mq-verdict.md`,
  ACCEPT_WITH_FLAGS) raised 2 FLAGs: FLAG-A (concentration
  provenance) and FLAG-B (Task 0.2b NON-NO-OP). RC verdict
  (`scratch/2026-05-09-spec-v1.2-review/rc-verdict.md`) ACCEPT — no
  reproducibility-class fixes. ✅
- (b) **No pin loosened, no candidate added** — patch is strictly
  tightening: §6.1 adds independent-benchmark provenance for
  $\alpha_S + \beta_S = 100$; §15.4 escalates Task 0.2b from NO-OP to
  NON-NO-OP (more verification, not less). ✅
- (c) **Audit-trail integrity preserved** — v1.2 §15.3 / §15.4
  retained verbatim with explicit "v1.2.1 correction" preface
  blockquotes; prior assumption (form coincidence ⇒ prior
  coincidence) explicitly disclaimed; no rewrite of historical text
  to suppress the mistake. ✅
- (d) **Old + new + preserved-guarantees argument** — this section.
  ✅
- (e) **Post-hoc verify on the result** — independent RC + MQ 2-wave
  reverify on v1.2.1 queued before CLOSE plan v0.2 Phase 1 dispatch.
  ⏳

**FLAG-A — concentration provenance (§6.1, MQ verdict).**

| Element | v1.2 | v1.2.1 |
|---|---|---|
| §6.1 concentration defence | "moderate" (no independent benchmark) | NEW concentration-provenance defence paragraph: $>10\%$/mo upper exclusion via SURVEY.md citation 5; rejection of $\alpha_S+\beta_S<50$ on cohort-billing-model grounds; rejection of $>200$ on Stage-3 falsification-capacity grounds |

**Fix-A**. §6.1 concentration $\alpha_S + \beta_S = 100$ is now
defended on three independent benchmarks: (i) tail-mass exclusion
of $>10\%$/mo against SURVEY.md citation 5 prosumer-segment
benchmark; (ii) lower-bound rejection ($<50$) on contractual-billing
cohort grounds (SURVEY.md §3.1 distinguishing from BG/NBD non-
contractual setting); (iii) upper-bound rejection ($>200$) on
Stage-3 Weibull-falsification-capacity grounds. Concentration $=
100$ sits in the documented mid-band where 95% prior CI brackets
4–5% with margin.

**FLAG-B — Task 0.2b NON-NO-OP routing (§15.4, MQ verdict).**

| Element | v1.2 | v1.2.1 |
|---|---|---|
| §15.3 prior-coincidence claim | "coincidence, not ratification" (form + prior assumed coincident) | revised — form coincidence preserved; prior-mismatch explicitly disclaimed |
| §15.4 Task 0.2b status | NO-OP authorized; "*defined to have been conducted* under v1.2 prior" | NON-NO-OP routing; real re-fit required; HALT-on-ELPD-rank-flip in force |
| §15.4 prior-mismatch acknowledgement | absent | NEW — C3 v0.3 implements $\mathrm{Beta}(2.0, 38.0)$; v1.2 pins $\mathrm{Beta}(4.5, 95.5)$; priors NOT equivalent |
| §15.4 anti-fishing posture | implicit | NEW — explicit assertion that v1.2 prior was selected on lit grounds *before* `priors.py` inspection |

**Fix-B**. §15.4 NO-OP authorization rescinded. C3 must be re-fit
under $\lambda \sim \mathrm{Beta}(4.5, 95.5)$ per the procedure
documented in §15.4 (revised). The HALT-on-ELPD-rank-flip safeguard
from CLOSE plan v0.2 Phase 0 Task 0.2b remains in force. The prior
delta ($\mathrm{Beta}(2.0, 38.0) \to \mathrm{Beta}(4.5, 95.5)$) is
documented as a real Stage-2 methodology change, not cosmetic.

**Anti-fishing assertion (load-bearing, v1.2.1 author certification).**
The v1.2 $\mathrm{Beta}(4.5, 95.5)$ pin was derived from SURVEY.md
citation 5 (4–5% prosumer-segment midpoint) and the concentration
provenance now in §6.1, both grounded in literature decoupled from
implementation per CLOSE plan v0.2 BLOCK-2. The v1.2 author did NOT
inspect `simulations/saas_builder/cohort_3/priors.py` prior to
selecting the prior hyperparameters. The prior-mismatch surfaced by
v1.2 audit is therefore evidence of independent derivation, not
post-hoc selection. The lit-derived prior stands; C3 v0.3 must
adapt under Task 0.2b.

**Preserved guarantees (v1.2.1).** Items 1–7 of §15.5 carry forward
verbatim. Additionally:

8. **§6 candidate-set closure** — unchanged. $S_t = (1-\lambda)^t$
   remains the only admitted survival form.
9. **CLOSE plan v0.2 HALT-on-flip mechanic** — preserved and now
   load-bearing on the Task 0.2b re-fit.
10. **§9 verification gates** — unchanged; same $4\cdot\mathrm{SE}$
    PASS / $2\cdot\mathrm{SE}$ INDISTINGUISHABLE thresholds apply
    to the re-fit ELPD ranking.

**MQ verdict citation.** Both FLAGs documented in
`scratch/2026-05-09-spec-v1.2-review/mq-verdict.md`
(ACCEPT_WITH_FLAGS) per the v1.2 independent-audit dispatch.

End of CORRECTIONS-α v1.2 → v1.2.1.
