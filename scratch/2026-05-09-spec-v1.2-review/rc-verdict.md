# Reality-Checker Verdict — Spec v1.1.1 → v1.2 Amendment

**Verdict:** ACCEPT
**Date:** 2026-05-08
**Scope:** `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (908 lines, v1.2)
**Authoritative inputs cross-referenced:**
- `scratch/2026-05-09-st-literature-survey/SURVEY.md` (TOP rec line 174)
- `docs/plans/2026-05-09-saas-cohort-close.md` v0.2 §0.1–0.3, §15 BLOCK-2 fix (ll. 351–353)
- Spec §14 CORRECTIONS-α format precedent (v1.0 → v1.1)

---

## Dimension-by-dimension findings

**1. §6.1 pin correctness — PASS.** Spec ll. 406–408 pins $S_t = (1-\lambda)^t$,
$\lambda \sim \mathrm{Beta}(4.5, 95.5)$. Verified arithmetic: mean
$= 4.5/100 = 0.045$ exact (matches §6.1 ll. 441–442). Independent scipy
computation: 95% CI = $[0.01379, 0.09319]$ vs. spec-stated $[0.013, 0.094]$
— accurate rounding. Concentration $\alpha+\beta=100$ correctly characterized
as "moderate-informative". 4–5%/mo benchmark anchor traceable to SURVEY.md
citation 5.

**2. Authority chain — PASS.** Spec §6.1 ll. 413–417 + §15.2 ll. 792–793
explicitly cite SURVEY.md, NOT C3 v0.3 implementation. §15.6 ll. 894–905
documents the directional ordering: `(literature + cohort economics) →
SURVEY.md → spec v1.2 §6.1 → C3 conformance check`, and explicitly
contrasts against the prohibited `(C3 v0.3) → spec ratification` ordering.
This satisfies CLOSE plan v0.2 BLOCK-2 fix (ll. 351–353).

**3. Five literature citations present — PASS.** Spec §6.1 ll. 417–421
enumerates the 5 SURVEY.md citations (Zammit&Zerafa 2025; Han,Hou&Chen 2018;
Equihua et al. 2023; Tsubota&Beppu 2025; Reichheld+Recurly/Paddle/Indie
Hackers). §15.2 ll. 810–822 re-lists them with arxiv IDs. Cross-checked
against SURVEY.md §5/§7 — citation set matches.

**4. Stage-3 falsification path — PASS.** Spec §6.1 ll. 452–460 states
$S_t = (1-\lambda)^t$ is the $k=1$ nested null inside Weibull
$S(t) = e^{-(\lambda t)^k}$, with falsification deferred to Stage-3
(LR test or posterior CI on $k$ excluding 1) per cited Han,Hou&Chen 2018.
Scope-boundary justification (synthetic-Bayesian Stage-2 lacks data to
identify $k$) is methodologically defensible — not a fishing escape hatch.

**5. Task 0.2b NO-OP authorization — PASS.** Spec §15.4 ll. 838–855
explicitly authorizes Task 0.2b as NO-OP because TOP recommendation matches
C3 v0.3 form. HALT-on-flip is preserved (ll. 850–855): "If C3 v0.3 source
code uses a different $\lambda$ prior … Task 0.2b becomes a NON-NO-OP and
a real re-fit is triggered". Matches CLOSE plan v0.2 §0.2b Step 5
(ll. 92).

**6. §15 CORRECTIONS-α block — PASS.** All five validity gates of
`feedback_pathological_halt_anti_fishing_checkpoint` documented at ll.
753–779: (a) external trigger MQ-FLAG-2; (b) ≥3 pivot options enumerated;
(c) decoupled lit-survey adjudication; (d) old/new/preserved-guarantees
delta table at §15.1; (e) Wave-1+2 reverify queued. Anti-fishing posture
§15.6 ll. 883–892 explicitly: "*strictly tightening* … No threshold
relaxed. No pin loosened. No candidate added."

**7. No collateral relaxation — PASS.** Sampled invariants verified
unchanged: §8 anti-fishing 10-item block (ll. 498–565); §6 $\Upsilon_t$
closed candidate set (4 forms); §9 PSIS-LOO-CV thresholds ($>4\cdot$SE
PASS, $<2\cdot$SE INDISTINGUISHABLE); $N_{\text{MIN}}=75$,
$\text{POWER}_{\text{MIN}}=0.80$, $\text{MDES}_{\text{SD}}=0.40$. §15.5
ll. 857–880 enumerates 7 preserved guarantees verbatim.

**8. Version header — PASS.** Header ll. 3–4 reads `spec_version: v1.2`
and `emit_timestamp_utc: 2026-05-08`. corrections_block field at ll. 11
extended to cite both §14 (v1.0→v1.1) and §15 (v1.1.1→v1.2).

**9. Coincidence framing — PASS.** §15.3 ll. 824–836 explicitly frames
the C3-v0.3 / SURVEY.md form match as **coincidence, not ratification**,
quoting SURVEY.md's $P\gtrsim 0.8$ no-op subjective probability. Counter-
factual stated: "Had SURVEY.md recommended Weibull-with-prior-near-$k=1$
… or BG/NBD …, v1.2 would have pinned that form and C3 v0.3 would have
been re-fit accordingly." This is the canonical anti-fishing framing.

---

## Residual flags

None blocking. The amendment satisfies all 9 reality-check dimensions
defaulted to REJECT under the integration-agent skeptical posture.

## Recommendation

PROCEED to Wave-2 MQ verify (CLOSE plan v0.2 §0.3 Step 2). On joint
ACCEPT/ACCEPT_WITH_FLAGS, advance Phase 0 to closeout and authorize
Task 0.2b NO-OP commit per §15.4.
