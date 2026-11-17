"""Tests for scripts/leak-check and hooks/pre-push.

Run from the repo root:  python3 -m unittest discover -s scripts -p 'test_*.py'
Every repo here is a temporary one, and the deny-list is a temporary file of made-up words.
"""

import os
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "leak-check")
HOOK = os.path.join(os.path.dirname(HERE), "hooks", "pre-push")

DENIED = "zorbleflux"          # made up; the temporary deny-list's only word
DENY_TEXT = "# test deny-list\n\\bzorble[a-z]*\\b\nquux-?vandal\n"


def run(args, cwd, env=None, check=True):
    p = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise AssertionError(f"{args} failed: {p.stdout}{p.stderr}")
    return p


class LeakCheckCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="leak-check-test-")
        self.deny = os.path.join(self.tmp, "deny.txt")
        with open(self.deny, "w") as f:
            f.write(DENY_TEXT)
        self.env = dict(os.environ, SKILLS_LEAK_DENY=self.deny,
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="Test Author", GIT_AUTHOR_EMAIL="author@example.com",
                        GIT_COMMITTER_NAME="Test Author", GIT_COMMITTER_EMAIL="author@example.com")
        self.repo = self.new_repo("work")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def new_repo(self, name):
        path = os.path.join(self.tmp, name)
        os.makedirs(path)
        self.git(path, "init", "-q", "-b", "master")
        os.makedirs(os.path.join(path, "scripts"))
        shutil.copy(CHECK, os.path.join(path, "scripts", "leak-check"))
        os.makedirs(os.path.join(path, "hooks"))
        shutil.copy(HOOK, os.path.join(path, "hooks", "pre-push"))
        self.write(path, "README.md", "a clean line\n")
        self.git(path, "add", "-A")
        self.git(path, "commit", "-q", "-m", "start")
        return path

    def git(self, repo, *args, env=None):
        return run(["git", *args], repo, env or self.env).stdout.strip()

    def write(self, repo, name, text):
        with open(os.path.join(repo, name), "w") as f:
            f.write(text)

    def commit(self, name, text, message="change", env=None):
        self.write(self.repo, name, text)
        self.git(self.repo, "add", "-A")
        self.git(self.repo, "commit", "-q", "-m", message, env=env)
        return self.git(self.repo, "rev-parse", "HEAD")

    def check(self, *args, env=None):
        return run(["python3", CHECK, *args], self.repo, env or self.env, check=False)

    # fails closed

    def test_missing_deny_list_is_an_error(self):
        env = dict(self.env, SKILLS_LEAK_DENY=os.path.join(self.tmp, "absent.txt"))
        p = self.check(env=env)
        self.assertEqual(p.returncode, 2)
        self.assertIn("fails closed", p.stderr)

    def test_empty_deny_list_is_an_error(self):
        with open(self.deny, "w") as f:
            f.write("# only a comment\n\n")
        p = self.check()
        self.assertEqual(p.returncode, 2)
        self.assertIn("no pattern", p.stderr)

    # tree mode

    def test_tree_clean(self):
        p = self.check()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_tree_finds_denied_word_case_insensitively(self):
        self.commit("notes.md", "one\nwe met ZorbleFlux today\n")
        p = self.check()
        self.assertEqual(p.returncode, 1)
        self.assertIn("notes.md:2: deny-list line 2", p.stdout)
        self.assertNotIn("ZorbleFlux", p.stdout)

    def test_tree_generic_shapes_without_echoing_the_value(self):
        key = "sk-" + "ant-" + "a1B2c3D4e5F6g7H8i9J0"
        home = "/ho" + "me/someone/project"
        mail = "someone" + "@" + "corp-mail.dk"
        ip = ".".join(["10", "1", "2", "3"])
        self.commit("cfg.txt", f"key={key}\nmail: {mail}\nhost {ip}\n{home}\n"
                               "fine: user@example.com 127.0.0.1 noreply@github.com\n")
        p = self.check()
        self.assertEqual(p.returncode, 1)
        self.assertIn("cfg.txt:1: anthropic-key", p.stdout)
        self.assertIn("cfg.txt:2: email", p.stdout)
        self.assertIn("cfg.txt:3: ipv4", p.stdout)
        self.assertIn("cfg.txt:4: home-path", p.stdout)
        self.assertNotIn("cfg.txt:5", p.stdout)
        self.assertNotIn(key, p.stdout)

    def test_allow_entry_is_exact(self):
        self.commit("notes.md", f"{DENIED} is public here\n")
        entry = run(["python3", CHECK, "--entry", "notes.md:1"], self.repo, self.env).stdout.strip()
        self.write(self.repo, "scripts/leak-allow.txt", entry + "\n")
        self.git(self.repo, "add", "-A")
        self.git(self.repo, "commit", "-q", "-m", "allow")
        self.assertEqual(self.check().returncode, 0)
        self.commit("notes.md", f"{DENIED} is public here, and more\n")
        self.assertEqual(self.check().returncode, 1)

    # range mode

    def test_range_reads_added_lines_only(self):
        base = self.commit("notes.md", f"old {DENIED} line\nkeep\n")
        head = self.commit("notes.md", "keep\nnew clean line\n")
        p = self.check("--range", f"{base}..{head}")
        self.assertEqual(p.returncode, 0, p.stdout)
        head2 = self.commit("notes.md", f"keep\nnew clean line\nquuxvandal here\n")
        p = self.check("--range", f"{head}..{head2}")
        self.assertEqual(p.returncode, 1)
        self.assertIn("notes.md:3: deny-list line 3", p.stdout)

    # history mode

    def test_history_finds_commit_message(self):
        self.commit("a.md", "clean\n", message=f"about {DENIED}")
        p = self.check("--history")
        self.assertEqual(p.returncode, 1)
        self.assertIn("message:1: deny-list line 2", p.stdout)

    def test_history_finds_author_email(self):
        env = dict(self.env, GIT_AUTHOR_EMAIL=f"me@{DENIED}.example.com")
        self.commit("a.md", "clean\n", env=env)
        p = self.check("--history")
        self.assertEqual(p.returncode, 1)
        self.assertIn("author e-mail: deny-list line 2", p.stdout)

    def test_history_reaches_every_ref(self):
        self.git(self.repo, "checkout", "-q", "-b", "side")
        self.commit("side.md", f"{DENIED}\n")
        self.git(self.repo, "checkout", "-q", "master")
        p = self.check("--history")
        self.assertEqual(p.returncode, 1)
        self.assertIn("side.md:1", p.stdout)

    # the hook

    def push(self, branch):
        return run(["git", "push", "-q", "origin", branch], self.repo, self.env, check=False)

    def test_hook_refuses_a_leak_and_allows_a_clean_push(self):
        remote = os.path.join(self.tmp, "remote.git")
        run(["git", "init", "-q", "--bare", remote], self.tmp, self.env)
        self.git(self.repo, "remote", "add", "origin", remote)
        self.git(self.repo, "config", "core.hooksPath", "hooks")
        p = self.push("master")                    # new branch on the remote, clean
        self.assertEqual(p.returncode, 0, p.stderr)
        self.commit("b.md", "still clean\n")
        self.assertEqual(self.push("master").returncode, 0)
        self.commit("c.md", f"a {DENIED} slipped in\n")
        p = self.push("master")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused", p.stderr)
        self.git(self.repo, "checkout", "-q", "-b", "fresh")   # new branch carrying the leak
        self.assertNotEqual(self.push("fresh").returncode, 0)
        self.assertEqual(run(["git", "branch", "--list", "fresh"], remote, self.env).stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
