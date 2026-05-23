---
name: SOTA Review 2026-05-08 — competitive landscape findings
description: Headline findings from the May 2026 4-track SOTA review (Numo as benchmark) — what cross-product is empty, who are the partners, who are the pivot risks
type: project
---

SOTA review committed at `3a75595` on `iter/saas-builder-stage-2`. Artifacts under `scratch/2026-05-08-sota-review/` (DESIGN.md, 4 tracks, SUMMARY.md). Numo (Robert Leifke) used as triple-role benchmark.

**Headline finding.** The cross-product of (convex × EM-FX-native × wage-earner-accessible × premium-funded ratchet × open-source × permissionless) is empty across 50+ players surveyed. No competitor in May 2026 occupies the Abrigo intersection.

**Numo status.** Numoen (2022 "world's first permissionless options exchange," squared/perpetual options via RMM) pivoted to Numo (2025–26 "market maker for global payments" — linear EM-FX forward AMM, YieldSpace-style discount curves, Uniswap V4 hook, Valora wallet fork). Forwards are linear. Abrigo's convex + premium-funded ratchet wedge survives intact. Numo is the highest-probability future competitor (6–12 months) — could bolt options onto `forex-swap` given the squared-options pedigree.

**Top-5 partnership candidates** (ranked): Mento (denomination layer, also pivot risk), Panoptic (settlement venue), Littio + Bitso (LATAM on-ramp), Yellow Card (Africa on-ramp), Cowrywise (Africa white-label / population-fit precedent).

**Top-3 competitive risks**: (1) Numo bolts options onto FX-forward AMM; (2) Nubank pivots into long-gamma USDC vs BRL (R$45B BR 2026 investment, 131M users, USDC desk at 4%); (3) Lemon Cash extends Morpho integration to Panoptic (smallest technical leap among Track-3 fintechs).

**Anti-fishing.** No silent scope expansion; 7-axis scoring schema pinned in DESIGN.md before dispatch; refutation candidates (Numo overlap, Dalgıç 2024 insurance-arrangement) surfaced explicitly. Pair-D PASS verdict empirically strikes down the only refutation candidate (premium drag dominates spot-stablecoin holding).

**Why:** Establishes the competitive landscape at the May 2026 snapshot; informs Stage-2 M-design positioning, partnership outreach sequencing (Mento + Panoptic before Numo pivot), and grant/accelerator competitive sections.

**How to apply:** When the user discusses positioning, partnerships, competitive context, grant applications, or Numo specifically — reference this artifact set rather than re-deriving the landscape. The tracks and SUMMARY have inline citations and 7-axis scoring tables. Reverify before recommending action against any specific player (their state may have shifted since 2026-05-08).
