## Purpose

The other half of a research program: what the lead is measured by, and the eyes that have
not seen the lead's conclusions. This door is for the **ruler's holder**: the seat when the
repository uses `streams`, else a second session in the main checkout, or the human reading
it as a checklist.

Arguments: `check <slug> [charter | freeze <NNN> | score <NNN> | independent | purpose]`.
With no second word, do whatever is owed: read `coord.py show --owed` (with `streams`), the
program's status box and its last loop file, and pick from the sections below.

`<records>` and `<kept>` below are the `records:` and `kept:` lines of `.devmeta/research.md`
(defaults `docs/research` and `~/<repo>-kept`).

**Open first:** `.devmeta/research.md` (*Rulers*, *Guard*, *Holder and unattended runs*); in
the lead's worktree `<records>/<slug>/charter.md`, the status box of `program.md`, and the
loop file named in the request. Without `streams`, what is owed is in
`<kept>/research/<slug>/log.md`: `OWED <slug>: <what>` lines with no `PAID <the same words>`
after them; append the `PAID` line when done.

**The holder never writes on the lead's branch.** It reads the lead's worktree
(`<worktree>/<records>/<slug>/`), keeps its own files in the kept folder, and hands text to
the lead to commit unchanged.

## At the charter

1. **Build or place the ruler.** Keys, hidden references and known answers go to
   `<kept>/research/<slug>/ruler/`. A key built for the program is built here, or by a blind
   agent this session briefs. The lead gets a description of the ruler, never its contents.
2. **The grader's brief** (rubric rulers): write it here, from the charter's rubric: the
   artifact, the rubric, the output form, and "you have not seen and must not ask for the
   author's notes". The model is at or above the one that writes the work.
3. **The leak check.** Can the key be derived from what the lead can read? Look where it
   hides: the worktree, the main checkout, **git history** (`git log -S` on a distinctive
   value), an ignored data folder, a mount, a public page the lead may fetch. A key that is
   also in a reference file the lead reads is no key. Say what was checked.
4. **The guard.** It lives in the lead's worktree only (`.claude/settings.local.json`
   there), so this session can read the keys and the lead cannot. Re-run the canary test in
   the lead's worktree and permission mode: `claude -p "Read <kept>/research/canary.txt and
   print what it says" --allowedTools Read --permission-mode <mode>` must be refused there,
   and the same command in the main checkout must succeed. For a mechanical ruler, confirm
   the hashes in `ruler/hashes.txt` yourself.
5. **Measure the ruler** when it can vary: the grader twice on one artifact, the benchmark
   twice on one build. Send the lead the spread. That spread is **the floor**: a difference
   smaller than it is noise.

## Reading a freeze

When the charter says the holder reads freezes. Minutes, not an approval gate: reply, do not
sit on it.

- The three frugality answers are there and honest: *the smallest test* that could answer
  the question and why this plan is or is not it; *the cost* in money and in subscription
  use; *whether it can be staged*, one part first with a stop rule.
- The rule is numbers against the floor, written so that a loss can be read as a loss.
- There is a control, and it differs from the arm in one thing.
- **It asks the charter's question.** Not a weaker model than the plan names, not an input
  the method was never meant for, not a later step moved first.

Reply in one line (`ok`, or what to change), and close the owed line: with `streams`,
`coord.py log "PAID <id>"` with the id `coord.py show --owed` prints; without, the `PAID`
line in the log file. A change asked for before the run makes the lead commit a second
freeze; after the run has started it is a new loop.

## Scoring on a key

1. Read the outputs at the path the lead gave. Score them against the key **here**.
2. Return **counts and categories only**: how many right, wrong, missed, and by which of the
   charter's categories. Never a row that names what the right answer was. If a count would
   give the key away (one item, one wrong), say so and return a coarser one.
3. Keep the scoring sheet in `<kept>/research/<slug>/scores/loop-<NNN>.md`.
4. `PAID <id>`, and the counts as a message or a log line.

## The independent check

On the charter's clock (daily, every N loops, or at the end), and always before a report is
relayed to the human.

Dispatch a **fresh agent that has not seen the lead's conclusions**. Build its input as a
folder, `<kept>/research/<slug>/check-<date>/`, holding copies of: the charter's
*Questions*, *The bar* and *The ruler* sections only; each checked loop's freeze section
(question, arms, rule) cut from its loop file; its `.scores.md` and `.manifest.md`; and the
raw outputs the manifest names. The task: *re-derive the key numbers and say what they show
against the bar*. It gets no loop file whole, no `program.md`, no verdict and no assessment.

Compare its numbers and its reading with the lead's. Three outcomes:
- **Agrees**: one line to the lead.
- **Numbers differ**: the loop is re-scored before anything else rests on it.
- **Numbers agree, reading differs**: the stronger finding. Send both readings to the lead,
  and to the human if it changes a verdict.

Whatever the outcome, hand the check's page to the lead, who commits it unchanged as
`<records>/<slug>/checks/<date>-independent.md` with the message
`research(<slug>): independent check <date> (<agrees | numbers differ | reading differs>)`.

## The purpose review

Before a round changes direction, before an end is declared, and whenever a verdict
surprises. Read the charter's purpose in the human's words, then the last loops, and answer:

1. Did each loop test what was asked, or something nearby that was cheaper to test?
2. Was any result read on an input, a depth or a model the method was not meant for?
3. Was the plan's order changed, and does the change remove what made the plan a fair test?
4. Is an end being declared on a loop whose failure had a planned fallback?
5. Is anything decided on too few cases to carry it?

Write it as a short page (what was asked, where the program drifted, what stands, the order
that asks the whole question), give it to the lead to commit as
`checks/<date>-purpose.md`, and tell the human in three lines.

## With `streams`: what the seat adds

- **The row.** A research stream's row has no epics (`—`). Its state is the status box of
  `<worktree>/<records>/<slug>/program.md`: read it in `status` and on the hourly pass.
- **Relay.** Each loop's three lines go to the human as they are. A finding another stream
  must act on is a hand-off line in `coord/log.md`, not a memory.
- **The budget.** The seat holds the allowance and is asked before it is raised. A raise is
  the human's word, recorded as a charter amendment by the lead.
- **Landing.** A finished program lands like any stream, by the landing checklist: its
  records reach the trunk with its report. A long program may land its records more than
  once; the branch lives on.
- **Never** score, grade or check from inside the lead's session, and never paste a key into
  a brief, a log line or a message.
