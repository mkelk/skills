---
name: streams
description: The seat that sees every stream — for the one session that coordinates several dmtix increments running side by side in their own worktrees. "status" prints what is running, what is waiting on the human and what has stalled, from files; "cut" sets a new side stream up (branch, worktree, ports, records, a brief). Not for the sessions that run a stream — they use dmtix go. Landing is still by hand until the land door exists.
---

# streams — the seat that sees every tree

One session holds this seat. It talks to the human, cuts streams, watches them, lands them,
and relays what one stream finds that another must act on. It never runs an increment and
never writes code on a stream's branch. **Dispatch on the argument; read ONLY the matching
reference and follow it exactly.** With no or an unknown argument, show this table and ask.

| Argument | Cadence | Door |
|---|---|---|
| `status` | whenever the human asks "what is running" | `references/status.md` — one screen from `.devmeta/streams.md`, `tk`, the process list and `ListAgents`; what waits on the human; what has stalled. |
| `cut <slug>` | once per new side stream | `references/cut.md` — the next free port block, a branch and worktree, `.env`, deps, the records, a brief file the new session reads. |
| `land <slug>` | once per finished stream | **not built yet** — `references/land.md` holds the checklist; landings are done by hand against it until two have confirmed every step. |

Principles, binding for every door:
- **The state is a file.** `.devmeta/streams.md` on master is the table of every running
  stream and the standing rules; the seat edits it with a scratch worktree and `git
  update-ref`, never a checkout — the main checkout belongs to whichever session runs the
  mainline. Every stream gets it by sync forward.
- **Doors, not engines.** The loop lives in the ticks skill; scoping in `dmtix start`. These
  doors read state, set streams up, and print what to tell a session. They never dispatch a
  tick and never decide anything the human should.
- **Verify on the thing.** A session's report is not its state. `status` reads `tk`, the
  worktrees and the process list; it does not ask the sessions.
- **The seat is expensive.** Whatever this skill can read from a file, the seat must not
  carry in context. If a door is missing something the seat keeps remembering, the fix is
  the door, not the memory.

Where it came from: `docs/thoughts/2026-09-20-orchestrator-pattern.md` in the project that
first needed it. Source of truth: `github.com/mkelk/skills` → `skills/streams/`.
