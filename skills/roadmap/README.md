# roadmap

A plan above the increments, for work that several streams build together. It keeps the plan in
one place, shows where every piece really is, and records what you decided.

## Overview

A roadmap is made of **increments**, an increment of **epics**, an epic of **ticks**. A
[stream](https://github.com/mkelk/skills/tree/master/skills/streams) is where an increment runs.
One roadmap usually has several streams, and no single stream can see the others' tickets.

The roadmap adds only what tickets cannot hold: **the links between streams** ("this piece needs
that piece in another stream"). It creates no tickets of its own. How far a piece has come is
always read from that stream's own ticks, so nothing goes stale.

The seat writes it; a stream never does. A stream sends the seat its news, its decision or its
change, and the seat records it.

**When not to use it.** For one increment, use [dmtix](https://github.com/mkelk/skills/tree/master/skills/dmtix).
For the table of running streams, use [streams](https://github.com/mkelk/skills/tree/master/skills/streams).
It is for the seat only, and it needs the streams skill's `coord/` folder.

## Commands

| You type | It does |
|---|---|
| `/roadmap new <name>` | starts a roadmap: the live file, and a folder in git with the plan and a `status.md` |
| `/roadmap status <name>` | one answer: what is running and how far, what is blocked and on what, what waits on you |
| `/roadmap update <name>` | writes a stream's news into the live file (a wave started, an epic closed, a new tick id) |
| `/roadmap decide <name>` | records your decision in git, with your words and the date, and tells the streams it touches |
| `/roadmap review <name>` | the checkpoint look: what is done, what drifted and why, what to change, with a recommendation |

The usual order: `new` once, `update` as streams report, `status` whenever you ask where it
stands, `review` at a checkpoint, and `decide` after each decision.

## What it asks, and when it stops

- **It asks only where the plan needs your word:** `new` asks for the name and the pieces; `decide`
  asks for your decision in your own words (it records them with the date); `review` ends with a
  recommendation and waits for your answer. Everything else it reads and shows.
- **It stops after each command.** There is no run: `status` and `review` only look, `update` writes
  one row, `decide` writes one decision. It never starts, merges or changes a stream.
- A name it does not know, or a stream that has not reported, is shown as "unknown", not guessed.

## Where things live

| What | Where | Committed? |
|---|---|---|
| Live state: the pieces, their ticks, your tasks | `coord/roadmaps/<name>.md` in git's common directory | no |
| The plan of record | the roadmap's folder in git, e.g. `docs/plans/<name>/` | yes, on the trunk |
| Decisions and changes to the plan | `status.md` in that folder | yes, on the trunk |
| What waits on you | a row in `coord/asks.md` | no |

## Good to know

- **Live state is per machine**, like all of `coord/`. If another machine must read it, use an
  issue in your tracker or the folder's `status.md`.
- **A decision moves the trunk, not the streams.** The seat commits it on the trunk and tells the
  streams "sync when it suits you". It never merges into a stream's branch.
- **A budget line repeats your approvals. It never grants one.**
- **Adapt it locally.** The skill is generic; the live file and the plan folder are your project's own, and updating the skill never overwrites them.

## Set up

```bash
npx skills add mkelk/skills --skill roadmap --skill streams -g -a claude-code
```

Run `/streams init` first (it creates `coord/`), then `/roadmap new <name>`.

## How it works inside

This page is for people. The exact steps of each door and the format of the live file are written
for Claude in the skill's own file: [`SKILL.md`](SKILL.md).
