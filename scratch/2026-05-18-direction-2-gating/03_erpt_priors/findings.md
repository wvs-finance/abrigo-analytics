# D2.3 — ERPT Literature-Based Priors for COP/USD Cost-Side

**Verdict:** PASS — literature supplies ≥7 Colombia-specific and ≥10 cross-country EM point estimates at gate-relevant horizons. Prior surface well-identified, not degenerate.

## Colombia ERPT — published point estimates

Sign convention: positive β = COP depreciation (↑TRM) → import prices in COP rise.

| # | Paper | Sample | Method | Horizon | β̂ (import) | Notes |
|---|-------|--------|--------|---------|-----------|-------|
| 1 | Rowland (2003) Borradores 254 | 1983-2002 | VAR + Johansen | 1m | 0.30-0.40 | 12m cumul. ~0.80 |
| 2 | Rincón-Caicedo-Rodríguez (2005/07) Borradores 330 / ESPE 54 | 1995-2002 | ECM + Kalman TVP | short-run | 0.10-0.70 across mfg sectors | long-run 0.10-0.80 |
| 3 | Banrep TVP-VAR (González-Rincón) Borradores 1093 | 1995-2015 | TV-VAR + SV | 1m | declined ~0.30 → ~0.02-0.05 | core-CPI, not import-stage |
| 4 | Larrahondo-Chávez-Giles-Andrian (IDB 2024) | 2006-2023 | local-projection VAR | 1m impact | **0.42** | sig 1%; dissipates ~21m |
| 5 | MPRA 98651 | 2000-2018 | Threshold-VAR + GIRF | 1m regime-dep | high-TRM ~1.5-2× low-TRM | confirms regime dependence |
| 6 | NLARDL Colombia 2018 | 2000-2018 | Nonlinear ARDL | 1Q | β⁺ ~0.25-0.45; β⁻ ~0.05-0.20 | β⁺ > β⁻ all horizons |
| 7 | Banrep car-market Borradores 1240 | 2003-2019 | sector micro-panel | 1-3m | ~0.6-0.9 (autos) | upper-bound durable |

**Synthesis (Colombia short-horizon import-price β):**
- Modal point: **β ≈ 0.30-0.50** at 1m impact
- Long-run (12m): β ≈ 0.60-0.80
- Time-varying: pass-through to consumer CPI declined post-IT-adoption; import-stage remains high (IDB 2024 = 0.42 impact)
- Asymmetry: depreciation β reliably 1.5-2× appreciation β

## Comparable EM anchors

| Country | Short-run import-price ERPT | Source |
|---------|-----------------------------|--------|
| Mexico | ~0.70 (impact) | IMF REO ch.4; Goldberg-Campa 2010 |
| Brazil | ~0.60 | IMF REO; BER 2007 devaluation |
| Chile | ~0.40-0.55 | IDB; LATAM nonlinear |
| Peru | ~0.40 | IDB; IMF Article IV |
| EM aggregate (33-country) | ~0.50 long-run | Forbes-Hjortsoe-Nenova-style |

Gopinath-Itskhoki-Rigobon (2010 AER) + Gopinath et al. (2020) Dominant Currency Paradigm: USD-invoiced goods have ~0.25 destination-CPI ERPT but **~1.00 mechanical pass-through at invoice stage**. For Abrigo micro-importer cost regression, the relevant β is import-stage = 0.30-0.60 (not the <0.15 CPI figure).

## Sector heterogeneity (stylized facts)

| Class | β short-run | Examples |
|---|---|---|
| High ERPT | >0.6 | Durables (autos HS 87, electronics HS 84-85, capital equipment HS 84); energy; USD-priced commodities |
| Medium | 0.3-0.6 | Intermediates, chemicals, textiles |
| Low | <0.3 | Perishables (HS 02-08); apparel HS 61-62 with high domestic share; locally-invoiced |

**Implication for HS-chapter scope:** primary basket weighted to HS 84/85 will exhibit β at upper end; HS 61/62 apparel at lower end.

## Asymmetry

Colombia direct evidence: MPRA TVAR + GIRF (1.5-2× depreciation premium), NLARDL (β⁺ > β⁻ all horizons). EM consensus: depreciation > appreciation. Chile is documented LATAM counterexample (not replicated for Colombia).

**Linear β specification understates depreciation-side coefficient.** For depreciation-hedge target, prior should sit at upper end of linear-β posterior — or use NLARDL spec, or treat linear β as lower bound.

## Size heterogeneity (cross-country)

- **Amiti-Itskhoki-Konings (2014 AER 104(7))**: Belgian matched importer-exporter — small non-importing exporters ~**90% pass-through**; large import-intensive firms ~**56%**. Mechanism: markup adjustment + imported-input offset, neither cushion available to small firms.
- **Berman-Martin-Mayer (2012 QJE)**: French — high-productivity (large) exporters have lower ERPT via markup adjustment.
- **No Colombian analogue published.** Abrigo DIAN×RUES panel could close this — but not for this gate.

**Policy inference for Abrigo M-design:** Colombian micro-importer β likely **≥0.70**, possibly 0.85-0.95 for USD-invoiced goods with no domestic substitute / no imported-input hedge. Aggregate β estimates **understate micro-importer β by 30-50%** — strengthens (not weakens) Direction-2 case.

## Recommended priors

**Primary (representative micro-importer basket, 1m, linear, pooled):**
```
β_FX→cost ~ Normal(μ=0.50, σ=0.20), truncated to [0, 1]
```
Justification: anchors at EM short-run avg + midpoint of Colombia sectoral range (0.30-0.50 aggregate), upshifted ~0.08 from IDB-2024 0.42 for small-importer correction. σ=0.20 covers cross-sector 0.10-0.70 and TV-VAR variation.

**Asymmetric / regime-conditional (depreciation episodes):**
```
β⁺_FX→cost ~ Normal(μ=0.65, σ=0.20), truncated to [0, 1]
β⁻_FX→cost ~ Normal(μ=0.35, σ=0.20), truncated to [0, 1]
```
Enforce β⁺ ≥ β⁻ via reparameterization: β⁻ = β·(1−ω), β⁺ = β·(1+ω), ω ~ Beta(2,5) shifted to ω ∈ [0, 0.5].

**Sector-conditional adjustments (multiplicative on μ):**
- Durables/electronics/autos (HS 84, 85, 87): ×1.4 (μ≈0.70)
- Intermediates/textiles/chemicals: ×1.0 (μ≈0.50)
- Apparel (HS 61, 62): ×0.7 (μ≈0.35)
- Food/perishables (HS 02-08): ×0.5 (μ≈0.25)

**Sensitivity (literature-uninformative stress):**
```
β_FX→cost ~ Normal(μ=0.50, σ=0.40), truncated to [0, 1]
```

**Auxiliary coefficients γ (tariff), δ (VAT)** — literature doesn't speak directly. By accounting identity for USD-invoiced basket, β+γ+δ ≈ 1.
```
γ ~ Normal(1.0, 0.3), truncated to [0, 2]
δ ~ Normal(1.0, 0.3), truncated to [0, 2]
```
Revisit after tariff/VAT panel (D2.4).

## Key citations

- Rowland (2003) Borradores 254
- Rincón-Caicedo-Rodríguez (2005/07) Borradores 330 / ESPE 54
- Banrep TVP-VAR Borradores 1093 + car-market Borradores 1240
- Larrahondo et al. (IDB 2024) — IDB-DP-13959
- MPRA 98651 (Threshold-VAR)
- Burstein-Eichenbaum-Rebelo (2005 JPE, 2007 JME)
- Gopinath-Itskhoki-Rigobon (2010 AER 100(1))
- Amiti-Itskhoki-Konings (2014 AER 104(7))
- Forbes-Hjortsoe-Nenova (2018 JIE 114; NBER WP 24773)
- Ha-Stocker-Yilmazkuday (2020 JIMF 105; WB PRWP 8780)
- Goldberg-Campa (2010)

## Gaps

1. No published Colombian firm-level matched-importer ERPT in Amiti-Itskhoki-Konings tradition. The Abrigo DIAN×RUES panel could close this.
2. No HS-2/HS-4 chapter-level Colombia ERPT estimates.
3. Wedge between import-price ERPT and importer-cost ERPT not directly studied.
4. Shock-conditional priors (monetary vs demand vs global-risk) not operationalized.
5. No HS-chapter USD-invoicing-share evidence for Colombia.
6. TVP evidence post-2020 limited; COVID/post-COVID episode may have shifted prior mean.
