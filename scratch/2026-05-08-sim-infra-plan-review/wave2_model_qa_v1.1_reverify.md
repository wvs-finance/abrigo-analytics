# Wave-2 Model QA — v1.1 Reverify (post-CORRECTIONS-α)

**Auditor**: Model QA Specialist
**Date**: 2026-05-08
**Plan version**: v1.1 (`docs/plans/2026-05-07-sim-infra-0.md`)
**Spec anchor**: v1.1.1 (REVERIFY-PASSED)
**Verdict**: **ACCEPT_WITH_FLAGS** — 2 NEW MQ-FLAGs (MEDIUM), no NEW BLOCKs. Sub-task dispatch: **PROCEED**.

The four v0.1 MQ-BLOCKs are substantively resolved by the Phase 2 prelude. Two pins (M2 support, M2 absolute-vs-relative tightness) carry residual under-specification that the spec itself does not pin tighter, so the plan inherits — not introduces — the slack. The split-Pin-M1 architecture (types open / sampler enforces) is methodologically clean given the spec's own §8(6) wording. No theatrical-fix patterns detected.

---

## Resolution status — v0.1 BLOCKs

### MQ-BLOCK-1 (TruncPareto α-floor) — **RESOLVED**

Pin M1 plus Task 2.2 contract ("TruncPareto sampler refuses $\alpha < 1.5$ at construction time, typed `ValueError`") plus Task 2.4 contract ("M1 floor — sampler raises on $\alpha < 1.5$") plus Task 4.1 step 9 ("M1 sampler `ValueError` on $\alpha < 1.5$ verified by direct test execution") form a closed enforcement chain. An implementer cannot ship a sampler accepting $\alpha = 1.4$ and pass Phase 4.

**Sub-question 1 (split clean?)** — YES. Spec §8(6) is explicitly *cohort-scoped* ("$\alpha < 1.5$ → HALT" lives in COHORT-2 row, line 502; the 1.5 number is saas-specific, the form is generic). A future iteration with different α-floor (e.g., Pair-D-style heavier-tail bracket allowing 1.2) would need a different sampler Callable but can reuse the same Value type. The split matches the spec's own scoping. The MQ-FLAG-F concern from v0.1 (saas-specifics leaking into generic types/) is correctly resolved by §15.13.

**Sub-question 2 (sampler-refusal vs posterior-refusal)** — DEFENSIBLE. Spec §8(6) is a *posterior HALT* (the gate fires when posterior mass concentrates below 1.5). The sampler refusal at $\alpha < 1.5$ is a *stricter* constraint (refuses even drawing from such a region) appropriate at infrastructure level: SIM-INFRA-0 produces synthetic-cohort priors (`cohort_prior.parquet`); preventing $\alpha < 1.5$ at synthesis ensures the prior support obeys the saas commitment. The posterior-level §8(6) gate fires later, in COHORT-2. These are distinct enforcement points, not collapsed. **Document hand-off**: sampler-refusal does NOT replace posterior-§8(6); plan §15.13 should be tightened to say so. (See NEW MQ-FLAG-G below.)

### MQ-BLOCK-2 (Softplus β-tightness) — **PARTIALLY_RESOLVED**

Pin M2 plus Task 2.2 contract ("refuses $\beta$ values failing the M2 tightness criterion at construction time") plus Task 2.4 ("softplus refuses non-tight $\beta$") form an enforcement chain. The criterion is computable (`tightness_l1_deviation()` method).

**Sub-question 1 (support $[0, 2\kappa]$)** — **NEW MQ-FLAG**. The spec (§5.1, lines 223–228) says "$L^1$ deviation $< \epsilon\cdot\kappa$" without naming the support. Closed-form analysis: softplus deviation from ReLU is concentrated at the kink $x = 0$ (i.e., at $\tau_t = \kappa$ in the post-shift coordinate); $\|sp_\beta - (\cdot)^+\|_{L^1(\mathbb{R})}$ diverges (softplus tail $\beta^{-1}\log 2$ is constant for $x \to -\infty$). So a finite support is REQUIRED for the criterion to be well-defined; spec is silent and plan picks $[0, 2\kappa]$. This is a *defensible plan-level choice* but **not** equivalent to spec §9 TODO-COHORT-2 "$\beta \to \infty$ asymptotic value reported alongside the regularized estimate" or §5.2 bracket-point evaluation. The kink-centered support $[\kappa - 0.5\kappa, \kappa + 0.5\kappa]$ in the user-question is a different, equally-defensible choice. Both produce comparable numerics ($\pi^2/(12\beta)$ vs $\pi^2/(12\beta)$ — symmetric around the kink either way). Since spec underspecifies, plan-choice is non-fishing as long as the support is *fixed before data touch*. **Resolution**: ACCEPT plan choice; flag for spec-side clarification in v1.1.2 (defer, not block).

**Sub-question 2 (absolute vs relative threshold)** — Absolute-tokens scaled-by-$\kappa$ is correct: $\epsilon \cdot \kappa$ has units of "softplus-output dollars-per-token-region-width", which is what enters $q_t^{\text{USD}}$ via $p_t \cdot \mathrm{softplus}_\beta(\cdot)$. A relative threshold ($L^1 / L^1(\beta=0)$) would be undefined since $L^1$ at $\beta = 0$ over $[0, 2\kappa]$ gives $\kappa^2$ (the ReLU integral itself), not a calibration anchor. Absolute is correct. NO flag.

### MQ-BLOCK-3 (Blended $p_t$ verbatim) — **RESOLVED**

Pin M3 reproduces the formula verbatim. Independently verified arithmetic:
$0.539 \cdot 3 \cdot (1 - 0.95 + 0.95 \cdot 0.10) + 0.461 \cdot 15$
$= 0.539 \cdot 3 \cdot 0.145 + 0.461 \cdot 15$
$= 0.234465 + 6.915 = 7.149\ldots$ ✓

**Sub-question 2 (cache-discount on input only)** — CORRECT. Anthropic prompt-caching pricing applies the 90% discount to *cached input tokens* only; output tokens are billed at full rate. Formula is empirically faithful.

**Sub-question 3 (`dimensional-analysis` skill)** — DEFENSIBLE. The skill is listed as available; it annotates units in arithmetic-heavy code. For a `$/MTok` return type, dimensional annotation prevents the classic bug-class of mixing $/Mtok with $/token (off-by-$10^6$). The pin is enforceable: Reality Checker step 9 verifies the Sonnet ≈ 7.15/MTok value at test-execution time, which is a dimensional check by reproduction. Acceptable enforcement mechanism.

### MQ-BLOCK-4 (Parquet/JSON schemas verbatim) — **RESOLVED**

Pin M4 reproduces all three schemas verbatim. Cross-check vs spec §10:

- `cohort_prior.parquet`: spec columns `param, percentile, value, source, fetched_at_utc` — Pin M4 identical ✓
- `synthetic_tau_t.parquet`: spec columns `month, simulation_id, tier_id, r, p, alpha, x_m, tau_t, q_t_usd, q_t_cop` — Pin M4 identical ✓
- `Z_cap_pinned.json`: Pin M4 fields `Z_cop_per_month, ci_95_lo, ci_95_hi, audit_block, tier_mix` — match spec §10 (verified by §15.7 audit-trail).

Task 2.3 ("validates column presence on read", typed `SchemaMismatchError`), Task 4.1 step 9 ("M4 INCLUDING Z_cap_pinned.json schema enforced by direct test execution"). Closed chain.

---

## Resolution status — v0.1 FLAGs

| ID | Status | Note |
|---|---|---|
| MQ-FLAG-A (FX path source anchor) | RESOLVED | Pin M5 cites PRIMITIVES (6) + (8); docstring requirement |
| MQ-FLAG-B (mutation 80% justification) | RESOLVED | §15.12 cites Coles 2016, Petrović & Ivanković 2018; disambiguated from §8(7) |
| MQ-FLAG-C (audit-pass ordering) | RESOLVED | §15.5 swaps to pre-mortem (3.5) → mutation (3.6) |
| MQ-FLAG-D (pre-mortem scope) | RESOLVED | §15.4 expands to modules + utils |
| MQ-FLAG-E (joint-identifiability) | RESOLVED | §15.3 adds property test in 3.3 |
| MQ-FLAG-F (TruncParetoParams placement) | RESOLVED | §15.13 splits types (open) / sampler (enforces) |

---

## NEW MQ-FLAGs introduced by v1.1

### MQ-FLAG-G (LOW-MEDIUM) — Sampler-refusal vs posterior-§8(6) hand-off undocumented

§15.13 says floor binds at sampler boundary. It does NOT say the sampler-refusal *coexists with* the posterior-level §8(6) HALT in COHORT-2; an implementer reading the plan in isolation might assume sampler-refusal *replaces* the posterior gate (silently weakening §8(6) to "we never sampled there, so we can't HALT there"). **Fix**: add one sentence to §15.13: "Sampler-refusal at α < 1.5 is a synthesis-time guard; the posterior-level §8(6) gate in COHORT-2 is preserved unmodified — both fire if the data prefers α < 1.5 despite the prior support." Defer to v1.1.1 plan-doc patch (not blocking).

### MQ-FLAG-H (LOW) — M2 support window not justified

Pin M2 picks $[0, 2\kappa]$ without rationale. Spec §5.1 underspecifies (says "$L^1$ deviation"; no support named). Plan choice is non-fishing (fixed pre-data) but lacks documented rationale. **Fix**: add one sentence to Pin M2 — "Support choice $[0, 2\kappa]$ chosen to symmetrically span the kink at $\tau_t = \kappa$; alternative supports (e.g., $[0.5\kappa, 1.5\kappa]$) would yield equivalent tightness numerics by closed-form symmetry, and any choice fixed before data is anti-fishing-compliant." Non-blocking.

---

## NEW failure modes — assessment

### A. Pin M1 split (types open / modules enforces)
NOT a new failure mode. Documented in §15.13; matches spec scoping. Future-iteration risk addressed by MQ-FLAG-G hand-off note.

### B. Audit-pass reorder (3.5 ↔ 3.6)
Clean dependency. Pre-mortem produces fragility inventory → tests added under `hypothesis-tests` re-runs OR added at pre-mortem step → mutation-testing measures kill-rate of resulting suite. Order is methodologically correct (matches Petrović & Ivanković 2018 sequencing).

### C. Pre-mortem scope to utils/
ACCEPTABLE. The `pre-mortem` skill is described as identifying "fragile code, implicit assumptions, and likely failure modes by writing realistic incident reports" — IO boundaries (race conditions, schema drift, partial writes) are textbook pre-mortem surface. Skill handles both pure-transform and IO patterns.

### D. 5% equivalent-mutant cap
DEFENSIBLE BUT TIGHT. Coles 2016 reports practical equivalent-mutant rates of 10–20% for non-trivial codebases; 5% is aggressive. However, `simulations/{types, modules, utils}/` is intentionally a *thin* infrastructure layer (Value tier has no logic; Callable tier has tightly-scoped transforms). For thin layers, 5% is feasible. The Code-Reviewer-audit fallback (§15.6 "audits the exemption list before the audit pass closes") prevents the cap from forcing artificial test additions to dodge reviewer scrutiny. NO new flag, but watch-item for the implementing agent.

---

## Theatrical-fix detection

- §14 "no threshold relaxed" — **VERIFIED**. M1 adds typed-error enforcement (new constraint); M2 adds tightness-refusal (new constraint); M3 fixes formula verbatim (no threshold); M4 fixes schemas verbatim (no threshold); M5 fixes equation source (no threshold). 5% cap is a NEW constraint. NOT theatrical.
- §15.13 "saas-α-floor leak" — **GENUINE FIX**, not relabel. Old: ambiguous location; new: explicit split with sampler enforcement + Phase-4 verification step. Closed loop.
- §15.10 Phase-2 split — **GENUINE REDUCTION**. Total surface (4 directories of code) is unchanged, but per-dispatch surface is 1/4: each Data Engineer dispatch now sees only one tier's contract + scoped imports. This reduces *cognitive surface per agent*, which is the relevant complexity for theatrical-pass risk. NOT relabel — each dispatch has independent commit + ty-check + pytest gate.

---

## Sub-task dispatch recommendation

**PROCEED** to Phase 0 → Phase 5 execution per v1.1 plan, with two non-blocking follow-ups for v1.1.1 plan-doc patch:
1. MQ-FLAG-G: sampler-refusal vs posterior-§8(6) hand-off sentence.
2. MQ-FLAG-H: M2 support-window rationale sentence.

Both are documentation tightening, not behavior-contract changes. No re-dispatch of plan-doc 2-wave verify required for these.

End of Wave-2 Model QA v1.1 reverify.
