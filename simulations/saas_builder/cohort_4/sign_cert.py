"""Sign-verdict sidecar Markdown emission (plan v0.2 Pin M3 + Task 2.4).

Per Pin M3 (plan v0.2): the 5-TP sign verdicts are NOT first-class fields
on the shipped ``ZCapPinned`` Value (additive schema bump deferred). This
module renders the per-TP verdicts as a sidecar
``Z_cap_pinned.SIGN_VERDICTS.md`` artifact. NO IO here — this module
produces the Markdown string; ``cohort_4.io.SignVerdictSidecarWriter``
performs the file write at the IO Boundary.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from simulations.saas_builder.cohort_4.types import (
    NUMERICAL_IDENTITY_TOL,
    SignVerdict,
    TestPoint,
)


@dataclass(frozen=True)
class SignVerdictMarkdownRenderer:
    """Render the per-TP sign-verdict table to Markdown (Callable tier).

    Layout (plan v0.3 Pin M3 sidecar):

    - Header citing plan + spec.
    - Per-TP table: label, κ, X̄/Ȳ, σ₀, Z_mean, CI_lo, CI_hi, sign-pass,
      identity-residual, identity-pass, rationale.
    - Monotonicity row: ``|π|_TP4 > |π|_TP1 > |π|_TP5`` verdict
      (CORRECTIONS-α v0.3: replaced v0.2's TP2/TP1/TP3 κ-chain with
      the (X̄/Ȳ)-chain since κ ∉ free_symbols(π) under the honest
      derivation).
    - Audit-block citation (foreign-key into ``Z_cap_pinned.json``).
    """

    def __call__(
        self,
        sign_verdicts: Sequence[SignVerdict],
        test_points: Sequence[TestPoint],
        monotonicity_triple: tuple[float, float, float],
        audit_block: str,
    ) -> str:
        """Return the rendered Markdown body."""
        if len(sign_verdicts) != len(test_points):
            raise ValueError(
                "SignVerdictMarkdownRenderer: len(sign_verdicts) ="
                f" {len(sign_verdicts)} must equal len(test_points) ="
                f" {len(test_points)}"
            )
        by_label_tp = {tp.label: tp for tp in test_points}
        for sv in sign_verdicts:
            if sv.label not in by_label_tp:
                raise ValueError(
                    f"SignVerdictMarkdownRenderer: SignVerdict.label"
                    f" {sv.label!r} not in TestPoint set"
                )

        lines: list[str] = [
            "# SAAS-COHORT-4 — Z_cap_pinned Sign Verdicts (Pin M2 Sidecar)",
            "",
            "Plan: docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md (v0.3)",
            "Spec: docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md (v1.1.1)",
            "Foreign-key (audit_block): " + f"`{audit_block}`",
            "",
            "## Per-test-point sign verdicts",
            "",
            (
                "| Label | κ (tok/mo) | X̄/Ȳ | σ₀ |"
                " Ẑ | CI 95% lo | CI 95% hi |"
                " sign PASS | identity residual | identity PASS |"
                " rationale |"
            ),
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for sv in sign_verdicts:
            tp = by_label_tp[sv.label]
            lines.append(
                f"| {sv.label}"
                f" | {tp.kappa:.4e}"
                f" | {tp.x_over_y_bar:.4e}"
                f" | {tp.sigma_0:.4e}"
                f" | {sv.z_value:+.6e}"
                f" | {sv.ci_95_lo:+.6e}"
                f" | {sv.ci_95_hi:+.6e}"
                f" | {'YES' if sv.passes else 'NO'}"
                f" | {sv.identity_residual:.3e}"
                f" | {'YES' if sv.identity_passes else 'NO'}"
                f" | {tp.rationale} |"
            )
        lines.extend([
            "",
            "## Pin M2 monotonicity check",
            "",
            "Plan v0.3 §M2-fix (CORRECTIONS-α anti-fishing): "
            "``∂|π|/∂(X̄/Ȳ) > 0`` strict; equivalent chain"
            " ``|π|_TP4 > |π|_TP1 > |π|_TP5`` (FX brackets 4200/4000/3800).",
            "",
            "Note: v0.2's ``∂|π|/∂κ < 0`` chain was structurally"
            " unsatisfiable since κ ∉ free_symbols(π) under the honest"
            " PRIMITIVES.md §6→§8.1→§10→§15 derivation; the v0.2 1/κ"
            " coupling was a post-hoc fit (anti-fishing violation).",
            "",
            f"- |π|_TP4 = {monotonicity_triple[0]:.6e}",
            f"- |π|_TP1 = {monotonicity_triple[1]:.6e}",
            f"- |π|_TP5 = {monotonicity_triple[2]:.6e}",
            (
                "- verdict: "
                + (
                    "PASS"
                    if (
                        monotonicity_triple[0]
                        > monotonicity_triple[1]
                        > monotonicity_triple[2]
                    )
                    else "FAIL"
                )
            ),
            "",
            "## Identity-tolerance gate",
            "",
            f"Numerical tolerance ceiling: ``{NUMERICAL_IDENTITY_TOL:.0e}``"
            " (Path A v0 §10.4 inheritance).",
            "",
            "## Anti-fishing posture",
            "",
            "Per plan v0.2 anti-fishing posture: 5-test-point grid + sign"
            " expectations are pre-pinned and immutable; ANY violation"
            " fires HALT per `feedback_pathological_halt_anti_fishing_checkpoint`.",
            "",
        ])
        return "\n".join(lines) + "\n"


__all__ = [
    "SignVerdictMarkdownRenderer",
]
