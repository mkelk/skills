#!/usr/bin/env python3
"""Restart idle herdr Claude panes that run an older claude binary, resuming each session.

  herdr-reload.py            dry run: list every Claude pane and what would happen to it
  herdr-reload.py --apply    restart every pane marked "reload"
  herdr-reload.py --apply wY:p6 w19:p1   restart only those panes (must still be "reload")
  herdr-reload.py --force    restart every "reload" pane AND queue a note to each stale busy
                             pane's agent asking it to tell the user to restart that session

A running process cannot swap its executable. The only way onto a newer binary is
exit + resume, which keeps the conversation. Only the local herdr server is touched.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

EXIT_TIMEOUT_S = 30
START_TIMEOUT_MS = 60000


def herdr(*args, check=True):
    p = subprocess.run(["herdr", *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"herdr {' '.join(args)} failed: {(p.stderr or p.stdout).strip()}")
    return p


def herdr_json(*args):
    return json.loads(herdr(*args).stdout)["result"]


def current_binary():
    """Canonical path of the claude binary a fresh `claude` would run right now."""
    cand = None
    if shutil.which("mise"):
        p = subprocess.run(["mise", "which", "claude"], capture_output=True, text=True)
        if p.returncode == 0 and p.stdout.strip():
            cand = p.stdout.strip()
    if not cand:
        cand = shutil.which("claude")
        if cand and os.path.basename(os.path.realpath(cand)) == "mise":
            cand = None  # a mise command wrapper, but mise could not resolve it
    if not cand:
        sys.exit("herdr-reload: cannot resolve the current claude binary")
    return os.path.realpath(cand)


def version_of(path):
    m = re.search(r"(\d+\.\d+\.\d+)", path or "")
    return m.group(1) if m else "?"


def claude_proc(pane_id):
    info = herdr_json("pane", "process-info", "--pane", pane_id)["process_info"]
    procs = [p for p in info.get("foreground_processes", []) if p.get("name") == "claude"]
    return info, (procs[0] if procs else None)


def new_args(argv, session_id):
    """Original flags minus any resume/continue, plus --resume <session>."""
    out, skip = [], False
    for a in argv[1:]:
        if skip:
            skip = False
            continue
        if a in ("--resume", "-r"):
            skip = True
            continue
        if a.startswith("--resume=") or a in ("--continue", "-c"):
            continue
        out.append(a)
    return out + ["--resume", session_id]


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


def plan():
    target = current_binary()
    try:
        me = herdr_json("pane", "current")["pane"]["pane_id"]
    except RuntimeError:
        me = None
    rows = []
    for a in herdr_json("agent", "list")["agents"]:
        if a.get("agent") != "claude":
            continue
        pane = a["pane_id"]
        row = {"pane": pane, "cwd": a.get("cwd"), "status": a.get("agent_status"),
               "title": a.get("terminal_title_stripped", ""), "session": (a.get("agent_session") or {}).get("value")}
        try:
            info, proc = claude_proc(pane)
        except RuntimeError as e:
            row.update(action="skip", why=f"process-info failed: {e}")
            rows.append(row)
            continue
        if not proc:
            row.update(action="skip", why="no claude process in foreground")
            rows.append(row)
            continue
        try:
            exe = os.readlink(f"/proc/{proc['pid']}/exe")
        except OSError:
            exe = None
        row.update(pid=proc["pid"], argv=proc["argv"], exe=exe, version=version_of(exe))
        if exe and exe.endswith(" (deleted)"):
            row["version"] += " (deleted)"
        if pane == me:
            row.update(action="skip", why="this pane (the one running the reload) - /exit and `claude --resume` it yourself")
        elif exe == target:
            row.update(action="ok", why="already on the current binary")
        elif row["status"] != "idle":
            row.update(action="busy", why=f"status is {row['status']} - with --force its agent gets a restart note")
        elif not row["session"]:
            row.update(action="skip", why="herdr has no session id for it")
        else:
            row.update(action="reload", why="", cmd=new_args(proc["argv"], row["session"]))
        rows.append(row)
    return target, rows


def reload(row, taken):
    pane = row["pane"]
    # /exit via agent prompt: herdr refuses with agent_blocked if a dialog is open.
    herdr("agent", "prompt", pane, "/exit")
    deadline = time.time() + EXIT_TIMEOUT_S
    while time.time() < deadline:
        info, proc = claude_proc(pane)
        if not proc and info.get("foreground_process_group_id") == info.get("shell_pid"):
            break
        time.sleep(0.5)
    else:
        return f"FAILED: claude did not exit within {EXIT_TIMEOUT_S}s (draft text in its input box?) - check the pane"
    name = agent_name(row["cwd"], taken)
    p = herdr("agent", "start", name, "--kind", "claude", "--pane", pane,
              "--timeout", str(START_TIMEOUT_MS), "--", *row["cmd"], check=False)
    if p.returncode != 0:
        return f"FAILED to restart: {(p.stderr or p.stdout).strip()}  (run by hand: claude {' '.join(row['cmd'])})"
    _, proc = claude_proc(pane)
    exe = os.readlink(f"/proc/{proc['pid']}/exe") if proc else None
    return f"restarted as '{name}' on {version_of(exe)}"


def notify(row, target):
    resume = f"claude --resume {row['session']}" if row["session"] else "claude --continue"
    note = (f"[herdr-reload] This session runs an old Claude Code binary ({row['version']}); "
            f"{version_of(target)} is installed. Finish what you are doing - do not stop early "
            f"and do not restart anything yourself. At the end of your reply, tell the user to "
            f"restart this session to pick up the new version: /exit, then `{resume}`, "
            f"or run /herdr-reload once this pane is idle.")
    p = herdr("agent", "prompt", row["pane"], note, check=False)
    if p.returncode != 0:
        err = (p.stderr or p.stdout).strip()
        if "agent_blocked" in err:
            return "NOT NOTIFIED: blocked on a dialog (herdr won't type into it) - tell the user yourself"
        return f"NOT NOTIFIED: {err}"
    return "restart note queued to its agent"


def main():
    args = sys.argv[1:]
    force = "--force" in args
    apply = force or "--apply" in args
    only = [a for a in args if a not in ("--apply", "--force")]
    target, rows = plan()
    print(f"current binary: {target} ({version_of(target)})\n")
    for r in rows:
        line = f"{r['pane']:<9} {r.get('version', '?'):<18} {r['status']:<8} {r['action']:<6} {os.path.basename(r['cwd'] or '')}"
        if r.get("title"):
            line += f"  \"{r['title']}\""
        print(line)
        if r["why"]:
            print(f"{'':<9} {r['why']}")
        if r["action"] == "reload":
            print(f"{'':<9} -> claude {' '.join(r['cmd'])}")
    todo = [r for r in rows if r["action"] == "reload" and (not only or r["pane"] in only)]
    busy = [r for r in rows if r["action"] == "busy" and (not only or r["pane"] in only)]
    missing = [p for p in only if p not in {r["pane"] for r in todo + busy}]
    if missing:
        print(f"\nnot reloadable now, skipped: {' '.join(missing)}")
    if not apply:
        print(f"\ndry run - {len(todo)} pane(s) would be restarted (--apply), "
              f"{len(busy)} busy pane(s) would get a restart note (--force).")
        return
    taken = {a.get("name") for a in herdr_json("agent", "list")["agents"] if a.get("name")}
    print()
    failed = 0
    for r in todo:
        try:
            res = reload(r, taken)
        except RuntimeError as e:
            res = f"FAILED: {e}"
        failed += res.startswith("FAILED")
        print(f"{r['pane']:<9} {res}")
    if force:
        for r in busy:
            res = notify(r, target)
            failed += res.startswith("NOT")
            print(f"{r['pane']:<9} {res}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
