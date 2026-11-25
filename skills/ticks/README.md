# ticks

The engine for planned work with AI agents. You write down what you want as an **epic**. The skill splits it into small **ticks** (tasks), runs them as parallel agents in their own git worktrees, checks each tick and each wave of ticks, reviews the whole result, and writes down what it learned. The tracker is the `tk` command-line tool; its state is a folder of files in your repository, so a run can stop and resume at any time.

**When not to use it.** Ticks is for work that spans sessions, has dependencies, or needs a human to approve something. For a small job that you finish in one conversation, use a plain todo list (for example Claude's TodoWrite) and do not create ticks. Do not create a tick for every small thing.

## Commands

The skill has no slash command. You ask in plain words ("create ticks for this", "plan this", "run the epic") and the agent uses `tk`. These are the `tk` commands you meet in daily use:

| Command | What it does |
|---|---|
| `tk init` | Set up `.tick/` in the repository (once) |
| `tk create "Title" ...` | Make a tick; `-t epic` makes an epic, `--parent` puts it under an epic, `--acceptance` says how to verify it |
| `tk list` / `tk ready` / `tk blocked` | See open ticks, ticks that can start, ticks that wait |
| `tk graph <epic>` | Show the waves of ticks and how many can run in parallel |
| `tk next <epic>` | The next thing to do: implement, plan, or wait for a human |
| `tk show <id>` | Show one tick |
| `tk note <id> "text"` | Add a note (use `--from human` for your own words) |
| `tk close <id> --reason "..."` | Close a tick; always give a reason |
| `tk list --awaiting=` | Ticks that wait for you |
| `tk approve <id>` / `tk reject <id> "why"` | Answer a tick that waits for approval |
| `tk board` | Web board to watch progress |
| `tk roadmap` | Epics in order, with what blocks what |

The usual order:

1. `tk init` once, and keep `.tick/` in git.
2. Describe the work. The agent asks what is unclear, then runs `tk create` for the epic and its ticks. Every epic gets a definition of done (`--acceptance`).
3. Check the plan with `tk graph <epic>`. Do any tasks that only a human can do (`tk list --awaiting work`).
4. Run the epic from your agent session. Waves run one after another; the ticks inside a wave run in parallel.
5. Answer what waits for you (`tk approve`, `tk reject`, `tk note`).
6. At the end the close-out checks the epic against its definition of done and plans the next epic.

## What it asks, and when it stops

- **It asks before it plans:** what is unclear in your idea, what is in scope, and what "done"
  means for the epic. It also asks how far the run should go: one epic, one project, or the whole roadmap.
- **It asks during a run only through ticks that wait for you:** work only a human can do, an approval,
  or an input. They show in `tk list --awaiting=`; the run goes on with everything else.
- **It stops at a project checkpoint**, at a tick that waits for you, or at a real blocker (a failing
  wave gate it cannot repair). Between epics of one project it keeps going by itself.
- **It never changes the roadmap on its own:** adding, removing or reordering epics is your decision.

## The picture

![ticks: one loop per epic. Flow on top, left to right, from Roadmap through Plan, Waves, Merge, Final review and Close-out to a Checkpoint.](ticks.svg)

*Read it left to right: who acts is named under each box (you, the orchestrator, implementers, agents); the next epic starts the loop again.*

You set the roadmap: the epics, their order, and a definition of done for each. Agents plan each
epic into ticks, run them in parallel waves (one worktree each, with a check after every tick and
every wave), review the whole diff, and write down what they learned. At the end of a project the
run stops for you at a checkpoint.

## Set up

```bash
curl -fsSL https://raw.githubusercontent.com/pengelbrecht/ticks/main/install.sh | sh   # the tk binary
npx skills add mkelk/skills --skill ticks -g -a claude-code                            # this skill
tk init                                                                                # in your repository
```

## Good to know

- **Keep `.tick/` in git.** It holds the ticks, so a run can stop and resume, and it syncs by normal git.
- **Do not install upstream's own `ticks` skill**, and do not run `tk skills install`: it writes a
  tracker-only skill into `.claude/skills/ticks/` that can run instead of this one.
- **Roadmap changes are yours.** The agent may propose adding, removing or reordering epics. It does not do it.
- **`.tick/config.md` is optional.** It is your project's guidance for runs: test commands, rules,
  steps at the end of a wave or an epic. The skill is generic; this file is yours, and updating the skill never overwrites it.

## How it works inside

This page is for people. The run protocol, the `config.md` sections and every `tk` flag are written for Claude in the skill's own files:
[`SKILL.md`](SKILL.md) and [`references/`](references/).

## Credit and license

This skill began as the skill in [pengelbrecht/ticks](https://github.com/pengelbrecht/ticks) (MIT, Peter Engelbrecht) and moved here with its history. The `tk` binary comes from upstream. License: [LICENSE](LICENSE) (MIT; it keeps Peter Engelbrecht's copyright).
