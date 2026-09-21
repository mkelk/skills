---
name: sentry
description: Read what is actually in Sentry and report it plainly. "check" fetches the unresolved issues and the cron monitors for this project and says what needs a person, what is noise, and what the absence of events does and does not prove. Read-only — it never resolves, ignores or deletes anything. Use when the user types /sentry, asks what Sentry is showing, or wants to know whether an error actually reached it.
---

# sentry — what the error sink actually holds

**Dispatch on the argument; read ONLY the matching reference and follow it exactly.** With no
or an unknown argument, show this table and ask.

| Argument | Cadence | Door |
|---|---|---|
| `check` | whenever the human asks what Sentry is showing | `references/check.md` — the unresolved issues and the monitors, newest first, with what needs a person and what is throttling. |

Principles:

- **Read-only, always.** This skill never resolves, ignores, assigns, deletes or mutes
  anything. Sentry's state is a record of what happened; a tool that tidies it destroys the
  evidence the next person needs. If something should be resolved, say so and let a person do
  it.
- **The absence of an event is not the absence of a problem.** This project has three
  throttles between a failure and an issue — `SENTRY_BURST_PER_HOUR` (20 of one fingerprint an
  hour), `ERROR_RELAY_PER_HOUR` (20) and `ERROR_RELAY_PER_DAY` (50) — plus a Developer plan
  capped at 5,000 events a month. **A quiet Sentry can mean nothing broke, or that everything
  broke twenty-one times.** Every report says which throttles are in play rather than
  implying silence is health.
- **One project exists, and that is a decision, not an oversight.** `focusheron-prod` is the
  only Sentry project; the other hosts get one the day they need one. So a check covers
  production and says nothing about `docker-host` or `focusheron-stage`, and a report that
  does not say so is misleading by omission.
- **Say where each number came from.** A count from the issues list, a count from a monitor
  and a count from the plan's quota are three different instruments. When they disagree, that
  disagreement is the finding.
