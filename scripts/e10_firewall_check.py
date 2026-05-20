#!/usr/bin/env python3
"""E10 GSPS mechanical firewall checker (plan v0.2 Phase 0.11 + 0.12 + 0.13).

Runs all three E10 firewalls in a single pass; rejects (exit-code 1) on
any prohibited match. Used by:

- ``.git/hooks/pre-commit`` (developer-local enforcement)
- ``.github/workflows/e10-stage2-firewall.yml`` (CI enforcement)
- ``pytest simulations/e10_gsps/tests/integration/test_firewalls.py``
  (TDD foundation)

Usage:

    python scripts/e10_firewall_check.py [PATH...]

If no PATH given, scans the main-line scopes:
    simulations/e10_gsps/
    notebooks/e10_gsps/

The three firewalls (plan v0.2 §1 Phase 0):

1. **Stage-2 firewall (0.11)** — rejects Panoptic / LP / strike-selection
   / range-geometry / payoff-fitting / deployment language in main-line
   code OUTSIDE true Python docstrings and ``CHECK_ALLOWLIST``-marked
   lines. E10 Stage-1 (the §§3-9 measurement layer) is firewalled from
   the Stage-2 §13 M-sketch; payoff-fitting language belongs only in
   §13-resident M-sketch docstrings and explicit spec-§13 cross-refs.

2. **Fantasy-firewall (0.12)** — rejects any commit where the FX series
   or the $0.01 multiplier is sourced from a fitted prior, a synthetic
   generator, or a placeholder constant instead of the real central-bank
   pull or the verified x402 price. Enforces spec v0.4 §3.1 / §5.1 — X
   and the FX multiplier are 100% real; Q is the ONLY simulated quantity.

3. **Descriptive-posture firewall (0.13)** — rejects ``PASS``,
   ``confirmatory``, and inferential-beta verdict language anywhere in
   ``simulations/e10_gsps/`` or ``notebooks/e10_gsps/`` outside an
   explicitly tagged block quoting the spec §9 ladder or the §7 sign
   gate. Enforces CORRECTIONS-E10-4 Fix 1 / spec §9 — E10 v0.4 is
   descriptive-only.

Allowlist mechanism (adapted from e8 POST-CORRECTIONS-α — per-line).

Each line is scanned independently. All three firewalls exempt ONLY
individual lines that contain the literal token ``CHECK_ALLOWLIST``
(case-sensitive). The exemption never propagates to neighboring lines.
Spec/plan files in ``docs/`` are out of firewall scope by construction.

Docstring exemption (Stage-2 + descriptive-posture firewalls — AST-based).

True Python docstrings (the first ``ast.Expr`` whose value is an
``ast.Constant`` of type ``str`` inside ``Module``, ``ClassDef``,
``FunctionDef``, or ``AsyncFunctionDef``) are exempt from the Stage-2 and
descriptive-posture regexes — this allows §13 M-sketch references and
spec-§9-ladder quotes to live in module docstrings. Triple-quoted string
literals at any OTHER position are NOT docstrings and remain subject to
the firewalls. The fantasy-firewall has NO docstring exemption — a
fitted-prior FX substitution is a violation wherever it appears.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------
# Firewall 1 — Stage-2 (plan 0.11). Panoptic / LP / strike-selection /
# range-geometry / payoff-fitting / deployment language is firewalled
# out of main-line Stage-1 code.
# --------------------------------------------------------------------
STAGE2_BANNED = re.compile(
    r"(?i)(?:"
    r"\bPanoptic\b|"
    r"\b(?:re-?)?deploy(?:ment|able|ed|s|ing)?\b|"
    r"\bLP\b|"
    r"\bliquidity[\s_-]+sizing\b|"
    r"\bposition[\s_-]+open\b|"
    r"\bstrike[\s_-]+selection\b|"
    r"\bstrike[\s_-]*/[\s_-]*range\b|"
    r"\brange[\s_-]+geometry\b|"
    r"\bpayoff[\s_-]+fitting\b|"
    r"\bpayoff[\s_-]+sizing\b|"
    r"\bfitted[\s_-]+payoff\b|"
    r"\bpremium[\s_-]+fraction\b|"
    r"\bM[\s_-]?sketch[\s_-]+finalized\b|"
    r"\bready[\s_-]+to[\s_-]+deploy\b"
    r")"
)

# --------------------------------------------------------------------
# Firewall 2 — fantasy (plan 0.12). The FX series and the $0.01
# multiplier must be the real central-bank pull / verified x402 price;
# never a fitted prior, synthetic generator, or placeholder constant.
# Q is the ONLY generated quantity.
# --------------------------------------------------------------------
FANTASY_BANNED = re.compile(
    r"(?i)(?:"
    r"\bsynthetic[\s_-]+FX\b|"
    r"\bsimulated[\s_-]+FX\b|"
    r"\bfabricated[\s_-]+FX\b|"
    r"\bfake[\s_-]+FX\b|"
    r"\bmock[\s_-]+FX[\s_-]+(?:rate|series|path|panel)\b|"
    r"\bgenerated[\s_-]+FX[\s_-]+(?:rate|series|path|panel)\b|"
    r"\bfitted[\s_-]+(?:FX[\s_-]+)?prior[\s_-]+(?:for[\s_-]+)?FX\b|"
    r"\bFX[\s_-]+(?:rate|series|path|panel)[\s_-]+from[\s_-]+"
    r"(?:a[\s_-]+)?(?:fitted[\s_-]+prior|synthetic[\s_-]+generator|"
    r"placeholder)\b|"
    r"\bplaceholder[\s_-]+(?:FX[\s_-]+(?:rate|multiplier)|"
    r"x402[\s_-]+price)\b|"
    r"\bsynthetic[\s_-]+(?:per-query[\s_-]+)?(?:x402[\s_-]+)?price\b|"
    r"\bfabricated[\s_-]+(?:x402[\s_-]+)?(?:price|multiplier)\b|"
    r"\bhard-?cod(?:e|ed|ing)[\s_-]+(?:the[\s_-]+)?FX\b"
    r")"
)

# --------------------------------------------------------------------
# Firewall 3 — descriptive-posture (plan 0.13). E10 v0.4 is
# descriptive-only; PASS / confirmatory / inferential-beta verdict
# language is banned outside an explicitly tagged spec-quoting block.
# --------------------------------------------------------------------
DESCRIPTIVE_BANNED = re.compile(
    r"(?:"
    r"\bPASS\b|"  # bare verdict token — confirmatory rung
    r"(?i:\bconfirmatory\b)|"
    r"(?i:\b(?:beta|β)[\s_-]+verdict\b)|"
    r"(?i:\binferential[\s_-]+(?:beta|β)\b)|"
    r"(?i:\bsignificant[\s_-]+at\b)|"
    r"(?i:\bstatistically[\s_-]+significant\b)|"
    r"(?i:\breject[\s_-]+the[\s_-]+null\b)|"
    r"(?i:\bconfidence[\s_-]+statement\b)"
    r")"
)

ALLOWLIST_TOKEN = "CHECK_ALLOWLIST"

MAINLINE_CODE_ROOT = REPO_ROOT / "simulations" / "e10_gsps"
MAINLINE_NOTEBOOK_ROOT = REPO_ROOT / "notebooks" / "e10_gsps"


def _docstring_line_ranges(text: str) -> set[int]:
    """Return the set of 1-indexed line numbers inside a true Python
    docstring per CPython semantics (first statement of Module /
    ClassDef / FunctionDef / AsyncFunctionDef, an ast.Expr wrapping a
    str Constant). All other string literals are NOT docstrings.

    On SyntaxError returns an empty set — the file is then scanned in
    full with no docstring exemption (fail-closed)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    lines: set[int] = set()
    docstring_parents = (
        ast.Module,
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    )
    for node in ast.walk(tree):
        if not isinstance(node, docstring_parents):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if not isinstance(first, ast.Expr):
            continue
        value = first.value
        if not isinstance(value, ast.Constant):
            continue
        if not isinstance(value.value, str):
            continue
        start = getattr(first, "lineno", None)
        end = getattr(first, "end_lineno", None)
        if start is None or end is None:
            continue
        for ln in range(start, end + 1):
            lines.add(ln)
    return lines


TARGET_SUFFIXES = {".py", ".ipynb", ".md"}


def _is_scannable_file(path: Path) -> bool:
    """True iff ``path`` is a regular file with a target suffix and not
    inside a ``__pycache__`` directory."""
    if not path.is_file():
        return False
    if path.suffix not in TARGET_SUFFIXES:
        return False
    if "__pycache__" in path.parts:
        return False
    return True


def _iter_target_files(roots: list[Path]) -> list[Path]:
    """Yield .py / .ipynb / .md files under the given roots, recursive."""
    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if _is_scannable_file(path):
                found.append(path)
    return found


def _expand_explicit_targets(explicit: list[Path]) -> list[Path]:
    """Resolve explicit-path arguments (pre-commit hook / firewall test)
    into a flat list of scannable files.

    A directory argument is recursively expanded with the SAME suffix +
    ``__pycache__`` filter that ``_iter_target_files`` applies, so a
    staged directory (e.g. a ``git mv`` of a package dir) can never be
    silently dropped by the ``OSError`` handler in ``_scan`` — that
    would be a false-PASS surface in a scoped scan. A file argument is
    kept only if it is scannable; a non-existent path is skipped."""
    targets: list[Path] = []
    for path in explicit:
        if not path.exists():
            continue
        if path.is_dir():
            for child in path.rglob("*"):
                if _is_scannable_file(child):
                    targets.append(child)
        elif _is_scannable_file(path):
            targets.append(path)
    return targets


def _line_is_allowlisted(line: str) -> bool:
    """Per-line allowlist: only the line containing the literal
    CHECK_ALLOWLIST marker is exempted; other lines remain scanned."""
    return ALLOWLIST_TOKEN in line


def _scan(
    paths: list[Path],
    pattern: re.Pattern[str],
    *,
    docstring_exempt: bool,
) -> list[tuple[Path, int, str]]:
    """Run a firewall regex on each file, line by line.

    Per-line allowlist always applies. AST docstring exemption applies
    to .py files only when ``docstring_exempt`` is True."""
    violations: list[tuple[Path, int, str]] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if docstring_exempt and path.suffix == ".py":
            docstring_lines = _docstring_line_ranges(text)
        else:
            docstring_lines = set()
        for lineno, line in enumerate(text.splitlines(), start=1):
            if lineno in docstring_lines:
                continue
            if _line_is_allowlisted(line):
                continue
            match = pattern.search(line)
            if match:
                violations.append((path, lineno, match.group(0)))
    return violations


def check_stage2(paths: list[Path]) -> list[tuple[Path, int, str]]:
    """Stage-2 firewall (plan 0.11). Docstring-exempt."""
    return _scan(paths, STAGE2_BANNED, docstring_exempt=True)


def check_fantasy(paths: list[Path]) -> list[tuple[Path, int, str]]:
    """Fantasy-firewall (plan 0.12). NO docstring exemption — a
    fitted-prior FX substitution is a violation wherever it appears."""
    return _scan(paths, FANTASY_BANNED, docstring_exempt=False)


def check_descriptive(paths: list[Path]) -> list[tuple[Path, int, str]]:
    """Descriptive-posture firewall (plan 0.13). Docstring-exempt — a
    spec-§9-ladder quote may appear in a module docstring; an explicit
    CHECK_ALLOWLIST line exempts a spec-quoting block elsewhere."""
    return _scan(paths, DESCRIPTIVE_BANNED, docstring_exempt=True)


def main(argv: list[str]) -> int:
    explicit = [Path(p) for p in argv[1:]]
    if explicit:
        targets = _expand_explicit_targets(explicit)
    else:
        targets = _iter_target_files(
            [MAINLINE_CODE_ROOT, MAINLINE_NOTEBOOK_ROOT]
        )

    stage2_v = check_stage2(targets)
    fantasy_v = check_fantasy(targets)
    descriptive_v = check_descriptive(targets)

    if not (stage2_v or fantasy_v or descriptive_v):
        print(f"E10 firewall PASS — {len(targets)} files scanned clean.")
        return 0

    if stage2_v:
        print(
            "E10 Stage-2 firewall VIOLATIONS (plan Phase 0.11):",
            file=sys.stderr,
        )
        for path, lineno, hit in stage2_v:
            print(
                f"  {path}:{lineno}: banned-Stage-2 token '{hit}'",
                file=sys.stderr,
            )
    if fantasy_v:
        print(
            "E10 fantasy-firewall VIOLATIONS (plan Phase 0.12):",
            file=sys.stderr,
        )
        for path, lineno, hit in fantasy_v:
            print(
                f"  {path}:{lineno}: banned-fantasy token '{hit}' — FX / "
                f"x402 price must be the real pull, not a fitted prior",
                file=sys.stderr,
            )
    if descriptive_v:
        print(
            "E10 descriptive-posture firewall VIOLATIONS (plan Phase 0.13):",
            file=sys.stderr,
        )
        for path, lineno, hit in descriptive_v:
            print(
                f"  {path}:{lineno}: banned-inferential token '{hit}' — "
                f"E10 v0.4 is descriptive-only, makes no inferential beta "
                f"claim",
                file=sys.stderr,
            )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
