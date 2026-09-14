#!/usr/bin/env python3
"""no-dash-gate 훅에 가짜 페이로드를 먹여 막을 것과 통과시킬 것을 확인한다.

두 부트스트랩이 설치한 훅 경로를 넘겨 이 스크립트를 부른다. 하나라도 어긋나면
0 이 아닌 값으로 끝난다.

    python3 presets/user/hooks/test-no-dash-gate.py ~/.claude/hooks/no-dash-gate.py

줄표 문자를 이 파일에 직접 쓰지 않는다. 훅이 켜진 세션에서 이 파일을 고치다가
훅에 막히기 때문이다. 전부 이스케이프로 만든다.
"""

from __future__ import annotations

import json
import subprocess
import sys

EM = "\u2014"
EN = "\u2013"
BAR = "\u2015"


def run(hook: str, payload: object) -> tuple[str, int]:
    """훅을 돌려 결정(deny/allow)과 종료 코드를 돌려준다."""
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    proc = subprocess.run(
        [hook], input=stdin, capture_output=True, text=True, timeout=10
    )
    decision = "allow"
    out = proc.stdout.strip()
    if out:
        data = json.loads(out)
        decision = (
            data.get("hookSpecificOutput", {}).get("permissionDecision") or "allow"
        )
    return decision, proc.returncode


def claude(tool: str, **tool_input: object) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}


def codex(tool: str, command: str) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "turn_id": "t",
        "tool_name": tool,
        "tool_input": {"command": command},
    }


def patch(*body: str) -> str:
    return "\n".join(["*** Begin Patch", *body, "*** End Patch"])


CASES: list[tuple[str, object, str]] = [
    ("Claude Write, em dash", claude("Write", file_path="a.md", content=f"a {EM} b"), "deny"),
    ("Claude Write, en dash", claude("Write", file_path="a.md", content=f"18:30{EN}21:30"), "deny"),
    ("Claude Write, horizontal bar", claude("Write", file_path="a.md", content=f"a {BAR} b"), "deny"),
    ("Claude Write, hyphen and tilde only", claude("Write", file_path="a.md", content="a - b, 18:30~21:30"), "allow"),
    ("Claude Edit, dash added", claude("Edit", file_path="a.md", old_string="a, b", new_string=f"a {EM} b"), "deny"),
    ("Claude Edit, dash removed", claude("Edit", file_path="a.md", old_string=f"a {EM} b", new_string="a, b"), "allow"),
    (
        "Claude MultiEdit, dash in second edit",
        claude("MultiEdit", file_path="a.md", edits=[{"old_string": "x", "new_string": "y"}, {"old_string": "p", "new_string": f"q{EM}"}]),
        "deny",
    ),
    ("Claude NotebookEdit, dash in source", claude("NotebookEdit", notebook_path="a.ipynb", new_source=f"# a {EM} b"), "deny"),
    ("Claude Bash, literal dash in heredoc", claude("Bash", command=f"cat > a.md <<'EOF'\na {EM} b\nEOF"), "deny"),
    ("Claude Bash, escaped dash", claude("Bash", command="grep -nP '[\\x{2013}\\x{2014}\\x{2015}]' a.md"), "allow"),
    ("Claude Bash, unrelated", claude("Bash", command="git status"), "allow"),
    (
        "Codex apply_patch, added line with dash",
        codex("apply_patch", patch("*** Update File: a.md", "@@", "-a, b", f"+a {EM} b")),
        "deny",
    ),
    (
        "Codex apply_patch, dash only in removed and context lines",
        codex("apply_patch", patch("*** Update File: a.md", "@@", f" keep {EM} context", f"-a {EM} b", "+a, b")),
        "allow",
    ),
    (
        "Codex apply_patch, new file with dash",
        codex("apply_patch", patch("*** Add File: b.md", f"+title {EN} sub")),
        "deny",
    ),
    ("Codex Bash, literal dash", codex("Bash", f"echo 'a {EM} b' > a.md"), "deny"),
    ("empty stdin", "", "allow"),
    ("malformed stdin", "{not json", "allow"),
]


def main() -> int:
    if len(sys.argv) != 2:
        print("사용법: test-no-dash-gate.py <훅 경로>", file=sys.stderr)
        return 2
    hook = sys.argv[1]
    failures = 0
    for name, payload, expected in CASES:
        try:
            decision, code = run(hook, payload)
        except Exception as error:  # 훅이 없거나 실행이 안 되면 여기로 온다
            print(f"  실패  {name}: 실행 오류 {error!r}")
            failures += 1
            continue
        if code != 0 or decision != expected:
            print(f"  실패  {name}: 기대 {expected}, 실제 {decision} (exit {code})")
            failures += 1
        else:
            print(f"  통과  {name}: {decision}")
    if failures:
        print(f"실패 {failures}건 / {len(CASES)}건", file=sys.stderr)
        return 1
    print(f"전부 통과 ({len(CASES)}건)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
