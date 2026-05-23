"""Stochastic-FX typed errors.

Per functional-python skill: only Exception subclassing is admitted as
class-inheritance outside of Protocols. Parent spec
``docs/specs/2026-05-11-stochastic-fx-variant-design.md`` v0.3 defines
Pin Z1.3b (moment match), Pin Z1.4 (KS inversion), and the N=1000 MC
floor (§8 anti-fishing) gated by these error classes.
"""

from __future__ import annotations


class StochasticFXError(Exception):
    """Base class for the stochastic-fx package (gates Pin Z1 family)."""


class SDEParameterError(StochasticFXError):
    """Raised when an SDE Parameters frozen-dc ``__post_init__`` rejects invalid inputs."""


class InversionTestFailedError(StochasticFXError):
    """Raised by Pin Z1.4 KS goodness-of-fit gate failures."""


class MomentMatchFailedError(StochasticFXError):
    """Raised by Pin Z1.3b moment-match gate failures."""


class MCBudgetExceededError(StochasticFXError):
    """Raised when ``ensemble.paths.shape[0] != 1000`` at InversionVerifier construction (Pin Z1 N=1000 floor)."""


class RoundTripDriftError(StochasticFXError):
    """Raised when an IO-Boundary-tier emitter's write→read→equality check breaks.

    Task 5 NIT-RC-Task5 disposition (plan v0.6 §14 HALT routing): every
    emitter in :mod:`simulations.stochastic_fx.emit` is required to be
    round-trip-faithful at the byte level (parquet metadata) and at the
    field-by-field level (JSON sidecars). Any drift surfaces here so the
    foreground harness halts cleanly rather than silently degrading the
    audit trail. Mirrors :class:`simulations.saas_builder.cohort_4._errors.RoundTripDriftError`.
    """


__all__ = [
    "InversionTestFailedError",
    "MCBudgetExceededError",
    "MomentMatchFailedError",
    "RoundTripDriftError",
    "SDEParameterError",
    "StochasticFXError",
]
