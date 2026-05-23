"""IO-Boundary tier for the verify-only API.

Per design v0.3 §3a.4 + §3a.4.1 (with correction noted below).

Loads committed Stage-2 artifacts and emits a single ``trio_audit_sha256``
anchor consumed by every R-tag verdict. The four committed JSONs
(``Z_cap_pinned.json``, ``gate_verdict.json``, ``revenue_form_verdict.json``,
``_AUDIT.json``) each carry their own ``audit_block`` field whose value is a
sha256 over UPSTREAM source bytes (e.g. ``cohort_prior.parquet``,
``synthetic_tau_t/`` partitions), NOT over the JSON file itself. The full
upstream-lineage rehash via :class:`simulations.utils.audit_block.AuditBlockHasher`
requires the source files at the paths embedded in ``_AUDIT.json`` and is
out of scope for the notebook trio (which runs against committed artifacts
only).

The tamper anchor implemented here is the simpler "file-bytes anchor":
sha256 over each committed JSON's bytes, concatenated in alphabetical
order, re-hashed. This is deterministic and changes if any committed
artifact is mutated — adequate for the trio's tamper-detection contract.

At construction, the loader (a) confirms each artifact carries a
syntactically-valid 64-char lowercase-hex ``audit_block`` field, and
(b) computes the trio-level anchor. Construction raises
``AuditBlockMismatch`` if any artifact's ``audit_block`` field is
missing or malformed.

JSON field-name note
--------------------
The committed ``gate_verdict.json`` uses the pre-rename field names
``delta_lower_bound_95`` / ``delta_upper_bound_95`` in the evidence
array (written by the original COHORT-2 gate emitter before the
CR I1 v0.3 sweep renamed those fields to ``delta_lower_bound_quantile``
/ ``delta_upper_bound_quantile`` and added ``ci_level``).
:func:`_gate_verdict_from_dict` maps the on-disk names to the current
``SignVerdict`` field names, injecting ``ci_level=0.95`` (the
``_95`` suffix unambiguously encodes the 95 pct credible level).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import numpy as np

from simulations.saas_builder.cohort_2.types import CohortGateVerdict, SignVerdict
from simulations.types.posterior import ZCapPinned
from simulations.types.saas_cohort1_audit import Audit
from simulations.utils.json_io import AuditReader, ZCapPinnedReader

_AUDIT_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")
_HASH_CHUNK_BYTES: Final[int] = 1 << 20


class AuditBlockMismatch(RuntimeError):
    """Raised when a committed artifact's ``audit_block`` field is missing
    or not a 64-char lowercase-hex sha256."""


class GateVerdictSchemaError(RuntimeError):
    """Raised when ``gate_verdict.json`` is missing a required field."""


@dataclass(frozen=True)
class _ArtifactPaths:
    z_cap_pinned: Path
    gate_verdict: Path
    revenue_form_verdict: Path
    audit: Path
    posterior_chain: Path  # synthetic_tau_t partition root


def _file_sha256(path: Path) -> str:
    """Return 64-char lowercase hex sha256 over the file's bytes."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(_HASH_CHUNK_BYTES), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_audit_block_field(path: Path) -> str:
    """Read the ``audit_block`` field from a committed JSON artifact.

    Raises ``AuditBlockMismatch`` if missing or syntactically invalid.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "audit_block" not in raw:
        raise AuditBlockMismatch(
            f"{path.name}: missing 'audit_block' field"
        )
    value = raw["audit_block"]
    if not isinstance(value, str) or not _AUDIT_BLOCK_RE.fullmatch(value):
        raise AuditBlockMismatch(
            f"{path.name}: audit_block field not 64-char lowercase hex; "
            f"got {value!r}"
        )
    return value


def _gate_verdict_from_dict(raw: dict[str, Any]) -> CohortGateVerdict:
    """Reconstruct a ``CohortGateVerdict`` from parsed JSON.

    The JSON-on-disk schema in ``gate_verdict.json`` was written by the
    original COHORT-2 gate emitter using the pre-rename field names
    ``delta_lower_bound_95`` / ``delta_upper_bound_95`` in each evidence
    entry. The current ``SignVerdict`` dataclass (CR I1 v0.3 sweep) uses
    ``delta_lower_bound_quantile`` / ``delta_upper_bound_quantile`` plus an
    explicit ``ci_level`` field.

    This function maps the on-disk names to the current ``SignVerdict``
    fields, injecting ``ci_level=0.95`` (the ``_95`` suffix unambiguously
    encodes the 95 pct credible level). Evidence entries from the original
    emitter do not carry an ``audit_block`` field; the empty-string default
    is accepted by ``SignVerdict.__post_init__`` for in-memory records.
    """
    try:
        evidence_raw = raw["evidence"]
        evidence = tuple(
            SignVerdict(
                bracket_index=int(ev["bracket_index"]),
                delta_lower_bound_quantile=float(ev["delta_lower_bound_95"]),
                delta_median=float(ev["delta_median"]),
                delta_upper_bound_quantile=float(ev["delta_upper_bound_95"]),
                sign_strictly_negative=bool(ev["sign_strictly_negative"]),
                ci_level=float(ev.get("ci_level", 0.95)),
                audit_block=str(ev.get("audit_block", "")),
            )
            for ev in evidence_raw
        )
        return CohortGateVerdict(
            sub_task=raw["sub_task"],
            verdict=raw["verdict"],
            n_bracket_points=int(raw["n_bracket_points"]),
            n_sign_violations=int(raw["n_sign_violations"]),
            evidence=evidence,
            audit_block=str(raw["audit_block"]),
            fetched_at_utc=str(raw["fetched_at_utc"]),
            ppc_coverage=dict(raw.get("ppc_coverage", {})),
        )
    except KeyError as e:
        raise GateVerdictSchemaError(
            f"gate_verdict.json missing required field: {e!s}"
        ) from e


class CommittedArtifactLoader:
    """Load committed Stage-2 artifacts and emit a uniform trio audit anchor.

    Construction validates each artifact's ``audit_block`` field and
    computes ``trio_audit_sha256`` once (a sha256 over the four committed
    JSONs in alphabetical order by filename). Raises ``AuditBlockMismatch``
    if any artifact's ``audit_block`` is missing or malformed.

    The ``audit_block`` fields embedded in the committed JSONs are sha256
    values over UPSTREAM source bytes, not over the JSON files themselves.
    This class does not attempt to re-derive those upstream hashes (doing so
    would require the source files referenced in ``_AUDIT.json``, which are
    not present in the committed artifact set). The ``trio_audit_sha256``
    property is a file-bytes anchor computed here, separate from the
    per-artifact ``audit_block`` lineage chain.
    """

    def __init__(self, data_root: str | Path) -> None:
        root = Path(data_root)
        self._paths = _ArtifactPaths(
            z_cap_pinned=root / "Z_cap_pinned.json",
            gate_verdict=root / "gate_verdict.json",
            revenue_form_verdict=root / "revenue_form_verdict.json",
            audit=root / "_AUDIT.json",
            posterior_chain=root / "synthetic_tau_t",
        )
        # Validate audit_block field on each committed JSON
        for p in (
            self._paths.audit,
            self._paths.gate_verdict,
            self._paths.revenue_form_verdict,
            self._paths.z_cap_pinned,
        ):
            if not p.is_file():
                raise FileNotFoundError(
                    f"CommittedArtifactLoader: missing artifact at {p}"
                )
            _read_audit_block_field(p)
        self._trio_sha256 = self._compute_trio_audit_sha256()

    def _compute_trio_audit_sha256(self) -> str:
        """sha256 over file bytes of the four JSONs in alphabetical order, re-hashed."""
        ordered = sorted(
            [
                self._paths.audit,
                self._paths.gate_verdict,
                self._paths.revenue_form_verdict,
                self._paths.z_cap_pinned,
            ],
            key=lambda p: p.name,
        )
        h = hashlib.sha256()
        for p in ordered:
            h.update(_file_sha256(p).encode("ascii"))
        return h.hexdigest()

    @property
    def trio_audit_sha256(self) -> str:
        """The trio-level tamper anchor; same value across all 8 RTagVerdicts."""
        return self._trio_sha256

    def load_z_cap_pinned(self) -> ZCapPinned:
        return ZCapPinnedReader()(self._paths.z_cap_pinned)

    def load_audit(self) -> Audit:
        return AuditReader()(self._paths.audit)

    def load_gate_verdict(self) -> CohortGateVerdict:
        raw = json.loads(self._paths.gate_verdict.read_text(encoding="utf-8"))
        return _gate_verdict_from_dict(raw)

    def load_revenue_form_verdict(self) -> dict[str, Any]:
        """Load ``revenue_form_verdict.json`` as a parsed dict.

        The on-disk schema is a comparison-level structure (multiple
        fits + metadata) rather than a single ``RevenueFormFit`` value.
        Returning the dict lets R6/R7 verifiers read fields like
        ``_metadata.halt_on_flip_comparison`` directly without forcing
        a synthetic Value type that would only ever have one consumer.
        """
        return json.loads(
            self._paths.revenue_form_verdict.read_text(encoding="utf-8")
        )

    def load_posterior_chain(self) -> np.ndarray:
        """Load the C1 posterior partition as a 2-D numpy array.

        Reads the partitioned parquet under ``synthetic_tau_t/`` (partitioned
        by ``tier_id`` and ``month``). Returns shape ``(n_rows, n_columns)``
        with all numeric columns concatenated.
        """
        import pyarrow.dataset as ds
        import pyarrow.types as pa_types

        dataset = ds.dataset(self._paths.posterior_chain, format="parquet")
        table = dataset.to_table()
        # Drop string-valued partition columns (tier_id, sub_task, etc.)
        numeric_cols = [
            name
            for name, dtype in zip(table.column_names, table.schema.types)
            if pa_types.is_integer(dtype) or pa_types.is_floating(dtype)
        ]
        if not numeric_cols:
            return np.zeros((table.num_rows, 0), dtype=np.float64)
        return np.column_stack(
            [table.column(name).to_numpy() for name in numeric_cols]
        ).astype(np.float64, copy=False)
