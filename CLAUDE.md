# CLAUDE.md — Abrigo Analytics

This file provides guidance to Claude Code when working in this repository.

## Repository scope

This repo is the **analytics half** of the Abrigo project. It contains:

- Empirical-validation work (does the underlying microeconomic risk admit a
  positive measurable beta?) for the (Y, M, X) instrument family.
- Notebooks, plans, specs, and research artifacts driving each (Y, X) iteration.
- Data fetchers and processed panels, distributed via three reproducibility tiers.

The **contract half** (Solidity, Foundry, Rust nodes) lives separately in the
`thetaSwap-core-dev` repo; pointers to it are preserved in `memory/` and the
specs that depend on Panoptic / Uniswap V4 settlement.

## Abrigo Operating Framework — (Y, M, X) Triples for Permissionless Convex Hedges

**Highest-level goal**: **make actual investment productive** by providing
permissionless on-chain CFMM-based convex hedges against **micro-risks
identified via post-Keynesian theory** (Bhaduri-Laski-Riese 2006 virtual-vs-real
dichotomy; Minsky P_k/P_i two-price gap; Kaleckian investment-driven output).
The instruments alter the institutional structure that defaults to BLR's
"virtual prosperity coexisting with real stagnation" — they create the
conditions under which marginal capital flows toward real-economy production
rather than asset-trading recycling. Income-inequality reduction is one downstream
consequence; the operative mechanism is investment-productivity, not transfer.

**Investor classes (cohorts) the framework serves**: any decision-making unit
exposed to a hedgeable micro-risk on its productive-investment path. Examples
demonstrated in active iterations: Colombian import micro-vendors with USD COGS
(D2); Colombian USDC-savers facing depeg risk (D4); Colombian crypto-rail-paid
remote workers transitioning savings → capital (D1.D); Giveth/q-acc productive-
investment donors and recipients (D5 candidate). The **wage-earner → productive
capital transition** is one investor-class instance among these, not the
generalized headline — see `memory/project_abrigo_framing_clarification_investment_productivity.md`
(2026-05-18) for the canonical clarification.

**Instrument family**: permissionless on-chain perpetual convex instruments,
settled on **Panoptic** (perpetual options written on Uniswap v3/v4 LP
positions). The denomination of any given hedge — Mento-native (COPm, BRLm,
KESm, EURm, USDm), USDC, ETH, sectoral basket tokens, or any Panoptic-eligible
pair — is a *parameter of each iteration*, selected to fit the target cohort.

**Ideal-scenario modeling permitted (Panoptic-liquidity caveat).** Panoptic
deployment liquidity is structurally thin today. The framework permits — and at
this stage *requires* — modeling the **ideal scenario** in which the proposed
instrument settles cleanly with adequate liquidity. The empirical β-estimate
work (does the underlying microeconomic risk admit a positive measurable beta?)
is independent of actual on-chain deployment; the M-design step proposes the
ideal settlement architecture; only the deployment step requires real LP
capital. **Stage-correctly with explicit exit criteria:**

1. Empirical risk validation FIRST (exit: positive-β confirmation on the chosen X
   at conventional significance).
2. Ideal-scenario M sketch SECOND (exit: a Panoptic-position construction that
   *would* settle the empirical β if deployed; no liquidity sourcing required).
3. Deployment LAST (exit: live LP capital + execution test).

Stage drift (M-design ballooning back into apparatus) is anti-fishing-banned.

**Transmission mechanism — premium-funded ratchet on productive investment**:
the perpetual hedge functions as a liquidity-bootstrapping mechanism for the
*holder*. The investor pays a small recurring premium out of cash flow; the
instrument's accumulated convex payoff and roll yield convert over time into
*real-economy exposure* (productive inventory, capital equipment, equity in
real builders, hedged forward purchase commitments — the specific form depends
on cohort). The hedge's existence is what *protects* the investment from the
macro risks (X) that would otherwise destroy the productive-capital position
under unhedged exposure. This is the premium-funded ratchet design — not
up-front capital protection, not speculative leverage. **One concrete instance**:
wage-earner pays premium → convex payoff → productive-capital position
("self-LBM" / wage→capital story, preserved as iteration D1.D).
**Generalized form**: any investor pays premium → hedge protects the productive-
investment path → real output is produced under risk that would otherwise have
killed the project.

**Theoretical anchor (read for terminology consistency)**: `memory/reference_bhaduri_laski_riese_concept_bridge.md`
maps PK financialization concepts (virtual-vs-real; Minsky two-price;
Kaleckian wage-led vs profit-led growth) to on-chain analogs (AMM vs spot;
impermanent loss; Panoptic-perp-as-Pk/Pi-price). The cleanest unfilled academic
gap — Minsky P_k/P_i formally connected to AMM micro-structure and priced by
Panoptic-style perpetual options — is Abrigo's potential methods-paper
contribution, publishable in Cambridge JE / ROPE / Metroeconomica independent
of any single iteration's β verdict.

**Operating unit of work — (Y, M, X) triples**:

- **Y** = outcome variable on which the target cohort's *investment-productivity*
  is measured. Examples: cohort-aggregate real-investment-rate (R_real_t);
  productive-investment-vs-speculative-investment ratio (Y_real/Y_virtual, the
  on-chain BLR two-price gap); realized variance of cohort cash flow; margin
  of import-resale operations under FX shock; wallet-balance trajectories of
  USDC-saver populations. Inequality differentials remain a valid Y class for
  inequality-focused iterations (see Y₃) but are not the generalized headline.
- **M** = the Panoptic pool configuration that hosts the hedge — the underlying
  token pair, the strike/range geometry of the deployed position, and the payoff
  shape (long-gamma covered call, range LP, perpetual put, straddle, long-tail
  OTM put, ABC-vesting position, etc.). M choice is constrained by Panoptic's
  pool mechanics: the (Y, X) pair must admit a continuous on-chain reference
  price representable as a Panoptic position. Off-Panoptic venues are out of
  scope.
- **X** = the *major micro-risk* identified via PK theory that currently
  threatens the cohort's productive investment. First-cut iteration question:
  "what micro-risk, identified by post-Keynesian theory (BLR/Minsky/Kaleckian),
  destroys this cohort's productive-investment path?" Examples: COP/USD vol +
  jumps for import micro-vendors; USDC depeg for stablecoin savers; FX-induced
  real-wage erosion for cross-border-paid remote workers; ERPT regime shifts
  for tariff-exposed importers. X identification is empirical and must precede
  M selection.

**Iteration order (default — cohort-population dominant)**: fix the cohort →
fix Y on a candidate productive-investment-exposure measure → enumerate X
candidates from the empirical PK micro-risk surface → for each surviving X,
search Panoptic-eligible M for tradability. The (Y, X) pair only graduates to
instrument design once a Panoptic position with viable convex pricing exists.
Closed iterations (gate verdict FAIL) inform the X-search prior for the next
cohort, not silent re-runs of the same (Y, X) at different thresholds —
anti-fishing invariants carry forward.

## Active iterations (snapshot)

State of each iteration is canonical in `memory/` (project memories). Quick
summary as of repo bootstrap:

- **Pair D** (BPO offshoring × COP/USD lag) — **PASS** verdict; β = +0.137,
  p ≈ 1.5e-08; Stage-2 M-sketch unblocked. See `memory/project_pair_d_phase2_pass.md`
  + notebooks/`bpo_offshoring_fx_lag/`, `pair_d_stage_2_path_a/`,
  `pair_d_stage_2_path_b/`.
- **dev-AI Stage-1** (Colombian young-worker Section J × COP/USD lag) — Phase
  1 dispatched 2026-05-05; data ingest in progress. See specs
  `2026-05-04-dev-ai-stage-1-simple-beta-design.md` + notebooks/`dev_ai_cost/`.
- **FX-vol-on-CPI-surprise** — **CLOSED FAIL** 2026-04-19 (β̂ = −0.000685, 90%
  CI contains 0). Notebooks remain as reference. See
  `memory/project_fx_vol_cpi_notebook_complete.md`.
- **Phase-A.0 remittance** — **CLOSED EXIT_NON_REMITTANCE** 2026-04-24. See
  `memory/project_phase_a0_exit_verdict.md`.
- **P1 Bittensor SN18** — **PARKED** for record. See
  `memory/project_p1_sn18_spec_parked_for_record.md`.

## Repo structure

```
abrigo-analytics/
├── README.md              # Public-facing quickstart for cloners
├── CLAUDE.md              # This file
├── pyproject.toml         # uv-managed; mirrors requirements.txt; declares simulations/ package
├── requirements.txt       # exact pin from source repo's venv
├── Makefile               # data tiers + notebook execution + lint/test
├── notebooks/             # 7 notebook trios + 2 standalone analyses
├── simulations/           # functional-python three-tier package (added by SIM-INFRA-0)
│   ├── types/             # Value tier — frozen-dataclass parameter containers + Protocols
│   ├── modules/           # Callable tier — frozen-dc + __call__ stateless transforms
│   ├── utils/             # IO Boundary tier — class-with-__init__; mutable state lives ONLY here
│   ├── saas_builder/      # COHORT-1: T1 PyMC posterior + emission (priors/model/diagnostics/emit)
│   └── tests/             # pytest + Hypothesis strategies + math-pin verification
├── docs/specs/            # 14 specs (econ/analytics relevant)
├── docs/plans/            # 11 implementation plans (SIM-INFRA-0 added)
├── docs/sub-plans/        # 2 sub-plans (NB-α, ccop-provenance-audit)
├── scratch/               # ~245 research outputs (dispositions, reviews, designs)
├── memory/                # 65+ memory files — project state + feedback rules
├── data/                  # gitignored; populated via three Make targets
└── scripts/               # data fetchers (Tier 1/2) + panel builder (Tier 3)
```

**`simulations/` discipline.** Three-tier (Value / Callable / IO Boundary) per
`functional-python` skill: no inheritance except `Protocol` + `Exception` +
private Pydantic `BaseModel` (utils/json_io transient validators) + TypedDict
(utils/parquet_io row schemas). Tier-import discipline: types/ ↛ modules/utils;
modules/ ↛ utils. Code-touching work follows the Honnibal audit-pass chain
(tighten-types → contract-docstrings → hypothesis-tests → try-except →
pre-mortem → mutation-testing) as established by SIM-INFRA-0 Phase 3.

## Key commands

```bash
# First-time setup
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt

# Three data tiers (pick one — see data/README.md)
make data         # Tier 1: HuggingFace processed panels (~30 sec)
make data-raw     # Tier 2: DANE + Banrep raw (~30 min, ~5.3 GB)
make data-onchain # Tier 2: Celo RPC on-chain panels (~10 min)
make panels       # Tier 3: re-derive Tier 1 from Tier 2 raw

# Run all notebooks headless
make notebooks

# Verify reproducibility (Tier 3 vs published Tier 1)
make verify
```

## Code style

- **Python**: frozen dataclasses, free pure functions, full typing (per the
  `functional-python` skill). Composition over inheritance.
- **Notebooks**: trio discipline — every (why-markdown, code-cell,
  interpretation-markdown) trio is a HALT-checkpoint for human review per
  `feedback_notebook_trio_checkpoint.md`. Decision-citation block (4-part:
  reference / why / relevance / connection) precedes every test or spec choice
  per `feedback_notebook_citation_block.md`.

## Anti-fishing invariants (carried forward from contracts/ source)

These are NON-NEGOTIABLE across iterations:

- `N_MIN = 75`, `POWER_MIN = 0.80`, `MDES_SD = 0.40` SD-units of Y.
- Pre-pin sign expectation, lag structure, and primary specification BEFORE
  data is touched. Threshold tuning post-hoc is silent-fishing.
- HALT + disposition memo + user-enumerated pivot + CORRECTIONS block + post-hoc
  3-way review whenever spec contradicts data. See
  `feedback_pathological_halt_anti_fishing_checkpoint.md`.

## Cross-repo dependencies

This repo intentionally has **no Solidity / Foundry / Rust** code. Specs and
plans that reference Panoptic / Uniswap V4 / Mento contracts treat those as
external givens. The contract half remains in `thetaSwap-core-dev`; cloners do
not need it for analytics work.
