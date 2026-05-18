# D1.D + D4 Joint Iteration — Implementation Plan v0.1

**Plan version:** v0.2 (post 2-way review autofix; 5 Critical + 8 Strong addressed; closure re-review pending)
**Date:** 2026-05-18
**Anchors:**
- Spec: `docs/specs/2026-05-18-d1d-d4-joint-onchain-rails-wage-capital-design.md` v0.2
- Parent: `docs/specs/2026-05-18-four-direction-gating-step-plans.md` v0.3 §0.9
- D1 transparency: `memory/feedback_d1_transparency_continuation.md`
- Predecessor pattern: `docs/plans/2026-05-04-dev-ai-stage-1-simple-beta-implementation.md`

## Plan principles (carried forward from `feedback_*.md`)

- **Specialized agents per task** (`feedback_specialized_agents_per_task.md`): every task dispatches a named specialized subagent; foreground orchestrates + verifies, never authors
- **STRICT TDD** (`feedback_strict_tdd.md`): never write implementation for a feature whose test hasn't been written + failed first
- **Notebook trio checkpoint** (`feedback_notebook_trio_checkpoint.md`): every (why-md → code → interpretation-md) trio HALTs for human review
- **Decision-citation block** (`feedback_notebook_citation_block.md`): every test/decision/spec choice preceded by 4-part block
- **Data-quality disclosure block** (NEW per spec §6 + D1 transparency condition): every notebook discloses data used / gaps / non-claims
- **Three-tier reproducibility** (CLAUDE.md): Tier 1 panels / Tier 2 raw pulls / Tier 3 panel-builder

## Phase 0 — Pre-data scaffold (TDD foundation, no data touched) — v0.2 EXPANDED

**Goal**: lay sub-package skeleton + **failing tests for every downstream module** + mechanical anti-fishing enforcement BEFORE any external data pull. Per CR-C1 + RC-C2, every implementation task in Phases 1-2 has a corresponding failing-test task in Phase 0.

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 0.1 | Scaffold `simulations/d1d_d4_joint/` per spec §9 (types/ modules/ utils/ tests/); add `__init__.py` + `_errors.py` (`JointPanelError`, `StationarityGateError`, `DepegEventInsufficientError`, **`RhoHaltError`** per CR-S3) | Data Engineer | Spec v0.2 merged | Empty package skeleton + import-discipline test failing → passing | Code Reviewer compliance check |
| 0.2 | Pre-create HALT disposition template at `notebooks/d1d_d4_joint/dispositions/_TEMPLATE.md` with all 4 outcome scaffolds (PASS / PARTIAL / FAIL / NON-RETIREMENT) | Senior Project Manager | 0.1 done | Disposition template populated | n/a |
| 0.3 | Types tier (`types/`): `OnchainInflowRow`, `JointPanelRow`, `DepegEpisode`, `GPDFitResult`, `TransmissionRatio`, `OffRampDecomposition`, `StationarityGateResult` — all frozen dataclasses + Protocols. Hypothesis strategies in `tests/strategies/types_strategies.py` | Data Engineer | 0.1 done | All types instantiable; round-trip property tests pass | Code Reviewer tier-import-discipline check |
| 0.4 | Stationarity-gate test harness (`tests/unit/test_stationarity_gate.py`) — synthetic stationary + non-stationary + cointegrated series; ADF+KPSS thresholds per spec §4.1; AND-conjunction pre-pin | Senior Developer | 0.3 done | 6 test cases failing (no impl yet) | n/a (TDD) |
| **0.5** | **NEW (CR-C1)** Inflow-aggregator test harness (`tests/unit/test_inflow_aggregator.py`) — synthetic CEX-tagged transfers → expected monthly aggregates; multi-chain merge invariants | Senior Developer | 0.3 done | Test cases failing | n/a (TDD) |
| **0.6** | **NEW (CR-C1)** Off-ramp decomposition test harness (`tests/unit/test_off_ramp_decomp.py`) — residual sign expectation (≥0 panel mean) + residual<−0.10 HALT path | Senior Developer | 0.3 done | Test cases failing including HALT-trigger test | n/a (TDD) |
| **0.7** | **NEW (CR-C1 + CR-S3)** ρ-compute test harness (`tests/unit/test_rho_compute.py`) — ratio-of-means primary; \|ρ̂\|>1.5 HALT; denominator floor $10M HALT; residual<−0.10 HALT; `RhoHaltError` typed exception path | Senior Developer | 0.3 done | All 4 HALT-trigger tests failing | n/a (TDD) |
| **0.8** | **NEW (CR-C1)** GPD POT test harness (`tests/unit/test_gpd_pot.py`) — 3-arm fit (USDC-only, USDT-only, pooled); profile-likelihood CI + jackknife on event subset; pin against D4.2 cached fits | Senior Developer | 0.3 done | All 3 arms' test cases failing | n/a (TDD) |
| **0.9** | **NEW (RC-C2)** Notebook-execution integration-test harness (`tests/integration/test_notebooks_execute.py`) — `nbconvert --execute` on each of 6 notebooks; guard against 5-instance silent-test-pass catalog | Senior Developer | 0.4-0.8 done | Stub notebooks fail execution (no content yet); harness ready | n/a (TDD) |
| **0.10** | **NEW (RC-C3)** Anti-fishing mechanical enforcement: `simulations/d1d_d4_joint/anti_fishing_checks.py` module + notebook template (`notebooks/d1d_d4_joint/_TEMPLATE.ipynb`) embedding (a) primary-spec-first ordering, (b) sensitivity-arm sign-concordance integer-count display, (c) p-values BANNED from sensitivity outputs. Compliance test `tests/integration/test_anti_fishing_compliance.py` grep-checks every notebook for forbidden patterns | Senior Developer | 0.9 done | Compliance test failing on stub notebooks until they adopt template | mandatory CR review of template |
| **0.11** | **NEW (RC-S4)** D1 transparency disclosure block template (`notebooks/d1d_d4_joint/_TRANSPARENCY_BLOCK.md`) + structural grep test `tests/integration/test_transparency_disclosure.py` checking each notebook contains all 4 disclosure fields (data used / gaps / non-claims / possible outcomes incl. non-retirement) | Senior Developer | 0.10 done | Grep test failing on stub notebooks | n/a |
| **0.12** | **NEW (RC-S3)** Stage-2 firewall mechanical enforcement: pre-commit hook + CI grep at `.github/workflows/stage2-firewall.yml` rejecting any commit touching `simulations/d1d_d4_joint/` that introduces strings matching `(Panoptic\|deploy\|LP\|liquidity)` outside docstrings + spec references | Senior Developer | 0.10 done | Stage-2 firewall hook installed + test commit confirms rejection | n/a |

## Phase 1 — Data ingest (Week 1 per spec §10)

**Goal**: pull raw data into Tier 2; verify Tier 2 against published anchors.

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 1.1 | Implement `utils/dune_io.py` — Socrata + Dune SQL execution with explicit query-snapshot persistence (Tier 2 frozen-snapshot per CR strong rec); tests run against **frozen real Dune snapshot** persisted to `data/raw/onchain/snapshots/test-fixtures/` per `feedback_real_data_over_mocks.md` (CR-C2 — NOT a mock) | Data Engineer | 0.3 done | Query bundle for {Bitso 1, Lemon, Wenia} hot wallets × {ETH, Polygon, Tron, Base, Arbitrum} USDC+USDT inflow + outflow monthly 2020-01 → 2026-04 | Code Reviewer Tier-2-snapshot integrity check |
| 1.2 | Implement `utils/cryptocompare_io.py` — CryptoCompare histoday fetcher for USDC/USDT/DAI on Kraken (re-uses D4.2 gating scripts at `scratch/2026-05-18-direction-4-gating/02_depeg_events/data/fetch_prices_v2.py` as starting point) | Data Engineer | 0.3 done | Daily USDC/USDT/DAI 2018-09 → 2026-05 persisted to `data/raw/onchain/snapshots/2026-05-18_kraken_{usdc,usdt,dai}_daily.parquet` | n/a |
| 1.3 | Extend `scripts/fetch_banrep.py` for monthly services-credit USD (quarterly cross-check anchor only per §4.1 demotion) | Data Engineer | n/a | Banrep services-credit quarterly 2018-Q1 → 2025-Q4 + TRM daily (already in repo) | n/a |
| 1.4 | Implement `utils/mento_io.py` — Celo subgraph queries for Mento broker USDC↔COPm swap events + cCOP/COPm holder counts | Data Engineer | 0.3 done | Mento broker monthly volume + holder counts persisted to Tier 2 | n/a |
| 1.5 | Verification against ≥4 published anchors (RC-S2 expansion): (a) Chainalysis LATAM crypto adoption 2025; (b) Bitso public totals ($10.4B Jan-Jul 2025); (c) **DefiLlama Bitso flow dashboards**; (d) **Etherscan/hildobby label dataset cross-check**. Target ≥3 of 4 agree at order-of-magnitude | Reality Checker | 1.1, 1.2, 1.4 done | Cross-check memo `scratch/2026-05-XX-d1d-d4-joint-data-verification.md` | RC sign-off mandatory |
| **1.6** | **NEW (RC-S1)** Early RC checkpoint — review Phase 1 data ingest outputs BEFORE Phase 2 panel build (instead of waiting until 2.7); detect upstream contamination early | Reality Checker | 1.5 done | Phase-1 review verdict | mandatory |

## Phase 2 — Panel build (Week 2 per spec §10)

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 2.1.a | **SPLIT per CR-C3 + CR-S5** Implement `modules/inflow_aggregator.py` (CEX-tagged transfers → monthly inflow series); make 0.5 tests pass | Senior Developer | 0.5, 1.6 done | Module + green tests | n/a |
| 2.1.b | Implement `modules/colombia_scalar.py` (5-arm sensitivity per §4.3) | Senior Developer | 0.3, 1.6 done | Module + green tests | n/a |
| 2.1.c | Implement `modules/off_ramp_decomp.py` (Mento broker + Bitso withdrawals → off_ramp_ratio with explicit residual term per §4.3); make 0.6 tests pass including residual<−0.10 HALT path | Senior Developer | 0.6, 1.6 done | Module + green tests + HALT-trigger test green | Code Reviewer tier-discipline check |
| 2.2 | `modules/stationarity_gate.py` — ADF + KPSS implementation per spec §4.1 with AND-conjunction threshold pre-pin | Senior Developer | 0.4 done | ADF+KPSS module; integration tests against unit-root, stationary, cointegrated synthetic series | n/a |
| 2.3 | Implement `modules/gpd_pot.py` — GPD MLE + profile-likelihood CI + jackknife on event subset; 3-arm fit (USDC-only, USDT-only, pooled) per §4.2; make 0.8 tests pass | Senior Developer | 0.8, 1.2 done | Module + green tests pinned against D4.2 stored fits | n/a |
| 2.4 | Implement `modules/rho_compute.py` — ratio-of-means primary aggregation + monthly ρ_t secondary visualization (with denominator floor) per §4.3; make 0.7 tests pass; **ALL 4 HALT triggers (\|ρ̂\|>1.5, denom-floor $10M, residual<−0.10, RhoHaltError typed)** per CR-S3 | Senior Developer | 0.7, 2.1.c done | Module + green tests including all 4 HALT-trigger paths | n/a |
| 2.5 | `utils/panel_io.py` — Tier 1 parquet emit/read schema | Data Engineer | 0.3 done | Parquet round-trip tests pass | Code Reviewer |
| 2.6 | CLI panel-builder at `scripts/build_d1d_d4_joint_panel.py` — Tier 3 round-trip implementation (re-derives Tier 1 from Tier 2). **Tier 3 acceptance criterion per CR-S2**: `make verify` re-runs the panel build from Tier 2 raw, compares against the first emission via `pandas.testing.assert_frame_equal(...check_exact=False, atol=1e-9, rtol=1e-6)`; any discrepancy fails CI | Senior Developer | 2.1.a-c, 2.2-2.5 done | Tier 1 panel + DATA_PROVENANCE.md + `make verify` target passes | n/a |
| 2.7 | Pre-pin compliance review of panel-builder output: verify (month, E_t, CF_t, off_ramp_ratio_t, rho_t, X_t, depeg_event_indicator_t) columns; ensure stationarity-gate result attached as metadata | Reality Checker + Code Reviewer | 2.6 done | 2-way review approval | mandatory |

## Phase 3 — D1.D side notebook (Week 3 per spec §10)

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 3.1 | `notebooks/d1d_d4_joint/01_data_eda.ipynb` — inflow/outflow panel construction; coverage diagnostics; Colombia-scalar 5-arm sensitivity sweep; **mandatory data-quality disclosure block** per spec §6 + D1 transparency condition | Analytics Reporter | 2.7 done | Notebook with trio HALT-checkpoints | Trio human review (mandatory) |
| 3.2 | `notebooks/d1d_d4_joint/02_d1d_inflow_beta.ipynb` — Δ-spec β primary; stationarity-gate gate at top; γ≠0 / γ=0 sensitivity; Banrep quarterly sign-concordance cross-check (NOT inferential) | Analytics Reporter | 3.1 done | Notebook + β-estimate + HAC CIs + sensitivity-arm sign-concordance table | Trio human review |

## Phase 4 — D4.1 side notebook

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 4.1 | `notebooks/d1d_d4_joint/03_d4_depeg_gpd.ipynb` — 3-arm GPD POT fit (USDC-only, USDT-only, pooled); jackknife CI on event subset; sign-concordance check; CORRECTIONS-A pooled-prior posterior update | Analytics Reporter | 2.7, 3.1 done | Notebook + 3-arm GPD posterior + CORRECTIONS-A check | Trio human review |

## Phase 5 — Joint analysis

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 5.1 | `notebooks/d1d_d4_joint/04_joint_transmission_rho.ipynb` — ratio-of-means ρ̂_window primary; off-ramp decomposition with residual term + sign check; regime-conditional ρ̂ (calm/stress/depeg) labeled exploratory only | Analytics Reporter | 3.2, 4.1 done | Notebook + ρ̂_window + off-ramp decomposition + regime conditionals (labeled non-inferential) | Trio human review |
| 5.2 | `notebooks/d1d_d4_joint/05_sensitivity.ipynb` — 5-arm Colombia-share sensitivity; pre-2020/COVID regime-break test; Layer C composite-vs-wage placebo arm | Analytics Reporter | 5.1 done | Notebook with sensitivity-arm sign-concordance scoring | Trio human review |

## Phase 6 — Verdict + write-up

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 6.1 | `notebooks/d1d_d4_joint/06_verdict.ipynb` — PASS / PARTIAL / FAIL / NON-RETIREMENT verdict consolidation per §7 collectively-exhaustive matrix; population-scope clause attached | Analytics Reporter | 5.2 done | Notebook + verdict | Trio human review |
| **6.1.5** | **REORDERED per CR-S1** Pre-write-up Delphi via audit-econ (3 Opus auditors on closed verdict notebook); fix cascade if Critical emerges — runs BEFORE memo + LaTeX authoring to avoid re-authoring | audit-econ Delphi orchestration | 6.1 done | 3 independent audit reports + dependency-graph + autofix wave if needed | mandatory before 6.2 |
| 6.2 | Verdict memo at `memory/project_d1d_d4_joint_verdict.md` + LaTeX write-up at `docs/writeups/2026-05-XX-d1d-d4-joint-vX.X.X.{tex,pdf}` — incorporates any Delphi-driven amendments | Technical Writer | 6.1.5 done | Verdict memo + LaTeX scaffold | n/a |

## Phase 7 — Post-hoc 2-way impl review + PR

| # | Task | Specialized agent | Pre-conditions | Deliverable | Review checkpoint |
|---|---|---|---|---|---|
| 7.1 | Post-hoc impl-review (Code Reviewer) of full notebooks + panel-builder + tests | Code Reviewer | 6.2 done | CR review verdict | mandatory before merge |
| 7.2 | Post-hoc impl-review (Reality Checker) of data verification + verdict reasoning | Reality Checker | 6.2 done | RC review verdict | mandatory before merge (parallel with 7.1) |
| 7.3 | Commit + push + PR with verdict; clean pytest artifacts pre-commit | Git Workflow Master | 7.1, 7.2 done | PR opened + reviewed + merged | user approval mandatory before merge |

## Cross-cutting requirements

### Anti-fishing tripwires (per spec §3 + §3.1 single-primary commitment)

- Every notebook reports the **primary spec result first**, sensitivity arms below; never the reverse
- Sensitivity-arm sign-concordance reported as a single integer count (e.g., "4 of 5 arms agree on sign"), never as p-values
- Regime-conditional ρ̂ labeled "exploratory only" in every figure caption + interpretation block
- HALT triggers (\|ρ̂\| > 1.5, denominator floor, residual < −0.10, stationarity-gate fail) check in every notebook's data-QC cell

### D1 transparency condition (per `feedback_d1_transparency_continuation.md`)

Every notebook MUST include a data-quality disclosure block answering:
1. What data was used (concrete file paths + row counts + dates)
2. What gaps remain (carrying forward to interpretation)
3. What this notebook does NOT claim (negative-result disclosure)
4. What possible outcomes are *including non-retirement*

### Test discipline (per `feedback_strict_tdd.md` + `feedback_real_data_over_mocks.md`)

- All types tier code: Hypothesis property tests before implementation
- All modules tier: unit tests + at least one integration test against real Tier 2 data
- IO Boundary (utils): mocks only for HTTP errors that can't be reproduced; real data otherwise
- Integration tests run `nbconvert --execute` on every notebook (guard against `feedback_silent_test_pass` 5-instance catalog)

## Dependencies (DAG)

```
Phase 0 (scaffold + TDD foundation)
   ↓
Phase 1 (data ingest) — parallel-eligible after 0.3
   ↓
Phase 2 (panel build) — sequential, then 2.7 review checkpoint
   ↓
Phase 3 D1.D notebooks ⟷ Phase 4 D4.1 notebooks (parallel after 2.7)
   ↓
Phase 5 (joint analysis) — sequential after 3.2 + 4.1
   ↓
Phase 6 (verdict + write-up)
   ↓
Phase 7 (post-hoc 3-way review + merge)
```

## Estimated wall-clock (v0.2 EXPANDED per RC-C1)

Predecessor dev_ai_cost_v2 v0.2.1 consumed ~12 days for a *narrower* single-sided iteration. Joint iteration is structurally larger (on-chain Dune queries + GPD POT + joint ratio-of-means + 4 HALT triggers + 4 mechanical anti-fishing enforcement layers added in Phase 0).

| Phase | Effort | Wall-clock |
|---|---|---|
| Phase 0 (v0.2 expanded: 12 tasks) | ~16 hours | 2 days |
| Phase 1 (incl. 1.6 early RC) | ~12 hours | 2 days |
| Phase 2 (incl. split 2.1, Tier 3 verify) | ~14 hours | 2.5 days |
| Phase 3 + Phase 4 (parallel) | ~14 hours | 1.5 days |
| Phase 5 | ~8 hours | 1 day |
| Phase 6 (incl. 6.1.5 Delphi-before-memo) | ~12 hours | 1.5 days |
| Phase 7 (CR + RC parallel) | ~10 hours | 1.5 days |
| **Total** | **~86 hours** | **~12-14 working days** |

Matches spec §10 "3-week execution plan" wall-clock budget. Predecessor 12-day actual is now within the plan estimate (was outside v0.1's 9-day estimate per RC-C1).

## CORRECTIONS-C block (autofix-all 2026-05-18 per user directive)

Per RC-C1/C2/C3 + CR-C1/C2/C3 + 8 Strong recs, the following v0.2 amendments are user-approved per autofix-all directive (same pattern as spec v0.2 CORRECTIONS-B):

**TDD coverage gap closure (CR-C1 + RC-C2)**:
- Phase 0 expanded with 0.5-0.8 failing-test harnesses for every modules-tier component (inflow_aggregator, off_ramp_decomp, rho_compute, gpd_pot)
- Phase 0.9 adds `nbconvert --execute` integration-test harness against 5-instance silent-test-pass catalog
- Phase 0.10 adds anti-fishing-checks module + notebook template + compliance grep test (mechanical enforcement per RC-C3)
- Phase 0.11 adds transparency-disclosure-block template + structural grep test (per RC-S4)
- Phase 0.12 adds Stage-2 firewall pre-commit + CI hook (per RC-S3)

**Mock-vs-real closure (CR-C2)**: Phase 1.1 reworded to "frozen real Dune snapshot" per `feedback_real_data_over_mocks.md`

**Singular-specialist closure (CR-C3)**:
- Phase 0.3 dual-agent ("Data Engineer + functional-python") → single Data Engineer (functional-python is a skill not an agent; coordination via dispatch instructions)
- Phase 2.1 batched 3 modules → split into 2.1.a, 2.1.b, 2.1.c (single-specialist per task)

**Anchor expansion closure (RC-S2)**: Phase 1.5 expanded from 2 to ≥4 anchors (Chainalysis + Bitso + DefiLlama + Etherscan/hildobby); target ≥3 of 4 agree

**Early RC checkpoint closure (RC-S1)**: Phase 1.6 NEW inserted between Phase 1 ingest and Phase 2 panel build

**Tier 3 acceptance criterion closure (CR-S2)**: Phase 2.6 specifies `make verify` semantics + tolerance (`assert_frame_equal atol=1e-9, rtol=1e-6`)

**Residual-HALT test closure (CR-S3)**: Phase 0.6 + Phase 2.1.c + Phase 0.7 + Phase 2.4 now thread residual<−0.10 HALT through tests + module + `RhoHaltError` typed exception in 0.1

**Delphi-reorder closure (CR-S1)**: Phase 6.1.5 NEW inserted; Delphi runs between verdict notebook (6.1) and memo+LaTeX authoring (6.2) to avoid re-authoring on Critical findings

**Wall-clock realism (RC-C1)**: 9 days → 12-14 days (predecessor pattern)

## Open items for closure re-review

1. ~~Phase 1.5 anchors~~ — closed (4 anchors)
2. ~~Phase 2.7 cadence~~ — closed (1.6 early RC added; 2.7 retained for late-stage)
3. ~~Phase 7.1 Delphi auditor count~~ — closed (3 auditors retained per dev_ai_cost_v2 precedent; rotated to 6.1.5)
4. ~~Notebook 05 sensitivity arm count~~ — 10 arms remain but all are sign-concordance-only per spec §3.1
5. ~~Wall-clock~~ — closed (12-14 days)
6. **NEW**: anti-fishing-checks module (Phase 0.10) — is the grep-based enforcement sufficient, or should it be an AST-level Python lint?
7. **NEW**: Stage-2 firewall regex (Phase 0.12) — is `(Panoptic|deploy|LP|liquidity)` too aggressive, or is the docstring/spec-reference exception sufficient to avoid false positives?

## Anti-fishing closure

All anti-fishing invariants from spec v0.2 §3 + §3.1 + CORRECTIONS-B carry forward to this plan unchanged. The execution plan does not introduce any new estimands, thresholds, or specifications beyond what spec v0.2 locks. Implementation faithfully realizes the locked spec; deviations require CORRECTIONS-C block + 2-way review.

Plan v0.1 closes here. Awaiting 2-way review.
