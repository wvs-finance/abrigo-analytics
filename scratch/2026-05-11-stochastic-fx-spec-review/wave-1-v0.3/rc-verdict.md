# RC Wave-1 v0.3 Verdict — stochastic-fx-variant-design

**Spec**: `docs/specs/2026-05-11-stochastic-fx-variant-design.md`
**Commit**: `9906ffa`
**Scope**: Narrow re-review — (1) FLAG-RC-1-v2 closure, (2) GBM-fix patch
isolation. v0.2 body already approved at ACCEPT_WITH_FLAGS level.
**Verdict**: **ACCEPT**

---

## Q1 — FLAG-RC-1-v2 closure (§3 `variance_proxy.py` prose-ification)

**Closed.** §3 lines 143–152 (the `variance_proxy.py` bullet) no longer
contain typed function signatures. The two v0.2 inline backtick forms

- `compute_sigma_t_per_path(ensemble) → ndarray`
- `apply_inversion(sigma_T_value, x_bar) → eps_value`

are replaced with prose:

> "Two free functions: one computes the per-path realised variance array
> from an ensemble's path matrix, the other applies the algebraic
> inversion of eq. (8) pointwise per Pin Z1.3a."

Plus an explicit closure clause:

> "RC-FLAG-1-v2 disposition: function signatures previously embedded here
> are now described in prose; full implementation signatures live in the
> implementation plan, not this spec."

`grep` of the full spec for `(...) → ...`-shaped tokens returns only
mathematical limit/implication operators (σ → 0, ⟹) and version-flow
arrows (v0.1 → v0.2) — none are function signatures. Pin Z1.3a still
quotes `apply_inversion(σ_T_n, x_bar) == sqrt(8·σ_T_n / x_bar²)` as a
**pointwise algebraic identity** (a mathematical assertion about the
function's behavior, not its declared signature), which conforms to
`memory/feedback_no_code_in_specs_or_plans.md` and was already accepted
at v0.2.

Compliance with `feedback_no_code_in_specs_or_plans.md`: **YES**.

## Q2 — Patch isolation (NEW-BLOCK-MQ-4 fix preserves rest of spec)

**Confirmed.** `git show 9906ffa --stat` = single file, +34/−10. Diff
inspection shows exactly four localized hunks:

1. Frontmatter `spec_version` bump (v0.2 → v0.3).
2. §3 `variance_proxy.py` bullet prose-ification (FLAG-RC-1-v2 closure).
3. §4.2 GBM `E[σ_T]` row correction (MQ's lane — not assessed here).
4. §11.3 promoted "reserve" → "landed"; §11.4 + §11.5 appended.

No collateral edits to other sections, no signature reshuffles elsewhere
in §3, no changes to Pins Z1.1–Z1.5, gate ladder, anti-fishing
invariants, or RC-FLAG-2/3/4 dispositions.

## FLAG-RC-2-v2 (NIT) — deferral

§11.4 explicitly defers FLAG-RC-2-v2 to a v0.3.1 cosmetic patch.
Consistent with my v0.2 verdict ("can be deferred"). No objection.

## Bottom line

Both narrow-scope questions resolve cleanly. FLAG-RC-1-v2 is materially
closed; the patch is focused and does not perturb the v0.2-approved
body. No new RC findings. Recommend RC-clean status pending MQ's own
verdict on the GBM formula.

**RC verdict**: ACCEPT (no FLAGs, no BLOCKs).
**Re-review trigger**: only if MQ blocks again on v0.3 and a v0.4 lands.

---
RC re-review completed 2026-05-12.
