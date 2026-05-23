"""Sign-certification gate Callable for SAAS-COHORT-2.

Implements:

- :class:`SignCertificationGate` — for each ``BracketPoint`` in a
  ``BracketGrid``, evaluates Δ^(a_s) over posterior τ_t draws,
  computes the posterior-predictive 95% credible interval (NOT
  bootstrap; spec §9 row TODO-COHORT-2), and certifies
  ``delta_upper_bound_quantile < 0`` strictly per Pin BRACKET-M5.
- :class:`PPCQuantileCoverageCheck` — computes empirical coverage of
  the nominal 95% credible interval at τ_t quantiles ``{50, 90, 99}``-pct
  and raises :class:`PPCQuantileMiscoverageError` when any falls outside
  ``[0.93, 0.97]`` (MQ-FLAG-3 v0.2 fix).

Verdict alphabet per spec §10 line 520 (verbatim): ``PASS|WEAK|MARGINAL|
FAIL|INDISTINGUISHABLE``. HALT is a foreground action — not a verdict
value emitted to ``gate_verdict.json``.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Final, Mapping

import numpy as np
from numpy.typing import NDArray

from simulations.saas_builder.cohort_2._errors import (
    PPCQuantileMiscoverageError,
)
from simulations.saas_builder.cohort_2.derivatives import (
    DeltaNumericalEvaluator,
)
from simulations.saas_builder.cohort_2.types import (
    BracketGrid,
    BracketPoint,
    CohortGateVerdict,
    SignVerdict,
    VerdictLabel,
)

# ─── Module-level constants ───────────────────────────────────────────────────

#: Default credible-interval level (spec §9 TODO-COHORT-2).
DEFAULT_CI_LEVEL: Final[float] = 0.95

#: Pin (MQ-FLAG-3 v0.2 fix) — τ_t quantiles whose PPC coverage is checked.
PPC_QUANTILE_LEVELS: Final[tuple[float, float, float]] = (0.50, 0.90, 0.99)

#: PPC coverage tolerance band ±0.02 around the nominal 95% level
#: (MQ-FLAG-3 v0.2 fix; calibration ±0.02 implied: nominal 0.95).
PPC_COVERAGE_LOWER: Final[float] = 0.93
PPC_COVERAGE_UPPER: Final[float] = 0.97
PPC_NOMINAL_LEVEL: Final[float] = 0.95


# ─── Helpers ────────────────────────────────────────────────────────────────


def _credible_interval(
    delta_draws: NDArray[np.float64], ci_level: float
) -> tuple[float, float, float]:
    """Return ``(median, lower, upper)`` credible-interval bounds.

    Pure quantile-based (NOT bootstrap; spec §9 row TODO-COHORT-2
    explicitly forbids bootstrap).
    """
    if not (0.0 < ci_level < 1.0):
        raise ValueError(
            f"_credible_interval: ci_level = {ci_level} must lie in (0, 1)"
        )
    alpha = 1.0 - ci_level
    lower_q = alpha / 2.0
    upper_q = 1.0 - alpha / 2.0
    median = float(np.median(delta_draws))
    lower = float(np.quantile(delta_draws, lower_q))
    upper = float(np.quantile(delta_draws, upper_q))
    return (median, lower, upper)


def _audit_block_for(payload: bytes) -> str:
    """Compute sha256 of payload as 64-char lowercase hex."""
    return hashlib.sha256(payload).hexdigest()


def _now_utc_iso() -> str:
    """ISO-8601 UTC timestamp, second precision."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


# ─── Sign-certification gate ────────────────────────────────────────────────


#: Pin (MQ-BLOCK-1 v0.3 fix) — numerical-stability floor multiplier.
#: Δ_med must exceed ``factor · macheps · |q_max| · sum|f_t/(X/Y)²|``
#: in absolute value to be considered above the float64 noise floor;
#: factor 1e2 gives 2 decades of headroom over the analytic noise estimate.
NUMERICAL_STABILITY_FLOOR_FACTOR: Final[float] = 100.0


def numerical_stability_floor(
    bracket: BracketPoint,
    sigma_T: float,
    q_t_max: float,
) -> float:
    """Return the |Δ| floor below which sign certification is float64 noise.

    Per MQ-BLOCK-1 v0.3 fix: the catastrophic-cancellation noise floor
    on the closed-form Δ is

        ``noise ≈ T · macheps · |q_max| · max|f_t/(X/Y)²| · prefactor``

    where ``prefactor = 4 / (X̄/Ȳ · ε(σ_T))``. We multiply by
    ``NUMERICAL_STABILITY_FLOOR_FACTOR = 1e2`` to require ≥ 2 decades
    of headroom. A computed Δ_med whose magnitude is below this floor
    is route to ``FAIL`` with a numerical-stability tag (NOT silently
    PASS-routed).

    Args:
        bracket: the BracketPoint at which Δ was evaluated.
        sigma_T: realized-variance proxy.
        q_t_max: maximum |q_t| across the τ_t draws used in the gate.

    Returns:
        Floor magnitude (non-negative float). Δ values whose magnitude
        falls below this are treated as noise.
    """
    fxp = bracket.fx_params
    T = int(bracket.horizon_T)
    t_grid = np.arange(1, T + 1, dtype=np.float64)
    f_t = np.cos(fxp.omega * t_grid) ** 2 - 0.5
    x_over_y_t = (1.0 + fxp.epsilon * f_t) * fxp.mean_x_over_y
    weight = np.abs(f_t / (x_over_y_t ** 2))
    eps_sigma = math.sqrt(8.0 * sigma_T / fxp.mean_x_over_y ** 2)
    prefactor = 4.0 / (fxp.mean_x_over_y * eps_sigma)
    macheps = float(np.finfo(np.float64).eps)
    return (
        NUMERICAL_STABILITY_FLOOR_FACTOR
        * float(T)
        * macheps
        * abs(q_t_max)
        * float(weight.max())
        * prefactor
    )


@dataclass(frozen=True)
class SignCertificationGate:
    """Pin BRACKET-M5 sign-certification gate.

    For each ``BracketPoint`` supplied at call time, computes Δ^(a_s)
    over the posterior τ_t draws (shape ``(n_draws, T)``), then certifies
    via posterior-predictive 95% credible interval that
    ``delta_upper_bound_quantile < 0`` strictly. A single failure flips the
    verdict to ``FAIL`` and records ``n_sign_violations``.

    Verdict alphabet (spec §10 line 520): ``PASS|WEAK|MARGINAL|FAIL|
    INDISTINGUISHABLE``. The gate emits ``PASS`` if all bracket points
    strictly negative; ``FAIL`` otherwise. ``WEAK`` / ``MARGINAL`` /
    ``INDISTINGUISHABLE`` are reserved for future cohort-2 sub-verdicts
    (e.g. CI straddling zero with a robust median negative); the present
    implementation routes every non-PASS outcome to ``FAIL`` until those
    sub-verdicts are pinned by spec.

    API note (CR-BLOCKING-1 / MQ-BLOCK-3 v0.3 fix). The gate consumes a
    raw ``tuple[BracketPoint, ...]`` at ``__call__``-time, NOT a
    ``BracketGrid``. The primary path constructs a validated
    ``BracketGrid`` and passes its ``.points`` tuple; the bank-spread
    robustness arm passes overlaid points directly without needing the
    M5 anchor invariant. This avoids the ``object.__new__`` bypass.
    """

    sigma_T: float
    ci_level: float = DEFAULT_CI_LEVEL

    def __post_init__(self) -> None:
        if not (math.isfinite(self.sigma_T) and self.sigma_T > 0.0):
            raise ValueError(
                f"SignCertificationGate.sigma_T = {self.sigma_T}"
                " must be a finite float > 0"
            )
        if not (0.0 < self.ci_level < 1.0):
            raise ValueError(
                f"SignCertificationGate.ci_level = {self.ci_level}"
                " must lie in (0, 1)"
            )

    def __call__(
        self,
        points: tuple[BracketPoint, ...] | BracketGrid,
        tau_t_draws_per_bracket: tuple[NDArray[np.float64], ...],
        ppc_coverage: Mapping[str, float] | None = None,
    ) -> CohortGateVerdict:
        """Run the sign-certification gate over the bracket points.

        Args:
            points: tuple of BracketPoint (primary path passes
                ``grid.points``; robustness arm passes overlaid points).
                For backwards compatibility, a ``BracketGrid`` is also
                accepted and unwrapped to ``grid.points``.
            tau_t_draws_per_bracket: tuple of length ``len(points)``;
                each entry is a 2-D float64 array of shape ``(n_draws, T_i)``
                aligned with ``points[i].horizon_T``.
            ppc_coverage: optional pre-computed PPC coverage mapping for
                the {p50, p90, p99} τ_t quantiles. The gate does NOT
                re-compute coverage internally; it records what is
                provided. When ``None``, an empty mapping is recorded.

        Returns:
            ``CohortGateVerdict``.

        Raises:
            ValueError: shape mismatch between draws and points.
        """
        if isinstance(points, BracketGrid):
            bracket_points = points.points
        else:
            bracket_points = points
        n = len(bracket_points)
        if n < 1:
            raise ValueError(
                "SignCertificationGate: points must be non-empty"
            )
        if len(tau_t_draws_per_bracket) != n:
            raise ValueError(
                "SignCertificationGate: tau_t_draws_per_bracket length"
                f" {len(tau_t_draws_per_bracket)} must equal points size {n}"
            )

        evidence: list[SignVerdict] = []
        n_violations = 0
        for idx, (point, draws) in enumerate(
            zip(bracket_points, tau_t_draws_per_bracket, strict=True)
        ):
            evaluator = DeltaNumericalEvaluator(
                bracket=point, sigma_T=self.sigma_T
            )
            delta_draws = evaluator(draws)
            median, lower, upper = _credible_interval(
                delta_draws, self.ci_level
            )
            strict = upper < 0.0
            # Numerical-stability check (MQ-BLOCK-1 v0.3 fix). If |Δ_med|
            # falls below the noise floor, demote sign-strictly-negative
            # to False (route to FAIL) — a Δ at the float64 noise floor
            # is not a credible negative-sign certification.
            # Compute q_max from the actual composed q_t (uses the
            # numerically-stable softplus already wired into the evaluator).
            # The composer is reused from the evaluator.
            assert evaluator._composer is not None  # __post_init__ guarantees
            q_max_est = float(np.max(np.abs(evaluator._composer(draws))))
            floor = numerical_stability_floor(
                bracket=point, sigma_T=self.sigma_T, q_t_max=q_max_est
            )
            if abs(median) < floor:
                strict = False
            if not strict:
                n_violations += 1
            verdict_evidence = SignVerdict(
                bracket_index=idx,
                delta_median=median,
                delta_lower_bound_quantile=lower,
                delta_upper_bound_quantile=upper,
                sign_strictly_negative=strict,
                ci_level=self.ci_level,
            )
            evidence.append(verdict_evidence)

        verdict_label: VerdictLabel = "PASS" if n_violations == 0 else "FAIL"
        # Audit block — sha256 of the (verdict-label, evidence-tuple repr).
        payload = repr(
            (
                verdict_label,
                tuple(
                    (
                        ev.bracket_index,
                        ev.delta_median,
                        ev.delta_lower_bound_quantile,
                        ev.delta_upper_bound_quantile,
                        ev.sign_strictly_negative,
                        ev.ci_level,
                    )
                    for ev in evidence
                ),
            )
        ).encode("utf-8")
        return CohortGateVerdict(
            sub_task="COHORT-2",
            verdict=verdict_label,
            n_bracket_points=n,
            n_sign_violations=n_violations,
            evidence=tuple(evidence),
            audit_block=_audit_block_for(payload),
            fetched_at_utc=_now_utc_iso(),
            ppc_coverage=dict(ppc_coverage) if ppc_coverage else {},
        )


# ─── PPC quantile coverage check (MQ-FLAG-3 v0.2 fix) ────────────────────────


@dataclass(frozen=True)
class PPCQuantileCoverageCheck:
    """Posterior-predictive coverage diagnostic at pinned τ_t quantiles.

    Pin (MQ-FLAG-3 v0.2 fix; plan Task 2.5): at each of the user-relevant
    τ_t quantiles ``{50, 90, 99}``-pct, empirical coverage of the nominal
    95% credible interval must fall within ``[0.93, 0.97]`` (calibration
    tolerance ±0.02). Failure indicates the posterior CI is mis-calibrated
    and could absorb a near-zero Δ sign violation; the check raises
    :class:`PPCQuantileMiscoverageError` (HALT trigger).

    Computation: given ``(n_draws, T)`` posterior τ_t draws and a
    ``(n_obs, T)`` array of held-out τ_t observations (one held-out
    sample per posterior draw, paired by index), compute the empirical
    quantile τ_q across each draw / observation pair and verify that the
    fraction of observations falling within the per-draw 95% credible
    interval is within ``[0.93, 0.97]``.
    """

    nominal_level: float = PPC_NOMINAL_LEVEL
    coverage_lower: float = PPC_COVERAGE_LOWER
    coverage_upper: float = PPC_COVERAGE_UPPER

    def __post_init__(self) -> None:
        if not (0.0 < self.nominal_level < 1.0):
            raise ValueError(
                f"PPCQuantileCoverageCheck.nominal_level = {self.nominal_level}"
                " must lie in (0, 1)"
            )
        if not (
            0.0 < self.coverage_lower
            < self.nominal_level
            < self.coverage_upper
            < 1.0
        ):
            raise ValueError(
                "PPCQuantileCoverageCheck: must satisfy 0 < coverage_lower"
                " < nominal_level < coverage_upper < 1;"
                f" got ({self.coverage_lower}, {self.nominal_level},"
                f" {self.coverage_upper})"
            )

    def __call__(
        self,
        ppc_draws: NDArray[np.float64],
        observed_quantiles: Mapping[str, NDArray[np.float64]],
    ) -> dict[str, float]:
        """Return per-quantile τ_q empirical coverage; raise on miscoverage.

        Per CR-BLOCKING-3 v0.3 fix: compute the q-th percentile τ_q of
        each posterior-predictive draw (row), then build the per-draw
        95% CI of those τ_q values across the ``n_ppc`` axis, and check
        what fraction of the held-out observed τ_q values fall inside
        that interval. The keys ``"p50"|"p90"|"p99"`` now drive distinct
        computations (q ∈ {0.50, 0.90, 0.99}).

        Args:
            ppc_draws: 2-D float64 array of shape ``(n_ppc, n_obs)`` —
                posterior-predictive τ_t draws across observation
                replicates. Each row is one posterior draw's τ_t vector
                across the ``n_obs`` time/observation index.
            observed_quantiles: mapping from ``"p50"|"p90"|"p99"`` to a
                1-D float64 array of length ``n_obs`` holding the
                observed τ_t quantile per replicate (independent
                held-out samples used for coverage assessment).

        Returns:
            Mapping ``{"p50": coverage, "p90": coverage, "p99": coverage}``
            of empirical coverage values in ``[0, 1]``.

        Raises:
            ValueError: input-shape mismatch.
            PPCQuantileMiscoverageError: any quantile's coverage outside
                ``[coverage_lower, coverage_upper]``.
        """
        if ppc_draws.ndim != 2:
            raise ValueError(
                f"PPCQuantileCoverageCheck: ppc_draws.ndim = {ppc_draws.ndim}"
                " must be 2"
            )
        n_ppc, n_obs = ppc_draws.shape
        if n_ppc < 1 or n_obs < 1:
            raise ValueError(
                f"PPCQuantileCoverageCheck: ppc_draws.shape = {ppc_draws.shape}"
                " must have positive size on both axes"
            )

        alpha = 1.0 - self.nominal_level
        lower_q = alpha / 2.0
        upper_q = 1.0 - alpha / 2.0

        coverage: dict[str, float] = {}
        for key, level in zip(("p50", "p90", "p99"), PPC_QUANTILE_LEVELS):
            if key not in observed_quantiles:
                raise ValueError(
                    f"PPCQuantileCoverageCheck: observed_quantiles missing"
                    f" key {key!r}"
                )
            obs = observed_quantiles[key]
            if obs.ndim != 1 or obs.shape[0] < 1:
                raise ValueError(
                    "PPCQuantileCoverageCheck: observed_quantiles"
                    f" [{key!r}] shape = {obs.shape} must be 1-D"
                    " with positive length (one held-out τ_q per replicate)"
                )
            # Per-row sample q-th percentile of each posterior-predictive
            # draw (axis=1 ⇒ along n_obs): yields shape (n_ppc,) — one
            # τ_q estimate per posterior draw.
            tau_q_per_draw = np.quantile(ppc_draws, level, axis=1)
            # Build a 95% CI of τ_q across the posterior-draw axis.
            ci_lo = float(np.quantile(tau_q_per_draw, lower_q))
            ci_hi = float(np.quantile(tau_q_per_draw, upper_q))
            # Coverage = fraction of held-out observed τ_q values within CI.
            in_band = (obs >= ci_lo) & (obs <= ci_hi)
            coverage[key] = float(np.mean(in_band))

        # Threshold check.
        for key, cov in coverage.items():
            if not (self.coverage_lower <= cov <= self.coverage_upper):
                raise PPCQuantileMiscoverageError(
                    "PPCQuantileCoverageCheck: empirical coverage at"
                    f" quantile {key} = {cov:.4f} outside band"
                    f" [{self.coverage_lower}, {self.coverage_upper}];"
                    " HALT per anti-fishing"
                    " (feedback_pathological_halt_anti_fishing_checkpoint)"
                )
        return coverage


__all__ = [
    "DEFAULT_CI_LEVEL",
    "NUMERICAL_STABILITY_FLOOR_FACTOR",
    "PPCQuantileCoverageCheck",
    "PPC_COVERAGE_LOWER",
    "PPC_COVERAGE_UPPER",
    "PPC_NOMINAL_LEVEL",
    "PPC_QUANTILE_LEVELS",
    "SignCertificationGate",
    "numerical_stability_floor",
]
