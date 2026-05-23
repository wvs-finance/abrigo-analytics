"""dev_ai_cost_v2 typed errors.

Per functional-python skill: only Exception subclassing is admitted as
class-inheritance outside of Protocols. Parent spec
``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.1 §3.5
defines JSONLSchemaError as the schema-drift gate raised by
``simulations.dev_ai_cost_v2.jsonl_io.JSONLReader``.

Sibling spec ``docs/specs/2026-05-16-r6-continuous-stream-simulation-design.md``
v0.1.3 CORRECTIONS-AA introduces ``DevAICostError(Exception)`` as the
sub-package root, matching the ``simulations.stochastic_fx._errors``
convention. Future R6 errors (NHPPCalibrationError, SparsePoolError, etc.)
will inherit from DevAICostError.
"""
from __future__ import annotations

from simulations.utils.errors import SchemaMismatchError


class DevAICostError(Exception):
    """Base class for the dev_ai_cost_v2 sub-package.

    Matches the ``StochasticFXError`` convention from
    ``simulations.stochastic_fx._errors``. Catch this to capture any
    sub-package-typed error.
    """


class JSONLSchemaError(DevAICostError, SchemaMismatchError):
    """Raised by ``JSONLReader`` when an Anthropic JSONL row violates the
    pinned Pydantic schema (``extra="forbid"`` or missing required field).

    Multiple inheritance preserves backward compatibility:
    - ``except DevAICostError``: catches all sub-package errors (new pattern).
    - ``except SchemaMismatchError``: catches IO-boundary schema violations
      across the simulations package (existing pattern from ``utils.errors``).
    - ``except ValueError``: existing broad-catch handlers continue to work.

    MRO: JSONLSchemaError → DevAICostError → SchemaMismatchError → ValueError → Exception.
    """


__all__ = ["DevAICostError", "JSONLSchemaError"]
