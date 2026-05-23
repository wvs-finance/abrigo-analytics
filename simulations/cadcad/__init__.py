"""cadCAD integration of the verified stochastic-FX machinery (paper §6).

Parent spec: ``docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex``
§6 — six state variables ``(X, S, C, P, W, R)`` plus six PSUBs running in
deterministic order at every step. Phase 1 ships the FX-side / σ_T-side /
ratchet-side (PSUBs 1, 2, 6) that depend only on already-verified
stochastic-fx primitives. PSUBs 3, 4, 5 are scaffolded as stubs that
raise ``NotImplementedError`` pending the cost-factor spec convergence and
the replicating-portfolio integration design.

Public surface:

- :class:`CadCADState` / :class:`CadCADConfig` / :class:`CadCADTrajectory` —
  Value-tier frozen dataclasses.
- :func:`pre_sample_fx_path` — Callable-tier FX-family dispatcher backing
  PSUB-1.
- :func:`psub_1_fx_advance` / :func:`psub_2_sigma_t_accumulator` /
  :func:`psub_2_sigma_t_accumulator_with_dt` / :func:`psub_6_ratchet` —
  the three live PSUBs in Phase 1.
- :func:`psub_3_cost_advance` / :func:`psub_4_replicating_portfolio_update`
  / :func:`psub_5_wage_premium_drain` — Phase 2 stubs that raise
  ``NotImplementedError``.
- :func:`run_simulation` — IO-Boundary-tier orchestrator that loops over
  the PSUBs and emits a :class:`CadCADTrajectory`.
- :class:`CadCADError` / :class:`CadCADConfigError` / :class:`CadCADStateError`
  — error hierarchy (extends ``StochasticFXError``).
"""

from simulations.cadcad._errors import (
    CadCADConfigError,
    CadCADError,
    CadCADStateError,
)
from simulations.cadcad.driver import run_simulation
from simulations.cadcad.psubs import (
    pre_sample_fx_path,
    psub_1_fx_advance,
    psub_2_sigma_t_accumulator,
    psub_2_sigma_t_accumulator_with_dt,
    psub_3_cost_advance,
    psub_4_replicating_portfolio_update,
    psub_5_wage_premium_drain,
    psub_6_ratchet,
)
from simulations.cadcad.types import (
    CadCADConfig,
    CadCADState,
    CadCADTrajectory,
)

__all__ = [
    "CadCADConfig",
    "CadCADConfigError",
    "CadCADError",
    "CadCADState",
    "CadCADStateError",
    "CadCADTrajectory",
    "pre_sample_fx_path",
    "psub_1_fx_advance",
    "psub_2_sigma_t_accumulator",
    "psub_2_sigma_t_accumulator_with_dt",
    "psub_3_cost_advance",
    "psub_4_replicating_portfolio_update",
    "psub_5_wage_premium_drain",
    "psub_6_ratchet",
    "run_simulation",
]
