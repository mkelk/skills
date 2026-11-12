## Purpose

Keep the long-running stream sessions small. The human, 2026-10-27: some streams and the seat run for
weeks. A large context is fine in the middle of a piece of work, but they spend most of their time waiting, and
every wait adds to what each call resends. Measured that day, from each session's own transcript:

| session | context then | peak | running since |
|---|---|---|---|
| stream 1 | ~500k | ~835k | 2026-09-26 |
| stream 2 | ~275k | ~966k | 2026-09-24 |
| stream 3 | ~266k | ~903k | 2026-09-30 |
| stream 4 | ~183k | ~967k | 2026-10-01 |

Two costs follow. Every call rereads the whole context (cheap per token from the cache, but hundreds of calls a day).
And every wait longer than the cache's life (5 minutes, or 1 hour) writes the whole context to the cache again at
full price or more. For a session that mostly waits, the second is the bigger one.

## What Claude Code offers, and what it does not (checked 2026-10-27)

- **No session can compact itself.** No tool, skill, hook or scheduled task can run `/compact`.
- **The auto-compact point is a setting:** `autoCompactWindow` (100000 to 1000000 tokens) in a settings file, or
  the environment variable `CLAUDE_CODE_AUTO_COMPACT_WINDOW`. Without it, a 1M-context model compacts at about
  967k. Seen in the binary's settings schema, not only in the docs.
- **A `SessionStart` hook with matcher `compact`** runs after a compaction, and what it prints is added to the
  compacted context. No hook can steer what the compaction keeps.
- **Claude Code has its own idle compaction** ("Compacted while idle, before the prompt cache expired"). It is
  behind a server flag: `"idleCompaction": true` does not turn it on, only `false` turns it off. Don't count on it.
- **herdr can type into a session's pane** (`herdr agent prompt <pane> "<text>"`), and slash commands work there.
  It also shows each agent's state (`idle`, `done`, `working`). That is the one way to compact a session from
  outside, at a moment of the seat's choosing. **Without herdr** there is no way in from outside: the safety net
  below still holds, and the seat names the large, quiet streams to the human, who types `/compact` in each pane.

## The three parts

The scripts are in the skill's own `scripts/` directory. Below it is written `~/.claude/skills/streams`, where a
user-level install puts it; use the path the skill is installed at. A hook runs in the worktree, so give it the
absolute path, never one relative to the repository.

1. **A safety net in each stream's worktree:** `.claude/settings.local.json` (git ignores it) sets
   `"autoCompactWindow": 200000` for a build stream, so it compacts itself at 200k, not at 967k: its state lives in
   tk and the increment's files, and a smaller context costs less usage every turn. A discussion stream, whose work
   is the conversation until the spec is written, gets `300000` (the human, 2026-11-08). `cut` writes it into a new
   worktree. The seat's own checkout gets it too: the seat cannot safely be compacted from outside while it is
   working.
   **The seat is reminded instead** (the human, 2026-10-28): the main checkout's `settings.local.json` has a Stop
   hook, `scripts/seat-compact-reminder.py`, that reads the seat's context after every turn and, from 200k
   (`SEAT_COMPACT_REMIND_AT`), shows the human one line, *time to /compact when the streams are quiet*, again every
   further 30k (`SEAT_COMPACT_REMIND_STEP`), starting over after a compaction. It never blocks a turn.
   ```json
   "hooks": { "Stop": [ { "hooks": [
     { "type": "command", "command": "python3 ~/.claude/skills/streams/scripts/seat-compact-reminder.py" } ] } ] }
   ```
2. **The idle tidy, by the seat, twice a day at quiet times** (after the morning reads, about 10:00 the human's
   local time, and in the evening). Run it as part of `keep-running`, or on its own, from any checkout of the
   repository:
   ```bash
   python3 ~/.claude/skills/streams/scripts/compact-idle.py          # dry run: who would be compacted and why not
   python3 ~/.claude/skills/streams/scripts/compact-idle.py --apply  # send /compact to each that qualifies
   ```
   **Scheduled by the user crontab** (twice a day, e.g. 10:07 and 21:07 local time), so it doesn't depend on
   the seat being awake. `scripts/compact-cron.sh` takes the main checkout as its argument (or `$STREAMS_REPO`),
   sets PATH for cron, and appends each run to `<git common dir>/coord/compact.log`. The entry (installing it is
   the human's, since a crontab is persistence the classifier won't let a session add; list it in
   `coord/schedules.md` as the seat's):
   ```
   7 10,21 * * * ~/.claude/skills/streams/scripts/compact-cron.sh /path/to/main/checkout
   ```
   A session is compacted only when all of these hold. It is a stream's session in the live table
   (`coord/streams.md`), never the main checkout, so never the seat. herdr shows it `idle` or `done`. Its context
   is at least 150k (`--min-tokens`, or `COMPACT_MIN_TOKENS`). Its transcript has been quiet for 30 minutes
   (`--quiet-minutes`, or `COMPACT_QUIET_MINUTES`). No unexpired HOLD names it, as what is held or as the holder
   (read from the coord log with the skill's `scripts/coord.py`). Each `/compact` carries instructions on what to
   keep: who it is and its standing rules, the task and next step, what it waits for and from whom (with times),
   its open HOLD and OWED lines, the human's decisions with dates, and what it promised to report. Each send is
   logged to coord as the seat.
3. **The after-compaction hook in each stream's worktree,** in the same `settings.local.json`:
   ```json
   "hooks": { "SessionStart": [ { "matcher": "compact", "hooks": [
     { "type": "command", "command": "bash ~/.claude/skills/streams/scripts/after-compact.sh" } ] } ] }
   ```
   It prints the stream's row from the live table, its brief, its Active line, and `coord.py show` (open holds,
   what the seat owes, the newest log lines), and tells it to re-read them and the coord log before acting. Its
   state lives in files, so a compacted stream finds it there.

The settings file for a worktree, whole (a discussion stream: `300000`):
```json
{
  "autoCompactWindow": 200000,
  "hooks": {
    "SessionStart": [
      { "matcher": "compact", "hooks": [
        { "type": "command", "command": "bash ~/.claude/skills/streams/scripts/after-compact.sh" } ] }
    ]
  }
}
```
If the worktree already has a `settings.local.json`, merge these keys into it. Don't overwrite its permissions.

## What this door never does

- **Compact a session that is working, waiting on a permission, or holding a HOLD.** The script checks all three.
  A message to a stream wakes it, so it is no longer quiet: the next pass picks it up.
- **Compact the seat from outside.** The seat relies on the safety net, the reminder, and the human's own
  `/compact`.
- **Replace writing state down.** Compaction is only safe because streams keep their state in files: the coord
  log, their pages, commits and tk. A stream that keeps a promise only in its conversation will lose it. The hook
  tells it to ask the seat.

## Corrections from real runs

- 2026-10-27, the first runs. A stream at 68k (a trial with `--min-tokens 50000`) came back as a 2.3k-token
  summary, its four background tasks still running and the hook's text in place. The hook was added to a session
  that was already running and still fired, so `settings.local.json` changes are picked up live. Then three more
  at 183k, 275k and 500k. A 500k session takes minutes to compact, and herdr shows it `working` meanwhile.
- The hook must find the stream's row by its worktree as the table writes it (`~/git/<wt>`). In bash, `~` in a
  substitution's replacement expands back to `$HOME`, so the first version found no row. The tilde now goes
  through a variable.
