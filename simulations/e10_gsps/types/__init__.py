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
from .currency_spread import CurrencySpreadResult
from .panel import PanelCell
from .sensitivity_arms import (
    ArmName,
    ConcordanceVerdict,
    SensitivityArmResult,
    SensitivityArmsResult,
)
from .protocols import (
    DescriptiveVerdictClassifier,
    NHPPSimulationEngine,
    RegimeBreakScreen,
    SurfaceGridEvaluator,
    ThreeWayDecomposition,
)
from .surface import (
    InteriorCrossingResult,
    SurfaceGridPoint,
    SurfaceGridResult,
)
from .verdict import DescriptiveVerdict, DescriptiveVerdictResult
from .vol_on_vol import VolOnVolResult

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
    "InteriorCrossingResult",
    "VolOnVolResult",
    "CurrencySpreadResult",
    "ArmName",
    "ConcordanceVerdict",
    "SensitivityArmResult",
    "SensitivityArmsResult",
    "DescriptiveVerdict",
    "DescriptiveVerdictResult",
    "RegimeBreakScreen",
    "NHPPSimulationEngine",
    "ThreeWayDecomposition",
    "SurfaceGridEvaluator",
    "DescriptiveVerdictClassifier",
]
