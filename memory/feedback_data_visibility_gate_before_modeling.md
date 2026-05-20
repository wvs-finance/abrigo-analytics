---
name: data-visibility-gate-before-modeling
description: Universal methodology rule (2026-05-19) — brainstorming, modeling, and econometrics on any Abrigo iteration only after data-visibility under free tier (or quoted "data-visibility" tier provider) is established. Pre-pin, Y/X selection, and β estimation are downstream of data-reachability confirmation.
metadata:
  type: feedback
---

## Rule

For every active or candidate Abrigo (Y, M, X) iteration, the **data-visibility gate**
must pass BEFORE any brainstorming, modeling, or econometric work proceeds.

Two acceptable outcomes for the gate:
1. **Free-tier PASS** — required public data is reachable, queryable, and refreshable
   under a free public tier (e.g., Taostats API public endpoint, Dune free tier within
   credit limits, on-chain RPC, public CSV download from government agency).
2. **Quoted-provider PASS** — required data is behind a paid tier, but the provider
   is identified, the tier price is *quoted*, and the data scope under that tier is
   confirmed sufficient for the iteration. The decision to pay is then a separate
   user call; the gate itself is "we know what it costs and what it gets us."

If neither outcome holds → **BLOCK at G0**. No brainstorming, no modeling, no
econometric setup. Park the iteration until data-visibility is resolved.

## Why

Per user (2026-05-19, post-Wave-1 dispatch):

> "Range-sorming [brainstorming], the modeling and econometrics model, only after
> we establish if there is data visibility under the free tier or we quote
> 'data visibility' their order provider."

The rule prevents the failure mode of pre-pinning Y/X/lag/sign for a cohort whose
underlying data is structurally unreachable (E9-A `[GAP-1]` UPME registry 404 is the
proximate trigger). Pre-pin work without data-vis closure is rework risk: when the
data turns out to be unreachable, the pre-pin gets discarded; when the data turns
out to be reachable but in a different schema than assumed, the pre-pin gets edited
post-hoc (silent fishing exposure).

## How to apply

Every iteration's G0 gate (per [[portfolio-progressive-gating-workplan]]) must
include a data-visibility sub-check producing one of:

- **DV-PASS-FREE**: data source + endpoint + refresh cadence + sample row count
  documented; reproducible by anyone with the public URL
- **DV-PASS-QUOTED**: provider + tier name + monthly cost + data scope under tier
  documented; user decides separately whether to purchase
- **DV-BLOCK**: neither free-tier nor quoted-provider path exists at this time;
  iteration parked with explicit re-check trigger (e.g., "re-check 2026-Q4 when
  XM publishes AGPE registry")

The audit is a *cross-cutting* gate. It is run BEFORE the iteration's domain-specific
G0 checks (e.g., N_MIN cohort presence, regulatory permissibility, Panoptic
tradability). Order:
1. Data-visibility gate (this rule)
2. Permissionless-cohort regulatory gate ([[colombian-crypto-regulation-2026-constraint]])
3. N_MIN cohort presence (anti-fishing invariant)
4. Panoptic tradability / Stage-2 firewall
5. Iteration-specific G0 sub-checks

## Currently-active iteration audit status (post-Wave-1, 2026-05-19)

| Iteration | DV status | Notes |
|---|---|---|
| E8 dTAO × Maymin | DV-PASS-FREE | Taostats API public; Maymin (2026) data is published |
| E4 narrowed Superfluid | DV-PASS-FREE | Dune q/3399900 re-execute COMPLETED 83 credits |
| E7-A Mento Reserve | DV-PASS-FREE (pending verification) | Celo RPC + Mento Reserve dashboard public; needs explicit confirmation |
| E5 RefiColombia | DV-PASS-FREE | subsidios.reficolombia.org public API + Celo RPC; floor relaxation per [[e5-floor-relaxation-current-data-availability]] |
| E9-A AGPE Energy-AMM | DV-BLOCK (deferred) | UPME registry 404; XM API not yet verified — Wave 2 audit to resolve |

## Anti-fishing carry-forward

Data-visibility gating does NOT relax pre-pin / HALT-on-spec-vs-data invariants.
It adds an upstream gate. Once an iteration clears DV, all prior anti-fishing rules
apply unchanged.

## Links

[[portfolio-progressive-gating-workplan]] — workplan that this gate amends
[[e5-floor-relaxation-current-data-availability]] — paired methodology shift
[[abrigo-portfolio-prioritization-with-fallback]] — fantasy-threshold rules carry forward
[[colombian-crypto-regulation-2026-constraint]] — regulatory gate, runs after this one
[[pathological-halt-anti-fishing-checkpoint]] — anti-fishing preserved
