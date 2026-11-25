# streams

Run several pieces of work on one repository at the same time, each in its own worktree, with
one session that sees them all.

## Overview

One session doing one increment at a time is slow. Several sessions on one checkout step on each
other. **streams** gives each piece of work its own branch, worktree and resources, and keeps
the facts they share in files every worktree can read. One session, the **seat**, sees them all:
it cuts streams, reads their state, tells you what waits on you, and lands a finished stream.

**When not to use it.** For one piece of work at a time, use [dmtix](https://github.com/mkelk/skills/tree/master/skills/dmtix) alone. The sessions that run a stream do
not use this skill; they run `/dmtix go`. It is not for a plan above several increments (use the [roadmap](https://github.com/mkelk/skills/tree/master/skills/roadmap) skill) or for a
research program (use the [research-loop](https://github.com/mkelk/skills/tree/master/skills/research-loop) skill).

## Commands

| You type | It does | Reference |
|---|---|---|
| `/streams init` | writes the project file, creates `coord/` | [init.md](references/init.md) |
| `/streams status` | one screen: running, waiting on you, stalled | [status.md](references/status.md) |
| `/streams keep-running` | the hourly pass: look, then act | [keep-running.md](references/keep-running.md), [scout.md](references/scout.md) |
| `/streams queue` | the list of what waits on you, with what to type | [queue.md](references/queue.md) |
| `/streams explain` | says what is set up here and why; writes nothing | [init.md](references/init.md) (step 6) |
| `/streams cut <name> [--scope …]` | a new stream: branch, worktree, resources, records, brief | [cut.md](references/cut.md) |
| `/streams compact` | keeps long sessions' context small | [compact.md](references/compact.md) |
| `/streams restart` | brings back what ran on a clock after a stop | [restart.md](references/restart.md) |
| `/streams hotfix <name>` | one stream's fix to the trunk, the stream keeps running | [hotfix.md](references/hotfix.md) |
| `/streams land <name>` | a finished stream onto the trunk (a checklist for now) | [land.md](references/land.md) |

The usual order: `init` once, then `status` and `queue` as you work, `cut` for each new stream, `land` when one is finished. `keep-running`, `compact` and `restart` run by the clock or after a stop.

## The picture

![streams: you, the seat, the streams, and the files they share](streams.svg)

*Flow on top (you, the seat, the streams, the trunk); files below.*

You ask and decide; the seat cuts streams and reads them all. Each stream is one branch in one
worktree with its own session, running its own increment (or, for a research stream, its own program). A finished stream is merged into the
trunk by the seat. The files below the flow are the project file (committed), `coord/` (shared
by every worktree, never committed) and what a cut writes into the new worktree.

## An example: the status screen

This is what `/streams status` prints (names, ports and times are invented):

```text
> /streams status

STREAMS · 2026-03-05 14:10

NEEDS YOU
  k2v   search   DO approve or reword the empty-result message
                 · WHERE ../app-search/docs/ui/empty-state.png
                 · CLOSES WHEN your words are in the close reason

STALLED / UNKNOWN DRIVER
  docs   idle 95 min, 2 ticks left, no commit since 12:31

STREAM    SESSION   STATE     EPICS   ~%   AT              IN FLIGHT              LAST    WHAT NOW              RESOURCES
search    search    idle      ●●◑○    62   E3 of 4 · 3/6   clean                  9m      waits on you (k2v)    api 8000 · staging
billing   billing   working   ●◔○     38   E2 of 3 · 1/5   2 implementers, 140    2m      a wave running        api 8010
docs      docs      idle      ◑       25   E1 of 1 · 2/4   clean                  1h39m   idle, 2 ticks left    —

HEAVY RUNS  free

HOLDS
  staging  13:52   until 14:32, 22 min left   billing

OWED
  a3   docs   1h10m   which page layout to keep

SCHEDULES
  seat     hourly pass · :05 each hour
  billing  nightly import test · 02:00
  after the terminal server or Claude stops: /streams restart (each row says how)

LOG  (the newest lines of coord/log.md)
  2026-03-05 13:52 UTC billing: HOLD staging: schema migration test until 2026-03-05 14:32 UTC
  2026-03-05 13:40 UTC search: READY E3 checkpoint, k2v waits on the human
```

One glyph per epic: `●` done, `◑` half way, `○` not started. `~%` is a rough share of the whole
increment. See [references/status.md](references/status.md).

## What the words mean

- **The trunk** is the branch every stream lands on, usually `main`.
- **A stream** is one piece of planned work (a dmtix increment) on its own branch, in its own
  git worktree, driven by its own Claude session. It holds its own share of anything two
  streams may not share, such as a block of ports.
- **The seat** is the one session that sees every stream. It sits in the main checkout, talks to
  you, cuts streams, reads their state, and lands a stream when it is done. It never writes code
  on a stream's branch.
- **`coord/`** is a folder inside git's common directory. Every worktree sees it; git never
  tracks it. It holds the table of running streams, a log, what runs on a clock, and what waits on you.
- **The project file** `.devmeta/streams.md` is committed. It holds the facts the skill cannot
  guess: the trunk, where worktrees go, what a fresh worktree needs, what a landing must run.

## Set up

```bash
npx skills add mkelk/skills --skill streams --skill dmtix --skill ticks -g -a claude-code
```

(and the `tk` binary; see the [repo README](https://github.com/mkelk/skills#install)). Then:

1. `/streams init`, once, in the main checkout on the trunk. It asks two questions (what may two
   streams not share, and where worktrees should go) and writes the project file.
2. `/streams status` whenever you want to know what is running and what waits on you.
3. `/streams cut <name>` to start a stream. The name is one short lowercase word. Its own
   session then runs `/dmtix go`; the seat does not run increments.

## Good to know

- **A cut makes a stream.** It asks nothing in the normal case. It asks one yes-or-no
  question only when the project deploys somewhere and no main line of work exists yet.
- **Claude Code 2.1.331 or later.** Version 2.1.325 did not report its status to herdr. The seat
  then typed its text into a trust question.
- **A trust question.** A session in a folder Claude Code does not trust yet stops at its trust
  question. You answer it in that pane, never the seat.
- **The seat only pushes the trunk**, and never merges into a running stream's branch.
- **Landing is by hand for now.** The seat follows a checklist until two landings confirm every step.
- **`coord/` is per machine.** Anything another machine must see goes to your tracker. The seat is a
  session and may be asleep: anything that must happen without it needs a guard or a schedule.
- **Adapt it locally.** The skill is generic. `.devmeta/streams.md` and the `coord/` files are
  the project's own. Updating the skill never overwrites them.

## How it works inside

This page is for people. The rules behind every door, the project-file format, the terminal
adapter and heavy-run recipes are written for Claude in the skill's own files:
[`SKILL.md`](SKILL.md) and [`references/`](references/).
