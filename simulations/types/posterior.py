"""Posterior-draw and emission Value containers.

Covers spec §10 emission schemas at the **Value-tier** layer (the *row*
TypedDict shapes used by the parquet/JSON readers live in
``simulations.utils`` per Phase 1 reconciliation §2.1):

- ``PosteriorDraws`` — frozen-dc holding numpy posterior arrays plus the
  parameter-metadata that disambiguates them. Consumed by sticky-cost /
  Z-pin downstream Callables.
- ``MonthlyCDF`` — pinned-percentile CDF (p10 / p50 / p90 / p99 per spec
  §9 TODO-COHORT-1 verdict gate).
- ``ZCapPinned`` — emission Value for ``estimates/Z_cap_pinned.json`` per
  spec §10. Includes ``schema_version`` per Phase 1 reconciliation §2.4.

Math pin involvement: M4 schema columns are validated at the IO boundary
in ``simulations.utils``. This file only carries the typed in-memory Values
that the IO boundary returns to consumers.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, field
from typing import Final, Literal, Mapping

import numpy as np
from numpy.typing import NDArray

from simulations.types.tier import TIER_IDS, TierID


def _is_finite_positive(x: float) -> bool:
    """Return True iff x is a finite (non-inf, non-NaN) strictly-positive float."""
    return math.isfinite(x) and x > 0.0


#: Compiled regex matching exactly 64 lowercase hex characters (sha256 hex form).
_AUDIT_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")

# ─── Module-level constants ───────────────────────────────────────────────────

#: Default schema version for emission artifacts (Phase 1 reconciliation §2.4).
#:
#: SAAS-COHORT-CLOSE Phase 4 — schema v1.0 → v1.1 additive bump:
#: v1.1 adds the optional ``sign_verdicts`` field on ``ZCapPinned``
#: (per-test-point sign certification absorbed from the prior
#: ``Z_cap_pinned.SIGN_VERDICTS.md`` sidecar). v1.0 readers continue
#: to work unchanged — the new field defaults to ``None`` and is
#: emitted by the writer only when populated. v1.1 writers MUST set
#: ``schema_version="v1.1"``; v1.0 writers MUST set ``"v1.0"`` and
#: leave ``sign_verdicts`` as ``None``.
DEFAULT_SCHEMA_VERSION: Final[str] = "v1.0"

#: SAAS-COHORT-CLOSE Phase 4 — v1.1 emission tag for writers that
#: populate the new ``sign_verdicts`` field. Backward-compat invariant:
#: a v1.1 file with ``sign_verdicts`` omitted is indistinguishable from
#: a v1.0 file at the byte level (additive semantics).
SCHEMA_VERSION_V1_1: Final[str] = "v1.1"

#: Spec §9 pinned percentile grid for monthly $/mo CDF.
DEFAULT_CDF_PERCENTILES: Final[tuple[float, float, float, float]] = (
    10.0,
    50.0,
    90.0,
    99.0,
)


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PosteriorDraws:
    """Posterior-draws container for Stage-2 cohort calibration.

    Holds a 2-D numpy array of shape ``(n_chains * n_draws, n_params)`` plus
    the ordered parameter-name metadata that disambiguates columns. Per spec
    §8(8) the Stage-2 PyMC fits use ≥ 4000 draws across ≥ 4 chains; this Value
    container is the canonical hand-off shape from the sampler Callable
    (``simulations.modules``) to the analysis Callables.

    Validation contract:

    - ``draws.ndim == 2``;
    - ``draws.shape[1] == len(param_names)``;
    - ``len(param_names)`` ≥ 1;
    - ``param_names`` has no duplicates;
    - ``draws.shape[0]`` ≥ 1.

    Note:
        The numpy array is held by reference. Frozen-dc immutability does
        not prevent in-place mutation of array contents — callers MUST treat
        the array as read-only. Future hardening could ``draws.flags.writeable
        = False`` at construction time, but doing so cross-tier-couples to
        numpy semantics; the contract is documentary for now.
    """

    draws: NDArray[np.float64]
    param_names: tuple[str, ...]
    schema_version: str = DEFAULT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.draws.ndim != 2:
            raise ValueError(
                f"PosteriorDraws.draws.ndim = {self.draws.ndim} must be 2"
            )
        n_rows, n_cols = self.draws.shape
        if n_rows < 1:
            raise ValueError(
                f"PosteriorDraws.draws must have ≥ 1 row (got {n_rows})"
            )
        if len(self.param_names) < 1:
            raise ValueError("PosteriorDraws.param_names must be non-empty")
        if n_cols != len(self.param_names):
            raise ValueError(
                f"PosteriorDraws.draws.shape[1] = {n_cols} must equal"
                f" len(param_names) = {len(self.param_names)}"
            )
        if len(set(self.param_names)) != len(self.param_names):
            raise ValueError(
                f"PosteriorDraws.param_names contains duplicates: {self.param_names}"
            )


@dataclass(frozen=True)
class MonthlyCDF:
    """Pinned-percentile monthly $/mo CDF (spec §9 TODO-COHORT-1).

    Stores the posterior-predictive monthly cost CDF at the spec-pinned
    percentile grid (default p10 / p50 / p90 / p99). Per spec §9 the
    cohort-1 verdict gate compares these percentiles to the §5.2 brackets.

    Symbol map:

    - ``percentiles`` ↔ percentile grid (e.g. (10, 50, 90, 99));
    - ``values_usd`` ↔ posterior-predictive monthly cost in USD at each
      percentile (parallel to ``percentiles``);
    - ``currency`` ↔ ISO-4217 code; ``"USD"`` or ``"COP"``.

    Validation contract:

    - ``len(percentiles) == len(values_usd)`` and both ≥ 1;
    - ``percentiles`` strictly increasing in ``(0, 100)``;
    - ``values_usd`` non-decreasing and non-negative;
    - ``currency`` is one of ``("USD", "COP")``.
    """

    percentiles: tuple[float, ...]
    values_usd: tuple[float, ...]
    currency: str = "USD"

    def __post_init__(self) -> None:
        if len(self.percentiles) != len(self.values_usd):
            raise ValueError(
                f"MonthlyCDF: percentiles ({len(self.percentiles)}) and"
                f" values_usd ({len(self.values_usd)}) must have equal length"
            )
        if len(self.percentiles) < 1:
            raise ValueError("MonthlyCDF.percentiles must be non-empty")
        for i, q in enumerate(self.percentiles):
            if not (0.0 < q < 100.0):
                raise ValueError(
                    f"MonthlyCDF.percentiles[{i}] = {q} must lie in (0, 100)"
                )
            if i > 0 and not (q > self.percentiles[i - 1]):
                raise ValueError(
                    "MonthlyCDF.percentiles must be strictly increasing"
                    f" (got {self.percentiles!r})"
                )
        for i, v in enumerate(self.values_usd):
            if v < 0.0:
                raise ValueError(
                    f"MonthlyCDF.values_usd[{i}] = {v} must be ≥ 0"
                )
            if i > 0 and v < self.values_usd[i - 1]:
                raise ValueError(
                    "MonthlyCDF.values_usd must be non-decreasing"
                    f" (got {self.values_usd!r})"
                )
        if self.currency not in ("USD", "COP"):
            raise ValueError(
                f"MonthlyCDF.currency = {self.currency!r} must be 'USD' or 'COP'"
            )


#: SAAS-COHORT-CLOSE Phase 4 — closed alphabet for per-TP sign-verdict
#: labels (mirrors ``simulations.saas_builder.cohort_4.types.TestPointLabel``
#: but without re-importing across the cohort_4 boundary into the
#: schema-Value tier).
SignVerdictLabel = Literal["TP1", "TP2", "TP3", "TP4", "TP5"]


@dataclass(frozen=True)
class SignVerdictEntry:
    """One per-test-point sign-verdict record (schema v1.1 ``ZCapPinned`` field).

    SAAS-COHORT-CLOSE Phase 4 — additive schema bump v1.0 → v1.1.

    Carries the per-TP outputs that v1.0 published as a sidecar
    ``Z_cap_pinned.SIGN_VERDICTS.md`` Markdown table. Now first-class
    on ``ZCapPinned`` so consumers can audit per-TP sign-pass status
    without parsing Markdown.

    Validation contract:

    - ``label`` ∈ ``("TP1","TP2","TP3","TP4","TP5")``;
    - ``z`` finite (NOT required > 0 — pre-HALT verdicts may record
      sign violations for the disposition memo);
    - ``ci_95_lo ≤ z ≤ ci_95_hi``; both finite;
    - ``sign`` ∈ ``("PASS","FAIL")``; consistent with ``ci_95_lo > 0``
      (PASS iff lo > 0, else FAIL);
    - ``identity_residual`` finite, ≥ 0;
    - ``identity_passes`` is the boolean form of the pass/fail flag.
    """

    label: SignVerdictLabel
    z: float
    ci_95_lo: float
    ci_95_hi: float
    sign: Literal["PASS", "FAIL"]
    identity_residual: float
    identity_passes: bool

    def __post_init__(self) -> None:
        if self.label not in ("TP1", "TP2", "TP3", "TP4", "TP5"):
            raise ValueError(
                f"SignVerdictEntry.label = {self.label!r} must be TP1..TP5"
            )
        for name, val in (
            ("z", self.z),
            ("ci_95_lo", self.ci_95_lo),
            ("ci_95_hi", self.ci_95_hi),
            ("identity_residual", self.identity_residual),
        ):
            if not math.isfinite(val):
                raise ValueError(
                    f"SignVerdictEntry.{name} = {val} must be finite"
                )
        if not (self.ci_95_lo <= self.z <= self.ci_95_hi):
            raise ValueError(
                "SignVerdictEntry: must satisfy ci_95_lo ≤ z ≤ ci_95_hi;"
                f" got ({self.ci_95_lo}, {self.z}, {self.ci_95_hi})"
            )
        if self.sign not in ("PASS", "FAIL"):
            raise ValueError(
                f"SignVerdictEntry.sign = {self.sign!r} must be 'PASS' or 'FAIL'"
            )
        derived_pass = self.ci_95_lo > 0.0
        if derived_pass != (self.sign == "PASS"):
            raise ValueError(
                "SignVerdictEntry.sign must equal 'PASS' iff ci_95_lo > 0;"
                f" got sign={self.sign!r}, ci_95_lo={self.ci_95_lo}"
            )
        if self.identity_residual < 0.0:
            raise ValueError(
                f"SignVerdictEntry.identity_residual = {self.identity_residual}"
                " must be ≥ 0"
            )


@dataclass(frozen=True)
class ZCapPinned:
    """Pinned Z-cap emission Value for ``estimates/Z_cap_pinned.json`` (spec §10).

    Math pin M4 column-set (spec §10 + Phase 2 prelude):

    - ``Z_cop_per_month`` — posterior-predictive mean of monthly cap (COP);
    - ``ci_95_lo`` / ``ci_95_hi`` — 95% credible interval bounds;
    - ``audit_block`` — sha256 audit-block string (input-data lineage pin);
    - ``tier_mix`` — Mapping[TierID, float] of posterior tier mass;
    - ``schema_version`` — additive-only schema evolution tag (Phase 1
      reconciliation §2.4); default ``"v1.0"``.

    Validation contract:

    - ``Z_cop_per_month > 0``;
    - ``ci_95_lo ≤ Z_cop_per_month ≤ ci_95_hi`` and ``ci_95_lo > 0``;
    - ``audit_block`` is a 64-character lowercase hex string (sha256);
    - ``tier_mix`` keys are exactly ``TIER_IDS``; values in ``(0, 1]``
      summing to 1 within ``1e-9``;
    - ``schema_version`` is non-empty.

    NOTE (pre-mortem #6, scratch/2026-05-08-sim-infra-audit/): the
    sum-to-one tolerance ``1e-9`` is calibrated for the closed 3-tier
    set ``TIER_IDS``. A future expansion to O(100) tiers would
    accumulate float64 summation rounding above this threshold and
    require a tolerance scaling with ``len(tier_mix)``.
    """

    Z_cop_per_month: float
    ci_95_lo: float
    ci_95_hi: float
    audit_block: str
    tier_mix: Mapping[TierID, float] = field(
        default_factory=lambda: {"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30}
    )
    schema_version: str = DEFAULT_SCHEMA_VERSION
    #: SAAS-COHORT-CLOSE Phase 4 — schema v1.1 additive field. ``None``
    #: under v1.0 (sidecar-only emission); a 5-tuple under v1.1 (one
    #: ``SignVerdictEntry`` per test point TP1..TP5). Backward-compat
    #: invariant: v1.0 readers see ``None`` (field absent on disk);
    #: v1.1 readers materialise the tuple. The field is intentionally
    #: ``Optional`` rather than required so v1.0 callers continue to
    #: construct ``ZCapPinned`` with the original 5-arg signature.
    sign_verdicts: tuple[SignVerdictEntry, ...] | None = None

    def __post_init__(self) -> None:
        if not _is_finite_positive(self.Z_cop_per_month):
            raise ValueError(
                f"ZCapPinned.Z_cop_per_month = {self.Z_cop_per_month}"
                f" must be a finite float > 0"
            )
        if not _is_finite_positive(self.ci_95_lo):
            raise ValueError(
                f"ZCapPinned.ci_95_lo = {self.ci_95_lo} must be a finite float > 0"
            )
        if not _is_finite_positive(self.ci_95_hi):
            raise ValueError(
                f"ZCapPinned.ci_95_hi = {self.ci_95_hi} must be a finite float > 0"
            )
        if not (self.ci_95_lo <= self.Z_cop_per_month <= self.ci_95_hi):
            raise ValueError(
                f"ZCapPinned: must have ci_95_lo ({self.ci_95_lo})"
                f" ≤ Z_cop_per_month ({self.Z_cop_per_month})"
                f" ≤ ci_95_hi ({self.ci_95_hi})"
            )
        if not _AUDIT_BLOCK_RE.fullmatch(self.audit_block):
            raise ValueError(
                f"ZCapPinned.audit_block must be exactly 64 lowercase hex chars;"
                f" got {self.audit_block!r} (len={len(self.audit_block)})"
            )
        if not isinstance(self.tier_mix, MappingABC):
            raise TypeError(
                f"ZCapPinned.tier_mix must be a Mapping"
                f" (got {type(self.tier_mix).__name__})"
            )
        if set(self.tier_mix.keys()) != set(TIER_IDS):
            raise ValueError(
                f"ZCapPinned.tier_mix keys must be exactly {set(TIER_IDS)};"
                f" got {set(self.tier_mix.keys())}"
            )
        for k, v in self.tier_mix.items():
            if not (0.0 < v <= 1.0):
                raise ValueError(
                    f"ZCapPinned.tier_mix[{k!r}] = {v} must lie in (0, 1]"
                )
        total = sum(self.tier_mix.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"ZCapPinned.tier_mix must sum to 1 (got {total!r})"
            )
        if not self.schema_version:
            raise ValueError("ZCapPinned.schema_version must be non-empty")
        # SAAS-COHORT-CLOSE Phase 4 — sign_verdicts (v1.1) validation.
        #
        # Backward-compat invariant: ``None`` (the v1.0 default) is
        # always admissible regardless of ``schema_version``. When
        # populated, the tuple must contain exactly 5 entries, one
        # per TP1..TP5, with no duplicate labels.
        if self.sign_verdicts is not None:
            if not isinstance(self.sign_verdicts, tuple):
                raise TypeError(
                    f"ZCapPinned.sign_verdicts must be a tuple"
                    f" (got {type(self.sign_verdicts).__name__})"
                )
            if len(self.sign_verdicts) != 5:
                raise ValueError(
                    "ZCapPinned.sign_verdicts must have exactly 5 entries"
                    f" (one per TP1..TP5); got {len(self.sign_verdicts)}"
                )
            labels = tuple(sv.label for sv in self.sign_verdicts)
            if set(labels) != {"TP1", "TP2", "TP3", "TP4", "TP5"}:
                raise ValueError(
                    "ZCapPinned.sign_verdicts labels must be exactly"
                    f" {{TP1..TP5}}; got {sorted(labels)}"
                )
            if len(set(labels)) != len(labels):
                raise ValueError(
                    f"ZCapPinned.sign_verdicts contains duplicate labels: {labels}"
                )


# ─── Free-function accessors ──────────────────────────────────────────────────


def n_total_draws(draws: PosteriorDraws) -> int:
    """Return the total number of posterior draws (rows)."""
    return int(draws.draws.shape[0])


def parameter_index(draws: PosteriorDraws, name: str) -> int:
    """Return the column index of a named parameter in ``draws.draws``.

    Contract:
        Preconditions:
            - ``name`` must be present in ``draws.param_names``.

        Raises:
            ValueError: re-raised with a descriptive message listing the
                available parameter names if ``name`` is not found
                (explicit; chains the underlying ``tuple.index`` error
                via ``from exc``).
    """
    try:
        return draws.param_names.index(name)
    except ValueError as exc:
        raise ValueError(
            f"PosteriorDraws has no parameter named {name!r};"
            f" available: {draws.param_names}"
        ) from exc


def cdf_percentile_value(cdf: MonthlyCDF, percentile: float) -> float:
    """Return the value at a pinned percentile, or raise if not pinned.

    Contract:
        Preconditions:
            - ``percentile`` must appear in ``cdf.percentiles`` (exact
              float equality — no tolerance applied).

        Raises:
            ValueError: re-raised with the available percentile grid in
                the message if ``percentile`` is not pinned
                (explicit; chains via ``from exc``).
    """
    try:
        idx = cdf.percentiles.index(percentile)
    except ValueError as exc:
        raise ValueError(
            f"MonthlyCDF has no pinned percentile {percentile!r};"
            f" available: {cdf.percentiles}"
        ) from exc
    return cdf.values_usd[idx]


def ci_95_width(z: ZCapPinned) -> float:
    """Return the 95% CI width ``ci_95_hi - ci_95_lo``."""
    return z.ci_95_hi - z.ci_95_lo
