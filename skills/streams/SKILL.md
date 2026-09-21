---
name: streams
description: The seat that sees every stream — for the one session that coordinates several dmtix increments running side by side in their own worktrees. "status" prints what is running, what is waiting on the human and what has stalled, from files; "cut" sets a new side stream up (branch, worktree, ports, records, a brief). Not for the sessions that run a stream — they use dmtix go. Landing is still by hand until the land door exists.
---

# streams — the seat that sees every tree

One session holds this seat. It talks to the human, cuts streams, watches them, lands them,
and relays what one stream finds that another must act on. It never runs an increment and
never writes code on a stream's branch. **Dispatch on the argument; read ONLY the matching
reference and follow it exactly.** With no or an unknown argument, show this table and ask.

| Argument | Cadence | Door |
|---|---|---|
| `status` | whenever the human asks "what is running" | `references/status.md` — one screen from `.devmeta/streams.md`, `tk`, the process list and `ListAgents`; what waits on the human; what has stalled. |
| `keep-running` | on a timer, every ~30 min | `references/keep-running.md` — `status`, then **act**: close forgotten windows, answer streams owed an answer, refresh drifted cells, land what is finished, restart what stalled, relay what one stream found. Prints only what the human must act on. |
| `cut <slug>` | once per new stream | `references/cut.md` — asks first whether it is a side stream or the mainline in a worktree, then: the port block, a branch and worktree, `.env`, deps, the records, a brief file the new session reads. |
| `hotfix <slug>` | when a host is blocked on a running stream's gated fix | `references/hotfix.md` — merge one stream's branch to `master` **without landing it**: the stream is unfinished and stays alive. Needs the human's go, a conflict-free merge, a typecheck on the merged tree, and the SHA handed to whoever owns the host. |
| `land <slug>` | once per finished stream | **not built yet** — `references/land.md` holds the checklist; landings are done by hand against it until two have confirmed every step. |

Principles, binding for every door:
- **The state is a file.** `.devmeta/streams.md` on master is the table of every running
  stream and the standing rules; the seat edits it with a scratch worktree and `git
  update-ref`, never a checkout — the main checkout belongs to whichever session runs the
  mainline. Every stream gets it by sync forward.
- **The seat writes on master. A stream's branch belongs to the stream — including the merge.**
  Sync-forward at the cut is the seat's, because nobody holds the tree yet. After that it is
  the stream's: the seat says *master has moved, sync when it suits you*, and the stream
  merges when its own work allows. On 2026-09-21 the seat merged master into a running
  stream's branch to deliver a table update, and that stream had **two implementer worktrees
  already provisioned from the previous head** and had to reset both before dispatch. Nothing
  was lost, and nothing about the change was wrong — it was one file the stream did not touch.
  The cost was entirely in the timing, which is the point: a seat cannot see what a stream has
  staged, so it cannot know a harmless merge is harmless. Announce; do not merge.
- **Doors, not engines.** The loop lives in the ticks skill; scoping in `dmtix start`. These
  doors read state, set streams up, and print what to tell a session. They never dispatch a
  tick and never decide anything the human should.
- **Verify on the thing — and on the right copy of it.** A session's report is not its state.
  `status` reads `tk`, the worktrees and the process list; it does not ask the sessions. Four
  faces of one fault, each of which cost something real on 2026-09-21: a hold *file* read
  instead of `pgrep`; a *tracker* read instead of the tree; a *roster* read instead of the
  worktree; and the streams table read from a **checkout's disk** instead of from `master`,
  which printed "nothing is running" over two live streams because `update-ref` moves a ref
  and touches no working tree. Reading the real thing is not enough if you read a stale copy
  of it.
- **Identity is what a session holds, not what it is called.** `ListAgents` names sessions,
  and a name says nothing about which branch one drives. Reading a naming convention as an
  absence made this seat call a working stream stalled and have a second pane opened on a
  worktree that already had a driver — two sessions believing they held one tree, the most
  dangerous state on the machine. Ask the worktree who has been committing, never the roster
  who is present. One session may hold two streams, so the session cell repeats and no door
  may treat one-row-per-session as an invariant.
- **A stream missing from the table is invisible, not merely miscounted.** Every door reads
  the table, so an unlisted stream gets the machine handed away over the top of it. Reconcile
  `git worktree list` against the table before acting on the machine, and add the row before
  the first command — a rule in the `cut` door cannot catch a stream that never went through
  that door.
- **A merge silently restores what a stream moved out, and nobody is watching for it.** When
  a stream scopes a todo entry into its overview, it deletes that entry on its branch. Master
  never saw the delete — so when the seat adds new entries *adjacent* to it, the next sync
  forward turns a clean delete into a conflict whose obvious resolution **puts the moved entry
  back**. No second stream, no mistake by anyone. On 2026-09-21 a stream caught two entries
  restored this way and only because it verified **both** directions: zero occurrences in
  `todo/todo.md`, two in the overview. Checking only the file you edited finds nothing. **The
  brief's usual warning does not cover this** — *tell the seat which entries you moved* guards
  against a second stream taking one, not against master re-adding it underneath you. And the
  seat manufactures the conflict: it adds entries to master all day, beside entries streams
  have already moved. So **announce which entries were added and where**, so a stream resolving
  a todo conflict can tell a new entry from a ghost; and after any sync that touched the todo,
  verify in both directions.
- **The seat is never a load-bearing part of operations.** Morten, 2026-09-21, rejecting a
  default that named the orchestrator as executor: *"better that prod hits the ceiling and
  sends Sentry issues than you being a 'shadow' part of ops."* A stream had registered a
  decision correctly — recommendation, default, named executor — and the executor it named was
  the seat: *pause the newsletter when spend nears the ceiling.* The seat accepted, twice
  noting it had no alarm and would check when it happened to look. **That is not a control; it
  is a wish with a name attached.** A seat is an interactive session that may be asleep,
  elsewhere, or gone next week, and work that depends on one being awake has no owner at all.
  So when a default needs an executor and the honest answer is "the seat, by remembering",
  **the default is wrong and the right answer is a guard that trips.** And a guard is a claim
  until someone has watched it fire: replacing a person who remembers with a mechanism that
  is *assumed* to work replaces one wish with another.
- **A written rule whose evidence has expired is more dangerous than no rule, because it is
  followed without being read.** Three instances on 2026-09-21, and the seat was central to
  all three. *Two tiers do not fit on this machine* had been obsolete in `.tick/profile.md`'s
  own words for a day — both the memory figure and the tier's cost — and four streams obeyed it
  anyway, because obeying was cheaper than checking. The screenshot-blindness finding that an
  afternoon of measurement produced **was already in `.tick/learnings.md`**, tolerance named
  explicitly; it was rediscovered at full cost. And a stream planning a wave hit a `tk` flag
  that is silently ignored, whose fix was the last line of a learnings entry it had not re-read
  though its own protocol says to.
  So the failure has two halves and they need different answers. **A rule that is stale gets
  obeyed** — so when a rule cites a measurement, **date the measurement, not the rule.** The
  difference decides whether anyone ever checks: *"30.5 GiB, measured 2026-09-19"* invites a
  re-measure; *"as of 2026-09-19, two tiers do not fit"* reads as provenance and is obeyed as
  fact. The memory figure was dangerous less for its age than because **its number was
  load-bearing and uncheckable in place** — *two tiers do not fit* never said against what, so
  nobody could tell it had stopped being true without going and measuring. A rule whose
  numbers cannot be pointed at is a hypothesis. **A finding that is not
  re-read gets rediscovered** — so the value of writing it down is entirely in the re-reading,
  and a protocol that says *re-read before planning* is one of the few instructions worth
  obeying mechanically. When measurement and a written record disagree, the measurement wins
  and **the record gets the measurement folded into it**, not a second entry beside it.
- **The seat is expensive.** Whatever this skill can read from a file, the seat must not
  carry in context. If a door is missing something the seat keeps remembering, the fix is
  the door, not the memory.
- **Coordination is a cost, and it must be re-priced against the machine it runs on.**
  Morten, 2026-09-21: *"i think maybe we are organizing too conservatively here."* He was
  right, and the way he was right is the lesson. The alternation rule — *two UI tiers do not
  fit on this machine* — was measured against 15 GB and a 15.4-minute, 2.9 GB tier. The
  machine is **30.5 GiB with 20 cores**, and since 2026-09-21 the tier runs over a production
  build at **495 MB and about three minutes**. Both halves were obsolete, both corrections
  were already written down in `.tick/profile.md`, and the seat held four streams' Vitest
  suites anyway — across a window longer than the run it protected. **A rule whose measurement
  has been superseded is a cached answer presented as a measurement**, the same fault this
  door hunts everywhere else, wearing the costume of caution. So: hold for a **writing** run
  only, publish the window as a duration rather than an open-ended wait, and let read-only
  verification and Vitest run alongside. The distinction that survives, from the stream that
  argued it: **the finding-and-telling earns its cost; the stop-the-world does not.**

## Open problem: worktrees, sessions and panes are three things with no mapping

**Morten, 2026-09-21: "we need much better alignment between worktrees, sessions, panes."**
Not solved. Named here because every door currently guesses at it, and on one night of five
parallel streams the guessing failed five distinct ways:

- A session drove a stream under a name that said nothing about the branch it held, so the
  seat read "no session for this stream" as a stall and had a **second pane opened on a
  worktree that already had a driver**.
- A stream was cut without a row, so it was **invisible to every door** and the machine was
  handed away over the top of its running tier.
- A session **renamed itself mid-life**; messages to the old name still worked, which hid it.
  (On 2026-09-21 it happened again and the old name **bounced** — `No agent named … is
  reachable` — which is the better failure of the two: a send that silently succeeds against a
  stale name is how a stream gets told something its driver never reads.)
- A session held **two branches**, which the one-row-per-session table cannot represent, so
  the reconciliation kept dropping one and its row silently reverted.
- Panes were **closed while their work was unfinished** (a mainline seat mid-deploy) and
  **left open on deleted worktrees** — both invisible from the seat, in opposite directions.

What a fix has to give, whatever its shape:
- **Given a worktree, name its session; given a session, name its worktrees.** Both
  directions, from the machine rather than from anyone's memory. Today only the first is
  recoverable — and **it is more recoverable than this section has been admitting**:
  `herdr api snapshot` answers it directly, giving every agent's `cwd`, `agent_status`,
  `pane_id` and terminal title, which is worktree → pane → state without asking anyone. On
  2026-09-21 the doors had that answer in hand and still printed `—` for both sessions and
  still ended a cut by asking the human for a name. **The missing half is not the measurement,
  it is the habit of using it.** What is genuinely still missing is the other direction: a
  session that dispatches ticks into trees it does not sit in cannot be asked what it holds.
- **One driver per worktree, provably.** Two seats on one tree is the most dangerous state
  on the machine and tonight it was caught by luck — one of them said out loud what it
  thought it owned.
- **A pane's existence is not the question; what it holds is.** A closed pane whose stream is
  unfinished and an open pane whose worktree is deleted are the same fault, and neither shows
  up in a roster of names.
- **The human should not be the index.** Asking "whose pane is this?" cost real time tonight
  and only worked because three sessions answered honestly. A door that ends by saying *tell
  me the session's name and I will put it in the table* has made him the index in writing;
  the `cut` door said exactly that until 2026-09-21.
- **Store no identity that the machine can answer on demand.** Every handle a table can hold
  drifts, and on 2026-09-21 all three drifted within twenty minutes of being written, each a
  different way: a session **renamed itself mid-life** (`fh-side-prod-c2` → `side-prod`, and a
  message to the old name bounced); a **pane id changed** when a pane was closed and reopened
  (`w10:p1` → `w22:p1`) with nothing about the stream changing; and a **terminal title is
  whatever a human last typed** — `inc-09`, `todo.md review`, `Increment definition`,
  `Claude Code`, not one of them naming a branch. **The worktree path is the only join key
  that cannot drift**, because a session's `cwd` cannot differ from the tree it is sitting in,
  and it is already in the table. The `[ref]` is the only stable name-like handle; it survived
  the rename unchanged. So a session column is a cache with a short life, and every door that
  reads one should resolve it again rather than believe it.

Until it exists, every door treats the roster as a hint and the machine as the fact.

Where it came from: `docs/thoughts/2026-09-20-orchestrator-pattern.md` in the project that
first needed it. Source of truth: `github.com/mkelk/skills` → `skills/streams/`.
