# dmtix — devmeta-on-ticks

A delivery method (the "devmeta" increment discipline) running on the synthesized **ticks**
engine: P3 lifecycle config + P6 execution readiness + P7 dispatch economics + P8
partitioning doctrine. It gives you a predictable *scope → run → records* rhythm — interactive
increment scoping, a walk-away autonomous run, and durable per-increment narrative records —
on top of ticks' parallel-agent execution.

**Doors, not engines.** dmtix holds only the interactive/ergonomic surface; all execution
process lives in the ticks skill and the tk structure. `SKILL.md` routes on an argument to one
of three doors in `references/`.

## Invocation

| `/dmtix <arg>` | Cadence | Does |
|---|---|---|
| `bootstrap` | once per project | installs the method into a ticks project: verifies the ticks skill resolves, `tk init`, injects `.tick/config.md` lifecycle sections (additive — never overwrites), scaffolds `.devmeta/`. Idempotent. |
| `start` | once per increment | interactive scoping — engine-drafted / human-ratified epic partition, goal-compatible definitions of done — then writes the records tree and the tk roadmap. Setup only; never executes. |
| `go` | per session | starts **or resumes** the active increment's run; thin wrapper over the ticks skill; stops at the project checkpoint. |

## Dependency: the ticks engine

dmtix is the *method*; it runs on the synthesized *ticks* skill (the *engine*). Install that
too — it must resolve at user level (`~/.claude/skills/ticks/`) or be vendored into the
project (`.claude/skills/ticks/`). `/dmtix bootstrap` checks for it and tells you if it's
missing. (Stock upstream ticks lives at `github.com/pengelbrecht/ticks`; the synthesized
engine dmtix targets is developed on a fork.)

## Where things live (the method's separation of concerns)

- **Method** (edit only to change how you work): `.tick/config.md`
- **Live state**: tk (`tk roadmap`, `tk board`); inferred execution facts: `.tick/profile.md`
- **Narrative records** (written by the run at each boundary): `.devmeta/increments/<id>/`
  (`_overview.md`, `ia-cycles/`, `completion.md`) + `.devmeta/project-history.md`
- **Engine**: the ticks skill (user-level or vendored per project)
