## Purpose

**Not rehearsed. The default is one seat per repository** (`references/init.md`); use this
only when the human asks for one seat over several repositories in so many words.

Tested so far (2026-11-24): `coord.py -C`, the seats file and `coord.py repos` (unit tests);
an `OWED` line from a second repository reaching the seat; `/add-dir` and the settings rule
below. Not yet run end to end from one seat: `init` and `dmtix bootstrap` for another
repository, a `cut` and a landing there, `status` and `keep-running` over several, the scout,
a compaction. The other doors do not mention this file: when it is used, the seat applies it
to each door itself. (The human, 2026-11-24, first: *"I want the seat to be able to work over
several repos and I want only one seat per developer"*; then, for a live workshop: *"one seat
per repo"*, the set-up that had been tested.)

This file says what changes when a seat serves more than one repository. Every door still
works one repository at a time; the seat runs it once per repository.

## What stays per repository

Each repository keeps its own state, and nothing is shared between them:

- its own `coord/` in its own git common directory, with its own `streams.md`, `log.md`,
  `asks.md`, `schedules.md` and `seat.json`;
- its own project file, `.devmeta/streams.md`, its own trunk and its own worktrees beside it;
- its own `init`, its own landings, its own `## Standing rules`.

A stream belongs to exactly one repository: its worktree is a worktree of that repository.

## Adding a repository to the seat

In the seat's pane, for the new repository `<repo>` (its main checkout):

0. Give the seat the repository as a working directory: `/add-dir <repo>` in the seat (or start
   it with `claude --add-dir <repo>`). A session asks before reading or editing files outside
   its own directories, and the seat writes `.devmeta/` and `.tick/` there; a seat that stops
   on such a question at night has stalled. The seat keeps the settings of the repository it
   was started in: an added repository's `.claude/settings.json` does not apply to it (tested
   2026-11-24), so the seat's own allow rules go in its first repository.
1. `init` for that repository: follow `references/init.md` with every command run there,
   `git -C <repo> …` and `coord.py -C <repo> …`. The project file is written and committed in
   `<repo>`, on its trunk.
2. `coord.py -C <repo> seat --here`. This registers the seat in that repository's `coord/`,
   and records the repository in the user's seats file. `coord.py repos` lists every
   repository this seat serves; `coord.py repos --paths` gives one main checkout per line.
3. Say it to the human in one line: which repositories this seat now serves.

`dmtix bootstrap` and `research-loop init` take the repository the same way: run them for
`<repo>`, every command there.

## The doors, with several repositories

- **`cut <slug>`** asks which repository when the seat serves more than one and the human did
  not say. The worktree, the branch, the brief, the row and the `CUT` log line all go in that
  repository. Slugs only need to be unique within one repository; say the repository with the
  slug when two repositories have a stream of the same name.
- **`status`** and **`keep-running`**: once per repository in `coord.py repos --paths`, each
  block headed by the repository's name. NEEDS YOU comes first, gathered from all of them.
- **`land`, `hotfix`, `restart`, `queue`, `compact`**: per repository, as written, with
  `-C <repo>` on every `coord.py` call and `git -C <repo>` on every git call.
- **Relay.** A stream's `OWED` line reaches this seat from any repository it is registered
  in. A `PAID` line written with `coord.py -C <repo> log` reaches the stream in `<repo>`.

## In herdr

A stream's space nests under the space whose first terminal sits in the same repository's
main checkout. The seat sits in one repository, so streams of another repository open as a
space of their own, named after the stream. That is expected. If the human wants them nested
too, a plain terminal in the other repository's main checkout, as the first terminal of a
space, gives them a parent.

## What not to do

- **Two seats on one repository.** Registering this seat in a repository moves the
  repository off any other seat's list (`coord.py repos` shows `moved to <s>` for the old
  one). Check `coord.py -C <repo> seat` first, and ask the human before taking a repository
  from another seat.
- **One `coord/` for several repositories.** `COORD_DIR` is for tests; never point two
  repositories at one directory.
