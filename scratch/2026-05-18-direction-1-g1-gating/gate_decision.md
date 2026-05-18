# Direction 1 — G1 Gate Decision (Final)

**Status:** COMPLETE — 2026-05-18
**Spec anchor:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 1 + §0.5 (v0.2)
**Effort:** 4 parallel sub-task agents + 4 parallel salvage-path agents

## Composite verdict

**CONDITIONAL PASS via Direction 1.D (on-chain crypto-rails salvage path)** — revised from the FAIL trajectory of the initial 4 sub-tasks.

Initial verdict (4 sub-tasks alone): structural FAIL at panel-construction gate. Cohort *exists* (75K central, 25K-150K range, 25-55% YoY growth) but *not measurable at monthly frequency on standard public sources*.

Salvage verdict (4 paths investigated in parallel): Path 4 (on-chain crypto rails) provides a viable Direction 1.D panel that meets the spec's N≥75 floor structurally, sources free public data via Dune, and uniquely aligns with the Stage-2 Panoptic deployment channel.

## Sub-task results

| Sub-task | Verdict | Headline |
|---|---|---|
| D1.1 DANE GEIH | FAIL | P6920 empirically confirmed = pension contribution; no foreign-employer or wage-currency variable in 2023/2024/2025; Migration Module = inbound Venezuelans only; EMICRON has no foreign-client distinction; Ley 2121/2021 mandate unfulfilled |
| D1.2 Banrep BoP | FAIL | CoE H1-2025 USD 12M = 92× smaller than computer-services + 534× smaller than remittances; quarterly only; no country breakdown; cohort wages likely mis-classified inside remittances without separability |
| D1.3 Salary surveys | CONDITIONAL | Wage levels converge $45-60K median; cohort N order-of-magnitude only ($24K/$43K/$92K Jr/Mid/Sr Tecla.io; $59,393 Arc.dev); **ADPRI = zero Colombia coverage**; Bitwage Sept-2025: cohort structurally contractor-classified by Colombian labor law (USD/USDC channels not employee-payroll) |
| D1.4 Cohort triangulation | PASS | 5-factor Fermi LOW=9.6K / GM=35K / HIGH=127K; reweighted with direct anchors (Fedesoft 406K IT/telecom, Deel +55% YoY, Banrep IT exports $1.758B 2024 implying ~30K) to 75K central / 25K-150K range; 25-55% YoY growth |

## Salvage-path results

| Path | Verdict | Wall-clock | N | Coverage | Stage-2 alignment |
|---|---|---|---|---|---|
| 1. Banrep Sistema Información Cambiaria | NOT VIABLE standalone; CONDITIONAL secondary | 6-18 mo microdata (low approval); instant for aggregates | Bucket only | 10-20% realistic (voluntary canalization) | Indirect |
| 2. DIAN admin records | CONDITIONAL aggregate-only | Months for microdata (Londoño-Vélez precedent); instant for aggregates | Annual aggregates | <50% (Art. 583 reserva + filing threshold + crypto rails invisible) | Indirect |
| 3. EOR-firm partnerships | CONDITIONAL 6-12 mo parallel | 4-12 mo per firm; <35% per-firm success | Monthly back to 2018 *if delivered* | 40-60% multi-firm; un-platformed half always missing | Direct (firm data) |
| **4. On-chain crypto rails ⭐** | **CONDITIONAL VIABLE as Direction 1.D** | **3 weeks (Dune free tier)** | **N=76 structurally** | 15-35% (central 20-25%) | **DIRECT — same channel as Stage-2** |

## Direction 1.D — recommended salvage iteration

### Cohort definition
Colombian-resident wallets depositing USDC/USDT to Bitso/Lemon hot wallets across {Ethereum, Polygon, Tron, Base, Arbitrum}. Scope as a *subset* (crypto-rail-paid sub-cohort) of the broader USD-paid remote-worker cohort. Coverage estimate: 15-35% of full cohort.

### Pre-pin (locked, anti-fishing per spec §0.2)

| Field | Value |
|---|---|
| Sign | β > 0 (Bitso/Lemon USDC inflow proportional to Banrep services-credit USD) |
| Magnitude floor | \|β\| ≥ 0.10 (elasticity SD-units) |
| Lag | Contemporaneous primary; k=0-1 months secondary; k>3 BANNED |
| Primary specification | `log(Bitso_USDC_inflow_CO_share)_t = α + β·log(Banrep_services_credit_USD)_t + ε_t`, monthly |
| Inference | HAC L = ⌊T^(1/3)⌋ |
| Power | 0.80 on N=76 with prior correlation 0.4-0.6 |
| Colombia-share scalar | 20% (sensitivity 10% / 35%) — scalar is a constant, doesn't bias β; only scales magnitude |
| HALT | If FAIL, informative about coverage (crypto-rail too small to register against BoP), NOT re-tunable |

### Anchor address
**Bitso 1: `0x58b704065b7aff3ed351052f8560019e05925023`** — main exchange wallet, 1.29M tx, $39.78M token holdings (USDT $32.16M + USDC $7.12M), active continuously since 2021-05, multichain (Polygon/Arbitrum/Optimism/Avalanche/Base).

### 3-week execution plan

| Week | Deliverable |
|---|---|
| 1 | Dune query bundle for Bitso/Lemon CEX inflow monthly panel; verify against published Bitso 2024 totals |
| 2 | Banrep services-credit reconciliation; cohort-share scalar derivation; pre-pin spec memo |
| 3 | Estimation + HALT-checkpoint trio + gate verdict |

### Two non-fatal binding gaps

**Gap A — Colombian-resident attribution**: Bitso/Lemon hot wallets are operator-tagged but country-of-deposit is NOT in on-chain data. Mitigation: 20% Colombia-share scalar (sensitivity 10%/35%). The scalar is a *constant* in the regression so it doesn't bias β; only scales magnitude of E_T.

**Gap B — Contractor-vs-speculator attribution (Layer C)**: Wage inflow vs speculator/saver round-trip not solved by chain data alone. Phase 1 (gating): treat all stablecoin inflow as wage+savings composite. Phase 2: add labeled-payroll-router attribution (Deel/Bitwage/Remote/Request/Superfluid) + cadence detection.

## Cross-direction structural finding

**D1.D ↔ D4.1 wage→capital ratchet**: D1.D (Path 4 wage-earner cohort, 15-35% of 75K = 11K-26K wallets) and D4.1 (USDC-saver cohort, 242K wallets) share the same on-chain rail with structural overlap 30-60% and directional causality D1.D → D4.1. Joint model:

```
D1.D inflow (E_T) → CEX off-ramp ratio (1 - savings retention) → D4.1 balance change (CF_T)
```

This is **precisely the wage→capital transition the Abrigo framework was designed to measure**. The on-chain rail is simultaneously the measurement channel AND the Stage-2 deployment channel — unique among all 4 salvage paths.

## FINANCILATION operationalization

Per `~/learning/post-keynesian/notes/FINANCILATION.md`: `CF_T = E_T − L_T`
- **E_T (wage earnings flow)** = Bitso/Lemon USDC inflow × Colombia-share scalar (Layer A+B)
- **L_T (savings depletion)** = COP off-ramp flow (Mento broker + Bitso withdrawals to bank accounts) + savings retention
- **CF_T (cumulative financial position)** = D4.1 USDC-saver wallet balance trajectory

The "instrument that creates the capital position" in Abrigo's wage→capital story IS the crypto rail itself. Without USDC payroll: 3-7% Wise/Payoneer FX friction + low-yield COP banking. With USDC payroll: USD-stable native + productive-capital exposure via Panoptic.

## Recommended spec v0.3 amendments

### §0.5 D1 phase split — UPDATED
D1 G1 evolves from "ADP G1 + ADP G2" (already descoped) to **D1.D crypto-rails Direction**. Cohort definition narrows to crypto-rail-paid sub-cohort with explicit coverage caveat (20% scalar, sensitivity 10-35%).

### §Direction 1 Y, M, X — REFRAMED
- **Y**: monthly log(Bitso/Lemon CEX USDC+USDT inflow × CO-share) — composite wage+savings indicator at Phase 1; refined to wage-only at Phase 2 via Layer C attribution
- **X**: Banrep services-credit USD (quarterly, interpolated to monthly) as the macro USD-flow anchor; secondary: COP/USD spot for M-sizing
- **M (cohort-wallet perspective per §0.1)**: long-COPm / short-USDC on Mento USDC/COPm Panoptic pool, sized to next-period expected USD wage. Premium funded by USDC supply yield on collateral (aUSDC / sUSDS). **Same rail as the measurement channel** — measurement and deployment co-located on-chain.

### §0.6 sequencing — UPDATED
D1 sequencing collapses to "Direction 1.D 3-week execution" (after D2 full-iteration spec is drafted). D1.D and D4 share infrastructure; should be advanced as a joint workstream rather than separate.

## Open issues for user decision

1. **Adopt Direction 1.D as the canonical D1 path?** Yes/no. If yes, spec v0.3 amendments above land.
2. **Phase 1 / Phase 2 split**: Phase 1 = composite stablecoin inflow on N=76; Phase 2 = Layer C attribution. Accept this two-stage approach or insist on Layer C before any β estimate?
3. **D1.D ↔ D4 joint workstream**: combine into a single iteration with shared on-chain pipeline + joint model, or keep separate?
4. **Path 3 (EOR partnership) parallel track**: open Tier-1 outreach (Deel-Thomas + Bitwage/Paystand) now as a 6-12mo parallel, or hold until D1.D Phase 1 verdict?
5. **Cohort labeling**: "Colombian crypto-rail-paid remote workers (15-35% subset of broader USD-paid cohort)" — accept narrower scope, or descope D1 entirely?

## Files

- `01_dane_geih/findings.md` — FAIL (P6920 = pension confirmed empirically)
- `02_banrep_bop/findings.md` — FAIL (CoE 92× too small + quarterly + no country)
- `03_salary_surveys/findings.md` — CONDITIONAL (wage levels + Bitwage CO contractor-classification structural finding)
- `04_cohort_triangulation/findings.md` — PASS (75K central, 5.7× growth)
- `salvage-paths/CONSOLIDATION.md` — 4-path roll-up + Path 4 dominance reasoning
- `salvage-paths/{01..04}/findings.md` — individual salvage-path investigations
- `gate_decision.md` — this file
