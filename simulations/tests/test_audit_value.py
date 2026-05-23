"""Audit Value-tier tests."""
from __future__ import annotations

import dataclasses

import pytest

from simulations.types.saas_cohort1_audit import (
    Audit,
    AuditVerdict,
    AuditValueError,
)


def _good_verdict() -> AuditVerdict:
    return AuditVerdict(
        rhat_max=1.0000265166749636,
        ess_bulk_min=338539.83453266014,
        ess_tail_min=213751.90098294566,
        divergence_frac=0.0,
        ci_width_ratio_max=1.0038739188714958,
        n_chains=4,
        n_draws_per_chain=178000,
    )


def test_audit_constructs_valid() -> None:
    audit = Audit(
        audit_block="ded06012ea8e01bea660e4ae6bdc2be1470b6de84c647735cb8161927b06162a",
        schema_version="v1.0",
        synthetic_tau_path="/abs/path/synthetic_tau_t",
        cohort_prior_path="/abs/path/cohort_prior.parquet",
        month=3,
        n_rows_synthetic=712000,
        verdict=_good_verdict(),
    )
    assert audit.audit_block.startswith("ded06012")
    assert audit.verdict.rhat_max == pytest.approx(1.0000265166749636)


def test_audit_rejects_short_audit_block() -> None:
    with pytest.raises(AuditValueError, match="64-char"):
        Audit(
            audit_block="abc",
            schema_version="v1.0",
            synthetic_tau_path="/p",
            cohort_prior_path="/p",
            month=3,
            n_rows_synthetic=712000,
            verdict=_good_verdict(),
        )


def test_audit_rejects_negative_n_rows() -> None:
    with pytest.raises(AuditValueError, match="n_rows_synthetic"):
        Audit(
            audit_block="d" * 64,
            schema_version="v1.0",
            synthetic_tau_path="/p",
            cohort_prior_path="/p",
            month=3,
            n_rows_synthetic=-1,
            verdict=_good_verdict(),
        )


def test_audit_is_frozen() -> None:
    audit = Audit(
        audit_block="d" * 64,
        schema_version="v1.0",
        synthetic_tau_path="/p",
        cohort_prior_path="/p",
        month=3,
        n_rows_synthetic=712000,
        verdict=_good_verdict(),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        audit.month = 4  # type: ignore[misc]  # ty: ignore[invalid-assignment]


def test_audit_verdict_rejects_rhat_below_one() -> None:
    with pytest.raises(AuditValueError, match="rhat_max"):
        AuditVerdict(
            rhat_max=0.5,
            ess_bulk_min=338539.0,
            ess_tail_min=213751.0,
            divergence_frac=0.0,
            ci_width_ratio_max=1.0,
            n_chains=4,
            n_draws_per_chain=178000,
        )


def test_audit_verdict_rejects_negative_ess() -> None:
    with pytest.raises(AuditValueError, match="ess_bulk_min"):
        AuditVerdict(
            rhat_max=1.01,
            ess_bulk_min=-1.0,
            ess_tail_min=213751.0,
            divergence_frac=0.0,
            ci_width_ratio_max=1.0,
            n_chains=4,
            n_draws_per_chain=178000,
        )


def test_audit_verdict_rejects_divergence_frac_above_one() -> None:
    with pytest.raises(AuditValueError, match="divergence_frac"):
        AuditVerdict(
            rhat_max=1.01,
            ess_bulk_min=338539.0,
            ess_tail_min=213751.0,
            divergence_frac=1.5,
            ci_width_ratio_max=1.0,
            n_chains=4,
            n_draws_per_chain=178000,
        )


def test_audit_verdict_rejects_nan_metric() -> None:
    with pytest.raises(AuditValueError):
        AuditVerdict(
            rhat_max=float("nan"),
            ess_bulk_min=338539.0,
            ess_tail_min=213751.0,
            divergence_frac=0.0,
            ci_width_ratio_max=1.0,
            n_chains=4,
            n_draws_per_chain=178000,
        )


def test_audit_rejects_empty_schema_version() -> None:
    with pytest.raises(AuditValueError, match="schema_version"):
        Audit(
            audit_block="d" * 64,
            schema_version="",
            synthetic_tau_path="/p",
            cohort_prior_path="/p",
            month=3,
            n_rows_synthetic=712000,
            verdict=_good_verdict(),
        )
