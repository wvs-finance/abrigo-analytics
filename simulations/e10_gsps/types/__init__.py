"""E10 GSPS — Value tier (frozen-dataclass containers + Protocols).

Per plan v0.2 Phase 0.3. NO logic here — only data containers and
structural Protocols. Tier-import discipline forbids imports from
``..modules`` or ``..utils``.
"""

from __future__ import annotations

from .decomposition import ThreeWayDecompositionCell
from .fx import (
    PANEL_CURRENCIES,
    PANEL_WINDOW,
    CurrencyDailyFXRow,
    MonthlyRealizedVarianceCell,
    PanelWindowDiagnostics,
)
from .nhpp import (
    CostStreamTrajectory,
    LambdaModulationForm,
    LambdaModulationSpec,
    NHPPIntensityParameters,
)
from .panel import PanelCell
from .protocols import (
    DescriptiveVerdictClassifier,
    NHPPSimulationEngine,
    RegimeBreakScreen,
    SurfaceGridEvaluator,
    ThreeWayDecomposition,
)
from .surface import SurfaceGridPoint, SurfaceGridResult
from .verdict import DescriptiveVerdict, DescriptiveVerdictResult

__all__ = [
    "PANEL_CURRENCIES",
    "PANEL_WINDOW",
    "CurrencyDailyFXRow",
    "MonthlyRealizedVarianceCell",
    "PanelWindowDiagnostics",
    "LambdaModulationForm",
    "LambdaModulationSpec",
    "NHPPIntensityParameters",
    "CostStreamTrajectory",
    "PanelCell",
    "ThreeWayDecompositionCell",
    "SurfaceGridPoint",
    "SurfaceGridResult",
    "DescriptiveVerdict",
    "DescriptiveVerdictResult",
    "RegimeBreakScreen",
    "NHPPSimulationEngine",
    "ThreeWayDecomposition",
    "SurfaceGridEvaluator",
    "DescriptiveVerdictClassifier",
]
