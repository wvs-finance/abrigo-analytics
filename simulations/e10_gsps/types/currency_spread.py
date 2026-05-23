"""Non-statistical 5-currency min-max / IQR spread-display Value-tier
container (spec v0.7 §4.3; plan task 4.3 / CORR-E10P-11 / spec v0.6 W-2).

At G~=5 the wild-cluster bootstrap is size-broken (G < ~12 threshold)
and the permutation arm has 2^5 = 32-point support with EM/DM
exchangeability violated — both bands are DROPPED. The replacement is
the **raw 5-currency min-max / IQR spread display**: overplot the 5
per-currency surface curves and report the pointwise min / max / Q1 / Q3
/ median envelope. **NON-statistical** — a descriptive spread of 5
observed values, NOT a confidence interval, NOT an inferential band, NOT
a hypothesis test.

The display gates no verdict.

Discipline
----------
``types``-tier: frozen-dataclass container; no logic, no imports from
``..modules`` / ``..utils``. The ``Literal["EM", "DM"]`` typed mapping
tags each panel currency for EM-vs-DM colour coding in the notebook
overplot (cosmetic, not statistical) — per Model QA Item 4 enforcement
recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .surface import SurfaceGridResult


@dataclass(frozen=True, slots=True)
class CurrencySpreadResult:
    """Per-currency surface curves + non-statistical envelope.

    ``per_currency_grids`` maps each panel currency code (e.g. "COP")
    to the ``SurfaceGridResult`` computed by filtering the panel to that
    currency's cells. Five entries at G=5.

    ``envelope_q_grid`` is the shared log-spaced Q-grid the 5 per-
    currency surfaces are evaluated on (the same anchored-range grid
    every per-currency call uses).

    ``envelope_min`` / ``envelope_max`` are the pointwise min and max
    of the 5 per-currency shares at each grid point.
    ``envelope_q1`` / ``envelope_q3`` are the pointwise first and third
    quartiles. ``envelope_median`` is the pointwise median.

    ``is_em_or_dm`` tags each panel currency as "EM" or "DM" (per
    Model QA review Item 4 — cosmetic colour-coding for the notebook
    overplot).

    ``non_statistical_label`` is the literal in-figure label the
    consuming notebook MUST render alongside the envelope display so
    a figure leaving its surrounding prose still self-firewalls
    (per Model QA review Item 4 enforcement note).
    """

    per_currency_grids: dict[str, SurfaceGridResult]
    envelope_q_grid: tuple[float, ...]
    envelope_min: tuple[float, ...]
    envelope_max: tuple[float, ...]
    envelope_q1: tuple[float, ...]
    envelope_q3: tuple[float, ...]
    envelope_median: tuple[float, ...]
    is_em_or_dm: dict[str, Literal["EM", "DM"]]
    non_statistical_label: str
