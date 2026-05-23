"""Dump production JSONLReader kept rows and compare to a simulated
ccusage replay on the same data, restricted to the 27-weekday overlap.
"""
from __future__ import annotations
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
import polars as pl

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
)
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader

REPO = Path(__file__).resolve().parents[2]
SINCE = date(2024, 1, 1)
UNTIL = date(2026, 5, 17)

# Production JSONLReader (real code path)
pricing = PricingTable.from_litellm_sha(
    LITELLM_SHA_PINNED,
    cached_json_path=REPO / "data" / "raw" / "litellm_model_prices.json",
)
reader = JSONLReader(pricing=pricing)
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    result = reader(SINCE, UNTIL)

# Aggregate by date (UTC) post-dedup, no weekend filter (mirror probe3)
ours_daily = defaultdict(lambda: [0, 0, 0, 0, 0])  # in, out, cc, cr, n
for r in result.records:
    if r.is_error:
        continue
    d = r.ts.date().isoformat()
    ours_daily[d][0] += r.input_tok
    ours_daily[d][1] += r.output_tok
    ours_daily[d][2] += r.cache_create_5m + r.cache_create_1h
    ours_daily[d][3] += r.cache_read
    ours_daily[d][4] += 1

# Read ccusage output
ccu_json = json.loads(Path("/tmp/ccusage_post_y9.json").read_text())["daily"]
ccu_daily = {r["period"]: (
    r["inputTokens"], r["outputTokens"], r["cacheCreationTokens"], r["cacheReadTokens"]
) for r in ccu_json}

# Restrict to overlap weekdays (which is what production parquet uses)
parquet = pl.read_parquet("data/panels/notional_cost_panel.parquet")
overlap_dates = [d.isoformat() for d in parquet["date_utc"].to_list()]
print(f"Overlap (27 weekdays): {len(overlap_dates)}")

o_in = o_out = o_cc = o_cr = o_n = 0
c_in = c_out = c_cc = c_cr = 0
for d in overlap_dates:
    if d in ours_daily:
        v = ours_daily[d]
        o_in += v[0]; o_out += v[1]; o_cc += v[2]; o_cr += v[3]; o_n += v[4]
    if d in ccu_daily:
        v = ccu_daily[d]
        c_in += v[0]; c_out += v[1]; c_cc += v[2]; c_cr += v[3]

print(f"Production reader on overlap (no weekend filter, no TRM join):")
print(f"  input  : {o_in:,}")
print(f"  output : {o_out:,}")
print(f"  cc     : {o_cc:,}")
print(f"  cr     : {o_cr:,}")
print(f"  n_msg  : {o_n:,}")
print(f"ccusage on overlap:")
print(f"  input  : {c_in:,}")
print(f"  output : {c_out:,}")
print(f"  cc     : {c_cc:,}")
print(f"  cr     : {c_cr:,}")
print(f"DELTAS (ours - ccusage):")
print(f"  input  : {o_in - c_in:+,}")
print(f"  output : {o_out - c_out:+,}")
print(f"  cc     : {o_cc - c_cc:+,}")
print(f"  cr     : {o_cr - c_cr:+,}")
