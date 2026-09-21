## Purpose

Set a new side stream up so its session can start from files alone. Everything the seat used
to do by hand, and the brief it used to write from memory.

Arguments: `cut <slug> [--from mainline|master] [--scope "<todo entry name>"]`. `slug` names
the branch and the worktree (`<repo>-side-<slug>` beside the main checkout).

**Branch names put the slug first and the date last: `<slug>-<YYYY-MM-DD>`.** A mainline's
slug is `inc<NN>`. So `prod-2026-09-21`, `todos-2026-09-21`, `inc09-2026-09-21` — never
`2026-09-21-side-prod`. **The date-first form is unreadable in every narrow list**, which is
where branch names are actually read: Morten's herdr sidebar on 2026-09-21 showed three
streams as `2026-09-21-side-…`, `2026-09-21-incre…` and `2026-09-21-side-…`, identical for
eleven characters and truncated exactly where they started to differ. A name is for telling
things apart, and a shared prefix is the one place that cannot happen. Several streams cut on
one day is the normal case, not the exception, so the date is the least distinguishing part
of the name and belongs at the end, where it still sorts and still says when. Default `--from mainline`: cut from the mainline's branch tip so the stream has the
current tree; `--from master` when the stream must not carry the mainline's unfinished work.

## Step 0 — Is this a side stream at all?

The door's name and every default in it assume a mainline is already running and this is a
stream *beside* it. **When the table has no mainline row, stop and ask the human which this
is**, because the answer changes four things at once and none of them is cheap to change
afterwards: the port block (3900–3919 or 39k0–39k9), whether it may touch the deploy host, the
increment id's form, and whether the Active line may say "beside the mainline" at all.

Two shapes, both legitimate:

- **The mainline, in a worktree of its own.** Id `<NN>-<xxx>`; ports 3900–3919 and Inngest
  8288; it owns the deploy host and may deploy. The main checkout then stays on `master`
  driving nothing. Say that in the table's header in as many words — **a session sitting in
  the main checkout is the thing a seat will mistake for the mainline**, and the mistake is
  silent.
- **A side stream.** Id `<NN>s<k>-<xxx>`; the lowest free `39k0–39k9`; no host, `DEPLOY_HOST`
  commented out.

Do not infer it from the argument. On 2026-09-21 the human asked for "a worktree to work
through the GitHub issues" on an empty machine; either reading was defensible, and the one he
wanted (the mainline, in a worktree) was the one the door's defaults would have got wrong.

## Step 1 — Read the table, claim a block

From `.devmeta/streams.md`: the mainline's branch and host, and every port block in use. The
new block is the **lowest** `39k0–39k9` (k ≥ 2) no *live* row holds — a landed stream's block
is free again (08s1 landed and 3920 was free while 3960 looked next; the first cut nearly took
3960). Refuse if none is free — say which rows hold what.

## Step 2 — Branch and worktree

From the main checkout (read-only; never `git checkout` there):

```bash
git worktree add -b <slug>-<date> ../<repo>-side-<slug> <from-branch>
```

**A mainline in a worktree is named after its increment, not after a slug:** branch
`inc<NN>-<date>`, worktree `<repo>-increment-<NN>`. The worktree's name is the only
label a human reads in `git worktree list`, in a pane title and in `/proc/<pid>/cwd`, so it
should say which branch lives there — that is one cheap half of the mapping problem the
SKILL names, paid for at the cut.

Then in the worktree: copy the main checkout's `.env`, set `WEB_PORT=39k0` and
`WORKER_PORT=39k1`, and comment `DEPLOY_HOST` out with a line saying the stream has no host
and the mainline owns the deploy host. Install deps (`pnpm install --frozen-lockfile`). If
`--from master`, `git merge <mainline branch>` and resolve the diary/todo seams keep-both.

## Step 3 — Records

- **Active line.** Rewrite the block above `## Streams` in `.devmeta/current-increment.md` on
  the new branch: `**Active:** <increment id> — <title> (side stream beside the mainline
  <id>)`, overview path, status `NOT STARTED`, branch and worktree and ports, and the
  sentence "This Active line is this branch's only: at landing keep the mainline's."
- **Increment id.** `<NN>s<k>-<xxx>`: `NN` the mainline's number, `k` the next side index in
  the table, `xxx` three random lowercase letters. **A mainline's is `<NN>-<xxx>`** — no `s`,
  no index — whether or not it runs in the main checkout.
- **If `--scope` names a todo entry:** move it whole (index line and details) from
  `todo/todo.md` into a new `.devmeta/increments/increment-<id>/_overview.md` under a
  `## Taken from the todo` heading, write the overview's skeleton (Goal, Produces, Not
  included, Roadmap, Definitions of done, Exit criteria, How to run) from it, and create the
  tk project and one epic with `tk create`, stamping `--base-branch` on the epic. Otherwise, if
  the seat already knows the scope well (it was designed in conversation and nothing is in the
  todo), write the overview directly — complete, with definitions of done — and create the tk
  project and epic; that is what the first cut did for the streams CLI. Only leave scoping to
  `/dmtix start` when the scope is genuinely open.
- **The Streams row.** On **master**, via a scratch worktree and `git update-ref`: add the row
  (session `—` until the human names it, status `cut, not started`), commit, push. Then
  `git merge master` into the new branch so it carries its own row. **This is the one merge
  into a stream's branch the seat ever does**, and it is safe only because it happens at the
  cut, before any session holds the tree. Every later table change is announced to the
  stream, never merged in by the seat — see the SKILL's principle on whose branch it is.
  **Then put the main checkout back in line, in the same breath:**
  ```bash
  git -C <main checkout> restore --source=HEAD --staged --worktree .devmeta/streams.md
  ```
  `update-ref` moves the ref and touches no working tree, so the main checkout is left holding
  the *old* file — and, worse, holding it as a staged modification it never made. Any door that
  reads the table from disk there then answers about a machine that no longer exists. On
  2026-09-21 the seat wrote two rows, pushed them, and its own `streams:status` printed an
  empty table with both streams live; `--json` returned `[]`. That is the SKILL's own named
  failure — *a stream missing from the table is invisible, not merely miscounted* — produced
  by this door's own procedure. The durable half of the fix belongs in `status.md` (read the
  ref, not the disk); this line is the half that keeps the checkout clean for whoever takes it
  next.

## Step 4 — The brief

Write `docs/thoughts/<date>-<slug>-brief.md` on the new branch, then commit. It carries what
the new session cannot see:

1. Where it is: worktree, branch, cut point, ports, `DEPLOY_HOST` unset on purpose.
2. What to read first: its overview (or "run `/dmtix start` with the id `<id>` set by hand").
3. Its neighbours, from `streams.md`: each stream's session name, worktree, ports, and the
   files it owns — so a tick that wants one of them stops and asks.
4. The standing rules, copied from `streams.md`'s footer (Playwright, seams, sync forward,
   landing is the seat's, tiers, the two rules).
5. Anything specific the seat knows: a decision already made, a trap already found, a file the
   mainline has also touched.

**Every fact in a brief is a copy, and the seat must know which copy it took.** A brief is
written fast, from the todo, the diary, a completion report and the seat's own memory — all
of which were true when written and none of which is checked at the moment of copying. So
**cite the source for anything a stream will act on**, and when a stream later measures one
of them false, the brief is the *least* important copy to fix: find where the claim came from
and check that too.

On 2026-09-21 a brief told a production stream that the host's model runner was the inert
default and one command remained. The stream measured the box: the runner had been live for
two days. The seat had quoted a todo entry written 48 hours earlier and reported it as the
state now. Correcting the brief would have closed the incident and left the fault in place —
**the same false sentence was in `docs/current/how/hosts.md`**, the living documentation, the
copy that has to be true. A brief is dated exploration and may age; `docs/current/` may not.

The check that was missing, and that belongs in any brief touching a host: **a chosen value
and a running value are different things.** `grep` the host's `.env` for what somebody set;
`docker exec … printenv` for what the process actually has. A value can be live by derivation
with nothing in the file at all, which is exactly how a runner ran for two days while three
documents said it was inert.

Commit as `side(<slug>): cut from <from-branch> at <sha>; brief`.

## Step 5 — Say what to open

Print, and stop:

```
Stream <id> cut. Open a terminal:
  cd ~/git/<repo>-<slug>
  claude
then: /dmtix go          (or /dmtix start with the id <id> given by hand, if not scoped)
The brief is docs/thoughts/<date>-<slug>-brief.md; tell the session to read it first.
```

**Say "give `/dmtix start` the id by hand" whenever the stream is unscoped**, and say why: the
Active line and the row already name that id and point at an `_overview.md` that does not
exist yet. A method that picks its own id leaves two ids for one increment, and the records go
quietly wrong rather than loudly.

**Do not end by asking the human for the session's name.** *The human should not be the
index* — that is the SKILL's own requirement, and herdr already answers half of it: once the
pane is open, `herdr api snapshot` gives an agent at that worktree with its `agent_status`,
`pane_id` and terminal title, and `status` resolves the driver from the worktree without
anyone being asked. Ask for a name only when herdr is not running (`~/.config/herdr/herdr.sock`
absent), and say that is why. The door still does not message the new session: it does not
exist yet.

## Corrections from real runs

- 2026-09-21: **branch names were date-first and therefore unreadable where they are read.**
  Three streams cut on one day gave `2026-09-21-side-prod`, `2026-09-21-side-todos` and
  `2026-09-21-increment-09` — identical for eleven characters, and a narrow sidebar truncates
  precisely where they begin to differ. Slug first, date last. **Existing running streams are
  not renamed for this**: a branch rename moves the worktree's head, the `--base-branch` stamp
  every provisioned tick carries, and any implementer worktree already cut from it. The
  convention changes for the next cut; the cost of applying it backwards is paid by whoever is
  mid-wave.
- 2026-09-21, cutting two streams onto an empty machine (`fh`): three faults, all in this
  door. **(1)** It had no answer for "there is no mainline yet" and its defaults would have
  made the human's mainline into a side stream — Step 0 now asks. **(2)** `update-ref` left
  the main checkout holding the old table as a staged modification, and `streams:status`
  printed an empty table over two live streams — Step 3 now realigns, and `status.md` now
  reads the ref. **(3)** Step 5 ended by asking the human for the session name, which is the
  indexing job the SKILL says must not be his; herdr already knows who sits in a worktree.
  All three were invisible until the door was walked end to end on a machine whose shape it
  did not anticipate.

- 2026-09-20, first cut (08s4-pvp, the streams CLI): the port rule said "next free" and the seat
  read it as "after the highest" — the lowest free block was 3920, a landed stream's. Reworded.
  No todo entry existed for a scope designed in conversation; the door now says to write the
  overview directly in that case. Step 3's "merge master into the new branch" conflicts on the
  Active line (keep the stream's) and the todo (keep both) when master has moved since the cut
  point — expected, not a defect.
