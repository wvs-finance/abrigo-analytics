r"""IO Boundary tier for the stochastic-fx variant — Task 5 emitters.

Per the functional-python skill: this is the ONLY tier where mutable
state and external IO live. All classes have ``__init__`` (not frozen-dc).

Emitters delivered:

- :class:`PathEnsembleEmitter` — writes one parquet file per
  :class:`~simulations.stochastic_fx.types.PathEnsemble` at
  ``{emit_dir}/path_ensemble_{family_id}.parquet`` (long-format, one row per
  ``(path_index, step_index, x_t)`` triple). Parquet schema-level metadata
  carries ``canonical_params_json``, ``audit_block``, and ``rng_seed`` so
  the on-disk artefact is self-describing. Round-trip readback re-applies
  spec v0.3 §6 eq. (7) via
  :func:`simulations.stochastic_fx.variance_proxy.recompute_sigma_t` to
  reconstruct the per-path σ_T vector.
- :class:`InversionVerdictEmitter` — writes one JSON v1.0 file per
  :class:`~simulations.stochastic_fx.types.InversionVerdict` at
  ``{emit_dir}/inversion_verdict_{family_id}.json``. The on-disk schema
  carries all 12 verdict fields plus the three :mod:`variance_proxy`
  tolerance constants (FLAG-RC-3 single-source-of-truth) plus a
  ``schema_version`` and ``emitted_at_utc`` stamp.
- :class:`TexFragmentEmitter` — existence-only re-emit (Task 2.1 wrote
  the bytes; this class confirms the artefact survives at the canonical
  ``notes/stochastic_fx_tex/sigma_t_moments_{family_id}.tex`` path).
- :class:`StochasticFxResultsEmitter` — writes ``notes/STOCHASTIC_FX_RESULTS.md``
  in the same R-tagged + cross-family-summary-table format as
  ``notes/STAGE_2_RESULTS.md`` (the per-family parent).

Round-trip discipline (cohort_4 io.py precedent):
``PathEnsembleEmitter.emit_and_verify`` and
``InversionVerdictEmitter.emit_and_verify`` write, read, and compare
field-by-field; mismatch raises :class:`RoundTripDriftError`. The
markdown + tex emitters are committed human-readable artefacts and have
no readback (mirrors ``SignVerdictSidecarWriter`` in cohort_4).

Tier purity (functional-python — IO Boundary):

- Allowed: stdlib (``datetime``, ``json``, ``pathlib``, ``typing``);
  ``numpy``; ``pyarrow`` / ``pyarrow.parquet``;
  :mod:`simulations.stochastic_fx.types`;
  :mod:`simulations.stochastic_fx._errors`;
  :mod:`simulations.stochastic_fx.variance_proxy` (for tolerance constants
  and :func:`recompute_sigma_t`).
- FORBIDDEN at module load: sibling Callables
  :mod:`simulations.stochastic_fx.generators` and
  :mod:`simulations.stochastic_fx.moments` — emitters consume already-built
  Value containers; emission MUST NOT trigger generator sampling.
"""

from __future__ import annotations

import datetime as _datetime
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Final

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from simulations.stochastic_fx._errors import RoundTripDriftError
from simulations.stochastic_fx.types import InversionVerdict, PathEnsemble
from simulations.stochastic_fx.variance_proxy import (
    KS_PVALUE_FLOOR,
    MOMENT_REL_TOL,
    NUMERICAL_IDENTITY_TOL,
    recompute_sigma_t,
)

#: Default directory for the parquet + JSON sidecars (gitignored — see
#: ``.gitignore`` data/ rules; ``git check-ignore`` returns 0 for any
#: artefact under here).
DEFAULT_DATA_DIR: Final[Path] = Path("simulations/stochastic_fx/data")

#: Default directory for the LaTeX fragment re-emit existence check
#: (Task 2.1 wrote the bytes; this class only re-confirms the path).
DEFAULT_TEX_DIR: Final[Path] = Path("notes/stochastic_fx_tex")

#: Default directory for the human-readable results markdown.
DEFAULT_RESULTS_DIR: Final[Path] = Path("notes")

#: JSON sidecar schema version (Task 5 first-time emit per plan v0.6
#: §10). NOT subject to backwards-compat shims — the package is new at
#: this commit and no older readers exist.
SCHEMA_VERSION_V1_0: Final[str] = "v1.0"

#: Parquet metadata keys for ``PathEnsemble`` lineage fields. Keyed with
#: the ``stochastic_fx.`` prefix so the namespace cannot collide with
#: pyarrow's own pandas/index metadata keys.
_META_KEY_CANONICAL_PARAMS_JSON: Final[bytes] = b"stochastic_fx.canonical_params_json"
_META_KEY_AUDIT_BLOCK: Final[bytes] = b"stochastic_fx.audit_block"
_META_KEY_RNG_SEED: Final[bytes] = b"stochastic_fx.rng_seed"
_META_KEY_FAMILY_ID: Final[bytes] = b"stochastic_fx.family_id"


# ─── PathEnsembleEmitter ─────────────────────────────────────────────────────


class PathEnsembleEmitter:
    """Write / read a :class:`PathEnsemble` to / from parquet (IO Boundary).

    On-disk layout:

    - One parquet file per family at
      ``{emit_dir}/path_ensemble_{family_id}.parquet``.
    - Long-format rows: ``(path_index: int64, step_index: int64, x_t: float64)``.
      Row count is ``n_paths * (n_steps + 1)``.
    - Schema-level metadata key/value pairs carry ``canonical_params_json``,
      ``audit_block``, ``rng_seed`` (string-encoded), and ``family_id``.

    Round-trip discipline:
    :meth:`emit_and_verify` writes the file, reads it back via :meth:`read`,
    and asserts that the reconstructed ``PathEnsemble`` matches the original
    on the audit-block (verbatim hex equality), the
    ``canonical_params_json`` string, the ``rng_seed`` int, and the
    ``sigma_t`` array (within ``1e-12`` relative tolerance — the σ_T
    reconstruction is float-arithmetic-equivalent but not bit-identical
    to the original because :func:`recompute_sigma_t` follows the same
    formula but operates on the parquet-roundtripped path bytes).

    The :func:`recompute_sigma_t` path-mean+sum-of-squares formula matches
    the generators' inline computation exactly (see
    :mod:`simulations.stochastic_fx.generators` line ~183 for GBM, ~285 for
    OU, ~425 for Merton — all three families share the same eq. (7)
    statistic), so a parquet round-trip that preserves the path bytes
    byte-for-byte recovers the original σ_T to machine epsilon.
    """

    def __init__(self, emit_dir: str | Path | None = None) -> None:
        self._emit_dir: Path = (
            Path(emit_dir) if emit_dir is not None else DEFAULT_DATA_DIR
        )

    @property
    def emit_dir(self) -> Path:
        return self._emit_dir

    def _path_for(self, family_id: str) -> Path:
        return self._emit_dir / f"path_ensemble_{family_id}.parquet"

    def emit(self, ensemble: PathEnsemble) -> Path:
        """Write ``ensemble`` to parquet and return the on-disk path.

        The parquet rows are constructed in lex order on ``(path_index,
        step_index)`` so a downstream reader can re-pivot deterministically.
        Pyarrow's row ordering IS preserved across write/read (we re-sort
        defensively on read regardless).

        Parameters
        ----------
        ensemble:
            A validated :class:`PathEnsemble` (closed alphabet, finite
            arrays, valid audit_block — all guarded by
            :meth:`PathEnsemble.__post_init__`).

        Returns
        -------
        pathlib.Path
            Absolute or relative on-disk path of the written file.
        """
        n_paths, n_steps_plus_1 = ensemble.paths.shape
        # Long-format triples — one row per (path_index, step_index, x_t).
        path_idx = np.repeat(
            np.arange(n_paths, dtype=np.int64), n_steps_plus_1
        )
        step_idx = np.tile(
            np.arange(n_steps_plus_1, dtype=np.int64), n_paths
        )
        x_t = ensemble.paths.reshape(-1).astype(np.float64, copy=False)

        table = pa.Table.from_pydict(
            {
                "path_index": path_idx,
                "step_index": step_idx,
                "x_t": x_t,
            }
        )
        # Attach lineage metadata to the schema. Pyarrow metadata must be
        # ``dict[bytes, bytes]`` — encode every value to UTF-8.
        meta: dict[bytes, bytes] = {
            _META_KEY_CANONICAL_PARAMS_JSON: ensemble.canonical_params_json.encode(
                "utf-8"
            ),
            _META_KEY_AUDIT_BLOCK: ensemble.audit_block.encode("utf-8"),
            _META_KEY_RNG_SEED: str(ensemble.rng_seed).encode("utf-8"),
            _META_KEY_FAMILY_ID: ensemble.family_id.encode("utf-8"),
        }
        table = table.replace_schema_metadata(meta)

        self._emit_dir.mkdir(parents=True, exist_ok=True)
        target = self._path_for(ensemble.family_id)
        pq.write_table(table, target)
        return target

    def read(self, family_id: str) -> PathEnsemble:
        """Read the parquet at ``{emit_dir}/path_ensemble_{family_id}.parquet``.

        Reconstructs the ``paths`` matrix by pivoting the long-format rows
        on ``(path_index, step_index)`` and recomputes ``sigma_t`` from
        the path bytes via :func:`recompute_sigma_t` (the same eq. (7)
        statistic the generators emit; see class docstring).

        Parameters
        ----------
        family_id:
            One of ``{"gbm", "ou", "merton"}``. The corresponding parquet
            must exist on disk (else :class:`FileNotFoundError`).

        Returns
        -------
        PathEnsemble
            Reconstructed ensemble; the constructor re-validates via
            :meth:`PathEnsemble.__post_init__`.

        Raises
        ------
        FileNotFoundError
            Target parquet missing.
        RoundTripDriftError
            Parquet metadata missing one of the required lineage keys.
        """
        target = self._path_for(family_id)
        if not target.is_file():
            raise FileNotFoundError(
                f"PathEnsembleEmitter: missing parquet at {target}"
            )
        table = pq.read_table(target)
        schema_meta = table.schema.metadata or {}

        def _require_meta(key: bytes) -> bytes:
            if key not in schema_meta:
                raise RoundTripDriftError(
                    f"PathEnsembleEmitter.read: parquet at {target} missing "
                    f"metadata key {key!r}; cannot reconstruct PathEnsemble"
                )
            return schema_meta[key]

        canonical_params_json = _require_meta(
            _META_KEY_CANONICAL_PARAMS_JSON
        ).decode("utf-8")
        audit_block = _require_meta(_META_KEY_AUDIT_BLOCK).decode("utf-8")
        rng_seed_str = _require_meta(_META_KEY_RNG_SEED).decode("utf-8")
        rng_seed = int(rng_seed_str)
        on_disk_family_id = _require_meta(_META_KEY_FAMILY_ID).decode("utf-8")
        if on_disk_family_id != family_id:
            raise RoundTripDriftError(
                f"PathEnsembleEmitter.read: family_id mismatch — "
                f"requested {family_id!r}, parquet metadata carries "
                f"{on_disk_family_id!r}"
            )

        # Pivot long-format rows back to (n_paths, n_steps + 1).
        path_idx = table.column("path_index").to_numpy().astype(np.int64)
        step_idx = table.column("step_index").to_numpy().astype(np.int64)
        x_t = table.column("x_t").to_numpy().astype(np.float64)
        n_paths = int(path_idx.max()) + 1
        n_steps_plus_1 = int(step_idx.max()) + 1
        if path_idx.shape[0] != n_paths * n_steps_plus_1:
            raise RoundTripDriftError(
                f"PathEnsembleEmitter.read: row count {path_idx.shape[0]} "
                f"!= n_paths * (n_steps + 1) = {n_paths * n_steps_plus_1}"
            )
        # Sort defensively in case pyarrow's row ordering ever drifts.
        sort_keys = path_idx.astype(np.int64) * n_steps_plus_1 + step_idx
        order = np.argsort(sort_keys, kind="stable")
        paths = x_t[order].reshape(n_paths, n_steps_plus_1)

        # σ_T reconstruction via recompute_sigma_t — same formula as the
        # generators' inline computation, byte-faithful path matrix.
        # Build a transient PathEnsemble with a placeholder sigma_t for
        # the recomputation, then construct the final returned ensemble
        # with the recomputed array.
        placeholder_sigma_t = np.zeros(n_paths, dtype=np.float64)
        transient = PathEnsemble(
            family_id=family_id,
            paths=paths,
            sigma_t=placeholder_sigma_t,
            canonical_params_json=canonical_params_json,
            rng_seed=rng_seed,
            audit_block=audit_block,
        )
        sigma_t = recompute_sigma_t(transient)

        return PathEnsemble(
            family_id=family_id,
            paths=paths,
            sigma_t=sigma_t,
            canonical_params_json=canonical_params_json,
            rng_seed=rng_seed,
            audit_block=audit_block,
        )

    def emit_and_verify(self, ensemble: PathEnsemble) -> Path:
        """Write + read + round-trip-verify; raise :class:`RoundTripDriftError` on drift.

        Comparison semantics:

        - ``audit_block`` — verbatim hex equality (no float tolerance).
        - ``canonical_params_json`` — verbatim string equality.
        - ``rng_seed`` — exact int equality.
        - ``family_id`` — verbatim string equality.
        - ``sigma_t`` — ``np.allclose(rtol=1e-12)`` (re-computed via
          eq. (7); float-arithmetic-equivalent to the original).
        - ``paths`` — ``np.array_equal`` (parquet preserves float64 bytes
          exactly via pyarrow's typed columns).
        """
        target = self.emit(ensemble)
        round_tripped = self.read(ensemble.family_id)

        if round_tripped.audit_block != ensemble.audit_block:
            raise RoundTripDriftError(
                "PathEnsembleEmitter.emit_and_verify: audit_block drift — "
                f"wrote {ensemble.audit_block!r}, read back "
                f"{round_tripped.audit_block!r}"
            )
        if round_tripped.canonical_params_json != ensemble.canonical_params_json:
            raise RoundTripDriftError(
                "PathEnsembleEmitter.emit_and_verify: canonical_params_json "
                f"drift — wrote {ensemble.canonical_params_json!r}, read back "
                f"{round_tripped.canonical_params_json!r}"
            )
        if round_tripped.rng_seed != ensemble.rng_seed:
            raise RoundTripDriftError(
                "PathEnsembleEmitter.emit_and_verify: rng_seed drift — "
                f"wrote {ensemble.rng_seed!r}, read back {round_tripped.rng_seed!r}"
            )
        if round_tripped.family_id != ensemble.family_id:
            raise RoundTripDriftError(
                "PathEnsembleEmitter.emit_and_verify: family_id drift — "
                f"wrote {ensemble.family_id!r}, read back "
                f"{round_tripped.family_id!r}"
            )
        if not np.array_equal(round_tripped.paths, ensemble.paths):
            raise RoundTripDriftError(
                "PathEnsembleEmitter.emit_and_verify: paths byte-drift — "
                "parquet round-trip did not preserve the path matrix"
            )
        if not np.allclose(
            round_tripped.sigma_t, ensemble.sigma_t, rtol=1e-12, atol=0.0
        ):
            raise RoundTripDriftError(
                "PathEnsembleEmitter.emit_and_verify: sigma_t drift > 1e-12 "
                "rtol — eq.(7) recomputation did not match the original"
            )
        return target


# ─── InversionVerdictEmitter ─────────────────────────────────────────────────


class InversionVerdictEmitter:
    """Write / read an :class:`InversionVerdict` to / from JSON (IO Boundary).

    On-disk layout:

    - One JSON file per family at
      ``{emit_dir}/inversion_verdict_{family_id}.json``.
    - Schema v1.0 fields: all 12 :class:`InversionVerdict` fields
      (``family_id``, three phase-pass bools + three phase-residual /
      rel-err / p-value floats, ``phase_c_n_paths``, ``composite_pass``,
      ``tex_anchor``, ``audit_block``) PLUS three tolerance constants
      imported from :mod:`simulations.stochastic_fx.variance_proxy`
      (``phase_a_tolerance = NUMERICAL_IDENTITY_TOL``,
      ``phase_b_tolerance = MOMENT_REL_TOL``,
      ``phase_c_tolerance = KS_PVALUE_FLOOR``) per FLAG-RC-3
      single-source-of-truth, PLUS ``schema_version`` and ``emitted_at_utc``.
    - Byte-stable serialization: ``json.dumps(..., indent=2, sort_keys=True)``.

    Round-trip discipline: :meth:`emit_and_verify` writes, reads back, and
    asserts field-by-field equality on the 12 verdict fields (the three
    tolerance constants are informational and not re-checked — they're
    re-imported live on every emission so changes there would invalidate
    the audit-block-bound digest upstream, not the JSON round-trip).
    """

    def __init__(self, emit_dir: str | Path | None = None) -> None:
        self._emit_dir: Path = (
            Path(emit_dir) if emit_dir is not None else DEFAULT_DATA_DIR
        )

    @property
    def emit_dir(self) -> Path:
        return self._emit_dir

    def _path_for(self, family_id: str) -> Path:
        return self._emit_dir / f"inversion_verdict_{family_id}.json"

    def emit(self, verdict: InversionVerdict) -> Path:
        """Write ``verdict`` to JSON and return the on-disk path.

        The emitted payload is sorted, indented JSON; re-emits at fixed
        inputs are byte-stable (``emitted_at_utc`` aside).
        """
        payload: dict[str, object] = {
            "family_id": verdict.family_id,
            "phase_a_pass": verdict.phase_a_pass,
            "phase_a_max_residual": verdict.phase_a_max_residual,
            "phase_b_pass": verdict.phase_b_pass,
            "phase_b_mean_rel_err": verdict.phase_b_mean_rel_err,
            "phase_b_var_rel_err": verdict.phase_b_var_rel_err,
            "phase_c_pass": verdict.phase_c_pass,
            "phase_c_ks_pvalue": verdict.phase_c_ks_pvalue,
            "phase_c_n_paths": verdict.phase_c_n_paths,
            "composite_pass": verdict.composite_pass,
            "tex_anchor": verdict.tex_anchor,
            "audit_block": verdict.audit_block,
            # FLAG-RC-3 disposition: tolerance constants flow from
            # variance_proxy.py (single source of truth) so the sidecar
            # records the gate-of-record at emit time. Informational —
            # ignored on read-back.
            "phase_a_tolerance": NUMERICAL_IDENTITY_TOL,
            "phase_b_tolerance": MOMENT_REL_TOL,
            "phase_c_tolerance": KS_PVALUE_FLOOR,
            "schema_version": SCHEMA_VERSION_V1_0,
            "emitted_at_utc": _datetime.datetime.now(
                _datetime.timezone.utc
            ).isoformat(),
        }
        self._emit_dir.mkdir(parents=True, exist_ok=True)
        target = self._path_for(verdict.family_id)
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
        return target

    def read(self, family_id: str) -> InversionVerdict:
        """Read the JSON at ``{emit_dir}/inversion_verdict_{family_id}.json``.

        Validates ``schema_version == "v1.0"`` and reconstructs the
        :class:`InversionVerdict` via its frozen-dc constructor (which
        re-applies the composite-AND invariant + finite checks).

        Raises
        ------
        FileNotFoundError
            Target JSON missing.
        RoundTripDriftError
            Schema-version mismatch or missing required fields.
        """
        target = self._path_for(family_id)
        if not target.is_file():
            raise FileNotFoundError(
                f"InversionVerdictEmitter: missing JSON at {target}"
            )
        payload = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RoundTripDriftError(
                f"InversionVerdictEmitter.read: top-level value at {target} "
                f"must be a JSON object; got {type(payload).__name__}"
            )
        on_disk_schema = payload.get("schema_version")
        if on_disk_schema != SCHEMA_VERSION_V1_0:
            raise RoundTripDriftError(
                f"InversionVerdictEmitter.read: schema_version mismatch — "
                f"expected {SCHEMA_VERSION_V1_0!r}, got {on_disk_schema!r}"
            )
        required_keys: tuple[str, ...] = (
            "family_id",
            "phase_a_pass",
            "phase_a_max_residual",
            "phase_b_pass",
            "phase_b_mean_rel_err",
            "phase_b_var_rel_err",
            "phase_c_pass",
            "phase_c_ks_pvalue",
            "phase_c_n_paths",
            "composite_pass",
            "tex_anchor",
            "audit_block",
        )
        missing = [k for k in required_keys if k not in payload]
        if missing:
            raise RoundTripDriftError(
                f"InversionVerdictEmitter.read: JSON at {target} missing "
                f"required field(s) {missing!r}"
            )
        return InversionVerdict(
            family_id=str(payload["family_id"]),
            phase_a_pass=bool(payload["phase_a_pass"]),
            phase_a_max_residual=float(payload["phase_a_max_residual"]),
            phase_b_pass=bool(payload["phase_b_pass"]),
            phase_b_mean_rel_err=float(payload["phase_b_mean_rel_err"]),
            phase_b_var_rel_err=float(payload["phase_b_var_rel_err"]),
            phase_c_pass=bool(payload["phase_c_pass"]),
            phase_c_ks_pvalue=float(payload["phase_c_ks_pvalue"]),
            phase_c_n_paths=int(payload["phase_c_n_paths"]),
            composite_pass=bool(payload["composite_pass"]),
            tex_anchor=str(payload["tex_anchor"]),
            audit_block=str(payload["audit_block"]),
        )

    def emit_and_verify(self, verdict: InversionVerdict) -> Path:
        """Write + read + field-by-field equality check; raise on drift.

        All 12 :class:`InversionVerdict` fields are compared. Floats use
        relative tolerance ``1e-15`` (JSON ``json.dumps``/``json.loads``
        round-trip is bit-exact for finite float64 values per CPython's
        ``repr``/``float`` semantics; the tolerance is defence-in-depth).
        """
        target = self.emit(verdict)
        round_tripped = self.read(verdict.family_id)
        _assert_verdict_fields_equal(verdict, round_tripped)
        return target


def _assert_verdict_fields_equal(
    a: InversionVerdict, b: InversionVerdict
) -> None:
    """Raise :class:`RoundTripDriftError` if ``a`` and ``b`` differ on any field.

    Exact equality on bools / ints / strings; ``1e-15`` relative tolerance
    on floats (JSON round-trip preserves float64 bit-exactness for finite
    values in CPython but the explicit tolerance documents the contract).
    """
    for name in (
        "family_id",
        "phase_a_pass",
        "phase_b_pass",
        "phase_c_pass",
        "composite_pass",
        "phase_c_n_paths",
        "tex_anchor",
        "audit_block",
    ):
        if getattr(a, name) != getattr(b, name):
            raise RoundTripDriftError(
                f"InversionVerdictEmitter.emit_and_verify: {name} drift — "
                f"wrote {getattr(a, name)!r}, read back {getattr(b, name)!r}"
            )
    for name in (
        "phase_a_max_residual",
        "phase_b_mean_rel_err",
        "phase_b_var_rel_err",
        "phase_c_ks_pvalue",
    ):
        fa = getattr(a, name)
        fb = getattr(b, name)
        if not (abs(fa - fb) <= 1e-15 * max(1.0, abs(fa))):
            raise RoundTripDriftError(
                f"InversionVerdictEmitter.emit_and_verify: {name} float drift "
                f"— wrote {fa!r}, read back {fb!r}"
            )


# ─── TexFragmentEmitter ──────────────────────────────────────────────────────


class TexFragmentEmitter:
    """Existence-check re-emitter for the Task 2.1 per-family .tex fragments.

    Task 2.1 wrote the bytes under ``notes/stochastic_fx_tex/`` (committed
    artefacts). This class is the IO-Boundary surface for the re-emit
    workflow (Task 6 end-to-end): it confirms the artefact survives at
    the expected path but does NOT regenerate the LaTeX. Re-generation
    is the job of ``scripts/emit_stochastic_fx_tex.py`` (Task 2.1).
    """

    def __init__(self, emit_dir: str | Path | None = None) -> None:
        self._emit_dir: Path = (
            Path(emit_dir) if emit_dir is not None else DEFAULT_TEX_DIR
        )

    @property
    def emit_dir(self) -> Path:
        return self._emit_dir

    def _path_for(self, family_id: str) -> Path:
        return self._emit_dir / f"sigma_t_moments_{family_id}.tex"

    def emit(self, family_id: str) -> Path:
        """Return the committed tex path; raise :class:`FileNotFoundError` if absent.

        Parameters
        ----------
        family_id:
            One of ``{"gbm", "ou", "merton"}``.

        Returns
        -------
        pathlib.Path
            ``{emit_dir}/sigma_t_moments_{family_id}.tex``. Existence is
            verified; the file is NOT rewritten.

        Raises
        ------
        FileNotFoundError
            The tex fragment is missing. The recovery path is to run
            ``scripts/emit_stochastic_fx_tex.py`` (Task 2.1) — this
            emitter is re-emit-only.
        """
        target = self._path_for(family_id)
        if not target.is_file():
            raise FileNotFoundError(
                f"TexFragmentEmitter: missing tex fragment at {target}; "
                "re-run scripts/emit_stochastic_fx_tex.py (Task 2.1) to "
                "regenerate it."
            )
        return target


# ─── StochasticFxResultsEmitter ──────────────────────────────────────────────


class StochasticFxResultsEmitter:
    """Write ``notes/STOCHASTIC_FX_RESULTS.md`` from a tuple of verdicts.

    Format mirrors ``notes/STAGE_2_RESULTS.md``:

    - Header section with cross-family summary table.
    - Per-family R-tagged subsections (R1 = GBM, R2 = OU, R3 = Merton)
      carrying composite_pass, Phase A residual, Phase B mean + var
      rel-errs (Phase B var is audit-trail-only under v0.5 §11.6
      disposition — still emitted for transparency), Phase C KS p-value,
      audit_block hex, and tex_anchor link.
    - Citations to parent spec v0.5 §11.6 (Phase B mean-only gate) +
      §11.7 (Phase C per-family reference dispatch — Merton empirical-CDF
      via high-N reference run).

    No round-trip readback: markdown is human-readable, not deserialized.
    """

    #: R-tag order across families (mirrors STAGE_2_RESULTS §2 R-tag
    #: convention — small integers, family-fixed).
    _FAMILY_R_TAGS: Final[dict[str, str]] = {
        "gbm": "R1",
        "ou": "R2",
        "merton": "R3",
    }

    #: Human-readable display labels per family (used in the cross-family
    #: summary table + section headings).
    _FAMILY_LABELS: Final[dict[str, str]] = {
        "gbm": "Geometric Brownian motion",
        "ou": "Ornstein-Uhlenbeck",
        "merton": "Merton jump-diffusion",
    }

    def __init__(self, emit_dir: str | Path | None = None) -> None:
        self._emit_dir: Path = (
            Path(emit_dir) if emit_dir is not None else DEFAULT_RESULTS_DIR
        )

    @property
    def emit_dir(self) -> Path:
        return self._emit_dir

    @property
    def results_path(self) -> Path:
        return self._emit_dir / "STOCHASTIC_FX_RESULTS.md"

    def emit(self, verdicts: Sequence[InversionVerdict]) -> Path:
        """Render the markdown and write to ``{emit_dir}/STOCHASTIC_FX_RESULTS.md``.

        Parameters
        ----------
        verdicts:
            Sequence of :class:`InversionVerdict` — one per family. Order
            is preserved in the per-family subsection rendering; the
            cross-family summary table is sorted by R-tag for stability.

        Returns
        -------
        pathlib.Path
            On-disk path of the written markdown.
        """
        body = self._render(verdicts)
        self._emit_dir.mkdir(parents=True, exist_ok=True)
        target = self.results_path
        target.write_text(body, encoding="utf-8")
        return target

    def _render(self, verdicts: Sequence[InversionVerdict]) -> str:
        """Build the markdown body. Pure-string method (no IO)."""
        # Stable sort on R-tag for the cross-family summary table.
        sorted_verdicts: list[InversionVerdict] = sorted(
            verdicts,
            key=lambda v: self._FAMILY_R_TAGS.get(v.family_id, "Z"),
        )

        lines: list[str] = []
        lines.append("# STOCHASTIC_FX_RESULTS — Stochastic-FX variant verdicts")
        lines.append("")
        lines.append(
            "Stage-3 open-item 2 (per `notes/STAGE_2_RESULTS.md` §5) closure: "
            "three-phase verification (algebraic / moment-match / KS goodness-"
            "of-fit) for the GBM, OU, and Merton jump-diffusion stochastic-FX "
            "families. R-tag prefix continues the STAGE_2_RESULTS R-tag "
            "lineage; Z1.x pins are spec v0.5 anchors."
        )
        lines.append("")
        lines.append(
            "Parent spec citations: §11.6 (Pin Z1.3b mean-only Phase-B gate; "
            "variance rel-err is audit-trail observation, not a gate); §11.7 "
            "(Pin Z1.4 per-family Phase-C reference dispatch — Merton uses "
            "empirical-CDF via high-N reference run at pinned "
            "`N_REF = 100_000`, `N_REF_SEED = 20260513`)."
        )
        lines.append("")

        # ── Cross-family summary table ──────────────────────────────────────
        lines.append("## §1 Cross-family summary")
        lines.append("")
        lines.append(
            "| R-tag | Family | composite_pass | Phase A max_residual | "
            "Phase B mean_rel_err | Phase C KS p-value | audit_block (prefix) |"
        )
        lines.append(
            "|---|---|---|---|---|---|---|"
        )
        for v in sorted_verdicts:
            r_tag = self._FAMILY_R_TAGS.get(v.family_id, "?")
            label = self._FAMILY_LABELS.get(v.family_id, v.family_id)
            lines.append(
                f"| {r_tag} | {label} | "
                f"{'PASS' if v.composite_pass else 'FAIL'} | "
                f"{v.phase_a_max_residual:.3e} | "
                f"{v.phase_b_mean_rel_err:.3e} | "
                f"{v.phase_c_ks_pvalue:.3e} | "
                f"`{v.audit_block[:16]}…` |"
            )
        lines.append("")

        # ── Per-family R-tagged subsections ─────────────────────────────────
        lines.append("## §2 Per-family verdicts")
        lines.append("")
        for v in sorted_verdicts:
            r_tag = self._FAMILY_R_TAGS.get(v.family_id, "?")
            label = self._FAMILY_LABELS.get(v.family_id, v.family_id)
            lines.append(f"### §2.{r_tag[1:]} {label} ({r_tag})")
            lines.append("")
            lines.append(
                f"- **composite_pass**: "
                f"{'PASS' if v.composite_pass else 'FAIL'}"
            )
            lines.append(
                f"- **Phase A** (Pin Z1.3a algebraic identity, "
                f"tol = `NUMERICAL_IDENTITY_TOL`): "
                f"`max_residual = {v.phase_a_max_residual:.6e}`, "
                f"pass = {v.phase_a_pass}"
            )
            lines.append(
                f"- **Phase B** (Pin Z1.3b mean-only, "
                f"tol = `MOMENT_REL_TOL = {MOMENT_REL_TOL}` — spec v0.5 §11.6): "
                f"`mean_rel_err = {v.phase_b_mean_rel_err:.6e}`, "
                f"`var_rel_err = {v.phase_b_var_rel_err:.6e}` "
                f"(audit-trail only — does NOT gate composite_pass), "
                f"pass = {v.phase_b_pass}"
            )
            lines.append(
                f"- **Phase C** (Pin Z1.4 KS goodness-of-fit, "
                f"floor = `KS_PVALUE_FLOOR = {KS_PVALUE_FLOOR}` — spec v0.5 "
                f"§11.7 per-family reference dispatch): "
                f"`ks_pvalue = {v.phase_c_ks_pvalue:.6e}`, "
                f"`n_paths = {v.phase_c_n_paths}` (TEST sample; N_REF for "
                f"Merton reference recorded in audit_block, not here), "
                f"pass = {v.phase_c_pass}"
            )
            lines.append(
                f"- **audit_block**: `{v.audit_block}`"
            )
            lines.append(
                f"- **tex_anchor**: [{v.tex_anchor}](../{v.tex_anchor})"
            )
            lines.append("")

        # ── References ──────────────────────────────────────────────────────
        lines.append("## §3 References")
        lines.append("")
        lines.append(
            "- `docs/specs/2026-05-11-stochastic-fx-variant-design.md` v0.5 — "
            "parent spec; §6 three-phase verification; §11.6 (Pin Z1.3b "
            "mean-only Phase-B gate); §11.7 (Pin Z1.4 per-family Phase-C "
            "reference dispatch)."
        )
        lines.append(
            "- `docs/plans/2026-05-11-stochastic-fx-variant.md` v0.6 — "
            "implementation plan; §10 Task 5 (this emitter); §16.5 + §16.7 "
            "(CORRECTIONS-α landing the v0.4→v0.5→v0.6 amendments)."
        )
        lines.append(
            "- `notes/STAGE_2_RESULTS.md` §5 — Stage-3 open-item 2 hand-off "
            "(stochastic-FX variant per PRIMITIVES.md §15 open item 2)."
        )
        lines.append("")
        return "\n".join(lines)


__all__ = [
    "DEFAULT_DATA_DIR",
    "DEFAULT_RESULTS_DIR",
    "DEFAULT_TEX_DIR",
    "InversionVerdictEmitter",
    "PathEnsembleEmitter",
    "SCHEMA_VERSION_V1_0",
    "StochasticFxResultsEmitter",
    "TexFragmentEmitter",
]
