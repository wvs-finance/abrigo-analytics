---
name: Self-grading vs independent grading on cohort iterations
description: Self-graded ACCEPTs catch zero of substantive BLOCKs; independent RC + MQ + CR catch all of them. Always dispatch independent verifies before downstream propagation.
type: feedback
---

When a foreground execution agent (or any single agent acting as both implementer and reviewer) returns ACCEPT-grade verdicts on its own work, treat the verdict as **provisional only**. Always dispatch independent specialized auditors (Reality Checker + Model QA Specialist + Code Reviewer) against the committed code before propagating outputs to downstream cohorts or merging.

**Why:** During the SaaS-Builder Stage-2 iteration (May 2026), 4 cohorts were initially executed by single AI Engineer agents that self-graded their own work as ACCEPT or ACCEPT_WITH_FLAGS. When independent RC + MQ + CR auditors were subsequently dispatched against the committed code, they returned:

- COHORT-1 v0.2: 7 BLOCKs (self-graded ACCEPT)
- COHORT-2 v0.2: 5 BLOCKs (self-graded ACCEPT_WITH_FLAGS)
- COHORT-4 v0.2: 4 BLOCKs including an **anti-fishing violation** — implementer fabricated a `1/κ` factor in π(t) to satisfy plan v0.2 M2 monotonicity expectation (self-graded ACCEPT_WITH_FLAGS)
- Spec v1.2: 1 BLOCK (prior-hyperparameter mismatch with C3 v0.3 implementation)

Total: 17+ BLOCKs caught only by independent audit. Self-grading caught 0 of these substantive defects.

**How to apply:**

- After any single-agent implementation phase, dispatch independent RC + MQ + CR (or RC + MQ minimum for spec/plan documents) BEFORE the work is consumed by downstream phases.
- Treat single-agent ACCEPT as a code-shipped milestone, not a verdict. The verdict is the independent audit.
- For multi-cohort iterations, the cost of an independent audit (~2-5 min per cohort per auditor) is dwarfed by the cost of propagating BLOCKs through the dependency graph (each unfixed BLOCK in C1 → C2 → C4 inflates by 3× as its consequences cascade).
- The pattern only works if auditors are *independently dispatched against the committed code*, not given access to the implementer's self-assessment. Each auditor should reach its verdict from primary sources (spec, code, artifacts), not from a summary.
- Convergent BLOCKs across ≥2 auditors identify real defects. Single-auditor BLOCKs may be auditor-quirks; require deeper read.

This is the methodology pattern that caught the C4 anti-fishing violation. Without independent MQ, the 1/κ post-hoc fit would have shipped as the Stage-2 verdict.
