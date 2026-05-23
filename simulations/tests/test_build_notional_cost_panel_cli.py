"""CLI smoke tests for ``scripts/build_notional_cost_panel.py``.

These tests exercise ``argparse`` wiring only — they do not invoke the
panel build itself (which requires a populated ``~/.claude/projects``
tree, a Banrep TRM parquet, and a LiteLLM pricing cache that Task 10
provisions). Smoke coverage is sufficient for Task 8's exit criteria:
the CLI is importable, ``--help`` prints, and required-arg omission
exits non-zero.
"""
from __future__ import annotations

import subprocess
import sys

from scripts.build_notional_cost_panel import _parse_args


def test_cli_help_runs() -> None:
    """`python -m scripts.build_notional_cost_panel --help` exits 0 and lists --since/--until."""
    r = subprocess.run(
        [sys.executable, "-m", "scripts.build_notional_cost_panel", "--help"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert "--since" in r.stdout
    assert "--until" in r.stdout


def test_cli_missing_required_args_exits_nonzero() -> None:
    """Invoking the CLI without --since/--until must exit with a non-zero code."""
    r = subprocess.run(
        [sys.executable, "-m", "scripts.build_notional_cost_panel"],
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    # argparse writes the usage error to stderr.
    assert "--since" in r.stderr or "required" in r.stderr.lower()


def test_cli_args_parsing(monkeypatch) -> None:
    """`_parse_args` parses well-formed --since/--until into ``datetime.date``."""
    from datetime import date
    from pathlib import Path

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_notional_cost_panel",
            "--since",
            "2024-01-01",
            "--until",
            "2024-02-01",
        ],
    )
    args = _parse_args()
    assert args.since == date(2024, 1, 1)
    assert args.until == date(2024, 2, 1)
    assert isinstance(args.projects_root, Path)
    assert isinstance(args.litellm_cache, Path)
    assert isinstance(args.trm_path, Path)
    assert isinstance(args.out, Path)
    # Default --out should live under the repo's data/panels/ tree.
    assert args.out.name == "notional_cost_panel.parquet"
    assert args.out.parent.name == "panels"
