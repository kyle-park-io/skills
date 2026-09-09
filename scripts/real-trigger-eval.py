#!/usr/bin/env python3
"""실제 설치된 플러그인 스킬로 트리거 발동률을 측정한다.

`skill-creator` 의 트리거 eval 은 `.claude/commands/` 에 커맨드 파일을
심어 스킬을 흉내낸다. 그 프록시는 실물 플러그인 스킬만큼 발동하지 않아서,
실물로는 7초 만에 뜨는 스킬이 프록시로는 한 번도 안 뜨는 일이 생긴다.
그래서 프록시로 잰 발동률은 스킬의 발동률이 아니다.

여기서는 플러그인을 실제로 켜둔 프로젝트에서 `claude -p` 를 돌리고
스트림에서 Skill 툴 호출을 직접 관측한다.

사용법:

    python3 scripts/real-trigger-eval.py \\
        --eval-set eval.json \\
        --project <플러그인을 켜둔 레포 경로> \\
        --skill schema-review \\
        --out result.json

`--project` 는 대상 스킬의 도메인 플러그인이 `.claude/settings.json` 에
켜져 있고, 스킬이 다룰 코드가 실제로 들어 있는 레포여야 한다. 빈
디렉터리에서 재면 발동률이 실제보다 낮게 나온다.

eval.json 은 `[{"query": "...", "should_trigger": true}, ...]` 형식이다.
발동해야 하는 쿼리와 아닌 쿼리를 비슷한 수로 섞고, 부정 쿼리는 키워드가
겹치는 근접 사례로 채운다. 명백히 무관한 쿼리는 아무것도 검증하지 않는다.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor


def run_once(query, cwd, skill, model, timeout):
    """쿼리 하나를 돌리고 대상 스킬이 열렸는지 반환한다."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    proc = subprocess.Popen(
        ["claude", "-p", query, "--model", model,
         "--output-format", "stream-json", "--verbose"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=cwd, env=env)
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
            if event.get("type") == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use" and block.get("name") == "Skill":
                        if skill in str(block.get("input", {})):
                            triggered = True
            if event.get("type") == "result":
                break
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
    return triggered


def evaluate(item, args):
    """쿼리 하나를 여러 번 돌려 과반으로 발동 여부를 정한다."""
    started = time.time()
    hits = sum(run_once(item["query"], args.project, args.skill,
                        args.model, args.timeout)
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
    parser.add_argument("--eval-set", required=True, help="쿼리 JSON 경로")
    parser.add_argument("--project", required=True, help="플러그인을 켜둔 레포 경로")
    parser.add_argument("--skill", required=True, help="측정할 스킬 이름")
    parser.add_argument("--out", required=True, help="결과 JSON 경로")
    parser.add_argument("--model", default="claude-opus-5")
    parser.add_argument("--runs", type=int, default=3, help="쿼리당 반복 횟수")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=300,
                        help="런 하나의 상한 초. 짧게 잡으면 발동을 놓친다")
    args = parser.parse_args()

    settings = os.path.join(args.project, ".claude", "settings.json")
    if not os.path.exists(settings):
        print(f"경고: {settings} 가 없다. 플러그인이 켜져 있는지 확인한다.",
              file=sys.stderr)

    items = json.load(open(args.eval_set))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda i: evaluate(i, args), items))

    summary = summarize(results)
    with open(args.out, "w") as f:
        json.dump({"summary": summary, "results": results}, f,
                  ensure_ascii=False, indent=2)
    print("SUMMARY " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
