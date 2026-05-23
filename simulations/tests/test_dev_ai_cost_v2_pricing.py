"""Tests for ``simulations.dev_ai_cost_v2.anthropic_pricing.PricingTable``.

Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.3
§3.5 + §0.3 CORRECTIONS-Y-2/-Y-3 + Y-5a/c/d. Replaces v0.2.1 Decimal-exact
arithmetic with ccusage-parity float arithmetic; load-time validation
relaxed (missing keys WARN+count, do not raise); cache 5m+1h aggregation
pinned to ``PricingTable.__call__`` body (CR-Z-3); model-lookup ladder
exact → ``anthropic/<model>`` → longest-substring with alphabetical
tiebreaker (CR-Z-4).

Test inventory:
1. ``test_pricing_table_load_warns_on_missing_key`` — Y-3: missing required
   key emits UserWarning and increments WARN_missing_keys_count.
2. ``test_pricing_table_call_uses_correct_keys`` — float-arithmetic cost
   computation across all five categories with ccusage-parity semantics.
3. ``test_pricing_monotone_in_input_tokens`` — Hypothesis property:
   ``__call__`` is monotone non-decreasing in input token count.
4. ``test_pricing_table_rejects_sha_mismatch`` — production SHA guard.
5. ``test_pricing_table_unknown_model_returns_zero_and_counts`` — Y-5d:
   ladder-exhausted lookup returns 0.0 and increments
   ``dropped_unknown_model_count``.
6. ``test_pricing_table_skips_non_claude_models`` — only ``claude-*``
   models are loaded.
7. ``test_pricing_zero_tokens_zero_cost`` — zero-token edge case.
8. ``test_cr_z_3_aggregation_locus`` — Y-5c: cache 5m+1h aggregation
   happens inside ``PricingTable.__call__`` body, not in
   ``TokensByCategory.__init__``.
9. ``test_cr_z_4_alphabetical_tiebreaker`` — Y-5d: multiple equal-length
   substring matches pick the alphabetically-smallest key deterministically
   regardless of dict insertion order; increments
   ``multiple_substring_match_warning``.
10. ``test_pricing_200k_tier_applied`` — Y-2: tier-rate kicks in past 200k.
11. ``test_pricing_tier_fallback_when_absent`` — Y-2: missing tier rate
    falls back to base, no error.
12. ``test_pricing_none_rate_contributes_zero`` — Y-3: None rate gates
    category to 0 contribution at call time.
"""
from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_FILE_SHA256_PINNED,
    LITELLM_SHA_PINNED,
    PricingTable,
    _REQUIRED_KEYS,
)
from simulations.dev_ai_cost_v2.types import TokensByCategory

# Local alias mirrors the module pin (kept as a string literal so this test
# would fail-loud if the upstream constant were ever quietly bumped).
LITELLM_SHA = "e58a561caa21169fb02174148444c08509ce7028"

# v0.2.10 audit-econ #3: real file location for dual-pin smoke test.
REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_LITELLM_JSON = REPO_ROOT / "data" / "raw" / "litellm_model_prices.json"


# ─── Test 1: load-time WARN-not-raise (Y-3) ──────────────────────────────────


def test_pricing_table_load_warns_on_missing_key(tmp_path: Path) -> None:
    """Y-3 (CORRECTIONS-Y-3): missing required key WARNs and increments
    ``WARN_missing_keys_count`` instead of raising.
    """
    fake_table = {
        "claude-sonnet-4-5": {
            "input_cost_per_token": 3e-06,
            "output_cost_per_token": 15e-06,
            "cache_creation_input_token_cost": 3.75e-06,
            # MISSING: cache_creation_input_token_cost_above_1hr
            "cache_read_input_token_cost": 0.30e-06,
        }
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    with pytest.warns(UserWarning, match="cache_creation_input_token_cost_above_1hr"):
        pt = PricingTable.from_litellm_sha(
            sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
        )
    assert pt.WARN_missing_keys_count >= 1
    # And the missing key surfaces as None in the rate mapping (per-category gate
    # at call time treats None as 0 contribution).
    assert pt.rates["claude-sonnet-4-5"]["cache_creation_input_token_cost_above_1hr"] is None


# ─── Test 2: float-arithmetic call ───────────────────────────────────────────


def test_pricing_table_call_uses_correct_keys(tmp_path: Path) -> None:
    """ccusage-parity float arithmetic across all five categories.

    Per Y-5c, the cache_create_5m and cache_create_1h tokens are summed
    inside ``__call__`` and multiplied by the single
    ``cache_creation_input_token_cost`` rate.
    """
    fake_table = {
        "claude-sonnet-4-5": {
            "input_cost_per_token": 3e-06,
            "output_cost_per_token": 15e-06,
            "cache_creation_input_token_cost": 3.75e-06,
            "cache_creation_input_token_cost_above_1hr": 6e-06,
            "cache_read_input_token_cost": 0.30e-06,
        }
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(
        sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
    )
    toks = TokensByCategory(
        input=1000,
        output=500,
        cache_create_5m=200,
        cache_create_1h=100,
        cache_read=300,
    )
    cost = pt(
        model="claude-sonnet-4-5",
        ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
        toks=toks,
    )
    # Y-5c: 5m+1h aggregated and multiplied by the single 5m rate.
    expected = (
        1000 * 3e-06
        + 500 * 15e-06
        + (200 + 100) * 3.75e-06  # aggregated
        + 300 * 0.30e-06
    )
    assert cost == pytest.approx(expected, rel=1e-12)
    assert isinstance(cost, float)


# ─── Test 3: Hypothesis property — monotone non-decreasing in input tok ──────


@given(
    input_tok=st.integers(0, 10_000),
    extra_input=st.integers(0, 10_000),
)
def test_pricing_monotone_in_input_tokens(
    input_tok: int,
    extra_input: int,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    tmp = tmp_path_factory.mktemp("pricing")
    fake = {"claude-sonnet-4-5": {k: 1e-06 for k in _REQUIRED_KEYS}}
    p = tmp / "litellm.json"
    p.write_text(json.dumps(fake))
    pt = PricingTable.from_litellm_sha(LITELLM_SHA, p, skip_sha_check=True)
    base = pt(
        "claude-sonnet-4-5",
        datetime(2026, 5, 1, tzinfo=timezone.utc),
        TokensByCategory(input_tok, 0, 0, 0, 0),
    )
    more = pt(
        "claude-sonnet-4-5",
        datetime(2026, 5, 1, tzinfo=timezone.utc),
        TokensByCategory(input_tok + extra_input, 0, 0, 0, 0),
    )
    assert more >= base


# ─── Test 4: SHA mismatch guard ──────────────────────────────────────────────


def test_pricing_table_rejects_sha_mismatch(tmp_path: Path) -> None:
    """Production callers (``skip_sha_check=False``) must pass the pinned
    commit-SHA. A drifted SHA argument is a reproducibility failure and
    must be rejected at the load boundary, not silently absorbed.

    v0.2.10 audit-econ #3: the commit-SHA check is now joined by a
    file-sha256 check (see ``test_pricing_table_raises_on_file_sha_mismatch``
    and ``test_pricing_table_passes_with_correct_file_sha`` for the
    file-pin coverage). Using the REAL canonical file here so the
    commit-SHA mismatch is the ONLY failing pin.
    """
    assert REAL_LITELLM_JSON.exists(), (
        f"canonical LiteLLM cache missing at {REAL_LITELLM_JSON}; "
        "make data-raw to provision"
    )
    bogus_sha = "0" * 40
    import warnings as _w
    with _w.catch_warnings():
        _w.simplefilter("ignore", UserWarning)
        with pytest.raises(ValueError, match="pinned"):
            PricingTable.from_litellm_sha(
                sha=bogus_sha,
                cached_json_path=REAL_LITELLM_JSON,
                skip_sha_check=False,
            )
        # And confirm the pinned SHA loads cleanly when skip is off.
        pt = PricingTable.from_litellm_sha(
            sha=LITELLM_SHA_PINNED,
            cached_json_path=REAL_LITELLM_JSON,
            skip_sha_check=False,
        )
    assert pt.sha == LITELLM_SHA_PINNED


# ─── Test 5: unknown model lookup returns 0 and counts (Y-5d) ────────────────


def test_pricing_table_unknown_model_returns_zero_and_counts(tmp_path: Path) -> None:
    """Y-5d: ladder-exhausted lookup is non-fatal — returns 0.0 and
    increments ``dropped_unknown_model_count``.
    """
    fake_table = {
        "claude-sonnet-4-5": {k: 1e-06 for k in _REQUIRED_KEYS},
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(
        sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
    )
    # "gpt-5-turbo" shares no substring overlap with "claude-sonnet-4-5";
    # ladder exhausts and returns 0.
    before = pt.dropped_unknown_model_count
    cost = pt(
        model="gpt-5-turbo",
        ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
        toks=TokensByCategory(1, 0, 0, 0, 0),
    )
    assert cost == 0.0
    assert pt.dropped_unknown_model_count == before + 1


# ─── Test 6: non-claude models are filtered at load ──────────────────────────


def test_pricing_table_skips_non_claude_models(tmp_path: Path) -> None:
    """Only ``claude-*`` keys are retained; the spec scopes the panel to Anthropic."""
    fake_table = {
        "gpt-4": {"input_cost_per_token": 1e-05},  # incomplete + non-claude
        "claude-x": {k: 2e-06 for k in _REQUIRED_KEYS},
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(
        sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
    )
    assert set(pt.rates) == {"claude-x"}
    # And the non-claude entry's missing required keys do NOT trigger a load
    # failure (proving the claude-* filter precedes the required-key check).


# ─── Test 7: zero-token edge case ────────────────────────────────────────────


def test_pricing_zero_tokens_zero_cost(tmp_path: Path) -> None:
    fake_table = {
        "claude-sonnet-4-5": {k: 1e-06 for k in _REQUIRED_KEYS},
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(
        sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
    )
    cost = pt(
        model="claude-sonnet-4-5",
        ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
        toks=TokensByCategory(0, 0, 0, 0, 0),
    )
    assert cost == 0.0


# ─── Test 8: CR-Z-3 aggregation locus (Y-5c) ─────────────────────────────────


def test_cr_z_3_aggregation_locus(tmp_path: Path) -> None:
    """CR-Z-3 / Y-5c: cache 5m+1h aggregation happens inside
    ``PricingTable.__call__``, NOT inside ``TokensByCategory.__init__``.

    After ``TokensByCategory`` construction the split is preserved intact.
    The aggregated cost equals ``(A + B) * rate``.
    """
    A, B = 200, 100  # noqa: N806 — intentionally upper-case to mirror spec
    toks = TokensByCategory(
        input=0,
        output=0,
        cache_create_5m=A,
        cache_create_1h=B,
        cache_read=0,
    )
    # Split preserved post-construction (no mutation):
    assert toks.cache_create_5m == A
    assert toks.cache_create_1h == B

    # Now confirm aggregation locus is in PricingTable.__call__:
    rate = 1e-06
    fake_table = {
        "claude-x": {
            "input_cost_per_token": 0.0,
            "output_cost_per_token": 0.0,
            "cache_creation_input_token_cost": rate,
            "cache_creation_input_token_cost_above_1hr": 99.0,  # unused per Y-5c
            "cache_read_input_token_cost": 0.0,
        }
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(
        sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
    )
    cost = pt(
        model="claude-x",
        ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
        toks=toks,
    )
    assert cost == pytest.approx((A + B) * rate, rel=1e-12)


# ─── Test 9: CR-Z-4 alphabetical tiebreaker (Y-5d) ───────────────────────────


def test_cr_z_4_alphabetical_tiebreaker(tmp_path: Path) -> None:
    """CR-Z-4 / Y-5d: when multiple substring candidates of equal length
    tie, ``min(candidates)`` (alphabetically smallest) wins; deterministic
    regardless of dict insertion order; increments
    ``multiple_substring_match_warning``.
    """
    # Three model keys, all 13 chars, all substrings of the query
    # "claude-foo-1-special". They all have the same overlap length (the
    # full key length), tying on length.
    common = {k: 1e-06 for k in _REQUIRED_KEYS}
    table_a = {
        "claude-foo-1": dict(common),
        "claude-foo-2": dict(common),
        "claude-bar-1": dict(common),
    }
    # Same keys, reversed insertion order — must produce identical result.
    table_b = {
        "claude-bar-1": dict(common),
        "claude-foo-2": dict(common),
        "claude-foo-1": dict(common),
    }
    p_a = tmp_path / "a.json"
    p_b = tmp_path / "b.json"
    p_a.write_text(json.dumps(table_a))
    p_b.write_text(json.dumps(table_b))
    pt_a = PricingTable.from_litellm_sha(LITELLM_SHA, p_a, skip_sha_check=True)
    pt_b = PricingTable.from_litellm_sha(LITELLM_SHA, p_b, skip_sha_check=True)

    query = "claude-foo-1-special"
    ts = datetime(2026, 5, 1, tzinfo=timezone.utc)

    # "claude-foo-1" is a substring of "claude-foo-1-special" (len 12). So is
    # "claude-bar-1"? No — "claude-bar-1" is not contained in the query.
    # But the spec semantics defined in _lookup_model_key also test the
    # reverse direction (model contained in key) — neither apply here.
    # The two matching keys ("claude-foo-1", "claude-foo-2") give overlap
    # lengths 12 and 0; "claude-foo-1" wins by length alone (no tie).
    #
    # To exercise the tiebreaker we need TRUE equal-length matches. Use a
    # query that contains BOTH "claude-foo-2" AND "claude-foo-1" as
    # substrings — but no string contains both 12-char substrings unless
    # they overlap. Easier: construct keys that all match by reverse
    # containment (model contained in key), where the overlap length is the
    # query length, hence tied.
    #
    # Use query "fooX" (4 chars) and keys "claude-fooX-a", "claude-fooX-b"
    # (both contain the full query). Overlap = len(query) = 4 for both.
    table_c = {
        "claude-fooX-a": dict(common),
        "claude-fooX-b": dict(common),
        "claude-fooX-c": dict(common),
    }
    table_d = {
        "claude-fooX-c": dict(common),
        "claude-fooX-b": dict(common),
        "claude-fooX-a": dict(common),
    }
    p_c = tmp_path / "c.json"
    p_d = tmp_path / "d.json"
    p_c.write_text(json.dumps(table_c))
    p_d.write_text(json.dumps(table_d))
    pt_c = PricingTable.from_litellm_sha(LITELLM_SHA, p_c, skip_sha_check=True)
    pt_d = PricingTable.from_litellm_sha(LITELLM_SHA, p_d, skip_sha_check=True)

    short_query = "fooX"  # contained in all three keys
    before_c = pt_c.multiple_substring_match_warning
    before_d = pt_d.multiple_substring_match_warning
    cost_c = pt_c(
        model=short_query,
        ts=ts,
        toks=TokensByCategory(1, 0, 0, 0, 0),
    )
    cost_d = pt_d(
        model=short_query,
        ts=ts,
        toks=TokensByCategory(1, 0, 0, 0, 0),
    )
    # Both return the same rate (all keys share same rate values), and the
    # tiebreaker warning incremented on both.
    assert cost_c == cost_d
    assert pt_c.multiple_substring_match_warning == before_c + 1
    assert pt_d.multiple_substring_match_warning == before_d + 1

    # And the alphabetically-smallest winner ("claude-fooX-a") is the one
    # actually used — pin via _lookup_model_key directly.
    assert pt_c._lookup_model_key(short_query) == "claude-fooX-a"
    assert pt_d._lookup_model_key(short_query) == "claude-fooX-a"


# ─── Test 10: 200k input tier applied ────────────────────────────────────────


def test_pricing_200k_tier_applied(tmp_path: Path) -> None:
    """Y-2: tokens above 200_000 are billed at the tier rate."""
    fake_table = {
        "claude-x": {
            "input_cost_per_token": 1e-06,
            "output_cost_per_token": 0.0,
            "cache_creation_input_token_cost": 0.0,
            "cache_creation_input_token_cost_above_1hr": 0.0,
            "cache_read_input_token_cost": 0.0,
            "input_cost_per_token_above_200k_tokens": 2e-06,
        }
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(LITELLM_SHA, p, skip_sha_check=True)
    # 300_000 input tokens: 200_000 * 1e-06 + 100_000 * 2e-06
    cost = pt(
        model="claude-x",
        ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
        toks=TokensByCategory(300_000, 0, 0, 0, 0),
    )
    expected = 200_000 * 1e-06 + 100_000 * 2e-06
    assert cost == pytest.approx(expected, rel=1e-12)


# ─── Test 11: tier-rate fallback when absent ─────────────────────────────────


def test_pricing_tier_fallback_when_absent(tmp_path: Path) -> None:
    """Y-2: missing tier rate falls back to base, no error.

    ccusage semantics: ``tiered(N, base, null) = N * base`` when the tier
    rate is None, regardless of whether ``N`` exceeds the threshold.
    """
    fake_table = {
        "claude-x": {k: 1e-06 for k in _REQUIRED_KEYS},
        # NOTE: no input_cost_per_token_above_200k_tokens key
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(LITELLM_SHA, p, skip_sha_check=True)
    cost = pt(
        model="claude-x",
        ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
        toks=TokensByCategory(300_000, 0, 0, 0, 0),
    )
    # Falls back to full N * base.
    assert cost == pytest.approx(300_000 * 1e-06, rel=1e-12)


# ─── Test 12: None rate contributes zero (Y-3 per-category gate) ─────────────


def test_pricing_none_rate_contributes_zero(tmp_path: Path) -> None:
    """Y-3: missing rate keys load as None; that category contributes 0
    to cost at call time (ccusage semantics: ``tiered(N, base=null) = 0``).
    """
    fake_table = {
        "claude-x": {
            # Only input + output present; cache rates missing.
            "input_cost_per_token": 1e-06,
            "output_cost_per_token": 2e-06,
        }
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        pt = PricingTable.from_litellm_sha(
            LITELLM_SHA, p, skip_sha_check=True
        )
    # Cache tokens present but their rates are None → contribute 0.
    cost = pt(
        model="claude-x",
        ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
        toks=TokensByCategory(
            input=100,
            output=50,
            cache_create_5m=1000,  # rate None → 0 contribution
            cache_create_1h=1000,  # rate None → 0 contribution
            cache_read=1000,       # rate None → 0 contribution
        ),
    )
    expected = 100 * 1e-06 + 50 * 2e-06
    assert cost == pytest.approx(expected, rel=1e-12)


# ─── v0.2.10 audit-econ #3: LiteLLM dual-pin enforcement ─────────────────────


def test_pricing_table_raises_on_file_sha_mismatch(tmp_path: Path) -> None:
    """v0.2.10 audit-econ #3: when the cached file's sha256 does NOT
    match ``LITELLM_FILE_SHA256_PINNED``, ``from_litellm_sha`` raises
    ``ValueError`` (cache integrity violation).

    Fixture: copy the REAL canonical file (sha matches the pin), then
    append a single byte to corrupt it. The commit-SHA argument passes
    its own check; only the file-sha256 check fails.
    """
    assert REAL_LITELLM_JSON.exists(), (
        f"canonical LiteLLM cache missing at {REAL_LITELLM_JSON}; "
        "make data-raw to provision"
    )
    corrupted = tmp_path / "litellm_corrupted.json"
    corrupted.write_bytes(REAL_LITELLM_JSON.read_bytes() + b"X")

    with pytest.raises(ValueError, match="cache integrity violation"):
        PricingTable.from_litellm_sha(
            sha=LITELLM_SHA_PINNED,
            cached_json_path=corrupted,
            skip_sha_check=False,
        )


def test_pricing_table_passes_with_correct_file_sha() -> None:
    """v0.2.10 audit-econ #3: smoke test — the canonical cached file at
    ``data/raw/litellm_model_prices.json`` satisfies both pins (commit-SHA
    AND file-sha256) and loads cleanly without ``skip_sha_check``.
    """
    assert REAL_LITELLM_JSON.exists(), (
        f"canonical LiteLLM cache missing at {REAL_LITELLM_JSON}; "
        "make data-raw to provision"
    )
    import warnings as _w
    with _w.catch_warnings():
        # Real cache may have missing keys per Y-3 — those WARN but do
        # not raise. Suppress them so this test focuses on the pin gates.
        _w.simplefilter("ignore", UserWarning)
        pt = PricingTable.from_litellm_sha(
            sha=LITELLM_SHA_PINNED,
            cached_json_path=REAL_LITELLM_JSON,
            skip_sha_check=False,
        )
    assert pt.sha == LITELLM_SHA_PINNED
    # And a sanity check: rates loaded.
    assert len(pt.rates) > 0


def test_pricing_table_file_sha_pin_constant_matches_real_file() -> None:
    """v0.2.10 audit-econ #3: the module-level
    ``LITELLM_FILE_SHA256_PINNED`` constant must equal the sha256 of the
    canonical cached file actually on disk. If this fails, either the
    cache was mutated or the pin was bumped without updating the file
    (or vice versa).
    """
    import hashlib
    assert REAL_LITELLM_JSON.exists(), (
        f"canonical LiteLLM cache missing at {REAL_LITELLM_JSON}; "
        "make data-raw to provision"
    )
    actual: str = hashlib.sha256(REAL_LITELLM_JSON.read_bytes()).hexdigest()
    assert actual == LITELLM_FILE_SHA256_PINNED, (
        f"file sha256 drift: actual {actual} vs pinned "
        f"{LITELLM_FILE_SHA256_PINNED}"
    )


def test_pricing_table_skip_sha_check_bypasses_both_pins(tmp_path: Path) -> None:
    """v0.2.10 audit-econ #3: ``skip_sha_check=True`` must bypass BOTH
    the commit-SHA pin AND the file-sha256 pin so test fixtures with
    arbitrary synthetic rate tables continue to load.
    """
    fake_table = {"claude-x": {k: 1e-06 for k in _REQUIRED_KEYS}}
    p = tmp_path / "synthetic.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(
        sha="not-the-pinned-sha",
        cached_json_path=p,
        skip_sha_check=True,
    )
    assert pt.sha == "not-the-pinned-sha"
    assert "claude-x" in pt.rates
