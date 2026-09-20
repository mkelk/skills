## Purpose

Set a new side stream up so its session can start from files alone. Everything the seat used
to do by hand, and the brief it used to write from memory.

Arguments: `cut <slug> [--from mainline|master] [--scope "<todo entry name>"]`. `slug` names
the branch (`YYYY-MM-DD-side-<slug>`) and the worktree (`<repo>-side-<slug>` beside the main
checkout). Default `--from mainline`: cut from the mainline's branch tip so the stream has the
current tree; `--from master` when the stream must not carry the mainline's unfinished work.

## Step 1 — Read the table, claim a block

From `.devmeta/streams.md`: the mainline's branch and host, and every port block in use. The
new block is the lowest `39k0–39k9` (k ≥ 2) no row holds. Refuse if none is free — say which
rows hold what.

## Step 2 — Branch and worktree

From the main checkout (read-only; never `git checkout` there):

```bash
git worktree add -b <date>-side-<slug> ../<repo>-side-<slug> <from-branch>
```

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
  the table, `xxx` three random lowercase letters.
- **If `--scope` names a todo entry:** move it whole (index line and details) from
  `todo/todo.md` into a new `.devmeta/increments/increment-<id>/_overview.md` under a
  `## Taken from the todo` heading, write the overview's skeleton (Goal, Produces, Not
  included, Roadmap, Definitions of done, Exit criteria, How to run) from it, and create the
  tk project and one epic with `tk create`, stamping `--base-branch` on the epic. Otherwise
  leave scoping to `/dmtix start` in the worktree and say so.
- **The Streams row.** On **master**, via a scratch worktree and `git update-ref`: add the row
  (session `—` until the human names it, status `cut`), commit, push. Then `git merge master`
  into the new branch so it carries its own row.

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

Commit as `side(<slug>): cut from <from-branch> at <sha>; brief`.

## Step 5 — Say what to open

Print, and stop:

```
Stream <id> cut. Open a terminal:
  cd ~/git/<repo>-side-<slug>
  claude
then: /dmtix go          (or /dmtix start, if not scoped)
The brief is docs/thoughts/<date>-<slug>-brief.md; tell the session to read it first.
Once you know the session's name, tell me and I will put it in the table.
```

The door does not message the new session: it does not exist yet, and the human names it.
