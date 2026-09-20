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
| its session | Two sources, and the second is the better one. (1) `ListAgents`: match the row's session name; gives busy / idle / waiting. (2) **`herdr api snapshot`** (when herdr runs — `~/.config/herdr/herdr.sock` exists): every agent with its `cwd` and `agent_status` (working / idle / **blocked**). Match by cwd = the row's worktree; this catches sessions that never registered with Claude's list (a resumed session, a pane opened by the human) and gives `blocked` as a first-class state, which `ListAgents` only shows as "waiting". **Two agents with the same cwd is a finding in itself** — report it; one checkout, one orchestrator. **Except the seat's own pane:** the orchestrating session is often started in the main checkout and is one of the two; identify it first (`herdr pane read <id>` shows its own prompt) and exclude it. Better still, start the seat in a directory of its own. Needs `tk` ≥ 0.31 for `tk herd`, but the snapshot is `herdr`'s own CLI and needs nothing. |
| its ticks | in the row's worktree: `tk list --status open`. **The tracker is shared across every worktree of one repo, so filter by the stream's own epics** — a tick belongs to the stream if `tk show <id>` names one of its epics as parent. Count in-progress (●) and awaiting-human (◐) that way. **Ready is not `tk ready`** (it has no per-epic scope and counts the whole tracker): derive it from `tk graph <epic> --json` as open tasks whose blockers are all closed. Ignore ◐ ticks from earlier increments that were never closed (they show in every worktree). |
| at checkpoint | **the stream's own** `.devmeta/increments/increment-<its id>/completion.md` exists — never a glob over `increments/*/`, which matches every finished increment in the tree and says yes for everyone. |
| implementer worktrees | `git worktree list` from the row's worktree, rows under `.ticks-worktrees/` whose branch is `tick/<one of its epics>/*`; for each, uncommitted lines (`git status --short | wc -l`) and commits ahead of the stream branch. |
| last movement | age of the stream branch's tip commit; age of the newest commit on any of its tick branches. |
| playwright | `pgrep -f "playwright tes[t]"` — if any, which worktree path it runs in. |
| progress | From the tick files, not `tk graph` (which counts only open tasks): for each of the increment's epics in roadmap order, its children (`parent == epic id`) and how many are closed. The increment's position is **the first epic not closed, out of the epic count** ("E1 of 3"); that epic's `closed/total` is the bar. Epics after it usually have zero children — the method plans just-in-time — so they show as "unplanned", never as 0%. **Never print an increment-wide percentage**: three epics are not equal-sized, and "29% done" for a stream a third through its first epic is a number that gets trusted and is wrong. |

## Step 3 — Classify

Per stream, one word, by these rules in order:

- **checkpoint** — project tick open, `completion.md` present, no in-progress tick → waiting to be landed.
- **needs Morten** — any tick awaiting human, or a human item in the overview not yet answered.
- **unknown driver** — the branch or a tick branch moved recently but no agent in either source has the row's worktree as its cwd. Not a stall: someone is working and the seat cannot see who. Report it first; the human usually knows (a session resumed from a transcript does not register with the others). If the row says the stream is the human's own, this is expected and is not reported.
- **stalled** — no in-progress tick, no implementer process, AND either (a) open ready ticks exist with no dispatch for more than 20 minutes, or (b) the session is `waiting` (ListAgents) or **`blocked` (herdr)** and the newest commit is older than 30 minutes — `blocked` means it is sitting on a prompt and will not move until a human answers in that pane, or (c) an implementer worktree has uncommitted work and no session. Say which.
- **running** — in-progress ticks or live implementer worktrees.
- **idle** — nothing open, nothing in flight (a scoped-not-started stream, a docs-only branch).

## Step 4 — Print

Exactly this shape. Column headers always; columns aligned; a `—` where a column does not
apply; nothing narrated between the header and the table. Prose, if any, goes **after**, and
only when something needs saying beyond what the table shows.

```
STREAMS · <date> <time>

NEEDS YOU
  <tick>   <stream>   <what to do, where, and what closes it>   (or "  —")

STALLED / UNKNOWN DRIVER
  <stream>   <which rule fired, with the number>            (or "  —")

STREAM      INCREMENT                  SESSION            STATE      WORK IN FLIGHT              LAST    PORTS       HOST
<name>      <id + title>               <session or "Morten's own">   <working|idle|blocked|—>   <n implementers, m lines uncommitted | clean | docs only>   <age of newest commit>   <block>   <host or —>
…

PROGRESS
<stream>    <one glyph per epic>   E<n> of <N> · <closed>/<total> ticks   <one clause: "E1 done; E2 wave 1 running">
…

PLAYWRIGHT  free | held by <worktree>
```

PROGRESS shows the whole increment's shape and the current epic's depth in one line, without
pretending unequal epics are equal. **One glyph per epic, in roadmap order:** `●` closed;
the current epic by its tick fraction — `○` none closed, `◔` under a quarter, `◑` under
half, `◕` under all, `●` when its last tick closes; `○` for every epic after it (unplanned
is normal: the method plans just-in-time). Then "E*n* of *N* · closed/total ticks" for the
numbers, then one clause on what is happening now. Never a single increment-wide
percentage: three epics are not equal-sized, and "ticks closed over ticks that exist" reads
100% the moment E1 closes with two epics still to come.

Rules for the table: the mainline first, then side streams in port order, then any docs-only
branch. STATE comes from herdr (working / idle / blocked) or `ListAgents`; `—` for a
hand-driven stream. WORK IN FLIGHT counts *live* implementer worktrees (touched within
30 min) and the lines uncommitted across them; "clean" when live worktrees exist with
nothing uncommitted; "docs only" for a branch with no ticks. LAST is the age of the newest
commit on the stream branch or any of its tick branches, whichever is newer. NEEDS YOU
leads with the tick id so the human can act on it without reading further — and the rest of
the line is **an instruction, not the tick's title**. Build it from `tk show <id>`: the
description says where to look (a route, a file, a screenshot) and the acceptance says what
closes it (his approval quoted in the close reason; a decision written into an overview; a
value put on a host). Three parts, in this order, in plain words:

    <tick>   <stream>   DO <the act> · WHERE <session or path> · CLOSES WHEN <the acceptance>

    txj   inspiration   DO read the seed card's five parts and approve or reword them
                        · WHERE the inspiration session, or the PNGs under
                          apps/web/tests/ui/__screenshots__/inspiration-seed.spec.ts/
                        · CLOSES WHEN your words are in the close reason (--from human)

Wrap to three indented lines if it does not fit one. If the tick's description does not
say where or what closes it, say so — "(tick gives no location)" — rather than guessing;
that is a defect in the tick, and naming it gets it fixed.

## What this door never does

- Message a session. A stall is reported to the human; nudging is the seat's judgement.
- Edit `streams.md`. If the table is wrong (a row for a landed stream, a missing row), say so
  and let the seat fix it with the update-ref procedure.
- Nudge, land or message a stream whose row says it is the human's own.

## Corrections from real runs

- 2026-09-20, fourth run: the "two agents in the main checkout" finding was the seat itself,
  reported three times before `herdr pane read` identified it. Excluded above. Also: count
  implementer worktrees as *live* (touched within 30 min), not as existing — stale tick
  branches from earlier waves overstate the number.
- 2026-09-20, second run: `ListAgents` does not see herdr panes at all (a resumed session, a
  pane the human opened). `herdr api snapshot` does, by cwd, with a real `blocked` state — it
  found the mainline's orchestrator blocked on a prompt and a second agent in the same
  checkout. Added as the primary session source.
- 2026-09-20, first run: `tk ready` is tracker-wide; a `completion.md` glob matched every
  finished increment; a moving branch with no visible session was reported as a stall when it
  was the human's own resumed session. All three fixed above.
