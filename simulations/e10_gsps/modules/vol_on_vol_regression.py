"""Vol-on-vol regression — descriptive sign gate under two co-primary
FE specifications (spec v0.7 §4.1; plan task 4.1 / CORR-E10P-11).

What this unit does
-------------------
Runs the §4.1 vol-on-vol regression — regress the Y-side cost-stream
realized variance on the X-side FX realized variance — under the **two
co-primary** fixed-effects specifications mandated by CORR-E10P-11 /
spec v0.6 W-1:

- **(i) Two-way FE — currency FE + month FE — primary.** The
  within-transformation projects out both currency means and month
  means; the residualized variation is the (currency, month) idiosyncratic
  FX-variance dispersion. At n=150 cells with 5 + 30 - 1 = 34 absorbed
  parameters (one collinear with the intercept), 115 residual DoF
  remain for the single slope.
- **(ii) Currency-FE-only — co-primary.** The within-transformation
  projects out only currency means; the residualized variation
  preserves the cross-month / cross-currency level information that
  the §13 M-sketch's hedge-sizing depends on.

The two-way-vs-currency-only gap = ``beta_two_way - beta_currency_only``
is reported as descriptive content (a Frisch-Waugh-Lovell decomposition
of global-vs-idiosyncratic FX-vol exposure).

Posture
-------
**Descriptive sign only.** No t-stat. No p-value. No inferential claim.
At G~=5 the cluster-robust variance estimator is severely size-distorted
(the (G-1)/G Bessel-style correction is meaningless); the result object
carries a literal G-caveat label the consuming notebook MUST render at
the point of use.

Algorithm — within-transformation slope
---------------------------------------
For a FE specification absorbing groups ``g_1, ..., g_k``, the slope is::

    x_tilde = x - mean(x | g_1) - mean(x | g_2) - ... + (k-1)*grand_mean
    y_tilde = y - mean(y | g_1) - mean(y | g_2) - ... + (k-1)*grand_mean
    beta = sum(x_tilde * y_tilde) / sum(x_tilde * x_tilde)

For the two-way (currency + month) case ``k=2``, so the
demeaning includes ``mean(x|currency) + mean(x|month) - grand_mean``.
For currency-FE-only ``k=1``, so the demeaning is just
``mean(x|currency)``. Population means are used throughout.

Discipline
----------
``modules``-tier: frozen-dataclass stateless container + free pure
functions; no mutable state, no imports from ``..utils``. Inputs are
``PanelCell`` containers from the Phase-3 panel; the function is pure
in the panel argument.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from simulations.e10_gsps.types import PanelCell, VolOnVolResult


_G_CAVEAT_LABEL: str = (
    "G~=5 currency clusters — descriptive sign only; "
    "clustered SE is structurally size-distorted at this G and is "
    "reported (if at all) as context, not as an inferential claim."
)


def _sign(x: float) -> int:
    """Mathematical sign of a float (+1, 0, -1)."""
    if x > 0.0:
        return 1
    if x < 0.0:
        return -1
    return 0


def _two_way_demean(
    values: np.ndarray,
    currency_idx: np.ndarray,
    month_idx: np.ndarray,
    n_currencies: int,
    n_months: int,
) -> np.ndarray:
    """Two-way within-transformation: subtract currency mean + month
    mean and add back the grand mean (one-step FWL identity for a
    balanced panel; for an unbalanced panel this is a first-order
    approximation, but the E10 panel is balanced at 5 x 30 = 150).

    Args:
        values: The variable to be demeaned (length-n vector).
        currency_idx: Integer currency index per cell (0..n_currencies-1).
        month_idx: Integer month index per cell (0..n_months-1).
        n_currencies: Distinct currency count.
        n_months: Distinct month count.

    Returns:
        The within-transformed values (length-n vector).
    """
    grand_mean = float(values.mean())
    currency_means = np.zeros(n_currencies)
    for c in range(n_currencies):
        mask = currency_idx == c
        if mask.any():
            currency_means[c] = float(values[mask].mean())
    month_means = np.zeros(n_months)
    for m in range(n_months):
        mask = month_idx == m
        if mask.any():
            month_means[m] = float(values[mask].mean())
    return (
        values
        - currency_means[currency_idx]
        - month_means[month_idx]
        + grand_mean
    )


def _currency_demean(
    values: np.ndarray,
    currency_idx: np.ndarray,
    n_currencies: int,
) -> np.ndarray:
    """Currency-FE-only within-transformation: subtract currency mean.

    Args:
        values: The variable to be demeaned (length-n vector).
        currency_idx: Integer currency index per cell.
        n_currencies: Distinct currency count.

    Returns:
        The within-transformed values (length-n vector).
    """
    currency_means = np.zeros(n_currencies)
    for c in range(n_currencies):
        mask = currency_idx == c
        if mask.any():
            currency_means[c] = float(values[mask].mean())
    return values - currency_means[currency_idx]


def _within_slope(x_tilde: np.ndarray, y_tilde: np.ndarray) -> float:
    """Within-FE slope: sum(x_t*y_t) / sum(x_t**2).

    Args:
        x_tilde: Within-transformed regressor.
        y_tilde: Within-transformed regressand.

    Returns:
        The slope estimate. Returns 0.0 if the regressor has no within-
        variation (denominator zero) — the regressor is collinear with
        the absorbed FE and the slope is not identified; the
        descriptive-sign gate is moot in that degenerate case.
    """
    denom = float((x_tilde * x_tilde).sum())
    if denom == 0.0:
        return 0.0
    return float((x_tilde * y_tilde).sum() / denom)


def run_vol_on_vol(panel: Sequence[PanelCell]) -> VolOnVolResult:
    """Run the §4.1 vol-on-vol regression under both co-primary FE specs.

    Args:
        panel: Sequence of assembled ``PanelCell`` records (the Phase-3
            output). Each cell carries ``x_realized_variance`` (the
            §3.2 X) and ``y_realized_variance`` (the §5.2 Y) on the
            common daily gapped grid.

    Returns:
        A ``VolOnVolResult`` carrying the two co-primary slopes, the
        descriptive signs, the two-way-vs-currency-only gap, the panel
        dimensions, the residual DoF counts, and the G-caveat label
        the consuming notebook must render at the point of use.

    Raises:
        ValueError: The panel is empty (no cells) — the regression
            cannot run on an empty panel.
    """
    if len(panel) == 0:
        raise ValueError(
            "vol-on-vol regression requires a non-empty panel"
        )

    x_values = np.array(
        [cell.x_realized_variance for cell in panel], dtype=float
    )
    y_values = np.array(
        [cell.y_realized_variance for cell in panel], dtype=float
    )

    currency_codes = [cell.currency for cell in panel]
    distinct_currencies = sorted(set(currency_codes))
    currency_to_idx = {c: i for i, c in enumerate(distinct_currencies)}
    currency_idx = np.array(
        [currency_to_idx[c] for c in currency_codes], dtype=int
    )

    month_keys = [(cell.year, cell.month) for cell in panel]
    distinct_months = sorted(set(month_keys))
    month_to_idx = {m: i for i, m in enumerate(distinct_months)}
    month_idx = np.array(
        [month_to_idx[m] for m in month_keys], dtype=int
    )

    n_cells = len(panel)
    n_currencies = len(distinct_currencies)
    n_months = len(distinct_months)

    # (i) Two-way FE — currency + month.
    x_tw = _two_way_demean(
        x_values, currency_idx, month_idx, n_currencies, n_months
    )
    y_tw = _two_way_demean(
        y_values, currency_idx, month_idx, n_currencies, n_months
    )
    beta_two_way = _within_slope(x_tw, y_tw)

    # (ii) Currency-FE-only.
    x_co = _currency_demean(x_values, currency_idx, n_currencies)
    y_co = _currency_demean(y_values, currency_idx, n_currencies)
    beta_currency_only = _within_slope(x_co, y_co)

    gap = beta_two_way - beta_currency_only

    # Absorbed parameters: two-way FE absorbs (n_currencies + n_months - 1)
    # parameters (one collinear with the intercept). Currency-FE-only
    # absorbs n_currencies (intercept is the omitted currency).
    absorbed_two_way = n_currencies + n_months - 1
    absorbed_currency_only = n_currencies
    # Residual DoF = n - absorbed - 1 (the single slope).
    residual_dof_two_way = max(0, n_cells - absorbed_two_way - 1)
    residual_dof_currency_only = max(0, n_cells - absorbed_currency_only - 1)

    return VolOnVolResult(
        beta_two_way=beta_two_way,
        beta_currency_only=beta_currency_only,
        gap=gap,
        sign_two_way=_sign(beta_two_way),
        sign_currency_only=_sign(beta_currency_only),
        n_cells=n_cells,
        n_currency_clusters=n_currencies,
        residual_dof_two_way=residual_dof_two_way,
        residual_dof_currency_only=residual_dof_currency_only,
        g_caveat_label=_G_CAVEAT_LABEL,
    )
