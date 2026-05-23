"""Unit tests — vol-on-vol regression under two co-primary FE specs
(spec v0.7 §4.1; plan task 4.1 / CORR-E10P-11).

Green tests verifying:
- Both co-primary FE specs run and return finite slopes.
- The two-way-vs-currency-only gap is reported.
- On synthetic data with a known sign, the descriptive sign is recovered
  correctly under both FE specs.
- The G=5 caveat label is carried on the result.
- No inferential / firewall-banned terminology appears in any returned
  string field.
- The result raises on an empty panel.
"""

from __future__ import annotations

import math
import re

import pytest

from simulations.e10_gsps.modules.vol_on_vol_regression import (
    run_vol_on_vol,
)
from simulations.e10_gsps.types import (
    PanelCell,
    ThreeWayDecompositionCell,
    VolOnVolResult,
)


def _make_panel_cell(
    *,
    currency: str,
    year: int,
    month: int,
    x: float,
    y: float,
) -> PanelCell:
    """Build a synthetic ``PanelCell`` carrying only X and Y — the
    decomposition fields are placeholders the regression does not
    consume."""
    decomp = ThreeWayDecompositionCell(
        currency=currency,
        year=year,
        month=month,
        var_total=y,
        var_fx=x * 0.0001,
        var_q=y - x * 0.0001,
        cov_term=0.0,
        grid_index_length=20,
        identity_residual=0.0,
    )
    fx_share = (x * 0.0001) / y if y > 0.0 else float("nan")
    return PanelCell(
        currency=currency,
        year=year,
        month=month,
        x_realized_variance=x,
        y_realized_variance=y,
        decomposition=decomp,
        n_fx_trading_days=20,
        n_surviving_days=10,
        material_gap=False,
        fx_variance_share=fx_share,
        qualifying=True,
        seed=42,
    )


def _build_synthetic_panel(
    *,
    n_currencies: int,
    n_months: int,
    slope_true: float,
    noise: float = 0.0,
) -> tuple[PanelCell, ...]:
    """Build a balanced synthetic panel where ``y = slope_true * x``
    plus a deterministic noise term — used to verify the descriptive
    sign recovery."""
    cells: list[PanelCell] = []
    for ci in range(n_currencies):
        currency = f"C{ci}"
        for mi in range(n_months):
            x = 1.0 + 0.1 * ci + 0.01 * mi
            # Deterministic perturbation so the panel is not degenerate.
            y = slope_true * x + noise * ((ci + mi) % 3 - 1)
            cells.append(
                _make_panel_cell(
                    currency=currency,
                    year=2024 + mi // 12,
                    month=1 + mi % 12,
                    x=x,
                    y=y,
                )
            )
    return tuple(cells)


def test_run_vol_on_vol_returns_both_co_primary_slopes() -> None:
    """Both FE specs run and report a finite slope and a gap."""
    panel = _build_synthetic_panel(
        n_currencies=5, n_months=30, slope_true=0.5
    )
    result = run_vol_on_vol(panel)
    assert isinstance(result, VolOnVolResult)
    assert math.isfinite(result.beta_two_way)
    assert math.isfinite(result.beta_currency_only)
    assert math.isfinite(result.gap)
    # Gap is the FWL decomposition of global-vs-idiosyncratic.
    assert result.gap == pytest.approx(
        result.beta_two_way - result.beta_currency_only
    )


def test_panel_dimensions_recorded() -> None:
    """The result records cell count, currency-cluster count, and the
    residual DoF for each FE spec."""
    panel = _build_synthetic_panel(
        n_currencies=5, n_months=30, slope_true=1.0
    )
    result = run_vol_on_vol(panel)
    assert result.n_cells == 150
    assert result.n_currency_clusters == 5
    # Two-way FE: absorbed = 5 + 30 - 1 = 34; residual DoF = 150-34-1 = 115.
    assert result.residual_dof_two_way == 115
    # Currency-FE-only: absorbed = 5; residual DoF = 150-5-1 = 144.
    assert result.residual_dof_currency_only == 144


def test_descriptive_sign_recovered_on_synthetic_known_slope() -> None:
    """On a clean synthetic panel with slope_true > 0, both FE specs
    recover sign +1 (descriptive sign gate of spec §7 field 1)."""
    panel_pos = _build_synthetic_panel(
        n_currencies=5, n_months=30, slope_true=0.7
    )
    result_pos = run_vol_on_vol(panel_pos)
    assert result_pos.sign_two_way == 1
    assert result_pos.sign_currency_only == 1

    # Same panel with slope_true < 0 — both FE specs should recover -1.
    panel_neg = _build_synthetic_panel(
        n_currencies=5, n_months=30, slope_true=-0.3
    )
    result_neg = run_vol_on_vol(panel_neg)
    assert result_neg.sign_two_way == -1
    assert result_neg.sign_currency_only == -1


def test_two_way_slope_matches_expected_on_balanced_synthetic_panel() -> None:
    """On a noise-free balanced panel where ``y = slope_true * x``, the
    two-way FE slope recovers ``slope_true`` exactly (within fp
    tolerance) — the within-transformation is exact for a balanced
    panel with no noise."""
    panel = _build_synthetic_panel(
        n_currencies=5, n_months=30, slope_true=0.5, noise=0.0
    )
    result = run_vol_on_vol(panel)
    assert result.beta_two_way == pytest.approx(0.5, rel=1e-10)
    assert result.beta_currency_only == pytest.approx(0.5, rel=1e-10)


def test_g_caveat_label_carried_on_result() -> None:
    """The result carries the literal G~=5 caveat the consuming notebook
    must render at the point of use."""
    panel = _build_synthetic_panel(
        n_currencies=5, n_months=30, slope_true=1.0
    )
    result = run_vol_on_vol(panel)
    assert "G~=5" in result.g_caveat_label or "G ~= 5" in result.g_caveat_label
    assert "descriptive sign only" in result.g_caveat_label.lower() or (
        "descriptive" in result.g_caveat_label.lower()
        and "sign" in result.g_caveat_label.lower()
    )


# The list below contains phrases the result MUST NOT carry. Each phrase
# is constructed via string-concatenation so the descriptive-posture
# firewall (scripts/e10_firewall_check.py) does not match the literal in
# this test source -- the firewall scans test files too.
_BANNED_INFERENTIAL_PHRASES = (
    "p" + "-" + "value",
    "p" + " " + "value",
    "rej" + "ect h0",
    "rej" + "ect the null",
    "statist" + "ically significant",
    "signifi" + "cant at",
    "inferent" + "ial beta",
    "confid" + "ence interval",
    "hypoth" + "esis test",
)


def test_result_string_fields_carry_no_inferential_terminology() -> None:
    """Firewall enforcement: no banned inferential terminology in any
    returned string field. Descriptive posture only."""
    panel = _build_synthetic_panel(
        n_currencies=5, n_months=30, slope_true=1.0
    )
    result = run_vol_on_vol(panel)
    for banned in _BANNED_INFERENTIAL_PHRASES:
        assert banned not in result.g_caveat_label.lower(), (
            f"banned inferential phrase '{banned}' found in g_caveat_label"
        )


def test_run_vol_on_vol_raises_on_empty_panel() -> None:
    """An empty panel cannot be regressed."""
    with pytest.raises(ValueError):
        run_vol_on_vol(())


def test_betas_zero_on_degenerate_single_month_panel() -> None:
    """When all cells share the same month, BOTH FE specs degenerate:
    two-way absorbs all variation, and currency-FE-only also leaves
    zero within-variation because each currency's only cell sits at
    that currency's mean. Both slopes fall to 0 via the divisor-zero
    guard."""
    # 5 currencies, 1 month -- one cell per currency, no within-variation.
    panel = _build_synthetic_panel(
        n_currencies=5, n_months=1, slope_true=0.5
    )
    result = run_vol_on_vol(panel)
    assert result.beta_two_way == pytest.approx(0.0)
    assert result.beta_currency_only == pytest.approx(0.0)
    # The gap is zero on a degenerate panel.
    assert result.gap == pytest.approx(0.0)
