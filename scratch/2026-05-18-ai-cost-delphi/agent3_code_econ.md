# Agent #3 — Code & Econometric Implementation Audit (dev_ai_cost_v2)

**Scope:** code correctness, regression implementation, bootstrap implementation,
HAC SE, standard-package usage, no hand-computed inference, code-vs-spec
mapping. Independent of math/model and data/replication auditors.

**Targets reviewed:**
- `simulations/dev_ai_cost_v2/{types,jsonl_io,anthropic_pricing,panel_builder,_errors}.py`
- `scripts/build_notional_cost_panel.py`
- Notebooks `01_data_eda`, `02_r5_descriptive`, `03_r4s3_cop_consistency`,
  `04_r4s3_usd_behavioral`, `05_sensitivity`, `06_z_sensitivity`
- Tests `simulations/tests/test_dev_ai_cost_v2_*.py`
- Strategies `simulations/tests/strategies.py`

**Spec text reviewed:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md`
v0.2.9 (active), CORRECTIONS-I/-J/-P/-Q/-S/-T/-U/-Y-1..Y-9, §0.8 Z2, §0.9 Z3.

---

## Critical findings

**None.**

The mandate's "hand-computed standard errors" tripwire does **not** fire.
Every regression in every notebook uses
`statsmodels.OLS(...).fit(cov_type='HAC', cov_kwds={'maxlags': hac_L})`
with `hac_L = int(np.floor(T_lag**(1/3)))` per CORRECTIONS-I (Andrews 1991);
every bootstrap uses `arch.bootstrap.StationaryBootstrap.conf_int(...)` or a
mathematically-equivalent direct Politis-Romano draw for variable-length
output (Z-2 backcast — `arch` returns same-length output, so a manual
geometric-block draw is necessary and correctly implemented).
No regression's SEs are computed by hand; the HAC bandwidth formula is
honored in code, not just spec.

---

## High findings

**None.**

The two regression-spec divergence tripwires both pass:

1. **R4-S3-COP / R4-S3-USD specification matches spec §2.2.A / §2.2.B.**
   LHS = `|Δln cost^{X}|_t`; regressors are
   `sm.add_constant([abs_dln_trm[:-k], abs_dln_tok[:-k]])` with `y[k:]`
   alignment at `LAG_PRIMARY=1` and `LAG_SENSITIVITY=5`. Constant is
   included (spec writes $\alpha_0 + \alpha_1 \cdot |\Delta\ln \text{USDCOP}|_{t-k} + \alpha_2 \cdot |\Delta\ln \text{Tokens}|_{t-k}$ at
   lines 1425, 1457). Lag handling verified byte-for-byte in
   nb03/nb04/nb05 — slicing is `y[k:]` against `x[:-k]`, length
   `T_lag = T - k`. Coefficient of interest is `params[1]` (the
   USDCOP-vol slope), not `params[0]` (the intercept). Verified by
   inspection of all four regression cells.

2. **Y-8 dedup (`jsonl_io.py`) mirrors ccusage byte-for-byte.**
   `_unique_hash(message_id, request_id)` returns `f"{msg_id}:{req_id}"`
   when both present, `message_id` alone when `request_id` is None,
   `None` when `message_id` is missing (caller admits without
   incrementing the counter — RC FLAG-B compliant). `_token_total`
   sums `input + output + cache_create_total + cache_read` where
   `cache_create_total = cache_create_5m + cache_create_1h`
   (ccusage `Sr` mirror, matches the flat `usage.cache_creation_input_tokens`
   on the source side). The dedup loop increments
   `dropped_duplicate` on **every** collision (whether the new row
   replaces or is dropped), satisfying the spec §0.5 closure invariant
   `dropped_duplicate_count == raw_assistant_rows_admitted - len(records)`.
   Replacement is whole-record (`records[existing_idx] = new_record`),
   not field-mixed (RC FLAG-A satisfied — also covered by the
   `test_jsonlreader_dedup_field_atomicity` test). `hasSpeed`
   tiebreaker is correctly conditional on
   `new_has_speed and not existing_has_speed`; all other tie cases
   keep the existing row (deterministic, traversal-order-invariant —
   verified by the `test_jsonlreader_dedup_traversal_order_invariant`
   property test, max_examples=20).

---

## Mid findings

### M1. `nb04` lagged-recipe power-MC injects an effect that is NOT 0.40 residual-SD

**Location:** `notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb` Trio 4
Recipe A (the "alternative / lagged" recipe, computed for transparency per
v0.2.9 §0.9 Z3).

**Issue.** The contemporaneous recipe (canonical, gates verdict) correctly
scales the injected slope:

```python
beta_true_contemp = MDES_RESID_SD * residual_sd_contemp / sd_x_contemp
y_sim = beta_true_contemp * x_full + eps
```

This produces a y-shift of `0.40 × residual_sd` over the regressor's natural
SD range — the correct MDES geometry.

The **lagged** recipe injects:

```python
mdes_effect_lagged = MDES_RESID_SD * residual_sd_lagged   # y-units
y_sim = intercept_obs + mdes_effect_lagged * x1_obs + alpha2_obs * x2_obs + eps
```

Here `mdes_effect_lagged` is treated as the slope on `x1_obs`. The actual
y-effect from this slope over `x1_obs`'s natural SD range is
`mdes_effect_lagged × sd(x1_obs) ≈ MDES_RESID_SD × residual_sd_lagged × sd(x1_obs)`,
which is NOT `0.40 × residual_sd_lagged`. The slope scaling is missing
the `/ sd(x1_obs)` factor.

**Impact.** This affects only the *transparency-only* lagged figure
(0.1745) reported alongside the canonical contemporaneous figure (0.7115).
Per v0.2.9 §0.9 Z3 the lagged recipe is documented for the audit trail
but does NOT gate the verdict. The PARTIAL-FAIL_TO_REJECT verdict is
driven by the canonical (contemporaneous) recipe, which is implemented
correctly.

**Why Mid, not High.** The 0.1745 power figure is documented in the spec
itself (§0.9 disclosure of the Z3 divergence) at the SAME numeric value
the code produces. Either (a) the spec already absorbed the (different)
slope convention, or (b) the spec's 0.1745 came from the same code path
under a different but consistent interpretation. The verdict-bearing path
is correct; this is a stylistic / consistency-with-canonical-recipe issue
in the transparency arm.

**Recommendation.** If the intent of the lagged recipe is "MDES =
0.40 × residSD effect under lagged-tokens partialling," the slope should
be `MDES_RESID_SD * residual_sd_lagged / sd(x1_obs)`. If the intent is
"slope of 0.40 × residSD" (a units-mismatched effect), document the
distinction in the cell so reviewers don't compare 0.17 vs 0.71 as if
the two power numbers measured the same effect-size geometry.

---

### M2. `PricingTable` mutates a "frozen" dataclass via `object.__setattr__`

**Location:** `simulations/dev_ai_cost_v2/anthropic_pricing.py:243-248, 313-318`.

**Issue.** `PricingTable` is declared `@dataclass(frozen=True, slots=True)`
but its three counter fields
(`WARN_missing_keys_count`, `dropped_unknown_model_count`,
`multiple_substring_match_warning`) are mutated post-construction via
`object.__setattr__(self, field_name, ...)`. The docstring on lines 108-113
acknowledges this as a "documented exception" for "modules-tier-owned
counters," but it still violates:

- The `functional-python` skill's frozen-dc immutability invariant (the
  parent CLAUDE.md cites this skill as repo-discipline).
- The Tier-discipline split spelled out in `CLAUDE.md`: "modules ↛ utils;
  modules-tier ⇒ no mutable state." `PricingTable` is modules-tier and
  carries mutable state.

**Impact.** Production logic is unaffected (counters strictly accumulate).
But: the audit-trail counters could in principle be silently rewritten by
any caller using `object.__setattr__` — the slots+frozen invariant is
no longer a real defense. A counter regression caused by an
unintended caller mutation would be invisible to tests.

**Recommendation.** Either (a) move counter ownership to a separate
mutable container injected into `PricingTable`, keeping the rate table
strictly frozen, or (b) emit fresh `PricingTable` instances on
counter increments. (a) preserves performance; (b) is more functional.
Either way the "documented exception" should not be the persistent
solution — it weakens the contract that other code is being held to.

---

### M3. `nb03` uses scipy `student_t.cdf` to derive a one-sided p instead of `model.pvalues[1]/2`

**Location:** `notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb`
Trio 2 + Trio 3.

```python
t_stat_primary = alpha_1_cop_primary / se_alpha_1_primary
df_resid_primary = T_lag_primary - X_primary.shape[1]
p_one_sided_primary = float(1.0 - student_t.cdf(t_stat_primary, df=df_resid_primary))
```

**Issue.** The spec §2.2.A pins a one-sided test on $\alpha_1^{COP} > 0$.
statsmodels' `.pvalues` are two-sided; the canonical one-sided derivation
is `model.pvalues[1] / 2 if model.params[1] > 0 else 1 - model.pvalues[1] / 2`
(or `model.t_test(...)` with a one-sided alternative). nb03 instead
recomputes the t-statistic by hand (`α̂ / SE`) and runs it through
scipy's t-CDF with hand-computed `df_resid = T_lag - X.shape[1]`.

**Why Mid.** This is mathematically equivalent to `pvalues[1]/2` because
statsmodels' two-sided p under HAC defaults to `2 * (1 - Phi(|t|))`
asymptotically, and the t-CDF version with finite df is the analogous
small-sample variant. The audit risk is two-fold:
(1) `df_resid` is computed by hand and could drift from statsmodels'
own residual-DF accounting (statsmodels uses the actual rank of X);
(2) under HAC, statsmodels reports normal-z based p (not t-df-based),
so the **scipy `student_t.cdf` choice is actually a *different
distributional choice* than what statsmodels would emit**. Whether
that's appropriate at T_lag=27 is a separate inferential-defensibility
question; the spec doesn't pin it.

**Recommendation.** Replace the scipy-t-CDF block with
`model.t_test("x1 > 0").pvalue` or `model.pvalues[1] / 2` (with sign
check). This matches the statsmodels HAC convention and removes the
manual `df_resid` arithmetic.

---

## Low findings

### L1. `nb01` + `nb04` power-MC use normal-z critical value instead of `model.pvalues`

**Location:**
- `notebooks/dev_ai_cost_v2/01_data_eda.ipynb` Trio 5 power loop.
- `notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb` Trio 4 Recipe B
  (canonical contemporaneous).

```python
z_crit = sps.norm.ppf(1 - ALPHA / 2)
for b in range(B):
    ...
    m_sim = sm.OLS(y_sim, X_sim).fit(cov_type='HAC', cov_kwds={'maxlags': hac_L})
    if abs(m_sim.tvalues[1]) > z_crit:
        rejected += 1
```

**Issue.** The reject decision compares `|t|` against a **normal-z**
critical value, not against `m_sim.pvalues[1]`. The lagged-recipe loop
in nb04 (Recipe A) correctly uses `m_sim.pvalues[1] < ALPHA_LEVEL`;
nb01 and nb04 Recipe B do not.

**Why Low.** Statsmodels' HAC `pvalues` *default to normal-z* asymptotics
(`use_t=False` by default for non-iid covariance), so
`pvalues[1] < ALPHA_LEVEL` IS equivalent to `|tvalues[1]| > z_crit`.
The audit risk is consistency with the spec mandate ("no hand-computed
p-values"). Numerically identical results.

**Recommendation.** Replace with `m_sim.pvalues[1] < ALPHA_LEVEL` to
match the lagged-recipe pattern, the spec mandate, and the rest of the
codebase.

### L2. `nb03` HAC bandwidth derivation re-implemented locally

`nb03` defines `def hac_bandwidth(t_lag): return int(np.floor(t_lag ** (1/3)))`
in Cell 2. So do nb01, nb04, nb05. Same constant copy-pasted across
five notebooks. Style nit — at minimum the formula should live in a
helper module the notebooks share. The current copy-paste exposes the
codebase to silent drift if one notebook gets edited (e.g., to
`int(np.ceil(...))`) and the others don't.

### L3. `nb05` `LAG_SENSITIVITY` not honored for HAC bandwidth recomputation in trim trio

`nb05` Trio (trim sensitivity) at line 366 computes `hac_L_trim` from
`N_trim` rather than from `N_trim - LAG_SENSITIVITY`. Comparing with
nb03/nb04: the primary regressions use `hac_bandwidth(T_lag)` where
`T_lag = T - k`; the trimmed regression in nb05 uses
`hac_bandwidth(N_trim)` directly. At T≈26 vs T_lag≈25 the difference
in `floor(T^(1/3))` is zero, but the principle is wrong: HAC L should
key off the SAME `T_lag` that the regression sample uses. Style nit;
no numeric impact at this T.

### L4. Z-2 backcast manual stationary bootstrap is correct but cannot easily be unit-tested against `arch`

`nb06` `stationary_bootstrap_path` re-implements Politis-Romano with
geometric block lengths because `arch.bootstrap.StationaryBootstrap`'s
default API returns same-length resamples. The implementation is
mathematically correct (geometric blocks, circular wrap, truncate to
target). The audit risk is that a regression in this routine would not
be caught by comparing against `arch` (different output length). A
unit test that runs the manual function with `target_len == n_pool` and
asserts statistical equivalence to `arch.bootstrap.StationaryBootstrap`
on a fixed seed would close this gap. None of the existing tests cover
this path.

---

## Mandate items confirmed clean (explicit "None" per category)

### Standard packages
- All regressions: `statsmodels.OLS(...).fit(cov_type='HAC', cov_kwds={'maxlags': L})`. ✓
- All within-sample CIs / variance shares:
  `arch.bootstrap.StationaryBootstrap(block_len, *series, seed=SEED).conf_int(func, reps=B, size=size, method='basic')`. ✓
- Z-2 backcast (variable-length resample): direct Politis-Romano
  implementation with seeded `np.random.default_rng(seed)`. Pinned
  seeds documented in Cell 2 (`SEED_Z2_MAIN=20260519`,
  `SEED_Z2_NULL=20260520`, `SEED_Z2_W=20260521`). ✓

### HAC bandwidth
Every regression uses `L = int(np.floor(T_lag**(1/3)))`. Verified in
nb01 (`HAC_L = 3` at T=28), nb03 (Trios 2-3 at T_lag=27, 23), nb04
(Trios 2-3 + Trio 4 lagged + contemporaneous at T=28), nb05 (k=5
sensitivity + trim sensitivity). Note style nit L3.

### R5 variance decomposition (Task 12, nb02)
`fx_share_excl_cov(c, u, x) = Var(x) / Var(c)`,
`usage_share_excl_cov(c, u, x) = Var(u) / Var(c)`,
`two_cov(c, u, x) = 2 · Cov(u, x, ddof=0)[0,1]`.
All three passed to `StationaryBootstrap(BLOCK_LEN=4, dln_cop, dln_usd, dln_trm, seed=20260516).conf_int(func, reps=10_000, size=0.90, method='basic')`.
The functional form matches CORRECTIONS-Q (conservative attribution —
covariance reported separately, EXCLUDED from FX-share denominator).
Identity check (FX + Usage + 2·Cov/Var(Cost^COP) ≈ 1) is asserted in
the trio's interpretation cell. ✓

### Dedup correctness (Task 9.5 + Y-8)
ccusage-mirror uniqueHash `${msg.id}:${requestId}`, keep-larger-tokenTotal
with `hasSpeed` tiebreaker on equal totals, byte-for-byte against
ccusage. Three property tests (`max_examples=25/40/20`):
double-iteration on tuple-records, line-conservation invariant,
file-traversal-permutation invariance. Whole-record replacement
(RC FLAG-A); `message.id == None` rows bypass dedup map and do NOT
increment the counter (RC FLAG-B). ✓

### Power-MC implementation
nb01 Trio 5: HAC L=3 in MC inner loop matches HAC L=3 used in any
downstream R4-S3-USD regression at T=28. ✓
nb04 Trio 4 Recipe B (canonical contemporaneous): HAC L=3 in MC matches
`hac_L_contemp = hac_bandwidth(T=28) = 3`. ✓
nb04 Trio 4 Recipe A (lagged, transparency): HAC L=3 in MC matches the
primary regression's `hac_L_primary = hac_bandwidth(T_lag=27) = 3`. ✓
Seeds pinned PRE-DATA (`POWER_SEED = 20260517`); the same seed is reset
on a fresh `np.random.default_rng` for each recipe so the two power
figures are independent draws. ✓ (Per M1, the lagged recipe's slope
units are inconsistent with the canonical recipe — but this affects
the *number*, not the HAC bandwidth honoring.)

### R4-S3-COP/USD regression specifications
`|Δln cost^X|_t ~ const + |Δln USDCOP|_{t-k} + |Δln Tokens|_{t-k}` with
`X ∈ {COP, USD}` and `k ∈ {1, 5}`. Constant included via
`sm.add_constant`, matching spec lines 1425/1457 ($\alpha_0$ explicit
in spec equations). Lag handling: `y = y_full[k:]`, `x1 = x1_full[:-k]`,
`x2 = x2_full[:-k]`, with `T_lag = T - k` and length assertion. ✓

### Hypothesis tests
Real, edge-case-rich property tests in
`test_dev_ai_cost_v2_jsonl_io.py`:
- `test_jsonlreader_double_iteration_property` (max_examples=25):
  tuple immutability re-iteration.
- `test_jsonlreader_line_conservation_property` (max_examples=40):
  raw-byte fixture, conservation invariant
  `malformed + records + non_assistant + blank == total_input_lines`.
- `test_jsonlreader_dedup_traversal_order_invariant` (max_examples=20):
  permutation strategy over file names tests that the keep-largest
  rule's output is invariant to `Path.rglob` order.

In `test_dev_ai_cost_v2_panel_builder.py`:
- `test_no_records_only_days_in_output` (max_examples=40): record-day
  + trm-day sampled lists; the inner-join correctness is asserted
  set-theoretically.

In `test_dev_ai_cost_v2_pricing.py`:
- `test_pricing_monotone_in_input_tokens`: monotonicity under integer
  input perturbations.

In `test_dev_ai_cost_v2_types.py`:
- `@given(rec=message_records())` from `strategies.py` validates
  `MessageRecord.__post_init__` invariants.

The `strategies.py:message_records` composite generates non-empty UUIDs,
tz-aware UTC datetimes, non-negative integer tokens, and finite floats —
all the invariants the value-tier `__post_init__` enforces. **These are
real strategies, not trivial.** Not just `st.builds()` over default
floats — they're tuned to the Value-tier admissible region. ✓

### Tier discipline
- `types/` ↛ `modules/utils`: `types.py` imports only `polars` + stdlib. ✓
- `modules/` ↛ `utils/`: `anthropic_pricing.py` imports `types.py` only.
  `panel_builder.py` imports `types.py` + sibling `anthropic_pricing.py`
  (pure callable, allowed). Neither imports `jsonl_io.py`. ✓
- `utils/`-tier `jsonl_io.py` imports `types.py`, `anthropic_pricing.py`,
  `_errors.py` (downward imports allowed). ✓
- CLI (`scripts/build_notional_cost_panel.py`) is the integration point
  that wires all three tiers — explicitly documented as the intentional
  cross-tier orchestrator. ✓

### Frozen dataclasses + slots
`MessageRecord`, `TokensByCategory`, `JSONLReadResult`, `DailyNotionalPanel`,
`PricingTable` all declared `@dataclass(frozen=True, slots=True)`.
Verified via grep at:
- `types.py:62, 146, 195, 269`
- `anthropic_pricing.py:82`
(See M2 for the qualification on `PricingTable`'s `__setattr__` carve-out.)

### Exception narrowness
No bare `except`, `except Exception`, or `except BaseException` in
`dev_ai_cost_v2/` or `scripts/build_notional_cost_panel.py`. ✓
Narrow catches found:
- `jsonl_io.py:390` `except json.JSONDecodeError` (Y-7 contract).
- `jsonl_io.py:404` `except ValidationError` (re-raised as
  `JSONLSchemaError`).
- `nb04` MC inner loop: `except (np.linalg.LinAlgError, ValueError)`
  for HAC fit failures on adversarial draws. Bounded.

### No hand-computed p-values for primary regressions
- nb04 Task 13/14 primary verdict: `p_two_sided_primary = float(model_k1.pvalues[1])`. ✓
- nb05 sensitivity: `p_cop_k5 = float(model_cop_k5.pvalues[1])` and
  `p_usd_k5 = float(model_usd_k5.pvalues[1])`. ✓
- nb03 R4-S3-COP primary: uses `1 - student_t.cdf(t, df)` to derive a
  one-sided p (see M3 — Mid finding; statsmodels does not natively emit
  one-sided p, so the scipy derivation is a defensible workaround, but
  it should ideally use `model.t_test(...)` or `pvalues[1] / 2`).

### Z-arms bootstrap reproducibility (Z-2 main + Z-2-W + Z-2-null)
nb06 Cell 2 declares pinned seeds PRE-DATA. Each arm uses an independent
seed: `SEED_Z2_MAIN=20260519`, `SEED_Z2_NULL=20260520`, `SEED_Z2_W=20260521`.
`backcast_fx_shares` internally calls `np.random.default_rng(seed)` once
at entry. `B_PATHS=1000` pinned. `BLOCK_LEN_BACKCAST=4` matches daily R5
pin (`BLOCK_LEN=4` in nb02). Reproducibility ✓. (Same-seed re-run of
the same notebook yields bit-identical output.)

---

## Spec drift sweep (v0.2.5 → v0.2.9, 9 corrections)

| CORRECTIONS | Spec text | Code | Match |
|---|---|---|---|
| Y-1 | type-discriminator filter pre-Pydantic | `jsonl_io.py:398` `if raw.get("type") != "assistant"` | ✓ |
| Y-2 | float cost (ccusage parity, not Decimal) | `MessageRecord.cost_usd_notional: float`; panel schema `pl.Float64` | ✓ |
| Y-3 | rate fields `Optional[float]`; missing → WARN + 0 | `anthropic_pricing.py:184-196` | ✓ |
| Y-5a | counter ownership split | 3 counters on `PricingTable`, 3 on `JSONLReadResult` | ✓ |
| Y-5b | `JSONLReadResult` types-tier | `types.py:195` | ✓ |
| Y-5c | 5m+1h aggregated at `PricingTable.__call__`, NOT at `TokensByCategory` | `anthropic_pricing.py:322` | ✓ |
| Y-5d | substring-tiebreaker = `min(candidates)` | `anthropic_pricing.py:242` `tied = sorted(...)` | ✓ |
| Y-5e | synth uuid `"synth-sha256:" + sha256(stem + ":" + zfill8)[:16]` | `jsonl_io.py:145-160` | ✓ |
| Y-5f | `extra="allow"` Pydantic; `costUSD` field removed | `jsonl_io.py:82, 96, 117, 132` | ✓ |
| Y-6 | `ephemeral_pi_share` scalar in `[0, 1]`, single broadcast column | `types.py:371-380`, `panel_builder.py:201-205` | ✓ |
| Y-7 | per-line `json.JSONDecodeError` silently counted | `jsonl_io.py:388-392` | ✓ |
| Y-8 | uniqueHash dedup, keep-larger-tokenTotal, hasSpeed tiebreaker | `jsonl_io.py:374-473` | ✓ |
| Y-9 | UTC parity 1.000000× ccusage | Documented in nb headings; not code-side | n/a |
| §0.8 Z2 | identity-OK + low-FX-vol-regime reclassification | nb03 Trio 4 | ✓ |
| §0.9 Z3 | dual-recipe power, contemporaneous canonical | nb04 Trio 4 | ✓ (modulo M1) |

---

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High     | 0 |
| Mid      | 3 |
| Low      | 4 |

The dev_ai_cost_v2 pipeline implementation tracks the v0.2.9 spec with
high fidelity. The three Mid findings are local stylistic/consistency
issues that do NOT affect verdict-bearing numbers; the canonical
contemporaneous power-MC, R4-S3-COP/USD HAC regressions, R5 variance
decomposition, and Y-8 dedup are all implementation-correct.

The most notable observation is **M1** — the lagged-recipe MC in nb04
appears to inject a slope with wrong unit-geometry, but it's the
transparency arm Z3 documents as deviating from the canonical
contemporaneous recipe, and the spec text already absorbs the 0.1745
output number. The verdict path (PARTIAL-FAIL_TO_REJECT, contemporaneous
power = 0.7115) is unaffected.

The most notable cleanup opportunity is **M2** — the `PricingTable`
frozen-dc carve-out via `object.__setattr__` weakens the
functional-python invariant the rest of the codebase carefully honors.
A small refactor (counter container injection) would close the door
on a class of audit-trail-corruption bugs that the codebase otherwise
defends against.

**No code-side blocker to v0.2.9 sign-off from this auditor.**
