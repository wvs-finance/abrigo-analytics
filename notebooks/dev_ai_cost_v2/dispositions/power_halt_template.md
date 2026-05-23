# Power-HALT Disposition Memo Template

**Trigger:** `01_data_eda.ipynb` power-measurement HALT-checkpoint fired
(measured power < 0.50 at MDES = 0.40 residual-SD, current T).

**Anticipated per spec v0.2.1 CORRECTIONS-U** — Model QA's independent calc
at T=38 gave ~0.54–0.66 with HAC small-sample inflation, so this HALT is a
high-probability operational event.

## Pre-enumerated user pivots

### Option A: Expand T by waiting
- Pause iteration; resume when `max(weekday days observed)` ≥ <target T>.
- Re-run from Task 10 (panel build) at the new window.
- Decision-citation block: <fill at firing>

### Option B: Lower MDES to 0.30 residual-SD (documented downgrade)
- Update §2.2.B power threshold in a v0.2.2 patch.
- Disclose downgrade in §0 CORRECTIONS-X.
- Decision-citation block: <fill at firing>

### Option C: Accept lower-power result with explicit caveat in headline
- Proceed past HALT with documented power = <measured>.
- Add caveat banner to `04_r4s3_usd_behavioral.ipynb` headline cell.
- Decision-citation block: <fill at firing>

## HALT routing chain
Per `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`:
1. HALT + this disposition memo
2. User-enumerated pivot (A/B/C)
3. CORRECTIONS block in spec
4. Post-hoc 3-way review before resuming

## Status
- [ ] HALT fired (date: ____)
- [ ] User pivot selected: ____
- [ ] Disposition committed
