"""Cohort-4 typed errors.

Per functional-python skill: only Exception subclassing is admitted as
class-inheritance outside of Protocols.
"""

from __future__ import annotations


class DiagnosticGateError(Exception):
    """Raised by SAAS-COHORT-4 when a sign-verdict or MC-budget gate fires HALT.

    Per ``feedback_pathological_halt_anti_fishing_checkpoint``: any sign
    violation across the 5 pinned test points OR any CI lower bound ≤ 0
    OR an MC stderr/Ẑ > 1e-3 floor at N_draws ≥ 4000 routes through this
    error class to surface to the foreground harness.
    """


class IdentityToleranceError(Exception):
    """Raised when the ``π(t)·Δt − ΔΠ`` identity exceeds Pin M2 tolerance.

    Symbolic: ≤ 1e-10 · N_legs (PRIMITIVES.md §12 ledger inheritance).
    Numerical: ≤ 1e-6 (Path A v0 §10.4 inheritance).
    """


class AuditBlockDriftError(Exception):
    """Raised when the recomputed audit-block sha256 disagrees with a recorded one.

    Pin M4 enforcement of post-PASS file-mutation detection. NEVER swallowed.
    """


class MCErrorBudgetExceededError(Exception):
    """Raised when ``stderr(Ẑ)/Ẑ > 1e-3`` with N_draws ≥ 4000 (Pin M2-fix).

    Distinct from the identity-tolerance gate; covers MC integration of the
    posterior-predictive expectation only.
    """


class RoundTripDriftError(Exception):
    """Raised by ``pin_and_emit`` when the JSON round-trip breaks equality.

    Phase-3 close (CR NIT-3 v0.3 sweep): replaces the prior bare
    ``RuntimeError`` raised on ``pin_and_emit`` round-trip equality
    breach. Routes consistently with :class:`AuditBlockDriftError`
    so both sidecar-equality failures expose a typed cohort-4 error
    class to the foreground harness.
    """


__all__ = [
    "AuditBlockDriftError",
    "DiagnosticGateError",
    "IdentityToleranceError",
    "MCErrorBudgetExceededError",
    "RoundTripDriftError",
]
