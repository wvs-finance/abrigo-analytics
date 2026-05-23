# Wave-2 Model QA — v1.1 Reverify (post-CORRECTIONS-α)

**Spec audited:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1
**Predecessor verdict:** REJECT v1.0 — 7 MQ-BLOCK + 6 MQ-FLAG (`wave2_model_qa.md`).
**Reverify mandate:** `feedback_pathological_halt_anti_fishing_checkpoint` step 5.

---

## Verdict: **ACCEPT_WITH_FLAGS**

Six of seven MQ-BLOCKs are RESOLVED substantively (math, not theatrics). One is PARTIALLY_RESOLVED (MQ-BLOCK-1 — semantically downgraded; reasoning below). Two NEW MQ-FLAGs raised by v1.1 introductions. v1.0 PASSes preserved. Sub-task dispatch recommendation: **PROCEED** with the two NEW FLAGs flagged for sub-task plan authoring.

---

## Per-BLOCK resolution

### MQ-BLOCK-1 (Pareto unbounded mean) — **PARTIALLY_RESOLVED**

§5.1 line 186–190: TruncPareto$(\alpha, x_m, x_{\max}=\kappa)$, $\alpha\in[1.5,2.5]$, §8(6) refuses $\alpha<1.5$.

(a) **Bounded mean check.** A truncated Pareto on $[x_m, x_{\max}]$ has compact support, so *every* moment is finite for *any* $\alpha>0$. The mean is $\mathbb{E}[\tau] = \frac{\alpha x_m^\alpha}{1-\alpha}\frac{x_{\max}^{1-\alpha}-x_m^{1-\alpha}}{x_{\max}^{-\alpha}-x_m^{-\alpha}}$ (well-defined for $\alpha\ne1$). So the literal v1.0 finding ("$\mathbb{E}[\tau]=\infty$") is **mechanically resolved by truncation alone, independent of the $\alpha\ge 1.5$ floor**.

(b) **$x_{\max}=\kappa$ defensibility.** Defensible: anything beyond $\kappa$ enters the metered (T2) regime priced separately. This is *the right truncation point* for the model's economic logic.

(c) **$\alpha<1.5$ HALT trigger substantively binding?** The floor is no longer needed for moment existence (truncation handles it). It now binds for **tail-shape posterior plausibility** — prior reliance on indie reports (Ouyang 30× spread, alderson) implies $\alpha\in[1.5,2.5]$; a posterior driving $\alpha\to 1$ would indicate prior-data conflict on tail shape, which is a legitimate HALT condition. The floor is therefore *meaningful but for a different reason* than v1.0 stated.

**Verdict:** PARTIALLY_RESOLVED. Math fix is real; the §8(6) floor is now effectively a **tail-shape sanity check** rather than a moment-existence guard. Spec should annotate this nuance — currently §8(6) reads "expectation-based inference is unsound" which is no longer the failure mode under truncation. **Raises NEW MQ-FLAG-G** (below).

### MQ-BLOCK-2 (LogNormal $N_j$) — **RESOLVED**

§5.1 line 182–185: NegBin$(r,p)$. (a) Integer-valued ✓. (b) Anthropic costs-doc p90/mean = 30/13 = 2.31 — variance/mean ratio ≥ 2.31 inconsistent with Poisson (variance = mean), consistent with NegBin. ✓. (c) Priors on $(r,p)$ deferred to TODO-COHORT-1 sub-task — acceptable per spec scope (§5.2 lines 314–319 give bracket anchors for $N_j$ medians).

### MQ-BLOCK-3 ($x_m(i)$ unpinned) — **RESOLVED**

§5.1 lines 191–193 pin **iid primary**; sensitivity arms (a)/(b)/(c)/(d) closed candidate set lines 196–215.

(a) iid primary defensibility under Ouyang. The spec is now *honest about the trade*: iid is the tractable primary; the Ouyang context-resend mechanism is captured as sensitivity arm (b) with explicit acknowledgement at line 204 ("Breaks $\tau_{j,i}$ iid — declared explicitly"). This is no longer silent contradiction; it's an explicit modeling choice with a sensitivity test for the load-bearing alternative. ✓.

(b) $\beta\in[0.05,0.15]$ exponential bracket. Sanity-check at $i=40$ (Ouyang): $\exp(0.05\cdot40)=7.4$; $\exp(0.15\cdot40)=403$. Range 7×–400× context multiplier at the 40th turn — brackets the qualitative claim "40th pays for everything before it." Plausible, with $i_{\max}=50$ cap preventing divergence. ✓.

(c) Markovian 4-state. State space + transition source pinned. ✓.

### MQ-BLOCK-4 (kink Dirac) — **RESOLVED**

§5.1 lines 218–229: softplus$_\beta(x)=\beta^{-1}\log(1+e^{\beta x})$.

(a) $C^\infty$ everywhere ✓. (b) $\beta\to\infty$ recovers $(\cdot)^+$ ✓ (pointwise; standard). (c) $L^1$ deviation $<10^{-3}\kappa$ as regularization criterion: dimensionally correct. (d) §9 line 495: 5 test points including two at $\kappa\pm0.5\kappa$. The bracket is wide enough that softplus regularization is genuinely tested across the kink region. ✓.

### MQ-BLOCK-5 (tier inconsistency) — **RESOLVED**

§5.1 lines 235–242 (Categorical $\pi$, Dirichlet $\alpha_0=10$); §5.2 lines 287–293 (bracket); §6 line 383–384 (discrete RV indexed by tier$_i$); §9 line 492 ("tier mix emitted"). All four locations consistent ✓.

(b) PyMC implementability: Categorical with discrete latent works in PyMC via `pm.Categorical` + marginalization or NUTS-with-discrete via mixture observation likelihood. Standard pattern. ✓.

(c) Dirichlet $\alpha_0=10$ on 3-simplex with mean $(0.20,0.50,0.30)$: equivalent prior sample size = 10. With concentration vector $(2,5,3)$, marginal var on $\pi_{\text{Pro}}$ is $0.2\cdot0.8/11=0.0145$, sd = 0.12. That is *moderately informative*, not "mild" — but defensible given the §5.2 bracket of $[0.10,0.30]$ which implies sd ≈ 0.05; the prior is *looser* than the bracket. "Mild" is a slight overstatement; the prior is mid-strength. **NEW MQ-FLAG-H** below (low severity).

### MQ-BLOCK-6 (AICc on PyMC) — **RESOLVED**

§7 line 420, §9 line 494: PSIS-LOO-CV via `arviz.compare`; thresholds $\Delta\text{elpd}>4\cdot\text{SE}$ PASS, $<2\cdot\text{SE}$ INDISTINGUISHABLE.

The 2·SE threshold for "indistinguishable" is the conventional Vehtari/Sivula heuristic. The 4·SE PASS threshold is **stricter than canonical** — Vehtari et al. 2017 do not endorse a specific PASS multiple; 2·SE is the standard "different" threshold. Stricter is conservative-acceptable. ✓ (with minor literature-citation ambiguity — see NEW MQ-FLAG-I).

### MQ-BLOCK-7 (stationary bootstrap) — **RESOLVED**

§7 line 416–418 strips bootstrap, replaces with `pm.sample_posterior_predictive` + percentile. §9 line 493 echoes ("from posterior-predictive draws, NOT bootstrap"). Grep against §7+§9: no bootstrap residue. ✓.

---

## Per-FLAG resolution

- **MQ-FLAG-A** (N_MIN=75): §8 lines 432–439 + §8(MQ-FLAG-A) lines 482–486 — Stage-3-only binding declared; ≥3 independent first-party sources per parameter as Stage-2 substitute. Substantively scoped. **RESOLVED.**

- **MQ-FLAG-B** ($p_t$ scalar): line 254–256, math check: $0.539\cdot3\cdot(0.05+0.95\cdot0.10)+0.461\cdot15 = 0.539\cdot3\cdot0.145+6.915 = 0.2345+6.915 = 7.1495$. Spec rounds to 7.15. **Math correct.** **RESOLVED.**

- **MQ-FLAG-C** ($q_t^{\text{commit}}$): §6 line 392 row defines additive ratchet $q_t^{\text{commit}}=q_{t-1}^{\text{commit}}+\bar c_{\text{ann}}\mathbf{1}[t=t_{\text{renew}}]$. Annual ratchet is the right form for AWS reserved/annual-plan commitments. ✓ **RESOLVED.**

- **MQ-FLAG-D** (T1/T2 numbering): §6 line 394–397 explicit annotation. **RESOLVED.**

- **MQ-FLAG-E** (stale Poisson): no Poisson residue in spec proper (Poisson appears only at line 318/386 as an *over-disp Poisson sensitivity arm*, intentional). Sub-task plans not yet written — risk transferred to plan authoring. **RESOLVED at spec level.**

- **MQ-FLAG-F** (Markovian hand-waving): §5.1 lines 207–211 pin 4-state space + transition source. **RESOLVED.**

---

## v1.0 PASSes preserved

- (5') universal balance sheet form: §6 line 381 unchanged ✓.
- PRIMITIVES (10) closed form for $\Delta^{(a_s)}$: §6 unchanged in claim; only $q_t$ form swapped. ✓.
- Sign expectation $\Delta^{(a_s)}<0$: §8(1) line 444–446 preserved as anti-fishing invariant. ✓.

---

## NEW MQ-FLAGs introduced by v1.1

**MQ-FLAG-G (low) — TruncPareto $\alpha<1.5$ HALT rationale stale.** §8(6) line 461–464 says "cost generator has unbounded variance and the spec's expectation-based inference is unsound." Under truncation at $\kappa$, this is technically false — all moments are bounded. The floor still has merit as a **prior-data conflict / tail-shape plausibility check**, but the spec's stated rationale is the *un-truncated* failure mode. Annotation fix in v1.2: "$\alpha<1.5$ posterior indicates prior-data conflict on tail shape; refuse for plausibility, not moment existence."

**MQ-FLAG-H (low) — Dirichlet $\alpha_0=10$ described as "mild".** §5.1 line 240–242: prior sd ≈ 0.12 on $\pi_{\text{Pro}}$ vs. bracket-implied sd ≈ 0.05; prior is looser than bracket so "mild" is defensible directionally, but "mild" is conventional shorthand for $\alpha_0\to 0$. Use "moderately informative" or report effective prior sample size = 10 explicitly.

**MQ-FLAG-I (low) — PSIS-LOO 4·SE PASS threshold non-standard.** Vehtari et al. 2017 do not pin a 4·SE PASS multiplier; 2·SE "different" is canonical. Conservative-acceptable but cite as "spec-internal threshold (stricter than 2·SE Vehtari/Sivula heuristic)" rather than as Vehtari literature standard.

**MQ-FLAG-J (low) — Joint posterior identifiability on $(\alpha, x_m, \kappa, x_{\max})$.** §5.1 truncation pins $x_{\max}=\kappa$, removing one DoF. But $\kappa$ itself has a §5.2 bracket $[\kappa_0\cdot0.5, \kappa_0\cdot2.0]$ (line 311). With $x_m$, $\alpha$, and $\kappa$ all latent, joint identifiability under modest data may be weak. Mitigation: §8(7) posterior CI-width threshold catches non-identification post-hoc. Acceptable; flag for sub-task to monitor.

---

## Theatrical-fix detection — clean

- §14.3 "no threshold relaxed": verified. Pareto-α floor and candidate-set closure are *new constraints*; bracket immutability preserved; only "loosenings" (Stage-3 scoping of N_MIN, bank-spread demotion) are framework-correct.
- §8 anti-fishing: 10 invariants are concrete and Stage-2-applicable (sign pre-pin, Pareto-α floor, candidate-set closure, posterior-CI width, sim-count floor with $\hat R\le 1.01$/ESS≥400, prior-sensitivity sweep). Not boilerplate.
- §0.1 reconciliation: math-level on three grounds (population mismatch, Section M counter-evidence with cited $\beta=+0.455$/$p=1.13e\text{-}6$, CLAUDE.md ideal-scenario clause). Includes HALT trigger at line 92–96 if Stage-2 returns $\Delta^{(a_s)}\ge 0$. Substantive.

---

## Sub-task dispatch: **PROCEED**

v1.1 clears the methodological bar. NEW MQ-FLAGs G/H/I/J are low-severity annotation/monitoring items; none block sub-task authoring. Recommend: TODO-COHORT-1..4 plan authoring proceeds; sub-task plans should reference §5.1/§6/§8/§9 as the locked methodology and treat MQ-FLAG-G/H/I/J as v1.2 spec-annotation items.

— Model QA Specialist, Wave-2 reverify
