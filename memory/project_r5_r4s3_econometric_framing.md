---
name: project-r5-r4s3-econometric-framing
description: AI-cost-factor-model R5 + R4-S3 estimands — descriptive variance decomposition (primary) + behavioral subscription-inelasticity test (USD); N=38 pilot floor, HAC L=floor(T^(1/3)), stationary bootstrap B=10000
metadata:
  type: project
---

**R5 (primary estimand)** = descriptive variance decomposition of per-message AI cost into model-mix / cache-hit / message-length / prompt-style components. Inference via **stationary bootstrap (Politis-Romano)** with `B = 10,000`, block length `ceil(T^(1/3))`.

**R4-S3 split** (critical, easy to confuse):
- **R4-S3-COP** = consistency check on COP-denominated cost. NOT novel; serves only as cross-check.
- **R4-S3-USD** = behavioral test of **subscription inelasticity** on USD cost. Two-sided null `α_1^USD = 0`. **Inverted-test interpretation**: failing to reject = inelasticity is consistent with data; rejecting = elasticity present.

**Sample-floor relaxation** per CORRECTIONS-G: `N = max(weekday days observed) ≈ 38`. This is **pilot demonstration-grade**, not the global `N_MIN = 75` from `CLAUDE.md` anti-fishing. Justified by single-operator (Juan) data scarcity.

**Inference machinery pins**:
- HAC bandwidth: `L = floor(T^(1/3))`
- Stationary-bootstrap block: `ceil(T^(1/3))`, `B = 10,000`
- CI threshold: ≤ 0.15 half-width per CORRECTIONS-T

**Power-HALT expected at T=38** per Model QA's independent calculation. Pre-disposition memo template lives at `notebooks/dev_ai_cost_v2/dispositions/power_halt_template.md`. The HALT is **planned**, not a surprise — fires the [[feedback-pathological-halt-anti-fishing-checkpoint]] protocol with `pilot-demonstration-grade` already declared.

**Why this note**: the COP/USD split has structurally different roles (consistency vs. behavioral) and the N=38 floor diverges from the project-global N_MIN. Both are easy to forget post-compaction and would produce wrong fishing flags if conflated.

**Links**: [[project-ai-cost-v0-2-3-state]] · [[feedback-pathological-halt-anti-fishing-checkpoint]] · [[project-mdes-formulation-pin]]
