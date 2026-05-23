"""Per-day comparison between our parquet and ccusage daily output on the
27-weekday overlap, with per-row drill-down on the biggest divergence day.
"""
from __future__ import annotations
import json
from pathlib import Path
import polars as pl

OUR = pl.read_parquet("data/panels/notional_cost_panel.parquet")
ccu_json = json.loads(Path("/tmp/ccusage_post_y9.json").read_text())["daily"]

ccu = pl.DataFrame([{
    "date_utc": r["period"],
    "ccu_in": r["inputTokens"],
    "ccu_out": r["outputTokens"],
    "ccu_cc": r["cacheCreationTokens"],
    "ccu_cr": r["cacheReadTokens"],
} for r in ccu_json])

ours = OUR.with_columns(pl.col("date_utc").cast(pl.Utf8).alias("d_s"))
ccu = ccu.with_columns(pl.col("date_utc").alias("d_s"))

joined = ours.join(ccu.drop("date_utc"), on="d_s", how="inner")
joined = joined.with_columns([
    (pl.col("cache_create_5m") + pl.col("cache_create_1h")).alias("our_cc"),
    (pl.col("input_tok") - pl.col("ccu_in")).alias("d_in"),
    (pl.col("output_tok") - pl.col("ccu_out")).alias("d_out"),
])
joined = joined.with_columns(
    (pl.col("our_cc") - pl.col("ccu_cc")).alias("d_cc"),
    (pl.col("cache_read") - pl.col("ccu_cr")).alias("d_cr"),
)

print("Per-day deltas (ours - ccusage) sorted by |d_in|:")
sel = joined.select([
    "date_utc", "input_tok", "ccu_in", "d_in",
    "output_tok", "ccu_out", "d_out",
    "d_cc", "d_cr",
]).sort(pl.col("d_in").abs(), descending=True)
print(sel.to_pandas().to_string(index=False))
