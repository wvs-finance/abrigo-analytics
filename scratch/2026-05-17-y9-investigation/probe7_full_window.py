"""Get production reader totals on the FULL window for direct comparison
to my simulator's full-window totals."""
from __future__ import annotations
import warnings
from datetime import date
from pathlib import Path

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
)
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader

REPO = Path(__file__).resolve().parents[2]
pricing = PricingTable.from_litellm_sha(
    LITELLM_SHA_PINNED,
    cached_json_path=REPO / "data" / "raw" / "litellm_model_prices.json",
)
reader = JSONLReader(pricing=pricing)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    result = reader(date(2024, 1, 1), date(2026, 5, 17))

# Counters
print("--- JSONLReadResult counters ---")
print(f"records              : {len(result.records):,}")
print(f"dropped_non_assistant: {result.dropped_non_assistant_count:,}")
print(f"dropped_malformed    : {result.dropped_malformed_line_count:,}")
print(f"dropped_duplicate    : {result.dropped_duplicate_count:,}")

# Aggregate non-error
total_in = total_out = total_cc = total_cr = 0
n_err = 0
for r in result.records:
    if r.is_error:
        n_err += 1
        continue
    total_in += r.input_tok
    total_out += r.output_tok
    total_cc += r.cache_create_5m + r.cache_create_1h
    total_cr += r.cache_read

print(f"is_error rows        : {n_err:,}")
print(f"non-error records    : {len(result.records) - n_err:,}")
print(f"--- Totals (non-error, full window) ---")
print(f"input  : {total_in:>14,}")
print(f"output : {total_out:>14,}")
print(f"cc     : {total_cc:>14,}")
print(f"cr     : {total_cr:>14,}")
