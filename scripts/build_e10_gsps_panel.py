#!/usr/bin/env python3
"""Tier-3 builder — re-derive the E10 GSPS panel from Tier-2 frozen snapshots.

Plan v0.2 Phase 3 task 3.4. Two modes:

    python scripts/build_e10_gsps_panel.py                    # build
    python scripts/build_e10_gsps_panel.py --verify-against-tier1

The build:

1. Reads the 5 frozen Tier-2 central-bank FX snapshots
   (``data/raw/e10_gsps/fx/fx_<CUR>.<ts>.raw``) — real FX, 100% offline.
2. Applies the spec-§3.3 regime-break screen (NGN confined to its
   post-June-2023 float).
3. Builds the X-side FX realized-variance cells (spec §3.2).
4. Runs the fixed-seed R6 NHPP simulator against each cell's real FX path
   to produce the cost-stream trajectory (Q is the only simulated
   quantity; the seed is derived deterministically per (currency, month)).
5. Assembles the per-cell panel — X, Y, and the exact §4.2 three-way
   log-variance decomposition — on the plan-task-3.0 common daily grid.
6. Emits the Tier-1 panel parquet to ``data/panels/e10_gsps_panel.parquet``.

In ``--verify-against-tier1`` mode the panel is re-derived in memory and
compared cell-by-cell to the on-disk Tier-1 parquet (plan CORR-E10P-7):

- ``x_realized_variance`` — bit-exact (the real FX panel cell).
- The simulator-derived cells (``y_realized_variance``, the decomposition
  terms) — within a 1e-9 relative tolerance (fixed-seed determinism;
  the only divergence is floating-point summation order).

Any mismatch is fatal (exit 1) — this is the canonical Tier-3
reproducibility check (HALT if the round-trip fails, plan §3).
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from simulations.e10_gsps.modules.nhpp_engine import (  # noqa: E402
    NHPPSimulationEngineModule,
    calibrated_intensity_parameters,
)
from simulations.e10_gsps.modules.panel_construction import (  # noqa: E402
    PanelCell,
    build_panel_cell,
)
from simulations.e10_gsps.modules.realized_variance import (  # noqa: E402
    build_fx_variance_cell,
)
from simulations.e10_gsps.modules.regime_break import (  # noqa: E402
    confine_to_float_regime,
)
from simulations.e10_gsps.types import PANEL_CURRENCIES  # noqa: E402
from simulations.e10_gsps.types.fx import CurrencyDailyFXRow  # noqa: E402
from simulations.e10_gsps.utils.fx_ingest_io import (  # noqa: E402
    _parse_currency_payload,
)
from simulations.e10_gsps.utils.panel_io import PanelParquetIO  # noqa: E402

FX_SNAPSHOT_DIR = REPO_ROOT / "data" / "raw" / "e10_gsps" / "fx"
PANEL_PATH = REPO_ROOT / "data" / "panels" / "e10_gsps_panel.parquet"
WINDOW_START = "2023-11-01"
WINDOW_END = "2026-04-30"

# Tier-3 round-trip tolerances (plan CORR-E10P-7).
_REAL_FX_BIT_EXACT = True
_SIMULATOR_REL_TOL = 1e-9


def _latest_snapshot(currency: str) -> Path:
    """Return the frozen Tier-2 FX snapshot for ``currency``.

    Raises:
        FileNotFoundError: no snapshot exists for the currency.
    """
    snaps = sorted(FX_SNAPSHOT_DIR.glob(f"fx_{currency}.*.raw"))
    if not snaps:
        raise FileNotFoundError(
            f"no frozen Tier-2 FX snapshot for {currency} under "
            f"{FX_SNAPSHOT_DIR}; run the Phase-1 FX ingest first."
        )
    return snaps[-1]


def _load_currency_rows(currency: str) -> tuple[CurrencyDailyFXRow, ...]:
    """Parse one currency's frozen Tier-2 snapshot, regime-screened."""
    body = _latest_snapshot(currency).read_bytes()
    rows = _parse_currency_payload(currency, body, WINDOW_START, WINDOW_END)
    return confine_to_float_regime(rows, currency=currency)


def build_panel() -> tuple[PanelCell, ...]:
    """Re-derive the full 5-currency × ~30-month E10 panel from Tier-2."""
    params = calibrated_intensity_parameters()
    engine = NHPPSimulationEngineModule(params)
    cells: list[PanelCell] = []

    for currency in PANEL_CURRENCIES:
        rows = _load_currency_rows(currency)
        by_month: dict[tuple[int, int], list[CurrencyDailyFXRow]] = (
            defaultdict(list)
        )
        for r in rows:
            by_month[(r.observation_date.year, r.observation_date.month)].append(r)

        for (year, month), month_rows in sorted(by_month.items()):
            month_rows.sort(key=lambda r: r.observation_date)
            fx_levels = tuple(r.fx_rate for r in month_rows)
            qualifying = all(r.post_regime_break for r in month_rows)

            fx_cell = build_fx_variance_cell(
                currency=currency,
                year=year,
                month=month,
                daily_fx_level=fx_levels,
                qualifying=qualifying,
            )
            trajectory = engine(params, currency, year, month, fx_levels)
            cells.append(build_panel_cell(fx_cell, trajectory))

    return tuple(cells)


def _rel_close(a: float, b: float, *, tol: float) -> bool:
    """Relative-tolerance float comparison; NaN == NaN; exact-zero match."""
    if math.isnan(a) and math.isnan(b):
        return True
    if a == b:
        return True
    scale = max(abs(a), abs(b), 1.0)
    return abs(a - b) <= tol * scale


def _verify(rebuilt: tuple[PanelCell, ...]) -> int:
    """Compare a freshly-rebuilt panel to the on-disk Tier-1 parquet.

    Returns 0 on a clean round-trip, 1 on any mismatch.
    """
    io = PanelParquetIO(PANEL_PATH)
    on_disk = {(c.currency, c.year, c.month): c for c in io.read()}
    fresh = {(c.currency, c.year, c.month): c for c in rebuilt}

    if on_disk.keys() != fresh.keys():
        print(
            "Tier-3 round-trip FAIL — cell-key set mismatch between the "
            "on-disk Tier-1 panel and the re-derived panel.",
            file=sys.stderr,
        )
        return 1

    mismatches: list[str] = []
    for key, fresh_cell in fresh.items():
        disk_cell = on_disk[key]
        cur, yr, mo = key
        tag = f"{cur} {yr}-{mo:02d}"

        # Real FX panel cell — bit-exact (CORR-E10P-7).
        if _REAL_FX_BIT_EXACT and (
            fresh_cell.x_realized_variance != disk_cell.x_realized_variance
        ):
            mismatches.append(
                f"{tag}: x_realized_variance not bit-exact "
                f"({fresh_cell.x_realized_variance!r} vs "
                f"{disk_cell.x_realized_variance!r})"
            )

        # Simulator-derived cells — 1e-9 relative tolerance.
        for name, fv, dv in (
            ("y_realized_variance",
             fresh_cell.y_realized_variance,
             disk_cell.y_realized_variance),
            ("var_total",
             fresh_cell.decomposition.var_total,
             disk_cell.decomposition.var_total),
            ("var_fx",
             fresh_cell.decomposition.var_fx,
             disk_cell.decomposition.var_fx),
            ("var_q",
             fresh_cell.decomposition.var_q,
             disk_cell.decomposition.var_q),
            ("cov_term",
             fresh_cell.decomposition.cov_term,
             disk_cell.decomposition.cov_term),
            ("fx_variance_share",
             fresh_cell.fx_variance_share,
             disk_cell.fx_variance_share),
        ):
            if not _rel_close(fv, dv, tol=_SIMULATOR_REL_TOL):
                mismatches.append(
                    f"{tag}: {name} outside 1e-9 rel-tol "
                    f"({fv!r} vs {dv!r})"
                )

    if mismatches:
        print(
            f"Tier-3 round-trip FAIL — {len(mismatches)} cell mismatch(es):",
            file=sys.stderr,
        )
        for m in mismatches[:30]:
            print(f"  {m}", file=sys.stderr)
        return 1

    print(  # CHECK_ALLOWLIST: Tier-3 reproducibility status, not a beta verdict
        f"Tier-3 round-trip OK — {len(fresh)} cells re-derive Tier-1 "
        f"within tolerance (FX bit-exact; simulator cells 1e-9 rel-tol)."
    )
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Tier-3 builder for the E10 GSPS panel."
    )
    parser.add_argument(
        "--verify-against-tier1",
        action="store_true",
        help="re-derive and hash-check against the on-disk Tier-1 panel",
    )
    args = parser.parse_args(argv[1:])

    rebuilt = build_panel()

    if args.verify_against_tier1:
        return _verify(rebuilt)

    io = PanelParquetIO(PANEL_PATH)
    out = io.emit(rebuilt)
    n_gap = sum(1 for c in rebuilt if c.material_gap)
    print(
        f"E10 GSPS panel emitted — {len(rebuilt)} cells "
        f"({n_gap} material-gap) → {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
