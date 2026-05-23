"""Vol-on-vol regression result Value-tier container (spec v0.7 §4.1;
plan task 4.1 / CORR-E10P-11).

The vol-on-vol regression is the necessary-not-sufficient descriptive
sign gate of spec §7 field 1: regress the Y-side cost-stream realized
variance on the X-side FX realized variance under two co-primary
fixed-effects (FE) specifications and report the descriptive sign of
beta on each.

The two co-primary FE specifications (per CORR-E10P-11 / spec v0.6 W-1):
- **Two-way FE (currency FE + month FE)** — primary. At 150 cells with
  5 + 30 - 1 = 34 absorbed parameters, 115 residual DoF.
- **Currency-FE-only** — co-primary (promoted from a sensitivity arm to
  a co-primary descriptive specification). Preserves cross-currency
  level information.

The **two-way-vs-currency-only gap** = beta_two_way - beta_currency_only
is a Frisch-Waugh-Lovell decomposition: it quantifies how much of the
beta signal lives in global (month-FE-absorbed) FX-vol co-movement vs
idiosyncratic (within-month, cross-currency) FX-vol dispersion. The §13
M-sketch depends on this gap.

Posture: **descriptive only**. The sign of beta is reported; no t-stat,
no p-value, no inferential claim. At G~=5 the cluster-robust variance
estimator is severely size-distorted (the (G-1)/G Bessel correction is
meaningless); clustered SE is reported as context only, never as an
inferential claim.

Discipline
----------
``types``-tier: frozen-dataclass container; no logic, no imports from
``..modules`` / ``..utils``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VolOnVolResult:
    """Vol-on-vol regression result under the two co-primary FE specs.

    ``beta_two_way`` is the slope of Y-side realized variance on X-side
    realized variance under the two-way FE (currency FE + month FE)
    primary specification. ``beta_currency_only`` is the slope under the
    co-primary currency-FE-only specification. ``gap`` =
    ``beta_two_way - beta_currency_only`` is the Frisch-Waugh-Lovell
    descriptive gap (global-vs-idiosyncratic FX-vol exposure split).

    ``sign_two_way`` / ``sign_currency_only`` are the descriptive signs
    (+1, 0, -1) of the corresponding betas — the necessary-not-sufficient
    descriptive sign gate of spec §7 field 1.

    ``n_cells`` is the panel cell count fed to the regression.
    ``n_currency_clusters`` is the binding identification dimension
    (G ~= 5).

    ``residual_dof_two_way`` is the residual degree-of-freedom count of
    the two-way FE fit (n - absorbed parameters - 1 slope).
    ``residual_dof_currency_only`` is the same for the currency-FE-only
    fit.

    ``g_caveat_label`` is the literal in-figure caveat the consuming
    notebook MUST render alongside any reported point estimate
    (descriptive context only — at G~=5 no inferential claim is valid).
    """

    beta_two_way: float
    beta_currency_only: float
    gap: float
    sign_two_way: int
    sign_currency_only: int
    n_cells: int
    n_currency_clusters: int
    residual_dof_two_way: int
    residual_dof_currency_only: int
    g_caveat_label: str
