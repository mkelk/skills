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

dmtix is the *method*; it runs on the synthesized *ticks* skill (the *engine*). Install it too:

```bash
npx skills add mkelk/ticks-melk -g -a claude-code --copy
```

It must resolve at user level (`~/.claude/skills/ticks/`) or be vendored into the project
(`.claude/skills/ticks/`); `/dmtix bootstrap` checks for it and tells you if it's missing.
(`mkelk/ticks-melk` is a fork of the stock tracker at `github.com/pengelbrecht/ticks`; its
default branch carries the synthesized engine upgrades.)

Two sources, two jobs: the **`tk` binary** comes from upstream `pengelbrecht/ticks` (its
install script; 0.31 and 0.32 both work), the **skill** from `mkelk/ticks-melk`. Don't
install upstream's own `ticks` skill: since v0.32 it is tracker-only, with no run loop, and
`/dmtix bootstrap` refuses it.

## Upgrading

```bash
npx skills update -g          # the engine (ticks) and dmtix, at user level
```

Then run `/dmtix bootstrap` in each project, or just start its next increment: `/dmtix start`
runs the same upgrade check. Nothing needs migrating by hand and nothing breaks if you skip
it. The check offers what would otherwise stay on the old behaviour — drop a pinned engine
copy, split an over-budget learnings file, group `## Testing` under the two gates — each shown
in full before it is written, never during a run.

A project in the middle of an increment can be kept on the engine it started with: point
`.claude/skills/ticks` at a frozen copy before updating (a symlink, outside git), and the next
`/dmtix start` offers to drop it.

## Where things live (the method's separation of concerns)

- **Method** (edit only to change how you work): `.tick/config.md`
- **Live state**: tk (`tk roadmap`, `tk board`); inferred execution facts: `.tick/profile.md`
- **Narrative records** (written by the run at each boundary): `.devmeta/increments/<id>/`
  (`_overview.md`, `ia-cycles/`, `completion.md`) + `.devmeta/project-history.md`
- **Engine**: the ticks skill (user-level or vendored per project)
