# Wave-1 Reality Checker — v1.1 Reverify (post-CORRECTIONS-α)

**Reviewer:** Reality Checker (Wave-1, post-hoc 2-wave reverify per `feedback_pathological_halt_anti_fishing_checkpoint` step 5)
**Artifact under review:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.1 LOCKED-PENDING-REVERIFY
**Predecessor:** v1.0 REJECTED (3 RC-BLOCKs + 5 RC-FLAGs by this reviewer)
**Verdict:** **ACCEPT_WITH_FLAGS** — all 3 RC-BLOCKs + 5 RC-FLAGs RESOLVED; 2 NEW RC-FLAGs raised; no NEW RC-BLOCKs. **Sub-task dispatch: PROCEED** conditional on Wave-2 MQ reverify concurring.

Default-to-REJECT discipline applied; the patch clears the bar substantively, not theatrically. Findings below.

---

## Resolution status — v1.0 RC-BLOCKs

### RC-BLOCK-1 (dev-AI Stage-1 FAIL silently ignored) — **RESOLVED**

§0.1 (lines 38–96) addresses the FAIL directly with three independent grounds. Audit per ground:

1. **Population mismatch** (lines 48–59): Section J = aggregate employment-share among 14–28 cohort across narrow ICT; Stage-2 cohort = post-revenue solo builders with USD costs vs COP MRR. The objects ARE structurally different — Section J is a labor-allocation transmission, the SaaS-builder $a_s$ is a per-user balance-sheet exposure. Backed by CORRECTIONS-ι "$a_s$ is per-user instrument-level, not aggregate population-level" (cited line 56). **Substantive, not sophistry.**

2. **Section M counter-evidence** (lines 61–69): cites β=+0.455, p=1.13e-6 from R2 sensitivity arm on Section M (professional/scientific/technical/admin services CIIU 69-75). SaaS builders sit in occupational classes closer to Section M than Section J narrow ICT. This is verifiable against `memory/project_dev_ai_section_j_fail.md` and is load-bearing. **Substantive.**

3. **CLAUDE.md ideal-scenario clause** (lines 71–80): correctly invokes the verbatim CLAUDE.md text "empirical β-estimate work is independent of actual on-chain deployment; the M-design step proposes the ideal settlement architecture; only the deployment step requires real LP capital." Stage-2 work is M-design. The invocation is textually faithful and authorized. **Substantive.**

**HALT trigger genuinely binding** (lines 91–96): "If TODO-COHORT-2 fitting on the synthetic cohort distribution returns $\Delta^{(a_s)} \ge 0$ at any pinned bracket point, this reconciliation is invalidated and the spec must be parked." This is a real exit criterion tied to §8(1) sign pre-pin. Not theatrical.

### RC-BLOCK-2 (N_MIN/POWER/MDES mis-import) — **RESOLVED**

§8 (lines 429–486) explicitly declares: "The $N_{\text{MIN}}=75$, ... thresholds in CLAUDE.md were framed for **Stage-1 empirical β regression** on real cohort data. They bind the **Stage-3 cohort survey** ... when it runs. They do *not* bind Stage-2 synthetic-Bayesian calibration." Declaration is unhedged.

10 substitute Stage-2-applicable invariants land at lines 441–480: sign pre-pin (1), convexity expectation (2), bracket immutability (3), tier-cap immutability (4), candidate-set closure (5), Pareto-α floor 1.5 (6), posterior CI-width threshold (7), sim-count floor 4000 draws / 4 chains / R̂≤1.01 (8), prior-sensitivity sweep ≥3 parameterizations (9), HALT cascade (10).

Each is genuinely applicable to a synthetic-Bayesian regime and several (Pareto-α floor, candidate-set closure) are *new* binding constraints. §14.3 line 640 explicitly notes "NO threshold was relaxed" — verified by inspection.

### RC-BLOCK-3 (bank-spread overlay vs §3) — **RESOLVED**

§3 line 126: "**No bank-spread overlay in the primary path** (resolves RC-BLOCK-3)." Lines 130–132: explicitly demoted to sensitivity arm. §5.4(c) lines 372–374: "Bank-spread $s_t \in [1\%, 3\%]$ overlay is a **§3 sensitivity arm only** — *not* in the primary FX path. No silent primary-spec mutation." §6 line 389 confirms in functional-form table: "(X/Y)_t | (6) deterministic perturbation | §3 | GBM, OU, jump, empirical, bank-spread $s_t$" (bank-spread listed in sensitivity column only). **Triple-consistent across §3 / §5.4 / §6. No residue.**

---

## Resolution status — v1.0 RC-FLAGs

- **RC-FLAG-1 ($Z$ undefined)** — **RESOLVED.** §4.1 (lines 144–157) gives the operational definition with the cohort-note formula. §10 line 512 schemas `estimates/Z_cap_pinned.json`. §9 TODO-COHORT-4 done-when (line 495) requires $Z$ pinning. Three-point lock (definition + schema + gate).

- **RC-FLAG-2 ($2k truncation vs >$2k p99)** — **RESOLVED.** §5.4(a) line 367–368: "modal coverage ~$2k/mo, **heavy tail with p99 > $2k preserved per §5.2.** No upper-bound truncation." Reworded as recommended.

- **RC-FLAG-3 ($\kappa$ stale post-2026-05-06)** — **RESOLVED.** §5.2 lines 301–303 footnote post-doubling event. Lines 308–309: "Post-doubling $\kappa$ sensitivity arm: repeat all (T2) fits at $2 \cdot \kappa$ per tier; report stability across." Lines 310–312 add explicit $\kappa \in [\kappa_0 \cdot 0.5, \kappa_0 \cdot 2.0]$ uncertainty bracket. Stronger than my v1.0 recommendation.

- **RC-FLAG-4 (effective-rate ambiguous)** — **RESOLVED.** §5.1 lines 246–256 give the explicit blended-$p_t$ formula with $w_{\text{in}}=0.539$, $h_{\text{cache}}=0.95$, computing $p_t^{\text{Sonnet}} \approx \$7.15$/MTok. Lines 254–256: "replaces the prior $0.30 figure which was cached-portion only; resolves RC-FLAG-4."

- **RC-FLAG-5 (citation overstates costs-doc)** — **RESOLVED.** §5.2 line 338: "Heavy / multi-agent (single anecdote) | $50/day | b2l-ouyang (single named anecdote, not screenshotted)" — split per recommendation. Line 337 keeps costs-doc at p90 $30/day separately.

---

## v1.0 PASS items — preservation check

- **Cohort fencing §1↔§5.1**: §1 (lines 100–109) unchanged; §5.1 (lines 168–172) class scope still terminal-based agentic AI coding. PRESERVED.
- **Bracket immutability §8**: now §8(3), preserved verbatim with strengthened candidate-set closure §8(5). PRESERVED + strengthened.
- **Output-artifact schema §10**: §10 lines 502–514 retains all v1.0 rows; adds `tier_id` to synthetic_tau_t and `Z_cap_pinned.json`. EXPANDED, not broken.
- **Reference integrity (CORRECTIONS-η/-ι, Path A)**: §7 still references Path A v0 §10.4 reconciliation tolerance (line 411); §0.1 cites CORRECTIONS-ι (line 56); §8(2) cites CORRECTIONS-η RC-BLOCK-2 precedent (line 449). PRESERVED.

---

## NEW elements introduced in v1.1 — substantive check

- **§0.1 reconciliation**: substantive (see RC-BLOCK-1 above).
- **§4.1 $Z$ operational definition**: substantive — cohort-note formula correctly transcribed; emission gate concrete.
- **§6 $q_t^{\text{commit}}$ row** (line 392): substantive — gives explicit additive ratchet $q_{t-1}^{\text{commit}} + \bar c_{\text{ann}} \cdot \mathbf{1}[t = t_{\text{renew}}]$ and a degenerate-case carve-out.
- **§6 (T1)/(T2) local-numbering note** (lines 394–397): substantive — explicit "T-numbering is local to this spec" prevents downstream confusion.
- **§8 ten Stage-2 invariants**: substantive (see RC-BLOCK-2 above).
- **§14 CORRECTIONS-α delta record + preserved-guarantees**: substantive. Carry-forward / defer matrix (§14.1, lines 583–616) records every BLOCK/FLAG fix with v1.1 location pointer. §14.2 preserved-guarantees (lines 618–635) is honestly accounted for — claims (1)–(7) are verifiable. §14.3 anti-fishing posture (line 640): "NO threshold was relaxed" — verified above.

---

## NEW RC-BLOCKs — none

No load-bearing reality / scope / source issues introduced.

## NEW RC-FLAGs

### RC-FLAG-NEW-1 — Section M β=+0.455 sourcing in §0.1 ground 2 needs a primary-source pin
**Severity:** Low. **Where:** §0.1 lines 61–69. The Section M counter-evidence is load-bearing for the reconciliation but is cited only via `memory/project_dev_ai_section_j_fail.md`. The memory file is a derived artifact. Fix: add the upstream notebook / R-output cell reference (e.g., `notebooks/dev_ai_cost/<notebook>.ipynb` cell or scratch disposition) so the +0.455 figure has a primary trace, not a memory-file trace.

### RC-FLAG-NEW-2 — §5.1 blended $p_t$ derivation has an arithmetic mismatch with the v1.1 footnote
**Severity:** Low. **Where:** §5.1 lines 246–256. The formula expands to $p_t^{\text{Sonnet}} = 0.539 \cdot 3 \cdot (1 - 0.95 + 0.95 \cdot 0.10) + 0.461 \cdot 15 = 0.539 \cdot 3 \cdot 0.145 + 0.461 \cdot 15 = 0.234 + 6.915 = 7.15$/MTok. The line 254 expansion writes `0.539 · 3 · 0.145` (correct on input side: $\approx 0.234$) and `0.461 · 15` ($= 6.915$), summing to 7.15 — checks. **However**, my v1.0 RC-FLAG-4 estimate ($\approx \$0.43$/MTok blended) used input-only weighting; the v1.1 number ($7.15) blends across input AND output via $w_{\text{in}}, w_{\text{out}}$, which is a *different* statistical object than my v1.0 estimate — the spec uses $w$ as the input-vs-output **token mix**, multiplied through the per-MTok rate. Arithmetically consistent with the formula as written, but the dimensional reading deserves an explicit one-line: "$p_t$ = expected per-MTok dollar cost per token consumed, weighted by the input/output token mix from arxiv 2601.14470." Without that, a sub-task author could mis-apply $p_t$ as a per-input-MTok rate. Fix: add one clarifying line in §5.1.

---

## Patch fidelity table

| v1.0 finding | v1.1 §location | Status | Evidence quote / line |
|---|---|---|---|
| RC-BLOCK-1 | §0.1 lines 38–96 | RESOLVED | three-ground reconciliation + binding HALT |
| RC-BLOCK-2 | §8 lines 429–486 | RESOLVED | Stage-3-only declaration + 10 substitute invariants |
| RC-BLOCK-3 | §3 line 126 + §5.4(c) lines 372–374 + §6 line 389 | RESOLVED | "No bank-spread overlay in the primary path" |
| RC-FLAG-1 | §4.1 + §10 + §9 | RESOLVED | three-point lock |
| RC-FLAG-2 | §5.4(a) lines 367–368 | RESOLVED | "heavy tail with p99 > $2k preserved" |
| RC-FLAG-3 | §5.2 lines 301–312 | RESOLVED | post-doubling footnote + 2× sensitivity arm + uncertainty bracket |
| RC-FLAG-4 | §5.1 lines 246–256 | RESOLVED | explicit blended formula |
| RC-FLAG-5 | §5.2 lines 337–338 | RESOLVED | citation split |

---

## Theater check

- §0.1 three-ground argument: **NOT theater.** Each ground is independently load-bearing; ground 3 (CLAUDE.md ideal-scenario clause) alone authorizes Stage-2; grounds 1 and 2 narrow the FAIL's scope. Argument is short but correct.
- §8 Stage-3-binding declaration: **NOT theater.** Anti-fishing is *strengthened* (Pareto-α floor + candidate-set closure are new binding constraints absent from v1.0).
- §14 "no threshold relaxed" claim: **VERIFIED.** N_MIN/POWER/MDES retain Stage-1 binding; bank-spread demotion is strictly less surface, not more. Bracket immutability preserved.

---

## Sub-task dispatch recommendation

**PROCEED** to Wave-2 MQ reverify. If Wave-2 concurs, dispatch TODO-COHORT-1..4 plans via `superpowers:writing-plans`. The 2 NEW RC-FLAGs are non-blocking and can land in v1.2 alongside any Wave-2 residue or be addressed inline at sub-task plan-authoring time.

— Reality Checker, Wave-1 reverify (v1.1)
