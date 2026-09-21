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
  of it. **And a fifth face, the one aimed at the seat: a report can cite a run that did not
  contain the thing it reports on.** On 2026-09-21 a tick reported two named baselines
  "both passed unchanged in the union run" — and that spec **was not in the union**, not in
  the list it was given and not in the one that ran. The conclusion happened to be right; a
  later direct run confirmed it. **Had it been wrong, the report would have read exactly the
  same.** So before accepting a per-spec result from any session, check the named spec
  actually appears in the run it is attributed to — a grep over a log that already exists.
  **A spec list inside a report is a claim like every other sentence in it**, and it is the
  one nobody thinks to check, because it looks like provenance rather than assertion.
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
  is *assumed* to work replaces one wish with another. **A guard's stated guarantee is a
  second claim, separate from the guard, and it is the one that gets published.** On
  2026-09-21 an anti-staleness guard was a regex over runner source text whose docstring said
  *the day a runner changes what it needs, that test fails* — and a reviewer ran the real
  regex over twelve idioms: `config?.KEY` alone defeats it, one character from the code as
  written, and the walk never enters the package every config comes from. The claim had
  already been copied into `docs/current/`. So: **test the sentence the guard makes about
  itself, against the case that sentence names**, and where a gap remains, say it aloud in the
  same breath. A guard that over-promises is worse than none, because it is believed — and its
  promise outlives it, in documentation nobody re-derives.
  **And the trap under the trap: a plant can pass.** 2026-09-21, proving a guard by planting a
  mutation — `Waiting` → `NotWaiting` — the assertion **still passed**, because
  `getByRole(..., { name })` matches by **substring**, exactly like `getByText`. With
  `{ exact: true }` it failed properly. So the guard absorbed the plant and **read as proven
  while being blind.** This is the one case where *watch it fail* misleads: it does not fail,
  and that gets recorded as evidence. **A mutation that does not change the result is not a
  clean bill — it is an unexplained result**, and the two explanations (the assertion is
  blind; the plant did not do what you thought) must be told apart before either is believed.
  First thing to check, and state it in the direction you can actually apply: **is the string
  you planted a SUPERSTRING of the string the assertion names?** `Waiting` → `NotWaiting` is
  the canonical shape — the rendered text changed, and the matcher still matches because what
  it looks for is still inside it. A **rename-style plant can never fail** against a substring
  matcher, so choosing one is choosing a test that cannot fail. Plant a *deletion* or an
  unrelated token instead.
  **And this is not a testing detail; it is how this project accepts any guard at all.** Every
  red-green proof every stream runs is *plant it, watch it fail, revert* — so every stream can
  be misled by it, and **the failure is silent in the direction that reads as success**. The
  sentence that certifies a blind guard is *"planted it, still passed, so it must be covered
  elsewhere."* (09s3-kbw, 2026-09-21, generalising its own `kni` finding past the fixtures it
  was found in.)
  **And the other half, which completes the rule: a mutation that fails for the WRONG REASON
  is not proof either.** 2026-09-21, a reviewer proving a negative assertion was live mutated
  `DEAD_END_CAUSES`, the test failed — and it failed on a **sibling assertion that said nothing
  about the string in question**. It threw its own proof out and built one that fails on the
  right line. **So the mutation must fail, and fail where you claimed.** A red that arrives
  from somewhere else in the same test is the same fault as a green: it tells you the file is
  wired up, not that the assertion you are defending is doing anything. Quote the failing
  message and check it names your line.
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
- **When two careful observations of one command disagree, read the command's own help
  first.** Two streams measured `--update-snapshots` from the outside — one saw a stale
  baseline survive, one saw 125 passing baselines rewritten — and the seat recorded it as an
  open question between them. It was neither: a bare `--update-snapshots` presets to
  `changed`, `=all` rewrites matching snapshots too, and no flag at all defaults to `missing`
  and writes a baseline for any spec lacking one. **Three modes, three observations, no
  contradiction.** The answer cost one `--help` and one `grep` of the wrapper — no browser, no
  tier, no window — and it had sat unresolved because both parties measured a *behaviour* from
  outside where the thing is a *preset* on the inside. So before arbitrating between two
  observations, check whether the tool simply states the answer: **a disagreement about what a
  command does is usually a question about its flags wearing the costume of a question about
  its behaviour.**
- **In a wide wave, the diary is the orchestrator's to write, not the implementer's.**
  `docs/diary.md` is an end-of-file append, which is the known merge seam, so four sibling
  ticks appending to it produce three conflicts and one lucky winner. On 2026-09-21 one tick
  of four deliberately did **not** append, on exactly that reasoning, and its stream wrote the
  entry at close instead; the other three appended and two conflicted. **The implementer that
  skipped it was right, and the rule generalises to any end-of-file record a wave writes
  in parallel** — one writer at the close, not N writers during. Tell a stream this before its
  first wide wave rather than after its first three-way conflict.
- **The recurring defect has one shape: an absence of signal reads as a positive result.**
  Named by 09s4-hos, 2026-09-21, after the third instrument in one day failed the same way —
  and it is worth stating as a class, because each instance looks like a different bug and the
  fix for each one is local while the fix for the class is a habit.
  - A **planted mutation that does not fail** reads as *the guard works*. (It can mean the
    assertion is blind.)
  - A **gagged write that was rejected** reads as *it was recorded*. (`tk update --status
    in-progress`, six ticks, a whole day.)
  - An **idle pane with an open tick and nothing in flight** reads as *stalled*. (The work was
    running on a remote host, invisible to every local instrument.)
  - A **screenshot that passes under tolerance** reads as *nothing changed*. (Stale-and-green;
    found twice in one increment.)
  - A **spec that does not appear in a run** reads as *it passed in that run*.
  In every case the instrument produced **nothing**, and nothing was read as **good**. The
  common cure is not more instruments — it is to ask, of any green result, *what would this
  look like if the instrument were simply not working?* **Where the answer is "the same", the
  result is not evidence yet**, and one cheap check converts it: name the run the spec was in,
  force the byte comparison, read the render rather than the pass, ask for the run id, take the
  gag off stderr. **A result that cannot distinguish success from silence is a result you have
  not taken.**
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
