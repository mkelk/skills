#!/usr/bin/env python3
"""Compact idle stream sessions (the streams skill's `compact` door, references/compact.md).

The long-running stream sessions build a very large context during long waits, and every call resends it
(2026-10-27). This finds the stream sessions that are idle, large and quiet, and sends each one `/compact`
with instructions, through herdr. That is the only route: no session can compact itself (no tool, hook or
skill can run a built-in slash command). Without herdr there is no way in from outside: the per-worktree
`autoCompactWindow` is the safety net, and the human can type `/compact` in a pane.

A session is compacted only when ALL of these hold:
  - herdr shows a claude agent whose cwd is a stream's worktree in the live table (never the main checkout,
    so never the seat);
  - herdr says it is `idle` or `done` (not `working`, not waiting on a permission);
  - its context (the last call's input + cache tokens in its newest transcript) is at least --min-tokens;
  - its transcript has not moved for at least --quiet-minutes (nothing in flight);
  - no unexpired HOLD in the coord log names the stream, its worktree, or its pane, as what is held or
    as the holder (read with this directory's coord.py).

Dry run by default. `--apply` sends; each send is logged to coord as the seat. `--only <stream>` limits it
to one stream. Run it from any checkout of the repository.

    python3 <skill dir>/scripts/compact-idle.py            # what would be compacted, and why not
    python3 <skill dir>/scripts/compact-idle.py --apply --only <stream>

Defaults come from the environment when set: COMPACT_MIN_TOKENS (150000), COMPACT_QUIET_MINUTES (30).
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coord  # noqa: E402  (the skill's own helper, beside this file)

MIN_TOKENS = int(os.environ.get("COMPACT_MIN_TOKENS", "150000"))
QUIET_MINUTES = int(os.environ.get("COMPACT_QUIET_MINUTES", "30"))

COMPACT_INSTRUCTIONS = (
    "/compact Keep: who you are (stream, increment, worktree, branch, ports) and your standing rules; "
    "the task in progress and its next step; what you are waiting for, from whom and when (with times); "
    "open HOLD and OWED lines; decisions the human made, with their dates; anything you promised to report. "
    "Drop: finished threads, tool output already written to files or commits, superseded plans, old message text."
)


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def repo_root():
    return sh(["git", "rev-parse", "--show-toplevel"]).stdout.strip()


def main_checkout():
    """The main checkout: the directory that holds git's common directory."""
    common = sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"]).stdout.strip()
    return os.path.realpath(os.path.dirname(common)) if common else os.path.realpath(repo_root())


def streams_from_table(directory):
    """{absolute worktree path: stream name} from the live table's rows, columns found by header name."""
    rows = {}
    path = os.path.join(directory, coord.STREAMS)
    if not os.path.exists(path):
        sys.exit(f"no live table at {path}: nothing to compact (coord.py init creates it)")
    header = None
    for line in open(path, encoding="utf-8"):
        if not line.strip().startswith("|"):
            header = None  # a table starts again after any other line
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set(":-") and c for c in cells):
            continue
        try:
            name = cells[header.index("stream")]
            worktree = cells[header.index("worktree")].strip("`")
        except (ValueError, IndexError):
            continue
        if not name or not worktree or worktree in ("—", "-"):
            continue
        rows[os.path.realpath(os.path.expanduser(worktree))] = name
    return rows


def herdr_agents():
    try:
        out = sh(["herdr", "agent", "list"])
    except FileNotFoundError:
        sys.exit("herdr is not installed: no way to send /compact from outside. The per-worktree "
                 "autoCompactWindow still holds; the human can type /compact in a quiet stream's pane.")
    if out.returncode != 0:
        sys.exit(f"herdr agent list failed ({out.stderr.strip() or out.stdout.strip()}): is herdr running? "
                 "Without it nothing can be compacted from outside; the per-worktree autoCompactWindow still holds.")
    return json.loads(out.stdout)["result"]["agents"]


def transcript_state(cwd):
    """(context tokens of the last call, minutes since the transcript last moved, file) for the newest session."""
    proj = os.path.expanduser("~/.claude/projects/" + cwd.replace("/", "-"))
    try:
        files = [os.path.join(proj, f) for f in os.listdir(proj) if f.endswith(".jsonl")]
    except FileNotFoundError:
        return None
    if not files:
        return None
    newest = max(files, key=os.path.getmtime)
    tokens = None
    with open(newest, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"usage"' not in line:
                continue
            try:
                msg = json.loads(line).get("message")
            except json.JSONDecodeError:
                continue
            usage = msg.get("usage") if isinstance(msg, dict) else None
            if usage:
                tokens = (usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
                          + usage.get("cache_creation_input_tokens", 0))
    quiet = (dt.datetime.now().timestamp() - os.path.getmtime(newest)) / 60
    return tokens, quiet, newest


def held_names(directory):
    """Lower-cased names in an unexpired HOLD: what is held, and who holds it."""
    now = dt.datetime.now(dt.timezone.utc)
    names = set()
    for hold in coord.open_holds(coord.read_lines(directory)):
        if hold["end"] > now:
            names.add(hold["what"].lower())
            names.add(hold["who"].lower())
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="send /compact (default: dry run)")
    ap.add_argument("--only", help="one stream by name")
    ap.add_argument("--min-tokens", type=int, default=MIN_TOKENS)
    ap.add_argument("--quiet-minutes", type=int, default=QUIET_MINUTES)
    a = ap.parse_args()

    directory = coord.coord_dir()
    if not directory:
        sys.exit("not inside a git repository: run this from a checkout of the repository the streams share")
    table = streams_from_table(directory)
    seat_checkout = main_checkout()
    held = held_names(directory)
    sent = seen = 0
    for ag in herdr_agents():
        if ag.get("agent") != "claude":
            continue
        cwd = os.path.realpath(ag.get("cwd", ""))
        name = table.get(cwd)
        if not name or cwd == seat_checkout:
            continue
        if a.only and name != a.only:
            continue
        seen += 1
        state = transcript_state(cwd)
        if not state or state[0] is None:
            print(f"{name:10} skip: no transcript usage found")
            continue
        tokens, quiet, _ = state
        reasons = []
        if ag.get("agent_status") not in ("idle", "done"):
            reasons.append(f"herdr says {ag.get('agent_status')}")
        if tokens < a.min_tokens:
            reasons.append(f"context {tokens // 1000}k < {a.min_tokens // 1000}k")
        if quiet < a.quiet_minutes:
            reasons.append(f"active {quiet:.0f} min ago")
        mine = {name.lower(), os.path.basename(cwd).lower(), str(ag.get("pane_id", "")).lower()}
        if mine & held:
            reasons.append("an unexpired HOLD names it")
        if reasons:
            print(f"{name:10} skip: {'; '.join(reasons)}")
            continue
        verb = "compact" if a.apply else "would compact"
        print(f"{name:10} {verb}: context {tokens // 1000}k, quiet {quiet:.0f} min, pane {ag['pane_id']}")
        if a.apply:
            r = sh(["herdr", "agent", "prompt", ag["pane_id"], COMPACT_INSTRUCTIONS])
            if r.returncode != 0:
                print(f"{name:10} send failed: {r.stderr.strip() or r.stdout.strip()}")
                continue
            sent += 1
            try:
                coord.write(directory, f"compacted {name} (idle, context {tokens // 1000}k, quiet "
                                       f"{quiet:.0f} min) via herdr /compact", "seat")
            except coord.CoordError as err:
                print(f"{name:10} sent, but the coord line was refused: {err}")
    if not seen:
        print("no stream session found in herdr (a claude agent whose cwd is a worktree in coord/streams.md)")
    if a.apply:
        print(f"sent {sent}")


if __name__ == "__main__":
    main()
