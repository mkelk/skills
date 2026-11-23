#!/usr/bin/env python3
"""Tests for guard-hook.py. Run: python3 test_guard_hook.py"""
import importlib.util
import os
import unittest

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("guard_hook", os.path.join(here, "guard-hook.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

HOME = "/home/u"
PATS = g.patterns(["~/repo-kept/research/*/ruler", "~/repo-kept/research/canary.txt", "/srv/keys/*/ruler"], HOME)


class Guard(unittest.TestCase):
    def hit(self, tool_input):
        return g.refused(tool_input, PATS)

    def test_shell_read_with_tilde(self):
        self.assertTrue(self.hit({"command": "cat ~/repo-kept/research/triage/ruler/key.jsonl"}))

    def test_shell_read_in_full_and_with_home_variable(self):
        self.assertTrue(self.hit({"command": "head " + HOME + "/repo-kept/research/canary.txt"}))
        self.assertTrue(self.hit({"command": 'wc -l "$HOME/repo-kept/research/x/ruler/a"'}))
        self.assertTrue(self.hit({"command": "ls ${HOME}/repo-kept/research/x/ruler"}))

    def test_file_tools_and_nested_input(self):
        self.assertTrue(self.hit({"file_path": HOME + "/repo-kept/research/a/ruler/k"}))
        self.assertTrue(self.hit({"edits": [{"path": "~/repo-kept/research/a/ruler"}]}))

    def test_absolute_path_outside_home(self):
        self.assertTrue(self.hit({"pattern": "x", "path": "/srv/keys/p1/ruler"}))

    def test_what_the_lead_may_read(self):
        self.assertIsNone(self.hit({"command": "cat ~/repo-kept/research/triage/data/tune.jsonl"}))
        self.assertIsNone(self.hit({"file_path": HOME + "/repo/docs/research/triage/ruler/hashes.txt"}))
        self.assertIsNone(self.hit({"command": "git status"}))
        self.assertIsNone(self.hit(None))

    def test_star_is_one_folder(self):
        self.assertIsNone(self.hit({"command": "ls ~/repo-kept/research/a/b/ruler"}))


if __name__ == "__main__":
    unittest.main()
