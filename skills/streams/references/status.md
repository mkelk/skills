## Purpose

Answer "what is running, is anything waiting for me, has anything stalled" in one screen,
from files and processes, never from memory and never by asking the sessions.

**The steps below are the definition of this door.** They name every section the screen shows
— NEEDS YOU, STALLED / UNKNOWN DRIVER, the stream table, HEAVY RUNS, HOLDS, OWED, SCHEDULES,
LOG — and the file or process each is computed from: `coord/streams.md`, `coord/log.md` (read
through `coord.py show`), `coord/schedules.md` and `coord/asks.md` in git's common directory;
`tk` in each stream's worktree; `git worktree list`; the process list; the project's
`## Heavy runs` (`coord.py config --get heavy-runs`); and the terminal server's sessions
(`term.py ls`) or `ListAgents`.

**A project may ship its own command that prints this screen; if the project's file or
instruction file names one, run it instead of Steps 1–3.** It reads the same sources in about a
second and costs the seat nothing — the seat's context is the expensive thing on the machine.
Read its output, print Step 5's shape, and fall back to the steps below only when it is absent
or refuses a row. **Run the worktree reconciliation yourself even then**: `git worktree list`
against the rows the command printed, every time. A command's empty table is a claim;
`git worktree list` is the measurement. (2026-09-21) a status command answered "nothing is
running" with two streams live and three worktrees on disk.

**Where the command and these steps disagree, these steps are right and the command has a
bug** — say so, and record it where the project records work.

## Step 1 — Read coord first: the table, then the log

**Coord is read first, before anything is done on the machine or a host.** A session that
starts or resumes runs this door (or at least `coord.py show`) before it acts: the facts other
streams depend on — a hold on a host, which build is live, what to wait for — are lines in
`coord/log.md`, not messages.

**The table is `<git common dir>/coord/streams.md`.** Every worktree reads the same file at
once; git never tracks it, so there is no stale copy on a branch. It is **per machine**. The
seat edits it in place.

**If a project has no `coord/streams.md` yet and still keeps the table committed on the trunk,
read it from the ref — `git show "$(coord.py config --get trunk)":<path>` — never from a
checkout's disk, and say on the screen which home was read.** `update-ref` moves a ref without
touching any working tree. (2026-09-21) a door reading a checkout's disk printed "nothing is
running" over two live streams.

Each row gives a stream's increment, session, branch, worktree, resources, host and epics.
**The worktree is the only cell that is a fact; the session and epics cells are caches** the
seat wrote by hand. Step 2 says where each is really read from. If no table can be read, say
so and stop.

**The increment id may be in either the `stream` cell or the `increment` cell.** Match either.
A row that lists epics but carries no id in either cell is refused **by name** — say which row
and what it is missing, and carry on; a docs-only row (no epics, `—`) is exempt.

**Then read the rest of coord**, for the sections after the table (Step 5):

- `coord.py show` — open holds with their time left, holds past their end, the seat's unpaid
  `OWED` lines, the log's newest lines. Read through the script, not by eye: a hold is open only
  until a `RELEASE` line for the same `<what>`, and its end is the `until … UTC` stored last.
- `coord/schedules.md` — its **Dies with its session** section (session crons, `/loop`s,
  background shells waiting for a time). The `restart` door owns the format.
- `coord/asks.md` — its **Now** rows. The `queue` door owns the file.

A coord file that is not there is said on its section's line, never skipped in silence: a
missing `schedules.md` means nobody has listed what runs on a clock, not that nothing does.

### Then read the machine, and reconcile it against the table

Run `git worktree list`, and for every worktree that is neither the main checkout nor a
`.ticks-worktrees/` tick tree, find its row. **A worktree with no row is a stream the seat
cannot see**: every other door reads the table, so a landing or a machine hand-off is decided
as though it did not exist. Print each under its own heading with branch, head, last commit
time and whether anything of its is running, say plainly that it is unlisted, find its seat,
and add the row before doing anything else with the machine. Only a detector that starts from
the machine catches a stream that never went through `cut`. In reverse: a row whose worktree is
gone is a landed stream whose row was never removed. (2026-09-21) an unlisted stream held the
browser for a screenshot regeneration while the seat, reading only the table, released the
machine to another stream.

## Step 2 — Measure each stream, on the thing

For every row, gather — all read-only, all from the machine, none from a message:

| what | how |
|---|---|
| its session | `term.py ls --json` (hc when hc holds sessions, else herdr's snapshot; exits 2 when neither answers; every answer names its `server`): every agent with its `cwd`, `foreground_cwd`, state (working / idle / **blocked**), id and label. `ListAgents` is a second source (busy / idle / waiting) that a CLI cannot call. Rules below. |
| its epics | **From the stream's own `.devmeta/current-increment.md`, not the table's epics cell.** Its `**Roadmap (tk):**` line, written per branch when the stream scopes, reads `project <id> → <epic> (E1 …), …` or `none.`; it is authoritative. Fall back to the table's cell only when the worktree is gone, and say which source was used. (2026-09-21) two streams ran waves for an hour while the table said `— (not scoped)`, and the door printed them as unscoped. |
| its ticks | **In the stream's own worktree, never anywhere else** — the tracker is per branch, and the same command in the main checkout answers plausibly about the mainline. `tk list --status open`, filtered to ticks whose parent is one of the stream's epics. Count in-progress (●) and awaiting-human (◐). **Awaiting counts only ticks not closed**: `tk close` does not clear `awaiting`. **Ready is not `tk ready`** (tracker-wide): derive it from `tk graph <epic> --json` as open tasks whose blockers are all closed, **through the parent chain** — a tick under a blocked or unplanned epic has an empty `blocked_by` and is not ready. Ignore ◐ ticks from earlier increments never closed. (2026-09-21) a tick 55 s reachable read "ready 35 min" because its own `blocked_by` was empty. |
| at checkpoint | **the stream's own** `.devmeta/increments/increment-<its id>/completion.md` exists — never a glob over `increments/*/`. |
| implementer worktrees | `git worktree list` from the row's worktree: rows under `.ticks-worktrees/` on `tick/<one of its epics>/*`; for each, uncommitted lines (`git status --short | wc -l`) and commits ahead. Count only *live* ones (touched within 30 min). |
| last movement | age of the stream branch's tip; age of the newest commit on any of its tick branches. |
| heavy runs | The project's `## Heavy runs` names how to see one (a `pgrep` pattern, a container name) and its rules; absent, print `HEAVY RUNS  — (the project names none)`. Then **check each match is a runner, not a watcher**: read `/proc/<pid>/cmdline` and discard shells (`bash -c`, a wait-loop whose own command line contains the pattern). A bracket in the pattern (`tes[t]`) stops it matching its own `pgrep`, not other processes. **A stream's tick worktrees count as that stream's.** A running cwd no row claims prints `held by <cwd>`; never print "free" while a process runs. A run inside a container shows an unreadable `cwd`: ask the container runtime (`docker ps`) and print `held by <container>`. **Refuse to act on a process you cannot attribute** — unreadable is not permissive. (2026-09-21) two wait-loops matching their own pattern read as a running tier and held three streams off for nothing — wait on a PID, not a name. |
| progress | From the tick files, not `tk graph` (open only): for each epic in roadmap order, its children and how many are closed. Position is **the first epic not closed, out of the epic count** ("E1 of 3"); that epic's `closed/total` is the bar. Later epics with no children show "unplanned", never 0%; a current epic with none is unplanned too, not "0/0". An increment whose every epic tick is closed reads 100%. |

**Session rules.** **Match by worktree: `cwd` as a prefix, and `foreground_cwd` too.** The
snapshot carries no session name; its label is the terminal title, which coincides with the
session name often enough to fool a reader and drifts the moment anything else sets a title. A
driver that dispatches into other trees sits in its own known worktree, so it is attributed by
the tree it sits in; an agent under **no** row's worktree gets **its own line** ("agent in no
stream's tree", with its cwd). One row per agent at most.
- **Store the session id**, not just the name (`.value` of herdr's `agent_session`, which is an
  object — comparing the object matches nothing, forever, without erroring). A changed id on an
  unchanged worktree is a finding: the pane was replaced. Until a row carries one, print the name
  as recorded, never as verified.
- **Unreachable is not absent.** When the terminal server's answer fails, mark sessions
  unseen; the classifier reads that as *unknown*, not *nobody*.
- **Two agents with the same cwd is the loudest finding this door has** — one checkout, one
  orchestrator. **Except the seat's own pane: the caller says who it is; the door does not
  guess.** A project command takes `--self <cwd or pane id>` (falling back to the server's pane
  id variable); `--self <cwd>` takes an agent exactly there first, then one inside it, never one
  above it. The caller is dropped from the snapshot **once, before any check runs**, so neither
  the duplicate rule nor the "no stream's tree" line sees it. Excluding it must not swallow a
  real finding (two *other* agents in one checkout still report), and the caller is never read
  as a row's session: if no other agent shares that cwd, the row prints `—` in both columns and
  the unknown-driver rule is skipped for it. Better still, start the seat in a directory of its
  own. (2026-09-24) a matcher taking either direction removed an agent in the home directory in
  the seat's place.
- **On a cwd match, print what the machine knows — the id and the label — never `—`.** `—` in
  the session column means *nobody is there*, never *somebody the table has not named*.

## Step 3 — Classify

Per stream, one word, by these rules in order:

- **checkpoint** — project tick open at `awaiting: checkpoint`, the stream's own
  `completion.md` present, no in-progress tick → waiting to be landed. **A NEEDS YOU item before
  and after the landing**: the close is the human's (review, smoke-test, close reason), and it
  clears when the project tick closes, not when the stream lands. The flag alone is not the
  fact: it is written at scoping, so for a reachable worktree with no `completion.md` print
  nothing. A worktree that is *gone* keeps the line on the flag alone. (2026-09-23) the flag
  alone printed "review the completion report" for a stream with no report.
- **needs you** — any tick awaiting human, or a human item in the overview not yet answered.
- **unknown driver** — the branch or a tick branch moved **within the last 30 minutes** and no
  agent is found at the row's worktree (nor its recorded session anywhere). Not a stall: someone
  is working and the seat cannot see who. **Never for a stream nobody has opened yet**: exempt a
  row whose status reads `cut, not started`, or whose branch's commits are all the seat's own
  cut. Report it first; the human usually knows. A row the human drives is not reported.
- **stalled** — no in-progress tick, no implementer process, AND one of:
  - **(a)** open ready ticks with no dispatch for more than 20 minutes — **unless the stream's
    own pane footer shows a running shell** (`term.py read <session>`: the lines below the
    input box's last rule, or the last non-empty line with no box; text quoted above the box is
    not the footer). A running shell holds (a) off for the row, **for an hour at most**; past
    it, print `check: a shell is running but nothing has dispatched for <n> min`. When no pane
    could be read at all, still fire, worded as a check ("pane unreadable, check rather than
    assume stalled"). (2026-09-23) a stream waiting on its own long test tier read as stalled
    while its pane's state said `done`, which means the turn ended, not that nothing runs.
  - **(b)** the session is `waiting` or **`blocked`** and the newest commit is older than 30
    minutes — `blocked` sits on a prompt until a human answers in that pane.
  - **(c)** an implementer worktree has uncommitted work and **the stream's own session** is
    absent from both sources (implementers are not panes; reading it the other way makes every
    live wave look stalled). Off for the caller's row and a row the human drives.
  - **(d)** a tick whose branch is already merged into the stream branch is still open, with
    nothing in progress — the tree is green so (a) and (b) stay silent. Check: is
    `tick/<epic>/<id>` an ancestor of the stream branch? After any red gate, re-read the graph
    rather than memory: in-progress ticks merged and gated get orphaned there too.

  Say which rule fired.
- **running** — in-progress ticks or live implementer worktrees.
- **idle** — nothing open, nothing in flight (scoped-not-started, a docs-only branch).

**`idle` with undispatched work is the stall signature.** `working` has a run continuing;
`idle` has ended a turn, so `idle` + an unfinished epic + nothing dispatched means the turn
ended without starting the next thing. *The report reads like the end of the work* is the
tell: an epic boundary is a waypoint. When it recurs, ask for an order change —
**dispatch first, report second** — not a reassurance. (2026-09-21) a stream said "final review
next", ended its turn, and sat 31 minutes.

**But `open` is not evidence that nothing is running; it is evidence that nothing wrote.**
Work on a remote host is invisible to every local instrument: before calling a remote-flavoured
tick stalled, ask for the run id. And `2>/dev/null` on a command that **changes** state makes
*recorded* and *rejected* the same answer. (2026-09-21) six ticks stayed `open` all their lives
because `tk update --status in-progress` (the value is `in_progress`) failed under a gag.

**Point the silence check at whoever is furthest ahead** — its silence costs most and looks
most like concentration. (2026-09-20) twice the furthest-ahead stream was the unwatched one.

## When a stream is silent, probe before concluding

This door sees *that* a stream is idle, never *why*: blocked on a prompt, its tier refusing, or
the account. Send the session, or the tier in question, **"reply ALIVE, no tools"** — about
three seconds, nothing spent. A refusal's text says nothing about its scope; report the probe's
result, not the 429's prose. (2026-09-20) four streams held 45 minutes on one tier's 429s while
a one-word probe showed the limit had already lifted.

## Step 4 — Restart what is stalled, before you print

**A stall is work that has stopped, and the seat's job is to start it again** (the human,
2026-09-20). For every stream classified **stalled**, message its session: which rule fired,
with the number, and ask for one line back if it is mid-something. Then print, naming each
stream you nudged. Never nudge a stream waiting on the human (a NEEDS YOU item), a row the
human drives, or the caller's own row.

Prefer asking to instructing: "`8ab` has been ready 21 minutes with nothing dispatched; one line
is enough if you are mid-something" gets a truthful answer, where "dispatch `8ab`" gets
compliance. Name a stall's shape when it has been seen before.

## Step 5 — Print

Exactly this shape. Column headers always; columns aligned; `—` where a column does not apply;
nothing narrated between the header and the table. Prose, if any, goes **after**.

```
STREAMS · <date> <time>

NEEDS YOU
  <tick>   <stream>   <what to do, where, and what closes it>   (or "  —")

STALLED / UNKNOWN DRIVER
  <stream>   <which rule fired, with the number>            (or "  —")

STREAM   SESSION   STATE   EPICS   ~%   AT   IN FLIGHT   LAST   WHAT NOW   RESOURCES
<name>   <session or "the human's own">   <working|idle|blocked|—>   <one glyph per epic>   <rough %>   E<n> of <N> · <closed>/<total>   <n implementers, m lines | clean | —>   <age>   <one clause>   <what the row claims> · <host if any>
…

HEAVY RUNS  free | held by <worktree or container> | — (the project names none)

HOLDS
  <what>   <since>   until <HH:MM>, <n> min left | ended <n> min ago: release it or hold it again   <by>   (or "  —")

OWED
  <id>   <stream>   <how long it has waited>   <what is owed>   (or "  —")

SCHEDULES
  <owner>   <what> · <when>                                  (or "  —   <why there are none>")
  after the terminal server or Claude stops: /streams restart (each row says how)

LOG  (the newest lines of coord/log.md)
  <line>                                                     (or "  —   nothing logged yet")
```

**One table, one row per stream** — session and progress on one line. **One glyph per epic, in
roadmap order:** `●` closed; the current epic by its fraction — `○` none closed, `◔` under a
quarter, `◑` under half, `◕` under all; `○` for every epic after it. **`~%` is rough, by the
human's definition (2026-09-20):** each epic is worth `100 / N`; a closed epic counts in full,
the running one `closed / total` of its share, an unplanned one zero (`●◑○` at 3/6 = 50%). It is
the only increment-wide number. AT is "E*n* of *N* · closed/total"; WHAT NOW is one clause ("a
wave running", "idle *n*m, *k* ticks left — watch"). No title column. Order: the mainline first,
then side streams in the order of their resources, then docs-only branches. STATE from `term.py
ls` or `ListAgents`; `—` for a hand-driven stream. IN FLIGHT counts live implementer worktrees
and their uncommitted lines; "clean" when live with nothing uncommitted; "docs only" for a branch
with no ticks. LAST is the newest commit on the stream branch or any tick branch. RESOURCES is
the row's claim from the project's `## Resources`, or `—`.

**NEEDS YOU leads with the tick id, and the rest is an instruction**, in three parts:

    <tick>   <stream>   DO <the act> · WHERE <session or path> · CLOSES WHEN <the acceptance>

    k2v   search   DO read the result page's three states and approve or reword them
                   · WHERE the search session, or the PNGs under tests/ui/__screenshots__/
                   · CLOSES WHEN your words are in the close reason (--from human)

- **DO is the tick's title**, verbatim when it reads as an act; a third-person title ("the card
  is approved") becomes the act ("approve the card") and nothing else changes. Never invent a
  step.
- **WHERE is the first qualifying thing in the description's own text — text order, not rank
  by kind.** Qualifying: a path naming a file that exists, relative to the stream's worktree; a
  `docs/` path naming a file; a URL route (`/about`). Read every path, backticked or not, every
  match. Only when nothing qualifies, in order: a bare file mention, a bare directory, "(tick
  gives no location)". A brace path is shown as written; a lone `.png` is never a location.
  **Never a candidate:** scratch paths (`/tmp`, `/var/tmp`, `/dev/shm`, `/run/user`); a build or
  output directory anywhere in the path (`node_modules`, `.next`, `dist`, `build`, `coverage`,
  `test-results`); an absolute path on a disk (`/home/…`, `~/…`); a slash command (`/dmtix go`).
  (2026-09-23) three passes: a throwaway `/tmp` path, then a boilerplate directory, then a diary
  file named in standing gates each outranked a tick's own `/about`.
- **CLOSES WHEN** from the acceptance (approval quoted in the close reason; a decision in an
  overview; a value on a host). If the tick does not say where or what closes it, say so rather
  than guess: that is a defect in the tick.

Wrap to three indented lines if it does not fit one.

**NEEDS YOU has three sources:** ticks awaiting the human; every **Now** row of
`coord/asks.md`, with its id and the exact thing to type; and **every hold past its end**:

    hold   <what>   DO release it if it is done: coord.py log "RELEASE <what>". Otherwise hold it again with a new end (--for 40m)
                    · WHERE <what>'s hold ended <n> min ago, at <HH:MM>
                    · CLOSES WHEN the log has a RELEASE line for it, or a new hold with a later end

The sections after HEAVY RUNS come from coord (Step 1), and each prints `  —` rather than
disappearing when empty:

- **HOLDS** — every open hold: since, time left, who holds it. **A hold has an end** (the human,
  2026-09-29): `coord.py log` refuses one without `--for` or `--until`. **When the end has
  passed the hold stays held** — listed as ended here *and* under NEEDS YOU, until `RELEASE
  <what>` or a new `HOLD <what>` from the same holder. Nothing releases on its own; nothing with
  no end is listed. Clock times in the human's local time; the log stores UTC.
- **OWED** — every unpaid `OWED <stream>: <what>`, with id, stream, wait and what; `PAID <id>`
  closes one. A stream correctly holding says nothing, so it falls out of a seat's working set;
  the seat reads this on every pass instead of remembering. (2026-09-21) a stream sat 29 minutes
  waiting for a window close the seat never sent.
- **SCHEDULES** — `coord/schedules.md`'s **Dies with its session** rows: owner, what, when;
  struck-through rows are left out. No file prints `  —   no coord/schedules.md: list what runs
  on a clock there`; no such rows prints `  —   nothing on a clock dies with a session`.
- **LOG** — the newest lines of `coord/log.md`, oldest first.

## What this door never does

- Edit a stream's tree, dispatch its ticks, or decide anything the human should.
- Edit any coord file or write a log line. A wrong table is said, for the seat to fix in place;
  a hold past its end is a NEEDS YOU item, not something this door releases.
- Nudge, land or message a stream whose row says it is the human's own.

## Field notes

One line each; the rule is above.
- (2026-09-21) the seat said "the machine is free" and a stream read it as a go and started a
  regeneration — a statement about the process list is not a grant; only the seat's explicit
  OPEN, after every stream has answered, is.
- (2026-09-21) a hold file still enforced the pre-correction rule after its prose was rewritten
  — when a prose rule is corrected, the thing that enforces it is a second edit; ask which kind
  of "holding" a stream means.
- (2026-09-21) the door demanded a name match on a field the snapshot does not have — a
  specification written from the armchair is a claim; run the snapshot before writing a rule.
- (2026-09-21) exact cwd equality missed a session in a subdirectory of its own worktree — match
  on a prefix, and read `foreground_cwd`.
- (2026-09-21) the door printed before it restarted, because the steps were out of order — the
  sequence is the instruction: classify, probe, restart, print.
- (2026-09-21) a fresh cut read as an unknown driver on the seat's own commit — a sentence the
  seat writes about the machine is a claim, and the machine outranks it.
- (2026-09-20) writing this door as code found eight underspecified places — a door that has
  never been implemented has not been read carefully.
- (2026-09-20) a row said "the human's own" for three hours after the human handed it on — a row
  the human drives is re-checked like any other cache.
- (2026-09-20) `ListAgents` did not see panes the human opened or resumed sessions — the
  terminal server's snapshot is the primary session source.
