"""Cohort-local typed exceptions for SAAS-COHORT-1.

Lives here (not in ``simulations.utils.errors``) per the plan's
"Any extension to ``simulations/{types,modules,utils}/`` infrastructure
— SIM-INFRA-0 follow-up" rule. Cohort-internal exceptions are not
infrastructure; they are part of the cohort surface.
"""

from __future__ import annotations


class DiagnosticGateError(RuntimeError):
    """Raised when posterior emission is attempted on a failing diagnostic verdict.

    Carries the failing :class:`simulations.saas_builder.diagnostics.DiagnosticVerdict`
    so callers can inspect which gate(s) tripped (r-hat, ESS_bulk, ESS_tail,
    divergence, sim-count floor, or §8(7) posterior-vs-prior CI-width ratio).
    Subclasses ``RuntimeError`` because diagnostic failure is a runtime
    pre-condition violation at the emission boundary, not a typed-input
    error (``ValueError``) or an IO schema drift (``SchemaMismatchError``).
    """


__all__ = ["DiagnosticGateError"]
