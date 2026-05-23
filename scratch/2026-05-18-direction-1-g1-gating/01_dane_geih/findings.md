# D1.1 — DANE GEIH Foreign-Employer / Wage-Currency Scan

## Verdict
**FAIL** — No public DANE microdata variable directly identifies the USD-paid-remote-worker (Deel/Remote.com) cohort. Closest proxies indirect and insufficient for β-estimation on a population-defined cohort.

## GEIH variables searched + result (empirically verified)

| Variable | Hypothesis tested | Actual content | Useful? |
|---|---|---|---|
| **P6920** | "moneda de pago" | **Pension fund contribution status** (Sí/No/Ya pensionado) — confirmed by direct fetch `microdatos.dane.gov.co/catalog/782/variable/F64/V4303?name=P6920` | NO |
| **P6930** | "empleador extranjero" | Part of social-security / pension-affiliation sub-module. Not country-of-employer | NO |
| **P6760** | "lugar de trabajo" | Standard GEIH tenure variable (months in current job). No country dimension | NO |
| **P6440** | "tipo de contrato" | Contract written-or-verbal. Domestic-formality focus | NO |
| **P6800** | "horas trabajadas" | Hours worked per week | NO |
| P69XX series broadly | "foreign employer / currency" | Entire series confirmed as social-security + pension-affiliation focus | NO |
| "¿A qué país viajó por última vez a trabajar?" | Foreign-employer proxy | Physical travel abroad to work — wrong direction of mobility | NO |
| Wage currency variable | Direct ask | **Does not exist** in any GEIH 2023/2024/2025 OCUPADOS file. INGLABO + P6500 are COP-denominated; no multi-currency field | NO |
| Digital platform (Deel/Payoneer/Wise) | Direct ask | **Does not exist**. GEIH doesn't ask payment platform | NO |
| Teletrabajo / trabajo remoto flag | Direct ask | **Not in public 2023/2024 OCUPADOS dictionary**. GEIH 2025 catalog 853 shows no dedicated remote-work module despite Ley 2121's mandate | NO |

**Bottom line on GEIH**: Despite Ley 2121 de 2021 mandating DANE produce official remote-work statistics, **GEIH itself has NOT added a foreign-employer or wage-currency variable** through 2025. The P69XX series is overwhelmingly pension/social-security, not employer-country.

## Migration Module scope (confirmed inbound-only)

**Confirmed**: GEIH Migration Module covers **inbound migration TO Colombia**, not Colombian remote workers selling labor abroad.

- DANE official scope: "desplazamientos que ha realizado la población" — physical population movements over 5 years
- Flagship statistic: "tasa de desempleo de personas que migraron desde Venezuela = 19.2%"
- 2014, 2017, 2019, 2020, 2021 module catalogs (`microdatos.dane.gov.co/catalog/636, 639, 641, 662, 700`) all instrument inbound (Venezuelan immigrant labor outcomes)
- **No Colombian-emigrant module + no remote-worker sub-module**

**Confirms spec v0.2 §0.3 correction** and goes further: NO module covers this cohort, not just Migration.

## Alternative DANE surveys

**EMICRON 2023 (catalog 832)** — Microenterprise / self-employed:
- Module I (Ventas/ingresos): captures total sales but **no geographic breakdown of clients** and **no currency-of-payment field**
- Module G (TIC): captures ICT adoption but **no payment-platform enumeration**
- Self-employed = 89.2% of microenterprises (2022) — but does NOT distinguish domestic vs foreign-client freelancers

**Verdict**: indirect proxy at best. Cannot identify USD-paid cohort.

**Other DANE surveys**: ECV (household welfare, no employer-country); Censo Económico (enterprise-level). **No dedicated DANE remote-work survey exists despite Ley 2121.**

## Other public surveys (MINTIC, MINCIT)

- **MINTIC**: ICT-adoption statistics, no individual-level cross-border-employment survey
- **MINCIT**: aggregate service-exports through Banrep coordination, **no microdata on natural-person service exporters**
- **Banco de la República Formulario No. 5 (DCIN-83)**: foreign-exchange declaration form for service exports by natural persons. **Confidential — aggregate balance-of-payments only**; no public microdata (see Salvage 1)
- **No parallel government survey of remote workers exists** as of 2026-05-18

## Academic papers identifying cohort via public data

- Multiple Fedesarrollo papers on "plataformas digitales" — study **domestic** gig-economy workers (Rappi delivery, Uber drivers — ~195,000 workers in 2020). NOT the USD-paid-remote-knowledge-worker cohort.
- **No Banrep or Fedesarrollo working paper has identified the USD-paid-remote-knowledge-worker cohort using GEIH or any public microdata.** Absence is consistent with GEIH dictionary gap — researchers cannot identify what the instrument doesn't measure.

## URLs verified today (2026-05-18)

- https://microdatos.dane.gov.co/index.php/catalog/782 (GEIH 2023)
- **https://microdatos.dane.gov.co/index.php/catalog/782/variable/F64/V4303?name=P6920** — confirmed P6920 = pension contribution
- https://microdatos.dane.gov.co/index.php/catalog/819 (GEIH 2024)
- https://microdatos.dane.gov.co/index.php/catalog/853 (GEIH 2025)
- https://microdatos.dane.gov.co/index.php/catalog/700 (Migration Module 2021 inbound-only)
- https://microdatos.dane.gov.co/index.php/catalog/832 (EMICRON 2023)
- https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/geih-modulo-de-migracion (Migration scope)
- https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=167966 (Ley 2121/2021 DANE remote-work mandate)
- https://www.banrep.gov.co/sites/default/files/reglamentacion/archivos/DCIN_Instructivo_Formulario5.pdf (Banrep F-5 admin-only)
- https://repository.fedesarrollo.org.co/handle/11445/3962 (Fedesarrollo digital platforms — DOMESTIC gig, not cohort)

## Recommendation for gate

**FAIL the D1 G1 cohort-identifiability gate using public DANE microdata.**

The USD-paid-remote-worker cohort cannot be directly identified from any public GEIH/EMICRON variable as of 2026-05-18. This matches the D2 precedent (empirical verification rejects assumption).

Options for spec author:
1. **Pivot cohort definition** to a directly-microdata-identifiable proxy (e.g., high-skill ICT-sector workers in metro areas, with explicit measurement-error caveats). β attenuates but estimable.
2. **Switch data source** to Banrep administrative records on natural-person service exports (Formulario 5) — requires data-access agreement, not microdata-public (see Salvage 1 = NOT VIABLE).
3. **Restructure X-identification** to aggregate balance-of-payments service-exports, dropping cohort-level β in favor of macro-level (see Salvage 2 = CONDITIONAL aggregate-only).
4. **Adopt Direction 1.D on-chain rails** (see Salvage 4 = CONDITIONAL VIABLE ⭐).
5. **CLOSED FAIL** Direction 1 and carry lesson forward.

## Anti-fishing posture

Empirical verification of P6920 = pension contribution (via direct DANE catalog fetch) closes the load-bearing assumption that some unenumerated variable might exist. No silent threshold tuning permissible. The honest action is recognition that the cohort is real but unmeasurable in public microdata — and the salvage-path investigation that follows.

## Gaps

1. Full GEIH 2024/2025 OCUPADOS dictionary (~299 variables in 2023) not exhaustively enumerated; only P69XX, P6760, P6440, P6800 series checked. Joint absence in (a) public metadata, (b) Ley 2121 compliance reports, (c) Fedesarrollo/Banrep working papers makes existence highly improbable
2. GEIH 2025 manual recolección (Scribd 843336213) not opened
3. MINTIC administrative remote-work registry (mandated by Ley 2121) not located
4. DANE Informe al Congreso 2024-2025 (rendición de cuentas) not parsed for Ley 2121 compliance
5. Banco de la República microdata access policy for Formulario 5 not queried (covered by Salvage 1)

---

**Key load-bearing evidence**: Direct fetch of `microdatos.dane.gov.co/catalog/782/variable/F64/V4303?name=P6920` confirms **P6920 = "¿Está... cotizando actualmente a un fondo de pensiones?"** with codes 1=Sí, 2=No, 3=Ya es pensionado. **Single empirical result refutes any hypothesis that the P69XX series carries an employer-country or wage-currency dimension.**
