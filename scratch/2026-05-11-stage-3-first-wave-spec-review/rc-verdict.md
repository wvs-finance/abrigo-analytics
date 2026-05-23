# RC verdict — Stage-3 first-wave master design spec v0.1

**Reviewer:** Reality Checker (RC)
**Spec under review:** `docs/specs/2026-05-11-stage-3-first-wave-design.md`
**Review wave:** Wave-1 plan-time (per spec §6.1)
**Date:** 2026-05-11
**Verdict:** ACCEPT_WITH_FLAGS

## Executive summary

Every load-bearing factual claim in the spec is traceable to a real
artifact at a verified line/byte location: audit-block prefixes for
both `IronCondor_strip.json` and `Z_cap_pinned.json` resolve verbatim,
the `REPLICATION_REL_TOL = 0.35` constant exists where claimed,
anti-fishing constants match `CLAUDE.md`, and all cited sections of
`PRIMITIVES.md`, `STAGE_2_RESULTS.md`, and `SaaS_Builders_AI_NativeBuilders.md`
contain what the spec says they contain. Anti-fishing posture is
intact — exit criteria are deliverable-existence + review-PASS with no
smuggled outcome-direction pins. Four non-blocking FLAGs (citation-path
hygiene, one orphan reference, one pin-table coverage gap, one internal
cross-reference consistency check) and three NITs. No BLOCKs.

## Findings (severity-graded)

### BLOCK

(none)

### FLAG (material, non-blocking)

- **RC-FLAG-1: Feedback-file citations omit `memory/` path prefix.** Citation: spec
  lines 10, 87, 118, 335, 479–484. The spec cites
  `feedback_pathological_halt_anti_fishing_checkpoint`,
  `feedback_notebook_citation_block.md`, and
  `feedback_post_hoc_fit_anti_fishing_pattern.md` as bare filenames. All
  three actually live under `memory/` (verified: `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`
  etc. exist; bare-name lookups fail). A downstream reviewer or sub-agent
  doing a literal `ls feedback_*.md` finds nothing.
  **Fix:** prefix `memory/` in §0 frontmatter, §1.1 line 87, §1.4 line 118,
  §6.1 line 335, and §10 lines 479–484.

- **RC-FLAG-2: B2 (Streamia premium plumbing) is listed as a deferred
  Stage-3 second-wave item in §0 (line 60) but has no parent reference
  in Stage-2 verdict memo §9 readiness checklist.** Citation:
  `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md:343–356`.
  Stage-2 §9 enumerates: (i) real-data conditioning of C1 [= A2], (ii) per-tier
  θ_k [= A3], (iii) hierarchical pooling for C3 [= C2], (iv) Weibull k≠1
  falsification (NOT in spec's deferred set), (v) on-chain 12-leg
  IronCondor [= B1], (vi) LP capital provisioning. "Streamia premium
  plumbing" appears in neither the verdict memo nor any other §10
  reference. The Weibull k≠1 falsification IS in Stage-2 §9 but is NOT
  captured anywhere in this spec's in/out scope partition.
  **Fix:** either add a citation for where B2 was introduced (probably
  `notes/SaaS_Builders_AI_NativeBuilders.md` discussion of premium form),
  or relabel as "B2 — TBD (not in Stage-2 §9; deferred to second-wave
  scoping)". Separately, add Weibull k≠1 falsification to the §0
  out-of-scope list with a Stage-2-spec-v1.2.1 §6.1 citation so the
  second-wave plan author has a complete carry-forward set.

- **RC-FLAG-3: Pin-table P-A1.x coverage drops the §2.1 HALT pre-pin
  on 5-percentage-point envelope threshold.** Citation: spec §2.1 line
  158–162 ("Pre-pinned envelope-comparison threshold for REPLACE:
  candidate X must beat the existing IronCondor by ≥ 5 percentage
  points") vs §5 pin table lines 307–311 (P-A1.1, P-A1.2, P-A1.3 cover
  comparison-table coverage, envelope reproducibility, verdict
  citation — but NO pin guards the 5pp threshold pre-pinning). This
  threshold is a substantive anti-fishing pre-commitment and per §1.1
  carry-forward MUST be locked before data is touched. Without a pin,
  there is no gate for RC/MQ Wave-1 review on the A1 plan to verify
  the threshold was committed before the comparison table was built.
  **Fix:** add **P-A1.4** to §5: "5-percentage-point REPLACE threshold
  pinned in the A1 plan BEFORE comparison-table emit (anti-fishing per
  spec §1.1)."

- **RC-FLAG-4: Pin S6 (cohort_5_strip strategy framing) cites a ≤ 5%
  envelope tolerance while `types.py::REPLICATION_REL_TOL = 0.35` (35%)
  is what the B1 forge assertion will read.** Citation:
  `simulations/saas_builder/cohort_5_strip/__init__.py:34–35` ("max
  relative error vs log-contract proxy ≤ 5% over a 17-point grid") vs
  `simulations/saas_builder/cohort_5_strip/types.py:65–74` (35% with
  explicit comment that the theoretical floor is ~33% and 35% gives a
  small margin). This is NOT a defect in the spec under review (the
  spec correctly cites 35% in §2.3 line 225–227 and P-B1.2 line 317),
  but the spec is silent on the cohort_5_strip-internal Pin-S6-vs-tolerance
  inconsistency. A B1 plan author who reads the strategy framing first
  may pre-commit to the wrong tolerance.
  **Fix:** add a sentence to §2.3 phase 4 noting "the ≤ 5% target in
  cohort_5_strip Pin S6 is the *aspirational* envelope at higher leg
  counts (N=5/7/12 strip refinements per types.py line 71–73); the
  CURRENT N=3 12-leg strip uses the 35% tolerance which is the floor
  B1 binds to." This pre-empts a foreseeable B1-plan-author confusion.

### NIT (cosmetic)

- **RC-NIT-1: §9 CORRECTIONS-α block is correctly empty and reserved
  per spec §0/§6.4.** Citation: spec lines 446–450. Confirmed as
  claimed; no action required. Recording only because the dispatch
  brief asked me to verify it explicitly.

- **RC-NIT-2: Audit-block prefixes in §1.3 and §10 use trailing
  ellipsis (`94150326…`, `1fb1f7a4…5d31`).** Verified against the live
  JSONs: full `audit_block` for `IronCondor_strip.json:2` is
  `94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329`;
  for `Z_cap_pinned.json:3` is
  `1fb1f7a42131268f3448da8d61b685ce27fe1facf356122e557ac10d329b5d31`.
  Both prefixes match. Truncation is fine but consider adopting a
  consistent style (first 8 chars … last 4 chars vs first 8 only).

- **RC-NIT-3: §10 References cites "PRIMITIVES.md §10 Carr-Madan, §11
  discrete strip, §12 tolerance ledger" — all verified.** PRIMITIVES.md
  headers at lines 16 (§1), 280 (§9), 295 (§10 Carr-Madan), 343 (§11
  discrete strip), 363 (§12 tolerances) match the spec's section labels
  exactly. No action.

## Citation trace audit

| Spec claim | Verified location | Pass/Fail |
|------------|-------------------|-----------|
| `IronCondor_strip.audit_block` = `94150326…` (§1.3, §4) | `simulations/saas_builder/data/IronCondor_strip.json:2` — `94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329` | PASS |
| Stage-2 v1.1 Z_cap audit `1fb1f7a4…5d31` (§1.3) | `simulations/saas_builder/data/Z_cap_pinned.json:3` — `1fb1f7a42131268f3448da8d61b685ce27fe1facf356122e557ac10d329b5d31` | PASS |
| `REPLICATION_REL_TOL = 0.35` (§2.3, §10) | `simulations/saas_builder/cohort_5_strip/types.py:74` — `REPLICATION_REL_TOL: Final[float] = 0.35` | PASS |
| `N_MIN = 75` (§1.1) | `CLAUDE.md:173` — `N_MIN = 75, POWER_MIN = 0.80, MDES_SD = 0.40` | PASS |
| Commit `3442852` cohort_5_strip emit (§0) | `git log --oneline` — `3442852 feat(saas-cohort-5-strip): Carr-Madan 3-condor (12-leg) IronCondor strip emit` | PASS |
| Commit `abd0a94` this spec (§ frontmatter implicit) | `git log` — `abd0a94 spec(stage-3-first-wave): master design — A1 / A2 / B1 with RC+MQ 2-way review` | PASS |
| B1 lives in `thetaSwap-core-dev` (§2.3, §8.1) | No `thetaSwap-core-dev` path inside this repo; spec correctly scopes B1 as JSON-artifact handoff contract only (lines 205–211, 420–423) — no implementation claim | PASS |
| Stage-2 §15.4 rank-flip safeguard (§2.2 P-A2.4) | `docs/specs/2026-05-07-saas-builder-stage-2-prereg-lock.md:881, 914` — §15.4 exists; HALT-on-ELPD-rank-flip explicitly armed | PASS |
| PRIMITIVES.md §10 / §11 / §12 (§10 References) | `notes/PRIMITIVES.md:295, 343, 363` | PASS |
| STAGE_2_RESULTS.md R1–R8 + §5 Stage-3 open items (§10) | `notes/STAGE_2_RESULTS.md` headers at lines 44–212 cover R1–R8; §5 at line 212 | PASS |
| `SaaS_Builders_AI_NativeBuilders.md` §"Identification strategy" (A2) | `notes/SaaS_Builders_AI_NativeBuilders.md:116` — header exists, lists Twitter/X, Discord, Platzi, GitHub Octoverse LATAM | PASS |
| Stage-2 verdict memo §9 readiness checklist (§10) | `docs/specs/2026-05-09-saas-builder-stage-2-verdict-memo.md:343` — section exists; A1 (Panoptic re-survey) NOT a literal bullet but emerges from §9 line 351 IronCondor strip + this spec's framing as a precondition | PARTIAL (see RC-FLAG-2) |
| §9 CORRECTIONS-α empty/reserved (§6.4 → §9) | spec lines 446–450 — confirmed reserved | PASS |
| Pin table covers §2 deliverables | spec §5 lines 307–319 — P-A1.1/2/3, P-A2.1/2/3/4, P-B1.1/2, P-X.1/2 — but 5pp threshold pre-pin not gated (see RC-FLAG-3) | PARTIAL |
| Feedback citations resolve | `feedback_pathological_halt_anti_fishing_checkpoint.md` etc. only exist under `memory/`; spec cites bare names (see RC-FLAG-1) | FAIL (cosmetic) |

## Anti-fishing posture audit

CONFIRMED CLEAN. Each track's exit criteria are deliverable-existence
+ review-PASS:

- **A1 (§2.1):** exit deliverables are `STRATEGY_COMPARISON.md`,
  `strategy_verdict.json`, and (conditionally) a delta-spec. The
  verdict alphabet is `KEEP | REPLACE`; the 5pp REPLACE threshold IS
  pre-pinned before the comparison table is built (line 159–162) —
  this is exactly the anti-fishing-correct posture. No "A1 will keep
  IronCondor" or "A1 will replace with butterfly" pre-pinning anywhere.
- **A2 (§2.2):** exit deliverables are the SOURCING_PROTOCOL,
  empirical parquet, Z_cap v1.2 re-pin, strip re-emit. P-A2.1 forces
  pre-pinning of sourcing protocol BEFORE data; P-A2.2 forces $N \ge 75$
  AT EXIT (with explicit guard against pre-registration smuggling at
  line 313). No outcome-magnitude pre-pinning on $\bar C$ percentiles.
  Rank-flip HALT armed per Stage-2 §15.4.
- **B1 (§2.3):** envelope tolerance bound (35%) is the floor inherited
  from `types.py::REPLICATION_REL_TOL`, not a re-derived value —
  P-B1.2 explicitly forbids re-derivation. HALT triggers route to the
  strategy layer (A1) rather than tolerance-relaxation, which is the
  anti-fishing-correct routing.
- **§0 scope guard (line 64–71):** explicit textual commitment that
  the spec is SCOPE-AND-GATE only and does NOT pre-pin outcomes, with
  a citation to the pathological-HALT feedback rule. §8.4 (line 439–444)
  repeats this commitment.

No smuggled outcome-direction claims. The spec's §0 anti-fishing scope
guard is a model implementation of the feedback rule.

---

*End of RC verdict. Word count ≈ 1480.*
