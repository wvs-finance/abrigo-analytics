"""Verify-only API surface for SaaS-Builder Stage-2 notebooks-trio.

Per design v0.3 §3a. Three-tier: types (Value), checks (Callable),
io (IO Boundary). Notebooks import only from this module; no reach
into simulations.modules / simulations.utils internals.
"""
from __future__ import annotations

from simulations.saas_builder.verify.checks import (
    verify_r1_sigma_0_anchor,
    verify_r2_kappa_eliminated_in_pi_t,
    verify_r3_perpetual_identity,
    verify_r4_bracket_cardinality,
    verify_r5_marginalization_match,
    verify_r6_softplus_l1_tightness,
    verify_r7_s_t_pin,
    verify_r8_z_cap_closed_form,
)
from simulations.saas_builder.verify.io import (
    AuditBlockMismatch,
    CommittedArtifactLoader,
    GateVerdictSchemaError,
)
from simulations.saas_builder.verify.types import RTagVerdict, TrioRollup

__all__: list[str] = [
    "AuditBlockMismatch",
    "CommittedArtifactLoader",
    "GateVerdictSchemaError",
    "RTagVerdict",
    "TrioRollup",
    "verify_r1_sigma_0_anchor",
    "verify_r2_kappa_eliminated_in_pi_t",
    "verify_r3_perpetual_identity",
    "verify_r4_bracket_cardinality",
    "verify_r5_marginalization_match",
    "verify_r6_softplus_l1_tightness",
    "verify_r7_s_t_pin",
    "verify_r8_z_cap_closed_form",
]
