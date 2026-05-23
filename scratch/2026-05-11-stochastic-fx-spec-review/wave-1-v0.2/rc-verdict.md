# RC verdict — stochastic-fx-variant-design v0.2 (Wave-1 re-review)
**Reviewer:** Reality Checker (RC)
**Spec under review:** docs/specs/2026-05-11-stochastic-fx-variant-design.md @ commit `6b1a466`
**Date:** 2026-05-12
**Verdict:** ACCEPT_WITH_FLAGS

v0.2 substantially closes the v0.1 review surface. MQ's three BLOCKs are
honestly disposed (not renamed): the math reframing in §4.2 + Pin Z1.3a/b
split is structurally correct, the per-family parameter pin table is
present with concrete numerical values, and the hand-derived moment table
carries literature anchors (Hull, Andersen-Piterbarg). The anti-fishing
posture is materially stronger (KS calibration rationale + N-floor rule).
Strip preservation (Pin Z1.6) is now verifiable by direct hex grep and
the grep succeeds against the live JSON.

Two of my four v0.1 FLAGs are NOT fully closed, however — see FLAG-RC-1-v2
and FLAG-RC-2-v2 below. Neither is a BLOCK; both are honest residuals that
should be cleaned in a v0.2 → v0.2.1 patch BEFORE plan authorship, not
re-dispatched as another Wave-1 cycle.

---

## Prior-FLAG closure status

| Prior FLAG | v0.2 location | Status |
|---|---|---|
| FLAG-RC-1 (§3 code-like signatures) | §3 lines 145–146 still present | **NOT FULLY CLOSED** — see FLAG-RC-1-v2 |
| FLAG-RC-2 (§15 unnumbered-bullet citation) | §1 table line 69 unchanged | **NOT FULLY CLOSED** — see FLAG-RC-2-v2 |
| FLAG-RC-3 (Pin Z1.6 hex grep, not `git log -p`) | §5 line 299 + §8 line 417 + §6 line 323 | **CLOSED** |
| FLAG-RC-4 (new gitignore line called out explicitly) | §4.1 step 5 lines 228–231 + §11.2 line 492 | **CLOSED** |

---

## Findings on v0.2

### FLAG-RC-1-v2 — §3 STILL contains code-like function signatures (commit claim is partially false)

**Severity:** Material FLAG (not BLOCK; honest mistake, not a math defect).

Commit message asserts: *"§3 ASCII tree code-like signatures removed
(RC-FLAG-1 disposition); per-file responsibilities described in prose per
feedback_no_code_in_specs_or_plans.md."*

The ASCII tree at lines 110–120 was correctly stripped (just filenames now,
no signatures). **But** §3's prose paragraph on `variance_proxy.py` (lines
144–146) reads:

> Free function `compute_sigma_t_per_path(ensemble) → ndarray`.
> Free function `apply_inversion(sigma_T_value, x_bar) → eps_value`
> implements eq. (8) algebraically per Pin Z1.3a.

These are typed function signatures with `(args) → return-type` syntax —
exactly the pattern `memory/feedback_no_code_in_specs_or_plans.md` lines
7–13 forbid ("no function signatures"). The commit message claims removal;
the live spec contradicts the claim.

**Disposition ask:** in a v0.2.1 cleanup, replace with prose, e.g.: "a free
function computing σ_T per path from the ensemble, returning a numpy
array" and "a free function applying eq. (8) algebraically given σ_T and
x_bar, returning the inverted ε value". This is a 30-second edit; should
NOT trigger another Wave-1 re-dispatch cycle.

### FLAG-RC-2-v2 — §1 cross-references table still says "§15 open item 2" without the bullet-count caveat

**Severity:** NIT.

My v0.1 FLAG-RC-2 disposition ask was: "drop '2' and cite by bullet text".
v0.2 §11.1 NIT-RC-2 row (line 483) acknowledges the caveat ("§15 uses
unnumbered bullets — bullet count is the unambiguous reference"), but §1
table line 69 itself still reads raw `§15 open item 2`. The caveat lives
only in the disposition log, not at the citation site. Cheap fix: append
"(by bullet position; §15 uses unnumbered bullets)" inline at line 69. NIT
because the citation does resolve correctly by count.

### NIT-RC-1-v2 — §11.1 line 482 mislabels the v0.1 finding ID

**Severity:** NIT (cosmetic).

§11.1 disposition table uses `FLAG-RC-1` for the §3-signatures finding (my
v0.1 ID was indeed `FLAG-RC-1`, material), and `NIT-RC-2 / NIT-RC-3 /
NIT-RC-4` for my §15-citation / Pin-Z1.6 / gitignore findings (my v0.1 IDs
were `FLAG-RC-2 / FLAG-RC-3 / FLAG-RC-4` — all marked NIT severity in the
v0.1 verdict). This is a renaming-not-renaming inconsistency; the
substance is correctly disposed. No action required, but the IDs should
match the source verdict.

### NIT-RC-2-v2 — Footer line 528 still says "v0.1"

**Severity:** NIT (cosmetic).

End-of-document footer: *"End of stochastic-FX variant design spec v0.1."*
Frontmatter is v0.2. Single-character fix.

---

## MQ-BLOCK disposition accuracy

| MQ finding | v0.2 disposition location | Accurate? |
|---|---|---|
| BLOCK-MQ-1 (eq. 6 reduction ill-posed) | §4.2 trivial-degenerate note (lines 273–287) + §5 Pin Z1.3a (line 295) — both explicitly state "trivial degeneracy, not a reduction to eq. (6)" with per-family parameter axes (σ→0, θ→∞, λ→0) yielding point mass at x_0 | YES — math claim honestly downgraded |
| BLOCK-MQ-2 (KS-test undefined / tautological) | §4.1 Phase C (lines 218–224) + §5 Pin Z1.4 (line 297) — adopts MQ recommendation (c): moment-matched parametric reference (gamma for OU, lognormal for GBM/Merton) per §4.2 table | YES — tautology removed, external reference defined |
| BLOCK-MQ-3 (sympy cannot do Itô calculus) | §3 new `moments.py` Callable-tier module (lines 151–156) + §4.2 hand-derived moment table (lines 263–267) with literature anchors (Hull §15, Andersen-Piterbarg Vol I §2.7) + §5 Pin Z1.3b (line 296) — sympy explicitly scoped to (a) algebraic inversion and (b) `sympy.latex()` rendering | YES — symbolic scope honest |
| FLAG-MQ-1 (KS 0.01 calibration) | §8 lines 392–404 — rationale (MC-noise-matched comparison) documented; FROZEN-at-v0.2 language present | YES |
| FLAG-MQ-2 (family-parameter dependence of mapping) | §4.2 + §11.1 disposition row | YES |
| NIT-MQ-1 (B1 σ_T contract cross-ref) | §4.1 step 3 (line 200) cites MQ-FLAG-B1.1 disposition | YES |

**§4.2 per-family parameter pin table verification.** Lines 254–258 contain
concrete numerical pins per family: GBM (μ=0, σ=0.10/√12, x_0=4000, T=12,
n_steps=5000); OU (θ=1.0, μ̄=4000, σ=0.10·4000/√(2·1.0), …); Merton (μ=0,
σ=0.05/√12, λ=1/year, μ_J=0, σ_J=0.10, …). Values are consistent with the
cohort_5_strip canonical fixture (x̄=4000, ε=0.1, T=12). Reference
distribution per family pinned (lognormal/gamma/lognormal). Pin Z1.1 has
diff-visible content now, not deferred docstrings.

**Hand-derived analytic moment expressions.** Table at lines 263–267 gives
E[σ_T] per family with explicit literature anchor (Hull §15 Itô variance
estimator for GBM; standard OU stationary variance; Andersen-Piterbarg Vol
I §2.7 for Merton). Var[σ_T] forms are deferred to the `.tex` fragments
but the table is the canonical authority for Pin Z1.3b. Math content is
non-trivial and properly anchored.

---

## Anti-fishing posture (§8)

**KS-gate 0.01 calibration.** §8 lines 392–404 document: (a) the threshold
is permissive vs. conventional 0.05; (b) rationale is that both sides of
the test are MC-noise-bearing estimates of the same population quantity
(empirical σ_T_n vs. parametric reference fit to discretization-implied
moments); (c) the calibration is FROZEN at v0.2 and tightening to 0.05
requires CORRECTIONS-α + version bump. Honest framing.

**"Never increase N until passing" rule.** §8 lines 405–412 explicit:
N=1000 is a FLOOR, not a parameter to grow. Failure dispositions per Pin
Z1.5 routing: drop family, substitute reference shape, refine
discretization. NEVER raise N silently. Forecloses the most subtle
KS-gate-fishing pattern.

---

## Strip preservation (Pin Z1.6)

Live grep of the audit_block hex against the JSON returns:

    "audit_block": "94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329",

Full 64-hex match, bit-exact. Pin Z1.6 binding to a live artifact, not
just to a git-log assertion. RC-FLAG-3 cleanly disposed.

---

## Convention compliance

- **No Python code blocks in §3.** Searched for ` ```python ` / ` ```py `
  fenced blocks: ZERO matches across the spec. PASS.
- **Spec lives at `docs/specs/`**, NOT `docs/superpowers/specs/`. Verified
  by `ls`. PASS.
- **No code in spec body** at the fenced-block level. The two residual
  signature strings flagged under FLAG-RC-1-v2 are in inline-backtick
  prose, not in fenced blocks — but still violate `feedback_no_code_in_specs_or_plans.md`
  which forbids "function signatures" categorically.

---

## Verdict

**ACCEPT_WITH_FLAGS.** 2 residual material/NIT FLAGs (FLAG-RC-1-v2 +
FLAG-RC-2-v2) + 2 cosmetic NITs. NO BLOCKs. The math reframing is sound
and MQ's three BLOCKs are honestly disposed.

**Recommended next step:** v0.2 → v0.2.1 patch addressing FLAG-RC-1-v2
(remove the two residual signature strings in §3 lines 145–146) and
FLAG-RC-2-v2 (inline the bullet-count caveat in §1 line 69). This is a
CORRECTIONS-α cosmetic patch, NOT a re-dispatch trigger — under
master-spec §6.1, ACCEPT_WITH_FLAGS with cosmetic residuals does not
require another Wave-1 cycle. Plan authorship of
`docs/plans/2026-05-NN-stochastic-fx-variant.md` may proceed in parallel
with the v0.2.1 cleanup, contingent on MQ's parallel verdict also
landing ACCEPT-class.
