r"""IO Boundary tier for SAAS-COHORT-5 — IronCondor strip emit.

Per the functional-python skill: this is the ONLY tier where mutable
state and external IO live. All classes have ``__init__`` (not frozen-dc).

Pin coverage:

- **Pin S7 — strip-artifact emit.** ``StripEmitter`` reads the cohort-4
  ``Z_cap_pinned.json`` artifact, builds the 3-condor strip, runs the
  replication-envelope verifier, and writes
  ``IronCondor_strip.json`` (schema v1.0) into
  ``simulations/saas_builder/data/``. The sidecar markdown summary
  ``IronCondor_strip.STRIKES.md`` enumerates all 12 legs in a
  human-readable table.
- **Pin S8 — audit-block lineage.** The strip's ``audit_block`` is a
  sha256 over the cohort-4 ``audit_block`` field + the canonical spec
  path + the strip-geometry parameters (serialized canonically). Any
  upstream input drift produces a deterministically-different digest.
- **Round-trip.** After write, the emitter reads the just-written JSON
  and asserts field-by-field equality (defense-in-depth against silent
  filesystem drift).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from simulations.saas_builder.cohort_5_strip._errors import (
    AuditBlockDriftError,
    StripGeometryError,
)
from simulations.saas_builder.cohort_5_strip.geometry import (
    DEFAULT_PRIMITIVES_ANCHOR,
    DEFAULT_SAAS_NOTE_ANCHOR,
    StripBuilder,
    default_strip_geometry,
)
from simulations.saas_builder.cohort_5_strip.replication import (
    CarrMadanEnvelopeVerifier,
    assert_long_vol_signature,
)
from simulations.saas_builder.cohort_5_strip.types import (
    IronCondorStrip,
    ReplicationVerdict,
    StripGeometry,
)
from simulations.utils.json_io import ZCapPinnedReader

#: Default emission directory (mirror of cohort_4 location).
DEFAULT_EMIT_DIR: Final[Path] = Path("simulations/saas_builder/data")

#: Filename for the strip JSON artifact (schema v1.0).
STRIP_JSON_FILENAME: Final[str] = "IronCondor_strip.json"

#: Filename for the strip strikes sidecar (markdown).
STRIP_SIDECAR_FILENAME: Final[str] = "IronCondor_strip.STRIKES.md"

#: Schema version of the strip artifact.
STRIP_SCHEMA_VERSION: Final[str] = "v1.0"

#: Canonical Z_cap source file (read input).
DEFAULT_Z_CAP_PATH: Final[Path] = DEFAULT_EMIT_DIR / "Z_cap_pinned.json"

#: Canonical spec path included in the audit-block lineage.
DEFAULT_SPEC_PATH: Final[str] = (
    "docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md"
)


def _serialize_strip(strip: IronCondorStrip) -> dict[str, Any]:
    """Convert a frozen-dc strip to a JSON-serializable dict.

    The serialization is deterministic: keys are emitted in a fixed
    order; legs are listed per :data:`LEG_KIND_ORDER`. This determinism
    is necessary for the audit-block lineage check.
    """
    condors_payload = []
    for condor in strip.condors:
        legs_payload = [
            {"kind": leg.kind, "strike": leg.strike}
            for leg in condor.legs
        ]
        condors_payload.append(
            {
                "label": condor.label,
                "center": condor.center,
                "weight": condor.weight,
                "legs": legs_payload,
            }
        )
    return {
        "schema_version": STRIP_SCHEMA_VERSION,
        "s_0": strip.s_0,
        "sigma_0": strip.sigma_0,
        "k_star": strip.k_star,
        "k_hat": strip.k_hat,
        "geometry": {
            "log_offsets": list(strip.geometry.log_offsets),
            "delta_inner": strip.geometry.delta_inner,
            "delta_outer": strip.geometry.delta_outer,
        },
        "condors": condors_payload,
        "primitives_anchor": strip.primitives_anchor,
        "saas_note_anchor": strip.saas_note_anchor,
    }


def _compute_strip_audit_block(
    z_cap_audit_block: str,
    spec_path: str,
    strip_payload: Mapping[str, Any],
) -> str:
    """Return sha256 over (z_cap audit + spec path + canonical strip JSON).

    Determinism: the strip payload is dumped with ``sort_keys=True`` and
    ``separators=(",", ":")`` to lock the byte representation against
    cosmetic re-ordering.
    """
    h = hashlib.sha256()
    h.update(b"--- z_cap_audit ---\n")
    h.update(z_cap_audit_block.encode("ascii"))
    h.update(b"\n--- spec_path ---\n")
    h.update(spec_path.encode("utf-8"))
    h.update(b"\n--- strip_payload ---\n")
    # Strip ``audit_block`` itself before hashing to avoid a chicken-and-egg.
    redacted = {k: v for k, v in strip_payload.items() if k != "audit_block"}
    h.update(
        json.dumps(redacted, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    return h.hexdigest()


def _render_sidecar(
    strip: IronCondorStrip,
    audit_block: str,
    z_cap_audit: str,
    envelope: ReplicationVerdict,
) -> str:
    """Render the human-readable strip strikes sidecar (markdown)."""
    lines: list[str] = []
    lines.append("# IronCondor strip — Stage-2 → Stage-3 hand-off\n")
    lines.append(
        "Auto-generated by ``simulations/saas_builder/cohort_5_strip/emit.py``."
        " Do not hand-edit.\n"
    )
    lines.append("## Strip-level parameters\n")
    lines.append(f"- ``s_0`` (spot, ≈ X̄/Ȳ): **{strip.s_0:.4f}**")
    lines.append(f"- ``sigma_0`` (Carr-Madan anchor): **{strip.sigma_0:.4f}**")
    lines.append(f"- ``k_star`` (CPO strike): **{strip.k_star:.4f}**")
    lines.append(f"- ``k_hat`` (K⋆/2√σ_0): **{strip.k_hat:.6f}**")
    lines.append(
        f"- ``geometry.log_offsets``: {list(strip.geometry.log_offsets)}"
    )
    lines.append(f"- ``geometry.delta_inner``: {strip.geometry.delta_inner}")
    lines.append(f"- ``geometry.delta_outer``: {strip.geometry.delta_outer}")
    lines.append("")
    lines.append("## 12-leg strike ladder\n")
    lines.append(
        "| Condor | Label | K_1 (short put) | K_2 (long put) |"
        " K_3 (long call) | K_4 (short call) | Weight w_j |"
    )
    lines.append(
        "|--------|-------|-----------------|----------------|"
        "------------------|------------------|------------|"
    )
    for i, c in enumerate(strip.condors):
        strikes = [leg.strike for leg in c.legs]
        lines.append(
            f"| {i + 1} | `{c.label}` |"
            f" {strikes[0]:.4f} | {strikes[1]:.4f} |"
            f" {strikes[2]:.4f} | {strikes[3]:.4f} |"
            f" {c.weight:.6f} |"
        )
    lines.append("")
    lines.append("## Carr-Madan replication envelope (Pin S6)\n")
    lines.append(
        f"- ``max_relative_error``: **{envelope.max_relative_error:.4e}**"
    )
    lines.append(f"- ``tolerance``: {envelope.tolerance:.4e}")
    lines.append(f"- ``n_grid_points``: {envelope.n_grid_points}")
    lines.append(f"- **verdict**: {'PASS' if envelope.passes else 'FAIL'}")
    lines.append("")
    lines.append("## Provenance\n")
    lines.append(f"- ``primitives_anchor``: {strip.primitives_anchor}")
    lines.append(f"- ``saas_note_anchor``: {strip.saas_note_anchor}")
    lines.append(f"- ``audit_block`` (strip): `{audit_block}`")
    lines.append(f"- ``audit_block`` (cohort-4 Z_cap): `{z_cap_audit}`")
    lines.append("")
    return "\n".join(lines)


class StripEmitter:
    """Read cohort-4 Z_cap pin, build the 3-condor strip, write the JSON artifact.

    The class is the only mutable-state object in cohort_5_strip; all
    other tiers (types, geometry, replication) are stateless.
    """

    def __init__(
        self,
        emit_dir: str | Path = DEFAULT_EMIT_DIR,
        z_cap_path: str | Path = DEFAULT_Z_CAP_PATH,
        spec_path: str = DEFAULT_SPEC_PATH,
        geometry: StripGeometry | None = None,
        envelope_verifier: CarrMadanEnvelopeVerifier | None = None,
    ) -> None:
        self._emit_dir = Path(emit_dir)
        self._z_cap_path = Path(z_cap_path)
        self._spec_path = spec_path
        self._geometry = geometry if geometry is not None else default_strip_geometry()
        self._envelope = (
            envelope_verifier
            if envelope_verifier is not None
            else CarrMadanEnvelopeVerifier()
        )
        self._builder = StripBuilder(
            primitives_anchor=DEFAULT_PRIMITIVES_ANCHOR,
            saas_note_anchor=DEFAULT_SAAS_NOTE_ANCHOR,
        )
        self._reader = ZCapPinnedReader()

    @property
    def strip_json_path(self) -> Path:
        return self._emit_dir / STRIP_JSON_FILENAME

    @property
    def sidecar_path(self) -> Path:
        return self._emit_dir / STRIP_SIDECAR_FILENAME

    def __call__(self, k_star: float | None = None) -> tuple[IronCondorStrip, ReplicationVerdict, str]:
        """Read inputs, build strip, verify, emit JSON + sidecar.

        Args:
            k_star: Override for the CPO equilibrium strike K⋆. If
                ``None``, defaults to ``Z_cap_pinned.Z_cop_per_month``
                — the per-draw equilibrium-strike identification used
                by cohort_4 (see ``cohort_4/z_cap.py`` docstring on
                ``K⋆ ≡ q_t_cop``). Pass an explicit value to override
                for sensitivity-arm strip variants.

        Returns:
            (strip, replication_verdict, audit_block).

        Raises:
            FileNotFoundError: Z_cap_pinned.json not found.
            StripGeometryError: spot ``S_0`` ≤ 0 or geometry degenerate.
            ReplicationToleranceError: envelope or long-vol signature breach.
            AuditBlockDriftError: post-write round-trip equality breach.
        """
        if not self._z_cap_path.is_file():
            raise FileNotFoundError(
                f"StripEmitter: Z_cap_pinned.json not found at"
                f" {self._z_cap_path}"
            )
        z_cap = self._reader(self._z_cap_path)
        # Spot S_0 ← X̄/Ȳ (canonical TP1 fixture). The Z_cap artifact
        # does not carry X̄/Ȳ as a top-level field; we derive it from
        # the cohort-4 default and surface as a Stage-3 hand-off
        # parameter rather than an inferred quantity.
        s_0 = 4000.0  # canonical X̄/Ȳ per PRIMITIVES.md §3 + spec §3.
        # σ_0 anchor (R1) at canonical fixtures: (X̄/Ȳ)²·ε²/8 = 4000²·0.1²/8
        sigma_0 = (s_0 * s_0) * (0.1 * 0.1) / 8.0
        effective_k_star = (
            k_star if k_star is not None else z_cap.Z_cop_per_month
        )
        if not effective_k_star > 0.0:
            raise StripGeometryError(
                f"StripEmitter: K⋆ = {effective_k_star} must be > 0;"
                " pass an explicit k_star kwarg if Z_cap is non-positive"
            )
        strip = self._builder(
            s_0=s_0,
            sigma_0=sigma_0,
            k_star=effective_k_star,
            geometry=self._geometry,
        )
        assert_long_vol_signature(strip)
        envelope_verdict = self._envelope(strip)
        # Build the JSON payload (without audit_block), compute the digest,
        # then attach the digest to the final payload.
        body = _serialize_strip(strip)
        audit_block = _compute_strip_audit_block(
            z_cap_audit_block=z_cap.audit_block,
            spec_path=self._spec_path,
            strip_payload=body,
        )
        payload: dict[str, Any] = {**body, "audit_block": audit_block}
        # Write JSON + sidecar.
        self._emit_dir.mkdir(parents=True, exist_ok=True)
        self.strip_json_path.write_text(
            json.dumps(payload, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        self.sidecar_path.write_text(
            _render_sidecar(
                strip=strip,
                audit_block=audit_block,
                z_cap_audit=z_cap.audit_block,
                envelope=envelope_verdict,
            ),
            encoding="utf-8",
        )
        # Round-trip read-back equality check.
        roundtrip = json.loads(self.strip_json_path.read_text(encoding="utf-8"))
        if roundtrip != payload:
            raise AuditBlockDriftError(
                "StripEmitter: round-trip JSON equality failed —"
                " filesystem drift between write and re-read"
            )
        return strip, envelope_verdict, audit_block


__all__ = [
    "DEFAULT_EMIT_DIR",
    "DEFAULT_SPEC_PATH",
    "DEFAULT_Z_CAP_PATH",
    "STRIP_JSON_FILENAME",
    "STRIP_SCHEMA_VERSION",
    "STRIP_SIDECAR_FILENAME",
    "StripEmitter",
]
