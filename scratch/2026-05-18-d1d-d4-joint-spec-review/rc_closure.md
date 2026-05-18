# Reality Checker — D1.D + D4 Joint Iteration Spec v0.2 (CLOSURE-ONLY)

**Reviewer:** Reality Checker (default-NEEDS_WORK, evidence-based)
**Date:** 2026-05-18
**Target:** `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2 (343 lines)
**Scope:** Closure verification of v0.1 NEEDS_WORK verdict; C1–C4 + S1–S6 + 7 nits

---

## Closure verdict

**APPROVED_WITH_NITS** — All four CRITICAL items (C1–C4) are substantively
closed in the v0.2 CORRECTIONS-B block and reflected in the body §1, §3.1, §4.1,
§4.3, §7. The four resolutions are *correct in direction* and *honestly
costed* (composite framing, ratio-of-means primary, spline removed, ρ̄-floor
withdrawn). Four of six Strong recs (S1, S3, S4, S5) are integrated inline;
S2 partially deferred to notebook 05; S6 partially closed via §7 collective-
exhaustiveness rewrite (the explicit Joint aggregation matrix from S6 is not
reproduced verbatim but the four-row precedence resolves the same cases). One
NEW low-priority risk introduced by v0.2 amendments is flagged below
(§"NEW issues") but does not block dispatch.

**Implementation may proceed on Notebook 01.** Remaining nits are
implementation-time fixes, not pre-dispatch blockers.

---

## C1–C4 closure check

### C1 (Joint-identity wallet non-overlap) — CLOSED

v0.2 §1 explicitly downgrades the identity to "aggregate-level transmission
proxy, NOT wallet-level identity," names the 30–60% overlap, and adopts
resolution-path (B) "aggregate-with-bias-disclosure" from the three I offered.
§4.3 row "Primary estimand" uses ratio-of-means on aggregates; the
"Bias direction disclosure" row commits to Phase-1 ρ̂ *understating* the true
wage→capital rate via two named mechanisms (non-overlap external CF inflows,
speculator round-trips in E). This is the honest framing I asked for. Path (B)
was my second-preference resolution (Path 1 — restrict-to-overlap — would have
been more identity-coherent at the cost of cohort size); the choice is
defensible and the cost is explicitly disclosed. **Closure: correct direction,
acceptable execution.**

### C2 (Layer C wage/saver/speculator bias direction) — CLOSED

v0.2 §1 walks back the strong "post-Keynesian wage→capital ratchet rate"
framing I flagged. New language: ρ̂ is "a composite indicator that conflates
wage receipts, savings inflows, and speculator round-trips — NOT … the pure
wage→capital ratchet rate." §4.3 "Bias direction disclosure" row pins the
specific bias mechanisms. §13 CORRECTIONS-B RC C2 row codifies that pure-rate
attribution requires Phase 2 Layer C decomposition (deferred, not promised).
I had specifically asked for a "bias-direction table" — the spec opted for
prose-disclosure-with-mechanism-naming instead of a table, which is
substantively equivalent and acceptable. **Closure: correct direction,
prose-instead-of-table is acceptable.**

### C3 (Cubic-spline quarterly→monthly) — CLOSED

v0.2 §4.1 fully implements my preferred Path-2 alternative: COP/USD spot daily
(natively monthly, no interpolation) is the PRIMARY X; Banrep services-credit
is demoted to quarterly-only validation (not interpolated). The spline is
REMOVED entirely (§13 CORRECTIONS-B MUST-1 explicit: "Spline interpolation
REMOVED"). Bonus: §4.1 adds a stationarity gate (ADF + KPSS) and switches the
primary to Δ-spec (first-differences) to close the spurious-regression-via-
Granger-Newbold risk — this is a tighter posture than my original C3 ask.
**Closure: correct direction, tighter than asked.** Note: §5.2 row "Banrep
BoP services-credit" still says "interpolated to monthly via cubic spline" —
this is a stale fragment that contradicts §4.1 + §13 MUST-1. Flagged as a NEW
issue below (see N-NEW-1); not blocking.

### C4 (Verdict criteria exhaustiveness + ρ̄≥0.05 floor undertheorized) — CLOSED

v0.2 §7 is rewritten as a 4-row table with explicit "Headline trigger" +
"Population scope reminder" columns, and a "Collective exhaustiveness check"
clause at the bottom claiming every (β-sign, ρ̂-sign, GPD-ξ-exclusion,
data-availability) state maps to exactly one row, with precedence resolving
edge cases to PARTIAL-PASS. The undertheorized ρ̄ ≥ 0.05 floor is REMOVED
(§4.3 row "Magnitude floor": "Floor REMOVED from v0.1. No pre-specified
ρ̂ ≥ 0.05 threshold (undertheorized — RC C4 found no derivation)"). §13
CORRECTIONS-B RC C4 row codifies the removal. This is the strongest possible
closure: rather than retroactively deriving a floor, the spec admits no
derivation existed and drops the criterion. **Closure: correct direction,
strongest possible execution.** The collective-exhaustiveness claim is
defensible on inspection — every cell I had previously flagged (β>0
sig + ρ̂ ∈ [0, 0.05]) now lands in PARTIAL-PASS via the sensitivity-
concordance trigger, which is collectively-exhaustive with FAIL and
NON-RETIREMENT.

---

## S1–S6 closure check

**S1 (Colombia-share scalar sensitivity insufficient) — CLOSED.** §4.3 now
specifies a 5-arm sensitivity sweep (10/10, 20/20, 35/35, asymmetric 20/35
and 35/20) covering both magnitude-uniform and asymmetric-scalar cases I
asked for. §7 NON-RETIREMENT row adds "Colombia-share-scalar magnitude-
agreement check (RC S1 — 20% scalar deviates >2× from independent
triangulation)" as a NON-RETIREMENT trigger. The Chainalysis citation gap
I flagged is not resolved with a specific page reference but is now bounded
by the 5-arm sensitivity envelope — acceptable substitute.

**S2 (Pre-2020 USDC gap + COVID-epoch dominance) — PARTIALLY CLOSED.**
§2 transparency disclosure row 3 mentions "pre-2020 USDC has no Kraken-direct
USD market" as a known gap. §13 CORRECTIONS-B mentions "pre-2020/COVID
regime-break test deferred to notebook 05 sensitivity." I had asked for an
explicit regime-break test (Chow / Bai-Perron) at 2022-01 or 2022-06. The
deferral to notebook 05 is acceptable but should be enforced at notebook-05
review time; flag for closure-review-of-implementation.

**S3 (Multiple-comparison protection under-specified) — CLOSED.** New §3.1
"Multiple-testing protection" implements the single-primary commitment I
asked for: "ONE primary spec per estimand; sensitivity arms judged via
sign-concordance only, NOT independently inferential"; Bonferroni-equivalent
posture; banned-moves list. This is exactly the anti-fishing tripwire I asked
for, expressed cleanly.

**S4 (M-sketch §8 Stage-1-only banner) — CLOSED.** §8 now opens with an
explicit STAGE-2 FIREWALL paragraph: "this section is descriptive only. NO
M-sketch position is implemented, simulated, deployed, or sized within this
iteration. The iteration's verdict … depends solely on §4-§7 estimands."
This is precisely the low-cost guardrail I requested.

**S5 (Population-scope honesty in verdict criteria) — CLOSED.** §7 every
verdict row now has an explicit "Population scope reminder" column carrying
the 15-35% sub-cohort caveat. PASS row reads "Result applies to crypto-rail
sub-cohort only (15-35% of broader cohort); off-rail wage flows invisible."
Exactly what I asked for.

**S6 (Pre-pin commitment on D1.D PASS × D4.1 FAIL aggregation) — PARTIALLY
CLOSED.** The explicit 4×3 aggregation matrix I drafted is NOT reproduced
verbatim in §7. Instead, §7 collective-exhaustiveness clause resolves edge
cases by precedence ("Edge cases (PARTIAL on one estimand + PASS on another)
resolve to PARTIAL-PASS by precedence"). This is substantively equivalent
for the (D1.D PASS, D4.1 FAIL) case — it lands in PARTIAL-PASS via the §7
FAIL row condition (c) "D4.1 USDC-only AND USDT-only AND pooled all fail
ξ exclusion" + the precedence rule. The aggregation is implicit-via-precedence
rather than explicit-via-matrix; acceptable but slightly less audit-friendly.
Flag for implementation: notebook 06 must reproduce the implicit aggregation
explicitly when emitting the verdict.

---

## Nit closure

| Nit | v0.2 status |
|---|---|
| N1 (Kalecki-Levy attribution) | DEFERRED to implementation (LaTeX write-up scaffold in nb 06 can add). Not closed; not blocking. |
| N2 (MDES_SD=0.40 vs β≥0.10 derivation) | DEFERRED. §3 still asserts MDES_SD=0.40; §4.1 still asserts β ≥ 0.10. No CORRECTIONS-C block. Deferred to implementation. Not blocking but flag for notebook 02 pre-pin memo. |
| N3 (Tron tagging confirmation) | DEFERRED. §5.1 still lists Tron in chain set without confirming tagging coverage. Open item #7 in §14 raises a different point. Flag for Week-1 task: confirm Tron tagging or remove. |
| N4 (Per-notebook trio count) | DEFERRED. §6 still says "YES" in trio-HALT column without per-notebook trio counts. Implementation-time fix. |
| N5 (gpd_pot.py Callable-tier fit) | DEFERRED. §9 scaffold unchanged. Implementation-time check during SIM-INFRA work. |
| N6 (D4.1 pre-pin = "frozen at D4 gate close" framing) | DEFERRED. §3 unchanged. Implicit via CORRECTIONS-A signed reference; not blocking. |
| N7 (Week-3 plan compression) | DEFERRED. §10 unchanged. The 3-week estimate is aggressive; flag for milestone tracking, not a spec blocker. |

All 7 nits are deferred to implementation; none blocking. This is the
expected disposition for nits per my v0.1 review ("MAY fix").

---

## NEW issues introduced by v0.2 amendments

### N-NEW-1 (LOW severity, NOT blocking): §5.2 stale spline reference

§5.2 data-sources table row "Banrep BoP services-credit" still reads
"Quarterly 2018-Q1 → 2025-Q4, interpolated to monthly via cubic spline."
This contradicts §4.1 (spline removed; services-credit demoted to quarterly
validation) and §13 CORRECTIONS-B MUST-1 ("Spline interpolation REMOVED").
This is a documentation-consistency bug introduced by the v0.2 autofix not
propagating fully into §5.2. Fix: edit §5.2 row to read "Quarterly 2018-Q1 →
2025-Q4, used as quarterly-frequency validation only (no interpolation per
§4.1 + §13 MUST-1)." Not blocking dispatch — §4.1 governs because it is the
pre-pin section.

### N-NEW-2 (LOW severity, NOT blocking): §13 closes "Notebook 14" duplicated heading

§13 (CORRECTIONS-B) and §14 (Open items for closure re-review) and §14
(Anti-fishing closure) — there are TWO sections labeled §14 (line 322 "Open
items" + line 333 "Anti-fishing closure"). This is a numbering collision
introduced when CORRECTIONS-B was inserted as §13 without renumbering the
trailing sections. Fix: renumber Anti-fishing closure to §15. Cosmetic only.

### N-NEW-3 (LOW severity, NOT blocking): §4.3 partition residual ambiguity

§4.3 off-ramp decomposition row: `ρ̂_window = 1 − off_ramp_ratio −
consumption_ratio + external_inflow_ratio + residual`. The sign structure
implies `consumption_ratio` is subtracted from the wage→capital fraction
(consumption is leakage), but `external_inflow_ratio` is added (external
sources of CF that didn't flow through E). The `residual` is unexplained.
This is correctly flagged as "NOT a clean identity" per the CR strong rec,
but the residual sign-expectation is not pre-pinned. Acceptable at spec stage
since the row is auxiliary diagnostic, not a verdict input. Flag for notebook
04: pre-pin a sign-and-magnitude expectation for `residual` before fitting.

### N-NEW-4 (INFORMATIONAL): §14 open item #8 stationarity-gate AND-vs-OR

§14 open item #8 raises whether "ADF p<0.05 AND KPSS p>0.05" is too
restrictive (vs. OR). The conservative AND-conjunction is the right choice
for a pre-pin: it forces the burden of proof onto the log-level spec rather
than the Δ-spec. If both tests disagree, defaulting to Δ-spec is the safe
choice — Δ-spec under-rejection is less harmful than log-level spurious
regression (Granger-Newbold). Spec author's question is well-posed but the
AND-conjunction should stay. Not a blocking item.

**None of the four NEW issues blocks dispatch.** All are documentation-
consistency or implementation-time refinements. The autofix cascade is
substantively clean — the only true regression is N-NEW-1 (stale §5.2
fragment) and it is contradicted by the governing §4.1 + §13 sections.

---

## Pass/fail on autofix completeness

**PASS.** All four Critical items (C1–C4) are correctly resolved in the
v0.2 CORRECTIONS-B block and reflected in the spec body. Of six Strong
recommendations, four are fully integrated (S1, S3, S4, S5) and two are
acceptably partial (S2 deferred to notebook-05 sensitivity; S6 resolved
implicitly via §7 precedence rather than explicit aggregation matrix).
All seven nits are deferred to implementation as expected.

The autofix-all directive 2026-05-18 was executed correctly. The CR MUST-1
(spurious regression) closure is a notable bonus — by switching to Δ-spec
primary + stationarity gate, the spec closes a risk I did not flag in v0.1
but which would have surfaced as a separate issue in any econometrically-
rigorous review. The §4.1 + §3.1 + §4.3 trio is now tighter than v0.1.

The four NEW issues (N-NEW-1 through N-NEW-4) are low-severity documentation-
consistency points that should be cleaned at next-touch but do not block
Notebook 01 dispatch.

**Updated verdict: APPROVED_WITH_NITS.** Implementation of Notebook 01
(`01_data_eda.ipynb`) may proceed against v0.2. Recommend the spec author
fold N-NEW-1 (§5.2 stale spline reference) into a v0.2.1 documentation pass
at next-touch, but this is not a dispatch blocker.

---

## Evidence summary

- v0.2 spec read in full (343 lines, all 14+1 sections including duplicate §14).
- v0.1 review re-read in full (450 lines, all 4 Critical + 6 Strong + 7 nits).
- Cross-referenced §1, §3.1, §4.1, §4.3, §7, §8, §13 against the C1–C4 / S1–S6
  asks in v0.1.
- Confirmed §13 CORRECTIONS-B explicitly maps to each MUST-1..4 / RC C1..C4
  closure.
- Confirmed §14 (open items) closes #1–#6 as resolved with strikethrough,
  raises #7–#8 as NEW low-severity questions (acceptable).
- No re-litigation of CORRECTIONS-A (D4.1 prior) per orchestrator scope.
