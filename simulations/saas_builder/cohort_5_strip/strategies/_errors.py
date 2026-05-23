"""Cohort-5-strip strategies sub-package typed errors.

Per the functional-python skill, only ``Exception`` subclassing is
admitted as class-inheritance outside of Protocols. These exceptions
gate the Stage-3 Track A1 alternative-strategy comparability lane:
non-reverse-IC primitives may only be compared to the canonical
reverse-IC strip via one of three pre-committed comparability proofs
(``tiled_body``, ``primitive_variant``, ``normalized_score``).

A missing proof is a SPEC violation (the adapter author forgot to
declare which lane applies). A FALSIFIED proof is a RUNTIME violation
(the adapter declared ``tiled_body`` but the built strip fails the
long-vol signature). Both are gating; neither is swallowed.
"""

from __future__ import annotations


class StrategyAdapterError(Exception):
    """Base class for the cohort_5_strip.strategies sub-package.

    Subclasses gate the alternative-strategy comparability lane:
    a strategy adapter that produces an ``IronCondorStrip`` must
    declare which comparability proof applies to its primitive and
    supply the matching evidence (a primitive-specific verifier for
    ``primitive_variant``; a Pin S5 long-vol signature pass for
    ``tiled_body``; a finite normalized-score scalar for
    ``normalized_score``).
    """


class ComparabilityProofMissingError(StrategyAdapterError):
    """Raised when a strategy adapter omits its comparability proof.

    Two trigger conditions:

    1. The adapter result has no ``comparability_proof`` declaration
       (the spec-violation case — the author forgot to commit to one
       of the three Wave-1 pre-registered lanes).
    2. The adapter declares ``comparability_proof = "primitive_variant"``
       but no :class:`PrimitiveVariantVerifier` is supplied to the
       evaluation pipeline (the missing-evidence case — primitive-
       variant proofs require an explicit, primitive-specific
       envelope verifier per Task 2.3b).

    Anti-fishing invariant: NEVER silently fall back to the
    ``normalized_score`` lane when ``primitive_variant`` evidence
    is missing — that would be a post-hoc lane swap.
    """


class ComparabilityProofFalsifiedError(StrategyAdapterError):
    """Raised when a tiled_body comparability claim is empirically false.

    Trigger condition: an adapter declares
    ``comparability_proof = "tiled_body"`` (i.e., it asserts that its
    built strip satisfies Pin S5 — ``Π_strip(S_0) = 0`` plus positive
    payoff on both sides of the body) but the runtime check via
    ``assert_long_vol_signature`` raises ``ReplicationToleranceError``.

    Distinct from :class:`ComparabilityProofMissingError`: the claim
    is PRESENT, but FALSE. A false claim is a strictly worse failure
    mode than a missing claim and is recorded as such for Wave-1
    re-review.
    """


__all__ = [
    "ComparabilityProofFalsifiedError",
    "ComparabilityProofMissingError",
    "StrategyAdapterError",
]
