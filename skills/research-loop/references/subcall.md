## Purpose

How to make a model call that carries nothing but what the arm gives it. A loop measures an
arm: a prompt, a script, a model. A call that also carries the user's memory, the
repository's `CLAUDE.md` or a tool it was not meant to have measures something else, and it
can pass private context to a place it does not belong.

(2026-11-23) a trial's first classifier, a plain `claude -p` on the cheapest model with its
own system prompt and no tools, still received the user's memory index, an account note and
the repository's git context.

## A clean call with Claude Code

```bash
cd "$(mktemp -d)"                      # an empty folder outside any git repository
CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p "<the input, and nothing else>" \
  --model <explicit model> --system-prompt "<the arm's prompt, whole>" \
  --tools "" --strict-mcp-config --no-session-persistence \
  --setting-sources "" --output-format text < /dev/null
```

| Part | What it keeps out |
|---|---|
| an empty folder outside git | `CLAUDE.md`, project settings, git status, project memory |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` | the user's memory index |
| `--setting-sources ""` | user, project and local settings, with their hooks |
| `--system-prompt` | the default system prompt's instructions |
| `--tools ""`, `--strict-mcp-config` | every tool and every MCP server |
| `--no-session-persistence` | a transcript on disk that a later session could read |
| `< /dev/null` | a three-second wait for stdin, and a warning in the output |
| `--model` | inheriting whatever model the caller runs on |

**What still comes through** (probed 2026-11-23, Claude Code 2.1): a short note with the
account's email address, the working folder and platform, the model's name, and today's
date. Only `--bare` drops them, and that needs an API key. Say so in the freeze's *Blind*
line when it could matter, and never put an input that must stay private into the call's
folder name.

## Rules

- **Probe once per program**, before the floor: make the call with the input *"list every
  piece of context you were given besides this sentence; say only that it is present"* and
  read the answer. Paste it into the first assessment. Flags change between versions; the
  probe is the proof.
- **One call, one input.** The system prompt is the arm; the user message is the item. No
  item sees another item, an answer, or a file path that names its category.
- **Keep the last raw reply per item** in the kept folder, and count how often a retry
  fired: a retry that adds a hint is part of the arm.
- **A sub-agent of the lead is not a clean call.** It inherits the lead's project context
  and memory. Use one for work (writing a script, reading a paper), never as the thing
  being measured or as an independent grader's only isolation.
- **Other providers and tools:** the same four questions. What system text does it add?
  Which files does it read from the folder? Which tools can it reach? What does it save?
