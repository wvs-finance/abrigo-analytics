"""Smoke tests for simulations.dev_ai_cost_v2._errors hierarchy.

Verifies CORRECTIONS-AA (R6 v0.1.3): DevAICostError introduced as sub-package
root; JSONLSchemaError multi-inherits from both DevAICostError and
SchemaMismatchError; MRO well-defined.
"""
from __future__ import annotations

from simulations.dev_ai_cost_v2._errors import DevAICostError, JSONLSchemaError
from simulations.utils.errors import SchemaMismatchError


def test_dev_ai_cost_error_is_exception_subclass() -> None:
    assert issubclass(DevAICostError, Exception)


def test_jsonl_schema_error_multi_inheritance() -> None:
    assert issubclass(JSONLSchemaError, DevAICostError)
    assert issubclass(JSONLSchemaError, SchemaMismatchError)
    assert issubclass(JSONLSchemaError, ValueError)
    assert issubclass(JSONLSchemaError, Exception)


def test_jsonl_schema_error_mro() -> None:
    """MRO should resolve cleanly per CORRECTIONS-AA docstring."""
    mro = JSONLSchemaError.__mro__
    # JSONLSchemaError, DevAICostError, SchemaMismatchError, ValueError, Exception, BaseException, object
    assert mro[0] is JSONLSchemaError
    assert DevAICostError in mro
    assert SchemaMismatchError in mro
    assert ValueError in mro
    assert Exception in mro


def test_jsonl_schema_error_raisable_and_catchable_as_each_ancestor() -> None:
    """Real raise/catch semantics — not just issubclass."""
    for catch_type in (JSONLSchemaError, DevAICostError, SchemaMismatchError, ValueError, Exception):
        try:
            raise JSONLSchemaError("test message")
        except catch_type as exc:
            assert str(exc) == "test message"
