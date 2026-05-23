"""Posterior + prior parquet emission for SAAS-COHORT-1.

Orchestrates spec §10 emission:

- ``synthetic_tau_t.parquet`` — Hive-partitioned by ``tier_id`` × ``month``;
  τ_t / q_t_usd / q_t_cop populated from ``pm.sample_posterior_predictive``
  per spec §7 (MQ-B4 fix); r / p / α / x_m populated from ``idata.posterior``
  with the (μ, φ) → (r, p) reparameterization applied at emission time
  (NegBin parameterization pin per MQ-B2).
- ``cohort_prior.parquet`` — five percentiles (5/25/50/75/95) for each prior
  parameter; ``source = "spec-v1.1.1-§5.1-§5.2"``; ``fetched_at_utc =
  datetime.now(UTC).isoformat()``; ``schema_version`` from
  :data:`simulations.types.posterior.DEFAULT_SCHEMA_VERSION`.

Diagnostic gate (spec §8(7) + §8(8)) is enforced before any emission via
:class:`simulations.saas_builder.diagnostics.PosteriorDiagnostic`. Failed
verdict raises :class:`simulations.saas_builder._errors.DiagnosticGateError`
— NO partial emission.

Tier-import discipline: writes through
:class:`simulations.utils.parquet_io.SyntheticTauWriter` and
:class:`simulations.utils.parquet_io.CohortPriorWriter` ONLY. No direct
pandas / pyarrow calls. Hive layout (``tier_id=*/month=*/``) is enforced
by the writer per ``SYNTHETIC_TAU_PARTITION_COLS``.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

import arviz as az
import numpy as np
import pymc as pm

from simulations.modules.samplers import TruncParetoSampler
from simulations.saas_builder._errors import DiagnosticGateError
from simulations.saas_builder.diagnostics import (
    DiagnosticVerdict,
    PosteriorDiagnostic,
    compute_ci_width_ratio_per_param,
)
from simulations.saas_builder.priors import (
    CohortPriors,
    negbin_mu_phi_to_r_p,
    tier_id_at_index,
)
from simulations.types.distributions import TruncParetoParams
from simulations.types.posterior import DEFAULT_SCHEMA_VERSION
from simulations.types.tier import TIER_IDS, TierID
from simulations.utils.audit_block import compute_audit_block
from simulations.utils.parquet_io import (
    CohortPriorRow,
    CohortPriorWriter,
    SyntheticTauRow,
    SyntheticTauWriter,
    cohort_prior_row,
    synthetic_tau_row,
)

# ─── Module-level constants ───────────────────────────────────────────────────

#: Spec §10 cohort_prior.parquet percentile grid. Strings (parquet column
#: dtype is "string" per ``COHORT_PRIOR_DTYPES``).
COHORT_PRIOR_PERCENTILES: tuple[str, ...] = ("5", "25", "50", "75", "95")

#: Numeric percentile grid corresponding to ``COHORT_PRIOR_PERCENTILES``.
_COHORT_PRIOR_QUANTILES: tuple[float, ...] = (0.05, 0.25, 0.50, 0.75, 0.95)

#: Spec-source string for cohort_prior.parquet provenance.
_PRIOR_SOURCE_TAG: str = "spec-v1.1.1-§5.1-§5.2"

#: Names of model.py parameters to emit cohort priors for. The TruncPareto
#: ``alpha_pareto`` is renamed to ``alpha`` at emission time so its column
#: name matches the synthetic_tau_t schema (see _PARAM_NAME_RENAME_MAP).
_PRIOR_PARAM_EMISSION_NAMES: tuple[str, ...] = (
    "mu",
    "phi",
    "alpha_pareto",
    "x_m",
)

#: Cohort-prior `param` column rename map: PyMC RV name → emission name
#: (per Phase-5 Code-Reviewer N-2). COHORT-2 readers filter by `alpha`,
#: not `alpha_pareto`, so we emit the spec §10 / synthetic_tau_t-aligned
#: column label.
_PARAM_NAME_RENAME_MAP: Mapping[str, str] = {
    "alpha_pareto": "alpha",
}


# ─── Emission summary TypedDict ───────────────────────────────────────────────


class EmissionSummary(TypedDict):
    """Return shape of :meth:`CohortEmitter.__call__`.

    Pinned at the IO Boundary (consumed by callers as a documentation
    surface for what an emission produced). NOT a Pydantic model — this
    structure does not cross a system boundary requiring validation.
    """

    verdict: "DiagnosticVerdict"
    synthetic_tau_path: Path
    cohort_prior_path: Path
    audit_path: Path
    audit_block: str
    n_rows_synthetic: int


# ─── Posterior-predictive driver ──────────────────────────────────────────────


#: Posterior-predictive variable names sampled by PyMC. The compound-sum
#: τ_t is **NOT** in this list — it is built post-hoc from per-turn
#: TruncPareto draws (BLOCK-1 fix; spec §5.1 verbatim). Likewise
#: ``tier_idx`` is NOT a PyMC RV in v0.4 (CORRECTIONS-α v0.3 → v0.4
#: marginalization); it is drawn numpy-side from posterior ``pi`` at PP
#: time and injected into the ``posterior_predictive`` group.
_PP_PYMC_VAR_NAMES: tuple[str, ...] = ()

#: Default active-days-per-month when emit-side reconstructs n_month
#: post-hoc from posterior (μ, φ). Mirrors
#: :data:`simulations.saas_builder.priors.ACTIVE_DAYS_PER_MONTH` (= 22).
_DEFAULT_ACTIVE_DAYS_PER_MONTH: int = 22

#: Default cohort size for the post-hoc per-builder tier draw at PP time.
#: Mirrors :data:`simulations.saas_builder.model.DEFAULT_N_BUILDERS` (1000).
_DEFAULT_N_BUILDERS_PP: int = 1000

def _atomic_write_text(path: Path, text: str) -> None:
    """Atomic write of ``text`` to ``path`` via temp + ``os.replace``.

    Used for the ``_AUDIT.json`` sidecar (CR-IMPORTANT I8 v0.3 sweep).
    Writing to a sibling temp file in the same directory and replacing
    keeps the artifact either at its prior content or at the new
    content; never half-written. ``os.replace`` is atomic on POSIX
    when source and dest are on the same filesystem.
    """
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_str = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(parent)
    )
    tmp_path = Path(tmp_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_path, path)
    except OSError:
        # Best-effort cleanup of orphaned temp file on failure.
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


#: Default emission directory — resolved as an absolute path relative to
#: this package, so callers running from a different cwd still write to
#: ``simulations/saas_builder/data/`` (CR-IMPORTANT v0.3 sweep, item I3:
#: relative-path default ``Path("simulations/saas_builder/data")`` was
#: cwd-dependent and silently emitted into the caller's cwd subtree).
_DEFAULT_BASE_DIR_ABS: Path = Path(__file__).resolve().parent / "data"


def run_posterior_predictive(
    model: pm.Model,
    posterior_idata: az.InferenceData,
    *,
    x_max_fixed: float,
    blended_price_per_mtok: float,
    fx_cop_per_usd: float,
    var_names: tuple[str, ...] = _PP_PYMC_VAR_NAMES,
    random_seed: int | None = 42,
    n_builders: int = _DEFAULT_N_BUILDERS_PP,
    active_days_per_month: int = _DEFAULT_ACTIVE_DAYS_PER_MONTH,
) -> az.InferenceData:
    """Run posterior-predictive + spec §5.1 compound-sum τ_t reduction.

    BLOCK-1 fix (plan v0.3 CORRECTIONS-α): the spec §5.1 (T1) compound
    sum

        τ_t = Σ_{j=1}^{D_t} Σ_{i=1}^{N_j} τ_{j,i},   τ_{j,i} ~ TruncPareto(α, x_m, κ)

    is realized in two stages because PyMC cannot represent a doubly-
    stochastic compound sum as a fixed-shape Deterministic without a
    custom distribution. We therefore:

    1. Call ``pm.sample_posterior_predictive`` to populate ``n_per_day``,
       ``n_month``, ``tier_idx`` (PyMC-graph variables).
    2. For each posterior draw of ``(α, x_m, n_month)``, draw ``n_month``
       iid TruncPareto variates via the shipped
       :class:`simulations.modules.samplers.TruncParetoSampler` and reduce
       to ``τ_t = Σ τ_{j,i}``. This produces nonzero within-row per-turn
       variance at fixed parameters (BLOCK-3 verification target).
    3. Compute ``q_t_usd = τ_t · price / 1e6`` and
       ``q_t_cop = q_t_usd · FX``.
    4. Inject ``tau_t``, ``q_t_usd``, ``q_t_cop`` back into the
       ``posterior_predictive`` group as numpy arrays of shape
       ``(chain, draw, n_builders)``.

    Args:
        model: the ``pm.Model`` from
            :func:`simulations.saas_builder.model.T1ModelFactory.__call__`.
        posterior_idata: posterior :class:`arviz.InferenceData` from
            ``pm.sample(...)``.
        x_max_fixed: TruncPareto upper truncation κ pin from
            ``priors.x_m.x_max_fixed`` (spec §5.1 (T1)).
        blended_price_per_mtok: spec §5.1 closed-form Sonnet blended
            price (≈ 7.1495 $/MTok per M3 assertion).
        fx_cop_per_usd: COP/USD stationary FX rate.
        var_names: PyMC-graph names to sample. Default
            :data:`_PP_PYMC_VAR_NAMES`. Compound-sum ``tau_t`` is added
            post-hoc.
        random_seed: optional RNG seed for reproducibility.

    Returns:
        An :class:`arviz.InferenceData` with ``posterior_predictive``
        populated by ``var_names`` PLUS the post-hoc compound-sum
        ``tau_t``, ``q_t_usd``, ``q_t_cop`` arrays of shape
        ``(chain, draw)``. Within-row per-turn variance is nonzero at
        fixed posterior parameter draws because each (chain, draw) cell
        re-samples ``n_month`` independent TruncPareto variates.

    Contract:
        Preconditions:
            - ``x_max_fixed > 0``, ``blended_price_per_mtok > 0``,
              ``fx_cop_per_usd > 0`` (callers should pass the priors
              and model's pinned values).
            - ``posterior_idata.posterior`` must contain ``alpha_pareto``
              and ``x_m`` for the per-turn TruncPareto draws.
        Raises:
            KeyError: if posterior is missing ``alpha_pareto``/``x_m``.
            ValueError: if any draw yields ``alpha < 1.5`` (M1 floor; the
                shipped ``TruncParetoSampler.__post_init__`` raises).
    """
    # CORRECTIONS-α v0.4 tertiary marginalization: ``n_month`` and
    # ``tier_idx`` are no longer PyMC RVs. If ``var_names`` is empty
    # (the v0.4 default), skip ``pm.sample_posterior_predictive``
    # entirely and synthesize the posterior_predictive group from
    # numpy-side post-hoc draws.
    post_group = posterior_idata["posterior"]
    if var_names:
        with model:
            pp = pm.sample_posterior_predictive(
                posterior_idata,
                var_names=list(var_names),
                random_seed=random_seed,
                progressbar=False,
            )
        pp_group = pp["posterior_predictive"]
    else:
        # Empty posterior_predictive Dataset; populated below. Use a
        # placeholder dummy variable to ensure the group is created;
        # we drop it before returning.
        n_chains_seed = int(post_group["mu"].shape[0])
        n_draws_seed = int(post_group["mu"].shape[1])
        dummy = np.zeros((n_chains_seed, n_draws_seed), dtype=np.float64)
        pp = az.from_dict(posterior_predictive={"_pp_init": dummy})
        pp_group = pp["posterior_predictive"]

    # Shapes: posterior arrays are (chain, draw, ...); n_month is
    # Deterministic so it is in posterior (NOT posterior_predictive)
    # when produced via pm.sample_posterior_predictive on Deterministics
    # downstream of NegBin RVs — but PyMC versions vary, so check both.
    # CORRECTIONS-α v0.4 tertiary marginalization: n_month is no longer
    # a PyMC RV. Reconstruct post-hoc by drawing
    # ``n_month ~ NegBin(D_t·μ, D_t·φ)`` from the posterior (μ, φ) per
    # (chain, draw) cell. Sum-of-iid NegBin closed form: each per-day
    # NegBin(μ, φ) summed over D_t days is NegBin(D_t·μ, D_t·φ) in the
    # mean–dispersion form.
    # Backwards-compatible fallbacks: if a caller hand-crafts a v0.3
    # idata with n_month or n_per_day pre-populated, prefer those.
    rng_seed = 42 if random_seed is None else int(random_seed)
    rng = np.random.default_rng(rng_seed)

    if "n_month" in pp_group:
        n_month_arr = np.asarray(pp_group["n_month"].values)
    elif "n_month" in post_group:
        n_month_arr = np.asarray(post_group["n_month"].values)
    elif "n_per_day" in pp_group:
        n_per_day_arr = np.asarray(pp_group["n_per_day"].values)
        n_month_arr = n_per_day_arr.sum(axis=-1)
    else:
        # v0.4 default path: synthesize n_month from posterior (μ, φ).
        if "mu" not in post_group or "phi" not in post_group:
            raise KeyError(
                "run_posterior_predictive: posterior is missing 'mu' or"
                " 'phi'; cannot perform the v0.4 post-hoc n_month draw."
            )
        mu_arr = np.asarray(post_group["mu"].values)
        phi_arr = np.asarray(post_group["phi"].values)
        d_t = float(active_days_per_month)
        # NegBin(mu_total=D_t·μ, alpha=D_t·φ) — convert to numpy's
        # (n=alpha, p=alpha/(alpha+mu)) parameterization.
        mu_total = mu_arr * d_t
        alpha_total = phi_arr * d_t
        p_arr = alpha_total / (alpha_total + mu_total)
        n_month_arr = rng.negative_binomial(n=alpha_total, p=p_arr)

    alpha_arr = np.asarray(post_group["alpha_pareto"].values)
    x_m_arr = np.asarray(post_group["x_m"].values)

    # CR-NIT-new-1 (v0.3 → v0.4 sweep): the prior dead ``if
    # n_month_arr.ndim == 3: pass`` branch was a vestige of an aborted
    # broadcast variant and is removed; the per-cell ``int(np.asarray(
    # nm_raw).sum())`` reduction below already handles 1-D / 2-D / 3-D
    # ``n_month_arr`` shapes uniformly.
    n_chains_arr = alpha_arr.shape[0]
    n_draws_arr = alpha_arr.shape[1]

    tau_t_arr = np.empty((n_chains_arr, n_draws_arr), dtype=np.float64)
    for c in range(n_chains_arr):
        for d in range(n_draws_arr):
            alpha_cd = float(alpha_arr[c, d])
            x_m_cd = float(x_m_arr[c, d])
            # Pull scalar n_month for this draw (sum across active days).
            nm_raw = n_month_arr[c, d] if n_month_arr.ndim >= 2 else n_month_arr[c]
            n_total = int(np.asarray(nm_raw).sum())
            if n_total <= 0:
                tau_t_arr[c, d] = 0.0
                continue
            params = TruncParetoParams(
                alpha=alpha_cd,
                x_m=x_m_cd,
                x_max=float(x_max_fixed),
            )
            sampler = TruncParetoSampler(params=params)
            draws = sampler(size=n_total, rng=rng)
            tau_t_arr[c, d] = float(draws.sum())

    q_t_usd_arr = tau_t_arr * float(blended_price_per_mtok) / 1.0e6
    q_t_cop_arr = q_t_usd_arr * float(fx_cop_per_usd)

    # CORRECTIONS-α v0.4: post-hoc per-builder tier draw from posterior π.
    # ``pi`` is in posterior group with shape (chain, draw, 3). For each
    # (chain, draw) cell, draw ``n_builders`` iid tier indices from
    # Categorical(pi[c, d, :]) using the shipped numpy Generator. This
    # recovers the per-builder ``tier_idx`` that was marginalized out of
    # the inference graph (an exact identity since the COHORT-1 likelihood
    # does not condition on tier_idx).
    if "pi" not in post_group:
        raise KeyError(
            "run_posterior_predictive: posterior is missing 'pi'; cannot"
            " perform the v0.4 post-hoc tier_idx draw."
        )
    pi_arr = np.asarray(post_group["pi"].values)  # (chain, draw, 3)
    if pi_arr.ndim != 3 or pi_arr.shape[2] != 3:
        raise ValueError(
            f"run_posterior_predictive: pi posterior shape {pi_arr.shape}"
            f" must be (chain, draw, 3) for the per-builder tier draw."
        )
    if n_builders <= 0:
        raise ValueError(
            f"run_posterior_predictive: n_builders = {n_builders} must be > 0"
        )
    tier_idx_arr = np.empty(
        (n_chains_arr, n_draws_arr, n_builders), dtype=np.int64,
    )
    for c in range(n_chains_arr):
        for d in range(n_draws_arr):
            pi_cd = pi_arr[c, d, :]
            # Defensive renormalization: posterior draws sum to 1 within
            # numerical tolerance, but rng.choice requires exact-sum.
            pi_norm = pi_cd / pi_cd.sum()
            tier_idx_arr[c, d, :] = rng.choice(
                3, size=n_builders, p=pi_norm,
            )

    # Inject the compound-sum arrays back into the pp dataset.
    pp_group["tau_t"] = (("chain", "draw"), tau_t_arr)
    pp_group["q_t_usd"] = (("chain", "draw"), q_t_usd_arr)
    pp_group["q_t_cop"] = (("chain", "draw"), q_t_cop_arr)
    pp_group["tier_idx"] = (
        ("chain", "draw", "builder"),
        tier_idx_arr,
    )
    # Drop placeholder dummy variable used to bootstrap an empty pp group.
    if "_pp_init" in pp_group:
        del pp_group["_pp_init"]

    return pp


# ─── Emission orchestrator ────────────────────────────────────────────────────


@dataclass(frozen=True)
class CohortEmitter:
    """Spec §10 emission Callable.

    Attributes:
        base_dir: filesystem root for emission. ``synthetic_tau_t/`` and
            ``cohort_prior.parquet`` are written under this root. Defaults
            to ``simulations/saas_builder/data/``.
        diagnostic: the §8(7) + §8(8) gate Callable. Default uses
            :data:`~simulations.saas_builder.diagnostics.DEFAULT_MONITORED_PARAMS`.

    Behavior contract:

    - ``__call__(priors, model, posterior_idata, prior_idata)`` first
      runs ``diagnostic`` on the (posterior, prior) pair; raises
      :class:`DiagnosticGateError` on ``passed=False``.
    - Then runs ``pm.sample_posterior_predictive`` for τ_t / q_t_usd /
      q_t_cop (MQ-B4).
    - Then emits both parquet artifacts via the shipped writers.
    - Returns an emission summary dict with verdict + paths.
    - Idempotent: re-running over the same ``(tier_id, month)`` partition
      overwrites cleanly (writer-controlled).
    - Audit-block sha (from :mod:`simulations.utils.audit_block`) is
      recorded for every emission and written into a sidecar
      ``_AUDIT.json`` under ``base_dir``.
    """

    base_dir: Path = field(
        default_factory=lambda: _DEFAULT_BASE_DIR_ABS,
    )
    diagnostic: PosteriorDiagnostic = field(default_factory=PosteriorDiagnostic)
    fx_cop_per_usd: float = 4000.0
    n_builders: int = _DEFAULT_N_BUILDERS_PP

    def __post_init__(self) -> None:
        # Coerce base_dir to Path defensively (callers may pass str).
        if not isinstance(self.base_dir, Path):
            object.__setattr__(self, "base_dir", Path(self.base_dir))

    def __call__(
        self,
        *,
        priors: CohortPriors,
        model: pm.Model,
        posterior_idata: az.InferenceData,
        prior_idata: az.InferenceData,
        month: int,
        tier_assignments: np.ndarray | None = None,
        random_seed: int | None = 42,
    ) -> EmissionSummary:
        """Run the gate, posterior-predictive, and parquet emission.

        Args:
            priors: prior pin bundle (used for cohort_prior.parquet rows).
            model: the ``pm.Model`` from ``T1ModelFactory().__call__()``.
            posterior_idata: ``arviz.InferenceData`` from ``pm.sample(...)``.
            prior_idata: ``arviz.InferenceData`` from
                ``pm.sample_prior_predictive(...)`` (required by §8(7) gate).
            month: integer month identifier (e.g. ``1``..``12``); becomes
                Hive partition key ``month=N``.
            tier_assignments: optional 1-D array of per-row ``TIER_IDS``
                indices (0/1/2). If ``None``, the emitter pulls ``tier_idx``
                samples from the posterior (this is the production path).
            random_seed: optional seed for the posterior-predictive draw.

        Returns:
            :class:`EmissionSummary` TypedDict with verdict, paths,
            audit-block hex, and row count.

        Contract:
            Preconditions:
                - ``month > 0`` (explicit guard, line ~218; raises
                  ``ValueError``).
                - ``posterior_idata`` must satisfy the
                  :meth:`PosteriorDiagnostic.__call__` preconditions
                  (posterior + sample_stats groups).
                - ``prior_idata`` must satisfy the §8(7) CI-width gate
                  preconditions (non-None; prior group present).
                - ``model`` must be a ``pm.Model`` whose unobserved RVs
                  match the names in ``posterior_idata.posterior`` so
                  ``pm.sample_posterior_predictive`` can resolve them.
                  A mismatch surfaces as a ``KeyError`` from PyMC at
                  the ``run_posterior_predictive`` step (implicit).
                - The shipped writer ``SyntheticTauWriter`` requires a
                  non-empty row list; if posterior + pp idata flatten
                  to zero rows (impossible for valid sample-output
                  shapes), it raises ``ValueError`` (implicit
                  fallthrough).
                - ``self.base_dir`` must be writable; otherwise
                  ``OSError`` propagates from
                  ``parent.mkdir(parents=True, exist_ok=True)`` and
                  ``DataFrame.to_parquet(...)``.

            Raises:
                DiagnosticGateError: explicit, line ~228. Fires iff the
                    spec §8(7) + §8(8) gate yields ``passed=False`` —
                    NO partial emission, NO sidecar audit-block. Caller
                    HALTs.
                ValueError: explicit, line ~218 (month ≤ 0); also
                    propagated from writers on dtype-cast failure.
                SchemaMismatchError: from
                    ``simulations.utils.parquet_io._check_columns``
                    if the row TypedDicts somehow diverge from
                    ``SYNTHETIC_TAU_COLUMNS`` / ``COHORT_PRIOR_COLUMNS``
                    (defensive — the row factories
                    ``synthetic_tau_row`` / ``cohort_prior_row``
                    construct the exact column set).
                OSError: filesystem write failure (mkdir / parquet
                    write / sidecar JSON write).
                pymc.SamplingError / pytensor.* errors: from
                    ``pm.sample_posterior_predictive`` if the model
                    surface is malformed (caller responsibility).

            Silences: none. NO partial emission means: if any step
                after the gate raises, the ``_AUDIT.json`` sidecar is
                NOT written, signaling caller that the parquet may be
                partial. Re-emission to the same partition path is
                idempotent (writer-controlled).
        """
        if month <= 0:
            raise ValueError(f"CohortEmitter: month = {month} must be > 0")

        # 1) Spec §8(7) + §8(8) gate.
        verdict = self.diagnostic(posterior_idata, prior_idata)
        if not verdict.passed:
            raise DiagnosticGateError(
                f"SAAS-COHORT-1 emission HALTED on diagnostic gate failure:"
                f" {verdict!r}"
            )

        # 2) Posterior-predictive draws for τ_t / q_t_usd / q_t_cop (MQ-B4
        # + BLOCK-1 fix: τ_t is the spec §5.1 compound sum, built post-hoc
        # from per-turn TruncPareto draws by run_posterior_predictive).
        # Resolve the M3 blended price and x_max_fixed from priors at the
        # call site (no global module state).
        from simulations.saas_builder.model import _build_sonnet_blended_price
        blended_price = _build_sonnet_blended_price()
        pp_idata = run_posterior_predictive(
            model,
            posterior_idata,
            x_max_fixed=priors.x_m.x_max_fixed,
            blended_price_per_mtok=blended_price,
            fx_cop_per_usd=self.fx_cop_per_usd,
            random_seed=random_seed,
            n_builders=self.n_builders,
        )

        # 3) Build synthetic_tau_t rows.
        rows = self._build_synthetic_tau_rows(
            posterior_idata=posterior_idata,
            pp_idata=pp_idata,
            month=month,
            tier_assignments=tier_assignments,
        )
        writer_tau = SyntheticTauWriter(base_dir=self.base_dir)
        synthetic_tau_path = writer_tau(rows)

        # 4) Build cohort_prior.parquet rows from the prior_idata percentiles.
        prior_rows = self._build_cohort_prior_rows(
            priors=priors,
            prior_idata=prior_idata,
        )
        writer_prior = CohortPriorWriter(base_dir=self.base_dir)
        cohort_prior_path = writer_prior(prior_rows)

        # 5) Audit block sidecar. Hash the cohort_prior parquet file plus
        # every parquet leaf under the synthetic_tau Hive tree (the
        # synthetic_tau_path is a directory; compute_audit_block requires
        # regular files only).
        synthetic_tau_files = sorted(synthetic_tau_path.rglob("*.parquet"))
        audit_block = compute_audit_block(
            [cohort_prior_path, *synthetic_tau_files]
        )
        audit_path = self.base_dir / "_AUDIT.json"
        # CR-IMPORTANT (v0.3 sweep): per-parameter ci_width_ratio map
        # (RC-FLAG-A). The aggregate ``ci_width_ratio_max`` was opaque
        # to which monitored parameter triggered the §8(7) gate; this
        # widens the audit surface to cover every monitored param.
        ci_width_ratio_per_param = compute_ci_width_ratio_per_param(
            posterior_idata, prior_idata, self.diagnostic.monitored_params
        )
        audit_payload: dict[str, object] = {
            "audit_block": audit_block,
            "schema_version": DEFAULT_SCHEMA_VERSION,
            "synthetic_tau_path": str(synthetic_tau_path),
            "cohort_prior_path": str(cohort_prior_path),
            "month": month,
            "n_rows_synthetic": len(rows),
            "verdict": {
                "rhat_max": verdict.rhat_max,
                "ess_bulk_min": verdict.ess_bulk_min,
                "ess_tail_min": verdict.ess_tail_min,
                "divergence_frac": verdict.divergence_frac,
                "ci_width_ratio_max": verdict.ci_width_ratio_max,
                "ci_width_ratio_per_param": dict(ci_width_ratio_per_param),
                "n_chains": verdict.n_chains,
                "n_draws_per_chain": verdict.n_draws_per_chain,
            },
        }
        # CR-IMPORTANT I8 (v0.3 sweep): atomic ``_AUDIT.json`` write.
        # Prior naive ``audit_path.write_text(...)`` left a half-written
        # JSON on disk if the process was killed mid-write. Use a temp
        # file in the same directory + ``os.replace`` for atomic publish.
        _atomic_write_text(audit_path, json.dumps(audit_payload, indent=2))

        return EmissionSummary(
            verdict=verdict,
            synthetic_tau_path=synthetic_tau_path,
            cohort_prior_path=cohort_prior_path,
            audit_path=audit_path,
            audit_block=audit_block,
            n_rows_synthetic=len(rows),
        )

    # ─── Private builders ────────────────────────────────────────────────

    def _build_synthetic_tau_rows(
        self,
        *,
        posterior_idata: az.InferenceData,
        pp_idata: az.InferenceData,
        month: int,
        tier_assignments: np.ndarray | None,
    ) -> list[SyntheticTauRow]:
        """Construct the ``SyntheticTauRow`` list for one month emission.

        Pulls posterior parameter draws (mu, phi, alpha_pareto, x_m) and
        posterior-predictive emission draws (tau_t, q_t_usd, q_t_cop) and
        zips them into one row per (chain × draw). NegBin (μ, φ) → (r, p)
        reparameterization applied at the boundary per MQ-B2.

        Tier assignment: if ``tier_assignments`` is None, samples are
        drawn from the posterior ``tier_idx`` group (production path).
        Each row's ``tier_id`` is the corresponding ``TIER_IDS[idx]``.
        """
        post = posterior_idata["posterior"]
        pp = pp_idata["posterior_predictive"]
        # Flatten (chain, draw) → row using xarray ``.stack`` so the
        # (chain, draw) → row mapping is explicit and dimension-named,
        # not raw ``.ravel()`` (CR-IMPORTANT I1 v0.3 sweep). The stacked
        # 1-D values still equal the C-order ravel because xarray ``.stack``
        # uses np.stack-equivalent ordering, but the dimension is
        # documented now.
        mu_arr = np.asarray(post["mu"].stack(row=("chain", "draw")).values)
        phi_arr = np.asarray(post["phi"].stack(row=("chain", "draw")).values)
        alpha_arr = np.asarray(
            post["alpha_pareto"].stack(row=("chain", "draw")).values
        )
        x_m_arr = np.asarray(post["x_m"].stack(row=("chain", "draw")).values)
        n_rows = mu_arr.shape[0]

        tau_arr = np.asarray(pp["tau_t"].stack(row=("chain", "draw")).values)
        qusd_arr = np.asarray(pp["q_t_usd"].stack(row=("chain", "draw")).values)
        qcop_arr = np.asarray(pp["q_t_cop"].stack(row=("chain", "draw")).values)

        # CR-IMPORTANT I2 (v0.3 sweep): assert exact-shape match instead
        # of the prior silent ``[:n_rows]`` truncation. Mismatch indicates
        # a pp/posterior shape divergence that must surface, not be masked.
        if tau_arr.size != n_rows:
            raise ValueError(
                f"_build_synthetic_tau_rows: posterior_predictive tau_t"
                f" has {tau_arr.size} elements but posterior has"
                f" {n_rows}; refusing to truncate (CR-IMPORTANT I2)."
            )
        if qusd_arr.size != n_rows or qcop_arr.size != n_rows:
            raise ValueError(
                f"_build_synthetic_tau_rows: posterior_predictive shape"
                f" mismatch (tau_t={tau_arr.size}, q_t_usd={qusd_arr.size},"
                f" q_t_cop={qcop_arr.size}, expected {n_rows})."
            )

        if tier_assignments is None:
            # CORRECTIONS-α v0.4: tier_idx now lives in the posterior_-
            # predictive group (post-hoc draw from posterior π in
            # ``run_posterior_predictive``). Backwards-compatible
            # fallback: if a caller hand-crafts an idata with tier_idx
            # in the posterior group (test fixtures pre-v0.4), prefer
            # that source.
            if "tier_idx" in pp:
                tier_raw = np.asarray(pp["tier_idx"].values)
            elif "tier_idx" in post:
                tier_raw = np.asarray(post["tier_idx"].values)
            else:
                raise KeyError(
                    "_build_synthetic_tau_rows: tier_idx absent from both"
                    " posterior_predictive and posterior groups."
                )
            if tier_raw.ndim == 3:
                # (chain, draw, n_builders) — flatten across (chain, draw)
                # and pick builder slot 0 for each row. Synthetic_tau_t is
                # keyed per (chain, draw) following the v0.2 layout.
                # RC-FLAG (v0.3 sweep): builder slot-0 collapse is intentional
                # — the v0.2 row-count layout is one row per (chain, draw),
                # so per-builder draws collapse to a representative slot.
                # An explicit shape assertion guards against silent reshape.
                n_chain, n_draw, _n_b = tier_raw.shape
                if n_chain * n_draw != n_rows:
                    raise ValueError(
                        f"_build_synthetic_tau_rows: tier_idx (chain, draw)"
                        f" shape ({n_chain}, {n_draw}) does not match"
                        f" posterior n_rows={n_rows}."
                    )
                tier_idx_arr = tier_raw[:, :, 0].reshape(n_chain * n_draw)
            else:
                tier_flat = tier_raw.ravel()
                if tier_flat.size != n_rows:
                    raise ValueError(
                        f"_build_synthetic_tau_rows: tier_idx ravel size"
                        f" {tier_flat.size} != posterior n_rows {n_rows}."
                    )
                tier_idx_arr = tier_flat
        else:
            tier_idx_arr = np.asarray(tier_assignments, dtype=np.int64)
            if tier_idx_arr.shape[0] != n_rows:
                raise ValueError(
                    f"tier_assignments length {tier_idx_arr.shape[0]}"
                    f" must match flattened posterior rows {n_rows}"
                )

        rows: list[SyntheticTauRow] = []
        for sim_id in range(n_rows):
            mu_v = float(mu_arr[sim_id])
            phi_v = float(phi_arr[sim_id])
            r_v, p_v = negbin_mu_phi_to_r_p(mu_v, phi_v)
            idx = int(tier_idx_arr[sim_id]) % len(TIER_IDS)
            tier_id: TierID = tier_id_at_index(idx)
            rows.append(
                synthetic_tau_row(
                    month=int(month),
                    simulation_id=int(sim_id),
                    tier_id=tier_id,
                    r=r_v,
                    p=p_v,
                    alpha=float(alpha_arr[sim_id]),
                    x_m=float(x_m_arr[sim_id]),
                    tau_t=float(tau_arr[sim_id]),
                    q_t_usd=float(qusd_arr[sim_id]),
                    q_t_cop=float(qcop_arr[sim_id]),
                )
            )
        return rows

    def _build_cohort_prior_rows(
        self,
        *,
        priors: CohortPriors,
        prior_idata: az.InferenceData,
    ) -> list[CohortPriorRow]:
        """Construct ``CohortPriorRow`` list — five percentiles per param."""
        prior = prior_idata["prior"]
        fetched_at = datetime.now(timezone.utc).isoformat()
        rows: list[CohortPriorRow] = []
        for param in _PRIOR_PARAM_EMISSION_NAMES:
            if param not in prior:
                # Defensive: skip params absent from the prior idata
                # (e.g. emission name mismatch); never silently emit
                # zero values.
                continue
            samples = np.asarray(prior[param].values).ravel()
            finite = samples[np.isfinite(samples)]
            if finite.size == 0:
                continue
            emission_name = _PARAM_NAME_RENAME_MAP.get(param, param)
            for pct_str, q in zip(
                COHORT_PRIOR_PERCENTILES, _COHORT_PRIOR_QUANTILES
            ):
                value = float(np.quantile(finite, q))
                rows.append(
                    cohort_prior_row(
                        param=emission_name,
                        percentile=pct_str,
                        value=value,
                        source=_PRIOR_SOURCE_TAG,
                        fetched_at_utc=fetched_at,
                    )
                )
        # Also emit the Dirichlet α-vector concentration as a documentary row.
        for i, a in enumerate(priors.tier.alpha_vector):
            rows.append(
                cohort_prior_row(
                    param=f"dirichlet_alpha[{i}]",
                    percentile="50",
                    value=float(a),
                    source=_PRIOR_SOURCE_TAG,
                    fetched_at_utc=fetched_at,
                )
            )
        # RC-FLAG (v0.3 sweep): if the prior idata carries a 3-component
        # ``pi`` Dirichlet draw, emit per-component percentiles instead
        # of a flat ravel that would conflate the three categories. The
        # categorical axis (axis=2 in (chain, draw, 3) layout) is held
        # fixed while (chain, draw) collapse to the percentile sample.
        if "pi" in prior:
            pi_samples = np.asarray(prior["pi"].values)
            if pi_samples.ndim == 3 and pi_samples.shape[2] == len(TIER_IDS):
                for k in range(pi_samples.shape[2]):
                    component = pi_samples[:, :, k].ravel()
                    finite_k = component[np.isfinite(component)]
                    if finite_k.size == 0:
                        continue
                    for pct_str, q in zip(
                        COHORT_PRIOR_PERCENTILES, _COHORT_PRIOR_QUANTILES
                    ):
                        rows.append(
                            cohort_prior_row(
                                param=f"pi[{k}]",
                                percentile=pct_str,
                                value=float(np.quantile(finite_k, q)),
                                source=_PRIOR_SOURCE_TAG,
                                fetched_at_utc=fetched_at,
                            )
                        )
        # And the active-days-per-month constant (M1 anchor).
        rows.append(
            cohort_prior_row(
                param="active_days_per_month",
                percentile="50",
                value=float(priors.active_days_per_month),
                source=_PRIOR_SOURCE_TAG,
                fetched_at_utc=fetched_at,
            )
        )
        return rows


__all__ = [
    "COHORT_PRIOR_PERCENTILES",
    "CohortEmitter",
    "EmissionSummary",
    "run_posterior_predictive",
]
