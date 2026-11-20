#!/usr/bin/env python3
"""Run the public artifact's solver-free verification suite.

Checks the GPW 2026 paper artifact (scripts/verify_quick.py, tests/) and then the
post-GPW certified result as of 2026-11-12 (scripts/verify_post_gpw.py).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    try:
        run(sys.executable, "scripts/verify_quick.py")
        run(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q")
        run(sys.executable, "scripts/verify_post_gpw.py")
    except subprocess.CalledProcessError as error:
        return error.returncode
    print("ALL PUBLIC ARTIFACT CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
