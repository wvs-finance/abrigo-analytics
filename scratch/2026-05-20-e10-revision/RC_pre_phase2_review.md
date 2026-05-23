# RC Pre-Phase-2 Review — E10 GSPS (plan §7 hook 1)

**Reviewer:** Reality Checker. **Date:** 2026-05-20.
**Mandate:** plan v0.4 §7 hook 1 — verify the §6.2 NON-FANTASY observed-trace
anchor is genuine and non-trivial (RC OBS-1 / spec §7 field 7a); confirm
Phase-1 panel soundness; confirm no drift from accepted spec v0.6.
**Posture:** default NEEDS WORK; evidence required to clear.
**Verdict:** **PASS** — E10 is cleared to enter Phase 2.
**BLOCK count: 0.**

---

## 1. Reality-check commands executed

- Enumerated `scratch/2026-05-20-e10-revision/` + `notebooks/e10_gsps/diagnostics/`.
- Read: anchor extraction, E10.1 calibration note, E10.0 panel-window JSON,
  Phase-1 completion memo, spec v0.6 §0/§6/§7/§8/§9, plan §7, anti-fishing memory.
- Independently re-derived from the raw datasets:
  - `e10_q_anchor_daily.csv` centre sum = **63**, bracket sum = **151** —
    reconcile exactly with the extraction's headline 63 / 151 / 214.
  - `e10_q_anchor_calls.csv` = 214 data rows; `cut` of the tool column shows
    **only INCLUDE-set tools** (WebSearch 59, WebFetch 35, Bash-curl 63,
    mcp__dune/github/arxiv reads) — no `Edit`, `Read`, `Task*`, `Agent`,
    no MCP write op. The §1.1 mapping rule was actually applied, not just
    described.
  - Secret scan (`api_key|secret|token|sk-|bearer|0x[40-hex]`) over the calls
    CSV — **zero hits.** `coarse_target` column holds only URL hosts /
    `mcp__server__op` / `curl:<host>` strings. Metadata-only guarantee holds.

## 2. Anchor — genuine and non-trivial (spec §7 field 7a)

**STRONG.** The trace clears the field-7a HALT gate.

- **Genuine.** 214 timestamped tool calls mined from the literal Claude Code
  JSONL session record across 34 transcripts (~96 MB). Per-call timestamps are
  real ISO-8601 with sub-second precision and session IDs; the day sums
  reconcile to the headline counts. Not synthesised.
- **Non-trivial.** 4 query-bearing centre sessions / 4 active days; 7 bracket
  sessions / 12 active days; multi-week structure; 4 of the 5 §6.3 λ(t)
  modulations directly exhibited (diurnal/weekday, burstiness, event spikes,
  secular drift). It is not a flat or single-burst trace. ~60–130 priceable
  queries/month is small in absolute terms but is the **project's own** trace
  and is the §6.2 centre *by construction* — the spec does not set a volume
  floor, only a "genuine + non-trivial + representative" gate, which is met.
- **Mapping honestly applied — no over-counting.** The INCLUDE/EXCLUDE split is
  the x402-priceable network-external-fetch criterion; the github/dune
  read-vs-write split is load-bearing and correctly enforced (write ops in the
  EXCLUDE set, verified absent from the CSV). The note records that counting
  orchestration tools would have inflated Q ~12× — that inflation was
  *avoided*, the conservative direction. No `Read`/`Edit` leaked in.
- **CENTRE vs BRACKET split is clean.** CENTRE = the three abrigo-analytics
  path-history dirs (the project's own workflow → §6.2 centre); BRACKET = 6
  sampled non-abrigo project dirs (→ §6.2 researched-range upper envelope).
  The bracket brackets the centre *from above* on volume (42 vs 27/day) and
  the directory-selection sampling step is disclosed as deliberate, not a
  census. Roles map exactly onto spec §6.2's centre/bracket construction.

## 3. Phase-1 panel — sound and drift-free

**STRONG.** `E10.0_panel_window.json`: 5 currencies (COP, BRL, EUR, GBP, NGN) ×
30 months = 150 cells; common post-regime-break intersection window
2023-11-01 → 2026-04-30; per-currency daily rows (590–635) and frozen Tier-2
snapshot hashes recorded; ZAR/KES/GHS recorded as **dropped, not substituted**.
NGN confined to its post-June-2023 float regime (CORRECTIONS-E10-4 Fix 3) —
every NGN row in-window is post-float, so confinement does not shorten the
panel. The anti-fishing note states plainly that 150 cells clears N_MIN=75 at
the *cell* dimension while G≈5 is the binding identification dimension — no
N_MIN gaming, no window extension, no currency expansion. Consistent with the
HALT-DV → CORRECTIONS-E10-5 chain in the Phase-1 completion memo.

**OBSERVATION (WEAK, non-blocking).** The panel-window JSON's `spec` field cites
`v0.5 §3.3 / §7 field 6` and `corrections_ref` cites CORRECTIONS-E10-5. v0.6 is
now the accepted spec. Per spec v0.6 §0.5/§7, the field-6 panel *dimension* is
carried forward from v0.5 **verbatim and unchanged** — v0.6 amends only the FE
*description*. So the JSON's substantive content (5 currencies, 150 cells, G≈5,
window) is fully current; only the citation string lags one version. Not drift;
recommend a one-line citation refresh at notebook-build time.

## 4. Spec v0.6 drift check

**No substantive drift.** Cross-checked the calibration note + extraction
against accepted spec v0.6:

- **Descriptive posture** — intact. Calibration note §6 and the extraction make
  no inferential claim; Q is "a controlled input with a real anchor," verdict
  ladder untouched. Field 5 frozen.
- **5-currency panel** — intact. COP/BRL/EUR/GBP/NGN, 150 cells, G≈5; NGN
  regime-break preserved.
- **7 pre-pin fields** — intact. Fields 1–5,7 frozen; field 6's *dimension*
  unchanged; the calibration work touches none of them. The note correctly
  treats the overdispersion mechanism and λ(t) forms as §6.3 functional-form
  locks (which §6.3 explicitly routes to the E10.1 note), **not** as pre-pin
  fields — correct separation.

## 5. Anti-fishing check

**STRONG — no post-hoc tuning detected.**

- The overdispersion mechanism (Cox / doubly-stochastic NHPP) is *locked from
  the trace evidence*, not tuned to a target: the trace shows VMR≈20 at the
  daily level **independently in centre and bracket**, plus structured bursts
  (5-min windows of 16–24 calls), which one-directionally favours the Cox route
  over a bare negative-binomial. The choice precedes any simulation run; no
  magnitude target imported (Pair D's +0.137 etc. correctly out of scope).
- The four locked λ(t) modulations each carry a 4-part decision-citation tied
  to a specific extraction §-reference and `e10_q_anchor_buckets.json` field.
- The two OPEN items are flagged *honestly* (see §6), not silently filled.
- Arithmetic note (OBSERVATION, not a finding): the documented daily VMR of
  20.6 uses sample variance (n−1: 108.4/5.25); a population-variance recompute
  on the same 12 daily counts gives 18.9. Both are standard and both say "≈20×,
  decisively overdispersed." Convention difference only — not fishing. Worth a
  one-word convention note in the notebook for reproducibility.

## 6. The two OPEN items — confirmed non-HALT, spec-anticipated

**STRONG.** Both are genuinely spec-routed, not hidden gaps:

1. **Modulation 4 (month-end seasonality magnitude).** The own-trace spans ~11
   days inside one month (centre) / one month-boundary (bracket) — structurally
   too short to isolate a reporting-cadence bump from sprint clustering. The
   *modulation itself* is pre-committed (§6.3 item 4, retained); only its
   *magnitude* is deferred. Spec §6.2 **explicitly** routes bracket magnitudes
   to researched proxies. The note commits to pinning it at plan task 2.2 from
   proxies and to PARTIAL (per CORR-E10P-8) if proxies are unreachable — no
   flat-fill. Honest.
2. **`Q_low`.** Spec §2.4 defines `Q_low` as a behavioral qualitative-limit
   threshold; the metadata-only extraction (no payloads) structurally cannot
   observe whether a query *needed* archive/trace capability. The note records
   this as the reason `Q_low` cannot be own-trace-pinned and defers it to the
   §2.4 proxy-corroborated pinning rule at task 2.3b. Honest.

Neither is a disguised blocker. Both modulations/thresholds remain visible OPEN
slots routed to a spec-named mechanism; the own-trace centre is not weakened.

## 7. Secrets check

**STRONG.** The transcripts contained API keys; the extractor stores only
(timestamp, tool name, coarse target). Independent regex scan of the emitted
calls CSV found zero credential-shaped strings. Payload fields are never read
into the pipeline. No secret surfaced in any emitted artifact.

## 8. Findings ledger

| # | Severity | Finding |
|---|---|---|
| F-1 | STRONG | Anchor genuine + non-trivial — clears §7 field 7a; mapping honestly/conservatively applied; centre/bracket split clean. |
| F-2 | STRONG | Phase-1 panel sound — 150 cells, G≈5, regime-break correct, ZAR/KES/GHS dropped not substituted. |
| F-3 | STRONG | No substantive spec-v0.6 drift; descriptive posture, 5-currency panel, 7 pre-pin fields intact. |
| F-4 | STRONG | Two OPEN items honest, non-HALT, spec-anticipated; no flat-fill, no hidden gap. |
| F-5 | STRONG | Overdispersion mechanism + λ(t) forms trace-anchored / pre-pinned — no post-hoc tuning; metadata-only, no secrets. |
| O-1 | OBSERVATION | Panel-window JSON cites spec v0.5; v0.6 carries field 6 forward unchanged — citation string lag only, refresh at notebook build. |
| O-2 | OBSERVATION | Documented daily VMR 20.6 = sample variance; population variance = 18.9. Same conclusion; add a one-word convention note. |

**BLOCK: 0. STRONG: 5. WEAK: 0. OBSERVATION: 2.**

## 9. Verdict

**PASS.** No BLOCK findings. The NON-FANTASY observed-trace anchor is genuine
and non-trivial and clears spec §7 field-7a; the Phase-1 5-currency panel is
sound and drift-free; the calibration note and Phase-1 work have not drifted
from accepted spec v0.6; the two OPEN items are honest and spec-anticipated; no
post-hoc tuning; no secrets surfaced.

**E10 is CLEARED to enter Phase 2 (E10.1 R6 NHPP simulator build).** The two
OBSERVATIONs (O-1 citation refresh, O-2 VMR convention note) are housekeeping
for the Phase-2 calibration notebook and do not gate entry.

This PASS is contingent on the parallel Model QA reviewer not raising a
convergent BLOCK. If Model QA raises a BLOCK that converges with any item here,
the block protocol applies: CORRECTIONS block + scoped re-review before the
build begins. On the RC mandate alone, Phase 2 is cleared.
