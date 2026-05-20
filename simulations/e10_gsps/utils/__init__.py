"""E10 GSPS — IO Boundary tier (the only tier where mutable state lives).

Per plan v0.2 Phase 0 and CLAUDE.md ``simulations/`` discipline. This
tier MAY import from ``..types`` for return-shape contracts but NOT from
``..modules``.

Phase 0 holds no IO-boundary code. The per-currency central-bank FX
ingest (plan task 1.1), the x402 price probe (plan task 1.3), the
Tier-1 parquet emit/read, and the frozen-snapshot manager (plan task
3.4) land in Phases 1-3.
"""

__all__: list[str] = []
