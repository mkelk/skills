---
name: dmtix
description: devmeta-on-ticks — a delivery method on the synthesized ticks engine. Explicit user invocation with an argument; "bootstrap" installs the method into a project, "explain" says what the method is in this project, "discuss-project" opens a Claude-led discussion of a not-yet-scoped project, "start" scopes a new increment, "go" starts or resumes the active increment's run. Not for general tk/tick work — the ticks skill owns that.
---

# dmtix — devmeta-on-ticks

Five doors, factored by cadence. **Dispatch on the argument; read ONLY the matching
reference and follow it exactly.** With no or an unknown argument, show this table and ask.

| Argument | Cadence | Door |
|---|---|---|
| `bootstrap` | once per project, and after an engine update | `references/bootstrap.md` — install the method: verify the ticks skill resolves (user-level; Claude Code resolves personal over project), tk init, config lifecycle sections (additive), `.devmeta/` scaffold; on an existing project, the upgrade check (offers only, each shown first; `start` runs it too). Idempotent. |
| `explain` | whenever asked | `references/bootstrap.md` → step 8: say what the method is in this project, what was set up and why. Read-only. |
| `discuss-project` | before `start`, when the project isn't clear enough to spec | `references/discuss-project.md` — Claude opens: "what is the project?"; orients in the repo and the org's conventions; keeps a dated thought document (or directory, if it grows artifacts) in `docs/thoughts/`; hunts unknowns (knowledge, decisions); plays the outline back and challenges the human's intuition; ends with a verdict: ready for `start`, not ready, or dropped. Talk and notes only — no ticks, no code. |
| `start` (or `start-increment-spec`) | once per increment | `references/start-increment-spec.md` — interactive scoping (engine-drafted epic partition, human-ratified; goal-compatible DoDs), records tree, tk roadmap. Setup only. |
| `go` | per session | `references/go.md` — start **or resume** the run; thin wrapper over the ticks skill; stops at the project checkpoint. |

Principles (binding for every door):
- **Doors, not engines.** These files hold the interactive surface only. All process lives
  in the ticks skill and the tk structure — never add loop logic here.
- **Method vs state:** `.tick/config.md` is method (edited only to change how you work);
  per-increment facts resolve via `.devmeta/current-increment.md` and tick descriptions.
- Records land in `.devmeta/` (written by the run's lifecycle hooks); live state is tk
  (`tk roadmap`, `tk board`).

Research is not an increment: a question whose answer is knowledge or a decision runs under
the `research-loop` skill, which `discuss-project` hands over to and whose report hands back
to `start`.

Source of truth for this skill: `github.com/mkelk/skills` → `skills/dmtix/`.
Install / update via `npx skills` (see the repo README).
