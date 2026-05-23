"""Cohort-local typed exceptions for SAAS-COHORT-2.

These exceptions tag IO and math-pin violations in a way callers can catch
without conflating with generic ``ValueError`` from upstream Value-type
construction. Per the functional-python skill, ``Exception`` subclassing
is the only inheritance form admitted in user code apart from ``Protocol``.
"""

from __future__ import annotations


class M2TightnessNotAchievedError(ValueError):
    """Raised when the softplus-β fitter cannot satisfy Pin M2 on the grid.

    Pin M2 (spec §5.1 (T2)): the L¹ deviation of ``softplus_β`` from ReLU
    on the support ``[0, 2 κ]`` must be strictly less than ``1e-3 · κ``.
    Pin M2-fit (plan v0.2 Phase 2 prelude) bounds the search grid at
    ``β ∈ [0.01/κ, 100/κ]`` (50 log-spaced points). When NO grid point
    satisfies M2, the fitter raises this exception rather than silently
    widening the grid (anti-fishing per
    ``feedback_pathological_halt_anti_fishing_checkpoint``).

    Subclasses ``ValueError`` so existing ``except ValueError`` clauses
    continue to catch it; the typed name disambiguates Pin M2 violations
    from arbitrary parameter validation errors.
    """


class FXPathReconstructionError(ValueError):
    """Raised when an FX path fails the M5 path-reconstruction check.

    Pin BRACKET-M5 (plan v0.2 Phase 2 prelude; cross-references shipped
    ``simulations/tests/test_modules.py:185,194``): the M5 sinusoidal FX
    path with TRM-pinned ``X̄/Ȳ`` MUST recover the values
    ``(4200, 3800, 4200)`` at sample times ``t ∈ {0, π/2, π}`` within
    ``1e-9`` tolerance. Construction of a ``BracketGrid`` over a path that
    fails this check is a Pin BRACKET-M5 violation; this exception is the
    runtime guard.
    """


class SignCertificationFailureError(RuntimeError):
    """Raised when the sign-certification gate's symbolic / numerical reconciler diverges.

    Pin Δ-cohort (PRIMITIVES.md §11.b tolerance ``1e-10 · N_terms``): if
    the closed-form symbolic Δ^(a_s) and the hand-coded numerical
    evaluator disagree by more than the tolerance at the reconciliation
    point, the implementation has a closed-form bug and the gate cannot
    proceed. Foreground HALTs per
    ``feedback_pathological_halt_anti_fishing_checkpoint``.
    """


class PPCQuantileMiscoverageError(RuntimeError):
    """Raised when posterior-predictive coverage at a pinned τ_t quantile drifts out of band.

    Pin (MQ-FLAG-3 v0.2 fix; plan Task 2.5 contract): empirical coverage
    of the nominal 95% credible interval at each of ``{50, 90, 99}``-pct
    τ_t must fall within ``[0.93, 0.97]`` (calibration tolerance ±0.02).
    Miscoverage indicates the posterior CI is mis-calibrated and could
    silently absorb a near-zero sign violation in the Δ gate; HALT per
    ``feedback_pathological_halt_anti_fishing_checkpoint``.
    """


__all__ = [
    "FXPathReconstructionError",
    "M2TightnessNotAchievedError",
    "PPCQuantileMiscoverageError",
    "SignCertificationFailureError",
]
