r"""Strike-placement + Carr-Madan weighting for the 3-condor strip.

Implements PRIMITIVES.md §10 (Carr-Madan replication) and §11 (Discrete
strip — Panoptic IronCondor implementation). All callables here are
free functions or frozen-dc ``__call__``s; NO IO and NO mutable state.

The strip emitter (``emit.StripEmitter``) consumes these functions to
produce ``IronCondor_strip.json`` from the cohort_4-pinned Stage-2
posterior fixtures (X̄/Ȳ, σ_0, K⋆, ε, ω).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from simulations.saas_builder.cohort_5_strip._errors import (
    StripGeometryError,
    WeightNormalizationError,
)
from simulations.saas_builder.cohort_5_strip.types import (
    LEG_KIND_ORDER,
    STRIP_CONDOR_COUNT,
    STRIP_LABEL_ORDER,
    WEIGHT_SUM_TOL,
    CondorLeg,
    IronCondor,
    IronCondorStrip,
    StripGeometry,
)

#: Default citation anchors (Pin S4).
DEFAULT_PRIMITIVES_ANCHOR: Final[str] = (
    "PRIMITIVES.md §10 (Carr-Madan eq. 18) + §11 (Discrete strip eq. 20)"
)

DEFAULT_SAAS_NOTE_ANCHOR: Final[str] = (
    "SaaS_Builders_AI_NativeBuilders.md §Payoff (Π = K_s·√σ_T from §8.1)"
)

#: Default Carr-Madan strip geometry parameters.
#:
#: Log-offsets at ±ε (default ε = 0.1 per PRIMITIVES.md §5 / Stage-2
#: canonical fixture) place the left/right tail condors at the FX-
#: excursion bounds. ``delta_inner = ε`` tiles each condor's inner
#: body across the full offset spacing so there are NO gaps between
#: adjacent condors (the left-tail's right body-edge meets the ATM's
#: left body-edge meets the right-tail's left body-edge at S_0).
#: ``delta_outer = 2·ε`` extends the outer wings a full ε beyond each
#: condor's body, giving the long-vol cap room to widen.
#:
#: Under this tiling, the strip payoff at spot Π_strip(S_0) is exactly
#: zero (Pin S5 strict floor) — every condor's body covers S_0 (ATM)
#: or borders it (left/right tails), so all 12 legs are OTM or
#: at-strike, contributing nothing.
DEFAULT_EPSILON: Final[float] = 0.1
DEFAULT_DELTA_INNER: Final[float] = DEFAULT_EPSILON  # 0.10
DEFAULT_DELTA_OUTER: Final[float] = 2.0 * DEFAULT_EPSILON  # 0.20


def default_strip_geometry(epsilon: float = DEFAULT_EPSILON) -> StripGeometry:
    """Return the canonical N=3 strip geometry tied to FX-path amplitude ε.

    Log-offsets are ``(−ε, 0, +ε)`` so the left/right condors bracket
    the deterministic FX-path excursion zone of PRIMITIVES.md §6 eq. (6).
    Inner/outer half-widths default to ε/4 and 3ε/4 — see
    :data:`DEFAULT_DELTA_INNER` and :data:`DEFAULT_DELTA_OUTER`.

    Raises:
        StripGeometryError: If ``epsilon`` is non-finite or non-positive.
    """
    if not (math.isfinite(epsilon) and epsilon > 0.0):
        raise StripGeometryError(
            f"default_strip_geometry: epsilon = {epsilon}"
            " must be a finite float > 0"
        )
    return StripGeometry(
        log_offsets=(-epsilon, 0.0, +epsilon),
        delta_inner=epsilon,
        delta_outer=2.0 * epsilon,
    )


def place_condor_centers(
    s_0: float, log_offsets: tuple[float, float, float]
) -> tuple[float, float, float]:
    """Return condor centers ``K_j = S_0 · exp(x_j)`` for j ∈ {left, atm, right}.

    Per PRIMITIVES.md §11: each condor is placed at a multiplicative
    offset from spot ``S_0`` in log-strike units. The default offsets
    (PRIMITIVES.md §11 Path A v2) place left/right at ``±ε`` so the
    condors bracket the FX-path excursion zone.

    Raises:
        StripGeometryError: If ``s_0`` is non-finite or non-positive,
            or if the resulting centers are not strictly increasing.
    """
    if not (math.isfinite(s_0) and s_0 > 0.0):
        raise StripGeometryError(
            f"place_condor_centers: s_0 = {s_0} must be a finite float > 0"
        )
    centers = tuple(s_0 * math.exp(x) for x in log_offsets)
    if not (centers[0] < centers[1] < centers[2]):
        raise StripGeometryError(
            "place_condor_centers: centers not strictly increasing;"
            f" got {centers}"
        )
    return centers  # type: ignore[return-value]


def compute_carr_madan_weights(
    centers: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Return normalized Carr-Madan weights ``w_j ∝ 1/K_j²``.

    Per PRIMITIVES.md §10 eq. (18), the variance contribution from each
    strike interval scales as ``1/K²``. Normalizing so ``sum(w_j) = 1``
    gives a unit-notional strip whose absolute Carr-Madan scale is
    carried separately on the strip's K̂ field.

    Raises:
        WeightNormalizationError: If any center is non-positive, or if
            the normalized weights do not sum to 1.0 within
            :data:`WEIGHT_SUM_TOL`.
    """
    for i, k in enumerate(centers):
        if not (math.isfinite(k) and k > 0.0):
            raise WeightNormalizationError(
                f"compute_carr_madan_weights: centers[{i}] = {k}"
                " must be a finite float > 0"
            )
    raw = tuple(1.0 / (k * k) for k in centers)
    total = sum(raw)
    if total <= 0.0:
        raise WeightNormalizationError(
            f"compute_carr_madan_weights: raw weight sum {total} non-positive"
        )
    normalized = tuple(w / total for w in raw)
    s = sum(normalized)
    if abs(s - 1.0) > WEIGHT_SUM_TOL:
        raise WeightNormalizationError(
            "compute_carr_madan_weights: normalized sum deviates from 1.0"
            f" by {s - 1.0:.3e} (tol {WEIGHT_SUM_TOL:.3e})"
        )
    return normalized  # type: ignore[return-value]


@dataclass(frozen=True)
class CondorBuilder:
    """Construct a single reverse-IC condor from (center, widths, weight, label).

    Strikes are placed symmetrically around the center in log-strike
    units: ``K_i = center · exp(±δ_inner_or_outer)``. The leg-kind
    structure follows :data:`LEG_KIND_ORDER` (long-vol convention).
    """

    def __call__(
        self,
        center: float,
        delta_inner: float,
        delta_outer: float,
        weight: float,
        label: str,
    ) -> IronCondor:
        if not (math.isfinite(center) and center > 0.0):
            raise StripGeometryError(
                f"CondorBuilder: center = {center} must be a finite float > 0"
            )
        if not (math.isfinite(delta_inner) and delta_inner > 0.0):
            raise StripGeometryError(
                f"CondorBuilder: delta_inner = {delta_inner}"
                " must be a finite float > 0"
            )
        if not (math.isfinite(delta_outer) and delta_outer > delta_inner):
            raise StripGeometryError(
                f"CondorBuilder: delta_outer = {delta_outer}"
                f" must be a finite float > delta_inner = {delta_inner}"
            )
        if label not in ("left_tail", "atm", "right_tail"):
            raise StripGeometryError(
                f"CondorBuilder: label = {label!r} must be one of"
                " left_tail | atm | right_tail"
            )
        k_1 = center * math.exp(-delta_outer)
        k_2 = center * math.exp(-delta_inner)
        k_3 = center * math.exp(+delta_inner)
        k_4 = center * math.exp(+delta_outer)
        legs = tuple(
            CondorLeg(kind=kind, strike=strike)
            for kind, strike in zip(LEG_KIND_ORDER, (k_1, k_2, k_3, k_4))
        )
        return IronCondor(
            legs=legs,  # type: ignore[arg-type]
            center=center,
            weight=weight,
            label=label,  # type: ignore[arg-type]
        )


build_iron_condor = CondorBuilder()


@dataclass(frozen=True)
class StripBuilder:
    """Compose the full 3-condor strip from spot + geometry + cohort-4 fixtures.

    Inputs are the Stage-2 pinned scalars:

    - ``s_0`` — spot price (≈ X̄/Ȳ, default canonical 4000 COP/USD).
    - ``sigma_0`` — Carr-Madan linearization point (R1 anchor 20,000).
    - ``k_star`` — equilibrium strike K⋆ (PRIMITIVES.md §8.1).
    - ``geometry`` — strike-ladder generator.

    Output is a frozen ``IronCondorStrip`` with all 12 legs enumerated,
    Carr-Madan weights normalized, and K̂ pinned to K⋆/(2·√σ_0).
    """

    primitives_anchor: str = DEFAULT_PRIMITIVES_ANCHOR
    saas_note_anchor: str = DEFAULT_SAAS_NOTE_ANCHOR

    def __call__(
        self,
        s_0: float,
        sigma_0: float,
        k_star: float,
        geometry: StripGeometry,
    ) -> IronCondorStrip:
        if not (math.isfinite(sigma_0) and sigma_0 > 0.0):
            raise StripGeometryError(
                f"StripBuilder: sigma_0 = {sigma_0} must be a finite float > 0"
            )
        if not (math.isfinite(k_star) and k_star > 0.0):
            raise StripGeometryError(
                f"StripBuilder: k_star = {k_star} must be a finite float > 0"
            )
        centers = place_condor_centers(s_0, geometry.log_offsets)
        weights = compute_carr_madan_weights(centers)
        condors = tuple(
            build_iron_condor(
                center=center,
                delta_inner=geometry.delta_inner,
                delta_outer=geometry.delta_outer,
                weight=weight,
                label=label,
            )
            for center, weight, label in zip(centers, weights, STRIP_LABEL_ORDER)
        )
        if len(condors) != STRIP_CONDOR_COUNT:
            raise StripGeometryError(
                f"StripBuilder: produced {len(condors)} condors;"
                f" expected {STRIP_CONDOR_COUNT}"
            )
        k_hat = k_star / (2.0 * math.sqrt(sigma_0))
        return IronCondorStrip(
            condors=condors,  # type: ignore[arg-type]
            s_0=s_0,
            sigma_0=sigma_0,
            k_star=k_star,
            k_hat=k_hat,
            geometry=geometry,
            primitives_anchor=self.primitives_anchor,
            saas_note_anchor=self.saas_note_anchor,
        )


build_strip = StripBuilder()


__all__ = [
    "DEFAULT_DELTA_INNER",
    "DEFAULT_DELTA_OUTER",
    "DEFAULT_EPSILON",
    "DEFAULT_PRIMITIVES_ANCHOR",
    "DEFAULT_SAAS_NOTE_ANCHOR",
    "CondorBuilder",
    "StripBuilder",
    "build_iron_condor",
    "build_strip",
    "compute_carr_madan_weights",
    "default_strip_geometry",
    "place_condor_centers",
]
