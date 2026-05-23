"""IO Boundary tier for SAAS-COHORT-3 — Pin R5 emission contract.

The ONLY tier where mutable state and external IO live (per
functional-python skill three-tier discipline). All classes have
``__init__``; not frozen-dc.

Pin coverage:

- Pin R5: ``InferenceDataPersister`` writes/reads idata via
  ``arviz.to_netcdf`` / ``from_netcdf`` to/from
  ``estimates/cohort_3_idata_{form}.nc``.
- Pin R5: ``VerdictArtifactWriter`` writes/reads
  ``VerdictRouting`` JSON to/from ``estimates/cohort_3_verdict.json``.
- Pin R5: audit-block sha helper hashes the input parquet path +
  cohort prior fetched_at_utc + the three idata.nc paths.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import SupportsFloat, cast

import arviz as az

from simulations.saas_builder.cohort_3._errors import SchemaMismatchError
from simulations.saas_builder.cohort_3.types import VerdictLabel, VerdictRouting

#: Pin R5 — closed VerdictLabel set, used for inbound JSON validation.
_VERDICT_LABELS: frozenset[str] = frozenset({
    "PASS", "MARGINAL", "INDISTINGUISHABLE", "WEAK", "FAIL",
})

#: Pin R5 — JSON schema field set.
_VERDICT_JSON_FIELDS: frozenset[str] = frozenset({
    "winning_form",
    "verdict",
    "delta_elpd_loo",
    "se",
    "pareto_k_max_per_form",
    "weights_per_form",
    "audit_block",
    "fetched_at_utc",
})


class InferenceDataPersister:
    """Round-trip arviz InferenceData via NetCDF.

    Pin R5 contract — three forms emit to:

    - ``estimates/cohort_3_idata_martingale.nc``
    - ``estimates/cohort_3_idata_ar1_log.nc``
    - ``estimates/cohort_3_idata_det_churn.nc``

    Mutable state at the IO boundary: the ``estimates_root`` directory
    is created on first write.
    """

    def __init__(self, estimates_root: str | Path):
        self.estimates_root = Path(estimates_root)

    def path_for(self, form_name: str) -> Path:
        """Return the canonical file path for a form's idata.nc."""
        return self.estimates_root / f"cohort_3_idata_{form_name}.nc"

    def write(self, form_name: str, idata: az.InferenceData) -> Path:
        """Write idata to ``cohort_3_idata_{form_name}.nc`` and return path."""
        self.estimates_root.mkdir(parents=True, exist_ok=True)
        path = self.path_for(form_name)
        idata.to_netcdf(str(path))
        return path

    def read(self, form_name: str) -> az.InferenceData:
        """Read idata from ``cohort_3_idata_{form_name}.nc``."""
        path = self.path_for(form_name)
        if not path.exists():
            raise FileNotFoundError(f"InferenceData NetCDF not found: {path}")
        return az.from_netcdf(str(path))


class VerdictArtifactWriter:
    """Round-trip ``VerdictRouting`` Value to ``cohort_3_verdict.json``."""

    def __init__(self, estimates_root: str | Path):
        self.estimates_root = Path(estimates_root)

    @property
    def verdict_path(self) -> Path:
        return self.estimates_root / "cohort_3_verdict.json"

    def write(self, verdict: VerdictRouting) -> Path:
        """Serialize ``verdict`` to JSON; return the on-disk path."""
        self.estimates_root.mkdir(parents=True, exist_ok=True)
        payload = {
            "winning_form": verdict.winning_form,
            "verdict": verdict.verdict,
            "delta_elpd_loo": verdict.delta_elpd_loo,
            "se": verdict.se,
            "pareto_k_max_per_form": dict(verdict.pareto_k_max_per_form),
            "weights_per_form": dict(verdict.weights_per_form),
            "audit_block": verdict.audit_block,
            "fetched_at_utc": verdict.fetched_at_utc,
        }
        path = self.verdict_path
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))
        return path

    def read(self) -> VerdictRouting:
        """Read JSON; reconstruct VerdictRouting (validates Pin R5 schema)."""
        path = self.verdict_path
        if not path.exists():
            raise FileNotFoundError(f"Verdict JSON not found: {path}")
        loaded: object = json.loads(path.read_text())
        if not isinstance(loaded, dict):
            raise SchemaMismatchError(
                f"VerdictArtifactWriter.read: top-level JSON must be object;"
                f" got {type(loaded).__name__}"
            )
        payload = cast("dict[str, object]", loaded)
        keys = frozenset(payload.keys())
        if keys != _VERDICT_JSON_FIELDS:
            missing = _VERDICT_JSON_FIELDS - keys
            extra = keys - _VERDICT_JSON_FIELDS
            raise SchemaMismatchError(
                f"VerdictArtifactWriter.read: schema drift —"
                f" missing={sorted(missing)} extra={sorted(extra)}"
            )
        pkmpf = payload["pareto_k_max_per_form"]
        wpf = payload["weights_per_form"]
        if not isinstance(pkmpf, Mapping) or not isinstance(wpf, Mapping):
            raise SchemaMismatchError(
                "VerdictArtifactWriter.read: pareto_k_max_per_form and"
                " weights_per_form must be JSON objects"
            )
        verdict_raw = payload["verdict"]
        if not isinstance(verdict_raw, str) or verdict_raw not in _VERDICT_LABELS:
            raise SchemaMismatchError(
                f"VerdictArtifactWriter.read: 'verdict' = {verdict_raw!r}"
                f" must be one of {sorted(_VERDICT_LABELS)}"
            )
        verdict_label: VerdictLabel = cast(VerdictLabel, verdict_raw)
        return VerdictRouting(
            verdict=verdict_label,
            winning_form=str(payload["winning_form"]),
            delta_elpd_loo=_to_float(payload["delta_elpd_loo"]),
            se=_to_float(payload["se"]),
            pareto_k_max_per_form={
                str(k): _to_float(v) for k, v in pkmpf.items()
            },
            weights_per_form={
                str(k): _to_float(v) for k, v in wpf.items()
            },
            audit_block=str(payload["audit_block"]),
            fetched_at_utc=str(payload["fetched_at_utc"]),
        )


def _to_float(value: object) -> float:
    """Coerce a JSON-decoded numeric to float; raise SchemaMismatchError otherwise.

    Phase-3 nit (CR N2 v0.3 sweep): the prior
    ``isinstance(value, (int, float)) or isinstance(value, SupportsFloat)``
    was redundant — ``int`` and ``float`` are both ``SupportsFloat``
    subtypes. A single ``SupportsFloat`` check suffices and tightens
    type narrowing.
    """
    if isinstance(value, SupportsFloat):
        return float(value)
    raise SchemaMismatchError(
        f"VerdictArtifactWriter._to_float: value {value!r}"
        f" of type {type(value).__name__} is not numeric"
    )


def compute_audit_block(
    parquet_path: str | Path,
    cohort_prior_fetched_at_utc: str,
    idata_paths: Mapping[str, str | Path],
) -> str:
    """Compute SHA-256 audit block per Pin R5.

    Hashes a deterministic concatenation:

        str(parquet_path) || "\\n" || cohort_prior_fetched_at_utc
        || "\\n" || "form_name=<path>" lines, sorted by form name.

    Returns the 64-char lowercase hex digest.
    """
    parts = [
        str(parquet_path),
        str(cohort_prior_fetched_at_utc),
    ]
    for name in sorted(idata_paths):
        parts.append(f"{name}={idata_paths[name]}")
    payload = "\n".join(parts).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


__all__ = [
    "InferenceDataPersister",
    "VerdictArtifactWriter",
    "compute_audit_block",
]
