# Claude Code per-usage cost research — for CPO hedge pricing

Date: 2026-05-07
Frame: q_t = N_t(W) · τ̄(W) · p_t + infra_t(W) + subscription_residual_t
W = solo AI-native LATAM builder, multi-turn agentic IDE coding via Claude Code.

## 1. TL;DR

Yes, a workflow-derived per-usage cost model is defensible from public data. Anthropic publishes per-token prices [pricing] and *its own* per-developer empirical distribution: mean ≈ $13/active-day, p90 ≤ $30/active-day, $150–$250/dev/month at enterprise scale [costs-doc]. The Pro/Max subscription is a cap-truncated version of this same per-token reality: when active builders breach the (5-hour rolling × weekly) caps they are blocked or kicked to metered API overflow [help-models]. The "$500–$2,000/mo despite paying for Max" claim is **substantiated qualitatively but rarely with screenshots**: one well-documented case ($1,600/mo, Jenny Ouyang) [b2l-ouyang], one HN-cited heavy user at 150–200 M tokens/day implying $5k/mo retail-API equivalent [alderson], plus a Reddit pattern of Max-20x users hitting weekly caps in 1–2 days [gh-9424]. Plausible LATAM-builder $/mo range, full-time agentic Claude Code use, no subsidy: **$150–$400/mo modal, $500–$1,500/mo p90, >$2,000/mo p99**, with very high cross-day variance (single-task token cost spreads 30× run-to-run) [arxiv-2604.22750]. Distribution is heavy-tailed; this is exactly the shape a convex-payoff option prices.

## 2. Anthropic published structure

**Per-token rates (May 2026)** [pricing, finout-pricing]:
- Haiku 4.5: $1 / $5 per MTok (input/output)
- Sonnet 4.6: $3 / $15 per MTok (1M ctx at standard rate)
- Opus 4.6: $5 / $25 per MTok
- Opus 4.7 (released 2026-04-16): $5 / $25, but new tokenizer emits up to **+35% tokens** for the same text → effective rate ↑ ~35% [finout-opus47]
- Prompt caching: cached input −90%; batch: −50% all token classes [finout-pricing]

**Subscription tiers** [pricing, claude-pricing]:
- Pro $20/mo, Max 5x $100/mo, Max 20x $200/mo. All are caps-on-usage, not unlimited.
- Caps shared across Claude.ai chat + Claude Code in one bucket [allthings].

**Cap mechanics** [tokenmix, portkey, gh-9424]:
- 5-hour rolling session window + weekly cap (introduced 2025-08-28).
- Pro / Max 5x: blocked until window resets when capped; weekly cap is hard.
- Max 20x: opt-in metered API overflow at standard per-token rates (this is the exit door from "subscription mode" into the q_t = N·τ·p regime).
- 2026-05-06: Anthropic doubled 5-hour limits and removed peak-hour reductions [9to5google, anthropic-spacex]; baseline numbers not officially published.
- Anthropic's only published "messages" anchor: ~45 short messages per Pro 5-hour window [allthings]. Not load-bearing — heavily dependent on tool-use and context length.

**Tool-use overhead (key for τ̄)** [costs-doc, claudefa-context]:
- Context window 200K tokens (500K some Enterprise).
- Claude Code resends full message history + system prompt + tool schemas every turn; "the 40th message in a session pays for everything before it" [b2l-ouyang]. This makes τ̄ super-linear in turn-count within a session.
- MCP tool definitions deferred since recent updates (only names enter context until invoked) [costs-doc].
- Agent teams: ~7× tokens vs single-agent sessions [costs-doc].

## 3. Empirical N_t and τ̄ priors

Treating each turn (user message + tool round-trips + model reply) as one invocation.

**Anthropic's own published distribution** [costs-doc]:
- Mean spend ≈ $13/dev/active day; p90 ≤ $30/active-day; **$150–$250/dev/month** at enterprise scale.
- Anthropic's recommended team rate-limit table → per-user TPM 10k–300k depending on org size; for a 1–5-user team, 200–300k TPM and 5–7 RPM. At full-day saturation that ceiling implies > 100M tokens/day per user, but typical use is far below.

**Independent estimates** [verdent, tokenmix]:
- Pro window quota ≈ 44k tokens / 5h; Max 5x ≈ 88k; Max 20x ≈ 220k. Treat as approximate.
- Light user (1–2 sessions/day, focused tasks): $2–5/day API.
- Active user (3–5 hr/day, multi-file work): $6–12/day, ~$100–200/mo Sonnet 4.6.
- Heavy: $30–50/day on multi-agent or refactor days.

**Per-task / per-turn distribution** [arxiv-2604.22750, arxiv-2601.14470]:
- Same task across runs: **30× spread in total tokens** — token consumption is *inherently stochastic*, not a deterministic function of the prompt.
- Agentic tasks consume **~1000× more tokens than chat or code-completion** for ostensibly similar problems.
- Per-task input/output/reasoning split: 53.9% / 24.4% / 21.6% (input dominates).
- Code-review-style turns burn ≈ 59% of session tokens; coding ≈ 9%; design ≈ 2%.
- Models disagree: Claude Sonnet 4.5 and Kimi-K2 use **>1.5M more tokens than GPT-5** on identical tasks.
- Models predict their own consumption at correlation ≤ 0.39 and systematically underestimate.

**Recommended priors for a CPO model:**
- N_t (turns/active-day) ≈ LogNormal, median ~80, p90 ~250 (back-out from $13/$30 days at observed τ̄).
- τ̄ (tokens/turn, weighted i+o) ≈ Pareto-tailed, median 2–8k, p90 50–150k, p99 > 200k. Within-session compounding via context re-read makes τ̄ session-position-dependent.
- 95% prompt-cache hit assumed; effective input rate ≈ $0.30/MTok Sonnet [alderson].

## 4. Heavy-user regime — substantiated/refuted

**Substantiated qualitatively**, weakly substantiated quantitatively. Honest accounting:

| Source | Claim | Quality |
|---|---|---|
| Jenny Ouyang via build-to-launch [b2l-ouyang] | $1,600/mo personal Claude Code bill; attributed to file-content accumulation, full MCP JSON, context re-read | Single named anecdote, no screenshot in source |
| Alderson [alderson] citing HN | One user 150–200M tokens/day → $400–600/day retail = ~$5,000/mo; Anthropic's own avg = $6/day, p90 $12/day | Second-hand HN, but consistent with Anthropic's own /cost figures |
| GitHub issue #9424 [gh-9424] | Multiple Max 20x ($200/mo) users hit weekly cap in 1–2 days; reports of "5% used in ONE message" on Max 5x; cancellations | Crowd anecdote, not metered |
| Reddit / r/ClaudeCode synthesized [aitooldiscovery] | "$400+ invoice"; one user 10B tokens / 8 mo = $15k API equivalent paid as $800 Max sub | Anonymous; consistent with order-of-magnitude |

**Refuting context** — Anthropic's own median-spend table caps "active full-time" at p90 ≤ $30/active-day [costs-doc]. So ~22 active days × $30 ⇒ $660/mo p90 *measured at the API*. The $500–$2,000/mo regime is the **right tail of an empirically heavy-tailed distribution**, plausibly 5–15% of full-time agentic users. Levelsio / Marc Lou / Tony Dinh: no usable public Claude bill screenshots found in this search; do not cite.

**Bottom line for CPO pricing**: the $/mo random variable is *log-positive-skewed with a fat right tail* and a *cap-induced kink* at the Max 20x → metered-API boundary. This is exactly the regime where a long-gamma payoff has positive value.

## 5. Academic-model survey

The literature is thin but recently materialized:

- **arxiv 2604.22750** "How Do AI Agents Spend Your Money?" — first systematic study of token consumption in agentic coding. Documents 30× same-task variance, 1000× agentic-vs-chat ratio, weak self-prediction (ρ ≤ 0.39). **Direct prior for τ̄ distribution.**
- **arxiv 2601.14470** "Tokenomics: Quantifying Where Tokens Are Used in Agentic SE" — phase decomposition (review-heavy, coding-light); 53.9% input dominance.
- **arxiv 2603.24582** "The Stochastic Gap: A Markovian Framework for ... Agentic AI" — agent execution as a Markov chain over tool calls with policy-sampled next actions, transition kernel, path-dependent uncertainty. **Direct functional form for N_t modeling.**
- **arxiv 2601.20404** AGENTS.md impact on token consumption — shows configuration files measurably move per-PR token cost.
- **arxiv 2601.22037** Meta-tools / sequence fusion to compress agentic traces.
- **arxiv 2305.05176** FrugalGPT (Chen, Zaharia, Zou 2023) — LLM-cascade and prompt-adaptation cost-reduction; foundational but pre-agent.

**Honest gap**: no public paper jointly models (i) per-turn token cost, (ii) Markovian turn-transitions, and (iii) cap-truncated subscription billing as a single stochastic process suitable for option pricing on $/mo. This is open methodological territory and is *exactly* what the CPO M-design step would need to formalize.

## 6. Open data gaps

What public data already gives us:
- Per-token prices (firm).
- Anthropic's own per-developer mean and p90 spend at enterprise scale (firm).
- Order-of-magnitude τ̄ stochasticity (arxiv).
- Cap-mechanics structure (Anthropic docs + community).

What we'd need first-party for a LATAM solo-builder cohort (n=30–75 survey):
1. Self-reported active hours/day on Claude Code, by builder type.
2. Subscription tier history and *cap-hit count* per week (proxy for breach probability).
3. Monthly Anthropic invoice (USD) for the metered overflow + subscription.
4. COP wage / total revenue numerator to compute the bill-to-income ratio (the actual hedged variable).
5. Optional: `/usage` JSON dumps for τ̄ and N_t empirical CDFs.

This is small-N feasible and would close the only real gap: the **conditional distribution of monthly $ given "Colombian solo builder coding ≥30h/wk"**, which is the population-specific Y in the (Y, M, X) sense. Without it we are extrapolating from US enterprise averages and US-builder anecdotes; with it we can pin a 90% CI on the breach probability that the CPO actually sells.

---

## References

- [pricing] https://platform.claude.com/docs/en/about-claude/pricing
- [claude-pricing] https://claude.com/pricing
- [costs-doc] https://code.claude.com/docs/en/costs (Anthropic, "Manage costs effectively")
- [help-models] https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code
- [allthings] https://allthings.how/claude-code-usage-limits-explained-pro-max-and-weekly-caps/
- [tokenmix] https://tokenmix.ai/blog/complete-claude-limits-guide-2026-tokens-uploads-5-hour
- [portkey] https://portkey.ai/blog/claude-code-limits/
- [verdent] https://www.verdent.ai/guides/claude-code-pricing-2026
- [finout-pricing] https://www.finout.io/blog/anthropic-api-pricing
- [finout-opus47] https://www.finout.io/blog/claude-opus-4.7-pricing-the-real-cost-story-behind-the-unchanged-price-tag
- [9to5google] https://9to5google.com/2026/05/06/claude-code-is-getting-higher-usage-limits-doubled-for-most-users/
- [anthropic-spacex] https://www.anthropic.com/news/higher-limits-spacex
- [b2l-ouyang] https://buildtolaunch.substack.com/p/claude-code-token-optimization
- [alderson] https://martinalderson.com/posts/no-it-doesnt-cost-anthropic-5k-per-claude-code-user/
- [gh-9424] https://github.com/anthropics/claude-code/issues/9424 (Weekly Usage Limits Making Claude Subscriptions Unusable)
- [aitooldiscovery] https://www.aitooldiscovery.com/guides/claude-code-reddit
- [claudefa-context] https://claudefa.st/blog/guide/mechanics/context-management
- [arxiv-2604.22750] How Do AI Agents Spend Your Money? Analyzing and Predicting Token Consumption in Agentic Coding Tasks. https://arxiv.org/abs/2604.22750
- [arxiv-2601.14470] Tokenomics: Quantifying Where Tokens Are Used in Agentic Software Engineering. https://arxiv.org/abs/2601.14470
- [arxiv-2603.24582] The Stochastic Gap: A Markovian Framework for Pre-Deployment Reliability and Oversight-Cost Auditing in Agentic AI. https://arxiv.org/abs/2603.24582
- [arxiv-2601.20404] On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents. https://arxiv.org/abs/2601.20404
- [arxiv-2601.22037] Optimizing Agentic Workflows using Meta-tools. https://arxiv.org/abs/2601.22037
- [arxiv-2305.05176] Chen, Zaharia, Zou. FrugalGPT. https://arxiv.org/abs/2305.05176
