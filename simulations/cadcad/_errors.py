"""cadCAD-integration typed errors.

Parent spec: ``docs/papers/2026-05-16-stochastic-fx-variance-proxy-paper.tex``
§6 (cadCAD integration of the verified stochastic-FX machinery). Per the
functional-python skill only Exception subclassing is admitted as
class-inheritance outside Protocols. The cadCAD error hierarchy extends the
stochastic-fx ``StochasticFXError`` base so that downstream callers can
catch a single root for the whole stochastic-FX + cadCAD surface.
"""

from __future__ import annotations

from simulations.stochastic_fx._errors import StochasticFXError


class CadCADError(StochasticFXError):
    """Base class for cadCAD-integration errors (paper §6 family)."""


class CadCADConfigError(CadCADError):
    """Raised when ``CadCADConfig.__post_init__`` rejects invalid hyperparameters."""


class CadCADStateError(CadCADError):
    """Raised when ``CadCADState.__post_init__`` rejects invalid state values."""


__all__ = [
    "CadCADConfigError",
    "CadCADError",
    "CadCADStateError",
]
