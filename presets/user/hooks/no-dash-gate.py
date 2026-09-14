#!/usr/bin/env python3
"""에이전트가 파일이나 명령에 줄표를 쓰려 하면 막는다.

Claude Code 와 Codex 가 같은 스크립트를 쓴다. 둘 다 PreToolUse 에서 이 훅을 부르고,
막는 JSON 형식(hookSpecificOutput.permissionDecision = "deny")이 같다.

막는 문자
  U+2014 (em dash), U+2013 (en dash), U+2015 (horizontal bar)

왜 있는가
  줄표는 에이전트가 쓴 글이라는 티가 가장 많이 나는 표시다. 사용자가 여러 번
  지적했고 규칙으로도 적었지만 규칙만으로는 계속 새어 나왔다. 규칙과 근거는
  ~/code/writing-guides/common/general/ai-tells.md 에 있다.

왜 deny 인가
  fanout-cost-gate 와 같은 이유다. ask 는 bypassPermissions 모드에서 건너뛰어질 수
  있다. 이 규칙은 모드와 무관하게 서야 한다.

무엇을 검사하나
  새로 들어가는 글만 본다. 줄표를 지우는 수정까지 막으면 고칠 방법이 없어진다.
  - Claude Write: content
  - Claude Edit: new_string (old_string 은 보지 않는다)
  - Claude MultiEdit: 각 edit 의 new_string
  - Claude NotebookEdit: new_source
  - Bash (Claude, Codex): command 전체. 명령에서 추가와 삭제를 가를 수 없다
  - Codex apply_patch: 패치에서 + 로 시작하는 추가 줄만. 문맥 줄과 - 줄은 보지 않는다

통과시키는 법
  - 원문을 그대로 옮겨야 하는 파일은 쓰기 도구 대신 cp 로 복사한다. 명령에 줄표
    문자가 들어가지 않는다.
  - 줄표를 찾거나 지우는 명령은 문자를 직접 쓰지 않고 코드 포인트 이스케이프로 쓴다.

입력을 읽지 못하면 조용히 통과한다. 이 훅 때문에 도구가 멈추면 안 된다.

줄표 문자를 이 파일에 직접 쓰지 않는다. 이 파일을 고치다가 훅에 막히기 때문이다.
"""

from __future__ import annotations

import json
import sys

DASHES = {
    chr(0x2014): "U+2014",
    chr(0x2013): "U+2013",
    chr(0x2015): "U+2015",
}

MAX_SHOWN = 3


def added_patch_lines(patch: str) -> str:
    """apply_patch 본문에서 추가되는 줄만 남긴다."""
    lines = []
    for line in patch.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])
    return "\n".join(lines)


def texts_to_check(payload: dict) -> list[str]:
    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return []

    def field(name: str) -> str:
        value = tool_input.get(name)
        return value if isinstance(value, str) else ""

    if tool == "apply_patch":
        return [added_patch_lines(field("command"))]
    if tool == "Bash":
        return [field("command")]
    if tool == "Write":
        return [field("content")]
    if tool == "Edit":
        return [field("new_string")]
    if tool == "MultiEdit":
        edits = tool_input.get("edits")
        if not isinstance(edits, list):
            return []
        return [
            e.get("new_string", "")
            for e in edits
            if isinstance(e, dict) and isinstance(e.get("new_string"), str)
        ]
    if tool == "NotebookEdit":
        return [field("new_source")]
    return []


def offending_lines(texts: list[str]) -> tuple[list[str], set[str]]:
    shown: list[str] = []
    found: set[str] = set()
    for text in texts:
        for line in text.splitlines():
            hits = {code for char, code in DASHES.items() if char in line}
            if not hits:
                continue
            found |= hits
            if len(shown) < MAX_SHOWN:
                marked = line
                for char, code in DASHES.items():
                    marked = marked.replace(char, f"[{code}]")
                shown.append(marked.strip()[:160])
    return shown, found


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else None
    except json.JSONDecodeError:
        return 0
    if not isinstance(payload, dict):
        return 0

    shown, found = offending_lines(texts_to_check(payload))
    if not found:
        return 0

    codes = ", ".join(sorted(found))
    reason = "\n".join(
        [
            f"줄표({codes})가 들어가 있어 막았습니다. 줄표는 쓰지 않습니다.",
            "쉼표, 마침표, 콜론, 괄호로 바꾸거나 문장을 나눠 다시 쓰십시오.",
            "",
            "걸린 줄:",
            *[f"  {line}" for line in shown],
            "",
            "원문을 그대로 옮겨야 하는 파일이면 쓰기 도구 대신 cp 로 복사하십시오.",
            "줄표를 찾거나 지우는 명령이면 문자를 직접 쓰지 말고 코드 포인트 이스케이프로 쓰십시오.",
            "규칙: ~/code/writing-guides/common/general/ai-tells.md",
        ]
    )
    print(
        json.dumps(
            {
                "systemMessage": f"차단됨: 줄표({codes})를 쓰려 했습니다.",
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                },
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
