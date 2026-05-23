"""Cross-tier structural Protocols.

Per the functional-python skill, ``typing.Protocol`` is the only allowed form
of inheritance. Cross-tier interfaces (e.g., a parquet reader consumed by a
``modules/`` Callable but implemented in ``utils/``) are declared here as
Protocols so that the tier-import discipline holds: ``modules/`` imports the
abstract Protocol from ``types/`` rather than the concrete class from
``utils/``.

Implementations live in ``simulations.utils`` (IO Boundary tier).
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from simulations.types.posterior import PosteriorDraws, ZCapPinned


@runtime_checkable
class PosteriorDrawsReader(Protocol):
    """Read a ``PosteriorDraws`` Value from a parquet artifact.

    Implementations live in ``simulations.utils``. The reader validates the
    column schema (Pin M4) before constructing the Value.
    """

    def __call__(self, path: Path) -> PosteriorDraws: ...


@runtime_checkable
class PosteriorDrawsWriter(Protocol):
    """Write a ``PosteriorDraws`` Value to a parquet artifact.

    Implementations enforce the M4 column schema and (per Phase 1
    reconciliation §2.4) emit the ``schema_version`` column.
    """

    def __call__(self, draws: PosteriorDraws, path: Path) -> None: ...


@runtime_checkable
class ZCapPinnedReader(Protocol):
    """Read a ``ZCapPinned`` Value from a JSON artifact (spec §10)."""

    def __call__(self, path: Path) -> ZCapPinned: ...


@runtime_checkable
class ZCapPinnedWriter(Protocol):
    """Write a ``ZCapPinned`` Value to a JSON artifact (spec §10)."""

    def __call__(self, z: ZCapPinned, path: Path) -> None: ...


@runtime_checkable
class AuditBlockHasher(Protocol):
    """Compute a stable sha256 audit-block hex string over a list of paths.

    Pure with respect to the contents of the listed files; implementations
    live in ``simulations.utils`` because they touch the filesystem.
    """

    def __call__(self, paths: tuple[Path, ...]) -> str: ...
