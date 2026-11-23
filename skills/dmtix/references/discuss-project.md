## Context

- Determine today's date with `date +%Y-%m-%d`.
- The project idea may be passed as the argument after `discuss-project`
  (e.g. `/dmtix discuss-project "offline sync"`). With no argument, open the dialogue
  with the question in Step 1.

## Purpose

An open, Claude-led discussion about a project the human wants to do but cannot yet scope.
It is the step *before* `/dmtix start`: it runs until the project is understood well enough
that an increment spec can be written without guessing. This command is a **door, not an
engine**: it talks, researches the repo, and writes thought documents under `docs/thoughts/`.
It never creates ticks, never touches `.tick/` or `.devmeta/`, and never writes code.

The output is **shared understanding**, captured in a document, that ends with one of three
verdicts: *ready for `/dmtix start`*, *not ready — these unknowns remain*, or *don't do it*.
All three are good outcomes.

## Step 1 — Open the discussion (Claude starts)

Begin with the question, in plain words: **"What is the project you want to do?"** (skip if
passed as the argument; restate it back in one or two sentences instead and ask whether
that's right). Then follow the human's thread. Don't hand over a questionnaire; ask one or
two questions at a time, and let the answers decide the next question.

## Step 1b — Agree how to run this discussion (an open question to the user)

Once you have the gist of the project, and before digging in, decide *with the user* how
this discussion is organized. Do not decide it for them. Say what you see, then ask:

1. **What kind of project is it?** Work out which of these two it is, say which you think and
   why, and let the user correct you:
   - **Development:** the outcome is known, so it can be specified, built and tested
     against checkable criteria. This is what `/dmtix start` and `go` are made for.
   - **Research / exploration:** the output is knowledge, a decision, or a go/no-go, and
     "done" is not a shipped feature. Its shape varies: sometimes one focused pass to an
     answer, sometimes a number of loops that each learn something and build on the last.
     Don't assume loops; find out which fits this question, and don't force a fixed spec
     onto it. Its run is not `/dmtix start`: it is the `research-loop` skill
     (`/research-loop charter`), when that skill is installed.
   Many projects are a mix; say which parts are which.
2. **How should we organize this discussion?** Offer the shape that fits, e.g. a short
   talk-through to a spec, or a longer discussion with research notes kept in the thought
   directory, or splitting it up (see below). Ask what they want.
3. **When do we slip from discussing into defining the project?** Ask what would make them
   feel ready, and offer your own proposed trigger (e.g. "when the blocking unknowns are
   resolved or parked"). Revisit this at each checkpoint (Step 5); the answer can change.

Rules this sets:

- **The discussion is not the project.** It exists to understand and to find unknowns, not
  to do the work. Don't build the thing, and don't quietly produce the project's deliverable
  as "research". If the project *is* research or exploration, the discussion defines the
  question, the method, what counts as an answer, and when to stop. It does not carry out
  the research.
- **Deep investigation and prototypes: suggest, don't just do.** Light checks that settle
  an unknown in minutes (read the code, a quick lookup, a small experiment) belong in the
  discussion. When an unknown needs real investigation, a spike, or a prototype, say so and
  put it to the user as a choice: *split the work into several projects, the first being
  that exploration* (then this document defines the exploration as its own project, and
  the main project waits on its answer), *or do a bounded piece of it here and now* (agree
  what, and how far, first), *or park it as a non-blocking unknown*. The user may not want
  to split it, and may want something explored right now. That is their call. Record what was
  chosen and why under **Decisions made**.

## Step 2 — Create the thought document

Location: `docs/thoughts/` at the repo root (create if missing). Name:
`YYYY-MM-DD-<slug>` — today's date, a short kebab-case slug of the project.

- **Start as a single file:** `docs/thoughts/YYYY-MM-DD-<slug>.md`.
- **Promote to a directory** the moment the discussion needs more than one markdown file or
  any non-markdown artifact (images, sketches, downloaded documents, data samples,
  fetched references): `git mv` the file to
  `docs/thoughts/YYYY-MM-DD-<slug>/README.md` (same name minus `.md`, the old file becomes the
  directory's `README.md`), and keep everything else beside it. Tell the user when you do.
- If a thought document for this project already exists, resume it — read it first, and
  append rather than start over. Never silently overwrite.

Document skeleton (grow it as the discussion goes; keep it short and current, not a
transcript):

```markdown
# <Project title>

**Date:** <date> · **Status:** DISCUSSING (→ READY FOR START | NOT READY | DROPPED)

## Purpose
What problem, for whom, and what is different afterwards. In the human's words where possible.

## Context — where this lands
What exists today (repo / org conventions, adjacent code, constraints). Cite paths.

## Shape
How it is supposed to work, in the current best understanding (the outline Claude has been
checking with the human).

## Decisions made
| Decision | Why | Alternatives rejected |
|---|---|---|

## Unknowns
| # | Unknown | Kind (knowledge / decision / dependency / human-taste) | How it gets resolved | Blocks start? |
|---|---|---|---|---|

## Out of scope (so far)

## Verdict
<ready for /dmtix start — with the goal sentence · not ready — what remains · dropped — why>
```

## Step 3 — Orient in the real world (not optional)

The discussion must be grounded in what is actually there, not in what a project like this
usually looks like. Early on, and again whenever the topic shifts, **go look** — then say
what you found and how it changes the picture:

- The current repo: structure, the code the project would touch or sit beside, existing
  patterns, tests, build and deploy, `CLAUDE.md`/docs, past increments in `.devmeta/` and
  earlier `docs/thoughts/`, recent git history in the area.
- **Other repos.** Ask the user early: "Which other repos or services does this touch,
  sit beside, or should copy from?" Get paths or URLs, then look at them the same way. Don't
  guess that a project is single-repo.
- How this organization typically does things: conventions, stack, naming, how similar
  features were built, infrastructure and service boundaries (the other repos above are
  the best evidence).
- Outside knowledge the project hinges on (an API, a library, a standard): research it, and
  save the useful material into the thought directory (promote to a directory if needed).

Record findings in **Context**, cited by path. If something the human assumes conflicts with
what you find, say so plainly — that is the most valuable thing this step produces.

## Step 4 — Find the unknowns

The core job. Keep the **Unknowns** table honest and visible. Hunt for:

- **Knowledge we don't have** — how does X actually behave, what does that API allow, what
  do users really do today, what does it cost, what is the data like.
- **Decisions not yet made** — architecture, build vs. reuse, where it lives, data model,
  migration, who owns it, what it replaces.
- **Dependencies** — other teams, accounts, keys, environments, approvals.
- **Human-taste items** — things only the human can judge once they see them.
- **Edges** — failure modes, scale, security, rollout, how we'd know it works.

For each unknown, say how it gets resolved: ask the human now, a light check now, a spike or
prototype (name it — and per Step 1b, offer to make it its own project rather than doing it
here), or a decision to make before start. Resolve what can be resolved in the
discussion; the rest stays in the table, marked whether it **blocks start**. An unknown that
could change the epic partition or an epic's definition of done blocks start.

## Step 5 — Checkpoints: outline and challenge

Roughly every time the picture has materially firmed up — at least two or three times in a
real discussion, and always once before any verdict — **stop and play it back**:

1. Give a compact outline (5–10 lines): the purpose, how it is supposed to work, the main
   parts, what it touches, what is excluded, the biggest open unknowns.
2. Then challenge the human directly, to engage their intuition and smell:
   - "Does this match what you have in your head? What's off?"
   - "What's missing that you'd expect to see here?"
   - "Which part of this are you least sure about, or would be most surprised by if it
     went wrong?"
   - "Anything here that sounds easy but you suspect isn't?"
   Add your own sharpest doubt too — name the weakest assumption you see and argue the
   opposite side once. Do not accept a quick "looks fine" on the first pass for a
   checkpoint that matters; ask what *specifically* they checked.
3. Fold the answers into the document (Decisions, Unknowns, Shape) before continuing.
4. Re-ask the Step 1b questions in a line: still the right way to run this? Is it time to
   slip into defining the project, or should something be split off or explored first?

## Step 6 — Close the discussion

The discussion is done when, and only when, you and the human can both say the project is
well defined: the purpose is clear, the shape is clear, the main unknowns are resolved or
consciously parked as non-blocking, and it is clear what would need doing and roughly how.
If the work turned out to be several projects, the verdict names them and their order (often
an exploration first), and each gets its own `/dmtix start` when its time comes. Test it:
write the **goal sentence** an increment spec would open with ("afterwards the user
can …") and the likely epic outline in two or three lines. If you can't, it isn't ready.

Set the **Verdict** and **Status** in the document, commit it
(`thoughts(<slug>): <verdict>` — `docs/thoughts/` only), and report:

```
## Discussion: <title> — <verdict>
Document: <path> · Open unknowns: <n> (<m> block start)
Next: /dmtix start "<title>"   (or: resolve <unknowns> first)
```

**When the project, or its first part, is research:** the next door is not `/dmtix start`.
Say so in the verdict, and report `Next: /research-loop charter <slug>` with this document as
the charter's raw material (purpose, decisions, unknowns). If the `research-loop` skill is not
installed, say that and name it (`npx skills add mkelk/skills --skill research-loop`). A mixed
project names both, in order: often the research first, and the increment its report defines.

If ready, tell the user that `/dmtix start` should be pointed at this document as the source
of truth for the increment. **Do NOT start `/dmtix start` yourself, create ticks, or plan epic
internals** — that is the next door, and it is the human's call.
