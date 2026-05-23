# Phase 6.5 — E10 GSPS Closure Code Review

**Reviewer role:** Code Reviewer (parallel with Reality Checker).
**Scope:** Per plan task 6.5 — code quality only. Does NOT review data
provenance / posture / fantasy (Reality Checker's lane).
**Branch:** `iter/e10-gsps-2026-05-20` @ `8e7892a` + uncommitted LaTeX
export, verdict memo, and figures.
**Date:** 2026-05-23.

---

## Top-line verdict — **APPROVED_WITH_NITS**

Substantive code quality is excellent. Three-tier discipline is clean,
the functional-python contract holds, the firewall is robust (verified
adversarially), determinism is in place, and the LaTeX export is
numerically consistent with the diagnostic JSONs end-to-end. The full
test suite is **223 passed / 6 failed (97.4%)**; the 6 failures are
all integration-tier anti-fishing notebook-banner checks driven by a
single root cause (canonical-string drift between spec v0.4 and v0.7),
not by a defect in the code under review. Two minor regressions vs prior
reviews are documented below (no Critical findings).

The Delphi final-audit verification matrix invoked only
`tests/unit/` (152/152). The integration-tier failures are a Phase 6
verification-scope gap, not new code defects. They are mechanical to
fix (string update in one module) and the merge can proceed either way
— see Important-1 below for the recommendation.

---

## Findings

### Critical

**None.**

### Important

#### I-1 — Integration tests: anti-fishing notebook-banner compliance fails on notebooks 03 / 04 / 05

- **Where.** `simulations/e10_gsps/tests/integration/test_anti_fishing_compliance.py`
  failures (6/6):
  - `test_analysis_notebook_carries_descriptive_posture_banner[03|04|05]`
  - `test_analysis_notebook_carries_pre_pin_locked_block[03|04|05]`
- **Root cause.** The canonical anti-fishing literals are pinned to
  spec v0.4 wording in `simulations/e10_gsps/modules/anti_fishing_checks.py`:
  - `PRE_PIN_LOCKED_MARKER` requires `"E10 v0.4 PRE-PIN LOCKED (spec v0.4 §7) — …"`
    (literal, em-dash).
  - `DESCRIPTIVE_POSTURE_BANNER` requires `"DESCRIPTIVE POSTURE — E10 GSPS v0.4
    is a descriptive / illustrative iteration. …"` (literal, em-dash).
  Notebooks 03 / 04 / 05 were authored against spec **v0.7** and use the
  newer "CALIBRATION-CONDITIONAL DESCRIPTIVE" banner and a v0.7-tagged
  PRE-PIN marker, with ASCII dashes; notebooks 01 / 02 still carry the
  v0.4 literals verbatim.
- **Impact.** Test failure only — no runtime defect. Verdict, surface,
  numerics, classifier, firewall, identity residual, determinism all
  unaffected.
- **Why the autofix wave didn't catch it.** `Phase6_Delphi_final_audit.md`
  verification matrix and `Phase6_Delphi_autofix_verification.md` both ran
  `uv run pytest simulations/e10_gsps/tests/unit/` (152/152 PASS) and did
  not invoke `tests/integration/`. The propagation map lists
  `tests/integration/test_anti_fishing_compliance.py` only as an
  indirect consumer of Fix 3, no fix targets it.
- **Recommended fix (≤30 min).** Either (a) update the two canonical
  strings in `anti_fishing_checks.py` to the v0.7 wording, then update
  notebooks 01 and 02 + `_TEMPLATE.ipynb` to match (preferred — keeps
  spec/code/notebook aligned), or (b) add the v0.4 canonical strings as
  additional markdown lines at the top of notebooks 03/04/05 alongside
  the v0.7 banner. Path (a) is cleaner; path (b) preserves the spec v0.7
  banner content but adds redundancy.
- **Merge-block recommendation.** Treat as a fix-before-merge nit since
  the test failure is real and the canonical-literal version drift is a
  durable hazard (any future iteration cohort review will hit the same
  failure). Estimated effort is sub-30-minutes.

### Minor

#### M-1 — `DATA_PROVENANCE.md` spec-basis line is stale

- **Where.** `simulations/e10_gsps/DATA_PROVENANCE.md:4` reads
  `**Spec basis:** docs/specs/2026-05-20-e10-gsps-v0.6-convex-multicurrency-design.md (v0.6).`
- **Impact.** The verdict memo, methods-paper export, and plan task
  references all point to **v0.7**. Auditor following the provenance
  trail sees an out-of-date pointer.
- **Fix.** One-line update to `v0.7-convex-multicurrency-design.md (v0.7)`.

#### M-2 — `make panels` does not regenerate the E10 panel

- **Where.** `Makefile:45-46` invokes `scripts/build_panels.py` only.
  `scripts/build_e10_gsps_panel.py` exists and is the canonical Tier-3
  E10 builder, but it is not chained from `make panels` and
  `scripts/build_panels.py` contains no references to E10 / `e10_gsps`.
- **Impact.** A fresh checkout running `make panels` will NOT
  re-derive the E10 panel parquet; the cloner must know to invoke
  `python scripts/build_e10_gsps_panel.py` separately. Tier-3 round-trip
  verification (`make verify`) is therefore not E10-aware either.
- **Fix.** Either (a) extend `scripts/build_panels.py` to discover &
  call the E10 builder (preferred — central orchestration matches the
  Makefile help text "centralizes the orchestration so a cloner has one
  entry point"), or (b) add an explicit `panels-e10:` Makefile target
  and document it in the help block. Same scope decision applies to
  E4 / E7-A / E8 builds — recommend a follow-up consolidation issue
  rather than blocking this PR.

#### M-3 — `type: ignore[typeddict-item]` in `utils/panel_io.py:217`

- **Where.** `simulations/e10_gsps/utils/panel_io.py:217` —
  `PanelRow(**record)  # type: ignore[typeddict-item]`.
- **Assessment.** Narrowly-scoped, justified suppression: the
  `pyarrow.Table.to_pylist()` returns `list[dict[str, Any]]` which the
  type-checker cannot map onto a TypedDict via `**unpack`. Runtime
  safety is enforced upstream by the explicit
  `if tuple(table.column_names) != PANEL_COLUMNS` schema check at
  line 211. **Acceptable as-is** — no fix required. Logged for
  completeness because the prior reviews report "0 `type: ignore`" and
  this pre-existing one is the singular exception (introduced before
  the autofix wave; not new).

---

## Verification matrix (Code Reviewer)

| Check | Result |
|---|---|
| Three-tier import discipline (types ↛ modules/utils; modules ↛ utils) | **HOLDS** — verified via grep on all 25 source files |
| All result types `@dataclass(frozen=True, slots=True)` | **HOLDS** — 18/18 dataclasses frozen+slots |
| No inheritance except `Protocol` / `Exception` / Enum / TypedDict / utils-tier `class with __init__` exemption | **HOLDS** — `FXSeriesIngest` + `PanelParquetIO` are the two utils-tier exempt classes per CLAUDE.md |
| Full type annotations on production code | **HOLDS** — no unannotated callables found |
| `type: ignore` / `# noqa` / broad `except` in production | 1 pre-existing narrow `type: ignore` (M-3); 0 `# noqa`; 0 broad `except` |
| Unit tests | **152 / 152 PASS** in 3.89s |
| Integration tests | **71 / 77 PASS, 6 FAIL** (all I-1 root cause) |
| Total tests | **223 / 229 PASS** |
| Verdict classifier exhaustive flag-state coverage (`itertools.product([F,T], repeat=6)`) | **64 / 64** combos exercised |
| Hypothesis property-based coverage | Present on decomposition identity + types roundtrip (4 test files import `hypothesis`) |
| Firewall — `scripts/e10_firewall_check.py simulations/e10_gsps/ notebooks/e10_gsps/` | **PASS — 66 files scanned clean** |
| Firewall adversarial test (synthetic FX + Panoptic + PASS + strike-selection + fitted payoff) | **FIRES** on all 4 banned-token classes |
| Pre-commit hook chains E4 + E7-A + E8 + E10 | **CHAINED** — `.git/hooks/pre-commit` invokes all four checkers in sequence |
| LaTeX PDF exists at expected size | **PRESENT** — `docs/writeups/e10_gsps_methods_paper_section_5.pdf`, 381,948 bytes, 12 pages |
| LaTeX numerics match diagnostic JSON | **CONSISTENT** — `s̄ = 1.535e-4`, `s_be = 0.25`, 3.21 decades, 150 cells, 5 currencies, 5 arms verified |
| Figures present at expected paths | **PRESENT** — `e10_figure1_surface_vs_break_even.pdf` (25.5 KB) + `e10_figure2_currency_spread.pdf` (29.9 KB) |
| Markdown draft parallel to .tex | **CONSISTENT** — same headline numerics, same verdict subtype, same 6-input flag set |
| Verdict memo carries title / date / verdict / 4 §9 flags / panel-mean share / trajectory rationale / methods-paper anchor preservation / links | **PRESENT** — `memory/project_e10_gsps_verdict.md` covers all required fields |
| NHPP simulator deterministic seeding (per-cell from `(currency, year, month)`) | **HOLDS** — `_cell_seed` + `np.random.default_rng(seed)` |
| Arm-d GBM/JD comparator deterministic | **HOLDS** — `rng_seed_base = 4242` + per-currency offset |
| 7 propagation-map fixes applied | **APPLIED** — `is_panel_mean_broadcast`, `q_variance_dominance_flag_spec_form`, BLR-strip from classifier, arm-d recalibration, arm-b wording, FWL docstring all verified by grep |

---

## What was NOT regressed vs prior reviews

- **No new banned tokens.** Firewall passes clean against the full sub-package + notebook tree.
- **No new test failures within scope of the autofix wave.** The 152 unit tests held green; the 6 integration failures are the canonical-literal version-drift surface, not introduced by the autofix.
- **No new `type: ignore` / `# noqa` / broad `except`.** The one
  `type: ignore` pre-dates the Phase 6 autofix and is structurally
  justified.
- **Verdict invariance held.** The Phase 4 / Phase 5 / Phase 6 numerics
  reconcile end-to-end: surface → arms → classifier → diagnostic JSON →
  LaTeX/markdown → verdict memo.

---

## Conclusion

**APPROVED_WITH_NITS.** The code base is in good shape for PR open +
merge. The Important finding (I-1) is the only real defect — a string
literal in `anti_fishing_checks.py` that needs to track the spec
v0.4 → v0.7 update — and is mechanical to fix in well under 30 minutes.
The two Minor findings (M-1 stale provenance pointer, M-2 `make panels`
not E10-wired) are paper-cuts that can land in a polish follow-up if
the user prefers to merge immediately.

Recommended path: fix I-1 as part of this PR (one short commit
updating the canonical-string version markers in `anti_fishing_checks.py`
and aligning notebooks 01 / 02 / `_TEMPLATE.ipynb` to the v0.7 banner,
OR adding the v0.4 literal alongside the v0.7 banner in notebooks
03 / 04 / 05). Then merge.
