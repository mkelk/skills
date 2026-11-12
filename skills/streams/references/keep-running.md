## Purpose

Run on a timer. Do `status`, then **act on what it found** and **say only what the human needs
to hear**. The other doors answer a question when asked; this one notices what nobody asked
about.

Its value is not the screen — `status` already prints that. It is that **things go stale while
nobody is looking**, and on 2026-09-21 every one of the failures below happened to a seat that
was paying attention.

**The seat is the human's representative for keeping things moving** (the human, 2026-11-01:
they "very often" asked the seat to look for stuck work, and it nearly always found some). So
the default on every pass is to **go looking for work that should be moving and isn't, and move
it** — not to wait to be asked, and not to report it and stop. Step 2's *Stuck hunt* is the
list; run all of it every pass.

## Step 1 — Run the status door

**On the timer (since 2026-11-06, hourly):** the looking in Steps 1 and 2 is done by a scout
subagent on the cheapest model the harness offers, so the seat's context keeps only its report:
follow `references/scout.md`, then act here from Step 2. Run the door yourself only when the
human asks for a pass, or when the scout's report cannot be trusted (it failed, or contradicts
itself).

`references/status.md`, whole. Do not shortcut it because this is a routine pass; a routine
pass is exactly when a seat reads a cached answer and calls it a measurement.

## Step 2 — Push forward. This is the half that is not `status`.

For each, act rather than report:

- **A stream waiting on the seat.** The worst one and the easiest to miss: a stream that is
  correctly holding says nothing, so it falls out of a seat's working set. On 2026-09-21 one
  sat idle **29 minutes** waiting for a window close the seat never sent — because the seat
  tracked *who had spoken lately* instead of *who was holding*. **The list is the open `OWED`
  lines in `coord/log.md`; read them here (`coord.py show --owed`), by name, every pass, instead
  of remembering.** Write a line when you take on a debt: `python3 <skill dir>/scripts/coord.py
  log "OWED <stream>: <what>" --as seat` (it prints the id, e.g. `a7`), and close it when paid:
  `coord.py log "PAID a7" --as seat`. Silence from a stream is not absence of need.
- **The queue** (`references/queue.md`). Read `coord/asks.md`: move a row the human answered in
  the seat to **Done** with their words; close rows that no longer wait on anything; add a row
  for anything waiting on the human that has none (a stream's checkpoint, a go the seat asked
  for); move a **Later** row whose time has come to **Now**.
- **Schedules.** Read `coord/schedules.md`. A row whose owner is no longer running, or whose
  script is not in the process list, is missing: follow `references/restart.md`. A row whose
  owner has closed or whose end has passed: strike it. A schedule a stream mentions in the log
  that has no row: add it, or ask the stream to.
- **Windows.** Is a hold still in force with nothing writing? `coord.py show --holds` lists the
  open holds with when each began and the time left, and the ones past their end. Close it
  (`coord.py log "RELEASE <what>" --as seat`), or let its holder hold again with a new end. Tell
  everyone who was asked to hold, not only whoever spoke last. A hold written without an end is
  not listed; if a window seems open with nothing under the holds, read the newest log lines
  (`coord.py show --log 30`).
- **Compaction.** At the quiet times `references/compact.md` names, the pass may run the idle
  tidy that door describes (the dry run first); never on the seat.
- **Stale table cells.** `status` reads epics from each stream's own Roadmap line, so a
  mismatch with `coord/streams.md` is visible here and nowhere else. Refresh session,
  epics and status cells when they have drifted. They drift within the hour, repeatedly.
- **Finished and unlanded.** A stream at its checkpoint holds a worktree, a port block and a
  session, and usually something another stream wants. `land.md`: *land as soon as it can be
  landed.*
- **Stalled streams.** Restart per `status.md` Step 4 — message the session, name the rule
  that fired, ask rather than instruct. Never nudge a stream that is waiting on the human, and
  never one the human drives.
- **Stuck hunt.** Each of these was found on 2026-11-01 only because the human asked. Look for
  every one, every pass, and act the same pass:
  - **A self-matching wait**: a `while pgrep -f "<pattern>"` loop that matches its own command
    line and never ends. Find them in the process list (a shell whose command line holds
    `pgrep -f` and the pattern it waits on). One stream sat 4 h in one, and another stream sat
    behind it. Message the owner at once with the pid and the fix (`pgrep -f "[x]yz"`, or wait
    on a pid). The seat cannot stop another session's process (auto mode refuses it), so if the
    owner does not answer, ask the human for `! kill <pid>`.
  - **What the wait was for.** Read the end of the job's log. A job that failed hours ago behind
    a wait nobody saw end is the usual find (on 2026-11-01 a stream's queued job had failed
    before doing any work, and nobody knew). Tell the owner what failed.
  - **Idle with a ready tick and nothing in flight**, quiet for more than about 15 minutes:
    ask, in one line, what the stream is waiting on. If it waits on the seat, answer it now. If
    it waits on another stream, chase that stream, and check that one for the same faults.
  - **A stream waiting on a promise** ("late morning", "after the bench"): when the time has
    passed, ask the stream that promised.
  - **The seat's own background tasks** (a snapshot, a test run): check how long each has run,
    and say so when one passes its usual time.
  - **`OWED` older than a day**: pay it, or put it to the human again as one plain question.
  - **A row with no session for days** (a parked stream): ask the human once whether to close
    it, then don't ask again.
- **Orphans.** Any process whose `cwd` is `(deleted)` belongs to a worktree that no longer
  exists and **nothing on the machine knows it is there**. One set survived eight days, an
  increment, five streams landing and a repository rename. Report them; kill only on the
  human's word, by PID, root first.
- **Relays owed.** Did a stream find something another must act on and the seat has not passed
  it? That is the seat's whole job and it is the thing that silently does not happen.

## Step 3 — Always print the table

**The timer's hourly pass is the exception** (since 2026-11-06): it tells the human only what
needs them, one line if nothing does, and no table unless they ask (`references/scout.md`, the
seat's half). Every pass the human asks for, or the seat runs the door for itself, prints the
table as below.

**Otherwise the full status table goes out every pass, without exception** — every stream, every column,
as `status.md` Step 5 defines them. Not a summary, not the rows that changed, not an
abbreviation because the pass was quiet. It is the thing the human actually reads: a glance
tells them who is moving, who is not, and how the machine is loaded, and that glance only
works if the shape is identical every time. A pass that prints prose and no table has failed,
however good the prose.

**Lead with whether anything needs them**, then the table. Do not narrate the upkeep — that a
cell was refreshed or a window closed is the seat doing its job, not news.

```
STREAMS · <date> <time> · nothing needs you   (or: NEEDS YOU — <n> items)

NEEDS YOU
  <tick>  <stream>  DO … · WHERE … · CLOSES WHEN …          (or "  —")

STREAM  SESSION  STATE  EPICS  ~%  AT  IN FLIGHT  LAST  WHAT NOW  PORTS
<every stream, every column, the same shape every pass>

PLAYWRIGHT  free | held by <worktree>

Pushed forward: <one line, only if something was actually done>
```

**Every column, every pass.** IN FLIGHT and LAST are how a human sees a stream drifting before
it stalls; PORTS is how they know which is which; PLAYWRIGHT is the one line that says whether
the machine is spoken for. Dropping a column because it looked uninteresting this pass is how
the pass where it mattered reads the same as the pass where it did not.

**A NEEDS YOU item is only an item if the human can act on it now — and reachability is the
test, not the flag.** A close-out or checkpoint tick is assigned to the human and flagged
awaiting **from the moment the epic is planned**, so it prints as NEEDS YOU for the whole
epic — hours, sometimes a day — before its preconditions exist. Measured 2026-09-21: a tick
reading *"Close out E2, and the increment checkpoint … STOP for Morten"* surfaced while its
epic sat at 0 of 8 with four implementers running. The flag was honest; the door's reading
was not. **Apply the same parent-chain test as readiness:** a tick whose siblings are
unfinished, or whose epic is unplanned or blocked, is not actionable however it is flagged.
Print it only when the human could actually act, and until then it belongs in the stream's
WHAT NOW, not in his list.

**A NEEDS YOU item is only an item if the human can act on it now.** A registered decision
whose default is already running and doing no harm is not urgent — say it once, then let the
tick carry it, and do not re-raise it every pass. **A recurring report that repeats the
same three items becomes wallpaper, and the pass where one of them changes is the pass nobody
reads.** If an item has not moved in several passes, either it does not need them or the way it
is being asked is wrong; say which.

## Step 4 — Schedule the next pass, and know when to stop

An hour is the timer's default (the human, 2026-11-06; thirty minutes until then). Go sooner when something is mid-flight the seat must see the end
of; go quiet when every stream is deep in a wave and nothing is owed.

**Stop when there is nothing to keep running.** No streams, or every stream finished and
landed: say so and end the loop rather than waking every hour to print an empty table.

## What this door never does

- **Dispatch a tick, or do a stream's work.** It restarts stopped work by asking its session;
  it never reaches into a tree.
- **Decide anything the human should.** It surfaces decisions; it does not resolve them.
- **Nag.** A stream that is working does not need a wellness check, and a human who has already
  seen an item does not need it again on the next pass.

## Corrections from real runs

- 2026-09-21, the run that produced this door: the seat asked four streams to hold, opened a
  window, then narrowed it — and told only the three that had spoken since. The fourth held
  silently for 29 minutes. **The list of who is owed an answer has to be written down, because
  the streams that behave best are the ones that vanish from a seat's attention.**
