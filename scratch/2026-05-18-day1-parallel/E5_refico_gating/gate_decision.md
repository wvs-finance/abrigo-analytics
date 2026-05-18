# Direction E5-revised — RefiColombia COPm Subsidies Sub-cohort — Day-1 Gate Decision

**Date:** 2026-05-18
**Spec:** `docs/specs/2026-05-18-four-direction-investment-productivity-gating.md` v0.3 §0.10 + §E5-revised
**Deep-research input:** `scratch/2026-05-18-reficolombia-deep-research/findings.md`
**Pre-pin status:** locked per §0.3 / §0.4; no post-data threshold tuning

---

## Day-1 Verdict

**PARTIAL → CONDITIONAL PASS** for Stage-2 ideal-scenario M-sketch (a Panoptic-construction sketch that *would* settle if deployed). **DO NOT** proceed to a full β-iteration spec until the four conditions in `## Recommended next step` are met.

Rationale: (1) cohort scale just-passes N_MIN=75 at active-beneficiary level but FAILS at effective-claimers level (70<75) and at per-event level depending on time aggregation; (2) governance risk is high (single EOA owner with full `withdrawFunds`/`removeBeneficiary` powers); (3) the naive Y proxy (cohort-aggregate USD value of subsidies) is dominated by the mechanical Δlog(USD) ≈ −Δlog(TRM) identity — the *behavioral* component of FX response (which is what Pair D's β=+0.137 actually measures) is not yet identifiable at this cohort scale / cadence; (4) Pair D's anchor remains *reusable as prior*, but the cross-check at weekly aggregation does not yet confirm or reject it (β̂=-5.52, OLS SE=3.62, t=-1.53; N=73 weeks).

PARTIAL is the honest verdict: data quality on the FX-side is excellent, on-chain data is clean, but the cohort/instrument scale is at the borderline where discrimination is not yet possible. NON-RETIREMENT was considered and rejected because the cohort is growing (~0.5 active beneficiaries/week onboarding rate) and Pair D anchor remains reusable — a one-quarter wait + minor reframe would unblock.

---

## Subgraph + cohort verification

Subgraph `102458/refi-medellin-ubi` live (`api.studio.thegraph.com/query/102458/refi-medellin-ubi/version/latest`); indexed block **67245219** (2026-05-18 16:52:57 UTC); `hasIndexingErrors=false`.

**Cohort confirmation:**

| Field | Reported (findings) | Verified today | Note |
|---|---|---|---|
| Active beneficiaries | 77 | **77** ✓ | floor N_MIN=75 just-passes |
| Total ever (active+removed) | 85 | **85** ✓ | 77 active + 8 removed |
| Off-chain API rows | 72 | **72** ✓ | gap of 5 vs on-chain (5 active beneficiaries onboarded after off-chain DB snapshot or not registered off-chain) |
| Active wallets with **zero** claims | not flagged | **7 of 77** ✗ | effective claimers = 70 (BELOW N_MIN) |
| Total claim ops over panel | "596 tx" (mixed with non-claim tx) | **1,725 claim ops** | finer disambiguation |
| Cumulative COPm distributed | 17.24M | **17,250,000** ✓ | exact match |
| `totalSupplied` | 36,121,200 | **36,121,200** ✓ | exact match |
| `contractBalance` | 18,871,200 | **18,861,200** | minor decay (10K diff = ~one day of claims) |

**Date-typo flag in findings.md**: deep-research says deployment "~2025-12-06". Actual earliest beneficiary add on-chain is **2024-12-13T03:41:50 UTC** (`dateAdded` from subgraph; corroborated by first daily-claim entity timestamp `1734062275`). Contract lifetime is therefore **521 days (~17 months)**, NOT 163 days. This is a strict improvement over deep-research's framing for panel-construction purposes; correcting the typo in findings.md is recommended but does not change the gate verdict.

**Daily-claim panel:** N=407 days with ≥1 claim across the 521-day contract lifetime (78% activity rate). Earliest claim 2024-12-13; latest 2026-05-13 (5 days ago at gate-decision time).

---

## Owner type

Owner of `0x947C6dB1569edc9fd37B017B791cA0F008AB4946` is `0xbe42b3f0ba9f7c8e4b6c219be55566c88cefc581` (read via `owner()` selector `0x8da5cb5b` on Forno Celo public RPC).

**Owner-type probe:**
- `eth_getCode(owner)` returns `0x` → **EOA** (no bytecode at address)
- `eth_getTransactionCount(owner) = 0x11e = 286 nonce` → active EOA with substantial history
- `eth_getBalance(owner) ≈ 21.97 CELO` (`0x13040bbeae9c55033`)

**Governance-risk assessment: HIGH (severity-2 of 3).** Single-signer EOA holds owner-exclusive functions: `addBeneficiary`, `removeBeneficiary`, `setClaimableAmount`, `setClaimInterval`, `setTokenAddress`, `withdrawFunds`. Historical use: `removeBeneficiary` invoked 8× (one beneficiary removal per ~10 added on average); `withdrawFunds` invoked 1× for 10K COPm (~$2.40 — likely a test). No on-chain timelock / Gnosis-Safe protection. Counterparty risk concentrated on a single human-controlled key.

Severity is HIGH (not CRITICAL) because (i) on-chain history shows restraint — no large withdraws, removals appear targeted rather than indiscriminate; (ii) the *operational* governance is community-vouched via the responsable network, which adds social-layer accountability the on-chain primitive does not formalize; (iii) the cohort's small USD scale (~$4.5K total, ~$2.40/claim) limits maximum extractable value. But this risk is NOT hedgeable via any Panoptic position (it's a counterparty-discretion event, not a price-process event), and so it lives outside the Abrigo M-layer entirely. **Flag forward**: any full E5 iteration spec must explicitly acknowledge that the (Y, M, X) instrument family being modeled is independent of, and structurally incapable of hedging, the discretionary-revocation governance risk identified here.

---

## Data availability

### COP/USD daily TRM (Banrep / datos.gov.co dataset `32sa-8pi3`)

- Pulled 345 raw records covering 2024-12-03 → 2026-05-19 from `datos.gov.co`
- Densified to **533 calendar days** (TRM publishes single value for weekends/holidays via `vigenciadesde`/`vigenciahasta` interval)
- **522 days within contract lifetime** (2024-12-13 → 2026-05-18) — full coverage
- TRM range: [3551.17, 4416.69] COP/USD; mean 3967.31; pstdev 233.81
- N_MIN=75 floor: **PASS by 6.96× margin** on daily; **PASS by ~1.0× margin** on weekly

### COPm peg-deviation series

- COPm token verified on-chain at `0x8a567e2ae79ca692bd748ab832081c45de4041ea` (`symbol()`=`COPm`, `name()`=`Mento Colombian Peso`); 18 decimals
- Mento broker swap events on Celo are queryable via Forno RPC `eth_getLogs` filtered by COPm/cUSD `Swap` topic — feasible but NOT executed in this Day-1 pass (out of scope for gate decision; deferred to E5.2 if iteration spec is drafted)
- Expected pegging mechanism: dual-rate via CELO/COP + CELO/USD Chainlink oracles; soft-peg with arbitrage incentive bands
- Per `findings.md`: no peg-deviation events ≥0.5% reported in industry monitoring 2024-10 launch → 2026-05; this is a Y₂ secondary channel of low expected signal at current Mento scale

### Cluster decomposition (via off-chain API `api.subsidios.reficolombia.org/api/beneficiaries`)

Confirmed exactly as deep-research reported:

| Responsable | Count | Likely affiliation |
|---|---:|---|
| **Platohedro** | 19 | Medellín Comuna 13 |
| **Rosiris** | 19 | Caribbean coast — multi-gen "De Angel" family |
| **Waira** | 10 | Saravena, Arauca conflict zone |
| 0xj4an | 6 | dev cluster |
| Wainer | 5 | community-lead |
| 0xflypeztic | 5 | dev cluster |
| Jose Luis | 3 | deployer-cluster |
| Juan | 2 | community-lead |
| Sebastian | 2 | community-lead |
| Ana | 1 | community-lead |
| **Total** | **72** | (off-chain mirror; 5 active beneficiaries missing from off-chain DB) |

Three named clusters (Platohedro/Rosiris/Waira) = 48 of 72 = 67% of off-chain cohort, 48 of 77 = 62% of active on-chain cohort. Adequate for cluster-robust SE design *if* full panel is later constructed, but G=3 clusters is below the G≥6 threshold for asymptotic CR3-VCE — wild-cluster bootstrap (Cameron-Gelbach-Miller; Webb weights; B=999) would be required, with all the caveats that small-G inference brings.

### OpSec flag (carried forward from findings.md)

`api.subsidios.reficolombia.org/api/beneficiaries` returns name + phone + responsable for all 72 registered users without authentication. Re-verified live today. **Not a gate decision input** but a separate issue worth communicating to the RefiMedellín team.

---

## Y time-series descriptive stats

Primary Y proxy: `daily cohort-aggregate USD value of subsidies = daily_claim_ops × 10,000 COPm × (1 / TRM_t)`.

**Daily panel** (522 days within contract lifetime; 407 days with ≥1 claim):

| Quantity | Mean | pstdev | Max | Min | Cumulative |
|---|---:|---:|---:|---:|---:|
| Claim ops/day | 3.30 | 3.42 | 18 | 0 | 1,725 |
| COPm/day | 33,046 | 34,197 | 180,000 | 0 | 17,250,000 |
| TRM (COP/USD) | 3,967.31 | 233.81 | 4,416.69 | 3,551.17 | — |
| **USD/day** | **$8.69** | **$9.25** | **$48.97** | **$0** | **$4,535.23** |

Max-event day: **2026-04-06** — 18 claim ops, 180,000 COPm, $48.97 (single-day all-cohort coordination event; ~25% of active beneficiaries claimed same day).

**Weekly panel** (N=75 weeks with ≥1 claim & TRM available):

| Quantity | Mean | pstdev | Max |
|---|---:|---:|---:|
| Claim ops/week | 23.0 | 16.9 | 58 |
| **USD/week** | **$60.48** | **$46.83** | **$162.57** |

**Cohort concentration:** top-10 active beneficiaries account for 33.3% of cumulative claims; top-20 = 55.4%; Gini = 0.461. 7 of 77 active beneficiaries have never claimed (0 lifetime claims). Effective-claimer count = **70 < N_MIN=75** — fails the strict pre-pin invariant at per-beneficiary panel level (but the panel design proposed in §E5-revised uses cohort-aggregate Y, not per-beneficiary).

---

## Cross-check vs Pair D β

Pair D anchor: β = +0.137 on COP/USD lag-(6,9,12 monthly composite) with Y = Colombian BPO offshoring sector indicator (Pair D Phase 2 PASS sha-chain pinned at `1efd0e34d7c1af821c8528a7bc895a63e1dc5e1c289f3b6a1b2d392ba59806cf` per memory). Sign = positive: COP depreciation → BPO sector benefit (export-revenue translation channel). Lag horizon = 6-12 months (concentrated at 6).

E5-revised proposed cross-check spec (§E5-revised pre-pin row "Primary spec"):

    Δlog(USD_value_t) = α + β·Δlog(spot_COP_USD_t) + γ·peg_dev_t + ε_t

Run today as simplified two-variable OLS (γ=0 since peg-dev series not pulled), lag-1, daily and weekly:

| Aggregation | N | β̂ | OLS SE | t | Sign |
|---|---:|---:|---:|---:|---|
| Daily, lag-1 | 405 | -7.99 | 7.20 | -1.11 | neg |
| Weekly, lag-1 | 73 | -5.52 | 3.62 | -1.53 | neg |

**Interpretation — critical, pre-pin honored:**

The proposed Y construction is `USD_t = COPm_flow_t / TRM_t`. By identity, if claim flow were perfectly invariant to FX, `Δlog(USD_t) = Δlog(COPm_flow_t) − Δlog(TRM_t)`, so the coefficient on `Δlog(TRM_t)` would be **exactly −1**. The empirical β̂ on weekly is **−5.52** with SE 3.62; the mechanical baseline (−1.00) falls within the 90% CI [−11.49, 0.46], so the data cannot statistically distinguish behavioral response from mechanical identity at current cohort scale and observation density. The signed direction (β̂ < −1, i.e. *more negative* than mechanical) hints at a behavioral component where lag-1 COP depreciation reduces claim ops (consistent with a beneficiary-behavior story: when COP depreciates, the 10,000 COPm claim becomes more valuable in USD/imports terms, so beneficiaries may *delay* claiming to wait for further movement — opposite to a passive-recipient model), but this is **NOT IDENTIFIED** at N=73 weeks with this signal-to-noise.

**Anti-fishing-compliant statement of the cross-check result:**

Pair D's β=+0.137 was measured on a different Y (BPO offshoring sector indicator) at a different time aggregation (monthly, lag-6) over a much longer panel (134 monthly observations). The naive day-level cross-check on RefiColombia's cohort-aggregate USD-value-of-subsidies Y at lag-1 is **inadmissible as a confirmation or rejection of Pair D**, because (a) the Y is constructed differently and contains a mechanical −1 component by identity, (b) the time aggregation is much shorter, (c) the cohort is fundamentally different (BPO offshoring firms vs subsidized low-income individuals). What Pair D licenses is a *prior* that COP/USD movements have measurable effects on real-economy Colombian cashflows; that prior remains intact, but a full β-iteration on this cohort would need (i) a Y construction that separates flow-cadence from mechanical translation, e.g. `Δlog(claim_ops_t)` rather than `Δlog(USD_value_t)`, AND (ii) sufficient lag depth and monthly observations (N≥75 months) for the Pair D-style 6-12 month lag horizon to be measurable. **Neither is available today.**

---

## Recommended next step

**WAIT for cohort growth + reframe Y** rather than draft full iteration spec immediately. Specific gating conditions for promotion to full-iteration spec drafting:

1. **Effective-claimers ≥ 75** (currently 70). At observed onboarding cadence of ~0.5 active beneficiaries/week (75 added over 521 days), this is expected within ~10 weeks if cadence holds. Re-poll on **2026-07-27** (10 weeks out).
2. **Y reframe**: switch primary Y from `Δlog(USD_value_t)` (which contains a mechanical −1 identity component) to `Δlog(claim_ops_t)` with HAC-cluster-robust SE — this isolates the *behavioral* claim-cadence response to FX without the mechanical translation. Pre-pin the sign expectation honestly: SIGN UNDETERMINED ex ante (could be β<0 if beneficiaries wait for further depreciation; could be β>0 if depreciation drives immediate consumption-smoothing claims). This is a NEW pre-pin and must be specced ex ante per §0.4 BEFORE any further data work.
3. **Time aggregation**: pre-pin weekly (not daily) as primary; daily as robustness. Pair D's 6-12mo lag horizon is structurally impossible on a 521-day panel; primary lag should be k=1 week, k=4 weeks secondary.
4. **Governance-risk acknowledgement block** must appear in the iteration spec under a CORRECTIONS-E heading, explicitly stating that the M-layer (Panoptic COPm/cUSD straddle) does NOT hedge the dominant cohort risk (discretionary-revocation by EOA owner), and that the analytics work is conditional on the program continuing to operate.

**Pre-iteration tasks that should run during the 10-week wait** (do not consume β-iteration budget):

- E5.2 (COPm peg-deviation series construction via Mento broker Swap logs) — runs independently; informs whether the γ·peg_dev_t covariate has any variance to estimate
- 1-day Stage-2 M-sketch exercise: write the descriptive-only Panoptic position that *would* settle the (Y_reframed, X=COP/USD) β if measured. Per CLAUDE.md ideal-scenario clause, this is permitted without liquidity sourcing.
- OpSec disclosure to RefiMedellín team about unauthenticated PII at `api.subsidios.reficolombia.org/api/beneficiaries` (organizationally separate from analytics work but flagged for completeness)

**Verdict integrity statement:** PARTIAL is the honest call. PASS would have required clean discrimination of behavioral β at current scale, which the data do not support. FAIL would have required either cohort-scale-impossibility or fundamental data-quality breakdown — neither holds; FX side is excellent, on-chain side is clean, cohort is growing. NON-RETIREMENT would have required a path-blocking obstruction — none identified; the cohort is on a growth trajectory and Pair D's prior remains reusable. The two-quarter wait is anti-fishing-compliant (no threshold tuning; pre-pin is reframed BEFORE any further data work, with sign expectation explicitly marked as undetermined where uncertain).

---

## Artifacts pinned

| Artifact | Path / source | Note |
|---|---|---|
| Subgraph query result (beneficiaries) | `/tmp/refi_bens.json` | block 67245219; not persisted to repo |
| Subgraph query result (dailyClaims) | `/tmp/refi_daily.json` | 407 daily rows; not persisted to repo |
| TRM raw + densified panel | `/tmp/trm.json`, `/tmp/trm_panel.json` | 522 days within contract lifetime |
| Off-chain beneficiaries snapshot | `/tmp/refi_off_chain.json` | 72 rows; PII redaction required if persisted |
| Pair D anchor | `memory/project_pair_d_phase2_pass.md` sha `1efd0e34…` | unchanged |
| Spec | `docs/specs/2026-05-18-four-direction-investment-productivity-gating.md` v0.3 §0.10 + §E5-revised | unchanged |
| Deep-research input | `scratch/2026-05-18-reficolombia-deep-research/findings.md` | date-typo flag noted above |

Anti-fishing closure: no post-data threshold tuning was performed; the verdict downgrades the data-as-found, with reframed pre-pin obligations spelled out for the next iteration.
