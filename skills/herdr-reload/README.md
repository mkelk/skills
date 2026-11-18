# herdr-reload

After a Claude Code update, the sessions already running in your
[herdr-app](https://github.com/herdrdev/herdr-app) (or [herdr](https://herdr.dev)) terminals
are still on the old binary. A running process can't switch to a new executable, so
the only fix is to exit and resume. `/herdr-reload` does that for every idle session at once,
including the ones on machines herdr-app is connected to, and each conversation carries on.

## Use

```
/herdr-reload
```

It shows each Claude session with its running version and whether it would be restarted, and
asks before touching anything. Busy sessions and the one you're typing in are left alone.

The script also runs on its own:

```bash
python3 scripts/herdr-reload.py                 # dry run
python3 scripts/herdr-reload.py --apply         # restart every stale idle pane
python3 scripts/herdr-reload.py --apply t2      # just that session (machine/t5 on a connected machine)
python3 scripts/herdr-reload.py --force         # --apply, plus a restart note to each busy session
python3 scripts/herdr-reload.py --local         # leave connected machines alone
python3 scripts/herdr-reload.py --server herdr  # force the older herdr server (local only)
```

`/herdr-reload force` skips the confirmation. Busy sessions are never interrupted: their agent
gets a queued note telling it to finish its work and then ask you to restart the session.

Needs `hc` (herdr-core) or `herdr`, and `python3`. It resolves the current binary through
`mise` when mise is present, and works on Linux only, because it reads `/proc` (on a
connected machine too, through `hc exec --on`).

```bash
cd scripts && python3 -m unittest test_herdr_reload   # tests, no terminal server needed
```

## Install

```bash
npx skills add mkelk/skills --skill herdr-reload -g -a claude-code
```

## License

MIT.
