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
| its session | Two sources, and the second is the better one. (1) `ListAgents`: match the row's session name; gives busy / idle / waiting. (2) **`herdr api snapshot`** (when herdr runs — `~/.config/herdr/herdr.sock` exists): every agent with its `cwd` and `agent_status` (working / idle / **blocked**). Match by cwd = the row's worktree; this catches sessions that never registered with Claude's list (a resumed session, a pane opened by the human) and gives `blocked` as a first-class state, which `ListAgents` only shows as "waiting". **Two agents with the same cwd is a finding in itself** — report it; one checkout, one orchestrator. Needs `tk` ≥ 0.31 for `tk herd`, but the snapshot is `herdr`'s own CLI and needs nothing. |
| its ticks | in the row's worktree: `tk list --status open`. **The tracker is shared across every worktree of one repo, so filter by the stream's own epics** — a tick belongs to the stream if `tk show <id>` names one of its epics as parent. Count in-progress (●) and awaiting-human (◐) that way. **Ready is not `tk ready`** (it has no per-epic scope and counts the whole tracker): derive it from `tk graph <epic> --json` as open tasks whose blockers are all closed. Ignore ◐ ticks from earlier increments that were never closed (they show in every worktree). |
| at checkpoint | **the stream's own** `.devmeta/increments/increment-<its id>/completion.md` exists — never a glob over `increments/*/`, which matches every finished increment in the tree and says yes for everyone. |
| implementer worktrees | `git worktree list` from the row's worktree, rows under `.ticks-worktrees/` whose branch is `tick/<one of its epics>/*`; for each, uncommitted lines (`git status --short | wc -l`) and commits ahead of the stream branch. |
| last movement | age of the stream branch's tip commit; age of the newest commit on any of its tick branches. |
| playwright | `pgrep -f "playwright tes[t]"` — if any, which worktree path it runs in. |

## Step 3 — Classify

Per stream, one word, by these rules in order:

- **checkpoint** — project tick open, `completion.md` present, no in-progress tick → waiting to be landed.
- **needs Morten** — any tick awaiting human, or a human item in the overview not yet answered.
- **unknown driver** — the branch or a tick branch moved recently but no agent in either source has the row's worktree as its cwd. Not a stall: someone is working and the seat cannot see who. Report it first; the human usually knows (a session resumed from a transcript does not register with the others). If the row says the stream is the human's own, this is expected and is not reported.
- **stalled** — no in-progress tick, no implementer process, AND either (a) open ready ticks exist with no dispatch for more than 20 minutes, or (b) the session is `waiting` (ListAgents) or **`blocked` (herdr)** and the newest commit is older than 30 minutes — `blocked` means it is sitting on a prompt and will not move until a human answers in that pane, or (c) an implementer worktree has uncommitted work and no session. Say which.
- **running** — in-progress ticks or live implementer worktrees.
- **idle** — nothing open, nothing in flight (a scoped-not-started stream, a docs-only branch).

## Step 4 — Print

Exactly this shape, nothing narrated around it:

```
NEEDS MORTEN:
  <stream>: <what, in one line, with the tick id>          (or "nothing")
STALLED / UNKNOWN DRIVER:
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
- Nudge, land or message a stream whose row says it is the human's own.

## Corrections from real runs

- 2026-09-20, second run: `ListAgents` does not see herdr panes at all (a resumed session, a
  pane the human opened). `herdr api snapshot` does, by cwd, with a real `blocked` state — it
  found the mainline's orchestrator blocked on a prompt and a second agent in the same
  checkout. Added as the primary session source.
- 2026-09-20, first run: `tk ready` is tracker-wide; a `completion.md` glob matched every
  finished increment; a moving branch with no visible session was reported as a stall when it
  was the human's own resumed session. All three fixed above.
