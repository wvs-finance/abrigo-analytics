---
artifact_kind: independent_reality_check_verdict
auditor: Reality Checker (main-session-dispatched, independent)
emit_timestamp_utc: 2026-05-08
target_artifact: docs/specs/2026-05-09-simulations-notebooks-saas-builder-stage-2-design.md (v0.2)
default_verdict: REJECT
---

# RC Wave-1 Verdict — Notebooks Trio Design v0.2

## Verdict: ACCEPT_WITH_FLAGS

The design's math anchoring (R1–R8 mapping, numeric pins, R-tag clusters)
checks out cleanly against the underlying artifacts. The verify-API
sub-package proposal is structurally sound. However, §3a.4 contains a
material misstatement about the type-machinery being reused (claims
TypedDict reuse from `json_io`, where the actual existing surface is
frozen-dataclass Values + Protocols), which will mislead the
implementation plan if it is not corrected before writing-plans hand-off.
Two additional FLAGs are non-blocking but worth fixing.

## Per-claim audit table

| # | Claim (design §) | Verification | Status |
|---|---|---|---|
| 1 | Trio split: R1–R5 in 01, R6–R7 in 02, R8 in 03 (§3) | `notes/STAGE_2_RESULTS.md` §2.1–2.5 carry tags R1–R5; §3.2 carries R6 (line 163); §3.3 carries R7 (line 180); §4 carries R8 (line 204). Mapping is consistent. | PASS |
| 2 | Committed artifacts `Z_cap_pinned.json`, `gate_verdict.json`, `revenue_form_verdict.json`, `_AUDIT.json` exist under `simulations/saas_builder/data/` | `ls simulations/saas_builder/data/` shows all four present (plus `Z_cap_pinned.SIGN_VERDICTS.md`, `cohort_prior.parquet`, etc.). | PASS |
| 3 | `notebooks/dev_ai_cost/env.py` and `references.bib` exist with author-year citekeys | `env.py` opens with parents-fix path resolution + repo-rooted constants pattern; `references.bib` uses author-year keys (e.g. `baumolBowen1966performingArts`). Convention claim accurate. | PASS |
| 4 | Verify-API §3a layout consistent with three-tier discipline in `simulations/README.md` | README §"Three-tier discipline" pins Value/Callable/IO Boundary import directions; design §3a.1 import rules match (types→stdlib+numpy; checks→types+modules; io→types+filesystem). | PASS |
| 5 | R8 numeric pins: `Z_cap = 4687.94`, 95% CI [168.17, 14606.14] match verdict memo §1 | `Z_cap_pinned.json` reads `Z_cop_per_month = 4687.942347178384`, `ci_95_lo = 168.172482700353`, `ci_95_hi = 14606.142570117216` (TP1–TP3 baseline). Verdict memo §4.4 row TP1 confirms the same. | PASS |
| 6 | R3 residual ≤ 6.31e-9 matches memo §1 | `Z_cap_pinned.json::sign_verdicts[*].identity_residual = 6.307049068335715e-09`; memo §4.4 reports 6.31×10⁻⁹. | PASS |
| 7 | R7 claim: `λ ~ Beta(4.5, 95.5)`, `S_t = (1-λ)^t` matches spec v1.2.1 §6.1 | Spec lines 405–442: `S_t = (1 - λ)^t`, `λ ~ Beta(α_S = 4.5, β_S = 95.5)`. Exact match. | PASS |
| 8 | R4 cardinality `3 × 2 × 2 × 2 = 24` attributed to spec v1.2.1 §5.2 | Spec §5.2 (lines 262–388) does NOT contain the explicit Cartesian-product formula. The cardinality formula and the `B_24 = {tier} × {α_arm} × {h_cache} × {κ_arm}` enumeration appear in `notes/STAGE_2_RESULTS.md` §2.4 (R4 derivation), which itself cites "spec §5.2 lines 383–388". The four index sets are individually defined in spec §5.2, but the product expansion is derivative. The design line "matches spec §5.2 verbatim" is overstated — `verbatim` is incorrect; the correct attribution is "matches the index sets enumerated in spec §5.2; explicit cardinality derivation appears in STAGE_2_RESULTS.md §2.4 (R4)". | FLAG-1 |
| 9 | TypedDict reuse §3a.4: schemas come from `simulations.utils.parquet_io` / `simulations.utils.json_io` | `parquet_io.py` exposes TypedDicts `CohortPriorRow` and `SyntheticTauRow` (lines 97, 108) — partial truth. `json_io.py` exposes ZERO TypedDicts; it returns the frozen-dataclass Value `ZCapPinned` (defined in `simulations/types/posterior.py`) via Pydantic transient validation. The design's named types `ZCapPinnedDict`, `GateVerdictDict`, `RevenueFormVerdictDict`, `AuditDict` do NOT exist anywhere in the codebase. The actual existing Value-tier types the loader should return are `ZCapPinned`, `CohortGateVerdict`, `RevenueFormFit`, plus a (currently absent) Audit Value. This is a material misstatement of the existing surface. | BLOCK-1 |
| 10 | CORRECTIONS-α v0.1 → v0.2 accurately characterizes the patch | The correction states "added §3a, three-tier discipline preserved, 8 verifiers, CommittedArtifactLoader, ≥16 pytest cases, §4 R-tag table now references verifier functions, §9 gained 4 new bullets". §3a is present and structured per the description; §4 R-tag table column 2 is now "Verifier function (§3a.3)"; §9 bullet count gained four new entries (verify/ sub-package, test_verify, no direct file reads, import-only-from-verify). All four checks pass. The "anti-fishing impact" claim that R2's κ-elimination check moves to pytest is consistent with §3a.6. | PASS |

## BLOCKs (must-fix before plan dispatch)

1. **§3a.4 — TypedDict reuse claim is wrong.** The text "the TypedDict
   row schemas are reused from `simulations.utils.parquet_io` /
   `simulations.utils.json_io` per Phase 2 M4 pin — no schema
   duplication" misrepresents the existing infrastructure. Reality:
   - `parquet_io.py` exposes `CohortPriorRow`, `SyntheticTauRow`
     (TypedDicts, correct).
   - `json_io.py` exposes the frozen-dataclass Value `ZCapPinned`
     (NOT a TypedDict). Pydantic is used transiently and never
     re-exported.
   - There are no existing types named `ZCapPinnedDict`,
     `GateVerdictDict`, `RevenueFormVerdictDict`, or `AuditDict`.
   - Existing Value types that the loader should return are
     `simulations.types.posterior.ZCapPinned`,
     `simulations.types.saas_cohort2_verdict.CohortGateVerdict` (per
     `test_saas_cohort2.py:72`), and
     `simulations.types.saas_cohort3.RevenueFormFit` (per
     `test_saas_cohort3.py:76`). No `Audit` Value exists yet — one
     must be added under `simulations/types/` (Value tier), NOT under
     `verify/types.py`, to preserve the global-types-first discipline
     of `simulations/README.md` §"Extension model".

   Fix before plan dispatch: rewrite §3a.4 to (a) name the actual
   Value classes, not invented `*Dict` typed-dicts; (b) call out that
   `verify.io.CommittedArtifactLoader` returns the existing global
   Value types via existing `ZCapPinnedReader` / equivalent gate
   readers; (c) flag the missing `Audit` Value as a precondition
   subtask (add to `simulations/types/`, not to `verify/types.py`).

   This BLOCK is upstream of the entire writing-plans phase: the
   plan would otherwise authorize creation of duplicate `*Dict`
   TypedDicts inside the verify sub-package, violating the
   no-schema-duplication invariant the design itself states.

## FLAGs (non-blocking, recommend addressing)

1. **§4 R4 attribution overreach.** Code-cell entry for R4 says
   "matches spec §5.2 verbatim". Spec §5.2 enumerates the four index
   sets but does not state the Cartesian product or compute
   `|B_24| = 24`. The verbatim cardinality derivation lives in
   `notes/STAGE_2_RESULTS.md` §2.4 (R4 tag). Recommend amending the
   §4 R4 row to: "matches the four index sets in spec §5.2 (lines
   383–388); cardinality derivation per STAGE_2_RESULTS.md §2.4
   (R4)". Same edit applies to §3a.3's R4 row attribution.

2. **§3a.4 audit_sha256 source-of-truth ambiguity.** Design says
   "`audit_sha256` is computed once at load time and threaded
   through every `RTagVerdict.audit_sha256`." But each committed
   artifact already carries its own `audit_block` field (verified:
   `Z_cap_pinned.json::audit_block`, `gate_verdict.json::audit_block`,
   `_AUDIT.json::audit_block`). Recommend clarifying whether the
   loader (a) re-hashes the file and asserts equality with the
   embedded `audit_block`, or (b) merely surfaces the embedded
   value. (a) is the actual tamper check; (b) is window-dressing.
   Without disambiguation the implementation plan will guess. The
   `simulations.utils.audit_block.AuditBlockHasher` exists for case
   (a) and should be cited explicitly.

3. **§9 success criterion "no direct parquet/JSON file reads".** The
   bullet "Notebook code cells contain no direct parquet/JSON file
   reads (all I/O routes through `CommittedArtifactLoader`)" is good
   discipline, but `cohort_prior.parquet` and the
   `synthetic_tau_t/` partition are also under `data/` and the loader
   API in §3a.4 covers only the four JSON artifacts. If R5
   (marginalization) actually consumes the synthetic-τ chain, the
   loader needs a fifth method or R5 must be re-scoped to
   sympy-only. Recommend the writing-plans phase resolve this open
   item (currently unmentioned in §10 open items).

## Evidence summary

```
$ ls simulations/saas_builder/data/
Z_cap_pinned.SIGN_VERDICTS.md   PRIMARY_RESULTS.md          gate_verdict.json
Z_cap_pinned.json               ROBUSTNESS_RESULTS.md       revenue_form_verdict.json
_AUDIT.json                     cohort_prior.parquet        synthetic_tau_t
estimates_cohort_3              # → all four named JSONs present

$ jq '.Z_cop_per_month, .ci_95_lo, .ci_95_hi, .sign_verdicts[0].identity_residual' \
     simulations/saas_builder/data/Z_cap_pinned.json
4687.942347178384
168.172482700353
14606.142570117216
6.307049068335715e-09          # → R8 + R3 pins confirmed

$ grep -nE "tag\{R[1-8]" notes/STAGE_2_RESULTS.md
52:\tag{R1}    | §2.1 σ₀ anchor
74:\tag{R2}    | §2.2 π(t) closed form
97:\tag{R3}    | §2.3 Perpetual identity
111:\tag{R4}   | §2.4 24-bracket family
127:\tag{R5}   | §2.5 C1 marginalization
163:\tag{R6}   | §3.2 sticky-cost (CLOSED)
180:\tag{R7}   | §3.3 Υ_t (INDISTINGUISHABLE)
204:\tag{R8}   | §4 Z_cap pinned                # → R-tag location map matches §3 trio split

$ grep -n "S_t \\\\;=\\\\;\\|Beta(\\\\alpha_S" docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md
407: S_t \;=\; (1 - \lambda)^t, \qquad \lambda \sim \mathrm{Beta}(\alpha_S, \beta_S)
438: \lambda \sim \mathrm{Beta}(\alpha_S = 4.5,\; \beta_S = 95.5)
                                  # → R7 pin matches verbatim

$ grep -n "TypedDict\|class .*Dict" simulations/utils/parquet_io.py simulations/utils/json_io.py
parquet_io.py:22: from typing import Final, TypedDict
parquet_io.py:97: class CohortPriorRow(TypedDict):
parquet_io.py:108: class SyntheticTauRow(TypedDict):
json_io.py:                # → ZERO matches; json_io exposes ZCapPinned (frozen-dc),
                           #   not any TypedDict. BLOCK-1 confirmed.

$ grep -nE "ZCapPinned|CohortGateVerdict|RevenueFormFit" simulations/types/posterior.py | head -3
12:- ``ZCapPinned`` — emission Value for ``estimates/Z_cap_pinned.json``
264: class ZCapPinned:
                       # → existing Value type names that the verify
                       #   sub-package should reuse, not invent `*Dict` aliases for.

$ sed -n '262p;383,388p' docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md
### §5.2 Parameter brackets — LOCKED v1.1
| $\text{tier}_i$ | Categorical(...) per builder | §5.1, §5.2 | Dirichlet bracket |
| $\bar p_{\text{sub}}$ | Discrete RV indexed by tier_i: {20, 100, 200} | §5.2 | post-doubling κ arm |
| $q_t^{\text{sticky}}$ | (T2) softplus-regularized overage | §5.1 | β→∞ asymptotic |
| $N_j$ (turns/day) | NegBin(r, p) | §5.1, §5.2 | ZINB; over-disp Poisson |
| $\tau_{j,i}$ | TruncPareto(α, x_m, κ), α ∈ [1.5, 2.5] | §5.1, §5.2 | ... |
                       # → No "3 × 2 × 2 × 2 = 24" formula present in spec §5.2;
                       #   FLAG-1 confirmed.
```

---

**Recommendation to orchestrator.** Verdict ACCEPT_WITH_FLAGS contingent
on resolving BLOCK-1 (rewrite §3a.4 to name actual existing Value types
and add an `Audit` Value precondition). Once BLOCK-1 is patched in a
v0.3, the design is cleared for writing-plans hand-off; FLAG-1, FLAG-2,
FLAG-3 can be folded into the same v0.3 patch or carried into the
implementation plan as Phase-0 tasks.
