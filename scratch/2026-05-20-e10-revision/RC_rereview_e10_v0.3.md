# Reality-Checker Re-Review — E10 GSPS v0.3 Convex Multi-Currency Design

**Reviewer:** TestingRealityChecker (independent RC) — closure-focused second-round re-review
**Date:** 2026-05-20
**Spec under review:** `docs/specs/2026-05-20-e10-gsps-v0.3-convex-multicurrency-design.md` (391 lines, v0.3 DRAFT)
**Prior review:** `RC_review_e10_v0.2.md` (3 BLOCK, 2 STRONG, 3 WEAK — verdict NEEDS WORK)
**Posture:** read-only feasibility + truthfulness audit. No spec edits, no code, no simulation.
**Verification key:** [V] verified live this session; [I] inferred from verified inputs; [DOC] vendor/research doc.

---

## VERDICT: PARTIAL

All three prior BLOCKs are genuinely resolved — not cosmetically. The v0.3
decoupling of the measurement layer from Mento (§1.3), the restoration of the
NON-FANTASY clause (§6.2), and the central-bank-FX panel re-anchoring (§§1–3)
are real structural fixes, each traceable to a CORRECTIONS-E10-3 row and the
implementing section. The truthfulness sweep finds no new false claim.

PARTIAL not PASS because one new finding is a genuine BLOCK: the panel's
identification rests on G≈8 currency clusters, which is structurally
underpowered for any inference arm the spec proposes — including the second
arm it adds. The spec is honest about this (it flags G≈8 four times and labels
the iteration demonstration-grade), but honesty about a structural deficiency
does not remove the deficiency. v0.3 is a credible PARTIAL-track spec; it is
not PASS-ready until the 8-cluster feasibility BLOCK is dispositioned.

**1 new BLOCK, 1 STRONG, 2 OBSERVATION.**

---

## Closure verification — the 3 prior RC BLOCKs

### RC BLOCK-1 (unverified 360-cell panel, ambiguous month axis) → CLOSED

v0.2 pinned "~12 currencies × ~30 months ≈ 360 cells" as a LOCKED-pre-pin fact
with an axis ambiguous between Mento-token age and central-bank FX history.
v0.3 resolves both halves:

- **Axis disambiguated.** §1.3, §3.3, §7 field 6 all state explicitly the panel
  month is central-bank FX history — "a real rate that always exists,
  independent of any token." The Mento-token-age reading is killed outright.
- **Count no longer pinned blind.** §7 field 6 re-derives the cell count "from
  the *shortest qualifying* central-bank series at E10.0, not pinned blind";
  E10.0 (§10) is a HALT-gating precondition that drops any currency lacking a
  confirmed series. No unverified count sits inside a LOCKED field — the field
  reads "8 currencies × ~30 months" with "~30" explicitly a placeholder for the
  E10.0 re-derivation.

**Per-currency free-data verification (this session).** The 8 named currencies —
COP, BRL, KES, NGN, GHS, ZAR, EUR, GBP — were checked against each central
bank's data portal:

| Currency | Source | Free daily ~30-month series? | Status |
|---|---|---|---|
| COP | Banrep TRM | yes — reused Pair D + E5 | [V via prior-iteration reuse] |
| BRL | BCB (PTAX) | yes — standard free daily series | [I — BCB PTAX is a well-known free daily series] |
| KES | CBK | yes — daily indicative rates, free export, yearly datasets to 2003 | [V — centralbank.go.ke] |
| GHS | BoG | yes — explicit "Historical Interbank FX Rates" page, free daily | [V — bog.gov.gh] |
| NGN | CBN | daily NFEM rates, free, Excel export — BUT see caveat | [V with caveat] |
| ZAR | SARB | yes — SARB publishes free daily rand series | [I — SARB daily series is standard and free] |
| EUR | ECB | yes — ECB daily reference rates, free | [I — ECB SDW daily, canonical] |
| GBP | BoE | yes — BoE daily spot series, free | [I — BoE database daily, canonical] |

The 8-currency free-data claim is **substantially verified.** The BLOCK is
closed: the panel no longer rests on a false count, the axis is unambiguous,
and re-verification is correctly gated at E10.0.

**Caveat carried into a STRONG finding below — NGN.** The Nigerian naira
floated on **June 2023** (NFEM/willing-buyer-willing-seller unification) [V].
That is ~35 months before today — so a *daily, market-determined* NGN/USD
series with genuine realized variance does exist for the full ~30-month panel
window. But pre-float CBN "official" daily rates were a managed peg with near-
zero realized variance; if E10.0's window reaches before June 2023 for NGN it
straddles a regime break (a peg-to-float structural break, not a missing-data
gap). This is not enough to keep BLOCK-1 open — the window can be confined to
the post-float period — but the spec should flag NGN's regime-break window
explicitly at E10.0. Folded into STRONG-1.

**Verdict: CLOSED.** (with NGN window caveat → STRONG-1)

### RC BLOCK-2 (Mento m-tokens don't exist; live set is c-tokens) → CLOSED

v0.2 named both the empirical panel and the M-sketch in `m`-suffix tokens that
are not live on-chain. v0.3 resolves this cleanly:

- §1.3 makes "FX currency" (a central-bank rate) and "Mento stablecoin" (a
  token, possibly not live) **explicitly distinct objects**.
- The empirical panel (§3.3) names *currencies only* — COP, BRL, KES, NGN, GHS,
  ZAR, EUR, GBP — and §3 states "v0.3's empirical panel never references a
  token" (§1.3). I confirmed by sweep: §§1–9 contain no `m`-suffix or `c`-prefix
  token symbol used as a panel key.
- Mento tokens appear only in §13 (the Stage-2 M-sketch), and §13.5 explicitly
  flags the `c`/`m` rebrand status as a Stage-2 verification item — "only USDm
  is Live; the legacy `c`-tokens remain the live tradable assets." This is the
  honest statement v0.2 omitted from its open-items list.

The decoupling is genuine: the measurement layer is now token-free; the rebrand
risk is confined to §13 and named there. **Verdict: CLOSED.**

### RC BLOCK-3 (cohort is an undocumented phenomenon) → CLOSED

v0.2's §9 ladder asserted properties of a "cohort" a one-representative
simulation cannot deliver, and v0.2 had dropped the v0.1 NON-FANTASY clause.
v0.3 resolves this:

- **NON-FANTASY clause restored.** §6.2 makes the user's own observed query
  logs the *centre* of the Q-volume range; researched proxies *bracket* it.
  This is the v0.1 anchor v0.2 dropped.
- **Verdict ladder no longer asserts unobserved-cohort properties.** §9 states
  every verdict "names the *declared representative profile* and the *anchored
  range*, never an unobserved cohort." I checked all four rungs: PASS reads
  "for the declared representative profile across the anchored Q-volume range";
  PARTIAL, FAIL, NON-RETIREMENT are all phrased against the declared profile
  and the surface. §2.2 restricts verdict language explicitly. §2.5 bans
  counterfactual cohort scaling.
- The Q-process is reframed as a *controlled input* with a real anchor (§6.1,
  §6.2), not a free parameter — this is the substantive fix, not just wording.

The reframing is honest. One residual subtlety (not BLOCK-reopening): the
"user's own observed data-query logs" anchor is asserted but the spec does not
show those logs exist or are non-trivial — §6.2 defers the concrete value to
E10.1. This is acceptable because §10 puts the anchor calibration in E10.1
before any simulation run, and §2.4/§6.2 specify the *rule* in the spec. RC
v0.2's fix (c) — "anchor to a real observed trace" — is implemented as a rule;
the E10.1 calibration note must deliver the actual trace. **Verdict: CLOSED**
(E10.1 must produce the real trace, or the anchor degrades back to a modeler
choice — flagged as OBS-1).

**All 3 prior BLOCKs CLOSED.**

---

## New finding — BLOCK

### NEW-BLOCK-1 — G≈8 currency clusters is structurally underpowered; the iteration cannot produce a confirmatory verdict and the spec's "demonstration-grade" label does not fully discharge the problem.

**This is the feasibility verdict the re-review brief assigns to RC.**

**What the spec says.** §7 inference and §8 are honest: G≈8 is "below the
borderline-safe range for wild cluster bootstrap (size distortion persists
below G≈15–20, worst for one-sided tests near the null — exactly the §9
geometry)." v0.3's response is a *second inference arm* (randomization /
permutation across currencies) and a requirement that "both arms agree."

**Why honesty does not close it.** The brief asks: is 8 clusters viable for ANY
credible inference? My feasibility verdict: **8 clusters is structurally
underpowered for the verdict the spec wants to produce, and the second arm does
not rescue it.**

1. **The wild cluster bootstrap arm is known-distorted at G=8.** The spec says
   so itself. At G≈8 with a one-sided test near a threshold (the §9 geometry —
   "CI excludes the break-even from below"), size distortion is not a footnote;
   it is large enough that a "PASS" CI is not interpretable as a confidence
   statement. This is the spec's own admission, restated.

2. **The randomization arm has thin permutation support at G=8.** A
   permutation/randomization arm across 8 currencies draws its null
   distribution from rearrangements of 8 units. The permutation support is
   small (the achievable p-value grid is coarse — with 8 units the finest
   two-sided p-value resolution is on the order of 1/(small combinatorial
   count), and many test statistics tie). §11 item 2 itself asks Model QA to
   "confirm a randomization arm across 8 currencies has adequate permutation
   support" — the spec is *not confident* the second arm works. A second arm
   that is itself in question is not a rescue.

3. **"Both arms must agree" can make things worse, not better.** Requiring two
   underpowered arms to concur raises the false-negative rate (a real effect
   must clear two noisy gates) without fixing the false-positive distortion of
   either. It is a conservative rule, but conservatism at G=8 mostly means the
   iteration is likely to land PARTIAL or NON-RETIREMENT regardless of the
   underlying truth — i.e., the inference machinery cannot discriminate.

4. **The two-way FE makes the cluster problem worse, not better.** §7 field 6
   adds month FE (correctly — Model QA S-2). But month FE absorbs the *common*
   FX-vol component, leaving only *idiosyncratic per-currency* variation to
   identify the effect. With 8 currencies, after two-way FE, the identifying
   variation is a within-8-clusters residual. The spec correctly says the
   binding dimension is G≈8, not the ~240 cells — but does not connect that
   month FE strips out exactly the variation that 8 clusters had the most of.

**Feasibility verdict on the 8-cluster panel.** The panel can produce a
*descriptive sensitivity surface* (the §4.3 object) honestly — that part is
fine; a surface is a description, not an inference. What it **cannot** produce
is a defensible *inferential* verdict: PASS as defined in §9 ("both inference
arms put a CI on the share that excludes the break-even") is not credibly
attainable at G=8, because neither arm delivers a trustworthy CI. The
iteration is therefore structurally pre-committed to PARTIAL or NON-RETIREMENT —
which means the §9 ladder is not collectively reachable, and a "PASS" rung that
cannot in practice be reached is anti-fishing-cosmetic.

**Why this is BLOCK not STRONG.** It is not a wording defect. It determines
whether the iteration can answer its own question. The spec must either (a)
expand the cluster dimension — more currencies (the integration research listed
PHP, XOF, AUD, CAD, JPY, CHF as additional Mento currencies; if their
central-bank FX series are free and 30-month, G could reach ~12–14, still
marginal but materially better), or (b) move identification to a different
dimension entirely (e.g., a within-currency time-clustering design, or treating
(currency × sub-period) regimes as units), or (c) explicitly retire the PASS
rung and re-state the ladder as PARTIAL/NON-RETIREMENT-only, making the
demonstration-grade ceiling structural rather than aspirational. Until one of
these is chosen, the inference design does not support the verdict ladder.

§11 item 6 asks "is 8 currencies adequate for the two-way-FE panel" and item 2
asks about permutation support — the spec is *already asking* this question.
The honest answer is no, and it needs a §0.3-grade structural response, not a
sixth open item.

---

## New finding — STRONG

### NEW-STRONG-1 — NGN regime-break window is not flagged; the §8 sub-task does not protect against a peg-to-float structural break.

§3.3 and §10 (E10.0) verify *availability* of a free daily NGN series — and the
data does exist. But the naira floated June 2023 [V]. A ~30-month window
reaching back to ~late 2023 is post-float and clean; a window reaching to early
2023 straddles the peg-to-float break, where pre-break realized variance is
near-zero by administrative fixing, not by low FX risk. If E10.0 takes "shortest
qualifying series" mechanically, NGN could anchor the panel window to a length
that forces other currencies' windows back across NGN's regime break — or NGN's
own pre-float cells enter the panel as artificially-low-variance observations.

This is STRONG not BLOCK because it is fixable at E10.0 (confine the NGN window
to post-June-2023; the panel window is the intersection of *post-structural-
break* qualifying series, not raw availability). But the spec's E10.0 step
(§10) only says "confirm per-currency free 30-month daily availability" — it
does not say "confirm the series is free of an administrative-peg regime break
within the window." Add that check. The same caveat is latent for any EM
currency with a managed-float history in the window (GHS and KES both had
periods of heavy management) — E10.0 should screen all 8 for within-window
regime breaks, not just availability.

---

## §11 open-items disposition

| # | §11 item | RC disposition |
|---|---|---|
| 1 | Break-even derivation timing (Stage-1/2 firewall) | **Acceptable deferral.** The break-even is a pinned Stage-2-derived *input* to the Stage-1 pre-pin (§5.4) — importing a derived number across the firewall is legitimate (the firewall bans *estimation* leakage, not pinned-parameter import). Model QA owns whether it is genuinely derivable at spec stage. No RC objection. |
| 2 | Eight clusters + dual inference | **GENUINE BLOCKER — see NEW-BLOCK-1.** The spec asks the right question; the answer is structural and cannot be left as an open item. |
| 3 | `Q_low` pinning rule | **Acceptable deferral.** The rule is in the spec (§2.4); the value is pinned at E10.1 before any simulation run. Anti-fishing discipline is preserved because the *rule* is frozen ex ante. RC concurs. |
| 4 | Q–FX independence in the primary | **Acceptable deferral.** Independence as primary with coupling as a pre-committed sensitivity arm is defensible; the choice is declared and frozen (§6.4). Model QA owns the sign-relevance detail. |
| 5 | Surface-based verdict operationalization | **Acceptable-with-caveat.** "Across the whole anchored range" needs an operational rule (endpoints vs full sweep). Low-risk because the §7 field 7 HALT is also range-defined; but the spec should specify the inspection grid at E10.3. Genuinely deferrable to E10.3. |
| 6 | NGN / dropping below 8 currencies | **GENUINE — feeds NEW-BLOCK-1 and NEW-STRONG-1.** "Is 8 adequate" — RC answer: no, 8 is the floor of viability and probably below it (NEW-BLOCK-1). And yes, dropping below 8 at E10.0 *should* trigger a HALT — the spec should pin that, not leave it as a reviewer question. |

Net: item 2 is a live BLOCK; item 6 is a live BLOCK/STRONG feed; items 1, 3, 4,
5 are genuinely deferrable.

---

## Truthfulness sweep — new factual claims in v0.3

- **$0.01 x402 per-query price.** Verified in the v0.2 round via live header
  decode (`amount:"10000"` ÷ 10^6) [DOC, VERIFIED]. v0.3 carries it correctly,
  scopes it as a *cost-model parameter* not a tool purchased (§1.1, §9), and
  pins re-verification at E10.0. **Sound.**
- **$399 Dune Plus price.** v0.3 §2.3 pins `Q_high = 39,900 = $399 ÷ $0.01` per
  RC STRONG-1. This session: Dune's live pricing page did not render a
  structured price to the fetcher; third-party 2026 sources cite **$390/mo per
  user (Dune Pro)** and the research input cited $399. The $390/$399 figure is
  **mildly unsettled** — but v0.3 correctly treats it as a model cap, never a
  purchase, and `Q_high` is explicitly "a modeling boundary with a behavioral
  substitutability assumption attached, not a sharp empirical cutoff" (§2.3).
  Because `c=$0.01` is a scale-invariant multiplier (§4.1), neither $390 nor
  $399 biases the FX-variance share; only the band edge moves. **Acceptable as
  a model parameter; the residual $390/$399 ambiguity is non-load-bearing.**
  Minor: §2.3 states $399 as "verified" — it is third-party-sourced, not probe-
  verified; "verified" slightly overstates. OBSERVATION, not a finding.
- **8-currency free-data claim.** Verified this session per the BLOCK-1 table —
  KES, GHS, NGN [V]; COP reused [V]; BRL, ZAR, EUR, GBP [I, canonical free
  daily series]. **Substantially sound;** NGN carries the regime-break caveat
  (NEW-STRONG-1).
- **R6 ~10–15% reuse restatement.** §6.5 restates v0.2's "~25–30%" honestly,
  separating ~10–15% reusable *code* (three-tier scaffolding, dual-SHA pinning,
  `stochastic_fx` generators) from a reusable *design* (the R6 NHPP blueprint,
  19 tasks, never coded, "carries its own implementation risk"). This matches
  the `dev_ai_cost_model_evaluation` finding and resolves RC STRONG-2 exactly.
  **Sound and honest.**
- **"Decomposition is exact in log space" (§4.2, leading-order caveat deleted).**
  Matches the Model QA Algebra note — `Δlog cost = Δlog Q + Δlog FX` is an
  exact identity since `c` is constant. **Sound** (Model QA owns the algebra;
  RC concurs the deletion is correct).

No new false claim. The sweep is clean.

---

## OBSERVATIONS

### OBS-1 — The NON-FANTASY anchor is a rule, not yet a delivered trace.

§6.2 anchors Q's centre to "the user's own observed data-query logs." v0.3
specifies this as a rule and defers the concrete trace to E10.1. This closes
BLOCK-3 *as a spec* — but the anti-fantasy guarantee is only as good as the
E10.1 calibration note. If the user's actual query logs turn out sparse or
non-representative (the dev_ai_cost precedent was n=1, 28 weekday rows — too
sparse to estimate anything), the "anchor" degrades back to a modeler choice.
E10.1 must deliver a genuine, non-trivial observed trace, or the iteration
should HALT at E10.1 rather than proceed on a thin anchor. Not a finding —
the spec's sequencing is correct — but flagged so E10.1 is held to it.

### OBS-2 — CORRECTIONS-E10-3 is an exemplary visible record; §0.4 banned-moves list is genuine.

The six-row CORRECTIONS-E10-3 table (§0.3) traces every fix to its review
source and implementing section; §0.4 enumerates what the corrections do NOT do
(no post-hoc pre-pin relaxation, no panel-window extension, no silent rename,
no prior-β import, no x402-substrate un-parking). This is the HALT-checkpoint
discipline done correctly — nothing is silently changed. The x402-on-Base
substrate remains correctly NON-RETIREMENT-PENDING-MATURITY (§9, re-check
2026-11). These sections are the spec's strongest, as in v0.2.

---

## Summary

| Finding | Severity | One-line |
|---|---|---|
| RC BLOCK-1 | CLOSED | Panel re-anchored to central-bank FX history; axis disambiguated; count re-derived at E10.0; 8-currency free-data substantially verified |
| RC BLOCK-2 | CLOSED | Measurement layer decoupled from Mento; panel names currencies only; tokens confined to §13 with rebrand flagged |
| RC BLOCK-3 | CLOSED | NON-FANTASY clause restored (§6.2); verdict ladder reads against declared representative profile + anchored range, never an unobserved cohort |
| NEW-BLOCK-1 | BLOCK | G≈8 clusters structurally underpowered; neither inference arm delivers a credible CI; the §9 PASS rung is not practically reachable |
| NEW-STRONG-1 | STRONG | NGN floated June 2023 — E10.0 must screen all 8 currencies for within-window administrative-peg regime breaks, not just availability |
| OBS-1 | OBSERVATION | NON-FANTASY anchor is a rule; E10.1 must deliver a genuine non-trivial observed trace or HALT |
| OBS-2 | OBSERVATION | CORRECTIONS-E10-3 and §0.4 banned-moves are an exemplary visible record |

**3 prior BLOCKs CLOSED. 1 new BLOCK, 1 STRONG, 2 OBSERVATION. Verdict: PARTIAL.**

The closure work is genuine — all three v0.2 BLOCKs are resolved structurally,
not cosmetically, and the truthfulness sweep is clean. v0.3 is a materially
better spec. It is not PASS because a PASS requires all 3 prior BLOCKs CLOSED
*and no new BLOCK*; NEW-BLOCK-1 (the 8-cluster feasibility problem) is a real
BLOCK. The spec is honest that G≈8 is marginal, but honesty about a structural
deficiency is not a resolution of it. v0.3 needs one more revision cycle: a
§0.3-grade structural response to the cluster dimension — expand currencies,
move the identifying dimension, or formally retire the PASS rung and lock the
ceiling at PARTIAL. With that, the spec is PASS-track.
