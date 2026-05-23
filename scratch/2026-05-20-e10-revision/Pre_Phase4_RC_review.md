# E10 GSPS — Pre-Phase-4 Reality-Checker Review

**Reviewer:** Reality Checker (RC half of mandatory 2-way pre-Phase-4 gate)
**Scope:** Reality, posture, provenance (Model QA reviews modeling/econometric design separately)
**Spec basis:** v0.7 (`docs/specs/2026-05-20-e10-gsps-v0.7-convex-multicurrency-design.md`)
**Plan §7 item 2 (RC half):** seven verification items below
**Date:** 2026-05-23
**Last main-line commit reviewed:** `abfaf28` (feat(E10): GSPS Phase 2-3 — NHPP simulator, panel decomposition, spec v0.7)

---

## Verdict — top line

**CONDITIONAL.** Phase 4 (E10.3) may fire after two **minor-fix, non-blocking** spec-citation refreshes to two diagnostics artifacts. Every load-bearing item (provenance, identity verification, ex-ante threshold, §7 pre-pin freeze, descriptive-posture firewall, NON-FANTASY Q anchor, I-1 honest deferral) is **PASS**. The two FLAGs are cosmetic citation-staleness that v0.7 explicitly carries forward unchanged from v0.6 — they do not contaminate the pre-pin or the data, and they do not require a CORRECTIONS cycle. The Model QA half is run in parallel; final gate verdict is the conjunction.

---

## Per-item verdicts

### 1. Panel data provenance — **PASS**

`data/panels/e10_gsps_panel.parquet` (16,068 B, 2026-05-20) derives deterministically from `scripts/build_e10_gsps_panel.py` (`scripts/build_e10_gsps_panel.py:1-`) + 5 frozen Tier-2 raw central-bank snapshots under `data/raw/e10_gsps/fx/` (COP/BRL/EUR/GBP/NGN `.raw` + `.provenance.json` sidecars). `simulations/e10_gsps/DATA_PROVENANCE.md:25-31` lists all 5 sha256 prefixes and bytes. `notebooks/e10_gsps/diagnostics/E10.0_panel_window.json:6-19` pins **150 cells × 5 currencies × 30 months (2023-11-01 → 2026-04-30)** per CORRECTIONS-E10-5. Confirmed identically in Phase-3 completion memo §2 (`scratch/2026-05-20-e10-revision/e10_phase3_completion.md:45-52`). Tier-3 round-trip `--verify-against-tier1` **PASS** for all 150 cells (completion memo §5, line 101).

### 2. §4.2 identity verified empirically — **PASS**

Implementation: `simulations/e10_gsps/modules/decomposition.py` (11,806 B, `decompose_cell` / `ThreeWayDecompositionModule`) with raise-on-mismatch `DecompositionIdentityError`. Test harness: `simulations/e10_gsps/tests/unit/test_panel_construction.py` + `test_decomposition.py` (4/4 task-0.6 GREEN incl. exact-identity property and mismatched-grid rejection — completion memo §6, line 110). Empirical headline: **max |identity_residual| = 1.3e-15 across all 150 cells** (completion memo §4, line 88-96 + diagnostics artifact `notebooks/e10_gsps/diagnostics/E10.2_decomposition_summary.json`). Floating-point zero; identity holds exactly per cell as required by spec v0.7 §4.2.

### 3. Phase-2.5 break-even frozen — **PASS**

`notebooks/e10_gsps/diagnostics/E10.2.5_break_even_threshold.md` exists (22,039 B). `s_be = 0.25` is unambiguous and frozen at multiple positions: line 1 title ("FROZEN"), line 289 (derivation conclusion `s_be = 0.25 / 1 = 0.25`), line 293, line 335 (boxed **FROZEN BREAK-EVEN FX-VARIANCE SHARE: s_be = 0.25**). Firewall statement at line 344-352 affirms zero Phase-3 §4 decomposition content was consumed. **26 CHECK_ALLOWLIST markers present** (`grep -c` = 26; brief required ≥25 — satisfied with margin; they live on the §13 M-sketch payoff-geometry quote lines, legitimate per spec §13). Pin is ex-ante and verifiably before any §4 surface evaluation.

### 4. Seven §7 pre-pin fields not drifted — **PASS**

Read `docs/specs/2026-05-20-e10-gsps-v0.7-convex-multicurrency-design.md:269-283`. All seven rows (Sign, Primary object, Material threshold = `s_be = 0.25`, Lag, Posture, Panel & FE = 5 currencies × ~30 months ≈ 150 cells with G ≈ 5, HALT condition) are explicitly marked **UNCHANGED** with rationale. v0.7 §7 preamble (line 273) and §8 anti-fishing carry-forward (line 297) both state CORRECTIONS-E10-7 is a *construction-grid pin* on already-specified objects (§3.2 X, §5.2 Y, §4.2 decomposition) and **does not re-pin any §7 field value**. Banned-moves list (line 287) explicitly forbids post-hoc threshold adjustment / panel-window extension / currency expansion / sensitivity-arm rescue / β magnitude import. **No drift.**

### 5. Descriptive-posture firewall has not leaked — **PASS**

Ran `python scripts/e10_firewall_check.py` against current working tree → **"E10 firewall PASS — 54 files scanned clean."** (CI hook in `.git/hooks/pre-commit` is wired and was the gate at commit `abfaf28`; the 19→54 file count grew with non-E10 artifacts in the scan envelope, the pass is unchanged.) Spot-check of `simulations/e10_gsps/modules/decomposition.py` and `simulations/e10_gsps/modules/panel_construction.py`: zero hits on `significance|p-value|p_value|reject H0|reject_null|null hypothesis`. The only `inferential` occurrences are in `anti_fishing_checks.py:16,60,63` and `verdict_classifier.py:11,41-43`, which **prohibit** inferential claims — these are guardrails, not leakage (`emit_inferential_verdict` raises). Descriptive posture intact.

### 6. NON-FANTASY anchor still holds — **PASS**

`notebooks/e10_gsps/diagnostics/E10.1_calibration_note.md:8-10` cites `scratch/2026-05-20-e10-revision/e10_q_anchor_extraction.md` (the trace-mining method) plus `e10_q_anchor_calls.csv` (**214 rows**) and `e10_q_anchor_daily.csv`. Extraction memo `scratch/2026-05-20-e10-revision/e10_q_anchor_extraction.md:1-32` documents trace-mining method (genuine Claude Code JSONL transcripts mined from user's own three abrigo-analytics on-disk path histories + 6-project bracket sample; tool-call classification rule lines 26-31). Headline: "Trace is GENUINE and NON-TRIVIAL" (line 17); daily-count **VMR = 20.6 (centre) / 19.8 (bracket)** (line 22-23). The 214 calls match the brief's claim. Cox / doubly-stochastic mechanism is trace-anchored and §6.2 NON-FANTASY profile holds.

### 7. I-1 remediation logged honestly — **PASS**

`scratch/2026-05-20-e10-revision/I-1_remediation_backlog.md` (2,472 B, 2026-05-23) is honest deferred-remediation, not fishing erasure. Specifically:
- Names the spec-vs-code drift hazard explicitly (lines 22-25: "A unilateral code change to threshold = 3 would silently drift the runtime from the spec, violating the anti-fishing/spec-vs-code-coherence invariant").
- Routes remediation through the proper CORRECTIONS-E10-8 path (lines 32-40: spec edit + 2-way review + code patch + re-review).
- Acknowledges no production cell currently hits the latent (all 150 cells have ≥ 4 surviving days, far above the threshold).
- Travels with five other minor findings (lines 42-50) — bundled honestly, not buried.

No fantasy-style "we already fixed it" language; no silent code patch; transparent about why deferral is correct discipline rather than convenience.

---

## Flags (minor, non-blocking)

**FLAG-RC-1 (cosmetic):** `simulations/e10_gsps/DATA_PROVENANCE.md:4` cites "Spec basis: v0.6" — should refresh to v0.7. v0.7 §0 explicitly carries v0.6 content forward unchanged for everything DATA_PROVENANCE.md references, so the *content* is current; only the version-number citation is stale. Same issue at `notebooks/e10_gsps/diagnostics/E10.0_panel_window.json:4` (citation refresh already done per the RC O-1 note in that field), and at `notebooks/e10_gsps/diagnostics/E10.1_calibration_note.md:6` ("Spec basis: v0.6") and `E10.2.5_break_even_threshold.md:5` ("Spec basis: v0.6"). **Fix:** mechanical refresh of the spec-basis citation lines to v0.7 with a one-line note that content is carried forward unchanged (already true). Does not require a CORRECTIONS cycle (no content change). **Non-blocking for Phase 4.**

**FLAG-RC-2 (informational):** Phase-3 completion memo `scratch/2026-05-20-e10-revision/e10_phase3_completion.md:6` cites spec v0.6 — but v0.7 is the current standing version with CORRECTIONS-E10-7 (the gapped-grid construction the Phase-3 work *triggered*). Same cosmetic refresh recommended. **Non-blocking.**

Neither FLAG touches a §7 pre-pin, a data input, a fitted threshold, or a posture statement. They are purely citation hygiene.

---

## Auxiliary observation (information only)

Phase-3 headline (FX-variance share ≈ 0.014%–0.02% panel mean, Q-variance dominates by 3-4 orders of magnitude — completion memo §3, lines 64-84) is exactly the spec-anticipated trajectory toward **§9 NON-RETIREMENT** ("Q-variance component dominates the decomposition across the whole anchored Q-volume range"). Phase 4's job is to characterize the surface across the §6.2 Q range and read it against `s_be = 0.25`; the verdict is *not pre-decided* by the panel mean, because §9 NON-RETIREMENT is conditional on the dominance holding "across the **whole** anchored range," not on the mean. Phase 4 must compute the surface honestly and report whichever §9 rung applies. Reality Checker: no posture-pressure flag at this gate; the descriptive ladder is verdict-permissive of this trajectory.

---

## Required action before Phase 4 fires

None blocking. Optional citation refresh (FLAG-RC-1, FLAG-RC-2) may be done in-flight during Phase 4 or rolled into a closure pass — neither gates dispatch.

**RC verdict — CONDITIONAL → effectively PASS contingent on Model QA half.** Phase 4 (E10.3 — surface characterization) is cleared from the Reality-Checker side.

---

*Pre-Phase-4 RC review — closes 2026-05-23.*
