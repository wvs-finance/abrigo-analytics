"""modules-tier pure Callable: notional USD cost from token counts.

Spec ref: ``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.3 §3.5
+ §0.3 CORRECTIONS-Y-2/-Y-3 + Y-5a/c/d. Replaces v0.2.1 Decimal-exact
arithmetic with ccusage-parity float arithmetic (Y-2). All rate fields are
``Optional[float] = None`` (Y-3); the model-lookup ladder
exact → ``anthropic/<model>`` → longest-substring with alphabetical
tiebreaker (Y-5d) drives lookup at call time.

Tier rule: ``modules/`` may import ``types/`` but NOT ``utils/`` nor
``_errors``. ``PricingTable`` performs a single bounded JSON read at
construction (via ``Path.read_bytes`` in the classmethod); the resulting
instance is a frozen-slots dataclass with immutable ``MappingProxyType`` rate
dicts. ``__call__`` is purely arithmetic — no IO, no mutation.

ccusage parity (CORRECTIONS-Y-2): the per-category cost formula matches
``calculateTieredCost`` from the ccusage TypeScript reference. Tiered pricing
for ``input_tokens`` on ``claude-*`` models uses the 200_000-token boundary:
the first 200k tokens are billed at ``input_cost_per_token``; tokens above
that are billed at ``input_cost_per_token_above_200k_tokens`` when present
(fall back to base rate when absent — no error). Per-category gating: if a
required rate is ``None``, the category contributes ``0`` to the cost
(``tiered(N, base, null) = 0``).

Cache aggregation locus (CR-Z-3 / Y-5c): ``__call__`` reads
``toks.cache_create_5m + toks.cache_create_1h`` and multiplies by the single
``cache_creation_input_token_cost`` rate. ``TokensByCategory`` preserves the
split intact for diagnostic-only consumers; aggregation does NOT happen at
the Value tier.

Counter ownership (Y-5a): the table carries three int counters:
``WARN_missing_keys_count``, ``dropped_unknown_model_count``,
``multiple_substring_match_warning``. The JSONL-side counter
``dropped_non_assistant_count`` lives on ``JSONLReadResult`` (types tier).
"""
from __future__ import annotations

import hashlib
import json
import warnings
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from types import MappingProxyType

from simulations.dev_ai_cost_v2.types import TokensByCategory


# ─── Pinned LiteLLM rate-card constants ──────────────────────────────────────
#
# v0.2.3 (CORRECTIONS-Y-3): the previous Wave 1 RC hint (every key required at
# load time) is relaxed. Missing keys WARN and increment
# ``WARN_missing_keys_count``; the call-time per-category gate treats
# ``None`` rates as 0 (ccusage semantics).

_REQUIRED_KEYS: tuple[str, ...] = (
    "input_cost_per_token",
    "output_cost_per_token",
    "cache_creation_input_token_cost",
    "cache_creation_input_token_cost_above_1hr",
    "cache_read_input_token_cost",
)

# Tier-pricing key per Anthropic / LiteLLM (200k-token input boundary).
_INPUT_TIER_KEY: str = "input_cost_per_token_above_200k_tokens"
_INPUT_TIER_THRESHOLD: int = 200_000

LITELLM_SHA_PINNED: str = "e58a561caa21169fb02174148444c08509ce7028"

# v0.2.10 audit-econ #3: sha256 of the cached
# ``data/raw/litellm_model_prices.json`` file BYTES, computed at the same
# upstream commit as ``LITELLM_SHA_PINNED``. The commit-SHA pin documents
# UPSTREAM LINEAGE (which LiteLLM release the rates came from); the file
# sha256 pin documents LOCAL CACHE INTEGRITY (the bytes on disk have not
# been mutated since the snapshot). The two are distinct concerns and are
# checked independently in ``PricingTable.from_litellm_sha``.
LITELLM_FILE_SHA256_PINNED: str = (
    "05b050523e4c71581a12605c4bc49cf7049bafe3f51e1506b9da61afb9791db9"
)


# ─── ModelRates value type ───────────────────────────────────────────────────
#
# Stored as a plain ``MappingProxyType`` of ``str -> float | None``; chosen
# over a dataclass to keep the table memory footprint small at load time
# (45+ claude-* models × 6 rate fields). Per Y-3, every rate field is
# Optional[float]; ``None`` denotes a key absent from the LiteLLM SHA.


# ─── PricingTable ────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class PricingTable:
    """Frozen rate-card lookup: ``(model, ts, toks) -> float USD cost``.

    Fields:
        rates: nested immutable mapping
            ``{model: {key: Optional[float] rate}}`` (``MappingProxyType`` at
            both levels). Only ``claude-*`` models are retained at load time.
            Every key in ``_REQUIRED_KEYS + (_INPUT_TIER_KEY,)`` is present
            in each inner mapping; absent rates surface as ``None``.
        sha: the LiteLLM commit SHA the rate card was loaded at. Pinned by
            ``LITELLM_SHA_PINNED`` for reproducibility audits.
        WARN_missing_keys_count: number of ``(model, key)`` absences observed
            at load time (Y-5a / CR-Z-1). Each absence WARNs via
            ``warnings.warn`` and increments this counter; load does NOT
            raise.
        dropped_unknown_model_count: number of call-time lookups that
            exhausted the model-lookup ladder (Y-5a). Surfaced by the
            panel-builder into ``DailyNotionalPanel``.
        multiple_substring_match_warning: number of call-time lookups where
            multiple longest-substring candidates of equal length tied
            (Y-5d). The tiebreaker is ``min(candidates)`` (alphabetically
            smallest) for determinism.

    Invariants:
        - ``rates`` is immutable (``MappingProxyType``) — load-time only.
        - The three counter fields are mutated via ``object.__setattr__``
          on a frozen-slots instance. This is the documented exception for
          modules-tier-owned counters: ``PricingTable`` is the only
          modules-tier dc that carries mutable state, and the mutation is
          confined to bookkeeping (no rate or model-id is altered after
          construction).
    """

    rates: Mapping[str, Mapping[str, float | None]]
    sha: str
    WARN_missing_keys_count: int = field(default=0)
    dropped_unknown_model_count: int = field(default=0)
    multiple_substring_match_warning: int = field(default=0)

    @classmethod
    def from_litellm_sha(
        cls,
        sha: str,
        cached_json_path: Path,
        *,
        skip_sha_check: bool = False,
    ) -> "PricingTable":
        """Load the cached LiteLLM ``model_prices_and_context_window.json``.

        v0.2.3 (CORRECTIONS-Y-3): load is permissive. All rate fields are
        ``Optional[float]``. Missing keys WARN and increment
        ``WARN_missing_keys_count``; the loader does NOT raise on absences.
        Per CORRECTIONS-V, the ``ts`` argument on ``__call__`` is a sentinel
        for multi-step dispatch; v0.2.3 single-snapshot loads accept ``ts``
        without altering lookup.

        v0.2.10 audit-econ #3: DUAL-PIN ENFORCEMENT. The previous
        implementation checked only the caller-supplied commit-SHA
        argument against ``LITELLM_SHA_PINNED``; the file BYTES on disk
        were never hashed. A mutated cache (manual edit, partial write,
        accidental overwrite) would load silently. The fix adds a second
        independent check: compute ``hashlib.sha256(raw).hexdigest()`` of
        the file bytes and compare to ``LITELLM_FILE_SHA256_PINNED``.
        Both pins are enforced unless ``skip_sha_check=True`` (test
        escape hatch). The two pins document different concerns —
        commit-SHA = upstream lineage; file-SHA256 = local cache integrity.

        Args:
            sha: LiteLLM commit SHA. Must equal ``LITELLM_SHA_PINNED`` unless
                ``skip_sha_check``.
            cached_json_path: filesystem path to the cached LiteLLM JSON
                blob (``Path.read_bytes`` is the single IO call).
            skip_sha_check: testing escape hatch. When ``True``, BOTH the
                commit-SHA AND the file-SHA256 comparisons are bypassed
                (so test fixtures with synthetic tables can be loaded).
                Production callers MUST pass ``False`` (the default).

        Returns:
            A frozen ``PricingTable`` with ``MappingProxyType`` rate
            mappings. ``WARN_missing_keys_count`` reflects the per-model
            per-required-key absences seen at load.

        Raises:
            ValueError: when ``skip_sha_check`` is ``False`` and either
                (a) the supplied ``sha`` does not equal
                ``LITELLM_SHA_PINNED``, or (b) the sha256 of the file
                bytes does not equal ``LITELLM_FILE_SHA256_PINNED``.

        Errors from external state:
            FileNotFoundError: when ``cached_json_path`` does not exist.
            json.JSONDecodeError: when the cached file is not valid JSON.
            OSError: for other filesystem read failures.

        Silenced errors:
            None. Non-dict and non-``claude-*`` entries in the source JSON
            are filtered (the v0.2.3 spec scopes the panel to Anthropic);
            this is a *filter*, not a swallowed error. Missing required
            keys are WARNed and counted, not silenced.
        """
        raw: bytes = cached_json_path.read_bytes()
        if not skip_sha_check:
            # Pin 1: upstream commit-SHA (caller-supplied) must match.
            if sha != LITELLM_SHA_PINNED:
                raise ValueError(
                    f"PricingTable refuses load: requested SHA {sha} != "
                    f"pinned {LITELLM_SHA_PINNED}"
                )
            # Pin 2 (v0.2.10 audit-econ #3): file-bytes sha256 must match
            # ``LITELLM_FILE_SHA256_PINNED``. Distinct from the commit-SHA
            # pin: commit-SHA = upstream lineage; file-SHA256 = local
            # cache integrity. Both checks are required.
            file_digest: str = hashlib.sha256(raw).hexdigest()
            if file_digest != LITELLM_FILE_SHA256_PINNED:
                raise ValueError(
                    f"PricingTable refuses load: cached file sha256 "
                    f"{file_digest} != pinned "
                    f"{LITELLM_FILE_SHA256_PINNED} "
                    f"(local cache integrity violation at "
                    f"{cached_json_path})"
                )

        table = json.loads(raw)
        out: dict[str, Mapping[str, float | None]] = {}
        warn_count: int = 0
        for model, rates in table.items():
            if not model.startswith("claude-"):
                continue
            if not isinstance(rates, dict):
                continue
            entry: dict[str, float | None] = {}
            for k in _REQUIRED_KEYS:
                if k in rates:
                    entry[k] = float(rates[k])
                else:
                    entry[k] = None
                    warn_count += 1
                    warnings.warn(
                        f"PricingTable load: model {model!r} missing key {k!r}; "
                        f"category will contribute 0 at call time",
                        UserWarning,
                        stacklevel=2,
                    )
            # 200k-tier key is optional (CORRECTIONS-Y-2: fall back to base
            # rate when absent — no error, no WARN).
            entry[_INPUT_TIER_KEY] = (
                float(rates[_INPUT_TIER_KEY])
                if _INPUT_TIER_KEY in rates
                else None
            )
            out[model] = MappingProxyType(entry)
        return cls(
            rates=MappingProxyType(out),
            sha=sha,
            WARN_missing_keys_count=warn_count,
        )

    def _lookup_model_key(self, model: str) -> str | None:
        """Resolve a model id to a key in ``self.rates``.

        Ladder (Y-5d):
          1. Exact match.
          2. ``anthropic/<model>`` prefix match.
          3. Longest-substring overlap; alphabetically-smallest key wins on
             tie (``min(candidates)``); a tied tiebreaker increments
             ``multiple_substring_match_warning``.

        Returns ``None`` if all three rungs fail. Caller increments
        ``dropped_unknown_model_count``.
        """
        if model in self.rates:
            return model
        prefixed = f"anthropic/{model}"
        if prefixed in self.rates:
            return prefixed

        # Substring overlap: pick keys that share a contiguous overlap with
        # ``model`` either way (``key in model`` or ``model in key``). Score
        # by overlap length; tie → alphabetically smallest.
        candidates: list[tuple[int, str]] = []
        for key in self.rates:
            if key in model:
                candidates.append((len(key), key))
            elif model in key:
                candidates.append((len(model), key))
        if not candidates:
            return None
        best_len = max(c[0] for c in candidates)
        tied = sorted(k for ln, k in candidates if ln == best_len)
        if len(tied) > 1:
            object.__setattr__(
                self,
                "multiple_substring_match_warning",
                self.multiple_substring_match_warning + 1,
            )
        return tied[0]

    @staticmethod
    def _tiered(n: int, base: float | None, tier_rate: float | None,
                threshold: int) -> float:
        """ccusage ``calculateTieredCost`` semantics for one category.

        Returns ``0.0`` if ``base`` is ``None`` (per-category gate). For
        ``n <= threshold`` returns ``n * base``. For ``n > threshold``
        returns ``threshold * base + (n - threshold) * tier_rate`` if
        ``tier_rate`` is present, else falls back to ``n * base``
        (CORRECTIONS-Y-2: tier-rate absence is a soft fallback, not an
        error).
        """
        if base is None:
            return 0.0
        if n <= threshold:
            return float(n) * base
        excess = n - threshold
        if tier_rate is None:
            return float(n) * base
        return float(threshold) * base + float(excess) * tier_rate

    @staticmethod
    def _flat(n: int, rate: float | None) -> float:
        """Flat per-token cost with per-category None gate."""
        if rate is None:
            return 0.0
        return float(n) * rate

    def __call__(
        self,
        model: str,
        ts: datetime,
        toks: TokensByCategory,
    ) -> float:
        """Notional USD cost for one message using ccusage-parity float math.

        Per CORRECTIONS-Y-2: float arithmetic (not Decimal). Per Y-5c the
        ``cache_create_5m + cache_create_1h`` aggregation happens here, not
        in ``TokensByCategory.__init__``. Per Y-5d the model-lookup ladder
        is exact → ``anthropic/<model>`` prefix → longest-substring
        (alphabetical tiebreaker).

        Args:
            model: Anthropic model identifier. Lookup ladder per Y-5d. If
                the ladder exhausts (no rates for the model), returns
                ``0.0`` and increments ``dropped_unknown_model_count``.
            ts: timezone-aware UTC datetime of the message (sentinel for
                future time-varying lookups; not used in v0.2.3
                single-snapshot mode).
            toks: per-category token counts.

        Returns:
            ``float`` USD cost. Non-negative.

        Raises:
            None. v0.2.3 unknown-model lookup is non-fatal (Y-5d
            tiebreaker + Y-3 per-category gate handle absences gracefully);
            the operator sees the count via
            ``dropped_unknown_model_count``.
        """
        del ts  # sentinel for future multi-step dispatch — see docstring.
        key = self._lookup_model_key(model)
        if key is None:
            object.__setattr__(
                self,
                "dropped_unknown_model_count",
                self.dropped_unknown_model_count + 1,
            )
            return 0.0
        r = self.rates[key]
        # Y-5c: aggregate 5m + 1h at the call site.
        cache_create_total = toks.cache_create_5m + toks.cache_create_1h
        # Y-2: 200k-tier for input_tokens.
        input_cost = self._tiered(
            toks.input,
            r["input_cost_per_token"],
            r[_INPUT_TIER_KEY],
            _INPUT_TIER_THRESHOLD,
        )
        return (
            input_cost
            + self._flat(toks.output, r["output_cost_per_token"])
            + self._flat(
                cache_create_total, r["cache_creation_input_token_cost"]
            )
            + self._flat(toks.cache_read, r["cache_read_input_token_cost"])
        )


__all__ = [
    "LITELLM_SHA_PINNED",
    "PricingTable",
]
