"""Cohort-5-strip typed errors.

Per the functional-python skill, only ``Exception`` subclassing is
admitted as class-inheritance outside of Protocols. These exceptions
gate the math-to-position translator that emits the 12-leg IronCondor
strip JSON artifact consumed by the contracts-side Foundry deployment.
"""

from __future__ import annotations


class StripGeometryError(Exception):
    """Raised when an IronCondor's strike ladder violates K1 < K2 < K3 < K4.

    Also raised when the strip's log-offset triple does not span left
    tail / ATM / right tail (the strict-ordering invariant of
    PRIMITIVES.md §11 N=3 strip).
    """


class WeightNormalizationError(Exception):
    """Raised when Carr-Madan weights do not satisfy the §10 1/K_j² scaling.

    The weights MUST be strictly positive and MUST sum to exactly 1.0
    (after normalization to a unit-notional strip). A non-normalized
    weight set is a derivation bug, not a tolerance issue.
    """


class ReplicationToleranceError(Exception):
    """Raised when ‖Π_realized − K̂·σ_T‖ exceeds Path A v2 §11.b envelope.

    Replication tolerance per PRIMITIVES.md §12: max relative error
    ≤ 5% over the (ε, ω) grid points evaluated. A breach here means
    the discrete strip geometry is too coarse to replicate the
    linearized payoff and must be re-pinned at a finer N or wider span.
    """


class AuditBlockDriftError(Exception):
    """Raised when the recomputed strip audit-block disagrees with a recorded one.

    Mirror of cohort_4 enforcement: the strip artifact MUST be
    bit-reproducible from the canonical cohort-4 inputs + the
    strip-geometry parameters. NEVER swallowed.
    """


__all__ = [
    "AuditBlockDriftError",
    "ReplicationToleranceError",
    "StripGeometryError",
    "WeightNormalizationError",
]
