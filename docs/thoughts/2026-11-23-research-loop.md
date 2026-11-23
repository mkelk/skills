# research-loop: design notes (2026-11-23)

**Status:** v1 written and dry-run once on a toy program (a speed-up with a mechanical ruler: one arm lost, one shown, every freeze committed before its run). The dry run's sixteen findings are fixed. Not yet run on a real program, with streams, with an answer key, or overnight.

## Why a skill

`/dmtix discuss-project` already tells research from development, and says research may be one
pass or loops. It had nowhere to send a research verdict: `start` and `go` build. Research
was being run ad hoc, each repository writing its own loop into `CLAUDE.md`. The loops that
worked shared a small set of rules, and the ones that went wrong lacked the same two: a
ruler kept away from the researcher, and a scoring rule frozen before the run.

## What it is distilled from

A research program run for several weeks in a private repository, with a charter, one
program page, numbered loop briefs with freezes, a seat that held the answer keys and a
daily independent check. The dated lessons in `SKILL.md` are from that program's records.
Nothing of that repository's subject is in the skill.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| A skill of doors, no scripts in v1 | Git already gives the two proofs: a freeze commit precedes its run's commit, and `git hash-object` pins a ruler. A script would need tests before it could be trusted | `coord.py`-style tooling now |
| Six doors: init, charter, go, check, report, explain | Same cadence split as dmtix (once per repository, once per program, per session), plus the holder's side and the closing report | folding research into dmtix `start`/`go`: their loop is ticks and gates, a different engine |
| `init` exists, and adopts | A repository with its own rounds, rubric and scoreboard should keep them. Init maps files to roles and names the gaps | a fixed folder layout imposed on every repository |
| Project facts in `.devmeta/research.md` on the trunk | beside `.devmeta/streams.md`; every worktree checks it out | a section inside `.tick/config.md`: that file is dmtix's method |
| Program records in `docs/research/<slug>/` on the lead's branch | the lead commits each loop; no stream writes on the trunk; landing brings them over | `.devmeta/increments/`: a program is not an increment; the main checkout: it is the seat's |
| Keys outside git and every worktree | a file in the repository is in every worktree and in history for good | a gitignored folder inside the repository: one `git add -f` or a worktree copy away |
| Two roles, the seat as holder | a lead that holds its ruler grades itself | a single session with a "do not read" rule |
| Four ruler kinds, chosen per question in the charter | the tasks differ: identical outputs, known past cases, a graded report, taste | one kind (a judged benchmark) |
| Verdict words: shown, lost, not shown, broken, confounded | "not shown", "broken" and "confounded" each stop a different wrong reading | pass/fail |
| `explain` as a door, run at the end of init and charter | a human who cannot say how their research is run cannot steer it | a closing paragraph nobody can ask for again |

## Open

- The guard is a deny rule in the lead's worktree only (`.claude/settings.local.json`), so the
  holder can read its own keys, tested from a fresh headless session because a sub-agent
  tests the caller's settings. The dry run found the first form of the rule matched nothing:
  an absolute path needs two leading slashes.
- The guard is a deny rule plus a canary test. A shell command can read what a Read rule
  denies; the doors say so. An unattended run with a key that matters needs the key off the
  machine or the lead in a box. No recipe for that box yet.
- `streams` reads a research stream's state from one line in `status.md`. `keep-running` and
  the scout learn of it only through the project's `## Scout` section, which `init` offers.
- Scoring on a key waits for the seat. Overnight the seat's hourly pass must pay `OWED`
  lines; not yet exercised.
- `land` for a research stream is the ordinary landing checklist. A long program that lands
  its records several times is described, not tested.
- Whether one stream may hold a research program and then its increment, or the increment
  always gets its own stream.
