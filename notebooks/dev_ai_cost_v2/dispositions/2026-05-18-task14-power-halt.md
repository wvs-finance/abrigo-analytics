# Disposition memo — Task 14 R4-S3-USD POWER-HALT (2026-05-18)

**Spec:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.10 §0.10
CORRECTIONS-W3 Amendment #8 (Z3 REVERTED to LAGGED canonical recipe).
**Plan:** Task 14, post-Wave-0 closure.
**Notebook:** `notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb`.

## Trigger

Power-measurement HALT-checkpoint fired in Trio 4:
- Canonical recipe per v0.2.10 §0.10 Amendment #8 = **LAGGED tokens partialling**
  (matches R4-S3-USD k=1 spec's lag structure).
- Measured power (canonical) = **0.1745**  (< 0.50 demonstration-grade floor).
- Alternative recipe (contemporaneous, diagnostic) = **0.7115**.
- N observed = 28 (< spec floor N_MIN = 38; not reached because power HALT fires first).
- Residual SD (canonical / lagged) = 1.155794.
- MDES effect at 0.40 × residual SD = 0.462317.

**Anticipated per CORRECTIONS-U**: Model QA's independent calc at T=38 gave
~0.54–0.66 with HAC small-sample inflation, so this HALT is a high-probability
operational event. v0.2.10 §0.10 Amendment #8 reverts the v0.2.9 §0.9
contemporaneous pin to honest disclosure — the lagged recipe matches the
regression's own lag structure and is the natural reading of CORRECTIONS-J.

## Pre-enumerated user pivots (from `dispositions/power_halt_template.md`)

### Option A: Expand T by waiting
- Pause iteration; resume when `max(weekday days observed) ≥ 38` (spec N_MIN).
- Re-run from Task 10 (panel build) at the new window.
- Decision-citation block: <fill at user-selection time>

### Option B: Lower MDES to 0.30 residual-SD (documented downgrade)
- Update §2.2.B power threshold in a v0.2.11 patch.
- Disclose downgrade in §0 CORRECTIONS-X-NEXT.
- Decision-citation block: <fill at user-selection time>

### Option C: Accept lower-power result with explicit caveat in headline
- Proceed past HALT with documented canonical (lagged) power = 0.1745.
- Add caveat banner to `04_r4s3_usd_behavioral.ipynb` headline cell.
- Decision-citation block: <fill at user-selection time>

## HALT routing chain
Per `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`:
1. HALT + this disposition memo (DONE)
2. User-enumerated pivot (A/B/C) — pending
3. CORRECTIONS block in spec — if user pivot adds a threshold change
4. Post-hoc 3-way review before resuming

## Status
- [x] HALT fired (date: 2026-05-18; canonical lagged power 0.1745 < 0.50)
- [ ] User pivot selected: ____
- [ ] Disposition committed (this file is staged; commit follows user-pivot decision)

## v0.2.10 audit-trail context

This memo supersedes the v0.2.9 PARTIAL-FAIL_TO_REJECT verdict recorded in
commit `90f099e` (2026-05-17, notebook 04 Z3 power-recipe pin + PARTIAL-*
verdict under contemporaneous canonical). The v0.2.9 commit remains in git
history for audit trail; v0.2.10 §0.10 Amendment #8 reverts the canonical
recipe to lagged on honest-disclosure-as-process grounds (the v0.2.9
"first-principles" defense for contemporaneous overstated the case).

The corroboration accounting is now **ONE descriptive ratio (R5) + ONE
POWER-HALTed behavioral test (R4-S3-USD)** per v0.2.10 §0.10 Amendment #4
(Z-arms and R4-S3-COP are same-ratio corroborations / removed; not
independent measurements).
