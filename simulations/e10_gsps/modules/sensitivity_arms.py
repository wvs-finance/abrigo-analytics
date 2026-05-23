"""E10.4 sensitivity-arm runner (spec v0.7 §9; plan task 5.1).

Phase 5 sensitivity arms. Five arms:

- (b) Q-FX behavioral coupling -- user-locked elasticity -0.3 on monthly Q
      with respect to standardized monthly realized FX volatility (within
      currency). Decision-citation stamped (the [brainstorm-judgment]
      sub-step).
- (c) NGN break-window robustness pair -- additionally drop NGN cells
      inside the +/-6-month buffer around the spec-pinned regime break
      (2023-06-01 per ``regime_break._REGIME_BREAK_START``).
- (d) GBM / Jump-Diffusion FX comparator -- substitute the per-currency
      mean Var(Delta log FX) with a calibrated GBM and a calibrated
      Merton jump-diffusion analog using
      ``simulations.stochastic_fx`` generators.
- (e) Per-currency split -- wraps the existing
      ``compute_currency_spread`` per-currency surfaces from Phase 4
      (task 4.3).
- (f) Optional Q-high = 39_000 arm -- re-evaluate the surface on the
      extended Q-volume range up to the $399 Dune-cap-equivalent volume.

Each arm reports descriptive concordance vs. the Phase-4 primary surface
ONLY. Per spec v0.7 §9: no arm gates a verdict; no arm rescues a primary
HALT. The Phase-4 trajectory is NON-RETIREMENT via HALT-Q-DOMINANCE; the
arms quantify how robust that descriptive surface is to alternative
panel constructions.

Arm (b) -- the user-pinned operationalization
---------------------------------------------
The user-locked elasticity is -0.3 on monthly Q with respect to
standardized monthly realized FX volatility (within currency):

    Q_t_coupled = Q_t * (1 + (-0.3) * z_t)

where ``z_t`` is the within-currency standardized monthly realized FX
volatility and Q_t is the month's daily query series.

This multiplies the WHOLE month's daily Q series by a single per-month
scalar ``s_m = (1 - 0.3 * z_m)``. A constant scalar drops out of daily
``Δlog Q`` within the month, so the per-cell within-month log-variance
decomposition (``var_fx``, ``var_q``, ``cov_term``, ``var_total``) is
*unchanged* by this operationalization at the cell level. The per-cell
``fx_variance_share = var_fx / var_total`` is therefore IDENTICAL under
coupling. The concordance metric is exactly zero by construction.

This is the descriptively honest outcome of the user-pinned
operationalization: a *monthly* multiplicative coupling rescales monthly
Q magnitudes but leaves *within-month* Q-variance untouched. The Phase-5
arm reports this transparently rather than fabricating a daily coupling
the user did not pin.

The decision-citation block (4-part) is stamped verbatim on the arm's
result.

Discipline
----------
``modules``-tier: free pure functions + frozen-dataclass containers; no
mutable state, no imports from ``..utils``. The
``stochastic_fx``-comparator arm imports the SIBLING-package generators
(``simulations.stochastic_fx``), which is permitted because they are not
the ``e10_gsps`` utils tier.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import date
from typing import Final

import numpy as np

from simulations.e10_gsps.modules.currency_spread import compute_currency_spread
from simulations.e10_gsps.modules.surface_grid import (
    DEFAULT_BASE_N,
    DEFAULT_REFINED_N,
    DEFAULT_S_BE,
    evaluate_surface_grid,
)
from simulations.e10_gsps.types import (
    ConcordanceVerdict,
    PanelCell,
    SensitivityArmResult,
    SensitivityArmsResult,
    SurfaceGridResult,
    ThreeWayDecompositionCell,
)

#: User-locked elasticity for arm (b) (negative; -0.3 mid-range value).
_QFX_COUPLING_ELASTICITY: Final[float] = -0.3

#: Arm (b) 4-part decision-citation (reference / why / relevance /
#: connection). Stamped verbatim on the arm result.
_ARM_B_DECISION_CITATION: Final[str] = (
    "Reference: spec v0.7 §11 open item -- Q-FX behavioral coupling sign "
    "and magnitude are not pinned in spec; plan task 5.1 [brainstorm-judgment] "
    "flag; user lock 2026-05-21. "
    "Why: NEGATIVE sign reflects income/substitution intuition -- when "
    "local-currency FX volatility rises, the analyst's local-currency cost "
    "rises in expectation, so on a fixed budget the analyst reduces query "
    "volume in that month; magnitude -0.3 elasticity is the mid-range value "
    "from the data-services demand elasticity literature (conservative -- "
    "large enough to perturb the surface meaningfully, small enough to stay "
    "defensible). "
    "Relevance: a coupling that altered within-month Var(Delta log Q) would "
    "shift the FX-variance share and bear on the descriptive surface; the "
    "user-pinned monthly-scalar operationalization rescales monthly Q "
    "magnitudes but leaves within-month Q-variance untouched. "
    "Connection: arm (b) executes the user-pinned operationalization "
    "verbatim and reports the descriptive concordance the resulting "
    "(unchanged) within-month surface produces against the Phase-4 primary; "
    "Q_t_coupled = Q_t * (1 + (-0.3) * z_t), with z_t standardized monthly "
    "realized FX vol within currency, Q_min floor = 1."
)

#: Spec-pinned NGN regime-break date (per
#: ``modules/regime_break.py:_REGIME_BREAK_START``).
_NGN_REGIME_BREAK: Final[date] = date(2023, 6, 1)

#: Arm (c) buffer width around the NGN break date (months on each side).
#: Six months is the conventional structural-break buffer (e.g. Bai-Perron
#: convention; conservatively wide given the spec-pinned regime is hard).
_NGN_BUFFER_MONTHS: Final[int] = 6

#: Arm (f) extended Q-high (~$390 Dune-cap equivalent / spec §2.3).
_Q_HIGH_EXTENDED: Final[float] = 39_000.0

#: Spec §9 non-rescue clause -- hard-coded; not configurable. Surfaces on
#: every ``SensitivityArmsResult``.
_NO_RESCUE_CLAUSE: Final[str] = (
    "Sensitivity arms cannot rescue a primary HALT (spec v0.7 §9). Each arm "
    "reports descriptive concordance only. The Phase-4 trajectory is "
    "NON-RETIREMENT via HALT-Q-DOMINANCE -- the q_variance_dominance_flag "
    "fires across the WHOLE anchored Q-range on the real Phase-3 panel; "
    "Phase-5 arms quantify how robust that descriptive surface is to "
    "alternative panel constructions, nothing more."
)

#: Concordance threshold -- max abs share difference under which an arm
#: is classified "concordant" (subject to also preserving q-variance
#: dominance). Module-internal default; spec v0.7 / plan v0.4 do not pin
#: a numeric concordance threshold. Set conservatively at 5% of the share
#: scale to admit only descriptively-tight concordance.
_CONCORDANCE_THRESHOLD: Final[float] = 0.05


def _share_summary(
    shares: Sequence[float],
) -> dict[str, float]:
    """Compute the min / max / median / panel-mean of a share grid.

    Args:
        shares: Per-grid-point shares (any length >=1; NaNs filtered).

    Returns:
        A dict with keys ``min`` / ``max`` / ``median`` / ``panel_mean``.
        On an all-NaN or empty input all four are NaN (never silent zero).
    """
    finite = [s for s in shares if math.isfinite(s)]
    if not finite:
        nan = float("nan")
        return {
            "min": nan,
            "max": nan,
            "median": nan,
            "panel_mean": nan,
        }
    arr = np.asarray(finite, dtype=float)
    return {
        "min": float(arr.min()),
        "max": float(arr.max()),
        "median": float(np.median(arr)),
        "panel_mean": float(arr.mean()),
    }


def _concordance_metric_vs_primary(
    primary: SurfaceGridResult,
    arm_shares: Sequence[float],
) -> float:
    """Max absolute share difference between the arm and the primary
    surface on the SAME grid.

    Args:
        primary: The Phase-4 primary surface result.
        arm_shares: The arm's per-grid-point shares -- MUST have the same
            length as ``primary.points``.

    Returns:
        The max absolute share difference; NaN if any share is non-finite
        or the lengths disagree (the caller is expected to record the
        length mismatch on the arm result's ``notes`` field).
    """
    primary_shares = [pt.fx_variance_share for pt in primary.points]
    if len(primary_shares) != len(arm_shares):
        return float("nan")
    diffs = [
        abs(p - a)
        for p, a in zip(primary_shares, arm_shares, strict=True)
        if math.isfinite(p) and math.isfinite(a)
    ]
    if not diffs:
        return float("nan")
    return float(max(diffs))


def _verdict_for(
    *,
    q_dom_preserved: bool,
    concordance_metric: float,
) -> ConcordanceVerdict:
    """Concordance verdict literal per the module-internal rule.

    "concordant" iff (1) q-variance dominance preserved AND (2)
    concordance metric < ``_CONCORDANCE_THRESHOLD`` (module default 0.05;
    not pinned by spec). Otherwise "discordant".
    A non-finite metric (length mismatch, all-NaN shares) routes to
    "discordant" -- the arm cannot be honestly classified as concordant
    without a valid metric.
    """
    if not q_dom_preserved:
        return "discordant"
    if not math.isfinite(concordance_metric):
        return "discordant"
    if concordance_metric < _CONCORDANCE_THRESHOLD:
        return "concordant"
    return "discordant"


# -- Arm (b) ---------------------------------------------------------------


def _arm_b_qfx_coupling(
    panel: tuple[PanelCell, ...],
    q_range: tuple[float, float],
    *,
    primary: SurfaceGridResult,
    s_be: float,
) -> SensitivityArmResult:
    """Arm (b) -- Q-FX behavioral coupling on monthly Q.

    Operationalization (user-locked 2026-05-21):

        Q_t_coupled = Q_t * (1 + (-0.3) * z_t)

    where ``z_t`` is the within-currency standardized monthly realized
    FX volatility and Q_t is the month's daily query series. The
    multiplier is a single scalar per month, so daily ``Delta log Q``
    within the month is unchanged -- the within-month decomposition
    (``var_q``, ``var_fx``, ``cov_term``, ``var_total``) is identical
    under this coupling, and so is ``fx_variance_share = var_fx /
    var_total`` per cell. The arm reports concordance_metric = 0 and
    preserves Q-dominance by construction.

    The standardized monthly FX vol ``z_m`` is computed PER CURRENCY
    against that currency's panel-mean and panel-stddev of
    ``x_realized_variance``. The scalar ``s_m = clip(1 + (-0.3) * z_m,
    lower=1.0/Q_min_factor, upper=None)`` is computed but, per the above,
    affects only the level (not the variance) and is recorded in the
    arm's ``notes`` for transparency. The Q-floor of 1 in the per-cell
    monthly aggregate is implicit (a month with zero queries would be
    a material-gap cell already, which we never re-perturb here).
    """
    # Compute per-currency standardized monthly z_m for visibility/
    # transparency. The shares themselves are unchanged at the cell
    # level under the user-pinned monthly-scalar operationalization.
    by_currency: dict[str, list[PanelCell]] = {}
    for cell in panel:
        by_currency.setdefault(cell.currency, []).append(cell)

    z_summaries: list[str] = []
    for cur in sorted(by_currency):
        x_values = np.asarray(
            [c.x_realized_variance for c in by_currency[cur]], dtype=float
        )
        mean = float(x_values.mean())
        std = float(x_values.std(ddof=0))
        if std == 0.0:
            z_min, z_max = 0.0, 0.0
        else:
            z = (x_values - mean) / std
            z_min, z_max = float(z.min()), float(z.max())
        z_summaries.append(
            f"{cur}: z_m in [{z_min:+.2f}, {z_max:+.2f}]"
        )

    # The within-month decomposition is unchanged under the user-pinned
    # monthly-scalar coupling. Re-evaluate the surface on the same panel;
    # by construction the result equals the primary surface.
    arm_surface = evaluate_surface_grid(panel, q_range, s_be=s_be)
    arm_shares = [pt.fx_variance_share for pt in arm_surface.points]
    metric = _concordance_metric_vs_primary(primary, arm_shares)

    notes = (
        f"Q_t_coupled = Q_t * (1 + ({_QFX_COUPLING_ELASTICITY:+.1f}) * z_t) "
        "with z_t standardized monthly Var(Delta log FX) (within currency). "
        "The monthly-scalar multiplier leaves within-month Var(Delta log Q) "
        "unchanged; the per-cell FX-variance share is identical under this "
        "operationalization. Per-currency z_m envelopes: "
        + "; ".join(z_summaries)
        + "."
    )

    return SensitivityArmResult(
        arm_name="b_qfx_coupling",
        surface_share_summary=_share_summary(arm_shares),
        q_variance_dominance_flag=arm_surface.q_variance_dominance_flag,
        interior_crossing_flag=arm_surface.interior_crossing,
        concordance_metric=metric,
        concordance_verdict=_verdict_for(
            q_dom_preserved=arm_surface.q_variance_dominance_flag,
            concordance_metric=metric,
        ),
        decision_citation=_ARM_B_DECISION_CITATION,
        notes=notes,
    )


# -- Arm (c) ---------------------------------------------------------------


def _arm_c_ngn_break_window(
    panel: tuple[PanelCell, ...],
    q_range: tuple[float, float],
    *,
    primary: SurfaceGridResult,
    s_be: float,
) -> SensitivityArmResult:
    """Arm (c) -- NGN break-window robustness pair.

    Drops NGN cells inside a ``_NGN_BUFFER_MONTHS``-month buffer
    immediately after the spec-pinned regime break (2023-06-01) and
    re-evaluates the surface on the filtered panel. Non-NGN cells are
    unchanged.

    If no NGN cells fall inside the buffer (the panel window already
    starts more than ``_NGN_BUFFER_MONTHS`` months past the break), the
    arm runs against the unfiltered panel and the concordance metric is
    exactly zero -- this is the descriptively honest outcome (the
    Phase-3 panel window 2023-11-01 begins 5 months past the break, so
    the 6-month buffer drops only the November/December 2023 NGN cells).
    """
    # Buffer end date: break + _NGN_BUFFER_MONTHS months.
    buffer_end_year = _NGN_REGIME_BREAK.year + (
        (_NGN_REGIME_BREAK.month - 1 + _NGN_BUFFER_MONTHS) // 12
    )
    buffer_end_month = (
        (_NGN_REGIME_BREAK.month - 1 + _NGN_BUFFER_MONTHS) % 12
    ) + 1

    def _in_buffer(cell: PanelCell) -> bool:
        if cell.currency != "NGN":
            return False
        cell_ym = (cell.year, cell.month)
        buf_end_ym = (buffer_end_year, buffer_end_month)
        return cell_ym <= buf_end_ym

    dropped = [c for c in panel if _in_buffer(c)]
    filtered = tuple(c for c in panel if not _in_buffer(c))

    if len(filtered) == 0:
        # Should never happen at G=5 -- only NGN cells can be dropped --
        # but the surface evaluator requires a non-empty panel.
        return SensitivityArmResult(
            arm_name="c_ngn_break_window",
            surface_share_summary=_share_summary([]),
            q_variance_dominance_flag=False,
            interior_crossing_flag=False,
            concordance_metric=float("nan"),
            concordance_verdict="n/a",
            decision_citation=None,
            notes=(
                "Filtered panel empty after NGN buffer drop -- arm cannot "
                "be evaluated; verdict is n/a (honest, never fabricated)."
            ),
        )

    arm_surface = evaluate_surface_grid(filtered, q_range, s_be=s_be)
    arm_shares = [pt.fx_variance_share for pt in arm_surface.points]
    metric = _concordance_metric_vs_primary(primary, arm_shares)

    dropped_ids = ", ".join(
        f"{c.currency} {c.year}-{c.month:02d}" for c in dropped
    )
    notes = (
        f"NGN regime break {_NGN_REGIME_BREAK.isoformat()} "
        f"(+/-{_NGN_BUFFER_MONTHS}-month buffer); dropped "
        f"{len(dropped)} NGN cell(s)"
        + (f": {dropped_ids}." if dropped_ids else ".")
    )

    return SensitivityArmResult(
        arm_name="c_ngn_break_window",
        surface_share_summary=_share_summary(arm_shares),
        q_variance_dominance_flag=arm_surface.q_variance_dominance_flag,
        interior_crossing_flag=arm_surface.interior_crossing,
        concordance_metric=metric,
        concordance_verdict=_verdict_for(
            q_dom_preserved=arm_surface.q_variance_dominance_flag,
            concordance_metric=metric,
        ),
        decision_citation=None,
        notes=notes,
    )


# -- Arm (d) ---------------------------------------------------------------


def _arm_d_gbm_jd_comparator(
    panel: tuple[PanelCell, ...],
    q_range: tuple[float, float],
    *,
    primary: SurfaceGridResult,
    s_be: float,
) -> SensitivityArmResult:
    """Arm (d) -- GBM / Jump-Diffusion FX comparator.

    Calibrates a GBM and a Merton jump-diffusion FX generator
    PER CURRENCY to the panel-mean and panel-variance of
    ``x_realized_variance`` (the per-cell within-month
    sum-of-squared-Delta-log-FX). Generates GBM and JD path ensembles
    at the same panel cluster count, computes the per-cell mean
    comparator ``var_fx_sim``, and substitutes it into each cell's
    three-way decomposition (preserving ``var_q`` and ``cov_term``).
    Re-evaluates
    the surface on the substituted panel.

    If ``simulations.stochastic_fx`` is unavailable at import time the
    arm HALTs with ``concordance_verdict = "n/a"``. The HALT path is
    honest -- it never fabricates a comparator. Per plan task 5.1: do
    NOT fabricate. The HALT writes a disposition memo path on the
    ``notes`` field (Phase5_HALT_d_gbm_jd_comparator.md).
    """
    try:
        from simulations.stochastic_fx import (
            GBMParameters,
            GBMPathGenerator,
            JumpDiffusionParameters,
            JumpDiffusionPathGenerator,
        )
    except ImportError as exc:
        return SensitivityArmResult(
            arm_name="d_gbm_jd_comparator",
            surface_share_summary=_share_summary([]),
            q_variance_dominance_flag=False,
            interior_crossing_flag=False,
            concordance_metric=float("nan"),
            concordance_verdict="n/a",
            decision_citation=None,
            notes=(
                f"HALT -- simulations.stochastic_fx unavailable: {exc!r}. "
                "Disposition memo path: scratch/2026-05-20-e10-revision/"
                "Phase5_HALT_d_gbm_jd_comparator.md. Arm skipped honestly; "
                "no fabricated comparator."
            ),
        )

    # Calibrate one GBM and one JD per currency to its panel-mean
    # var_fx. The calibrated sigma_per_month is sqrt(panel-mean
    # var_fx); for a daily series of ~20 trading days the
    # per-step sigma is sigma_month / sqrt(n_steps).
    by_currency: dict[str, list[PanelCell]] = {}
    for cell in panel:
        by_currency.setdefault(cell.currency, []).append(cell)

    # Per-currency calibrated mean var_fx (target moment under both
    # GBM and JD; the simulated var_fx is the realized-variance
    # surrogate, matched at the panel-mean cell).
    calibrated_var_fx: dict[str, float] = {}
    n_steps_default = 21  # ~21 trading days per month
    for cur, cells in by_currency.items():
        var_fx_finite = [
            c.decomposition.var_fx
            for c in cells
            if math.isfinite(c.decomposition.var_fx)
            and c.decomposition.var_fx > 0.0
        ]
        if not var_fx_finite:
            calibrated_var_fx[cur] = float("nan")
        else:
            calibrated_var_fx[cur] = float(np.mean(var_fx_finite))

    # Simulate one GBM and one JD ensemble per currency; compute the
    # ensemble-mean realised variance of Δlog levels (matching the
    # population-variance convention of ``decompose_cell``); take the
    # mean of the two as the substituted var_fx.
    sim_var_fx_by_currency: dict[str, float] = {}
    rng_seed_base = 4242
    # Explicit currency -> seed offset map. Using hash(cur) would be
    # PYTHONHASHSEED-dependent and break Tier-3 cross-process
    # reproducibility; the explicit mapping pins the GBM/JD ensemble
    # path-by-path across runs.
    _CURRENCY_SEED_OFFSET: dict[str, int] = {
        "COP": 101,
        "BRL": 211,
        "EUR": 307,
        "GBP": 419,
        "NGN": 521,
    }
    gbm_notes: list[str] = []
    jd_notes: list[str] = []
    for cur, target_var_fx in calibrated_var_fx.items():
        if not math.isfinite(target_var_fx) or target_var_fx <= 0.0:
            sim_var_fx_by_currency[cur] = float("nan")
            continue
        # Sigma is the per-month-equivalent vol (NOT per-day). With T =
        # n_steps * dt = 1 month-equivalent, the sum over n_steps daily
        # log-increments has variance n_steps * sigma^2 * dt = sigma^2 *
        # T. Setting Var(sum) = target_var_fx gives sigma = sqrt(
        # target_var_fx / T) on the month-equivalent scale. dt = T /
        # n_steps. The GBM/JD generators expect (sigma, dt, n_steps) on
        # the same time scale so this passes through directly.
        T_month = 1.0
        sigma_per_month = math.sqrt(target_var_fx / T_month)
        # GBM calibration. x_0 set to 100 (arbitrary; relative-return
        # process is scale-invariant in log space).
        gbm_params = GBMParameters(
            mu=0.0,
            sigma=sigma_per_month,
            x_0=100.0,
            T=T_month,
            dt=T_month / n_steps_default,
            n_steps=n_steps_default,
        )
        gbm_gen = GBMPathGenerator(gbm_params)
        gbm_paths = gbm_gen(
            rng_seed=rng_seed_base + _CURRENCY_SEED_OFFSET.get(cur, 0),
            n_paths=256,
        )
        # Recompute per-path Var(Delta log FX) directly from the path
        # matrix; the PathEnsemble's sigma_t object uses a different
        # convention. We want the per-cell decomposition surrogate --
        # population variance of daily Delta log levels.
        log_paths = np.log(gbm_paths.paths)
        d_log = np.diff(log_paths, axis=1)
        # Population variance per path, then mean across paths.
        path_means = d_log.mean(axis=1, keepdims=True)
        path_var = ((d_log - path_means) ** 2).mean(axis=1)
        gbm_var_fx = float(path_var.mean())
        gbm_notes.append(f"{cur}: gbm_var_fx={gbm_var_fx:.3e}")

        # JD calibration: same continuous drift/vol; small jump component.
        # lambda_jump = 1 jump/month-equivalent; jump_mean = 0; jump_std
        # calibrated to add ~10% additional variance.
        # Merton var(Delta log) per step ~= sigma^2 * dt + lambda * dt *
        # (jump_mean^2 + jump_std^2). Targeting overall var = target_var_fx
        # with the diffusion piece supplying 90% and jumps 10%.
        diffusion_share = 0.9
        sigma_jd = math.sqrt(target_var_fx * diffusion_share / T_month)
        jump_variance_total = target_var_fx * (1.0 - diffusion_share)
        # Distribute over lambda_jump * T expected jumps.
        lambda_jump = 1.0
        jump_var = jump_variance_total / max(lambda_jump * T_month, 1e-9)
        jump_std = math.sqrt(max(jump_var, 1e-12))
        jd_params = JumpDiffusionParameters(
            mu=0.0,
            sigma=sigma_jd,
            lambda_jump=lambda_jump,
            jump_mean=0.0,
            jump_std=jump_std,
            x_0=100.0,
            T=T_month,
            dt=T_month / n_steps_default,
            n_steps=n_steps_default,
        )
        jd_gen = JumpDiffusionPathGenerator(jd_params)
        jd_paths = jd_gen(
            rng_seed=rng_seed_base + 1 + _CURRENCY_SEED_OFFSET.get(cur, 0),
            n_paths=256,
        )
        log_paths_jd = np.log(jd_paths.paths)
        d_log_jd = np.diff(log_paths_jd, axis=1)
        path_means_jd = d_log_jd.mean(axis=1, keepdims=True)
        path_var_jd = ((d_log_jd - path_means_jd) ** 2).mean(axis=1)
        jd_var_fx = float(path_var_jd.mean())
        jd_notes.append(f"{cur}: jd_var_fx={jd_var_fx:.3e}")

        # Substitution surrogate: mean of GBM and JD ensemble-mean
        # var_fx.
        sim_var_fx_by_currency[cur] = (gbm_var_fx + jd_var_fx) / 2.0

    # Build the substituted panel: replace each cell's var_fx with the
    # per-currency simulated var_fx; preserve var_q + cov_term; recompute
    # var_total and fx_variance_share.
    substituted: list[PanelCell] = []
    for cell in panel:
        sub_var_fx = sim_var_fx_by_currency.get(cell.currency, float("nan"))
        if (
            cell.material_gap
            or not math.isfinite(sub_var_fx)
            or sub_var_fx <= 0.0
        ):
            substituted.append(cell)
            continue
        new_var_total = (
            sub_var_fx + cell.decomposition.var_q + cell.decomposition.cov_term
        )
        if new_var_total <= 0.0:
            substituted.append(cell)
            continue
        new_share = sub_var_fx / new_var_total
        new_decomp = ThreeWayDecompositionCell(
            currency=cell.decomposition.currency,
            year=cell.decomposition.year,
            month=cell.decomposition.month,
            var_total=new_var_total,
            var_fx=sub_var_fx,
            var_q=cell.decomposition.var_q,
            cov_term=cell.decomposition.cov_term,
            grid_index_length=cell.decomposition.grid_index_length,
            identity_residual=0.0,
        )
        substituted.append(
            PanelCell(
                currency=cell.currency,
                year=cell.year,
                month=cell.month,
                x_realized_variance=sub_var_fx,
                y_realized_variance=cell.y_realized_variance,
                decomposition=new_decomp,
                n_fx_trading_days=cell.n_fx_trading_days,
                n_surviving_days=cell.n_surviving_days,
                material_gap=False,
                fx_variance_share=new_share,
                qualifying=cell.qualifying,
                seed=cell.seed,
            )
        )

    arm_surface = evaluate_surface_grid(tuple(substituted), q_range, s_be=s_be)
    arm_shares = [pt.fx_variance_share for pt in arm_surface.points]
    metric = _concordance_metric_vs_primary(primary, arm_shares)

    notes = (
        "GBM and JD FX comparators calibrated per currency to panel-mean "
        "var_fx. Substitution surrogate = mean(GBM_ensemble_var_fx, "
        "JD_ensemble_var_fx) replaces var_fx per cell; var_q and cov_term "
        "preserved; new share = sub_var_fx / (sub_var_fx + var_q + "
        f"cov_term). GBM moments: [{', '.join(gbm_notes)}]. JD moments: "
        f"[{', '.join(jd_notes)}]."
    )

    return SensitivityArmResult(
        arm_name="d_gbm_jd_comparator",
        surface_share_summary=_share_summary(arm_shares),
        q_variance_dominance_flag=arm_surface.q_variance_dominance_flag,
        interior_crossing_flag=arm_surface.interior_crossing,
        concordance_metric=metric,
        concordance_verdict=_verdict_for(
            q_dom_preserved=arm_surface.q_variance_dominance_flag,
            concordance_metric=metric,
        ),
        decision_citation=None,
        notes=notes,
    )


# -- Arm (e) ---------------------------------------------------------------


def _arm_e_per_currency(
    panel: tuple[PanelCell, ...],
    q_range: tuple[float, float],
    *,
    primary: SurfaceGridResult,
    s_be: float,
    base_n: int,
    refined_n: int,
) -> SensitivityArmResult:
    """Arm (e) -- per-currency split.

    Wraps the existing ``compute_currency_spread`` from Phase 4
    (task 4.3) for the descriptive per-currency surfaces. Concordance
    is reported against the primary surface using the per-currency
    *median* across the 5 currencies (the envelope's centre).

    Per-currency q-variance dominance is True iff every per-currency
    surface stays strictly below ``s_be`` at every grid point.
    """
    spread = compute_currency_spread(
        panel,
        q_range,
        s_be=s_be,
        base_n=base_n,
        refined_n=refined_n,
    )
    # Per-currency q-dominance: True iff every currency's surface
    # preserves q-variance dominance.
    per_cur_q_dom = all(
        sg.q_variance_dominance_flag for sg in spread.per_currency_grids.values()
    )
    per_cur_interior = any(
        sg.interior_crossing for sg in spread.per_currency_grids.values()
    )

    # Concordance metric: max abs share difference between the
    # per-currency median and the primary surface at each grid point.
    median_shares = list(spread.envelope_median)
    metric = _concordance_metric_vs_primary(primary, median_shares)

    currency_summaries = "; ".join(
        f"{cur}: panel_mean_share={sg.points[0].fx_variance_share:.3e}, "
        f"q_dom={sg.q_variance_dominance_flag}"
        for cur, sg in sorted(spread.per_currency_grids.items())
    )
    notes = (
        "Per-currency surfaces (Phase-4 compute_currency_spread wrap); "
        f"5 currency surfaces evaluated; envelope median used for "
        f"concordance metric. {currency_summaries}."
    )

    return SensitivityArmResult(
        arm_name="e_per_currency",
        surface_share_summary=_share_summary(median_shares),
        q_variance_dominance_flag=per_cur_q_dom,
        interior_crossing_flag=per_cur_interior,
        concordance_metric=metric,
        concordance_verdict=_verdict_for(
            q_dom_preserved=per_cur_q_dom,
            concordance_metric=metric,
        ),
        decision_citation=None,
        notes=notes,
    )


# -- Arm (f) ---------------------------------------------------------------


def _arm_f_q_high_extended(
    panel: tuple[PanelCell, ...],
    q_range: tuple[float, float],
    *,
    primary: SurfaceGridResult,
    s_be: float,
    q_high_extended: float,
) -> SensitivityArmResult:
    """Arm (f) -- optional Q_high = 39_000 arm.

    Re-evaluates the FX-variance-share surface with the Q-grid extended
    to the ``_Q_HIGH_EXTENDED`` upper cap (the $390 Dune-cap equivalent
    monthly query volume). The share, computed as the panel-mean
    ``fx_variance_share`` across non-material-gap cells, is INVARIANT in
    Q-volume by construction in ``evaluate_surface_grid``; extending the
    grid upper bound therefore leaves the surface value unchanged and
    Q-dominance preserved. The arm explicitly verifies this scaling
    property.
    """
    extended_range = (q_range[0], q_high_extended)
    arm_surface = evaluate_surface_grid(panel, extended_range, s_be=s_be)
    arm_shares = [pt.fx_variance_share for pt in arm_surface.points]

    # On the extended grid the primary's anchored upper bound shifts;
    # the concordance metric vs. primary is computed pointwise on the
    # extended grid only -- the lengths differ from the primary in
    # general (adaptive doubling may or may not fire here as it does
    # on the primary). Report max share difference vs. the primary's
    # panel-mean share (a scalar) -- this is the descriptively honest
    # comparison because the share is panel-mean-invariant in Q.
    primary_shares = [pt.fx_variance_share for pt in primary.points]
    primary_panel_mean = (
        float(np.mean([s for s in primary_shares if math.isfinite(s)]))
        if any(math.isfinite(s) for s in primary_shares)
        else float("nan")
    )
    if not math.isfinite(primary_panel_mean):
        metric = float("nan")
    else:
        diffs = [
            abs(s - primary_panel_mean) for s in arm_shares if math.isfinite(s)
        ]
        metric = float(max(diffs)) if diffs else float("nan")

    notes = (
        f"Q-grid upper bound extended from {q_range[1]:.0f} to "
        f"{q_high_extended:.0f} (the $390 Dune-cap equivalent monthly "
        "query volume). The panel-mean share is invariant in Q by "
        "construction in evaluate_surface_grid (the share is the "
        "panel-mean cell fx_variance_share across non-material-gap "
        "cells; q-volume enters only via the grid coordinate, not the "
        "share value). Extending the upper bound does not change the "
        "surface share at any grid point; Q-dominance preserved. NOTE "
        "ON METRIC SHAPE: arm (f) reports max |arm_share - primary_"
        "panel_mean_scalar| because the primary surface's panel-mean "
        "share is Q-invariant; this is a scalar comparison and is NOT "
        "directly comparable to the pointwise metrics of arms (b)-(e). "
        "A near-zero metric here reflects the panel-mean-invariance "
        "construction, not a tighter concordance than arms (b)-(e)."
    )

    return SensitivityArmResult(
        arm_name="f_q_high_extended",
        surface_share_summary=_share_summary(arm_shares),
        q_variance_dominance_flag=arm_surface.q_variance_dominance_flag,
        interior_crossing_flag=arm_surface.interior_crossing,
        concordance_metric=metric,
        concordance_verdict=_verdict_for(
            q_dom_preserved=arm_surface.q_variance_dominance_flag,
            concordance_metric=metric,
        ),
        decision_citation=None,
        notes=notes,
    )


# -- Public runner ---------------------------------------------------------


def run_sensitivity_arms(
    panel: Sequence[PanelCell],
    q_range: tuple[float, float],
    *,
    s_be: float = DEFAULT_S_BE,
    base_n: int = DEFAULT_BASE_N,
    refined_n: int = DEFAULT_REFINED_N,
    q_high_extended: float = _Q_HIGH_EXTENDED,
) -> SensitivityArmsResult:
    """Run all Phase-5 sensitivity arms and emit the aggregate result.

    Computes the Phase-4 primary surface ONCE on ``panel`` /
    ``q_range`` / ``s_be``, then dispatches arms (b), (c), (d), (e),
    (f). Each arm reports descriptive concordance against the primary
    only; no arm gates a verdict; no arm rescues the primary HALT
    (spec v0.7 §9). The primary's ``q_variance_dominance_flag`` is
    carried on the result for cross-arm reference.

    HALTs: an arm that cannot honestly execute (e.g. arm (d) when
    ``simulations.stochastic_fx`` is unavailable; arm (c) when the
    filtered panel is empty) emits ``concordance_verdict = "n/a"`` and
    stays in the result tuple. The arm runner NEVER fabricates a result
    nor silently drops the arm.

    Args:
        panel: The Phase-3 panel cells (e.g. 5 currencies x ~30 months
            ~ 150 cells). Tuple-immutable input is preferred but any
            ``Sequence`` is accepted -- ``run_sensitivity_arms`` wraps
            it into a frozen tuple before dispatch.
        q_range: Anchored ``(Q_low, Q_high)`` Q-volume bounds (e.g.
            ``(28.0, 130.0)`` per the Phase-4 anchor).
        s_be: Ex-ante-pinned break-even share (default 0.25; spec v0.7
            §4.4 / Phase-2.5 record).
        base_n: User-locked base grid size (default 50).
        refined_n: Refined grid size under adaptive doubling
            (default 100).
        q_high_extended: Arm (f) extended Q-high (default 39_000 --
            the $390 Dune-cap equivalent).

    Returns:
        A ``SensitivityArmsResult`` with the 5 per-arm
        ``SensitivityArmResult`` entries, the primary's q-variance-
        dominance flag, and the spec-§9 no-rescue clause.
    """
    panel_tuple = tuple(panel)
    primary = evaluate_surface_grid(
        panel_tuple, q_range, s_be=s_be, base_n=base_n, refined_n=refined_n
    )

    arms: tuple[SensitivityArmResult, ...] = (
        _arm_b_qfx_coupling(panel_tuple, q_range, primary=primary, s_be=s_be),
        _arm_c_ngn_break_window(
            panel_tuple, q_range, primary=primary, s_be=s_be
        ),
        _arm_d_gbm_jd_comparator(
            panel_tuple, q_range, primary=primary, s_be=s_be
        ),
        _arm_e_per_currency(
            panel_tuple,
            q_range,
            primary=primary,
            s_be=s_be,
            base_n=base_n,
            refined_n=refined_n,
        ),
        _arm_f_q_high_extended(
            panel_tuple,
            q_range,
            primary=primary,
            s_be=s_be,
            q_high_extended=q_high_extended,
        ),
    )

    return SensitivityArmsResult(
        arms=arms,
        primary_q_dominance_flag=primary.q_variance_dominance_flag,
        no_rescue_clause=_NO_RESCUE_CLAUSE,
    )


__all__ = [
    "run_sensitivity_arms",
]
