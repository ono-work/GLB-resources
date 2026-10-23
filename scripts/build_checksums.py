#!/usr/bin/env python3
"""Rebuild CHECKSUMS.sha256 for the distributable artifact."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "CHECKSUMS.sha256"
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", "generated"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    rows = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path == OUTPUT:
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        rows.append((relative.as_posix(), digest(path)))
    OUTPUT.write_text(
        "".join(f"{value}  {relative}\n" for relative, value in sorted(rows)),
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {OUTPUT.name}: {len(rows)} files")


if __name__ == "__main__":
    main()
