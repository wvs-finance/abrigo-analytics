"""R6 NHPP query-workflow simulation engine — E10.1 (plan task 2.1).

The load-bearing build of Phase 2: the representative Web3-data-analyst
Q-process, resurrected from the R6 19-task NHPP design blueprint
(``docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md`` §2.1)
and built fresh against the E10.1 calibration note
(``notebooks/e10_gsps/diagnostics/E10.1_calibration_note.md``).

What the engine is
------------------
The arrival process is a **Cox / doubly-stochastic NHPP** (calibration
note §3.3, RATIFIED by the pre-Phase-2 Model QA review): a deterministic
intensity envelope λ_det(t) carrying the five §6.3 modulations, multiplied
by a *random* per-day sprint-intensity Λ_d. The sprint-intensity layer is
what produces the trace's observed daily variance-to-mean ratio ≈ 20 —
roughly 20× the equidispersed-Poisson value — which a deterministically
modulated NHPP cannot reproduce (it is Poisson-equidispersed conditional
on λ(t)).

Sprint-intensity mixing distribution
------------------------------------
The mixing law for Λ_d is a build-time choice. Per Model QA Strong-1
(pre-Phase-2 review): the *mechanism class* (Cox / doubly-stochastic) is
trace-anchored, but the *Gamma* mixing distribution is a conjugacy
default — it is NOT discriminable from log-normal at n≈12-28 daily
counts. The engine therefore carries TWO mixing arms:

- ``"gamma"`` — PRIMARY. Gamma-mixed Poisson day-counts ⇒ a
  negative-binomial daily marginal, so the calibration-note §3.4
  fallback (a bare NB marginal) nests cleanly.
- ``"lognormal"`` — the §4.3 SENSITIVITY arm. Same mechanism class, a
  heavier-tailed mixing law; carried so tail-shape sensitivity is
  explicit rather than buried in a default.

The arm is selected by ``NHPPIntensityParameters.overdispersion_mechanism``:
``"cox"`` ⇒ Gamma-mixed (primary); ``"cox_lognormal"`` ⇒ log-normal-mixed
(sensitivity); ``"negative_binomial"`` ⇒ the §3.4 NB-marginal fallback
(equivalent to the Gamma-mixed Cox marginal without the within-day burst
layer). Any of the three is a CALIBRATED mechanism; an empty string is
uncalibrated and raises ``NHPPCalibrationError`` at construction.

The five λ(t) modulation slots (calibration note §4)
----------------------------------------------------
1. DIURNAL_WEEKDAY_CYCLE — weekday weight × two-peak diurnal envelope.
2. BURSTINESS_OVERDISPERSION — the Cox sprint-intensity layer itself
   (calibration note §4.2: burstiness and overdispersion are two
   readouts of one mechanism, not a separate functional form).
3. EVENT_DRIVEN_SPIKES — a sparse Bernoulli day-marker × heavy-tail
   multiplier; in the Cox framing, the upper tail of Λ_d.
4. MONTH_END_SEASONALITY — a multiplicative end-of-month bump; its
   *magnitude* is the proxy-bracket-pending OPEN item (calibration
   note §4.4) and defaults to a no-op (magnitude 0) until pinned.
5. SECULAR_WORKLOAD_DRIFT — a log-linear baseline-λ trend over the
   panel window.

Q ⊥ FX (spec §6.4)
------------------
In the primary specification Q is generated **independently of FX**:
``__call__`` accepts the real FX path but the simulated Q counts never
condition on it (calibration note §6). Two runs against different FX
paths at the same seed produce identical Q. ``cost = Q × $0.01 × FX``
is the only place the real FX path enters.

Discipline
----------
``modules``-tier: a frozen-dataclass stateless callable + free pure
functions; no mutable state, no imports from ``..utils``. All randomness
is drawn from a freshly seeded ``numpy.random.Generator`` per call so the
engine is referentially transparent in ``(params, …, seed)``.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import numpy as np

from simulations.e10_gsps._errors import NHPPCalibrationError
from simulations.e10_gsps.types import (
    CostStreamTrajectory,
    LambdaModulationForm,
    LambdaModulationSpec,
    NHPPIntensityParameters,
)

# ── Per-query x402 price (spec §4.2 — verified flat $0.01 USDC) ──────────
_X402_PRICE_USDC: float = 0.01

# ── Calibration-note-anchored modulation constants ──────────────────────
#
# These are the functional-form parameters LOCKED in the E10.1 calibration
# note §4. They are engine defaults; a calibrated ``LambdaModulationSpec``
# may override the per-modulation ``params`` tuple, but the calibrated
# Q-process used by Phase 2.4 / Phase 3 runs on these note-anchored values.

# §4.1 modulation 1 — weekday/weekend split. Trace: ~95% weekday
# (centre 62/63 = 98.4%; bracket 142/151 = 94%).
_WEEKEND_WEIGHT: float = 0.05

# §4.1 modulation 1 — two-peak diurnal envelope. Trace diurnal_utc shows
# bimodal clustering at UTC 11-12h and 21-22h. A day's arrivals are
# allocated across 24 hour-blocks by a sum of two Gaussian bumps; the
# engine aggregates intra-day to a daily count, so the diurnal shape
# affects only the within-day allocation, never the daily total.
_DIURNAL_PEAKS_UTC: tuple[float, float] = (11.5, 21.5)
_DIURNAL_PEAK_SD: float = 1.5

# §3 / §4.2 — Cox sprint-intensity. The daily variance-to-mean ratio in
# the trace is ≈ 20 (centre 20.6 / bracket 19.8, sample variance;
# population variance 18.9 / 19.1 — same conclusion). Per Model QA
# Strong, VMR ≈ 20 is the CENTRE of a swept range, not a hard target;
# ``vmr_target`` is a constructor parameter so the §4.3 surface can sweep
# it. The Gamma sprint-intensity has mean 1 (so it does not shift the
# envelope) and shape k chosen so the day-count marginal hits the target
# VMR: a Gamma(k, 1/k)-mixed Poisson(μ) has VMR = 1 + μ/k.
_VMR_TARGET_DEFAULT: float = 20.0

# §4.3 modulation 3 — event-driven spikes. Sparse Bernoulli day-marker:
# the trace shows ~2 spike days against ~10 background days. The spike
# multiplier is heavy-tailed; in the Cox framing it is the upper tail of
# the sprint-intensity, realised as a whole-day multiplier.
_SPIKE_DAY_PROB: float = 0.10
_SPIKE_MULTIPLIER_MEAN: float = 5.0

# Variance of the mean-1 background sprint-intensity component (most
# days). A mild dispersion: the background carries the §6.3-item-2
# within-day burstiness, while the heavy spike component (above) carries
# the §6.3-item-3 event spikes. The overall mixture variance is then
# affine-rescaled to the VMR target, so this is a SHAPE constant, not a
# magnitude — the background/spike split it encodes is the structured-
# overdispersion shape the trace shows.
_BACKGROUND_VAR: float = 0.5

# §4.5 modulation 5 — log-linear secular drift. Bracket weekly counts
# rise monotonically 2→6→25→44→74 over 5 weeks. The drift is parametrised
# as a gentle log-linear trend on baseline λ across the panel window;
# ``drift_log_slope_per_month`` is the per-month log-slope and defaults to
# a mild positive trend. Over a single simulated month the drift is held
# at the month's mid-point value (the within-month change is negligible).
_DRIFT_LOG_SLOPE_PER_MONTH_DEFAULT: float = 0.0

# §4.4 modulation 4 — month-end seasonality. The bump SHAPE is
# pre-committed; its MAGNITUDE is the proxy-bracket-pending OPEN
# calibration item. Default 0.0 ⇒ a no-op bump until the proxy research
# of plan task 2.2 pins it (or PARTIAL fires per CORR-E10P-8).
_MONTH_END_BUMP_MAGNITUDE_DEFAULT: float = 0.0
_MONTH_END_BUMP_DAYS: int = 3

# ── Trace-anchored calibration constants (E10.1 calibration note §2) ────
#
# The CENTRE of the Q-volume range, set by the user's own observed
# data-query logs (calibration note §1.2 / §2): ~60-130 priceable
# queries/month in sprint-driven months. The mid-band centre ⇒ a baseline
# arrival rate of ~95 queries/month. lambda_0 is queries/HOUR at the
# reference block; with the weekday/weekend envelope a 30-day month
# integrates to roughly lambda_0 × 24 × (≈22 weekday-equivalent days),
# so lambda_0 ≈ 95 / (24 × 22) ≈ 0.18 reproduces the ~95/mo centre.
_CALIBRATED_LAMBDA_0: float = 0.18

# Q_high — pinned off the $399 Dune-Plus price (spec §2.3): the volume at
# which pay-per-query cost crosses the flat subscription. NOT trace-derived.
_CALIBRATED_Q_HIGH: float = 39_900.0

# Q_low — the §2.4 qualitative-limit threshold. OPEN / proxy-bracket-
# pending (calibration note §5): the metadata-only trace cannot observe
# the qualitative free-tier deficiencies §2.4 keys on. Carried as NaN ⇒
# "unpinned"; a calibrated value is supplied only once plan task 2.2's
# proxy research pins it (or PARTIAL fires per CORR-E10P-8).
_Q_LOW_UNPINNED: float = float("nan")

_PRIMARY_MECHANISM: str = "cox"
_SENSITIVITY_MECHANISM: str = "cox_lognormal"
_FALLBACK_MECHANISM: str = "negative_binomial"
_VALID_MECHANISMS: frozenset[str] = frozenset(
    {_PRIMARY_MECHANISM, _SENSITIVITY_MECHANISM, _FALLBACK_MECHANISM}
)


def _validate_calibrated(params: NHPPIntensityParameters) -> None:
    """Assert ``params`` is a CALIBRATED parameter set fit to run.

    A calibrated set has (a) all five §6.3 λ(t) modulation slots present
    and ``locked``, and (b) a recognised, non-empty overdispersion
    mechanism. An uncalibrated set — empty mechanism, unlocked forms — is
    a Phase-0 stub state and must never reach a simulation run.

    Args:
        params: The NHPP intensity-parameter container under test.

    Raises:
        NHPPCalibrationError: ``params`` is uncalibrated — the
            overdispersion mechanism is empty or unrecognised, any λ(t)
            modulation slot is unlocked, or the five §6.3 slots are not
            all present. There is no default-priors escape hatch (spec
            §7 field 7a).
    """
    mech = params.overdispersion_mechanism
    if not mech:
        raise NHPPCalibrationError(
            "overdispersion mechanism is unset — an uncalibrated NHPP "
            "parameter set cannot drive a simulation run (calibration "
            "note §3; plan task 2.3a). Lock 'cox' (Gamma-mixed primary), "
            "'cox_lognormal' (sensitivity arm), or 'negative_binomial' "
            "(§3.4 fallback)."
        )
    if mech not in _VALID_MECHANISMS:
        raise NHPPCalibrationError(
            f"unrecognised overdispersion mechanism {mech!r}; the E10.1 "
            f"calibration note locks one of {sorted(_VALID_MECHANISMS)}"
        )
    forms_present = {m.form for m in params.modulations}
    if forms_present != set(LambdaModulationForm):
        missing = set(LambdaModulationForm) - forms_present
        raise NHPPCalibrationError(
            f"NHPP parameter set is missing λ(t) modulation slots "
            f"{sorted(f.name for f in missing)}; the engine wires all "
            f"five §6.3 modulations (calibration note §4)"
        )
    unlocked = tuple(m.form.name for m in params.modulations if not m.locked)
    if unlocked:
        raise NHPPCalibrationError(
            f"λ(t) modulation slots {sorted(unlocked)} are not locked — "
            f"each functional form must be decision-cited and locked in "
            f"the E10.1 calibration note (plan task 2.3) before any run"
        )


def _weekday_weight(weekday: int) -> float:
    """Multiplicative day-type weight for ``weekday`` (Mon=0 … Sun=6).

    Weekdays carry weight 1.0; weekends carry ``_WEEKEND_WEIGHT`` — the
    calibration-note §4.1 ~95%/~5% weekday/weekend split.
    """
    return 1.0 if weekday < 5 else _WEEKEND_WEIGHT


def _month_end_weight(
    day_of_month: int, days_in_month: int, bump_magnitude: float
) -> float:
    """Multiplicative month-end seasonality weight (modulation 4).

    Returns ``1 + bump_magnitude`` for the final ``_MONTH_END_BUMP_DAYS``
    days of the month and ``1.0`` otherwise. With the default
    ``bump_magnitude = 0.0`` (the proxy-bracket-pending OPEN item) this is
    a no-op until plan task 2.2's proxy research pins the magnitude.
    """
    if day_of_month > days_in_month - _MONTH_END_BUMP_DAYS:
        return 1.0 + bump_magnitude
    return 1.0


def _drift_weight(month_index: int, log_slope_per_month: float) -> float:
    """Multiplicative secular-drift weight for ``month_index`` (modulation 5).

    A log-linear trend: ``exp(log_slope_per_month × month_index)``. With
    the default zero slope this is a no-op; a positive slope reproduces
    the bracket's monotone weekly rise.
    """
    return float(np.exp(log_slope_per_month * month_index))


def diurnal_hourly_envelope() -> tuple[float, ...]:
    """The modulation-1 two-peak diurnal intensity envelope (24 UTC hours).

    A sum of two Gaussian bumps centred on the calibration-note §4.1
    UTC-morning and UTC-evening working blocks, normalised to sum to 1.
    The two-peak shape (not a single Gaussian) is the locked modulation-1
    form: the trace ``diurnal_utc`` buckets show bimodal clustering at
    UTC 11-12h and 21-22h.

    The engine's daily-grid aggregation (plan task 3.0) collapses the
    within-day hour structure, so this envelope shapes only the intra-day
    arrival texture; it is exposed as a pure function so the calibration
    notebook (plan task 2.4) can plot the locked diurnal form and the
    Phase-0.5 harness can exercise the modulation-1 slot.
    """
    hours = np.arange(24, dtype=float)
    envelope = np.zeros(24, dtype=float)
    for peak in _DIURNAL_PEAKS_UTC:
        envelope += np.exp(-0.5 * ((hours - peak) / _DIURNAL_PEAK_SD) ** 2)
    probs = envelope / envelope.sum()
    return tuple(float(x) for x in probs)


def _sprint_intensity(
    rng: np.random.Generator,
    n_days: int,
    *,
    mechanism: str,
    mu: float,
    vmr_target: float,
) -> np.ndarray:
    """Draw the per-day Cox sprint-intensity multiplier Λ_d.

    Λ_d is the doubly-stochastic layer (calibration note §3.3): a random
    mean-1 multiplier on the deterministic envelope. It is a TWO-component
    mixture — a moderate-variance *background* draw on most days, and a
    heavy-tailed *spike* draw on a sparse Bernoulli fraction of days.
    Per the calibration note, modulations 2 (burstiness/overdispersion)
    and 3 (event-driven spikes) are **two readouts of one mechanism**
    (§4.2 / §4.3): the event spike is the upper tail of the *same*
    sprint-intensity process, NOT an independent multiplier. The two
    components are therefore drawn together here and the whole mixture is
    the single overdispersion mechanism.

    The mixture is rescaled so it has mean approximately 1 (it shifts the
    deterministic envelope, not its level) and the day-count marginal
    *approximately* pins to ``vmr_target``: for a mean-μ Poisson day-count
    mixed by a mean-1 multiplier of variance σ², the day-count VMR is
    ``1 + μ·σ²``, so the target pins σ² = (VMR−1)/μ.

    Two reasons the realized daily VMR only *approximately* hits the
    target (review M-1 / M-2):

    - The day-count marginal is a mixture over heterogeneous λ_det(d)
      (weekday vs weekend, drift, month-end), so the realized daily VMR
      also carries the between-day envelope variance and is not exactly
      ``1 + μ̄·σ²``. ``vmr_target`` is therefore a swept-range *centre*
      (calibration note §0-A2), not a hard target.
    - The post-rescale ``np.clip(..., 1e-6, None)`` floor truncates the
      rescaled lower tail; for large ``scale`` (high ``vmr_target``, low
      μ) this lifts the realized mean fractionally above 1, so Λ_d's mean
      is not *exactly* 1. The effect is small at the calibrated
      μ≈4 / VMR≈20 corner and grows in the §4.3 high-VMR sweep corner.

    Args:
        rng: The per-call seeded generator.
        n_days: Number of calendar days to draw.
        mechanism: ``"cox"`` ⇒ Gamma background (primary); ``"cox_lognormal"``
            ⇒ log-normal background (Model QA Strong-1 sensitivity arm);
            ``"negative_binomial"`` ⇒ Gamma background (the §3.4 fallback
            shares the Gamma marginal).
        mu: The mean deterministic day-count μ (queries/day) — the level
            the multiplier rescales the day-count VMR against.
        vmr_target: The target daily variance-to-mean ratio — VMR ≈ 20 is
            the swept-range centre (Model QA Strong), not a hard target.

    Returns:
        A length-``n_days`` array of strictly positive mean-1 multipliers
        whose variance pins the day-count marginal to ``vmr_target``.
    """
    if n_days == 0:
        return np.zeros(0, dtype=float)

    # Raw two-component mixture, BEFORE rescaling: most days draw a unit-mean
    # background; a sparse Bernoulli fraction draw a heavy-tailed spike with
    # mean _SPIKE_MULTIPLIER_MEAN. Background dispersion is a mild fixed
    # shape; the spike component contributes the heavy upper tail.
    #
    # Background: mean 1, variance _BACKGROUND_VAR (Gamma shape 2 scale 0.5
    # OR the equal-variance log-normal). Spike: Exponential(mean = M) ⇒
    # mean M, variance M². The mixture (spike w.p. p) has the analytic
    # moments below; rescaling uses these CONSTANTS, not a noisy per-month
    # sample estimate — so the day-count VMR pins to the target stably.
    p = _SPIKE_DAY_PROB
    bg_mean, bg_var = 1.0, _BACKGROUND_VAR
    sp_mean = _SPIKE_MULTIPLIER_MEAN
    sp_var = _SPIKE_MULTIPLIER_MEAN**2
    mix_mean = (1.0 - p) * bg_mean + p * sp_mean
    # Var of a 2-component mixture: weighted within-component var plus the
    # between-component spread of the component means.
    mix_var = (
        (1.0 - p) * (bg_var + bg_mean**2)
        + p * (sp_var + sp_mean**2)
        - mix_mean**2
    )

    spike_marker = rng.random(n_days) < p
    if mechanism in (_PRIMARY_MECHANISM, _FALLBACK_MECHANISM):
        # Gamma background, mean 1, variance _BACKGROUND_VAR (Gamma-mixed
        # Poisson ⇒ NB marginal — the §3.4 fallback nests cleanly).
        bg_shape = bg_mean**2 / bg_var
        background = rng.gamma(
            shape=bg_shape, scale=bg_var / bg_mean, size=n_days
        )
    else:
        # Log-normal background, same mean/variance — the Model QA
        # Strong-1 heavier-tailed sensitivity arm.
        s2 = float(np.log1p(bg_var / bg_mean**2))
        background = rng.lognormal(
            mean=float(np.log(bg_mean)) - 0.5 * s2,
            sigma=float(np.sqrt(s2)),
            size=n_days,
        )
    spike = rng.exponential(scale=sp_mean, size=n_days)
    raw = np.where(spike_marker, spike, background)

    # Normalise to mean 1 (shifts the envelope, not its level) by the
    # ANALYTIC mixture mean, then affine-rescale around 1 to the variance
    # that pins the day-count marginal: VMR = 1 + μ·σ², so σ² = (VMR−1)/μ.
    centred = raw / mix_mean
    centred_var = mix_var / mix_mean**2
    if centred_var <= 1e-12:
        return np.clip(centred, 1e-6, None)
    target_sigma2 = max((vmr_target - 1.0) / max(mu, 1e-9), 1e-9)
    scale = float(np.sqrt(target_sigma2 / centred_var))
    # Affine rescale around mean 1 preserves the mean and the mixture
    # SHAPE (background-vs-spike split) while setting the variance.
    rescaled = 1.0 + (centred - 1.0) * scale
    # Floor at 1e-6 to keep Λ_d strictly positive (a non-positive Poisson
    # rate is invalid). This truncates the rescaled lower tail and so
    # lifts the realized mean fractionally above 1 — an APPROXIMATION,
    # negligible at the calibrated μ≈4 / VMR≈20 corner but growing in the
    # §4.3 high-VMR sweep corner (review M-2).
    return np.clip(rescaled, 1e-6, None)


def _simulate_day_counts(
    rng: np.random.Generator,
    *,
    params: NHPPIntensityParameters,
    n_days: int,
    weekdays: tuple[int, ...],
    days_in_month: tuple[int, ...],
    day_of_month: tuple[int, ...],
    month_index: int,
    vmr_target: float,
    drift_log_slope_per_month: float,
    month_end_bump_magnitude: float,
) -> tuple[int, ...]:
    """Simulate the Cox doubly-stochastic NHPP daily query counts.

    For each calendar day d:
      λ_det(d) = λ_0·24 × weekday_weight × month_end_weight × drift_weight
      Λ_d      ~ mean-1 two-component sprint-intensity (background + spike)
      Q_d      ~ Poisson( λ_det(d) × Λ_d )

    The Cox sprint-intensity Λ_d is the SINGLE overdispersion mechanism:
    its background component carries the §6.3-item-2 burstiness and its
    sparse heavy spike component carries the §6.3-item-3 event spikes —
    two readouts of one mechanism (calibration note §4.2 / §4.3), not two
    independent multipliers. Λ_d inflates the day-count variance above the
    mean — the structured overdispersion the trace shows (VMR ≈ 20).
    Λ_d ⊥ FX by construction (no FX argument enters here).

    Returns:
        The per-day integer query counts (length ``n_days``).
    """
    # Baseline deterministic day-count: lambda_0 is queries/hour at the
    # reference block; a day integrates to lambda_0 * 24 at the reference
    # weekday with no bump and no drift.
    base_day = params.lambda_0 * 24.0

    weekday_w = np.array([_weekday_weight(wd) for wd in weekdays])
    month_end_w = np.array(
        [
            _month_end_weight(dom, dim, month_end_bump_magnitude)
            for dom, dim in zip(day_of_month, days_in_month, strict=True)
        ]
    )
    drift_w = _drift_weight(month_index, drift_log_slope_per_month)

    lambda_det = base_day * weekday_w * month_end_w * drift_w

    mu = float(lambda_det.mean()) if n_days else 0.0
    sprint = _sprint_intensity(
        rng,
        n_days,
        mechanism=params.overdispersion_mechanism,
        mu=mu,
        vmr_target=vmr_target,
    )

    rate = lambda_det * sprint
    counts = rng.poisson(np.clip(rate, 0.0, None))
    return tuple(int(c) for c in counts)


def _simulate_calendar_month(
    rng: np.random.Generator,
    *,
    params: NHPPIntensityParameters,
    year: int,
    month: int,
    vmr_target: float,
    drift_log_slope_per_month: float,
    month_end_bump_magnitude: float,
) -> tuple[int, ...]:
    """Simulate one calendar month's per-day Cox NHPP counts.

    The single shared calendar-walk + ``_simulate_day_counts`` call site:
    derives the month's calendar facts and the panel-epoch month index
    (months since the 2023-01 panel-window floor), then draws the daily
    counts. Both ``NHPPSimulationEngineModule.__call__`` and
    ``simulate_monthly_query_counts`` route through here so the two code
    paths cannot drift (review M-3).

    Args:
        rng: The per-cell seeded generator.
        params: The calibrated NHPP intensity-parameter set.
        year: Calendar year of the simulated month.
        month: Calendar month (1-12).
        vmr_target: The daily variance-to-mean-ratio centre.
        drift_log_slope_per_month: The modulation-5 secular-drift log-slope.
        month_end_bump_magnitude: The modulation-4 month-end bump magnitude.

    Returns:
        The per-day integer query counts for the month.
    """
    n_days, weekdays, days_in_month, day_of_month = _calendar_facts(
        year, month
    )
    # month_index keys the secular drift to a panel epoch — months since
    # 2023-01 (the panel-window era floor).
    month_index = (year - 2023) * 12 + (month - 1)
    return _simulate_day_counts(
        rng,
        params=params,
        n_days=n_days,
        weekdays=weekdays,
        days_in_month=days_in_month,
        day_of_month=day_of_month,
        month_index=month_index,
        vmr_target=vmr_target,
        drift_log_slope_per_month=drift_log_slope_per_month,
        month_end_bump_magnitude=month_end_bump_magnitude,
    )


def _calendar_facts(
    year: int, month: int
) -> tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    """Return (n_days, weekdays, days_in_month, day_of_month) for a month.

    ``weekdays`` is Mon=0…Sun=6 per calendar day; ``days_in_month`` repeats
    the month length; ``day_of_month`` is 1…n_days. Pure calendar arithmetic.
    """
    n_days = calendar.monthrange(year, month)[1]
    weekdays = tuple(
        calendar.weekday(year, month, d) for d in range(1, n_days + 1)
    )
    return (
        n_days,
        weekdays,
        tuple([n_days] * n_days),
        tuple(range(1, n_days + 1)),
    )


@dataclass(frozen=True, slots=True)
class NHPPSimulationEngineModule:
    """Stateless callable — the R6 NHPP query-workflow simulation engine.

    Generates the representative-analyst Q-process (a Cox / doubly-
    stochastic NHPP) against a real central-bank FX path, emitting a
    per-(currency, month) ``CostStreamTrajectory``. Q is the ONLY
    generated quantity; the FX path is real and is consumed unchanged
    (spec §6.4 — Q ⊥ FX in the primary).

    Satisfies the ``types.NHPPSimulationEngine`` Protocol.

    Attributes:
        params: The CALIBRATED NHPP intensity-parameter set (the five
            §6.3 λ(t) forms locked, an overdispersion mechanism chosen).
            ``__post_init__`` rejects an uncalibrated set.
        vmr_target: The daily variance-to-mean-ratio centre for the Cox
            sprint-intensity layer — VMR ≈ 20 is the swept-range centre
            (Model QA Strong), exposed so the §4.3 surface can sweep it.
        drift_log_slope_per_month: The modulation-5 secular-drift log-slope.
        month_end_bump_magnitude: The modulation-4 month-end bump
            magnitude — the proxy-bracket-pending OPEN item; default 0.0
            (a no-op) until plan task 2.2's proxy research pins it.
    """

    params: NHPPIntensityParameters
    vmr_target: float = _VMR_TARGET_DEFAULT
    drift_log_slope_per_month: float = _DRIFT_LOG_SLOPE_PER_MONTH_DEFAULT
    month_end_bump_magnitude: float = _MONTH_END_BUMP_MAGNITUDE_DEFAULT

    def __post_init__(self) -> None:
        """Reject an uncalibrated parameter set at construction.

        Raises:
            NHPPCalibrationError: ``params`` is uncalibrated (see
                ``_validate_calibrated``).
        """
        _validate_calibrated(self.params)

    def __call__(
        self,
        params: NHPPIntensityParameters,
        currency: str,
        year: int,
        month: int,
        daily_fx_rate: tuple[float, ...],
    ) -> CostStreamTrajectory:
        """Simulate one (currency, month) cost-stream trajectory.

        The daily query counts are a Cox doubly-stochastic NHPP draw; the
        cost stream is ``cost_d = Q_d × $0.01 × FX_d`` against the real
        FX path. Q is generated independently of FX: ``daily_fx_rate``
        enters ONLY the cost product, never the arrival process.

        The simulation seed is derived deterministically from
        ``(currency, year, month)`` so a given (currency, month) cell is
        reproducible (Tier-3 round-trip, plan task 3.4) and so two runs
        against different FX paths but the same cell produce identical Q.

        Args:
            params: The calibrated NHPP parameter set for this run. Must
                match the constructor ``params`` (the engine is anchored
                to one calibrated set; a divergent set is a caller bug).
            currency: The panel currency code (COP / BRL / EUR / GBP / NGN).
            year: Calendar year of the simulated month.
            month: Calendar month (1-12).
            daily_fx_rate: The REAL central-bank daily FX path for the
                month — one rate per FX trading day, in order. In a Phase-3
                panel cell this is the month's full daily index; if it is
                shorter (e.g. FX trading days < calendar days, or a
                deliberately short test path), the emitted trajectory is
                aligned to the FX index — the Q counts are simulated on the
                full calendar grid and truncated to the FX length for the
                cost product. The cost product is the ONLY place FX enters
                (spec §6.4 — Q ⊥ FX), so a different FX path never changes
                the simulated Q.

        Returns:
            A ``CostStreamTrajectory`` whose daily Q counts, FX path, and
            cost product share one daily index (length = len(daily_fx_rate),
            or the calendar length when FX covers the full month).

        Raises:
            NHPPCalibrationError: ``params`` is uncalibrated, OR the FX
                path is longer than the month's calendar length (an FX
                index that over-runs the month is a caller bug — the
                simulated month has no Q to align past its last day).
        """
        _validate_calibrated(params)
        n_days = calendar.monthrange(year, month)[1]
        if len(daily_fx_rate) > n_days:
            raise NHPPCalibrationError(
                f"FX path for {currency} {year}-{month:02d} has "
                f"{len(daily_fx_rate)} daily rates but the month has only "
                f"{n_days} calendar days; the FX index over-runs the "
                f"simulated month (plan task 3.0 common differencing grid)"
            )
        seed = _cell_seed(currency, year, month)
        rng = np.random.default_rng(seed)
        counts = _simulate_calendar_month(
            rng,
            params=params,
            year=year,
            month=month,
            vmr_target=self.vmr_target,
            drift_log_slope_per_month=self.drift_log_slope_per_month,
            month_end_bump_magnitude=self.month_end_bump_magnitude,
        )
        # Align the trajectory to the FX index: Q is simulated on the full
        # calendar grid, then the trajectory's three series share the FX
        # length (the common differencing grid of plan task 3.0). When FX
        # covers the full month nothing truncates.
        fx_len = len(daily_fx_rate)
        # ``counts[:fx_len]`` yields ``()`` when ``fx_len == 0`` — the
        # documented empty-FX-path behaviour. No conditional needed: a
        # ``counts if fx_len else counts`` guard would keep the FULL
        # calendar counts on an empty FX path and crash the ``strict=True``
        # zip below (review I-1).
        aligned_counts = counts[:fx_len]
        aligned_fx = tuple(daily_fx_rate)
        daily_cost = tuple(
            q * _X402_PRICE_USDC * fx
            for q, fx in zip(aligned_counts, aligned_fx, strict=True)
        )
        return CostStreamTrajectory(
            currency=currency,
            year=year,
            month=month,
            daily_query_counts=aligned_counts,
            daily_fx_rate=aligned_fx,
            daily_cost=daily_cost,
            seed=seed,
        )


def _cell_seed(currency: str, year: int, month: int) -> int:
    """Derive a deterministic per-(currency, month) simulation seed.

    A stable hash of the cell identity so the same (currency, month)
    cell reproduces bit-stably across runs (plan task 3.4) and is
    independent of the FX path (spec §6.4 — Q ⊥ FX).
    """
    base = sum(ord(ch) for ch in currency)
    return (base * 1_000_000) + (year * 100) + month


def simulate_monthly_query_counts(
    *,
    params: NHPPIntensityParameters,
    n_months: int,
    seed: int,
) -> tuple[int, ...]:
    """Simulate a series of monthly-aggregate Q counts.

    Runs the Cox doubly-stochastic NHPP for ``n_months`` consecutive
    months and returns the per-month total query count. The doubly-
    stochastic sprint-intensity layer makes the *monthly-aggregate* Q
    overdispersed relative to a pure-Poisson equidispersed null — a pure
    NHPP, even with a deterministically modulated λ(t), is equidispersed
    conditional on the rate and cannot produce this (calibration note
    §3.1, plan CORR-E10P-2 / task 2.3a).

    Months are walked forward from 2024-01 so the secular-drift term
    (modulation 5) and the calendar structure vary month to month, as in
    a real panel.

    Args:
        params: The calibrated NHPP intensity-parameter set.
        n_months: Number of consecutive months to simulate (>= 1).
        seed: The master seed; each month draws from a deterministic
            child stream so the whole series is reproducible.

    Returns:
        A length-``n_months`` tuple of monthly-aggregate query counts.

    Raises:
        NHPPCalibrationError: ``params`` is uncalibrated.
        ValueError: ``n_months`` is not a positive integer.
    """
    _validate_calibrated(params)
    if n_months < 1:
        raise ValueError(f"n_months must be >= 1, got {n_months}")
    master = np.random.default_rng(seed)
    out: list[int] = []
    base_year, base_month = 2024, 1
    for k in range(n_months):
        year = base_year + (base_month - 1 + k) // 12
        month = (base_month - 1 + k) % 12 + 1
        # A fresh child generator per month — reproducible, independent.
        child = np.random.default_rng(master.integers(0, 2**63 - 1))
        # Routes through the shared calendar-walk; this aggregate helper
        # deliberately runs the engine DEFAULTS (no engine instance is in
        # scope here) — see review M-3.
        counts = _simulate_calendar_month(
            child,
            params=params,
            year=year,
            month=month,
            vmr_target=_VMR_TARGET_DEFAULT,
            drift_log_slope_per_month=_DRIFT_LOG_SLOPE_PER_MONTH_DEFAULT,
            month_end_bump_magnitude=_MONTH_END_BUMP_MAGNITUDE_DEFAULT,
        )
        out.append(sum(counts))
    return tuple(out)


def calibrated_intensity_parameters(
    *,
    mechanism: str = _PRIMARY_MECHANISM,
    q_low: float = _Q_LOW_UNPINNED,
) -> NHPPIntensityParameters:
    """Return the E10.1 trace-anchored calibrated NHPP parameter set.

    This is the canonical calibrated Q-process the Phase-2.4 calibration
    notebook and the Phase-3 panel run against — the centre of the
    §6.2 NON-FANTASY anchor (calibration note §2: ~60-130 priceable
    queries/month). All five §6.3 λ(t) modulation slots are present and
    locked, each with its calibration-note-§4 functional form.

    Args:
        mechanism: The overdispersion mechanism — ``"cox"`` (Gamma-mixed
            primary, the default), ``"cox_lognormal"`` (the Model QA
            Strong-1 log-normal-mixing sensitivity arm), or
            ``"negative_binomial"`` (the calibration-note §3.4 fallback).
        q_low: The §2.4 qualitative-limit threshold. Defaults to NaN —
            ``Q_low`` is the proxy-bracket-pending OPEN calibration item
            (calibration note §5); a real value is supplied only once
            plan task 2.2's proxy research pins it. A NaN ``q_low`` is a
            visible "unpinned" marker, never a fabricated default.

    Returns:
        A CALIBRATED ``NHPPIntensityParameters`` — ready to construct an
        ``NHPPSimulationEngineModule``.

    Raises:
        NHPPCalibrationError: ``mechanism`` is not a recognised locked
            mechanism (raised by the engine constructor downstream; the
            value is validated there).
    """
    locked = tuple(
        LambdaModulationSpec(
            form=form,
            functional_form=_CALIBRATED_FORM_NAMES[form],
            params=(),
            locked=True,
        )
        for form in LambdaModulationForm
    )
    return NHPPIntensityParameters(
        lambda_0=_CALIBRATED_LAMBDA_0,
        modulations=locked,
        overdispersion_mechanism=mechanism,
        q_low=q_low,
        q_high=_CALIBRATED_Q_HIGH,
        qfx_independent=True,
    )


# Calibration-note §4 — the locked functional form of each modulation.
_CALIBRATED_FORM_NAMES: dict[LambdaModulationForm, str] = {
    LambdaModulationForm.DIURNAL_WEEKDAY_CYCLE: (
        "weekday_weight_x_two_peak_diurnal"
    ),
    LambdaModulationForm.BURSTINESS_OVERDISPERSION: (
        "cox_gamma_mixed_sprint_intensity"
    ),
    LambdaModulationForm.EVENT_DRIVEN_SPIKES: (
        "sprint_intensity_upper_tail_spike_mixture"
    ),
    LambdaModulationForm.MONTH_END_SEASONALITY: (
        "end_of_month_bump_magnitude_OPEN"
    ),
    LambdaModulationForm.SECULAR_WORKLOAD_DRIFT: "log_linear_baseline_drift",
}


__all__ = [
    "NHPPSimulationEngineModule",
    "calibrated_intensity_parameters",
    "diurnal_hourly_envelope",
    "simulate_monthly_query_counts",
]
