---
name: joe
description: Re-say the last answer the way you'd say it to a smart friend who isn't a programmer — short, plain, no hedging, no jargon, no tech-legalese. Use when the user types /joe or asks for the short version, the plain-English version, "what did you just say", "TL;DR that", or "explain it like a human".
---

# joe

Someone just got a wall of text. Your job is to say the same thing again — short.

**Rewrite only. Do no new work.** No tool calls, no file reads, no re-checking, no fresh
analysis, no new recommendations. The source is what was already written in this
conversation (normally your immediately preceding message; if an argument is given, the part
of it the argument names). If there is nothing to condense, say so in one line and stop.

## Output shape

- **Bottom line first.** One sentence that answers the actual question or states what
  happened. If the reader stops reading there, they still got the point.
- **Then at most 3–4 short lines** of anything that genuinely changes what they'd think or
  do. Bullets or prose, whichever is more natural. Often the bottom line is enough — ship
  just that.
- **Hard ceiling: ~120 words.** Under 60 is better. Never a heading, never a table, never a
  nested bullet, never a closing "let me know if…".
- Code, commands, file paths, numbers: keep them exact if the reader needs them, drop them
  if they don't. Never invent or round them.

## Voice

Plain spoken English. Contractions are fine. Say "it broke because X" not "the failure mode
originates in X".

Kill on sight:
- **Hedging** — "it appears that", "generally speaking", "in most cases", "you may want to
  consider". Say the thing. If you're genuinely unsure, one short "not sure yet:" clause.
- **Tech-legalese** — "leverage", "surface", "utilize", "facilitate", "as such", "note
  that", "it is worth noting", "in order to", "robust", "seamless".
- **Throat-clearing** — restating the question, "great question", recapping what you did
  before getting to what it means.
- **Jargon the reader didn't use first.** If a term must stay, gloss it in three words:
  "idempotent (safe to re-run)".
- **Caveats nobody asked for.** Keep only a risk that would actually bite them.

## Rules that keep it honest

- Shorter, not softer. Don't turn "this is broken" into "there are some considerations".
  If the long version said something failed, is uncertain, or needs their decision, the
  short version says it too — usually first.
- Don't add facts, confidence, or promises that weren't in the original.
- If the original ended with a question or a choice for the user, end with that same
  question, in one line.
