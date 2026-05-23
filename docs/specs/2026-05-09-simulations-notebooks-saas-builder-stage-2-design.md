# Simulations Notebooks — SaaS-Builder Stage-2 (Math × Code Anchor) — Design

**Iteration**: SaaS-Builder (Y, M, X) Stage-2 — post-cycle anchor artifact
**Branch**: `iter/saas-builder-stage-2`
**Date**: 2026-05-09
**Status**: DESIGN v0.3 (Wave-1 RC+MQ ACCEPT_WITH_FLAGS; v0.3 patches resolve 1 BLOCK + 8 FLAGs)
**Version**: v0.3 (RC BLOCK-1 + RC FLAGs 1–3 + MQ FLAGs F2–F6 resolved; F1+RC-BLOCK-1 are the same defect, dedup'd; F3+RC-FLAG-3 are the same defect, dedup'd)
**Audience**: future Stage-3 implementer; supervisor / advisor review;
contributor onboarding into the `simulations/` package

---

## 1. Purpose

Author a notebook trio under `simulations/notebooks/saas_builder_stage_2/`
that pairs the math anchors of `notes/STAGE_2_RESULTS.md` (R1–R8) against
the actual Phase 2 simulation code committed under
`simulations/saas_builder/`. Each R-tag becomes a HALT-checkpoint trio
(why-markdown / code-cell / interpretation-markdown) per
`memory/feedback_notebook_trio_checkpoint.md`. The trio's primary
contract is: **the closed forms documented in STAGE_2_RESULTS.md hold
numerically at the committed artifact values**. If they don't, the
notebook breaks loudly and Stage-3 contributors are forced to update the
math anchor or the artifact in lockstep.

This is not data exploration; the data-EDA tree at
`notebooks/saas_builder_stage_2/` was deliberately empty for this cycle
and remains so. This trio anchors **math against committed simulation
output**, which is why it lives inside the `simulations/` package.

## 2. Location and naming

```
simulations/
├── notebooks/
│   └── saas_builder_stage_2/
│       ├── 01_math_anchors.ipynb
│       ├── 02_cohort_runs.ipynb
│       ├── 03_z_cap_synthesis.ipynb
│       ├── env.py
│       ├── references.bib
│       ├── estimates/         (gitignored; re-emitted JSONs for tamper check)
│       └── figures/           (committed; PDF figures linked from STAGE_2_RESULTS.md)
```

Naming mirrors the canonical trio convention in
`notebooks/dev_ai_cost/`: `01_*.ipynb`, `02_*.ipynb`, `03_*.ipynb`.
`env.py` carries path setup + `np.random.seed(0)` + an
`assert_clean_state()` helper. `references.bib` carries `@PRIMITIVES`,
`@spec_v121`, `@verdict_memo`, `@stage2_results` as citekeys.

## 3. Trio split — R-tag clusters

| Notebook | R-tags | What it loads | Heavy compute? |
|---|---|---|---|
| `01_math_anchors.ipynb` | R1 (σ₀ anchor), R2 (π(t) closed form), R3 (perpetual identity), R4 (24-bracket family enumeration), R5 (C1 marginalization sum-out) | sympy + numpy only; no parquet | No (<30s) |
| `02_cohort_runs.ipynb` | R6 (softplus + M2 tightness), R7 (S_t = (1−λ)^t with λ ~ Beta(4.5, 95.5)) | `gate_verdict.json`, `revenue_form_verdict.json` from `simulations/saas_builder/data/` | No (<30s) |
| `03_z_cap_synthesis.ipynb` | R8 (Z_cap closed form + boxed key result) | `Z_cap_pinned.json`, `_AUDIT.json` | No (<10s) |

The R-tag → notebook mapping is **chosen to keep each notebook
self-contained**: 01 needs only the math primitives, 02 needs C2 + C3
verdicts, 03 needs the C4 emit. No notebook depends on another's
in-memory state.

## 3a. Verify-API sub-package (`simulations/saas_builder/verify/`)

The notebooks do not reach into internal modules directly. Instead, a
purpose-built verify-API surface is added under
`simulations/saas_builder/verify/`, sized exactly for the verify-only
contract of §5. This keeps notebook code cells minimal (math density
stays in WHY/INTERPRETATION markdown), centralizes assertion logic so
it is pytest-able, and gives Stage-3 a stable surface so internal
module restructuring does not break the math anchor.

### 3a.1 Layout (three-tier discipline preserved)

```
simulations/saas_builder/verify/
├── __init__.py     ← explicit __all__: 8 verify_r{1..8}_* + 4 load_*
├── types.py        ← Value tier   — frozen Verdict dataclasses
├── checks.py       ← Callable tier — free pure functions, one per R-tag
└── io.py           ← IO Boundary  — committed-artifact loader + sha256
```

Tier-import discipline (NON-NEGOTIABLE per `simulations/README.md`):
`types.py` imports stdlib + numpy only; `checks.py` imports
`simulations.saas_builder.verify.types` and the relevant
`simulations.modules` callables; `io.py` imports `verify.types` and
performs the only filesystem reads. No tier inversion; no inheritance
beyond `Protocol` / `Exception`.

### 3a.2 Value-tier contract

The verify sub-package introduces only TWO new Value types — the verdict
container and the rollup. **All committed-artifact data classes are
reused from existing `simulations.types`**, not redefined. See §3a.4 for
the reuse contract.

```
# simulations/saas_builder/verify/types.py
@dataclass(frozen=True)
class RTagVerdict:
    r_tag: str                    # "R1" .. "R8"
    passed: bool
    expected: float | None        # closed-form / pinned value
    actual: float | None          # computed-or-loaded value
    residual: float | None        # |expected - actual|, when meaningful
    audit_sha256: str             # trio-level sha256 (NOT Optional — see §3a.4)
    message: str                  # human-readable summary

@dataclass(frozen=True)
class TrioRollup:
    verdicts: tuple[RTagVerdict, ...]   # length 8 in canonical order
    all_passed: bool
    audit_sha256: str             # same trio-level anchor as in each verdict
```

`audit_sha256` is **not Optional** — every verdict, including the
sympy-only verifiers (R1, R2, R3, R4), carries the same trio-level
anchor (per §3a.4 tamper contract). This closes the silent-tamper-gap
on R1–R5 flagged by Wave-1 MQ-F2.

A new `Audit` Value is added to `simulations/types/` (NOT to
`verify/types.py`) to host the existing `_AUDIT.json` schema; this
preserves the global-types-first discipline of `simulations/README.md`
§"Extension model" per Wave-1 RC-BLOCK-1 fix. The reader for
`_AUDIT.json` follows the same `ZCapPinnedReader` pattern already
established in `simulations/utils/json_io.py`.

### 3a.3 Callable-tier contract — one free pure function per R-tag

| Function | Inputs (all pre-loaded; no IO) | Source of truth |
|---|---|---|
| `verify_r1_sigma_0_anchor` | `x_bar, y_bar, eps, expected, tol, audit_sha256` | PRIMITIVES (8); verdict memo §1 σ₀ = 20,000 |
| `verify_r2_kappa_eliminated_in_pi_t` | `audit_sha256` (sympy live; no other input) | `feedback_post_hoc_fit_anti_fishing_pattern` free-symbol audit |
| `verify_r3_perpetual_identity` | `tol, audit_sha256` | Verdict memo §1: residual ≤ 6.31e-9 |
| `verify_r4_bracket_cardinality` | `brackets, audit_sha256` | Index sets in spec v1.2.1 §5.2; cardinality derivation in `notes/STAGE_2_RESULTS.md` §2.4 (R4) |
| `verify_r5_marginalization_match` | `posterior_chain: np.ndarray, tol, audit_sha256` | C1 v0.4 marginalization (memo §6) |
| `verify_r6_softplus_l1_tightness` | `kappa, tol_factor, audit_sha256` | M2 pin: `tightness_l1_deviation < 1e-3·κ` |
| `verify_r7_s_t_pin` | `gate_verdict: CohortGateVerdict, audit_sha256` | spec v1.2.1 §6.1: `S_t = (1-λ)^t`, `λ ~ Beta(4.5, 95.5)` |
| `verify_r8_z_cap_closed_form` | `z_cap_pinned: ZCapPinned, audit_sha256` | Verdict memo §1: 4,687.94 COP/mo, 95% CI [168.17, 14,606.14] |

All eight return `RTagVerdict`. None mutate. **None do filesystem
I/O** — `CommittedArtifactLoader` (§3a.4) produces all loaded inputs
including the posterior chain as a pre-materialized numpy array. The
v0.2 R5 signature `posterior_path` was a tier leak (Callable
performing IO); v0.3 fixes per Wave-1 MQ-F3 + RC-FLAG-3.

R3 renamed from v0.2's `verify_r3_perpetual_identity_residual` to
`verify_r3_perpetual_identity` for naming-pattern consistency with the
other seven verifiers (the residual scalar lives in
`RTagVerdict.residual`, not in the function name) — Wave-1 MQ-F6.

R4 attribution corrected: index sets are in spec §5.2 (lines 383–388);
cardinality derivation (3 × 2 × 2 × 2 = 24) lives in
`notes/STAGE_2_RESULTS.md` §2.4 (R4 tag) — Wave-1 RC-FLAG-1.

### 3a.4 IO-Boundary-tier contract — reuse-existing-Value-types

Per Wave-1 RC-BLOCK-1 fix: the loader returns **existing frozen
Value-tier dataclasses** from `simulations.types`, not invented
TypedDicts. The v0.2 names (`ZCapPinnedDict`, `GateVerdictDict`, …)
were misstatements; they do not exist on disk. The actual existing
Values (verified by RC against the live codebase):

| Loader method | Return type (existing Value) | Defined at |
|---|---|---|
| `load_z_cap_pinned()` | `ZCapPinned` (frozen-dc) | `simulations/types/posterior.py` |
| `load_gate_verdict()` | `CohortGateVerdict` (frozen-dc) | `simulations/types/saas_cohort2_verdict.py` |
| `load_revenue_form_verdict()` | `RevenueFormFit` (frozen-dc) | `simulations/types/saas_cohort3.py` |
| `load_audit()` | `Audit` (frozen-dc) | `simulations/types/saas_cohort1_audit.py` (NEW — see precondition) |
| `load_posterior_chain()` | `np.ndarray` (shape (N_draws, n_params)) | n/a — numpy primitive |

Existing Pydantic-validated readers in `simulations/utils/json_io.py`
(`ZCapPinnedReader` and equivalents) provide the load+validate path;
the loader composes them. No re-export of internal Pydantic models.

**Precondition subtask (Phase 0 of the implementation plan)**: add a
new `Audit` frozen-dataclass to `simulations/types/saas_cohort1_audit.py`
hosting the existing `_AUDIT.json` schema, plus an `AuditReader` in
`simulations/utils/json_io.py` following the `ZCapPinnedReader`
pattern. This is the only cross-tier addition the verify sub-package
requires; it lives in the global types tier per `simulations/README.md`
§"Extension model" (no per-iteration types/), preserving the
global-types-first discipline.

```
# simulations/saas_builder/verify/io.py
class CommittedArtifactLoader:
    def __init__(self, data_root: Path, audit_block_hasher: AuditBlockHasher) -> None: ...
    def load_z_cap_pinned(self) -> ZCapPinned: ...
    def load_gate_verdict(self) -> CohortGateVerdict: ...
    def load_revenue_form_verdict(self) -> RevenueFormFit: ...
    def load_audit(self) -> Audit: ...
    def load_posterior_chain(self) -> np.ndarray: ...
    def trio_audit_sha256(self) -> str: ...   # see tamper contract below
```

### 3a.4.1 Tamper-detection contract (uniform across 8/8 verdicts)

Per Wave-1 MQ-F2 fix: v0.2 left `audit_sha256 = None` for the four
sympy-only verifiers (R1–R4), creating a silent gap. v0.3 closes this:

1. At loader construction, `CommittedArtifactLoader` reads ALL committed
   artifacts (`Z_cap_pinned.json`, `gate_verdict.json`,
   `revenue_form_verdict.json`, `_AUDIT.json`).
2. For each artifact, the loader computes a fresh sha256 over the file
   bytes AND asserts equality with the embedded `audit_block` field
   already present in each JSON. **This is a real tamper check, not
   window-dressing** — Wave-1 RC-FLAG-2 disambiguation. The existing
   `simulations.utils.audit_block.AuditBlockHasher` performs the rehash;
   the loader composes it.
3. The four per-artifact sha256s are concatenated in canonical order
   (alphabetical by filename) and re-hashed to produce a single
   **trio_audit_sha256**.
4. Every `RTagVerdict.audit_sha256` (and `TrioRollup.audit_sha256`) is
   bound to this trio-level anchor — including R1, R2, R3, R4, which
   load nothing. The tamper chain is uniform across 8/8 verdicts.

If any embedded `audit_block` mismatches the recomputed file sha256,
the loader raises `AuditBlockMismatch` at construction time — the
notebook fails before any verifier runs.

### 3a.5 Notebook code-cell shape (post-API)

```python
loader = CommittedArtifactLoader(DATA_ROOT)
v = verify_r8_z_cap_closed_form(z_cap_pinned=loader.load_z_cap_pinned())
assert v.passed, v.message
print(f"{v.r_tag}: Z_cap = {v.actual:,.2f} COP/mo  "
      f"(residual {v.residual:.2e}; audit {v.audit_sha256[:8]}…)")
```

### 3a.6 pytest coverage (mandatory)

`simulations/tests/test_verify.py` exercises each verifier with the
per-R-tag negative cases enumerated below (per Wave-1 MQ-F5: do not
leave negative cases to plan-author discretion). ≥ 20 test cases
total (≥ 2 per verifier; several R-tags require 3+).

| R-tag | Happy path | Negative cases (mandatory) |
|---|---|---|
| R1 | committed σ₀ = 20,000 within tol | (a) ε perturbed by 10× tol → fail |
| R2 | sympy π(t) free of κ | (a) inject `1/κ + π(t)` → fail; **precondition assertion** that `sympy.simplify(injected).free_symbols` is non-empty before invoking the verifier (Wave-1 MQ-F4 — guards against `1/κ - 1/κ` cancellation false-pass) |
| R3 | residual ≤ 6.31e-9 | (a) tol tightened by 100× → fail |
| R4 | brackets length 24, factorization 3×2×2×2 | (a) length 23 → fail; (b) length 25 → fail; (c) length 24 but factorization 4×2×3×1 → fail (Wave-1 MQ-F5 — verifier must check factorization, not just cardinality) |
| R5 | empirical = analytic within tol | (a) tol tightened 1000× → fail; (b) chain shape mis-match → fail |
| R6 | softplus L¹ deviation < 1e-3·κ | (a) injected `tightness_l1_deviation = 1e-2·κ` (10× M2 pin) → fail (Wave-1 MQ-F5) |
| R7 | exact `Beta(4.5, 95.5)` and `(1-λ)^t` tokens | (a) near-miss `Beta(4, 96)` → fail; (b) `S_t = (1-λ)^(t-1)` → fail (Wave-1 MQ-F5 — string equality alone is too brittle for HALT-on-flip semantics) |
| R8 | Z_cap = 4687.94, CI lower > 0 | (a) Z_cap perturbed by 1% → fail; (b) CI lower set to −1 → fail |

Total: 20 test cases (8 happy + 12 negative). Plus 1 cross-cutting test
that injects an `audit_block` mismatch into one of the four committed
JSONs and asserts `CommittedArtifactLoader.__init__` raises
`AuditBlockMismatch`. Grand total ≥ 21.

### 3a.7 Cost

~250–350 LOC across 4 new files; ~16 new pytest cases. Adds one phase
to the implementation plan (verify-API authoring) before notebook
authoring. Net positive: math cells stay thin and Stage-3 churn cannot
break the math anchor.

## 4. Section API per R-tag (the math×code pairing pattern)

Each R-tag produces one trio (one HALT-checkpoint):

```
## §N — Rk: <name>            ← header verbatim from STAGE_2_RESULTS.md §N

### Decision-citation block    ← 4-part per
                                  feedback_notebook_citation_block.md:
                                  reference / why / relevance / connection

### WHY (markdown)             ← LaTeX equation copied verbatim from
                                  STAGE_2_RESULTS.md; predecessor lineage
                                  cited (e.g. PRIMITIVES (8), spec §6.1)

### CODE (cell)                ← imports from simulations.{types, modules,
                                  utils, saas_builder}; loads the committed
                                  artifact OR derives via sympy; asserts the
                                  closed form holds; prints the key value

### INTERPRETATION (markdown)  ← what the assertion proved; numeric residual;
                                  link back to artifact audit_block sha256;
                                  HALT-checkpoint if drift detected
```

R-tag → assertion contract:

| R | Verifier function (§3a.3) | Code-cell asserts |
|---|---|---|
| R1 | `verify_r1_sigma_0_anchor` | `σ₀ = (X̄/Ȳ)²·ε²/8` numerically; expected σ₀ = 20,000 (per verdict memo §1) within tolerance |
| R2 | `verify_r2_kappa_eliminated_in_pi_t` | `κ ∉ free_symbols(π(t))` (sympy free-symbol audit — anti-fishing live demo); π(t) reduces to the boxed (4ωt cos − sin) form |
| R3 | `verify_r3_perpetual_identity` | Perpetual identity `Δ^{(a_s)}_∞ = lim_{t→∞} Δ^{(a_s)}_t` residual ≤ 1e-8 (memo §1: 6.31×10⁻⁹) |
| R4 | `verify_r4_bracket_cardinality` | `len(brackets) == 24` AND factorization `3 tiers × 2 α × 2 cache × 2 κ` (index sets per spec §5.2; cardinality derivation per `notes/STAGE_2_RESULTS.md` §2.4) |
| R5 | `verify_r5_marginalization_match` | Marginalization sum-out: empirical posterior mean from saved chain trace matches analytic marginal at the same nodes (Phase 2 N_draws ≥ 712k) |
| R6 | `verify_r6_softplus_l1_tightness` | softplus L¹ deviation < 1e-3·κ on [0, 2κ] (M2 pin); load `revenue_form_verdict.json` and re-derive |
| R7 | `verify_r7_s_t_pin` | `gate_verdict.json` contains `lambda_prior: Beta(4.5, 95.5)` and `S_t_form: "(1-lambda)^t"`; HALT-on-flip token unchanged |
| R8 | `verify_r8_z_cap_closed_form` | `Z_cap_pinned.json::Z_cap == 4687.94` (within parquet tolerance); 95% CI lower bound > 0 |

## 5. Code-playback discipline (NON-NEGOTIABLE)

**Verify-only.** Notebooks never re-run PyMC. They load committed
artifacts under `simulations/saas_builder/data/` and verify the closed
forms at those committed values. Per user decision (Question 1, locked):

> *Notebooks load committed JSON/parquet under
> simulations/saas_builder/data/ and verify each R-tag closed form holds
> numerically. No PyMC, no re-fit. Fast (<60s total), deterministic,
> doubles as tamper detector. Stage-3 contributors break the notebook if
> they change upstream artifacts.*

Consequences:

- Total notebook runtime is bounded at < 60s wall-clock.
- Determinism: any failure is a real artifact drift, not an RNG flake.
- The notebook is **part of the audit chain** — running it is a
  tamper-check on `Z_cap_pinned.json`'s `audit_block` sha256.
- Stage-3 implementers who change upstream parquet must update the
  notebook assertions in the same commit.

There is no opt-in re-execute mode. If a Stage-3 contributor needs the
slow path, they invoke `scripts/run_cohort{1..4}_emit.py` directly.

## 6. Inherited conventions from `notebooks/dev_ai_cost/`

- `env.py` does the `sys.path` setup so `from simulations.types import …`
  works from a notebook kernel; sets `np.random.seed(0)` for any local
  numerical sanity checks; defines `assert_audit_block_sha256(path,
  expected_tail)` to centralize the tamper-check pattern.
- `references.bib` provides citekeys consumed via the `[@…]` markdown
  pattern in WHY cells.
- `estimates/` is gitignored; running the notebook re-emits a small
  JSON sidecar for tamper diff against the committed artifact (helpful
  during Stage-3 churn).
- `figures/` is committed; the trio produces three reference plots that
  Stage-3 docs may reference: π(t) curve over t ∈ [0, 24] months, S_t
  survival under the Beta(4.5, 95.5) prior, σ₀ posterior overlay.

## 7. Anti-fishing posture

- The C4 1/κ case study from the cycle is shown live in
  `01_math_anchors.ipynb` §2 (R2): a sympy free-symbol audit
  (`assert κ not in pi_t.free_symbols`) runs as the first cell after
  the WHY markdown, mirroring the detection heuristic from
  `memory/feedback_post_hoc_fit_anti_fishing_pattern.md`.
- The HALT-on-flip semantic from R7 is preserved: 02 asserts the
  Beta(4.5, 95.5) prior token verbatim from `gate_verdict.json`.
- No magnitude-promise language anywhere in the trio. Verbiage matches
  STAGE_2_RESULTS.md §3 (TODO-COHORT-N closure semantics: DEFERRED /
  CLOSED / INDISTINGUISHABLE).
- Anti-fishing invariants (`N_MIN`, `POWER_MIN`, `MDES_SD`) are not
  re-validated here — that's the verdict memo's job. The trio
  assertions are at the closed-form-identity level, not the gate level.

## 8. Out of scope (deferred / Stage-3)

- Re-execution of cohort drivers — explicitly excluded per §5.
- Real-data conditioning — Stage-3 milestone.
- Hierarchical pooling for C3, Weibull k≠1 falsification, per-tier θ_k
  differentiation — Stage-3 work; the trio anchors the synthetic
  Stage-2 baseline only.
- Panoptic-deployment math (PRIMITIVES §11 discrete-strip replication) —
  out of scope for this artifact.

## 9. Success criteria

- [ ] Three notebooks executable headless with `make notebooks` (or
      `jupyter nbconvert --to notebook --execute`); total wall < 60s.
- [ ] Every R-tag (R1–R8) appears as exactly one trio with the §4 four-cell
      pattern.
- [ ] Each R-tag code cell contains at least one `assert` against a
      committed artifact value or sympy identity.
- [ ] `01_math_anchors.ipynb` §2 contains the explicit
      `κ ∉ free_symbols(π(t))` cell (anti-fishing live demo).
- [ ] `references.bib` resolves all `[@…]` citekeys used in WHY cells.
- [ ] No PyMC import anywhere in the notebook directory.
- [ ] Adding the trio does not change `make verify` semantics (it's
      audit-additive, not gate-altering).
- [ ] `simulations/saas_builder/verify/` sub-package exists with the
      §3a layout; `__init__.py` declares `__all__` explicitly.
- [ ] `simulations/tests/test_verify.py` covers every R-tag per the
      §3a.6 negative-case table (≥ 20 cases + 1 audit-block-mismatch
      cross-cutting test = ≥ 21 total).
- [ ] `simulations/types/saas_cohort1_audit.py` adds the `Audit`
      frozen-dataclass; `simulations/utils/json_io.py` adds an
      `AuditReader` following the `ZCapPinnedReader` pattern
      (Phase 0 precondition).
- [ ] `CommittedArtifactLoader.__init__` rehashes every committed JSON
      and asserts equality with each artifact's embedded `audit_block`
      field; raises `AuditBlockMismatch` on drift.
- [ ] Every `RTagVerdict.audit_sha256` (including R1–R4 sympy-only)
      carries the trio-level anchor; the field is non-Optional.
- [ ] Notebook code cells contain no direct parquet/JSON file reads
      (all I/O routes through `CommittedArtifactLoader`).
- [ ] Notebook code cells import only from
      `simulations.saas_builder.verify` and `env.py` — no reach into
      `simulations.modules` / `simulations.utils` internals.

## 10. Open items (for the implementation plan to resolve)

- `make notebooks` target update — does it need a new sub-target for
  `simulations/notebooks/`, or is the existing top-level glob
  sufficient? Plan to verify against the current Makefile during
  Phase 0.
- `references.bib` content — author-year citekeys to be drawn from the
  closest existing `.bib` (likely `notebooks/dev_ai_cost/references.bib`)
  with three additions for PRIMITIVES, spec, verdict memo, and
  STAGE_2_RESULTS.
- Figure generation cell placement — figures live in INTERPRETATION
  cells (per existing trio convention) or as a §"Figures" appendix per
  notebook? Plan to inspect `notebooks/dev_ai_cost/03_*.ipynb` and
  match.

## 11. Cross-references

- `notes/STAGE_2_RESULTS.md` — the math anchor this trio plays code
  against (R1–R8).
- `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md` — the
  cycle's canonical deliverable; trio assertions check the memo's
  numeric pins.
- `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (spec
  v1.2.1) — §5.2 parameter family enumerated by R4; §6.1 S_t pin
  asserted by R7.
- `simulations/README.md` — user manual section already documents
  reproducibility; the trio is the executable counterpart to that
  narrative.
- `memory/feedback_notebook_trio_checkpoint.md`,
  `memory/feedback_notebook_citation_block.md`,
  `memory/feedback_post_hoc_fit_anti_fishing_pattern.md` — convention
  sources.

---

## CORRECTIONS-α — v0.2 → v0.3

**Trigger.** Wave-1 independent verify dispatched 2026-05-09 to scratch
`scratch/2026-05-09-notebooks-trio-design-review/`. RC verdict
ACCEPT_WITH_FLAGS (1 BLOCK + 3 FLAGs); MQ verdict ACCEPT_WITH_FLAGS
(0 BLOCKs + 6 FLAGs). RC-BLOCK-1 ≡ MQ-F1 (TypedDict misstatement);
RC-FLAG-3 ≡ MQ-F3 (R5 tier leak). 8 distinct fixes after dedup.

**Patches (each cited to its origin verdict line)**:

1. **§3a.2 + §3a.4 — TypedDict→Value reuse** (RC-BLOCK-1, MQ-F1; rc-verdict
   L34, L37–70; mq-verdict L163–195). The four invented `*Dict` TypedDicts
   are removed; loader returns existing frozen Values from
   `simulations.types`: `ZCapPinned`, `CohortGateVerdict`, `RevenueFormFit`.
   New `Audit` Value added to `simulations/types/saas_cohort1_audit.py`
   (Phase 0 precondition); not to `verify/types.py`. Preserves
   global-types-first discipline.
2. **§3a.4.1 — Uniform tamper-detection contract** (MQ-F2; mq-verdict
   L79–96, L217–223). Loader computes a single `trio_audit_sha256`
   spanning all four committed JSONs and threads it into every
   `RTagVerdict.audit_sha256`. Field becomes non-Optional. Closes the
   silent-gap on R1–R4 (sympy-only, formerly `None`).
3. **§3a.4 + §3a.3 — R5 tier leak fixed** (RC-FLAG-3, MQ-F3; rc-verdict
   L96–105; mq-verdict L225–229). `verify_r5_marginalization_match` now
   accepts `posterior_chain: np.ndarray`, not a path. Load moves to
   `CommittedArtifactLoader.load_posterior_chain()`. Three-tier
   discipline restored.
4. **§3a.6 — R2 simplification guard** (MQ-F4; mq-verdict L231–235). The
   1/κ regression test must precondition-assert
   `sympy.simplify(injected).free_symbols` is non-empty to prevent
   `1/κ - 1/κ + π(t)` cancellation false-pass.
5. **§3a.6 — Per-R-tag negative cases enumerated** (MQ-F5; mq-verdict
   L237–241). Negative cases for R4 (cardinality + factorization),
   R6 (wide tightness 1e-2·κ), R7 (near-miss prior, off-by-one
   exponent). Test floor 16 → 20.
6. **§3a.3 + §4 — R3 renamed** (MQ-F6; mq-verdict L243–246).
   `verify_r3_perpetual_identity_residual` → `verify_r3_perpetual_identity`.
7. **§3a.3 + §4 — R4 attribution corrected** (RC-FLAG-1; rc-verdict
   L33, L74–81). "Matches spec §5.2 verbatim" replaced with "index sets
   per spec §5.2; cardinality derivation per STAGE_2_RESULTS.md §2.4".
8. **§3a.4.1 — `audit_sha256` source-of-truth pinned** (RC-FLAG-2;
   rc-verdict L83–94). Loader REHASHES each file and ASSERTS equality
   with the embedded `audit_block`, citing
   `simulations.utils.audit_block.AuditBlockHasher`. Real check, not
   surface-and-display.

**Posture.** Strictly tightening on every axis: tamper chain becomes
uniform (8/8 verdicts anchored, was 4/8); tier discipline restored
(R5 leak closed); naming consistent (R3 verbiage); negative-case
floor raised (16 → 20+1); type reuse aligned with reality (no
invented dicts); audit chain becomes a real check (rehash+assert,
not surface). No upstream pin relaxed. No new claim. R1–R8 set
unchanged.

**Anti-fishing impact.** Strictly stronger across the board.
Per-R-tag negative-case enumeration prevents the C4-class defect
(post-hoc fit in any R-tag, not just R2) from slipping past pytest.
The R2 simplification precondition closes a subtle false-pass
vector. The uniform tamper anchor means a Stage-3 contributor cannot
silently mutate sympy primitives without breaking the trio.

---

## CORRECTIONS-α — v0.1 → v0.2

**Trigger.** User question 2026-05-09: *"Do we need to define [an] API to
abstract away implementation on the modules?"* The v0.1 design had
notebooks reaching directly into `simulations.types` /
`simulations.modules` / raw committed JSON. This created three problems:
(i) Stage-3 internal renames would break notebooks needlessly; (ii)
assertion logic scattered across notebook cells could not be
pytest-tested; (iii) the verify-only contract was implicit rather than
named.

**Patch.** Added §3a — a purpose-built `simulations/saas_builder/verify/`
sub-package with three-tier discipline preserved (Value `types.py` /
Callable `checks.py` / IO Boundary `io.py`), 8 free-pure-function
verifiers (one per R-tag), a `CommittedArtifactLoader` IO class, and a
mandatory `simulations/tests/test_verify.py` with ≥ 16 cases. §4 R-tag
table now references the verifier functions. §9 success criteria gained
4 new bullets covering the verify-API surface.

**Posture.** Strictly tightening: the verify-API is a *named* contract
where v0.1 had implicit cell-scope conventions. Math content unchanged.
R1–R8 set unchanged. Verify-only mode unchanged. No upstream pin
relaxed.

**Anti-fishing impact.** R2's `κ ∉ free_symbols(π(t))` check moves from
"a notebook cell" to "a pytest case in `test_verify.py`" — the C4 1/κ
detection is now part of CI, not just a notebook-execution-time check.
Strictly stronger.

End of design (v0.3).

