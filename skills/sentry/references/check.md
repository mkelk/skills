## Purpose

Fetch what is in Sentry right now and report it so a person can act. Read-only.

## Step 0 — The token, and what to do when there is not one

**This project's `SENTRY_DSN` is write-only.** A DSN sends events; it cannot read them. Reading
needs a **Sentry auth token**, and as of 2026-09-21 there is none on this machine — not in the
environment, not in `~/.config/sentry`, not in the repo's `.env`, and `.env.example` documents
no variable for one. So the first run of this door will stop here, and that is the correct
behaviour rather than a failure.

Look, in order: `$SENTRY_AUTH_TOKEN`, then `~/.config/sentry/token` (a single line, mode 600).

If neither exists, print exactly what to do and stop:

> Sentry needs a read token, which is separate from the DSN. Make one at
> **Settings → Account → User Auth Tokens** (or an organization token under
> **Settings → Auth Tokens**) with the scopes **`event:read`**, **`project:read`** and
> **`org:read`** — read scopes only; this skill never writes. Then:
> `mkdir -p ~/.config/sentry && printf '%s' '<token>' > ~/.config/sentry/token && chmod 600 ~/.config/sentry/token`

**Never print the token, never pass it in argv** (it shows in `ps` and `docker top`) — pass it
in a header from an environment variable. Verify it by prefix and length only.

## Step 1 — The region

Use **`https://de.sentry.io/api/0/`**. The DSN is on `ingest.de.sentry.io`, the EU region, and
the regional host is the one to prefer.

**Corrected 2026-09-21, first real run:** this door previously claimed a token made in the EU
organisation returns `401` or an empty list against `sentry.io`, and that this "will bite."
**It does not.** Measured with a real `sntryu_` token: `sentry.io` and `de.sentry.io` returned
*identical* results for `/organizations/`, `/organizations/<org>/projects/` and the issues
endpoint — same status, same bodies. The warning was written from expectation and never
tested, in a door whose whole subject is that an untested claim gets believed. Use the
regional host anyway (it is the documented one and avoids a redirect), but **do not diagnose a
`401` as a region problem** — that was invented here, and chasing it would waste exactly the
time the warning claimed to save.

## Step 2 — Discover the organisation and project. Do not hard-code them.

```
GET /api/0/organizations/                       → the org slug(s) this token can see
GET /api/0/organizations/<org>/projects/        → the project slugs
```

Expect exactly one project, `focusheron-prod`. **If you find more than one, say so** — it means
another host got a project since `docs/current/how/hosts.md` was written, and the report's
scope changed without anyone saying. If you find none, the token is scoped to the wrong
organisation.

## Step 3 — Fetch

- **Unresolved issues**, newest first:
  `GET /api/0/projects/<org>/<project>/issues/?query=is:unresolved&statsPeriod=14d`
  Take for each: `shortId`, `title`, `culprit`, `level`, `count`, `userCount`, `firstSeen`,
  `lastSeen`, `permalink`.
- **The cron monitors**: `GET /api/0/organizations/<org>/monitors/` — this project runs
  `newsletter-schedule` (`SENTRY_MONITORS`), one monitor on the Developer plan. A monitor that
  has not checked in is a different and usually worse signal than an error: it means something
  did not run at all.

Both are paginated. Read the `Link` header rather than assuming one page — a busy day is more
than 100 issues and a truncated list reported as complete is the failure this skill exists to
avoid.

## Step 4 — Report

Lead with whether anything needs a person.

```
SENTRY · focusheron-prod · <date> <time>

NEEDS A PERSON
  <shortId>  <level>  <title>
             <count> events, <userCount> users, last seen <age>
             <permalink>                                         (or "  —")

MONITORS
  newsletter-schedule   <ok | missed | error>   last check-in <age>

QUIET, OR THROTTLED
  <what the throttles would have hidden — see below>
```

**Rank by what a person would act on, not by count.** A single `error` on a delivery path
outranks two hundred `warning`s from a crawler. `level`, `culprit` and `userCount` decide that;
`count` alone does not.

**Always state the throttles.** Say, in one line, that one fingerprint is capped at 20 an hour,
the relay at 20 an hour and 50 a day, and the plan at 5,000 events a month — and that a
fingerprint at or near 20 in the last hour is **evidence of throttling, not of a count**. When
an issue's `count` sits exactly on a limit, say that the real number is unknown and larger.

**Name what this does not cover:** only `focusheron-prod` has a Sentry project, so the report
says nothing about `docker-host` or `focusheron-stage`. Silence from them is not evidence.

## Step 5 — Do not tidy

No resolving, ignoring, assigning, deleting or muting, ever, including when the human asks
in passing. If something should be resolved, name it and let them click. A skill that cleans a
record destroys the evidence its next run depends on.

## Known, and worth carrying into the first real check

- **Whether a spend-ceiling refusal reaches Sentry at all is unproven** as of 2026-09-21. The
  architecture relies on it: Morten chose *let prod hit the ceiling and send Sentry issues*
  over any seat-executed pause. If a ceiling hit lands only as a `logger.warn`, production goes
  quiet with nothing raised. **A guard is a claim until someone has watched it fire** — so if a
  check runs after a ceiling hit and shows nothing, that is a finding, not a clean bill.
- The Developer plan carries **5,000 events and one cron monitor** a month.
