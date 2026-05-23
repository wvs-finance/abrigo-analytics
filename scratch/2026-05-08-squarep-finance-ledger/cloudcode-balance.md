# Cloud Code Session Balance Log

**Why this file exists:** Operating rule from the daily TODO plan — "if Cloud Code session balance drops below $30, AGENT pings user before next agent dispatch." This log tracks daily start-of-day balance so the trigger has a clean signal and so the user has a forecast curve.

**Pre-cycle context:** $100 top-up sunk before this cycle started; current session credit ~$17 as of 2026-05-08 morning per user statement. Next top-up will count against the $400/mo cap.

## Conventions

- Record balance once per day at session start (or at first agent dispatch of the day)
- "Burn" = previous-day balance minus today's balance (positive number)
- Trigger: any day where balance < $30, alert user immediately

## Log

| Date | Balance ($) | Burn since last entry ($) | Cumulative session burn ($) | Trigger fired? | Notes |
|------|-------------|---------------------------|------------------------------|----------------|-------|
| 2026-05-08 | ~17 | n/a | n/a | **Approaching trigger ($30)** | User confirmed $17 starting balance during 2026-05-08 brainstorm; top-up likely needed within the week |
