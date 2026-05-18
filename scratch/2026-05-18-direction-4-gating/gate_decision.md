# Direction 4 — Colombian USDC-Saver Cohort — Gate Decision

**Status:** IN PROGRESS (dispatched 2026-05-18)
**Spec anchor:** `docs/specs/2026-05-18-four-direction-gating-step-plans.md` §Direction 4 (v0.2)
**Effort:** 5 working days (extended from 3), public-data + Fermi method only

## Gating question (revised per D4-RC)

Can a 5-factor Fermi-bound estimate of the Colombian USDC-holder cohort yield ≥10K wallets, AND have ≥2 genuine USDC depeg episodes occurred with tail-distance-from-peg sufficient to identify a long-tail option payoff?

## Pre-pin (locked, anti-fishing per spec §0.2)

| Field | Value |
|---|---|
| Sign | β > 0 for `Y_depeg = (usdc_price − 1) × balance × spot_COP_USD` regressed on depeg indicator |
| Magnitude floor | Tail-distance-from-peg ≥ 1.0% on at least one historical episode |
| Lag | Contemporaneous (depeg is intraday); k=0 only |
| Primary specification | Peaks-over-threshold GPD with u = $0.99 (1% below peg); secondary: empirical-CDF tail |
| Inference | GPD MLE with profile-likelihood CI; jackknife on event subset |
| Power floor | Demonstration-grade only (genuine event N ≤ 5 mechanically rules out 0.80); requires user CORRECTIONS block to proceed |
| HALT chain | If Fermi fails OR genuine-event count < 2, return FAIL without further analysis |

## Pass criteria

- Fermi cohort estimate (5-factor): low-bound ≥10K wallets
- Genuine depeg episode count (≥1.0% tail-distance, ≥1-day persistence): ≥2 events
- Native USDC supply yield (Aave/Compound history): sufficient to cover hedge premium

## Fail criteria

- Fermi low-bound <1K wallets
- <2 genuine depeg episodes (excluding microstructure noise)
- Native yield insufficient to fund premium-ratchet

## Sub-tasks (parallel)

| ID | Investigation | Output |
|---|---|---|
| D4.1 | 5-factor Fermi cohort estimate with current public anchors | `01_fermi_cohort/findings.md` |
| D4.2 | USDC/USDT depeg event inventory + GPD POT preparation | `02_depeg_events/findings.md` |
| D4.3 | USDC supply yield history (Aave/Compound) for premium funding | `03_premium_yield/findings.md` |
