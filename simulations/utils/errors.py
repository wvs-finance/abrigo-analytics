"""Typed exceptions raised at IO boundaries.

These exceptions surface schema-level violations *before* a
``simulations.types`` Value is constructed — i.e., they signal that the
on-disk artifact does not match the M4 column / field contract pinned by
spec §10. Per the functional-python skill, ``Exception`` subclassing is
the only inheritance form admitted in user code apart from ``Protocol``.
"""

from __future__ import annotations


class SchemaMismatchError(ValueError):
    """Raised when an on-disk artifact's schema does not match the M4 pin.

    Signals one of:

    - missing required column / JSON field;
    - unexpected extra column / field that the writer did not emit;
    - a column / field whose dtype cannot be coerced to the declared one.

    Subclasses ``ValueError`` so existing ``except ValueError`` clauses
    continue to catch it; the typed name disambiguates IO-boundary
    schema violations from in-process Value validation errors.
    """
