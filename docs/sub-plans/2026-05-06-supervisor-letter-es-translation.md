# Supervisor-Letter Spanish Translation — Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to execute this sub-plan task-by-task. Same approach as the REVISION-C / REVISION-D sub-plans.

**Parent letter (source):** `docs/supervisor-review/letter.tex` → `2026-05-06-supervisor-letter.pdf` (committed `cf6b7a4`, 7 pp, English v1.4)
**Parent spec:** `docs/specs/2026-05-06-supervisor-review-document-design.md@cdaff56` (REVISION-A + REVISION-C + REVISION-D integrated)
**Background research:** `/tmp/spanish-academic-agent-research.md` (Spanish-academic-AI-writing agent recon, 2026-05-06)

**Goal:** Spanish translation of the v1.4 entry-point letter. Source letter is unchanged. Target is a new deliverable `letter-es.tex` → `2026-05-06-supervisor-letter-es.pdf`. The 37-pp companion is OUT of scope for this translation pass.

**Architecture:** Four-task sub-plan mirroring REVISION-D. Task A (research) is DONE. Task B amends the spec and runs lightweight Wave-1 verify. Task C authors the two briefs. Task D dispatches translator → recompiles → dispatches reviewer → integrates findings → final commit.

**Tech Stack:** Same as parent + babel-spanish. `\usepackage[spanish,es-noindentfirst,es-tabla,es-nodecimaldot]{babel}` replaces `\usepackage[english]{babel}` for the Latin-American Spanish letter. All other packages unchanged. Bibliography unchanged (refs are international or already Spanish-titled BanRep entries).

---

## Translation discipline (user-locked decisions, 2026-05-06)

These are the user-given decisions that bind the translator brief. Re-litigation is out of scope.

1. **Dialect: Latin-American academic Spanish (Colombian standard).** NO peninsular features (no `vosotros`, no `vale`, no `ordenador`, no `mola`). The supervisor is Colombian; translation must read as natural Colombian academic register.
2. **Address form: `usted` throughout.** NO `tú`/`vos` tuteo. Academic memoranda to a thesis supervisor in the Colombian convention use `usted`.
3. **Verdict labels (`PASS` / `FAIL` / `EXIT_NON_REMITTANCE` / `PARKED`): KEEP IN ENGLISH** inside `\texttt{...}`. These are technical audit-trail identifiers tied verbatim to the spec text and to the project memory (`project_pair_d_phase2_pass.md` etc.) — translating them would break the audit chain.
4. **Leifke verbatim quote (§1 Suggested-solution): KEEP IN ENGLISH** as a block quote (it is a direct quote from an English-language video). Add a single-line Spanish footnote gloss for the supervisor's reading convenience. Translator's call on phrasing.
5. **Repo names, sha hashes, file paths, BibTeX citation keys: UNCHANGED.** These are technical identifiers, not prose.
6. **Math notation: UNCHANGED.** `\hat{\beta}_{\mathrm{composite}}`, `\(...\)`, `\[...\]`, `\mathrm{...}`, etc. all preserved.

---

## Pinned terminology table (translator MUST use these)

| English source | Latin-American Spanish (translator-binding) |
|---|---|
| FX-pass-through cost shock | choque de costos por traspaso cambiario |
| parametric cost insurance | seguro paramétrico de costos |
| wage→capital boundary | frontera salario→capital |
| purchasing-parity stablecoin | stablecoin de paridad de poder adquisitivo |
| supervisor (academic) | asesor |
| iteration (workstream) | iteración |
| verdict | veredicto |
| sample size | tamaño muestral |
| primary specification | especificación principal |
| robustness arm / row | brazo / fila de robustez |
| sign-flipped | con signo invertido |
| underpowered null | hipótesis nula con baja potencia |
| pre-registration | pre-registro |
| anti-fishing | (keep English in `\texttt{}`) — technical project-internal term |
| kill criteria / criterion | criterios / criterio de cierre |
| identification (econometrics) | identificación |
| predictive regression | regresión predictiva |
| structural-causal | estructural-causal |
| convex-payoff sufficiency | suficiencia del payoff convexo |
| underwriting standard | estándar de suscripción |
| familywise / FWER | tasa de error por familia / FWER (sigla en inglés mantenida) |
| false-discovery rate / FDR | tasa de descubrimientos falsos / FDR (sigla en inglés mantenida) |
| transmission channel | canal de transmisión |
| pass-through (FX → inflation) | traspaso (cambiario → inflación) |
| issuer / underwriter / counterparty | emisor / suscriptor / contraparte |
| call option | opción de compra (call) |
| devaluation insurance | seguro contra devaluación |
| young workers (14–28) | trabajadores jóvenes (14–28 años) |
| working-class | clase trabajadora |
| ICT services | servicios de TIC (tecnologías de la información y comunicaciones) |
| broad services aggregate | agregado de servicios amplios |
| lagged-FX predictor | predictor cambiario rezagado |
| companion (37-page document) | documento técnico complementario |
| letter (entry-point document) | carta (documento de entrada) |
| supervisor-asks (§4 of the letter) | solicitudes al asesor |

The translator MUST use these renderings consistently. If the translator finds a source phrase that is not on this table and does not have an obvious natural Colombian-Spanish translation, the translator should leave a `% TRANSLATOR-NOTE: ambiguous: <English phrase>` comment in the LaTeX source for the reviewer to flag. Inventing new technical terminology silently is forbidden.

---

## Babel-Spanish preamble change

The English letter uses `\usepackage[english]{babel}`. The Spanish letter substitutes:

```latex
\usepackage[spanish,es-noindentfirst,es-tabla,es-nodecimaldot]{babel}
```

Options:
- `spanish` — base Spanish locale
- `es-noindentfirst` — do not indent the first paragraph after a section heading (matches Colombian academic convention)
- `es-tabla` — render `\tablename` as "Cuadro" instead of "Tabla" (Latin-American academic convention; matches BanRep "borradores" style)
- `es-nodecimaldot` — keep `0.05` as `0.05` (English decimal mark) instead of `0,05` — preserve econometric numerical conventions and citation precision; this is a deliberate departure from default Spanish typography. **Rationale:** the document contains many numerical results (`p ≈ 1.46e-08`, `\hat{\beta} = +0.137`, etc.) and the audit trail is keyed to these decimal-dot strings. Switching to comma would break consistency with the source memory files and the 37-pp companion.

The `\hyphenation{...}` macro for project-specific words is OPTIONAL (LaTeX babel-spanish handles standard Spanish hyphenation). Reviewer flags any visibly bad hyphenation.

---

## File structure

| Path | Status | Purpose |
|---|---|---|
| `docs/specs/2026-05-06-supervisor-review-document-design.md` | modify | Add §3.12 (Spanish translation deliverable record) |
| `docs/supervisor-review/letter-es.tex` | create | Spanish LaTeX source |
| `docs/supervisor-review/2026-05-06-supervisor-letter-es.pdf` | create (build output) | Compiled Spanish PDF |
| `docs/supervisor-review/preamble.tex` | UNCHANGED | shared preamble (NOT edited; the Spanish letter swaps babel only inline in `letter-es.tex`, which `\input{preamble}` and then redeclares the babel package — see Task D.1 for the exact pattern) |
| `docs/supervisor-review/refs.bib` | UNCHANGED | bibliography is shared; refs are international or BanRep-Spanish-titled |
| `scratch/2026-05-06-supervisor-review/brief-es-translator.md` | create | Translator brief |
| `scratch/2026-05-06-supervisor-review/brief-es-reviewer.md` | create | Reviewer brief |
| `scratch/2026-05-06-supervisor-review/agent-output-letter-es-translator.tex` | create (translator output) | Spanish LaTeX from translator agent |
| `scratch/2026-05-06-supervisor-review/agent-output-letter-es-reviewer.md` | create (reviewer output) | Reviewer findings (markdown report, not LaTeX) |

The preamble shared-vs-fork question: the existing `letter.tex` uses `\input{preamble}`, and `preamble.tex` declares `\usepackage[english]{babel}`. If `letter-es.tex` also `\input{preamble}`, it inherits English babel — wrong. Two options:

(a) **Inline-redeclare babel in `letter-es.tex`** *after* `\input{preamble}` — `\renewcommand` won't work for package options. The cleanest approach is to NOT use the shared preamble and instead duplicate it inline in `letter-es.tex` with `\usepackage[spanish,...]{babel}` substituted. Files diverge by one line; preamble.tex stays English-only.

(b) **Make `preamble.tex` language-agnostic** by removing the `\usepackage[...]{babel}` line and putting it inline in each language-specific `letter*.tex`. Cleaner long-term but modifies the shared preamble (touches the English compile and requires a recompile of the English letter to verify it still works).

**Decision: Option (a)** — duplicate preamble inline in `letter-es.tex` with babel-spanish substitution. Preamble.tex unchanged. English letter unaffected. Simpler diff. Documented in Task D.1.

---

## Tasks

### Task A: Background research — DONE

Spanish-academic-AI-writing agent reconnaissance complete. Report at `/tmp/spanish-academic-agent-research.md`. Recommended roster:
- **Translator:** `general-purpose` (no Spanish-specialist agent exists locally; external `deusyu/translate-book` deferred to user-decision per the LaTeX-math-agent recon precedent).
- **Reviewer:** `Cultural Intelligence Strategist` (CIS) — only locally-installed agent that touches localization. Mismatch with the typical CIS use (UX semiotics, icons, colors) is acknowledged; the brief in Task C.2 specifically scopes the reviewer to academic-translation accuracy + dialect/register check + LaTeX integrity.

If the user wants a different reviewer (e.g., a second `general-purpose` instance with a verification-only brief, or an external clone of `deusyu/translate-book`), substitute in Task D.3. Default is CIS.

---

### Task B: Spec amendment §3.12 + Wave-1 verify + commit

**Files:**
- Modify: `docs/specs/2026-05-06-supervisor-review-document-design.md` (append §3.12)

- [ ] **Step B.1: Append spec amendment §3.12**

Append after §3.11 (REVISION-D corrections), before `## §4. Multi-agent authorship plan`:

```markdown
### §3.12 Spanish Translation of the Entry-Point Letter (2026-05-06)

This sub-section records the Spanish translation of the 7-page entry-point
letter v1.4 (committed `cf6b7a4`). The Spanish translation is a NEW
deliverable, NOT a modification of the English source; both versions are
preserved.

**Source.** `docs/supervisor-review/letter.tex` → `2026-05-06-supervisor-letter.pdf`.
Compile state: 7 pp, all citations resolved, REVISION-D corrections
integrated.

**Target.** `docs/supervisor-review/letter-es.tex` → `2026-05-06-supervisor-letter-es.pdf`.
Latin-American academic Spanish (Colombian standard); `usted`-form
throughout; verdict labels (`PASS` / `FAIL` / `EXIT_NON_REMITTANCE` /
`PARKED`) preserved in English under `\texttt{...}`; Leifke verbatim
quote preserved in English with a Spanish footnote gloss.

**Pipeline.** Two-agent sequential pipeline:
- Translator (`general-purpose` subagent): produces `letter-es.tex` from
  the English source; consumes a translator-brief that pins the
  terminology table (~30 entries) and the babel-spanish preamble swap.
- Reviewer (`Cultural Intelligence Strategist` subagent, independent
  fresh invocation): verifies translation accuracy + Latin-American
  Spanish register + LaTeX integrity + anglicism/calque flag list.
  Findings integrated by main thread before final commit.

The 37-pp technical companion is NOT translated in this sub-plan; the
Spanish letter references it via the existing English file paths
(`docs/supervisor-review/2026-05-06-empirical-record-letter.pdf`) so the
supervisor can drill into either language at his discretion.

**Background research.** Spanish-academic-AI-writing agent reconnaissance
at `/tmp/spanish-academic-agent-research.md` (2026-05-06) confirmed no
local Spanish-specialist agent exists; the external `deusyu/translate-book`
template (multi-agent translation, language-agnostic, NOT LaTeX-native)
is deferred to user-decision and is not adopted in this run.

**Out of scope for this translation pass.** No changes to the English
letter; no changes to the 37-pp companion; no changes to `refs.bib`
(international refs untranslated; BanRep refs already Spanish-titled);
no changes to the project's spec / plan / sub-plans beyond this §3.12
record. Future iterations may translate the companion or add other
language versions; both are explicitly deferred.
```

- [ ] **Step B.2: Lightweight Wave-1 RC on the spec diff**

Dispatch a single Reality Checker review:
- description: "Wave 1 RC — Spanish-translation spec diff"
- subagent_type: `Reality Checker`
- prompt: review the §3.12 amendment for fidelity to the user-given decisions (dialect, usted, verdict labels, Leifke quote, math/repo unchanged); **≤ 250 words** (per Wave-2 PM FLAG-LOW — the §3.12 amendment is ~40 lines and the prior 200-word budget was tight); output to `/tmp/wave1_rc_es_taskB.md`.

- [ ] **Step B.3: Commit Task B**

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git add docs/specs/2026-05-06-supervisor-review-document-design.md
git commit -m "docs(spec): §3.12 Spanish translation deliverable record

Records the Spanish translation of letter v1.4 as a new deliverable
(letter-es.tex -> 2026-05-06-supervisor-letter-es.pdf). Latin-American
academic Spanish, usted-form, verdict labels in English, Leifke quote
in English with Spanish footnote gloss.

Pipeline: general-purpose translator + Cultural Intelligence Strategist
reviewer per /tmp/spanish-academic-agent-research.md.

Wave-1 RC verification on spec diff: ACCEPT.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task C: Author the two briefs

**Files:**
- Create: `scratch/2026-05-06-supervisor-review/brief-es-translator.md`
- Create: `scratch/2026-05-06-supervisor-review/brief-es-reviewer.md`

- [ ] **Step C.1: Author `brief-es-translator.md` (general-purpose translator)**

Brief content (verbatim into scratch file). The brief reproduces the dialect rules + terminology table + babel-spanish preamble swap + per-section discipline.

```markdown
# Translator Brief — Spanish translation of supervisor letter v1.4

**Sub-agent type:** `general-purpose`
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-letter-es-translator.tex`
**Source file:** `docs/supervisor-review/letter.tex` (committed `cf6b7a4`, 7 pp English v1.4)

You are translating an English LaTeX academic memorandum into Latin-American academic Spanish. The supervisor is Colombian; the translation must read as natural Colombian academic register.

## Hard rules (load-bearing)

1. **Dialect:** Latin-American academic Spanish (Colombian standard). NO peninsular features (no `vosotros`, no `vale`, no `ordenador`, no `mola`).
2. **Address form:** `usted` throughout. NO `tú` / `vos` tuteo.
3. **Math:** preserve all `\(...\)`, `\[...\]`, `\hat{\beta}_{\mathrm{composite}}`, `\mathrm{...}`, etc. UNCHANGED.
4. **LaTeX commands:** preserve all `\section{...}`, `\subsection{...}`, `\href{...}{...}`, `\citep{...}`, `\citet{...}`, `\textbf{...}`, `\textit{...}`, `\texttt{...}`, `\paragraph{...}`, `\item[...]`, etc. ONLY the prose inside these commands changes.
5. **Citation keys:** UNCHANGED (`\citep{rincontorresInterdependenceFXTreasury2021}` stays exactly that).
6. **Repo paths and sha hashes:** UNCHANGED (`\href{https://github.com/JMSBPP/abrigo-analytics/...}{\texttt{notebooks/...}}` stays).
7. **Verdict labels (`PASS`, `FAIL`, `EXIT_NON_REMITTANCE`, `PARKED`):** KEEP IN ENGLISH inside `\texttt{...}` or as bare uppercase tokens. They are technical audit-trail identifiers; translating breaks the audit chain.
8. **Leifke verbatim quote in §1 Suggested-solution:** KEEP IN ENGLISH (it is a direct quote from an English-language video). Add a Spanish footnote gloss with `\footnote{Traducción libre: ...}` immediately after the closing English quote mark. Keep the gloss to a single sentence.
9. **Spec amendment cross-references:** `\S 1`, `\S 2`, etc. — UNCHANGED (Spanish convention also uses `\S` for section symbol).

## Babel-spanish preamble swap (Task D.1 will integrate)

The output file should be a **complete self-contained LaTeX document** (not just sections). At the top, instead of `\input{preamble}`, **inline-duplicate the preamble with the babel-spanish substitution**:

```latex
\documentclass[11pt,a4paper]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noindentfirst,es-tabla,es-nodecimaldot]{babel}
% (REST OF preamble.tex CONTENT, COPIED VERBATIM)
```

You should `Read` `docs/supervisor-review/preamble.tex` and copy it verbatim into the top of `agent-output-letter-es-translator.tex`, swapping ONLY the babel line. Update the title block:

```latex
\renewcommand{\@title}{Seguro Paramétrico de Costos de Cambio para Trabajadores Digitales Latinoamericanos Subatendidos --- Cobertura mediante Instrumentos On-Chain \\[0.3em]
\large Registro de Iteraciones Cerradas y Solicitud de Lineamientos Metodológicos}
\renewcommand{\@author}{d\textsuperscript{2}~finance \\ \href{https://github.com/wvs-finance}{\texttt{github.com/wvs-finance}}}
\renewcommand{\@date}{2026-05-06}
```

(The author block is the same; only the title is translated. The English title can be retained as a sub-title in italics if you want bilingual headering — judgment call.)

## Pinned terminology table (USE THESE; DO NOT INVENT NEW)

| English | Spanish |
|---|---|
| FX-pass-through cost shock | choque de costos por traspaso cambiario |
| parametric cost insurance | seguro paramétrico de costos |
| wage→capital boundary | frontera salario→capital |
| purchasing-parity stablecoin | stablecoin de paridad de poder adquisitivo |
| supervisor (academic) | asesor |
| iteration (workstream) | iteración |
| verdict | veredicto |
| sample size | tamaño muestral |
| primary specification | especificación principal |
| robustness arm / row | brazo / fila de robustez |
| sign-flipped | con signo invertido |
| underpowered null | hipótesis nula con baja potencia |
| pre-registration | pre-registro |
| anti-fishing | `\texttt{anti-fishing}` (keep English) |
| kill criteria | criterios de cierre |
| identification (econometrics) | identificación |
| predictive regression | regresión predictiva |
| structural-causal | estructural-causal |
| convex-payoff sufficiency | suficiencia del payoff convexo |
| underwriting standard | estándar de suscripción |
| familywise / FWER | tasa de error por familia / FWER |
| false-discovery rate / FDR | tasa de descubrimientos falsos / FDR |
| transmission channel | canal de transmisión |
| pass-through (FX→inflation) | traspaso (cambiario→inflación) |
| issuer / underwriter / counterparty | emisor / suscriptor / contraparte |
| call option | opción de compra (call) |
| devaluation insurance | seguro contra devaluación |
| young workers (14–28) | trabajadores jóvenes (14–28 años) |
| working-class | clase trabajadora |
| ICT services | servicios de TIC (Tecnologías de la Información y Comunicaciones) on first occurrence; \texttt{servicios de TIC} thereafter |
| broad services aggregate | agregado de servicios amplios |
| lagged-FX predictor | predictor cambiario rezagado |
| companion (37-page document) | documento técnico complementario |
| letter (entry-point document) | carta (documento de entrada) |
| supervisor-asks | solicitudes al asesor |

If you encounter a phrase that is NOT on this table and does NOT have an obvious natural Colombian-Spanish translation, leave a `% TRANSLATOR-NOTE: ambiguous: <English phrase>` comment in the LaTeX source for the reviewer to flag. Inventing new technical terminology silently is forbidden.

## Per-section guidance (light)

- **§1 Motivation bullet:** the BanRep citations have Spanish titles; preserve the cite keys and let `natbib` render the Spanish title automatically.
- **§1 Suggested-solution bullet:** Leifke quote in English block, Spanish footnote gloss after.
- **§2 Five iteration blocks:** the inlined data attribute paragraphs (`\textbf{Source:} ... \textbf{Frequency:} ... etc.`) translate the labels (`Source:` → `Fuente:`, `Frequency:` → `Frecuencia:`, `Window:` → `Ventana:`, `Sample:` → `Muestra:`, `Transformations:` → `Transformaciones:`, `Repo:` → `Repositorio:`, `Spec sha:` → `Sha de la especificación:`, `Spec fingerprint:` → `Huella de la especificación:`, `Spec:` → `Especificación:`, `Spec chain:` → `Cadena de especificación:`); the Result/Interpretation/Caveats labels also translate (`Result.` → `Resultado.`, `Interpretation.` → `Interpretación.`, `Caveats inherited from independent review.` → `Salvedades heredadas de la revisión independiente.`, `Why it fails.` → `Razón del rechazo.`, `Why it fails and sensitivity caveat.` → `Razón del rechazo y salvedad de sensibilidad.`, `Why it exits.` → `Razón de la salida.`, `Why parked.` → `Razón de la pausa.`).
- **§3 Risk-target framing:** plain prose; translate fully; preserve the inline `\(Y_{\mathrm{inequality}}(t) = R_a(t) - R_c(t)\)` reference verbatim.
- **§4 Asks:** translate sub-section headings (`\subsection{Suggested specifications}` → `\subsection{Especificaciones sugeridas}`, etc.) and their prose. The Risks bullet list translates fully.

## Output format

A single LaTeX file at `scratch/2026-05-06-supervisor-review/agent-output-letter-es-translator.tex`. Complete self-contained document (preamble + body). The reviewer will diff against the English source.

After writing, run a self-check:
- Grep for any remaining English words in non-`\texttt{}`, non-`\verb` contexts (excluding the Leifke quote, citation keys, repo URLs, and verdict labels). Report any leakage.
- Grep for `tú\b`, `\bvos\b`, `vosotros`, `os\b` to verify NO tuteo / peninsular forms.
- Grep for `0,\d` — should be EMPTY (decimal dots preserved per `es-nodecimaldot`).

## Anti-overreach

ONLY produce the Spanish letter. Do NOT modify the English letter, the spec, the plan, the sub-plans, the companion, or `refs.bib`. Do NOT compile (the main thread runs the build). Do NOT invent new bib entries.

## Report format

- Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- File path written
- Word count (Spanish typically runs ~15% longer than English)
- TRANSLATOR-NOTE comment count (ambiguous phrases flagged for reviewer)
- Self-check results (English-leakage, tuteo/peninsular, decimal-dot)
- Any concerns
```

- [ ] **Step C.2: Author `brief-es-reviewer.md` (Cultural Intelligence Strategist reviewer)**

Brief content (verbatim into scratch file):

```markdown
# Reviewer Brief — Spanish translation verification

**Sub-agent type:** `Cultural Intelligence Strategist`
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-letter-es-reviewer.md`

You are an INDEPENDENT reviewer of a Spanish translation. The translator (a `general-purpose` agent in a separate session) produced `agent-output-letter-es-translator.tex` from the English source `docs/supervisor-review/letter.tex` (committed `cf6b7a4`).

Your job is verification — NOT re-translation. Find issues, propose specific fixes, do NOT rewrite the file.

**Note on agent-type fit.** Your typical scope is UX semiotics (icons, colors, cultural symbols). This brief explicitly scopes you to academic-translation review for one document. Treat the dialect/register/anglicism axis as the primary verification surface, with academic-translation accuracy as the secondary surface.

## Source documents

1. English source: `docs/supervisor-review/letter.tex`
2. Spanish translation under review: `scratch/2026-05-06-supervisor-review/agent-output-letter-es-translator.tex`
3. Translator brief (the rules the translator was bound to): `scratch/2026-05-06-supervisor-review/brief-es-translator.md`

Read all three in full before reviewing.

## Verification scope (5 axes)

### Axis 1: Translation accuracy (paragraph-level diff)

For each paragraph in the Spanish letter, locate the corresponding English paragraph and verify:
- All factual content preserved (no claims dropped, no claims added)
- All numerical values preserved (β=+0.137, p≈1.46e-08, N=134, etc. UNCHANGED)
- All citation keys preserved (`\citep{rincontorresInterdependenceFXTreasury2021}` UNCHANGED)
- All hyperref URLs preserved (the `https://github.com/JMSBPP/abrigo-analytics/...` URLs UNCHANGED)
- Math notation preserved (`\hat{\beta}_{\mathrm{composite}}` UNCHANGED)
- Verdict labels preserved in English (`PASS`, `FAIL`, etc.)

Report any paragraph where these checks fail.

### Axis 2: Spanish dialect / register (Latin-American academic Colombian)

- NO peninsular features (`vosotros`, `os`, `vale`, `ordenador`, `mola`, leísmo with personal-pronoun confusion)
- NO tuteo (`tú`, `vos` against the user-locked `usted` rule)
- Academic register (no colloquial register, no marketing language, no English-calque idioms)
- Colombian-standard vocabulary preferred over Mexican / Argentinian variants where they differ (e.g., "computadora" not "computador" in academic context, but Colombian "computador" is also acceptable)
- Run grep on the Spanish text for: `\btú\b`, `\bvos\b`, `\bvosotros\b` — must be empty. (Per Wave-1 RC NIT 1: do NOT grep bare `\bos\b` — it false-positives on `nosotros`, `costos`, `pesos`, `procesos`, etc. The peninsular-clitic signature is captured by `\bvosotros\b` alone, plus a secondary pattern ` os \w+(áis|éis)\b` if a more aggressive sweep is wanted.)

### Axis 3: Anglicism / calque flag list

Read the Spanish prose looking for:
- Direct anglicisms (e.g., "asumir" used as "assume" instead of correct "suponer"; "soportar" used as "support" instead of correct "respaldar"; "aplicar" used as "apply [to a job]" instead of correct "postular"; "actualmente" used as "currently" instead of correct "en este momento" depending on context)
- LaTeX-environment anglicisms ("Tabla" instead of correct `Cuadro` per `es-tabla` babel option — should be auto-rendered correctly via babel)
- Untranslated technical terms that ARE on the pinned terminology table

For each anglicism found, report: location (line number), the offending phrase, the suggested correction, brief justification.

### Axis 4: LaTeX integrity (`diff`-style)

Run a structural diff comparing the English and Spanish LaTeX:
- Section count: same?
- Subsection count: same?
- Equation count: same?
- Citation count: same?
- Hyperref count: same?
- `\paragraph{...}` count: same?
- `\item` count: same?

Report any structural mismatch. Use `grep -c` style counts for each.

### Axis 5: Translator-flagged ambiguities

The translator may have left `% TRANSLATOR-NOTE: ambiguous: <phrase>` comments in the LaTeX source for terms that did not have a clear Colombian-Spanish translation. Enumerate each one and propose a specific resolution.

## Output format

Write a markdown report at `scratch/2026-05-06-supervisor-review/agent-output-letter-es-reviewer.md` with this structure:

```
# Reviewer findings

## Verdict
ACCEPT | ACCEPT_WITH_REVISIONS | BLOCK

## Axis 1: Accuracy diff findings
(per-paragraph; only listed if issues found)

## Axis 2: Dialect / register findings
(grep results + qualitative read)

## Axis 3: Anglicism / calque flag list
(table)

## Axis 4: LaTeX integrity
(count comparison table)

## Axis 5: Translator-flagged ambiguities
(per-flag resolution proposals)

## Closure recommendations
(prioritized list of fixes the main thread should apply before commit)
```

## Independence rule

Do NOT trust the translator's self-check results — re-run them yourself. Do NOT trust the translator's report of issues — read the source.

## Anti-overreach

You are reading + reporting. Do NOT modify any LaTeX file. Do NOT modify the spec / plan / sub-plans / companion. Findings go to the reviewer report only.

## Report format (terminal)

- Verdict (ACCEPT / ACCEPT_WITH_REVISIONS / BLOCK)
- Issue count by axis (1-5)
- Path to the report
```

- [ ] **Step C.3: NO commit (briefs are scratch, per `feedback_two_wave_doc_verification` "Out of scope" rule)**

---

### Task D: Dispatch translator → recompile → dispatch reviewer → integrate → final commit

**Files:**
- Create: `docs/supervisor-review/letter-es.tex`
- Create (build output): `docs/supervisor-review/2026-05-06-supervisor-letter-es.pdf`

- [ ] **Step D.1: Dispatch the translator (`general-purpose`)**

Single Agent call with the brief content from Task C.1 as the prompt.

After the translator returns DONE:
1. Verify file exists at `scratch/.../agent-output-letter-es-translator.tex`
2. Verify it is non-empty and contains a `\begin{document}` + `\end{document}` pair
3. Verify it contains a `\usepackage[spanish,...]{babel}` line (the babel-spanish swap)
4. Verify the translator-side self-checks (English leakage, tuteo, decimal-dot) all returned clean per the translator's report

If any check fails, halt and report BLOCKED — do not proceed.

- [ ] **Step D.2: Copy translator output to deliverable path + recompile**

```bash
cp /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review/agent-output-letter-es-translator.tex /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review/letter-es.tex
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review
pdflatex -interaction=nonstopmode letter-es.tex >/dev/null 2>&1
bibtex letter-es
pdflatex -interaction=nonstopmode letter-es.tex >/dev/null 2>&1
pdflatex -interaction=nonstopmode letter-es.tex >/dev/null 2>&1
mv -f letter-es.pdf 2026-05-06-supervisor-letter-es.pdf
pdfinfo 2026-05-06-supervisor-letter-es.pdf | grep -E "Pages|File size"
```

**Note on `bibtex` locale (per Wave-2 PM FLAG-LOW):** `bibtex letter-es` is invoked WITHOUT `-l spanish` because the project uses `natbib` + `plainnat` style, which renders citation joiners (",", ";", "and"/"y") at typeset time via `babel`'s active locale, not at `bibtex` time. The `-l` flag controls `bibtex`'s sort order for non-Latin scripts and is a no-op for Spanish. If the reviewer (Task D.3) flags bibliography rendering anomalies (stray "and" instead of "y", "ed." instead of "ed.", "pp." instead of "págs.") the fix is to load `babel`'s `\bibsetup` macros or to add the `babelbib` package — escalate to user; do not silently patch the bib style.

HALT branch (mirrors REVISION-D Task D.5):
- Fatal compile errors → BLOCKED
- Undefined citations after `bibtex` → BLOCKED (likely a translator-introduced typo in `\citep{}`)
- Undefined references → BLOCKED
- Page count outside [6, 10] → SOFT REVIEW (Spanish runs longer than English; 7 → ~8-9 pp expected)

If all checks pass, proceed to D.3.

- [ ] **Step D.3: Dispatch the reviewer (`Cultural Intelligence Strategist`)**

Single Agent call with the brief content from Task C.2 as the prompt. The reviewer reads the English source + the Spanish translation + the translator brief in full.

Wait for completion. Read the reviewer report at `scratch/.../agent-output-letter-es-reviewer.md`.

- [ ] **Step D.4: Integrate reviewer findings**

Iteration-cap discipline (per Wave-2 PM FLAG-MED — disambiguated from prior REVISION-D wording):
- **Mechanical Edits by main thread: UNLIMITED.** Anglicism fixes, terminology corrections, label translations, missing footnote glosses, etc. — main thread applies as many `Edit` tool calls as needed to close the reviewer's prioritized fixes.
- **Translator re-dispatch budget: 1 retry maximum.** If reviewer findings include paragraph-level register / dialect / accuracy issues that require regeneration rather than mechanical edit, the main thread re-dispatches the translator ONCE with a closure prompt enumerating the specific issues. After that single retry, no further translator dispatches; remaining issues escalate to user.
- **Reviewer re-dispatch: NONE.** The reviewer runs once. Re-running the reviewer post-fix is not in scope (iteration cap 0 on reviewer).

Decision tree (after the single reviewer pass):
- Reviewer verdict `ACCEPT` (no issues) → proceed to D.5 commit unchanged.
- Reviewer verdict `ACCEPT_WITH_REVISIONS` → main thread applies all mechanical-Edit fixes (unlimited); if any finding requires regeneration, main thread dispatches the single translator retry with a closure prompt; main thread then mechanically integrates the retry output. Recompile. Re-verify HALT checks. Commit.
- Reviewer verdict `BLOCK` → halt the sub-plan, report to user, do NOT commit. The translation has failed verification.

- [ ] **Step D.5: Final commit Task D**

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git add docs/supervisor-review/letter-es.tex docs/supervisor-review/2026-05-06-supervisor-letter-es.pdf
git commit -m "docs: supervisor letter v1.0 ES — Spanish translation of letter v1.4

Latin-American academic Spanish (Colombian standard); usted-form;
verdict labels in English; Leifke quote in English with Spanish footnote
gloss. Pinned terminology table (~30 entries) per translator brief.

Two-agent pipeline:
  - Translator: general-purpose subagent with sharpened brief per
    /tmp/spanish-academic-agent-research.md
  - Reviewer: Cultural Intelligence Strategist (independent fresh
    invocation) with verification-only brief

Pipeline outcome: <verdict from D.3 reviewer>; <findings integrated /
issues remaining>.

Page count: <N> pp.

Source (unchanged): docs/supervisor-review/letter.tex@cf6b7a4 (English v1.4).

Implements Task D of sub-plan
docs/sub-plans/2026-05-06-supervisor-letter-es-translation.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Self-review

| Requirement | Sub-plan task |
|---|---|
| Spanish translation deliverable (letter-es.tex + PDF) | Task D.1 (translator) → D.2 (compile) → D.4 (integrate) → D.5 (commit) |
| Latin-American academic Spanish (Colombian) | Translator brief Hard Rule #1; Reviewer brief Axis 2 |
| `usted`-form throughout | Translator brief Hard Rule #2; Reviewer brief Axis 2 grep |
| Verdict labels in English | Translator brief Hard Rule #7; Reviewer brief Axis 1 |
| Leifke quote in English with Spanish footnote gloss | Translator brief Hard Rule #8; Reviewer brief Axis 1 |
| Math / repo / sha / cite keys unchanged | Translator brief Hard Rules #3-6; Reviewer brief Axis 1 + 4 |
| Babel-spanish preamble (`es-noindentfirst,es-tabla,es-nodecimaldot`) | Translator brief preamble swap; Reviewer brief Axis 4 |
| Pinned terminology table (~30 entries) | Translator brief table; Reviewer brief Axis 3 |
| Independent reviewer (different agent type) | Recon recommendation: `Cultural Intelligence Strategist`; brief explicit on independence |
| Background research before translation | Task A — DONE; recon at /tmp/spanish-academic-agent-research.md |
| Spec amendment recording the deliverable | Task B.1 (§3.12) |
| Wave-1 verification on spec | Task B.2 |
| HALT discipline on compile + page count | Task D.2 |
| Reviewer-finding integration with iteration cap | Task D.4 (cap 1) |
| 37-pp companion + English letter unchanged | Out of scope by construction |

**Placeholder scan:** No TBDs. All brief contents reproduced verbatim.

**Type consistency:** File paths consistent (`scratch/2026-05-06-supervisor-review/agent-output-letter-es-{translator,reviewer}.{tex,md}`). Subagent types match recon recommendation. Spec section numbering (§3.12 follows §3.11).

**Scope check:** Single subsystem (Spanish letter only). 37-pp companion + English letter explicitly out of scope.

---

## Out of scope

- Translation of the 37-pp technical companion. Future sub-plan if requested.
- Translation of the spec, the plan, or the sub-plans. The audit trail is in English by project convention.
- Installing external translation agents (`deusyu/translate-book` etc.). Deferred to user-decision; mirrors the LaTeX-math-agent recon precedent.
- Re-running translator with a different agent type if the `general-purpose` translator's output is rejected. Per Task D.4, iteration cap is 1; second-failure escalation goes to the user.
- Translation of `refs.bib`. International refs are language-agnostic; BanRep refs already have Spanish titles in the source bib.
