"""Structural Protocols for the E10 GSPS callable tier (spec v0.4 §6, §4).

Protocol is the ONLY inheritance permitted in the types tier per the
``functional-python`` discipline (alongside Exception / private-Pydantic
/ TypedDict elsewhere). These describe the __call__ shape each Phase-1+
module must satisfy; they pin the contract, not the implementation.
"""

from __future__ import annotations

from typing import Protocol

from .decomposition import ThreeWayDecompositionCell
from .fx import CurrencyDailyFXRow, MonthlyRealizedVarianceCell
from .nhpp import CostStreamTrajectory, NHPPIntensityParameters
from .surface import SurfaceGridResult
from .verdict import DescriptiveVerdictResult


class RegimeBreakScreen(Protocol):
    """Panel-currency verification + regime-break screen (plan task 1.2).

    Confines each currency to its qualifying post-structural-break float
    window and emits the per-currency qualifying-window start date.

    Note (M-4): the contract pins only the positional ``rows`` argument.
    An implementation MAY add keyword-only parameters with defaults — the
    Phase-1 ``RegimeBreakScreenModule`` adds ``allow_mixed_regime: bool =
    True`` — and still satisfies this Protocol structurally, since a
    caller using the Protocol shape never supplies the extra keyword.
    """

    def __call__(
        self, rows: tuple[CurrencyDailyFXRow, ...]
    ) -> tuple[CurrencyDailyFXRow, ...]: ...


class NHPPSimulationEngine(Protocol):
    """R6 NHPP query-workflow simulation engine (plan task 2.1).

    Generates the representative-analyst Q-process against a real FX
    path, emitting a per-(currency, month) cost-stream trajectory. Q is
    the only generated quantity.
    """

    def __call__(
        self,
        params: NHPPIntensityParameters,
        currency: str,
        year: int,
        month: int,
        daily_fx_rate: tuple[float, ...],
    ) -> CostStreamTrajectory: ...


class ThreeWayDecomposition(Protocol):
    """Exact §4.2 three-way log-variance decomposition (plan task 3.3).

    Computes the additive identity Var(d log cost) = Var(d log FX) +
    Var(d log Q) + 2*Cov on a common X/Q differencing grid.
    """

    def __call__(
        self,
        fx_cell: MonthlyRealizedVarianceCell,
        trajectory: CostStreamTrajectory,
    ) -> ThreeWayDecompositionCell: ...


class SurfaceGridEvaluator(Protocol):
    """FX-variance-share surface-grid evaluator (plan tasks 4.2 / 4.2a).

    Evaluates the share on a grid across the whole anchored Q-volume
    range and scans every cell for an interior crossing below break-even.
    """

    def __call__(
        self,
        decomposition_cells: tuple[ThreeWayDecompositionCell, ...],
        break_even_share: float,
        grid_resolution: float,
    ) -> SurfaceGridResult: ...


class DescriptiveVerdictClassifier(Protocol):
    """Descriptive-verdict classifier (plan tasks 0.8 / 6.1).

    Maps the six §9 flags to exactly one of SURFACE-PRODUCED / PARTIAL /
    NON-RETIREMENT. Cannot emit an inferential beta verdict.
    """

    def __call__(
        self,
        *,
        surface_computed: bool,
        material_gap: bool,
        simulator_anchored: bool,
        q_variance_dominates: bool,
        interior_crossing: bool,
        dv_gate_passed: bool,
    ) -> DescriptiveVerdictResult: ...
