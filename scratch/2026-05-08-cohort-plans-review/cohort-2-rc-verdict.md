# RC Verdict — Plan `2026-05-08-saas-cohort-2-t2-pricing-sign.md` v0.1

**Wave:** 1 of 2 (Reality Checker). **Default:** REJECT.
**Verdict:** REJECT.
**Plan path:** `/home/jmsbpp/apps/abrigo-analytics/docs/plans/2026-05-08-saas-cohort-2-t2-pricing-sign.md`

## Dimension-by-dimension reality check

1. Agent dispatchability — PASS. `gsd-phase-researcher` is in active registry; AI Engineer / Reality Checker / Model QA Specialist / Code Reviewer referenced exist outside `_archived/` (verified `find ~/.claude/agents -name '...'`).
2. C1 dependency gate — PASS. Phase 0.4 (lines 118–122) explicitly HALTs if `synthetic_tau_t.parquet` + `cohort_prior.parquet` absent and cross-checks column names against spec §10 lines 516–517. Schema list verbatim-equivalent.
3. File-path concreteness — ACCEPT_WITH_FLAGS. No TBDs, but `simulations/utils/errors.py` (line 223) is referenced as if shipped without verification step; pre-task patch is conditional ("if not present, contribute a one-line addition"). FLAG-1.
4. Math-pin verbatim — **BLOCK-1.** Plan line 89 pins BRACKET-M5 as `$\overline{X/Y} \;\in\; \{4200,\; 3800,\; 4200\}$` — i.e., three distinct *FX-path means*. Authoritative shipped contract (`simulations/tests/test_modules.py:185,194` + `simulations/tests/README.md:32`) defines `(4200, 3800, 4200)` as FX-path *values at three sample times* $t \in \{0,\pi/2,\pi\}$ around a single $\overline{X/Y}$. Spec §3 (lines 133–135) further pins one $\overline{X/Y}$ as the 12-month trailing TRM mean, sha-pinned per audit_block. The plan re-types path-points-at-time-t as an enumeration over means. This is a **mathematical type error**, not a verbatim citation. Sign-cert gate built on this misreading would HALT or PASS for the wrong reason. M2 wording (line 75) is verbatim-equivalent to spec line 227–228 (`< 10^{-3}\cdot\kappa` ↔ `< \epsilon\cdot\kappa, \epsilon = 10^{-3}`) — accept.
5. Δ closed-form citation — PASS-WITH-FLAG. Plan line 82 cites `PRIMITIVES.md §7 eq. (7')` for Δ-cohort, does not silently re-derive. NOTE: user's brief said "PRIMITIVES.md §10 Δ closed forms" but PRIMITIVES.md §10 is Carr-Madan; §7 is correct. Plan cites §7 — accept; user brief had typo. FLAG-2.
6. Bank-spread overlay arm — PASS. Phase-2 Task 2.4 (lines 260–282) defines `BankSpreadRobustnessRunner`; emits to `ROBUSTNESS_RESULTS.md` (line 318, 332); explicitly walled off from primary `gate_verdict.json` (line 273); not theatrical.
7. Sign-expectation pre-pin — **BLOCK-2.** Plan line 90 declares `Δ^(a_s) < 0` strict expectation pre-pinned at "every bracket point × every (ε, ω) grid cell." However, gate verdict enum (line 198, 274) uses `Literal["PASS","FAIL","HALT"]`, while spec §10 line 520 pins enum verbatim as `"PASS|WEAK|MARGINAL|FAIL|INDISTINGUISHABLE"`. Plan silently truncates the spec-pinned verdict alphabet. Schema-write validation (line 274) would either fail or coerce. This is silent threshold relaxation banned by §8 anti-fishing.
8. Out-of-scope discipline — PASS. Lines 27 enumerate hard exclusions: T1 latent (COHORT-1), $\Upsilon_t$ (COHORT-3), Z-cap (COHORT-4), Stage-3 deployment, mutation of shipped `simulations/{types,modules,utils}/`. Clean.
9. Audit-pass chain canonical Honnibal ordering — PASS. Tasks 3.1–3.6 enumerate tighten-types → contract-docstrings → hypothesis-tests → try-except → pre-mortem → mutation-testing in canonical order (lines 351–395). Pre-mortem precedes mutation-testing as required.
10. 2-wave verifier structure — PASS. Phase 4 separates Reality Checker (4.1) + Model QA Specialist (4.2) before Code Reviewer (5.1, lines 464–468). Plan-doc verify note line 458 acknowledges the pre-commit 2-wave is foreground-orchestrated.

## BLOCKs (must fix to clear REJECT)

- **BLOCK-1 (line 89, line 198 BracketGrid validator, line 303 test).** Re-state BRACKET-M5 as a single audit_block-pinned $\overline{X/Y}$ (12-month TRM mean per spec §3) with the FX-path values $(X/Y)_t$ at $t \in \{0, \pi/2, \pi\}$ recovering `(4200, 3800, 4200)` *as a verification target*, not as a sweep over means. The (ε, ω) grid is the actual sweep; bracket points are the spec §5.2 parameter brackets, not FX-mean enumerations.
- **BLOCK-2 (lines 198, 274, table line 491).** Replace verdict literal `"PASS|FAIL|HALT"` with the spec §10 verbatim alphabet `"PASS|WEAK|MARGINAL|FAIL|INDISTINGUISHABLE"`. HALT is a foreground action, not a verdict-enum value.

## FLAGs (non-blocking; address in v0.2)

- **FLAG-1 (line 223).** Verify `simulations/utils/errors.py` shipped state in Task 0.3, not conditionally inside Task 2.2. If absent, escalate to SIM-INFRA-0 owner per line 116, do not patch from this plan.
- **FLAG-2 (line 20).** User-brief's "§10 Δ closed forms" was a typo (Carr-Madan vs §7); plan cites §7 correctly. No plan change needed; record in 2-wave verdict bundle.

## Disposition

REJECT — return to author for v0.2 with BLOCK-1, BLOCK-2 fixes; CORRECTIONS-block + 3-way review per `feedback_pathological_halt_anti_fishing_checkpoint`. Wave-2 (Model QA) should re-run after v0.2 commits.

Word count: ~570.
