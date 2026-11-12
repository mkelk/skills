#!/usr/bin/env python3
"""Stop hook for the seat: remind the human to /compact when the seat's context grows large.

The idle tidy (compact-idle.py) never compacts the seat, so the seat's own context is watched here. At the end of
every turn this reads the newest model call's usage from the session transcript (the same sum compact-idle.py uses)
and, past SEAT_COMPACT_REMIND_AT tokens, prints a one-line systemMessage. It reminds again only after the context has
grown another SEAT_COMPACT_REMIND_STEP tokens, and starts over after a compaction (the context drops). Never blocks,
never fails a turn: any error prints nothing.

The human, 2026-10-28: "could you make some kind of monitor and alert in seat so am reminded when it is time to
compact?"

State, one small file per session: $XDG_CACHE_HOME/streams-seat-compact/ (default ~/.cache/streams-seat-compact/).
"""
import json
import os
import sys

REMIND_AT = int(os.environ.get("SEAT_COMPACT_REMIND_AT", "200000"))
STEP = int(os.environ.get("SEAT_COMPACT_REMIND_STEP", "30000"))
TAIL_BYTES = 4 * 1024 * 1024


def last_context_tokens(path):
    with open(path, "rb") as fh:
        fh.seek(0, os.SEEK_END)
        fh.seek(max(0, fh.tell() - TAIL_BYTES))
        lines = fh.read().decode("utf-8", errors="replace").splitlines()
    for line in reversed(lines):
        if '"usage"' not in line:
            continue
        try:
            msg = json.loads(line).get("message")
        except json.JSONDecodeError:
            continue
        usage = msg.get("usage") if isinstance(msg, dict) else None
        if usage:
            return (usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
                    + usage.get("cache_creation_input_tokens", 0))
    return None


def state_dir():
    cache = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(cache, "streams-seat-compact")


def main():
    hook = json.load(sys.stdin)
    path = hook.get("transcript_path")
    session = os.path.basename(str(hook.get("session_id", "unknown")))
    if not path or not os.path.exists(path):
        return
    tokens = last_context_tokens(path)
    if tokens is None:
        return
    directory = state_dir()
    os.makedirs(directory, exist_ok=True)
    state = os.path.join(directory, session)
    try:
        with open(state) as fh:
            last = int(fh.read().strip() or 0)
    except (FileNotFoundError, ValueError):
        last = 0
    if tokens < REMIND_AT:
        if last:
            os.remove(state)  # compacted, or never reached: start over
        return
    if last and tokens < last + STEP:
        return
    with open(state, "w") as fh:
        fh.write(str(tokens))
    print(json.dumps({"systemMessage": f"seat context {tokens // 1000}k (reminder from {REMIND_AT // 1000}k): "
                                       "time to /compact when the streams are quiet"}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
