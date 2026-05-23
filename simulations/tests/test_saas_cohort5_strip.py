r"""Tests for SAAS-COHORT-5-STRIP — Carr-Madan 3-condor (12-leg) strip emit.

Coverage:

- **Pin S1** — strike-ladder invariant (K_1 < K_2 < K_3 < K_4) and
  reverse-IC leg-kind ordering. Rejection of permutations.
- **Pin S2** — Carr-Madan weight normalization (sum(w_j) = 1.0 within
  WEIGHT_SUM_TOL); w_j ∝ 1/K_j².
- **Pin S3** — strip cardinality (exactly 3 condors, 12 legs total).
- **Pin S4** — citation strings non-empty.
- **Pin S5** — long-vol convexity signature (Π_strip(S_0) = 0 under
  tiled-body geometry; Π_strip > 0 on both sides of the body).
- **Pin S6** — Carr-Madan envelope passes at the documented 35%
  tolerance for the 3-condor strip.
- **Pin S7** — StripEmitter writes JSON + sidecar; JSON round-trips.
- **Pin S8** — audit-block determinism (same inputs → same digest;
  geometry change → different digest).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from simulations.saas_builder.cohort_5_strip import (
    LEG_KIND_ORDER,
    LEGS_PER_CONDOR,
    REPLICATION_REL_TOL,
    STRIP_CONDOR_COUNT,
    STRIP_LABEL_ORDER,
    STRIP_TOTAL_LEGS,
    WEIGHT_SUM_TOL,
    CondorLeg,
    IronCondor,
    IronCondorStrip,
    ReplicationToleranceError,
    StripBuilder,
    StripEmitter,
    StripGeometry,
    StripGeometryError,
    WeightNormalizationError,
    assert_long_vol_signature,
    build_iron_condor,
    build_strip,
    compute_carr_madan_weights,
    condor_payoff,
    default_strip_geometry,
    place_condor_centers,
    strip_payoff,
    verify_carr_madan_envelope,
)


# ─── Canonical Stage-2 fixtures ──────────────────────────────────────────────

S_0_CANONICAL = 4000.0  # X̄/Ȳ at TP1
SIGMA_0_CANONICAL = 20_000.0  # R1 anchor
K_STAR_CANONICAL = 4_687.94  # Z_cap_pinned.Z_cop_per_month


@pytest.fixture
def canonical_strip() -> IronCondorStrip:
    """Build the canonical 3-condor strip used by most tests."""
    return build_strip(
        s_0=S_0_CANONICAL,
        sigma_0=SIGMA_0_CANONICAL,
        k_star=K_STAR_CANONICAL,
        geometry=default_strip_geometry(),
    )


# ─── Pin S1 — strike ladder ──────────────────────────────────────────────────


def test_pin_s1_strike_ladder_strict_ordering(canonical_strip: IronCondorStrip) -> None:
    for c in canonical_strip.condors:
        strikes = [leg.strike for leg in c.legs]
        for i in range(LEGS_PER_CONDOR - 1):
            assert strikes[i] < strikes[i + 1], (
                f"Condor {c.label!r}: K_{i + 1} = {strikes[i]} should be"
                f" < K_{i + 2} = {strikes[i + 1]}"
            )


def test_pin_s1_leg_kind_order(canonical_strip: IronCondorStrip) -> None:
    for c in canonical_strip.condors:
        actual = tuple(leg.kind for leg in c.legs)
        assert actual == LEG_KIND_ORDER, (
            f"Condor {c.label!r} leg kinds = {actual} ≠ {LEG_KIND_ORDER}"
        )


def test_pin_s1_reject_wrong_strike_order() -> None:
    with pytest.raises(ValueError, match="strike ladder violated"):
        IronCondor(
            legs=(
                CondorLeg(kind="short_put", strike=100.0),
                CondorLeg(kind="long_put", strike=90.0),  # wrong: 90 < 100
                CondorLeg(kind="long_call", strike=110.0),
                CondorLeg(kind="short_call", strike=120.0),
            ),
            center=100.0,
            weight=1.0,
            label="atm",
        )


def test_pin_s1_reject_wrong_leg_kind_permutation() -> None:
    with pytest.raises(ValueError, match="must be 'short_put'"):
        IronCondor(
            legs=(
                CondorLeg(kind="long_put", strike=90.0),  # wrong: expected short_put
                CondorLeg(kind="short_put", strike=95.0),
                CondorLeg(kind="long_call", strike=105.0),
                CondorLeg(kind="short_call", strike=110.0),
            ),
            center=100.0,
            weight=1.0,
            label="atm",
        )


# ─── Pin S2 — Carr-Madan weight normalization ────────────────────────────────


def test_pin_s2_weights_sum_to_one(canonical_strip: IronCondorStrip) -> None:
    s = sum(c.weight for c in canonical_strip.condors)
    assert abs(s - 1.0) <= WEIGHT_SUM_TOL


def test_pin_s2_weights_proportional_to_inverse_k_squared(
    canonical_strip: IronCondorStrip,
) -> None:
    """w_j / w_k should equal (K_k / K_j)² for any pair."""
    centers = tuple(c.center for c in canonical_strip.condors)
    weights = tuple(c.weight for c in canonical_strip.condors)
    for j in range(STRIP_CONDOR_COUNT):
        for k in range(STRIP_CONDOR_COUNT):
            if j == k:
                continue
            lhs = weights[j] / weights[k]
            rhs = (centers[k] ** 2) / (centers[j] ** 2)
            assert math.isclose(lhs, rhs, rel_tol=1e-12), (
                f"w_{j} / w_{k} = {lhs} ≠ (K_{k} / K_{j})² = {rhs}"
            )


def test_pin_s2_compute_weights_rejects_nonpositive_center() -> None:
    with pytest.raises(WeightNormalizationError, match="must be a finite float > 0"):
        compute_carr_madan_weights((100.0, 0.0, 110.0))


# ─── Pin S3 — strip cardinality ──────────────────────────────────────────────


def test_pin_s3_strip_has_three_condors(canonical_strip: IronCondorStrip) -> None:
    assert len(canonical_strip.condors) == STRIP_CONDOR_COUNT == 3


def test_pin_s3_strip_has_twelve_legs(canonical_strip: IronCondorStrip) -> None:
    n_legs = sum(len(c.legs) for c in canonical_strip.condors)
    assert n_legs == STRIP_TOTAL_LEGS == 12


def test_pin_s3_strip_labels_match_canonical_order(
    canonical_strip: IronCondorStrip,
) -> None:
    labels = tuple(c.label for c in canonical_strip.condors)
    assert labels == STRIP_LABEL_ORDER


def test_pin_s3_geometry_log_offsets_strictly_increasing(
    canonical_strip: IronCondorStrip,
) -> None:
    x = canonical_strip.geometry.log_offsets
    assert x[0] < 0.0 == x[1] < x[2]


# ─── Pin S4 — citations ──────────────────────────────────────────────────────


def test_pin_s4_anchors_non_empty(canonical_strip: IronCondorStrip) -> None:
    assert canonical_strip.primitives_anchor != ""
    assert canonical_strip.saas_note_anchor != ""
    assert "PRIMITIVES.md" in canonical_strip.primitives_anchor


# ─── Pin S5 — long-vol signature ─────────────────────────────────────────────


def test_pin_s5_spot_floor_is_zero_under_tiled_geometry(
    canonical_strip: IronCondorStrip,
) -> None:
    """With delta_inner = ε, the body of each condor borders S_0."""
    floor = strip_payoff(canonical_strip, canonical_strip.s_0)
    assert abs(floor) < 1e-9 * canonical_strip.s_0


def test_pin_s5_long_vol_monotone_away_from_spot(
    canonical_strip: IronCondorStrip,
) -> None:
    s_0 = canonical_strip.s_0
    di = canonical_strip.geometry.delta_inner
    assert strip_payoff(canonical_strip, s_0 * math.exp(+di)) > 0.0
    assert strip_payoff(canonical_strip, s_0 * math.exp(-di)) > 0.0


def test_pin_s5_assert_long_vol_signature_passes(
    canonical_strip: IronCondorStrip,
) -> None:
    # Should not raise.
    assert_long_vol_signature(canonical_strip)


# ─── Pin S6 — envelope ────────────────────────────────────────────────────────


def test_pin_s6_replication_envelope_passes_at_default_tolerance(
    canonical_strip: IronCondorStrip,
) -> None:
    verdict = verify_carr_madan_envelope(canonical_strip)
    assert verdict.passes
    assert verdict.tolerance == REPLICATION_REL_TOL
    assert verdict.n_grid_points >= 3


def test_pin_s6_envelope_fails_at_too_tight_tolerance(
    canonical_strip: IronCondorStrip,
) -> None:
    """At a 5% tolerance, the 3-condor strip is expected to FAIL."""
    from simulations.saas_builder.cohort_5_strip import CarrMadanEnvelopeVerifier
    verdict = CarrMadanEnvelopeVerifier(tolerance=0.05)(canonical_strip)
    assert not verdict.passes


# ─── Pin S7 — emit + round-trip ──────────────────────────────────────────────


def test_pin_s7_emit_writes_json_and_sidecar(tmp_path: Path) -> None:
    # Place Z_cap_pinned.json in tmp_path by copying from the repo data dir.
    repo_data = Path("simulations/saas_builder/data/Z_cap_pinned.json")
    if not repo_data.is_file():
        pytest.skip("Z_cap_pinned.json not in repo (cohort_4 emit not run)")
    target_z = tmp_path / "Z_cap_pinned.json"
    target_z.write_bytes(repo_data.read_bytes())
    emitter = StripEmitter(emit_dir=tmp_path, z_cap_path=target_z)
    strip, verdict, audit = emitter()
    assert (tmp_path / "IronCondor_strip.json").is_file()
    assert (tmp_path / "IronCondor_strip.STRIKES.md").is_file()
    assert verdict.passes
    assert len(audit) == 64
    # Round-trip JSON read-back equality.
    payload = json.loads((tmp_path / "IronCondor_strip.json").read_text())
    assert payload["audit_block"] == audit
    assert payload["schema_version"] == "v1.0"
    assert len(payload["condors"]) == 3
    for c_payload in payload["condors"]:
        assert len(c_payload["legs"]) == 4


# ─── Pin S8 — audit-block determinism ────────────────────────────────────────


def test_pin_s8_audit_block_deterministic(tmp_path: Path) -> None:
    repo_data = Path("simulations/saas_builder/data/Z_cap_pinned.json")
    if not repo_data.is_file():
        pytest.skip("Z_cap_pinned.json not in repo")
    target_z = tmp_path / "Z_cap_pinned.json"
    target_z.write_bytes(repo_data.read_bytes())
    emitter1 = StripEmitter(emit_dir=tmp_path / "run1", z_cap_path=target_z)
    emitter2 = StripEmitter(emit_dir=tmp_path / "run2", z_cap_path=target_z)
    _, _, audit1 = emitter1()
    _, _, audit2 = emitter2()
    assert audit1 == audit2


def test_pin_s8_audit_block_changes_with_geometry(tmp_path: Path) -> None:
    repo_data = Path("simulations/saas_builder/data/Z_cap_pinned.json")
    if not repo_data.is_file():
        pytest.skip("Z_cap_pinned.json not in repo")
    target_z = tmp_path / "Z_cap_pinned.json"
    target_z.write_bytes(repo_data.read_bytes())
    geom1 = default_strip_geometry()
    geom2 = StripGeometry(
        log_offsets=(-0.12, 0.0, +0.12),
        delta_inner=0.12,
        delta_outer=0.24,
    )
    emitter1 = StripEmitter(
        emit_dir=tmp_path / "run1", z_cap_path=target_z, geometry=geom1
    )
    emitter2 = StripEmitter(
        emit_dir=tmp_path / "run2", z_cap_path=target_z, geometry=geom2
    )
    _, _, audit1 = emitter1()
    _, _, audit2 = emitter2()
    assert audit1 != audit2


# ─── Geometry helpers ────────────────────────────────────────────────────────


def test_place_condor_centers_correct_for_default_offsets() -> None:
    centers = place_condor_centers(4000.0, (-0.1, 0.0, +0.1))
    assert math.isclose(centers[0], 4000.0 * math.exp(-0.1), rel_tol=1e-12)
    assert math.isclose(centers[1], 4000.0, rel_tol=1e-12)
    assert math.isclose(centers[2], 4000.0 * math.exp(+0.1), rel_tol=1e-12)


def test_place_condor_centers_rejects_nonpositive_spot() -> None:
    with pytest.raises(StripGeometryError, match="must be a finite float > 0"):
        place_condor_centers(0.0, (-0.1, 0.0, +0.1))


def test_strip_geometry_rejects_inner_gte_outer() -> None:
    with pytest.raises(ValueError, match="delta_outer > delta_inner"):
        StripGeometry(
            log_offsets=(-0.1, 0.0, +0.1), delta_inner=0.2, delta_outer=0.1
        )


def test_strip_geometry_rejects_nonzero_x_atm() -> None:
    with pytest.raises(ValueError, match="x_atm.*must equal 0"):
        StripGeometry(
            log_offsets=(-0.1, 0.05, +0.1), delta_inner=0.05, delta_outer=0.1
        )


def test_condor_payoff_zero_in_inner_body() -> None:
    c = build_iron_condor(
        center=100.0,
        delta_inner=0.1,
        delta_outer=0.2,
        weight=1.0,
        label="atm",
    )
    assert condor_payoff(c, 100.0) == 0.0
    assert condor_payoff(c, c.legs[1].strike) == 0.0
    assert condor_payoff(c, c.legs[2].strike) == 0.0


def test_condor_payoff_capped_in_outer_wings() -> None:
    c = build_iron_condor(
        center=100.0,
        delta_inner=0.1,
        delta_outer=0.2,
        weight=1.0,
        label="atm",
    )
    k1, k2, k3, k4 = (leg.strike for leg in c.legs)
    deep_down = c.legs[0].strike * 0.5
    deep_up = c.legs[3].strike * 2.0
    assert math.isclose(condor_payoff(c, deep_down), k2 - k1, rel_tol=1e-12)
    assert math.isclose(condor_payoff(c, deep_up), k4 - k3, rel_tol=1e-12)
