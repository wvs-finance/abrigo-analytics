"""NHPP simulation-engine Value-tier containers (spec v0.4 §6; R6 blueprint).

The NHPP intensity-parameter container, its five lambda(t) modulation-form
slots, and the per-(currency, month) cost-stream trajectory. Q is the ONLY
simulated quantity (spec v0.4 §0 / §3.1 — X and the FX multiplier are
real). Phase 0 holds the five lambda(t) form slots; it does NOT choose
them — that judgment is Phase 2 (plan tasks 2.3 / 2.3a).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LambdaModulationForm(Enum):
    """The five realistic NHPP intensity lambda(t) modulations the R6
    simulator must carry (spec v0.4 §6.3). The *functional form* of each
    is a Phase-2 ``[brainstorm-judgment]`` choice (plan tasks 2.3 /
    2.3a); this enum names the five SLOTS only — it pins no form.

    - DIURNAL_WEEKDAY_CYCLE — query arrivals concentrate in working
      hours and on weekdays.
    - BURSTINESS_OVERDISPERSION — dashboard batch-refreshes and research
      sprints cluster arrivals above pure-Poisson; the monthly-aggregate
      Q-distribution is overdispersed. The overdispersion *mechanism*
      (Cox / mixed-Poisson / Hawkes) is the plan task 2.3a judgment.
    - EVENT_DRIVEN_SPIKES — market/protocol events trigger query bursts.
    - MONTH_END_SEASONALITY — reporting cadence raises end-of-month
      volume.
    - SECULAR_WORKLOAD_DRIFT — the analyst's baseline workload trends
      over the panel window.
    """

    DIURNAL_WEEKDAY_CYCLE = "diurnal_weekday_cycle"
    BURSTINESS_OVERDISPERSION = "burstiness_overdispersion"
    EVENT_DRIVEN_SPIKES = "event_driven_spikes"
    MONTH_END_SEASONALITY = "month_end_seasonality"
    SECULAR_WORKLOAD_DRIFT = "secular_workload_drift"


@dataclass(frozen=True, slots=True)
class LambdaModulationSpec:
    """A single lambda(t) modulation form-and-parameter slot.

    ``form`` names which of the five §6.3 modulations this slot carries.
    ``functional_form`` is the chosen functional family (e.g.
    ``"sinusoidal"``, ``"step"``, ``"linear_drift"``) — Phase 0 leaves
    this empty; it is locked in the E10.1 calibration note (plan task
    2.3). ``params`` carries the chosen form's parameters. ``locked``
    records whether the Phase-2 judgment has been made and decision-cited.
    """

    form: LambdaModulationForm
    functional_form: str
    params: tuple[float, ...]
    locked: bool


@dataclass(frozen=True, slots=True)
class NHPPIntensityParameters:
    """R6 NHPP intensity-parameter container.

    ``lambda_0`` is the baseline arrival rate (queries/hour at the
    reference hour-block). The five ``modulations`` are the lambda(t)
    form slots of §6.3, carried as a length-5 tuple keyed by
    ``LambdaModulationForm``. ``overdispersion_mechanism`` records the
    plan-task-2.3a choice (``"cox"`` / ``"negative_binomial"`` /
    ``"hawkes"``) — empty until Phase 2 locks it. ``q_low`` / ``q_high``
    are the anchored Q-volume range bounds (spec v0.4 §2.3 / §2.4).
    ``qfx_independent`` pins the primary-spec Q-perp-FX independence
    (spec v0.4 §6.4 — Cov ~= 0 by construction in the primary).
    """

    lambda_0: float
    modulations: tuple[LambdaModulationSpec, ...]
    overdispersion_mechanism: str
    q_low: float
    q_high: float
    qfx_independent: bool


@dataclass(frozen=True, slots=True)
class CostStreamTrajectory:
    """Per-(currency, month) simulated cost-stream trajectory.

    The cost stream is ``cost = Q * 0.01 USDC * FX`` over the sub-monthly
    daily index (spec v0.4 §5.2). ``daily_query_counts`` is the NHPP
    arrival process aggregated to the common daily within-month grid
    (plan task 3.0). ``daily_fx_rate`` is the REAL central-bank FX path
    (not simulated). ``daily_cost`` is their product times the verified
    flat 0.01-USDC per-query price. ``seed`` pins the fixed simulator
    seed for Tier-3 reproducibility (plan task 3.4 — 1e-9 relative
    tolerance for simulator-derived cells).
    """

    currency: str
    year: int
    month: int
    daily_query_counts: tuple[int, ...]
    daily_fx_rate: tuple[float, ...]
    daily_cost: tuple[float, ...]
    seed: int
