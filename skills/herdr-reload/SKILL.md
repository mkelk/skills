---
name: herdr-reload
description: Move running Claude Code sessions in herdr panes onto the newest installed claude binary. A running process cannot swap its executable, so each stale idle pane is exited and resumed with `claude --resume <session>` in the same pane, keeping the conversation. Dry run first, restart only on the user's go. Use when the user types /herdr-reload, or asks to get their herdr panes / running Claude sessions onto the latest Claude Code version after an update.
---

# herdr-reload — get running Claude panes onto the new binary

A new Claude Code install only affects sessions started afterwards. Panes that were already
running keep the binary they started with until they are restarted. This skill does that
restart for every herdr pane that needs it: `/exit`, then `claude --resume <same session>` in
the same pane.

The mechanics are in `scripts/herdr-reload.py` (next to this file). Run it; don't redo it by hand.

## Steps

1. **Dry run.** `python3 <skill-dir>/scripts/herdr-reload.py`
   It lists every Claude pane on the local herdr server with its running version and an
   action:
   - `reload`: idle, on an older binary (or one that was deleted), and herdr knows its
     session id. The `->` line is the exact command it will be restarted with (the original
     flags, minus any old `--resume`/`--continue`).
   - `ok`: already on the current binary.
   - `busy`: on an older binary and not `idle` (`working`, `blocked`, or `done`, which herdr shows
     for a finished turn that may still have background work). Never restarted. With
     `--force`, its agent gets a restart note instead (see below).
   - `skip`: with the reason. The pane running the script, which is your own, is always
     skipped.
2. **Show the user the list and ask before restarting.** Restarting interrupts their
   sessions. If they want only some of them, pass those pane ids. **Skip this step only
   when the user said `force`** (`/herdr-reload force`, "force reload", "just do it"). Then
   go straight to step 3 with `--force`.
3. **Apply.** `python3 <skill-dir>/scripts/herdr-reload.py --apply [pane-id ...]`
   It goes one pane at a time: sends `/exit` with `herdr agent prompt`, waits until the
   pane's shell is back in the foreground, then runs `herdr agent start <name> --kind claude
   --pane <id> -- <args>`. That gives the pane a live herdr agent name taken from its
   folder, and the command returns once Claude is ready. Each line then reports the version
   the pane is running now, or `FAILED` with the reason and the command to run by hand.

   **`--force`** does the same as `--apply` and also handles the `busy` panes: it queues a
   short `[herdr-reload]` note to each one's agent with `herdr agent prompt`. Claude Code
   queues typed input while it works. The note tells that agent to finish its current task
   and then ask the user to restart it (`/exit`, then `claude --resume <session>`). Nothing
   busy is interrupted or restarted. A `blocked` pane (sitting at a permission or question
   dialog) can't take the note, because herdr won't type into a dialog. Those come back as
   `NOT NOTIFIED`, so pass them on to the user yourself.
4. **Report** what was restarted, what was skipped and why, and any failure as it was
   printed. For your own pane, tell the user to `/exit` and run `claude --resume` themselves
   (or `claude -c` in the same folder).

## Things that can go wrong

- **Text sitting unsent in a pane's input box.** `/exit` lands after that text, so Claude
  doesn't exit, and the script reports `FAILED: did not exit`. Leave that pane for the user
  to deal with. Never send `ctrl+c` or clear their input to force it.
- **A pane that went busy between the dry run and `--apply`.** The plan is rebuilt on apply,
  so the pane shows up as `skip`.
- **Remote panes** (`herdr --remote`, `--machine`) are not covered. The script reads
  `/proc` on this machine, so it only handles the local server.
- **"Current binary"** is the one `mise which claude` resolves to (or `claude` on PATH if
  there's no mise). If the user just installed a new version and the dry run still shows the
  old one as current, the install isn't the active version yet. Fix that first.
