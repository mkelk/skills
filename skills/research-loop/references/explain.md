## Purpose

Say, to a human, what this skill does in this repository and how it was adapted, in words
they could repeat to a colleague. `init` and `charter` each end by running this door; it can
also be asked for at any time.

Arguments: `explain [<slug>]`. Read-only: it writes nothing.

`<records>` and `<kept>` below are the `records:` and `kept:` lines of `.devmeta/research.md`
(defaults `docs/research` and `~/<repo>-kept`).

## What to read

- `.devmeta/research.md`: every section, and `## How we do research here` first. If that
  section disagrees with the sections below it, the sections are right: say so, and offer
  to rewrite it.
- With a slug: `<records>/<slug>/charter.md` and the status box of `program.md`.
- `.devmeta/streams.md` when present: who the seat is, the standing rules.

If the project file is missing, say that the skill is installed but not set up here, and
that `init` is the next step. Do not explain a setup that does not exist.

## What to say

Plain sentences, no jargon the human did not use first, 15 lines at most without a slug and
25 with one. In this order:

1. **What it is for.** Questions whose answer is knowledge or a decision. Building is
   dmtix's.
2. **How it runs.** Two roles (the lead runs the loop; the ruler's holder owns what it is
   measured by). The loop: assess, freeze, run, score, verdict, record. The rule is written
   and committed before each run. It does not wait for the human except for money beyond
   the allowance, production, a ruler change or a change of purpose.
3. **How this repository adapted it**, each with its reason:
   - what was adopted from a loop the repository already had, and which gaps the skill
     filled;
   - which rulers exist here and who holds each;
   - where records live, and where the kept folder is and what stays in it;
   - the allowance and who may raise it;
   - what is out of bounds, and the fetching rule if there is one;
   - the guard, how it was tested, and what it does not cover.
4. **With a slug, this program's choices:** its purpose in the human's own words, its
   questions, its bar, its ruler, its allowance, how it ends, and where it stands now.
5. **What the human does:** give the go on a charter; read three lines per loop; decide what
   only they can decide; read the report.
6. **What to type next.**

End with one question back: *"Is any of this not how you want it to work?"* An answer that
changes a fact is a change to the project file (`init --force` keeps the rest) or a charter
amendment, made on their word.
