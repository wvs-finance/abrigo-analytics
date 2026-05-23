"""Value-tier containers for stochastic-fx — per-family SDE Parameters, canonical pins, MC ensemble + inversion verdict.

Parent spec: ``docs/specs/2026-05-11-stochastic-fx-variant-design.md`` v0.3 §4.2
is the authority for the canonical numerical pins re-exported from this module.

This module declares one ``@dataclass(frozen=True)`` Parameters container per
SDE family covered by the stochastic-fx variant package, plus the two
verdict-bearing Value types consumed by the Phase-A/B/C verifier pipeline:

- ``GBMParameters`` — geometric Brownian motion (drift ``mu``, volatility
  ``sigma``).
- ``OUParameters`` — mean-reverting Ornstein-Uhlenbeck (speed ``theta``,
  long-run level ``mu_bar``, volatility ``sigma``).
- ``JumpDiffusionParameters`` — Merton jump-diffusion (continuous drift
  ``mu``/``sigma`` plus compound-Poisson jump component
  ``lambda_jump``/``jump_mean``/``jump_std``).
- ``PathEnsemble`` — deterministic Monte-Carlo path matrix + per-path σ_T
  (Pin Z1.2 reproducibility surface).
- ``InversionVerdict`` — Phase-A algebraic / Phase-B moment / Phase-C KS
  pass/fail with composite-AND invariant (Pins Z1.3a/Z1.3b/Z1.4).

Each frozen-dc validates invariants in ``__post_init__`` and raises
``SDEParameterError`` on violation. All numeric fields are checked for
finiteness; family-specific positivity / non-negativity constraints follow the
invariants table in the parent plan Task 1.2 brief.

The three module-level ``Final`` canonical pins (``CANONICAL_GBM``,
``CANONICAL_OU``, ``CANONICAL_MERTON``) reproduce spec v0.3 §4.2 verbatim and
function as the reference fixtures consumed downstream by the per-family
verifiers (Phase A algebraic / Phase B moment match / Phase C KS GoF).

NO IO at this tier. NO inheritance except Exception (via the raised
``SDEParameterError`` from ``simulations.stochastic_fx._errors``).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Final

import numpy as np

from simulations.stochastic_fx._errors import SDEParameterError

#: Closed alphabet of admitted SDE family identifiers (spec v0.3 §4.2).
_FAMILY_ALPHABET: Final[frozenset[str]] = frozenset({"gbm", "ou", "merton"})

#: 64-char lowercase hex audit_block regex (sha256 hexdigest format).
_AUDIT_BLOCK_REGEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _require_finite(name: str, value: float) -> None:
    """Raise ``SDEParameterError`` if ``value`` is NaN or +/- infinity."""
    if not math.isfinite(value):
        raise SDEParameterError(f"{name} must be finite; got {value!r}")


def _require_finite_array(name: str, arr: np.ndarray) -> None:
    """Raise ``SDEParameterError`` if any element of ``arr`` is NaN or +/- infinity."""
    if not np.all(np.isfinite(arr)):
        raise SDEParameterError(f"{name} must contain only finite values")


# ─── GBM ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GBMParameters:
    """Parameters for the geometric Brownian motion family.

    Invariants (raise ``SDEParameterError``):

    - ``sigma > 0``, ``x_0 > 0``, ``T > 0``, ``dt > 0``;
    - ``n_steps >= 2``;
    - ``abs(n_steps * dt - T) < 1e-9 * T`` (grid consistency);
    - all numeric fields finite.
    """

    mu: float
    sigma: float
    x_0: float
    T: float
    dt: float
    n_steps: int

    def __post_init__(self) -> None:
        _require_finite("mu", self.mu)
        _require_finite("sigma", self.sigma)
        _require_finite("x_0", self.x_0)
        _require_finite("T", self.T)
        _require_finite("dt", self.dt)
        if self.sigma <= 0.0:
            raise SDEParameterError(f"sigma must be > 0; got {self.sigma!r}")
        if self.x_0 <= 0.0:
            raise SDEParameterError(f"x_0 must be > 0; got {self.x_0!r}")
        if self.T <= 0.0:
            raise SDEParameterError(f"T must be > 0; got {self.T!r}")
        if self.dt <= 0.0:
            raise SDEParameterError(f"dt must be > 0; got {self.dt!r}")
        if self.n_steps < 2:
            raise SDEParameterError(f"n_steps must be >= 2; got {self.n_steps!r}")
        if abs(self.n_steps * self.dt - self.T) >= 1e-9 * self.T:
            raise SDEParameterError(
                "n_steps * dt must equal T within 1e-9 * T; "
                f"got n_steps={self.n_steps!r}, dt={self.dt!r}, T={self.T!r}, "
                f"residual={abs(self.n_steps * self.dt - self.T)!r}"
            )


# ─── OU ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class OUParameters:
    """Parameters for the Ornstein-Uhlenbeck (mean-reverting) family.

    Invariants (raise ``SDEParameterError``):

    - ``theta > 0``, ``sigma > 0``, ``mu_bar > 0``, ``x_0 > 0``;
    - ``T > 0``, ``dt > 0``;
    - ``n_steps >= 2``;
    - all numeric fields finite.
    """

    theta: float
    mu_bar: float
    sigma: float
    x_0: float
    T: float
    dt: float
    n_steps: int

    def __post_init__(self) -> None:
        _require_finite("theta", self.theta)
        _require_finite("mu_bar", self.mu_bar)
        _require_finite("sigma", self.sigma)
        _require_finite("x_0", self.x_0)
        _require_finite("T", self.T)
        _require_finite("dt", self.dt)
        if self.theta <= 0.0:
            raise SDEParameterError(f"theta must be > 0; got {self.theta!r}")
        if self.sigma <= 0.0:
            raise SDEParameterError(f"sigma must be > 0; got {self.sigma!r}")
        if self.mu_bar <= 0.0:
            raise SDEParameterError(f"mu_bar must be > 0; got {self.mu_bar!r}")
        if self.x_0 <= 0.0:
            raise SDEParameterError(f"x_0 must be > 0; got {self.x_0!r}")
        if self.T <= 0.0:
            raise SDEParameterError(f"T must be > 0; got {self.T!r}")
        if self.dt <= 0.0:
            raise SDEParameterError(f"dt must be > 0; got {self.dt!r}")
        if self.n_steps < 2:
            raise SDEParameterError(f"n_steps must be >= 2; got {self.n_steps!r}")


# ─── Merton jump-diffusion ───────────────────────────────────────────────────


@dataclass(frozen=True)
class JumpDiffusionParameters:
    """Parameters for the Merton jump-diffusion family.

    Invariants (raise ``SDEParameterError``):

    - ``sigma > 0``, ``lambda_jump >= 0``, ``jump_std > 0``;
    - ``x_0 > 0``, ``T > 0``, ``dt > 0``;
    - ``n_steps >= 2``;
    - all numeric fields finite.

    The continuous drift ``mu`` and the jump-size mean ``jump_mean`` are
    unrestricted (any finite real number is admitted).
    """

    mu: float
    sigma: float
    lambda_jump: float
    jump_mean: float
    jump_std: float
    x_0: float
    T: float
    dt: float
    n_steps: int

    def __post_init__(self) -> None:
        _require_finite("mu", self.mu)
        _require_finite("sigma", self.sigma)
        _require_finite("lambda_jump", self.lambda_jump)
        _require_finite("jump_mean", self.jump_mean)
        _require_finite("jump_std", self.jump_std)
        _require_finite("x_0", self.x_0)
        _require_finite("T", self.T)
        _require_finite("dt", self.dt)
        if self.sigma <= 0.0:
            raise SDEParameterError(f"sigma must be > 0; got {self.sigma!r}")
        if self.lambda_jump < 0.0:
            raise SDEParameterError(
                f"lambda_jump must be >= 0; got {self.lambda_jump!r}"
            )
        if self.jump_std <= 0.0:
            raise SDEParameterError(f"jump_std must be > 0; got {self.jump_std!r}")
        if self.x_0 <= 0.0:
            raise SDEParameterError(f"x_0 must be > 0; got {self.x_0!r}")
        if self.T <= 0.0:
            raise SDEParameterError(f"T must be > 0; got {self.T!r}")
        if self.dt <= 0.0:
            raise SDEParameterError(f"dt must be > 0; got {self.dt!r}")
        if self.n_steps < 2:
            raise SDEParameterError(f"n_steps must be >= 2; got {self.n_steps!r}")


# ─── Canonical pins (spec v0.3 §4.2) ─────────────────────────────────────────


#: Canonical GBM pin per spec v0.3 §4.2.
CANONICAL_GBM: Final[GBMParameters] = GBMParameters(
    mu=0.0,
    sigma=0.10 / math.sqrt(12.0),
    x_0=4000.0,
    T=12.0,
    dt=12.0 / 5000.0,
    n_steps=5000,
)

#: Canonical OU pin per spec v0.3 §4.2.
CANONICAL_OU: Final[OUParameters] = OUParameters(
    theta=1.0,
    mu_bar=4000.0,
    sigma=0.10 * 4000.0 / math.sqrt(2.0 * 1.0),
    x_0=4000.0,
    T=12.0,
    dt=12.0 / 5000.0,
    n_steps=5000,
)

#: Canonical Merton jump-diffusion pin per spec v0.3 §4.2.
CANONICAL_MERTON: Final[JumpDiffusionParameters] = JumpDiffusionParameters(
    mu=0.0,
    sigma=0.05 / math.sqrt(12.0),
    lambda_jump=1.0,
    jump_mean=0.0,
    jump_std=0.10,
    x_0=4000.0,
    T=12.0,
    dt=12.0 / 5000.0,
    n_steps=5000,
)


# ─── PathEnsemble ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PathEnsemble:
    """Deterministic Monte-Carlo path ensemble for one SDE family (Pin Z1.2).

    Holds a 2-D path matrix of shape ``(N_paths, n_steps + 1)``, the per-path
    realised-variance vector ``sigma_t`` of length ``N_paths`` (one σ_T per
    path), the canonical parameters JSON, the RNG seed used, and the 64-char
    lowercase hex audit_block. Audit-block COMPUTATION is a Callable-tier
    concern downstream; this Value type only validates the value's format.

    Invariants (raise ``SDEParameterError``):

    - ``family_id`` in closed alphabet ``{"gbm", "ou", "merton"}``;
    - ``paths.ndim == 2``;
    - ``sigma_t.ndim == 1`` and ``sigma_t.shape[0] == paths.shape[0]``;
    - all entries of ``paths`` and ``sigma_t`` are finite;
    - ``canonical_params_json`` is a non-empty ``str``;
    - ``rng_seed`` is a non-negative ``int`` (and not a ``bool``);
    - ``audit_block`` matches ``^[0-9a-f]{64}$``.

    Equality / hash caveat: ``__eq__`` and ``__hash__`` are the
    ``dataclass(frozen=True)``-auto-generated forms, which dispatch through
    ``np.ndarray.__eq__`` on the ``paths`` / ``sigma_t`` fields. Comparing
    two ``PathEnsemble`` instances raises ``ValueError`` and hashing raises
    ``TypeError`` for the same reason ndarray is non-hashable. Mirrors
    ``simulations.saas_builder.cohort_4.types.ZEvaluationResult`` —
    round-trip equality is supplied by a hand-written helper at the IO
    Boundary tier (forward-reference: Task 5 ``emit.py``).
    """

    family_id: str
    paths: np.ndarray
    sigma_t: np.ndarray
    canonical_params_json: str
    rng_seed: int
    audit_block: str

    def __post_init__(self) -> None:
        if self.family_id not in _FAMILY_ALPHABET:
            raise SDEParameterError(
                f"family_id must be one of {sorted(_FAMILY_ALPHABET)!r}; "
                f"got {self.family_id!r}"
            )
        if not isinstance(self.paths, np.ndarray):
            raise SDEParameterError(
                f"paths must be a numpy.ndarray; got {type(self.paths)!r}"
            )
        if not isinstance(self.sigma_t, np.ndarray):
            raise SDEParameterError(
                f"sigma_t must be a numpy.ndarray; got {type(self.sigma_t)!r}"
            )
        if self.paths.ndim != 2:
            raise SDEParameterError(
                f"paths must be 2-D; got ndim={self.paths.ndim!r}"
            )
        if self.sigma_t.ndim != 1:
            raise SDEParameterError(
                f"sigma_t must be 1-D; got ndim={self.sigma_t.ndim!r}"
            )
        if self.sigma_t.shape[0] != self.paths.shape[0]:
            raise SDEParameterError(
                "sigma_t length must equal paths.shape[0]; "
                f"got sigma_t.shape[0]={self.sigma_t.shape[0]!r}, "
                f"paths.shape[0]={self.paths.shape[0]!r}"
            )
        _require_finite_array("paths", self.paths)
        _require_finite_array("sigma_t", self.sigma_t)
        if not isinstance(self.canonical_params_json, str):
            raise SDEParameterError(
                "canonical_params_json must be a str; "
                f"got {type(self.canonical_params_json)!r}"
            )
        if len(self.canonical_params_json) == 0:
            raise SDEParameterError("canonical_params_json must be a non-empty str")
        if isinstance(self.rng_seed, bool) or not isinstance(self.rng_seed, int):
            raise SDEParameterError(
                f"rng_seed must be an int (not bool); got {type(self.rng_seed)!r}"
            )
        if self.rng_seed < 0:
            raise SDEParameterError(
                f"rng_seed must be >= 0; got {self.rng_seed!r}"
            )
        if not isinstance(self.audit_block, str):
            raise SDEParameterError(
                f"audit_block must be a str; got {type(self.audit_block)!r}"
            )
        if _AUDIT_BLOCK_REGEX.fullmatch(self.audit_block) is None:
            raise SDEParameterError(
                "audit_block must match ^[0-9a-f]{64}$; "
                f"got {self.audit_block!r}"
            )


# ─── InversionVerdict ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class InversionVerdict:
    """Three-phase verification verdict for one SDE family (Pins Z1.3a/Z1.3b/Z1.4).

    Carries Phase-A algebraic-inversion residual (Pin Z1.3a), Phase-B per-moment
    relative errors against hand-derived analytic moments (Pin Z1.3b), and
    Phase-C KS goodness-of-fit p-value against the moment-matched parametric
    reference (Pin Z1.4). ``composite_pass`` MUST equal the logical AND of the
    three phase-pass flags.

    Invariants (raise ``SDEParameterError``):

    - ``family_id`` in closed alphabet ``{"gbm", "ou", "merton"}``;
    - each ``*_pass`` field is a ``bool`` (not just an ``int``);
    - ``composite_pass == phase_a_pass and phase_b_pass and phase_c_pass``;
    - all float fields are finite;
    - ``phase_a_max_residual >= 0``;
    - ``phase_b_mean_rel_err >= 0``, ``phase_b_var_rel_err >= 0``;
    - ``0.0 <= phase_c_ks_pvalue <= 1.0``;
    - ``phase_c_n_paths >= 0``;
    - ``tex_anchor`` is a non-empty ``str``;
    - ``audit_block`` matches ``^[0-9a-f]{64}$``.
    """

    family_id: str
    phase_a_pass: bool
    phase_a_max_residual: float
    phase_b_pass: bool
    phase_b_mean_rel_err: float
    phase_b_var_rel_err: float
    phase_c_pass: bool
    phase_c_ks_pvalue: float
    phase_c_n_paths: int
    composite_pass: bool
    tex_anchor: str
    audit_block: str

    def __post_init__(self) -> None:
        if self.family_id not in _FAMILY_ALPHABET:
            raise SDEParameterError(
                f"family_id must be one of {sorted(_FAMILY_ALPHABET)!r}; "
                f"got {self.family_id!r}"
            )
        for name, value in (
            ("phase_a_pass", self.phase_a_pass),
            ("phase_b_pass", self.phase_b_pass),
            ("phase_c_pass", self.phase_c_pass),
            ("composite_pass", self.composite_pass),
        ):
            if not isinstance(value, bool):
                raise SDEParameterError(
                    f"{name} must be bool; got {type(value)!r}"
                )
        expected_composite = (
            self.phase_a_pass and self.phase_b_pass and self.phase_c_pass
        )
        if self.composite_pass != expected_composite:
            raise SDEParameterError(
                "composite_pass must equal "
                "(phase_a_pass and phase_b_pass and phase_c_pass); "
                f"got composite_pass={self.composite_pass!r}, "
                f"expected={expected_composite!r}"
            )
        _require_finite("phase_a_max_residual", self.phase_a_max_residual)
        _require_finite("phase_b_mean_rel_err", self.phase_b_mean_rel_err)
        _require_finite("phase_b_var_rel_err", self.phase_b_var_rel_err)
        _require_finite("phase_c_ks_pvalue", self.phase_c_ks_pvalue)
        if self.phase_a_max_residual < 0.0:
            raise SDEParameterError(
                f"phase_a_max_residual must be >= 0; got {self.phase_a_max_residual!r}"
            )
        if self.phase_b_mean_rel_err < 0.0:
            raise SDEParameterError(
                f"phase_b_mean_rel_err must be >= 0; got {self.phase_b_mean_rel_err!r}"
            )
        if self.phase_b_var_rel_err < 0.0:
            raise SDEParameterError(
                f"phase_b_var_rel_err must be >= 0; got {self.phase_b_var_rel_err!r}"
            )
        if not (0.0 <= self.phase_c_ks_pvalue <= 1.0):
            raise SDEParameterError(
                "phase_c_ks_pvalue must lie in [0.0, 1.0]; "
                f"got {self.phase_c_ks_pvalue!r}"
            )
        if isinstance(self.phase_c_n_paths, bool) or not isinstance(
            self.phase_c_n_paths, int
        ):
            raise SDEParameterError(
                f"phase_c_n_paths must be an int (not bool); "
                f"got {type(self.phase_c_n_paths)!r}"
            )
        if self.phase_c_n_paths < 0:
            raise SDEParameterError(
                f"phase_c_n_paths must be >= 0; got {self.phase_c_n_paths!r}"
            )
        if not isinstance(self.tex_anchor, str):
            raise SDEParameterError(
                f"tex_anchor must be a str; got {type(self.tex_anchor)!r}"
            )
        if len(self.tex_anchor) == 0:
            raise SDEParameterError("tex_anchor must be a non-empty str")
        if not isinstance(self.audit_block, str):
            raise SDEParameterError(
                f"audit_block must be a str; got {type(self.audit_block)!r}"
            )
        if _AUDIT_BLOCK_REGEX.fullmatch(self.audit_block) is None:
            raise SDEParameterError(
                "audit_block must match ^[0-9a-f]{64}$; "
                f"got {self.audit_block!r}"
            )


__all__ = [
    "CANONICAL_GBM",
    "CANONICAL_MERTON",
    "CANONICAL_OU",
    "GBMParameters",
    "InversionVerdict",
    "JumpDiffusionParameters",
    "OUParameters",
    "PathEnsemble",
]
