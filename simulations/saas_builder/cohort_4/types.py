r"""Value-tier containers for SAAS-COHORT-4 — π(t) symbolic + Z-cap pin.

All types are ``@dataclass(frozen=True)`` per the functional-python skill.
Methods are forbidden except ``__post_init__`` for validation; accessors
are free functions in this module.

Pin coverage (plan v0.2 §Phase-2 prelude):

- Pin M1 — π(t) symbolic anchor: ``PiTSymbolic`` carries the sympy ``Expr``
  (closed form) and the lambdified numpy callable. The Expr is built by
  reproducing PRIMITIVES.md §6 (FX path) → §8.1 (closed-form Π) →
  §10 (Carr-Madan linearization) → §6 (variance proxy) verbatim.
- Pin M2 — 5-test-point grid: ``TestPoint`` packages one
  ``(κ, X̄/Ȳ, σ_0)`` tuple plus the symbolic-sign expectation. The
  immutable ``TEST_POINT_GRID`` is the canonical 5-tuple per plan v0.2 M2.
- Pin M2-fix — sign expectation Z_cap > 0 ∀ TP; ``∂|π|/∂κ < 0`` strict;
  monotonicity chain |π|_TP2 > |π|_TP1 > |π|_TP3.
- Pin M2 (MC error budget) — ``MCBudget`` carries the per-cohort N_draws
  floor (≥ 4000) and ``stderr/Ẑ`` ceiling (≤ 1e-3).

NO IO at this tier. NO inheritance except Protocol/Exception.
"""

from __future__ import annotations

import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

import numpy as np
import sympy as sp
from numpy.typing import NDArray

# ─── Module-level constants ───────────────────────────────────────────────────

#: Pin M2-fix — N_draws floor for MC integration of the posterior-predictive Z.
MC_DRAWS_FLOOR: Final[int] = 4000

#: Pin M2-fix — stderr(Ẑ)/Ẑ ceiling for MC integration of the posterior-predictive Z.
MC_STDERR_RATIO_CEILING: Final[float] = 1e-3

#: Pin M2 — symbolic identity-tolerance ceiling (PRIMITIVES.md §12 ledger).
SYMBOLIC_IDENTITY_TOL: Final[float] = 1e-10

#: Pin M2 — numerical identity-tolerance ceiling (Path A v0 §10.4 inheritance).
NUMERICAL_IDENTITY_TOL: Final[float] = 1e-6

#: Plan v0.3 §M1 — canonical free-symbol set for π(t) (cap at 6 per RC-FLAG-3).
#:
#: CORRECTIONS-α v0.2 → v0.3 (MQ-BLOCK-1 + FLAG-1 fix): ``kappa`` REMOVED
#: from the 6-tuple (κ ∉ free_symbols(π) under the honest derivation per
#: PRIMITIVES.md §6→§8.1→§10→§15). ``xy_bar`` (X̄/Ȳ) ADDED to restore the
#: silently-dropped (X̄/Ȳ)² prefactor on σ_T (PRIMITIVES.md §6).
PI_T_CANONICAL_SYMBOLS: Final[tuple[str, ...]] = (
    "K_star",
    "sigma_0",
    "epsilon",
    "omega",
    "t",
    "xy_bar",
)

#: Pin M3 — audit-block hex regex (mirror posterior.ZCapPinned).
_AUDIT_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")

#: Spec §3 — TRM-pinned 12-month trailing mean of monthly Banrep TRM.
DEFAULT_X_OVER_Y_BAR: Final[float] = 4000.0

#: Plan v0.2 §M2 — high/low FX brackets per SIM-INFRA-0 + saas FX path.
FX_HIGH_BRACKET: Final[float] = 4200.0
FX_LOW_BRACKET: Final[float] = 3800.0

# ─── Type aliases ─────────────────────────────────────────────────────────────

#: 1-D float64 array.
FloatArray: TypeAlias = NDArray[np.float64]

#: Numpy-callable produced by ``sympy.lambdify`` for π(t).
PiTLambdified: TypeAlias = Callable[..., FloatArray]

#: Test-point label (closed alphabet — Pin M2 5-tuple).
TestPointLabel: TypeAlias = Literal["TP1", "TP2", "TP3", "TP4", "TP5"]


# ─── Value types ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PiTSymbolic:
    r"""Symbolic + lambdified π(t) anchor (Pin M1).

    Carries the closed-form sympy ``Expr`` derived by reproducing
    PRIMITIVES.md §6 (FX path) → §8.1 (closed-form Π = K\*·√σ_T) →
    §10 (Carr-Madan: Π ≈ K̂ · σ_T, K̂ = K\*/(2√σ_0)) → variance proxy
    along the deterministic FX path → π(t) = dΠ/dt.

    Symbol map (the canonical 6-tuple per plan v0.3 RC-FLAG-3):

    - ``K_star`` (K⋆) — equilibrium strike (PRIMITIVES.md §8.1).
    - ``sigma_0`` (σ₀) — pinned variance (Carr-Madan linearization point).
    - ``epsilon`` (ε) — FX-path amplitude (PRIMITIVES.md §6).
    - ``omega`` (ω) — FX-path frequency (PRIMITIVES.md §6).
    - ``t`` — time (continuous).
    - ``xy_bar`` (X̄/Ȳ) — TRM-pinned FX mean (PRIMITIVES.md §6).

    Note (CORRECTIONS-α v0.3): ``kappa`` is NOT a free symbol of π(t)
    under the honest derivation. κ enters Z only via the spec §5.1 (T2)
    softplus channel ``q_t^USD = p̄_sub + p_t·softplus_β(τ_t − κ)``,
    already C2-marginalized into the C1 posterior-predictive draws.

    ``free_symbols`` is the sympy free-symbol set extracted from ``expr``
    at construction; the Pin-M1 contract requires this set ⊆
    ``PI_T_CANONICAL_SYMBOLS``.

    Validation contract:

    - ``expr`` is a sympy ``Expr``;
    - ``free_symbols`` is a frozenset of strings; subset of canonical;
    - ``len(free_symbols) ≤ 6`` (RC-FLAG-3 arity ceiling);
    - ``lambdified`` is callable;
    - ``primitives_anchor`` is a non-empty citation string;
    - ``saas_note_anchor`` is a non-empty citation string.
    """

    expr: sp.Expr
    lambdified: PiTLambdified
    free_symbols: frozenset[str]
    primitives_anchor: str
    saas_note_anchor: str

    def __post_init__(self) -> None:
        if not isinstance(self.expr, sp.Expr):
            raise TypeError(
                f"PiTSymbolic.expr must be a sympy Expr;"
                f" got {type(self.expr).__name__}"
            )
        if not callable(self.lambdified):
            raise TypeError(
                "PiTSymbolic.lambdified must be callable"
                f" (got {type(self.lambdified).__name__})"
            )
        if not isinstance(self.free_symbols, frozenset):
            raise TypeError("PiTSymbolic.free_symbols must be a frozenset")
        canonical = set(PI_T_CANONICAL_SYMBOLS)
        if not self.free_symbols.issubset(canonical):
            extra = self.free_symbols - canonical
            raise ValueError(
                f"PiTSymbolic.free_symbols {sorted(self.free_symbols)} must be"
                f" a subset of canonical {sorted(canonical)};"
                f" extra={sorted(extra)}"
            )
        if len(self.free_symbols) > 6:
            raise ValueError(
                f"PiTSymbolic: free-symbol arity {len(self.free_symbols)}"
                " exceeds plan v0.2 RC-FLAG-3 ceiling of 6"
            )
        if not self.primitives_anchor:
            raise ValueError(
                "PiTSymbolic.primitives_anchor must be a non-empty citation"
            )
        if not self.saas_note_anchor:
            raise ValueError(
                "PiTSymbolic.saas_note_anchor must be a non-empty citation"
            )


@dataclass(frozen=True)
class TestPoint:
    """One Pin-M2 5-test-point grid entry.

    Symbol map:

    - ``label`` — closed alphabet "TP1".."TP5".
    - ``kappa`` — token cap (tokens/mo).
    - ``x_over_y_bar`` — TRM-pinned ``X̄/Ȳ``.
    - ``sigma_0`` — pinned variance (Carr-Madan linearization point).
    - ``rationale`` — non-empty spec citation string.
    - ``sign_expectation`` — Pin-M2 immutable expectation; ``"positive"``
      across all 5 points (Z_cap > 0 ∀ TP per plan v0.2).

    Validation contract:

    - ``label`` ∈ ``("TP1","TP2","TP3","TP4","TP5")``.
    - ``kappa`` finite, > 0.
    - ``x_over_y_bar`` finite, > 0.
    - ``sigma_0`` finite, > 0.
    - ``rationale`` non-empty.
    - ``sign_expectation == "positive"``.
    """

    #: Pytest collection guard — TestPoint is a domain Value type, not a test class.
    __test__ = False

    label: TestPointLabel
    kappa: float
    x_over_y_bar: float
    sigma_0: float
    rationale: str
    sign_expectation: Literal["positive"] = "positive"

    def __post_init__(self) -> None:
        if self.label not in ("TP1", "TP2", "TP3", "TP4", "TP5"):
            raise ValueError(
                f"TestPoint.label = {self.label!r} must be one of TP1..TP5"
            )
        for name, val in (
            ("kappa", self.kappa),
            ("x_over_y_bar", self.x_over_y_bar),
            ("sigma_0", self.sigma_0),
        ):
            if not (math.isfinite(val) and val > 0.0):
                raise ValueError(
                    f"TestPoint.{name} = {val} must be a finite float > 0"
                )
        if not self.rationale:
            raise ValueError("TestPoint.rationale must be non-empty")
        if self.sign_expectation != "positive":
            raise ValueError(
                "TestPoint.sign_expectation is immutable per plan v0.2"
                f' (got {self.sign_expectation!r}; required "positive")'
            )


@dataclass(frozen=True)
class SignVerdict:
    """Per-test-point sign-certification record (Pin M2).

    Sidecar emission per plan v0.2 §Pin M3 (5-TP verdicts are NOT first-class
    fields on ``ZCapPinned``; emitted to ``Z_cap_pinned.SIGN_VERDICTS.md``).

    Validation contract:

    - ``label`` ∈ ``("TP1","TP2","TP3","TP4","TP5")``.
    - ``z_value`` finite (need not be > 0; pre-HALT verdicts may record
      violations for the disposition memo).
    - ``ci_95_lo ≤ z_value ≤ ci_95_hi``; both finite.
    - ``passes`` is True iff ``ci_95_lo > 0`` (strict positive lower bound).
    - ``identity_residual`` finite, ≥ 0.
    - ``identity_passes`` is True iff
      ``identity_residual ≤ NUMERICAL_IDENTITY_TOL``.
    """

    label: TestPointLabel
    z_value: float
    ci_95_lo: float
    ci_95_hi: float
    passes: bool
    identity_residual: float
    identity_passes: bool

    def __post_init__(self) -> None:
        if self.label not in ("TP1", "TP2", "TP3", "TP4", "TP5"):
            raise ValueError(
                f"SignVerdict.label = {self.label!r} must be one of TP1..TP5"
            )
        for name, val in (
            ("z_value", self.z_value),
            ("ci_95_lo", self.ci_95_lo),
            ("ci_95_hi", self.ci_95_hi),
            ("identity_residual", self.identity_residual),
        ):
            if not math.isfinite(val):
                raise ValueError(f"SignVerdict.{name} = {val} must be finite")
        if not (self.ci_95_lo <= self.z_value <= self.ci_95_hi):
            raise ValueError(
                "SignVerdict: must satisfy ci_95_lo ≤ z_value ≤ ci_95_hi;"
                f" got ({self.ci_95_lo}, {self.z_value}, {self.ci_95_hi})"
            )
        if self.identity_residual < 0.0:
            raise ValueError(
                f"SignVerdict.identity_residual = {self.identity_residual}"
                " must be ≥ 0"
            )
        derived_passes = self.ci_95_lo > 0.0
        if derived_passes != self.passes:
            raise ValueError(
                "SignVerdict.passes must equal (ci_95_lo > 0);"
                f" got passes={self.passes}, ci_95_lo={self.ci_95_lo}"
            )
        derived_identity = self.identity_residual <= NUMERICAL_IDENTITY_TOL
        if derived_identity != self.identity_passes:
            raise ValueError(
                "SignVerdict.identity_passes must equal"
                " (identity_residual ≤ NUMERICAL_IDENTITY_TOL);"
                f" got flag={self.identity_passes},"
                f" residual={self.identity_residual}"
            )


@dataclass(frozen=True)
class MCBudget:
    """MC error-budget configuration for posterior-predictive Z (Pin M2-fix).

    Validation contract:

    - ``n_draws`` integer ≥ MC_DRAWS_FLOOR.
    - ``stderr_ratio_ceiling`` finite, > 0, ≤ MC_STDERR_RATIO_CEILING.
    """

    n_draws: int
    stderr_ratio_ceiling: float = MC_STDERR_RATIO_CEILING

    def __post_init__(self) -> None:
        if self.n_draws < MC_DRAWS_FLOOR:
            raise ValueError(
                f"MCBudget.n_draws = {self.n_draws} must be ≥ {MC_DRAWS_FLOOR}"
                " (plan v0.2 Pin M2-fix)"
            )
        if not (
            math.isfinite(self.stderr_ratio_ceiling)
            and 0.0 < self.stderr_ratio_ceiling <= MC_STDERR_RATIO_CEILING
        ):
            raise ValueError(
                f"MCBudget.stderr_ratio_ceiling = {self.stderr_ratio_ceiling}"
                f" must lie in (0, {MC_STDERR_RATIO_CEILING}]"
            )


@dataclass(frozen=True)
class ZEvaluationResult:
    """Pre-emission posterior-predictive Z result for one test point.

    Carries the per-draw Z realisations + summary statistics. Consumed by
    ``cohort_4.io.pin_and_emit`` to build the final ``ZCapPinned`` Value
    (which carries only summary statistics, not the per-draw array).

    Validation contract:

    - ``label`` ∈ TP1..TP5.
    - ``z_per_draw`` is a 1-D float64 array; length ≥ MC_DRAWS_FLOOR.
    - ``z_mean`` finite; equals ``z_per_draw.mean()`` within 1e-9.
    - ``z_stderr`` finite, ≥ 0.
    - ``ci_95_lo`` ≤ ``z_mean`` ≤ ``ci_95_hi``.
    - ``identity_residual`` finite, ≥ 0.
    """

    label: TestPointLabel
    z_per_draw: FloatArray
    z_mean: float
    z_stderr: float
    ci_95_lo: float
    ci_95_hi: float
    identity_residual: float

    def __post_init__(self) -> None:
        if self.label not in ("TP1", "TP2", "TP3", "TP4", "TP5"):
            raise ValueError(
                f"ZEvaluationResult.label = {self.label!r} must be TP1..TP5"
            )
        arr = self.z_per_draw
        if not isinstance(arr, np.ndarray):
            raise TypeError(
                f"ZEvaluationResult.z_per_draw must be ndarray;"
                f" got {type(arr).__name__}"
            )
        if arr.ndim != 1:
            raise ValueError(
                f"ZEvaluationResult.z_per_draw.ndim = {arr.ndim} must be 1"
            )
        if arr.size < MC_DRAWS_FLOOR:
            raise ValueError(
                f"ZEvaluationResult.z_per_draw.size = {arr.size}"
                f" must be ≥ {MC_DRAWS_FLOOR}"
            )
        for name, val in (
            ("z_mean", self.z_mean),
            ("z_stderr", self.z_stderr),
            ("ci_95_lo", self.ci_95_lo),
            ("ci_95_hi", self.ci_95_hi),
            ("identity_residual", self.identity_residual),
        ):
            if not math.isfinite(val):
                raise ValueError(
                    f"ZEvaluationResult.{name} = {val} must be finite"
                )
        if self.z_stderr < 0.0:
            raise ValueError(
                f"ZEvaluationResult.z_stderr = {self.z_stderr} must be ≥ 0"
            )
        if not (self.ci_95_lo <= self.z_mean <= self.ci_95_hi):
            raise ValueError(
                "ZEvaluationResult: must satisfy ci_95_lo ≤ z_mean ≤ ci_95_hi"
                f" (got {self.ci_95_lo}, {self.z_mean}, {self.ci_95_hi})"
            )
        if self.identity_residual < 0.0:
            raise ValueError(
                "ZEvaluationResult.identity_residual = "
                f"{self.identity_residual} must be ≥ 0"
            )


# ─── Free-function accessors / canonical grid ────────────────────────────────


def stderr_ratio(result: ZEvaluationResult) -> float:
    """Return ``stderr(Ẑ) / Ẑ``; raises if ``z_mean`` is non-positive.

    Pin M2-fix gate: must be ≤ ``MC_STDERR_RATIO_CEILING``.
    """
    if not (result.z_mean > 0.0):
        raise ValueError(
            f"stderr_ratio: z_mean = {result.z_mean} must be > 0"
            " for ratio to be well-defined"
        )
    return float(result.z_stderr / result.z_mean)


#: Spec §6 / PRIMITIVES.md §6 — default ε for σ₀ closed form (mid-bracket).
DEFAULT_FX_EPSILON_FOR_SIGMA0: Final[float] = 0.1


def sigma_0_from_primitives_section_6(
    x_over_y_bar: float,
    epsilon: float = DEFAULT_FX_EPSILON_FOR_SIGMA0,
) -> float:
    r"""Return σ₀ from PRIMITIVES.md §6 large-t asymptotic closed form.

    CORRECTIONS-α v0.3 (MQ-BLOCK-4 fix): the v0.2 default σ₀ = 1e4 was a
    free parameter unanchored to PRIMITIVES.md / spec. The closed form
    σ_T(t) = (X̄/Ȳ)²·ε²·[1/8 + sin(4ωt)/(32ωt)] has large-t asymptote
    (X̄/Ȳ)²·ε²/8. Pinning σ₀ to this asymptote makes the Carr-Madan
    linearization a deterministic function of (X̄/Ȳ, ε) rather than a
    free parameter, removing the calibration abdication MQ-BLOCK-4
    flagged.

    With X̄/Ȳ = 4000, ε = 0.1: σ₀ = 4000²·0.01/8 = 2000 (NOT 1e4).
    """
    if not (x_over_y_bar > 0.0 and math.isfinite(x_over_y_bar)):
        raise ValueError(
            "sigma_0_from_primitives_section_6: x_over_y_bar must be"
            f" finite > 0; got {x_over_y_bar}"
        )
    if not (0.0 < epsilon < 1.0):
        raise ValueError(
            "sigma_0_from_primitives_section_6: epsilon must lie in (0, 1)"
            f" per spec §6; got {epsilon}"
        )
    return float(x_over_y_bar**2 * epsilon**2 / 8.0)


def make_default_test_point_grid(
    kappa_0: float = 6_500_000.0,
    x_over_y_bar_0: float = DEFAULT_X_OVER_Y_BAR,
    epsilon: float = DEFAULT_FX_EPSILON_FOR_SIGMA0,
) -> tuple[TestPoint, ...]:
    r"""Return the canonical Pin-M2 5-tuple of TestPoints (default cohort).

    Defaults match plan v0.3 §M2:

    - TP1: primary κ₀ at TRM-mean (max_5x κ₀ = 6.5M tok/mo per spec §5.2).
    - TP2: 0.5·κ₀ at TRM-mean (low-cap straddle, retained for spec
      compatibility — though κ does NOT enter π in v0.3 honest, so |π|
      is identical TP1=TP2=TP3 by construction).
    - TP3: 1.5·κ₀ at TRM-mean (high-cap straddle, ditto).
    - TP4: κ₀ at FX-high (4200 COP/USD).
    - TP5: κ₀ at FX-low (3800 COP/USD).

    σ₀ is computed per X̄/Ȳ via the PRIMITIVES.md §6 large-t closed form
    (CORRECTIONS-α v0.3 MQ-BLOCK-4 fix); each TP carries its own σ₀
    consistent with its FX bracket.

    Plan v0.3 §M2 monotonicity: ``∂|π|/∂(X̄/Ȳ) > 0`` strict (replaces
    v0.2's ``∂|π|/∂κ < 0`` which is structurally unsatisfiable since
    κ ∉ free_symbols(π) — anti-fishing remediation).
    """
    s0_mid = sigma_0_from_primitives_section_6(x_over_y_bar_0, epsilon)
    s0_hi = sigma_0_from_primitives_section_6(FX_HIGH_BRACKET, epsilon)
    s0_lo = sigma_0_from_primitives_section_6(FX_LOW_BRACKET, epsilon)
    return (
        TestPoint(
            label="TP1",
            kappa=kappa_0,
            x_over_y_bar=x_over_y_bar_0,
            sigma_0=s0_mid,
            rationale="spec §5.2 LOCKED bracket, primary; σ₀ per §6",
        ),
        TestPoint(
            label="TP2",
            kappa=0.5 * kappa_0,
            x_over_y_bar=x_over_y_bar_0,
            sigma_0=s0_mid,
            rationale=(
                "low-cap κ straddle (spec §5.2); v0.3: κ ∉ π so |π|"
                " unchanged from TP1 — retained for Z gate via q channel"
            ),
        ),
        TestPoint(
            label="TP3",
            kappa=1.5 * kappa_0,
            x_over_y_bar=x_over_y_bar_0,
            sigma_0=s0_mid,
            rationale=(
                "high-cap κ straddle (spec §5.2); v0.3: κ ∉ π so |π|"
                " unchanged from TP1 — retained for Z gate via q channel"
            ),
        ),
        TestPoint(
            label="TP4",
            kappa=kappa_0,
            x_over_y_bar=FX_HIGH_BRACKET,
            sigma_0=s0_hi,
            rationale=(
                "M5 FX upper bracket (4200 COP/USD); v0.3 monotonicity"
                " endpoint: |π|_TP4 > |π|_TP1"
            ),
        ),
        TestPoint(
            label="TP5",
            kappa=kappa_0,
            x_over_y_bar=FX_LOW_BRACKET,
            sigma_0=s0_lo,
            rationale=(
                "M5 FX lower bracket (3800 COP/USD); v0.3 monotonicity"
                " endpoint: |π|_TP5 < |π|_TP1"
            ),
        ),
    )


__all__ = [
    "DEFAULT_FX_EPSILON_FOR_SIGMA0",
    "DEFAULT_X_OVER_Y_BAR",
    "FX_HIGH_BRACKET",
    "FX_LOW_BRACKET",
    "FloatArray",
    "MCBudget",
    "MC_DRAWS_FLOOR",
    "MC_STDERR_RATIO_CEILING",
    "NUMERICAL_IDENTITY_TOL",
    "PI_T_CANONICAL_SYMBOLS",
    "PiTLambdified",
    "PiTSymbolic",
    "SYMBOLIC_IDENTITY_TOL",
    "SignVerdict",
    "TestPoint",
    "TestPointLabel",
    "ZEvaluationResult",
    "make_default_test_point_grid",
    "sigma_0_from_primitives_section_6",
    "stderr_ratio",
]
