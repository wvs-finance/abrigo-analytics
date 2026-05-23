"""Posterior-diagnostic gate for SAAS-COHORT-1 emission.

Implements spec §8(8) convergence floor + spec §8(7) posterior-vs-prior
CI-width invariant as a HALT-gate (NOT advisory; MQ-B5 v0.1→v0.2 fix).

Gate definition (NON-NEGOTIABLE — failure of any one yields ``passed=False``
and the consumer at :mod:`emit` raises
:class:`simulations.saas_builder._errors.DiagnosticGateError`):

1. **§8(8) convergence floor** — for every monitored parameter:

   - ``r_hat ≤ 1.01``;
   - ``ESS_bulk ≥ 400`` AND ``ESS_tail ≥ 400`` (TWO thresholds, MQ-B5;
     heavy-tailed TruncPareto α posterior is the most likely tail-ESS
     violator given §8(6) α-floor proximity);
   - divergences ≤ 0.5 % of post-warmup draws;
   - sim-count floor: ≥ 4000 post-warmup draws **per chain** AND ≥ 4
     chains — total ≥ 16,000 draws (Stage-2 PyMC pin per spec §8(8)
     line 432-439; MQ-FLAG-D + BLOCK-4 fix — NOT CLAUDE.md ``N_MIN=75``,
     which is a Stage-3 cohort-survey invariant and is OUT OF SCOPE for
     this Stage-2 synthetic-Bayesian fit). Plan v0.3 CORRECTIONS-α
     §"BLOCK-4 fix" tightens the per-chain semantics (v0.2 enforced
     total-only, allowing 4 chains × 1000 draws to silently pass).

2. **§8(7) posterior-CI-width invariant** — for every monitored
   parameter, posterior 95 % CI width ≤ 2× prior 95 % CI width. If
   exceeded, the data is not informative for that parameter and the
   emission HALTs per the spec's anti-fishing invariant. v0.1 demoted
   this to advisory shrinkage; v0.2 restores it to a HALT-gate
   alongside §8(8) (MQ-B5).

3. PSIS-LOO ``k̂ < 0.7`` is OUT OF SCOPE for COHORT-1 (model selection
   deferred to COHORT-3 per spec §9 / TODO-COHORT-3); see plan
   §MQ-FLAG-C.

This file is Callable tier — frozen-dc + ``__call__`` returning a
:class:`DiagnosticVerdict` Value. ``arviz`` only; no PyMC import.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

import arviz as az
import numpy as np

# ─── Module-level constants (gate thresholds — spec §8(7), §8(8)) ─────────────

#: Spec §8(8) r-hat ceiling for every monitored parameter.
RHAT_GATE: Final[float] = 1.01

#: Spec §8(8) ESS_bulk floor for every monitored parameter (MQ-B5 split).
ESS_BULK_GATE: Final[float] = 400.0

#: Spec §8(8) ESS_tail floor for every monitored parameter (MQ-B5 split).
ESS_TAIL_GATE: Final[float] = 400.0

#: Spec §8(8) divergence rate ceiling (fraction of post-warmup draws).
DIVERGENCE_FRAC_GATE: Final[float] = 0.005

#: Spec §8(8) Stage-2 PyMC sim-count floor — post-warmup draws **per chain**.
#: BLOCK-4 fix (plan v0.3 CORRECTIONS-α): the threshold is per-chain, NOT
#: total; the total minimum is :data:`SIM_COUNT_CHAIN_FLOOR` × this constant
#: (= 16,000 with the default 4-chain pin).
SIM_COUNT_DRAW_FLOOR: Final[int] = 4000

#: Spec §8(8) Stage-2 PyMC sim-count floor — chain count.
SIM_COUNT_CHAIN_FLOOR: Final[int] = 4

#: Spec §8(7) posterior-vs-prior 95 % CI width ratio HALT-gate (MQ-B5).
CI_WIDTH_RATIO_GATE: Final[float] = 2.0

#: Default monitored-parameter list. Subclasses / callers may override.
DEFAULT_MONITORED_PARAMS: Final[tuple[str, ...]] = (
    "mu",
    "phi",
    "alpha_pareto",
    "x_m",
    "pi",
)


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DiagnosticVerdict:
    """Result of the spec §8(7) + §8(8) gate.

    Attributes:
        rhat_max: max r-hat over monitored parameters.
        ess_bulk_min: min ESS_bulk over monitored parameters.
        ess_tail_min: min ESS_tail over monitored parameters.
        divergence_frac: divergences / post-warmup draws.
        sim_count_floor_violated: True iff per-chain post-warmup draws
            < SIM_COUNT_DRAW_FLOOR (= 4000 per BLOCK-4 fix) OR
            n_chains < SIM_COUNT_CHAIN_FLOOR (= 4).
            (Renamed from v0.1 ``n_min_violated`` per MQ-FLAG-D —
            ``N_MIN=75`` is a Stage-3 cohort-survey invariant, NOT a
            Stage-2 thinning guard.)
        ci_width_ratio_max: max over monitored params of
            ``posterior_95_CI_width / prior_95_CI_width``. HALT-gate at
            :data:`CI_WIDTH_RATIO_GATE` per spec §8(7) (MQ-B5 fix
            restoring this from advisory to gate).
        n_chains: number of chains in the input idata.
        n_draws_per_chain: per-chain draw count.
        passed: True iff all four §8(8) thresholds AND the §8(7)
            CI-width ratio gate pass simultaneously.

    Validation contract:

    - All numeric fields are finite and non-negative.
    - ``n_chains > 0`` and ``n_draws_per_chain > 0``.
    """

    rhat_max: float
    ess_bulk_min: float
    ess_tail_min: float
    divergence_frac: float
    sim_count_floor_violated: bool
    ci_width_ratio_max: float
    n_chains: int
    n_draws_per_chain: int
    passed: bool

    def __post_init__(self) -> None:
        for name, value in (
            ("rhat_max", self.rhat_max),
            ("ess_bulk_min", self.ess_bulk_min),
            ("ess_tail_min", self.ess_tail_min),
            ("divergence_frac", self.divergence_frac),
            ("ci_width_ratio_max", self.ci_width_ratio_max),
        ):
            if not math.isfinite(value):
                raise ValueError(
                    f"DiagnosticVerdict.{name} = {value!r} must be finite"
                )
            if value < 0.0:
                raise ValueError(
                    f"DiagnosticVerdict.{name} = {value!r} must be ≥ 0"
                )
        if self.n_chains <= 0:
            raise ValueError(
                f"DiagnosticVerdict.n_chains = {self.n_chains} must be > 0"
            )
        if self.n_draws_per_chain <= 0:
            raise ValueError(
                f"DiagnosticVerdict.n_draws_per_chain ="
                f" {self.n_draws_per_chain} must be > 0"
            )


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _scalar_max(arr: np.ndarray) -> float:
    """Return ``float(arr.max())`` ignoring NaNs; treat all-NaN as +inf."""
    if arr.size == 0:
        return float("inf")
    finite_mask = np.isfinite(arr)
    if not np.any(finite_mask):
        return float("inf")
    return float(np.nanmax(arr[finite_mask]))


def _scalar_min(arr: np.ndarray) -> float:
    """Return ``float(arr.min())`` ignoring NaNs; treat all-NaN as 0.0."""
    if arr.size == 0:
        return 0.0
    finite_mask = np.isfinite(arr)
    if not np.any(finite_mask):
        return 0.0
    return float(np.nanmin(arr[finite_mask]))


def _ci_width_95(samples: np.ndarray) -> float:
    """Return the 95 % CI width (q_{0.975} − q_{0.025}) of a 1-D sample.

    Uses :func:`numpy.quantile` with ``method='linear'`` (default).
    Returns 0.0 if the sample is empty (degenerate CI).
    """
    flat = samples.ravel()
    if flat.size == 0:
        return 0.0
    finite = flat[np.isfinite(flat)]
    if finite.size == 0:
        return 0.0
    lo = float(np.quantile(finite, 0.025))
    hi = float(np.quantile(finite, 0.975))
    return hi - lo


def compute_ci_width_ratio_max(
    posterior: az.InferenceData,
    prior: az.InferenceData,
    monitored: Iterable[str],
) -> float:
    """Return max over ``monitored`` of posterior/prior 95 % CI width ratio.

    Spec §8(7) HALT-gate at :data:`CI_WIDTH_RATIO_GATE` (MQ-B5).

    For each parameter name in ``monitored``:

    - Read posterior samples from ``posterior.posterior[name]`` and prior
      samples from ``prior.prior[name]`` (both shape (chain, draw, *event)).
    - Compute 95 % CI widths of flattened arrays.
    - Compute ratio ``posterior_width / prior_width``; if prior_width is
      0 (degenerate prior), record ratio +inf for that parameter.
    - Track maximum over monitored params.

    CR-IMPORTANT (v0.3 → v0.4 sweep): all monitored parameters are
    visited — no short-circuit on the first degenerate prior — so a
    full per-parameter map of ratios can be produced via
    :func:`compute_ci_width_ratio_per_param`. The aggregate function
    here returns ``max(ratios)`` after every parameter has been
    measured, preserving the v0.2 monotone HALT semantic (any +inf
    forces the max to +inf) while removing the silent first-failure
    early-return that masked downstream violations.

    Args:
        posterior: ``arviz.InferenceData`` with ``.posterior`` group.
        prior: ``arviz.InferenceData`` with ``.prior`` group.
        monitored: parameter names; each must appear in both groups.

    Returns:
        Max ratio over monitored params; +inf if any prior_width = 0.

    Raises:
        KeyError: if a monitored name is missing from either group.
    """
    per_param = compute_ci_width_ratio_per_param(posterior, prior, monitored)
    if not per_param:
        return 0.0
    return max(per_param.values())


def compute_ci_width_ratio_per_param(
    posterior: az.InferenceData,
    prior: az.InferenceData,
    monitored: Iterable[str],
) -> dict[str, float]:
    """Return per-parameter posterior/prior 95 % CI width ratio map.

    Companion to :func:`compute_ci_width_ratio_max`. Visits every
    monitored parameter (no short-circuit) so callers can surface a
    full violation map. Used by the ``_AUDIT.json`` writer to emit
    per-parameter ``ci_width_ratio`` fields (CR-IMPORTANT v0.3 sweep).

    Args:
        posterior: ``arviz.InferenceData`` with ``.posterior`` group.
        prior: ``arviz.InferenceData`` with ``.prior`` group.
        monitored: parameter names; each must appear in both groups.

    Returns:
        Mapping ``{param_name: ratio}``. Ratio is +inf where the prior
        95 % CI width is 0 (degenerate prior); otherwise
        ``post_width / prior_width``.

    Raises:
        KeyError: if a monitored name is missing from either group.
    """
    posterior_group = posterior["posterior"]
    prior_group = prior["prior"]
    ratios: dict[str, float] = {}
    for name in monitored:
        post_samples = np.asarray(posterior_group[name].values)
        prior_samples = np.asarray(prior_group[name].values)
        post_w = _ci_width_95(post_samples)
        prior_w = _ci_width_95(prior_samples)
        ratios[name] = float("inf") if prior_w <= 0.0 else post_w / prior_w
    return ratios


@dataclass(frozen=True)
class PosteriorDiagnostic:
    """Spec §8(7) + §8(8) HALT-gate, applied to an ``arviz.InferenceData``.

    Attributes:
        monitored_params: parameter names to track. Defaults to
            :data:`DEFAULT_MONITORED_PARAMS`.

    Behavior contract:

    - ``__call__(idata, prior_idata)`` returns a :class:`DiagnosticVerdict`
      with all six fields populated.
    - ``passed`` is True iff:
        - ``rhat_max ≤ 1.01``;
        - ``ess_bulk_min ≥ 400`` AND ``ess_tail_min ≥ 400``;
        - ``divergence_frac ≤ 0.005``;
        - ``sim_count_floor_violated`` is False;
        - ``ci_width_ratio_max ≤ 2.0``.
    - Refuses to mark ``passed=True`` if ANY of the six thresholds fail.
    - ``prior_idata`` is required for the §8(7) gate; passing ``None``
      raises :class:`ValueError` (the CI-width gate cannot silently skip
      per MQ-B5 v0.2 restoration).
    - No PyMC import; ``arviz`` only.
    """

    monitored_params: tuple[str, ...] = DEFAULT_MONITORED_PARAMS

    def __post_init__(self) -> None:
        if len(self.monitored_params) < 1:
            raise ValueError(
                "PosteriorDiagnostic.monitored_params must be non-empty"
            )
        if len(set(self.monitored_params)) != len(self.monitored_params):
            raise ValueError(
                f"PosteriorDiagnostic.monitored_params has duplicates:"
                f" {self.monitored_params}"
            )

    def __call__(
        self,
        idata: az.InferenceData,
        prior_idata: az.InferenceData | None = None,
    ) -> DiagnosticVerdict:
        """Compute the verdict on ``idata`` against ``prior_idata``.

        Args:
            idata: posterior :class:`arviz.InferenceData` from
                ``pm.sample(...)``. Must include ``.posterior`` and
                ``.sample_stats`` groups.
            prior_idata: prior :class:`arviz.InferenceData` from
                ``pm.sample_prior_predictive(...)``. Required for the
                §8(7) CI-width gate; raises :class:`ValueError` if None.

        Returns:
            :class:`DiagnosticVerdict` with all gate fields populated.

        Contract:
            Preconditions:
                - ``idata`` must have a ``"posterior"`` group containing
                  every name in ``self.monitored_params`` AND a
                  ``"sample_stats"`` group with a ``"diverging"`` boolean
                  array of shape ``(n_chains, n_draws)``. Missing groups
                  raise ``KeyError`` (implicit, ``idata["..."]`` on
                  line ~318).
                - ``prior_idata`` must NOT be None (explicit check, line
                  ~310; raises ``ValueError`` per MQ-B5 — the §8(7)
                  CI-width gate cannot silently skip).
                - ``prior_idata.prior[name]`` 95 % CI width must be > 0
                  for each monitored ``name``; degenerate prior with
                  zero width yields ``ci_width_ratio_max = +inf``,
                  forcing ``passed = False`` (no exception).
                - ``self.monitored_params`` is non-empty and has no
                  duplicates (enforced at ``__post_init__``).

            Raises:
                ValueError: if ``prior_idata is None`` (explicit, line
                    ~310). Caller MUST supply prior draws.
                KeyError: if a monitored parameter is missing from
                    either ``idata.posterior`` or ``prior_idata.prior``
                    (implicit, dict-style group access).

            Silences: none. NaN values inside arrays are filtered by
                ``_scalar_max`` / ``_scalar_min`` (treated as +inf /
                0.0 respectively); this is intentional fallthrough so
                an all-NaN diagnostic forces ``passed = False`` rather
                than crashing.
        """
        if prior_idata is None:
            raise ValueError(
                "PosteriorDiagnostic: prior_idata is required for the"
                " spec §8(7) CI-width HALT-gate (MQ-B5). Pass an"
                " arviz.InferenceData from pm.sample_prior_predictive."
            )

        # r-hat / ESS_bulk / ESS_tail across monitored parameters.
        var_names = list(self.monitored_params)
        rhat_da = az.rhat(idata, var_names=var_names)
        ess_bulk_da = az.ess(idata, var_names=var_names, method="bulk")
        ess_tail_da = az.ess(idata, var_names=var_names, method="tail")
        rhat_arr = np.concatenate(
            [np.asarray(rhat_da[v].values).ravel() for v in var_names]
        )
        ess_bulk_arr = np.concatenate(
            [np.asarray(ess_bulk_da[v].values).ravel() for v in var_names]
        )
        ess_tail_arr = np.concatenate(
            [np.asarray(ess_tail_da[v].values).ravel() for v in var_names]
        )
        rhat_max = _scalar_max(rhat_arr)
        ess_bulk_min = _scalar_min(ess_bulk_arr)
        ess_tail_min = _scalar_min(ess_tail_arr)

        # Divergence rate.
        sample_stats = idata["sample_stats"]
        diverging = np.asarray(sample_stats["diverging"].values, dtype=bool)
        n_chains = int(diverging.shape[0])
        n_draws_per_chain = int(diverging.shape[1])
        total_draws = n_chains * n_draws_per_chain
        divergence_frac = (
            float(diverging.sum()) / float(total_draws)
            if total_draws > 0
            else 0.0
        )

        # Sim-count floor — BLOCK-4 fix: enforce per-chain ≥ 4000 AND
        # n_chains ≥ 4 (NOT total ≥ 4000, which silently passed
        # 4 chains × 1000 draws under v0.2). Plan v0.3 CORRECTIONS-α.
        sim_count_floor_violated = (
            n_draws_per_chain < SIM_COUNT_DRAW_FLOOR
            or n_chains < SIM_COUNT_CHAIN_FLOOR
        )

        # §8(7) CI-width gate.
        ci_width_ratio_max = compute_ci_width_ratio_max(
            idata, prior_idata, var_names
        )

        passed = (
            rhat_max <= RHAT_GATE
            and ess_bulk_min >= ESS_BULK_GATE
            and ess_tail_min >= ESS_TAIL_GATE
            and divergence_frac <= DIVERGENCE_FRAC_GATE
            and not sim_count_floor_violated
            and ci_width_ratio_max <= CI_WIDTH_RATIO_GATE
        )

        return DiagnosticVerdict(
            rhat_max=rhat_max,
            ess_bulk_min=ess_bulk_min,
            ess_tail_min=ess_tail_min,
            divergence_frac=divergence_frac,
            sim_count_floor_violated=sim_count_floor_violated,
            ci_width_ratio_max=ci_width_ratio_max,
            n_chains=n_chains,
            n_draws_per_chain=n_draws_per_chain,
            passed=passed,
        )


__all__ = [
    "CI_WIDTH_RATIO_GATE",
    "DEFAULT_MONITORED_PARAMS",
    "DIVERGENCE_FRAC_GATE",
    "ESS_BULK_GATE",
    "ESS_TAIL_GATE",
    "RHAT_GATE",
    "SIM_COUNT_CHAIN_FLOOR",
    "SIM_COUNT_DRAW_FLOOR",
    "DiagnosticVerdict",
    "PosteriorDiagnostic",
    "compute_ci_width_ratio_max",
    "compute_ci_width_ratio_per_param",
]
