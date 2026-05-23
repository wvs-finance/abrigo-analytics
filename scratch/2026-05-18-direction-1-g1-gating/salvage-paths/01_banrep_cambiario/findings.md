# Salvage Path 1 — Banrep Sistema de Información Cambiaria

## Verdict
**NOT VIABLE** as standalone D1 panel-construction source. **CONDITIONAL** as supplementary aggregate validation layer (treat as censored lower bound on flows passing through IMCs, never as population denominator).

## Three structural blockers (any one suffices)

1. **Voluntary canalization** — Banrep's 2017 régimen-cambiario reference: "Los servicios son operaciones del mercado libre o no regulado; por tanto, su canalización en el mercado cambiario, es voluntaria" (`ce_dcin_2017.txt` p. 49). Borradores 1351 (2026): cambiario records "no brindan una cobertura completa al no ser operaciones de obligatoria canalización" (p. 44). **D1 cohort overwhelmingly keeps USD in Wise/Payoneer/USDC and never touches SIC.**

2. **Reserva estadística under Ley 31/1992 art. 51** — no published academic-access pathway exists for IMC microdata. Eslava-style precedent (Banrep-DIAN convenio) covers F-530 customs goods data, NOT cambiario services data.

3. **No natural-person disaggregation in public aggregates** — suameca portal publishes "balanza cambiaria" at broad-bucket level; per-numeral monthly series and CC-vs-NIT ID-type split captured in microdata but not released publicly.

**Even maximum-optimistic microdata access wouldn't help** — voluntary-canalization censoring is the binding constraint, and it's **non-random**: the more crypto-native / offshore-retaining cohort is systematically MORE likely to be missing.

## DCIP-83 (DCIN-83) regulatory framework

Current: **Circular DCIP-83** (renamed from DCIN-83 Sept 2021). Last material update Boletín 43/2025 (Dec 16, 2025).

Hierarchy: Ley 9/1991 (régimen marco) → Ley 31/1992 art. 51 (confidencialidad) → Resolución Externa 1/2018 JDBR → Circular DCIP-83 (10 capítulos + 4 anexos)

**Chapter 10** = services/transfers (Formulario 5). **Anexo 1** = numerales catalog.

**Formulario 5 fields**: ID type (CC/CE/NIT/PB/RC distinguishes natural vs legal); moneda + valor + tipo de cambio + valor USD; numeral cambiario; país origen/destino. No CIIU field on F-5 itself.

**Who files**: IMC generates declaration with resident's data when operation is channeled.

**Threshold**: No across-the-board USD threshold for services. **Penalty**: 25-100% of misreported sum on MANDATORY-canalization operations only. **Services canalization is voluntary → non-filing has no sanction exposure** — structural reason for cohort underreporting.

## Numerales cambiarios for natural-person service exports

| Numeral | Side | Description | D1 fit |
|---|---|---|---|
| **1840** | Ingreso | **Servicios empresariales, profesionales y técnicos** ("Consultoría... informática y científica; Desarrollo, diseño y puesta a punto de software; honorarios") | **Canonical** for contractor cohort |
| 2906 | Egreso | Mirror of 1840 | |
| 1809 | Ingreso | Remesas de trabajadores ("colombianos en el exterior") | Wrong (cohort is RESIDENT IN CO) |
| 1810 | Ingreso | Donaciones y transferencias sin contraprestación | Conceptually wrong but plausible mis-coding |
| 1813 | Ingreso | Remesas PN colombianas no residentes → cuentas trámite simplificado | Low-income remittance (2011 addition) |
| **1814** | Ingreso | Compra divisas para cuentas dispersión remesas | Added Dec-2025 (Boletín 43/2025) — NEW remittance infra, NOT services |
| 1706 | Ingreso | Viajes negocios, pagos laborales a residentes, seguridad social | Alternative if W-2-equivalent; mixed bucket |
| 1602 | Ingreso | Pago exportación servicios vía PSP agregadores | Narrow PSP scope |

**Critical taxonomic point**: same USD inflow can be coded {1840, 1706, 1810} depending on IMC clerk discretion. Even with microdata, aggregate series for D1 substance would be noisy across these 3 buckets.

## Access pathways

| Pathway | Status |
|---|---|
| Public aggregates (balanza cambiaria, suameca) | OPEN — bucket-level only |
| BoP services exports (quarterly MECIS 2010 categories) | OPEN |
| Datos transversales (códigos referencia) | OPEN — codes only |
| **SIC Formulario-5 microdata** | **RESTRICTED — Ley 31/1992 art. 51** |
| DANE MTCES/EMCES microdata | OPEN with anonymization — **NIT-only universe** (excludes natural-person freelancers) |
| Banrep-DIAN-DANE convenio | Exists for goods customs + MTCES; NOT extended to external academics for cambiario |

**No academic pathway** to Formulario-5 microdata documented in any public source.

## Granularity + frequency

| Series | Granularity | Frequency | Period |
|---|---|---|---|
| Balanza cambiaria agregada | National | Weekly | 2001-09+ |
| Balanza cambiaria — "servicios" bucket | Broad bucket | Weekly/monthly | 2001-09+ |
| Balanza cambiaria por numeral 1840 | Per-numeral | **NOT openly published** | — |
| BoP servicios | 12 MECIS categories | Quarterly | 1994+ |
| MTCES/EMCES (DANE) | CPC × modo × país | Trimestral → Mensual (2023+) | 2013+ |
| SIC microdata (theoretical) | Per-transaction | Per-transaction | 2001+ |

D1 wanted monthly individual-level panel; gap to best obtainable = ~3 orders of magnitude.

## Cohort coverage estimate

Voluntary-canalization leak — D1 cohort can:
- Hold USD offshore indefinitely → **0% cambiario footprint**
- Spend via Wise debit card on COP merchants → 0% (merchant sees COP)
- P2P USDC → COP via informal markets → 0%
- Convert via IMC-channeled COP withdrawal → IMC declares under whatever resident self-declares (often 1810 or unreported)

**Order-of-magnitude**: BoP "otros servicios empresariales" ~USD 1.5-2B/yr (2019, per be_1351). Cohort wages (triangulated) ~USD 1.5-3B/yr. **Implied D1 coverage by numeral 1840: optimistic 30-50%, realistic 10-20%.** Censoring non-random + biased AWAY from most-relevant sub-cohort.

## Academic precedent

| Paper | Used cambiario microdata? | Notes |
|---|---|---|
| Eslava et al. "Import market in Colombia" | **No** — DIAN F-530 customs (goods) | Convenio with DIAN, not Banrep SIC |
| Camacho-Marín & Andrade-Bohórquez 2026 (be_1351) | Mentions cambiario only as "contraste, validación, complemento" | Explicitly acknowledges incomplete coverage |
| Banrep "Doc técnico revisión BoP servicios" | Internal — combines MTCES + cambiario + surveys | Reconciliation algorithm undisclosed |

**No paper uses Formulario-5 microdata at natural-person level.** Consistent with Ley 31/1992 + no external pathway.

## URLs verified

- https://www.banrep.gov.co/es/regulacion-operaciones-cambiarias-dcip-83 (DCIP-83 index)
- https://www.banrep.gov.co/sites/default/files/reglamentacion/archivos/dcip-83-compendio-anexo1.pdf (Anexo 1 numerales)
- https://www.banrep.gov.co/sites/default/files/reglamentacion/archivos/DCIN_Instructivo_Formulario5.pdf (F-5 instructivo)
- https://www.banrep.gov.co/sites/default/files/publicaciones/archivos/ce_dcin_2017.pdf (régimen cambiario 2017, **p.49 canonical "voluntaria"**)
- https://repositorio.banrep.gov.co/bitstream/handle/20.500.12134/11367/be_1351.pdf (Borradores 1351 2026, **p.44 coverage-gap acknowledgement**)
- https://suameca.banrep.gov.co/estadisticas-economicas/informacionSerie/4230/balanza_cambiaria (bucket-level)
- https://microdatos.dane.gov.co/index.php/catalog/820 (MTCES 2013-2022 NIT-only)

## Cost / SLA estimate

- Public aggregates: USD 0, instant
- DANE MTCES microdata: USD 0, ~1 week (but NIT-only is limiting)
- SIC Formulario-5 microdata: **6-18 months wall-clock**, low approval probability. Direct derecho de petición almost certainly denied citing Ley 31/1992.

**For D1 gate that needs to close: timeline effectively infinite.**

## Recommendation for D1 salvage

1. **De-prioritize cambiario microdata** to "secondary validation" only
2. **Use public BoP services series** (quarterly MECIS) as aggregate-level boundary check
3. **If numeral-1840 monthly series can be pulled from suameca at bucket level** (next-step verification), use as **lower-bound proxy** for non-offshore-retaining D1 flows. Test whether 1840 ~ USD/COP — if weak, reinforces D1.3 finding (offshore-retention dominates)
4. **STOP pursuing Formulario-5 microdata.** Opportunity cost vs paths 02/03/04 too high
5. **Memorialize the structural-censoring finding** as methodological contribution: any Colombia-official-source-only D1 study under-counts the most relevant sub-cohort

## Gaps

1. Did NOT verify whether numeral 1840 is published as separate monthly series at suameca catalog level (JS-rendered nav). Direct portal scrape from notebook is next step
2. Did NOT confirm whether Banrep has 2025+ plans to integrate fintech-rail data (Wise/Payoneer CO, SEDPE flows) into SIC. Boletín 43/2025 added only remittance-dispersal infra
3. Did NOT precisely quantify D1 cohort share through IMCs vs offshore. 10-50% bracket triangulated from MTCES vs cohort-size estimates. **Direct cohort survey (N≥100, "channel through IMC or keep offshore?")** would resolve better than any admin source
4. Did NOT exhaust salvage path 02 — specifically **Form 1647** (reporte de cuentas en el exterior) — which approaches the cohort from the OTHER side (residents who DO declare offshore Wise/Payoneer balances). Should be next salvage path; likely dominates this one
