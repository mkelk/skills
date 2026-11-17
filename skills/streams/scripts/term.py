#!/usr/bin/env python3
"""One door between the streams tooling and the terminal server the sessions run in.

Two terminal servers can hold the sessions: `hc` (herdr-core, https://github.com/herdrdev/herdr-core,
the server behind the herdr-app window, https://github.com/herdrdev/herdr-app) and herdr
(https://github.com/herdrdev/herdr, written against 0.9.5, its own server read through
`~/.config/herdr/herdr.sock`). Every caller in the streams skill goes through this file, so moving
sessions from one server to the other changes nothing upstream, and this file is the one place to
adapt for another terminal server. With neither one, every command exits 2 and the seat prints what
to open by hand.

    term.py which [--json]                         which server answers, and what each one says
    term.py ls [--json]                            sessions: id, cwd, foreground_cwd, label, agent,
                                                   state, status, session
    term.py read <session> [--lines N] [--json]    what the session shows, with N lines of history
    term.py send <session> <text> [--json]         type the text and press Enter
    term.py start <cwd> <label> [--json] -- <cmd...>
                                                   start a program (a Claude session) in a new place
    term.py wait <session> [--timeout S] [--json]  until it stops working (exit 1 on timeout,
                                                   exit 2 when the server reports an error)

`--server hc|herdr` forces one server. Every `--json` answer carries `"server": "hc"|"herdr"`.

Which server answers (the rule, in this order):
  1. hc answers with sessions: `hc ls --json` exits 0, prints JSON, and lists at least one live
     terminal. -> hc.
  2. herdr answers with sessions: `~/.config/herdr/herdr.sock` exists, `herdr api snapshot` exits 0
     and prints JSON, and its snapshot has at least one pane. -> herdr.
  3. hc answers with no sessions. -> hc (hc is the server new sessions go to).
  4. herdr answers with no sessions. -> herdr.
  5. Neither answers: one line on stderr, exit 2.
So while every session runs in herdr and hc is empty, the answer is herdr; once one session runs in
hc, it is hc. While sessions are moving one at a time, `ls` lists the chosen server's sessions and then
the other server's, each session tagged with its own `server`; `read`, `send` and `wait` look the
session up in both (hc first) and use the server that has it.

A session's `state` is `idle`, `working`, `blocked` or `unknown`. The server's own word stays in
`status` (herdr: working, idle, done, blocked; hc: idle, working, done, blocked, error): `done` reads
`idle`, `blocked` (waiting on a prompt) stays `blocked`, anything else reads `unknown`, so a session
waiting on a prompt is never taken for idle. `foreground_cwd` is the directory of the program in the
foreground, when the server gives it (else empty); `session` is the agent's own session id (the
string inside herdr's `agent_session` object; hc's `session` label), or null.

Python 3 standard library only.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SERVERS = ("hc", "herdr")
LIST_TIMEOUT = 20  # seconds for a list or snapshot call; a server that does not answer by then is down


class TermError(Exception):
    """A failure this door reports in one line; `code` is the exit code (2: no server answers)."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def _run(args, timeout=LIST_TIMEOUT):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, "", f"{args[0]} did not answer in {timeout}s")


def _json(text):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _state(word):
    if word == "working":
        return "working"
    if word in ("idle", "done"):
        return "idle"
    if word == "blocked":
        return "blocked"
    return "unknown"


def herdr_socket():
    return os.path.expanduser("~/.config/herdr/herdr.sock")


# ---------------------------------------------------------------------------------------------- probing

def probe_hc():
    """{'answers': bool, 'sessions': [...], 'why': str}"""
    if not shutil.which("hc"):
        return {"answers": False, "sessions": [], "why": "hc is not installed"}
    r = _run(["hc", "ls", "--json"])
    if r is None:
        return {"answers": False, "sessions": [], "why": "hc is not installed"}
    data = _json(r.stdout) if r.returncode == 0 else None
    if not isinstance(data, dict):
        why = (r.stderr or r.stdout).strip().splitlines()
        return {"answers": False, "sessions": [],
                "why": f"hc ls failed: {why[-1] if why else 'exit ' + str(r.returncode)}"}
    sessions = [s for s in (_hc_session(t) for t in data.get("terminals") or []) if s]
    return {"answers": True, "sessions": sessions, "why": f"{len(sessions)} live terminal(s)"}


def _hc_session(t):
    if not isinstance(t, dict) or t.get("state") == "finished" or not t.get("address"):
        return None
    status = t.get("status")
    word = status.get("state") if isinstance(status, dict) else status if isinstance(status, str) else None
    labels = t.get("labels") if isinstance(t.get("labels"), dict) else {}
    fg = t.get("foreground") if isinstance(t.get("foreground"), dict) else {}
    agent = t.get("agent") or (os.path.basename(t["argv"][0]) if t.get("argv") else "")
    return {
        "server": "hc",
        "id": t["address"],
        "cwd": t.get("cwd") or fg.get("cwd") or "",
        "foreground_cwd": fg.get("cwd") or "",
        "label": labels.get("stream") or t.get("name") or t.get("where") or "",
        "agent": agent or "",
        "state": _state(word),
        "status": word,
        "session": labels.get("session"),
    }


def probe_herdr():
    if not os.path.exists(herdr_socket()):
        return {"answers": False, "sessions": [], "why": f"herdr is not running ({herdr_socket()} is absent)"}
    r = _run(["herdr", "api", "snapshot"])
    if r is None:
        return {"answers": False, "sessions": [], "why": "herdr is not installed"}
    data = _json(r.stdout) if r.returncode == 0 else None
    snap = ((data or {}).get("result") or {}).get("snapshot") if isinstance(data, dict) else None
    if not isinstance(snap, dict):
        why = (r.stderr or r.stdout).strip().splitlines()
        return {"answers": False, "sessions": [],
                "why": f"herdr api snapshot failed: {why[-1] if why else 'exit ' + str(r.returncode)}"}
    spaces = {w.get("workspace_id"): w.get("label") for w in snap.get("workspaces") or [] if isinstance(w, dict)}
    panes = snap.get("panes")
    if panes is None:
        panes = snap.get("agents") or []
    sessions = [s for s in (_herdr_session(p, spaces) for p in panes) if s]
    return {"answers": True, "sessions": sessions, "why": f"{len(sessions)} pane(s)"}


def _herdr_session(p, spaces):
    if not isinstance(p, dict) or not p.get("pane_id"):
        return None
    sess = p.get("agent_session")
    sid = sess.get("value") if isinstance(sess, dict) else None
    word = p.get("agent_status") or None
    return {
        "server": "herdr",
        "id": p["pane_id"],
        "cwd": p.get("cwd") or "",
        "foreground_cwd": p.get("foreground_cwd") or "",
        "label": spaces.get(p.get("workspace_id")) or p.get("terminal_title_stripped") or "",
        "agent": p.get("agent") or "",
        "state": _state(word),
        "status": word,
        "session": sid if isinstance(sid, str) and sid else None,
    }


PROBES = {"hc": probe_hc, "herdr": probe_herdr}


def choose(forced=None):
    """(server, {server: probe}) by the rule in the module docstring; TermError(code 2) when none answers."""
    if forced:
        p = PROBES[forced]()
        if not p["answers"]:
            raise TermError(f"term: {forced} does not answer: {p['why']}", 2)
        return forced, {forced: p}
    probes = {"hc": probe_hc()}
    if probes["hc"]["answers"] and probes["hc"]["sessions"]:
        probes["herdr"] = probe_herdr()  # still read, for `ls` mid-move and for `which`
        return "hc", probes
    probes["herdr"] = probe_herdr()
    for server, need_sessions in (("herdr", True), ("hc", False), ("herdr", False)):
        p = probes[server]
        if p["answers"] and (p["sessions"] or not need_sessions):
            return server, probes
    raise TermError(f"term: no terminal server answers ({probes['hc']['why']}; {probes['herdr']['why']})", 2)


def sessions(forced=None):
    """(server, [session, ...]): the chosen server's sessions, then the other one's (each tagged)."""
    server, probes = choose(forced)
    out = list(probes[server]["sessions"])
    for other, p in probes.items():
        if other != server and p["answers"]:
            out += p["sessions"]
    return server, out


def locate(session, forced=None):
    """The server that holds this session: hc first, then herdr, else the chosen server."""
    if forced:
        choose(forced)
        return forced
    server, probes = choose()
    for name in SERVERS:
        p = probes.get(name) or PROBES[name]()
        if p["answers"] and any(s["id"] == session for s in p["sessions"]):
            return name
    return server


# ---------------------------------------------------------------------------------------------- actions

def _check(r, what):
    if r is None:
        raise TermError(f"term: {what}: not installed", 2)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout).strip().splitlines()
        raise TermError(f"term: {what} failed: {msg[-1] if msg else 'exit ' + str(r.returncode)}")
    return r


def read(session, lines=15, forced=None):
    server = locate(session, forced)
    if server == "hc":
        r = _check(_run(["hc", "read", session, "--lines", str(lines), "--json"]), "hc read")
        data = _json(r.stdout)
        text = data.get("text", "") if isinstance(data, dict) else r.stdout
    else:
        r = _check(_run(["herdr", "pane", "read", session, "--lines", str(lines), "--format", "text"]),
                   "herdr pane read")
        text = r.stdout
    return {"server": server, "session": session, "text": text}


def send(session, text, forced=None):
    server = locate(session, forced)
    if server == "hc":
        r = _check(_run(["hc", "send", session, text, "--json"], timeout=300), "hc send")
    else:
        r = _check(_run(["herdr", "agent", "prompt", session, text], timeout=120), "herdr agent prompt")
    return {"server": server, "session": session, "sent": True, "result": _json(r.stdout)}


def wait(session, timeout=None, forced=None):
    server = locate(session, forced)
    limit = None if timeout is None else timeout + 30
    if server == "hc":
        args = ["hc", "wait", session, "--json"] + ([] if timeout is None else ["--timeout", str(timeout)])
        try:
            r = _check(_run(args, timeout=limit), "hc wait")
        except TermError as err:
            raise TermError(str(err), 2)
        data = _json(r.stdout)
        if not isinstance(data, dict) or not isinstance(data.get("ended"), bool):
            raise TermError(f"term: hc wait gave no `ended`: {r.stdout.strip()[:200]}", 2)
        ended = data["ended"]
    else:
        args = ["herdr", "agent", "wait", session] + ([] if timeout is None else ["--timeout", str(timeout * 1000)])
        r = _run(args, timeout=limit)
        if r is None:
            raise TermError("term: herdr agent wait: not installed", 2)
        data = _json(r.stdout)
        if r.returncode == 0:
            ended = True
        elif _herdr_timed_out(data, r):
            ended = False
        else:
            msg = (r.stderr or r.stdout).strip().splitlines()
            raise TermError(f"term: herdr agent wait failed: {msg[-1] if msg else 'exit ' + str(r.returncode)}", 2)
    return {"server": server, "session": session, "ended": ended, "result": data}


def _herdr_timed_out(data, r):
    """herdr's own timeout: error code `timeout` (or its "timed out waiting" message); nothing else."""
    err = data.get("error") if isinstance(data, dict) else None
    if isinstance(err, dict):
        return err.get("code") == "timeout"
    return "timed out waiting for agent" in (r.stderr or "") + (r.stdout or "")


def _slug(label):
    s = re.sub(r"[^a-z0-9_-]+", "-", label.lower()).strip("-")[:32]
    return s or None


def _pane_id(obj):
    """herdr's new pane: the root pane's id first, then any pane id anywhere in the answer."""
    res = obj.get("result") if isinstance(obj, dict) and isinstance(obj.get("result"), dict) else obj
    if isinstance(res, dict):
        for k in ("root_pane", "pane"):
            if isinstance(res.get(k), dict) and isinstance(res[k].get("pane_id"), str) and res[k]["pane_id"]:
                return res[k]["pane_id"]
        if isinstance(res.get("root_pane_id"), str) and res["root_pane_id"]:
            return res["root_pane_id"]
    return _find_key(obj, ("pane_id", "root_pane_id", "pane"))


def _find_key(obj, keys):
    """The first string value under any of these keys, anywhere in a JSON answer."""
    if isinstance(obj, dict):
        for k in keys:
            if isinstance(obj.get(k), str) and obj[k]:
                return obj[k]
        obj = list(obj.values())
    if isinstance(obj, list):
        for v in obj:
            found = _find_key(v, keys)
            if found:
                return found
    return None


def start(cwd, label, cmd, forced=None, workspace=None):
    """Start cmd in cwd, named label, where the human can see it. Returns the new session's id."""
    if not cmd:
        raise TermError("term: start needs a command after --")
    cwd = os.path.abspath(os.path.expanduser(cwd))
    server, _ = choose(forced)
    if server == "hc":
        tid, app_ok = None, False
        if shutil.which("herdr-app"):
            # Shown in the window: a space named after the stream, its first tab running the command.
            args = ["herdr-app", "do", "space.new", "--name", label, "--folder", cwd, "--tab", label,
                    "--argv", json.dumps(cmd)]
            if workspace:
                args = ["herdr-app", "do", "tab.new", "--space", workspace, "--name", label, "--folder", cwd,
                        "--argv", json.dumps(cmd)]
            r = _run(args, timeout=60)
            if r is not None and r.returncode == 0:
                app_ok = True
                tid = _find_key(_json(r.stdout), ("terminal",))
        if app_ok and not tid:
            # The window opened it, so the program is running there: never start a second one.
            raise TermError(f"term: herdr-app opened a space but named no terminal: {r.stdout.strip()[:200]}", 2)
        if tid:
            _check(_run(["hc", "label", tid, f"stream={label}"]), "hc label")
        else:
            # herdr-app is absent or exited non-zero: nothing was started.
            # No window to show it in: a terminal hc keeps alive, reachable by `hc attach`.
            args = ["hc", "run", "--bg", "--json", "--no-parent", "--outlive-parent", "--cwd", cwd,
                    "--label", f"stream={label}"]
            if _slug(label):
                args += ["--name", _slug(label)]
            r = _check(_run(args + ["--"] + list(cmd), timeout=120), "hc run")
            tid = _find_key(_json(r.stdout), ("address",))
        return {"server": "hc", "session": tid, "cwd": cwd, "label": label}

    # herdr (0.9.5): a workspace (nested under the given one as a worktree when --workspace is set), then
    # the program in its root pane.
    if workspace:
        args = ["herdr", "worktree", "open", "--workspace", workspace, "--path", cwd, "--label", label, "--no-focus"]
    else:
        args = ["herdr", "workspace", "create", "--cwd", cwd, "--label", label, "--no-focus"]
    r = _check(_run(args, timeout=60), " ".join(args[:3]))
    pane = _pane_id(_json(r.stdout))
    if not pane:
        raise TermError(f"term: {' '.join(args[:3])} named no pane: {r.stdout.strip()[:200]}")
    if os.path.basename(cmd[0]) == "claude":
        _check(_run(["herdr", "agent", "start", label, "--kind", "claude", "--pane", pane, "--"] + list(cmd[1:]),
                    timeout=330), "herdr agent start")
    else:
        _check(_run(["herdr", "pane", "run", pane] + list(cmd), timeout=60), "herdr pane run")
    return {"server": "herdr", "session": pane, "cwd": cwd, "label": label}


def which(forced=None):
    server, probes = choose(forced)
    out = {"server": server}
    for name, p in probes.items():
        out[name] = {"answers": p["answers"], "sessions": len(p["sessions"]), "why": p["why"]}
    return out


# ---------------------------------------------------------------------------------------------- CLI

def _print(obj, as_json, text):
    if as_json:
        print(json.dumps(obj, indent=None if isinstance(obj, dict) and "sessions" not in obj else 1))
    else:
        print(text)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = []
    if "--" in argv:
        i = argv.index("--")
        argv, cmd = argv[:i], argv[i + 1:]
    # --json and --server are read anywhere before `--`, so `term.py --json ls` and `term.py ls --json` agree.
    as_json = "--json" in argv
    argv = [x for x in argv if x != "--json"]
    forced = None
    for i, x in enumerate(argv):
        if x == "--server" or x.startswith("--server="):
            forced = x.split("=", 1)[1] if "=" in x else (argv[i + 1] if i + 1 < len(argv) else "")
            del argv[i:i + (1 if "=" in x else 2)]
            break
    if forced is not None and forced not in SERVERS:
        print(f"term: --server takes one of {', '.join(SERVERS)}", file=sys.stderr)
        return 2
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="JSON output")
    common.add_argument("--server", choices=SERVERS, help="use this server only")
    ap = argparse.ArgumentParser(prog="term.py", description="The streams skill's door to the terminal server.",
                                 parents=[common])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("which", parents=[common], help="which server answers")
    sub.add_parser("ls", parents=[common], help="list sessions")
    p = sub.add_parser("read", parents=[common], help="print a session's screen and history")
    p.add_argument("session")
    p.add_argument("--lines", type=int, default=15)
    p = sub.add_parser("send", parents=[common], help="type text into a session and press Enter")
    p.add_argument("session")
    p.add_argument("text")
    p = sub.add_parser("start", parents=[common], help="start a program: start <cwd> <label> -- <cmd...>")
    p.add_argument("cwd")
    p.add_argument("label")
    p.add_argument("--workspace", help="herdr: open as a worktree under this workspace; hc: a tab in this space")
    p = sub.add_parser("wait", parents=[common], help="wait until a session stops working")
    p.add_argument("session")
    p.add_argument("--timeout", type=int, help="seconds (exit 1 when it is still working then)")
    a = ap.parse_args(argv)
    a.json, a.server = as_json, forced

    try:
        if a.cmd == "which":
            w = which(a.server)
            _print(w, a.json, w["server"])
        elif a.cmd == "ls":
            server, ss = sessions(a.server)
            rows = [f"{s['server']:5} {s['id']:12} {s['state']:8} {s['agent']:8} {s['label'][:24]:24} {s['cwd']}"
                    for s in ss]
            _print({"server": server, "sessions": ss}, a.json, "\n".join(rows) or f"({server}: no sessions)")
        elif a.cmd == "read":
            r = read(a.session, a.lines, a.server)
            _print(r, a.json, r["text"].rstrip("\n"))
        elif a.cmd == "send":
            r = send(a.session, a.text, a.server)
            _print(r, a.json, f"sent to {r['session']} ({r['server']})")
        elif a.cmd == "start":
            r = start(a.cwd, a.label, cmd, a.server, a.workspace)
            _print(r, a.json, f"{r['session']} ({r['server']})")
        elif a.cmd == "wait":
            r = wait(a.session, a.timeout, a.server)
            _print(r, a.json, f"{r['session']} ({r['server']}): {'stopped' if r['ended'] else 'still working'}")
            return 0 if r["ended"] else 1
    except TermError as err:
        print(str(err), file=sys.stderr)
        return err.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
