"""Check rows where requestId IS NULL (JSON null, not absent).

ccusage's Tr validator uses yr which rejects null. ccusage's Or fast-path
uses kr which also rejects rows with "requestId":null substring. So
requestId-null rows are REJECTED by ccusage entirely.

Our pipeline (_Row.requestId: str | None = None) accepts null. We admit
these rows and they contribute extra tokens.
"""
from __future__ import annotations
import json
from datetime import date, datetime, time, timezone
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
SINCE = date(2024, 1, 1)
UNTIL = date(2026, 5, 17)


def in_win(ts):
    try:
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return False
    if t.tzinfo is None:
        return False
    u = t.astimezone(timezone.utc)
    return datetime.combine(SINCE, time.min, tzinfo=timezone.utc) <= u < datetime.combine(UNTIL, time.min, tzinfo=timezone.utc)


def in_overlap(ts):
    OVERLAP = {
        "2026-01-06", "2026-01-07", "2026-03-03", "2026-03-04", "2026-03-05",
        "2026-03-06", "2026-03-10", "2026-03-11", "2026-03-12", "2026-03-13",
        "2026-04-08", "2026-04-09", "2026-04-10", "2026-04-14", "2026-04-15",
        "2026-04-16", "2026-04-17", "2026-04-23", "2026-04-24", "2026-04-28",
        "2026-04-29", "2026-04-30", "2026-05-05", "2026-05-06", "2026-05-07",
        "2026-05-08", "2026-05-12", "2026-05-13", "2026-05-14",
    }
    try:
        t = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)
        return t.date().isoformat() in OVERLAP
    except Exception:
        return False


# Categorize rows
abs_rid = 0         # requestId key not present
null_rid = 0        # requestId: null
str_rid = 0         # requestId: "..."
abs_rid_tokens = [0]*4
null_rid_tokens = [0]*4
str_rid_tokens = [0]*4
abs_overlap_tokens = [0]*4
null_overlap_tokens = [0]*4

for p in PROJECTS.rglob("*.jsonl"):
    try:
        with p.open() as f:
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
                if not isinstance(ts, str) or not in_win(ts):
                    continue
                msg = raw.get("message", {})
                u = msg.get("usage", {})
                if not isinstance(u, dict) or not isinstance(u.get("input_tokens"), int):
                    continue
                # Tokens
                cc = u.get("cache_creation_input_tokens") or 0
                cr = u.get("cache_read_input_tokens") or 0
                tk = (u["input_tokens"], u["output_tokens"], cc, cr)
                # Category
                if "requestId" not in raw:
                    abs_rid += 1
                    for i in range(4):
                        abs_rid_tokens[i] += tk[i]
                    if in_overlap(ts):
                        for i in range(4):
                            abs_overlap_tokens[i] += tk[i]
                elif raw["requestId"] is None:
                    null_rid += 1
                    for i in range(4):
                        null_rid_tokens[i] += tk[i]
                    if in_overlap(ts):
                        for i in range(4):
                            null_overlap_tokens[i] += tk[i]
                elif isinstance(raw["requestId"], str):
                    str_rid += 1
                    for i in range(4):
                        str_rid_tokens[i] += tk[i]
    except OSError:
        continue

print(f"Rows w/ requestId=string (admitted by both): {str_rid:,}")
print(f"  tokens: in={str_rid_tokens[0]:,} out={str_rid_tokens[1]:,} cc={str_rid_tokens[2]:,} cr={str_rid_tokens[3]:,}")
print(f"Rows w/ requestId key absent (ours admits; ccusage Tr admits ('undefined')): {abs_rid:,}")
print(f"  tokens (full): in={abs_rid_tokens[0]:,} out={abs_rid_tokens[1]:,} cc={abs_rid_tokens[2]:,} cr={abs_rid_tokens[3]:,}")
print(f"  tokens (overlap): in={abs_overlap_tokens[0]:,} out={abs_overlap_tokens[1]:,} cc={abs_overlap_tokens[2]:,} cr={abs_overlap_tokens[3]:,}")
print(f"Rows w/ requestId=null (ours admits; ccusage Tr REJECTS via yr): {null_rid:,}")
print(f"  tokens (full): in={null_rid_tokens[0]:,} out={null_rid_tokens[1]:,} cc={null_rid_tokens[2]:,} cr={null_rid_tokens[3]:,}")
print(f"  tokens (overlap): in={null_overlap_tokens[0]:,} out={null_overlap_tokens[1]:,} cc={null_overlap_tokens[2]:,} cr={null_overlap_tokens[3]:,}")
