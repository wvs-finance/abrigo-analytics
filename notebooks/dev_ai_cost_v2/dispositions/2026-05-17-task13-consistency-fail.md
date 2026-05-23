# Task 13 HALT Disposition — R4-S3-COP CONSISTENCY-FAIL

**Date:** 2026-05-17
**Trigger:** `notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb` k=1 primary and k=5 sensitivity both fired CONSISTENCY-FAIL on the production panel `data/panels/notional_cost_panel.parquet` (29 rows; HEAD `11e238d`; 1.000000× ccusage parity post-v0.2.7 Y-9 closure).
**Verdict labels (per spec §2.2.A):** `{CONSISTENCY-PASS, CONSISTENCY-FAIL}` only.
**Spec citation:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.7 §2.2.A lines 1212–1234; §0.1 CORRECTIONS-S; §0.1 CORRECTIONS-I (HAC bandwidth ⌊T^(1/3)⌋).

## What happened

The R4-S3-COP arm was specified as a **consistency check** under the v0.2.5 expectation
that `|Δln NotionalCost^COP|` is dominated by `|Δln USDCOP|` (spec §2.2.A lines
1222–1230). Both pre-pinned lag specifications fired FAIL:

| Spec | T_lag | HAC L | α̂₁^COP | HAC SE | t | p_1s (α₁>0) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| k=1 primary | 27 | 3 | **−17.977387** | 40.268154 | −0.4464 | 0.670360 | CONSISTENCY-FAIL |
| k=5 sensitivity | 23 | 2 | **−35.887636** | 30.540578 | −1.1751 | 0.873118 | CONSISTENCY-FAIL |

Per pre-pinned verdict logic (§2.2.A lines 1232–1234), the primary verdict is the k=1
result: **CONSISTENCY-FAIL**. Pre-data pins (LAG_PRIMARY=1, LAG_SENSITIVITY=5,
HAC_LAGS=⌊T^(1/3)⌋, ALPHA_LEVEL=0.05 one-sided, TOKENS_PROXY=`output_tok`) were
declared in Cell 2 BEFORE data read and were NOT tuned post-hoc.

## Root-cause diagnosis — NOT data corruption

The spec §2.2.A FAIL handler reads: *"A consistency-fail HALTs the pipeline (suspect
data corruption), not the framework."* Investigation rules out data corruption:

### 1. Cost-panel additive identity holds exactly

```
max | Δln NotionalCost^COP_t − (Δln NotionalCost^USD_t + Δln USDCOP_t) | = 1.78e-15
```

The multiplicative construction `NotionalCost^COP_t = NotionalCost^USD_t · USDCOP_t`
is exact to machine precision (29 rows, all dates). This rules out the panel-builder
joining the wrong TRM to the wrong day or applying TRM in level rather than rate
form. Same identity check passed in `02_r5_descriptive.ipynb` Trio 1 (cited there
as confirming "panel's multiplicative construction is internally consistent").

### 2. Y-9 closure means cost data is verified at 1.000000× ccusage parity

Per `memory/project_dev_ai_cost_v2_y9_closure.md` (post-PR#4 HEAD `11e238d`), the
cost-data parser is verified at 1.000000× ccusage parity (UTC apples-to-apples).
This rules out parser-divergence as a source of LHS contamination.

### 3. Contemporaneous (lag 0) correlations are the expected sign

```
corr( |Δln Cost^COP|_t , |Δln USDCOP|_t  ) = +0.103
corr( |Δln Cost^COP|_t , |Δln Tokens|_t  ) = +0.743
```

The FX series enters the LHS with the correct sign at lag 0 (additive identity
guarantees this). The token process dominates contemporaneously (corr 0.74 vs 0.10),
which is consistent with Task 12 R5's headline FX share of 0.000028 — token vol
is ~36,000× larger than FX vol in variance contribution to `|Δln Cost^COP|`.

### 4. The FAIL is at lag 1 (and lag 5), NOT at lag 0

```
corr( |Δln Cost^COP|_t , |Δln USDCOP|_{t-1} ) = -0.074
corr( |Δln Cost^COP|_t , |Δln Tokens|_{t-1} ) = -0.042
```

Both *lagged* regressors enter slightly negative (statistically indistinguishable
from zero). This is the actual source of the FAIL: the spec's §2.2.A regression
asks for FX vol *at lag t−k* to predict LHS vol at t, but the additive identity
the FAIL-handler text implicitly relies on is *contemporaneous* — it does not
mechanically propagate to the lagged regressor under low FX share.

## Why the FAIL fires under the v0.2.7 panel — spec-premise mismatch

The §2.2.A FAIL handler ("suspect data corruption") implicitly assumes the
arithmetic chain:

1. `NotionalCost^COP_t = NotionalCost^USD_t · USDCOP_t` (additive identity in logs).
2. *Therefore* `|Δln Cost^COP|` is dominated by `|Δln USDCOP|` (spec §2.2.A line 1225).
3. *Therefore* lagged `|Δln USDCOP|_{t−1}` should predict `|Δln Cost^COP|_t` via
   vol-clustering persistence on the FX series.

Step (1) is true and verified. Step (2) is **false on the v0.2.7 panel**: Task 12
(R5) measured FX share = **0.000028** of `Var(Δln Cost^COP)` — the USD-side
(token volume) dominates variance by ~36,000:1. With FX contributing 0.003% of LHS
variance, no lagged FX vol-clustering signal can survive HAC SE at T=27.

In other words, the spec wrote the FAIL handler text under the assumption that
the LHS would inherit substantial FX-vol content (suggesting α̂₁^COP would
mechanically be positive and significant via mere arithmetic propagation). The
empirical Task-12 measurement of FX share = 0.000028 contradicts this assumption
and explains why the lagged FX regression does **not** mechanically deliver a
positive coefficient.

## Scope — which Y-9-closed data branch this affects

**None.** The FAIL does not falsify any cost-data branch:

- `notional_cost_cop`, `notional_cost_usd`, `trm_cop_per_usd`: additive identity
  holds to 1.78e-15 (passes Trio 1 algebraic check, identical to 02_r5_descriptive
  Trio 1).
- `output_tok`: tokens-proxy enters with finite, non-zero magnitudes and contributes
  the bulk of contemporaneous LHS variance (corr 0.74 at lag 0 — sign and order
  of magnitude as expected).
- Y-9 closure (1.000000× ccusage parity): verified upstream; no implication for
  this FAIL.

The FAIL is a **spec-text vs. empirical-fact mismatch**, not a data-pipeline failure.

## Anti-fishing — what is NOT done here

- **No retro-fitting** of LAG_PRIMARY (e.g., trying lag 0 or lag 2 post-hoc) — pins
  declared PRE-DATA and stand.
- **No swap** of TOKENS_PROXY (post-hoc reaching for `input_tok` or
  `cache_create_5m` would be silent fishing — the largest-token-class rationale
  was pre-pinned).
- **No switch** to two-sided test (the one-sided α₁^COP > 0 alternative is
  pre-pinned per §2.2.A line 1220).
- **No widening** of ALPHA_LEVEL.
- **No adjustment** of HAC bandwidth (⌊T^(1/3)⌋ rule per CORRECTIONS-I is pinned).
- **No mechanical continuation to Task 14** (R4-S3-USD behavioral arm) — this
  disposition memo is the gate.

## User-enumerated pivot options (REQUIRES USER DECISION)

Per `feedback_pathological_halt_anti_fishing_checkpoint.md`, when a HALT fires the
disposition memo enumerates pivot options and the user picks. The Claude agent
does NOT silently pick one. Options:

### Option A — Amend spec §2.2.A FAIL-handler text in v0.2.8

Replace the "suspect data corruption" language with the empirically-grounded:
*"CONSISTENCY-FAIL under the v0.2.7 panel reflects that the empirical FX-share
of LHS variance (≈ 0.000028, per Task-12 R5) is too small for the lagged FX
regressor to deliver a statistically detectable positive coefficient at T=27.
The additive identity (multiplicative-construction integrity) is verified
independently in Trio 1; pipeline-integrity is therefore confirmed by the algebraic
check, not by the regression."* This makes the R4-S3-COP arm's pipeline-integrity
verdict rely on the Trio 1 additive-identity check (which PASSED at 1.78e-15)
rather than the OLS sign-and-significance check (which FAILED due to the low
FX-share empirics R5 already measured). Then re-issue verdict as PASS-via-identity.

### Option B — Proceed to Task 14 (R4-S3-USD) under explicit "consistency arm spec-mismatch documented" footnote

Treat the CONSISTENCY-FAIL as documented and proceed to the framework-relevant
arm (R4-S3-USD). Cite this disposition memo + the additive-identity verification
as the actual pipeline-integrity evidence. Task 14 verdict (PASS/FAIL on the
two-sided test of α₁^USD) is independent of R4-S3-COP per CORRECTIONS-S.

### Option C — HALT to spec-review session

Convene a spec review specifically on §2.2.A FAIL-handler logic. Determine
whether the empirical FX-share measurement from R5 fundamentally changes whether
R4-S3-COP can serve as a pipeline-integrity check at all (and if not, whether
the additive-identity Trio 1 check supersedes it as the canonical pipeline
integrity gate).

### Option D — Block downstream tasks pending Y-10+ analysis

Treat the FAIL as a genuine signal that something else in the panel is off (despite
the additive-identity passing), and convene a Y-10-style review.

## Recommendation (Claude — for user decision)

Option **A or B**. The additive-identity verification (1.78e-15) is the cleanest
direct pipeline-integrity check; the lagged OLS was a noisy indirect proxy that
empirically cannot fire under low-FX-share data, as already measured by R5. The
v0.2.5/v0.2.7 spec §2.2.A FAIL-handler text appears to predate the R5 empirical
finding (FX share = 0.000028) and over-promised mechanical OLS positivity. Options
C and D require user time but are not warranted by the data; the FAIL is fully
explained by the empirical FX-share already measured in Task 12.

## CORRECTIONS block

This disposition memo will be referenced in the v0.2.8 spec amendment if Option A
is chosen. Pin: do NOT silently re-run Task 13 with different pins or
alternative tokens-proxies; if Option A is chosen, the v0.2.8 spec edit makes
the verdict source explicit (additive-identity Trio 1) and Task 13 is re-run
once with the amended verdict logic.

## Files

- Notebook (frozen, FAIL committed honestly):
  `notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb`
- Spec section under review: `docs/specs/2026-05-16-ai-cost-factor-model-design.md`
  v0.2.7 §2.2.A lines 1212–1234.
- Related R5 finding (FX share = 0.000028 with 90% CI [−0.000003, 0.000041]):
  `notebooks/dev_ai_cost_v2/02_r5_descriptive.ipynb` Trio 4.
- Anti-fishing protocol: `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`.
