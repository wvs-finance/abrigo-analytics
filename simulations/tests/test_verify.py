"""Verify sub-package tests (23 cases) per design v0.3 §3a.6 negative-case table.

Coverage:
  - 8 happy-path tests (R1–R8)
  - 12 negative tests (R1 perturbed-eps; R2 1/κ injection — calls
    verifier with injected expression + asserts passed=False; R4
    length-23 + length-25 + wrong-factorization 4×2×3×1; R5 tightened
    tol + shape-mismatch; R6 wide-tightness; R7 halt_on_flip False +
    _metadata missing; R8 perturbed-Z + ci-lo-nonpositive)
  - 1 R3 finite-guard test (negative tol forces FAIL with safe residual)
  - 2 cross-cutting tamper tests (AuditBlockMismatch + trio SHA drift)

Total: 23 cases. Floor 21 satisfied.
"""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import sympy as sp

from simulations.saas_builder.verify import (
    AuditBlockMismatch,
    CommittedArtifactLoader,
    verify_r1_sigma_0_anchor,
    verify_r2_kappa_eliminated_in_pi_t,
    verify_r3_perpetual_identity,
    verify_r4_bracket_cardinality,
    verify_r5_marginalization_match,
    verify_r6_softplus_l1_tightness,
    verify_r7_s_t_pin,
    verify_r8_z_cap_closed_form,
)

DATA_ROOT = Path("simulations/saas_builder/data")
DUMMY_SHA = "0" * 64


# ---------------------------------------------------------------------------
# R1: σ₀ = (X̄/Ȳ)² · ε² / 8   (M2 pin: 20,000)
# ---------------------------------------------------------------------------


def test_r1_happy() -> None:
    """R1 closed form at pinned parameters: σ₀ = (2/1)² · 200² / 8 = 20,000."""
    v = verify_r1_sigma_0_anchor(
        x_bar=2.0,
        y_bar=1.0,
        eps=200.0,
        expected=20_000.0,
        tol=1e-6,
        audit_sha256=DUMMY_SHA,
    )
    assert v.passed, v.message


def test_r1_negative_perturbed_eps() -> None:
    """R1: perturbing ε by 0.1 shifts σ₀ by ~500 — residual exceeds tol=1e-6."""
    v = verify_r1_sigma_0_anchor(
        x_bar=2.0,
        y_bar=1.0,
        eps=200.1,
        expected=20_000.0,
        tol=1e-6,
        audit_sha256=DUMMY_SHA,
    )
    assert not v.passed


# ---------------------------------------------------------------------------
# R2: κ ∉ free_symbols(π(t)) — anti-fishing free-symbol audit
# ---------------------------------------------------------------------------


def test_r2_happy_no_kappa() -> None:
    """R2: canonical π(t) form has κ eliminated after sympy.simplify."""
    v = verify_r2_kappa_eliminated_in_pi_t(audit_sha256=DUMMY_SHA)
    assert v.passed, v.message


def test_r2_negative_inject_one_over_kappa() -> None:
    """C4 anti-fishing regression guard: 1/κ injection must fail.

    Precondition (Wave-1 MQ-F4): simplified injected expression must
    retain κ in free_symbols (prevents 1/κ - 1/κ + π(t) cancellation
    false-pass). Then call the verifier with the injected expression
    and assert passed=False — exercises the actual contract.
    """
    K_star, eps_, X_bar, Y_bar, omega, t, sigma_0, kappa = sp.symbols(
        "K_star eps X_bar Y_bar omega t sigma_0 kappa", positive=True
    )
    legit = K_star * eps_**2 * (X_bar / Y_bar) ** 2 / (
        64 * omega * sp.sqrt(sigma_0) * t**2
    )
    injected = legit / kappa  # the C4 fabricated 1/κ factor
    # Wave-1 MQ-F4 precondition: prevent cancellation false-pass
    assert kappa in sp.simplify(injected).free_symbols, (
        "regression-guard precondition: simplified injected expression "
        f"must retain κ; got {sp.simplify(injected).free_symbols}"
    )
    v = verify_r2_kappa_eliminated_in_pi_t(
        audit_sha256=DUMMY_SHA, pi_t_expression=injected,
    )
    assert not v.passed, v.message


# ---------------------------------------------------------------------------
# R3: lim_{t→∞} Δ^{(a_s)}_t residual ≤ tol
# ---------------------------------------------------------------------------


def test_r3_happy() -> None:
    """R3: symbolic limit of amplitude-shape factor at t→∞ is 0 within tol 1e-8."""
    v = verify_r3_perpetual_identity(tol=1e-8, audit_sha256=DUMMY_SHA)
    assert v.passed, v.message



def test_r3_negative_nonfinite() -> None:
    """R3 finite-guard: negative tol forces FAIL with safe (non-nan/inf) residual.

    Phase 1 fix #1: when the sympy limit is not provably finite, the verifier
    returns FAIL with residual=None rather than float('nan'). This test
    exercises the negative-tol FAIL path and confirms the residual is either
    None or a finite float (never nan/inf), preserving JSON-serialisability.
    """
    v = verify_r3_perpetual_identity(tol=-1.0, audit_sha256=DUMMY_SHA)
    assert not v.passed
    if v.residual is not None:
        assert math.isfinite(v.residual)


# ---------------------------------------------------------------------------
# R4: |B_24| = 24 AND factorization 3 × 2 × 2 × 2
# ---------------------------------------------------------------------------


def _full_24() -> list[tuple[int, int, int, int]]:
    """Canonical 24-bracket set with factorization 3×2×2×2."""
    return [
        (t_, a, c, k_)
        for t_ in range(3)
        for a in range(2)
        for c in range(2)
        for k_ in range(2)
    ]


def test_r4_happy_24_full_factorization() -> None:
    """R4: 24 brackets with correct 3×2×2×2 factorization passes."""
    v = verify_r4_bracket_cardinality(brackets=_full_24(), audit_sha256=DUMMY_SHA)
    assert v.passed, v.message


def test_r4_negative_23() -> None:
    """R4: 23 brackets — cardinality below 24 must fail."""
    v = verify_r4_bracket_cardinality(
        brackets=_full_24()[:23], audit_sha256=DUMMY_SHA
    )
    assert not v.passed


def test_r4_negative_25() -> None:
    """R4: 25 brackets — cardinality above 24 must fail."""
    extra = _full_24() + [(0, 0, 0, 0)]
    v = verify_r4_bracket_cardinality(brackets=extra, audit_sha256=DUMMY_SHA)
    assert not v.passed


def test_r4_negative_wrong_factorization_4_2_3_1() -> None:
    """R4: cardinality 24 with wrong factorization 4×2×3×1 must fail.

    |B| = 4 × 2 × 3 × 1 = 24 but per-axis cardinalities (4, 2, 3, 1) ≠
    (3, 2, 2, 2) — verifier must reject even though total count is correct.
    """
    bad = [(t_, a, c, 0) for t_ in range(4) for a in range(2) for c in range(3)]
    assert len(bad) == 24, f"fixture error: expected 24 got {len(bad)}"
    v = verify_r4_bracket_cardinality(brackets=bad, audit_sha256=DUMMY_SHA)
    assert not v.passed


# ---------------------------------------------------------------------------
# R5: marginalized posterior MC SE within tol at N_draws
# ---------------------------------------------------------------------------


def test_r5_happy_synthetic_chain() -> None:
    """R5: MC SE of a normal(1, 0.1) chain at 712,000 draws is well below 1e-3."""
    rng = np.random.default_rng(0)
    chain = rng.normal(loc=1.0, scale=0.1, size=(712_000, 3))
    v = verify_r5_marginalization_match(
        posterior_chain=chain, tol=1e-3, audit_sha256=DUMMY_SHA
    )
    assert v.passed, v.message


def test_r5_negative_tightened_tol() -> None:
    """R5: tol squeezed to 1e-30 — MC SE cannot satisfy max_se ≤ 1e-30."""
    rng = np.random.default_rng(0)
    chain = rng.normal(loc=1.0, scale=0.1, size=(712_000, 3))
    v = verify_r5_marginalization_match(
        posterior_chain=chain, tol=1e-30, audit_sha256=DUMMY_SHA
    )
    assert not v.passed


def test_r5_negative_shape_mismatch() -> None:
    """R5: 1-D array is not a valid posterior chain — must fail with ndim message."""
    chain_1d = np.array([1.0, 2.0, 3.0])
    v = verify_r5_marginalization_match(
        posterior_chain=chain_1d, tol=1e-3, audit_sha256=DUMMY_SHA
    )
    assert not v.passed


# ---------------------------------------------------------------------------
# R6: softplus L¹ deviation ≤ tol_factor · κ on [0, 2κ]
# ---------------------------------------------------------------------------


def test_r6_happy_default_kappa() -> None:
    """R6: at κ=1.0 with default β_factor=50, deviation ≈ 6.6e-4 < 1e-3·κ."""
    v = verify_r6_softplus_l1_tightness(
        kappa=1.0, tol_factor=1e-3, audit_sha256=DUMMY_SHA
    )
    assert v.passed, v.message


def test_r6_negative_wide_tightness() -> None:
    """R6: tol_factor squeezed to 1e-15 — deviation ≈ 6.6e-4 >> 1e-15·κ → FAIL."""
    v = verify_r6_softplus_l1_tightness(
        kappa=1.0, tol_factor=1e-15, audit_sha256=DUMMY_SHA
    )
    assert not v.passed


# ---------------------------------------------------------------------------
# R7: HALT-on-flip safeguard for S_t pin
# ---------------------------------------------------------------------------


def test_r7_happy_halt_on_flip_true() -> None:
    """R7: _metadata.halt_on_flip_comparison = True → safeguard armed → PASS."""
    revenue = {"_metadata": {"halt_on_flip_comparison": True}}
    v = verify_r7_s_t_pin(revenue_form_verdict=revenue, audit_sha256=DUMMY_SHA)
    assert v.passed, v.message


def test_r7_negative_halt_on_flip_false() -> None:
    """R7: halt_on_flip_comparison = False → safeguard disarmed → FAIL."""
    revenue = {"_metadata": {"halt_on_flip_comparison": False}}
    v = verify_r7_s_t_pin(revenue_form_verdict=revenue, audit_sha256=DUMMY_SHA)
    assert not v.passed


def test_r7_negative_metadata_missing() -> None:
    """R7: _metadata key absent → halt_on_flip_comparison is None → FAIL."""
    revenue = {"_comparison": {}}
    v = verify_r7_s_t_pin(revenue_form_verdict=revenue, audit_sha256=DUMMY_SHA)
    assert not v.passed


# ---------------------------------------------------------------------------
# R8: Z_cap ≈ 4687.94 COP/mo, 95% CI lower bound > 0
# ---------------------------------------------------------------------------


def _fake_z(z: float, lo: float, hi: float) -> SimpleNamespace:
    """Lightweight stand-in for ZCapPinned with only the fields R8 reads.

    ``ZCapPinned.__post_init__`` validates many invariants (tier_mix,
    audit_block hex, etc.) that are out of scope for R8 unit tests. Using
    SimpleNamespace avoids that overhead while exercising the same attribute
    path that ``verify_r8_z_cap_closed_form`` reads.
    """
    return SimpleNamespace(Z_cop_per_month=z, ci_95_lo=lo, ci_95_hi=hi)


def test_r8_happy() -> None:
    """R8: Z_cap at M2-pin value 4687.94 COP/mo with positive CI → PASS."""
    z = _fake_z(4687.94, 168.17, 14606.14)
    v = verify_r8_z_cap_closed_form(
        z_cap_pinned=z,  # type: ignore[arg-type]
        audit_sha256=DUMMY_SHA,
    )
    assert v.passed, v.message


def test_r8_negative_z_perturbed_one_percent() -> None:
    """R8: Z_cap perturbed by +1% (~46.9 COP) exceeds tol=1.0 → FAIL."""
    z = _fake_z(4687.94 * 1.01, 168.17, 14606.14)
    v = verify_r8_z_cap_closed_form(
        z_cap_pinned=z,  # type: ignore[arg-type]
        audit_sha256=DUMMY_SHA,
    )
    assert not v.passed


def test_r8_negative_ci_lo_nonpositive() -> None:
    """R8: ci_95_lo = -1.0 violates the strictly-positive CI check → FAIL."""
    z = _fake_z(4687.94, -1.0, 14606.14)
    v = verify_r8_z_cap_closed_form(
        z_cap_pinned=z,  # type: ignore[arg-type]
        audit_sha256=DUMMY_SHA,
    )
    assert not v.passed


# ---------------------------------------------------------------------------
# Cross-cutting: CommittedArtifactLoader tamper detection
# ---------------------------------------------------------------------------


def test_loader_raises_on_audit_block_tamper(tmp_path: Path) -> None:
    """Tamper an artifact's audit_block field; confirm AuditBlockMismatch.

    Mutates Z_cap_pinned.json's audit_block to a syntactically invalid
    string and confirms the loader raises AuditBlockMismatch at construction
    (not silently loading a corrupt artifact).
    """
    src = DATA_ROOT
    if not src.exists():
        pytest.skip("committed data root absent")
    dst = tmp_path / "data"
    shutil.copytree(src, dst)
    z_path = dst / "Z_cap_pinned.json"
    raw = json.loads(z_path.read_text())
    raw["audit_block"] = "not-a-hex"
    z_path.write_text(json.dumps(raw))
    with pytest.raises(AuditBlockMismatch):
        CommittedArtifactLoader(dst)


def test_loader_trio_sha_changes_on_artifact_tamper(tmp_path: Path) -> None:
    """Mutate artifact bytes (not audit_block); confirm trio_audit_sha256 drifts.

    Injects a ``__tamper_marker`` field into Z_cap_pinned.json — this keeps
    the audit_block field syntactically valid so the loader constructs
    successfully, but changes the file bytes so the trio-level anchor
    (sha256-of-sha256 over the four JSONs) differs from the original.
    """
    src = DATA_ROOT
    if not src.exists():
        pytest.skip("committed data root absent")
    dst = tmp_path / "data"
    shutil.copytree(src, dst)
    # Capture baseline SHA from the original (unmodified) tree
    pre_sha = CommittedArtifactLoader(src).trio_audit_sha256
    # Inject a non-audit_block field to change file bytes without breaking
    # the audit_block hex validation
    z_path = dst / "Z_cap_pinned.json"
    raw = json.loads(z_path.read_text())
    raw["__tamper_marker"] = "test"
    z_path.write_text(json.dumps(raw))
    post_sha = CommittedArtifactLoader(dst).trio_audit_sha256
    assert pre_sha != post_sha
