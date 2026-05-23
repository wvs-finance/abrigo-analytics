# Dependency Propagation Map — AI-Cost Delphi (12 Critical+High findings)

- **Date**: 2026-05-18
- **Source audits**: `scratch/2026-05-18-ai-cost-delphi/agent{1,2,3}_*.md`
- **Spec target**: `docs/specs/2026-05-16-ai-cost-factor-model-design.md` v0.2.9
- **Panel sha256 baseline**: `c002df3b42042bf7db37499482486d1548a72f45bea8ff58d14569fb72d6b6ff`
- **Purpose**: route fix agents and verification agents so that every consumer
  of a changed artifact is updated coherently. Captures cross-finding
  interactions and re-emission cascades.

Legend for **Form-sensitive derivations** column:
- A derivation is *form-sensitive* if its expression assumes a specific
  functional form / counter shape / dataclass attribute name of the affected
  object. Changing the form (e.g., splitting one counter into three) requires
  rewriting every dependent expression — not just re-running.

CASCADE keys:
- `CASCADE-PANEL` = re-emit `notional_cost_panel.parquet` → re-run notebooks
  01-06 → update `DATA_PROVENANCE.md` → update Task 17 verdict memo.
- `CASCADE-SPEC` = bump frontmatter `spec_version` + append `§12` revision
  history entry + add new `## 0.N` CORRECTIONS block.
- `CASCADE-COUNTERS` = update **both** dataclass (`types.py` / pricing) **and**
  threading in `panel_builder.py` / `jsonl_io.py` / CLI **and** tests **and**
  `DATA_PROVENANCE.md` counter table.

---

## Master propagation table

| # | Finding (short) | Affected object | Direct consumers | Indirect consumers | Cross-cuts (other findings) | Form-sensitive derivations |
|---|---|---|---|---|---|---|
| 1 | Silent panel drop on Colombian-holiday Mondays (11 weekday-UTC days; $821 / 29% post-filter cost; mis-labeled "weekend") | `simulations/dev_ai_cost_v2/panel_builder.py` L162, L178-192, L211-216 (inner join + `weekend_records` counter); `DailyNotionalPanel` schema in `types.py:269`; `DATA_PROVENANCE.md` counter table L91 | `scripts/build_notional_cost_panel.py` (calls `build_daily_notional_panel`); `simulations/tests/test_dev_ai_cost_v2_panel_builder.py` (asserts inner-join semantics + counter values); `data/panels/notional_cost_panel.parquet` (output artifact, sha256 `c002df3b...`); `DATA_PROVENANCE.md` §"Counter table" + §"Build window" | Notebooks 01-06 (all read the parquet → re-emit cascade); Task 17 verdict memo (N changes 28→36 if Mondays restored); spec §2.3 N-floor narrative; spec §3.5 build-window definition; spec §6 "weekends dropped on both sides — forward-fill forbidden" rule; `memory/project_dev_ai_section_j_fail.md` if precedent gets cited | #5 (N=28 was load-bearing for floor-relaxation justification — restored N may cross 38 and remove PARTIAL label); #6 (Z2 additive-identity check geometry is unchanged but identity-defense narrative changes); #10 (unit-mixing fix — splitting `dropped_rows_count` is prerequisite to publishing the Monday-drop counter); #11 (N-sensitivity is exactly this finding's downstream consequence); #12 (rebuild resolves counter drift) | If pipeline gains `trm_missing_weekday_message_count` + `trm_missing_weekday_day_count`, every reconciliation formula in `DATA_PROVENANCE` and notebooks that used `dropped_rows_count` as a single quantity must be re-derived as a SUM over the three new named counters. Spec §6 forward-fill clause must be split into "operator-weekend" (forbidden) vs "TRM-holiday" (NEW design choice). **CASCADE-PANEL + CASCADE-COUNTERS + CASCADE-SPEC.** |
| 2 | ccusage parity "1.000000×" tautological (inner-join geometry; 27 ccusage-only days excluded; true parity ≈ 0.70× over full window) | `scratch/2026-05-17-y9-investigation/compare_ratios.py` L35 (`how="inner"`); `DATA_PROVENANCE.md` §"ccusage parity verdict" L41-72, L126 | `simulations/tests/test_real_jsonl_integration.py` L148-152 (ccusage CLI invocation — missing `--timezone UTC`); spec §0.7 CORRECTIONS-Y-9 narrative L999-1083; spec L1955 revision-history entry for v0.2.7 | Task 17 verdict memo (cannot cite "parity satisfied" as evidence of pipeline correctness without three-row disclosure); R5 / R4-S3 verdict-eligibility reasoning in §2.1 §2.2 (R5 was unblocked by Y-9 closure); `memory/project_ai_cost_v0_2_3_state.md` if cited | #1 (the 27 ccusage-only days INCLUDE the 11 Monday Claude-active days + 5 Codex/GPT days — restoring #1 + #9 reduces the gap and **changes the parity table numbers**); #9 (Codex commingling is the source of 5 of the 27 ccusage-only days); #12 (counter drift suggests panel pre-dates the probe → parity geometry already stale) | Parity ratio is a function of the JOIN GEOMETRY. Switching from `how="inner"` → three-row disclosure (`ours-only` / `both` / `ccu-only`) changes the SHAPE of the parity claim. Every memo/notebook cell that quotes "1.000000×" must be rewritten as a tuple `(both=29 days @ 1.0000×, ccu-only=27 days, ours-only=0)`. The 0.1% target itself (CORRECTIONS-Y-4) must be re-scoped: applies only to the "both" subset; needs a separate denominator-coverage threshold for "ccu-only". **CASCADE-SPEC + DATA_PROVENANCE rewrite.** |
| 3 | LiteLLM SHA pin not mechanically enforced (string equality on caller-supplied SHA; never hashes file bytes) | `simulations/dev_ai_cost_v2/anthropic_pricing.py:168-174` (`from_litellm_sha` body); `LITELLM_SHA_PINNED` constant L141; `scripts/build_notional_cost_panel.py:112-114` (caller-supplied SHA); `simulations/tests/test_dev_ai_cost_v2_pricing.py:181-184` (existing test only exercises string-equality path) | `data/raw/litellm_model_prices.json` (the file whose sha256 must now be pinned); `DATA_PROVENANCE.md` §"LiteLLM pin" L62 (cites file sha256 `05b050523e...` but no code enforces it) | spec §5 reproducibility pins L1765; spec §11 cited-files table; any CI / Makefile target that builds the panel; future re-builds (Finding 7 rebuild) will exercise the new check | #1 / #9 / #10 (any pipeline fix that re-emits the panel must run after the SHA-pin enforcement lands so the new panel sha256 publishes against a verified rate-card); #12 (resolving counter drift requires panel rebuild → must occur after #3) | A fix that adds `LITELLM_FILE_SHA256_PINNED` + `hashlib.sha256(raw).hexdigest()` comparison creates a NEW form: callers now pass both pins. Every test fixture / spec citation that references "the SHA pin" (singular) must be rewritten to reference "commit-SHA pin (upstream lineage) + file-SHA256 pin (local cache integrity)". Requires new test fixture: a deliberately-corrupted JSON file to verify the file-SHA check raises. **CASCADE-SPEC (§5 + §0.N new) + new test fixture.** |
| 4 | Convergent-evidence claim circular (R5 / Z-arms / R4-S3-COP all reduce to `Var(Δln TRM)/Var(Δln Cost^COP)`; only R4-S3-USD independent) | Spec §0.8 L1084-1186 (Z2 reclassification); spec §0.9 L1285-1290 (4-measurement bullet); spec §0.6 v0.2.6 narrative; notebook 02 cell 17 (R5 Trio 6 cross-check); notebook 03 cell 16 (R4-S3-COP interp); notebook 06 (Z-arms) | Task 17 verdict memo (cannot claim "convergent evidence" without rewording to "one measurement + one behavioral test"); spec §12 revision history (need new entry); spec §0.1 CORRECTIONS-R (R5 Role A — its standalone authority increases when Z-arms are deconfounded) | `memory/project_ai_cost_v0_2_3_state.md` if cited as iteration narrative | #6 (Z2 additive-identity reclassification is part of the circular chain — fix #4 may remove the Z2 narrative entirely); #7 (R4-S3-COP corroboration is the third leg of the circular chain — fix #4 removes it from the "convergent" list); #8 (Z3 power-recipe pin is upstream of which R4-S3-USD recipe gates the verdict, which is the ONLY independent measurement remaining) | The "FOUR independent measurements" claim is form-sensitive: it asserts a particular cardinality. Reducing to "ONE measurement + ONE behavioral test" requires rewriting (a) §0.8 closing bullets, (b) §0.9 §closing summary, (c) §0.6 Z-arms framing in v0.2.6, (d) every notebook's interpretation cell that cites "convergent". The headline verdict label may need to change from "PARTIAL-FAIL_TO_REJECT (corroborated by Z2/R4-S3-COP)" to "PARTIAL-FAIL_TO_REJECT (single behavioral test, sub-floor power)". **CASCADE-SPEC (multiple section edits) + notebook re-emission of interpretation cells only (no parquet re-emit needed).** |
| 5 | Pre-data floor relaxation hidden in CORRECTIONS-G/J (N_MIN 75→38 AND POWER_MIN 0.80→0.50 simultaneously) | Spec §0 CORRECTIONS-G L109-117; CORRECTIONS-J (via CORRECTIONS-U L221-229); §2.3 L1526-1540; §7 anti-fishing invariants L1842-1847; §2.2.B verdict-logic table L1492-1524 | Notebook 01 Trio 5 power-HALT logic (POWER_MIN gate); notebook 04 verdict-bearing power gate; Task 11 in plan; Task 17 verdict memo (labels PARTIAL-FAIL_TO_REJECT depend on floors); spec §2.2.B verdict labels | `CLAUDE.md` anti-fishing invariant statement; `memory/feedback_pathological_halt_anti_fishing_checkpoint.md` (precedent Rev-5.3.1); `memory/project_dev_ai_section_j_fail.md` (prior iteration's floor-handling precedent) | #1 (restoring Mondays raises N to ~36 — closer to 38 floor but still sub-75; affects whether the "demonstration-grade" framing survives); #4 (if convergent-evidence is rewritten to a single behavioral test, the floor relaxation becomes load-bearing alone, not corroborated); #8 (Z3 reversion to lagged recipe pushes power = 0.17 < both 0.50 AND 0.80 — under either floor the verdict becomes POWER-HALT); #10 (PARTIAL-* label is contingent on 38 floor being canonical) | The floor pair (N_MIN, POWER_MIN) is form-sensitive: the verdict-logic in §2.2.B is a function `verdict(N, power) = PARTIAL if N≥38 ∧ power≥0.50 else HALT`. Restoring to (75, 0.80) re-shapes the function and changes the verdict at the current (N=28, power=0.71): becomes HALT, not PARTIAL. Alternative — adding the Rev-5.3.1-style preserved-power-floor proof at N=38 — requires NEW spec text computing `required_power(N=38, MDES=0.40, ...)` and matching it ≥0.80. **CASCADE-SPEC (§0 + §2.3 + §7 + §2.2.B verdict table) → notebook 04 re-runs ONLY if floor changes (numbers don't change but PASS/HALT label may).** |
| 6 | §0.8 Z2 identity check holds by construction (`max\|Δln cost^COP − Δln cost^USD − Δln USDCOP\| < 1e-12` is FP-precision tautology, not a test) | Spec §0.8 CORRECTIONS-Z2 L1084-1186 (full block); notebook 03 cell 15 (`identity_max_error = 1.78e-15`); spec §0.8 L1175 ("STRICTER than HAC-OLS" claim) | Task 13 R4-S3-COP CONSISTENCY-FAIL interpretation; notebook 03 Trio 4 interpretation cell; Task 17 verdict memo §"Z2 framing"; spec §0.6 (v0.2.6 closure references Z2 as a pin) | spec §12 revision history v0.2.8 entry | #4 (Z2 is a circular-evidence leg; #4 fix may simply remove Z2 from the convergent list); #1 (additive identity GEOMETRY is panel-arithmetic — re-emitting the panel after #1 fix changes neither the identity nor the variance-ratio numbers); #7 (Z2 and R4-S3-COP corroboration are paired; fixing #6 implies fixing #7) | The "STRICTER" claim is form-sensitive: it presumes the FP-identity check tests the SAME pipeline-integrity property as HAC-OLS. Reframing to "the regression arm is UNINFORMATIVE in low-FX-vol regime; the additive identity is a separate sanity check on parquet bytes" requires rewriting §0.8 to drop the "stricter" comparison and to recharacterize Z2 as a panel-construction-only assertion. **CASCADE-SPEC (§0.8 rewrite, §0.6 reference update, §12 entry).** |
| 7 | R4-S3-COP cannot corroborate (zero-power test failing to reject is zero evidence) | Spec §0.8 L1107-1116 (corroboration claim); spec §0.9 L1285-1290 (convergent list); notebook 03 cell 16 interpretation; verdict label "CONSISTENCY-FAIL → supports R5" | Task 17 verdict memo §"corroboration narrative"; spec §2.2.A verdict semantics (does CONSISTENCY-FAIL still get a special verdict-label?); spec §11 cited-files row for notebook 03 | spec §12 revision history | #4 (R4-S3-COP is one leg of the circular-evidence chain — #4 fix may remove R4-S3-COP from the corroboration list, making #7 a sub-fix of #4); #6 (Z2 reclassification was authored to PAIR with R4-S3-COP corroboration — both must change together) | The "supports R5 PRIMARY" framing is form-sensitive: it asserts the negative-result is evidence-positive. Rewriting to "R4-S3-COP is uninformative in this regime; drop from corroboration list" changes verdict-label semantics and removes a line from §0.8 / §0.9. **CASCADE-SPEC (§0.8 + §0.9 + notebook 03 interp cell only — no parquet re-emit).** |
| 8 | §0.9 Z3 pin canonicalizes the passing recipe (contemporaneous power 0.71 over lagged 0.17; pin authored AFTER POWER-HALT fired on lagged) | Spec §0.9 CORRECTIONS-Z3 L1188-1292 (full block); notebook 04 Trio 4 Recipe A (lagged) + Recipe B (contemporaneous); notebook 01 cell 14 (R²=0.5515 contemp) | Task 14 verdict; Task 17 verdict memo §"R4-S3-USD power"; spec §2.2.B verdict-logic gate (`power ≥ 0.50`); spec §11 cited-files for notebook 01 + 04; agent3 M1 finding (lagged-recipe MC slope-units inconsistency) | spec §12 revision history v0.2.9 entry; `memory/feedback_pathological_halt_anti_fishing_checkpoint.md` (HALT routing precedent) | #4 (if Z3 reverts to lagged, R4-S3-USD becomes POWER-HALT — leaving ZERO independent measurements after #4 strips the circular-evidence claim); #5 (floor relaxation interacts: under POWER_MIN=0.80, even contemporaneous 0.71 < 0.80 → HALT; under 0.50, contemp passes but lagged fails); #11 (different N from #1 fix changes residual-SD → changes BOTH recipes' power numbers); agent3-M1 (lagged-recipe MC slope is unit-mismatched — fix M1 may change the 0.17 number itself) | The recipe-pin choice is form-sensitive: it asserts which residual-SD enters the power-MC injection scaling. Reverting to lagged requires (a) §0.9 rewrite, (b) `power_halt_template.md` disposition fill, (c) Task 14 re-run with lagged-recipe canonical (notebook 04 only, no parquet re-emit needed unless #1 lands first), (d) Task 17 verdict label changes to POWER-HALT or PARTIAL-FAIL_TO_REJECT-low-power. **CASCADE-SPEC + notebook 04 + dispositions/.** |
| 9 | Codex/GPT cross-contamination undisclosed (operator's `~/.claude/projects/` contains both Claude Code AND OpenAI Codex sessions; 5 days × $4.78 silently filtered) | `simulations/dev_ai_cost_v2/anthropic_pricing.py:180` (`if not model.startswith("claude-"): continue`); `JSONLReader` admission (admits all assistant rows regardless of model); `dropped_unknown_model_count` counter on `PricingTable`; `DATA_PROVENANCE.md` L91 (counter description mis-attributes cause) | `simulations/tests/test_dev_ai_cost_v2_pricing.py` (lookup-ladder tests); `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` (admission tests); panel parquet (Codex tokens currently inflate `input_tok` / `output_tok` aggregates with cost=0); spec §1.2 proxy-framing narrative L1294+ | Task 17 verdict memo §"proxy framing scope"; notebook 02 R5 variance ratio (denominator includes Codex tokens silently — small but non-zero bias toward FX-share=0); notebook 01 EDA (token totals); spec §0.5 closure invariant (line-conservation must split by vendor) | #1 (3 of the 11 dropped Mondays are Codex-only — fix #1 + #9 jointly clarify the breakdown); #2 (5 of the 27 ccusage-only days are Codex — parity table must separate Claude-only vs Codex-only); #10 (counter split: `dropped_non_anthropic_model_count` vs `dropped_unknown_anthropic_model_count` is a sub-case of the unit-mixing fix); #12 (counter drift partially explained by Codex usage in the operator's daily workflow) | Splitting `dropped_unknown_model_count` is form-sensitive: every reconciliation formula in `DATA_PROVENANCE` summing the old counter must use `dropped_non_anthropic_model_count + dropped_unknown_anthropic_model_count`. The R5 denominator (`Var(Δln Cost^COP)` where Cost^COP includes Codex tokens at $0) is invalidated if Codex tokens are excluded from the token aggregates as well — either (a) filter Codex at JSONLReader admission (excludes their tokens entirely; cleaner) or (b) filter at PricingTable but zero-out tokens too. Choice (a) requires a NEW JSONLReader filter and re-emission. **CASCADE-PANEL + CASCADE-COUNTERS + CASCADE-SPEC (§1.2 + §0.5).** |
| 10 | Unit-mixing in `dropped_rows_count` (sums messages + TRM-rows + days into one counter) | `simulations/dev_ai_cost_v2/panel_builder.py:162` (`weekend_records` msg-level); L188 (`weekend_trm` row-level); L211 (`join_loss_left` day-level); L212 (the mixed sum); `DailyNotionalPanel.dropped_rows_count` field in `types.py`; `DATA_PROVENANCE.md` L91 counter table | `simulations/tests/test_dev_ai_cost_v2_panel_builder.py` (assertions on `dropped_rows_count`); `scripts/build_notional_cost_panel.py` (logs counter); notebook 01 EDA cells that quote the counter; spec §3.5 closure invariant | spec §0.5 line-conservation invariant; spec §11 cited-files counter table; Task 17 verdict memo §"data composition" | #1 (the new `trm_missing_weekday_day_count` is EXACTLY the day-level slice of `join_loss_left` — #10 fix is the structural prerequisite for #1's surfacing); #9 (vendor split in pricing-table counters is the parallel fix on the other dataclass); #12 (resolving #10 requires panel rebuild which also resolves counter drift) | The counter is form-sensitive: any test or doc that compares `dropped_rows_count == X` against an integer is broken when split into three named counters. Tests must be rewritten to assert `weekend_message_count + weekend_trm_row_count + trm_missing_weekday_day_count == old_total` initially (regression-safety), then assert each named counter individually. Hypothesis property test must be added: sum-equals-total invariant. **CASCADE-PANEL + CASCADE-COUNTERS.** Per Y-5a, the JSONL-sourced counters live on `JSONLReadResult` (types.py); panel-sourced live on `DailyNotionalPanel` (types.py). New counters here belong to `DailyNotionalPanel`. |
| 11 | N=28 sensitive to TRM filter (restoring 8 Claude-active Mondays would push N from 28→36) | Panel rows (29 → ~37 if Mondays restored); first-diff N (28 → 36); `simulations/dev_ai_cost_v2/panel_builder.py` inner-join semantics; spec §6 forward-fill rule | Notebooks 01-06 every regression / variance calc (all read panel); spec §2.2.B verdict label (PARTIAL → potentially PASS or POWER-HALT depending on power recomputation); spec §2.3 N-floor narrative; Task 17 verdict memo headline N | Task 11 power-MC (residual-SD changes with new observations → power numbers shift); Task 12 R5 variance ratio (more observations → tighter CI); Task 14 R4-S3-USD regression (lag-1 alignment recomputed); Z-arms in notebook 06 | #1 (this finding IS the downstream consequence of #1 — they should be jointly resolved); #5 (N change interacts with floor — N=36 is still <38 floor; N=36 vs 28 changes power but not the floor verdict at 38); #8 (recipe-pin power numbers recompute with new N — could move 0.71 in either direction); #4 (more data may strengthen or weaken R4-S3-USD as the sole independent test) | The reported N is form-sensitive: it asserts a specific filter geometry (inner-join on TRM-as-is). Every notebook cell that pre-pins T=28 (e.g., HAC bandwidth `floor(T^(1/3))=3` at T=28 → still 3 at T=37; bootstrap block_len=4 unchanged at expected `T^(1/3)≈3.3`) must be re-checked. Some formulas are robust; the verdict label is not. **All numbers in notebooks 01-06 + Task 17 memo must be re-emitted.** This is the most expensive cascade. **CASCADE-PANEL** (joint with #1). |
| 12 | Counter drift between DATA_PROVENANCE and current probe (gaps: 568 non-assistant / 1 duplicate / 1 error) | `DATA_PROVENANCE.md` L91-94 counter values (snapshot at build T0); `scratch/2026-05-17-y9-investigation/probe_output.txt` (live values at T1>T0); JSONL root (continues to grow as operator works) | All notebooks (read parquet built at T0); spec §0.5 closure invariant assertions; Task 17 verdict memo "build window" claim; ccusage parity table (Finding 2 — parity geometry assumes panel and probe are coeval) | spec §3.5 build-window definition; `memory/project_ai_cost_v0_2_3_state.md` if cited as a snapshot reference | #1 / #9 / #10 (a rebuild that lands #1+#9+#10 fixes simultaneously resolves the drift on a single consistent snapshot); #2 (parity geometry is invalidated by drift — fixing #12 by rebuild resolves part of #2 too); #3 (rebuild must occur AFTER file-SHA pin enforcement lands) | Drift is form-sensitive on the "raw line denominator" used in the malformed-rate calculation: `1 / 134,514 = 7.4e-6` vs `1 / 222,909 = 4.5e-6`. The baseline rate is published in DATA_PROVENANCE L124 and cited in spec §0.4 CORRECTIONS — must be recomputed against the correct denominator regardless of rebuild. Adding a `raw_jsonl_line_count` counter on `JSONLReadResult` is a counter-split (Y-5a-compliant). **CASCADE-COUNTERS + (option A) CASCADE-PANEL via rebuild OR (option B) snapshot annotation only.** |

---

## Cross-cut interaction matrix

| Finding | Cuts INTO | Cuts FROM |
|---|---|---|
| #1 | #5, #11, #12 (data inputs to all three) | #10 (must split counter first to expose it) |
| #2 | #4 (parity claim feeds convergent-evidence narrative) | #1, #9 (the missing days that distort the parity geometry) |
| #3 | #12 (any rebuild requires pin enforcement) | (independent — pure pipeline integrity) |
| #4 | Task 17 verdict memo headline | #6, #7, #8 (the three circular legs being deconfounded) |
| #5 | #11 verdict label, Task 17 | #1 (N might cross 38 under fix) |
| #6 | #4 (Z2 is one leg) | #1 (panel arithmetic is unchanged but narrative changes) |
| #7 | #4 (R4-S3-COP is one leg) | (independent of pipeline fixes) |
| #8 | #4 (R4-S3-USD recipe is the SOLE remaining measurement post-#4) | #1, #11 (residual-SD changes with N) |
| #9 | #2 parity geometry, #10 counter split, R5 denominator bias | (independent pipeline finding; admission filter) |
| #10 | #1 (Monday counter surfacing requires split first), #9 (vendor split is sibling) | (structural prerequisite for #1, #9) |
| #11 | Every notebook + Task 17 | #1 (this is #1's downstream consequence) |
| #12 | #2 parity, Task 17 build-window claim | #1, #9, #10 (rebuild resolves) |

---

## Execution-order DAG (topological)

```
                                  Wave 0 — independent spec amendments
                                  (no pipeline / no notebook impact yet)
                                  ────────────────────────────────────
                                  #4 spec §0.8 + §0.9 + §0.6 rewrite (convergent-evidence)
                                  #6 spec §0.8 Z2 reframing (uninformative-arm)
                                  #7 spec §0.8 + §0.9 R4-S3-COP drop from corroboration
                                  #5 spec §0 CORRECTIONS-G/J + §2.3 + §7 + §2.2.B floor decision
                                  #8 spec §0.9 Z3 recipe decision
                                              │
                                              ▼
                                  Wave 1 — pipeline fixes (counter / admission / SHA)
                                  ────────────────────────────────────────────────────
                                  #3 file-SHA enforcement   (anthropic_pricing.py, test fixture)
                                  #10 counter split          (panel_builder.py, types.py, tests)
                                  #9 Codex filter            (jsonl_io.py admission + pricing split)
                                  #1 Monday-drop counter     (panel_builder.py — depends on #10)
                                              │
                                              ▼
                                  Wave 2 — re-emit panel parquet
                                  ──────────────────────────────
                                  scripts/build_notional_cost_panel.py
                                  → new sha256 (replaces c002df3b...)
                                  → resolves #12 drift on a fresh snapshot
                                  → resolves #2 parity geometry inputs
                                              │
                                              ▼
                                  Wave 3 — re-run all notebooks
                                  ─────────────────────────────
                                  01_data_eda      → new N, new power numbers
                                  02_r5_descriptive → new variance ratio (very small change expected)
                                  03_r4s3_cop      → new HAC numbers
                                  04_r4s3_usd      → new HAC + power-MC (#11 cascade; #8 recipe decision lands here)
                                  05_sensitivity   → all four diagnostic arms
                                  06_z_sensitivity → Z-arm numbers
                                              │
                                              ▼
                                  Wave 4 — update DATA_PROVENANCE.md
                                  ──────────────────────────────────
                                  - 3-row ccusage parity table (#2)
                                  - new counter values (#1, #9, #10, #12)
                                  - LiteLLM dual-pin disclosure (#3)
                                  - Codex commingling disclosure (#9)
                                  - spec_version 0.2.7 → 0.2.10 (or whatever Wave 0 sets)
                                              │
                                              ▼
                                  Wave 5 — Task 17 verdict memo
                                  ─────────────────────────────
                                  Consumes ALL above. Headline label may change from
                                  PARTIAL-FAIL_TO_REJECT to POWER-HALT (#5 + #8) or to
                                  "single behavioral test, sub-floor" (#4).
                                  Updates §12 revision history of the spec.
```

**Critical-path constraints:**
1. Wave 0 spec amendments are independent and can land in parallel (no code).
2. Wave 1 pipeline fixes order: **#10 BEFORE #1** (counter split is structural
   prerequisite for surfacing the Monday-drop counter). **#3 BEFORE Wave 2
   rebuild** (the new panel must publish against a verified rate-card pin).
3. Wave 2 (re-emit) MUST happen after Wave 1 lands all four pipeline fixes —
   running it mid-way wastes a rebuild cycle.
4. Wave 3 notebook re-runs are gated on Wave 2; cannot be partial.
5. Wave 4 DATA_PROVENANCE rewrite consumes Waves 2+3 outputs; cannot anticipate.
6. Wave 5 verdict memo is the final consumer; the verdict label depends on the
   Wave-0 spec decisions interacting with Wave-3 numbers.

**Anti-fishing constraint:** Wave 0 spec decisions (especially #5 floor and
#8 recipe-pin) MUST be made BEFORE seeing Wave 3 numbers. If the post-rebuild
N (#11) is e.g. 36 and the operator is tempted to re-relax the floor to 36,
that is silent fishing. Pre-pin the floor decision in Wave 0; let Wave 3
return whatever it returns.

---

## 5-line cascade-priority summary

1. **Wave 0** (parallel, spec-only): land #4, #5, #6, #7, #8 amendments BEFORE any rebuild — anti-fishing requires pre-pinning floors/recipes before new numbers land.
2. **Wave 1** (pipeline): #10 counter-split → #1 Monday surfacing; #9 Codex filter; #3 file-SHA enforcement. Tests for each.
3. **Wave 2**: re-emit `notional_cost_panel.parquet` once — new sha256 replaces `c002df3b...`; resolves #12 drift.
4. **Wave 3**: re-run notebooks 01-06; #11 N-change propagates through every power/variance number.
5. **Waves 4-5**: rewrite DATA_PROVENANCE (3-row parity table, new counters, dual pin); Task 17 verdict memo absorbs everything — headline label may change.
