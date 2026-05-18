# Salvage Path 3 — EOR & Stablecoin-Payroll Firm Partnerships

## Verdict
**CONDITIONAL** — viable only as a 6-12 month parallel track, NOT near-term D1 unblock. No firm currently publishes Colombia-specific monthly panels at D1's required granularity. Cross-tenant aggregate APIs do NOT exist at any firm surveyed.

## EOR firm research-arm publications

| Firm | Research arm | Colombia output | Gating | Cadence | Granularity |
|---|---|---|---|---|---|
| **Deel** | Deel Lab + Deel Works (Lauren Thomas, founding economist) | "Contratación en Latinoamérica" ES blog; State of Global Hiring 2025/26 | Demo-form gated; press free | Annual + ad hoc | Country callouts (CO +49% intl hiring 2025); no monthly panel |
| **Remote.com** | Global Workforce Report | NONE — CO not in survey universe | Gated | Annual | HR-leader survey, not payroll micro |
| **G-P** | World at Work | NONE Colombia-specific (6,000 execs across 6 markets) | Gated | Annual | Exec survey |
| **Multiplier** | None | None | n/a | n/a | n/a |
| **Velocity Global** | Marketing only | None | n/a | n/a | n/a |
| **Oyster HR** | Global Hiring Trends 2025 | CO +43% YoY hires 2023→2024; 14% of Oyster new global hires | Free PDF | Annual | Firm-platform share only |
| **Bitwage** | Blog (content marketing) | "State of Stablecoins in Colombia" Sept-2025 — single post | Free | Ad hoc | Lifetime totals: 90K workers, 4,500 cos, $400M payroll; no CO-only HC |
| **Bitso Business** | "Stablecoin Landscape LatAm" H1-2025 | MX-heavy; CO "catching up"; no CO panel | Free w/email | Semi-annual | 1,300+ institutional clients aggregate |
| **Lemon** | Press releases only | None (entered CO 2025) | n/a | n/a | n/a |
| **Rise (Riseworks)** | "Stablecoin Payroll Report 2025" | LATAM-aggregated; AR/CL/BO called out, CO not | Free landing | Annual | Cross-country aggregates |
| **Mural Pay** | Blog | "Why CO Payroll Platforms Are Shifting to Stablecoin Rails" — narrative | Free | Ad hoc | Quotes Chainalysis 31% stable share CO 2024 |

**Implication**: published outputs are annual snapshots. D1's lag-regression requires unpublished aggregates → partnership ask.

## Academic data-sharing precedent

- **Deel ↔ academic**: weak. Deel Lab has 1 artifact (EU-US DPF). Lauren Thomas joined ~2024; signaled intent to publish via Deel Works; no NBER/SSRN paper under Deel affiliation as of 2026-05.
- **Remote.com**: no precedent, no identifiable chief economist
- **Bitso ↔ academic**: industry reports with consultancies (Asset Servicing Times); no co-authored academic paper
- **Bitwage ↔ academic**: none. Paystand-owned since 2024-2025; blog posts only
- **No firm-side template exists** — closest analogue is WFH Research (Bloom/Davis/Hansen) but their data is from job postings + surveys, NOT EOR platforms. LinkedIn Economic Graph / Indeed Hiring Lab are employee data, not contractor

D1 partnership would be **establishing a first** in the literature.

## API status (cross-tenant aggregate access)

| Firm | Public API | Cross-tenant aggregate endpoint? |
|---|---|---|
| Deel | developer.deel.com, OAuth | **No** — workspace-scoped only |
| Remote.com | HRIS integration | **No** |
| Bitso Business | Institutional payment API | **No** |
| Bitwage | Business payment API | **No** |
| Mural | Stablecoin payment API | **No** |
| Rise | Payroll API | **No** |

**No published SLA** for bespoke data-extraction agreements at any firm.

## Coverage estimate per firm (CO USD-paid remote contractor cohort)

Order-of-magnitude only:

| Firm | Est. share of cohort | Basis |
|---|---|---|
| **Deel** | 15-30% (highest single) | Owns CO entity; CO = 2nd-largest LATAM talent source; $22B/yr global payroll, 35K customers |
| Remote.com | 5-10% | Owns CO entity; smaller LATAM footprint |
| Multiplier / G-P / Velocity / Oyster / RemoFirst | 1-5% each | Smaller global EORs |
| Bitwage | <2% headcount; 5-10% of stablecoin sub-cohort | 90K global ÷ probable CO fraction |
| Bitso Business | Treasury/B2B settler, not direct counterparty | Settles FOR other payroll platforms |
| Mural / Rise | <1% each | Smaller, growing |
| Lemon | Negligible (new in CO 2025) | — |
| **All EORs cooperating** | ~40-60% of formal-EOR-routed cohort | — |

**Critical caveat**: CO USD-paid remote contractor cohort ≈ O(100K-300K). EOR-routed fraction probably <50%; remainder via Payoneer / Wise / Upwork-Payoneer / direct USDC. **No EOR partnership captures the un-platformed half.**

## Partnership model options

### (A) Pro-bono academic collaboration
University signs MOU; firm provides aggregate panel; researcher publishes acknowledging firm; firm gets PR + "data partner" credit. Targets: Deel (has economist, motivated), Bitwage (publishes CO content, low marginal cost), Oyster (shown CO callouts). Time: 3-9 mo outreach→MOU + 1-3 mo delivery. Cost: ~$0 cash, ~40-60 researcher-hours legal, ~20h firm-side aggregation.

### (B) Paid data feed
Custom anonymized extract / dashboard license. Targets: Deel, Bitso Business. Time: 4-10 wk contact→contract + 4-8 wk delivery. Cost: $5K-$50K/yr inferred.

### (C) White-label data-for-analysis exchange ⭐
**Strongest single play.** Abrigo offers β-estimate dashboard showing macro-risk-hedged real-wage path of firm's CO contractors; firm shares underlying panel; co-branded report. Inverts the ask: Abrigo brings scarce analytical capability. Targets: Deel (Thomas would consume/co-author), Bitwage (blog needs content). Time: 6-12 mo. Cost: 100-200 researcher-hours.

## Cost / time estimate per firm

| Firm | Outreach→data | Prob. success | Recommended model |
|---|---|---|---|
| **Deel** | 3-9 mo | 25-35% | (A) or (C) via Lauren Thomas |
| Remote.com | 6-12 mo | ~10% (CO not in survey universe) | (B) only |
| **Bitwage** | 2-5 mo | 30-40% | (A) academic + co-blog |
| Bitso Business | 4-8 mo | 15-25% | (B) paid LATAM feed |
| Oyster | 4-9 mo | 15-20% | (A) or (C) |
| G-P/Multiplier/Velocity | 6-12 mo | <10% each | (B) only |

Best-case single-firm timeline: **4-6 months** (Deel-via-Thomas or Bitwage-via-Paystand). Prob. two firms within 12 mo: ~30%. Prob. ~50% cohort-coverage panel within 12 mo: **<10%**.

## URLs verified

- https://www.deel.com/resources/global-hiring-report-24/
- https://www.deel.com/es/blog/reporte-sobre-la-contratacion-en-latinoamerica/ (CO +49% intl hiring 2025; 1M+ contracts methodology)
- https://www.deel.com/deel-works/meet-our-economist/ (Lauren Thomas)
- https://lab.deel.com/data-eu-us-privacy-framework
- https://developer.deel.com/api/contractors/introduction (workspace-scoped)
- https://remote.com/resources/research/remote-workforce-report (CO not in universe)
- https://www.oysterhr.com/library/2025-global-hiring-trends-and-impact-report
- https://bitwage.com/en-us/blog/state-of-stablecoins-in-colombia---september-2025
- https://business.bitso.com/ebook/stablecoin-landscape-in-latin-america-first-half-2025
- https://www.riseworks.io/blog/stablecoin-payroll-report-2025
- https://www.muralpay.com/blog/why-colombian-payroll-platforms-are-shifting-to-stablecoin-rails

## Recommendation for D1 salvage

1. **Do NOT gate D1 on EOR partnership** — timeline (4-12 mo) and per-firm success probability (<35%) inconsistent with salvage urgency. Parallel medium-term track only.

2. **Weeks 1-4**: scrape every published Colombia number — Bitwage Sept-2025 + Deel ES-LATAM blog + Oyster 2025 + Bitso H1-2025 together yield ~6-8 annual triangulation points. Use as **cross-checks** on Banrep + DANE spine (salvages 01 + 02), not as panel itself.

3. **Months 2-6**: open two parallel outreaches:
   - **Deel Lab / Lauren Thomas** — academic-collaboration framing with concrete paper title + Abrigo Pair-D PASS verdict (β=+0.137, p≈1.5e-08) as carrot
   - **Bitwage research / Paystand** — co-publication; they already publish CO content

4. **Months 6-12**: if (3) yields, expand to Oyster + Bitso Business. Do NOT pay for commercial extracts before exhausting pro-bono.

5. **Hard rule**: any data delivered MUST include firm-written methodology note specifying k-anonymity threshold, denominator, geo/temporal granularity. Uninspectable aggregate denominators violate `feedback_pathological_halt_anti_fishing_checkpoint.md`.

## Outreach contact strategy

**Tier 1 — immediate:**
- **Deel — Lauren Thomas**: LinkedIn DM + general econ@deel.com (verify). Lead: "We have positive β on Colombian USD-paid contractor real-wage path against COP/USD lag; would value co-authored paper using anonymized monthly Deel CO aggregates." Attach Pair-D PASS. Response rate est: 20-30%.
- **Bitwage / Paystand**: blog general contact + Paystand press. Lead: "Follow-up to your Sept-2025 CO post — monthly stablecoin payroll volume by corridor; co-publish wage-stability analysis." Response rate est: 25-35%.

**Tier 2 (if Tier 1 yields signal)**: Bitso Business; Oyster 2025 report author; Rise (Hello@Riseworks.io).

**Tier 3 (last-resort)**: Remote.com (no CO); G-P / Multiplier / Velocity (no research arms).

**Template**: lead with finding, not ask. Position Abrigo as bringing analytical capability. Cite Pair-D. State k-anonymity ≥ 5, no individual data needed. Offer "data partner" credit on publication.

## Privacy / legal (Ley 1581/2012)

GDPR-adjacent. Irreversibly anonymized data outside scope (Recital 26 analogue). k-anonymity ≥ 5 binned salary distributions not personal data. Cross-border to US universities via SCCs. All targets have CO local entities + Habeas-Data-compliant — aggregate releases legally low-friction. **Blocker is firm willingness, not regulation.**

## Gaps

1. No verified email for Lauren Thomas or Bitwage research (LinkedIn/forms only)
2. Un-platformed ~50% of cohort structurally unsolved by EOR path alone — **necessarily complementary to Salvages 01 (Banrep cambiario) + 04 (on-chain)**
3. Deel "currency hopping" headline closest public match; underlying microdata not in press release
4. No prior verified of EOR firm sharing monthly CO panel with academic researcher
5. Back-fill risk: post-delivery-date data useless for retrospective β; 2018-start MUST be specified upfront
6. N_MIN=75 constraint: monthly 2018→2025 = 96 raw; firms with only post-2022 = 36-48 (FAIL N_MIN)
