"""Value-tier containers for SAAS-COHORT-3 Υ_t form selection.

All Value types are ``@dataclass(frozen=True)`` with ``__post_init__``
validation only. Free-function accessors live in this same module.

Pin coverage:

- Pin R1: ``RevenueFormName`` Literal-typed; ``MartingaleParams`` /
  ``Ar1LogParams`` / ``DetChurnParams`` carry per-form parameters with
  spec §5 brackets enforced.
- Pin R3: ``VerdictLabel`` Literal in {PASS, MARGINAL, INDISTINGUISHABLE,
  WEAK, FAIL}.
- Pin R4 / R4-bis: ``RevenueFormFit.gates_passed`` and
  ``RevenueFormFit.rho_boundary_mass`` (None for non-AR(1) forms).
- Pin R5: ``UpsilonPanel`` panel of (month, simulation_id, upsilon_cop,
  cohort_id) with ≥ 1 cohort and ≥ 24 months.
- Pin R5: ``LooComparisonResult`` mirrors ``arviz.compare`` columns;
  ``VerdictRouting`` carries the JSON emit shape.
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

import numpy as np
from numpy.typing import NDArray

# ─── Module-level constants ───────────────────────────────────────────────────

#: Pin R1 — closed candidate set.
REVENUE_FORM_NAMES: Final[tuple[str, str, str]] = (
    "martingale",
    "ar1_log",
    "det_churn",
)

#: Pin R5 — minimum panel month count for any Υ_t fit.
UPSILON_PANEL_MIN_MONTHS: Final[int] = 24

#: Pin R1 — AR(1) stationarity bracket (open).
AR1_RHO_LOWER: Final[float] = -1.0
AR1_RHO_UPPER: Final[float] = 1.0

#: Pin R1 — det+churn growth bracket (sanity).
DET_CHURN_G_LOWER: Final[float] = -0.5
DET_CHURN_G_UPPER: Final[float] = 5.0

#: Pin R4-bis — ρ boundary-mass thresholds.
RHO_BOUNDARY_MASS_CLEAN_MAX: Final[float] = 0.05
RHO_BOUNDARY_MASS_WEAK_MAX: Final[float] = 0.20
RHO_BOUNDARY_TAIL_THRESHOLD: Final[float] = 0.95

#: Audit-block sha256 hex regex.
_AUDIT_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")


# ─── Type aliases ─────────────────────────────────────────────────────────────

#: Pin R1 — closed Literal of allowed form names.
RevenueFormName: TypeAlias = Literal["martingale", "ar1_log", "det_churn"]

#: Pin R3 — verdict-router output Literal.
VerdictLabel: TypeAlias = Literal[
    "PASS", "MARGINAL", "INDISTINGUISHABLE", "WEAK", "FAIL"
]

#: Pin R3 — cross-validation method label.
CvMethod: TypeAlias = Literal["loo", "lfo"]


# ─── Value types — per-form parameter containers (Pin R1) ─────────────────────


@dataclass(frozen=True)
class MartingaleParams:
    """Martingale form parameters: Υ_t = Υ_{t-1} + ε_t.

    Validation contract:

    - ``sigma_epsilon`` finite and > 0.
    """

    sigma_epsilon: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.sigma_epsilon) and self.sigma_epsilon > 0.0):
            raise ValueError(
                f"MartingaleParams.sigma_epsilon = {self.sigma_epsilon}"
                f" must be a finite float > 0"
            )


@dataclass(frozen=True)
class Ar1LogParams:
    """AR(1)-log form parameters: log Υ_t = ρ log Υ_{t-1} + ε_t, |ρ| < 1.

    Validation contract:

    - ``-1 < rho < 1`` strict (stationarity).
    - ``sigma_epsilon`` finite and > 0.
    """

    rho: float
    sigma_epsilon: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.rho):
            raise ValueError(f"Ar1LogParams.rho = {self.rho} must be finite")
        if not (AR1_RHO_LOWER < self.rho < AR1_RHO_UPPER):
            raise ValueError(
                f"Ar1LogParams.rho = {self.rho} must satisfy"
                f" {AR1_RHO_LOWER} < rho < {AR1_RHO_UPPER} (stationarity)"
            )
        if not (math.isfinite(self.sigma_epsilon) and self.sigma_epsilon > 0.0):
            raise ValueError(
                f"Ar1LogParams.sigma_epsilon = {self.sigma_epsilon}"
                f" must be a finite float > 0"
            )


@dataclass(frozen=True)
class DetChurnParams:
    """Deterministic + churn form parameters: Υ_t = Υ_0·(1+g)^t · ∏(1-λ).

    Validation contract:

    - ``upsilon_0`` finite and > 0.
    - ``g`` finite and in ``[DET_CHURN_G_LOWER, DET_CHURN_G_UPPER]``.
    - ``lam`` finite and in ``(0, 1)`` (open) — Beta-prior support.
    """

    upsilon_0: float
    g: float
    lam: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.upsilon_0) and self.upsilon_0 > 0.0):
            raise ValueError(
                f"DetChurnParams.upsilon_0 = {self.upsilon_0}"
                f" must be a finite float > 0"
            )
        if not (math.isfinite(self.g) and DET_CHURN_G_LOWER <= self.g <= DET_CHURN_G_UPPER):
            raise ValueError(
                f"DetChurnParams.g = {self.g} must lie in"
                f" [{DET_CHURN_G_LOWER}, {DET_CHURN_G_UPPER}]"
            )
        if not (math.isfinite(self.lam) and 0.0 < self.lam < 1.0):
            raise ValueError(
                f"DetChurnParams.lam = {self.lam} must lie in (0, 1)"
            )


# ─── Value types — panel + fit + comparison + verdict ─────────────────────────


@dataclass(frozen=True)
class UpsilonPanel:
    """Cohort revenue panel — Pin R5 input contract.

    Columns (parallel arrays of equal length ``n_obs``):

    - ``month_index`` — int month index (≥ 0); strictly increasing within
      each (cohort_id, simulation_id) group.
    - ``simulation_id`` — string label per posterior simulation trajectory.
    - ``upsilon_cop`` — Υ_t in COP (positive float).
    - ``cohort_id`` — string label.

    Validation contract:

    - Arrays equal length ≥ 1.
    - At least one cohort (``len(set(cohort_id))`` ≥ 1).
    - ``unique_months_per_trajectory`` ≥ ``UPSILON_PANEL_MIN_MONTHS``
      (= 24) for at least one (cohort, simulation) trajectory.
    - All ``upsilon_cop`` finite and > 0.
    - All ``month_index`` ≥ 0.
    """

    month_index: NDArray[np.int64]
    simulation_id: tuple[str, ...]
    upsilon_cop: NDArray[np.float64]
    cohort_id: tuple[str, ...]

    def __post_init__(self) -> None:
        n = self.month_index.shape[0]
        if n < 1:
            raise ValueError("UpsilonPanel must have ≥ 1 row")
        if self.upsilon_cop.shape[0] != n:
            raise ValueError(
                f"UpsilonPanel.upsilon_cop length {self.upsilon_cop.shape[0]}"
                f" must equal month_index length {n}"
            )
        if len(self.simulation_id) != n:
            raise ValueError(
                f"UpsilonPanel.simulation_id length {len(self.simulation_id)}"
                f" must equal month_index length {n}"
            )
        if len(self.cohort_id) != n:
            raise ValueError(
                f"UpsilonPanel.cohort_id length {len(self.cohort_id)}"
                f" must equal month_index length {n}"
            )
        if not np.all(np.isfinite(self.upsilon_cop)):
            raise ValueError("UpsilonPanel.upsilon_cop contains non-finite values")
        if not np.all(self.upsilon_cop > 0.0):
            raise ValueError("UpsilonPanel.upsilon_cop must be strictly positive")
        if not np.all(self.month_index >= 0):
            raise ValueError("UpsilonPanel.month_index must be ≥ 0")
        # Trajectory length sanity: at least one (cohort, sim) trajectory has
        # ≥ UPSILON_PANEL_MIN_MONTHS unique months.
        max_traj_len = _max_trajectory_length(
            self.cohort_id, self.simulation_id, self.month_index
        )
        if max_traj_len < UPSILON_PANEL_MIN_MONTHS:
            raise ValueError(
                f"UpsilonPanel: longest trajectory has {max_traj_len} months;"
                f" Pin R5 requires ≥ {UPSILON_PANEL_MIN_MONTHS} for at least one"
                f" (cohort_id, simulation_id) group"
            )


def _max_trajectory_length(
    cohort_id: tuple[str, ...],
    simulation_id: tuple[str, ...],
    month_index: NDArray[np.int64],
) -> int:
    """Return max unique-month count over (cohort, sim) trajectories."""
    groups: dict[tuple[str, str], set[int]] = {}
    for c, s, m in zip(cohort_id, simulation_id, month_index.tolist()):
        groups.setdefault((c, s), set()).add(int(m))
    if not groups:
        return 0
    return max(len(months) for months in groups.values())


@dataclass(frozen=True)
class RevenueFormFit:
    """Per-form fit result — Pin R4 + R4-bis.

    Attributes:
        form_name: closed-set form Literal.
        idata_path: path to NetCDF InferenceData on disk (Pin R5).
        rhat_max: max r-hat across monitored params.
        ess_bulk_min: min ESS_bulk.
        ess_tail_min: min ESS_tail.
        n_chains: chain count (Pin R4: ≥ 4).
        n_draws_per_chain: per-chain draw count (Pin R4: ≥ 4000 floor →
            16000 total).
        pareto_k_max: max Pareto-k̂ over LOO observations.
        pareto_k_high_frac: fraction of LOO obs with k̂ ≥ 0.7.
        gates_passed: True iff all four Pin R4 conditions pass AND
            ``pareto_k_high_frac ≤ 0.05``.
        rho_boundary_mass: P(|ρ| > 0.95 | data) for AR(1)-log only;
            None for other forms (Pin R4-bis).
        cv_method: "loo" (default) or "lfo" (CORRECTIONS-α §15.3).
    """

    form_name: RevenueFormName
    idata_path: str
    rhat_max: float
    ess_bulk_min: float
    ess_tail_min: float
    n_chains: int
    n_draws_per_chain: int
    pareto_k_max: float
    pareto_k_high_frac: float
    gates_passed: bool
    rho_boundary_mass: float | None = None
    cv_method: CvMethod = "loo"

    def __post_init__(self) -> None:
        if self.form_name not in REVENUE_FORM_NAMES:
            raise ValueError(
                f"RevenueFormFit.form_name = {self.form_name!r}"
                f" must be one of {REVENUE_FORM_NAMES}"
            )
        for name, value in (
            ("rhat_max", self.rhat_max),
            ("ess_bulk_min", self.ess_bulk_min),
            ("ess_tail_min", self.ess_tail_min),
            ("pareto_k_max", self.pareto_k_max),
            ("pareto_k_high_frac", self.pareto_k_high_frac),
        ):
            if not math.isfinite(value):
                raise ValueError(f"RevenueFormFit.{name} = {value} must be finite")
            if value < 0.0:
                raise ValueError(f"RevenueFormFit.{name} = {value} must be ≥ 0")
        if not (0.0 <= self.pareto_k_high_frac <= 1.0):
            raise ValueError(
                f"RevenueFormFit.pareto_k_high_frac = {self.pareto_k_high_frac}"
                f" must lie in [0, 1]"
            )
        if self.n_chains <= 0:
            raise ValueError(
                f"RevenueFormFit.n_chains = {self.n_chains} must be > 0"
            )
        if self.n_draws_per_chain <= 0:
            raise ValueError(
                f"RevenueFormFit.n_draws_per_chain = {self.n_draws_per_chain}"
                f" must be > 0"
            )
        # rho_boundary_mass: Pin R4-bis — required-iff-AR(1)-log.
        if self.form_name == "ar1_log":
            if self.rho_boundary_mass is None:
                raise ValueError(
                    "RevenueFormFit: ar1_log requires non-None rho_boundary_mass"
                    " (Pin R4-bis)"
                )
            if not (math.isfinite(self.rho_boundary_mass)
                    and 0.0 <= self.rho_boundary_mass <= 1.0):
                raise ValueError(
                    f"RevenueFormFit.rho_boundary_mass = {self.rho_boundary_mass}"
                    f" must lie in [0, 1]"
                )
        else:
            if self.rho_boundary_mass is not None:
                raise ValueError(
                    f"RevenueFormFit.rho_boundary_mass must be None for"
                    f" form_name = {self.form_name!r} (Pin R4-bis)"
                )
        if self.cv_method not in ("loo", "lfo"):
            raise ValueError(
                f"RevenueFormFit.cv_method = {self.cv_method!r}"
                f" must be 'loo' or 'lfo'"
            )


@dataclass(frozen=True)
class LooComparisonResult:
    """Result of ``arviz.compare(..., ic='loo', method='stacking')``.

    Attributes:
        ranked_forms: form names in ``arviz.compare`` rank order (best first).
        elpd_loo: per-form ``elpd_loo`` (key = form name).
        elpd_diff: per-form ``elpd_diff`` (top form has 0).
        dse: per-form ``dse`` (SE of difference vs. top).
        weight: per-form ``weight`` (stacking weights, sum to 1).
        se: per-form ``se`` (SE of elpd_loo).
        warning: per-form warning flag (any arviz convergence warning).

    Validation contract:

    - ``ranked_forms`` length ∈ {1, 2, 3} (subset of REVENUE_FORM_NAMES).
    - Mappings have keys identical to ``ranked_forms``.
    - All values finite; ``weight`` ∈ [0, 1].
    - Top form has ``elpd_diff = 0.0``.
    - ``sum(weight.values())`` ∈ [1 - 1e-6, 1 + 1e-6].
    """

    ranked_forms: tuple[str, ...]
    elpd_loo: Mapping[str, float]
    elpd_diff: Mapping[str, float]
    dse: Mapping[str, float]
    weight: Mapping[str, float]
    se: Mapping[str, float]
    warning: Mapping[str, bool]

    def __post_init__(self) -> None:
        n = len(self.ranked_forms)
        if not (1 <= n <= 3):
            raise ValueError(
                f"LooComparisonResult.ranked_forms length {n} must be in {{1,2,3}}"
            )
        if len(set(self.ranked_forms)) != n:
            raise ValueError(
                f"LooComparisonResult.ranked_forms has duplicates:"
                f" {self.ranked_forms}"
            )
        for name in self.ranked_forms:
            if name not in REVENUE_FORM_NAMES:
                raise ValueError(
                    f"LooComparisonResult.ranked_forms contains {name!r}"
                    f" not in {REVENUE_FORM_NAMES}"
                )
        for fname, mapping in (
            ("elpd_loo", self.elpd_loo),
            ("elpd_diff", self.elpd_diff),
            ("dse", self.dse),
            ("weight", self.weight),
            ("se", self.se),
            ("warning", self.warning),
        ):
            if set(mapping.keys()) != set(self.ranked_forms):
                raise ValueError(
                    f"LooComparisonResult.{fname} keys {set(mapping.keys())}"
                    f" must equal ranked_forms {set(self.ranked_forms)}"
                )
        for fname, mapping in (
            ("elpd_loo", self.elpd_loo),
            ("elpd_diff", self.elpd_diff),
            ("dse", self.dse),
            ("weight", self.weight),
            ("se", self.se),
        ):
            for k, v in mapping.items():
                if not math.isfinite(v):
                    raise ValueError(
                        f"LooComparisonResult.{fname}[{k!r}] = {v} must be finite"
                    )
        for k, w in self.weight.items():
            if not (0.0 <= w <= 1.0 + 1e-9):
                raise ValueError(
                    f"LooComparisonResult.weight[{k!r}] = {w} must lie in [0, 1]"
                )
        weight_sum = sum(self.weight.values())
        if not math.isclose(weight_sum, 1.0, abs_tol=1e-6):
            raise ValueError(
                f"LooComparisonResult.weight sum = {weight_sum}"
                f" must be ≈ 1 (abs_tol=1e-6)"
            )
        # Top form (rank 0) must have elpd_diff = 0 by arviz.compare convention.
        top = self.ranked_forms[0]
        if not math.isclose(self.elpd_diff[top], 0.0, abs_tol=1e-9):
            raise ValueError(
                f"LooComparisonResult: top form {top!r} elpd_diff ="
                f" {self.elpd_diff[top]} must be 0 (arviz convention)"
            )


@dataclass(frozen=True)
class VerdictRouting:
    """Verdict-routing emission Value — Pin R3 + R5 JSON schema.

    Attributes:
        verdict: Pin R3 Literal in {PASS, MARGINAL, INDISTINGUISHABLE,
            WEAK, FAIL}.
        winning_form: top-ranked form name iff ``verdict ∈ {PASS, WEAK,
            MARGINAL}``; ``""`` (no winner declared) iff ``verdict ∈
            {INDISTINGUISHABLE, FAIL}`` per Pin R3 explicit-non-winner
            semantics (CORRECTIONS-α v0.3 §15.10 / CR-S5 / RC-FLAG-1).
        delta_elpd_loo: |elpd_loo[top] - elpd_loo[runner-up]|; 0 if
            single form.
        se: dse for the top-vs-runner-up comparison; 0 if single form.
        pareto_k_max_per_form: per-form max Pareto-k̂.
        weights_per_form: per-form stacking weight from arviz.compare.
        audit_block: 64-char lowercase sha256 hex string.
        fetched_at_utc: ISO-8601 UTC timestamp string.

    Validation contract:

    - ``verdict`` in the closed Literal.
    - ``winning_form`` empty iff ``verdict ∈ {INDISTINGUISHABLE, FAIL}``;
      otherwise (verdict ∈ {PASS, WEAK, MARGINAL}) must be in
      REVENUE_FORM_NAMES.
    - ``delta_elpd_loo ≥ 0`` and ``se ≥ 0``.
    - All keys in ``pareto_k_max_per_form`` / ``weights_per_form`` ⊆
      REVENUE_FORM_NAMES (allows partial — e.g. fewer than 3 if a fit
      crashed).
    - ``audit_block`` is exactly 64 lowercase hex chars.
    - ``fetched_at_utc`` non-empty.
    """

    verdict: VerdictLabel
    winning_form: str
    delta_elpd_loo: float
    se: float
    pareto_k_max_per_form: Mapping[str, float]
    weights_per_form: Mapping[str, float]
    audit_block: str
    fetched_at_utc: str

    def __post_init__(self) -> None:
        if self.verdict not in (
            "PASS", "MARGINAL", "INDISTINGUISHABLE", "WEAK", "FAIL",
        ):
            raise ValueError(
                f"VerdictRouting.verdict = {self.verdict!r} not a Pin R3 label"
            )
        if self.winning_form != "" and self.winning_form not in REVENUE_FORM_NAMES:
            raise ValueError(
                f"VerdictRouting.winning_form = {self.winning_form!r}"
                f" must be empty or in {REVENUE_FORM_NAMES}"
            )
        if not math.isfinite(self.delta_elpd_loo) or self.delta_elpd_loo < 0.0:
            raise ValueError(
                f"VerdictRouting.delta_elpd_loo = {self.delta_elpd_loo}"
                f" must be a finite float ≥ 0"
            )
        if not math.isfinite(self.se) or self.se < 0.0:
            raise ValueError(
                f"VerdictRouting.se = {self.se} must be a finite float ≥ 0"
            )
        for fname, mapping in (
            ("pareto_k_max_per_form", self.pareto_k_max_per_form),
            ("weights_per_form", self.weights_per_form),
        ):
            if not isinstance(mapping, Mapping):
                raise TypeError(
                    f"VerdictRouting.{fname} must be a Mapping"
                )
            for k, v in mapping.items():
                if k not in REVENUE_FORM_NAMES:
                    raise ValueError(
                        f"VerdictRouting.{fname} key {k!r}"
                        f" not in {REVENUE_FORM_NAMES}"
                    )
                if not math.isfinite(v):
                    raise ValueError(
                        f"VerdictRouting.{fname}[{k!r}] = {v} must be finite"
                    )
        if not _AUDIT_BLOCK_RE.fullmatch(self.audit_block):
            raise ValueError(
                f"VerdictRouting.audit_block must be 64 lowercase hex chars;"
                f" got {self.audit_block!r}"
            )
        if not self.fetched_at_utc:
            raise ValueError("VerdictRouting.fetched_at_utc must be non-empty")


# ─── Free-function accessors ──────────────────────────────────────────────────


def is_known_form(name: str) -> bool:
    """Return True iff ``name`` is one of the closed Pin R1 forms."""
    return name in REVENUE_FORM_NAMES


def n_obs(panel: UpsilonPanel) -> int:
    """Return number of observations in an UpsilonPanel."""
    return int(panel.month_index.shape[0])


__all__ = [
    "AR1_RHO_LOWER",
    "AR1_RHO_UPPER",
    "DET_CHURN_G_LOWER",
    "DET_CHURN_G_UPPER",
    "REVENUE_FORM_NAMES",
    "RHO_BOUNDARY_MASS_CLEAN_MAX",
    "RHO_BOUNDARY_MASS_WEAK_MAX",
    "RHO_BOUNDARY_TAIL_THRESHOLD",
    "UPSILON_PANEL_MIN_MONTHS",
    "Ar1LogParams",
    "CvMethod",
    "DetChurnParams",
    "LooComparisonResult",
    "MartingaleParams",
    "RevenueFormFit",
    "RevenueFormName",
    "UpsilonPanel",
    "VerdictLabel",
    "VerdictRouting",
    "is_known_form",
    "n_obs",
]
