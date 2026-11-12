#!/usr/bin/env python3
"""Live coordination state for the streams skill: shared by every worktree of one repository on one
machine, committed nowhere.

It lives in git's common directory (`git rev-parse --path-format=absolute --git-common-dir`), under
`coord/`. Every worktree of the repository shares that directory, so a file there is one file for all of
them, and git never tracks what is inside `.git`. It is per machine: anything that must cross machines
goes to the project's issue tracker. `COORD_DIR` overrides the directory (the tests use it).

- `coord/streams.md`   the running streams' rows; the seat edits it in place.
- `coord/log.md`       append-only, one dated line per event another session must be able to read later:
                       a hold taken or released, a deploy, a hand-off, what the seat owes.
- `coord/schedules.md` what runs on a clock, with owner and how to restart it (the `restart` door).
- `coord/asks.md`      what waits on the human (the `queue` door).
- `coord/roadmaps/`    a roadmap's live state (the `roadmap` skill).

Lines with a meaning in the log:

- `HOLD <what>: <why>` with `--for 40m` or `--until 07:30` (the human's local time). The end is stored
  last on the line as `until YYYY-MM-DD HH:MM UTC`. A HOLD with no end is refused. One holder at a time:
  a HOLD on something another holder has until an end that has not come is refused. The same holder
  moves the end with a new HOLD. Nothing releases on its own; a hold past its end may be taken by anyone.
- `RELEASE <what>: <why>` closes the hold; anyone may release a gone holder's hold.
- `OWED <stream>: <what>` gets an id (`OWED a7 <stream>: <what>`); `PAID a7` closes it.

Usage:
    coord.py init
    coord.py log "<text>" [--as <who>] [--for 40m | --until HH:MM]
    coord.py show [--holds] [--owed] [--log N]

Python 3 standard library only.
"""
import argparse
import datetime as dt
import os
import re
import subprocess
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = dt.timezone.utc

STREAMS = "streams.md"
LOG = "log.md"
ASKS = "asks.md"
SCHEDULES = "schedules.md"
ROADMAPS = "roadmaps"


class CoordError(Exception):
    """A line coord refuses to write; the message says what to do instead."""


# ------------------------------------------------------------------ where coord lives


def coord_dir(cwd=None):
    """`$COORD_DIR`, else `<git common dir>/coord` for the checkout at `cwd`; None outside a repository."""
    override = os.environ.get("COORD_DIR")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    try:
        out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                             capture_output=True, text=True, cwd=cwd)
    except FileNotFoundError:
        return None
    common = out.stdout.strip()
    if out.returncode != 0 or not common:
        return None
    return os.path.join(common, "coord")


def default_who(cwd=None):
    """`$COORD_AS`, else the current worktree's directory name, else the current directory's."""
    who = os.environ.get("COORD_AS")
    if who:
        return who
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=cwd)
        top = out.stdout.strip() if out.returncode == 0 else ""
    except FileNotFoundError:
        top = ""
    return os.path.basename(top or os.path.abspath(cwd or os.getcwd()))


def _self_command():
    path = os.path.abspath(__file__)
    home = os.path.expanduser("~")
    if path.startswith(home + os.sep):
        path = "~" + path[len(home):]
    return f"python3 {path}"


# ------------------------------------------------------------------ the human's local time


def local_zone():
    """The human's time zone: `$TZ` when it names a zone, else the system's (DST-aware), else UTC."""
    name = os.environ.get("TZ", "").lstrip(":")
    if name:
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            pass
    try:
        link = os.path.realpath("/etc/localtime")
        if "zoneinfo/" in link:
            return ZoneInfo(link.split("zoneinfo/", 1)[1])
    except (ZoneInfoNotFoundError, ValueError, OSError):
        pass
    try:
        with open("/etc/localtime", "rb") as fh:
            return ZoneInfo.from_file(fh)
    except (OSError, ValueError):
        pass
    return UTC


def resolve_local_clock(clock, now, zone):
    """The next moment after `now` (aware, UTC) that the clock in `zone` reads `HH:MM`.

    A time the spring change skips is refused; a time the autumn change repeats gives the first of the
    two moments that is still ahead.
    """
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", clock.strip())
    if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
        raise CoordError(f"--until {clock} is not a time. Write it as 07:30, the human's local time.")
    hour, minute = int(m.group(1)), int(m.group(2))
    today = now.astimezone(zone).date()
    for shift in (0, 1, 2):
        day = today + dt.timedelta(days=shift)
        wall = dt.datetime(day.year, day.month, day.day, hour, minute)
        moments = []
        for fold in (0, 1):
            aware = wall.replace(tzinfo=zone, fold=fold)
            utc = aware.astimezone(UTC)
            if utc.astimezone(zone).replace(tzinfo=None) == wall:  # the wall time exists
                moments.append(utc)
        if not moments:
            # A skipped minute. Ahead of us it is refused; behind us, the next day may have it.
            if wall.replace(tzinfo=zone, fold=0).astimezone(UTC) > now:
                raise CoordError(f"--until {clock} does not exist on {day.isoformat()}: the clocks skip that "
                                 "time. Pick a time before or after it.")
            continue
        ahead = sorted(t for t in set(moments) if t > now)
        if ahead:
            return ahead[0]
    raise CoordError(f"--until {clock}: found no such moment in the next two days.")


def local_clock(moment, now, zone):
    """`10:15 CET`, with the date in front when it is not `now`'s day on the local clock."""
    here = moment.astimezone(zone)
    text = here.strftime("%H:%M ") + (here.tzname() or "")
    if here.date() != now.astimezone(zone).date():
        text = here.strftime("%Y-%m-%d ") + text
    return text.strip()


def parse_duration(text):
    """`40m`, `2h`, `1h30m` or `90` (minutes) as a timedelta; None when it is none of these."""
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m?)?", text.strip())
    if not m or (m.group(1) is None and m.group(2) is None):
        return None
    minutes = int(m.group(1) or 0) * 60 + int(m.group(2) or 0)
    return dt.timedelta(minutes=minutes) if minutes > 0 else None


def human_span(delta):
    minutes = max(0, int(delta.total_seconds() // 60))
    hours, minutes = divmod(minutes, 60)
    if hours >= 24:
        days, hours = divmod(hours, 24)
        return f"{days}d{hours}h"
    return f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"


# ------------------------------------------------------------------ log lines

LINE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC (\S+?): (.*)$")
HOLD_END = re.compile(r"\buntil (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\s*$")
KEYWORD = re.compile(r"^(HOLD|RELEASED?)(?=[\s:]|$)", re.IGNORECASE)
OWED_LINE = re.compile(r"^OWED (a\d+) ([^\s:]+):? (.*)$")
PAID_LINE = re.compile(r"^PAID\s+([^\s:,.;]+)")


def stamp(moment):
    return moment.astimezone(UTC).strftime("%Y-%m-%d %H:%M")


def parse_stamp(text):
    return dt.datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)


def parse_line(line):
    """(time, who, text) for a log line; None for anything else (the header, blank lines)."""
    m = LINE.match(line.rstrip("\n"))
    if not m:
        return None
    return parse_stamp(m.group(1)), m.group(2), m.group(3)


def read_lines(directory):
    """Every event line of the log, oldest first; empty when there is no log."""
    path = os.path.join(directory, LOG)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [line.rstrip("\n") for line in fh if LINE.match(line)]


def clean_what(token):
    """A word without the punctuation a sentence puts around it: `author.` and `stage,` name `author`, `stage`."""
    token = re.sub(r"^[(\"'`\[]+", "", token)
    return re.sub(r"[\s.,;:!?)\"'`\]’”]+$", "", token)


def hold_words(text):
    """('hold', what) | ('release', what or None) | ('nowhat', None) for a HOLD/RELEASE line; None otherwise.

    `HOLD <what> released …` and `RELEASED <what>` are older wordings of a release and close a hold too.
    """
    kw = KEYWORD.match(text)
    if not kw:
        return None
    rest = text[kw.end():].lstrip()
    token = rest.split(None, 1)[0] if rest.strip() else ""
    what = clean_what(token)
    named = bool(re.search(r"\w", what))
    if kw.group(1).upper() != "HOLD":
        return ("release", what if named else None)
    if not named:
        return ("nowhat", None)
    if what.lower() == "released":
        return ("release", None)
    after = rest[len(token):].lstrip()
    if what == token and re.match(r"released\b", after, re.IGNORECASE):
        return ("release", what)
    return ("hold", what)


def open_holds(lines):
    """The holds the log leaves open, oldest first: dicts with what, who, since, end, text.

    A later HOLD for the same `<what>` (any case) replaces the earlier one; from the same holder it keeps
    the first `since`. RELEASE closes it. A hold past its end stays open: nothing releases on its own.
    A HOLD with no stored end is never listed.
    """
    held = {}
    for line in lines:
        parsed = parse_line(line)
        if not parsed:
            continue
        when, who, text = parsed
        words = hold_words(text)
        if not words or words[0] == "nowhat":
            continue
        kind, what = words
        if kind == "release":
            if what:
                held.pop(what.lower(), None)
            continue
        key = what.lower()
        before = held.pop(key, None)
        end = HOLD_END.search(text)
        if not end:
            continue
        since = before["since"] if before and before["who"] == who else when
        held[key] = {"what": what, "who": who, "since": since, "end": parse_stamp(end.group(1)), "text": text}
    return list(held.values())


def _owed_entries(lines):
    owed, paid = {}, set()
    for line in lines:
        parsed = parse_line(line)
        if not parsed:
            continue
        when, who, text = parsed
        m = OWED_LINE.match(text)
        if m:
            owed[m.group(1)] = {"id": m.group(1), "stream": m.group(2), "what": m.group(3), "since": when, "who": who}
            continue
        m = PAID_LINE.match(text)
        if m:
            paid.add(m.group(1))
    return owed, paid


def open_owed(lines):
    """The OWED lines no PAID line has closed, oldest first."""
    owed, paid = _owed_entries(lines)
    return [entry for oid, entry in owed.items() if oid not in paid]


# ------------------------------------------------------------------ writing


def prepare(text, who, lines, now, for_=None, until=None, zone=None):
    """The text to write for `log`, or CoordError saying why not."""
    zone = zone or local_zone()
    text = re.sub(r"\s*\n\s*", " ", text).strip()
    if not text:
        raise CoordError('Nothing to write. Usage: coord.py log "<text>" [--as <who>] [--for 40m | --until HH:MM]')
    wants_end = for_ is not None or until is not None
    words = hold_words(text)

    if words and words[0] == "release":
        if wants_end:
            raise CoordError("--for and --until go with a HOLD line only.")
        if KEYWORD.match(text).group(1).upper() == "HOLD":
            which = words[1] or "<what>"
            raise CoordError(f'That line ends a hold. Write it as: {_self_command()} log "RELEASE {which}: <why>"')
        if not words[1]:
            raise CoordError('A release names what it lets go: "RELEASE <what>: <why>".')
        return re.sub(r"^release(d?)", lambda m: "RELEASE" + m.group(1).upper(), text, count=1, flags=re.IGNORECASE)

    if not words:
        if wants_end:
            raise CoordError("--for and --until go with a HOLD line only.")
        return _prepare_owed_paid(text, lines)

    if words[0] == "nowhat":
        raise CoordError('A hold names what it holds: "HOLD <what>: <why>" (the stream or host, then why).')
    what = words[1]
    if for_ is not None and until is not None:
        raise CoordError("Give the end once: --for or --until, not both.")
    if not wants_end:
        raise CoordError("A hold needs an end. Add --for 40m (a length) or --until 07:30 (the human's local time).")
    if for_ is not None:
        length = parse_duration(for_)
        if length is None:
            raise CoordError(f"--for {for_} is not a length. Write 40m, 2h or 1h30m.")
        end = now + length
    else:
        end = resolve_local_clock(until, now, zone)
    current = next((h for h in open_holds(lines) if h["what"].lower() == what.lower()), None)
    if current and current["who"] != who and current["end"] > now:
        raise CoordError(
            f"{current['what']} is held by {current['who']} until {local_clock(current['end'], now, zone)}; "
            f"ask them, or wait. If they are gone, release it: "
            f"{_self_command()} log \"RELEASE {current['what']}: <why>\"")
    written = re.sub(r"^hold", "HOLD", text, count=1, flags=re.IGNORECASE)
    return f"{written} until {stamp(end)} UTC"


def _prepare_owed_paid(text, lines):
    if re.match(r"^OWED(\s|:|$)", text):
        m = re.match(r"^OWED\s+([^\s:]+?):?\s+(\S.*)$", text)
        if not m:
            raise CoordError('An OWED line names the stream and what is owed: "OWED <stream>: <what>".')
        if re.fullmatch(r"a\d+", m.group(1)):
            raise CoordError('The log gives an OWED line its id. Write "OWED <stream>: <what>".')
        owed, _ = _owed_entries(lines)
        n = max((int(oid[1:]) for oid in owed), default=0) + 1
        return f"OWED a{n} {m.group(1)}: {m.group(2)}"
    if re.match(r"^PAID(\s|:|$)", text):
        m = PAID_LINE.match(text)
        if not m:
            raise CoordError('PAID names the id of an OWED line: "PAID a7".')
        owed, paid = _owed_entries(lines)
        oid = m.group(1)
        if oid not in owed:
            raise CoordError(f"No OWED line has the id {oid}. {_self_command()} show --owed lists the unpaid ones.")
        if oid in paid:
            raise CoordError(f"OWED {oid} is already paid.")
    return text


LOG_HEADER = """# Coordination log

Append-only. One line per event another session must be able to read later: a hold taken or
released, a deploy (which build, by whom), a hand-off, what the seat owes. Newest at the bottom.
Written with the streams skill's `scripts/coord.py log "<text>"`. Lives in git's common directory:
every worktree on this machine reads the same file; nothing here is committed.

"""


def write(directory, text, who, now=None, for_=None, until=None, zone=None):
    """Check `text` against the log so far and append it. Returns the line written."""
    now = now or dt.datetime.now(UTC)
    if not who or re.search(r"[\s:]", who):
        raise CoordError(f"--as {who!r}: a name is one word, without spaces or colons.")
    lines = read_lines(directory)
    body = prepare(text, who, lines, now, for_=for_, until=until, zone=zone)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, LOG)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(LOG_HEADER)
    line = f"{stamp(now)} UTC {who}: {body}"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return line


# ------------------------------------------------------------------ init

STREAMS_HEADER = """# Streams — the live table

The running streams **on this machine**. It lives in git's common directory, so every worktree
reads the same file and nothing here is committed: the seat edits it in place, and it is current
for everyone at once. The rules for streams, and landed streams' history, stay in git, in
`.devmeta/streams.md`.

| stream | increment | session | branch | worktree | ports | host | epics | status |
|---|---|---|---|---|---|---|---|---|
"""

ASKS_HEADER = """# What waits on the human

The seat writes and reads this file. One row per thing only the human can do or decide: an id
(`q1`, `q2`, … never reused), what it is in plain words, the exact thing to type (a `!` command, or
`say` for a decision in their own words), who waits on it, since when (UTC). Every row has a why
under **Why**: what it is, what each answer does, what happens if nothing is decided.

## Now

| id | what | type | waiting | since |
|---|---|---|---|---|

## Optional, no deadline

| id | what | type | waiting | since |
|---|---|---|---|---|

## Later

| id | what | type | waiting | when |
|---|---|---|---|---|

## Done

| id | what | answer | closed |
|---|---|---|---|

## Why
"""

_SCHEDULE_TABLE = """| what | owner | kind | when (UTC) | script / prompt | ends | restart |
|---|---|---|---|---|---|---|
"""

SCHEDULES_HEADER = f"""# Schedules — what runs on a clock, on this machine

What fires by itself, who owns it, and how to bring it back after herdr, a Claude session, WSL or
the machine stopped (the streams skill's `restart` door). The seat keeps it; a stream that starts,
changes or ends anything on a clock edits its own row in the same breath and logs it. `same` in
the restart column means the row above's. An ended row is struck through (`~~what~~ ended <when>`).

## Survives a session stop (system)

{_SCHEDULE_TABLE}
## Dies with its session (restart by hand)

{_SCHEDULE_TABLE}
## One-off waits

{_SCHEDULE_TABLE}"""


def init(directory):
    """Create coord/ and the files that are not there yet. Returns the paths created."""
    created = []
    os.makedirs(directory, exist_ok=True)
    for name, body in ((STREAMS, STREAMS_HEADER), (LOG, LOG_HEADER), (ASKS, ASKS_HEADER),
                       (SCHEDULES, SCHEDULES_HEADER)):
        path = os.path.join(directory, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(body)
            created.append(path)
    roadmaps = os.path.join(directory, ROADMAPS)
    if not os.path.isdir(roadmaps):
        os.makedirs(roadmaps)
        created.append(roadmaps + os.sep)
    return created


# ------------------------------------------------------------------ show


def show(directory, holds=False, owed=False, log=None, now=None, zone=None):
    """The report `show` prints, as a string."""
    now = now or dt.datetime.now(UTC)
    zone = zone or local_zone()
    everything = not holds and not owed and log is None
    lines = read_lines(directory)
    out = [f"coord: {directory}"]
    if everything or holds:
        current = open_holds(lines)
        live = [h for h in current if h["end"] > now]
        ended = [h for h in current if h["end"] <= now]
        out.append("HOLDS")
        for h in live:
            out.append(f"  {h['what']}  by {h['who']} since {local_clock(h['since'], now, zone)}, "
                       f"until {local_clock(h['end'], now, zone)} ({human_span(h['end'] - now)} left): {h['text']}")
        if not live:
            out.append("  (none)")
        out.append("EXPIRED HOLDS (still held: RELEASE it, or HOLD it again with a new end)")
        for h in ended:
            out.append(f"  {h['what']}  by {h['who']}, ended {local_clock(h['end'], now, zone)} "
                       f"({human_span(now - h['end'])} ago): {h['text']}")
        if not ended:
            out.append("  (none)")
    if everything or owed:
        out.append("OWED")
        unpaid = open_owed(lines)
        for o in unpaid:
            out.append(f"  {o['id']}  {o['stream']}, waiting {human_span(now - o['since'])}: {o['what']}")
        if not unpaid:
            out.append("  (none)")
    if everything or log is not None:
        count = 10 if log is None else log
        tail = lines[-count:] if count > 0 else []
        out.append(f"LOG (newest {len(tail)})")
        out.extend(f"  {line}" for line in tail)
        if not tail:
            out.append("  (empty)")
    return "\n".join(out)


# ------------------------------------------------------------------ the command


def main(argv=None):
    ap = argparse.ArgumentParser(prog="coord.py", description="The streams skill's coordination state.")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="create coord/ and its files")
    p_log = sub.add_parser("log", help="append one line to coord/log.md")
    p_log.add_argument("text", nargs="+")
    p_log.add_argument("--as", dest="who")
    p_log.add_argument("--for", dest="for_")
    p_log.add_argument("--until")
    p_show = sub.add_parser("show", help="open holds, expired holds, unpaid OWED, newest log lines")
    p_show.add_argument("--holds", action="store_true")
    p_show.add_argument("--owed", action="store_true")
    p_show.add_argument("--log", type=int, metavar="N")
    a = ap.parse_args(argv)

    directory = coord_dir()
    if not directory:
        print("coord: not inside a git repository, and COORD_DIR is not set: there is no common directory "
              "to share.", file=sys.stderr)
        return 1

    if a.command == "init":
        created = init(directory)
        print(f"coord: {directory}")
        for path in created:
            print(f"  created {path}")
        if not created:
            print("  everything was already there; nothing written")
        return 0

    if a.command == "log":
        try:
            line = write(directory, " ".join(a.text), a.who or default_who(), for_=a.for_, until=a.until)
        except CoordError as err:
            print(f"coord log: {err}", file=sys.stderr)
            return 2
        print(line)
        m = re.search(r": OWED (a\d+) ", line)
        if m:
            print(f'  owed {m.group(1)}: close it with {_self_command()} log "PAID {m.group(1)}"')
        return 0

    print(show(directory, holds=a.holds, owed=a.owed, log=a.log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
