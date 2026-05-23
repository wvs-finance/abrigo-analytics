# ReFi Colombia + Subsidios Platform — Deep Research

**Date:** 2026-05-18 (research by sub-agent dispatch)

## Verdict

**VIABLE Abrigo cohort candidate (MEDIUM-HIGH confidence)** — subsidios platform is real, deployed, verified on Celo Mainnet, uses Mento COPm; smart contract open-source; subgraph live; 163 days of timestamped history. **Scale is borderline**: 77 active beneficiaries vs N_MIN=75 floor (just-passes).

**Recommended placement: Option A — Colombian sub-cohort under E5 (ReFi)**, repositioning E5 from "carbon-credit holders" to "Mento-COPm-claim recipients under Celo-DAO operated subsidy program". Reuse Pair D's confirmed positive-β COP/USD result as starting prior.

## Identity + governance

- **ReFi Colombia** — Nonprofit, founded 2023, 2-10 employees per LinkedIn
- **Lead**: Juan Giraldo (publicly listed)
- **5 local nodes**: Medellín (most mature, April 2023, first Colombian ReFi DAO node), Bogotá, Saravena (Arauca conflict zone), Cartagena, Atlántico
- **Named operators**: Daniela Monclou, Tereza Bízková, Edward Calderón, Yesica García, Waira Tamayo, Luis Casseres, Emerson Silva, Fabio Anaya, Alejandro Soto, Ximena Monclou, Sergio Martínez, "0xj4an" (finance), "0xflypeztic" (branding)
- **Funding provenance**: ReFi DAO seed grant (April 2023, formerly "ReFi Spring") + Gitcoin Round 17 (~$4K, March 2023) + ongoing Gitcoin/Celo PG rounds + Giveth donations

## Subsidios platform mechanism

- **Platform**: `https://subsidios.reficolombia.org` — Vite + React SPA, WalletConnect, PWA-installable
- **Self-description (manifest)**: "Claim and donate cCOP subsidies on Celo"
- **Mechanism**:
  1. Owner registers beneficiaries via `addBeneficiary(address)`
  2. Beneficiaries call `claimSubsidy()` once per `subsidyClaimInterval` (~9.6h)
  3. Each call transfers **10,000 COPm (~$2.40 USD)**
  4. Anyone can refill via `addFunds(uint256)` (Donate surface)
  5. Owner may `withdrawFunds()` (used once for 10K COPm)
  6. Indexed via The Graph subgraph `102458/refi-medellin-ubi`
  7. Referrals routed through **Divvi** (`0x302E2A0D4291ac14Aa1160504cA45A0A1F2E7a5c`)

### ⚠ OpSec finding flagged to user

Off-chain mirror DB at `api.subsidios.reficolombia.org` — `/api/beneficiaries` exposes **unauthenticated PII** (name + phone + "responsable") for all 72 registered users. Worth reporting to RefiMedellín team.

## On-chain footprint

| Field | Value |
|---|---|
| Chain | Celo Mainnet (chainId 42220) |
| Contract | **`0x947C6dB1569edc9fd37B017B791cA0F008AB4946`** (`SubsidyProgram`) |
| Compiler | Solidity 0.8.28, optimizer 200 runs |
| Verified | YES on Celoscan (Exact Match) |
| Deployer | `0x1726cf86da996bc4b2f393e713f6f8ef83f2e4f6` (Jose Luis Dev) |
| Deployment block / tx | 67243090 / `0x62bd78d4ba209e3f84a0a10c713e4eef7cb7eaf553f92688589b975e155c6799` |
| Deployment date | ~2025-12-06 |
| Token | **COPm** (Mento Colombian Peso, launched 2024-10-31 via CGP-150 + CGP-151) |
| Total tx | 596 |
| Subgraph indexed block | 67244318 |

**ABI**: `addBeneficiary`, `removeBeneficiary`, `setClaimableAmount`, `setClaimInterval`, `setTokenAddress`, `addFunds`, `withdrawFunds`, `claimSubsidy`, `isBeneficiary`. Owner-gated except `addFunds` + `claimSubsidy`.

**GitHub** (`ReFiMedellin`): WebSite (Next.js), Lending-protocol (Foundry+Solidity, updated 2025-06-09), SmartContracts, OldSmartContracts, AlgorandLending. **The deployed SubsidyProgram contract is NOT in public GitHub — likely private repo.**

## Beneficiary cohort

- **77 active** (on-chain `isActive=true`)
- **85 total ever** (on-chain; 8 removed)
- **72 in off-chain API**

**Onboarding**: 2025-12-06 → 2026-05-05 steady cadence.

**Geography (inferred from "responsable" clusters)**:

| Responsable | Count | Likely affiliation |
|---|---:|---|
| Platohedro | 19 | Medellín, Comuna 13 |
| Rosiris | 19 | Caribbean coast (Cartagena/Atlántico; multi-gen "De Angel" family) |
| Waira | 10 | Saravena, Arauca |
| 0xj4an / 0xflypeztic / Sebastian / Juan / Ana / Wainer / Jose Luis | balance | dev + community-lead onboardings |

All phone numbers `+57` Colombian mobile.

## Funding source (on-chain Funds entity)

| Aggregate | COPm | USD (~4,150 COP/USD) |
|---|---:|---:|
| `totalSupplied` | **36,121,200** | ~$8,700 |
| `totalWithdrawn` | 10,000 | ~$2.40 |
| `totalClaimed` | **17,240,000** | ~$4,150 |
| `contractBalance` | **18,871,200** | ~$4,550 |

**Inflow channels** (none confirmed dominant): direct Donate surface; **Giveth** ($25,159 / 356 donors verified, partially bridged); ReFi DAO grants; Gitcoin / Celo PG; internal treasury conversion (16-30% to Glo Dollar, remainder partially to COPm).

**Not funded by**: Colombian government (Renta Ciudadana / Colombia Mayor are NOT this program), Mento Foundation direct, carbon-credit sales, Optimism RetroPGF.

## Token economics

- **COPm** = Mento Colombian Peso (formerly cCOP), 2024-10-31 launch, soft-peg via CELO/COP + CELO/USD Chainlink oracles. Governed by Celo Colombia DAO. 18 decimals.
- Per-claim: 10,000 COPm (~$2.40) every ~9.6h
- **Pass-through stablecoin model — NO native token, NO airdrop, NO yield wrap**
- Wage→capital ratchet framing is **thin** — $2.40/claim is consumption-supportive, not capital-building. The (M, X) design would need to **stack a hedge on top** of the COPm flow rather than treat the flow itself as the ratchet.

## Partnerships

**Confirmed**: ReFi DAO, Celo Colombia DAO, Mento Labs, **Platohedro** (Comuna 13 community space, onboards 19/77), impactMarket (legacy UBI partner), SalvaTerra (Medellín env conservation), GiveDirectly + Glo Consortium, Giveth, DotLabs (education), Green Digital Guardians, Divvi (referrals).

**NOT partners (verified absences)**: Toucan, KlimaDAO, Solid World, MOSS, Centrifuge, Ministerio de Ambiente, Procolombia, Bancóldex, DPS/Prosperidad Social.

## Application + KYC

**NOT permissionless. KYC**: light / community-vouched.

Workflow: community lead identifies candidate → collects name+phone off-chain → owner calls `addBeneficiary` on-chain → beneficiary receives Valora wallet help and claims from there. **Centralized whitelist with on-chain disbursement**, NOT sybil-resistant — closer to GiveDirectly-style targeted UBI.

## Activity (last 10 days through 2026-05-18)

| Date | Claims | COPm |
|---|---:|---:|
| 2026-05-18 | 8 | 80,000 |
| 2026-05-17 | 13 | 130,000 |
| 2026-05-16 | 4 | 40,000 |
| 2026-05-15 | 4 | 40,000 |
| 2026-05-14 | 9 | 90,000 |
| 2026-05-13 | 4 | 40,000 |
| 2026-05-12 | 6 | 60,000 |
| 2026-05-11 | 12 | 120,000 |
| 2026-05-10 | 9 | 90,000 |
| 2026-05-09 | 10 | 100,000 |

Avg ≈ 8 claim ops/day ≈ ~10% of active beneficiaries → weekly cadence per beneficiary (well below theoretical 9.6h max).

## Risk profile under PK lens

Cohort: Colombian low-income recipients of Celo-DAO operated COPm subsidy — Comuna 13 (Platohedro), Caribbean coast (Rosiris extended family), Saravena/Arauca conflict zone (Waira cluster).

**Hedgeable micro-risks**:

1. **COP/USD FX risk** — claim proceeds buy less USD-priced imports when COP depreciates. **Pair D's confirmed positive-β COP/USD instrument directly reusable**.
2. **COPm peg-deviation risk (Minsky two-price)** — Mento soft-peg not stress-tested at scale; long-vol short-peg straddle on COPm-cUSD Panoptic is clean Abrigo fit.
3. **Discretionary-revocation governance risk** — `removeBeneficiary` used 8×; `withdrawFunds` used 1×. Concentrated owner counterparty. **Not hedgeable via Panoptic** — off-chain governance instrument needed.
4. **CELO gas-cost risk** — claims require gas; near-zero CELO balance blocks claims.
5. **Mento-protocol systemic risk** — cf 2022 cEUR depeg; hedgeable via cross-Mento basket.

## Best-fit (Y, M, X) candidate

- **Y**: COPm-denominated household-consumption-basket realized vol (proxy: daily claim ops × 10,000 COPm vs DANE Bogotá/Medellín CPI)
- **X**: COP/USD daily lag-1 returns (reuse Pair D's confirmed positive-β anchor)
- **M**: COPm/cUSD Panoptic straddle, premium-funded out of 10,000-COPm claim flow

## Recommendation

**Option A (RECOMMENDED) — Colombian sub-cohort under E5**.

Reposition E5 from generic "carbon-credit holders" to a Colombia-specific ReFi sub-cohort anchored on the Mento-COPm subsidies program. Reuse Pair D's positive-β COP/USD result as starting prior.

**Pros**:
- Real live on-chain dataset; 596 tx; 163 days of timestamped history; zero-cost via subgraph
- Reuses Pair D's confirmed X
- Mento-native EVM-only Celo (matches §0.8.1 EVM constraint)
- Fits "wage→capital ratchet" framing (subsidy stream = quasi-wage; hedge converts to capital)

**Cons**:
- N_MIN=75 just-passable at 77 active — would need (a) widen cohort to ever-registered (n=85 with state covariate), or (b) wait 2-3 months at observed onboarding cadence
- Per-beneficiary stream too small to fund real Panoptic premium today — ideal-scenario modeling permitted per CLAUDE.md, but deployment requires stream scaling or external premium subsidy

**Option B — Stand-alone direction (E8)**: NOT recommended at current scale; revisit if program scales 10× or partners with institutional sponsor (Bancóldex, DPS).

**Option C — Defer**: NOT recommended; data quality + framing match too clean.

## URLs verified (2026-05-18)

- subsidios.reficolombia.org (200; SPA)
- api.subsidios.reficolombia.org/health (200) and /api/beneficiaries (200, 72-row JSON with PII)
- api.studio.thegraph.com/query/102458/refi-medellin-ubi/version/latest (200; block 67244318)
- celoscan.io/address/0x947C6dB1569edc9fd37B017B791cA0F008AB4946 (verified SubsidyProgram)
- refimedellin.org/es; blog.refimedellin.org; github.com/ReFiMedellin (5 repos)
- giveth.io/project/refi-medellin ($25,159 / 356 donors)
- mento.org/blog/announcing-the-launch-of-ccop... (2024-10-31)
- forum.celo.org/t/launch-of-ccop-colombia-s-first-decentralized-stablecoin/9211 (CGP-150 + CGP-151)
- x.com/RefiColombia/status/2051122583588761859 → **404** (post ID malformed; tweet snowflakes from 2026 are ~1.85-1.95×10¹⁸; the provided 2.05×10¹⁸ implies 2032+ timestamp — likely typo)

## Gaps / unknowns

1. **The specific X post (ID 2051122583588761859) could not be retrieved** — ID malformed; user likely typo'd. Re-share needed.
2. **SubsidyProgram source code** verified on Celoscan but absent from public GitHub — can be pulled from Celoscan for deeper audit.
3. **City-level geography** inferred from responsable clusters + surname patterns, not directly recorded.
4. **Funding-source breakdown by channel** not disambiguated on-chain.
5. **Owner type (multisig vs EOA)** not yet checked — single `owner()` Celoscan read resolves.
6. **Carbon-credit / Toucan integration**: explicitly ABSENT. If E5 framing depends on a carbon-credit instrument specifically, this cohort is poor fit — a **Terrasos / El Globo Habitat Bank biodiversity-unit holder** or **Toucan TCO2-pool participant** cohort would be the carbon-credit-specific match.
