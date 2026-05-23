"""AuditReader IO-Boundary tier tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from simulations.types.saas_cohort1_audit import Audit
from simulations.utils.json_io import AuditReader


@pytest.fixture
def audit_json(tmp_path: Path) -> Path:
    payload = {
        "audit_block": "ded06012ea8e01bea660e4ae6bdc2be1470b6de84c647735cb8161927b06162a",
        "schema_version": "v1.0",
        "synthetic_tau_path": "/abs/path/synthetic_tau_t",
        "cohort_prior_path": "/abs/path/cohort_prior.parquet",
        "month": 3,
        "n_rows_synthetic": 712000,
        "verdict": {
            "rhat_max": 1.0000265,
            "ess_bulk_min": 338539.83,
            "ess_tail_min": 213751.90,
            "divergence_frac": 0.0,
            "ci_width_ratio_max": 1.0038739,
            "n_chains": 4,
            "n_draws_per_chain": 178000,
        },
    }
    p = tmp_path / "_AUDIT.json"
    p.write_text(json.dumps(payload))
    return p


def test_audit_reader_returns_audit_value(audit_json: Path) -> None:
    reader = AuditReader()
    audit = reader(audit_json)
    assert isinstance(audit, Audit)
    assert audit.audit_block.startswith("ded06012")
    assert audit.month == 3
    assert audit.verdict.n_chains == 4


def test_audit_reader_rejects_missing_field(tmp_path: Path) -> None:
    p = tmp_path / "_AUDIT.json"
    p.write_text(json.dumps({"audit_block": "d" * 64}))
    reader = AuditReader()
    with pytest.raises(ValidationError):
        reader(p)


def test_audit_reader_loads_committed_audit() -> None:
    """Smoke test against the actual committed _AUDIT.json."""
    p = Path("simulations/saas_builder/data/_AUDIT.json")
    if not p.exists():
        pytest.skip("committed _AUDIT.json not present (regenerate via cohort1)")
    reader = AuditReader()
    audit = reader(p)
    assert audit.verdict.n_chains == 4
    assert audit.n_rows_synthetic == 712000
