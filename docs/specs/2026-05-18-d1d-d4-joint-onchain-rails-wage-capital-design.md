# D1.D + D4 Joint Iteration — On-Chain Rails Wage→Capital Transmission

**Spec version:** v0.2 (post 2-way review autofix; 6 Critical + 12 Strong addressed; CORRECTIONS-B user-approved 2026-05-18; closure-only re-review pending)
**Date:** 2026-05-18
**Parent specs:** `2026-05-18-four-direction-gating-step-plans.md` v0.3 §0.7-§0.11
**Gate exit verdicts:** D1 G1 CONDITIONAL PASS via Direction 1.D (Path 4 salvage); D4 CONDITIONAL PASS with user-signed CORRECTIONS-A
**Anchor memos:** `memory/feedback_d1_transparency_continuation.md`, `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`, `~/learning/post-keynesian/notes/FINANCILATION.md`

---

## 1. Intent — what this iteration measures

Direct measurement of the **wage→capital transmission rate** for Colombians using on-chain crypto rails. The framework's headline (Y, M, X) triple under a single joint identity per the user's FINANCILATION framing:

```
CF_T = E_T − L_T
```

Where:
- **E_T** (D1.D side, "earnings flow") = monthly USDC+USDT inflow to Bitso/Lemon hot wallets × Colombia-share scalar
- **L_T** ("liabilities / outflow side") = COP off-ramp flow (Mento broker swaps USDC→COPm + Bitso withdrawals to CO bank accounts) + within-period spending
- **CF_T** (D4.1 side, "cumulative financial position") = USDC-saver wallet balance trajectory

**Headline quantity (per v0.2 CORRECTIONS-B revision):**
```
ρ̂_window = (Σ_t ΔCF_t) / (Σ_t E_t)      (ratio-of-means aggregate transmission proxy)
```
ρ̂ ∈ [0, ~1] is an **aggregate-level transmission proxy**, NOT a wallet-level identity. The two numerators (D1.D inflow + D4.1 wallet-balance change) are measured on *different but partially overlapping wallet sets* (30-60% intersection per Salvage-4 findings). At Phase 1, ρ̂ should be read as a **composite indicator** that conflates wage receipts, savings inflows, and speculator round-trips — NOT as the pure wage→capital ratchet rate.

**Per CR MUST-3 + RC C2 corrections:**
- Ratio-of-means is the primary aggregation. ρ_t monthly time-series is a *secondary visualization only* — it is NOT an inferential object due to denominator-blowup risk + Jensen bias on mean-of-ratios
- Phase 1 ρ̂ is a *composite* proxy; the pure wage→capital ratchet rate requires Phase 2 Layer C attribution (wage-vs-saver-vs-speculator decomposition)
- **Likely bias direction (CR strong rec)**: Phase 1 ρ̂ probably understates true wage→capital rate because (a) non-overlap external inflows inflate CF without flowing through D1.D's E_T, and (b) speculator round-trips inflate E_T without producing capital formation

This iteration is a **demonstration-grade** Stage-1 test: does the on-chain rail empirically exhibit a nontrivial ρ̂ that responds to macro-risk shocks (COP/USD vol, USDC depeg events)? Stage-2 (M-design) and Stage-3 (deployment) remain downstream — **firewall**: no Stage-2 implementation work occurs inside this iteration (CLAUDE.md stage-drift discipline + RC S4).

## 2. Population scope (transparent per §0.8 standing rule)

**In scope (15-35% of broader cohort):** Colombian-resident wallets that deposit USDC/USDT to tagged Bitso/Lemon hot wallets across {Ethereum, Polygon, Tron, Base, Arbitrum} and/or interact with Mento broker on Celo. Anchor: Bitso 1 `0x58b704065b7aff3ed351052f8560019e05925023`.

**Out of scope (60-85% of broader cohort, not measurable here):**
- USD-paid Colombian remote workers who receive USD via Wise / Payoneer / Mercury / bank wire and never touch on-chain (largest residual)
- Cash USD held offshore indefinitely
- Direct fiat USD bank accounts in CO (where allowed)
- USDC holders who never deposit to Colombian exchanges (e.g., self-custody only)

**Transparency disclosure (per §0.8):**
1. *Data we need*: monthly USDC/USDT inflow + outflow at Bitso/Lemon (Colombia-attributable); USDC-saver wallet balance trajectories; Banrep services-credit USD; COP/USD spot; USDC/USDT spot
2. *Data we actually have*: free Dune subgraph queries for all on-chain; free Banrep services-credit quarterly + COP/USD spot daily; CryptoCompare/Kraken free USDC daily 2020-01 → 2026-04
3. *Gaps*: (a) Colombia-attribution via 20% scalar with 10-35% sensitivity (no per-deposit country tag); (b) Layer C wage-vs-speculator attribution deferred to Phase 2; (c) cash/wire USD invisible; (d) pre-2020 USDC has no Kraken-direct USD market
4. *Possible outcomes — INCLUDING NON-RETIREMENT*:
   - PASS: ρ_t estimable with sign + significance + magnitude floor
   - PARTIAL-PASS: ρ_t estimable but only at coverage-scalar-conditional confidence
   - FAIL: ρ_t indistinguishable from zero (composite stablecoin inflow doesn't track Banrep services-credit USD)
   - **NON-RETIREMENT**: data quality insufficient to discriminate PASS / PARTIAL / FAIL; iteration closes as "data-blocked" without manufacturing a clean verdict — this is an honest acceptable outcome, NOT a license to threshold-tune

## 3. Anti-fishing invariants (NON-NEGOTIABLE per `feedback_pathological_halt_anti_fishing_checkpoint.md`)

- **N_MIN = 75** monthly observations (panel runs 2020-01 → 2026-04 = N=76, satisfied structurally)
- **POWER_MIN = 0.80** for E_T → CF_T regression (D1.D side)
- **POWER_MIN = demonstration-grade** for USDC depeg β (D4.1 side, USDC N=1 + USDT N=14 pooled prior per CORRECTIONS-A)
- **MDES_SD = 0.40** (β-magnitude floor in SD-units of Δlog Y)
- All pre-pin fields (sign, magnitude, lag, primary spec, inference, power, HALT) declared BEFORE any data is touched (§4)
- HALT chain fires on any spec-vs-data contradiction: disposition memo + user-enumerated pivot + CORRECTIONS block + post-hoc 3-way review

### 3.1 Multiple-testing protection (CR MUST-4 + RC S3 — v0.2 lock)

**Single-primary commitment per estimand**:
- D1.D side: ONE primary spec (§4.1 below); sensitivity arms judged via **sign-concordance only**, NOT independently inferential
- D4.1 side: ONE primary GPD POT fit at u=$0.99 (§4.2); pooled-vs-USDT-only is a sensitivity arm, not a parallel test
- Joint ρ̂: ONE primary aggregation (ratio-of-means over full window); regime conditionals are *exploratory only* and labeled as such in every notebook output

**Bonferroni-equivalent posture**: any "secondary" or "sensitivity" finding requires the primary to also clear its threshold; secondary cannot rescue a primary FAIL.

**Banned moves**: post-hoc selection of "favorable" sensitivity arm; cherry-picking a regime where ρ̂ crosses a threshold; re-running on a sub-window to recover a signal that the full window doesn't show.

## 4. Pre-pin (anti-fishing locked; values below are commitments, not estimates)

### 4.1 D1.D side — wage receipt panel (CR MUST-1 + RC C3 corrections)

**v0.2 revisions to address spurious-regression risk + spline-interpolation autocorrelation:**

| Field | Value (v0.2) |
|---|---|
| Y | `Δlog(Bitso/Lemon USDC+USDT inflow × Colombia-share scalar)` monthly — **first-differences as primary** to avoid non-stationarity (Granger-Newbold) |
| X (PRIMARY, promoted) | `Δlog(spot_COP_USD)` monthly, 21-day average — daily public data, no interpolation needed |
| X (SECONDARY, demoted) | Banrep services-credit USD **quarterly only** (not interpolated). Used as upper-bound validation per RC C3 |
| Stationarity gate (PRE-DATA) | ADF + KPSS on log(Y), log(X). If both non-stationary AND not cointegrated (Engle-Granger), drop log-level spec and use Δ-spec primary. Threshold: ADF p<0.05 OR KPSS p>0.05 for stationarity claim |
| Sign | β > 0 (Δlog Bitso inflow co-moves with Δlog COP/USD spot — depreciation episodes → more cohort USDC receipt) |
| Magnitude floor | β ≥ 0.10 (elasticity SD-units of Δlog Y) |
| Lag | Contemporaneous primary; k=0-1 months secondary; k>3 BANNED |
| Primary specification | `Δlog(Y_t) = α + β·Δlog(spot_COP_USD_t) + ε_t`, monthly, HAC L=⌊T^(1/3)⌋ |
| Auxiliary spec (CR strong rec) | Same with γ on additional FX-vol covariate; estimated separately for sensitivity (γ≠0 vs γ=0 specs as two arms) |
| Colombia-share scalar | 20% (sensitivity arms: 10% / 35%) — scalar is constant, doesn't bias β; only re-scales magnitude of E_T |
| Banrep quarterly cross-check | Aggregate Y to quarters; check Δlog(Y_Q) sign correlation with Δlog(Banrep_services_credit_Q). Sign-concordance only (RC S3); not an inferential test |
| HALT trigger (PRIMARY) | β CI contains zero at α=0.10 two-sided IN PRIMARY SPEC → FAIL (sensitivity arms cannot rescue per §3.1) |

### 4.2 D4.1 side — USDC depeg tail β (CR strong rec on pooled-vs-USDT arm)

| Field | Value (v0.2) |
|---|---|
| Y | `Y_depeg_t = (usdc_price_t − 1) × balance_t × spot_COP_USD_t` (compound-Y decomposed) |
| X | USDC/USDT spot deviation from 1.0000, daily; peaks-over-threshold u=$0.99 |
| Sign | β > 0 on POT exceedance indicator |
| Magnitude floor | Tail-distance-from-peg ≥ 1.0% on at least one historical episode (March-2023 satisfies at 12.6%) |
| Lag | Contemporaneous (depeg is intraday); k=0 only |
| **Primary GPD fit** | USDC-only fit at u=$0.99; report N_exc, ξ̂, σ̂, profile-likelihood CI honestly with N_exc=1 caveat |
| **Sensitivity arm A (CR strong rec)** | Pooled USDC+USDT+DAI fit at u=$0.99 (per CORRECTIONS-A user-signed); reports ξ̂=0.18 prior expectation |
| **Sensitivity arm B (CR strong rec)** | USDT-only fit at u=$0.99 (D4.2 found ξ̂=0.018 — empirically diverges from pooled by ~10×) |
| Bayesian posterior (per CORRECTIONS-A) | ξ ~ Normal(0.03, 0.10²) truncated [-0.2, 0.5] USDT-derived prior; σ ~ LogNormal centered on 0.009 pooled-derived. Updated with USDC-only N=1 observation |
| Inference | GPD MLE for each arm; profile-likelihood CI; jackknife on event subset |
| Power floor | Demonstration-grade per CORRECTIONS-A (signed) |
| **Multiple-testing protection** | All 3 arms reported; only primary (USDC-only) is inferential. Posterior is the headline. Arms A/B are sign-concordance-only sensitivity (per §3.1) |
| HALT trigger | Fermi cohort fails OR genuine-event count <2 across USDC+pooled prior → FAIL |

### 4.3 Joint transmission ratio ρ̂ (CR MUST-2 + MUST-3 + RC C1 + C4 corrections — v0.2 major rewrite)

**Resolution of joint-identity wallet non-overlap (CR MUST-2 / RC C1)**: Path **(B) aggregate-with-bias-disclosure** selected. ρ̂ is a *population-aggregate transmission proxy*, NOT a wallet-level identity. D1.D inflows and D4.1 wallet-balance changes are measured on different (30-60% overlapping) wallet sets; the aggregate identity `CF = E - L` holds at the *balance-sheet population* level only with explicit bias disclosure per §1.

| Field | Value (v0.2) |
|---|---|
| **Primary estimand** | `ρ̂_window = (Σ_t ΔCF_t) / (Σ_t E_t)` — **ratio-of-means** over the full window (RC C1 / CR MUST-3) |
| **Numerator (ΔCF)** | Aggregate USDC balance change in {Colombian-resident USDC-holder wallet population, D4.1 cohort} in month t. Population identified via Bitso/Lemon CEX-deposit-address proxy + Mento COPm holdership + 20% Colombia-share scalar |
| **Denominator (E)** | Aggregate CEX inflow to {Bitso, Lemon} hot wallets in month t × 20% Colombia-share scalar |
| Sign | ρ̂ ≥ 0 (population aggregate; cohort cannot collectively decumulate while receiving) |
| **Magnitude floor (RC C4)** | Floor REMOVED from v0.1. No pre-specified ρ̂ ≥ 0.05 threshold (undertheorized — RC C4 found no derivation). Verdict criteria in §7 are sign + significance + sensitivity-arm sign-concordance only, NOT magnitude-threshold |
| Off-ramp decomposition (CR strong rec) | `ρ̂_window = 1 − off_ramp_ratio − consumption_ratio + external_inflow_ratio + residual`. `off_ramp_ratio` measured from Mento broker volume + Bitso CO-bank withdrawals; `consumption_ratio` unobserved (residual proxy); **residual term explicit** — partition is NOT a clean identity (CR strong rec). **Residual sign expectation (RC N-NEW-3)**: residual ≥ 0 expected at panel mean (unmeasured external inflows dominate unmeasured leakage). If realized residual < −0.10 at panel mean, HALT with disposition memo (measurement error suggests cohort definition is wrong) |
| **Aggregation HALT** | `\|ρ̂_window\| > 1.5` → HALT with disposition memo (measurement error or wallet-set non-overlap dominates; identity has broken down) |
| **Denominator floor** | If `Σ_t E_t < $10M` (below Mento COPm total supply scale of $65K × 10× × N=76 months), HALT with disposition memo — panel is too thin to measure aggregate transmission |
| **Secondary visualization (NOT inferential)** | `ρ_t = ΔCF_t / E_t` monthly time-series, with denominator floor `E_t > 0.05 × max(E_t)` to suppress blowups. **For descriptive plotting only**; no inferential claim attached |
| **Regime conditional** | Pre-pinned regimes: (i) "calm" = COP/USD 30d realized vol < median; (ii) "stress" = COP/USD 30d realized vol ≥ p75; (iii) "depeg" = months containing ≥1 USDC depeg event ≥0.5%. Reported as exploratory secondary, NOT inferential (per §3.1 multiple-testing) |
| **Bias direction disclosure** | Phase 1 ρ̂ likely **understates** true wage→capital rate due to: (a) non-overlap external inflows boost CF without flowing through D1.D's E_T; (b) speculator round-trips inflate E_T without producing capital formation. Pure wage→capital rate requires Phase 2 Layer C attribution |
| **Coverage-scalar asymmetry (CR strong rec)** | Colombia-share scalar appears in **both** E_T and ΔCF (consistently 20%); ratio-of-means estimator is INVARIANT to the scalar at population aggregate level. Caveat: if D1.D and D4.1 cohorts have different Colombia-share rates, ratio depends on scalar-ratio. Sensitivity arms test 10/10, 20/20, 35/35, and asymmetric 20/35 + 35/20 |

## 5. Data sources + provenance

### 5.1 On-chain (Layer A — primary)

| Source | Coverage | Method |
|---|---|---|
| Dune free tier | Bitso/Lemon hot-wallet USDC+USDT inflow + outflow, monthly, {ETH, Polygon, Tron, Base, Arbitrum} | SQL against `tokens.transfers` filtered by destination ∈ tagged CEX set |
| Celo subgraph | Mento broker USDC↔COPm swap events; cCOP/COPm holder counts | The Graph |
| Etherscan + hildobby | Bitso/Lemon address tagging verification | Public API |
| CryptoCompare `histoday` | USDC/USDT/DAI daily 2018-09 → 2026-05 on Kraken | Free tier 100K req/mo |
| Kraken native OHLC | Intraday SVB-window finer resolution | No auth, 720-bar rolling |

### 5.2 Macro anchors (Layer B — secondary)

| Source | Coverage | Method |
|---|---|---|
| Banrep BoP services-credit | Quarterly 2018-Q1 → 2025-Q4. **NOT interpolated** (RC C3 / MUST-1). Used quarterly-only as upper-bound validation against §4.1 quarterly cross-check; never as monthly regressor | `suameca.banrep.gov.co` |
| Banrep TRM (COP/USD spot) | Daily 2018-01-01 → 2026-04-30 | `fetch_banrep.py` (existing) |
| Banrep CoE (compensation of employees) | Quarterly, used as sanity-check upper bound NOT as Y | `informeBOP2025XX.pdf` |

### 5.3 Fermi cohort anchors (Layer C — context only, NOT regressors)

D4.1 5-factor Fermi (already-computed):
- LATAM crypto users 70-130M (Chainalysis 2025)
- CO share 5-8.5% (Chainalysis, Triple-A, Bitso)
- Stablecoin holder rate 40-70% (Chainalysis, Bitso)
- USDC share 12-30% (Artemis, CoinGecko)
- Active rate 25-60%
→ Cohort 42K-1.4M wallets (LOW-HIGH), GM=242K. AUM central ≈ $48M.

### 5.4 Reproducibility tier (per CLAUDE.md three-tier discipline)

- **Tier 1 (HuggingFace processed panels)**: final joint panel `data/panels/d1d_d4_joint_panel.parquet` with `(month, E_t, CF_t, off_ramp_ratio_t, rho_t, X_t, depeg_event_indicator_t)`
- **Tier 2 (raw on-chain pulls)**: Dune SQL outputs + CryptoCompare daily JSONs in `data/raw/onchain/`
- **Tier 3 (panel-builder)**: `simulations/d1d_d4_joint/panel_builder.py` re-derives Tier 1 from Tier 2

## 6. Notebooks plan (trio discipline per `feedback_notebook_trio_checkpoint.md` + `feedback_notebook_citation_block.md`)

Six notebooks, each with mandatory (why-markdown → code-cell → interpretation-markdown) trio + decision-citation block + **data-quality disclosure block** per §0.8 transparency condition:

| # | Notebook | Purpose | Trio HALT? |
|---|---|---|---|
| 01 | `01_data_eda.ipynb` | Inflow/outflow panel construction; coverage diagnostics; Colombia-scalar sensitivity sweep | YES |
| 02 | `02_d1d_inflow_beta.ipynb` | β estimate for D1.D side (Bitso USDC inflow vs Banrep services-credit) | YES |
| 03 | `03_d4_depeg_gpd.ipynb` | USDC+USDT+DAI pooled GPD POT fit; jackknife CI; sensitivity across 3 priors | YES |
| 04 | `04_joint_transmission_rho.ipynb` | Joint ρ_t estimate; off-ramp decomposition; regime-conditional analysis | YES |
| 05 | `05_sensitivity.ipynb` | Coverage-scalar sweep (10%/20%/35%); cohort-definition stress; Layer C placebo | YES |
| 06 | `06_verdict.ipynb` | PASS/PARTIAL/FAIL/NON-RETIREMENT verdict consolidation; LaTeX write-up scaffold | YES |

**Mandatory transparency block in every notebook** (new requirement per §0.8):
- *What data was used* (concrete file paths + row counts + dates)
- *What gaps remain* (acknowledged limitations carrying forward to interpretation)
- *What this notebook does NOT claim* (negative-result disclosure)

## 7. Verdict criteria (collectively exhaustive per RC C4; population scope per RC S5)

**Per RC C4 — verdict criteria rewritten to be collectively exhaustive and removed the undertheorized ρ̄ ≥ 0.05 floor (no derivation existed).** All four verdict rows now carry an explicit **population-scope clause** (RC S5) reminding the reader that ρ̂ measures the on-chain crypto-rail-paid sub-cohort (15-35% of broader USD-paid CO remote-worker cohort).

| Verdict | Headline trigger | Population scope reminder |
|---|---|---|
| **PASS** | (a) D1.D β > 0 sig at α=0.05 in primary Δ-spec; AND (b) D4.1 GPD posterior (USDC-only with USDT-prior update) excludes ξ ≤ -0.1 at 90% credible; AND (c) ρ̂_window > 0 with sensitivity-arm sign-concordance (≥4 of 5 scalar combos agree); AND (d) stationarity gate passed OR Δ-spec used | Result applies to crypto-rail sub-cohort only (15-35% of broader cohort); off-rail wage flows invisible |
| **PARTIAL-PASS** | (a) D1.D β > 0 sig in primary but ≥1 sensitivity arm reverses sign; OR (b) ρ̂_window > 0 but sensitivity-arm concordance breaks (3 of 5); OR (c) D4.1 USDC-only posterior fails ξ exclusion but pooled-prior posterior passes | Same as PASS + sensitivity flag indicates coverage-scalar dominance over the signal |
| **FAIL** | (a) D1.D β CI contains zero in primary spec; OR (b) ρ̂_window ≤ 0 or > 1.5; OR (c) D4.1 USDC-only AND USDT-only AND pooled all fail ξ exclusion; OR (d) cointegration test rejects AND Δ-spec also fails | Result implies on-chain rail is NOT a measurable wage→capital transmission channel under public-data constraints |
| **NON-RETIREMENT** (honest data-blocked per §0.8 standing rule) | Coverage gaps prevent discrimination between PASS/PARTIAL/FAIL; Layer C ambiguity dominates; OR data quality issues block ≥1 of (D1.D, D4.1, ρ̂); OR cohort identification fails Colombia-share-scalar magnitude-agreement check (RC S1 — 20% scalar deviates >2× from independent triangulation) | Iteration closes without verdict; lesson preserved for future iterations |

**Collective exhaustiveness check** (RC C4): every (β-sign, ρ̂-sign, GPD-ξ-exclusion, data-availability) state maps to exactly one verdict row. Edge cases (PARTIAL on one estimand + PASS on another) resolve to PARTIAL-PASS by precedence.

## 8. M-sketch (Stage 2 — ideal-scenario per CLAUDE.md staging discipline)

**STAGE-2 FIREWALL (RC S4)**: this section is descriptive only. NO M-sketch position is implemented, simulated, deployed, or sized within this iteration. The iteration's verdict (PASS/PARTIAL/FAIL/NON-RETIREMENT) depends solely on §4-§7 estimands. M-sketch is preserved here to demonstrate stage-correctness (β-existence on Y_t → M-design downstream) but explicitly forbidden from execution within this iteration's notebooks. Stage 2 work begins only after a PASS or PARTIAL-PASS verdict triggers a separate downstream spec.

**Cohort-wallet perspective per §0.1 convention. NOT implemented in this iteration; sketched for downstream Stage-2 work only.**

### 8.1 D1.D side — wage-receipt FX hedge
- **Position**: long-COPm / short-USDC on Mento `USDC/COPm` Panoptic pool
- **Sizing**: notional = expected next-period USDC inflow (rolling 3-month avg)
- **Rationale**: cohort is naturally long-USD at wage receipt; long-COPm offsets COP appreciation risk that would erode COP-converted purchasing power
- **Premium funding**: from USDC supply yield on collateral

### 8.2 D4.1 side — savings retention depeg hedge
- **Position**: long-tail OTM put on USDC, 25-delta (K≈$0.97-0.98 at σ=5%)
- **Pool**: USDC/USDT or USDC/DAI v3, **0.01% fee tier** (per §0.10.a)
- **Collateral**: aUSDC or sUSDS (per §0.10.b)
- **Tenor**: Panoptic perpetual; notional 1-month analogue
- **HALT trigger**: σ > 10% (7-day realized) → suspend roll, hold convex payoff (per §0.10.c)

### 8.3 Joint deployment alignment
Both positions would deploy on the **same on-chain infrastructure** used to measure the panel (Bitso/Lemon CEX flows + Mento USDC/COPm pool + Panoptic perpetuals). Measurement and deployment channels are **co-located on the same protocol stack** — narrows the typical measurement-vs-deployment gap (CR NIT-6: not "identical"; co-location ≠ wallet-set identity).

## 9. Sub-package scaffold (per CLAUDE.md three-tier discipline)

```
simulations/d1d_d4_joint/
├── types/                  # Value tier: frozen-dc parameter containers + Protocols
│   ├── panel.py            # OnchainInflowRow, JointPanelRow, ρ_t result types
│   ├── depeg.py            # DepegEpisode, GPDFitResult types
│   └── transmission.py     # TransmissionRatio, OffRampDecomposition types
├── modules/                # Callable tier: frozen-dc + __call__ stateless transforms
│   ├── inflow_aggregator.py    # CEX-tagged transfers → monthly inflow series
│   ├── colombia_scalar.py      # Apply 20%/10%/35% scalars
│   ├── off_ramp_decomp.py      # Mento broker + Bitso withdrawals → off_ramp_ratio
│   ├── rho_compute.py          # ρ_t = ΔCF_t / E_t with regime conditioning
│   └── gpd_pot.py              # POT exceedances + MLE fit + pooled prior posterior
├── utils/                  # IO Boundary tier: class-with-__init__; mutable state HERE only
│   ├── dune_io.py              # Dune SQL execution + result parsing
│   ├── cryptocompare_io.py     # CryptoCompare histoday fetcher
│   ├── banrep_io.py            # Banrep services-credit + TRM (extend existing fetch_banrep.py)
│   └── panel_io.py             # Tier 1 parquet emit/read
└── tests/
    ├── unit/                   # Hypothesis property tests on types + modules
    └── integration/            # Tier 3 round-trip; end-to-end panel build
```

Tier-import discipline: types/ ↛ modules/utils; modules/ ↛ utils. Composition over inheritance (except Protocol + Exception + private Pydantic BaseModel for utils/json_io + TypedDict for utils/parquet_io row schemas).

## 10. 3-week execution plan (per gate_decision.md Path 4 sketch)

| Week | Tasks |
|---|---|
| **1** | Dune query bundle for Bitso/Lemon CEX inflow+outflow monthly panel; verify against published Bitso 2024 totals; Mento broker subgraph queries; CryptoCompare USDC/USDT/DAI daily pulls + GPD POT fitter |
| **2** | Banrep services-credit reconciliation + COP/USD TRM pull (existing); cohort-share scalar derivation + 3 sensitivity arms; pre-pin spec memo; Tier 3 panel-builder implementation |
| **3** | Notebook 01-06 execution per trio discipline; HALT-checkpoint trio review; PASS/PARTIAL/FAIL/NON-RETIREMENT verdict; LaTeX write-up scaffold |

## 11. Cross-references + dependencies

- **Parent spec**: `docs/specs/2026-05-18-four-direction-gating-step-plans.md` v0.3 §0.7-§0.11
- **D1 G1 gate**: `scratch/2026-05-18-direction-1-g1-gating/gate_decision.md`
- **D4 gate**: `scratch/2026-05-18-direction-4-gating/gate_decision.md`
- **D4.2 GPD data + scripts**: `scratch/2026-05-18-direction-4-gating/02_depeg_events/data/`
- **Standing rules**: `memory/feedback_d1_transparency_continuation.md`, `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`, `memory/feedback_notebook_trio_checkpoint.md`, `memory/feedback_notebook_citation_block.md`
- **Reuses existing**: `scripts/fetch_banrep.py` (TRM + BoP), `simulations/dev_ai_cost_v2/jsonl_io.py` patterns
- **Stage-2 reference**: spec §0.10 M-design conventions; §0.1 cohort-wallet perspective

## 12. Pre-implementation 2-way review

Per `feedback_three_way_review.md` adapted for spec-only (no implementation yet) review:
1. **Reality Checker** — data feasibility, anti-fishing posture, transparency-condition compliance, joint-identity econometric coherence
2. **Code Reviewer** — methodology rigor, identification gaps, pre-pin sufficiency, joint-model specification, transmission-ratio econometrics

Verdicts roll up to spec v0.2 amendments before any implementation begins.

## 13. CORRECTIONS-B block (user-approved 2026-05-18, v0.2 autofix-all)

Per CR MUST 1-4 + RC C1-C4 findings, the following amendments are user-approved per autofix-all directive 2026-05-18 and binding for v0.2:

**MUST-1 / RC C3 — Spurious-regression risk closure**:
- Δ-spec (first-differences) is PRIMARY (§4.1)
- COP/USD spot daily promoted to PRIMARY X; Banrep services-credit demoted to quarterly validation only
- Stationarity gate (ADF + KPSS) declared as pre-data gate; cointegration test as fallback condition
- Spline interpolation REMOVED

**MUST-2 / RC C1 — Joint identity wallet non-overlap closure**:
- Path (B) aggregate-with-bias-disclosure adopted (§1, §4.3)
- ρ̂ explicitly framed as *population-aggregate transmission proxy*, NOT wallet-level identity
- Bias direction disclosed: Phase 1 ρ̂ likely understates true wage→capital rate

**MUST-3 / CR — Ratio-estimator instability closure**:
- Ratio-of-means (Σ ΔCF / Σ E) is PRIMARY aggregation (§4.3)
- ρ_t monthly time-series demoted to secondary visualization only with denominator floor
- Second HALT trigger added: \|ρ̂_window\| > 1.5 triggers disposition memo
- Denominator-floor HALT: Σ E_T < $10M triggers disposition memo

**MUST-4 / RC S3 — Multiple-testing protection closure**:
- New §3.1 with single-primary commitment per estimand
- Sensitivity arms = sign-concordance only, NOT independently inferential
- Bonferroni-equivalent posture: secondary cannot rescue primary FAIL

**RC C2 — Layer C bias direction on ρ closure**:
- §1 framing downgraded: ρ̂ is "composite indicator" at Phase 1, not "wage→capital ratchet rate"
- Pure rate requires Phase 2 Layer C attribution (deferred, not promised)
- Bias direction disclosure added to §1 + §4.3

**RC C4 — Verdict criteria exhaustiveness closure**:
- §7 rewritten as collectively exhaustive 4-row matrix
- ρ̄ ≥ 0.05 floor REMOVED (was undertheorized — no derivation existed)
- Population-scope clause added to every verdict row per RC S5

**Strong recommendations (12) integrated inline**:
- CR: COP/USD γ≠0 and γ=0 specs as sensitivity (§4.1); pooled-vs-USDT-only as sensitivity arm (§4.2); off-ramp decomposition has explicit residual term (§4.3); coverage-scalar 3.5× swing documented (§4.3); Tier 2 frozen Dune snapshots required (§5.4 below)
- RC: Colombia-scalar magnitude-agreement check (§7 NON-RETIREMENT trigger); pre-2020/COVID regime-break test deferred to notebook 05 sensitivity; Stage-2 firewall sentence in §8; population-scope clause in every verdict row (§7); pre-data D1.D × D4.1 aggregation matrix declared in §4.3

**Tier 2 frozen-snapshot requirement (CR strong rec)**: Dune query SQL + materialized result snapshot (parquet) BOTH committed to `data/raw/onchain/snapshots/YYYY-MM-DD_<query>.{sql,parquet}`. Dune query state can change; snapshot ensures reproducibility.

**Stationarity gate ADF/KPSS p-value threshold pre-pin**: ADF null=non-stationary, p<0.05 ⇒ stationary; KPSS null=stationary, p>0.05 ⇒ stationary. BOTH must agree for log-level spec. If they disagree OR ADF fails to reject, Δ-spec primary.

**User signature on CORRECTIONS-B**: implicit per "autofix all Critical and High" directive 2026-05-18.

## 14. Open items for closure re-review

1. ~~Colombia-share scalar coverage~~ — addressed (§4.3 5-arm sensitivity)
2. ~~Quarterly→monthly spline~~ — REMOVED per MUST-1 (COP/USD spot is primary X)
3. ~~Joint identity wallet non-overlap~~ — closed per MUST-2 (aggregate-with-bias-disclosure)
4. ~~Layer C deferral~~ — closed per RC C2 (downgraded ρ̂ framing to composite indicator)
5. ~~Pre-2020 USDC gap~~ — closed as known epoch limitation; explicit in §2 transparency disclosure
6. ~~CORRECTIONS-A already signed~~ — remains user-approved; v0.2 adds CORRECTIONS-B without re-litigating A
7. **NEW (for closure review only)**: are the 5 coverage-scalar sensitivity arms (10/10, 20/20, 35/35, 20/35, 35/20) sufficient to cover the asymmetric-scalar bias case (CR strong rec), or should we add a 6th arm at independent priors?
8. **NEW**: stationarity-gate threshold (ADF p<0.05 AND KPSS p>0.05) — is the AND-conjunction too restrictive? Spec adopts conservative AND; reviewer flag if should be OR.

## 15. Anti-fishing closure

This spec inherits anti-fishing carry-forward from spec v0.3 §0.8 transparency condition + `feedback_pathological_halt_anti_fishing_checkpoint.md`:
- All pre-pin fields declared above BEFORE data is touched
- HALT chain fires on any spec-vs-data contradiction
- NON-RETIREMENT is an honest outcome; threshold tuning to manufacture PASS is BANNED
- Coverage-scalar sensitivity arms (10%/20%/35%) are committed; post-hoc selection of the "favorable" arm is BANNED
- "Composite stablecoin inflow" Phase 1 framing is locked; cherry-picking wage-only subset post-hoc is BANNED

Spec v0.1 closes here. Awaiting 2-way review.
