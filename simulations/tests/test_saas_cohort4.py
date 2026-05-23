r"""Tests for SAAS-COHORT-4 — π(t) + Z-cap pin (plan v0.2 Pins M1–M4).

Coverage:

- M1 verification — symbolic π(t) closed form + free-symbol arity ≤ 6.
- M2 verification — 5-test-point sign-cert PASS (ci_95_lo > 0 ∀ TP).
- M2 monotonicity — strict chain |π|_TP2 > |π|_TP1 > |π|_TP3.
- M2 identity tolerance — π(t)·Δt ≈ ΔΠ residual ≤ 1e-6.
- M2-fix MC error budget — stderr/Ẑ ≤ 1e-3 with N_draws ≥ 4000.
- M3 schema enforcement — ZCapPinned constructor rejects malformed input.
- M4 audit-block determinism — same inputs → same digest; 1-byte change
  produces a different digest.
- Round-trip — ZCapPinned via writer + reader is field-equal.
- HALT triggers — DiagnosticGateError / MCErrorBudgetExceededError fire
  on synthetic violations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import numpy as np
import pytest
import sympy as sp
from hypothesis import HealthCheck, given, settings, strategies as st

from simulations.saas_builder.cohort_4 import (
    AuditBlockDriftError,
    AuditBlockResolver,
    DiagnosticGateError,
    IdentityResidualEvaluator,
    MCBudget,
    MCErrorBudgetExceededError,
    PerDrawZEvaluator,
    PiTSymbolic,
    SignVerdict,
    SignVerdictMarkdownRenderer,
    TestPoint,
    ZCapRunner,
    assert_audit_block_unchanged,
    assert_pin_m2_monotonicity,
    derive_pi_t_symbolic,
    make_default_test_point_grid,
    pin_and_emit,
)
from simulations.saas_builder.cohort_4.io import (
    _z_cap_pinned_equal,
)
from simulations.saas_builder.cohort_4.types import (
    MC_DRAWS_FLOOR,
    NUMERICAL_IDENTITY_TOL,
    PI_T_CANONICAL_SYMBOLS,
    stderr_ratio,
)
from simulations.types.posterior import ZCapPinned
from simulations.utils.json_io import ZCapPinnedReader, ZCapPinnedWriter

# ─── Reproducibility seed ────────────────────────────────────────────────────
_RNG_SEED: Final[int] = 20260508


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def pi_t() -> PiTSymbolic:
    return derive_pi_t_symbolic()


@pytest.fixture(scope="session")
def test_point_grid() -> tuple[TestPoint, ...]:
    return make_default_test_point_grid()


@pytest.fixture()
def realistic_q_t_cop_draws() -> np.ndarray:
    """N_draws sized to meet the Pin M2-fix MC budget (stderr/Ẑ ≤ 1e-3).

    Approximates the C1 posterior-predictive marginal as a tight
    log-normal (CV ≈ 0.05) so the per-draw Z population variance keeps
    stderr/Ẑ comfortably below the 1e-3 ceiling at the MC_DRAWS_FLOOR.
    For a smoke-run with the empirical C1 marginal (CV ≈ 0.84), the
    ``ZCapRunner`` would require ``mc_budget.n_draws ≈ 1e6`` to satisfy
    the budget — outside the scope of this fixture-driven unit test.
    """
    rng = np.random.default_rng(_RNG_SEED)
    n = MC_DRAWS_FLOOR
    # log-normal with E[X] = 1500, CV ≈ 0.05; stderr/Ẑ ≈ 0.05/√4000 ≈ 8e-4.
    sigma = 0.05
    mu = np.log(1500.0) - 0.5 * sigma**2
    return rng.lognormal(mean=mu, sigma=sigma, size=n).astype(np.float64)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Resolve repo root from this test file (works in any cwd)."""
    return Path(__file__).resolve().parents[2]


# ─── M1 — Symbolic π(t) ──────────────────────────────────────────────────────


class TestM1SymbolicPiT:
    def test_returns_PiTSymbolic_value(self, pi_t: PiTSymbolic) -> None:
        assert isinstance(pi_t, PiTSymbolic)
        assert isinstance(pi_t.expr, sp.Expr)

    def test_free_symbols_are_canonical_subset(self, pi_t: PiTSymbolic) -> None:
        canonical = set(PI_T_CANONICAL_SYMBOLS)
        assert pi_t.free_symbols.issubset(canonical)

    def test_free_symbol_arity_le_6(self, pi_t: PiTSymbolic) -> None:
        assert len(pi_t.free_symbols) <= 6

    def test_anchors_present(self, pi_t: PiTSymbolic) -> None:
        assert "PRIMITIVES" in pi_t.primitives_anchor
        assert "8.1" in pi_t.primitives_anchor
        assert "Carr-Madan" in pi_t.primitives_anchor
        assert "saas" in pi_t.saas_note_anchor.lower()
        assert "4.1" in pi_t.saas_note_anchor

    def test_lambdified_callable(self, pi_t: PiTSymbolic) -> None:
        # v0.3 honest signature: (K_star, sigma_0, eps, omega, t, xy_bar).
        # σ₀ pinned per PRIMITIVES.md §6 closed form: (4000²·0.1²)/8 = 2000.
        out = pi_t.lambdified(1.0e6, 2.0e3, 0.1, 1.0, 6.0, 4000.0)
        assert np.isfinite(out)
        # At t=6, ω=1, ε=0.1, X̄/Ȳ=4000, σ₀=2e3, K⋆=1e6:
        # numerator (4·6·cos(24) − sin(24)) ≈ −11.88 < 0?
        # cos(24 rad) ≈ -0.5328, sin(24 rad) ≈ -0.9056 → 24·-0.533+0.906 ≈ -11.88
        # Wait: numerator = 4ωt·cos(4ωt) − sin(4ωt) = 24·-0.5328 − (-0.9056) ≈ -11.88
        # So π < 0 at this anchor. Don't assert sign — surface honest output.
        # (Sign of π(t) varies in t per the closed-form trig kernel; sign
        # cert at the cap level operates on Z = q/(X/Y) + π, not on π
        # alone — Z > 0 follows from q/(X/Y) dominating |π| at the
        # per-draw level when K⋆_d = q_t_cop_d ∼ O(1500 COP).)

    def test_lambdified_broadcasts_K_star(self, pi_t: PiTSymbolic) -> None:
        K_arr = np.array([1.0e5, 1.0e6, 1.0e7], dtype=np.float64)
        out = pi_t.lambdified(K_arr, 2.0e3, 0.1, 1.0, 6.0, 4000.0)
        out = np.asarray(out)
        assert out.shape == (3,)
        # Strict monotone in |π| under K⋆ (linear scaling).
        assert abs(out[0]) < abs(out[1]) < abs(out[2])

    def test_kappa_not_in_free_symbols(self, pi_t: PiTSymbolic) -> None:
        # CORRECTIONS-α v0.3: κ MUST NOT appear in π(t).
        assert "kappa" not in pi_t.free_symbols
        assert "xy_bar" in pi_t.free_symbols

    def test_perpetual_identity_symbolic(self, pi_t: PiTSymbolic) -> None:
        # Non-tautological identity check: π(t) ≡ dΠ_lin/dt symbolically.
        from simulations.saas_builder.cohort_4.pi_derivation import (
            assert_perpetual_identity_symbolic,
        )
        # Raises ValueError on drift; does nothing on success.
        assert_perpetual_identity_symbolic(pi_t)


# ─── M2 — 5-test-point sign cert ─────────────────────────────────────────────


class TestM2FiveTestPointSignCert:
    def test_grid_is_5_tuple(
        self, test_point_grid: tuple[TestPoint, ...]
    ) -> None:
        assert len(test_point_grid) == 5
        labels = [tp.label for tp in test_point_grid]
        assert labels == ["TP1", "TP2", "TP3", "TP4", "TP5"]

    def test_sign_expectation_is_immutable_positive(
        self, test_point_grid: tuple[TestPoint, ...]
    ) -> None:
        for tp in test_point_grid:
            assert tp.sign_expectation == "positive"

    def test_per_draw_evaluator_produces_z_gt_0(
        self,
        pi_t: PiTSymbolic,
        test_point_grid: tuple[TestPoint, ...],
        realistic_q_t_cop_draws: np.ndarray,
    ) -> None:
        ev = PerDrawZEvaluator()
        for tp in test_point_grid:
            res = ev(pi_t, tp, realistic_q_t_cop_draws)
            assert res.z_mean > 0.0, f"{tp.label}: z_mean = {res.z_mean}"
            assert res.ci_95_lo > 0.0, f"{tp.label}: ci_95_lo = {res.ci_95_lo}"

    def test_runner_pass_path(
        self,
        pi_t: PiTSymbolic,
        test_point_grid: tuple[TestPoint, ...],
        realistic_q_t_cop_draws: np.ndarray,
    ) -> None:
        runner = ZCapRunner()
        results, sign_verdicts, mono = runner(
            pi_t, test_point_grid, realistic_q_t_cop_draws
        )
        assert len(results) == 5
        assert len(sign_verdicts) == 5
        for sv in sign_verdicts:
            assert sv.passes is True
            assert sv.identity_passes is True
        # v0.3 strict mono chain: |π|_TP4 > |π|_TP1 > |π|_TP5
        # (∂|π|/∂(X̄/Ȳ) > 0; replaces v0.2 κ-chain).
        assert mono[0] > mono[1] > mono[2]


# ─── M2 — Monotonicity (∂|π|/∂κ < 0) ─────────────────────────────────────────


class TestM2Monotonicity:
    def test_strict_chain_holds(
        self, pi_t: PiTSymbolic, test_point_grid: tuple[TestPoint, ...]
    ) -> None:
        triple = assert_pin_m2_monotonicity(pi_t, test_point_grid)
        assert triple[0] > triple[1] > triple[2]

    def test_violation_raises_DiagnosticGateError(
        self, pi_t: PiTSymbolic
    ) -> None:
        # v0.3: monotonicity is now in (X̄/Ȳ); invert TP4 and TP5 brackets.
        bad_grid = (
            TestPoint(label="TP1", kappa=6.5e6, x_over_y_bar=4000.0,
                      sigma_0=2.0e3, rationale="primary"),
            TestPoint(label="TP2", kappa=3.25e6, x_over_y_bar=4000.0,
                      sigma_0=2.0e3, rationale="low-cap"),
            TestPoint(label="TP3", kappa=9.75e6, x_over_y_bar=4000.0,
                      sigma_0=2.0e3, rationale="high-cap"),
            # Inverted: TP4 has LOWER X̄/Ȳ than TP5.
            TestPoint(label="TP4", kappa=6.5e6, x_over_y_bar=3800.0,
                      sigma_0=1.805e3, rationale="inverted-fx-low-as-high"),
            TestPoint(label="TP5", kappa=6.5e6, x_over_y_bar=4200.0,
                      sigma_0=2.205e3, rationale="inverted-fx-high-as-low"),
        )
        with pytest.raises(DiagnosticGateError, match="monotonicity violation"):
            assert_pin_m2_monotonicity(pi_t, bad_grid)


# ─── M2 — Identity tolerance ─────────────────────────────────────────────────


class TestM2IdentityTolerance:
    def test_residual_under_numerical_tolerance(
        self, pi_t: PiTSymbolic
    ) -> None:
        ev = IdentityResidualEvaluator()
        residual = ev(
            pi_t,
            K_star=1.0e6,
            sigma_0=2.0e3,  # v0.3: per PRIMITIVES §6 closed form (X̄/Ȳ=4000, ε=0.1)
            epsilon=0.1,
            omega=1.0,
            xy_bar=4000.0,
        )
        # Carr-Madan linearization is exact in σ_T to first order so the
        # discrete π·Δt ≈ ΔΠ identity holds tightly via the trapezoid rule.
        # Pin M2 numerical tolerance is 1e-6.
        assert residual < NUMERICAL_IDENTITY_TOL, (
            f"Identity residual {residual:.3e} exceeds {NUMERICAL_IDENTITY_TOL}"
        )


# ─── M2-fix — MC error budget ────────────────────────────────────────────────


class TestM2FixMCBudget:
    def test_stderr_ratio_under_ceiling(
        self,
        pi_t: PiTSymbolic,
        test_point_grid: tuple[TestPoint, ...],
        realistic_q_t_cop_draws: np.ndarray,
    ) -> None:
        ev = PerDrawZEvaluator()
        for tp in test_point_grid:
            res = ev(pi_t, tp, realistic_q_t_cop_draws)
            ratio = stderr_ratio(res)
            assert ratio <= 1e-3, (
                f"{tp.label}: stderr/Ẑ = {ratio:.6e} > 1e-3 ceiling"
            )

    def test_runner_breach_routes_to_HALT(
        self, pi_t: PiTSymbolic, test_point_grid: tuple[TestPoint, ...]
    ) -> None:
        # Force a tiny stderr-ratio ceiling (1e-12) so even a near-zero
        # variance population breaches the budget.
        budget = MCBudget(n_draws=MC_DRAWS_FLOOR,
                          stderr_ratio_ceiling=1e-12)
        runner = ZCapRunner(mc_budget=budget)
        rng = np.random.default_rng(_RNG_SEED)
        # High-variance draws guarantee stderr/Ẑ > 1e-12.
        draws = rng.lognormal(mean=7.0, sigma=0.4, size=MC_DRAWS_FLOOR)
        with pytest.raises(MCErrorBudgetExceededError):
            runner(pi_t, test_point_grid, draws)

    def test_below_floor_n_draws_raises(self) -> None:
        with pytest.raises(ValueError, match="must be ≥ 4000"):
            MCBudget(n_draws=100)


# ─── M3 — ZCapPinned schema enforcement ──────────────────────────────────────


class TestM3SchemaEnforcement:
    def test_audit_block_wrong_length_rejected(self) -> None:
        with pytest.raises(ValueError, match="audit_block"):
            ZCapPinned(
                Z_cop_per_month=1.0,
                ci_95_lo=0.5,
                ci_95_hi=1.5,
                audit_block="abc123",  # too short
            )

    def test_tier_mix_keys_drift_rejected(self) -> None:
        with pytest.raises(ValueError, match="tier_mix keys"):
            ZCapPinned(
                Z_cop_per_month=1.0,
                ci_95_lo=0.5,
                ci_95_hi=1.5,
                audit_block="0" * 64,
                tier_mix={"pro": 0.5, "max_5x": 0.5},  # missing max_20x
            )

    def test_tier_mix_sum_rejected(self) -> None:
        with pytest.raises(ValueError, match="sum to 1"):
            ZCapPinned(
                Z_cop_per_month=1.0,
                ci_95_lo=0.5,
                ci_95_hi=1.5,
                audit_block="0" * 64,
                tier_mix={"pro": 0.1, "max_5x": 0.1, "max_20x": 0.1},
            )

    def test_ci_ordering_rejected(self) -> None:
        with pytest.raises(ValueError, match="ci_95_lo"):
            ZCapPinned(
                Z_cop_per_month=1.0,
                ci_95_lo=2.0,  # > Z_cop_per_month
                ci_95_hi=3.0,
                audit_block="0" * 64,
            )


# ─── M4 — Audit-block determinism ────────────────────────────────────────────


class TestM4AuditBlockDeterminism:
    def test_same_inputs_same_digest(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f1.write_text("contents of a\n")
        f2 = tmp_path / "b.txt"
        f2.write_text("contents of b\n")
        resolver = AuditBlockResolver(
            repo_root=tmp_path, input_paths=("a.txt", "b.txt")
        )
        d1 = resolver()
        d2 = resolver()
        assert d1 == d2
        assert len(d1) == 64
        assert all(c in "0123456789abcdef" for c in d1)

    def test_one_byte_change_changes_digest(self, tmp_path: Path) -> None:
        f1 = tmp_path / "a.txt"
        f1.write_text("contents of a\n")
        f2 = tmp_path / "b.txt"
        f2.write_text("contents of b\n")
        resolver = AuditBlockResolver(
            repo_root=tmp_path, input_paths=("a.txt", "b.txt")
        )
        d1 = resolver()
        f1.write_text("contents of A\n")  # single-byte change
        d2 = resolver()
        assert d1 != d2

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        resolver = AuditBlockResolver(
            repo_root=tmp_path, input_paths=("nonexistent.txt",)
        )
        with pytest.raises(FileNotFoundError):
            resolver()

    def test_assert_audit_block_unchanged_drift_raises(
        self, tmp_path: Path
    ) -> None:
        f1 = tmp_path / "a.txt"
        f1.write_text("v1\n")
        resolver = AuditBlockResolver(
            repo_root=tmp_path, input_paths=("a.txt",)
        )
        original = resolver()
        f1.write_text("v2\n")
        with pytest.raises(AuditBlockDriftError):
            assert_audit_block_unchanged(
                original, repo_root=tmp_path, input_paths=("a.txt",)
            )

    def test_directory_expansion(self, tmp_path: Path) -> None:
        d = tmp_path / "subdir"
        d.mkdir()
        (d / "x").write_text("x")
        (d / "y").write_text("y")
        resolver = AuditBlockResolver(
            repo_root=tmp_path, input_paths=("subdir",)
        )
        digest = resolver()
        assert len(digest) == 64


# ─── JSON round-trip ─────────────────────────────────────────────────────────


class TestJsonRoundTrip:
    def test_roundtrip_field_equal(self, tmp_path: Path) -> None:
        z = ZCapPinned(
            Z_cop_per_month=1500.0,
            ci_95_lo=1200.0,
            ci_95_hi=1800.0,
            audit_block="a" * 64,
            tier_mix={"pro": 0.20, "max_5x": 0.50, "max_20x": 0.30},
        )
        path = tmp_path / "z.json"
        ZCapPinnedWriter()(z, path)
        z2 = ZCapPinnedReader()(path)
        assert _z_cap_pinned_equal(z, z2)


# ─── Sidecar Markdown render ─────────────────────────────────────────────────


class TestSidecarRender:
    def test_renderer_includes_all_TP_rows(
        self, test_point_grid: tuple[TestPoint, ...]
    ) -> None:
        renderer = SignVerdictMarkdownRenderer()
        sign_verdicts = tuple(
            SignVerdict(
                label=tp.label,
                z_value=1.0,
                ci_95_lo=0.5,
                ci_95_hi=1.5,
                passes=True,
                identity_residual=1e-9,
                identity_passes=True,
            )
            for tp in test_point_grid
        )
        body = renderer(
            sign_verdicts, test_point_grid, (1.5, 1.0, 0.5), "f" * 64
        )
        for tp in test_point_grid:
            assert tp.label in body
        assert "f" * 64 in body
        assert "PASS" in body
        assert "monotonicity" in body.lower()


# ─── pin_and_emit (full pipeline) ────────────────────────────────────────────


class TestPinAndEmitPipeline:
    def test_with_synthetic_inputs_emits_files(
        self,
        pi_t: PiTSymbolic,
        test_point_grid: tuple[TestPoint, ...],
        realistic_q_t_cop_draws: np.ndarray,
        tmp_path: Path,
    ) -> None:
        # Stub audit-block input files in tmp_path.
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        emit_dir = tmp_path / "emit"
        json_path, sidecar_path, z_cap, sign_verdicts = pin_and_emit(
            q_t_cop_draws=realistic_q_t_cop_draws,
            test_points=test_point_grid,
            repo_root=tmp_path,
            audit_input_paths=("a.txt", "b.txt"),
            emit_dir=emit_dir,
        )
        assert json_path.is_file()
        assert sidecar_path.is_file()
        assert z_cap.Z_cop_per_month > 0.0
        assert z_cap.ci_95_lo > 0.0
        assert len(sign_verdicts) == 5
        for sv in sign_verdicts:
            assert sv.passes is True

        # JSON round-trip via reader.
        z2 = ZCapPinnedReader()(json_path)
        assert _z_cap_pinned_equal(z_cap, z2)

        # Sidecar contains audit block + per-TP rows.
        body = sidecar_path.read_text()
        assert z_cap.audit_block in body
        for tp in test_point_grid:
            assert tp.label in body


# ─── Hypothesis property strategies ──────────────────────────────────────────


@st.composite
def _test_point_strategy(draw: st.DrawFn) -> TestPoint:
    label = draw(st.sampled_from(("TP1", "TP2", "TP3", "TP4", "TP5")))
    xy = draw(st.floats(min_value=3000.0, max_value=5000.0,
                        allow_nan=False, allow_infinity=False))
    eps = draw(st.floats(min_value=0.05, max_value=0.5,
                         allow_nan=False, allow_infinity=False))
    # σ₀ pinned per PRIMITIVES.md §6 closed form (CORRECTIONS-α v0.3).
    s0 = (xy**2) * (eps**2) / 8.0
    return TestPoint(
        label=label,
        kappa=draw(st.floats(min_value=1e5, max_value=1e8,
                             allow_nan=False, allow_infinity=False)),
        x_over_y_bar=xy,
        sigma_0=s0,
        rationale="hypothesis-strategy",
    )


class TestHypothesisProperties:
    @given(tp=_test_point_strategy())
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    def test_test_point_invariants(self, tp: TestPoint) -> None:
        assert tp.kappa > 0
        assert tp.x_over_y_bar > 0
        assert tp.sigma_0 > 0
        assert tp.sign_expectation == "positive"

    @given(
        xy_bar=st.floats(min_value=3000.0, max_value=5000.0,
                         allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50, deadline=None)
    def test_pi_strict_increasing_in_xy_bar(self, xy_bar: float) -> None:
        """Joint-identifiability: ∂|π|/∂(X̄/Ȳ) > 0 (plan v0.3 §M2-fix).

        CORRECTIONS-α v0.3: replaces v0.2's ∂|π|/∂κ < 0 property which
        was structurally unsatisfiable (κ ∉ free_symbols(π)) and was
        only "passing" in v0.2 via a spurious 1/κ post-hoc factor.
        """
        pi_t = derive_pi_t_symbolic()
        xy2 = xy_bar * 1.1  # 10% higher
        # σ₀ pinned per X̄/Ȳ via PRIMITIVES.md §6 closed form.
        s0_1 = (xy_bar**2) * 0.01 / 8.0
        s0_2 = (xy2**2) * 0.01 / 8.0
        v1 = float(np.abs(np.asarray(
            pi_t.lambdified(1.0e6, s0_1, 0.1, 1.0, 6.0, xy_bar)
        ).item()))
        v2 = float(np.abs(np.asarray(
            pi_t.lambdified(1.0e6, s0_2, 0.1, 1.0, 6.0, xy2)
        ).item()))
        assert v2 > v1, (
            f"Expected |π|({xy2}) > |π|({xy_bar}); got {v2} vs {v1}"
        )


# ─── Smoke test against real C1 outputs (if present) ─────────────────────────


class TestSmokeAgainstC1:
    def test_pin_and_emit_with_real_C1_outputs(
        self,
        pi_t: PiTSymbolic,
        test_point_grid: tuple[TestPoint, ...],
        repo_root: Path,
        tmp_path: Path,
    ) -> None:
        """Smoke-run against real C1 + spec; stub C2/C3 if missing."""
        c1_synth = repo_root / "simulations/saas_builder/data/synthetic_tau_t"
        if not c1_synth.is_dir():
            pytest.skip("C1 synthetic_tau_t not present")
        # Build draws from C1.
        from simulations.utils.parquet_io import SyntheticTauReader

        reader = SyntheticTauReader()
        rows = reader(c1_synth)
        # Use the first MC_DRAWS_FLOOR rows of q_t_cop.
        q_t_cop = np.asarray(
            [r["q_t_cop"] for r in rows[: MC_DRAWS_FLOOR]],
            dtype=np.float64,
        )

        # Synthesize stub C2/C3 artifact files at canonical paths if missing.
        nb_dir = repo_root / "notebooks/saas_builder_stage_2/estimates"
        created: list[Path] = []
        nb_dir_created = False
        if not nb_dir.exists():
            nb_dir.mkdir(parents=True)
            nb_dir_created = True
        for relname in ("ROBUSTNESS_RESULTS.md", "PRIMARY_RESULTS.md"):
            p = nb_dir / relname
            if not p.exists():
                p.write_text(
                    f"# stub for cohort-4 smoke test ({relname})\n",
                    encoding="utf-8",
                )
                created.append(p)
        # Empirical C1 CV ≈ 0.84 ⟹ stderr/Ẑ ≈ 1.3e-2 at N=4000, which
        # breaches the Pin M2-fix MC budget (1e-3). Per plan v0.2 HALT-
        # pivot ladder: the proper disposition is HALT + WEAK verdict
        # pending C1 re-fit; the smoke test asserts that breach rather
        # than silently widening the ceiling (anti-fishing).
        cv_real = float(q_t_cop.std() / q_t_cop.mean())
        if cv_real / np.sqrt(MC_DRAWS_FLOOR) > 1e-3:
            with pytest.raises(MCErrorBudgetExceededError):
                pin_and_emit(
                    q_t_cop_draws=q_t_cop,
                    test_points=test_point_grid,
                    repo_root=repo_root,
                    emit_dir=tmp_path,
                )
            return  # smoke-run completes; HALT is the expected route
        try:
            json_path, sidecar_path, z_cap, sign_verdicts = pin_and_emit(
                q_t_cop_draws=q_t_cop,
                test_points=test_point_grid,
                repo_root=repo_root,
                emit_dir=tmp_path,
            )
            assert json_path.is_file()
            assert z_cap.Z_cop_per_month > 0.0
            for sv in sign_verdicts:
                assert sv.passes is True
        finally:
            # Cleanup stubs we created.
            for p in created:
                p.unlink()
            if nb_dir_created:
                # Remove only if we created and it's empty.
                try:
                    nb_dir.rmdir()
                    nb_dir.parent.rmdir()
                except OSError:
                    pass
