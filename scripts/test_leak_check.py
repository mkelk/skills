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
SIZE = os.path.join(HERE, "size-check")

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
        shutil.copy(SIZE, os.path.join(path, "scripts", "size-check"))  # the hook runs it too
        os.makedirs(os.path.join(path, "hooks"))
        shutil.copy(HOOK, os.path.join(path, "hooks", "pre-push"))
        self.write(path, "README.md", "a clean line\n")
        os.makedirs(os.path.join(path, "skills", "streams"))
        self.write(path, "skills/streams/SKILL.md", "a clean line\n")  # something for size-check
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

    def test_tree_reads_names_binaries_and_symlinks_without_echoing(self):
        self.commit(f"docs-{DENIED}.md", "hi\n")
        with open(os.path.join(self.repo, "blob.bin"), "wb") as f:
            f.write(b"\x89PNG\0\0" + DENIED.encode() + b"\0\x01\x02")
        with open(os.path.join(self.repo, "wide.bin"), "wb") as f:
            f.write(b"\0\0" + "quuxvandal".encode("utf-16-le"))
        os.symlink(f"/x/{DENIED}", os.path.join(self.repo, "lnk"))
        self.git(self.repo, "add", "-A")
        self.git(self.repo, "commit", "-q", "-m", "shapes")
        p = self.check()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("file name: deny-list line 2", p.stdout)
        self.assertIn("blob.bin: binary content: deny-list line 2", p.stdout)
        self.assertIn("wide.bin: binary content: deny-list line 3", p.stdout)
        self.assertIn("lnk: symlink target: deny-list line 2", p.stdout)
        self.assertNotIn(DENIED, p.stdout + p.stderr)

    def test_file_name_allow_entry_is_exact(self):
        self.commit(f"{DENIED}.md", "hi\n")
        p = self.check()
        entry = p.stdout.split("(allow entry ")[1].split(")")[0]
        self.write(self.repo, "scripts/leak-allow.txt", entry + "\n")
        self.git(self.repo, "add", "-A")
        self.git(self.repo, "commit", "-q", "-m", "allow")
        self.assertEqual(self.check().returncode, 0)
        self.commit(f"{DENIED}-2.md", "hi\n")
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

    def test_history_reads_names_binaries_symlinks_tags_and_refs(self):
        self.commit(f"docs-{DENIED}.md", "hi\n")
        with open(os.path.join(self.repo, "blob.bin"), "wb") as f:
            f.write(b"\0" + DENIED.encode() + b"\0")
        os.symlink(f"/x/{DENIED}", os.path.join(self.repo, "lnk"))
        self.git(self.repo, "add", "-A")
        self.git(self.repo, "commit", "-q", "-m", "shapes")
        self.git(self.repo, "tag", "-a", "v1", "-m", f"tag about {DENIED}")
        env = dict(self.env, GIT_COMMITTER_NAME=f"Q {DENIED}")
        self.git(self.repo, "tag", "-a", "v2", "-m", "clean tag", env=env)
        self.git(self.repo, "branch", f"side-{DENIED}")
        p = self.check("--history")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("file name: deny-list line 2", p.stdout)
        self.assertIn("blob.bin: binary content: deny-list line 2", p.stdout)
        self.assertIn("lnk:1: deny-list line 2", p.stdout)
        self.assertIn("message:1: deny-list line 2", p.stdout)       # the tag's message
        self.assertIn("tagger name: deny-list line 2", p.stdout)
        self.assertIn("ref name: deny-list line 2", p.stdout)
        self.assertNotIn(DENIED, p.stdout + p.stderr)

    def test_range_reads_an_annotated_tag_it_is_given(self):
        self.git(self.repo, "tag", "-a", "v1", "-m", f"about {DENIED}")
        p = self.check("--range", "v1")
        self.assertEqual(p.returncode, 1)
        self.assertIn("message:1: deny-list line 2", p.stdout)

    def test_name_mode(self):
        self.assertEqual(self.check("--name", "refs/heads/fine").returncode, 0)
        p = self.check("--name", f"refs/heads/{DENIED}")
        self.assertEqual(p.returncode, 1)
        self.assertNotIn(DENIED, p.stdout + p.stderr)

    # the hook

    def push(self, *refs):
        return run(["git", "push", "-q", "origin", *refs], self.repo, self.env, check=False)

    def remote(self):
        remote = os.path.join(self.tmp, "remote.git")
        run(["git", "init", "-q", "--bare", remote], self.tmp, self.env)
        self.git(self.repo, "remote", "add", "origin", remote)
        self.git(self.repo, "config", "core.hooksPath", "hooks")
        self.assertEqual(self.push("master").returncode, 0)
        return remote

    def remote_sha(self, remote, ref):
        return run(["git", "rev-parse", "-q", "--verify", ref], remote, self.env, check=False).stdout.strip()

    def test_hook_new_branch_with_and_without_a_leak(self):
        remote = self.remote()
        self.git(self.repo, "checkout", "-q", "-b", "clean")
        self.commit("a.md", "clean\n")
        self.assertEqual(self.push("clean").returncode, 0)
        self.git(self.repo, "checkout", "-q", "-b", "dirty")
        self.commit("b.md", f"{DENIED}\n")
        p = self.push("dirty")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused refs/heads/dirty", p.stderr)
        self.assertNotIn(DENIED, p.stdout + p.stderr)
        self.assertEqual(self.remote_sha(remote, "refs/heads/dirty"), "")

    def test_hook_force_push(self):
        remote = self.remote()
        self.commit("a.md", "clean\n")
        self.assertEqual(self.push("master").returncode, 0)
        self.git(self.repo, "commit", "-q", "--amend", "-m", f"now about {DENIED}")
        self.assertNotEqual(self.push("-f", "master").returncode, 0)
        self.git(self.repo, "commit", "-q", "--amend", "-m", "clean again")
        self.assertEqual(self.push("-f", "master").returncode, 0)
        self.assertEqual(self.remote_sha(remote, "refs/heads/master"), self.git(self.repo, "rev-parse", "HEAD"))

    def test_hook_several_refs_one_leaking(self):
        remote = self.remote()
        self.git(self.repo, "branch", "two")
        self.commit("a.md", "clean\n")
        self.git(self.repo, "checkout", "-q", "two")
        self.commit("b.md", f"{DENIED}\n")
        self.git(self.repo, "checkout", "-q", "master")
        p = self.push("master", "two")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused refs/heads/two", p.stderr)
        self.assertNotIn("refused refs/heads/master", p.stderr)
        self.assertEqual(self.remote_sha(remote, "refs/heads/two"), "")

    def test_hook_lets_a_branch_delete_through(self):
        remote = self.remote()
        self.git(self.repo, "checkout", "-q", "-b", "feat")
        self.commit("a.md", "clean\n")
        self.assertEqual(self.push("feat").returncode, 0)
        self.assertEqual(self.push(":feat").returncode, 0)
        self.assertEqual(self.remote_sha(remote, "refs/heads/feat"), "")

    def test_hook_push_by_sha(self):
        remote = self.remote()
        clean = self.commit("a.md", "clean\n")
        self.assertEqual(self.push(f"{clean}:refs/heads/by-sha").returncode, 0)
        dirty = self.commit("b.md", f"{DENIED}\n")
        self.assertNotEqual(self.push(f"{dirty}:refs/heads/by-sha-2").returncode, 0)
        self.assertEqual(self.remote_sha(remote, "refs/heads/by-sha-2"), "")

    def test_hook_refuses_a_leaking_ref_name_or_tag(self):
        remote = self.remote()
        self.git(self.repo, "branch", f"x-{DENIED}")
        p = self.push(f"x-{DENIED}")
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn(DENIED, p.stdout + p.stderr)
        self.git(self.repo, "tag", "-a", "v1", "-m", f"about {DENIED}")
        self.assertNotEqual(self.push("v1").returncode, 0)
        self.git(self.repo, "tag", "-a", "v2", "-m", "clean")
        self.assertEqual(self.push("v2").returncode, 0)
        self.assertEqual(self.remote_sha(remote, "refs/tags/v1"), "")

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


    def test_hook_refuses_a_skill_over_its_size_budget(self):
        remote = os.path.join(self.tmp, "remote.git")
        run(["git", "init", "-q", "--bare", remote], self.tmp, self.env)
        self.git(self.repo, "remote", "add", "origin", remote)
        self.git(self.repo, "config", "core.hooksPath", "hooks")
        self.commit("skills/streams/SKILL.md", "a clean line\n" * 1400)  # over 16 KB
        p = self.push("master")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("size-check", p.stderr)


if __name__ == "__main__":
    unittest.main()
