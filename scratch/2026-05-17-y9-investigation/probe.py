"""Y-9 root-cause probe — empirical comparison of our dedup vs ccusage's.

Goal: identify the divergence(s) that produce per-token-class residuals
between our pipeline and ccusage on the 27-weekday overlap.

Pre-pinned hypotheses (from spec §0.5 Y-9):
  H1: ccusage aggregates iterations[i].input_tokens (we read top-level only)
  H2: ccusage prices dropped_unknown_model via fallback (we drop entirely)
  H3: hasSpeed tiebreaker collisions differ in which row is kept
  H4 (added during probe): nested cache_creation.ephemeral_{5m,1h} vs flat
       cache_creation_input_tokens differ; ccusage uses the flat field
  H5 (added during probe): isApiErrorMessage=true admission policy differs
  H6 (added during probe): validator strictness — ccusage Tr rejects rows
       missing message.id, with non-text content items, etc.

Output: scratch/2026-05-17-y9-investigation/probe_output.txt
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any

PROJECTS_ROOT = Path.home() / ".claude" / "projects"
# 27-weekday overlap is governed by the production CLI window. Use the
# same window as the spec's parity comparison.
SINCE = date(2024, 1, 1)
UNTIL = date(2026, 5, 17)


def utc_in_window(ts_str: str) -> bool:
    """Parse ISO-8601 timestamp string and test against [SINCE, UNTIL)."""
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


def unique_hash(msg_id: str | None, req_id: str | None) -> str | None:
    if not msg_id:
        return None
    if req_id is None:
        return msg_id
    return f"{msg_id}:{req_id}"


def ccusage_admit(raw: dict[str, Any]) -> bool:
    """Mirror ccusage's Tr validator + Or isApiErrorMessage filter.

    Rejection criteria (Tr):
      - cwd not string-or-undefined
      - sessionId not string (non-empty) or undefined
      - requestId not string (non-empty) or undefined
      - costUSD not number-or-undefined
      - isApiErrorMessage not boolean-or-undefined
      - version present and not matching version regex
      - timestamp not string or not matching timestamp regex
      - message.model not string-or-undefined
      - message.id not string (non-empty) or undefined
      - message.content present but not an array (or array contains non-text)
      - usage.input_tokens or usage.output_tokens not number
      - usage.cache_creation_input_tokens / cache_read_input_tokens not
        number-or-undefined
      - usage.speed not in {undefined, "standard", "fast"}

    Or fast path also rejects rows with isApiErrorMessage=true substring
    OR with any `:null` value among id/cwd/model/speed/costUSD/version/
    sessionId/requestId/isApiErrorMessage/cache_read_input_tokens/
    cache_creation_input_tokens.

    Returns True if the row would be admitted by EITHER Or or Tr path.
    """
    msg = raw.get("message")
    if not isinstance(msg, dict):
        return False

    # message.id MUST be a non-empty string (yr returns false for null/empty)
    mid = msg.get("id")
    if mid is None or not isinstance(mid, str) or mid == "":
        return False

    # message.model: string or undefined; ours allows missing → "unknown"
    model = msg.get("model")
    if model is not None and (not isinstance(model, str) or model == ""):
        return False

    # requestId: string (non-empty) or undefined
    rid = raw.get("requestId")
    if rid is not None and (not isinstance(rid, str) or rid == ""):
        return False

    # isApiErrorMessage: boolean or undefined; AND in Or it must not be true
    err = raw.get("isApiErrorMessage")
    if err is True:
        return False
    if err is not None and not isinstance(err, bool):
        return False

    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return False
    inp = usage.get("input_tokens")
    out = usage.get("output_tokens")
    if not isinstance(inp, int) or not isinstance(out, int):
        return False

    cc = usage.get("cache_creation_input_tokens")
    if cc is not None and not isinstance(cc, int):
        return False
    cr = usage.get("cache_read_input_tokens")
    if cr is not None and not isinstance(cr, int):
        return False

    speed = usage.get("speed")
    if speed is not None and speed not in ("standard", "fast"):
        return False

    # message.content validity
    content = msg.get("content")
    if content is not None:
        if not isinstance(content, list):
            return False
        for c in content:
            if not isinstance(c, dict):
                return False
            t = c.get("text")
            if t is not None and not isinstance(t, str):
                return False

    return True


def token_total_flat(usage: dict[str, Any]) -> int:
    """ccusage Sr: input + output + cache_creation_input_tokens + cache_read"""
    return (
        usage["input_tokens"]
        + usage["output_tokens"]
        + (usage.get("cache_creation_input_tokens") or 0)
        + (usage.get("cache_read_input_tokens") or 0)
    )


def token_total_nested(usage: dict[str, Any]) -> int:
    """Our Sr: input + output + ephemeral_5m + ephemeral_1h + cache_read"""
    cc = usage.get("cache_creation") or {}
    return (
        usage["input_tokens"]
        + usage["output_tokens"]
        + (cc.get("ephemeral_5m_input_tokens") or 0)
        + (cc.get("ephemeral_1h_input_tokens") or 0)
        + (usage.get("cache_read_input_tokens") or 0)
    )


def main() -> None:
    # Collect every assistant row admitted by EITHER pipeline, with both
    # versions of token total and key dedup metadata.
    # Stats counters
    total_rows = 0
    total_assistant = 0
    ours_admit = 0  # we admit (current code: just "type==assistant")
    ccu_admit = 0
    only_ours = 0
    only_ccu = 0
    both = 0

    # cache_creation flat vs nested divergence (per row admitted by both)
    cc_flat_eq_nested = 0
    cc_flat_neq_nested = 0
    cc_flat_minus_nested_sum = 0

    # iterations[] presence
    has_iterations = 0
    multi_iterations = 0
    iter_input_eq_top = 0
    iter_input_neq_top = 0
    iter_input_total = 0
    top_input_total = 0

    # isApiErrorMessage admission
    api_error_true_count = 0
    api_error_true_token_total = 0

    # Missing message.id
    missing_msg_id = 0
    missing_msg_id_token_total = 0

    # Per-row records for dedup comparison (only rows admitted by ccusage,
    # because that's the apples-to-apples slice)
    # key = uniqueHash; value = list of (file, line_no, raw)
    by_hash: dict[str, list[tuple[Path, int, dict]]] = defaultdict(list)
    no_hash_rows = 0  # ccusage-admitted rows without uniqueHash (none, since
    # Tr requires message.id) — but ours admits even without id

    # Also build our-pipeline by_hash to compare keep choices
    by_hash_ours: dict[str, list[tuple[Path, int, dict]]] = defaultdict(list)
    no_hash_ours = 0

    for jp in PROJECTS_ROOT.rglob("*.jsonl"):
        try:
            with jp.open() as f:
                for ln, line in enumerate(f, 1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    total_rows += 1
                    try:
                        raw = json.loads(stripped)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(raw, dict):
                        continue
                    if raw.get("type") != "assistant":
                        continue
                    total_assistant += 1
                    ts = raw.get("timestamp")
                    if not isinstance(ts, str) or not utc_in_window(ts):
                        continue

                    # Our admission: just timestamp-window + assistant; we
                    # don't validate message.id existence pre-admission, and
                    # we don't reject isApiErrorMessage=true.
                    ours_ok = True
                    ccu_ok = ccusage_admit(raw)

                    if ours_ok:
                        ours_admit += 1
                    if ccu_ok:
                        ccu_admit += 1

                    if ours_ok and ccu_ok:
                        both += 1
                    elif ours_ok:
                        only_ours += 1
                    elif ccu_ok:
                        only_ccu += 1

                    msg = raw.get("message", {})
                    usage = msg.get("usage", {})
                    mid = msg.get("id")
                    rid = raw.get("requestId")
                    h = unique_hash(mid, rid)

                    # Diagnostics for divergence categories
                    err = raw.get("isApiErrorMessage")
                    if err is True and isinstance(usage, dict):
                        tt = token_total_flat(usage) if isinstance(
                            usage.get("input_tokens"), int
                        ) else 0
                        api_error_true_count += 1
                        api_error_true_token_total += tt

                    if mid is None or mid == "":
                        missing_msg_id += 1
                        if isinstance(usage, dict) and isinstance(
                            usage.get("input_tokens"), int
                        ):
                            missing_msg_id_token_total += token_total_flat(usage)

                    if isinstance(usage, dict):
                        # iterations[] probe (H1)
                        iters = usage.get("iterations")
                        if isinstance(iters, list) and len(iters) > 0:
                            has_iterations += 1
                            if len(iters) > 1:
                                multi_iterations += 1
                            sum_iter_in = sum(
                                (it.get("input_tokens") or 0)
                                for it in iters
                                if isinstance(it, dict)
                            )
                            top_in = usage.get("input_tokens") or 0
                            iter_input_total += sum_iter_in
                            top_input_total += top_in
                            if sum_iter_in == top_in:
                                iter_input_eq_top += 1
                            else:
                                iter_input_neq_top += 1

                        # H4: flat vs nested cache_creation
                        if ccu_ok:
                            flat = usage.get("cache_creation_input_tokens")
                            nested = usage.get("cache_creation") or {}
                            nest_sum = (nested.get("ephemeral_5m_input_tokens") or 0) + (
                                nested.get("ephemeral_1h_input_tokens") or 0
                            )
                            if (flat or 0) == nest_sum:
                                cc_flat_eq_nested += 1
                            else:
                                cc_flat_neq_nested += 1
                                cc_flat_minus_nested_sum += (flat or 0) - nest_sum

                    # Record by_hash for dedup comparison
                    if ccu_ok and h is not None:
                        by_hash[h].append((jp, ln, raw))
                    if ours_ok:
                        if h is not None:
                            by_hash_ours[h].append((jp, ln, raw))
                        else:
                            no_hash_ours += 1
        except OSError:
            continue

    # Dedup comparison: for each hash with >1 entry, simulate ccusage's
    # keep-choice and ours, count divergences.
    ccusage_dedup_collisions = 0
    ours_dedup_collisions = 0
    divergent_keeps = 0
    impact_input = 0
    impact_output = 0
    impact_cc = 0
    impact_cr = 0

    for h, entries in by_hash.items():
        if len(entries) <= 1:
            continue
        ccusage_dedup_collisions += len(entries) - 1

        # ccusage scoring: tokenTotal_flat (input+output+cc_flat+cr) +
        # hasSpeed (usage.speed is not None). Keep first; replace on
        # $(new, old) returns True i.e., new_tt > old_tt OR
        # (new_tt==old_tt AND new_hasspeed AND not old_hasspeed).
        def ccu_score(raw: dict) -> tuple[int, bool, dict]:
            u = raw["message"]["usage"]
            tt = token_total_flat(u)
            hs = u.get("speed") is not None
            return tt, hs, u

        def ours_score(raw: dict) -> tuple[int, bool, dict]:
            u = raw["message"]["usage"]
            tt = token_total_nested(u)
            hs = u.get("speed") is not None
            return tt, hs, u

        # Replay both pipelines in file-iteration order
        # (we iterate rglob in OS order; both pipelines see the same order)
        ccu_kept = entries[0]
        ccu_tt, ccu_hs, ccu_u = ccu_score(ccu_kept[2])
        for cand in entries[1:]:
            new_tt, new_hs, new_u = ccu_score(cand[2])
            if new_tt > ccu_tt or (new_tt == ccu_tt and new_hs and not ccu_hs):
                ccu_kept = cand
                ccu_tt, ccu_hs, ccu_u = new_tt, new_hs, new_u

        # Ours: same entries (we admit a superset, but on this hash with
        # ccu_ok we definitely see these). Replay with nested scoring.
        # Note: ours might admit additional entries not in `entries` if
        # they fail ccu_admit but have the same hash. Check.
        ours_entries = by_hash_ours.get(h, [])
        if len(ours_entries) > 1:
            ours_dedup_collisions += len(ours_entries) - 1
        if not ours_entries:
            continue
        ours_kept = ours_entries[0]
        our_tt, our_hs, our_u = ours_score(ours_kept[2])
        for cand in ours_entries[1:]:
            new_tt, new_hs, new_u = ours_score(cand[2])
            if new_tt > our_tt or (new_tt == our_tt and new_hs and not our_hs):
                ours_kept = cand
                our_tt, our_hs, our_u = new_tt, new_hs, new_u

        # Compare kept rows
        if ccu_kept[2] is not ours_kept[2]:
            divergent_keeps += 1
            # Per-token-class impact: ours - ccusage
            ou = ours_kept[2]["message"]["usage"]
            cu = ccu_kept[2]["message"]["usage"]
            impact_input += (ou.get("input_tokens", 0)) - (cu.get("input_tokens", 0))
            impact_output += (ou.get("output_tokens", 0)) - (cu.get("output_tokens", 0))
            # For cache_create, use what each pipeline would report
            ou_cc_nested = (ou.get("cache_creation") or {})
            ou_cc = (ou_cc_nested.get("ephemeral_5m_input_tokens", 0)) + (
                ou_cc_nested.get("ephemeral_1h_input_tokens", 0)
            )
            cu_cc = cu.get("cache_creation_input_tokens", 0) or 0
            impact_cc += ou_cc - cu_cc
            impact_cr += (ou.get("cache_read_input_tokens", 0) or 0) - (
                cu.get("cache_read_input_tokens", 0) or 0
            )

    # Print findings
    out = []
    out.append("=" * 72)
    out.append("Y-9 ROOT-CAUSE PROBE — empirical findings")
    out.append("=" * 72)
    out.append("")
    out.append(f"Window: [{SINCE}, {UNTIL})")
    out.append(f"Projects root: {PROJECTS_ROOT}")
    out.append("")
    out.append("─── Raw counts ──────────────────────────────────────────────")
    out.append(f"  total JSONL lines           : {total_rows:>10,}")
    out.append(f"  total assistant rows        : {total_assistant:>10,}")
    out.append(f"  in-window assistant rows    : {ours_admit:>10,}")
    out.append("")
    out.append("─── Admission divergence (ours vs ccusage) ──────────────────")
    out.append(f"  admitted by ours (any row)  : {ours_admit:>10,}")
    out.append(f"  admitted by ccusage (Tr/Or) : {ccu_admit:>10,}")
    out.append(f"  admitted by both            : {both:>10,}")
    out.append(f"  ours only (ccusage rejects) : {only_ours:>10,}")
    out.append(f"  ccusage only (ours rejects) : {only_ccu:>10,}")
    out.append("")
    out.append("─── H5: isApiErrorMessage=true rows ─────────────────────────")
    out.append(f"  count                       : {api_error_true_count:>10,}")
    out.append(f"  sum tokenTotal              : {api_error_true_token_total:>10,}")
    out.append("")
    out.append("─── H6: missing message.id rows (ours admits, ccusage rejects) ─")
    out.append(f"  count                       : {missing_msg_id:>10,}")
    out.append(f"  sum tokenTotal              : {missing_msg_id_token_total:>10,}")
    out.append("")
    out.append("─── H4: flat vs nested cache_creation ───────────────────────")
    out.append(f"  rows where flat == nested   : {cc_flat_eq_nested:>10,}")
    out.append(f"  rows where flat != nested   : {cc_flat_neq_nested:>10,}")
    out.append(f"  sum(flat - nested)          : {cc_flat_minus_nested_sum:>10,}")
    out.append("")
    out.append("─── H1: iterations[] aggregation ─────────────────────────────")
    out.append(f"  rows with iterations[]      : {has_iterations:>10,}")
    out.append(f"  rows with >1 iteration      : {multi_iterations:>10,}")
    out.append(f"  iter_input == top_input     : {iter_input_eq_top:>10,}")
    out.append(f"  iter_input != top_input     : {iter_input_neq_top:>10,}")
    out.append(f"  sum(top input over iter rows): {top_input_total:>10,}")
    out.append(f"  sum(iterations input)       : {iter_input_total:>10,}")
    out.append(
        f"  delta (iter - top)          : {iter_input_total - top_input_total:>10,}"
    )
    out.append("")
    out.append("─── H3: hasSpeed tiebreaker / dedup-keep divergence ──────────")
    out.append(f"  uniqueHash collisions (ccu) : {ccusage_dedup_collisions:>10,}")
    out.append(f"  uniqueHash collisions (ours): {ours_dedup_collisions:>10,}")
    out.append(f"  divergent keep choices      : {divergent_keeps:>10,}")
    out.append(f"  impact: ours_input - ccu_input  = {impact_input:>10,}")
    out.append(f"  impact: ours_output - ccu_output= {impact_output:>10,}")
    out.append(f"  impact: ours_cc - ccu_cc        = {impact_cc:>10,}")
    out.append(f"  impact: ours_cr - ccu_cr        = {impact_cr:>10,}")
    out.append("")

    text = "\n".join(out)
    print(text)
    out_path = Path(__file__).parent / "probe_output.txt"
    out_path.write_text(text)


if __name__ == "__main__":
    main()
