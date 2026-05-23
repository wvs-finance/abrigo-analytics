# Supervisor-Letter REVISION-D Corrections — Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this sub-plan task-by-task. Same approach as the parent plan and the REVISION-C sub-plan.

**Parent plan:** `docs/plans/2026-05-06-supervisor-review-document-implementation.md@f16f3be`
**Parent spec:** `docs/specs/2026-05-06-supervisor-review-document-design.md@0082dbf` (REVISION-A + REVISION-C integrated)
**Prior sub-plan:** `docs/sub-plans/2026-05-06-supervisor-letter-revC-corrections.md@208fab7`
**Letter v1.3 (current):** `docs/supervisor-review/letter.tex` → `2026-05-06-supervisor-letter.pdf` (committed `05b436d`, 6 pp)

**Goal:** Apply five user-given corrections (REVISION-D, 2026-05-06) to the entry-point letter only. The 37-page companion is unchanged.

**Architecture:** Four-task sub-plan. Task A dispatches two parallel research background-agents (FX-transmission Colombian-context references + YouTube transcript extraction). Task B amends the spec (§3.11 REVISION-D record) and runs a lightweight Wave-1 verify. Task C authors the two re-author briefs incorporating Task A's research outputs. Task D dispatches one Data-Methodology + one Econ-Writer revision in parallel, stitches selectively into `letter.tex`, recompiles, runs Wave-1 RC verify, commits as v1.4.

**Tech Stack:** Same as parent + REVISION-C — LaTeX `article`, plain `natbib`, `pdflatex` + `bibtex`. Web access via `WebFetch` for the YouTube transcript.

---

## REVISION-D corrections (verbatim from user 2026-05-06)

### Correction D-1 — Citation swap to Colombian-context FX-transmission references

> "On top of or instead of these references on the raanFromAngstrom/contracts/** there are some research done by agents that show better references landed to the Colombian case that prove FX rate is in the global economy foreign exchange is the main transmission layer of all other risks, inflation interest rate volatility, etc. There are some borradores de economía that say that inflation is a follower of this and also the yield rates of TES. Have a background agent that checks and adjusts this."

The current `letter.tex` §1 Motivation bullet cites three FX-as-primary-transmission references introduced in REVISION-C: `calvo_reinhart_2002` (*Fear of Floating*), `rey_2015` (*Dilemma not Trilemma*), `bruno_shin_2015` (*Cross-Border Banking and Global Liquidity*). These are correct in spirit (FX as primary transmission channel for emerging-market macro shocks) but generic; the user has flagged that **better Colombian-context references exist in the cross-repository research base** at `/home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/{notes,research,design,docs,refs,security-reviews}/` (the `ranFromAngstrom` worktree of the contracts repo). Specifically: **Banrep "borradores de economía"** (working papers) on Colombian inflation pass-through from FX, and TES (government-bond) yield-rate dynamics following FX.

**Background research scope (Task A.1):** scan the `ranFromAngstrom` worktree for prior agent-produced research that surfaces Colombian-context references on (i) FX as primary transmission channel for inflation pass-through, (ii) TES yield-rate dynamics following FX, (iii) the Banrep "borradores de economía" working-paper series. Return a short bibliography with citation keys, citation strings, and a brief one-sentence justification per reference for inclusion in §1 Motivation.

**Outcome:** the §1 Motivation bullet's `\citep{calvo_reinhart_2002,rey_2015,bruno_shin_2015}` is replaced (or augmented) with the Colombian-context references found by Task A.1. The generic `calvo_reinhart_2002` / `rey_2015` / `bruno_shin_2015` may stay as supporting general references if the new Colombian-context references are insufficient on their own, but Colombian-specific references take primacy.

### Correction D-2 — YouTube transcript extraction + content integration

> "I need you to do a transcript and context gathering through the video recorded and extract the content needed."

The current `letter.tex` §1 Suggested-solution bullet cites `\citep{depreciation_insurance_talk}` as a placeholder — the bib entry currently has `[Speaker --- to be filled by user]` and a generic title. The user wants the **actual transcript extracted from the video** (`https://www.youtube.com/watch?v=-nPTjKRMSK8&t=1250s`, timestamp ≈ 20:50 = 1250 seconds), the speaker identified, the talk title resolved, and the exact quote about "people on underserved countries look for depreciation insurance in the form of a call option on foreign exchange rate" extracted and either quoted directly in §1 or recorded in the bib entry's `note` field.

**Background research scope (Task A.2):** use `WebFetch` (or `mcp__plugin_playwright_playwright__browser_navigate` with the auto-generated YouTube transcript URL pattern, e.g. `https://youtube.com/api/timedtext?v=-nPTjKRMSK8&lang=en`, OR simply fetch the YouTube video page and search for the closed-caption track) to extract the transcript around timestamp 20:50. Return: (i) speaker name(s), (ii) talk title and venue, (iii) date (as available), (iv) the relevant quote about depreciation-insurance-as-call-option (verbatim, ±60 seconds of context).

**Outcome:** the `depreciation_insurance_talk` bib entry is updated with real metadata; the §1 Suggested-solution bullet either retains the citation as-is (with the metadata now correct) or quotes the verbatim phrase inline if the user wants the supervisor to see the source language.

### Correction D-3 — Repo HTTP URLs for data references (not relative paths)

> "The data must point at the repo http url not just notebooks/bpo_offshoring_fx_lag/ since the paper will be sent through email."

The current `letter.tex` §2 iteration blocks reference data via relative paths in `\texttt{...}` blocks: `\texttt{notebooks/bpo\_offshoring\_fx\_lag/}`, `\texttt{notebooks/dev\_ai\_cost/}`, `\texttt{notebooks/fx\_vol\_cpi\_surprise/}`. When the PDF is delivered by email, these paths are not clickable; the supervisor cannot navigate to them without the local repo.

**Replacement:** every relative-path data reference becomes a clickable HTTP URL via `\href{...}{...}` (the `hyperref` package is already in the preamble). The repo origin is `https://github.com/JMSBPP/abrigo-analytics`. URL pattern:

- `notebooks/bpo_offshoring_fx_lag/` → `\href{https://github.com/JMSBPP/abrigo-analytics/tree/master/notebooks/bpo_offshoring_fx_lag}{\texttt{notebooks/bpo\_offshoring\_fx\_lag}}`
- `notebooks/dev_ai_cost/` → `\href{https://github.com/JMSBPP/abrigo-analytics/tree/master/notebooks/dev_ai_cost}{\texttt{notebooks/dev\_ai\_cost}}`
- `notebooks/fx_vol_cpi_surprise/` → `\href{https://github.com/JMSBPP/abrigo-analytics/tree/master/notebooks/fx_vol_cpi_surprise}{\texttt{notebooks/fx\_vol\_cpi\_surprise}}`

For Phase-A.0 (no notebook directory exists at iteration close because the spec exited pre-estimation), use a link to the spec file or to `memory/project_phase_a0_exit_verdict.md` if appropriate, or omit the link and keep the spec-sha reference only. For P1, link to the spec file under `docs/specs/2026-04-27-p1-sn18-event-study-design.md`.

### Correction D-4 — Expanded data attributes / sources / length / transformations description

> "More description on the data attributes, sources, length data transformations done is crucial. In case the author does not have time to go through the repo himself."

The current `letter.tex` §2 iteration blocks describe data in one short line ("Data: \texttt{...} (governing spec sha \texttt{X}, N=Y monthly, A through B).") The user wants this expanded to a per-iteration **data attribute block** that surfaces the supervisor-relevant metadata without requiring him to visit the repo:

Per-iteration data block (replaces the single-line "Data:" sentence):

- **Source.** Authoritative source (DANE GEIH micro-data; Banrep TRM end-of-month spot; Banrep IBR; DANE CPI release calendar; Celo on-chain RPC; etc.).
- **Frequency.** Monthly / weekly / daily.
- **Window.** Concrete start date through concrete end date.
- **Sample size.** N = (post sample-window compliance).
- **Key transformations.** Logit on share-Y; log-level on FX; lag-aligned to spec; Newey-West HAC SE with fixed-`L` per iteration; etc.
- **Repo link.** `\href{}` to the iteration's notebook directory in the GitHub repo (per Correction D-3).
- **Spec sha.** Governing spec hash for pre-registration audit.

Target: expand the data line from ~1 sentence to ~5–7 lines per iteration. Net page-count effect: +0.5 pp roughly (5 iterations × +0.1 pp each). Should fit within the existing 6-pp envelope without spilling to 7 — if it does spill, accept the 7-pp count (still within the user's 8-pp ceiling).

### Correction D-5 — Even shorter interpretations: "failed + short why"

> "The interpretations need to be even shorter and only say it failed and short description why?"

The current §2 Interpretation lines are already shortened from REVISION-C v1.2 (10–15 words each). User wants them **even shorter — just "failed + short why"**:

- **Pair D (PASS).** Current: "Lagged-FX positively predicts broad-services young-worker share; gate cleared." → New: "PASS — gate cleared." (or absorb into the verdict in the heading; possibly delete the Interpretation line entirely for Pair D since "Caveats inherited from independent review" already follows.)
- **dev-AI Stage-1 (FAIL).** Current: "Sign-flipped FAIL: positive-sign expectation rejected at the Section-J narrow cut, not an underpowered null." → New: "FAIL — sign-flipped at Section-J narrow cut."
- **FX-vol-CPI (FAIL).** Current: "No detectable weekly-RV response to CPI surprises under the pre-committed primary." → New: "FAIL — no weekly-RV response to CPI surprises."
- **Phase-A.0 (EXIT).** Current: "Specification never estimated; killed pre-estimation by k1 + partial-k2 on 2026-04-24." → New: "EXIT — never estimated; killed by k1 + partial-k2."
- **P1 (PARKED).** Current: "Slow-lane apparatus parked; no graduating empirical claim." → New: "PARKED — apparatus complete, no claim graduated."

Rationale: the verdict label (PASS / FAIL / EXIT / PARKED) is already in the iteration heading; the Interpretation line should add a minimum-information signal of *why* the verdict landed where it did, not paraphrase the heading. The "Why it fails" line that follows handles the long-form post-mortem. Target: each Interpretation line ≤ 10 words.

---

## File structure

| Path | Status | Purpose |
|---|---|---|
| `docs/specs/2026-05-06-supervisor-review-document-design.md` | modify | Add §3.11 REVISION-D record (Task B.1) |
| `docs/supervisor-review/refs.bib` | modify | Replace `depreciation_insurance_talk` placeholder metadata with Task-A.2 transcript output; add Colombian-context FX-transmission entries from Task A.1 |
| `docs/supervisor-review/letter.tex` | modify | §1 Motivation citations + §1 Suggested solution (YouTube quote/cite refresh); §2 5 iteration blocks (data block + repo HTTP URL + interpretation contraction) |
| `scratch/2026-05-06-supervisor-review/research-revD-fx-transmission-co.md` | create (Task A.1 output) | FX-transmission Colombian-context bibliography from `ranFromAngstrom/contracts/**` |
| `scratch/2026-05-06-supervisor-review/research-revD-youtube-transcript.md` | create (Task A.2 output) | YouTube transcript extract + speaker/title/venue metadata |
| `scratch/2026-05-06-supervisor-review/brief-revD-iterations.md` | create | Data-Methodology brief: §2 data-block expansion + repo HTTP URLs + interpretation cuts |
| `scratch/2026-05-06-supervisor-review/brief-revD-citations.md` | create | Econ-Writer brief: §1 citation swap + YouTube quote integration |
| `scratch/2026-05-06-supervisor-review/agent-output-letter-revD-iterations.tex` | create (Data-Methodology output) | New §2 5 iteration blocks |
| `scratch/2026-05-06-supervisor-review/agent-output-letter-revD-citations.tex` | create (Econ-Writer output) | New §1 Motivation + Suggested-solution bullets |
| `docs/supervisor-review/2026-05-06-supervisor-letter.pdf` | rebuild | Re-compiled letter v1.4 (target 6–7 pp; ceiling 8) |

---

## Tasks

### Task A: Background research (parallel)

**Files (created by sub-agents):**
- `scratch/2026-05-06-supervisor-review/research-revD-fx-transmission-co.md`
- `scratch/2026-05-06-supervisor-review/research-revD-youtube-transcript.md`

**Parallelism note (per Wave-2 PM NIT):** dispatch A.1 + A.2 background agents in a single message at start of Task A, then **immediately begin Task B** in main thread — Tasks A and B are independent and can proceed in parallel. Task C waits on the A.3 completion gate.

- [ ] **Step A.1: Dispatch FX-transmission Colombian-context research agent (background; runs in parallel with A.2)**

`Agent` call:
- description: "FX-transmission Colombian refs research"
- subagent_type: `general-purpose`
- run_in_background: `true`
- prompt: see `Step A.1 prompt` block below.

```
You are a research agent. The user wants Colombian-context references that
support the claim "in the global economy, foreign exchange is the main
transmission layer for all other macro risks (inflation, interest-rate
volatility, capital-flow shocks, etc.)" — specifically references that
land in the Colombian case (e.g., Banrep "borradores de economía" working
papers showing inflation is a follower of FX, and TES yield rates also
following FX).

Search scope (in priority order):
1. /home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/notes/
2. /home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/research/
3. /home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/refs/
4. /home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/docs/
5. /home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/design/
6. /home/jmsbpp/apps/abrigo-analytics/memory/ (project memory files mentioning FX-transmission, inflation pass-through, TES, borradores)
7. /home/jmsbpp/apps/liq-soldk-dev/notes/MACRO_RISKS/ (cross-repo research base referenced in feedback memories)

Search terms: "borradores de economía", "borrador de economía", "Banrep
working paper", "inflation pass-through", "FX pass-through", "TES yield",
"TES bond", "Colombian inflation", "exchange-rate transmission",
"transmission channel", "fear of floating Colombia", "monetary
transmission Colombia".

For each reference found:
- citation key (suggest a natbib-compatible key like author_year)
- full citation string (author, year, title, venue, optional URL/DOI)
- 1-sentence justification of why it supports the FX-as-primary-transmission claim for the Colombian case
- the file path (in the search scope) where the reference was surfaced

Return up to 8 best references; prioritize Colombian-specific over generic
emerging-market literature. If the search returns nothing useful, say so
explicitly (do not pad with weak hits).

Output: write a markdown report to
/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review/research-revD-fx-transmission-co.md.
Total length under 800 words. Cite source paths.

Anti-overreach: do NOT modify any document, spec, plan, or
letter.tex. Do NOT install packages or fetch external sources beyond the
filesystem search scope. This is reconnaissance only.
```

- [ ] **Step A.2: Dispatch YouTube transcript extraction agent (background; runs in parallel with A.1)**

`Agent` call:
- description: "YouTube transcript extraction"
- subagent_type: `general-purpose`
- run_in_background: `true`
- prompt: see `Step A.2 prompt` block below.

```
You are a research agent. The user wants the transcript and context
gathered from a YouTube video and the relevant content extracted for
citation in a formal academic letter.

Video URL: https://www.youtube.com/watch?v=-nPTjKRMSK8&t=1250s
Timestamp of interest: 20:50 (= 1250 seconds)
Content of interest: the speaker discusses that "people on underserved
countries look for depreciation insurance in the form of a call option on
the foreign-exchange rate."

Approach (try in this order until one yields the transcript):

1. WebFetch the YouTube video page directly:
   https://www.youtube.com/watch?v=-nPTjKRMSK8
   YouTube embeds video metadata (title, channel name, upload date,
   description) in the page HTML.

2. WebFetch a YouTube transcript service (e.g., the "show transcript"
   feature is exposed via the timedtext API):
   https://www.youtube.com/api/timedtext?v=-nPTjKRMSK8&lang=en
   or
   https://www.youtube.com/api/timedtext?v=-nPTjKRMSK8&lang=es
   (try English first, then Spanish; the speaker may be Spanish-speaking).

3. If WebFetch fails or returns garbled content, try
   mcp__plugin_playwright_playwright__browser_navigate to the video URL
   and use browser_snapshot to read the rendered transcript panel.

4. If all transcript-fetch approaches fail, document what was attempted
   and return a structured report with the metadata that IS retrievable
   (title, channel, upload date) plus a placeholder note for the quote.

Return:
- Speaker name (channel name as fallback)
- Talk title
- Venue / channel
- Upload date
- Transcript excerpt: ±60 seconds around timestamp 20:50 (= 1190s to
  1310s), verbatim if available
- The specific quote about depreciation-insurance-as-call-option (if
  identifiable)
- Suggested updated `depreciation_insurance_talk` BibTeX entry with
  resolved metadata, in the same format as the existing entry in
  /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/refs.bib
  (search for "depreciation_insurance_talk" to see the current placeholder
  format).

Output: write a markdown report to
/home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review/research-revD-youtube-transcript.md.
Total length under 800 words. Quote sparingly (fair-use); paraphrase the
non-quoted portion.

Anti-overreach: do NOT modify refs.bib or letter.tex. Do NOT push
content to GitHub or any external service. This is reconnaissance only.
```

- [ ] **Step A.3: Wait for both research agents to complete**

Auto mode: continue with sub-plan tasks B / C in main thread while A.1 and A.2 run in background. When both notification arrive (status `completed`), proceed to Task C with the research outputs in scope.

If either agent fails / returns BLOCKED / produces an empty file, halt and report to user; do NOT silently proceed with placeholders.

---

### Task B: Spec amendment §3.11 + lightweight Wave-1 verify + commit

**Files:**
- Modify: `docs/specs/2026-05-06-supervisor-review-document-design.md` (append §3.11)

- [ ] **Step B.1: Append spec amendment §3.11**

Append after the existing §3.10 (REVISION-C corrections) and before `## §4. Multi-agent authorship plan`:

```markdown
### §3.11 Entry-Point Letter — REVISION-D corrections (2026-05-06)

This sub-section records five user-given corrections that apply to the
6-page entry-point letter v1.3 (`docs/supervisor-review/letter.tex` →
`2026-05-06-supervisor-letter.pdf`, committed `05b436d`), NOT to the
37-page technical companion. The companion remains unchanged.

**Correction D-1 (§1 Motivation citation swap to Colombian context).**
The v1.3 §1 Motivation bullet cites three generic FX-as-primary-transmission
references (Calvo & Reinhart 2002 *QJE*; Rey 2015 NBER WP 21162;
Bruno & Shin 2015 *RES*). Replace (or augment) with Colombian-context
references — Banrep "borradores de economía" working papers on inflation
pass-through and TES yield-rate dynamics following FX — sourced via a
background-agent scan of `/home/jmsbpp/apps/ThetaSwap/thetaSwap-core-dev/.worktree/ranFromAngstrom/contracts/{notes,research,refs,docs,design}/`.
Generic references may stay as supporting literature if the
Colombian-specific references are insufficient on their own; Colombian
references take primacy.

**Correction D-2 (§1 Suggested-solution YouTube transcript integration).**
The v1.3 cites `depreciation_insurance_talk` with placeholder bib
metadata. Resolve metadata via background-agent transcript extraction of
`https://www.youtube.com/watch?v=-nPTjKRMSK8` around timestamp 20:50
(= 1250s); fill in speaker, title, channel, upload date, and verbatim
quote about underserved-country demand for depreciation insurance as a
call option on FX rate. Optionally inline-quote the verbatim phrase in
the §1 prose if the supervisor would benefit from seeing the source
language.

**Correction D-3 (§2 data references — repo HTTP URLs).**
The v1.3 §2 iteration blocks reference data via relative paths
(`\texttt{notebooks/bpo\_offshoring\_fx\_lag/}`). Replace with clickable
HTTP URLs via `\href{...}{...}` (hyperref already in preamble); origin is
`https://github.com/JMSBPP/abrigo-analytics`. Required for email delivery
where the supervisor cannot navigate the local repo.

**Correction D-4 (§2 expanded data attribute blocks).**
The v1.3 §2 iteration blocks describe data in a single line. Expand each
to a per-iteration data attribute block surfacing supervisor-relevant
metadata (source, frequency, window, sample size, key transformations,
repo link, spec sha). ~5–7 lines per iteration. Net page-count effect:
+~0.5 pp; ceiling 8 pp per the user's earlier guidance.

**Correction D-5 (§2 Interpretation lines — even shorter).**
The v1.3 Interpretation lines are 10–15 words each. Tighten further to
"verdict + short why," ≤ 10 words each. The verdict label is already in
the iteration heading; the Interpretation line should add a
minimum-information *why* signal, not paraphrase the heading. The
"Why it fails" line that follows handles the long-form post-mortem.

**Out of scope for REVISION-D.** No changes to §3 Risk-target framing,
§4 Asks structure (the four asks remain unchanged), the title block, or
the bibliography section heading. No changes to the 37-page companion.
The §5 anti-overclaim invariants are unchanged; REVISION-D corrections
are mechanical (citation accuracy, link clickability, attribute
disclosure, length cuts) and do not introduce new claims.
```

- [ ] **Step B.2: Lightweight Wave-1 RC on the spec diff**

Dispatch a single Reality Checker review of the spec diff:
- description: "Wave 1 RC — REVISION-D spec diff"
- subagent_type: `Reality Checker`
- prompt: review the §3.11 amendment for fidelity to the five user-given corrections; confirm no fabricated specifics; ≤ 200 words; **output to `/tmp/wave1_rc_revD_taskB.md`** (filename consistent with the symmetric Task-D wave at `/tmp/wave1_rc_revD_taskD.md`).

If ACCEPT, commit. If FLAG, integrate inline and re-verify.

- [ ] **Step B.3: Commit Task B**

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git add docs/specs/2026-05-06-supervisor-review-document-design.md
git commit -m "docs(spec): REVISION-D corrections to entry-point letter

Five user-given corrections to letter v1.3 (commit 05b436d):
  D-1: §1 Motivation citation swap to Colombian-context FX-transmission
       references (background-agent search of ranFromAngstrom/contracts/**)
  D-2: §1 Suggested-solution YouTube transcript extraction +
       depreciation_insurance_talk bib metadata refresh
  D-3: §2 data references converted from relative paths to clickable
       repo HTTP URLs (https://github.com/JMSBPP/abrigo-analytics)
  D-4: §2 expanded per-iteration data attribute blocks (source,
       frequency, window, N, transformations, link, spec sha)
  D-5: §2 Interpretation lines cut to 'verdict + short why' (<= 10 words)

Wave-1 RC verification on spec diff: ACCEPT.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task C: Author the two re-author briefs (incorporates Task A research)

**Files:**
- Create: `scratch/2026-05-06-supervisor-review/brief-revD-iterations.md`
- Create: `scratch/2026-05-06-supervisor-review/brief-revD-citations.md`

- [ ] **Step C.1: Wait for Task A.1 + A.2 to complete**

Both research outputs must be on disk before brief-authoring:
- `scratch/.../research-revD-fx-transmission-co.md` (FX-transmission Colombian refs)
- `scratch/.../research-revD-youtube-transcript.md` (YouTube transcript)

If either output reports BLOCKED / no useful content, halt the sub-plan and report to user — do NOT proceed with placeholder content.

- [ ] **Step C.2: Author `brief-revD-iterations.md` (Data-Methodology)**

Brief content (verbatim into scratch file):

```markdown
# Section-Author Brief — REVISION-D iterations (Data-Methodology)

**Sub-agent type:** `Model QA Specialist`
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-letter-revD-iterations.tex`
**Length budget:** ~3 pp total (5 iterations × ~0.6 pp each — slight expansion vs v1.3 §2 from data-block expansion)

## What to produce

A single LaTeX block (NO BEGIN/END markers needed — main thread will
splice as the entire §2 body) replacing the existing letter.tex §2.
Begin the file with `\section{Five iterations}\label{sec:2}`.

Five paragraph-blocks, one per iteration, in this order: Pair D (PASS),
dev-AI Stage-1 (FAIL), FX-vol-CPI-surprise (FAIL), Phase-A.0 Remittance
(EXIT_NON_REMITTANCE), P1 Bittensor SN18 (PARKED).

## Per-iteration template (REVISION-D format)

\paragraph{<Iteration name> (<short scope> --- <verdict>).}
[1-line population + (Y, X) pair description.]
\[ <model equation in display math> \]
where <where-clause defining Y_t and X_{t-k}>.

\textit{Data.}
\begin{itemize}
  \item \textbf{Source.} <authoritative source>
  \item \textbf{Frequency.} <monthly/weekly/daily>
  \item \textbf{Window.} <start> through <end>
  \item \textbf{Sample size.} \(N = <N>\) <unit>
  \item \textbf{Key transformations.} <logit / log-level / lag-aligned / HAC SE / etc.>
  \item \textbf{Repo.} \href{https://github.com/JMSBPP/abrigo-analytics/tree/master/notebooks/<dir>}{\texttt{notebooks/<dir>}}
  \item \textbf{Spec sha.} \texttt{<short sha>}
\end{itemize}

\textit{Result.} <compact test statistics — single line>

\textit{Interpretation.} <verdict + short why; <= 10 words>

\textit{<Caveat / why-it-fails / why-parked>.} <one to three sentences; preserved load-bearing post-mortem from v1.3>

## Per-iteration data attributes (use these — extracted from v1.3 + memory)

### Pair D
- Source: DANE GEIH micro-data (young-worker share by sector); Banrep TRM end-of-month spot
- Frequency: monthly
- Window: 2015-01-31 through 2026-02-28
- N: 134 monthly
- Transformations: logit on share-Y; log-level on FX; lag panel \(k \in \{6, 9, 12\}\); HAC(L=12) Newey-West SE; FEX_C_2018 expansion factors
- Repo dir: bpo_offshoring_fx_lag
- Spec sha: 964c62cca0...ef659

### dev-AI Stage-1
- Source: DANE GEIH micro-data restricted to CIIU Rev. 4 Section J (Divisions 58–63); Banrep TRM
- Frequency: monthly
- Window: 2015-01-31 through 2026-03-31
- N: 134 monthly
- Transformations: logit on Section-J share; log-level on FX; same lag panel as Pair D; HAC(L=12); FEX_C_2018; empalme residual-bias diagnostic at 2020-12 → 2021-01 boundary
- Repo dir: dev_ai_cost
- Spec sha: 7c72292516...751f5a

### FX-vol-CPI-surprise
- Source: Banrep TRM daily log-return panel; DANE CPI release calendar; DANE CPI realized values for AR(1) surprise construction
- Frequency: weekly (Friday anchor)
- Window: 2008-01-02 through 2026-02-23
- N: 947 weekly
- Transformations: weekly RV from daily log-returns; signed AR(1) CPI surprise mapped to weekly cadence (carried across release week, zero otherwise); HAC(4) Newey-West SE; small set of macro-surprise controls
- Repo dir: fx_vol_cpi_surprise
- Spec fingerprint: nb1_panel_fingerprint.json

### Phase-A.0 Remittance
- Source: was-to-be Banrep monthly remittance + Celo on-chain cCOP / COPM aggregate user activity; spec exited pre-estimation
- Frequency: weekly (planned; never reached final N)
- Window: 2024-09 through 2026-04 (planned)
- N: not produced — exited pre-estimation
- Transformations: pre-registered; never executed
- Repo dir: NO notebook directory exists — spec exited pre-estimation. Use `\href{https://github.com/JMSBPP/abrigo-analytics/blob/master/docs/specs/2026-04-20-remittance-surprise-trm-rv-design.md}{\texttt{docs/specs/2026-04-20-remittance-surprise-trm-rv-design.md}}` linking to the spec file directly. Do NOT synthesise a `notebooks/phase\_a0\_remittance/` link — that directory does not exist in the repo.
- Spec sha: Phase-A.0 Rev 4.1 chain (kill-criterion-bearing)

### P1 Bittensor SN18
- Source: Bittensor SN18 (Cortex.t) alpha event-study; pre-pinned policy-event dates (Bittensor halving 2025-12-15; dTAO mainnet 2025-02-13; Cortex.t milestones)
- Frequency: event-window (asymmetric L)
- Window: per-event ±L
- N: planned N_min^events = 8; data ingest deferred
- Transformations: event-window abnormal-alpha indicator; nine-cell verdict cube; Bonferroni at α_primary = 0.0167 over P1+P2+P3
- Repo dir: (no notebook directory; spec at docs/specs/2026-04-27-p1-sn18-event-study-design.md)
- Spec sha: f855e036d3...b47aeab

## Interpretation lines (REVISION-D — verdict + short why; <= 10 words)

- Pair D: "PASS — gate cleared on lagged-FX predictor."
- dev-AI Stage-1: "FAIL — sign-flipped at Section-J narrow cut."
- FX-vol-CPI: "FAIL — no weekly-RV response to CPI surprises."
- Phase-A.0: "EXIT — never estimated; killed by k1 + partial-k2."
- P1: "PARKED — apparatus complete, no claim graduated."

(The verbose interpretive prose from v1.3 is dropped; the post-mortem
caveat block immediately following each Interpretation line carries the
load-bearing detail.)

## Discipline (UNCHANGED from REVISION-C)

LaTeX `\(...\)` inline only; `\[...\]` display only. NO unicode math.
`\hat{\beta}_{\mathrm{composite}}` (mathrm). NO bare `$...$`. NO biblatex
commands. The `Caveats inherited from independent review` /
`Why it fails` / `Why it exits` / `Why parked` blocks from v1.3 are
PRESERVED VERBATIM (do not re-author the post-mortem prose; it carries
the load-bearing RC FLAGs and inheritance discipline).

## Anti-overreach

ONLY §2 of letter.tex. Do NOT touch §1, §3, §4, the spec, the plan, or
the 37-page companion.
```

- [ ] **Step C.3: Author `brief-revD-citations.md` (Econ-Writer)**

Brief content (verbatim into scratch file):

```markdown
# Section-Author Brief — REVISION-D citations (Econ-Writer)

**Sub-agent type:** `Book Co-Author`
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-letter-revD-citations.tex`
**Length budget:** ~0.5 pp total (just §1 Motivation + §1 Suggested-solution bullets — surgical re-emit)

## What to produce

A single LaTeX file with TWO blocks:

```latex
% === BEGIN BULLET MOTIVATION ===
\item[Motivation.] [REVISED motivation bullet with Colombian-context FX-transmission citations]
% === END BULLET MOTIVATION ===

% === BEGIN BULLET SUGGESTED-SOLUTION ===
\item[Suggested solution.] [REVISED suggested-solution bullet with YouTube quote integration]
% === END BULLET SUGGESTED-SOLUTION ===
```

(Just the two `\item` lines that go inside the existing §1 `description`
list. Main thread will replace the corresponding lines in letter.tex.)

## Inputs from Task A

Read both research outputs IN FULL before drafting:
- `scratch/2026-05-06-supervisor-review/research-revD-fx-transmission-co.md`
  (Colombian-context FX-transmission references)
- `scratch/2026-05-06-supervisor-review/research-revD-youtube-transcript.md`
  (YouTube speaker / title / quote / metadata)

## §1 Motivation bullet (Correction D-1)

Replace the v1.3 citation chain
`\citep{calvo_reinhart_2002,rey_2015,bruno_shin_2015}` with citations
from the Task A.1 Colombian-context research output. Specifically:
- Lead with Colombian-context citations (Banrep "borradores de economía"
  on FX → inflation pass-through; TES yield → FX dynamics) found by
  Task A.1.
- If the Colombian-context references prove the FX-as-primary-transmission
  claim sufficiently on their own, drop the generic Calvo-Reinhart / Rey /
  Bruno-Shin citations. If they only partially prove it, keep the generic
  ones as supporting references after the Colombian-specific ones.
- The bullet's prose may need adjustment if Task A.1's references support
  a slightly different framing — adjust the prose, do not adjust the
  evidence.

Add the new bib keys to refs.bib (the main thread merges this; you don't
need to edit refs.bib directly — just specify the keys in the prose).
The Task A.1 output should provide both the keys and the BibTeX entry
strings for the main thread to add.

## §1 Suggested-solution bullet (Correction D-2)

Update the v1.3 citation `\citep{depreciation_insurance_talk}` with the
resolved metadata from Task A.2:
- The bib entry for `depreciation_insurance_talk` is updated by the main
  thread (Task D.3) with the resolved speaker / title / venue / date.
- The prose in the bullet can either retain the existing citation
  (`\citep{depreciation_insurance_talk}`) — the metadata refresh happens
  in the bib, not in the prose — OR add a verbatim quote inline if the
  Task A.2 transcript surfaces a particularly clean phrase. Judgment
  call: a verbatim quote of ≤ 25 words can be inlined in `\textit{...}`
  or `\enquote{...}` (preamble may need `csquotes` — check; if absent,
  use `\textit{...}` or simple quotation marks); a longer extract should
  stay in the bib note rather than the prose.

If Task A.2 returns BLOCKED (the transcript could not be extracted), do
NOT modify the §1 Suggested-solution bullet — leave the v1.3 citation
in place and flag in your report so the main thread knows to handle
the bib metadata manually before commit.

## Discipline

- LaTeX `\(...\)` inline only; NO unicode math; NO biblatex commands.
- Citations: `\cite{key}` / `\citet{key}` / `\citep{key}` — natbib only.
- NO ideology mentions.
- Brief surgical edits only — preserve the rest of the v1.3 §1 bullets
  (Problem, Challenges, Bridge to §2) verbatim by NOT emitting them.

## Anti-overreach

ONLY the two §1 bullets specified. Do NOT emit a full §1 section, do NOT
touch §2, §3, §4, the spec, the plan, or the 37-page companion. Do NOT
modify refs.bib directly — flag bib-entry additions/updates in your
report and the main thread (Task D.3) will apply them.
```

- [ ] **Step C.4: NO commit (briefs + research outputs are scratch)**

Per `feedback_two_wave_doc_verification` "Out of scope" rule.

---

### Task D: Dispatch + stitch + recompile + commit v1.4

**Files:**
- Modify: `docs/supervisor-review/letter.tex`
- Modify: `docs/supervisor-review/refs.bib` (add Colombian-context entries from Task A.1; refresh `depreciation_insurance_talk` from Task A.2)
- Rebuild: `docs/supervisor-review/2026-05-06-supervisor-letter.pdf`

- [ ] **Step D.1: Dispatch the two re-author agents in parallel**

Single message with two `Agent` calls (per the brief contents from Task C.2 + C.3).

- [ ] **Step D.2: Verify both agent outputs landed**

Same 4-row decision table as REVISION-C sub-plan Task B.2 (file present + non-empty + correct markers OR halt + selective-retry; iteration cap 2).

- [ ] **Step D.3: Update refs.bib with Colombian-context entries + YouTube metadata refresh**

Append the new BibTeX entries (citation strings provided by Task A.1 in
its research output) to refs.bib. Replace the placeholder
`depreciation_insurance_talk` entry with the resolved metadata from
Task A.2.

- [ ] **Step D.4: Stitch into letter.tex**

Three surgical edits:

1. Replace the §1 Motivation `\item[Motivation.] ...` line with the
   content from `agent-output-letter-revD-citations.tex` BULLET
   MOTIVATION block.
2. Replace the §1 Suggested-solution `\item[Suggested solution.] ...`
   line with the content from `agent-output-letter-revD-citations.tex`
   BULLET SUGGESTED-SOLUTION block.
3. Replace the entire §2 body with the content of
   `agent-output-letter-revD-iterations.tex` (the file already includes
   `\section{Five iterations}\label{sec:2}` so it is a complete §2).

- [ ] **Step D.5: Recompile with HALT branch**

Same recompile + HALT discipline as REVISION-C sub-plan Task B.4
(`set -uo pipefail`, post-compile grep on letter.log for fatal /
undefined citations / undefined references; bibtex non-zero is
hard-error not silent-pass).

Page-count decision rule:

| Page count | Action |
|---|---|
| 6 ≤ N ≤ 8 | **ACCEPT** — within tolerance band of the user's 8-pp ceiling |
| N = 9 | **SOFT REVIEW** — tighten data-attribute bullets if any of them are over-detailed; one re-edit pass |
| N > 9 | **HARD HALT** — report; tighten or escalate |

- [ ] **Step D.6: Lightweight Wave-1 RC verify on assembled letter**

≤ 200 words; ACCEPT / FLAG. Output to `/tmp/wave1_rc_revD_taskD.md` (symmetric with Task B.2's `/tmp/wave1_rc_revD_taskB.md`).

- [ ] **Step D.7: Final commit Task D**

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git add docs/supervisor-review/letter.tex docs/supervisor-review/refs.bib docs/supervisor-review/2026-05-06-supervisor-letter.pdf
git commit -m "docs: supervisor letter v1.4 — REVISION-D five corrections

Five user-given corrections to v1.3 (commit 05b436d):

  D-1: §1 Motivation citation swap to Colombian-context FX-transmission
       references sourced via background-agent scan of
       ranFromAngstrom/contracts/{notes,research,refs,docs,design}/.
       Banrep 'borradores de economía' on inflation-as-FX-follower and
       TES yield-rate dynamics following FX. Generic Calvo-Reinhart /
       Rey / Bruno-Shin retained as supporting literature where the
       Colombian references are insufficient on their own.

  D-2: §1 Suggested-solution depreciation_insurance_talk metadata
       refreshed from background-agent YouTube transcript extraction
       (https://www.youtube.com/watch?v=-nPTjKRMSK8 timestamp 20:50).
       Speaker / title / channel / date resolved; verbatim quote on
       underserved-country demand for depreciation-insurance-as-call-
       option captured in bib note.

  D-3: §2 data references converted from relative paths to clickable
       repo HTTP URLs (https://github.com/JMSBPP/abrigo-analytics/tree/
       master/notebooks/<dir>). Required for email delivery.

  D-4: §2 expanded per-iteration data attribute blocks (source,
       frequency, window, N, transformations, repo link, spec sha)
       from one-line summary to ~5-7 lines per iteration.

  D-5: §2 Interpretation lines cut to 'verdict + short why' (<= 10
       words each); the Caveats / Why-it-fails post-mortem block
       immediately following carries the load-bearing detail.

Page count: <N> pp.
Compile: 0 fatal errors, all citations resolved.
Wave-1 RC verification on stitched letter: ACCEPT (or FLAGs integrated).

Implements REVISION-D Tasks A-D of sub-plan
docs/sub-plans/2026-05-06-supervisor-letter-revD-corrections.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Self-review

| REVISION-D requirement | Sub-plan task |
|---|---|
| D-1 §1 Motivation citation swap to Colombian-context FX-transmission refs (with background research) | Task A.1 (research) → Task C.3 (brief) → Task D.1 (dispatch) → Task D.3 (bib update) → Task D.4 (stitch) |
| D-2 §1 Suggested-solution YouTube transcript extraction + metadata refresh | Task A.2 (transcript) → Task C.3 (brief) → Task D.1 (dispatch) → Task D.3 (bib refresh) → Task D.4 (stitch) |
| D-3 §2 data references — repo HTTP URLs | Task C.2 (brief) → Task D.1 (dispatch) → Task D.4 (stitch) |
| D-4 §2 expanded data attribute blocks | Task C.2 (brief, with attribute table inline) → Task D.1 (dispatch) → Task D.4 (stitch) |
| D-5 §2 Interpretation lines ≤ 10 words | Task C.2 (brief, with verbatim line inline) → Task D.1 (dispatch) → Task D.4 (stitch) |
| Spec amendment recording all five corrections | Task B.1 (§3.11) |
| Lightweight verification (Wave-1 RC) | Task B.2 (spec diff) + Task D.6 (assembled letter) |
| Page count within user's 8-pp ceiling | Task D.5 decision rule (6 ≤ N ≤ 8 ACCEPT) |
| 37-page companion preserved unchanged | Out of scope by construction |
| Background research before brief authoring (per user "before implementation" instruction) | Task A precedes Task C; Task C waits on Task A.3 completion gate |

**Placeholder scan:** No TBDs, no "fill in details." All brief contents and spec amendment text reproduced verbatim in this sub-plan.

**Type consistency:** File paths consistent (`scratch/2026-05-06-supervisor-review/agent-output-letter-revD-{iterations,citations}.tex`). Subagent types match parent plan + REVISION-C sub-plan rosters. Spec section numbering (§3.11 follows §3.10).

**Scope check:** Single subsystem (entry-point letter only, plus refs.bib). No spec section without a covering task. No task expands beyond the five REVISION-D corrections.

---

## Out of scope for this sub-plan

- The 37-page technical companion (`main.tex` → `2026-05-06-empirical-record-letter.pdf`) — unchanged.
- The implementation plan and the parent / REVISION-C sub-plans — unchanged.
- §3 Risk-target framing, §4 Asks structure (the four asks remain unchanged), title block, bibliography section heading.
- Re-running the full three-way verification — Wave-1 RC alone is the verification gate for REVISION-D (the changes are mechanical: citation accuracy, link clickability, attribute disclosure, length cuts).
- Installing external packages or fetching content beyond the YouTube URL and the filesystem search scope.
