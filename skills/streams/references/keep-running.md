## Purpose

Run on a timer. Do `status`, then **act on what it found** and **say only what the human needs
to hear**. The other doors answer a question when asked; this one notices what nobody asked
about.

Its value is not the screen — `status` already prints that. It is that **things go stale while
nobody is looking**, and on 2026-09-21 every one of the failures below happened to a seat that
was paying attention.

## Step 1 — Run the status door

`references/status.md`, whole. Do not shortcut it because this is a routine pass; a routine
pass is exactly when a seat reads a cached answer and calls it a measurement.

## Step 2 — Push forward. This is the half that is not `status`.

For each, act rather than report:

- **A stream waiting on the seat.** The worst one and the easiest to miss: a stream that is
  correctly holding says nothing, so it falls out of a seat's working set. On 2026-09-21 one
  sat idle **29 minutes** waiting for a window close the seat never sent — because the seat
  tracked *who had spoken lately* instead of *who was holding*. **Keep an explicit list of
  every stream owed an answer, and check it here, by name, every pass.** Silence from a stream
  is not absence of need.
- **Windows.** Is a hold still in force with nothing writing? Close it, tell everyone who was
  asked to hold — not only whoever spoke last.
- **Stale table cells.** `status` reads epics from each stream's own Roadmap line, so a
  mismatch with `.devmeta/streams.md` is visible here and nowhere else. Refresh session,
  epics and status cells when they have drifted. They drift within the hour, repeatedly.
- **Finished and unlanded.** A stream at its checkpoint holds a worktree, a port block and a
  session, and usually something another stream wants. `land.md`: *land as soon as it can be
  landed.*
- **Stalled streams.** Restart per `status.md` Step 4 — message the session, name the rule
  that fired, ask rather than instruct. Never nudge a stream that is waiting on the human, and
  never one the human drives.
- **Orphans.** Any process whose `cwd` is `(deleted)` belongs to a worktree that no longer
  exists and **nothing on the machine knows it is there**. One set survived eight days, an
  increment, five streams landing and a repository rename. Report them; kill only on the
  human's word, by PID, root first.
- **Relays owed.** Did a stream find something another must act on and the seat has not passed
  it? That is the seat's whole job and it is the thing that silently does not happen.

## Step 3 — Always print the table

**The full status table goes out every pass, without exception** — every stream, every column,
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

**A NEEDS YOU item is only an item if the human can act on it now.** A registered decision
whose default is already running and doing no harm is not urgent — say it once, then let the
tick carry it, and do not re-raise it every half hour. **A recurring report that repeats the
same three items becomes wallpaper, and the pass where one of them changes is the pass nobody
reads.** If an item has not moved in several passes, either it does not need them or the way it
is being asked is wrong; say which.

## Step 4 — Schedule the next pass, and know when to stop

Thirty minutes is the default. Go sooner when something is mid-flight the seat must see the end
of; go quiet when every stream is deep in a wave and nothing is owed.

**Stop when there is nothing to keep running.** No streams, or every stream finished and
landed: say so and end the loop rather than waking every half hour to print an empty table.

## What this door never does

- **Dispatch a tick, or do a stream's work.** It restarts stopped work by asking its session;
  it never reaches into a tree.
- **Decide anything the human should.** It surfaces decisions; it does not resolve them.
- **Nag.** A stream that is working does not need a wellness check, and a human who has already
  seen an item does not need it again in thirty minutes.

## Corrections from real runs

- 2026-09-21, the run that produced this door: the seat asked four streams to hold, opened a
  window, then narrowed it — and told only the three that had spoken since. The fourth held
  silently for 29 minutes. **The list of who is owed an answer has to be written down, because
  the streams that behave best are the ones that vanish from a seat's attention.**
