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

MISSING = object()


def render(value: object) -> str:
    """스칼라만 값을 보여준다. 마켓플레이스 객체를 통째로 찍어봐야 안 읽힌다."""
    if isinstance(value, (bool, int, float, str)) or value is None:
        return json.dumps(value, ensure_ascii=False)
    return "..."


def describe(label: str, key: str, previous: object, value: object) -> str:
    """추가와 변경을 구분해서 적는다.

    둘을 같은 기호로 찍으면 플러그인을 내린 것이 켠 것처럼 보인다. 이 스크립트의
    출력이 적용 결과를 확인하는 유일한 자리라 그 구분이 곧 검증이다.
    """
    if previous is MISSING:
        return f"추가  {label}.{key} = {render(value)}"
    return f"변경  {label}.{key}: {render(previous)} -> {render(value)}"


def merge_mapping(target: dict, preset: dict, label: str, changes: list[str]) -> None:
    """프리셋 키를 덮어쓴다. 대상에만 있는 키는 남긴다."""
    for key, value in preset.items():
        previous = target.get(key, MISSING)
        if previous != value:
            changes.append(describe(label, key, previous, value))
        target[key] = copy.deepcopy(value)


def merge_plugins(
    target: dict, preset: dict, installed: set[str] | None, changes: list[str]
) -> None:
    """`false` 는 설치된 플러그인에만 적는다.

    `false` 가 하는 일은 이미 켜져 있는 것을 끄는 것 하나뿐이다. 설치되지 않은
    플러그인에는 끌 것이 없고, 대신 세션마다 **로드 에러가 난다.** 클로드가 그
    항목을 "프로젝트 설정이 켰는데 설치가 안 됐다"로 읽기 때문이다. 이미 적혀
    있으면 지운다.

    설치 목록을 못 받았으면 (`--installed` 없이 돌렸으면) 전부 그대로 적는다.
    """
    for key, value in preset.items():
        if value is False and installed is not None and key not in installed:
            if key in target:
                del target[key]
                changes.append(f"제거  enabledPlugins.{key} (설치되지 않음)")
            continue
        previous = target.get(key, MISSING)
        if previous != value:
            changes.append(describe("enabledPlugins", key, previous, value))
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
            changes.append(f"추가  env.{key} = \"\" (값은 직접 채운다)")
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
                changes.append(f"추가  hooks.{event}[{matcher}]")
                continue

            hooks = entry.setdefault("hooks", [])
            for preset_hook in preset_entry.get("hooks", []):
                command = preset_hook.get("command")
                for index, hook in enumerate(hooks):
                    if hook.get("command") == command:
                        if hook != preset_hook:
                            hooks[index] = copy.deepcopy(preset_hook)
                            changes.append(f"변경  hooks.{event}[{matcher}] {command}")
                        break
                else:
                    hooks.append(copy.deepcopy(preset_hook))
                    changes.append(f"추가  hooks.{event}[{matcher}] {command}")


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
    parser.add_argument(
        "--installed",
        type=Path,
        help="설치된 플러그인 id 목록 파일. 한 줄에 하나. "
        "주면 미설치 플러그인의 false 항목을 적지 않는다",
    )
    args = parser.parse_args()

    preset = json.loads(args.preset.read_text(encoding="utf-8"))

    installed: set[str] | None = None
    if args.installed:
        installed = {
            line.strip()
            for line in args.installed.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

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
            if key not in preset:
                continue
            if key == "enabledPlugins":
                merge_plugins(
                    target.setdefault(key, {}), preset[key], installed, changes
                )
            else:
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
        print(f"  {change}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
