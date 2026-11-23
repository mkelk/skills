#!/usr/bin/env python3
"""A tripwire for a research lead's worktree: refuse any tool call that names a guarded path.

A `Read(...)` deny rule stops the Read tool only; `cat` in a shell still reads the file. This
hook looks at every tool call's input (a command, a path, a pattern) and refuses the call
when it names a guarded path. It is a tripwire, not a sandbox: a path built from pieces, or
reached after a `cd`, gets past it. For a key that matters, keep the key where the lead's
user cannot read it.

Install it as a PreToolUse hook in the lead's worktree, `.claude/settings.local.json`:

    "hooks": { "PreToolUse": [ { "hooks": [ { "type": "command",
      "command": "python3 <this file> '~/repo-kept/research/*/ruler' '~/repo-kept/research/canary.txt'"
    } ] } ] }

Each argument is a path; `*` stands for one folder name; `~` is the home folder. The call is
refused when its input contains the path written with `~`, with `$HOME`, or in full.

Exit 0: allowed. Exit 2: refused, with the reason on stderr (Claude Code shows it to the
session). Python 3.9+, standard library only.
"""
import json
import os
import re
import sys


def patterns(paths, home):
    """One regex per guarded path, matching it written with ~, $HOME, ${HOME} or in full."""
    out = []
    for p in paths:
        p = p.rstrip("/")
        if p.startswith("~/"):
            tail = p[1:]
        elif p.startswith(home + "/"):
            tail = p[len(home):]
        else:
            tail = None
        body = "[^/\\s'\"]+".join(re.escape(part) for part in (tail if tail is not None else p).split("*"))
        if tail is not None:
            heads = "(?:~|\\$HOME|\\$\\{HOME\\}|" + re.escape(home) + ")"
            out.append((p, re.compile(heads + body)))
        else:
            out.append((p, re.compile(body)))
    return out


def strings(value):
    """Every string inside a JSON value."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def refused(tool_input, pats):
    """The guarded path a tool input names, or None."""
    for s in strings(tool_input):
        for path, rx in pats:
            if rx.search(s):
                return path
    return None


def main(argv):
    if len(argv) < 2:
        print("guard-hook: give at least one guarded path", file=sys.stderr)
        return 0
    try:
        call = json.load(sys.stdin)
    except ValueError:
        return 0
    hit = refused(call.get("tool_input"), patterns(argv[1:], os.path.expanduser("~")))
    if hit:
        print(f"research guard: this call names {hit}, which a lead must not read. "
              "Ask the ruler's holder for counts; do not look for another way in.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
