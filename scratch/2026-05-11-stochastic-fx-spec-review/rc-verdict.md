# RC verdict — stochastic-fx-variant-design v0.1
**Reviewer:** Reality Checker (RC)
**Spec under review:** docs/specs/2026-05-11-stochastic-fx-variant-design.md
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

Default-NEEDS_WORK posture relaxed: every load-bearing claim is
traceable, the strip-preservation invariant binds to a live bit-exact
match, and the anti-fishing posture is structurally honest. Flags are
NITs / disposition asks, not BLOCKs.

## Findings

### FLAG-RC-1 — §3 component tree contains typed function signatures
**Severity:** FLAG (not BLOCK; admissible per the orchestrator's RC
brief: "Tree-structure ASCII (in §3) and JSON-schema shape
illustrations are admissible").

`memory/feedback_no_code_in_specs_or_plans.md` is categorical: "no
function signatures". The §3 ASCII tree (lines 105–153) embeds typed
signatures inside the tree, e.g.
`GBMPathGenerator (frozen-dc, __call__(rng_seed: int, n_paths: int) → PathEnsemble)`
and `mc_inversion_check(ensemble: PathEnsemble, x_bar: float) → (ks_pvalue, empirical_eps_array)`.
These are clearly within the orchestrator's whitelist for THIS spec but
sit in tension with the global memory rule. **Disposition ask:** in
v0.2, replace `__call__(rng_seed: int, n_paths: int) → PathEnsemble`
with prose like "Callable mapping (rng_seed, n_paths) to a
PathEnsemble" so that the implementation plan still gets to choose the
final signature shape unsupervised.

### FLAG-RC-2 — §15 "open item 2" is non-numeric citation
**Severity:** NIT.

PRIMITIVES.md §15 (line 406+) uses *unnumbered bullets*. There is no
"item 2" literal in the source; the spec's frontmatter and §1 table
both label this as "open item 2". By bullet position, the
"Stochastic-FX variant (Path A v3): GBM, OU, jump-diffusion,
empirical-calibrated" bullet is indeed the second bullet under §15. The
citation resolves correctly by count, but PRIMITIVES.md should either
number the bullets or the spec should drop "2" and cite by bullet text
("§15 'Stochastic-FX variant' bullet"). Recommend the latter; cheaper.

### FLAG-RC-3 — Pin Z1.6 verification command is loose
**Severity:** NIT.

Z1.6 says: "`git log -p simulations/saas_builder/data/IronCondor_strip.json`
shows no commits between the strip's pin commit and the
stochastic-fx package merge." This proves the file is unchanged *in
git*, but the strip's audit_block is also a function of the COHORT-4
audit input + spec path; if either of those mutates upstream, a
re-emit would produce a different audit_block even with the strip
package untouched. Suggest tightening Z1.6 to: "the JSON file
`audit_block` field value remains literally `94150326...329` at
implementation-merge time, verified by direct grep, not by
git-log absence of edits." (This is implementation-plan
territory but worth flagging now.)

### FLAG-RC-4 — §4 step 4 gitignore reference points at strip's line, not stochastic_fx's
**Severity:** NIT.

§4 step 4 says: "gitignored at `.gitignore:53` — under
`simulations/saas_builder/data/` is gitignored; we'll add
`simulations/stochastic_fx/data/` to the gitignore as a single-line
addition." Verified: line 53 currently reads
`simulations/saas_builder/data/`. The spec correctly acknowledges that
adding `simulations/stochastic_fx/data/` is NEW work and that it isn't
yet present. NIT is purely cosmetic — the language is slightly
ambiguous on first read ("gitignored at .gitignore:53" sounds like the
new dir is already covered, when it isn't).

## Citation trace audit

| Claim location in spec | Cited anchor | Verified? | Notes |
|---|---|---|---|
| frontmatter `strip_anchor` | `simulations/saas_builder/cohort_5_strip/` | YES | Directory exists; `__init__.py` is 5673 bytes, exports the full strip API. |
| frontmatter audit `94150326...329` | `IronCondor_strip.json::audit_block` | YES | Direct JSON load returns `94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329` — bit-exact match, full 64 hex chars. |
| frontmatter commit `3442852` | git history | YES | `git rev-parse 3442852` resolves to `344285210a7579c205ed1b03275a4f879faf74b8` — "feat(saas-cohort-5-strip): Carr-Madan 3-condor (12-leg) IronCondor strip emit". |
| §1 table — PRIMITIVES.md §5 eq. (6) deterministic generator | `notes/PRIMITIVES.md:181` | YES | §5 line 181 contains eq. (6) cos² perturbation kernel verbatim. |
| §1 table — PRIMITIVES.md §6 eq. (7), (8) | `notes/PRIMITIVES.md:201` | YES | §6 line 201 contains eq. (7) variance proxy and the boxed eq. (8) `ε(σ_T)=√(8σ_T/(X̄/Ȳ)²)` inversion. Spec's quoted form matches the source's form. |
| §1 table — PRIMITIVES.md §15 open item 2 (Path A v3) | `notes/PRIMITIVES.md:406+` | PARTIAL | See FLAG-RC-2 — bullet count matches, but no explicit "item 2" numbering in source. |
| §1 table — STAGE_2_RESULTS.md §2.1 R1 σ_0 anchor | `notes/STAGE_2_RESULTS.md:44` | YES | §2.1 (R1) is the σ_0 anchor section; inverts eq. (8). Deterministic-limit reduction claim is coherent. |
| §1 table — master spec §3 cross-track graph | `docs/specs/2026-05-11-stage-3-first-wave-design.md:321` | YES | Master spec §3 contains the A1/A2/B1 dependency graph; stochastic-FX is correctly NOT listed in it. |
| §10 — `scratch/2026-05-11-stochastic-fx-spec-review/` | filesystem | YES | Directory exists (this verdict file is being written into it). |
| §11 anti-fishing routing via "master-spec §6.4" | `docs/specs/2026-05-11-stage-3-first-wave-design.md:468` | YES | §6.4 "BLOCK-routing escalation" exists and defines CORRECTIONS-α routing semantics consistent with Pin Z1.5's invocation. |
| §1 table — `memory/feedback_pathological_halt_anti_fishing_checkpoint.md` | filesystem | YES | File exists (2176 bytes). |
| §1 table — `memory/feedback_no_code_in_specs_or_plans.md` | filesystem | YES | File exists (1381 bytes). See FLAG-RC-1 for compliance commentary. |

## Anti-fishing posture audit

**Outcome-direction pre-pinning (the most common silent-fishing
pattern): clean.** §0 explicitly states "this spec does NOT pre-pin
which families will PASS or FAIL". §4, §5, §6, §8 all hold to that —
no smuggled language like "GBM will PASS" or "OU is the canonical
family". §8 explicitly forbids "re-run with more paths until passing"
(which would be silent-fishing on the KS gate). The KS threshold
`≥ 0.01` is the conventional rejection level, not an artificially soft
gate.

**Z1.5 routing through CORRECTIONS-α: structurally honest.** §6 HALT
table routes family-level FAILURES (sympy residual > 1e-6 OR
ks_pvalue < 0.01) through CORRECTIONS-α + scoped Wave-1 re-review per
master-spec §6.4 semantic. §8 reiterates: "A failed family is
documented honestly, not silently dropped or retuned to PASS." The
routing is verified-honest at the spec level; verification at Wave-2
will catch any silent re-tuning in practice.

**One subtle anti-fishing hole closed (commendable).** §7.5 explicitly
bans re-emission of cohort_5_strip under stochastic-path expectations.
This forecloses the most insidious failure mode: stochastic-FX
"passing" → engineer pressure to re-emit the strip "now that we
understand FX better" → strip's existing audit_block silently retuned
post-hoc. Pin Z1.6 backs §7.5 with a bit-exact invariant.

**Sympy "expected form" pre-derivation (§8 bullet 3): correct framing.**
The expected analytic ε form per family is derived from the SDE's
stationary variance closed form, not chosen to match Monte Carlo. This
is the only honest direction.

## Convention-compliance audit

**No-code-in-specs.** Scan for fenced `python` / `py` / `Python`
blocks: ZERO. Only two fenced blocks exist (lines 105 and 153), both
delimiting the ASCII component tree, which the orchestrator's RC brief
explicitly admits ("Tree-structure ASCII in §3 and JSON-schema shape
illustrations are admissible"). PASS at the literal level. See
FLAG-RC-1 for the tension with the global memory rule (typed
signatures inside the tree).

**Project path discipline.** Spec lives at
`docs/specs/2026-05-11-stochastic-fx-variant-design.md`, NOT
`docs/superpowers/specs/...`. Compliant with the project override.

**Strip preservation invariant.** Verified by direct JSON load: the
file `simulations/saas_builder/data/IronCondor_strip.json` field
`audit_block` literally contains
`94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329`,
exact 64-hex match with the spec's quoted value. No partial-truncation
ambiguity (`94150326…` resolves uniquely). Git history: the only
commit touching the JSON is the strip's pin commit; no subsequent
edits. Bit-exact preservation is currently true and binding.

**Cross-coupling check (§9 anti-coupling guard).** Grepped spec for
"cohort_5_strip": 13 mentions across §0, §1, §2, §3, §5 (Z1.6), §6,
§7 (defer + ban), §9 (independence claim), §12 (references). Every
single mention is either (a) READ-ONLY ("does NOT modify", "does NOT
consume", "does NOT import from"), (b) Pin Z1.6 preservation language,
or (c) §7.5 explicit re-emit ban. ZERO mentions assert any mutation
or extension of the strip. Independence claim is structurally honest.

## Verdict

**ACCEPT_WITH_FLAGS.** 4 FLAGs (3 NITs + 1 disposition ask on §3
signatures). No BLOCKs. The spec is implementable AS-IS with v0.2
incorporating disposition responses on the four flags.

The orchestrator may proceed to (a) await MQ's Wave-1 independently,
(b) merge both verdicts under Delphi-independence semantics, and
(c) authorize the writing-plans cycle for
`docs/plans/2026-05-NN-stochastic-fx-variant.md` once both Wave-1
verdicts are ACCEPT or ACCEPT_WITH_FLAGS-disposed.
