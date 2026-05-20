"""Failing-test harness — R6 NHPP query-workflow simulation engine.

Plan v0.2 Phase 0.5. RED in Phase 0: imports the not-yet-existent
``simulations.e10_gsps.modules.nhpp_engine`` module, so collection
fails. The engine lands in Phase 2 (plan task 2.1).

Harness exercises:
- the five lambda(t) modulations (spec v0.4 §6.3);
- the chosen overdispersion mechanism (plan task 2.3a) — monthly-aggregate
  Q must be overdispersed relative to a pure-Poisson equidispersed null;
- the Q-perp-FX independence in the primary spec (spec v0.4 §6.4 —
  Cov ~= 0 by construction).
"""

from __future__ import annotations

import pytest

from simulations.e10_gsps._errors import (  # noqa: F401 — RED import
    NHPPCalibrationError,
    SimulatorAnchorError,
)
from simulations.e10_gsps.modules.nhpp_engine import (  # noqa: F401 — RED import
    NHPPSimulationEngineModule,
    simulate_monthly_query_counts,
)
from simulations.e10_gsps.types import (
    LambdaModulationForm,
    LambdaModulationSpec,
    NHPPIntensityParameters,
)


def _calibrated_params(*, qfx_independent: bool = True) -> NHPPIntensityParameters:
    """A synthetic CALIBRATED parameter set — all five lambda(t) forms
    locked, an overdispersion mechanism chosen. In Phase 2 these come
    from the E10.1 calibration note."""
    return NHPPIntensityParameters(
        lambda_0=4.0,
        modulations=tuple(
            LambdaModulationSpec(
                form=form,
                functional_form="sinusoidal",
                params=(1.0,),
                locked=True,
            )
            for form in LambdaModulationForm
        ),
        overdispersion_mechanism="negative_binomial",
        q_low=2_000.0,
        q_high=39_900.0,
        qfx_independent=qfx_independent,
    )


def test_engine_carries_five_lambda_modulations() -> None:
    """The engine wires in exactly the five §6.3 lambda(t) slots."""
    engine = NHPPSimulationEngineModule(params=_calibrated_params())
    assert len(engine.params.modulations) == 5


def test_simulated_monthly_q_is_overdispersed() -> None:
    """Per plan CORR-E10P-2 / task 2.3a: a pure NHPP is equidispersed
    conditional on lambda(t); the chosen overdispersion mechanism must
    inflate the monthly-aggregate variance ABOVE the mean (Fano > 1)."""
    counts = simulate_monthly_query_counts(
        params=_calibrated_params(), n_months=240, seed=42
    )
    mean = sum(counts) / len(counts)
    var = sum((c - mean) ** 2 for c in counts) / len(counts)
    assert var > mean, "monthly-aggregate Q must be overdispersed (Fano > 1)"


def test_q_is_independent_of_fx_in_primary_spec() -> None:
    """Spec v0.4 §6.4: in the primary spec Q is generated independently
    of FX — the engine accepts the FX path but the simulated Q does not
    condition on it. Two runs against different FX paths but the same
    seed must produce identical Q counts."""
    params = _calibrated_params(qfx_independent=True)
    engine = NHPPSimulationEngineModule(params=params)
    fx_a = tuple(float(x) for x in range(1, 21))
    fx_b = tuple(float(x) * 5.0 for x in range(1, 21))
    traj_a = engine(params, "COP", 2025, 1, fx_a)
    traj_b = engine(params, "COP", 2025, 1, fx_b)
    assert traj_a.daily_query_counts == traj_b.daily_query_counts


def test_engine_raises_on_uncalibrated_params() -> None:
    """An uncalibrated parameter set (no overdispersion mechanism chosen,
    lambda(t) forms unlocked) raises NHPPCalibrationError."""
    uncalibrated = NHPPIntensityParameters(
        lambda_0=4.0,
        modulations=tuple(
            LambdaModulationSpec(
                form=form, functional_form="", params=(), locked=False
            )
            for form in LambdaModulationForm
        ),
        overdispersion_mechanism="",
        q_low=2_000.0,
        q_high=39_900.0,
        qfx_independent=True,
    )
    with pytest.raises(NHPPCalibrationError):
        NHPPSimulationEngineModule(params=uncalibrated)
