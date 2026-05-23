# E10 Phase 0 — Code-Quality Review (Stage 2 of 2)

**Reviewer role:** code-quality (correctness / maintainability / quality).
Spec-compliance (Stage 1) already PASSED.
**Date:** 2026-05-20
**Scope:** `simulations/e10_gsps/`, `scripts/e10_firewall_check.py`,
`.github/workflows/e10-stage2-firewall.yml`, `notebooks/e10_gsps/`,
`.git/hooks/pre-commit`.

## Verdict: APPROVED_WITH_NITS

No Critical findings. No unaddressed Important findings (the two Important
items are doc-accuracy / robustness, not correctness defects in shipped
behavior). Counts: **Critical 0 / Important 2 / Minor 5**.

Evidence run (venv, Python 3.13):
- `python scripts/e10_firewall_check.py` -> `PASS — 37 files scanned clean`, exit 0.
- `pytest simulations/e10_gsps/tests` -> GREEN tests (types round-trip,
  tier-import discipline, all 27 firewall tests) pass; all 5 RED stub
  harnesses + the 2 notebook harnesses fail by design (NotImplementedError /
  missing-notebook), exactly as the plan specifies for Phase 0.

The Phase 0 scaffold is well-structured, accurately typed, and faithfully
ports the E8 POST-CORRECTIONS-α firewall hardening. The findings below are
polish, not blockers.

---

## Important

### I-1. `anti_fishing_checks.py:19-20` — docstring describes a firewall mechanism that does not exist

The module docstring states the file "is itself excluded from the firewall
self-scan via the `CHECK_ALLOWLIST` marker **on its own filename**." The
e10 checker has **no filename-matching logic** — `_line_is_allowlisted`
tests only line content, and `_iter_target_files` filters only by suffix /
`__pycache__`. The file is in fact exempted correctly, but entirely by the
**per-line** `CHECK_ALLOWLIST` markers on lines 26-27 and 53-58.

This matters because a future maintainer trusting the docstring may add a
new banned-token line without a per-line marker, assuming whole-file
exemption is active — and the firewall *will* fire (correct behavior, but
a surprise contradicting the documented contract). The verified banner
string itself matches `\binferential[\s_-]+beta\b`; only the per-line
markers on lines 53-58 keep it clean.

**Fix:** rewrite lines 19-20 to describe the actual mechanism — "every
line that names a banned token carries an end-of-line `CHECK_ALLOWLIST`
marker; there is no filename-level exemption." Drop the "on its own
filename" claim.

### I-2. `e10_firewall_check.py:289` (explicit-path mode) — staged directories / non-target suffixes silently skipped

In explicit-path mode (`argv[1:]`, used by `pre-commit` and
`test_firewalls.py`) `targets = [p for p in explicit if p.exists()]`
applies **no suffix filter and no recursion**. If a staged path is a
directory (rename of a package dir, `git mv`), the checker keeps it in
`targets`; `_scan` then calls `path.read_text()` on the directory, hits
`OSError`, and `except (OSError, UnicodeDecodeError): continue` **silently
drops it** — a scoped scan that produces a false PASS. The default-scan
path (`_iter_target_files`) is correctly hardened; the explicit path is
not symmetric with it.

E8 has the identical gap, so this is an inherited shape, not a regression
— but it is a genuine false-negative surface in the load-bearing Phase-0
code and worth closing now.

**Fix:** in explicit-path mode, expand any directory via `rglob` and apply
the same `{.py,.ipynb,.md}` suffix + `__pycache__` filter that
`_iter_target_files` uses, or assert `p.is_file()` and emit a warning for
skipped non-files so a directory arg cannot pass silently.

---

## Minor

### M-1. `e10_firewall_check.py` STAGE2_BANNED — `redeploy` / `re-deploy` morphology

`\bdeploy(?:ment|able|ed|s|ing)?\b` matches `re-deploy` (word boundary at
the hyphen) but **not** `redeploy` (no boundary inside the token).
Confirmed by direct regex test. Low-risk for this codebase (no current
hit), but a real false-negative if "redeploy" language ever appears.
Consider `(?:re-?)?deploy...` if redeployment language is plausible in
Stage-2 leakage.

### M-2. `nhpp_engine.py:30` — `__post_init__` raises in the RED stub

`NHPPSimulationEngineModule.__post_init__` raises `NotImplementedError`,
so even *construction* fails. This is intentional and documented, and
`test_nhpp_engine.py` relies on it (the harness goes RED at construction).
It is correct for Phase 0. Flagging only so the Phase-2 implementer knows
this line must be deleted, not edited — the docstring says so but the
contrast with the other four stubs (which raise only in `__call__`) is
worth a one-line `# Phase 2: delete this method` marker.

### M-3. Test-tier typing uses `obj: object` + `# type: ignore`

`test_types_roundtrip.py` annotates every fixture as `object` and then
litters `# type: ignore[attr-defined/misc]` to access fields. The
concrete container types are knowable and imported one module away. Using
the real types (`CurrencyDailyFXRow`, etc.) would drop ~20 `type: ignore`
comments and let the type checker actually verify the round-trip asserts.
Pre-existing E8 pattern, so consistent — but the brief asks for "no bare
`Any`/`object` where concrete types are knowable." Tighten when convenient.

### M-4. `test_decomposition.py` mixes `@given` with `st.data()` for paired-length draws

`test_additive_identity_holds_exactly_on_common_grid` takes
`fx_log_returns` via `@given` then draws `q_log_returns` of matching `n`
via a nested `st.data()`. This works but is harder to shrink and read than
a single `@st.composite` strategy yielding the aligned pair. Functionally
fine for a RED harness; consider a `paired_log_returns()` composite
strategy when the Phase-3 module lands so failure shrinking stays clean.

### M-5. `CHECK_ALLOWLIST` comment mechanism in `_DV_RECORD.md` / `_TEMPLATE.md` — confirmed minimal-scope

Per the spec-reviewer's request to confirm: the markers are minimal and
correctly scoped. Every `CHECK_ALLOWLIST` in the disposition files sits on
an individual line that legitimately names a banned token (`DV-PASS-FREE`,
`DV-PASS-QUOTED` — both contain `PASS` which the descriptive regex matches
via `\bPASS\b` since `-` is a non-word boundary; spec-§9 quoting blocks
naming the retired `PASS`/`FAIL` rungs). Verified: `grep` for banned
tokens *without* a `CHECK_ALLOWLIST` marker returns nothing in either
disposition file. The per-line discipline holds; no whole-file or
whole-block over-exemption. No change needed — confirmation only.

---

## Checklist results (passing items, condensed)

- **Three-tier discipline:** PASS. `test_tier_import_discipline.py` GREEN;
  direct import inspection confirms `types/` imports only stdlib +
  intra-`types`, `modules/` imports only `types`, `utils/` is empty.
- **functional-python conformance:** PASS. All containers
  `@dataclass(frozen=True, slots=True)`; callables are frozen-dc with
  `__call__` or free functions; no mutable state outside `utils/` (empty
  in Phase 0); inheritance limited to `Enum`, `Protocol`, `RuntimeError`
  subclasses. Full typing throughout `simulations/` source.
- **Firewall checker hardening:** PASS. Per-line allowlist (no whole-file
  exemption — `test_per_line_allowlist_does_not_exempt_whole_file` GREEN);
  AST-based docstring detection via `_docstring_line_ranges` with
  fail-closed `SyntaxError` handling; boundary-anchored `\bLP\b`,
  `\bPASS\b`; full deploy morphology; all three firewalls fire on
  synthetic violations; fantasy firewall correctly has no docstring
  exemption; exit code 1 on violation, 0 on clean.
- **RED stubs:** PASS. All 5 stubs typed with full signatures, bodies
  raise `NotImplementedError` with a phase-naming message
  (`_PHASE1`.._PHASE6`), no logic. Each docstring names its landing phase.
- **Test harness quality:** PASS. No vacuous `assert True`; RED harnesses
  test real surface (additive identity, overdispersion Fano>1, Q-perp-FX
  independence, interior-crossing, 2^6 verdict exhaustiveness). Hypothesis
  strategies type-appropriate; `three_way_decomposition_cells` correctly
  constructs exact-identity cells.
- **Pre-commit hook:** PASS. Executable (`-rwxr-xr-x`); chains
  e8/e7a/e4/e10; each block guards on `[ -f "$CHECKER" ]` and only runs
  when staged files match the scope regex; `set -e` propagates checker
  failure. Missing-venv handled — uses `python3` directly, no venv
  assumption.
- **CI workflow:** PASS. Triggers on `push` (main/master) + `pull_request`
  + `workflow_dispatch`; correct path filters; invokes the e10 checker;
  Python 3.13 matches `requires-python = ">=3.13"` in `pyproject.toml`.
- **Security:** PASS. No hardcoded secrets / keys; no `eval`/`exec`/
  `pickle`; `ast.parse` is parse-only (no code execution). The firewall
  test writes synthetic files into the tree but removes them in a
  `finally` block.
- **Maintainability:** PASS. File sizes reasonable (checker 312 lines,
  largest module 99); one responsibility per file; E8 RED-stub pattern
  consistently mirrored.

## Single most important finding

**I-1** — the `anti_fishing_checks.py` docstring documents a filename-based
firewall exemption that the checker does not implement. The exemption
works (via per-line markers), but the inaccurate docstring will mislead
the Phase-2+ maintainer into omitting a required per-line marker. A
two-line docstring correction closes it.
