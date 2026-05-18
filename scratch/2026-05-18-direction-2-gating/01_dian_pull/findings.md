# D2.1 — DIAN / DANE Customs Data Availability

**Verdict:** CONDITIONAL PASS
- **Aggregate panel (HS-10 × origin × month, no firm-ID): UNCONDITIONAL PASS** — N≈100 months 2018-01→2026-04
- **Firm-level (NIT) join via DANE public download: BLOCKED** (NIT field suppressed in actual file — empirically confirmed)
- **Firm-level via DIAN datos.gov.co Form 500 weekly: CONDITIONAL** (slug `fan6-7ztf`; researcher-accessible per Banrep precedent)

## Empirical NIT-suppression test (run 2026-05-18)

Downloaded DANE catalog 473 zip (download/24390, 597 MB) containing Aug-Dec 2024 monthly imports. Extracted `Agosto 2024/Agosto.csv` and counted fields:

- **41 fields actual**, vs 44 documented in data dictionary
- Field 41 = DEREL (last); **NIT, DigV, RZIMPO are ABSENT from the public file**
- Field 22 = **CLASE** (clase de importador) — DIAN-internal crude size proxy present
- Schema includes: FECH, ADUA, PAISGEN, PAISPRO, PAISCOM, DEPTODES, VIATRANS, BANDERA, REGIMEN, ACUERDO, PBK, PNK, CANU, CODA, **NABAN (HS10)**, **VAFODO (FOB USD)**, FLETE, **VACID (CIF USD)**, **VACIP (CIF COP)**, IMP1 (IVA), OTDER, CLASE, CUIDAIMP, CUIDAEXP, ACTECON (CIIU), CODADAD, VADUA, VRAJUS, BASEIVA, OTROSP, OTROSBASE, TOTALIVAYO, SEGUROS, OTROSG, LUIN, CODLUIN, DEPIM, COPAEX, TIPOIM, PORARA, DEREL

**Confirms** the DIAN press statement (`https://www.dian.gov.co/dian/cifras/Documents/Preguntas-y-respuestas-del-webinar-tablero-COMEX.pdf`): "por reserva estadística, no se publica información correspondiente a la identificación de importadores tales como NIT y razón social."

**Resolves** the load-bearing CONDITIONAL flagged in the agent review: public DANE microdata download does NOT carry NIT. The conflicting DANE methodology fragment was incorrect.

## Aggregate panel availability

- DANE catalog 473 (2012-2024): instant-download monthly zips, semicolon-delimited CSV + .dta + .sav
- DANE catalog 856 (2025-2026): same schema, certified through Feb-2026
- DANE catalog 184 (2008-2011): historical extension
- No COVID gap; continuous monthly series 2008→2026
- HS disaggregation: **10-digit NANDINA** (full subpartida nacional) via NABAN field
- Values: VAFODO (FOB USD), VACID (CIF USD), VACIP (CIF COP)
- Co-variables: PAISGEN/PAISPRO/PAISCOM (origin/procedencia/compra), ACTECON (CIIU), DEPIM (importer dept), CLASE (size proxy)

## Firm-level workaround paths

1. **DIAN datos.gov.co Form 500 weekly** (`fan6-7ztf` slug, Hacienda y Crédito Público) — natural-person NITs masked to `0`, legal-entity NIT exposed. **Researcher precedent**: Banrep "The import market in Colombia and the firms that import" (Eslava et al.) used this source.
2. **DIAN directorio de importadores** (separate annual ZIPs 2017-2026) — carries NIT + razón social as firm-attribute sidecar. Joinable to RUES (see D2.2).
3. **DANE Banco de Datos custom microdata request** — restricted-access pathway; cost/SLA not published. Out of public-data-only scope per user direction.

## URLs verified today (2026-05-18)

- https://www.dian.gov.co/dian/cifras/Paginas/EstadisticasComEx.aspx
- https://importaciones.dian.gov.co/ (tablero BI)
- https://microdatos.dane.gov.co/index.php/catalog/473 (2012-2024)
- https://microdatos.dane.gov.co/index.php/catalog/856 (2025-2026)
- https://microdatos.dane.gov.co/index.php/catalog/184 (2008-2011)
- https://muisca.dian.gov.co/WebArancel/DefMenuConsultas.faces (HS arancel lookup)
- https://www.datos.gov.co/Hacienda-y-Cr-dito-P-blico/Declaraciones-de-Importaci-n-Formulario-500-Semana/fan6-7ztf (referenced; 404 on direct fetch today — re-verify slug)

## Recommended HS-chapter scope

**Primary basket** (e-commerce micro-importer): HS 85 (electronics), HS 61 (knit apparel), HS 62 (non-knit apparel), HS 42 (leather), HS 94 (furniture/lighting).
**Secondary** (sensitivity): HS 64 (footwear), HS 95 (toys), HS 71 (jewelry), HS 39 (plastics), HS 90 (optics).
**Out of scope**: HS 27, 87, 30, 84 (corporate-importer dominated).

## Bottom line for gate

- HS × origin × month aggregate panel: instant, free, ~100 months → **PASS unconditional**
- Firm-level join: route via DIAN datos.gov.co Form 500 (legal entities only) + DIAN directorio sidecar → RUES bracket join. NIT-via-DANE-microdata path: **closed**.
- Recommendation: run β-existence test on aggregate panel first (CLAUDE.md stage-drift discipline); escalate to firm-level only if aggregate PASS.

## Gaps
- DIAN Form 500 datos.gov.co slug returned 404 — re-locate before pipeline build
- Banco de Datos custom-request cost/SLA unknown (descoped anyway)
- HS code drift across 2018-2026 from 2024/2025 arancel modifications — handle by aggregating to HS6/HS8 for time-series stability
