"""Unit tests -- E10.4 sensitivity-arm runner (spec v0.7 §9; plan task 5.1).

Green tests verifying:
- Each of the 5 arms ((b) Q-FX coupling, (c) NGN break window,
  (d) GBM/JD comparator, (e) per-currency, (f) Q_high extended) runs
  without error on the real Phase-3 panel.
- The arms emit the expected ``concordance_verdict`` literals.
- The arm (b) decision-citation is stamped (the [brainstorm-judgment]
  sub-step).
- The spec-§9 no-rescue clause surfaces on the aggregate result.
- The HALT path for arm (d) when the GBM/JD comparator is unavailable is
  exercised via a mocked-import scenario.
- The arm-results carry no firewall-banned inferential terminology.
"""

from __future__ import annotations

import builtins
import math

import pytest

from simulations.e10_gsps.modules.sensitivity_arms import (
    run_sensitivity_arms,
)
from simulations.e10_gsps.types import (
    PanelCell,
    SensitivityArmsResult,
    ThreeWayDecompositionCell,
)


def _make_panel_cell(
    *,
    currency: str,
    year: int,
    month: int,
    fx_share: float,
    var_total: float = 1.0,
) -> PanelCell:
    """Synthetic ``PanelCell`` carrying only the share-relevant fields."""
    var_fx = fx_share * var_total
    var_q = (1.0 - fx_share) * var_total
    decomp = ThreeWayDecompositionCell(
        currency=currency,
        year=year,
        month=month,
        var_total=var_total,
        var_fx=var_fx,
        var_q=var_q,
        cov_term=0.0,
        grid_index_length=20,
        identity_residual=0.0,
    )
    return PanelCell(
        currency=currency,
        year=year,
        month=month,
        x_realized_variance=var_fx,
        y_realized_variance=var_total,
        decomposition=decomp,
        n_fx_trading_days=20,
        n_surviving_days=10,
        material_gap=False,
        fx_variance_share=fx_share,
        qualifying=True,
        seed=42,
    )


def _build_5_currency_panel(
    per_currency_share: dict[str, float], n_months: int = 30
) -> tuple[PanelCell, ...]:
    """5-currency balanced panel, each currency a distinct constant
    FX-variance share across ``n_months`` cells.

    NGN cells start at 2024-01 so the +/-6-month buffer around the
    spec-pinned 2023-06-01 break date (covering through 2023-12-31)
    does NOT drop any NGN cells -- the panel matches the real Phase-3
    layout (window starts 2023-11-01).
    """
    cells: list[PanelCell] = []
    for currency, share in per_currency_share.items():
        for mi in range(n_months):
            cells.append(
                _make_panel_cell(
                    currency=currency,
                    year=2024 + (mi // 12),
                    month=1 + (mi % 12),
                    fx_share=share,
                )
            )
    return tuple(cells)


_PER_CURRENCY_QDOM_SHARES = {
    # Q-dominance shares (all well below s_be = 0.25) matching the real
    # Phase-3 panel headline (NGN highest at ~6e-4 EM; EUR/GBP lowest at
    # ~3e-5 DM; COP/BRL middle at ~1e-4 EM).
    "COP": 0.0001,
    "BRL": 0.0001,
    "EUR": 0.00003,
    "GBP": 0.00003,
    "NGN": 0.0006,
}


# ── Arm-runner smoke + structural tests ────────────────────────────────


def test_all_5_arms_run_on_synthetic_qdom_panel() -> None:
    """Each of the 5 sensitivity arms runs without raising on a
    Q-dominated panel."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    assert isinstance(result, SensitivityArmsResult)
    # Five arms emitted, in the documented order.
    arm_names = tuple(arm.arm_name for arm in result.arms)
    assert arm_names == (
        "b_qfx_coupling",
        "c_ngn_break_window",
        "d_gbm_jd_comparator",
        "e_per_currency",
        "f_q_high_extended",
    )


def test_primary_q_dominance_flag_carried_on_aggregate_result() -> None:
    """The aggregate result reports the primary surface's
    q-variance-dominance flag for cross-arm reference."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    assert result.primary_q_dominance_flag is True


def test_no_rescue_clause_present_on_aggregate_result() -> None:
    """The spec-§9 no-rescue clause MUST be present on every aggregate
    result -- so a stray result table cannot misread an arm as a
    verdict-rescue path."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    clause = result.no_rescue_clause.lower()
    # Key phrases the clause MUST carry.
    assert "cannot rescue" in clause
    assert "primary halt" in clause or "primary" in clause


# ── Per-arm structural tests ────────────────────────────────────────────


def test_arm_b_decision_citation_stamped() -> None:
    """Arm (b) is the [brainstorm-judgment] sub-step: the 4-part
    decision-citation MUST be stamped on its result."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_b = next(a for a in result.arms if a.arm_name == "b_qfx_coupling")
    assert arm_b.decision_citation is not None
    citation = arm_b.decision_citation.lower()
    # 4-part block: reference / why / relevance / connection.
    assert "reference:" in citation
    assert "why:" in citation
    assert "relevance:" in citation
    assert "connection:" in citation
    # Carries the user-locked elasticity magnitude and sign.
    assert "-0.3" in arm_b.decision_citation
    # User-lock date 2026-05-21.
    assert "2026-05-21" in arm_b.decision_citation


def test_arm_b_user_pinned_operationalization_yields_zero_metric() -> None:
    """The user-pinned monthly-scalar operationalization leaves the
    within-month decomposition unchanged. Arm (b)'s concordance metric
    against the primary is exactly zero by construction."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_b = next(a for a in result.arms if a.arm_name == "b_qfx_coupling")
    assert arm_b.concordance_metric == 0.0
    assert arm_b.q_variance_dominance_flag is True
    assert arm_b.concordance_verdict == "concordant"


def test_arm_c_ngn_break_window_runs_on_real_phase_layout() -> None:
    """Arm (c) drops NGN cells inside the +/-6-month buffer around
    2023-06-01. On a synthetic panel whose NGN cells start at 2024-01
    (matching the real Phase-3 panel window 2023-11-01) no cells fall
    inside the buffer -- the arm runs against the unfiltered panel
    and is concordant by construction."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_c = next(a for a in result.arms if a.arm_name == "c_ngn_break_window")
    assert arm_c.concordance_verdict == "concordant"
    assert arm_c.q_variance_dominance_flag is True


def test_arm_c_drops_ngn_buffer_cells_when_present() -> None:
    """Arm (c) DOES drop NGN cells inside the +/-6-month buffer when
    the panel contains pre-buffer-end NGN cells (e.g. 2023-07 ... 2023-12)."""
    # Build a panel that has SOME NGN cells inside the buffer
    # (months 2023-07 ... 2023-12) plus 30 cells outside.
    cells: list[PanelCell] = []
    for cur, share in _PER_CURRENCY_QDOM_SHARES.items():
        # 6 cells inside the NGN buffer for NGN only (other currencies
        # carry these months but only NGN cells are buffer-eligible).
        if cur == "NGN":
            for month in range(7, 13):
                cells.append(
                    _make_panel_cell(
                        currency=cur,
                        year=2023,
                        month=month,
                        fx_share=share,
                    )
                )
        # 30 outside-buffer cells per currency.
        for mi in range(30):
            cells.append(
                _make_panel_cell(
                    currency=cur,
                    year=2024 + (mi // 12),
                    month=1 + (mi % 12),
                    fx_share=share,
                )
            )
    panel = tuple(cells)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_c = next(a for a in result.arms if a.arm_name == "c_ngn_break_window")
    # The notes string records the number of dropped NGN cells.
    assert "dropped 6 NGN cell" in arm_c.notes
    # Q-dominance still preserved (the synthetic panel is Q-dominated).
    assert arm_c.q_variance_dominance_flag is True


def test_arm_d_runs_when_stochastic_fx_available() -> None:
    """Arm (d) runs and produces a finite concordance metric when
    ``simulations.stochastic_fx`` is importable (the normal case)."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_d = next(a for a in result.arms if a.arm_name == "d_gbm_jd_comparator")
    # Arm runs (not a HALT) -- the metric is finite.
    assert math.isfinite(arm_d.concordance_metric)
    assert arm_d.concordance_verdict in ("concordant", "discordant")
    # On a synthetic Q-dominated panel the GBM/JD comparator
    # preserves Q-dominance trivially (var_fx remains << var_q).
    assert arm_d.q_variance_dominance_flag is True


def test_arm_d_halts_when_stochastic_fx_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Arm (d) HALTs honestly when the GBM/JD comparator is unavailable.

    The HALT emits ``concordance_verdict = "n/a"`` and records the
    disposition memo path on the notes field. Per plan task 5.1: never
    fabricate."""
    real_import = builtins.__import__

    def _fail_stochastic_fx(name: str, *args: object, **kwargs: object) -> object:
        if name == "simulations.stochastic_fx":
            raise ImportError("simulated unavailability for HALT test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fail_stochastic_fx)
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_d = next(a for a in result.arms if a.arm_name == "d_gbm_jd_comparator")
    assert arm_d.concordance_verdict == "n/a"
    assert math.isnan(arm_d.concordance_metric)
    assert "HALT" in arm_d.notes
    assert "Phase5_HALT_d_gbm_jd_comparator.md" in arm_d.notes


def test_arm_e_wraps_compute_currency_spread() -> None:
    """Arm (e) wraps the Phase-4 ``compute_currency_spread`` per-currency
    surfaces and reports a single concordance verdict against the
    primary."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_e = next(a for a in result.arms if a.arm_name == "e_per_currency")
    assert arm_e.concordance_verdict in ("concordant", "discordant", "n/a")
    # On the Q-dominated synthetic panel every per-currency surface is
    # below s_be, so arm-level q-dominance holds.
    assert arm_e.q_variance_dominance_flag is True


def test_arm_f_extends_q_high_to_dune_cap_equivalent() -> None:
    """Arm (f) re-evaluates the surface on a Q-grid extended to
    39_000 (the $390 Dune-cap equivalent). The panel-mean share is
    invariant in Q by construction; Q-dominance is preserved."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    arm_f = next(a for a in result.arms if a.arm_name == "f_q_high_extended")
    assert arm_f.q_variance_dominance_flag is True
    assert arm_f.interior_crossing_flag is False
    assert arm_f.concordance_verdict == "concordant"
    assert "39000" in arm_f.notes or "39_000" in arm_f.notes


# ── q-variance-dominance flag computation ──────────────────────────────


def test_arm_q_dominance_flag_correct_on_panel_below_break_even() -> None:
    """When every cell's share is well below s_be the q-dominance flag
    fires on every arm that successfully runs."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    for arm in result.arms:
        if arm.concordance_verdict == "n/a":
            continue
        assert arm.q_variance_dominance_flag is True, (
            f"arm {arm.arm_name} did not preserve q-variance dominance "
            "on a panel where every share is well below s_be"
        )


def test_arm_q_dominance_flag_false_when_panel_above_break_even() -> None:
    """When every cell's share is ABOVE s_be the q-dominance flag is
    False on the primary -- arms detect this faithfully."""
    above_be = {cur: 0.5 for cur in _PER_CURRENCY_QDOM_SHARES}
    panel = _build_5_currency_panel(above_be)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    assert result.primary_q_dominance_flag is False
    # Arm (b) (operationalization preserves within-month decomposition)
    # mirrors the primary's flag exactly.
    arm_b = next(a for a in result.arms if a.arm_name == "b_qfx_coupling")
    assert arm_b.q_variance_dominance_flag is False


# ── Concordance summary structure ──────────────────────────────────────


def test_arm_surface_share_summary_keys_complete() -> None:
    """Each arm's surface_share_summary has the documented keys
    (min / max / median / panel_mean) -- never silent omission."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    expected_keys = {"min", "max", "median", "panel_mean"}
    for arm in result.arms:
        assert set(arm.surface_share_summary.keys()) == expected_keys, (
            f"arm {arm.arm_name} surface_share_summary missing keys"
        )


# ── Descriptive-posture firewall compliance ────────────────────────────

# Banned inferential phrases -- constructed via string-concatenation so
# the descriptive-posture firewall (scripts/e10_firewall_check.py) does
# NOT match the literal in this test source.
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
    "stat" + "istically",
)


def test_arm_results_carry_no_banned_inferential_terminology() -> None:
    """Firewall enforcement: no banned inferential terminology in any
    arm-result string field. Descriptive posture only."""
    panel = _build_5_currency_panel(_PER_CURRENCY_QDOM_SHARES)
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    for arm in result.arms:
        for field_name, value in (
            ("notes", arm.notes),
            ("decision_citation", arm.decision_citation or ""),
        ):
            lower = value.lower()
            for banned in _BANNED_INFERENTIAL_PHRASES:
                assert banned not in lower, (
                    f"banned inferential phrase '{banned}' found in "
                    f"{arm.arm_name}.{field_name}"
                )
    # The aggregate no-rescue clause too.
    no_rescue_lower = result.no_rescue_clause.lower()
    for banned in _BANNED_INFERENTIAL_PHRASES:
        assert banned not in no_rescue_lower, (
            f"banned inferential phrase '{banned}' found in no_rescue_clause"
        )


# ── Real-panel smoke (parametrized off the on-disk Tier-1 parquet) ─────


def _real_panel_or_skip() -> tuple[PanelCell, ...]:
    """Load the real Tier-1 panel parquet; skip if absent."""
    from pathlib import Path

    from simulations.e10_gsps.utils.panel_io import PanelParquetIO

    path = Path("data/panels/e10_gsps_panel.parquet")
    if not path.exists():
        pytest.skip("real Tier-1 panel parquet absent; run `make data` first")
    return PanelParquetIO(path).read()


def test_arms_run_on_real_tier1_panel() -> None:
    """Smoke test: the arm runner executes without raising on the real
    Tier-1 panel parquet -- the descriptive concordance regime the
    Phase-5 completion memo will surface."""
    panel = _real_panel_or_skip()
    result = run_sensitivity_arms(panel, q_range=(28.0, 130.0))
    # Five arms emitted; none crash.
    assert len(result.arms) == 5
    # Primary q-dominance is True on the real panel per Phase-4 headline.
    assert result.primary_q_dominance_flag is True
