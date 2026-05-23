"""Bank-spread robustness arm Callable for SAAS-COHORT-2 (Pin ROBUST-BS).

Implements:

- :class:`BankSpreadRobustnessRunner` — re-runs the sign-certification
  gate under a multiplicative bank-spread overlay on the FX path
  ``(X/Y)_t · (1 + s_t)`` per spec §3 sensitivity row + §5.4(c). The
  result is returned as a separate :class:`CohortGateVerdict`; it MUST
  NOT overwrite the primary verdict (Pin ROBUST-BS — RC-BLOCK-3 v1.1
  spec demoted bank-spread from primary to sensitivity).

The overlay is implemented as a *per-bracket FX-path mutation*: for each
``BracketPoint`` in the input grid, a sibling ``BracketPoint`` is
constructed with ``mean_x_over_y · (1 + s)`` (multiplicative spread on
the rate, broadcast across t for additivity simplicity in the
sensitivity arm). Spec §3 sensitivity row + §5.4(c) describe a
time-varying ``s_t``; the implementation accepts a scalar ``s`` for the
default sensitivity sweep — a future arm extending to time-varying
``s_t`` would extend ``FXPathParams`` rather than this Callable.

Tier-import discipline: imports allowed from
``simulations.saas_builder.cohort_2.{_errors, types, sign_cert}`` and
from ``simulations.{types, modules, utils}``. MUST NOT import from
``simulations.saas_builder.cohort_2.io``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Mapping

import numpy as np
from numpy.typing import NDArray

from simulations.saas_builder.cohort_2.sign_cert import (
    DEFAULT_CI_LEVEL,
    SignCertificationGate,
)
from simulations.saas_builder.cohort_2.types import (
    BracketGrid,
    BracketPoint,
    CohortGateVerdict,
)
from simulations.types.fx import FXPathParams

#: Pin ROBUST-BS — default scalar bank-spread used in the sensitivity arm
#: (∼ 50 bps spread on FX rate as a representative midpoint of the
#: spec §5.4(c) range; the exact float is a sensitivity-arm dial, not a
#: math-pinned threshold).
DEFAULT_BANK_SPREAD: Final[float] = 0.005


@dataclass(frozen=True)
class BankSpreadRobustnessRunner:
    """Pin ROBUST-BS — bank-spread sensitivity arm runner.

    Mutates the FX path's ``mean_x_over_y`` by a multiplicative
    ``(1 + bank_spread)`` factor and re-runs the sign-certification gate.
    The resulting verdict is *separate* from the primary; callers persist
    it to ``ROBUSTNESS_RESULTS.md``, NEVER to ``gate_verdict.json``.

    Note on M5 path-reconstruction (CR-BLOCKING-1 / MQ-BLOCK-3 v0.3 fix):
    the M5 anchor values ``(4200, 3800, 4200)`` are only recovered when
    ``X̄/Ȳ = 4000`` and ``ε = 0.1``. After the bank-spread mutation,
    ``X̄/Ȳ_overlaid = 4000 · (1 + s)``; the M5 anchor reconstruction
    will NO LONGER hold — this is BY DESIGN. v0.3 routes the overlaid
    points through ``SignCertificationGate`` via the new tuple-of-points
    call signature (``gate(points, draws, ...)``); no ``BracketGrid``
    construction, no ``object.__new__`` bypass, no frozen-dataclass
    invariant violation.
    """

    bank_spread: float = DEFAULT_BANK_SPREAD
    ci_level: float = DEFAULT_CI_LEVEL

    def __post_init__(self) -> None:
        if not math.isfinite(self.bank_spread):
            raise ValueError(
                f"BankSpreadRobustnessRunner.bank_spread = {self.bank_spread}"
                " must be finite"
            )
        if abs(self.bank_spread) >= 1.0:
            raise ValueError(
                f"BankSpreadRobustnessRunner.bank_spread = {self.bank_spread}"
                " must satisfy |s| < 1 (multiplicative overlay)"
            )
        if not (0.0 < self.ci_level < 1.0):
            raise ValueError(
                f"BankSpreadRobustnessRunner.ci_level = {self.ci_level}"
                " must lie in (0, 1)"
            )

    def __call__(
        self,
        primary_grid: BracketGrid,
        sigma_T: float,
        tau_t_draws_per_bracket: tuple[NDArray[np.float64], ...],
        ppc_coverage: Mapping[str, float] | None = None,
    ) -> CohortGateVerdict:
        """Re-run the sign-certification gate under the bank-spread overlay.

        Args:
            primary_grid: the BracketGrid used by the primary gate.
            sigma_T: realized-variance proxy.
            tau_t_draws_per_bracket: posterior τ_t draws aligned with
                ``primary_grid.points``.
            ppc_coverage: optional pre-computed PPC coverage mapping;
                forwarded into the verdict (not re-computed here).

        Returns:
            ``CohortGateVerdict`` whose verdict is the sign-cert outcome
            on the overlaid FX paths.

        Raises:
            ValueError: shape mismatch.
        """
        # Construct sibling BracketPoints with overlaid FX-mean. We do
        # NOT wrap them in a BracketGrid: anchor recovery would fail
        # (mean·(1+s) ≠ 4000) — and the gate's new v0.3 API takes a raw
        # tuple of points directly, so no BracketGrid construction nor
        # object.__new__ bypass is needed. The frozen-dataclass invariant
        # on BracketGrid is preserved.
        overlaid_points = tuple(
            _overlay_bracket_point(p, self.bank_spread)
            for p in primary_grid.points
        )
        gate = SignCertificationGate(
            sigma_T=sigma_T, ci_level=self.ci_level
        )
        return gate(
            overlaid_points,
            tau_t_draws_per_bracket,
            ppc_coverage=ppc_coverage,
        )


def _overlay_bracket_point(
    point: BracketPoint, bank_spread: float
) -> BracketPoint:
    """Return a sibling BracketPoint with FX mean × (1 + bank_spread).

    Per Pin ROBUST-BS the mutation is multiplicative on
    ``mean_x_over_y``; ``ε`` and ``ω`` are unchanged.
    """
    fxp = point.fx_params
    overlaid = FXPathParams(
        mean_x_over_y=fxp.mean_x_over_y * (1.0 + bank_spread),
        epsilon=fxp.epsilon,
        omega=fxp.omega,
    )
    return BracketPoint(
        cost_params=point.cost_params,
        fx_params=overlaid,
        horizon_T=point.horizon_T,
    )


__all__ = [
    "BankSpreadRobustnessRunner",
    "DEFAULT_BANK_SPREAD",
]
