# Direction 1 — USD-paid Colombian Remote Workers — G1 Gate Decision

**Status:** IN PROGRESS (dispatched 2026-05-18)
**Spec anchor:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 1 + §0.5 (v0.2)
**Effort:** 5 working days, public-data only (ADP/G2 descoped per user direction)

## Gating question

Can publicly-accessible data sources (DANE GEIH 2023+ microdata + Banrep BoP + Bumeran/Mercer/Hays salary surveys + ADP Research Institute public publications) yield a defensible estimate of the Colombian USD-paid-remote-worker cohort size AND a monthly time-series of cohort-aggregate USD wage volume of length ≥75 months?

## Pre-pin (locked, anti-fishing per spec §0.2)

| Field | Value |
|---|---|
| Sign | β_vol(COP-realized wage on FX vol) < 0 (higher FX vol erodes wage-buying-power via either conversion-timing loss or precautionary saving); β on FX *level* is mechanical identity, BANNED as primary X |
| Magnitude floor | \|β_vol\| ≥ 0.10 SD-units of Δlog(USD_wage × TRM) |
| Lag | Contemporaneous primary; k=1 month secondary; k>3 BANNED |
| Primary specification | `Δlog(USD_wage × TRM)_t = α + β_vol·RV_t^FX + γ·cohort_churn_t + ε_t` |
| Inference | HAC with L = ⌊T^(1/3)⌋ |
| Power floor | 0.80 |
| HALT chain | Spec-vs-data contradiction → disposition memo |

## Pass criteria

- DANE GEIH 2023+ has identifiable foreign-employer / wage-currency variable, OR
- Banrep BoP + salary-survey triangulation yields a defensible cohort-aggregate USD-wage proxy with monthly granularity ≥75 obs
- Estimated cohort size ≥10K workers (defensible from public anchors)
- Cohort growth rate ≥5% YoY (policy-relevance)

## Fail criteria

- No public source yields monthly cohort-aggregate USD wage volume
- All cohort-size proxies converge below 1K workers

## Sub-tasks (parallel)

| ID | Investigation | Output |
|---|---|---|
| D1.1 | DANE GEIH 2023+ microdata dictionary scan | `01_dane_geih/findings.md` |
| D1.2 | Banrep BoP services-exports analysis | `02_banrep_bop/findings.md` |
| D1.3 | Salary surveys + ADP Research Institute | `03_salary_surveys/findings.md` |
| D1.4 | Cohort-size triangulation across sources | `04_cohort_triangulation/findings.md` |
