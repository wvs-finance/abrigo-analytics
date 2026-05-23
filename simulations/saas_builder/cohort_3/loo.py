"""LOO comparator + verdict router for SAAS-COHORT-3.

Implements spec §7 PSIS-LOO-CV via ``arviz.compare(model_dict, ic="loo",
method="stacking")`` and spec §9 verdict-routing thresholds (Pin R3).

Pin coverage:

- Pin R2: ``LooComparator`` invokes ``arviz.compare`` with ``ic="loo"`` and
  ``method="stacking"``; returns ``LooComparisonResult`` Value.
- Pin R3: ``VerdictRouter`` maps ratio = |Δelpd|/SE to:
    * INDISTINGUISHABLE iff ratio ∈ [0, 2)         (strict <)
    * MARGINAL          iff ratio ∈ [2, 4]         (closed both ends)
    * PASS              iff ratio ∈ (4, ∞)         (strict >)
  Edge: ratio = 2.0 → MARGINAL. ratio = 4.0 → MARGINAL.
- Pin R4 / R4-bis: gate failures and ρ boundary-mass downgrade per
  CORRECTIONS-α §15.4.
- Pin R6: thresholds 2·SE / 4·SE are ``Final`` constants — no parameter
  override path exists.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

import arviz as az

from simulations.saas_builder.cohort_3._errors import RhoBoundaryHaltError
from simulations.saas_builder.cohort_3.types import (
    REVENUE_FORM_NAMES,
    RHO_BOUNDARY_MASS_CLEAN_MAX,
    RHO_BOUNDARY_MASS_WEAK_MAX,
    LooComparisonResult,
    RevenueFormFit,
    VerdictLabel,
    VerdictRouting,
)

# ─── Pin R3 verdict thresholds — Final, no override ───────────────────────────

#: Pin R3 — strict-< threshold separating INDISTINGUISHABLE from MARGINAL.
INDISTINGUISHABLE_RATIO_MAX: Final[float] = 2.0

#: Pin R3 — strict-> threshold separating MARGINAL from PASS.
PASS_RATIO_MIN: Final[float] = 4.0


#: Pin R2 — closed Literal of allowed arviz.compare method names.
LooMethod: TypeAlias = Literal["stacking", "BB-pseudo-BMA", "pseudo-BMA"]


# ─── LooComparator (Pin R2) ────────────────────────────────────────────────────


@dataclass(frozen=True)
class LooComparator:
    """Compare per-form InferenceData via PSIS-LOO-CV.

    Spec §7 — PSIS-LOO-CV via ``arviz.compare(idata_dict, ic="loo",
    method="stacking")``. Returns a :class:`LooComparisonResult` Value.
    """

    method: LooMethod = "stacking"

    def __post_init__(self) -> None:
        if self.method not in ("stacking", "BB-pseudo-BMA", "pseudo-BMA"):
            raise ValueError(
                f"LooComparator.method = {self.method!r}"
                f" must be 'stacking', 'BB-pseudo-BMA', or 'pseudo-BMA'"
            )

    def __call__(
        self, idata_per_form: Mapping[str, az.InferenceData]
    ) -> LooComparisonResult:
        for k in idata_per_form:
            if k not in REVENUE_FORM_NAMES:
                raise ValueError(
                    f"LooComparator: form name {k!r} not in"
                    f" closed set {REVENUE_FORM_NAMES}"
                )
        if not idata_per_form:
            raise ValueError("LooComparator: idata_per_form must be non-empty")
        df = az.compare(dict(idata_per_form), ic="loo", method=self.method)
        # Sort by rank ascending to get the canonical arviz order.
        df_sorted = df.sort_values("rank")
        ranked_forms = tuple(str(idx) for idx in df_sorted.index)
        elpd_loo = {
            name: float(df_sorted.loc[name, "elpd_loo"])
            for name in ranked_forms
        }
        elpd_diff = {
            name: float(df_sorted.loc[name, "elpd_diff"])
            for name in ranked_forms
        }
        dse = {
            name: float(df_sorted.loc[name, "dse"])
            for name in ranked_forms
        }
        weight = {
            name: float(df_sorted.loc[name, "weight"])
            for name in ranked_forms
        }
        se = {
            name: float(df_sorted.loc[name, "se"])
            for name in ranked_forms
        }
        warning = {
            name: bool(df_sorted.loc[name, "warning"])
            for name in ranked_forms
        }
        # arviz.compare sometimes leaves elpd_diff for the top form as ~0 but
        # not exactly 0 (DataFrame coercion); pin to exactly 0 for top form.
        top = ranked_forms[0]
        elpd_diff[top] = 0.0
        # Normalize weight rounding to ensure sum ≈ 1 within validation
        # tolerance (1e-6 in LooComparisonResult.__post_init__).
        total = sum(weight.values())
        if total > 0.0:
            weight = {k: v / total for k, v in weight.items()}
        return LooComparisonResult(
            ranked_forms=ranked_forms,
            elpd_loo=elpd_loo,
            elpd_diff=elpd_diff,
            dse=dse,
            weight=weight,
            se=se,
            warning=warning,
        )


# ─── Verdict router (Pin R3 + R4 + R4-bis) ─────────────────────────────────────


def _classify_ratio(ratio: float) -> VerdictLabel:
    """Map |Δelpd|/SE ratio to {INDISTINGUISHABLE, MARGINAL, PASS}.

    Pin R3 boundary semantics (CORRECTIONS-α §15.2):

    - ratio ∈ [0, 2)         → INDISTINGUISHABLE
    - ratio ∈ [2, 4]         → MARGINAL  (closed both ends)
    - ratio ∈ (4, ∞)         → PASS

    Edge cases: ratio = 2.0 → MARGINAL. ratio = 4.0 → MARGINAL.

    Raises:
        ValueError: on non-finite or negative ``ratio``.
    """
    if not math.isfinite(ratio) or ratio < 0.0:
        raise ValueError(f"_classify_ratio: ratio = {ratio} must be finite ≥ 0")
    if ratio < INDISTINGUISHABLE_RATIO_MAX:
        return "INDISTINGUISHABLE"
    if ratio <= PASS_RATIO_MIN:
        return "MARGINAL"
    return "PASS"


@dataclass(frozen=True)
class VerdictRouter:
    """Map (LooComparisonResult + per-form fits) to a VerdictRouting Value.

    Spec §9 TODO-COHORT-3 row — Pin R3 verdict thresholds.

    Pin R4 / R4-bis routing precedence (most-failing first):

    1. If TOP form's ``gates_passed`` is False  → FAIL.
    2. If a non-top form's ``gates_passed`` is False  → WEAK on that form,
       but the verdict is still computed from the gate-pinned top form
       per the 4·SE / 2·SE comparison; if top is gate-clean and ratio is
       PASS-band, the overall verdict becomes WEAK (degraded from PASS).
    3. AR(1)-log boundary-mass routing (Pin R4-bis):
       - mass ≤ 0.05 → no action
       - 0.05 < mass ≤ 0.20 → AR(1)-log marked WEAK; if AR(1)-log was top,
         overall verdict downgraded to WEAK regardless of ratio band.
       - mass > 0.20 → :class:`RhoBoundaryHaltError` raised (HALT).
    4. Otherwise classify by ratio = |Δelpd_loo[top]−Δelpd_loo[runner-up]|
       / dse[runner-up] per Pin R3.
    """

    audit_block_default: str = "0" * 64
    fetched_at_utc_default: str = "1970-01-01T00:00:00Z"

    def __call__(
        self,
        comparison: LooComparisonResult,
        fits: Mapping[str, RevenueFormFit],
        audit_block: str | None = None,
        fetched_at_utc: str | None = None,
    ) -> VerdictRouting:
        ranked = comparison.ranked_forms
        top = ranked[0]
        # Per-form gate flags + Pareto k̂ statistics extracted from fits.
        pareto_k_max_per_form: dict[str, float] = {
            name: fits[name].pareto_k_max
            for name in ranked
            if name in fits
        }
        weights_per_form: dict[str, float] = dict(comparison.weight)

        # Pin R4-bis HALT — AR(1)-log boundary-mass > 0.20.
        if "ar1_log" in fits:
            ar1_fit = fits["ar1_log"]
            mass = ar1_fit.rho_boundary_mass
            if mass is not None and mass > RHO_BOUNDARY_MASS_WEAK_MAX:
                raise RhoBoundaryHaltError(
                    f"VerdictRouter: AR(1)-log P(|ρ|>0.95 | data) = {mass}"
                    f" exceeds Pin R4-bis HALT threshold {RHO_BOUNDARY_MASS_WEAK_MAX}"
                )

        # Compute ratio against runner-up (if any).
        # CORRECTIONS-α v0.3 §15.9 (CR-S1): explicit branch on se == 0 to
        # avoid the dse=0 → +inf → PASS misclassification. Two cases:
        #   (a) se == 0.0 ∧ delta_elpd == 0.0 → ratio = 0.0
        #       (legitimate ties under stacking; route to INDISTINGUISHABLE)
        #   (b) se == 0.0 ∧ delta_elpd != 0.0 → degenerate input from
        #       arviz.compare; raise ValueError (caller's data is ill-defined).
        if len(ranked) >= 2:
            runner_up = ranked[1]
            delta_elpd = abs(
                comparison.elpd_loo[top] - comparison.elpd_loo[runner_up]
            )
            se = comparison.dse[runner_up]
            if se == 0.0:
                if delta_elpd == 0.0:
                    ratio = 0.0
                else:
                    raise ValueError(
                        f"VerdictRouter: degenerate input from arviz.compare —"
                        f" dse[{runner_up!r}] = 0.0 but |Δelpd_loo| ="
                        f" {delta_elpd} ≠ 0; ratio is ill-defined. Refusing to"
                        f" classify (CORRECTIONS-α v0.3 §15.9 / CR-S1)."
                    )
            else:
                ratio = delta_elpd / se
        else:
            delta_elpd = 0.0
            se = 0.0
            ratio = 0.0  # single form → INDISTINGUISHABLE band

        # Gate-failure routing precedence (Pin R4).
        if top in fits and not fits[top].gates_passed:
            verdict: VerdictLabel = "FAIL"
            winning_form = ""
        else:
            non_top_gate_fail = any(
                name in fits and not fits[name].gates_passed
                for name in ranked[1:]
            )
            ar1_boundary_weak = False
            if "ar1_log" in fits:
                m = fits["ar1_log"].rho_boundary_mass
                if (m is not None
                        and RHO_BOUNDARY_MASS_CLEAN_MAX < m
                        <= RHO_BOUNDARY_MASS_WEAK_MAX):
                    ar1_boundary_weak = True

            if len(ranked) == 1:
                # Single form — INDISTINGUISHABLE by definition (no
                # comparison possible). Still PASS only if user supplies
                # a non-empty ranking with a positive ratio, which
                # cannot happen with one form.
                verdict = "INDISTINGUISHABLE"
            else:
                verdict = _classify_ratio(ratio)

            # Downgrades: non-top gate fail → WEAK; AR(1) boundary WEAK
            # downgrade if AR(1) is top.
            if non_top_gate_fail:
                verdict = "WEAK"
            if ar1_boundary_weak and top == "ar1_log":
                verdict = "WEAK"

            # CORRECTIONS-α v0.3 §15.10 (CR-S5 = RC-FLAG-1): only
            # verdicts in {PASS, WEAK, MARGINAL} declare a winning_form.
            # INDISTINGUISHABLE and FAIL declare NO winner (winning_form
            # = "") per Pin R3's "no winner declared" semantics. The
            # numerically-best form is still inspectable via
            # ``comparison.ranked_forms[0]``; verdict-router does NOT
            # advertise it on INDISTINGUISHABLE.
            if verdict in ("PASS", "WEAK", "MARGINAL"):
                winning_form = top
            else:
                # verdict ∈ {INDISTINGUISHABLE, FAIL} → no winner.
                winning_form = ""

        return VerdictRouting(
            verdict=verdict,
            winning_form=winning_form,
            delta_elpd_loo=delta_elpd,
            se=se,
            pareto_k_max_per_form=pareto_k_max_per_form,
            weights_per_form=weights_per_form,
            audit_block=audit_block or self.audit_block_default,
            fetched_at_utc=fetched_at_utc or self.fetched_at_utc_default,
        )


__all__ = [
    "INDISTINGUISHABLE_RATIO_MAX",
    "LooComparator",
    "PASS_RATIO_MIN",
    "VerdictRouter",
]
