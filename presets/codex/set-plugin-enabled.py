#!/usr/bin/env python3
"""Set one or more local-marketplace plugin defaults in Codex config.toml."""

from __future__ import annotations

import argparse
import fcntl
import os
from pathlib import Path
import re
import stat
import tempfile
import tomllib


TABLE_RE = re.compile(r"^\s*\[")
ENABLED_RE = re.compile(r"^(\s*)enabled\s*=.*$")


def set_enabled(text: str, selector: str, enabled: bool) -> str:
    if '"' in selector or "\n" in selector:
        raise ValueError(f"invalid plugin selector: {selector!r}")

    header = f'[plugins."{selector}"]'
    value = "true" if enabled else "false"
    lines = text.splitlines(keepends=True)

    for start, line in enumerate(lines):
        if line.strip() != header:
            continue

        end = start + 1
        while end < len(lines) and not TABLE_RE.match(lines[end]):
            match = ENABLED_RE.match(lines[end].rstrip("\n"))
            if match:
                newline = "\n" if lines[end].endswith("\n") else ""
                lines[end] = f"{match.group(1)}enabled = {value}{newline}"
                return "".join(lines)
            end += 1

        lines.insert(start + 1, f"enabled = {value}\n")
        return "".join(lines)

    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    if lines and lines[-1].strip():
        lines.append("\n")
    lines.extend([f"{header}\n", f"enabled = {value}\n"])
    return "".join(lines)


def write_atomically(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    os.chmod(temporary, mode)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("state", choices=("true", "false"))
    parser.add_argument("selectors", nargs="+")
    args = parser.parse_args()

    args.config.parent.mkdir(parents=True, exist_ok=True)
    lock_path = args.config.with_name(f"{args.config.name}.lock")
    with lock_path.open("a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        text = args.config.read_text(encoding="utf-8") if args.config.exists() else ""
        enabled = args.state == "true"
        for selector in args.selectors:
            text = set_enabled(text, selector, enabled)

        tomllib.loads(text)
        write_atomically(args.config, text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
