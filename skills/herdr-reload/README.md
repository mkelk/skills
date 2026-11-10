# herdr-reload

After a Claude Code update, the sessions already running in your [herdr](https://herdr.dev)
panes are still on the old binary. A running process can't switch to a new executable, so
the only fix is to exit and resume. `/herdr-reload` does that for every idle pane at once,
and each conversation carries on.

## Use

```
/herdr-reload
```

It shows each Claude pane with its running version and whether it would be restarted, and
asks before touching anything. Busy panes and the pane you're typing in are left alone.

The script also runs on its own:

```bash
python3 scripts/herdr-reload.py                 # dry run
python3 scripts/herdr-reload.py --apply         # restart every stale idle pane
python3 scripts/herdr-reload.py --apply wY:p6   # just that pane
python3 scripts/herdr-reload.py --force         # --apply, plus a restart note to each busy pane
```

`/herdr-reload force` skips the confirmation. Busy panes are never interrupted: their agent
gets a queued note telling it to finish its work and then ask you to restart the session.

Needs `herdr` and `python3`. It resolves the current binary through `mise` when mise is
present, and works on Linux only, because it reads `/proc`.

## Install

```bash
npx skills add mkelk/skills --skill herdr-reload -g -a claude-code
```

## License

MIT.
