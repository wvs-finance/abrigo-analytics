"""Y-9 H8: file-iteration order divergence.

ccusage SORTS JSONL files alphabetically by full path (function Yr ends
with `t.sort(fe)`). Our rglob iterates in OS readdir order (unsorted on
Linux). On (tokenTotal, hasSpeed) ties the FIRST-seen row wins per the
$ rule. Different file orders → different first-seen → different kept row
when ties exist.

This probe re-replays both pipelines using TWO orderings (sorted vs
rglob-order) and reports how many keep choices differ.
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


def unique_hash(msg_id, req_id):
    if not msg_id:
        return None
    return msg_id if req_id is None else f"{msg_id}:{req_id}"


def tt_flat(u):
    return u["input_tokens"] + u["output_tokens"] + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)


def tt_nested(u):
    cc = u.get("cache_creation") or {}
    return u["input_tokens"] + u["output_tokens"] + (cc.get("ephemeral_5m_input_tokens") or 0) + (cc.get("ephemeral_1h_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)


def replay(file_order, tt_fn, scoring_label):
    """Replay one pipeline over file_order with tt_fn scoring; return
    map uniqueHash -> kept usage dict.
    """
    kept = {}  # h -> (tt, hasSpeed, usage, ts)
    for jp in file_order:
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
                    if not isinstance(raw, dict) or raw.get("type") != "assistant":
                        continue
                    ts = raw.get("timestamp")
                    if not isinstance(ts, str) or not in_window(ts):
                        continue
                    msg = raw.get("message")
                    if not isinstance(msg, dict):
                        continue
                    u = msg.get("usage")
                    if not isinstance(u, dict) or not isinstance(u.get("input_tokens"), int) or not isinstance(u.get("output_tokens"), int):
                        continue
                    mid = msg.get("id")
                    if not isinstance(mid, str) or mid == "":
                        continue
                    if raw.get("isApiErrorMessage") is True:
                        continue
                    h = unique_hash(mid, raw.get("requestId"))
                    if h is None:
                        continue
                    new_tt = tt_fn(u)
                    new_hs = u.get("speed") is not None
                    prev = kept.get(h)
                    if prev is None:
                        kept[h] = (new_tt, new_hs, u, ts)
                    else:
                        if new_tt > prev[0] or (new_tt == prev[0] and new_hs and not prev[1]):
                            kept[h] = (new_tt, new_hs, u, ts)
        except OSError:
            continue
    return kept


def main():
    # rglob order (what we use)
    files_rglob = list(PROJECTS_ROOT.rglob("*.jsonl"))
    # sorted (what ccusage does via fe comparator on full path)
    files_sorted = sorted(files_rglob, key=lambda p: str(p))

    print(f"Files: {len(files_rglob)}")
    print(f"First 3 rglob: {[str(p)[-50:] for p in files_rglob[:3]]}")
    print(f"First 3 sorted: {[str(p)[-50:] for p in files_sorted[:3]]}")
    print()

    # ccusage replay: sorted order + flat scoring
    kept_ccu = replay(files_sorted, tt_flat, "ccusage(sorted,flat)")
    # ours actual replay: rglob order + nested scoring
    kept_ours = replay(files_rglob, tt_nested, "ours(rglob,nested)")

    print(f"ccusage kept: {len(kept_ccu):,}")
    print(f"ours kept   : {len(kept_ours):,}")

    # Compare kept choices on common hashes
    common = set(kept_ccu) & set(kept_ours)
    print(f"common hashes: {len(common):,}")

    diff_count = 0
    d_in = d_out = d_cc = d_cr = 0
    for h in common:
        ccu_u = kept_ccu[h][2]
        our_u = kept_ours[h][2]
        if ccu_u is our_u:
            continue
        # Compare actual token counts
        ccu_in = ccu_u["input_tokens"]; our_in = our_u["input_tokens"]
        ccu_out = ccu_u["output_tokens"]; our_out = our_u["output_tokens"]
        ccu_cc_v = ccu_u.get("cache_creation_input_tokens") or 0
        our_cc_nested = our_u.get("cache_creation") or {}
        our_cc_v = (our_cc_nested.get("ephemeral_5m_input_tokens") or 0) + (our_cc_nested.get("ephemeral_1h_input_tokens") or 0)
        ccu_cr_v = ccu_u.get("cache_read_input_tokens") or 0
        our_cr_v = our_u.get("cache_read_input_tokens") or 0

        if (ccu_in, ccu_out, ccu_cc_v, ccu_cr_v) != (our_in, our_out, our_cc_v, our_cr_v):
            diff_count += 1
            d_in += our_in - ccu_in
            d_out += our_out - ccu_out
            d_cc += our_cc_v - ccu_cc_v
            d_cr += our_cr_v - ccu_cr_v

    print(f"divergent kept rows: {diff_count:,}")
    print(f"  delta sum input  : {d_in:>10,}")
    print(f"  delta sum output : {d_out:>10,}")
    print(f"  delta sum cc     : {d_cc:>14,}")
    print(f"  delta sum cr     : {d_cr:>14,}")


if __name__ == "__main__":
    main()
