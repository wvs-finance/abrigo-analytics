"""Cohort-local typed exceptions for SAAS-COHORT-3."""

from __future__ import annotations


class CandidateSetClosedError(RuntimeError):
    """Raised when a 4th Υ_t form is registered with the fit driver.

    Pin R6 / spec §8(5) anti-fishing: the candidate set
    ``{martingale, ar1_log, det_churn}`` is CLOSED. Adding a fourth form is
    an anti-fishing violation; this exception is the runtime guard.
    """


class LfoCvUnavailableError(RuntimeError):
    """Raised when LFO-CV refit is requested but ``arviz`` lacks utilities.

    Pin R3 / CORRECTIONS-α §15.3: the LFO-CV refit branch requires
    ``arviz`` LFO-CV utilities. If absent, foreground HALTs per
    ``feedback_pathological_halt_anti_fishing_checkpoint``.
    """


class RhoBoundaryHaltError(RuntimeError):
    """Raised when AR(1)-log posterior tail-mass on |ρ|>0.95 exceeds 0.20.

    Pin R4-bis / CORRECTIONS-α §15.4: posterior mass piling up at the
    stationarity boundary indicates AR(1)-log is mis-fitting the data.
    HALT per ``feedback_pathological_halt_anti_fishing_checkpoint``.
    """


class SchemaMismatchError(ValueError):
    """Raised when on-disk parquet/JSON schema diverges from Pin R5."""


__all__ = [
    "CandidateSetClosedError",
    "LfoCvUnavailableError",
    "RhoBoundaryHaltError",
    "SchemaMismatchError",
]
