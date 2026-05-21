"""Phase-3 Tier-1 panel emit/read tests (plan task 3.4).

Exercises the ``PanelParquetIO`` round-trip: an assembled panel emitted
to parquet and read back must reconstruct the typed ``PanelCell``s
exactly. Schema-drift detection is verified too.
"""

from __future__ import annotations

import math
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from simulations.e10_gsps.modules.panel_construction import build_panel_cell
from simulations.e10_gsps.modules.realized_variance import (
    build_fx_variance_cell,
)
from simulations.e10_gsps.types import CostStreamTrajectory
from simulations.e10_gsps.utils.panel_io import PANEL_COLUMNS, PanelParquetIO


def _sample_cell() -> object:
    fx_cell = build_fx_variance_cell(
        currency="COP",
        year=2025,
        month=3,
        daily_fx_level=[4000.0, 4040.0, 3990.0, 4010.0],
        qualifying=True,
    )
    fx = (4000.0, 4040.0, 3990.0, 4010.0)
    counts = (100, 120, 90, 110)
    traj = CostStreamTrajectory(
        currency="COP",
        year=2025,
        month=3,
        daily_query_counts=counts,
        daily_fx_rate=fx,
        daily_cost=tuple(q * 0.01 * f for q, f in zip(counts, fx, strict=True)),
        seed=4242,
    )
    return build_panel_cell(fx_cell, traj)


def test_emit_read_round_trip_preserves_cell(tmp_path: Path) -> None:
    """A panel cell survives the emit → read round-trip exactly."""
    cell = _sample_cell()
    io = PanelParquetIO(tmp_path / "panel.parquet")
    io.emit([cell])
    back = io.read()
    assert len(back) == 1
    r = back[0]
    assert r.currency == cell.currency
    assert r.year == cell.year and r.month == cell.month
    assert math.isclose(r.x_realized_variance, cell.x_realized_variance)
    assert math.isclose(r.y_realized_variance, cell.y_realized_variance)
    assert math.isclose(
        r.decomposition.var_total, cell.decomposition.var_total
    )
    assert math.isclose(r.fx_variance_share, cell.fx_variance_share)
    assert r.material_gap == cell.material_gap
    assert r.seed == cell.seed


def test_emit_writes_declared_column_schema(tmp_path: Path) -> None:
    """The emitted parquet carries exactly the declared column set."""
    io = PanelParquetIO(tmp_path / "panel.parquet")
    io.emit([_sample_cell()])
    table = pq.read_table(tmp_path / "panel.parquet")
    assert tuple(table.column_names) == PANEL_COLUMNS


def test_read_rejects_column_drift(tmp_path: Path) -> None:
    """A parquet whose column set differs from the schema is rejected."""
    bad = tmp_path / "panel.parquet"
    pq.write_table(
        pa.table({"currency": ["COP"], "unexpected": [1]}), bad
    )
    io = PanelParquetIO(bad)
    with pytest.raises(ValueError, match="column drift"):
        io.read()


def test_read_missing_parquet_raises(tmp_path: Path) -> None:
    io = PanelParquetIO(tmp_path / "absent.parquet")
    with pytest.raises(FileNotFoundError):
        io.read()
