"""Value-tier types for the verify-only API.

Per design v0.3 §3a.2. Two new Values:
- ``RTagVerdict`` — verdict container returned by every verifier
- ``TrioRollup`` — end-of-trio summary aggregate

All committed-artifact data classes are reused from existing
``simulations.types``: ``ZCapPinned``, ``CohortGateVerdict``,
``RevenueFormFit``, ``Audit``. No new TypedDicts.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RTagVerdict:
    """Verdict for a single R-tag in the math×code trio.

    ``audit_sha256`` is non-Optional (per design v0.3 §3a.4.1 uniform
    tamper contract); every verifier including sympy-only ones binds
    the trio-level anchor.
    """

    r_tag: str
    passed: bool
    expected: float | None
    actual: float | None
    residual: float | None
    audit_sha256: str
    message: str


@dataclass(frozen=True)
class TrioRollup:
    """Aggregate of all 8 R-tag verdicts for a single notebook run."""

    verdicts: tuple[RTagVerdict, ...]
    all_passed: bool
    audit_sha256: str
