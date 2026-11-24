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
- `coord/seat.json`    the seat's terminal (session id, when it was set in UTC): where `log` sends what
                       the seat must hear. Written by `seat --here`, in the seat's pane.

The default is one seat per repository. One seat may also serve several (not rehearsed:
`references/several-repos.md`). Each repository keeps its own `coord/`
and its own `seat.json`; registering a seat also records the repository in a file of the user's,
`$STREAMS_SEATS` or `$XDG_STATE_HOME/streams/seats.json` (default `~/.local/state/streams/seats.json`),
so `repos` can list every repository a seat serves. `-C <dir>` runs any command as if started in `<dir>`,
like `git -C`: that is how one seat works in a repository it does not sit in.

Lines with a meaning in the log:

- `HOLD <what>: <why>` with `--for 40m` or `--until 07:30` (the human's local time). The end is stored
  last on the line as `until YYYY-MM-DD HH:MM UTC`. A HOLD with no end is refused. One holder at a time:
  a HOLD on something another holder has until an end that has not come is refused. The same holder
  moves the end with a new HOLD. Nothing releases on its own; a hold past its end may be taken by anyone.
- `RELEASE <what>: <why>` closes the hold; anyone may release a gone holder's hold.
- `OWED <stream>: <what>` gets an id (`OWED a7 <stream>: <what>`); `PAID a7` closes it, and so does
  `PAID a7: <note>`.

A line in the log wakes nobody, so `log` also tells a terminal, through `term.py send`, once the line is
written:

- an `OWED` line goes to the registered seat, as `<who>: <the text>`;
- a `PAID <id>` line goes to the stream that wrote the OWED line (to the stream the OWED line names when
  the payer wrote it itself), as `PAID <id>: <what was owed>`, then ` -- <note>` when the line has one.
  The stream's worktree is the one named like the writer (`git worktree list`), its session the one whose
  cwd is in that worktree (`term.py ls`);
- any other line goes nowhere unless `--tell seat` or `--tell <stream slug or session id>` says so;
- `--no-tell` tells nobody, and the terminal the command runs in (`$HC_TERMINAL_ID`) is never told.

A relay that fails never fails the log: the line is written, stderr says in one line why it was not
delivered, and the exit code is 0. A delivered relay prints `told <session>`.

Usage:
    coord.py init
    coord.py log "<text>" [--as <who>] [--for 40m | --until HH:MM] [--tell seat|<stream>|<session> | --no-tell]
    coord.py show [--holds] [--owed] [--log N]
    coord.py seat [--here | --set <session> | --clear]
    coord.py config [--slug <slug>] [--json | --get <fact>] [--file <path>]
    coord.py init-file [--trunk B] [--worktree-root DIR] [--at-cut L]... [--at-landing L]...
                       [--resources L]... [--force]

The project file `.devmeta/streams.md` (committed, at the repository's top) holds the project's facts in
optional sections: `## Project` (`trunk:`, `worktree root:`), `## Resources`, `## At cut`, `## At landing`,
and the prose sections the doors paste or follow (`## Heavy runs`, `## Standing rules`, `## Seams`,
`## At hotfix`, `## Scout`). `config` prints each fact with where it came from: the file, or what was detected when
the file says nothing; `config --get <fact>` prints one fact's bare value, for a command line.

Python 3 standard library only.
"""
import argparse
import datetime as dt
import json
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
SEAT = "seat.json"
TERM_TIMEOUT = 60  # seconds for one term.py call; `hc send` waits while a person has a draft in the terminal


class CoordError(Exception):
    """A line coord refuses to write; the message says what to do instead."""


class NotTold(Exception):
    """A relay that reached no terminal; the message says why. It never fails the log."""


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


_CHDIR = None   # the -C directory of this run, so a printed command runs in the same repository


def _tilde(path):
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home + os.sep) else path


def _self_command():
    cmd = f"python3 {_tilde(os.path.abspath(__file__))}"
    if _CHDIR:
        cmd += f" -C {_tilde(_CHDIR)}"
    return cmd


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
        with open("/etc/localtime", "rb") as f:
            return ZoneInfo.from_file(f)
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
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if LINE.match(line)]


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
            raise CoordError('PAID names the id of an OWED line: "PAID a7", or "PAID a7: <note>".')
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
        with open(path, "w", encoding="utf-8") as f:
            f.write(LOG_HEADER)
    line = f"{stamp(now)} UTC {who}: {body}"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line


# ------------------------------------------------------------------ init

STREAMS_HEADER = """# Streams — the live table

The running streams **on this machine**. It lives in git's common directory, so every worktree
reads the same file and nothing here is committed: the seat edits it in place, and it is current
for everyone at once. The rules for streams stay in git, in `.devmeta/streams.md`; what landed is in
git history and `coord/log.md`.

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

What fires by itself, who owns it, and how to bring it back after the terminal server (hc or herdr),
a Claude session, WSL or the machine stopped (the streams skill's `restart` door). The seat keeps
it; a stream that starts, changes or ends anything on a clock edits its own row in the same breath
and logs it. `same` in the restart column means the row above's. An ended row is struck through (`~~what~~ ended <when>`).

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
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
            created.append(path)
    roadmaps = os.path.join(directory, ROADMAPS)
    if not os.path.isdir(roadmaps):
        os.makedirs(roadmaps)
        created.append(roadmaps + os.sep)
    return created


# ------------------------------------------------------------------ the project file

PROJECT_FILE = os.path.join(".devmeta", "streams.md")
# The sections the doors read. Any other `## ` heading is reported as a warning, never refused.
KNOWN_SECTIONS = ("Project", "Resources", "At cut", "At landing", "Standing rules", "Heavy runs", "Seams",
                  "At hotfix", "Scout")
SECTION = re.compile(r"^##\s+(.+?)\s*$")
# The sections the doors follow as written; `config` passes them through untouched. `Standing rules`
# is pasted into every brief; `Scout` is read only by the hourly scout (references/scout.md), never a brief.
PROSE_SECTIONS = ("Heavy runs", "Standing rules", "Seams", "At hotfix", "Scout")
# `config --get <fact>`: one fact's bare value, for a command line such as `git show "$(... --get trunk)":<path>`.
GET_FACTS = ("trunk", "worktree-root", "worktree", "repo", "file", "at-cut", "at-landing", "resources",
             "heavy-runs", "standing-rules", "seams", "at-hotfix", "scout")


def _git(args, cwd=None):
    """git's stdout, stripped, or None when git is missing or the command fails."""
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)
    except FileNotFoundError:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def repo_top(cwd=None):
    """The current checkout's top directory; None outside a repository."""
    top = _git(["rev-parse", "--show-toplevel"], cwd)
    return top or None


def main_checkout(cwd=None):
    """The repository's main checkout (the one whose `.git` is the common directory); else the current top."""
    common = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
    if common and os.path.basename(common.rstrip(os.sep)) == ".git":
        return os.path.dirname(common.rstrip(os.sep))
    return repo_top(cwd)


FENCE = re.compile(r"^\s*(```|~~~)")


def _unfence(body):
    """A body that is one fenced block, fence lines and all, as the lines inside it."""
    lines = body.splitlines()
    if len(lines) >= 2 and FENCE.match(lines[0]) and FENCE.match(lines[-1]) \
            and not any(FENCE.match(x) for x in lines[1:-1]):
        return "\n".join(lines[1:-1]).strip()
    return body


def parse_sections(text):
    """(sections, order): each `## ` heading's body, stripped, in file order. Text before the first is dropped.

    A `## ` line inside a fenced block is body, not a heading; a body that is one fenced block is
    returned as the lines inside the fence."""
    sections, order, name, body, fenced = {}, [], None, [], False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
        m = None if fenced else SECTION.match(line)
        if m:
            if name is not None:
                sections[name] = _unfence("\n".join(body).strip())
            name, body = m.group(1), []
            if name not in order:
                order.append(name)
            continue
        if name is not None:
            body.append(line)
    if name is not None:
        sections[name] = _unfence("\n".join(body).strip())
    return sections, order


def parse_project(body):
    """`key: value` lines of `## Project`, keys lower case; a ` # comment` after the value is dropped."""
    facts = {}
    for line in body.splitlines():
        line = re.sub(r"\s+#.*$", "", line).strip()
        m = re.match(r"^[-*]?\s*([A-Za-z][\w -]*?)\s*:\s*(.*)$", line)
        if m and m.group(2):
            facts[m.group(1).lower()] = m.group(2).strip()
    return facts


def detect_trunk(cwd=None):
    """(branch, how): origin's HEAD, else `main` or `master` when one exists, else the current branch."""
    ref = _git(["symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"], cwd)
    if ref and ref.startswith("refs/remotes/origin/"):
        return ref[len("refs/remotes/origin/"):], "detected: refs/remotes/origin/HEAD"
    for name in ("main", "master"):
        if _git(["rev-parse", "--verify", "--quiet", f"refs/heads/{name}"], cwd) is not None:
            return name, f"detected: local branch {name} exists"
    current = _git(["symbolic-ref", "--quiet", "--short", "HEAD"], cwd)
    if current:
        return current, "detected: the current branch"
    return None, "detected: nothing (no origin HEAD, no main or master, detached HEAD)"


def config(cwd=None, path=None, slug=None):
    """The project's facts, each {value, source}, plus `resources`, `warnings` and `file`.

    The project file, a relative `worktree root:` and `.tick/config.md` resolve against the main
    checkout, so the answer is the same from any worktree of the repository."""
    if not repo_top(cwd):
        raise CoordError("not inside a git repository: there is no project to read.")
    top = main_checkout(cwd)
    rel = path or PROJECT_FILE
    file_path = rel if os.path.isabs(rel) else os.path.join(top, rel)
    sections, order, warnings = {}, [], []
    shown = os.path.relpath(file_path, top) if file_path.startswith(top + os.sep) else file_path
    if os.path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            sections, order = parse_sections(f.read())
        for name in order:
            if name not in KNOWN_SECTIONS:
                warnings.append(f"unknown section '## {name}' in {shown}; the doors do not read it")
    project = parse_project(sections.get("Project", ""))
    from_file = f"file: {shown} → ## Project"

    if project.get("trunk"):
        trunk = {"value": project["trunk"], "source": f"{from_file}, trunk:"}
    else:
        value, how = detect_trunk(cwd)
        trunk = {"value": value, "source": how}

    home = top
    repo = os.path.basename(home)
    if project.get("worktree root"):
        root = os.path.expanduser(project["worktree root"])
        if not os.path.isabs(root):
            root = os.path.join(top, root)
        worktree_root = {"value": os.path.normpath(root), "source": f"{from_file}, worktree root:"}
    else:
        worktree_root = {"value": os.path.dirname(home), "source": "detected: the main checkout's parent directory"}

    if sections.get("At cut"):
        at_cut = {"value": sections["At cut"], "source": f"file: {shown} → ## At cut"}
    else:
        at_cut = {"value": "", "source": "default: nothing to run"}

    if sections.get("At landing"):
        at_landing = {"value": sections["At landing"], "source": f"file: {shown} → ## At landing"}
    else:
        tick = os.path.join(top, ".tick", "config.md")
        testing = ""
        if os.path.exists(tick):
            with open(tick, encoding="utf-8") as f:
                testing = parse_sections(f.read())[0].get("Testing", "")
        if testing:
            # Prose, not commands: `--get at-landing` prints nothing; the human-readable output points there.
            at_landing = {"value": "", "hint": "see .tick/config.md → ## Testing",
                          "source": "default: nothing here; .tick/config.md has a ## Testing section"}
        else:
            at_landing = {"value": "", "source": "default: nothing (no .tick/config.md → ## Testing)"}

    result = {
        "file": file_path if os.path.exists(file_path) else None,
        "repo": repo,
        "trunk": trunk,
        "worktree_root": worktree_root,
        "at_cut": at_cut,
        "at_landing": at_landing,
        "resources": sections.get("Resources", ""),
        "sections": {name: sections.get(name, "") for name in PROSE_SECTIONS},
        "warnings": warnings,
    }
    if slug is not None:
        result["worktree"] = os.path.join(worktree_root["value"], f"{repo}-{slug}")
    return result


def show_config(facts):
    """The text `config` prints."""
    out = [f"project file: {facts['file'] or '(none; every fact below is detected or a default)'}"]
    for key in ("trunk", "worktree_root", "at_cut", "at_landing"):
        fact = facts[key]
        value = fact["value"] if fact["value"] not in (None, "") else fact.get("hint") or "(nothing)"
        if "\n" in value:
            out.append(f"{key}:  ({fact['source']})")
            out.extend(f"    {line}" for line in value.splitlines())
        else:
            out.append(f"{key}: {value}  ({fact['source']})")
    out.append(f"worktree: {facts['worktree_root']['value']}/{facts['repo']}-<slug>"
               if "worktree" not in facts else f"worktree: {facts['worktree']}")
    if facts["resources"]:
        out.append("resources:")
        out.extend(f"    {line}" for line in facts["resources"].splitlines())
    else:
        out.append("resources: (none; a stream claims nothing)")
    present = [name for name in PROSE_SECTIONS if facts["sections"].get(name)]
    out.append(f"sections: {', '.join('## ' + n for n in present)}" if present
               else "sections: (no ## Heavy runs, ## Standing rules, ## Seams, ## At hotfix or ## Scout)")
    for w in facts["warnings"]:
        out.append(f"warning: {w}")
    return "\n".join(out)


def get_fact(facts, name):
    """One fact's bare value ('' when the project names none). Raises CoordError for an unknown name."""
    if name not in GET_FACTS:
        raise CoordError(f"no fact '{name}'; the facts are: {', '.join(GET_FACTS)}.")
    if name == "worktree":
        if "worktree" not in facts:
            raise CoordError("--get worktree needs --slug <slug>.")
        return facts["worktree"]
    key = name.replace("-", "_")
    if key == "trunk" and not facts[key]["value"]:
        raise CoordError(f"no trunk: {facts[key]['source']}. Name it in ## Project (`trunk: main`).")
    if key in ("trunk", "worktree_root", "at_cut", "at_landing"):
        return facts[key]["value"] or ""
    if key in ("repo", "file", "resources"):
        return facts[key] or ""
    return facts["sections"][name.replace("-", " ").capitalize()]


def _block(values):
    """Repeated flag values as one block of lines; literal `\\n` in a value also breaks a line."""
    if not values:
        return ""
    return "\n".join(v.replace("\\n", "\n").strip() for v in values if v and v.strip()).strip()


def _tilde(path):
    """A path under the home directory as `~/...`, so the committed file is the same for everyone."""
    home = os.path.expanduser("~")
    if home and home != "~" and (path == home or path.startswith(home.rstrip(os.sep) + os.sep)):
        return "~" + path[len(home.rstrip(os.sep)):]
    return path


def project_file_text(trunk=None, worktree_root=None, at_cut=None, at_landing=None, resources=None):
    """The project file with only the sections that have content."""
    parts = ["# Streams — this project's facts",
             "",
             "Read by the streams skill (`coord.py config`). Every section is optional; a missing one is",
             "detected or left empty."]
    project = []
    if trunk:
        project.append(f"trunk: {trunk}")
    if worktree_root:
        project.append(f"worktree root: {_tilde(worktree_root)}")
    for name, body in (("Project", "\n".join(project)), ("Resources", _block(resources)),
                       ("At cut", _block(at_cut)), ("At landing", _block(at_landing))):
        if body:
            parts += ["", f"## {name}", "", body]
    return "\n".join(parts) + "\n"


def init_file(cwd=None, path=None, force=False, **values):
    """Write the project file at the repository's top. Returns its path; refuses to overwrite without force."""
    top = repo_top(cwd)
    if not top:
        raise CoordError("not inside a git repository: there is no top directory to write the file in.")
    rel = path or PROJECT_FILE
    file_path = rel if os.path.isabs(rel) else os.path.join(top, rel)
    if os.path.exists(file_path) and not force:
        raise CoordError(f"{file_path} already exists; nothing written. Edit it by hand, or pass --force "
                         "to replace it.")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(project_file_text(**values))
    return file_path


# ------------------------------------------------------------------ the seat's terminal, and telling one


def read_seat(directory):
    """The registered seat, {session, set}; None when none is registered or the file does not read."""
    try:
        with open(os.path.join(directory, SEAT), encoding="utf-8") as f:
            seat = json.load(f)
    except (OSError, ValueError):
        return None
    if isinstance(seat, dict) and isinstance(seat.get("session"), str) and seat["session"]:
        return seat
    return None


def set_seat(directory, session, now=None):
    """Register `session` as the seat's terminal. Returns what was written."""
    session = (session or "").strip()
    if not session or re.search(r"\s", session):
        raise CoordError(f"{session!r} is not a session id; `term.py ls` lists them (hc: t7, herdr: a pane id).")
    os.makedirs(directory, exist_ok=True)
    seat = {"session": session, "set": f"{stamp(now or dt.datetime.now(UTC))} UTC"}
    with open(os.path.join(directory, SEAT), "w", encoding="utf-8") as f:
        f.write(json.dumps(seat) + "\n")
    return seat


def clear_seat(directory):
    """Remove the registration. Returns the seat that was registered, or None."""
    seat = read_seat(directory)
    path = os.path.join(directory, SEAT)
    if os.path.exists(path):
        os.remove(path)
    return seat


def seat_line(directory):
    """`seat: t17 (set 2026-01-15 10:00 UTC)`, or `seat: not registered`."""
    seat = read_seat(directory)
    if not seat:
        return "seat: not registered"
    return f"seat: {seat['session']} (set {seat.get('set') or 'at an unknown time'})"


# ------------------------------------------------------------------ the repositories one seat serves


def seats_file():
    """`$STREAMS_SEATS`, else `$XDG_STATE_HOME/streams/seats.json`, else `~/.local/state/streams/seats.json`."""
    override = os.environ.get("STREAMS_SEATS")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    state = os.environ.get("XDG_STATE_HOME") or os.path.join(os.path.expanduser("~"), ".local", "state")
    return os.path.join(state, "streams", "seats.json")


def read_seats():
    """{session: {main checkout: when it was registered}}; {} when the file is missing or does not read."""
    try:
        with open(seats_file(), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {s: r for s, r in data.items() if isinstance(r, dict)}


def _write_seats(data):
    path = seats_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def record_repo(session, repo, now=None):
    """Record that `session` is the seat of the repository whose main checkout is `repo`. A repository has one
    seat, so the repository is taken off any other session's list."""
    repo = os.path.realpath(repo)
    data = read_seats()
    for other in list(data):
        data[other].pop(repo, None)
        if not data[other]:
            del data[other]
    data.setdefault(session, {})[repo] = f"{stamp(now or dt.datetime.now(UTC))} UTC"
    _write_seats(data)


def forget_repo(session, repo):
    """Take the repository off `session`'s list (the seat's registration there was cleared)."""
    repo = os.path.realpath(repo)
    data = read_seats()
    if session in data and repo in data[session]:
        del data[session][repo]
        if not data[session]:
            del data[session]
        _write_seats(data)


def repos_of(session):
    """[(main checkout, state)] for every repository `session` serves, sorted. The state is `seat` when the
    repository's own seat.json still names the session, `moved to <s>` or `not registered` when it does not,
    and `gone` when the directory is no longer a repository."""
    out = []
    for repo in sorted(read_seats().get(session, {})):
        directory = coord_dir(cwd=repo) if os.path.isdir(repo) else None
        if not directory:
            out.append((repo, "gone"))
            continue
        seat = read_seat(directory)
        if not seat:
            out.append((repo, "not registered"))
        elif seat["session"] != session:
            out.append((repo, f"moved to {seat['session']}"))
        else:
            out.append((repo, "seat"))
    return out


def term(args, timeout=TERM_TIMEOUT):
    """Run term.py (the file beside this one) with `args`: (exit code, stdout, stderr). The tests replace it."""
    script = os.path.join(os.path.dirname(os.path.realpath(__file__)), "term.py")
    try:
        out = subprocess.run([sys.executable or "python3", script, *args], capture_output=True, text=True,
                             timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", f"term.py did not answer in {timeout}s"
    except OSError as err:
        return 127, "", f"term.py did not start: {err}"
    return out.returncode, out.stdout, out.stderr


def _last_line(*texts):
    for text in texts:
        lines = (text or "").strip().splitlines()
        if lines:
            return lines[-1]
    return "it printed nothing"


def worktrees(cwd=None):
    """The directory of every worktree of the repository at `cwd`, the main checkout first; [] outside one."""
    out = _git(["worktree", "list", "--porcelain"], cwd) or ""
    return [os.path.realpath(line[len("worktree "):]) for line in out.splitlines() if line.startswith("worktree ")]


def stream_worktree(name, trees):
    """The worktree a log writer or a stream slug names: the directory `name`, else `<repo>-<name>`, else
    the only one ending in `-<name>`. None when there is none."""
    wanted = [name, f"{os.path.basename(trees[0])}-{name}"] if trees else []
    for base in wanted:
        for tree in trees:
            if os.path.basename(tree) == base:
                return tree
    ending = [tree for tree in trees if os.path.basename(tree).endswith(f"-{name}")]
    return ending[0] if len(ending) == 1 else None


def stream_session(tree, trees, sessions):
    """The id of the session working in `tree`: its cwd (else its foreground program's) is the worktree or
    under it, and under no worktree nested deeper. A Claude session wins over a shell. None when there is none."""
    def home(path):
        path = os.path.realpath(path) if path else ""
        inside = [t for t in trees if path == t or path.startswith(t.rstrip(os.sep) + os.sep)]
        return max(inside, key=len) if inside else None

    for key in ("cwd", "foreground_cwd"):
        found = [s for s in sessions if isinstance(s, dict) and s.get("id") and home(s.get(key)) == tree]
        if found:
            found.sort(key=lambda s: "claude" not in (s.get("agent") or ""))
            return found[0]["id"]
    return None


def tell_target(directory, name, cwd=None, or_session=False):
    """The session id for `seat` or for a stream (its name in the log, or its slug); NotTold says why there
    is none. With `or_session`, a name no worktree carries is taken as a session id."""
    if name == "seat":
        seat = read_seat(directory)
        if not seat:
            raise NotTold(f"no seat is registered; `{_self_command()} seat --here` in the seat's pane fixes it")
        return seat["session"]
    trees = worktrees(cwd)
    tree = stream_worktree(name, trees)
    if not tree:
        if or_session:
            return name
        raise NotTold(f"no session found for the stream {name}: no worktree of this repository is named for it")
    code, out, err = term(["ls", "--json"])
    if code != 0:
        raise NotTold(f"no session found for the stream {name}: term.py ls exited {code}: {_last_line(err, out)}")
    try:
        listed = json.loads(out).get("sessions") or []
    except (ValueError, AttributeError):
        raise NotTold(f"no session found for the stream {name}: term.py ls printed no session list")
    session = stream_session(tree, trees, listed)
    if not session:
        raise NotTold(f"no session found for the stream {name}: no terminal has its cwd in {tree}")
    return session


def relay(directory, line, tell=None, cwd=None):
    """Tell a terminal about the line `log` just wrote. Returns the session told; None when the line is for
    nobody, or for the terminal this command runs in. Raises NotTold when it could not be delivered.

    `tell` names who (`seat`, a stream, a session id). Without it an OWED line goes to the seat, a PAID line
    to the stream that wrote the OWED line, and any other line to nobody.
    """
    parsed = parse_line(line)
    if not parsed:
        return None
    _, who, text = parsed
    target, message = tell, f"{who}: {text}"
    paid = PAID_LINE.match(text)
    if OWED_LINE.match(text):
        target = target or "seat"
    elif paid:
        entry = _owed_entries(read_lines(directory))[0].get(paid.group(1))
        if entry:
            note = re.sub(r"^[\s:,.;–—-]+", "", text[paid.end():]).strip()
            message = f"PAID {entry['id']}: {entry['what']}" + (f" -- {note}" if note else "")
            # The payer wrote the OWED line itself (the seat's own list): the stream it names is the one to tell.
            target = target or (entry["stream"] if entry["who"] == who else entry["who"])
    if not target:
        return None
    session = tell_target(directory, target, cwd, or_session=bool(tell))
    if session == os.environ.get("HC_TERMINAL_ID"):
        return None
    code, out, err = term(["send", session, message])
    if code != 0:
        # After a timeout the server's own send can still be waiting on a draft in that terminal.
        late = "; the text may still arrive" if code == 124 else ""
        raise NotTold(f"term.py send {session} exited {code}: {_last_line(err, out)}{late}")
    return session


# ------------------------------------------------------------------ show


def show(directory, holds=False, owed=False, log=None, now=None, zone=None):
    """The report `show` prints, as a string."""
    now = now or dt.datetime.now(UTC)
    zone = zone or local_zone()
    everything = not holds and not owed and log is None
    lines = read_lines(directory)
    out = [f"coord: {directory}"]
    if everything or owed:
        out.append(seat_line(directory))
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
    global _CHDIR
    _CHDIR = None
    ap = argparse.ArgumentParser(prog="coord.py", description="The streams skill's coordination state.")
    ap.add_argument("-C", dest="chdir", metavar="DIR",
                    help="run as if started in DIR, like git -C: the repository there (a seat serving several)")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="create coord/ and its files")
    p_log = sub.add_parser("log", help="append one line to coord/log.md, and tell the terminal it concerns",
                           description="Append one line to coord/log.md. Once it is written, an OWED line is typed "
                                       "into the seat's terminal and a PAID line into the terminal of the stream "
                                       "that wrote the OWED line. A relay that fails is reported on stderr and "
                                       "never fails the log.")
    p_log.add_argument("text", nargs="+")
    p_log.add_argument("--as", dest="who")
    p_log.add_argument("--for", dest="for_")
    p_log.add_argument("--until")
    g_tell = p_log.add_mutually_exclusive_group()
    g_tell.add_argument("--tell", metavar="WHO",
                      help="also type the line into a terminal: seat (the registered one), a stream (its name in "
                           "the log, or its slug) or a session id. Without it an OWED line goes to the seat and a "
                           "PAID line to the stream that wrote the OWED line")
    g_tell.add_argument("--no-tell", action="store_true", help="tell no terminal, also for an OWED or PAID line")
    p_show = sub.add_parser("show", help="the seat's terminal, open holds, expired holds, unpaid OWED, newest "
                                         "log lines")
    p_show.add_argument("--holds", action="store_true")
    p_show.add_argument("--owed", action="store_true")
    p_show.add_argument("--log", type=int, metavar="N")
    p_seat = sub.add_parser("seat", help="print the seat's registered terminal (coord/seat.json), or change it",
                            description="The terminal `log` tells about an OWED line and a `--tell seat` line. "
                                        "With no flag: print it.")
    g_seat = p_seat.add_mutually_exclusive_group()
    g_seat.add_argument("--here", action="store_true",
                       help="register the terminal this command runs in ($HC_TERMINAL_ID, set by herdr-core)")
    g_seat.add_argument("--set", dest="session", metavar="SESSION", help="register this session id")
    g_seat.add_argument("--clear", action="store_true", help="remove the registration")
    p_repos = sub.add_parser("repos", help="every repository a seat serves, and whether it is still the seat there",
                             description="The repositories a seat was registered in (seat --here or --set), from "
                                         "the user's seats file. Default: this terminal's session ($HC_TERMINAL_ID), "
                                         "else the seat registered in the current repository.")
    p_repos.add_argument("--seat", metavar="SESSION", help="the seat's session id")
    p_repos.add_argument("--paths", action="store_true", help="only the main checkouts where it is the seat, one per "
                                                              "line (for a loop)")
    p_cfg = sub.add_parser("config", help="the project's facts from .devmeta/streams.md, or detected")
    p_cfg.add_argument("--file", help="the project file (default .devmeta/streams.md at the top)")
    p_cfg.add_argument("--slug", help="also print the worktree path for this stream slug")
    p_cfg.add_argument("--json", action="store_true")
    p_cfg.add_argument("--get", metavar="FACT", help=f"print one fact's bare value: {', '.join(GET_FACTS)}")
    p_init = sub.add_parser("init-file", help="write .devmeta/streams.md from flags, only non-empty sections")
    p_init.add_argument("--file", help="where to write (default .devmeta/streams.md at the top)")
    p_init.add_argument("--trunk")
    p_init.add_argument("--worktree-root")
    p_init.add_argument("--at-cut", action="append", help="a line for ## At cut (repeatable)")
    p_init.add_argument("--at-landing", action="append", help="a line for ## At landing (repeatable)")
    p_init.add_argument("--resources", action="append", help="a line for ## Resources (repeatable)")
    p_init.add_argument("--force", action="store_true", help="replace an existing file")
    a = ap.parse_args(argv)

    if a.chdir:
        target = os.path.expanduser(a.chdir)
        if not os.path.isdir(target):
            print(f"coord: -C {a.chdir}: no such directory", file=sys.stderr)
            return 2
        os.chdir(target)
        _CHDIR = os.path.realpath(target)

    if a.command == "repos":
        session = (a.seat or "").strip()
        if not session:
            # This terminal, when it is a seat; else the seat registered in this repository (a check run
            # from a plain terminal must report on the seat, not on that terminal).
            mine = os.environ.get("HC_TERMINAL_ID", "").strip()
            here = coord_dir()
            seat = read_seat(here) if here else None
            registered = seat["session"] if seat else ""
            session = mine if (mine and repos_of(mine)) else (registered or mine)
        if not session:
            print("coord repos: which seat? Give --seat <session>, or run it in the seat's pane.", file=sys.stderr)
            return 2
        found = repos_of(session)
        if a.paths:
            for repo, state in found:
                if state == "seat":
                    print(repo)
            return 0
        if not found:
            print(f"seat {session}: no repositories recorded ({seats_file()})")
            return 0
        print(f"seat {session} serves:")
        for repo, state in found:
            print(f"  {repo}" + ("" if state == "seat" else f"  ({state})"))
        return 0

    if a.command == "config":
        try:
            facts = config(path=a.file, slug=a.slug)
        except CoordError as err:
            print(f"coord config: {err}", file=sys.stderr)
            return 1
        if a.get:
            try:
                value = get_fact(facts, a.get)
            except CoordError as err:
                print(f"coord config: {err}", file=sys.stderr)
                return 2
            if value:
                print(value)
            elif a.get == "at-landing" and facts["at_landing"].get("hint"):
                print(f"coord config: no ## At landing; {facts['at_landing']['hint']}", file=sys.stderr)
            return 0
        print(json.dumps(facts, indent=2, ensure_ascii=False) if a.json else show_config(facts))
        return 0

    if a.command == "init-file":
        try:
            written = init_file(path=a.file, force=a.force, trunk=a.trunk, worktree_root=a.worktree_root,
                                at_cut=a.at_cut, at_landing=a.at_landing, resources=a.resources)
        except CoordError as err:
            print(f"coord init-file: {err}", file=sys.stderr)
            return 2
        print(f"wrote {written}")
        return 0

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
        if not a.no_tell:
            try:
                told = relay(directory, line, tell=a.tell)
                if told:
                    print(f"told {told}")
            except NotTold as err:
                print(f"coord log: written, not delivered: {err}", file=sys.stderr)
            except Exception as err:  # the line is written: no relay failure may fail the log
                print(f"coord log: written, not delivered: {type(err).__name__}: {err}", file=sys.stderr)
        return 0

    if a.command == "seat":
        if a.clear:
            was = clear_seat(directory)
            repo = main_checkout()
            if was and repo:
                forget_repo(was["session"], repo)
            print(f"seat: cleared (was {was['session']})" if was else "seat: not registered; nothing to clear")
            return 0
        if a.here or a.session is not None:
            session = a.session
            if a.here:
                session = os.environ.get("HC_TERMINAL_ID", "").strip()
                if not session:
                    print(f"coord seat: HC_TERMINAL_ID is not set, so this is not a herdr-core (hc) terminal. Name "
                          f"the session: {_self_command()} seat --set <session> (`term.py ls` lists them).",
                          file=sys.stderr)
                    return 2
            try:
                set_seat(directory, session)
            except CoordError as err:
                print(f"coord seat: {err}", file=sys.stderr)
                return 2
            repo = main_checkout()
            if repo:
                record_repo(session.strip(), repo)
        print(seat_line(directory))
        if not read_seat(directory):
            print(f"  register it in the seat's pane: {_self_command()} seat --here")
        return 0

    print(show(directory, holds=a.holds, owed=a.owed, log=a.log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
