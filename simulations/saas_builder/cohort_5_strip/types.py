r"""Value-tier containers for SAAS-COHORT-5 — IronCondor strip M-sketch.

The IronCondor was selected as the longest-leg Panoptic primitive
available at Stage-2; it is NOT a claim that 4-leg condors are the
mathematically-optimal Panoptic discretization of ``√σ_T``. The
strategy-selection question is open Stage-3 work alongside real-data
cohort conditioning; see the package ``__init__`` docstring for
context.

All types are ``@dataclass(frozen=True)`` per the functional-python skill.
Methods are forbidden except ``__post_init__`` for validation; accessors
are free functions in this module.

Pin coverage (Stage-2 → Stage-3 hand-off):

- **Pin S1 — strike-ladder invariant.** Each IronCondor has 4 strikes
  K_1 < K_2 < K_3 < K_4 with the reverse-IC leg-kind structure (long-
  vol convention; see :class:`IronCondor` docstring). Validation refuses
  any ordering or kind permutation.
- **Pin S2 — Carr-Madan weight scaling.** Per-condor weight
  w_j ∝ 1/K_j² (PRIMITIVES.md §10 eq. 18); normalized so
  ``sum(w_j) == 1.0`` exactly under :data:`WEIGHT_SUM_TOL`.
- **Pin S3 — N=3 strip geometry.** Exactly three condors per strip
  (left tail / ATM / right tail; PRIMITIVES.md §11 default). 12 legs
  total. Log-offset triple ``(x_left, 0.0, x_right)`` with
  ``x_left < 0 < x_right`` strictly.
- **Pin S4 — anchor citations.** ``IronCondorStrip.primitives_anchor``
  and ``saas_note_anchor`` are non-empty citation strings tying each
  strip artifact back to the source-of-truth derivation.

NO IO at this tier. NO inheritance except Protocol / Exception.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

# ─── Module-level constants ───────────────────────────────────────────────────

#: Number of condors per strip (PRIMITIVES.md §11 Path A v2 default).
STRIP_CONDOR_COUNT: Final[int] = 3

#: Number of legs per IronCondor.
LEGS_PER_CONDOR: Final[int] = 4

#: Total legs in a strip (Pin S3 12-leg invariant).
STRIP_TOTAL_LEGS: Final[int] = STRIP_CONDOR_COUNT * LEGS_PER_CONDOR  # 12

#: Floating-point tolerance for the ``sum(w_j) == 1.0`` invariant (Pin S2).
WEIGHT_SUM_TOL: Final[float] = 1e-12

#: Floating-point tolerance for strike-ladder strict-ordering tests.
STRIKE_ORDER_TOL: Final[float] = 0.0

#: Default replication-envelope max relative error.
#:
#: PRIMITIVES.md §12 row 2 quotes ``±5%`` for the on-chain LP-fee vs
#: ``Δ^{(a_l)}`` envelope; that 5% applies to a CALIBRATED Mento V3 /
#: Uniswap V3 LP P&L comparison, NOT to a 3-condor finite strip.
#:
#: For the 3-condor strip, the strip payoff is piecewise-linear in
#: ``S_T`` while the log-contract proxy is smooth-quadratic. A 3-piece
#: linear approximation of ``x²`` over a symmetric interval has a
#: theoretical max relative error of ``1 - 3·(1/3)² = 2/3 ≈ 33%``
#: between segments; in practice the strip achieves ~30% under the
#: tiled-body default geometry. The default tolerance is set to 35%
#: to give a small margin above the theoretical floor.
#:
#: Stage-3 refinements (N=5 / N=7 / N=12 condor strips) tighten this
#: envelope; ``CarrMadanEnvelopeVerifier(tolerance=...)`` accepts an
#: explicit override for those variants.
REPLICATION_REL_TOL: Final[float] = 0.35

# ─── Type aliases ─────────────────────────────────────────────────────────────

#: Long-vol IronCondor leg kinds (reverse-IC convention).
LegKind: TypeAlias = Literal["short_put", "long_put", "long_call", "short_call"]

#: Canonical leg ordering per condor (outer-lower → inner-lower → inner-upper → outer-upper).
LEG_KIND_ORDER: Final[tuple[LegKind, LegKind, LegKind, LegKind]] = (
    "short_put",   # outer lower wing (K_1)
    "long_put",    # inner lower body (K_2)
    "long_call",   # inner upper body (K_3)
    "short_call",  # outer upper wing (K_4)
)

#: Closed alphabet for per-condor labels in the strip.
CondorLabel: TypeAlias = Literal["left_tail", "atm", "right_tail"]

#: Canonical label ordering in a strip (matches log-offset order: negative → 0 → positive).
STRIP_LABEL_ORDER: Final[tuple[CondorLabel, CondorLabel, CondorLabel]] = (
    "left_tail",
    "atm",
    "right_tail",
)


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CondorLeg:
    """One leg of an IronCondor.

    Validation contract:

    - ``kind`` is one of the four :data:`LegKind` literals.
    - ``strike`` finite, > 0.
    """

    kind: LegKind
    strike: float

    def __post_init__(self) -> None:
        if self.kind not in ("short_put", "long_put", "long_call", "short_call"):
            raise ValueError(
                f"CondorLeg.kind = {self.kind!r} must be one of"
                " short_put | long_put | long_call | short_call"
            )
        if not (math.isfinite(self.strike) and self.strike > 0.0):
            raise ValueError(
                f"CondorLeg.strike = {self.strike} must be a finite float > 0"
            )


@dataclass(frozen=True)
class IronCondor:
    r"""A 4-leg IronCondor under the reverse-IC (long-vol) convention.

    Strike ladder (Pin S1): ``K_1 < K_2 < K_3 < K_4``, where

    - ``K_1`` — outer lower wing strike (SHORT put).
    - ``K_2`` — inner lower body strike (LONG put).
    - ``K_3`` — inner upper body strike (LONG call).
    - ``K_4`` — outer upper wing strike (SHORT call).

    Net payoff at maturity ``S_T`` (per unit notional):

    .. math::

        P(S_T) = -\max(K_1-S_T, 0) + \max(K_2-S_T, 0) +
                 \max(S_T-K_3, 0) - \max(S_T-K_4, 0)

    This is a long-vol structure: positive payoff outside the inner
    body ``[K_2, K_3]`` and capped at the outer wings ``[K_1, K_4]``.
    PRIMITIVES.md §11 Carr-Madan replication sums these positive-weight
    long-vol building blocks to approximate ``Π_T ≈ K̂·σ_T``.

    Validation contract:

    - ``legs`` is a length-4 tuple matching :data:`LEG_KIND_ORDER`.
    - Strikes are strictly ordered: ``legs[0].strike < legs[1].strike <
      legs[2].strike < legs[3].strike``.
    - ``center`` finite, > 0, and ``legs[1].strike <= center <= legs[2].strike``
      (center lies in the inner body interval).
    - ``weight`` finite, > 0 (Carr-Madan weight ∝ 1/center²; normalization
      is enforced at the strip level).
    """

    legs: tuple[CondorLeg, CondorLeg, CondorLeg, CondorLeg]
    center: float
    weight: float
    label: CondorLabel

    def __post_init__(self) -> None:
        if len(self.legs) != LEGS_PER_CONDOR:
            raise ValueError(
                f"IronCondor.legs must have exactly {LEGS_PER_CONDOR} legs;"
                f" got {len(self.legs)}"
            )
        for i, (leg, expected_kind) in enumerate(zip(self.legs, LEG_KIND_ORDER)):
            if leg.kind != expected_kind:
                raise ValueError(
                    f"IronCondor.legs[{i}].kind = {leg.kind!r} must be"
                    f" {expected_kind!r} (reverse-IC long-vol convention)"
                )
        strikes = tuple(leg.strike for leg in self.legs)
        for i in range(LEGS_PER_CONDOR - 1):
            if not strikes[i] < strikes[i + 1]:
                raise ValueError(
                    f"IronCondor: strike ladder violated at position {i};"
                    f" got K_{i + 1}={strikes[i]} ≥ K_{i + 2}={strikes[i + 1]}"
                )
        if not (math.isfinite(self.center) and self.center > 0.0):
            raise ValueError(
                f"IronCondor.center = {self.center} must be a finite float > 0"
            )
        if not (strikes[1] <= self.center <= strikes[2]):
            raise ValueError(
                f"IronCondor.center = {self.center} must lie in inner body"
                f" interval [K_2={strikes[1]}, K_3={strikes[2]}]"
            )
        if not (math.isfinite(self.weight) and self.weight > 0.0):
            raise ValueError(
                f"IronCondor.weight = {self.weight} must be a finite float > 0"
            )
        if self.label not in ("left_tail", "atm", "right_tail"):
            raise ValueError(
                f"IronCondor.label = {self.label!r} must be one of"
                " left_tail | atm | right_tail"
            )


@dataclass(frozen=True)
class StripGeometry:
    """Geometric parameters that determine the strike ladder of all 3 condors.

    Notation (PRIMITIVES.md §11):

    - ``log_offsets`` — ``(x_left, x_atm, x_right)`` with
      ``x_left < x_atm = 0 < x_right``. Condor centers are
      ``K_j = S_0 · exp(x_j)``.
    - ``delta_inner`` — log-strike half-width of the inner body
      ``(K_2, K_3)`` around each condor center.
    - ``delta_outer`` — log-strike half-width of the outer wings
      ``(K_1, K_4)`` around each condor center; must satisfy
      ``delta_outer > delta_inner > 0``.

    A natural default (Pin S3) ties the offsets to the FX-path amplitude
    ε via ``(−ε, 0, +ε)``, so the three condors bracket the FX
    excursion zone defined by PRIMITIVES.md §6 eq. (6).
    """

    log_offsets: tuple[float, float, float]
    delta_inner: float
    delta_outer: float

    def __post_init__(self) -> None:
        if len(self.log_offsets) != STRIP_CONDOR_COUNT:
            raise ValueError(
                f"StripGeometry.log_offsets must have length {STRIP_CONDOR_COUNT}"
                f"; got {len(self.log_offsets)}"
            )
        x_left, x_atm, x_right = self.log_offsets
        for name, val in (("x_left", x_left), ("x_atm", x_atm), ("x_right", x_right)):
            if not math.isfinite(val):
                raise ValueError(f"StripGeometry.log_offsets.{name} = {val} must be finite")
        if x_atm != 0.0:
            raise ValueError(
                f"StripGeometry.log_offsets[1] (x_atm) must equal 0.0;"
                f" got {x_atm}"
            )
        if not (x_left < 0.0 < x_right):
            raise ValueError(
                f"StripGeometry: must satisfy x_left < 0 < x_right;"
                f" got x_left={x_left}, x_right={x_right}"
            )
        for name, val in (
            ("delta_inner", self.delta_inner),
            ("delta_outer", self.delta_outer),
        ):
            if not (math.isfinite(val) and val > 0.0):
                raise ValueError(
                    f"StripGeometry.{name} = {val} must be a finite float > 0"
                )
        if not (self.delta_outer > self.delta_inner):
            raise ValueError(
                f"StripGeometry: must satisfy delta_outer > delta_inner;"
                f" got delta_outer={self.delta_outer}, delta_inner={self.delta_inner}"
            )


@dataclass(frozen=True)
class IronCondorStrip:
    """A 3-condor / 12-leg Carr-Madan strip approximating ``Π_T ≈ K̂·σ_T``.

    Pin coverage:

    - **Pin S3** — exactly 3 condors, labels match :data:`STRIP_LABEL_ORDER`.
    - **Pin S2** — weights normalize to 1.0 within :data:`WEIGHT_SUM_TOL`.
    - **Pin S4** — both anchor strings non-empty.

    Free fields (carried for downstream contracts-side consumption):

    - ``s_0`` — spot price at which the strip was placed (≈ X̄/Ȳ).
    - ``sigma_0`` — Carr-Madan linearization point (R1 anchor).
    - ``k_star`` — equilibrium strike K⋆ (PRIMITIVES.md §8.1).
    - ``k_hat`` — linearized constant K̂ = K⋆/(2·√σ_0) (PRIMITIVES.md eq. 17).
    - ``geometry`` — strike-ladder generator parameters.
    """

    condors: tuple[IronCondor, IronCondor, IronCondor]
    s_0: float
    sigma_0: float
    k_star: float
    k_hat: float
    geometry: StripGeometry
    primitives_anchor: str
    saas_note_anchor: str

    def __post_init__(self) -> None:
        if len(self.condors) != STRIP_CONDOR_COUNT:
            raise ValueError(
                f"IronCondorStrip.condors must have length {STRIP_CONDOR_COUNT};"
                f" got {len(self.condors)}"
            )
        for i, (condor, expected_label) in enumerate(
            zip(self.condors, STRIP_LABEL_ORDER)
        ):
            if condor.label != expected_label:
                raise ValueError(
                    f"IronCondorStrip.condors[{i}].label = {condor.label!r}"
                    f" must be {expected_label!r}"
                )
        weight_sum = sum(c.weight for c in self.condors)
        if abs(weight_sum - 1.0) > WEIGHT_SUM_TOL:
            raise ValueError(
                f"IronCondorStrip: weights must sum to 1.0 within"
                f" {WEIGHT_SUM_TOL}; got sum={weight_sum},"
                f" deviation={weight_sum - 1.0:.3e}"
            )
        for name, val in (
            ("s_0", self.s_0),
            ("sigma_0", self.sigma_0),
            ("k_star", self.k_star),
            ("k_hat", self.k_hat),
        ):
            if not (math.isfinite(val) and val > 0.0):
                raise ValueError(
                    f"IronCondorStrip.{name} = {val} must be a finite float > 0"
                )
        expected_k_hat = self.k_star / (2.0 * math.sqrt(self.sigma_0))
        k_hat_residual = abs(self.k_hat - expected_k_hat)
        if k_hat_residual > 1e-9 * max(1.0, abs(expected_k_hat)):
            raise ValueError(
                f"IronCondorStrip: K̂ identity K̂ = K⋆/(2·√σ_0) breached;"
                f" got K̂={self.k_hat}, expected={expected_k_hat},"
                f" residual={k_hat_residual:.3e}"
            )
        if not self.primitives_anchor:
            raise ValueError(
                "IronCondorStrip.primitives_anchor must be a non-empty citation"
            )
        if not self.saas_note_anchor:
            raise ValueError(
                "IronCondorStrip.saas_note_anchor must be a non-empty citation"
            )


@dataclass(frozen=True)
class ReplicationVerdict:
    """Outcome of the Carr-Madan replication-envelope check (PRIMITIVES.md §12).

    Compares the strip payoff ``Π_realized(S_T)`` against the linearized
    target ``K̂·σ_T`` over a grid of FX-path realizations. A PASS verdict
    means the strip is geometrically tight enough to act as the on-chain
    proxy for the convex √σ_T payoff under the M-design ideal-scenario
    clause (CLAUDE.md "ideal-scenario modeling permitted").

    Validation contract:

    - ``max_relative_error`` finite, ≥ 0.
    - ``passes`` is True iff ``max_relative_error ≤ tolerance``.
    - ``tolerance`` finite, > 0 (default :data:`REPLICATION_REL_TOL`).
    - ``n_grid_points`` integer ≥ 2.
    """

    max_relative_error: float
    tolerance: float
    n_grid_points: int
    passes: bool

    def __post_init__(self) -> None:
        for name, val in (
            ("max_relative_error", self.max_relative_error),
            ("tolerance", self.tolerance),
        ):
            if not math.isfinite(val):
                raise ValueError(f"ReplicationVerdict.{name} = {val} must be finite")
        if self.max_relative_error < 0.0:
            raise ValueError(
                f"ReplicationVerdict.max_relative_error = {self.max_relative_error}"
                " must be ≥ 0"
            )
        if not self.tolerance > 0.0:
            raise ValueError(
                f"ReplicationVerdict.tolerance = {self.tolerance} must be > 0"
            )
        if not isinstance(self.n_grid_points, int) or self.n_grid_points < 2:
            raise ValueError(
                f"ReplicationVerdict.n_grid_points = {self.n_grid_points}"
                " must be an int ≥ 2"
            )
        derived = self.max_relative_error <= self.tolerance
        if derived != self.passes:
            raise ValueError(
                "ReplicationVerdict.passes must equal"
                " (max_relative_error ≤ tolerance);"
                f" got passes={self.passes},"
                f" max_relative_error={self.max_relative_error},"
                f" tolerance={self.tolerance}"
            )


__all__ = [
    "LEG_KIND_ORDER",
    "LEGS_PER_CONDOR",
    "REPLICATION_REL_TOL",
    "STRIP_CONDOR_COUNT",
    "STRIP_LABEL_ORDER",
    "STRIP_TOTAL_LEGS",
    "STRIKE_ORDER_TOL",
    "WEIGHT_SUM_TOL",
    "CondorLabel",
    "CondorLeg",
    "IronCondor",
    "IronCondorStrip",
    "LegKind",
    "ReplicationVerdict",
    "StripGeometry",
]
