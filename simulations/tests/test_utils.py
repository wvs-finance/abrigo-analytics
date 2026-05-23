"""IO-Boundary unit tests for ``simulations.utils``.

Covers parquet round-trip + dtype enforcement at the writer boundary,
JSON round-trip via Pydantic, the audit-block sha256 helper (path-order
invariance + str/Path acceptance), and the typed error surfaces
(``SchemaMismatchError`` on column drift; ``FileNotFoundError`` on
empty / missing dataset paths per the I4-fix).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal, cast

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from simulations.types.posterior import (
    DEFAULT_SCHEMA_VERSION,
    SCHEMA_VERSION_V1_1,
    SignVerdictEntry,
    ZCapPinned,
)
from simulations.utils.audit_block import AuditBlockHasher, compute_audit_block
from simulations.utils.errors import SchemaMismatchError
from simulations.utils.json_io import ZCapPinnedReader, ZCapPinnedWriter
from simulations.utils.parquet_io import (
    COHORT_PRIOR_COLUMNS,
    SYNTHETIC_TAU_COLUMNS,
    CohortPriorReader,
    CohortPriorRow,
    CohortPriorWriter,
    SyntheticTauReader,
    SyntheticTauWriter,
    cohort_prior_row,
    synthetic_tau_row,
)
from simulations.utils.pricing_fetcher import StaticPricingFetcher


# ─── Cohort prior parquet round-trip ──────────────────────────────────────────


class TestCohortPriorIO:
    def test_cohort_prior_round_trip(self, tmp_path: Path) -> None:
        """Write 3 rows of cohort_prior and read back with all columns intact."""
        rows: list[CohortPriorRow] = [
            cohort_prior_row(
                param=p,
                percentile=q,
                value=v,
                source="spec_5_2",
                fetched_at_utc="2026-05-07T00:00:00Z",
            )
            for p, q, v in [
                ("alpha", "p50", 2.0),
                ("alpha", "p90", 2.5),
                ("p_in_sonnet", "pin", 3.0),
            ]
        ]
        writer = CohortPriorWriter(base_dir=tmp_path)
        writer(rows)
        reader = CohortPriorReader(base_dir=tmp_path)
        recovered = reader()
        assert len(recovered) == 3
        recovered_sorted = sorted(recovered, key=lambda r: (r["param"], r["percentile"]))
        original_sorted = sorted(rows, key=lambda r: (r["param"], r["percentile"]))
        for got, want in zip(recovered_sorted, original_sorted):
            assert got == want

    def test_cohort_prior_default_base_dir_is_constructible(self) -> None:
        """Default ``base_dir`` resolves to the canonical M4 data path.

        Catches mutations like ``Path(None)`` (would raise) or path-string
        mutations that would relocate the default. We don't write here —
        just verify the constructor builds and the resolved path matches the
        documented Spec §M4 location.
        """
        w = CohortPriorWriter()
        r = CohortPriorReader()
        # Internal default path is documented as ``simulations/saas_builder/data``.
        assert w._base_dir == Path("simulations/saas_builder/data")
        assert r._base_dir == Path("simulations/saas_builder/data")

    def test_synthetic_tau_default_base_dir_is_constructible(self) -> None:
        """Default ``base_dir`` resolves to the canonical M4 data path."""
        w = SyntheticTauWriter()
        r = SyntheticTauReader()
        assert w._base_dir == Path("simulations/saas_builder/data")
        assert r._base_dir == Path("simulations/saas_builder/data")

    def test_cohort_prior_writer_creates_missing_parents(self, tmp_path: Path) -> None:
        """Writer auto-creates the full base_dir parent chain.

        Catches mutations dropping ``parents=True`` from the writer's ``mkdir``.
        """
        deep = tmp_path / "a" / "b" / "c"
        rows: list[CohortPriorRow] = [
            cohort_prior_row(
                param="alpha",
                percentile="p50",
                value=2.0,
                source="spec",
                fetched_at_utc="2026-05-07T00:00:00Z",
            )
        ]
        CohortPriorWriter(base_dir=deep)(rows)
        assert (deep / "cohort_prior.parquet").is_file()

    def test_cohort_prior_writer_does_not_emit_pandas_index(
        self, tmp_path: Path
    ) -> None:
        """Writer must call ``index=False`` on ``to_parquet`` — no row-index col.

        Catches mutations like ``index=True`` (would add a numeric index column
        and break the column-set check on read).
        """
        rows: list[CohortPriorRow] = [
            cohort_prior_row(
                param="alpha",
                percentile="p50",
                value=2.0,
                source="spec",
                fetched_at_utc="2026-05-07T00:00:00Z",
            )
        ]
        CohortPriorWriter(base_dir=tmp_path)(rows)
        out = tmp_path / "cohort_prior.parquet"
        df = pd.read_parquet(out)
        assert not any(c.startswith("__index_level") for c in df.columns), (
            f"index column leaked into parquet: {list(df.columns)}"
        )
        # Stricter: the column set on disk must be exactly the declared schema.
        assert set(df.columns) == set(COHORT_PRIOR_COLUMNS), (
            f"unexpected columns on disk: {set(df.columns) - set(COHORT_PRIOR_COLUMNS)}"
        )

    def test_cohort_prior_writer_empty_raises(self, tmp_path: Path) -> None:
        """Empty rows list rejected."""
        with pytest.raises(ValueError, match="non-empty"):
            CohortPriorWriter(base_dir=tmp_path)([])

    def test_cohort_prior_reader_missing_file_raises(self, tmp_path: Path) -> None:
        """Reading from an empty directory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="missing parquet"):
            CohortPriorReader(base_dir=tmp_path)()

    def test_cohort_prior_reader_schema_mismatch_extra_column(
        self, tmp_path: Path
    ) -> None:
        """Reader raises SchemaMismatchError when on-disk parquet has extra column."""
        # Hand-craft a parquet with an extra column.
        df = pd.DataFrame(
            {
                "param": ["alpha"],
                "percentile": ["p50"],
                "value": [2.0],
                "source": ["s"],
                "fetched_at_utc": ["t"],
                "schema_version": ["v1.0"],
                "rogue_extra": ["nope"],
            }
        )
        out = tmp_path / "cohort_prior.parquet"
        df.to_parquet(out, index=False)
        with pytest.raises(SchemaMismatchError, match="extra"):
            CohortPriorReader(base_dir=tmp_path)()

    def test_cohort_prior_reader_schema_mismatch_missing_column(
        self, tmp_path: Path
    ) -> None:
        """Reader raises SchemaMismatchError when on-disk parquet is missing a column."""
        df = pd.DataFrame(
            {
                "param": ["alpha"],
                "percentile": ["p50"],
                "value": [2.0],
                "source": ["s"],
                # Missing fetched_at_utc + schema_version.
            }
        )
        out = tmp_path / "cohort_prior.parquet"
        df.to_parquet(out, index=False)
        with pytest.raises(SchemaMismatchError, match="missing"):
            CohortPriorReader(base_dir=tmp_path)()


# ─── Synthetic-tau Hive-partitioned parquet round-trip ────────────────────────


def _make_tau_rows(n_per_combo: int = 1) -> list:
    """Build 12 SyntheticTauRows: 3 tiers × 4 months × n_per_combo."""
    rows = []
    sim_id = 0
    for tier in ("pro", "max_5x", "max_20x"):
        for month in (1, 2, 3, 4):
            for _ in range(n_per_combo):
                rows.append(
                    synthetic_tau_row(
                        month=month,
                        simulation_id=sim_id,
                        tier_id=tier,
                        r=4.0,
                        p=0.5,
                        alpha=2.0,
                        x_m=1.0,
                        tau_t=1234.0,
                        q_t_usd=20.0,
                        q_t_cop=80000.0,
                    )
                )
                sim_id += 1
    return rows


class TestSyntheticTauIO:
    def test_synthetic_tau_round_trip_via_hive_tree(self, tmp_path: Path) -> None:
        """Write 12 mixed-tier mixed-month rows; read back with partitions intact."""
        rows = _make_tau_rows()
        SyntheticTauWriter(base_dir=tmp_path)(rows)
        recovered = SyntheticTauReader(base_dir=tmp_path)()
        assert len(recovered) == 12
        # Confirm partition columns survived.
        tiers = {r["tier_id"] for r in recovered}
        months = {r["month"] for r in recovered}
        assert tiers == {"pro", "max_5x", "max_20x"}
        assert months == {1, 2, 3, 4}

    def test_synthetic_tau_round_trip_field_fidelity(self, tmp_path: Path) -> None:
        """Each numeric field round-trips with distinct values — catches field-swap bugs.

        Uses prime-distinct values for r/p/alpha/x_m/tau_t/q_t_usd/q_t_cop so that
        a mutation that swaps two field assignments in ``synthetic_tau_row`` or
        re-orders the row constructor surfaces as a value mismatch on read.
        """
        # Distinct primes/decimals — no two fields share a value.
        row = synthetic_tau_row(
            month=7,
            simulation_id=42,
            tier_id="pro",
            r=3.14,
            p=0.59,
            alpha=2.71,
            x_m=1.41,
            tau_t=1729.0,
            q_t_usd=23.0,
            q_t_cop=89897.0,
        )
        SyntheticTauWriter(base_dir=tmp_path)([row])
        recovered = SyntheticTauReader(base_dir=tmp_path)()
        assert len(recovered) == 1
        got = recovered[0]
        # Field-by-field equality — distinct values prevent silent swap survival.
        assert got["month"] == 7
        assert got["simulation_id"] == 42
        assert got["tier_id"] == "pro"
        assert got["r"] == 3.14
        assert got["p"] == 0.59
        assert got["alpha"] == 2.71
        assert got["x_m"] == 1.41
        assert got["tau_t"] == 1729.0
        assert got["q_t_usd"] == 23.0
        assert got["q_t_cop"] == 89897.0
        assert got["schema_version"] == DEFAULT_SCHEMA_VERSION

    def test_synthetic_tau_row_helper_field_assignment(self) -> None:
        """``synthetic_tau_row`` assigns each kwarg to the correctly-named field.

        Direct test of the row-builder — independent of parquet I/O — so each
        keyword argument's destination is checked. Catches mutations that
        delete/swap field assignments inside the constructor.
        """
        row = synthetic_tau_row(
            month=11,
            simulation_id=99,
            tier_id="max_20x",
            r=5.0,
            p=0.6,
            alpha=3.0,
            x_m=2.0,
            tau_t=4242.0,
            q_t_usd=11.0,
            q_t_cop=44440.0,
        )
        assert row["month"] == 11
        assert row["simulation_id"] == 99
        assert row["tier_id"] == "max_20x"
        assert row["r"] == 5.0
        assert row["p"] == 0.6
        assert row["alpha"] == 3.0
        assert row["x_m"] == 2.0
        assert row["tau_t"] == 4242.0
        assert row["q_t_usd"] == 11.0
        assert row["q_t_cop"] == 44440.0
        assert row["schema_version"] == DEFAULT_SCHEMA_VERSION

    def test_synthetic_tau_row_helper_custom_schema_version(self) -> None:
        """Non-default ``schema_version`` flows through unchanged."""
        row = synthetic_tau_row(
            month=1,
            simulation_id=0,
            tier_id="pro",
            r=1.0,
            p=0.1,
            alpha=1.0,
            x_m=1.0,
            tau_t=1.0,
            q_t_usd=1.0,
            q_t_cop=1.0,
            schema_version="v9.9-test",
        )
        assert row["schema_version"] == "v9.9-test"

    def test_synthetic_tau_dtype_enforcement(self, tmp_path: Path) -> None:
        """Float-typed `month=4.0` input lands on disk as int (Hive dir `month=4/`)."""
        # SyntheticTauRow is a TypedDict; runtime ignores the int annotation.
        # We construct via dict() to bypass the helper's keyword validation.
        rogue_row: dict[str, object] = {
            "month": 4.0,  # caller passed float
            "simulation_id": 0,
            "tier_id": "pro",
            "r": 4.0,
            "p": 0.5,
            "alpha": 2.0,
            "x_m": 1.0,
            "tau_t": 1234.0,
            "q_t_usd": 20.0,
            "q_t_cop": 80000.0,
            "schema_version": "v1.0",
        }
        SyntheticTauWriter(base_dir=tmp_path)(cast(Any, [rogue_row]))
        # The Hive partition directory must be `month=4/`, not `month=4.0/`.
        partition_dirs = list(
            (tmp_path / "synthetic_tau_t" / "tier_id=pro").glob("month=*")
        )
        assert len(partition_dirs) == 1
        assert partition_dirs[0].name == "month=4"
        # Reader-side: month is int.
        recovered = SyntheticTauReader(base_dir=tmp_path)()
        assert recovered[0]["month"] == 4
        assert isinstance(recovered[0]["month"], int)

    def test_synthetic_tau_writer_creates_missing_parents(self, tmp_path: Path) -> None:
        """Writer auto-creates the full output-root parent chain.

        Catches mutations dropping ``parents=True`` from ``mkdir``.
        """
        deep = tmp_path / "a" / "b" / "c"
        # Parent chain "a/b/c" does not exist yet.
        SyntheticTauWriter(base_dir=deep)(_make_tau_rows(n_per_combo=1))
        assert (deep / "synthetic_tau_t").is_dir()

    def test_synthetic_tau_writer_does_not_emit_pandas_index(
        self, tmp_path: Path
    ) -> None:
        """Writer must call ``preserve_index=False`` so no index column lands on disk.

        Build a DataFrame with a non-default index and ensure the round-trip
        still produces a clean column set (no ``__index_level_0__`` leak).
        Catches mutations like ``preserve_index=True``.
        """
        rows = _make_tau_rows(n_per_combo=1)
        SyntheticTauWriter(base_dir=tmp_path)(rows)
        # Inspect any one parquet file for the absence of an index column.
        any_parquet = next(
            (tmp_path / "synthetic_tau_t").rglob("*.parquet")
        )
        df = pd.read_parquet(any_parquet)
        assert not any(c.startswith("__index_level") for c in df.columns), (
            f"index column leaked into parquet: {list(df.columns)}"
        )

    def test_synthetic_tau_writer_empty_rows_raises(self, tmp_path: Path) -> None:
        """Empty rows list rejected with explicit error mentioning 'non-empty'."""
        with pytest.raises(ValueError, match="non-empty"):
            SyntheticTauWriter(base_dir=tmp_path)([])

    def test_synthetic_tau_writer_error_identifies_class(self, tmp_path: Path) -> None:
        """Empty-rows error message names the writer class for diagnosability."""
        with pytest.raises(ValueError, match=r"SyntheticTauWriter"):
            SyntheticTauWriter(base_dir=tmp_path)([])

    def test_synthetic_tau_reader_error_identifies_class(self, tmp_path: Path) -> None:
        """Missing-dataset error message names the reader class for diagnosability."""
        with pytest.raises(FileNotFoundError, match=r"SyntheticTauReader"):
            SyntheticTauReader(base_dir=tmp_path)()

    def test_synthetic_tau_reader_empty_dir_raises(self, tmp_path: Path) -> None:
        """Reading a missing dataset directory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="missing dataset"):
            SyntheticTauReader(base_dir=tmp_path)()

    def test_synthetic_tau_reader_empty_existing_dir_raises(
        self, tmp_path: Path
    ) -> None:
        """An existing but empty dataset dir surfaces the I4 'no parquet files' guard."""
        empty_root = tmp_path / "synthetic_tau_t"
        empty_root.mkdir()
        with pytest.raises(FileNotFoundError, match="no parquet files"):
            SyntheticTauReader(base_dir=tmp_path)()

    def test_synthetic_tau_reader_schema_mismatch(self, tmp_path: Path) -> None:
        """A parquet emitted with the wrong column set raises SchemaMismatchError."""
        out_root = tmp_path / "synthetic_tau_t" / "tier_id=pro" / "month=1"
        out_root.mkdir(parents=True)
        # Drop the schema_version column on purpose.
        df = pd.DataFrame(
            {
                "simulation_id": [0],
                "r": [4.0],
                "p": [0.5],
                "alpha": [2.0],
                "x_m": [1.0],
                "tau_t": [1234.0],
                "q_t_usd": [20.0],
                "q_t_cop": [80000.0],
                # missing schema_version
            }
        )
        table = pa.Table.from_pandas(df, preserve_index=False)
        pq.write_table(table, out_root / "part-0.parquet")
        with pytest.raises(SchemaMismatchError):
            SyntheticTauReader(base_dir=tmp_path)()


# ─── ZCapPinned JSON round-trip ───────────────────────────────────────────────


def _zcap_sample() -> ZCapPinned:
    return ZCapPinned(
        Z_cop_per_month=120_000.0,
        ci_95_lo=110_000.0,
        ci_95_hi=130_000.0,
        audit_block="a" * 64,
        tier_mix={"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30},
    )


class TestZCapPinnedJsonIO:
    def test_zcap_pinned_round_trip(self, tmp_path: Path) -> None:
        """Pydantic-validated round trip preserves every M4 field."""
        target = tmp_path / "Z_cap_pinned.json"
        z = _zcap_sample()
        ZCapPinnedWriter()(z, target)
        recovered = ZCapPinnedReader()(target)
        assert recovered == z

    def test_zcap_pinned_round_trip_non_default_schema_version(
        self, tmp_path: Path
    ) -> None:
        """schema_version flows through reader unchanged when non-default.

        Catches mutations that drop ``schema_version`` from the reader's
        constructor (which would silently substitute the dataclass default).
        """
        target = tmp_path / "Z_cap_pinned.json"
        z = ZCapPinned(
            Z_cop_per_month=120_000.0,
            ci_95_lo=110_000.0,
            ci_95_hi=130_000.0,
            audit_block="b" * 64,
            tier_mix={"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30},
            schema_version="v9.9-test",  # non-default
        )
        ZCapPinnedWriter()(z, target)
        recovered = ZCapPinnedReader()(target)
        assert recovered.schema_version == "v9.9-test"
        assert recovered == z

    def test_zcap_pinned_writer_creates_missing_parents(self, tmp_path: Path) -> None:
        """Writer auto-creates the full parent directory chain.

        Catches mutations that drop ``parents=True`` from the ``mkdir`` call
        (e.g. ``parents=False`` would raise ``FileNotFoundError`` here).
        """
        deep = tmp_path / "a" / "b" / "c" / "Z_cap_pinned.json"
        # Parent chain "a/b/c" does not exist yet.
        ZCapPinnedWriter()(_zcap_sample(), deep)
        assert deep.is_file()

    def test_zcap_pinned_writer_output_is_indented_and_sorted(
        self, tmp_path: Path
    ) -> None:
        """ZCap JSON output is human-readable: indent=2 + sort_keys=True.

        Catches mutations that drop ``indent``, ``sort_keys``, or change the
        ``encoding`` argument away from utf-8 (audit-relevant byte fidelity).
        """
        target = tmp_path / "Z_cap_pinned.json"
        ZCapPinnedWriter()(_zcap_sample(), target)
        text = target.read_text(encoding="utf-8")
        # indent=2 ⇒ output spans multiple lines, with two-space indent.
        assert "\n" in text, "output not indented (single-line JSON)"
        assert "\n  " in text, "output indent depth not 2 spaces"
        # sort_keys=True ⇒ keys appear alphabetically.
        # Z_cop_per_month < audit_block < ci_95_hi < ci_95_lo (alphabetical, capital Z first).
        # Find positions of known keys; sorted order must hold.
        idx_audit = text.index('"audit_block"')
        idx_ci_hi = text.index('"ci_95_hi"')
        idx_ci_lo = text.index('"ci_95_lo"')
        idx_schema = text.index('"schema_version"')
        idx_tier = text.index('"tier_mix"')
        # Alphabetical: audit_block < ci_95_hi < ci_95_lo < schema_version < tier_mix
        assert idx_audit < idx_ci_hi < idx_ci_lo < idx_schema < idx_tier, (
            "sort_keys=True ordering broken"
        )

    def test_zcap_pinned_reader_missing_file(self, tmp_path: Path) -> None:
        """Reading a missing JSON raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="missing JSON"):
            ZCapPinnedReader()(tmp_path / "absent.json")

    def test_zcap_pinned_reader_schema_drift_extra_field(self, tmp_path: Path) -> None:
        """Extra top-level field surfaces as SchemaMismatchError."""
        target = tmp_path / "Z_cap_pinned.json"
        payload = {
            "Z_cop_per_month": 100.0,
            "ci_95_lo": 90.0,
            "ci_95_hi": 110.0,
            "audit_block": "0" * 64,
            "tier_mix": {"pro": 0.2, "max_5x": 0.5, "max_20x": 0.3},
            "schema_version": "v1.0",
            "rogue_extra": "nope",
        }
        target.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(SchemaMismatchError, match="extra"):
            ZCapPinnedReader()(target)

    def test_zcap_pinned_reader_top_level_must_be_object(self, tmp_path: Path) -> None:
        """A JSON list at top level is rejected with SchemaMismatchError."""
        target = tmp_path / "Z_cap_pinned.json"
        target.write_text(json.dumps(["nope"]), encoding="utf-8")
        with pytest.raises(SchemaMismatchError, match="object"):
            ZCapPinnedReader()(target)

    def test_zcap_pinned_reader_tier_mix_drift(self, tmp_path: Path) -> None:
        """tier_mix with wrong keys surfaces as SchemaMismatchError."""
        target = tmp_path / "Z_cap_pinned.json"
        payload = {
            "Z_cop_per_month": 100.0,
            "ci_95_lo": 90.0,
            "ci_95_hi": 110.0,
            "audit_block": "0" * 64,
            "tier_mix": {"a": 0.5, "b": 0.5},
            "schema_version": "v1.0",
        }
        target.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(SchemaMismatchError, match="tier_mix"):
            ZCapPinnedReader()(target)


# ─── SAAS-COHORT-CLOSE Phase 4 — schema v1.0 → v1.1 backward-compat ──────────


def _zcap_v11_sample() -> ZCapPinned:
    """v1.1 ZCapPinned sample with a fully populated 5-tuple sign_verdicts.

    All five entries have ``ci_95_lo > 0`` so ``sign == "PASS"``;
    ``identity_residual ≤ 1e-6`` so ``identity_passes == True``.
    """
    labels: tuple[
        Literal["TP1"], Literal["TP2"], Literal["TP3"],
        Literal["TP4"], Literal["TP5"],
    ] = ("TP1", "TP2", "TP3", "TP4", "TP5")
    entries = tuple(
        SignVerdictEntry(
            label=lbl,
            z=100.0 + i,
            ci_95_lo=90.0 + i,
            ci_95_hi=110.0 + i,
            sign="PASS",
            identity_residual=1e-9,
            identity_passes=True,
        )
        for i, lbl in enumerate(labels)
    )
    return ZCapPinned(
        Z_cop_per_month=120_000.0,
        ci_95_lo=110_000.0,
        ci_95_hi=130_000.0,
        audit_block="c" * 64,
        tier_mix={"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30},
        schema_version=SCHEMA_VERSION_V1_1,
        sign_verdicts=entries,
    )


class TestZCapPinnedSchemaV11Backcompat:
    """Schema v1.0 ↔ v1.1 additive bump — round-trip + cross-version reads.

    Plan v0.2 SAAS-COHORT-CLOSE Phase 4 invariants:

    - v1.0 readers continue to work unchanged on v1.0 files.
    - v1.1 round-trip preserves all 5 sign_verdicts entries.
    - v1.0 file read by the (post-bump) reader yields ``sign_verdicts is None``.
    - v1.1 file read by the (post-bump) reader yields the 5-tuple.
    - A v1.0 ZCapPinned (sign_verdicts=None) writes a JSON file
      byte-equivalent to the pre-bump v1.0 emission (no extra field).
    """

    def test_v10_default_roundtrip_omits_sign_verdicts(self, tmp_path: Path) -> None:
        """v1.0 default ZCapPinned writes JSON without ``sign_verdicts`` key.

        Backward-compat invariant: v1.0 files emitted post-bump must be
        byte-identical to v1.0 files emitted pre-bump (additive
        semantics — no ghost field on disk).
        """
        target = tmp_path / "Z_cap_pinned.json"
        z = _zcap_sample()  # sign_verdicts=None default
        ZCapPinnedWriter()(z, target)
        on_disk = json.loads(target.read_text(encoding="utf-8"))
        assert "sign_verdicts" not in on_disk, (
            "v1.0 emission must NOT carry sign_verdicts on disk"
            " (additive semantics breach)"
        )
        recovered = ZCapPinnedReader()(target)
        assert recovered.sign_verdicts is None
        assert recovered.schema_version == DEFAULT_SCHEMA_VERSION
        assert recovered == z

    def test_v11_roundtrip_preserves_sign_verdicts(self, tmp_path: Path) -> None:
        """v1.1 ZCapPinned with 5-tuple sign_verdicts round-trips losslessly."""
        target = tmp_path / "Z_cap_pinned.json"
        z = _zcap_v11_sample()
        ZCapPinnedWriter()(z, target)
        recovered = ZCapPinnedReader()(target)
        assert recovered.schema_version == SCHEMA_VERSION_V1_1
        assert recovered.sign_verdicts is not None
        assert len(recovered.sign_verdicts) == 5
        # Frozen-dc equality (the field-by-field __eq__ generated by
        # @dataclass(frozen=True)) is the canonical equality.
        assert recovered == z

    def test_v11_emission_includes_sign_verdicts_on_disk(
        self, tmp_path: Path
    ) -> None:
        """v1.1 emission carries the ``sign_verdicts`` JSON array on disk."""
        target = tmp_path / "Z_cap_pinned.json"
        ZCapPinnedWriter()(_zcap_v11_sample(), target)
        on_disk = json.loads(target.read_text(encoding="utf-8"))
        assert "sign_verdicts" in on_disk
        assert isinstance(on_disk["sign_verdicts"], list)
        assert len(on_disk["sign_verdicts"]) == 5
        # Spot-check one entry's required field set.
        entry0 = on_disk["sign_verdicts"][0]
        for key in (
            "label",
            "z",
            "ci_95_lo",
            "ci_95_hi",
            "sign",
            "identity_residual",
            "identity_passes",
        ):
            assert key in entry0, f"v1.1 sign_verdicts entry missing {key!r}"

    def test_v10_file_read_by_post_bump_reader(self, tmp_path: Path) -> None:
        """A pre-bump-shaped v1.0 file (no ``sign_verdicts``) reads cleanly.

        Hand-crafted JSON with the v1.0 6-field shape — no
        ``sign_verdicts`` key. The post-bump reader must succeed and
        materialise ``sign_verdicts=None`` (backward-compat path).
        """
        target = tmp_path / "Z_cap_pinned.json"
        payload = {
            "Z_cop_per_month": 120_000.0,
            "ci_95_lo": 110_000.0,
            "ci_95_hi": 130_000.0,
            "audit_block": "d" * 64,
            "tier_mix": {"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30},
            "schema_version": "v1.0",
        }
        target.write_text(json.dumps(payload), encoding="utf-8")
        recovered = ZCapPinnedReader()(target)
        assert recovered.schema_version == "v1.0"
        assert recovered.sign_verdicts is None
        assert recovered.Z_cop_per_month == 120_000.0

    def test_v11_file_read_yields_sign_verdicts_tuple(self, tmp_path: Path) -> None:
        """A hand-crafted v1.1 JSON yields a 5-tuple of SignVerdictEntry."""
        target = tmp_path / "Z_cap_pinned.json"
        payload = {
            "Z_cop_per_month": 120_000.0,
            "ci_95_lo": 110_000.0,
            "ci_95_hi": 130_000.0,
            "audit_block": "e" * 64,
            "tier_mix": {"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30},
            "schema_version": "v1.1",
            "sign_verdicts": [
                {
                    "label": lbl,
                    "z": 100.0,
                    "ci_95_lo": 90.0,
                    "ci_95_hi": 110.0,
                    "sign": "PASS",
                    "identity_residual": 1e-9,
                    "identity_passes": True,
                }
                for lbl in ("TP1", "TP2", "TP3", "TP4", "TP5")
            ],
        }
        target.write_text(json.dumps(payload), encoding="utf-8")
        recovered = ZCapPinnedReader()(target)
        assert recovered.sign_verdicts is not None
        assert len(recovered.sign_verdicts) == 5
        assert {sv.label for sv in recovered.sign_verdicts} == {
            "TP1",
            "TP2",
            "TP3",
            "TP4",
            "TP5",
        }
        assert all(sv.sign == "PASS" for sv in recovered.sign_verdicts)
        assert all(sv.identity_passes for sv in recovered.sign_verdicts)

    def test_v10_caller_constructor_signature_unchanged(self) -> None:
        """v1.0 callers (5 args, no sign_verdicts) construct unchanged.

        Backward-compat: callers that never knew about ``sign_verdicts``
        must continue to construct ``ZCapPinned`` with the original
        positional/keyword signature.
        """
        z = ZCapPinned(
            Z_cop_per_month=100.0,
            ci_95_lo=90.0,
            ci_95_hi=110.0,
            audit_block="0" * 64,
            tier_mix={"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30},
        )
        assert z.sign_verdicts is None
        assert z.schema_version == DEFAULT_SCHEMA_VERSION

    def test_v11_rejects_wrong_count(self) -> None:
        """sign_verdicts must have exactly 5 entries (one per TP1..TP5)."""
        partial = (
            SignVerdictEntry(
                label="TP1",
                z=1.0,
                ci_95_lo=0.5,
                ci_95_hi=1.5,
                sign="PASS",
                identity_residual=0.0,
                identity_passes=True,
            ),
        )
        with pytest.raises(ValueError, match="exactly 5 entries"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=90.0,
                ci_95_hi=110.0,
                audit_block="0" * 64,
                sign_verdicts=partial,
            )

    def test_v11_rejects_duplicate_labels(self) -> None:
        """sign_verdicts labels must be exactly {TP1..TP5}; no duplicates."""
        # Five entries but TP1 repeated, TP5 missing — labels-set check.
        dup_labels: tuple[
            Literal["TP1"], Literal["TP2"], Literal["TP3"],
            Literal["TP4"], Literal["TP1"],
        ] = ("TP1", "TP2", "TP3", "TP4", "TP1")
        dup = tuple(
            SignVerdictEntry(
                label=lbl,
                z=1.0,
                ci_95_lo=0.5,
                ci_95_hi=1.5,
                sign="PASS",
                identity_residual=0.0,
                identity_passes=True,
            )
            for lbl in dup_labels
        )
        with pytest.raises(ValueError, match="labels must be exactly"):
            ZCapPinned(
                Z_cop_per_month=100.0,
                ci_95_lo=90.0,
                ci_95_hi=110.0,
                audit_block="0" * 64,
                sign_verdicts=dup,
            )


# ─── Audit-block sha256 helper ────────────────────────────────────────────────


class TestAuditBlock:
    def _make_files(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        a = tmp_path / "a.txt"
        b = tmp_path / "b.txt"
        c = tmp_path / "c.txt"
        a.write_bytes(b"alpha")
        b.write_bytes(b"beta")
        c.write_bytes(b"gamma")
        return a, b, c

    def test_compute_audit_block_returns_64_lowercase_hex(self, tmp_path: Path) -> None:
        """Output is a 64-char lowercase hex string."""
        a, _, _ = self._make_files(tmp_path)
        h = compute_audit_block([a])
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_compute_audit_block_path_order_invariant(self, tmp_path: Path) -> None:
        """Reordering input paths does not change the digest."""
        a, b, c = self._make_files(tmp_path)
        h1 = compute_audit_block([a, b, c])
        h2 = compute_audit_block([c, a, b])
        h3 = compute_audit_block([b, c, a])
        assert h1 == h2 == h3

    def test_compute_audit_block_str_or_path_mixed(self, tmp_path: Path) -> None:
        """Accepts a mixed list of str and Path inputs."""
        a, b, _ = self._make_files(tmp_path)
        h_str = compute_audit_block([str(a), str(b)])
        h_mixed = compute_audit_block([str(a), b])
        h_path = compute_audit_block([a, b])
        assert h_str == h_mixed == h_path

    def test_compute_audit_block_empty_raises(self) -> None:
        """Empty path list rejected."""
        with pytest.raises(ValueError, match="non-empty"):
            compute_audit_block([])

    def test_compute_audit_block_missing_file_raises(self, tmp_path: Path) -> None:
        """A non-existent path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not a regular file"):
            compute_audit_block([tmp_path / "absent.txt"])

    def test_compute_audit_block_content_sensitive(self, tmp_path: Path) -> None:
        """Mutating one byte changes the digest."""
        a = tmp_path / "a.txt"
        a.write_bytes(b"alpha")
        h0 = compute_audit_block([a])
        a.write_bytes(b"alphb")
        h1 = compute_audit_block([a])
        assert h0 != h1

    def test_audit_block_hasher_class_matches_function(self, tmp_path: Path) -> None:
        """AuditBlockHasher class delegates to compute_audit_block."""
        a, b, _ = self._make_files(tmp_path)
        free_hash = compute_audit_block([a, b])
        cls_hash = AuditBlockHasher()((a, b))
        assert free_hash == cls_hash

    def test_compute_audit_block_known_value(self, tmp_path: Path) -> None:
        """Single-file digest matches the documented stream-format."""
        a = tmp_path / "x.txt"
        a.write_bytes(b"hello")
        expected = hashlib.sha256(f"--- {a}\n".encode("utf-8") + b"hello").hexdigest()
        assert compute_audit_block([a]) == expected


# ─── Schema-set sanity (M4 column tuples are immutable & complete) ────────────


class TestM4Schemas:
    def test_cohort_prior_columns_present(self) -> None:
        """COHORT_PRIOR_COLUMNS contains the M4 spec §10 columns."""
        assert "param" in COHORT_PRIOR_COLUMNS
        assert "percentile" in COHORT_PRIOR_COLUMNS
        assert "value" in COHORT_PRIOR_COLUMNS
        assert "source" in COHORT_PRIOR_COLUMNS
        assert "fetched_at_utc" in COHORT_PRIOR_COLUMNS

    def test_synthetic_tau_columns_present(self) -> None:
        """SYNTHETIC_TAU_COLUMNS contains the M4 spec §10 columns."""
        for c in (
            "month",
            "simulation_id",
            "tier_id",
            "r",
            "p",
            "alpha",
            "x_m",
            "tau_t",
            "q_t_usd",
            "q_t_cop",
        ):
            assert c in SYNTHETIC_TAU_COLUMNS, f"missing column {c!r}"


# ─── Phase 3.5 — Pre-mortem regression tests ──────────────────────────────────
#
# Skill: pre-mortem. Pins documented intentional behaviors at IO boundaries.
# See scratch/2026-05-08-sim-infra-audit/pre_mortem_report.md for narratives.


class TestPreMortem:
    """Pre-mortem regression tests pinning IO boundary contracts."""

    def test_synthetic_tau_dtypes_pin_month_int64(self) -> None:
        """SYNTHETIC_TAU_DTYPES['month'] MUST be int64 — load-bearing for Hive.

        Pre-mortem #3. The astype(SYNTHETIC_TAU_DTYPES) step in
        SyntheticTauWriter is the only mechanism preventing
        ``month=4.0/`` Hive directories. Removing the int64 declaration
        (or the cast itself) would silently corrupt partition layout.
        This test surfaces ANY change to the load-bearing dtype constant.
        """
        from simulations.utils.parquet_io import SYNTHETIC_TAU_DTYPES

        assert SYNTHETIC_TAU_DTYPES["month"] == "int64", (
            "month dtype is load-bearing for Hive partition naming"
            " (month=4/ vs month=4.0/); changing it requires explicit"
            " migration review per pre-mortem #3."
        )
        assert SYNTHETIC_TAU_DTYPES["simulation_id"] == "int64", (
            "simulation_id dtype guards integer identity through pyarrow"
        )
        assert SYNTHETIC_TAU_DTYPES["tier_id"] == "string", (
            "tier_id dtype is load-bearing for Hive partition naming"
        )

    def test_zcap_pinned_reader_extra_field_is_not_pydantic_validation_error(
        self, tmp_path: Path
    ) -> None:
        """Extra-field drift surfaces as SchemaMismatchError, NOT pydantic ValidationError.

        Pre-mortem #4. The pre-Pydantic field-set check on lines 118–125
        of json_io.py runs BEFORE model_validate_json. A future refactor
        that reorders these would silently change the error type from
        SchemaMismatchError (subclass of ValueError) to
        pydantic.ValidationError, breaking ``except ValueError`` consumers.
        """
        import pydantic

        target = tmp_path / "Z_cap_pinned.json"
        payload = {
            "Z_cop_per_month": 100.0,
            "ci_95_lo": 90.0,
            "ci_95_hi": 110.0,
            "audit_block": "0" * 64,
            "tier_mix": {"pro": 0.2, "max_5x": 0.5, "max_20x": 0.3},
            "schema_version": "v1.0",
            "rogue_extra": "nope",
        }
        target.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(SchemaMismatchError) as exc_info:
            ZCapPinnedReader()(target)
        # Critical contract: must NOT be a pydantic.ValidationError.
        assert not isinstance(exc_info.value, pydantic.ValidationError), (
            "ZCapPinnedReader extra-field path must surface as"
            " SchemaMismatchError (ValueError subclass), NOT"
            " pydantic.ValidationError. The pre-Pydantic check ordering"
            " is load-bearing — see pre-mortem #4."
        )
        # Also: SchemaMismatchError IS a ValueError (existing-consumer guarantee).
        assert isinstance(exc_info.value, ValueError)

    def test_compute_audit_block_path_form_matters(self, tmp_path: Path) -> None:
        """Relative vs absolute Path forms produce DIFFERENT digests.

        Pre-mortem #5. The path-sort key is ``str(p)`` and the hashed
        delimiter is ``f"--- {p}\\n"``, so two callers passing the same
        underlying file via different Path representations get different
        audit blocks. This test pins the documented (intentional)
        non-canonicalization behavior. A future change to canonicalize
        via ``Path.resolve()`` would deliberately fail this test, forcing
        a contract review.
        """
        a_abs = tmp_path / "x.txt"
        a_abs.write_bytes(b"hello")
        # Same file, accessed via a non-canonical relative-style path.
        a_rel = tmp_path / "." / "x.txt"
        h_abs = compute_audit_block([a_abs])
        # str(Path("./x.txt")) collapses to str(Path("x.txt")) — pathlib
        # normalizes leading "./". The real fragility is the
        # absolute-vs-cwd-relative path-string distinction, which we
        # exercise next:
        _ = compute_audit_block([a_rel])  # constructed but not asserted
        import os

        cwd_before = os.getcwd()
        try:
            os.chdir(tmp_path)
            a_relative_str = Path("x.txt")  # relative to cwd
            h_relative = compute_audit_block([a_relative_str])
        finally:
            os.chdir(cwd_before)
        # Absolute and relative forms hash differently (path string is
        # embedded in the digest stream).
        assert h_abs != h_relative, (
            "compute_audit_block must remain path-string-sensitive;"
            " a change to canonicalize via Path.resolve() requires"
            " explicit contract review per pre-mortem #5."
        )



class TestIdempotentWrite:
    """Defensive Pattern-4 mutation tests: writing the same payload twice
    to the same target must not raise.

    Catches mutmut Pattern-4 mutations that drop ``exist_ok=True`` from the
    writers' ``mkdir`` (or otherwise make rewrites non-idempotent). The
    first call creates the target; the second call must overwrite cleanly.
    """

    def test_synthetic_tau_writer_idempotent_rewrite(self, tmp_path: Path) -> None:
        """SyntheticTauWriter overwrites an existing tier_id partition cleanly."""
        writer = SyntheticTauWriter(base_dir=tmp_path)
        rows = [
            synthetic_tau_row(
                month=1,
                simulation_id=0,
                tier_id="pro",
                r=1.0,
                p=0.5,
                alpha=2.0,
                x_m=1.0,
                tau_t=10.0,
                q_t_usd=1.0,
                q_t_cop=4000.0,
            )
        ]
        writer(rows)
        # Second write of same data must succeed (idempotent), not raise.
        writer(rows)
        # Read-back sanity: the partition still resolves and contains the row.
        recovered = SyntheticTauReader(base_dir=tmp_path)()
        assert len(recovered) >= 1

    def test_cohort_prior_writer_idempotent_rewrite(self, tmp_path: Path) -> None:
        """CohortPriorWriter overwrites an existing cohort_prior.parquet cleanly."""
        writer = CohortPriorWriter(base_dir=tmp_path)
        rows = [
            cohort_prior_row(
                param="alpha",
                percentile="p50",
                value=2.0,
                source="test",
                fetched_at_utc="2026-01-01T00:00:00Z",
            )
        ]
        writer(rows)
        # Second write must succeed without raising (idempotent overwrite).
        writer(rows)
        recovered = CohortPriorReader(base_dir=tmp_path)()
        assert len(recovered) == 1


# ─── Static pricing fetcher (spec §5.2 frozen-table emitter) ──────────────────


class TestStaticPricingFetcher:
    """Cover the pricing-table emitter: row count, schema-shape, and timestamp pinning."""

    def test_emits_six_rows(self) -> None:
        """Spec §5.2 declares 6 prices: in/out × {Sonnet, Opus, Haiku}."""
        rows = StaticPricingFetcher()()
        assert len(rows) == 6

    def test_emits_distinct_param_names(self) -> None:
        """Each row has a distinct ``param`` — no accidental key collisions."""
        rows = StaticPricingFetcher()()
        params = [r["param"] for r in rows]
        assert len(set(params)) == 6
        # Spot-check that all six expected names are present.
        expected = {
            "sonnet_price_in_usd_per_mtok",
            "sonnet_price_out_usd_per_mtok",
            "opus_price_in_usd_per_mtok",
            "opus_price_out_usd_per_mtok",
            "haiku_price_in_usd_per_mtok",
            "haiku_price_out_usd_per_mtok",
        }
        assert set(params) == expected

    def test_emits_positive_finite_prices(self) -> None:
        """All emitted prices must be positive finite floats."""
        rows = StaticPricingFetcher()()
        for r in rows:
            assert r["value"] > 0.0
            assert r["value"] < 1e6  # sanity ceiling

    def test_pricing_source_is_pinned(self) -> None:
        """Emitted ``source`` cites spec §5.2 — catches mutations to the citation string."""
        rows = StaticPricingFetcher()()
        for r in rows:
            src = r["source"]
            assert "5.2" in src, f"source citation drift: {src!r}"

    def test_percentile_label_is_p50(self) -> None:
        """Emitted ``percentile`` is the median label."""
        rows = StaticPricingFetcher()()
        for r in rows:
            assert r["percentile"] == "P50"

    def test_explicit_timestamp_round_trips(self) -> None:
        """Constructor-supplied ``fetched_at_utc`` flows through unchanged."""
        ts = "2026-05-08T12:34:56+00:00"
        rows = StaticPricingFetcher(fetched_at_utc=ts)()
        for r in rows:
            assert r["fetched_at_utc"] == ts

    def test_default_timestamp_is_iso_utc(self) -> None:
        """Default-constructed fetcher emits an ISO-8601 second-precision UTC stamp."""
        rows = StaticPricingFetcher()()
        # All rows share the same construction-time stamp.
        stamps = {r["fetched_at_utc"] for r in rows}
        assert len(stamps) == 1
        ts = stamps.pop()
        # Second-precision: no microseconds.
        assert "." not in ts
        # UTC offset present.
        assert ts.endswith("+00:00") or ts.endswith("Z")

    def test_schema_version_is_default(self) -> None:
        """Emitted ``schema_version`` equals the canonical default."""
        rows = StaticPricingFetcher()()
        for r in rows:
            assert r["schema_version"] == DEFAULT_SCHEMA_VERSION

    def test_round_trip_via_cohort_prior_writer(self, tmp_path: Path) -> None:
        """Emitted rows survive a write-and-read round-trip through CohortPriorIO."""
        rows = StaticPricingFetcher()()
        CohortPriorWriter(base_dir=tmp_path)(rows)
        recovered = CohortPriorReader(base_dir=tmp_path)()
        assert len(recovered) == 6
        # Sort both sides by param to compare.
        rows_sorted = sorted(rows, key=lambda r: r["param"])
        recovered_sorted = sorted(recovered, key=lambda r: r["param"])
        for got, want in zip(recovered_sorted, rows_sorted):
            assert got == want

