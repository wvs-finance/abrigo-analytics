"""Phase-3 panel-construction tests (plan tasks 3.0 / 3.1 / 3.2 / 3.4).

Covers the common-differencing-grid pin (task 3.0), the X-side and Y-side
realized-variance constructors (3.1 / 3.2), the panel-cell assembly, and
the Tier-1 emit/read round-trip (3.4). Real-data-over-mocks: the
end-to-end panel test re-derives from the FROZEN Tier-2 central-bank FX
snapshots — the real pull, never a generated FX stand-in.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from simulations.e10_gsps._errors import DecompositionIdentityError
from simulations.e10_gsps.modules.differencing_grid import (
    assert_common_grid,
    verify_cell_grid,
)
from simulations.e10_gsps.modules.nhpp_engine import (
    NHPPSimulationEngineModule,
    calibrated_intensity_parameters,
)
from simulations.e10_gsps.modules.panel_construction import (
    build_panel_cell,
    verify_panel_grids,
)
from simulations.e10_gsps.modules.realized_variance import (
    build_cost_variance_cell,
    build_fx_variance_cell,
    daily_log_returns,
    population_variance,
    realized_variance_sum,
)
from simulations.e10_gsps.types import CostStreamTrajectory

REPO_ROOT = Path(__file__).resolve().parents[4]
FX_DIR = REPO_ROOT / "data" / "raw" / "e10_gsps" / "fx"


# ── Task 3.0 — common differencing grid ────────────────────────────────


def test_verify_cell_grid_accepts_aligned_indices() -> None:
    """X and Q on a common daily grid verify and yield n-1 log-returns."""
    report = verify_cell_grid(
        currency="COP",
        year=2025,
        month=3,
        fx_index_length=20,
        q_index_length=20,
    )
    assert report.aligned
    assert report.log_return_length == 19


def test_verify_cell_grid_rejects_mismatched_indices() -> None:
    """Mismatched X / Q daily indices raise — never a silent inexact grid."""
    with pytest.raises(DecompositionIdentityError):
        verify_cell_grid(
            currency="COP",
            year=2025,
            month=3,
            fx_index_length=20,
            q_index_length=18,
        )


def test_assert_common_grid_returns_shared_length() -> None:
    """assert_common_grid returns the common index length on a match."""
    assert assert_common_grid([1.0, 2.0, 3.0], [4.0, 5.0, 6.0]) == 3


def test_assert_common_grid_rejects_mismatch() -> None:
    with pytest.raises(DecompositionIdentityError):
        assert_common_grid([1.0, 2.0], [4.0, 5.0, 6.0])


# ── Task 3.1 / 3.2 — realized-variance constructors ────────────────────


def test_daily_log_returns_length_is_n_minus_one() -> None:
    """A length-n level series yields n-1 daily log-returns."""
    returns = daily_log_returns([100.0, 110.0, 99.0, 105.0])
    assert len(returns) == 3
    assert math.isclose(returns[0], math.log(110.0 / 100.0))


def test_daily_log_returns_rejects_non_positive_level() -> None:
    """A zero or negative level has an undefined log-return."""
    with pytest.raises(ValueError):
        daily_log_returns([100.0, 0.0, 105.0])


def test_realized_variance_sum_is_sum_of_squares() -> None:
    """The spec-§3.2 realized variance is the sum of squared returns."""
    rv = realized_variance_sum([0.1, -0.2, 0.05])
    assert math.isclose(rv, 0.1**2 + 0.2**2 + 0.05**2)


def test_population_variance_additive_identity() -> None:
    """Var(a+b) = Var a + Var b + 2Cov — the §4.2 operator property."""
    a = [0.01, -0.02, 0.03, -0.01]
    b = [0.02, 0.01, -0.02, 0.0]
    s = [x + y for x, y in zip(a, b, strict=True)]
    var_a = population_variance(a)
    var_b = population_variance(b)
    var_s = population_variance(s)
    n = len(a)
    mean_a, mean_b = sum(a) / n, sum(b) / n
    cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b, strict=True)) / n
    assert math.isclose(var_s, var_a + var_b + 2.0 * cov, abs_tol=1e-15)


def test_build_fx_variance_cell_carries_sum_convention() -> None:
    """The X-side cell carries the §3.2 sum-of-squares realized variance."""
    cell = build_fx_variance_cell(
        currency="COP",
        year=2025,
        month=3,
        daily_fx_level=[4000.0, 4040.0, 3990.0, 4010.0],
        qualifying=True,
    )
    expected = realized_variance_sum(
        daily_log_returns([4000.0, 4040.0, 3990.0, 4010.0])
    )
    assert math.isclose(cell.realized_log_variance, expected)
    assert cell.n_trading_days == 4


def test_build_cost_variance_cell_from_trajectory() -> None:
    """The Y-side cell is the realized variance of Δlog(cost)."""
    traj = CostStreamTrajectory(
        currency="COP",
        year=2025,
        month=3,
        daily_query_counts=(100, 120, 90, 110),
        daily_fx_rate=(4000.0, 4040.0, 3990.0, 4010.0),
        daily_cost=tuple(
            q * 0.01 * fx
            for q, fx in zip((100, 120, 90, 110),
                             (4000.0, 4040.0, 3990.0, 4010.0), strict=True)
        ),
        seed=7,
    )
    cell = build_cost_variance_cell(traj)
    assert cell.realized_log_variance > 0.0
    assert cell.n_trading_days == 4


# ── Panel-cell assembly ────────────────────────────────────────────────


def test_panel_cell_drops_zero_query_days_and_holds_identity() -> None:
    """A cell with zero-Q days drops them; the §4.2 identity holds exactly
    on the surviving positive-Q common grid."""
    fx_cell = build_fx_variance_cell(
        currency="COP",
        year=2025,
        month=3,
        daily_fx_level=[4000.0, 4040.0, 3990.0, 4010.0, 4025.0, 3995.0],
        qualifying=True,
    )
    # Days 2 and 5 (0-indexed 1, 4) carry zero queries.
    counts = (100, 0, 90, 110, 0, 95)
    fx = (4000.0, 4040.0, 3990.0, 4010.0, 4025.0, 3995.0)
    traj = CostStreamTrajectory(
        currency="COP",
        year=2025,
        month=3,
        daily_query_counts=counts,
        daily_fx_rate=fx,
        daily_cost=tuple(q * 0.01 * f for q, f in zip(counts, fx, strict=True)),
        seed=7,
    )
    cell = build_panel_cell(fx_cell, traj)
    assert not cell.material_gap
    assert cell.n_surviving_days == 4  # 6 days minus 2 zero-Q days
    d = cell.decomposition
    residual = d.var_total - (d.var_fx + d.var_q + d.cov_term)
    assert abs(residual) < 1e-12
    assert abs(d.identity_residual) < 1e-12


def test_panel_cell_flags_material_gap_when_too_few_surviving_days() -> None:
    """A cell with fewer than two positive-Q days cannot be log-differenced
    and carries material_gap=True."""
    fx_cell = build_fx_variance_cell(
        currency="COP",
        year=2025,
        month=3,
        daily_fx_level=[4000.0, 4040.0, 3990.0],
        qualifying=True,
    )
    counts = (100, 0, 0)  # only one positive-Q day
    fx = (4000.0, 4040.0, 3990.0)
    traj = CostStreamTrajectory(
        currency="COP",
        year=2025,
        month=3,
        daily_query_counts=counts,
        daily_fx_rate=fx,
        daily_cost=tuple(q * 0.01 * f for q, f in zip(counts, fx, strict=True)),
        seed=7,
    )
    cell = build_panel_cell(fx_cell, traj)
    assert cell.material_gap
    assert math.isnan(cell.fx_variance_share)


def test_verify_panel_grids_emits_one_report_per_cell() -> None:
    """The task-3.0 verification artifact has one aligned report per cell."""
    fx_cell = build_fx_variance_cell(
        currency="COP",
        year=2025,
        month=3,
        daily_fx_level=[4000.0, 4040.0, 3990.0, 4010.0],
        qualifying=True,
    )
    fx = (4000.0, 4040.0, 3990.0, 4010.0)
    traj = CostStreamTrajectory(
        currency="COP",
        year=2025,
        month=3,
        daily_query_counts=(100, 120, 90, 110),
        daily_fx_rate=fx,
        daily_cost=tuple(q * 0.01 * f for q, f in zip((100, 120, 90, 110), fx, strict=True)),
        seed=7,
    )
    reports = verify_panel_grids([(fx_cell, traj)])
    assert len(reports) == 1
    assert reports[0].aligned


# ── End-to-end — real frozen Tier-2 FX (real-data-over-mocks) ──────────


@pytest.mark.skipif(
    not FX_DIR.exists() or not list(FX_DIR.glob("*.raw")),
    reason="frozen Tier-2 FX snapshots not present",
)
def test_full_panel_identity_holds_exactly_on_real_data() -> None:
    """The exact §4.2 identity holds for EVERY cell of the real
    5-currency × ~30-month panel re-derived from frozen Tier-2 FX."""
    from collections import defaultdict

    from simulations.e10_gsps.modules.regime_break import (
        confine_to_float_regime,
    )
    from simulations.e10_gsps.types import PANEL_CURRENCIES
    from simulations.e10_gsps.types.fx import CurrencyDailyFXRow
    from simulations.e10_gsps.utils.fx_ingest_io import (
        _parse_currency_payload,
    )

    params = calibrated_intensity_parameters()
    engine = NHPPSimulationEngineModule(params)
    n_cells = 0
    for currency in PANEL_CURRENCIES:
        snaps = sorted(FX_DIR.glob(f"fx_{currency}.*.raw"))
        rows = _parse_currency_payload(
            currency, snaps[-1].read_bytes(), "2023-11-01", "2026-04-30"
        )
        rows = confine_to_float_regime(rows, currency=currency)
        by_month: dict[tuple[int, int], list[CurrencyDailyFXRow]] = (
            defaultdict(list)
        )
        for r in rows:
            by_month[(r.observation_date.year, r.observation_date.month)].append(r)
        for (year, month), mrows in sorted(by_month.items()):
            mrows.sort(key=lambda r: r.observation_date)
            fx_levels = tuple(r.fx_rate for r in mrows)
            fx_cell = build_fx_variance_cell(
                currency=currency,
                year=year,
                month=month,
                daily_fx_level=fx_levels,
                qualifying=all(r.post_regime_break for r in mrows),
            )
            traj = engine(params, currency, year, month, fx_levels)
            cell = build_panel_cell(fx_cell, traj)
            n_cells += 1
            if not cell.material_gap:
                d = cell.decomposition
                residual = d.var_total - (d.var_fx + d.var_q + d.cov_term)
                assert abs(residual) < 1e-9, (
                    f"{currency} {year}-{month}: identity residual {residual}"
                )
    assert n_cells == 150
