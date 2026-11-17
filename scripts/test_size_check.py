"""Tests for scripts/size-check.

Run from the repo root:  python3 -m unittest discover -s scripts -p 'test_*.py'
Every tree here is a temporary one.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "size-check")


class SizeCheck(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="size-check-test-")

    def tearDown(self):
        shutil.rmtree(self.root)

    def put(self, rel, size):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("x" * size)

    def run_check(self, *args):
        return subprocess.run([sys.executable, "-I", CHECK, "--root", self.root, *args],
                              capture_output=True, text=True)

    def test_within_budget_passes(self):
        self.put("skills/streams/SKILL.md", 1000)
        self.put("skills/roadmap/references/new.md", 16 * 1024 - 1)
        p = self.run_check()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("2 files within budget", p.stdout)

    def test_skill_md_at_budget_fails_naming_file(self):
        self.put("skills/roadmap/SKILL.md", 16 * 1024)
        p = self.run_check()
        self.assertEqual(p.returncode, 1)
        self.assertIn("skills/roadmap/SKILL.md: 16384 bytes, budget 16384", p.stdout)

    def test_readme_counts(self):
        self.put("skills/streams/SKILL.md", 100)
        self.put("skills/streams/README.md", 16 * 1024)
        p = self.run_check()
        self.assertEqual(p.returncode, 1)
        self.assertIn("skills/streams/README.md: 16384 bytes, budget 16384", p.stdout)

    def test_status_has_its_own_budget(self):
        self.put("skills/streams/references/status.md", 20 * 1024)
        self.assertEqual(self.run_check().returncode, 0)
        self.put("skills/streams/references/status.md", 24 * 1024)
        self.assertEqual(self.run_check().returncode, 1)

    def test_recipes_count_and_other_skills_do_not(self):
        self.put("skills/streams/references/recipes/heavy.md", 17 * 1024)
        self.put("skills/other/SKILL.md", 40 * 1024)
        self.put("skills/streams/scripts/big.py", 40 * 1024)
        p = self.run_check()
        self.assertEqual(p.returncode, 1)
        self.assertIn("references/recipes/heavy.md", p.stdout)
        self.assertNotIn("other", p.stdout)
        self.assertNotIn("big.py", p.stdout)

    def test_top_lists_largest_first(self):
        self.put("skills/streams/SKILL.md", 300)
        self.put("skills/streams/references/cut.md", 900)
        self.put("skills/roadmap/SKILL.md", 100)
        lines = self.run_check("--top", "2").stdout.splitlines()
        self.assertIn("references/cut.md", lines[0])
        self.assertIn("streams/SKILL.md", lines[1])

    def test_no_files_is_an_error(self):
        self.assertEqual(self.run_check().returncode, 1)


if __name__ == "__main__":
    unittest.main()
