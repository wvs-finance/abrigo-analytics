# Day-1 4-Direction Consolidation

**Date:** 2026-05-18
**Spec anchor:** `docs/specs/2026-05-18-four-direction-investment-productivity-gating.md` v0.3

## Per-direction Day-1 verdicts

| Direction | Verdict | Headline |
|---|---|---|
| **E5-revised** (RefiColombia COPm) | **PARTIAL** — reframe + wait | Effective claimers = 70 (below N_MIN=75); lifetime 521d (17mo, not 163d — strict improvement); owner EOA = HIGH governance risk (not Panoptic-hedgeable); Y cross-check against Pair D mechanically biased by β=−1 identity. Reframe Y → Δlog(claim_ops) weekly + wait ~10 weeks for cohort growth |
| **E8** (Bittensor dTAO × Maymin) | **CONDITIONAL PASS — methods-paper-only** | wTAO EVM ✓, Subtensor EVM mainnet live ✓, native dTAO pools observable via Taostats ✓ — but **LATAM operator cohort = HARD FAIL** (zero indexed hits; anti-fishing-banned to retrofit). Maymin's CEV β−1 = −0.86 (94% subnets negative; p<0.001) empirically replicates BLR/Minsky concept-bridge ⭐ |
| **E4.0** (PG builders conversion) | **CONDITIONAL → leaning FAIL** | ~55% of OP RetroPGF recipients convert to USD within observable window. **Option A (preferred)**: narrow to Superfluid-streamed R3+ sub-cohort where un-vested OP IS exposed; M = stream-tail hedge. **Option B**: NON-RETIREMENT close. STIP wrong-target (protocols not builders) |
| **E6.1** (LATAM-RWA inventory) | **FAIL → NON-RETIREMENT close** | Only 2 surviving candidates (Plume × Mercado Bitcoin Brazil + BlackOpal LiquidStone II) — both Plume L1, single-venue, Brazilian institutional/accredited. Goldfinch V1 sunset; Credix Solana; Polytrade dormant. Conjunctive ≥3-active + ≥$20M criterion unmet |

## Cross-direction structural findings

### ⭐ E8's Maymin CEV result is the headline empirical contribution

CEV elasticity median β−1 = **−0.86**, 94% of 90 Bittensor subnets negative, rejects pure CEV at β=0 (p<0.001) over 2025-08 → 2026-02. This is **direct empirical evidence for the BLR/Minsky concept-bridge statement** that "the Minsky P_k/P_i gap is endogenously instantiated by every concentrated-liquidity AMM, and Panoptic-style perpetual options price that gap directly." Strongest result of today's parallel exploration; makes the **joint E3+E8 methods-paper** publishable on empirical content not just theory.

### E5 unlocked sharper diagnostic
The agent's discovery that effective claimers (70) < registered active (77) — the cohort distinction we missed in the deep-research — sharpens the N_MIN gate. Combined with the date-typo correction (521-day vs 163-day panel), E5 becomes more empirically tractable on a weekly aggregation than the daily one originally specified.

### E4.0 surfaced a sharper sub-target (Option A)
Original M-sketch (Panoptic put on OP/USDC) chases hedged-away risk for ~55% of cohort. But **Superfluid-streamed R3+ recipients are mechanically unable to sell un-vested OP** → stream-tail un-vested balance IS exposed. M = stream-tail hedge sized to un-vested balance. Anti-fishing requires locking the narrowing BEFORE re-running data.

### E6 closure is the third in the "LATAM RWA permissionless premise is binding kill" series (E2 → E6)
Consistent with both 8-agent reviews. **Forward lesson**: LATAM-specific tokenized SME / impact-bond cohorts at meaningful scale require Brazilian-CVM-or-equivalent legal wrapper which breaks the permissionless premise. Not a 2026 framework path; revisit when EVM-side LATAM SME tokenization grows past the 3-instrument threshold.

## Final ranked candidate set under realizability × mission

🥇 **1. E8.4 + E8.5 methods-paper (Maymin CEV refit + joint with E3)** — MOST REALIZABLE NOW
- Taostats API live; Maymin's 2026 pipeline directly replicable; extended window 2025-08 → 2026-05 gains +50% obs for OOS robustness; Dec-2025 halving as natural-experiment instrument
- Cambridge JE / ROPE / Metroeconomica target; the strongest single conceptual contribution from today's session
- **No N_MIN gate problem** (90 subnets × 200 obs each ≫ 75)
- **No permissionless premise problem** (Bittensor subnet pools are permissionless by construction)
- **No empirical-impossibility problem** (unlike E3 alone, Bittensor pools predate Panoptic but Maymin's CEV doesn't require Panoptic — only AMM data)

🥈 **2. E5-revised RefiColombia with amendments** — REALIZABLE after reframe + wait
- Live on-chain dataset; 521-day history; subgraph free; Pair D's COP/USD β reusable
- Amendments: Y → Δlog(claim_ops) weekly (not Δlog(USD)); wait ~10 weeks for cohort N≥75; CORRECTIONS-E acknowledging governance risk unhedged
- OpSec PII flag to report to RefiMedellín team (separate organizational item)
- §0.8.2 underserved-population focus PURELY anchored (Comuna 13 + Caribbean coast + Saravena/Arauca)

🥉 **3. E4 narrowed to Superfluid-streamed R3+ sub-cohort** — REALIZABLE after re-execute Dune
- Stream-tail un-vested OP IS the genuine hedge exposure
- Re-execute Dune q/3399900 with `DATE_DIFF` for vest-window panel; ≥30-wallet sample per cohort
- Anti-fishing requires pre-locking narrowing rule before data re-run

❌ **CLOSED**: E1 (EVM-incompatible) / E2 (permissionless+P_k-inversion kill) / E3 as β-iteration (folded into E8 joint methods-paper) / E6 (NON-RETIREMENT — LATAM RWA permissionless thin in 2026)

## Recommended next dispatch (single most-realizable primitive)

**E8.4 + E8.5 joint methods-paper draft** is the cleanest dispatch:
1. Pull Taostats API daily panel 2025-08 → 2026-05 (extended window over Maymin's published)
2. Replicate CEV elasticity fit; report β−1 with pre/post Dec-2025 halving as natural experiment
3. Add Uniswap V3 stablecoin+volatile LP empirical fit (E3 application) using same CEV framework
4. Draft methods paper Section 1-2 (theory + concept-bridge framing) + Section 3 (E8 empirical) + Section 4 (E3 empirical) + Section 5 (BLR/Minsky implications)
5. Target Cambridge JE / ROPE / Metroeconomica submission

Sibling dispatches in parallel (NOT competing for priority):
- E5-revised: amend pre-pin (weekly + Δlog(claim_ops)); freeze panel for re-evaluation in 10 weeks
- E4 narrowed: dispatch Option A spec amendment + Dune q/3399900 re-execute
