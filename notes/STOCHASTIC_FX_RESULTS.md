# STOCHASTIC_FX_RESULTS — Stochastic-FX variant verdicts

Stage-3 open-item 2 (per `notes/STAGE_2_RESULTS.md` §5) closure: three-phase verification (algebraic / moment-match / KS goodness-of-fit) for the GBM, OU, and Merton jump-diffusion stochastic-FX families. R-tag prefix continues the STAGE_2_RESULTS R-tag lineage; Z1.x pins are spec v0.5 anchors.

Parent spec citations: §11.6 (Pin Z1.3b mean-only Phase-B gate; variance rel-err is audit-trail observation, not a gate); §11.7 (Pin Z1.4 per-family Phase-C reference dispatch — Merton uses empirical-CDF via high-N reference run at pinned `N_REF = 100_000`, `N_REF_SEED = 20260513`).

## §1 Cross-family summary

| R-tag | Family | composite_pass | Phase A max_residual | Phase B mean_rel_err | Phase C KS p-value | audit_block (prefix) |
|---|---|---|---|---|---|---|
| R1 | Geometric Brownian motion | PASS | 7.105e-15 | 1.121e-02 | 1.229e-01 | `3a0f75401d517f6d…` |
| R2 | Ornstein-Uhlenbeck | PASS | 3.553e-15 | 1.681e-03 | 3.033e-01 | `0589f35b10f1ca7f…` |
| R3 | Merton jump-diffusion | PASS | 2.274e-13 | 7.015e-03 | 1.160e-01 | `12890ce95a36ffea…` |

## §2 Per-family verdicts

### §2.1 Geometric Brownian motion (R1)

- **composite_pass**: PASS
- **Phase A** (Pin Z1.3a algebraic identity, tol = `NUMERICAL_IDENTITY_TOL`): `max_residual = 7.105427e-15`, pass = True
- **Phase B** (Pin Z1.3b mean-only, tol = `MOMENT_REL_TOL = 0.05` — spec v0.5 §11.6): `mean_rel_err = 1.120790e-02`, `var_rel_err = 2.126514e-01` (audit-trail only — does NOT gate composite_pass), pass = True
- **Phase C** (Pin Z1.4 KS goodness-of-fit, floor = `KS_PVALUE_FLOOR = 0.01` — spec v0.5 §11.7 per-family reference dispatch): `ks_pvalue = 1.228968e-01`, `n_paths = 1000` (TEST sample; N_REF for Merton reference recorded in audit_block, not here), pass = True
- **audit_block**: `3a0f75401d517f6db0d169effc4f1d1c1fd3a9dc59194d4b4905633e64c42462`
- **tex_anchor**: [notes/stochastic_fx_tex/sigma_t_moments_gbm.tex](../notes/stochastic_fx_tex/sigma_t_moments_gbm.tex)

### §2.2 Ornstein-Uhlenbeck (R2)

- **composite_pass**: PASS
- **Phase A** (Pin Z1.3a algebraic identity, tol = `NUMERICAL_IDENTITY_TOL`): `max_residual = 3.552714e-15`, pass = True
- **Phase B** (Pin Z1.3b mean-only, tol = `MOMENT_REL_TOL = 0.05` — spec v0.5 §11.6): `mean_rel_err = 1.681336e-03`, `var_rel_err = 2.711400e-02` (audit-trail only — does NOT gate composite_pass), pass = True
- **Phase C** (Pin Z1.4 KS goodness-of-fit, floor = `KS_PVALUE_FLOOR = 0.01` — spec v0.5 §11.7 per-family reference dispatch): `ks_pvalue = 3.033296e-01`, `n_paths = 1000` (TEST sample; N_REF for Merton reference recorded in audit_block, not here), pass = True
- **audit_block**: `0589f35b10f1ca7f36b5659b92b7194895d60eebad841183320ed411b3bed71e`
- **tex_anchor**: [notes/stochastic_fx_tex/sigma_t_moments_ou.tex](../notes/stochastic_fx_tex/sigma_t_moments_ou.tex)

### §2.3 Merton jump-diffusion (R3)

- **composite_pass**: PASS
- **Phase A** (Pin Z1.3a algebraic identity, tol = `NUMERICAL_IDENTITY_TOL`): `max_residual = 2.273737e-13`, pass = True
- **Phase B** (Pin Z1.3b mean-only, tol = `MOMENT_REL_TOL = 0.05` — spec v0.5 §11.6): `mean_rel_err = 7.015415e-03`, `var_rel_err = 2.727393e+00` (audit-trail only — does NOT gate composite_pass), pass = True
- **Phase C** (Pin Z1.4 KS goodness-of-fit, floor = `KS_PVALUE_FLOOR = 0.01` — spec v0.5 §11.7 per-family reference dispatch): `ks_pvalue = 1.159565e-01`, `n_paths = 1000` (TEST sample; N_REF for Merton reference recorded in audit_block, not here), pass = True
- **audit_block**: `12890ce95a36ffea7fd4ceea03b6dbc11356dd1589ec5a6ea155e4cda96f6848`
- **tex_anchor**: [notes/stochastic_fx_tex/sigma_t_moments_merton.tex](../notes/stochastic_fx_tex/sigma_t_moments_merton.tex)

## §3 References

- `docs/specs/2026-05-11-stochastic-fx-variant-design.md` v0.5 — parent spec; §6 three-phase verification; §11.6 (Pin Z1.3b mean-only Phase-B gate); §11.7 (Pin Z1.4 per-family Phase-C reference dispatch).
- `docs/plans/2026-05-11-stochastic-fx-variant.md` v0.6 — implementation plan; §10 Task 5 (this emitter); §16.5 + §16.7 (CORRECTIONS-α landing the v0.4→v0.5→v0.6 amendments).
- `notes/STAGE_2_RESULTS.md` §5 — Stage-3 open-item 2 hand-off (stochastic-FX variant per PRIMITIVES.md §15 open item 2).
