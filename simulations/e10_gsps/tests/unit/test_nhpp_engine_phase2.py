"""Phase-2 (E10.1) tests for the R6 NHPP simulation engine.

The task-0.5 RED harness (``test_nhpp_engine.py``) pins the Phase-0
contract — five λ(t) slots, monthly overdispersion, Q ⊥ FX, the
uncalibrated-params guard. This file adds the behaviour-focused tests for
the Phase-2 implementation choices (plan task 2.1, STRICT TDD): the Cox
Gamma-mixed primary mechanism, the log-normal sensitivity arm, the
calendar-grid cost product, the FX-index alignment, and the locked
two-peak diurnal modulation form.

All forms are LOCKED in the E10.1 calibration note; these tests verify
the engine *implements* the locked choices.
"""

from __future__ import annotations

import calendar
import math

import pytest

from simulations.e10_gsps._errors import NHPPCalibrationError
from simulations.e10_gsps.modules.nhpp_engine import (
    NHPPSimulationEngineModule,
    calibrated_intensity_parameters,
    diurnal_hourly_envelope,
    simulate_monthly_query_counts,
)
from simulations.e10_gsps.types import (
    LambdaModulationForm,
    LambdaModulationSpec,
    NHPPIntensityParameters,
)


def _params(*, mechanism: str = "cox") -> NHPPIntensityParameters:
    """A calibrated parameter set — five λ(t) forms locked, an
    overdispersion mechanism chosen (the E10.1 calibration-note shape)."""
    return NHPPIntensityParameters(
        lambda_0=4.0,
        modulations=tuple(
            LambdaModulationSpec(
                form=form,
                functional_form="calibration-note-§4",
                params=(1.0,),
                locked=True,
            )
            for form in LambdaModulationForm
        ),
        overdispersion_mechanism=mechanism,
        q_low=2_000.0,
        q_high=39_900.0,
        qfx_independent=True,
    )


def _vmr(counts: tuple[int, ...]) -> float:
    """Sample variance-to-mean ratio of a count series."""
    mean = sum(counts) / len(counts)
    var = sum((c - mean) ** 2 for c in counts) / (len(counts) - 1)
    return var / mean


# ── Cox primary mechanism ───────────────────────────────────────────────

def test_cox_primary_is_decisively_overdispersed() -> None:
    """The Cox / doubly-stochastic primary (Gamma-mixed sprint-intensity)
    must produce a monthly-aggregate VMR well above the equidispersed
    Poisson value of 1 — the calibration-note §3.1 finding."""
    counts = simulate_monthly_query_counts(
        params=_params(mechanism="cox"), n_months=240, seed=7
    )
    assert _vmr(counts) > 3.0, "Cox mechanism must overdisperse Q decisively"


def test_negative_binomial_fallback_also_overdisperses() -> None:
    """The §3.4 fallback (NB marginal) is a recognised calibrated
    mechanism and also overdisperses the monthly aggregate."""
    counts = simulate_monthly_query_counts(
        params=_params(mechanism="negative_binomial"), n_months=240, seed=7
    )
    mean = sum(counts) / len(counts)
    var = sum((c - mean) ** 2 for c in counts) / len(counts)
    assert var > mean


# ── log-normal sensitivity arm (Model QA Strong-1) ──────────────────────

def test_lognormal_sensitivity_arm_is_a_valid_mechanism() -> None:
    """Per Model QA Strong-1: the Gamma mixing law is a conjugacy
    default, not trace-discriminated; a log-normal-mixing sensitivity arm
    is carried alongside. It must be an accepted calibrated mechanism and
    must also overdisperse Q."""
    counts = simulate_monthly_query_counts(
        params=_params(mechanism="cox_lognormal"), n_months=240, seed=7
    )
    mean = sum(counts) / len(counts)
    var = sum((c - mean) ** 2 for c in counts) / len(counts)
    assert var > mean


def test_unrecognised_mechanism_raises() -> None:
    """A mechanism string outside the three locked choices is rejected —
    the engine does not guess a mechanism."""
    with pytest.raises(NHPPCalibrationError):
        NHPPSimulationEngineModule(params=_params(mechanism="poisson"))


# ── cost product + FX-index alignment ───────────────────────────────────

def test_cost_is_q_times_price_times_fx() -> None:
    """The cost stream is exactly ``Q × $0.01 × FX`` cell by cell."""
    engine = NHPPSimulationEngineModule(params=_params())
    n_days = 31  # 2025-01
    fx = tuple(4000.0 + float(d) for d in range(n_days))
    traj = engine(_params(), "COP", 2025, 1, fx)
    for q, rate, cost in zip(
        traj.daily_query_counts, traj.daily_fx_rate, traj.daily_cost
    ):
        assert math.isclose(cost, q * 0.01 * rate, rel_tol=1e-12)


def test_trajectory_series_share_one_index() -> None:
    """The three trajectory series (Q, FX, cost) share one daily index —
    the common differencing grid (plan task 3.0)."""
    engine = NHPPSimulationEngineModule(params=_params())
    fx = tuple(4000.0 + float(d) for d in range(31))
    traj = engine(_params(), "BRL", 2025, 1, fx)
    assert (
        len(traj.daily_query_counts)
        == len(traj.daily_fx_rate)
        == len(traj.daily_cost)
        == 31
    )


def test_fx_path_overrunning_the_month_raises() -> None:
    """An FX path longer than the month's calendar length is a caller
    bug — the simulated month has no Q to align past its last day."""
    engine = NHPPSimulationEngineModule(params=_params())
    too_long = tuple(float(d) for d in range(40))  # Feb has 28 days
    with pytest.raises(NHPPCalibrationError):
        engine(_params(), "EUR", 2025, 2, too_long)


def test_cell_is_reproducible_across_runs() -> None:
    """A (currency, year, month) cell reproduces bit-stably — the seed is
    derived from the cell identity (Tier-3 round-trip, plan task 3.4)."""
    engine = NHPPSimulationEngineModule(params=_params())
    fx = tuple(4000.0 + float(d) for d in range(31))
    a = engine(_params(), "COP", 2025, 1, fx)
    b = engine(_params(), "COP", 2025, 1, fx)
    assert a.daily_query_counts == b.daily_query_counts
    assert a.seed == b.seed


def test_distinct_currencies_get_distinct_q() -> None:
    """Different panel currencies draw distinct Q-processes — the cell
    seed keys on the currency code."""
    engine = NHPPSimulationEngineModule(params=_params())
    fx = tuple(1.0 for _ in range(31))
    cop = engine(_params(), "COP", 2025, 1, fx)
    ngn = engine(_params(), "NGN", 2025, 1, fx)
    assert cop.daily_query_counts != ngn.daily_query_counts


# ── modulation 1 — locked two-peak diurnal form ─────────────────────────

def test_diurnal_envelope_is_two_peaked_and_normalised() -> None:
    """Modulation 1 is locked (calibration note §4.1) as a TWO-peak
    diurnal envelope (UTC-morning + UTC-evening), not a single bump.
    The envelope is a normalised 24-hour probability vector with two
    distinct local maxima."""
    env = diurnal_hourly_envelope()
    assert len(env) == 24
    assert math.isclose(sum(env), 1.0, rel_tol=1e-9)
    # Two interior local maxima ⇒ a bimodal shape.
    peaks = [
        h
        for h in range(1, 23)
        if env[h] > env[h - 1] and env[h] > env[h + 1]
    ]
    assert len(peaks) == 2, "diurnal envelope must be two-peaked"


# ── secular drift — modulation 5 ────────────────────────────────────────

def test_positive_drift_slope_raises_monthly_volume() -> None:
    """Modulation 5 (log-linear secular drift): a positive drift slope
    must raise later-month query volume above earlier months."""
    drifting = NHPPSimulationEngineModule(
        params=_params(), drift_log_slope_per_month=0.05
    )
    fx = tuple(1.0 for _ in range(31))
    early = sum(drifting(_params(), "COP", 2024, 1, fx).daily_query_counts)
    late = sum(drifting(_params(), "COP", 2025, 12, fx).daily_query_counts)
    assert late > early


# ── month-end seasonality — modulation 4 (OPEN magnitude) ───────────────

# ── trace-anchored calibrated parameter factory ─────────────────────────

def test_calibrated_params_are_runnable_and_q_low_unpinned() -> None:
    """The E10.1 calibrated parameter factory returns a runnable set —
    five λ(t) slots locked, the Cox primary mechanism — and ``Q_low`` is
    NaN (the proxy-bracket-pending OPEN calibration item, calibration
    note §5), never a fabricated default."""
    params = calibrated_intensity_parameters()
    engine = NHPPSimulationEngineModule(params=params)  # must not raise
    assert engine.params.overdispersion_mechanism == "cox"
    assert len(params.modulations) == 5
    assert all(m.locked for m in params.modulations)
    assert math.isnan(params.q_low), "Q_low must be unpinned (OPEN item)"
    assert params.q_high == 39_900.0


def test_calibrated_centre_is_in_the_anchored_q_volume_range() -> None:
    """The calibrated centre reproduces the calibration-note §2 anchor —
    a representative-analyst monthly Q on the order of ~60-130 priceable
    queries in sprint-driven months. The simulated monthly-aggregate Q
    mean must sit in (roughly) that anchored band."""
    counts = simulate_monthly_query_counts(
        params=calibrated_intensity_parameters(), n_months=240, seed=11
    )
    mean_monthly = sum(counts) / len(counts)
    assert 40.0 < mean_monthly < 200.0, (
        f"calibrated monthly-Q centre {mean_monthly:.0f} is outside the "
        f"anchored ~60-130/mo band's tolerance window"
    )


def test_calibrated_sensitivity_arm_selectable() -> None:
    """The log-normal-mixing sensitivity arm is selectable through the
    factory (Model QA Strong-1)."""
    params = calibrated_intensity_parameters(mechanism="cox_lognormal")
    NHPPSimulationEngineModule(params=params)  # must not raise


def test_month_end_bump_defaults_to_no_op() -> None:
    """Modulation 4's magnitude is the proxy-bracket-pending OPEN
    calibration item (calibration note §4.4). The engine default is a
    no-op bump (magnitude 0.0) until plan task 2.2's proxy research pins
    it — so the default engine and an explicit-zero engine agree."""
    default_engine = NHPPSimulationEngineModule(params=_params())
    explicit_zero = NHPPSimulationEngineModule(
        params=_params(), month_end_bump_magnitude=0.0
    )
    fx = tuple(1.0 for _ in range(31))
    a = default_engine(_params(), "COP", 2025, 1, fx)
    b = explicit_zero(_params(), "COP", 2025, 1, fx)
    assert a.daily_query_counts == b.daily_query_counts


# ── empty FX path — the documented edge case (review I-1) ───────────────

def test_empty_fx_path_yields_empty_aligned_trajectory() -> None:
    """An empty FX path is the documented degenerate case: the trajectory
    is aligned to the FX index, so an empty FX index ⇒ empty Q, FX, and
    cost series — NOT the full calendar counts (which would crash the
    strict-zip cost product). Locks the review I-1 fix."""
    engine = NHPPSimulationEngineModule(params=_params())
    traj = engine(_params(), "COP", 2025, 1, ())
    assert traj.daily_query_counts == ()
    assert traj.daily_fx_rate == ()
    assert traj.daily_cost == ()


def test_short_fx_path_truncates_q_to_fx_length() -> None:
    """A non-empty but short FX path (FX trading days < calendar days)
    truncates the simulated Q to the FX length — the three series stay
    aligned on the FX index."""
    engine = NHPPSimulationEngineModule(params=_params())
    fx = tuple(4000.0 + float(d) for d in range(20))  # 20 < 31 calendar
    traj = engine(_params(), "COP", 2025, 1, fx)
    assert (
        len(traj.daily_query_counts)
        == len(traj.daily_fx_rate)
        == len(traj.daily_cost)
        == 20
    )


# ── VMR mapping — vmr_target tunability (review M-4) ─────────────────────

def _weekday_pooled_vmr(target: float, *, n_months: int = 24) -> float:
    """Realized daily VMR pooled over WEEKDAY counts across ``n_months``.

    The VMR mapping pins the *within-day-type* count dispersion; pooling
    over all calendar days would instead be dominated by the weekday vs
    weekend envelope spread (review M-1). Pooling weekday counts isolates
    the dispersion the ``vmr_target`` mapping actually controls.
    """
    engine = NHPPSimulationEngineModule(params=_params(), vmr_target=target)
    weekday_counts: list[int] = []
    for k in range(n_months):
        year = 2024 + k // 12
        month = k % 12 + 1
        n_days = calendar.monthrange(year, month)[1]
        fx = tuple(1.0 for _ in range(n_days))
        counts = engine(
            _params(), "COP", year, month, fx
        ).daily_query_counts
        for day_idx, count in enumerate(counts):
            if calendar.weekday(year, month, day_idx + 1) < 5:
                weekday_counts.append(count)
    return _vmr(tuple(weekday_counts))


def test_realized_vmr_tracks_vmr_target() -> None:
    """The load-bearing VMR mapping: a given ``vmr_target`` must map to a
    realized daily VMR in its neighbourhood. The mapping is APPROXIMATE —
    the day-count marginal carries between-day envelope variance and the
    post-clip floor lifts the mean slightly (review M-1 / M-2), and the
    realized VMR runs somewhat ABOVE target — so a generous band is used,
    but a silently broken mapping (e.g. VMR pinned at the Poisson value 1)
    would fall well outside it."""
    for target in (10.0, 40.0):
        realized = _weekday_pooled_vmr(target)
        assert 0.5 * target < realized < 2.5 * target, (
            f"realized weekday VMR {realized:.1f} far from target {target}"
        )


def test_higher_vmr_target_gives_higher_realized_vmr() -> None:
    """Monotonicity of the VMR mapping: a higher ``vmr_target`` must
    produce a higher realized daily VMR (review M-4)."""
    assert _weekday_pooled_vmr(10.0) < _weekday_pooled_vmr(40.0)
