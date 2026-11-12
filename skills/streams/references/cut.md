## Purpose

Set a new side stream up so its session can start from files alone. Everything the seat used
to do by hand, and the brief it used to write from memory.

Arguments: `cut <slug> [--from mainline|master] [--scope "<task>"]`. `slug` names
the branch and the worktree (`<repo>-<slug>` beside the main checkout).

**One name per stream (2026-09-23):** the slug *is* the stream's name — a short lowercase word
said in chat — and it **leads every label** the stream carries: the branch, the worktree
(`<repo>-<slug>`, no `side-`), the session (`/rename <slug>` in its pane), its row in
`coord/streams.md`, and whatever the project's issue tracker groups the stream's tasks under (a
milestone `<slug> — <title> (<id>)`, say). The increment id follows the name, never replaces it:
*<slug> (<id>)*. The places names are read — the herdr sidebar, `git worktree list`, a pane
title, a milestone list — cut them off from the right, the same reason the branch rule below
gives. Streams cut before the rule keep their branches and worktrees (renaming a live branch
moves every tick's base-branch stamp) but take the name in chat and in their session.

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

From `<git common dir>/coord/streams.md` (`git rev-parse --path-format=absolute
--git-common-dir`): the mainline's branch and host, and every port block in use. The
new block is the **lowest** `39k0–39k9` (k ≥ 2) no *live* row holds — a landed stream's block
is free again (08s1 landed and 3920 was free while 3960 looked next; the first cut nearly took
3960). Refuse if none is free — say which rows hold what.

## Step 2 — Branch and worktree

From the main checkout (read-only; never `git checkout` there):

```bash
git worktree add -b <slug>-<date> ../<repo>-<slug> <from-branch>
```

**A mainline in a worktree is named after its increment, not after a slug:** branch
`inc<NN>-<date>`, worktree `<repo>-increment-<NN>`. The worktree's name is the only
label a human reads in `git worktree list`, in a pane title and in `/proc/<pid>/cwd`, so it
should say which branch lives there — that is one cheap half of the mapping problem the
SKILL names, paid for at the cut.

Then in the worktree: copy the main checkout's `.env`, set `WEB_PORT=39k0` and
`WORKER_PORT=39k1`, and comment `DEPLOY_HOST` out with a line saying the stream has no host
and the mainline owns the deploy host. Install deps (`pnpm install --frozen-lockfile`). Write
the worktree's compact settings per `references/compact.md`: a `.claude/settings.local.json`
with the auto-compact window for the stream's kind (a build stream's is smaller than a
discussion stream's) and the after-compaction hook. If `--from master`, `git merge <mainline
branch>` and resolve the diary/todo seams keep-both.

## Step 3 — Records

- **Active line.** Rewrite the block above `## Streams` in `.devmeta/current-increment.md` on
  the new branch: `**Active:** <increment id> — <title> (side stream beside the mainline
  <id>)`, overview path, status `NOT STARTED`, branch and worktree and ports, and the
  sentence "This Active line is this branch's only: at landing keep the mainline's."
- **Increment id.** `<NN>s<k>-<xxx>`: `NN` the mainline's number, `k` the next side index in
  the table, `xxx` three random lowercase letters. **A mainline's is `<NN>-<xxx>`** — no `s`,
  no index — whether or not it runs in the main checkout.
- **If `--scope` names a task in the project's issue tracker: claim it with the project's own
  claim mechanism** (a label plus a claim comment naming the increment, say), refused when the
  task is already claimed; nothing is written on `master` for it. The overview names the tasks
  by number under `## Taken from the issues`. This is the same rule as the file-based one below
  — mark, do not move; check the claim before taking it — with the tracker as the one home; a
  project moved its tasks from a file in git to the tracker on 2026-09-23, and the file-based
  rule is kept for its reasoning and for projects that still keep their tasks in a file.
- **If `--scope` names a todo entry in a file: MARK it on `master`, do not move it.** (The
  human, 2026-09-21; the rule lived in the project's `CLAUDE.md` → *Todo, one home per task*.)
  On `master`, in a commit made through a scratch worktree and `git update-ref` (never a
  `git checkout` in the main checkout), change the entry's index line from
  `- [ ]` to `- [~] … — **<increment>**, taken <date>`. **Nothing is deleted and nothing is
  copied.** The new `.devmeta/increments/increment-<id>/_overview.md` **names** the entries
  under a `## Taken from the todo` heading, **each head-noted with what has aged** — the text
  stays in the todo file (`todo.md`), which every worktree already has.
  **Before marking, check the entry is not already `[~]` on `master`.** That is the whole
  prevention: a stream that syncs forward sees a claim before it scopes. Marking on the
  stream's branch instead buys only late detection, and moving buys none at all — two streams
  scoping one entry used to write the *same delete*, which git merges cleanly.
  **The delete happens once, at the landing**, by the stream that finished it, into
  the done file (`todo.done.md`) with the date and where it landed.
  **Transitional, until the streams cut before 2026-09-21 have landed:** those streams still
  carry deletes on their branches while `master` carries the mark. At their landing the
  resolution is the same either way — the entry is done, so it moves to `todo.done.md` — but
  expect a conflict there rather than a clean delete, and resolve it as *done*, not as *keep*.
  Then write the overview's skeleton (Goal, Produces, Not
  included, Roadmap, Definitions of done, Exit criteria, How to run) from it, and create the
  tk project and one epic with `tk create`, stamping `--base-branch` on the epic. Otherwise, if
  the seat already knows the scope well (it was designed in conversation and nothing is in the
  todo), write the overview directly — complete, with definitions of done — and create the tk
  project and epic; that is what the first cut did for the streams CLI. Only leave scoping to
  `/dmtix start` when the scope is genuinely open.
- **The Streams row.** In `<git common dir>/coord/streams.md`, **in place**: add the row
  (session `<slug>` once its pane is open and renamed, `—` until then; status `cut, not
  started`). No commit, no `update-ref`, no merge into the new branch and no announcement: the
  file is one file for every worktree of the repository on this machine, so the new stream's
  tree already sees its own row. Copy the file to the session scratchpad first, edit by exact
  match (never by line number), and **read the row back**. (Since 2026-09-23. Until then the row
  was committed on `master` through a scratch worktree and `git update-ref`, and the seat then
  merged `master` into the new branch so it carried its own row — the one merge into a
  stream's branch the seat ever did, safe only because it happened at the cut, before any
  session held the tree. A day on which the table churned through a commit per row is what
  moved it out of git.)
- **Any commit the seat makes on `master` at a cut** — the todo mark above, in a project that
  keeps one — still goes through a scratch worktree and `update-ref`, and the two faults that
  procedure produced on 2026-09-21, when the row itself was committed that way, apply to every
  such commit.
  **Never let a failed edit reach a commit.** Between editing and committing, assert that
  something is actually staged and stop if not:
  ```bash
  test -n "$(git diff --cached --name-only)" || { echo "nothing staged"; exit 1; }
  ```
  On 2026-09-21 the seat pushed **two** hollow commits this way — `8759931` and `fa9ec93` —
  each carrying a message describing a row it did not contain. A failed assertion in the edit
  script aborted the write, and the commit-and-push chain after it ran anyway on an unchanged
  tree. Both times a stream was live on disk with **no row**, which is the state this skill
  names first: invisible, not merely miscounted. The push output says `master -> master` and
  looks exactly like success. **Verify the change is on master by reading it back** — a push that
  succeeded is not evidence that a change was made. Do not rewrite the bad commits afterwards:
  with streams running and possibly fetched, a force-push to tidy a message is the worse trade,
  and the history is more honest with the mistake and its correction both visible.

  **Then put the main checkout back in line, in the same breath:**
  ```bash
  git -C <main checkout> restore --source=HEAD --staged --worktree <the files the commit changed>
  ```
  `update-ref` moves the ref and touches no working tree, so the main checkout is left holding
  the *old* file — and, worse, holding it as a staged modification it never made. Any door that
  reads the table from disk there then answers about a machine that no longer exists. On
  2026-09-21 the seat wrote two rows, pushed them, and its own status command printed an
  empty table with both streams live; `--json` returned `[]`. That is the SKILL's own named
  failure — *a stream missing from the table is invisible, not merely miscounted* — produced
  by this door's own procedure. The durable half of the fix was to read the ref, not the
  disk, and the row's move to `coord/streams.md` has since removed the stale copy altogether;
  this line is the half that still keeps the checkout clean, for any file an `update-ref`
  commit touches, for whoever takes it next.

## Step 4 — The brief

Write `docs/thoughts/<date>-<slug>-brief.md` on the new branch, then commit. It carries what
the new session cannot see:

1. Where it is: worktree, branch, cut point, ports, `DEPLOY_HOST` unset on purpose.
2. What to read first: its overview (or "run `/dmtix start` with the id `<id>` set by hand").
3. Its neighbours, from `coord/streams.md`: each stream's session name, worktree, ports, and
   the files it owns — so a tick that wants one of them stops and asks.
4. The standing rules, copied from `.devmeta/streams.md`'s footer (Playwright, seams, sync
   forward, landing is the seat's, tiers, the two rules), and where coordination state lives:
   holds, deploys and hand-offs as lines in `coord/log.md` through the skill's
   `scripts/coord.py log` (a `HOLD` needs `--for` or `--until`).
5. Anything on a clock goes in `<git common dir>/coord/schedules.md`, one row each, before it
   first fires, with its restart line; its script lives in the worktree, never only under
   `/tmp` (`references/restart.md`).
6. Anything specific the seat knows: a decision already made, a trap already found, a file the
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
**the same false sentence was in the project's page on its hosts**, the living documentation,
the copy that has to be true. A brief is dated exploration and may age; the living
documentation may not.

**An entry moved into an overview gets a head-note, as a matter of course.** A todo entry is
written as if it were current — that is what makes it readable and what makes it dangerous a
week later. One moved on 2026-09-21 carried three claims that had aged in two days, including
a *prescribed fix Morten had just rejected*; the note saying so was put further down, where a
reader meets the rejected plan first. So: when `--scope` moves an entry, put the note at the
**head** of its section — what has been overruled, what was measured since, and the date — and
do it for every entry moved, not only the ones already known to be stale. The entry's own
prose cannot warn anyone; only the head-note can.

**A todo entry is not the state of the code, and this is the mistake the seat keeps making.**
On 2026-09-21 two briefs passed a stale entry to a stream as current fact: one said a host's
model runner was inert when it had been live for two days, and one described a chat's failure
mode from an entry's prose — quoting a refusal sentence **that is not in the code**, for a case
that **does not refuse at all** (the runner is built outside the try, the constructor throws,
the component awaits with no catch, and the visitor's message sits in the transcript with
nothing after it). Both were caught by streams reading the tree instead of the brief. An entry
is a record of what someone observed *when they wrote it*, and the fresher the entry looks the
more dangerous it is. **Quote code from code; cite the entry as the reason to look, never as
the thing seen.**

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
then: /rename <slug>
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

### Or start it yourself, when the human says so

When the human has asked the seat to start the stream (2026-11-05: *"cut a stream … and then
start it when it is the right time"*), open it through herdr instead of printing the block
above. Four steps, each checked before the next:

```bash
# 1. A workspace of its own, in the worktree. Never a tab in the seat's workspace: the human
#    looks for each stream as its own workspace, and opens a second pane on the same tree
#    when it is not there.
#    Open it as the repository's worktree, so herdr nests it under the repository's workspace
#    beside the other streams; `herdr workspace create --cwd` makes a top-level workspace with
#    no repository link instead.
herdr worktree open --workspace <the seat's workspace id> --path ~/git/<repo>-<slug> --label <slug> --no-focus   # note the root pane id
# 2. Claude in that pane.
herdr agent start <slug> --kind claude --pane <pane id>
# 3. The name first, ALONE. Wait until the pane shows "Session renamed to: <slug>" before step 4.
herdr agent prompt <pane id> '/rename <slug>'
herdr pane read <pane id>          # repeat until the rename line is there
# 4. The start prompt: read the brief, then /dmtix start with the id by hand (or /dmtix go),
#    and bring the draft epics to the seat before any build.
herdr agent prompt <pane id> 'You are the <slug> side stream (increment <id>) ...'
```

Then check on the machine: `herdr api snapshot` shows exactly one agent whose `cwd` is the
worktree, `working`, and `/proc/<pid>/cwd` agrees. Set the row's session to `<slug>` in
`coord/streams.md`, and write the cut as one line in `coord/log.md` (the skill's
`scripts/coord.py log "CUT <slug> (<id>): …"`).

**When herdr is not running** (`~/.config/herdr/herdr.sock` absent), the seat has no pane to
open: print the block above, say that is why, and stop. Once the human has opened it, the
process list (a `claude` whose `/proc/<pid>/cwd` is the worktree) or `ListAgents` shows the
session, and the row's session is set from that.

- **Send the rename alone and wait for it.** On 2026-11-05 the seat sent `/rename <slug>` and
  the start prompt back to back; the second was typed into the first, the session was named
  `<slug>You are the <slug> side stream…`, and the start prompt never ran. A second `/rename`
  and a resend fixed it.
- **Use `herdr worktree open`, not `herdr workspace create --cwd`.** On 2026-11-05 the seat
  opened a stream with `workspace create`; it showed as its own top-level space, not under the
  repository with the other streams, and the human asked for it there. `herdr worktree open
  --workspace <seat ws> --path ~/git/<repo>-<slug> --label <slug>` on the running workspace
  linked it in place (`already_open: true`), the session untouched.
- **A stream started in the seat's workspace can be moved while it runs.** The same day the seat
  opened another stream as a tab in its own workspace; the human looked for that stream's
  workspace, found none, and opened an empty one on the same worktree. The fix kept the session
  alive: `herdr pane move <old pane> --tab <new workspace's tab> --split right`, then
  `herdr pane close <the empty shell pane>`, then `herdr workspace rename <ws> <slug>`. herdr
  closes the emptied tab by itself, and the moved pane gets a new id. Never start a second
  Claude in the other pane instead: that is two drivers on one tree.

## Corrections from real runs

- 2026-09-21: **branch names were date-first and therefore unreadable where they are read.**
  Three streams cut on one day gave `2026-09-21-side-prod`, `2026-09-21-side-todos` and
  `2026-09-21-increment-09` — identical for eleven characters, and a narrow sidebar truncates
  precisely where they begin to differ. Slug first, date last. **Existing running streams are
  not renamed for this**: a branch rename moves the worktree's head, the `--base-branch` stamp
  every provisioned tick carries, and any implementer worktree already cut from it. The
  convention changes for the next cut; the cost of applying it backwards is paid by whoever is
  mid-wave.
- 2026-09-21, cutting two streams onto an empty machine: three faults, all in this
  door. **(1)** It had no answer for "there is no mainline yet" and its defaults would have
  made the human's mainline into a side stream — Step 0 now asks. **(2)** `update-ref` left
  the main checkout holding the old table as a staged modification, and the status command
  printed an empty table over two live streams — Step 3 now realigns, and `status.md` now
  reads the ref (the row has since moved to `coord/streams.md`). **(3)** Step 5 ended by asking the human for the session name, which is the
  indexing job the SKILL says must not be his; herdr already knows who sits in a worktree.
  All three were invisible until the door was walked end to end on a machine whose shape it
  did not anticipate.

- 2026-09-20, first cut (08s4-pvp, the streams CLI): the port rule said "next free" and the seat
  read it as "after the highest" — the lowest free block was 3920, a landed stream's. Reworded.
  No todo entry existed for a scope designed in conversation; the door now says to write the
  overview directly in that case. Step 3's "merge master into the new branch" conflicts on the
  Active line (keep the stream's) and the todo (keep both) when master has moved since the cut
  point — expected, not a defect.
