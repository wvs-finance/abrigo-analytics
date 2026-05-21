# E10 Q-Process Calibration-Anchor Extraction — NON-FANTASY Trace

**Date:** 2026-05-20
**Task:** E10 v0.4 implementation-plan task 2.2 preparation (Phase-2 data-mining).
**Purpose:** Extract the user's real, Claude-Code-mediated data-query workflow to
serve as the NON-FANTASY calibration anchor for the E10 GSPS simulator's Q-process
(spec v0.6 §6.2). Q = monthly data-query volume — the ONLY simulated quantity in E10.
**Posture:** This artifact PRODUCES the calibration anchor. It does NOT build the
simulator or run Phase 2.
**Scope decision:** user, 2026-05-20 — CENTRE = abrigo-analytics project sessions;
BRACKET = a representative sample of the user's other Claude Code projects.

---

## 0. Headline verdict

- **Trace is GENUINE and NON-TRIVIAL** — it clears the spec §7 field-7a HALT gate.
  The centre yields 63 real, timestamped data-query tool calls across 4 sessions /
  4 active days, with the bracket adding 151 more across 7 sessions / 12 active days.
  The trace exhibits every one of the five §6.3 λ(t) modulations the simulator must
  carry. **Phase 2 is NOT HALTed on anchor grounds.**
- **Q is OVERDISPERSED, decisively.** Daily-count variance-to-mean ratio (VMR) is
  **20.6 (centre)** and **19.8 (bracket)** — roughly 20× the equidispersed-Poisson
  value of 1.0. This directly settles plan task 2.3a: the overdispersion mechanism
  is required, not optional.
- **Data-query mapping (1 line):** a tool call counts as an x402-priceable data
  query iff it fetches data from a network-external source — `WebFetch`, `WebSearch`,
  read-only data MCP calls (`mcp__dune/github/arxiv/somnia/bigquery__*`), and `Bash`
  commands that are `curl`/`wget`/`cast`-RPC HTTP fetches; all local-state and
  authoring tools (`Edit`, `Write`, `Read`, non-fetch `Bash`, `Task*`, `Agent`,
  and MCP *write* ops) are excluded.

---

## 1. Transcripts enumerated

### 1.1 Centre — abrigo-analytics

Three on-disk project directories map to the abrigo-analytics project across its
path history; all three are folded into the CENTRE:

| Project dir | jsonl files | mined |
|---|---|---|
| `-home-jmsbpp-apps-d2p-abrigo-abrigo-analytics` (current path) | 4 | yes |
| `-home-jmsbpp-apps-abrigo-analytics` (prior path) | 7 | yes |
| `-home-jmsbpp-apps-d2p-abrigo-abrigo-analytics-notebooks` | 1 | yes |

**Centre total: 12 JSONL files, ~50 MB.** 63 data-query tool calls extracted,
distributed across 4 sessions that actually contain data queries (the other 8
files are authoring/planning sessions with zero network fetches — consistent with
this repo being analytics/spec work, not live data-pull work).

### 1.2 Bracket — representative sample of other projects

Sampled 6 non-abrigo project directories spanning the user's domain range
(Solidity contract dev, frontend, post-Keynesian theory, CFMM linear algebra,
work tools, home/general):

| Project dir | jsonl files |
|---|---|
| `-home-jmsbpp-apps-ThetaSwap-thetaSwap-core-dev--worktree-ranFromAngstrom` | 5 |
| `-home-jmsbpp-apps-d2p-frontend` | 2 |
| `-home-jmsbpp-learning-post-keynesian` | 1 |
| `-home-jmsbpp-learning-cfmm-theory-cfmm-linear-algebra` | 1 |
| `-home-jmsbpp-work-tools` | 2 |
| `-home-jmsbpp` | 11 |

**Bracket total: 22 JSONL files, ~46 MB.** 151 data-query tool calls extracted
across 7 query-bearing sessions / 12 active days.

**Sampling note.** All JSONL files in each sampled directory were fully parsed
line-by-line (no within-file sampling was needed — total volume ~96 MB is
tractable). The bracket *directory* selection is the only sampling step: 6 of the
~16 non-abrigo project dirs were chosen for domain spread. This is documented as a
deliberate, representative subset, not an exhaustive census — consistent with the
bracket's role as a calibration RANGE, not the centre.

---

## 2. Data-query mapping — `[brainstorm-judgment]` decision

This is the load-bearing classification: it determines what counts toward Q.

### 2.1 Decision-citation block (4-part)

> **Reference:** E10 spec v0.6 §6.2 (the NON-FANTASY anchor — "the user's own
> observed data-query logs"); §4.2 (`cost = Q × $0.01 × FX`, Q = monthly
> data-query volume); §2.2 (Q = "monthly data-query volume"); the x402
> methodology anchor (The Graph Gateway `exact`-scheme offer: $0.01 USDC *per
> query*, flat); `memory/feedback_dune_last_resort_exhaust_free_resources.md`.
>
> **Why this mapping:** E10's Q is, by spec construction, the count of
> *priceable data fetches* — the events that would each incur one $0.01 USDC
> x402 charge if the analyst's workflow were settled on a pay-per-query data
> substrate. The user's real data-gathering workflow is mediated entirely by
> Claude Code: every time the user (via Claude) reaches out to a network-external
> data source, that is one query event in the x402 sense. The classification
> must therefore include exactly the tool calls that hit an *external data
> endpoint* and exclude everything that touches only local state or authors
> artifacts. A `WebFetch` of a central-bank JSON, a `mcp__dune__executeQueryById`,
> an `arxiv` search, a `curl` to a Celo RPC node — each is a priceable fetch. An
> `Edit`, a `Read` of a local file, a `pytest` run, a `TaskUpdate` — none of these
> is a data query; they would never appear on an x402 invoice.
>
> **Relevance to E10 v0.6:** Q is the *only* simulated quantity (§5.2, §6.2); its
> calibration centre is set by this trace. An over-broad mapping (counting `Read`
> or `Edit`) would inflate Q with non-priceable events and bias the FX-variance
> share downward (larger spurious `Var(Δlog Q)` in the §4.2 denominator). An
> over-narrow mapping (e.g. WebFetch only) would understate burstiness. The
> boundary is chosen on the single criterion "would this event incur an x402
> charge?" — which is exactly the spec's cost model.
>
> **Connection to the chosen path:** the per-call metadata extracted under this
> mapping feeds (a) the §4.3 anchored Q-volume *centre*, (b) the five §6.3 λ(t)
> modulation shapes, and (c) the task-2.3a overdispersion-mechanism evidence.

### 2.2 INCLUDE set (counts as a data query)

| Tool / pattern | Rationale |
|---|---|
| `WebFetch` | Fetches and reads a remote URL — a priceable external data pull. |
| `WebSearch` | Issues a query to an external search backend — priceable. |
| `mcp__dune__*` *(read ops)* | `executeQueryById`, `getExecutionResults`, `searchTables*`, `getDuneQuery`, etc. — on-chain analytics data fetches; the literal Dune-vs-x402 substrate of E10's cost model. |
| `mcp__github__*` *(read ops)* | `search_repositories`, `get_file_contents`, `search_code`, `get_pull_request*`, `list_*` — external repo/data reads. |
| `mcp__arxiv__*` | Paper search / abstract / download — external academic-data fetches. |
| `mcp__somnia-mcp__*`, `mcp__bigquery__*` | Chain-data and warehouse queries — priceable fetches. |
| `Bash` that is a `curl` / `wget` / `httpie` / `cast {call,rpc,block,tx,logs,...}` | HTTP/RPC data fetches issued from the shell — central-bank JSON pulls, RPC node calls. Detected by regex on the command string (host extracted as coarse target only). |

### 2.3 EXCLUDE set (does NOT count)

| Tool / pattern | Rationale |
|---|---|
| `Edit`, `Write`, `MultiEdit` | Author local artifacts — no external fetch. |
| `Read` | Reads a *local* file — no network, no x402 charge. |
| `Bash` that is not a fetch | `pytest`, `git`, `ls`, `python3 script.py`, `make` — local computation/IO. |
| `Task`, `Agent`, `TaskCreate`, `TaskUpdate`, `TaskStop` | Orchestration/dispatch — not data fetches. (In the largest centre file alone, TaskUpdate=341 + TaskCreate=197 + Agent=198 — correctly excluded; counting them would have inflated Q ~12×.) |
| `mcp__github__*` / `mcp__dune__*` *write ops* | `create_issue`, `create_pull_request`, `push_files`, `createDuneQuery`, `updateDashboard`, etc. — mutations, not priceable reads. Explicitly filtered out (`GH_WRITE`, `DUNE_WRITE` sets in the extractor). |
| `Skill`, `ToolSearch`, `AskUserQuestion`, `NotebookEdit` | Harness/meta operations — no external data fetch. |

**Boundary justification.** The single discriminating question is *"does this
event hit a network-external data endpoint such that an x402-style substrate
would meter it?"* WebFetch/WebSearch/data-MCP-reads/curl-RPC all do; everything
else does not. The github/dune read-vs-write split matters because a `createIssue`
is a side-effecting mutation a data-services invoice would not bill as a query.
This mapping was sanity-checked against raw counts: 63 of ~1314 tool calls in the
largest centre transcript are data queries (~5%), the remainder dominated by
TaskUpdate, non-fetch Bash, Agent, Edit, Read — all correctly excluded.

**Metadata-only guarantee.** The extractor stores, per call, ONLY: (a) ISO
timestamp, (b) tool name, (c) a coarse target (URL host / `mcp__server__op` /
`curl:<host>`). It never stores `input` payloads, request bodies, response
bodies, query arguments, or file contents. Any API key or credential the user
pasted in chat is structurally unreachable by this pipeline — payload fields are
never read into the output. No secret appears in any emitted artifact.

---

## 3. Volume — Q magnitude

### 3.1 Centre (abrigo-analytics) — the calibration CENTRE

| Aggregation | Value |
|---|---|
| Total data queries | **63** |
| Span | 11.3 days (2026-05-08 → 2026-05-19) |
| Query-bearing sessions | 4 |
| Active days | 4 (of 12 calendar days in span) |
| Per active-day counts | 27, 27, 8, 1 |
| Per-session counts | 27, 16, 12, 8 (mean 15.8) |
| Per-week counts | W19: 27, W20: 1, W21: 35 |
| Daily mean over the 12-day span (zero-filled) | 5.25 queries/day |
| Daily variance | 108.4 |

**Monthly-aggregate Q.** The centre trace lives entirely inside 2026-05. The
abrigo-analytics project, as an analytics/spec repo, does data-pull work in
*concentrated sprints* rather than continuously: 2 of the 4 active days carry 27
queries each (research sprints), the other 2 carry 8 and 1. Extrapolated to a
monthly aggregate at the observed active-day intensity, the centre implies a
representative-analyst Q on the order of **~60–130 priceable queries/month** in
sprint-driven months — small in absolute terms, but this is the *project's own*
trace and is the §6.2 centre by construction.

### 3.2 Bracket (other projects) — the calibration RANGE

| Aggregation | Value |
|---|---|
| Total data queries | **151** |
| Span | 26.8 days (2026-04-16 → 2026-05-13) |
| Query-bearing sessions | 7 |
| Active days | 12 |
| Per active-day counts | 42, 26, 24, 20, 13, 6, 5, 4, 4, 3, 2, 2 |
| Per-session counts | 40, 28, 28, 21, 16, 10, 8 (mean 21.6) |
| Daily mean over the 28-day span (zero-filled) | 5.39 queries/day |

The bracket's heavier-tooled projects (Solidity contract dev, frontend) push the
per-session and per-day maxima above the centre — bracket session max 40 vs centre
27; bracket day max 42 vs centre 27. The bracket therefore *brackets the centre
from above* on volume, as intended: it supplies the upper edge of the calibration
range without redefining the centre.

**Q-volume calibration range (for §4.3 / §6.2):** centre ≈ 16 queries/session
(mean), sprint days ≈ 27/day; bracket extends the session/day envelope to ≈ 22/
session and ≈ 42/day. Both are far below the spec's modeling boundary
`Q_high = 39,900/month` — consistent with the representative analyst sitting in
the *middle band* (§2.2), and confirming the trace does not approach the
flat-subscription crossover.

---

## 4. Source mix

### 4.1 Centre tool mix

| Tool class | Count | Share |
|---|---|---|
| `WebSearch` | 33 | 52% |
| `WebFetch` | 19 | 30% |
| `Bash` curl/RPC | 7 | 11% |
| `mcp__arxiv__*` | 4 | 6% |

Coarse target highlights (centre): `WebSearch` (33), `arxiv:search_papers` (4),
`curl:microdatos.dane.gov.co` (3 — DANE microdata pulls, the repo's Tier-2 data
source), plus assorted `WebFetch` hosts (encodeclub, dorahacks, ethglobal,
wiiw.ac.at, semanticscholar). The mix is **search-dominated** — characteristic of
research/spec work: literature and source discovery rather than repeated
programmatic data pulls.

### 4.2 Bracket tool mix

| Tool class | Count | Share |
|---|---|---|
| `Bash` curl/RPC | 56 | 37% |
| `mcp__github__*` | 30 | 20% |
| `WebSearch` | 26 | 17% |
| `mcp__dune__*` | 23 | 15% |
| `WebFetch` | 16 | 11% |

The bracket's mix is **fetch/MCP-dominated** — `curl` to RPC endpoints
(`forno.celo.org`, `localhost:8888`), Dune analytics calls
(`executeQueryById`, `getExecutionResults`, `searchTablesByContractAddress`), and
GitHub reads. This is the genuine programmatic-data-pull pattern of contract and
frontend work, and it is exactly the workload profile E10's representative
*Web3 data analyst* is meant to model. The bracket mix is the more
analyst-representative of the two; the centre mix is more research-skewed.

**Calibration implication for the source-mix component of λ(t):** the simulator's
Q need not distinguish source types (Q is a scalar count), but the mix confirms
the *arrival-generating activities* are heterogeneous — search bursts, RPC-poll
loops, Dune query batches — which is the micro-foundation of the burstiness in §5.

---

## 5. Cadence — mapping onto the five §6.3 λ(t) modulations

The spec §6.3 pre-commits the NHPP intensity λ(t) to carry five modulations. Each
is directly evidenced in the trace:

### 5.1 Modulation 1 — diurnal + weekday/weekend cycle

**Weekday/weekend — STRONG.** Centre: 62 of 63 queries fall on weekdays, only 1 on
a weekend (98.4% weekday). Bracket: 142 of 151 on weekdays (94%). Combined ≈ 95%
weekday concentration.

**Diurnal — PRESENT, bimodal.** Centre query hours (UTC) cluster at 11–12h (33
calls) and 21–22h (23 calls) — two working blocks (a UTC-morning and a UTC-evening
session), consistent with a Colombia-based analyst (UTC−5: ~06–07h and ~16–17h
local). Bracket shows the same bimodal shape (peaks at 11–12h and 23h, plus a 03h
block). λ(t) should carry a working-hours envelope with a two-peak daily shape,
not a single Gaussian bump.

### 5.2 Modulation 2 — burstiness / overdispersion

**STRONG — this is the dominant feature.** Binned into 5-minute windows:
- Centre 5-min window sizes: `[1,1,1,3,3,4,5,7,8,14,16]` — a max of 16 queries in
  a single 5-minute window; 8 of 11 active windows carry >1 query.
- Bracket 5-min window sizes run up to **24** in one window; 28 of 38 windows
  carry >1 query.
- Within-session inter-arrival median is **1.9 s (centre)** / 11.7 s (bracket) —
  arrivals are tightly clustered, far below any pure-Poisson spacing implied by
  the daily mean. Many gaps are near-zero because Claude issues parallel
  tool-call batches.

This is **research-sprint / batch-refresh clustering** — exactly the §6.3-item-2
mechanism. See §6 for the formal overdispersion verdict.

### 5.3 Modulation 3 — event-driven spikes

**PRESENT.** The per-day distribution is spike-dominated, not smooth: centre has
two 27-query spike days (2026-05-08, 2026-05-18) against background days of 8 and
1. Bracket has discrete spike days of 42 (2026-05-11) and 26 (2026-05-13) against
background days of 2–6. These spikes coincide with discrete research/build pushes
(the centre's 05-08 and 05-18 spikes align with E10-revision and prior-iteration
spec sprints). λ(t) needs a multiplicative event-spike term that fires on
discrete days, not a continuous modulation.

### 5.4 Modulation 4 — month-end reporting seasonality

**WEAK / INCONCLUSIVE at this trace length.** The centre trace spans only ~11 days
within a single month (2026-05), so a month-end pattern cannot be resolved from
the centre alone. The bracket spans a month boundary (2026-04 → 2026-05): activity
is present near the 2026-04 month-end (04-26/04-27: 24 queries) and is heavy in
early-to-mid May — but the sample is too short to isolate a *reporting-cadence*
month-end bump from ordinary sprint clustering. **Recommendation:** keep
modulation 4 in λ(t) as pre-committed (it is a documented analyst behavior), but
flag in the E10.1 calibration note that its *magnitude* is **not** anchored by
this trace and must be set from bracketing proxy research (The Graph
query-volume statistics / analyst-tooling telemetry) per §6.2. This is a calibration
gap, not a HALT condition — modulation 4 is the one of the five the own-trace
cannot pin.

### 5.5 Modulation 5 — slow secular workload drift

**PRESENT (bracket), visible.** Bracket per-week counts rise monotonically:
W16: 2 → W17: 6 → W18: 25 → W19: 44 → W20: 74 — a clear upward secular drift in
data-query workload over the 5-week bracket window. The centre's 3-week window
(W19: 27, W20: 1, W21: 35) is too short and too sprint-dominated to read a trend.
λ(t)'s drift term should be calibrated off the bracket's monotone weekly rise; the
centre confirms the workload is non-stationary but does not itself pin the slope.

### 5.6 Modulation summary

| § 6.3 modulation | Evidence | Anchored by |
|---|---|---|
| 1. Diurnal + weekday/weekend | ~95% weekday; bimodal UTC 11-12h / 21-23h | centre + bracket (strong) |
| 2. Burstiness / overdispersion | VMR ≈ 20; 5-min windows up to 24 calls | centre + bracket (strong) |
| 3. Event-driven spikes | discrete 27/42-query spike days vs 1-6 background | centre + bracket (strong) |
| 4. Month-end seasonality | not resolvable at this trace length | **proxy bracket only** — flag for E10.1 |
| 5. Secular drift | monotone weekly rise 2→74 over 5 weeks | bracket (clear) |

Four of the five modulations are anchored by the own-trace; modulation 4 must be
set from proxy research — recorded here as the one explicit calibration gap.

---

## 6. Overdispersion evidence — settles plan task 2.3a

Variance-to-mean ratio (VMR; equidispersed Poisson ⇒ VMR = 1):

| Aggregation level | Centre VMR | Bracket VMR |
|---|---|---|
| Per calendar day (zero-filled over span) | **20.6** | **19.8** |
| Per ISO week | 15.0 | 29.1 |
| Per session | 4.2 | 6.0 |
| Per 5-minute window | 4.6 | 5.3 |

**Verdict: Q is decisively OVERDISPERSED at every aggregation level.** The
daily-count VMR of ~20 (both centre and bracket, independently) is ~20× the
Poisson-equidispersed value. Even at the session level — where the analyst is
"active" — VMR is 4–6×. The trace is nowhere near Poisson.

**Implication for plan task 2.3a (overdispersion mechanism).** A homogeneous or
even a smoothly-modulated NHPP with a Poisson count law will NOT reproduce this
trace — the monthly-aggregate Q must be generated with an explicit
overdispersion mechanism. The two standard, defensible choices:

- **Negative-binomial count law** (Gamma-mixed Poisson) — a single dispersion
  parameter; the cleanest fit, and the natural choice given a ~20× VMR.
- **Cox process / doubly-stochastic NHPP** — a stochastic λ(t) (e.g. λ itself
  driven by a Gamma or log-normal sprint-intensity process), which *also*
  endogenously produces the §6.3-item-2 burstiness and the §6.3-item-3 event
  spikes from the same mechanism.

The trace argues for the **Cox / doubly-stochastic route**: the overdispersion is
not a featureless inflation of the variance — it is *structured* (5-min windows of
16-24 calls, discrete spike days). A Gamma-mixed λ(t) reproduces both the ~20×
VMR and the burst structure with one mechanism. A bare negative-binomial count law
would match the VMR but not the within-day clustering. Final functional-form
choice is locked in the E10.1 calibration note per §6.3; this trace's evidence
recommends the doubly-stochastic mechanism.

---

## 7. Centre vs bracket — calibration roles

| Dimension | CENTRE (abrigo-analytics) | BRACKET (other projects) |
|---|---|---|
| Role | calibration *centre* of the Q-volume range (§6.2) | bracketing *range* — upper envelope |
| Volume | 63 queries; 16/session mean; 27/day sprint max | 151 queries; 22/session mean; 42/day max |
| Source mix | search-dominated (WebSearch 52%) | fetch/MCP-dominated (curl 37%, Dune 15%) |
| Daily VMR | 20.6 | 19.8 |
| Most analyst-representative | research/spec work | yes — RPC + Dune programmatic pulls |

The centre sets the Q-process *centre* per the §6.2 NON-FANTASY clause. The
bracket widens the defended range on both volume (upper edge) and source mix
(confirms the programmatic-pull workload the representative *Web3 data analyst*
embodies). Both independently confirm ~20× daily overdispersion — the
overdispersion finding is robust to the centre/bracket split.

---

## 8. Anchor-adequacy verdict (spec §7 field 7a / RC OBS-1)

Spec §7 field-7(a) HALTs E10 at E10.1 if the simulator "cannot be anchored to the
§6.2 NON-FANTASY profile (thin/non-representative observed trace)".

**The trace is adequate. NO HALT on anchor grounds.**

- It is **genuine** — 214 real, timestamped tool calls (63 centre + 151 bracket),
  extracted from the literal Claude Code session record, no synthesis.
- It is **non-trivial** — it is not a flat or single-burst trace: it carries
  multi-session, multi-day, multi-week structure and exhibits 4 of the 5 §6.3
  modulations directly, with the 5th (month-end) deferred to proxy bracketing per
  the spec's own §6.2 design.
- It is **representative enough** — the bracket's RPC/Dune-heavy mix matches the
  declared Web3-data-analyst profile; the centre supplies the project's own
  workflow as the §6.2 centre.

**Two items for the E10.1 calibration note (not HALT conditions):**
1. **Modulation 4 (month-end seasonality)** magnitude is NOT anchored by the
   own-trace (trace too short to span enough month boundaries). It must be pinned
   from the §6.2 proxy bracket (The Graph query-volume statistics / analyst
   telemetry). Record this explicitly as a proxy-anchored, not own-anchored,
   modulation.
2. **`Q_low` pinning (§2.4).** This trace gives the volume *centre*; the §2.4
   `Q_low` qualitative-limit threshold still requires the corroborating proxy
   research the spec specifies. The trace alone does not pin `Q_low`.

Both are calibration tasks the spec already routes to proxy research — neither
weakens the own-trace centre.

---

## 9. Emitted artifacts

All under `scratch/2026-05-20-e10-revision/` — metadata only, no payloads, no secrets:

| File | Contents |
|---|---|
| `e10_q_anchor_extraction.md` | this analysis |
| `e10_q_anchor_calls.csv` | per-call metadata: `scope, timestamp_utc, tool, coarse_target, session` (214 rows) |
| `e10_q_anchor_daily.csv` | per-day query counts, zero-filled across span: `scope, date, query_count` |
| `e10_q_anchor_buckets.json` | per-week / per-month / diurnal-UTC / weekday / per-session / tool-mix / target-mix / VMR, for centre and bracket |

The CSV/JSON datasets are the structured calibration inputs for plan task 2.2
(Q-process calibration) and task 2.3a (overdispersion mechanism). They contain no
request/response payloads, no query arguments beyond a coarse host/op identifier,
and no credentials.
