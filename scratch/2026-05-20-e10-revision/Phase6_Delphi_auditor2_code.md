# Phase 6 Delphi — Auditor #2 (Code & Data Provenance)

**Auditor scope:** code correctness, data provenance, tier-import discipline,
firewalls, test quality, reproducibility.
**Working directory:** `/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics`.
**Independence:** I did NOT see auditors #1 or #3's work.
**Date:** 2026-05-23.

---

## 1. Provenance verification — 5 FX currencies

Verified `DATA_PROVENANCE.md` table against on-disk Tier-2 snapshots:

| Currency | DATA_PROVENANCE sha256 (16) | Re-computed sha256 (16) | Bytes (expected/on-disk) | Match |
|---|---|---|---|---|
| COP | `861be2848592affa` | `861be2848592affa` | 70,741 / 70,741 | yes |
| BRL | `ba75a914696af794` | `ba75a914696af794` | 58,379 / 58,379 | yes |
| EUR | `9cd19cf85ac11200` | `9cd19cf85ac11200` | 132,350 / 132,350 | yes |
| GBP | `378df39672a4cca0` | `378df39672a4cca0` | 12,573 / 12,573 | yes |
| NGN | `e61225c8f8fdd854` | `e61225c8f8fdd854` | 7,987,807 / 7,987,807 | yes |

All five raw payloads exist under `data/raw/e10_gsps/fx/` with `.provenance.json`
sidecars. Endpoints in `fx_ingest_io.py:110-122` correspond cleanly to the
documented central-bank sources (Banrep Socrata, BCB Olinda OData, ECB SDW,
BoE IADB, CBN Gateway).

Dropped-currency disposition (ZAR/KES/GHS): documented at `fx_ingest_io.py:41-60`
and `:202-207`; `fetch_currency` raises `ValueError` on those codes
(`:351-357`). No silent substitution path exists.

Per-currency parser (`_parse_currency_payload`) raises
`DataVisibilityRevokedError` on empty rows (`:468-472`) — no flat-fill, no
placeholder. NGN windowing happens in code because CBN has no window parameter
(documented at `:101-108` + `:181-189`).

## 2. Q-process anchor — the 214 calls

- `scratch/2026-05-20-e10-revision/e10_q_anchor_calls.csv` has **215 lines**
  (1 header + 214 rows). Group counts: `centre 63 + bracket 151 = 214` — matches
  the extraction note §1.1/§1.2.
- VMR 20.6 (centre) / 19.8 (bracket) appears in the extraction note §6 and in
  the calibration note `E10.1_calibration_note.md`; the dispersion mechanism
  selection (Cox doubly-stochastic NHPP) is justified by the table.
- The trace is genuine — per-call metadata only (timestamp / tool /
  coarse-target / session); no payloads / no secrets — per the §2.3
  "Metadata-only guarantee" in the extraction note. Spot-checked first 3 rows:
  real ISO-8601 timestamps in 2026-05, real session IDs (`15beb448`, etc.),
  WebFetch/WebSearch tool calls.

## 3. Tier-import discipline

- `types/` — `grep "from simulations"` returns ONLY sibling `.types`
  re-exports (e.g. `types/panel.py:15 from .decomposition import ...`). No
  imports from `modules/` or `utils/`. CLEAN.
- `modules/` — only `from simulations.e10_gsps._errors`,
  `from simulations.e10_gsps.types`, sibling `modules.*`, and (in arm-d) a
  lazy `from simulations.stochastic_fx` inside a `try:` at
  `sensitivity_arms.py:435-457`. NO imports from `utils/`. Verified by
  `grep "from simulations.e10_gsps.utils" simulations/e10_gsps/modules/` —
  zero hits. CLEAN.
- `utils/` is the only tier with mutable state (`FXSeriesIngest.requests_issued`
  counter at `fx_ingest_io.py:256`). CLEAN.
- Phase 4/5/6 modules (`surface_grid.py`, `vol_on_vol_regression.py`,
  `currency_spread.py`, `sensitivity_arms.py`, `verdict_classifier.py`): all
  inspected — no `def __init__` containing mutable state outside frozen
  dataclasses. The only `self.` references in `modules/` are inside frozen-DC
  `__post_init__` validators (e.g. `nhpp_engine.py:578-647`). CLEAN.

## 4. Firewall coverage

- `python scripts/e10_firewall_check.py simulations/e10_gsps/ notebooks/e10_gsps/`
  → **`E10 firewall PASS — 66 files scanned clean.`**
- Pre-commit hook at `.git/hooks/pre-commit` includes the E10 block
  (E10_CHECKER block present, scoped to
  `simulations/e10_gsps/|notebooks/e10_gsps/`). Chains E4/E7-A/E8/E10. CLEAN.
- The three firewalls (Stage-2 / fantasy / descriptive-posture) are all live in
  `scripts/e10_firewall_check.py` lines 75-92, 96+, 36-40. The `CHECK_ALLOWLIST`
  per-line mechanism is enforced via AST docstring exemption.

## 5. Test quality

`uv run pytest simulations/e10_gsps/tests/unit/` → **152 passed in 3.52s**.

- `test_verdict_classifier.py` — 8 tests covering all 6 verdict-routing flags;
  the exhaustive `test_every_flag_state_maps_to_exactly_one_descriptive_verdict`
  enumerates 2^6 = 64 states; firewall test
  `test_classifier_cannot_emit_inferential_beta_verdict` synthesizes the
  banned `"PASS"` token via string concatenation to evade the firewall regex
  (the `CHECK_ALLOWLIST` marker is correctly applied).
- `test_surface_grid.py` — 20 tests, specific assertions (e.g.
  `len(result.points) > 2`, `crossing_volumes contains 3000.0`,
  `q_variance_dominance_flag is True`).
- `test_sensitivity_arms.py` — 16 tests; HALT-d path exercised via
  `monkeypatch.setattr(builtins, "__import__", _fail_stochastic_fx)`, then
  asserts `concordance_verdict == "n/a"`, `math.isnan(concordance_metric)`,
  `"HALT" in arm_d.notes`, and the disposition memo path is referenced.
- Hypothesis property-based coverage: present at
  `test_decomposition.py:22-38` (`@given`) and via
  `tests/strategies/types_strategies.py`. Not blanket, but the §4.2 identity
  is property-tested.
- Determinism: tested via per-currency explicit seed map
  (`sensitivity_arms.py:494-499` — `{"COP": 101, "BRL": 211, ...}`), avoiding
  the `hash()` / PYTHONHASHSEED pitfall (commented as the rationale at
  `:490-493`).

## 6. No fabricated comparators / hand-rolled statistics

- Arm (d) GBM/JD: imports `simulations.stochastic_fx` and uses real
  `GBMPathGenerator` + `JumpDiffusionPathGenerator`. The HALT path returns
  `concordance_verdict="n/a"` on ImportError. NO inline hand-coded GBM. CLEAN.
- §4.2 variance decomposition (`modules/decomposition.py`): uses
  `population_variance` (a shared utility, presumably from
  `realized_variance.py`), and computes 2·Cov via the standard
  `mean(a·b) - mean(a)·mean(b)` formula. Enforces the exact identity at 1e-12.
  Pure-python sums (not numpy) but mathematically correct. CLEAN.
- Vol-on-vol regression: SEE Finding M-1 below.

## 7. Reproducibility

- `scripts/build_e10_gsps_panel.py --verify-against-tier1` is the
  documented round-trip path; `DATA_PROVENANCE.md §5` records the verdict
  ("verified PASS on all 150 cells").
- `_cell_seed(currency, year, month)` at `nhpp_engine.py:676-685`:
  `base = sum(ord(ch) for ch in currency); return base*1e6 + year*100 + month`
  — deterministic, NOT hash-based, NOT PYTHONHASHSEED-dependent. CLEAN.
- NHPP simulator uses `np.random.default_rng(seed)` exclusively
  (`nhpp_engine.py:639, 723, 730`). No `np.random` global state. CLEAN.
- Per-currency arm-d GBM/JD seeds use an explicit lookup table
  (`sensitivity_arms.py:494-499`), with documented rationale against `hash()`.
  CLEAN.

## 8. Code-quality red flags

- `type: ignore` instances: 1 in main code (`utils/panel_io.py:217`,
  TypedDict spread — acceptable), 10 in tests (all on frozen-dataclass
  assignment-rejection tests — legitimate). CLEAN.
- `# noqa: F401 — RED import` markers: 4 in tests, all marking the
  TDD-RED import-the-not-yet-existent-module pattern. CLEAN.
- `except Exception`: zero hits in `modules/`/`types/`/`utils/`. CLEAN.
- The only broad-ish handler is the deliberate `ImportError` catch at
  `sensitivity_arms.py:442` — narrow, documented, and is the HALT-d entry. CLEAN.
- Mutable defaults: zero hits via `grep "=\\s*\\[\\]\\|=\\s*\\{\\}" def `. CLEAN.

---

## Findings

### M-1 — vol-on-vol regression uses hand-rolled FWL slope, not statsmodels OLS

```
FINDING:
- Name: vol_on_vol uses hand-rolled within-FE slope instead of statsmodels
- Severity: Mid
- Location: simulations/e10_gsps/modules/vol_on_vol_regression.py:144-160 (_within_slope)
- Problem: The §4.1 two-way and currency-only within-FE slopes are computed
  by `sum(x_tilde * y_tilde) / sum(x_tilde**2)` against numpy arrays —
  algebraically equivalent to the FWL/within OLS coefficient, but no
  statsmodels OLS object is constructed and no standard errors / residual
  variance are produced.
- Proposed fix: Either (a) leave as-is and document explicitly in §5 that
  the regression is a *slope-and-sign-only descriptive estimator* with no
  inferential output (the existing `_G_CAVEAT_LABEL` at line 64-68 partly
  does this), OR (b) replace with `statsmodels.OLS` on within-demeaned data
  for the slope and emit `None` for SEs at G=5 with the G-caveat — this
  gives a third-party-replicable estimator object even though the SE is
  unreported.
- Evidence: vol_on_vol_regression.py:155-160:
      denom = float((x_tilde * x_tilde).sum())
      if denom == 0.0:
          return 0.0
      return float((x_tilde * y_tilde).sum() / denom)
  The function returns ONLY the slope. The VolOnVolResult container at
  line 237-248 carries `beta_two_way`, `beta_currency_only`, `sign_*`, and
  `g_caveat_label` — no SE, no residual variance. Under the
  descriptive-only posture this is honest, but the audit-prompt's specific
  ask was statsmodels-or-equivalent. Reading the FWL identity charitably,
  the slope IS equivalent, so this is Mid (code-quality drift), not High
  (fabricated statistics).
```

### L-1 — DATA_PROVENANCE.md "$0.01" multiplier description claim

```
FINDING:
- Name: x402 multiplier provenance verified offline only
- Severity: Low
- Location: data/raw/e10_gsps/x402/x402_payment_required.json
- Problem: The single JSON file at this path is the recorded x402 probe
  payload that pins the $0.01/query multiplier. I confirmed the file
  exists (`ls` shows it) but did not re-fetch from The Graph Gateway
  to verify the live offer is still $0.01.
- Proposed fix: Note in §5 that the $0.01 figure is a frozen 2026-05
  observation; cite the snapshot path. No live re-pull required.
- Evidence: DATA_PROVENANCE.md §2 documents the file; no automatic
  re-verification job exists. This is acceptable per spec v0.6 — the
  multiplier is treated as a fixed historic constant.
```

### Levels with NO findings

- **Critical** — none. All FX bytes hash-verified against
  `DATA_PROVENANCE.md`. No fabricated data anywhere. The 214-call anchor
  is a real CSV with real timestamps.
- **High** — none. Tier-import discipline is intact, no silent data
  substitution, no fabricated statistics (the hand-rolled FWL is
  mathematically equivalent under the descriptive posture).

---

## Top-line verdict

**APPROVE FOR §5 AUTHORING.**

The code/data provenance is sound:

1. All 5 FX currencies have hash-verified Tier-2 snapshots from documented
   central-bank endpoints.
2. The 214-call Q-anchor is real, timestamped, and metadata-only.
3. Tier-import discipline is clean across all Phase 4/5/6 modules.
4. The E10 firewall passes (66 files); pre-commit hook chains all four
   firewalls.
5. 152/152 unit tests pass. HALT paths are exercised. Determinism is
   pinned via explicit per-currency seed maps (no PYTHONHASHSEED leak).
6. Arm-d uses the real `simulations.stochastic_fx` generators, not inline
   GBM. HALT-on-missing-import is honest.
7. Cell-seed derivation is fully deterministic
   (`sum(ord) * 1e6 + year * 100 + month`).

The single Mid finding (M-1) is a code-quality nit, not a correctness bug
— the slope estimator is FWL-equivalent. It can be addressed by a §5
sentence explicitly noting the descriptive-only posture, or in a follow-up
to swap in statsmodels for replicability. Neither blocks §5 authoring.

Recommended cleanup before final commit: address M-1 by adding one
sentence in §5 stating "the vol-on-vol slopes are within-FE FWL
estimators, computed on numpy-vectorized demeaned series; no SE is
reported owing to G=5 (see `_G_CAVEAT_LABEL`)."
