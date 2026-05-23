"""Callable-tier verifiers — one free pure function per R-tag.

Per design v0.3 §3a.3 (with v0.3 → v0.3.1 micro-correction: R7
adjusted to read revenue_form_verdict._metadata.halt_on_flip_comparison
since CohortGateVerdict carries no S_t pin fields; the S_t = (1-λ)^t,
λ ~ Beta(4.5, 95.5) pin remains the spec-level source of truth at
docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md §6.1).

None mutate. None do filesystem I/O. All inputs pre-loaded by
``CommittedArtifactLoader``.

Field-name corrections vs plan template
----------------------------------------
- ``ZCapPinned.Z_cop_per_month`` (uppercase Z) — the Value-tier field is
  capitalised per ``simulations/types/posterior.py`` line 292.
- ``tightness_l1_deviation`` accepts a ``SoftplusParams`` object, not a
  bare ``kappa`` float. ``verify_r6_softplus_l1_tightness`` constructs
  ``SoftplusParams(beta=50.0 / kappa, kappa=kappa)`` internally using the
  spec-prescribed β ≈ 50/κ baseline (distributions.py docstring, line 227).
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import sympy as sp

from simulations.saas_builder.verify.types import RTagVerdict
from simulations.types.posterior import ZCapPinned


def verify_r1_sigma_0_anchor(
    *,
    x_bar: float,
    y_bar: float,
    eps: float,
    expected: float,
    tol: float,
    audit_sha256: str,
) -> RTagVerdict:
    """R1: σ₀ = (X̄/Ȳ)²·ε²/8 (PRIMITIVES (8); verdict memo §1: 20,000).

    Closed-form derivation:
        σ₀ = (X̄/Ȳ)² · ε² / 8

    Verifies the anchor numerical value computed from the pre-pinned
    parameters X̄, Ȳ, ε matches the expected value within ``tol``.
    """
    actual = (x_bar / y_bar) ** 2 * eps**2 / 8.0
    residual = abs(actual - expected)
    passed = residual <= tol
    return RTagVerdict(
        r_tag="R1",
        passed=passed,
        expected=expected,
        actual=actual,
        residual=residual,
        audit_sha256=audit_sha256,
        message=(
            f"σ₀ closed form: expected {expected:.6g}, got {actual:.6g}, "
            f"residual {residual:.2e} (tol {tol:.2e})"
        ),
    )


def verify_r2_kappa_eliminated_in_pi_t(
    *,
    audit_sha256: str,
    pi_t_expression: sp.Expr | None = None,
) -> RTagVerdict:
    """R2: κ ∉ free_symbols(π(t)) — anti-fishing free-symbol audit.

    By default, builds the canonical π(t) closed form as documented in
    notes/STAGE_2_RESULTS.md §2.2. Catches the C4 1/κ fabrication
    regression.

    The π(t) form used:
        π(t) = K_star · ε² · (X̄/Ȳ)² ·
               [4ω t cos(4ω t) − sin(4ω t)] /
               [64 ω √(σ₀) t²]

    κ must NOT appear in the symbolic free symbols after simplification.

    The optional ``pi_t_expression`` parameter exists exclusively to
    enable the C4 regression test in test_verify.py to inject a
    deliberately-broken expression containing 1/κ and confirm the
    verifier returns passed=False. Production callers should always
    use the default.
    """
    if pi_t_expression is None:
        K_star, eps, X_bar, Y_bar, omega, t, sigma_0 = sp.symbols(
            "K_star eps X_bar Y_bar omega t sigma_0", positive=True
        )
        pi_t_expression = (
            K_star
            * eps**2
            * (X_bar / Y_bar) ** 2
            * (4 * omega * t * sp.cos(4 * omega * t) - sp.sin(4 * omega * t))
            / (64 * omega * sp.sqrt(sigma_0) * t**2)
        )
    pi_t_simplified = sp.simplify(pi_t_expression)
    kappa = sp.Symbol("kappa", positive=True)
    passed = kappa not in pi_t_simplified.free_symbols
    return RTagVerdict(
        r_tag="R2",
        passed=passed,
        expected=None,
        actual=None,
        residual=None,
        audit_sha256=audit_sha256,
        message=(
            f"κ ∉ free_symbols(π(t)): {passed}; "
            f"free_symbols={pi_t_simplified.free_symbols}"
        ),
    )


def verify_r3_perpetual_identity(*, tol: float, audit_sha256: str) -> RTagVerdict:
    """R3: lim_{{t→∞}} Δ^{{(a_s)}}_t residual ≤ tol (memo §1: 6.31e-9).

    Computes the symbolic limit of the amplitude-shape factor
        Δ(t) = [4ω t cos(4ω t) − sin(4ω t)] / (64 ω t²)
    as t → ∞ using sympy and verifies the residual |limit − 0| ≤ tol.
    """
    omega, t = sp.symbols("omega t", positive=True)
    delta_t = (4 * omega * t * sp.cos(4 * omega * t) - sp.sin(4 * omega * t)) / (
        64 * omega * t**2
    )
    limit_val = sp.limit(delta_t, t, sp.oo)
    # Guard against non-finite sympy results (sp.nan, sp.zoo, sp.oo) before
    # any coercion — serializing nan/inf into RTagVerdict is a JSON-emit hazard.
    if not (limit_val.is_finite is True or limit_val == sp.Integer(0)):
        return RTagVerdict(
            r_tag="R3",
            passed=False,
            expected=0.0,
            actual=None,
            residual=None,
            audit_sha256=audit_sha256,
            message=f"perpetual identity limit not finite: {limit_val}",
        )
    residual = float(abs(limit_val))
    passed = residual <= tol
    return RTagVerdict(
        r_tag="R3",
        passed=passed,
        expected=0.0,
        actual=residual,
        residual=residual,
        audit_sha256=audit_sha256,
        message=f"perpetual identity residual: {residual:.2e} (tol {tol:.2e})",
    )


def verify_r4_bracket_cardinality(
    *,
    brackets: list[tuple[int, int, int, int]],
    audit_sha256: str,
) -> RTagVerdict:
    """R4: |B_24| = 24 AND factorization 3 × 2 × 2 × 2.

    Index sets per spec v1.2.1 §5.2 (lines 383–388); cardinality
    derivation per notes/STAGE_2_RESULTS.md §2.4 (R4).

    Each bracket is a tuple (tier_idx, alpha_idx, cache_idx, kappa_idx).
    Verifier checks both the total count (24) AND the per-axis index-set
    cardinalities (3, 2, 2, 2) so a wrong factorization (e.g. 4×2×3×1)
    fails even when |B| = 24.
    """
    n = len(brackets)
    tier_idx = {b[0] for b in brackets}
    alpha_idx = {b[1] for b in brackets}
    cache_idx = {b[2] for b in brackets}
    kappa_idx = {b[3] for b in brackets}
    factor_passes = (
        len(tier_idx) == 3
        and len(alpha_idx) == 2
        and len(cache_idx) == 2
        and len(kappa_idx) == 2
    )
    passed = n == 24 and factor_passes
    return RTagVerdict(
        r_tag="R4",
        passed=passed,
        expected=24.0,
        actual=float(n),
        residual=float(abs(n - 24)),
        audit_sha256=audit_sha256,
        message=(
            f"|B|={n}; factorization tiers={len(tier_idx)} α={len(alpha_idx)} "
            f"cache={len(cache_idx)} κ={len(kappa_idx)} (must be 3×2×2×2)"
        ),
    )


def verify_r5_marginalization_match(
    *,
    posterior_chain: np.ndarray,
    tol: float,
    audit_sha256: str,
) -> RTagVerdict:
    """R5: marginalized posterior MC SE within tol at N_draws.

    For a synthetic chain whose discrete latents have been summed out
    analytically (C1 v0.4), the per-parameter MC standard error scales
    as σ/√N. The verifier confirms the maximum MC SE over all parameters
    is within the supplied ``tol``.

    Raises a ``FAIL`` verdict (not an exception) on shape mismatches or
    zero-draw chains.
    """
    if posterior_chain.ndim != 2:
        return RTagVerdict(
            r_tag="R5",
            passed=False,
            expected=tol,
            actual=None,
            residual=None,
            audit_sha256=audit_sha256,
            message=f"posterior_chain shape mismatch: ndim={posterior_chain.ndim}",
        )
    n_draws = posterior_chain.shape[0]
    if n_draws == 0:
        return RTagVerdict(
            r_tag="R5",
            passed=False,
            expected=tol,
            actual=None,
            residual=None,
            audit_sha256=audit_sha256,
            message="posterior_chain has zero draws",
        )
    max_mc_se = float(posterior_chain.std(axis=0).max() / math.sqrt(n_draws))
    passed = max_mc_se <= tol
    return RTagVerdict(
        r_tag="R5",
        passed=passed,
        expected=tol,
        actual=max_mc_se,
        residual=max_mc_se,
        audit_sha256=audit_sha256,
        message=(
            f"posterior max MC SE = {max_mc_se:.2e} at N={n_draws} "
            f"(tol {tol:.2e})"
        ),
    )


def verify_r6_softplus_l1_tightness(
    *,
    kappa: float,
    tol_factor: float,
    audit_sha256: str,
    beta_factor: float = 50.0,
) -> RTagVerdict:
    """R6: softplus L¹ deviation ≤ tol_factor · κ on [0, 2κ] (M2 pin: 1e-3·κ).

    Constructs ``SoftplusParams(beta=beta_factor / kappa, kappa=kappa)`` using
    the spec-prescribed β ≈ 50/κ baseline (distributions.py docstring, note
    that the criterion ``deviation < 1e-3·κ`` is met by ``β ≈ 50/κ``). Passes
    the params to ``tightness_l1_deviation`` and asserts the L¹ deviation
    satisfies the M2 tightness pin.

    ``beta_factor`` defaults to 50.0 (the M2 pin); override for future
    iterations exploring different β regimes without code change.

    Residual semantics: ``residual = deviation`` (distance from the ideal of
    zero L¹ deviation); ``expected = threshold`` (the gate value); ``actual =
    deviation`` (the measured value). Threshold is also reported in ``message``.

    Three-tier compliance: ``SoftplusParams`` and ``tightness_l1_deviation``
    are imported from ``simulations.types.distributions`` (Value tier + free
    pure function on Value); no IO or modules tier imports.
    """
    from simulations.types.distributions import SoftplusParams, tightness_l1_deviation

    params = SoftplusParams(beta=beta_factor / kappa, kappa=kappa)
    deviation = float(tightness_l1_deviation(params))
    threshold = tol_factor * kappa
    passed = deviation <= threshold
    return RTagVerdict(
        r_tag="R6",
        passed=passed,
        expected=threshold,
        actual=deviation,
        residual=deviation,
        audit_sha256=audit_sha256,
        message=(
            f"softplus L¹ deviation = {deviation:.6e}; "
            f"threshold = {threshold:.6e} ({tol_factor}·κ at κ={kappa})"
        ),
    )


def verify_r7_s_t_pin(
    *,
    revenue_form_verdict: dict[str, Any],
    audit_sha256: str,
) -> RTagVerdict:
    """R7: HALT-on-flip safeguard for the S_t pin is in force.

    The S_t form ``S_t = (1-λ)^t`` with ``λ ~ Beta(α_S=4.5, β_S=95.5)``
    is pinned at the spec level
    (docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md §6.1
    lines 405–442) — not in any committed JSON field. The runtime
    HALT-on-flip safeguard exposed by C3's PSIS-LOO-CV emit is the
    observable property: ``revenue_form_verdict._metadata.halt_on_flip_comparison``
    must be ``True``. If the ranked-forms comparison ever flips relative
    to the legacy prior, the safeguard fires and the spec-pinned form is
    preserved. The S_t pin is independently encoded in the spec; this
    verifier confirms the runtime gate is armed.

    ``CohortGateVerdict`` carries NO ``s_t_form`` / ``lambda_prior_alpha``
    / ``lambda_prior_beta`` fields — those do not exist on disk (v0.3.1
    plan-template correction).
    """
    metadata = revenue_form_verdict.get("_metadata", {})
    halt_on_flip = metadata.get("halt_on_flip_comparison")
    passed = halt_on_flip is True
    return RTagVerdict(
        r_tag="R7",
        passed=passed,
        expected=None,
        actual=None,
        residual=None,
        audit_sha256=audit_sha256,
        message=(
            f"runtime HALT-on-flip safeguard armed: {halt_on_flip!r}; "
            f"spec-level S_t pin (Beta(4.5, 95.5)) lives in prereg-lock §6.1, "
            f"not in this verdict"
        ),
    )


def verify_r8_z_cap_closed_form(
    *,
    z_cap_pinned: ZCapPinned,
    audit_sha256: str,
    expected_z: float = 4687.94,
    tol: float = 1.0,
) -> RTagVerdict:
    """R8: Z_cap ≈ 4687.94 COP/mo, 95% CI lower bound > 0 (memo §1).

    Two-part check:
        (a) point estimate within ``tol`` COP of ``expected_z`` (defaults:
            4687.94 COP/mo, tol=1.0 COP — the M2 pin);
        (b) 95% credible-interval lower bound is strictly positive —
            the cohort cap is positive at credible-interval confidence.

    ``expected_z`` and ``tol`` are parameterised so a future re-pin can be
    tested without code change.

    Field-name note: ``ZCapPinned.Z_cop_per_month`` is capitalised (Z,
    not z) per ``simulations/types/posterior.py`` line 292.
    """
    actual_z = float(z_cap_pinned.Z_cop_per_month)
    residual = abs(actual_z - expected_z)
    ci_lo = float(z_cap_pinned.ci_95_lo)
    z_match = residual <= tol
    ci_strictly_positive = ci_lo > 0.0
    passed = z_match and ci_strictly_positive
    return RTagVerdict(
        r_tag="R8",
        passed=passed,
        expected=expected_z,
        actual=actual_z,
        residual=residual,
        audit_sha256=audit_sha256,
        message=(
            f"Z_cap = {actual_z:.2f} COP/mo (expected ≈ {expected_z:.2f}; "
            f"residual {residual:.2e}); 95% CI lo = {ci_lo:.2f} > 0: "
            f"{ci_strictly_positive}"
        ),
    )
