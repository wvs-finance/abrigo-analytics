# RC Re-Review — E10 GSPS v0.5 (post-HALT closure re-review)

**Reviewer:** TestingRealityChecker (Reality-Checker)
**Date:** 2026-05-20
**Scope:** CORRECTIONS-E10-5 closure re-spec only — the 8→5 currency panel narrowing
following the E10.0 HALT-DV. Read-only; no spec/plan edits.
**Spec under review:** `docs/specs/2026-05-20-e10-gsps-v0.5-convex-multicurrency-design.md` (452L, v0.5 DRAFT)
**Cross-checked against:** v0.4 spec; `e10_phase1_completion.md`; `E10.0_HALT-DV.md`;
`docs/plans/2026-05-20-e10-gsps-v0.4-implementation-plan.md` (CORR-E10P-10).

---

## VERDICT: PASS

The re-spec is **HONEST**. The 6 untouched pre-pin fields are verified untouched.
G≈5 is verified named, not hidden. No new BLOCK finding. All four PASS preconditions met.

---

## Check 1 — Re-spec honesty: HONEST

The 3-currency drop is documented honestly with per-currency unavailability evidence.

- **Diff vs source memos.** v0.5 §0.5 / §1.2 per-currency evidence table matches the
  Phase 1 completion memo and `E10.0_HALT-DV.md` §4 verbatim: ZAR (SARB `SarbWebApi`
  snapshot-only; legacy `wwwrs.resbank.co.za` "no route to host" ×3); KES (CBK series
  ends 2024-01-04; current rates ~2,164 per-day PDFs); GHS (`bog.gov.gh` behind a
  Radware `validate.perfdrive.com` bot wall). No drift between spec and the evidence.
- **5 retained currencies cross-check the Phase 1 memo exactly** — COP 590, BRL 627,
  EUR 635, GBP 631, NGN 617 in-window daily rows; common window 2023-11-01→2026-04-30.
- **No fabrication.** §0.6 banned-moves block explicitly forbids flat-fill, interpolate,
  substitute, FRED/OANDA/aggregator stand-in, and panel-currency *expansion*. §1.2,
  §3.3, §8 each restate "not substituted, not flat-filled, not interpolated." The
  disposition memo §4 anti-fishing note confirms free options were exhausted (SARB
  probed ×3, CBK AJAX driven with cookie+nonce, BoG probed with browser UA) before each
  UNAVAILABLE verdict. The non-bypassable data gate fired honestly.
- **Honest about the prior over-assertion.** v0.5 §0.5 names plainly that the v0.4 §0
  DV record's "30-month free daily availability confirmed for all eight panel
  currencies" did NOT survive the E10.0 per-currency re-verification. The re-spec does
  not bury the v0.4 mistake — it surfaces it as the HALT-DV trigger.

## Check 2 — The 6 untouched pre-pin fields: VERIFIED UNTOUCHED

Field-by-field diff of §7 v0.5 against v0.4:

| Field | v0.4 value | v0.5 value | Verdict |
|---|---|---|---|
| 1 Sign | β>0 vol-on-vol, descriptive gate | identical | UNCHANGED |
| 2 Primary object | FX-variance-share surface + ex-ante break-even | identical | UNCHANGED |
| 3 Material threshold | fitted-hedge break-even, ex ante | identical | UNCHANGED |
| 4 Lag | contemporaneous, monthly | identical | UNCHANGED |
| 5 Posture | descriptive/illustrative, non-confirmatory | value identical (added clause only *explains* G≈5 doesn't demote — no value change) | UNCHANGED |
| 6 Panel & FE | 8 currencies × ~30 mo, two-way FE | **5 currencies × ~30 mo ≈ 150 cells, G≈5, two-way FE RETAINED** | FRESH PRE-PIN (panel dimension only) |
| 7 HALT condition | 4 binding triggers | identical | UNCHANGED |

Field 6 moves because the panel *dimension* changed (8→5), not because the *test* was
tuned. Two-way FE is retained — no silent switch to currency-FE-only. No sign flip, no
threshold relaxation, no lag change, no posture demotion, no HALT-condition weakening.
The fresh field-6 pre-pin is itself recorded in the visible CORRECTIONS-E10-5 block —
not a silent re-run at adjusted scope.

## Check 3 — G≈5 thinness named, not hidden: VERIFIED NAMED

G≈5 is named plainly in §0.5, §7 (field 6 + descriptive-bands paragraph), §8, and §9 —
in each case as "structurally even thinner than the G≈8 that already forced the
descriptive demotion" and "well below the G≈12 wild-cluster-bootstrap size-distortion
threshold." §7's descriptive-bands paragraph hardens the label quantitatively: permutation
support drops to 2^5=32 sign assignments; the EM-vs-DM exchangeability violation persists
(COP/BRL/NGN not exchangeable with EUR/GBP). A reader cannot mistake the 5-currency panel
for a strong one — the honesty bar is cleared.

## Check 4 — Posture unchanged: VERIFIED

E10 was already non-inferential since v0.4 (CORRECTIONS-E10-4 Fix 1). v0.5 correctly
states G≈5 does not demote it further — a 5-currency surface is still a valid
*description*. The §9 verdict ladder is structurally identical: SURFACE-PRODUCED /
PARTIAL / NON-RETIREMENT — no rung added, removed, or renamed. The §9 PARTIAL row still
references "a further panel currency drops" (correct — additional thinning is still a
PARTIAL trigger). No PASS rung resurrected.

## Check 5 — Plan consistency: VERIFIED

Plan CORR-E10P-10 matches the spec: §0 DV record = 5 currencies + 3 dropped HALT-DV;
Phase 1 (E10.0) marked DONE for the 5-currency panel; panel references updated to
5×~150 cells, G≈5 throughout (§§0, 1, 2, 6 updated; carried-forward "8/240/G≈8" text
explicitly governed by CORR-E10P-10). Plan §5 anti-fishing block restates the descriptive
posture is unchanged. Task 4.1 / 4.3 carry the G≈5 caveat at point of use. Consistent.

## Check 6 — The 4 §11 open items

- **New item 1 — G≈5 descriptive-band labelling.** FEASIBLE. Retaining the wild-cluster
  bootstrap + permutation arm as hardened-label descriptive bands at G≈5 is defensible;
  dropping them entirely is the safer alternative and is also feasible. The item is
  correctly surfaced for the user, not silently resolved. WEAK observation: at 2^5=32
  permutation assignments the arm is near-degenerate — leaning toward *drop from the
  deliverable* would reduce mis-read risk, but keeping with the hardened label is not a
  blocker.
- **New item 2 — two-way-FE viability at G≈5.** FEASIBLE but genuinely marginal. Two-way
  FE (currency + month) on G≈5 clusters leaves very thin identifying variation; v0.5
  honestly says so in field 6 and §11. Retaining two-way FE as the unchanged primary is
  acceptable for a descriptive iteration (the surface, not β, is the deliverable);
  promoting currency-FE-only to co-primary is a reasonable user call. Correctly left to
  the reviewer gate. Feasible either way — not a blocker.
- Carried items 3 (surface-grid resolution) and 4 (ex-ante exposure assumption) are
  unchanged from v0.4 and were not reopened. Correct.

## New findings

- **OBSERVATION (not BLOCK).** v0.5 §3.3 keeps the NGN robustness-pair item 3 sentence
  "E10.0 screens all 5 surviving currencies for ... regime breaks" — the screen already
  ran (Phase 1, all 5 done); the present-tense phrasing is a harmless carry-over from
  v0.4. Cosmetic; no action required for PASS.
- **OBSERVATION.** §9 PARTIAL row still lists "a further panel currency drops below the
  qualifying window at E10.0" — E10.0 is complete, so this can only fire at a future
  re-run. Harmless; the rung remains collectively-exhaustive-correct. No action.

No BLOCK, no STRONG finding. The re-spec is a clean panel-dimension narrowing.

---

## Summary

| PASS precondition | Status |
|---|---|
| Re-spec verified honest | MET |
| 6 fields verified untouched | MET |
| G≈5 verified named | MET |
| No new BLOCK | MET |

**VERDICT: PASS.** The CORRECTIONS-E10-5 re-spec is an honest, visibly-recorded
panel-dimension narrowing. The descriptive posture, the 6 untouched pre-pin fields, the
(Y,M,X) triple, and the methods-paper hook are all carried forward intact. The post-HALT
discipline (disposition memo → user-enumerated pivot → CORRECTIONS block → 2-way
re-review) was followed correctly. v0.5 may proceed to E10.1 on the 5-currency panel
after the user closes the two §11 new open items.
