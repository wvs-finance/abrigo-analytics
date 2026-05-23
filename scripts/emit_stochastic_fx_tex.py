"""Emit per-family LaTeX fragments for stochastic-fx moment closed forms.

Parent plan: ``docs/plans/2026-05-11-stochastic-fx-variant.md`` §7 Task 2.1.
Parent spec: ``docs/specs/2026-05-11-stochastic-fx-variant-design.md`` v0.3 §4.2.

This script is the IO-Boundary entrypoint for Task 2.1 ``.tex`` fragment
emission. It is intentionally kept SEPARATE from
``simulations/stochastic_fx/moments.py`` to preserve Callable-tier
discipline on that module: ``moments.py`` is pure scalar math with no
imports from ``sympy`` and no filesystem access; this script is the only
place where the emission side-effect lives.

Outputs (under ``notes/stochastic_fx_tex/``):

- ``eps_inversion.tex``        — eq. (8) family-agnostic algebraic
  inversion ``ε(σ_T) = √(8 σ_T / x̄²)``.
- ``sigma_t_moments_gbm.tex``  — GBM closed forms (Hull §15).
- ``sigma_t_moments_ou.tex``   — OU stationary closed forms.
- ``sigma_t_moments_merton.tex`` — Merton jump-diffusion closed forms
  (Andersen-Piterbarg Vol I §2.7 and §2.7.3).

Each per-family fragment retains the symbolic ``(X̄/Ȳ)²`` envelope-scale
notation (FLAG-MQ-2 disposition) and appends a
``\\paragraph{Numerical pin at canonical fixture}`` block reporting the
Python-form numerical evaluation at the spec v0.3 §4.2 canonical pin to
six significant figures.

Determinism / idempotence
-------------------------
The script emits byte-identical content on repeated runs: no timestamps,
no machine-specific metadata, no hash-of-runtime-state. This is required
by the Task 2.1 acceptance test ``test_tex_emission_is_idempotent``.

Run with:

    .venv/bin/python -m scripts.emit_stochastic_fx_tex

or directly via:

    .venv/bin/python scripts/emit_stochastic_fx_tex.py
"""

from __future__ import annotations

from pathlib import Path

import sympy as sp

from simulations.stochastic_fx.moments import (
    gbm_sigma_t_moments,
    merton_sigma_t_moments,
    ou_sigma_t_moments,
)
from simulations.stochastic_fx.types import (
    CANONICAL_GBM,
    CANONICAL_MERTON,
    CANONICAL_OU,
)


def _output_dir() -> Path:
    """Resolve the on-disk output directory ``notes/stochastic_fx_tex/``.

    Uses the script's own location to climb to the repo root rather than
    relying on the current working directory; lets the script be invoked
    either as a module (``python -m scripts.emit_stochastic_fx_tex``) or
    by path.
    """
    return Path(__file__).resolve().parents[1] / "notes" / "stochastic_fx_tex"


def _build_eps_inversion_tex() -> str:
    """Family-agnostic ε ↔ σ_T inversion fragment (PRIMITIVES.md §6 eq. 8).

    Single-line algebraic identity ``ε(σ_T) = √(8 σ_T / x̄²)``. No
    canonical-pin paragraph here — the fragment is family-agnostic and
    has no SDE-parameter dependence.
    """
    sigma_T = sp.Symbol(r"\sigma_T", positive=True)
    xbar = sp.Symbol(r"\bar{x}", positive=True)
    expr = sp.sqrt(8 * sigma_T / xbar**2)
    return (
        "% Family-agnostic eps <-> sigma_T inversion.\n"
        "% ref: notes/PRIMITIVES.md section 6 eq. (8) — this repo.\n"
        "\\[ \\varepsilon(\\sigma_T) = " + sp.latex(expr) + " \\]\n"
    )


def _build_gbm_tex() -> str:
    """GBM closed-form moments fragment (Hull §15 anchor, NEW-BLOCK-MQ-4 fix)."""
    sigma = sp.Symbol("sigma", positive=True)
    T = sp.Symbol("T", positive=True)
    xbar = sp.Symbol(r"\bar{X}", positive=True)
    ybar = sp.Symbol(r"\bar{Y}", positive=True)
    env = (xbar / ybar) ** 2
    e_expr = env * ((sp.exp(sigma**2 * T) - 1) / (sigma**2 * T) - 1)
    v_expr = (
        2 * env**2 * (sp.exp(sigma**2 * T) - 1) ** 2 / (sigma**4 * T**2)
    )
    e_num, v_num = gbm_sigma_t_moments(CANONICAL_GBM)
    return (
        "% GBM envelope moments under mean-zero log-drift.\n"
        "% ref: Hull, Options Futures and Other Derivatives, section 15.\n"
        "% Corrected per NEW-BLOCK-MQ-4: trailing -1 inside the bracket\n"
        "% required for the sigma -> 0 vanishing limit.\n"
        "\\paragraph{Closed forms.}\n"
        "\\[ \\mathbb{E}[\\sigma_T] = " + sp.latex(e_expr) + " \\]\n"
        "\\[ \\mathrm{Var}[\\sigma_T] = " + sp.latex(v_expr) + " \\]\n"
        "\\paragraph{Numerical pin at canonical fixture}\n"
        "At $\\sigma = 0.10 / \\sqrt{12}$, $T = 12$, "
        "$\\bar{X}/\\bar{Y} = 4000$: "
        f"$\\mathbb{{E}}[\\sigma_T] = {e_num:.6g}$, "
        f"$\\mathrm{{Var}}[\\sigma_T] = {v_num:.6g}$.\n"
    )


def _build_ou_tex() -> str:
    """OU stationary closed-form moments fragment."""
    sigma = sp.Symbol("sigma", positive=True)
    T = sp.Symbol("T", positive=True)
    theta = sp.Symbol("theta", positive=True)
    e_expr = sigma**2 / (2 * theta)
    v_expr = 2 * sigma**4 / ((2 * theta) ** 2 * T)
    e_num, v_num = ou_sigma_t_moments(CANONICAL_OU)
    return (
        "% Ornstein-Uhlenbeck stationary envelope moments.\n"
        "% ref: standard OU stationary Gaussian measure;\n"
        "% see e.g. Karatzas-Shreve, Brownian Motion and Stochastic Calculus, section 5.6.\n"
        "\\paragraph{Closed forms (stationary).}\n"
        "\\[ \\mathbb{E}[\\sigma_T] = " + sp.latex(e_expr) + " \\]\n"
        "\\[ \\mathrm{Var}[\\sigma_T] = " + sp.latex(v_expr) + " \\]\n"
        "\\paragraph{Numerical pin at canonical fixture}\n"
        "At $\\theta = 1$, $\\sigma = 0.10 \\cdot 4000 / \\sqrt{2}$, $T = 12$: "
        f"$\\mathbb{{E}}[\\sigma_T] = {e_num:.6g}$, "
        f"$\\mathrm{{Var}}[\\sigma_T] = {v_num:.6g}$.\n"
    )


def _build_merton_tex() -> str:
    """Merton jump-diffusion closed-form moments fragment.

    Mean form per Andersen-Piterbarg Vol I §2.7; variance form per
    §2.7.3 (compound-Poisson moment-of-moment, fourth-moment expansion
    of ``(e^J - 1)`` under Gaussian J).
    """
    sigma = sp.Symbol("sigma", positive=True)
    T = sp.Symbol("T", positive=True)
    lam = sp.Symbol("lambda", positive=True)
    mu_J = sp.Symbol("mu_J", real=True)
    sigma_J = sp.Symbol("sigma_J", positive=True)
    xbar = sp.Symbol(r"\bar{X}", positive=True)
    ybar = sp.Symbol(r"\bar{Y}", positive=True)
    env = (xbar / ybar) ** 2

    e_jump = (
        sp.exp(2 * (mu_J + sigma_J**2))
        - 2 * sp.exp(mu_J + sigma_J**2 / 2)
        + 1
    )
    e_expr = env * sigma**2 * T + lam * env * e_jump * T

    # M_4 = E[(e^J - 1)^4]  via binomial + Gaussian MGF
    m4 = (
        sp.exp(4 * mu_J + 8 * sigma_J**2)
        - 4 * sp.exp(3 * mu_J + sp.Rational(9, 2) * sigma_J**2)
        + 6 * sp.exp(2 * mu_J + 2 * sigma_J**2)
        - 4 * sp.exp(mu_J + sigma_J**2 / 2)
        + 1
    )
    v_expr = 2 * sigma**4 * env**2 * T + lam * env**2 * m4 * T

    e_num, v_num = merton_sigma_t_moments(CANONICAL_MERTON)
    return (
        "% Merton jump-diffusion envelope moments under mean-zero log-drift.\n"
        "% ref: Andersen & Piterbarg, Interest Rate Modeling Vol I,\n"
        "%      section 2.7 for E[sigma_T] and section 2.7.3 for Var[sigma_T]\n"
        "%      (compound-Poisson moment-of-moment).\n"
        "% Fourth-moment expansion uses E[(e^J - 1)^4] = sum_{k=0..4} C(4,k) (-1)^(4-k) E[e^{kJ}]\n"
        "% with E[e^{kJ}] = exp(k mu_J + k^2 sigma_J^2 / 2).\n"
        "\\paragraph{Closed forms.}\n"
        "\\[ \\mathbb{E}[\\sigma_T] = " + sp.latex(e_expr) + " \\]\n"
        "\\[ \\mathrm{Var}[\\sigma_T] = " + sp.latex(v_expr) + " \\]\n"
        "\\paragraph{Numerical pin at canonical fixture}\n"
        "At $\\sigma = 0.05/\\sqrt{12}$, $\\lambda = 1$, $\\mu_J = 0$, "
        "$\\sigma_J = 0.10$, $T = 12$, $\\bar{X}/\\bar{Y} = 4000$: "
        f"$\\mathbb{{E}}[\\sigma_T] = {e_num:.6g}$, "
        f"$\\mathrm{{Var}}[\\sigma_T] = {v_num:.6g}$.\n"
    )


def emit_all() -> dict[str, Path]:
    """Render and write the four ``.tex`` fragments; return ``{name: path}``.

    Idempotent: repeated invocations produce byte-identical output. The
    function returns the mapping ``stem -> Path`` for the four written
    fragments, in alphabetical order of stem, so callers can iterate
    deterministically.
    """
    out = _output_dir()
    out.mkdir(parents=True, exist_ok=True)
    fragments = {
        "eps_inversion": _build_eps_inversion_tex(),
        "sigma_t_moments_gbm": _build_gbm_tex(),
        "sigma_t_moments_merton": _build_merton_tex(),
        "sigma_t_moments_ou": _build_ou_tex(),
    }
    paths: dict[str, Path] = {}
    for stem, content in fragments.items():
        path = out / f"{stem}.tex"
        path.write_text(content, encoding="utf-8")
        paths[stem] = path
    return paths


if __name__ == "__main__":
    written = emit_all()
    for stem, path in written.items():
        print(f"wrote {stem}: {path}")
