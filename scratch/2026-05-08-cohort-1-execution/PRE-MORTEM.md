# Pre-Mortem Report — SAAS-COHORT-1 (`simulations/saas_builder/`)

**Scope:** `simulations/saas_builder/model.py` + `simulations/saas_builder/emit.py`.
**Date:** 2026-05-08.

## Summary

Five post-mortems. Three concern math-pin fragility (M3 closed-form drift, NegBin
parameterization confusion, α-floor near-1.5 divergence cluster — the latter
flagged in the plan §3.5 explicitly). Two concern emission-path fragility
(posterior-vs-pp draw alignment, partition-write idempotency under concurrent
emission). All are "non-obvious cause / effect lives elsewhere" scenarios where
a reasonable refactor in one file silently breaks downstream consumers.

## Post-Mortems

### 1. M3 closed-form drift after Sonnet pricing update

**Severity:** Critical
**Component:** `model.py:_build_sonnet_blended_price`,
`simulations/types/fx.py:SONNET_PRICE_*`
**Fragility type:** Stringly-typed contracts / load-bearing defaults

#### What happened

After Anthropic refreshed Sonnet pricing in spec v1.2 (e.g. $3 → $4 input,
$15 → $18 output), a developer updated
`simulations.types.fx.SONNET_PRICE_IN_USD_PER_MTOK` and
`SONNET_PRICE_OUT_USD_PER_MTOK` to the new values. The next CI run failed
with `AssertionError: M3 BLOCK: BlendedPriceFn(Sonnet defaults)() = 8.5495
drifts from spec §5.1 closed form 7.1495 by |Δ| = 1.4`. The COHORT-1 model
factory refused to construct, so no posterior draws were emitted and
COHORT-2 / COHORT-3 / COHORT-4 all stalled.

#### The change that caused it

A two-line edit to `simulations/types/fx.py` lifting Sonnet input/output
per-MTok prices to the v1.2 spec. The change passed a local
`pytest simulations/tests/test_types.py` and the developer assumed the
constants were data-only.

#### Why it broke

`model.py:M3_SONNET_BLENDED_PRICE_EXPECTED = 7.1495` is a **second copy** of
the spec closed-form result that is NOT recomputed from the pinned inputs.
The assertion at line ~108 compares the live `BlendedPriceFn(...)()` output
against this hard-coded literal with `abs_tol=0.01`. The fix needed in
`model.py` was a one-line update to the literal — but nothing in the
`fx.py` change-site signals that another file holds the verification
target. The two pinned numbers are coupled by the spec but disconnected in
code.

#### How it was caught

Caught immediately by the cohort-1 test suite (`TestM3SonnetClosedForm.test_closed_form_evaluates_within_tolerance`).
But only because the assertion runs at model-construction time. If the
assertion lived only in tests, a developer running the COHORT-3 fit suite
without `simulations/tests/test_saas_builder.py` would have emitted
posterior draws priced at the old rate.

#### Hardening suggestions

1. Compute `M3_SONNET_BLENDED_PRICE_EXPECTED` from the same `fx.py`
   constants (`SONNET_PRICE_IN_USD_PER_MTOK`, `SONNET_PRICE_OUT_USD_PER_MTOK`,
   `DEFAULT_W_IN`, `DEFAULT_W_OUT`, `DEFAULT_H_CACHE`, `CACHED_INPUT_DISCOUNT`)
   at module import: `0.539*p_in*(1-h+h*0.1) + 0.461*p_out` — so an `fx.py`
   bump auto-propagates. Keep the `0.01` tolerance to flag drift from a
   *spec-rewrite* (i.e. tier mix or formula change), not a *price* update.
2. Add a comment in `simulations/types/fx.py` near the Sonnet pin block:
   "Bumping these requires a corresponding edit to
   `simulations/saas_builder/model.py:M3_SONNET_BLENDED_PRICE_EXPECTED` and
   spec §5.1 (T1) M3 line." That comment is greppable and would catch the
   developer before they push.
3. Move the M3 assertion onto a CI smoke target so it fires on every PR
   touching either file.

### 2. NegBin reparameterization inverted on emit

**Severity:** High
**Component:** `emit.py:_build_synthetic_tau_rows`,
`priors.py:negbin_mu_phi_to_r_p`
**Fragility type:** Invisible invariants (cross-tier convention mismatch)

#### What happened

A reviewer noticed that the COHORT-2 sign-certification fit produced
`Var/μ ≈ 0.43` rather than the spec-anchored `≈ 2.3` over-dispersion ratio
on the emitted `synthetic_tau_t.parquet` rows. Tracing back: the `(r, p)`
columns in the parquet were the inverse of the spec convention.

#### The change that caused it

A SIM-INFRA-0 follow-up renamed `simulations.types.distributions.NegBinParams`
fields from `(r, p)` to `(n_failures, success_prob)` to match the SciPy
naming convention. The COHORT-1 author updated the import but not the
emit-time reparameterization in
`emit.py:_build_synthetic_tau_rows`, which still calls
`negbin_mu_phi_to_r_p(mu, phi)` and writes the result to the `r` and `p`
columns directly — but the column-emission path no longer matches the
stored Value-tier convention.

#### Why it broke

The parquet columns `r` and `p` in `synthetic_tau_t.parquet` are pinned by
spec §10 / `SYNTHETIC_TAU_COLUMNS` and document the *PyMC convention*
(`r = φ`, `p = φ/(φ+μ)`). The Value-tier `NegBinParams` previously matched
that convention, so passing `(r, p)` straight from the Value to the parquet
worked by coincidence. The renamed fields with swapped semantics passed
type-checking (still two floats) but inverted the meaning, and no test
asserted that a row's `(r, p)` recovers the same μ via the inverse map.

#### How it was caught

Downstream visual inspection — the COHORT-2 reviewer noticed the
over-dispersion ratio looked wrong on a posterior summary plot. Test suite
did not catch it because the test
`TestNegBinReparameterizationRoundtrip` exercises the *function*, not the
emit path. By the time it surfaced, two cohort fits had been published with
the wrong column.

#### Hardening suggestions

1. Add an emission-path round-trip assertion test: build minimal
   `synthetic_tau_t` rows from a known `(μ, φ)`, write through the writer,
   read back, and assert `mu_recovered = r·(1-p)/p == mu_original` within
   tolerance. This anchors the column convention against drift.
2. Annotate the `r` and `p` parquet-column docstrings (in
   `simulations/utils/parquet_io.py:SyntheticTauRow` and the dtype map) with
   the spec §5.2 mean-dispersion convention pinned: "r = φ (PyMC alpha=); p
   = φ / (φ + μ)". This makes the expected semantics greppable.
3. Consider having `emit.py` pass `(mu, phi)` columns directly to the
   parquet (additive M4 schema bump) and deprecate the `(r, p)` columns,
   eliminating the conversion site entirely.

### 3. α prior near-1.5 divergence cluster (plan-flagged)

**Severity:** Medium
**Component:** `model.py:T1ModelFactory.__call__` (the
`pm.TruncatedNormal("alpha_pareto", lower=ap.alpha_lower, ...)` line)
**Fragility type:** Assumptions baked into transformations

#### What happened

After a routine `pymc` minor-version bump (5.28 → 5.32), CI started reporting
`SamplingError: Initial evaluation of model logp resulted in NaN` on the
COHORT-1 production fit. Posterior diagnostics never produced; verdict
fail-closed prevented any emission. Investigation revealed that NUTS was
proposing α slightly below 1.5 due to a numerical precision change in
`pymc`'s TruncatedNormal log-density at the lower boundary, hitting the
`SaasTruncParetoSampler`'s α≥1.5 ValueError if invoked downstream — but the
direct symptom was logp NaN at α=1.5 exactly.

#### The change that caused it

A Dependabot-style `requirements.txt` PR that bumped `pymc==5.28.5` to
`pymc==5.32.0` to pick up an unrelated bug fix.

#### Why it broke

The α-prior `TruncatedNormal(mu=2.0, sigma=0.25, lower=1.5, upper=2.5)` has
~2% prior mass within 0.1 of the lower bound. PyMC's NUTS tunes step-size
adaptively; near a half-truncated boundary, the log-density gradient blows
up and any change to the boundary-handling algorithm can shift NaN
behavior. The plan §3.5 itself flagged this fragility ("re-parameterize
via log(α - 1.5) if surfaced"). The mitigation was foreseen but not
preemptively implemented.

#### How it was caught

CI noisily — the smoke fit on the PR ran but showed `n_chains_failed=4` in
the logs. Nothing emitted, so no silent corruption.

#### Hardening suggestions

1. Add a regression test `test_alpha_prior_logp_finite_at_boundary` that
   instantiates the model, evaluates logp at α = 1.5 + 1e-10 and α = 1.5 +
   1e-6, and asserts both are finite. This pins the boundary behavior.
2. Implement the plan-foreseen `log(α - 1.5)` reparameterization as a
   second `T1ModelFactory` Construction option (kept off by default) so a
   future failure can flip the constructor flag rather than rewrite the
   model. Document the reparameterization in
   `model.py:T1ModelFactory.__call__` docstring as a known mitigation.
3. Pin `pymc` and `pytensor` exact versions in `requirements.txt` (not
   `>=`); upgrade these only as part of an explicit dependency-bump PR
   that re-runs the cohort smoke fit.

### 4. `tier_idx` posterior shape drift breaks emit row count

**Severity:** Medium
**Component:** `emit.py:_build_synthetic_tau_rows` (the
`tier_idx_arr = np.asarray(post["tier_idx"].values).ravel()[:n_rows]` line)
**Fragility type:** Implicit ordering / invisible invariants

#### What happened

A COHORT-3 follow-up extended `T1ModelFactory` to model per-builder tier
mixing within a month (replacing the scalar `pm.Categorical("tier_idx")`
with `pm.Categorical("tier_idx", shape=(n_builders,))`). The next emit run
produced a `synthetic_tau_t.parquet` dataset with N times as many rows as
expected, partition keys mostly assigned to `tier_id=pro/`.

#### The change that caused it

A one-line shape addition to the Categorical in `model.py` to support a
new per-builder tier-mix feature.

#### Why it broke

`emit.py` flattens posterior arrays via `.ravel()[:n_rows]`, where `n_rows`
is computed from `mu_arr.shape[0]` (a scalar). When `tier_idx` becomes a
vector of shape `(n_chains, n_draws, n_builders)`, the ravel yields
`n_chains * n_draws * n_builders` entries, but the downstream loop
iterates only `n_rows` (= `n_chains * n_draws`). Result: only the first
`n_rows` builder-positions are emitted, all from chain-0/draw-0/builder-0
through chain-?/draw-?/builder-0. The emitted rows are coherent but
mis-stratified, and the partition assignment is biased toward whichever
tier dominates builder 0.

#### How it was caught

A reviewer noticed the partition counts (`tier_id=pro/` ≈ 95% of rows)
disagreed with the Dirichlet π posterior mean (`(0.20, 0.50, 0.30)`).
Tests did not catch it because the test fixtures construct posterior idata
with the original scalar shape.

#### Hardening suggestions

1. Add an explicit shape assertion in `_build_synthetic_tau_rows` after
   pulling `tier_idx`: assert `tier_idx_arr.shape == mu_arr.shape` or raise
   a descriptive error pointing to the model.py change. This converts a
   silent mis-stratification into a loud failure.
2. Pin a property test `test_emit_row_count_equals_posterior_flat` that
   parameterizes over posterior shapes (scalar, vector, matrix) — generated
   via Hypothesis — and verifies the emitted row count matches
   `n_chains * n_draws * (any vector dimension shape product)`.
3. Document the scalar-`tier_idx` assumption in the
   `T1ModelFactory.__call__` docstring under a "downstream consumer
   contract" section.

### 5. Idempotent re-emit corrupts partition under concurrent writes

**Severity:** Low
**Component:** `emit.py:CohortEmitter.__call__` (the `SyntheticTauWriter`
call) and `simulations/utils/parquet_io.py:SyntheticTauWriter.__call__`
**Fragility type:** Non-atomic compound operations

#### What happened

A COHORT-2 + COHORT-3 dual-cohort run emitted both fits to the same
`base_dir = simulations/cohorts/data/` directory (a future shared layout).
Two `pq.write_to_dataset(...)` calls landed in the same `tier_id=pro/
month=4/` partition at overlapping times. The result was a parquet file
that was valid but contained both fits' rows interleaved, with no
provenance tag distinguishing them; downstream readers blended posteriors
from incompatible models.

#### The change that caused it

A COHORT-3 plan task refactored emission to share `base_dir` across
cohorts in the interest of "one parquet tree, three sub-cohort prefixes".
The change deleted the cohort-specific subdirectory.

#### Why it broke

`SyntheticTauWriter.__call__` calls `pyarrow.parquet.write_to_dataset(...,
root_path=str(out_root), partition_cols=...)` which writes one file per
group under each Hive partition. Two concurrent calls don't collide on
exact filenames (pyarrow generates UUIDs) but they DO drop files into the
same `tier_id=pro/month=4/` directory, so a downstream
`SyntheticTauReader` sees the union. Idempotency holds for "re-running
COHORT-1 over the same partition" (the writer's behavior was tested in
`test_idempotent_re_emit_same_partition`) but breaks when the partition
is shared by *different* cohorts.

#### How it was caught

A model-quality reviewer plotted posterior τ_t against a synthetic test
prior and noticed bimodality where unimodal was expected. Took two days to
trace.

#### Hardening suggestions

1. Pin a per-cohort subdirectory convention in the writer contract:
   `SyntheticTauWriter(base_dir=...)` should append a default
   `cohort_id="saas_builder_t1"` subdirectory automatically, requiring an
   explicit override to disable. This makes cross-cohort partition sharing
   a deliberate decision.
2. Write the audit-block sha into the partition's `_AUDIT.json` filename
   (e.g. `_AUDIT.<sha[:8]>.json`) so concurrent emissions produce
   distinguishable sidecars; downstream cohort-aware readers can refuse to
   read a partition with two distinct audit blocks.
3. Add a CI smoke test that runs two emits in parallel under
   `concurrent.futures.ProcessPoolExecutor` to the same partition and
   asserts a `SchemaMismatchError`-style cross-cohort guard fires (this
   guard does not exist yet — the smoke test would document the missing
   protection until it lands).

## Themes and Recommendations

Two structural themes link these:

**A. Math pins live in two places.** Three of the five post-mortems (1, 2, 3)
share a pattern: the spec pins a numeric truth (M3 closed-form, NegBin
convention, α floor) and the codebase encodes it twice — once at the source
constant in `simulations/types/fx.py` or
`simulations/types/distributions.py`, and once at the consumer assertion in
`simulations/saas_builder/model.py`. The two copies are coupled by the spec
but unlinked in code; either side can drift while the other sleeps. Recommended
structural change: every M-pin assertion in the cohort layer should be derived
from the type-tier constant at import time, with the assertion checking
*formula identity* (not numeric identity) against the spec. The numeric
literal lives only in the test suite.

**B. The emission column convention is implicit.** Post-mortems 2 and 4 both
hinge on `synthetic_tau_t.parquet` columns whose semantic contract lives in
the spec but is not asserted at the emit boundary. The Hive partition layout,
the `(r, p)` reparameterization, the row-count formula, the tier_idx-shape
assumption — none of these are captured as run-time invariants on the row
TypedDicts. Recommended structural change: extend `simulations/utils/parquet_io.py`
with a `SyntheticTauInvariants` Callable that asserts cross-column
relationships (e.g. `r·(1-p)/p > 0`, `tier_id ∈ TIER_IDS`, `q_t_cop ≈ q_t_usd
× FX_anchor` within a wide tolerance) and run it at emit-time. This is a
SIM-INFRA-1 follow-up.

Outside these themes, post-mortem 5 stands alone as a concurrency-related
fragility unique to multi-cohort deployment; no Stage-2 work surfaces it, but
Stage-3 production deployment will.
