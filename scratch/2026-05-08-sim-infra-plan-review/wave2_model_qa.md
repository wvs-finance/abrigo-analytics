# Wave-2 Model QA — `docs/plans/2026-05-07-sim-infra-0.md`

**Auditor**: Model QA Specialist (Wave-2, methodological adversary)
**Date**: 2026-05-08
**Spec anchor**: v1.1.1 (REVERIFY-PASSED)
**Verdict**: **REJECT** — pre-commit. 4 MQ-BLOCKs + 6 MQ-FLAGs.

The plan is structurally sound (three-tier discipline, audit-pass chain, agent dispatch). But it is **methodologically under-constrained** at exactly the spots where v1.1.1 of the spec earned its "REVERIFY-PASSED" stamp by pinning math the v1.0 silently mutated. The plan delegates "behavior contracts" to the implementing agent without surfacing the v1.1.1 pins that must reach the agent. Default to BLOCK: an implementing agent reading this plan in isolation will rebuild several of the v1.0 BLOCKs that v1.1.1 corrected.

---

## MQ-BLOCKs

### MQ-BLOCK-1 (HIGH) — TruncPareto sampler correctness undefined; α-floor not propagated

**Plan §**: line 142 ("`TruncParetoParams`...agent decides per-file granularity"); line 144 (Callable "samplers"); line 241 (hypothesis-tests targets `α ∈ [1.5, 2.5]`).

**Spec §** v1.1.1 §5.1 (T1), §5.2 ("$\alpha \in [1.5, 2.5]$ bracket"), §8(6) (α-floor HALT trigger; corrected rationale: tail-shape plausibility + joint $(\alpha, x_m, \kappa)$ identifiability under truncation).

**Math reference**: TruncPareto density on $[x_m, \kappa]$:
$$f(x;\alpha,x_m,\kappa) = \frac{\alpha\, x_m^\alpha\, x^{-(\alpha+1)}}{1 - (x_m/\kappa)^\alpha},\qquad x_m \le x \le \kappa.$$
Inverse-CDF sampling requires $F^{-1}(u) = x_m\,[1-u(1-(x_m/\kappa)^\alpha)]^{-1/\alpha}$. Naive call to `scipy.stats.pareto` and clipping to $\kappa$ is **biased** (mass past $\kappa$ is lost, not redistributed).

**Defect**: Plan §3.3 mentions $\alpha \in [1.5, 2.5]$ inside the *test strategy* brief but the **sampler behavior contract** in Phase 2 (line 144) is bare ("samplers"). An agent following this plan can ship a clipped-Pareto and pass the property tests if the strategies likewise clip. The sampler's distributional correctness (KS-test against analytic CDF) is not pinned as a property invariant. Phase 1.4 (line 89) flags PyMC TruncPareto research, but for the sampler used outside PyMC (synthetic-cohort generation in `simulations/modules/`) no library is pinned and no correctness oracle is named.

**Fix**: Add to Phase 2 Task 2.1 behavior contracts:
- TruncPareto sampler MUST use inverse-CDF transform (formula above) OR rejection from un-truncated Pareto with rejection rate documented.
- Required property: KS statistic vs. analytic CDF $\le 0.02$ at $n = 10^4$, sample-mean within 2 SE of analytic mean $\mu = \frac{\alpha x_m}{\alpha-1}\cdot\frac{1-(x_m/\kappa)^{\alpha-1}}{1-(x_m/\kappa)^\alpha}$ (for $\alpha\ne 1$).
- `TruncParetoParams` must validate $\alpha \ge 1.5$ at construction (frozen-dc `__post_init__`); construction failure is the plan-level encoding of §8(6) HALT.

### MQ-BLOCK-2 (HIGH) — Softplus regularization tightness pin missing from contract

**Plan §**: line 144 ("softplus regularizer" in modules); §6 row "Softplus regularizer params" (line 401).

**Spec §** v1.1.1 §5.1 (T2): "Pin $\beta$ such that softplus-vs-ReLU $L^1$ deviation $< \epsilon\cdot\kappa$ for $\epsilon = 10^{-3}$"; §9 TODO-COHORT-2: "$\beta\to\infty$ asymptotic value reported alongside the regularized estimate".

**Math reference**: $\mathrm{softplus}_\beta(x) = \beta^{-1}\log(1+e^{\beta x})$; $L^1$ deviation from ReLU on $[-\kappa,\kappa]$ is $\beta^{-1}\int \log(1+e^{-\beta|x|})dx \approx \pi^2/(6\beta)$. The pin requires $\beta \gtrsim \pi^2/(6\cdot 10^{-3}\kappa) \approx 1645/\kappa$.

**Defect**: Plan never references the $\epsilon = 10^{-3}\cdot\kappa$ tolerance. `SoftplusParams` field set is unspecified; the Callable's behavior contract is silent on whether the regularizer must accept $\beta$ as parameter or compute it from $\kappa$. An agent implementing $\beta = 1$ (the textbook softplus) would pass type-checks and unit tests but fail the spec's regularization-tightness criterion that COHORT-2 depends on for $\Gamma^{(a_s)}$ continuity.

**Fix**: Add to Phase 2 contract: `SoftplusParams` carries fields `(beta: float, kappa: float)`; provide a constructor `SoftplusParams.from_epsilon(epsilon: float, kappa: float)` that solves $\beta \ge \pi^2/(6\epsilon\kappa)$. Add hypothesis property: $\|\mathrm{softplus}_\beta - \mathrm{ReLU}\|_{L^1[-\kappa,\kappa]} \le 10^{-3}\kappa$ for any params constructed via `from_epsilon(1e-3, ·)`.

### MQ-BLOCK-3 (HIGH) — Blended-price formula not in plan; agent-degree-of-freedom theatrical-pass risk

**Plan §**: line 144 ("blended-price function"); §6 verification matrix row "Blended $p_t$ formula" (line 403) — *cites the row but doesn't reproduce the math*.

**Spec §** v1.1.1 §5.1 (resolves MQ-FLAG-B): $p_t = w_{\text{in}}\cdot p_{\text{in}}\cdot(1 - h_{\text{cache}} + h_{\text{cache}}\cdot 0.10) + w_{\text{out}}\cdot p_{\text{out}}$ with $w_{\text{in}}=0.539$, $h_{\text{cache}}=0.95$, model-mix $\rho=(0.70,0.20,0.10)$.

**Defect**: This is *the* formula the v1.0 RC-FLAG-4 + MQ-FLAG-B fix locked in v1.1. The plan calls it "blended-price function" with no formula, no parameter names, no model-mix indexing. An agent could legitimately implement $p_t = w_{\text{in}}p_{\text{in}} + w_{\text{out}}p_{\text{out}}$ (no cache discount) and pass functional-python audits — silently re-introducing RC-FLAG-4. This is a **theatrical-fix risk**: spec v1.1.1 fixed the bug; plan v1 lets the implementing agent re-introduce it.

**Fix**: Behavior contract in Phase 2 must explicitly cite spec §5.1 blended-$p_t$ equation, name the four required inputs ($w_{\text{in}}, h_{\text{cache}}, p_{\text{in}}, p_{\text{out}}$), require model-mix as a separate Callable indexed by tier+model. Hypothesis property: at $h_{\text{cache}}=0$, $p_t = w_{\text{in}}p_{\text{in}} + w_{\text{out}}p_{\text{out}}$ (no-cache limit); at $h_{\text{cache}}=1$, $p_t = 0.1\cdot w_{\text{in}}p_{\text{in}} + w_{\text{out}}p_{\text{out}}$ (full-cache limit).

### MQ-BLOCK-4 (MEDIUM-HIGH) — Parquet schema delegated to agent despite spec §10 already pinning columns

**Plan §**: line 144 ("parquet read/write…class with `__init__`"); verification matrix lines 404–406; §3.3 says "behavior contracts" but no schema-citation step.

**Spec §** v1.1.1 §10: explicit column lists for `cohort_prior.parquet` (`param, percentile, value, source, fetched_at_utc`) and `synthetic_tau_t.parquet` (`month, simulation_id, tier_id, r, p, alpha, x_m, tau_t, q_t_usd, q_t_cop`). `Z_cap_pinned.json` schema also pinned.

**Defect**: Plan tells Phase-1.1 researcher to study "parquet schema patterns" (line 86) — unnecessary indirection given the spec already pins the schema. If the agent invents columns or reorders, downstream COHORT-2/3/4 readers (which the plan does not produce) will silently misread. The IO boundary is the most failure-prone tier per `pre-mortem` literature; loose contract here is the highest-leverage failure surface.

**Fix**: Phase 2 contract must enumerate verbatim the §10 column lists and require IO-boundary classes to validate schemas at read/write (Pydantic `BaseModel` per row, or `pyarrow.Schema` declared as `Final`). Add Phase 4 Reality-Checker check item: "parquet writer rejects DataFrames whose columns do not match spec §10 verbatim".

---

## MQ-FLAGs

### MQ-FLAG-A (MEDIUM) — FX path generator equation source not anchored

Plan line 144 names "FX path generator" but does not cite PRIMITIVES (6) $(X/Y)_t = (1+\varepsilon(\cos^2(\omega t)-1/2))\overline{X/Y}$ or PRIMITIVES (8) inversion $\varepsilon(\sigma_T) = \sqrt{8\sigma_T/\overline{X/Y}^2}$. Phase 3.3 *implies* the round-trip (line 241: "$\varepsilon(\sigma_T)$ inversion in PRIMITIVES (8) — round-trip property") but the implementer's contract should cite PRIMITIVES eqs (6)+(7)+(8) by number. **Fix**: add the three equations verbatim (or reference by primitive number) to Phase 2 inputs list.

### MQ-FLAG-B (MEDIUM) — Mutation kill-rate threshold 80% defensible but unjustified

Plan §3.5 pins ≥80% kill rate. Literature (Petrović & Ivanković 2018, Google's mutation-testing-at-scale) places 75–90% as practical industry target; 80% is mid-range, defensible. **But** the plan should distinguish *equivalent-mutant accounting*: surviving-mutant documentation ("OR document why each survivor is a non-bug semantic-equivalent mutation") creates a backdoor. **Fix**: cap exempted-equivalent mutants at, e.g., ≤10% of total surviving mutants; require each exemption commit-reviewed.

### MQ-FLAG-C (MEDIUM) — Audit-pass sequence: `mutation-testing` should follow `pre-mortem`, not precede it

Plan order (3.3 hypothesis → 3.4 try-except → 3.5 mutation → 3.6 pre-mortem) places `mutation-testing` before `pre-mortem`. Sequence is methodologically backwards: `pre-mortem` surfaces fragility hypotheses → tests added → THEN mutation-testing measures whether the new tests catch perturbations. Running mutation first means pre-mortem-suggested tests are not evaluated for kill-effectiveness. **Fix**: swap 3.5 ↔ 3.6.

### MQ-FLAG-D (MEDIUM) — `pre-mortem` scope excludes `simulations/utils/`

Plan §3.6 explicitly scopes to `simulations/modules/` only. IO boundaries are the canonical `pre-mortem` surface (race conditions, schema drift, partial writes). **Fix**: extend pre-mortem to `simulations/{modules,utils}/`. `types/` can stay out (Value tier is structurally low-fragility).

### MQ-FLAG-E (LOW-MEDIUM) — Joint-identifiability $(\alpha, x_m, \kappa)$ test absent

Spec §8(6) explicitly carries joint-identifiability concern (MQ reverify FLAG-J). Plan does not require any hypothesis property exercising the ridge: posteriors with $\alpha$ near 1.5 and $\kappa$ near upper bracket should produce wider CIs than well-identified interior points. **Fix**: add property test "as $\alpha \to 1.5^+$ AND $x_m/\kappa \to 1^-$, posterior CI width on each parameter monotone non-decreasing" — flagged because this is borderline COHORT-1's responsibility, not infrastructure's. Acceptable to defer with a documented hand-off note.

### MQ-FLAG-F (LOW) — Forward-look: `TruncParetoParams` placement is generic but not asserted

Plan line 142 places `TruncParetoParams` in `simulations/types/` (generic). Spec ties the α-floor to *this cohort* (§8(6) is SaaS-specific in its 1.5 number, generic in form). The plan should distinguish: generic `TruncParetoParams` (no α-floor enforced) in `simulations/types/`, vs. `SaasBuilderTruncParetoParams` (α ≥ 1.5 enforced) in `simulations/saas_builder/types/` (per the §F forward-look question). Currently the location is ambiguous — same risk as MQ-BLOCK-1 leaking saas-specifics into the generic layer. **Fix**: behavior contract must say the floor lives in saas-specific subclass / wrapper, not in generic `simulations/types/`.

---

## Summary table

| ID | Severity | Spec anchor | Theatrical-fix risk |
|---|---|---|---|
| MQ-BLOCK-1 | HIGH | §5.1, §5.2, §8(6) | YES — clipped-Pareto sampler can pass |
| MQ-BLOCK-2 | HIGH | §5.1 (T2), §9 | YES — naive $\beta=1$ can pass |
| MQ-BLOCK-3 | HIGH | §5.1 ($p_t$), MQ-FLAG-B fix | YES — re-introduces RC-FLAG-4 |
| MQ-BLOCK-4 | MED-HIGH | §10 | YES — schema drift silent |
| MQ-FLAG-A | MED | PRIMITIVES (6,7,8) | partial |
| MQ-FLAG-B | MED | §3.5 plan-internal | partial |
| MQ-FLAG-C | MED | audit-chain ordering | low |
| MQ-FLAG-D | MED | pre-mortem scope | low |
| MQ-FLAG-E | LOW-MED | §8(6), MQ FLAG-J | low |
| MQ-FLAG-F | LOW | forward-look | low |

## Disposition

**REJECT** pre-commit. The plan must add a "Behavior contracts — math pins" section to Phase 2 enumerating the four BLOCK fixes (TruncPareto sampler + α-floor enforcement; softplus $\beta$ tightness pin; blended-$p_t$ formula verbatim; parquet schema verbatim from §10) before the implementing agent is dispatched. FLAGs A–F can be addressed in the same commit or in a v1.0.1 plan revision.

The plan's structural skeleton (audit-pass chain, agent dispatch, three-tier discipline) is preserved as-is; only the Phase 2 behavior-contract section needs hardening. Estimated revision scope: ~150–200 lines added under §"Phase 2 — Implementation".

End of Wave-2 Model QA.
