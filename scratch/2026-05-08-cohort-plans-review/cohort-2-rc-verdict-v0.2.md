# Cohort-2 Reality Checker reverify — plan v0.2 (CORRECTIONS-α)

**Plan:** `docs/plans/2026-05-08-saas-cohort-2-t2-pricing-sign.md` v0.2
**Reverify date:** 2026-05-07
**Predecessor verdict:** `cohort-2-rc-verdict.md` (v0.1) — REJECT, 2 BLOCKs + 2 FLAGs
**Authoritative inputs cross-checked:** spec v1.1.1 §3 lines 133–135, §10 line 520; PRIMITIVES.md §7; shipped `simulations/tests/test_modules.py:178–221`.

## Verdict

**ACCEPT**

Both RC-BLOCKs resolved at the semantic level required by spec and shipped tests. Both RC-FLAGs folded with structural rather than cosmetic fixes. CORRECTIONS-α block (lines 555–575) is internally consistent with the patches it claims.

## RC-BLOCK-1 — BRACKET-M5 semantic mistyping → RESOLVED

v0.1 framed `(4200, 3800, 4200)` as three distinct FX-path means (an enumeration over $\overline{X/Y}$). v0.2 rewrites this consistently across all six sites:

- **Pin BRACKET-M5 (line 89):** "one TRM-pinned $\overline{X/Y}$ … the triple `(4200, 3800, 4200)` is the set of FX-path **values** $(X/Y)_t$ at sample times $t \in \{0, \pi/2, \pi\}$ that the M5 sinusoidal FX-perturbation kernel produces *around* the single TRM-pinned mean."
- **`BracketGrid` value-type contract (line 198):** construction validates against M5 path-reconstruction at sample times.
- **Verification matrix (line 494), RC compliance brief (line 417), anti-fishing posture (line 549):** all carry the path-reconstruction semantic; the (ε, ω) grid is the actual sweep; FX-mean enumeration is banned.

Cross-check against shipped `test_modules.py:184–194` confirms canonical reference: `FXPathParams(mean_x_over_y=4000.0, epsilon=0.1, omega=1.0)` at `ts = [0, π/2, π]` yields `[4200.0, 3800.0, 4200.0]`. Single mean, three sample-time values. v0.2 matches exactly. Spec §3 line 133 ("12-month trailing TRM mean … sha-pinned per audit_block") corroborates the single-mean reading.

## RC-BLOCK-2 — Verdict alphabet truncation → RESOLVED

v0.1 declared `Literal["PASS","FAIL","HALT"]`. Spec §10 line 520 verbatim: `PASS|WEAK|MARGINAL|FAIL|INDISTINGUISHABLE`. v0.2 carries the full alphabet at:

- Line 198 — `CohortGateVerdict.verdict: Literal["PASS","WEAK","MARGINAL","FAIL","INDISTINGUISHABLE"]`.
- Line 274 — `gate_verdict.json` schema string `"PASS|WEAK|MARGINAL|FAIL|INDISTINGUISHABLE"`.
- Line 497 — verification matrix row matches spec §10 line 520 character-for-character.

HALT clarified at lines 198, 274 as a foreground harness action, NOT a verdict-enum value written to artifacts. Unblocks JSON schema validation on write.

## RC-FLAGs — both folded structurally

- **RC-FLAG-1 (errors.py verification level):** promoted from conditional Task 2.2 fallback to Phase-0 Task 0.3 Step 3 (line 115) with explicit HALT-and-escalate to SIM-INFRA-0 owner if `M2TightnessNotAchievedError` absent. Task 2.2 (line 223) references the Phase-0 check rather than re-checking. Correct ordering: blocking dependency verified before downstream Tasks dispatch.
- **RC-FLAG-2:** addressed within the CORRECTIONS-α block alongside the MQ flags.

## Residual notes (non-blocking)

None warranting downgrade. Anti-fishing invariants preserved (BRACKET-M5 grid immutable at Value-type construction; bank-spread arm structurally walled off from primary verdict).

## Authority

Reality Checker — Cohort-2 plan v0.2 reverify. Predecessor verdict superseded.
