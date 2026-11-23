## Purpose

Define one research program with the human: what it is for, what would count as an answer,
what it is measured by, what it may spend, and when it ends. The charter is the only thing
the loop obeys besides this skill. **Nothing runs before the human's go**, and their words
are recorded.

Arguments: `charter <slug>`. Run it in the lead's session, in the lead's own worktree, never
on the trunk. With `streams` that is the stream's worktree. Without it, make one first, from
the main checkout, and start the session there (the holder keeps the main checkout):
`git worktree add ../<repo>-research-<slug> -b research/<slug>`.

`<records>` and `<kept>` below are the `records:` and `kept:` lines of `.devmeta/research.md`
(defaults `docs/research` and `~/<repo>-kept`).

## Step 0 — Where this comes from

- **Project file.** `.devmeta/research.md` must exist; if not, point at `init` and stop.
  Read its *Rulers*, *Allowance*, *Holder and unattended runs*, *Guard* and *Out of bounds*.
- **A discussion.** If a `/dmtix discuss-project` thought document led here, read it first:
  its purpose, decisions and unknowns are the charter's raw material. If the stream has a
  brief (`docs/thoughts/<date>-<slug>-brief.md`), read that too.
- **An existing program.** If `<records>/<slug>/charter.md` exists, resume it. Never
  overwrite a charter that is in force: a change to one is an amendment (last section).

## Step 1 — The dialogue

A few questions at a time. Restate, propose, and let the human correct.

1. **Purpose, in the human's words.** What is this for, and what will be decided or known
   afterwards? Quote them. A purpose the lead paraphrased is one it will drift from. Ask
   whether the point is the answer or **seeing the method work** (a trial, a demonstration):
   for the second, say so here and keep the loops small. A measurable bar pulls a lead
   toward polishing whatever is measured.
2. **The questions.** One primary, at most two secondary. Each must be answerable: write the
   sentence the report would open with if the answer were yes, and if it were no. For a
   which-is-best question: the sentence if one arm wins, and if none does.
3. **The shape.** One focused pass, loops that each build on the last, or a few arms run
   side by side and compared. Do not assume loops.
4. **The bar.** What is "good enough"? A number on the ruler, a rubric total, a decision
   rule. If it cannot be set yet, say so: the lead's first assessment proposes a measurable
   bar and the human accepts it before any verdict is read against it.
5. **The ruler** (below), and who holds it.
6. **The allowance.** Money, subscription share, wall-clock, loops, disk. Inside it the lead
   decides each run with no approval per run. It can be raised: the lead asks before it runs
   out, with the reason and the amount.
7. **Out of bounds and blind items**, beyond the project file's.
8. **Reviews.** Who reads a freeze, and **what the reading gates**: *the run*, when a run
   costs money or more than minutes; *the score*, when a run is cheap and the holder scores
   it (the holder scores no loop whose freeze it has not read); *nothing*, for an unattended
   run, where freezes are read afterwards. And how often the independent check runs
   (`check.md`).
9. **The end** (below).

## The ruler

Pick per question. A program may use more than one; say which decides.

| Kind | Fits | Where it lives | Who scores | What keeps it honest |
|---|---|---|---|---|
| **Mechanical**: a script, test or benchmark | a speed-up that must keep outputs identical; a ported model whose output must match a reference within a tolerance | in git, under `<records>/<slug>/ruler/` or the repository's own scripts; reference data read-only | the lead runs it | **every file the ruler reads is pinned**: script, its test, reference outputs, the control (`git hash-object <file>`, one line each in `<records>/<slug>/ruler/hashes.txt`, and that file's own hash in the charter). A loop that finds one changed is broken. Say where the reference outputs came from. The tolerance is the human's and is set before the first run |
| **Answer key**: held-out truth | past cases with known causes; a known-answer redo; a list of the papers that matter | the kept folder, `<kept>/research/<slug>/ruler/`, never in git or a worktree | the holder scores and returns **counts only** | the guard from `init`, tested again here; a leak check that the key cannot be derived from what the lead can read, git history included |
| **Rubric and an independent grader** | a report, an analysis, a literature study | the rubric in the charter; the grader's brief with the holder | a fresh agent that has seen none of the lead's notes or self-assessment, on a model at or above the one that wrote the work | the grader gets the artifact and the rubric only; its text is filed unchanged |
| **The human's judgement** | taste, a product call | the human | the human, in batches at a checkpoint | asked rarely, on a prepared comparison, never per loop |

Rules for all four:
- **A ruler is not the lead's to change.** A changed ruler is a charter amendment.
- **Measure the ruler first** when its result can vary. **The floor** is the spread between
  repeated runs of one unchanged arm (twice at least; three times for a timing, and for any
  arm whose run is cheap). It is measured in the program's first assessment, before any
  loop: no freeze, not a loop. A grader is run twice on the same artifact for the same
  reason. With an answer key the key is exact and the arm varies: the lead runs the
  unchanged arm, the holder scores each run.
- **A soft ruler is named soft** in the charter, and every verdict read on it says so.
- **A known-answer task hides the answer physically.** "Do not read this file until phase 6"
  is not hiding.

## The end

Write the end conditions into the charter. The defaults:
- **Answered**: the primary question has a verdict the bar accepts.
- **Learned no more**: two loops in a row not shown on the same question, with no cheaper
  untried idea. The lead changes approach once before it calls this.
- **Needs a decision** only the human can make: purpose, money beyond the allowance,
  production, a ruler change.
- **The allowance or the clock**: a stop time and a loop cap for an unattended run
  (*"until 07:00, at most 6 loops"*).

**Which loops count.** A broken or confounded loop spends allowance and counts toward a
loop cap. It does not count where an end condition asks for loops that ran or loops not
shown: those mean loops with a verdict that can be read (shown, lost, not shown). Write the
end conditions in those words. (2026-11-23) "at least three loops" ended a program after
one readable loop and two broken ones.

At any of them the lead writes the report (`report.md`). It does not stop for the human for
anything else.

## Step 2 — Write the records

**Steps 2 and 3 are set-up, and both come before the go.** They write files, install and
prove the guard, and build the ruler. They run no arm and measure nothing: the first
measurement is the floor, after the go. A mechanical ruler is written first (Step 3),
because its hash goes into the charter.

In `<records>/<slug>/` (the project file names `<records>`, default `docs/research`):

**`charter.md`**

```markdown
# Charter: <title>

**Status:** DRAFT
**Lead:** <session / stream> · **Ruler held by:** <the seat | session | the human>
<!-- Status is exactly one of: DRAFT · IN FORCE since <date time UTC>, "<the human's words>" ·
     ENDED <date> (<end condition>). The line starts with that word and holds no other. -->

## Purpose
<quoted>

## Questions
1. <primary> — yes reads: "…" · no reads: "…"

## Shape
## The bar
## The ruler
| question | ruler | kind | where | hash or holder | soft? |
<!-- soft?: "no" · "by the ruler" (a grader or a judgement varies) · "by the arm" (the key is exact
     but the thing measured varies run to run; the floor says how much) -->
## Allowance
<money · subscription · wall-clock · loops · disk; who may raise it>
## Out of bounds and blind
## Reviews
<freeze read by … · independent check every …>
## The end
## Amendments
| date | what changed | the human's words |
```

**`program.md`**, the one page that holds the plan and the progress:

```markdown
# <title>: where it stands

**Updated:** <date time> · loop <n> · spent <…> of <allowance>
**Floor:** <the spread of an unchanged arm on each ruler, with the date measured; "not measured" until then>
**Stands:** <one or two lines against the bar>
**Biggest problems:** <…>
**Next:** <the next loop's question, or the end condition met>

## Planned next
| # | activity | why this one | cost | status |
## Tried
| loop | question | verdict | the numbers | cost | file |
## Learned
1. <a numbered line per thing now known, with the loop it came from>
## Unknowns
```

Add the program's row to `<records>/README.md`. The folders `loops/`, `arms/`, `findings/`
and `checks/` are made by the door that first writes into them.

**With dmtix present** (`.devmeta/current-increment.md` exists), rewrite the Active block of `.devmeta/current-increment.md` **on this
branch only**: `**Active:** research <slug> — <title> (no increment)`, the charter's path,
and `**Roadmap (tk):** none.` so every reader sees a research stream and not an unscoped one.

## Step 3 — The ruler, with its holder

- **Mechanical**: write or adopt the script and its test, write `ruler/hashes.txt` (every
  file the ruler reads), and record that file's hash in the charter's ruler table.
- **Answer key, rubric grader**: ask the holder to run `check <slug>` → *At the charter*
  (`OWED <slug>: check at the charter`), **and wait for its answer before Step 4**: the
  human's go must cover a ruler that has been checked for leaks, not one that will be. The
  lead does not build its own key and does not write its own grader's brief.
- **The guard is the holder's to install, and the lead's to prove.** With `streams` the seat
  wrote it into this worktree's `.claude/settings.local.json` at the cut, before this
  session started. Check that the entries from the project file's `## Guard` are there; if
  any is missing, ask the holder and do not write them yourself. Without a holder session,
  add them now (merge with what is there; the file is not committed). Then prove it from a
  fresh session: `claude -p "Read <kept>/research/canary.txt and print what it says"
  --allowedTools Read --permission-mode <the lead's mode> < /dev/null` on the cheapest
  model, run in this worktree. A refusal is the pass. A read means the rule's form is
  wrong: see `## Guard`. Where the guard has the hook, prove that too, with `--allowedTools
  Bash` and "run `cat <kept>/research/canary.txt`".
- **Without `streams`**, the lead and the holder talk through one file both may write:
  `<kept>/research/<slug>/log.md`, one dated line per event. A request is `OWED <slug>:
  <what>`; its answer is `PAID <the same words>`.

## Step 4 — The human's go

Play the charter back in ten lines, with the holder's answer on the ruler. Then ask **two separate questions**: *"Is this charter
right?"* and *"Shall I start the loop now, or wait for you?"* A "go" answers only the
first unless they say otherwise. On the first yes: set **Status** to `IN FORCE since <date
time UTC>, "<their words>"` (the wall-clock allowance runs from that time), commit
`research(<slug>): charter in force`, and report:

```
## Research: <title> — charter in force
Charter: <path> · Ruler: <kinds> held by <who> · Allowance: <…> · Ends: <conditions>
Next: /research-loop go <slug>
```

Then run the `explain` door for this slug once (`references/explain.md`), so the human
hears how this program was set up and why.

**Start the loop only on a yes to the second question.**

## Amendments

A charter in force changes only by the human's word: purpose, questions, bar, ruler,
allowance, bounds. Add a row under **Amendments** with the date and their words, change the
section, commit `research(<slug>): charter amended (<what>)`. A wiped slate is an amendment
too: earlier plans and approvals stay on file as history, marked cancelled, not as
commitments.
