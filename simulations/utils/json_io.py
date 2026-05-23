"""JSON IO boundaries for the M4 ``Z_cap_pinned.json`` schema (spec §10).

Per Phase 1 reconciliation §2.2, **Pydantic appears ONLY here**. The
private ``_ZCapPinnedJsonModel`` is a *transient* validation container:
it is constructed by ``model_validate_json`` on read, immediately
converted to the frozen-dc ``ZCapPinned`` Value, and then discarded. It
is never returned to consumers and never exported.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal, cast

from pydantic import BaseModel, ConfigDict, Field

from simulations.types.posterior import (
    DEFAULT_SCHEMA_VERSION,
    SignVerdictEntry,
    SignVerdictLabel,
    ZCapPinned,
)
from simulations.types.saas_cohort1_audit import Audit, AuditVerdict
from simulations.types.tier import TIER_IDS, TierID
from simulations.utils.errors import SchemaMismatchError

#: M4 ``Z_cap_pinned.json`` REQUIRED field set (schema v1.0 + v1.1).
#:
#: Both schemas require these fields. SAAS-COHORT-CLOSE Phase 4 added
#: ``sign_verdicts`` as an OPTIONAL field for v1.1; see
#: ``Z_CAP_PINNED_OPTIONAL_FIELDS`` below.
Z_CAP_PINNED_FIELDS: Final[tuple[str, ...]] = (
    "Z_cop_per_month",
    "ci_95_lo",
    "ci_95_hi",
    "audit_block",
    "tier_mix",
    "schema_version",
)

#: SAAS-COHORT-CLOSE Phase 4 — schema v1.1 additive optional fields.
#:
#: A field-set check that allows ANY of these as extras (but no others)
#: keeps both v1.0 (none present) and v1.1 (``sign_verdicts`` present)
#: readable by the same reader. Adding a new optional field for a
#: future v1.2 bump amounts to extending this tuple.
Z_CAP_PINNED_OPTIONAL_FIELDS: Final[tuple[str, ...]] = ("sign_verdicts",)


class _SignVerdictEntryJsonModel(BaseModel):
    """Transient Pydantic validator for one ``sign_verdicts`` entry (private).

    SAAS-COHORT-CLOSE Phase 4 — schema v1.1 additive type. Mirrors
    ``simulations.types.posterior.SignVerdictEntry`` exactly; the
    reader converts each instance to the frozen-dc Value before
    surfacing the result to consumers.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    label: str
    z: float
    ci_95_lo: float
    ci_95_hi: float
    sign: str
    identity_residual: float
    identity_passes: bool


class _ZCapPinnedJsonModel(BaseModel):
    """Transient Pydantic validator for ``Z_cap_pinned.json`` (private).

    Not exported; never returned to consumers. Constructed by the JSON
    reader, converted to ``ZCapPinned`` (frozen-dc Value), then discarded
    per Phase 1 reconciliation §2.2.

    SAAS-COHORT-CLOSE Phase 4 — accepts BOTH schema v1.0 (no
    ``sign_verdicts``) AND v1.1 (``sign_verdicts`` is a 5-list of
    ``_SignVerdictEntryJsonModel``). v1.0 readers continue to work
    unchanged because the field defaults to ``None``.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    Z_cop_per_month: float
    ci_95_lo: float
    ci_95_hi: float
    audit_block: str = Field(min_length=64, max_length=64)
    tier_mix: dict[str, float]
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, min_length=1)
    sign_verdicts: list[_SignVerdictEntryJsonModel] | None = None


def _coerce_tier_mix(raw: Mapping[str, float]) -> dict[TierID, float]:
    """Narrow string keys back into the ``TierID`` Literal set; raise on drift."""
    admissible = set(TIER_IDS)
    keys = set(raw.keys())
    if keys != admissible:
        raise SchemaMismatchError(
            f"Z_cap_pinned.json: tier_mix keys must be exactly {admissible};"
            f" got {keys}"
        )
    # ``raw`` keys are str-typed at the JSON layer; we have just verified
    # set-equality with the TierID literal set, so the cast is safe.
    return cast(
        "dict[TierID, float]",
        {k: float(v) for k, v in raw.items()},
    )


class ZCapPinnedReader:
    """Read ``Z_cap_pinned.json`` (M4); return a ``ZCapPinned`` Value."""

    def __init__(self) -> None:
        pass

    def __call__(self, path: str | Path) -> ZCapPinned:
        """Read JSON at ``path`` and return a validated ``ZCapPinned`` Value.

        Contract:
            Preconditions:
                - File at ``path`` must exist (explicit
                  ``FileNotFoundError``).
                - File contents must parse as JSON (``json.JSONDecodeError``
                  propagates — NOT silenced).
                - Top-level value must be a JSON object (``SchemaMismatchError``
                  if list/scalar).
                - Field set must equal ``Z_CAP_PINNED_FIELDS``
                  (pre-Pydantic check; ``SchemaMismatchError``).
                - Field types/values must satisfy
                  ``_ZCapPinnedJsonModel`` constraints (``audit_block``
                  exactly 64 chars; Pydantic ``ValidationError`` propagates
                  on type drift).
                - ``tier_mix`` keys must equal ``set(TIER_IDS)``
                  (``SchemaMismatchError`` from ``_coerce_tier_mix``).
                - The constructed ``ZCapPinned`` must satisfy its own
                  ``__post_init__`` invariants (CI ordering, sum-to-one,
                  audit-block hex regex); ``ValueError`` propagates.

            Raises:
                FileNotFoundError: target JSON missing.
                SchemaMismatchError: top-level not object, field-set drift,
                    or tier_mix key drift.
                json.JSONDecodeError: malformed JSON.
                pydantic.ValidationError: per-field type/length violations.
                ValueError: ZCapPinned ``__post_init__`` rejection.
        """
        target = Path(path)
        if not target.is_file():
            raise FileNotFoundError(f"ZCapPinnedReader: missing JSON at {target}")
        raw_text = target.read_text(encoding="utf-8")
        # Pre-check the JSON's field set so consumers get a SchemaMismatchError
        # (rather than a Pydantic ValidationError) on column drift.
        parsed = json.loads(raw_text)
        if not isinstance(parsed, dict):
            raise SchemaMismatchError(
                f"Z_cap_pinned.json: top-level value must be an object;"
                f" got {type(parsed).__name__}"
            )
        actual = set(parsed.keys())
        required = set(Z_CAP_PINNED_FIELDS)
        optional = set(Z_CAP_PINNED_OPTIONAL_FIELDS)
        missing = required - actual
        # SAAS-COHORT-CLOSE Phase 4 — extras are unauthorized UNLESS they
        # appear in the optional-field set (schema v1.1 backward-compat).
        unauthorized_extra = actual - required - optional
        if missing or unauthorized_extra:
            raise SchemaMismatchError(
                f"Z_cap_pinned.json: field set mismatch."
                f" missing={sorted(missing)!r}"
                f" extra={sorted(unauthorized_extra)!r}"
            )
        validated = _ZCapPinnedJsonModel.model_validate_json(raw_text)
        # Convert transient Pydantic model → frozen-dc Value before returning.
        sign_verdicts: tuple[SignVerdictEntry, ...] | None
        if validated.sign_verdicts is None:
            sign_verdicts = None
        else:
            # SAAS-COHORT-CLOSE Phase 4 — v1.1 path: lift each transient
            # Pydantic entry into the frozen-dc Value.
            # SignVerdictEntry.__post_init__ rejects any out-of-alphabet
            # ``label`` / ``sign`` value, so the cast is provably safe at
            # the dataclass boundary; we cast here only to satisfy the
            # static checker (Pydantic returns ``str``, the frozen-dc
            # expects ``Literal``).
            sign_verdicts = tuple(
                SignVerdictEntry(
                    label=cast("SignVerdictLabel", sv.label),
                    z=sv.z,
                    ci_95_lo=sv.ci_95_lo,
                    ci_95_hi=sv.ci_95_hi,
                    sign=cast('Literal["PASS", "FAIL"]', sv.sign),
                    identity_residual=sv.identity_residual,
                    identity_passes=sv.identity_passes,
                )
                for sv in validated.sign_verdicts
            )
        return ZCapPinned(
            Z_cop_per_month=validated.Z_cop_per_month,
            ci_95_lo=validated.ci_95_lo,
            ci_95_hi=validated.ci_95_hi,
            audit_block=validated.audit_block,
            tier_mix=_coerce_tier_mix(validated.tier_mix),
            schema_version=validated.schema_version,
            sign_verdicts=sign_verdicts,
        )


class ZCapPinnedWriter:
    """Write a ``ZCapPinned`` Value to a JSON file (M4)."""

    def __init__(self) -> None:
        pass

    def __call__(self, z: ZCapPinned, path: str | Path) -> None:
        """Serialize ``z`` to JSON at ``path`` (parent dirs auto-created).

        The ``ZCapPinned`` Value is already validated by its frozen-dc
        ``__post_init__``, so this writer performs no additional
        validation — it relies on the type's invariants.

        Contract:
            Preconditions:
                - ``z`` must be a valid ``ZCapPinned`` (enforced upstream
                  by the dataclass; not re-checked here).
                - Parent directory of ``path`` must be creatable
                  (otherwise ``OSError`` from ``mkdir``).

            Raises:
                OSError: mkdir or write_text failure (disk full,
                    permission denied).
                TypeError: from ``json.dumps`` if ``tier_mix`` contains
                    non-JSON-serializable values (cannot occur given
                    ``ZCapPinned`` invariants — float values only).
        """
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {
            "Z_cop_per_month": z.Z_cop_per_month,
            "ci_95_lo": z.ci_95_lo,
            "ci_95_hi": z.ci_95_hi,
            "audit_block": z.audit_block,
            "tier_mix": dict(z.tier_mix),
            "schema_version": z.schema_version,
        }
        # SAAS-COHORT-CLOSE Phase 4 — schema v1.1 additive emission.
        # Only emit the field when populated; absence on disk is
        # indistinguishable from a v1.0 file (additive semantics).
        if z.sign_verdicts is not None:
            payload["sign_verdicts"] = [
                {
                    "label": sv.label,
                    "z": sv.z,
                    "ci_95_lo": sv.ci_95_lo,
                    "ci_95_hi": sv.ci_95_hi,
                    "sign": sv.sign,
                    "identity_residual": sv.identity_residual,
                    "identity_passes": sv.identity_passes,
                }
                for sv in z.sign_verdicts
            ]
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )


class _AuditVerdictJsonModel(BaseModel):
    """Pydantic transient validator for AuditVerdict block."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    rhat_max: float
    ess_bulk_min: float
    ess_tail_min: float
    divergence_frac: float
    ci_width_ratio_max: float
    n_chains: int
    n_draws_per_chain: int


class _AuditJsonModel(BaseModel):
    """Pydantic transient validator for `_AUDIT.json`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    audit_block: str
    schema_version: str
    synthetic_tau_path: str
    cohort_prior_path: str
    month: int
    n_rows_synthetic: int
    verdict: _AuditVerdictJsonModel


class AuditReader:
    """IO-Boundary reader for ``_AUDIT.json`` → ``Audit`` Value.

    Mirrors the ``ZCapPinnedReader`` pattern: validate via a private
    Pydantic model, then construct the frozen-dataclass Value. The
    Pydantic model is never re-exported.

    Note: unlike ``ZCapPinnedReader``, this reader does not perform a
    pre-Pydantic field-set check; field drift in ``_AUDIT.json`` is
    surfaced as ``pydantic.ValidationError`` rather than a domain
    ``SchemaMismatchError``. Consumers that need the domain-error
    framing can wrap the call.
    """

    def __init__(self) -> None:
        # Stateless beyond the boundary tier shape.
        pass

    def __call__(self, path: str | Path) -> Audit:
        """Read and validate ``_AUDIT.json`` at ``path``; return ``Audit`` Value.

        Contract
        --------
        Preconditions:
            - ``path`` resolves to an existing JSON file matching the
              ``_AUDIT.json`` schema (audit_block 64-char hex lowercase,
              schema_version non-empty, six gate-metric floats finite,
              R̂_max ≥ 1, divergence_frac ∈ [0, 1], ESS ≥ 0,
              ci_width_ratio_max > 0, n_chains/n_draws_per_chain > 0,
              month ∈ [1, 12], n_rows_synthetic ≥ 0).

        Raises:
            FileNotFoundError: if ``path`` does not point to an
                existing file.
            pydantic.ValidationError: on field-set drift or
                type-mismatch in the JSON payload.
            simulations.types.saas_cohort1_audit.AuditValueError:
                if values pass Pydantic but fail the frozen-dc Value
                invariants in ``Audit.__post_init__`` /
                ``AuditVerdict.__post_init__``.
        """
        target = Path(path)
        if not target.is_file():
            raise FileNotFoundError(f"AuditReader: missing JSON at {target}")
        raw = json.loads(target.read_text(encoding="utf-8"))
        model = _AuditJsonModel.model_validate(raw)
        return Audit(
            audit_block=model.audit_block,
            schema_version=model.schema_version,
            synthetic_tau_path=model.synthetic_tau_path,
            cohort_prior_path=model.cohort_prior_path,
            month=model.month,
            n_rows_synthetic=model.n_rows_synthetic,
            verdict=AuditVerdict(
                rhat_max=model.verdict.rhat_max,
                ess_bulk_min=model.verdict.ess_bulk_min,
                ess_tail_min=model.verdict.ess_tail_min,
                divergence_frac=model.verdict.divergence_frac,
                ci_width_ratio_max=model.verdict.ci_width_ratio_max,
                n_chains=model.verdict.n_chains,
                n_draws_per_chain=model.verdict.n_draws_per_chain,
            ),
        )
