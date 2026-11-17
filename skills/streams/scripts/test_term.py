"""Tests for term.py: fake `hc`, `herdr` and `herdr-app` executables in a temp dir, alone on PATH.

Each fake logs its argv (one JSON line per call) and answers from an environment variable, so a test
sets what each server shows and then reads which fake was called with what.

    cd skills/streams/scripts && python3 -m unittest test_term
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TERM = os.path.join(HERE, "term.py")

FAKE = """#!{python}
import json, os, sys
name = os.path.basename(sys.argv[0])
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps([name] + sys.argv[1:]) + "\\n")
key = "FAKE_" + name.upper().replace("-", "_") + "_" + "_".join(a.upper().replace("-", "_").replace(".", "_")
                                                             for a in sys.argv[1:2])
out = os.environ.get(key, os.environ.get("FAKE_" + name.upper().replace("-", "_") + "_DEFAULT", "{{}}"))
fail = os.environ.get(key + "_EXIT")
print(out)
sys.exit(int(fail) if fail else 0)
"""

HC_LIVE = {"terminals": [
    {"address": "t3", "agent": "claude", "cwd": "/w/repo-a", "state": "live", "labels": {"stream": "a"},
     "status": {"state": "idle"}, "foreground": {"cwd": "/w/repo-a/sub"}},
    {"address": "t1", "agent": "bash", "cwd": "/w", "state": "finished"},
]}
HC_EMPTY = {"hidden_finished": 1, "terminals": []}
HERDR_SNAP = {"result": {"snapshot": {
    "workspaces": [{"workspace_id": "w6", "label": "b"}],
    "panes": [{"pane_id": "w6:p1", "workspace_id": "w6", "cwd": "/w/repo-b", "agent": "claude",
               "agent_status": "done", "agent_session": {"value": "uuid-1"}, "foreground_cwd": "/w/repo-b/x"},
              {"pane_id": "w6:p2", "workspace_id": "w6", "cwd": "/w/repo-c", "agent": "claude",
               "agent_status": "blocked", "terminal_title_stripped": "stream c"}],
    "agents": []}}}
HERDR_EMPTY = {"result": {"snapshot": {"workspaces": [], "panes": [], "agents": []}}}


class TermTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bin = os.path.join(self.tmp.name, "bin")
        self.home = os.path.join(self.tmp.name, "home")
        os.makedirs(self.bin)
        os.makedirs(self.home)
        self.log = os.path.join(self.tmp.name, "calls.log")
        self.env = {"PATH": self.bin, "HOME": self.home, "FAKE_LOG": self.log}

    def tearDown(self):
        self.tmp.cleanup()

    def fake(self, name, **answers):
        path = os.path.join(self.bin, name)
        with open(path, "w") as f:
            f.write(FAKE.format(python=sys.executable))
        os.chmod(path, 0o755)
        for key, value in answers.items():
            self.env[f"FAKE_{name.upper().replace('-', '_')}_{key}"] = value if isinstance(value, str) else json.dumps(value)

    def hc(self, ls=HC_LIVE, **answers):
        self.fake("hc", LS=ls, **answers)

    def herdr(self, snapshot=HERDR_SNAP, running=True, **answers):
        self.fake("herdr", API=snapshot, **answers)
        if running:
            os.makedirs(os.path.join(self.home, ".config", "herdr"), exist_ok=True)
            open(os.path.join(self.home, ".config", "herdr", "herdr.sock"), "w").close()

    def term(self, *args):
        r = subprocess.run([sys.executable, TERM, *args], capture_output=True, text=True, env=self.env)
        return r.returncode, r.stdout, r.stderr

    def answer(self, *args):
        code, out, err = self.term("--json", *args)  # before any `--`
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def calls(self, name=None):
        if not os.path.exists(self.log):
            return []
        with open(self.log) as f:
            rows = [json.loads(line) for line in f]
        return [r for r in rows if name is None or r[0] == name]

    # --------------------------------------------------------------------- which server answers

    def test_hc_with_terminals_is_hc(self):
        self.hc()
        self.herdr()
        self.assertEqual(self.answer("which")["server"], "hc")
        ls = self.answer("ls")
        self.assertEqual(ls["server"], "hc")
        # mid-move: hc's sessions first, then herdr's, each tagged
        self.assertEqual([(s["server"], s["id"]) for s in ls["sessions"]],
                         [("hc", "t3"), ("herdr", "w6:p1"), ("herdr", "w6:p2")])
        self.assertEqual(ls["sessions"][0]["label"], "a")
        self.assertEqual(ls["sessions"][0]["state"], "idle")
        self.assertEqual(ls["sessions"][0]["foreground_cwd"], "/w/repo-a/sub")

    def test_hc_empty_and_herdr_with_panes_is_herdr(self):
        self.hc(ls=HC_EMPTY)
        self.herdr()
        self.assertEqual(self.answer("which")["server"], "herdr")
        ls = self.answer("ls")
        self.assertEqual(ls["server"], "herdr")
        by_id = {s["id"]: s for s in ls["sessions"]}
        self.assertEqual(by_id["w6:p1"]["state"], "idle")  # done reads idle
        self.assertEqual(by_id["w6:p1"]["session"], "uuid-1")
        self.assertEqual(by_id["w6:p1"]["label"], "b")
        self.assertEqual(by_id["w6:p1"]["foreground_cwd"], "/w/repo-b/x")
        self.assertEqual(by_id["w6:p2"]["label"], "stream c")  # the pane's title wins over the workspace's label
        self.assertEqual(by_id["w6:p2"]["state"], "blocked")  # blocked is never idle, nor unknown
        self.assertEqual(by_id["w6:p2"]["status"], "blocked")
        self.assertEqual(by_id["w6:p2"]["foreground_cwd"], "")
        self.assertIsNone(by_id["w6:p2"]["session"])

    def test_hc_empty_and_herdr_empty_is_hc(self):
        self.hc(ls=HC_EMPTY)
        self.herdr(snapshot=HERDR_EMPTY)
        self.assertEqual(self.answer("which")["server"], "hc")

    def test_only_herdr_is_herdr(self):
        self.herdr()
        self.assertEqual(self.answer("which")["server"], "herdr")
        self.assertEqual(self.answer("ls")["server"], "herdr")

    def test_only_herdr_with_no_panes_is_herdr(self):
        self.herdr(snapshot=HERDR_EMPTY)
        self.assertEqual(self.answer("which")["server"], "herdr")

    def test_hc_failing_is_not_an_answer(self):
        self.hc(LS_EXIT="1")
        self.herdr()
        self.assertEqual(self.answer("which")["server"], "herdr")

    def test_herdr_without_socket_does_not_answer(self):
        self.herdr(running=False)
        code, out, err = self.term("ls", "--json")
        self.assertEqual(code, 2)
        self.assertEqual(self.calls("herdr"), [])  # never asked: the call would hang

    def test_neither_is_exit_2_with_one_line(self):
        code, out, err = self.term("ls")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertIn("no terminal server answers", err)

    def test_server_flag_forces(self):
        self.hc()
        self.herdr()
        ls = self.answer("ls", "--server", "herdr")
        self.assertEqual(ls["server"], "herdr")
        self.assertEqual({s["server"] for s in ls["sessions"]}, {"herdr"})
        self.assertEqual(self.answer("--server", "hc", "which")["server"], "hc")
        self.assertEqual(self.answer("which", "--server=hc")["server"], "hc")

    def test_forced_server_absent_is_exit_2(self):
        self.herdr()
        code, _, err = self.term("which", "--server", "hc")
        self.assertEqual(code, 2)
        self.assertIn("hc does not answer", err)

    # --------------------------------------------------------------------- read / send / wait / start

    def test_read_on_hc(self):
        self.hc(READ={"text": "hello\n", "complete": True, "how": "screen"})
        r = self.answer("read", "t3", "--lines", "40")
        self.assertEqual((r["server"], r["text"]), ("hc", "hello\n"))
        self.assertIn(["hc", "read", "t3", "--lines", "40", "--json"], self.calls("hc"))

    def test_read_on_herdr(self):
        self.hc(ls=HC_EMPTY)
        self.herdr(PANE="screen text")
        r = self.answer("read", "w6:p1")
        self.assertEqual(r["server"], "herdr")
        self.assertIn(["herdr", "pane", "read", "w6:p1", "--lines", "15", "--format", "text"], self.calls("herdr"))

    def test_read_finds_the_session_on_the_other_server(self):
        self.hc()  # hc has t3, so hc is chosen, but the pane is on herdr
        self.herdr(PANE="x")
        self.assertEqual(self.answer("read", "w6:p2")["server"], "herdr")
        self.assertEqual([c for c in self.calls("hc") if c[1] == "read"], [])

    def test_send_on_hc(self):
        self.hc(SEND={"turn": 4, "started": True})
        r = self.answer("send", "t3", "/compact now")
        self.assertEqual(r["server"], "hc")
        self.assertIn(["hc", "send", "t3", "/compact now", "--json"], self.calls("hc"))

    def test_send_on_herdr(self):
        self.herdr(AGENT="{}")
        r = self.answer("send", "w6:p1", "/compact now")
        self.assertEqual(r["server"], "herdr")
        self.assertIn(["herdr", "agent", "prompt", "w6:p1", "/compact now"], self.calls("herdr"))

    def test_send_failure_is_exit_1(self):
        self.herdr(AGENT_EXIT="3")
        code, _, err = self.term("send", "w6:p1", "hi")
        self.assertEqual(code, 1)
        self.assertIn("herdr agent prompt failed", err)

    def test_wait_on_hc(self):
        self.hc(WAIT={"terminal": "t3", "ended": True, "reason": "status", "turn": 5, "children": []})
        r = self.answer("wait", "t3", "--timeout", "60")
        self.assertTrue(r["ended"])
        self.assertIn(["hc", "wait", "t3", "--json", "--timeout", "60"], self.calls("hc"))

    def test_wait_timeout_on_hc_is_exit_1(self):
        self.hc(WAIT={"terminal": "t3", "ended": False, "reason": "timeout", "turn": 5, "children": []})
        code, out, _ = self.term("wait", "t3", "--timeout", "1", "--json")
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)["ended"])

    def test_wait_on_hc_without_ended_is_an_error(self):
        self.hc(WAIT={"terminal": "t3", "reason": "status"})
        code, out, err = self.term("wait", "t3", "--timeout", "1")
        self.assertEqual(code, 2)
        self.assertIn("no `ended`", err)

    def test_wait_failure_on_hc_is_exit_2(self):
        self.hc(WAIT_EXIT="1")
        code, _, err = self.term("wait", "t3")
        self.assertEqual(code, 2)
        self.assertIn("hc wait failed", err)

    def test_wait_timeout_on_herdr_is_exit_1(self):
        self.herdr(AGENT={"error": {"code": "timeout", "message": "timed out waiting for agent status"}},
                   AGENT_EXIT="1")
        code, out, _ = self.term("wait", "w6:p1", "--timeout", "1", "--json")
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)["ended"])

    def test_wait_error_on_herdr_is_exit_2(self):
        self.herdr(AGENT={"error": {"code": "agent_not_found", "message": "agent target w6:p9 not found"}},
                   AGENT_EXIT="1")
        code, out, err = self.term("wait", "w6:p9", "--timeout", "1")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("herdr agent wait failed", err)

    def test_wait_on_herdr(self):
        self.herdr(AGENT="{}")
        r = self.answer("wait", "w6:p1", "--timeout", "2")
        self.assertEqual(r["server"], "herdr")
        self.assertIn(["herdr", "agent", "wait", "w6:p1", "--timeout", "2000"], self.calls("herdr"))

    def test_start_on_hc_without_window(self):
        self.hc(ls=HC_EMPTY, RUN={"address": "t9"})
        r = self.answer("start", "/w/repo-d", "D stream", "--", "claude", "--resume", "abc")
        self.assertEqual((r["server"], r["session"]), ("hc", "t9"))
        run = [c for c in self.calls("hc") if c[1] == "run"][0]
        self.assertEqual(run[run.index("--") + 1:], ["claude", "--resume", "abc"])
        self.assertIn("--bg", run)
        self.assertEqual(run[run.index("--cwd") + 1], "/w/repo-d")
        self.assertEqual(run[run.index("--label") + 1], "stream=D stream")
        self.assertEqual(run[run.index("--name") + 1], "d-stream")

    def test_start_on_hc_in_the_window(self):
        self.hc(ls=HC_EMPTY, LABEL="{}")
        self.fake("herdr-app", DO={"space": "s2", "terminal": "t8"})
        r = self.answer("start", "/w/repo-d", "d", "--", "claude")
        self.assertEqual(r["session"], "t8")
        app = self.calls("herdr-app")[0]
        self.assertEqual(app[1:3], ["do", "space.new"])
        self.assertEqual(json.loads(app[app.index("--argv") + 1]), ["claude"])
        self.assertIn(["hc", "label", "t8", "stream=d"], self.calls("hc"))
        self.assertEqual([c for c in self.calls("hc") if c[1] == "run"], [])

    def test_start_in_the_window_naming_no_terminal_starts_nothing_more(self):
        self.hc(ls=HC_EMPTY, RUN={"address": "t9"})
        self.fake("herdr-app", DO={"space": "s2"})
        code, _, err = self.term("start", "/w/repo-d", "d", "--", "claude")
        self.assertEqual(code, 2)
        self.assertIn("named no terminal", err)
        self.assertEqual([c for c in self.calls("hc") if c[1] in ("run", "label")], [])

    def test_start_falls_back_to_hc_run_when_the_window_fails(self):
        self.hc(ls=HC_EMPTY, RUN={"address": "t9"})
        self.fake("herdr-app", DO="no window", DO_EXIT="1")
        r = self.answer("start", "/w/repo-d", "d", "--", "claude")
        self.assertEqual(r["session"], "t9")
        self.assertEqual(len([c for c in self.calls("hc") if c[1] == "run"]), 1)

    def test_start_on_herdr_takes_the_root_pane(self):
        self.herdr(WORKSPACE={"result": {"focused": {"pane_id": "w5:p7"}, "workspace": {"workspace_id": "w5"},
                                         "root_pane": {"pane_id": "w5:p1"}}}, PANE="{}")
        r = self.answer("start", "/w/x", "x", "--", "bash")
        self.assertEqual(r["session"], "w5:p1")

    def test_start_on_herdr_claude(self):
        self.hc(ls=HC_EMPTY)
        self.herdr(WORKTREE={"result": {"workspace": {"workspace_id": "w9"}, "root_pane": {"pane_id": "w9:p1"}}},
                   AGENT="{}")
        r = self.answer("start", "/w/repo-e", "e", "--workspace", "w1", "--", "claude", "--resume", "u")
        self.assertEqual((r["server"], r["session"]), ("herdr", "w9:p1"))
        calls = self.calls("herdr")
        self.assertIn(["herdr", "worktree", "open", "--workspace", "w1", "--path", "/w/repo-e", "--label", "e",
                       "--no-focus"], calls)
        self.assertIn(["herdr", "agent", "start", "e", "--kind", "claude", "--pane", "w9:p1", "--", "--resume", "u"],
                      calls)

    def test_start_on_herdr_other_program(self):
        self.herdr(WORKSPACE={"result": {"pane_id": "w4:p1"}}, PANE="{}")
        r = self.answer("start", "/w/x", "x", "--", "bash", "-l")
        self.assertEqual(r["session"], "w4:p1")
        calls = self.calls("herdr")
        self.assertIn(["herdr", "workspace", "create", "--cwd", "/w/x", "--label", "x", "--no-focus"], calls)
        self.assertIn(["herdr", "pane", "run", "w4:p1", "bash", "-l"], calls)


if __name__ == "__main__":
    unittest.main()
