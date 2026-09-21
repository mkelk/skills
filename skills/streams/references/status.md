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
increment, session name, branch, worktree, ports, host and epics. If the file is
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

**So: `cwd`, prefix not exact, and `foreground_cwd` too.** One row per agent at most. The 2026-09-20 case this rule was written for — a driver dispatching ticks into trees it does not sit in — is real and gets a better answer than a name: **the driver's own cwd is itself one of the seat's known worktrees**, so it is attributed by asking which row's tree it sits in. An agent whose cwd is under **no** row's worktree is the genuinely unattributable one, and it gets **its own line** ("agent in no stream's tree", with its cwd) rather than being reported as an unknown driver on somebody's row.

**Store the `agent_session` UUID, not just the name.** It is stable across a rename — the one handle that is both durable and reachable from a CLI — and it turns the session cell from a claim into something checkable: *is the agent in this worktree still the session this row recorded?* Until a row carries one, **print the name as recorded, never as verified**, because nothing in the command can check it; that check belongs to a session with `ListAgents`, not to the CLI. Match by cwd = the row's worktree; this catches sessions that never registered with Claude's list (a resumed session, a pane opened by the human) and gives `blocked` as a first-class state, which `ListAgents` only shows as "waiting". **Two agents with the same cwd is a finding in itself, and it is the loudest one this door has** — report it; one checkout, one orchestrator. It is also the only identity claim answerable from `cwd` alone, which is why it survives every correction to the rest of this cell: two seats on one tree is the most dangerous state on the machine, and it needs no name to detect. **Except the seat's own pane:** the orchestrating session is often started in the main checkout and is one of the two. **The caller says who it is; the door does not guess.** A project command takes `--self <cwd or pane id>`, falling back to `HERDR_PANE_ID` when the flag is absent, so both ways of calling are right; a seat reading these steps by hand excludes the pane it is sitting in, which it knows for free. Inference was tried and failed twice — `herdr pane read <id>` to recognise its own prompt, which does not work when the door runs as a subprocess, and cwd matching, which is wrong the moment the seat steps into a stream's worktree to write records. **Excluding the caller must not swallow a real finding:** two *other* agents in one checkout is still reported, and the flag is shown wherever the door shows the command, or nobody passes it. Better still, start the seat in a directory of its own. **The caller is never read as a row's session or state** — excluding it must not then turn the seat's own stream into an "unknown driver". If another agent shares that cwd, it supplies the session and state; if none does, the row prints `—` in both columns and the unknown-driver rule is skipped for that row alone. The seat knows it is sitting there; saying so tells the human nothing. **When a row's driver is matched by cwd rather than by name, print what the machine knows — the pane id and the terminal's title — never `—`.** herdr gives both, and a row printing a live state beside an empty session says the door found somebody and will not name them. `—` in that column means *nobody is there*; it must never mean *somebody is there and the table has not been told their name*. Needs `tk` ≥ 0.31 for `tk herd`, but the snapshot is `herdr`'s own CLI and needs nothing. |
| its ticks | **Read them in the stream's own worktree, never anywhere else** — the tracker is per branch, so the same command in the main checkout answers about the mainline's ticks and looks entirely plausible. `tk list --status open` there. **The tracker is shared across every worktree of one repo, so filter by the stream's own epics** — a tick belongs to the stream if `tk show <id>` names one of its epics as parent. Count in-progress (●) and awaiting-human (◐) that way. **An awaiting query counts only ticks whose status is not closed:** `tk close` does not clear the `awaiting` flag, so a closed tick keeps it forever and every hand-built sweep reports work the human answered days ago as still waiting on them. Filter on status first, `awaiting` second. **Ready is not `tk ready`** (it has no per-epic scope and counts the whole tracker): derive it from `tk graph <epic> --json` as open tasks whose blockers are all closed. Ignore ◐ ticks from earlier increments that were never closed (they show in every worktree). |
| at checkpoint | **the stream's own** `.devmeta/increments/increment-<its id>/completion.md` exists — never a glob over `increments/*/`, which matches every finished increment in the tree and says yes for everyone. |
| implementer worktrees | `git worktree list` from the row's worktree, rows under `.ticks-worktrees/` whose branch is `tick/<one of its epics>/*`; for each, uncommitted lines (`git status --short | wc -l`) and commits ahead of the stream branch. |
| last movement | age of the stream branch's tip commit; age of the newest commit on any of its tick branches. |
| playwright | `pgrep -f "playwright tes[t]"` — if any, which worktree path it runs in. **A stream's tick worktrees under `.ticks-worktrees/` count as that stream's**, so a tier running in `nl-4xn` is held by the mainline, not by nobody. A running cwd that no row claims prints `held by <cwd>`; never print "free" while a process is running, whoever it belongs to — "free" is the word another session acts on. |
| progress | From the tick files, not `tk graph` (which counts only open tasks): for each of the increment's epics in roadmap order, its children (`parent == epic id`) and how many are closed. The increment's position is **the first epic not closed, out of the epic count** ("E1 of 3"); that epic's `closed/total` is the bar. Epics after it usually have zero children — the method plans just-in-time — so they show as "unplanned", never as 0%. **The current epic can have zero children too** (it was reached before it was cut): it is named unplanned as well, not "0/0". And **an increment whose every epic tick is closed reads 100%** whatever the last epic's children look like — a closed epic is closed; do not let a half-populated child list drag a finished increment back below the line. The `~%` column is the one increment-wide number, by Morten's formula (see Step 5); it is labelled rough and sits beside the glyphs that show the true shape. |

## Step 3 — Classify

Per stream, one word, by these rules in order:

- **checkpoint** — project tick open, `completion.md` present, no in-progress tick → waiting to be landed. **A stream at its checkpoint is a NEEDS YOU item, before and after the landing.** The method ends `/dmtix go` at the checkpoint and the close is the human's: they review, smoke-test, and give the close reason. Landing it does not discharge that — a landed stream whose project tick is still open is still waiting on them, and a status that prints `NEEDS YOU —` beside a row reading "at checkpoint" is contradicting itself. Say what they are being asked to look at and where. **It is the project tick at `awaiting: checkpoint` specifically, and it clears when that tick closes, not when the stream lands** — the fix must not make every stream permanently loud.
- **needs Morten** — any tick awaiting human, or a human item in the overview not yet answered.
- **unknown driver** — the branch or a tick branch moved **within the last 30 minutes** and **neither the row's named session nor any agent at the row's worktree is found** — the name is checked first and anywhere, since a session can drive a stream from another tree. Not a stall: someone is working and the seat cannot see who. **Never for a stream nobody has opened yet:** the cut writes the Active line and the brief and commits them, so a stream's branch always moved a minute ago and every stream is *born* matching this rule, for half an hour, before a session exists. Two tests, either exempting the row — its status still reads `cut, not started`, or every commit on its branch is the seat's own cut. The branch test is the measurable one; a status cell is a claim the starting session is meant to clear and sometimes does not. It matters because unknown drivers print *above* the table and are chased first: a signal that fires on every cut is one a seat learns to skim, and the night it means something is the night it gets skimmed. Report it first; the human usually knows (a session resumed from a transcript does not register with the others). If the row says the stream is the human's own, this is expected and is not reported.
- **stalled** — no in-progress tick, no implementer process, AND either (a) open ready ticks exist with no dispatch for more than 20 minutes, or (b) the session is `waiting` (ListAgents) or **`blocked` (herdr)** and the newest commit is older than 30 minutes — `blocked` means it is sitting on a prompt and will not move until a human answers in that pane, or (c) an implementer worktree has uncommitted work and **the stream's own session is absent from both sources** — the session named in the row, not an agent in the tick worktree; implementers are not herdr panes and are never seen there, so reading (c) the other way makes every live wave look stalled. or **(d) a tick whose branch is already merged into the stream branch is still open, with nothing in progress** — merged-and-gated but not closed, which is the one that hides best: the tree is green, so nothing reads as ready, so rules (a) and (b) stay silent while the session has in fact stopped. Check it directly: for each open tick, is `tick/<epic>/<id>` an ancestor of the stream branch? Rule (c) is off for the caller's own row and for a row the human drives. Say which rule fired.

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
