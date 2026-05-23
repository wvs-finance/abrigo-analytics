"""Compute per-class ratios on the 27-weekday overlap between our pipeline
and ccusage. Reports apples-to-apples (date-intersection)."""
from __future__ import annotations
import json
from pathlib import Path
import polars as pl

OUR_PANEL = Path("data/panels/notional_cost_panel.parquet")
CCU_JSON = Path("/tmp/ccusage_post_y9.json")

ours = pl.read_parquet(OUR_PANEL)
print("Our panel columns:", ours.columns)
print("Our panel rows:", len(ours))
print(ours.head(3))

ccu = json.loads(CCU_JSON.read_text())["daily"]
print("ccusage daily rows:", len(ccu))
ccu_df = pl.DataFrame([
    {
        "date": r["period"],
        "ccu_input": r["inputTokens"],
        "ccu_output": r["outputTokens"],
        "ccu_cc": r["cacheCreationTokens"],
        "ccu_cr": r["cacheReadTokens"],
        "ccu_cost": r["totalCost"],
    }
    for r in ccu
    if r.get("agent") in ("all", None) or "agent" not in r
])
# Cast our date col to string
ours_norm = ours.with_columns(pl.col("date_utc").cast(pl.Utf8).alias("date_s"))
print("Sample our dates:", ours_norm.select("date_s").head(5).to_series().to_list())
print("Sample ccu dates:", ccu_df.select("date").head(5).to_series().to_list())

joined = ours_norm.join(ccu_df, left_on="date_s", right_on="date", how="inner")
print("\nOVERLAP rows:", len(joined))
print(joined.columns)

# Identify our token columns
# Typical schema from prior runs: cost_usd, input_tokens, output_tokens,
# cache_create_5m, cache_create_1h, cache_read
cols = joined.columns
our_input = "input_tokens" if "input_tokens" in cols else "input_tok"
our_output = "output_tokens" if "output_tokens" in cols else "output_tok"
if "cost_usd" in cols:
    our_cost = "cost_usd"
elif "cost_usd_notional" in cols:
    our_cost = "cost_usd_notional"
elif "notional_cost_usd" in cols:
    our_cost = "notional_cost_usd"
else:
    our_cost = "cost"
# cache_create sum
cc_cols = [c for c in cols if c.startswith("cache_create")]
print("cache_create cols:", cc_cols)
our_cr = "cache_read" if "cache_read" in cols else "cache_read_tokens"

summary = joined.select(
    pl.col(our_cost).sum().alias("our_cost"),
    pl.col("ccu_cost").sum().alias("ccu_cost"),
    pl.col(our_input).sum().alias("our_input"),
    pl.col("ccu_input").sum().alias("ccu_input"),
    pl.col(our_output).sum().alias("our_output"),
    pl.col("ccu_output").sum().alias("ccu_output"),
    sum(pl.col(c) for c in cc_cols).sum().alias("our_cc"),
    pl.col("ccu_cc").sum().alias("ccu_cc"),
    pl.col(our_cr).sum().alias("our_cr"),
    pl.col("ccu_cr").sum().alias("ccu_cr"),
)
print("\n=== Aggregate on overlap ===")
print(summary)

row = summary.row(0, named=True)
print("\n=== Per-class ratios (ours / ccusage) ===")
for k in ("cost", "input", "output", "cc", "cr"):
    ours_v = row[f"our_{k}"]
    ccu_v = row[f"ccu_{k}"]
    if ccu_v == 0:
        print(f"  {k:6s}: ours={ours_v}  ccu={ccu_v}  ratio=N/A")
    else:
        r = ours_v / ccu_v
        diff_pct = (r - 1) * 100
        print(f"  {k:6s}: ours={ours_v:>14,.2f}  ccu={ccu_v:>14,.2f}  ratio={r:.6f}  ({diff_pct:+.3f}%)")
