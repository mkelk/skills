# skills

Agent skills by [@mkelk](https://github.com/mkelk), installable with the
[`skills`](https://skills.sh) CLI.

## Skills

- **[dmtix](skills/dmtix/)** — devmeta-on-ticks. A delivery method (interactive increment
  scoping → autonomous walk-away run → durable narrative records) on top of the **ticks**
  engine below. Invoked with an argument: `/dmtix bootstrap | explain | discuss-project | start | go`. Start at
  **[skills/dmtix/README.md](skills/dmtix/README.md)**.

- **[ticks](skills/ticks/README.md)** — the engine dmtix runs on: plans an epic into ticks, runs them
  as parallel or warm-chained agents in their own worktrees, gates each tick and each wave,
  reviews, retros, and resumes from the tracker after any stop. Works the `tk` tracker,
  whose binary comes from [`pengelbrecht/ticks`](https://github.com/pengelbrecht/ticks). It
  began as the skill in that repo (MIT, Peter Engelbrecht; see
  [skills/ticks/LICENSE](skills/ticks/LICENSE)) and moved here with its history; upstream's
  own skill is now tracker-only, so install this one, not that.

- **[streams](skills/streams/)** — the seat that sees every stream. For the one session that
  coordinates several dmtix increments running side by side: `/streams init` (the project
  file, once), `/streams status` (what is running, what waits on the human, what has stalled —
  from files), `/streams keep-running` (the hourly pass that acts on it), `/streams queue` (what
  waits on the human), `/streams cut <slug>` (a new stream: branch, worktree, the resources
  the project names, records, a brief), and `compact`, `restart`, `hotfix`, `land`. Live state lives in git's common directory (`coord/`), shared
  by every worktree and never committed; `scripts/coord.py` writes its log and enforces holds
  with an end. Landing is a checklist until two hand landings confirm it.
  New to it? Start at **[skills/streams/README.md](skills/streams/README.md)**: what the seat
  and a stream are, how to begin, and an example.

- **[roadmap](skills/roadmap/)** — beside `streams`, for the seat: a plan above the
  increments that several streams build together. Each piece points at one tick in its own
  stream, and the roadmap holds only what ticks cannot, the links between streams. `/roadmap
  status | update | decide | review | new <name>`.

- **[research-loop](skills/research-loop/)** — research in loops, for a question whose answer is
  knowledge or a decision and not a feature. `/research-loop init` (once per repository: adopts
  how it already does research, and explains the set-up), `charter <slug>` (purpose, bar, ruler,
  allowance, end, with the human), `go` (assess, freeze, run, verdict, record, without waiting),
  `check` (the seat's side: keys, scoring, the independent check), `report`, `explain`. The lead
  never grades its own work: with `streams` the seat holds the ruler. `/dmtix discuss-project`
  hands over to it, and its report hands back to `/dmtix start`.
  Start at **[skills/research-loop/README.md](skills/research-loop/README.md)**: where the files
  live and an example.

- **[joe](skills/joe/)** — type `/joe` after a long agent answer and get the same thing back
  short and in plain English: bottom line first, no hedging, and plain words in place of dense technical wording.
  Rewrite only — it does no new work. See [skills/joe/README.md](skills/joe/README.md).

- **[herdr-reload](skills/herdr-reload/)** — after a Claude Code update, `/herdr-reload` moves
  the sessions already running in your herdr-app (hc) or herdr terminals, here and on connected
  machines, onto the new binary. Each idle session on an old version gets `/exit` and then
  `claude --resume` of the same session. Dry run first; busy sessions are never interrupted.
  `/herdr-reload force` skips the confirmation and queues a restart note to each busy
  session's agent instead. See [skills/herdr-reload/README.md](skills/herdr-reload/README.md).

## Which skill when

| You want to... | Use |
| --- | --- |
| Build one feature or fix as an increment: scope it, run it, keep records | **dmtix** |
| Work the tick tracker: plan an epic, run ticks, resume after a stop | **ticks** (dmtix runs on it) |
| Coordinate several dmtix increments that run side by side | **streams** |
| Plan above the increments, for pieces that several streams build together | **roadmap** (beside streams) |
| Answer a question whose answer is knowledge or a decision, not a feature | **research-loop** |

How they hand over: dmtix runs on ticks, so every increment is an epic of ticks. When more
than one increment runs at once, the streams seat coordinates them, and roadmap sits beside
streams for plans that cross streams. A research-loop usually runs as a stream beside the
dmtix increments: `/dmtix discuss-project` can hand over to it, and its report hands back to
`/dmtix start`.

The skills are generic. Each project adapts them locally: the files a skill writes into your
repository are yours to edit, and updating the skill never overwrites them.

The pictures (for the four main skills; flow on top, files below):
[dmtix](skills/dmtix/dmtix.svg), [streams](skills/streams/streams.svg),
[research-loop](skills/research-loop/research-loop.svg), [ticks](skills/ticks/ticks.svg).
Regenerate them with `python3 diagrams/build.py`.

## Install

```bash
# the tk tracker binary (for dmtix and ticks), from upstream
curl -fsSL https://raw.githubusercontent.com/pengelbrecht/ticks/main/install.sh | sh

# everything in this repo, globally (user dir), for Claude Code
npx skills add mkelk/skills -g -a claude-code

# or just the method and its engine
npx skills add mkelk/skills --skill dmtix --skill ticks -g -a claude-code

# into one repository only (no -g), as files it can commit: the method travels with the repo
npx skills add mkelk/skills --skill dmtix --skill ticks --skill streams --skill research-loop \
    -a claude-code --copy

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
it; a file-name hit prints its own entry); the file takes exact lines only, never patterns.

Beside it, `scripts/size-check` holds the skills an agent loads whole to a size budget: each
`SKILL.md`, `README.md` and `references/*.md` (recipes too) of `streams`, `roadmap` and `research-loop` under 16 KB,
`streams/references/status.md` under 24 KB. A file over budget prints with its size and the check
fails; `--top 3` also prints the largest. The pre-push hook runs both; to run them by hand:

```bash
python3 -I scripts/leak-check && python3 scripts/size-check
```

Tests: `python3 -m unittest discover -s scripts -p 'test_*.py'`.

## License

MIT — see [LICENSE](LICENSE). `skills/ticks/` carries its own MIT notice, which keeps Peter
Engelbrecht's copyright: [skills/ticks/LICENSE](skills/ticks/LICENSE).
