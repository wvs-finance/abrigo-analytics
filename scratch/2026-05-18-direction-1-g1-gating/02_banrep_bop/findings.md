# D1.2 — Banrep BoP as USD-Wage Proxy

## Verdict
**FAIL** — Banrep BoP cannot serve as monthly aggregate USD-wage proxy for Colombian remote workers. Two independent disqualifications:

1. **Compensation of Employees (CoE)** — the BPM6 line that *should* host such wages — is 2-3 orders of magnitude too small (H1-2025: USD 12M credit / USD 19M debit), because its measured universe is border/seasonal/short-term workers, not Colombian-resident remote workers paid into personal accounts
2. **"Comunicaciones, información e informática"** is firm invoice revenue under BPM6, not wage income (spec v0.2 §0.3 correction confirmed). H1-2025 USD 1,108M; useful as macro context only
3. **Frequency is independently fatal**: BoP is **quarterly**, not monthly. No counterparty-country breakdown for CoE annex

## BPM6 classification confirmed

CoE = labor income to a *resident* worker from a *non-resident* employer, while the worker stays in the home economy. Services exports = firm-resident revenue, regardless of who performed the underlying work.

A Colombian sole proprietor invoicing a US firm and paid into a personal Wise account is recorded — to the extent recorded at all — as services exports if a Colombian exchange intermediary classifies it as such, NOT as CoE. CoE is reserved for the case where the worker remains resident AND the employer-of-record is non-resident, paying compensation directly.

## CoE empirical magnitude (H1-2025)

| Period | CoE credit (USD M) | CoE debit (USD M) | Net (USD M) |
|---|---|---|---|
| H1 2024 | 11 | 22 | -11 |
| H1 2025 | 12 | 19 | -7 |

**Annualized H1-2025 ≈ USD 24M credit.** Compare to:
- Computer-services exports H1-2025: **USD 1,108M** (92× larger)
- Remittances inflows H1-2025: **USD 6,408M** (534× larger)

**No structural break in CoE despite documented Deel/LinkedIn cohort explosion 2020-2026.** Diagnostic evidence: the line doesn't capture the phenomenon. YoY change 2024-H1 → 2025-H1 = +USD 1M = statistical noise.

## Computer-services line as macro context

| Period | Credit USD M | Debit USD M |
|---|---|---|
| H1 2024 | 944 | 864 |
| H1 2025 | 1,108 | 1,000 |
| YoY Δ | +17.4% | +15.6% |

Annualized H1-2025 ≈ USD 2.2B. Not a wage proxy (firm gross export revenue including intermediate inputs, license payments, corporate margins). Useful as **upper-bound sanity check only**: if cohort wage flows existed at salary-survey-implied magnitudes (~75K × $50K = $3.75B), they would have to show up somewhere other than CoE — most likely mis-classified inside remittances.

## Double-counting / contamination with remittances

**BPM6 distinction**: CoE (resident worker, non-resident employer) vs Remittances (migrant transfers from non-resident workers).

**Empirical reality**: Banrep measures remittances primarily through cambiario system (regulated FX intermediaries report inflows classified as "personal transfer"). Critical blind spots:

1. **Colombian-resident remote worker paid in USD into personal Wise/Payoneer/Mercury, then transferred to Colombian bank** = bank tags as personal transfer/remittance (no employer-of-record information). **Cohort wages probably classified as remittances**, not CoE.
2. **Funds that never enter local FX system** (USD kept offshore, converted via P2P/crypto) appear in **neither** line.

Implication: remittances series at USD 6,408M H1-2025 contains the cohort wages but is conflated with genuine migrant transfers from Colombian emigrants in US/Spain. Without microdata-level employer-of-record metadata, **the two cannot be separated**.

**Remittances are unsound as a USD-wage-of-residents proxy.**

## Recommendation for D1 G1 gate

**FAIL** — Banrep BoP cannot supply the monthly aggregate USD-wage panel ≥75 obs that Direction 1 requires. Specifically:

1. CoE: wrong magnitude (2-3 OOM too small), quarterly frequency, no country breakdown
2. Computer-services: wrong concept (firm revenue not wage), quarterly
3. Remittances: contaminated, no separability without microdata

Aggregate USD-wage flow for the Direction-1 cohort is **NOT directly observable** in any Banrep BoP line. Bottom-up construction (GEIH micro × salary surveys) would yield annual aggregates only — not monthly.

## Implications across D1 subtasks

- **01_dane_geih**: FAIL (confirmed) — no microdata variable identifies cohort
- **02_banrep_bop**: FAIL (this finding) — no aggregate proxy at required frequency
- **03_salary_surveys**: CONDITIONAL PASS for wage levels; insufficient for monthly panel
- **04_cohort_triangulation**: PASS for existence + size; insufficient for monthly panel

**Net D1 G1 composite verdict: structural FAIL at the panel-construction gate.** Cohort exists and is large/growing, but not measurable at monthly frequency on public data.

Possible salvages (all out of public-data-only scope per user direction):
- Banrep Sistema de Información Cambiaria (microdata, restricted access)
- DIAN administrative records on natural-person service-exporter declarations
- Direct data partnership with Deel / Remote.com / Bitwage

## URLs

- BoP main page: https://www.banrep.gov.co/en/balance-payments
- BoP metadata summary: https://www.banrep.gov.co/sites/default/files/paginas/Colombia%20Balance%20of%20Payments%20Metadata%20summary.pdf
- Latest BoP report (Q2-2025): https://www.banrep.gov.co/sites/default/files/informeBOP202502.pdf
- Remittances suameca series: https://suameca.banrep.gov.co/estadisticas-economicas/informacionSerie/4150/remesas_trabajadores/
- Remittances methodology (Reportes Emisor 71): https://www.banrep.gov.co/es/las-remesas-trabajadores-y-las-compras-cambistas-profesionales-balanza-pagos-colombia
- Borradores comercio exterior servicios 1994-2024: https://www.banrep.gov.co/es/publicaciones-investigaciones/borradores-economia/comercio-exterior-servicios-colombia
- IMF SDDS DQAF Colombia BoP: https://dsbb.imf.org/sdds/dqaf-base/country/COL/category/BOP00

## Gaps

1. Full 2018-Q1 → 2025-Q4 quarterly CoE vintage not pulled (totoro/suameca in maintenance); retry via IMF BOPS / IFS code BXIPCO
2. Borradores "Comercio exterior de servicios" full PDF not extracted (labor-share inside computer-services exports would tighten upper-bound)
3. Reportes Emisor 71 methodological detail on cambiario classification not deep-read
4. Sistema de Información Cambiaria (Banrep micro) — could in principle yield monthly resident-remote-worker wage estimates; access conditions unknown, restricted

---

**Key finding for D1 G1 consolidation**: Both the conceptual line for cross-border wages (CoE) AND the previously-mis-claimed line (computer services) are unsuitable as monthly aggregates. Cohort wages most likely mis-classified inside remittances (USD 6,408M H1-2025) but cannot be separated from genuine migrant transfers without microdata. Direction-1 Y must be built bottom-up from GEIH + salary surveys (annual aggregates only) — does not satisfy spec's monthly N≥75 requirement.
