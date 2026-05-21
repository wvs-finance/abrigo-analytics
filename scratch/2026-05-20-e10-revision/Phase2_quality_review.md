# E10 Phase 2 (E10.1) — Stage-2 Code-Quality Review

**Reviewer posture:** code-quality / correctness / numerical soundness (Stage 2 of 2).
**Date:** 2026-05-20
**Scope:** `simulations/e10_gsps/modules/nhpp_engine.py`, `types/nhpp.py`,
`tests/unit/test_nhpp_engine_phase2.py` + `test_nhpp_engine.py`,
`notebooks/e10_gsps/01_simulator_calibration.ipynb` (light pass).

## Verdict

**APPROVED_WITH_NITS**

One Important finding (a dead, inverted edge-case branch that crashes on an
empty FX path) — but it is not reachable from any Phase-2 or Phase-3 call site
(panel cells always pass a full-month FX index), so it does not block Phase-2
exit. It should be fixed before Phase 3 wires real panel cells. No Critical.
The Cox/doubly-stochastic construction, the mixture sampling, the VMR mapping,
the RNG threading, and the NaN handling are all sound.

**Counts:** Critical 0 / Important 1 / Minor 4.

## Independent verification

- `pytest test_nhpp_engine_phase2.py test_nhpp_engine.py` — 19 passed.
- `scripts/e10_firewall_check.py` — PASS, 44 files clean, exit 0.
- VMR tunability sweep (`vmr_target` ∈ {5, 20, 50}, 12 simulated months):
  realized daily VMR 5.7 / 17.6 / 32.4 — monotone and tracks the target.
- Determinism: fixed seed → identical monthly series and identical cell counts;
  RNG threaded explicitly via `np.random.default_rng`, no global `np.random`.
- NaN `Q_low`: engine constructs and runs with `params.q_low = NaN`; no NaN
  leaks into `daily_cost` (Q_low is never read by the arrival/cost path).
- Tier discipline: `nhpp_engine.py` imports only `numpy`, `_errors`, `types`;
  `types/nhpp.py` imports only stdlib. Clean `modules ↛ utils`, `types ↛ modules`.

## Findings

### Important

**I-1 — `nhpp_engine.py:592` inverted empty-FX guard crashes `__call__`.**
`aligned_counts = counts[:fx_len] if fx_len else counts`. When
`daily_fx_rate` is empty (`fx_len == 0`) the `else` branch keeps the *full*
calendar counts (28-31 days) while `aligned_fx` is empty, so the
`zip(..., strict=True)` at line 596 raises `ValueError: zip() argument 2 is
shorter`. Confirmed by direct call `engine(p,'COP',2025,1,())`. The docstring
(lines 540-547) explicitly contemplates a short/empty FX path and claims
"aligned to the FX index" — the code does the opposite for the empty case.
Not reachable from Phase-2 tests or a real Phase-3 panel cell (FX always
covers the month), hence Important not Critical.
**Minimal fix:** drop the conditional — `counts[:fx_len]` already yields
`counts[:0] == ()` when `fx_len == 0`, which is the documented behaviour.
Replace line 592 with `aligned_counts = counts[:fx_len]`.

### Minor

**M-1 — VMR mapping uses envelope-mean μ, ignores between-day λ_det spread.**
`_sprint_intensity` pins σ² via `VMR = 1 + μ·σ²` with `μ = lambda_det.mean()`
(`_simulate_day_counts:437`). The day-count marginal is a *mixture over
heterogeneous* λ_det(d) (weekday vs weekend, drift, month-end), so the realized
daily VMR also carries the between-day envelope variance and is not exactly
`1 + μ̄·σ²`. This is why the sweep undershoots (17.6 for target 20). Acceptable
— the calibration note §0-A2 explicitly makes `vmr_target` a swept-range
*centre*, not a hard target — but the `_sprint_intensity` docstring (lines
308-312) states the marginal "hits `vmr_target`" more strongly than the math
delivers. Recommend softening the docstring to "approximately pins" and noting
the envelope-heterogeneity caveat.

**M-2 — `_sprint_intensity` clip floor can bias the mean off 1.**
Line 387 `np.clip(rescaled, 1e-6, None)` truncates the lower tail after the
affine rescale. For large `scale` (high `vmr_target`, low μ) the rescaled
background lower tail goes negative and is floored, which lifts the realized
mean fractionally above 1, so Λ_d no longer has mean *exactly* 1. Effect is
small at the calibrated μ≈4 / VMR≈20 but grows in the §4.3 sweep's high-VMR
corner. Consider documenting the floor as an approximation, or re-centring
post-clip if the §4.3 surface needs the mean-1 property tight.

**M-3 — `simulate_monthly_query_counts` duplicates the `_simulate_day_counts`
call site.** Lines 662-679 re-implement the calendar-walk + day-count call that
`__call__` (560-586) already does, with the engine defaults hardcoded
(`_VMR_TARGET_DEFAULT`, etc.) rather than taken from an engine instance. Two
code paths to the same simulation can drift. Consider having the monthly helper
delegate to a shared private routine, or documenting why it deliberately runs
the defaults-only process.

**M-4 — No test asserts realized VMR within tolerance of `vmr_target`.**
The 19 tests assert overdispersion (`VMR > 3.0`, `var > mean`) and that
`vmr_target` is a constructor param, but none checks that a *given*
`vmr_target` actually maps to a realized daily VMR near it (the load-bearing
M-1 mapping). `test_cox_primary_is_decisively_overdispersed` would still pass
if the VMR mapping were silently broken. Recommend one test asserting realized
daily VMR is within a generous band of two distinct `vmr_target` values, and
one asserting monotonicity (higher target ⇒ higher realized VMR). No vacuous
tests found; the existing 19 are genuine behaviour assertions.

## Confirmed sound

- **Cox construction** — `Poisson(λ_det(d) × Λ_d)` with Λ_d drawn per day then
  arrivals conditioned on it: correct doubly-stochastic order (`_simulate_day_counts`
  446-447). λ_det carries all five §6.3 slots (weekday, drift, month-end as
  multiplicative weights; burstiness+spikes as the Λ_d mixture). Arrival
  generation is direct Poisson draw on the daily grid — exact, no thinning bias.
- **Mixture sampling** — two-component (Gamma/log-normal background + sparse
  Exponential spike), Bernoulli day-marker, analytic mixture moments used for
  rescale (not a noisy per-month estimate) — correct and stable. Gamma and
  log-normal background parametrised to matched mean/variance; NB fallback
  shares the Gamma path (correct, since Gamma-mixed Poisson ⇒ NB marginal).
- **Q ⊥ FX** — `daily_fx_rate` enters only the `cost` product (594-597); the
  seed `_cell_seed` keys on `(currency, year, month)` only, never FX. Verified.
- **RNG / determinism** — `np.random.default_rng(seed)` threaded explicitly
  through every draw; `simulate_monthly_query_counts` spawns per-month child
  generators from a master. Reproducible. Tier-3-discipline-compliant.
- **NaN `Q_low`** — carried as `float("nan")` in `NHPPIntensityParameters`,
  never read by the arrival or cost path; no silent propagation, no crash.
- **Month-end no-op** — `_month_end_weight` returns `1.0` at magnitude 0.0;
  `test_month_end_bump_defaults_to_no_op` confirms default == explicit-zero.
- **functional-python / tier discipline** — frozen `@dataclass(slots=True)`
  containers; engine is a frozen-dc stateless `__call__`; full typing; only
  `Protocol`/`Exception` inheritance. `modules ↛ utils`, `types ↛ modules` clean.
- **Maintainability** — 759 lines, one responsibility, no secrets, no `eval`/
  `exec`/shell, no global state. Docstrings thorough and decision-cited.
- **Notebook** — 21 cells, light pass: descriptive-posture banner, decision-
  citation blocks, trio structure present; no engine logic re-implemented in
  the notebook; consumes the engine API cleanly.
