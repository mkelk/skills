"""Run every diagrams/*.py module (except svgkit and this file) to rebuild the SVGs."""
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
skip = {"svgkit.py", "build.py"}
for name in sorted(os.listdir(here)):
    if name.endswith(".py") and name not in skip and not name.startswith("_"):
        print("build", name)
        subprocess.run([sys.executable, os.path.join(here, name)], check=True)
