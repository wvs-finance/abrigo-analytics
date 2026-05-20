"""Cohort-local typed exceptions for the E10 GSPS v0.4 iteration.

Lives at the sub-package root (not in shared infrastructure) per the
SIM-INFRA-0 rule: cohort-internal exceptions are part of the cohort
surface, not shared infrastructure.

Each exception below carries a specific Phase-0 -> Phase-6 failure mode
identified in plan v0.2 (Phase 0.1 deliverable). The error families map
1:1 to the failing-test harnesses of tasks 0.4-0.9.
"""

from __future__ import annotations


class PanelCurrencyCoverageError(RuntimeError):
    """Raised when a panel currency's free post-regime-break qualifying
    daily central-bank FX series falls below the ~30-month panel target
    (spec v0.4 §3.3 / §10 E10.0; plan §1 Phase 1.4). Routes to PARTIAL or
    NON-RETIREMENT per the spec §9 descriptive ladder — never engineered
    away by a window extension."""


class RegimeBreakScreenError(RuntimeError):
    """Raised when the regime-break screen cannot confine a currency to a
    qualifying post-structural-break float regime — e.g. an NGN series
    that cannot be confined to its post-June-2023 float window, or a
    GHS/KES managed-float period that cannot be screened out (spec v0.4
    §3.3). The screen never silently mixes a peg regime with a float
    regime in one realized-variance series."""


class NHPPCalibrationError(RuntimeError):
    """Raised when the R6 NHPP query-workflow simulation engine cannot
    calibrate the representative-analyst Q-process to the §6.2
    NON-FANTASY observed-trace anchor — optimizer failure, sparse-bin
    collapse, or a lambda(t) modulation form that does not fit. Distinct
    from SimulatorAnchorError, which is the data-availability failure."""


class SimulatorAnchorError(RuntimeError):
    """Raised when the simulator cannot be anchored to the §6.2
    NON-FANTASY profile because the user's observed query trace is thin
    or non-representative (spec v0.4 §7 field 7a / RC OBS-1). Routes to
    NON-RETIREMENT per spec §9 — there is no default-priors escape hatch."""


class DecompositionIdentityError(RuntimeError):
    """Raised when the exact §4.2 three-way log-variance decomposition's
    additive identity ``Var(d log cost) = Var(d log FX) + Var(d log Q)
    + 2*Cov`` fails to hold exactly — typically because X and the
    Q-component were differenced on mismatched sub-monthly grids (spec
    v0.4 §4.2; plan CORR-E10P-3 / task 3.0). The identity holds exactly
    only on the common differencing grid."""


class SurfaceGridError(RuntimeError):
    """Raised when the FX-variance-share surface cannot be evaluated on a
    grid across the whole anchored Q-volume range (DV-gate fail or a
    material data gap; spec v0.4 §7 field 7c). Routes to PARTIAL or
    NON-RETIREMENT per spec §9."""


class DescriptiveVerdictError(RuntimeError):
    """Raised when the descriptive-verdict classifier is asked to emit an
    inferential beta verdict, a confirmatory ``PASS``, or any state
    outside the §9 collectively-exhaustive descriptive ladder
    (SURFACE-PRODUCED / PARTIAL / NON-RETIREMENT). E10 v0.4 makes no
    inferential beta claim; emission of one is structurally BANNED, not a
    runtime warning."""


class DataVisibilityRevokedError(RuntimeError):
    """Raised when any of the 8 central-bank FX series, the x402 price
    probe, or The Graph free tier goes dark / paywalled / auth-gated
    mid-execution (spec v0.4 §1 HALT-DV; plan §3 HALT-DV). Triggers a
    disposition memo and DV re-classification to PASS-QUOTED or BLOCK.
    NO silent migration to alternative providers."""


__all__ = [
    "PanelCurrencyCoverageError",
    "RegimeBreakScreenError",
    "NHPPCalibrationError",
    "SimulatorAnchorError",
    "DecompositionIdentityError",
    "SurfaceGridError",
    "DescriptiveVerdictError",
    "DataVisibilityRevokedError",
]
