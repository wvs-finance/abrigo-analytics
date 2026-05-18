# Reality Checker — Direction 2 (Colombian Import Micro-Vendors)

**Reviewer:** TestingRealityChecker
**Date:** 2026-05-18
**Spec under review:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §"Direction 2" (lines 69–121)
**Default disposition:** NEEDS WORK (per RC mandate)
**Final verdict (this review):** **CONDITIONAL PASS with mandatory revisions** — the gating direction is salvageable but the *plan as written* contains at least three factual / operational misstatements and one structural under-scoping issue. None are fatal; all must be fixed before the gate is executed.

---

## 1. Reality-Check Validation (commands run / evidence collected)

- Read full `docs/specs/2026-05-18-four-direction-gating-step-plans.md` (all four directions) for cross-direction context.
- Read `memory/project_dev_ai_cost_v2_verdict.md` (PAUSED-PENDING-MORE-DATA anchor).
- Read `CLAUDE.md` for Abrigo framework / anti-fishing invariants.
- Web-verified DIAN open-data surface (datos.gov.co, dian.gov.co, dane.gov.co/microdatos).
- Web-verified DIAN importer-size classification scheme (RUT registration documents).
- Web-verified Centrifuge active-pool inventory and Goldfinch borrower-pool status.
- Web-searched for Colombian micro-importer universe size (Bancóldex / Confecámaras / Mercado Libre).
- Attempted live fetch of `app.centrifuge.io/pools` — page is JS-rendered, returned no usable HTML (treat as inconclusive; cross-referenced via secondary sources).

Evidence cross-references appear inline below; sources listed at the bottom.

---

## 2. Per-Numbered-Concern Findings (the six review prompts)

### 2.1 DIAN public-data realism (HS × RUT-size × monthly cross-tab) — **PARTIAL: claim is overstated**

Verified facts:

- **DIAN does publish monthly import-declaration data publicly.** The "Estadísticas de Comercio Exterior" portal at `dian.gov.co/dian/cifras/Paginas/EstadisticasComEx.aspx` and the tablero COMEX provide monthly aggregates **since 2001**, disaggregable by tariff sub-item (subpartida arancelaria) and origin country.
- **DANE also publishes a parallel imports microdata catalog** (`microdatos.dane.gov.co/index.php/catalog/473` for 2012–2024 and `/catalog/856` for 2025–2026). This catalog provides record-level import declarations with importer identifiers (anonymized/coded in the public release).
- **Therefore monthly N is not a binding constraint.** Monthly observations 2018-01 → 2026-04 give N ≈ 100, comfortably above N_MIN=75. The spec's "monthly N=99 since 2018 *if monthly request approved*" framing (line 97) is **misleadingly conservative** — monthly is the **default** public granularity, not a microdata-request escalation.

What the spec gets wrong:

- Line 80 says "DIAN customs import declarations — public quarterly aggregates; monthly granularity may require a data request." This is **factually inverted**. Monthly is public; quarterly aggregates are a *coarser rollup*, not the public floor.
- Line 91 says "File a custom DIAN data request for monthly granularity if quarterly is insufficient. (DIAN has a microdata-request process; 4-6 week SLA.)" The 4-6 week SLA may still apply for **record-level microdata with non-standard joins** (HS × importer-size jointly), but plain monthly HS-aggregated data is downloadable today.

**Implication:** the gating step should *start* from the public monthly portal and only escalate to a microdata request if the importer-size join is unavailable in the public release. Plan as written front-loads the SLA pessimism and may waste Day 1.

### 2.2 RUT importer-size brackets — **PROBLEM: this is the load-bearing assumption and it is not verified**

This is the most important finding in the review.

What the spec assumes (lines 81, 93, 98, 102):

- "Importer RUT size bracket (DIAN classifies importers; the smallest brackets approximate the micro-cohort)"
- Pass-criterion: "Importer count in target RUT-size brackets ≥ 5,000"

What the evidence actually shows:

- The DIAN cartilla de importación and Formulario 500 classify importers by **legal form** ("01" mixed-economy enterprise, "02" private enterprise, "03" other) — **not by size**. (Source: `dian.gov.co/atencionciudadano/formulariosinstructivos/.../Cartilla_importacion_2008.pdf`.)
- The general Colombian micro/small/medium/large classification is established by **Decreto 957 de 2019** (MINCIT, not DIAN) and uses **annual revenue thresholds by sector** (manufacturing, services, commerce — different cut-offs each). Source: contadorespublicossantander.com summary of Decreto 957.
- This classification is applied via the **Cámara de Comercio** business registry (RUES — Registro Único Empresarial y Social, operated by Confecámaras), **not** by DIAN customs records directly.
- To get importer-size brackets in a DIAN customs panel, one would have to **join** importer-RUT from the DIAN import declaration to RUES annual-revenue (or DANE EAM/EAS revenue tiers) to compute the size bracket as a derived field.

**This join is not a public dataset.** It would require either (a) a custom DIAN data request that returns size-tagged records (DIAN itself may not maintain the size tag), (b) a join performed by the analyst using publicly listed importer RUTs (the **Directorio de Importadores/Exportadores**, available from 2017 — see source 3) against RUES microdata (also requires request), or (c) a proxy by **import-volume bracket** (e.g., importers in the bottom quartile of annual FOB imports), which is **algorithmically derivable** from the DIAN records themselves but is **not the same construct** as the MINCIT micro-business definition.

**Verdict on the plan's framing:** the spec assumes a publicly-available DIAN size-bracketed cross-tab that almost certainly does not exist as a one-shot download. The gating step must either:
1. **Switch to a derived-bracket proxy** (e.g., importers with annual FOB < $X) using the public Directorio de Importadores + the public records, explicitly noting the proxy is **not** the MINCIT definition; OR
2. **Plan for the RUES / EAM join**, which adds a separate data-request track with its own SLA; OR
3. **File the DIAN microdata request expecting the size-bracket field to be unavailable** and adjust pass-criteria accordingly.

This is a **mandatory revision** before the gate is executed. Without it, Day 1's "DIAN public-data pull + structure assessment" will discover the missing field and the plan's Pass criteria (≥5,000 importers in target brackets) cannot be evaluated.

### 2.3 Centrifuge factor-pool inventory — **PROBLEM: factual claim is unverifiable and likely wrong**

The spec (line 99) claims at least 3 of {BRL, NGN, IDR, MXN, ZAR} pools must exist for prior construction.

Verified facts (as of 2026-Q1, multiple sources):

- Centrifuge's actively cited pools in 2026 are: **Anemoy Liquid Treasury Series 1, JTRSY (Janus Henderson Anemoy Treasury Fund), JAAA (AAA-rated CLO fund), New Silver Series 3 (US real estate bridge loans), Flowcarbon Nature Offsets Series 2** (Source: Bitget Academy Centrifuge Protocol Guide 2026; cryptonewsnavigator.com).
- These are **US-Treasury / US real estate / carbon-credit** pools. **None are EM-currency-denominated trade-finance pools.** Centrifuge in 2026 has pivoted strongly toward institutional US-denominated assets (LayerZero composability March 2026, $1.34B TVL milestone).
- **Goldfinch** (the protocol the spec actually wants, conflated with Centrifuge in line 86: "Goldfinch BRL / NGN pools as factor-loading anchors. Public via Centrifuge subgraph") is a *separate* protocol. Goldfinch's historical borrowers (PayJoy MX, QuickCheck NG, Divibank LatAm, Cauris) lent to **fintech borrowers in EM jurisdictions** but pools were **USDC-denominated, not BRL/NGN-denominated**. Goldfinch's V1 borrower-pool model wound down — 24 borrower pools have **closed**, $101.3M active loans remain, 11% of total has been repaid. The protocol has pivoted to "Goldfinch Prime: institutional private credit funds onchain" (Sources: goldfinch.finance, docs.goldfinch.finance, westafricatradehub.com Goldfinch Crypto Review 2026).

**What the spec gets wrong:**

- Conflates Centrifuge and Goldfinch (line 86: "Goldfinch BRL / NGN pools ... Public via Centrifuge subgraph" — Goldfinch is not on the Centrifuge subgraph).
- Asserts the existence of **BRL, NGN, IDR, MXN, ZAR pools** as if they were currently active EM-trade-finance vehicles. There is **no public evidence** that 3+ of these exist as active, on-chain, ≥6-month-NAV-history pools today.
- The Bayesian-prior construction strategy ("borrowing strength from sister EM tokenized-credit pools") is the **single most novel methodological move** in this direction. If the pools don't exist, the small-N pivot **collapses** to "fit a prior from one or zero analogs", which is not a credible Bayesian small-N strategy.

**Implication for the gate:** the Centrifuge factor-pool inventory step (Day 2) should be **moved to Day 1** and re-framed as a **kill-switch**: if no ≥3 active EM-trade-finance pools with NAV histories exist (across **Centrifuge + Goldfinch + Maple + Credix + Huma combined**, not just Centrifuge), the small-N pivot is unsupported and the direction's value proposition narrows to "wait for N=75 monthly DIAN observations" — at which point the small-N pivot is moot.

This is the **second mandatory revision**.

### 2.4 Mercado Libre seller-cohort access — **MOSTLY OK but minor issue**

The spec already correctly descopes ML from the gate decision (line 117: "Mercado Libre seller-cohort access is a partnership ask, not a public-data ask. Gate decision should NOT depend on ML access being granted."). This is appropriate.

Minor concern: line 84 lists ML as data input #2 *before* descoping it at line 117. The plan would be cleaner if ML were listed in a separate "Out-of-scope for gate, in-scope for full iteration" subsection. As written, a reader might allocate Day 3 effort to ML API exploration thinking it matters for the gate (and Day 3's task description "Mercado Libre API capability assessment" reinforces this confusion). **Verdict:** clarify that Day 3 is *informational only* and cannot block PASS/FAIL.

Realism on ML partnership access generally: ML has a **public Developer Platform** with order/inventory APIs available to any seller with an ML account, but **seller-cohort aggregates** (cross-seller statistics) are gated behind ML's internal data team. Without an established commercial relationship, the realistic path is **scraping public seller storefronts** (which has TOS implications) or buying from **ML's reseller intelligence partners** (e.g., Nubimetrics, Real Trends). Both are out of scope for a 5-day gate.

### 2.5 5-day effort vs 4-6 week DIAN SLA — **OK as stated, but with caveat**

The plan correctly acknowledges (lines 107, 115) that the **5-day effort estimate** is for the gating analysis itself and that the **4-6 week wall-clock** SLA on a microdata request is **parallelized** with other directions. This is operationally sound.

The unaddressed risk: if Section 2.2's "RUT-size join via RUES" path is required, that introduces a **second** parallel SLA (RUES / Confecámaras microdata request), and the joint distribution of two SLAs is not additive — it's max(SLA1, SLA2), but with non-trivial probability of needing a second request after the first comes back malformed. Suggest the plan budget **two microdata-request cycles** (~8-12 weeks wall-clock combined for the worst case).

### 2.6 Cohort-size estimation — "≥5,000 importers in target brackets" — **UNDERSPECIFIED**

The spec gives a numeric pass-criterion (≥5,000) but no derivation. Available reference points:

- The **DIAN Directorio de Importadores** is the canonical list of all natural/legal persons doing imports, available 2017+ (Source: search result on DIAN's data assets register on datos.gov.co).
- Public Bancóldex / MINCIT statistics indicate Colombia has on the order of tens of thousands of formal importers; LegisComex (one search result) hosts breakdown analyses but is paywalled.
- The Alibaba / Aliexpress / Mercado Libre micro-importer segment is **not officially measured** by any of Bancóldex, Confecámaras, or DANE — it sits at the intersection of (informal e-commerce reselling × DIAN's "courier / postal" import regime for low-value shipments × formal importer-RUT cohort).
- DIAN's **"tráfico postal y envíos urgentes"** regime (simplified declaration for shipments ≤ $2,000 USD FOB) is **the** customs channel for this cohort. Whether DIAN's monthly stats disaggregate by this regime is verifiable but **not in the plan**.

**Mandatory addition to the plan:** the pass-criterion should be re-anchored as one of:
- "Count of importer-RUTs filing ≥1 declaration in target HS codes from CN/US origin in a representative month ≥ 5,000", OR
- "Count of `tráfico postal` simplified declarations ≥ X per month".

Without anchoring "the target RUT-size brackets" to a concrete derivable proxy, the pass-criterion is **unmeasurable** and the gate can be silently fished. This is exactly the kind of post-hoc threshold drift that Abrigo's anti-fishing invariants exist to prevent.

---

## 3. Issues Persisting From Earlier Documents (carry-forward check)

Not applicable — this is the first review of this spec.

The relevant carry-forward from `project_dev_ai_cost_v2_verdict.md` is the **PAUSED-PENDING-MORE-DATA** verdict and the explicit pivot menu (Option 1 / 2 / 3 at lines 59–63 of that memo). Direction 2 is consistent with **Option 3** (pivot to a different Y where FX-channel hypothesis is empirically stronger ex-ante). The framing is appropriate; Direction 2 does not silently re-run dev_ai_cost_v2's (Y, X).

---

## 4. New Issues Discovered

1. **DIAN data-availability claim inverted** (§2.1) — monthly is public; the plan treats it as escalation. Wastes Day 1.
2. **RUT-size-bracket field assumed to exist in DIAN customs data, but actually requires a RUES join** (§2.2) — load-bearing assumption, unverified.
3. **Centrifuge / Goldfinch EM-trade-finance pool inventory overstated** (§2.3) — the BRL/NGN/IDR/MXN/ZAR list is not backed by current evidence. Goldfinch and Centrifuge are conflated.
4. **Mercado Libre track is structurally optional but operationally entangled** in the Day 3 task (§2.4).
5. **"≥5,000 importers" pass-criterion has no derivation**, no link to a measurable DIAN field, no anchor to the **postal-traffic regime** that almost certainly contains the target cohort (§2.6).
6. **The 5-day budget under-scopes the two-microdata-request worst case** (§2.5) — should plan for ~8-12 weeks wall-clock in worst case, with explicit "parallelize-then-resync" governance.

### Critical (must-fix before gate execution)

- Issue #2 (RUT-size brackets) — kills the pass-criterion unless replaced with a derived-bracket proxy.
- Issue #3 (factor-pool inventory) — kills the small-N pivot story unless re-scoped to a broader cross-protocol pool inventory.

### Medium (should-fix)

- Issue #1 (DIAN monthly availability) — wastes Day 1 if not fixed.
- Issue #5 (pass-criterion derivation) — anti-fishing invariant violation if not fixed.

### Minor (recommend-fix)

- Issue #4 (ML scoping clarity).
- Issue #6 (SLA budget realism).

---

## 5. Specification-vs-Reality Compliance Table

| Spec claim (line) | Reality check verdict | Evidence |
|---|---|---|
| L80: "DIAN customs import declarations — public quarterly aggregates; monthly granularity may require a data request" | **WRONG** — monthly is public default since 2001 | dian.gov.co/dian/cifras EstadisticasComEx; DANE microdatos 473 / 856 |
| L81: "Importer RUT size bracket (DIAN classifies importers; the smallest brackets approximate the micro-cohort)" | **MISLEADING** — DIAN classifies by legal form, not size; size = MINCIT/RUES join | DIAN Cartilla de importación; Decreto 957/2019 |
| L86: "Goldfinch BRL / NGN pools as factor-loading anchors. Public via Centrifuge subgraph" | **WRONG** — Goldfinch ≠ Centrifuge; Goldfinch pools were USDC-denom not BRL/NGN | goldfinch.finance; docs.goldfinch.finance; cryptonewsnavigator.com |
| L98: "Importer count in target RUT-size brackets ≥ 5,000 (cohort relevance)" | **UNMEASURABLE AS STATED** — no public field matches; must define proxy | (negative finding) |
| L99: "At least 3 Centrifuge factor pools (BRL, NGN, IDR, MXN, ZAR) exist" | **UNVERIFIED, LIKELY FALSE** — current Centrifuge pools are US-Treasury / RE / carbon | Bitget Academy 2026; cryptonewsnavigator.com |
| L107: "5 working days (with a 4-6 week wall-clock if DIAN microdata request is filed)" | **CORRECT for primary path, UNDER-SCOPED for RUES-join path** | (compound SLA reasoning) |
| L117: "Mercado Libre seller-cohort access is a partnership ask ... Gate decision should NOT depend on ML access" | **CORRECT** | (consistency with Day 3 task is the only issue) |

---

## 6. Quality Rating (RC honest assessment)

- **Direction value-proposition rating (is the (Y, M, X) candidate worth pursuing?):** B+
  - Strong analog to Numo / Robert's Nigerian product; same wrong-way exposure structure.
  - Direct ratchet-design fit (USD COGS → COP revenue, premium-funded long-gamma).
  - This direction is *substantively the strongest of the four* — it has the clearest mechanical fit to the Abrigo framework (Y, M, X all named, transmission channel explicit, X is well-attested in macro literature, and M maps to a Panoptic position that Numo has demonstrated commercial demand for in NGN).
- **Plan-quality rating (as-written gating plan):** **C+**
  - Three factual misstatements (DIAN monthly availability, Centrifuge/Goldfinch conflation, RUT-size brackets).
  - One unmeasurable pass-criterion.
  - Day-by-day breakdown is plausible *after* the revisions.
  - No anti-fishing pre-pin language for the gate itself (acceptable — it's a feasibility step, not a β estimate — but worth a one-liner that *if Day 4 cohort-size estimation triggers threshold ambiguity, HALT and submit a disposition memo*).

- **Gating step's production-readiness:** **NEEDS WORK** (default). Cannot execute as written without the §2.2 / §2.3 revisions; if those revisions are made, then **CONDITIONAL PASS** to execute.

---

## 7. Required Fixes Before Gate Execution

1. **Rewrite §"Data inputs" item 1** to reflect that DIAN monthly imports are publicly available; reposition the microdata request to the *importer-size-bracket join* (RUES / EAM) path, not the *monthly granularity* path.
2. **Replace the RUT-size-bracket pass-criterion** with a derived-bracket proxy (annual FOB-import-volume quantile from the Directorio de Importadores) plus an explicit fall-back to *postal-traffic regime* counts. State the proxy explicitly as "*not the MINCIT micro-business definition*" to preserve framework honesty.
3. **Audit the factor-pool inventory claim**: replace "Centrifuge BRL/NGN pools" with a current-state inventory across **Centrifuge, Goldfinch, Maple, Credix, Huma, Untangled, Polytrade** (or whichever protocols actually carry active EM trade-finance pools in 2026). Make the *inventory itself* the Day 2 deliverable, and only then derive pass-criteria.
4. **Add a kill-switch**: if Day 2 factor-pool inventory finds <3 active EM trade-finance pools with ≥6-month NAV histories, the gate FAILS on the small-N-pivot leg even if DIAN data is sufficient. This is a logical pass-criterion that the current plan's three-prong PASS test (line 96-99) implicitly contains but doesn't make explicit.
5. **Reword Day 3** to make clear that ML is informational-only, not pass-criterion-relevant.
6. **Add a one-line anti-fishing pin**: "Pass-criterion thresholds (≥75 obs, ≥5K importers proxy, ≥3 factor pools) are *fixed before Day 1*; any post-hoc threshold revision triggers a CORRECTIONS block per `feedback_pathological_halt_anti_fishing_checkpoint.md`."

### Realistic timeline if revisions accepted

- Spec revision: 0.5 day (these are mostly textual / scoping fixes, no new methodology needed).
- Gate execution: 5 working days as planned (with the SLA caveat).
- Wall-clock to gate decision: ~5-12 weeks depending on whether the RUES join is needed.

---

## 8. Re-Assessment Conditions

This RC review should be re-run after the six fixes above are applied. Re-assessment should verify:

- Pass-criteria are anchored to **measurable public fields** with explicit field names and source URLs.
- The factor-pool inventory pass-criterion lists **specific named candidate pools** (not currency tags) and an evidence trail.
- The DIAN data-acquisition tree clearly distinguishes (a) immediately-available monthly aggregates from (b) microdata-request-gated joins.
- The anti-fishing pin is present.

---

## Sources Cited

- DIAN Estadísticas de Comercio Exterior: `https://www.dian.gov.co/dian/cifras/Paginas/EstadisticasComEx.aspx`
- DIAN Datos Abiertos: `https://www.dian.gov.co/atencionciudadano/Paginas/Datos-Abiertos.aspx`
- DANE Importaciones microdatos (2012-2024): `https://microdatos.dane.gov.co/index.php/catalog/473`
- DANE Importaciones microdatos (2025-2026): `https://microdatos.dane.gov.co/index.php/catalog/856`
- Datos Abiertos Colombia — Activos de Información DIAN: `https://www.datos.gov.co/Hacienda-y-Cr-dito-P-blico/Activos-de-Informaci-n-DIAN/3n4a-naej/data`
- DIAN Cartilla de importación: `https://www.dian.gov.co/atencionciudadano/formulariosinstructivos/Formularios/2008/Cartilla_importacion_2008.pdf`
- Decreto 957 / 2019 size-classification summary: `https://contadorespublicossantander.com/?p=11899`
- Bitget Academy — Centrifuge Protocol Guide 2026: `https://www.bitget.com/academy/12560603880584`
- Crypto News Navigator — Centrifuge RWA TVL milestone: `https://www.cryptonewsnavigator.com/academy/article/centrifuge-rwa-infrastructure-tvl-institutional-pivot`
- Centrifuge tinlake-pools-mainnet metadata: `https://github.com/centrifuge/tinlake-pools-mainnet`
- Goldfinch official: `https://www.goldfinch.finance/`
- Goldfinch V1 docs: `https://docs.goldfinch.finance/goldfinch/goldfinch-v1/`
- Goldfinch Crypto Review 2026: `https://westafricatradehub.com/reviews/goldfinch/`
- MINCIT — Cómo importar a Colombia: `https://www.mincit.gov.co/mincomercioexterior/como-importar-a-colombia`
