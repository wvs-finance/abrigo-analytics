"""Tier-3 CLI: build data/panels/notional_cost_panel.parquet.

Single orchestration point that imports across utils + modules tiers
(spec v0.2.3 §3.3, §3.5). This is the only module in the dev_ai_cost_v2
pipeline permitted to wire IO Boundary (jsonl_io) together with Callable
tier (anthropic_pricing, panel_builder); per spec §3.3 the CLI is the
intentional cross-tier integration point and is NOT a tier-import-rule
violation.

v0.2.3 (Y-5f migration): the CLI consumes ``JSONLReadResult`` (not bare
Sequence[MessageRecord]) and threads the 5 audit counters into the
operator print line + DATA_PROVENANCE emission per Y-5a.

Reads:
    --projects-root  Anthropic Claude Code JSONL transcript root.
    --litellm-cache  Pinned LiteLLM model_prices_and_context_window.json.
    --trm-path       Banrep daily TRM parquet (produced by fetch_banrep.py).

Writes:
    --out            Daily notional cost panel parquet (one row per UTC
                     date with cost in both USD and COP).

Exit codes:
    0  Panel written successfully.
    !0 Any reconciliation, schema-drift, SHA-mismatch, or IO failure
       propagates as a non-zero exit via uncaught exception (SystemExit
       wraps the traceback so the operator sees the root cause).
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import polars as pl

from simulations.dev_ai_cost_v2.anthropic_pricing import (
    LITELLM_SHA_PINNED,
    PricingTable,
)
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader
from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel

REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_args() -> argparse.Namespace:
    """Parse and return CLI arguments.

    Contract:
        * ``--since`` and ``--until`` are required ISO-8601 dates
          (``date.fromisoformat`` raises ``ValueError`` on malformed input,
          which argparse converts to a non-zero exit).
        * All path arguments are typed as ``pathlib.Path``; defaults are
          resolved relative to ``REPO_ROOT``.
        * Missing ``--since`` or ``--until`` causes argparse to print
          usage and exit with code 2.
    """
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--since", type=date.fromisoformat, required=True)
    p.add_argument("--until", type=date.fromisoformat, required=True)
    p.add_argument(
        "--projects-root",
        default=Path("~/.claude/projects").expanduser(),
        type=Path,
    )
    p.add_argument(
        "--litellm-cache",
        default=REPO_ROOT / "data" / "raw" / "litellm_model_prices.json",
        type=Path,
    )
    p.add_argument(
        "--trm-path",
        default=REPO_ROOT / "data" / "raw" / "banrep_trm_daily.parquet",
        type=Path,
    )
    p.add_argument(
        "--out",
        default=REPO_ROOT / "data" / "panels" / "notional_cost_panel.parquet",
        type=Path,
    )
    return p.parse_args()


def main() -> int:
    """Orchestrate the panel build end-to-end.

    Contract:
        * Creates ``args.out.parent`` if missing (CORRECTIONS-W).
        * Loads the LiteLLM pricing table at the spec-pinned SHA via
          ``PricingTable.from_litellm_sha(LITELLM_SHA_PINNED, ...)``
          (signature unchanged per v0.2.3 RC closure note).
        * Reads the daily TRM parquet via ``pl.read_parquet``.
        * Materializes JSONL ``read_result`` via ``JSONLReader`` (the only
          IO Boundary call). The reader returns a ``JSONLReadResult``
          carrying ``dropped_non_assistant_count`` (Y-5a, Y-5b).
        * Joins records × pricing × TRM via ``build_daily_panel``;
          forward-fill is FORBIDDEN by the panel builder's contract.
        * Writes the resulting parquet and prints a one-line summary
          including all 5 v0.2.3 counters + the Y-6 π̂ scalar for
          operator reconciliation.

    Returns:
        ``0`` on success. Any exception propagates uncaught so the
        operator sees the full traceback.
    """
    args = _parse_args()

    # CORRECTIONS-W: data/panels/ may not exist on a fresh clone.
    args.out.parent.mkdir(parents=True, exist_ok=True)

    pricing = PricingTable.from_litellm_sha(
        LITELLM_SHA_PINNED, cached_json_path=args.litellm_cache
    )
    trm = pl.read_parquet(args.trm_path)
    reader = JSONLReader(pricing=pricing)
    read_result = reader(args.since, args.until, projects_root=args.projects_root)
    panel = build_daily_panel(read_result, pricing, trm)

    panel.df.write_parquet(args.out)
    # Operator-visible audit line: v0.2.10 audit-econ #10 splits the old
    # single ``dropped_rows`` counter into three named counters pinned to
    # one unit each (message / TRM-row / weekday-day). The day-level
    # counter surfaces holiday-Monday drops (audit-econ #1).
    # Counters grouped: weekend/TRM-missing (panel-side) first, then
    # error, then JSONLReader-sourced (non_assistant, malformed,
    # duplicate), then PricingTable-sourced, then Y-6 π̂.
    print(
        f"[OK] wrote {args.out} ({panel.df.height} rows; "
        f"dropped_weekend_message={panel.dropped_weekend_message_count}, "
        f"dropped_weekend_trm_row={panel.dropped_weekend_trm_row_count}, "
        f"dropped_trm_missing_weekday={panel.dropped_trm_missing_weekday_count}, "
        f"dropped_error={panel.dropped_error_count}, "
        f"dropped_non_assistant={panel.dropped_non_assistant_count}, "
        f"dropped_malformed={panel.dropped_malformed_line_count}, "
        f"dropped_duplicate={panel.dropped_duplicate_count}, "
        f"dropped_non_anthropic={panel.dropped_non_anthropic_count}, "
        f"warn_missing_keys={panel.warn_missing_keys_count}, "
        f"dropped_unknown_model={panel.dropped_unknown_model_count}, "
        f"substr_tiebreaker={panel.multiple_substring_match_warning}, "
        f"ephemeral_pi_share={panel.ephemeral_pi_share:.6f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
