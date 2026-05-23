---
name: d1d-d4-blr-minsky-sharpening
description: Bhaduri-Laski-Riese / Minsky two-price retroactive lens for D1.D+D4 joint iteration — carries BLR terminology forward without amending v0.2 spec
metadata:
  type: reference
---

Retroactive theoretical sharpening of `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2 via BLR/Minsky lens. **Does NOT amend the spec** (CORRECTIONS-A + CORRECTIONS-B locked); only carries language forward for interpretation in notebooks 06_verdict, the LaTeX write-up, and any future external-facing pitch.

## Three sharpenings (do not require spec amendment)

### 1. ρ̂ as P_k/P_i indicator (not just savings retention)

v0.2 frames ρ̂ as "fraction of wage receipt retained as savings". Under BLR/Minsky: **fraction of received liquidity preserved as real cash-flow position (P_i = supply-price-of-output side) rather than discharged into asset-trading or consumption (P_k = demand-price-of-asset side)**. The framing shift is conceptual not numerical; ρ̂ computation is unchanged.

### 2. Bias direction sharpened (theoretical justification beyond wallet-overlap)

v0.2 says "Phase 1 ρ̂ likely understates true wage→capital rate" (bias attributed to wallet-set non-overlap). BLR strengthens this:
- **Denominator inflation**: virtual-economy AMM churn (speculative swaps, MEV pass-through, ponzinomic yield-farming cycles) inflates E_T without representing real wage receipt
- **Numerator suppression**: real-economy productive-investment outflow is INVISIBLE in v0.2's `L_T = off_ramp + consumption + external_inflow + residual` decomposition — it lives inside `consumption_ratio` or `residual`

So ρ̂ misses both directions: denominator-noise-inflation pushes ρ̂ DOWN; numerator-signal-suppression pushes ρ̂ DOWN. Both confirm the v0.2 understatement direction with stronger theoretical justification.

### 3. Self-LBM ≡ Minsky hedge-finance position

The "premium-funded ratchet / self-LBM" in spec §1 and `CLAUDE.md` is a **literal on-chain instantiation of a Minsky hedge-finance position** (P_i committed > P_k speculative): bonded capital cannot be withdrawn arbitrarily, redemption schedule committed, project must produce to vest. This is the Steindl forced-saving + Minsky hedge-finance combination that the concept-bridge map flagged as "gap to position into" (per [[bhaduri-laski-riese-concept-bridge]]).

**Outward-facing copy implication**: when pitching to post-Keynesian economists / impact-finance funders, use:
- "productive-capital ratchet" (preferred)
- "wage-to-capital bridge instrument" (preferred)
- NOT "self-LBM" (reads as crypto jargon)

## Anti-amendment discipline

Spec v0.2 §13 CORRECTIONS-B is locked. Adding §0.13 BLR retroactive sharpening would reopen 2-way review for terminology-only changes — net-negative ROI. Keep the lens in this memory and consume it at:
- Notebook 06 verdict interpretation block
- LaTeX write-up framing section
- External presentations / pitches

## Direction 5 connection

Per `scratch/2026-05-18-direction-5-brainstorm/findings.md`, Direction 5 (Kaleckian productive-investment via MiniPay × Giveth/q-acc) **complements** D1.D + D4 by adding the productive-investment outflow (L_productive) measurement that v0.2's L_T decomposition treats as residual.

Combined wage→capital headline quantity:
```
ρ̂_wage_to_capital = ρ̂_D1D_D4 × ρ̂_D5_productive
                  ≈ Σ(productive outflow) / Σ(wage inflow)
```

Direction 5 cannot run as Stage-1 β in 2026-Q2 (productive-investment volume 3-4 orders too small — q/acc <$1M, cCOP $67K mcap, Glo $764/month). Park Direction 5.0 as measurement-feasibility scoping; revisit Stage-1 β when productive-investment ≥$10M (~2027-Q3).

## Methods-paper opportunity

No peer-reviewed paper has empirically operationalized BLR's Y_real / Y_virtual ratio. The on-chain Abrigo data infrastructure (D1.D + D4 + Direction 5) is uniquely positioned to do so. **Publishable in Cambridge JE / ROPE / Metroeconomica** independent of Stage-1 β magnitude. Methods-paper draft is a parallel-track 2026-2027 deliverable.

## Links

[[bhaduri-laski-riese-concept-bridge]] — full concept-bridge map + literature review
[[d1-transparency-continuation]] — standing D1 disclosure rule
[[pathological-halt-anti-fishing-checkpoint]] — HALT discipline carry-forward
