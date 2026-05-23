r"""Stage-3 A1 envelope comparator — runs each adapter through the shipped
:class:`CarrMadanEnvelopeVerifier` and returns a ranked tuple of
:class:`NormalizedEnvelopeScore`.

The comparator is the Phase-2 glue layer (Task 2.3, plan v0.3 §2.3): given
a tuple of pre-registered :class:`StrategyAdapter` implementations and one
Pin-M2 :class:`TestPoint` fixture (cohort-4 Value type), it

1. builds each adapter's 12-leg ``IronCondorStrip`` (delegating geometry
   choice to the adapter),
2. RUNTIME-CHECKS the adapter's declared ``comparability_proof`` against
   the strip BEFORE collecting a score — a missing or falsified proof
   raises the typed sub-package exception and is never silently swallowed,
3. runs the shipped :class:`CarrMadanEnvelopeVerifier` to produce a
   :class:`ReplicationVerdict` and the FROZEN normalized-score scalar,
4. assembles :class:`NormalizedEnvelopeScore` records and SORTS them in
   a single tuple by a proof-dependent key (tiled_body / primitive_variant
   rank on the raw ``max_relative_error``; normalized_score lane ranks on
   the multiplicatively-penalized scalar). Secondary lex sort on
   ``primitive_id`` resolves float-ties within ``1e-12``.

COMPARABILITY-ACROSS-LANE CAVEAT. Comparing scores ACROSS different
``comparability_proof`` lanes is technically not meaningful — the
``tiled_body`` lane ranks on a Pin S6 envelope residual; the
``normalized_score`` lane ranks on the SAME envelope residual multiplied
by an off-tile penalty; the ``primitive_variant`` lane (Task 2.3b) may
use a different proxy entirely. THIS COMPARATOR'S RESPONSIBILITY is
limited to COMPUTING the per-adapter scores under their declared lane and
returning them sorted. The cross-lane VERDICT INTERPRETATION — including
the Wave-1 5pp threshold and any per-lane caveat — is the responsibility
of the Phase-3 verdict logic (Task 3.1). The single sorted tuple is a
PRESENTATION choice, not a claim of cross-lane equivalence.

ANTI-FISHING INVARIANTS (carry forward from plan v0.3 §2.3):

- The verifier instance + per-lane comparability proofs are PRE-COMMITTED
  at adapter authorship (Task 2.2 froze each adapter's ``comparability_proof``).
  This comparator MUST NOT swap an adapter's declared lane post-hoc; if
  the runtime check fails, it raises — never falls through to
  ``normalized_score``.
- Empty ``primitive_variant_verifiers`` is the Task 2.3 DEFAULT (no
  Task 2.2 adapter uses the ``primitive_variant`` lane). Task 2.3b
  conditionally populates this mapping per its per-primitive review
  verdict.

NO IO at this tier. The comparator is a Value-tier composition (frozen
dataclass + ``__call__``) per the functional-python skill.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from simulations.saas_builder.cohort_4.types import TestPoint
from simulations.saas_builder.cohort_5_strip._errors import (
    ReplicationToleranceError,
)
from simulations.saas_builder.cohort_5_strip.replication import (
    CarrMadanEnvelopeVerifier,
    assert_long_vol_signature,
)
from simulations.saas_builder.cohort_5_strip.strategies._errors import (
    ComparabilityProofFalsifiedError,
    ComparabilityProofMissingError,
)
from simulations.saas_builder.cohort_5_strip.strategies.types import (
    NormalizedEnvelopeScore,
    PrimitiveVariantVerifier,
    StrategyAdapter,
    compute_normalized_score,
)

#: Absolute float-tolerance for declaring two ``normalized_score`` /
#: ``max_relative_error`` values "tied" for the secondary lexicographic
#: ``primitive_id`` sort. Plan v0.3 §2.3 acceptance criterion 4.
SORT_TIE_TOLERANCE: float = 1e-12


def _quantize_for_tie(score: float) -> float:
    """Quantize ``score`` to the :data:`SORT_TIE_TOLERANCE` grid.

    Two scores ``a`` and ``b`` with ``|a - b| < SORT_TIE_TOLERANCE``
    collapse to the SAME quantized key, so Python's stable sort then
    breaks the tie via the next element of the sort key (``primitive_id``).
    Quantization is performed via integer flooring after dividing by the
    tolerance — exactly reproducible across runs (no floating-point
    division-order non-determinism).
    """
    return float(int(score / SORT_TIE_TOLERANCE))


@dataclass(frozen=True)
class EnvelopeComparator:
    r"""Run each :class:`StrategyAdapter` through the shipped envelope verifier.

    Fields:

    - ``verifier`` — the canonical :class:`CarrMadanEnvelopeVerifier`
      instance applied to every adapter's built strip. Defaults to a
      freshly-constructed verifier with the shipped Pin S6 defaults
      (``n_grid_points = 17``, ``span = 0.15``,
      ``tolerance = REPLICATION_REL_TOL = 0.35``).
    - ``primitive_variant_verifiers`` — mapping ``primitive_id`` →
      :class:`PrimitiveVariantVerifier` for adapters declaring
      ``comparability_proof = "primitive_variant"``. EMPTY by default at
      Task 2.3 (no Task 2.2 adapter uses the primitive-variant lane);
      Task 2.3b populates conditionally on per-primitive review.

    Method contract:

    ``__call__(adapters, fixture, k_star)`` —

    - ``adapters``: tuple of :class:`StrategyAdapter`. Each adapter MUST
      expose ``primitive_id`` (str) and ``comparability_proof``
      (one of :data:`COMPARABILITY_PROOFS`) attributes per the Task 2.2
      convention. Empty tuple returns an empty result tuple.
    - ``fixture``: cohort-4 :class:`TestPoint`. Only ``x_over_y_bar`` and
      ``sigma_0`` are consumed here (the Carr-Madan linearization point
      and the FX-mean spot proxy). ``kappa`` is NOT consumed at this
      tier — adapters depend on (S_0, σ_0, K\*), not on the token cap.
    - ``k_star``: equilibrium strike at which to place the strip. Passed
      through to each adapter's ``__call__`` unchanged.
    - Returns: tuple of :class:`NormalizedEnvelopeScore`, ranked by the
      proof-dependent key documented in Sort Order below.

    Per-adapter processing:

    1. Build the strip via ``adapter(fixture.x_over_y_bar, fixture.sigma_0,
       k_star)`` — adapter validation errors propagate unchanged.
    2. Runtime comparability-proof gate:

       - ``"tiled_body"`` — invoke ``assert_long_vol_signature(strip)``;
         on ``ReplicationToleranceError``, wrap and re-raise as
         :class:`ComparabilityProofFalsifiedError`.
       - ``"primitive_variant"`` — look up
         ``self.primitive_variant_verifiers[adapter.primitive_id]``;
         raise :class:`ComparabilityProofMissingError` if absent. Task
         2.3b will additionally cross-check the variant verifier against
         the canonical verifier on a reverse-IC baseline (equivalence
         pre-check); Task 2.3 only enforces presence.
       - ``"normalized_score"`` — no runtime check; the multiplicative
         penalty in the FROZEN score formula IS the proof.

    3. Run ``self.verifier(strip)`` to produce the
       :class:`ReplicationVerdict`.
    4. Compute the FROZEN normalized-score scalar via
       :func:`compute_normalized_score`.
    5. Construct the :class:`NormalizedEnvelopeScore` record.

    Sort order (proof-dependent primary key, plan v0.3 §2.3 §4):

    - ``tiled_body`` adapters rank by ``raw_verdict.max_relative_error``
      ascending. Pin S5 collapses the off-tile penalty to 1.0, so the
      normalized scalar equals ``max_relative_error`` exactly under
      tiled-body — ranking on either is identical.
    - ``normalized_score`` adapters rank by ``normalized_score``
      ascending. The leading factor inherits the Pin S6 envelope; the
      penalty rewards smaller off-tile residuals at S_0.
    - ``primitive_variant`` adapters rank by the variant verifier's
      ``max_relative_error`` (surfaced by Task 2.3b). At Task 2.3, the
      default fall-back is the canonical
      ``raw_verdict.max_relative_error``.
    - Secondary sort within :data:`SORT_TIE_TOLERANCE` is
      lexicographic ascending on ``primitive_id`` (deterministic
      tie-break for cross-run stability).

    Returns the scores in a SINGLE sorted tuple; cross-lane VERDICT
    interpretation is Phase-3 verdict-logic territory (Task 3.1).
    """

    verifier: CarrMadanEnvelopeVerifier = field(
        default_factory=CarrMadanEnvelopeVerifier
    )
    primitive_variant_verifiers: Mapping[str, PrimitiveVariantVerifier] = field(
        default_factory=dict
    )

    def __call__(
        self,
        adapters: tuple[StrategyAdapter, ...],
        fixture: TestPoint,
        k_star: float,
    ) -> tuple[NormalizedEnvelopeScore, ...]:
        scores: list[NormalizedEnvelopeScore] = []
        for adapter in adapters:
            strip = adapter(
                fixture.x_over_y_bar, fixture.sigma_0, k_star
            )
            proof = adapter.comparability_proof
            if proof == "tiled_body":
                try:
                    assert_long_vol_signature(strip)
                except ReplicationToleranceError as exc:
                    raise ComparabilityProofFalsifiedError(
                        f"adapter {adapter.primitive_id!r} claims"
                        f' comparability_proof = "tiled_body" but the built'
                        f" strip fails the Pin S5 long-vol signature: {exc}"
                    ) from exc
            elif proof == "primitive_variant":
                if adapter.primitive_id not in self.primitive_variant_verifiers:
                    raise ComparabilityProofMissingError(
                        f"adapter {adapter.primitive_id!r} claims"
                        f' comparability_proof = "primitive_variant" but no'
                        f" PrimitiveVariantVerifier was supplied to"
                        f" EnvelopeComparator.primitive_variant_verifiers"
                        f" (Task 2.3b populates this mapping after"
                        f" per-primitive review)"
                    )
                # Task 2.3b: also run the variant verifier and pre-check it
                # against the canonical verifier on a reverse-IC baseline.
                # Task 2.3 only enforces presence (see class docstring).
            # "normalized_score" — no runtime check; penalty IS the proof.
            verdict = self.verifier(strip)
            normalized_score = compute_normalized_score(verdict, strip)
            scores.append(
                NormalizedEnvelopeScore(
                    primitive_id=adapter.primitive_id,
                    comparability_proof=proof,
                    normalized_score=normalized_score,
                    raw_verdict=verdict,
                )
            )
        return tuple(sorted(scores, key=_sort_key))


def _sort_key(score: NormalizedEnvelopeScore) -> tuple[float, str]:
    """Return the (primary, secondary) sort key for one score record.

    Primary key — proof-dependent (plan v0.3 §2.3 §4):

    - ``tiled_body`` -> ``raw_verdict.max_relative_error``.
    - ``normalized_score`` -> ``normalized_score`` (the FROZEN scalar).
    - ``primitive_variant`` -> ``raw_verdict.max_relative_error``
      (Task 2.3 fallback; Task 2.3b will substitute the variant
      verifier's own ``max_relative_error``).

    The primary value is QUANTIZED to :data:`SORT_TIE_TOLERANCE` so
    that float-ties within tolerance fall through to the secondary key.

    Secondary key — ``primitive_id`` lexicographic ascending.
    """
    proof = score.comparability_proof
    if proof == "normalized_score":
        primary_raw = score.normalized_score
    elif proof == "tiled_body":
        primary_raw = score.raw_verdict.max_relative_error
    else:  # "primitive_variant"
        primary_raw = score.raw_verdict.max_relative_error
    return (_quantize_for_tie(primary_raw), score.primitive_id)


__all__ = [
    "SORT_TIE_TOLERANCE",
    "EnvelopeComparator",
]
