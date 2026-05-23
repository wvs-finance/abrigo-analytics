# RC verdict — STAGE_2_RESULTS.md (Stage-2 math anchor)

**Doc**: `notes/STAGE_2_RESULTS.md` (761 lines).
**Plan pin**: `docs/plans/2026-05-09-stage-2-results-anchor.md` v0.2.
**Frozen HEAD**: `9fd92e5`. **Reviewer HEAD**: `4363fcc`.
**Verdict**: **ACCEPT_WITH_FLAGS** (2 minor FLAGs; no BLOCKs).

---

## §1 Reality-check dimensions evaluated

### D1 §-skeleton compliance — PASS
Doc has §0 Preface, §1 Empirical verdict, §2 Math claims index (§2.A 8
primitives + §2.B 5 pins + §2.C 8 forward-fix + §2.D 8 artifact rows),
§3 Cohort cross-cut (4 sub), §4 Anti-fishing case studies (3:
C1-marg, C2-bracket, C4-1/κ), §5 Reproducibility certificate, §6
Stage-3 hand-off (10 items, no magnitude promises), §7 References.
Matches plan §1 pin and the 29-§2-entries count (8+5+8+8) exactly.

### D2 file:line resolution at 9fd92e5 — PASS
Sampled and verified at frozen HEAD via `git show 9fd92e5:<f> | sed -n
'<line>p'`:
- `notes/PRIMITIVES.md:186-191` (eq. 6) — verbatim FX path closed form. PASS.
- `notes/PRIMITIVES.md:204-208` (eq. 7), `:212-215` (eq. 8), `:228-233`
  (eq. 10), `:243-247` (eq. 11) — all verbatim. PASS.
- `simulations/modules/fx_path.py:66-72` — `FXPath.__call__` with
  `cos²(ωt)` body. PASS.
- `simulations/saas_builder/cohort_4/pi_derivation.py:70-100` —
  `_step_5a_variance_proxy_symbolic` docstring with PRIMITIVES.md §6+§7
  chain. PASS.
- `cohort_4/pi_derivation.py:113-122` — `_step_4_carr_madan_K_hat` with
  `K̂ = K⋆/(2√σ₀)`. PASS.
- `cohort_4/pi_derivation.py:124-141` — `derive_pi_t_symbolic`; closed-form
  docstring `π = K⋆·ε²·(X̄/Ȳ)²·(4ωt·cos(4ωt)−sin(4ωt))/(64·ω·√σ₀·t²)`
  and `Note κ ∉ free_symbols`. PASS.
- `cohort_4/pi_derivation.py:324-330` — `assert_perpetual_identity_symbolic`
  with sympy.S.Zero claim. PASS.
- `cohort_2/derivatives.py:118-129` — softplus q_t symbolic build. PASS.
- `cohort_2/sign_cert.py:240-298` — gate evaluator loop. PASS.
- `cohort_2/pricing.py:114-145` (fitter), `:158-209` (composer) — PASS.
- `priors.py:163-227` — `TruncParetoAlphaPrior` with `alpha_lower >= 1.5`
  spec §8(6) wording. PASS.
- `model.py:91-93` — `M3_SONNET_BLENDED_PRICE_EXPECTED = 7.1495`. PASS.
- `model.py:116-144`, `model.py:281-299` — present. PASS.
- `cohort_4/types.py:72-73` — `FX_HIGH_BRACKET = 4200.0; FX_LOW_BRACKET =
  3800.0`. PASS.
- `cohort_4/z_cap.py:138-220` — `PerDrawZEvaluator`. PASS.

### D3 pytest test name resolution — PASS
Sampled 11 cited test names; all resolve in the named test files at HEAD:
`test_property_7_marginalization_numerical_equivalence` (test_saas_builder.py:786);
`test_default_alpha_lower_is_1_5` (:120); `test_alpha_lower_below_1_5_raises`
(:128); `test_closed_form_evaluates_within_tolerance` (:214);
`test_synthetic_tau_round_trip` (:504); `test_grid_has_24_brackets`
(test_saas_cohort2.py:668); `test_fitter_returns_smallest_beta_satisfying_pin_m2`
(:152); `test_kappa_not_in_free_symbols` (test_saas_cohort4.py:146);
`test_perpetual_identity_symbolic` (:151); `test_grid_is_5_tuple` (:164);
`test_r3_classify_indistinguishable_band` (test_saas_cohort3.py:231).

### D4 sha256 anchors verbatim — PASS (live re-hash)
Live `python3 -c "import json; print(json.load(open(...))['audit_block'])"`:
- `Z_cap_pinned.json::audit_block` = `1fb1f7a42131268f3448da8d61b685ce27fe1facf356122e557ac10d329b5d31` — matches doc §0 ll. 27-28, §2.C.6 l. 375, §2.D.7, §5 l. 586. PASS.
- `gate_verdict.json::audit_block` = `4da660b55e7ad33071711dc313f12a4d06283717e7a332a7f7ddcd8a19672173` — matches §0 l. 30, §2.C.2 l. 299, §2.D.3, §5 l. 588. PASS.
- `revenue_form_verdict.json::audit_block` = `588a491b...8adb` — matches §2.C.4 l. 334, §2.D.6, §5 l. 593. PASS.
- `_AUDIT.json::audit_block` = `ded06012...162a` — matches §2.C.1 l. 281, §5 l. 595. PASS.

### D5 Forward-fix claim provenance — PASS (3-spot-check)
- §2.C.1 marginalization → plan v0.4 CORRECTIONS-α v0.3→v0.4 (cited);
  ESS 38→7,537→338,540 figures match cohort-1 audit verdicts. OK.
- §2.C.6 π(t) closed form → plan v0.3 honest derivation; FLAG-1
  `(X̄/Ȳ)²` restoration + BLOCK-4 σ₀ anchor cited; cross-walked to
  audit dir `2026-05-08-saas-cohort-4-independent-audit/`. OK.
- §2.C.4 Beta(4.5, 95.5) → spec v1.2.1 §6.1 (correctly cited). OK.

### D6 §4 detection-heuristic enumeration — PASS
- §4.1 cites tautological-identity audit + derivation-anchor citation check.
- §4.2 cites free-symbol audit.
- §4.3 cites sign-target retro-fit audit + derivation-anchor citation check.

### D7 §6 no magnitude promises — PASS
§6 explicit at l. 622: "**No magnitude promises.**" Item 5 (l. 641-644)
states "Stage-3 MUST NOT inherit these as magnitude predictions". No
"scale up" / "commercial readiness" language anywhere in §6.

### D8 Freeze-pin authority chain — PASS-WITH-FLAG-1
`git merge-base --is-ancestor 9fd92e5 HEAD` → ancestor confirmed.
`git diff 9fd92e5 HEAD -- simulations/` shows ONLY `simulations/README.md`
modified (added user-manual content per plan v0.2). No substantive code
diff under `simulations/saas_builder/` or `simulations/modules/`.

### D9 Tone — PASS
Doc reads as math-anchor-precise, claim-indexed. Distinct from the
verdict-memo narrative. Anchor tails enforced consistently.

---

## §2 Findings

### FLAG-1 (minor) — README.md drift not acknowledged
Doc §0 ll. 22-24 claims "Substantive Stage-2 codepaths (`simulations/`...)
have not changed since `9fd92e5`." Live `git diff 9fd92e5 HEAD --
simulations/` shows `simulations/README.md` modified (~140 lines added).
The change is non-substantive (user manual additions), but the §0 wording
casts the freeze as `simulations/` directory-scope rather than
"substantive codepaths under `simulations/saas_builder/` and
`simulations/modules/`". §5 ll. 612-614 already carves an explicit
exception for "Cosmetic post-freeze commits outside those paths"; §0 should
make the same carve-out for consistency. **Suggested fix**: §0 add
parenthetical "(simulations/saas_builder/ + simulations/modules/ +
simulations/types/ + simulations/utils/ + simulations/tests/; the
README.md user-manual additions of `4363fcc` are doc-only and outside
the freeze pin per §5)".

### FLAG-2 (minor) — Eq. (10) inequality strictness wording
§2.A.4 l. 106 reproduces `Δ^(a_s) = ... < 0` as "claim verbatim". The
PRIMITIVES.md eq. (10) shown at 9fd92e5 does include the `< 0`
inequality, so this is verbatim — but readers may misread as the doc
*asserting* strict negativity rather than reproducing the source claim.
Consider adding a single clarifying word ("the boxed primitive
asserts...") at first occurrence. Non-blocking.

---

## §3 Verdict
**ACCEPT_WITH_FLAGS.** All §2 sha256s match live artifacts byte-for-byte.
All sampled file:line citations resolve at `9fd92e5`. All sampled pytest
test names exist. §-skeleton matches plan pin. §6 contains explicit "No
magnitude promises" + ten-item Stage-3 hand-off without scale-up claims.
Two minor wording FLAGs (D8 README-scope + D2 inequality strictness) do
not affect the doc's load-bearing role as Stage-3 import point. Doc may
be merged after FLAG-1 wording fix; FLAG-2 optional.
