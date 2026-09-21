## Purpose

Answer "what is running, is anything waiting for me, has anything stalled" in one screen,
from files and processes, never from memory and never by asking the sessions.

**If the project provides a status command, run it instead of Steps 1–3.** A project that has
worn this door long enough usually grows one (in `ai-newsletter`: `pnpm fp streams:status`,
`--json` for the parts). It reads the same sources in about a second and costs the seat
nothing, which is the whole point — the seat's context is the expensive thing on the machine.
Read its output, print Step 5's shape, and fall back to the steps below only when it is absent
or refuses a row.

**Run the worktree reconciliation yourself even then.** `git worktree list` against the rows
the command printed, every time — it is three seconds, and it is the one guard that catches
both of this door's blind spots at once: a stream that never went through `cut` and so has no
row, and a command that read a stale copy of the table and so printed no rows at all. On
2026-09-21 a command answered "nothing is running" with two streams live and three worktrees
on disk; the reconciliation would have caught it without the seat needing to already know.
**A command's empty table is a claim; `git worktree list` is the measurement.**

The steps below stay here because they are the specification the command is measured against,
and because the seat must be able to answer without it. **Where the command and these steps
disagree, these steps are right and the command has a bug** — say so, and record it where the
project records work, rather than quietly reporting what the command said.

## Step 1 — Read the table

**`git show master:.devmeta/streams.md` — from the ref, never from a checkout's disk.** The
file is the same on every branch, which is exactly what makes reading it from disk look safe;
it is not. The seat writes the table on master with `update-ref`, and **`update-ref` moves the
ref without touching any working tree**, so the bytes on disk stay at whatever they were
before the last row was written. A door reading them answers about a machine that no longer
exists. Read the ref and the whole class of fault is gone. Each row gives a stream's
increment, session name, branch, worktree, ports, host and epics. **The worktree is the only
cell that is a fact; the session and epics cells are caches the seat wrote by hand** and both
have been measured wrong on the same afternoon. Step 2 says where each is really read from. If the file is
missing, say so and stop — this door has nothing to stand on without it.

**The increment id may be in either the `stream` cell or the `increment` cell** (`08s3-pci` is
a stream name that is also an id). Match it in either. A row that lists epics but carries no id
in either cell is refused **by name** — say which row and what it is missing, and carry on with
the rest; a docs-only row (no epics, `—`) is exempt, since it has no increment to find.

### Then read the machine, and reconcile it against the table

**The table is the seat's claim; `git worktree list` is the measurement.** Run it, and for
every worktree that is neither the mainline's nor a `.ticks-worktrees/` tick tree, find its
row. **A worktree with no row is a stream the seat cannot see** — worse than a stream whose
driver moved, because every other door reads the table: a `status` reports it as absent, and
a landing or a machine hand-off is decided as though it did not exist. Print each one under
its own heading with its branch, head, last commit time and whether anything of its is
running, and say plainly that it is unlisted. Then find its seat by asking the plausible
sessions by name, and add the row before doing anything else with the machine.

On 2026-09-21 an unlisted `tierspeed` stream held the browser for a `chat.png` regeneration
while this seat, reading only the table, released the machine to another stream; two full
Vitest suites ran inside the screenshot window and the image was committed on the strength
of it. A rule in the `cut` door would not have caught it — the stream never went through
that door. **Only a detector that starts from the machine catches a stream that never
announced itself.** Run the same reconciliation in reverse: a row whose worktree no longer
exists on disk is a landed stream whose row was never removed.

## Step 2 — Measure each stream, on the thing

For every row, gather — all read-only, all from the machine, none from a message:

| what | how |
|---|---|
| its session | Two sources, and the second is the better one. (1) `ListAgents`: match the row's session name; gives busy / idle / waiting. (2) **`herdr api snapshot`** (when herdr runs — `~/.config/herdr/herdr.sock` exists): every agent with its `cwd` and `agent_status` (working / idle / **blocked**). **Match by worktree. There is no name to match on.** This door said "match by name first" until 2026-09-21, when a stream checked the snapshot instead of the door: **`herdr api snapshot` carries no session name.** Its per-agent fields are `agent`, `agent_session` (an opaque UUID), `agent_status`, `cwd`, `focused`, `foreground_cwd`, `pane_id`, `revision`, `state_change_seq`, `tab_id`, `terminal_id`, `terminal_title`, `terminal_title_stripped`, `workspace_id`. The only human-readable label is `terminal_title`, which this same door documents as worthless — whatever a human last typed, naming no branch. It *looks* like a name because Claude sets the terminal title from the session name when a session has one, so the two coincide often enough to fool a reader; they are not the same field and they drift apart the moment anything else sets a title. The name in the table exists only in `ListAgents`, which is an agent tool and **cannot be called from a `tsx` CLI at all**. So name-matching is not a rule a project's status command can implement, and a door that demands it is asking for something unreachable.

**All of this is reachable only while herdr is up, and unverifiable is not the same answer as absent.** When the socket exists but the call fails, the door already marks sessions unseen and the classifier reads that as *unknown*, not *nobody*. Every identity check added here rides that same distinction rather than inventing a second one: a UUID that cannot be checked and a UUID that does not match are different findings.

**So: `cwd`, prefix not exact, and `foreground_cwd` too.** One row per agent at most. The 2026-09-20 case this rule was written for — a driver dispatching ticks into trees it does not sit in — is real and gets a better answer than a name: **the driver's own cwd is itself one of the seat's known worktrees**, so it is attributed by asking which row's tree it sits in. An agent whose cwd is under **no** row's worktree is the genuinely unattributable one, and it gets **its own line** ("agent in no stream's tree", with its cwd) rather than being reported as an unknown driver on somebody's row.

**Store the session id, not just the name.** It is stable across a rename — the one handle that is both durable and reachable from a CLI — and it turns the session cell from a claim into something checkable: *is the agent in this worktree still the session this row recorded?* A changed id on an unchanged worktree is its own finding: the pane was closed and replaced, which the seat cannot see today. Until a row carries one, **print the name as recorded, never as verified**; that check belongs to a session with `ListAgents`, not to the CLI.

**`agent_session` is an object, not a string.** It is `{agent, kind, source, value}` and the id is **`.value`**; `kind` is `"id"` today and would not exist as a field if that were the only kind it could ever be. Read `.value` and refuse to assume the rest — comparing the object itself yields `"[object Object]"`, which matches nothing, forever, without ever erroring. That is the quiet-failure shape this door exists to hunt.

Proof it really is the Claude session id, since nobody should take a field's name for its meaning: the pane at one worktree reported `value` `c8954c0f-…`, and that is the same id the harness had independently keyed that session's scratchpad path on. Two witnesses, one id.

**And a warning for whoever checks this next: the terminal title will look like a valid key and is not.** On 2026-09-21 `terminal_title_stripped` equalled the `ListAgents` session name on **all four** live panes — `orchestrator`, `side-todos`, `inc-09`, `side-prod`. Four for four is what a reader will see, and it is still wrong: the agreement is Claude setting the title from the name, not an identity between them. Anything else that sets a title breaks it, silently, and nothing in the sample warns you. Match by cwd = the row's worktree; this catches sessions that never registered with Claude's list (a resumed session, a pane opened by the human) and gives `blocked` as a first-class state, which `ListAgents` only shows as "waiting". **Two agents with the same cwd is a finding in itself, and it is the loudest one this door has** — report it; one checkout, one orchestrator. It is also the only identity claim answerable from `cwd` alone, which is why it survives every correction to the rest of this cell: two seats on one tree is the most dangerous state on the machine, and it needs no name to detect. **Except the seat's own pane:** the orchestrating session is often started in the main checkout and is one of the two. **The caller says who it is; the door does not guess.** A project command takes `--self <cwd or pane id>`, falling back to `HERDR_PANE_ID` when the flag is absent, so both ways of calling are right; a seat reading these steps by hand excludes the pane it is sitting in, which it knows for free. Inference was tried and failed twice — `herdr pane read <id>` to recognise its own prompt, which does not work when the door runs as a subprocess, and cwd matching, which is wrong the moment the seat steps into a stream's worktree to write records. **Excluding the caller must not swallow a real finding:** two *other* agents in one checkout is still reported, and the flag is shown wherever the door shows the command, or nobody passes it. Better still, start the seat in a directory of its own. **The caller is never read as a row's session or state** — excluding it must not then turn the seat's own stream into an "unknown driver". If another agent shares that cwd, it supplies the session and state; if none does, the row prints `—` in both columns and the unknown-driver rule is skipped for that row alone. The seat knows it is sitting there; saying so tells the human nothing. **When a row's driver is matched by cwd rather than by name, print what the machine knows — the pane id and the terminal's title — never `—`.** herdr gives both, and a row printing a live state beside an empty session says the door found somebody and will not name them. `—` in that column means *nobody is there*; it must never mean *somebody is there and the table has not been told their name*. Needs `tk` ≥ 0.31 for `tk herd`, but the snapshot is `herdr`'s own CLI and needs nothing. |
| its epics | **From the stream's own `.devmeta/current-increment.md`, not from the table's epics cell.** The `**Roadmap (tk):**` line is per branch, written by the method when the stream scopes itself, and reads either `project <id> → <epic> (E1 …), <epic> (E2 …)` or the literal `none.` when nothing is scoped. That line is authoritative; the table's cell is the seat's memory of it, refreshed by hand and therefore stale by default. **The two differ constantly and the difference is not cosmetic**: on 2026-09-21 two streams scoped themselves and ran implementer waves for an hour while the table still said `— (not scoped)`, so the door printed *unscoped, docs only* over live work — identical, on screen, to the one stream that genuinely had no increment. **A door that cannot tell "not scoped yet" from "scoped, and the seat has not noticed" renders both as the first**, which is the more reassuring of the two and the wrong one. Fall back to the table's cell only when the worktree is gone (a landed stream whose row survives), and say which source was used. |
| its ticks | **Read them in the stream's own worktree, never anywhere else** — the tracker is per branch, so the same command in the main checkout answers about the mainline's ticks and looks entirely plausible. `tk list --status open` there. **The tracker is shared across every worktree of one repo, so filter by the stream's own epics** — a tick belongs to the stream if `tk show <id>` names one of its epics as parent. Count in-progress (●) and awaiting-human (◐) that way. **An awaiting query counts only ticks whose status is not closed:** `tk close` does not clear the `awaiting` flag, so a closed tick keeps it forever and every hand-built sweep reports work the human answered days ago as still waiting on them. Filter on status first, `awaiting` second. **Ready is not `tk ready`** (it has no per-epic scope and counts the whole tracker): derive it from `tk graph <epic> --json` as open tasks whose blockers are all closed. **And readiness runs through the parent chain, not the tick's own `blocked_by`.** A tick parked under a future epic has an *empty* `blocked_by` — the blocking lives on its parent — so by its own record it looks ready the moment it is created, and the stall rule fires on its age. Measured 2026-09-21: a tick created at 11:06:23 under an epic blocked until 11:40:47 was reported "ready 35 min, no dispatch" at 11:41:42; its real reachable age was 55 seconds. **Switching to an unblock clock does not fix it** — that tick has no blocker whose clearing could be timed. A tick is not ready if its parent epic is blocked, or if that epic has not been planned into children. Streams park ticks under future epics deliberately; expect more of it. Ignore ◐ ticks from earlier increments that were never closed (they show in every worktree). |
| at checkpoint | **the stream's own** `.devmeta/increments/increment-<its id>/completion.md` exists — never a glob over `increments/*/`, which matches every finished increment in the tree and says yes for everyone. |
| implementer worktrees | `git worktree list` from the row's worktree, rows under `.ticks-worktrees/` whose branch is `tick/<one of its epics>/*`; for each, uncommitted lines (`git status --short | wc -l`) and commits ahead of the stream branch. |
| last movement | age of the stream branch's tip commit; age of the newest commit on any of its tick branches. |
| playwright | `pgrep -f "playwright tes[t]"` — then **check each match is a runner, not a watcher.** The bracket stops the pattern matching *its own* `pgrep`; it does nothing about other processes whose command line happens to contain the string, and the most common such process is a wait-loop somebody wrote to sit out a tier (`while pgrep -f "playwright test"; do sleep 15; done`). Read `/proc/<pid>/cmdline` for every match and **discard the shells**: a real tier is a `node` process under `node_modules`, not `/usr/bin/bash -c`. On 2026-09-21 the door reported the machine held for several minutes after a tier had finished, because two of the mainline's own wait-loops survived it — and those loops could never exit either, since each one's `pgrep` matched its own command line and then the other's. Three streams held off a tier for nothing, one of them about to build a page. **Reporting "held" when nothing runs is the mirror of reporting "free" while something does, and the door already forbids the second.** It is cheaper than the first only because it wastes other people's time instead of corrupting an artefact. | **A stream's tick worktrees under `.ticks-worktrees/` count as that stream's**, so a tier running in `nl-4xn` is held by the mainline, not by nobody. A running cwd that no row claims prints `held by <cwd>`; never print "free" while a process is running, whoever it belongs to — "free" is the word another session acts on. |
| progress | From the tick files, not `tk graph` (which counts only open tasks): for each of the increment's epics in roadmap order, its children (`parent == epic id`) and how many are closed. The increment's position is **the first epic not closed, out of the epic count** ("E1 of 3"); that epic's `closed/total` is the bar. Epics after it usually have zero children — the method plans just-in-time — so they show as "unplanned", never as 0%. **The current epic can have zero children too** (it was reached before it was cut): it is named unplanned as well, not "0/0". And **an increment whose every epic tick is closed reads 100%** whatever the last epic's children look like — a closed epic is closed; do not let a half-populated child list drag a finished increment back below the line. The `~%` column is the one increment-wide number, by Morten's formula (see Step 5); it is labelled rough and sits beside the glyphs that show the true shape. |

## Step 3 — Classify

Per stream, one word, by these rules in order:

- **checkpoint** — project tick open, `completion.md` present, no in-progress tick → waiting to be landed. **A stream at its checkpoint is a NEEDS YOU item, before and after the landing.** The method ends `/dmtix go` at the checkpoint and the close is the human's: they review, smoke-test, and give the close reason. Landing it does not discharge that — a landed stream whose project tick is still open is still waiting on them, and a status that prints `NEEDS YOU —` beside a row reading "at checkpoint" is contradicting itself. Say what they are being asked to look at and where. **It is the project tick at `awaiting: checkpoint` specifically, and it clears when that tick closes, not when the stream lands** — the fix must not make every stream permanently loud.
- **needs Morten** — any tick awaiting human, or a human item in the overview not yet answered.
- **unknown driver** — the branch or a tick branch moved **within the last 30 minutes** and **neither the row's named session nor any agent at the row's worktree is found** — the name is checked first and anywhere, since a session can drive a stream from another tree. Not a stall: someone is working and the seat cannot see who. **Never for a stream nobody has opened yet:** the cut writes the Active line and the brief and commits them, so a stream's branch always moved a minute ago and every stream is *born* matching this rule, for half an hour, before a session exists. Two tests, either exempting the row — its status still reads `cut, not started`, or every commit on its branch is the seat's own cut. The branch test is the measurable one; a status cell is a claim the starting session is meant to clear and sometimes does not. It matters because unknown drivers print *above* the table and are chased first: a signal that fires on every cut is one a seat learns to skim, and the night it means something is the night it gets skimmed. Report it first; the human usually knows (a session resumed from a transcript does not register with the others). If the row says the stream is the human's own, this is expected and is not reported.
- **stalled** — no in-progress tick, no implementer process, AND either (a) open ready ticks exist with no dispatch for more than 20 minutes, or (b) the session is `waiting` (ListAgents) or **`blocked` (herdr)** and the newest commit is older than 30 minutes — `blocked` means it is sitting on a prompt and will not move until a human answers in that pane, or (c) an implementer worktree has uncommitted work and **the stream's own session is absent from both sources** — the session named in the row, not an agent in the tick worktree; implementers are not herdr panes and are never seen there, so reading (c) the other way makes every live wave look stalled. or **(d) a tick whose branch is already merged into the stream branch is still open, with nothing in progress** — merged-and-gated but not closed, which is the one that hides best: the tree is green, so nothing reads as ready, so rules (a) and (b) stay silent while the session has in fact stopped. Check it directly: for each open tick, is `tick/<epic>/<id>` an ancestor of the stream branch? Rule (c) is off for the caller's own row and for a row the human drives. Say which rule fired.

**`idle` with undispatched work is the stall signature, and it is not the same as `working`.**
A session that is `working` has a run continuing; a session that is `idle` has ended a turn.
So `idle` + an unfinished epic + nothing dispatched means **the turn ended without starting
the next thing**, which is a stall even though nothing is broken and nobody is blocked.
Measured 2026-09-21: a stream said *"final review next"*, ended its turn, and sat 31 minutes;
the probe was what restarted it, and its own diagnosis was the shape the runner doc names —
**finishing a large body of work triggers the urge to summarise and hand back, and an epic
boundary is a waypoint, not a stopping point.** It wrote a good summary instead of starting
the next thing. So do not read a well-written hand-over as completion: *the report reads like
the end of the work* is the tell.

**A failed gate is a branch in the loop where closes get orphaned.** The same probe found two
ticks still `in_progress` that had been merged and gated: the wave gate went red, attention
moved to the repair tick, and the deferred closes fell through that gap. The stream would have
sworn the wave was closed. **`tk graph` is authoritative where anybody's recollection is
not** — so after any red gate, re-read the graph rather than the memory of what was merged.
This is stall rule (d) one step earlier: (d) catches *open* ticks whose branch is merged; this
catches *in-progress* ones, which look even more like work is happening.

**Point the silence check at whoever is furthest ahead.** That stream's silence costs the most and looks the most like concentration — twice on 2026-09-20 the furthest-ahead stream was the one nobody was watching.
- **running** — in-progress ticks or live implementer worktrees.
- **idle** — nothing open, nothing in flight (a scoped-not-started stream, a docs-only branch).

## When a stream is silent, probe before concluding

This door can see that a stream is idle; it can never see *why*, and the three reasons look
identical from outside — the session is blocked on a prompt, its tier is refusing, or the
account is. One word settles it: send the session, or the tier in question, **"reply ALIVE, no
tools"**. It answers in about three seconds and costs nothing.

A refusal's own text says nothing about its scope. On 2026-09-20 four implementers died on
sonnet 429s; the seat read that as account-wide and told four streams to hold for 45 minutes.
A one-word sonnet probe answered immediately — the limit had already lifted, and a haiku scout
and an opus dispatch had been running through the whole window. Report the probe's result, not
the 429's prose.

## Step 4 — Restart what is stalled, before you print

**A stall is not a line in a report. It is work that has stopped, and the seat's job is to
start it again** (Morten, 2026-09-20). So after Step 3 and before Step 5's screen: for every
stream classified **stalled**, message its session — say which rule fired, with the number, and
ask for one line back if it is mid-something. Then print, naming each stream you nudged.

The one exception: **a stream waiting on the human is not stalled and is never nudged.** Its
work has not stopped, it has been handed over. That is a NEEDS YOU item, and the human is the
only one who can clear it.

Two further exceptions keep their existing force: a row the human drives is the human's to
nudge, and the caller's own row is skipped.

Prefer asking to instructing. "`8ab` has been ready 21 minutes with nothing dispatched; one
line is enough if you are mid-something" gets a truthful answer, where "dispatch `8ab`" gets
compliance and sometimes a wrong dispatch. And when a stall has a shape that has been seen
before, name it — a session that recognises *the report reads like the end of the work* fixes
the cause, not the instance.

## Step 5 — Print

Exactly this shape. Column headers always; columns aligned; a `—` where a column does not
apply; nothing narrated between the header and the table. Prose, if any, goes **after**, and
only when something needs saying beyond what the table shows.

```
STREAMS · <date> <time>

NEEDS YOU
  <tick>   <stream>   <what to do, where, and what closes it>   (or "  —")

STALLED / UNKNOWN DRIVER
  <stream>   <which rule fired, with the number>            (or "  —")

STREAM     SESSION         STATE     EPICS   ~%    AT               IN FLIGHT                LAST   WHAT NOW                     PORTS
<name>     <session or "Morten's own">   <working|idle|blocked|—>   <one glyph per epic>   <rough %>   E<n> of <N> · <closed>/<total>   <n implementers, m lines | clean | —>   <age>   <one clause>   <block> · <host if any>
…

PLAYWRIGHT  free | held by <worktree>
```

**One table, one row per stream** — the session and the progress on the same line, so a
glance answers "who is on it and how far are they" together. EPICS and AT show the whole
increment's shape and the current epic's depth without pretending unequal epics are equal. **One glyph per epic, in roadmap order:** `●` closed;
the current epic by its tick fraction — `○` none closed, `◔` under a quarter, `◑` under
half, `◕` under all, `●` when its last tick closes; `○` for every epic after it (unplanned
is normal: the method plans just-in-time). **`~%` is a rough increment-wide estimate, by Morten's definition (2026-09-20):** every epic is
worth `100 / N`; a closed epic counts in full; the running epic counts `closed / total` of its
share; an unplanned epic counts zero. So `●◑○` with the middle epic at 3/6 is 33 + 17 + 0 =
50%. The tilde is part of the column name on purpose: epics are not equal-sized and the
running epic's total can still grow, so this is a reading, not a measurement. It is printed
because a rough number at a glance is worth having; the glyphs beside it are the honest shape.
AT is "E*n* of *N* · closed/total"; WHAT NOW is one clause on what is happening in that
epic — a wave running, scouts out, a review, "idle *n*m, *k* ticks left — watch". Never ticks-over-ticks: the `~%` column is the only increment-wide number, and it is by
the formula above.
The increment's title is not a column: the stream name says which is which, and the title
was the widest column for the least information. Rules for the table: the mainline first, then side streams in port order, then any docs-only
branch. STATE comes from herdr (working / idle / blocked) or `ListAgents`; `—` for a
hand-driven stream. WORK IN FLIGHT counts *live* implementer worktrees (touched within
30 min) and the lines uncommitted across them; "clean" when live worktrees exist with
nothing uncommitted; "docs only" for a branch with no ticks. LAST is the age of the newest
commit on the stream branch or any of its tick branches, whichever is newer. NEEDS YOU
leads with the tick id so the human can act on it without reading further — and the rest of
the line is **an instruction**. **DO is the tick's title** — the only imperative-shaped field
`tk show <id>` has — verbatim when it already reads as an act. When the title is third person
("the seed card is approved", "the tour is re-walked"), turn it into the act and change nothing
else ("approve the seed card", "re-walk the tour"); never invent a step the title does not
name. WHERE and CLOSES WHEN come from the rest of `tk show`: the description says where to look
(a route, a file, a screenshot) and the acceptance says what closes it (his approval quoted in
the close reason; a decision written into an overview; a value put on a host). Three parts, in this order, in plain words:

    <tick>   <stream>   DO <the act> · WHERE <session or path> · CLOSES WHEN <the acceptance>

    txj   inspiration   DO read the seed card's five parts and approve or reword them
                        · WHERE the inspiration session, or the PNGs under
                          apps/web/tests/ui/__screenshots__/inspiration-seed.spec.ts/
                        · CLOSES WHEN your words are in the close reason (--from human)

Wrap to three indented lines if it does not fit one. If the tick's description does not
say where or what closes it, say so — "(tick gives no location)" — rather than guessing;
that is a defect in the tick, and naming it gets it fixed.

## What this door never does

- Edit a stream's tree, dispatch its ticks, or decide anything the human should.
- Edit `streams.md`. If the table is wrong (a row for a landed stream, a missing row), say so
  and let the seat fix it with the update-ref procedure.
- Nudge, land or message a stream whose row says it is the human's own.

## Corrections from real runs

- 2026-09-21: **an unchanged baseline has three meanings, not two, and the file list can never
  say which.** (1) Nothing changed. (2) The change stayed under the tolerance — which is a
  ratio over a **full-page** capture, so the longer the page the blinder it is to its own
  chrome. (3) **The changed thing was not in frame.** The third was read, not inferred: two
  chat specs moved asymmetrically, and cropping the top 150 px of the phone baseline showed
  the inspiration chat opens there as a **drawer covering the masthead** — so a masthead change
  genuinely did not alter that render, and Playwright correctly left the file untouched while
  125 siblings were rewritten. The old symmetry heuristic reads all three as one. **Only
  reading a render distinguishes them**, so budget for reading renders wherever a state is
  small or sits under an overlay. Related and worth keeping: `--update-snapshots=all` rewrites
  files whose comparison *passed*, so where it leaves a file alone the render was identical
  rather than merely close — that is the one guarantee a forced pass gives.
  **Demonstrated rather than argued, 2026-09-21.** A four-line change added one link to
  `AppBar`, whose two flex groups are joined by `justify-between`, so the right group widens
  and its left edge moves — a diff confined to a band the height of the bar. **Twenty-seven
  `/app` captures took that identical change. Exactly two went red, and they are the two
  shortest captures on the list** — 3381 px and 3601 px, both measuring 0.02 against the 0.01
  cap. **About twenty-five changed for real and stayed green.** Same change, same band, and
  whether a picture notices depends *only* on how long that page happens to be. The competing
  explanation dies on the same evidence: had the bar wrapped to a new line, every phone
  capture would have shifted down and failed far above 2%. It did not. **Control and treatment
  in one run** — which is why this needs no second measurement to interpret, and why it is the
  entry to cite rather than the arithmetic.
  **And the dangerous case is not a baseline that moves unexpectedly; it is one that stays
  green while the page moves underneath it.** A moved baseline announces itself. A stale one
  waits for somebody else's regeneration and then **looks like their fault**. Measured the
  same day: a seeded-routing change altered one `Select`'s rendered option on
  `/admin/routing` — a dozen characters in one table cell — and the baseline stayed green
  under the tolerance. The tick that made the change reported the page "passed unchanged",
  which was true of the test and false of the page. So when a change *could* have touched a
  rendered surface, **read the render or reason from the component, and record the
  attribution on the tick**: the next regeneration will surface it, and without a note it is
  charged to whoever ran that regeneration.
  **A third state exists and is worse than both, because a regeneration does not fix it
  either: a baseline that was never compared at all.** When one test shoots more than one
  picture, a failed assertion before the second aborts the test, and that second baseline is
  not passing, not stale-but-green — it is **unexamined**, and the run reports nothing about
  it in either direction. Measured 2026-09-21: `admin.spec.ts` shoots a card at `:498` and
  the full page at `:526` inside one test; a caption change blew the card shot at all four
  projects, so the full-page shot was never reached. **Corrected 2026-09-21 by reading Playwright 1.63's source rather
  than waiting to measure it: a forced `--update-snapshots=all` pass DOES write both shots.**
  On a *missing* snapshot under `all`, `expect.js:12481-12484` writes the file and returns
  `createMatcherResult(message, true, …)` — `pass` is the second argument — so the assertion
  **passes and the test continues** to the second shot. The seat had written the opposite here
  and told a stream so ten minutes before it ran. **So the fourth state is real on a reading
  run**, where `toHaveScreenshot` throws and aborts — and a forced pass rescues it. The
  ordered-pair discipline still earns its place, for the other reason: **it protects the
  verification run, not the regeneration.** `.tick/config.md` already says a test that fails never reaches its screenshot;
  what it does not say is that **two pictures in one test make this reachable with nothing
  red at the end** — fix the first, and the second was never in the run. The rule is cheap:
  **when one test shoots more than one baseline, force the earlier one first and confirm the
  test runs to completion before reading the later one.**
  **And prove the picture was written rather than inferring it from a green exit** — *"the
  test passed" and "the picture was written" are different facts, and the second is the one
  you need.* **Corrected 2026-09-21, from the source, within the hour of being written here.** The seat
  recorded a three-bucket pre-pass manifest whose middle bucket — *new mtime, same hash =
  written and examined* — **cannot occur**. Under `all`, `expect.js:12645` sets `expected` to
  `void 0` before the browser is asked, so **no tolerance comparison happens at all**; `:12654`
  then compares bytes and calls `writeFiles` **only if they differ**, and byte-identical falls
  through to `handleMatching()` — pass, writing nothing. So **mtime changes if and only if the
  hash changes**: two states, not three, and mtime is corroboration of the hash rather than an
  independent signal. It **cannot prove a picture was examined**, which was the whole reason
  the seat asked for it. It also follows that `git status` *is* an accurate list of what was
  written under `all`, because Playwright never rewrites an identical file — so the argument
  that a manifest was needed to see past it was wrong too.
  **What actually proves the second shot was reached is the missing-snapshot path, not a
  manifest:** under `all` a missing snapshot passes and the test continues, so `same mtime`
  can only mean byte-identical. A pre-pass manifest still earns a smaller, real job — a stable
  before-state with per-file hashes, so a cause can be named per file and a wrong keep reverted
  against something known — but it is not the instrument it was billed as. **The step was
  right for the wrong mode**, which is the same conflation twice in one afternoon, by two
  different parties, about the same two modes.

- 2026-09-21: **"the machine is free" and "the window is open" are different sentences, and the
  seat said the first.** Having established that a stream's stuck wait-loops were not a running
  tier, the seat told it the Playwright lock was free. It read that as a go and started a
  340-baseline regeneration a minute before the hold request arrived — 17 baselines written,
  killed and reverted, reported unprompted. A statement about the process list is not a grant.
  Only the seat's explicit OPEN, after every stream has answered, is.
- 2026-09-21: **the hold file enforces the pre-correction version of the rule it enforces.**
  The prose was rewritten on 2026-09-20 from *no other browser* — which named the kind of
  process instead of the machine's state — after two sessions walked through that gap in one
  afternoon, one with a full Vitest suite and one with two production builds. **The file that
  implements it was never rewritten.** Its contract still says "no browser may run", and then
  says *do every other part of the tick and every other gate* — so an implementer whose gate
  list ends in the full suite is told **by the hold file** to run the second item on the seat's
  no-list. A "holding" from a stream with a live implementer is therefore not the same fact as
  a "holding" from a stream sitting on an undispatched chain: the first is a running agent the
  mechanism does not reach. **Ask which kind of holding it is.** And when a prose rule is
  corrected, the thing that enforces it is a second edit nobody remembers to make.

- 2026-09-21: **the door called two bash wait-loops a running Playwright tier.** The real run
  had exited; what `pgrep` still matched were the mainline's own watchers, each of which
  contained the literal string `playwright test` in its command line. Worse, those loops were
  themselves undeadable: each one's `pgrep -f "playwright test"` matched its own command line,
  so the condition could never go false and a second loop had been started on top of the
  first. The door reported the machine held, three other streams held off correctly and for
  nothing, and the session that owned the loops sat waiting on something that could not
  happen. **A pattern match over `ps` is a claim about what a string looks like; a PID is the
  process.** Step 2 now says to read `/proc/<pid>/cmdline` and discard the shells, and any
  wait a session writes should wait on a PID rather than a name.

- 2026-09-21: **the door could not tell an unscoped stream from a scoped one the seat had not
  noticed.** Both scoped streams had projects, epics and running implementer waves; the table
  still carried the `— (not scoped)` the cut door wrote an hour earlier, and the screen showed
  all three streams as *unscoped, docs only* — the two mid-wave indistinguishable from the one
  that genuinely had no increment. Epics now come from the stream's own
  `.devmeta/current-increment.md` **Roadmap** line, which the method writes per branch when it
  scopes. The table's cell is a cache and is treated as one. Same shape as the session cells,
  the stale table, and a two-day-old todo entry quoted as the state of a host: a cached answer
  presented as a measurement, this time in the instrument whose job is catching that.

- 2026-09-21: **this door demanded a match on a field that does not exist.** It said the
  driver is found by name, from `ListAgents` *or* `herdr api snapshot`. herdr's snapshot has
  no session name — only `terminal_title`, which this same door calls worthless two sentences
  later — and `ListAgents` is an agent tool a `tsx` CLI cannot call. The two look alike
  because Claude sets the terminal title from the session name, so they coincide often enough
  to pass a reading. **The seat wrote that rule, wrote a five-branch matching matrix on top of
  it, and only a stream that ran the snapshot instead of reading the door caught it.** Rule 1
  is now worktree-matching, with the unattributable agent on its own line and the
  `agent_session` UUID named as the durable handle. The lesson is the door's own: a
  specification written from the armchair is a claim, and this one had been standing in for a
  measurement since 2026-09-20.
- 2026-09-21: **the agent matcher used exact string equality while the Playwright matcher
  twenty lines away used a prefix.** A session that has `cd`'d into a subdirectory of its own
  worktree therefore reads as *no agent at all* — which is not hypothetical: the seat's own
  cwd was moved in and out of three worktrees that afternoon by its harness. Match on a
  prefix, and read `foreground_cwd` as well as `cwd` for a pane that has moved.

- 2026-09-21: **every session cell in the table was wrong twenty minutes after being written**,
  in three different ways — a session renamed itself and the old name bounced, a pane id
  changed when its pane was reopened, and a terminal title was whatever a human last typed.
  Read a row's driver from its **worktree** (the column beside the session cell); a `cwd`
  cannot drift from the tree it holds, while every name, title and pane id can and did. Match
  the stored name if it still resolves, fall back to the worktree, and treat the cell as a
  cache to refresh rather than a fact to report. `ListAgents`' `[ref]` survived the rename
  unchanged and is the handle worth storing.

- 2026-09-21: **the door did not read in the order it asks for.** "Step 5 — Restart what is
  stalled, **before you print**" sat after Step 4, Print, with the probe section wedged
  between them. A door read top to bottom therefore printed first and restarted afterwards,
  which is the opposite of what its own heading demanded, and the probe — the one-word check
  that tells a stall from a block — sat past the point where it was useful. Reordered:
  classify, probe, restart, print. Nothing changed but the sequence, and the sequence was the
  instruction.

- 2026-09-21, two streams cut onto an empty machine (`fh`). **The table was read from disk and
  the disk was stale.** The seat wrote both rows on master with `update-ref`, pushed them, and
  its own `streams:status` answered "nothing is running" — `--json` returned `[]` — because
  `update-ref` moves the ref without touching any working tree and Step 1 read the checkout's
  copy. The rows existed in the commit and on GitHub; only the bytes the reader opened were
  old. Step 1 now reads `git show master:.devmeta/streams.md`. This is the skill's own named
  failure, *a stream missing from the table is invisible*, reached through its own procedure —
  and the reason "verify on the thing" has to include *which* copy of the thing.
- 2026-09-21, same run: **a freshly cut stream read as an unknown driver**, one minute after
  the cut, on the seat's own commit. The cut moves the branch, so every stream is born
  matching the rule for thirty minutes. Exempted in Step 3. The seat had written into the
  table that "neither branch has moved" and the door contradicted it a minute later — a
  reminder that a sentence the seat writes about the machine is a claim, and the machine
  outranks it.
- 2026-09-21, same run: **the door printed a state with no session.** Both rows showed a live
  `blocked`/`idle` state resolved by cwd while the session column said `—`, because the table
  had not been told the names. That tells the human the door found somebody and will not say
  who. Step 2 now says to print the pane id and terminal title on a cwd match; `—` may only
  mean *nobody is there*.

- 2026-09-20, from building the command (08s4-pvp in `ai-newsletter`): writing this door as
  code found eight places it was underspecified, and two of them were defects every hand-built
  sweep had been shipping — a closed tick keeps its `awaiting` flag, so answered work was
  reported as still waiting on the human; and a stream's ticks were being read outside its own
  worktree, where the per-branch tracker gives a plausible wrong answer. Both are now stated in
  Step 2. The other six: DO's source, "recently" as a number, whose absence stall (c) means,
  the seat's own row, tick worktrees counting for Playwright, and a current epic with no
  children. **A door that has never been implemented has not been read carefully.**
- 2026-09-20, first run of the command: a stream whose driver sat in *another* worktree read
  as an unknown driver, because the door matched drivers by cwd and a driver dispatches ticks
  into trees it does not sit in. Fixed above: the row's session is matched by name, anywhere;
  cwd is the fallback. This is the same failure that let a row say "Morten's own" for three
  hours after he handed the stream on, and left it the one stream unwatched through an outage.
  Also seen: the duplicate-agents finding still fires on the seat itself when the door runs as
  a subprocess and cannot identify its own pane. The exclusion needs a handle the caller can
  pass, not an inference. **Specified in Step 2 on 2026-09-21** as `--self`, falling back to
  `HERDR_PANE_ID`: an open complaint in a door is a defect nobody owns, and this one sat for a
  day while two sessions worked around it.
- 2026-09-20, the 45-minute hold: see the probe section above.
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
