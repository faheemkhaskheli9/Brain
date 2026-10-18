"""Run every ```python block in the topic files, each in its own process.

AGENTS.md requires topic code to run; this checks it. Stdlib only (the blocks need numpy).
A block whose first line says "not run here" (a sketch needing a heavy library) is skipped.
Run: python run_code_blocks.py [topic.md ...]   (no arguments: every topic)
Blocks run from the repo root. Exits 1 if any block fails or runs over 60 s.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
FOLDERS = ("anatomy", "function", "learning", "simulation", "guides")


def topic_files(args):
    if args:
        return [Path(a).resolve() for a in args]
    return [p for folder in FOLDERS for p in sorted((ROOT / folder).glob("*.md"))]


def label(path):
    try:
        return path.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main(args=()):
    failed = total = 0
    for path in topic_files(args):
        text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        for n, code in enumerate(re.findall(r"^```python\n(.*?)^```", text, re.S | re.M), 1):
            name = f"{label(path)} block {n}"
            if "not run here" in code.split("\n", 1)[0]:
                print(f"skip {name} (marked not run here)")
                continue
            total += 1
            try:
                r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                                   timeout=60, cwd=ROOT)
                err = r.stderr.strip().splitlines()[-1:] if r.returncode else None
            except subprocess.TimeoutExpired:
                err = ["timed out after 60 s"]
            if err is not None:
                failed += 1
                print(f"FAIL {name}: {err[0] if err else 'exit ' + str(r.returncode)}")
            else:
                print(f"ok   {name}")
    print(f"{total - failed} of {total} blocks ran")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
