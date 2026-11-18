"""Tests for herdr-reload.py with every outside call faked: no hc, no herdr, no machine is touched.

The fake answers `run()` from a table of terminals, so the remote path (`hc exec --on <machine>`)
is exercised without a remote machine.

    cd skills/herdr-reload/scripts && python3 -m unittest test_herdr_reload
"""
import base64
import importlib.util
import json
import os
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hr", os.path.join(HERE, "herdr-reload.py"))
hr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hr)

S1, S2, S3 = ("11111111-1111-4111-8111-111111111111", "22222222-2222-4222-8222-222222222222",
              "33333333-3333-4333-8333-333333333333")
OLD, NEW = "/m/claude/2.1.325/claude", "/m/claude/2.1.326/claude"


def term(addr, status="idle", turn=3, root="/usr/bin/bash", fg="claude", pid=100, session=None, cwd="/w/a"):
    return {"ls": {"address": addr, "agent": "claude-code", "cwd": cwd, "state": "live", "status": status,
                   "turn": turn, "where": f"{addr} / 1"},
            "get": {"address": addr, "argv": [root], "labels": {"session": session} if session else {},
                    "foreground": {"name": fg, "pid": pid, "argv": [NEW if fg == "claude" else fg]}}}


class Fake:
    """Answers run(): `hc ls/get/send/exec`, and the host programs behind `hc exec --on` or run directly."""

    def __init__(self, terms, procs, target=NEW):
        self.terms = {t["ls"]["address"]: t for t in terms}
        self.procs = procs  # (machine, pid) -> {exe, cmdline, fds, cwd}
        self.target = target
        self.calls = []

    def host(self, machine, argv):
        if argv[:2] == ["mise", "which"]:
            return 0, self.target
        if argv[0] == "readlink" and argv[1] == "-f":
            return 0, argv[2]
        pid = int(argv[-1].split("/")[2]) if argv[-1].startswith("/proc/") else None
        p = self.procs.get((machine, pid), {})
        if argv[0] == "readlink":
            what = argv[1].rsplit("/", 1)[1]
            return (0, p[what]) if what in p else (1, "")
        if argv[0] == "cat":
            what = argv[1].rsplit("/", 1)[1]
            return (0, p.get(what, "")) if what == "cmdline" or what in p else (1, "")
        if argv[0] == "ls":
            return 0, "".join(f"lrwx------ 1 u u 64 x {i} -> {f}\n" for i, f in enumerate(p.get("fds", [])))
        return 1, ""

    def __call__(self, argv, timeout=60, plain=False):
        self.calls.append((list(argv), plain))
        if argv[0] != "hc":
            return (*self.host(None, argv)[:1], self.host(None, argv)[1].encode(), b"")
        if argv[1] == "ls":
            return 0, json.dumps({"terminals": [t["ls"] for t in self.terms.values()]}).encode(), b""
        if argv[1] == "get":
            t = self.terms.get(argv[2])
            return (0, json.dumps(t["get"]).encode(), b"") if t else (3, b"", b"no terminal")
        if argv[1] == "exec":
            machine = argv[argv.index("--on") + 1]
            rc, out = self.host(machine, argv[argv.index("--") + 1:])
            body = {"code": rc, "stdout": base64.b64encode(out.encode()).decode()}
            return 0, json.dumps(body).encode(), b""
        if argv[1] == "send":
            t = self.terms[argv[2]]
            if argv[3] == "/exit":
                t["get"]["foreground"] = {"name": "bash", "pid": 1}
            elif argv[3].startswith("claude "):
                t["get"]["foreground"] = {"name": "claude", "pid": 777, "argv": [NEW]}
                self.procs[(argv[2].rpartition("/")[0] or None, 777)] = {"exe": NEW}
            return 0, b"{}", b""
        return 1, b"", b"unknown"


def proc(exe=OLD, argv=None, fds=(), **kw):
    return {"exe": exe, "cmdline": "\0".join(argv or [exe]) + "\0", "fds": list(fds), **kw}


def tasks(sid):
    return f"/tmp/claude-1000/-w-a/{sid}/tasks"


class Helpers(unittest.TestCase):
    def test_new_args_drops_old_resume_and_session_id(self):
        self.assertEqual(hr.new_args(["claude", "--model", "x", "--resume", S1, "-c"], S2),
                         ["--model", "x", "--resume", S2])
        self.assertEqual(hr.new_args(["claude", f"--session-id={S1}"], S2), ["--resume", S2])

    def test_resume_id(self):
        self.assertEqual(hr.resume_id(["claude", "--resume", S1]), S1)
        self.assertEqual(hr.resume_id(["claude", f"--resume={S1}"]), S1)
        self.assertIsNone(hr.resume_id(["claude", "--resume", "not-an-id"]))


class Plan(unittest.TestCase):
    def plan(self, fake, local=False):
        hr.run = fake
        os.environ["HC_TERMINAL_ID"] = "t6"
        return {r["id"]: r for r in hr.plan(hr.Hc(local))}

    def test_every_action(self):
        fake = Fake(
            [term("t2", pid=2), term("t3", pid=3), term("t4", pid=4), term("t5", status="working", pid=5),
             term("t6", pid=6), term("t7", pid=7, root="claude"), term("t8", pid=8, turn=0)],
            {(None, 2): proc(fds=[tasks(S1)]), (None, 3): proc(exe=NEW), (None, 4): proc(),
             (None, 5): proc(fds=[tasks(S2)]), (None, 6): proc(), (None, 7): proc(), (None, 8): proc()})
        rows = self.plan(fake)
        self.assertEqual(rows["t2"]["action"], "reload")
        self.assertEqual(rows["t2"]["cmd"], ["--resume", S1])
        self.assertEqual(rows["t3"]["action"], "ok")
        self.assertEqual(rows["t4"]["action"], "skip")          # idle, no session id, has run turns
        self.assertIn("no session id", rows["t4"]["why"])
        self.assertEqual(rows["t5"]["action"], "busy")
        self.assertEqual(rows["t5"]["session"], S2)
        self.assertEqual(rows["t6"]["action"], "skip")          # this session
        self.assertIn("this session", rows["t6"]["why"])
        self.assertEqual(rows["t7"]["action"], "skip")          # claude is the terminal's own program
        self.assertEqual(rows["t8"]["action"], "skip")          # turn 0: no transcript fallback

    def test_session_from_label_argv_and_transcript(self):
        fake = Fake([term("t2", pid=2, session=S1), term("t3", pid=3), term("t4", pid=4)],
                    {(None, 2): proc(), (None, 3): proc(argv=[OLD, "--resume", S2]), (None, 4): proc()})
        orig = hr.Host.transcript_ids
        hr.Host.transcript_ids = lambda self, pid: {S3} if pid == 4 else set()
        try:
            rows = self.plan(fake)
        finally:
            hr.Host.transcript_ids = orig
        self.assertEqual([rows[k]["session"] for k in ("t2", "t3", "t4")], [S1, S2, S3])

    def test_two_sessions_open_is_ambiguous(self):
        fake = Fake([term("t2", pid=2)], {(None, 2): proc(fds=[tasks(S1), tasks(S2)])})
        self.assertEqual(self.plan(fake)["t2"]["action"], "skip")

    def test_remote_terminal_is_read_on_its_machine(self):
        fake = Fake([term("fw/t5", pid=50), term("fw/t6", pid=60, status="idle")],
                    {("fw", 50): proc(fds=[tasks(S1)]), ("fw", 60): proc(exe=NEW)})
        rows = self.plan(fake)
        self.assertEqual(rows["fw/t5"]["action"], "reload")
        self.assertEqual(rows["fw/t5"]["machine"], "fw")
        self.assertEqual(rows["fw/t6"]["action"], "ok")
        execs = [c for c, _ in fake.calls if c[:2] == ["hc", "exec"]]
        self.assertTrue(execs and all(c[c.index("--on") + 1] == "fw" for c in execs))

    def test_local_flag_never_touches_a_machine(self):
        fake = Fake([term("t2", pid=2), term("fw/t5", pid=50)],
                    {(None, 2): proc(fds=[tasks(S1)]), ("fw", 50): proc()})
        rows = self.plan(fake, local=True)
        self.assertEqual(list(rows), ["t2"])
        self.assertFalse([c for c, _ in fake.calls if "fw/t5" in c or "fw" in c])

    def test_machine_without_a_claude_binary_is_skipped_not_fatal(self):
        fake = Fake([term("fw/t5", pid=50)], {("fw", 50): proc(fds=[tasks(S1)])}, target="")
        fake.host_orig = fake.host
        fake.host = lambda m, a: (1, "") if a[0] in ("mise", "sh") else fake.host_orig(m, a)
        row = self.plan(fake)["fw/t5"]
        self.assertEqual(row["action"], "skip")
        self.assertIn("on fw", row["why"])


class Reload(unittest.TestCase):
    def test_exit_then_resume_typed_into_the_shell_without_the_hc_tag(self):
        fake = Fake([term("fw/t5", pid=50)], {("fw", 50): proc(fds=[tasks(S1)])})
        hr.run = fake
        hr.time.sleep = lambda s: None
        row = [r for r in hr.plan(hr.Hc())][0]
        res = hr.Hc().reload(row, row["host"], set())
        self.assertEqual(res, "restarted on 2.1.326")
        sends = [(c, plain) for c, plain in fake.calls if c[:2] == ["hc", "send"]]
        self.assertEqual([c[3] for c, _ in sends], ["/exit", f"claude --resume {S1}"])
        self.assertTrue(all(plain for _, plain in sends))      # HC_TERMINAL_ID kept off: no <hc from> tag
        self.assertTrue(all(c[2] == "fw/t5" for c, _ in sends))

    def test_blocked_session_is_not_notified(self):
        row = {"id": "t2", "status": "blocked"}
        self.assertTrue(hr.Hc().notify(row, "note").startswith("NOT NOTIFIED"))


if __name__ == "__main__":
    unittest.main()
