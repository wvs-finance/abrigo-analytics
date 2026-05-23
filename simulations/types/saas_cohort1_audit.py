"""Audit Value tier — frozen-dataclass mirror of `_AUDIT.json` schema.

Hosts the existing `_AUDIT.json` schema as a frozen-dataclass Value type.
Created by SaaS-Builder Stage-2 verify sub-package Phase 0; consumed by
`simulations.utils.json_io.AuditReader` and threaded into the trio audit
chain through `simulations.saas_builder.verify.io.CommittedArtifactLoader`.

Math pin: not directly involved. The hosted `audit_block` is the same
64-char lowercase hex sha256 produced by
`simulations.utils.audit_block.compute_audit_block`.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Final

#: Compiled regex matching exactly 64 lowercase hex characters (sha256 hex form).
_AUDIT_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")


class AuditValueError(ValueError):
    """Raised when an Audit Value fails post-init validation."""


@dataclass(frozen=True)
class AuditVerdict:
    """C1 posterior diagnostic block (six gate metrics)."""

    rhat_max: float
    ess_bulk_min: float
    ess_tail_min: float
    divergence_frac: float
    ci_width_ratio_max: float
    n_chains: int
    n_draws_per_chain: int

    def __post_init__(self) -> None:
        if self.n_chains <= 0:
            raise AuditValueError(f"n_chains must be positive, got {self.n_chains}")
        if self.n_draws_per_chain <= 0:
            raise AuditValueError(
                f"n_draws_per_chain must be positive, got {self.n_draws_per_chain}"
            )
        for name, val in (
            ("rhat_max", self.rhat_max),
            ("ess_bulk_min", self.ess_bulk_min),
            ("ess_tail_min", self.ess_tail_min),
            ("divergence_frac", self.divergence_frac),
            ("ci_width_ratio_max", self.ci_width_ratio_max),
        ):
            if not math.isfinite(val):
                raise AuditValueError(
                    f"{name} must be finite, got {val}"
                )
        if self.rhat_max < 1.0:
            raise AuditValueError(
                f"rhat_max must be >= 1.0 (R-hat bounded below by 1 by construction),"
                f" got {self.rhat_max}"
            )
        if self.ess_bulk_min < 0.0:
            raise AuditValueError(
                f"ess_bulk_min must be >= 0, got {self.ess_bulk_min}"
            )
        if self.ess_tail_min < 0.0:
            raise AuditValueError(
                f"ess_tail_min must be >= 0, got {self.ess_tail_min}"
            )
        if not (0.0 <= self.divergence_frac <= 1.0):
            raise AuditValueError(
                f"divergence_frac must be in [0.0, 1.0], got {self.divergence_frac}"
            )
        if self.ci_width_ratio_max <= 0.0:
            raise AuditValueError(
                f"ci_width_ratio_max must be > 0, got {self.ci_width_ratio_max}"
            )


@dataclass(frozen=True)
class Audit:
    """C1 audit block — input-data lineage + posterior diagnostic verdict."""

    audit_block: str
    schema_version: str
    synthetic_tau_path: str
    cohort_prior_path: str
    month: int
    n_rows_synthetic: int
    verdict: AuditVerdict

    def __post_init__(self) -> None:
        if not _AUDIT_BLOCK_RE.fullmatch(self.audit_block):
            raise AuditValueError(
                f"audit_block must be 64-char lowercase hex sha256; "
                f"got {self.audit_block!r} (len={len(self.audit_block)})"
            )
        if self.schema_version.strip() == "":
            raise AuditValueError(
                f"schema_version must be non-empty, got {self.schema_version!r}"
            )
        if self.n_rows_synthetic < 0:
            raise AuditValueError(
                f"n_rows_synthetic must be non-negative, got {self.n_rows_synthetic}"
            )
        if self.month < 1 or self.month > 12:
            raise AuditValueError(f"month must be in [1, 12], got {self.month}")
