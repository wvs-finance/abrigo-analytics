"""IO Boundary tier for SAAS-COHORT-2 — verdict / robustness emission.

Mutable state lives ONLY at this tier per the functional-python skill.

- :class:`PosteriorTauReader` — reads the C1-emitted Hive-partitioned
  ``synthetic_tau_t`` dataset and returns a 2-D float64 array of shape
  ``(n_simulations × n_months, T_per_sim)`` aligned for ingestion by
  the Δ evaluator. Wraps the shipped ``SyntheticTauReader``.
- :class:`GateVerdictWriter` — writes ``gate_verdict.json`` per spec
  §10 line 520 verbatim alphabet (``PASS|WEAK|MARGINAL|FAIL|
  INDISTINGUISHABLE``); RC-BLOCK-2 v0.2 fix.
- :class:`RobustnessResultsAppender` — appends a Markdown section to
  ``ROBUSTNESS_RESULTS.md`` with the bank-spread arm's per-bracket
  evidence; the file is created with a header on first call. Pin
  ROBUST-BS — robustness verdicts MUST NOT touch the primary
  ``gate_verdict.json``.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Final

import numpy as np
from numpy.typing import NDArray

from simulations.saas_builder.cohort_2.types import CohortGateVerdict
from simulations.utils.parquet_io import SyntheticTauReader

#: Default emission directory for cohort-2 artifacts.
DEFAULT_ESTIMATES_DIR: Final[Path] = Path(
    "notebooks/saas_builder_stage_2/estimates"
)


# ─── PosteriorTauReader ──────────────────────────────────────────────────────


class PosteriorTauReader:
    """IO Boundary — read C1's synthetic_tau_t parquet into per-sim τ_t arrays.

    Returns a ``dict`` mapping each ``simulation_id`` to a 1-D float64
    array of τ_t values across the C1-emitted months. Callers reshape
    these per the BracketGrid's horizon_T (the C1 emit is 3 months ×
    16000 rows; cohort-2 callers stack months as T).
    """

    _reader: SyntheticTauReader

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._reader = SyntheticTauReader(base_dir=base_dir)

    def __call__(
        self, root: str | Path | None = None
    ) -> NDArray[np.float64]:
        """Return τ_t draws as a 2-D array shape ``(n_simulations, n_months)``.

        Aggregation:
            Each unique ``simulation_id`` becomes one row;
            month index orders the columns.

        Raises:
            FileNotFoundError: missing C1 parquet (HALT trigger upstream).
            SchemaMismatchError: column-set drift.
        """
        rows = self._reader(root)
        # Group by simulation_id, sort by month → list of (month, tau).
        grouped: dict[int, list[tuple[int, float]]] = defaultdict(list)
        for r in rows:
            grouped[r["simulation_id"]].append((r["month"], r["tau_t"]))
        # Sort sim_ids and per-sim months for deterministic shape.
        sim_ids = sorted(grouped.keys())
        # Determine horizon T from the first sim's month count.
        if not sim_ids:
            raise ValueError(
                "PosteriorTauReader: no rows found in synthetic_tau_t dataset"
            )
        n_months = len(grouped[sim_ids[0]])
        out = np.empty((len(sim_ids), n_months), dtype=np.float64)
        for i, sid in enumerate(sim_ids):
            sorted_pairs = sorted(grouped[sid])
            if len(sorted_pairs) != n_months:
                raise ValueError(
                    "PosteriorTauReader: simulation_id"
                    f" {sid} has {len(sorted_pairs)} months;"
                    f" expected {n_months}"
                )
            for j, (_m, tau) in enumerate(sorted_pairs):
                out[i, j] = tau
        return out


# ─── GateVerdictWriter ───────────────────────────────────────────────────────


class GateVerdictWriter:
    """IO Boundary — emit ``gate_verdict.json`` per spec §10 line 520.

    Schema (verbatim spec §10): ``{"sub_task": "COHORT-2", "verdict":
    "PASS|WEAK|MARGINAL|FAIL|INDISTINGUISHABLE", "evidence": [...],
    "audit_block": str, "fetched_at_utc": str, "ppc_coverage": {...},
    "n_bracket_points": int, "n_sign_violations": int}``.
    """

    _base_dir: Path

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._base_dir = (
            Path(base_dir)
            if base_dir is not None
            else DEFAULT_ESTIMATES_DIR
        )

    def __call__(
        self, verdict: CohortGateVerdict, filename: str = "gate_verdict.json"
    ) -> Path:
        """Write the verdict to ``<base_dir>/<filename>`` and return the path.

        Pin ROBUST-BS guard: this writer ONLY persists the primary
        verdict; robustness verdicts route through
        :class:`RobustnessResultsAppender`. Callers MUST verify
        ``verdict.sub_task == "COHORT-2"`` (the dataclass enforces this
        already; the assertion here is a defense-in-depth restatement).
        """
        if verdict.sub_task != "COHORT-2":
            raise ValueError(
                f"GateVerdictWriter: verdict.sub_task = {verdict.sub_task!r}"
                " must equal 'COHORT-2'"
            )
        payload = {
            "sub_task": verdict.sub_task,
            "verdict": verdict.verdict,
            "n_bracket_points": verdict.n_bracket_points,
            "n_sign_violations": verdict.n_sign_violations,
            "evidence": [
                {
                    "bracket_index": ev.bracket_index,
                    "delta_median": ev.delta_median,
                    "delta_lower_bound_quantile": ev.delta_lower_bound_quantile,
                    "delta_upper_bound_quantile": ev.delta_upper_bound_quantile,
                    "ci_level": ev.ci_level,
                    "sign_strictly_negative": ev.sign_strictly_negative,
                }
                for ev in verdict.evidence
            ],
            "ppc_coverage": dict(verdict.ppc_coverage),
            "audit_block": verdict.audit_block,
            "fetched_at_utc": verdict.fetched_at_utc,
        }
        self._base_dir.mkdir(parents=True, exist_ok=True)
        out = self._base_dir / filename
        try:
            out.write_text(json.dumps(payload, indent=2, sort_keys=True))
        except OSError as e:
            raise OSError(
                f"GateVerdictWriter: failed to write {out}: {e}"
            ) from e
        return out


# ─── RobustnessResultsAppender ───────────────────────────────────────────────


class RobustnessResultsAppender:
    """IO Boundary — append bank-spread arm result to ``ROBUSTNESS_RESULTS.md``.

    Pin ROBUST-BS — the robustness arm's verdict is logged separately
    from the primary; this writer ONLY mutates ``ROBUSTNESS_RESULTS.md``,
    NEVER ``gate_verdict.json``.
    """

    _base_dir: Path

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self._base_dir = (
            Path(base_dir)
            if base_dir is not None
            else DEFAULT_ESTIMATES_DIR
        )

    def __call__(
        self,
        robustness_verdict: CohortGateVerdict,
        bank_spread: float,
        filename: str = "ROBUSTNESS_RESULTS.md",
    ) -> Path:
        """Append a markdown section for the bank-spread arm.

        Args:
            robustness_verdict: the overlaid-FX-path verdict from
                :class:`BankSpreadRobustnessRunner`.
            bank_spread: the scalar overlay used.
            filename: target file under ``base_dir``.

        Returns:
            The path of the appended file.
        """
        self._base_dir.mkdir(parents=True, exist_ok=True)
        out = self._base_dir / filename
        if not out.is_file():
            out.write_text(
                "# COHORT-2 Robustness — Bank-Spread Sensitivity Arm\n\n"
                "Pin ROBUST-BS — bank-spread overlay sensitivity arm,\n"
                "walled off from the primary `gate_verdict.json`.\n\n"
            )
        section = _format_robustness_section(robustness_verdict, bank_spread)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(section)
        return out


def _format_robustness_section(
    verdict: CohortGateVerdict, bank_spread: float
) -> str:
    """Format one robustness-arm section as markdown."""
    lines = [
        "",
        f"## Bank-spread = {bank_spread:+.4f}"
        f" ({verdict.fetched_at_utc})",
        "",
        f"- verdict: **{verdict.verdict}**",
        f"- n_bracket_points: {verdict.n_bracket_points}",
        f"- n_sign_violations: {verdict.n_sign_violations}",
        f"- audit_block: `{verdict.audit_block}`",
        "",
        "| bracket_index | Δ median | CI lower | CI upper | ci_level | strict<0 |",
        "|---|---|---|---|---|---|",
    ]
    for ev in verdict.evidence:
        lines.append(
            f"| {ev.bracket_index}"
            f" | {ev.delta_median:+.6e}"
            f" | {ev.delta_lower_bound_quantile:+.6e}"
            f" | {ev.delta_upper_bound_quantile:+.6e}"
            f" | {ev.ci_level:.2f}"
            f" | {'YES' if ev.sign_strictly_negative else 'NO'} |"
        )
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "DEFAULT_ESTIMATES_DIR",
    "GateVerdictWriter",
    "PosteriorTauReader",
    "RobustnessResultsAppender",
]
