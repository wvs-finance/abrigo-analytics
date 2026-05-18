# Salvage Path 2 — DIAN Administrative Records

## Verdict
**CONDITIONAL — VIABLE ONLY AT AGGREGATE GRANULARITY.** Useful as a *validation layer* + *sector-level fallback Y*, not as standalone D1 G1 backbone.

## Three structural blockers vs standalone use

1. **No public microdata at individual-declaration level.** Art. 583 ET (reserva tributaria) is strict and has NO investigator-access pathway analogous to DANE's anonymized microdata. Concepto DIAN 16779/2025 reaffirmed reserva even inside judicial expedients.
2. **"Exportador de servicios" flag not separately tabulated** in published aggregates. CIIU axis reaches service-sector codes (J/M/K) but does NOT separate USD-denominated revenue from peso revenue inside those codes.
3. **Cohort coverage gap structural and large.** DIAN only sees filers crossing ~1,400 UVT renta threshold (~COP 65M/yr) who actually registered RUT. Lower-paid USD freelancers, USDC-rail recipients, non-declarers invisible. **>50% of cohort likely invisible to DIAN.**

## DIAN open-data catalog

| Series | Granularity | Years | Format |
|---|---|---|---|
| Agregados Renta Personas Naturales | CIIU × income-quantile × asset-quantile | 2014-2024 | Excel/zip |
| Agregados Renta Personas Jurídicas | Same | 2014-2024 | Excel |
| Agregados IVA | CIIU + seccional | Multi-year | Excel |
| Agregados GMF/Patrimonio/Consumo/Retención | Cell aggregates | Multi-year | Excel |
| Recaudo mensual | Tax × seccional | 2000-2019 | CSV (datos.gov.co) |
| Directorio Importadores/Exportadores | Goods only (no services) | 2017+ | Lookup |

**Not in public DIAN data**: individual renta declarations; "exportador de servicios" flag in aggregates; foreign-currency income separately; cross-walk RUT-exporter↔renta filings.

## Formulario 210 + RUT exposure

Cohort-relevant fields:
- Casilla 32 = ingresos brutos rentas de trabajo (wages + honorarios)
- Casilla 43+ = rentas no laborales (where contractor/service-export USD revenue is booked)
- CIIU principal (RUT-derived): J62/J63 (IT services), M70/M71/M74 (consulting), K (finance)

**Public exposure**: aggregated by CIIU × quantile yes; individual fields no. Art. 583 ET applies. D2 precedent (DANE strips NIT) does NOT transfer — DIAN releases no individual microdata at all, anonymized or otherwise.

**MUISCA RUT consulta pública** (`muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces`): free, no-auth, 24/7. Returns state, name, CIIU, responsabilidades fiscales. Responsabilidad code 10 = "exportador"; boxes 55-58 specify modalidad. **One-NIT-at-a-time only** — no bulk export, scraping violates ToS + Ley 1581.

## Art. 481 ET IVA-exempt exporter registry

Art. 481 lit. c exempts services rendered in Colombia and used exclusively abroad by non-residents. Filer must register RUT responsabilidad 10 + activate boxes 55-58 + comply with facturación electrónica (Conceptos DIAN 8660/2024 + 5846/2024).

**Public visibility**: per-NIT lookup yes; aggregate registry NOT published. CIIU × quantile renta mixes exporters with domestic-revenue independents in same CIIU code.

**Important**: many USD-paid remote workers do NOT register as Art. 481 exporters because (a) registration triggers facturación-electrónica obligations they avoid, (b) the exemption is on IVA not income tax, (c) services billed abroad face no IVA from foreign payer anyway. **Art. 481 registry is a LOWER BOUND on the cohort.**

## Régimen Simple de Tributación

Régimen Simple (Ley 1943/2018 → 2010/2019 → 2155/2021 → 2277/2022) lets naturales below ~80,000 UVT brutos opt into unified 1.6%-14.5% rate. Many USD freelancers use it.

**Public data**: agregados include Régimen Simple as separate series 2019-2024; granularity = total declarantes, recaudo by CIIU bracket.

**Critical limitation**: Régimen Simple has NO "exportador" flag in its form. USD-paid freelancer under Simple is observationally identical to peso-paid freelancer with same CIIU.

## Cohort coverage gap (informal vs filed)

Filters excluding cohort members from DIAN aggregates:

1. **Filing threshold**: ingresos brutos ≥ 1,400 UVT (~COP 65M, 2024) or patrimonio ≥ 4,500 UVT triggers declaración renta. Below = invisible.
2. **E-invoicing threshold**: ≥ 3,500 UVT (~COP 165M) triggers e-invoicing. Below, many freelancers operate cash/transfer without invoices.
3. **RUT registration**: presupposes filing. USD-paid via Wise/Payoneer/USDC into personal accounts often skip.
4. **Crypto rails**: USDC never touches cambiario, often skips RUT — likely highest informality fraction.

Quantitative anchors:
- Mincit/El Colombiano 2024: international transfers via Wise/Payoneer-like rails ≈ USD 8.68B Jan-Sep 2024 (+17.2% YoY). Mix of remittances and remote-work income.
- DANE 2025: ~2.8M independent/freelance workers nationally.
- ILO 2025 LAC platform-workers report: 4% of LAC workforce = main-job platform worker → O(0.5-1M) Colombia.

**Informal-to-formal ratio likely >50%** — selection bias for any DIAN-based Y measure.

## Academic precedent (microdata access pathway)

- **Londoño-Vélez and Ávila-Mahecha** (2018-2023): wealth inequality, audit responses, offshore-tax behavior — DIAN-supplied administrative microdata via formal data-use agreement. Non-redistributable.
- **Alvaredo and Londoño-Vélez** top-incomes literature.
- **Fedesarrollo / Comisión de Expertos** tax-equity work — bilateral cooperation, not public microdata.

**Microdata access timeline**: months. Output: non-redistributable; publication of aggregate results only.

## URLs verified

- https://www.dian.gov.co/dian/cifras/Paginas/TributosDIAN.aspx
- https://www.dian.gov.co/atencionciudadano/Paginas/Datos-Abiertos.aspx
- https://muisca.dian.gov.co/WebRutMuisca/DefConsultaEstadoRUT.faces
- https://www.dian.gov.co/atencionciudadano/formulariosinstructivos/Formularios/2025/Formulario_210_2025.pdf
- https://www.datos.gov.co/stories/s/DECLARACION-DE-RENTA-PERSONAS-NATURALES/n2jp-53s2/
- https://normograma.dian.gov.co/dian/compilacion/docs/oficio_dian_16779_2025.htm (Concepto 16779/2025 reserva)
- https://www.dian.gov.co/Contribuyentes-Plus/Documents/7-CONCEPTO-008660-int-987-08112024.pdf (Concepto 8660/2024 Art. 481)
- https://www.banrep.gov.co/es/numerales-cambiarios (cross-ref Salvage 1)

## Recommendation for D1 salvage

**Do NOT promote DIAN to standalone D1 G1 backbone.** Use in two bounded roles:

### Role 1 — Population-frame validation layer
Use renta agregados by CIIU (J62/J63/M70/M71/M74) × quantile to anchor magnitudes and pin external-validity ceiling: D1 results generalize at most to top-N% of cohort that files renta. Make ceiling an explicit pre-registered scope condition.

### Role 2 — Sector-level differential as fallback Y
If Banrep cambiario also fails (Salvage 1) AND EOR/on-chain infeasible (Salvages 3/4), redefine Y at CIIU level: e.g., YoY ingresos brutos in J62 (IT services) vs J47 (retail) deflated by sector CPI, with COP/USD as X. **Collapses the cohort question to a sector question; (Y,M,X) framing shifts (M targets sectoral index, not individual hedge); inequality-transmission story weakens.**

### Stronger composite recommendation
Combine DIAN aggregates with Banrep cambiario service-export numerales (Salvage 1) + Mincit/Procolombia services-export tables. Triangulate at sector level. Salvageable but **a different question** than original D1.

### Out-of-scope path (formal microdata access)
DIAN bilateral agreement à la Londoño-Vélez. Months timeline; non-redistributable output — violates open-data tier of Abrigo reproducibility model.

## Gaps

1. datos.gov.co n2jp-53s2 content not directly read (portal chrome only); .xlsx files live on dian.gov.co/cifras
2. Régimen Simple agregado .xlsx column structure not verified
3. Banrep cambiario × DIAN renta gap not quantified
4. DIAN academic-microdata-use agreement procedure not publicly documented (template not located)
5. Coverage-gap quantification for USD-paid remote-worker informality has no single authoritative source
