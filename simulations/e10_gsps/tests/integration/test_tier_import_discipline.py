"""Tier-import discipline test (plan v0.2 Phase 0.1 deliverable acceptance).

CLAUDE.md ``simulations/`` rule:
- types/ does NOT import from modules/ or utils/
- modules/ does NOT import from utils/
- utils/ MAY import from types/ but not from modules/

This test goes GREEN in Phase 0 (the skeleton imports cleanly under the
tier-import discipline).
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # simulations/e10_gsps/


def _walk_py(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]


def _module_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


@pytest.mark.parametrize("py_file", _walk_py(PACKAGE_ROOT / "types"))
def test_types_does_not_import_modules_or_utils(py_file: Path) -> None:
    for imp in _module_imports(py_file):
        assert "e10_gsps.modules" not in imp, (
            f"{py_file} imports modules — types-tier discipline violation"
        )
        assert "e10_gsps.utils" not in imp, (
            f"{py_file} imports utils — types-tier discipline violation"
        )


@pytest.mark.parametrize("py_file", _walk_py(PACKAGE_ROOT / "modules"))
def test_modules_does_not_import_utils(py_file: Path) -> None:
    for imp in _module_imports(py_file):
        assert "e10_gsps.utils" not in imp, (
            f"{py_file} imports utils — modules-tier discipline violation"
        )


@pytest.mark.parametrize("py_file", _walk_py(PACKAGE_ROOT / "utils"))
def test_utils_does_not_import_modules(py_file: Path) -> None:
    for imp in _module_imports(py_file):
        assert "e10_gsps.modules" not in imp, (
            f"{py_file} imports modules — utils-tier discipline violation"
        )


def test_package_skeleton_imports_cleanly() -> None:
    """Phase 0.1 exit criterion: the skeleton imports cleanly."""
    for module_name in (
        "simulations.e10_gsps",
        "simulations.e10_gsps._errors",
        "simulations.e10_gsps.types",
        "simulations.e10_gsps.modules",
        "simulations.e10_gsps.utils",
    ):
        importlib.import_module(module_name)
