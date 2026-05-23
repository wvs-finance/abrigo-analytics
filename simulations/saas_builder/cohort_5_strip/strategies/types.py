r"""Value-tier Protocols + frozen-dc for Stage-3 A1 alternative strategies.

Stage-2 closed with the canonical reverse-IC strip emitted by
``cohort_5_strip``. Stage-3 Track A1 evaluates whether non-reverse-IC
Panoptic primitives (long strangle, calendar spread, butterfly, etc.)
can be compared on equal footing against that canonical strip. This
module declares the Value-tier surface that lets such primitives be
ADAPTED into the existing ``IronCondorStrip`` container (no subclassing
— the existing frozen-dc is re-used as the comparability vehicle).

Three comparability proofs are pre-registered (Wave-1 pin); a strategy
adapter must declare exactly one:

- ``tiled_body`` — the adapter's built strip satisfies the canonical
  Pin S5 long-vol signature (``Π_strip(S_0) = 0`` exactly under
  tiled-body geometry, positive payoff on both sides). Verified by
  the shipped ``assert_long_vol_signature``.
- ``primitive_variant`` — the adapter supplies a primitive-specific
  envelope verifier (centering / proxy / β-fit may differ from the
  log-contract canonical form). Authored in Task 2.3b.
- ``normalized_score`` — fallback for primitives that fail both
  prior lanes; comparability is achieved by reporting a scalar score
  ``max_relative_error · (1 + |Π_strip(S_0)| / max|Π_strip|_grid)``.
  Smaller is better; the strip-payoff floor at spot penalizes any
  non-tiled-body residual.

NORMALIZED-SCORE FORMULA PIN. The formula is FROZEN at this commit
(Task 2.1, plan v0.3). Ex-post adjustment (e.g., changing the penalty
multiplier, swapping in a different normalization) requires a
CORRECTIONS-α block and Wave-1 re-review — anti-fishing forbids
silent post-hoc score-formula tuning.

NO IO at this tier. NO inheritance except Protocol / Exception.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal, Protocol, TypeAlias, runtime_checkable

from simulations.saas_builder.cohort_5_strip.types import (
    IronCondorStrip,
    ReplicationVerdict,
)

# ─── Module-level constants ───────────────────────────────────────────────────

#: Closed alphabet of comparability proofs (Wave-1 pin, plan v0.3 §2.1).
ComparabilityProof: TypeAlias = Literal[
    "tiled_body", "primitive_variant", "normalized_score"
]

#: Set form of :data:`ComparabilityProof`, used at runtime in ``__post_init__``.
COMPARABILITY_PROOFS: Final[frozenset[str]] = frozenset(
    {"tiled_body", "primitive_variant", "normalized_score"}
)

#: Default grid span (log-spot) used by :func:`compute_normalized_score`;
#: mirrors :class:`CarrMadanEnvelopeVerifier` Pin S6 default.
NORMALIZED_SCORE_GRID_SPAN: Final[float] = 0.15

#: Default grid point count for :func:`compute_normalized_score`;
#: odd so that ``S_0`` itself is sampled (mirrors CarrMadanEnvelopeVerifier).
NORMALIZED_SCORE_GRID_POINTS: Final[int] = 17

#: Documentation string for the FROZEN normalized-score formula.
#:
#: This constant is intentionally an attribute (not a docstring) so
#: downstream emit / audit tooling can serialize the formula text
#: alongside any emitted ``NormalizedEnvelopeScore`` artifact. The
#: text is bit-stable across the Wave-1 freeze.
NORMALIZED_SCORE_FORMULA_DOCSTRING: Final[str] = (
    "normalized_score(strip, verdict) = "
    "verdict.max_relative_error * "
    "(1.0 + |strip_payoff(strip, S_0)| / max_{S in grid} |strip_payoff(strip, S)|), "
    "where grid = {S_0 * exp(-span + 2*span*i/(N-1)) : i = 0..N-1}, "
    "span = 0.15, N = 17. "
    "Smaller is better. The leading factor inherits the Pin S6 envelope "
    "residual; the multiplicative penalty rewards strips whose payoff floor "
    "at spot is small relative to the peak (tiled-body geometry achieves "
    "floor = 0 -> penalty = 1.0; off-tile geometries pay > 1.0). "
    "FROZEN at Task 2.1 (plan v0.3); ex-post adjustment requires "
    "CORRECTIONS-alpha + Wave-1 re-review."
)


# ─── Protocols ────────────────────────────────────────────────────────────────


@runtime_checkable
class StrategyAdapter(Protocol):
    """Build an :class:`IronCondorStrip` from a non-reverse-IC primitive.

    Implementers wrap a Panoptic primitive (long strangle, butterfly,
    calendar spread, etc.) and translate its leg topology into the
    canonical 12-leg ``IronCondorStrip`` container so that the
    Stage-2 shipped verifiers (Pin S5 long-vol signature, Pin S6
    Carr-Madan envelope) can be applied uniformly.

    Adapter implementations are NOT subclasses of ``IronCondorStrip``;
    they construct one and return it. This preserves the existing
    Pin S1-S4 strike-ladder / weight / cardinality / anchor invariants
    unchanged — a non-reverse-IC primitive that cannot be expressed
    in the 12-leg container is rejected at adapter-construction time
    by raising the appropriate ``cohort_5_strip._errors`` subclass.

    Required attributes (consumed by :class:`EnvelopeComparator`):

    - ``primitive_id`` — short canonical id (str, non-empty), e.g.,
      ``"long_strangle"``, ``"reverse_iron_condor"``.
    - ``comparability_proof`` — pre-registered lane, one of
      :data:`COMPARABILITY_PROOFS`. Declared at adapter authorship per
      Wave-1 plan v0.3 §2.1 (never post-hoc).

    Method contract (callable surface — matches the cohort_5_strip
    convention shared with :class:`StripBuilder`, :class:`CondorBuilder`,
    and :class:`CarrMadanEnvelopeVerifier`):

    - ``s_0`` finite, > 0 (spot price at which the strip is placed).
    - ``sigma_0`` finite, > 0 (Carr-Madan linearization point).
    - ``k_star`` finite, > 0 (equilibrium strike K*).
    - Returns a fully-validated ``IronCondorStrip`` whose
      ``__post_init__`` has run successfully.
    """

    primitive_id: str
    comparability_proof: ComparabilityProof

    def __call__(
        self, s_0: float, sigma_0: float, k_star: float
    ) -> IronCondorStrip:
        """Build the 12-leg strip representation of this primitive."""
        ...


class PrimitiveVariantVerifier(Protocol):
    """Primitive-specific envelope verifier (``primitive_variant`` lane).

    Mirrors the shipped :class:`CarrMadanEnvelopeVerifier` contract
    (frozen-dc + ``__call__`` returning a :class:`ReplicationVerdict`)
    but allows the centering / proxy / beta-fit choices to be
    primitive-specific. Concrete implementations are authored
    conditionally in Task 2.3b, gated by per-primitive analytical
    justification (e.g., a long-strangle proxy other than the
    log-contract).

    Anti-fishing invariant: a primitive-variant verifier MUST be
    pre-registered before it is run against any candidate strip; the
    primitive_id of the wrapped score and the verifier identity are
    paired at Wave-1 review, not after first results.
    """

    def __call__(self, strip: IronCondorStrip) -> ReplicationVerdict:
        """Return the primitive-specific replication verdict."""
        ...


# ─── Value type ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class NormalizedEnvelopeScore:
    """Wraps a :class:`ReplicationVerdict` with comparability metadata.

    Fields:

    - ``primitive_id`` — short canonical id (e.g., ``"long_strangle"``,
      ``"reverse_iron_condor"``, ``"butterfly"``). Non-empty.
    - ``comparability_proof`` — one of
      :data:`ComparabilityProof`. Declares which Wave-1
      pre-registered lane applies to this primitive.
    - ``normalized_score`` — finite, >= 0; the
      :func:`compute_normalized_score` output. Smaller is better.
    - ``raw_verdict`` — the underlying envelope verdict (canonical
      ``CarrMadanEnvelopeVerifier`` for ``tiled_body``;
      primitive-specific verifier for ``primitive_variant``;
      either is acceptable for ``normalized_score``).

    Validation contract:

    - ``primitive_id`` non-empty.
    - ``comparability_proof`` in :data:`COMPARABILITY_PROOFS`.
    - ``normalized_score`` finite, >= 0.
    - ``raw_verdict.tolerance > 0`` (inherited from
      ``ReplicationVerdict.__post_init__`` but re-asserted here
      for defensive isolation across the strategies/ boundary).
    """

    primitive_id: str
    comparability_proof: ComparabilityProof
    normalized_score: float
    raw_verdict: ReplicationVerdict

    def __post_init__(self) -> None:
        if not self.primitive_id:
            raise ValueError(
                "NormalizedEnvelopeScore.primitive_id must be a non-empty"
                " string identifying the Panoptic primitive"
            )
        if self.comparability_proof not in COMPARABILITY_PROOFS:
            raise ValueError(
                f"NormalizedEnvelopeScore.comparability_proof ="
                f" {self.comparability_proof!r} must be one of"
                f" {sorted(COMPARABILITY_PROOFS)}"
            )
        if not math.isfinite(self.normalized_score):
            raise ValueError(
                f"NormalizedEnvelopeScore.normalized_score ="
                f" {self.normalized_score} must be finite"
            )
        if self.normalized_score < 0.0:
            raise ValueError(
                f"NormalizedEnvelopeScore.normalized_score ="
                f" {self.normalized_score} must be >= 0"
            )
        if not self.raw_verdict.tolerance > 0.0:
            raise ValueError(
                f"NormalizedEnvelopeScore.raw_verdict.tolerance ="
                f" {self.raw_verdict.tolerance} must be > 0"
            )


# ─── Free functions ───────────────────────────────────────────────────────────


def compute_normalized_score(
    raw_verdict: ReplicationVerdict, strip: IronCondorStrip
) -> float:
    r"""Compute the FROZEN normalized-score scalar (plan v0.3 §2.1).

    Formula (see :data:`NORMALIZED_SCORE_FORMULA_DOCSTRING`):

    .. math::

        \mathrm{score} = \mathrm{verdict.max\_relative\_error}
            \cdot \left(1 + \frac{|\Pi_{\mathrm{strip}}(S_0)|}
                                 {\max_{S \in \mathrm{grid}}
                                  |\Pi_{\mathrm{strip}}(S)|}\right)

    Grid: 17 points evenly spaced in log-spot over
    ``[S_0 * exp(-0.15), S_0 * exp(+0.15)]`` (mirrors
    :class:`CarrMadanEnvelopeVerifier` defaults).

    Strip-payoff terms are computed via the SHIPPED
    :func:`cohort_5_strip.replication.strip_payoff`; no separate
    payoff formula is introduced in this module.

    Raises:
        ValueError: If the strip-payoff grid is identically zero
            (degenerate primitive — cannot normalize). Mirrors
            the corresponding guard in
            :class:`CarrMadanEnvelopeVerifier`.
    """
    # Local import to avoid module-load cycles: replication imports
    # from .types (the parent module), and the strategies/types
    # module is a sibling — keep the import inside the function.
    from simulations.saas_builder.cohort_5_strip.replication import strip_payoff

    span = NORMALIZED_SCORE_GRID_SPAN
    n_pts = NORMALIZED_SCORE_GRID_POINTS
    s_0 = strip.s_0
    step = 2.0 * span / (n_pts - 1)
    s_grid = tuple(
        s_0 * math.exp(-span + step * i) for i in range(n_pts)
    )
    payoff_grid = tuple(strip_payoff(strip, s) for s in s_grid)
    max_abs_payoff = max(abs(v) for v in payoff_grid)
    if not max_abs_payoff > 0.0:
        raise ValueError(
            "compute_normalized_score: max |Π_strip| over the grid is 0;"
            " primitive is degenerate (cannot normalize)"
        )
    payoff_at_s0 = strip_payoff(strip, s_0)
    penalty = 1.0 + abs(payoff_at_s0) / max_abs_payoff
    return raw_verdict.max_relative_error * penalty


__all__ = [
    "COMPARABILITY_PROOFS",
    "NORMALIZED_SCORE_FORMULA_DOCSTRING",
    "NORMALIZED_SCORE_GRID_POINTS",
    "NORMALIZED_SCORE_GRID_SPAN",
    "ComparabilityProof",
    "NormalizedEnvelopeScore",
    "PrimitiveVariantVerifier",
    "StrategyAdapter",
    "compute_normalized_score",
]
