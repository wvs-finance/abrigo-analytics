r"""SAAS-COHORT-2 — T2 softplus pricing fit + Δ^(a_s) sign certification.

Implements spec v1.1.1 §5.1 (T2), §5.2, §6, §9 (TODO-COHORT-2), §10 and
PRIMITIVES.md §6 / §7 / §8 — the cohort-2 sign-certification gate that
verifies $\Delta^{(a_s)} < 0$ strictly at every spec §5.2 bracket point on
the M5 single-mean / three-time-point FX path with TRM-pinned
$\overline{X/Y}$.

Pin coverage per plan v0.2:

- Pin M2 — softplus β tightness ``L¹ < 1e-3·κ`` enforced by shipped
  ``simulations.modules.regularizers.SoftplusRegularizer``;
  ``M2TightnessNotAchievedError`` raised when the fit grid is infeasible.
- Pin M2-fit — log-spaced grid ``β ∈ [0.01/κ, 100/κ]`` with 50 points;
  HALT (no silent grid widening) per anti-fishing.
- Pin Δ-cohort — PRIMITIVES.md §7 eq. (10) substituted with T2 ``q_t``
  per spec §5.1.
- Pin Γ-cohort — second derivative w.r.t. ``σ(X/Y)``; sign NOT pre-pinned
  (output, not gate input).
- Pin BRACKET-M5 — FX-path reconstruction at ``t ∈ {0, π/2, π}`` recovers
  ``(4200, 3800, 4200)`` around a single TRM-pinned mean; cross-references
  shipped ``simulations.tests.test_modules.TestM5FXPath``.
- Pin ROBUST-BS — bank-spread overlay sensitivity arm walled off from
  primary verdict (robustness file, not gate_verdict.json).

Three-tier discipline (functional-python skill):

- ``types.py`` — Value tier (frozen-dc + ``__post_init__``).
- ``pricing.py`` / ``derivatives.py`` / ``sign_cert.py`` /
  ``robustness.py`` — Callable tier (frozen-dc + ``__call__``).
- ``io.py`` — IO Boundary tier (class with ``__init__``).
- ``_errors.py`` — typed cohort-local exceptions.

Verdict alphabet (spec §10 line 520): ``PASS|WEAK|MARGINAL|FAIL|
INDISTINGUISHABLE``. HALT is a foreground/harness action — not a verdict
value emitted to gate_verdict.json.
"""

from __future__ import annotations
