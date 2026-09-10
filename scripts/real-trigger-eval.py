#!/usr/bin/env python3
"""실제 설치된 플러그인 스킬로 트리거 발동률을 측정한다.

`skill-creator` 의 트리거 eval 은 `.claude/commands/` 에 커맨드 파일을
심어 스킬을 흉내낸다. 그 프록시는 실물 플러그인 스킬만큼 발동하지 않아서,
실물로는 7초 만에 뜨는 스킬이 프록시로는 한 번도 안 뜨는 일이 생긴다.
그래서 프록시로 잰 발동률은 스킬의 발동률이 아니다.

여기서는 플러그인을 실제로 켜둔 프로젝트에서 Claude Code 또는 Codex 를
비대화형으로 돌리고, 스트림에서 대상 스킬이 실제로 열린 것을 관측한다.

사용법:

    python3 scripts/real-trigger-eval.py \\
        --harness claude \\
        --eval-set evals/<스킬>.json \\
        --project <플러그인을 켜둔 레포 경로> \\
        --skill schema-review \\
        --out result.json

`--project` 는 대상 스킬이 실제로 설치된 상태이고, 스킬이 다룰 코드가
들어 있는 레포여야 한다. Claude Code 는 프로젝트의 `.claude/settings.json`,
Codex 는 사용자 플러그인 설치 상태나 프로젝트의 `.agents/skills/` 를 쓴다.
빈 디렉터리에서 재면 발동률이 실제보다 낮게 나온다.

명시 호출은 재지 않는다. `$skill-name` 처럼 직접 부르면 Codex 호스트가 턴을
시작하기 전에 본문을 넣을 수 있어 JSONL 에 파일 읽기 이벤트가 남지 않는다.
이 스크립트의 목적은 description 에 의한 암시 발동을 재는 것이다.

쿼리 셋은 `evals/<스킬>.json` 에 둔다. 스킬 폴더 안에 두면 플러그인
페이로드로 딸려 나가 설치자에게 쓸모없는 파일이 된다. 형식과 음성 쿼리를
고르는 법, 그리고 지금까지의 측정 기록은 `evals/README.md` 에 있다.

비용
----

쿼리 수 x --runs 만큼 독립 세션이 뜬다. 각 세션이 자기 시스템 프롬프트를 새로
싣고 대상 레포를 탐색한다. 14 쿼리를 3회씩 Opus 5 로 돌린 실측이 에이전트
작업 113분이었다. **돌리기 전에 그 곱셈을 하고, 남이 쓰는 쿼터면 먼저 묻는다.**

모델
----

평소 쓰는 모델로 재야 그 숫자가 내 세션의 숫자다. 스킬 선택은 모델이 하는
판단이라 모델이 바뀌면 답도 바뀐다.

다만 description 을 고쳐가며 반복하는 동안에는 싼 모델로 훑는다. "아예 안
뜬다" 나 "아무 데나 뜬다" 같은 큰 실패는 거기서 다 잡힌다. 확정 직전에 한 번만
실제로 쓰는 모델로 잰다.

언제 돌리나
-----------

**새 스킬을 만들 때마다 돌리지 않는다.** 이건 진단이지 관문이 아니다.

돌릴 때는 이렇다. 써야 할 스킬이 안 떠서 손으로 부른 적이 있을 때. 새 스킬의
트리거 상황이 기존 스킬과 겹쳐 보일 때. 도메인을 남에게 열 때.

지금까지 두 번 (schema-review, project-templates) 다 결과가 만점이었고,
**측정은 이미 맞던 description 을 확인해준 것뿐이었다.** 트리거 정확도를 만든
것은 측정이 아니라 description 에 "이럴 때 쓰지 않는다" 를 명시적으로 쓴
쪽이다. 그게 먼저고, 이 스크립트는 그게 안 통했을 때 부른다.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor


def codex_event_triggered(event, skill):
    """Codex JSONL 이벤트가 대상 SKILL.md 를 실제로 연 명령인지 본다."""
    item = event.get("item", {})
    if item.get("type") != "command_execution":
        return False
    command = item.get("command", "").replace("\\\\", "/")
    return f"/{skill}/SKILL.md" in command


def run_claude_once(query, cwd, skill, model, timeout, max_turns):
    """쿼리 하나를 돌리고 대상 스킬이 열렸는지 반환한다.

    런은 두 가지 조건에서 즉시 끝난다. 둘 다 측정에 아무것도 더하지 않는 구간을
    잘라내는 것이고, 이 함수가 도는 비용의 대부분이 거기 있었다.

    스킬이 열리면 그 자리에서 끊는다. 발동 여부는 그 시점에 확정이고, 이후는
    에이전트가 그 스킬의 작업을 실제로 수행하는 시간이다. 이 조건이 없던 동안
    양성 쿼리 한 런이 음성 쿼리의 두 배를 썼다 (측정: 216초 대 106초).

    스킬 없이 max_turns 턴을 넘기면 끊는다. 스킬 선택은 첫 턴의 판단이라 그때
    안 열린 것은 뒤에도 안 열린다. 음성 쿼리는 발동이 없어 앞의 조건에 안 걸리므로
    이쪽이 상한이 된다.
    """
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    proc = subprocess.Popen(
        ["claude", "-p", query, "--model", model,
         "--output-format", "stream-json", "--verbose"],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, cwd=cwd, env=env, text=True)
    triggered = False
    turns = 0
    deadline = time.time() + timeout
    try:
        for raw in proc.stdout:
            if time.time() > deadline:
                break
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "assistant":
                turns += 1
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use" and block.get("name") == "Skill":
                        if skill in str(block.get("input", {})):
                            triggered = True
                            break
                if triggered or turns >= max_turns:
                    break
            if event.get("type") == "result":
                break
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
    return triggered


def run_codex_once(query, cwd, skill, model, timeout):
    """Codex JSONL 에서 대상 스킬 본문을 연 command_execution 을 찾는다."""
    command = [
        "codex", "exec", "--ephemeral", "--json", "--sandbox", "read-only",
        "-C", cwd,
    ]
    if model:
        command.extend(["--model", model])
    command.append(query)

    proc = subprocess.Popen(
        command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL, cwd=cwd, text=True)
    triggered = False
    deadline = time.time() + timeout
    try:
        for raw in proc.stdout:
            if time.time() > deadline:
                break
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if codex_event_triggered(event, skill):
                triggered = True
                break
            if event.get("type") == "turn.completed":
                break
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
    return triggered


def run_once(query, cwd, skill, harness, model, timeout, max_turns):
    if harness == "claude":
        return run_claude_once(query, cwd, skill, model, timeout, max_turns)
    return run_codex_once(query, cwd, skill, model, timeout)


def evaluate(item, args):
    """쿼리 하나를 여러 번 돌려 과반으로 발동 여부를 정한다."""
    started = time.time()
    hits = sum(run_once(item["query"], args.project, args.skill, args.harness,
                        args.model, args.timeout, args.max_turns)
               for _ in range(args.runs))
    fired = hits > args.runs // 2
    result = {
        "query": item["query"],
        "should_trigger": item["should_trigger"],
        "hits": hits,
        "runs": args.runs,
        "fired": fired,
        "correct": fired == item["should_trigger"],
        "secs": round(time.time() - started, 1),
    }
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


def summarize(results):
    tp = sum(1 for r in results if r["should_trigger"] and r["fired"])
    fn = sum(1 for r in results if r["should_trigger"] and not r["fired"])
    fp = sum(1 for r in results if not r["should_trigger"] and r["fired"])
    tn = sum(1 for r in results if not r["should_trigger"] and not r["fired"])
    return {
        "tp": tp, "fn": fn, "fp": fp, "tn": tn,
        "accuracy": round((tp + tn) / len(results), 3) if results else None,
        "precision": round(tp / (tp + fp), 3) if tp + fp else None,
        "recall": round(tp / (tp + fn), 3) if tp + fn else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--harness", choices=("claude", "codex"),
                        default="claude", help="측정할 하네스 (기본: claude)")
    parser.add_argument("--eval-set", required=True, help="쿼리 JSON 경로")
    parser.add_argument("--project", required=True, help="플러그인을 켜둔 레포 경로")
    parser.add_argument("--skill", required=True, help="측정할 스킬 이름")
    parser.add_argument("--out", required=True, help="결과 JSON 경로")
    parser.add_argument("--model", help="모델. 생략하면 Claude는 claude-opus-5, "
                                        "Codex는 현재 설정값을 쓴다")
    parser.add_argument("--runs", type=int, default=3, help="쿼리당 반복 횟수")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=300,
                        help="런 하나의 상한 초. 짧게 잡으면 발동을 놓친다")
    parser.add_argument("--max-turns", type=int, default=6,
                        help="Claude에서 스킬 없이 이 턴을 넘기면 미발동으로 끊는다. "
                             "Codex exec는 한 턴이라 이 값을 쓰지 않는다")
    args = parser.parse_args()

    if args.model is None and args.harness == "claude":
        args.model = "claude-opus-5"

    if args.harness == "claude":
        settings = os.path.join(args.project, ".claude", "settings.json")
        if not os.path.exists(settings):
            print(f"경고: {settings} 가 없다. 플러그인이 켜져 있는지 확인한다.",
                  file=sys.stderr)
    else:
        repo_skills = os.path.join(args.project, ".agents", "skills")
        if not os.path.exists(repo_skills):
            print("알림: 프로젝트 .agents/skills 가 없다. 사용자 스코프에 대상 "
                  "플러그인이 설치되어 있는지 `codex plugin list` 로 확인한다.",
                  file=sys.stderr)

    items = json.load(open(args.eval_set))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda i: evaluate(i, args), items))

    summary = summarize(results)
    with open(args.out, "w") as f:
        json.dump({
            "harness": args.harness,
            "model": args.model or "configured-default",
            "skill": args.skill,
            "summary": summary,
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print("SUMMARY " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
