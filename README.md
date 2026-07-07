# skills

Agent skills by [@mkelk](https://github.com/mkelk), installable with the
[`skills`](https://skills.sh) CLI.

## Skills

- **[dmtix](skills/dmtix/)** — devmeta-on-ticks. A delivery method (interactive increment
  scoping → autonomous walk-away run → durable narrative records) on top of the synthesized
  **ticks** parallel-agent engine. Invoked with an argument: `/dmtix bootstrap | start | go`.
  Requires the ticks engine skill (see the skill's README).

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
