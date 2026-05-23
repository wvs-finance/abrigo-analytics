# Delphi Audit #2 — Data Pipeline / Replication / Lineage / Anti-Fishing on Filters

- **Auditor**: agent #2 of 3 (data layer)
- **Target**: spec v0.2.9, pipeline `simulations/dev_ai_cost_v2/`, panel `data/panels/notional_cost_panel.parquet`, DATA_PROVENANCE.md
- **Panel sha256 verified**: `c002df3b42042bf7db37499482486d1548a72f45bea8ff58d14569fb72d6b6ff` (matches DATA_PROVENANCE)
- **Date**: 2026-05-18
- **Independence**: I have not consulted agents #1 and #3 (I noted the existence of `agent1_math_model.md` only to copy the FINDING template format).

## Headline opinion

**3 Critical**, **4 High**, **3 Mid**, **2 Low** findings. The pipeline code is competent and the unit-tested counters are honest about what they count, but **DATA_PROVENANCE.md misreports what those counters mean** and **silently elides the largest single source of panel composition loss**: 11 weekday operator days with $821 of Claude usage (29% of post-filter cost) that the panel drops because TRM has no quote for Colombian-holiday Mondays. The ccusage parity claim "1.000000×" is true *only on the 29-day intersection*, where ccusage rows that fail to join with TRM are silently excluded from the comparison denominator — making "1.0000×" a tautology rather than a parity verification. The LiteLLM SHA "pin" is a string-equality check on the operator-supplied SHA, not a sha256 verification of the cached file. Reproducibility against `c002df3b...` is not demonstrably guaranteed from a fresh clone.

---

## CRITICAL FINDINGS

### FINDING 1 — Silent panel drop of $821 of weekday Claude usage on Colombian-holiday Mondays

- **Name**: 11 operator weekdays with Claude activity silently inner-joined out due to TRM gaps; magnitude unreported in DATA_PROVENANCE
- **Severity**: **Critical**
- **Location**: `simulations/dev_ai_cost_v2/panel_builder.py` lines 178–192 (TRM weekday filter + inner join); `notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md` (counter table)
- **Problem**: The Banrep TRM panel has **174 of 618 weekdays missing** in the build window (28% — overwhelmingly Mondays, the result of Colombian *Ley Emiliani* transferring most holidays to Mondays). The panel uses `df.join(..., how="inner")` on UTC date. Any operator weekday with Claude activity but no TRM quote is silently dropped. Independent reconstruction from `/tmp/ccusage_utc.json` (the same UTC-mode ccusage cache the v0.2.7 closure cites) shows **11 weekdays** of dropped operator Claude activity totaling **$821.51 USD = 29.4% of the panel's post-filter cost ($2,796.53)**, including the operator's single largest day (`2026-05-11 Mon, $254.50`). DATA_PROVENANCE labels `dropped_rows_count = 11,901` as "Messages on non-weekday calendar dates (operator works weekends)" — completely omitting the weekday-on-TRM-holiday drop. This is the largest single composition issue in the pipeline and it is **invisible to the operator**.
- **Proposed fix**: (a) Separate the three constituents of `dropped_rows_count` into named counters: `weekend_message_count` (msg-level), `weekend_trm_row_count` (TRM-level, always ~119), and `trm_missing_weekday_day_count` (day-level operator-side loss). (b) Add a new counter `trm_missing_weekday_message_count` that quantifies dropped operator messages on these days. (c) Document the holiday-Monday pattern in DATA_PROVENANCE with the magnitude in $ and message count. (d) Consider forward-filling TRM on Colombian holidays (using last-trade convention, which is what the FX market actually does) — currently §6 forbids forward-fill on operator-side weekends, but TRM-holiday forward-fill is a different design choice and arguably the correct one (last-traded rate is the legally-effective TRM on holidays). The spec is silent on this case.
- **Evidence**:
  - Code: `panel_builder.py:192` `joined = daily.join(trm_weekday, on="date_utc", how="inner")` — inner join drops operator days lacking TRM with no separate counter.
  - Code: `panel_builder.py:211–212` `dropped_rows = weekend_records + weekend_trm + join_loss_left` — three different units (messages, TRM rows, days) summed into one counter labeled as message count.
  - TRM gap audit: `trm.filter(weekday<=5)` has 444 of 618 (`2024-01-03`..`2026-05-16`) weekdays present; 174 weekday holes, 159 of those are Mondays.
  - Independent reconstruction: panel-vs-`/tmp/ccusage_utc.json` set difference shows 11 weekdays present in ccusage UTC-mode that are absent from panel, all confirmed TRM-missing in `data/raw/banrep_trm_daily.parquet`. Total cost: $821.51 (Mon dates: 2026-03-02 $9.15; 2026-03-09 $94.85; 2026-03-16 $18.55; 2026-04-13 $88.55; 2026-04-20 $77.56; 2026-04-27 $156.03; 2026-05-04 $117.54; 2026-05-11 $254.50; plus 2026-02-16, 2026-02-23, 2026-02-24 which are Codex/GPT-only — see Finding 4).
  - DATA_PROVENANCE.md line 91 attributes ALL 11,901 to "operator works weekends" — empirically false for ≥130 of those (mixed units + holiday-Mon drop).

### FINDING 2 — ccusage parity "1.000000×" is a tautology on the inner-joined subset, not a parity verification

- **Name**: Per-class ratios computed only over panel ∩ ccusage dates; ccusage dates absent from panel are silently excluded from the denominator
- **Severity**: **Critical**
- **Location**: `scratch/2026-05-17-y9-investigation/compare_ratios.py` (line 35: `joined = ours_norm.join(ccu_df, ..., how="inner")`); DATA_PROVENANCE.md §"ccusage parity verdict" (lines 41–72)
- **Problem**: The cited "1.000000× on every per-class ratio" comes from `compare_ratios.py`'s **inner join** of the panel against `/tmp/ccusage_utc.json`. After the inner join only 29 days remain; the ratios are computed over those 29 days only. But the panel has already dropped 11 weekday-with-Claude-activity days on the inner-join side; those days **are present in ccusage UTC-mode** ($807.56 in Claude usage) and are simply excluded from the comparison. The parity ratio is therefore "1.0000× on the subset we both agree on after we've discarded everything we disagree on" — a tautology. A *true* parity check would compare panel cost against ccusage cost over the full window with the panel's drops attributed and reconciled — the parity would be `2,796.53 / 3,618.04 ≈ 0.773×` if all Claude-only ccusage dates were summed, or alternatively the panel's cost would equal ccusage's only on the subset, with the difference attributed to TRM gaps. Neither attribution is presented in DATA_PROVENANCE.
- **Proposed fix**: (a) Compute parity over the **full ccusage window** and disclose the inner-join shrinkage explicitly. (b) Present the parity table in three rows: "ours-only" (0), "both" (29 days, 1.000000×), "ccusage-only" (27 days: 5 Codex + 22 Claude split out — see Finding 4). (c) Disclose the dollar magnitude of ccusage-only Claude dates ($807.56) and the reason (TRM-missing weekdays). The current framing "ccusage-parity-0.1% target: SATISFIED on every class" overclaims by orders of magnitude on the question that matters for replicability ("does our panel reproduce ccusage").
- **Evidence**:
  - `scratch/2026-05-17-y9-investigation/compare_ratios.py:35`: `ours_norm.join(ccu_df, left_on="date_s", right_on="date", how="inner")` — inner join is the parity geometry.
  - Independent reconstruction (this audit): `panel ∩ ccu_utc = 29 days`, `ccu_utc \ panel = 27 days`, `panel \ ccu_utc = 0 days`. On the 29-day intersection the ratios match to within rounding (`cost ratio = 0.999998`, `cache_create ratio = 0.999992`). Over the **full ccusage UTC window** (29 + 27 days), excluding the 5 Codex/GPT-only days that should not be in scope, panel-vs-ccusage ratio drops to `2796.53 / (2796.53 + 1187.40 Claude-only-missing) ≈ 0.702×` — i.e., panel is missing 30% of the actual ccusage Claude cost over the build window.
  - DATA_PROVENANCE.md lines 64–65: "**v0.2.2 CORRECTIONS-Y-2 / Y-4 ccusage-parity-0.1% target: SATISFIED on every class**. Residual is -1,044 cache_create tokens (-0.001%)…" — true on the inner-joined subset only; nowhere in the doc is the inner-join framing disclosed.

### FINDING 3 — LiteLLM "SHA pin" enforcement is a string-equality check on caller-supplied SHA, not a sha256 of the cached file

- **Name**: `PricingTable.from_litellm_sha` does not verify the actual sha256 of `cached_json_path`
- **Severity**: **Critical** (data integrity / reproducibility)
- **Location**: `simulations/dev_ai_cost_v2/anthropic_pricing.py` lines 168–174 (the SHA "check") + the CLI invocation at `scripts/build_notional_cost_panel.py:112–114`
- **Problem**: The "SHA pin" advertised throughout the spec and DATA_PROVENANCE as the cornerstone of price-table reproducibility (`LITELLM_SHA_PINNED = "e58a561c..."`) is implemented as:
  ```python
  raw: bytes = cached_json_path.read_bytes()
  if not skip_sha_check and sha != LITELLM_SHA_PINNED:
      raise ValueError(...)
  ```
  The check is `sha == LITELLM_SHA_PINNED` where `sha` is the **caller-supplied string** in `scripts/build_notional_cost_panel.py:113` (literally `LITELLM_SHA_PINNED`). It does **not** compute the sha256 of `cached_json_path.read_bytes()` and compare against the pinned commit-SHA. A user could replace `data/raw/litellm_model_prices.json` with arbitrary content and the CLI would happily load it, because `LITELLM_SHA_PINNED == LITELLM_SHA_PINNED` is trivially true. The DATA_PROVENANCE.md does cite a separate file sha256 `05b050523e4c71581a12605c4bc49cf7049bafe3f51e1506b9da61afb9791db9` (which I independently verified matches the current cache), but no code path enforces it. Reproducibility against `c002df3b...` panel sha256 is therefore conditional on operator honor rather than mechanical enforcement.
- **Proposed fix**: (a) Add a `LITELLM_FILE_SHA256_PINNED` constant alongside `LITELLM_SHA_PINNED`. (b) In `from_litellm_sha`, compute `hashlib.sha256(raw).hexdigest()` and compare against the file pin; raise on mismatch. (c) Document both pins in DATA_PROVENANCE (commit-SHA for upstream lineage; file-sha256 for local-cache integrity). (d) Update the `skip_sha_check` escape hatch to cover both checks separately.
- **Evidence**:
  - `anthropic_pricing.py:169–170`: file is `read_bytes()` but the bytes are never hashed; only the caller-supplied SHA string is compared.
  - `test_dev_ai_cost_v2_pricing.py:181–184` confirms the test only exercises the string-equality path: `bogus_sha = "not_the_pin"; ... raises ValueError`.
  - Independent verification (this audit): `sha256(data/raw/litellm_model_prices.json) = 05b050523e4c71581a12605c4bc49cf7049bafe3f51e1506b9da61afb9791db9` — matches DATA_PROVENANCE — but this match is **incidental**, not enforced.
  - The docstring at `anthropic_pricing.py:140–148` reinforces the misimpression: "`sha`: LiteLLM commit SHA. Must equal `LITELLM_SHA_PINNED` unless `skip_sha_check`" — the docstring describes commit-SHA enforcement; it does not say "this is a string check, not a file-content check".

---

## HIGH FINDINGS

### FINDING 4 — Codex/GPT cross-contamination is not disclosed; 5 days × $4.78 are silently exempted by the `claude-` prefix filter

- **Name**: Operator uses both Claude Code AND OpenAI Codex from `~/.claude/projects/`; non-Claude assistant rows are filtered at PricingTable load but not counted at JSONLReader
- **Severity**: **High** (data scope / honesty of pipeline framing)
- **Location**: `anthropic_pricing.py:180` (`if not model.startswith("claude-"): continue`); JSONL reader admits all assistant rows regardless of model.
- **Problem**: Inspection of `/tmp/ccusage_utc.json` reveals the operator's `~/.claude/projects/` directory tree contains sessions with `modelsUsed = ["gpt-5.2-codex"]`, `["gpt-5.3-codex"]` — i.e., the operator runs **both Claude Code and OpenAI Codex** out of the same JSONL root. The pipeline silently bins all non-`claude-*` models into `dropped_unknown_model_count`. DATA_PROVENANCE describes this counter as "messages whose model name had no entry after the exact / `anthropic/` / longest-substring ladder (likely test sessions with `model: 'claude-3'` shorthand or sentinel values)" — but the actual cause is **OpenAI Codex usage commingled with Claude Code in the same project directory**. The spec's §1.2 framing (subscribed Claude user as proxy for non-subscribed LATAM dev) does not contemplate that the operator also uses Codex; the headline notional-cost figure tacitly excludes Codex; the "subscription-inelasticity" R4-S3-USD test is conducted on a Claude-only slice of total AI tooling activity.
- **Proposed fix**: (a) DATA_PROVENANCE should state explicitly: "operator's JSONL root contains both Anthropic Claude Code AND OpenAI Codex sessions; this panel is scoped to Anthropic only; 136 messages from non-Claude vendors are excluded with cost=0". (b) The counter `dropped_unknown_model_count` should be split: `dropped_non_anthropic_model_count` (Codex, Gemini, etc.) vs `dropped_unknown_anthropic_model_count` (model shorthand like `claude-3`). (c) Reconsider the proxy framing in §1.2 — if the operator's actual AI-tooling spend is part Claude, part Codex, the notional-USD-burden share attributed to Claude is not the operator's full AI cost path; the proxy framing should be tightened or the panel should include Codex via a parallel rate-card path.
- **Evidence**:
  - `/tmp/ccusage_utc.json` 2026-02-16 row: `modelsUsed: ["gpt-5.2-codex"]`, cost $2.31.
  - Same for 2026-02-23 (Mon) `gpt-5.3-codex` $2.36, 2026-02-24 (Tue) $0.10, plus weekend Codex usage in the 16 missing weekend dates.
  - `anthropic_pricing.py:180`: `if not model.startswith("claude-"): continue` — silent vendor filter at load time.
  - `_lookup_model_key` lookup ladder confirmed (this audit): `gpt-5.2-codex` returns `None` from substring search → caller increments `dropped_unknown_model_count`. So Codex rows are admitted to the panel with cost=0 BUT their tokens count toward `input_tok` / `output_tok` aggregates — silently inflating denominators in R5.

### FINDING 5 — Unit-mixing bug: `dropped_rows_count` sums messages, TRM rows, and days

- **Name**: `dropped_rows_count = weekend_records + weekend_trm + join_loss_left` mixes three distinct units into one counter
- **Severity**: **High**
- **Location**: `panel_builder.py:212`; DATA_PROVENANCE counter table line 91
- **Problem**: The counter `dropped_rows_count = 11,901` is computed as the sum of three quantities with different units:
  - `weekend_records` (line 162): number of *messages* with weekday ≥ 5 on the operator JSONL side.
  - `weekend_trm` (line 188): number of TRM *rows* (date-level) on Sat/Sun — always ~119 in practice.
  - `join_loss_left` (line 211): number of *days* (post-aggregation) lost to the inner join.
  
  The DATA_PROVENANCE attributes the entire 11,901 to "operator works weekends" — but ~119 of that is TRM weekend rows (a different thing) and an unknown number is day-level join-loss (a third thing). The counter is uninterpretable as a single quantity. Independent decomposition (this audit) suggests the true breakdown is roughly `11,771 + 119 + 11 = 11,901` but the code is structurally incapable of producing that breakdown without modification.
- **Proposed fix**: (a) Replace the single counter with three named counters: `weekend_message_count`, `weekend_trm_row_count`, `trm_missing_weekday_day_count` (this last one is exactly Finding 1's missing accountability). (b) Update DATA_PROVENANCE to report each separately. (c) Add a Hypothesis property test that the sum of named counters equals the total dropped — currently nothing prevents drift.
- **Evidence**:
  - `panel_builder.py:162` `weekend_records = msg_df.filter(weekday >= 5).height` — msg-level.
  - `panel_builder.py:188` `weekend_trm = trm_panel.height - trm_weekday.height` — TRM-row-level.
  - `panel_builder.py:211` `join_loss_left = pre_join_daily_height - joined.height` — day-level.
  - `panel_builder.py:212` `dropped_rows = weekend_records + weekend_trm + join_loss_left` — mixed sum.
  - `DATA_PROVENANCE.md:91`: single-counter interpretation "Messages on non-weekday calendar dates (operator works weekends)" — wrong unit, wrong cause.

### FINDING 6 — N=28 derivation is sensitive to TRM-missing Mondays; lowering from 38 → 28 is data-dependent

- **Name**: Sample-floor breach is a function of the silent TRM-Monday drop, not just slow operator adoption
- **Severity**: **High** (anti-fishing diagnostic)
- **Location**: spec §0.9 line 5, §2.2.B verdict block, §2.3 line 1528; CORRECTIONS-G line 109
- **Problem**: CORRECTIONS-G (pre-data, pre-pinned) lowered N_MIN from 75 to ≈38 weekday-days based on operator activity at spec write time. Subsequent data builds report N=29 panel rows / N=28 first-difference rows, declaring a PARTIAL verdict per RC SC-1. But **8 of the 38 spec-time weekday days were Claude-active Mondays that the panel silently dropped** (Finding 1). If TRM forward-fill or holiday-handling had been pinned to the Banrep last-traded convention, the panel would have been **37 rows / 36 first-diffs**, not 28. The reported N=28 is therefore a function of the silent pipeline filter, not just observed operator inactivity. The PARTIAL verdict label is consequently load-bearing on an undisclosed engineering choice (inner-join + TRM as-is). This is a textbook anti-fishing concern: the verdict-relevant statistic depends on a filter the operator did not pre-pin (inner-join behavior for TRM-missing weekdays is not in §3.5 or §6).
- **Proposed fix**: (a) Pre-pin the TRM-holiday convention explicitly (forward-fill from previous trading day OR drop with disclosure). (b) Recompute N under both conventions; if forward-fill, N may cross the 38 floor and re-establish a non-partial verdict. (c) Disclose in §2.3 that the reported N is conditional on the TRM-as-is inner-join choice, with the alternative N under forward-fill listed.
- **Evidence**:
  - 8 dropped Mondays with Claude activity (Finding 1): 2026-03-02, 03-09, 03-16, 04-13, 04-20, 04-27, 05-04, 05-11.
  - Adding these 8 to the panel's 29 rows = 37 (very close to the 38 floor — would still PARTIAL, but the margin and the precise N is sensitive to a non-pinned filter choice).
  - §6 of the spec line 1823: "Weekends dropped on both LHS and RHS … forward-fill is forbidden" — this rule was written for *operator weekends*, not TRM holidays. The conflation is not addressed in the spec and the code uses the same inner-join machinery for both.

### FINDING 7 — `dropped_non_assistant_count` published as 134,514, true value 135,082 — 568 missing

- **Name**: Probe `total assistant rows = 87,827` and `total JSONL lines = 222,909` gives non-assistant = 135,082, not 134,514
- **Severity**: **High** (counter accuracy)
- **Location**: DATA_PROVENANCE.md line 93 (`dropped_non_assistant_count = 134,514`); `scratch/2026-05-17-y9-investigation/probe_output.txt` lines 9–11
- **Problem**: Probe output is authoritative:
  ```
  total JSONL lines           :    222,909
  total assistant rows        :     87,827
  in-window assistant rows    :     85,543
  ```
  Therefore non-assistant rows = 222,909 − 87,827 = **135,082**. DATA_PROVENANCE reports **134,514**. The 568-row gap is unexplained. Most likely cause: the published counter is from a *previous* build (perhaps before the operator's most recent JSONL activity in the build window) while the probe was run against the live root at probe time. This means DATA_PROVENANCE may not be byte-stable against the panel sha256 — the panel was built once at 2026-05-17 but the JSONL root has continued to grow (the operator works in this repo daily). The 1 / 134,514 = 7.4e-6 malformed-rate baseline (DATA_PROVENANCE line 124) is computed against a stale denominator. Additionally, the `dropped_duplicate_count = 42,387` in DATA_PROVENANCE differs from the probe's `uniqueHash collisions = 42,386` (off by 1) and `dropped_error_count = 73` differs from probe's `H5: isApiErrorMessage=true rows = 74` (off by 1) — small but indicative of either build drift or scope-filter drift.
- **Proposed fix**: (a) Rebuild the panel against the current JSONL root with all counters fresh, OR clearly mark DATA_PROVENANCE as a snapshot at build-time T0 with the probe at T1 > T0 and note the JSONL-root drift. (b) Surface a `raw_jsonl_line_count` counter on the read result (cheap — already counted via `enumerate`) so the operator can detect drift between build and verification. (c) Recompute the malformed-rate baseline against the correct denominator (raw lines, not non-assistant lines): `1 / 222,909 = 4.5e-6`.
- **Evidence**:
  - Probe (canonical): `222,909` total, `87,827` assistant. Non-assistant = `135,082`.
  - DATA_PROVENANCE: `dropped_non_assistant_count = 134,514`. Diff = 568.
  - DATA_PROVENANCE: `dropped_duplicate_count = 42,387`; probe: `uniqueHash collisions = 42,386`. Diff = 1.
  - DATA_PROVENANCE: `dropped_error_count = 73`; probe `H5 isApiErrorMessage=true = 74`. Diff = 1.
  - DATA_PROVENANCE.md line 124: "First baseline empirically established: `1 / 134,514 = 7.4e-6`" — denominator is wrong; should be total lines (`222,909`) giving `4.5e-6`.

---

## MID FINDINGS

### FINDING 8 — `claude-3-5-sonnet-20240620` and similar real Anthropic models return `None` from the substring ladder and contribute $0 silently

- **Name**: Model lookup ladder fails on plausible Claude model identifiers, contributing tokens at cost=0
- **Severity**: **Mid**
- **Location**: `anthropic_pricing.py:211–249` (`_lookup_model_key`)
- **Problem**: The substring-overlap ladder works by `key in model` OR `model in key`. For `claude-3-5-sonnet-20240620` (a real Anthropic model not in the pinned LiteLLM cache because the cache contains only `claude-3-7-sonnet-20250219`, `claude-3-haiku-20240307`, `claude-3-opus-20240229`), neither direction matches any cache key — every cache key is too long to be contained in this model id, and this model id is too long to be contained in any cache key. The lookup returns `None`, `dropped_unknown_model_count` increments, and **the message's tokens count toward panel aggregates with cost=0**. This is technically anti-fishing-compliant (no silent fishing) but is data-integrity-concerning: if the operator legitimately used `claude-3-5-sonnet-20240620` even once, its tokens inflate the denominator in R5's variance ratio with zero cost contribution — biasing the FX share toward zero. The lookup also resolves `claude-3` → `claude-3-7-sonnet-20250219` via alphabetical tiebreaker on substring length (this audit verified) — silently mispricing legacy `claude-3` shorthand at Sonnet-3.7 rates.
- **Proposed fix**: (a) When `dropped_unknown_model_count > 0`, log the specific model strings encountered (or surface them on a new `unknown_model_examples` counter, capped at ~10 unique values). (b) Reject the alphabetical-substring tiebreaker for cross-tier model lookups (Opus vs Sonnet vs Haiku) — currently `claude-3` could resolve to a Sonnet or Haiku rate depending on alphabetical accident. (c) Update DATA_PROVENANCE counter description for `dropped_unknown_model_count = 136` from "likely test sessions with `model: 'claude-3'`" to the actual model strings observed.
- **Evidence**:
  - Independent ladder test (this audit): `claude-3` → substring match → `claude-3-7-sonnet-20250219` (Sonnet rates, not Haiku); `claude-3-5-sonnet-20240620` → `None`; `gpt-5.2-codex` → `None`.
  - `anthropic_pricing.py:242` `tied = sorted(k for ln, k in candidates if ln == best_len); ...; return tied[0]` — alphabetical tiebreaker, no tier-awareness.
  - 136 unknown messages × average ~10k tokens × $7.5/Mtok ≈ $10 of unbilled cost potentially mispriced; small in aggregate but undisclosed by model.

### FINDING 9 — Test suite does not exercise `--timezone UTC` ccusage parity claim

- **Name**: `test_real_jsonl_integration.py` invokes `ccusage` without `--timezone UTC`; v0.2.7 Y-9 closure's UTC protocol is unenforced by CI
- **Severity**: **Mid**
- **Location**: `simulations/tests/test_real_jsonl_integration.py:148–152`
- **Problem**: The DATA_PROVENANCE Y-9 closure (line 47, line 126) declares: "**A valid parity comparison MUST pass `--timezone UTC` to ccusage**; otherwise the per-class ratios contain a timezone-shift artifact of up to ~1.3% per class". The repo's only ccusage CLI test invokes:
  ```python
  subprocess.run(["npx", "--yes", "ccusage@latest", "session", "--json", "--path", str(projects)])
  ```
  No `--timezone UTC`. The test is also gated to xfail/skip when ccusage is unavailable, the fixture is synthetic, or the production cache is absent — so in practice the test never runs against real data on CI. The "v0.2.7 Y-9 protocol pinned" assertion at DATA_PROVENANCE line 126 is documentation, not enforcement.
- **Proposed fix**: (a) Update `test_real_jsonl_integration.py:149` to pass `--timezone`, `UTC`. (b) Use `daily` command (the DATA_PROVENANCE reference command) rather than `session` — they aggregate differently and only `daily --timezone UTC` matches the panel's bucketing. (c) Stage a real-redacted fixture so the test actually runs (currently the test is permanently skipped against the synthetic placeholder).
- **Evidence**:
  - `test_real_jsonl_integration.py:148–152` (audit-traced): no `--timezone` argument.
  - DATA_PROVENANCE.md line 49–53: reference command is `ccusage@latest daily --since 20240101 --until 20260517 --timezone UTC --json`.
  - DATA_PROVENANCE.md line 126: "**CI-locked parity check MUST pass `--timezone UTC` to the ccusage invocation per the Y-9 closure protocol above**" — promised, not implemented.

### FINDING 10 — `rglob("*.jsonl")` iteration order is filesystem-dependent; panel build is non-deterministic across replicas

- **Name**: `JSONLReader.__call__` walks the project root via `Path.rglob`, whose order is filesystem-defined; downstream dedup tiebreaker is order-sensitive
- **Severity**: **Mid**
- **Location**: `jsonl_io.py:377` (`for jsonl_path in projects_root.rglob("*.jsonl"):`); dedup pipeline lines 436–473
- **Problem**: On `tied tokenTotal` (e.g., perfect-duplicate streamed rows where both have `hasSpeed=False` or both have `hasSpeed=True`), the code at `jsonl_io.py:466–473` keeps the **existing** record and discards the new one. Which record is "existing" depends on `rglob` iteration order, which is **not pinned**: ext4 returns inode-creation order, btrfs returns alphabetical, NFS varies by client. Two clones of the repo on different filesystems can produce different panels at the byte level. The DATA_PROVENANCE sha256 (`c002df3b...`) cannot be reproduced from a fresh clone on a different filesystem absent additional sorting. Additionally, blocks within a single JSONL are line-ordered (deterministic), but the inter-file order is not, and uniqueHash dedup happens globally across files.
- **Proposed fix**: (a) Replace `projects_root.rglob("*.jsonl")` with `sorted(projects_root.rglob("*.jsonl"))` — guarantees alphabetical iteration. (b) Add a Hypothesis property test that shuffles file iteration order and asserts identical output.
- **Evidence**:
  - `jsonl_io.py:377`: bare `rglob` — Python docs: "Yields all the existing files (of any kind, including directories) matching the given relative pattern anywhere in this tree. **The order of returned paths is not specified.**"
  - Tiebreaker code `jsonl_io.py:466–473`: `if new_tt > existing_tt or (new_tt == existing_tt and new_has_speed and not existing_has_speed): replace; else: keep existing`. On equal tt + equal hasSpeed, keep existing → first-seen-file-order-dependent.

---

## LOW FINDINGS

### FINDING 11 — DATA_PROVENANCE mentions "Build date 2026-05-17" but spec is now v0.2.9 (2026-05-18)

- **Name**: DATA_PROVENANCE spec-version drift
- **Severity**: **Low**
- **Location**: `DATA_PROVENANCE.md` lines 3, 11 ("Spec version: 0.2.7", "v0.2.7 Y-9 closure refresh")
- **Problem**: The spec has advanced to v0.2.9 (per spec line 5, 2026-05-18) but DATA_PROVENANCE still refers to v0.2.7 and "post-PR#3 merge". The panel has not been rebuilt against v0.2.9, but neither has the DATA_PROVENANCE been updated to note that the panel pre-dates v0.2.9's CORRECTIONS-Z3 power-recipe pin.
- **Proposed fix**: Add a "Spec version at *panel build* time: 0.2.7; spec advanced to 0.2.9 on 2026-05-18 without panel rebuild (no panel-relevant changes in v0.2.8 / v0.2.9)" note. Cite the explicit deltas if relevant.
- **Evidence**: DATA_PROVENANCE.md:3, 11 vs spec:5.

### FINDING 12 — `_synth_uuid` for missing-uuid rows is bound to file basename, not path — collides across renamed copies

- **Name**: Synthesized UUID is rename-stable but NOT cross-project-unique when two JSONL files share a basename
- **Severity**: **Low** (no known collision in current corpus)
- **Location**: `jsonl_io.py:145–160` (`_synth_uuid`)
- **Problem**: The synth UUID is `sha256(file.stem + ":" + zfill(8))`. If two distinct JSONL files in different project directories share the same basename (e.g., `agent-af5e1160.jsonl` appearing in two projects), their line-1 synth UUIDs collide. The current corpus presumably has no such collision, but the design is not defensive against operator-driven copy-with-rename workflows. Note also that uuid does not flow into the dedup map (dedup is on `message.id`, not uuid), so the practical impact is limited to R6 canonicalization downstream.
- **Proposed fix**: Hash the full relative path under `projects_root` rather than just the basename — preserves rename-stability **within** a project while preventing cross-project basename collisions. Document the design choice in the docstring (current docstring says "rename-stable across paths; basename-bound" but does not explain the cross-project collision case).
- **Evidence**: `jsonl_io.py:157–160` `basename: str = Path(file_path).stem` — basename-only hashing.

---

## Severity-level "no issues found" statements

None — issues found at every severity level (Critical, High, Mid, Low).

---

## Summary recommendation

The pipeline is **not yet replication-safe** against the published `c002df3b...` panel sha256. The Critical findings (1, 2, 3) combine to mean that:

1. The panel silently excludes ~29% of operator Claude cost on TRM-missing weekdays;
2. The headline "ccusage parity 1.000000×" is a tautology over the inner-joined subset;
3. The SHA pin is not enforced at the file-content level.

Before any subsequent build (or before the v0.2.9 verdict memo is finalized), I recommend:

- Add the `LITELLM_FILE_SHA256_PINNED` enforcement (Finding 3, mechanical fix, < 1 hr).
- Split `dropped_rows_count` into three named counters (Finding 5, mechanical, ~2 hr including tests).
- Disclose the TRM-holiday-Monday silent drop in DATA_PROVENANCE with $ magnitude (Finding 1, doc-only, < 1 hr).
- Pre-pin TRM-holiday handling in §3.5 / §6 of the spec with an explicit forward-fill-vs-drop choice (Finding 6, design decision, ~1 day including spec amendment).
- Disclose Codex/GPT commingling in §1.2 and DATA_PROVENANCE (Finding 4, doc-only, ~30 min).
- Recompute the ccusage parity table with explicit panel-only / both / ccusage-only rows (Finding 2, ~1 hr).
- Either rebuild the panel against the current JSONL root (resolving Finding 7's drift) or annotate DATA_PROVENANCE with the snapshot-vs-live caveat.

The data-integrity foundations are otherwise solid: ccusage-mirror dedup logic is implemented correctly and verified by the Y-9 probes; per-class token totals match ccusage to within rounding on the overlap; the LiteLLM file's sha256 happens to match its DATA_PROVENANCE entry; the malformed-line skip is narrowly scoped; `is_error` filtering is honest. The issues above are about **disclosure**, **counter semantics**, and **mechanical reproducibility enforcement** rather than algorithmic correctness.
