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

## Install

```bash
npx skills add mkelk/skills --skill joe -g -a claude-code
```

## License

MIT.
