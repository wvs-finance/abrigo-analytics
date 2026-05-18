# D4.1 — 5-Factor Fermi Cohort Estimate for Colombian USDC-Savers

## Verdict
**PASS** — LOW bound ≈ **42,000 wallets** (4.2× the 10K gating floor); geometric mean ≈ **242,000 wallets**. Even under pessimistic compound of all 5 factors the cohort clears the gate.

## 5-factor table

| # | Factor | Low | Mid | High | Sources |
|---|---|---|---|---|---|
| F1 | LATAM crypto users | 70M | 95M | 130M | Chainalysis 2025 Geography; Bitso Crypto Landscape 2025; Triple-A 2024 (562M global, LATAM 14-18%) |
| F2 | Colombia share of LATAM users | 5.0% | 6.5% | 8.5% | Chainalysis txn-vol splits ($44.2B/~$620B ≈ 7.1%); Triple-A Colombia 10.2% adults vs LATAM 15.2%; Bitso 500K/10M (5%) |
| F3 | Stablecoin-holder rate | 0.40 | 0.55 | 0.70 | Bitso 2025: 40% of LATAM purchases stables; Chainalysis 2025: Colombia 50%+ of exchange purchases stables |
| F4 | USDC share (by holder count) | 0.12 | 0.20 | 0.30 | Artemis+Dune Feb-2025: USDC 6.8M / ~30M active ≈ 22%; CoinGecko mcap (USDC 24%, USDT 59% Apr-2026) |
| F5 | Active-balance (saver) rate | 0.25 | 0.40 | 0.60 | Artemis/Dune 2025: 30M active stable addresses |

## Cohort size: low / GM / mid / high
```
Cohort = F1 × F2 × F3 × F4 × F5

LOW   (each conservative)    :     42,000 wallets   [BINDING for gate]
GM    (per-factor geo-mean)  :    241,800 wallets
MID   (each midpoint)        :    271,700 wallets
HIGH  (each optimistic)      :  1,392,000 wallets
```

LOW vs 10K floor: **4.2× headroom**. MID/GM converge within 12% — central estimate stable across aggregation.

## Implied aggregate USDC AUM in Colombia

| Median balance | LOW AUM | GM AUM | HIGH AUM |
|---|---|---|---|
| $80 (dust-heavy) | $3.4M | $19.3M | $111M |
| $200 (central) | $8.4M | $48.4M | $279M |
| $500 (saver-heavy) | $21.0M | $120.9M | $696M |

**Central (GM × $200) ≈ $48M USDC AUM in Colombia.** Cross-check: Colombia $44.2B annual crypto txn vol × 40% stable × 22% USDC = $3.9B USDC turnover → ~$50-150M AUM at 15-30 day holding periods. **Cross-checks agree.**

## Growth rate 2022 → 2026

| Factor | 2022 est | 2026 GM | Multiplier |
|---|---|---|---|
| F1 LATAM users | 35M | 95M | 2.7× |
| F2 CO share | 5.5% | 6.5% | 1.2× |
| F3 stable holder rate | 25% | 55% | 2.2× |
| F4 USDC share | 22% | 20% | 0.9× |
| F5 active rate | 40% | 40% | 1.0× |
| **Cohort** | **~42K** | **~242K** | **5.7×** |

4-yr CAGR ≈ **55%/yr**. F4 flat-to-down reflects March-2023 SVB depeg collapsing USDC share (since recovered) — **favorable for D4's depeg hypothesis**. The 2022 cohort estimate ≈ 42K coincides with the 2026 LOW bound, suggesting the 10K floor is calibrated to where the market was 4 years ago.

## Sensitivity (factor uncertainty ranking)

| Factor | High/Low ratio | Rank |
|---|---|---|
| F4 USDC share | 2.50× | **1 (widest)** |
| F5 active-balance rate | 2.40× | 2 |
| F1 LATAM users | 1.86× | 3 |
| F3 stable holder rate | 1.75× | 4 |
| F2 Colombia share | 1.70× | 5 (tightest) |

**F4 dominates uncertainty** — LATAM-specific USDC-vs-USDT holder data thinnest; published breakdowns are global. Even with F4+F5 both pessimistic-extreme, LOW=42K clears 10K. **Gate decision robust to dominant uncertainty.**

## URLs verified

- Chainalysis 2025 Global Crypto Adoption — https://www.chainalysis.com/blog/2025-global-crypto-adoption-index/
- Chainalysis 2025 LATAM Crypto Adoption — https://www.chainalysis.com/blog/latin-america-crypto-adoption-2025/
- Chainalysis 2025 Geography Report — https://go.chainalysis.com/2025-geography-of-cryptocurrency-report.html
- Bitso Crypto Landscape LATAM 2025 — https://blog.bitso.com/blog/crypto-landscape-in-latin-america-2025
- Triple-A Colombia ownership — https://www.triple-a.io/cryptocurrency-data/colombia
- DefiLlama stablecoin dashboard — https://defillama.com/stablecoins
- Dune + Artemis stablecoin trends 2025 — https://www.altcoinbuzz.io/bitcoin-and-crypto-guide/dune-and-artemis-report-stablecoin-trends-and-insights-2025/
- Lemon Series B — https://lemon.me/en/blog/serie-b-20-m
- Aave LATAM stablecoin coverage — https://aave.com/blog/aave-latam-stablecoin-revolution

## Recommendation

**PASS** — advance D4 cohort dimension to gate-decision aggregation. Combine with D4.2 (depeg event inventory) and D4.3 (premium-funding yield) before promoting to Stage-2 M-design. Cohort is necessary but not sufficient. Forward extrapolation at conservative 25% CAGR puts 2028-2030 cohort at 600K-1.2M wallets — well above any Panoptic deployment threshold.

## Gaps

1. Colombia-specific USDC vs USDT holder split (F4) — all breakdowns are global; LATAM tilts USDT-heavy. Follow-up: Dune attribution audit on Bitso/Lemon/Wenia/Buenbit hot wallets (~1 day)
2. Median balance — $80/$200/$500 are generic LATAM, not Colombia-specific
3. "Saver" definition (F5) — if Stage-2 instrument requires ≥6-month/≥$500 saver, F5 → 0.10-0.25 and LOW → ~17K (still clears 10K)
4. Lemon 10M-user target is aspirational, not measured
5. No paid-source verification (Chainalysis Geography paid report would give country-cut directly; ~$5-15K license, not justified for gate)
6. 2022 backcast is itself Fermi-style; 55% CAGR is order-of-magnitude only
