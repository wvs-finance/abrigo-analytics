"""Drill down on 2026-03-12 (biggest input delta day). Compare each
unique_hash that appears in our pipeline's records for that date with
its corresponding ccusage-rule kept row.
"""
from __future__ import annotations
import json
import warnings
from collections import defaultdict
from datetime import date, datetime, time, timezone
from pathlib import Path

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
)
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader

REPO = Path(__file__).resolve().parents[2]
PROJECTS = Path.home() / ".claude" / "projects"
TARGET_DATE = "2026-03-12"

# 1. Get production-kept rows for target date
pricing = PricingTable.from_litellm_sha(
    LITELLM_SHA_PINNED,
    cached_json_path=REPO / "data" / "raw" / "litellm_model_prices.json",
)
reader = JSONLReader(pricing=pricing)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    result = reader(date(2024, 1, 1), date(2026, 5, 17))

prod_for_date = []
for r in result.records:
    if r.is_error:
        continue
    if r.ts.date().isoformat() == TARGET_DATE:
        prod_for_date.append(r)
print(f"Production kept rows on {TARGET_DATE}: {len(prod_for_date)}")
ph_to_record = {}
for r in prod_for_date:
    # hash key
    key = f"{r.uuid}" if r.uuid else "?"
    ph_to_record[key] = r

# 2. Reconstruct what ccusage would keep
# For target date, find all hashes that appear; for each, find global
# ccusage-rule winner and check date.
def unique_hash(mid, rid):
    if not mid: return None
    return mid if rid is None else f"{mid}:{rid}"

def in_win(ts):
    try:
        t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return False
    if t.tzinfo is None: return False
    u = t.astimezone(timezone.utc)
    return datetime(2024,1,1,tzinfo=timezone.utc) <= u < datetime(2026,5,17,tzinfo=timezone.utc)

def tt_flat(u):
    return u["input_tokens"] + u["output_tokens"] + (u.get("cache_creation_input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)

by_hash = defaultdict(list)
for jp in sorted(PROJECTS.rglob("*.jsonl"), key=str):
    try:
        with jp.open() as f:
            for ln, line in enumerate(f, 1):
                s = line.strip()
                if not s: continue
                try: raw = json.loads(s)
                except: continue
                if not isinstance(raw, dict) or raw.get("type") != "assistant": continue
                ts = raw.get("timestamp")
                if not isinstance(ts, str) or not in_win(ts): continue
                msg = raw.get("message", {})
                u = msg.get("usage", {})
                mid = msg.get("id")
                if not isinstance(mid, str) or mid == "": continue
                if raw.get("isApiErrorMessage") is True: continue
                rid = raw.get("requestId")
                if rid is not None and (not isinstance(rid, str) or rid == ""): continue
                if not isinstance(u, dict) or not isinstance(u.get("input_tokens"), int): continue
                h = unique_hash(mid, rid)
                d = datetime.fromisoformat(ts.replace("Z","+00:00")).astimezone(timezone.utc).date().isoformat()
                by_hash[h].append({"file": str(jp)[-60:], "ln": ln, "date": d, "u": u, "hs": u.get("speed") is not None, "tt": tt_flat(u)})
    except OSError:
        continue

# For each hash that has at least one entry on TARGET_DATE, find the
# global ccusage winner and report whether it's on TARGET_DATE.
relevant_hashes = set()
for h, ents in by_hash.items():
    if any(e["date"] == TARGET_DATE for e in ents):
        relevant_hashes.add(h)
print(f"Hashes with at least one entry on {TARGET_DATE}: {len(relevant_hashes)}")

ccu_in = ccu_out = ccu_cc = ccu_cr = 0
prod_in = prod_out = prod_cc = prod_cr = 0
shifted = 0  # hashes where global winner is NOT on TARGET_DATE
all_hashes_seen_by_prod = 0

for h in relevant_hashes:
    ents = by_hash[h]
    # ccusage winner (global, flat scoring)
    winner = ents[0]
    for cand in ents[1:]:
        if cand["tt"] > winner["tt"] or (cand["tt"] == winner["tt"] and cand["hs"] and not winner["hs"]):
            winner = cand
    if winner["date"] == TARGET_DATE:
        u = winner["u"]
        ccu_in += u["input_tokens"]
        ccu_out += u["output_tokens"]
        ccu_cc += u.get("cache_creation_input_tokens") or 0
        ccu_cr += u.get("cache_read_input_tokens") or 0
    else:
        shifted += 1

# Sum production target-date totals
for r in prod_for_date:
    prod_in += r.input_tok
    prod_out += r.output_tok
    prod_cc += r.cache_create_5m + r.cache_create_1h
    prod_cr += r.cache_read

print(f"  ccusage-rule winners stay on {TARGET_DATE}: {len(relevant_hashes)-shifted}")
print(f"  ccusage-rule winners SHIFTED to other date: {shifted}")
print()
print(f"Production sum: in={prod_in:,} out={prod_out:,} cc={prod_cc:,} cr={prod_cr:,}")
print(f"ccusage  sum  : in={ccu_in:,}  out={ccu_out:,}  cc={ccu_cc:,}  cr={ccu_cr:,}")
print(f"Delta (p-c)   : in={prod_in-ccu_in:+,}  out={prod_out-ccu_out:+,}  cc={prod_cc-ccu_cc:+,}  cr={prod_cr-ccu_cr:+,}")
