# DATA_PROVENANCE — `dev_ai_cost_v2` panel

Spec: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.10 §5.4.

## Build date
2026-05-18 (v0.2.10 audit-econ Wave-2/3 refresh; supersedes the v0.2.7 Y-9
build dated 2026-05-17)

## Repo state at build time
- Branch: `master`
- HEAD: post-Wave-3 commit `fff2501` (Wave-3 notebook re-execute + interp
  updates per v0.2.10) — DATA_PROVENANCE rewrite is the Wave-4 deliverable
  building on this HEAD.
- Spec version: 0.2.10 (§0.10 CORRECTIONS-W3 amendments #1–#12)
- Plan version: 2026-05-16 plan (17 tasks; Task 10 = this build refreshed under
  Wave-2 rebuild; Task 14 = POWER-HALT under v0.2.10 Amendment #8 lagged pin)

---

## ⚠ Iteration scope disclosure (per spec §2.3.1)

This iteration operates at **demonstration-grade** scope (relaxed floors per
CORRECTIONS-G/J, restated and pinned in v0.2.10 §2.3.1):

- `N_MIN = 38` (vs project default `N_MIN = 75`)
- `POWER_MIN = 0.50` (vs project default `POWER_MIN = 0.80`)
- `MDES_SD = 0.40` SD-units of Y (unchanged from project default)

Observed `N = 28` weekday rows after first-diff (29 raw rows minus 1 boundary
for `Δ`) → **below demonstration-grade floor of 38** → all PARTIAL
fail-to-reject verdicts that v0.2.9 had recorded under contemporaneous-pin
arms were **withdrawn in v0.2.10 (§0.10 Amendment #8)** in favor of the
spec-canonical lagged Newey-West recipe; under the lagged recipe the
realized power on the R4-S3-USD arm is `0.17 < 0.50` → verdict =
**POWER-HALT** (see disposition memo
`notebooks/dev_ai_cost_v2/dispositions/2026-05-18-task14-power-halt.md`).

Any claim that this iteration's findings graduate to verdict-grade
(project-default floors `N_MIN = 75`, `POWER_MIN = 0.80`) must be
re-supported with a larger panel (N ≥ 75 weekday rows) and a higher-power
test design (power ≥ 0.80 at MDES = 0.40 residual-SD). Demonstration-grade
findings are scaffolding for iteration-2 priors, not standalone evidence.

---

## Pinned external sources

| Source | Pin | Enforcement |
|---|---|---|
| LiteLLM commit SHA | `e58a561caa21169fb02174148444c08509ce7028` | Yes — caller-supplied SHA argument must `==` `LITELLM_SHA_PINNED` constant; raises `ValueError` on mismatch (pre-v0.2.10) |
| LiteLLM file sha256 | `05b050523e4c71581a12605c4bc49cf7049bafe3f51e1506b9da61afb9791db9` | **Yes (NEW v0.2.10 audit-econ #3 fix)** — `hashlib.sha256(file_bytes).hexdigest()` of the LiteLLM JSON payload is compared to `LITELLM_FILE_SHA256_PINNED`; raises `ValueError` on mismatch. Closes the audit-econ Critical-#3 finding that the previous SHA "pin" was a string-equality check on the operator-supplied commit SHA, not a content hash of the cached file. |
| Banrep daily TRM panel | Datos Abiertos Socrata (TRM oficial COP/USD), pulled 2026-05-17 | sha256 `4bf90ff093eb553659b23856974db965a0713446fceb28be2006d0c350432fe0` |
| Anthropic Claude Code session logs | local `~/.claude/projects/**/*.jsonl` at build time | (not hashed — operator-private; rooted by `--projects-root`) |

## CLI invocation

```
uv run python scripts/build_notional_cost_panel.py \
    --since 2024-01-01 \
    --until 2026-05-17
```

## Output

| Artifact | Path | Sha256 |
|---|---|---|
| Daily notional cost panel | `data/panels/notional_cost_panel.parquet` | `83dc8410bada080a1533bb308d889a33d6f85a7337974e6983afc03563fe06c8` |

(Supersedes v0.2.7 panel sha256 `c002df3b42042bf7db37499482486d1548a72f45bea8ff58d14569fb72d6b6ff`. The
panel rebuild under Wave-2 was triggered by audit-econ Critical-#9
(non-Anthropic upstream filter), High-#1 (Colombian-holiday counter
surfacing), and the #10 counter unit-split — none of which alone changed
panel rows, but the rebuild is the source of truth for the v0.2.10
counter-audit table below.)

### Panel shape
- Rows: **29** (one row per weekday-UTC date with recorded Claude Code usage
  that joins against TRM)
- Columns (11): `date_utc, notional_cost_usd, notional_cost_cop,
  trm_cop_per_usd, input_tok, output_tok, cache_create_5m, cache_create_1h,
  cache_read, n_messages, ephemeral_pi_share`
- Date window observed: **2026-01-06 → 2026-05-14**
- Post-first-diff usable N: **28** (one boundary lost to Δ)

---

## ccusage parity — 3-row disclosure (v0.2.10 audit-econ #2 fix)

**Why this section was rewritten.** The v0.2.7 build presented a 1-row
"1.000000× on every per-class ratio" parity table computed by an **inner
join** between the panel and ccusage UTC-mode output. The inner-join geometry
silently discarded every ccusage day absent from the panel (notably the
11 TRM-holiday-Monday weekdays where the operator had Claude activity but
TRM has no quote, plus the Codex-only days). The "1.0000×" claim was
therefore a tautology on the subset where the two sources agree by
construction — not a parity verification on the build window. Audit-econ
Critical-#2 demanded explicit 3-row geometry; this section delivers it.

**Comparison protocol (UNCHANGED from Y-9 closure).** ccusage's default daily
aggregator buckets timestamps into the operator's local timezone (EDT here).
Our panel buckets in UTC. A valid parity comparison MUST pass
`--timezone UTC` to ccusage; otherwise the per-class ratios contain a
timezone-shift artifact of up to ~1.3% per class (root-caused in spec §0.7
CORRECTIONS-Y-9).

**Reference command (canonical):**

```
npx ccusage@latest daily --since 20240101 --until 20260517 --timezone UTC --json
```

**Reproducibility script:**
`scratch/2026-05-18-ai-cost-delphi/parity_3row.py`. Inputs: the v0.2.10
panel (sha256 above) and a fresh ccusage UTC-daily dump. The script computes
set differences explicitly — it does NOT inner-join.

### Geometry (build window 2024-01-01 → 2026-05-17)

| Subset | Days | Panel cost (USD) | ccusage cost (USD) | Ratio |
|---|---|---|---|---|
| `panel ∩ ccusage` (both) | 29 weekdays | $2,796.53 | $2,796.53 | **0.999998×** |
| `panel \ ccusage` (panel-only) | 0 dates | $0.00 | n/a | n/a |
| `ccusage \ panel` (ccusage-only, ALL) | 27 dates | n/a | $2,396.05 | n/a |
| `ccusage \ panel` (ccusage-only, Claude-only — excl Codex) | 22 dates | n/a | $2,388.60 | n/a |
| **Combined window aggregate** | All cost in [2024-01-01, 2026-05-17] | $2,796.53 | $5,192.58 | **0.5386×** |

### Interpretation

The **0.1% per-class parity target** (§0.2 CORRECTIONS-Y-2 / §6 v0.2.2
amendments) **APPLIES ONLY to the `panel ∩ ccusage` subset** and IS satisfied
there (`0.999998× → 0.0002% absolute residual on cost`, well below the 0.1%
floor and four orders of magnitude below the 0.5% per-class success
criterion). Per-class token totals on this subset match ccusage to within
rounding (cache_create −0.001% / −1,044 tokens; all other classes ≤ ±0.000%).

The **combined-window ratio of 0.5386×** reflects three distinct
SCOPE differences (not algorithmic disagreement):

1. **Weekend Claude usage excluded from panel** (per spec §6 weekend-drop
   invariant — Banrep TRM does not quote weekends). Documented; counter
   `dropped_weekend_message_count = 11,765` (message-level) +
   `dropped_weekend_trm_row_count = 119` (TRM-row-level).
2. **Colombian-holiday Mondays with Claude activity, excluded by inner-join
   against TRM** (per audit-econ Critical-#1). Surfaced in v0.2.10 via the
   NEW counter `dropped_trm_missing_weekday_count = 8`. Largest single
   omitted day: 2026-05-11 Mon, $254.50.
3. **Codex / non-Anthropic days excluded entirely from panel scope** (per
   audit-econ Critical-#9). 136 message rows from `gpt-5.2-codex` /
   `gpt-5.3-codex` sessions were filtered upstream at JSONLReader admission
   in the v0.2.10 rebuild (previously these were silently misclassified as
   `dropped_unknown_model_count` at the pricing layer). 5 of the 27
   ccusage-only days are pure Codex sessions ($7.45 across those 5 days,
   `ccusage \ panel` ALL − Claude-only = $2,396.05 − $2,388.60 = $7.45).

The combined-window **0.5386× ratio is NOT a parity failure**; it is a
documented SCOPE difference. The spec's parity target is on the `both` subset
where the comparison is apples-to-apples. Re-classifying the 22
Claude-only-ccusage-only days as in-scope (which would require relaxing the
TRM-quote requirement on the panel join) is OUT OF SCOPE for this iteration
and would invalidate the FX-COP-per-USD identification anyway (no quote ⇒
no Δln TRM ⇒ no R5 regression possible on those rows).

---

## Counter audit (v0.2.10 — 12 counters + π̂; closes audit-econ #10 + #12)

All counter values are read from the `[OK] wrote …` stderr line emitted by
`scripts/build_notional_cost_panel.py` against the v0.2.10 sha256-pinned
panel. The 8-counter table in the v0.2.7 build (which contained a
unit-mixed `dropped_rows_count = 11,901` lumping message-rows and TRM-rows
into a single integer per audit-econ Critical-#10) is REPLACED in full.

| Counter | Source tier | Value | Interpretation | Changes vs v0.2.7 |
|---|---|---|---|---|
| `dropped_weekend_message_count` | panel_builder (weekend filter on message timestamp) | 11,765 | Claude assistant messages on Sat/Sun UTC dates (operator works weekends; weekends excluded from panel per §6 weekend-drop invariant) | **NEW name** — was implicit inside `dropped_rows_count=11,901` (audit #10 split) |
| `dropped_weekend_trm_row_count` | panel_builder (weekend filter on TRM date) | 119 | Banrep TRM rows for Sat/Sun dates that fail the weekday gate | **NEW name** — was implicit inside `dropped_rows_count=11,901` (audit #10 split) |
| `dropped_trm_missing_weekday_count` | panel_builder (TRM-missing weekday gate) | **8** | Weekday operator dates with Claude activity but NO TRM quote (Colombian Ley-Emiliani Monday holidays + other transferred holidays). Pre-v0.2.10 this was silently lumped into the unit-mixed counter; surfacing it is the audit-econ Critical-#1 fix. | **NEW counter** (audit #1 surfaces the holiday-Monday composition issue) |
| `dropped_error_count` | panel_builder (`is_error=True`) | **0** | API-error assistant rows excluded from cost aggregation (CORRECTIONS-V). Pre-v0.2.10 this read `73`; the drop to 0 is the predicted consequence of audit-econ Critical-#9 (the 73 `is_error` rows were on Codex sessions, now filtered UPSTREAM at JSONLReader admission rather than DOWNSTREAM at pricing). Hypothesis confirmed by the simultaneous appearance of `dropped_non_anthropic_count = 136`. | **Value changed** 73 → 0 (audit #9 upstream filter consumed the 73 Codex error rows before they reached the panel-builder is_error tier) |
| `dropped_non_assistant_count` | JSONLReader (Y-5a / Y-1) | 136,170 | JSONL rows where `type != "assistant"` (user/system/summary lines) | Unchanged semantics; value drift from 134,514 reflects new operator sessions between v0.2.7 and v0.2.10 builds |
| `dropped_malformed_count` | JSONLReader (Y-7) | **1** | The trailing-null-byte block in `agent-af5e1160f7be358ba.jsonl` that triggered the v0.2.3 → v0.2.4 amendment | Unchanged |
| `dropped_duplicate_count` | JSONLReader (Y-8) | **42,384** | Streaming-chunk / iteration duplicates by `${message.id}:${requestId}`; ccusage-mirror keep-larger-tokenTotal + hasSpeed-tiebreaker. ~63% of raw assistant rows were duplicates (the root cause of pre-v0.2.5's 2.11× cost overcount). | Unchanged semantics; minor drift from 42,387 reflects de-dup logic acting on slightly different raw-row population post-#9 upstream filter |
| `dropped_non_anthropic_count` | **JSONLReader (NEW v0.2.10 admission filter)** | **136** | Message rows whose `model` field starts with anything other than `claude-*` / `anthropic/*` — empirically `gpt-5.2-codex` and `gpt-5.3-codex` from Codex sessions commingled in `~/.claude/projects/`. Filter is applied UPSTREAM at JSONLReader so these rows never reach panel-builder; their tokens are excluded from panel aggregates entirely (not just their cost). | **NEW counter** (audit #9 fix) — REPLACES the v0.2.7 `dropped_unknown_model_count = 136` which mis-attributed these rows |
| `warn_missing_keys_count` | PricingTable (Y-5a / Y-3) | 6 | claude-* models in LiteLLM SHA pin missing one or more rate keys (e.g., `claude-sonnet-4-5`, `claude-sonnet-4-6` lack `cache_creation_input_token_cost_above_1hr`). Emits `UserWarning` at PricingTable load; missing categories contribute 0 at call time. | Unchanged |
| `dropped_unknown_model_count` | PricingTable (Y-5a) | **0** | Messages whose model name had no entry after the exact / `anthropic/` / longest-substring ladder. **The previous v0.2.7 value of 136 was misclassified** — those rows were Codex (non-Anthropic), not unknown-model Anthropic. Post-#9 upstream filter, the residual is genuinely 0. | **Value changed** 136 → 0 (audit #9 — the 136 were vendor-misattributed) |
| `substr_tiebreaker_count` | PricingTable (Y-5d) | 0 | Alphabetical-tiebreaker never invoked (longest-substring matches were unique in this corpus) | Renamed from `multiple_substring_match_warning`; value unchanged |
| `ephemeral_pi_share` (Y-6) | DailyNotionalPanel scalar | **0.398977** | 39.9% of cache-creation tokens are 1h-tier ephemeral. Cost magnitudes here apply 5m rate to total cache-creation; true cost is up to `1 + π̂·(rate_1h/rate_5m − 1) ≈ 1.40×` higher (rate_1h ≈ 2·rate_5m). FX-share point estimate (variance-based) is unaffected. | Unchanged |

**Counter drift (audit-econ #12) — RESOLVED.** All counters above are fresh
as of build date 2026-05-18 against the canonical panel sha256
`83dc8410…`. Cross-references in spec / notebooks / disposition memos to
the v0.2.7 8-counter table are obsolete and must be read alongside this
v0.2.10 12-counter refresh.

---

## Codex commingling disclosure (NEW — closes audit-econ Critical-#9)

The operator runs **both Claude Code AND OpenAI Codex** out of the same
`~/.claude/projects/` directory tree. Sessions with
`modelsUsed = ["gpt-5.2-codex"]` / `["gpt-5.3-codex"]` are present alongside
Claude sessions in the same per-project JSONL files (Codex tooling reuses
Anthropic's session-log directory convention).

**Pre-v0.2.10 behavior.** The 136 non-Anthropic message rows were silently
filtered at the **pricing layer** as `dropped_unknown_model_count = 136`,
implying the cause was Anthropic-side: "test sessions with `model: 'claude-3'`
shorthand or sentinel values." This was wrong — and worse, the tokens from
those 136 rows were **already included** in raw-row aggregates upstream of
the pricing miss; only the cost was zeroed out. The spec's §1.2
"subscribed Claude user as proxy for non-subscribed LATAM dev" framing did
not contemplate cross-vendor commingling, and the notional-cost headline
tacitly excluded Codex without disclosure.

**v0.2.10 fix (audit-econ #9).** A non-Anthropic admission filter moves
UPSTREAM to `JSONLReader.read()`: any assistant message whose `model` field
does not start with `claude-` (or its `anthropic/` mirror) is dropped at
admission and counted in `dropped_non_anthropic_count`. Tokens from those
rows never enter raw-row aggregates; the panel is now a strict Claude-only
slice. The prior `dropped_unknown_model_count = 136` collapses to 0 (the
136 were vendor-misattributed, not model-name-misattributed).

**Scope implication.** The R4-S3-USD "subscription-inelasticity" test is
explicitly conducted on a **Claude-only slice of total AI tooling
activity**, not on the operator's full AI spend. Per audit-econ #9, the
ccusage 3-row table above breaks out 5 pure-Codex days from the
`ccusage \ panel` set ($2,396.05 ALL − $2,388.60 Claude-only = $7.45
across those 5 Codex-only days). Headline notional cost ($2,796.53) is the
**Claude subset**, not the operator's full AI tooling expenditure. Cross-vendor
substitution effects (Codex ↔ Claude) are not measured in this iteration.

---

## Verdict status (v0.2.10 — post Wave-3 re-execute)

- **R5 PRIMARY** (FX-vol share of cost variance): FX share ≈ **0.003%**
  (Var(Δln TRM) / Var(Δln Cost^COP), variance-based, ratio-of-variances
  identification). UNCHANGED across the v0.2.7 → v0.2.10 audit-econ
  amendments; not sensitive to lag vs contemporaneous arm choice. **Verdict
  on R5 holds**: cost-side FX-share is empirically negligible at the
  Claude subscription level.
- **R4-S3-COP** (CPI-residualized COP-passthrough arm): **REGIME-CONDITIONAL
  FAIL** verdict preserved in the v0.2.9 audit trail; uninformative for the
  iteration-level verdict per v0.2.10 §0.10 Amendment #7 (R4-S3-COP was
  removed from the corroboration list because the CPI-residualization is
  collinear with the COP/USD level on the demonstration-grade panel).
- **R4-S3-USD** (USD-pure passthrough arm under lagged canonical Newey-West
  recipe): **POWER-HALT** verdict per v0.2.10 §0.10 Amendment #8.
  Realized power on the lagged arm = `0.17 < 0.50` (demonstration-grade
  floor). The v0.2.9 contemporaneous-pin PARTIAL-FAIL_TO_REJECT verdict on
  this arm is WITHDRAWN (Amendment #8 restores the spec-canonical lagged
  recipe as the verdict-producing arm; contemporaneous-pin retained as
  Z-arm sanity check, not as verdict measurement).
- **Z-arms** (corroboration arms Z1 / Z2 / Z3): treated as SAME-RATIO
  corroborations of R4-S3-USD, NOT independent measurements (per
  Amendment #4 — convergent-evidence framing rewritten to avoid
  double-counting). Z2 reframed as a sanity check (Amendment #6); Z3
  reverted to lagged → POWER-HALT (Amendment #8).

**Disposition memo cross-link:**
`notebooks/dev_ai_cost_v2/dispositions/2026-05-18-task14-power-halt.md`.

---

## Project-root scope

`/home/jmsbpp/.claude/projects/` — 1,732 JSONL files across all top-level
project directories. No allow-list / deny-list filter applied at the
project-directory level (the subscription-as-proxy framing per §1.2 treats
all Claude sessions as equally representative of the single-developer
pilot's pattern). The new model-level filter (`dropped_non_anthropic_count`,
v0.2.10) operates at JSONL-row admission and excludes Codex commingling
from the panel without excluding the originating project directories.

## Closed audit-econ Delphi findings (v0.2.10)

The following audit-econ Delphi findings (cohort
`scratch/2026-05-18-ai-cost-delphi/`) are closed by Wave-1/2/3/4 work:

| # | Title | Closure mechanism |
|---|---|---|
| #1 | Colombian-holiday weekday composition loss | Surfaced as `dropped_trm_missing_weekday_count = 8` (counter table above); 3-row parity table magnitude-discloses the $821.51 dropped weekday cost |
| #2 | ccusage parity "1.0000×" is a tautology on inner-joined subset | 3-row parity disclosure section above with explicit set-difference geometry |
| #3 | LiteLLM "SHA pin" was string-equality check, not file-sha256 | Dual-pin enforcement (commit SHA + file sha256); see "Pinned external sources" table above; commit `d02943d` |
| #4 | Convergent-evidence framing double-counts Z-arms | Spec §0.10 Amendment #4 rewrite; Z-arms treated as SAME-RATIO corroborations not independent measurements (this doc's Verdict section above) |
| #5 | Demonstration-grade scope not disclosed in headline | Headline disclosure block at top of this doc (§2.3.1) |
| #6 | Z2 over-promoted as independent measurement | Spec §0.10 Amendment #6 reframes Z2 as sanity check |
| #7 | R4-S3-COP collinearity not flagged | Spec §0.10 Amendment #7 removes R4-S3-COP from corroboration list; Verdict section above |
| #8 | Z3 contemporaneous-pin masked POWER-HALT | Spec §0.10 Amendment #8 reverts Z3 to lagged canonical recipe → POWER-HALT; disposition memo `2026-05-18-task14-power-halt.md` |
| #9 | Codex commingling silently misattributed at pricing layer | Upstream JSONLReader admission filter; `dropped_non_anthropic_count` counter; Codex commingling disclosure section above; commit `abbbcbd` |
| #10 | Unit-mixed `dropped_rows_count = 11,901` lumped message + TRM rows | Counter split into 3 named counters (`dropped_weekend_message_count`, `dropped_weekend_trm_row_count`, `dropped_trm_missing_weekday_count`); commit `96c51e1` |
| #11 | N-sensitivity not disclosed in headline | Covered by #1 surfacing (the 8 dropped weekdays) + §2.3.1 floor disclosure block at top of this doc |
| #12 | Counter values in DATA_PROVENANCE drifted from current pipeline | Resolved by Wave-2 panel rebuild; all 12 counters in the table above are fresh against v0.2.10 panel sha256 `83dc8410…` |

## Known amendments (carried forward, still active)

- **Y-8 (uniqueHash dedup, v0.2.5)**: OSS-mirror dedup by
  `${message.id}:${requestId}` with keep-larger-tokenTotal + hasSpeed
  tiebreaker → 42,384 duplicates skipped (~63% of raw assistant rows). Active.
- **Y-7 (line-level malformed-skip, v0.2.4)**: trailing-null-byte block at
  `agent-af5e1160f7be358ba.jsonl:586` skipped silently →
  `dropped_malformed_count = 1`. Active.
- All 6 CR-Z architectural pins (v0.2.3). Active.
- All 4 Y-1/Y-2/Y-3/Y-4 OSS-mirror amendments (v0.2.2). Active.
- Y-9 timezone-comparison protocol (v0.2.7 §0.7): `--timezone UTC`
  mandatory for ccusage parity invocations. Active.

## Deferred (post-v0.2.10)

- Quantitative hard-fail threshold on
  `dropped_malformed_count / total_lines` (v0.2.4 RC FLAG-5a). First
  baseline empirically established: `1 / 134,514 = 7.4e-6`; v0.2.10
  reaffirms baseline at `1 / 136,170 = 7.3e-6`.
- DATA_PROVENANCE schema pin for Y-7's counter (this document instantiates
  the freeform shape; v0.3+ to formalize as a Pydantic model under
  `simulations/dev_ai_cost_v2/`).
- ccusage-parity oracle activation pending real PII-redacted fixture
  replacing the synthetic one at
  `simulations/tests/fixtures/real_claude_jsonl/synthetic_sample.jsonl`.
  CI-locked parity check MUST pass `--timezone UTC` to the ccusage
  invocation per the Y-9 closure protocol. (audit-econ #9 CI-enforcement
  follow-up; not closed in v0.2.10.)
- Remaining audit-econ Mid/Low findings (cohort
  `scratch/2026-05-18-ai-cost-delphi/`, agents 1 and 3) not enumerated
  in the #1–#12 Critical/High list above; queued for v0.2.11 review.
- Cross-vendor substitution (Codex ↔ Claude) measurement: out of scope for
  this iteration; would require a separate Codex panel and a joint
  cross-vendor cost model. Queued as a candidate iteration-2 prior.
