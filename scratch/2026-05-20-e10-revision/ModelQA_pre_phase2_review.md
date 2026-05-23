# Model-QA Pre-Phase-2 Review — E10 GSPS Q-Process Calibration

**Reviewer role:** Model-QA (modeling-soundness side; Reality Checker covers anchor-genuineness/feasibility in parallel).
**Object under review:** `notebooks/e10_gsps/diagnostics/E10.1_calibration_note.md`, resting on `scratch/2026-05-20-e10-revision/e10_q_anchor_extraction.md` + `e10_q_anchor_{calls,daily}.csv` + `e10_q_anchor_buckets.json`.
**Gate:** plan §7 mandatory pre-Phase-2 review; a PASS clears Phase 2 (tasks 2.1–2.4) entry.
**Date:** 2026-05-20. **Posture:** read-only audit.

---

## Verdict: PASS

E10 is **cleared to enter Phase 2.** Critical findings: **0**. The calibration note
is complete enough that the R6 NHPP simulator build (tasks 2.1–2.4) can proceed
against it without an unresolved modeling gap. All findings below are Strong/Weak/
Observation and are non-blocking; none triggers CORRECTIONS.

---

## Cox overdispersion mechanism — explicit call: **RATIFY**

The §3.3 decision-citation locking the overdispersion mechanism as a **Cox /
doubly-stochastic NHPP with a Gamma-mixed sprint-intensity λ(t)** is **RATIFIED**.
The decision-citation stands; no separate user confirmation is required.

Soundness of the choice, point by point:

- **Evidence supports doubly-stochastic over equidispersed.** Daily VMR ≈ 20 at
  both centre and bracket, reached *independently* — confirmed by re-computation
  from `e10_q_anchor_daily.csv` (sample-variance VMR 20.6 / 19.8; population-
  variance VMR 18.9 / 19.1 — same order, conclusion invariant to the estimator).
  A homogeneous or deterministically-modulated NHPP has a Poisson conditional
  count law and cannot reach VMR ≈ 20. An explicit overdispersion mechanism is
  *required*, not optional. Correct.

- **Rejection of bare negative-binomial is sound.** A single-Gamma NB marginal
  matches the ~20× VMR but is silent on *within-day* clustering (5-min windows of
  16–24 calls) and on discrete whole-day spikes. It would force §6.3 items 2 and
  3 to be modelled by a second, disconnected mechanism — a strictly less
  parsimonious specification with two free knobs where the trace supports one.
  Rejecting it as the primary is correct.

- **Rejection of self-exciting Hawkes is sound.** Hawkes encodes *endogenous
  contagion* — arrivals trigger arrivals. The trace evidence is the opposite: the
  27/27-query centre spike days (05-08, 05-18) and the 42/26 bracket spikes align
  with discrete, externally-scheduled research/build sprints. Burst timing is
  exogenously driven; a Hawkes self-excitation kernel would mis-attribute
  exogenous sprint structure to endogenous feedback. Rejecting it is correct and
  well-argued.

- **The Cox route ties Q-variance to observed structure, not a free knob.** This
  is the load-bearing point for §4.3: Q-variance is the `Var(Δlog Q)` term that
  competes with `Var(Δlog FX)` in the FX-variance-share denominator. Anchoring it
  to an observed sprint-intensity process rather than a tunable dispersion
  parameter keeps the §4.3 surface honest. The §3.3 "Relevance" paragraph states
  this correctly.

- **§3.4 fallback is a clean fallback.** NB-marginal + a *separately specified*
  burst layer is recorded as the fallback should the review read the choice as
  open — pre-stated so it is not a fresh design step. It is genuinely a fallback
  (one mechanism short on parsimony, not on validity) and is correctly recorded.

The one qualification is **STRONG-1** below: the *Gamma* mixing distribution is
asserted, not shown to dominate log-normal. This does not block ratification of
the *mechanism class* (Cox / doubly-stochastic), which is what §3.3 routes here.

---

## Findings

### STRONG-1 — Gamma mixing distribution asserted, not discriminated from log-normal
The note locks the mixing law as **Gamma**. Both candidate-1 wording and the
extraction §6 explicitly name "Gamma *or* log-normal" sprint-intensity. The
metadata-only trace (n=12 centre / 28 bracket daily counts) cannot discriminate a
Gamma from a log-normal mixing tail at any useful power — the spike days are too
few to fix tail curvature. Gamma is defensible as the *conjugate, parsimonious*
default (Gamma-mixed Poisson → NB marginal, so the §3.4 fallback nests cleanly),
but the note presents it as trace-anchored when it is in fact a modelling-economy
default. **Recommendation:** Phase 2 task 2.3a should either (a) reword the lock
to "Gamma mixing — chosen for conjugacy/NB-nesting, not trace-discriminated; tail
shape is a sensitivity knob," or (b) carry log-normal as a §4.3 sensitivity arm.
Non-blocking: the *mechanism class* is correctly anchored; only the within-class
tail shape is a soft default. Mitigated in practice because §4.3 sweeps the
modulation magnitudes, which partly absorbs tail-shape sensitivity.

### STRONG-2 — overdispersion estimated on n=12 / n=28 daily counts
VMR ≈ 20 rests on 12 centre and 28 bracket daily observations, of which the bulk
are structural zeros and 2–4 are spike days. The point estimate is dominated by a
handful of spike days; its sampling uncertainty is wide. The note treats VMR ≈ 20
as a firm magnitude. This is acceptable for a *mechanism-selection* decision (any
VMR materially above 1 settles "overdispersion required"), and the centre/bracket
agreement at ≈20 independently is genuinely reassuring. But the *magnitude* 20
should not be hard-pinned as a calibration target. **Recommendation:** Phase 2
should treat VMR ≈ 20 as the centre of a swept range in the §4.3 surface, not a
fixed input — consistent with §6.3's "magnitude is what the surface sweeps."
The note's framing already leans this way; make it explicit at task 2.3a.

### STRONG-3 — extrapolation from 4 active days to a 60–130/mo monthly Q
The Q-volume centre (~60–130 priceable queries/mo) is extrapolated from 4 active
days inside a single month, 2 of which are 27-query sprints. The note is candid
that this is the project's own sprint-driven trace, and the bracket brackets it
from above. As a *calibration range* for a surface that is *swept across the
range* (§4.3), this is defensible — the decisive object is a surface, not a point,
and the range is honestly bracketed centre-to-upper-envelope. The risk is only if
a downstream step collapses the range to a point estimate. **Recommendation:**
Phase 2 task 2.4 must sweep the full 60–130 bracket envelope; no single-Q run may
stand in for the surface. Non-blocking given the surface design.

### WEAK-1 — two OPEN items genuinely cannot be pinned from the own-trace — confirmed
Both deferrals were checked against the underlying data and the spec, and are
**genuine, not dodges**:
- *Month-end seasonality magnitude (modulation 4):* the centre `daily.csv` spans
  2026-05-08→05-19 — inside one month, no month boundary. The bracket spans one
  boundary (04→05) but ~27 days across a single boundary cannot isolate a
  reporting-cadence bump from sprint clustering. Confirmed un-pinnable from the
  own-trace. Deferral to §6.2 proxy research is spec-mandated, not invented.
- *`Q_low`:* §2.4 defines `Q_low` by *qualitative* free-tier deficiencies
  (archive/trace access, cross-subgraph curation). The metadata-only extractor
  stores only a coarse host/op per call — by the metadata-only guarantee it
  never records whether a query *needed* an archive capability. `Q_low` is
  therefore structurally unobservable in this trace. Deferral to §2.4-mandated
  proxy research is correct.
Both are correctly recorded as **non-HALT, spec-anticipated** OPEN items with the
CORR-E10P-8 / RC WEAK-2 PARTIAL fallback (no flat-fill if proxies unreachable).
This is sound. **Caveat for Phase 2:** tasks 2.2/2.3b inherit a real dependency —
if proxy research fails, the §4.3 surface degrades band→point and the iteration
goes PARTIAL. That is a *known, spec-routed* contingency, not a modeling gap, so
it does not block Phase-2 entry — but the plan must carry it forward visibly.

### WEAK-2 — λ(t) modulation 4 is committed as a *form* with an unset magnitude
Modulation 4 is "LOCKED form / OPEN magnitude." That is internally coherent (the
multiplicative end-of-month bump *shape* is §6.3-pre-committed; only its
magnitude is unset). The simulator can be *built* with the slot present and the
magnitude as a parameter — task 2.1 is not blocked. Confirmed consistent.
Observation only: the §4.6 summary table should make the form/magnitude split
explicit in one cell rather than the single word "OPEN," to prevent a future
reader treating the whole modulation as unspecified.

### OBSERVATION-1 — the four locked λ(t) forms are sound and citation-complete
The four own-trace-anchored modulations were checked against `buckets.json`:
- *Mod 1 (diurnal two-peak + weekday):* `weekday` buckets show 62/63 centre and
  142/151 bracket on weekdays; `diurnal_utc` shows genuine bimodality (centre
  peaks 11–12h and 21–22h). A two-peak Gaussian-sum over a single bump is the
  correct call. 4-part citation present and complete.
- *Mod 3 (discrete-day Bernoulli × heavy-tail multiplier):* `daily.csv` confirms
  spike-dominated days (27 vs 1; 42 vs 2) — a continuous modulation cannot
  produce this. Modelling spikes as the upper tail of the same Cox process is a
  parsimony gain, correctly noted. Citation complete.
- *Mod 5 (log-linear secular drift):* bracket per-week 2→6→25→44→74 is monotone;
  log-linear is a parsimonious, non-overfit choice for a 5-week window. Centre
  correctly used only to confirm non-stationarity, not to fix the slope.
  Citation complete.
- *Mod 2:* covered by the §3 Cox citation; correctly not duplicated.
All four carry the 4-part reference/why/relevance/connection block. Decision-
citations are **complete.**

### OBSERVATION-2 — Q ⊥ FX is consistent with spec §6.4
§6 of the note states the primary generates Q independently of FX (Cov ≈ 0 by
construction); the behavioral-coupling arm is sensitivity-only and may not rescue
a primary HALT. This matches spec §6.4 verbatim and the §8 anti-fishing carry-
forward. The anchor *supports* independence: Q is mined from research/build
sprints exogenous to COP/BRL/EUR/GBP/NGN realized variance. Consistent.

### OBSERVATION-3 — anti-fishing posture is clean
No calibration parameter is a post-hoc tuning. The mapping rule (§1.1) is pinned
on a single ex-ante criterion ("would this appear on an x402 invoice?"); Q_high
is pinned off the $399 Dune-Plus price independent of the trace; the overdisper-
sion mechanism is selected on the structured-burst evidence, not fitted to a
target VMR; the two OPEN items are deferred *rather than* force-pinned — the anti-
fishing-correct choice. The VMR ≈ 20 magnitude (STRONG-2) is the only number that
could be mis-used as a hard target; the recommendation there keeps it a swept
range. No fishing surface introduced.

---

## Phase-2-entry call

**E10 is CLEARED to enter Phase 2 (tasks 2.1–2.4).**

The calibration note locks every functional form the R6 NHPP engine must be built
against: the Cox/doubly-stochastic overdispersion mechanism (RATIFIED), the four
own-trace-anchored λ(t) modulation forms, the Q⊥FX primary structure, and the
60–130/mo Q-volume range. The two OPEN items (month-end magnitude, `Q_low`) are
genuine, spec-anticipated proxy-research deferrals that do not block the simulator
*build* — task 2.1 builds the slots; tasks 2.2/2.3b fill them. No Critical
finding; no convergent BLOCK. CORRECTIONS is **not** triggered.

The three STRONG findings are forward-carried recommendations for Phase 2, not
re-review gates: (S-1) reword the Gamma lock as a conjugacy default or carry
log-normal as a sensitivity arm; (S-2) treat VMR ≈ 20 as a swept-range centre,
not a hard target; (S-3) ensure task 2.4 sweeps the full 60–130 Q envelope rather
than a point. Phase 2 should action these in-stride.

---

## Summary

| Item | Result |
|---|---|
| Verdict | **PASS** |
| Critical findings | **0** |
| Strong / Weak / Observation | 3 / 2 / 3 |
| Cox overdispersion mechanism | **RATIFY** |
| Phase-2 entry | **CLEARED** |

**Review path:** `scratch/2026-05-20-e10-revision/ModelQA_pre_phase2_review.md`
