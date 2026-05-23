---
artifact_kind: independent_methodology_audit_verdict
auditor: Model QA Specialist (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-09
target_artifact: docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md
default_verdict: REJECT
---

# MQ Verdict — SAAS-COHORT-CLOSE Phase 5 Memo

**Verdict: ACCEPT_WITH_FLAGS** (3 FLAGs; 0 BLOCKs)

The memo's headline claims are supported by artifacts: 24/24 Δ < 0 (gate_verdict.json `audit_block 4da660b5…2173`), Z_cap pin 4687.94 COP/mo with strictly-positive CI lower bound 168.17 (Z_cap_pinned.json), perpetual-identity residual 6.31e-09, Cohort-3 INDISTINGUISHABLE reported honestly with Δelpd/SE = 1.67 < 2.0 (l. 188-191). Anti-fishing remediations (1/κ removal C4 v0.2→v0.3; 24-bracket re-orientation C2; spec v1.2→v1.2.1) are framed as caught-and-fixed defects, not routine bugs (§6 table, l. 268-281). Stage-3 limitations (l. 286-311) enumerate gaps without making forward-looking magnitude promises; the §8 product-surface translation discloses the $1.17/mo USD-equivalent honestly without burying it (l. 320-326). MC-budget chain (1.32e-2 breach → Path α 4k→178k×4chains=712k → ESS 338,540, l. 122-124, 232-234) is internally consistent and matches `_AUDIT.json`.

However, three flags require correction before final commit.

---

**FLAG-1 (Material — π contribution magnitude misstatement) — l. 295-296**

Verbatim quote: *"The π contribution to $Z_{\text{cap}}$ is small relative to the $q_t/(\bar{X}/\bar{Y})$ baseline (~5% of nominal $Z_{\text{cap}}$)."*

Artifact evidence (`Z_cap_pinned.SIGN_VERDICTS.md` ll. 23-25):
- |π|_TP1 = 4687.727
- Z_cap_TP1 = 4687.942

The π-magnitude is ~99.995% of Z_cap, not ~5%. The user's framing in the audit prompt was correct: at v0.3 fixtures the π contribution was ~1e-10 vs baseline ~0.2 (negligible), but at the *pinned* TP1 (X̄/Ȳ=4000, σ₀=20000), π *is essentially Z_cap* via the relation Z_cap = π · (X̄/Ȳ) · q_t with the post-1/κ-removal scaling. The "5%" claim is unsupported by any extant artifact and inverts the actual decomposition. **Required fix:** either re-derive the π-share with arithmetic shown, or replace with "π is the dominant scale factor in Z_cap; the small absolute magnitude (4687 COP) reflects the (X̄/Ȳ)² coupling at calibrated σ₀=20000 rather than a π-vs-baseline split."

---

**FLAG-2 (Material — Z_cap CI table over-uniformizes across FX brackets) — l. 219-221**

Memo §4.4 table reports CI = [168.17, 14606.14] for TP1, TP2, TP3, TP4, TP5 uniformly. Artifact `Z_cap_pinned.json` shows TP4 CI = [176.58, 15336.38] and TP5 CI = [159.76, 13875.90] — strictly different from TP1-TP3. The memo's "[168, 14606]" is the TP1 CI, not the cross-TP envelope. **Required fix:** report per-TP CIs (matching the SIGN_VERDICTS.md sidecar table) or explicitly label [168.17, 14606.14] as "TP1 CI; TP4/TP5 shift monotonically with FX per Pin M2 §6". The current presentation suggests CI invariance under FX shift, which contradicts the §6 monotonicity check (l. 19, SIGN_VERDICTS.md).

---

**FLAG-3 (Minor — "structurally viable" claim faithfulness) — l. 25-28**

Verbatim quote: *"the SaaS-Builder cohort hedge is **structurally viable** as a permissionless convex instrument under the Stage-2 ideal-scenario assumption; magnitudes are small but architecturally sound"*

The aggregate claim is supported (sign PASS 24/24, identity PASS 5/5, CI_lo > 0, perpetual-identity sympy-exact). However, "structurally viable" reads as a stronger statement than the synthetic-Bayesian regime warrants — viability typically implies the instrument *works* in some economic sense, whereas Stage-2 has demonstrated only that the *mathematical architecture* is internally consistent under a fully prior-driven model. **Recommended softening:** "structurally well-formed" or "architecturally consistent under the synthetic-Bayesian regime" — preserving §8's honest framing ("The Stage-3 question is whether real-data magnitudes scale up to be commercially material — that is not a Stage-2 question and Stage-2 does not pretend to answer it", l. 322-326) without leaking implicit magnitude approval into §1.

---

**Confirmed sound (no findings):**
- Δ magnitude reconciliation (l. 161-168): β·κ ≈ 2.33e4 → softplus saturation → q_t collapses to floor — analytic prediction matches; no fishing.
- C3 INDISTINGUISHABLE language (l. 180, 188-191): correctly *not* reported as "ar1_log wins"; det_churn pinned per spec §6.1, with HALT-on-flip safeguard documented (no flip detected, l. 194-198).
- C4 1/κ removal framed as anti-fishing violation (§6 row 4, l. 274), not bug fix.
- HALT triggers documented: MC-budget breach + Path α resolution (l. 232-234); spec v1.2→v1.2.1 prior-mismatch BLOCK (§6 row 5, l. 275); C3 INDISTINGUISHABLE rather than silent default-to-martingale (l. 180).
- No Stage-3 magnitude promises; §8 explicitly disclaims (l. 322-326).

**Disposition:** ACCEPT_WITH_FLAGS — fix FLAG-1 and FLAG-2 (factual corrections against artifacts) before commit; FLAG-3 is a recommended softening.

**Authoritative artifacts cross-checked:**
- `/home/jmsbpp/apps/abrigo-analytics/simulations/saas_builder/data/Z_cap_pinned.json`
- `/home/jmsbpp/apps/abrigo-analytics/simulations/saas_builder/data/Z_cap_pinned.SIGN_VERDICTS.md`
- `/home/jmsbpp/apps/abrigo-analytics/docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`

End of MQ verdict on Phase 5 memo.
