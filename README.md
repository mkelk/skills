# skills

Agent skills by [@mkelk](https://github.com/mkelk), installable with the
[`skills`](https://skills.sh) CLI.

## Skills

- **[dmtix](skills/dmtix/)** — devmeta-on-ticks. A delivery method (interactive increment
  scoping → autonomous walk-away run → durable narrative records) on top of the **ticks**
  engine below. Invoked with an argument: `/dmtix bootstrap | start | go`.

- **[ticks](skills/ticks/)** — the engine dmtix runs on: plans an epic into ticks, runs them
  as parallel or warm-chained agents in their own worktrees, gates each tick and each wave,
  reviews, retros, and resumes from the tracker after any stop. Works the `tk` tracker,
  whose binary comes from [`pengelbrecht/ticks`](https://github.com/pengelbrecht/ticks). It
  began as the skill in that repo (MIT, Peter Engelbrecht; see
  [skills/ticks/LICENSE](skills/ticks/LICENSE)) and moved here with its history; upstream's
  own skill is now tracker-only, so install this one, not that.

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
# the tk tracker binary (for dmtix and ticks), from upstream
curl -fsSL https://raw.githubusercontent.com/pengelbrecht/ticks/main/install.sh | sh

# everything in this repo, globally (user dir), for Claude Code
npx skills add mkelk/skills -g -a claude-code

# or just the method and its engine
npx skills add mkelk/skills --skill dmtix --skill ticks -g -a claude-code

# a single skill, and copy instead of symlink
npx skills add mkelk/skills --skill dmtix -g -a claude-code --copy
```

`-g` installs to `~/.claude/skills/` (available in every project) instead of the current
project's `.claude/skills/`. Omit `-a` and the CLI offers every detected agent. `npx skills
update` upgrades; `npx skills remove` uninstalls. See <https://skills.sh>.

**A user-level skill shadows a project's own skill of the same name.** Claude Code resolves
same-name skills *personal over project*, and picks up a changed `SKILL.md` in running sessions.
So if a repo on your machine ships its own `.claude/skills/streams` (or any name here), don't
install that skill globally: every session in that repo would get this repo's version instead
of its own.

## Before you push

This repo is public, so every push goes through a leak check. `scripts/leak-check` looks for
two things: shapes that never belong in a public repo (API keys and tokens, private-key
headers, real e-mail addresses, IP addresses, absolute home-directory paths), and the words on
a private deny-list. The deny-list is one regex per line, read from `$SKILLS_LEAK_DENY` or else
`~/.config/skills-leak/deny.txt`. It lives outside the repo on purpose: a list of words to keep
out of a public repo would itself be the leak. Without it the check stops with an error; it
never passes by default.

```bash
git config core.hooksPath hooks     # once per clone: pushes run hooks/pre-push
scripts/leak-check                  # the tracked files as they are now: names, lines,
                                    #   strings inside binary files, symlink targets
scripts/leak-check --history        # every commit on every ref: the same, plus messages,
                                    #   authors, ref names and annotated tags
```

The hook checks the name of each ref being pushed and the file names, lines, binary files,
messages and author names of the commits (and any annotated tag) being pushed, and refuses the
push on a hit. A hit prints as `file:line: <kind>` and never shows the matched value; a file or
ref name that is itself the hit prints as a hash. A line that is reviewed and fine goes in
`scripts/leak-allow.txt` as one exact entry (`scripts/leak-check --entry <file>:<line>` prints
it; a file-name hit prints its own entry); the file takes exact lines only, never patterns. Tests:
`python3 -m unittest discover -s scripts -p 'test_*.py'`.

## License

MIT — see [LICENSE](LICENSE). `skills/ticks/` carries its own MIT notice, which keeps Peter
Engelbrecht's copyright: [skills/ticks/LICENSE](skills/ticks/LICENSE).
