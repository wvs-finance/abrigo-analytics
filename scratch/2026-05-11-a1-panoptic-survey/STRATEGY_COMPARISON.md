# Panoptic Primitive Comparison Table — Stage-3 A1 Phase 1

**Author:** general-purpose implementer (Stage-3 A1 Task 1.1)
**Date:** 2026-05-11
**Plan anchor:** docs/plans/2026-05-11-stage-3-a1-panoptic-restrategy.md v0.2
**Consumed strip audit_block:** 94150326332b90e50cfe02b580e6d05280100b430de0089ea9197c8fa4aaf329
**Anti-fishing posture:** factual catalogue ONLY; no pre-ranking; no recommendation.

## §1 Methodology

Sources consulted on 2026-05-11 via WebFetch against the public `panoptic.xyz` documentation, research, and blog surfaces. Three pages drove the primitive enumeration: the research piece "18 Options Strategies Every Trader Should Know" (which enumerates the explicit named strategies the Panoptic product layer surfaces to traders), the `/docs/contracts/smart-contracts-overview` page (which constrains every Panoptic position to at most four legs via the Semi-Fungible Position Manager wrapping up to 4-legged Uniswap v3 positions), and the `/docs/product/streamia` and `/docs/product/timescales` pages (which establish that Streamia is a funding-rate mechanism applied universally to all positions and Timescales is a per-position width parameter — neither is a primitive in its own right). The liquidity-status column is anchored to the July-2025 corporate blog post "Panoptic: Your Next DeFi Alpha", which is the most recent reachable status statement; it confirms live deployments on Ethereum mainnet, Unichain, and Base, with cumulative trading volume above USD 25M since the December 2024 launch.

Scope limits I want to be explicit about. I did not access the Solidity source on GitHub, the V2-beta technical paper, or any Dune dashboard for per-primitive open-interest. The "on-chain liquidity status" column therefore reflects *protocol-level* liquidity reachability (live / limited / inactive at the venue), not per-primitive OI. Where the named strategy in the research article exceeds the contract-layer 4-leg ceiling (ZEEHBS has 6 legs), I mark the on-chain status as "constructible only as multi-position bundle" rather than as a single SFPM-wrapped position — this is a factual contract constraint, not an opinion on tradability. Streamia and Timescales are catalogued as non-primitives in §3 rather than as table rows.

## §2 Comparison table

| primitive_id | leg_count | payoff_shape | convexity_class | on-chain_liquidity | admits_strip_emit? | source_url | access_timestamp |
|---|---|---|---|---|---|---|---|
| long_call | 1 | piecewise-linear, convex above strike | long-vol (directional bullish) | live (Ethereum, Unichain, Base) | yes — single strike, single weight is a trivial ladder | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| long_put | 1 | piecewise-linear, convex below strike | long-vol (directional bearish) | live (Ethereum, Unichain, Base) | yes — single strike, single weight | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| short_call | 1 | piecewise-linear, concave above strike | short-vol (directional bearish) | live (Ethereum, Unichain, Base) | yes — single strike, single weight (negative) | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| short_put | 1 | piecewise-linear, concave below strike | short-vol (directional bullish) | live (Ethereum, Unichain, Base) | yes — single strike, single weight (negative) | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| long_straddle | 2 | piecewise-linear, convex (V-shape at strike) | long-vol | live (Ethereum, Unichain, Base) | yes — two coincident strikes, equal weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| long_strangle | 2 | piecewise-linear, convex (flat between strikes) | long-vol | live (Ethereum, Unichain, Base) | yes — two separated strikes, equal weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| call_spread | 2 | piecewise-linear, bounded | directional bullish (mixed-vol) | live (Ethereum, Unichain, Base) | yes — two strikes, one long one short | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| put_spread | 2 | piecewise-linear, bounded | directional bearish (mixed-vol) | live (Ethereum, Unichain, Base) | yes — two strikes, one long one short | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| call_calendar_spread | 2 | mixed (path-dependent on timescale) | short-vol | live (Ethereum, Unichain, Base) | no — payoff depends on timescale, not strikes alone; no deterministic strike-ladder | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| diagonal_spread | 2 | mixed (path-dependent on timescale + strike) | directional bullish (mixed) | live (Ethereum, Unichain, Base) | no — timescale is the second axis, not a strike | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| jade_lizard | 3 | piecewise-linear, asymmetric (capped upside, unlimited downside) | short-vol | live (Ethereum, Unichain, Base) | yes — three strikes (one short put, one short call, one long call), three weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| big_lizard | 3 | piecewise-linear, asymmetric | short-vol | live (Ethereum, Unichain, Base) | yes — three strikes, three weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| super_bull | 3 | piecewise-linear, asymmetric | directional bullish | live (Ethereum, Unichain, Base) | yes — three strikes, three weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| super_bear | 3 | piecewise-linear, asymmetric | directional bearish | live (Ethereum, Unichain, Base) | yes — three strikes, three weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| call_ratio_spread | 3 | piecewise-linear (ratio-asymmetric) | mixed | live (Ethereum, Unichain, Base) | yes — three strikes; weights are non-unit ratios | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| zebra | 3 | piecewise-linear, leveraged-replication | directional bullish (mixed-vol) | live (Ethereum, Unichain, Base) | yes — three strikes with documented 2:1 ratio weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| iron_condor | 4 | piecewise-linear, symmetric (flat middle, capped wings) | short-vol | live (Ethereum, Unichain, Base) | yes — four strikes, four weights (sign-alternating) | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| iron_butterfly | 4 | piecewise-linear, symmetric (peak at center) | short-vol | live (Ethereum, Unichain, Base) | yes — four strikes (two coincident at the body) | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| bats | 4 | piecewise-linear, asymmetric | short-vol | live (Ethereum, Unichain, Base) | yes — four strikes, four weights | https://panoptic.xyz/research/essential-options-strategies-to-know | 2026-05-11 |
| zeehbs | 6 | piecewise-linear, leveraged-strangle replica | long-vol | constructible only as multi-position bundle (exceeds 4-leg SFPM ceiling) | yes — six strikes, six weights, but emit must span ≥2 SFPM positions | https://panoptic.xyz/research/essential-options-strategies-to-know · https://panoptic.xyz/docs/contracts/smart-contracts-overview | 2026-05-11 |

## §3 Strip-emit-eligibility summary

Per master-spec §2.1 HALT-trigger #1, a primitive admits a strip-emit iff its payoff is fully specified by a finite, deterministic tuple of strikes and weights — i.e., the payoff at any underlying price is reconstructible from `{(K_i, w_i)}_{i=1..n}` without reference to time-of-entry or per-leg timescale parameters.

**Admit strip-emit (deterministic strike-ladder + weight vector exists):**
`long_call`, `long_put`, `short_call`, `short_put`, `long_straddle`, `long_strangle`, `call_spread`, `put_spread`, `jade_lizard`, `big_lizard`, `super_bull`, `super_bear`, `call_ratio_spread`, `zebra`, `iron_condor`, `iron_butterfly`, `bats`, `zeehbs` (subject to the 4-leg SFPM caveat: a single `zeehbs` emit must produce ≥2 SFPM-position payload entries).

**Do NOT admit strip-emit (HALT candidates):**
- `call_calendar_spread` — payoff depends on two *timescales* (short-term short leg, longer-term long leg), not on two strikes; a `{(K_i, w_i)}` tuple cannot capture the time-axis asymmetry. Rationale: Panoptic Timescales are a per-leg width parameter that determines streamia accrual range, not a strike.
- `diagonal_spread` — same time-axis issue as the calendar spread, compounded with a strike offset; the payoff surface is two-dimensional in (strike, timescale) and not reducible to a one-dimensional strike ladder.

Two non-primitive mechanisms appear in Panoptic but are out of scope for the strip-emit table because they are not standalone payoff objects:
- **Streamia** — funding-rate mechanism applied to every position; modifies cashflow timing of any primitive above but produces no independent payoff.
- **Timescales** — per-position width parameter (1H, 1D, 1W, 1M, 1Y presets) that fixes the streamia-accrual range; not a primitive.

## §4 References

- Panoptic. "18 Options Strategies Every Trader Should Know (With Emojis)." Research. https://panoptic.xyz/research/essential-options-strategies-to-know — accessed 2026-05-11.
- Panoptic Docs. "Streamia." https://panoptic.xyz/docs/product/streamia — accessed 2026-05-11.
- Panoptic Docs. "Timescales." https://panoptic.xyz/docs/product/timescales — accessed 2026-05-11.
- Panoptic Docs. "Smart Contracts Overview." https://panoptic.xyz/docs/contracts/smart-contracts-overview — accessed 2026-05-11. (Source for the 4-leg SFPM ceiling.)
- Panoptic Blog. "Panoptic: Your Next DeFi Alpha" (dated 2025-07-25). https://panoptic.xyz/blog/panoptic-your-next-defi-alpha — accessed 2026-05-11. (Source for live-on-Ethereum/Unichain/Base status and cumulative volume figure.)

## §5 Filtered candidate set

**Filter rule (v0.3, strict-equality predicate — anchor: Plan v0.2 → v0.3 §11.2 commit 997ac9f).** A row from §2 enters this set iff it satisfies BOTH predicates simultaneously:

1. `admits_strip_emit = yes` (deterministic `{(K_i, w_i)}` tuple exists, per §3).
2. `convexity_class == "long-vol"` (STRICT string equality; "mixed", "mixed-vol", or any directional-flavored compound class does NOT qualify).

**Math justification.** Carr-Madan replication of σ_T (PRIMITIVES.md §10 eq. 18) is a *positive*-weighted integral of OTM put + call payoffs. Mixed-vol primitives carry negative distributional δ-mass at strike kinks — outside the long-vol cone, unusable as σ_T building blocks. The v0.3 predicate excludes them ex-ante via strict `convexity_class == "long-vol"`, tightening the v0.2 negation rule (`!= "short-vol"`) which over-admitted 8 mixed-vol rows.

**Reverse-IC baseline.** §2's `iron_condor` is classed `short-vol` under standard (debit-paid) leg orientation; cohort_5_strip uses the LONG-vol orientation (credit-wings flipped to debit-wings — see `simulations/saas_builder/cohort_5_strip/__init__.py` package docstring, "long-vol Carr-Madan 3-condor"), under which the convexity class is long-vol — qualifying it as the explicit baseline anchor.

**Candidate set (rule-pass rows; not pre-ranked, per anti-fishing):**

| primitive_id | role | one-line rationale (strip-emit eligibility · long-vol-strict qualification) |
|---|---|---|
| reverse_iron_condor (cohort_5_strip) | BASELINE — comparison anchor | Strip-emit eligible: four strikes, four sign-alternating weights, same SFPM 4-leg footprint as standard IC. Long-vol qualification: cohort_5_strip's reverse-orientation produces a long-vol Carr-Madan 3-condor (per `simulations/saas_builder/cohort_5_strip/__init__.py` package docstring). |
| long_straddle | candidate | Strip-emit eligible: two coincident strikes, equal positive weights. §2 `convexity_class` value is exactly `"long-vol"` — strict equality holds; pure long-vol with no directional skew. |
| long_strangle | candidate | Strip-emit eligible: two separated strikes, equal positive weights. §2 `convexity_class` value is exactly `"long-vol"` — strict equality holds. |
| zeehbs | candidate (with caveat) | Strip-emit eligible: six strikes, six weights — emit payload must span ≥2 SFPM positions (6 > 4-leg SFPM ceiling, §2 on-chain_liquidity column). §2 `convexity_class` value is exactly `"long-vol"` — strict equality holds. |

**Filtered-OUT by v0.3 predicate tightening** (were in v0.2 §5 but no longer qualify under strict equality):
- `long_call` — **primary: cohort_5_strip API-arity constraint.** Emit API accepts only 12-leg payloads (`STRIP_TOTAL_LEGS = 12`, pinned at `simulations/saas_builder/cohort_5_strip/types.py:49`); a 1-leg primitive does not fit. Secondary (cosmetic): `convexity_class = "long-vol (directional bullish)"` fails strict equality. Even under §2 reclassification to pure `"long-vol"`, API-arity would still exclude.[^arity]
- `long_put` — same dual rationale: primary 1-leg-vs-12-leg API-arity exclusion; secondary string mismatch (`"long-vol (directional bearish)"`).[^arity]
- `call_spread`, `put_spread`, `super_bull`, `super_bear`, `call_ratio_spread`, `zebra` — all mixed-vol (point-concavity at strike kinks, PRIMITIVES.md §10 anchor); excluded by the strict-equality predicate.

**Count after v0.3 filter:** 3 candidates + 1 baseline = 4 rows; within plan's "2–4 primitives" range.

[^arity]: §2's `admits_strip_emit = "yes"` (annotated "trivial ladder") for `long_call`/`long_put` is a v0.2-era latent classification error: the cohort_5_strip emit API requires a 12-leg payload (`STRIP_TOTAL_LEGS = STRIP_CONDOR_COUNT * LEGS_PER_CONDOR = 12`, `simulations/saas_builder/cohort_5_strip/types.py:49`), so 1-leg primitives do not admit strip-emit regardless of analytic ladder-ability. Amending §2 is **out of scope for Task 1.2**; a separate follow-up task will land the disposition memo and §2 correction.

## §6 Comparability proof routing

**Task 2.3b status: SKIPPED for this A1 execution.** Plan v0.3 §6 Task 2.3b is conditional on at least one Phase-1 filtered candidate adapter declaring `comparability_proof = "primitive_variant"`. Inspection of the four adapters landed under Task 2.2 (commit `6c871f0`, with downstream filter-set refinement at `d0aa41e`) shows none take that lane; every adapter routes to one of the two already-shipped verifier classes (`CarrMadanEnvelopeVerifier` for `tiled_body`, `NormalizedScoreVerifier` for `normalized_score`). The conditional therefore evaluates false and Task 2.3b records this rationale in lieu of authoring a third verifier.

**Per-adapter `comparability_proof` routing (from Task 2.2 commit `6c871f0`):**

- `reverse_iron_condor` → `tiled_body` — the strip satisfies the cohort_5_strip tiled-body convention; the existing `CarrMadanEnvelopeVerifier` applies unchanged, since the 12-leg payload is exactly a 3-tile reverse-IC ladder.
- `long_straddle` → `normalized_score` — narrow-clustered geometry produces a non-zero strip floor at S_0, absorbed by the multiplicative correction the normalized-score verifier already implements.
- `long_strangle` → `normalized_score` — wide-separated bodies likewise produce a non-zero strip floor at S_0, absorbed by the same multiplicative correction.
- `zeehbs` → `normalized_score` — 6-leg primitive approximated by a 12-leg reverse-IC; the residual floor from the approximation is absorbed by the normalized-score correction.

**Forward-deferral contract.** No `PrimitiveVariantVerifier` implementations are authored under this A1 plan; the `primitive_variant` lane remains DEFERRED. If a future Stage-3 wave introduces an adapter whose `comparability_proof = "primitive_variant"`, that wave must (a) author the verifier per the Task 2.3b spec in plan v0.3, (b) add an entry to `EnvelopeComparator.primitive_variant_verifiers` registering the new adapter, and (c) author an equivalence test against the shipped `CarrMadanEnvelopeVerifier` on a reverse-IC baseline so the two lanes agree on the existing tiled-body case before the new lane is consumed downstream.

**Provenance.** Routing-decision evidence: Task 2.2 commit `6c871f0` (adapter `comparability_proof` field assignments) and Task 2.3 commit `d0aa41e` (Phase-1 candidate filter to deterministic-emit set). No further Task 2.3b artifacts are produced under this plan.
