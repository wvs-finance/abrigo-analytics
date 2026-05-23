# Wave-1 Reality Checker — saas-builder-stage-2-prereg-lock v1.0

**Reviewer:** Reality Checker (Wave-1, doc/source/scope discipline only — math QA is Wave-2)
**Artifact under review:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.0 LOCKED-PENDING-USER-REVIEW
**Verdict:** **REJECT** — 3 RC-BLOCKs, 5 RC-FLAGs.

Default-to-REJECT discipline applied per repo precedent (`scratch/path-b-stage-2/phase-1/corrections_eta_decomposition.md` Wave-1). Reality issues below must be patched before sub-task plans dispatch. None require re-doing the empirical research; all are spec-text fixes.

---

## RC-BLOCKs (load-bearing; prevent ACCEPT)

### RC-BLOCK-1 — dev-AI Stage-1 FAIL is not addressed anywhere in the spec
**Severity:** Highest. This is the load-bearing reality-check failure.

**Evidence.** Grep for `dev-ai|dev_ai|section j|stage-1 fail|macro fail` across the entire spec returns **zero hits**. Yet `memory/project_dev_ai_section_j_fail.md` (2026-05-06) records: "Section J × COP/USD lagged tested NEGATIVE β=-0.146 sign-flip … Stage-1 hypothesis empirically REJECTED for dev-AI-paying population … Per-user a_s instrument cannot be designed against rejected transmission (would be SHORT-FX, opposite of what dev-AI-paying population needs given USD-denominated AI tooling costs)." `memory/project_saas_builder_stage_2_active.md` explicitly notes: "dev-AI failure raises required Stage-1 sign-prior strength but does not invalidate this iteration's hypothesis."

The spec under review *is* a SaaS-builder Stage-2 cohort calibration pre-reg whose target population overlaps strongly with the dev-AI-paying population just FAILED at Stage-1. It silently proceeds to Stage-2 ideal-scenario M-sketch without reconciling. Per CLAUDE.md "Stage-correctly with explicit exit criteria" — Stage 1 *empirical β confirmation* is exit-1. Proceeding to Stage-2 against a sign-flipped Stage-1 is exactly the stage-drift the framework anti-fishing-bans, unless the spec explicitly argues *why this cohort differs from Section J ICT* and what new sign-prior justifies Stage-2.

**Quote.** §0 "Out of scope. Stage-1 empirical β work (handled by separate iteration)" — this disposition silently waves away the FAIL without engaging it.

**Fix.** Add §0.1 "Relation to dev-AI Stage-1 FAIL (2026-05-06)": (i) acknowledge β=-0.146 sign-flip on Section J; (ii) state explicitly why this cohort (post-revenue solo SaaS builders with COP MRR + USD AI costs) is *not* the Section J narrow-ICT employment-share population; (iii) declare the new Stage-1 sign-prior (or argue Stage-2 ideal-scenario is permitted under CLAUDE.md "ideal-scenario clause" *independent* of empirical β); (iv) record this as a CORRECTIONS-block ancestor.

---

### RC-BLOCK-2 — N_MIN=75 / POWER_MIN=0.80 / MDES_SD=0.40 mis-imported into a synthetic-data setting
**Severity:** High. Substantive trap flagged in the prompt.

**Evidence.** §8 lines 273-275: "Carried verbatim from CLAUDE.md (NON-NEGOTIABLE): N_MIN=75, POWER_MIN=0.80, MDES_SD=0.40 SD-units of any outcome variable." But §5 + §10 + §9 establish the Stage-2 calibration as Bayesian posterior over (T1) parameters fed by `data/synthetic_tau_t.parquet` (per §10 schema: "columns: month, simulation_id, lambda, mu, s, tau_t, q_t_usd, q_t_cop"). N_MIN=75 is an **empirical-cohort sample-size floor** (anti-fishing for power calculations on real Y); MDES_SD is the minimum-detectable-effect for an empirical regression. Neither is meaningful for a synthetic-data Bayesian posterior over (lambda, mu, s) priors anchored to public-pricing brackets — you can run 10000 sims trivially, and there is no "outcome variable Y" being regressed.

The verbatim carry-forward is *category-error*: the invariants apply to Stage-1 empirical β work, where this iteration explicitly is not. CLAUDE.md "Anti-fishing invariants" section is written for the empirical-validation half. §5 of the spec calls out "Cohort first-party survey (Option γ) is a Stage-3 prerequisite, not a Stage-2 input" — i.e., Stage-2 has no n=75 cohort to apply N_MIN to.

**Fix.** Replace §8 verbatim invariants with: (a) the genuinely-applicable invariants — pre-pin sign expectation BEFORE simulation; bracket immutability; HALT-on-spec-data-conflict; (b) explicit declaration that N_MIN/POWER_MIN/MDES apply to Stage-3 cohort survey (Option γ, n=30-75 per RESEARCH.md §6) when it runs, not Stage-2 synthetic calibration; (c) Stage-2-specific synthetic-fit invariants (e.g., posterior credible-interval width thresholds, sim-count floor, prior-sensitivity sweep requirement).

---

### RC-BLOCK-3 — §5.4(c) introduces bank-spread $s_t$ overlay nowhere instantiated in §3 FX path
**Severity:** High. Silent realism-override that contradicts the FX-path-class lock.

**Evidence.** §5.4(c) line 216-217: "Bank-spread overlay $s_t \in [1\%, 3\%]$ applied to $(X/Y)_t$ in primary spec; varied as sensitivity arm." Yet §3 lines 60-63 lock the primary FX scenario as the deterministic perturbation (PRIMITIVES.md (6)) with no $s_t$ term: "$(X/Y)_t = (1 + \varepsilon(\cos^2(\omega t) - 1/2))\,\overline{X/Y}$" — full stop. §6 functional-form table line 229 says " $(X/Y)_t$ — (6) deterministic perturbation … sensitivity arms: GBM, OU, jump, empirical." No bank-spread arm.

This is a quiet primary-spec mutation hidden in §5.4 ("realism overrides committed"). Either §3 is the lock (and $s_t$ is a sensitivity arm only — fix §5.4 wording), or §3 needs to explicitly add the $s_t$ overlay to the primary path equation. Right now §3 and §5.4(c) contradict.

**Fix.** Pick one: (option A) Demote §5.4(c) to "sensitivity arm" only — $s_t$ does not enter §3 primary path; primary $(X/Y)_t$ remains pure (6). (option B) Promote $s_t$ into §3 with explicit modified equation $(X/Y)_t^{\text{eff}} = (1+s_t) \cdot (X/Y)_t$ and update §6 row.

---

## RC-FLAGs (lower-severity; follow-up required)

### RC-FLAG-1 — pitch's $Z$ has no operational definition in this spec
**Evidence.** §4 line 76: "$Z$ in the pitch ('bill in COP never exceeds $Z$') reported in COP." That is the *only* mention of $Z$ in the spec. The pitch's math interpretation lives in `notes/SaaS_Builders_AI_NativeBuilders.md` lines 137-141 ($Z$ is the cap such that $E[q^{det}/(X/Y) + \pi(t)] \le Z$). The spec inherits the pitch but does not (a) cite the cohort-note formula by line, (b) commit a sub-task gate to *computing* $Z$, or (c) record $Z$ in the §10 output schema. Risk: marketing claim with no math backing materializes downstream.
**Fix.** Add §4.1 referencing cohort-note pitch formula verbatim; add `estimates/Z_cap_pinned.json` to §10 schema; add to TODO-COHORT-4 done-when criterion.

### RC-FLAG-2 — §5.4(a) ~$2k/mo upper bound contradicts §5.2 ">$2,000 p99"
**Evidence.** §5.4(a) line 213: "Bracket subsumes mixed-tier usage including API-heavy builders to ~$2k/mo upper bound." §5.2 line 191: "$150-$400 modal, $500-$1,500 p90, **> $2,000 p99**." A p99 of >$2k means the distribution has positive mass *above* $2k; an "upper bound ~$2k" caps it at $2k. The right tail is exactly the regime the CPO sells (per §5.2 line 192-193 + RESEARCH.md TL;DR). Don't truncate it via §5.4(a) phrasing.
**Fix.** Reword §5.4(a) to "modal coverage ~$2k/mo, distribution is heavy-tailed with p99 > $2k preserved per §5.2."

### RC-FLAG-3 — Cap-quota $\kappa$ ≈14.5 M tokens/mo derivation has stale arithmetic
**Evidence.** §5.2 lines 153-157: "Max-20x ≈ 220k tok/5h [tokenmix, verdent]. Annualized at 22 active days/mo, three 5-hour windows/day: Max-20x $\kappa \approx 14.5$ M tokens/month." 22 × 3 × 220k = 14.52 M — checks. BUT: §5.2 line 150-152 also notes "2026-05-06: 5-hour limits doubled, peak-hour reductions removed [9to5google, anthropic-spacex]; baseline numbers not officially published." If limits doubled on 2026-05-06 (yesterday relative to spec date 2026-05-07) the 220k figure is stale; new effective cap could be ~440k tok/5h ⇒ $\kappa$ ≈ 29 M tok/mo. The spec preserves the pre-doubling number for $\kappa$ without flagging it.
**Fix.** Add explicit footnote: "$\kappa$ value uses pre-2026-05-06 cap structure; post-doubling re-pin queued for next audit_block when independent third-parties publish updated estimates" — and pin a sensitivity arm at 2× the bracket.

### RC-FLAG-4 — §5.2 effective input rate "≈$0.30/MTok Sonnet w/ 95% cache hit" is not derivable from cited sources
**Evidence.** §5.2 line 188: "Effective input rate w/ 95% cache hit ≈ $0.30/MTok Sonnet". Sonnet input is $3/MTok; with 95% cache hit at -90% on hits: $0.05 \cdot 3 + 0.95 \cdot 0.3 = 0.435$ ≈ $0.44/MTok. The spec figure $0.30 implies 95% × ($3 × 0.10) + 5% × $3 ≈ $0.435 — wait, the math depends on whether the -90% applies on the *cached* portion (then 95% pay $0.30, 5% pay $3.00, blend = $0.435) or on the entire bill. Either way $0.30 is the *cached-tokens-only* rate, not the blended effective rate. Source [alderson] is cited in RESEARCH.md line 62 for the same number — but RESEARCH.md attributes it to alderson directly. Spec should clarify whether $0.30 = blended or cached-only.
**Fix.** Add one-line clarification in §5.2: "$0.30/MTok = cached-portion rate (= $3 × 0.10); blended at 95% cache hit ≈ $0.43/MTok."

### RC-FLAG-5 — §5.3 substantiation honesty is good, but §5.2 row "Heavy / multi-agent $30-50/day" cites both [costs-doc] and [b2l-ouyang]
**Evidence.** §5.2 line 174: "Heavy / multi-agent $/day | $30-$50/day | costs-doc, b2l-ouyang". RESEARCH.md §3 line 49 says heavy is "$30-50/day on multi-agent or refactor days" with no source citation in that line; only Ouyang ($1,600/mo ≈ $50/day) is in §4. costs-doc has p90≤$30/day. So the bracket $30-$50 is a bridge between costs-doc p90 ($30) and Ouyang single anecdote ($50/day blended). Calling that "costs-doc, b2l-ouyang" overstates costs-doc — costs-doc's p90 is the ceiling not the bracket. Minor source-citation hygiene issue.
**Fix.** Change citation to "costs-doc (p90 $30/day) + b2l-ouyang ($50/day single anecdote)".

---

## Summary
- 3 RC-BLOCKs: dev-AI FAIL silently ignored; anti-fishing invariants mis-imported into synthetic regime; bank-spread overlay contradicts §3 FX-path lock.
- 5 RC-FLAGs: $Z$ undefined; §5.4(a) vs §5.2 numerical inconsistency; $\kappa$ stale post-2026-05-06; effective-rate arithmetic ambiguous; one citation overstates source.
- All other reality-check focus areas (cohort fencing §1↔§5.1; bracket immutability §8; output-artifact schema §10; reference integrity for CORRECTIONS-η/-ι and Path A v0/v1/v2/v3) **PASS** on this Wave-1 inspection.
- Send back for revision; re-submit at v1.1 addressing 3 BLOCKs at minimum. Wave-2 Model QA does not run until BLOCKs cleared.
