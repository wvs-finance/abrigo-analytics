"""Panel-currency verification + regime-break screen (plan task 1.2).

Phase-1 implementation of the spec v0.5 §3.3 regime-break treatment.
Callable tier — frozen-dataclass + free pure functions, no mutable state
(the tier-import discipline forbids importing from ``..utils``).

What the screen does (spec v0.5 §3.3 / §10 E10.0):

- **NGN** is confined to its **post-June-2023 float regime** (NFEM /
  willing-buyer-willing-seller unification). Pre-float CBN "official"
  daily rates were a managed peg with administrative near-zero realized
  variance — a peg-to-float structural break, not a missing-data gap.
  The screen drops every pre-2023-06-01 NGN row.
- COP, BRL, EUR, GBP are free-floating across the whole panel window —
  no within-window administrative-peg break.
- Any currency whose qualifying post-structural-break window falls below
  the ~30-month panel target raises ``PanelCurrencyCoverageError`` — the
  window is never extended to manufacture cells (spec §8 anti-fishing).
- A series the screen cannot confine to a single float regime raises
  ``RegimeBreakScreenError`` — peg and float are never silently mixed in
  one realized-variance series.

The per-currency regime-break dates are spec-pinned constants (spec
§3.3), declared here BEFORE any data is touched — not a post-data window
choice. The numeric FX values flowing through the screen are 100% real
central-bank data (the fantasy-firewall, plan Phase 0.12, enforces this);
this module only *filters* rows by date, it never synthesizes a rate.

Note — GHS / KES dropped at E10.0 (CORRECTIONS-E10-5). The v0.4 panel
included GHS and KES; the E10.0 HALT-DV re-spec narrowed the panel to 5
currencies (COP, BRL, EUR, GBP, NGN). The GHS / KES regime-break dates
remain in ``_REGIME_BREAK_START`` only as the historical pinned record —
neither is a v0.5 panel currency and neither reaches the live panel.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from simulations.e10_gsps._errors import (
    PanelCurrencyCoverageError,
    RegimeBreakScreenError,
)
from simulations.e10_gsps.types import CurrencyDailyFXRow

# ── Spec-pinned per-currency regime-break registry (spec v0.5 §3.3) ──────
#
# ``qualifying_window_start`` is the first date of the currency's
# qualifying post-structural-break float / managed-float window. Pinned
# here BEFORE E10.0 touches data so it is not a post-data window choice.
#
# v0.5 panel currencies (5):
# - NGN: 2023-06-01 — NFEM / willing-buyer-willing-seller float (spec
#   §3.3, CORRECTIONS-E10-4 Fix 3). Pre-float CBN official rates are an
#   administrative peg and are screened out.
# - COP / BRL / EUR / GBP: free-floating across the whole panel window —
#   no within-window administrative-peg regime break — so their
#   qualifying-window start is the panel-window floor (None sentinel ⇒
#   "no confinement; raw availability qualifies").
#
# Historically-dropped at E10.0 (HALT-DV; CORRECTIONS-E10-5) — NOT v0.5
# panel currencies; their pinned dates are kept only as the historical
# record and never reach the live 5-currency panel:
# - GHS / KES: were screened for heavily-managed administrative-peg
#   periods; both lacked a free machine-readable daily ~30-month series
#   and were dropped from the panel.
_REGIME_BREAK_START: dict[str, date | None] = {
    "NGN": date(2023, 6, 1),
    "COP": None,
    "BRL": None,
    "EUR": None,
    "GBP": None,
    # Historically-dropped (CORRECTIONS-E10-5) — not v0.5 panel members.
    "GHS": date(2023, 1, 1),
    "KES": date(2023, 3, 1),
}

# A month is ~30.44 days; the ~30-month panel target ⇒ this many days.
_DAYS_PER_MONTH: float = 30.4368


@dataclass(frozen=True, slots=True)
class ManagedFloatScreenResult:
    """Per-currency regime-break screen result.

    ``qualifying_window_start`` is the first date of the currency's
    qualifying post-structural-break window (``None`` for a currency with
    no within-window administrative-peg break — it floats throughout).
    ``regime_break`` records whether a structural break was pinned for
    this currency at all.
    """

    currency: str
    qualifying_window_start: date | None
    regime_break: bool


def _span_months(rows: tuple[CurrencyDailyFXRow, ...]) -> float:
    """Calendar span of ``rows`` in months (max date − min date)."""
    if not rows:
        return 0.0
    dates = [r.observation_date for r in rows]
    return (max(dates) - min(dates)).days / _DAYS_PER_MONTH


def screen_managed_float(*, currency: str) -> ManagedFloatScreenResult:
    """Return the spec-pinned regime-break screen result for ``currency``.

    Args:
        currency: A currency code (spec v0.5 §3.3 — 5 panel currencies
            COP, BRL, EUR, GBP, NGN; the registry also retains the
            historically-dropped GHS / KES record).

    Returns:
        A ``ManagedFloatScreenResult`` carrying the qualifying-window
        start date. For NGN it is the post-June-2023 float start; for
        GHS / KES the post-managed-peg qualifying start; for a
        free-floating currency the start is ``None``.

    Raises:
        RegimeBreakScreenError: ``currency`` is not a recognised panel
            currency — the screen has no pinned regime registry for it
            and will not guess.
    """
    if currency not in _REGIME_BREAK_START:
        raise RegimeBreakScreenError(
            f"no spec-pinned regime registry for currency {currency!r}; "
            f"the screen never guesses a regime-break date"
        )
    start = _REGIME_BREAK_START[currency]
    return ManagedFloatScreenResult(
        currency=currency,
        qualifying_window_start=start,
        regime_break=start is not None,
    )


def confine_to_float_regime(
    rows: tuple[CurrencyDailyFXRow, ...],
    *,
    currency: str,
    min_months: int = 0,
) -> tuple[CurrencyDailyFXRow, ...]:
    """Confine ``currency``'s daily FX rows to its qualifying float regime.

    Drops every row dated before the currency's spec-pinned
    qualifying-window start (spec §3.3). For a free-floating currency
    (no pinned break) the rows are returned unchanged.

    Args:
        rows: The currency's daily central-bank FX rows (any regime mix).
        currency: One of the 5 v0.5 panel currency codes
            (COP, BRL, EUR, GBP, NGN).
        min_months: If > 0, the confined window must span at least this
            many months or the call raises ``PanelCurrencyCoverageError``.

    Returns:
        The rows dated on/after the qualifying-window start, sorted
        ascending by observation date, each with ``post_regime_break``
        consistency verified.

    Raises:
        RegimeBreakScreenError: ``currency`` has no pinned regime
            registry; OR a confined row carries ``post_regime_break=False``
            (a peg-regime row leaked into the float window — the screen
            never silently mixes regimes).
        PanelCurrencyCoverageError: ``min_months > 0`` and the confined
            window spans fewer than ``min_months`` months — the window is
            never extended to manufacture cells (spec §8 anti-fishing).
    """
    screen = screen_managed_float(currency=currency)
    start = screen.qualifying_window_start

    confined = (
        rows
        if start is None
        else tuple(r for r in rows if r.observation_date >= start)
    )

    # A confined row claiming pre-break status is a regime-mix leak.
    for r in confined:
        if start is not None and not r.post_regime_break:
            raise RegimeBreakScreenError(
                f"{currency} row {r.observation_date.isoformat()} is inside "
                f"the qualifying float window (>= {start.isoformat()}) but "
                f"carries post_regime_break=False — peg/float regime mix"
            )

    if min_months > 0:
        span = _span_months(confined)
        if span < min_months:
            raise PanelCurrencyCoverageError(
                f"{currency} qualifying post-regime-break window spans "
                f"{span:.1f} months — below the {min_months}-month panel "
                f"target; the window is NEVER extended to manufacture cells "
                f"(spec v0.5 §8). Routes to PARTIAL / NON-RETIREMENT per §9."
            )

    return tuple(sorted(confined, key=lambda r: r.observation_date))


@dataclass(frozen=True, slots=True)
class RegimeBreakScreenModule:
    """Stateless callable — confines each currency to its qualifying
    post-structural-break float window (spec v0.5 §3.3 / plan task 1.2).

    Satisfies the ``types.RegimeBreakScreen`` Protocol. The optional
    ``allow_mixed_regime`` keyword controls whether a peg/float-mixed
    series is screened (the default) or rejected outright.
    """

    def __call__(
        self,
        rows: tuple[CurrencyDailyFXRow, ...],
        *,
        allow_mixed_regime: bool = True,
    ) -> tuple[CurrencyDailyFXRow, ...]:
        """Screen ``rows`` — confine every currency present to its
        qualifying float regime.

        Args:
            rows: Daily FX rows across one or more panel currencies.
            allow_mixed_regime: When ``False``, a currency series that
                contains both pre-break (peg) and post-break (float) rows
                raises ``RegimeBreakScreenError`` instead of being
                silently confined — used to assert the screen never
                blends regimes implicitly.

        Returns:
            The union of every currency's confined float-regime rows,
            sorted ascending by (currency, observation date).

        Raises:
            RegimeBreakScreenError: ``allow_mixed_regime=False`` and a
                currency carries both peg-regime and float-regime rows;
                OR a currency has no pinned regime registry.
        """
        currencies = {r.currency for r in rows}
        out: list[CurrencyDailyFXRow] = []
        for cur in sorted(currencies):
            cur_rows = tuple(r for r in rows if r.currency == cur)
            if not allow_mixed_regime:
                has_peg = any(not r.post_regime_break for r in cur_rows)
                has_float = any(r.post_regime_break for r in cur_rows)
                if has_peg and has_float:
                    raise RegimeBreakScreenError(
                        f"{cur} series mixes peg-regime and float-regime "
                        f"rows; allow_mixed_regime=False forbids the screen "
                        f"from blending them into one realized-variance "
                        f"series (spec v0.5 §3.3)"
                    )
            out.extend(confine_to_float_regime(cur_rows, currency=cur))
        return tuple(
            sorted(out, key=lambda r: (r.currency, r.observation_date))
        )


__all__ = [
    "ManagedFloatScreenResult",
    "RegimeBreakScreenModule",
    "confine_to_float_regime",
    "screen_managed_float",
]
