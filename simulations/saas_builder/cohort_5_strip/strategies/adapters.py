r"""Concrete :class:`StrategyAdapter` implementations for Stage-3 A1.

Task 2.2 (plan v0.3) authors one adapter per Phase-1 filtered Panoptic
primitive (``scratch/2026-05-11-a1-panoptic-survey/STRATEGY_COMPARISON.md``
§5). Each adapter is a frozen-dataclass with ``__call__(s_0, sigma_0,
k_star) -> IronCondorStrip`` whose returned strip is the canonical
12-leg ``IronCondorStrip`` container — the strip API itself is fixed.

The adapter's freedom is in CHOOSING THE STRIP GEOMETRY (log offsets
+ inner/outer half-widths) such that the strip's combined payoff
APPROXIMATES the named primitive's natural payoff shape over the
FX-excursion zone (Carr-Madan philosophy: any twice-differentiable
convex payoff is replicable by a strip of OTM options with 2/K² weights;
different target payoffs are discretized into the same 12-leg API).

Comparability lane (Wave-1 pin, plan v0.3 §2.1):

- ``reverse_iron_condor`` — BASELINE; ``tiled_body`` lane. Geometry
  matches ``default_strip_geometry()`` so Pin S5 long-vol signature
  passes by construction.
- ``long_straddle`` — ``normalized_score`` lane. Bodies narrow + tightly
  clustered around S_0; strip does NOT tile S_0 in every condor's body
  in the canonical reverse-IC sense, so the Pin S5 tiled-body proof is
  not available.
- ``long_strangle`` — ``normalized_score`` lane. Bodies wider, clearly
  separated around S_0; mimics a wide-strangle payoff. Same rationale
  for the lane choice as ``long_straddle``.
- ``zeehbs`` — ``normalized_score`` lane. zeehbs is a 6-leg primitive;
  here APPROXIMATED by an asymmetric-wider 12-leg reverse-IC strip
  geometry. The approximation is faithful only in the σ_T-replication
  sense — the metric Phase-2's envelope evaluates.

Three-tier discipline (functional-python skill):

- This module is Value-tier (frozen-dc + ``__call__`` returning a
  fully-validated Value-tier ``IronCondorStrip``). NO IO. NO inheritance
  beyond ``Protocol`` / ``Exception`` / module-local frozen-dc.

ε defaults to :data:`cohort_5_strip.DEFAULT_EPSILON` (= 0.1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from simulations.saas_builder.cohort_5_strip.geometry import (
    DEFAULT_EPSILON,
    build_strip,
    default_strip_geometry,
)
from simulations.saas_builder.cohort_5_strip.strategies.types import (
    ComparabilityProof,
)
from simulations.saas_builder.cohort_5_strip.types import (
    IronCondorStrip,
    StripGeometry,
)

#: Anchor citation common to all Phase-1 filtered adapters.
#:
#: Tied to ``STRATEGY_COMPARISON.md`` §2 (per-primitive metadata row).
#: §5 records the v0.3 filter predicate (`admits_strip_emit = "yes"`
#: AND `convexity_class == "long-vol"` strictly).
STRATEGY_COMPARISON_ANCHOR: Final[str] = (
    "scratch/2026-05-11-a1-panoptic-survey/STRATEGY_COMPARISON.md §2 row"
)


# ─── Adapter 1 — reverse_iron_condor (BASELINE) ───────────────────────────────


@dataclass(frozen=True)
class ReverseIronCondorAdapter:
    r"""Baseline adapter — re-exports the canonical reverse-IC strip.

    PRIMITIVE PAYOFF SHAPE. Reverse iron condor (long-vol orientation;
    cohort_5_strip's flipped credit/debit-wing convention): piecewise-
    linear, symmetric, FLAT zero through the inner body ``[K_2, K_3]``
    and positively-sloped outside the body up to the outer wings
    ``[K_1, K_4]``. Three such condors are tiled at log-offsets
    ``(−ε, 0, +ε)`` so the combined strip approximates the convex
    ``√σ_T`` Carr-Madan target on the FX-excursion zone.

    CHOSEN STRIP GEOMETRY (defaults; see :func:`default_strip_geometry`):

    - ``log_offsets = (−ε, 0, +ε)`` with ``ε = DEFAULT_EPSILON = 0.1``.
    - ``delta_inner = ε`` (tiled-body convention: each condor's inner
      body spans the FULL offset spacing, so the left-tail's right
      body-edge meets the ATM's left body-edge meets the right-tail's
      left body-edge at S_0).
    - ``delta_outer = 2·ε`` (extends the outer wings a full ε beyond
      each condor's body, giving the long-vol cap room to widen).

    COMPARABILITY PROOF. ``"tiled_body"`` — under the tiled-body default
    geometry, every condor's body covers S_0 (ATM) or borders it
    (left/right tails), so all 12 legs are OTM or at-strike at S_0 and
    ``Π_strip(S_0) = 0`` exactly. Pin S5 long-vol signature holds by
    construction; the Wave-1-shipped
    :func:`cohort_5_strip.replication.assert_long_vol_signature` verifies
    it without modification.

    ANCHOR. STRATEGY_COMPARISON.md §2 row 17 (`iron_condor`); §5
    BASELINE row (reverse_iron_condor — cohort_5_strip's long-vol
    re-orientation of the standard short-vol IC). Wave-1 plan v0.3 §2.1.
    """

    primitive_id: str = field(default="reverse_iron_condor", init=False)
    comparability_proof: ComparabilityProof = field(
        default="tiled_body", init=False
    )

    def __call__(
        self, s_0: float, sigma_0: float, k_star: float
    ) -> IronCondorStrip:
        """Build the canonical 12-leg reverse-IC strip via :func:`build_strip`.

        Delegates to the shipped ``StripBuilder`` instance with the
        canonical ``default_strip_geometry()`` so the returned strip is
        byte-identical to cohort_5_strip's existing baseline emit.

        Raises:
            StripGeometryError: Propagated from ``build_strip`` when
                ``s_0`` / ``sigma_0`` / ``k_star`` are non-finite or
                non-positive.
        """
        return build_strip(
            s_0=s_0,
            sigma_0=sigma_0,
            k_star=k_star,
            geometry=default_strip_geometry(),
        )


# ─── Adapter 2 — long_straddle ────────────────────────────────────────────────


@dataclass(frozen=True)
class LongStraddleAdapter:
    r"""Adapter for the 2-leg long-vol ``long_straddle`` primitive.

    PRIMITIVE PAYOFF SHAPE. Long straddle (long call + long put at the
    SAME strike ``K = S_0``): piecewise-linear, symmetric, V-shape with
    its single kink at S_0 — payoff is ``|S_T − S_0|``, strictly
    positive everywhere except at ``S_T = S_0`` where it is exactly 0.

    CHOSEN STRIP GEOMETRY (narrow + tightly-clustered around S_0 so the
    combined 12-leg payoff approximates the single-kink V-shape):

    - ``log_offsets = (−ε/4, 0, +ε/4)`` with ``ε = DEFAULT_EPSILON = 0.1``.
    - ``delta_inner = ε/8`` (very narrow inner bodies — each condor's
      body is one quarter of a quarter-ε).
    - ``delta_outer = ε/4`` (wings cover the offset spacing).

    Under this geometry the three condor centers cluster within a
    log-strike window of ±0.025 (vs. ±0.1 for the canonical tiled-body
    baseline). The combined strip payoff therefore behaves like a
    single deep-ATM straddle out to the wing cap, faithfully mimicking
    the long_straddle's V-shape inside the FX-excursion zone.

    COMPARABILITY PROOF. ``"normalized_score"`` — the strip does NOT
    tile S_0 in every condor's body in the canonical reverse-IC sense
    (the bodies are narrow and meet only at the offset boundaries, not
    spanning S_0 in every condor). Pin S5 ``Π_strip(S_0) = 0`` cannot
    be asserted by construction, so the ``tiled_body`` proof is
    unavailable; the FROZEN normalized-score formula (Task 2.1) is the
    correct comparability lane.

    ANCHOR. STRATEGY_COMPARISON.md §2 row 5 (`long_straddle`):
    ``leg_count = 2``, ``payoff_shape = "piecewise-linear, convex
    (V-shape at strike)"``, ``convexity_class = "long-vol"`` (strict-
    equality long-vol qualifier; v0.3 filter survivor); §5 candidate
    row. Wave-1 plan v0.3 §2.1.
    """

    primitive_id: str = field(default="long_straddle", init=False)
    comparability_proof: ComparabilityProof = field(
        default="normalized_score", init=False
    )
    epsilon: float = DEFAULT_EPSILON

    def __call__(
        self, s_0: float, sigma_0: float, k_star: float
    ) -> IronCondorStrip:
        """Build a narrow-clustered 12-leg strip approximating a long straddle.

        Geometry parameters are derived from :attr:`epsilon` (default
        ``DEFAULT_EPSILON = 0.1``).

        Raises:
            StripGeometryError: Propagated from ``build_strip`` (validation
                of ``s_0`` / ``sigma_0`` / ``k_star``) or from
                ``StripGeometry.__post_init__`` (geometry invariants).
        """
        eps = self.epsilon
        geometry = StripGeometry(
            log_offsets=(-eps / 4.0, 0.0, +eps / 4.0),
            delta_inner=eps / 8.0,
            delta_outer=eps / 4.0,
        )
        return build_strip(
            s_0=s_0, sigma_0=sigma_0, k_star=k_star, geometry=geometry
        )


# ─── Adapter 3 — long_strangle ────────────────────────────────────────────────


@dataclass(frozen=True)
class LongStrangleAdapter:
    r"""Adapter for the 2-leg long-vol ``long_strangle`` primitive.

    PRIMITIVE PAYOFF SHAPE. Long strangle (long call + long put at
    DIFFERENT strikes — long put at ``K_lo < S_0`` + long call at
    ``K_hi > S_0``): piecewise-linear, FLAT zero between
    ``[K_lo, K_hi]`` (the "strangle gap"), and convex/sloped outside.
    Distinguished from the straddle by a non-degenerate flat segment
    around spot.

    CHOSEN STRIP GEOMETRY (wider inner bodies + clearly separated
    condor centers, mimicking the strangle's flat-then-sloped payoff):

    - ``log_offsets = (−ε, 0, +ε)`` with ``ε = DEFAULT_EPSILON = 0.1``.
    - ``delta_inner = ε/2`` (each condor's body is half-ε wide — bodies
      do NOT meet at S_0, leaving a "flat gap" in the combined strip
      payoff over ``[exp(−ε/2)·S_0, exp(+ε/2)·S_0]`` for the ATM condor
      and analogous gaps for the tails).
    - ``delta_outer = ε`` (wings cover the full offset spacing).

    Under this geometry the inner bodies are clearly separated rather
    than tiled, producing a combined-strip payoff with a flat zero
    region around S_0 (mimicking the strangle's no-payoff zone between
    its long-put and long-call strikes) before the wing-payoff slope
    engages outside ``±ε/2`` from each condor center.

    COMPARABILITY PROOF. ``"normalized_score"`` — separated-body geometry
    means the strip's payoff at S_0 is NOT zero by construction (the
    ATM condor's body covers S_0 but the tail condors' bodies do NOT
    span S_0). Pin S5 cannot be asserted; FROZEN normalized-score
    formula is the correct lane.

    ANCHOR. STRATEGY_COMPARISON.md §2 row 6 (`long_strangle`):
    ``leg_count = 2``, ``payoff_shape = "piecewise-linear, convex
    (flat between strikes)"``, ``convexity_class = "long-vol"`` (strict-
    equality long-vol qualifier; v0.3 filter survivor); §5 candidate
    row. Wave-1 plan v0.3 §2.1.
    """

    primitive_id: str = field(default="long_strangle", init=False)
    comparability_proof: ComparabilityProof = field(
        default="normalized_score", init=False
    )
    epsilon: float = DEFAULT_EPSILON

    def __call__(
        self, s_0: float, sigma_0: float, k_star: float
    ) -> IronCondorStrip:
        """Build a wider-separated-body 12-leg strip approximating a long strangle.

        Geometry parameters are derived from :attr:`epsilon` (default
        ``DEFAULT_EPSILON = 0.1``).

        Raises:
            StripGeometryError: Propagated from ``build_strip`` or from
                ``StripGeometry.__post_init__``.
        """
        eps = self.epsilon
        geometry = StripGeometry(
            log_offsets=(-eps, 0.0, +eps),
            delta_inner=eps / 2.0,
            delta_outer=eps,
        )
        return build_strip(
            s_0=s_0, sigma_0=sigma_0, k_star=k_star, geometry=geometry
        )


# ─── Adapter 4 — zeehbs ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class ZeehbsAdapter:
    r"""Adapter for the 6-leg long-vol ``zeehbs`` primitive (approximation).

    PRIMITIVE PAYOFF SHAPE. ``zeehbs`` is a 6-leg leveraged-strangle
    replica with bullish-bearish-hybrid topology — piecewise-linear,
    asymmetric across the six strikes, long-vol class (positive
    convexity outside the central zone). On Panoptic the native form
    requires ≥2 SFPM positions (4-leg ceiling per position).

    NOTE ON APPROXIMATION. The 6-leg structure is APPROXIMATED here by
    a 12-leg reverse-IC strip — this is a faithful approximation only
    in the σ_T-replication sense (Carr-Madan envelope; Pin S6 ≤ 35%
    against the log-contract proxy), which IS what Phase-2's envelope
    metric evaluates. Leg-level topological equivalence is explicitly
    NOT claimed; the normalized-score lane is the honest comparability
    proof.

    CHOSEN STRIP GEOMETRY (asymmetric-wider geometry, intentionally
    pushing tail-condor centers beyond the FX-excursion edge so the
    combined strip approximates zeehbs's leveraged convex tails):

    - ``log_offsets = (−1.5·ε, 0, +1.5·ε)`` with
      ``ε = DEFAULT_EPSILON = 0.1`` (50% wider tail placement than
      baseline).
    - ``delta_inner = ε`` (inner bodies wider than baseline's
      tiled-body ``ε`` because the offsets are wider — bodies still
      meet but only at ``±0.5·ε`` from S_0 rather than 0).
    - ``delta_outer = 1.5·ε`` (wings cover the full offset spacing,
      so outer wing strikes coincide with the next condor's center).

    Note on the body-tiling boundary: with ``log_offsets = ±1.5·ε`` and
    ``delta_inner = ε``, the ATM condor's body spans ``±ε`` around S_0,
    and the tail condors' bodies meet the ATM body at ``±0.5·ε`` (not
    at S_0). The strip is therefore wider-spread than the baseline but
    still has the ATM body covering S_0 — the canonical Pin S5 floor
    holds for the ATM contribution only, not for the strip as a whole.

    COMPARABILITY PROOF. ``"normalized_score"`` — the asymmetric-wider
    geometry breaks the canonical tiled-body strict floor (only the
    ATM condor contributes 0 at S_0; tail condors contribute non-zero
    body payoff at their offset positions). Pin S5 cannot be asserted
    by construction; the FROZEN normalized-score formula (Task 2.1)
    quantifies the off-tile residual and is the correct lane.

    ANCHOR. STRATEGY_COMPARISON.md §2 row 20 (`zeehbs`):
    ``leg_count = 6``, ``payoff_shape = "piecewise-linear, leveraged-
    strangle replica"``, ``convexity_class = "long-vol"`` (strict-
    equality long-vol qualifier; v0.3 filter survivor), with the
    4-leg-SFPM caveat (``on-chain_liquidity`` column — emit payload
    spans ≥2 SFPM positions); §5 candidate row. Wave-1 plan v0.3 §2.1.
    """

    primitive_id: str = field(default="zeehbs", init=False)
    comparability_proof: ComparabilityProof = field(
        default="normalized_score", init=False
    )
    epsilon: float = DEFAULT_EPSILON

    def __call__(
        self, s_0: float, sigma_0: float, k_star: float
    ) -> IronCondorStrip:
        """Build an asymmetric-wider 12-leg strip approximating zeehbs's long-vol cone.

        Geometry parameters are derived from :attr:`epsilon` (default
        ``DEFAULT_EPSILON = 0.1``).

        Raises:
            StripGeometryError: Propagated from ``build_strip`` or from
                ``StripGeometry.__post_init__``.
        """
        eps = self.epsilon
        geometry = StripGeometry(
            log_offsets=(-1.5 * eps, 0.0, +1.5 * eps),
            delta_inner=eps,
            delta_outer=1.5 * eps,
        )
        return build_strip(
            s_0=s_0, sigma_0=sigma_0, k_star=k_star, geometry=geometry
        )


__all__ = [
    "STRATEGY_COMPARISON_ANCHOR",
    "LongStraddleAdapter",
    "LongStrangleAdapter",
    "ReverseIronCondorAdapter",
    "ZeehbsAdapter",
]
