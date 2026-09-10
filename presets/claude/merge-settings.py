#!/usr/bin/env python3
"""Merge the repo preset into a user-scope Claude Code settings.json."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile


MERGED_KEYS = ("extraKnownMarketplaces", "enabledPlugins")


def merge_mapping(target: dict, preset: dict, label: str, changes: list[str]) -> None:
    """프리셋 키를 덮어쓴다. 대상에만 있는 키는 남긴다."""
    for key, value in preset.items():
        if target.get(key) != value:
            changes.append(f"{label}.{key}")
        target[key] = copy.deepcopy(value)


def merge_env(target: dict, preset: dict, changes: list[str]) -> None:
    """빈 값을 가진 프리셋 키는 자리만 만든다.

    `CONTEXT7_API_KEY` 가 레포에 빈 문자열로 들어 있으므로, 그대로 덮어쓰면
    이미 발급해 넣은 키를 지운다.
    """
    for key, value in preset.items():
        if target.get(key):
            continue
        if key not in target:
            changes.append(f"env.{key}")
        target[key] = value


def merge_hooks(target: dict, preset: dict, changes: list[str]) -> None:
    """훅을 `command` 기준으로 합친다. 같은 명령이면 갱신, 없으면 추가한다.

    대상에 이미 있는 다른 훅은 건드리지 않는다.
    """
    for event, preset_entries in preset.items():
        target_entries = target.setdefault(event, [])
        for preset_entry in preset_entries:
            matcher = preset_entry.get("matcher")
            entry = next(
                (e for e in target_entries if e.get("matcher") == matcher), None
            )
            if entry is None:
                target_entries.append(copy.deepcopy(preset_entry))
                changes.append(f"hooks.{event}[{matcher}]")
                continue

            hooks = entry.setdefault("hooks", [])
            for preset_hook in preset_entry.get("hooks", []):
                command = preset_hook.get("command")
                for index, hook in enumerate(hooks):
                    if hook.get("command") == command:
                        if hook != preset_hook:
                            hooks[index] = copy.deepcopy(preset_hook)
                            changes.append(f"hooks.{event}[{matcher}] {command} 갱신")
                        break
                else:
                    hooks.append(copy.deepcopy(preset_hook))
                    changes.append(f"hooks.{event}[{matcher}] {command} 추가")


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
    parser.add_argument("preset", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument(
        "--backup-dir",
        type=Path,
        help="실제로 쓸 때만 대상 파일을 여기에 복사한다",
    )
    args = parser.parse_args()

    preset = json.loads(args.preset.read_text(encoding="utf-8"))

    args.target.parent.mkdir(parents=True, exist_ok=True)
    lock_path = args.target.with_name(f"{args.target.name}.lock")
    with lock_path.open("a", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)

        if args.target.exists():
            raw = args.target.read_text(encoding="utf-8").strip()
            target = json.loads(raw) if raw else {}
        else:
            target = {}

        changes: list[str] = []
        for key in MERGED_KEYS:
            if key in preset:
                merge_mapping(
                    target.setdefault(key, {}), preset[key], key, changes
                )
        if "env" in preset:
            merge_env(target.setdefault("env", {}), preset["env"], changes)
        if "hooks" in preset:
            merge_hooks(target.setdefault("hooks", {}), preset["hooks"], changes)

        if not changes:
            print("설정 변경 없음")
            return 0

        if args.backup_dir and args.target.exists():
            args.backup_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup = args.backup_dir / f"{args.target.name}.{stamp}"
            backup.write_bytes(args.target.read_bytes())
            print(f"  백업: {backup}")

        write_atomically(
            args.target, json.dumps(target, indent=2, ensure_ascii=False) + "\n"
        )

    for change in changes:
        print(f"  + {change}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
