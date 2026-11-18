#!/usr/bin/env python3
"""Restart idle Claude Code sessions that run an older claude binary, resuming each session.

  herdr-reload.py            dry run: list every Claude session and what would happen to it
  herdr-reload.py --apply    restart every session marked "reload"
  herdr-reload.py --apply t2 laptop/t5   restart only those (must still be "reload")
  herdr-reload.py --force    restart every "reload" session AND queue a note to each stale busy
                             session's agent asking it to tell the user to restart that session
  --server hc|herdr          force one terminal server (default: hc when it holds Claude sessions,
                             else herdr)
  --local                    leave the connected machines alone (hc only)

A running process cannot swap its executable. The only way onto a newer binary is
exit + resume, which keeps the conversation.

Two terminal servers can hold the sessions: `hc` (herdr-core, the server behind the herdr-app
window; sessions on its connected machines are covered too, addressed `machine/t7`) and the older
`herdr` (local server only). Every outside call goes through run(), so the tests can fake them.
"""
import base64
import json
import os
import re
import shlex
import subprocess
import sys
import time

EXIT_TIMEOUT_S = 30
START_TIMEOUT_S = 60
SHELLS = {"bash", "zsh", "fish", "sh", "dash", "nu", "ksh", "tcsh", "csh"}
UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


class Fail(Exception):
    """A step that went wrong, in one line the user can read."""


def run(argv, timeout=60, plain=False):
    """(returncode, stdout bytes, stderr bytes). The one door to every outside program.

    plain=True runs it without HC_TERMINAL_ID: `hc send` from inside an hc terminal wraps the text
    as <hc from="t6">...</hc>, and then Claude no longer sees `/exit` as a command."""
    env = {k: v for k, v in os.environ.items() if k != "HC_TERMINAL_ID"} if plain else None
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout, env=env)
    except FileNotFoundError:
        return 127, b"", f"{argv[0]}: not installed".encode()
    except subprocess.TimeoutExpired:
        return 124, b"", f"{argv[0]}: no answer in {timeout}s".encode()
    return p.returncode, p.stdout, p.stderr


def say(rc, out, err):
    """The last line of what a failed command printed."""
    lines = ((err or b"").decode(errors="replace").strip() or (out or b"").decode(errors="replace").strip()).splitlines()
    return lines[-1] if lines else f"exit {rc}"


def jload(raw):
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def version_of(path):
    m = re.search(r"(\d+\.\d+\.\d+)", path or "")
    return m.group(1) if m else "?"


def new_args(argv, session_id):
    """Original flags minus any resume/continue/session-id, plus --resume <session>."""
    out, skip = [], False
    for a in argv[1:]:
        if skip:
            skip = False
            continue
        if a in ("--resume", "-r", "--session-id"):
            skip = True
            continue
        if a.startswith(("--resume=", "--session-id=")) or a in ("--continue", "-c"):
            continue
        out.append(a)
    return out + ["--resume", session_id]


def resume_id(argv):
    """The session id an already-resumed process was started with, if its flags say so."""
    for i, a in enumerate(argv[1:], 1):
        if a in ("--resume", "-r", "--session-id") and i + 1 < len(argv) and re.fullmatch(UUID, argv[i + 1]):
            return argv[i + 1]
        m = re.fullmatch(rf"--(?:resume|session-id)=({UUID})", a)
        if m:
            return m.group(1)
    return None


# ------------------------------------------------------------------------------------------ hosts

class Host:
    """A machine's /proc and shell, here or on a machine hc is connected to (`hc exec --on`)."""

    def __init__(self, machine=None):
        self.machine = machine
        self._target = None

    def sh(self, *argv, timeout=60):
        """(exit code, stdout text) of one program, run without a shell."""
        if not self.machine:
            rc, out, _ = run(list(argv), timeout)
            return rc, out.decode(errors="replace")
        rc, out, err = run(["hc", "exec", "--on", self.machine, "--json", "--", *argv], timeout + 10)
        data = jload(out) if rc == 0 else None
        if not isinstance(data, dict):
            return rc or 1, ""
        try:
            text = base64.b64decode(data.get("stdout") or "").decode(errors="replace")
        except ValueError:
            text = ""
        return data.get("code", 1), text

    def exe(self, pid):
        rc, out = self.sh("readlink", f"/proc/{pid}/exe")
        return (out.strip() or None) if rc == 0 else None

    def cmdline(self, pid):
        rc, out = self.sh("cat", f"/proc/{pid}/cmdline")
        return [x for x in out.split("\0") if x] if rc == 0 else None

    def session_ids(self, pid):
        """Claude keeps /tmp/claude-<uid>/<folder>/<session id>/tasks open: that names its session."""
        rc, out = self.sh("ls", "-l", f"/proc/{pid}/fd")
        return set(re.findall(rf"/({UUID})/tasks", out)) if rc == 0 else set()

    def transcript_ids(self, pid):
        """Transcripts of this process's folder written since it started (a session that ran a turn)."""
        rc, raw = self.sh("cat", f"/proc/{pid}/environ")
        env = dict(x.split("=", 1) for x in raw.split("\0") if "=" in x) if rc == 0 else {}
        cfg = env.get("CLAUDE_CONFIG_DIR") or os.path.join(env.get("HOME", ""), ".claude")
        rc1, cwd = self.sh("readlink", f"/proc/{pid}/cwd")
        rc2, started = self.sh("stat", "-c", "%Y", f"/proc/{pid}")
        if rc1 or rc2 or not cwd.strip() or not started.strip().isdigit():
            return set()
        folder = f"{cfg}/projects/{re.sub('[^A-Za-z0-9]', '-', cwd.strip())}"
        rc, out = self.sh("find", folder, "-maxdepth", "1", "-name", "*.jsonl", "-newermt", f"@{started.strip()}")
        names = [os.path.basename(x)[:-6] for x in out.split("\n") if x.endswith(".jsonl")] if rc == 0 else []
        return {n for n in names if re.fullmatch(UUID, n)}

    def target(self):
        """Canonical path of the claude binary a fresh `claude` would run here right now, or None."""
        if self._target is None:
            found = ""
            for cmd in (("mise", "which", "claude"), ("sh", "-lc", "command -v claude")):
                rc, out = self.sh(*cmd)
                path = out.strip().splitlines()[-1] if rc == 0 and out.strip() else ""
                if path:
                    rc, real = self.sh("readlink", "-f", path)
                    path = real.strip() if rc == 0 and real.strip() else path
                    if os.path.basename(path) != "mise":  # a mise wrapper that could not resolve
                        found = path
                        break
            self._target = found
        return self._target or None


# ------------------------------------------------------------------------------------------ hc

class Hc:
    name = "hc"

    def __init__(self, local=False):
        self.local = local

    def rows(self):
        rc, out, err = run(["hc", "ls", "--json"], 20)
        data = jload(out) if rc == 0 else None
        if not isinstance(data, dict):
            raise Fail(f"hc ls failed: {say(rc, out, err)}")
        rows = []
        for t in data.get("terminals") or []:
            if t.get("state") != "live" or t.get("agent") not in ("claude-code", "claude") or not t.get("address"):
                continue
            addr = t["address"]
            machine = addr.rpartition("/")[0] or None
            if machine and self.local:
                continue
            status = t.get("status")
            row = {"id": addr, "machine": machine, "cwd": t.get("cwd"), "title": t.get("where", ""), "turn": t.get("turn"),
                   "status": status.get("state") if isinstance(status, dict) else status,
                   "me": not machine and addr == os.environ.get("HC_TERMINAL_ID")}
            g = self.get(addr)
            if not g:
                row["skip"] = "hc get failed (machine not connected?)"
            else:
                fg = g.get("foreground") or {}
                root = os.path.basename((g.get("argv") or [""])[0])
                if fg.get("name") != "claude" or not fg.get("pid"):
                    row["skip"] = "no claude process in foreground"
                elif root not in SHELLS:
                    row["skip"] = "claude is the terminal's own program: exiting it would end the terminal"
                else:
                    row.update(pid=fg["pid"], argv=fg.get("argv"), session=(g.get("labels") or {}).get("session"))
            rows.append(row)
        return rows

    def get(self, addr):
        rc, out, _ = run(["hc", "get", addr, "--json"], 20)
        data = jload(out) if rc == 0 else None
        return data if isinstance(data, dict) else None

    def foreground_pid(self, addr):
        fg = (self.get(addr) or {}).get("foreground") or {}
        return fg.get("pid") if fg.get("name") == "claude" else None

    def reload(self, row, host, taken):
        addr = row["id"]
        rc, out, err = run(["hc", "send", addr, "/exit", "--if", "idle", "--json"], 90, plain=True)
        if rc != 0:
            return f"FAILED: /exit not sent: {say(rc, out, err)}"
        deadline = time.time() + EXIT_TIMEOUT_S
        while time.time() < deadline:
            if self.foreground_pid(addr) is None:
                break
            time.sleep(0.5)
        else:
            return f"FAILED: claude did not exit within {EXIT_TIMEOUT_S}s (draft text in its input box?) - check the session"
        line = shlex.join(["claude", *row["cmd"]])
        rc, out, err = run(["hc", "send", addr, line, "--json"], 90, plain=True)
        if rc != 0:
            return f"FAILED to restart: {say(rc, out, err)}  (run by hand: {line})"
        deadline = time.time() + START_TIMEOUT_S
        while time.time() < deadline:
            pid = self.foreground_pid(addr)
            if pid:
                return f"restarted on {version_of(host.exe(pid))}"
            time.sleep(0.5)
        return f"FAILED: claude did not start within {START_TIMEOUT_S}s (run by hand: {line})"

    def notify(self, row, note):
        if row["status"] == "blocked":
            return "NOT NOTIFIED: blocked on a dialog (hc won't type into it) - tell the user yourself"
        rc, out, err = run(["hc", "send", row["id"], note, "--json"], 90, plain=True)
        return "restart note queued to its agent" if rc == 0 else f"NOT NOTIFIED: {say(rc, out, err)}"


# ------------------------------------------------------------------------------------------ herdr

class Herdr:
    name = "herdr"

    def call(self, *args, check=True):
        rc, out, err = run(["herdr", *args], 120)
        if check and rc != 0:
            raise Fail(f"herdr {' '.join(args)} failed: {say(rc, out, err)}")
        return rc, out, err

    def json(self, *args):
        return jload(self.call(*args)[1])["result"]

    def rows(self):
        try:
            me = self.json("pane", "current")["pane"]["pane_id"]
        except (Fail, TypeError, KeyError):
            me = None
        rows = []
        for a in self.json("agent", "list")["agents"]:
            if a.get("agent") != "claude":
                continue
            pane = a["pane_id"]
            row = {"id": pane, "machine": None, "cwd": a.get("cwd"), "status": a.get("agent_status"),
                   "title": a.get("terminal_title_stripped", ""), "me": pane == me,
                   "session": (a.get("agent_session") or {}).get("value"), "name": a.get("name")}
            try:
                info, proc = self.claude_proc(pane)
            except Fail as e:
                row["skip"] = f"process-info failed: {e}"
            else:
                if proc:
                    row.update(pid=proc["pid"], argv=proc.get("argv"))
                else:
                    row["skip"] = "no claude process in foreground"
            rows.append(row)
        return rows

    def claude_proc(self, pane):
        info = self.json("pane", "process-info", "--pane", pane)["process_info"]
        procs = [p for p in info.get("foreground_processes", []) if p.get("name") == "claude"]
        return info, (procs[0] if procs else None)

    def reload(self, row, host, taken):
        pane = row["id"]
        self.call("agent", "prompt", pane, "/exit")  # herdr refuses with agent_blocked if a dialog is open
        deadline = time.time() + EXIT_TIMEOUT_S
        while time.time() < deadline:
            info, proc = self.claude_proc(pane)
            if not proc and info.get("foreground_process_group_id") == info.get("shell_pid"):
                break
            time.sleep(0.5)
        else:
            return f"FAILED: claude did not exit within {EXIT_TIMEOUT_S}s (draft text in its input box?) - check the pane"
        name = agent_name(row["cwd"], taken)
        rc, out, err = self.call("agent", "start", name, "--kind", "claude", "--pane", pane,
                                 "--timeout", str(START_TIMEOUT_S * 1000), "--", *row["cmd"], check=False)
        if rc != 0:
            return f"FAILED to restart: {say(rc, out, err)}  (run by hand: claude {shlex.join(row['cmd'])})"
        _, proc = self.claude_proc(pane)
        return f"restarted as '{name}' on {version_of(host.exe(proc['pid']) if proc else None)}"

    def notify(self, row, note):
        rc, out, err = self.call("agent", "prompt", row["id"], note, check=False)
        if rc == 0:
            return "restart note queued to its agent"
        msg = (err or out).decode(errors="replace").strip()
        if "agent_blocked" in msg:
            return "NOT NOTIFIED: blocked on a dialog (herdr won't type into it) - tell the user yourself"
        return f"NOT NOTIFIED: {msg}"


def agent_name(cwd, taken):
    base = re.sub(r"[^a-z0-9_-]+", "-", os.path.basename(cwd or "claude").lower()).strip("-_")
    if not base or not base[0].isalpha():
        base = "c-" + base
    base = base[:28]
    name, n = base, 2
    while name in taken:
        name, n = f"{base[:28]}-{n}", n + 1
    taken.add(name)
    return name


def choose(forced=None, local=False):
    """hc when it holds Claude sessions; else herdr when its server answers; else hc."""
    if forced:
        return Hc(local) if forced == "hc" else Herdr()
    hc, hc_why = Hc(local), None
    try:
        if hc.rows():
            return hc
    except Fail as e:
        hc_why = str(e)
    herdr = Herdr()
    try:
        if herdr.rows():
            return herdr
    except (Fail, TypeError, KeyError):
        pass
    if hc_why:
        sys.exit(f"herdr-reload: no terminal server answers ({hc_why}; herdr is not running)")
    return hc  # hc answers, with no Claude sessions


# ------------------------------------------------------------------------------------------ plan

def plan(backend):
    hosts = {}
    rows = backend.rows()
    for r in rows:
        host = hosts.setdefault(r["machine"], Host(r["machine"]))
        r["host"] = host
        r["session"] = r.get("session") or None
        r.setdefault("version", "?")
        r["why"] = ""
        if r.get("skip"):
            r.update(action="skip", why=r["skip"])
            continue
        exe = host.exe(r["pid"])
        argv = host.cmdline(r["pid"]) or r.get("argv")
        if not argv:
            r.update(action="skip", why="cannot read the process's arguments")
            continue
        r.update(exe=exe, argv=argv, version=version_of(exe) + (" (deleted)" if exe and exe.endswith(" (deleted)") else ""))
        target = host.target()
        r["target"] = target
        if r["me"]:
            r.update(action="skip", why="this session (the one running the reload) - /exit and `claude --resume` it yourself")
        elif target and exe == target:
            r.update(action="ok", why="already on the current binary")
        elif not target:
            where = f" on {r['machine']}" if r["machine"] else ""
            r.update(action="skip", why=f"cannot resolve the current claude binary{where}")
        else:
            r["session"] = r["session"] or resume_id(argv)
            if not r["session"]:
                ids = host.session_ids(r["pid"])
                if not ids and (r.get("turn") or 0) > 0:
                    ids = host.transcript_ids(r["pid"])
                r["session"] = next(iter(ids)) if len(ids) == 1 else None
            if r["status"] != "idle":
                r.update(action="busy", why=f"status is {r['status']} - with --force its agent gets a restart note")
            elif not r["session"]:
                r.update(action="skip", why="no session id (it has not run a turn yet, or it holds several)")
            else:
                r.update(action="reload", cmd=new_args(argv, r["session"]))
    return rows


def main():
    args = sys.argv[1:]
    forced = None
    if "--server" in args:
        i = args.index("--server")
        forced = args[i + 1] if i + 1 < len(args) else None
        if forced not in ("hc", "herdr"):
            sys.exit("herdr-reload: --server takes hc or herdr")
        del args[i:i + 2]
    force = "--force" in args
    local = "--local" in args
    apply = force or "--apply" in args
    only = [a for a in args if a not in ("--apply", "--force", "--local")]
    backend = choose(forced, local)
    try:
        rows = plan(backend)
    except Fail as e:
        sys.exit(f"herdr-reload: {e}")
    targets = sorted({r["target"] for r in rows if r.get("target")})
    print(f"server: {backend.name}   current binary: {', '.join(f'{t} ({version_of(t)})' for t in targets) or '?'}\n")
    width = max([len(r["id"]) for r in rows] + [9])
    for r in rows:
        line = f"{r['id']:<{width}} {r['version']:<18} {str(r['status']):<8} {r['action']:<6} {os.path.basename(r['cwd'] or '')}"
        if r.get("title"):
            line += f"  \"{r['title']}\""
        print(line)
        if r["why"]:
            print(f"{'':<{width}} {r['why']}")
        if r["action"] == "reload":
            print(f"{'':<{width}} -> claude {shlex.join(r['cmd'])}")
    todo = [r for r in rows if r["action"] == "reload" and (not only or r["id"] in only)]
    busy = [r for r in rows if r["action"] == "busy" and (not only or r["id"] in only)]
    missing = [p for p in only if p not in {r["id"] for r in todo + busy}]
    if missing:
        print(f"\nnot reloadable now, skipped: {' '.join(missing)}")
    if not apply:
        print(f"\ndry run - {len(todo)} session(s) would be restarted (--apply), "
              f"{len(busy)} busy session(s) would get a restart note (--force).")
        return
    taken = {r["name"] for r in rows if r.get("name")}
    print()
    failed = 0
    for r in todo:
        try:
            res = backend.reload(r, r["host"], taken)
        except Fail as e:
            res = f"FAILED: {e}"
        failed += res.startswith("FAILED")
        print(f"{r['id']:<{width}} {res}")
    if force:
        for r in busy:
            resume = f"claude --resume {r['session']}" if r["session"] else "claude --continue"
            note = (f"[herdr-reload] This session runs an old Claude Code binary ({r['version']}); "
                    f"{version_of(r['target'])} is installed. Finish what you are doing - do not stop early "
                    f"and do not restart anything yourself. At the end of your reply, tell the user to "
                    f"restart this session to pick up the new version: /exit, then `{resume}`, "
                    f"or run /herdr-reload once this session is idle.")
            res = backend.notify(r, note)
            failed += res.startswith("NOT")
            print(f"{r['id']:<{width}} {res}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
