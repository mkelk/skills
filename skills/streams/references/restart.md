## Purpose

Bring back what runs on a clock after herdr, a Claude session, WSL or the machine stopped. The human, 2026-10-28:
*"keep a list of cronned tasks etc, that is running in the stream complex and in which streams - so we can restart, if
herdr/claude has been stopped"*.

The list is `<git common dir>/coord/schedules.md`, beside `streams.md` and `log.md`: shared by every worktree, never
committed, kept by the seat (the skill's `scripts/coord.py init` creates it with its three sections). The rule that
every stream keeps its own rows true is one of the standing rules in `.devmeta/streams.md`. The `status` door reads
its session-bound rows.

## What the file holds

Three sections, each a table:

| section | what is in it | what a stop does to it |
|---|---|---|
| **Survives a session stop (system)** | crontab lines, systemd user timers | nothing; a machine or WSL restart keeps them too (the crontab and the timers are the user's own) |
| **Dies with its session (restart by hand)** | CronCreate jobs, `/loop`, a `run_in_background` shell waiting for a time | gone with the session; a WSL restart also empties `/tmp`, so a script kept only there is gone too |
| **One-off waits** | a shell waiting once, today | ends on its own; the owner re-arms it if it still matters |

Each row: **what**, **owner** (the stream), **kind**, **when** (UTC), **script / prompt** (the file that brings it
back), **ends** (the condition that retires it), **restart** (how, in words a fresh session can follow). `same` in
the restart column means the row above's. A row that has ended is struck through (`~~what~~ ended <when>`) and
`status` leaves it out; delete struck rows at the weekly tidy.

## Step 1 — Read what should be running

```bash
cat "$(git rev-parse --path-format=absolute --git-common-dir)/coord/schedules.md"
crontab -l; systemctl --user list-timers --no-pager
```

Check the system section against `crontab -l` and the timers: a line in one and not the other is a finding
(installed by hand and never listed, or listed and never installed).

## Step 2 — Find what is missing

For each session-bound row:

- **A background shell:** is its script running? `pgrep -af <script name>` and read the cwd
  (`readlink /proc/<pid>/cwd`). Running → nothing to do.
- **A session cron or `/loop`:** invisible from outside the session. Ask the owner (`SendMessage`), or, when its
  session is gone, treat it as missing.
- **The owner's session is gone** (not in `ListAgents`, no agent in its worktree in herdr, or with herdr not
  running, no `claude` process whose cwd is its worktree): every row it owns is missing.

Has the row's **when** already passed today? Its restart says whether to run it at once or wait for the next one.

## Step 3 — Restart through the owner, never in its place

The seat does not run a stream's schedule for it. The owner's session holds the context, the guards and the budget
(a stream's runs may go through its own guard scripts and spending caps; a job the seat restarts outside them is a
paid or subscription call nobody approved).

- **The owner's session is alive:** `SendMessage` it: which rows are missing, and the row's restart line. Ask it to
  *check* first (`CronList`) and re-create only what is missing (see the correction below).
- **The owner's session is gone:** tell the human which pane to open (`cd <worktree> && claude --resume`, which keeps
  the session's crons, or `claude` when there is nothing to resume), and what to say first: *"read
  `coord/schedules.md`, check your rows, restart only what is missing, and confirm each in the coord log"*. A stream
  that keeps a resume note (a memory note or a resume file in its worktree) names it in its row.
- **The system section:** the human's, with `!` (the classifier refuses the seat a crontab write).

Log it with the skill's `scripts/coord.py`:

```bash
python3 ~/.claude/skills/streams/scripts/coord.py log "restart after <what stopped>: <rows> asked of <streams>" --as seat
python3 ~/.claude/skills/streams/scripts/coord.py log "OWED <stream>: confirm your schedules are running" --as seat
```

One `OWED` line for each owner not yet confirmed. Close each with `PAID <id>` when the owner's own coord line says
it is running.

## Step 4 — Keep the list true

- A stream that starts, changes or ends anything on a clock edits its own row in the same breath, and logs it.
- At `cut`: the brief says so. At landing or close: the stream's rows are struck through or moved to their next
  owner (a handover names the new owner in the row).
- A schedule's script lives in the stream's worktree, committed, never only under `/tmp`.
- `keep-running` reads `coord/schedules.md` on every pass: a row whose owner has closed, or whose **ends** condition
  has passed, is a row to strike.

## Corrections from real runs

- 2026-10-28, the first inventory: one stream's four daily jobs ran as background shells in its session, from
  scripts under `/tmp`. A herdr stop would have ended them silently and a WSL restart would have lost the scripts.
  Two session crons (two other streams' last reads) had died at an earlier session exit and were brought back only
  because each stream wrote a resume note.
- 2026-10-28 ~03:51 UTC, the first real restart (WSL, not the kernel): the crontab and timers came back by themselves;
  every detached or background shell was gone (one stream's four loops, two others' waits), and so was a script one
  stream kept under `/tmp`. **Session crons survived where the session was resumed** (`claude --resume`): three
  streams found theirs alive with the same ids, and re-creating one would have run it twice. So ask the owner to
  *check* first (`CronList`) and re-create only what is missing; restart processes by `pgrep`, never by assumption.
