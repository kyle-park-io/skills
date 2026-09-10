#!/usr/bin/env python3
"""Serena 가 세션마다 여는 창을 끈다.

왜 별도 스크립트인가
    `~/.serena/serena_config.yml` 은 Claude 설정이 아니라 Serena 자신의 설정이라
    `settings.json` 병합으로 닿지 않는다. 그런데 새 머신에서 Serena 를 처음 띄우면
    브라우저 탭이 하나 열리고, 그 뒤로 세션을 다시 적재할 때마다 또 열린다.

왜 YAML 파서를 쓰지 않는가
    그 파일은 주석이 본문보다 길다. 어떤 값이 무엇을 하는지, 대시보드를 수동으로
    여는 주소가 무엇인지가 전부 주석에 있다. 통째로 다시 쓰면 그게 사라진다.
    바꾸는 것은 두 줄뿐이니 그 두 줄만 갈아 끼운다.

파일이 없으면 아무것도 하지 않는다
    Serena 는 처음 실행될 때 이 파일을 만든다. 새 머신에서는 부트스트랩이
    먼저 도니 파일이 없는 것이 정상이고, 그때는 다시 돌리라고 알리고 빠진다.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import re


# 창을 여는 설정 둘. 값은 문자열로 비교한다.
FLAGS = {
    "gui_log_window": "false",
    "web_dashboard_open_on_launch": "false",
}


def apply(text: str) -> tuple[str, list[str]]:
    """최상위 키만 바꾼다. 없으면 끝에 덧붙인다."""
    changes: list[str] = []
    for key, wanted in FLAGS.items():
        pattern = re.compile(rf"^{re.escape(key)}:[ \t]*(\S+)[ \t]*$", re.M)
        match = pattern.search(text)
        if match is None:
            text = text.rstrip("\n") + f"\n\n{key}: {wanted}\n"
            changes.append(f"추가  {key} = {wanted}")
            continue
        if match.group(1) == wanted:
            continue
        text = pattern.sub(f"{key}: {wanted}", text, count=1)
        changes.append(f"변경  {key}: {match.group(1)} -> {wanted}")
    return text, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backup-dir",
        type=Path,
        help="실제로 쓸 때만 대상 파일을 여기에 복사한다",
    )
    args = parser.parse_args()

    home = Path(os.environ.get("SERENA_HOME") or Path.home() / ".serena")
    config = home / "serena_config.yml"

    if not config.exists():
        print(f"  Serena 설정이 아직 없다: {config}")
        print("  Serena 를 한 번 띄운 뒤 이 스크립트를 다시 돌린다.")
        return 0

    text = config.read_text(encoding="utf-8")
    updated, changes = apply(text)

    if not changes:
        print("  Serena 설정 변경 없음")
        return 0

    if args.backup_dir:
        args.backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup = args.backup_dir / f"{config.name}.{stamp}"
        backup.write_bytes(config.read_bytes())
        print(f"  백업: {backup}")

    config.write_text(updated, encoding="utf-8")
    for change in changes:
        print(f"  {change}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
