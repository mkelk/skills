## Purpose

Answer "what is running, is anything waiting for me, has anything stalled" in one screen,
from files and processes, never from memory and never by asking the sessions.

**If the project provides a status command, run it instead of Steps 1–3.** A project that has
worn this door long enough usually grows one (in `ai-newsletter`: `pnpm fp streams:status`,
`--json` for the parts). It reads the same sources in about a second and costs the seat
nothing, which is the whole point — the seat's context is the expensive thing on the machine.
Read its output, print Step 4's shape, and fall back to the steps below only when it is absent
or refuses a row. The steps stay here because they are the specification the command is
measured against, and because the seat must be able to answer without it.

## Step 1 — Read the table

`.devmeta/streams.md` in the current checkout (it is the same on every branch; if the checkout
is behind master, read master's with `git show master:.devmeta/streams.md`). Each row gives a
stream's increment, session name, branch, worktree, ports, host and epics. If the file is
missing, say so and stop — this door has nothing to stand on without it.

**The increment id may be in either the `stream` cell or the `increment` cell** (`08s3-pci` is
a stream name that is also an id). Match it in either. A row that lists epics but carries no id
in either cell is refused **by name** — say which row and what it is missing, and carry on with
the rest; a docs-only row (no epics, `—`) is exempt, since it has no increment to find.

## Step 2 — Measure each stream, on the thing

For every row, gather — all read-only, all from the machine, none from a message:

| what | how |
|---|---|
| its session | Two sources, and the second is the better one. (1) `ListAgents`: match the row's session name; gives busy / idle / waiting. (2) **`herdr api snapshot`** (when herdr runs — `~/.config/herdr/herdr.sock` exists): every agent with its `cwd` and `agent_status` (working / idle / **blocked**). **Match the row's session by name first, wherever it sits; match by cwd only when the row names no session.** A session can drive a stream it is not sitting in — it dispatches ticks into worktrees, and its own cwd may be another branch entirely — so cwd alone finds a driver only by luck. Match by cwd = the row's worktree; this catches sessions that never registered with Claude's list (a resumed session, a pane opened by the human) and gives `blocked` as a first-class state, which `ListAgents` only shows as "waiting". **Two agents with the same cwd is a finding in itself** — report it; one checkout, one orchestrator. **Except the seat's own pane:** the orchestrating session is often started in the main checkout and is one of the two; identify it first (`herdr pane read <id>` shows its own prompt) and exclude it. Better still, start the seat in a directory of its own. **The caller is never read as a row's session or state** — excluding it must not then turn the seat's own stream into an "unknown driver". If another agent shares that cwd, it supplies the session and state; if none does, the row prints `—` in both columns and the unknown-driver rule is skipped for that row alone. The seat knows it is sitting there; saying so tells the human nothing. Needs `tk` ≥ 0.31 for `tk herd`, but the snapshot is `herdr`'s own CLI and needs nothing. |
| its ticks | **Read them in the stream's own worktree, never anywhere else** — the tracker is per branch, so the same command in the main checkout answers about the mainline's ticks and looks entirely plausible. `tk list --status open` there. **The tracker is shared across every worktree of one repo, so filter by the stream's own epics** — a tick belongs to the stream if `tk show <id>` names one of its epics as parent. Count in-progress (●) and awaiting-human (◐) that way. **An awaiting query counts only ticks whose status is not closed:** `tk close` does not clear the `awaiting` flag, so a closed tick keeps it forever and every hand-built sweep reports work the human answered days ago as still waiting on them. Filter on status first, `awaiting` second. **Ready is not `tk ready`** (it has no per-epic scope and counts the whole tracker): derive it from `tk graph <epic> --json` as open tasks whose blockers are all closed. Ignore ◐ ticks from earlier increments that were never closed (they show in every worktree). |
| at checkpoint | **the stream's own** `.devmeta/increments/increment-<its id>/completion.md` exists — never a glob over `increments/*/`, which matches every finished increment in the tree and says yes for everyone. |
| implementer worktrees | `git worktree list` from the row's worktree, rows under `.ticks-worktrees/` whose branch is `tick/<one of its epics>/*`; for each, uncommitted lines (`git status --short | wc -l`) and commits ahead of the stream branch. |
| last movement | age of the stream branch's tip commit; age of the newest commit on any of its tick branches. |
| playwright | `pgrep -f "playwright tes[t]"` — if any, which worktree path it runs in. **A stream's tick worktrees under `.ticks-worktrees/` count as that stream's**, so a tier running in `nl-4xn` is held by the mainline, not by nobody. A running cwd that no row claims prints `held by <cwd>`; never print "free" while a process is running, whoever it belongs to — "free" is the word another session acts on. |
| progress | From the tick files, not `tk graph` (which counts only open tasks): for each of the increment's epics in roadmap order, its children (`parent == epic id`) and how many are closed. The increment's position is **the first epic not closed, out of the epic count** ("E1 of 3"); that epic's `closed/total` is the bar. Epics after it usually have zero children — the method plans just-in-time — so they show as "unplanned", never as 0%. **The current epic can have zero children too** (it was reached before it was cut): it is named unplanned as well, not "0/0". And **an increment whose every epic tick is closed reads 100%** whatever the last epic's children look like — a closed epic is closed; do not let a half-populated child list drag a finished increment back below the line. The `~%` column is the one increment-wide number, by Morten's formula (see Step 4); it is labelled rough and sits beside the glyphs that show the true shape. |

## Step 3 — Classify

Per stream, one word, by these rules in order:

- **checkpoint** — project tick open, `completion.md` present, no in-progress tick → waiting to be landed.
- **needs Morten** — any tick awaiting human, or a human item in the overview not yet answered.
- **unknown driver** — the branch or a tick branch moved **within the last 30 minutes** and **neither the row's named session nor any agent at the row's worktree is found** — the name is checked first and anywhere, since a session can drive a stream from another tree. Not a stall: someone is working and the seat cannot see who. Report it first; the human usually knows (a session resumed from a transcript does not register with the others). If the row says the stream is the human's own, this is expected and is not reported.
- **stalled** — no in-progress tick, no implementer process, AND either (a) open ready ticks exist with no dispatch for more than 20 minutes, or (b) the session is `waiting` (ListAgents) or **`blocked` (herdr)** and the newest commit is older than 30 minutes — `blocked` means it is sitting on a prompt and will not move until a human answers in that pane, or (c) an implementer worktree has uncommitted work and **the stream's own session is absent from both sources** — the session named in the row, not an agent in the tick worktree; implementers are not herdr panes and are never seen there, so reading (c) the other way makes every live wave look stalled. Rule (c) is off for the caller's own row and for a row the human drives. Say which rule fired.
- **running** — in-progress ticks or live implementer worktrees.
- **idle** — nothing open, nothing in flight (a scoped-not-started stream, a docs-only branch).

## Step 4 — Print

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

## What this door never does

- Message a session, except the one-word probe above when a stream is silent and the answer
  changes what the human is told. A stall is reported to the human; nudging is the seat's
  judgement.
- Edit `streams.md`. If the table is wrong (a row for a landed stream, a missing row), say so
  and let the seat fix it with the update-ref procedure.
- Nudge, land or message a stream whose row says it is the human's own.

## Corrections from real runs

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
  pass, not an inference.
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
