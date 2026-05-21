"""Tier-1 panel emit/read IO boundary — E10 GSPS panel (plan task 3.4).

IO Boundary tier — mutable state (the parquet path) lives ONLY here, per
the CLAUDE.md three-tier discipline. The callable / value tiers never
hold IO state.

What this unit does
-------------------
Emits the assembled 5-currency × ~30-month E10 panel (the per-cell X, Y,
and exact §4.2 three-way log-variance decomposition — ``PanelCell``
records) to a Tier-1 parquet, and reads it back to typed ``PanelCell``
containers. The parquet column schema is fixed and declared here; a
``TypedDict`` row schema validates each row at the IO boundary before
conversion to a typed Value container.

Round-trip tolerance (plan task 3.4 / CORR-E10P-7)
--------------------------------------------------
- The real FX panel cells (``x_realized_variance``) re-derive **bit-exact**
  from the frozen Tier-2 FX snapshots.
- The fixed-seed simulator-derived cells (``y_realized_variance`` and the
  decomposition terms) re-derive within a **1e-9 relative tolerance** — the
  NHPP engine is referentially transparent in ``(currency, year, month)``
  via its deterministic per-cell seed, so the only divergence is
  floating-point summation order.

Discipline
----------
The numeric FX values written are 100% real central-bank data
(fantasy-firewall enforced); Q is the only simulated quantity.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Final, TypedDict

import pyarrow as pa
import pyarrow.parquet as pq

from simulations.e10_gsps.types import PanelCell, ThreeWayDecompositionCell

#: Tier-1 E10 panel parquet columns, in emission order.
PANEL_COLUMNS: Final[tuple[str, ...]] = (
    "currency",
    "year",
    "month",
    "x_realized_variance",
    "y_realized_variance",
    "var_total",
    "var_fx",
    "var_q",
    "cov_term",
    "fx_variance_share",
    "identity_residual",
    "grid_index_length",
    "n_fx_trading_days",
    "n_surviving_days",
    "material_gap",
    "qualifying",
    "seed",
)

#: Parquet schema version — bump on any column-set change.
PANEL_SCHEMA_VERSION: Final[str] = "e10-gsps-panel-v1"


class PanelRow(TypedDict):
    """One row of the Tier-1 E10 panel parquet — the IO-boundary schema.

    Validated at read time before conversion to a typed ``PanelCell``.
    """

    currency: str
    year: int
    month: int
    x_realized_variance: float
    y_realized_variance: float
    var_total: float
    var_fx: float
    var_q: float
    cov_term: float
    fx_variance_share: float
    identity_residual: float
    grid_index_length: int
    n_fx_trading_days: int
    n_surviving_days: int
    material_gap: bool
    qualifying: bool
    seed: int


def _cell_to_row(cell: PanelCell) -> PanelRow:
    """Flatten one ``PanelCell`` into a Tier-1 panel row."""
    d = cell.decomposition
    return PanelRow(
        currency=cell.currency,
        year=cell.year,
        month=cell.month,
        x_realized_variance=cell.x_realized_variance,
        y_realized_variance=cell.y_realized_variance,
        var_total=d.var_total,
        var_fx=d.var_fx,
        var_q=d.var_q,
        cov_term=d.cov_term,
        fx_variance_share=cell.fx_variance_share,
        identity_residual=d.identity_residual,
        grid_index_length=d.grid_index_length,
        n_fx_trading_days=cell.n_fx_trading_days,
        n_surviving_days=cell.n_surviving_days,
        material_gap=cell.material_gap,
        qualifying=cell.qualifying,
        seed=cell.seed,
    )


def _row_to_cell(row: PanelRow) -> PanelCell:
    """Reconstruct a typed ``PanelCell`` from a validated panel row."""
    decomposition = ThreeWayDecompositionCell(
        currency=row["currency"],
        year=row["year"],
        month=row["month"],
        var_total=row["var_total"],
        var_fx=row["var_fx"],
        var_q=row["var_q"],
        cov_term=row["cov_term"],
        grid_index_length=row["grid_index_length"],
        identity_residual=row["identity_residual"],
    )
    return PanelCell(
        currency=row["currency"],
        year=row["year"],
        month=row["month"],
        x_realized_variance=row["x_realized_variance"],
        y_realized_variance=row["y_realized_variance"],
        decomposition=decomposition,
        n_fx_trading_days=row["n_fx_trading_days"],
        n_surviving_days=row["n_surviving_days"],
        material_gap=row["material_gap"],
        fx_variance_share=row["fx_variance_share"],
        qualifying=row["qualifying"],
        seed=row["seed"],
    )


class PanelParquetIO:
    """Tier-1 E10 panel emit/read IO-boundary unit (plan task 3.4).

    Mutable state — the parquet path — is confined to this IO-boundary
    class.
    """

    def __init__(self, panel_path: Path) -> None:
        """Initialise the panel IO unit.

        Args:
            panel_path: Filesystem path of the Tier-1 panel parquet. The
                parent directory is created on emit if absent.
        """
        self._panel_path: Path = Path(panel_path)

    @property
    def panel_path(self) -> Path:
        """The Tier-1 panel parquet path."""
        return self._panel_path

    def emit(self, cells: Sequence[PanelCell]) -> Path:
        """Emit the assembled panel to the Tier-1 parquet.

        Cells are written in a deterministic (currency, year, month) order
        so the parquet is byte-stable across runs given identical inputs.

        Args:
            cells: The assembled ``PanelCell`` records.

        Returns:
            The path the panel parquet was written to.
        """
        self._panel_path.parent.mkdir(parents=True, exist_ok=True)
        ordered = sorted(
            cells, key=lambda c: (c.currency, c.year, c.month)
        )
        rows = [_cell_to_row(c) for c in ordered]
        table = pa.Table.from_pylist(
            [dict(r) for r in rows],
            schema=_arrow_schema(),
        ).replace_schema_metadata(
            {b"schema_version": PANEL_SCHEMA_VERSION.encode("utf-8")}
        )
        pq.write_table(table, self._panel_path)
        return self._panel_path

    def read(self) -> tuple[PanelCell, ...]:
        """Read the Tier-1 panel parquet back to typed ``PanelCell``s.

        Returns:
            The panel cells in (currency, year, month) order.

        Raises:
            FileNotFoundError: the panel parquet does not exist.
            ValueError: the parquet column set does not match
                ``PANEL_COLUMNS`` — a schema drift the read never
                silently tolerates.
        """
        if not self._panel_path.exists():
            raise FileNotFoundError(
                f"E10 panel parquet not found at {self._panel_path}; "
                f"run scripts/build_e10_gsps_panel.py first."
            )
        table = pq.read_table(self._panel_path)
        if tuple(table.column_names) != PANEL_COLUMNS:
            raise ValueError(
                f"E10 panel parquet column drift: expected {PANEL_COLUMNS}, "
                f"got {tuple(table.column_names)}."
            )
        rows: list[PanelRow] = [
            PanelRow(**record)  # type: ignore[typeddict-item]
            for record in table.to_pylist()
        ]
        return tuple(_row_to_cell(r) for r in rows)


def _arrow_schema() -> pa.Schema:
    """The fixed Arrow schema for the Tier-1 E10 panel parquet."""
    return pa.schema(
        [
            ("currency", pa.string()),
            ("year", pa.int32()),
            ("month", pa.int32()),
            ("x_realized_variance", pa.float64()),
            ("y_realized_variance", pa.float64()),
            ("var_total", pa.float64()),
            ("var_fx", pa.float64()),
            ("var_q", pa.float64()),
            ("cov_term", pa.float64()),
            ("fx_variance_share", pa.float64()),
            ("identity_residual", pa.float64()),
            ("grid_index_length", pa.int32()),
            ("n_fx_trading_days", pa.int32()),
            ("n_surviving_days", pa.int32()),
            ("material_gap", pa.bool_()),
            ("qualifying", pa.bool_()),
            ("seed", pa.int64()),
        ]
    )


__all__ = [
    "PANEL_COLUMNS",
    "PANEL_SCHEMA_VERSION",
    "PanelParquetIO",
    "PanelRow",
]
