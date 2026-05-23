# Supervisor-Review Document Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the `docs/supervisor-review/2026-05-06-empirical-record-letter.{tex,pdf}` LaTeX memorandum + `refs.bib` bibliography deliverable governed by spec `docs/specs/2026-05-06-supervisor-review-document-design.md` (sha pinned at commit `f5dcea9`).

**Architecture:** Three sub-agents (Model QA Specialist, Technical Writer, Book Co-Author) author distinct sections in parallel; the main thread stitches the LaTeX file, merges the bibliographies, compiles to PDF, then re-runs the two-wave verification (Reality Checker + Model QA Specialist) on the assembled output before final commit.

**Tech Stack:** LaTeX `article` class (`pdflatex`); BibTeX backend (no `biber`); `natbib` for citation rendering — **plain `natbib` package, NOT `biblatex` with bibtex backend** (avoiding the hybrid footgun flagged by Wave-1 RC FLAG-1); standard packages (`hyperref`, `amsmath`, `amsthm`, `booktabs`, `graphicx`, `xcolor`, `enumitem`, `fancyhdr`, `parskip`).

**Authorship roster note (LaTeX-research recon, 2026-05-06).** A separate research agent surveyed available LaTeX-mathematical-writing agents and reported: no local agent is purpose-built for econometric LaTeX writing; two external candidates exist (`pedrohcgs/claude-code-my-workflow`, `AlessandroCaforio/Academic-Writing`) but are out of scope for this run (no installs). Recommendation adopted: **keep the current three-agent roster (`Model QA Specialist`, `Technical Writer`, `Book Co-Author`) and harden each brief with explicit math-typesetting directives** to compensate for Claude's documented failure mode of defaulting to unicode-styled equations rather than LaTeX math environments. Math-typesetting directives are folded into Task 3 briefs.

---

## Spec source of truth

This plan operationalises `docs/specs/2026-05-06-supervisor-review-document-design.md` (committed at `f5dcea9` 2026-05-06). Every task references the spec section it implements; if a step appears to deviate, **stop and reconcile against the spec** rather than improvise.

The spec has been verified via the project's `feedback_two_wave_doc_verification` rule (Wave 1 Reality Checker + Wave 2 Model QA Specialist; reports preserved at `/tmp/wave1_rc_supervisor_review_design.md` and `/tmp/wave2_modelqa_supervisor_review_design.md`).

---

## File structure

| Path | Status | Purpose |
|---|---|---|
| `docs/supervisor-review/main.tex` | create | Assembled LaTeX root file with `\input{}` directives for each section |
| `docs/supervisor-review/preamble.tex` | create | Document class, packages, macros, header/footer |
| `docs/supervisor-review/sections/01-introduction.tex` | create | §1 Introduction & Economic Motivation (Econ-Writer) |
| `docs/supervisor-review/sections/02-framework.tex` | create | §2 Operating Framework (Econ-Writer) |
| `docs/supervisor-review/sections/03-lemma.tex` | create | §3 Abrigo Lemma (Econ-Writer) |
| `docs/supervisor-review/sections/04-onchain-primer.tex` | create | §4 On-Chain Settlement Substrate (On-Chain Explainer) |
| `docs/supervisor-review/sections/05-methodology.tex` | create | §5 Empirical Methodology (Data-Methodology) |
| `docs/supervisor-review/sections/06-log.tex` | create | §6 Abrigo Log (Data-Methodology) |
| `docs/supervisor-review/sections/07-questions.tex` | create | §7 Open Methodological Questions (Econ-Writer) |
| `docs/supervisor-review/sections/08-request.tex` | create | §8 Request for Guidelines (Econ-Writer) |
| `docs/supervisor-review/sections/appA-glossary.tex` | create | Appendix A Glossary (Econ-Writer + On-Chain Explainer halves) |
| `docs/supervisor-review/sections/appB-bibliography.tex` | create | Appendix B narrative wrapper around `\printbibliography` |
| `docs/supervisor-review/sections/appC-pair-d-verdict-header.tex` | create | Appendix C Pair D verdict header artifact (Data-Methodology) |
| `docs/supervisor-review/sections/appD-power-calculation.tex` | create | Appendix D Power-calculation transparency table (Data-Methodology) |
| `docs/supervisor-review/refs.bib` | create | Merged BibTeX file (deduplicated across the three sub-agents) |
| `docs/supervisor-review/build.sh` | create | Manual compile sequence (`pdflatex` → `bibtex` → `pdflatex` × 2) |
| `docs/supervisor-review/2026-05-06-empirical-record-letter.pdf` | create (build output) | Compiled PDF deliverable |
| `docs/supervisor-review/.gitignore` | create | Ignore `.aux`, `.log`, `.out`, `.toc`, `.bbl`, `.blg`, `.synctex.gz` |
| `scratch/2026-05-06-supervisor-review/brief-data-methodology.md` | create | Section-author brief for Model QA Specialist |
| `scratch/2026-05-06-supervisor-review/brief-onchain-explainer.md` | create | Section-author brief for Technical Writer |
| `scratch/2026-05-06-supervisor-review/brief-econ-writer.md` | create | Section-author brief for Book Co-Author |
| `scratch/2026-05-06-supervisor-review/agent-output-data.tex` | create (agent output) | Data-Methodology agent's combined LaTeX output |
| `scratch/2026-05-06-supervisor-review/agent-output-onchain.tex` | create (agent output) | On-Chain Explainer agent's combined LaTeX output |
| `scratch/2026-05-06-supervisor-review/agent-output-econ.tex` | create (agent output) | Econ-Writer agent's combined LaTeX output |
| `scratch/2026-05-06-supervisor-review/citations-data.bib` | create (agent output) | Data-Methodology agent's BibTeX sub-list |
| `scratch/2026-05-06-supervisor-review/citations-onchain.bib` | create (agent output) | On-Chain Explainer agent's BibTeX sub-list |
| `scratch/2026-05-06-supervisor-review/citations-econ.bib` | create (agent output) | Econ-Writer agent's BibTeX sub-list |

**Decomposition rule.** One `.tex` file per spec section. Each file is small (≤ ~5 pp of source), focused, and individually editable in response to supervisor feedback. The main file is a thin index that `\input`s sections in order.

---

## Tasks

### Task 1: Workspace setup + toolchain verification

**Files:**
- Create: `docs/supervisor-review/` (directory)
- Create: `scratch/2026-05-06-supervisor-review/` (directory)
- Create: `docs/supervisor-review/.gitignore`

- [ ] **Step 1: Verify LaTeX toolchain prerequisites (independent of Step 2 — may run in parallel)**

```bash
which pdflatex bibtex && \
  pdflatex --version | head -1 && \
  bibtex --version 2>&1 | head -1 && \
  kpsewhich natbib.sty hyperref.sty amsmath.sty amsthm.sty booktabs.sty fancyhdr.sty geometry.sty
```

Expected: both binaries resolve under `/usr/bin/` (or a TeX Live install); pdflatex + bibtex version lines; all `.sty` files resolve to a TeX Live tree path. If any `.sty` is missing, halt and ask the user to install (Arch: `pacman -S texlive-latexrecommended texlive-fontsrecommended texlive-publishers`; Debian/Ubuntu: `apt install texlive-latex-recommended texlive-fonts-recommended texlive-publishers`).

- [ ] **Step 1b: Pre-flight probe — verify all four sub-agent types resolve before Task 4 / Task 8 dispatch (per Wave-1 RC FLAG-2)**

The `Model QA Specialist` and `Book Co-Author` definitions may live in `~/.claude/agents/_archived/` rather than the active agent path. Before relying on them in Task 4 and Task 8, dispatch a no-op probe to confirm the runtime resolves all four:

Send four `Agent` calls in a single message, each with description `"Pre-flight probe: confirm dispatch"` and prompt:

```
Reply with the exact one-line string: "Probe ack from <subagent_type>" — substituting the subagent_type value into <subagent_type>. Do nothing else. No tool calls, no file reads.
```

Subagent types to probe: `Model QA Specialist`, `Book Co-Author`, `Technical Writer`, `Reality Checker`.

Expected: all four return their ack line within ~30 seconds. If any returns "subagent type not found" or fails to dispatch, halt and ask the user how to proceed (e.g., move the archived definition to the active path, or substitute a different agent — Wave-1 RC reports archived candidates `~/.claude/agents/_archived/specialized/specialized-model-qa.md` and `~/.claude/agents/_archived/marketing/marketing-book-co-author.md`).

- [ ] **Step 2: Create directory layout (independent of Step 1 — may run in parallel)**

```bash
mkdir -p /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/sections
mkdir -p /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review
ls -la /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review
```

Expected: both directories exist; `sections/` is empty.

- [ ] **Step 3: Add `.gitignore` for LaTeX build artifacts**

Write `docs/supervisor-review/.gitignore` with content:

```gitignore
# LaTeX intermediate / build artifacts
*.aux
*.log
*.out
*.toc
*.bbl
*.blg
*.synctex.gz
*.fdb_latexmk
*.fls
*.lot
*.lof
```

- [ ] **Step 4: Commit Task 1**

```bash
git add docs/supervisor-review/.gitignore
git commit -m "docs: scaffold docs/supervisor-review workspace + LaTeX gitignore

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

(Commit prefix `docs:` is the project precedent — see git log; `chore:` is also acceptable but `docs:` is preferred for the documentation tree.)

Expected: commit lands; `git log -1 --oneline` shows the new commit.

---

### Task 2: LaTeX skeleton (preamble + main + section stubs)

**Files:**
- Create: `docs/supervisor-review/preamble.tex`
- Create: `docs/supervisor-review/main.tex`
- Create: `docs/supervisor-review/sections/01-introduction.tex` through `appD-power-calculation.tex` (12 stubs)
- Create: `docs/supervisor-review/build.sh`

This task produces a compilable but empty document. The skeleton is verifiable: it must compile to a PDF with section headers and "TBD — drafted by [agent role]" placeholders. The placeholders are replaced in Task 5 by the agent outputs from Task 4.

- [ ] **Step 1: Write the preamble**

Write `docs/supervisor-review/preamble.tex`:

```latex
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[english]{babel}
\usepackage[a4paper,margin=2.5cm]{geometry}
\usepackage{setspace}
\onehalfspacing
\usepackage{parskip}
\usepackage{microtype}

\usepackage{amsmath,amssymb,amsthm}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{titlesec}

% --- Citation idiom: plain natbib + bibtex backend (NOT biblatex). ---
% Per Wave-1 RC FLAG-1: avoid the biblatex-with-bibtex-backend hybrid.
% Sub-agents are instructed to use \cite{key} / \citet{key} / \citep{key}.
\usepackage[authoryear,round]{natbib}
\bibliographystyle{plainnat}

\usepackage[colorlinks=true,linkcolor=blue!50!black,citecolor=blue!50!black,urlcolor=blue!50!black]{hyperref}

\theoremstyle{plain}
\newtheorem{lemma}{Lemma}

% --- Provenance footer (per Wave-2 PM NIT) ---
% Records the spec sha and build date so the supervisor (or any future
% auditor) can reconstruct the production process from the PDF alone.
\newcommand{\specsha}{f5dcea9}
\newcommand{\builddate}{\today}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Supervisor-Review Memorandum}
\fancyhead[R]{\small \builddate}
\fancyfoot[L]{\scriptsize spec: \texttt{docs/specs/2026-05-06-supervisor-review-document-design.md@\specsha}}
\fancyfoot[C]{\thepage}
\fancyfoot[R]{\scriptsize built \builddate}

\titleformat{\section}{\Large\bfseries}{\S\thesection.}{0.5em}{}
\titleformat{\subsection}{\large\bfseries}{\S\thesubsection}{0.5em}{}

\title{A Methodological Framework for Identifying and Empirically Validating
Macroeconomic Risks Suitable for On-Chain Convex Hedge Instruments \\[0.5em]
\large Record of Closed Iterations and Request for Supervisor Guidance}
\author{[author block — fill at composition time]}
\date{2026-05-06}
```

- [ ] **Step 2: Write the main file with section inputs**

Write `docs/supervisor-review/main.tex`:

```latex
\input{preamble}

\begin{document}
\maketitle
\thispagestyle{empty}

\tableofcontents
\newpage

\input{sections/01-introduction}
\input{sections/02-framework}
\input{sections/03-lemma}
\input{sections/04-onchain-primer}
\input{sections/05-methodology}
\input{sections/06-log}
\input{sections/07-questions}
\input{sections/08-request}

\appendix
\input{sections/appA-glossary}
\input{sections/appB-bibliography}
\input{sections/appC-pair-d-verdict-header}
\input{sections/appD-power-calculation}

\end{document}
```

- [ ] **Step 3: Write each section stub**

For each of the 12 section files, write a stub of the form:

```latex
% docs/supervisor-review/sections/01-introduction.tex
\section{Introduction \& Economic Motivation}\label{sec:1}

\textit{TBD — drafted by Econ-Writer (Book Co-Author) per spec \S3.1.}
```

Specific stubs (one per file, matching the spec's section assignments):

- `01-introduction.tex` → `\section{Introduction \& Economic Motivation}\label{sec:1}` — Econ-Writer per spec §3.1
- `02-framework.tex` → `\section{Operating Framework: The (Y, M, X) Triple}\label{sec:2}` — Econ-Writer per spec §3.2
- `03-lemma.tex` → `\section{The Abrigo Lemma: Inequality Differential as Hedge Target}\label{sec:3}` — Econ-Writer per spec §3.3
- `04-onchain-primer.tex` → `\section{On-Chain Settlement Substrate: Primer for the Non-Specialist Reader}\label{sec:4}` — On-Chain Explainer per spec §3.4
- `05-methodology.tex` → `\section{Empirical Methodology}\label{sec:5}` — Data-Methodology per spec §3.5
- `06-log.tex` → `\section{The Abrigo Log: Record of Closed and Active Iterations}\label{sec:6}` — Data-Methodology per spec §3.6
- `07-questions.tex` → `\section{Open Methodological Questions for Supervisor Review}\label{sec:7}` — Econ-Writer per spec §3.7
- `08-request.tex` → `\section{Request for Guidelines}\label{sec:8}` — Econ-Writer per spec §3.8
- `appA-glossary.tex` → `\section{Glossary}\label{app:A}` — Econ-Writer + On-Chain Explainer per spec §3.9
- `appB-bibliography.tex` → `\section{Cited Literature}\label{app:B}` followed by `\bibliography{refs}` (plain natbib idiom; `\printbibliography` is biblatex-specific and was removed per Wave-1 RC FLAG-1 closure)
- `appC-pair-d-verdict-header.tex` → `\section{Sample Artifact: Pair D Verdict Header}\label{app:C}` — Data-Methodology per spec §3.9
- `appD-power-calculation.tex` → `\section{Power-Calculation Transparency Table}\label{app:D}` — Data-Methodology per spec §3.9

- [ ] **Step 4: Create a stub `refs.bib` so the skeleton compiles**

Write `docs/supervisor-review/refs.bib`:

```bibtex
@misc{stub_2026,
  title  = {Stub citation; replaced in Task 6},
  author = {{Main thread}},
  year   = {2026}
}
```

- [ ] **Step 5: Write the build script**

Write `docs/supervisor-review/build.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
mv main.pdf 2026-05-06-empirical-record-letter.pdf
echo "PDF: $(pwd)/2026-05-06-empirical-record-letter.pdf"
```

Then make it executable:

```bash
chmod +x /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/build.sh
```

- [ ] **Step 6: Verify the skeleton compiles**

Run:

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review && ./build.sh
```

Expected: PDF generated at `docs/supervisor-review/2026-05-06-empirical-record-letter.pdf`; one warning about the stub citation key being undefined (acceptable at this stage); no fatal errors. Page count ~3-5 (TOC + 12 stub sections).

- [ ] **Step 7: Commit Task 2**

```bash
git add docs/supervisor-review/preamble.tex docs/supervisor-review/main.tex docs/supervisor-review/sections/ docs/supervisor-review/refs.bib docs/supervisor-review/build.sh
git commit -m "feat: scaffold supervisor-review LaTeX skeleton (compiles to placeholder PDF)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

Note: `2026-05-06-empirical-record-letter.pdf` is not committed at this stage; it will be committed once content is in (Task 7).

---

### Task 3: Author the three section-author briefs

**Files:**
- Create: `scratch/2026-05-06-supervisor-review/brief-data-methodology.md`
- Create: `scratch/2026-05-06-supervisor-review/brief-onchain-explainer.md`
- Create: `scratch/2026-05-06-supervisor-review/brief-econ-writer.md`

Each brief is a self-contained mission for one sub-agent. Briefs are scratch artifacts (per `feedback_two_wave_doc_verification` "Out of scope" exclusion); they are not committed to the main tree but are preserved for audit.

- [ ] **Step 1: Write `brief-data-methodology.md`**

Write the brief verbatim:

````markdown
# Section-Author Brief — Data-Methodology

**Sub-agent type:** `Model QA Specialist`
**Output sections:** §5, §6, App C, App D (per spec §3 table + §4 multi-agent table)
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-data.tex`
**Citation file:** `scratch/2026-05-06-supervisor-review/citations-data.bib`
**Length budget:** §5 ~6 pp + §6 ~7 pp + App C ~1 p + App D ~1 p ≈ 15 pp; soft ±10% latitude.

## Source materials (read in full before drafting)

1. `docs/specs/2026-05-06-supervisor-review-document-design.md` — your binding spec; especially §3.5, §3.6, §3.9, §5, App D specification.
2. `docs/specs/2026-04-27-simple-beta-pair-d-design.md` — Pair D spec; ground truth for §6.1 iteration block.
3. `docs/specs/2026-05-04-dev-ai-stage-1-simple-beta-design.md` — dev-AI Stage-1 spec; ground truth for §6.2.
4. `memory/project_pair_d_phase2_pass.md` — Pair D PASS verdict + four RC FLAGs to inherit.
5. `memory/project_fx_vol_econ_gate_verdict_and_product_read.md` — FX-vol FAIL gate verdict + pivot paths.
6. `memory/project_fx_vol_cpi_notebook_complete.md` — FX-vol-CPI notebook detail.
7. `memory/project_phase_a0_exit_verdict.md` — Phase-A.0 EXIT verdict.
8. `memory/project_no_mento_carbon_protocol_integration.md` — Rev-5.3.7 retraction (load-bearing for §6.4).
9. `memory/project_p1_sn18_spec_parked_for_record.md` — P1 PARKED.
10. `CLAUDE.md` — anti-fishing invariants.
11. `~/.claude/skills/structural-econometrics/SKILL.md` — your discipline source.

## What to produce

A single LaTeX file (`agent-output-data.tex`) with FOUR top-level blocks corresponding to §5 / §6 / App C / App D, each surrounded by HTML-style start/end markers so the main thread can splice cleanly:

```latex
% === BEGIN SECTION 5 ===
[methodology section content]
% === END SECTION 5 ===

% === BEGIN SECTION 6 ===
[log section content]
% === END SECTION 6 ===

% === BEGIN APPENDIX C ===
[Pair D verdict header artifact]
% === END APPENDIX C ===

% === BEGIN APPENDIX D ===
[power-calculation transparency table]
% === END APPENDIX D ===
```

PLUS a citation sub-list in BibTeX format at `scratch/2026-05-06-supervisor-review/citations-data.bib`. Cite using `\cite{key}`; the main thread will dedupe across all three agents at Task 6.

## Spec-bound constraints (from spec §5 anti-overclaim invariants)

These bind your prose word-for-word. Do not negotiate around them.

1. **No code, no Python, no SQL, no Solidity, no fetcher walkthroughs.** Methodology is described in math + words.
2. **Pair D is correlation-identified, not BPO-causally-identified.** Hedge accordingly. Inherit all four RC FLAGs in §6.1, including FLAG #5 (verdict-sensitivity-to-design-decision off-spec orchestrator-brief sensitivity test).
3. **FX-vol-CPI is FAIL on the pre-registered weekly primary.** Do NOT call A1 monthly the "main finding". The A1 / A4 sensitivities are "pre-registered robustness checks that produced positive-significance at 90% CI", not "the result".
4. **No Carbon-DeFi as Mento-native demand language.** Use the §6.4 framing in the design spec verbatim — the 2026-04-24 attribution was retracted on 2026-04-27 via `project_no_mento_carbon_protocol_integration.md` Rev-5.3.7.
5. **Cross-iteration FWER posture.** Do NOT present the 5 iterations as if independent. Flag iteration-selection as a meta-multiple-comparison concern; cross-reference §7.5.
6. **Power-calculation transparency.** App D presents per-iteration back-of-the-envelope power derivation (Hansen 2022 §6.18 method with HAC-corrected effective-sample-size adjustment); cells where derivation is infeasible at writing time are flagged "inherited from Phase-A.0 Rev-5.3.1, not re-derived" and cross-referenced to §7.4 supervisor-ask. Do NOT fabricate power numbers; if you do not have enough information to derive, say so explicitly.
7. **HAC lag-truncation rule is fixed-integer per iteration**, NOT `T^{1/3}`. Pair D / dev-AI use `L = 12`; FX-vol-CPI primary uses `L = 4`. Automatic-selection rules are explicitly NOT used.
8. **Primary inference is OLS-homoskedastic SE**; HAC is R4 robustness. Headlines report the more conservative of OLS-SE and HAC-SE wherever the verdict is invariant. State this explicitly in §5.3.
9. **Verdict-mapping Clause B numerics:** `|β/SE| < 0.5` AND (`|skew(residuals)| > 1.0` OR `excess kurtosis(residuals) > 3.0`). Pin in §5.6.
10. **Each §6 iteration block uses the 9-field schema** from spec §3.6: target population, (Y, X) pair, sign+lit anchor, primary spec, sample, verdict, headlines, key caveats, pre-registration sha256 chain.

## Style discipline

- Formal academic English; first-person plural ("we"); past-tense for closed iterations; present-tense for the framework.
- **Math typesetting (load-bearing per LaTeX-research recon 2026-05-06):**
  - Inline math: `\(...\)` ONLY. Do NOT use bare `$...$`. Do NOT use unicode characters for mathematical symbols. Replace any unicode β / σ / ρ / α / Σ / ∈ / ≤ / ≥ / ≠ / · / × / ⊂ / ⊆ / ∩ / ∪ / ∀ / ∃ that you would otherwise emit with the corresponding LaTeX macro inside `\(...\)` (e.g., `\(\beta\)`, `\(\sigma^2\)`, `\(\rho\)`, `\(\Sigma\)`, `\(\in\)`, `\(\leq\)`, `\(\subset\)`).
  - Display math: `\[...\]` or the `equation` / `align` environments (NOT bare `$$...$$`).
  - Econometric notation: estimators use `\hat{\cdot}` (e.g., `\(\hat{\beta}\)`); estimated variances use `\widehat{\mathrm{Var}}`; expectations use `\mathbb{E}`; probability limits use `\mathrm{plim}`; convergence in distribution `\xrightarrow{d}`; convergence in probability `\xrightarrow{p}`. Sub-/super-scripts on Greek letters use braces (`\(\beta_{\text{composite}}\)` not `\(\beta_composite\)`).
  - Numbered equations inside §5 / §6 use `\begin{equation}\label{eq:...}\end{equation}` so they can be cross-referenced.
  - Final pass: re-read your output and replace every remaining unicode math character with the LaTeX macro. This is the highest-priority typesetting discipline; the supervisor will read inconsistent math notation as undisciplined.
- Tables: `booktabs`. NO vertical rules.
- Code-snippet voice (e.g. "the script applies...", "the notebook reports...") is BANNED. The supervisor does not have programming background. Phrase as "the analysis reports...", "the estimation produces...".
- Citations: `\cite{key}` for parenthetical, `\citet{key}` for textual ("Hansen \citet{hansen2022}"), `\citep{key}` for explicit parenthetical. Plain `natbib` macros only — do NOT use `\autocite` or other biblatex-specific commands.

## Anti-overreach

You are NOT the main thread. Your output is one of three inputs that get stitched together. Do not reproduce sections you are not assigned (no §1, no §2, no §3, no §4, no §7, no §8, no App A, no App B). Do not write the preamble. Do not write `\maketitle` or `\tableofcontents`. **Do NOT emit your own `\section{Cited Literature}` for App B** — App B is assembled by the main thread from the three citation sub-lists; your job is just to populate `citations-data.bib`.

If you have questions about scope or framing, surface them in a `## Author notes` block at the end of `agent-output-data.tex` rather than guessing — the main thread will adjudicate at composition time.
````

- [ ] **Step 2: Write `brief-onchain-explainer.md`**

Write the brief verbatim:

````markdown
# Section-Author Brief — On-Chain Explainer

**Sub-agent type:** `Technical Writer`
**Output sections:** §4 (and the on-chain half of App A glossary)
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-onchain.tex`
**Citation file:** `scratch/2026-05-06-supervisor-review/citations-onchain.bib`
**Length budget:** §4 ~4 pp + App A on-chain half ~1 pp ≈ 5 pp; soft ±10% latitude.

## Source materials (read in full before drafting)

1. `docs/specs/2026-05-06-supervisor-review-document-design.md` — your binding spec; especially §3.4, §3.9 App A on-chain half, §5 anti-overclaim invariants.
2. `memory/project_no_mento_carbon_protocol_integration.md` — Mento V3 manifest verification (Rev-5.3.7) — load-bearing for the Mento section.
3. `memory/project_mento_canonical_naming_2026.md` — Mento basket canonical naming.
4. `memory/project_abrigo_inequality_hedge_thesis.md` — context on why on-chain matters to the framework.
5. Mento V3 deployment manifest (web): https://docs.mento.org/mento-v3/build/deployments/addresses.md
6. Panoptic public docs (web; cite specific pages used).
7. `/home/jmsbpp/apps/liq-soldk-dev/notes/MACRO_RISKS/` — research corpus referenced in Appendix B; not for Section 4 prose, but useful for understanding what the framework treats as "macro risk."

## Audience

The reader is a senior econometrician with no programming or on-chain background. He understands financial derivatives in their traditional form (futures, options, swaps, perpetuals), is comfortable with continuous-time stochastic processes, and reads Stock-Watson 2019 / Hansen 2022 fluently. He does NOT understand Solidity, will not be reading source code, and should not be exposed to terminology like "smart contract," "ABI," "calldata," or "EIP-712" — translate any necessary on-chain concept to its traditional-finance analogue.

## What to produce

A single LaTeX file (`agent-output-onchain.tex`) with TWO top-level blocks:

```latex
% === BEGIN SECTION 4 ===
[on-chain primer content]
% === END SECTION 4 ===

% === BEGIN APPENDIX A — ON-CHAIN HALF ===
[on-chain glossary entries — to be merged with Econ-Writer's econometric half]
% === END APPENDIX A — ON-CHAIN HALF ===
```

PLUS a citation sub-list at `citations-onchain.bib` (web sources cite as `@misc` with `note = {Accessed 2026-05-06}`; document URLs).

## Required topics in §4 (per spec §3.4)

1. **What "on-chain" means** — programmable settlement on a public ledger; analogue to a clearinghouse with public, verifiable, programmable rule-set.
2. **Panoptic protocol** — perpetual options written on Uniswap V3/V4 LP positions. Analogue: a perpetual-future-on-options instrument where the option strike is encoded as the price range of a market-making position. Describe the payoff geometry and what makes it a convex instrument; do NOT describe Solidity implementation.
3. **Mento purchasing-parity stablecoins** (COPm, BRLm, KESm, EURm, USDm) — digital country-currency-pegged claims with on-chain reserve-backed pegs. Crucial empirical point: a hedge denominated in COPm settles in the user's *consumption currency*, not USD — purchasing-parity preserving by construction. Cite the Mento V3 manifest URL for the StableToken roster (12 currencies).
4. **Political-receptivity context** — Trump-Petro tariff standoff Jan 2025 → +100% Littio USDC user-account-growth spike per `OFFCHAIN_COP_BEHAVIOR.md`. This is a USER-side responsiveness signal, not a presidential transaction. Anecdotal frame, NOT load-bearing for any empirical or methodological claim.
5. **Critical disclaimer (load-bearing).** β-validation work is *independent* of on-chain deployment. Off-chain DANE, Banrep, GEIH data drive estimation. On-chain provides settlement venue. The supervisor's review concerns the econometrics; on-chain content is contextual, not evidentiary.

## Required closing pattern

End §4 with a four-bullet reader-takeaway list (per spec §3.4):
1. On-chain options exist and are tradable today (Panoptic).
2. Purchasing-parity stablecoin denominations exist (Mento).
3. The empirical work the supervisor is reviewing is off-chain econometrics.
4. The rest of the document does not require on-chain familiarity.

## App A on-chain half

Glossary entries with traditional-finance analogues. Required terms: `Panoptic`, `Mento`, `purchasing-parity stablecoin`, `Uniswap V3/V4 LP position`, `perpetual option (on-chain)`, `on-chain settlement`, `programmable rule-set`, `reserve-backed peg`, `Mento Broker`, `Carbon DeFi (excluded — third-party DEX, NOT Mento-native)`. One-line definition + one-line traditional-finance analogue per term.

## Spec-bound constraints (from spec §5 anti-overclaim invariants)

1. **No "Carbon-DeFi as Mento-native demand" language.** Carbon DeFi has no protocol-level integration with Mento per `project_no_mento_carbon_protocol_integration.md` Rev-5.3.7. If you mention Carbon at all, frame it as "third-party DEX activity, NOT Mento Reserve user demand."
2. **No "Colombian president has publicly transacted on-chain"** language. The political-receptivity claim is the Trump-Petro 2025 / Littio user-side spike — sourced — not a presidential transaction.
3. **No marketing copy.** No "Abrigo as product" framing. The on-chain content is contextual, not promotional.
4. **No code, no Solidity, no Python, no walkthrough of any data fetcher.**
5. **No promises about Stage-2 / Stage-3 deployment timelines.**

## Style discipline

- Formal academic English; first-person plural; past-tense for the political-receptivity context; present-tense for the protocol descriptions (Panoptic / Mento are deployed and operating).
- Translate every on-chain concept to its traditional-finance analogue at first introduction.
- **Math typesetting (load-bearing per LaTeX-research recon 2026-05-06):**
  - If §4 contains any math (e.g., describing Panoptic payoff geometry), use `\(...\)` for inline and `\[...\]` for display. NO bare `$...$`. NO unicode math characters — replace with LaTeX macros.
  - Stablecoin notation: write `\textsc{copm}` / `\textsc{brlm}` / `\textsc{usdm}` (small caps) for the token tickers, NOT bare `COPm` mid-prose.
- Tables: `booktabs`. NO vertical rules.
- If a term is on-chain-specific and has no traditional-finance analogue, define it in two lines maximum and move on.
- Citations: `\cite{key}` / `\citet{key}` / `\citep{key}` (plain natbib only — NOT biblatex `\autocite`).

## Anti-overreach

You are NOT writing the empirical methodology, the iteration log, the Lemma, or the supervisor questions. Stay inside §4 and the on-chain half of Appendix A. **Do NOT emit a `\section{Glossary}` line in your App-A on-chain output** — the main thread (Task 5 step 9) writes the glossary header; you provide only the on-chain entries themselves (e.g., `\item[Panoptic] ...`). Do NOT emit `\section{Cited Literature}` for App B — main thread assembles App B from the three sub-lists.
````

- [ ] **Step 3: Write `brief-econ-writer.md`**

Write the brief verbatim:

````markdown
# Section-Author Brief — Econometric Writer

**Sub-agent type:** `Book Co-Author`
**Output sections:** §1, §2, §3, §7, §8, App A econometric half (per spec §3 table + §4 multi-agent table)
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-econ.tex`
**Citation file:** `scratch/2026-05-06-supervisor-review/citations-econ.bib`
**Length budget:** §1 ~3 pp + §2 ~3 pp + §3 ~2 pp + §7 ~5 pp + §8 ~1 p + App A econ half ~1 pp ≈ 15 pp; soft ±10% latitude.

## Source materials (read in full before drafting)

1. `docs/specs/2026-05-06-supervisor-review-document-design.md` — your binding spec; especially §3.1, §3.2, §3.3, §3.7, §3.8, §3.9 App A econ half, §5 anti-overclaim invariants.
2. `CLAUDE.md` — Abrigo Operating Framework; (Y, M, X) triple definition; anti-fishing invariants.
3. `memory/project_abrigo_inequality_hedge_thesis.md` — load-bearing for §3 Lemma derivation.
4. `memory/project_abrigo_convex_instruments_inequality.md` — load-bearing for §7.2 convex-payoff sufficiency ask.
5. `memory/project_pair_d_phase2_pass.md` — context for §7.1 identification ask (T1 exogeneity rejected).
6. `memory/project_fx_vol_econ_gate_verdict_and_product_read.md` — context for §7.1 predictive-vs-causal framing.
7. `memory/MEMORY.md` — high-level memory index.

## Audience

The reader is a senior econometrician with neoclassical / neoliberal training. He is comfortable with HAC, OLS, GARCH, IV, panel methods, and reads Hansen 2022 / Stock-Watson 2019 / Kilian-Lütkepohl 2017 / Wooldridge 2010. He does NOT have programming background. He has not seen the Abrigo framework before this letter; he is supervising the analytics work and is being asked for guidance.

## What to produce

A single LaTeX file (`agent-output-econ.tex`) with SIX top-level blocks (one per assigned section):

```latex
% === BEGIN SECTION 1 ===
[introduction & economic motivation]
% === END SECTION 1 ===

% === BEGIN SECTION 2 ===
[operating framework — (Y, M, X) triple]
% === END SECTION 2 ===

% === BEGIN SECTION 3 ===
[Abrigo Lemma]
% === END SECTION 3 ===

% === BEGIN SECTION 7 ===
[open methodological questions]
% === END SECTION 7 ===

% === BEGIN SECTION 8 ===
[request for guidelines]
% === END SECTION 8 ===

% === BEGIN APPENDIX A — ECON HALF ===
[econometric glossary — to be merged with On-Chain Explainer's on-chain half]
% === END APPENDIX A — ECON HALF ===
```

PLUS a citation sub-list at `citations-econ.bib`.

## Required content per assigned section

### §1 Introduction & Economic Motivation (~3 pp)

Per spec §3.1. Frame inequality as institutionally-determined, empirically-measurable wealth-distribution gap. Acknowledge post-Keynesian intellectual origin in one sentence; do NOT litigate against the supervisor's neoclassical lens. Introduce the wage→capital boundary as a documented friction (cite Mendieta-Muñoz 2017, Rodrik 2016, McMillan-Rodrik 2011 NBER WP 17143). State the project goal: identify macro risks `X` blocking the wage→capital transition for specific populations + validate empirically. Close with a forward pointer to §2.

### §2 Operating Framework — The (Y, M, X) Triple (~3 pp)

Per spec §3.2. Define `Y`, `X`, `M`. Stage discipline (validation FIRST, M-design SECOND, deployment LAST). Iteration order: target-population dominant. Reproduce relevant `CLAUDE.md` "Abrigo Operating Framework" prose with on-chain operational details elided (those are §4's job).

### §3 The Abrigo Lemma (~2 pp)

Per spec §3.3. Use a `lemma` environment for the formal proposition. State it as a *proposition motivating the iteration design*, NOT as a proven theorem (this is a §5 anti-overclaim invariant). Discussion: why single-aggregate hedges (CPI alone, TRM alone) fail; two-sided market existence (working-class LONG, capital-holders naturally SHORT via existing positions, parametric-insurance counterparty matching per Carter et al. 2017 *World Development*); continuous-time differential as a stochastic process whose calibration is deferred to §7.3.

### §7 Open Methodological Questions for Supervisor Review (~5 pp)

Per spec §3.7. Five sub-asks in priority order:
- §7.1 Identification (predictive-regression vs causal; IV / event-study / structural VAR; cite Hansen 2022 §6/§12, Kilian-Lütkepohl 2017, Wooldridge 2010).
- §7.2 Convex-payoff sufficiency (mean-β necessary not sufficient; distributional / GARCH-X / EVT extensions; cite Engle 2002 *JBES* DCC, Embrechts-Klüppelberg-Mikosch 1997 EVT).
- §7.3 Multi-Y differential calibration (joint-leg correlation, FWER vs SDR, regime-switching; cite Engle 2002 DCC again).
- §7.4 Anti-fishing protocol defensibility (`N_MIN=75`, `POWER_MIN=0.80`, `MDES_SD=0.40` SD; cite Olken 2015 *J Econ Perspectives*, Christensen-Miguel 2018 *J Econ Lit*; cross-reference Appendix D).
- §7.5 Cross-iteration FWER and iteration-selection bias (added on Wave-2 FLAG-F6 closure; question is meta-multiple-comparison correction across 5 iterations + iteration-selection-bias mitigation).

### §8 Request for Guidelines (~1 p)

Per spec §3.8. Short closing. Explicit request for the supervisor's recommended priority ordering across §7.1–§7.5 and (where applicable) thresholds. Frame so the response is actionable (e.g. "we will adopt `N_MIN = X` based on the supervisor's recommendation"). NO implicit promises about the supervisor's response.

### Appendix A econometric half (~1 p)

Glossary entries: HAC (Newey-West), composite-β, MDES, FWER, SDR, structural VAR, predictive regression, Granger causality, DCC-MGARCH, EVT POT, quantile regression, pre-analysis plan, MDES_SD, R-row, ESCALATE Clause A/B, SUBSTRATE_TOO_NOISY. One-line definition each.

## Spec-bound constraints (from spec §5 anti-overclaim invariants)

1. **No "Abrigo as product" framing.** Abrigo appears as the operating-framework context that explains why these iterations exist, not as a brand being sold.
2. **No marketing register.** No "10x better," no "painkiller-not-vitamin," no "premium-funded ratchet" sales framing. The reader is your supervisor, not a customer.
3. **The Abrigo Lemma is a proposition, NOT a proven theorem.** Repeat the disclaimer in §3 prose immediately after the proposition box.
4. **No code, no Python, no Solidity, no fetcher walkthroughs.**
5. **Cross-iteration FWER posture in §1.** Acknowledge in §1 that the project has run 5 iterations and that cross-iteration FWER / iteration-selection-bias is an open methodological question — cross-reference §7.5. The §1 narrative MUST NOT present the 5 verdicts as if pre-iteration-selection independence held.
6. **Power-calculation transparency in §7.4.** The thresholds are inherited from Phase-A.0 Rev-5.3.1 and have NOT been re-derived per iteration; cross-reference Appendix D and §5.2.
7. **No "Colombian president has publicly transacted on-chain"** language anywhere. (This is an On-Chain-Explainer §4 concern, but if §1 / §2 prose strays into political-receptivity territory, follow §4's framing — Trump-Petro 2025 / Littio user-side spike.)

## Style discipline

- Formal academic English; first-person plural; past-tense for closed iterations; present-tense for the framework; future-tense only inside §7.
- The Lemma uses a `lemma` environment (declared in `preamble.tex`).
- **Math typesetting (load-bearing per LaTeX-research recon 2026-05-06):**
  - Inline: `\(...\)` ONLY. NO bare `$...$`. NO unicode math characters (β / σ / ρ / α / Σ / ∈ / ≤ / ≥ etc.) — replace with LaTeX macros (`\(\beta\)`, `\(\sigma\)`, `\(\rho\)`, `\(\alpha\)`, `\(\Sigma\)`, `\(\in\)`, `\(\leq\)`).
  - Display: `\[...\]` or `equation` / `align` environments. NO bare `$$...$$`.
  - The Lemma's `Y_inequality(t) = R_a(t) - R_c(t)` displays inside the `lemma` environment as `\[Y_{\text{inequality}}(t) = R_a(t) - R_c(t)\]` — sub-script uses `\text{}`, the difference operator uses `-` (LaTeX hyphen-minus, NOT unicode minus).
  - Estimators: `\hat{\beta}`; expectations: `\mathbb{E}`; probability limits: `\mathrm{plim}`; convergence: `\xrightarrow{d}` / `\xrightarrow{p}`.
  - Final pass: re-read every section and replace any remaining unicode math character with its LaTeX macro.
- Citations: `\cite{key}` / `\citet{key}` / `\citep{key}` — plain `natbib` only. BibTeX entries in `citations-econ.bib`.
- Tables: `booktabs`. NO vertical rules.

## Anti-overreach

You are NOT writing the on-chain primer (§4), the empirical methodology (§5), the iteration log (§6), Appendix C (Pair D verdict header), or Appendix D (power-calculation table). Stay inside your assigned sections. **Do NOT emit a `\section{Glossary}` line in your App-A econ output** — the main thread (Task 5 step 9) writes the glossary header and the `\subsection*{Econometric terms}` break; you provide only the econ entries themselves (e.g., `\item[HAC (Newey-West)] ...`). Do NOT emit `\section{Cited Literature}` for App B — main thread assembles App B from the three sub-lists.
````

- [ ] **Step 4: Verify briefs are well-formed**

Run:

```bash
ls -la /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review/
wc -l /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review/brief-*.md
```

Expected: three files (`brief-data-methodology.md`, `brief-onchain-explainer.md`, `brief-econ-writer.md`); each ~100-200 lines.

- [ ] **Step 5: No commit (briefs live in `scratch/`)**

Per `feedback_two_wave_doc_verification` "Out of scope" rule, scratch files are not subject to the verification pipeline; they are also not committed to the main tree. Briefs are preserved on disk for the duration of the implementation; they will be referenced in the final-commit message footer at Task 9 for audit traceability.

---

### Task 4: Dispatch the three section-author agents in parallel

**Files (created by sub-agents):**
- `scratch/2026-05-06-supervisor-review/agent-output-data.tex` (Model QA Specialist)
- `scratch/2026-05-06-supervisor-review/agent-output-onchain.tex` (Technical Writer)
- `scratch/2026-05-06-supervisor-review/agent-output-econ.tex` (Book Co-Author)
- `scratch/2026-05-06-supervisor-review/citations-data.bib`
- `scratch/2026-05-06-supervisor-review/citations-onchain.bib`
- `scratch/2026-05-06-supervisor-review/citations-econ.bib`

- [ ] **Step 1: Dispatch all three agents in a single message (parallel)**

Use the `Agent` tool with three calls in one message. Each prompt is the entire contents of the corresponding brief from Task 3, plus a one-line opening: "You are the [role] sub-agent dispatched per the implementation plan at docs/plans/2026-05-06-supervisor-review-document-implementation.md Task 4."

Agent 1 (`Model QA Specialist`):
- description: "Author §5+§6+App C+App D LaTeX"
- subagent_type: `Model QA Specialist`
- prompt: contents of `scratch/2026-05-06-supervisor-review/brief-data-methodology.md`

Agent 2 (`Technical Writer`):
- description: "Author §4+App A on-chain LaTeX"
- subagent_type: `Technical Writer`
- prompt: contents of `scratch/2026-05-06-supervisor-review/brief-onchain-explainer.md`

Agent 3 (`Book Co-Author`):
- description: "Author §1+§2+§3+§7+§8+App A econ LaTeX"
- subagent_type: `Book Co-Author`
- prompt: contents of `scratch/2026-05-06-supervisor-review/brief-econ-writer.md`

Expected: each agent reports completion and writes its output files to `scratch/2026-05-06-supervisor-review/`.

- [ ] **Step 2: Verify all six expected agent-output files exist**

Run:

```bash
ls -la /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review/
```

Expected: 9 files total — 3 briefs from Task 3 + 3 `.tex` outputs + 3 `.bib` outputs.

If any file is missing, re-dispatch with selective-retry discipline (per Wave-2 PM FLAG-MED on Task 4): the retry agent writes ONLY the missing file(s) to a new path `agent-output-<role>-retry.tex` (or `citations-<role>-retry.bib`); the main thread merges the retry output into the canonical filename only after verifying the retry output. Retry prompt prepends:

> "Your previous dispatch did not produce `<filename>` (or produced it malformed). Please re-author ONLY the missing block(s); write to `<role>-retry.tex` and `<role>-retry.bib`. Do not re-emit blocks that were already produced correctly. List which blocks you are re-authoring at the top of your retry file."

Iteration cap: at most 2 retries per agent. After the second failure, halt and report to user.

- [ ] **Step 3: Smoke-test each agent output for the BEGIN/END markers**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review
echo "data: $(grep -c '% === BEGIN' agent-output-data.tex) (expected 4)"
echo "onchain: $(grep -c '% === BEGIN' agent-output-onchain.tex) (expected 2)"
echo "econ: $(grep -c '% === BEGIN' agent-output-econ.tex) (expected 6)"
echo "data END: $(grep -c '% === END' agent-output-data.tex) (expected 4)"
echo "onchain END: $(grep -c '% === END' agent-output-onchain.tex) (expected 2)"
echo "econ END: $(grep -c '% === END' agent-output-econ.tex) (expected 6)"
```

Expected: every line shows actual count matching expected count. BEGIN and END counts must match within each file (every BEGIN paired with an END).

If any count is off, the agent did not respect the brief's BEGIN/END envelope contract. Trigger a partial-block selective retry (per Wave-2 PM FLAG-MED): identify which specific sections are missing or malformed, and re-dispatch with the retry-prompt template from Step 2 listing only those sections.

- [ ] **Step 3b: Smoke-test math typesetting (per LaTeX-research recon)**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review
# Look for unicode math characters that should have been LaTeX macros
grep -nE '[βσραΣ∈≤≥≠⊂⊆∩∪∀∃]' agent-output-*.tex | head -20 || echo "OK: no unicode math characters"
# Look for bare $...$ (should be \(...\))
grep -nE '\$[^$]+\$' agent-output-*.tex | head -10 || echo "OK: no bare dollar math"
# Look for biblatex-specific commands that shouldn't appear (preamble is natbib)
grep -nE '\\autocite|\\textcite|\\printbibliography' agent-output-*.tex && echo "FAIL: biblatex command found" || echo "OK: no biblatex commands"
```

Expected: all three checks return `OK:` lines. If any check fails, the offending agent did not honour the math-typesetting style discipline; re-dispatch with the retry-prompt template plus an additional instruction listing the specific characters / commands found.

- [ ] **Step 4: No commit (agent outputs live in `scratch/`)**

---

### Task 5: Stitch agent outputs into section files

**Files modified:**
- `docs/supervisor-review/sections/01-introduction.tex` through `appD-power-calculation.tex` (all 12 stub files replaced with actual content)

**Parallelism note (per Wave-2 PM FLAG-LOW).** Steps 1–11 below operate on independent file paths and can be issued in parallel as a single batch of `Read` + `Write` calls. Sequential ordering is shown for readability; the executor may dispatch them in parallel for ~3-5× wall-clock savings.

For each section file, replace the stub with the corresponding BEGIN/END block extracted from the agent output. The 12-to-3 mapping:

| Section file | Source agent output | BEGIN/END marker |
|---|---|---|
| `01-introduction.tex` | `agent-output-econ.tex` | `% === BEGIN SECTION 1 ===` |
| `02-framework.tex` | `agent-output-econ.tex` | `% === BEGIN SECTION 2 ===` |
| `03-lemma.tex` | `agent-output-econ.tex` | `% === BEGIN SECTION 3 ===` |
| `04-onchain-primer.tex` | `agent-output-onchain.tex` | `% === BEGIN SECTION 4 ===` |
| `05-methodology.tex` | `agent-output-data.tex` | `% === BEGIN SECTION 5 ===` |
| `06-log.tex` | `agent-output-data.tex` | `% === BEGIN SECTION 6 ===` |
| `07-questions.tex` | `agent-output-econ.tex` | `% === BEGIN SECTION 7 ===` |
| `08-request.tex` | `agent-output-econ.tex` | `% === BEGIN SECTION 8 ===` |
| `appA-glossary.tex` | both `agent-output-econ.tex` (econ half) + `agent-output-onchain.tex` (on-chain half) | `% === BEGIN APPENDIX A — ECON HALF ===` and `% === BEGIN APPENDIX A — ON-CHAIN HALF ===` |
| `appB-bibliography.tex` | (already correct from Task 2 — `\printbibliography`) | n/a |
| `appC-pair-d-verdict-header.tex` | `agent-output-data.tex` | `% === BEGIN APPENDIX C ===` |
| `appD-power-calculation.tex` | `agent-output-data.tex` | `% === BEGIN APPENDIX D ===` |

- [ ] **Step 1: Extract Section 1 from `agent-output-econ.tex` into `01-introduction.tex`**

Read `scratch/2026-05-06-supervisor-review/agent-output-econ.tex`. Locate the line `% === BEGIN SECTION 1 ===` and the matching `% === END SECTION 1 ===`. Copy the content STRICTLY between those markers (excluding the markers themselves) into `docs/supervisor-review/sections/01-introduction.tex`, REPLACING the stub line. The new file content opens with `\section{Introduction \& Economic Motivation}\label{sec:1}` (already present in the agent output).

Run:

```bash
head -3 /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/sections/01-introduction.tex
```

Expected: first non-blank line is `\section{Introduction \& Economic Motivation}\label{sec:1}`.

- [ ] **Step 2: Repeat for Section 2 → `02-framework.tex`**

Same procedure. Extract `% === BEGIN SECTION 2 ===` block from `agent-output-econ.tex` into `02-framework.tex`.

- [ ] **Step 3: Repeat for Section 3 → `03-lemma.tex`**

Same procedure.

- [ ] **Step 4: Repeat for Section 4 → `04-onchain-primer.tex`**

Source: `agent-output-onchain.tex`. Extract the `% === BEGIN SECTION 4 ===` block.

- [ ] **Step 5: Repeat for Section 5 → `05-methodology.tex`**

Source: `agent-output-data.tex`. Extract `% === BEGIN SECTION 5 ===` block.

- [ ] **Step 6: Repeat for Section 6 → `06-log.tex`**

Source: `agent-output-data.tex`. Extract `% === BEGIN SECTION 6 ===` block.

- [ ] **Step 7: Repeat for Section 7 → `07-questions.tex`**

Source: `agent-output-econ.tex`. Extract `% === BEGIN SECTION 7 ===` block.

- [ ] **Step 8: Repeat for Section 8 → `08-request.tex`**

Source: `agent-output-econ.tex`. Extract `% === BEGIN SECTION 8 ===` block.

- [ ] **Step 9a: Write the App-A glossary section header**

Write `docs/supervisor-review/sections/appA-glossary.tex` with content:

```latex
\section{Glossary}\label{app:A}

\subsection*{Econometric terms}
```

This is a fresh write replacing the Task-2 stub.

- [ ] **Step 9b: Append the econ-half glossary entries**

Read `scratch/2026-05-06-supervisor-review/agent-output-econ.tex`. Locate `% === BEGIN APPENDIX A — ECON HALF ===` and the matching `% === END APPENDIX A — ECON HALF ===`. Copy the content STRICTLY between those markers (excluding the markers; the brief instructed the agent NOT to emit `\section{Glossary}` itself, so the content should be glossary entries directly — typically a `description` list with `\item[term] definition` rows). Append to `appA-glossary.tex`.

If the agent did emit a `\section{Glossary}` line in violation of the brief, strip it before appending.

- [ ] **Step 9c: Append the on-chain subsection break**

Append to `appA-glossary.tex`:

```latex

\subsection*{On-chain terms}
```

- [ ] **Step 9d: Append the on-chain-half glossary entries**

Read `scratch/2026-05-06-supervisor-review/agent-output-onchain.tex`. Locate `% === BEGIN APPENDIX A — ON-CHAIN HALF ===` and the matching `% === END APPENDIX A — ON-CHAIN HALF ===`. Same extraction discipline as 9b. Append to `appA-glossary.tex`.

- [ ] **Step 10: Repeat for App C → `appC-pair-d-verdict-header.tex`**

Source: `agent-output-data.tex`. Extract `% === BEGIN APPENDIX C ===` block.

- [ ] **Step 11: Repeat for App D → `appD-power-calculation.tex`**

Source: `agent-output-data.tex`. Extract `% === BEGIN APPENDIX D ===` block.

- [ ] **Step 12: Verify all section files now have actual content (no `TBD`)**

```bash
grep -L "TBD" /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/sections/*.tex
```

Expected: all 12 files printed (i.e., none of them contain `TBD` — `grep -L` lists files NOT matching). If any file still has `TBD`, re-do the extract step for that file.

- [ ] **Step 13: Commit Task 5**

```bash
git add docs/supervisor-review/sections/
git commit -m "feat: stitch sub-agent section drafts into supervisor-review document

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Merge and deduplicate the three citation sub-lists into `refs.bib`

**Files modified:**
- `docs/supervisor-review/refs.bib` (replaces stub from Task 2)

- [ ] **Step 1: Concatenate the three citation sub-lists**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review
cat citations-data.bib citations-onchain.bib citations-econ.bib > merged-pre-dedupe.bib
wc -l merged-pre-dedupe.bib
```

- [ ] **Step 2: Deduplicate by citation key**

Read `merged-pre-dedupe.bib`. For each `@type{key,` block, if `key` has already appeared, drop the duplicate; if it has not appeared, keep it. Manual deduplication is acceptable for a file with < 50 citations; a quick Python script is also acceptable. Write the deduplicated output to `docs/supervisor-review/refs.bib`, REPLACING the stub.

```bash
cd /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review
grep -c "^@" merged-pre-dedupe.bib
grep -c "^@" /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/refs.bib
```

Expected: `refs.bib` has fewer entries than `merged-pre-dedupe.bib` (some citations like Hansen 2022 may be cited by both Data-Methodology and Econ-Writer; Mendieta-Muñoz 2017 may appear in multiple sub-lists).

- [ ] **Step 3: Verify all `\cite{key}` / `\citet{key}` / `\citep{key}` references in section files resolve to a `refs.bib` entry**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review
grep -hoE '\\cite[tp]?\{[^}]+\}' sections/*.tex | sed 's/\\cite[tp]\?{//; s/}//' | tr ',' '\n' | sed 's/^ *//; s/ *$//' | sort -u > /tmp/cited-keys.txt
grep -oE '^@[a-z]+\{[^,]+' refs.bib | sed 's/^@[a-z]\+{//' | sort -u > /tmp/bib-keys.txt
echo "cited but not in refs.bib (must be empty):"
comm -23 /tmp/cited-keys.txt /tmp/bib-keys.txt
echo "in refs.bib but not cited (info only — uncited entries are OK):"
comm -13 /tmp/cited-keys.txt /tmp/bib-keys.txt
```

Expected: the first `comm -23` block produces no output (every cited key has a corresponding bib entry). The second `comm -13` block may have entries (uncited `refs.bib` entries are non-fatal). The `diff`-based check used in earlier drafts of this plan was replaced with `comm -23` per Wave-1 RC FLAG-MED on direction-asymmetry. If a cited key is missing from `refs.bib`, the agent who introduced the cite did not include the BibTeX entry; either request the entry from the agent or add it manually with explicit `@misc{key, note = {Citation introduced by agent X; entry reconstructed by main thread on 2026-05-06}}` provenance.

- [ ] **Step 4: Commit Task 6**

```bash
git add docs/supervisor-review/refs.bib
git commit -m "feat: merge + deduplicate three sub-agent BibTeX sub-lists into refs.bib

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Compile + smoke-test the assembled PDF

**Files (build outputs):**
- `docs/supervisor-review/2026-05-06-empirical-record-letter.pdf` (committed)
- `docs/supervisor-review/main.{aux,log,bbl,blg,toc,out}` (gitignored)

- [ ] **Step 1: Run the build script**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review && ./build.sh
```

Expected: PDF generated at `2026-05-06-empirical-record-letter.pdf`. The build script runs `pdflatex` → `bibtex` → `pdflatex` → `pdflatex` (LaTeX requires multiple passes for cross-references and bibliography to resolve).

- [ ] **Step 2: Inspect compile log for fatal errors**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review
grep -E "^!|Undefined control sequence|Missing |Runaway|LaTeX Error" main.log | head -20
```

Expected: no output (no fatal errors). Acceptable warnings (do not block):
- "Overfull \hbox" / "Underfull \hbox" — typesetting micro-warnings.
- "Reference `xxx' on page Y undefined" — only on the first `pdflatex` pass; should resolve by the third pass.
- "There were undefined references" — same, resolves on later passes.
- "Citation `xxx' undefined" — should NOT appear after `bibtex` + 2 more passes; if it does, the citation key is missing from `refs.bib` (re-run Task 6 step 3).

- [ ] **Step 3: Verify page count is in target range (decision rule per Wave-2 PM FLAG-MED)**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review
pdfinfo 2026-05-06-empirical-record-letter.pdf | grep Pages
```

Bounded numerical decision rule:

| Page count | Action |
|---|---|
| 30 ≤ N ≤ 40 | **ACCEPT** — within tolerance band of the spec's 32–37 target. Proceed to Step 4. |
| 27 ≤ N < 30 OR 40 < N ≤ 43 | **SOFT RE-DISPATCH** — identify which section is materially off-target (compare against the spec §3 table per-section budget); re-dispatch only the offending agent with an explicit length correction (e.g. "your previous §6 was 4 pp; the budget is 7 pp; please expand the §6.X iteration block(s) flagged below"). One soft retry per agent. After retry, re-run from Task 5 step `<corresponding>`. |
| N < 27 OR N > 43 | **HARD HALT** — material spec deviation; report to user with the actual page count + per-section breakdown. Do NOT proceed to Task 8. User adjudicates whether to accept, re-spec, or re-architect. |

If the page count is in the SOFT RE-DISPATCH band, before retry, identify the offending section by skimming the PDF / counting pages in each `\section` block:

```bash
# Approximate per-section page count via aux-file pageref data
grep '\\newlabel{sec:' main.aux
```

- [ ] **Step 4: Spot-check the table of contents**

Visual check (open the PDF, read the TOC). Expected entries:
1. Introduction & Economic Motivation
2. Operating Framework: The (Y, M, X) Triple
3. The Abrigo Lemma: Inequality Differential as Hedge Target
4. On-Chain Settlement Substrate: Primer for the Non-Specialist Reader
5. Empirical Methodology
6. The Abrigo Log: Record of Closed and Active Iterations
7. Open Methodological Questions for Supervisor Review
8. Request for Guidelines

Plus four appendices (A Glossary, B Cited Literature, C Pair D Verdict Header, D Power-Calculation Transparency Table).

- [ ] **Step 5: Commit Task 7**

```bash
git add docs/supervisor-review/2026-05-06-empirical-record-letter.pdf
git commit -m "docs: compile supervisor-review document v1.0 PDF

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

(Commit prefix `docs:` per project precedent — replaces earlier `build:` per Wave-2 PM NIT.)

---

### Task 8: Two-wave verification on the assembled LaTeX

Per `feedback_two_wave_doc_verification`, governance-level documents under `docs/specs/` and `docs/plans/` require two-wave review before commit. The supervisor-review document is delivered to an external reviewer (the supervisor) and is therefore subject to the spirit of the rule even though it lives under `docs/supervisor-review/` rather than `docs/specs/`. We dispatch a final pass on the assembled document.

**Files (verification outputs):**
- `/tmp/wave1_rc_supervisor_review_assembled.md` (Wave 1 report — not committed)
- `/tmp/wave2_modelqa_supervisor_review_assembled.md` (Wave 2 report — not committed)

- [ ] **Step 1: Dispatch Wave 1 (Reality Checker) and Wave 2 (Model QA Specialist) in parallel**

Use the `Agent` tool with two calls in one message.

**Wave 1 — Reality Checker:**

```
description: "Wave 1 — RC review of assembled LaTeX"
subagent_type: "Reality Checker"
prompt:

You are Wave 1 of the post-assembly two-wave verification per `memory/feedback_two_wave_doc_verification.md`. Your role: catch fantasy / unsupported assertions / fabricated specifics in the FINAL ASSEMBLED LATEX DOCUMENT before final commit.

**Document under review (read in full):**

`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/main.tex`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/sections/*.tex`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/refs.bib`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/2026-05-06-empirical-record-letter.pdf`

**Spec the document is supposed to fulfill:**

`/home/jmsbpp/apps/abrigo-analytics/docs/specs/2026-05-06-supervisor-review-document-design.md` (committed at `f5dcea9`)

**What to check:**

1. Concrete numbers, citations, sha256 references, and status claims trace to source memory/specs (re-do the spot-check from `/tmp/wave1_rc_supervisor_review_design.md` against the assembled prose).
2. The five anti-overclaim invariants from spec §5 hold in prose:
   - No "Carbon-DeFi as Mento-native demand" (§4 + §6.4).
   - No "Colombian president has publicly transacted on-chain" (§4 political-receptivity context).
   - Pair D framed as correlation-not-BPO-causal (§6.1).
   - FX-vol-CPI primary FAIL, A1/A4 as pre-registered sensitivities not "main finding" (§6.3).
   - Abrigo Lemma framed as proposition, not theorem (§3).
3. Cross-iteration FWER posture acknowledged in §1 + §6 (per spec §5 invariant added on Wave-2 FLAG-F6 closure).
4. No code, no Python, no Solidity, no fetcher walkthroughs.
5. Cross-references resolve (every `\ref{sec:X}` and `\ref{app:Y}` points to a real label).

**Findings format:** BLOCK / FLAG / NIT, with file:line references, what's wrong, what's needed to close.

**Output path:** `/tmp/wave1_rc_supervisor_review_assembled.md`. Do not edit the LaTeX directly.

**Anti-overreach.** Do not flag the document for omitting topics that are out-of-scope per spec §8.
```

**Wave 2 — Model QA Specialist + Wave 2-bis — Technical Writer (parallel; per Wave-2 PM FLAG-MED on Wave-2-prompt-scope):**

The assembled document is hybrid: §3 Abrigo Lemma (formal proposition), §4 on-chain primer, §5/§6 econometrics, §7 supervisor-asks, §8 closing. Single-domain Wave-2 review under-covers it. Dispatch BOTH a domain-econometric reviewer (Model QA Specialist) AND a documentation-prose reviewer (Technical Writer) in parallel; they cover complementary surfaces.

**Wave 2 (Model QA Specialist) — econometric correctness:**

```
description: "Wave 2 — Model QA review of assembled LaTeX (econometric domain)"
subagent_type: "Model QA Specialist"
prompt:

You are Wave 2 of the post-assembly two-wave verification per `memory/feedback_two_wave_doc_verification.md`. Your role: econometric domain review of the FINAL ASSEMBLED LATEX DOCUMENT. The Wave 2-bis Technical Writer is reviewing prose / cross-document consistency in parallel; you focus on econometric correctness.

**Document under review (read in full):**

`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/main.tex`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/sections/*.tex`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/refs.bib`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/2026-05-06-empirical-record-letter.pdf`

**Spec:**
`/home/jmsbpp/apps/abrigo-analytics/docs/specs/2026-05-06-supervisor-review-document-design.md` (committed at `f5dcea9`)

**What to check:**

1. §5 methodology summary matches project practice (HAC fixed-L per iteration, primary OLS-SE convention, Clause B numerics, R-row universe).
2. §6 iteration blocks correctly characterise the actual verdict and key caveats per the source memory files (Pair D, dev-AI Stage-1, FX-vol-CPI, Phase-A.0, P1).
3. §7 supervisor-asks are well-posed and non-redundant (§7.1–§7.5).
4. §3 Abrigo Lemma is econometrically defensible.
5. App C Pair D verdict header reproduces the actual sha256 chain accurately.
6. App D power-calculation derivation is methodologically sound (or correctly flagged as inherited-not-re-derived where derivation is infeasible).

**Findings format:** BLOCK / FLAG (HIGH/MED/LOW) / NIT, with file:line references, what's wrong, what's needed to close.

**Output path:** `/tmp/wave2_modelqa_supervisor_review_assembled.md`. Do not edit the LaTeX directly.

**Anti-overreach.** Do not flag the document for omitting topics that are out-of-scope per spec §8.
```

**Wave 2-bis (Technical Writer) — prose, cross-section coherence, math typesetting:**

```
description: "Wave 2-bis — Technical Writer review of assembled LaTeX (prose / typesetting)"
subagent_type: "Technical Writer"
prompt:

You are Wave 2-bis of the post-assembly two-wave verification. Wave 1 RC checks fantasy / unsupported assertions; Wave 2 Model QA checks econometric correctness; YOUR scope is documentation prose, cross-section coherence, audience adaptation, and math typesetting consistency. The reader is a senior econometrician without on-chain or programming background.

**Document under review (read in full):**

`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/main.tex`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/sections/*.tex`
`/home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/2026-05-06-empirical-record-letter.pdf`

**Spec:**
`/home/jmsbpp/apps/abrigo-analytics/docs/specs/2026-05-06-supervisor-review-document-design.md` (committed at `f5dcea9`)

**What to check:**

1. **Math typesetting consistency.** No bare `$...$` (should be `\(...\)`). No unicode math characters (β / σ / ρ / Σ / ∈ / ≤ etc. — should be LaTeX macros). Estimator hats consistent (`\hat{\beta}` not `β̂`). Probability limits `\mathrm{plim}`. Expectations `\mathbb{E}`. Run a grep pass equivalent to Task 4 step 3b across `sections/*.tex`.
2. **Audience-fit.** §4 on-chain primer translates every on-chain concept to a traditional-finance analogue at first introduction. §5/§6 prose avoids code-snippet voice ("the script applies..." → "the analysis reports..."). No Solidity, no Python, no fetcher walkthroughs.
3. **Cross-section coherence.** §1 → §2 → §3 → §4 → §5 → §6 → §7 → §8 narrative arc holds. Forward references (§3 deferring lemma calibration to §7.3; §5.2 forward-referencing §7.4; §6.1 referencing App C; §6 referencing App D) all resolve to actual content in the target section. No contradictions between §1's framing claim and §6's per-iteration headlines.
4. **§4 framing discipline.** No "Abrigo as product" register. Trump-Petro / Littio anecdote framed as user-side responsiveness signal, NOT presidential transaction. No Carbon-DeFi as Mento-native demand language.
5. **Citation rendering.** `\cite{key}` / `\citet{key}` / `\citep{key}` used appropriately; no biblatex commands; bibliography appears correctly in the compiled PDF.
6. **Glossary completeness.** Every on-chain term used in §4 has an entry in App A. Every econometric term used in §5/§6 (HAC, MDES, FWER, SDR, structural VAR, predictive regression, Granger causality, DCC-MGARCH, EVT POT, quantile regression, R-row, ESCALATE Clauses A/B) has an entry in App A.
7. **Cross-iteration FWER posture in prose.** §1 acknowledges the iteration-selection-bias concern with a forward reference to §7.5; §6 iteration log does NOT present the 5 verdicts as if independence held.

**Findings format:** BLOCK / FLAG (HIGH/MED/LOW) / NIT, with file:line references, what's wrong, what's needed to close.

**Output path:** `/tmp/wave2bis_techwriter_supervisor_review_assembled.md`. Do not edit the LaTeX directly.

**Anti-overreach.** Do not flag content under Model QA's domain (econometric correctness of methodology / iteration verdicts / lemma defensibility) — those are Wave 2's findings to make. Do not flag spec §8 out-of-scope omissions.
```

- [ ] **Step 2: Read all three wave reports**

```bash
cat /tmp/wave1_rc_supervisor_review_assembled.md
cat /tmp/wave2_modelqa_supervisor_review_assembled.md
cat /tmp/wave2bis_techwriter_supervisor_review_assembled.md
```

Expected: each report has a verdict line (`ACCEPT_*`) and a finding list.

- [ ] **Step 3: Decision tree**

- If all three verdicts are `ACCEPT` (no FLAGs / no BLOCKs) → proceed to Task 9.
- If verdicts are `ACCEPT_WITH_FLAGS` or `ACCEPT_WITH_REVISIONS` → proceed to Task 9 with the integration sub-task active.
- If any verdict is `BLOCK` → halt the plan, report to user, do NOT proceed to Task 9. The implementation has failed verification; remediation is out-of-scope for this run and requires user adjudication.

---

### Task 9: Integrate wave findings + final commit

**Files modified (depending on wave findings):**
- Any of `docs/supervisor-review/sections/*.tex` (per the specific findings)
- `docs/supervisor-review/refs.bib` (if a citation correction is required)

- [ ] **Step 1: Classify each wave finding and route it (per Wave-2 PM FLAG-HIGH on Task 9 re-authorship route)**

For each FLAG / NIT in `/tmp/wave1_rc_*assembled.md`, `/tmp/wave2_modelqa_*assembled.md`, and `/tmp/wave2bis_techwriter_*assembled.md`, classify by remediation type using this decision table:

| Finding type | Examples | Route |
|---|---|---|
| **Mechanical** | typo, unicode-math character to replace, broken `\ref{}`, missing `\cite{}`, `comm -23` reported a missing bib key, `\hat{\beta}` inconsistency, formatting nit | **Main thread `Edit`** — fast, single-file diff. Apply directly. |
| **Cross-section consistency** | terminology mismatch between §5 and §6, section reference points to wrong target, glossary entry missing | **Main thread `Edit`** — fast, multi-file but mechanical. |
| **Paragraph-level prose / framing** | "this prose reads as Abrigo-as-product" (§5 invariant violation), "the §6.X iteration block omits the verdict-sensitivity-to-design caveat", "the §3 lemma reads as proven not as proposition" | **Re-dispatch to original sub-agent** — content judgment requires the agent that produced the surrounding voice. Use the same brief from Task 3, plus the specific finding(s) prepended as a `# Wave-N closure prompt` block. Fix only the called-out paragraph(s); leave the rest intact. |
| **Factual / numeric correction** | "the Pair D `t = +5.5456` is reported as `+5.55` in §6.1", "App C sha256 chain has a typo on revision v1.2.1", "the dev-AI cell_count range is wrong" | **Re-dispatch to original sub-agent (Data-Methodology)** — agent has the source memory in working memory. |
| **Lemma / framework substantive** | "the lemma's two-sided market argument has a logical gap", "§3.3 conflates Abrigo Lemma with a CFMM existence claim" | **Re-dispatch to Econ-Writer** — the agent that authored the lemma's prose; they have the framework context. |
| **NIT, user says ship as-is** | minor stylistic preference, deferred App-D power-derivation cell, etc. | **Document deferral in final commit message under a "DEFERRED FINDINGS" footer.** Do not edit. |

Iteration cap on re-dispatch: at most 2 re-dispatch rounds per agent. After the second round, halt and ask the user to adjudicate (either accept the partial fix or escalate to manual rewrite).

For each finding, log the routing decision and outcome in `/tmp/wave-finding-integration-log.md` so the final commit message can summarise.

- [ ] **Step 2: Re-compile after edits**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review && ./build.sh
```

Expected: clean compile (same passing criteria as Task 7 step 2).

- [ ] **Step 3: Verify page count remains in target range**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review
pdfinfo 2026-05-06-empirical-record-letter.pdf | grep Pages
```

- [ ] **Step 4: Final commit**

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git add docs/supervisor-review/sections/ docs/supervisor-review/refs.bib docs/supervisor-review/2026-05-06-empirical-record-letter.pdf
git commit -m "feat: supervisor-review document v1.0 — final after two-wave verification

Two-wave verification per feedback_two_wave_doc_verification:
- Wave 1 Reality Checker: [paste verdict line]
- Wave 2 Model QA Specialist: [paste verdict line]

Wave findings integrated inline; reports preserved at
/tmp/wave{1,2}_*supervisor_review_assembled.md for audit.

Section briefs preserved at scratch/2026-05-06-supervisor-review/
brief-{data-methodology,onchain-explainer,econ-writer}.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 5: Hand off to user**

Report to user:

```
Supervisor-review document v1.0 ready at:
- LaTeX source: docs/supervisor-review/main.tex (+ sections/, refs.bib)
- Compiled PDF: docs/supervisor-review/2026-05-06-empirical-record-letter.pdf
- Page count: [N] pp

Two-wave verification complete:
- Wave 1 RC: [verdict]
- Wave 2 MQS: [verdict]

[If wave findings were deferred as NITs, list them here.]

Spec source of truth: docs/specs/2026-05-06-supervisor-review-document-design.md (committed f5dcea9).
Implementation plan: docs/plans/2026-05-06-supervisor-review-document-implementation.md.

Document is ready for supervisor delivery.
```

---

## Self-review

This plan operationalises spec `docs/specs/2026-05-06-supervisor-review-document-design.md`. Cross-checking spec coverage against tasks:

| Spec section | Plan task |
|---|---|
| §3.1 §1 Introduction | Task 4 (Econ-Writer) → Task 5 step 1 |
| §3.2 §2 Framework | Task 4 (Econ-Writer) → Task 5 step 2 |
| §3.3 §3 Abrigo Lemma | Task 4 (Econ-Writer) → Task 5 step 3 |
| §3.4 §4 On-chain primer | Task 4 (Technical Writer) → Task 5 step 4 |
| §3.5 §5 Empirical methodology | Task 4 (Model QA) → Task 5 step 5 |
| §3.6 §6 Abrigo Log | Task 4 (Model QA) → Task 5 step 6 |
| §3.7 §7 Open questions (incl. §7.5) | Task 4 (Econ-Writer) → Task 5 step 7 |
| §3.8 §8 Request | Task 4 (Econ-Writer) → Task 5 step 8 |
| §3.9 App A Glossary | Task 4 (Econ-Writer + Technical Writer) → Task 5 step 9 |
| §3.9 App B Citations | Task 4 (all three sub-lists) → Task 6 |
| §3.9 App C Pair D verdict | Task 4 (Model QA) → Task 5 step 10 |
| §3.9 App D Power-calc | Task 4 (Model QA) → Task 5 step 11 |
| §4 Multi-agent authorship | Task 3 (briefs) + Task 4 (dispatch) |
| §5 Anti-overclaim invariants | Encoded in each Task-3 brief; verified at Task 8 |
| §6 Output paths | Task 1 (workspace) + Task 7 (compile) + Task 9 (final commit) |
| §7 Verification (this spec, two-wave) | Already done at spec-commit time (`f5dcea9`); Task 8 re-verifies the assembled document |
| §8 Out of scope | Acknowledged — no tasks for revision cycles, supervisor-response handling, or follow-up iterations |

**Placeholder scan.** No `TBD` / `TODO` / "fill in details" patterns. Each step has either an exact command, an exact file path with content, or an exact agent dispatch with prompt content.

**Type consistency.** Section labels (`sec:1`–`sec:8`, `app:A`–`app:D`) consistent across Task 2 stubs, Task 5 stitching, and Task 8 cross-reference verification. Agent assignment names (`Model QA Specialist`, `Technical Writer`, `Book Co-Author`) consistent between Task 3 briefs and Task 4 dispatch. File paths consistent throughout.

**Spec gap check.** No spec section without a covering task. The spec's §7 "Verification" of itself was satisfied at spec-commit time and is not re-done here; the assembled-document verification at Task 8 is a separate (deeper) review of the actual output, not of the spec.
