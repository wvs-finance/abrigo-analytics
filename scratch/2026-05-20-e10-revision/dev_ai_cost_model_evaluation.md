# dev_ai_cost Model Evaluation — Correctness + E10 v0.2 Applicability

**Date:** 2026-05-20
**Posture:** read-only QA audit feeding the E10 spec revision. No code/spec/notebook edits.
**Auditor scope:** correctness of the dev-AI cost model, and its reusability for the
E10 v0.2 convex (vol-on-vol) data-consumption FX hedge.

**One-line correctness verdict:** the implemented half of the model (JSONL parser →
pricing → daily COP panel → R5 variance decomposition) is methodologically sound and
free of math/sign errors; the **simulation half (R6) that E10 v0.2 actually needs was
specified but never implemented**, and the implemented model produces cost *levels /
realized variance*, not a *distribution of monthly cost from which vol-on-vol β is
estimable*.

---

## 1. Model inventory — what dev_ai_cost actually is

There are **two distinct artifacts** sharing the `dev_ai_cost` name. Disambiguate first:

### 1.A `notebooks/dev_ai_cost/` — the OLD iteration (NOT the relevant one)

The dev-AI Stage-1 simple-β iteration: Y = Colombian young-worker employment share in
CIIU Section J (ICT) × X = COP/USD lag. **Closed FAIL 2026-05-06**, β = −0.146,
sign-flipped (`memory/project_dev_ai_section_j_fail.md`). This is a DANE structural-
econometric employment-share study with no cost model, no simulation, no PyMC. It is
not the model the task asks about and transfers nothing to E10 except the cross-
iteration lesson that sector-specific FX elasticity has heterogeneous sign.

### 1.B `simulations/dev_ai_cost_v2/` + `notebooks/dev_ai_cost_v2/` — the ACTUAL model

The "dev-AI cost factor model" — the AI-API consumption-cost iteration, **PAUSED-
PENDING-MORE-DATA at v0.2.10** (`memory/project_dev_ai_cost_v2_verdict.md`).

**Structure (what is IMPLEMENTED — `simulations/dev_ai_cost_v2/`, 1,632 LoC):**

| Module | Role | Substance |
|---|---|---|
| `jsonl_io.py` (519 LoC) | IO: parse Claude Code `~/.claude/projects/*.jsonl` | type-discriminates `assistant` rows, permissive Pydantic, line-level malformed skip, `message.id:requestId` dedup (keep-largest-token-sum) |
| `anthropic_pricing.py` (383 LoC) | modules: `PricingTable` cost callable | `Σ_cat tokens_cat × rate_cat` from LiteLLM rate card; 200k input tier; dual-pin (commit SHA + file sha256) |
| `panel_builder.py` (241 LoC) | modules: `JSONLReadResult → DailyNotionalPanel` | daily group-by, weekday filter, inner-join to Banrep daily TRM, `cost_cop = cost_usd × TRM` |
| `types.py` (439 LoC) | Value tier | `MessageRecord`, `TokensByCategory`, `JSONLReadResult`, `DailyNotionalPanel` |
| `_errors.py` (43 LoC) | sub-package error root | `DevAICostError`; also declares R6 error names that are never used |

**Workflow / R5 estimation layer (notebooks `01`–`06`):**
- `02_r5_descriptive.ipynb` — R5 PRIMARY: variance decomposition of |Δln Cost^COP|
  via stationary bootstrap (Politis-Romano, B=10,000).
- `04_r4s3_usd_behavioral.ipynb` — R4-S3-USD vol-clustering HAC-OLS regression.
- `03/05/06` — consistency/sensitivity/Z arms.

**Inputs:** one developer's Claude Code JSONL (n=1 pilot subject, window
2026-01-06 → 2026-05-14, T=28 weekday rows post-first-diff) + Banrep daily TRM.

**Outputs:** point estimates + 90% bootstrap CIs of: realized vol σ̂ of |Δln Cost^COP|,
5% VaR, and the **variance decomposition** Var(Δln Cost^COP) = Var(Δln Cost^USD) +
Var(Δln TRM) + 2·Cov; headline "FX share" = Var(Δln TRM)/Var(Δln Cost^COP) ≈ 0.0000277.

**The workflow-modeling component the user described ("Kafka + a draft model where we
model workflows"):**
- There is **NO Kafka** anywhere in the spec, plans, or code. The grep is clean. The
  "Kafka" recollection does not match any artifact in this repo.
- The "model workflows" component IS real but is the **R6 sibling iteration**
  (`docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md`, v0.1.3 APPROVED).
  R6 = a within-session **NHPP arrival-process simulation** (Non-Homogeneous Poisson,
  λ(t)=λ₀·f(hour-block)·g(day-type), 4×2 = 8-cell seasonality grid) + session-
  composition bootstrap + Monte-Carlo (M=10,000) **cost-trajectory ensemble** under FX
  block-bootstrap paths, producing a simulated monthly cost-burden DISTRIBUTION
  (VaR/CVaR/percentiles) + cap-wait friction.
- **CRITICAL: R6 was never implemented.** Only `_errors.py` mentions the NHPP class
  names; no `arrival_generators.py`, no `cost_simulation.py`, no `NHPPArrivalGenerator`.
  R6 is "parked at v0.1.3, ready for dispatch" — a spec with a 19-task plan and zero code.

**PyMC / Bayesian component:** there is **none** in dev_ai_cost_v2. R5 is frequentist
(stationary bootstrap CIs); R4-S3 is HAC-OLS. (PyMC lives in the unrelated
`simulations/saas_builder/` cohort work, not here.)

---

## 2. Correctness verdict + severity-ranked findings

**Verdict: the implemented model is CORRECT for what it claims to do.** The R5 variance
decomposition is mathematically sound; the cost code matches its spec. The iteration's
PAUSE is an honest power/N limitation, not a model defect. No fabricated factors, no
sign errors, no dimensional errors found in the implemented path.

### Strong findings

**S-1 — The simulation engine E10 v0.2 needs does not exist as code.**
R6 (`docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` §2.1–§2.6,
lines 452–559) is the only part of the dev-AI work that produces a *cost distribution*
via *workflow simulation*. It is unimplemented (`simulations/dev_ai_cost_v2/` contains
zero R6 modules; confirmed by `grep NHPP|ArrivalGenerator|CostSimulator`). Any claim
that E10 can "reuse the simulation engine" is reusing a **spec**, not code. Severity:
Strong because it reframes the whole reuse question — the transferable asset is a
19-task plan, not a working simulator.

**S-2 — The implemented model is structurally directional/level-oriented, not
convex.** R5 produces ONE realized-variance ratio per panel (`02_r5_descriptive.ipynb`
code cell 11: `fx_share = np.var(x)/np.var(c)`). It is a point decomposition of a
single observed time series. It does NOT produce a distribution of monthly costs, and
it does NOT model variance-of-variance. The dev-AI iteration's own headline X is a
*level* channel (Δln TRM into Δln Cost), and the R4-S3 test is a vol-clustering
regression on |returns| — adjacent to but not the same as a vol-on-vol β. See §4.

### Weak findings

**W-1 — Trio 5 counterfactual is informationally degenerate.**
`02_r5_descriptive.ipynb` code cell 14: the "FX held at sample mean" counterfactual is
`cf = notional_cost_usd × mean(TRM)`, so `dln_cf_tokonly = diff(log(USD)) + diff(log
(const)) = dln_usd` exactly. σ̂_token-only therefore equals σ̂ of `dln_usd` by
construction — it adds no information beyond the usage-share already in Trio 4. The
notebook interpretation cell presents it as a distinct "no-hedge comparator"; it is
algebraically the usage path. Not wrong, but redundant — and a reused-as-is risk if
E10 copies the counterfactual pattern expecting independent signal.

**W-2 — FX-share ≈ 0 is regime-conditional and proxy-bound.**
The verdict memo (`project_dev_ai_cost_v2_verdict.md` §3) is explicit and honest: FX
share ≈ 0.0000277 is "regime-conditional descriptive finding on the n=1 proxy subject,"
NOT "FX channel does not exist." The window (2026-Q1–Q2) was a low-COP/USD-vol regime.
This is correctly disclosed — but it means the dev-AI result carries **no informative
prior** for E10's vol-on-vol β (a different statistic, a different regime, a different
cohort). Treat E10's β as identified from scratch (E10 spec §7 already pins this).

**W-3 — Cost-level magnitude bias (π̂), correctly bounded.**
CORRECTIONS-Y-6 (spec lines 546–561): aggregating `cache_create_5m + cache_create_1h`
at the 5m rate underestimates cost LEVELS by up to a factor ~(1+π̂). The spec correctly
proves variance-of-log-returns is scale-invariant, so R5's FX share is unaffected. This
is sound for R5. **But it is a finding FOR E10**: if E10 ever needs cost *levels* (it
does, for VaR/notional sizing), this bias must be fixed, not inherited.

### Observations

**O-1 — `PricingTable` frozen-dataclass mutates counters via `object.__setattr__`**
(`anthropic_pricing.py` lines 284, 354). Documented as the deliberate single exception
to modules-tier immutability (docstring lines 118–125). Acceptable as documented;
flagged only because a Monte-Carlo reuse calling `__call__` across 10,000×N paths would
accumulate counter state across the ensemble — harmless for totals, but not thread-safe
if E10 parallelizes the simulation. Worth knowing before reuse.

**O-2 — Why the iteration paused (and whether it transfers to E10).**
The PAUSE cause is purely **N / power**: 28 weekday rows < the demonstration-grade
floor of 38; R4-S3-USD power 0.1745 < 0.50 (verdict memo §1–§2). The cause is
*single-subject real-data scarcity at observed logging cadence* (~1.5 rows/week, ~12–18
months to reach N≥75). **This reason transfers directly to E10** and is in fact the
explicit motivation for E10 v0.2's simulation posture: x402 launched 2026-05-12, the
real cohort is structurally too young (E10 spec §0.5 CORRECTIONS-E10-1). Both
iterations hit the *same wall*: substrate/subject too sparse for empirical N. E10's
answer is to simulate — which is exactly what dev-AI's unbuilt R6 was for.

**O-3 — Implemented code quality is high.** Dual-SHA pinning, line-conservation
Hypothesis property, ccusage-parity oracle, full audit-econ Delphi closure (5
amendments). The parser/pricing layer is production-grade and well-tested.

---

## 3. Applicability matrix — component × disposition × rationale

E10 v0.2 needs: simulate multi-currency Web3-analyst data-query workflows → extrapolate
a cost stream → compute realized variance of FX rate (X) and of local-ccy query cost
(Y) → estimate vol-on-vol β (β>0) on the simulated panel.

| dev_ai_cost component | Disposition | Rationale |
|---|---|---|
| `jsonl_io.py` JSONL parser | **Discard** | Parses Claude Code AI-API logs. E10's substrate is x402/Superfluid on-chain payment events (subgraph queries), not local JSONL. Different schema, different source entirely. |
| `anthropic_pricing.py` `PricingTable` | **Adapt (pattern only)** | The *pattern* `cost = Σ_cat units_cat × rate_cat` transfers: E10 query cost = Σ query-type × per-query USDC price. But Anthropic token rates, the 200k tier, LiteLLM SHA pins, cache categories are all AI-specific — discard the data, keep the "rate-card callable" shape. Light lift. |
| `panel_builder.py` daily aggregation + TRM join | **Adapt** | The structure — aggregate per period, inner-join an FX panel, multiply `cost_local = cost_usd × FX` — is directly reusable. Adaptations: (a) multi-currency join (E10 cohort spans COP/BRL/KES/EUR... — needs a currency key, not a single TRM); (b) monthly not daily aggregation if matching E10 §3.1; (c) Banrep TRM → multi-source FX panel. Medium lift. |
| `types.py` Value-tier dataclasses | **Adapt (convention)** | The frozen-dataclass three-tier discipline and panel-schema-validation pattern transfer as a *coding convention* (already repo-wide via `functional-python`). The specific fields (`cache_create_5m`, `input_tok`) discard. |
| R5 variance decomposition (`02_r5_descriptive.ipynb`) | **Discard for the β; salvage for diagnostics** | R5 decomposes ONE observed series into level shares — it is NOT a vol-on-vol estimator. The stationary-bootstrap CI machinery and the additive-identity sanity check are reusable diagnostic tooling. The decomposition itself answers a different question (see §4). |
| R4-S3 vol-clustering HAC-OLS (`04_...ipynb`) | **Adapt — closest existing analog** | R4-S3 regresses \|Δln Cost\| on \|Δln FX\| — a *magnitude-on-magnitude* spec. This is the nearest thing in the codebase to E10's vol-on-vol test, but it is realized-absolute-return regression, not realized-VARIANCE-on-realized-VARIANCE. E10 needs Var-per-month(FX) → Var-per-month(cost). The HAC inference geometry and the pre-pinned one-sided structure transfer; the LHS/RHS construction must be rebuilt as monthly realized variances. Medium-heavy lift. |
| R6 NHPP workflow simulation **spec** (`2026-05-16-r6-...-design.md`) | **Reuse the design; build the code** | This is the single most valuable transfer. R6's design — NHPP within-session arrivals, hour-block×day-type seasonality, session-composition bootstrap, M=10,000 Monte-Carlo cost-trajectory ensemble producing a *cost distribution* — is exactly the simulation architecture E10 v0.2 requires, with "AI tool-call arrival" swapped for "data-query arrival." But it is a spec + 19-task plan with **zero implementation**. E10 builds it fresh, guided by the R6 spec. |
| R6 cap-wait / Anthropic 5h-cap logic | **Discard** | Session-cap friction is Anthropic-subscription-specific. x402 has no session cap; pricing is pay-per-query. Not applicable. |
| Dual-SHA pinning / audit_block / Hypothesis line-conservation | **Reuse as-is (engineering discipline)** | Reproducibility scaffolding is iteration-agnostic and should be carried into E10's simulation code verbatim. |
| `simulations/stochastic_fx/generators.py` (referenced by R6) | **Reuse as-is** | R6 mirrors `GBMPathGenerator` / `JumpDiffusionPathGenerator` for FX paths. E10's vol-on-vol test needs simulated FX paths with realistic variance dynamics — this existing generator family is directly reusable and is the FX-side engine. |

---

## 4. Convex-expressibility verdict

**Question:** can the reused dev_ai_cost model produce cost-VARIANCE driven by
FX-VARIANCE, or only cost-levels / point estimates?

**Verdict: the IMPLEMENTED model can produce only ONE realized variance per panel — it
cannot, as built, express the vol-on-vol convex test. The R6 SPEC can, once
implemented.**

Reasoning:

1. **R5 produces a single realized variance, not a distribution of variances.** R5
   takes the one observed T=28 cost series and computes one `Var(Δln Cost^COP)` and one
   FX-share ratio. The stationary bootstrap puts a CI *around that one number* — it does
   not generate a panel of monthly variances. E10 v0.2's β>0 test needs a *panel*:
   {(Var_FX[month t], Var_cost[month t])} across many months/paths, then regress one on
   the other. R5 has a sample size of one variance observation. **Not expressible.**

2. **R4-S3 is the closest analog but is magnitude-on-magnitude, not variance-on-
   variance.** R4-S3-USD regresses |Δln Cost| on |Δln FX| at daily frequency. Absolute
   returns proxy volatility, so R4-S3 is *vol-adjacent*. But E10's pinned design is
   explicitly Var(FX rate per month) → Var(cost per month): a realized-variance panel
   regression. Converting R4-S3 to that requires rebuilding the LHS and RHS as monthly
   realized variances — i.e., a new estimator, not a reuse.

3. **The convex reframe REQUIRES a cost distribution, which only a simulation can
   supply at E10's data scarcity.** With x402 too young (8 days of real data) you cannot
   observe a panel of monthly cost variances empirically. The only way to get
   {Var_cost[t]} is to **simulate** many monthly query-cost trajectories under
   stochastic FX paths and stochastic query workflows, then measure realized variance
   per simulated month. **This is precisely what R6 was designed to do** — R6's M=10,000
   Monte-Carlo cost-trajectory ensemble (spec §2.6) IS a distribution of monthly costs.
   R6 output (1) is literally "Cost-burden distribution ... VaR/CVaR/percentiles."

4. **Therefore the convex reframe IS expressible — but on the R6 architecture, not the
   implemented R5 model.** R6's ensemble gives, per Monte-Carlo path, a monthly cost;
   group by simulated month → realized variance per month; pair with the FX path's
   realized variance per month → the vol-on-vol panel. The architecture supports it.
   The code does not exist.

**Bottom line:** convex-expressible = YES on the R6 design, NO on the implemented R5
codebase. E10 v0.2 must build the simulation engine; it cannot reframe the existing
estimator into a convex test because the existing estimator has n=1 variance
observation.

---

## 5. Recommendation — how much to reuse, what to build fresh

**Reuse ~25–30% (engineering + design), build ~70% fresh (the estimation core).**

**Reuse as-is (low/zero lift):**
- The repo's three-tier functional-python discipline, dual-SHA pinning, audit_block
  convention, Hypothesis line-conservation property — engineering scaffolding.
- `simulations/stochastic_fx/generators.py` (GBM / Jump-Diffusion FX path generators) —
  this is E10's FX-path engine and the source of the X-side realized-variance series.
- The R6 spec `docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` as the
  design blueprint for the workflow simulator (NHPP arrivals, seasonality grid,
  session-composition bootstrap, Monte-Carlo cost ensemble). Adopt the architecture;
  re-derive the calibration on x402 query-workflow data.

**Adapt (medium lift):**
- The `cost = Σ units × rate` pricing-callable pattern → x402 per-query-type USDC
  pricing.
- The `panel_builder` aggregate-then-FX-join structure → multi-currency monthly panel
  (currency key, not single TRM; E10 cohort spans the Mento-15 EM subset).
- The R4-S3 HAC-OLS inference geometry and pre-pinned one-sided test discipline → the
  vol-on-vol regression's inference layer.

**Build fresh (the 70% — the load-bearing core):**
1. **The R6 simulation engine itself** — NHPP query-arrival generator, workflow
   composition, Monte-Carlo cost-trajectory ensemble. Spec exists, code does not.
2. **The vol-on-vol estimator** — realized-variance-per-month construction on both
   X (FX) and Y (query cost), and the β>0 panel regression. R5/R4-S3 do NOT do this;
   they answer level/magnitude questions on one series.
3. **Multi-currency machinery** — dev-AI is single-currency (COP). E10 spans
   COP/BRL/KES/EUR/... — currency-keyed FX panels, per-currency calibration, and the
   cross-currency pooling decision in the β regression.
4. **The convex M-side framing** — Panoptic long-gamma straddle, not a directional put.
   (Note: per `integration_blockers.md` §3, the convex hedge is strictly ideal-scenario
   — no FX-pair options venue exists on-chain in 2026 — so M stays Stage-2 descriptive.)

**Biggest adaptation gap (the one-sentence headline):** dev_ai_cost's implemented model
estimates a *level/realized-variance decomposition on a single observed cost series*,
whereas E10 v0.2 needs a *variance-on-variance β estimated across a simulated panel of
monthly cost variances* — and the only dev-AI component that bridges that gap (R6's
Monte-Carlo cost-distribution simulator) was specified but never built, so E10's
estimation core is effectively a from-scratch build guided by the R6 design.

**Final guidance for the E10 v0.2 reviser:** do not budget E10 as "adapt an existing
model." Budget it as "implement the R6 simulation spec for a new substrate, then build
a new vol-on-vol estimator on top." The genuine reuse is the *design thinking* (R6's
workflow-simulation architecture is sound and directly applicable) and the *engineering
discipline*, not the estimator. The PAUSE reason (substrate too sparse for empirical N)
is the same wall E10 faces — confirming the simulation posture is the right call, and
confirming that R6 is the asset to resurrect, not R5.
