r"""SAAS-COHORT-5-STRIP — Carr-Madan 3-condor (12-leg) IronCondor strip.

Stage-2 → Stage-3 hand-off module. Takes the Stage-2 pinned cohort-4
artifacts (``Z_cap_pinned.json``, σ_0 anchor, K⋆ identification) and
emits the deterministic 12-leg strike ladder + Carr-Madan weights
that the contracts-side Foundry deployment consumes to provision the
Panoptic position family.

**Strategy framing (NOT the ground truth — best-fit available).** The
IronCondor (reverse-IC, long-vol convention) was selected as the
Panoptic primitive with the most legs available at the Stage-2 horizon
and therefore the closest finite-leg approximation to the convex
``√σ_T`` payoff. It is *not* the canonical ground-truth replication —
the canonical form (PRIMITIVES.md §10) is a continuous Carr-Madan
integral that cannot be deployed as-is on any current AMM-options
venue. The 12-leg discrete strip is one admissible discretization;
Stage-3 may identify a Panoptic strategy that fits the post-Stage-2
results better (different leg topology, alternative primitive, larger
N). The strategy-selection question is a Stage-3 open item alongside
real-data conditioning of the cohort distributions.

Pin coverage (Stage-2 → Stage-3 hand-off):

- **Pin S1 — strike ladder** (types.IronCondor): K_1 < K_2 < K_3 < K_4
  with reverse-IC long-vol leg-kind convention.
- **Pin S2 — Carr-Madan weight scaling** (geometry.compute_carr_madan_weights):
  w_j ∝ 1/K_j² normalized so sum(w_j) = 1.
- **Pin S3 — N=3 strip geometry** (types.IronCondorStrip): exactly
  3 condors at log-offsets (−ε, 0, +ε) = 12 legs total.
- **Pin S4 — anchor citations** (types.IronCondorStrip): non-empty
  PRIMITIVES.md / SaaS-note references on every emitted artifact.
- **Pin S5 — long-vol signature** (replication.assert_long_vol_signature):
  Π_strip(S_0) ≡ 0, Π_strip(S_T) > 0 for |S_T − S_0| outside the inner body.
- **Pin S6 — replication envelope** (replication.CarrMadanEnvelopeVerifier):
  centered-strip max relative error vs log-contract proxy ≤ 35% over
  a 17-point grid (default ``REPLICATION_REL_TOL`` in types.py). The
  35% ceiling reflects the theoretical floor for a 3-piece linear
  approximation of x² (≈ 33%); finer-N strips tighten this.
- **Pin S7 — strip artifact emit** (emit.StripEmitter): writes
  ``IronCondor_strip.json`` + ``IronCondor_strip.STRIKES.md`` into
  ``simulations/saas_builder/data/``.
- **Pin S8 — audit-block lineage** (emit._compute_strip_audit_block):
  sha256 over (cohort-4 audit + spec path + canonical strip payload).

Three-tier discipline (functional-python skill):

- ``types.py`` — Value tier (frozen-dc + ``__post_init__``).
- ``geometry.py`` / ``replication.py`` — Callable tier (frozen-dc +
  ``__call__`` or free functions).
- ``emit.py`` — IO Boundary tier (class with ``__init__``).
- ``_errors.py`` — typed cohort-local exceptions.

Tier-import discipline (NON-NEGOTIABLE):

- May import: ``simulations.types``, ``simulations.modules``,
  ``simulations.utils``, ``simulations.saas_builder.cohort_4`` (read-only
  consumer of the cohort-4 JSON artifact via the shipped
  ``ZCapPinnedReader``).
- May NOT modify any of the above.
"""

from __future__ import annotations

from simulations.saas_builder.cohort_5_strip._errors import (
    AuditBlockDriftError,
    ReplicationToleranceError,
    StripGeometryError,
    WeightNormalizationError,
)
from simulations.saas_builder.cohort_5_strip.emit import (
    DEFAULT_EMIT_DIR,
    DEFAULT_SPEC_PATH,
    DEFAULT_Z_CAP_PATH,
    STRIP_JSON_FILENAME,
    STRIP_SCHEMA_VERSION,
    STRIP_SIDECAR_FILENAME,
    StripEmitter,
)
from simulations.saas_builder.cohort_5_strip.geometry import (
    DEFAULT_DELTA_INNER,
    DEFAULT_DELTA_OUTER,
    DEFAULT_EPSILON,
    DEFAULT_PRIMITIVES_ANCHOR,
    DEFAULT_SAAS_NOTE_ANCHOR,
    CondorBuilder,
    StripBuilder,
    build_iron_condor,
    build_strip,
    compute_carr_madan_weights,
    default_strip_geometry,
    place_condor_centers,
)
from simulations.saas_builder.cohort_5_strip.replication import (
    CarrMadanEnvelopeVerifier,
    assert_long_vol_signature,
    condor_payoff,
    log_contract_proxy,
    strip_payoff,
    verify_carr_madan_envelope,
)
from simulations.saas_builder.cohort_5_strip.types import (
    LEG_KIND_ORDER,
    LEGS_PER_CONDOR,
    REPLICATION_REL_TOL,
    STRIP_CONDOR_COUNT,
    STRIP_LABEL_ORDER,
    STRIP_TOTAL_LEGS,
    WEIGHT_SUM_TOL,
    CondorLabel,
    CondorLeg,
    IronCondor,
    IronCondorStrip,
    LegKind,
    ReplicationVerdict,
    StripGeometry,
)

__all__ = [
    "AuditBlockDriftError",
    "CarrMadanEnvelopeVerifier",
    "CondorBuilder",
    "CondorLabel",
    "CondorLeg",
    "DEFAULT_DELTA_INNER",
    "DEFAULT_DELTA_OUTER",
    "DEFAULT_EMIT_DIR",
    "DEFAULT_EPSILON",
    "DEFAULT_PRIMITIVES_ANCHOR",
    "DEFAULT_SAAS_NOTE_ANCHOR",
    "DEFAULT_SPEC_PATH",
    "DEFAULT_Z_CAP_PATH",
    "IronCondor",
    "IronCondorStrip",
    "LEGS_PER_CONDOR",
    "LEG_KIND_ORDER",
    "LegKind",
    "REPLICATION_REL_TOL",
    "ReplicationToleranceError",
    "ReplicationVerdict",
    "STRIP_CONDOR_COUNT",
    "STRIP_JSON_FILENAME",
    "STRIP_LABEL_ORDER",
    "STRIP_SCHEMA_VERSION",
    "STRIP_SIDECAR_FILENAME",
    "STRIP_TOTAL_LEGS",
    "StripBuilder",
    "StripEmitter",
    "StripGeometry",
    "StripGeometryError",
    "WEIGHT_SUM_TOL",
    "WeightNormalizationError",
    "assert_long_vol_signature",
    "build_iron_condor",
    "build_strip",
    "compute_carr_madan_weights",
    "condor_payoff",
    "default_strip_geometry",
    "log_contract_proxy",
    "place_condor_centers",
    "strip_payoff",
    "verify_carr_madan_envelope",
]
