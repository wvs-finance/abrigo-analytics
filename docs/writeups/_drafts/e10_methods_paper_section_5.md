# §5 — Detecting Q-Dominance Ex-Ante for Streamed-Liability Convex Hedges: An FX-Variance-Share Sensitivity Surface Methodology

**Iteration:** E10 GSPS (v0.7).
**Date:** 2026-05-21.
**Posture:** descriptive only — calibration-conditional; no inferential β claim is made.
**Companion LaTeX export:** `docs/writeups/e10_gsps_methods_paper_section_5.{tex,pdf}` (the LaTeX export is the canonical artifact; this markdown is a stripped draft kept for non-LaTeX consumers).

---

## Abstract

We propose a methodology for detecting, ex-ante and from public-source data, whether a streamed-liability convex hedge addresses the dominant variance vector of a target cohort's cost stream. The methodology is built around an exact three-way log-variance decomposition of the cost-stream identity `Cfx_t · p · Q_t` into FX, Q, and covariance components on a common daily gapped grid; an FX-variance-share sensitivity surface evaluated on a log-spaced grid across an anchored Q-volume range; and a six-input collectively-exhaustive descriptive verdict ladder consuming surface, material-gap, simulator-anchored, Q-variance-dominance, interior-crossing, and data-visibility flags. The methodology emits one of **SURFACE-PRODUCED**, **PARTIAL**, or **NON-RETIREMENT**. Applied to the E10 representative Web3 data-analyst cohort over a 5-currency panel (COP, BRL, EUR, GBP, NGN; 150 monthly cells; 2023-11 to 2026-04), the empirical FX-variance share sits ≈ 3.21 decades below the ex-ante-pinned break-even `s_be = 0.25` at every grid point on the anchored `[28, 130]` queries/month range; all five pre-committed sensitivity arms remain concordant; the verdict is **NON-RETIREMENT subtype `q_dominance`**. The methodology contribution survives the specific verdict.

---

## §5.1 — Motivation and contribution claim

The construction step for permissionless on-chain convex hedges — how to size, price, and statically replicate a convex payoff (Panoptic / Maymin) — has matured. What has not matured is the **detection** step that must precede construction: does the cohort's cost-stream variance actually load on the variance vector the proposed instrument prices?

This section contributes a methodology for **detecting Q-dominance ex-ante** from public-source data alone. Under Q-dominance the variance of the cohort's stochastic activity intensity Q dominates the FX leg in the cost-stream log-variance decomposition; a convex FX hedge addresses the wrong variance vector for the cohort. The contribution is the detection step — it is independent of, and survives, any particular cohort's verdict.

Throughout we adopt a **descriptive** posture: no inferential β claim is made, no p-value is computed, no null hypothesis is rejected. The objects emitted are surfaces, decompositions, and verdict classifications under a stated calibration; they are read against ex-ante-pinned thresholds.

---

## §5.2 — Setup and assumptions

- **A1 (cohort).** The cohort pays a continuous-stream liability of the form `C_t = Q_t · p · FX_t`, where Q_t is daily query volume (an x402-priceable activity intensity), p is a verified flat unit price (E10: $0.01 USDC per query, x402-protocol-verified), and FX_t is the daily local/USD rate from a sovereign central bank.
- **A2 (data anchors).** Q_t is empirically anchored to a NON-FANTASY observed trace (E10: 214 genuine Claude Code tool calls; daily VMR ≈ 20). FX panels come from free public central-bank feeds (Banrep COP, BCB BRL, ECB EUR, BoE GBP, CBN NGN).
- **A3 (panel construction).** Balanced `(currency × month)` panel on a daily gapped grid: zero-Q days dropped on the same surviving index for X and Q (forced by the log domain — `Δlog(0)` is undefined). E10: 5 × 30 = 150 cells; window 2023-11-01 → 2026-04-30. NGN confined to post-June-2023 float regime.
- **A4 (descriptive-only posture).** No inferential β claim. The methodology emits a calibration-conditional sensitivity surface; the verdict ladder reads the surface against an ex-ante-pinned break-even.
- **A5 (ex-ante break-even).** Threshold `s_be` pinned ex ante from option-premium economics against an ex-ante exposure assumption. E10: `s_be = 0.25` derived from ATM long-straddle / variance-swap geometry, ideal-scenario fair pricing (`c_payoff = 1`), pinned premium fraction `φ = 0.25`; firewall preserved.

---

## §5.3 — The three-way log-variance decomposition

The methodology's load-bearing identity is the exact additive decomposition of cost-stream log-variance.

Take the natural log of A1's cost identity and first-difference on the surviving (positive-Q) index:

> `Δlog C_t = Δlog Q_t + Δlog FX_t`

(p is a constant additive offset that drops out under Δ.) Applying the population variance operator `Var(z) = mean(z²) − (mean z)²` on the surviving index yields the exact additive identity:

> **`Var(Δlog C) = Var(Δlog FX) + Var(Δlog Q) + 2 · Cov(Δlog FX, Δlog Q)`**

This is exact — no leading-order term, no remainder. It holds cell-by-cell because `log C_b − log C_a = (log Q_b − log Q_a) + (log FX_b − log FX_a)` for any pair of strictly-positive (Q, FX, C) days.

**Empirical residual (E10).** Maximum `|identity_residual|` across 150 panel cells: **1.33 × 10⁻¹⁵** — machine-precision zero. Source: `notebooks/e10_gsps/diagnostics/E10.2_decomposition_summary.json`.

**The FX-variance share** is `s = Var(Δlog FX) / Var(Δlog C)`. Three properties: (i) calibration-conditional (FX numerator real, Q denominator simulator-derived); (ii) the level-variance object `Var(C)` has no clean additive split and is banned from s; (iii) under negligible cross-covariance the complementary `Var(Δlog Q)/Var(Δlog C) ≈ 1 − s` is a useful diagnostic, but the ladder consumes only s.

---

## §5.4 — The FX-variance-share sensitivity surface

The surface is a calibration-conditional descriptive object evaluated on a log-spaced grid across an anchored Q-volume range `[Q_low, Q_high]` (E10: `[28, 130]` queries/month, set from the NON-FANTASY observed-trace centre and bracketed by proxy research).

- **Grid spec.** 50 log-spaced points across the anchored range; adaptive doubling to 100 if any cell falls within ±0.5 dex of `s_be`. (E10: adaptive doubling not triggered — empirical share > 3 decades below `s_be`.)
- **Honest disclosure — panel-mean broadcast.** For E10 the empirical share is approximately invariant in Q-volume across the anchored range. The implementation broadcasts the panel-mean share to every grid point and emits an `is_panel_mean_broadcast` flag so consumers cannot mistake the surface for an estimated Q→s mapping. A kernel-smoothed Q-dependent surface would be a natural follow-up.
- **Q-variance dominance flag (dual form).**
  - Share form (classifier-consumed): `q_dom_flag_share = 1{s(Q) < s_be for all Q in [Q_low, Q_high]}`.
  - Spec form (descriptive sibling): `q_dom_flag_spec = 1{Var(Δlog Q)/Var(Δlog C) > 1 − s_be for all Q}`.
  - Equivalent when `|Cov(Δlog FX, Δlog Q)|` is small relative to `Var(Δlog Q) + Var(Δlog FX)` — the operative case under A2.
- **Interior-crossing rule.** `≥ 3` contiguous strictly-interior cells with `s < s_be`; endpoints excluded. Semantic guard: at least one endpoint must clear (`s ≥ s_be`); a surface entirely below `s_be` is Q-variance dominance, not interior crossing.

---

## §5.5 — The §9 verdict ladder

Six inputs: `dv_gate_passed`, `simulator_anchored`, `surface_computed`, `material_gap`, `q_variance_dominates`, `interior_crossing`.
Outputs: `SURFACE-PRODUCED`, `PARTIAL`, `(NON-RETIREMENT, subtype)` with subtype ∈ `{dv_fail, simulator_unanchored, q_dominance}`.

The ladder (locked ex ante; collectively exhaustive over 2⁶ = 64 flag states):

1. If `¬dv_gate_passed` → `(NON-RETIREMENT, dv_fail)`.
2. Else if `¬simulator_anchored` → `(NON-RETIREMENT, simulator_unanchored)`.
3. Else if `¬surface_computed ∧ material_gap` → `PARTIAL`.
4. Else if `¬surface_computed` → `(NON-RETIREMENT, q_dominance)`.
5. Else if `q_variance_dominates` → `(NON-RETIREMENT, q_dominance)`.
6. Else if `material_gap` → `PARTIAL`.
7. Otherwise → `SURFACE-PRODUCED`.

The classifier carries a separate inferential-emit method that **unconditionally raises** `DescriptiveVerdictError` — a structural firewall enforcing A4 at the code level. There is no PASS rung and no FAIL-on-β rung.

---

## §5.6 — Sensitivity arms and the no-rescue clause

Five arms are pre-committed before any panel data is touched:

- **Arm (b) — Q–FX coupling.** Pinned monthly-scalar coupling `Q_coupled = Q · (1 + η·z_month)` with elasticity `η = −0.3`. Under the user-pinned monthly-scalar operationalization, a constant scalar drops out of daily `Δlog Q`; arm (b) is thus an **algebraic-identity assertion** that the within-month decomposition is unchanged at the cell level, **not** a coupled-daily re-simulation. Concordance metric is exactly zero by construction; reported transparently.
- **Arm (c) — NGN regime-break removal.** Drops NGN cells inside the ±6-month buffer around 2023-06-01.
- **Arm (d) — GBM / JD comparator.** Substitutes empirical `Var(Δlog FX)` by GBM and Merton-JD per-currency comparators calibrated to the panel-mean; preserves `Var(Δlog Q)` and the covariance term.
- **Arm (e) — Per-currency split.** Reports min/Q1/median/Q3/max envelope; uses the median for concordance.
- **Arm (f) — Q_high extended.** Extends upper Q-range bound to the $390 Dune-cap equivalent.

**No-rescue clause (load-bearing).** *Sensitivity arms cannot rescue a primary HALT.* No arm can flip a primary `NON-RETIREMENT` verdict to `SURFACE-PRODUCED`. The clause is constructor-pinned and hard-coded on the aggregate result type.

---

## §5.7 — E10 application and results

### Table 1 — Data provenance (5 Tier-2 frozen central-bank snapshots)

| Currency | Central bank / endpoint | Payload SHA-256 (head) | Bytes | Daily rows |
|---|---|---|---:|---:|
| COP | Banrep TRM (datos.gov.co Socrata `32sa-8pi3`) | `861be2848592affa` | 70,741 | 590 |
| BRL | BCB Olinda OData PTAX `CotacaoDolarPeriodo` | `ba75a914696af794` | 58,379 | 627 |
| EUR | ECB Data Portal SDW `EXR/D.USD.EUR.SP00.A` | `9cd19cf85ac11200` | 132,350 | 635 |
| GBP | BoE IADB series `XUDLUSS` | `378df39672a4cca0` | 12,573 | 631 |
| NGN | CBN Gateway `/api/GetAllExchangeRates` | `e61225c8f8fdd854` | 7,987,807 | 617 |

Window: 2023-11-01 → 2026-04-30 (30 calendar months; 150 panel cells). NGN confined to post-June-2023 float. ZAR/KES/GHS dropped at the data-visibility gate (no free machine-readable daily ~30-month series). x402 per-query price `$0.01 USDC` re-verified live.

### Table 2 — Seven pre-pinned methodology fields

| # | Field | Value |
|---|---|---|
| 1 | Sign expectation | β > 0 on vol-on-vol; necessary-not-sufficient *descriptive* gate |
| 2 | Primary spec | FX-variance-share sensitivity surface + ex-ante-pinned `s_be`; not a β magnitude |
| 3 | Material threshold | `s_be = 0.25`; ex-ante from option-premium economics (`s_exp = 0.25`, `φ = 0.25`, `c_payoff = 1`) |
| 4 | Lag | Contemporaneous, monthly |
| 5 | Posture | Descriptive / illustrative; demonstration-grade-or-below; NOT confirmatory |
| 6 | Panel & FE | 5 currencies × 30 months = 150 cells; two co-primary FE specs (two-way; currency-only); G ≈ 5 clusters |
| 7 | HALT condition | HALT on (a) simulator unanchored, (b) Q-variance dominance over whole range → NON-RETIREMENT, (c) surface uncomputable, (d) any spec-vs-data contradiction |

### Table 3 — §9 verdict-classifier inputs and outcome

| Flag | Value | Source |
|---|---|---|
| `dv_gate_passed` | True | `E10.0_panel_window.json` |
| `simulator_anchored` | True | `E10.1_calibration_note.md` (214 calls; VMR ≈ 20) |
| `surface_computed` | True | `E10.3_surface_summary.json` |
| `material_gap` | False | `E10.3_surface_summary.json` |
| `q_variance_dominates` | True | `E10.3_surface_summary.json` |
| `interior_crossing` | False | `E10.3_surface_summary.json` |

**Resulting verdict: NON-RETIREMENT subtype `q_dominance`** (rung 5 of the ladder).

### Figure 1 — FX-variance-share surface vs ex-ante break-even
`docs/writeups/figures/e10_figure1_surface_vs_break_even.pdf` — panel-mean surface (≈ 1.535 × 10⁻⁴) ~3.21 decades below `s_be = 0.25` on the `[28, 130]` Q-range; 5-currency min/max + IQR envelope shaded. **DESCRIPTIVE / CALIBRATION-CONDITIONAL.** NOT a confidence interval. NOT an inferential band.

### Figure 2 — Per-currency FX-variance share (5-currency spread)
`docs/writeups/figures/e10_figure2_currency_spread.pdf` — EM (BRL/COP/NGN) vs DM (EUR/GBP); NGN largest (≈ 5.97 × 10⁻⁴), GBP smallest (≈ 2.10 × 10⁻⁵); all two-to-four decades below `s_be`. **NON-STATISTICAL spread.** NOT a confidence interval.

### Table 4 — Sensitivity-arm concordance summary

| Arm | Concordance metric | q_dom | Verdict | Panel-mean share |
|---|---:|:---:|---|---:|
| (b) Q–FX coupling | 0.000 | True | concordant | 1.535 × 10⁻⁴ |
| (c) NGN break-window | 4.04 × 10⁻⁵ | True | concordant | 1.131 × 10⁻⁴ |
| (d) GBM / JD comparator | 3.41 × 10⁻⁵ | True | concordant | 1.876 × 10⁻⁴ |
| (e) Per-currency split | 9.43 × 10⁻⁵ | True | concordant | 5.922 × 10⁻⁵ |
| (f) Q_high extended | 2.71 × 10⁻²⁰ | True | concordant | 1.535 × 10⁻⁴ |

### Headline numerics

- Vol-on-vol regression: `β̂_two-way = +68.151` (currency FE + month FE), `β̂_currency-only = +54.715` (currency FE only, co-primary).
- Descriptive gap: `+13.436`; sign concordance preserved (both signs +1); magnitude differential ~20% of the smaller coefficient. Descriptive sign gate of pre-pin field 1 holds. The gap is interpretive content for the §13 M-sketch hedge-sizing step (idiosyncratic vs global FX-vol exposure load).
- Panel-mean FX-variance share `s̄ = 1.535 × 10⁻⁴` across 150 cells; ≈ 3.21 decades below `s_be = 0.25` at every grid point on `[28, 130]`.
- All five sensitivity arms concordant.

**Verdict: NON-RETIREMENT subtype `q_dominance`.**

---

## §5.8 — Interpretation (post-Keynesian theoretical frame)

*Interpretive prose only — explicitly labeled. Not a hypothesis test; does not predict the verdict post-hoc. Calibration-conditional reading: all four bullets are interpretive prose for the configuration in pre-pin fields 1–7.*

The Bhaduri–Laski–Riese (BLR) virtual-vs-real dichotomy frames financialization as a structural gap between the virtual economy (asset valuation, financial-cycle volatility) and the real economy (output, productive investment). The Minsky two-price theory formalizes the gap between `P_k` (asset-side demand price) and `P_i` (output-side supply price). The Kaleckian investment-driven growth tradition insists investment, not asset revaluation, is the prime mover of output.

The E10 representative Web3 data-analyst cohort is one whose cost-stream is bound to its own activity intensity (Q, the own-output / `P_i` side) rather than to virtual-economy price volatility (FX, the `P_k` analog). Under the calibration in A2 on the `[28, 130]` anchored Q-range, the empirical FX-variance share sits ≈ 3 decades below the ex-ante break-even — the convex FX hedge addresses the wrong variance vector for this cohort:

- **BLR virtual-vs-real:** The convex FX hedge prices into the virtual-economy price-volatility vector (`P_k` analog); the cohort's cost-stream variance is structurally bound to the real-economy production decision (the analyst's Q scheduling).
- **Minsky two-price:** The instrument prices into the `P_k` gap but the cohort's exposure lives on the `P_i` side.
- **Kaleckian:** The cohort's cost-stream variance reflects effective-demand-driven activity intensity, not asset-revaluation flow.
- **Methods-paper hook:** The detection methodology survives the specific verdict — it correctly routes this (cohort, instrument) pair to NON-RETIREMENT subtype `q_dominance` from public-source data alone; the trail is auditable end-to-end.

The verdict is not a bug of the data and not a failure of the convex hedge instrument family; it is a finding about the (cohort, instrument) pair.

---

## §5.9 — Methodology contribution survives the verdict

The contribution is the **methodology**, not the specific E10 verdict. The methodology successfully identifies:

(a) a cohort whose cost-stream variance is Q-dominated under a NON-FANTASY simulator anchor and a frozen ex-ante break-even (A2, A5);
(b) an instrument (the convex FX hedge) that addresses the wrong variance vector for that cohort, with the dominance gap quantified at > 3 decades below the ex-ante threshold;
(c) the verdict ladder routing this (cohort, instrument) pair to NON-RETIREMENT subtype `q_dominance`;
(d) an auditable trail — Tier-2-frozen central-bank data with payload-SHA-256 provenance sidecars; NON-FANTASY simulator anchor against 214 observed tool calls; the exact §5.3 identity at machine precision; an ex-ante-pinned break-even derived before any decomposition runs.

The methodology is venue-publishable as a stand-alone §5 of a methods paper at **Cambridge Journal of Economics**, **Review of Political Economy**, or **Metroeconomica** independent of the specific E10 verdict. Companion sections of the methods paper apply analogous detection methodologies to alternative (cohort, instrument) pairs (E8 dTAO/Maymin; E9 LATAM RWA) and are reported separately.

---

## §5.10 — Limitations and future iterations

Honest disclosures:

- **Q–FX coupling arm (b) is an algebraic-identity assertion** under the user-pinned monthly-scalar operationalization — a coupled-daily re-simulation is the natural extension.
- **The FX-variance-share surface is panel-mean-invariant in Q for the E10 calibrated simulator.** The implementation broadcasts the panel-mean and emits the `is_panel_mean_broadcast` flag; a kernel-smoothed Q-dependent surface would be a natural follow-up.
- **`G = 5` currency clusters is structurally thin.** Cluster-robust inference at `G = 5` is size-distorted; we report descriptive sign and non-statistical min–max / IQR spreads only. Bootstrap-based bands were considered and dropped at this G in spec v0.6 (CORRECTIONS-E10-6).
- **Arm (d) GBM/JD calibration is per-step rather than monthly-aggregate.** The deflation does not flip the verdict but is reported here for transparency.
- **`_MIN_SURVIVING_DAYS = 2` in the cell-decomposition function is methodologically degenerate** at n = 2; benign for E10 (all 150 production cells have ≫ 3 surviving days); future amendment raises to 3.
- **Ideal-scenario premium** (`c_payoff = 1`, `φ = 0.25`): no FX-stablecoin options venue with real depth exists in 2026; a real venue would impose `c_payoff < 1` and lift `s_be` above 0.25. The frozen `s_be = 0.25` is the ideal-scenario lower bound.
- The methods-paper §5 hook is robust across alternative cohort/instrument pairings (E8, E9 are companion sections).

---

## References

- Abrigo Analytics (2026). E10 GSPS v0.7 — `docs/specs/2026-05-20-e10-gsps-v0.7-convex-multicurrency-design.md`.
- Bhaduri, A. & Marglin, S. (1990). Unemployment and the Real Wage. *Cambridge Journal of Economics*, 14(4).
- Bhaduri, A., Laski, K. & Riese, M. (2006). A Model of Interaction between the Virtual and the Real Economy. *Metroeconomica*, 57(3).
- Cox, D. R. (1955). Some Statistical Methods Connected with Series of Events. *JRSS-B*, 17(2).
- Kalecki, M. (1971). *Selected Essays on the Dynamics of the Capitalist Economy 1933–1970*.
- Lambert, G., Lyons, J. & Jiao, J. (2022). Panoptic. arXiv:2204.14232.
- Maymin, P. (2026). A CEV-based Process for AMM Tokens. arXiv:2603.29763.
- Merton, R. C. (1976). Option Pricing when Underlying Stock Returns are Discontinuous. *J. Financial Economics*, 3.
- Mento Labs (2024). Mento Protocol.
- Minsky, H. P. (1975). *John Maynard Keynes*.
- Tymoigne, E. (2010). Minsky's Two-Price Theory of Investment. Levy Working Paper.
- x402 Working Group (2025). x402 protocol specification (Linux Foundation).

---

*E10 GSPS §5 methods-paper draft — markdown stripped-version of the LaTeX export — closes here.*
