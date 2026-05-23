"""Failing-test harness — panel-currency verification + regime-break screen.

Plan v0.2 Phase 0.4. RED in Phase 0: imports the not-yet-existent
``simulations.e10_gsps.modules.regime_break`` module, so collection
fails. The screen lands in Phase 1 (plan task 1.2).

Fixtures exercise the spec v0.4 §3.3 regime-break treatment:
- NGN confined to its post-June-2023 float regime (NFEM unification).
- GHS / KES screened for heavily-managed administrative-peg periods.
"""

from __future__ import annotations

from datetime import date

import pytest

from simulations.e10_gsps._errors import (
    PanelCurrencyCoverageError,
    RegimeBreakScreenError,
)
from simulations.e10_gsps.modules.regime_break import (  # noqa: F401 — RED import
    RegimeBreakScreenModule,
    confine_to_float_regime,
    screen_managed_float,
)
from simulations.e10_gsps.types import CurrencyDailyFXRow


def _ngn_pre_float_rows() -> tuple[CurrencyDailyFXRow, ...]:
    """Synthetic NGN managed-peg rows BEFORE the June-2023 float — these
    must be screened out (administrative near-zero realized variance)."""
    return tuple(
        CurrencyDailyFXRow(
            currency="NGN",
            observation_date=date(2023, 1, d),
            fx_rate=460.0,  # pegged — flat
            source="CBN",
            post_regime_break=False,
        )
        for d in range(1, 21)
    )


def _ngn_post_float_rows() -> tuple[CurrencyDailyFXRow, ...]:
    """Synthetic NGN post-float rows — genuine market-determined variance."""
    return tuple(
        CurrencyDailyFXRow(
            currency="NGN",
            observation_date=date(2023, 8, d),
            fx_rate=750.0 + d * 3.0,
            source="CBN",
            post_regime_break=True,
        )
        for d in range(1, 21)
    )


def test_ngn_pre_float_rows_are_confined_out() -> None:
    """The NGN series is confined to the post-June-2023 float regime."""
    rows = _ngn_pre_float_rows() + _ngn_post_float_rows()
    confined = confine_to_float_regime(rows, currency="NGN")
    assert all(r.observation_date >= date(2023, 6, 1) for r in confined)
    assert all(r.post_regime_break for r in confined)


def test_managed_float_screen_flags_ghs_kes() -> None:
    """GHS / KES heavily-managed administrative-peg periods are screened."""
    screen = RegimeBreakScreenModule()
    for currency in ("GHS", "KES"):
        result = screen_managed_float(currency=currency)
        assert result.qualifying_window_start is not None
        assert result.currency == currency
    del screen


def test_screen_raises_when_qualifying_window_below_target() -> None:
    """A currency whose qualifying float window falls below the ~30-month
    panel target raises PanelCurrencyCoverageError."""
    short_rows = _ngn_post_float_rows()[:5]
    with pytest.raises(PanelCurrencyCoverageError):
        confine_to_float_regime(short_rows, currency="NGN", min_months=30)


def test_screen_raises_when_regime_cannot_be_confined() -> None:
    """A series that cannot be confined to a single float regime raises
    RegimeBreakScreenError — never silently mixes peg and float."""
    mixed = _ngn_pre_float_rows() + _ngn_post_float_rows()
    with pytest.raises(RegimeBreakScreenError):
        screen = RegimeBreakScreenModule()
        screen(mixed, allow_mixed_regime=False)
