## Purpose

Set a repository up for streams once: write the project file `.devmeta/streams.md` with the
facts the other doors read, and create `coord/` in git's common directory. A project with no
file still works (every fact has a detected default); this door is for writing down what
detection gets wrong or cannot know.

Arguments: `init [--force]`. Run it in the repository's main checkout, on the trunk.

The file is committed and read by the seat only. Every section is optional, and the door
writes only the sections that have content:

| Section | What goes in it | Read by |
|---|---|---|
| `## Project` | `trunk: <branch>`, `worktree root: <dir>` | every door, through `coord.py config` |
| `## Resources` | what one stream holds alone: a port block, a database schema, a queue, a host | `cut`, `status` |
| `## At cut` | the commands that make a fresh worktree runnable | `cut`, after the worktree exists |
| `## At landing` | the checks run on the merged tree | `land` |
| `## Heavy runs` | the runs too heavy for two at once (a browser test tier, say): how to see one running (a `pgrep` pattern), and the project's rules for them; `references/recipes/` has worked ones to point at | `status`, `land` |
| `## Standing rules`, `## Seams`, `## At hotfix` | prose: rules pasted into a brief, files two branches both edit and how each resolves, a hotfix's verify and hand-off | `cut`, `land`, `hotfix` |

Only the first five are written by this door; add the prose sections by hand when the project
has something to say in them.

`coord.py` below means `python3 <skill dir>/scripts/coord.py`. `coord.py config --get <fact>`
prints one bare value (`trunk`, `worktree --slug <s>`, `at-cut`, `heavy-runs`, …) for a command line.

## Step 1 — Is there a file already?

`coord.py config`. It prints `project file:` with a path when one exists. If it does, stop and
show the human what it says: this door does not replace a file unless the human says
`--force`, and then it replaces the whole file (keep anything by hand that the flags below do
not cover, such as `## Standing rules` or `## Seams`).

## Step 2 — Detect

Read, do not ask, for these. Say what was found and from where.

- **Trunk.** `coord.py config` prints it with its source: origin's `HEAD`, else a local `main`
  or `master`, else the current branch. A source of "the current branch" is a guess; confirm
  it with the human.
- **Package manager**, from the lockfile at the top:

  | Lockfile | At cut |
  |---|---|
  | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` |
  | `package-lock.json` | `npm ci` |
  | `yarn.lock` | `yarn install --frozen-lockfile` |
  | `uv.lock` | `uv sync` |
  | `poetry.lock` | `poetry install` |
  | `Cargo.lock` | `cargo fetch` |
  | `go.sum` | `go mod download` |

  Several lockfiles (a web front and a Python back, say) give several lines. None gives none.
- **Env file.** A `.env.example` (or `.env.sample`) at the top means a fresh worktree needs
  `cp .env.example .env`, plus whatever per-stream values Step 3 decides.
- **Test runner**, for `## At landing`: `package.json` → `scripts.test` (and `typecheck`,
  `lint` when present) as `<manager> run <script>`; `pytest.ini`, `[tool.pytest]` in
  `pyproject.toml`, or a `tests/` directory with `conftest.py` → `pytest`; `Cargo.toml` →
  `cargo test`; `go.mod` → `go test ./...`; a `Makefile` with a `test:` target → `make test`.
  If `.tick/config.md` has a `## Testing` section, leave `## At landing` out: the default
  already points there, and one home is better than two copies.

## Step 3 — Ask the human

Two questions, in one message, each with what was detected as the proposed answer:

1. **Resources.** "What may two streams not share at once? Ports (which block per stream),
   a database or a schema, a queue, a deploy host?" Write each as a line a person can read,
   with `k` for the stream's number: `web: 70k0`, `schema: app_s<k>`, `host: one at a time,
   held with a coord HOLD`. "Nothing" is a fine answer; then the section is left out.
2. **Worktree root.** The default puts a stream's worktree beside the main checkout
   (`<parent>/<repo>-<slug>`). Ask only when that is wrong: the repository is a submodule (its
   parent is another working tree), or the parent is a directory the human keeps clean. Then
   ask where, for instance `~/trees`.

## Step 4 — Write the file

One command, with only the flags that have a value; each `--at-cut`, `--at-landing` and
`--resources` is one line and may repeat:

```bash
coord.py init-file --trunk main --worktree-root ~/trees \
  --at-cut "uv sync" --at-cut "cp .env.example .env" \
  --at-landing "pytest" \
  --resources "web: 70k0"
```

Leave `--trunk` out when detection found it from origin's `HEAD` (the file then follows the
remote if it changes); give it when the human confirmed a guess. It refuses an existing file
without `--force`.

## Step 5 — Create coord/ and check

```bash
coord.py init
coord.py config --slug demo
```

`init` creates `coord/` in git's common directory and its files, and writes nothing that is
already there. `config` must print the trunk, the worktree path for `demo` and the sections
just written, each with `file:` as its source, and no `warning:` line.

## Step 6 — Commit and report

Commit `.devmeta/streams.md` on the trunk (only that path), and tell the human, in a few
lines: the file's facts, what was detected and what they chose, and that `cut` is next.
