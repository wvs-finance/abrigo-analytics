# Reality Checker — v0.2.6 spec amendment (CORRECTIONS-Z) review

**Scope.** Two-wave review of `docs/specs/2026-05-16-ai-cost-factor-model-design.md`
v0.2.6 §0.6 (CORRECTIONS-Z-1 multi-period aggregation; CORRECTIONS-Z-2
backcast bootstrap; CORRECTIONS-Z-3 R6 escalation gate) added after Task 12
R5 PRIMARY returned FX share ≈ 0.00003 (90% CI [-3.4e-6, +4.1e-5]) on the
28-day 2026-Q1-Q2 window.

**Reviewer role.** Wave 1 Reality Checker. Charter: anti-fishing audit,
spec-vs-reality cross-checks, pre-mortem of failure modes. No verdict
authority over methodology pinning (defer to Wave 2 Model QA).

**HEAD reviewed.** `master` post-Task-12 (`fa77c8f`).

---

## 0. Verdict summary

| Q | Topic | Verdict |
|---|-------|---------|
| 1 | Anti-fishing pre-registration of Z-arm parameters | **PASS** with one FLAG (TRM bucket aggregator footnote) |
| 2 | CORRECTIONS-K consistency (diagnostic-only) | **PASS** |
| 3 | Monthly stratum with N=4 | **CONDITIONAL_PASS** — report-but-drop-from-narrative explicitly required |
| 4 | Backcast Z-2 counterfactual validity | **FLAG** — premise + IID-of-blocks composition risk |
| 5 | Z-3 escalation threshold pre-pinning defensibility | **CONDITIONAL_PASS** — disjunctive "OR" admits one inert branch |
| 6 | R6 non-trigger close-out | **FLAG** — premature closure risk under stale-parity panel |
| 7 | §2.4 internal consistency | **FLAG** — table not updated; cross-ref ambiguity |
| 8 | Pre-mortem of Z-2 specifically | **FLAG** — heavy-tail / blow-up failure mode unacknowledged |

**Overall verdict: CONDITIONAL_APPROVE.** Z-1 is sound and well-pinned. Z-2
and Z-3 have legitimate but addressable methodological gaps that should
land as inline pre-data-touch disclosures, not silent assumptions. The
spec-level integrity issue (Z-arms layered on a panel that the spec itself
declares "NOT verdict-eligible" at lines 889–894) is the only finding
approaching a BLOCK; classified here as a FLAG because the spec also
explicitly states Z-arms are diagnostic-only, which keeps the contradiction
internally consistent — but the audit trail must record that Z-arms run on
a known-stale-by-2.3% cost panel.

---

## 1. Per-question findings

### Q1. Anti-fishing classification of Z-arm parameters — PASS (with one FLAG)

**What's pinned (verified in §0.6 lines 805–877):**

| Parameter | Z-1 (daily/weekly/monthly) | Z-2 (backcast) | Z-3 (gate) |
|---|---|---|---|
| `B` (bootstrap replications) | 10,000 (each frequency) | `B_paths = 1,000` | n/a |
| `seed` | 20260516, 20260517, 20260518 | 20260519 | n/a |
| `block_len` | `⌈T^(1/3)⌉` (4 daily, 2-3 weekly, n/a monthly) | 4 (= same as daily R5) | n/a |
| escalation threshold | n/a | "≥ 5× daily baseline OR ≥ 0.05 absolute" | inherited |
| backcast horizon | n/a | 2024-01-03 → 2025-12-31 (~520 weekdays) | n/a |
| bootstrap pool | n/a | OBSERVED 28-day series only | n/a |
| starting cost | n/a | median observed daily cost | n/a |
| cov rule | CORRECTIONS-Q (separate) | CORRECTIONS-Q (separate) | n/a |
| CI level | 90% | 90% inter-path interval | n/a |

All pre-data-touch parameters numerically pinned. Cell-2 declaration
requirement (line 878–879) is the standard anti-fishing pattern; aligned
with §0.5 / §0.4 prior CORRECTIONS practice.

**FLAG-Q1-A (TRM bucket aggregator).** Line 813 says volume-weighted-in-code
but simple-mean in v0.2.6. This is a real methodological choice for Z-1
that affects the weekly stratum (e.g., a low-cost weekday with a TRM spike
should weight differently under volume-weighted vs simple mean). The spec
calls it "keep simple per scope" — acceptable, but **the choice itself is a
pin** and the simple-mean vs volume-weighted decision should be a
pre-registered citation, not a parenthetical. Recommend: lift this into the
"Pre-pinned" bullet list as a first-class item.

**Otherwise PASS.** No tuning knob is left for post-hoc adjustment.

---

### Q2. CORRECTIONS-K (diagnostic-only) consistency — PASS

§0.6 line 795–797: *"All arms are diagnostic-only per CORRECTIONS-K — they
do not have verdict authority over the R5/R4-S3 framework."*

§0.6 line 884–885: *"R5 PRIMARY's headline FX share remains on the daily
2026-Q1-Q2 real data; Z-arms are corroborative only."*

CORRECTIONS-K (§2.4 line 1128): *"No arm has verdict authority. Period."*

The Z-arms inherit the discipline. Z-3 escalation gate is NOT a verdict on
R5; it's a routing gate to a separate iteration (R6) that has its own
review/methodology stack. That preserves CORRECTIONS-K: Z-2 cannot flip the
R5 verdict, only trigger a different framework to ask the question
differently. Clean.

---

### Q3. Monthly stratum with N=4 — CONDITIONAL_PASS

**Spec text (line 808, 819–821):** *"N=4 below the bootstrap CI-usability
floor — record but disclose the CI is uninformative... reported but
flagged as 'below bootstrap usability floor'; the verdict on FX share stays
on daily."*

**Analysis.** N=4 is genuinely below ANY reasonable bootstrap floor; the
block-bootstrap minimum theoretical floor is roughly `T ≥ 2·block_len + 5`
which with `block_len = ⌈4^(1/3)⌉ = 2` gives T ≥ 9. At T=4 the bootstrap
distribution is a delta-mass on a tiny finite set of resamples — the
"interval" is degenerate.

**The honest question:** does reporting an uninformative CI invite noise,
or is it forensic transparency?

**Verdict CONDITIONAL_PASS.** Honesty wins IF the disclosure is
operational rather than performative. Specifically:

- The 06_z_sensitivity.ipynb monthly cell **must show the CI explicitly
  with a "CI not usable" annotation in the output**, not bury it in a
  preamble.
- The narrative interpretation in the disposition memo **must not** cite
  the monthly point estimate as evidence for anything.
- The R6 escalation gate (Z-3) **must not** use monthly as an input.

These conditions can be enforced by extending §0.6 Z-1 with: *"Monthly
stratum: point estimate displayed without CI; explicitly excluded from
the Z-3 escalation-gate input; cited in disposition memo only as 'CI
uninformative at T=4'."*

If the spec amendment lands that one-line guard, this is a clean PASS. As
written, the risk is non-zero that a future reader treats the monthly
number as comparable to weekly/daily.

**Alternative considered:** DROP monthly entirely. Rejected because:
1. The user asked "is small-FX a structural property OR regime-conditional?"
   and the monthly aggregation is the only frequency at which a TRM
   trending move (the 2024-2025 ~19% range) would dominate within-bucket
   token-burst noise. Excluding it pre-emptively forecloses a relevant
   diagnostic.
2. Recording it with explicit "uninformative" tagging is the lower-bias
   choice vs silently dropping.

---

### Q4. Backcast Z-2 counterfactual validity — FLAG

**Setup (lines 827–855):** hold cost-behavior fixed at observed
2026-Q1-Q2 empirical distribution (28 Δln cost^USD values); stationary-
bootstrap-resample to fill ~520 weekdays in 2024-01-03 to 2025-12-31; join
real Banrep daily TRM; compute COP cost and R5 decomposition; B_paths=1000.

**Finding-Q4-A (premise mis-stated empirically).** §0.6 line 829–832
characterizes the 2026-Q1-Q2 window as a "quiet" TRM regime that Z-2 will
contrast against a "higher-vol TRM regime (e.g., 2024-Q1)". I verified
against `data/raw/banrep_trm_daily.parquet` (563 rows, 2024-01-03 →
2026-05-16):

| Window | N | sd(Δln TRM) | range_pct |
|---|---|---|---|
| 2024-Q1 | 57 | 0.00473 | 3.47% |
| 2024-full | 237 | 0.00684 | 18.99% |
| 2025-full | 236 | 0.00737 | 19.15% |
| 2026-Apr-May (≈28d) | 31 | 0.00634 | 6.92% |
| 2026-Q1-Q2 | 89 | 0.00626 | 6.94% |

The 2026-Q1-Q2 daily innovation vol (0.00626) is **higher** than 2024-Q1
(0.00473) and only ~10% lower than 2024-full and 2025-full. The 2024-2025
years had ~19% range vs 2026-Q1-Q2's ~7% range, but that's drift-driven,
not innovation-vol-driven. Daily R5's variance decomposition is dominated
by Δln-scale innovations, not by levels.

**Implication.** Z-2's stated premise — that backcasting onto 2024-2025
TRM exposes a "higher-vol regime" — is empirically weak when measured at
the daily innovation level that R5 operates on. The 5× escalation
threshold (Z-3) is calibrated against a baseline that is unlikely to be
moved much by a regime that has only ~10% higher daily innovation vol.

**Recommended fix.** §0.6 Z-2 should add a one-sentence empirical note:
*"The 2024-2025 horizon provides ~3× more trading days and approximately
1.1× the daily innovation vol of 2026-Q1-Q2; the regime contrast is
primarily in path-level drift (~19% vs ~7% range) and weakly in daily
volatility. The Z-2 test therefore exposes whether **path-level TRM drift**
(which can shift the joint distribution of cost ×TRM via trending
co-movement) matters for FX share, NOT whether higher daily TRM vol
matters."*

That framing makes Z-2's success criterion honest: a non-trivial FX-share
shift under Z-2 would indicate **drift-induced TRM-cost coupling**, not
"high-vol regime exposure". This is still informative — arguably more so
— but the spec narrative as written sets the reader up for a different
interpretation.

**Finding-Q4-B (Claude-Code-v2-didn't-exist-in-2024 confounding — user-asked).**
User's question: "does Z-2 assume cost behavior in 2024 would be IDENTICAL
to 2026's, which is empirically false (Claude Code v2 didn't exist in
2024)?"

The spec is **explicit** about this and the design **does not** claim a
real backcast. Line 829–831: *"holds cost-behavior fixed at the observed
2026-Q1-Q2 empirical distribution and swaps in real historical TRM."* This
is a **counterfactual** ("if a 2026-pattern user had existed in 2024-2025,
what FX share would have been observed?"), not a forecast or actual
back-test. The construct is internally consistent with that framing.

**However**, the spec does NOT explicitly state this is a counterfactual
(rather than a back-test). A reader skimming §0.6 line 829 might read
"would the FX share be different in a higher-vol TRM regime (e.g.,
2024-Q1)?" as a factual back-test claim. **Recommend** adding one line:
*"This is a counterfactual sensitivity, not a back-test: cost-behavior is
asserted-stable for the purpose of isolating the TRM-regime channel.
Validity claim is conditional on that fixed-cost-behavior assumption; no
calibration against actual 2024-2025 Claude Code usage is performed or
required."*

**Finding-Q4-C (block bootstrap composition for path generation).** Line
838–842: *"draw one `Δln cost^USD` value via **stationary bootstrap**...
reconstruct a path of `cost^USD_t = cost^USD_{t-1} × exp(Δln_t)`."*

Stationary bootstrap with `block_len = 4` resamples blocks of size ≈4 with
geometric block-length to preserve short-run serial dependence. But the
RECONSTRUCTED path is the cumulative product of these draws over ~520
weekdays. With block_len=4 and 520 weekdays, the path has ~130
independent-ish blocks. The resulting cumulative log-cost is approximately
a random walk whose terminal-time variance scales with horizon.

This raises **two issues** the spec does not address:

1. **Cost trajectory blow-up risk.** If the observed 28-day Δln cost
   series has a mean ≠ 0 (which it almost certainly does — Claude Code
   usage is bursty and the maintainer is increasing usage over time), the
   reconstructed 520-day path drifts by `520 × mean(Δln cost^USD)`. Even a
   small positive mean of 0.01 implies a 520-day terminal cost ≈
   `exp(5.2) ≈ 180×` starting cost. Variance of `Δln (cost × TRM)` is
   shift-invariant in level so FX share is in principle invariant — but
   the cost^COP series itself is now astronomical, and any downstream
   reporting in cost-level terms is meaningless.
2. **Heavy-tail amplification.** See Q8 (pre-mortem).

**Recommended fix.** §0.6 Z-2 should pin one of:
- **Center the bootstrap pool** at zero mean before resampling
  (recommended — preserves serial structure, eliminates spurious drift in
  the counterfactual).
- **OR** explicitly declare that path-level cost is not interpreted and
  only Δln-series FX share decomposition is computed (which is the variance
  ratio we actually want anyway).

As written the spec does neither and the resulting paths will exhibit
either spurious drift or spurious damping depending on the realized
28-day series mean.

---

### Q5. Z-3 escalation threshold (≥ 5× baseline OR ≥ 0.05 absolute) — CONDITIONAL_PASS

**The disjunctive form is the issue.** Baseline = 0.00003. Then:

- "≥ 5× baseline" = ≥ 0.00015 (= 0.015%)
- "≥ 0.05 absolute" = ≥ 5% absolute

These thresholds differ by ~333×. The 5×-baseline threshold is the
sensitive branch (will trigger if the backcast moves FX share even a
little); the 0.05-absolute threshold is essentially a sanity floor that
will never bind unless something is catastrophically different.

**Pre-pinning analysis.** Pre-data-touch numeric pinning of both is good
anti-fishing hygiene. But the **purpose** of an "OR" disjunction in a
threshold is to take the MIN (more permissive) — so effectively only "≥ 5×
baseline = ≥ 0.00015" is the operative gate. The 0.05-absolute branch is
inert.

**Two readings:**

1. **Charitable.** The 0.05 floor exists as a sanity check: if for any
   reason the baseline is computed wrong (e.g., truly zero or negative
   due to estimator artifact), the absolute threshold provides a fallback
   so escalation isn't suppressed by a degenerate baseline. **This is a
   defensible safety pin.**
2. **Uncharitable.** The 0.05 floor is decorative — a "magic
   psychologically-comfortable number" that adds no operational value.

The spec does not explain which interpretation is intended. **Recommend**
adding: *"The 0.05-absolute branch is a degenerate-baseline safety floor;
in practice the 5×-baseline branch dominates and is the operative gate."*
Or, alternatively, replace with a single threshold and explain its
calibration.

**Calibration of the 5× factor itself.** No justification is given. A 5×
multiplicative shift in FX share is large enough to be substantively
meaningful (0.003% → 0.015%) but small enough that random variation in a
1000-path bootstrap could plausibly cross it. The spec does not show what
the 95% inter-path quantile is expected to be under the null
(cost-distribution-stable, TRM-regime-swapped). **Recommend** that the
disposition memo include a "null-calibration" check: simulate B_paths
under the actual 2026-Q1-Q2 TRM (not 2024-2025), confirm the 95% upper
inter-path quantile of FX share is below 5× baseline, and only then
interpret a 2024-2025-TRM result above 5× as signal. As written, the gate
may trigger on Monte-Carlo noise.

**Verdict CONDITIONAL_PASS.** Threshold values are pre-pinned numerically
(satisfies anti-fishing). Two improvements should land: (a) explain the
disjunctive structure or collapse it; (b) add the null-calibration check
to the disposition memo template.

---

### Q6. R6 non-trigger close-out — FLAG

**Spec text (lines 868–870):** *"If Z-2's median FX share stays within ±2×
of the daily baseline, the R6 escalation is NOT triggered and the
iteration closes at v0.2.6 with the R5 Role A finding intact + the
multi-regime corroboration."*

**Two concerns:**

1. **Stale-parity panel issue.** §0.6 line 887–894 explicitly states:
   *"v0.2.2 CORRECTIONS-Y-2 / Y-4 ccusage-parity-0.1% criterion is **NOT
   yet satisfied**. Y-9 must close the residual before §2.1 R5
   verdict-table eligibility... verdict-eligible R5/R4-S3 outputs require
   Y-9 closure."*

   The R5 PRIMARY 0.00003 number that triggered §0.6 and that Z-arms
   corroborate runs on a panel that is 2.3% off ccusage. The spec itself
   has declared this panel NOT verdict-eligible. Closing the iteration at
   v0.2.6 under the non-trigger branch would close on a finding the spec
   has already said is provisional pending Y-9. This is a **timing
   inconsistency**.

   **Required fix.** §0.6 line 868–870 should add: *"...AND the Y-9
   ccusage-parity-0.1% closure has landed (per §0.6 'Parity-target status'
   above). If Y-9 has not landed, closure remains conditional on Y-9
   regardless of Z-2 outcome."*

   Without this guard, the spec contradicts itself: the close-out
   condition (Z-2 non-trigger) does not require Y-9, but the verdict-table
   eligibility (which any "close iteration" action implicitly invokes) does.

2. **Y/X-exploration foreclosure.** The user's broader concern: does
   non-triggering R6 preemptively close the door on alternative
   (Y, X) exploration?

   **Reading the spec carefully:** Z-3 is the **only** documented
   escalation path in §0.6, and it routes to R6 (a methodological
   alternative — different stochastic process for cost arrivals, same Y
   and X). It does NOT route to alternative (Y, X) iterations. If the
   R5/Z-1/Z-2 results all confirm small-FX-share is a structural property
   of the proxy user, then the honest conclusion is "for THIS proxy user
   under THIS instrument (Claude Code subscription), FX vol is not the
   dominant cost-burden driver — closing this (Y, X) pair." That is
   exactly the (Y, M, X) framework's CLOSED-FAIL pattern (cf.
   `memory/project_fx_vol_cpi_notebook_complete.md` and
   `memory/project_phase_a0_exit_verdict.md`).

   The spec's close-out is **honest** in that sense. But it would be
   strengthened by explicit framework-discipline language: *"Non-trigger
   close means the (Y=non-subscribed-LATAM-dev-AI-cost, X=COP/USD) pair is
   recorded as CLOSED_SMALL_BETA in `memory/` — informing the next
   population's X-search prior per the CLAUDE.md iteration-order doctrine.
   The instrument-family itself is not foreclosed; future (Y, X)
   iterations on different populations / different cost-rails remain open."*

   That keeps the framework's anti-fishing memory-update discipline
   visible and prevents future readers from interpreting the close as
   "instrument family failed".

**FLAG (not BLOCK).** The spec is internally consistent if read fully
across §0.6 and §2.1, but the close-out language reads as if Y-9 is
already satisfied. Two surgical edits (Y-9 gate + framework-discipline
note) fix this.

---

### Q7. §2.4 internal consistency — FLAG

**Current state.** §2.4 (lines 1113–1128) lists 4 sensitivity arms: Lag
k=5, Model-fixed subset, Pre-/post-price-step regime split,
Outlier-trimmed. All operate on R4-S3 (the auxiliary inferential arm),
not on R5 (the descriptive primary).

§0.6 Z-arms operate on R5 (the descriptive primary). They are a different
kind of sensitivity — methodological regime/aggregation sensitivity for
the variance decomposition, not robustness checks on the inferential
regression.

**Recommendation.** §2.4 should remain the canonical R4-S3 sensitivity
table; §0.6 should remain the canonical R5 sensitivity location.
**However**, §2.4 should add a one-line cross-reference: *"R5 PRIMARY
sensitivity arms (multi-period aggregation, backcast bootstrap) are
specified in §0.6 CORRECTIONS-Z and inherit the same diagnostic-only
discipline (CORRECTIONS-K)."*

Without that cross-reference, a Wave-2 reviewer reading §2.4 in isolation
would not know the Z-arms exist. The spec audit-trail discipline (per
CORRECTIONS-K's explicit "no arm has verdict authority. Period.") merits
the back-pointer.

---

### Q8. Pre-mortem of Z-2 specifically — FLAG (failure mode not acknowledged)

**The user-asked failure mode:** *"if the resampled cost-changes are
heavy-tailed, the backcast distribution may have extreme outliers that
swamp FX vol."*

**Empirical context.** The 28-day Δln cost^USD pool is small (N=28) and
includes the maintainer's actual usage pattern, which includes occasional
heavy-token-burst days (e.g., long agent runs). The empirical distribution
on N=28 will have a few extreme values that, under stationary bootstrap
with block_len=4, will appear in roughly `4/28 ≈ 14%` of resample blocks.

**Failure mode A: heavy-tail outlier domination.** A single block
containing the maximum |Δln cost^USD| (call it 3σ) appearing 130 times in
a 520-day reconstructed path means variance of cost-changes is dominated
by these outliers. FX share = Var(Δln TRM) / [Var(Δln Cost^USD) + Var(Δln
TRM) + 2·Cov(...)]. If Var(Δln Cost^USD) blows up under heavy-tail
resampling, FX share **shrinks toward zero** — Z-2 would then artificially
support the small-FX-share conclusion regardless of regime. This is the
**Type-II error mode** (Z-3 fails to trigger when it should).

**Failure mode B: low-cost-burst blocks producing artificial signal.**
Conversely, in resampled paths that happen to over-represent low-|Δln
cost^USD| blocks, Var(Δln Cost^USD) is artificially small and FX share is
inflated — potentially crossing Z-3's 5× threshold spuriously. This is the
**Type-I error mode** (Z-3 triggers R6 escalation on noise).

**Neither failure mode is acknowledged in §0.6.** The 1000-path inter-path
interval will widen to reflect the resampling variability, but a wide
interval doesn't fix a biased median.

**Recommended fix.** §0.6 Z-2 should add:
- A pre-data-touch DATA_DIAGNOSTIC: report the empirical distribution
  of the 28 Δln cost^USD values (min, P10, P25, P50, P75, P90, max, sd,
  skewness, kurtosis) BEFORE running the backcast. Specifically: if
  kurtosis > 10 (heavy-tail), explicitly flag the Z-2 result as
  "heavy-tail-pool" and treat the median FX share as a lower bound, not
  a point estimate.
- A Winsorization sensitivity sub-arm Z-2-W: re-run Z-2 with the
  cost-pool Winsorized at 5%/95% (or at 1%/99%, matching the §2.4
  outlier-trimmed arm convention). If Z-2 and Z-2-W disagree
  materially, report both and HALT on interpretation. (Pin Winsorization
  thresholds NOW, pre-data-touch, to preserve anti-fishing.)

The current spec leaves Z-2 vulnerable to either failure mode without an
internal check.

---

## 2. Anti-fishing audit

The Z-arms satisfy the **letter** of the anti-fishing protocol:

- ✅ All numeric parameters (B, seed, block_len, escalation threshold,
  backcast horizon, B_paths, starting cost) pinned in §0.6 before any
  Z-arm code runs.
- ✅ Pre-pinned interpretation rules stated for Z-1 ("If weekly FX
  share within ±2× of daily, not horizon artifact...") and Z-2 ("If
  median FX share ≥ 5× daily baseline OR ≥ 0.05 absolute, escalate to
  Z-3").
- ✅ Z-3 has a clear pre-data-touch routing rule with both branches
  documented (trigger → R6 activation; non-trigger → close at v0.2.6).
- ✅ Diagnostic-only classification per CORRECTIONS-K explicit.
- ✅ Cell-2 declaration requirement in 06_z_sensitivity.ipynb (line
  878–879) enforces the pin at code-execution time, not just at spec time.

The Z-arms satisfy the **spirit** with the following caveats — all
addressable by inline spec edits, none requiring methodology rework:

1. (Q1-A) TRM-bucket aggregator (simple-mean vs volume-weighted) is a
   pin, not a parenthetical — lift to first-class pin.
2. (Q3) Monthly stratum needs explicit Z-3-input-exclusion guard so its
   uninformative CI cannot propagate.
3. (Q4-A) Premise of Z-2 (high-vol regime) is empirically weak at the
   daily innovation level — recharacterize as drift-channel test, not
   vol-channel test.
4. (Q4-B) Z-2 is a counterfactual, not a back-test — say so explicitly.
5. (Q4-C) Bootstrap pool should be mean-centered before path
   reconstruction OR cost levels should be declared
   non-interpreted-output — pin one.
6. (Q5) Z-3's disjunctive OR has an inert branch — explain or collapse.
   Add null-calibration check to disposition memo.
7. (Q6) Close-out branch must gate on Y-9 ccusage-parity closure to
   avoid contradicting §0.6's own non-verdict-eligibility statement.
8. (Q8) Pre-mortem the heavy-tail failure mode + add kurtosis diagnostic
   + add Winsorized sub-arm Z-2-W.

**No anti-fishing-banned pattern detected.** No threshold tuning to fit
the already-observed 0.00003 result. No post-hoc parameter choice. No
silent re-run of the same (Y, X) at a different threshold.

---

## 3. Spec-vs-reality cross-checks (executed)

1. ✅ `data/raw/banrep_trm_daily.parquet` exists. Shape (563, 2), date
   range 2024-01-03 → 2026-05-16. **The Z-2 backcast horizon
   (2024-01-03 → 2025-12-31, ~520 weekdays) is fully inside the existing
   panel** — no additional data-fetcher work required for Z-2.
2. ✅ Daily TRM vol comparison (table in Q4): refutes the spec's
   "higher-vol regime" framing — daily innovation vol is comparable
   across windows; the contrast is drift-driven, not vol-driven.
3. ✅ R6 sibling spec exists at v0.1.3 (matches §0.6 line 863 reference);
   plan exists at `docs/plans/2026-05-16-r6-continuous-stream-simulation-plan.md`.
   R6 is APPROVED for plan emission per its own frontmatter, not yet
   implemented — consistent with §0.6's "activate the R6 sibling
   iteration" framing (Z-3 trigger is the implementation green-light).
4. ✅ §0.6 line 887–894 explicitly admits the underlying cost panel is
   off-ccusage by 2.3% and that R5 outputs require Y-9 closure for
   verdict-eligibility. **This is honest disclosure**, and the Z-arms
   inheriting that provisional status is consistent — but the close-out
   branch (Q6) needs an explicit Y-9 gate to prevent contradiction.
5. ✅ §2.4 R4-S3 sensitivity table is unchanged and unaffected by Z-arms;
   no contradiction — but missing cross-reference (Q7).

---

## 4. Overall verdict — CONDITIONAL_APPROVE

**Approve subject to landing the following inline spec edits (all surgical;
none methodological):**

| # | Edit | Location | Severity |
|---|------|----------|----------|
| 1 | Lift TRM-bucket aggregator choice (simple-mean) to first-class pin | §0.6 Z-1 pre-pinned bullet list | Minor |
| 2 | Add "Monthly excluded from Z-3 input; CI not displayed without 'uninformative' tag" guard | §0.6 Z-1 | Important |
| 3 | Recharacterize Z-2 premise: drift channel, not daily-vol channel; cite empirical TRM vol comparison | §0.6 Z-2 paragraph 1 | Important |
| 4 | Declare Z-2 a counterfactual, not a back-test; cost-behavior assumed-stable | §0.6 Z-2 | Important |
| 5 | Pin either mean-centering of bootstrap pool OR declare cost-levels uninterpreted | §0.6 Z-2 | Important |
| 6 | Explain disjunctive escalation gate ("OR 0.05 absolute") or collapse | §0.6 Z-2 / Z-3 | Minor |
| 7 | Add null-calibration check to disposition memo template (Z-2 under 2026-Q1-Q2 TRM) | §0.6 Z-2 / 06_z_sensitivity.ipynb spec | Minor |
| 8 | Gate close-out branch on Y-9 ccusage-parity closure | §0.6 Z-3 paragraph 2 | **Important** |
| 9 | Add framework-discipline language: non-trigger close = (Y, X) CLOSED_SMALL_BETA; instrument family not foreclosed | §0.6 Z-3 paragraph 2 | Minor |
| 10 | Add cross-reference to §0.6 in §2.4 sensitivity table | §2.4 | Minor |
| 11 | Add heavy-tail / kurtosis pre-data DATA_DIAGNOSTIC + Z-2-W Winsorized sub-arm (pin thresholds now) | §0.6 Z-2 | Important |

**Edits 2, 3, 4, 5, 8, 11 are Important** because they protect the audit
trail from misinterpretation or close a contradiction; **edits 1, 6, 7, 9,
10 are Minor housekeeping** that improve readability and reviewer
discoverability without changing methodology.

**Recommendation to Wave 2 reviewers:** Wave 2 Model QA should rule on
edits 3, 4, 5, 11 (counterfactual framing, mean-centering, heavy-tail
treatment) as methodology matters. Wave 2 Code Reviewer should rule on
notebook 06_z_sensitivity.ipynb trio scaffolding (9 trios per §0.6 line
877) and ensure the cell-2 pin declaration is structurally enforceable
(not just documented).

**No BLOCK issued.** The spec amendment is broadly sound, well-pinned,
and inherits the diagnostic-only discipline correctly. The CONDITIONAL on
the APPROVE reflects that 11 inline edits — mostly disclosure / framing /
guard-rail — will significantly improve the audit trail without
requiring methodology rework.

---

## 5. Cross-reference artifacts

- Spec under review: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.6 §0.6
- R6 sibling spec: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md` v0.1.3
- R6 plan: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/docs/plans/2026-05-16-r6-continuous-stream-simulation-plan.md`
- Daily TRM panel: `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/data/raw/banrep_trm_daily.parquet` (563 rows, 2024-01-03 → 2026-05-16)
- CORRECTIONS-K (parent diagnostic-only doctrine): §2.4 lines 1113–1128
- Y-9 backlog item: §0.6 line 887–894 (parity-target status)
- Anti-fishing iteration discipline: `CLAUDE.md` "Abrigo Operating Framework" + `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`

---

**Reviewer:** TestingRealityChecker (Wave 1)
**Date:** 2026-05-17
**Repository HEAD:** `master` post-Task-12 (`fa77c8f`)
**Report path:** `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/scratch/2026-05-17-v0_2_6-spec-review/reality_checker.md`
