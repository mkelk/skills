## Purpose

Define one research program with the human: what it is for, what would count as an answer,
what it is measured by, what it may spend, and when it ends. The charter is the only thing
the loop obeys besides this skill. **Nothing runs before the human's go**, and their words
are recorded.

Arguments: `charter <slug>`. Run it in the lead's session: in the stream's worktree when the
repository uses `streams`, else on a branch `research/<slug>`. Never on the trunk.

## Step 0 — Where this comes from

- **Project file.** `.devmeta/research.md` must exist; if not, point at `init` and stop.
- **A discussion.** If a `/dmtix discuss-project` thought document led here, read it first:
  its purpose, decisions and unknowns are the charter's raw material. If the stream has a
  brief (`docs/thoughts/<date>-<slug>-brief.md`), read that too.
- **An existing program.** If `<records>/<slug>/charter.md` exists, resume it. Never
  overwrite a charter that is in force: a change to one is an amendment (last section).

## Step 1 — The dialogue

A few questions at a time. Restate, propose, and let the human correct.

1. **Purpose, in the human's words.** What is this for, and what will be decided or known
   afterwards? Quote them. A purpose the lead paraphrased is one it will drift from.
2. **The questions.** One primary, at most two secondary. Each must be answerable: write the
   sentence the report would open with if the answer were yes, and if it were no.
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
8. **Reviews.** Who reads a freeze before it runs (the holder, or nobody for an unattended
   run), and how often the independent check runs (`check.md`).
9. **The end** (below).

## The ruler

Pick per question. A program may use more than one; say which decides.

| Kind | Fits | Where it lives | Who scores | What keeps it honest |
|---|---|---|---|---|
| **Mechanical**: a script, test or benchmark | a speed-up that must keep outputs identical; a ported model whose output must match a reference within a tolerance | in git, under `<records>/<slug>/ruler/` or the repository's own scripts; reference data read-only | the lead runs it | its hash is written in the charter (`git hash-object`); a loop that finds it changed is broken. The tolerance is the human's and is set before the first run |
| **Answer key**: held-out truth | past cases with known causes; a known-answer redo; a list of the papers that matter | the kept folder, `<kept>/research/<slug>/ruler/`, never in git or a worktree | the holder scores and returns **counts only** | the guard from `init`, tested again here; a leak check that the key cannot be derived from what the lead can read, git history included |
| **Rubric and an independent grader** | a report, an analysis, a literature study | the rubric in the charter; the grader's brief with the holder | a fresh agent that has seen none of the lead's notes or self-assessment, on a model at or above the one that wrote the work | the grader gets the artifact and the rubric only; its text is filed unchanged |
| **The human's judgement** | taste, a product call | the human | the human, in batches at a checkpoint | asked rarely, on a prepared comparison, never per loop |

Rules for all four:
- **A ruler is not the lead's to change.** A changed ruler is a charter amendment.
- **Measure the ruler first** when its result can vary: run one arm twice and record the
  spread as the floor. A grader is run twice on the same artifact for the same reason.
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

At any of them the lead writes the report (`report.md`). It does not stop for the human for
anything else.

## Step 2 — Write the records

In `<records>/<slug>/` (the project file names `<records>`, default `docs/research`):

**`charter.md`**

```markdown
# Charter: <title>

**Status:** DRAFT (→ IN FORCE since <date>, "<the human's words>" | ENDED <date>)
**Lead:** <session / stream> · **Ruler held by:** <the seat | session | the human>

## Purpose
<quoted>

## Questions
1. <primary> — yes reads: "…" · no reads: "…"

## Shape
## The bar
## The ruler
| question | ruler | kind | where | hash or holder | soft? |
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

Also create `loops/`, `findings/` and `checks/`, and add the program's row to
`<records>/README.md`.

**With dmtix present**, rewrite the Active block of `.devmeta/current-increment.md` **on this
branch only**: `**Active:** research <slug> — <title> (no increment)`, the charter's path,
and `**Roadmap (tk):** none.` so every reader sees a research stream and not an unscoped one.

## Step 3 — The ruler, with its holder

- **Mechanical**: write or adopt the script and its test, record `git hash-object <file>` in
  the charter's ruler table.
- **Answer key, rubric grader**: ask the holder to run `check <slug>` → *At the charter*. The
  lead does not build its own key and does not write its own grader's brief.
- Re-run the guard's canary test from this worktree, in the permission mode the loop will
  run in. A refusal is the pass.

## Step 4 — The human's go

Play the charter back in ten lines and ask for the go. On it: set **Status** to IN FORCE with
the date and their words, commit `research(<slug>): charter in force`, and report:

```
## Research: <title> — charter in force
Charter: <path> · Ruler: <kinds> held by <who> · Allowance: <…> · Ends: <conditions>
Next: /research-loop go <slug>
```

Then run `explain <slug>` once, so the human hears how this program was set up and why.

**Do not start the loop yourself** unless the human's go said so.

## Amendments

A charter in force changes only by the human's word: purpose, questions, bar, ruler,
allowance, bounds. Add a row under **Amendments** with the date and their words, change the
section, commit `research(<slug>): charter amended (<what>)`. A wiped slate is an amendment
too: earlier plans and approvals stay on file as history, marked cancelled, not as
commitments.
