# Reality-Checker Review — E10 GSPS v0.2 Convex Multi-Currency Design

**Reviewer:** TestingRealityChecker (independent RC)
**Date:** 2026-05-20
**Spec under review:** `docs/specs/2026-05-20-e10-gsps-v0.2-convex-multicurrency-design.md` (330 lines, v0.2 DRAFT)
**Posture:** read-only feasibility + truthfulness audit. No spec edits, no code, no simulation.
**Verification key:** [V] verified live this session; [I] inferred from verified inputs; [DOC] vendor/research doc.

---

## VERDICT: NEEDS WORK

The convex reframe (§4 FX-variance-share decisive object) is the spec's genuine strength
and is anti-fishing-honest. But the spec rests on a **factually false panel-size claim**
that propagates into the pre-pin (§7 field 6), the power posture, and the inference
geometry. The "~12 currencies × ~30 months = ~360 cells" panel does not exist as
described. Fixing it is not a wording patch — it changes N, the cluster count, and the
bootstrap choice. Three BLOCK findings, two STRONG, three WEAK, two OBSERVATION.

**Single biggest truthfulness risk:** the spec asserts a ~30-month panel history for
~12 Mento currencies. Verified launch dates show several panel currencies (cNGN, cCHF,
cJPY) went live **June 2025 — ~11 months ago**, and the live tradable tokens are the
legacy `c`-series, not the `m`-suffix tokens the spec names (only **USDm is "Live"**;
the other 11 `m`-tokens are "Coming Soon" on mento.org/stablecoins [V]). The panel as
specced collapses; this is the load-bearing failure.

---

## BLOCK findings (must fix before PASS)

### BLOCK-1 — The ~30-month panel window is not available for most panel currencies.

**Claim (§7 field 6):** "Panel cell = (currency, month); ~360 cells (~12 currencies ×
~30 months)."

**Why it fails truthfulness/feasibility:** the panel cell axis is *months of Mento
on-chain currency existence* — but §3 actually defines X as **realized variance of
central-bank FX rates**, which is independent of Mento token launch dates. The spec
conflates two different "months" — and both readings break:

- If the panel month is **central-bank FX history**: 30 months of free daily FX is
  available for COP/BRL/KES/NGN/GHS/ZAR/EUR/GBP [V — Banrep, BoG, CBK, CBN, ECB, BoE
  all publish free series]. Under this reading the panel does NOT need Mento at all
  and the "12 currencies" framing is fine — but then the *cohort* (a Mento-currency
  Web3 analyst) is decorative, because X is just a sovereign FX series the iteration
  could have built without any Mento dependency. The Mento panel is then a naming
  device, not an identifying substrate.
- If the panel month is **cohort/substrate existence** (the §6 simulation runs
  representative analysts "calibrated to that currency's market," which implies the
  Mento-currency market): verified launch dates kill it. cNGN/cCHF/cJPY launched
  **June 2025 [V]** — ~11 months. cGHS proposal October 2024 [V]. cKES operational
  ~mid/Q3-2024 [V]. cCOP launched on the Mento platform (date per `integration_blockers`
  §1.1 "Yes — launched"). The currencies do **not** share a common 30-month window.

The spec never resolves which "month" the panel runs on. Either way the "~12 × ~30 =
360" arithmetic is presented as a fact and is not one.

**What would fix it:** (a) state explicitly that the panel month is central-bank FX
history (real, 30-month-available), and (b) then honestly disclose that the Mento
currency set only restricts *which* sovereign FX series qualify — it is not itself the
data substrate — and (c) drop the "~30 months" as a pinned number or re-derive it from
the *shortest* qualifying central-bank series after E10.0 verification, not before.
Until E10.0 runs, "~360 cells" is an unverified assumption sitting inside a LOCKED
pre-pin field. A pre-pin field cannot contain an unverified count.

### BLOCK-2 — The named currency panel (`m`-suffix tokens) is not live; the live set is the legacy `c`-tokens, and the spec treats the rebrand as a deferred footnote when it is a substrate-identity question.

**Claim (§2.2, §13.2):** panel currencies "COPm, BRLm, KESm, NGNm, …"; M-sketch on
"COPm/USDC, BRLm/USDC."

**Verified [V] 2026-05-20:** mento.org/stablecoins lists exactly **one** token as
"Live" — **USDm** — and EURm, BRLm, KESm, PHPm, COPm, XOFm, NGNm, JPYm, CHFm, ZARm,
GBPm all as **"Coming Soon."** The 15-currency count the spec and `integration_blockers`
cite is the legacy `c`-token set (cUSD, cEUR, cREAL, cKES, cCOP, …), confirmed live on
Celo. The `m`-suffix rebrand is mid-rollout: the names the spec uses as panel keys are
**not the on-chain symbols today.**

**Why it fails truthfulness:** the spec writes the panel and the M-sketch entirely in
`m`-suffix names and relegates verification to E10.0 (§10) and §11 is *silent* on it —
§11 lists 6 open items and the rebrand is not one of them. A spec that pins a currency
panel should not name it in symbols that do not exist on-chain. This is not cosmetic:
if a reader (or a downstream agent) takes "COPm/USDC" literally, the M-sketch references
a non-existent pair.

**What would fix it:** (a) state the panel in the `c`-names that are actually live, or
explicitly note "`c`-names are the live on-chain symbols; `m`-names used here are the
post-rebrand target"; (b) promote the rebrand to a §11 open item; (c) since the iteration
is simulation-driven and X is central-bank FX (not Mento on-chain prices), the cleaner
fix is to **decouple the cohort label from the data substrate entirely** — see BLOCK-1.

### BLOCK-3 — The cohort is a phenomenon that does not yet exist, and the spec's "simulation posture" does not fully clear the fantasy threshold.

**Claim (§6, §2):** the iteration simulates "one representative analyst per currency …
calibrated to that currency's market."

**Test against the fantasy-threshold rules** (`memory/project_abrigo_portfolio_prioritization_with_fallback.md`,
4-dimension table):

| Dimension | Acceptable | E10 v0.2 status |
|---|---|---|
| Input data | real public data | **PARTIAL** — X (FX) real [V]; price $0.01 real [V]; **Q fully generated** |
| Counterfactual scope | "what would an operator look like under observed dynamics" | **RISK** — "Web3 data analysts in Mento-currency countries who pay for data via continuous streams" is closer to "what would Colombia look like if it had a thriving Bittensor scene" — projecting a cohort whose existence is unverified |
| Pre-pin discipline | assumptions declared before running | OK on paper (§7) — but `Q_low`, `Q_high`, the representative-analyst workflow, query-mix are all *unpinned* (§11 item 2 admits `Q_low` is "under-identified") |
| Output framing | "hypothetical operator under observed dynamics" + caveat | **WEAKEST POINT** — §9 PASS action reads "FX volatility confirmed as the dominant cohort cost-stream risk." That asserts a property *of a cohort*. The honest framing is "of a *simulated representative profile*." |

**Why it fails truthfulness:** the dev_ai_cost evaluation (§O-2) is explicit — the real
analog cohort (one developer, 28 weekday rows) was too sparse to estimate anything, and
that is the *direct precedent* for E10. But E10's substrate is younger still: x402-on-Graph
is 8 days old, and a population of Mento-currency-resident analysts paying x402 streams
for data is **not a documented phenomenon** — the spec offers zero evidence such users
exist in any number. The simulation is therefore not "a hypothetical operator under
observed global dynamics" (acceptable); it is closer to "what the economics *would* look
like if this cohort existed" (fantasy). The spec's own §2.4 bans "counterfactual cohort
scaling" and §6.3 says it "does not fabricate a cohort population" — good — but emitting
"one representative analyst per currency calibrated to that currency's market" when no
such analyst is known to exist *is* fabricating a cohort, just at N=1-per-currency
instead of N=many.

**What would fix it:** (a) the verdict-ladder PASS/PARTIAL actions (§9) must be reworded
so no verdict asserts anything about a "cohort" — only about a *declared representative
profile*; (b) the spec must add a sentence stating plainly that the analyst cohort is
*hypothetical and unobserved*, not merely "too young to enumerate" — the §6.1 phrasing
"too young to observe a panel … empirically" implies the cohort exists but is unmeasured,
which is not established; (c) ideally, anchor the representative profile to a *real*
observed data-consumption trace (dev_ai_cost's own §9 v0.1 E10-Sim clause did exactly
this — "the consumption profile is the user's own observed profile" — v0.2 dropped that
anchor and is weaker for it). Without (c), the simulation rests on a profile picked by
the modeler, which is dimension-1 and dimension-2 fantasy.

---

## STRONG findings

### STRONG-1 — Q_high is pinned off $390 when the verified price is $399; the model cap is not defensible as primary.

**Claim (§2.2, §2.3, §11 item 1):** `Q_high = 39,000 = $390 ÷ $0.01`; the $9 gap to the
observed $399 is a "calibration note" with a `Q_high = 39,900` sensitivity arm.

**Verified [V] 2026-05-20:** Dune Plus is **$399/mo** — confirmed independently against
dune.com/pricing and multiple 2026 sources; the research input `x402_subgraph_design_space`
§3.1/Open-Q1 also says $399 and explicitly recommends "v0.2 should update to $399."

**Why it is STRONG not BLOCK:** the spec *flags* the discrepancy honestly (§2.3, §11),
so it is not a hidden error. But the resolution is backwards: it keeps a **stale, wrong
number ($390) as primary** because "it is the figure carried in v0.1 and the brainstorm."
That is precedent-deference, not evidence-deference. The research input the spec itself
cites recommends $399. `Q_high` is a pre-pinned field (§7 frozen); pinning it off a known-
wrong figure means the *primary* spec is built on a falsified input while the *correct*
value is demoted to a sensitivity arm.

**What would fix it:** re-pin `Q_high = 39,900` off the verified $399; keep `39,000` as
the sensitivity arm if desired. The reviewer mandate in §11 item 1 explicitly asks RC to
"rule on whether the live $399 should be primary" — ruling: **yes, $399 should be
primary.** $390 has no evidentiary basis; it is a transcription artifact.

### STRONG-2 — The R6 "resurrection" is a spec, not an asset; "~25-30% reusable" overstates what transfers.

**Claim (§6.2):** reuse ~25-30%, including "the R6 NHPP design blueprint … adopted as
the architecture."

**Verified against `dev_ai_cost_model_evaluation` [DOC]:** R6 is "a spec with a 19-task
plan and **zero code**" (§S-1, §1.B). The evaluation is blunt: "do not budget E10 as
'adapt an existing model.' Budget it as 'implement the R6 simulation spec for a new
substrate, then build a new vol-on-vol estimator on top.'" The genuine reusable code is
narrow: `stochastic_fx/generators.py` (FX paths) + engineering scaffolding (SHA pinning,
Hypothesis property). Everything labeled "reuse" under R6 is *design reuse* — reading a
document.

**Why it is STRONG:** §6.2 is *mostly* honest — it does say "the R6 spec is a design +
19-task plan with zero implementation" and lists the simulation engine under "build
fresh." But the headline "~25-30% reuse" rolls a *design document* into a "reuse"
percentage alongside actual code, which inflates the apparent maturity of the asset. A
design blueprint that has never been executed carries unmodeled implementation risk —
the 19-task plan was never stress-tested by contact with code. The honest figure is
closer to "~10-15% reusable code; the rest is a fresh build guided by an unproven design."

**What would fix it:** restate §6.2 to separate "reusable code (~10-15%: stochastic_fx
generators + scaffolding)" from "reusable design (the R6 blueprint, unimplemented, carries
its own risk)." Do not present a design document as a fractional reuse credit.

---

## WEAK findings

### WEAK-1 — The 0.30 material-share threshold rests on "materiality," and §11 item 4 admits it.

§7 field 3 pins FX-variance share ≥ 0.30; §11 item 4 concedes the rationale is
"materiality, not a power calculation." This is *better* than a fished threshold — it is
pinned before data and frozen, and the spec bans post-hoc adjustment. But 0.30 is a round
number with no derivation. The anti-fishing risk is low (it is locked ex ante and a
HALT-on-Q-dominance verdict exists), but a reviewer cannot *confirm* 0.30 is defensible
because there is nothing to check it against. Acceptable as a *declared* convention IF the
spec adds one sentence on *why 0.30 and not 0.20 or 0.50* — e.g., a reference to a
variance-share materiality convention elsewhere in the portfolio. As written it is
defensible only as "an honest arbitrary floor," which the spec should say outright.

### WEAK-2 — The three-way variance decomposition is "leading order"; §11 item 3 defers the exact algebra.

§4.2 states `Var(cost) = FX + Q + cov` "to leading order in log-returns." `cost = Q·c·FX`
is a product of two stochastic factors; the exact variance carries higher-order and
interaction terms. The FX-variance *share* is the decisive object (§4.3) — if the
higher-order terms are non-negligible, the share estimate is biased and the 0.30 gate is
applied to a mismeasured quantity. The spec defers the exact form to E10.2. This is an
acceptable *deferred* item only if E10.2 is genuinely required to produce the exact
decomposition before any share is computed — the sub-task order (§10) does put
decomposition in E10.2, so the sequencing is fine. Flag: the leading-order share should
never be reported as the verdict object; only the exact-decomposition share. The spec
should say so explicitly in §7 field 2.

### WEAK-3 — "Demonstration-grade" power posture is asserted but N_MIN reasoning is loose.

§8 says the ~360-cell panel "clears N_MIN at the cell dimension." With BLOCK-1
unresolved, 360 is not established. Separately, with ~12 currency clusters the spec
correctly pre-commits a wild cluster bootstrap (Webb weights) for small-G — good. But
"clears N_MIN = 75" at the *cell* level while the *effective* inference unit is the
*currency cluster* (≈12) is the standard small-cluster trap: 360 cells with 12 clusters
is not 360 independent observations. The demonstration-grade posture (§7 field 5) is the
honest ceiling and is correctly chosen, but §8's "clears N_MIN" sentence is misleading
about which dimension carries identification. Reword to: "N_MIN is cleared at the
cell dimension; identification rests on ~12 currency clusters and is demonstration-grade
for that reason."

---

## OBSERVATIONS

### OBS-1 — x402 $0.01/query: claim is sound, stability is the open risk.

The $0.01 flat price is well-verified — the research input decoded a live `payment-required`
header (`amount:"10000"` ÷ 10^6) on 2026-05-20 [DOC, VERIFIED]. The claim is sound *as of
that probe*. Two caveats the spec under-weights: (a) the probe covered only ONE subgraph;
x402 pricing *could* vary by subgraph (research Open-Q2); (b) x402-on-Graph is 8 days old —
an 8-day-old endpoint's price is not a stable parameter, it is a snapshot. The spec pins
`Q_high` and the entire cost multiplier off it. Since `c = $0.01` enters as a *constant
multiplier* and §4.1 shows variance-of-log-returns is scale-invariant to it, a price
*change* does not bias the FX-variance share — but it *does* move `Q_high` (the band
edge). Acceptable to use as a parameter; the spec should add "price verified 2026-05-20;
re-verify at E10.0" rather than treating it as permanently fixed.

### OBS-2 — Panoptic ideal-scenario claim is honestly stated. CORRECTIONS-E10-2 is a visible record.

§13.3 is exemplary: it states plainly that the M-sketch "cannot be deployed in 2026,"
enumerates the three hard gaps (no Celo/Base Panoptic; no FX-stablecoin Uniswap pool;
Mento vAMM not a Uniswap v3 pool), and confines deployment to Stage-3. This matches
`integration_blockers` §3 and the CLAUDE.md Panoptic-liquidity caveat. No quiet
deployability assumption. CORRECTIONS-E10-2 (§0.2) is a genuine visible pivot record —
it preserves v0.1's retired pre-pin, names what changes and what is preserved, and the
directional→convex + Colombia→multi-currency pivot is user-approved ex ante. Nothing is
silently dropped. The HALT chain (§7 field 7: share<0.30, Q-dominance, spec-vs-data) is
collectively exhaustive against the §4 decisive object and the Q-dominance NON-RETIREMENT
verdict is an honest acceptable outcome, not engineered away. These are the spec's
strongest sections.

---

## §11 open-items disposition

| # | §11 item | RC disposition |
|---|---|---|
| 1 | $390 vs $399 | **Genuine — resolve now.** STRONG-1: re-pin primary to $399. Not deferrable; it sits in a frozen pre-pin field. |
| 2 | `Q_low` operationalization | **Genuine BLOCKER-adjacent.** Feeds BLOCK-3 — an unpinned behavioral parameter inside a simulation-driven verdict is a fantasy-dimension-3 risk. Must be pinned before E10.1, with a declared rationale, or the band lower bound is under-identified as §11 itself admits. |
| 3 | Decomposition exactness | **Acceptable deferred** — see WEAK-2; sequencing in §10 handles it; add the "report only exact-decomposition share" guard. |
| 4 | 0.30 threshold | **Acceptable deferred-with-caveat** — see WEAK-1; needs one sentence of derivation/convention, then it can lock. |
| 5 | Representative-analyst calibration | **Genuine — feeds BLOCK-3.** A single representative Q per currency cannot honestly support a "cohort risk" claim. Either model a type-distribution or restrict every verdict to "the declared representative profile." |
| 6 | R6 reuse fraction | **Genuine — see STRONG-2.** The build-fresh list is essentially complete; the problem is the *reuse* fraction overstates a design document as an asset. |

Net: items 1, 2, 5 are not "deferred" — they are live defects feeding BLOCK/STRONG
findings. Items 3, 4 are genuinely deferrable. Item 6 is a framing fix.

---

## Anti-fishing assessment

- **Pre-pin genuinely locked before data:** mostly yes — §7 declares seven fields and
  bans post-hoc moves. BUT field 6 (`~360 cells`) contains an unverified count
  (BLOCK-1), and `Q_low`/`Q_high` band edges and the representative-analyst profile are
  *not* pinned (they are "parameters of the §6 simulation"). A pre-pin that defers its
  own load-bearing simulation parameters to the simulation is partially circular — those
  parameters can be chosen during E10.1 to influence the Q-variance vs FX-variance split,
  which is *exactly* the §4.3 decisive object. This is a real fishing surface: a modeler
  tuning `Q_low`/`Q_high`/workflow-mix changes the simulated Q-variance and hence the
  FX-variance share. The spec must pin these (or pin a rule + sensitivity grid for them)
  *before* E10.1, not "in the §6 simulation."
- **HALT chain collectively exhaustive:** yes — share<0.30, Q-dominance, spec-vs-data
  contradiction cover the failure surface against the §4 object, and Q-dominance as a
  valid NON-RETIREMENT verdict is honest.
- **CORRECTIONS-E10-2 visible record:** yes — OBS-2; nothing quietly dropped.
- **No prior-β import:** confirmed — §8 explicitly bans importing Pair D's +0.137; the
  primary object is a share not a magnitude, so there is no magnitude target to fish toward.

The §4 FX-variance-share framing is the spec's real anti-fishing achievement: it
correctly identifies that naive β>0 is mechanically true and demotes it to a
necessary-not-sufficient gate. That reasoning is sound. The fishing surface that remains
is **not** in the estimator — it is in the *unpinned simulation inputs* that determine
the Q-variance component.

---

## Summary

| Finding | Severity | One-line |
|---|---|---|
| BLOCK-1 | BLOCK | ~30-month / ~360-cell panel not verified; panel-month axis ambiguous; several Mento currencies <12 months old |
| BLOCK-2 | BLOCK | `m`-suffix panel tokens not live (only USDm); live set is legacy `c`-tokens; rebrand absent from §11 |
| BLOCK-3 | BLOCK | Cohort is an unobserved phenomenon; §9 verdicts assert "cohort" properties a simulation cannot deliver |
| STRONG-1 | STRONG | `Q_high` pinned off wrong $390; verified Dune Plus is $399 — re-pin primary |
| STRONG-2 | STRONG | R6 "reuse" is a never-coded design doc; ~25-30% overstates the asset |
| WEAK-1 | WEAK | 0.30 threshold is an honest arbitrary floor; needs one sentence of justification |
| WEAK-2 | WEAK | Leading-order variance decomposition may bias the share; report only exact form |
| WEAK-3 | WEAK | "Clears N_MIN" misleads — identification rests on ~12 clusters, not 360 cells |
| OBS-1 | OBSERVATION | x402 $0.01 sound but 8-day-old snapshot; re-verify at E10.0 |
| OBS-2 | OBSERVATION | Panoptic ideal-scenario and CORRECTIONS-E10-2 honestly stated — spec's strongest part |

**3 BLOCK, 2 STRONG, 3 WEAK, 2 OBSERVATION. Verdict: NEEDS WORK.**

The convex reframe is good economics and the anti-fishing architecture around the
FX-variance share is genuinely sound. But the spec ships a panel whose size, currency
symbols, and 30-month window are stated as facts and are not — and the simulation-driven
posture has not fully cleared the fantasy threshold because the cohort it represents is
not a documented phenomenon and the verdict ladder asserts properties of that cohort.
Fix BLOCK-1/2/3 and STRONG-1/2; the spec is then a credible PARTIAL-track candidate.
