"""Hypothesis strategies for E10 GSPS types-tier containers (plan task 0.3).

Round-trip and invariant-preserving strategies. Used by:

- ``tests/unit/test_types_roundtrip.py`` (Phase 0.3)
- ``tests/unit/test_panel_regime_break.py`` (Phase 0.4)
- ``tests/unit/test_nhpp_engine.py`` (Phase 0.5)
- ``tests/unit/test_decomposition.py`` (Phase 0.6)
- ``tests/unit/test_surface_grid.py`` (Phase 0.7)
- ``tests/unit/test_verdict_classifier.py`` (Phase 0.8)

Phase 0: type round-trip strategies are complete. Downstream module
strategies that need calibrated inputs land alongside the Phase 2 /
Phase 3 / Phase 4 modules they support.
"""

from __future__ import annotations

from datetime import date

from hypothesis import strategies as st

from simulations.e10_gsps.types import (
    PANEL_CURRENCIES,
    CostStreamTrajectory,
    CurrencyDailyFXRow,
    LambdaModulationForm,
    LambdaModulationSpec,
    MonthlyRealizedVarianceCell,
    NHPPIntensityParameters,
    SurfaceGridPoint,
    SurfaceGridResult,
    ThreeWayDecompositionCell,
)
from simulations.e10_gsps.types.verdict import (
    DescriptiveVerdict,
    DescriptiveVerdictResult,
)

# Central-bank source labels keyed to the eight panel currencies.
_SOURCE_BY_CURRENCY = {
    "COP": "Banrep",
    "BRL": "BCB",
    "KES": "CBK",
    "NGN": "CBN",
    "GHS": "BoG",
    "ZAR": "SARB",
    "EUR": "ECB",
    "GBP": "BoE",
}

# Spec v0.4 §1.2 — 30-month free daily availability window (illustrative
# bounds for synthetic fixtures; the real window is fixed at E10.0).
WINDOW_START = date(2023, 6, 1)
WINDOW_END = date(2026, 5, 31)


@st.composite
def currency_daily_fx_rows(draw: st.DrawFn) -> CurrencyDailyFXRow:
    """Synthetic (currency, day) central-bank FX rows."""
    currency = draw(st.sampled_from(PANEL_CURRENCIES))
    return CurrencyDailyFXRow(
        currency=currency,
        observation_date=draw(
            st.dates(min_value=WINDOW_START, max_value=WINDOW_END)
        ),
        fx_rate=draw(st.floats(min_value=1e-3, max_value=1e5, allow_nan=False)),
        source=_SOURCE_BY_CURRENCY[currency],
        post_regime_break=draw(st.booleans()),
    )


@st.composite
def monthly_realized_variance_cells(
    draw: st.DrawFn,
) -> MonthlyRealizedVarianceCell:
    """Synthetic (currency, month) realized-log-variance cells."""
    return MonthlyRealizedVarianceCell(
        currency=draw(st.sampled_from(PANEL_CURRENCIES)),
        year=draw(st.integers(min_value=2023, max_value=2026)),
        month=draw(st.integers(min_value=1, max_value=12)),
        realized_log_variance=draw(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
        ),
        n_trading_days=draw(st.integers(min_value=15, max_value=23)),
        qualifying=draw(st.booleans()),
    )


@st.composite
def lambda_modulation_specs(draw: st.DrawFn) -> LambdaModulationSpec:
    """Synthetic lambda(t) modulation slots. Phase 0 leaves the
    functional form unlocked (the Phase-2 judgment per plan task 2.3)."""
    return LambdaModulationSpec(
        form=draw(st.sampled_from(list(LambdaModulationForm))),
        functional_form=draw(st.sampled_from(["", "sinusoidal", "step"])),
        params=tuple(
            draw(
                st.lists(
                    st.floats(min_value=-10.0, max_value=10.0, allow_nan=False),
                    min_size=0,
                    max_size=4,
                )
            )
        ),
        locked=draw(st.booleans()),
    )


@st.composite
def nhpp_intensity_parameters(draw: st.DrawFn) -> NHPPIntensityParameters:
    """Synthetic NHPP intensity-parameter containers."""
    q_low = draw(st.floats(min_value=100.0, max_value=10_000.0, allow_nan=False))
    q_high = draw(
        st.floats(min_value=q_low + 1.0, max_value=39_900.0, allow_nan=False)
    )
    return NHPPIntensityParameters(
        lambda_0=draw(st.floats(min_value=0.1, max_value=100.0, allow_nan=False)),
        modulations=tuple(
            LambdaModulationSpec(
                form=form,
                functional_form="",
                params=(),
                locked=False,
            )
            for form in LambdaModulationForm
        ),
        overdispersion_mechanism=draw(
            st.sampled_from(["", "cox", "negative_binomial", "hawkes"])
        ),
        q_low=q_low,
        q_high=q_high,
        qfx_independent=draw(st.booleans()),
    )


@st.composite
def cost_stream_trajectories(draw: st.DrawFn) -> CostStreamTrajectory:
    """Synthetic per-(currency, month) cost-stream trajectories."""
    n_days = draw(st.integers(min_value=15, max_value=23))
    counts = tuple(
        draw(
            st.lists(
                st.integers(min_value=0, max_value=5_000),
                min_size=n_days,
                max_size=n_days,
            )
        )
    )
    fx = tuple(
        draw(
            st.lists(
                st.floats(min_value=1e-3, max_value=1e5, allow_nan=False),
                min_size=n_days,
                max_size=n_days,
            )
        )
    )
    cost = tuple(c * 0.01 * f for c, f in zip(counts, fx))
    return CostStreamTrajectory(
        currency=draw(st.sampled_from(PANEL_CURRENCIES)),
        year=draw(st.integers(min_value=2023, max_value=2026)),
        month=draw(st.integers(min_value=1, max_value=12)),
        daily_query_counts=counts,
        daily_fx_rate=fx,
        daily_cost=cost,
        seed=draw(st.integers(min_value=0, max_value=2**31 - 1)),
    )


@st.composite
def three_way_decomposition_cells(draw: st.DrawFn) -> ThreeWayDecompositionCell:
    """Synthetic three-way decomposition cells. The strategy constructs
    an exact-identity cell: var_total is the sum of the three parts so
    identity_residual is exactly zero."""
    var_fx = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    var_q = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    cov_term = draw(st.floats(min_value=-0.5, max_value=0.5, allow_nan=False))
    var_total = var_fx + var_q + cov_term
    return ThreeWayDecompositionCell(
        currency=draw(st.sampled_from(PANEL_CURRENCIES)),
        year=draw(st.integers(min_value=2023, max_value=2026)),
        month=draw(st.integers(min_value=1, max_value=12)),
        var_total=var_total,
        var_fx=var_fx,
        var_q=var_q,
        cov_term=cov_term,
        grid_index_length=draw(st.integers(min_value=15, max_value=23)),
        identity_residual=0.0,
    )


@st.composite
def surface_grid_points(draw: st.DrawFn) -> SurfaceGridPoint:
    """Synthetic surface grid points."""
    share = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    half = draw(st.floats(min_value=0.0, max_value=0.2, allow_nan=False))
    return SurfaceGridPoint(
        q_volume=draw(
            st.floats(min_value=100.0, max_value=39_900.0, allow_nan=False)
        ),
        fx_variance_share=share,
        band_low=max(0.0, share - half),
        band_high=min(1.0, share + half),
        below_break_even=draw(st.booleans()),
    )


@st.composite
def surface_grid_results(draw: st.DrawFn) -> SurfaceGridResult:
    """Synthetic surface-grid results."""
    points = tuple(
        draw(st.lists(surface_grid_points(), min_size=2, max_size=20))
    )
    return SurfaceGridResult(
        points=points,
        break_even_share=draw(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
        ),
        grid_resolution=draw(
            st.floats(min_value=1.0, max_value=1_000.0, allow_nan=False)
        ),
        interior_crossing=draw(st.booleans()),
        crossing_q_volumes=(),
        anchored_range_low=draw(
            st.floats(min_value=100.0, max_value=1_000.0, allow_nan=False)
        ),
        anchored_range_high=draw(
            st.floats(min_value=1_001.0, max_value=39_900.0, allow_nan=False)
        ),
    )


@st.composite
def descriptive_verdict_results(draw: st.DrawFn) -> DescriptiveVerdictResult:
    """Synthetic descriptive-verdict results across the §9 ladder."""
    return DescriptiveVerdictResult(
        verdict=draw(st.sampled_from(list(DescriptiveVerdict))),
        surface_computed=draw(st.booleans()),
        material_gap=draw(st.booleans()),
        simulator_anchored=draw(st.booleans()),
        q_variance_dominates=draw(st.booleans()),
        interior_crossing=draw(st.booleans()),
        dv_gate_passed=draw(st.booleans()),
        rationale=draw(st.text(max_size=200)),
    )
