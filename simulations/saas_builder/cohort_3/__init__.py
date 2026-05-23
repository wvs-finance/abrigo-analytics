"""SAAS-COHORT-3 — Υ_t (cohort revenue process) form selection via PSIS-LOO-CV.

Implements spec v1.1.1 §5 (Υ_t spec), §6 (functional-form table row Υ_t),
§7 (PSIS-LOO-CV via ``arviz.compare``), §9 (TODO-COHORT-3 verdict gate),
§10 (output artifact contract).

Three Υ_t candidate forms — CLOSED set per Pin R6 / spec §8(5):

1. **Martingale** — Υ_t = Υ_{t-1} + ε_t with ε_t ~ Normal(0, σ_ε).
2. **AR(1)-log** — log Υ_t = ρ log Υ_{t-1} + ε_t with |ρ| < 1.
3. **Deterministic + churn** — Υ_t = f(t)·S_t with f(t) = Υ_0·(1+g)^t and
   S_t = ∏(1 - λ).

Selection: ``arviz.compare(idata_dict, ic="loo", method="stacking")`` with
verdict-routing thresholds 4·SE (PASS) and 2·SE (INDISTINGUISHABLE). Pin R3
boundary semantics: INDISTINGUISHABLE iff |Δ|/SE ∈ [0, 2); MARGINAL iff
|Δ|/SE ∈ [2, 4] (closed both ends); PASS iff |Δ|/SE ∈ (4, ∞).

Three-tier discipline (functional-python skill):

- ``types.py`` / ``priors.py`` — Value tier (frozen-dc + ``__post_init__``).
- ``models.py`` / ``loo.py`` — Callable tier (frozen-dc + ``__call__``).
- ``io.py`` — IO Boundary tier (class with ``__init__``).
- ``_errors.py`` — typed cohort-local exceptions.
"""

from __future__ import annotations
