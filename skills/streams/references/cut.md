## Purpose

Set a new side stream up so its session can start from files alone. Everything the seat used
to do by hand, and the brief it used to write from memory.

Arguments: `cut <slug> [--from mainline|trunk] [--scope "<task>"]`. `slug` names the branch and
the worktree. The project's facts come from `coord.py config` (the trunk, the worktree place,
`## Resources`, `## At cut`, `## Standing rules`, `## Seams`); a fact the project file does not
name has the detected default `config` prints, and a section it does not have means nothing to
do.

**One name per stream (2026-09-23):** the slug *is* the stream's name — a short lowercase word
said in chat — and it **leads every label** the stream carries: the branch, the worktree (no
`side-`), the session's pane (named by `term.py start <worktree> <slug>`; no `/rename`), its row in `coord/streams.md`, and
whatever the project's issue tracker groups the stream's tasks under (a milestone `<slug> —
<title> (<id>)`, say). The increment id follows the name, never replaces it: *<slug> (<id>)*.
Streams cut before the rule keep their branches (renaming a live branch moves every tick's
base-branch stamp) but take the name in chat and in their session.

**Branch names put the slug first and the date last: `<slug>-<YYYY-MM-DD>`.** A mainline's slug
is `inc<NN>`. So `search-2026-09-21`, `inc09-2026-09-21` — never `2026-09-21-search`. Narrow
lists (a sidebar, `git worktree list`, a pane title) cut names off from the right, and several
streams cut on one day is normal, so the date is the least distinguishing part. (2026-09-21)
three date-first branches were identical for eleven characters in a sidebar that truncated
there — existing streams were not renamed; the convention changed for the next cut.

Default `--from mainline`: cut from the mainline's branch tip so the stream has the current
tree; `--from trunk` (the trunk, `coord.py config --get trunk`) when the stream must not carry
the mainline's unfinished work.

## Step 0 — Is this a side stream at all?

**When the table has no mainline row, stop and ask the human which this is**, because the
answer changes four things at once: the resources (the mainline's or a side stream's), whether
it may touch a deploy host, the increment id's form, and whether the Active line may say
"beside the mainline". Do not infer it from the argument. (2026-09-21) "a worktree to work
through the issues" on an empty machine meant the mainline, which the defaults would have made
a side stream.

- **The mainline, in a worktree of its own.** Id `<NN>-<xxx>`; the mainline's resources; it owns
  any deploy host. The main checkout then stays on the trunk driving nothing. Say that in the
  table's header — **a session sitting in the main checkout is the thing a seat will mistake for
  the mainline**, and the mistake is silent.
- **A side stream.** Id `<NN>s<k>-<xxx>`; the lowest free side-stream share of each resource;
  no host.

## Step 1 — Read the table, claim what the project names

From `<git common dir>/coord/streams.md`: the mainline's branch and host, and what each live row
claims. Then `coord.py config --get resources`: **a stream claims what `## Resources` names, and
nothing when it is absent.** Each line names a resource and its share for stream `k` (`api
port: 8000 + 10×k`, `redis db: k`, `staging: one at a time, held with a coord HOLD`). The new stream takes
the **lowest** `k` no *live* row holds — a landed stream's share is free again. Refuse if none is
free, saying which rows hold what. (2026-09-20) "next free" was read as "after the highest"
while the lowest was a landed stream's — lowest, not next.

## Step 2 — Branch and worktree

From the main checkout (read-only; never `git checkout` there):

```bash
tree=$(coord.py config --slug <slug> --get worktree)
git worktree add -b <slug>-<date> "$tree" <from-branch>
```

**A mainline in a worktree is named after its increment:** branch `inc<NN>-<date>`, worktree
`coord.py config --slug inc<NN> --get worktree`, so its slug `inc<NN>` leads both labels too. The worktree's name is the only label a
human reads in `git worktree list`, a pane title and `/proc/<pid>/cwd`.

Then in the worktree:
- **Resources.** Write the stream's share of each claimed resource where the project's
  `## Resources` says it goes (an env file's keys, say), and leave any resource the stream does
  not hold (a deploy host) unset with a line saying who holds it.
- **`## At cut`.** Run its lines in order (`coord.py config --get at-cut`): an install, an env
  file copied from the main checkout or its example. Absent, nothing.
- **Compact settings** per `references/compact.md`: `.claude/settings.local.json` with the
  auto-compact window for the stream's kind and the after-compaction hook.
- If `--from mainline`, `git merge <trunk>` so the cut also carries what landed on the trunk since
  the mainline last synced, and resolve by `## Seams` (an end-of-file record or a list file: keep
  both).

## Step 3 — Records

- **Active line.** Rewrite the block above `## Streams` in `.devmeta/current-increment.md` on
  the new branch: `**Active:** <increment id> — <title> (side stream beside the mainline <id>)`,
  overview path, status `NOT STARTED`, branch, worktree and claimed resources, and the sentence
  "This Active line is this branch's only: at landing keep the mainline's."
- **Increment id.** `<NN>s<k>-<xxx>`: `NN` the mainline's number, `k` the next side index in the
  table, `xxx` three random lowercase letters. A mainline's is `<NN>-<xxx>`.
- **If `--scope` names a task in the project's issue tracker: claim it with the project's own
  claim mechanism** (a label plus a claim comment naming the increment, say), refused when it is
  already claimed; nothing is written on the trunk for it. The overview names the tasks by
  number under `## Taken from the issues`.
- **If `--scope` names an entry in a task file: MARK it on the trunk, do not move it** (the
  human, 2026-09-21). Through a scratch worktree and `git update-ref` (never a `git checkout` in
  the main checkout), change its index line from `- [ ]` to `- [~] … — **<increment>**, taken
  <date>`. Nothing is deleted or copied; the overview **names** it under `## Taken from the
  todo`, **head-noted with what has aged** (below). **Before marking, check the entry is not
  already `[~]` on the trunk** — that is the whole prevention. The delete happens once, at the
  landing, into the done file with the date and where it landed. (2026-09-21) two streams
  scoping one entry wrote the same delete, which git merges cleanly — so mark, do not move.
- **The overview.** If the seat knows the scope well (designed in conversation), write the
  overview directly — Goal, Produces, Not included, Roadmap, Definitions of done, Exit criteria,
  How to run — and create the tk project and one epic with `tk create`, stamping
  `--base-branch` on the epic. Leave scoping to `/dmtix start` only when the scope is open.
- **The Streams row.** In `<git common dir>/coord/streams.md`, **in place**: add the row (session
  `<slug>` once its pane is open, `—` until then; status `cut, not started`;
  resources as claimed). No commit, no announcement: every worktree sees the file at once. Copy
  it to the scratchpad first, edit by exact match (never by line number), and **read the row
  back**.
- **Any commit the seat makes on the trunk at a cut** (a task-file mark) goes through a scratch
  worktree and `update-ref`. **Never let a failed edit reach a commit**:
  ```bash
  test -n "$(git diff --cached --name-only)" || { echo "nothing staged"; exit 1; }
  ```
  and verify on the trunk by reading the change back — a successful push is not evidence a
  change was made. Do not force-push to tidy a bad commit afterwards. Then put the main checkout
  back in line in the same breath, since `update-ref` touches no working tree:
  ```bash
  git -C <main checkout> restore --source=HEAD --staged --worktree <the files the commit changed>
  ```
  (2026-09-21) an aborted edit with a chained commit-and-push put two hollow commits on the
  trunk while a stream ran with no row.

## Step 4 — The brief

Write `docs/thoughts/<date>-<slug>-brief.md` on the new branch, then commit. It carries what the
new session cannot see:

1. Where it is: worktree, branch, cut point, the resources it holds, and what it does not hold
   (a deploy host) on purpose.
2. What to read first: its overview (or "run `/dmtix start` with the id `<id>` set by hand").
3. Its neighbours, from `coord/streams.md`: each stream's session, worktree, resources, and the
   files it owns — so a tick that wants one of them stops and asks.
4. The project's `## Standing rules` and `## Seams`, pasted as they are (`coord.py config --get
   standing-rules`, `--get seams`; never `## Scout`, which is the seat's); its `## Heavy runs` rules if it has them; and where
   coordination state lives: holds, deploys and hand-offs as lines in `coord/log.md` through
   `coord.py log` (a `HOLD` needs `--for` or `--until`); landing is the seat's.
5. Anything on a clock goes in `coord/schedules.md`, one row each, before it first fires, with
   its restart line; its script lives in the worktree, never only under `/tmp`
   (`references/restart.md`).
6. Anything specific the seat knows: a decision already made, a trap already found, a file the
   mainline has also touched.

**Every fact in a brief is a copy, and the seat must know which copy it took.** **Cite the
source for anything a stream will act on**, and when a stream measures one false, the brief is
the *least* important copy to fix: find where the claim came from and fix that too — the living
documentation may not age. (2026-09-21) a brief called a host's runner inert, quoting a
two-day-old task entry; it had been live for two days, and the same sentence was in the docs.

**An entry moved into an overview gets a head-note, as a matter of course**: at the **head** of
its section, what has been overruled, what was measured since, and the date — for every entry
moved. (2026-09-21) a moved entry led with a fix the human had just rejected, the note further
down.

**A task entry is not the state of the code.** Quote code from code; cite the entry as the
reason to look, never as the thing seen. And **a chosen value and a running value are different
things**: `grep` a host's env file for what somebody set, `docker exec … printenv` for what the
process has. (2026-09-21) a brief quoted a refusal sentence that is not in the code, for a case
that does not refuse.

Commit as `side(<slug>): cut from <from-branch> at <sha>; brief`.

## Step 5 — Open the stream's session

**The default is to open it** (the human, 2026-11-20: *"make it default in the skill"*). A cut
that only prints what to open leaves the human looking for a pane that is not there. Print the
block below instead only when the human said not to start it yet, or when no terminal server
answers (`term.py` exits 2); say which of the two it was.

Open it through `term.py`: herdr-core (`hc`) when it holds sessions, herdr otherwise
(`term.py which` says which; links in the README's example 7). Three steps, each checked before
the next:

```bash
# 1. Claude in a place of its own, in the worktree — never a tab in the seat's place: the human
#    looks for each stream as its own space. On herdr pass --workspace <the seat's workspace id>
#    so it opens as the repository's worktree, nested beside the other streams.
term.py start <the worktree> <slug> [--workspace <the seat's workspace id>] -- claude   # note the session id
term.py wait --timeout 60 <session>   # until Claude's prompt is up, before typing anything
# 2. No /rename: `start`'s label already names the pane (check it with `term.py ls --json`).
# 3. The start prompt: read the brief, then /dmtix start with the id by hand (or /dmtix go),
#    and bring the draft epics to the seat before any build. A research stream's prompt
#    says /research-loop charter <slug> instead, and to bring the draft charter to the human.
term.py send <session> 'You are the <slug> side stream (increment <id>) ...'
```

**Say "give `/dmtix start` the id by hand" in the start prompt whenever the stream is
unscoped**, and why: the Active line and the row already name that id, and a method that picks
its own leaves two ids for one increment.

**Do not end by asking the human for the session's name** — the human should not be the index.
`term.py ls --json` gives the session at that worktree with its state, id and label.

The block to print when the session is not opened:

```
Stream <id> cut. Open a terminal:
  cd <the worktree>
  claude
then: /dmtix go          (or /dmtix start with the id <id> given by hand, if not scoped;
                          or /research-loop charter <slug>, for a research stream)
The brief is docs/thoughts/<date>-<slug>-brief.md; tell the session to read it first.
```

Then check on the machine: `term.py ls --json` shows exactly one session whose `cwd` is the
worktree, `working`, and `/proc/<pid>/cwd` agrees. Set the row's session to `<slug>`, and log the
cut: `coord.py log "CUT <slug> (<id>): …"`, naming the session id.

- (2026-11-20) a cut that printed what to open, by the old default, left the human asking where
  the pane was — opening the session became the default.
- (2026-11-20) `/rename` sent through hc was answered as a chat message ("a built-in command, I
  can't run it"): `hc send` delivers `<hc from="t5">/rename replay</hc>`, so no slash command
  runs that way. The label from `start` already named the pane.
- (2026-11-20) the rename step was dropped (the human: the panes are named well, *"let's drop the
  internal rename"*); it had also failed on 11-05, when the rename and the start prompt sent back
  to back named the session `<slug>You are…` and the prompt never ran.
- (2026-11-05) a stream opened as a plain herdr workspace showed top-level, not under the
  repository — `term.py start --workspace` opens it as a worktree.
- (2026-11-05) a stream opened as a tab in the seat's workspace was moved while it ran, with the
  server's own pane-move, pane-close and rename commands — never start a second Claude in the
  other pane instead: that is two drivers on one tree.

## Field notes

- (2026-09-21) the door's three faults on an empty machine were invisible until it was walked end
  to end — walk a door on a machine whose shape it did not anticipate.
- (2026-09-20) a sync-forward at the cut conflicts on the Active line (keep the stream's) and on
  list files (keep both) when the trunk has moved — expected, not a defect.
