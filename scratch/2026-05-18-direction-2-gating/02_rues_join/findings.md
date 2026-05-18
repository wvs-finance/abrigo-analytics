# D2.2 — RUES × DIAN NIT-Join Feasibility

**Verdict:** CONDITIONAL PASS — operationally feasible for legal-entity importers; natural-person importers dropped by DIAN policy.

## Decreto 957/2019 size thresholds (UVT, sector-dependent)

| Sector | Micro (≤) | Pequeña (rango) | Mediana (rango) | Grande (>) |
|---|---|---|---|---|
| Manufactura | 23,563 UVT | (23,563, 204,995] | (204,995, 1,736,565] | >1,736,565 |
| Servicios | 32,988 UVT | (32,988, 131,951] | (131,951, 483,034] | >483,034 |
| Comercio | 44,769 UVT | (44,769, 431,196] | (431,196, 2,160,692] | >2,160,692 |

Single criterion = `ingresos por actividades ordinarias anuales` (Decreto 957/2019 replaced earlier headcount+assets criteria). Mixed-activity firms default to manufactura thresholds (Art. 2.2.1.13.2.2). UVT 2024=COP 47,065 / UVT 2025=COP 49,799 — UVT 2026 must be confirmed against DIAN annual resolución.

**Reference (target cohort):** micro-importer commerce-sector ceiling ≈ COP 2,200M revenue/year ≈ USD 530K at TRM 4,200.

## RUES public surfaces

| Surface | Fields exposed | Joinable bulk? |
|---|---|---|
| `rues.confecamaras.co` single-NIT (public, free) | razón social, NIT, matrícula, estado, dirección, rep legal, CIIU, fecha matrícula | No — single-NIT card only |
| `www.rues.org.co` advanced consulta (login) | Filterable by tipo organización, depto, municipio, sector, CIIU, **tamaño** (4 legacy SMLV bands) | CSV/TXT export per 2025 CCC user manual — **unverified live** |
| `datos.gov.co/c82u-588k` Socrata API (anonymous, free) | 21 fields: NIT, DV, razón social, CIIU3/4, fecha_matricula, fecha_renovacion, estado_matricula, tipo_sociedad, organizacion_juridica, sigla, rep_legal | **No tamaño, no ingresos** |

**Critical unknown:** RUES advanced-consulta CSV export — does it actually include `tamaño` column? Documented in 2025 CCC manual but not live-tested. **Single item that flips CONDITIONAL → PASS or FAIL.**

## NIT join feasibility

- **Legal-entity importers:** YES via NIT match
  - DIAN datos.gov.co Form 500 weekly (`fan6-7ztf` — researcher precedent: Banrep Eslava et al.) → filter `nit != 0`
  - Join NIT → RUES `c82u-588k` Socrata for CIIU + estado_matricula (free)
  - Pull tamaño via RUES advanced-consulta export OR per-NIT scrape fallback (~50K requests/yr legal-entity importers, rate-limited)
- **Natural-person importers:** NO — DIAN recategorizes NIT to `0` and razón social to `PERSONA NATURAL` per Ley 1581/2012. **Cohort by construction = legal-entity micro-importers only.** Quantify the natural-person exclusion magnitude upfront.

## Alternative size-classification proxies (if RUES advanced-consulta fails)

| Proxy | Joinable to DIAN at NIT? | Cost | Verdict |
|---|---|---|---|
| DANE IMPO 2012-2024 anonymized firm-id | Anonymized only — no NIT | Free | Independent sanity check |
| DANE IMPO 2025-2026 | Firm dim **removed** | Free | Breakage point: 2025+ DANE drops firm |
| DANE EMC | No (sample survey) | Free | Macro reference |
| MINCIT Tejido Empresarial | No (aggregates) | Free | Denominator validation |
| Bancóldex SME registry | No public | n/a | **Descoped** (public-only) |
| Confecámaras Dinámica Empresarial | No (PDF aggregates) | Free | Macro reference |
| DANE EAM | Researcher-restricted | Restricted | **Descoped** |

## Pipeline (recommended)

1. Anchor on DIAN datos.gov.co Form 500 weekly (re-locate live slug)
2. Filter `nit != 0` (legal entities); count natural-person exclusion
3. Join NIT → RUES `c82u-588k` Socrata for CIIU + estado_matricula → derive macro-sector (Manuf 10-33 / Comercio 45-47 / Servicios 49-96 per CIIU rev4)
4. Pull size band via RUES advanced-consulta CSV (if column present) OR per-NIT scrape fallback
5. Apply Decreto-957 UVT thresholds → micro/pequeña/mediana/grande classification
6. Reconcile against MINCIT Tejido Empresarial aggregates

**Pre-register the truncation** in disposition memo BEFORE downloading: cohort = "legal-entity micro-importers per RUES self-reported tamaño, excluding natural persons and stale/absent matrículas." Per anti-fishing, cohort-definition tuning after seeing β is silent-fishing.

## URLs verified

- https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=94550 (Decreto 957/2019)
- https://www.rues.org.co/ (RUES portal)
- https://www.datos.gov.co/resource/c82u-588k.json (Confecámaras RUES Socrata)
- https://www.dian.gov.co/atencionciudadano/Paginas/Datos-Abiertos.aspx
- https://www.banrep.gov.co/en/import-market-colombia-and-firms-import (Banrep firm-level imports paper — research precedent)
- https://www.ccc.org.co/wp-content/uploads/2025/01/Manual-de-usuario-RUES-Consulta-beneficio-a-empresarios_2025.pdf (RUES advanced-consulta manual)

## Risks / unverified

1. RUES advanced-consulta CSV `tamaño` column presence — load-bearing unknown
2. DIAN Form 500 slug `fan6-7ztf` 404 today — re-locate
3. UVT 2026 COP value — pending DIAN resolución
4. SMLV-band → UVT-band crosswalk approximate
5. `c82u-588k` Socrata last-refresh — verify `:updated_at` metadata
6. Natural-person truncation permanent under Ley 1581/2012 — cohort labeled accordingly
7. Tamaño self-reported + stale-renewed — expect 5-15% missing/wrong size flags
8. DANE 2025+ removed firm dim — historical Banrep panel can't be extended past 2024 via DANE alone; DIAN datos.gov.co only forward firm-keyed source
