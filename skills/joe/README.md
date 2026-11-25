# joe

Type `/joe` right after a long agent answer and get the same answer back — short, plain,
and without the tech-legalese.

## Why

Agents over-explain. They hedge, they recap, they add caveats nobody asked for, and the one
sentence you actually needed is buried in paragraph four. `joe` pulls that sentence out.

## Use

```
/joe              # condense the message that just came in
/joe the risks    # condense just that part of it
```

It rewrites only — no new tool calls, no fresh analysis, no new recommendations. Bottom line
first, ~120 words max, and it stays honest: if the long version said something is broken or
needs your decision, the short one says it too.

## When not to use it

- You want new analysis, a check or a recommendation. `joe` only re-says what is already
  written.
- The long answer is the point, such as a spec or a report to keep. Shortening it loses
  detail.

## What it never does

- Run tools, read files or re-check anything.
- Add facts, confidence or advice that the long version did not have.
- Soften a failure or hide a decision that is yours to make.

## Install

```bash
npx skills add mkelk/skills --skill joe -g -a claude-code
```

## License

MIT.
