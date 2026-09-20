## Purpose

Answer "what is running, is anything waiting for me, has anything stalled" in one screen,
from files and processes, never from memory and never by asking the sessions.

## Step 1 — Read the table

`.devmeta/streams.md` in the current checkout (it is the same on every branch; if the checkout
is behind master, read master's with `git show master:.devmeta/streams.md`). Each row gives a
stream's increment, session name, branch, worktree, ports and host. If the file is missing,
say so and stop — this door has nothing to stand on without it.

## Step 2 — Measure each stream, on the thing

For every row, gather — all read-only, all from the machine, none from a message:

| what | how |
|---|---|
| its session | `ListAgents`; match the row's session name. Absent → `no session`. State as listed: busy / idle / waiting. |
| its ticks | in the row's worktree: `tk list --status open` filtered to the increment's project and epics. Count in-progress (●), awaiting-human (◐), open-and-ready (○ with no blocker), at-checkpoint (the project tick open with `completion.md` present). |
| implementer worktrees | `git worktree list` from the row's worktree, rows under `.ticks-worktrees/` whose branch is `tick/<one of its epics>/*`; for each, uncommitted lines (`git status --short | wc -l`) and commits ahead of the stream branch. |
| last movement | age of the stream branch's tip commit; age of the newest commit on any of its tick branches. |
| playwright | `pgrep -f "playwright tes[t]"` — if any, which worktree path it runs in. |

## Step 3 — Classify

Per stream, one word, by these rules in order:

- **checkpoint** — project tick open, `completion.md` present, no in-progress tick → waiting to be landed.
- **needs Morten** — any tick awaiting human, or a human item in the overview not yet answered.
- **stalled** — no in-progress tick, no implementer process, AND either (a) open ready ticks exist with no dispatch for more than 20 minutes, or (b) the session is `waiting` and the newest commit is older than 30 minutes, or (c) an implementer worktree has uncommitted work and no session. Say which.
- **running** — in-progress ticks or live implementer worktrees.
- **idle** — nothing open, nothing in flight (a scoped-not-started stream, a docs-only branch).

## Step 4 — Print

Exactly this shape, nothing narrated around it:

```
NEEDS MORTEN:
  <stream>: <what, in one line, with the tick id>          (or "nothing")
STALLED:
  <stream>: <which rule fired, with the number>            (or "nothing")

<stream>   <increment>   <session/state>   <ticks: n running, n ready, n human>   <last commit Xm ago>   <ports>
…
playwright: free | held by <worktree>
```

Then stop. If the human asks a follow-up ("why is X stalled"), answer from what was
measured; do not re-run the sweep.

## What this door never does

- Message a session. A stall is reported to the human; nudging is the seat's judgement.
- Edit `streams.md`. If the table is wrong (a row for a landed stream, a missing row), say so
  and let the seat fix it with the update-ref procedure.
