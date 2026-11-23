## Purpose

Close a research program with its findings: what was asked, what is now known and how
firmly, what it changes, and what to do next. The report is what the human reads; the loop
files are its evidence.

Arguments: `report <slug>`. Run it in the lead's session when `go` reaches an end condition,
or when the human asks for a report early (then it is an interim report and the charter
stays in force).

`<records>` and `<kept>` below are the `records:` and `kept:` lines of `.devmeta/research.md`
(defaults `docs/research` and `~/<repo>-kept`).

## Step 1 — Before writing

1. Re-read the charter: the purpose in the human's words, each question's *yes reads* and
   *no reads* sentences, the bar, the end conditions.
2. Read `program.md` and every loop file's verdict. Build the answer from verdicts, never
   from the memory of the session.
3. **Ask for the independent check and the purpose review** if the last ones are older than
   the last loop the answer rests on (`check <slug> independent` and `check <slug> purpose`,
   the holder's). A report relayed before its numbers were re-derived says so on its first
   line.
4. Ask the purpose question once more: does the answer about to be written answer what was
   asked, or what was tested?

## Step 2 — Write `<records>/<slug>/report.md`

Short. A reader who stops after the first section has the answer.

```markdown
# <title>: findings (<date>)

**Ended by:** <answered | learned no more | needs a decision | allowance or clock | interim>
**Independent check:** <date, agrees / differs — or "not run">

## The answer
<Per question: the charter's own yes or no sentence, or "not shown", in one or two lines.
Then how firm: the ruler it rests on (soft or not), how many loops, how many cases, clear of
the floor by how much.>

## What it rests on
| question | loops | verdicts | the numbers | file |

## What it changes
<In the repository, the product or the next decision. What we believed before that is now
wrong, and what is confirmed.>

## What is not known
<Unmeasured, measured on too little, or read on a soft ruler. Each with what would settle it
and roughly at what cost.>

## What to do next
<One of, with the reason:>
- **Build it**: name the goal sentence and the likely parts in two or three lines, and the
  arm under `arms/` that showed it. With dmtix: `/dmtix start "<title>"`, pointed at this
  report as the source of truth. Without: the same lines are the task's description.
- **More research**: a new charter, with the question this one opened.
- **Decide**: what the human must decide, with the options and what each costs.
- **Stop**: why nothing further is worth its cost.

## Spend
<money · subscription by model · wall-clock · loops, against the allowance>
```

Rules for the text:
- **Every claim carries its loop.** A sentence with no loop behind it is an opinion: mark it
  as one or cut it.
- **Not shown is written as not shown**, never as a weak yes.
- **A verdict on a soft ruler says soft** in the same sentence.
- No client data, no key material, nothing from the kept folder's ruler.

## Step 3 — Close

1. `charter.md`: the **Status** line becomes `**Status:** ENDED <date> (<end condition>)`,
   with nothing else on it (not for an interim report). `program.md`: the status box says ended and points at the report.
2. `<records>/README.md`: the program's row gets its status and the report's path.
3. Commit `research(<slug>): report (<ended by>)`.
4. **Three lines plus the link**, to the holder and through it to the human: *the answer /
   what it rests on / what next*. With `streams`: a `coord.py log` line as well.
5. **Landing is the holder's.** With `streams` the seat lands the stream: its records reach
   the trunk. Without it, say that the branch is ready to merge. Never merge to the trunk
   from the lead's session.
6. **The kept folder**: list what the program left there (rulers, data, scores) with sizes,
   and what must be deleted (client data, by the project's rule) or kept. Deleting is the
   human's word.

**Do not start `/dmtix start`, a new charter or a merge yourself.** Each is the human's call.
