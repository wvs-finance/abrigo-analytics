# `simulations/tests/` — test scaffold (Task 2.4)

This directory contains the initial test scaffold for the
`simulations/{types,modules,utils}/` global infrastructure. Phase 3.3
`hypothesis-tests` will EXTEND these files with property tests over the
Callable transforms in `simulations/modules/`.

## Layout

| File                | Tier              | Scope                                                  |
| ------------------- | ----------------- | ------------------------------------------------------ |
| `strategies.py`     | shared            | One Hypothesis strategy per Value type in `types/`     |
| `test_types.py`     | Value             | Validation invariants, accessor sanity, strategy smoke |
| `test_modules.py`   | Callable          | Math pins **M1, M2, M3, M5** verified by direct call   |
| `test_utils.py`     | IO Boundary       | Parquet / JSON round-trip, sha256 audit, schema errors |

## Run

```bash
pytest simulations/tests/ -v
pytest simulations/tests/ --cov=simulations
```

## M1–M5 verification matrix

| Pin | Spec ref     | What is tested                                                       | Test                                                        |
| --- | ------------ | -------------------------------------------------------------------- | ----------------------------------------------------------- |
| M1  | §8(6)        | `TruncParetoSampler` refuses α < 1.5 at construction                 | `test_modules.py::TestM1TruncParetoAlphaFloor`              |
| M2  | §5.1 (T2)    | `SoftplusRegularizer` refuses non-tight β (deviation ≥ 1e-3·κ)       | `test_modules.py::TestM2SoftplusTightness`                  |
| M3  | §5.1, §5.4   | `BlendedPriceFn(Sonnet defaults)` ≈ 7.149 USD/MTok + cache corners   | `test_modules.py::TestM3BlendedPrice`                       |
| M4  | §10          | parquet/JSON column-set + dtype enforcement, schema-mismatch errors  | `test_utils.py::TestCohortPriorIO / TestSyntheticTauIO / TestZCapPinnedJsonIO` |
| M5  | PRIMITIVES (6),(8) | FX path at t∈{0,π/2,π} = (4200,3800,4200); ε(σ_T) round-trip   | `test_modules.py::TestM5FXPath`                             |

The M5 `epsilon_from_sigma_T` round-trip is exact when σ_T is supplied via
the closed form `σ_T = ε² · mean² / 8` (PRIMITIVES (8)). When σ_T is
estimated empirically from a finite path, the round-trip is approximate
because mean-squared deviation samples the cos² envelope at finite cadence;
the loose round-trip test uses 4096 samples spanning ~650 cycles and
clears a 1e-2 absolute tolerance.

## Phase 3.3 extension contract

The following stay stable across the audit-pass chain:

- The Hypothesis strategies in `strategies.py` are *append-only*. New
  strategies may be added; existing strategy signatures should not change
  without a migration plan.
- Property tests added by Phase 3.3 should LIVE in `test_modules.py` (or
  a new `test_property.py` if mass calls for it) and IMPORT strategies
  from `strategies.py`. Do not redefine strategies inline.
- The CORRECTIONS-α §15.3 joint-identifiability property test for the
  TruncPareto sampler extends `test_modules.py::TestM1TruncParetoAlphaFloor`.
