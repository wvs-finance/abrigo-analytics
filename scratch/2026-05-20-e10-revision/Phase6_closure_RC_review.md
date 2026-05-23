# Phase 6.5 Closure RC Review — E10 GSPS

**Reviewer:** TestingRealityChecker (RC discipline — reality / posture / fantasy / provenance / anti-fishing)
**Date:** 2026-05-23
**Scope:** Final pre-PR honesty/posture/provenance check on the closed E10 GSPS iteration. Code-quality review is out of scope (parallel Code Reviewer owns it).

---

## Top-line: **APPROVED**

All 12 RC scope items pass. No fantasy detected, no posture leakage, no provenance fabrication, no anti-fishing footprint. The verdict claim shape is bounded to the cohort + calibration; the methodology-survives-verdict framing is consistently applied across memo, LaTeX, markdown draft, and notebook 05. Ready for PR open + merge.

Three INFO-level observations are filed below for future polish; none block.

---

## Item-by-item verification

### 1. Verdict memo honesty — PASS
- `memory/project_e10_gsps_verdict.md:13-24` states verdict unambiguously: **NON_RETIREMENT subtype `q_dominance`**, spec v0.7 §9 rung 5.
- Cohort scope is correctly bounded — "the representative Web3 data-analyst cohort" (line 24); **does not** generalize to "convex FX hedges fail in general". The closing crossiteration note (lines 97-99) explicitly frames this as a methodology-prior input, not a global no-go on the instrument family.
- Drop disclosure for ZAR/KES/GHS is explicit at `DATA_PROVENANCE.md:30` (HALT-DV at E10.0, not substituted), echoed in the LaTeX caption at line 421-424.
- Methods-paper §5 anchor preservation: clearly framed as methodology-not-verdict (`project_e10_gsps_verdict.md:51-58`).

### 2. LaTeX §5 export honesty — PASS
Spot-checked numerics against diagnostic JSONs:

| LaTeX claim | LaTeX line | Source JSON | Match |
|---|---|---|---|
| `s̄ = 1.535 × 10⁻⁴` | 577, 510 | `E10.3_surface_summary.json:18` (`0.0001535157617749653`) | YES |
| 3.21 decades below `s_be` | 511, 579 | `E10.5_verdict_summary.json:17` (`-3.211787036673344`) | YES |
| `β̂_two-way = +68.151` | 566 | `E10.3_surface_summary.json:27` (`68.15124620607666`) | YES |
| `β̂_currency-only = +54.715` | 568 | `E10.3_surface_summary.json:28` (`54.714823014552536`) | YES |
| gap `+13.436` | 570 | `E10.3_surface_summary.json:29` (`13.436423191524128`) | YES |
| identity residual `1.33×10⁻¹⁵` | 203 | `E10.2_decomposition_summary.json:14` (`1.3322676295501878e-15`) | YES |
| 214 calls / VMR≈20 | 134-136 | `E10.1_calibration_note.md:135` ("214 real, timestamped tool calls"); §3.1 VMR table | YES |
| Per-currency means (NGN 5.97e-4, COP 6.16e-5, BRL 5.92e-5, EUR 2.91e-5, GBP 2.10e-5) | Table 6.4 captions at 520-530; envelope at LaTeX 510 | `E10.2_decomposition_summary.json:24-54` | YES (all five) |
| 5 arms with concordance metrics in `[0, 9.43e-5]` | Table at LaTeX 549-557 | `E10.4_arms_summary.json:18-58` | YES (all five) |
| Six §9 flags | Table at LaTeX 487-492 | `E10.3_surface_summary.json:33-38` + `E10.5_verdict_summary.json:7-13` | YES |

- §5.9 "Methodology contribution survives the verdict" (LaTeX line 633-661) correctly frames per spec v0.7 §11.
- §5.10 Limitations (LaTeX line 664-721) honestly discloses: arm (b) algebraic-identity (line 671-678), panel-mean broadcast (line 679-685), G=5 non-statistical bands (line 687-691), arm (d) per-step calibration (line 693-702), `_MIN_SURVIVING_DAYS=2` degeneracy (line 704-709), ideal-scenario premium (line 711-715). Methods-paper §5 robustness disclosed (line 717-720).
- No inferential-β leakage in the LaTeX. The only matches against banned regex are explicit negations: "NOT a confidence interval", "NOT an inferential band", "it does not predict ... post-hoc" (LaTeX 513, 527-528, 588).

### 3. Markdown draft parity — PASS
- `docs/writeups/_drafts/e10_methods_paper_section_5.md:12, 122-123, 134, 140, 143, 146, 152-160` carry parallel numerics, identical posture banners, identical §9 ladder, identical figure captions. Reads as a faithful markdown counterpart of the LaTeX.

### 4. PDF render — PASS
- `docs/writeups/e10_gsps_methods_paper_section_5.pdf`: 12 pages, 381,948 bytes (verified via `pdfinfo`).
- `docs/writeups/figures/e10_figure1_surface_vs_break_even.pdf` (25,569 B) and `e10_figure2_currency_spread.pdf` (29,892 B) present.

### 5. Notebook chain reality — PASS
All five notebooks carry the descriptive-posture banner:
- `01_simulator_calibration.ipynb` line 1 (CHECK_ALLOWLIST-tagged).
- `02_panel_decomposition.ipynb` (CHECK_ALLOWLIST-tagged).
- `03_surface_characterization.ipynb` (CHECK_ALLOWLIST-tagged; explicit CORR-E10P-11 reference for non-statistical band labeling).
- `04_sensitivity_arms.ipynb` (CHECK_ALLOWLIST-tagged; no-rescue clause repeated in-banner).
- `05_verdict_writeup.ipynb` line 11 (CHECK_ALLOWLIST-tagged).

Notebook 05 Trio 6 PK/BLR interpretive labeling: `05_verdict_writeup.ipynb:478` carries the literal string "this trio is interpretive prose only - no new code, no new computation" — load-bearing label present.

### 6. Data provenance — PASS
`simulations/e10_gsps/DATA_PROVENANCE.md:25-31` records all 5 currencies with source URL, payload SHA-256 head (16 chars), byte count, and window:

| Currency | Source | SHA head | Bytes |
|---|---|---|---|
| COP | Banrep TRM datos.gov.co `32sa-8pi3` | `861be2848592affa` | 70,741 |
| BRL | BCB Olinda OData PTAX | `ba75a914696af794` | 58,379 |
| EUR | ECB Data Portal SDW `EXR/D.USD.EUR.SP00.A` | `9cd19cf85ac11200` | 132,350 |
| GBP | BoE IADB `XUDLUSS` | `378df39672a4cca0` | 12,573 |
| NGN | CBN Gateway `/api/GetAllExchangeRates` | `e61225c8f8fdd854` | 7,987,807 |

Window 2023-11-01 → 2026-04-30 for all 5. NGN confined to post-NFEM-float regime (line 34-36). The dropped trio (ZAR/KES/GHS) is honestly disposed at line 19-23 (HALT-DV, not substituted, no flat-fill). x402 price re-verified live (line 41-45).

### 7. NON-FANTASY anchor still genuine — PASS
- `E10.1_calibration_note.md:135` — "214 real, timestamped tool calls extracted from the literal Claude Code session record — no synthesis, no fabrication."
- `e10_q_anchor_calls.csv` row count = 215 (header + 214 calls) — matches.
- `e10_q_anchor_extraction.md` headline (lines 14-19) confirms genuine, non-trivial, multi-session multi-day structure.
- VMR ≈ 20 derived empirically (centre 20.6, bracket 19.8, sample-variance; population variance recompute 18.9/19.1 — same conclusion, calibration note §3.1, A4 addendum).
- Cox / doubly-stochastic NHPP locked against trace evidence (4-part decision-citation at calibration note §3.3).

### 8. Descriptive-posture firewall — PASS
- Live run: `python scripts/e10_firewall_check.py simulations/e10_gsps/ notebooks/e10_gsps/` → **"E10 firewall PASS — 66 files scanned clean."**
- Adversarial test (added `simulations/e10_gsps/_adv_test2.py` containing "statistically significant", "reject the null", "confirmatory verdict") → firewall caught all three banned tokens with correct file:line attribution. Test file removed; clean re-run confirmed.
- LaTeX is outside firewall scope but was manually grep-checked: only banned-term matches were explicit negations (NOT-a-confidence-interval style). Clean.

### 9. Anti-fishing carry-forward — PASS
- `s_be = 0.25` was pinned ex-ante. `notebooks/e10_gsps/diagnostics/E10.2.5_break_even_threshold.md:9` dated **2026-05-20**. `E10.2_decomposition_summary.json:4` (Phase 3) generated **2026-05-21T00:45:30 UTC** — strictly *after* the 2.5 pin. Firewall bright line (E10.2.5 §0.1) explicitly states no Phase-3 decomposition output was consumed in `s_be` derivation. Verified.
- CORRECTIONS ledger ends at **E10-7** (Phase-3 era). Spec v0.7 grep confirms tail at line 392 ("CORRECTIONS-E10-7; awaiting post-HALT spec-compliance re-review"). No Phase 4/5/6 era amendment. Anti-fishing carry-forward respected.
- 5 sensitivity arms did NOT rescue the verdict: `E10.4_arms_summary.json:60` carries the constructor-pinned no-rescue clause string; all five arms return `q_variance_dominance_flag: True`. Concordance metrics ∈ [0, 9.43e-5] are descriptive only and `concordance_verdict: concordant` — none flips Q-dominance.

### 10. D1 transparency disclosure — PASS
- Notebook 05 Trio 7 (`05_verdict_writeup.ipynb:585-695`) carries explicit "D1 transparency disclosure" block: what data is real (FX panels — 5 currencies w/ SHAs), what was dropped (ZAR/KES/GHS HALT-DV), what was Tier-2-frozen, what is simulated (Q only — 214-call anchor + Cox NHPP). Fantasy-firewall (Phase 0.12) explicitly referenced.

### 11. The 7 fixes landed truthfully — PASS
Per `Phase6_Delphi_autofix_verification.md` and `Phase6_Delphi_final_audit.md`:
- **Fix 1 (arm-d calibration scale):** per-step convention restored; standalone numerical verification target_var_fx=1.5e-4 vs measured 1.43e-4, rel-err 0.048 (within 0.1 tolerance). Panel-mean share moved from broken 9.11e-6 → corrected 1.88e-4 (ratio 22:1 — matches predicted 21× deflation removal). Verdict invariant.
- **Fix 2 (panel-mean broadcast):** `is_panel_mean_broadcast` flag added to `SurfaceGridResult`; 4 call-sites wired; honest disclosure landed in LaTeX §5.10 + notebook 03 + 05 banners.
- **BLR-strip from machine-emitted classifier rationale:** confirmed at `Phase6_Delphi_final_audit.md:86` ("Verdict rationale cites only spec mechanism (no BLR/Minsky/Kaleckian)"). PK prose preserved in notebook 05 Trio 6 only, labeled "interpretive prose only" (verified — see Item 5).

### 12. Methods-paper §5 framing alignment — PASS
- Spec v0.7 §11 mandate: §5 contribution is the methodology, not the E10 verdict.
- LaTeX §5.9 (line 633-661) — "The contribution of this section is the *methodology*, not the specific E10 verdict."
- Verdict memo `project_e10_gsps_verdict.md:51-58` — "The §5 contribution is the **methodology** for detecting Q-dominance ex-ante via the FX-variance-share sensitivity surface — NOT the specific E10 verdict."
- Notebook 05 closing trio (line 11 banner): "The methods-paper §5 anchor survives any §9 rung (spec v0.7 §11 / §9 methods-paper hook)."

All three artifacts converge on the same framing. No drift.

---

## INFO-level observations (non-blocking)

- **INFO-1 — adversarial firewall regex coverage.** The descriptive-posture regex matches `\bstatistically[\s_-]+significant\b` with a separator requirement. A camel-case or inner-word usage (e.g. `isStatisticallySignificant`, `var_is_statistically_significantflag`) without a separator on both sides might slip past. Current codebase is clean. Future hardening: tighten the boundary or add a substring fallback. Not blocking — the literal phrase + underscore + dash variants are caught.
- **INFO-2 — verdict memo references "v0.7 §9 verdict ladder, rung 5".** The LaTeX Algorithm 1 enumerates 7 rungs; rung 5 is `q_variance_dominates → q_dominance`. Consistent. Nothing to fix; flagging for cross-readers.
- **INFO-3 — Phase 6 Delphi final audit's three INFO items carry forward.** `Phase6_Delphi_final_audit.md` F-FINAL-1/2/3 are non-blocking and pre-disclosed; the unit-test gap on the spec-form sibling flag (F-FINAL-1) is the most actionable polish.

---

## Verdict

**APPROVED — ready for PR open + merge.**

Evidence chain holds end-to-end: raw central-bank bytes (SHA-pinned) → Tier-1 panel parquet → exact §4.2 identity at machine precision (1.33e-15) → calibration-anchored simulator (214-call NON-FANTASY trace, VMR≈20) → ex-ante-frozen `s_be = 0.25` (Phase-2.5 dated 2026-05-20, before Phase-3) → FX-variance-share surface (panel-mean 1.535e-4, 3.21 decades below `s_be`) → §9 ladder rung 5 → NON-RETIREMENT subtype `q_dominance` → 5 concordant sensitivity arms (no rescue) → LaTeX §5 (12 pages) + verdict memo + notebook 05 all carry the methodology-survives-verdict framing without claim inflation.

No fantasy. No posture leakage. No fabricated provenance. No anti-fishing. CORRECTIONS ledger closed at E10-7. Cohort-bounded claim shape preserved. Honest disclosure of the four known limitations (panel-mean broadcast, arm-b algebraic identity, G=5 non-statistical bands, arm-d per-step convention) in both LaTeX §5.10 and notebook closing trios.

Recommend merge.

---

*Phase 6.5 closure RC review — closes 2026-05-23.*
