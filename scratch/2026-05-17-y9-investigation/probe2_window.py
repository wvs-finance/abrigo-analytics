"""Y-9 H7: window-vs-dedup ordering divergence.

Hypothesis: ccusage dedupes GLOBALLY (all rows, all dates) and then filters
by --since/--until at the daily aggregation step. Our pipeline filters by
window FIRST (rejects rows outside window) and then dedupes within the
admitted set. This means duplicates split across the window boundary are
handled differently:

  Scenario A: Row R1 (in-window, large tokenTotal) + Row R2 (out-of-window,
              smaller tokenTotal), same uniqueHash.
              ccusage: keeps R1 (larger tt), aggregates into daily totals → R1.
              Ours: only sees R1 (R2 filtered out), aggregates R1.
              IDENTICAL.

  Scenario B: Row R1 (in-window, smaller tt) + Row R2 (out-of-window, larger tt),
              same uniqueHash.
              ccusage: keeps R2 globally; R2 is outside window → daily totals
              EXCLUDE R2's contribution AND don't include R1 (the in-window
              row was dropped by dedup).
              Ours: only sees R1 (R2 filtered out), aggregates R1.
              OURS reports R1; ccusage reports NOTHING.

  Scenario C: Both rows in-window. Identical.

Probe: count Scenario B occurrences and quantify the per-token-class impact.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any

PROJECTS_ROOT = Path.home() / ".claude" / "projects"
SINCE = date(2024, 1, 1)
UNTIL = date(2026, 5, 17)


def ccusage_admit(raw: dict[str, Any]) -> bool:
    msg = raw.get("message")
    if not isinstance(msg, dict):
        return False
    mid = msg.get("id")
    if not isinstance(mid, str) or mid == "":
        return False
    rid = raw.get("requestId")
    if rid is not None and (not isinstance(rid, str) or rid == ""):
        return False
    err = raw.get("isApiErrorMessage")
    if err is True:
        return False
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return False
    if not isinstance(usage.get("input_tokens"), int):
        return False
    if not isinstance(usage.get("output_tokens"), int):
        return False
    speed = usage.get("speed")
    if speed is not None and speed not in ("standard", "fast"):
        return False
    return True


def unique_hash(msg_id: str | None, req_id: str | None) -> str | None:
    if not msg_id:
        return None
    return msg_id if req_id is None else f"{msg_id}:{req_id}"


def in_window(ts_str: str) -> bool:
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return False
    if ts.tzinfo is None:
        return False
    ts_utc = ts.astimezone(timezone.utc)
    lo = datetime.combine(SINCE, time.min, tzinfo=timezone.utc)
    hi = datetime.combine(UNTIL, time.min, tzinfo=timezone.utc)
    return lo <= ts_utc < hi


def token_total_flat(u: dict[str, Any]) -> int:
    return (
        u["input_tokens"]
        + u["output_tokens"]
        + (u.get("cache_creation_input_tokens") or 0)
        + (u.get("cache_read_input_tokens") or 0)
    )


def main() -> None:
    # Collect all ccusage-admitted assistant rows with timestamps; tag in/out.
    # Group by uniqueHash; for each hash, compute who ccusage keeps (global)
    # vs who ours keeps (in-window only).

    # rows[h] = list of (in_window, tt, hasSpeed, usage, ts_str)
    rows: dict[str, list[tuple[bool, int, bool, dict, str]]] = defaultdict(list)
    total_assistant_admitted = 0
    in_window_admitted = 0

    for jp in PROJECTS_ROOT.rglob("*.jsonl"):
        try:
            with jp.open() as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        continue
                    try:
                        raw = json.loads(s)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(raw, dict):
                        continue
                    if raw.get("type") != "assistant":
                        continue
                    if not ccusage_admit(raw):
                        continue
                    total_assistant_admitted += 1
                    ts = raw.get("timestamp")
                    if not isinstance(ts, str):
                        continue
                    iw = in_window(ts)
                    if iw:
                        in_window_admitted += 1
                    msg = raw["message"]
                    u = msg["usage"]
                    h = unique_hash(msg.get("id"), raw.get("requestId"))
                    if h is None:
                        continue
                    tt = token_total_flat(u)
                    hs = u.get("speed") is not None
                    rows[h].append((iw, tt, hs, u, ts))
        except OSError:
            continue

    # Replay ccusage: keep best globally (by $(new,old)).
    # Replay ours: keep best among in-window only.
    # Scenario B = hash where the global winner is OUT-of-window AND there
    # exists an in-window row. ccusage excludes; ours includes.
    # Scenario D = hash where global winner is IN-window but DIFFERENT row
    # than the in-window-only winner (only possible if "best in-window" !=
    # "best globally" — impossible since global ⊇ in-window restricted).
    #   Actually: if global winner IS in-window, then both pipelines keep it.
    #   If global winner is OUT-of-window: ccusage drops the whole hash;
    #     ours keeps the best in-window row.

    scenario_a_or_c = 0  # global winner in-window — both agree
    scenario_b = 0  # global winner out-of-window — ours includes an in-window row
    scenario_b_input = 0
    scenario_b_output = 0
    scenario_b_cc = 0  # flat
    scenario_b_cr = 0
    # Also: ours_only "extra input" = sum of in-window rows our pipeline
    # contributes that ccusage drops.

    # And impact for hashes with NO in-window row but global winner out-of-window:
    # both report nothing — skip.

    for h, entries in rows.items():
        # Find global winner via ccusage $
        ge = entries[0]
        for cand in entries[1:]:
            if cand[1] > ge[1] or (cand[1] == ge[1] and cand[2] and not ge[2]):
                ge = cand
        # Find in-window winner via ours (same $ rule)
        in_entries = [e for e in entries if e[0]]
        if not in_entries:
            continue  # no in-window row at all — both report nothing
        oe = in_entries[0]
        for cand in in_entries[1:]:
            if cand[1] > oe[1] or (cand[1] == oe[1] and cand[2] and not oe[2]):
                oe = cand

        if ge[0]:  # global winner in-window
            # Both pipelines should keep ge (same selection)
            scenario_a_or_c += 1
        else:  # global winner out-of-window → ccusage drops hash entirely
            scenario_b += 1
            u = oe[3]
            scenario_b_input += u["input_tokens"]
            scenario_b_output += u["output_tokens"]
            scenario_b_cc += u.get("cache_creation_input_tokens") or 0
            scenario_b_cr += u.get("cache_read_input_tokens") or 0

    print(f"Total ccusage-admitted assistant rows: {total_assistant_admitted:,}")
    print(f"  ... in window: {in_window_admitted:,}")
    print()
    print(f"Hashes where global winner is in-window (both agree): {scenario_a_or_c:,}")
    print(f"Hashes where global winner is OUT-of-window (Scenario B): {scenario_b:,}")
    print(f"  Scenario B impact (ours - ccusage = ours's extra contribution):")
    print(f"    input  : {scenario_b_input:,}")
    print(f"    output : {scenario_b_output:,}")
    print(f"    cc     : {scenario_b_cc:,}")
    print(f"    cr     : {scenario_b_cr:,}")


if __name__ == "__main__":
    main()
