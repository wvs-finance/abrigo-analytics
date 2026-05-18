# D2.4 — Colombian Tariff + VAT Step-Function Panel 2018-2026

**Verdict:** PASS — panel constructible from public legal sources at HS-chapter granularity. Every step grounded in a public *decreto* / *ley* / *resolución*.

## Headline events (most material for target HS chapters)

| Year | Event | Affected HS | Magnitude | Source |
|---|---|---|---|---|
| 2017-Feb | **Ley 1819/2016** | All | IVA general 16% → **19%** | Pre-window baseline |
| 2020-Mar | **Decreto 410/2020** | 28-30, 38-40, 48, 56, 61(PPE), 63, 84, 85(med), 88, 90, 94(hosp.) | NMF → 0% × 6m (COVID) | suin-juriscol 30038950 |
| 2021-Apr | **Decreto 414/2021** | **61, 62** (apparel) | NMF → arancel mixto (40% if FOB ≤ USD 10/kg; 15% + USD 1.50/kg otherwise) | Major step-up |
| 2022-Dec-23 | **Decreto 2598/2022** | **61, 62** | Derogates 414 → **flat 40% NMF** all FOB; TLC exempted | DIAN normograma 2598/2022 |
| 2022-Dec | **Ley 2277/2022** (Reforma Petro) | Hotelería 0%→19%; tiquetes aéreos 5%→19%; bracket re-classifications | General 19% retained | Función Pública 199883 |
| 2025-Feb-27 | Decreto 0214/2025 | Chap 52-64 | Threshold prices updated (US CPI 2018-2023); enforcement floor — does NOT change MFN rate | MINCIT |
| 2025-Nov-08 | Decreto 1184/2025 | 37 inputs textil + calzado | NMF → 0% × 2 years (input-side) | Presidencia + INCP |
| 2026 effective | Reforma Tributaria 2025 | Postal de minimis | **USD 200 → USD 50** = +19% IVA on cross-border ≤ USD 200 (Shein/Temu/AliExpress) | larepublica, infobae 2025-09 |

## Effective τ + IVA panel — target HS chapters

### HS 85 — Electrical machinery, electronics
| Year | τ_NMF (chapter-wtd) | IVA | Notes |
|---|---|---|---|
| 2018 | 5-10% (smartphones/laptops 0% per Decreto 2179/2014; 5-15% other) | 19% | |
| 2019 | Same + inputs 8509.90/8516.90/8539.90 → 0% (Decreto 2074) | 19% | |
| 2020 | Same; Decreto 410 → 0% medical-electronics subhdgs Mar-Sep | 19% | + 3 días sin IVA |
| 2021 | Restored | 19% | + 3 días sin IVA |
| 2022-2024 | No change | 19% | + 3 días sin IVA/yr |
| 2025 | No MFN change; Decreto 0214 enforcement | 19% | |
| 2026 | No MFN change; **de minimis USD 200 → USD 50** = +19% IVA on cross-border ≤ USD 200 | 19% | Cross-border channel step |

### HS 61 + 62 — Apparel
| Year | τ_NMF | IVA | Notes |
|---|---|---|---|
| 2018 | 15% baseline; TLC 0-5% phase-out | 19% | |
| 2019 | 15% | 19% | |
| 2020 | 15%; Decreto 410 → 0% PPE subhdgs Mar-Sep | 19% | |
| 2021-Apr | **Decreto 414/2021**: arancel mixto (40% if FOB ≤ USD 10/kg; 15% + USD 1.50/kg) | 19% | **Major step-up** |
| 2022-Dec-23 | **Decreto 2598/2022**: flat **40% NMF** all FOB | 19% | High-value bracket also up |
| 2023-2024 | **40%** confirmed | 19% | |
| 2025 | **40%** + 0214 threshold update | 19% | |
| 2026 | **40%** + de minimis USD 50 = +19% IVA on cross-border | 19% | |

### HS 94 — Furniture, lighting, home goods
| Year | τ_NMF | IVA | Notes |
|---|---|---|---|
| 2018-2019 | 15% (furniture); 10-15% lighting | 19% | |
| 2020 | Same; Decreto 410 → 0% hospital-bed 9402 Mar-Sep | 19% | |
| 2021-2025 | Restored; no structural change | 19% | |
| 2026 | USD 200 → USD 50 de minimis (limited Chap. 94 cross-border share) | 19% | |

## Días sin IVA dates (Ley 2010/2019 + Ley 2155/2021 codification)

Affect Chap. 61, 62, 85, 94 — encode as fractional dummy `frac_dias_sin_iva_t`:
- 2020: Jun-19, Jul-03, Jul-19 (DL 682)
- 2021: Oct-28, Nov-19, Dec-03
- 2022: Mar-11, Jun-17, Dec-02
- 2023: Jun-23, Jul-21, Dec-02
- 2024-2026: 3 days/yr per Ley 2155 framework (DIAN annual resolución)

## Anti-dumping vigentes (sub-heading specific, minimal target-chapter overlap)

Coverage Nov-2023: 13 derechos antidumping vigentes (steel, ceramics, agro, plastic, paper). Almost none touch Chap. 61/62/85/94 directly at the chapter aggregate level.

Notable: Res. 048/2023 lavaplatos de acero inoxidable (7324.10, China) = 132% ad valorem. Out of target basket.

## De minimis / cross-border-ecommerce regime evolution

| Period | Threshold | Source |
|---|---|---|
| 2012-2021 | USD 200, any origin, IVA-excluded | Ley 1607/2012 Art. 428 ET |
| 2021-2025 | USD 200, TLC-partner origins only | Ley 2155/2021 Art. 47 (mod. Art. 428 ET) |
| **2026** | **USD 50** + 19% IVA above | Reforma Tributaria 2025 / emergencia económica |

**Single most material change for target basket in 2026** — directly raises effective τ on cross-border e-commerce channel by ~19 pp for median cross-border SKU.

## Panel-ready output schema

For Direction-2 regression at `data/processed/tariff_vat_panel.csv`:
```
year, month, hs_chapter, tau_nmf_pct, iva_general_pct,
d_covid_410, d_apparel_step_2021, d_apparel_flat_2022,
d_postal_demin_2026, frac_dias_sin_iva, antidump_flag
```
9 years × 4 target chapters × 12 months = **432 rows**. Every step traceable to a decreto/ley URL.

## URLs (canonical)

**Leyes (VAT):**
- Ley 1819/2016: http://www.secretariasenado.gov.co/senado/basedoc/ley_1819_2016.html
- Ley 2010/2019: http://www.secretariasenado.gov.co/senado/basedoc/ley_2010_2019.html
- Ley 2155/2021: https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=170902
- Ley 2277/2022: https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=199883

**Decretos (Arancel):**
- Decreto 2153/2016 (base): suin-juriscol id=30030336
- Decreto 410/2020 (COVID 0%): suin-juriscol ruta=Decretos/30038950
- Decreto 462/2020 (COVID export ban): suin-juriscol ruta=Decretos/30038990
- Decreto 2598/2022 (apparel 40% permanente): normograma.dian.gov.co/dian/compilacion/docs/decreto_2598_2022.htm
- Decreto 0214/2025 (umbral 52-64): mincit.gov.co/normatividad/decretos/2025/decreto-0214-del-27-de-febrero-de-2025
- Decreto 1184/2025 (37 inputs 0% × 2yr): presidencia.gov.co 2025-11

**Resoluciones (Antidumping):**
- Vigentes list: mincit.gov.co/mincomercioexterior/defensa-comercial/dumping/derechos-antidumping-vigentes

**TLC schedules:**
- TLC EE.UU. listas de desgravación: tlc.gov.co/acuerdos/vigente/acuerdo-de-promocion-comercial-estados-unidos/2-contenido-del-acuerdo/listas-de-desgravacion

**MUISCA arancel (DIAN):**
- https://muisca.dian.gov.co/WebArancel/DefConsultaEstructuraArancelaria.faces

## Gaps

1. Sub-heading 10-digit τ pull for surgical β estimation — chapter-aggregate proxy sufficient for gate, refine for structural estimation
2. TLC phase-out schedules — NMF used as τ regressor assuming non-FTA origins (China dominant for target basket) drive marginal cost pass-through
3. Anti-dumping at sub-heading — flag as binary covariates if specific RUES-panel importers touch covered subheadings
4. Postal de minimis 2026 concurrent with regression window end — single-period step; insufficient post-event obs for clean identification. Treat as sample-end caveat unless panel extends to 2027+
5. Decreto 414/2021 → Decreto 2598/2022 apparel step is the **dominant confounder** in 2021-2022 for HS 61/62 — if not controlled, will absorb most of the FX β signal
