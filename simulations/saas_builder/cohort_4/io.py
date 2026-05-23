r"""IO Boundary tier for SAAS-COHORT-4 — Z-cap pin emission + sidecar.

Per the functional-python skill: this is the ONLY tier where mutable
state and external IO live. All classes have ``__init__`` (not frozen-dc).

Pin coverage:

- Pin M3 — ``ZCapPinnedWriter`` (shipped in ``simulations/utils/json_io.py``)
  is wrapped by ``pin_and_emit`` to write ``Z_cap_pinned.json``.
- Pin M3 sidecar — ``SignVerdictSidecarWriter`` writes
  ``Z_cap_pinned.SIGN_VERDICTS.md`` per plan v0.2.
- Pin M4 — ``compute_audit_block`` (shipped in
  ``simulations/utils/audit_block.py``) is invoked over the canonical
  5-file input list.
- Round-trip — ``pin_and_emit`` reads the just-written JSON via
  ``ZCapPinnedReader`` and asserts field-by-field equality (defense-in-
  depth against silent file-system drift).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Final

import numpy as np
from numpy.typing import NDArray

from simulations.saas_builder.cohort_4._errors import (
    AuditBlockDriftError,
    DiagnosticGateError,
    RoundTripDriftError,
)
from simulations.saas_builder.cohort_4.pi_derivation import (
    derive_pi_t_symbolic,
)
from simulations.saas_builder.cohort_4.sign_cert import (
    SignVerdictMarkdownRenderer,
)
from simulations.saas_builder.cohort_4.types import (
    SignVerdict,
    TestPoint,
    ZEvaluationResult,
)
from simulations.saas_builder.cohort_4.z_cap import ZCapRunner
from simulations.types.posterior import (
    SCHEMA_VERSION_V1_1,
    SignVerdictEntry,
    ZCapPinned,
)
from simulations.types.tier import TIER_IDS, TierID
from simulations.utils.audit_block import compute_audit_block
from simulations.utils.json_io import ZCapPinnedReader, ZCapPinnedWriter

#: Plan v0.2 Pin M4 — relative paths of the 5 audit-block input files.
DEFAULT_AUDIT_INPUT_RELATIVE_PATHS: Final[tuple[str, ...]] = (
    "simulations/saas_builder/data/synthetic_tau_t",
    "simulations/saas_builder/data/cohort_prior.parquet",
    "notebooks/saas_builder_stage_2/estimates/ROBUSTNESS_RESULTS.md",
    "notebooks/saas_builder_stage_2/estimates/PRIMARY_RESULTS.md",
    "docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md",
)

#: Default emission directory for the Z-cap pin + sidecar.
DEFAULT_EMIT_DIR: Final[Path] = Path("simulations/saas_builder/data")

#: Default tier-mix per spec §5.2 + plan v0.2 Pin M3.
DEFAULT_TIER_MIX: Final[Mapping[TierID, float]] = {
    "pro": 0.20,
    "max_5x": 0.50,
    "max_20x": 0.30,
}


# ─── Audit-block resolver (IO Boundary) ──────────────────────────────────────


class AuditBlockResolver:
    """Compute the SHA-256 audit block over the Pin M4 5-file input list.

    Resolution rules (plan v0.2 Pin M4):

    - All paths canonicalized via ``Path.resolve()`` BEFORE hashing
      (compute_audit_block embeds path string in the digest).
    - Missing files raise ``FileNotFoundError`` (the desired upstream-
      dependency enforcement; HALT routing upstream).
    - For directories (e.g., the Hive-partitioned ``synthetic_tau_t``),
      the resolver enumerates child files in lex order and hashes each.
    """

    def __init__(
        self,
        repo_root: str | Path | None = None,
        input_paths: Sequence[str | Path] | None = None,
    ) -> None:
        self._repo_root = (
            Path(repo_root).resolve()
            if repo_root is not None
            else Path.cwd().resolve()
        )
        if input_paths is None:
            input_paths = DEFAULT_AUDIT_INPUT_RELATIVE_PATHS
        self._input_paths: tuple[Path, ...] = tuple(
            (self._repo_root / Path(p)).resolve() for p in input_paths
        )

    @property
    def input_paths(self) -> tuple[Path, ...]:
        return self._input_paths

    def __call__(self) -> str:
        """Return the 64-char lowercase hex SHA-256 audit block."""
        # Expand any directories to their constituent files (lex-sorted).
        expanded: list[Path] = []
        for p in self._input_paths:
            if p.is_dir():
                # Recursively enumerate; sorted for deterministic ordering.
                for child in sorted(p.rglob("*")):
                    if child.is_file():
                        expanded.append(child.resolve())
            elif p.is_file():
                expanded.append(p)
            else:
                raise FileNotFoundError(
                    f"AuditBlockResolver: missing audit-block input path: {p}"
                )
        if not expanded:
            raise FileNotFoundError(
                "AuditBlockResolver: empty file list after directory expansion"
            )
        return compute_audit_block(expanded)


# ─── Sidecar writer (IO Boundary) ────────────────────────────────────────────


class SignVerdictSidecarWriter:
    """Write the per-TP sign verdicts to ``Z_cap_pinned.SIGN_VERDICTS.md``.

    Plan v0.2 Pin M3 sidecar — emitted alongside ``Z_cap_pinned.json`` so
    consumers can audit per-TP sign-pass status without a schema bump on
    ``ZCapPinned``.
    """

    def __init__(self, emit_dir: str | Path | None = None) -> None:
        self.emit_dir = (
            Path(emit_dir) if emit_dir is not None else DEFAULT_EMIT_DIR
        )
        self._renderer = SignVerdictMarkdownRenderer()

    @property
    def sidecar_path(self) -> Path:
        return self.emit_dir / "Z_cap_pinned.SIGN_VERDICTS.md"

    def __call__(
        self,
        sign_verdicts: Sequence[SignVerdict],
        test_points: Sequence[TestPoint],
        monotonicity_triple: tuple[float, float, float],
        audit_block: str,
    ) -> Path:
        """Render + write the sidecar; return the on-disk path."""
        body = self._renderer(
            sign_verdicts, test_points, monotonicity_triple, audit_block
        )
        self.emit_dir.mkdir(parents=True, exist_ok=True)
        path = self.sidecar_path
        path.write_text(body, encoding="utf-8")
        return path


# ─── Top-level pin-and-emit orchestrator (IO Boundary) ───────────────────────


def _to_sign_verdict_entry(sv: SignVerdict) -> SignVerdictEntry:
    """Convert cohort_4 SignVerdict (Value) → posterior SignVerdictEntry (schema).

    SAAS-COHORT-CLOSE Phase 4 — bridge from the cohort_4 internal
    Value type to the schema-Value emitted on ``ZCapPinned`` v1.1.
    The two types carry identical information; the duplication keeps
    the schema-tier (``simulations.types.posterior``) free of cohort_4
    imports per the tier-import discipline (CLAUDE.md).
    """
    return SignVerdictEntry(
        label=sv.label,
        z=sv.z_value,
        ci_95_lo=sv.ci_95_lo,
        ci_95_hi=sv.ci_95_hi,
        sign="PASS" if sv.passes else "FAIL",
        identity_residual=sv.identity_residual,
        identity_passes=sv.identity_passes,
    )


def _build_z_cap_pinned(
    results: Sequence[ZEvaluationResult],
    audit_block: str,
    tier_mix: Mapping[TierID, float] = DEFAULT_TIER_MIX,
    sign_verdicts: Sequence[SignVerdict] | None = None,
) -> ZCapPinned:
    """Build the ``ZCapPinned`` Value from the per-TP results.

    Aggregation: the headline ``Z_cop_per_month`` is the TP1 (primary
    bracket) posterior-predictive mean; the 95% CI is TP1's per-draw
    percentile pair. This matches the spec §5.2 LOCKED brackets pin —
    other TPs are sign-certification straddles, not the cap-of-record.

    SAAS-COHORT-CLOSE Phase 4 — when ``sign_verdicts`` is supplied, the
    returned ``ZCapPinned`` carries schema v1.1 with the per-TP entries
    populated; otherwise the v1.0 default (None / sidecar-only) is
    preserved.

    Validation: TP1 ``ci_95_lo`` MUST be > 0 (else the upstream sign
    gate would have already raised). The frozen-dc ``__post_init__``
    re-asserts ordering invariants.
    """
    by_label = {r.label: r for r in results}
    if "TP1" not in by_label:
        raise DiagnosticGateError(
            "_build_z_cap_pinned: TP1 missing from results;"
            " plan v0.2 §M2 requires TP1 as the primary cap-of-record"
        )
    tp1 = by_label["TP1"]
    sv_field: tuple[SignVerdictEntry, ...] | None
    schema_version: str
    if sign_verdicts is None:
        sv_field = None
        # v1.0 default flows from ZCapPinned default; explicit for clarity.
        return ZCapPinned(
            Z_cop_per_month=tp1.z_mean,
            ci_95_lo=tp1.ci_95_lo,
            ci_95_hi=tp1.ci_95_hi,
            audit_block=audit_block,
            tier_mix=tier_mix,
        )
    sv_field = tuple(_to_sign_verdict_entry(sv) for sv in sign_verdicts)
    schema_version = SCHEMA_VERSION_V1_1
    return ZCapPinned(
        Z_cop_per_month=tp1.z_mean,
        ci_95_lo=tp1.ci_95_lo,
        ci_95_hi=tp1.ci_95_hi,
        audit_block=audit_block,
        tier_mix=tier_mix,
        schema_version=schema_version,
        sign_verdicts=sv_field,
    )


def pin_and_emit(
    q_t_cop_draws: NDArray[np.float64],
    test_points: Sequence[TestPoint],
    repo_root: str | Path | None = None,
    audit_input_paths: Sequence[str | Path] | None = None,
    emit_dir: str | Path | None = None,
    runner: ZCapRunner | None = None,
    tier_mix: Mapping[TierID, float] = DEFAULT_TIER_MIX,
) -> tuple[Path, Path, ZCapPinned, tuple[SignVerdict, ...]]:
    """Run the full cohort-4 pipeline + emit Z_cap_pinned.json + sidecar.

    Pipeline:

    1. Derive symbolic π(t) via ``derive_pi_t_symbolic`` (Pin M1).
    2. Resolve audit-block sha256 over the 5-file Pin M4 set.
    3. Run ``ZCapRunner`` over the 5-TP grid + posterior draws (Pin M2 +
       Pin M2-fix MC budget). Sign / identity / monotonicity HALT routes
       through cohort-4 errors.
    4. Build ``ZCapPinned`` Value from TP1 (cap-of-record).
    5. Write ``Z_cap_pinned.json`` via ``ZCapPinnedWriter``.
    6. Round-trip-verify by reading back via ``ZCapPinnedReader`` and
       asserting field equality (RuntimeError on drift).
    7. Write ``Z_cap_pinned.SIGN_VERDICTS.md`` sidecar.

    Returns:
        Tuple ``(json_path, sidecar_path, z_cap_value, sign_verdicts)``.

    Raises:
        FileNotFoundError: missing audit-block input files (Pin M4
            enforcement).
        DiagnosticGateError / IdentityToleranceError /
            MCErrorBudgetExceededError: from ``ZCapRunner`` (HALT routing).
        RuntimeError: JSON round-trip equality breach.
    """
    if runner is None:
        runner = ZCapRunner()

    # Step 1 — π(t) symbolic.
    pi_t = derive_pi_t_symbolic()

    # Step 2 — audit block.
    resolver = AuditBlockResolver(
        repo_root=repo_root, input_paths=audit_input_paths
    )
    audit_block = resolver()

    # Step 3 — runner (Pin M2 + Pin M2-fix gates).
    results, sign_verdicts, monotonicity_triple = runner(
        pi_t, test_points, q_t_cop_draws
    )

    # Step 4 — build ZCapPinned (TP1 = cap-of-record).
    # SAAS-COHORT-CLOSE Phase 4: pass sign_verdicts so the emitted
    # ZCapPinned carries schema v1.1 with per-TP entries populated.
    z_cap = _build_z_cap_pinned(
        results,
        audit_block=audit_block,
        tier_mix=tier_mix,
        sign_verdicts=sign_verdicts,
    )

    # Step 5 — write JSON.
    target_dir = Path(emit_dir) if emit_dir is not None else DEFAULT_EMIT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    json_path = target_dir / "Z_cap_pinned.json"
    ZCapPinnedWriter()(z_cap, json_path)

    # Step 6 — round-trip verify (defense-in-depth against fs drift).
    roundtripped = ZCapPinnedReader()(json_path)
    if not z_cap_pinned_equal(roundtripped, z_cap):
        raise RoundTripDriftError(
            f"pin_and_emit: round-trip equality breach at {json_path}"
            f" — wrote {z_cap!r}, read back {roundtripped!r}"
        )

    # Step 7 — sidecar.
    sidecar_writer = SignVerdictSidecarWriter(emit_dir=target_dir)
    sidecar_path = sidecar_writer(
        sign_verdicts, test_points, monotonicity_triple, audit_block
    )

    return json_path, sidecar_path, z_cap, sign_verdicts


def z_cap_pinned_equal(a: ZCapPinned, b: ZCapPinned) -> bool:
    """Field-by-field equality predicate for round-trip verification.

    Promoted from the prior leading-underscore-private
    ``_z_cap_pinned_equal`` (CR NIT-2 v0.3 sweep) — the function is
    imported by the cohort-4 test suite and must therefore live on
    the public surface of ``simulations.saas_builder.cohort_4.io``.
    """
    if a.audit_block != b.audit_block:
        return False
    if a.schema_version != b.schema_version:
        return False
    for fa, fb in (
        (a.Z_cop_per_month, b.Z_cop_per_month),
        (a.ci_95_lo, b.ci_95_lo),
        (a.ci_95_hi, b.ci_95_hi),
    ):
        if not (abs(fa - fb) <= 1e-12 * max(1.0, abs(fa))):
            return False
    if set(a.tier_mix.keys()) != set(b.tier_mix.keys()):
        return False
    for k in a.tier_mix:
        if abs(a.tier_mix[k] - b.tier_mix[k]) > 1e-12:
            return False
    # SAAS-COHORT-CLOSE Phase 4 — schema v1.1 sign_verdicts comparison.
    # Both None (v1.0) is equal; mixed None / not-None is unequal;
    # both populated requires per-entry field-by-field equality (with
    # float tolerance on the numeric fields, exact match on labels /
    # sign / identity_passes).
    if (a.sign_verdicts is None) != (b.sign_verdicts is None):
        return False
    if a.sign_verdicts is not None and b.sign_verdicts is not None:
        if len(a.sign_verdicts) != len(b.sign_verdicts):
            return False
        # Compare sorted-by-label so insertion-order drift does not break
        # equality (the dataclass labels are a closed alphabet — set
        # equality on labels is enforced upstream by __post_init__).
        a_by_label = {sv.label: sv for sv in a.sign_verdicts}
        b_by_label = {sv.label: sv for sv in b.sign_verdicts}
        if set(a_by_label.keys()) != set(b_by_label.keys()):
            return False
        for label, sva in a_by_label.items():
            svb = b_by_label[label]
            if sva.sign != svb.sign:
                return False
            if sva.identity_passes != svb.identity_passes:
                return False
            for fa, fb in (
                (sva.z, svb.z),
                (sva.ci_95_lo, svb.ci_95_lo),
                (sva.ci_95_hi, svb.ci_95_hi),
                (sva.identity_residual, svb.identity_residual),
            ):
                if not (abs(fa - fb) <= 1e-12 * max(1.0, abs(fa))):
                    return False
    return True


def assert_audit_block_unchanged(
    expected_sha: str,
    repo_root: str | Path | None = None,
    input_paths: Sequence[str | Path] | None = None,
) -> None:
    """Re-resolve the audit block and HALT on drift (Pin M4 post-PASS guard).

    Raises ``AuditBlockDriftError`` if the recomputed digest differs from
    ``expected_sha``. Used by the user to verify deterministic re-runs.
    """
    resolver = AuditBlockResolver(
        repo_root=repo_root, input_paths=input_paths
    )
    actual = resolver()
    if actual != expected_sha:
        raise AuditBlockDriftError(
            f"Pin M4 audit-block drift: expected {expected_sha!r},"
            f" got {actual!r}"
        )


# ─── Helper: dataclasses.replace surface for tier-mix overrides ──────────────


def with_tier_mix(z: ZCapPinned, tier_mix: Mapping[TierID, float]) -> ZCapPinned:
    """Return a frozen-dc replace of ``z`` with a new tier-mix.

    Validates the new tier-mix via ``ZCapPinned.__post_init__`` indirectly
    through ``dataclasses.replace``. Intended for downstream cohort-4
    consumers wanting to substitute the spec §5.2 default with a posterior-
    fit tier-mix without touching ``Z_cop_per_month`` / CI fields.
    """
    if set(tier_mix.keys()) != set(TIER_IDS):
        raise ValueError(
            f"with_tier_mix: tier_mix keys must be exactly {set(TIER_IDS)};"
            f" got {set(tier_mix.keys())}"
        )
    return replace(z, tier_mix=tier_mix)


#: Backwards-compatible alias for the prior private name. New callers
#: should import :func:`z_cap_pinned_equal` directly (CR NIT-2 v0.3
#: sweep promoted the symbol to the public surface).
_z_cap_pinned_equal = z_cap_pinned_equal


__all__ = [
    "AuditBlockResolver",
    "DEFAULT_AUDIT_INPUT_RELATIVE_PATHS",
    "DEFAULT_EMIT_DIR",
    "DEFAULT_TIER_MIX",
    "SignVerdictSidecarWriter",
    "assert_audit_block_unchanged",
    "pin_and_emit",
    "with_tier_mix",
    "z_cap_pinned_equal",
]
