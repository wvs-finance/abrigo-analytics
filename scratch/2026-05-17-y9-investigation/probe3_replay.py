"""Y-9 probe3: simulate BOTH pipelines exactly and report per-class
totals on the 27-weekday overlap window.

Goal: pinpoint where the +1.25% input / -0.64% output residual originates.
This probe ignores cost (we know that's within 0.1%) and focuses purely on
token aggregation.

For each row admitted by EITHER pipeline:
  - Compute ccusage's view: admit per Tr/Or; dedup globally via uniqueHash
    with $ ($ uses tokenTotal_flat + hasSpeed).
  - Compute our view: admit (currently: any assistant row in window);
    dedup globally via uniqueHash with our $ (uses tokenTotal_nested + hasSpeed).

Sum kept rows per pipeline; compute difference; print per-class deltas with
the specific rows that contribute most.
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


def ours_admit(raw: dict[str, Any]) -> bool:
    """Our current admission: assistant + Pydantic schema valid.
    Pydantic schema requires: timestamp (AwareDatetime), message.usage with
    input_tokens, output_tokens. Permissive elsewhere.
    """
    msg = raw.get("message")
    if not isinstance(msg, dict):
        return False
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return False
    if not isinstance(usage.get("input_tokens"), int):
        return False
    if not isinstance(usage.get("output_tokens"), int):
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


def date_of(ts_str: str) -> str:
    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    return ts.astimezone(timezone.utc).date().isoformat()


def token_total_flat(u: dict[str, Any]) -> int:
    return (
        u["input_tokens"]
        + u["output_tokens"]
        + (u.get("cache_creation_input_tokens") or 0)
        + (u.get("cache_read_input_tokens") or 0)
    )


def token_total_nested(u: dict[str, Any]) -> int:
    cc = u.get("cache_creation") or {}
    return (
        u["input_tokens"]
        + u["output_tokens"]
        + (cc.get("ephemeral_5m_input_tokens") or 0)
        + (cc.get("ephemeral_1h_input_tokens") or 0)
        + (u.get("cache_read_input_tokens") or 0)
    )


def main() -> None:
    # Gather every row that EITHER pipeline admits, in-window only.
    # row tuple: (in_window, ccu_ok, ours_ok, usage, ts_str, msg_model)

    # For each uniqueHash, replay both pipelines.
    by_hash_ccu: dict[str, list[dict]] = defaultdict(list)
    by_hash_ours: dict[str, list[dict]] = defaultdict(list)

    # Also track rows with NO uniqueHash for our pipeline (these are NOT
    # deduped by us either since unique_hash returns None for missing msg_id)
    ours_no_hash: list[dict] = []

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
                    ts = raw.get("timestamp")
                    if not isinstance(ts, str) or not in_window(ts):
                        continue
                    ccu_ok = ccusage_admit(raw)
                    our_ok = ours_admit(raw)
                    if not (ccu_ok or our_ok):
                        continue
                    msg = raw["message"]
                    u = msg["usage"]
                    h = unique_hash(msg.get("id"), raw.get("requestId"))
                    item = {
                        "usage": u,
                        "ts": ts,
                        "ccu_ok": ccu_ok,
                        "our_ok": our_ok,
                    }
                    if ccu_ok and h is not None:
                        by_hash_ccu[h].append(item)
                    if our_ok:
                        if h is not None:
                            by_hash_ours[h].append(item)
                        else:
                            ours_no_hash.append(item)
        except OSError:
            continue

    # Replay both
    ccu_input = ccu_output = ccu_cc = ccu_cr = 0
    our_input = our_output = our_cc = our_cr = 0
    daily_ccu: dict[str, tuple[int, int, int, int]] = defaultdict(lambda: (0, 0, 0, 0))
    daily_our: dict[str, tuple[int, int, int, int]] = defaultdict(lambda: (0, 0, 0, 0))

    for h, items in by_hash_ccu.items():
        kept = items[0]
        kt = token_total_flat(kept["usage"])
        khs = kept["usage"].get("speed") is not None
        for cand in items[1:]:
            ct = token_total_flat(cand["usage"])
            chs = cand["usage"].get("speed") is not None
            if ct > kt or (ct == kt and chs and not khs):
                kept = cand
                kt, khs = ct, chs
        u = kept["usage"]
        d = date_of(kept["ts"])
        cur = daily_ccu[d]
        daily_ccu[d] = (
            cur[0] + u["input_tokens"],
            cur[1] + u["output_tokens"],
            cur[2] + (u.get("cache_creation_input_tokens") or 0),
            cur[3] + (u.get("cache_read_input_tokens") or 0),
        )
        ccu_input += u["input_tokens"]
        ccu_output += u["output_tokens"]
        ccu_cc += u.get("cache_creation_input_tokens") or 0
        ccu_cr += u.get("cache_read_input_tokens") or 0

    for h, items in by_hash_ours.items():
        kept = items[0]
        kt = token_total_nested(kept["usage"])
        khs = kept["usage"].get("speed") is not None
        for cand in items[1:]:
            ct = token_total_nested(cand["usage"])
            chs = cand["usage"].get("speed") is not None
            if ct > kt or (ct == kt and chs and not khs):
                kept = cand
                kt, khs = ct, chs
        u = kept["usage"]
        d = date_of(kept["ts"])
        cc = u.get("cache_creation") or {}
        cc_sum = (cc.get("ephemeral_5m_input_tokens") or 0) + (
            cc.get("ephemeral_1h_input_tokens") or 0
        )
        cur = daily_our[d]
        daily_our[d] = (
            cur[0] + u["input_tokens"],
            cur[1] + u["output_tokens"],
            cur[2] + cc_sum,
            cur[3] + (u.get("cache_read_input_tokens") or 0),
        )
        our_input += u["input_tokens"]
        our_output += u["output_tokens"]
        our_cc += cc_sum
        our_cr += u.get("cache_read_input_tokens") or 0

    # Rows our pipeline admits with no uniqueHash (NOT deduped at all)
    for item in ours_no_hash:
        u = item["usage"]
        d = date_of(item["ts"])
        cc = u.get("cache_creation") or {}
        cc_sum = (cc.get("ephemeral_5m_input_tokens") or 0) + (
            cc.get("ephemeral_1h_input_tokens") or 0
        )
        cur = daily_our[d]
        daily_our[d] = (
            cur[0] + u["input_tokens"],
            cur[1] + u["output_tokens"],
            cur[2] + cc_sum,
            cur[3] + (u.get("cache_read_input_tokens") or 0),
        )
        our_input += u["input_tokens"]
        our_output += u["output_tokens"]
        our_cc += cc_sum
        our_cr += u.get("cache_read_input_tokens") or 0

    print("─── Full window [2024-01-01, 2026-05-17), all dates ───")
    print(f"  ccusage     : input={ccu_input:>12,}  output={ccu_output:>12,}  cc={ccu_cc:>14,}  cr={ccu_cr:>14,}")
    print(f"  ours        : input={our_input:>12,}  output={our_output:>12,}  cc={our_cc:>14,}  cr={our_cr:>14,}")
    print(f"  delta o-c   : input={our_input-ccu_input:>12,}  output={our_output-ccu_output:>12,}  cc={our_cc-ccu_cc:>14,}  cr={our_cr-ccu_cr:>14,}")
    print()

    # 27-weekday overlap: days where BOTH pipelines reported any activity
    overlap = sorted(set(daily_ccu.keys()) & set(daily_our.keys()))
    print(f"  Overlap days (both >0): {len(overlap)}")
    o_in = o_out = o_cc = o_cr = 0
    c_in = c_out = c_cc = c_cr = 0
    for d in overlap:
        a, b, c, e = daily_our[d]
        f, g, h, j = daily_ccu[d]
        o_in += a; o_out += b; o_cc += c; o_cr += e
        c_in += f; c_out += g; c_cc += h; c_cr += j
    print("─── On overlap-only days ───")
    print(f"  ccusage     : input={c_in:>12,}  output={c_out:>12,}  cc={c_cc:>14,}  cr={c_cr:>14,}")
    print(f"  ours (sim)  : input={o_in:>12,}  output={o_out:>12,}  cc={o_cc:>14,}  cr={o_cr:>14,}")
    print(f"  delta o-c   : input={o_in-c_in:>12,}  output={o_out-c_out:>12,}  cc={o_cc-c_cc:>14,}  cr={o_cr-c_cr:>14,}")
    print()
    # Per-day rows with largest divergence
    print("─── Top 10 days by |input delta| (ours - ccusage) ───")
    diffs = []
    for d in overlap:
        a, b, c, e = daily_our[d]
        f, g, h, j = daily_ccu[d]
        diffs.append((d, a-f, b-g, c-h, e-j))
    diffs.sort(key=lambda x: -abs(x[1]))
    for d, di, do, dc, dr in diffs[:10]:
        print(f"  {d}: input{di:+8,}  output{do:+8,}  cc{dc:+10,}  cr{dr:+10,}")


if __name__ == "__main__":
    main()
