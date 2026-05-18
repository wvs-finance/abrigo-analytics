# Reality Checker review — Direction 1 (USD-earning Colombian Remote Workers, ADP bridge)

**Spec under review:** `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-18-four-direction-gating-step-plans.md` lines 13–65
**Reviewer:** Reality Checker (evidence-default; default verdict NEEDS_WORK absent overwhelming evidence)
**Scope:** Direction 1 only. Cross-direction context read but not adjudicated.

## Verdict

**NEEDS_WORK**

The direction is *substantively* sound — flipping FX exposure from cost-side to wage-side is a defensible response to the v0.2.10 R5 ≈ 0% null, and the population (USD-paid Colombian remote workers) is real and growing. However, the *gating plan* as written rests on at least three unverified empirical premises that, if false, collapse the parallel-track backstop to a single fragile branch (ADP). The 5-day effort estimate is unrealistic under any branch that requires institutional negotiation. The pass-criteria contain at least one unsupported numerical threshold that reads as wishful (10K cohort). Rework before dispatch.

This verdict is not a rejection of the direction. It is a rejection of the gating plan's confidence calibration.

---

## Critical issues (MUST fix)

### C1. DANE GEIH "foreign employer" identifier is asserted, not verified — and the Migration Module is almost certainly the wrong module

**Spec text (line 32):** "DANE GEIH 2023+ waves: scan for a 'trabaja para empleador extranjero' / 'remuneración en divisa' tag."
**Spec text (line 39):** "pull DANE GEIH 2023-2024 microdata; identify whether the 'foreign employer' identifier exists. If yes, this is a public-data backstop and ADP risk drops to zero."

**Reality check.** The DANE GEIH Migration Module that the spec implicitly relies on is titled "Módulo de Migración" and its documented scope is *"información básica de la población migrante presente en Colombia"* — i.e., immigrants **into** Colombia, not Colombians working remotely **for foreign employers from inside** Colombia. These are categorically different populations. The 2021 and 2024 catalog entries (`microdatos.dane.gov.co/index.php/catalog/700`, `/819`, `/837`) confirm the module is sized for the Venezuelan migration wave, not for cross-border-remote labor.

The core GEIH employment block does collect employer characteristics, but the standard variable set (P6630, P6920, P7050-series indexed by the catalog) records firm size, sector (CIIU), formality, and contract type — **not employer country-of-domicile or wage-currency-of-payment**. I could not locate any published GEIH variable that records "salary paid in USD" or "employer headquartered abroad." This is consistent with prior GEIH design intent (a labor-force survey for *domestic* labor-market statistics).

**Why this is a critical issue, not a nit.** The spec's risk-mitigation logic is: "ADP legal turnaround is unbounded. *Mitigated by* the DANE/Banrep parallel track which has no third-party dependency." If GEIH lacks the variable, the parallel track collapses to Banrep alone (see C2), and the "no third-party dependency" mitigation evaporates. The fail-criteria three-way AND condition (line 49) becomes effectively a two-way AND, materially raising the probability of a gate-step FAIL that the spec presently treats as a tail risk.

**Required fix.** Before dispatching the gate step, the spec author must either:
- (a) Cite the specific GEIH variable name (e.g., a P-code from the questionnaire dictionary) and year-range in which it appears, OR
- (b) Demote the GEIH branch from "public-data backstop" to "exploratory — likely-absent" and re-rank the risk mitigation accordingly, OR
- (c) Identify a *different* DANE instrument that does carry foreign-employer / foreign-currency-wage tags. The DEX (Declaración de Exportación de Servicios) filings via DIAN may be a better candidate but they are firm-level, not worker-level. The Encuesta Pulso de la Migración (EPM) is similarly mis-targeted.

**Until this is resolved, the "parallel track is the safety net" framing is structurally unsupported.**

### C2. Banrep BoP "servicios informáticos" is firm-invoice revenue, not worker wages — and the spec's "disaggregated to wage component" requirement is unverified

**Spec text (line 33):** "Banrep Balance of Payments services-exports line `servicios informáticos y de información`. Captures aggregate USD inflow at macro level — coarse but free and continuous since 2000."
**Spec text (line 49, fail criteria):** "Banrep BoP 'computer services' line cannot be disaggregated to wage component."

**Reality check.** Under IMF BPM6 (which Banrep follows per the BoP methodology summary at `banrep.gov.co/sites/default/files/paginas/Colombia%20Balance%20of%20Payments%20Metadata%20summary.pdf`), there are two structurally distinct accounts:

1. **Services account → "computer services" / "servicios informáticos"** — captures *firm-to-firm* invoicing for software, IT consulting, hosting. The exporter of record is a Colombian *firm*. This is where a Colombian software house or contractor LLC invoicing a US client lands.
2. **Primary income account → "compensation of employees"** — captures cross-border *wages* where the worker is resident in one country and the *employer* is resident in another. This is the BPM6 category designed for the Direction-1 population (Colombian-resident worker, US-resident employer paying via EOR).

The spec conflates these. A Colombian remote worker on Deel/Remote.com's EOR-of-record path may end up in **either**:
- "Compensation of employees" (if the BPM6 employer-residence test is satisfied — typically yes for a true EOR), OR
- "Computer services exports" (if the worker is invoicing through their own RUT as an independent contractor — common in the Colombian tech-freelancer cohort).

In practice **Banrep does not publicly disaggregate "compensation of employees" by sender country at monthly granularity**, and "computer services exports" includes a mix of firm-invoice and freelancer-invoice flows with no published cohort split. The "disaggregated to wage component" requirement in the fail criteria is therefore *not satisfiable from public data alone* under any obvious branch.

**Why this is critical.** Combined with C1, both public-data branches of the three-way OR in the pass criteria are weaker than the spec represents. The pass criteria (line 44) say "*At least one of* {ADP, DANE, Banrep} yields a monthly panel ≥75 obs." If DANE has no foreign-employer variable (C1) and Banrep can't separate wages from firm-invoice services exports (C2), then the gate genuinely depends on ADP delivering — which the spec elsewhere treats as the high-risk leg.

**Required fix.** The spec must clarify:
- (i) Which BoP line is the target — "compensation of employees" (primary income) or "computer services" (services account)? They have different policy meanings and different empirical β interpretations.
- (ii) For "compensation of employees": confirm Banrep publishes this at monthly frequency disaggregated by counterparty country (the IMF BPM6 *recommends* but does not require this; many central banks publish only quarterly aggregates).
- (iii) For "computer services": acknowledge upfront that this includes firm-level invoice revenue and is **not** the wage-channel Y the iteration claims to measure. Either (a) accept it as a *macro proxy* with explicit fragility, or (b) drop it from the parallel track.

### C3. The 10,000-worker cohort threshold is asserted without external evidence

**Spec text (line 45):** "Estimated cohort size ≥ 10,000 workers (population relevance)."
**Spec text (line 50, fail):** "Cohort size < 1,000 workers."

**Reality check.** Public evidence supports the *existence and growth* of the cohort (Bogota Post, Nearshore Americas, Deel's own marketing reports all cite Colombia among top LATAM destinations for international remote hiring; the often-cited "55% YoY growth in international hiring in Colombia" figure traces to Deel's 2024 Global Hiring Report). But I could not locate any peer-reviewable public source that pins the *level* of Colombian USD-paid remote workers at any specific number — vendor marketing reports are not adversarially audited.

The 10K threshold therefore reads as a round-number guess. It might be conservative; it might be aggressive. The point is the spec doesn't *justify* it. This matters because the threshold drives the gate verdict, and the verdict drives a multi-month iteration commitment.

**Required fix.** Either:
- (a) Cite a defensible external anchor (e.g., DANE's GEIH count of "ocupados en sector información y comunicaciones × estimated foreign-employed share" with arithmetic shown, or an aggregated Deel/Remote.com report figure with the URL and access date), OR
- (b) Reframe the threshold as **"≥ minimum-required-N for the downstream β-estimate's per-capita normalization to be stable"** — i.e., derive it from statistical requirements rather than asserting a population-relevance figure. The current 10K vs 1K split is a factor-of-10 dead zone with no decision rule.

This is not a quibble. The threshold-without-justification pattern is exactly what the project's `feedback_pathological_halt_anti_fishing_checkpoint.md` warns against. If empirical cohort size lands at 4,500, the spec leaves no principled way to adjudicate; the temptation will be to retune.

---

## Strong recommendations (SHOULD fix)

### S1. The 5-day effort estimate is unrealistic on at least two branches

**Spec text (lines 53–57):** Day-by-day plan totaling 5 working days, with day 1 = "draft ADP memo + run past your contact."

**Reality check.** Three branches of work each have wall-clock floors well above the rolled-up 5-day estimate:

1. **ADP path.** Per ADP's own public privacy stance (`adp.com/about-adp/data-privacy.aspx`, `adp.com/wfmlicenseterms`), aggregate-anonymized data sharing is governed by client confidentiality clauses and goes through ADP's Global Chief Privacy Officer. ADP **does** routinely publish aggregated anonymized data via the ADP Research Institute (National Employment Report, Pay Insights, Today at Work) — but **the country granularity is US-focused**, and country-level Colombian cuts are not a documented public product. A custom de-identified extract for an external researcher is a *legal-and-engineering* request, not a Day-1 email. Realistic SLA: 4–12 weeks if it happens at all; "weeks-to-quarters" is the right scale.
2. **DANE microdata path.** Standard GEIH waves are directly downloadable from `microdatos.dane.gov.co` (no application gate), so this *can* be a same-week pull. But custom microdata requests — which the spec contemplates (line 32: "propose a custom microdata request") — have their own SLA, typically 4–8 weeks for academic users.
3. **Banrep BoP path.** The aggregate quarterly series is downloadable today. But the *disaggregation* the spec requires (wage vs invoice, by counterparty country) likely requires a custom data request and is not on the public site.

**The 5-day clock assumes only the "happy path" pulls execute.** None of the rework branches fit in 5 days. The gating step as designed cannot reach its own pass/fail decision in the allotted time if any of {ADP-aggregate, DANE-custom, Banrep-disaggregated} is needed.

**Recommended fix.** Split the gating step into two phases:
- **Phase G1 (5 days, no external SLA dependency)**: download standard GEIH 2023/2024/2025 waves and verify variable inventory (yes/no on foreign-employer identifier); pull standard Banrep BoP quarterly aggregates; tabulate ADP Research Institute publicly published Latin-America figures (if any); compose the request memos. Output: data-availability matrix + drafted requests.
- **Phase G2 (4–12 weeks wall-clock, parallel-track)**: ADP legal turnaround + DANE/Banrep custom requests. Gate decision deferred to G2 close.

The current spec collapses G1 and G2 into a single 5-day window, which is an honesty-of-estimate problem.

### S2. Pre-pin the gate-decision rule and the "thin data" exception

**Spec text (line 44–50):** Pass and fail criteria are listed but the spec does not address what happens in the *middle zone* (e.g., one source delivers ≥75 obs but cohort size lands at 4K, or two sources deliver but neither reaches 75 obs alone).

**Reality check.** The middle zone is where threshold-tuning fishing typically enters. The v0.2.10 verdict memo explicitly anchors this iteration in the lessons of the closed cost-side iteration, and `feedback_pathological_halt_anti_fishing_checkpoint.md` is binding on gating decisions even though the spec correctly notes (line 9) that gating steps are exempt from N_MIN as β-floors.

**Recommended fix.** Add a CONDITIONAL pass case with pre-specified rules. Example:
- PASS = (any source ≥ 75 obs) AND (cohort ≥ 10K) AND (growth ≥ 5%)
- FAIL = all sources < 75 obs OR cohort < 1K
- CONDITIONAL = anything else → escalate to user for explicit pivot, **do not relax thresholds in place**.

The "CONDITIONAL" column already appears in the cross-direction governance matrix (line 246) but is not defined for Direction 1's own criteria. Define it.

### S3. The hedge instrument (M-sketch) has a sign error or framing issue

**Spec text (line 18):** "long-USDC / short-COPm position on the Mento `USDC/COPm` Panoptic pool, sized to expected next-period USD wage. Hedge protects against COP appreciation eroding COP-converted wage."

**Reality check.** A USD-paid worker faces *FX appreciation of the COP* as the income-eroding event (a stronger COP per USD = fewer COP per USD wage). A "long USDC / short COPm" position is *already* the worker's natural balance-sheet position — they hold USDC (their wage) and want COP. They are **structurally long USD/COP via their wage income**. A *hedge* should reduce, not amplify, that exposure. The position described would *double down* on USD/COP, not hedge it.

The premium-funded ratchet logic the Abrigo framework prescribes (per CLAUDE.md: "wage→productive capital via premium-funded ratchet") actually wants the *opposite*: the worker should run a position that pays off **when COP appreciates** (since that's when their COP-converted wage falls). That's long-COPm / short-USDC convex payoff, or equivalently a put on USDCOP.

This may be a wording slip rather than a fundamental design error, but the M-sketch as written in line 18 is internally inconsistent with the Y definition in line 16 ("`usd_wage × spot_COP_USD`" — i.e., COP-realized wage falls when spot falls, which is COP appreciation, which the spec then says it wants to hedge by being *long USD*).

**Recommended fix.** Re-examine the M-sketch sign. State the direction of the COP/USD shock against which the hedge protects, and confirm the Panoptic position pays off in that direction. This is gate-step out of scope (M-design is Stage 2 per CLAUDE.md), but the gate-step document is the anchor for the iteration's framing and should not contain a sign error that will propagate.

### S4. Single-source-on-ADP risk is acknowledged but the "do not single-source" framing is contradicted by the parallel-track collapse

**Spec text (line 31):** "Public-proxy parallel track (do not single-source on ADP)."

**Reality check.** This is the right *principle*, and the structural design intent is sound. But once C1 and C2 above are factored in, the parallel track is much thinner than the spec admits. If the gate runs and the answer is "GEIH variable absent + Banrep can't disaggregate," the only remaining path is ADP — exactly the single-source position the spec wanted to avoid. The risk register (line 60) flags ADP timeout as a risk but does not flag the *correlated failure* of the parallel track.

**Recommended fix.** Add a risk-register entry for "parallel-track correlated failure" with the mitigation being "fall back to a different Direction (2, 3, 4) rather than wait on ADP indefinitely." This is partly what the cross-direction governance (line 252) does, but it should be explicit at the Direction-1 level too.

---

## Nits (MAY fix)

### N1. "DANE handles these for academic users" (line 32) is unsourced

DANE does process custom microdata requests, but the affiliation requirements, SLA, and confidentiality terms are nontrivial. Cite the specific DANE process (URL or contact) the spec author has in mind.

### N2. Public salary surveys (Mercer, Hays, Bumeran) carry a sample bias toward formal-sector white-collar reporting

The spec lists them (line 34) without flagging this. For a population that includes a large independent-contractor share, these surveys systematically miss the relevant tail. Flag as caveat.

### N3. The "(b) headcount of the Colombian USD-paid cohort" field (line 25) duplicates field 6 ("YoY cohort growth rate")

If headcount is in the request, growth rate is a derivable column, not a separate field. Streamline the request memo.

### N4. The cohort-growth-≥5% pass criterion needs a denominator

Growth in absolute headcount? In USD-payroll volume? In Colombian-share of EOR providers' books? The denominator changes which signal you are reading. Specify.

### N5. Reference to "your contact" (line 54)

Anonymized for the spec, but the day-1 deliverable should record the contact's role (ADP US? ADP Latam? ADP corporate? ADP Research Institute?). Each routes to a different legal pathway.

---

## Open questions for the spec author

1. **GEIH variable existence.** Have you (or anyone you trust) verified that a "foreign employer" / "wage paid in foreign currency" variable exists in GEIH 2023+ microdata before drafting line 32–39? If yes, please cite the variable code. If no, please demote the GEIH branch in the risk register.

2. **BoP target line.** Are you targeting "compensation of employees" (primary income, BPM6) or "computer services exports" (services account, BPM6)? They are different populations and different β interpretations. Pick one as primary.

3. **ADP relationship granularity.** Is your contact at ADP US, ADP Latin America, or ADP Research Institute? The first two route through commercial+legal; the third routes through a research-partnership pathway (the Stanford Digital Economy Lab template). The two paths have very different SLAs.

4. **Cohort threshold derivation.** Where does 10K come from? If it's a guess, that's fine, but say so and convert it into a sensitivity ("at 5K we still proceed; at 1K we close") so the gate decision is not held hostage to a number you didn't defend.

5. **M-sketch direction.** Confirm the hedge direction (long-COPm / short-USDC, the put-on-USDCOP framing) rather than the wording in line 18 (long-USDC / short-COPm). If line 18 is intentional, justify why doubling down on the USD position serves the wage-earner.

6. **Gate-step output venue.** Line 65 says `scratch/2026-05-XX-direction-1-gating/gate_decision.md`. Today's date is 2026-05-18, the path stub will need filling. Trivial but flag for housekeeping when dispatched.

7. **Anti-fishing carryforward to G2.** If you accept the G1/G2 phase split (S1), please pre-pin in the spec which Phase-G2 outcomes trigger HALT vs CONDITIONAL vs PASS. The current spec only pre-pins G1's pass/fail rule. The longer wall-clock of G2 is where retuning temptation is largest.

---

## Summary for the framework owner

Direction 1 is a *substantively good* pivot but the gating plan is *structurally over-confident* in three places (DANE variable existence, Banrep disaggregation, 5-day clock). Two of these are empirically resolvable in a one-day pre-check (download GEIH 2024 dictionary; read Banrep BoP methodology PDF in full). I recommend a 1-day **pre-gate sanity check** by the spec author to confirm or deny C1 and C2 before the formal 5-day gate-step is dispatched. If C1 and C2 hold up, the spec is downgraded to a single-source-on-ADP plan and the resource allocation should reflect that. If they don't hold up, the spec is rewritten with the corrected parallel track.

Default to NEEDS_WORK; revisit after the pre-check.

---

**Evidence anchors used in this review:**

- Spec under review: lines 13–65 of `docs/specs/2026-05-18-four-direction-gating-step-plans.md`
- `memory/project_dev_ai_cost_v2_verdict.md` (the closed iteration motivating the pivot)
- `memory/feedback_pathological_halt_anti_fishing_checkpoint.md` (anti-fishing discipline binding here)
- `CLAUDE.md` Abrigo framework section (Y/M/X, premium-funded ratchet sign convention)
- DANE microdata catalog: `microdatos.dane.gov.co/index.php/catalog/{700, 782, 819, 837, 853}` — Migration Module scope and GEIH 2018-2025 catalog entries
- DANE Migration Module landing page: `dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/geih-modulo-de-migracion` — scope = migrant population *in* Colombia
- Banrep BoP methodology summary: `banrep.gov.co/sites/default/files/paginas/Colombia%20Balance%20of%20Payments%20Metadata%20summary.pdf` (PDF, mostly image content — methodology readable but disaggregation not confirmed in public pages)
- IMF SDDS Colombia BoP: `dsbb.imf.org/sdds/dqaf-base/country/COL/category/BOP00`
- ADP public privacy + data-sharing posture: `adp.com/about-adp/data-privacy.aspx`, `adp.com/wfmlicenseterms`, `adp.com/-/media/adp/privacy/pdf/bcrpc_en.pdf`
- ADP Research Institute partnerships pathway: `adpresearch.com/about-us/partnerships`, Stanford Digital Economy Lab collaboration template
- Colombian remote-work cohort context: thebogotapost.com 55%-YoY hiring growth article; nearshoreamericas.com "Chile, Colombia Drive Remote Hiring Boom"; Deel Global Hiring Report 2026 marketing page
- Colombian payroll/tax context for cross-border workers: brighttax.com Colombia expat guide; remotepeople.com Colombia payroll guide 2025/2026; deel.com W-8BEN glossary
