"""Audit-block sha256 pinning for input-data lineage.

This module exposes ``compute_audit_block`` and the ``AuditBlockHasher``
class implementing the ``simulations.types.protocols.AuditBlockHasher``
Protocol. The function is *pure with respect to the contents* of the listed
files (same paths + same bytes → same hex digest), but it touches the
filesystem to read those bytes and therefore lives in the IO Boundary tier.

Math pin: not directly involved. The audit-block string is consumed by
``ZCapPinned.audit_block`` (validated as a 64-char lowercase hex string in
``simulations.types.posterior``).
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from pathlib import Path
from typing import Final

#: Read-buffer size for streaming sha256 over file contents.
_HASH_CHUNK_BYTES: Final[int] = 1 << 20  # 1 MiB


def compute_audit_block(file_paths: Sequence[str | Path]) -> str:
    """Return a 64-char lowercase hex sha256 over a list of file contents.

    The hash is taken in **path-sorted order** (lexicographic on the
    string form of each path) so the output is deterministic regardless of
    the input order. Each file's bytes are fed into a single sha256 stream
    preceded by a delimiter line ``b"--- <path>\\n"`` so that two files
    swapping bytes cannot collide with the same total content.

    NOTE (pre-mortem #5, scratch/2026-05-08-sim-infra-audit/): the path
    string is embedded VERBATIM in the hashed delimiter — relative and
    absolute representations of the same file produce DIFFERENT digests.
    Callers that need cross-call-site digest equality MUST canonicalize
    (e.g., ``Path.resolve()``) before passing in. This is intentional;
    pinned by ``test_compute_audit_block_path_form_matters``.

    Args:
        file_paths: One or more existing regular files. Empty sequences
            raise ``ValueError`` (an empty audit block is meaningless).

    Returns:
        A 64-character lowercase hexadecimal sha256 digest.

    Raises:
        ValueError: If ``file_paths`` is empty.
        FileNotFoundError: If any path does not exist or is not a file.
    """
    if len(file_paths) == 0:
        raise ValueError("compute_audit_block: file_paths must be non-empty")

    coerced: list[Path] = [Path(p) for p in file_paths]
    sorted_paths: list[Path] = sorted(coerced, key=lambda p: str(p))
    h = hashlib.sha256()
    for p in sorted_paths:
        if not p.is_file():
            raise FileNotFoundError(f"compute_audit_block: not a regular file: {p}")
        h.update(f"--- {p}\n".encode("utf-8"))
        with p.open("rb") as fh:
            while True:
                chunk = fh.read(_HASH_CHUNK_BYTES)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()


class AuditBlockHasher:
    """IO-Boundary class implementing the ``AuditBlockHasher`` Protocol.

    Wraps ``compute_audit_block`` so that callers can depend on the typed
    Protocol (declared in ``simulations.types.protocols``) rather than a
    free function. The class is intentionally stateless apart from
    construction; mutability is admitted only because IO Boundary tier
    rules permit it.
    """

    def __init__(self) -> None:
        # No mutable state today; ``__init__`` exists to satisfy the IO
        # Boundary tier shape (class with __init__, not frozen-dc).
        pass

    def __call__(self, paths: tuple[Path, ...]) -> str:
        """Delegate to ``compute_audit_block``; identical contract.

        Contract:
            Preconditions:
                - ``paths`` non-empty (raises ``ValueError`` from callee).
                - Every entry must be a regular file
                  (``FileNotFoundError`` from callee).

            Raises:
                ValueError: empty ``paths``.
                FileNotFoundError: any path missing or not a regular file.
                OSError: read failure on a present file (propagates from
                    ``open``/``read``; not caught).
        """
        return compute_audit_block(paths)
