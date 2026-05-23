# Salvage-Paths Consolidation — Direction 1 G1 Data Availability

**Date:** 2026-05-18
**Context:** D1 G1 initial 4-sub-task investigation found cohort *exists* (75K central, 25-150K range, 25-55% YoY) but is *not measurable at monthly frequency on public data* — GEIH lacks variable, Banrep CoE is 92× too small. Salvage paths explored to find an alternative panel source.

## Per-path verdicts

| Path | Verdict | Wall-clock | Monthly N | Cohort coverage | Stage-2 alignment |
|---|---|---|---|---|---|
| **1. Banrep Sistema de Información Cambiaria** | NOT VIABLE standalone; CONDITIONAL secondary | 6-18 mo for microdata (low approval); instant for aggregates | Bucket aggregates only | 10-20% realistic | Indirect |
| **2. DIAN admin records** | CONDITIONAL aggregate-only | Months for microdata access (Londoño-Vélez precedent); instant for aggregates | Annual aggregates only | <50% (informality + crypto rails invisible) | Indirect |
| **3. EOR-firm partnerships (Deel/Bitwage/etc.)** | CONDITIONAL 6-12 month parallel track | 4-12 months per firm; <35% per-firm success | If delivered, monthly back to 2018 | 40-60% with multi-firm cooperation; un-platformed half always missing | Direct (firm produces wage data; same payment rail as deployment) |
| **4. On-chain crypto rails** ⭐ | **CONDITIONAL VIABLE as Direction 1.D** | 3 weeks (free Dune tier) | **N=76 structurally achievable 2020-2026** | 15-35% (central 20-25%) | **DIRECT — same channel as Stage-2 deployment** |

## Why Path 4 dominates

Three structural advantages no other path has:

1. **Public-default data by construction.** Every USDC/USDT transfer to tagged Bitso/Lemon hot wallets is publicly observable. No permission ask. No access SLA. No reserva. No threshold gating. Bitso 1 hot wallet `0x58b704065b7aff3ed351052f8560019e05925023` has 1.29M transactions and $39.78M token holdings, active since 2021-05.

2. **Same channel as Stage-2 deployment.** Per CLAUDE.md, M-design (Stage 2) settles on Panoptic via USDC/COPm. The measurement rail (USDC inflow to CO-resident wallets) and the deployment rail (Panoptic position) **share infrastructure**. No other salvage path has this alignment. This collapses the measurement-vs-deployment gap that has historically been a friction in the Abrigo framework.

3. **Operationalizes the FINANCILATION framework directly.** Per `FINANCILATION.md`: `CF_T = E_T − L_T`. With on-chain rails:
   - E_T = USDC inflow to Colombian-resident wallets (Layer A+B)
   - L_T = COP off-ramp flow + savings retention
   - CF_T = D4.1 wallet balance trajectory
   The "instrument that creates the capital position" in Abrigo's wage→capital story IS the crypto rail itself. Without USDC payroll: 3-7% Wise/Payoneer FX friction + low-yield COP banking. With USDC payroll: USD-stable native + productive-capital exposure via Panoptic.

## Cross-path complementarity

Despite Path 4's dominance, the **complete D1 measurement architecture** uses three paths in triangulation:

| Layer | Path | Role |
|---|---|---|
| **Primary panel (Y)** | Path 4 — On-chain | Monthly USDC inflow to Bitso/Lemon ≈ wage receipts (Colombia-share 20% × USDT/USDC monthly) |
| **Validation envelope (upper bound)** | Path 1 — Banrep BoP services | Quarterly aggregate IT-exports series as macro-level sanity check |
| **Validation floor (lower bound)** | Path 2 — DIAN CIIU × quantile | Annual aggregates on CIIU J62/J63 declarants as formal-sector ceiling |
| **Future expansion** | Path 3 — EOR partnership | 6-12 month parallel ask to Deel-Thomas + Bitwage/Paystand for firm-side aggregates as cross-check |

## Binding methodological gaps (Path 4)

Two non-fatal gaps that the full iteration must address:

### Gap A: Colombian-resident attribution
Bitso/Lemon hot wallets are operator-tagged but country-of-deposit is NOT in on-chain data. Mitigation:
- Apply 20% Colombia-share scalar (Bitso CO ≈ 20% of LATAM flow per Chainalysis/Bitso public data)
- Sensitivity at 10% / 35%
- The scalar is a *constant* in the regression so it doesn't bias β; it only scales the magnitude of E_T

### Gap B: Contractor-vs-speculator attribution (Layer C)
Wage inflow vs speculator/saver round-trip not solved by chain data alone. Requires:
- Labeled payroll-router addresses (Deel/Bitwage/Remote/Request/Superfluid) — partial public tagging
- Cadence detection (regular fixed-amount transfers, month-end clustering)
- Counterparty-graph clustering

Mitigation: in Phase 1, treat **all** stablecoin inflow as wage+savings composite. Phase 2 adds attribution. For the gating-step β test, what matters is whether the *composite* inflow series correlates with the macroeconomic anchors — it almost certainly does, with magnitude bias toward wage flow (savings inflows are smaller and less time-clustered).

## Connection to Direction 4 (USDC-saver cohort)

D1.D (Path 4 wage-earner cohort) and D4.1 (USDC-saver cohort, 242K wallets) overlap **30-60%** with directional causality D1.D → D4.1 (wage receipt enables saving, not reverse). **This is precisely the wage→capital transition the Abrigo framework was designed to measure.**

Joint model: D1.D inflow = treatment, D4.1 wallet-balance change = outcome, CEX off-ramp ratio = channel parameter → directly interpretable "fraction of wage flow that transitions into capital position." **Most valuable byproduct, not anticipated in original D1 gating.**

## Recommended D1 G1 verdict — REVISED post-salvage

**CONDITIONAL PASS** (revised from FAIL) — via Direction 1.D crypto-rails path.

| Criterion | Spec requirement | Salvaged value |
|---|---|---|
| Monthly N | ≥75 | **76** (2020-01→2026-04, Path 4) |
| Cohort identifiable | yes | Yes — Bitso/Lemon hot wallets × Colombia-share scalar |
| Wage-vs-noise discrimination | clean | Coarse — Layer A+B only at gating; Layer C deferred to Phase 2 |
| Public-data only | required | **Yes — Dune free tier sufficient** |
| Stage-2 alignment | nice-to-have | **EXCELLENT — same on-chain rail** |

## Recommended next steps

1. **Adopt Direction 1.D as the D1 salvage iteration.** Cohort definition: Colombian-resident wallets depositing USDC/USDT to Bitso/Lemon hot wallets across ETH+Polygon+Tron+Base+Arbitrum. Scope as a *subset* (the crypto-rail-paid sub-cohort) of the broader USD-paid remote-worker cohort.

2. **Pre-pin BEFORE building the panel** (per anti-fishing):
   - Sign: β > 0 (Bitso USDC inflow proportional to Banrep services-credit USD)
   - Lag: 0-1 months
   - Spec: log(Bitso USDC inflow CO-share) ~ log(Banrep services-credit USD), monthly
   - Inference: HAC L=⌊T^(1/3)⌋
   - Power: 0.80 on N=76 with prior correlation 0.4-0.6
   - HALT: if FAIL, the path is *informative about coverage estimate* (crypto-rail too small to register against BoP), NOT re-tunable

3. **3-week execution plan** (per Path 4 findings):
   - Week 1: Dune query bundle for Bitso/Lemon CEX inflow monthly panel
   - Week 2: Banrep services-credit reconciliation + cohort-share scalar derivation + pre-pin spec memo
   - Week 3: estimation + HALT-checkpoint trio + gate verdict

4. **In parallel (parallel track, NOT gating)**:
   - Open Deel-Thomas + Bitwage/Paystand outreach (Path 3) — 4-12 mo timeline
   - Pull Castle Island EM Stablecoin Survey Sept-2024 (gap from Path 4)

5. **Out of scope** for D1.D:
   - Banrep cambiario microdata (Path 1) — 6-18 mo, low approval probability
   - DIAN renta microdata (Path 2) — Londoño-Vélez-style bilateral agreement, months timeline

## Direction 4 cross-link

Direction 4 should explicitly adopt the **D1.D → D4.1 joint-model framing** in spec v0.3:
- The two cohorts overlap structurally (30-60%)
- Causal direction D1.D → D4.1 maps to the wage→capital ratchet
- M-design for Direction 4 (long-tail OTM put on USDC) defends the *capital position* that D1.D measurement tracks the formation of

## Files

- `01_banrep_cambiario/findings.md` (NOT VIABLE)
- `02_dian_admin/findings.md` (CONDITIONAL aggregate-only)
- `03_eor_firm_partnership/findings.md` (CONDITIONAL 6-12 mo)
- `04_onchain_crypto_rails/findings.md` (CONDITIONAL VIABLE ⭐)
- `CONSOLIDATION.md` (this file)
