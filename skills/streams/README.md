# streams

Run several pieces of work on one repository at the same time, each in its own worktree, with
one session that sees them all.

```mermaid
flowchart LR
  H((the human)) -- asks, gos, decisions --> SEAT[seat<br/>main checkout, on the trunk]
  SEAT -- cut: branch, worktree, brief --> S1
  SEAT -- cut --> S2
  SEAT -- cut --> S3
  subgraph streams[streams: one branch in one worktree each]
    S1[search<br/>search-2026-03-02<br/>../app-search]
    S2[billing<br/>billing-2026-03-04<br/>../app-billing]
    S3[docs<br/>docs-2026-03-05<br/>../app-docs]
  end
  subgraph coord["coord/ in the git common dir (never committed)"]
    T[(streams.md<br/>one row per stream)]
    L[(log.md<br/>holds, deploys, hand-offs)]
    C[(schedules.md<br/>what runs on a clock)]
  end
  S1 & S2 & S3 -- coord.py log --> L
  SEAT -- edits rows, reads all --> coord
  S1 & S2 & S3 -- land: merge when done --> TR[trunk]
  SEAT -- merges, runs the checks, pushes --> TR
```

## What it is

- **A stream** is one piece of planned work (a dmtix increment) on its own branch, in its own
  git worktree, driven by its own Claude session. It holds its own share of anything two
  streams may not share, such as a block of ports.
- **The seat** is the one session that sees every stream. It sits in the main checkout, talks to
  you, cuts new streams, reads their state, relays what one stream found that another needs, and
  lands a stream when it is done. It never writes code on a stream's branch.
- **`coord/`** is a folder inside git's common directory (`git rev-parse --git-common-dir`).
  Every worktree of the repository sees the same folder at once, and git never tracks it. It
  holds `streams.md` (the running streams, one row each), `log.md` (one dated line per hold,
  deploy, hand-off or debt), `schedules.md` (everything that runs on a clock, and how to restart
  it) and `asks.md` (what waits on you).
- **The project file** `.devmeta/streams.md` is committed. It holds the facts about your project
  that the skill cannot guess: the trunk, where worktrees go, what a fresh worktree needs, what a
  landing must run.

**Why.** One session doing one increment at a time is slow. Several sessions on one checkout
step on each other: one switches the branch under another, two take the same port, two write the
same file. Streams give each piece of work its own tree and its own resources, and put the facts
they share in files every tree can read. A message dies with its session; a line in `coord/`
does not.

## Start here

1. **Install.** The skill builds on the `dmtix` method and its `ticks` engine, so install all
   three, and the `tk` tracker binary they use (see the [repo README](../../README.md#install)):

   ```bash
   npx skills add mkelk/skills --skill streams --skill dmtix --skill ticks
   ```

2. **`/streams init`**, once, in the main checkout on the trunk. It detects the trunk, the
   package manager and the test runner, asks you two questions (what may two streams not share,
   and where worktrees should go), writes `.devmeta/streams.md` and creates `coord/`.
3. **`/streams status`** whenever you want to know what is running, what waits on you and what
   has stalled. It reads files and processes, never the sessions' own reports.
4. **`/streams cut <name>`** to start a new stream. The name is one short lowercase word, and it
   leads every label the stream carries.

Each stream's own session then runs `/dmtix go`. The seat does not run increments.

## Seven examples

All names, ports and times below are invented.

### 1. A day with three streams: the status screen

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
search    search    idle      ●●◑○    62   E3 of 4 · 3/6   clean                  9m      waits on you (k2v)    web 7000 · host-a
billing   billing   working   ●◔○     38   E2 of 3 · 1/5   2 implementers, 140    2m      a wave running        web 7010
docs      docs      idle      ◑       25   E1 of 1 · 2/4   clean                  1h39m   idle, 2 ticks left    —

HEAVY RUNS  free

HOLDS
  host-a   13:52   until 14:32, 22 min left   billing

OWED
  a3   docs   1h10m   which page layout to keep

SCHEDULES
  seat     hourly pass · :05 each hour
  billing  nightly import test · 02:00
  after the terminal server or Claude stops: /streams restart (each row says how)

LOG  (the newest lines of coord/log.md)
  2026-03-05 13:52 UTC billing: HOLD host-a: schema migration test until 2026-03-05 14:32 UTC
  2026-03-05 13:40 UTC search: READY E3 checkpoint, k2v waits on the human
```

One glyph per epic: `●` done, `◑` half way, `○` not started. `~%` is a rough share of the whole
increment. See [references/status.md](references/status.md).

### 2. A cut, from the ask to the brief

```text
> we need a stream for the docs site rewrite, beside search and billing

> /streams cut docs --scope "#41"

Side stream or mainline? The table has a mainline (search), so: side stream.
Claimed: web 7020 (k=2, lowest free).
Worktree ../app-docs on docs-2026-03-05, from search-2026-03-02 at 4f1c2aa.
At cut: pnpm install --frozen-lockfile ✓  cp .env.example .env ✓  WEB_PORT=7020 ✓
Records: Active line 07s2-ghi, issue #41 claimed, row added to coord/streams.md (read back).
Brief: docs/thoughts/2026-03-05-docs-brief.md, committed.

Stream 07s2-ghi cut. Open a terminal:
  cd ../app-docs
  claude
then: /rename docs
then: /dmtix start with the id 07s2-ghi given by hand
The brief is docs/thoughts/2026-03-05-docs-brief.md; tell the session to read it first.
```

The brief tells the new session where it is, what it holds and what it does not (no deploy host),
who its neighbours are and which files they own, and the project's standing rules. Say *"start
it yourself"* and the seat opens the session through `term.py` instead.
See [references/cut.md](references/cut.md).

### 3. A hold with an end, and its release

Hold only what cannot be shared: a run that **writes** to one shared thing. Every hold has an
end, so a forgotten one shows up instead of blocking the machine for good.

```text
$ coord.py log "HOLD host-a: schema migration test" --for 40m --as billing
2026-03-05 13:52 UTC billing: HOLD host-a: schema migration test until 2026-03-05 14:32 UTC

$ coord.py log "HOLD host-a: quick check"
coord log: A hold needs an end. Add --for 40m (a length) or --until 07:30 (the human's local time).

$ coord.py show --holds
HOLDS
  host-a  by billing since 13:52, until 14:32 (17m left): HOLD host-a: schema migration test …

$ coord.py log "RELEASE host-a" --as billing
2026-03-05 14:21 UTC billing: RELEASE host-a
```

A hold past its end prints under EXPIRED HOLDS and under NEEDS YOU in `status`: release it, or
hold it again with a new end. A debt works the same way: `OWED <stream>: <what>` prints an id
(`a3`), and `PAID a3` closes it. `coord.py` is `python3 <skill dir>/scripts/coord.py`.

### 4. A landing

```text
search: READY at 9be20d1 — E4 closed, completion.md written, k2v closed by the human.

> /streams land search
1  quiet point: no tick in progress, checkout clean, no heavy run (pgrep), worktrees match rows
2  done: project tick open, completion.md present, hand-over read
2b your close first: "ship it" recorded on the branch, before the merge
3  merge search-2026-03-02 into the trunk, in the main checkout
4  seams: diary keep-both in date order; tracker files by tk's merge driver; Active line the trunk's
5  overview's At landing: one registry row added, named in the merge message
6  gate on the merged tree: pnpm test ✓  (one run over the union with billing's last landing)
7  is-ancestor 9be20d1 origin/main ✓; trunk's records say what shipped ✓
8  pushed main 3d70e55; worktree and branch removed; row moved to .devmeta/streams.md as landed
9  close the "search" session now; billing and docs: the trunk moved, sync when it suits you
```

Landing is still a checklist the seat follows by hand: [references/land.md](references/land.md).
The seat merges into the trunk and pushes only the trunk. It never merges into a running
stream's branch; it tells the stream the trunk moved.

### 5. The hourly pass (scout)

`/streams keep-running` runs on a timer, hourly. A small, cheap subagent does the looking, so the
seat's context keeps only a short report. The seat then acts and tells you only what needs you.

```text
SCOUT 15:05 UTC
FOR THE SEAT
- docs: idle 1h50m after "back in 20 min" at 13:15 — evidence: log 13:15, no line since
  — suggest: ask docs what it waits on
- search: "rerun after 14:00" at 13:40, no line since — evidence: log 13:40 — suggest: ask search
FOR THE HUMAN
- search: READY since 13:40, landing waits on your close of k2v — evidence: asks.md q4
QUIET
- billing: working, wave 2 of E2, 2 implementers
```

The seat confirms one fact before acting on each line (a scout is a lead, not a measurement),
messages docs and search, and tells you one line: *"search is ready to land; q4 needs your
close."* See [references/keep-running.md](references/keep-running.md) and
[references/scout.md](references/scout.md).

### 6. The project file

`/streams init` writes the first four sections from what it detected and what you answered. Add
`## Heavy runs` by hand when the project has a run too heavy for two at once.

```markdown
# Streams — this project's facts

## Project

trunk: main
worktree root: ~/trees

## Resources

web: 70k0
schema: app_s<k>
host: one at a time, held with a coord HOLD

## At cut

pnpm install --frozen-lockfile
cp .env.example .env

## At landing

pnpm typecheck
pnpm test

## Heavy runs

- Browser UI tier: `pgrep -f "playwright tes[t]"`; one at a time.
- Recipe: references/recipes/playwright.md (the streams skill).
```

`k` is the stream's number: stream 1 gets web port 7010 and schema `app_s1`. Check what the doors
will read:

```text
$ coord.py config --slug docs
trunk: main  (file: .devmeta/streams.md → ## Project, trunk:)
worktree: ~/trees/app-docs
at_cut:  (file: .devmeta/streams.md → ## At cut)
    pnpm install --frozen-lockfile
    cp .env.example .env
at_landing: pnpm typecheck  (file: .devmeta/streams.md → ## At landing)
resources:
    web: 70k0
    …
```

See [references/init.md](references/init.md). Worked heavy-run rules live in
[references/recipes/](references/recipes/).

### 7. The terminal adapter

The seat finds each stream's session by asking the terminal server, not by remembering a name.
`term.py` is the only file that talks to it. It tries `hc` (the server behind the herdr-app
window) first and herdr as the fallback, so moving sessions from one to the other changes
nothing else.

```text
$ term.py which
hc

$ term.py ls
hc  t1  idle     claude  seat     ~/trees/app
hc  t4  idle     claude  search   ~/trees/app-search
hc  t5  working  claude  billing  ~/trees/app-billing
hc  t7  idle     claude  docs     ~/trees/app-docs

$ term.py read t7 --lines 15        # what the docs session shows
$ term.py send t7 'the trunk moved to 3d70e55; sync when it suits you'
```

The `cwd` column maps a worktree to its session without asking anyone. With `--json`, each
session carries `server`, `id`, `cwd`, `label` and `state`. When neither server answers,
`term.py` exits 2 and the seat falls back to printing what you should open.

## The doors

| You type | It does | Reference |
|---|---|---|
| `/streams init` | writes the project file, creates `coord/` | [init.md](references/init.md) |
| `/streams status` | one screen: running, waiting on you, stalled | [status.md](references/status.md) |
| `/streams keep-running` | the hourly pass: look, then act | [keep-running.md](references/keep-running.md), [scout.md](references/scout.md) |
| `/streams queue` | the list of what waits on you, with what to type | [queue.md](references/queue.md) |
| `/streams cut <name>` | a new stream: branch, worktree, resources, records, brief | [cut.md](references/cut.md) |
| `/streams compact` | keeps long sessions' context small | [compact.md](references/compact.md) |
| `/streams restart` | brings back what ran on a clock after a stop | [restart.md](references/restart.md) |
| `/streams hotfix <name>` | one stream's fix to the trunk, the stream keeps running | [hotfix.md](references/hotfix.md) |
| `/streams land <name>` | a finished stream onto the trunk (a checklist for now) | [land.md](references/land.md) |

Worked recipes for heavy runs: [references/recipes/](references/recipes/). The rules every door
follows, and why each exists: [SKILL.md](SKILL.md).

## Limits

- `coord/` is per machine. Anything another machine must see goes to your issue tracker.
- The seat is a session; it may be asleep. Anything that must happen without it needs a guard
  or a schedule, not the seat's memory.
- Landing is not automatic yet. The seat follows the checklist by hand until two landings
  confirm every step.
