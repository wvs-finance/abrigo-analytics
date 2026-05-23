# Supervisor-Letter REVISION-C Corrections — Sub-Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this sub-plan task-by-task. Same approach as the parent plan at `docs/plans/2026-05-06-supervisor-review-document-implementation.md@f16f3be`.

**Parent plan:** `docs/plans/2026-05-06-supervisor-review-document-implementation.md@f16f3be`
**Parent spec:** `docs/specs/2026-05-06-supervisor-review-document-design.md@3fd15bb` (REVISION-A integrated)
**Parent letter:** `docs/supervisor-review/letter.tex` → `2026-05-06-supervisor-letter.pdf` (committed `a198dc0`, 8 pp)
**Parent companion:** `docs/supervisor-review/main.tex` → `2026-05-06-empirical-record-letter.pdf` (committed `b93679a`, 37 pp)

**Goal:** Apply two user-given corrections (REVISION-C, 2026-05-06) to the entry-point letter only. The 37-page companion is unchanged.

**Architecture:** Two-task sub-plan. Task A amends the spec (records the REVISION-C corrections) and authors two re-author briefs. Task B dispatches one Data-Methodology and one Econ-Writer revision in parallel; main thread stitches into `letter.tex`; recompiles; verifies via lightweight 2-wave on the diff; commits as v1.2 of the entry-point letter.

**Tech Stack:** Same as parent — LaTeX `article`, plain `natbib`, `pdflatex` + `bibtex`, `booktabs` (for any compact reference table that survives), `amsmath` (for the centered model equations).

---

## REVISION-C corrections (verbatim from user 2026-05-06)

### Correction 3 — §1 restructure: bulleted Motivation → Problem → Suggested Solution → Challenges, then flow into §2

> "This section I want to be more like a bullet points of motivation, problem, suggested solution and then introduce the challenges and then show the model specifications and the failures as suggested."

The current `letter.tex` §1 is a prose section running ~1.5 pp (Purpose + Empirical-question subsection + iteration-count paragraph). Replace with a tight **bulleted structure** that compresses §1 to ~0.75–1 pp and flows directly into §2 (the equation-block iteration record per Correction C-1):

1. **Motivation** — one bullet: who the population is and why this work exists (LATAM digital workers paid in COP, USD-denominated AI/API/cloud/SaaS cost line, no existing bank product hedges this).
2. **Problem** — one bullet: the concrete risk in plain language (when COP weakens, the USD-denominated cost translates into unbudgeted COP expenditure; the worker has no hedging instrument calibrated to a hundred-to-low-thousands-USD monthly notional).
3. **Suggested solution** — one bullet: the framework's contribution as parametric FX-cost-insurance products underwritten on validated macro risks `X`; on-chain settlement is implementation infrastructure, deferred to the 37-page companion §4.
4. **Challenges** — short bulleted list of the open methodological questions that motivated this letter (one bullet per ask in §4: identification, convex-payoff-sufficiency under insurance-underwriting standard, multi-Y differential calibration, anti-fishing protocol defensibility, cross-iteration FWER + iteration-selection bias). Each bullet is one line — a forward pointer to §4, not a self-contained ask.
5. **Bridge to §2** — one closing line: "We have run five iterations to date, all closed or parked; the model specifications, results, and failure post-mortems follow in §2."

The wage→capital paragraph from the user's stylistic anchor (`mendieta_munoz_2017`, `rodrik_2016`, `mcmillan_rodrik_2011` citations) is **preserved** but compressed into the Motivation bullet (one sentence with the three citations) — the full prose paragraph stays in the 37-page companion §1. The user's anchor is what the citation-leaning register should look like, not a verbatim-preservation requirement here.

NO ideology mentions. NO post-Keynesian / neoclassical language. NO §1 sub-headings (the bullet structure replaces them).

### Correction 4 — §4 Supervisor-asks reframe: concrete asks, not methodological debate

> "The ask is for suggested specifications, risks, bibliography, connections of people interested on working on this."

The current `letter.tex` §4 ("Five methodological questions") presents five abstract econometric questions (identification, convex-payoff sufficiency, multi-Y calibration, anti-fishing protocol defensibility, cross-iteration FWER). Replace with **four concrete, practical asks** that match what a supervisor giving guidance to a junior research student would actually be asked to provide:

1. **§4.1 Suggested specifications.** "What specifications should the next iteration adopt?" — prompts the supervisor to recommend the (Y, X) pair, lag structure, sample window, primary inference convention, and robustness arms for the next round of work. Concrete actionable output expected: a pre-registration draft for iteration #6 informed by the supervisor's read of the closed five.
2. **§4.2 Risks.** "Which methodological risks should we flag that the present iteration roster does not address?" — the previous §4's five methodological-question content is repositioned here as risks the project has *already* identified (cross-iteration FWER, identification posture, convex-payoff sufficiency under insurance underwriting, multi-Y differential calibration, anti-fishing protocol defensibility). The supervisor is asked to add risks we have not flagged.
3. **§4.3 Bibliography.** "What references should we be reading?" — prompts the supervisor to point to literature he considers load-bearing for the framework's empirical work. The current `refs.bib` is the project's own reading; the supervisor's recommendations augment it for the next iteration.
4. **§4.4 Connections of interested people.** "Whom should we connect with?" — prompts the supervisor to introduce the project to other researchers, practitioners, or institutions who may have complementary expertise (parametric-insurance underwriters, FX-derivatives operators in LATAM, on-chain-settlement engineers, applied econometricians working on premature deindustrialization). This is network-introduction request, not a content-debate request.

Target: ~½ pp per ask → ~2 pp for §4 total. Net page count effect: §4 contracts from ~3 pp to ~2 pp; offsets the §1 contraction (Correction C-3) and the §2 expansion (Correction C-1).

The **content** of the previous five methodological questions is preserved IN §4.2 RISKS (as risks-the-project-has-flagged); none of the methodological substance is lost, only repositioned. The 37-page companion §7 retains the full methodological-question elaboration unchanged for the supervisor's reference.

### Correction 1 — §2 Five Iterations: drop the table; render each iteration as an equation block

> "The five iterations is best presented as the model equation centered for each iteration, reference to the data on the repo and the test results and interpretation and why it fails. I do not like the table for [this]."

The current `letter.tex` §2 uses a `booktabs` table with five rows × five columns (population, (Y, X) pair, verdict, headline number, one-line caveat). Replace with a sequence of paragraph-blocks, one per iteration, each containing:

1. **Heading line** — iteration name + verdict label (e.g., "Pair D (Section G–T broad services × COP/USD lag) — PASS").
2. **Centered model equation** — the actual estimating equation in `\[...\]` display math, with sub-/super-script discipline (`\hat{\beta}_{\mathrm{composite}}`, `\mathrm{logit}`, etc.). For monthly iterations: `\[ Y_t = \alpha + \beta_6 X_{t-6} + \beta_9 X_{t-9} + \beta_{12} X_{t-12} + \varepsilon_t \]` with a where-clause defining `Y_t` and `X_{t-k}` per-iteration.
3. **Data reference** — repo path of the canonical panel + sha256 + sample (N, window). E.g., "Data: `notebooks/dev_ai_cost/data/panel_combined.parquet` (sha `451f4c61…740d`, N=134, 2015-01 to 2026-02)."
4. **Test result** — headline numbers in compact form: `\hat{\beta}_{\mathrm{composite}} = +0.137`, HAC SE 0.025, t=+5.55, one-sided p ≈ 1.5e-8.
5. **Interpretation** — one sentence on what the result says about the transmission hypothesis.
6. **Why it fails (or what caveats apply on a PASS)** — the load-bearing post-mortem: for FAILs, what specifically rejected the spec (sign-flip, near-zero β, etc.); for PASSes, the inherited Reality-Checker FLAGs (correlation-not-causal, regime-mix, lag-6 dominance, verdict-sensitivity-to-design); for EXIT, the kill criteria that fired; for PARKED, why the apparatus was preserved without a graduating claim.

Target: ~½ page per iteration → ~2.5 pp for §2 total. Slight expansion vs the table's ~1.5 pp.

### Correction 2 — §3 Hedge-target Lemma: REMOVE for v1.2

> "The hedge target proposition is not necessary yet, in the sense that the real target is hedging the risk exposure due to fx volatility of this population with COP cash-flows and USD debt obligations exposures."

The current `letter.tex` §3 ("The hedge-target proposition") presents the abstract Abrigo Lemma `Y_inequality(t) = R_a(t) − R_c(t)` in a `lemma` environment + 2-sentence framing. **Remove this section entirely from the entry-point letter.** The Lemma proposition stays in the 37-page companion (`main.tex` §3, unchanged) for the supervisor to reference if interested.

Replace with a SHORT framing paragraph (≤ ½ pp, possibly absorbed into §1 or as a brief §3 stub) that states the **concrete risk target in plain economic language**:

> "The risk target is the FX-volatility exposure faced by an identifiable population: workers whose income is denominated in Colombian pesos (COP cash-flows) but whose recurring professional-input obligations are denominated in US dollars (USD-denominated AI / API services, cloud compute, software-as-a-service spend). When the COP weakens against the USD, the USD-denominated cost line translates into an unbudgeted increase in the worker's monthly COP expenditure. The intermediation product target is a contract that compensates for this FX-pass-through cost shock, denominated in a unit the worker actually spends (COP, or a COP-pegged purchasing-parity stablecoin). The Abrigo Lemma's abstract differential framing — present in the 37-page technical companion §3 — is the eventual analytical generalisation; the entry-point letter introduces the concrete target only."

No `lemma` environment in the letter. No proposition box. No two-sided market argument. The supervisor can pull the Lemma from the companion if he wants the formal generalisation.

---

## Spec coverage

This sub-plan amends the parent spec at `docs/specs/2026-05-06-supervisor-review-document-design.md` with a new sub-section recording REVISION-C, then governs the implementation. Spec-amendment is the first action in Task A.

The parent plan's §3 section structure (12 sections of the 37-page companion) is unchanged. Only the 8-page `letter.tex` is modified.

---

## File structure

| Path | Status | Purpose |
|---|---|---|
| `docs/specs/2026-05-06-supervisor-review-document-design.md` | modify | Add REVISION-C sub-section recording the two corrections (Task A.1) |
| `scratch/2026-05-06-supervisor-review/brief-revC-iterations.md` | create | Data-Methodology brief: produce 5 equation blocks for §2 |
| `scratch/2026-05-06-supervisor-review/brief-revC-population.md` | create | Econ-Writer brief: produce concrete-risk-target paragraph for §3 (or §1 absorption) |
| `scratch/2026-05-06-supervisor-review/agent-output-letter-revC-iterations.tex` | create (agent output) | Data-Methodology equation-block output |
| `scratch/2026-05-06-supervisor-review/agent-output-letter-revC-population.tex` | create (agent output) | Econ-Writer concrete-risk-target output |
| `docs/supervisor-review/letter.tex` | modify | Replace §2 + §3 with REVISION-C content |
| `docs/supervisor-review/2026-05-06-supervisor-letter.pdf` | rebuild | Re-compiled letter v1.2 (~7-9 pp depending on equation-block density) |
| `/tmp/wave1_rc_letter_revC.md` | scratch (verification) | Wave-1 Reality Checker on the REVISION-C diff |

NO new files in `refs.bib`. Equation blocks may need additional citations (panel sha references, but these are repo paths, not bib entries).

---

## Tasks

### Task A: Spec amendment + REVISION-C briefs

**Files:**
- Modify: `docs/specs/2026-05-06-supervisor-review-document-design.md` (add REVISION-C sub-section)
- Create: `scratch/2026-05-06-supervisor-review/brief-revC-iterations.md`
- Create: `scratch/2026-05-06-supervisor-review/brief-revC-population.md`

- [ ] **Step A.1: Spec amendment**

Append a new sub-section after §3.8 (the existing §3.8 is "Request for Guidelines"). New sub-section:

```markdown
### §3.10 Entry-Point Letter — REVISION-C corrections (2026-05-06)

This sub-section records two user-given corrections that apply to the
8-page entry-point letter (`docs/supervisor-review/letter.tex` →
`2026-05-06-supervisor-letter.pdf`), NOT to the 37-page technical
companion. The companion remains unchanged and continues to host the
full Lemma derivation, the on-chain primer, the methodology section,
and all four appendices. The entry-point letter is what the supervisor
reads first; the companion is referenced.

**Correction C-1 (§2 Five Iterations — equation-block format).** The
letter's §2 currently uses a `booktabs` table. Replace with a sequence
of paragraph-blocks, one per iteration, each containing:

1. Heading line (iteration name + verdict).
2. Centered model equation (`\[...\]` display math; sub-/super-script
   discipline: `\hat{\beta}_{\mathrm{composite}}`, `\mathrm{logit}`).
3. Data reference (repo path + sha256 + sample).
4. Test result (compact headline numbers).
5. One-sentence interpretation.
6. Why it fails (FAIL / EXIT) or what caveats apply (PASS) or why parked
   (PARKED).

Target: ~½ page per iteration → ~2.5 pp for §2.

**Correction C-2 (§3 Hedge-target Lemma — REMOVE for v1.2).** The
letter's current §3 presents the abstract Abrigo Lemma in a `lemma`
environment. Remove this section from the entry-point letter. Replace
with a short framing paragraph (≤ ½ pp) stating the concrete risk
target in plain language:

> The risk target is FX-volatility exposure for a specific population:
> Latin-American digital workers paid in Colombian pesos (COP
> cash-flows) but carrying recurring USD-denominated professional-input
> obligations (subscription AI services, API usage fees, cloud
> compute, software-as-a-service spend). When the COP weakens against
> the USD, the USD-denominated cost line translates into an unbudgeted
> COP-expenditure increase. The intermediation product target is a
> contract that compensates for this FX-pass-through cost shock,
> denominated in a unit the worker actually spends (COP, or a
> COP-pegged purchasing-parity stablecoin).

The Lemma's abstract `Y_inequality(t) = R_a(t) − R_c(t)` framing is
preserved in the 37-page companion §3 for supervisor reference; the
entry-point letter does not invoke it.

**Correction C-3 (§1 — bulleted Motivation/Problem/Suggested-solution/
Challenges/Bridge).** The letter's current §1 is prose (~1.5 pp).
Replace with a 5-item `description` list in the order Motivation →
Problem → Suggested solution → Challenges → Bridge to §2. The
wage→capital citations (`mendieta_munoz_2017`, `rodrik_2016`,
`mcmillan_rodrik_2011`) compress into the Motivation bullet.
Challenges bullet is a sub-list of forward pointers to §4 sub-asks.
NO ideology mentions. Target ~0.75–1 pp.

**Correction C-4 (§4 — supervisor-asks reframe to four concrete
asks).** The letter's current §4 ("Five methodological questions") is
replaced with FOUR concrete asks: §4.1 Suggested specifications, §4.2
Risks (which absorbs the prior five methodological questions as
risks-the-project-has-flagged + adds Stambaugh-bias and empalme
residual bias as further flagged risks), §4.3 Bibliography, §4.4
Connections of interested people. Target ~½ pp per ask, ~2 pp total.
The 37-page companion §7 retains the full methodological-question
content unchanged for supervisor reference.

**Out of scope for REVISION-C.** No changes to the §Purpose preamble
or the Closing of `letter.tex`. No changes to the 37-page companion.
No new bib entries. No changes to the spec's §5 anti-overclaim
invariants — the concrete-risk-target framing (C-2), the bulleted §1
restructure (C-3), and the four-ask reframe (C-4) strengthen rather
than weaken the "no marketing register / no Abrigo as product"
invariant by replacing abstract claims with plain-language exposure
descriptions and concrete actionable asks.
```

Commit message:

```
docs(spec): REVISION-C corrections to entry-point letter

User feedback 2026-05-06: §2 iteration table → equation-block format;
§3 Hedge-target Lemma removed from entry-point letter (preserved in
37-pp companion). Spec amendment in §3.10 records both corrections.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Per `feedback_two_wave_doc_verification`, run a LIGHTWEIGHT Wave-1 Reality Checker on the spec diff before commit (the change is small and additive; no full 2-wave needed).

- [ ] **Step A.2: Author `brief-revC-iterations.md` (Data-Methodology)**

The brief tells the Data-Methodology sub-agent to produce LaTeX for the FIVE equation blocks per Correction C-1. Brief content:

```markdown
# Section-Author Brief — REVISION-C iterations (Data-Methodology)

**Sub-agent type:** `Model QA Specialist`
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-letter-revC-iterations.tex`
**Length budget:** ~2.5 pp total (5 iterations × ~½ pp each)

## What to produce

A single LaTeX block (NO BEGIN/END markers needed — main thread will
splice as the entire §2 body) replacing the existing letter.tex §2
table. Five paragraph-blocks, one per iteration, in this order:
Pair D (PASS), dev-AI Stage-1 (FAIL), FX-vol-CPI-surprise (FAIL),
Phase-A.0 Remittance (EXIT_NON_REMITTANCE), P1 Bittensor SN18 (PARKED).

Per-iteration template:

\paragraph{<Iteration name> (<short scope> — <verdict>).}
[1-line population + (Y, X) pair description.]
\[ <model equation in display math> \]
where <where-clause defining Y_t and X_{t-k}>.
Data: \texttt{<repo path>} (panel sha \texttt{<short sha>}, N=<N>,
<window>).
Result: <compact test statistics>.
\textit{Interpretation.} <one sentence>.
\textit{<Caveat / why-it-fails / why-parked>.} <one to three sentences>.

## Source materials

1. `docs/supervisor-review/sections/06-log.tex` — the 37-page companion's
   §6 with full per-iteration blocks; condense each block's content into
   the equation-block format.
2. `memory/project_pair_d_phase2_pass.md` — Pair D ground truth.
3. `memory/project_dev_ai_section_j_fail.md` — dev-AI Stage-1 ground
   truth (CLOSED FAIL, β=−0.146; R2 Section M β=+0.455 reframes Pair D).
4. `memory/project_fx_vol_econ_gate_verdict_and_product_read.md` —
   FX-vol ground truth.
5. `memory/project_phase_a0_exit_verdict.md` — Phase-A.0 ground truth.
6. `memory/project_p1_sn18_spec_parked_for_record.md` — P1 ground truth.

## Equation conventions

- Monthly iterations (Pair D, dev-AI Stage-1) use the composite-β model:
  \[ Y_t = \alpha + \beta_6 X_{t-6} + \beta_9 X_{t-9} + \beta_{12} X_{t-12} + \varepsilon_t \]
  where \( Y_t = \mathrm{logit}(\text{share}_t) \) and
  \( X_{t-k} = \log(\mathrm{COP}/\mathrm{USD}_{t-k}) \).
- FX-vol-CPI uses the weekly RV-on-CPI-surprise model:
  \[ \mathrm{RV}^{\mathrm{COP/USD}}_{w} = \alpha + \beta\, \mathrm{Surp}^{\mathrm{CPI}}_{w-1} + \varepsilon_w \]
  where \( \mathrm{RV}_w \) is realised volatility in week \( w \) and
  \( \mathrm{Surp}^{\mathrm{CPI}}_{w-1} \) is the lagged CPI surprise.
- Phase-A.0 Remittance: render the originally pre-registered remittance-corridor specification per `memory/project_phase_a0_exit_verdict.md`:
  \[ \mathrm{RV}^{\mathrm{COP/USD}}_w = \alpha + \beta\, \Delta \mathrm{Remit}^{\mathrm{Col}}_{w-1} + \varepsilon_w \]
  where \( \mathrm{RV}_w \) is realised volatility in week \(w\) and \( \Delta \mathrm{Remit}^{\mathrm{Col}}_{w-1} \) is the lagged Colombian household-remittance flow change. The block then states explicitly that this specification was NEVER ESTIMATED — kill criterion k1 (X-driver fingerprint absent in remittance event-window data) and partial k2 (cCOP / COPM aggregate user activity is third-party-DEX volume, not Colombian household remittance) fired before estimation, producing the EXIT_NON_REMITTANCE label. The equation is rendered for completeness as the pre-registered specification; the result line should say "no empirical estimate produced — exited on kill criteria pre-estimation."
- P1 Bittensor SN18: event-study apparatus, no graduating empirical
  claim — render the apparatus equation only with a note that it never
  produced a verdict.

## Discipline

- LaTeX math: `\(...\)` inline only; `\[...\]` display only. NO unicode
  math. `\hat{\beta}_{\mathrm{composite}}` (mathrm not text).
- Citations: only for literature anchors if needed (Mendieta-Muñoz, etc.);
  repo paths and sha256 are `\texttt{...}`, NOT bib entries.
- The "why it fails" line is the load-bearing post-mortem. For Pair D,
  inherit the four RC FLAGs (correlation-not-causal, lag-6 dominance,
  regime-mix, verdict-sensitivity-to-design + the dev-AI R2 Section-M
  reframe). For dev-AI, name the sign-flip and the empalme residual
  bias. For FX-vol, name the primary FAIL and that A1/A4 sensitivities
  produced positive 90% CIs (not "main finding"). For Phase-A.0, name
  the kill criteria that fired and the EXIT_NON_REMITTANCE label. For
  P1, name "apparatus complete; no graduating empirical claim."
- NO ideology mentions (post-Keynesian, neoclassical, etc.). Project
  framing is concrete-risk-target only.
- NO Lemma proposition. The Y_inequality differential is NOT to be
  invoked here.

## Anti-overreach

You are NOT writing §1, §3, §4, Closing, or the spec / plan. You are
NOT modifying the 37-page companion. ONLY the §2 body of `letter.tex`.
Output is ~2.5 pp of LaTeX content.
```

- [ ] **Step A.3: Author `brief-revC-population.md` (Econ-Writer) — covers §1 bulleted restructure (C-3) + §3 Lemma replacement (C-2)**

The brief tells the Econ-Writer sub-agent to produce BOTH the §1 bulleted restructure (REVISION-C-3) AND the §3 Lemma replacement (REVISION-C-2). Both are Econ-Writer territory; bundling into one brief avoids cross-agent dependencies. Brief content:

```markdown
# Section-Author Brief — REVISION-C-3 + C-2 (Econ-Writer)

**Sub-agent type:** `Book Co-Author`
**Output file:** `scratch/2026-05-06-supervisor-review/agent-output-letter-revC-population.tex`
**Length budget:** §1 restructure ~0.75–1 pp; §3 replacement ≤ ½ pp; total ~1.25–1.5 pp.

## What to produce

A single LaTeX file with TWO top-level blocks:

```latex
% === BEGIN SECTION 1 ===
\section{Motivation, problem, suggested solution, challenges}\label{sec:1}
[bulleted §1 per Correction C-3]
% === END SECTION 1 ===

% === BEGIN SECTION 3 ===
[either \section{Risk-target framing}\label{sec:3} block per Correction C-2,
 OR an absorption note "the §3 replacement is folded into §1 bullet 3
 (Suggested solution); main thread should DELETE the existing §3 entirely
 from letter.tex and renumber §4 → §3" — judgment call.]
% === END SECTION 3 ===
```

If you choose the absorption path for §3, the §3 block should contain only the absorption-instruction sentence (no LaTeX content); the main thread will then delete the existing §3 from `letter.tex` and renumber `\section{Open methodological questions...}` from §4 to §3 + update any internal `\ref{sec:4}` to `\ref{sec:3}`.

If you choose the standalone-§3 path, the §3 block contains the actual replacement content per Correction C-2.

## §1 required structure (Correction C-3)

Render as `description` list or `itemize` list — not numbered. Five bulleted items:

1. `\item[Motivation.]` Who the population is and why this work exists.
   Single sentence with the Mendieta-Muñoz / Rodrik / McMillan-Rodrik
   citations compressed in (cite via `\citep{}`). One sentence: "We
   study Latin-American digital workers paid in Colombian pesos who
   carry recurring USD-denominated professional-input obligations
   (subscription AI services, API usage fees, cloud compute,
   software-as-a-service spend), a population for whom the path from
   wage income into productive-capital ownership has documented
   structural narrowing \citep{mendieta_munoz_2017,rodrik_2016,mcmillan_rodrik_2011}."
2. `\item[Problem.]` The concrete risk in plain language. Single
   sentence: "When the COP weakens against the USD, the
   USD-denominated cost line translates into unbudgeted COP
   expenditure, and no Colombian retail-bank product currently hedges
   the resulting FX-pass-through cost shock at the
   hundred-to-low-thousands-USD monthly notional these workers carry."
3. `\item[Suggested solution.]` The framework's contribution. Two
   sentences: "We identify the macro risks \(X\) that quantitatively
   produce these cost shocks, validate them empirically, and design
   parametric cost-insurance products that compensate for the
   FX-pass-through exposure
   \citep{carter_etal_2017,mahul_stutley_2010,clarke_2016}.
   The implementation venue is on-chain settlement infrastructure
   (described in the 37-page technical companion §4); on-chain is
   not the economic primitive."
4. `\item[Challenges.]` Bulleted sub-list, one bullet per ask in §4
   of the letter (= §7.1–§7.5 of the companion). Each sub-bullet is
   ONE LINE — a forward pointer, not a self-contained ask:
   - Identification (predictive vs causal; see §4.1).
   - Convex-payoff sufficiency under insurance-underwriting standard
     (see §4.2).
   - Multi-Y differential calibration; familywise vs false-discovery
     correction across legs (see §4.3).
   - Anti-fishing protocol defensibility — pre-registration thresholds
     `\(N_{\mathrm{MIN}}=75\)`, `\(\mathrm{POWER}_{\mathrm{MIN}}=0.80\)`,
     `\(\mathrm{MDES}_{\mathrm{SD}}=0.40\)` (see §4.4).
   - Cross-iteration familywise error and iteration-selection bias
     (see §4.5).
5. `\item[Bridge to §2.]` One closing line: "We have run five
   iterations to date, all closed or parked; the model
   specifications, results, and failure post-mortems follow in §2."

NO `\paragraph{...}` sub-headings. NO sub-section numbering. NO ideology
mentions. NO "post-Keynesian" or "neoclassical" anywhere.

## §3 required content (Correction C-2; if standalone-§3 path)

Per spec §3.10 Correction C-2 verbatim:

> The risk target is FX-volatility exposure for a specific population:
> Latin-American digital workers paid in Colombian pesos (COP
> cash-flows) but carrying recurring USD-denominated professional-input
> obligations. When the COP weakens against the USD, the
> USD-denominated cost line translates into an unbudgeted
> COP-expenditure increase. The intermediation product target is a
> contract that compensates for this FX-pass-through cost shock,
> denominated in a unit the worker actually spends (COP, or a
> COP-pegged purchasing-parity stablecoin). The Abrigo Lemma's abstract
> `\(Y_{\mathrm{inequality}}(t) = R_a(t) - R_c(t)\)` framing — present
> in the 37-page technical companion §3 — is the eventual analytical
> generalisation; the entry-point letter introduces the concrete target
> only.

If absorption-path is chosen, the §3 content is folded into the §1
bullet 3 (Suggested solution) and the standalone §3 is deleted; in
that case the §3 block in your output is just the absorption-instruction
sentence for the main thread.

## Discipline

- NO `lemma` environment anywhere in this output.
- NO `\(Y_{\mathrm{inequality}}(t) = R_a(t) - R_c(t)\)` equation in
  display form (the inline reference in §3 above is permitted as an
  identity hand-off to the companion).
- NO ideology mentions.
- Plain language; concrete population + concrete cost line + concrete
  hedge target throughout.
- LaTeX math: `\(...\)` inline only. NO unicode math characters. NO
  bare `$...$`. NO display math in §1 or §3 (the §2 equation blocks are
  Data-Methodology's domain).
- Citations: `\cite{key}` / `\citet{key}` / `\citep{key}` — natbib only.

## §4 required content (Correction C-4) — added 2026-05-06

The Econ-Writer brief is EXTENDED to cover §4 reframe per Correction C-4. Add a third top-level block to the output:

```latex
% === BEGIN SECTION 4 ===
\section{Asks}\label{sec:4}
[four sub-asks per Correction C-4: Suggested specifications, Risks, Bibliography, Connections]
% === END SECTION 4 ===
```

Length budget: ~½ pp per ask → ~2 pp total. Each ask:

- **§4.1 Suggested specifications.** Two-sentence ask: "We invite the supervisor to suggest the (Y, X) pair, lag structure, sample window, primary inference convention, and robustness arms for the next iteration. Specifically: which sectoral cut should follow the Pair D / dev-AI G–T / J split given the R2 Section M signal; whether to repeat the FX-vol-on-CPI-surprise primary at A1 monthly cadence as the next pre-registration; or whether to pivot to a non-Colombian LATAM panel."
- **§4.2 Risks.** Bulleted list — these ARE the previous §4's five methodological questions, repositioned as risks the project has already identified, with one-sentence each. The supervisor is asked to add risks the project has not flagged. Bullets:
  - Identification posture (predictive-regression versus structural-causal; T1 exogeneity rejected on FX-vol; HAC fixed-`L` per iteration).
  - Convex-payoff sufficiency under insurance-underwriting standard (mean-`\(\hat{\beta}\)` necessary not sufficient; Carter et al. 2017 / Mahul-Stutley 2010 / Clarke 2016 standards).
  - Multi-Y differential calibration (joint-leg correlation, FWER vs FDR, regime-switching).
  - Anti-fishing protocol defensibility (`\(N_{\mathrm{MIN}}=75\)`, `\(\mathrm{POWER}_{\mathrm{MIN}}=0.80\)`, `\(\mathrm{MDES}_{\mathrm{SD}}=0.40\)` inherited from Phase-A.0 Rev-5.3.1, not re-derived).
  - Cross-iteration FWER and iteration-selection bias (5 closed iterations; meta-multiple-comparison concern).
  - Stambaugh small-sample bias on persistent-regressor predictive regressions (log-FX is near-unit-root at monthly frequency).
  - Empalme residual bias (DANE Marco-2018 methodology break not fully neutralised; surfaced in dev-AI Stage-1 NB02 Trio 1 boundary anomaly).
- **§4.3 Bibliography.** One-paragraph ask: "The current bibliography is documented in the 37-page companion's Appendix B and is reproduced as `refs.bib`. We invite the supervisor to recommend additional references he considers load-bearing for the framework's empirical work, particularly on (a) parametric-index insurance pricing in low-counterparty-credit-standing populations, (b) sectoral employment-share predictive regressions on real-effective-exchange-rate panels, and (c) cross-iteration false-discovery-rate correction regimes for observational pre-registration."
- **§4.4 Connections of interested people.** One-paragraph ask: "We invite the supervisor to introduce the project to other researchers, practitioners, or institutions whose work might complement this iteration roster — including but not limited to parametric-insurance underwriters with LATAM exposure, FX-derivatives operators serving sub-corporate notionals, on-chain settlement engineers, and applied econometricians working on premature deindustrialization in Latin America. The framework's empirical work is open to collaboration; the supervisor's network is the most efficient channel for identifying complementary contributors."

Discipline (additional to the discipline already specified for §1 / §3):
- §4 has NO display equations (the equations live in §2; §4 is asks).
- Per-ask paragraphs, not numbered enumerations within the asks (sub-asks are bulleted only inside §4.2 Risks).
- The five methodological-question content from the previous v1.1 §4 is REPOSITIONED into §4.2 bullets — none of it is lost; check against the previous `letter.tex` §4.1–§4.5 to verify each bullet captures the corresponding prior question's load-bearing content.
- Heckman 1979 (`heckman_1979`) may appear in §4.2's iteration-selection-bias bullet if you cite it; bib already contains it.

## Anti-overreach

ONLY §1, §3, and §4 of `letter.tex`. Do NOT touch §2 (Data-Methodology's
domain — see `brief-revC-iterations.md`), do NOT touch the
Closing or the §Purpose preamble. Do NOT touch the 37-page companion
or the spec / plan.
```

- [ ] **Step A.4: Light Wave-1 RC verification on spec diff + commit Task A**

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git diff docs/specs/2026-05-06-supervisor-review-document-design.md > /tmp/spec-revC.diff
```

Dispatch a single Reality Checker review of the diff (≤ 200 words; ACCEPT or FLAG). If ACCEPT, commit Task A:

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git add docs/specs/2026-05-06-supervisor-review-document-design.md
git commit -m "docs(spec): REVISION-C corrections to entry-point letter

(commit message body per Step A.1)"
```

Briefs in `scratch/` are NOT committed (per `feedback_two_wave_doc_verification` "Out of scope" rule).

---

### Task B: Dispatch + stitch + recompile + commit

**Files:**
- Modify: `docs/supervisor-review/letter.tex` (replace §2 + §3 content)
- Rebuild: `docs/supervisor-review/2026-05-06-supervisor-letter.pdf`

- [ ] **Step B.1: Dispatch the two re-author agents in parallel**

Single message with two `Agent` calls:

Agent 1 (`Model QA Specialist`):
- description: "REVISION-C iteration equation blocks"
- subagent_type: `Model QA Specialist`
- prompt: contents of `scratch/2026-05-06-supervisor-review/brief-revC-iterations.md`

Agent 2 (`Book Co-Author`):
- description: "REVISION-C population framing"
- subagent_type: `Book Co-Author`
- prompt: contents of `scratch/2026-05-06-supervisor-review/brief-revC-population.md`

- [ ] **Step B.2: Verify both agent outputs landed (with missing-output halt branch per Wave-2 PM FLAG-LOW)**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/scratch/2026-05-06-supervisor-review
ls -la agent-output-letter-revC-*.tex
```

Verification cases:

| Output | Action |
|---|---|
| Both files present, both > 1 KB, both contain expected `% === BEGIN` markers | proceed to Step B.3 |
| One or both files missing | halt + report `BLOCKED`; re-dispatch the missing agent before proceeding |
| File present but < 1 KB OR `wc -l` < 5 | empty / truncated output; halt + report `BLOCKED`; re-dispatch with retry directive citing the empty-output failure |
| `% === BEGIN` markers absent | malformed envelope; halt + report `BLOCKED`; re-dispatch citing the marker-absence failure |

After file-presence verification, smoke-test for unicode math leakage and bare `$...$`:

```bash
grep -lE '[βσραΣ∈≤≥≠⊂⊆∩∪∀∃]' agent-output-letter-revC-*.tex || echo "OK no unicode"
grep -nE '\$[^$]+\$' agent-output-letter-revC-*.tex | grep -v '^[^:]*:[^:]*:%' || echo "OK no bare \$ outside comments"
```

If either check fails (excluding comment-only false positives), re-dispatch the offending agent with a notation-cleanup directive (per Plan Task 4 step 3b precedent). Iteration cap: 2 retries per agent; after the second failure, halt and escalate to user.

- [ ] **Step B.3: Stitch into `letter.tex` (with absorption-branch label discipline per Wave-1 RC NIT + Wave-2 PM NIT)**

This is a surgical edit, NOT a re-stitch of all section files. The `letter.tex` is a single self-contained file (not split into `sections/`).

**Stitch sequence:**

1. Use `Read` to locate the existing §1, §2, §3, §4 boundaries in `letter.tex`. Note all `\label{sec:N}` and `\ref{sec:N}` instances.
2. Use `Edit` to replace the §1 body with the bulleted content from `agent-output-letter-revC-population.tex` BEGIN/END SECTION 1 block (per Correction C-3).
3. Use `Edit` to replace the §2 body with the equation-block content from `agent-output-letter-revC-iterations.tex` (per Correction C-1).
4. **Decide §3 path:** read `agent-output-letter-revC-population.tex` BEGIN/END SECTION 3 block. If the agent chose the **standalone-§3 path** (the block contains real LaTeX content), use `Edit` to replace the §3 body with that content (per Correction C-2). If the agent chose the **absorption path** (the block contains only an absorption-instruction sentence), perform a **deletion + renumbering pass**:
   - DELETE the entire `\section{The hedge-target proposition}\label{sec:3}` section from `letter.tex`.
   - Re-number `\section{Five methodological questions}\label{sec:4}` to `\label{sec:3}`.
   - `grep -n '\\ref{sec:4}' letter.tex` and update each match to `\ref{sec:3}`.
   - `grep -n '\\ref{sec:3}' letter.tex` and inspect — any remaining references that pointed to the deleted §3 should be re-routed (typically to the §1 bullet-3 absorption target or to the 37-pp companion §3 cross-reference).
5. Use `Edit` to replace the §4 body (now §3 if absorption-path was chosen) with the four-ask content from `agent-output-letter-revC-population.tex` BEGIN/END SECTION 4 block (per Correction C-4). The four asks (Suggested specifications / Risks / Bibliography / Connections) replace the prior five methodological questions.
6. After all edits, run `grep -nE '\\\\(label|ref)\{sec:' letter.tex | sort -u` to verify every `\label` is matched by at least one `\ref` (or is a top-level section) and every `\ref` resolves to an existing `\label`. Manually fix any orphans.

**Absorption-path label discipline (load-bearing per Wave-2 PM NIT):** If §3 absorption is chosen, the renumbering pass is the gating step. Forgetting to update `\ref{sec:4}` instances will produce broken cross-references in the compiled PDF (typically rendered as `??`), which the supervisor will read as an undisciplined draft. Verify ALL `\ref{sec:4}` are updated before recompile.

- [ ] **Step B.4: Recompile (with compile-error HALT branch per Wave-2 PM FLAG-LOW; bibtex non-zero is hard-error not silent-pass)**

```bash
cd /home/jmsbpp/apps/abrigo-analytics/docs/supervisor-review
set -e
pdflatex -interaction=nonstopmode letter.tex
# bibtex: non-zero exit = hard-error after stitch (NOT silent-pass).
# Real \cite{} calls land in §1 (citations: mendieta_munoz_2017, etc.) —
# bibtex should resolve them all. Wave-2 PM NIT: || true masks
# missing-cite warnings post-stitch. Removed.
bibtex letter
pdflatex -interaction=nonstopmode letter.tex
pdflatex -interaction=nonstopmode letter.tex
set +e
# Compile-error HALT branch (per Wave-2 PM FLAG-LOW): even with
# nonstopmode, fatal errors in main.log require explicit detection.
if grep -qE "^!|Undefined control sequence|Missing |LaTeX Error" letter.log; then
    echo "FATAL: compile errors detected in letter.log"
    grep -E "^!|Undefined control sequence|Missing |LaTeX Error" letter.log | head -10
    echo "Halting Step B.4; report BLOCKED."
    exit 1
fi
if grep -qE "Citation .* undefined" letter.log; then
    echo "FATAL: undefined citations after bibtex pass:"
    grep -E "Citation .* undefined" letter.log | head -5
    echo "Halting Step B.4; report BLOCKED — fix the missing citation key in refs.bib OR remove the \\cite{} call."
    exit 1
fi
if grep -qE "Reference .* undefined" letter.log; then
    echo "FATAL: undefined references after triple-pass:"
    grep -E "Reference .* undefined" letter.log | head -5
    echo "Halting Step B.4; report BLOCKED — likely a broken \\ref{sec:N} from the absorption-path renumbering in Step B.3."
    exit 1
fi

if [[ -f letter.pdf ]]; then
    mv letter.pdf 2026-05-06-supervisor-letter.pdf
    pdfinfo 2026-05-06-supervisor-letter.pdf | grep Pages
else
    echo "FATAL: letter.pdf not produced; check letter.log"
    exit 1
fi
```

Page-count decision rule (relaxed from parent plan's 30-40 since this is the 8-pp letter):

| Page count | Action |
|---|---|
| 6 ≤ N ≤ 9 | **ACCEPT** — within tolerance band of the user's "8 pages max" instruction (slight flexibility for the equation-block expansion). |
| N = 10 | **SOFT REVIEW** — accept if the supervisor-asks (§4) couldn't be cut without losing methodological substance; otherwise tighten the iteration blocks (cut the where-clause repetition; merge the FX-vol and Phase-A.0 blocks if vestigial). |
| N > 10 | **HARD HALT** — material overrun; report to user; offer to cut a question or compress an iteration. |

- [ ] **Step B.5: Light Wave-1 RC verification on the new PDF**

Dispatch one Reality Checker review (≤ 200 words; ACCEPT / FLAG). Scope: did §2 equation blocks accurately reproduce the verdicts from the source memory? Did §3 framing drop the Lemma without inheriting its content silently? Did the page count land in [6, 9]? Did the unicode-math sweep stay clean?

If ACCEPT, proceed to commit. If FLAG, integrate inline and re-verify.

- [ ] **Step B.6: Commit Task B**

```bash
cd /home/jmsbpp/apps/abrigo-analytics
git add docs/supervisor-review/letter.tex docs/supervisor-review/2026-05-06-supervisor-letter.pdf
git commit -m "docs: supervisor letter v1.2 — REVISION-C (equation blocks + concrete risk target)

User feedback 2026-05-06: §2 table → equation-block format (one block
per iteration: model equation + repo data ref + test result +
interpretation + why it fails); §3 Hedge-target Lemma removed and
replaced with concrete risk-target framing (COP-cash-flow population
with USD-denominated obligations, FX-pass-through cost shock).

The 37-page companion at 2026-05-06-empirical-record-letter.pdf is
unchanged; the Lemma's abstract Y_inequality(t) = R_a(t) - R_c(t)
framing is preserved there for supervisor reference.

Implements REVISION-C per spec §3.10 amendment + sub-plan
docs/sub-plans/2026-05-06-supervisor-letter-revC-corrections.md.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Self-review

| REVISION-C requirement | Sub-plan task |
|---|---|
| C-1 §2 equation-block format with model + data + result + interpretation + why-fails per iteration | Task A.2 (brief) → Task B.1 (dispatch Data-Methodology) → Task B.3 step 3 (stitch §2) |
| C-2 §3 Lemma removal + concrete-risk-target replacement (standalone or absorbed) | Task A.3 (brief, §3 block) → Task B.1 (dispatch Econ-Writer) → Task B.3 step 4 (stitch §3 with absorption-branch) |
| C-3 §1 bulleted restructure (Motivation/Problem/Suggested solution/Challenges/Bridge) | Task A.3 (brief, §1 block) → Task B.1 (dispatch Econ-Writer) → Task B.3 step 2 (stitch §1) |
| C-4 §4 supervisor-asks reframe (Suggested specifications / Risks / Bibliography / Connections) | Task A.3 (brief, §4 block) → Task B.1 (dispatch Econ-Writer) → Task B.3 step 5 (stitch §4) |
| Spec amendment recording all four corrections | Task A.1 (§3.10 spec amendment covers C-1, C-2, C-3, C-4) |
| Lightweight verification (1-wave RC) before commit | Task A.4 (spec diff Wave-1) + Task B.5 (assembled letter Wave-1) |
| Page count within user's 8-pp guidance | Task B.4 decision rule (6 ≤ N ≤ 9 ACCEPT) |
| Hardenings from sub-plan-Wave-2 PM findings | Task B.2 missing-output halt branch; Task B.3 absorption-label discipline; Task B.4 compile-error HALT + bibtex non-zero hard-error |
| Phase-A.0 equation TBD resolution from sub-plan-Wave-1 RC NIT | Task A.2 brief resolves: render pre-registered remittance-corridor specification with explicit "never estimated; exited on kill criteria pre-estimation" annotation |
| 37-page companion preserved unchanged | Out of scope by construction; spec §3.10 explicitly so |
| Agent outputs uncommitted (sub-plan-Wave-2 PM FLAG-LOW) | INTENTIONAL per `feedback_two_wave_doc_verification` "Out of scope" rule for `scratch/` artifacts; agent outputs preserved on disk for the duration of the sub-plan execution and referenced in the final commit message footer for audit traceability |

**Placeholder scan:** No TBDs, no "fill in details," no vague specifications. Spec-amendment text + brief contents are reproduced verbatim in this sub-plan.

**Type consistency:** File paths consistent (`scratch/2026-05-06-supervisor-review/agent-output-letter-revC-{iterations,population}.tex`). Subagent types (`Model QA Specialist`, `Book Co-Author`) match the parent plan's roster. Spec section numbering (§3.10 follows the existing §3.1–§3.9 + §4–§8 structure of the parent spec).

**Scope check:** Single subsystem (the entry-point letter only). No spec section without a covering task. No task expands beyond the two REVISION-C corrections.

---

## Out of scope for this sub-plan

- The 37-page technical companion (`main.tex` → `2026-05-06-empirical-record-letter.pdf`) — unchanged.
- The implementation plan `docs/plans/2026-05-06-supervisor-review-document-implementation.md` — unchanged.
- Any new bib entries — none expected.
- Re-running the full three-way verification on the letter — Wave-1 RC alone is the verification gate for REVISION-C (the change is small and the parent doc has already passed full 3-way).
- The supervisor's response — unchanged from parent spec §8.
