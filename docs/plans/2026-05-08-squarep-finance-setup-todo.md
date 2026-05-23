# SquareP Finance Setup — Daily TODO Plan (May 8 → June 11)

> **For agentic workers:** This plan covers **admin / marketing / off-chain backend setup only**. Smart contracts, reactive contract logic, simulations, and analytics are out of scope — those run under the user's direct authorship in parallel. Tasks are tagged:
>
> - **AGENT** — Claude executes; user reviews + approves output
> - **USER** — third-party signup, payment auth, account creation, or any step requiring user identity
> - **HYBRID** — agent drafts, user reviews and submits/posts
>
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Operationally execute the May–June 2026 budget memo's admin-side commitments — brand surface, off-chain backend, Celo Proof of Ship cadence, and Hookathon-supporting marketing — across 34 days from memo date (2026-05-08) through UHI9 capstone submission (2026-06-11).

**Architecture:** Daily checklist mapped to the 34-day window. Each day has 1–3 prioritized tasks. Slipped tasks roll to next-day backlog without recalculating the schedule. The user's engineering work (Solidity hook, reactive contract, simulations, analytics) runs in parallel and is *not* gated by or gating this plan.

**Tech Stack (admin-side only):** Cloudflare (Registrar + DNS + Email Routing), Vercel (Hobby tier), Resend (transactional email free tier), X Basic, thirdweb (free tier), Alchemy (free → Growth June 1), AWS (on-demand), Karma GAP, Farcaster, GitHub.

**Spec source:** `docs/specs/2026-05-08-squarep-finance-budget-memo-design.md`

**Spend ledger:** `scratch/2026-05-08-squarep-finance-ledger/spend.md` (created Day 1, updated weekly minimum)

---

## Standing operating rules (apply every day)

- [ ] Every recurring vendor charge logged in spend ledger same-day
- [ ] If Cloud Code session balance drops below $30, AGENT pings user before next agent dispatch
- [ ] X posts cross-post to Farcaster same-day (Celo Proof of Ship reputation)
- [ ] No mainnet deploys other than Celo until UHI9 judges explicitly request mainnet polish
- [ ] If a daily task slips, append to next day's list — do not silently drop

---

## Week 1 (May 8 – May 14): Foundation

### Day 1 — Friday May 8 (today)

- [ ] ~~**HYBRID — Domain registration**~~ — **POSTPONED** per user decision 2026-05-08 PM. Trigger to revisit per spec §7. Saves $45 + Day 2 DNS/email setup overhead.

- [x] **USER — X free account created** (`@D2pFinance`) ✅ done — parent/lab handle
  - Paid subscription remains POSTPONED per spec §7

- [ ] **USER — Second X account: Abrigo product brand** (`@abrigo_xyz`, `@abrigo_fi`, or first-claim available)
  - Use the **new dedicated brand Gmail** (different from D2pFinance's email)
  - Same phone number reusable
  - Bio: agent will provide v1; cross-link with @D2pFinance
  - Success: account live; @D2pFinance and @abrigo bios cross-reference

- [ ] **AGENT — Draft X bio + multi-post pinned thread** *(pulled forward from Day 4)*
  - Output: `scratch/2026-05-08-squarep-finance-ledger/x-pinned-thread-v1.md` (8–10 short posts ≤280 chars each)
  - Brief: positioning, what Abrigo is, what UHI9 capstone will demo, link to GitHub
  - Success: user reads + approves; **posting moves to Day 2 or 3** (was Day 5 — 3 days of compound-interest claw-back)

- [x] **AGENT — Initialize spend ledger** at `scratch/2026-05-08-squarep-finance-ledger/spend.md` ✅ done

- [x] **AGENT — Note Cloud Code session balance** at start of day in ledger sidecar ✅ done

### Day 2 — Saturday May 9

*All Cloudflare DNS / Email Routing / Resend tasks REMOVED — domain postponed.*

- [ ] **AGENT — Draft @abrigo bio + multi-post pinned thread** (product-brand voice; distinct from @D2pFinance)
  - Output: `scratch/2026-05-08-squarep-finance-ledger/abrigo-pinned-thread-v1.md`
  - Cross-references @D2pFinance as parent

- [ ] **HYBRID — Post both pinned threads** (@D2pFinance + @abrigo)
  - Agent: revise per user edits
  - User: post + pin on both accounts
  - Success: both threads live; both pinned

### Day 3 — Sunday May 10

- [ ] **HYBRID — Vercel project scaffold**
  - Agent: scaffold a minimal Next.js or static site repo at `~/apps/d2p-finance-site/` (separate from analytics repo); README, single landing page placeholder, `vercel.json`
  - User: connect GitHub repo to Vercel; deploy
  - Success: `*.vercel.app` URL (e.g., `d2p-finance.vercel.app` or similar) serves placeholder landing page; URL added to both X bios

- [ ] ~~**HYBRID — Custom domain on Vercel**~~ — POSTPONED (domain itself postponed)

### Day 4 — Monday May 11

*X account creation pulled to Day 1, threads pulled to Day 2 (compound-interest claw-back). Paid subscription remains POSTPONED per spec §7. Custom-domain swap REMOVED — domain postponed.*

- [ ] **AGENT — Bio v2 polish** on both X accounts once Vercel landing page is live (replace GitHub-only link with `*.vercel.app` URL in @D2pFinance and @abrigo bios)
  - Success: bios updated; pinned threads untouched

### Day 5 — Tuesday May 12

*X pinned thread post pulled forward (target: Day 2 or 3 once user approves the draft from Day 1).*

- [ ] **AGENT — Prepare GitHub org `squarep-finance`** (or personal repo if org costs friction)
  - Create org skeleton repo `squarep-finance/site` (Vercel-linked) and a placeholder `squarep-finance/abrigo-hookathon` (the eventual UHI9 capstone repo — empty for now, user will populate with engineering content)
  - Success: org exists, two empty repos created with READMEs

### Day 6 — Wednesday May 13

- [ ] **USER — Karma GAP project listing** for Celo Proof of Ship
  - Project name: "Abrigo"
  - Description: agent-drafted (see next task)
  - Success: project visible on Karma GAP, claimable by user wallet

- [ ] **AGENT — Draft Karma GAP project description + roadmap milestones**
  - Output: `scratch/2026-05-08-squarep-finance-ledger/karma-gap-listing-v1.md`
  - Roadmap items map to Celo-side infrastructure work (Mento integration, agent identity primitives, reactive contracts on Celo) — *not* the UHI9 capstone secret sauce
  - Success: user pastes into Karma GAP

- [ ] **USER — Farcaster account creation** (`@squarepfi` or similar)
  - Connect Warpcast app; cross-post X content from Day 5 onward
  - Success: account live, first cast mirrors X pinned thread

### Day 7 — Thursday May 14

- [ ] **USER — thirdweb account creation** (free tier)
  - Connect deployer wallet (the same wallet that will deploy to Celo for Proof of Ship)
  - Success: thirdweb dashboard accessible

- [ ] **USER — Alchemy account creation** (free tier — Growth deferred to June 1)
  - Create projects: `abrigo-uhi9` (Unichain Sepolia), `abrigo-celo` (Celo mainnet)
  - Success: API keys generated, stored in user's password manager (NOT committed)

- [ ] **AGENT — Weekly ledger reconciliation**
  - Sum charges against May allocation; verify under $400 cap
  - Output appended to `spend.md`

---

## Week 2 (May 15 – May 21): Public surface + Celo Proof of Ship cadence

### Day 8 — Friday May 15

- [ ] **HYBRID — UHI10 reserve application drafted**
  - Agent: draft application copy answering Atrium's stock questions, framed for "Fair Flow Frontier" theme; positioned as Abrigo Stage-2 continuation
  - Output: `scratch/2026-05-08-squarep-finance-ledger/uhi10-application-draft.md`
  - User: **HOLD — do NOT submit.** This is a *reserve* artifact; only fires if June 11 capstone is missed. Saved on disk, ready to paste if needed.
  - Success: draft on disk, user has read it

### Day 9 — Saturday May 16

- [ ] **USER — First Celo Proof of Ship submission** via Karma GAP
  - Update Karma GAP project with first measurable shipping artifact (could be: site live, GitHub repo public, X account active — all administrative wins count for cadence)
  - Success: AI evaluator picks up the update at next monthly evaluation

### Day 10 — Sunday May 17

- [ ] **AGENT — Draft X thread "Why Abrigo: the wage→capital boundary problem"**
  - 5–8 tweets; non-jargon framing; references the structural problem post-Keynesian distribution
  - Output: `scratch/2026-05-08-squarep-finance-ledger/x-thread-002-wage-capital.md`
  - User reviews + posts (cross-cast to Farcaster)

### Day 11 — Monday May 18

- [ ] **HYBRID — Vercel landing page v1** (replace placeholder)
  - Agent: write minimal copy (one paragraph thesis + GitHub + X + Karma GAP links); use whatever stack the Vercel scaffold uses; no fancy UI
  - User: review, push to repo (Vercel auto-deploys)
  - Success: `*.vercel.app` URL serves real content, no Lorem Ipsum; URL pinned in both X bios

### Day 12 — Tuesday May 19

*Resend test email REMOVED — no custom-domain email; brand correspondence runs from dedicated Gmail.*

- [ ] **AGENT — Brand-Gmail signature template**
  - Output: short signature for the dedicated brand Gmail (name, role, X handles, GitHub, Vercel URL)
  - User pastes into Gmail Settings → Signatures
  - Success: outbound brand-Gmail emails carry consistent footer linking to public surfaces

### Day 13 — Wednesday May 20

- [ ] **USER — Farcaster cadence established**
  - All Day 5+ X content cross-cast to Farcaster
  - Karma GAP listing linked from Farcaster bio
  - Success: Farcaster account has ≥3 casts; AI evaluator for Proof of Ship can see activity

### Day 14 — Thursday May 21

- [ ] **AGENT — Draft X thread "Pair-D: empirical β = +0.137 explained"**
  - References the existing `memory/project_pair_d_phase2_pass.md`; non-statistician audience; one chart
  - Output: `scratch/2026-05-08-squarep-finance-ledger/x-thread-003-pair-d.md`
  - User reviews; *holds* until UHI9 build provides a hook to attach it to (don't burn the empirical proof too early — judges should encounter it on the demo)

- [ ] **AGENT — Week 2 spend ledger review + Cloud Code balance check**

---

## Week 3 (May 22 – May 28): UHI9 Hookathon kickoff (May 25); supporting marketing

### Day 15 — Friday May 22

- [ ] **AGENT — Build dev-journal template** for UHI9 capstone phase
  - Daily-entry template: what shipped, what blocked, what's tomorrow
  - Output: `~/apps/squarep-finance-site/dev-journal/2026-05-22.md` (and onward)
  - Purpose: feed Karma GAP + occasional X posts; *not* a blog post per day, just a note

### Day 16 — Saturday May 23

- [ ] **AGENT — UHI9 capstone repo READMEs scaffolded**
  - `squarep-finance/abrigo-hookathon/README.md`: project name, theme alignment ("IL-protection hook + reactive ratchet over Panoptic-style position"), team (solo), placeholder demo-day video link, license
  - User retains full authorship over Solidity/contract content; agent only drafts the framing prose
  - Success: README on `main`, no contract code yet (user-driven)

### Day 17 — Sunday May 24

- [ ] **AGENT — Draft X thread "How Abrigo's premium-funded ratchet maps to UHI9 theme"**
  - Bridges UHI9's "IL & Yield Systems" theme to Abrigo's product framing
  - Output: `scratch/2026-05-08-squarep-finance-ledger/x-thread-004-uhi9-fit.md`
  - User reviews, posts evening of May 25 (Day 18) to align with Hookathon kickoff

### Day 18 — Monday May 25 (UHI9 Hookathon official start)

- [ ] **USER — Post X thread 004** (UHI9-fit thread, drafted Day 17)

- [ ] **USER — Public-progress shipping commit** to UHI9 capstone repo
  - First contract scaffold or design doc — user's choice; agent doesn't author
  - Success: GitHub commit on `main`, visible to Karma GAP crawl

- [ ] **AGENT — Update Karma GAP with kickoff milestone**

### Day 19 — Tuesday May 26

- [ ] **AGENT — Monitor Alchemy free-tier usage**
  - If approaching rate limits, alert user; if not, hold Growth-tier upgrade for June 1

- [ ] **AGENT — Cloud Code top-up check**
  - If session balance < $30, alert user

### Day 20 — Wednesday May 27

- [ ] **AGENT — AWS account provisioning IF first control-proof job is queued by user**
  - Otherwise: hold; do NOT spin up account speculatively
  - User: confirms whether control proof is needed this week
  - Success: either AWS account active OR explicit "not yet" logged

### Day 21 — Thursday May 28

- [ ] **AGENT — Mid-cycle ledger review**
  - Compare May spend vs $400 cap
  - Forecast June commit (Alchemy $49 + AWS $100 budget + X $8 + mainnet gas $30)
  - Flag if any vendor is trending over

- [ ] **HYBRID — Cloud Code top-up if needed**
  - User authorizes; agent does not auto-renew
  - Log $100 → ledger if executed

---

## Week 4 (May 29 – June 4): Polish + secondary submission prep

### Day 22 — Friday May 29

- [ ] **HYBRID — Vercel landing page v2**
  - Agent: add "Status" section with live UHI9 commit-count, link to Karma GAP, prominent X handle
  - User: review, push
  - Success: site shows current build status, not just static thesis

### Day 23 — Saturday May 30

- [ ] **AGENT — Draft X thread "Reactive contracts: a primer for Hookathon judges"**
  - Bridges Reactive Network sponsor track + Somnia architectural overlap
  - Output: `scratch/2026-05-08-squarep-finance-ledger/x-thread-005-reactive.md`
  - User reviews; holds for posting in week 5

### Day 24 — Sunday May 31

- [ ] **USER — Second Celo Proof of Ship update** via Karma GAP
  - End-of-May milestone: list everything shipped this month (admin + engineering)
  - Success: AI evaluator scores the May submission

### Day 25 — Monday June 1

- [ ] **HYBRID — Alchemy Growth tier upgrade** ($49)
  - User: payment auth
  - Agent: confirm increased rate limits in dashboard
  - Log: $49 → ledger under "Hackathon infra committed"

### Day 26 — Tuesday June 2

- [ ] **AGENT — AWS spend monitor**
  - Daily cost alert configured (≤$5/day) so a runaway control-proof job pings instead of bleeding money silently
  - User: review CloudWatch billing alarm

### Day 27 — Wednesday June 3

- [ ] **HYBRID — Somnia Agentathon submission preparation**
  - User: pull dates/prize/track structure from the Somnia Agentathon page (JS-rendered; agent cannot)
  - Agent: if dates allow ≥4 days post-June 11, draft submission package skeleton (project description, demo link placeholder, track positioning); else mark "deferred to next iteration"
  - Output: `scratch/2026-05-08-squarep-finance-ledger/somnia-agentathon-submission-v1.md` OR a deferral note
  - Success: clear go/no-go decision logged

### Day 28 — Thursday June 4 (submission-week reserve activates)

- [ ] **AGENT — Daily ledger checks begin** (every day through June 11)

- [ ] **AGENT — Draft X "submission week" countdown thread**
  - 1 tweet per day June 4–10; final thread June 11
  - Output: `scratch/2026-05-08-squarep-finance-ledger/x-countdown-week.md` (all 8 entries pre-drafted; user posts daily)

---

## Week 5 (June 5 – June 11): UHI9 final polish + submission

### Day 29 — Friday June 5

- [ ] **USER — Post countdown tweet 1** (drafted Day 28)

- [ ] **AGENT — Draft "What we shipped" recap thread**
  - Comprehensive thread for posting June 11 after submission
  - Output: `scratch/2026-05-08-squarep-finance-ledger/x-recap-final.md`

### Day 30 — Saturday June 6

- [ ] **HYBRID — Demo video script draft**
  - Agent: 3-minute script structure (problem → architecture → demo → ask), references existing β = +0.137 result and reactive primitive
  - User: revises for technical accuracy and personal voice
  - Output: `scratch/2026-05-08-squarep-finance-ledger/demo-video-script.md`

- [ ] **USER — Post countdown tweet 2**

### Day 31 — Sunday June 7

- [ ] **USER — Demo video record + edit**
  - Agent does NOT touch this — user-only work (camera, screen capture, voiceover)
  - Success: 3-minute MP4 staged in cloud (Drive / Loom / similar)

- [ ] **USER — Post countdown tweet 3**

### Day 32 — Monday June 8

- [ ] **HYBRID — README final polish**
  - Agent: check Atrium's submission requirements; verify README hits every required section (project, theme alignment, team, demo link, deployment addresses, license)
  - User: pushes final README

- [ ] **HYBRID — Unichain Sepolia testnet deploy smoke-test**
  - User: deploys hook + reactive contract via thirdweb or forge script
  - Agent: verifies deployment address visibility on Unichain Sepolia explorer; updates README with addresses
  - Success: contract addresses in README link to live testnet explorer

- [ ] **USER — Post countdown tweet 4**

### Day 33 — Tuesday June 9 (buffer day)

- [ ] **AGENT — Submission-package dry run**
  - Walk Atrium's submission form fields; verify every field has a draft answer
  - Output: `scratch/2026-05-08-squarep-finance-ledger/submission-form-draft.md`
  - User: review and refine

- [ ] **HYBRID — Cloud Code top-up if balance low**
  - Don't let an overnight agent stall on submission week

- [ ] **USER — Post countdown tweet 5**

### Day 34 — Wednesday June 10 (T-1)

- [ ] **HYBRID — Final submission package assembly**
  - Agent: cross-check video link, README link, addresses link, demo URL all return 200
  - User: paste final answers into Atrium submission form (DO NOT submit yet — hold for June 11)

- [ ] **USER — Post countdown tweet 6**

### Day 35 — Thursday June 11 (SUBMISSION DAY)

- [ ] **USER — Final review of submission form** (no last-minute edits unless critical)

- [ ] **USER — Submit to UHI9 Hookathon by deadline** (verify Atrium's exact UTC cutoff time the morning of)

- [ ] **USER — Post final recap thread** (drafted Day 29)

- [ ] **AGENT — Update Karma GAP with submission milestone** (Celo Proof of Ship June scoring)

- [ ] **AGENT — Final May–June ledger reconciliation**
  - Compare actual spend to budget memo's realistic point estimate (~$505 of $800)
  - Output: `scratch/2026-05-08-squarep-finance-ledger/final-cycle-report.md`
  - Note rollover amount available for next cycle

---

## Post-window (June 12+) — out of plan, but seeded here for continuity

The following are *not* in this plan's 34-day window but are the natural next steps once submission lands. Listed so they don't fall through:

- **June 19 (UHI9 Demo Day)** — user attends; agent prepares "thank-you" follow-up tweets
- **Direct outreach drafts** to Algebra, Panoptic, Mento — agent drafts; user sends after Demo Day. Mento priority (cCOP/COPm fit). Templates in `scratch/2026-05-08-squarep-finance-ledger/outreach/`
- **Somnia Agentathon submission** — if dates allowed and architecture reskinned
- **UHI10 application** — fires only if June 11 missed; held draft from Day 8
- **Next-cycle budget memo** (covering July+) — separate spec when this cycle closes

---

## Risk register (operational, not budget)

| Risk | Mitigation |
|---|---|
| User burnout in submission week | Days 29–34 have agent-prepped artifacts; user only reviews/posts |
| Cloud Code session dies overnight mid-task | Standing rule: agent pings if balance < $30; user authorizes top-up before agents stall |
| DNS / email deliverability breaks | Day 12 (May 19) is the canary; Resend issues caught with 3+ weeks to fix |
| X account suspended | Backup: Farcaster + GitHub. Don't burn engagement-bait content; stay technical |
| Atrium changes submission requirements late | Day 32 (June 8) and Day 33 (June 9) catch this with 2+ days buffer |
| Solo-builder schedule slip on engineering | This plan's admin work is *parallel* and does not gate the engineering. If engineering slips, admin still ships, demo video still records, X cadence still runs |
| Somnia Agentathon URL never yields dates | Day 27 (June 3) is the go/no-go; deferral is acceptable, not a failure |

---

## Invariants

- This plan does not contain Solidity, simulation, or analytics tasks — those are user-domain
- Mainnet deploys are gated to Celo + (rare) Unichain L2; Ethereum mainnet is out
- Every dollar logged in spend ledger same-day; cumulative tracked against $400/mo cap
- Slipped daily tasks roll forward, never silently drop
- User retains explicit veto on any agent-drafted public-facing copy before it ships
