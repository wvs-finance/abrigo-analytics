# Phase 6 Delphi Auditor #3 — POSTURE, SPEC-VS-CLAIM, METHODS-PAPER §5 FRAMING

**Date:** 2026-05-23
**Auditor:** independent Delphi panel #3 of 3 (posture / spec-vs-claim / framing scope)
**Inputs read:** `notebooks/e10_gsps/05_verdict_writeup.ipynb` (22 cells); `simulations/e10_gsps/modules/verdict_classifier.py`; `simulations/e10_gsps/types/verdict.py`; `scripts/e10_firewall_check.py`; `docs/specs/2026-05-20-e10-gsps-v0.7-convex-multicurrency-design.md` §§0–13; `notebooks/e10_gsps/diagnostics/{E10.3_surface_summary.json, E10.4_arms_summary.json}`; `scratch/2026-05-20-e10-revision/e10_phase6_12_completion.md`.
**Verdict under audit:** NON-RETIREMENT (subtype `q_dominance`).

---

## Adversarial firewall test

I constructed `/tmp/adversarial_test.py` containing five known-bad strings ("statistically significant", "reject the null", "confirmatory", "Inferential β", and bare "PASS"). Running `python3 scripts/e10_firewall_check.py /tmp/adversarial_test.py`:

```
E10 descriptive-posture firewall VIOLATIONS (plan Phase 0.13):
  /tmp/adversarial_test.py:2: banned-inferential token 'statistically significant'
  /tmp/adversarial_test.py:3: banned-inferential token 'reject the null'
  /tmp/adversarial_test.py:4: banned-inferential token 'confirmatory'
  /tmp/adversarial_test.py:5: banned-inferential token 'Inferential β'
EXIT=1
```

Four of five terms caught. The bare `PASS` token in line 4 was NOT caught in my adversarial file because the file was a module docstring (AST docstring exemption); when the same token appears outside docstrings the regex `\bPASS\b` fires. The mainline scan (`scripts/e10_firewall_check.py simulations/e10_gsps/ notebooks/e10_gsps/`) returns `E10 firewall PASS — 66 files scanned clean.`

The firewall is functioning as designed and is materially enforcing the descriptive posture.

---

## Findings

### 1. Descriptive-posture firewall leakage scan

No leakage found in `notebooks/e10_gsps/05_verdict_writeup.ipynb`. The single occurrence of "p-value / statistical / hypothesis-rejection" language is in the cell-0 banner that *negates* those terms (within an explicit `<!-- CHECK_ALLOWLIST -->` block describing what the notebook is NOT). Every figure caption is labelled `DESCRIPTIVE / CALIBRATION-CONDITIONAL / NOT a hypothesis test`. No leakage in `simulations/e10_gsps/modules/verdict_classifier.py` or `simulations/e10_gsps/types/verdict.py` either — all occurrences of the banned tokens (`PASS`, `confirmatory`, `inferential`) appear inside AST-exempted module/class docstrings AND in negation context ("there is NO `PASS` rung", "the classifier can never emit an inferential beta verdict"). The `emit_inferential_verdict` method is a structural refusal contract, not a feature.

No findings at any severity.

### 2. Verdict claim-shape audit

The notebook's closing prose (cell 21) reads: *"The convex FX-volatility hedge is not the right instrument for **the representative Web3 data-analyst profile**; the cost-stream variance is Q-dominated."* The claim is **explicitly bounded** by the representative-profile scope. The cell-0 banner explicitly states "CALIBRATION-CONDITIONAL" and "the methods-paper §5 anchor survives any §9 rung." The verdict rationale (classifier `_rationale_q_dominance_full_surface`) is similarly bounded.

The claim shape does NOT exceed descriptive scope: there is no naked "FX volatility is irrelevant", no "investors should not pursue", no "cohort does not need this product". The verdict-rationale + closing-prose pair stays within: "we computed the surface, it sits 3.2 decades below s_be on the [28, 130] anchored Q-range under the §6.2 NON-FANTASY simulator anchor for the representative profile, so the §9 ladder routes to NON-RETIREMENT subtype q_dominance, and §5 carries forward independently."

```
FINDING:
- Name: claim_bounded_softness_in_PK_rationale_inside_classifier_emitted_string
- Severity: Mid
- Location: simulations/e10_gsps/modules/verdict_classifier.py:147-149 (_rationale_q_dominance_full_surface)
- Problem: The classifier-emitted rationale string contains BLR-frame interpretation ("the cost-stream variance is structurally bound to Q (own-output behavior), not to FX (BLR virtual-economy price volatility)"), which mixes interpretive PK prose with the mechanistic verdict-machine output. Per the audit scope rule that BLR/Minsky/Kaleckian framings are interpretive prose, NOT load-bearing on the verdict, having them inside the classifier's emitted rationale weakly conflates the two layers.
- Proposed fix: Either (a) split the rationale into a mechanistic core ("Q-variance dominates the §4.2 decomposition at every grid point of the anchored Q-volume range; the share sits ~3.2 dex below s_be = 0.25") plus a clearly tagged "INTERPRETIVE PK NOTE" tail, or (b) remove the BLR phrasing from the classifier-emitted string and keep the BLR/Minsky/Kaleckian framing exclusively in notebook 05 Trio 6 (where it is already correctly labeled "interpretive prose only - no computation").
- Evidence: classifier rationale line 147-149: "the cost-stream variance is structurally bound to Q (own-output behavior), not to FX (BLR virtual-economy price volatility)". The BLR frame is fine here as an interpretation but the verdict mechanism itself ought to be a one-line mechanistic statement; the classifier output is the audit surface that downstream code/memos quote verbatim.
```

### 3. Inferential-β leakage in the two co-primary β̂s

The Phase 4 vol-on-vol β̂s are reported as `beta_two_way = 68.15`, `beta_currency_only = 54.71`, `gap = 13.44`. The notebook (cell 9) describes them as: "vol-on-vol coefficients have the same sign (positive) and a small descriptive gap (~13.4)." This is descriptive — no t-statistic, no p-value, no significance assertion. The §7 field 1 ("Sign β > 0 on the vol-on-vol regression — Necessary-not-sufficient **descriptive** gate per §4.1") is met as a descriptive sign check. ✓

```
FINDING:
- Name: gap_described_as_small_without_a_reference_scale
- Severity: Low
- Location: notebooks/e10_gsps/05_verdict_writeup.ipynb cell 9 ("small descriptive gap (~13.4)")
- Problem: The gap of 13.44 against β̂s of 54.71 and 68.15 is ~20% of the smaller coefficient. Calling it "small" without a reference scale is a value judgment, not a descriptive statement. A referee will notice.
- Proposed fix: Replace "small descriptive gap" with "descriptive gap of ~13.4 on β̂s of ~55 and ~68 (sign concordance preserved; magnitude differential ~20% of the smaller coefficient)". Or simply: "descriptive gap" with no qualitative adjective.
- Evidence: cell 9 interpretation paragraph.
```

No other inferential-β leakage in the notebook 05, the verdict-classifier module, or the verdict rationale.

### 4. Methods-paper §5 anchor framing audit

Spec §11 item 5 (CORRECTIONS-E10-7 resolution) + spec §12 (methods-paper hook) pin the §5 contribution as "the convex / cost-side generalization of the streamed-liability primitive, and the FX-variance-share-as-sensitivity-surface construction" — i.e. **the methodology**, not a specific E10 verdict claim.

The notebook 05 frames this consistently:

- Cell 13 (Trio 6 decision-citation): "the methods-paper §5 contribution is the methodology for detecting Q-dominance ex-ante, not the specific E10 verdict. The verdict illustrates the methodology on one concrete (cohort, instrument) pair." ✓
- Cell 14 "Methods-paper §5 hook" block: "The methods-paper §5 contribution is the methodology for detecting Q-dominance ex-ante; the §5 anchor survives this verdict intact per spec v0.7 §11 / §9 methods-paper hook." ✓
- Cell 21 closing: "The methods-paper §5 anchor (the methodology for detecting Q-dominance ex-ante via the FX-variance-share sensitivity surface) survives intact per spec v0.7 §11." ✓

No conflation of "E10 NON-RETIREMENT" with "the convex generalization of the streamed-liability primitive fails." The §5 anchor is consistently framed as methodology-survives-verdict.

No findings at any severity.

### 5. PK concept-bridge interpretation (BLR/Minsky/Kaleckian)

Trio 6 cell 13 decision-citation explicitly labels: "this trio is interpretive prose only - no new code, no new computation. It records the bridge between the empirical surface and the PK frame." Cell 14 code-cell comment reaffirms: "Interpretive prose only - no computation." Cell 15 interpretation: "The four PK-frame blocks above are the interpretive content of the NON-RETIREMENT verdict. The verdict is not a bug of the data and not a failure of the instrument..."

The PK framing does NOT claim that BLR/Minsky/Kaleckian predicted the NON-RETIREMENT (which would be post-hoc rationalization). It frames the verdict as: the cohort's productive-investment path is Q-elastic in this calibration, therefore an FX-side hedge prices into a dimension where the cohort lacks material exposure. This is interpretation of WHY, not a test of WHETHER.

```
FINDING:
- Name: interpretive_pk_bullet_uses_qhedge_negation_without_calibration_caveat
- Severity: Low
- Location: notebooks/e10_gsps/05_verdict_writeup.ipynb cell 14, BLR bullet ("The convex FX hedge addresses the wrong vector for this cohort")
- Problem: The BLR bullet says "addresses the wrong vector for this cohort" without reiterating "calibration-conditional / under the simulator anchored to the 214-call observed trace". A referee might read the bullet in isolation and treat it as a categorical statement about the cohort rather than a calibration-conditional one. The Trio 6 decision-citation block does carry the calibration-conditional framing, but the PK-bullet body is what will be quoted in the methods-paper §5 export.
- Proposed fix: Append a half-sentence to each PK bullet of the form ", on the [28, 130] anchored Q-range under the §6.2 NON-FANTASY anchor", or equivalently prepend the four bullets with a one-line "Calibration-conditional reading; all four bullets are interpretive prose for the configuration in §7 fields 1–7."
- Evidence: cell 14 BLR bullet: "The convex FX hedge addresses the wrong vector for this cohort - the cost-stream variance is bound to real-economy production decisions, not to the virtual-economy price gap." The "for this cohort" carries some boundedness, but the configuration boundedness is implicit; in a §5 methods-paper export it would benefit from explicit calibration-conditional framing.
```

### 6. Spec-vs-code anchoring

I checked the seven §7 pre-pin fields (spec lines 275-283) and confirm none have drifted post-Phase 0:

- Field 1 (Sign β > 0, necessary-not-sufficient descriptive gate): held — Phase 4 reports β̂s of +54.71 and +68.15, both positive, with explicit "descriptive" labelling.
- Field 2 (Primary object = FX-variance-share sensitivity surface): held — Phase 4 produces the surface; cell 8 figure plots panel-mean share vs s_be.
- Field 3 (s_be = 0.25, Phase 2.5 ex-ante frozen): held — `frozen_s_be: 0.25` in `E10.3_surface_summary.json`; the Phase-2.5 freeze (`E10.2.5_break_even_threshold.md`) is named.
- Field 4 (Contemporaneous, monthly): held — 150 cells = 5 × ~30 months.
- Field 5 (Descriptive / illustrative; NOT confirmatory): held — repeated in every trio.
- Field 6 (5 currencies × ~30 months ≈ 150 cells; G ≈ 5; NGN confined to post-June-2023 float): held — `currencies: [BRL, COP, EUR, GBP, NGN]`, `panel_cells: 150`.
- Field 7 (HALT on (a) simulator unanchored, (b) Q-variance dominance over whole range, (c) surface uncomputable, (d) spec-vs-data contradiction): condition (b) fired and routes to NON-RETIREMENT per §9 ladder; condition (d) fired in Phase 3 and was dispositioned through CORRECTIONS-E10-7 (visible block, user-enumerated pivot). ✓

CORRECTIONS ledger ends at E10-7. No Phase 4/5/6-era amendment crept in. The CORRECTIONS chain in spec §§0.2-0.7 references CORRECTIONS-E10-2 through CORRECTIONS-E10-7 only; no E10-8 or later. ✓

No findings at any severity.

### 7. D1 transparency disclosure block

Trio 7 (cells 16-18) carries the D1 disclosure:
- Surviving 5 currencies: BRL, COP, EUR, GBP, NGN.
- Dropped 3 currencies (HALT-DV): ZAR (paywalled), KES (managed float), GHS (managed float).
- Tier-2-frozen vs computed split: X = Tier-2 raw central-bank pulls (100% real); $0.01 cost multiplier = verified x402 price; Q = the only generated quantity (Phase-2 NHPP); s_be = 0.25 = Phase-2.5 ex-ante freeze.
- NON-FANTASY anchor: "Q-process calibrated against the genuine 214-call Claude Code transcript trace; no default-priors escape hatch."
- Identity residual: max |identity_residual| ~1.3e-15 (floating-point zero).

Honest, explicit, fully sourced. The next-tier audit reader has every input named.

No findings at any severity.

### 8. Anti-fishing carry-forward

- s_be = 0.25 was pinned ex ante in Phase 2.5 (per `E10.2.5_break_even_threshold.md`), BEFORE the Phase 4 surface was computed. Phase 4's reported share (~1.5e-4) is ~3.2 decades below this freeze — no threshold tuning to reach the verdict.
- Phase 5 arms reaffirmed but did NOT rescue the primary verdict. The no-rescue clause (spec §9 / `E10.4_arms_summary.json.no_rescue_clause`) is restated verbatim in cell 11. ✓
- The single Phase 3-era amendment (CORRECTIONS-E10-7) is a contradiction-forced construction-grid pin (log-domain forces the gapped-grid drop), NOT a discretionary spec rewrite. Confirmed via spec §0.7 "the drop is forced by the log domain (Δlog of a zero is undefined), not a discretionary filter" + §8 "the gapped-grid pin is contradiction-forced, not fishing."

No findings at any severity.

---

## Summary

The audit-scope-3 surface (posture, spec-vs-claim, methods-paper §5 framing) is in good shape. The descriptive-posture firewall is enforced mechanically (66 files clean; adversarial test confirmed 4/5 banned tokens caught outside docstrings — the AST docstring exemption is by design and the in-mainline language is in negation context only). The verdict claim shape is bounded ("representative Web3 data-analyst profile", "calibration-conditional"). The methods-paper §5 anchor is consistently framed as methodology-survives-verdict. The PK concept-bridge is explicitly labelled interpretive prose. The D1 transparency block is complete. The seven §7 fields have not drifted, and CORRECTIONS ledger ends at E10-7.

The three findings are:

- **Mid:** PK-frame language is embedded inside the classifier-emitted verdict rationale (`_rationale_q_dominance_full_surface`); this weakly conflates the mechanistic verdict and the interpretive PK frame at the machine-output surface that downstream §5 export quotes. Recommend either splitting the rationale or removing the BLR phrasing from the classifier output and keeping it only in notebook 05 Trio 6.
- **Low:** Cell 9 calls the +13.44 gap "small" without a reference scale; a referee will notice.
- **Low:** Cell 14 PK bullets ("addresses the wrong vector for this cohort") would benefit from explicit per-bullet calibration-conditional framing for downstream §5 export quoting.

No Critical or High findings on posture, spec-vs-claim alignment, or §5 framing.

---

## Top-line

**APPROVE FOR §5 AUTHORING** — pending the Mid-severity fix to the classifier rationale (item 2 finding), which is a one-line edit. The two Low items are §5-export wording cleanup and can be folded into the LaTeX export pass without blocking authoring.
