---
name: roadmap
description: The seat's roadmaps — a plan above the increments that several streams build together. "status <name>" shows every piece's real state from its stream's ticks and what waits on what; "update <name>" writes a stream's news into the live file; "decide <name>" records the human's decision in git; "review <name>" is the checkpoint look with the human; "new <name>" starts a roadmap. Use when the human or a stream asks where a roadmap stands, sends a roadmap change, or decides something about one. Seat only, beside the streams skill; not for running an increment (dmtix) or for the streams table (streams).
---

# roadmap — a plan above the increments, kept by the seat

The words: a **roadmap** is made of **increments**, an increment of **epics**, an epic of
**ticks**. A **stream** is where an increment runs: its branch, worktree, ports and session (the
`streams` skill). One stream can run several increments in a row, and one roadmap usually has
several streams.

A roadmap is governed the way streams are — *keep plans and overall governance out of the
worktrees* — and this skill never changes the streams setup. It needs the `streams` skill's seat
and its `coord/` directory (`<git common dir>/coord/`, shared by every worktree, never committed;
`streams`' `scripts/coord.py init` creates it).

| What | Home | Who writes |
|---|---|---|
| **Live state**: the pieces and their ticks, where each piece is, the human's tasks, the budget if it spends | `<git common dir>/coord/roadmaps/<name>.md`, edited in place, never committed | the seat only |
| **The plan of record** | the roadmap's folder in git (e.g. `docs/plans/<name>/`: a `README.md` and whatever else the plan needs) | the seat only, on `master` |
| **Decisions and changes to the plan**, dated, with the human's words | the folder's `status.md` in git | the seat only, on `master` |
| What waits on the human | a row in `coord/asks.md` (the `streams` skill's `queue` door), named in the live file's *The human's tasks* | the seat |

A stream never edits any of these. It sends the seat its news, its decision or its change, and the
seat writes it.

## How it uses ticks: it reads them and owns none

- Every piece of a roadmap points at **one tick in its own stream**: a project (an increment) or an
  epic. The roadmap creates no tickets of its own, so nothing in it can go stale against the
  tracker.
- Inside an increment, tickets already hold order, blocked-by and open/closed. **They cannot see
  across streams**, because each stream's tickets live on its own branch.
- So the roadmap adds only what tickets cannot hold: **the links between streams** ("the record
  stream's E4 needs the sources stream's D1" is `| … | 4my | 6be |` in the Needs column). Whether D1
  is done is read from that stream's own tickets, never written down.
- A piece with no stream yet has Stream `—` and Tick `—` ("not cut"). When it is cut, its stream
  sends the tick id and the seat fills the row.

The table sits between markers, so a door — or a project command — can find it:

```markdown
<!-- roadmap:status <name> -->
| Piece | Stream | Tick | Needs |
|---|---|---|---|
| record · E4 setting up from a list | record | 4my | 6be |
| sources · D4 figures and streaming | — | — | 6be |
<!-- /roadmap:status <name> -->
```

Stream is the name in `coord/streams.md` (it gives the worktree, so the tick resolves in that
worktree's `.tick/`); Needs is tk ids separated by commas, or `—`.

## Doors

Dispatch on the argument. With none, or an unknown one, show this list and ask.

### `status <name>`

1. For each row of the table: find the stream's worktree in `coord/streams.md`, then in that
   worktree run `tk show <tick> --json` for the piece's status and `tk list --parent <tick> --json`
   for its children's. For each Needs id, the same `tk show` in whichever stream owns it. If the
   project's instruction file names a command that prints this, use it; this procedure is the
   definition it must match.
2. Answer in this order: what is running and how far along (children done of total), what is
   blocked and on what (a Needs tick still open), what waits on the human (*The human's tasks*),
   the budget line if there is one. Say times in the human's local time.
3. A row whose tick does not resolve (a typo, a closed project, a removed worktree) is a fault in the
   live file: fix it before answering, or say it.

### `update <name>`

When a stream reports (a wave dispatched, an epic closed, a tick id for a newly cut piece, a figure
spent):
1. Copy the live file to the scratchpad first.
2. Edit the one row by exact match (never by line number), in *The pieces and their ticks* (a tick
   id or a Needs link) or in *Where each piece is* (the news and what is next). Overwrite; the
   history goes to git only when it is a decision or a change to the plan.
3. Read the row back.
4. A change to the plan itself (scope, order, a piece added or dropped) is also a `decide`.

### `decide <name>`

When the human decides something, or a stream's decision changes the plan:
1. On `master`, append to `status.md` → *Decisions* (dated, the human's words quoted) and, when the
   plan changes, a row under *Changes to the plan* (date, change, why, where). Edit the plan of
   record where it says otherwise.
2. An entry in the project's narrative history when it changes direction, if the project keeps
   one (with dmtix: `.devmeta/project-history.md`).
3. Commit on `master` with named paths, push, and tell the streams it touches: *master has
   moved, sync when it suits you*. Never merge into a stream's branch.

### `review <name>`

At an epic's close-out, an increment's landing, or a checkpoint the plan names: run `status`, then
bring the human one framed answer — what is done, what drifted from the plan and why, what to
change, with a recommendation. Record what they decide with `decide`.

### `new <name>`

1. The human names it. Create `coord/roadmaps/<name>.md` with a header (what it is, that the seat
   keeps it, where the plan of record is), *The pieces and their ticks* between
   `<!-- roadmap:status <name> -->` markers, *Where each piece is*, *The human's tasks*, and a
   budget section if it spends.
2. Create its folder in git with the plan of record and a `status.md` holding only *Decisions* and
   *Changes to the plan*; commit on `master`.
3. Tell each stream it names that the roadmap exists and that their news goes to the seat.

## Rules

- **Live state is per machine**, like everything in `coord/`. A roadmap that must be read on
  another machine gets an issue in the project's tracker or the folder's `status.md`; the live file
  never moves into git.
- Never write the live file from a stream, and never let a stream edit the roadmap's folder on its
  branch. Both are the seat's.
- Verify a write by reading it back; a print after an edit is not a check.
- The budget section repeats the approvals the human gave; it never grants one. Paid runs stay
  capped at their approval, and every paid call counts toward it.
