# D4.3 — USDC Supply Yield vs Long-Tail Put Premium

## Verdict
**CONDITIONAL PASS** — central-regime premium-yield margin +2-4pp; stress-regime flips negative (March-2023 σ=15% premium ≈ 13.6% annualized exceeds all yield bands). Three spec amendments required.

## USDC supply yield 2020-2026 (USDC supply APY, indicative bands)

| Year | Aave V2→V3 | Compound V2→V3 | Spark/Sky sUSDC | Coinbase USDC retail |
|---|---|---|---|---|
| 2020 | 2/3/8 | 2/3/6 | n/a | n/a |
| 2021 | 3/6/12 | 3/5/11 | DSR ~0.01% | 0.15% promo |
| 2022 | 2/4/10 | 2/4/9 | DSR re-activated late | 1.5% (Nov 2022) |
| 2023 | 2/3.5/8 | 3/4/8 | DSR 1% → 5% | 2 → 4.5% |
| 2024 | 3/4/9 | 3/4/7 | SSR 9% peak Q3 → 6.5% Q4 | up to 4.7% (Wallet) |
| 2025 | 3/4.5/7 | 3/4/6.5 | SSR 4.5-6 range | 3.5% (One tier) |
| 2026 YTD | 3/3.45/5 | 3/3.5/5 | SSR 4.75% (Q2) | 4.35% current |

**Modal "fairway": 3-5% USDC supply APY across 2020-2026** outside 2021 peak.

Episodic peaks:
- 2021 leverage demand → Aave V2 USDC supply 10-12%
- May 2022 Terra event → brief 8-9% spike
- March 2023 USDC depeg → USDC supply FELL (liquidity flooded out); USDT borrow spiked >60% APR
- 2024 Q3 SSR hit 9% via T-bill/RWA allocators through PSM

## Premium estimate for OTM put on USDC

Black-Scholes European put, S=$1.00, r=4%, T=1/12 month.

### K=$0.99 (1% OTM, 1-month)

| Regime | σ ann | Premium % notional | Annualized rolling |
|---|---|---|---|
| Calm | 1% | 0.0000% | 0.00% |
| Normal | 2% | 0.0020% | 0.02% |
| Elevated | 5% | 0.1369% | 1.64% |
| Stress | 15% | 1.1324% | **13.59%** |
| Crisis | 30% | 2.8070% | 33.68% |

### 25-delta OTM put (recommended — auto-adjusts to vol)

| Regime | Strike K | Premium | Annualized rolling |
|---|---|---|---|
| Calm (σ=1%) | $1.0014 | 0.043% | 0.52% |
| Normal (σ=2%) | $0.9995 | 0.086% | 1.04% |
| Elevated (σ=5%) | $0.9937 | 0.217% | 2.60% |
| Stress (σ=15%) | $0.9754 | 0.661% | **7.93%** |
| Crisis (σ=30%) | $0.9500 | 1.351% | 16.21% |

### Panoptic-specific premium floor

Panoptic premium = continuously-integrated theta sourced from underlying Uniswap V3 pool fees. Pool fee tier sets floor:
- 0.05% fee tier with 50% time-in-range: floor ≈ 9.1% annualized
- 0.01% fee tier: floor ≈ 1.8% annualized

**Streaming premium bounded below by Uniswap fee tier; exceeds BS in calm regimes.** Pool-tier selection (0.01% vs 0.05%) dominates coverage calculation.

## Yield-vs-premium coverage table (BS-theoretical net, K=$0.99 1-mo)

| Yield scenario | Yield % | σ=2% | σ=5% | σ=15% |
|---|---|---|---|---|
| Low (calm floor) | 2.5% | +2.48 pp | +0.86 pp | **−11.09 pp** |
| Mid (modal) | 4.5% | +4.48 pp | +2.86 pp | **−9.09 pp** |
| High (bull) | 8.0% | +7.98 pp | +6.36 pp | **−5.59 pp** |
| Peak (2021) | 12.0% | +11.98 pp | +10.36 pp | −1.59 pp |

Calm/normal: +2 to +8 pp positive. Stress: flips negative across all yield bands.

**Panoptic-realized coverage**: 0.05% pool tier 9% premium floor exceeds Aave/Compound mid-yield → underwater in calm regime unless:
(a) 0.01% pool tier
(b) Wide range so time-in-range low
(c) **Yield-bearing-collateral integration** (post sUSDS / aUSDC as collateral; yield on collateral pays streaming premium)

**(c) is the only viable D4 implementation** and maps directly to spec v0.2 §0.1 "premium-funded ratchet" language.

## Risk-adjusted yield haircut

| Risk component | Haircut (bps/yr) |
|---|---|
| Smart-contract / governance | 30-80 (Iron Bank, Euler, Cream history) |
| USDC issuer / Circle / SVB-type | 20-50 (March 2023 realized once) |
| Oracle / liquidation cascade | 10-30 |
| Bridge / cross-chain (non-mainnet) | 50-200 |

Risk-free-equivalent yield ≈ headline minus 60-130 bps. 4.5% headline → ~3.2-3.9% risk-adjusted. Still covers BS premium in calm/normal; doesn't cover Panoptic 0.05% pool-fee floor without (a)-(c) above.

## Implementation note for Panoptic long-tail position

1. **Strike**: 25-delta OTM put (K≈$0.97-0.98 at σ=5%). **AVOID K=$0.99** — structurally underwater on Panoptic streaming in calm regime.
2. **Pool**: USDC/USDT or USDC/DAI v3, **0.01% fee tier** (0.05% kills coverage). Confirm Panoptic supports 0.01% tier — liquidity may be thin.
3. **Collateral**: Post as aUSDC or sUSDS. **This is the structural premium-funded ratchet.**
4. **Tenor**: Panoptic perpetual; "1-month tenor" is notional analogue.
5. **Roll discipline**: Re-strike to 25-delta when σ regime changes >2× (vol clustering rule).
6. **HALT trigger**: σ > 10% on 7-day realized → suspend roll, hold convex payoff, re-evaluate strike post-event.

## URLs

- DefiLlama Aave V3 USDC: https://defillama.com/yields/pool/aa70268e-4b52-42bf-a116-608b370f9501
- Aavescan: https://aavescan.com/ethereum-v3/usdc
- Compound USDC: https://compound.finance/markets/USDC
- Spark sUSDS: https://docs.spark.fi/user-guides/earning-savings/susds
- Coinbase USDC rewards: https://help.coinbase.com/en/coinbase/coinbase-staking/rewards/usd-coin-rewards-faq
- Panoptic whitepaper: https://arxiv.org/html/2204.14232v3
- Block Scholes × Panoptic research: https://www.blockscholes.com/research/block-scholes-x-panoptic-perpetual-option
- S&P stablecoin valuation: https://www.spglobal.com/content/dam/spglobal/corporate/en/images/general/special-editorial/stablecoinsadeepdiveintovaluationanddepegging.pdf
- Aave 2025 recap: https://aave.com/blog/aave-2025-recap

## Recommendation

**CONDITIONAL PASS** — proceed to D4 Stage 2 with three required spec amendments:

1. **D4 spec v0.2 §0.1**: specify 25-delta OTM tail-strike, NOT K=$0.99
2. **Add collateral-yield-bearing requirement** to premium-funded-ratchet definition (yield on posted collateral, not separate pool)
3. **Add σ ≥ 10% (7-day realized) HALT trigger** to operational playbook

Under central regime (σ 2-5%, yield 3-5%), premium-funded ratchet mechanically viable with ~2-4 pp positive net carry — sufficient to fund accumulation toward wage→capital transition over multi-year horizons. D4 does not fail at this gate; it requires structural spec corrections that sharpen v0.2 §0.1 rather than break it.

## Gaps

1. Canonical subgraph pull not executed (DefiLlama 403). Yield bands indicative; re-pull via Dune/DefiLlama API before Stage 2
2. USDC realized vol time series not computed; compute daily σ from TradingView/Kraken 2022-2026
3. Panoptic Streamia closed-form not extracted; replace 9% floor estimate
4. No empirical Panoptic USDC pool data — ideal-scenario only per CLAUDE.md
5. Coinbase retail rewards regional/tiered fragmentation; for Colombian cohort likely unavailable → Aave/Compound mainnet (bridging cost) or Aave on Celo (native, lower fees) more realistic
6. Smart-contract-risk haircut qualitative
7. No walk-forward backtest of full ratchet across 2020-2026 — flag for Stage 2
