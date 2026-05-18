---
name: colombian-crypto-regulation-2026-constraint
description: Colombian crypto regulation 2026 is a portfolio-level binding constraint on Abrigo iterations targeting Colombian retail cohorts on EVM. SFC/UIAF KYC on VASPs + Banrep stablecoin takeover 2026 + DIAN $50K retail-trade flagging. Closed E2 RWA original; closed E9 original framing. E5 RefiColombia survives via community-onboarding KYC. Future Colombian-retail-on-EVM directions must address this constraint at G0.
metadata:
  type: reference
---

## Surfaced via E9 G0 feasibility scoping 2026-05-18 (Check 5)

When evaluating Direction E9 (Colombian energy-AMM convex hedge), the G0 agent found the same structural failure pattern that closed E2 RWA original: **Colombian residential prosumer cannot transact tokenized assets on EVM through a regulated on-ramp without KYC.** This pattern is portfolio-level, not E9-specific.

## The binding constraint set (2026)

| Authority | Mandate | Effect on Abrigo |
|---|---|---|
| **SFC** (Superintendencia Financiera) | AML/KYC mandate on VASPs (Virtual Asset Service Providers); PSAV regime requires legal constitution in Colombia or local branch + KYC/AML/CFT | Permissionless cohort access on EVM requires either self-custody offshore (small population) or KYC'd VASP onboarding |
| **UIAF** (Unidad de Información y Análisis Financiero) | Stablecoin compliance checklist active; CFT rules for Colombian PSPs | Colombian PSPs handling stablecoin flows must register and report |
| **Banrep** | Takes over stablecoin regulation in 2026 | Stablecoin-denominated cohorts (USDC/USDT/COPm) face evolving Banrep-set rules |
| **DIAN** | 2026 first reportable tax year for crypto; $50K retail-trade flagging threshold; first annual report due May 2027 | Retail cohorts above $50K trading volume become traceable + taxable |

## Effect on Abrigo iteration portfolio

| Direction | Status under constraint | Why |
|---|---|---|
| E2 RWA original (CLOSED) | Killed | All 8 RWA vehicles required off-chain custodian + KYC at primary issuance |
| E5 RefiColombia (FROZEN READY) | Survives | KYC handled at community-onboarding by RefiMedellín team; beneficiaries receive Valora wallet help; subsidy disbursement is on-chain but VASP layer is licensed |
| E6 LATAM-RWA (CLOSED) | Killed | Brazilian-CVM and Colombian regulatory wrappers break permissionless |
| **E9 original** (CLOSED 2026-05-18) | Killed | Residential PV-prosumer has no community-onboarding analog; can't transact tokenized kWh through regulated on-ramp without individual KYC |
| E9-A (operator-level simulation) | Survives | Cohort is institutional AGPE operators, not residential prosumers; KYC less binding for utility-scale generators |
| E9-B (methods-paper-only) | Survives | No cohort claim → no KYC dependency |
| E7 Mento minter | Open | Mento minters are typically institutional treasury entities; KYC less binding |
| E8 Bittensor operators | Open | Bittensor cohort is global, not Colombian-retail; KYC less binding |

## The pattern

**Direction passes the regulation constraint IF**:
- Cohort is institutional / utility-scale / treasury (not residential retail), OR
- Cohort has a community-onboarding KYC layer (like RefiColombia), OR
- Cohort is global (not Colombian-retail-targeted), OR
- Iteration is methods-paper-only (no cohort claim)

**Direction FAILS the regulation constraint IF**:
- Cohort is Colombian residential retail, AND
- Iteration requires on-EVM permissionless access by the cohort, AND
- No community-onboarding KYC layer exists

## G0 checklist amendment

Every future Abrigo direction targeting a Colombian cohort must answer at G0:
1. Is the cohort residential retail or institutional?
2. If residential retail: is there a community-onboarding KYC layer (analog to RefiColombia)?
3. If no community layer: does cohort have self-custody-offshore access (e.g., Bitso/Lemon retail exchange accounts)?
4. Does the direction's M require permissionless on-EVM transaction by the cohort?

If all 4 answers point to "cohort cannot transact permissionlessly on EVM without individual KYC" → BLOCK at G0 with NON-RETIREMENT.

## Anti-fishing carry-forward

Do not rerun E2 / E6 / E9-original failure modes under new labels. The Colombian retail-on-EVM permissionless premise is closed-FAIL until the regulatory regime changes (Banrep stablecoin licensing framework matures, SFC opens a self-custody safe-harbor, or DIAN clarifies non-trading-flow treatment). Revisit constraint set in 2027-Q3+ unless legislative news triggers earlier reassessment.

## Links

[[abrigo-portfolio-prioritization-with-fallback]] — portfolio framework that incorporates this constraint
[[abrigo-framing-clarification-investment-productivity]] — broader investment-productivity framing
[[bhaduri-laski-riese-concept-bridge]] — PK theoretical anchor preserved

## Sources verified 2026-05-18

- Colombian PSP stablecoin compliance — `https://www.muralpay.com/blog/stablecoin-compliance-checklist-for-colombian-psps-uiaf-sfc-rules`
- Lightspark Colombia crypto regulation — `https://www.lightspark.com/knowledge/is-crypto-legal-in-colombia`
- Sumsub 2026 global crypto regulation — `https://sumsub.com/blog/global-crypto-regulations/`
- Colombia digital assets law draft — `https://www.ainvest.com/news/colombia-finalizes-digital-assets-law-draft-regulate-cryptocurrency-sector-2603/`
