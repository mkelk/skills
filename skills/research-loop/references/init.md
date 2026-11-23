## Purpose

Set a repository up for research once: write its research facts to `.devmeta/research.md`,
make the kept folder, and adapt the skill to how this repository already works. **The door
ends by telling the human what the skill does here, how it was adapted, and why.** That
explanation is part of the work, not a courtesy: a human who cannot say how their research
is run cannot steer it.

Arguments: `init [--force]`. Run it in the main checkout, on the trunk (the seat's place
when the repository uses `streams`). It writes nothing a program owns and starts no program.

## Step 1 — Is there a file already?

If `.devmeta/research.md` exists, stop and show the human what it says. This door replaces it
only on `--force`, and then it keeps every section it does not rewrite.

Check the ground: a git repository (stop if not); `.devmeta/current-increment.md` (dmtix)
and `.devmeta/streams.md` (streams) present or not. Neither is required. Say which were
found: they decide who holds the ruler (Step 3) and where a program runs. This door creates
`.devmeta/` when it is missing; that folder alone does not mean dmtix is installed.

## Step 2 — Read how this repository does research already

Read, do not ask. Say what was found and where.

- `CLAUDE.md` / `AGENTS.md`, the README, `docs/`, any notes, journal or brief files.
- **An existing loop.** A `CLAUDE.md` that already defines rounds or phases, a brief with a
  grading rubric, a scoreboard, a journal, a stop rule. **Adopt it; do not replace it.** Map
  each file to the role it already plays and write the mapping into the project file:

  | The repository has | It is this skill's |
  |---|---|
  | a brief with the question and a rubric | the charter's purpose, questions and ruler |
  | a scoreboard, one row per round | the program page's *Tried* table |
  | a journal or notes carried between runs | *Learned* |
  | phases written in `CLAUDE.md` | the run step of each loop |
  | a rule that hides a file until a late phase | a blind item: it moves behind the guard |

  What the existing loop lacks is what this skill adds. Name the gaps plainly (the usual
  ones: the same session grades its own work; the scoring rule is applied after the run, not
  frozen before it; a hidden file is hidden only by an instruction).
- **What could serve as a ruler.** Tests, benchmarks, a reference output, a compare script,
  past cases with known outcomes, a list only the human has.
- **What is sensitive.** Customer data, credentials, production hosts, anything on a mount.
- **What is slow, heavy or metered.** A long model run, a rate-limited download, a paid API.

## Step 3 — Ask the human what the repository cannot show

A few questions at a time, each with what Step 2 found and a recommendation. Follow the
answers; this is a dialogue, not a form.

1. **What kinds of questions get researched here?** One pass to an answer, loops that each
   build on the last, or both. Give the examples Step 2 suggested.
2. **What can each be measured by?** Offer the four kinds of ruler against their own
   examples, and ask which exist today: **mechanical** (a script, test or benchmark the
   lead runs; it sits in git, pinned by hash); **an answer key** (held-out truth the holder
   keeps and scores against, returning counts only); **a rubric with an independent
   grader** (a fresh agent that has not seen the lead's notes); **the human's judgement**
   (asked rarely, in batches).
3. **What must the lead never see?** Keys, hidden references, known answers. They go to the
   kept folder.
4. **Where is the kept folder?** Outside the repository and every worktree. Default
   `~/<repo>-kept/`. On a shared or backed-up disk only if the human says so.
5. **What is out of bounds?** Production, credentials, client data leaving the machine,
   pushing. And the **fetching rule** if research here reads the web: which tools, whether a
   block or a login wall counts as not read, an allowlist if there is one.
6. **The default allowance** for a program: money, subscription share, wall-clock, loops,
   disk. A program's charter may set its own inside it.
7. **Who holds the ruler**: the seat (streams), a second session, or the human.
8. **Does anything run unattended**, for how long, and **in which permission mode will a
   lead run** (prompting, accepting edits, or one that never prompts)? It decides the guard
   (Step 5) and the default stop rule.

Propose each choice with its reason. Change nothing the human has not agreed to.

## Step 4 — Write

**`.devmeta/research.md`**, committed. Every section is optional; write only what has content.

```markdown
# Research in this repository

## How we do research here
<the explanation from Step 6, kept current: what the skill does here, what was adapted, why>

## Records
records: docs/research
<the mapping from Step 2, when the repository had its own loop: file → role>

## Kept
kept: ~/<repo>-kept
<what lives there: rulers and keys under research/<slug>/ruler/, bulk under research/<slug>/data/>

## Rulers
| name | kind | where | held by |
|---|---|---|---|

## Allowance
<the default for a program, and who may raise it>

## Holder and unattended runs
<who holds the ruler · the permission mode a lead runs in · the default stop rule>

## Guard
<the deny rule as written for a lead, how it was tested and in which mode, what it does not cover>

## Out of bounds
## Fetching
## Standing rules
<rules every program here obeys, pasted into a research stream's brief>
```

**`docs/research/README.md`**: one line saying what the folder is, and an index table
(`program | question | status | report`) that `charter` and `report` keep.

**The kept folder**: create `<kept>/research/`, and in it `canary.txt` holding one line,
`this file must not be readable by a lead`. Step 5 uses it.

**When the repository uses `streams`**, offer two additions to `.devmeta/streams.md`, shown
in full, written on the human's yes:
- under `## Standing rules`: the *Out of bounds* and *Fetching* lines, and "a research lead
  never opens `<kept>/research/*/ruler/`", so every brief carries them;
- under `## Scout`: "for each research stream, read the status box of
  `<its worktree>/docs/research/<slug>/program.md`; say when its **Updated** line is older
  than two hours while its session is working, and repeat its *next* line".

**`CLAUDE.md`**: offer one line pointing at `.devmeta/research.md`. Nothing else.

## Step 5 — Decide the guard, and watch it fire once

A guard is a claim until someone has watched it fire.

- **The guard belongs to a lead, not to the repository.** The holder must read its own
  keys, so the deny never goes into the committed `.claude/settings.json`. It goes into
  each lead's worktree, in `.claude/settings.local.json`, when `charter` sets a program up.
  This door decides its form and proves it works.
- **The rule's form.** Two deny entries, for the rulers and the canary. Write a home path
  as `~/...` and any other absolute path **with two leading slashes**:
  `Read(~/<repo>-kept/research/*/ruler/**)`, or `Read(//srv/kept/research/*/ruler/**)`. A
  single leading slash is read as relative to the settings file and silently matches
  nothing. (2026-11-23) a dry run's canary was read through exactly that rule.
- **Prove it, in a fresh session, in the lead's permission mode.** Asking a sub-agent tests
  this session's settings, not a lead's. Make a scratch worktree, put the two entries in its
  `.claude/settings.local.json`, and run there:
  `claude -p "Read <kept>/research/canary.txt and print what it says" --allowedTools Read
  --permission-mode <the mode from Step 3>` on the cheapest model. It must be refused. If
  it is read, fix the rule's form first; only if a correct rule still does not hold, add a
  `PreToolUse` hook that refuses any tool call naming the path, and test again. Remove the
  scratch worktree.
- Write under `## Guard` what the rule is, what was tested, in which mode, and what happened.
- Say plainly what the guard does **not** cover: a shell command can still read a file a
  Read rule denies. For an unattended run with a key that matters, the key is on another
  machine, or the lead runs as a user or in a container that cannot reach it.

## Step 6 — Write the explanation, commit, then explain

1. **Write `## How we do research here`** in the project file, in plain sentences: what the
   skill does (two roles, the loop, the rule written before the run, where the state
   lives; five lines at most); how it was adapted to this repository, each choice from
   Steps 2 to 5 with its reason (what was adopted from an existing loop, which rulers,
   where the kept folder is, the allowance, the bounds, the guard and how it was tested);
   and what it could not settle, with who decides.
2. **Commit** as `chore(research-loop): init (project file, records index)`.
3. **Tell the human**: run the `explain` door (`references/explain.md`) and follow it,
   closing question included. Then say what to type next: with `streams`, cut a stream and
   run `charter <slug>` in it; without, `charter <slug>` makes the lead's worktree itself.

Any later change to the project file (a new ruler, a moved kept folder, `--force`) rewrites
`## How we do research here` in the same commit, so `explain` never reads a stale one.

**Do not start a program.** The next door is `charter`, and it is the human's call.
