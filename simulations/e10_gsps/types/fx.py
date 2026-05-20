"""FX measurement-layer Value-tier containers (spec v0.5 §3).

Per-currency daily central-bank FX observation and the per-(currency,
month) monthly realized-log-variance cell. X is 100% real data — these
containers carry central-bank rate histories only; no simulated quantity
appears here (the simulated Q lives in ``nhpp.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# The five panel currencies per spec v0.5 §3.3 / CORRECTIONS-E10-5 (the
# HALT-DV re-spec at E10.0). The v0.4 8-currency panel was narrowed to 5
# after the E10.0 per-currency re-verification found ZAR, KES, GHS lack a
# free machine-readable daily ~30-month central-bank series. The 3 are
# dropped — not substituted — and recorded as the historically-dropped
# set in ``HALT_DV_CURRENCIES`` (utils/fx_ingest_io.py). The panel is NOT
# expanded — no substitute EM currency replaces the dropped three.
PANEL_CURRENCIES: tuple[str, ...] = (
    "COP",
    "BRL",
    "EUR",
    "GBP",
    "NGN",
)


@dataclass(frozen=True, slots=True)
class CurrencyDailyFXRow:
    """One (currency, day) observation from a central bank's published
    daily local-currency-per-USD series.

    ``fx_rate`` is the local-currency-per-USD reference rate. ``source``
    names the issuing central bank (Banrep / BCB / ECB / BoE / CBN).
    ``post_regime_break`` records whether this day lies inside the
    currency's qualifying post-structural-break float window (spec v0.5
    §3.3 — NGN confined to post-June-2023 float).
    """

    currency: str
    observation_date: date
    fx_rate: float
    source: str
    post_regime_break: bool


@dataclass(frozen=True, slots=True)
class MonthlyRealizedVarianceCell:
    """One (currency, month) monthly realized-log-variance cell.

    ``realized_log_variance`` is the within-month sum of squared daily
    log-returns of the FX rate (sum-vs-mean convention fixed at pre-pin;
    spec v0.5 §3.2). ``n_trading_days`` is the count of daily
    observations contributing to the cell on the common differencing
    grid (plan task 3.0). ``qualifying`` records whether the cell lies
    inside the currency's post-regime-break qualifying window.
    """

    currency: str
    year: int
    month: int
    realized_log_variance: float
    n_trading_days: int
    qualifying: bool


@dataclass(frozen=True, slots=True)
class PanelWindowDiagnostics:
    """Phase-1 task-1.4 panel-window deliverable (spec v0.5 §3.3 / §7
    field 6; CORRECTIONS-E10-5).

    The post-regime-break intersection window the 5 v0.5 panel
    currencies share, with the (currency, month) cell count. ``window_start``
    / ``window_end`` are the inclusive ISO-8601 bounds of the common
    qualifying window; ``n_currencies`` is the panel cluster count G;
    ``months_per_currency`` is the per-currency month count; ``n_cells``
    is the total (currency, month) cell count of the two-way-FE panel.
    """

    window_start: str
    window_end: str
    n_currencies: int
    months_per_currency: int
    n_cells: int


# Phase-1 task-1.4 panel-window — the post-regime-break intersection the
# 5 v0.5 panel currencies share (spec v0.5 §3.3 / §7 field 6;
# CORRECTIONS-E10-5). Derived at E10.0 from the real frozen Tier-2
# snapshots: COP/BRL/EUR/GBP/NGN each yield 30 (currency, month) cells
# over 2023-11-01 → 2026-04-30 ⇒ 5 × 30 = 150 cells. The ~150-cell panel
# clears N_MIN = 75 at the cell dimension; the binding identification
# dimension is G ≈ 5 currency clusters (spec v0.5 §8).
PANEL_WINDOW: PanelWindowDiagnostics = PanelWindowDiagnostics(
    window_start="2023-11-01",
    window_end="2026-04-30",
    n_currencies=5,
    months_per_currency=30,
    n_cells=150,
)
