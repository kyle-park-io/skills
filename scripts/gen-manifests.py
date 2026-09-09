#!/usr/bin/env python3
"""domains.json 하나에서 하네스별 매니페스트를 전부 생성한다.

도메인 7개 x 하네스 2개 = 매니페스트 14개에 마켓플레이스 2개다. 손으로
관리하면 버전을 올릴 때마다 갈라진다. 여기서만 고치고 이 스크립트를 돌린다.

    python3 scripts/gen-manifests.py           생성
    python3 scripts/gen-manifests.py --check   생성물이 최신인지만 확인 (CI용)

생성되는 것:
    .claude-plugin/marketplace.json        Claude Code 마켓플레이스
    .agents/plugins/marketplace.json       크로스 런타임 마켓플레이스
    <domain>/.claude-plugin/plugin.json    Claude Code 플러그인
    <domain>/.codex-plugin/plugin.json     Codex 플러그인

손으로 고치지 않는다. domains.json 을 고친다.
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANNER = "생성물이다. 손으로 고치지 말고 domains.json 을 고친 뒤 scripts/gen-manifests.py 를 돌린다."


def load():
    return json.loads((ROOT / "domains.json").read_text(encoding="utf-8"))


def claude_marketplace(cfg):
    m, repo = cfg["marketplace"], cfg["marketplace"]["repository"]
    return {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": m["name"],
        "description": m["description"],
        "owner": m["author"],
        "plugins": [
            {
                "name": d["name"],
                "description": d["description"],
                "version": d["version"],
                "source": f"./{d['name']}",
                "category": d["claudeCategory"],
                "author": m["author"],
                "homepage": f"{repo}/tree/main/{d['name']}",
            }
            for d in cfg["domains"]
        ],
    }


def agents_marketplace(cfg):
    m = cfg["marketplace"]
    return {
        "name": m["name"],
        "interface": {"displayName": m["displayName"]},
        "plugins": [
            {
                "name": d["name"],
                "source": {"source": "url", "url": f"./{d['name']}"},
                "policy": {"installation": "AVAILABLE", "authentication": "NONE"},
                "category": d["codexCategory"],
            }
            for d in cfg["domains"]
        ],
    }


def claude_plugin(cfg, d):
    m, repo = cfg["marketplace"], cfg["marketplace"]["repository"]
    return {
        "name": d["name"],
        "description": d["description"],
        "version": d["version"],
        "author": m["author"],
        "homepage": f"{repo}/tree/main/{d['name']}",
        "repository": repo,
        "license": m["license"],
        "keywords": d["keywords"],
    }


def codex_plugin(cfg, d):
    """Codex 스키마는 Claude 것과 다르다.

    skills 경로를 명시해야 하고, hooks 키가 있어야 하며, 표시용 interface
    블록을 요구한다. 카테고리도 소문자 슬러그가 아니라 표시 문자열이다.
    """
    m, repo = cfg["marketplace"], cfg["marketplace"]["repository"]
    return {
        "name": d["name"],
        "version": d["version"],
        "description": d["description"],
        "author": m["author"],
        "homepage": f"{repo}/tree/main/{d['name']}",
        "repository": repo,
        "license": m["license"],
        "keywords": d["keywords"],
        "skills": "./skills/",
        "hooks": {},
        "interface": {
            "displayName": d["name"],
            "shortDescription": d["shortDescription"],
            "longDescription": d["description"],
            "developerName": m["author"]["name"],
            "category": d["codexCategory"],
            "capabilities": ["Interactive", "Read"],
            "defaultPrompt": d["prompts"],
            "websiteURL": repo,
        },
    }


def targets(cfg):
    out = {
        ".claude-plugin/marketplace.json": claude_marketplace(cfg),
        ".agents/plugins/marketplace.json": agents_marketplace(cfg),
    }
    for d in cfg["domains"]:
        out[f"{d['name']}/.claude-plugin/plugin.json"] = claude_plugin(cfg, d)
        out[f"{d['name']}/.codex-plugin/plugin.json"] = codex_plugin(cfg, d)
    return out


def render(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="쓰지 않고 최신 여부만 확인한다. 낡았으면 1로 종료한다.")
    args = ap.parse_args()

    stale, written = [], []
    for rel, obj in targets(load()).items():
        path, want = ROOT / rel, render(obj)
        have = path.read_text(encoding="utf-8") if path.exists() else None
        if have == want:
            continue
        if args.check:
            stale.append(rel)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(want, encoding="utf-8")
        written.append(rel)

    if args.check:
        if stale:
            print("낡은 매니페스트:", file=sys.stderr)
            for r in stale:
                print(f"  {r}", file=sys.stderr)
            print("\nscripts/gen-manifests.py 를 돌리고 결과를 커밋한다.", file=sys.stderr)
            return 1
        print("매니페스트 최신 상태")
        return 0

    for r in written:
        print(f"  생성 {r}")
    print(f"{len(written)}개 갱신, {len(targets(load())) - len(written)}개 변경 없음")
    print(f"\n{BANNER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
