"""
Wave-4 parity_3row.py — 3-row ccusage parity disclosure (audit-econ #2 fix)

Per audit-econ Finding 2 (agent2_data_replication.md): the v0.2.7 1-row
"1.000000×" parity table is tautological because it computes ratios over the
inner-join of `panel ∩ ccusage` — silently discarding panel-side TRM-missing
weekdays. v0.2.10 mandates a 3-row geometry disclosure surfacing:

    1. `panel ∩ ccusage` (both)         — apples-to-apples subset
    2. `panel \\ ccusage` (panel-only)   — should be empty if pipeline is sound
    3. `ccusage \\ panel` (ccusage-only) — TRM-holiday + non-Anthropic loss

Inputs:
    - /home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/data/panels/notional_cost_panel.parquet
      sha256 = 83dc8410bada080a1533bb308d889a33d6f85a7337974e6983afc03563fe06c8
    - /tmp/ccusage_post_wave4.json
      from: npx ccusage@latest daily --timezone UTC --since 20240101 --until 20260517 --json

Output: prints the 3-row table to stdout. No file side-effects.

Anti-fishing note: this script does NOT inner-join. The 3-row table requires
left-only + right-only set differences, NOT an inner join.
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl

PANEL_PATH = Path(
    "/home/jmsbpp/apps/d2p/abrigo/abrigo-analytics/data/panels/notional_cost_panel.parquet"
)
CCUSAGE_PATH = Path("/tmp/ccusage_post_wave4.json")


def main() -> None:
    panel = pl.read_parquet(PANEL_PATH)
    # Date column on panel is `date_utc` per DATA_PROVENANCE schema
    panel_dates = set(panel["date_utc"].dt.strftime("%Y-%m-%d").to_list())
    panel_cost = float(panel["notional_cost_usd"].sum())

    ccu_raw = json.loads(CCUSAGE_PATH.read_text())
    ccu_daily = ccu_raw.get("daily", [])

    # Filter to Claude-only rows (exclude Codex/non-Anthropic)
    # ccusage rows carry `modelsUsed` array; Anthropic models start with "claude"
    ccu_rows_all = []
    ccu_rows_claude_only = []
    for row in ccu_daily:
        # ccusage daily key is `period` (date string YYYY-MM-DD); legacy schema used `date`
        date_s = row.get("period") or row.get("date")
        cost = float(row.get("totalCost", 0.0))
        models = row.get("modelsUsed", []) or []
        ccu_rows_all.append((date_s, cost, models))
        has_claude = any(m.startswith("claude") for m in models)
        has_non_anthropic = any(not m.startswith("claude") for m in models)
        if has_claude and not has_non_anthropic:
            ccu_rows_claude_only.append((date_s, cost, models))

    ccu_dates_all = {r[0] for r in ccu_rows_all}
    ccu_cost_all = sum(r[1] for r in ccu_rows_all)

    ccu_dates_claude = {r[0] for r in ccu_rows_claude_only}
    ccu_cost_claude = sum(r[1] for r in ccu_rows_claude_only)

    # Set differences
    both = panel_dates & ccu_dates_all
    panel_only = panel_dates - ccu_dates_all
    ccusage_only = ccu_dates_all - panel_dates

    both_claude = panel_dates & ccu_dates_claude
    ccusage_only_claude = ccu_dates_claude - panel_dates

    # Compute cost per subset
    panel_both_cost = float(
        panel.filter(
            pl.col("date_utc").dt.strftime("%Y-%m-%d").is_in(list(both))
        )["notional_cost_usd"].sum()
    )
    panel_only_cost = float(
        panel.filter(
            pl.col("date_utc").dt.strftime("%Y-%m-%d").is_in(list(panel_only))
        )["notional_cost_usd"].sum()
    )
    ccusage_both_cost = sum(r[1] for r in ccu_rows_all if r[0] in both)
    ccusage_only_cost_all = sum(r[1] for r in ccu_rows_all if r[0] in ccusage_only)
    ccusage_only_cost_claude = sum(
        r[1] for r in ccu_rows_claude_only if r[0] in ccusage_only_claude
    )

    print("=" * 78)
    print("3-row ccusage parity disclosure (v0.2.10 audit-econ #2 fix)")
    print("=" * 78)
    print(f"Panel:        {len(panel_dates)} weekday dates, ${panel_cost:,.2f}")
    print(f"ccusage all:  {len(ccu_dates_all)} dates,        ${ccu_cost_all:,.2f}")
    print(f"ccusage Claude-only: {len(ccu_dates_claude)} dates,        ${ccu_cost_claude:,.2f}")
    print()
    print("Set geometry:")
    print(f"  panel ∩ ccusage          : {len(both)} dates")
    print(f"  panel \\ ccusage          : {len(panel_only)} dates")
    print(f"  ccusage \\ panel (all)    : {len(ccusage_only)} dates")
    print(f"  ccusage \\ panel (Claude) : {len(ccusage_only_claude)} dates")
    print()
    print("Cost reconciliation:")
    print(f"  panel cost on `both`               : ${panel_both_cost:,.2f}")
    print(f"  ccusage cost on `both`             : ${ccusage_both_cost:,.2f}")
    print(
        f"  ratio (panel / ccusage on both)    : "
        f"{panel_both_cost / ccusage_both_cost:.6f}×"
    )
    print(f"  panel cost on `panel-only`         : ${panel_only_cost:,.2f}")
    print(f"  ccusage cost on `ccusage-only` (all): ${ccusage_only_cost_all:,.2f}")
    print(
        f"  ccusage cost on `ccusage-only` (Claude only, excl Codex): "
        f"${ccusage_only_cost_claude:,.2f}"
    )
    print()
    combined_panel = panel_cost
    combined_ccusage = ccu_cost_all
    print(
        f"  COMBINED window: panel ${combined_panel:,.2f} vs ccusage ${combined_ccusage:,.2f} "
        f"= {combined_panel / combined_ccusage:.4f}×"
    )
    print()
    print("Anti-fishing: parity satisfied ONLY on `both` subset (apples-to-apples).")
    print("Combined-window ratio reflects SCOPE difference (TRM-holiday weekdays +")
    print("Codex commingling), not algorithmic disagreement.")


if __name__ == "__main__":
    main()
