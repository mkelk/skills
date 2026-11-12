# skills

Agent skills by [@mkelk](https://github.com/mkelk), installable with the
[`skills`](https://skills.sh) CLI.

## Skills

- **[dmtix](skills/dmtix/)** — devmeta-on-ticks. A delivery method (interactive increment
  scoping → autonomous walk-away run → durable narrative records) on top of the synthesized
  **ticks** parallel-agent engine. Invoked with an argument: `/dmtix bootstrap | start | go`.
  Requires the ticks engine skill (see the skill's README).

- **[streams](skills/streams/)** — the seat that sees every stream. For the one session that
  coordinates several dmtix increments running side by side: `/streams status` (what is
  running, what waits on the human, what has stalled — from files), `/streams keep-running`
  (the hourly pass that acts on it), `/streams queue` (what waits on the human), `/streams cut
  <slug>` (a new side stream: branch, worktree, ports, records, a brief), and `compact`,
  `restart`, `hotfix`, `land`. Live state lives in git's common directory (`coord/`), shared
  by every worktree and never committed; `scripts/coord.py` writes its log and enforces holds
  with an end. Landing is a checklist until two hand landings confirm it.

- **[roadmap](skills/roadmap/)** — beside `streams`, for the seat: a plan above the
  increments that several streams build together. Each piece points at one tick in its own
  stream, and the roadmap holds only what ticks cannot, the links between streams. `/roadmap
  status | update | decide | review | new <name>`.

- **[joe](skills/joe/)** — type `/joe` after a long agent answer and get the same thing back
  short and in plain English: bottom line first, no hedging, no jargon, no tech-legalese.
  Rewrite only — it does no new work.

- **[herdr-reload](skills/herdr-reload/)** — after a Claude Code update, `/herdr-reload` moves
  the sessions already running in your herdr panes onto the new binary. Each idle pane on an
  old version gets `/exit` and then `claude --resume` of the same session. Dry run first;
  busy panes are never interrupted. `/herdr-reload force` skips the confirmation and queues a
  restart note to each busy pane's agent instead.

## Install

```bash
# everything in this repo, globally (user dir), for Claude Code
npx skills add mkelk/skills -g -a claude-code

# a single skill, and copy instead of symlink
npx skills add mkelk/skills --skill dmtix -g -a claude-code --copy
```

`-g` installs to `~/.claude/skills/` (available in every project) instead of the current
project's `.claude/skills/`. Omit `-a` and the CLI offers every detected agent. `npx skills
update` upgrades; `npx skills remove` uninstalls. See <https://skills.sh>.

## License

MIT — see [LICENSE](LICENSE).
