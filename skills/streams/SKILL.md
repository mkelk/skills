---
name: streams
description: The seat that sees every stream — for the one session that coordinates several dmtix increments running side by side in their own worktrees. "init" writes the project's facts once; "status" prints what is running, what is waiting on the human and what has stalled, from files; "keep-running" acts on it hourly; "queue" keeps what waits on the human; "cut" sets a new stream up (branch, worktree, the resources the project names, records, a brief); "compact", "restart", "hotfix" and "land" cover the long-running sessions' context, bringing clocks back after a stop, an early fix to the trunk, and finishing a stream. Live state lives in git's common directory (coord/), shared by every worktree. Not for the sessions that run a stream — they use dmtix go.
---

# streams — the seat that sees every tree

One session holds this seat. It talks to the human, cuts streams, watches them, lands them,
and relays what one stream finds that another must act on. It never runs an increment and
never writes code on a stream's branch. **Dispatch on the argument; read ONLY the matching
reference and follow it exactly.** With no or an unknown argument, show this table and ask.

| Argument | Cadence | Door |
|---|---|---|
| `init` | once per repository, before the first `cut` | `references/init.md` — detect the trunk, package manager and test runner, ask the human about resources and the worktree root, write the project file `.devmeta/streams.md` (only the sections with content) with `scripts/coord.py init-file`, then `coord.py init`. `coord.py config` prints what the doors will read. |
| `status` | whenever the human asks "what is running" | `references/status.md` — one screen from `coord/streams.md`, `coord/log.md`, `tk`, the process list and the sessions (`scripts/term.py`, or `ListAgents`); what waits on the human; what has stalled; open holds, what the seat owes, what runs on a clock. |
| `keep-running` | on a timer, hourly (a cheap scout subagent does the looking: `references/scout.md`) | `references/keep-running.md` — `status`, then **act**: close forgotten windows, answer streams owed an answer, refresh drifted cells, land what is finished, restart what stalled, relay what one stream found. Prints only what the human must act on. |
| `queue` | whenever something waits on the human; checked every `keep-running` | `references/queue.md` — the list of what waits on the human (`coord/asks.md`, one row each, with the exact thing to type and a why), kept by the seat alone; a go counts only typed in the seat. |
| `compact` | twice a day at quiet times, or inside `keep-running` | `references/compact.md` — the long-running sessions' context: a larger auto-compact window and an after-compaction hook in each stream's worktree, and the idle tidy (`scripts/compact-idle.py`) that sends `/compact` to a stream that is idle, large, quiet and holds nothing. Never the seat. |
| `explain` | whenever asked | `references/init.md` → Step 6: what is set up here and why; writes nothing. |
| `cut <slug>` | once per new stream | `references/cut.md` — a stream (the project's mainline only when the human asks for it by name): the resources the project names, a branch and worktree, the project's `## At cut`, the records, a brief file the new session reads, and opens that session in its own pane (`term.py`) unless the human says not yet. |
| `restart` | after the terminal server, a Claude session, WSL or the machine stopped | `references/restart.md` — read `coord/schedules.md` (every crontab line, timer, session cron and background loop, with owner and how to restart it), find what is no longer running, and have each owner bring its own back. |
| `hotfix <slug>` | when a host is blocked on a running stream's gated fix | `references/hotfix.md` — merge one stream's branch to the trunk **without landing it**: the stream is unfinished and stays alive. Needs the human's go, a conflict-free merge, the project's checks on the merged tree, and the SHA handed to whoever owns the host. |
| `land <slug>` | once per finished stream | **not built yet** — `references/land.md` holds the checklist; landings are done by hand against it until two have confirmed every step. |

**The project's facts are not in this skill.** The trunk, where worktrees go, what a fresh
worktree needs, what a landing runs, what two streams may not share, which runs are too heavy
for two at once: each is a read of the project file `.devmeta/streams.md` through
`coord.py config` (`--get <fact>` for one bare value), with a detected default when the file
says nothing. "The trunk" below always means `coord.py config --get trunk`. `coord.py` means
`python3 <skill dir>/scripts/coord.py`; `term.py` means `python3 <skill dir>/scripts/term.py`,
the only place that talks to the terminal server.

Principles, binding for every door:
- **The state is a file — in git's common directory, not on a branch.** Live coordination state
  lives in `<git common dir>/coord/` (`git rev-parse --path-format=absolute --git-common-dir`):
  one directory every worktree of the repository shares at once, which git never tracks.

  | State | Home |
  |---|---|
  | The running streams' rows (worktree, session, resources, host, epics, status) | `coord/streams.md` |
  | Holds, deploys, hand-offs, what the seat owes: one dated line per event, append-only | `coord/log.md` |
  | What runs on a clock, with its owner and how to restart it | `coord/schedules.md` |
  | What waits on the human | `coord/asks.md` |
  | A roadmap's live state (the `roadmap` skill) | `coord/roadmaps/<name>.md` |
  | The project's facts and the rules for streams (what landed: git history and `coord/log.md`) | `.devmeta/streams.md`, in git |

  The seat edits `coord/streams.md` in place at a cut, a landing or a correction — no commit,
  no announcement for a row change — after copying it to the scratchpad, by exact match, and
  reads the change back. Any session writes a log line when it takes or releases a hold,
  deploys, or hands something to another stream, **in addition to** any message: a message is
  gone with its session, a log line is not. Write log lines with `coord.py log` (it delivers `OWED` to the seat and `PAID` back), which
  enforces the hold rules; `coord.py init` creates the directory on first use. **It is per
  machine**: anything that must cross machines goes to the project's issue tracker.
  (2026-09-23) a committed streams table churned a commit per row change and the facts streams
  depended on lived only in chat — so live state moved to `coord/`.
- **The seat writes on the trunk. A stream's branch belongs to the stream — including the
  merge.** Sync-forward at the cut is the seat's, because nobody holds the tree yet. After that
  it is the stream's: the seat says *the trunk has moved, sync when it suits you*, and the
  stream merges when its own work allows. A seat cannot see what a stream has staged, so it
  cannot know a harmless merge is harmless. (2026-09-21) a seat's one-file merge into a running
  stream forced it to reset two implementer worktrees already provisioned — so announce; do not
  merge.
- **Doors, not engines.** The loop lives in the ticks skill; scoping in `dmtix start`. These
  doors read state, set streams up, and print what to tell a session. They never dispatch a
  tick and never decide anything the human should.
- **Verify on the thing — and on the right copy of it.** A session's report is not its state.
  `status` reads `tk`, the worktrees and the process list; it does not ask the sessions. A hold
  file is not `pgrep`; a tracker is not the tree; a roster is not the worktree; a checkout's
  disk is not the branch's tip. **A report can cite a run that did not contain the thing it
  reports on**: before accepting a per-spec result, check the named spec appears in the run it
  is attributed to — a grep over a log that already exists. A spec list inside a report is a
  claim like every other sentence in it. (2026-09-21) a tick reported two baselines "passed in
  the union run" that were not in the union — right by luck, and it would have read the same
  wrong.
- **Identity is what a session holds, not what it is called.** A session's name says nothing
  about which branch it drives. Ask the worktree who has been committing, never the roster who
  is present. One session may hold two streams, so the session cell repeats and no door may
  treat one-row-per-session as an invariant. (2026-09-21) reading a naming convention as an
  absence called a working stream stalled and opened a second pane on a driven worktree.
- **A stream missing from the table is invisible, not merely miscounted.** Every door reads
  the table, so an unlisted stream gets the machine handed away over the top of it. Reconcile
  `git worktree list` against the table before acting on the machine, and add the row before
  the first command.
- **A merge silently restores what a stream moved out.** A list file two branches both edit
  (a todo file, say) loses an entry on a stream's branch; the seat adds entries beside it on the
  trunk; the sync-forward's obvious resolution puts the moved entry back. So announce which
  entries were added and where, and after any sync that touched such a file, verify in both
  directions (gone from the list, present where it moved). A project whose tasks live in an
  issue tracker is spared this for tasks. (2026-09-21) a stream caught two restored entries only
  because it checked both directions.
- **The seat is never a load-bearing part of operations.** A seat is an interactive session
  that may be asleep or gone next week, so when a default needs an executor and the honest
  answer is "the seat, by remembering", the default is wrong and the right answer is a guard
  that trips: a visible failure with an error report beats the seat as a hidden part of
  operations (the human, 2026-09-21).
- **A guard is a claim until someone has watched it fire — and its stated guarantee is a
  second claim.** Test the sentence the guard makes about itself against the case that
  sentence names, and say any gap aloud; a guard that over-promises is believed, and its promise
  outlives it in docs. (2026-09-21) a regex guard said "the day this changes, this test fails";
  `config?.KEY` defeated it, and the claim was already in the docs.
- **A planted mutation must fail, and fail where you claimed.** A plant that does not change the
  result is an unexplained result, not a clean bill: the assertion is blind, or the plant did
  not do what you thought. First check whether the string you planted is a SUPERSTRING of what
  the assertion names — a rename-style plant can never fail a substring matcher; plant a
  deletion or an unrelated token. And a red that arrives from a sibling assertion is the same
  fault as a green: quote the failing message and check it names your line. (2026-09-21)
  `Waiting` → `NotWaiting` passed a substring role match; with exact matching it failed.
- **A written rule whose evidence has expired is followed without being read.** When a rule
  cites a measurement, date the measurement, not the rule (*"16 GiB, measured 2026-03-01"*
  invites a re-measure; *"as of 2026-03-01, two tiers do not fit"* is obeyed as fact). A finding
  that is not re-read gets rediscovered, so a protocol's *re-read before planning* is worth
  obeying mechanically. When measurement and record disagree, the measurement wins and is folded
  into the record, not set beside it. (2026-09-21) four streams obeyed a memory limit the
  profile itself called obsolete.
- **When two careful observations of one command disagree, read the command's own help
  first.** A disagreement about what a command does is usually a question about its flags.
  (2026-09-21) two streams' opposite readings of a snapshot-update flag were its three modes,
  answered by one `--help`.
- **In a wide wave, an end-of-file record is the orchestrator's to write, not the
  implementer's.** A diary or changelog append is a merge seam: one writer at the close, not N
  during. Tell a stream before its first wide wave. (2026-09-21) three of four sibling ticks
  appended to the diary and two conflicted.
- **An absence of signal reads as a positive result.** A plant that does not fail reads as
  *the guard works*; a gagged write that was rejected reads as *recorded*; an idle pane whose
  work runs on a remote host reads as *stalled*; a screenshot under tolerance reads as
  *unchanged*; a spec absent from a run reads as *passed*; a print after an edit that changed
  nothing reads as *landed*. Ask of any green result *what would this look like if the
  instrument were not working?* Where the answer is "the same", it is not evidence yet: name
  the run, force the byte comparison, read the render, take the gag off stderr. A print
  statement is not a check — assert the new text after a write, and
  `test -n "$(git diff --cached --name-only)"` before a commit. (2026-09-21) an aborted heredoc
  edit with a chained commit put two hollow commits on the trunk.
- **The seat is expensive.** Whatever this skill can read from a file, the seat must not
  carry in context. If a door is missing something the seat keeps remembering, the fix is
  the door, not the memory.
- **Coordination is a cost, re-priced against the machine it runs on.** Hold only what cannot
  be isolated (a **writing** run on a shared singleton, not a read), and **every hold has an
  end** — `coord.py log "HOLD <what>: …" --for 40m` or `--until 07:30`, refused without one,
  one holder at a time, closed with `RELEASE <what>` — so a passed end shows under NEEDS YOU
  instead of holding the machine forever. Read-only verification runs alongside; a project that
  isolates its writing runs (a per-checkout build database, say) takes no hold for them. The
  finding-and-telling earns its cost; the stop-the-world does not. Organising too
  cautiously is a fault too (the human, 2026-09-21): the seat had held four suites on a
  measurement the machine had outgrown.

## Open problem: worktrees, sessions and panes are three things with no mapping

Worktrees, sessions and panes must line up far better than they do (the human, 2026-09-21).
Not solved. Each of these happened on one night of five parallel streams: a session drove a
stream under a name that said nothing about its branch; a stream was cut without a row and was
invisible; a session renamed itself mid-life (a send to a stale name that silently succeeds is
worse than one that bounces); one session held two branches; panes were closed on unfinished
work and left open on deleted worktrees.

What a fix has to give, whatever its shape:
- **Given a worktree, name its session; given a session, name its worktrees.** The first is
  recoverable today: `term.py ls --json` gives every session's `cwd`, `state`, `id` and label,
  worktree → session → state without asking anyone. Use it, rather than ending a door by asking
  the human for a name. Still missing: a session that dispatches into trees it does not sit in
  cannot be asked what it holds.
- **One driver per worktree, provably.** Two seats on one tree is the most dangerous state on
  the machine.
- **A pane's existence is not the question; what it holds is.**
- **The human should not be the index.** A door that ends *tell me the session's name* has made
  them the index in writing.
- **Store no identity that the machine can answer on demand.** Session names, pane ids and
  terminal titles all drift; the worktree path cannot, because a session's `cwd` is the tree it
  sits in. A session column is a cache with a short life; resolve it again rather than believe
  it. (2026-09-21) a session name, a pane id and a title all drifted within twenty minutes.

Until it exists, every door treats the roster as a hint and the machine as the fact.

Source of truth: `github.com/mkelk/skills` → `skills/streams/`.
