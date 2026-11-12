# dmtix — devmeta-on-ticks

A delivery method (the "devmeta" increment discipline) running on the synthesized **ticks**
engine: lifecycle-addressed config, execution readiness (profile + provisioned worktrees),
dispatch economics (warm-chains), and constraint-surface partitioning. It gives you a
predictable *scope → run → records* rhythm — interactive
increment scoping, a walk-away autonomous run, and durable per-increment narrative records —
on top of ticks' parallel-agent execution.

**Doors, not engines.** dmtix holds only the interactive/ergonomic surface; all execution
process lives in the ticks skill and the tk structure. `SKILL.md` routes on an argument to one
of three doors in `references/`.

## Invocation

| `/dmtix <arg>` | Cadence | Does |
|---|---|---|
| `bootstrap` | once per project, and again after an engine update | installs the method into a ticks project: verifies the ticks skill resolves, `tk init`, injects `.tick/config.md` lifecycle sections (additive — never overwrites), scaffolds `.devmeta/`. On an existing project it is the upgrade check: offers what a newer engine needs, each change shown first. Idempotent. |
| `start` | once per increment | interactive scoping — engine-drafted / human-ratified epic partition, goal-compatible definitions of done — then writes the records tree and the tk roadmap. Setup only; never executes. |
| `go` | per session | starts **or resumes** the active increment's run; thin wrapper over the ticks skill; stops at the project checkpoint. Integration ends at the increment's base branch — merging to `main` is the human's act. |

## Dependency: the ticks engine

dmtix is the *method*; it runs on the *ticks* skill (the *engine*), which lives in this repo
at [`skills/ticks/`](../ticks/). Install both:

```bash
npx skills add mkelk/skills --skill dmtix --skill ticks -g -a claude-code
```

The engine is installed at user level (`~/.claude/skills/ticks/`); `/dmtix bootstrap` checks
for it and tells you if it's missing. Claude Code resolves same-name skills *personal over
project*, so a project's own `.claude/skills/ticks/` never runs while the user-level one is
installed, and a project can't be held on another engine version. (It began as the skill in Peter Engelbrecht's `pengelbrecht/ticks`, by way of the
fork `mkelk/ticks-melk`, now retired; see `skills/ticks/LICENSE`.)

Two sources, two jobs: the **`tk` binary** comes from upstream `pengelbrecht/ticks` (its
install script; 0.31 and 0.32 both work), the **skill** from this repo. Don't install
upstream's own `ticks` skill, and don't run `tk skills install`: since v0.32 upstream's
skill is tracker-only, with no run loop, and the command writes it into the project's
`.claude/skills/ticks/`, where it runs if the engine isn't installed at user level and only
confuses things if it is. `/dmtix bootstrap` refuses the first and offers to remove the second.

## Upgrading

```bash
npx skills update -g          # the engine (ticks) and dmtix, at user level
```

Then run `/dmtix bootstrap` in each project, or just start its next increment: `/dmtix start`
runs the same upgrade check. Nothing needs migrating by hand and nothing breaks if you skip
it. The check offers what would otherwise stay on the old behaviour — split an over-budget
learnings file, group `## Testing` under the two gates, remove a leftover project copy of the
engine — each shown in full before it is written, never during a run.

**One engine per machine, so update between increments.** The engine is user-level, so
`npx skills update -g` changes it for every project at once, and no project copy can hold one
back. Running sessions pick the change up without a restart: Claude Code reloads a changed
`SKILL.md`, and the engine reads its `references/` from disk each time it uses them. An
orchestrator mid-epic finishes on the text it already loaded. The engine is written so an
increment started on an earlier version continues safely; if one must not see the change at
all, update after it reaches its checkpoint.

## Where things live (the method's separation of concerns)

- **Method** (edit only to change how you work): `.tick/config.md`
- **Live state**: tk (`tk roadmap`, `tk board`); inferred execution facts: `.tick/profile.md`
- **Narrative records** (written by the run at each boundary): `.devmeta/increments/<id>/`
  (`_overview.md`, `ia-cycles/`, `completion.md`) + `.devmeta/project-history.md`
- **Engine**: the ticks skill, user-level (`~/.claude/skills/ticks/`)
