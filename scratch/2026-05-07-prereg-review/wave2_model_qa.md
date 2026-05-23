# Wave-2 Model QA — SaaS-builder Stage-2 Pre-registration Lock

**Spec audited:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.0
**Auditor frame:** Methodological correctness of (T1)+(T2)+(S1)+(S4) and their composition with PRIMITIVES (5')–(10).
**Precedent:** sibling Wave-2 returned 6 BLOCKs (`scratch/path-b-stage-2/phase-1/corrections_eta_decomposition.md`).

---

## Verdict: **REJECT**

Seven load-bearing methodological errors; one of them (MQ-BLOCK-1, Pareto α-domain) is ill-posed-by-construction and forces the spec to fail its own (5') sign claim under realistic priors. Dispatching TODO-COHORT-1..4 sub-tasks against this lock will burn cycles on a divergent compound process and a non-bootstrappable kink statistic.

---

## MQ-BLOCKs (load-bearing)

### MQ-BLOCK-1 — Pareto $\tau_{j,i}$ has unbounded mean under the cited prior; (S1) expectation diverges

**Where.** §5.1 (T1) + §5.2 priors table ("$\tau_{j,i}$ Pareto, median 2–8k, p99 > 200k").

**Issue.** A Pareto distribution with shape parameter $\alpha \le 1$ has $\mathbb{E}[\tau] = \infty$; with $\alpha \le 2$ has $\mathrm{Var}[\tau] = \infty$. The cited tail (median 2–8k, p99 > 200k) implies a tail index $\alpha \approx \log(0.99/0.50)/\log(p99/p50) \approx \log(99)/\log(40) \approx 1.24$. That is in the **infinite-variance** regime ($\alpha < 2$) and dangerously close to the **infinite-mean** regime ($\alpha = 1$). p99 > 200k with median = 2k pushes $\alpha$ below 1.

**Consequence.** $\mathbb{E}[\tau_t] = D_t \cdot \mathbb{E}[N_j] \cdot \mathbb{E}[\tau_{j,i}]$ is undefined. Therefore $\mathbb{E}[a_s^{(T)}]$ is undefined, the sign claim $\Delta^{(a_s)} < 0$ in §8 cannot be evaluated in expectation, and the §9 TODO-COHORT-2 "magnitude reported with 95% bootstrap CI" is non-existent (CLT fails; bootstrap of heavy-tailed iid samples is well-known inconsistent for $\alpha < 2$, Athreya 1987; Politis-Romano stationary bootstrap inherits this).

**Fix.** Replace Pareto with a **truncated Pareto** $\tau_{j,i} \sim \mathrm{TruncPareto}(\alpha, x_m, x_{\max})$ with $x_{\max} = \kappa$ (the cap is the natural upper bound — anything past $\kappa$ enters the metered (T2) regime, which is *priced separately*). Pin $\alpha \in [1.5, 2.5]$ as a bracket and require sub-task COHORT-1 to report posteriors within this bracket. Refuse posteriors with $\alpha < 1.5$.

---

### MQ-BLOCK-2 — LogNormal $N_j$ for integer turn count is mis-specified; the cited evidence is for τ-variance, not N-variance

**Where.** §5.1: "LogNormal not Poisson — research finds 30× same-task variance ... arxiv 2604.22750."

**Issue.** Two errors stacked. (a) LogNormal is continuous on $\mathbb{R}_+$; turn count is integer-valued. (b) The 30× variance in arxiv 2604.22750 is **same-task token spread**, i.e., variance in $\tau$ given a fixed task — **not** variance in $N_j$ (turns/active-day). The justification cites the wrong moment of the wrong variable. Reading RESEARCH.md §3 confirms: "Same task across runs: 30× spread in **total tokens**" — that's $\tau$, not $N$.

**Consequence.** The compound process $\sum_j \sum_i \tau_{j,i}$ is parameterized by a continuous distribution where it should be discrete; convolution moments are wrong; PyMC priors will be mis-specified.

**Fix.** Use **Negative Binomial** $N_j \sim \mathrm{NegBin}(r, p)$ (the spec's own sensitivity-arm (c) — promote it to primary). NegBin handles over-dispersion natively (variance > mean), is integer-valued, has finite moments, and is the standard count-data heavy-tail. Re-cite: arxiv 2604.22750 supports the τ-variance only; the N-distribution justification needs Anthropic costs-doc p90/mean = 30/13 ≈ 2.3× over-dispersion, which is NegBin not LogNormal.

---

### MQ-BLOCK-3 — Within-session position-dependence is unspecified; (T1) silently parameter-rich

**Where.** §5.1 prose: *"Within-session position-dependence ('40th message pays for everything before it') is captured via $x_m$ scaling with turn index $i$ in the Markovian sensitivity arm."*

**Issue.** $x_m(i)$ functional form is **not pinned**. The cited Ouyang mechanism is super-linear in turn-index (context re-read), but the spec offers no functional commitment. Possible forms: $x_m(i) = x_m^0 \cdot i$ (linear), $x_m \cdot i^2$ (quadratic), $x_m \cdot e^{\beta i}$ (exponential — matches Ouyang's "40th pays for everything"). Each gives radically different right-tail mass. Worse: §5.1 makes $\tau_{j,i}$ *iid within session* in the primary form, but RESEARCH.md §2 says context-resend explicitly violates iid. Primary spec contradicts cited evidence.

**Consequence.** TODO-COHORT-1 posterior is identifiable only if $x_m(i)$ is fixed; otherwise the model is non-identified across $(\alpha, x_m^0, \beta)$. This is silent fishing — different sub-task implementations will land different functional forms post-hoc.

**Fix.** Pin **primary form** as iid with $x_m$ constant + position-dependence demoted to sensitivity arm with explicit $x_m(i) = x_m^0 \cdot (1 + i/i_0)$ functional commitment, $i_0$ in §5.2 brackets. Or pin **primary** as exponential context-resend $x_m(i) = x_m^0 \cdot \exp(\beta \min(i, i_{\max}))$ with $\beta$ bracketed; this matches RESEARCH.md but breaks the iid assumption — spec must then say so explicitly. Pick one; do not leave the form floating.

---

### MQ-BLOCK-4 — (T2) kink breaks $\Delta^{(a_s)}$ closed form (10); §9 TODO-COHORT-4 "three test points" insufficient

**Where.** §5.1 (T2): $q_t^{\mathrm{USD}} = \bar p_{\mathrm{sub}} + p_t \cdot (\tau_t - \kappa)^+$. PRIMITIVES (10) closed form: $\Delta^{(a_s)} = (4/\overline{X/Y}\varepsilon) \sum_t q_t f_t / (X/Y)_t^2$.

**Issue.** (10) is differentiated from $a_s = \Upsilon - \sum q_t/(X/Y)$ in $\sigma_T$ assuming $q_t$ is **smooth** in the FX path. With (T2), $q_t$ has an indicator $\mathbf{1}[\tau_t > \kappa]$. $\tau_t$ is FX-independent in the spec (cost is in tokens, not COP), so the kink is in $\tau$-space not $\sigma_T$-space, and (10) survives **almost everywhere**. But:
1. At $\tau_t = \kappa$ the $(\cdot)^+$ derivative is undefined; $\Gamma^{(a_s)}$ at this point is a Dirac mass with weight = density of $\tau_t$ at $\kappa$ times $p_t / (X/Y)_t$.
2. §9 TODO-COHORT-2: "$\Gamma^{(a_s)}$ sign + magnitude with 95% bootstrap CI" — bootstrap CI through a Dirac is undefined; the sample $\Gamma$ at the kink is identically the empirical density at $\kappa$.
3. §9 TODO-COHORT-4: "$\pi(t) dt = d\Pi/dt$ certified at three pinned $(\overline{X/Y}, \sigma_T)$ test points" — three points is a smoothness-only certification; insufficient at the kink.

**Fix.** Replace bootstrap-CI of point $\Gamma$ with **smoothed $\Gamma$** via either (a) softplus regularization $(\tau_t - \kappa)^+ \to \frac{1}{\beta}\log(1+e^{\beta(\tau_t - \kappa)})$ with $\beta \to \infty$ limit reported, or (b) integrated $\Gamma$ over a small $\sigma_T$-window. For TODO-COHORT-4, require certification at **5 test points** including two on each side of the cap-kink at $\kappa \pm 0.5\kappa$ (the §5.2 bracket boundaries).

---

### MQ-BLOCK-5 — Tier inconsistency: §6 pins primary tier = Max-20x, §9 emits "tier mix posterior"

**Where.** §6 row 3: "$q_t^{\mathrm{det}}$ = $\bar p_{\mathrm{sub}}$ from (T2) primary tier"; §5.2: "Primary tier $\bar p_{\mathrm{sub}} = 200$ (Max-20x)"; §9 TODO-COHORT-1 done-condition: "Posterior over (T1) parameters ... + **tier mix** $\bar p_{\mathrm{sub}}$ emitted."

**Issue.** A scalar primary-tier pin and a tier-mix posterior are different statistical objects. CORRECTIONS-ι (PRIMITIVES §4.1) is unambiguous: $a_s$ is per-user, cohort calibration produces a **distribution over per-user $(\Upsilon, q_t)$** — that includes tier choice. Pinning $\bar p_{\mathrm{sub}} = 200$ throws away cohort heterogeneity and contradicts (5') per-user framing.

**Fix.** §5.2 should pin **tier-prior** (e.g., Pro 20% / Max-5x 50% / Max-20x 30% with §5.2 bracket) not a primary tier. §6 should emit `tier_id` as a discrete latent per builder. Drop "primary tier = Max-20x" — it's a sub-population analysis label, not the primary spec.

---

### MQ-BLOCK-6 — AICc is wrong for the Bayesian PyMC pipeline §7 commits to

**Where.** §9 TODO-COHORT-3: "AICc winner declared with PASS/PASS-WEAK/MARGINAL/FAIL routing per CORRECTIONS-η MQ-BLOCK-2 precedent." §7: "PyMC for Bayesian posterior."

**Issue.** AICc is a frequentist penalty derived from MLE asymptotics; applying it to PyMC posterior samples is a category error. The CORRECTIONS-η precedent was for OLS-class models with $n/k < 40$. With PyMC, the natural model-selection criteria are **WAIC** (Watanabe-Akaike, posterior log-density-based) or **PSIS-LOO-CV** (Vehtari-Gelman-Gabry 2017). LOO-CV is the modern default and is implemented in `arviz.compare`. AICc on PyMC posteriors silently uses the posterior mean as a point estimate and discards uncertainty — defeats the purpose of going Bayesian.

**Fix.** Replace "AICc routing" with "PSIS-LOO-CV (`arviz.compare`) with $\Delta\mathrm{elpd}_{\mathrm{loo}} > 4 \cdot \mathrm{SE}$ as PASS, $\Delta < 2 \cdot \mathrm{SE}$ as INDISTINGUISHABLE, intermediate as MARGINAL." Keep the verdict-routing taxonomy from CORRECTIONS-η; just swap the criterion.

---

### MQ-BLOCK-7 — Stationary-bootstrap mis-application on synthetic Bayesian draws

**Where.** §7: "Politis-Romano stationary bootstrap (per CORRECTIONS-η MQ-BLOCK-5 precedent) for any CI on time-series quantities." §9 TODO-COHORT-2 echoes this.

**Issue.** Stationary bootstrap is a **time-series** resampling scheme designed to preserve serial dependence in a sample drawn from a stationary process. Applied to (i) PyMC posterior draws (which are exchangeable across chains, not a time series) or (ii) synthetic $\tau_t$ samples drawn from the (T1) generative model (which are conditionally iid given parameters), it is methodologically empty — geometric-block-length $p$ has no meaning when there is no serial dependence to preserve. Worse, the (T1) compound process across **months** does have serial dependence via persistent $(\nu_N, s_N, \alpha)$ posteriors, but that is captured by the **posterior**, not by bootstrapping.

**Fix.** Strip stationary-bootstrap from §7. CIs on time-series quantities computed from posterior predictive draws come from the posterior itself (`pm.sample_posterior_predictive` then percentile). Only retain stationary-bootstrap if and where the cohort survey produces *empirical* time-series with autocorrelation — a Stage-3 artifact, not Stage-2.

---

## MQ-FLAGs (lower severity)

**MQ-FLAG-A — N_MIN=75 inherited mechanically.** §8 carries CLAUDE.md anti-fishing thresholds verbatim. These were framed for empirical β regression. For Bayesian synthetic calibration, "N=75" should mean **effective sample size** of cohort priors (number of *independent* sources contributing to the prior, e.g., RESEARCH.md cites ~22 references with high overlap → effective N ≈ 8–12, not 75). Spec must define which N is bound by the threshold; otherwise the threshold is decorative. Recommended: explicit footnote that N_MIN=75 binds the **Stage-3 cohort survey**, not the Stage-2 prior-elicitation N, with a separate Stage-2 minimum (e.g., ≥3 independent first-party sources per parameter).

**MQ-FLAG-B — Cache discount and input/output asymmetry not parameterized in (T2).** §5.1 (T2) has scalar $p_t$. §5.2 lists $3/$15 input/output, 95% cache hit → effective $0.30/MTok input. Spec must commit: is $p_t$ the **blended** rate $0.539 \cdot 0.30 + 0.244 \cdot 15 = 3.82$ /MTok using the arxiv 2601.14470 split? If so, write that. If $p_t$ is model-specific (Sonnet vs Opus 4.7 +35% tokenizer), declare a **model-mix prior** alongside the tier prior. As written, $p_t$ is under-specified.

**MQ-FLAG-C — $q_t^{\mathrm{commit}}$ promised in §6 note, never defined.** §6 says "(S3) preserved for true commitments (annual plans, AWS reserved) as additive $q_t^{\mathrm{commit}}$ term." There is no equation. Either define it ($q_t^{\mathrm{commit}} = q_{t-1}^{\mathrm{commit}} + \bar c_{\mathrm{ann}} \cdot \mathbf{1}[t = t_{\mathrm{renew}}]$ with annual ratchet, say) or remove the forward reference.

**MQ-FLAG-D — PRIMITIVES.md does not define (T1) or (T2).** §6 row labels "(T1)" and "(T2)" as if they were PRIMITIVES equations. They are not — PRIMITIVES.md ends at (20). T-numbering is local to this spec. Add explicit "(T1) and (T2) defined in §5.1 of this document; not inherited from PRIMITIVES.md" to header to prevent downstream sub-task confusion.

**MQ-FLAG-E — Stale Poisson references.** Search `notebooks/saas_builder/` and `scratch/` for any earlier "Poisson $N_j$" residue from the pre-research draft; the §5.1 update is recent. Not visible in the spec itself but a transitive risk for sub-task plans.

**MQ-FLAG-F — Sensitivity-arm (b) "Markovian per arxiv 2603.24582" hand-waving.** §5.1 sensitivity arm (b) cites arxiv 2603.24582 for the transition kernel but does not specify state space, transition matrix structure, or stationary distribution. Per RESEARCH.md §5, the cited paper provides a *framework*, not a calibrated kernel. Either pin the state space (e.g., $\{$tool-call, code-edit, plan-step, terminal$\}$ with empirical transitions from arxiv 2601.14470's phase decomposition) or downgrade arm (b) from "Markovian framework" to "non-iid serial-dependence sensitivity arm — to be specified in TODO-COHORT-2."

---

## Summary table

| ID | Severity | Domain | One-line |
|---|---|---|---|
| MQ-BLOCK-1 | High | Stochastic spec | Pareto α likely <2 (infinite var) or <1 (infinite mean); need TruncPareto with α≥1.5 |
| MQ-BLOCK-2 | High | Stochastic spec | LogNormal $N_j$ continuous-not-integer; cited evidence is for τ not N; use NegBin |
| MQ-BLOCK-3 | High | Identification | $x_m(i)$ unspecified → non-identified; pin functional form |
| MQ-BLOCK-4 | High | Composition | (T2) kink breaks bootstrap CI for Γ and "3 test point" certification |
| MQ-BLOCK-5 | High | Cohort consistency | Primary tier vs tier-mix posterior contradiction in §5.2 vs §9 |
| MQ-BLOCK-6 | Medium-High | Model selection | AICc wrong for PyMC; use PSIS-LOO-CV |
| MQ-BLOCK-7 | Medium | Inference | Stationary bootstrap mis-applied to non-time-series posteriors |
| MQ-FLAG-A | Medium | Anti-fishing | N_MIN=75 inheritance unclear in synthetic-data regime |
| MQ-FLAG-B | Medium | Pricing | $p_t$ scalar conflates input/output/cache/model dimensions |
| MQ-FLAG-C | Low | Definition | $q_t^{\mathrm{commit}}$ referenced but undefined |
| MQ-FLAG-D | Low | Reference integrity | (T1)/(T2) labeled as PRIMITIVES eqs but defined locally |
| MQ-FLAG-E | Low | Stale refs | Audit for residual Poisson references in downstream notebooks |
| MQ-FLAG-F | Low | Sensitivity arm | Markovian arm cites framework, not a calibrated kernel |

---

## Recommendation

**Do not dispatch TODO-COHORT-1..4 against v1.0.** Patch to v1.1 addressing MQ-BLOCK-1..7 (bracketed-α, NegBin, $x_m(i)$ pin, kink-handling, tier-prior, LOO-CV, drop bootstrap), then re-run Wave-2. MQ-FLAGs A–F can land in v1.2 if v1.1 review concurs.

**Methodological adversary note.** MQ-BLOCK-1 alone is sufficient for REJECT — an instrument family premised on $\mathbb{E}[a_s]$ existing while the cost generator has undefined mean is the kind of error that survives Stage-2 paper review and detonates at Stage-3 deployment. The 6-BLOCK precedent in `corrections_eta_decomposition.md` set the bar; this spec clears it.

— Model QA Specialist, Wave-2
