"""ccusage-parity oracle integration test (v0.2.3 closure).

Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.3
§3.5 — ccusage-parity-within-0.1% on cost is the v0.2.3 cost-arithmetic
oracle (Y-2). This test confirms our PricingTable.__call__ output matches
ccusage's session totals on the same input JSONL.

Status today:
- The shared fixture is a synthetic placeholder (sample contains a
  ``// SYNTHETIC`` marker on its first line). When the fixture is
  synthetic, this test is SKIPPED (synthetic data cannot serve as an
  authoritative oracle).
- When the ccusage CLI is not installed, this test is XFAILed. Operators
  can run ``npm install -g ccusage`` (or ``npx ccusage@latest ...``) to
  enable the parity check.

The test also confirms (independent of ccusage):
- The reader does not raise on the fixture (parse covers all row types).
- Assistant rows are extracted; non-assistant rows are counted in
  ``dropped_non_assistant_count``.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import warnings
from datetime import date
from pathlib import Path

import pytest

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
    _REQUIRED_KEYS,
)
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader

FIXTURE_DIR = (
    Path(__file__).parent / "fixtures" / "real_claude_jsonl"
)
FIXTURE_FILE = FIXTURE_DIR / "synthetic_sample.jsonl"


def _is_synthetic(path: Path) -> bool:
    """A fixture is synthetic if its first JSON object carries a
    `_comment` field starting with "SYNTHETIC".
    """
    with path.open() as f:
        first_line = f.readline().strip()
    if not first_line:
        return False
    try:
        obj = json.loads(first_line)
    except json.JSONDecodeError:
        return False
    comment = obj.get("_comment", "") if isinstance(obj, dict) else ""
    return isinstance(comment, str) and comment.startswith("SYNTHETIC")


def _toy_pricing(tmp_path: Path) -> PricingTable:
    """Use a uniform 1e-06 rate so the parse smoke-test does not depend on
    a network LiteLLM cache. The ccusage-parity assertion below uses the
    real pinned cache when present (see _real_pricing).
    """
    fake = {
        m: {k: 1e-06 for k in _REQUIRED_KEYS}
        for m in ("claude-sonnet-4-5", "claude-haiku-4-5", "claude-opus-4-7")
    }
    p = tmp_path / "lite.json"
    p.write_text(json.dumps(fake))
    return PricingTable.from_litellm_sha(
        LITELLM_SHA_PINNED, p, skip_sha_check=True
    )


# ─── Parse-smoke (always runs if fixture exists) ────────────────────────────


def test_real_fixture_parses_without_error(tmp_path: Path) -> None:
    """The reader must parse the fixture without raising. Non-assistant
    rows must be counted via JSONLReadResult.dropped_non_assistant_count.
    """
    if not FIXTURE_FILE.exists():
        pytest.skip(f"no fixture at {FIXTURE_FILE}")

    # Copy the fixture into a tmp projects_root so we don't pollute the
    # checked-in tree with derived files.
    projects = tmp_path / "projects" / "p1"
    projects.mkdir(parents=True)
    shutil.copy(FIXTURE_FILE, projects / "session.jsonl")

    reader = JSONLReader(pricing=_toy_pricing(tmp_path))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        out = reader(
            since=date(2026, 5, 10),
            until=date(2026, 5, 11),
            projects_root=tmp_path / "projects",
        )

    # The synthetic fixture in this repo contains 5 assistant rows
    # (1 is_error=True) + 3 non-assistant rows (1 user, 1 summary, 1 system)
    # + 1 comment row (no type field → treated as non-assistant).
    assert len(out.records) == 5
    # 1 comment + 1 user + 1 summary + 1 system = 4 non-assistant skips.
    assert out.dropped_non_assistant_count == 4

    # All extracted records are assistant rows with valid uuids.
    for rec in out.records:
        assert rec.uuid != ""
        assert rec.input_tok >= 0


# ─── ccusage-parity oracle (xfail/skip-gated) ───────────────────────────────


def test_ccusage_parity_oracle(tmp_path: Path) -> None:
    """ccusage-parity oracle (v0.2.3 §3.5 cost arithmetic ground truth).

    Skipped if:
    - Fixture file missing.
    - Fixture is synthetic (cannot serve as authoritative oracle).
    XFailed if:
    - ccusage CLI not on PATH and ``npx ccusage`` unreachable.

    When all conditions met: assert
    ``abs(our_total - ccusage_total) / ccusage_total < 0.001``.
    """
    if not FIXTURE_FILE.exists():
        pytest.skip(f"no fixture at {FIXTURE_FILE}")
    if _is_synthetic(FIXTURE_FILE):
        pytest.skip(
            "synthetic fixture; real PII-redacted Claude Code session JSONL "
            "required for ccusage-parity oracle"
        )

    # Copy fixture into a tmp projects_root mirroring Claude Code layout.
    projects = tmp_path / "projects" / "p1"
    projects.mkdir(parents=True)
    shutil.copy(FIXTURE_FILE, projects / "session.jsonl")

    # Try to invoke ccusage. Two failure modes are both xfail:
    # - npx (npm) not installed
    # - ccusage exits non-zero (e.g., unsupported flag, network unreachable)
    try:
        result = subprocess.run(
            ["npx", "--yes", "ccusage@latest", "session",
             "--json", "--path", str(projects)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        pytest.xfail("ccusage CLI / npx not available on PATH")
    if result.returncode != 0:
        pytest.xfail(
            f"ccusage exited non-zero ({result.returncode}); "
            f"stderr={result.stderr[:300]!r}"
        )

    try:
        ccusage_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.xfail(
            f"ccusage stdout was not valid JSON; got {result.stdout[:300]!r}"
        )

    # ccusage session --json emits {"sessions": [{"totalCost": ...}, ...]}.
    # Schema may evolve; defend against breakage with xfail rather than
    # falsely failing the spec contract.
    ccusage_total: float
    try:
        ccusage_total = float(
            sum(s.get("totalCost", 0.0) for s in ccusage_data.get("sessions", []))
        )
    except (TypeError, KeyError, AttributeError):
        pytest.xfail(
            f"ccusage JSON schema not recognized: keys={list(ccusage_data)[:10]}"
        )

    if ccusage_total <= 0:
        pytest.xfail("ccusage returned zero total cost; cannot oracle-check")

    # Compute our total against the SAME pricing snapshot ccusage uses.
    # In real fixtures with the production LiteLLM cache available locally,
    # the operator should swap _toy_pricing for the pinned table.
    pricing_cache = (
        Path(__file__).resolve().parents[2]
        / "data" / "raw" / "litellm_model_prices.json"
    )
    if not pricing_cache.exists():
        pytest.xfail(
            f"production LiteLLM cache absent at {pricing_cache} — "
            "the parity oracle requires the same rate table ccusage uses"
        )
    pricing = PricingTable.from_litellm_sha(
        LITELLM_SHA_PINNED, pricing_cache, skip_sha_check=False
    )
    reader = JSONLReader(pricing=pricing)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        out = reader(
            since=date(2020, 1, 1),
            until=date(2099, 1, 1),
            projects_root=tmp_path / "projects",
        )
    our_total = sum(r.cost_usd_notional for r in out.records)

    rel_err = abs(our_total - ccusage_total) / ccusage_total
    assert rel_err < 1e-3, (
        f"ccusage parity oracle failed: ours={our_total}, "
        f"ccusage={ccusage_total}, rel_err={rel_err}"
    )
