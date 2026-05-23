r"""SAAS-COHORT-4 — π(t) symbolic derivation + Z-cap pin emission.

Implements plan v0.2 ``docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md``
+ spec v1.1.1 ``docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md``
§4.1, §5.2, §6, §9, §10. Final cohort sub-task for Stage-2.

Pin coverage:

- Pin M1 — ``pi_derivation.derive_pi_t_symbolic`` reproduces PRIMITIVES.md
  §6 (FX path) → §8.1 (Π = K⋆√σ_T) → §10 Carr-Madan → variance proxy →
  π(t) chain in sympy. Free-symbol arity ≤ 6 (RC-FLAG-3 ceiling).
- Pin M2 — ``z_cap.ZCapRunner`` evaluates 5 pre-pinned test points; sign
  expectation Z_cap > 0 ∀ TP. Monotonicity ``∂|π|/∂κ < 0`` strict.
- Pin M2-fix — MC error budget: stderr(Ẑ)/Ẑ ≤ 1e-3 with N_draws ≥ 4000.
- Pin M3 — ``io.pin_and_emit`` writes ``Z_cap_pinned.json`` via the
  shipped ``ZCapPinnedWriter``; sidecar ``Z_cap_pinned.SIGN_VERDICTS.md``
  carries per-TP sign verdicts (additive schema bump deferred to a
  future SIM-INFRA-0 v1.2 amendment per RC-FLAG-1).
- Pin M4 — ``io.AuditBlockResolver`` computes SHA-256 over the canonical
  5-file input set (C1 parquets + C2 ROBUSTNESS_RESULTS.md + C3 PRIMARY_
  RESULTS.md + spec); deterministic across runs with same inputs.

HALT routing (per ``feedback_pathological_halt_anti_fishing_checkpoint``):
sign violations → ``DiagnosticGateError``; identity-tolerance breach →
``IdentityToleranceError``; MC budget breach → ``MCErrorBudgetExceededError``;
audit-block drift → ``AuditBlockDriftError``.

Three-tier discipline (functional-python skill):

- ``types.py`` — Value tier (frozen-dc + ``__post_init__``).
- ``pi_derivation.py`` / ``z_cap.py`` / ``sign_cert.py`` — Callable tier
  (frozen-dc + ``__call__``).
- ``io.py`` — IO Boundary tier (class with ``__init__``).
- ``_errors.py`` — typed cohort-local exceptions.
"""

from __future__ import annotations

from simulations.saas_builder.cohort_4._errors import (
    AuditBlockDriftError,
    DiagnosticGateError,
    IdentityToleranceError,
    MCErrorBudgetExceededError,
)
from simulations.saas_builder.cohort_4.io import (
    AuditBlockResolver,
    SignVerdictSidecarWriter,
    assert_audit_block_unchanged,
    pin_and_emit,
)
from simulations.saas_builder.cohort_4.pi_derivation import (
    IdentityResidualEvaluator,
    derive_pi_t_symbolic,
)
from simulations.saas_builder.cohort_4.sign_cert import (
    SignVerdictMarkdownRenderer,
)
from simulations.saas_builder.cohort_4.types import (
    MCBudget,
    PiTSymbolic,
    SignVerdict,
    TestPoint,
    ZEvaluationResult,
    make_default_test_point_grid,
)
from simulations.saas_builder.cohort_4.z_cap import (
    PerDrawZEvaluator,
    SignCertifier,
    ZCapRunner,
    assert_pin_m2_monotonicity,
)

__all__ = [
    "AuditBlockDriftError",
    "AuditBlockResolver",
    "DiagnosticGateError",
    "IdentityResidualEvaluator",
    "IdentityToleranceError",
    "MCBudget",
    "MCErrorBudgetExceededError",
    "PerDrawZEvaluator",
    "PiTSymbolic",
    "SignCertifier",
    "SignVerdict",
    "SignVerdictMarkdownRenderer",
    "SignVerdictSidecarWriter",
    "TestPoint",
    "ZCapRunner",
    "ZEvaluationResult",
    "assert_audit_block_unchanged",
    "assert_pin_m2_monotonicity",
    "derive_pi_t_symbolic",
    "make_default_test_point_grid",
    "pin_and_emit",
]
