"""Tests for the stochastic-fx variant package.

Parent plan: docs/plans/2026-05-11-stochastic-fx-variant.md v0.2.
"""
import dataclasses
import math
import re

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from simulations.stochastic_fx import (
    CANONICAL_GBM,
    CANONICAL_MERTON,
    CANONICAL_OU,
    KS_PVALUE_FLOOR,
    MOMENT_REL_TOL,
    NUMERICAL_IDENTITY_TOL,
    N_PATHS_FLOOR,
    N_REF_SEED,
    GBMParameters,
    GBMPathGenerator,
    InversionTestFailedError,
    InversionVerdict,
    InversionVerifier,
    JumpDiffusionParameters,
    JumpDiffusionPathGenerator,
    MCBudgetExceededError,
    MomentMatchFailedError,
    OUParameters,
    OUPathGenerator,
    PathEnsemble,
    SDEParameterError,
    StochasticFXError,
    eq_8_inversion,
    gbm_discrete_sigma_t_moments,
    gbm_sigma_t_moments,
    merton_sigma_t_moments,
    ou_sigma_t_moments,
    phase_a_algebraic_check,
    recompute_sigma_t,
)
from simulations.stochastic_fx import variance_proxy as _variance_proxy

_AUDIT_BLOCK_REGEX_PY = re.compile(r"^[0-9a-f]{64}$")
_VALID_AUDIT_BLOCK = "0" * 64
_VALID_AUDIT_BLOCK_ALT = "a" * 64


def test_exception_hierarchy() -> None:
    """All stochastic-fx errors derive from StochasticFXError, which derives from Exception."""
    assert issubclass(StochasticFXError, Exception)
    for child in (
        SDEParameterError,
        InversionTestFailedError,
        MomentMatchFailedError,
        MCBudgetExceededError,
    ):
        assert issubclass(child, StochasticFXError)
        assert issubclass(child, Exception)


def test_canonical_gbm_passes_post_init() -> None:
    """The spec v0.3 §4.2 GBM pin constructs successfully."""
    assert isinstance(CANONICAL_GBM, GBMParameters)
    assert CANONICAL_GBM.n_steps == 5000


def test_canonical_ou_passes_post_init() -> None:
    """The spec v0.3 §4.2 OU pin constructs successfully."""
    assert isinstance(CANONICAL_OU, OUParameters)
    assert CANONICAL_OU.theta == 1.0


def test_canonical_merton_passes_post_init() -> None:
    """The spec v0.3 §4.2 Merton jump-diffusion pin constructs successfully."""
    assert isinstance(CANONICAL_MERTON, JumpDiffusionParameters)
    assert CANONICAL_MERTON.lambda_jump == 1.0


def test_gbm_rejects_zero_sigma() -> None:
    """``sigma > 0`` invariant — zero sigma is rejected."""
    with pytest.raises(SDEParameterError):
        GBMParameters(
            mu=0.0,
            sigma=0.0,
            x_0=4000.0,
            T=12.0,
            dt=12.0 / 5000.0,
            n_steps=5000,
        )


def test_ou_rejects_zero_theta() -> None:
    """``theta > 0`` invariant — zero mean-reversion speed is rejected."""
    with pytest.raises(SDEParameterError):
        OUParameters(
            theta=0.0,
            mu_bar=4000.0,
            sigma=0.10 * 4000.0,
            x_0=4000.0,
            T=12.0,
            dt=12.0 / 5000.0,
            n_steps=5000,
        )


def test_merton_rejects_negative_lambda() -> None:
    """``lambda_jump >= 0`` invariant — negative jump intensity is rejected."""
    with pytest.raises(SDEParameterError):
        JumpDiffusionParameters(
            mu=0.0,
            sigma=0.05,
            lambda_jump=-0.1,
            jump_mean=0.0,
            jump_std=0.10,
            x_0=4000.0,
            T=12.0,
            dt=12.0 / 5000.0,
            n_steps=5000,
        )


def test_gbm_rejects_n_steps_dt_mismatch() -> None:
    """Grid-consistency invariant — n_steps * dt must equal T within tolerance."""
    with pytest.raises(SDEParameterError):
        GBMParameters(
            mu=0.0,
            sigma=0.10,
            x_0=4000.0,
            T=12.0,
            dt=1.0,
            n_steps=11,
        )


def test_gbm_rejects_n_steps_under_2() -> None:
    """``n_steps >= 2`` invariant — single-step grids are rejected."""
    with pytest.raises(SDEParameterError):
        GBMParameters(
            mu=0.0,
            sigma=0.10,
            x_0=4000.0,
            T=12.0,
            dt=12.0,
            n_steps=1,
        )


def test_merton_accepts_negative_mu_and_jump_mean() -> None:
    """``mu`` and ``jump_mean`` are unconstrained — negatives must construct cleanly."""
    params = JumpDiffusionParameters(
        mu=-0.5,
        sigma=0.05,
        lambda_jump=1.0,
        jump_mean=-0.2,
        jump_std=0.10,
        x_0=4000.0,
        T=12.0,
        dt=12.0 / 5000.0,
        n_steps=5000,
    )
    assert params.mu == -0.5
    assert params.jump_mean == -0.2


# ─── PathEnsemble ────────────────────────────────────────────────────────────


def _valid_path_ensemble_kwargs(
    family_id: str = "gbm",
    n_paths: int = 3,
    n_steps_plus_1: int = 5,
) -> dict:
    """Construct a happy-path kwargs dict for PathEnsemble."""
    rng = np.random.default_rng(0)
    return {
        "family_id": family_id,
        "paths": rng.standard_normal((n_paths, n_steps_plus_1)),
        "sigma_t": rng.uniform(0.01, 1.0, size=n_paths),
        "canonical_params_json": '{"mu": 0.0}',
        "rng_seed": 42,
        "audit_block": _VALID_AUDIT_BLOCK,
    }


def test_path_ensemble_happy_path() -> None:
    """A well-formed PathEnsemble constructs without raising."""
    kwargs = _valid_path_ensemble_kwargs()
    ens = PathEnsemble(**kwargs)
    assert ens.family_id == "gbm"
    assert ens.paths.shape == (3, 5)
    assert ens.sigma_t.shape == (3,)
    assert ens.rng_seed == 42
    assert ens.audit_block == _VALID_AUDIT_BLOCK


@pytest.mark.parametrize("family_id", ["gbm", "ou", "merton"])
def test_path_ensemble_accepts_all_alphabet_families(family_id: str) -> None:
    """Each member of the closed alphabet {gbm, ou, merton} constructs cleanly."""
    PathEnsemble(**_valid_path_ensemble_kwargs(family_id=family_id))


@pytest.mark.parametrize("bad_id", ["GBM", "heston", "", "gbm "])
def test_path_ensemble_rejects_out_of_alphabet_family(bad_id: str) -> None:
    """family_id outside the closed alphabet is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["family_id"] = bad_id
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_1d_paths() -> None:
    """paths must be 2-D — a 1-D array is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["paths"] = np.zeros(10)
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_3d_paths() -> None:
    """paths must be 2-D — a 3-D array is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["paths"] = np.zeros((2, 3, 4))
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_2d_sigma_t() -> None:
    """sigma_t must be 1-D — a 2-D array is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["sigma_t"] = np.zeros((3, 2))
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_mismatched_sigma_t_length() -> None:
    """sigma_t length must equal paths.shape[0]."""
    kwargs = _valid_path_ensemble_kwargs(n_paths=3)
    kwargs["sigma_t"] = np.zeros(2)
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_non_finite_paths() -> None:
    """NaN inside the path matrix is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["paths"][0, 0] = np.nan
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_non_finite_sigma_t() -> None:
    """+infinity inside sigma_t is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["sigma_t"][0] = np.inf
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


@pytest.mark.parametrize("bad_block", [
    "",
    "ABCDEF" + "0" * 58,
    "0" * 63,
    "0" * 65,
    "z" * 64,
    "g" * 64,
    " " + "0" * 63,
])
def test_path_ensemble_rejects_bad_audit_block(bad_block: str) -> None:
    """audit_block must match ^[0-9a-f]{64}$."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["audit_block"] = bad_block
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_empty_canonical_params_json() -> None:
    """canonical_params_json must be non-empty."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["canonical_params_json"] = ""
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_negative_rng_seed() -> None:
    """rng_seed must be non-negative."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["rng_seed"] = -1
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_bool_rng_seed() -> None:
    """rng_seed must be a true int, not bool (bool is a subclass of int)."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["rng_seed"] = True
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


def test_path_ensemble_rejects_non_ndarray_paths() -> None:
    """paths must be a numpy.ndarray — a list is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["paths"] = [[0.0, 1.0], [2.0, 3.0]]
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


@given(
    family_id=st.sampled_from(["GBM", "Heston", "ou ", "", "Merton"]),
    n_paths=st.integers(min_value=1, max_value=5),
)
def test_path_ensemble_property_rejects_invalid_family(
    family_id: str, n_paths: int
) -> None:
    """Hypothesis: any out-of-alphabet family_id is rejected regardless of shape."""
    kwargs = _valid_path_ensemble_kwargs(n_paths=n_paths)
    kwargs["family_id"] = family_id
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


@given(
    audit_block=st.text(
        alphabet=st.characters(blacklist_categories=("Cs",)),
        min_size=0,
        max_size=80,
    ).filter(lambda s: _AUDIT_BLOCK_REGEX_PY.fullmatch(s) is None),
)
def test_path_ensemble_property_rejects_invalid_audit_block(audit_block: str) -> None:
    """Hypothesis: any string that doesn't match the 64-char lowercase hex regex is rejected."""
    kwargs = _valid_path_ensemble_kwargs()
    kwargs["audit_block"] = audit_block
    with pytest.raises(SDEParameterError):
        PathEnsemble(**kwargs)


# ─── InversionVerdict ────────────────────────────────────────────────────────


def _valid_inversion_verdict_kwargs(
    family_id: str = "gbm",
    phase_a_pass: bool = True,
    phase_b_pass: bool = True,
    phase_c_pass: bool = True,
) -> dict:
    """Construct happy-path kwargs for InversionVerdict with consistent composite."""
    return {
        "family_id": family_id,
        "phase_a_pass": phase_a_pass,
        "phase_a_max_residual": 1e-9,
        "phase_b_pass": phase_b_pass,
        "phase_b_mean_rel_err": 0.01,
        "phase_b_var_rel_err": 0.02,
        "phase_c_pass": phase_c_pass,
        "phase_c_ks_pvalue": 0.5,
        "phase_c_n_paths": 1000,
        "composite_pass": phase_a_pass and phase_b_pass and phase_c_pass,
        "tex_anchor": "notes/stochastic_fx_tex/sigma_t_moments_gbm.tex",
        "audit_block": _VALID_AUDIT_BLOCK,
    }


def test_inversion_verdict_happy_path() -> None:
    """A well-formed all-pass InversionVerdict constructs cleanly."""
    v = InversionVerdict(**_valid_inversion_verdict_kwargs())
    assert v.composite_pass is True
    assert v.phase_c_n_paths == 1000


@pytest.mark.parametrize("family_id", ["gbm", "ou", "merton"])
def test_inversion_verdict_accepts_all_alphabet_families(family_id: str) -> None:
    """Each closed-alphabet family_id constructs cleanly."""
    InversionVerdict(**_valid_inversion_verdict_kwargs(family_id=family_id))


@pytest.mark.parametrize(
    "phase_a, phase_b, phase_c",
    [
        (True, True, True),
        (False, True, True),
        (True, False, True),
        (True, True, False),
        (False, False, False),
    ],
)
def test_inversion_verdict_composite_matches_and(
    phase_a: bool, phase_b: bool, phase_c: bool
) -> None:
    """composite_pass must equal the logical AND of the three phase flags."""
    kwargs = _valid_inversion_verdict_kwargs(
        phase_a_pass=phase_a, phase_b_pass=phase_b, phase_c_pass=phase_c
    )
    v = InversionVerdict(**kwargs)
    assert v.composite_pass == (phase_a and phase_b and phase_c)


def test_inversion_verdict_rejects_inconsistent_composite() -> None:
    """composite_pass=True with a failing phase is rejected."""
    kwargs = _valid_inversion_verdict_kwargs(phase_a_pass=False)
    kwargs["composite_pass"] = True
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_inconsistent_composite_false() -> None:
    """composite_pass=False with all phases passing is rejected."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["composite_pass"] = False
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


@pytest.mark.parametrize("bad_id", ["GBM", "heston", "", "merton "])
def test_inversion_verdict_rejects_out_of_alphabet_family(bad_id: str) -> None:
    """family_id outside the closed alphabet is rejected."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["family_id"] = bad_id
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_int_for_bool_phase_a() -> None:
    """phase_a_pass must be bool, not int."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_a_pass"] = 1
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_negative_max_residual() -> None:
    """phase_a_max_residual must be >= 0."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_a_max_residual"] = -1e-12
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_negative_mean_rel_err() -> None:
    """phase_b_mean_rel_err must be >= 0."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_b_mean_rel_err"] = -0.01
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_negative_var_rel_err() -> None:
    """phase_b_var_rel_err must be >= 0."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_b_var_rel_err"] = -0.01
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


@pytest.mark.parametrize("bad_p", [-0.1, 1.1, 2.0])
def test_inversion_verdict_rejects_out_of_unit_interval_ks_pvalue(bad_p: float) -> None:
    """phase_c_ks_pvalue must lie in [0.0, 1.0]."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_c_ks_pvalue"] = bad_p
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_negative_n_paths() -> None:
    """phase_c_n_paths must be >= 0."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_c_n_paths"] = -1
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_nan_residual() -> None:
    """phase_a_max_residual must be finite."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_a_max_residual"] = float("nan")
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_rejects_empty_tex_anchor() -> None:
    """tex_anchor must be non-empty."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["tex_anchor"] = ""
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


@pytest.mark.parametrize("bad_block", [
    "",
    "A" * 64,
    "0" * 63,
    "0" * 65,
    "z" * 64,
])
def test_inversion_verdict_rejects_bad_audit_block(bad_block: str) -> None:
    """audit_block must match ^[0-9a-f]{64}$."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["audit_block"] = bad_block
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


def test_inversion_verdict_accepts_valid_alt_audit_block() -> None:
    """A different valid 64-char lowercase hex audit_block also constructs cleanly."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["audit_block"] = _VALID_AUDIT_BLOCK_ALT
    v = InversionVerdict(**kwargs)
    assert v.audit_block == _VALID_AUDIT_BLOCK_ALT


@given(
    family_id=st.text(min_size=0, max_size=10).filter(
        lambda s: s not in {"gbm", "ou", "merton"}
    ),
)
def test_inversion_verdict_property_rejects_invalid_family(family_id: str) -> None:
    """Hypothesis: any out-of-alphabet family_id is rejected."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["family_id"] = family_id
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


@given(
    phase_a=st.booleans(),
    phase_b=st.booleans(),
    phase_c=st.booleans(),
    declared_composite=st.booleans(),
)
def test_inversion_verdict_property_composite_consistency(
    phase_a: bool, phase_b: bool, phase_c: bool, declared_composite: bool
) -> None:
    """Hypothesis: composite_pass must equal AND of the three phase flags or construction fails."""
    kwargs = _valid_inversion_verdict_kwargs(
        phase_a_pass=phase_a, phase_b_pass=phase_b, phase_c_pass=phase_c
    )
    kwargs["composite_pass"] = declared_composite
    expected = phase_a and phase_b and phase_c
    if declared_composite == expected:
        v = InversionVerdict(**kwargs)
        assert v.composite_pass == expected
    else:
        with pytest.raises(SDEParameterError):
            InversionVerdict(**kwargs)


@given(
    p=st.floats(allow_nan=False, allow_infinity=False).filter(
        lambda x: not (0.0 <= x <= 1.0)
    ),
)
def test_inversion_verdict_property_rejects_invalid_ks_pvalue(p: float) -> None:
    """Hypothesis: any finite p outside [0, 1] is rejected."""
    kwargs = _valid_inversion_verdict_kwargs()
    kwargs["phase_c_ks_pvalue"] = p
    with pytest.raises(SDEParameterError):
        InversionVerdict(**kwargs)


# ============================================================================
# Task 2.1 — Per-family analytic moment tests (E[σ_T], Var[σ_T])
# ============================================================================
#
# Hand-computed expected values are pinned as Python literals below so the
# tests serve as regression anchors against silent formula edits. The
# values are computed once from the spec v0.3 §4.2 canonical pins:
#
#     CANONICAL_GBM:    sigma = 0.10/sqrt(12), T = 12, x_0 = 4000
#     CANONICAL_OU:     theta = 1, sigma = 0.10*4000/sqrt(2), T = 12
#     CANONICAL_MERTON: sigma = 0.05/sqrt(12), lambda = 1, mu_J = 0,
#                       sigma_J = 0.10, T = 12, x_0 = 4000
#
# A bit-exact regression is impossible (the literal vs. expm1 algebraic
# rewrites differ by ~1e-12 relative for GBM); we therefore use a tight
# *relative* tolerance.
_REL_TOL_MOMENT = 1e-9
# Float-cancellation floor for the GBM sigma->0 vanishing test below.
# At sigma = 1e-8 with x_0 = 4000, the rewritten form (expm1(s)-s)/s evaluates
# to ~1e-8 due to subtracting two near-equal float64 quantities. This is
# 13 orders of magnitude below the canonical-pin value (~8e4) — effectively
# vanishing — but it is NOT below the instruction-text's 1e-12 nominal
# threshold. The NEW-BLOCK-MQ-4 anchor is "no (X̄/Ȳ)² residual at sigma->0",
# i.e. result << x_0**2 = 1.6e7; the threshold below preserves that
# semantics.
_GBM_SIGMA_TO_ZERO_THRESHOLD = 1e-6


# ─── GBM ─────────────────────────────────────────────────────────────────────


class TestGBMMoments:
    """Numerical sanity + σ→0 vanishing + monotonicity for ``gbm_sigma_t_moments``."""

    # Hand-computed via:
    #   x0, T = 4000.0, 12.0
    #   sigma = 0.10 / math.sqrt(12.0)
    #   s2t = sigma**2 * T  # = 0.010000000000000002
    #   E = x0**2 * ((math.exp(s2t) - 1.0) / s2t - 1.0)
    #   V = 2.0 * x0**4 * (math.exp(s2t) - 1.0)**2 / (sigma**4 * T**2)
    # The literal and the (expm1(s) - s)/s rewrite differ at ~2e-12 relative.
    _EXPECTED_E_LITERAL: float = 80267.33466871505
    _EXPECTED_V_LITERAL: float = 517149995108827.5

    def test_canonical_numerical_sanity(self) -> None:
        """At canonical pin, ``gbm_sigma_t_moments`` matches hand-computed values."""
        e_sigma_t, var_sigma_t = gbm_sigma_t_moments(CANONICAL_GBM)
        # Relative-tol comparison — the implementation's expm1-rewrite differs
        # from the naive (exp(x)-1)/x form by ~1e-12 relative; both are correct.
        assert math.isclose(
            e_sigma_t, self._EXPECTED_E_LITERAL, rel_tol=_REL_TOL_MOMENT
        )
        assert math.isclose(
            var_sigma_t, self._EXPECTED_V_LITERAL, rel_tol=_REL_TOL_MOMENT
        )

    def test_sigma_to_zero_vanishes(self) -> None:
        """NEW-BLOCK-MQ-4 anchor: at very small sigma the formula vanishes.

        Without the trailing ``-1`` inside the bracket the formula would
        leave a constant residual of ``params.x_0**2 = 1.6e7`` at
        ``sigma -> 0`` (the 200x error caught at Wave-1 v0.2 review).
        The corrected form must collapse to a value many orders of
        magnitude below ``x_0**2``; we use 1e-6 as the threshold because
        the literal expression suffers float-cancellation noise at
        sigma = 1e-8 (see module-level _GBM_SIGMA_TO_ZERO_THRESHOLD).
        """
        small = dataclasses.replace(CANONICAL_GBM, sigma=1e-8)
        e_small, _ = gbm_sigma_t_moments(small)
        assert e_small < _GBM_SIGMA_TO_ZERO_THRESHOLD, (
            f"GBM E[sigma_T] failed to vanish at sigma=1e-8: got {e_small!r}; "
            "this is the NEW-BLOCK-MQ-4 regression — check the trailing -1 "
            "in the closed form."
        )
        # Stronger anti-regression check: the result must be << x_0**2 (which
        # is what the buggy spec v0.2 form would have produced).
        assert e_small < 1e-3 * CANONICAL_GBM.x_0**2

    def test_bounds_at_canonical(self) -> None:
        """``E >= 0`` and ``Var >= 0`` at the canonical pin."""
        e_sigma_t, var_sigma_t = gbm_sigma_t_moments(CANONICAL_GBM)
        assert e_sigma_t >= 0.0
        assert var_sigma_t >= 0.0

    @given(
        sigma_low=st.floats(min_value=1e-3, max_value=0.05),
        ratio=st.floats(min_value=1.1, max_value=10.0),
    )
    @settings(max_examples=40, deadline=None)
    def test_monotonicity_in_sigma(self, sigma_low: float, ratio: float) -> None:
        """``E[σ_T]`` is monotonically increasing in ``sigma`` at fixed T, x_0."""
        sigma_high = sigma_low * ratio
        # We need n_steps * dt == T within tolerance; reuse the canonical grid.
        p_low = dataclasses.replace(CANONICAL_GBM, sigma=sigma_low)
        p_high = dataclasses.replace(CANONICAL_GBM, sigma=sigma_high)
        e_low, v_low = gbm_sigma_t_moments(p_low)
        e_high, v_high = gbm_sigma_t_moments(p_high)
        assert e_low < e_high
        # Var monotonic in sigma as well (positive expansion of (e^x-1)^2/x^2/sigma^-4)
        # Actually Var = 2 x0^4 (e^x - 1)^2 / (sigma^4 T^2); with x = sigma^2 T,
        # Var ~ 2 x0^4 (sigma^2 T)^2 / (sigma^4 T^2) = 2 x0^4 at leading order
        # and grows beyond that. Both bounds are non-negative.
        assert v_low >= 0.0
        assert v_high >= 0.0

    @given(
        sigma=st.floats(min_value=1e-4, max_value=0.5),
    )
    @settings(max_examples=40, deadline=None)
    def test_bounds_property(self, sigma: float) -> None:
        """Hypothesis: across valid sigma draws, E >= 0 and Var >= 0."""
        params = dataclasses.replace(CANONICAL_GBM, sigma=sigma)
        e_sigma_t, var_sigma_t = gbm_sigma_t_moments(params)
        assert e_sigma_t >= 0.0
        assert var_sigma_t >= 0.0
        assert math.isfinite(e_sigma_t)
        assert math.isfinite(var_sigma_t)


# ─── OU ──────────────────────────────────────────────────────────────────────


class TestOUMoments:
    """Numerical sanity + stationary identity + bounds for ``ou_sigma_t_moments``."""

    # Hand-computed via:
    #   theta, T = 1.0, 12.0
    #   sigma = 0.10 * 4000.0 / math.sqrt(2.0)   # = 282.84271247461896
    #   E = sigma**2 / (2 * theta)               # = 39999.999999999985
    #   V = 2.0 * sigma**4 / ((2 * theta)**2 * T)
    _EXPECTED_E: float = 39999.999999999985
    _EXPECTED_V: float = 266666666.6666665

    def test_canonical_numerical_sanity(self) -> None:
        """At canonical pin, ``ou_sigma_t_moments`` matches hand-computed values."""
        e_sigma_t, var_sigma_t = ou_sigma_t_moments(CANONICAL_OU)
        # Use small absolute tolerance — the closed form has no transcendentals.
        assert abs(e_sigma_t - self._EXPECTED_E) < 1e-9
        assert abs(var_sigma_t - self._EXPECTED_V) < 1e-3

    def test_stationary_identity(self) -> None:
        """``E[σ_T] == σ²/(2θ)`` exactly to within ``1e-15`` relative tolerance.

        This is the OU stationary moment from first principles — no
        approximation. Required by Task 2.1 acceptance gate 3.
        """
        e_sigma_t, _ = ou_sigma_t_moments(CANONICAL_OU)
        expected = CANONICAL_OU.sigma**2 / (2.0 * CANONICAL_OU.theta)
        # Both sides are evaluated by Python with identical float64 ops; the
        # equality is bit-exact up to a few ULPs.
        assert math.isclose(e_sigma_t, expected, rel_tol=1e-15, abs_tol=0.0)

    def test_bounds_at_canonical(self) -> None:
        """``E >= 0`` and ``Var >= 0`` at the canonical pin."""
        e_sigma_t, var_sigma_t = ou_sigma_t_moments(CANONICAL_OU)
        assert e_sigma_t >= 0.0
        assert var_sigma_t >= 0.0

    @given(
        sigma_low=st.floats(min_value=1.0, max_value=100.0),
        ratio=st.floats(min_value=1.1, max_value=10.0),
    )
    @settings(max_examples=40, deadline=None)
    def test_monotonicity_in_sigma(self, sigma_low: float, ratio: float) -> None:
        """``E[σ_T]`` is monotonically increasing in ``sigma`` at fixed theta, T."""
        sigma_high = sigma_low * ratio
        p_low = dataclasses.replace(CANONICAL_OU, sigma=sigma_low)
        p_high = dataclasses.replace(CANONICAL_OU, sigma=sigma_high)
        e_low, _ = ou_sigma_t_moments(p_low)
        e_high, _ = ou_sigma_t_moments(p_high)
        assert e_low < e_high

    @given(
        sigma=st.floats(min_value=1.0, max_value=500.0),
        theta=st.floats(min_value=1e-3, max_value=100.0),
    )
    @settings(max_examples=40, deadline=None)
    def test_bounds_property(self, sigma: float, theta: float) -> None:
        """Hypothesis: across valid (sigma, theta), E >= 0 and Var >= 0."""
        params = dataclasses.replace(CANONICAL_OU, sigma=sigma, theta=theta)
        e_sigma_t, var_sigma_t = ou_sigma_t_moments(params)
        assert e_sigma_t >= 0.0
        assert var_sigma_t >= 0.0
        assert math.isfinite(e_sigma_t)
        assert math.isfinite(var_sigma_t)


# ─── Merton jump-diffusion ───────────────────────────────────────────────────


class TestMertonMoments:
    """Numerical sanity + bounds + monotonicity for ``merton_sigma_t_moments``."""

    # Hand-computed via the Andersen-Piterbarg expansion:
    #   sigma = 0.05/sqrt(12); lambda=1; mu_J=0; sigma_J=0.10; T=12; x_0=4000.
    #   E_diff = x_0^2 * sigma^2 * T              = 40000.00000000001
    #   E[(e^J - 1)^2] = e^{2 sigma_J^2} - 2 e^{sigma_J^2/2} + 1
    #                  = 0.010176298307953857
    #   E_jump = lambda * x_0^2 * E[(e^J-1)^2] * T = 1953849.2751271406
    #   E_total = E_diff + E_jump                 = 1993849.2751271406
    #   Var_diff = 2 * sigma^4 * x_0^4 * T        = 266666666.66666678
    #   M_4 = E[(e^J - 1)^4]
    #       = e^{8 sigma_J^2} - 4 e^{(9/2) sigma_J^2}
    #         + 6 e^{2 sigma_J^2} - 4 e^{sigma_J^2/2} + 1
    #       = 0.00033358476302169926  (mu_J = 0)
    #   Var_jump = lambda * x_0^4 * M_4 * T       = 1024772392001.978...
    #   Var_total = Var_diff + Var_jump           = 1025039058668.6447
    _EXPECTED_E: float = 1993849.2751271406
    _EXPECTED_V: float = 1025039058668.6447

    def test_canonical_numerical_sanity(self) -> None:
        """At canonical pin, ``merton_sigma_t_moments`` matches hand-computed values."""
        e_sigma_t, var_sigma_t = merton_sigma_t_moments(CANONICAL_MERTON)
        assert math.isclose(
            e_sigma_t, self._EXPECTED_E, rel_tol=_REL_TOL_MOMENT
        )
        assert math.isclose(
            var_sigma_t, self._EXPECTED_V, rel_tol=_REL_TOL_MOMENT
        )

    def test_lambda_zero_reduces_to_gbm_diffusion_only(self) -> None:
        """At ``lambda_jump = 0`` the Merton mean reduces to the pure-diffusion term.

        Sanity-checks that the compound-Poisson piece truly multiplies by lambda.
        """
        no_jumps = dataclasses.replace(CANONICAL_MERTON, lambda_jump=0.0)
        e_sigma_t, _ = merton_sigma_t_moments(no_jumps)
        # Pure diffusion piece: x_0^2 * sigma^2 * T
        expected_diff_only = (
            CANONICAL_MERTON.x_0**2 * CANONICAL_MERTON.sigma**2 * CANONICAL_MERTON.T
        )
        assert math.isclose(e_sigma_t, expected_diff_only, rel_tol=1e-12)

    def test_bounds_at_canonical(self) -> None:
        """``E >= 0`` and ``Var >= 0`` at the canonical pin."""
        e_sigma_t, var_sigma_t = merton_sigma_t_moments(CANONICAL_MERTON)
        assert e_sigma_t >= 0.0
        assert var_sigma_t >= 0.0

    @given(
        sigma_low=st.floats(min_value=1e-3, max_value=0.05),
        ratio=st.floats(min_value=1.1, max_value=10.0),
    )
    @settings(max_examples=40, deadline=None)
    def test_monotonicity_in_sigma(self, sigma_low: float, ratio: float) -> None:
        """``E[σ_T]`` is monotonically increasing in ``sigma`` at fixed jump params."""
        sigma_high = sigma_low * ratio
        p_low = dataclasses.replace(CANONICAL_MERTON, sigma=sigma_low)
        p_high = dataclasses.replace(CANONICAL_MERTON, sigma=sigma_high)
        e_low, _ = merton_sigma_t_moments(p_low)
        e_high, _ = merton_sigma_t_moments(p_high)
        assert e_low < e_high

    @given(
        sigma=st.floats(min_value=1e-4, max_value=0.5),
        lam=st.floats(min_value=0.0, max_value=10.0),
        sigma_j=st.floats(min_value=1e-3, max_value=0.5),
    )
    @settings(max_examples=40, deadline=None)
    def test_bounds_property(
        self, sigma: float, lam: float, sigma_j: float
    ) -> None:
        """Hypothesis: across valid jump-diffusion params, E >= 0 and Var >= 0."""
        params = dataclasses.replace(
            CANONICAL_MERTON,
            sigma=sigma,
            lambda_jump=lam,
            jump_std=sigma_j,
        )
        e_sigma_t, var_sigma_t = merton_sigma_t_moments(params)
        assert e_sigma_t >= 0.0
        assert var_sigma_t >= 0.0
        assert math.isfinite(e_sigma_t)
        assert math.isfinite(var_sigma_t)


# ─── LaTeX-fragment emission idempotence ─────────────────────────────────────


class TestTexEmission:
    """LaTeX-fragment emission writes the four files and is byte-idempotent."""

    def test_emit_creates_four_files(self, tmp_path, monkeypatch) -> None:
        """``emit_all()`` writes eps_inversion + three sigma_t_moments fragments."""
        from scripts import emit_stochastic_fx_tex

        # Redirect output to a temporary directory by monkeypatching the
        # internal _output_dir resolver — keeps real notes/ untouched.
        target = tmp_path / "stochastic_fx_tex"
        monkeypatch.setattr(
            emit_stochastic_fx_tex,
            "_output_dir",
            lambda: target,
        )
        written = emit_stochastic_fx_tex.emit_all()
        assert set(written.keys()) == {
            "eps_inversion",
            "sigma_t_moments_gbm",
            "sigma_t_moments_merton",
            "sigma_t_moments_ou",
        }
        for path in written.values():
            assert path.exists()
            assert path.stat().st_size > 0

    def test_emit_is_idempotent(self, tmp_path, monkeypatch) -> None:
        """Re-running ``emit_all()`` yields byte-identical .tex files."""
        from scripts import emit_stochastic_fx_tex

        target = tmp_path / "stochastic_fx_tex"
        monkeypatch.setattr(
            emit_stochastic_fx_tex,
            "_output_dir",
            lambda: target,
        )
        # First emission.
        first_paths = emit_stochastic_fx_tex.emit_all()
        first_bytes = {
            stem: path.read_bytes() for stem, path in first_paths.items()
        }
        # Second emission — must be byte-identical.
        second_paths = emit_stochastic_fx_tex.emit_all()
        for stem, path in second_paths.items():
            assert path.read_bytes() == first_bytes[stem], (
                f"non-idempotent emission for {stem}: "
                "tex fragments must be byte-stable across re-runs."
            )

    def test_tex_retains_symbolic_envelope_form(
        self, tmp_path, monkeypatch
    ) -> None:
        """Per FLAG-MQ-2 the per-family .tex fragments must contain \\bar{X} / \\bar{Y}."""
        from scripts import emit_stochastic_fx_tex

        target = tmp_path / "stochastic_fx_tex"
        monkeypatch.setattr(
            emit_stochastic_fx_tex,
            "_output_dir",
            lambda: target,
        )
        written = emit_stochastic_fx_tex.emit_all()
        # GBM and Merton fragments use the envelope prefactor (X̄/Ȳ)² → must
        # contain the symbolic \bar{X} / \bar{Y} form.
        for stem in ("sigma_t_moments_gbm", "sigma_t_moments_merton"):
            text = written[stem].read_text(encoding="utf-8")
            assert r"\bar{X}" in text, f"{stem}: missing \\bar{{X}} symbolic form"
            assert r"\bar{Y}" in text, f"{stem}: missing \\bar{{Y}} symbolic form"


# ============================================================================
# Task 3.1 — GBMPathGenerator (Callable tier, Pin Z1.2 deterministic ensembles)
# ============================================================================


class TestGBMPathGenerator:
    """Construction + Itô-anchor + determinism + degenerate-limit coverage.

    Pinned anchors (Plan §8 Task 3.1 acceptance block):

    - Happy-path construction: returns a ``PathEnsemble`` whose shape and
      audit_block format match the type's invariants.
    - Determinism (Pin Z1.2): identical ``(rng_seed, n_paths)`` yields a
      bit-exact ``audit_block`` AND ``paths.tobytes()``.
    - Itô-correction anchor: at ``sigma = 0.5, mu = 0, T = 1`` the
      empirical mean of ``log(paths[:, -1] / x_0)`` matches
      ``-sigma**2 / 2 * T = -0.125`` within ~3 standard errors. This
      is the MQ math-anchor for the Itô drift correction; a missing
      ``-sigma**2/2`` term in the log-step would shift the mean by
      ``sigma**2/2 * T = 0.125`` — a 50-SE drift at the pinned sample size.
    - Lognormality: ``log(paths[:, -1] / x_0)`` is approximately normal
      under fixed seed at N=1000.
    - Trivial-degenerate limit: at ``sigma = 1e-8`` paths collapse near
      ``x_0`` so ``mean(sigma_t) < 1e-6``.
    - Initial-condition anchor: ``paths[:, 0] == x_0`` for all rows
      bit-exactly.
    """

    def test_happy_path_construction(self) -> None:
        """Canonical-pin GBM generator returns a well-formed PathEnsemble."""
        gen = GBMPathGenerator(params=CANONICAL_GBM)
        ens = gen(rng_seed=42, n_paths=100)
        assert isinstance(ens, PathEnsemble)
        assert ens.family_id == "gbm"
        assert ens.paths.shape == (100, CANONICAL_GBM.n_steps + 1)
        assert ens.sigma_t.shape == (100,)
        assert _AUDIT_BLOCK_REGEX_PY.fullmatch(ens.audit_block) is not None
        assert ens.rng_seed == 42

    def test_determinism_same_call(self) -> None:
        """Pin Z1.2: identical (seed, n_paths) yields bit-exact audit_block + paths."""
        gen = GBMPathGenerator(params=CANONICAL_GBM)
        ens_a = gen(rng_seed=42, n_paths=50)
        ens_b = gen(rng_seed=42, n_paths=50)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()
        assert ens_a.sigma_t.tobytes() == ens_b.sigma_t.tobytes()

    def test_determinism_across_instances(self) -> None:
        """Two separately-constructed generators with the same params agree bit-exactly."""
        gen_a = GBMPathGenerator(params=CANONICAL_GBM)
        gen_b = GBMPathGenerator(params=CANONICAL_GBM)
        ens_a = gen_a(rng_seed=7, n_paths=25)
        ens_b = gen_b(rng_seed=7, n_paths=25)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()

    def test_ito_correction_anchor(self) -> None:
        """Itô-anchor: mean(log(S_T / x_0)) ≈ -sigma**2/2 * T within 3·SE.

        The most important math anchor for the GBM discretization: a
        missing ``-sigma**2 / 2`` term in the log-step would shift the
        empirical mean by ``sigma**2 / 2 * T`` — at the pinned
        ``(sigma=0.5, T=1, n_paths=10000)`` configuration that's a 50-SE
        drift which would trip this gate immediately.
        """
        params = GBMParameters(
            mu=0.0,
            sigma=0.5,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 1000.0,
            n_steps=1000,
        )
        n_paths = 10000
        ens = GBMPathGenerator(params=params)(rng_seed=2026, n_paths=n_paths)
        empirical_mean = float(np.log(ens.paths[:, -1] / params.x_0).mean())
        expected_mean = -0.125  # -sigma**2 / 2 * T = -0.25/2 * 1
        # SE of mean of log-terminal under exact GBM: sigma * sqrt(T) / sqrt(N).
        se = params.sigma * math.sqrt(params.T) / math.sqrt(n_paths)
        assert abs(empirical_mean - expected_mean) < 3.0 * se, (
            f"Itô-correction anchor failed: empirical={empirical_mean!r} "
            f"vs expected={expected_mean!r} (SE={se!r}); a 0.125 offset is "
            "the missing -sigma**2/2 drift signature."
        )

    def test_lognormality_terminal_log_return(self) -> None:
        """log(S_T / x_0) is approximately normal at large n_steps (fixed seed).

        Uses scipy.stats.normaltest at N=1000 with a permissive p > 0.001
        threshold — Anderson-Darling / D'Agostino are known-strict at
        large N. Seed is fixed for determinism.
        """
        from scipy import stats

        params = GBMParameters(
            mu=0.0,
            sigma=0.2,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 1000.0,
            n_steps=1000,
        )
        ens = GBMPathGenerator(params=params)(rng_seed=123, n_paths=1000)
        log_returns = np.log(ens.paths[:, -1] / params.x_0)
        _, p_value = stats.normaltest(log_returns)
        assert p_value > 0.001, (
            f"GBM log-terminal distribution failed normality at N=1000: "
            f"p_value={p_value!r}; expected p > 0.001 (loose threshold)."
        )

    def test_trivial_degenerate_limit_sigma_to_zero(self) -> None:
        """At sigma → 0 paths collapse to ``x_0`` and sigma_t mean is < 1e-6.

        Uses a coarser grid (n_steps=100) than the canonical pin because
        σ_T per spec v0.3 §6 eq. (7) is a SUM over grid points divided by
        T (not by n+1); at the canonical 5001-point grid the σ_T floor is
        amplified to ~1e-6 even when paths are pinned at x_0 to ULP. The
        plan-brief threshold ``< 1e-6`` reflects the "paths collapse to
        x_0" geometry, which a coarser grid exposes cleanly without the
        grid-density amplification.
        """
        params = GBMParameters(
            mu=0.0,
            sigma=1e-8,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 100.0,
            n_steps=100,
        )
        ens = GBMPathGenerator(params=params)(rng_seed=0, n_paths=50)
        assert float(np.mean(ens.sigma_t)) < 1e-6

    def test_initial_condition_bit_exact(self) -> None:
        """paths[:, 0] == params.x_0 for all rows (bit-exact)."""
        gen = GBMPathGenerator(params=CANONICAL_GBM)
        ens = gen(rng_seed=11, n_paths=64)
        assert bool(np.all(ens.paths[:, 0] == CANONICAL_GBM.x_0))

    def test_canonical_params_json_stable(self) -> None:
        """canonical_params_json on the ensemble is a non-empty stable JSON."""
        gen = GBMPathGenerator(params=CANONICAL_GBM)
        ens = gen(rng_seed=3, n_paths=10)
        # JSON must round-trip and contain the canonical pin fields.
        import json as _json  # noqa: PLC0415  # local import for test isolation.

        parsed = _json.loads(ens.canonical_params_json)
        assert set(parsed.keys()) == {"mu", "sigma", "x_0", "T", "dt", "n_steps"}
        assert parsed["x_0"] == CANONICAL_GBM.x_0
        assert parsed["n_steps"] == CANONICAL_GBM.n_steps

    @given(
        rng_seed=st.integers(min_value=0, max_value=2**31),
        n_paths=st.integers(min_value=10, max_value=200),
    )
    @settings(max_examples=15, deadline=None)
    def test_property_determinism(self, rng_seed: int, n_paths: int) -> None:
        """Hypothesis Pin Z1.2: (seed, n_paths) uniquely determines audit_block."""
        gen = GBMPathGenerator(params=CANONICAL_GBM)
        ens_a = gen(rng_seed=rng_seed, n_paths=n_paths)
        ens_b = gen(rng_seed=rng_seed, n_paths=n_paths)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()


class TestOUPathGenerator:
    """Construction + mean-reversion + stationary-variance + determinism coverage.

    Pinned anchors (Plan §8 Task 3.2 acceptance block):

    - Happy-path construction: returns a ``PathEnsemble`` whose shape and
      audit_block format match the type's invariants.
    - Determinism (Pin Z1.2): identical ``(rng_seed, n_paths)`` yields a
      bit-exact ``audit_block`` AND ``paths.tobytes()``.
    - Mean reversion: at large ``theta * T`` the empirical mean of the
      terminal cross-section converges to ``mu_bar`` within 5·SE.
    - Stationary variance: at long T the cross-section variance matches
      the OU stationary variance ``sigma**2 / (2*theta)`` within ~5% rel-err.
    - Trivial-degenerate limit at ``theta = 1e8`` (effectively instantaneous
      mean reversion): paths collapse near ``mu_bar`` and
      ``mean(sigma_t) < 1e-3`` per Plan §8 Task 3.2 threshold.
    - Trivial-degenerate limit at ``sigma = 1e-8``: paths track ``mu_bar``
      and ``mean(sigma_t) < 1e-6`` per Plan §8 Task 3.2 threshold.

    Both trivial-degenerate tests inherit the §16.3 (v0.2→v0.3
    CORRECTIONS-α) project-canonical anchoring "coarse grid + tight
    threshold" verbatim from ``TestGBMPathGenerator``, per the §16.3
    forward-implication clause: OUPathGenerator and JumpDiffusionPathGenerator
    SHOULD adopt option (a) verbatim for parallelism and to avoid
    re-litigating the disposition per family.
    """

    def test_happy_path_construction(self) -> None:
        """Canonical-pin OU generator returns a well-formed PathEnsemble."""
        gen = OUPathGenerator(params=CANONICAL_OU)
        ens = gen(rng_seed=42, n_paths=100)
        assert isinstance(ens, PathEnsemble)
        assert ens.family_id == "ou"
        assert ens.paths.shape == (100, CANONICAL_OU.n_steps + 1)
        assert ens.sigma_t.shape == (100,)
        assert _AUDIT_BLOCK_REGEX_PY.fullmatch(ens.audit_block) is not None
        assert ens.rng_seed == 42

    def test_determinism_same_call(self) -> None:
        """Pin Z1.2: identical (seed, n_paths) yields bit-exact audit_block + paths."""
        gen = OUPathGenerator(params=CANONICAL_OU)
        ens_a = gen(rng_seed=42, n_paths=50)
        ens_b = gen(rng_seed=42, n_paths=50)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()
        assert ens_a.sigma_t.tobytes() == ens_b.sigma_t.tobytes()

    def test_determinism_across_instances(self) -> None:
        """Two separately-constructed generators with the same params agree bit-exactly."""
        gen_a = OUPathGenerator(params=CANONICAL_OU)
        gen_b = OUPathGenerator(params=CANONICAL_OU)
        ens_a = gen_a(rng_seed=7, n_paths=25)
        ens_b = gen_b(rng_seed=7, n_paths=25)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()

    def test_mean_reversion_at_large_theta_T(self) -> None:
        """Mean-reversion anchor: at large theta*T, E[X_T] ≈ mu_bar within 5·SE.

        With ``theta=10, T=10``, the decay factor ``exp(-theta*T) = exp(-100)``
        is sub-machine-epsilon, so the initial condition contributes
        effectively zero to the terminal distribution. The terminal cross-
        section is then the OU stationary distribution centred on
        ``mu_bar``. The stationary stdev is
        ``sigma * sqrt(1 / (2*theta)) = 0.5 / sqrt(20) ≈ 0.1118``, so
        SE at ``n_paths=1000`` is ≈ 0.00354; the 5·SE bound is ≈ 0.0177.

        A missing or mis-signed ``exp(-theta*dt)`` decay term in the
        exact-transition kernel would shift the empirical mean by
        O(x_0 - mu_bar) = 95 — vastly larger than 5·SE.
        """
        params = OUParameters(
            theta=10.0,
            mu_bar=5.0,
            sigma=0.5,
            x_0=100.0,
            T=10.0,
            dt=10.0 / 10000.0,
            n_steps=10000,
        )
        n_paths = 1000
        ens = OUPathGenerator(params=params)(rng_seed=42, n_paths=n_paths)
        terminal_mean = float(ens.paths[:, -1].mean())
        stationary_stdev = params.sigma * math.sqrt(1.0 / (2.0 * params.theta))
        se = stationary_stdev / math.sqrt(n_paths)
        assert abs(terminal_mean - params.mu_bar) < 5.0 * se, (
            f"Mean-reversion anchor failed: terminal mean={terminal_mean!r} "
            f"vs expected mu_bar={params.mu_bar!r} (SE={se!r}, bound=5*SE)."
        )

    def test_stationary_variance(self) -> None:
        """Stationary-variance anchor: Var(X_T) ≈ sigma**2 / (2*theta) within 5%.

        After ``theta*T`` is large the cross-section variance converges to
        the OU stationary variance. A missing or wrong
        ``sqrt((1 - exp(-2*theta*dt)) / (2*theta))`` noise-scale factor in
        the exact-transition kernel would produce a variance off by
        O(dt) — easily blowing past the 5%-rel-err bound at the pinned
        ``(theta=10, T=10, n_paths=10000)`` configuration.
        """
        params = OUParameters(
            theta=10.0,
            mu_bar=5.0,
            sigma=0.5,
            x_0=100.0,
            T=10.0,
            dt=10.0 / 10000.0,
            n_steps=10000,
        )
        ens = OUPathGenerator(params=params)(rng_seed=2026, n_paths=10000)
        empirical_var = float(ens.paths[:, -1].var())
        theoretical_var = params.sigma**2 / (2.0 * params.theta)
        rel_err = abs(empirical_var - theoretical_var) / theoretical_var
        assert rel_err < 0.05, (
            f"Stationary-variance anchor failed: empirical={empirical_var!r} "
            f"vs theoretical={theoretical_var!r} (rel_err={rel_err!r}, bound=0.05)."
        )

    def test_trivial_degenerate_limit_theta_to_infinity(self) -> None:
        """At theta → ∞ paths collapse to mu_bar; sigma_t mean is < 1e-3.

        Inherits Plan §16.3 (v0.2→v0.3 CORRECTIONS-α) project-canonical
        anchoring: coarse grid (n_steps=100) + tight threshold (< 1e-3)
        rather than canonical-grid + relaxed threshold. The §16.3 forward-
        implication clause ratifies this verbatim for Task 3.2 to avoid
        re-litigating the disposition per family. ``x_0 == mu_bar`` so the
        paths start at the long-run mean and have no decay-driven excursion.
        """
        params = OUParameters(
            theta=1e8,
            mu_bar=4000.0,
            sigma=0.5,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 100.0,
            n_steps=100,
        )
        ens = OUPathGenerator(params=params)(rng_seed=0, n_paths=50)
        assert float(np.mean(ens.sigma_t)) < 1e-3

    def test_trivial_degenerate_limit_sigma_to_zero(self) -> None:
        """At sigma → 0 paths track mu_bar exactly; sigma_t mean is < 1e-6.

        Inherits Plan §16.3 (v0.2→v0.3 CORRECTIONS-α) project-canonical
        anchoring: coarse grid (n_steps=100) + tight threshold (< 1e-6)
        rather than canonical-grid + relaxed threshold (matches the
        ``TestGBMPathGenerator::test_trivial_degenerate_limit_sigma_to_zero``
        sibling). ``x_0 == mu_bar`` so the deterministic exact-transition
        kernel leaves the path identically at ``mu_bar`` modulo the
        sub-machine-epsilon noise term.
        """
        params = OUParameters(
            theta=1.0,
            mu_bar=4000.0,
            sigma=1e-8,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 100.0,
            n_steps=100,
        )
        ens = OUPathGenerator(params=params)(rng_seed=0, n_paths=50)
        assert float(np.mean(ens.sigma_t)) < 1e-6

    def test_initial_condition_bit_exact(self) -> None:
        """paths[:, 0] == params.x_0 for all rows (bit-exact)."""
        gen = OUPathGenerator(params=CANONICAL_OU)
        ens = gen(rng_seed=11, n_paths=64)
        assert bool(np.all(ens.paths[:, 0] == CANONICAL_OU.x_0))

    def test_canonical_params_json_stable(self) -> None:
        """canonical_params_json on the ensemble is a non-empty stable JSON."""
        gen = OUPathGenerator(params=CANONICAL_OU)
        ens = gen(rng_seed=3, n_paths=10)
        import json as _json  # noqa: PLC0415  # local import for test isolation.

        parsed = _json.loads(ens.canonical_params_json)
        assert set(parsed.keys()) == {
            "theta",
            "mu_bar",
            "sigma",
            "x_0",
            "T",
            "dt",
            "n_steps",
        }
        assert parsed["x_0"] == CANONICAL_OU.x_0
        assert parsed["n_steps"] == CANONICAL_OU.n_steps

    @given(
        rng_seed=st.integers(min_value=0, max_value=2**31),
        n_paths=st.integers(min_value=10, max_value=200),
    )
    @settings(max_examples=15, deadline=None)
    def test_property_determinism(self, rng_seed: int, n_paths: int) -> None:
        """Hypothesis Pin Z1.2: (seed, n_paths) uniquely determines audit_block."""
        gen = OUPathGenerator(params=CANONICAL_OU)
        ens_a = gen(rng_seed=rng_seed, n_paths=n_paths)
        ens_b = gen(rng_seed=rng_seed, n_paths=n_paths)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()


class TestJumpDiffusionPathGenerator:
    """Construction + lambda=0→GBM collapse + Itô anchor + jump-frequency + determinism coverage.

    Pinned anchors (Plan §8 Task 3.3 acceptance block):

    - Happy-path construction: returns a ``PathEnsemble`` whose shape and
      audit_block format match the type's invariants.
    - Determinism (Pin Z1.2): identical ``(rng_seed, n_paths)`` yields a
      bit-exact ``audit_block`` AND ``paths.tobytes()``.
    - λ → 0 collapses to pure GBM (headline math anchor): at
      ``lambda_jump = 0``, the JD generator's terminal-spot distribution
      is statistically indistinguishable from a matched GBM via
      ``scipy.stats.ks_2samp``. Because the JD path uses
      ``aggregated_log_jump = N·μ_J + sqrt(N)·σ_J·Z'`` with ``N`` all-zero
      when ``λ = 0``, the additive contribution is identically zero AND
      consumes no entropy from the second standard_normal stream — the
      two terminal arrays end up bit-identical (KS p ≈ 1.0). This is a
      strict superset of the "statistically indistinguishable" claim in
      the plan, so the test asserts the looser ``p > 0.01`` bound.
    - Itô-correction anchor (jumps off): mirrors
      ``TestGBMPathGenerator::test_ito_correction_anchor`` with the JD
      generator at ``lambda_jump = 0``.
    - Jump-frequency anchor: total Poisson count across the ensemble
      matches ``λ·T·n_paths`` within 3·SE — pins the Poisson sampling.
    - Trivial-degenerate limit at ``sigma = 1e-8 AND lambda_jump = 0``:
      paths collapse near ``x_0`` and ``mean(sigma_t) < 1e-6``. Inherits
      Plan §16.3 (v0.2→v0.3 CORRECTIONS-α) project-canonical anchoring
      "coarse grid + tight threshold" verbatim from
      ``TestGBMPathGenerator``, per the §16.3 forward-implication clause:
      OUPathGenerator and JumpDiffusionPathGenerator SHOULD adopt option
      (a) verbatim for parallelism.
    - Initial-condition anchor: ``paths[:, 0] == x_0`` for all rows
      bit-exactly.

    Moment cross-check against ``merton_sigma_t_moments`` is NOT included
    here. The analytic ``E[σ_T]`` in :mod:`simulations.stochastic_fx.moments`
    follows the spec §4.2 leading-order continuous-time integrated-
    variance form, while the generator's ``sigma_t`` is the spec §6 eq. (7)
    DISCRETE sum-of-squared-deviations from the path mean normalised by
    ``T``. The two are structurally different statistics with a non-
    trivial scaling factor (≈137× at canonical GBM; ≈79× at canonical
    Merton) — see ``TestGBMPathGenerator`` which similarly omits a moment
    cross-check at the generator-unit-test scope. Moment matching is the
    Phase-B verifier's responsibility (Task 4.2 ``InversionVerifier``).
    """

    def test_happy_path_construction(self) -> None:
        """Canonical-pin Merton generator returns a well-formed PathEnsemble."""
        gen = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)
        ens = gen(rng_seed=42, n_paths=100)
        assert isinstance(ens, PathEnsemble)
        assert ens.family_id == "merton"
        assert ens.paths.shape == (100, CANONICAL_MERTON.n_steps + 1)
        assert ens.sigma_t.shape == (100,)
        assert _AUDIT_BLOCK_REGEX_PY.fullmatch(ens.audit_block) is not None
        assert ens.rng_seed == 42

    def test_determinism_same_call(self) -> None:
        """Pin Z1.2: identical (seed, n_paths) yields bit-exact audit_block + paths."""
        gen = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)
        ens_a = gen(rng_seed=42, n_paths=50)
        ens_b = gen(rng_seed=42, n_paths=50)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()
        assert ens_a.sigma_t.tobytes() == ens_b.sigma_t.tobytes()

    def test_determinism_across_instances(self) -> None:
        """Two separately-constructed generators with the same params agree bit-exactly."""
        gen_a = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)
        gen_b = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)
        ens_a = gen_a(rng_seed=7, n_paths=25)
        ens_b = gen_b(rng_seed=7, n_paths=25)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()

    def test_initial_condition_bit_exact(self) -> None:
        """paths[:, 0] == params.x_0 for all rows (bit-exact)."""
        gen = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)
        ens = gen(rng_seed=11, n_paths=64)
        assert bool(np.all(ens.paths[:, 0] == CANONICAL_MERTON.x_0))

    def test_lambda_zero_collapses_to_gbm(self) -> None:
        """λ=0 ⟹ JD terminal-spot distribution statistically matches GBM.

        Plan §8 Task 3.3 headline math anchor: at ``lambda_jump = 0``,
        the JD generator must coincide distributionally with the
        GBM generator at matched ``(mu, sigma, T, n_steps, x_0)``. The
        aggregated-log-jump expression ``N·μ_J + sqrt(N)·σ_J·Z'`` reduces
        to exactly zero when every Poisson count is zero, so the JD log-
        step equals the GBM log-step entry-for-entry. The extra
        ``rng.poisson(...)`` and ``rng.standard_normal(...)`` draws DO
        consume RNG entropy and advance the bit-generator state, but they
        do NOT enter the per-step path arithmetic in the λ=0 limit.

        Critically, the JD generator samples the diffusion ``Z`` stream
        FIRST in its RNG order — mirroring the GBM generator's single
        ``rng.standard_normal`` call — so at the same ``rng_seed`` both
        generators consume the SAME ``Z`` matrix. The terminal arrays end
        up bit-identical (KS stat = 0, p = 1.0); the looser ``p > 0.01``
        bound is asserted to cover any future legitimate RNG-stream
        reorders downstream that would still preserve distributional
        equivalence.
        """
        from scipy import stats  # noqa: PLC0415  # local import for test isolation.

        jd_params = dataclasses.replace(CANONICAL_MERTON, lambda_jump=0.0)
        gbm_params = GBMParameters(
            mu=jd_params.mu,
            sigma=jd_params.sigma,
            T=jd_params.T,
            n_steps=jd_params.n_steps,
            x_0=jd_params.x_0,
            dt=jd_params.dt,
        )
        jd_term = JumpDiffusionPathGenerator(jd_params)(
            rng_seed=42, n_paths=5000
        ).paths[:, -1]
        gbm_term = GBMPathGenerator(gbm_params)(
            rng_seed=42, n_paths=5000
        ).paths[:, -1]
        _, ks_p = stats.ks_2samp(jd_term, gbm_term)
        assert ks_p > 0.01, (
            f"λ=0 collapse-to-GBM failed: KS p-value={ks_p!r} (bound > 0.01); "
            "the JD generator's diffusion stream must coincide with the GBM "
            "generator at matched parameters."
        )

    def test_ito_correction_anchor_jumps_off(self) -> None:
        """At λ=0, mean(log(S_T / x_0)) ≈ -sigma**2/2 * T within 3·SE.

        Sanity sister of ``TestGBMPathGenerator::test_ito_correction_anchor``
        invoked through the JD generator with ``lambda_jump = 0``: the
        diffusion side must carry the same Itô ``-sigma**2/2`` correction.
        A missing or mis-signed correction here would manifest at exactly
        the GBM-anchor signature (a 50-SE shift at this configuration).
        """
        params = JumpDiffusionParameters(
            mu=0.0,
            sigma=0.5,
            lambda_jump=0.0,
            jump_mean=0.0,
            jump_std=1e-8,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 1000.0,
            n_steps=1000,
        )
        n_paths = 10000
        ens = JumpDiffusionPathGenerator(params=params)(
            rng_seed=2026, n_paths=n_paths
        )
        empirical_mean = float(np.log(ens.paths[:, -1] / params.x_0).mean())
        expected_mean = -0.125  # -sigma**2 / 2 * T
        se = params.sigma * math.sqrt(params.T) / math.sqrt(n_paths)
        assert abs(empirical_mean - expected_mean) < 3.0 * se, (
            f"Itô-correction anchor (jumps off) failed: empirical={empirical_mean!r} "
            f"vs expected={expected_mean!r} (SE={se!r}); a 0.125 offset is "
            "the missing -sigma**2/2 drift signature on the diffusion side."
        )

    def test_jump_frequency_anchor(self) -> None:
        """Total Poisson count ≈ λ·T·n_paths within 3·SE — pins the Poisson sample.

        Reconstructs the JD generator's RNG-call order (standard_normal →
        poisson → standard_normal) exactly so the Poisson count matrix
        observed here is bit-identical to the one the generator consumes
        internally. The expected total across the ensemble is
        ``λ·T·n_paths = 10·1·1000 = 10000``; the Poisson sum has
        ``SE = sqrt(10000) = 100``, so the 3·SE bound is 300. A wrong
        Poisson rate (e.g. ``lambda_jump`` instead of ``lambda_jump·dt``
        per step) would produce a count off by O(n_steps) — easily
        catching a mis-scaled intensity.
        """
        params = JumpDiffusionParameters(
            mu=0.0,
            sigma=CANONICAL_MERTON.sigma,
            lambda_jump=10.0,
            jump_mean=0.0,
            jump_std=0.10,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 1000.0,
            n_steps=1000,
        )
        n_paths = 1000
        # Reconstruct the generator's RNG-call order exactly: diffusion Z
        # first, then Poisson counts, then conditional-jump Z'.
        rng = np.random.default_rng(42)
        _ = rng.standard_normal((n_paths, params.n_steps))
        counts = rng.poisson(params.lambda_jump * params.dt, (n_paths, params.n_steps))
        total_jumps = int(counts.sum())
        expected = params.lambda_jump * params.T * n_paths
        se = math.sqrt(expected)
        assert abs(total_jumps - expected) < 3.0 * se, (
            f"Jump-frequency anchor failed: empirical={total_jumps!r} "
            f"vs expected={expected!r} (SE={se!r}, bound=3*SE={3.0 * se!r})."
        )

    def test_trivial_degenerate_limit_sigma_and_lambda_zero(self) -> None:
        """At sigma → 0 AND lambda → 0, paths collapse to x_0; sigma_t mean is < 1e-6.

        Inherits Plan §16.3 (v0.2→v0.3 CORRECTIONS-α) project-canonical
        anchoring: coarse grid (n_steps=100) + tight threshold (< 1e-6),
        per the §16.3 forward-implication clause that ratifies option
        (a) verbatim for Task 3.3 (matches the
        ``TestGBMPathGenerator::test_trivial_degenerate_limit_sigma_to_zero``
        and ``TestOUPathGenerator::test_trivial_degenerate_limit_sigma_to_zero``
        siblings). With both the diffusion (``sigma=1e-8``) and the jump
        intensity (``lambda_jump=0.0``) snapped to their trivial limits,
        every per-step log-increment is sub-machine-epsilon and the
        paths stay at ``x_0`` bit-exactly modulo the diffusion noise.
        """
        params = JumpDiffusionParameters(
            mu=0.0,
            sigma=1e-8,
            lambda_jump=0.0,
            jump_mean=0.0,
            jump_std=1e-8,
            x_0=4000.0,
            T=1.0,
            dt=1.0 / 100.0,
            n_steps=100,
        )
        ens = JumpDiffusionPathGenerator(params=params)(rng_seed=0, n_paths=50)
        assert float(np.mean(ens.sigma_t)) < 1e-6

    def test_canonical_params_json_stable(self) -> None:
        """canonical_params_json on the ensemble is a non-empty stable JSON."""
        gen = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)
        ens = gen(rng_seed=3, n_paths=10)
        import json as _json  # noqa: PLC0415  # local import for test isolation.

        parsed = _json.loads(ens.canonical_params_json)
        assert set(parsed.keys()) == {
            "mu",
            "sigma",
            "lambda_jump",
            "jump_mean",
            "jump_std",
            "x_0",
            "T",
            "dt",
            "n_steps",
        }
        assert parsed["x_0"] == CANONICAL_MERTON.x_0
        assert parsed["n_steps"] == CANONICAL_MERTON.n_steps

    @given(
        rng_seed=st.integers(min_value=0, max_value=2**31),
        n_paths=st.integers(min_value=10, max_value=100),
    )
    @settings(max_examples=10, deadline=None)
    def test_property_determinism(self, rng_seed: int, n_paths: int) -> None:
        """Hypothesis Pin Z1.2: (seed, n_paths) uniquely determines audit_block.

        Reduced ``n_paths`` cap (100 vs 200 for GBM/OU) and reduced
        ``max_examples`` (10 vs 15) because the JD generator is slowest
        per call — two ``standard_normal`` draws plus one ``poisson``
        draw per (i, t) cell — at canonical n_steps=5000.
        """
        gen = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)
        ens_a = gen(rng_seed=rng_seed, n_paths=n_paths)
        ens_b = gen(rng_seed=rng_seed, n_paths=n_paths)
        assert ens_a.audit_block == ens_b.audit_block
        assert ens_a.paths.tobytes() == ens_b.paths.tobytes()


# ─── Task 4.1: variance_proxy.py — Phase-A algebraic inversion ───────────────


class TestVarianceProxy:
    """Phase-A algebraic checks per plan v0.4 §9 Task 4.1.

    Three free functions under test:
    - ``recompute_sigma_t`` — eq.(7) round-trip vs generator-stored σ_T.
    - ``eq_8_inversion`` — closed-form ε = sqrt(8·σ_T / x̄²).
    - ``phase_a_algebraic_check`` — Pin Z1.3a identity check.
    """

    def test_recompute_sigma_t_matches_generator_per_family(self) -> None:
        """Per-family eq.(7) round-trip: independently-recomputed σ_T agrees with stored σ_T.

        Pin Z1.3a fundamental check — if the recompute differs from the
        generator's stored σ_T by more than NUMERICAL_IDENTITY_TOL on any
        path, the formula has drifted between ``generators.py`` and
        ``variance_proxy.recompute_sigma_t``.
        """
        cases = [
            ("gbm", GBMPathGenerator(params=CANONICAL_GBM)),
            ("ou", OUPathGenerator(params=CANONICAL_OU)),
            ("merton", JumpDiffusionPathGenerator(params=CANONICAL_MERTON)),
        ]
        for family, gen in cases:
            ens = gen(rng_seed=42, n_paths=100)
            sigma_t_recomputed = recompute_sigma_t(ens)
            assert sigma_t_recomputed.shape == ens.sigma_t.shape, (
                f"{family}: shape mismatch"
            )
            max_diff = float(np.max(np.abs(sigma_t_recomputed - ens.sigma_t)))
            assert max_diff < NUMERICAL_IDENTITY_TOL, (
                f"{family}: max diff {max_diff!r} exceeds tol {NUMERICAL_IDENTITY_TOL!r}"
            )

    def test_eq_8_inversion_canonical_fixture(self) -> None:
        """eq.(8) at (σ_T=20000, x̄=4000) returns EXACTLY 0.1.

        Hand-verified: sqrt(8·20000 / 4000²) = sqrt(160000 / 16_000_000)
                     = sqrt(0.01) = 0.1.
        """
        eps = eq_8_inversion(sigma_t=20000.0, x_bar=4000.0)
        assert eps == pytest.approx(0.1, abs=1e-15)

    def test_eq_8_inversion_trivial_degenerate_at_zero(self) -> None:
        """Pin Z1.3a trivial-degenerate limit: σ_T=0 → ε=0 exactly."""
        assert eq_8_inversion(sigma_t=0.0, x_bar=4000.0) == 0.0

    @given(
        sigma_t=st.floats(
            min_value=0.0,
            max_value=1e10,
            allow_nan=False,
            allow_infinity=False,
        ),
        x_bar=st.floats(
            min_value=1e-6,
            max_value=1e10,
            allow_nan=False,
            allow_infinity=False,
        ),
    )
    @settings(max_examples=200, deadline=None)
    def test_eq_8_inversion_property_finite_nonnegative(
        self, sigma_t: float, x_bar: float
    ) -> None:
        """Hypothesis: for valid (σ_T ≥ 0, x̄ > 0), ε is finite and ≥ 0."""
        eps = eq_8_inversion(sigma_t=sigma_t, x_bar=x_bar)
        assert math.isfinite(eps)
        assert eps >= 0.0

    def test_eq_8_inversion_rejects_negative_sigma(self) -> None:
        """eq.(8) rejects σ_T < 0."""
        with pytest.raises(SDEParameterError, match="sigma_t must be >= 0"):
            eq_8_inversion(sigma_t=-1.0, x_bar=4000.0)

    def test_eq_8_inversion_rejects_zero_x_bar(self) -> None:
        """eq.(8) rejects x̄ = 0."""
        with pytest.raises(SDEParameterError, match="x_bar must be > 0"):
            eq_8_inversion(sigma_t=20000.0, x_bar=0.0)

    def test_eq_8_inversion_rejects_negative_x_bar(self) -> None:
        """eq.(8) rejects x̄ < 0."""
        with pytest.raises(SDEParameterError, match="x_bar must be > 0"):
            eq_8_inversion(sigma_t=20000.0, x_bar=-1.0)

    def test_phase_a_algebraic_check_passes_per_family(self) -> None:
        """Pin Z1.3a PASS at canonical fixtures for GBM, OU, Merton.

        Closed-form identity ⇒ residual is essentially machine epsilon
        for any well-formed ensemble, regardless of family.
        """
        cases = [
            ("gbm", GBMPathGenerator(params=CANONICAL_GBM), CANONICAL_GBM.x_0),
            ("ou", OUPathGenerator(params=CANONICAL_OU), CANONICAL_OU.x_0),
            (
                "merton",
                JumpDiffusionPathGenerator(params=CANONICAL_MERTON),
                CANONICAL_MERTON.x_0,
            ),
        ]
        for family, gen, x_bar in cases:
            ens = gen(rng_seed=42, n_paths=100)
            pass_flag, residual = phase_a_algebraic_check(ens, x_bar=x_bar)
            assert pass_flag is True, f"{family}: Phase A failed; residual={residual!r}"
            assert residual < NUMERICAL_IDENTITY_TOL, (
                f"{family}: residual {residual!r} exceeds tol "
                f"{NUMERICAL_IDENTITY_TOL!r}"
            )

    def test_phase_a_algebraic_check_rejects_zero_x_bar(self) -> None:
        """Phase A rejects x̄ = 0."""
        gen = GBMPathGenerator(params=CANONICAL_GBM)
        ens = gen(rng_seed=42, n_paths=10)
        with pytest.raises(SDEParameterError, match="x_bar must be > 0"):
            phase_a_algebraic_check(ens, x_bar=0.0)

    def test_phase_a_algebraic_check_rejects_negative_x_bar(self) -> None:
        """Phase A rejects x̄ < 0."""
        gen = GBMPathGenerator(params=CANONICAL_GBM)
        ens = gen(rng_seed=42, n_paths=10)
        with pytest.raises(SDEParameterError, match="x_bar must be > 0"):
            phase_a_algebraic_check(ens, x_bar=-1.0)

    def test_variance_proxy_tier_purity(self) -> None:
        """``variance_proxy`` does NOT pull in sibling Callables at import time.

        Tier-purity contract per plan v0.4 §9 Task 4.1: ``variance_proxy.py``
        is Callable tier and must NOT import sibling Callables
        ``moments`` or ``generators``. We verify by re-importing the
        module into a fresh ``sys.modules`` slot and asserting the
        forbidden modules don't appear among its transitive imports
        triggered by ``variance_proxy`` alone.

        We can't fully isolate transitive imports (other tests already
        loaded those modules into ``sys.modules``), so the check is
        STRUCTURAL: parse the source's AST and confirm no TOP-LEVEL import
        statements pull in ``simulations.stochastic_fx.moments`` /
        ``.generators``. LAZY imports nested inside function bodies are
        permitted (v0.6 amendment for the Merton high-N empirical-CDF
        reference helper ``_merton_reference_sigma_t``, which lazily imports
        ``JumpDiffusionPathGenerator`` per plan §16.7 disposition); they
        do not break module-load tier-purity.
        """
        import ast
        import pathlib

        src_path = (
            pathlib.Path(__file__).resolve().parent.parent
            / "stochastic_fx"
            / "variance_proxy.py"
        )
        source = src_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        # Inspect ONLY top-level import nodes (direct children of the module
        # body); imports nested inside FunctionDef bodies are lazy and
        # permitted (preserves module-load tier-purity).
        top_level_imports: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None:
                    top_level_imports.append(node.module)
        joined = "\n".join(top_level_imports)
        assert "simulations.stochastic_fx.moments" not in joined, (
            f"variance_proxy top-level imports forbidden sibling 'moments': {joined!r}"
        )
        assert "simulations.stochastic_fx.generators" not in joined, (
            "variance_proxy top-level imports forbidden sibling 'generators' "
            f"(LAZY imports inside function bodies are permitted): {joined!r}"
        )
        # And confirm the module itself loads without dragging the siblings
        # into sys.modules if they weren't already there (best-effort check).
        import importlib
        import sys

        sibling_already_loaded_moments = (
            "simulations.stochastic_fx.moments" in sys.modules
        )
        sibling_already_loaded_generators = (
            "simulations.stochastic_fx.generators" in sys.modules
        )
        # Force a reimport of variance_proxy
        if "simulations.stochastic_fx.variance_proxy" in sys.modules:
            del sys.modules["simulations.stochastic_fx.variance_proxy"]
        importlib.import_module("simulations.stochastic_fx.variance_proxy")
        if not sibling_already_loaded_moments:
            assert "simulations.stochastic_fx.moments" not in sys.modules, (
                "variance_proxy import pulled in moments"
            )
        # Note: ``generators`` may be in sys.modules already from earlier
        # tests in this suite or from this test's own preceding TestInversionVerifier
        # invocations (which exercise the lazy import). The MODULE-LOAD
        # tier-purity invariant is that variance_proxy's own import does
        # not pull generators in; once a downstream caller triggers the
        # lazy import path, generators will appear in sys.modules — that's
        # the intentional v0.6 runtime tier-cross documented in
        # ``_merton_reference_sigma_t``'s docstring.
        if not sibling_already_loaded_generators:
            assert "simulations.stochastic_fx.generators" not in sys.modules, (
                "variance_proxy MODULE-LOAD pulled in generators "
                "(lazy runtime import is permitted, but module-load tier "
                "purity must hold)"
            )


# ─── Task 4.2: InversionVerifier (v0.6 per-family Phase C dispatch) ───────────


class TestInversionVerifier:
    """Task 4.2: Phase A + Phase B mean-only + Phase C per-family-dispatch combiner.

    Spec v0.5 §11.7 + plan v0.6 §16.7 disposition: Phase C reference SHAPE
    dispatches on family_id (GBM lognormal MoM, OU gamma MoM, Merton empirical-
    CDF via high-N reference run at pinned ``N_REF = 100_000`` /
    ``N_REF_SEED = 20260513``). Pass threshold ``KS_PVALUE_FLOOR = 0.01`` is
    single-valued across families.

    Memory-test-mode: Merton-phase-C tests monkeypatch ``N_REF`` down to a
    locally tractable value (5_000) so the test suite runs on developer
    hardware. The PRODUCTION constant is unchanged at 100_000 per spec §11.7;
    CI infrastructure must allocate sufficient memory headroom (≥ 8 GB) to
    exercise the canonical reference run end-to-end (FLAG-RC-V0.5-1
    acknowledgement).
    """

    # Test-mode N_REF — small enough to run locally, large enough that the
    # 2-sample KS test resolves with usable power vs the N=1000 test sample.
    _TEST_N_REF = 5_000

    @pytest.fixture(autouse=True)
    def _patched_n_ref(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Patch ``N_REF`` to ``_TEST_N_REF`` and reset the reference cache.

        Per FLAG-RC-V0.5-1: the spec-pinned ``N_REF = 100_000`` is
        infeasible on developer hardware (~12 GB peak RSS at canonical
        ``n_steps = 5000``). Test mode patches the module-level constant
        down to 5_000 (~50 MB peak) and clears ``functools.cache`` so
        each test draws a fresh reference with the patched value.
        """
        monkeypatch.setattr(_variance_proxy, "N_REF", self._TEST_N_REF)
        _variance_proxy._merton_reference_sigma_t.cache_clear()
        yield
        _variance_proxy._merton_reference_sigma_t.cache_clear()

    # ── Headline: per-family canonical PASS at N=1000 ────────────────────────

    def test_gbm_canonical_pass_at_n_1000(self) -> None:
        """v0.6 headline: GBM at canonical pin, seed=42, N=1000 produces composite_pass=True."""
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=1000)
        verifier = InversionVerifier()
        verdict = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        assert verdict.family_id == "gbm"
        assert verdict.phase_a_pass is True
        assert verdict.phase_b_pass is True
        assert verdict.phase_c_pass is True
        assert verdict.composite_pass is True
        # Expected per spec §11.7: mean_rel ≈ 0.011, KS p ≈ 0.12
        assert verdict.phase_b_mean_rel_err < MOMENT_REL_TOL
        assert verdict.phase_c_ks_pvalue >= KS_PVALUE_FLOOR

    def test_ou_canonical_pass_at_n_1000(self) -> None:
        """v0.6 headline: OU at canonical pin, seed=42, N=1000 produces composite_pass=True."""
        ens = OUPathGenerator(params=CANONICAL_OU)(rng_seed=42, n_paths=1000)
        verifier = InversionVerifier()
        verdict = verifier(CANONICAL_OU, ens, x_bar=CANONICAL_OU.x_0)
        assert verdict.family_id == "ou"
        assert verdict.phase_a_pass is True
        assert verdict.phase_b_pass is True
        assert verdict.phase_c_pass is True
        assert verdict.composite_pass is True
        # Expected per spec §11.7: mean_rel ≈ 0.002, KS p ≈ 0.30
        assert verdict.phase_b_mean_rel_err < MOMENT_REL_TOL
        assert verdict.phase_c_ks_pvalue >= KS_PVALUE_FLOOR

    def test_merton_canonical_pass_at_n_1000(self) -> None:
        """v0.6 headline: Merton at canonical pin, seed=42, N=1000 produces composite_pass=True.

        Phase C uses empirical-CDF reference via high-N reference run
        (test-mode N_REF=5_000) per spec v0.5 §11.7 amendment. The v0.5
        lognormal-Merton reference was retired (KS p=3.41e-21 catastrophic
        rejection); empirical-CDF correctly handles the Poisson-mixture-of-
        lognormals geometry without relaxing the floor.
        """
        ens = JumpDiffusionPathGenerator(params=CANONICAL_MERTON)(
            rng_seed=42, n_paths=1000
        )
        verifier = InversionVerifier()
        verdict = verifier(CANONICAL_MERTON, ens, x_bar=CANONICAL_MERTON.x_0)
        assert verdict.family_id == "merton"
        assert verdict.phase_a_pass is True
        assert verdict.phase_b_pass is True
        assert verdict.phase_c_pass is True
        assert verdict.composite_pass is True
        # Expected per spec §11.7: mean_rel ≈ 0.007, KS p ≈ 0.20 (empirical-CDF)
        assert verdict.phase_b_mean_rel_err < MOMENT_REL_TOL
        assert verdict.phase_c_ks_pvalue >= KS_PVALUE_FLOOR

    # ── N-floor enforcement (Pin Z1.5 EXACT equality) ────────────────────────

    def test_n_floor_strict_equality_999_raises(self) -> None:
        """Pin Z1.5: 999 paths raises MCBudgetExceededError (below floor)."""
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=999)
        verifier = InversionVerifier()
        with pytest.raises(MCBudgetExceededError):
            verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)

    def test_n_floor_strict_equality_1001_raises(self) -> None:
        """Pin Z1.5: 1001 paths raises MCBudgetExceededError (EXACT-equality, not >=).

        Anti-fishing surface — "increase N until passing" is structurally
        impossible because N is checked for strict equality against the
        floor, not >=.
        """
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=1001)
        verifier = InversionVerifier()
        with pytest.raises(MCBudgetExceededError):
            verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)

    def test_n_floor_at_exactly_1000_passes_check(self) -> None:
        """Pin Z1.5: 1000 paths is the only admitted value."""
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=1000)
        verifier = InversionVerifier()
        # Should NOT raise MCBudgetExceededError (may or may not pass other gates).
        verdict = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        assert verdict.phase_c_n_paths == N_PATHS_FLOOR

    # ── Phase B v0.5 mean-only behaviour (var_rel_err audit-trail only) ──────

    def test_phase_b_var_rel_err_audit_trail_does_not_gate(self) -> None:
        """v0.5 mean-only gate: var_rel_err > MOMENT_REL_TOL does NOT raise/fail.

        GBM at canonical pin has analytic var_rel_err ≈ 21% (Isserlis Gaussian-
        quadratic-form leading order under-estimates true Var for lognormal X),
        which is > MOMENT_REL_TOL=0.05. Phase B must still PASS (mean is the
        only gate) and the verdict must carry the var rel-err for audit-trail
        inspection.
        """
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=1000)
        verifier = InversionVerifier()
        verdict = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        # Mean rel-err passes gate
        assert verdict.phase_b_mean_rel_err <= MOMENT_REL_TOL
        assert verdict.phase_b_pass is True
        # Var rel-err is populated as audit-trail observation
        assert verdict.phase_b_var_rel_err > 0.0
        # And at canonical GBM it exceeds MOMENT_REL_TOL — but does NOT gate.
        assert verdict.phase_b_var_rel_err > MOMENT_REL_TOL

    def test_phase_b_fail_raises_moment_match_failed(self) -> None:
        """Phase B mean-rel-err > MOMENT_REL_TOL ⇒ MomentMatchFailedError.

        Construct the failure by feeding an OU ensemble to the verifier but
        relabeling its family_id to 'gbm' so the dispatched analytic E is the
        wrong family's. The mean rel-err blows up.
        """
        ou_ens = OUPathGenerator(params=CANONICAL_OU)(rng_seed=42, n_paths=1000)
        # Re-wrap the OU ensemble with family_id='gbm' to force a mismatched
        # analytic-moment dispatch in Phase B.
        mismatched_ens = PathEnsemble(
            family_id="gbm",
            paths=ou_ens.paths,
            sigma_t=ou_ens.sigma_t,
            canonical_params_json=ou_ens.canonical_params_json,
            rng_seed=ou_ens.rng_seed,
            audit_block=ou_ens.audit_block,
        )
        verifier = InversionVerifier()
        # We pass GBMParameters so gbm_discrete_sigma_t_moments dispatches;
        # but the empirical sigma_t came from OU dynamics — huge mean rel-err.
        with pytest.raises(MomentMatchFailedError):
            verifier(CANONICAL_GBM, mismatched_ens, x_bar=CANONICAL_GBM.x_0)

    # ── Phase C fail (GBM with deeply mismatched lognormal MoM reference) ────

    def test_phase_c_fail_raises_inversion_test_failed(self) -> None:
        """Phase C KS p-value < KS_PVALUE_FLOOR ⇒ InversionTestFailedError.

        Construct: a GBM ensemble at canonical params is fed to the verifier,
        but the params handed in have a DIFFERENT sigma — so analytic moments
        build a lognormal reference at the wrong location/scale, and the KS
        test against the unmatched reference rejects.

        Phase B intervenes first (mean rel-err blows up with wrong sigma),
        so we engineer parameters that match the mean closely but mis-locate
        Var heavily. Easier: use a deeply mismatched parameter set such that
        the Phase A check still passes (ε² = 8·σ_T / x̄² is closed-form, can't
        fail on a healthy ensemble) but Phase B fails first.

        Realistically — given the implementation guards Phase B BEFORE Phase
        C and a parameter mismatch large enough to fail Phase C necessarily
        fails Phase B first — this test is best handled by directly invoking
        the internal _phase_c_ks_test helper with a constructed failure case.
        """
        # Direct invocation of the per-family dispatch helper with a
        # mismatched reference: feed a sigma_t array from a degenerate
        # distribution and ask for a lognormal MoM fit at canonical analytic
        # moments. KS p-value collapses.
        canonical_params_json = '{"mu": 0.0, "sigma": 0.029, "x_0": 4000.0, "T": 12.0, "dt": 0.0024, "n_steps": 5000}'
        # Construct a sigma_t array with a CDF that's mostly point-mass at 0
        # — nothing like the lognormal we'll reference against canonical
        # GBM moments.
        sigma_t_array = np.full(1000, 1e-9, dtype=np.float64)
        e_an, var_an = gbm_discrete_sigma_t_moments(CANONICAL_GBM)
        pass_flag, p_value = _variance_proxy._phase_c_ks_test(
            sigma_t_array, "gbm", e_an, var_an, canonical_params_json
        )
        assert pass_flag is False
        assert p_value < KS_PVALUE_FLOOR

    # ── Determinism ──────────────────────────────────────────────────────────

    def test_audit_block_deterministic_across_calls(self) -> None:
        """Same (params, ensemble, x_bar) ⇒ identical audit_block across __call__s."""
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=1000)
        verifier = InversionVerifier()
        v1 = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        v2 = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        assert v1.audit_block == v2.audit_block

    # ── tex_anchor correctness per family ────────────────────────────────────

    def test_tex_anchor_per_family(self) -> None:
        """tex_anchor encodes the family_id."""
        verifier = InversionVerifier()
        for family, gen_cls, canonical in (
            ("gbm", GBMPathGenerator, CANONICAL_GBM),
            ("ou", OUPathGenerator, CANONICAL_OU),
            ("merton", JumpDiffusionPathGenerator, CANONICAL_MERTON),
        ):
            ens = gen_cls(params=canonical)(rng_seed=42, n_paths=1000)
            verdict = verifier(canonical, ens, x_bar=canonical.x_0)
            assert verdict.tex_anchor.endswith(f"sigma_t_moments_{family}.tex")

    # ── Discrete moments cross-check (hand-derivation pin) ───────────────────

    def test_gbm_discrete_moments_tractable_pin(self) -> None:
        """Hand-derived discrete moments at tractable pin agree with closed-form to 1e-6.

        Tractable pin: x_0=100, sigma=0.1, T=1, n_steps=10 — small enough to
        cross-check by hand. The analytic E[σ_T] for the discrete eq.(7)
        statistic at this pin is computed by direct expansion of the
        centering-projection identity ``Σ_j (X_j - X̄)² = X^T M X`` against
        the GBM auto-covariance kernel
        ``Cov(X_j, X_k) = x_0² (e^{σ²·dt·min(j,k)} − 1)``.

        Per FLAG-MQ-V0.6-2 / NIT-RC-V0.6-1 dispositions (Wave-1 Task 4.2
        2026-05-13): independently verified value is E_an ≈ 201.0031
        (RC re-computed via separate code path). The prior docstring
        numbers (81.3148, ~16.5) were authoring slips. To kill the
        tautology risk that a shared np.expm1 bug between impl and test
        would propagate undetected, this test re-derives the expected
        value via PURE-STDLIB math.exp arithmetic (NOT numpy.expm1),
        and additionally anchors against the hand-computed literal.
        """
        tractable = GBMParameters(
            mu=0.0,
            sigma=0.1,
            x_0=100.0,
            T=1.0,
            dt=0.1,
            n_steps=10,
        )
        e_an, var_an = gbm_discrete_sigma_t_moments(tractable)

        # Independent re-derivation via pure-stdlib math.exp (different
        # code path from impl's numpy.expm1 — kills shared-transcription
        # tautology risk per FLAG-MQ-V0.6-2).
        sigma2_dt = tractable.sigma ** 2 * tractable.dt  # 0.001
        N = tractable.n_steps + 1  # 11
        x0sq = tractable.x_0 ** 2  # 10000

        diag_sum = 0.0
        for j in range(N):
            diag_sum += x0sq * (math.exp(sigma2_dt * j) - 1.0)

        total_sum = 0.0
        for j in range(N):
            for k in range(N):
                total_sum += x0sq * (math.exp(sigma2_dt * min(j, k)) - 1.0)

        # μ^T M μ = 0 (constant μ); E_an = (tr Σ − sum Σ / N) / T.
        expected_e = (diag_sum - total_sum / N) / tractable.T

        # Hardcoded hand-computed literal anchor — caught the v0.6
        # docstring drift (RC independently computed 201.0031).
        hand_computed_e = 201.0031

        assert abs(e_an - expected_e) / abs(expected_e) < 1e-6, (
            f"impl ({e_an}) vs independent math.exp re-derivation ({expected_e}) "
            f"disagree beyond rel-err 1e-6 — shared transcription error possible"
        )
        assert abs(e_an - hand_computed_e) / hand_computed_e < 1e-3, (
            f"impl ({e_an}) vs hand-computed literal ({hand_computed_e}) "
            f"disagree beyond rel-err 1e-3 — regression anchor failure"
        )
        assert var_an > 0.0

    # ── var_rel_err audit-trail populated for all three families ─────────────

    def test_phase_b_var_rel_err_populated_for_all_families(self) -> None:
        """phase_b_var_rel_err > 0 for GBM/OU/Merton at canonical PASS.

        var_rel_err is computed and emitted as audit-trail observation even
        though it does NOT gate phase_b_pass (v0.5 Option-B disposition).
        """
        verifier = InversionVerifier()
        for gen_cls, canonical in (
            (GBMPathGenerator, CANONICAL_GBM),
            (OUPathGenerator, CANONICAL_OU),
            (JumpDiffusionPathGenerator, CANONICAL_MERTON),
        ):
            ens = gen_cls(params=canonical)(rng_seed=42, n_paths=1000)
            verdict = verifier(canonical, ens, x_bar=canonical.x_0)
            assert verdict.phase_b_var_rel_err > 0.0

    # ── phase_c_n_paths semantics (v0.6 FLAG-RC-V0.5-2) ──────────────────────

    def test_phase_c_n_paths_equals_test_sample_not_reference(self) -> None:
        """phase_c_n_paths records TEST sample N (1000), NOT N_REF (Merton).

        v0.6 FLAG-RC-V0.5-2 disposition: the field's Task 1.3 docstring is
        "path-count used for the test sample". For Merton runs the high-N
        reference's existence is recorded via the audit_block binding
        (N_REF + N_REF_SEED), not via this field.
        """
        verifier = InversionVerifier()
        for gen_cls, canonical in (
            (GBMPathGenerator, CANONICAL_GBM),
            (OUPathGenerator, CANONICAL_OU),
            (JumpDiffusionPathGenerator, CANONICAL_MERTON),
        ):
            ens = gen_cls(params=canonical)(rng_seed=42, n_paths=1000)
            verdict = verifier(canonical, ens, x_bar=canonical.x_0)
            assert verdict.phase_c_n_paths == 1000  # NOT N_REF (test-mode 5_000 here)
            assert verdict.phase_c_n_paths != self._TEST_N_REF

    # ── audit_block binds N_REF and N_REF_SEED ───────────────────────────────

    def test_audit_block_binds_n_ref_constant(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """audit_block differs when N_REF changes (v0.6 FLAG-RC-V0.5-5).

        Re-running the verifier with a different N_REF produces a different
        audit_block, confirming that N_REF is byte-fed into the SHA-256
        hash recipe. This binds the Merton high-N reference to the audit
        trail so any spec amendment to N_REF invalidates the digest.

        Tested with a GBM ensemble (which does not need the high-N
        reference for its KS test) — confirms that N_REF is hashed in
        REGARDLESS of which family dispatches (single recipe across
        families).
        """
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=1000)
        verifier = InversionVerifier()
        verdict_a = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        # Re-patch N_REF to a different value; cache clear; rerun.
        monkeypatch.setattr(_variance_proxy, "N_REF", 7777)
        _variance_proxy._merton_reference_sigma_t.cache_clear()
        verdict_b = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        assert verdict_a.audit_block != verdict_b.audit_block

    def test_audit_block_binds_n_ref_seed_constant(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """audit_block differs when N_REF_SEED changes (v0.6 FLAG-RC-V0.5-5)."""
        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=1000)
        verifier = InversionVerifier()
        verdict_a = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        monkeypatch.setattr(_variance_proxy, "N_REF_SEED", 99999)
        _variance_proxy._merton_reference_sigma_t.cache_clear()
        verdict_b = verifier(CANONICAL_GBM, ens, x_bar=CANONICAL_GBM.x_0)
        assert verdict_a.audit_block != verdict_b.audit_block

    # ── Merton reference cache returns bit-identical output ──────────────────

    def test_merton_reference_cache_bit_identical(self) -> None:
        """_merton_reference_sigma_t returns bit-identical np.array on repeat calls.

        Per FLAG-RC-V0.5-1 / FLAG-MEM-1: the cached object is the sigma_t
        ARRAY only (NOT the full PathEnsemble). Confirms ``functools.cache``
        keyed on ``(canonical_params_json, N_REF, N_REF_SEED)`` returns the
        same array object across calls (avoids re-sampling).
        """
        canonical_params_json = '{"mu": 0.0, "sigma": 0.014433756729740645, "lambda_jump": 1.0, "jump_mean": 0.0, "jump_std": 0.1, "x_0": 4000.0, "T": 12.0, "dt": 0.0024, "n_steps": 5000}'
        out1 = _variance_proxy._merton_reference_sigma_t(
            canonical_params_json, self._TEST_N_REF, N_REF_SEED
        )
        out2 = _variance_proxy._merton_reference_sigma_t(
            canonical_params_json, self._TEST_N_REF, N_REF_SEED
        )
        assert np.array_equal(out1, out2)
        # Bit-identity confirms functools.cache returned the same object.
        assert out1 is out2

    def test_merton_reference_returns_ndarray_not_path_ensemble(self) -> None:
        """Cached object is np.ndarray (~ 5_000 floats), NOT a PathEnsemble.

        FLAG-MEM-1 / FLAG-RC-V0.5-1 disposition anchor: caching the full
        PathEnsemble would retain ~4 GB at canonical settings; the spec-
        compliant pattern caches the sigma_t array only.
        """
        canonical_params_json = '{"mu": 0.0, "sigma": 0.014433756729740645, "lambda_jump": 1.0, "jump_mean": 0.0, "jump_std": 0.1, "x_0": 4000.0, "T": 12.0, "dt": 0.0024, "n_steps": 5000}'
        out = _variance_proxy._merton_reference_sigma_t(
            canonical_params_json, self._TEST_N_REF, N_REF_SEED
        )
        assert isinstance(out, np.ndarray)
        assert out.ndim == 1
        assert out.shape == (self._TEST_N_REF,)
        # Not a PathEnsemble:
        assert not isinstance(out, PathEnsemble)

    # ── Constants surface ────────────────────────────────────────────────────

    def test_n_ref_and_n_ref_seed_are_finals(self) -> None:
        """N_REF and N_REF_SEED are spec-pinned module-level constants."""
        # Test-mode patches the value down to _TEST_N_REF — but only via
        # monkeypatch (autouse fixture). The autouse-patched value at this
        # point is _TEST_N_REF; without the patch the production value is
        # 100_000. We test the import surface:
        assert _variance_proxy.N_REF == self._TEST_N_REF  # patched
        # N_REF_SEED is also patched (no) — actually autouse only sets N_REF.
        # The non-patched N_REF_SEED is the production pinned 20260513:
        assert _variance_proxy.N_REF_SEED == 20260513
        # Re-imported top-level constant — production value (NOT patched
        # because the test's import-time binding captured the un-patched
        # value):
        # NB: simulations.stochastic_fx.N_REF_SEED is the production value.
        assert N_REF_SEED == 20260513


# ============================================================================
# Task 5 — Emit IO Boundary tier (parquet + JSON + tex + MD)
# ============================================================================


class TestEmit:
    """Task 5: IO Boundary tier emitters with round-trip readback verification.

    Plan v0.6 §10 acceptance:

    - PathEnsembleEmitter: parquet + lineage metadata round-trips byte-for-byte
      on paths; sigma_t reconstructed via recompute_sigma_t matches to 1e-12.
    - InversionVerdictEmitter: JSON v1.0 schema + tolerance constants;
      field-by-field equality on read-back.
    - TexFragmentEmitter: existence-only (Task 2.1 committed the bytes).
    - StochasticFxResultsEmitter: human-readable markdown with cross-family
      summary + per-family R-tagged subsections.
    - simulations/stochastic_fx/data/ is gitignored (Task 0 verification).
    """

    # ── Constants for verdict construction (small N for speed) ───────────────
    _MOCK_AUDIT_BLOCK: str = "a" * 64
    _MOCK_AUDIT_BLOCK_2: str = "b" * 64
    _MOCK_AUDIT_BLOCK_3: str = "c" * 64

    # ── PathEnsembleEmitter round-trip ───────────────────────────────────────

    @pytest.mark.parametrize(
        ("params", "gen_cls", "family_id"),
        [
            (CANONICAL_GBM, GBMPathGenerator, "gbm"),
            (CANONICAL_OU, OUPathGenerator, "ou"),
            (CANONICAL_MERTON, JumpDiffusionPathGenerator, "merton"),
        ],
    )
    def test_path_ensemble_round_trip_at_canonical_pin(
        self, tmp_path, params, gen_cls, family_id
    ) -> None:
        """Generate at canonical pin → emit → read → assert sigma_t / audit_block / params match.

        sigma_t: np.allclose(rtol=1e-12) — the float64 path bytes are
        parquet-faithful and recompute_sigma_t reapplies eq. (7) deterministically.
        audit_block: verbatim hex equality (no float tolerance).
        canonical_params_json: verbatim string equality.
        """
        from simulations.stochastic_fx import PathEnsembleEmitter

        ens = gen_cls(params=params)(rng_seed=42, n_paths=100)
        emitter = PathEnsembleEmitter(emit_dir=tmp_path)

        out_path = emitter.emit(ens)
        assert out_path.is_file()
        assert out_path.name == f"path_ensemble_{family_id}.parquet"

        round_tripped = emitter.read(family_id)
        assert round_tripped.family_id == ens.family_id
        assert round_tripped.audit_block == ens.audit_block
        assert round_tripped.canonical_params_json == ens.canonical_params_json
        assert round_tripped.rng_seed == ens.rng_seed
        assert np.array_equal(round_tripped.paths, ens.paths)
        assert np.allclose(
            round_tripped.sigma_t, ens.sigma_t, rtol=1e-12, atol=0.0
        )

    @pytest.mark.parametrize(
        ("params", "gen_cls"),
        [
            (CANONICAL_GBM, GBMPathGenerator),
            (CANONICAL_OU, OUPathGenerator),
            (CANONICAL_MERTON, JumpDiffusionPathGenerator),
        ],
    )
    def test_path_ensemble_emit_and_verify_passes(
        self, tmp_path, params, gen_cls
    ) -> None:
        """emit_and_verify is the canonical write+read+equality convenience method.

        Returns the on-disk path. Should NOT raise at canonical pins +
        seed=42 + n_paths=100.
        """
        from simulations.stochastic_fx import PathEnsembleEmitter

        ens = gen_cls(params=params)(rng_seed=42, n_paths=100)
        emitter = PathEnsembleEmitter(emit_dir=tmp_path)
        out_path = emitter.emit_and_verify(ens)
        assert out_path.is_file()

    def test_path_ensemble_emit_and_verify_raises_on_audit_block_corruption(
        self, tmp_path, monkeypatch
    ) -> None:
        """Corrupt the parquet metadata's audit_block; emit_and_verify must HALT.

        Defence-in-depth check: the audit-block round-trip is the canonical
        anti-drift guard. We corrupt the on-disk metadata by patching the
        read method to return a tampered ensemble; the equality check
        downstream must raise RoundTripDriftError.
        """
        from simulations.stochastic_fx import (
            PathEnsembleEmitter,
            RoundTripDriftError,
        )

        ens = GBMPathGenerator(params=CANONICAL_GBM)(rng_seed=42, n_paths=100)
        emitter = PathEnsembleEmitter(emit_dir=tmp_path)

        # Build a tampered PathEnsemble (different audit_block hex) and
        # monkeypatch the read method to return it. This simulates on-disk
        # parquet metadata tampering between write and read.
        tampered = dataclasses.replace(ens, audit_block="0" * 64)

        def _tampered_read(_family_id: str) -> PathEnsemble:
            return tampered

        monkeypatch.setattr(emitter, "read", _tampered_read)
        with pytest.raises(RoundTripDriftError, match="audit_block drift"):
            emitter.emit_and_verify(ens)

    def test_path_ensemble_read_raises_on_missing_metadata(
        self, tmp_path
    ) -> None:
        """If parquet exists but lineage metadata is stripped, read() raises RoundTripDriftError."""
        import pyarrow as pa
        import pyarrow.parquet as pq

        from simulations.stochastic_fx import (
            PathEnsembleEmitter,
            RoundTripDriftError,
        )

        # Write a parquet WITHOUT lineage metadata at the canonical path.
        target = tmp_path / "path_ensemble_gbm.parquet"
        table = pa.Table.from_pydict(
            {
                "path_index": np.array([0, 0, 1, 1], dtype=np.int64),
                "step_index": np.array([0, 1, 0, 1], dtype=np.int64),
                "x_t": np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64),
            }
        )
        pq.write_table(table, target)

        emitter = PathEnsembleEmitter(emit_dir=tmp_path)
        with pytest.raises(RoundTripDriftError, match="missing metadata"):
            emitter.read("gbm")

    def test_path_ensemble_read_raises_on_missing_file(self, tmp_path) -> None:
        """If parquet doesn't exist, read() raises FileNotFoundError."""
        from simulations.stochastic_fx import PathEnsembleEmitter

        emitter = PathEnsembleEmitter(emit_dir=tmp_path)
        with pytest.raises(FileNotFoundError, match="missing parquet"):
            emitter.read("gbm")

    # ── InversionVerdictEmitter round-trip ───────────────────────────────────

    def _build_mock_verdict(
        self, family_id: str, audit_block: str = "a" * 64
    ) -> InversionVerdict:
        """Construct a passing InversionVerdict (no PathEnsemble required)."""
        return InversionVerdict(
            family_id=family_id,
            phase_a_pass=True,
            phase_a_max_residual=1.23e-10,
            phase_b_pass=True,
            phase_b_mean_rel_err=1.1e-2,
            phase_b_var_rel_err=0.45,  # > MOMENT_REL_TOL OK (audit-trail only)
            phase_c_pass=True,
            phase_c_ks_pvalue=0.234,
            phase_c_n_paths=1000,
            composite_pass=True,
            tex_anchor=f"notes/stochastic_fx_tex/sigma_t_moments_{family_id}.tex",
            audit_block=audit_block,
        )

    @pytest.mark.parametrize("family_id", ["gbm", "ou", "merton"])
    def test_inversion_verdict_round_trip(
        self, tmp_path, family_id
    ) -> None:
        """Build verdict → emit → read → field-by-field equality on all 12 fields."""
        from simulations.stochastic_fx import InversionVerdictEmitter

        v = self._build_mock_verdict(family_id)
        emitter = InversionVerdictEmitter(emit_dir=tmp_path)

        out_path = emitter.emit(v)
        assert out_path.is_file()
        assert out_path.name == f"inversion_verdict_{family_id}.json"

        round_tripped = emitter.read(family_id)
        assert round_tripped.family_id == v.family_id
        assert round_tripped.phase_a_pass == v.phase_a_pass
        assert round_tripped.phase_a_max_residual == v.phase_a_max_residual
        assert round_tripped.phase_b_pass == v.phase_b_pass
        assert round_tripped.phase_b_mean_rel_err == v.phase_b_mean_rel_err
        assert round_tripped.phase_b_var_rel_err == v.phase_b_var_rel_err
        assert round_tripped.phase_c_pass == v.phase_c_pass
        assert round_tripped.phase_c_ks_pvalue == v.phase_c_ks_pvalue
        assert round_tripped.phase_c_n_paths == v.phase_c_n_paths
        assert round_tripped.composite_pass == v.composite_pass
        assert round_tripped.tex_anchor == v.tex_anchor
        assert round_tripped.audit_block == v.audit_block

    def test_inversion_verdict_emit_and_verify_passes(
        self, tmp_path
    ) -> None:
        """emit_and_verify writes + reads + asserts equality without raising."""
        from simulations.stochastic_fx import InversionVerdictEmitter

        v = self._build_mock_verdict("gbm")
        emitter = InversionVerdictEmitter(emit_dir=tmp_path)
        out_path = emitter.emit_and_verify(v)
        assert out_path.is_file()

    def test_inversion_verdict_emit_and_verify_raises_on_corruption(
        self, tmp_path, monkeypatch
    ) -> None:
        """Corrupt the on-disk JSON's audit_block; emit_and_verify must HALT."""
        from simulations.stochastic_fx import (
            InversionVerdictEmitter,
            RoundTripDriftError,
        )

        v = self._build_mock_verdict("gbm")
        emitter = InversionVerdictEmitter(emit_dir=tmp_path)

        # Patch read() to return a tampered verdict with a different audit_block.
        tampered = dataclasses.replace(v, audit_block="b" * 64)

        def _tampered_read(_family_id: str) -> InversionVerdict:
            return tampered

        monkeypatch.setattr(emitter, "read", _tampered_read)
        with pytest.raises(RoundTripDriftError, match="audit_block drift"):
            emitter.emit_and_verify(v)

    def test_inversion_verdict_schema_includes_tolerance_constants(
        self, tmp_path
    ) -> None:
        """JSON sidecar carries the three tolerance constants per FLAG-RC-3.

        Single source of truth: phase_a_tolerance = NUMERICAL_IDENTITY_TOL,
        phase_b_tolerance = MOMENT_REL_TOL, phase_c_tolerance = KS_PVALUE_FLOOR,
        schema_version = "v1.0".
        """
        import json

        from simulations.stochastic_fx import InversionVerdictEmitter

        v = self._build_mock_verdict("gbm")
        emitter = InversionVerdictEmitter(emit_dir=tmp_path)
        out_path = emitter.emit(v)
        on_disk = json.loads(out_path.read_text(encoding="utf-8"))

        assert on_disk["phase_a_tolerance"] == NUMERICAL_IDENTITY_TOL
        assert on_disk["phase_b_tolerance"] == MOMENT_REL_TOL
        assert on_disk["phase_c_tolerance"] == KS_PVALUE_FLOOR
        assert on_disk["schema_version"] == "v1.0"
        # emitted_at_utc must be present and a non-empty ISO-format string.
        assert isinstance(on_disk["emitted_at_utc"], str)
        assert len(on_disk["emitted_at_utc"]) > 0

    def test_inversion_verdict_read_rejects_wrong_schema_version(
        self, tmp_path
    ) -> None:
        """schema_version != "v1.0" raises RoundTripDriftError (no backwards-compat shim)."""
        import json

        from simulations.stochastic_fx import (
            InversionVerdictEmitter,
            RoundTripDriftError,
        )

        # Write a JSON with a fictitious schema_version.
        target = tmp_path / "inversion_verdict_gbm.json"
        target.write_text(
            json.dumps({"schema_version": "v0.9"}, indent=2), encoding="utf-8"
        )
        emitter = InversionVerdictEmitter(emit_dir=tmp_path)
        with pytest.raises(RoundTripDriftError, match="schema_version mismatch"):
            emitter.read("gbm")

    # ── TexFragmentEmitter ───────────────────────────────────────────────────

    @pytest.mark.parametrize("family_id", ["gbm", "ou", "merton"])
    def test_tex_fragment_emitter_finds_committed_artifact(
        self, family_id
    ) -> None:
        """Task 2.1 committed the .tex fragments; emit returns the on-disk path."""
        from simulations.stochastic_fx import TexFragmentEmitter

        # Default emit_dir == notes/stochastic_fx_tex/ — Task 2.1's committed
        # output location.
        emitter = TexFragmentEmitter()
        out_path = emitter.emit(family_id)
        assert out_path.is_file()
        assert out_path.name == f"sigma_t_moments_{family_id}.tex"

    def test_tex_fragment_emitter_raises_when_absent(self, tmp_path) -> None:
        """Pointed at an empty directory, emit raises FileNotFoundError."""
        from simulations.stochastic_fx import TexFragmentEmitter

        emitter = TexFragmentEmitter(emit_dir=tmp_path)
        with pytest.raises(FileNotFoundError, match="missing tex fragment"):
            emitter.emit("gbm")

    # ── StochasticFxResultsEmitter ───────────────────────────────────────────

    def test_results_markdown_contains_summary_and_per_family_sections(
        self, tmp_path
    ) -> None:
        """Emit with 3 mock verdicts; confirm structural anchors in the markdown."""
        from simulations.stochastic_fx import StochasticFxResultsEmitter

        verdicts = (
            self._build_mock_verdict("gbm", self._MOCK_AUDIT_BLOCK),
            self._build_mock_verdict("ou", self._MOCK_AUDIT_BLOCK_2),
            self._build_mock_verdict("merton", self._MOCK_AUDIT_BLOCK_3),
        )
        emitter = StochasticFxResultsEmitter(emit_dir=tmp_path)
        out_path = emitter.emit(verdicts)
        assert out_path.is_file()
        assert out_path.name == "STOCHASTIC_FX_RESULTS.md"
        text = out_path.read_text(encoding="utf-8")

        # Cross-family summary table — 3 R-tag rows.
        assert "## §1 Cross-family summary" in text
        for r_tag in ("R1", "R2", "R3"):
            assert r_tag in text
        # Per-family R-tagged subsections.
        assert "## §2 Per-family verdicts" in text
        for family in ("Geometric Brownian motion", "Ornstein-Uhlenbeck", "Merton jump-diffusion"):
            assert family in text
        # Audit-block hex strings rendered (full + prefix in summary).
        for ab in (
            self._MOCK_AUDIT_BLOCK,
            self._MOCK_AUDIT_BLOCK_2,
            self._MOCK_AUDIT_BLOCK_3,
        ):
            assert ab in text  # full audit_block rendered in per-family section
            assert ab[:16] in text  # prefix rendered in cross-family summary
        # Citations to spec v0.5 §11.6 + §11.7.
        assert "§11.6" in text
        assert "§11.7" in text

    # ── Data-dir gitignore verification ──────────────────────────────────────

    def test_stochastic_fx_data_dir_is_gitignored(self) -> None:
        """simulations/stochastic_fx/data/ files must NOT be git-tracked.

        Plan v0.6 §10 Task 5 acceptance bullet — Task 0 verification: ANY
        artefact emitted under simulations/stochastic_fx/data/ is ignored
        by git. Uses ``git check-ignore`` (exit 0 ⇒ path is ignored).
        """
        import subprocess

        result = subprocess.run(
            [
                "git",
                "check-ignore",
                "simulations/stochastic_fx/data/path_ensemble_gbm.parquet",
            ],
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, (
            f"simulations/stochastic_fx/data/ must be gitignored; "
            f"git check-ignore returned {result.returncode}: "
            f"stdout={result.stdout!r}, stderr={result.stderr!r}"
        )

    # ── Tier purity (module-load) ────────────────────────────────────────────

    def test_emit_module_load_does_not_pull_generators(self) -> None:
        """Importing emit must not load sibling Callable `generators`.

        IO Boundary tier purity per functional-python: emit consumes
        already-built Value containers; it must not depend at module load
        on the generator family that PRODUCES them. (Run-time test-helpers
        that import generators are fine; the import surface is what's
        tested here.)
        """
        import importlib
        import sys
        from pathlib import Path as _Path

        # Force a reload of emit to re-evaluate its module-load imports
        # without picking up cached state from prior test imports.
        # We can't actually evict generators because the test file at the
        # top already imported it; instead we assert emit.py's top-level
        # imports do NOT name `generators`.
        emit_module = importlib.import_module("simulations.stochastic_fx.emit")
        emit_source = _Path(emit_module.__file__).read_text(encoding="utf-8")
        # Top-level (module-load-time) imports MUST NOT name the sibling
        # Callables `generators` or `moments`. We do a coarse text grep
        # for `from simulations.stochastic_fx.generators` /
        # `from simulations.stochastic_fx.moments` at module scope.
        for forbidden in (
            "from simulations.stochastic_fx.generators",
            "from simulations.stochastic_fx.moments",
            "import simulations.stochastic_fx.generators",
            "import simulations.stochastic_fx.moments",
        ):
            assert forbidden not in emit_source, (
                f"emit.py must not import {forbidden!r} at module load — "
                "tier purity (functional-python IO Boundary tier)."
            )
        # Sanity: simulations.stochastic_fx.emit IS importable.
        assert hasattr(emit_module, "PathEnsembleEmitter")
        # sys.modules sanity — emit and types are loaded; this is the
        # admitted dependency surface.
        assert "simulations.stochastic_fx.emit" in sys.modules
        assert "simulations.stochastic_fx.types" in sys.modules
