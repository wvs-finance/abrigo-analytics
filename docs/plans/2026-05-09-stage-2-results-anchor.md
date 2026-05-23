# STAGE_2_RESULTS Anchor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Code-agnostic plan.** Per repo memory `feedback_no_code_in_specs_or_plans` (NON-NEGOTIABLE), this plan does NOT contain code blocks. The deliverable is a Markdown notes file authored by a Technical Writer agent.
>
> **Foreground orchestrates, never authors.** Per repo memory `feedback_specialized_agents_per_task` (NON-NEGOTIABLE). This plan's author also does NOT author the deliverable.

**Plan version:** v0.3 (FORMAT-PATTERN RESET; v0.2 §1.2 + §1.3 backbones produced citation registry instead of math anchor — see §"CORRECTIONS-α v0.2 → v0.3" at end)
**Status:** READY-FOR-REVERIFY
**Emit timestamp:** 2026-05-08

**Goal:** Author `notes/STAGE_2_RESULTS.md` — the math-results anchor that captures the Stage-2 frozen state of the SaaS-builder iteration as a continuation of the predecessor lineage `PRIMITIVES.md` → `SaaS_Builders_AI_NativeBuilders.md`. Format and tone MUST mirror those predecessors: math-flowing LaTeX-equation style, §-numbered, R-tagged equations, boxed key results, terse prose. This is a math reference, NOT a citation registry.

**Architecture:** Pure SaaS_Builders pattern + R-tagged equations. Lineage marker at top. §-numbered headers. LaTeX equations with R-prefix tags (R1, R2, ...). Tables comparing pre-cycle hypothesis vs post-cycle pinned form. Boxed key results. Closes the four TODO-COHORT-N labels from SaaS_Builders notes with cohort-calibration outcomes. Stage-3 open items in math form. NO file:line, NO pytest names, NO sha256 inline (only §6 reproducibility carries hashes compactly).

**Tech stack:** Markdown only. No code. Verification re-runs sha256 on a small inventory + checks math derivations against PRIMITIVES.md / spec / cohort plans.

**Predecessor chain:** `notes/PRIMITIVES.md` → `notes/SaaS_Builders_AI_NativeBuilders.md` → **`notes/STAGE_2_RESULTS.md`** (this deliverable). Stage-3 will produce `notes/STAGE_3_RESULTS.md` following the same pattern.

**Stage-2 freeze pin:** HEAD `9fd92e5` ("deliverable(saas-cohort): Stage-2 modeling memo + Phase-4 schema-bump audit") — confirm at Phase 0 via `git merge-base --is-ancestor 9fd92e5 HEAD` (true) AND `git diff 9fd92e5 HEAD -- simulations/ docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (empty). The verdict-memo commit `9fd92e5` is the canonical Stage-2 freeze marker; the upstream CORRECTIONS-α v0.4 marginalization closure is at `80f4ed4` (an ancestor of `9fd92e5`).

**Out of scope:** introducing any new claim not already in spec / PRIMITIVES / cohort plans / code; magnitude promises about real-data scale-up; Stage-3 implementation work; case-study narrative (lives in `feedback_post_hoc_fit_anti_fishing_pattern.md`); inline citation registries.

---

## Strategic delegation map

| Phase | Owner | Mode |
|---|---|---|
| 0 — Pre-flight | foreground (this plan author) | inline verify |
| 1 — Structure pin | foreground | inline (this plan locks structure) |
| 2 — Implementation | `Technical Writer` | single-agent dispatch |
| 3 — Re-verify | `Reality Checker` + `Model QA Specialist` | 2-wave parallel |
| 4 — Commit + push | foreground | inline |

---

## File structure

Single file deliverable:

```
notes/
└── STAGE_2_RESULTS.md   (to be created by Technical Writer in Phase 2 — full rewrite from scratch; v1.1 discarded)
```

No code, no tests, no fixtures. The file is a math anchor in the predecessor lineage; verification is by checking format inheritance + math derivation correctness in Phase 3.

---

## Phase 0 — Pre-flight

### Task 0.1 — Confirm Stage-2 freeze pin
- [ ] **Step 1** — Verify freeze-pin is in our history AND no Stage-2 substantive code/spec changed since:
  - `git merge-base --is-ancestor 9fd92e5 HEAD` MUST exit 0 (freeze pin is an ancestor of current HEAD).
  - `git diff 9fd92e5 HEAD -- simulations/ docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` MUST be empty (no Stage-2 substantive code or spec drift since the freeze).
  - Cosmetic post-freeze commits outside those paths (memory hygiene, README updates) are PERMITTED.
  - If either check fails → HALT and surface to user.
- [ ] **Step 2** — Run `git status --short`. Expect no modified files in `notes/`, `simulations/`, `docs/specs/`. Untracked acceptable.
- [ ] **Step 3** — Run `git branch --show-current`. Expect `iter/saas-builder-stage-2`.

### Task 0.2 — Verify source artifacts exist (HALT on missing)

Each item below MUST resolve. If any is missing, HALT and surface to user per `feedback_pathological_halt_anti_fishing_checkpoint`.

- [ ] **Step 1** — Predecessor notes (format authorities — Technical Writer reads these in full FIRST):
  - `notes/PRIMITIVES.md`
  - `notes/SaaS_Builders_AI_NativeBuilders.md`
- [ ] **Step 2** — Spec + verdict memo:
  - `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (v1.2.1 expected)
  - Stage-2 verdict memo: `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`
- [ ] **Step 3** — Cohort plans (5 files):
  - `docs/plans/2026-05-08-saas-cohort-1-t1-cost-posterior.md`
  - `docs/plans/2026-05-08-saas-cohort-2-t2-pricing-sign.md`
  - `docs/plans/2026-05-08-saas-cohort-3-revenue-form-loo.md`
  - `docs/plans/2026-05-08-saas-cohort-4-z-cap-derivation.md`
  - `docs/plans/2026-05-09-saas-cohort-close.md`
- [ ] **Step 4** — Two anchor JSON artifacts (sha256 cited compactly in §6):
  - `simulations/saas_builder/data/gate_verdict.json`
  - `simulations/saas_builder/data/Z_cap_pinned.json`

### Task 0.3 — Capture sha256 source-of-truth (compact; for §6 only)

The two sha256 anchors that STAGE_2_RESULTS.md §6 must cite (compactly — full sha for the two main hashes; tails only for any supplementary if cited):

- [ ] **Step 1** — `Z_cap_pinned.json::audit_block.sha256` — pre-pinned in user brief as `1fb1f7a4...5d31`. Verify via `python -c "import json; print(json.load(open('simulations/saas_builder/data/Z_cap_pinned.json'))['audit_block']['sha256'])"`. If divergent, HALT.
- [ ] **Step 2** — `gate_verdict.json::audit_block.sha256` — pre-pinned as `4da660b5...2173`. Verify analogously. If divergent, HALT.
- [ ] **Step 3** — Record both full sha256 values in worksheet `scratch/2026-05-09-stage-2-results-preflight/SHA256_INVENTORY.md`. Commit worksheet at end of Phase 0.

### Task 0.4 — Commit pre-flight worksheet

- [ ] **Step 1** — `git add scratch/2026-05-09-stage-2-results-preflight/`
- [ ] **Step 2** — `git commit -m "preflight(stage-2-results): sha256 anchor inventory + source artifact verification"`

---

## Phase 1 — Structure pin (foreground; locks the §-skeleton)

This phase produces no new files; it locks the structure that the Technical Writer brief in Phase 2 will require verbatim. The structure below mirrors the format authority of `notes/SaaS_Builders_AI_NativeBuilders.md` and is NON-NEGOTIABLE.

### Task 1.1 — Lock §-skeleton (math-anchor pattern)

The Technical Writer must produce `notes/STAGE_2_RESULTS.md` with exactly this structure, in this order. The pattern mirrors `notes/SaaS_Builders_AI_NativeBuilders.md` verbatim — lineage marker at top, §-numbered headers, math-flowing prose, LaTeX equations with R-prefix tags, boxed key results.

**Top of file:**
- Line 1: `**import [](./SaaS_Builders_AI_NativeBuilders.md)**` — lineage marker, exactly mirroring the SaaS_Builders notes' `**import [](./PRIMITIVES.md)**` pattern.
- Title: `# Stage-2 Results — Synthetic-Bayesian closure of the SaaS-builder cohort` (or equivalent terse title).
- One-paragraph notation reminder: this doc continues the SaaS_Builders cohort lineage. All math objects are specializations of numbered primitives in PRIMITIVES.md and S-tagged equations in SaaS_Builders notes. Equations introduced in this doc carry R-prefix tags (R1, R2, ...).

**§0 Cohort scope.** One paragraph carrying forward from SaaS_Builders notes. What changed at Stage-2: synthetic-Bayesian closure under the spec §5.2 24-cell parameter family at HEAD `9fd92e5`. NO real-data calibration; NO magnitude claims.

**§1 Empirical sign verdict.** One short paragraph + boxed result. References PRIMITIVES (10) + SaaS_Builders sign claim + spec §5.2.

> $$\boxed{\;\Delta^{(a_s)} \;<\; 0 \quad \text{across the spec §5.2 24-cell parameter family}\;}$$

Verdict source: gate_verdict.json (24/24 PASS primary). No file:line / no pytest name / no sha256 inline here; the sha256 lives in §6 only.

**§2 Closed forms that emerged (or were corrected) during the cycle.**

- **§2.1 — σ₀ anchor.** Closed-form derivation by inverting PRIMITIVES (8). Boxed result:

  > $$\sigma_0 \;=\; \frac{\overline{(X/Y)}^{2} \cdot \varepsilon^{2}}{8} \tag{R1}$$

  One-paragraph derivation referencing PRIMITIVES (8). No code citations.

- **§2.2 — π(t) closed form (perpetual streamed-premium variant).** Boxed result:

  > $$\pi(t) \;=\; \frac{K^\star \cdot \varepsilon^{2} \cdot \overline{(X/Y)}^{2} \cdot \big(4\omega t \cos(4\omega t) - \sin(4\omega t)\big)}{64 \cdot \omega \cdot \sqrt{\sigma_0} \cdot t^{2}} \tag{R2}$$

  Full derivation chain: PRIMITIVES (6) → (8) → (10) → §10 (Carr-Madan) → §15 open item 4 → R2. Document the v0.2 → v0.3 anti-fishing remediation as a one-paragraph aside (not a case-study format; the math is the record). Cite spec v1.2.1 + cohort-4 plan v0.3/v0.4 for the pinned form.

- **§2.3 — Perpetual identity.** Show that $\pi(t)\,dt \leftrightarrow d\Pi_{\text{lin}}/dt$ closes to sympy-exact zero (numerical residual ≈ 6.31e-9 carried as a one-line note, not a citation block).

  > $$\pi(t)\, dt \;=\; \frac{d\Pi_{\text{lin}}}{dt}\,dt \tag{R3}$$

- **§2.4 — Spec §5.2 24-bracket parameter family.** Express as a Cartesian-product set definition (NOT a list of pytest test names):

  > $$\mathcal{B}_{24} \;=\; \{\varepsilon\} \times \{\omega\} \times \{T\} \times \{\bar C\}, \quad |\mathcal{B}_{24}| = 24 \tag{R4}$$

  with the four index sets enumerated symbolically per spec §5.2.

- **§2.5 — C1 marginalization.** Analytic sum-out of `tier_idx + n_per_day + n_month` giving an identity at fixed parameters:

  > $$\sum_{\text{tier}_i, n_d, n_m} P(\bar C \mid \text{tier}_i, n_d, n_m) \cdot P(\text{tier}_i, n_d, n_m) \;=\; P(\bar C) \tag{R5}$$

  One-paragraph justification; no test name, no file:line.

**§3 TODO-COHORT-N closures (matches the four open labels in SaaS_Builders notes).**

This section is the CORE of the doc — it closes (or formally defers) each of the four TODO-COHORT-N labels left open in the predecessor SaaS_Builders notes.

- **§3.1 — TODO-COHORT-1** ($\bar C$ distribution). NOT closed at Stage-2: synthetic-Bayesian only; no DevSurvey real data. Deferred with rationale; flagged as Stage-3 hand-off (cross-link §5).
- **§3.2 — TODO-COHORT-2** (sticky-cost form). PINNED to softplus regularizer with M2 tightness ($L^1 < 10^{-3} \cdot \kappa$):

  > $$q_t^{\text{sticky}} \;=\; \beta^{-1}\log\big(1 + e^{\beta\,\bar c (X/Y)_t}\big), \quad L^1 < 10^{-3}\kappa \tag{R6}$$

- **§3.3 — TODO-COHORT-3** ($\Upsilon_t$ form). INDISTINGUISHABLE verdict per spec §9 / Pin R3 (LOO ELPD overlap). Spec v1.2.1 §6.1 pins det+churn form $S_t = (1-\lambda)^t$ with $\lambda \sim \text{Beta}(4.5, 95.5)$ for tractability:

  > $$S_t \;=\; (1-\lambda)^t, \quad \lambda \sim \text{Beta}(4.5, 95.5) \tag{R7}$$

  HALT-on-flip semantic preserved verbatim from spec.

- **§3.4 — TODO-COHORT-4** (π(t) under perpetual horizon). CLOSED at §2.2 / R2; cross-reference.

**§4 Z_cap pinned.** Closed form + magnitude table. Boxed result:

> $$\boxed{\;Z_{\text{cap}} \;=\; \mathbb{E}\!\left[\frac{q_t^{\text{det}}}{(X/Y)_t} + \pi(t)\right] \;}\tag{R8}$$

Magnitude table over the 5-test-point sign cert (synthetic; sign-only, NOT a magnitude prediction): Z = 4453–4922 COP/mo. One paragraph. No pytest name, no sha256 inline.

**§5 Stage-3 open items (math form, NOT engineering checklist).**

- Real-data conditioning of $\Upsilon_t$ and $q_t$ cohort distributions.
- Stochastic-FX variant per PRIMITIVES §15 (GBM, OU, jump-diffusion).
- Per-tier $\theta_k$ differentiation (resolves C1 MQ-FLAG-1 aggregation residual).
- Hierarchical pooling for C3 (resolves single-trajectory limitation).
- Weibull $k\neq 1$ falsification of $S_t$ form.
- On-chain Panoptic deployment (PRIMITIVES §11 discrete strip).

Each bullet is one short math-form sentence. NO magnitude promises. NO "real data will scale up" language.

**§6 Reproducibility.** ONE short paragraph. Freeze pin `9fd92e5`. The two anchor sha256 values cited compactly here and ONLY here:
- `Z_cap_pinned.json::audit_block.sha256 = 1fb1f7a4...5d31` (full sha in source-of-truth worksheet)
- `gate_verdict.json::audit_block.sha256 = 4da660b5...2173`

Verification command (one line, shell). NO inline citations elsewhere in the doc.

**§7 References (terse).** Bibliography-style, one line each:
- `notes/PRIMITIVES.md`
- `notes/SaaS_Builders_AI_NativeBuilders.md`
- `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` (v1.2.1)
- `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`

NO code paths. NO pytest names. NO audit verdict file paths inline. NO 31-file enumeration.

### Task 1.2 — Lock format-inheritance constraints (replaces v0.2 §1.2 + §1.3)

The Technical Writer brief MUST enforce the following format constraints, derived directly from inspection of `notes/PRIMITIVES.md` and `notes/SaaS_Builders_AI_NativeBuilders.md`:

1. **Lineage marker at top.** Line 1 MUST be `**import [](./SaaS_Builders_AI_NativeBuilders.md)**`. Mirrors SaaS_Builders' `**import [](./PRIMITIVES.md)**`.
2. **LaTeX equations with R-tags.** Every named equation introduced in this doc carries `\tag{R1}`, `\tag{R2}`, ... in incrementing order. Mirrors PRIMITIVES.md's numeric tags and SaaS_Builders' S-tags.
3. **Boxed key results.** Use `\boxed{...}` for headline results: σ₀ anchor, π(t) closed form, Z_cap pinned. Mirrors PRIMITIVES.md (8), (14), (17), (18) and SaaS_Builders (5').
4. **§-numbered headers.** Top-level sections numbered §0, §1, §2, ... matching SaaS_Builders header style.
5. **Math-flowing prose.** Sentences flow into and around equations. NO bullet-listed citation entries. NO 4-part cite blocks. NO claim/post-cycle-form/code-pointer/artifact-pointer tables.
6. **Tables comparing pre-cycle vs post-cycle pinned form** are PERMITTED for §3 (TODO-COHORT closures) — mirrors SaaS_Builders' "open cohort calibration TODOs" table at end. No `file:line` columns; no pytest columns; no sha256 columns.
7. **No inline file:line / pytest names / sha256.** The ONLY place sha256 appears is §6 (compact, two anchor values). The ONLY place git commits appear is §6. Code paths NEVER appear in the body.
8. **Tone.** PRIMITIVES.md tone: math-precise, brief, declarative. NOT narrative. NOT case-study. NOT citation-registry.

### Task 1.3 — Lock §3 TODO-COHORT closure semantics

Each §3.X subsection MUST state explicitly which of the four outcomes applies:
- **CLOSED** (TODO-COHORT-2, TODO-COHORT-4): pinned form + R-tagged equation.
- **DEFERRED** (TODO-COHORT-1): explicit Stage-3 hand-off rationale.
- **INDISTINGUISHABLE** (TODO-COHORT-3): LOO ELPD verdict + tractability-pin form + HALT-on-flip preservation.

NO case-study narrative. NO "pre-fix claim / pathology / detection heuristic / fix applied / evidence / lesson" 6-part format. The math IS the record.

### Task 1.4 — Lock §5 Stage-3 hand-off invariants (math form)

The §5 hand-off MUST be in math-bullet form, NOT engineering-checklist form. Each bullet is one sentence describing a math object Stage-3 must extend or condition. The §5 must NOT promise that "real data will scale up," "magnitudes will increase," or any equivalent. Anti-fishing.

### Task 1.5 — Verification matrix (format-inheritance focus)

Phase 3 RC + MQ verify two orthogonal axes:

| # | Axis | RC checks | MQ checks |
|---|---|---|---|
| 1 | Format inheritance (mirrors SaaS_Builders) | Lineage marker present; R-tags incrementing; boxed key results present; §-numbered; no inline file:line/pytest/sha256 except §6 | — |
| 2 | Math content | — | R1–R8 derivations math-correct; TODO-COHORT-N labels closed with cycle's actual outcomes (CLOSED/DEFERRED/INDISTINGUISHABLE per Task 1.3); §5 in math form not engineering form |
| 3 | Anti-fishing posture | No new claim outside spec/PRIMITIVES/SaaS-notes/cohort-plans at HEAD `9fd92e5`; no magnitude promise in §5 | Anti-fishing posture preserved (no relaxation of pins; HALT-on-flip preserved) |
| 4 | Reproducibility | §6 sha256 values match worksheet; freeze-pin `9fd92e5` correct | — |

### Task 1.6 — Commit Phase-1 structure-pin record

- [ ] **Step 1** — Append the Phase-1 locked skeleton (Tasks 1.1–1.5) to the worksheet `scratch/2026-05-09-stage-2-results-preflight/STRUCTURE_PIN.md`.
- [ ] **Step 2** — `git add scratch/2026-05-09-stage-2-results-preflight/STRUCTURE_PIN.md`
- [ ] **Step 3** — `git commit -m "structure-pin(stage-2-results): §-skeleton mirrors SaaS_Builders pattern; R-tagged equations; format-inheritance verification matrix"`

---

## Phase 2 — Implementation (Technical Writer dispatch)

### Task 2.1 — Author the Technical Writer brief

**Files:** Create: `scratch/2026-05-09-stage-2-results-preflight/TECHNICAL_WRITER_BRIEF.md`.

The brief MUST contain (foreground assembles; no agent dispatch yet):

- [ ] **Step 1** — **Read predecessors in full FIRST.** Brief opens with: "Before authoring, read `notes/PRIMITIVES.md` and `notes/SaaS_Builders_AI_NativeBuilders.md` in full. These are the format authorities. The deliverable must mirror their format verbatim: lineage marker, LaTeX equations with R-prefix tags, §-numbered headers, boxed key results, terse math-flowing prose."
- [ ] **Step 2** — **Discard v1.1 entirely.** Brief states explicitly: "The previous draft `notes/STAGE_2_RESULTS.md` v1.1 (commit `ae4ad9b`) is to be DISCARDED. Do NOT preserve any structure, headings, or content from it. Rewrite from scratch in the predecessor pattern. The 31 verdict files in `scratch/` already preserve the audit-trail material; the math anchor records the corrected math, nothing else."
- [ ] **Step 3** — Output path: `notes/STAGE_2_RESULTS.md`.
- [ ] **Step 4** — Required §-skeleton: copy Task 1.1 verbatim (lineage marker → §0 → §1 → §2.1–§2.5 → §3.1–§3.4 → §4 → §5 → §6 → §7).
- [ ] **Step 5** — Required format-inheritance constraints: copy Task 1.2 verbatim. Emphasize:
  - NO file:line / pytest names / sha256 inline (only §6 reproducibility carries sha256, compactly).
  - NO 4-part cite blocks. NO claim-registry tables.
  - NO case-study narrative format. The math is the record.
- [ ] **Step 6** — Required §3 TODO-COHORT closure semantics: copy Task 1.3 verbatim.
- [ ] **Step 7** — Required §5 hand-off invariants: copy Task 1.4 verbatim, with anti-magnitude-promise constraint emphasized.
- [ ] **Step 8** — sha256 source-of-truth (for §6 ONLY): cite the worksheet from Task 0.3 + the two anchor values (`1fb1f7a4...5d31`; `4da660b5...2173`). Brief states: any divergence → HALT.
- [ ] **Step 9** — Math depth requirement: full derivation of corrected π(t) chain from PRIMITIVES (6) → (8) → (10) → §10 → §15 open item 4 → R2 in §2.2. The σ₀ anchor (R1) derives by inversion of PRIMITIVES (8). The C1 marginalization (R5) is a one-paragraph analytic sum-out. M2 softplus tightness (R6) cites spec v1.2.1 M2 pin verbatim.
- [ ] **Step 10** — Anti-fishing constraint block (verbatim in brief): "STAGE_2_RESULTS.md cannot introduce any new claim not already in spec / PRIMITIVES.md / SaaS_Builders notes / cohort plans / code at HEAD `9fd92e5`. Anything resembling a new claim → HALT. The corrected math forms (π(t), σ₀, M2 amendment, det+churn $S_t$, Z_cap) are already pinned in spec v1.2.1 and cohort plans v0.3/v0.4 — this doc just expresses them in the predecessor's math-anchor format."
- [ ] **Step 11** — Tone constraint (verbatim in brief): "PRIMITIVES.md tone — math-precise, brief, declarative prose flowing around equations. NOT narrative-prose. NOT case-study. NOT citation-registry. Length budget: comparable to SaaS_Builders_AI_NativeBuilders.md (~210 lines), NOT to v1.1's 813 lines."
- [ ] **Step 12** — Commit the brief.
  - `git add scratch/2026-05-09-stage-2-results-preflight/TECHNICAL_WRITER_BRIEF.md`
  - `git commit -m "brief(stage-2-results): Technical Writer dispatch — predecessor-pattern format authority + R-tagged equations + math-anchor tone"`

### Task 2.2 — Dispatch Technical Writer

- [ ] **Step 1** — Foreground dispatches a single `Technical Writer` agent with the brief from Task 2.1 as its task description.
- [ ] **Step 2** — Wait for agent completion. Agent output: `notes/STAGE_2_RESULTS.md` (full rewrite from scratch).
- [ ] **Step 3** — Foreground sanity-check (NOT a re-verify; that is Phase 3): file exists, non-empty, line 1 is the lineage marker `**import [](./SaaS_Builders_AI_NativeBuilders.md)**`, top-level §0–§7 headers present in correct order, R1–R8 equation tags present, no inline `file:line`/pytest/sha256 patterns outside §6, no obvious placeholder strings (`TBD`, `TODO`, `FIXME`, `[fill in]`), length ≤ 350 lines (length sanity gate against citation-registry regression).
- [ ] **Step 4** — If sanity-check fails (especially the format-pattern regression checks): re-dispatch Technical Writer with sanity-check failure list. Do NOT foreground-edit the file.
- [ ] **Step 5** — On sanity-check pass, commit:
  - `git add notes/STAGE_2_RESULTS.md`
  - `git commit -m "feat(stage-2-results): notes/STAGE_2_RESULTS.md — math anchor in PRIMITIVES/SaaS_Builders lineage (PENDING-REVERIFY)"`

---

## Phase 3 — Independent re-verify (RC + MQ 2-wave)

### Task 3.1 — Wave-1 dispatch (parallel)

- [ ] **Step 1** — Foreground dispatches `Reality Checker` with brief: "Verify FORMAT INHERITANCE of `notes/STAGE_2_RESULTS.md` against the predecessor authorities `notes/PRIMITIVES.md` and `notes/SaaS_Builders_AI_NativeBuilders.md`. Specifically check: (a) line 1 is `**import [](./SaaS_Builders_AI_NativeBuilders.md)**`; (b) §-numbered headers in correct order (§0–§7); (c) LaTeX equations carry R-prefix tags (R1, R2, ...) in incrementing order; (d) boxed key results present (σ₀ R1, π(t) R2, Z_cap R8); (e) NO inline `file:line` patterns anywhere; (f) NO pytest test names anywhere; (g) NO sha256 outside §6; (h) §6 sha256 values match worksheet (`1fb1f7a4...5d31`, `4da660b5...2173`); (i) length ≤ 350 lines (regression gate vs the 813-line v1.1 citation registry); (j) freeze pin `9fd92e5` cited correctly in §6. Output: `scratch/2026-05-09-stage-2-results-reverify/RC_WAVE_1.md` with per-axis PASS/FLAG/BLOCK verdicts."
- [ ] **Step 2** — In parallel, foreground dispatches `Model QA Specialist` with brief: "Verify MATH CONTENT of `notes/STAGE_2_RESULTS.md`. Specifically check: (a) R1 σ₀ derivation correctly inverts PRIMITIVES (8); (b) R2 π(t) closed form matches the chain PRIMITIVES (6) → (8) → (10) → §10 → §15 open-item-4; (c) R3 perpetual identity is dimensionally and symbolically correct; (d) R4 §5.2 24-bracket Cartesian product matches spec §5.2; (e) R5 C1 marginalization is an analytic sum-out identity; (f) R6 M2 softplus tightness matches spec v1.2.1 M2 pin verbatim; (g) R7 det+churn $S_t = (1-\lambda)^t$ with $\lambda \sim \text{Beta}(4.5, 95.5)$ matches spec v1.2.1 §6.1; (h) R8 Z_cap closed form matches cohort-4 plan; (i) §3 TODO-COHORT closures correctly classify each as CLOSED / DEFERRED / INDISTINGUISHABLE per Task 1.3; (j) §5 Stage-3 open items in math form, NOT engineering checklist; (k) anti-fishing posture preserved (no relaxation of pins; HALT-on-flip preserved; no magnitude promise; no new claim outside spec/PRIMITIVES/SaaS-notes/cohort-plans/code at HEAD `9fd92e5`). Output: `scratch/2026-05-09-stage-2-results-reverify/MQ_WAVE_1.md`."
- [ ] **Step 3** — Wait for both. Read both verdicts.

### Task 3.2 — Adjudicate Wave-1

- [ ] **Step 1** — Foreground writes `scratch/2026-05-09-stage-2-results-reverify/WAVE_1_ADJUDICATION.md` summarizing union of BLOCKs and FLAGs.
- [ ] **Step 2** — If BLOCK count = 0 and FLAG count = 0: skip to Task 3.4.
- [ ] **Step 3** — Otherwise: dispatch Technical Writer (CORRECTIONS pass) with the union list as input. TW produces revised `notes/STAGE_2_RESULTS.md` + a CORRECTIONS-α appendix (final §) listing each fix in math-anchor tone (NOT a long change-log narrative). Commit.

### Task 3.3 — Wave-2 dispatch (parallel; only if Task 3.2 made changes)

- [ ] **Step 1** — Same dispatch pattern as Task 3.1, but agents re-read the post-CORRECTIONS doc. Output paths: `RC_WAVE_2.md`, `MQ_WAVE_2.md`, `WAVE_2_ADJUDICATION.md`.
- [ ] **Step 2** — Termination rule: convergence on zero BLOCKs (FLAGs may carry forward as documented limitations in §5). If Wave-2 still has BLOCKs, dispatch one more CORRECTIONS pass; if Wave-3 still has BLOCKs, HALT and surface to user.

### Task 3.4 — Re-verify completion record

- [ ] **Step 1** — Append final verdict (ACCEPT / ACCEPT_WITH_FLAGS) to `scratch/2026-05-09-stage-2-results-reverify/FINAL.md`.
- [ ] **Step 2** — Commit re-verify artifacts:
  - `git add scratch/2026-05-09-stage-2-results-reverify/`
  - `git commit -m "reverify(stage-2-results): RC+MQ 2-wave — <ACCEPT|ACCEPT_WITH_FLAGS>; format-inheritance + math-content verified"`

---

## Phase 4 — Commit + push

### Task 4.1 — Final state commit

- [ ] **Step 1** — Confirm `notes/STAGE_2_RESULTS.md` is the post-Wave-N (terminal-Wave) version; check via `git log --oneline notes/STAGE_2_RESULTS.md`.
- [ ] **Step 2** — Update CLAUDE.md "Active iterations" snapshot if a STAGE_2_RESULTS pointer should appear there. (Optional; foreground decides at Phase 4 time. If yes, separate commit.)

### Task 4.2 — Push branch

- [ ] **Step 1** — `git push origin iter/saas-builder-stage-2`. (No `--force`; no main/master push.)
- [ ] **Step 2** — Optionally open PR via `gh pr create` if user requests; not auto.

---

## Anti-fishing posture

NON-NEGOTIABLE constraints carried throughout:

1. **No new claims.** STAGE_2_RESULTS.md is a math anchor; it CANNOT introduce any claim not already in spec / PRIMITIVES.md / SaaS_Builders notes / cohort plans / code at HEAD `9fd92e5`. The corrected math forms (π(t), σ₀, M2 amendment, det+churn $S_t$, Z_cap) are already pinned upstream — this doc only expresses them in the predecessor's format.
2. **Format change is not a math change.** The v0.2 → v0.3 patch is a documentation-format correction, not a relaxation. No upstream claim relaxed; no spec amendment; no pin loosened.
3. **Frozen freeze pin.** Stage-2 is frozen at HEAD `9fd92e5`. STAGE_2_RESULTS.md captures that frozen state and does not auto-update.
4. **No magnitude promises in §5.** The Stage-3 hand-off section MUST NOT contain phrases like "real data will scale up," "magnitudes are expected to increase," or equivalents. Sign certs are sign certs; magnitudes are synthetic.
5. **HALT semantics preserved.** The C3 INDISTINGUISHABLE / HALT-on-flip semantic in §3.3 must be preserved as a HALT instruction for Stage-3, not softened to a recommendation.
6. **Format-pattern regression is itself anti-fishing-relevant.** A doc that hides math behind a citation registry obscures the audit surface. Mirroring PRIMITIVES.md / SaaS_Builders pattern keeps the math legible and the next iteration's "what changed" diff small.

---

## Self-review checklist

Run this before declaring the plan ready:

- [ ] **Format authority.** Tasks 1.1–1.4 reference `notes/PRIMITIVES.md` and `notes/SaaS_Builders_AI_NativeBuilders.md` as format authorities; Phase 2 brief instructs Technical Writer to read them in full FIRST.  ✓
- [ ] **Discard v1.1 explicit.** Phase 2 brief Step 2 explicitly instructs discard of `notes/STAGE_2_RESULTS.md` v1.1; rewrite from scratch.  ✓
- [ ] **No inline file:line / pytest / sha256 except §6.** Tasks 1.1, 1.2, 2.1 Step 5, Phase 3 RC Wave-1 brief all enforce this.  ✓
- [ ] **R-tagged equations.** Tasks 1.1 (R1–R8) and 1.2 enforce R-prefix tags; Phase 3 RC Wave-1 brief verifies.  ✓
- [ ] **TODO-COHORT closures classified.** Task 1.3 enumerates CLOSED / DEFERRED / INDISTINGUISHABLE for the four TODO-COHORT-N labels; Phase 3 MQ Wave-1 brief verifies (i).  ✓
- [ ] **§5 in math form.** Task 1.4; Phase 3 MQ brief check (j).  ✓
- [ ] **Length sanity gate.** Phase 2 Step 3 sanity-check enforces ≤ 350 lines (regression gate vs v1.1's 813 lines).  ✓
- [ ] **No case-study format.** Removed from Task 1.4 (replaced with §3 TODO-COHORT closure semantics); Phase 2 brief Step 5 explicitly excludes case-study format.  ✓
- [ ] **Type/citation consistency.** sha256 anchor values cited identically in Task 0.3 + Task 1.1 §6 + Task 2.1 Step 8 + Phase 3 RC Wave-1 brief: `Z_cap_pinned.json::audit_block` head `1fb1f7a4...` tail `...5d31`; `gate_verdict.json::audit_block` head `4da660b5...` tail `...2173`.  ✓
- [ ] **Type/citation consistency.** Output path `notes/STAGE_2_RESULTS.md` cited identically throughout.  ✓
- [ ] **Type/citation consistency.** Freeze-pin HEAD `9fd92e5` cited identically in goal, Task 0.1, Task 1.1 §6, Task 2.1 Step 10, Phase 3 RC Wave-1 brief, anti-fishing §3.  ✓
- [ ] **Code-agnostic.** No code blocks except shell commands and inline math LaTeX.  ✓
- [ ] **Foreground-no-author rule.** Phase 2 dispatches Technical Writer; Phase 3 dispatches RC + MQ; foreground only orchestrates and does sanity-checks.  ✓

---

## References

- Format authorities: `notes/PRIMITIVES.md`, `notes/SaaS_Builders_AI_NativeBuilders.md`
- Spec: `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md` v1.2.1
- Cohort plans: `docs/plans/2026-05-08-saas-cohort-{1,2,3,4}-*.md` + `docs/plans/2026-05-09-saas-cohort-close.md`
- Verdict memo: `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md`
- Skill: `superpowers:writing-plans`
- Repo memories: `feedback_no_code_in_specs_or_plans`, `feedback_specialized_agents_per_task`, `feedback_pathological_halt_anti_fishing_checkpoint`, `feedback_post_hoc_fit_anti_fishing_pattern`
- Predecessor verdict files (Wave-1 v0.1 → v0.2): `scratch/2026-05-09-stage-2-results-anchor-plan-review/{rc,mq}-verdict.md`
- Wave-2 v0.2 verdict files (ACCEPTs on the wrong format backbone — superseded by this v0.3 reset): `scratch/2026-05-09-stage-2-results-anchor-plan-review/{rc,mq}-verdict-v0.2.md`

---

## CORRECTIONS-α v0.1 → v0.2

Wave-1 plan-doc verify (RC + MQ, 2026-05-08) returned `ACCEPT_WITH_FLAGS` from both reviewers — RC with 2 BLOCKs + 3 FLAGs; MQ with 3 FLAGs. Anti-fishing posture: this revision is strictly tightening; no fix relaxes any pin or invariant. The two BLOCKs are factual corrections (sha attribution + git-semantic); the FLAGs are documentation precision. Architectural soundness was acknowledged by both reviewers. (See `scratch/2026-05-09-stage-2-results-anchor-plan-review/{rc,mq}-verdict.md`.)

### BLOCK resolutions (v0.1 → v0.2)

- **BLOCK-1 — Freeze-pin commit subject misattributed.** Corrected the quoted subject of `9fd92e5` and noted that `80f4ed4` is an ancestor.
- **BLOCK-2 — `git rev-parse HEAD` collides with current HEAD.** Replaced with ancestor-check + path-scoped diff-empty check.

### FLAG resolutions (v0.1 → v0.2)

- RC-FLAG-1 (cohort-close plan reference): ACK.
- RC-FLAG-2 (verdict memo path): hard-pinned.
- RC-FLAG-3 (sha256 truncation tail policy): 4-char tails added.
- MQ-FLAG-1 (§2.A.8 §11 scope extension): documented.
- MQ-FLAG-2 (§4 case-study detection-heuristic bullet): added.
- MQ-FLAG-3 (verification matrix row 6 granularity): per-§2.C.{1..8} verdicts required.

---

## CORRECTIONS-α v0.2 → v0.3

**Trigger.** User feedback after Phase 2 v0.2 dispatch: the resulting `notes/STAGE_2_RESULTS.md` v1.1 (813 lines, commit `ae4ad9b`) was "TREMENDOUSLY NOT what expected." The doc bore no resemblance to the predecessor lineage `notes/PRIMITIVES.md` / `notes/SaaS_Builders_AI_NativeBuilders.md` — those are math-flowing LaTeX-equation anchors with §-numbered headers, R/S-tagged equations, and boxed key results. v1.1 produced a citation registry instead.

**Diagnosis.** The v0.2 plan §1.2 backbone choice ("Hybrid math-claim-indexed backbone with cohort cross-references") and §1.3 citation format ("4-part citation format: claim verbatim / post-cycle form / file:line + pytest test name / sha256 audit_block") together prescribed a citation-registry shape. The Wave-1 RC + MQ verdicts on v0.2 (`scratch/2026-05-09-stage-2-results-anchor-plan-review/{rc,mq}-verdict-v0.2.md`) returned ACCEPT — but on the WRONG backbone. Format-pattern fidelity to the predecessor lineage was not in the v0.2 verification matrix; the math-anchor genre was not enforced. Result: a structurally correct citation registry (per v0.2 spec) that fails the actual purpose (a math anchor in the PRIMITIVES/SaaS_Builders lineage).

**Fix (v0.3 patch scope).**

- **§1.1 §-skeleton rewritten.** Replaced the prior §0–§7 skeleton (Preface / Empirical verdict / Math claims index / Cohort cross-cut / Anti-fishing case studies / Reproducibility / Stage-3 hand-off / References) with a SaaS_Builders-pattern skeleton: lineage marker → §0 Cohort scope → §1 Empirical sign verdict (boxed) → §2 Closed forms (R1–R5) → §3 TODO-COHORT-N closures → §4 Z_cap pinned (R8) → §5 Stage-3 open items (math form) → §6 Reproducibility (compact sha256) → §7 References (terse).
- **§1.2 (4-part citation format) deleted entirely.** Replaced with §1.2 Format-inheritance constraints: lineage marker, R-tagged equations, boxed results, math-flowing prose, NO inline file:line/pytest/sha256 except §6.
- **§1.3 (renamed and rewritten).** Now locks §3 TODO-COHORT closure semantics (CLOSED / DEFERRED / INDISTINGUISHABLE classification) instead of citation format.
- **§1.4 (anti-fishing case studies) removed from doc scope.** Case-study narrative belongs in `feedback_post_hoc_fit_anti_fishing_pattern.md` (already exists). The math anchor records the corrected math; the case-study narrative lives in feedback memos. Task 1.4 is now §5 hand-off invariants in math form.
- **§1.5 (was §6 hand-off invariants) merged with §1.4.**
- **§1.6 (was 8-row verification matrix) replaced with format-inheritance + math-content matrix (Task 1.5).**
- **Phase 2 brief rewritten.** Technical Writer instructed to: (a) read PRIMITIVES.md and SaaS_Builders notes in full FIRST; (b) discard v1.1 entirely; (c) mirror predecessor format verbatim; (d) NO file:line / pytest / sha256 inline (only §6 reproducibility); (e) PRIMITIVES.md tone; (f) length budget ≤ 350 lines (regression gate vs v1.1's 813 lines).
- **Phase 3 RC + MQ briefs rewritten.** RC verifies format inheritance (lineage marker, R-tags, boxed results, no inline citation patterns, length gate). MQ verifies math content (R1–R8 derivations, TODO-COHORT closures, anti-fishing posture).
- **v1.1 to be discarded on commit.** The 813-line citation registry is replaced by a fresh rewrite from scratch in Phase 2.

**Anti-fishing.** Format change is a documentation correction, not a math change. No upstream claim relaxed. No spec amendment. No pin loosened. No new claim introduced. The corrected math forms (π(t), σ₀, M2 amendment, det+churn $S_t$, Z_cap) were already pinned in spec v1.2.1 and cohort plans v0.3/v0.4 — this patch just expresses them in the right document format. The 31 verdict files in `scratch/` already preserve the audit-trail material that v1.1's citation registry tried to inline.

**Re-verify expectation.** RC + MQ Wave-3 plan-doc reverify on v0.3 will be triggered by the orchestrator before Phase 0 execution. RC will check that the §-skeleton mirrors SaaS_Builders pattern (lineage marker, R-tags, boxed results, no inline citation registry, length budget). MQ will check that the math content (when authored per Phase 2) covers the cycle's outcomes correctly (R1–R8, TODO-COHORT closures, anti-fishing posture preserved). Convergence target: zero BLOCKs from both reviewers.
