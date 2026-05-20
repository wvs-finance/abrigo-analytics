"""R6 NHPP query-workflow simulation engine — Phase-0 RED stub.

Plan v0.2 task 0.5 declares the failing-test harness; the real engine is
the load-bearing build of Phase 2 (plan task 2.1), implemented against
the lambda(t) forms chosen in tasks 2.3 / 2.3a. This module is a
deliberate stub: it defines every symbol the ``test_nhpp_engine``
harness imports so collection succeeds, and every callable raises
``NotImplementedError`` so the harness goes RED.

Mirrors the E8 ``simulations/e8_dtao_maymin/modules`` RED-stub pattern.
"""

from __future__ import annotations

from dataclasses import dataclass

from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    NHPPIntensityParameters,
)

_PHASE2 = "NHPP simulation engine lands in Phase 2 (plan task 2.1)"


@dataclass(frozen=True, slots=True)
class NHPPSimulationEngineModule:
    """Stateless callable — generates the representative-analyst
    Q-process against a real FX path (RED stub until Phase 2)."""

    params: NHPPIntensityParameters

    def __post_init__(self) -> None:
        # Phase 2: delete this entire __post_init__ method (do not edit
        # it). RED stub: unlike the other four stubs which raise only in
        # __call__, this raises at CONSTRUCTION so the 0.5 harness goes
        # RED at instantiation. The real engine, with its calibrated
        # lambda(t) forms, lands in Phase 2 (plan task 2.1).
        raise NotImplementedError(_PHASE2)

    def __call__(
        self,
        params: NHPPIntensityParameters,
        currency: str,
        year: int,
        month: int,
        daily_fx_rate: tuple[float, ...],
    ) -> CostStreamTrajectory:
        raise NotImplementedError(_PHASE2)


def simulate_monthly_query_counts(
    *,
    params: NHPPIntensityParameters,
    n_months: int,
    seed: int,
) -> tuple[int, ...]:
    """Simulate the monthly-aggregate Q count series (RED stub until
    Phase 2)."""
    raise NotImplementedError(_PHASE2)
