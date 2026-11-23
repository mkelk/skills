## Purpose

What differs when the stream being cut is a **research stream**: its session leads a program
under the `research-loop` skill, and this seat holds what the program is measured by. Read
`cut.md` first; this file only names the differences, step by step. The repository must have
`.devmeta/research.md` (`/research-loop init`, run in the seat); if not, run that first.

`<kept>` is the `kept:` line of `.devmeta/research.md`.

## Step 0

A research stream is a side stream, cut `--from trunk`. It has **no increment**: no id, no
epics, no tk project.

## Step 2 — the worktree

- **The guard, before the session exists.** Write the entries of the project file's
  `## Guard` into the worktree's `.claude/settings.local.json`, together with the compact
  settings: the `Read` denies, the hook when the project file names one, and `Read` denies
  for this seat's own scratch folder and transcript folder. A session loads its settings
  when it starts, so a guard written now holds from the lead's first turn, and the lead
  never edits the fence it is kept behind. `autoCompactWindow` is `200000`: the program's
  state is its program page.
- **The key, if the seat already has it.** It goes to `<kept>/research/<slug>/ruler/`, and
  what the lead may read to `<kept>/research/<slug>/data/`. A helper agent that builds a key
  writes its scripts into the ruler folder too.

## Step 3 — records

- **Active line** on the new branch: `**Active:** research <slug> — <title> (side stream; no
  increment; charter not written yet)`, the charter's future path
  (`<records>/<slug>/charter.md`), status `NOT STARTED`, branch, worktree, and `**Roadmap
  (tk):** none.` The `charter` door completes it.
- **The row**: increment `research`, epics `—`, status `cut, charter not written`. Its
  state is later read from the status box of `<worktree>/<records>/<slug>/program.md`.
- No overview, no tk project, nothing claimed in a task file.

## Step 4 — the brief

The six items of `cut.md`, and these:

1. **What the program is for**, in the human's own words, quoted with the date. The lead
   quotes them again in the charter.
2. **What exists**: a table of what the lead may read and where (`<kept>/…/data/`), and what
   it must never open (`<kept>/…/ruler/`), by path. Say who made the hidden part, and that
   the lead took no part.
3. **How results are scored**: which ruler decides, and the request line the lead writes
   (`OWED <slug>: score loop <NNN> at <path>`).
4. **Suggested answers for the charter**, when the seat knows the scope: one row per
   question of the `charter` door. Say that the human decides. A brief that carries them
   makes the charter dialogue one round.
5. **How to reach the seat**: `coord.py log "OWED <slug>: …"` is delivered to the seat's
   terminal by itself, and the answer comes back the same way; loop results go with
   `coord.py log --tell seat "…"`.
6. **The lead's permission mode**, the guard as installed, and what the seat already knows
   about clean model calls here (`research-loop` → `references/subcall.md`).

## Step 5 — the session

Before starting it: `coord.py seat` names this pane. If not, `coord.py seat --here`.

The start prompt: *"You are the `<slug>` stream: a research stream, not an increment. Read
`docs/thoughts/<date>-<slug>-brief.md` from start to end. Then run `/research-loop charter
<slug>` and bring the draft charter to the human in this pane. Nothing runs before their go.
Do not run `/dmtix start` or `/dmtix go`."*

Log the cut: `coord.py log "CUT <slug> (research): …"`.

## Afterwards: the seat's half

`research-loop` → `references/check.md` is this seat's door for the program: the check at
the charter, reading freezes, scoring, the independent check, the purpose review. Requests
arrive in this pane as `<who>: OWED <slug>: …`; `coord.py show --owed` lists them with ids.
