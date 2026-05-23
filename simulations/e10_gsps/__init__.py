"""E10 — GSPS v0.4: Convex Multi-Currency Data-Consumption FX-Volatility Hedge.

Three-tier (Value / Callable / IO Boundary) sub-package per CLAUDE.md
``simulations/`` discipline and the ``functional-python`` skill.

Sub-tier layout (per plan v0.2 Phase 0.1 / 0.3):

- ``types/``    — frozen-dataclass parameter containers + Protocols
                  (per-currency daily FX row; monthly realized-log-variance
                  cell; NHPP intensity-parameter container with five lambda(t)
                  modulation-form slots; per-(currency,month) cost-stream
                  trajectory; three-way decomposition result; surface-grid
                  result; descriptive-verdict result). NO logic.
- ``modules/``  — stateless callable transforms (panel-currency + regime-break
                  screen; R6 NHPP simulation engine; exact three-way
                  log-variance decomposition; surface-grid evaluator;
                  descriptive-verdict classifier; anti-fishing checks).
                  frozen-dc + __call__ Protocols. NO mutable state.
- ``utils/``    — IO Boundary tier (per-currency central-bank FX ingest,
                  x402 price probe, Tier-1 parquet emit/read, frozen-snapshot
                  manager). All mutable state is confined HERE.
- ``tests/``    — pytest + Hypothesis strategies + math-pin verification.

Tier-import discipline (NON-NEGOTIABLE):

- ``types/`` does NOT import from ``modules/`` or ``utils/``.
- ``modules/`` does NOT import from ``utils/``.
- ``utils/`` MAY import from ``types/`` (for return-shape contracts) but
  not from ``modules/``.

Posture (plan v0.2 §5, spec v0.4 §7 field 5 / §9): E10 v0.4 is a
**descriptive / illustrative** iteration. It makes NO inferential beta
claim. The deliverable is the FX-variance-share sensitivity surface — a
description, not a verdict point. The descriptive-posture firewall
(Phase 0.13) enforces this mechanically.

Stage discipline (spec v0.4 §13): Stage-1 measurement (this sub-package)
is firewalled from Stage-2 M-design. Stage-2 fitted-payoff / Panoptic-
sizing language is mechanically rejected from main-line code by the
Stage-2 firewall (Phase 0.11) outside the explicitly tagged spec-§13
M-sketch docstrings.
"""

__all__: list[str] = []
