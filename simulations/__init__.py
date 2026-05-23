"""Global simulations infrastructure for Abrigo FX-vol iterations.

Three-tier functional-python discipline (per ~/.claude/skills/functional-python/SKILL.md):

- ``simulations.types``  — Value tier: frozen-dataclass parameter containers,
  Protocols, TypeAliases, Final constants. NO logic, NO side effects.
- ``simulations.modules`` — Callable tier: frozen-dataclass + ``__call__``
  stateless transforms. Imports from ``types`` only.
- ``simulations.utils``   — IO Boundary tier: classes with ``__init__`` for
  filesystem / network. The only place mutable state is allowed.

See ``simulations/README.md`` for the full contract.
"""

from typing import Final

SIMULATIONS_VERSION: Final[str] = "0.1.0"

# Rolling horizon default (months) per spec §2 + PRIMITIVES §15.
DEFAULT_DT_MONTHS: Final[int] = 12

__all__: list[str] = [
    "SIMULATIONS_VERSION",
    "DEFAULT_DT_MONTHS",
]
