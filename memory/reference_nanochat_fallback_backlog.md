---
name: reference-nanochat-fallback-backlog
description: nanochat (karpathy) tracked as TaskList #36 last-resort for R6 v2 — fine-tune minimal LLM on observed Claude Code interactions to simulate token-arrival × token-size × model-choice if NHPP + whole-message bootstrap proves insufficient
metadata:
  type: reference
---

**The fallback**: https://github.com/karpathy/nanochat — minimal LLM training stack.

**Use case if activated**: R6 (continuous-stream-simulation) v2 needs to generate synthetic Claude Code interaction streams for stress testing. The v0.1.3 R6 spec uses **NHPP (non-homogeneous Poisson process) for token-arrival timing × whole-message bootstrap for content shape**. If that joint distribution turns out to be too crude (e.g., the marginals are right but the (arrival, size, model-choice) dependence structure is mis-specified), the fallback is:

1. Fine-tune a small LLM (nanochat-scale) on the observed JSONL corpus of real Claude Code interactions
2. Sample from the fine-tuned model to generate (timing, content, model-choice) triples that preserve the empirical joint distribution
3. Use the samples as the R6 v2 stream generator in place of the NHPP × bootstrap composition

**Status: PARKED. TaskList #36. Not active.**

**Why parked**: NHPP × bootstrap is the simpler, defensible baseline. Activating nanochat introduces a training-loop dependency, GPU requirement, and an opaque generator that's hard to audit against the anti-fishing invariants. Only activate if the baseline demonstrably fails an integration test that the v2 stream must pass.

**Activation gate**: R6 v1 must FAIL a specific integration test (TBD when v1 lands) before the nanochat path is allowed to fire. No speculative pre-work.

**Why this note**: the user raised this in passing during v0.2.x cycle discussion. Without a memory entry it would resurface in future sessions as a novel idea, wasting cycles re-evaluating its appropriateness. The PARKED status + activation gate are the load-bearing facts.

**Links**: [[project-ai-cost-v0-2-3-state]]
