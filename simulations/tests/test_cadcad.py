"""Tests for the cadCAD-integration package (paper §6, Phase 1).

Parent spec: ``docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex``
§6.2 — six state variables + six PSUBs. Phase 1 covers PSUBs 1, 2, 6;
PSUBs 3, 4, 5 are deferred-stub surfaces and the corresponding tests
assert that calling them raises ``NotImplementedError``.

Pin Z1.2 determinism is the primary integration invariant verified by
``TestRunSimulation::test_determinism_audit_block_and_arrays`` and
``TestCadCADCrossFamily``.
"""
from __future__ import annotations

import re

import numpy as np
import pytest

from simulations.cadcad import (
    CadCADConfig,
    CadCADConfigError,
    CadCADError,
    CadCADState,
    CadCADStateError,
    CadCADTrajectory,
    pre_sample_fx_path,
    psub_1_fx_advance,
    psub_2_sigma_t_accumulator,
    psub_2_sigma_t_accumulator_with_dt,
    psub_3_cost_advance,
    psub_4_replicating_portfolio_update,
    psub_5_wage_premium_drain,
    psub_6_ratchet,
    run_simulation,
)
from simulations.stochastic_fx import StochasticFXError

_AUDIT_BLOCK_REGEX = re.compile(r"^[0-9a-f]{64}$")


def _make_initial_state(**overrides: float | int) -> CadCADState:
    defaults: dict[str, float | int] = {
        "step": 0,
        "X": 4000.0,
        "S": 0.0,
        "C": 0.0,
        "P": 0.0,
        "W": 0.0,
        "R": 0.0,
    }
    defaults.update(overrides)
    return CadCADState(**defaults)  # type: ignore[arg-type]


def _make_config(**overrides) -> CadCADConfig:  # noqa: ANN003
    defaults = {
        "n_steps": 100,
        "dt": 0.01,
        "rng_seed": 42,
        "family_id": "gbm",
        "initial_state": _make_initial_state(),
    }
    defaults.update(overrides)
    return CadCADConfig(**defaults)


# ─── TestCadCADTypes ─────────────────────────────────────────────────────────


class TestCadCADTypes:
    """Value-tier invariant tests for CadCADState / CadCADConfig / CadCADTrajectory."""

    # ── error-hierarchy wiring ──────────────────────────────────────────────

    def test_error_hierarchy_root_extends_stochastic_fx(self) -> None:
        """CadCADError extends StochasticFXError per paper §6 charge."""
        assert issubclass(CadCADError, StochasticFXError)
        assert issubclass(CadCADError, Exception)
        assert issubclass(CadCADConfigError, CadCADError)
        assert issubclass(CadCADStateError, CadCADError)

    # ── CadCADState invariants ──────────────────────────────────────────────

    def test_state_constructs_valid(self) -> None:
        state = _make_initial_state()
        assert state.step == 0
        assert state.X == 4000.0

    def test_state_rejects_negative_step(self) -> None:
        with pytest.raises(CadCADStateError, match="step must be >= 0"):
            _make_initial_state(step=-1)

    def test_state_rejects_bool_step(self) -> None:
        with pytest.raises(CadCADStateError, match="step must be an int"):
            CadCADState(
                step=True,  # type: ignore[arg-type]
                X=4000.0,
                S=0.0,
                C=0.0,
                P=0.0,
                W=0.0,
                R=0.0,
            )

    def test_state_rejects_nonpositive_X(self) -> None:
        with pytest.raises(CadCADStateError, match="X must be > 0"):
            _make_initial_state(X=0.0)
        with pytest.raises(CadCADStateError, match="X must be > 0"):
            _make_initial_state(X=-1.0)

    def test_state_rejects_negative_W(self) -> None:
        with pytest.raises(CadCADStateError, match="W must be >= 0"):
            _make_initial_state(W=-0.1)

    def test_state_rejects_nonfinite_fields(self) -> None:
        for field in ("X", "S", "C", "P", "W", "R"):
            with pytest.raises(CadCADStateError, match="finite"):
                # X must remain > 0 even when the value is non-finite,
                # so we use an X-safe construction here.
                kwargs: dict[str, float] = {field: float("nan")}
                if field != "X":
                    kwargs.setdefault("X", 1.0)
                _make_initial_state(**kwargs)
            with pytest.raises(CadCADStateError, match="finite"):
                kwargs2: dict[str, float] = {field: float("inf")}
                if field != "X":
                    kwargs2.setdefault("X", 1.0)
                _make_initial_state(**kwargs2)

    def test_state_S_C_P_R_can_be_negative(self) -> None:
        """S, C, P, R have no positivity constraint at the Value tier."""
        state = _make_initial_state(S=-1.0, C=-1.0, P=-1.0, R=-1.0)
        assert state.S == -1.0
        assert state.C == -1.0

    # ── CadCADConfig invariants ─────────────────────────────────────────────

    def test_config_constructs_valid(self) -> None:
        cfg = _make_config()
        assert cfg.n_steps == 100
        assert cfg.family_id == "gbm"

    def test_config_rejects_nonpositive_n_steps(self) -> None:
        with pytest.raises(CadCADConfigError, match="n_steps must be > 0"):
            _make_config(n_steps=0)
        with pytest.raises(CadCADConfigError, match="n_steps must be > 0"):
            _make_config(n_steps=-5)

    def test_config_rejects_bool_n_steps(self) -> None:
        with pytest.raises(CadCADConfigError, match="n_steps must be an int"):
            _make_config(n_steps=True)

    def test_config_rejects_nonpositive_dt(self) -> None:
        with pytest.raises(CadCADConfigError, match="dt must be > 0"):
            _make_config(dt=0.0)
        with pytest.raises(CadCADConfigError, match="dt must be > 0"):
            _make_config(dt=-0.01)

    def test_config_rejects_nonfinite_dt(self) -> None:
        with pytest.raises(CadCADConfigError, match="dt must be finite"):
            _make_config(dt=float("inf"))

    def test_config_rejects_negative_rng_seed(self) -> None:
        with pytest.raises(CadCADConfigError, match="rng_seed must be >= 0"):
            _make_config(rng_seed=-1)

    def test_config_rejects_bool_rng_seed(self) -> None:
        with pytest.raises(CadCADConfigError, match="rng_seed must be an int"):
            _make_config(rng_seed=True)

    def test_config_rejects_unknown_family_id(self) -> None:
        with pytest.raises(CadCADConfigError, match="family_id must be one of"):
            _make_config(family_id="bachelier")

    def test_config_accepts_all_four_families(self) -> None:
        for fam in ("gbm", "ou", "merton", "deterministic"):
            cfg = _make_config(family_id=fam)
            assert cfg.family_id == fam

    def test_config_rejects_nonzero_initial_step(self) -> None:
        with pytest.raises(CadCADConfigError, match="initial_state.step must equal 0"):
            _make_config(initial_state=_make_initial_state(step=5))

    def test_config_rejects_non_cadcad_state(self) -> None:
        with pytest.raises(CadCADConfigError, match="initial_state must be a CadCADState"):
            CadCADConfig(
                n_steps=10,
                dt=0.01,
                rng_seed=0,
                family_id="gbm",
                initial_state="not-a-state",  # type: ignore[arg-type]
            )

    # ── CadCADTrajectory invariants ─────────────────────────────────────────

    def _valid_trajectory_kwargs(self) -> dict:
        n = 3
        return {
            "steps": np.arange(n + 1, dtype=np.int64),
            "X_path": np.ones(n + 1, dtype=np.float64),
            "S_path": np.zeros(n + 1, dtype=np.float64),
            "C_path": np.zeros(n + 1, dtype=np.float64),
            "P_path": np.zeros(n + 1, dtype=np.float64),
            "W_path": np.zeros(n + 1, dtype=np.float64),
            "R_path": np.zeros(n + 1, dtype=np.float64),
            "config_json": "{}",
            "audit_block": "0" * 64,
        }

    def test_trajectory_constructs_valid(self) -> None:
        traj = CadCADTrajectory(**self._valid_trajectory_kwargs())
        assert traj.steps.shape == (4,)

    def test_trajectory_rejects_mismatched_lengths(self) -> None:
        kwargs = self._valid_trajectory_kwargs()
        kwargs["X_path"] = np.ones(5, dtype=np.float64)
        with pytest.raises(CadCADStateError, match="X_path length must equal"):
            CadCADTrajectory(**kwargs)

    def test_trajectory_rejects_non_1d(self) -> None:
        kwargs = self._valid_trajectory_kwargs()
        kwargs["X_path"] = np.ones((2, 2), dtype=np.float64)
        with pytest.raises(CadCADStateError, match="X_path must be 1-D"):
            CadCADTrajectory(**kwargs)

    def test_trajectory_rejects_nonfinite_entries(self) -> None:
        kwargs = self._valid_trajectory_kwargs()
        kwargs["S_path"] = np.array([0.0, float("nan"), 0.0, 0.0], dtype=np.float64)
        with pytest.raises(CadCADStateError, match="S_path must contain only finite"):
            CadCADTrajectory(**kwargs)

    def test_trajectory_rejects_bad_audit_block(self) -> None:
        kwargs = self._valid_trajectory_kwargs()
        kwargs["audit_block"] = "not-a-hex-digest"
        with pytest.raises(CadCADStateError, match="audit_block must match"):
            CadCADTrajectory(**kwargs)

    def test_trajectory_rejects_empty_config_json(self) -> None:
        kwargs = self._valid_trajectory_kwargs()
        kwargs["config_json"] = ""
        with pytest.raises(CadCADStateError, match="config_json must be a non-empty"):
            CadCADTrajectory(**kwargs)

    def test_trajectory_rejects_integer_path_dtype(self) -> None:
        kwargs = self._valid_trajectory_kwargs()
        kwargs["X_path"] = np.zeros(4, dtype=np.int64)
        with pytest.raises(CadCADStateError, match="X_path must have floating dtype"):
            CadCADTrajectory(**kwargs)

    def test_trajectory_rejects_float_steps_dtype(self) -> None:
        kwargs = self._valid_trajectory_kwargs()
        kwargs["steps"] = np.arange(4, dtype=np.float64)
        with pytest.raises(CadCADStateError, match="steps must have integer dtype"):
            CadCADTrajectory(**kwargs)


# ─── TestPSUBs ───────────────────────────────────────────────────────────────


class TestPSUBs:
    """Golden-path tests for PSUB-1, PSUB-2, PSUB-6 + NotImplementedError stubs."""

    def test_psub_1_returns_next_path_entry(self) -> None:
        fx_path = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
        state = _make_initial_state(X=1.0)
        # step=0 → returns fx_path[1].
        assert psub_1_fx_advance(state=state, fx_path=fx_path) == 2.0
        state2 = _make_initial_state(step=2, X=3.0)
        assert psub_1_fx_advance(state=state2, fx_path=fx_path) == 4.0

    def test_psub_2_constant_path_yields_zero_sigma_t(self) -> None:
        """σ_T on a constant FX path is identically zero (paper eq. 7 sanity)."""
        fx_path = np.full(10, 100.0, dtype=np.float64)
        state = _make_initial_state(X=100.0)
        assert psub_2_sigma_t_accumulator_with_dt(
            state=state, fx_path=fx_path, dt=0.1
        ) == pytest.approx(0.0)
        # And the dt-agnostic form too.
        assert psub_2_sigma_t_accumulator(state=state, fx_path=fx_path) == pytest.approx(0.0)

    def test_psub_2_matches_full_path_sigma_t_at_terminal_step(self) -> None:
        """At the terminal step, the running σ_T matches the per-path σ_T form."""
        fx_path = np.array([1.0, 1.1, 0.9, 1.05, 0.95], dtype=np.float64)
        n_steps = 4
        dt = 0.25
        T = n_steps * dt
        # Stochastic-fx generators' per-path σ_T form (eq. 7).
        expected = float(np.sum((fx_path - fx_path.mean()) ** 2) / T)
        # PSUB-2 at state.step = n_steps - 1 → window covers full path.
        state = _make_initial_state(step=n_steps - 1, X=float(fx_path[n_steps - 1]))
        actual = psub_2_sigma_t_accumulator_with_dt(state=state, fx_path=fx_path, dt=dt)
        assert actual == pytest.approx(expected, rel=1e-12)

    def test_psub_6_returns_R_when_no_positive_increment(self) -> None:
        state = _make_initial_state(P=5.0, R=10.0)
        # P_new == P_old → no increment.
        assert psub_6_ratchet(state=state, P_new=5.0) == 10.0
        # P_new < P_old → still no increment (ratchet is one-sided).
        assert psub_6_ratchet(state=state, P_new=3.0) == 10.0

    def test_psub_6_accumulates_positive_increments_only(self) -> None:
        state = _make_initial_state(P=5.0, R=10.0)
        assert psub_6_ratchet(state=state, P_new=7.5) == pytest.approx(12.5)

    def test_psub_3_4_5_raise_not_implemented(self) -> None:
        state = _make_initial_state()
        with pytest.raises(NotImplementedError, match="PSUB-3"):
            psub_3_cost_advance(state=state)
        with pytest.raises(NotImplementedError, match="PSUB-4"):
            psub_4_replicating_portfolio_update(state=state)
        with pytest.raises(NotImplementedError, match="PSUB-5"):
            psub_5_wage_premium_drain(state=state)

    def test_pre_sample_fx_path_deterministic_is_constant(self) -> None:
        path = pre_sample_fx_path(
            family_id="deterministic", rng_seed=0, n_steps=10, dt=0.1, x_0=2.5
        )
        assert path.shape == (11,)
        assert np.all(path == 2.5)

    def test_pre_sample_fx_path_gbm_starts_at_x_0(self) -> None:
        path = pre_sample_fx_path(
            family_id="gbm", rng_seed=7, n_steps=50, dt=0.02, x_0=4000.0
        )
        assert path.shape == (51,)
        assert path[0] == 4000.0
        assert np.all(np.isfinite(path))

    def test_pre_sample_fx_path_pin_z12_determinism(self) -> None:
        """Same (family, seed, n_steps, dt, x_0) → bit-exact path."""
        a = pre_sample_fx_path(
            family_id="gbm", rng_seed=42, n_steps=100, dt=0.01, x_0=4000.0
        )
        b = pre_sample_fx_path(
            family_id="gbm", rng_seed=42, n_steps=100, dt=0.01, x_0=4000.0
        )
        np.testing.assert_array_equal(a, b)

    def test_pre_sample_fx_path_rejects_unknown_family(self) -> None:
        with pytest.raises(CadCADConfigError, match="family_id must be one of"):
            pre_sample_fx_path(
                family_id="bachelier", rng_seed=0, n_steps=10, dt=0.1, x_0=1.0
            )


# ─── TestRunSimulation ───────────────────────────────────────────────────────


class TestRunSimulation:
    """End-to-end tests of the run_simulation driver at the canonical small config."""

    def test_trajectory_shape_and_dtypes(self) -> None:
        cfg = _make_config()
        traj = run_simulation(cfg)
        n = cfg.n_steps
        assert traj.steps.shape == (n + 1,)
        assert traj.X_path.shape == (n + 1,)
        assert traj.S_path.shape == (n + 1,)
        assert traj.C_path.shape == (n + 1,)
        assert traj.P_path.shape == (n + 1,)
        assert traj.W_path.shape == (n + 1,)
        assert traj.R_path.shape == (n + 1,)
        assert np.issubdtype(traj.steps.dtype, np.integer)
        assert traj.X_path.dtype == np.float64

    def test_trajectory_finite_and_initial_seeded(self) -> None:
        cfg = _make_config()
        traj = run_simulation(cfg)
        assert np.all(np.isfinite(traj.X_path))
        assert np.all(np.isfinite(traj.S_path))
        # Initial state must seat at index 0 exactly.
        init = cfg.initial_state
        assert traj.X_path[0] == init.X
        assert traj.S_path[0] == init.S
        assert traj.C_path[0] == init.C
        assert traj.P_path[0] == init.P
        assert traj.W_path[0] == init.W
        assert traj.R_path[0] == init.R

    def test_audit_block_format(self) -> None:
        cfg = _make_config()
        traj = run_simulation(cfg)
        assert _AUDIT_BLOCK_REGEX.fullmatch(traj.audit_block) is not None

    def test_determinism_audit_block_and_arrays(self) -> None:
        """Pin Z1.2: identical config → bit-exact paths + audit_block."""
        cfg = _make_config()
        traj_a = run_simulation(cfg)
        traj_b = run_simulation(cfg)
        assert traj_a.audit_block == traj_b.audit_block
        for field in ("X_path", "S_path", "C_path", "P_path", "W_path", "R_path"):
            np.testing.assert_array_equal(
                getattr(traj_a, field), getattr(traj_b, field)
            )
        assert traj_a.config_json == traj_b.config_json

    def test_different_seeds_produce_different_paths(self) -> None:
        traj_a = run_simulation(_make_config(rng_seed=42))
        traj_b = run_simulation(_make_config(rng_seed=43))
        assert traj_a.audit_block != traj_b.audit_block
        # GBM with different seeds will produce different X paths.
        assert not np.array_equal(traj_a.X_path, traj_b.X_path)

    def test_phase_1_stubs_carry_state_forward(self) -> None:
        """PSUBs 3, 4, 5 deferred → C, P, W constant; PSUB-6 quiescent → R constant."""
        cfg = _make_config(
            initial_state=_make_initial_state(C=7.0, P=11.0, W=13.0, R=17.0)
        )
        traj = run_simulation(cfg)
        np.testing.assert_array_equal(traj.C_path, np.full_like(traj.C_path, 7.0))
        np.testing.assert_array_equal(traj.P_path, np.full_like(traj.P_path, 11.0))
        np.testing.assert_array_equal(traj.W_path, np.full_like(traj.W_path, 13.0))
        # R must remain at R_0 because PSUB-4 stub yields P_new == P_old,
        # so max(P_new − P_old, 0) == 0 and PSUB-6 emits R_{j+1} == R_j.
        np.testing.assert_array_equal(traj.R_path, np.full_like(traj.R_path, 17.0))

    def test_deterministic_family_yields_constant_X_and_zero_sigma(self) -> None:
        """End-to-end sanity: constant FX path → S_path identically zero."""
        cfg = _make_config(family_id="deterministic")
        traj = run_simulation(cfg)
        np.testing.assert_array_equal(traj.X_path, np.full_like(traj.X_path, 4000.0))
        # σ_T on a constant path is identically zero.
        np.testing.assert_array_equal(traj.S_path, np.zeros_like(traj.S_path))

    def test_gbm_terminal_sigma_t_matches_stochastic_fx_form(self) -> None:
        """End-to-end: terminal S_path matches the per-path σ_T from
        ``simulations.stochastic_fx.generators`` for the same (seed, x_0,
        n_steps, dt) — confirms the cadCAD layer's σ_T accumulator is
        wired to the same eq. 7 form, NOT a redefinition.
        """
        cfg = _make_config()
        traj = run_simulation(cfg)
        # Recompute the per-path σ_T directly from X_path.
        n_steps = cfg.n_steps
        T = n_steps * cfg.dt
        expected_terminal_sigma_t = float(
            np.sum((traj.X_path - traj.X_path.mean()) ** 2) / T
        )
        assert traj.S_path[-1] == pytest.approx(
            expected_terminal_sigma_t, rel=1e-12
        )

    def test_config_json_round_trippable(self) -> None:
        import json

        cfg = _make_config()
        traj = run_simulation(cfg)
        parsed = json.loads(traj.config_json)
        assert parsed["n_steps"] == cfg.n_steps
        assert parsed["dt"] == cfg.dt
        assert parsed["rng_seed"] == cfg.rng_seed
        assert parsed["family_id"] == cfg.family_id
        assert parsed["initial_state"]["X"] == cfg.initial_state.X


# ─── TestCadCADCrossFamily ───────────────────────────────────────────────────


class TestCadCADCrossFamily:
    """End-to-end runs across all four FX families + cross-family determinism."""

    @pytest.mark.parametrize("family_id", ["gbm", "ou", "merton", "deterministic"])
    def test_end_to_end_run_per_family(self, family_id: str) -> None:
        cfg = _make_config(family_id=family_id)
        traj = run_simulation(cfg)
        assert traj.X_path.shape == (cfg.n_steps + 1,)
        assert np.all(np.isfinite(traj.X_path))
        assert np.all(np.isfinite(traj.S_path))
        assert _AUDIT_BLOCK_REGEX.fullmatch(traj.audit_block) is not None
        assert traj.X_path[0] == cfg.initial_state.X

    @pytest.mark.parametrize("family_id", ["gbm", "ou", "merton", "deterministic"])
    def test_per_family_pin_z12_determinism(self, family_id: str) -> None:
        cfg = _make_config(family_id=family_id)
        a = run_simulation(cfg)
        b = run_simulation(cfg)
        assert a.audit_block == b.audit_block
        np.testing.assert_array_equal(a.X_path, b.X_path)
        np.testing.assert_array_equal(a.S_path, b.S_path)

    def test_different_families_produce_distinct_audit_blocks(self) -> None:
        """Different FX families on the same seed must produce different
        trajectories (and hence audit_blocks) — sanity check that the
        family_id dispatcher actually routes."""
        audits: dict[str, str] = {}
        for fam in ("gbm", "ou", "merton", "deterministic"):
            traj = run_simulation(_make_config(family_id=fam))
            audits[fam] = traj.audit_block
        # All four audit_blocks distinct.
        assert len(set(audits.values())) == 4
